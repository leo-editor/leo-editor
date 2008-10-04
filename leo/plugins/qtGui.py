# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20081004102201.619:@thin qtGui.py
#@@first

'''qt gui plugin.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< qt imports >>
#@+node:ekr.20081004102201.620:<< qt imports >>
import leo.core.leoGlobals as g
import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
import leo.core.leoFrame as leoFrame
import leo.core.leoFind as leoFind
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes

import os
import sys
import time

try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4 import Qsci
    from ui_main import Ui_MainWindow
except ImportError:
    qt = None
    g.es_print('can not import qt')
#@-node:ekr.20081004102201.620:<< qt imports >>
#@nl

#@+others
#@+node:ekr.20081004102201.623:Module level

#@+node:ekr.20081004102201.627:embed_ipython
def embed_ipython():

    import IPython.ipapi

    sys.argv = ['ipython', '-p' , 'sh']
    ses = IPython.ipapi.make_session(dict(w = window))
    ip = ses.IP.getapi()
    ip.load('ipy_leo')
    ses.mainloop()
#@nonl
#@-node:ekr.20081004102201.627:embed_ipython
#@+node:ekr.20081004102201.621:init
def init():

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    if not qt:
        return False

    if g.app.gui:
        return g.app.gui.guiName() == 'qt'
    else:
        g.app.gui = qtGui()
        # g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@-node:ekr.20081004102201.621:init
#@+node:ekr.20081004102201.624:main
def main():

    argv = sys.argv
    app = QApplication(sys.argv)
    window = Window()
    window.show()

    if 0:
        timer = QTimer()
        timer.setInterval(1)
        timer.setSingleShot(True)
        timer.connect(timer, SIGNAL("timeout()"), window.startup_ops)

    QTimer.singleShot(1, window.startup_ops)

    embed_ipython()
    sys.exit(app.exec_())
#@-node:ekr.20081004102201.624:main
#@+node:ekr.20081004102201.625:startleo
def startleo():

    global c,g, controller
    from leo.core import leoBridge
    controller = leoBridge.controller(gui='nullGui')
    g = controller.globals()
    c = None
#@nonl
#@-node:ekr.20081004102201.625:startleo
#@+node:ekr.20081004102201.626:tstart & tstop
def tstart():
    global __timing
    __timing = time.time()

def tstop():
    print ("Time: %1.2fsec" % (time.time() - __timing))
#@-node:ekr.20081004102201.626:tstart & tstop
#@-node:ekr.20081004102201.623:Module level
#@+node:ekr.20081004102201.628:class LeoQEventFilter
class LeoQEventFilter(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.bindings = {}
    def eventFilter(self, obj, event):

        # print "ev",obj, event
        if event.type() == QEvent.KeyPress:
            return self.key_pressed(obj, event)
        return False
    def key_pressed(self, obj, event):
        """ Handle key presses (on any window) """

        keynum = event.key()
        try:
            char = chr(keynum)
        except ValueError:
            char = "<unknown>"

        mods = []
        if event.modifiers() & Qt.AltModifier:
            mods.append("Alt")
        if event.modifiers() & Qt.ControlModifier:
            mods.append("Ctrl")
        if event.modifiers() & Qt.ShiftModifier:
            mods.append("Shift")

        txt = "+".join(mods) + (mods and "+" or "") + char
        print "Keypress: [",txt,"]", event.text(), obj, event.key(), event.modifiers()
        # key was not consumed

        cmd = self.bindings.get(txt, None)
        if cmd:
            cmd()
            return True

        return False
#@nonl
#@-node:ekr.20081004102201.628:class LeoQEventFilter
#@+node:ekr.20081004102201.629:class Window
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.connect(self.treeWidget, SIGNAL("itemSelectionChanged()"),  self.tree_select )
        self.connect(self.actionOpen,SIGNAL("activated()"),self.open_file)
        self.connect(self.actionSave,SIGNAL("activated()"),self.save_file)
        #self.connect(self.searchButton, SIGNAL("clicked()"), self.search)
        self.connect(self.textEdit,  SIGNAL("textChanged()"),self.text_changed)

        #self.connect(self.actionIPython,SIGNAL("activated()"),self.embed_ipython)
        self.selecting = True
        self.widget_dirty = False
        lexer = Qsci.QsciLexerPython(self.textEdit)
        self.textEdit.setLexer(lexer)
        self.ev_filt = LeoQEventFilter()
        self.ev_filt.bindings['Ctrl+H'] = self.edit_current_headline
        self.textEdit.installEventFilter(self.ev_filt)
        self.treeWidget.installEventFilter(self.ev_filt)
        self.icon_std = None
        self.icon_std = QIcon('icons/box00.GIF')
        self.icon_dirty = QIcon('icons/box01.GIF')

    def open_file(self):
        #print "file open"

        fd = QFileDialog(self)
        fname = fd.getOpenFileName()
        print `fname`
        self.load_file(fname)

    def load_file(self,f):
        self.clear_model()
        global c
        print "Load",f
        tstart()
        c = controller.openLeoFile(str(f))
        tstop()
        print "Populate tree widget"
        tstart()
        self.populate_tree()
        tstop()
        class Leox:
            pass
        _leox = Leox()
        _leox.c = c
        _leox.g = g
        import ipy_leo
        ipy_leo.update_commander(_leox)

    def save_file(self):
        c.save()

    def clear_model(self):
        global c
        self.treeWidget.clear()
        self.items = {}
        self.treeitems = {}
        if c is not None:
            c.close()
            c = None

    def populate_tree(self, parent=None):
        """ Render vnodes in tree """

        self.items = {}
        self.treeitems = {}

        self.treeWidget.clear()
        for p in c.allNodes_iter():

            parent = self.items.get(p.parent().v,  self.treeWidget)
            it = QTreeWidgetItem(parent)
            it.setIcon(0, self.icon_std)
            it.setFlags(it.flags() | Qt.ItemIsEditable)
            self.items[p.v] = it
            self.treeitems[id(it)] = p.t
            it.setText(0, p.headString())

    def flush_current_tnode(self):
        text = str(self.textEdit.text())
        self.cur_tnode.setBodyString(text)

    def tree_select(self):
        #print "tree selected!"
        self.selecting = True

        if self.widget_dirty:
            self.flush_current_tnode()

        self.cur_tnode = self.treeitems[id(self.treeWidget.currentItem())]
        self.textEdit.setText(self.cur_tnode.bodyString())
        self.selecting = False
        self.widget_dirty = False

    def text_changed(self):
        if self.selecting:
            return
        #print "text changed"
        if not self.widget_dirty:
            self.treeWidget.currentItem().setIcon(0,self.icon_dirty)
        self.widget_dirty = True

    def startup_ops(self):
        print "startup"

        if len(argv) > 1:
            self.load_file(argv[1])

    def edit_current_headline(self):
        #self.treeWidget.openPersistentEditor(self.treeWidget.currentItem())
        self.treeWidget.editItem(self.treeWidget.currentItem())
#@nonl
#@-node:ekr.20081004102201.629:class Window
#@+node:ekr.20081004102201.631:qtGui
class qtGui(leoGui.leoGui):

    """A class encapulating all calls to qt."""

    #@    @+others
    #@+node:ekr.20081004102201.632:qtGui birth & death
    #@+node:ekr.20081004102201.633: qtGui.__init__
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,'qt')

        self.bodyTextWidget  = leoGtkFrame.leoGtkTextWidget
        self.plainTextWidget = leoGtkFrame.leoGtkTextWidget
        self.loadIcons()

        win32clipboar = None

        self.qtClipboard = qt.Clipboard()
    #@-node:ekr.20081004102201.633: qtGui.__init__
    #@+node:ekr.20081004102201.634:createKeyHandlerClass (qtGui)
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        import leo.core.leoGtkKeys as leoGtkKeys # Do this here to break any circular dependency.

        return leoGtkKeys.qtKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@-node:ekr.20081004102201.634:createKeyHandlerClass (qtGui)
    #@+node:ekr.20081004102201.635:runMainLoop (qtGui)
    def runMainLoop(self):

        '''Start the qt main loop.'''

        if self.script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=self.script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in qtGui.runMainLoop')
        else:
            qt.main()
    #@-node:ekr.20081004102201.635:runMainLoop (qtGui)
    #@+node:ekr.20081004102201.636:Do nothings
    # These methods must be defined in subclasses, but they need not do anything.

    def createRootWindow(self):
        pass

    def destroySelf (self):
        pass

    def killGui(self,exitFlag=True):
        """Destroy a gui and terminate Leo if exitFlag is True."""
        pass

    def recreateRootWindow(self):
        """A do-nothing base class to create the hidden root window of a gui
        after a previous gui has terminated with killGui(False)."""
        pass

    #@-node:ekr.20081004102201.636:Do nothings
    #@+node:ekr.20081004102201.637:Not used
    # The tkinter gui ctor calls these methods.
    # They are included here for reference.

    if 0:
        #@    @+others
        #@+node:ekr.20081004102201.638:qtGui.setDefaultIcon
        def setDefaultIcon(self):

            """Set the icon to be used in all Leo windows.

            This code does nothing for Tk versions before 8.4.3."""

            gui = self

            try:
                version = gui.root.getvar("tk_patchLevel")
                # g.trace(repr(version),g.CheckVersion(version,"8.4.3"))
                if g.CheckVersion(version,"8.4.3") and sys.platform == "win32":

                    path = g.os_path_join(g.app.loadDir,"..","Icons")
                    if g.os_path_exists(path):
                        theFile = g.os_path_join(path,"LeoApp16.ico")
                        if g.os_path_exists(path):
                            self.bitmap = qt.BitmapImage(theFile)
                        else:
                            g.es("","LeoApp16.ico","not in Icons directory",color="red")
                    else:
                        g.es("","Icons","directory not found:",path, color="red")
            except:
                g.pr("exception setting bitmap")
                import traceback ; traceback.print_exc()
        #@-node:ekr.20081004102201.638:qtGui.setDefaultIcon
        #@+node:ekr.20081004102201.639:qtGui.getDefaultConfigFont
        def getDefaultConfigFont(self,config):

            """Get the default font from a new text widget."""

            if not self.defaultFontFamily:
                # WARNING: retain NO references to widgets or fonts here!
                w = g.app.gui.plainTextWidget()
                fn = w.cget("font")
                font = qtFont.Font(font=fn) 
                family = font.cget("family")
                self.defaultFontFamily = family[:]
                # g.pr('***** getDefaultConfigFont',repr(family))

            config.defaultFont = None
            config.defaultFontFamily = self.defaultFontFamily
        #@-node:ekr.20081004102201.639:qtGui.getDefaultConfigFont
        #@-others
    #@-node:ekr.20081004102201.637:Not used
    #@-node:ekr.20081004102201.632:qtGui birth & death
    #@+node:ekr.20081004102201.640:qtGui dialogs & panels
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        """Create and run a qt About Leo dialog."""
        d = leoGtkDialog.qtAboutLeo(c,version,theCopyright,url,email)
        return d.run(modal=False)

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        d = leoGtkDialog.qtAskLeoID()
        return d.run(modal=True)

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        """Create and run a qt an askOK dialog ."""
        d = leoGtkDialog.qtAskOk(c,title,message,text)
        return d.run(modal=True)

    def runAskOkCancelNumberDialog(self,c,title,message):
        """Create and run askOkCancelNumber dialog ."""
        d = leoGtkDialog.qtAskOkCancelNumber(c,title,message)
        return d.run(modal=True)

    def runAskOkCancelStringDialog(self,c,title,message):
        """Create and run askOkCancelString dialog ."""
        d = leoGtkDialog.qtAskOkCancelString(c,title,message)
        return d.run(modal=True)

    def runAskYesNoDialog(self,c,title,message=None):
        """Create and run an askYesNo dialog."""
        d = leoGtkDialog.qtAskYesNo(c,title,message)
        return d.run(modal=True)

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):
        """Create and run an askYesNoCancel dialog ."""
        d = leoGtkDialog.qtAskYesNoCancel(
            c,title,message,yesMessage,noMessage,defaultButton)
        return d.run(modal=True)

    # The compare panel has no run dialog.

    # def runCompareDialog(self,c):
        # """Create and run an askYesNo dialog."""
        # if not g.app.unitTesting:
            # leoGtkCompareDialog(c)
    #@+node:ekr.20081004102201.641:qtGui.createSpellTab
    def createSpellTab(self,c,spellHandler,tabName):

        return leoGtkFind.qtSpellTab(c,spellHandler,tabName)
    #@-node:ekr.20081004102201.641:qtGui.createSpellTab
    #@+node:ekr.20081004102201.642:qtGui file dialogs (to do)
    # We no longer specify default extensions so that we can open and save files without extensions.
    #@+node:ekr.20081004102201.643:runFileDialog
    def runFileDialog(self,
        title='Open File',
        filetypes=None,
        action='open',
        multiple=False,
        initialFile=None
    ):

        g.trace()

        """Display an open or save file dialog.

        'title': The title to be shown in the dialog window.

        'filetypes': A list of (name, pattern) tuples.

        'action': Should be either 'save' or 'open'.

        'multiple': True if multiple files may be selected.

        'initialDir': The directory in which the chooser starts.

        'initialFile': The initial filename for a save dialog.

        """

        initialdir=g.app.globalOpenDir or g.os_path_finalize(os.getcwd())

        if action == 'open':
            btns = (
                qt.STOCK_CANCEL, qt.RESPONSE_CANCEL,
                qt.STOCK_OPEN, qt.RESPONSE_OK
            )
        else:
            btns = (
                qt.STOCK_CANCEL, qt.RESPONSE_CANCEL,
                qt.STOCK_SAVE, qt.RESPONSE_OK
            )

        qtaction = g.choose(
            action == 'save',
            qt.FILE_CHOOSER_ACTION_SAVE, 
            qt.FILE_CHOOSER_ACTION_OPEN
        )

        dialog = qt.FileChooserDialog(
            title,
            None,
            qtaction,
            btns
        )

        try:

            dialog.set_default_response(qt.RESPONSE_OK)
            dialog.set_do_overwrite_confirmation(True)
            dialog.set_select_multiple(multiple)
            if initialdir:
                dialog.set_current_folder(initialdir)

            if filetypes:

                for name, patern in filetypes:
                    filter = qt.FileFilter()
                    filter.set_name(name)
                    filter.add_pattern(patern)
                    dialog.add_filter(filter)

            response = dialog.run()
            g.pr('dialog response' , response)

            if response == qt.RESPONSE_OK:

                if multiple:
                    result = dialog.get_filenames()
                else:
                    result = dialog.get_filename()

            elif response == qt.RESPONSE_CANCEL:
                result = None

        finally:

            dialog.destroy()

        g.pr('dialog result' , result)

        return result
    #@-node:ekr.20081004102201.643:runFileDialog
    #@+node:ekr.20081004102201.644:runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an qt open file dialog ."""

        return self.runFileDialog(
            title=title,
            filetypes=filetypes,
            action='open',
            multiple=multiple,
        )
    #@nonl
    #@-node:ekr.20081004102201.644:runOpenFileDialog
    #@+node:ekr.20081004102201.645:runSaveFileDialog
    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run an qt save file dialog ."""

        return self.runFileDialog(
            title=title,
            filetypes=filetypes,
            action='save',
            initialfile=initialfile
        )
    #@nonl
    #@-node:ekr.20081004102201.645:runSaveFileDialog
    #@-node:ekr.20081004102201.642:qtGui file dialogs (to do)
    #@+node:ekr.20081004102201.646:qtGui panels (done)
    def createComparePanel(self,c):
        """Create a qt color picker panel."""
        return None # This window is optional.

        ### If desired, this panel could be created as follows:
        # return leoGtkComparePanel.leoGtkComparePanel(c)

    def createFindPanel(self,c):
        """Create a hidden qt find panel."""
        return None # This dialog is deprecated.

    def createFindTab (self,c,parentFrame):
        """Create a qt find tab in the indicated frame."""
        return leoGtkFind.qtFindTab(c,parentFrame)

    def createLeoFrame(self,title):
        """Create a new Leo frame."""
        gui = self
        return leoGtkFrame.leoGtkFrame(title,gui)
    #@-node:ekr.20081004102201.646:qtGui panels (done)
    #@-node:ekr.20081004102201.640:qtGui dialogs & panels
    #@+node:ekr.20081004102201.647:qtGui utils (to do)
    #@+node:ekr.20081004102201.648:Clipboard (qtGui)
    #@+node:ekr.20081004102201.649:replaceClipboardWith
    def replaceClipboardWith (self,s):

        # g.app.gui.win32clipboard is always None.
        wcb = g.app.gui.win32clipboard

        if wcb:
            try:
                wcb.OpenClipboard(0)
                wcb.EmptyClipboard()
                wcb.SetClipboardText(s)
                wcb.CloseClipboard()
            except:
                g.es_exception()
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append(s)
    #@-node:ekr.20081004102201.649:replaceClipboardWith
    #@+node:ekr.20081004102201.650:getTextFromClipboard
    def getTextFromClipboard (self):

        return None ###

        # g.app.gui.win32clipboard is always None.
        wcb = g.app.gui.win32clipboard

        if wcb:
            try:
                wcb.OpenClipboard(0)
                data = wcb.GetClipboardData()
                wcb.CloseClipboard()
                # g.trace(data)
                return data
            except TypeError:
                # g.trace(None)
                return None
            except:
                g.es_exception()
                return None
        else:
            try:
                s = self.root.selection_get(selection="CLIPBOARD")
                return s
            except:
                return None
    #@-node:ekr.20081004102201.650:getTextFromClipboard
    #@-node:ekr.20081004102201.648:Clipboard (qtGui)
    #@+node:ekr.20081004102201.651:color (to do)
    # g.es calls gui.color to do the translation,
    # so most code in Leo's core can simply use Tk color names.

    def color (self,color):
        '''Return the gui-specific color corresponding to the qt color name.'''
        return leoColor.getco

    #@-node:ekr.20081004102201.651:color (to do)
    #@+node:ekr.20081004102201.652:Dialog (these are optional)
    #@+node:ekr.20081004102201.653:get_window_info
    # WARNING: Call this routine _after_ creating a dialog.
    # (This routine inhibits the grid and pack geometry managers.)

    def get_window_info (self,top):

        top.update_idletasks() # Required to get proper info.

        # Get the information about top and the screen.
        geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
        dim,x,y = geom.split('+')
        w,h = dim.split('x')
        w,h,x,y = int(w),int(h),int(x),int(y)

        return w,h,x,y
    #@-node:ekr.20081004102201.653:get_window_info
    #@+node:ekr.20081004102201.654:center_dialog
    def center_dialog(self,top):

        """Center the dialog on the screen.

        WARNING: Call this routine _after_ creating a dialog.
        (This routine inhibits the grid and pack geometry managers.)"""

        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        w,h,x,y = self.get_window_info(top)

        # Set the new window coordinates, leaving w and h unchanged.
        x = (sw - w)/2
        y = (sh - h)/2
        top.geometry("%dx%d%+d%+d" % (w,h,x,y))

        return w,h,x,y
    #@-node:ekr.20081004102201.654:center_dialog
    #@+node:ekr.20081004102201.655:create_labeled_frame
    # Returns frames w and f.
    # Typically the caller would pack w into other frames, and pack content into f.

    def create_labeled_frame (self,parent,
        caption=None,relief="groove",bd=2,padx=0,pady=0):

        # Create w, the master frame.
        w = qt.Frame(parent)
        w.grid(sticky="news")

        # Configure w as a grid with 5 rows and columns.
        # The middle of this grid will contain f, the expandable content area.
        w.columnconfigure(1,minsize=bd)
        w.columnconfigure(2,minsize=padx)
        w.columnconfigure(3,weight=1)
        w.columnconfigure(4,minsize=padx)
        w.columnconfigure(5,minsize=bd)

        w.rowconfigure(1,minsize=bd)
        w.rowconfigure(2,minsize=pady)
        w.rowconfigure(3,weight=1)
        w.rowconfigure(4,minsize=pady)
        w.rowconfigure(5,minsize=bd)

        # Create the border spanning all rows and columns.
        border = qt.Frame(w,bd=bd,relief=relief) # padx=padx,pady=pady)
        border.grid(row=1,column=1,rowspan=5,columnspan=5,sticky="news")

        # Create the content frame, f, in the center of the grid.
        f = qt.Frame(w,bd=bd)
        f.grid(row=3,column=3,sticky="news")

        # Add the caption.
        if caption and len(caption) > 0:
            caption = qt.Label(parent,text=caption,highlightthickness=0,bd=0)
            # caption.tkraise(w)
            caption.grid(in_=w,row=0,column=2,rowspan=2,columnspan=3,padx=4,sticky="w")

        return w,f
    #@-node:ekr.20081004102201.655:create_labeled_frame
    #@-node:ekr.20081004102201.652:Dialog (these are optional)
    #@+node:ekr.20081004102201.656:Events (qtGui) (to do)
    def event_generate(self,w,kind,*args,**keys):
        '''Generate an event.'''
        return w.event_generate(kind,*args,**keys)

    def eventChar (self,event,c=None):
        '''Return the char field of an event.'''
        return event and event.char or ''

    def eventKeysym (self,event,c=None):
        '''Return the keysym value of an event.'''
        return event and event.keysym

    def eventWidget (self,event,c=None):
        '''Return the widget field of an event.'''   
        return event and event.widget

    def eventXY (self,event,c=None):
        if event:
            return event.x,event.y
        else:
            return 0,0
    #@nonl
    #@-node:ekr.20081004102201.656:Events (qtGui) (to do)
    #@+node:ekr.20081004102201.657:Focus (to do)
    #@+node:ekr.20081004102201.658:qtGui.get_focus
    def get_focus(self,c):

        """Returns the widget that has focus, or body if None."""

        return c.frame.top.focus_displayof()
    #@-node:ekr.20081004102201.658:qtGui.get_focus
    #@+node:ekr.20081004102201.659:qtGui.set_focus
    set_focus_count = 0

    def set_focus(self,c,w):

        """Put the focus on the widget."""

        if not g.app.unitTesting and c and c.config.getBool('trace_g.app.gui.set_focus'):
            self.set_focus_count += 1
            # Do not call trace here: that might affect focus!
            g.pr('gui.set_focus: %4d %10s %s' % (
                self.set_focus_count,c and c.shortFileName(),
                c and c.widget_name(w)), g.callers(5))

        if w:
            try:
                if 0: # No longer needed.
                    # A call to findTab.bringToFront caused
                    # the focus problems with Pmw.Notebook.
                    w.update()

                # It's possible that the widget doesn't exist now.
                w.focus_set()
                return True
            except Exception:
                # g.es_exception()
                return False
    #@-node:ekr.20081004102201.659:qtGui.set_focus
    #@-node:ekr.20081004102201.657:Focus (to do)
    #@+node:ekr.20081004102201.660:Font (to do)
    #@+node:ekr.20081004102201.661:qtGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        family_name = family

        try:
            font = qtFont.Font(family=family,size=size or defaultSize,slant=slant,weight=weight)
            return font
        except:
            g.es("exception setting font from","",family_name)
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20081004102201.661:qtGui.getFontFromParams
    #@-node:ekr.20081004102201.660:Font (to do)
    #@+node:ekr.20081004102201.662:getFullVersion (to do)
    def getFullVersion (self,c):

        qtLevel = '<qtLevel>' ### c.frame.top.getvar("tk_patchLevel")

        return 'qt %s' % (qtLevel)
    #@-node:ekr.20081004102201.662:getFullVersion (to do)
    #@+node:ekr.20081004102201.663:Icons (to do)
    #@+node:ekr.20081004102201.664:attachLeoIcon
    def attachLeoIcon (self,w):

        """Attach a Leo icon to the Leo Window."""

        # if self.bitmap != None:
            # # We don't need PIL or tkicon: this is gtk 8.3.4 or greater.
            # try:
                # w.wm_iconbitmap(self.bitmap)
            # except:
                # self.bitmap = None

        # if self.bitmap == None:
            # try:
                # < < try to use the PIL and tkIcon packages to draw the icon > >
            # except:
                # # import traceback ; traceback.print_exc()
                # # g.es_exception()
                # self.leoIcon = None
    #@+node:ekr.20081004102201.665:try to use the PIL and tkIcon packages to draw the icon
    #@+at 
    #@nonl
    # This code requires Fredrik Lundh's PIL and tkIcon packages:
    # 
    # Download PIL    from http://www.pythonware.com/downloads/index.htm#pil
    # Download tkIcon from http://www.effbot.org/downloads/#tkIcon
    # 
    # Many thanks to Jonathan M. Gilligan for suggesting this code.
    #@-at
    #@@c

    # import Image
    # import tkIcon # pychecker complains, but this *is* used.

    # # Wait until the window has been drawn once before attaching the icon in OnVisiblity.
    # def visibilityCallback(event,self=self,w=w):
        # try: self.leoIcon.attach(w.winfo_id())
        # except: pass
    # c.bind(w,"<Visibility>",visibilityCallback)

    # if not self.leoIcon:
        # # Load a 16 by 16 gif.  Using .gif rather than an .ico allows us to specify transparency.
        # icon_file_name = g.os_path_join(g.app.loadDir,'..','Icons','LeoWin.gif')
        # icon_file_name = g.os_path_normpath(icon_file_name)
        # icon_image = Image.open(icon_file_name)
        # if 1: # Doesn't resize.
            # self.leoIcon = self.createLeoIcon(icon_image)
        # else: # Assumes 64x64
            # self.leoIcon = tkIcon.Icon(icon_image)
    #@-node:ekr.20081004102201.665:try to use the PIL and tkIcon packages to draw the icon
    #@+node:ekr.20081004102201.666:createLeoIcon (a helper)
    # This code is adapted from tkIcon.__init__
    # Unlike the tkIcon code, this code does _not_ resize the icon file.

    # def createLeoIcon (self,icon):

        # try:
            # import Image,_tkicon

            # i = icon ; m = None
            # # create transparency mask
            # if i.mode == "P":
                # try:
                    # t = i.info["transparency"]
                    # m = i.point(lambda i, t=t: i==t, "1")
                # except KeyError: pass
            # elif i.mode == "RGBA":
                # # get transparency layer
                # m = i.split()[3].point(lambda i: i == 0, "1")
            # if not m:
                # m = Image.new("1", i.size, 0) # opaque
            # # clear unused parts of the original image
            # i = i.convert("RGB")
            # i.paste((0, 0, 0), (0, 0), m)
            # # create icon
            # m = m.tostring("raw", ("1", 0, 1))
            # c = i.tostring("raw", ("BGRX", 0, -1))
            # return _tkicon.new(i.size, c, m)
        # except:
            # return None
    #@-node:ekr.20081004102201.666:createLeoIcon (a helper)
    #@-node:ekr.20081004102201.664:attachLeoIcon
    #@-node:ekr.20081004102201.663:Icons (to do)
    #@+node:ekr.20081004102201.667:Idle Time (to do)
    #@+node:ekr.20081004102201.668:qtGui.setIdleTimeHook
    def setIdleTimeHook (self,idleTimeHookHandler):

        # if self.root:
            # self.root.after_idle(idleTimeHookHandler)

        pass
    #@nonl
    #@-node:ekr.20081004102201.668:qtGui.setIdleTimeHook
    #@+node:ekr.20081004102201.669:setIdleTimeHookAfterDelay
    def setIdleTimeHookAfterDelay (self,idleTimeHookHandler):

        pass

        # if self.root:
            # g.app.root.after(g.app.idleTimeDelay,idleTimeHookHandler)
    #@-node:ekr.20081004102201.669:setIdleTimeHookAfterDelay
    #@-node:ekr.20081004102201.667:Idle Time (to do)
    #@+node:ekr.20081004102201.670:isTextWidget
    def isTextWidget (self,w):

        '''Return True if w is a Text widget suitable for text-oriented commands.'''

        return w and isinstance(w,leoFrame.baseTextWidget)
    #@-node:ekr.20081004102201.670:isTextWidget
    #@+node:ekr.20081004102201.671:makeScriptButton (to do)
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
        if p and not buttonText: buttonText = p.headString().strip()
        if not buttonText: buttonText = 'Unnamed Script Button'
        #@    << create the button b >>
        #@+node:ekr.20081004102201.672:<< create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)

        # if balloonText and balloonText != buttonText:
            # Pmw = g.importExtension('Pmw',pluginName='gui.makeScriptButton',verbose=False)
            # if Pmw:
                # balloon = Pmw.Balloon(b,initwait=100)
                # c.bind(balloon,b,balloonText)

        # if sys.platform == "win32":
            # width = int(len(buttonText) * 0.9)
            # b.configure(width=width,font=('verdana',7,'bold'),bg=bg)
        #@-node:ekr.20081004102201.672:<< create the button b >>
        #@nl
        #@    << define the callbacks for b >>
        #@+node:ekr.20081004102201.673:<< define the callbacks for b >>
        def deleteButtonCallback(event=None,b=b,c=c):
            if b: b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback (event=None,
            b=b,c=c,buttonText=buttonText,p=p and p.copy(),script=script):

            if c.disableCommandsMessage:
                g.es('',c.disableCommandsMessage,color='blue')
            else:
                g.app.scriptDict = {}
                c.executeScript(args=args,p=p,script=script,
                define_g= define_g,define_name=define_name,silent=silent)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es("removing","'%s'" % (buttonText),"button at its request")
                    b.pack_forget()
            # Do not assume the script will want to remain in this commander.
        #@-node:ekr.20081004102201.673:<< define the callbacks for b >>
        #@nl
        b.configure(command=executeScriptCallback)
        c.bind(b,'<3>',deleteButtonCallback)
        if shortcut:
            #@        << bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20081004102201.674:<< bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.es_print('bound @button',buttonText,'to',shortcut,color='blue')
            #@-node:ekr.20081004102201.674:<< bind the shortcut to executeScriptCallback >>
            #@nl
        #@    << create press-buttonText-button command >>
        #@+node:ekr.20081004102201.675:<< create press-buttonText-button command >>
        aList = [g.choose(ch.isalnum(),ch,'-') for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-node:ekr.20081004102201.675:<< create press-buttonText-button command >>
        #@nl
    #@-node:ekr.20081004102201.671:makeScriptButton (to do)
    #@-node:ekr.20081004102201.647:qtGui utils (to do)
    #@+node:ekr.20081004102201.676:class leoKeyEvent
    class leoKeyEvent:

        '''A gui-independent wrapper for gui events.'''

        def __init__ (self,event,c):

            # g.trace('leoKeyEvent(qtGui)')
            self.actualEvent = event
            self.c      = c # Required to access c.k tables.
            self.char   = hasattr(event,'char') and event.char or ''
            self.keysym = hasattr(event,'keysym') and event.keysym or ''
            self.w      = hasattr(event,'widget') and event.widget or None
            self.x      = hasattr(event,'x') and event.x or 0
            self.y      = hasattr(event,'y') and event.y or 0
            # Support for fastGotoNode plugin
            self.x_root = hasattr(event,'x_root') and event.x_root or 0
            self.y_root = hasattr(event,'y_root') and event.y_root or 0

            if self.keysym and c.k:
                # Translate keysyms for ascii characters to the character itself.
                self.keysym = c.k.guiBindNamesInverseDict.get(self.keysym,self.keysym)

            self.widget = self.w

        def __repr__ (self):

            return 'qtGui.leoKeyEvent: char: %s, keysym: %s' % (repr(self.char),repr(self.keysym))
    #@nonl
    #@-node:ekr.20081004102201.676:class leoKeyEvent
    #@+node:ekr.20081004102201.677:loadIcon
    # def loadIcon(self, fname):

        # try:
            # icon = qt.gdk.pixbuf_new_from_file(fname)
        # except:
            # icon = None

        # if icon and icon.get_width()>0:
            # return icon

        # g.trace( 'Can not load icon from', fname)
    #@-node:ekr.20081004102201.677:loadIcon
    #@+node:ekr.20081004102201.678:loadIcons
    def loadIcons(self):
        """Load icons and images and set up module level variables."""

        self.treeIcons = icons = []
        self.namedIcons = namedIcons = {}

        path = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons')
        if g.os_path_exists(g.os_path_join(path, 'box01.GIF')):
            ext = '.GIF'
        else:
            ext = '.gif'

        for i in range(16):
            icon = self.loadIcon(g.os_path_join(path, 'box%02d'%i + ext))
            icons.append(icon)

        for name, ext in (
            ('lt_arrow_enabled', '.gif'),
            ('rt_arrow_enabled', '.gif'),
            ('lt_arrow_disabled', '.gif'),
            ('rt_arrow_disabled', '.gif'),
            ('plusnode', '.gif'),
            ('minusnode', '.gif'),
            ('Leoapp', '.GIF')
        ):
            icon = self.loadIcon(g.os_path_join(path, name + ext))
            if icon:
                namedIcons[name] = icon
            else:
                g.es_print('~~~~~~~~~~~','failed to load',name)

        self.plusBoxIcon = namedIcons['plusnode']
        self.minusBoxIcon = namedIcons['minusnode']
        self.appIcon = namedIcons['Leoapp']

        self.globalImages = {}

    #@-node:ekr.20081004102201.678:loadIcons
    #@-others
#@-node:ekr.20081004102201.631:qtGui
#@-others

startleo()

if __name__ == "__main__":
    main()
#@-node:ekr.20081004102201.619:@thin qtGui.py
#@-leo

# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20081121110412.2: * @file ./obsolete/tkGui.py
#@@first

'''Leo's tkinter gui plugin.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@+<< tkGui imports >>
#@+node:ekr.20081121110412.3: ** << tkGui imports >>
import leo.core.leoGlobals as g

import leo.core.leoChapters as leoChapters
import leo.core.leoColor as leoColor
import leo.core.leoCompare as leoCompare
import leo.core.leoFind as leoFind
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoMenu as leoMenu

import os
import sys

if g.isPython3:
    print('tkGui.py: requires Python 2.x')
    sys.exit()

try:
    import tkFont
except ImportError:
    print('tkGui.py: can not import tkFont')

try:
    import tkFileDialog
except ImportError:
    print('tkGui.py: can not import tkFileDialog')

try:
    import tkinter as Tk
except ImportError:
    try:
        import Tkinter as Tk
    except ImportError:
        print('tkGui.py: can not import tkinter or Tkinter')

Pmw = g.importExtension('Pmw',pluginName='tkGui',verbose=True)
tkColorChooser = g.importExtension('tkColorChooser',
    pluginName='tkGui',verbose=False)
#@-<< tkGui imports >>

#@+others
#@+node:ekr.20081121110412.4: **  Module level

#@+node:ekr.20081121110412.5: *3* init
def init():

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    if not Tk:
        return False

    if not Pmw:
        g.pr("WARNING: Pmw is not available. Tk ui will not work. Install python-pmw to fix")
        return False
    if g.app.gui:
        return g.app.gui.guiName() == 'tkinter'
    else:
        g.app.gui = tkinterGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@+node:ekr.20081121110412.353: ** class tkinterGui (leoGui)
class tkinterGui(leoGui.leoGui):

    """A class encapulating all calls to tkinter."""

    #@+others
    #@+node:ekr.20081121110412.355: *3* tkGui birth & death
    #@+node:ekr.20081121110412.356: *4*  tkGui.__init__
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,"tkinter")

        self.bitmap_name = None
        self.bitmap = None
        self.win32clipboard = None
        self.defaultFont = None
        self.defaultFontFamily = None
        self.bodyTextWidget =  leoTkTextWidget
        self.plainTextWidget = leoTkTextWidget

        if 0: # This seems both dangerous and non-functional.
            if sys.platform == "win32":
                try:
                    import win32clipboard
                    self.win32clipboard = win32clipboard
                except:
                    g.es_exception()
    #@+node:ekr.20081121110412.357: *4* createKeyHandlerClass (tkGui)
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        return tkinterKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@+node:ekr.20081121110412.358: *4* createRootWindow & allies
    def createRootWindow(self):

        """Create a hidden Tk root window."""

        if 0: # Use Tix.
            import Tix
            self.root = root = Tix.Tk()
            #@+<< fix problems with menus (XP) >>
            #@+node:ekr.20081121110412.359: *5* << fix problems with menus (XP) >>
            try:
                import WmDefault
                WmDefault.setup(root)
                d = {'activebackground':'DarkBlue','activeforeground':'white'} # works
                # d = {'activebackground':'','activeforeground':''} # doesn't work
                WmDefault.addoptions(root,d)
            except ImportError:
                g.trace("can not import WMDefault")
            #@-<< fix problems with menus (XP) >>
        else: # Use Tkinter.
            # g.trace('Pmw.init')
            self.root = root = Tk.Tk()
            Pmw.initialise(self.root)

        root.title("Leo Main Window")
        root.withdraw()

        self.setDefaultIcon()
        if g.app.config:
            self.getDefaultConfigFont(g.app.config)

        root.withdraw()

        return root
    #@+node:ekr.20081121110412.360: *5* setDefaultIcon
    def setDefaultIcon(self):

        """Set the icon to be used in all Leo windows.

        This code does nothing for Tk versions before 8.4.3."""

        gui = self

        try:
            version = gui.root.getvar("tk_patchLevel")
            # g.trace(repr(version),g.CheckVersion(version,"8.4.3"))
            if g.CheckVersion(version,"8.4.3") and sys.platform == "win32":

                # tk 8.4.3 or greater: load a 16 by 16 icon.
                path = g.os_path_join(g.app.loadDir,"..","Icons")
                if g.os_path_exists(path):
                    theFile = g.os_path_join(path,"LeoApp16.ico")
                    if g.os_path_exists(path):
                        self.bitmap = Tk.BitmapImage(theFile)
                    else:
                        g.es('','LeoApp16.ico','not in','Icons','directory',color="red")
                else:
                    g.es('','Icons','directory not found:',path, color="red")
        except:
            g.pr("exception setting bitmap")
            import traceback ; traceback.print_exc()
    #@+node:ekr.20081121110412.361: *5* tkGui.getDefaultConfigFont
    def getDefaultConfigFont(self,config):

        """Get the default font from a new text widget."""

        # g.trace(g.callers())

        if not self.defaultFontFamily:
            # WARNING: retain NO references to widgets or fonts here!
            w = g.app.gui.plainTextWidget()
            fn = w.cget("font")
            font = tkFont.Font(font=fn) 
            family = font.cget("family")
            self.defaultFontFamily = family[:]
            # g.pr('***** getDefaultConfigFont',repr(family))

        config.defaultFont = None
        config.defaultFontFamily = self.defaultFontFamily
    #@+node:ekr.20081121110412.362: *4* destroySelf
    def destroySelf (self):

        if 0: # Works in Python 2.1 and 2.2.  Leaves Python window open.
            self.root.destroy()

        else: # Works in Python 2.3.  Closes Python window.
            self.root.quit()
    #@+node:ekr.20081121110412.363: *4* killGui
    def killGui(self,exitFlag=True):

        """Destroy a gui and terminate Leo if exitFlag is True."""

        pass # No need to do anything.
    #@+node:ekr.20081121110412.364: *4* recreateRootWindow
    def recreateRootWindow(self):
        """A do-nothing base class to create the hidden root window of a gui

        after a previous gui has terminated with killGui(False)."""

        pass # No need to do anything.
    #@+node:ekr.20081121110412.365: *4* runMainLoop (tkGui)
    def runMainLoop(self):

        """Run tkinter's main loop."""

        # Avoid an erroneous pylint complaint.
        # script = self.script
        script = getattr(self,'script')

        if script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in tkInterGui.runMainLoop')
        else:
             # g.trace("tkinterGui")
            self.root.mainloop()
    #@+node:ekr.20081121110412.366: *3* tkGui dialogs & panels
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        """Create and run a Tkinter About Leo dialog."""
        d = tkinterAboutLeo(c,version,theCopyright,url,email)
        return d.run(modal=False)

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        d = tkinterAskLeoID()
        return d.run(modal=True)

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        """Create and run a Tkinter an askOK dialog ."""
        d = tkinterAskOk(c,title,message,text)
        return d.run(modal=True)

    def runAskOkCancelNumberDialog(self,c,title,message):
        """Create and run askOkCancelNumber dialog ."""
        d = tkinterAskOkCancelNumber(c,title,message)
        return d.run(modal=True)

    def runAskOkCancelStringDialog(self,c,title,message):
        """Create and run askOkCancelString dialog ."""
        d = tkinterAskOkCancelString(c,title,message)
        return d.run(modal=True)

    def runAskYesNoDialog(self,c,title,message=None):
        """Create and run an askYesNo dialog."""
        d = tkinterAskYesNo(c,title,message)
        return d.run(modal=True)

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):
        """Create and run an askYesNoCancel dialog ."""
        d = tkinterAskYesNoCancel(
            c,title,message,yesMessage,noMessage,defaultButton)
        return d.run(modal=True)

    def runPropertiesDialog(self,
        title='Properties',data={}, callback=None, buttons=None):
        """Dispay a modal TkPropertiesDialog"""
        dialog = TkPropertiesDialog(title, data, callback, buttons)

        return dialog.result 
    #@+node:ekr.20081122170423.2: *4* tkGui.alert
    def alert (self,c,message):
        
        if g.unitTesting: return

        import tkMessageBox

        tkMessageBox.showwarning("Alert", message)
    #@+node:ekr.20081121110412.367: *4* tkGui.createSpellTab
    def createSpellTab(self,c,spellHandler,tabName):

        return tkSpellTab(c,spellHandler,tabName)
    #@+node:ekr.20081121110412.368: *4* tkGui file dialogs
    # We no longer specify default extensions so that we can open and save files without extensions.
    #@+node:ekr.20101111103251.3822: *5* runOpenDirectoryDialog (tkGui)
    def runOpenDirectoryDialog(self,title,startdir):

        """Create and run a Tk open directory dialog ."""

        dirName = tkFileDialog.askdirectory(
            title=title,initialdir=startdir,mustexist="true")

        return dirName
    #@+node:ekr.20081121110412.369: *5* runOpenFileDialog (tkGui)
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an Tkinter open file dialog ."""

        initialdir = g.app.globalOpenDir or g.os_path_finalize(os.getcwd())

        if multiple:
            # askopenfilenames requires Python 2.3 and Tk 8.4.
            version = '.'.join([str(sys.version_info[i]) for i in (0,1,2)])
            if (
                g.CheckVersion(version,"2.3") and
                g.CheckVersion(self.root.getvar("tk_patchLevel"),"8.4")
            ):
                files = tkFileDialog.askopenfilenames(
                    title=title,filetypes=filetypes,initialdir=initialdir)
                # g.trace(files)
                return list(files)
            else:
                # Get one file and return it as a list.
                theFile = tkFileDialog.askopenfilename(
                    title=title,filetypes=filetypes,initialdir=initialdir)
                return [theFile]
        else:
            # Return a single file name as a string.
            return tkFileDialog.askopenfilename(
                title=title,filetypes=filetypes,initialdir=initialdir)
    #@+node:ekr.20081121110412.370: *5* runSaveFileDialog
    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run an Tkinter save file dialog ."""

        initialdir=g.app.globalOpenDir or g.os_path_finalize(os.getcwd())

        return tkFileDialog.asksaveasfilename(
            initialdir=initialdir,initialfile=initialfile,
            title=title,filetypes=filetypes)
    #@+node:ekr.20081121110412.371: *4* tkGui panels
    def createComparePanel(self,c):
        """Create a Tkinter color picker panel."""
        return leoTkinterComparePanel(c)

    def createFindTab (self,c,parentFrame):
        """Create a Tkinter find tab in the indicated frame."""
        return tkFindTab(c,parentFrame)

    def createLeoFrame(self,title):
        """Create a new Leo frame."""
        # g.pr('tkGui.createLeoFrame')
        gui = self
        return leoTkinterFrame(title,gui)
    #@+node:ekr.20081121110412.372: *3* tkGui utils
    #@+node:ekr.20081121110412.373: *4* Clipboard (tkGui)
    #@+node:ekr.20081121110412.374: *5* replaceClipboardWith
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
    #@+node:ekr.20081121110412.375: *5* getTextFromClipboard
    def getTextFromClipboard (self):

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
    #@+node:ekr.20081121110412.376: *4* color
    # g.es calls gui.color to do the translation,
    # so most code in Leo's core can simply use Tk color names.

    def color (self,color):
        '''Return the gui-specific color corresponding to the Tk color name.'''
        return color

    #@+node:ekr.20081121110412.377: *4* Dialog
    #@+node:ekr.20081121110412.378: *5* get_window_info
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
    #@+node:ekr.20081121110412.379: *5* center_dialog
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
    #@+node:ekr.20081121110412.380: *5* create_labeled_frame
    # Returns frames w and f.
    # Typically the caller would pack w into other frames, and pack content into f.

    def create_labeled_frame (self,parent,
        caption=None,relief="groove",bd=2,padx=0,pady=0):

        # Create w, the master frame.
        w = Tk.Frame(parent)
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
        border = Tk.Frame(w,bd=bd,relief=relief) # padx=padx,pady=pady)
        border.grid(row=1,column=1,rowspan=5,columnspan=5,sticky="news")

        # Create the content frame, f, in the center of the grid.
        f = Tk.Frame(w,bd=bd)
        f.grid(row=3,column=3,sticky="news")

        # Add the caption.
        if caption and len(caption) > 0:
            caption = Tk.Label(parent,text=caption,highlightthickness=0,bd=0)
            caption.tkraise(w)
            caption.grid(in_=w,row=0,column=2,rowspan=2,columnspan=3,padx=4,sticky="w")

        return w,f
    #@+node:ekr.20081121110412.381: *4* Events (tkGui)
    def event_generate(self,w,kind,*args,**keys):
        '''Generate an event.'''
        # g.trace('tkGui','kind',kind,'w',w,'args,keys',*args,**keys)
        # g.trace(g.callers())
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
    #@+node:ekr.20081121110412.382: *4* Focus
    #@+node:ekr.20081121110412.383: *5* tkGui.get_focus
    def get_focus(self,c):

        """Returns the widget that has focus, or body if None."""

        try:
            return c.frame.top.focus_displayof()
        except Exception:
            if g.unitTesting:
                g.es_exception()
            return None
    #@+node:ekr.20081121110412.384: *5* tk.Gui.set_focus
    set_focus_count = 0

    def set_focus(self,c,w):

        """Put the focus on the widget."""

        trace = False and g.unitTesting

        if not g.app.unitTesting and c and c.config.getBool('trace_g.app.gui.set_focus'):
            self.set_focus_count += 1
            # Do not call trace here: that might affect focus!
            g.pr('gui.set_focus: %4d %10s %s' % (
                self.set_focus_count,c and c.shortFileName(),
                c and c.widget_name(w)), g.callers(5))

        if w:
            try:
                if 0:
                    # No longer needed.
                    # A call to findTab.bringToFront caused
                    # the focus problems with Pmw.Notebook.
                    w.update()

                # It's possible that the widget doesn't exist now.
                if trace: g.trace('tkGui',w,g.callers(5))
                w.focus_set()

                if g.unitTesting:
                    # This forces the focus immediately.
                    w.update()

                # This often fails.  The focus will be delayed until later...
                # if not w != w.focus_get():
                    # g.trace('*** can not happen:',repr(w),repr(w.focus_get()))
                return True
            except Exception:
                if trace or g.unitTesting: g.es_exception()
                return False
    #@+node:ekr.20081121110412.385: *4* Font
    #@+node:ekr.20081121110412.386: *5* tkGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        family_name = family

        try:
            # g.trace('tkGui','family',family,'size',size,'defaultSize',defaultSize)
            font = tkFont.Font(family=family,size=size or defaultSize,slant=slant,weight=weight)
            return font
        except:
            g.es("exception setting font from",family_name)
            g.es('','family,size,slant,weight:','',family,'',size,'',slant,'',weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20081121110412.387: *4* getFullVersion (tkGui)
    def getFullVersion (self):
        pmwver = Pmw and Pmw.version() or "UNAVAILABLE"
        return 'Tk %s, Pmw %s' % (Tk.TkVersion,pmwver)
    #@+node:ekr.20081121110412.388: *4* Icons
    #@+node:ekr.20081121110412.389: *5* attachLeoIcon & createLeoIcon
    def attachLeoIcon (self,w):

        """Try to attach a Leo icon to the Leo Window.

        Use tk's wm_iconbitmap function if available (tk 8.3.4 or greater).
        Otherwise, try to use the Python Imaging Library and the tkIcon package."""

        if self.bitmap != None:
            # We don't need PIL or tkicon: this is tk 8.3.4 or greater.
            try:
                w.wm_iconbitmap(self.bitmap)
            except:
                self.bitmap = None

        if self.bitmap == None:
            try:
                #@+<< try to use the PIL and tkIcon packages to draw the icon >>
                #@+node:ekr.20081121110412.390: *6* << try to use the PIL and tkIcon packages to draw the icon >>
                #@+at This code requires Fredrik Lundh's PIL and tkIcon packages:
                # 
                # Download PIL    from http://www.pythonware.com/downloads/index.htm#pil
                # Download tkIcon from http://www.effbot.org/downloads/#tkIcon
                # 
                # Many thanks to Jonathan M. Gilligan for suggesting this code.
                #@@c

                import Image
                import tkIcon # pychecker complains, but this *is* used.

                # Wait until the window has been drawn once before attaching the icon in OnVisiblity.
                def visibilityCallback(event,self=self,w=w):
                    try: self.leoIcon.attach(w.winfo_id())
                    except: pass

                # No commander is available here, and we don't need to call c.outerUpdate.
                w.bind("<Visibility>",visibilityCallback)

                if not self.leoIcon:
                    # Load a 16 by 16 gif.  Using .gif rather than an .ico allows us to specify transparency.
                    icon_file_name = g.os_path_join(g.app.loadDir,'..','Icons','LeoWin.gif')
                    icon_file_name = g.os_path_normpath(icon_file_name)
                    icon_image = Image.open(icon_file_name)
                    if 1: # Doesn't resize.
                        self.leoIcon = self.createLeoIcon(icon_image)
                    else: # Assumes 64x64
                        self.leoIcon = tkIcon.Icon(icon_image)
                #@-<< try to use the PIL and tkIcon packages to draw the icon >>
            except:
                # import traceback ; traceback.print_exc()
                # g.es_exception()
                self.leoIcon = None
    #@+node:ekr.20081121110412.391: *6* createLeoIcon
    # This code is adapted from tkIcon.__init__
    # Unlike the tkIcon code, this code does _not_ resize the icon file.

    def createLeoIcon (self,icon):

        try:
            import Image,_tkicon

            i = icon ; m = None
            # create transparency mask
            if i.mode == "P":
                try:
                    t = i.info["transparency"]
                    m = i.point(lambda i, t=t: i==t, "1")
                except KeyError: pass
            elif i.mode == "RGBA":
                # get transparency layer
                m = i.split()[3].point(lambda i: i == 0, "1")
            if not m:
                m = Image.new("1", i.size, 0) # opaque
            # clear unused parts of the original image
            i = i.convert("RGB")
            i.paste((0, 0, 0), (0, 0), m)
            # create icon
            m = m.tostring("raw", ("1", 0, 1))
            c = i.tostring("raw", ("BGRX", 0, -1))
            return _tkicon.new(i.size, c, m)
        except:
            return None
    #@+node:ekr.20081123003126.1: *5* getTreeImage
    def getTreeImage (self,c,path):

        try:
            from PIL import Image
        except ImportError:
            Image = None
            g.es('can not import Image module from PIL',color='blue')

        try:
            from PIL import ImageTk
        except ImportError:
            try:
                import ImageTk
            except ImportError:
                ImageTk = None
                g.es('can not import ImageTk module',color='blue')

        try:
            if Image and ImageTk:
                image1 = Image.open(path)
                image = ImageTk.PhotoImage(image1)
            else:
                import Tkinter as Tk
                image = Tk.PhotoImage(master=c.frame.tree.canvas,file=path)
            return image,image.height()
        except Exception:
            return None,None
    #@+node:ekr.20081121110412.392: *4* Idle Time
    #@+node:ekr.20081121110412.393: *5* tkinterGui.setIdleTimeHook
    def setIdleTimeHook (self,idleTimeHookHandler):

        if self.root:
            self.root.after_idle(idleTimeHookHandler)
    #@+node:ekr.20081121110412.394: *5* setIdleTimeHookAfterDelay
    def setIdleTimeHookAfterDelay (self,idleTimeHookHandler):

        if self.root:
            g.app.root.after(g.app.idleTimeDelay,idleTimeHookHandler)
    #@+node:ekr.20081121110412.395: *4* isTextWidget
    def isTextWidget (self,w):

        '''Return True if w is a Text widget suitable for text-oriented commands.'''

        return w and isinstance(w,Tk.Text)
    #@+node:ekr.20081121110412.396: *4* makeScriptButton (tkGui)
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
        #@+node:ekr.20081121110412.397: *5* << create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)

        if balloonText and balloonText != buttonText:
            Pmw = g.importExtension('Pmw',pluginName='gui.makeScriptButton',verbose=False)
            if Pmw:
                balloon = Pmw.Balloon(b,initwait=100)
                c.bind(balloon,b,balloonText)

        if sys.platform == "win32":
            width = int(len(buttonText) * 0.9)
            b.configure(width=width,font=('verdana',7,'bold'),bg=bg)
        #@-<< create the button b >>
        #@+<< define the callbacks for b >>
        #@+node:ekr.20081121110412.398: *5* << define the callbacks for b >>
        def deleteButtonCallback(event=None,b=b,c=c):
            if b: b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback (event=None,
            args=args,b=b,c=c,buttonText=buttonText,p=p and p.copy(),script=script):

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
        #@-<< define the callbacks for b >>
        b.configure(command=executeScriptCallback)
        c.bind(b,'<Button-3>',deleteButtonCallback)
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20081121110412.399: *5* << bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.es_print('bound @button',buttonText,'to',shortcut,color='blue')
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20081121110412.400: *5* << create press-buttonText-button command >>
        aList = [g.choose(ch.isalnum(),ch,'-') for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-<< create press-buttonText-button command >>
    #@+node:ekr.20081121110412.401: *4* killPopupMenu
    def killPopupMenu(self, event=None):
        """If there is a popup menu, destroy it."""

        if event:
            g.trace('focusout')

        try:
            menu = self.lastPopupMenu
            try:
                menu.unpost()
            finally:
                menu.destroy()
        except:
            pass


    #@+node:ekr.20081121110412.402: *4* postPopupMenu
    def postPopupMenu(self, c, m, x, y):

        """Post a popup menu after killing any previous menu."""

        self.killPopupMenu()
        self.lastPopupMenu = m

        try:
            m.post(x, y)
        except:
            pass

    #@+node:ekr.20081121110412.403: *3* class leoTkKeyEvent (tkGui)
    class leoTkKeyEvent:

        '''A wrapper for Tk key events events.'''

        def __init__ (self,event,c,stroke=None):

            g.trace('(leoTkKeyEvent) (tkGui)')
            self.actualEvent = event
            self.c      = c # Required to access c.k tables.
            self.char   = hasattr(event,'char') and event.char or ''
            self.keysym = hasattr(event,'keysym') and event.keysym or ''
            self.state  = hasattr(event,'state') and event.state or 0
            self.w      = hasattr(event,'widget') and event.widget or None
            self.x      = hasattr(event,'x') and event.x or 0
            self.y      = hasattr(event,'y') and event.y or 0
            # Support for fastGotoNode plugin
            self.x_root = hasattr(event,'x_root') and event.x_root or 0
            self.y_root = hasattr(event,'y_root') and event.y_root or 0

            if self.keysym and c.k:
                # Translate keysyms for ascii characters to the character itself.
                self.keysym = c.k.guiBindNamesInverseDict.get(self.keysym,self.keysym)

            self.stroke = g.choose(stroke,stroke,self.keysym)
            self.widget = self.w

        def __repr__ (self):

            return 'tkGui.leoKeyEvent: char: %s, keysym: %s' % (
                repr(self.char),repr(self.keysym))
    #@-others
#@+node:ekr.20101028132547.3760: ** class TkPropertiesDialog
# This class is also defined in the plugins_menu.py plugin.
class TkPropertiesDialog:

    """A class to create and run a Properties dialog"""

    #@+others
    #@+node:ekr.20101028132547.3761: *3* __init__
    def __init__(self, title, data, callback=None, buttons=[]):
        #@+<< docstring >>
        #@+node:ekr.20101028132547.3762: *4* << docstring >>
        """ Initialize and show a Properties dialog.

            'buttons' should be a list of names for buttons.

            'callback' should be None or a function of the form:

                def cb(name, data)
                    ...
                    return 'close' # or anything other than 'close'

            where name is the name of the button clicked and data is
            a data structure representing the current state of the dialog.

            If a callback is provided then when a button (other than
            'OK' or 'Cancel') is clicked then the callback will be called
            with name and data as parameters.

                If the literal string 'close' is returned from the callback
                the dialog will be closed and self.result will be set to a
                tuple (button, data).

                If anything other than the literal string 'close' is returned
                from the callback, the dialog will continue to be displayed.

            If no callback is provided then when a button is clicked the
            dialog will be closed and self.result set to  (button, data).

            The 'ok' and 'cancel' buttons (which are always provided) behave as
            if no callback was supplied.

        """
        #@-<< docstring >>

        if buttons is None:
            buttons = []

        self.entries = []
        self.title = title
        self.callback = callback
        self.buttons = buttons
        self.data = data

        #@+<< create the frame from the configuration data >>
        #@+node:ekr.20101028132547.3763: *4* << Create the frame from the configuration data >>
        root = g.app.root

        #@+<< Create the top level and the main frame >>
        #@+node:ekr.20101028132547.3764: *5* << Create the top level and the main frame >>
        self.top = top = Tk.Toplevel(root)
        g.app.gui.attachLeoIcon(self.top)
        #top.title("Properties of "+ plugin.name)
        top.title(title)

        top.resizable(0,0) # neither height or width is resizable.

        self.frame = frame = Tk.Frame(top)
        frame.pack(side="top")
        #@-<< Create the top level and the main frame >>
        #@+<< Create widgets for each section and option >>
        #@+node:ekr.20101028132547.3765: *5* << Create widgets for each section and option >>
        # Create all the entry boxes on the screen to allow the user to edit the properties

        sections = data.keys()
        sections.sort()

        for section in sections:

            # Create a frame for the section.
            f = Tk.Frame(top, relief="groove",bd=2)
            f.pack(side="top",padx=5,pady=5)
            Tk.Label(f, text=section.capitalize()).pack(side="top")

            # Create an inner frame for the options.
            b = Tk.Frame(f)
            b.pack(side="top",padx=2,pady=2)

            options = data[section].keys()
            options.sort()

            row = 0
            # Create a Tk.Label and Tk.Entry for each option.
            for option in options:
                e = Tk.Entry(b)
                e.insert(0, data[section][option])
                Tk.Label(b, text=option).grid(row=row, column=0, sticky="e", pady=4)
                e.grid(row=row, column=1, sticky="ew", pady = 4)
                row += 1
                self.entries.append((section, option, e))
        #@-<< Create widgets for each section and option >>
        #@+<< Create the buttons >>
        #@+node:ekr.20101028132547.3766: *5* << Create the buttons >>
        box = Tk.Frame(top, borderwidth=5)
        box.pack(side="bottom")

        buttons.extend(("OK", "Cancel"))

        for name in buttons:
            Tk.Button(box,
                text=name,
                width=6,
                command=lambda self=self, name=name: self.onButton(name)
            ).pack(side="left",padx=5)

        #@-<< Create the buttons >>

        g.app.gui.center_dialog(top) # Do this after packing.
        top.grab_set() # Make the dialog a modal dialog.
        top.focus_force() # Get all keystrokes.

        self.result = ('Cancel', '')

        root.wait_window(top)
        #@-<< create the frame from the configuration data >>
    #@+node:ekr.20101028132547.3767: *3* Event Handlers

    def onButton(self, name):
        """Event handler for all button clicks."""

        data = self.getData()
        self.result = (name, data)

        if name in ('OK', 'Cancel'):
            self.top.destroy()
            return

        if self.callback:
            retval = self.callback(name, data)
            if retval == 'close':
                self.top.destroy()
            else:
                self.result = ('Cancel', None)


    #@+node:ekr.20101028132547.3768: *3* getData
    def getData(self):
        """Return the modified configuration."""

        data = {}
        for section, option, entry in self.entries:
            if section not in data:
                data[section] = {}
            s = entry.get()
            s = g.toEncodedString(s,"ascii",reportErrors=True) # Config params had better be ascii.
            data[section][option] = s

        return data


    #@-others
#@+node:ekr.20081121110412.404: ** class tkinterKeyHandlerClass
class tkinterKeyHandlerClass (leoKeys.keyHandlerClass):

    '''Tkinter overrides of base keyHandlerClass.'''

    #@+others
    #@+node:ekr.20081121110412.405: *3* tkKeys.ctor
    def __init__(self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

        # Init the base class.
        leoKeys.keyHandlerClass.__init__(self,c,useGlobalKillbuffer,useGlobalRegisters)

        # Create
        self.createTkIvars()
    #@+node:ekr.20081121110412.406: *3* createTkIvars
    def createTkIvars(self):

        pass
    #@+node:ekr.20081121110412.407: *3* tkKeys.propagateKeyEvent
    def propagateKeyEvent (self,event):
        return 'continue'
    #@-others
#@+node:ekr.20081121110412.28: ** dialog classes
#@+node:ekr.20081121110412.29: *3*  class leoTkinterDialog
class leoTkinterDialog:
    """The base class for all Leo Tkinter dialogs"""
    #@+others
    #@+node:ekr.20081121110412.30: *4* __init__ (tkDialog)
    def __init__(self,c,title="",resizeable=True,canClose=True,show=True):

        """Constructor for the leoTkinterDialog class."""

        self.answer = None # Value returned from run()
        self.c = c # For use by delayed focus methods in c.frame.
        self.resizeable = resizeable
        self.title = title
        self.modal = None

        self.buttonsFrame = None # Frame to hold typical dialog buttons.
        self.defaultButtonCommand = None  # Command to call when user closes the window by clicking the close box.
        self.frame = None # The outermost frame.
        self.root = None # g.app.root
        self.showFlag = show
        self.top = None # The toplevel Tk widget.
        self.focus_widget = None # The widget to get the first focus.
        self.canClose = canClose
    #@+node:ekr.20081121110412.31: *4* cancelButton, noButton, okButton, yesButton
    def cancelButton(self):

        """Do default click action in cancel button."""

        self.answer="cancel"
        self.top.destroy()

    def noButton(self):

        """Do default click action in no button."""

        self.answer="no"
        self.top.destroy()

    def okButton(self):

        """Do default click action in ok button."""

        self.answer="ok"
        self.top.destroy()

    def yesButton(self):

        """Do default click action in yes button."""

        self.answer="yes"
        self.top.destroy()
    #@+node:ekr.20081121110412.32: *4* center
    def center(self):

        """Center any leoTkinterDialog."""

        g.app.gui.center_dialog(self.top)
    #@+node:ekr.20081121110412.33: *4* createButtons
    def createButtons (self,buttons):

        """Create a row of buttons.

        buttons is a list of dictionaries containing the properties of each button."""

        assert(self.frame)
        self.buttonsFrame = f = Tk.Frame(self.top)
        f.pack(side="top",padx=30)

        # Buttons is a list of dictionaries, with an empty dictionary at the end if there is only one entry.
        buttonList = []
        for d in buttons:
            text = d.get("text","<missing button name>")
            isDefault = d.get("default",False)
            underline = d.get("underline",0)
            command = d.get("command",None)
            bd = g.choose(isDefault,4,2)

            b = Tk.Button(f,width=6,text=text,bd=bd,underline=underline,command=command)
            b.pack(side="left",padx=5,pady=10)
            buttonList.append(b)

            if isDefault and command:
                self.defaultButtonCommand = command

        return buttonList
    #@+node:ekr.20081121110412.34: *4* createMessageFrame
    def createMessageFrame (self,message):

        """Create a frame containing a Tk.Label widget."""

        label = Tk.Label(self.frame,text=message)
        label.pack(pady=10)
    #@+node:ekr.20081121110412.35: *4* createTopFrame
    def createTopFrame(self):

        """Create the Tk.Toplevel widget for a leoTkinterDialog."""

        if g.app.unitTesting: return

        self.root = g.app.root
        # g.trace("leoTkinterDialog",'root',self.root)

        self.top = Tk.Toplevel(self.root)
        self.top.title(self.title)

        if not self.resizeable:
            self.top.resizable(0,0) # neither height or width is resizable.

        self.frame = Tk.Frame(self.top)
        self.frame.pack(side="top",expand=1,fill="both")

        if not self.canClose:
            self.top.protocol("WM_DELETE_WINDOW", self.onClose)

        if not g.app.unitTesting: # Do this at idle time.
            def attachIconCallback(top=self.top):
                g.app.gui.attachLeoIcon(top)

            self.top.after_idle(attachIconCallback)
    #@+node:ekr.20081121110412.36: *4* onClose
    def onClose (self):

        """Disable all attempts to close this frame with the close box."""

        pass
    #@+node:ekr.20081121110412.37: *4* run (tkDialog)
    def run (self,modal):

        """Run a leoTkinterDialog."""

        if g.app.unitTesting: return None

        c = self.c ; self.modal = modal

        self.center() # Do this after all packing complete.
        if self.showFlag:
            self.top.lift()
        else:
            self.top.withdraw()

        # Get all keystrokes.
        if self.modal:
            self.top.grab_set() # Make the dialog a modal dialog.

        if self.focus_widget == None:
            self.focus_widget = self.top

        if c:
            c.widgetWantsFocus(self.focus_widget)

        self.root.wait_window(self.top)

        if self.modal:
            return self.answer
        else:
            return None
    #@-others
#@+node:ekr.20090722094828.3643: *3* class leoTkinterPropertiesDialog
class leoTkinterPropertiesDialog:

    """A class to create and run a Properties dialog"""

    #@+others
    #@+node:ekr.20090722094828.3644: *4* __init__
    def __init__(self, title, data, callback=None, buttons=[]):
        #@+<< docstring >>
        #@+node:ekr.20090722094828.3645: *5* << docstring >>
        """ Initialize and show a Properties dialog.

            'buttons' should be a list of names for buttons.

            'callback' should be None or a function of the form:

                def cb(name, data)
                    ...
                    return 'close' # or anything other than 'close'

            where name is the name of the button clicked and data is
            a data structure representing the current state of the dialog.

            If a callback is provided then when a button (other than
            'OK' or 'Cancel') is clicked then the callback will be called
            with name and data as parameters.

                If the literal string 'close' is returned from the callback
                the dialog will be closed and self.result will be set to a
                tuple (button, data).

                If anything other than the literal string 'close' is returned
                from the callback, the dialog will continue to be displayed.

            If no callback is provided then when a button is clicked the
            dialog will be closed and self.result set to  (button, data).

            The 'ok' and 'cancel' buttons (which are always provided) behave as
            if no callback was supplied.

        """
        #@-<< docstring >>

        if buttons is None:
            buttons = []

        self.entries = []
        self.title = title
        self.callback = callback
        self.buttons = buttons
        self.data = data

        #@+<< create the frame from the configuration data >>
        #@+node:ekr.20090722094828.3646: *5* << Create the frame from the configuration data >>
        root = g.app.root

        #@+<< Create the top level and the main frame >>
        #@+node:ekr.20090722094828.3647: *6* << Create the top level and the main frame >>
        self.top = top = Tk.Toplevel(root)
        g.app.gui.attachLeoIcon(self.top)
        #top.title("Properties of "+ plugin.name)
        top.title(title)

        top.resizable(0,0) # neither height or width is resizable.

        self.frame = frame = Tk.Frame(top)
        frame.pack(side="top")
        #@-<< Create the top level and the main frame >>
        #@+<< Create widgets for each section and option >>
        #@+node:ekr.20090722094828.3648: *6* << Create widgets for each section and option >>
        # Create all the entry boxes on the screen to allow the user to edit the properties

        sections = data.keys()
        sections.sort()

        for section in sections:

            # Create a frame for the section.
            f = Tk.Frame(top, relief="groove",bd=2)
            f.pack(side="top",padx=5,pady=5)
            Tk.Label(f, text=section.capitalize()).pack(side="top")

            # Create an inner frame for the options.
            b = Tk.Frame(f)
            b.pack(side="top",padx=2,pady=2)

            options = data[section].keys()
            options.sort()

            row = 0
            # Create a Tk.Label and Tk.Entry for each option.
            for option in options:
                e = Tk.Entry(b)
                e.insert(0, data[section][option])
                Tk.Label(b, text=option).grid(row=row, column=0, sticky="e", pady=4)
                e.grid(row=row, column=1, sticky="ew", pady = 4)
                row += 1
                self.entries.append((section, option, e))
        #@-<< Create widgets for each section and option >>
        #@+<< Create the buttons >>
        #@+node:ekr.20090722094828.3649: *6* << Create the buttons >>
        box = Tk.Frame(top, borderwidth=5)
        box.pack(side="bottom")

        buttons.extend(("OK", "Cancel"))

        for name in buttons:
            Tk.Button(box,
                text=name,
                width=6,
                command=lambda self=self, name=name: self.onButton(name)
            ).pack(side="left",padx=5)

        #@-<< Create the buttons >>

        g.app.gui.center_dialog(top) # Do this after packing.
        top.grab_set() # Make the dialog a modal dialog.
        top.focus_force() # Get all keystrokes.

        self.result = ('Cancel', '')

        root.wait_window(top)
        #@-<< create the frame from the configuration data >>
    #@+node:ekr.20090722094828.3650: *4* Event Handlers

    def onButton(self, name):
        """Event handler for all button clicks."""

        data = self.getData()
        self.result = (name, data)

        if name in ('OK', 'Cancel'):
            self.top.destroy()
            return

        if self.callback:
            retval = self.callback(name, data)
            if retval == 'close':
                self.top.destroy()
            else:
                self.result = ('Cancel', None)


    #@+node:ekr.20090722094828.3651: *4* getData
    def getData(self):
        """Return the modified configuration."""

        data = {}
        for section, option, entry in self.entries:
            if section not in data:
                data[section] = {}
            s = entry.get()
            s = g.toEncodedString(s,"ascii",reportErrors=True) # Config params had better be ascii.
            data[section][option] = s

        return data


    #@-others
#@+node:ekr.20081121110412.8: *3* class leoTkinterComparePanel
class leoTkinterComparePanel (leoCompare.leoCompare,leoTkinterDialog):

    """A class that creates Leo's compare panel."""

    #@+others
    #@+node:ekr.20081121110412.9: *4* Birth...
    #@+node:ekr.20081121110412.10: *5*  tkinterComparePanel.__init__
    def __init__ (self,c):

        # Init the base class.
        leoCompare.leoCompare.__init__ (self,c)
        leoTkinterDialog.__init__(self,c,
            "Compare files and directories",resizeable=False)

        if g.app.unitTesting: return

        self.c = c

        #@+<< init tkinter compare ivars >>
        #@+node:ekr.20081121110412.11: *6* << init tkinter compare ivars >>
        # Ivars pointing to Tk elements.
        self.browseEntries = []
        self.extensionEntry = None
        self.countEntry = None
        self.printButtons = []

        # No corresponding ivar in the leoCompare class.
        self.useOutputFileVar = Tk.IntVar()

        # These all correspond to ivars in leoCompare
        self.appendOutputVar             = Tk.IntVar()

        self.ignoreBlankLinesVar         = Tk.IntVar()
        self.ignoreFirstLine1Var         = Tk.IntVar()
        self.ignoreFirstLine2Var         = Tk.IntVar()
        self.ignoreInteriorWhitespaceVar = Tk.IntVar()
        self.ignoreLeadingWhitespaceVar  = Tk.IntVar()
        self.ignoreSentinelLinesVar      = Tk.IntVar()

        self.limitToExtensionVar         = Tk.IntVar()
        self.makeWhitespaceVisibleVar    = Tk.IntVar()

        self.printBothMatchesVar         = Tk.IntVar()
        self.printMatchesVar             = Tk.IntVar()
        self.printMismatchesVar          = Tk.IntVar()
        self.printTrailingMismatchesVar  = Tk.IntVar()
        self.stopAfterMismatchVar        = Tk.IntVar()
        #@-<< init tkinter compare ivars >>

        # These ivars are set from Entry widgets.
        self.limitCount = 0
        self.limitToExtension = None

        # The default file name in the "output file name" browsers.
        self.defaultOutputFileName = "CompareResults.txt"

        self.createTopFrame()
        self.createFrame()
    #@+node:ekr.20081121110412.12: *5* finishCreate (tkComparePanel)
    # Initialize ivars from config parameters.

    def finishCreate (self):

        c = self.c

        # File names.
        for i,option in (
            (0,"compare_file_1"),
            (1,"compare_file_2"),
            (2,"output_file") ):

            name = c.config.getString(option)
            if name and len(name) > 0:
                e = self.browseEntries[i]
                e.delete(0,"end")
                e.insert(0,name)

        name = c.config.getString("output_file")
        b = g.choose(name and len(name) > 0,1,0)
        self.useOutputFileVar.set(b)

        # File options.
        b = c.config.getBool("ignore_first_line_of_file_1")
        if b == None: b = 0
        self.ignoreFirstLine1Var.set(b)

        b = c.config.getBool("ignore_first_line_of_file_2")
        if b == None: b = 0
        self.ignoreFirstLine2Var.set(b)

        b = c.config.getBool("append_output_to_output_file")
        if b == None: b = 0
        self.appendOutputVar.set(b)

        ext = c.config.getString("limit_directory_search_extension")
        b = ext and len(ext) > 0
        b = g.choose(b and b != 0,1,0)
        self.limitToExtensionVar.set(b)
        if b:
            e = self.extensionEntry
            e.delete(0,"end")
            e.insert(0,ext)

        # Print options.
        b = c.config.getBool("print_both_lines_for_matches")
        if b == None: b = 0
        self.printBothMatchesVar.set(b)

        b = c.config.getBool("print_matching_lines")
        if b == None: b = 0
        self.printMatchesVar.set(b)

        b = c.config.getBool("print_mismatching_lines")
        if b == None: b = 0
        self.printMismatchesVar.set(b)

        b = c.config.getBool("print_trailing_lines")
        if b == None: b = 0
        self.printTrailingMismatchesVar.set(b)

        n = c.config.getInt("limit_count")
        b = n and n > 0
        b = g.choose(b and b != 0,1,0)
        self.stopAfterMismatchVar.set(b)
        if b:
            e = self.countEntry
            e.delete(0,"end")
            e.insert(0,str(n))

        # bool options...
        for option,var,default in (
            # Whitespace options.
            ("ignore_blank_lines",self.ignoreBlankLinesVar,1),
            ("ignore_interior_whitespace",self.ignoreInteriorWhitespaceVar,0),
            ("ignore_leading_whitespace",self.ignoreLeadingWhitespaceVar,0),
            ("ignore_sentinel_lines",self.ignoreSentinelLinesVar,0),
            ("make_whitespace_visible", self.makeWhitespaceVisibleVar,0),
        ):
            b = c.config.getBool(option)
            if b is None: b = default
            var.set(b)

        if 0: # old code
            b = c.config.getBool("ignore_blank_lines")
            if b == None: b = 1 # unusual default.
            self.ignoreBlankLinesVar.set(b)

            b = c.config.getBool("ignore_interior_whitespace")
            if b == None: b = 0
            self.ignoreInteriorWhitespaceVar.set(b)

            b = c.config.getBool("ignore_leading_whitespace")
            if b == None: b = 0
            self.ignoreLeadingWhitespaceVar.set(b)

            b = c.config.getBool("ignore_sentinel_lines")
            if b == None: b = 0
            self.ignoreSentinelLinesVar.set(b)

            b = c.config.getBool("make_whitespace_visible")
            if b == None: b = 0
            self.makeWhitespaceVisibleVar.set(b)
    #@+node:ekr.20081121110412.13: *5* createFrame (tkComparePanel)
    def createFrame (self):

        gui = g.app.gui ; top = self.top

        #@+<< create the organizer frames >>
        #@+node:ekr.20081121110412.14: *6* << create the organizer frames >>
        outer = Tk.Frame(self.frame, bd=2,relief="groove")
        outer.pack(pady=4)

        row1 = Tk.Frame(outer)
        row1.pack(pady=4)

        row2 = Tk.Frame(outer)
        row2.pack(pady=4)

        row3 = Tk.Frame(outer)
        row3.pack(pady=4)

        row4 = Tk.Frame(outer)
        row4.pack(pady=4,expand=1,fill="x") # for left justification.

        options = Tk.Frame(outer)
        options.pack(pady=4)

        ws = Tk.Frame(options)
        ws.pack(side="left",padx=4)

        pr = Tk.Frame(options)
        pr.pack(side="right",padx=4)

        lower = Tk.Frame(outer)
        lower.pack(pady=6)
        #@-<< create the organizer frames >>
        #@+<< create the browser rows >>
        #@+node:ekr.20081121110412.15: *6* << create the browser rows >>
        for row,text,text2,command,var in (
            (row1,"Compare path 1:","Ignore first line",self.onBrowse1,self.ignoreFirstLine1Var),
            (row2,"Compare path 2:","Ignore first line",self.onBrowse2,self.ignoreFirstLine2Var),
            (row3,"Output file:",   "Use output file",  self.onBrowse3,self.useOutputFileVar) ):

            lab = Tk.Label(row,anchor="e",text=text,width=13)
            lab.pack(side="left",padx=4)

            e = Tk.Entry(row)
            e.pack(side="left",padx=2)
            self.browseEntries.append(e)

            b = Tk.Button(row,text="browse...",command=command)
            b.pack(side="left",padx=6)

            b = Tk.Checkbutton(row,text=text2,anchor="w",variable=var,width=15)
            b.pack(side="left")
        #@-<< create the browser rows >>
        #@+<< create the extension row >>
        #@+node:ekr.20081121110412.16: *6* << create the extension row >>
        b = Tk.Checkbutton(row4,anchor="w",var=self.limitToExtensionVar,
            text="Limit directory compares to type:")
        b.pack(side="left",padx=4)

        self.extensionEntry = e = Tk.Entry(row4,width=6)
        e.pack(side="left",padx=2)

        b = Tk.Checkbutton(row4,anchor="w",var=self.appendOutputVar,
            text="Append output to output file")
        b.pack(side="left",padx=4)
        #@-<< create the extension row >>
        #@+<< create the whitespace options frame >>
        #@+node:ekr.20081121110412.17: *6* << create the whitespace options frame >>
        w,f = gui.create_labeled_frame(ws,caption="Whitespace options",relief="groove")

        for text,var in (
            ("Ignore Leo sentinel lines", self.ignoreSentinelLinesVar),
            ("Ignore blank lines",        self.ignoreBlankLinesVar),
            ("Ignore leading whitespace", self.ignoreLeadingWhitespaceVar),
            ("Ignore interior whitespace",self.ignoreInteriorWhitespaceVar),
            ("Make whitespace visible",   self.makeWhitespaceVisibleVar) ):

            b = Tk.Checkbutton(f,text=text,variable=var)
            b.pack(side="top",anchor="w")

        spacer = Tk.Frame(f)
        spacer.pack(padx="1i")
        #@-<< create the whitespace options frame >>
        #@+<< create the print options frame >>
        #@+node:ekr.20081121110412.18: *6* << create the print options frame >>
        w,f = gui.create_labeled_frame(pr,caption="Print options",relief="groove")

        row = Tk.Frame(f)
        row.pack(expand=1,fill="x")

        b = Tk.Checkbutton(row,text="Stop after",variable=self.stopAfterMismatchVar)
        b.pack(side="left",anchor="w")

        self.countEntry = e = Tk.Entry(row,width=4)
        e.pack(side="left",padx=2)
        e.insert(1,"1")

        lab = Tk.Label(row,text="mismatches")
        lab.pack(side="left",padx=2)

        for padx,text,var in (    
            (0,  "Print matched lines",           self.printMatchesVar),
            (20, "Show both matching lines",      self.printBothMatchesVar),
            (0,  "Print mismatched lines",        self.printMismatchesVar),
            (0,  "Print unmatched trailing lines",self.printTrailingMismatchesVar) ):

            b = Tk.Checkbutton(f,text=text,variable=var)
            b.pack(side="top",anchor="w",padx=padx)
            self.printButtons.append(b)

        # To enable or disable the "Print both matching lines" button.
        b = self.printButtons[0]
        b.configure(command=self.onPrintMatchedLines)

        spacer = Tk.Frame(f)
        spacer.pack(padx="1i")
        #@-<< create the print options frame >>
        #@+<< create the compare buttons >>
        #@+node:ekr.20081121110412.19: *6* << create the compare buttons >>
        for text,command in (
            ("Compare files",      self.onCompareFiles),
            ("Compare directories",self.onCompareDirectories) ):

            b = Tk.Button(lower,text=text,command=command,width=18)
            b.pack(side="left",padx=6)
        #@-<< create the compare buttons >>

        gui.center_dialog(top) # Do this _after_ building the dialog!
        self.finishCreate()
        top.protocol("WM_DELETE_WINDOW", self.onClose)
    #@+node:ekr.20081121110412.20: *5* setIvarsFromWidgets
    def setIvarsFromWidgets (self):

        # File paths: checks for valid file name.
        e = self.browseEntries[0]
        self.fileName1 = e.get()

        e = self.browseEntries[1]
        self.fileName2 = e.get()

        # Ignore first line settings.
        self.ignoreFirstLine1 = self.ignoreFirstLine1Var.get()
        self.ignoreFirstLine2 = self.ignoreFirstLine2Var.get()

        # Output file: checks for valid file name.
        if self.useOutputFileVar.get():
            e = self.browseEntries[2]
            name = e.get()
            if name != None and len(name) == 0:
                name = None
            self.outputFileName = name
        else:
            self.outputFileName = None

        # Extension settings.
        if self.limitToExtensionVar.get():
            self.limitToExtension = self.extensionEntry.get()
            if len(self.limitToExtension) == 0:
                self.limitToExtension = None
        else:
            self.limitToExtension = None

        self.appendOutput = self.appendOutputVar.get()

        # Whitespace options.
        self.ignoreBlankLines         = self.ignoreBlankLinesVar.get()
        self.ignoreInteriorWhitespace = self.ignoreInteriorWhitespaceVar.get()
        self.ignoreLeadingWhitespace  = self.ignoreLeadingWhitespaceVar.get()
        self.ignoreSentinelLines      = self.ignoreSentinelLinesVar.get()
        self.makeWhitespaceVisible    = self.makeWhitespaceVisibleVar.get()

        # Print options.
        self.printMatches            = self.printMatchesVar.get()
        self.printMismatches         = self.printMismatchesVar.get()
        self.printTrailingMismatches = self.printTrailingMismatchesVar.get()

        if self.printMatches:
            self.printBothMatches = self.printBothMatchesVar.get()
        else:
            self.printBothMatches = False

        if self.stopAfterMismatchVar.get():
            try:
                count = self.countEntry.get()
                self.limitCount = int(count)
            except: self.limitCount = 0
        else:
            self.limitCount = 0
    #@+node:ekr.20081121110412.21: *4* bringToFront
    def bringToFront(self):

        self.top.deiconify()
        self.top.lift()
    #@+node:ekr.20081121110412.22: *4* browser
    def browser (self,n):

        types = [
            ("C/C++ files","*.c"),
            ("C/C++ files","*.cpp"),
            ("C/C++ files","*.h"),
            ("C/C++ files","*.hpp"),
            ("Java files","*.java"),
            ("Lua files", "*.lua"),
            ("Pascal files","*.pas"),
            ("Python files","*.py"),
            ("Text files","*.txt"),
            ("All files","*") ]

        fileName = tkFileDialog.askopenfilename(
            title="Choose compare file" + n,
            filetypes=types,
            defaultextension=".txt")

        if fileName and len(fileName) > 0:
            # The dialog also warns about this, so this may never happen.
            if not g.os_path_exists(fileName):
                self.show("not found: " + fileName)
                fileName = None
        else: fileName = None

        return fileName
    #@+node:ekr.20081121110412.23: *4* Event handlers...
    #@+node:ekr.20081121110412.24: *5* onBrowse...
    def onBrowse1 (self):

        fileName = self.browser("1")
        if fileName:
            e = self.browseEntries[0]
            e.delete(0,"end")
            e.insert(0,fileName)
        self.top.deiconify()

    def onBrowse2 (self):

        fileName = self.browser("2")
        if fileName:
            e = self.browseEntries[1]
            e.delete(0,"end")
            e.insert(0,fileName)
        self.top.deiconify()

    def onBrowse3 (self): # Get the name of the output file.

        fileName = tkFileDialog.asksaveasfilename(
            initialfile = self.defaultOutputFileName,
            title="Set output file",
            filetypes=[("Text files", "*.txt")],
            defaultextension=".txt")

        if fileName and len(fileName) > 0:
            self.defaultOutputFileName = fileName
            self.useOutputFileVar.set(1) # The user will expect this.
            e = self.browseEntries[2]
            e.delete(0,"end")
            e.insert(0,fileName)
    #@+node:ekr.20081121110412.25: *5* onClose
    def onClose (self):

        self.top.withdraw()
    #@+node:ekr.20081121110412.26: *5* onCompare...
    def onCompareDirectories (self):

        self.setIvarsFromWidgets()
        self.compare_directories(self.fileName1,self.fileName2)

    def onCompareFiles (self):

        self.setIvarsFromWidgets()
        self.compare_files(self.fileName1,self.fileName2)
    #@+node:ekr.20081121110412.27: *5* onPrintMatchedLines
    def onPrintMatchedLines (self):

        v = self.printMatchesVar.get()
        b = self.printButtons[1]
        state = g.choose(v,"normal","disabled")
        b.configure(state=state)
    #@-others
#@+node:ekr.20081121110412.38: *3* class tkinterAboutLeo
class tkinterAboutLeo (leoTkinterDialog):

    """A class that creates the Tkinter About Leo dialog."""

    #@+others
    #@+node:ekr.20081121110412.39: *4* tkinterAboutLeo.__init__
    def __init__ (self,c,version,theCopyright,url,email):

        """Create a Tkinter About Leo dialog."""

        leoTkinterDialog.__init__(self,c,"About Leo",resizeable=True) # Initialize the base class.

        if g.app.unitTesting: return

        self.copyright = theCopyright
        self.email = email
        self.url = url
        self.version = version

        c.inCommand = False # Allow the app to close immediately.

        self.createTopFrame()
        self.createFrame()
    #@+node:ekr.20081121110412.40: *4* tkinterAboutLeo.createFrame
    def createFrame (self):

        """Create the frame for an About Leo dialog."""

        if g.app.unitTesting: return

        c = self.c

        frame = self.frame
        theCopyright = self.copyright ; email = self.email
        url = self.url ; version = self.version

        # Calculate the approximate height & width. (There are bugs in Tk here.)
        lines = theCopyright.split('\n')
        height = len(lines) + 8 # Add lines for version,url,email,spacing.
        width = 0
        for line in lines:
            width = max(width,len(line))
        width = max(width,len(url))
        width += 10 # 9/9/02

        frame.pack(padx=6,pady=4)

        self.text = w = g.app.gui.plainTextWidget(
            frame,height=height,width=width,bd=0,bg=frame.cget("background"))
        w.pack(pady=10)

        try:
            bitmap_name = g.os_path_join(g.app.loadDir,"..","Icons","Leoapp.GIF") # 5/12/03
            image = Tk.PhotoImage(file=bitmap_name)
            w.image_create("1.0",image=image,padx=10)
        except Exception:
            pass # This can sometimes happen for mysterious reasons.

        w.insert("end",version) #,tag="version")
        w.tag_add('version','end-%dc' %(len(version)+1),'end-1c')
        w.insert("end",theCopyright) #,tag="copyright")
        w.tag_add('copyright','end-%dc' %(len(theCopyright)+1),'end-1c')
        w.insert("end",'\n')
        w.insert("end",url)
        w.tag_add('url','end-%dc' %(len(url)+1),'end-1c')
        w.insert("end",'\n')
        w.insert("end",email)
        w.tag_add('url','end-%dc' %(len(email)+1),'end-1c')

        w.tag_config("version",justify="center")
        w.tag_config("copyright",justify="center",spacing1="3")
        w.tag_config("url",underline=1,justify="center",spacing1="10")

        c.tag_bind(w,"url","<Button-1>",self.onAboutLeoUrl)
        c.tag_bind(w,"url","<Enter>",self.setArrowCursor)
        c.tag_bind(w,"url","<Leave>",self.setDefaultCursor)

        w.tag_config("email",underline=1,justify="center",spacing1="10")
        c.tag_bind(w,"email","<Button-1>",self.onAboutLeoEmail)
        c.tag_bind(w,"email","<Enter>",self.setArrowCursor)
        c.tag_bind(w,"email","<Leave>",self.setDefaultCursor)

        w.configure(state="disabled")
    #@+node:ekr.20081121110412.41: *4* tkinterAboutLeo.onAboutLeoEmail
    def onAboutLeoEmail(self,event=None):

        """Handle clicks in the email link in an About Leo dialog."""

        try:
            import webbrowser
            webbrowser.open("mailto:" + self.email)
        except:
            g.es("not found:",self.email)
    #@+node:ekr.20081121110412.42: *4* tkinterAboutLeo.onAboutLeoUrl
    def onAboutLeoUrl(self,event=None):

        """Handle clicks in the url link in an About Leo dialog."""

        try:
            import webbrowser
            webbrowser.open(self.url)
        except:
            g.es("not found:",self.url)
    #@+node:ekr.20081121110412.43: *4* tkinterAboutLeo: setArrowCursor, setDefaultCursor
    def setArrowCursor (self,event=None):

        """Set the cursor to an arrow in an About Leo dialog."""

        self.text.configure(cursor="arrow")

    def setDefaultCursor (self,event=None):

        """Set the cursor to the default cursor in an About Leo dialog."""

        self.text.configure(cursor="xterm")
    #@-others
#@+node:ekr.20081121110412.44: *3* class tkinterAskLeoID
class tkinterAskLeoID (leoTkinterDialog):

    """A class that creates the Tkinter About Leo dialog."""

    #@+others
    #@+node:ekr.20081121110412.45: *4* tkinterAskLeoID.__init__
    def __init__(self,c=None):

        """Create the Leo Id dialog."""

        # Initialize the base class: prevent clicks in the close box from closing.
        leoTkinterDialog.__init__(self,c,"Enter unique id",resizeable=False,canClose=False)

        if g.app.unitTesting: return

        self.id_entry = None
        self.answer = None

        self.createTopFrame()
        if c:
            c.bind(self.top,"<Key>", self.onKey)
        else:
            # g.trace('can not use c.bind')
            self.top.bind("<Key>", self.onKey)

        message = (
            "leoID.txt not found\n\n" +
            "Please enter an id that identifies you uniquely.\n" +
            "Your cvs login name is a good choice.\n\n" +
            "Leo uses this id to uniquely identify nodes.\n\n" +
            "Your id must contain only letters and numbers\n" +
            "and must be at least 3 characters in length.")
        self.createFrame(message)
        self.focus_widget = self.id_entry

        buttons = {"text":"OK","command":self.onButton,"default":True}, # Singleton tuple.
        buttonList = self.createButtons(buttons)
        self.ok_button = buttonList[0]
        self.ok_button.configure(state="disabled")
    #@+node:ekr.20081121110412.46: *4* tkinterAskLeoID.createFrame
    def createFrame(self,message):

        """Create the frame for the Leo Id dialog."""

        if g.app.unitTesting: return

        f = self.frame

        label = Tk.Label(f,text=message)
        label.pack(pady=10)

        self.id_entry = text = Tk.Entry(f,width=20)
        text.pack()
    #@+node:ekr.20081121110412.47: *4* tkinterAskLeoID.onButton
    def onButton(self):

        """Handle clicks in the Leo Id close button."""

        s = self.id_entry.get().strip()
        if len(s) < 3:  # Require at least 3 characters in an id.
            return

        self.answer = g.app.leoID = s

        self.top.destroy() # terminates wait_window
        self.top = None
    #@+node:ekr.20081121110412.48: *4* tkinterAskLeoID.onKey
    def onKey(self,event):

        """Handle keystrokes in the Leo Id dialog."""

        #@+<< eliminate invalid characters >>
        #@+node:ekr.20081121110412.49: *5* << eliminate invalid characters >>
        e = self.id_entry
        s = e.get().strip()
        i = 0 ; ok = True
        while i < len(s):
            ch = s[i]
            if not ch.isalnum():
                e.delete(str(i))
                s = e.get()
                ok = False
            else:
                i += 1
        if not ok: return
        #@-<< eliminate invalid characters >>
        #@+<< enable the ok button if there are 3 or more valid characters >>
        #@+node:ekr.20081121110412.50: *5* << enable the ok button if there are 3 or more valid characters >>
        e = self.id_entry
        b = self.ok_button

        if len(e.get().strip()) >= 3:
            b.configure(state="normal")
        else:
            b.configure(state="disabled")
        #@-<< enable the ok button if there are 3 or more valid characters >>

        ch = event.char.lower()
        if ch in ('\n','\r'):
            self.onButton()
        return "break"
    #@-others
#@+node:ekr.20081121110412.51: *3* class tkinterAskOk
class tkinterAskOk(leoTkinterDialog):

    """A class that creates a Tkinter dialog with a single OK button."""

    #@+others
    #@+node:ekr.20081121110412.52: *4* class tkinterAskOk.__init__
    def __init__ (self,c,title,message=None,text="Ok",resizeable=False):

        """Create a dialog with one button"""

        leoTkinterDialog.__init__(self,c,title,resizeable) # Initialize the base class.

        if g.app.unitTesting: return

        self.text = text
        self.createTopFrame()

        c.bind(self.top,"<Key>", self.onKey)

        if message:
            self.createMessageFrame(message)

        buttons = {"text":text,"command":self.okButton,"default":True}, # Singleton tuple.
        self.createButtons(buttons)
    #@+node:ekr.20081121110412.53: *4* class tkinterAskOk.onKey
    def onKey(self,event):

        """Handle Key events in askOk dialogs."""

        ch = event.char.lower()

        if ch in (self.text[0].lower(),'\n','\r'):
            self.okButton()

        return "break"
    #@-others
#@+node:ekr.20081121110412.54: *3* class tkinterAskOkCancelNumber
class  tkinterAskOkCancelNumber (leoTkinterDialog):

    """Create and run a modal Tkinter dialog to get a number."""

    #@+others
    #@+node:ekr.20081121110412.55: *4* tkinterAskOKCancelNumber.__init__
    def __init__ (self,c,title,message):

        """Create a number dialog"""

        leoTkinterDialog.__init__(self,c,title,resizeable=False) # Initialize the base class.

        if g.app.unitTesting: return

        self.answer = -1
        self.number_entry = None

        self.createTopFrame()
        c.bind(self.top,"<Key>", self.onKey)

        self.createFrame(message)
        self.focus_widget = self.number_entry

        buttons = (
                {"text":"Ok",    "command":self.okButton,     "default":True},
                {"text":"Cancel","command":self.cancelButton} )
        buttonList = self.createButtons(buttons)
        self.ok_button = buttonList[0] # Override the default kind of Ok button.
    #@+node:ekr.20081121110412.56: *4* tkinterAskOKCancelNumber.createFrame
    def createFrame (self,message):

        """Create the frame for a number dialog."""

        if g.app.unitTesting: return

        c = self.c

        lab = Tk.Label(self.frame,text=message)
        lab.pack(pady=10,side="left")

        self.number_entry = w = Tk.Entry(self.frame,width=20)
        w.pack(side="left")

        c.set_focus(w)
    #@+node:ekr.20081121110412.57: *4* tkinterAskOKCancelNumber.okButton, cancelButton
    def okButton(self):

        """Handle clicks in the ok button of a number dialog."""

        s = self.number_entry.get().strip()

        try:
            self.answer=int(s)
        except:
            self.answer=-1 # Cancel the operation.

        self.top.destroy()

    def cancelButton(self):

        """Handle clicks in the cancel button of a number dialog."""

        self.answer=-1
        self.top.destroy()
    #@+node:ekr.20081121110412.58: *4* tkinterAskOKCancelNumber.onKey
    def onKey (self,event):

        #@+<< eliminate non-numbers >>
        #@+node:ekr.20081121110412.59: *5* << eliminate non-numbers >>
        e = self.number_entry
        s = e.get().strip()

        i = 0
        while i < len(s):
            ch = s[i]
            if not ch.isdigit():
                e.delete(str(i))
                s = e.get()
            else:
                i += 1
        #@-<< eliminate non-numbers >>

        ch = event.char.lower()

        if ch in ('o','\n','\r'):
            self.okButton()
        elif ch == 'c':
            self.cancelButton()

        return "break"
    #@-others
#@+node:ekr.20081121110412.60: *3* class tkinterAskOkCancelString
class  tkinterAskOkCancelString (leoTkinterDialog):

    """Create and run a modal Tkinter dialog to get a string."""

    #@+others
    #@+node:ekr.20081121110412.61: *4* tkinterAskOKCancelString.__init__
    def __init__ (self,c,title,message):

        """Create a number dialog"""

        leoTkinterDialog.__init__(self,c,title,resizeable=False) # Initialize the base class.

        if g.app.unitTesting: return

        self.answer = -1
        self.number_entry = None

        self.createTopFrame()
        c.bind(self.top,"<Key>", self.onKey)

        self.createFrame(message)
        self.focus_widget = self.number_entry

        buttons = (
                {"text":"Ok",    "command":self.okButton,     "default":True},
                {"text":"Cancel","command":self.cancelButton} )
        buttonList = self.createButtons(buttons)
        self.ok_button = buttonList[0] # Override the default kind of Ok button.
    #@+node:ekr.20081121110412.62: *4* tkinterAskOkCancelString.createFrame
    def createFrame (self,message):

        """Create the frame for a number dialog."""

        if g.app.unitTesting: return

        c = self.c

        lab = Tk.Label(self.frame,text=message)
        lab.pack(pady=10,side="left")

        self.number_entry = w = Tk.Entry(self.frame,width=20)
        w.pack(side="left")

        c.set_focus(w)
    #@+node:ekr.20081121110412.63: *4* tkinterAskOkCancelString.okButton, cancelButton
    def okButton(self):

        """Handle clicks in the ok button of a string dialog."""

        self.answer = self.number_entry.get().strip()
        self.top.destroy()

    def cancelButton(self):

        """Handle clicks in the cancel button of a string dialog."""

        self.answer=''
        self.top.destroy()
    #@+node:ekr.20081121110412.64: *4* tkinterAskOkCancelString.onKey
    def onKey (self,event):

        ch = event.char.lower()

        if ch in ('\n','\r'):
            self.okButton()

        return "break"
    #@-others
#@+node:ekr.20081121110412.65: *3* class tkinterAskYesNo
class tkinterAskYesNo (leoTkinterDialog):

    """A class that creates a Tkinter dialog with two buttons: Yes and No."""

    #@+others
    #@+node:ekr.20081121110412.66: *4* tkinterAskYesNo.__init__
    def __init__ (self,c,title,message=None,resizeable=False):

        """Create a dialog having yes and no buttons."""

        leoTkinterDialog.__init__(self,c,title,resizeable) # Initialize the base class.

        if g.app.unitTesting: return

        self.createTopFrame()
        c.bind(self.top,"<Key>",self.onKey)

        if message:
            self.createMessageFrame(message)

        buttons = (
            {"text":"Yes","command":self.yesButton,  "default":True},
            {"text":"No", "command":self.noButton} )
        self.createButtons(buttons)
    #@+node:ekr.20081121110412.67: *4* tkinterAskYesNo.onKey
    def onKey(self,event):

        """Handle keystroke events in dialogs having yes and no buttons."""

        ch = event.char.lower()

        if ch in ('y','\n','\r'):
            self.yesButton()
        elif ch == 'n':
            self.noButton()

        return "break"
    #@-others
#@+node:ekr.20081121110412.68: *3* class tkinterAskYesNoCancel
class tkinterAskYesNoCancel(leoTkinterDialog):

    """A class to create and run Tkinter dialogs having three buttons.

    By default, these buttons are labeled Yes, No and Cancel."""

    #@+others
    #@+node:ekr.20081121110412.69: *4* askYesNoCancel.__init__
    def __init__ (self,c,title,
        message=None,
        yesMessage="Yes",
        noMessage="No",
        defaultButton="Yes",
        resizeable=False):

        """Create a dialog having three buttons."""

        leoTkinterDialog.__init__(self,c,title,resizeable,canClose=False) # Initialize the base class.

        if g.app.unitTesting: return

        self.yesMessage,self.noMessage = yesMessage,noMessage
        self.defaultButton = defaultButton

        self.createTopFrame()
        c.bind(self.top,"<Key>",self.onKey)

        if message:
            self.createMessageFrame(message)

        buttons = (
            {"text":yesMessage,"command":self.yesButton,   "default":yesMessage==defaultButton},
            {"text":noMessage, "command":self.noButton,    "default":noMessage==defaultButton},
            {"text":"Cancel",  "command":self.cancelButton,"default":"Cancel"==defaultButton} )
        self.createButtons(buttons)
    #@+node:ekr.20081121110412.70: *4* askYesNoCancel.onKey
    def onKey(self,event):

        """Handle keystrokes in dialogs with three buttons."""

        ch = event.char.lower()

        if ch in ('\n','\r'):
            ch = self.defaultButton[0].lower()

        if ch == self.yesMessage[0].lower():
            self.yesButton()
        elif ch == self.noMessage[0].lower():
            self.noButton()
        elif ch == 'c':
            self.cancelButton()

        return "break"
    #@+node:ekr.20081121110412.71: *4* askYesNoCancel.noButton & yesButton
    def noButton(self):

        """Handle clicks in the 'no' (second) button in a dialog with three buttons."""

        self.answer=self.noMessage.lower()
        self.top.destroy()

    def yesButton(self):

        """Handle clicks in the 'yes' (first) button in a dialog with three buttons."""

        self.answer=self.yesMessage.lower()
        self.top.destroy()
    #@-others
#@+node:ekr.20081121110412.72: *3* class tkinterListboxDialog
class tkinterListBoxDialog (leoTkinterDialog):

    """A base class for Tkinter dialogs containing a Tk Listbox"""

    #@+others
    #@+node:ekr.20081121110412.73: *4* tkinterListboxDialog.__init__
    def __init__ (self,c,title,label):

        """Constructor for the base listboxDialog class."""

        leoTkinterDialog.__init__(self,c,title,resizeable=True) # Initialize the base class.

        if g.app.unitTesting: return

        self.createTopFrame()
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)

        # Initialize common ivars.
        self.label = label
        self.positionList = []
        self.buttonFrame = None

        # Fill in the frame.
        self.createFrame()
        self.fillbox()

        # Make the common bindings after creating self.box.
        c.bind(self.box,"<Double-Button-1>",self.go)
    #@+node:ekr.20081121110412.74: *4* addStdButtons
    def addStdButtons (self,frame):

        """Add standard buttons to a listBox dialog."""

        # Create the ok and cancel buttons.
        self.ok = ok = Tk.Button(frame,text="Go",width=6,command=self.go)
        self.hideButton = hide = Tk.Button(frame,text="Hide",width=6,command=self.hide)

        ok.pack(side="left",pady=2,padx=5)
        hide.pack(side="left",pady=2,padx=5)
    #@+node:ekr.20081121110412.75: *4* createFrame
    def createFrame(self):

        """Create the essentials of a listBoxDialog frame

        Subclasses will add buttons to self.buttonFrame"""

        if g.app.unitTesting: return

        self.outerFrame = f = Tk.Frame(self.frame)
        f.pack(expand=1,fill="both")

        if self.label:
            labf = Tk.Frame(f)
            labf.pack(pady=2)
            lab = Tk.Label(labf,text=self.label)
            lab.pack()

        f2 = Tk.Frame(f)
        f2.pack(expand=1,fill="both")

        self.box = box = Tk.Listbox(f2,height=20,width=30)
        box.pack(side="left",expand=1,fill="both")

        bar = Tk.Scrollbar(f2)
        bar.pack(side="left", fill="y")

        bar.config(command=box.yview)
        box.config(yscrollcommand=bar.set)
    #@+node:ekr.20081121110412.76: *4* destroy
    def destroy (self,event=None):

        """Hide, do not destroy, a listboxDialog window

        subclasses may override to really destroy the window"""

        self.top.withdraw() # Don't allow this window to be destroyed.
    #@+node:ekr.20081121110412.77: *4* hide
    def hide (self):

        """Hide a list box dialog."""

        self.top.withdraw()
    #@+node:ekr.20081121110412.78: *4* fillbox
    def fillbox(self,event=None):

        """Fill a listbox from information.

        Overridden by subclasses"""

        pass
    #@+node:ekr.20081121110412.79: *4* go
    def go(self,event=None):

        """Handle clicks in the "go" button in a list box dialog."""

        c = self.c ; box = self.box

        # Work around an old Python bug.  Convert strings to ints.
        items = box.curselection()
        try:
            items = map(int, items)
        except ValueError: pass

        if items:
            n = items[0]
            p = self.positionList[n]
            c.expandAllAncestors(p)
            c.selectPosition(p)
            c.redraw()
    #@-others
#@+node:ekr.20081121110412.80: ** find/spell classes
#@+node:ekr.20081121110412.81: *3* class underlinedTkButton
class underlinedTkButton:

    #@+others
    #@+node:ekr.20081121110412.82: *4* __init__
    def __init__(self,buttonType,parent_widget,**keywords):

        self.buttonType = buttonType
        self.parent_widget = parent_widget
        self.hotKey = None
        text = keywords['text']

        #@+<< set self.hotKey if '&' is in the string >>
        #@+node:ekr.20081121110412.83: *5* << set self.hotKey if '&' is in the string >>
        index = text.find('&')

        if index > -1:

            if index == len(text)-1:
                # The word ends in an ampersand.  Ignore it; there is no hot key.
                text = text[:-1]
            else:
                self.hotKey = text [index + 1]
                text = text[:index] + text[index+1:]
        #@-<< set self.hotKey if '&' is in the string >>

        # Create the button...
        if self.hotKey:
            keywords['text'] = text
            keywords['underline'] = index

        if buttonType.lower() == "button":
            self.button = Tk.Button(parent_widget,keywords)
        elif buttonType.lower() == "check":
            self.button = Tk.Checkbutton(parent_widget,keywords)
        elif buttonType.lower() == "radio":
            self.button = Tk.Radiobutton(parent_widget,keywords)
        else:
            g.trace("bad buttonType")

        self.text = text # for traces
    #@+node:ekr.20081121110412.84: *4* bindHotKey
    def bindHotKey (self,widget):

        if self.hotKey:
            for key in (self.hotKey.lower(),self.hotKey.upper()):
                widget.bind("<Alt-%s>" % key,self.buttonCallback)
    #@+node:ekr.20081121110412.85: *4* buttonCallback
    # The hot key has been hit.  Call the button's command.

    def buttonCallback (self, event=None):

        # g.trace(self.text)
        self.button.invoke ()

        # See if this helps.
        return 'break'
    #@-others
#@+node:ekr.20081121110412.86: *3* class tkFindTab (findTab)
class tkFindTab (leoFind.findTab):

    '''A subclass of the findTab class containing all Tk code.'''

    #@+others
    #@+node:ekr.20081121110412.87: *4*  Birth
    #@+node:ekr.20081121110412.88: *5*  ctor (tkFindTab)
    if 0: # Use the base class ctor.

        def __init__ (self,c,parentFrame):

            leoFind.findTab.__init__(self,c,parentFrame)
                # Init the base class.
                # Calls initGui, createFrame, createBindings & init(c), in that order.

    #@+node:ekr.20081121110412.89: *5* initGui
    def initGui (self):

        self.svarDict = {}

        for key in self.intKeys:
            self.svarDict[key] = Tk.IntVar()

        for key in self.newStringKeys:
            self.svarDict[key] = Tk.StringVar()

    #@+node:ekr.20081121110412.90: *5* createFrame (tkFindTab)
    def createFrame (self,parentFrame):

        c = self.c

        # g.trace('findTab')

        #@+<< Create the outer frames >>
        #@+node:ekr.20081121110412.91: *6* << Create the outer frames >>
        configName = 'log_pane_Find_tab_background_color'
        bg = c.config.getColor(configName) or 'MistyRose1'

        parentFrame.configure(background=bg)

        self.top = Tk.Frame(parentFrame,background=bg)
        self.top.pack(side='top',expand=0,fill='both',pady=5)
            # Don't expand, so the frame goes to the top.

        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(relief='flat',background=bg)
        #@-<< Create the outer frames >>
        #@+<< Create the Find and Change panes >>
        #@+node:ekr.20081121110412.92: *6* << Create the Find and Change panes >>
        fc = Tk.Frame(outer, bd="1m",background=bg)
        fc.pack(anchor="n", fill="x", expand=1)

        # Removed unused height/width params: using fractions causes problems in some locales!
        fpane = Tk.Frame(fc, bd=1,background=bg)
        cpane = Tk.Frame(fc, bd=1,background=bg)

        fpane.pack(anchor="n", expand=1, fill="x")
        cpane.pack(anchor="s", expand=1, fill="x")

        # Create the labels and text fields...
        flab = Tk.Label(fpane, width=8, text="Find:",background=bg)
        clab = Tk.Label(cpane, width=8, text="Change:",background=bg)

        if self.optionsOnly:
            # Use one-line boxes.
            self.find_ctrl = ftxt = g.app.gui.plainTextWidget(
                fpane,bd=1,relief="groove",height=1,width=25,name='find-text')
            self.change_ctrl = ctxt = g.app.gui.plainTextWidget(
                cpane,bd=1,relief="groove",height=1,width=25,name='change-text')
        else:
            # Use bigger boxes for scripts.
            self.find_ctrl = ftxt = g.app.gui.plainTextWidget(
                fpane,bd=1,relief="groove",height=3,width=15,name='find-text')
            self.change_ctrl = ctxt = g.app.gui.plainTextWidget(
                cpane,bd=1,relief="groove",height=3,width=15,name='change-text')
        #@+<< Bind Tab and control-tab >>
        #@+node:ekr.20081121110412.93: *7* << Bind Tab and control-tab >>
        def setFocus(w):
            c = self.c
            c.widgetWantsFocusNow(w)
            w.setSelectionRange(0,0)
            return "break"

        def toFind(event,w=ftxt): return setFocus(w)
        def toChange(event,w=ctxt): return setFocus(w)

        def insertTab(w):
            data = w.getSelectionRange()
            if data: start,end = data
            else: start = end = w.getInsertPoint()
            w.replace(start,end,"\t")
            return "break"

        def insertFindTab(event,w=ftxt): return insertTab(w)
        def insertChangeTab(event,w=ctxt): return insertTab(w)

        c.bind(ftxt,"<Tab>",toChange)
        c.bind(ctxt,"<Tab>",toFind)
        c.bind(ftxt,"<Control-Tab>",insertFindTab)
        c.bind(ctxt,"<Control-Tab>",insertChangeTab)
        #@-<< Bind Tab and control-tab >>

        if 0: # Add scrollbars.
            fBar = Tk.Scrollbar(fpane,name='findBar')
            cBar = Tk.Scrollbar(cpane,name='changeBar')

            for bar,txt in ((fBar,ftxt),(cBar,ctxt)):
                txt['yscrollcommand'] = bar.set
                bar['command'] = txt.yview
                bar.pack(side="right", fill="y")

        if self.optionsOnly:
            flab.pack(side="left") ; ftxt.pack(side="left")
            clab.pack(side="left") ; ctxt.pack(side="left")
        else:
            flab.pack(side="left") ; ftxt.pack(side="right", expand=1, fill="x")
            clab.pack(side="left") ; ctxt.pack(side="right", expand=1, fill="x")
        #@-<< Create the Find and Change panes >>
        #@+<< Create two columns of radio and checkboxes >>
        #@+node:ekr.20081121110412.94: *6* << Create two columns of radio and checkboxes >>
        columnsFrame = Tk.Frame(outer,relief="groove",bd=2,background=bg)

        columnsFrame.pack(expand=0,padx="7p",pady="2p")

        numberOfColumns = 2 # Number of columns
        columns = [] ; radioLists = [] ; checkLists = []
        for i in range(numberOfColumns):
            columns.append(Tk.Frame(columnsFrame,bd=1))
            radioLists.append([])
            checkLists.append([])

        for i in range(numberOfColumns):
            columns[i].pack(side="left",padx="1p") # fill="y" Aligns to top. padx expands columns.

        radioLists[0] = []

        checkLists[0] = [
            # ("Scrip&t Change",self.svarDict["script_change"]),
            ("Whole &Word", self.svarDict["whole_word"]),
            ("&Ignore Case",self.svarDict["ignore_case"]),
            ("Wrap &Around",self.svarDict["wrap"]),
            ("&Reverse",    self.svarDict["reverse"]),
            ('Rege&xp',     self.svarDict['pattern_match']),
            ("Mark &Finds", self.svarDict["mark_finds"]),
        ]

        radioLists[1] = [
            (self.svarDict["radio-search-scope"],"&Entire Outline","entire-outline"),
            (self.svarDict["radio-search-scope"],"&Suboutline Only","suboutline-only"),  
            (self.svarDict["radio-search-scope"],"&Node Only","node-only"),
        ]

        checkLists[1] = [
            ("Search &Headline", self.svarDict["search_headline"]),
            ("Search &Body",     self.svarDict["search_body"]),
            ("Mark &Changes",    self.svarDict["mark_changes"]),
        ]

        for i in range(numberOfColumns):
            for var,name,val in radioLists[i]:
                box = underlinedTkButton(
                    "radio",columns[i],anchor="w",text=name,variable=var,value=val,background=bg)
                box.button.pack(fill="x")
                c.bind(box.button,"<Button-1>", self.resetWrap)
                if val == None: box.button.configure(state="disabled")
                box.bindHotKey(ftxt)
                box.bindHotKey(ctxt)
            for name,var in checkLists[i]:
                box = underlinedTkButton(
                    "check",columns[i],anchor="w",text=name,variable=var,background=bg)
                box.button.pack(fill="x")
                c.bind(box.button,"<Button-1>", self.resetWrap)
                box.bindHotKey(ftxt)
                box.bindHotKey(ctxt)
                if var is None: box.button.configure(state="disabled")
        #@-<< Create two columns of radio and checkboxes >>

        if  self.optionsOnly:
            buttons = []
        else:
            #@+<< Create two columns of buttons >>
            #@+node:ekr.20081121110412.95: *6* << Create two columns of buttons >>
            # Create the alignment panes.
            buttons  = Tk.Frame(outer,background=bg)
            buttons1 = Tk.Frame(buttons,bd=1,background=bg)
            buttons2 = Tk.Frame(buttons,bd=1,background=bg)
            buttons.pack(side='top',expand=1)
            buttons1.pack(side='left')
            buttons2.pack(side='right')

            width = 15 ; defaultText = 'Find' ; buttons = []

            for text,boxKind,frame,callback in (
                # Column 1...
                ('Find','button',buttons1,self.findButtonCallback),
                ('Find All','button',buttons1,self.findAllButton),
                # Column 2...
                ('Change','button',buttons2,self.changeButton),
                ('Change, Then Find','button',buttons2,self.changeThenFindButton),
                ('Change All','button',buttons2,self.changeAllButton),
            ):
                w = underlinedTkButton(boxKind,frame,
                    text=text,command=callback)
                buttons.append(w)
                if text == defaultText:
                    w.button.configure(width=width-1,bd=4)
                elif boxKind != 'check':
                    w.button.configure(width=width)
                w.button.pack(side='top',anchor='w',pady=2,padx=2)
            #@-<< Create two columns of buttons >>

        # Pack this last so buttons don't get squashed when frame is resized.
        self.outerScrolledFrame.pack(side='top',expand=1,fill='both',padx=2,pady=2)
    #@+node:ekr.20081121110412.96: *5* createBindings (tkFindTab)
    def createBindings (self):

        c = self.c ; k = c.k

        def resetWrapCallback(event,self=self,k=k):
            self.resetWrap(event)
            return k.masterKeyHandler(event)

        def findButtonBindingCallback(event=None,self=self):
            self.findButton()
            c.outerUpdate()
            return 'break'

        def rightClickCallback(event=None):
            val = k.masterClick3Handler(event, self.onRightClick)
            c.outerUpdate()
            return val

        table = [
            ('<Button-1>',  k.masterClickHandler),
            ('<Double-1>',  k.masterClickHandler),
            ('<Button-3>',  rightClickCallback),
            ('<Double-3>',  k.masterClickHandler),
            ('<Key>',       resetWrapCallback),
            ('<Return>',    findButtonBindingCallback),
            ("<Escape>",    self.hideTab),
        ]

        for w in (self.find_ctrl,self.change_ctrl):
            for event, callback in table:
                c.bind(w,event,callback)
    #@+node:ekr.20081121110412.97: *5* onRightClick
    def onRightClick(self, event):

        context_menu = self.c.widget_name(event.widget)
        return g.doHook('rclick-popup', c=self.c, event=event, context_menu=context_menu)
    #@+node:ekr.20081121110412.98: *5* tkFindTab.init
    def init (self,c):

        # g.trace('tkFindTab',g.callers())

        # N.B.: separate c.ivars are much more convenient than a dict.
        for key in self.intKeys:
            # New in 4.3: get ivars from @settings.
            val = c.config.getBool(key)
            setattr(self,key,val)
            val = g.choose(val,1,0) # Work around major Tk problem.
            self.svarDict[key].set(val)
            # g.trace(key,val)

        #@+<< set find/change widgets >>
        #@+node:ekr.20081121110412.99: *6* << set find/change widgets >>
        self.find_ctrl.delete(0,"end")
        self.change_ctrl.delete(0,"end")

        # New in 4.3: Get setting from @settings.
        for w,setting,defaultText in (
            (self.find_ctrl,"find_text",'<find pattern here>'),
            (self.change_ctrl,"change_text",''),
        ):
            s = c.config.getString(setting)
            if not s: s = defaultText
            w.insert("end",s)
        #@-<< set find/change widgets >>
        #@+<< set radio buttons from ivars >>
        #@+node:ekr.20081121110412.100: *6* << set radio buttons from ivars >>
        found = False
        for var,setting in (
            ("pattern_match","pattern-search"),
            ("script_search","script-search")):
            val = self.svarDict[var].get()
            if val:
                self.svarDict["radio-find-type"].set(setting)
                found = True ; break
        if not found:
            self.svarDict["radio-find-type"].set("plain-search")

        found = False
        for var,setting in (
            ("suboutline_only","suboutline-only"),
            ("node_only","node-only"),
            # ("selection_only","selection-only"),
        ):
            val = self.svarDict[var].get()
            if val:
                self.svarDict["radio-search-scope"].set(setting)
                found = True ; break
        if not found:
            self.svarDict["radio-search-scope"].set("entire-outline")
        #@-<< set radio buttons from ivars >>
    #@+node:ekr.20081121110412.101: *4* Support for minibufferFind class (tkFindTab)
    #@+node:ekr.20081121110412.102: *5* getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('%s = %s' % (ivar,val))
            return val
        else:
            g.trace('bad ivar name: %s' % ivar)
            return None
    #@+node:ekr.20081121110412.103: *5* setOption
    def setOption (self,ivar,val):

        if ivar in self.intKeys:
            if val is not None:
                var = self.svarDict.get(ivar)
                var.set(val)
                # g.trace('%s = %s' % (ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@+node:ekr.20081121110412.104: *5* toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-others
#@+node:ekr.20081121110412.105: *3* class tkSpellTab
class tkSpellTab:

    #@+others
    #@+node:ekr.20081121110412.106: *4* tkSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        self.c = c
        self.handler = handler
        self.tabName = tabName
        self.change_i, change_j = None,None
        self.createFrame()
        self.createBindings()
        self.fillbox([])
        self.positionList = []
    #@+node:ekr.20081121110412.107: *4* createBindings
    def createBindings (self):

        c = self.c ; k = c.k
        widgets = (self.listBox, self.outerFrame)

        for w in widgets:

            # Bind shortcuts for the following commands...
            for commandName,func in (
                ('full-command',            k.fullCommand),
                ('hide-spell-tab',          self.handler.hide),
                ('spell-add',               self.handler.add),
                ('spell-find',              self.handler.find),
                ('spell-ignore',            self.handler.ignore),
                ('spell-change-then-find',  self.handler.changeThenFind),
            ):
                junk, bunchList = c.config.getShortcut(commandName)
                for bunch in bunchList:
                    accel = bunch.val
                    shortcut = k.shortcutFromSetting(accel)
                    if shortcut:
                        # g.trace(shortcut,commandName)
                        c.bind(w,shortcut,func)

        for binding,func in (
            ("<Double-1>",  self.onChangeThenFindButton),
            ("<Button-1>",  self.onSelectListBox),
            ("<Map>",       self.onMap),
            # These never get called because focus is always in the body pane!
            # ("<Up>",        self.up),
            # ("<Down>",      self.down),
        ):
            c.bind(self.listBox,binding,func)
    #@+node:ekr.20081121110412.108: *4* createFrame
    def createFrame (self):

        c = self.c ; log = c.frame.log ; tabName = self.tabName
        setFont = False

        parentFrame = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        # Set the common background color.
        bg = c.config.getColor('log_pane_Spell_tab_background_color') or 'LightSteelBlue2'

        if setFont:
            fontSize = g.choose(sys.platform.startswith('win'),9,14)

        #@+<< Create the outer frames >>
        #@+node:ekr.20081121110412.109: *5* << Create the outer frames >>
        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(
                relief='flat',background=bg)
        #@-<< Create the outer frames >>
        #@+<< Create the text and suggestion panes >>
        #@+node:ekr.20081121110412.110: *5* << Create the text and suggestion panes >>
        f2 = Tk.Frame(outer,bg=bg)
        f2.pack(side='top',expand=0,fill='x')

        self.wordLabel = Tk.Label(f2,text="Suggestions for:")
        self.wordLabel.pack(side='left')

        if setFont:
            self.wordLabel.configure(font=('verdana',fontSize,'bold'))

        fpane = Tk.Frame(outer,bg=bg,bd=2)
        fpane.pack(side='top',expand=1,fill='both')

        self.listBox = Tk.Listbox(fpane,height=6,width=10,selectmode="single")
        self.listBox.pack(side='left',expand=1,fill='both')
        if setFont:
            self.listBox.configure(font=('verdana',fontSize,'normal'))

        listBoxBar = Tk.Scrollbar(fpane,name='listBoxBar')

        bar, txt = listBoxBar, self.listBox
        txt ['yscrollcommand'] = bar.set
        bar ['command'] = txt.yview
        bar.pack(side='right',fill='y')
        #@-<< Create the text and suggestion panes >>
        #@+<< Create the spelling buttons >>
        #@+node:ekr.20081121110412.111: *5* << Create the spelling buttons >>
        # Create the alignment panes
        buttons1 = Tk.Frame(outer,bd=1,bg=bg)
        buttons2 = Tk.Frame(outer,bd=1,bg=bg)
        buttons3 = Tk.Frame(outer,bd=1,bg=bg)
        for w in (buttons1,buttons2,buttons3):
            w.pack(side='top',expand=0,fill='x')

        buttonList = []
        if setFont:
            font = ('verdana',fontSize,'normal')
        width = 12
        for frame, text, command in (
            (buttons1,"Find",self.onFindButton),
            (buttons1,"Add",self.onAddButton),
            (buttons2,"Change",self.onChangeButton),
            (buttons2,"Change, Find",self.onChangeThenFindButton),
            (buttons3,"Ignore",self.onIgnoreButton),
            (buttons3,"Hide",self.onHideButton),
        ):
            if setFont:
                b = Tk.Button(frame,font=font,width=width,text=text,command=command)
            else:
                b = Tk.Button(frame,width=width,text=text,command=command)
            b.pack(side='left',expand=0,fill='none')
            buttonList.append(b)

        # Used to enable or disable buttons.
        (self.findButton,self.addButton,
         self.changeButton, self.changeFindButton,
         self.ignoreButton, self.hideButton) = buttonList
        #@-<< Create the spelling buttons >>

        # Pack last so buttons don't get squished.
        self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
    #@+node:ekr.20081121110412.112: *4* Event handlers
    #@+node:ekr.20081121110412.113: *5* onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
        self.change_i, self.change_j = None,None
    #@+node:ekr.20081121110412.114: *5* onChangeButton & onChangeThenFindButton
    def onChangeButton(self,event=None):

        """Handle a click in the Change button in the Spell tab."""

        self.handler.change()
        self.updateButtons()
        self.change_i, self.change_j = None,None


    def onChangeThenFindButton(self,event=None):

        """Handle a click in the "Change, Find" button in the Spell tab."""

        if self.handler.change():
            self.handler.find()
        self.updateButtons()
        self.change_i, self.change_j = None,None
    #@+node:ekr.20081121110412.115: *5* onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocus()
        self.change_i, self.change_j = None,None
    #@+node:ekr.20081121110412.116: *5* onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
        self.change_i, self.change_j = None,None
    #@+node:ekr.20081121110412.117: *5* onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
        self.change_i, self.change_j = None,None
    #@+node:ekr.20081121110412.118: *5* onMap
    def onMap (self, event=None):
        """Respond to a Tk <Map> event."""

        # self.update(show= False, fill= False)
        self.updateButtons()
    #@+node:ekr.20081121110412.119: *5* onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""

        c = self.c ; w = c.frame.body.bodyCtrl

        if self.change_i is None:
            # A bad hack to get around the fact that only one selection
            # exists at any one time on Linux.
            i,j = w.getSelectionRange()
            # g.trace('setting',i,j)
            self.change_i,self.change_j = i,j

        self.updateButtons()

        return 'continue'
    #@+node:ekr.20081121110412.120: *5* down/up
    def down (self,event):

        # Work around an old Python bug.  Convert strings to ints.
        w = self.listBox ; items = w.curselection()
        try: items = map(int, items)
        except ValueError: pass

        if items:
            n = items[0]
            if n + 1 < len(self.positionList):
                w.selection_clear(n)
                w.selection_set(n+1)
        else:
            w.selection_set(0)
        w.focus_force()
        return 'break'


    def up (self,event):

        # Work around an old Python bug.  Convert strings to ints.
        w = self.listBox ; items = w.curselection()
        try: items = map(int, items)
        except ValueError: pass

        if items: n = items[0]
        else:     n = 0
        w.selection_clear(n)
        w.selection_set(max(0,n-1))
        w.focus_force()
        return 'break'
    #@+node:ekr.20081121110412.121: *4* Helpers
    #@+node:ekr.20081121110412.122: *5* bringToFront
    def bringToFront (self):

        # g.trace('tkSpellTab',g.callers())
        self.c.frame.log.selectTab('Spell')
    #@+node:ekr.20081121110412.123: *5* fillbox
    def fillbox(self, alts, word=None):
        """Update the suggestions listBox in the Check Spelling dialog."""

        self.suggestions = alts

        if not word:
            word = ""

        self.wordLabel.configure(text= "Suggestions for: " + word)
        self.listBox.delete(0, "end")

        for i in range(len(self.suggestions)):
            self.listBox.insert(i, self.suggestions[i])

        # This doesn't show up because we don't have focus.
        if len(self.suggestions):
            self.listBox.select_set(1)
    #@+node:ekr.20081121110412.124: *5* getSuggestion
    def getSuggestion(self):
        """Return the selected suggestion from the listBox."""

        # Work around an old Python bug.  Convert strings to ints.
        items = self.listBox.curselection()
        try:
            items = map(int, items)
        except ValueError: pass

        if items:
            n = items[0]
            suggestion = self.suggestions[n]
            return suggestion
        else:
            return None
    #@+node:ekr.20081121110412.125: *5* updateButtons (spellTab)
    def updateButtons (self):

        """Enable or disable buttons in the Check Spelling dialog."""

        c = self.c ; w = c.frame.body.bodyCtrl

        start, end = w.getSelectionRange()

        # Bug fix: enable buttons when start = 0.
        state = g.choose(self.suggestions and start is not None,"normal","disabled")

        self.changeButton.configure(state=state)
        self.changeFindButton.configure(state=state)

        self.addButton.configure(state='normal')
        self.ignoreButton.configure(state='normal')
    #@-others
#@+node:ekr.20081121110412.126: ** frame classes
#@+node:ekr.20081121110412.128: *3* class leoTkinterBody
class leoTkinterBody (leoFrame.leoBody):

    """A class that represents the body pane of a Tkinter window."""

    #@+others
    #@+node:ekr.20081121110412.129: *4*  Birth & death
    #@+node:ekr.20081121110412.130: *5* tkBody. __init__
    def __init__ (self,frame,parentFrame):

        # g.trace("leoTkinterBody")

        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)

        c = self.c ; p = c.currentPosition()
        self.editor_name = None
        self.editor_v = None

        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        self.bodyCtrl = self.createControl(parentFrame,p)
        self.colorizer = leoColor.colorizer(c)
    #@+node:ekr.20081121110412.131: *5* tkBody.createBindings
    def createBindings (self,w=None):

        '''(tkBody) Create gui-dependent bindings.
        These are *not* made in nullBody instances.'''

        frame = self.frame ; c = self.c ; k = c.k
        if not w: w = self.bodyCtrl

        c.bind(w,'<Key>', k.masterKeyHandler)

        def onFocusOut(event,c=c):
            # This interferes with inserting new nodes.
                # c.k.setDefaultInputState()
            self.setEditorColors(
                bg=c.k.unselected_body_bg_color,
                fg=c.k.unselected_body_fg_color)
            # This is required, for example, when typing Alt-Shift-anyArrow in insert mode.
            # But we suppress coloring in the widget.
            oldState = k.unboundKeyAction
            k.unboundKeyAction = k.defaultUnboundKeyAction
            c.k.showStateAndMode(w=g.app.gui.get_focus(c))
            k.unboundKeyAction = oldState

        def onFocusIn(event,c=c):
            # g.trace('callback')
            c.k.setDefaultInputState()
            c.k.showStateAndMode()  # TNB - fix color when window manager returns focus to Leo

        c.bind(w,'<FocusOut>', onFocusOut)
        c.bind(w,'<FocusIn>', onFocusIn)

        table = [
            ('<Button-1>',  frame.OnBodyClick,          k.masterClickHandler),
            ('<Button-3>',  frame.OnBodyRClick,         k.masterClick3Handler),
            ('<Double-1>',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
            ('<Double-3>',  None,                       k.masterDoubleClick3Handler),
            ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        ]

        table2 = (
            ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        )

        if c.config.getBool('allow_middle_button_paste'):
            table.extend(table2)

        for kind,func,handler in table:
            def bodyClickCallback(event,handler=handler,func=func):
                return handler(event,func)

            c.bind(w,kind,bodyClickCallback)
    #@+node:ekr.20081121110412.132: *5* tkBody.createControl
    def createControl (self,parentFrame,p):

        c = self.c

        # New in 4.4.1: make the parent frame a Pmw.PanedWidget.
        self.numberOfEditors = 1 ; name = '1'
        self.totalNumberOfEditors = 1

        orient = c.config.getString('editor_orientation') or 'horizontal'
        if orient not in ('horizontal','vertical'): orient = 'horizontal'

        self.pb = pb = Pmw.PanedWidget(parentFrame,orient=orient)
        parentFrame = pb.add(name)
        pb.pack(expand=1,fill='both') # Must be done after the first page created.

        w = self.createTextWidget(parentFrame,p,name)
        self.editorWidgets[name] = w

        return w
    #@+node:ekr.20081121110412.133: *5* tkBody.createTextWidget
    def createTextWidget (self,parentFrame,p,name):

        c = self.c

        parentFrame.configure(bg='LightSteelBlue1')

        wrap = c.config.getBool('body_pane_wraps')
        wrap = g.choose(wrap,"word","none")

        # Setgrid=1 cause severe problems with the font panel.
        body = w = leoTkTextWidget (parentFrame,name='body-pane',
            bd=2,bg="white",relief="flat",setgrid=0,wrap=wrap)

        bodyBar = Tk.Scrollbar(parentFrame,name='bodyBar')

        def yscrollCallback(x,y,bodyBar=bodyBar,w=w):
            # g.trace(x,y,g.callers())
            if hasattr(w,'leo_scrollBarSpot'):
                w.leo_scrollBarSpot = (x,y)
            return bodyBar.set(x,y)

        body['yscrollcommand'] = yscrollCallback # bodyBar.set

        bodyBar['command'] =  body.yview
        bodyBar.pack(side="right", fill="y")

        # Always create the horizontal bar.
        bodyXBar = Tk.Scrollbar(
            parentFrame,name='bodyXBar',orient="horizontal")
        body['xscrollcommand'] = bodyXBar.set
        bodyXBar['command'] = body.xview

        if wrap == "none":
            # g.trace(parentFrame)
            bodyXBar.pack(side="bottom", fill="x")

        body.pack(expand=1,fill="both")

        self.wrapState = wrap

        if 0: # Causes the cursor not to blink.
            body.configure(insertofftime=0)

        # Inject ivars
        if name == '1':
            w.leo_p = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()

        w.leo_active = True
        # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
        w.leo_bodyBar = bodyBar # 2007/10/31
        w.leo_bodyXBar = bodyXBar # 2007/10/31
        w.leo_chapter = None
        w.leo_frame = parentFrame
        w.leo_name = name
        w.leo_label = None
        w.leo_label_s = None
        w.leo_scrollBarSpot = None
        w.leo_insertSpot = None
        w.leo_selection = None

        return w
    #@+node:ekr.20081121110412.134: *4* tkBody.setColorFromConfig
    def setColorFromConfig (self,w=None):

        c = self.c
        if w is None: w = self.bodyCtrl

        bg = c.config.getColor("body_text_background_color") or 'white'
        # g.trace(id(w),bg)

        try: w.configure(bg=bg)
        except:
            g.es("exception setting body text background color")
            g.es_exception()

        fg = c.config.getColor("body_text_foreground_color") or 'black'
        try: w.configure(fg=fg)
        except:
            g.es("exception setting body textforeground color")
            g.es_exception()

        bg = c.config.getColor("body_insertion_cursor_color")
        if bg:
            try: w.configure(insertbackground=bg)
            except:
                g.es("exception setting body pane cursor color")
                g.es_exception()

        sel_bg = c.config.getColor('body_text_selection_background_color') or 'Gray80'
        try: w.configure(selectbackground=sel_bg)
        except Exception:
            g.es("exception setting body pane text selection background color")
            g.es_exception()

        sel_fg = c.config.getColor('body_text_selection_foreground_color') or 'white'
        try: w.configure(selectforeground=sel_fg)
        except Exception:
            g.es("exception setting body pane text selection foreground color")
            g.es_exception()

        if sys.platform != "win32": # Maybe a Windows bug.
            fg = c.config.getColor("body_cursor_foreground_color")
            bg = c.config.getColor("body_cursor_background_color")
            if fg and bg:
                cursor="xterm" + " " + fg + " " + bg
                try: w.configure(cursor=cursor)
                except:
                    import traceback ; traceback.print_exc()
    #@+node:ekr.20081121110412.135: *4* tkBody.setFontFromConfig
    def setFontFromConfig (self,w=None):

        c = self.c

        if not w: w = self.bodyCtrl

        font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        w.configure(font=font)

        # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
    #@+node:ekr.20081121110412.136: *4* Focus (tkBody)
    def hasFocus (self):

        return self.bodyCtrl == self.frame.top.focus_displayof()

    def setFocus (self):

        self.c.widgetWantsFocus(self.bodyCtrl)
    #@+node:ekr.20081121110412.137: *4* Tk bindings (tkBody)
    #@+node:ekr.20081121110412.138: *5* Color tags (Tk spelling) (tkBody)
    def tag_add (self,tagName,index1,index2):
        self.bodyCtrl.tag_add(tagName,index1,index2)

    def tag_bind (self,tagName,event,callback):
        self.c.tag_bind(self.bodyCtrl,tagName,event,callback)

    def tag_configure (self,colorName,**keys):
        self.bodyCtrl.tag_configure(colorName,keys)

    def tag_delete(self,tagName):
        self.bodyCtrl.tag_delete(tagName)

    def tag_names(self,*args): # New in Leo 4.4.1.
        return self.bodyCtrl.tag_names(*args)

    def tag_remove (self,tagName,index1,index2):
        return self.bodyCtrl.tag_remove(tagName,index1,index2)
    #@+node:ekr.20081121110412.139: *5* Configuration (Tk spelling) (tkBody)
    def cget(self,*args,**keys):

        val = self.bodyCtrl.cget(*args,**keys)

        if g.app.trace:
            g.trace(val,args,keys)

        return val

    def configure (self,*args,**keys):

        # g.trace(args,keys)

        return self.bodyCtrl.configure(*args,**keys)
    #@+node:ekr.20081121110412.140: *5* Height & width
    # def getBodyPaneHeight (self):

        # return self.bodyCtrl.winfo_height()

    # def getBodyPaneWidth (self):

        # return self.bodyCtrl.winfo_width()
    #@+node:ekr.20081121110412.141: *5* Idle time...
    def scheduleIdleTimeRoutine (self,function,*args,**keys):

        if not g.app.unitTesting:
            self.bodyCtrl.after_idle(function,*args,**keys)
    #@+node:ekr.20081121110412.142: *5* Menus (tkBody) (May cause problems)
    def bind (self,*args,**keys):

        c = self.c
        return self.bodyCtrl.bind(*args,**keys)
    #@+node:ekr.20081121110412.143: *4* Editors (tkBody)
    #@+node:ekr.20081121110412.144: *5* createEditorFrame
    def createEditorFrame (self,pane):

        f = Tk.Frame(pane)
        f.pack(side='top',expand=1,fill='both')
        return f
    #@+node:ekr.20081121110412.145: *5* packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a Tk label widget.'''

        if not hasattr(w,'leo_label') or not w.leo_label:
            # g.trace('w.leo_frame',id(w.leo_frame))
            w.pack_forget()
            w.leo_label = Tk.Label(w.leo_frame)
            w.leo_label.pack(side='top')
            w.pack(expand=1,fill='both')
    #@+node:ekr.20081121110412.146: *5* setEditorColors
    def setEditorColors (self,bg,fg):

        c = self.c ; d = self.editorWidgets

        for key in d:
            w2 = d.get(key)
            # g.trace(id(w2),bg,fg)
            try:
                w2.configure(bg=bg,fg=fg)
            except Exception:
                g.es_exception()
    #@-others
#@+node:ekr.20081121110412.147: *3* class leoTkinterFrame
class leoTkinterFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in Tk/tkinter."""

    #@+others
    #@+node:ekr.20081121110412.148: *4*  Birth & Death (tkFrame)
    #@+node:ekr.20081121110412.149: *5* __init__ (tkFrame)
    def __init__(self,title,gui):

        # Init the base class.
        leoFrame.leoFrame.__init__(self,gui)

        self.title = title

        leoTkinterFrame.instances += 1

        self.c = None # Set in finishCreate.
        self.iconBarClass = self.tkIconBarClass
        self.statusLineClass = self.tkStatusLineClass
        self.iconBar = None

        self.trace_status_line = None # Set in finishCreate.

        #@+<< set the leoTkinterFrame ivars >>
        #@+node:ekr.20081121110412.150: *6* << set the leoTkinterFrame ivars >> (removed frame.bodyCtrl ivar)
        # "Official ivars created in createLeoFrame and its allies.
        self.bar1 = None
        self.bar2 = None
        self.body = None
        self.f1 = self.f2 = None
        self.findPanel = None # Inited when first opened.
        self.iconBarComponentName = 'iconBar'
        self.iconFrame = None 
        self.log = None
        self.canvas = None
        self.outerFrame = None
        self.statusFrame = None
        self.statusLineComponentName = 'statusLine'
        self.statusText = None 
        self.statusLabel = None 
        self.top = None
        self.tree = None
        # self.treeBar = None # Replaced by injected frame.canvas.leo_treeBar.

        # Used by event handlers...
        self.controlKeyIsDown = False # For control-drags
        self.draggedItem = None
        self.isActive = True
        self.redrawCount = 0
        self.wantedWidget = None
        self.wantedCallbackScheduled = False
        self.scrollWay = None
        #@-<< set the leoTkinterFrame ivars >>
    #@+node:ekr.20081121110412.151: *5* __repr__ (tkFrame)
    def __repr__ (self):

        return "<leoTkinterFrame: %s>" % self.title
    #@+node:ekr.20081121110412.152: *5* tkFrame.finishCreate & helpers
    def finishCreate (self,c):

        f = self ; f.c = c
        # g.trace('tkFrame','c',c,g.callers())

        self.bigTree           = c.config.getBool('big_outline_pane')
        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters      = c.config.getBool('use_chapters')
        self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

        # This must be done after creating the commander.
        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
        f.createOuterFrames()
        f.createIconBar()
        f.createLeoSplitters(f.outerFrame)
        f.createSplitterComponents()
        f.createStatusLine()
        f.createFirstTreeNode()
        f.menu = leoTkinterMenu(f)
            # c.finishCreate calls f.createMenuBar later.
        c.setLog()
        g.app.windowList.append(f)
        f.miniBufferWidget = f.createMiniBufferWidget()
        c.bodyWantsFocus()

        # f.enableTclTraces()
    #@+node:ekr.20081121110412.153: *6* createOuterFrames
    def createOuterFrames (self):

        f = self ; c = f.c
        f.top = top = Tk.Toplevel()
        g.app.gui.attachLeoIcon(top)
        top.title(f.title)
        top.minsize(30,10) # In grid units.

        if g.os_path_exists(g.app.user_xresources_path):
            f.top.option_readfile(g.app.user_xresources_path)

        f.top.protocol("WM_DELETE_WINDOW", f.OnCloseLeoEvent)
        c.bind(f.top,"<Button-1>", f.OnActivateLeoEvent)

        c.bind(f.top,"<Control-KeyPress>",f.OnControlKeyDown)
        c.bind(f.top,"<Control-KeyRelease>",f.OnControlKeyUp)

        # These don't work on Windows. Because of bugs in window managers,
        # there is NO WAY to know which window is on top!
        # c.bind(f.top,"<Activate>",f.OnActivateLeoEvent)
        # c.bind(f.top,"<Deactivate>",f.OnDeactivateLeoEvent)

        # Create the outer frame, the 'hull' component.
        f.outerFrame = Tk.Frame(top)
        f.outerFrame.pack(expand=1,fill="both")
    #@+node:ekr.20081121110412.154: *6* createSplitterComponents (tkFrame)
    def createSplitterComponents (self):

        f = self ; c = f.c

        # Create the canvas, tree, log and body.
        if f.use_chapters:
            c.chapterController = cc = leoChapters.chapterController(c)

        # split1.pane1 is the secondary splitter.

        if self.bigTree: # Put outline in the main splitter.
            if self.use_chapters and self.use_chapter_tabs:
                cc.tt = leoTkinterTreeTab(c,f.split1Pane2,cc)
            f.canvas = f.createCanvas(f.split1Pane1)
            f.tree  = leoTkinterTree(c,f,f.canvas)
            f.log   = leoTkinterLog(f,f.split2Pane2)
            f.body  = leoTkinterBody(f,f.split2Pane1)
        else:
            if self.use_chapters and self.use_chapter_tabs:
                cc.tt = leoTkinterTreeTab(c,f.split2Pane1,cc)
            f.canvas = f.createCanvas(f.split2Pane1)
            f.tree   = leoTkinterTree(c,f,f.canvas)
            f.log    = leoTkinterLog(f,f.split2Pane2)
            f.body   = leoTkinterBody(f,f.split1Pane2)

        # Configure.
        f.setTabWidth(c.tab_width)
        f.reconfigurePanes()
        f.body.setFontFromConfig()
        f.body.setColorFromConfig()
    #@+node:ekr.20081121110412.155: *6* f.enableTclTraces
    def enableTclTraces (self):

        c = self.c
        # Put this in unit tests before the assert:
        # c.frame.bar1.unbind_all("<FocusIn>")
        # c.frame.bar1.unbind_all("<FocusOut>")

        # Any widget would do:
        w = c.frame.bar1
        if True:
            def focusIn (event):
                g.pr("Focus in  %s (%s)" % (
                    event.widget,event.widget.winfo_class()))

            def focusOut (event):
                g.pr("Focus out %s (%s)" % (
                    event.widget,event.widget.winfo_class()))

            w.bind_all("<FocusIn>", focusIn)
            w.bind_all("<FocusOut>", focusOut)
        else:
            def tracewidget(event):
                g.trace('enabling widget trace')
                Pmw.tracetk(event.widget, 1)

            def untracewidget(event):
                g.trace('disabling widget trace')
                Pmw.tracetk(event.widget,0)

            w.bind_all("<Control-1>", tracewidget)
            w.bind_all("<Control-Shift-1>", untracewidget)
    #@+node:ekr.20081121110412.156: *5* tkFrame.createCanvas & helpers
    def createCanvas (self,parentFrame,pack=True):

        c = self.c

        scrolls = c.config.getBool('outline_pane_scrolls_horizontally')
        scrolls = g.choose(scrolls,1,0)
        canvas = self.createTkTreeCanvas(parentFrame,scrolls,pack)
        self.setCanvasColorFromConfig(canvas)

        return canvas
    #@+node:ekr.20081121110412.157: *6* f.createTkTreeCanvas & callbacks
    def createTkTreeCanvas (self,parentFrame,scrolls,pack):

        frame = self ; c = frame.c

        canvas = Tk.Canvas(parentFrame,name="canvas",
            bd=0,bg="white",relief="flat")

        treeBar = Tk.Scrollbar(parentFrame,name="treeBar")

        # New in Leo 4.4.3 b1: inject the ivar into the canvas.
        canvas.leo_treeBar = treeBar

        # Bind mouse wheel event to canvas
        if sys.platform != "win32": # Works on 98, crashes on XP.
            c.bind(canvas,"<MouseWheel>", frame.OnMouseWheel)
            if 1: # New in 4.3.
                #@+<< workaround for mouse-wheel problems >>
                #@+node:ekr.20081121110412.158: *7* << workaround for mouse-wheel problems >>
                # Handle mapping of mouse-wheel to buttons 4 and 5.

                def mapWheel(e):
                    if e.num == 4: # Button 4
                        e.delta = 120
                        return frame.OnMouseWheel(e)
                    elif e.num == 5: # Button 5
                        e.delta = -120
                        return frame.OnMouseWheel(e)

                c.bind2(canvas,"<ButtonPress>",mapWheel,add=1)
                #@-<< workaround for mouse-wheel problems >>

        canvas['yscrollcommand'] = self.setCallback
        treeBar['command']     = self.yviewCallback
        treeBar.pack(side="right", fill="y")
        if scrolls: 
            treeXBar = Tk.Scrollbar( 
                parentFrame,name='treeXBar',orient="horizontal") 
            canvas['xscrollcommand'] = treeXBar.set 
            treeXBar['command'] = canvas.xview 
            treeXBar.pack(side="bottom", fill="x")

        if pack:
            canvas.pack(expand=1,fill="both")

        c.bind(canvas,"<Button-1>", frame.OnActivateTree)

        # Handle mouse wheel in the outline pane.
        if sys.platform == "linux2": # This crashes tcl83.dll
            c.bind(canvas,"<MouseWheel>", frame.OnMouseWheel)

        # g.print_bindings("canvas",canvas)
        return canvas
    #@+node:ekr.20081121110412.159: *7* Scrolling callbacks (tkFrame)
    def setCallback (self,*args,**keys):

        """Callback to adjust the scrollbar.

        Args is a tuple of two floats describing the fraction of the visible area."""

        #g.trace(self.tree.redrawCount,args,g.callers())
        self.canvas.leo_treeBar.set(*args,**keys)

        if self.tree.allocateOnlyVisibleNodes:
            self.tree.setVisibleArea(args)

    def yviewCallback (self,*args,**keys):

        """Tell the canvas to scroll"""

        #g.trace(vyiewCallback,args,keys,g.callers())

        if self.tree.allocateOnlyVisibleNodes:
            self.tree.allocateNodesBeforeScrolling(args)

        self.canvas.yview(*args,**keys)
    #@+node:ekr.20081121110412.160: *6* f.setCanvasColorFromConfig
    def setCanvasColorFromConfig (self,canvas):

        c = self.c

        bg = c.config.getColor("outline_pane_background_color") or 'white'

        try:
            canvas.configure(bg=bg)
        except:
            g.es("exception setting outline pane background color")
            g.es_exception()
    #@+node:ekr.20081121110412.161: *5* tkFrame.createLeoSplitters & helpers
    #@+at The key invariants used throughout this code:
    # 
    # 1. self.splitVerticalFlag tells the alignment of the main splitter and
    # 2. not self.splitVerticalFlag tells the alignment of the secondary splitter.
    # 
    # Only the general-purpose divideAnySplitter routine doesn't know about these
    # invariants. So most of this code is specialized for Leo's window. OTOH, creating
    # a single splitter window would be much easier than this code.
    #@@c

    def createLeoSplitters (self,parentFrame):

        # Splitter 1 is the main splitter.
        f1,bar1,split1Pane1,split1Pane2 = self.createLeoTkSplitter(
            parentFrame,self.splitVerticalFlag,'splitter1')

        self.f1,self.bar1 = f1,bar1
        self.split1Pane1,self.split1Pane2 = split1Pane1,split1Pane2

        # ** new **
        split2parent = g.choose(self.bigTree,split1Pane2,split1Pane1)

        # Splitter 2 is the secondary splitter.
        f2,bar2,split2Pane1,split2Pane2 = self.createLeoTkSplitter(
            # split1Pane1,not self.splitVerticalFlag,'splitter2')
            split2parent,not self.splitVerticalFlag,'splitter2')

        self.f2,self.bar2 = f2,bar2
        self.split2Pane1,self.split2Pane2 = split2Pane1,split2Pane2
    #@+node:ekr.20081121110412.162: *6* createLeoTkSplitter
    def createLeoTkSplitter (self,parent,verticalFlag,componentName):

        c = self.c

        # Create the frames.
        f = Tk.Frame(parent,bd=0,relief="flat")
        f.pack(expand=1,fill="both",pady=1)

        f1 = Tk.Frame(f)
        f2 = Tk.Frame(f)
        bar = Tk.Frame(f,bd=2,relief="raised",bg="LightSteelBlue2")

        # Configure and place the frames.
        self.configureBar(bar,verticalFlag)
        self.bindBar(bar,verticalFlag)
        self.placeSplitter(bar,f1,f2,verticalFlag)

        return f, bar, f1, f2
    #@+node:ekr.20081121110412.163: *6* bindBar
    def bindBar (self, bar, verticalFlag):

        c = self.c

        if verticalFlag == self.splitVerticalFlag:
            c.bind(bar,"<B1-Motion>", self.onDragMainSplitBar)

        else:
            c.bind(bar,"<B1-Motion>", self.onDragSecondarySplitBar)
    #@+node:ekr.20081121110412.164: *6* divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self, frac, verticalFlag, bar, pane1, pane2):

        # if self.bigTree:
            # pane1,pane2 = pane2,pane1

        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            bar.place(rely=frac)
            pane1.place(relheight=frac)
            pane2.place(relheight=1-frac)
        else:
            # Panes arranged horizontally; vertical splitter bar
            bar.place(relx=frac)
            pane1.place(relwidth=frac)
            pane2.place(relwidth=1-frac)
    #@+node:ekr.20081121110412.165: *6* divideLeoSplitter
    # Divides the main or secondary splitter, using the key invariant.
    def divideLeoSplitter (self, verticalFlag, frac):

        if self.splitVerticalFlag == verticalFlag:
            self.divideLeoSplitter1(frac,verticalFlag)
            self.ratio = frac # Ratio of body pane to tree pane.
        else:
            self.divideLeoSplitter2(frac,verticalFlag)
            self.secondary_ratio = frac # Ratio of tree pane to log pane.

    # Divides the main splitter.
    def divideLeoSplitter1 (self, frac, verticalFlag): 
        self.divideAnySplitter(frac, verticalFlag,
            self.bar1, self.split1Pane1, self.split1Pane2)

    # Divides the secondary splitter.
    def divideLeoSplitter2 (self, frac, verticalFlag): 
        self.divideAnySplitter (frac, verticalFlag,
            self.bar2, self.split2Pane1, self.split2Pane2)
    #@+node:ekr.20081121110412.166: *6* onDrag...
    def onDragMainSplitBar (self, event):
        self.onDragSplitterBar(event,self.splitVerticalFlag)

    def onDragSecondarySplitBar (self, event):
        self.onDragSplitterBar(event,not self.splitVerticalFlag)

    def onDragSplitterBar (self, event, verticalFlag):

        # x and y are the coordinates of the cursor relative to the bar, not the main window.
        bar = event.widget
        x = event.x
        y = event.y
        top = bar.winfo_toplevel()

        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            wRoot = top.winfo_rooty()
            barRoot = bar.winfo_rooty()
            wMax = top.winfo_height()
            offset = float(barRoot) + y - wRoot
        else:
            # Panes arranged horizontally; vertical splitter bar
            wRoot = top.winfo_rootx()
            barRoot = bar.winfo_rootx()
            wMax = top.winfo_width()
            offset = float(barRoot) + x - wRoot

        # Adjust the pixels, not the frac.
        if offset < 3: offset = 3
        if offset > wMax - 2: offset = wMax - 2
        # Redraw the splitter as the drag is occuring.
        frac = float(offset) / wMax
        # g.trace(frac)
        self.divideLeoSplitter(verticalFlag, frac)
    #@+node:ekr.20081121110412.167: *6* placeSplitter
    def placeSplitter (self,bar,pane1,pane2,verticalFlag):

        # if self.bigTree:
            # pane1,pane2 = pane2,pane1

        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            pane1.place(relx=0.5, rely =   0, anchor="n", relwidth=1.0, relheight=0.5)
            pane2.place(relx=0.5, rely = 1.0, anchor="s", relwidth=1.0, relheight=0.5)
            bar.place  (relx=0.5, rely = 0.5, anchor="c", relwidth=1.0)
        else:
            # Panes arranged horizontally; vertical splitter bar
            # adj gives tree pane more room when tiling vertically.
            adj = g.choose(verticalFlag != self.splitVerticalFlag,0.65,0.5)
            pane1.place(rely=0.5, relx =   0, anchor="w", relheight=1.0, relwidth=adj)
            pane2.place(rely=0.5, relx = 1.0, anchor="e", relheight=1.0, relwidth=1.0-adj)
            bar.place  (rely=0.5, relx = adj, anchor="c", relheight=1.0)
    #@+node:ekr.20081121110412.168: *5* Destroying the tkFrame
    #@+node:ekr.20081121110412.169: *6* destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c ; tree = frame.tree ; body = self.body

        # g.printGcAll()

        # Do this first.
        #@+<< clear all vnodes and tnodes in the tree >>
        #@+node:ekr.20081121110412.170: *7* << clear all vnodes and tnodes in the tree>>
        # Using a dict here is essential for adequate speed.
        vList = [] ; tDict = {}

        for p in c.all_unique_positions():
            vList.append(p.v)
            if p.v:
                key = id(p.v)
                if key not in tDict:
                    tDict[key] = p.v

        for key in tDict:
            g.clearAllIvars(tDict[key])

        for v in vList:
            g.clearAllIvars(v)

        vList = [] ; tDict = {} # Remove these references immediately.
        #@-<< clear all vnodes and tnodes in the tree >>

        # Destroy all ivars in subcommanders.
        g.clearAllIvars(c.atFileCommands)
        if c.chapterController: # New in Leo 4.4.3 b1.
            g.clearAllIvars(c.chapterController)
        g.clearAllIvars(c.fileCommands)
        g.clearAllIvars(c.keyHandler) # New in Leo 4.4.3 b1.
        g.clearAllIvars(c.importCommands)
        g.clearAllIvars(c.tangleCommands)
        g.clearAllIvars(c.undoer)

        g.clearAllIvars(c)
        g.clearAllIvars(body.colorizer)
        g.clearAllIvars(body)
        g.clearAllIvars(tree)

        # This must be done last.
        frame.destroyAllPanels()
        g.clearAllIvars(frame)

    #@+node:ekr.20081121110412.171: *6* destroyAllPanels
    def destroyAllPanels (self):

        """Destroy all panels attached to this frame."""

        panels = (self.comparePanel, self.colorPanel, self.findPanel, self.fontPanel, self.prefsPanel)

        for panel in panels:
            if panel:
                panel.top.destroy()
    #@+node:ekr.20081121110412.172: *6* destroySelf (tkFrame)
    def destroySelf (self):

        # g.trace(self)

        # Remember these: we are about to destroy all of our ivars!
        top = self.top 
        c = self.c

        # Indicate that the commander is no longer valid.
        c.exists = False

        # New in Leo 4.4.8: Finish all window tasks before killing the window.
        top.update()

        # g.trace(self)

        # Important: this destroys all the objects of the commander too.
        self.destroyAllObjects()

        # New in Leo 4.4.8: Finish all window tasks before killing the window.
        top.update()

        c.exists = False # Make sure this one ivar has not been destroyed.

        top.destroy()
    #@+node:ekr.20081121110412.173: *4* class tkStatusLineClass (tkFrame)
    class tkStatusLineClass:

        '''A class representing the status line.'''

        #@+others
        #@+node:ekr.20081121110412.174: *5* ctor
        def __init__ (self,c,parentFrame):

            self.c = c
            self.colorTags = [] # list of color names used as tags.
            self.enabled = False
            self.isVisible = False
            self.lastRow = self.lastCol = 0
            self.log = c.frame.log
            #if 'black' not in self.log.colorTags:
            #    self.log.colorTags.append("black")
            self.parentFrame = parentFrame
            self.statusFrame = Tk.Frame(parentFrame,bd=2)
            text = "line 0, col 0, fcol 0"
            width = len(text) + 4
            self.labelWidget = Tk.Label(self.statusFrame,text=text,width=width,anchor="w")
            self.labelWidget.pack(side="left",padx=1)

            bg = self.statusFrame.cget("background")
            self.textWidget = w = g.app.gui.bodyTextWidget(
                self.statusFrame,
                height=1,state="disabled",bg=bg,relief="groove",name='status-line')
            self.textWidget.pack(side="left",expand=1,fill="x")
            c.bind(w,"<Button-1>", self.onActivate)
            self.show()

            c.frame.statusFrame = self.statusFrame
            c.frame.statusLabel = self.labelWidget
            c.frame.statusText  = self.textWidget
        #@+node:ekr.20081121110412.175: *5* clear
        def clear (self):

            w = self.textWidget
            if not w: return

            w.configure(state="normal")
            w.delete(0,"end")
            w.configure(state="disabled")
        #@+node:ekr.20081121110412.176: *5* enable, disable & isEnabled
        def disable (self,background=None):

            c = self.c ; w = self.textWidget
            if w:
                if not background:
                    background = self.statusFrame.cget("background")
                w.configure(state="disabled",background=background)
            self.enabled = False
            c.bodyWantsFocus()

        def enable (self,background="white"):

            # g.trace()
            c = self.c ; w = self.textWidget
            if w:
                w.configure(state="normal",background=background)
                c.widgetWantsFocus(w)
            self.enabled = True

        def isEnabled(self):
            return self.enabled
        #@+node:ekr.20081121110412.177: *5* get
        def get (self):

            w = self.textWidget
            if w:
                return w.getAllText()
            else:
                return ""
        #@+node:ekr.20081121110412.178: *5* getFrame
        def getFrame (self):

            return self.statusFrame
        #@+node:ekr.20081121110412.179: *5* onActivate
        def onActivate (self,event=None):

            # Don't change background as the result of simple mouse clicks.
            background = self.statusFrame.cget("background")
            self.enable(background=background)
        #@+node:ekr.20081121110412.180: *5* pack & show
        def pack (self):

            if not self.isVisible:
                self.isVisible = True
                self.statusFrame.pack(fill="x",pady=1)

        show = pack
        #@+node:ekr.20081121110412.181: *5* put (leoTkinterFrame:statusLineClass)
        def put(self,s,color=None):

            # g.trace('tkStatusLine',self.textWidget,s)

            w = self.textWidget
            if not w:
                g.trace('tkStatusLine','***** disabled')
                return

            w.configure(state="normal")
            w.insert("end",s)

            if color:
                if color not in self.colorTags:
                    self.colorTags.append(color)
                    w.tag_config(color,foreground=color)
                w.tag_add(color,"end-%dc" % (len(s)+1),"end-1c")
                w.tag_config("black",foreground="black")
                w.tag_add("black","end")

            w.configure(state="disabled")
        #@+node:ekr.20081121110412.182: *5* setBindings (tkStatusLine)
        def setBindings (self):

            c = self.c ; k = c.keyHandler ; w = self.textWidget

            c.bind(w,'<Key>',k.masterKeyHandler)

            k.completeAllBindingsForWidget(w)
        #@+node:ekr.20081121110412.183: *5* unpack & hide
        def unpack (self):

            if self.isVisible:
                self.isVisible = False
                self.statusFrame.pack_forget()

        hide = unpack
        #@+node:ekr.20081121110412.184: *5* update (statusLine)
        def update (self):

            c = self.c ; bodyCtrl = c.frame.body.bodyCtrl

            if g.app.killed or not self.isVisible:
                return

            s = bodyCtrl.getAllText()    
            index = bodyCtrl.getInsertPoint()
            row,col = g.convertPythonIndexToRowCol(s,index)
            if col > 0:
                s2 = s[index-col:index]
                s2 = g.toUnicode(s2)
                col = g.computeWidth (s2,c.tab_width)
            p = c.currentPosition()
            fcol = col + p.textOffset()

            # Important: this does not change the focus because labels never get focus.
            self.labelWidget.configure(text="line %d, col %d, fcol %d" % (row,col,fcol))
            self.lastRow = row
            self.lastCol = col
            self.lastFcol = fcol
        #@-others
    #@+node:ekr.20081121110412.185: *4* class tkIconBarClass
    class tkIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@+others
        #@+node:ekr.20081121110412.186: *5*  ctor
        def __init__ (self,c,parentFrame):

            self.c = c

            self.buttons = {}

            # Create a parent frame that will never be unpacked.
            # This allows us to pack and unpack the container frame without it moving.
            self.iconFrameParentFrame = Tk.Frame(parentFrame)
            self.iconFrameParentFrame.pack(fill="x",pady=0)

            # Create a container frame to hold individual row frames.
            # We hide all icons by doing pack_forget on this one frame.
            self.iconFrameContainerFrame = Tk.Frame(self.iconFrameParentFrame)
                # Packed in self.show()

            self.addRow()
            self.font = None
            self.parentFrame = parentFrame
            self.visible = False
            self.widgets_per_row = c.config.getInt('icon_bar_widgets_per_row') or 10
            self.show() # pack the container frame.
        #@+node:ekr.20081121110412.187: *5* add
        def add(self,*args,**keys):

            """Add a button containing text or a picture to the icon bar.

            Pictures take precedence over text"""

            c = self.c
            text = keys.get('text')
            imagefile = keys.get('imagefile')
            image = keys.get('image')
            command = keys.get('command')
            bg = keys.get('bg')

            if not imagefile and not image and not text: return

            self.addRowIfNeeded()
            f = self.iconFrame # Bind this after possibly creating a new row.

            if command:
                def commandCallBack(c=c,command=command):
                    val = command()
                    if c.exists:
                        c.bodyWantsFocus()
                        c.outerUpdate()
                    return val
            else:
                def commandCallback(n=g.app.iconWidgetCount):
                    g.pr("command for widget %s" % (n))
                command = commandCallback

            if imagefile or image:
                #@+<< create a picture >>
                #@+node:ekr.20081121110412.188: *6* << create a picture >>
                try:
                    if imagefile:
                        # Create the image.  Throws an exception if file not found
                        imagefile = g.os_path_join(g.app.loadDir,imagefile)
                        imagefile = g.os_path_normpath(imagefile)
                        image = Tk.PhotoImage(master=g.app.root,file=imagefile)
                        g.trace(image,imagefile)

                        # Must keep a reference to the image!
                        try:
                            refs = g.app.iconImageRefs
                        except:
                            refs = g.app.iconImageRefs = []

                        refs.append((imagefile,image),)

                    if not bg:
                        bg = f.cget("bg")

                    try:
                        b = Tk.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
                    except Exception:
                        g.es_print('image does not exist',image,color='blue')
                        b = Tk.Button(f,relief='flat',bd=0,command=command,bg=bg)
                    b.pack(side="left",fill="y")
                    return b

                except:
                    g.es_exception()
                    return None
                #@-<< create a picture >>
            elif text:
                b = Tk.Button(f,text=text,relief="groove",bd=2,command=command)
                if not self.font:
                    self.font = c.config.getFontFromParams(
                        "button_text_font_family", "button_text_font_size",
                        "button_text_font_slant",  "button_text_font_weight",)
                b.configure(font=self.font)
                if bg: b.configure(bg=bg)
                b.pack(side="left", fill="none")
                return b

            return None
        #@+node:ekr.20081121110412.189: *5* addRow
        def addRow(self,height=None):

            if height is None:
                height = '5m'

            w = Tk.Frame(self.iconFrameContainerFrame,height=height,bd=2,relief="groove")
            w.pack(fill="x",pady=2)
            self.iconFrame = w
            self.c.frame.iconFrame = w
            return w
        #@+node:ekr.20081121110412.190: *5* addRowIfNeeded
        def addRowIfNeeded (self):

            '''Add a new icon row if there are too many widgets.'''

            try:
                n = g.app.iconWidgetCount
            except:
                n = g.app.iconWidgetCount = 0

            if n >= self.widgets_per_row:
                g.app.iconWidgetCount = 0
                self.addRow()

            g.app.iconWidgetCount += 1
        #@+node:ekr.20081121110412.191: *5* addWidget
        def addWidget (self,w):

            self.addRowIfNeeded()
            w.pack(side="left", fill="none")


        #@+node:ekr.20081121110412.192: *5* clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            f = self.iconFrameContainerFrame

            for slave in f.pack_slaves():
                slave.pack_forget()
            f.pack_forget()

            self.addRow(height='0m')

            self.visible = False

            g.app.iconWidgetCount = 0
            g.app.iconImageRefs = []
        #@+node:ekr.20081121110412.193: *5* deleteButton (new in Leo 4.4.3)
        def deleteButton (self,w):

            w.pack_forget()
            self.c.bodyWantsFocus()
            self.c.outerUpdate()
        #@+node:ekr.20081121110412.194: *5* getFrame & getNewFrame
        def getFrame (self):

            return self.iconFrame

        def getNewFrame (self):

            # Pre-check that there is room in the row, but don't bump the count.
            self.addRowIfNeeded()
            g.app.iconWidgetCount -= 1

            # Allocate the frame in the possibly new row.
            frame = Tk.Frame(self.iconFrame)
            return frame

        #@+node:ekr.20081121110412.195: *5* pack (show)
        def pack (self):

            """Show the icon bar by repacking it"""

            if not self.visible:
                self.visible = True
                self.iconFrameContainerFrame.pack(fill='x',pady=2)

        show = pack
        #@+node:ekr.20081121110412.196: *5* setCommandForButton (new in Leo 4.4.3)
        def setCommandForButton(self,b,command):

            b.configure(command=command)
        #@+node:ekr.20081121110412.197: *5* unpack (hide)
        def unpack (self):

            """Hide the icon bar by unpacking it."""

            if self.visible:
                self.visible = False
                w = self.iconFrameContainerFrame
                w.pack_forget()

        hide = unpack
        #@-others
    #@+node:ekr.20081121110412.198: *4* Minibuffer methods (tkFrame)
    #@+node:ekr.20081121110412.199: *5* showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        frame = self

        if not frame.minibufferVisible:
            frame.minibufferFrame.pack(side='bottom',fill='x')
            frame.minibufferVisible = True
    #@+node:ekr.20081121110412.200: *5* hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        frame = self
        if frame.minibufferVisible:
            frame.minibufferFrame.pack_forget()
            frame.minibufferVisible = False
    #@+node:ekr.20081121110412.201: *5* f.createMiniBufferWidget
    def createMiniBufferWidget (self):

        '''Create the minbuffer below the status line.'''

        frame = self ; c = frame.c

        frame.minibufferFrame = f = Tk.Frame(frame.outerFrame,relief='flat',borderwidth=0)
        if c.showMinibuffer:
            f.pack(side='bottom',fill='x')

        lab = Tk.Label(f,text='mini-buffer',justify='left',anchor='nw',foreground='blue')
        lab.pack(side='left')

        label = g.app.gui.plainTextWidget(
            f,height=1,relief='groove',background='lightgrey',name='minibuffer')
        label.pack(side='left',fill='x',expand=1,padx=2,pady=1)

        frame.minibufferVisible = c.showMinibuffer

        return label
    #@+node:ekr.20081121110412.202: *5* f.setMinibufferBindings
    def setMinibufferBindings (self):

        '''Create bindings for the minibuffer..'''

        f = self ; c = f.c ; k = c.k ; w = f.miniBufferWidget

        # g.trace(g.callers(4))

        table = [
            ('<Key>',           k.masterKeyHandler),
            ('<Button-1>',      k.masterClickHandler),
            ('<Button-3>',      k.masterClick3Handler),
            ('<Double-1>',      k.masterDoubleClickHandler),
            ('<Double-3>',      k.masterDoubleClick3Handler),
        ]

        table2 = (
            ('<Button-2>',      k.masterClickHandler),
        )

        if c.config.getBool('allow_middle_button_paste'):
            table.extend(table2)

        for kind,callback in table:
            c.bind(w,kind,callback)

        if 0:
            if sys.platform.startswith('win'):
                # Support Linux middle-button paste easter egg.
                c.bind(w,"<Button-2>",f.OnPaste)
    #@+node:ekr.20081121110412.203: *4* Configuration (tkFrame)
    #@+node:ekr.20081121110412.204: *5* configureBar (tkFrame)
    def configureBar (self,bar,verticalFlag):

        c = self.c

        # Get configuration settings.
        w = c.config.getInt("split_bar_width")
        if not w or w < 1: w = 7
        relief = c.config.get("split_bar_relief","relief")
        if not relief: relief = "flat"
        color = c.config.getColor("split_bar_color")
        if not color: color = "LightSteelBlue2"

        try:
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(relief=relief,height=w,bg=color,cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(relief=relief,width=w,bg=color,cursor="sb_h_double_arrow")
        except: # Could be a user error. Use all defaults
            g.es("exception in user configuration for splitbar")
            g.es_exception()
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(height=7,cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(width=7,cursor="sb_h_double_arrow")
    #@+node:ekr.20081121110412.205: *5* configureBarsFromConfig (tkFrame)
    def configureBarsFromConfig (self):

        c = self.c

        w = c.config.getInt("split_bar_width")
        if not w or w < 1: w = 7

        relief = c.config.get("split_bar_relief","relief")
        if not relief or relief == "": relief = "flat"

        color = c.config.getColor("split_bar_color")
        if not color or color == "": color = "LightSteelBlue2"

        if self.splitVerticalFlag:
            bar1,bar2=self.bar1,self.bar2
        else:
            bar1,bar2=self.bar2,self.bar1

        try:
            bar1.configure(relief=relief,height=w,bg=color)
            bar2.configure(relief=relief,width=w,bg=color)
        except: # Could be a user error.
            g.es("exception in user configuration for splitbar")
            g.es_exception()
    #@+node:ekr.20081121110412.206: *5* reconfigureFromConfig (tkFrame)
    def reconfigureFromConfig (self):

        frame = self ; c = frame.c

        frame.tree.setFontFromConfig()
        frame.configureBarsFromConfig()

        frame.body.setFontFromConfig()
        frame.body.setColorFromConfig()

        frame.setTabWidth(c.tab_width)
        frame.log.setFontFromConfig()
        frame.log.setColorFromConfig()

        c.redraw_now()
    #@+node:ekr.20081121110412.207: *5* setInitialWindowGeometry (tkFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@+node:ekr.20081121110412.208: *5* setTabWidth (tkFrame)
    def setTabWidth (self, w):

        try: # This can fail when called from scripts
            # Use the present font for computations.
            font = self.body.bodyCtrl.cget("font") # 2007/10/27
            root = g.app.root # 4/3/03: must specify root so idle window will work properly.
            font = tkFont.Font(root=root,font=font)
            tabw = font.measure(" " * abs(w)) # 7/2/02
            self.body.bodyCtrl.configure(tabs=tabw)
            self.tab_width = w
            # g.trace(w,tabw)
        except:
            g.es_exception()
    #@+node:ekr.20081121110412.209: *5* setWrap (tkFrame)
    def setWrap (self,p):

        c = self.c
        theDict = c.scanAllDirectives(p)
        if not theDict: return

        wrap = theDict.get("wrap")
        if self.body.wrapState == wrap: return

        self.body.wrapState = wrap
        w = self.body.bodyCtrl

        # g.trace(wrap)
        if wrap:
            w.configure(wrap="word") # 2007/10/25
            w.leo_bodyXBar.pack_forget() # 2007/10/31
        else:
            w.configure(wrap="none")
            # Bug fix: 3/10/05: We must unpack the text area to make the scrollbar visible.
            w.pack_forget()  # 2007/10/25
            w.leo_bodyXBar.pack(side="bottom", fill="x") # 2007/10/31
            w.pack(expand=1,fill="both")  # 2007/10/25
    #@+node:ekr.20081121110412.210: *5* setTopGeometry (tkFrame)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):

        # Put the top-left corner on the screen.
        x = max(10,x) ; y = max(10,y)

        if adjustSize:
            top = self.top
            sw = top.winfo_screenwidth()
            sh = top.winfo_screenheight()

            # Adjust the size so the whole window fits on the screen.
            w = min(sw-10,w)
            h = min(sh-10,h)

            # Adjust position so the whole window fits on the screen.
            if x + w > sw: x = 10
            if y + h > sh: y = 10

        geom = "%dx%d%+d%+d" % (w,h,x,y)

        self.top.geometry(geom)
    #@+node:ekr.20081121110412.211: *5* reconfigurePanes (use config bar_width) (tkFrame)
    def reconfigurePanes (self):

        c = self.c

        border = c.config.getInt('additional_body_text_border')
        if border == None: border = 0

        # The body pane needs a _much_ bigger border when tiling horizontally.
        border = g.choose(self.splitVerticalFlag,2+border,6+border)
        self.body.bodyCtrl.configure(bd=border) # 2007/10/25

        # The log pane needs a slightly bigger border when tiling vertically.
        border = g.choose(self.splitVerticalFlag,4,2) 
        self.log.configureBorder(border)
    #@+node:ekr.20081121110412.212: *5* resizePanesToRatio (tkFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        # g.trace(ratio,ratio2,g.callers())

        self.divideLeoSplitter(self.splitVerticalFlag,ratio)
        self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@+node:ekr.20081121110412.213: *4* Event handlers (tkFrame)
    #@+node:ekr.20081121110412.214: *5* frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@+node:ekr.20081121110412.215: *5* frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        self.controlKeyIsDown = False
    #@+node:ekr.20081121110412.216: *5* OnActivateBody (tkFrame)
    def OnActivateBody (self,event=None):

        try:
            frame = self ; c = frame.c
            c.setLog()
            w = c.get_focus()
            if w != c.frame.body.bodyCtrl:
                frame.tree.OnDeactivate()
            c.bodyWantsFocus()
        except:
            g.es_event_exception("activate body")

        return 'break'
    #@+node:ekr.20081121110412.217: *5* OnActivateLeoEvent, OnDeactivateLeoEvent
    def OnActivateLeoEvent(self,event=None):

        '''Handle a click anywhere in the Leo window.'''

        self.c.setLog()

    def OnDeactivateLeoEvent(self,event=None):

        pass # This causes problems on the Mac.
    #@+node:ekr.20081121110412.218: *5* OnActivateTree
    def OnActivateTree (self,event=None):

        try:
            frame = self ; c = frame.c
            c.setLog()

            if 0: # Do NOT do this here!
                # OnActivateTree can get called when the tree gets DE-activated!!
                c.bodyWantsFocus()

        except:
            g.es_event_exception("activate tree")
    #@+node:ekr.20081121110412.219: *5* OnBodyClick, OnBodyRClick (Events)
    def OnBodyClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
                self.OnActivateBody(event=event)
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
            g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
            g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")
    #@+node:ekr.20081121110412.220: *5* OnBodyDoubleClick (Events)
    def OnBodyDoubleClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if event and not g.doHook("bodydclick1",c=c,p=p,v=p,event=event):
                c.editCommands.extendToWord(event) # Handles unicode properly.
                c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
            g.doHook("bodydclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodydclick")

        return "break" # Restore this to handle proper double-click logic.
    #@+node:ekr.20081121110412.221: *5* OnMouseWheel (Tomaz Ficko)
    # Contributed by Tomaz Ficko.  This works on some systems.
    # On XP it causes a crash in tcl83.dll.  Clearly a Tk bug.

    def OnMouseWheel(self, event=None):

        try:
            if event.delta < 1:
                self.canvas.yview(Tk.SCROLL, 1, Tk.UNITS)
            else:
                self.canvas.yview(Tk.SCROLL, -1, Tk.UNITS)
        except:
            g.es_event_exception("scroll wheel")

        return "break"
    #@+node:ekr.20081121110412.222: *4* Gui-dependent commands
    #@+node:ekr.20081121110412.223: *5* Minibuffer commands... (tkFrame)

    #@+node:ekr.20081121110412.224: *6* contractPane
    def contractPane (self,event=None):

        '''Contract the selected pane.'''

        f = self ; c = f.c
        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.contractBodyPane()
        elif wname.startswith('log'):
            f.contractLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.contractOutlinePane()
    #@+node:ekr.20081121110412.225: *6* expandPane
    def expandPane (self,event=None):

        '''Expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.expandBodyPane()
        elif wname.startswith('log'):
            f.expandLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.expandOutlinePane()
    #@+node:ekr.20081121110412.226: *6* fullyExpandPane
    def fullyExpandPane (self,event=None):

        '''Fully expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.fullyExpandBodyPane()
        elif wname.startswith('log'):
            f.fullyExpandLogPane()
        else:
            for z in ('head','canvas','tree'):
                f.fullyExpandOutlinePane()
                break
    #@+node:ekr.20081121110412.227: *6* hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus() or g.app.gui.get_focus(c)
        wname = c.widget_name(w)

        g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.hideBodyPane()
            c.treeWantsFocus()
        elif wname.startswith('log'):
            f.hideLogPane()
            c.bodyWantsFocus()
        else:
            for z in ('head','canvas','tree'):
                f.hideOutlinePane()
                c.bodyWantsFocus()
                break
    #@+node:ekr.20081121110412.228: *6* expand/contract/hide...Pane
    #@+at The first arg to divideLeoSplitter means the following:
    # 
    #     f.splitVerticalFlag: use the primary   (tree/body) ratio.
    # not f.splitVerticalFlag: use the secondary (tree/log) ratio.
    #@@c

    def contractBodyPane (self,event=None):
        '''Contract the body pane.'''
        f = self ; r = min(1.0,f.ratio+0.1)
        f.divideLeoSplitter(f.splitVerticalFlag,r)

    def contractLogPane (self,event=None):
        '''Contract the log pane.'''
        f = self ; r = min(1.0,f.secondary_ratio+0.1) # 2010/02/23: was f.ratio
        f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def contractOutlinePane (self,event=None):
        '''Contract the outline pane.'''
        f = self ; r = max(0.0,f.ratio-0.1)
        f.divideLeoSplitter(f.splitVerticalFlag,r)

    def expandBodyPane (self,event=None):
        '''Expand the body pane.'''
        self.contractOutlinePane()

    def expandLogPane(self,event=None):
        '''Expand the log pane.'''
        f = self ; r = max(0.0,f.secondary_ratio-0.1) # 2010/02/23: was f.ratio
        f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def expandOutlinePane (self,event=None):
        '''Expand the outline pane.'''
        self.contractBodyPane()
    #@+node:ekr.20081121110412.229: *6* fullyExpand/hide...Pane
    def fullyExpandBodyPane (self,event=None):
        '''Fully expand the body pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)

    def fullyExpandLogPane (self,event=None):
        '''Fully expand the log pane.'''
        f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

    def fullyExpandOutlinePane (self,event=None):
        '''Fully expand the outline pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideBodyPane (self,event=None):
        '''Completely contract the body pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

    def hideLogPane (self,event=None):
        '''Completely contract the log pane.'''
        f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

    def hideOutlinePane (self,event=None):
        '''Completely contract the outline pane.'''
        f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)
    #@+node:ekr.20081121110412.230: *5* Window Menu...
    #@+node:ekr.20081121110412.231: *6* toggleActivePane (tkFrame)
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c

        if c.get_focus() == frame.body.bodyCtrl: # 2007/10/25
            c.treeWantsFocus()
        else:
            c.endEditing()
            c.bodyWantsFocus()
    #@+node:ekr.20081121110412.232: *6* cascade
    def cascade (self,event=None):

        '''Cascade all Leo windows.'''

        x,y,delta = 10,10,10
        for frame in g.app.windowList:
            top = frame.top

            # Compute w,h
            top.update_idletasks() # Required to get proper info.
            geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
            dim,junkx,junky = geom.split('+')
            w,h = dim.split('x')
            w,h = int(w),int(h)

            # Set new x,y and old w,h
            frame.setTopGeometry(w,h,x,y,adjustSize=False)

            # Compute the new offsets.
            x += 30 ; y += 30
            if x > 200:
                x = 10 + delta ; y = 40 + delta
                delta += 10
    #@+node:ekr.20081121110412.233: *6* equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.resizePanesToRatio(0.5,frame.secondary_ratio)
    #@+node:ekr.20081121110412.234: *6* hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self
        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@+node:ekr.20081121110412.235: *6* minimizeAll
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        self.minimize(g.app.pythonFrame)
        for frame in g.app.windowList:
            self.minimize(frame)
            self.minimize(frame.findPanel)

    def minimize(self,frame):

        if frame and frame.top.state() == "normal":
            frame.top.iconify()
    #@+node:ekr.20081121110412.236: *6* toggleSplitDirection (tkFrame)
    # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

    def toggleSplitDirection (self,event=None):

        '''Toggle the split direction in the present Leo window.'''

        # Switch directions.
        f = self

        # The key invariant: self.splitVerticalFlag
        # tells the alignment of the main splitter.
        f.splitVerticalFlag = not f.splitVerticalFlag
        f.toggleTkSplitDirection(f.splitVerticalFlag)
    #@+node:ekr.20081121110412.237: *7* toggleTkSplitDirection
    def toggleTkSplitDirection (self,verticalFlag):

        # Abbreviations.
        frame = self
        bar1 = self.bar1 ; bar2 = self.bar2
        split1Pane1,split1Pane2 = self.split1Pane1,self.split1Pane2
        split2Pane1,split2Pane2 = self.split2Pane1,self.split2Pane2
        # Reconfigure the bars.
        bar1.place_forget()
        bar2.place_forget()
        self.configureBar(bar1,verticalFlag)
        self.configureBar(bar2,not verticalFlag)
        # Make the initial placements again.
        self.placeSplitter(bar1,split1Pane1,split1Pane2,verticalFlag)
        self.placeSplitter(bar2,split2Pane1,split2Pane2,not verticalFlag)
        # Adjust the log and body panes to give more room around the bars.
        self.reconfigurePanes()
        # Redraw with an appropriate ratio.
        vflag,ratio,secondary_ratio = frame.initialRatios()
        self.resizePanesToRatio(ratio,secondary_ratio)
    #@+node:ekr.20081121110412.238: *6* resizeToScreen
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fill the entire screen.'''

        top = self.top

        w = top.winfo_screenwidth()
        h = top.winfo_screenheight()

        if sys.platform.startswith('win'):
            top.state('zoomed')
        elif sys.platform == 'darwin':
            # Must leave room to get at very small resizing area.
            geom = "%dx%d%+d%+d" % (w-20,h-55,10,25)
            top.geometry(geom)
        else:
            # Fill almost the entire screen.
            # Works on Windows. YMMV for other platforms.
            geom = "%dx%d%+d%+d" % (w-8,h-46,0,0)
            top.geometry(geom)
    #@+node:ekr.20081121110412.239: *5* Help Menu...
    #@+node:ekr.20081121110412.240: *6* leoHelp
    def leoHelp (self,event=None):

        '''Open Leo's offline tutorial.'''

        frame = self ; c = frame.c

        theFile = g.os_path_join(g.app.loadDir,"..","doc","sbooks.chm")

        if g.os_path_exists(theFile):
            os.startfile(theFile)
        else:
            answer = g.app.gui.runAskYesNoDialog(c,
                "Download Tutorial?",
                "Download tutorial (sbooks.chm) from SourceForge?")

            if answer == "yes":
                try:
                    if 0: # Download directly.  (showProgressBar needs a lot of work)
                        url = "http://umn.dl.sourceforge.net/sourceforge/leo/sbooks.chm"
                        import urllib
                        self.scale = None
                        urllib.urlretrieve(url,theFile,self.showProgressBar)
                        if self.scale:
                            self.scale.destroy()
                            self.scale = None
                    else:
                        url = "http://prdownloads.sourceforge.net/leo/sbooks.chm?download"
                        import webbrowser
                        os.chdir(g.app.loadDir)
                        webbrowser.open_new(url)
                except:
                    g.es("exception downloading","sbooks.chm")
                    g.es_exception()
    #@+node:ekr.20081121110412.241: *7* showProgressBar
    def showProgressBar (self,count,size,total):

        # g.trace("count,size,total:",count,size,total)
        if self.scale == None:
            #@+<< create the scale widget >>
            #@+node:ekr.20081121110412.242: *8* << create the scale widget >>
            top = Tk.Toplevel()
            top.title("Download progress")
            self.scale = scale = Tk.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
            scale.pack()
            top.lift()
            #@-<< create the scale widget >>
        self.scale.set(count*size)
        self.scale.update_idletasks()
    #@+node:ekr.20081121110412.243: *4* Delayed Focus (tkFrame)
    #@+at New in 4.3. The proper way to change focus is to call c.frame.xWantsFocus.
    # 
    # Important: This code never calls select, so there can be no race condition here
    # that alters text improperly.
    #@+node:ekr.20081121110412.244: *4* Tk bindings... (tkFrame)
    def bringToFront (self):
        # g.trace(g.callers())
        self.top.deiconify()
        self.top.lift()

    def getFocus(self):
        """Returns the widget that has focus, or body if None."""
        try:
            # This method is unreliable while focus is changing.
            # The call to update_idletasks may help.  Or not.
            self.top.update_idletasks()
            f = self.top.focus_displayof()
        except Exception:
            f = None
        if f:
            return f
        else:
            return self.body.bodyCtrl # 2007/10/25

    def getTitle (self):
        return self.top.title()

    def setTitle (self,title):
        return self.top.title(title)

    def get_window_info(self):
        return g.app.gui.get_window_info(self.top)

    def iconify(self):
        self.top.iconify()

    def deiconify (self):
        self.top.deiconify()

    def lift (self):
        self.top.lift()

    def update (self):
        self.top.update()
    #@-others
#@+node:ekr.20081121110412.245: *3* class leoTkinterLog
class leoTkinterLog (leoFrame.leoLog):

    """A class that represents the log pane of a Tkinter window."""

    #@+others
    #@+node:ekr.20081121110412.246: *4* tkLog Birth
    #@+node:ekr.20081121110412.247: *5* tkLog.__init__
    def __init__ (self,frame,parentFrame):

        # g.trace("leoTkinterLog")

        # Call the base class constructor and calls createControl.
        leoFrame.leoLog.__init__(self,frame,parentFrame)

        self.c = c = frame.c # Also set in the base constructor, but we need it here.

        self.colorTags = []
            # The list of color names used as tags in present tab.
            # This gest switched by selectTab.

        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),"word","none")

        # New in 4.4a2: The log pane is a Pmw.Notebook...

        self.nb = None      # The Pmw.Notebook that holds all the tabs.
        self.colorTagsDict = {} # Keys are page names.  Values are saved colorTags lists.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.

        self.logCtrl = self.createControl(parentFrame)
        self.setFontFromConfig()
        self.setColorFromConfig()



    #@+node:ekr.20081121110412.248: *5* tkLog.createControl
    def createControl (self,parentFrame):

        c = self.c

        self.nb = Pmw.NoteBook(parentFrame,
            borderwidth = 1, pagemargin = 0,
            raisecommand = self.raiseTab,
            lowercommand = self.lowerTab,
            arrownavigation = 0,
        )

        menu = self.makeTabMenu(tabName=None)

        def hullMenuCallback(event):
            return self.onRightClick(event,menu)

        c.bind(self.nb,'<Button-3>',hullMenuCallback)

        self.nb.pack(fill='both',expand=1)
        self.selectTab('Log') # Create and activate the default tabs.

        return self.logCtrl
    #@+node:ekr.20081121110412.249: *5* tkLog.finishCreate
    def finishCreate (self):

        # g.trace('tkLog')

        c = self.c ; log = self

        c.searchCommands.openFindTab(show=False)
        c.spellCommands.openSpellTab()
        log.selectTab('Log')
    #@+node:ekr.20081121110412.250: *5* tkLog.createCanvasWidget
    def createCanvasWidget (self,parentFrame):

        self.logNumber += 1

        w = Tk.Canvas(parentFrame)

        logBar = Tk.Scrollbar(parentFrame,name="logBar")
        w['yscrollcommand'] = logBar.set
        logBar['command'] = w.yview
        logBar.pack(side="right", fill="y")

        logXBar = Tk.Scrollbar(parentFrame,name='logXBar',orient="horizontal") 
        w['xscrollcommand'] = logXBar.set 
        logXBar['command'] = w.xview 
        logXBar.pack(side="bottom", fill="x")

        w.pack(expand=1, fill="both")

        # Set the background color.
        configName = 'log_canvas_pane_tab_background_color'
        bg = self.c.config.getColor(configName) or 'MistyRose1'
        try: w.configure(bg=bg)
        except Exception: pass # Could be a user error.

        return w
    #@+node:ekr.20081121110412.251: *5* tkLog.createTextWidget
    def createTextWidget (self,parentFrame):

        self.logNumber += 1
        log = g.app.gui.plainTextWidget(
            parentFrame,name="log-%d" % self.logNumber,
            setgrid=0,wrap=self.wrap,bd=2,bg="white",relief="flat")

        logBar = Tk.Scrollbar(parentFrame,name="logBar")

        log['yscrollcommand'] = logBar.set
        logBar['command'] = log.yview

        logBar.pack(side="right", fill="y")
        # rr 8/14/02 added horizontal elevator 
        if self.wrap == "none": 
            logXBar = Tk.Scrollbar( 
                parentFrame,name='logXBar',orient="horizontal") 
            log['xscrollcommand'] = logXBar.set 
            logXBar['command'] = log.xview 
            logXBar.pack(side="bottom", fill="x")
        log.pack(expand=1, fill="both")

        return log
    #@+node:ekr.20081121110412.252: *5* tkLog.makeTabMenu
    def makeTabMenu (self,tabName=None,allowRename=True):

        '''Create a tab popup menu.'''

        # g.trace(tabName,g.callers())

        c = self.c
        hull = self.nb.component('hull') # A Tk.Canvas.

        menu = Tk.Menu(hull,tearoff=0)
        c.add_command(menu,label='New Tab',command=self.newTabFromMenu)
        c.add_command(menu,label='New CanvasTab',command=self.newCanvasTabFromMenu)

        if tabName:
            # Important: tabName is the name when the tab is created.
            # It is not affected by renaming, so we don't have to keep
            # track of the correspondence between this name and what is in the label.
            def deleteTabCallback():
                return self.deleteTab(tabName)

            label = g.choose(
                tabName in ('Find','Spell'),'Hide This Tab','Delete This Tab')
            c.add_command(menu,label=label,command=deleteTabCallback)

            def renameTabCallback():
                return self.renameTabFromMenu(tabName)

            if allowRename:
                c.add_command(menu,label='Rename This Tab',command=renameTabCallback)

        return menu
    #@+node:ekr.20081121110412.253: *4* Config & get/saveState
    #@+node:ekr.20081121110412.254: *5* tkLog.configureBorder & configureFont
    def configureBorder(self,border):

        self.logCtrl.configure(bd=border)

    def configureFont(self,font):

        self.logCtrl.configure(font=font)
    #@+node:ekr.20081121110412.255: *5* tkLog.getFontConfig
    def getFontConfig (self):

        font = self.logCtrl.cget("font")
        # g.trace(font)
        return font
    #@+node:ekr.20081121110412.256: *5* tkLog.restoreAllState
    def restoreAllState (self,d):

        '''Restore the log from a dict created by saveAllState.'''

        logCtrl = self.logCtrl

        # Restore the text.
        text = d.get('text')
        logCtrl.insert('end',text)

        # Restore all colors.
        colors = d.get('colors')
        for color in colors:
            if color not in self.colorTags:
                self.colorTags.append(color)
                logCtrl.tag_config(color,foreground=color)
            items = list(colors.get(color))
            while items:
                start,stop = items[0],items[1]
                items = items[2:]
                logCtrl.tag_add(color,start,stop)
    #@+node:ekr.20081121110412.257: *5* tkLog.saveAllState
    def saveAllState (self):

        '''Return a dict containing all data needed to recreate the log in another widget.'''

        logCtrl = self.logCtrl ; colors = {}

        # Save the text
        text = logCtrl.getAllText()

        # Save color tags.
        tag_names = logCtrl.tag_names()
        for tag in tag_names:
            if tag in self.colorTags:
                colors[tag] = logCtrl.tag_ranges(tag)

        d = {'text':text,'colors': colors}
        # g.trace('\n',g.dictToString(d))
        return d
    #@+node:ekr.20081121110412.258: *5* tkLog.setColorFromConfig
    def setColorFromConfig (self):

        c = self.c

        bg = c.config.getColor("log_pane_background_color") or 'white'

        try:
            self.logCtrl.configure(bg=bg)
        except:
            g.es("exception setting log pane background color")
            g.es_exception()
    #@+node:ekr.20081121110412.259: *5* tkLog.setFontFromConfig
    def SetWidgetFontFromConfig (self,logCtrl=None):

        c = self.c

        if not logCtrl: logCtrl = self.logCtrl

        font = c.config.getFontFromParams(
            "log_text_font_family", "log_text_font_size",
            "log_text_font_slant", "log_text_font_weight",
            c.config.defaultLogFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        logCtrl.configure(font=font)

        # g.trace("LOG",logCtrl.cget("font"),font.cget("family"),font.cget("weight"))

        bg = c.config.getColor("log_text_background_color")
        if bg:
            try: logCtrl.configure(bg=bg)
            except: pass

        fg = c.config.getColor("log_text_foreground_color")
        if fg:
            try: logCtrl.configure(fg=fg)
            except: pass

    setFontFromConfig = SetWidgetFontFromConfig # Renaming supresses a pychecker warning.
    #@+node:ekr.20081121110412.260: *4* Focus & update (tkLog)
    #@+node:ekr.20081121110412.261: *5* tkLog.onActivateLog
    def onActivateLog (self,event=None):

        try:
            self.c.setLog()
            self.frame.tree.OnDeactivate()
            self.c.logWantsFocus()
        except:
            g.es_event_exception("activate log")
    #@+node:ekr.20081121110412.262: *5* tkLog.hasFocus
    def hasFocus (self):

        return self.c.get_focus() == self.logCtrl
    #@+node:ekr.20081121110412.263: *5* forceLogUpdate
    def forceLogUpdate (self,s):

        if sys.platform == "darwin": # Does not work on MacOS X.
            try:
                g.pr(s,newline=False) # Don't add a newline.
            except UnicodeError:
                # g.app may not be inited during scripts!
                g.pr(g.toEncodedString(s))
        else:
            self.logCtrl.update_idletasks()
    #@+node:ekr.20081121110412.264: *4* put & putnl (tkLog)
    #@+at Printing uses self.logCtrl, so this code need not concern itself
    # with which tab is active.
    # 
    # Also, selectTab switches the contents of colorTags, so that is not concern.
    # It may be that Pmw will allow us to dispense with the colorTags logic...
    #@+node:ekr.20081121110412.265: *5* put
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        c = self.c

        # g.pr('tkLog.put',s)
        # g.pr('tkLog.put',len(s),g.callers())

        if g.app.quitting or not c or not c.exists:
            return

        if tabName:
            self.selectTab(tabName)

        # Note: this must be done after the call to selectTab.
        w = self.logCtrl
        if w:
            #@+<< put s to log control >>
            #@+node:ekr.20081121110412.266: *6* << put s to log control >>
            if color:
                if color not in self.colorTags:
                    self.colorTags.append(color)
                    w.tag_config(color,foreground=color)
                w.insert("end",s)
                w.tag_add(color,"end-%dc" % (len(s)+1),"end-1c")
                w.tag_add("black","end")
            else:
                w.insert("end",s)

            w.see('end')
            self.forceLogUpdate(s)
            #@-<< put s to log control >>
            self.logCtrl.update_idletasks()
        else:
            #@+<< put s to logWaiting and print s >>
            #@+node:ekr.20081121110412.267: *6* << put s to logWaiting and print s >>
            g.app.logWaiting.append((s,color),)

            g.pr("Null tkinter log")

            if g.isUnicode(s):
                s = g.toEncodedString(s,"ascii")

            g.pr(s)
            #@-<< put s to logWaiting and print s >>
    #@+node:ekr.20081121110412.268: *5* putnl
    def putnl (self,tabName='Log'):

        if g.app.quitting:
            return

        # g.pr('tkLog.putnl' # ,g.callers())

        if tabName:
            self.selectTab(tabName)

        w = self.logCtrl

        if w:
            w.insert("end",'\n')
            w.see('end')
            self.forceLogUpdate('\n')
        else:
            # Put a newline to logWaiting and print newline
            g.app.logWaiting.append(('\n',"black"),)
            g.pr("Null tkinter log")
    #@+node:ekr.20081121110412.269: *4* Tab (TkLog)
    #@+node:ekr.20081121110412.270: *5* clearTab
    def clearTab (self,tabName,wrap='none'):

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        if w: w.delete(0,'end')
    #@+node:ekr.20081121110412.271: *5* createCanvas
    def createCanvas (self,tabName=None):

        c = self.c ; k = c.k

        if tabName is None:
            self.logNumber += 1
            tabName = 'Canvas %d' % self.logNumber

        tabFrame = self.nb.add(tabName)
        menu = self.makeTabMenu(tabName,allowRename=False)

        w = self.createCanvasWidget(tabFrame)

        self.canvasDict [tabName ] = w
        self.textDict [tabName] = None
        self.frameDict [tabName] = tabFrame

        self.setCanvasTabBindings(tabName,menu)

        return w
    #@+node:ekr.20081121110412.272: *5* createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        # g.trace(tabName,wrap)

        c = self.c ; k = c.k
        tabFrame = self.nb.add(tabName)
        self.menu = self.makeTabMenu(tabName)
        if createText:
            #@+<< Create the tab's text widget >>
            #@+node:ekr.20081121110412.273: *6* << Create the tab's text widget >>
            w = self.createTextWidget(tabFrame)

            # Set the background color.
            configName = 'log_pane_%s_tab_background_color' % tabName
            bg = c.config.getColor(configName) or 'MistyRose1'

            if wrap not in ('none','char','word'): wrap = 'none'
            try: w.configure(bg=bg,wrap=wrap)
            except Exception: pass # Could be a user error.

            self.SetWidgetFontFromConfig(logCtrl=w)

            self.canvasDict [tabName ] = None
            self.frameDict [tabName] = tabFrame
            self.textDict [tabName] = w

            # Switch to a new colorTags list.
            if self.tabName:
                self.colorTagsDict [self.tabName] = self.colorTags [:]

            self.colorTags = ['black']
            self.colorTagsDict [tabName] = self.colorTags
            #@-<< Create the tab's text widget >>
        else:
            self.canvasDict [tabName] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabFrame

        if tabName != 'Log':
            # c.k doesn't exist when the log pane is created.
            # k.makeAllBindings will call setTabBindings('Log')
            self.setTabBindings(tabName)
    #@+node:ekr.20081121110412.274: *5* cycleTabFocus
    def cycleTabFocus (self,event=None,stop_w = None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        c = self.c ; d = self.frameDict # Keys are page names. Values are Tk.Frames.
        w = d.get(self.tabName)
        # g.trace(self.tabName,w)
        values = d.values()
        if self.numberOfVisibleTabs() > 1:
            i = i2 = values.index(w) + 1
            if i == len(values): i = 0
            tabName = d.keys()[i]
            self.selectTab(tabName)
            return 
    #@+node:ekr.20081121110412.275: *5* deleteTab
    def deleteTab (self,tabName,force=False):

        if tabName == 'Log':
            pass

        elif tabName in ('Find','Spell') and not force:
            self.selectTab('Log')

        elif tabName in self.nb.pagenames():
            # g.trace(tabName,force)
            self.nb.delete(tabName)
            self.colorTagsDict [tabName] = []
            self.canvasDict [tabName ] = None
            self.textDict [tabName] = None
            self.frameDict [tabName] = None
            self.tabName = None
            self.selectTab('Log')

        # New in Leo 4.4b1.
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@+node:ekr.20081121110412.276: *5* hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@+node:ekr.20081121110412.277: *5* getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@+node:ekr.20081121110412.278: *5* lower/raiseTab
    def lowerTab (self,tabName):

        if tabName:
            b = self.nb.tab(tabName) # b is a Tk.Button.
            b.config(bg='grey80')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        if tabName:
            b = self.nb.tab(tabName) # b is a Tk.Button.
            b.config(bg='LightSteelBlue1')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@+node:ekr.20081121110412.279: *5* numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@+node:ekr.20081121110412.280: *5* renameTab
    def renameTab (self,oldName,newName):

        # g.trace('newName',newName)

        label = self.nb.tab(oldName)
        label.configure(text=newName)
    #@+node:ekr.20081121110412.281: *5* selectTab
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c

        tabFrame = self.frameDict.get(tabName)
        logCtrl = self.textDict.get(tabName)

        if tabFrame and logCtrl:
            # Switch to a new colorTags list.
            newColorTags = self.colorTagsDict.get(tabName)
            self.colorTagsDict [self.tabName] = self.colorTags [:]
            self.colorTags = newColorTags
        elif not tabFrame:
            self.createTab(tabName,createText=createText,wrap=wrap)

        self.nb.selectpage(tabName)
        # Update the status vars.
        self.tabName = tabName
        w = self.textDict.get(tabName)
        if w: self.logCtrl = w
        self.tabFrame = self.frameDict.get(tabName)

        if 0: # Absolutely do not do this here!  It is a cause of the 'sticky focus' problem.
            c.widgetWantsFocusNow(self.logCtrl)
        return tabFrame
    #@+node:ekr.20081121110412.282: *5* setTabBindings
    def setTabBindings (self,tabName):

        c = self.c ; k = c.k
        tab = self.nb.tab(tabName)
        w = self.textDict.get(tabName) or self.frameDict.get(tabName)

        def logTextRightClickCallback(event):
            return c.k.masterClick3Handler(event,self.onLogTextRightClick)


        # Send all event in the text area to the master handlers.
        for kind,handler in (
            ('<Key>',       k.masterKeyHandler),
            ('<Button-1>',  k.masterClickHandler),
            ('<Button-3>',  logTextRightClickCallback),
        ):
            c.bind(w,kind,handler)

        # Clicks in the tab area are harmless: use the old code.
        def tabMenuRightClickCallback(event,menu=self.menu):
            return self.onRightClick(event,menu)

        def tabMenuClickCallback(event,tabName=tabName):
            return self.onClick(event,tabName)

        c.bind(tab,'<Button-1>',tabMenuClickCallback)
        c.bind(tab,'<Button-3>',tabMenuRightClickCallback)

        k.completeAllBindingsForWidget(w)
    #@+node:ekr.20081121110412.283: *5* onLogTextRightClick
    def onLogTextRightClick(self, event):

        g.doHook('rclick-popup', c=self.c, event=event, context_menu='log')
    #@+node:ekr.20081121110412.284: *5* setCanvasTabBindings
    def setCanvasTabBindings (self,tabName,menu):

        c = self.c ; tab = self.nb.tab(tabName)

        def tabMenuRightClickCallback(event,menu=menu):
            return self.onRightClick(event,menu)

        def tabMenuClickCallback(event,tabName=tabName):
            return self.onClick(event,tabName)

        c.bind(tab,'<Button-1>',tabMenuClickCallback)
        c.bind(tab,'<Button-3>',tabMenuRightClickCallback)

    #@+node:ekr.20081121110412.285: *5* Tab menu callbacks & helpers
    #@+node:ekr.20081121110412.286: *6* onRightClick & onClick
    def onRightClick (self,event,menu):

        c = self.c
        menu.post(event.x_root,event.y_root)


    def onClick (self,event,tabName):

        self.selectTab(tabName)
    #@+node:ekr.20081121110412.287: *6* newTabFromMenu & newCanvasTabFromMenu
    def newTabFromMenu (self,tabName='Log'):

        self.selectTab(tabName)

        # This is called by getTabName.
        def selectTabCallback (newName):
            return self.selectTab(newName)

        self.getTabName(selectTabCallback)

    def newCanvasTabFromMenu (self):

        self.createCanvas()
    #@+node:ekr.20081121110412.288: *6* renameTabFromMenu
    def renameTabFromMenu (self,tabName):

        if tabName in ('Log','Completions'):
            g.es('can not rename',tabName,'tab',color='blue')
        else:
            def renameTabCallback (newName):
                return self.renameTab(tabName,newName)

            self.getTabName(renameTabCallback)
    #@+node:ekr.20081121110412.289: *6* getTabName
    def getTabName (self,exitCallback):

        canvas = self.nb.component('hull')

        # Overlay what is there!
        c = self.c
        f = Tk.Frame(canvas)
        f.pack(side='top',fill='both',expand=1)

        row1 = Tk.Frame(f)
        row1.pack(side='top',expand=0,fill='x',pady=10)
        row2 = Tk.Frame(f)
        row2.pack(side='top',expand=0,fill='x')

        Tk.Label(row1,text='Tab name').pack(side='left')

        e = Tk.Entry(row1,background='white')
        e.pack(side='left')

        def getNameCallback (event=None):
            s = e.get().strip()
            f.pack_forget()
            if s: exitCallback(s)

        def closeTabNameCallback (event=None):
            f.pack_forget()

        b = Tk.Button(row2,text='Ok',width=6,command=getNameCallback)
        b.pack(side='left',padx=10)

        b = Tk.Button(row2,text='Cancel',width=6,command=closeTabNameCallback)
        b.pack(side='left')

        g.app.gui.set_focus(c,e)
        c.bind(e,'<Return>',getNameCallback)
    #@+node:ekr.20081121110412.290: *4* tkLog color tab stuff
    def createColorPicker (self,tabName):

        log = self

        #@+<< define colors >>
        #@+node:ekr.20081121110412.291: *5* << define colors >>
        colors = (
            "gray60", "gray70", "gray80", "gray85", "gray90", "gray95",
            "snow1", "snow2", "snow3", "snow4", "seashell1", "seashell2",
            "seashell3", "seashell4", "AntiqueWhite1", "AntiqueWhite2", "AntiqueWhite3",
            "AntiqueWhite4", "bisque1", "bisque2", "bisque3", "bisque4", "PeachPuff1",
            "PeachPuff2", "PeachPuff3", "PeachPuff4", "NavajoWhite1", "NavajoWhite2",
            "NavajoWhite3", "NavajoWhite4", "LemonChiffon1", "LemonChiffon2",
            "LemonChiffon3", "LemonChiffon4", "cornsilk1", "cornsilk2", "cornsilk3",
            "cornsilk4", "ivory1", "ivory2", "ivory3", "ivory4", "honeydew1", "honeydew2",
            "honeydew3", "honeydew4", "LavenderBlush1", "LavenderBlush2",
            "LavenderBlush3", "LavenderBlush4", "MistyRose1", "MistyRose2",
            "MistyRose3", "MistyRose4", "azure1", "azure2", "azure3", "azure4",
            "SlateBlue1", "SlateBlue2", "SlateBlue3", "SlateBlue4", "RoyalBlue1",
            "RoyalBlue2", "RoyalBlue3", "RoyalBlue4", "blue1", "blue2", "blue3", "blue4",
            "DodgerBlue1", "DodgerBlue2", "DodgerBlue3", "DodgerBlue4", "SteelBlue1",
            "SteelBlue2", "SteelBlue3", "SteelBlue4", "DeepSkyBlue1", "DeepSkyBlue2",
            "DeepSkyBlue3", "DeepSkyBlue4", "SkyBlue1", "SkyBlue2", "SkyBlue3",
            "SkyBlue4", "LightSkyBlue1", "LightSkyBlue2", "LightSkyBlue3",
            "LightSkyBlue4", "SlateGray1", "SlateGray2", "SlateGray3", "SlateGray4",
            "LightSteelBlue1", "LightSteelBlue2", "LightSteelBlue3",
            "LightSteelBlue4", "LightBlue1", "LightBlue2", "LightBlue3",
            "LightBlue4", "LightCyan1", "LightCyan2", "LightCyan3", "LightCyan4",
            "PaleTurquoise1", "PaleTurquoise2", "PaleTurquoise3", "PaleTurquoise4",
            "CadetBlue1", "CadetBlue2", "CadetBlue3", "CadetBlue4", "turquoise1",
            "turquoise2", "turquoise3", "turquoise4", "cyan1", "cyan2", "cyan3", "cyan4",
            "DarkSlateGray1", "DarkSlateGray2", "DarkSlateGray3",
            "DarkSlateGray4", "aquamarine1", "aquamarine2", "aquamarine3",
            "aquamarine4", "DarkSeaGreen1", "DarkSeaGreen2", "DarkSeaGreen3",
            "DarkSeaGreen4", "SeaGreen1", "SeaGreen2", "SeaGreen3", "SeaGreen4",
            "PaleGreen1", "PaleGreen2", "PaleGreen3", "PaleGreen4", "SpringGreen1",
            "SpringGreen2", "SpringGreen3", "SpringGreen4", "green1", "green2",
            "green3", "green4", "chartreuse1", "chartreuse2", "chartreuse3",
            "chartreuse4", "OliveDrab1", "OliveDrab2", "OliveDrab3", "OliveDrab4",
            "DarkOliveGreen1", "DarkOliveGreen2", "DarkOliveGreen3",
            "DarkOliveGreen4", "khaki1", "khaki2", "khaki3", "khaki4",
            "LightGoldenrod1", "LightGoldenrod2", "LightGoldenrod3",
            "LightGoldenrod4", "LightYellow1", "LightYellow2", "LightYellow3",
            "LightYellow4", "yellow1", "yellow2", "yellow3", "yellow4", "gold1", "gold2",
            "gold3", "gold4", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4",
            "DarkGoldenrod1", "DarkGoldenrod2", "DarkGoldenrod3", "DarkGoldenrod4",
            "RosyBrown1", "RosyBrown2", "RosyBrown3", "RosyBrown4", "IndianRed1",
            "IndianRed2", "IndianRed3", "IndianRed4", "sienna1", "sienna2", "sienna3",
            "sienna4", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "wheat1",
            "wheat2", "wheat3", "wheat4", "tan1", "tan2", "tan3", "tan4", "chocolate1",
            "chocolate2", "chocolate3", "chocolate4", "firebrick1", "firebrick2",
            "firebrick3", "firebrick4", "brown1", "brown2", "brown3", "brown4", "salmon1",
            "salmon2", "salmon3", "salmon4", "LightSalmon1", "LightSalmon2",
            "LightSalmon3", "LightSalmon4", "orange1", "orange2", "orange3", "orange4",
            "DarkOrange1", "DarkOrange2", "DarkOrange3", "DarkOrange4", "coral1",
            "coral2", "coral3", "coral4", "tomato1", "tomato2", "tomato3", "tomato4",
            "OrangeRed1", "OrangeRed2", "OrangeRed3", "OrangeRed4", "red1", "red2", "red3",
            "red4", "DeepPink1", "DeepPink2", "DeepPink3", "DeepPink4", "HotPink1",
            "HotPink2", "HotPink3", "HotPink4", "pink1", "pink2", "pink3", "pink4",
            "LightPink1", "LightPink2", "LightPink3", "LightPink4", "PaleVioletRed1",
            "PaleVioletRed2", "PaleVioletRed3", "PaleVioletRed4", "maroon1",
            "maroon2", "maroon3", "maroon4", "VioletRed1", "VioletRed2", "VioletRed3",
            "VioletRed4", "magenta1", "magenta2", "magenta3", "magenta4", "orchid1",
            "orchid2", "orchid3", "orchid4", "plum1", "plum2", "plum3", "plum4",
            "MediumOrchid1", "MediumOrchid2", "MediumOrchid3", "MediumOrchid4",
            "DarkOrchid1", "DarkOrchid2", "DarkOrchid3", "DarkOrchid4", "purple1",
            "purple2", "purple3", "purple4", "MediumPurple1", "MediumPurple2",
            "MediumPurple3", "MediumPurple4", "thistle1", "thistle2", "thistle3",
            "thistle4" )
        #@-<< define colors >>

        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        colors = list(colors)
        bg = parent.cget('background')

        outer = Tk.Frame(parent,background=bg)
        outer.pack(side='top',fill='both',expand=1,pady=10)

        f = Tk.Frame(outer)
        f.pack(side='top',expand=0,fill='x')
        f1 = Tk.Frame(f) ; f1.pack(side='top',expand=0,fill='x')
        f2 = Tk.Frame(f) ; f2.pack(side='top',expand=1,fill='x')
        f3 = Tk.Frame(f) ; f3.pack(side='top',expand=1,fill='x')

        label = g.app.gui.plainTextWidget(f1,height=1,width=20)
        label.insert('1.0','Color name or value...')
        label.pack(side='left',pady=6)

        #@+<< create optionMenu and callback >>
        #@+node:ekr.20081121110412.292: *5* << create optionMenu and callback >>
        colorBox = Pmw.ComboBox(f2,scrolledlist_items=colors)
        colorBox.pack(side='left',pady=4)

        def colorCallback (newName): 
            label.delete('1.0','end')
            label.insert('1.0',newName)
            try:
                for theFrame in (parent,outer,f,f1,f2,f3):
                    theFrame.configure(background=newName)
            except: pass # Ignore invalid names.

        colorBox.configure(selectioncommand=colorCallback)
        #@-<< create optionMenu and callback >>
        #@+<< create picker button and callback >>
        #@+node:ekr.20081121110412.293: *5* << create picker button and callback >>
        def pickerCallback ():
            rgb,val = tkColorChooser.askcolor(parent=parent,initialcolor=f.cget('background'))
            if rgb or val:
                # label.configure(text=val)
                label.delete('1.0','end')
                label.insert('1.0',val)
                for theFrame in (parent,outer,f,f1,f2,f3):
                    theFrame.configure(background=val)

        b = Tk.Button(f3,text="Color Picker...",
            command=pickerCallback,background=bg)
        b.pack(side='left',pady=4)
        #@-<< create picker button and callback >>
    #@+node:ekr.20081121110412.294: *4* tkLog font tab stuff
    #@+node:ekr.20081121110412.295: *5* createFontPicker
    def createFontPicker (self,tabName):

        log = self ; c = self.c
        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        bg = parent.cget('background')
        font = self.getFont()
        #@+<< create the frames >>
        #@+node:ekr.20081121110412.296: *6* << create the frames >>
        f = Tk.Frame(parent,background=bg) ; f.pack (side='top',expand=0,fill='both')
        f1 = Tk.Frame(f,background=bg)     ; f1.pack(side='top',expand=1,fill='x')
        f2 = Tk.Frame(f,background=bg)     ; f2.pack(side='top',expand=1,fill='x')
        f3 = Tk.Frame(f,background=bg)     ; f3.pack(side='top',expand=1,fill='x')
        f4 = Tk.Frame(f,background=bg)     ; f4.pack(side='top',expand=1,fill='x')
        #@-<< create the frames >>
        #@+<< create the family combo box >>
        #@+node:ekr.20081121110412.297: *6* << create the family combo box >>
        names = tkFont.families()
        names = list(names)
        names.sort()
        names.insert(0,'<None>')

        self.familyBox = familyBox = Pmw.ComboBox(f1,
            labelpos="we",label_text='Family:',label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=names)

        familyBox.selectitem(0)
        familyBox.pack(side="left",padx=2,pady=2)
        #@-<< create the family combo box >>
        #@+<< create the size entry >>
        #@+node:ekr.20081121110412.298: *6* << create the size entry >>
        Tk.Label(f2,text="Size:",width=10,background=bg).pack(side="left")

        sizeEntry = Tk.Entry(f2,width=4)
        sizeEntry.insert(0,'12')
        sizeEntry.pack(side="left",padx=2,pady=2)
        #@-<< create the size entry >>
        #@+<< create the weight combo box >>
        #@+node:ekr.20081121110412.299: *6* << create the weight combo box >>
        weightBox = Pmw.ComboBox(f3,
            labelpos="we",label_text="Weight:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['normal','bold'])

        weightBox.selectitem(0)
        weightBox.pack(side="left",padx=2,pady=2)
        #@-<< create the weight combo box >>
        #@+<< create the slant combo box >>
        #@+node:ekr.20081121110412.300: *6* << create the slant combo box>>
        slantBox = Pmw.ComboBox(f4,
            labelpos="we",label_text="Slant:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['roman','italic'])

        slantBox.selectitem(0)
        slantBox.pack(side="left",padx=2,pady=2)
        #@-<< create the slant combo box >>
        #@+<< create the sample text widget >>
        #@+node:ekr.20081121110412.301: *6* << create the sample text widget >>
        self.sampleWidget = sample = g.app.gui.plainTextWidget(f,height=20,width=80,font=font)
        sample.pack(side='left')

        s = 'The quick brown fox\njumped over the lazy dog.\n0123456789'
        sample.insert(0,s)
        #@-<< create the sample text widget >>
        #@+<< create and bind the callbacks >>
        #@+node:ekr.20081121110412.302: *6* << create and bind the callbacks >>
        def fontCallback(event=None):
            self.setFont(familyBox,sizeEntry,slantBox,weightBox,sample)

        for w in (familyBox,slantBox,weightBox):
            w.configure(selectioncommand=fontCallback)

        c.bind(sizeEntry,'<Return>',fontCallback)
        #@-<< create and bind the callbacks >>
        self.createBindings()
    #@+node:ekr.20081121110412.303: *5* createBindings (fontPicker)
    def createBindings (self):

        c = self.c ; k = c.k

        table = (
            ('<Button-1>',  k.masterClickHandler),
            ('<Double-1>',  k.masterClickHandler),
            ('<Button-3>',  k.masterClickHandler),
            ('<Double-3>',  k.masterClickHandler),
            ('<Key>',       k.masterKeyHandler),
            ("<Escape>",    self.hideFontTab),
        )

        w = self.sampleWidget
        for event, callback in table:
            c.bind(w,event,callback)

        k.completeAllBindingsForWidget(w)
    #@+node:ekr.20081121110412.304: *5* getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        try:
            return tkFont.Font(family=family,size=size,slant=slant,weight=weight)
        except Exception:
            g.es("exception setting font")
            g.es('','family,size,slant,weight:','',family,'',size,'',slant,'',weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20081121110412.305: *5* setFont
    def setFont(self,familyBox,sizeEntry,slantBox,weightBox,label):

        d = {}
        for box,key in (
            (familyBox, 'family'),
            (None,      'size'),
            (slantBox,  'slant'),
            (weightBox, 'weight'),
        ):
            if box: val = box.get()
            else:
                val = sizeEntry.get().strip() or ''
                try: int(val)
                except ValueError: val = None
            if val and val.lower() not in ('none','<none>',):
                d[key] = val

        family=d.get('family',None)
        size=d.get('size',12)
        weight=d.get('weight','normal')
        slant=d.get('slant','roman')
        font = self.getFont(family,size,slant,weight)
        label.configure(font=font)
    #@+node:ekr.20081121110412.306: *5* hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-others
#@+node:ekr.20081121110412.408: *3* class leoTkinterMenu
class leoTkinterMenu (leoMenu.leoMenu):
    """A class that represents a Leo window."""
    #@+others
    #@+node:ekr.20081121110412.409: *4* Birth & death
    #@+node:ekr.20081121110412.410: *5* leoTkinterMenu.__init__
    def __init__ (self,frame):

        # Init the base class.
        leoMenu.leoMenu.__init__(self,frame)

        self.top = frame.top
        self.c = c = frame.c
        self.frame = frame

        self.font = c.config.getFontFromParams(
            'menu_text_font_family', 'menu_text_font_size',
            'menu_text_font_slant',  'menu_text_font_weight',
            c.config.defaultMenuFontSize)
    #@+node:ekr.20081121110412.411: *4* Activate menu commands
    #@+node:ekr.20081121110412.412: *5* tkMenu.activateMenu
    def activateMenu (self,menuName):

        c = self.c ;  top = c.frame.top
        topx,topy = top.winfo_rootx(),top.winfo_rooty()
        menu = c.frame.menu.getMenu(menuName)

        if menu:
            d = self.computeMenuPositions()
            x = d.get(menuName)
            if x is None:
                x = 0 ; g.trace('oops, no menu offset: %s' % menuName)

            menu.tk_popup(topx+d.get(menuName,0),topy) # Fix by caugm.  Thanks!
        else:
            g.trace('oops, no menu: %s' % menuName)
    #@+node:ekr.20081121110412.413: *5* tkMenu.computeMenuPositions
    def computeMenuPositions (self):

        # A hack.  It would be better to set this when creating the menus.
        menus = ('File','Edit','Outline','Plugins','Cmds','Window','Help')

        # Compute the *approximate* x offsets of each menu.
        d = {}
        n = 0
        for z in menus:
            menu = self.getMenu(z)
            fontName = menu.cget('font')
            font = tkFont.Font(font=fontName)
            # g.pr('%8s' % (z),menu.winfo_reqwidth(),menu.master,menu.winfo_x())
            d [z] = n
            # A total hack: sorta works on windows.
            n += font.measure(z+' '*4)+1

        return d
    #@+node:ekr.20081121110412.414: *4* Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20081121110412.415: *5* Methods with Tk spellings
    #@+node:ekr.20081121110412.416: *6* add_cascade
    def add_cascade (self,parent,label,menu,underline):

        """Wrapper for the Tkinter add_cascade menu method."""

        if parent:
            return parent.add_cascade(label=label,menu=menu,underline=underline)
    #@+node:ekr.20081121110412.417: *6* add_command
    def add_command (self,menu,**keys):

        """Wrapper for the Tkinter add_command menu method."""

        if menu:
            return self.c.add_command(menu,**keys)
    #@+node:ekr.20081121110412.418: *6* add_separator
    def add_separator(self,menu):

        """Wrapper for the Tkinter add_separator menu method."""

        if menu:
            menu.add_separator()
    #@+node:ekr.20081121110412.419: *6* bind (not called)
    def bind (self,bind_shortcut,callback):

        """Wrapper for the Tkinter bind menu method."""

        g.trace(bind_shortcut,g.callers())

        c = self.c

        return c.bind(self.top,bind_shortcut,callback)
    #@+node:ekr.20081121110412.420: *6* delete
    def delete (self,menu,realItemName):

        """Wrapper for the Tkinter delete menu method."""

        if menu:
            return menu.delete(realItemName)
    #@+node:ekr.20081121110412.421: *6* delete_range
    def delete_range (self,menu,n1,n2):

        """Wrapper for the Tkinter delete menu method."""

        if menu:
            try:
                return menu.delete(n1,n2)
            except TypeError:
                g.es("delete_range failed, printing traceback to stdout", color="red")
                import traceback
                traceback.print_exc()

    #@+node:ekr.20081121110412.422: *6* destroy
    def destroy (self,menu):

        """Wrapper for the Tkinter destroy menu method."""

        if menu:
            return menu.destroy()
    #@+node:ekr.20081121110412.423: *6* insert
    def insert (self,menuName,position,label,command,underline=None):

        menu = self.getMenu(menuName)
        if menu:
            if underline is None:
                menu.insert(position,'command',label=label,command=command)
            else:
                menu.insert(position,'command',label=label,command=command,underline=underline)
    #@+node:ekr.20081121110412.424: *6* insert_cascade
    def insert_cascade (self,parent,index,label,menu,underline):

        """Wrapper for the Tkinter insert_cascade menu method."""

        if parent:
            return parent.insert_cascade(
                index=index,label=label,
                menu=menu,underline=underline)
    #@+node:ekr.20081121110412.425: *6* new_menu
    def new_menu(self,parent,tearoff=False,label=''): # label is for debugging.

        """Wrapper for the Tkinter new_menu menu method."""

        if self.font:
            try:
                return Tk.Menu(parent,tearoff=tearoff,font=self.font)
            except Exception:
                g.es_exception()
                return Tk.Menu(parent,tearoff=tearoff)
        else:
            return Tk.Menu(parent,tearoff=tearoff)
    #@+node:ekr.20081121110412.426: *5* Methods with other spellings (Tkmenu)
    #@+node:ekr.20081121110412.427: *6* clearAccel
    def clearAccel(self,menu,name):

        if not menu:
            return

        realName = self.getRealMenuName(name)
        realName = realName.replace("&","")

        menu.entryconfig(realName,accelerator='')
    #@+node:ekr.20081121110412.428: *6* createMenuBar (Tkmenu)
    def createMenuBar(self,frame):

        top = frame.top

        # Note: font setting has no effect here.
        topMenu = Tk.Menu(top,postcommand=self.updateAllMenus)

        # Do gui-independent stuff.
        self.setMenu("top",topMenu)
        self.createMenusFromTables()

        top.config(menu=topMenu) # Display the menu.
    #@+node:ekr.20081121110412.429: *6* createOpenWithMenu (Tkmenu)
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create a submenu.'''

        # g.trace(g.callers(5))

        menu = Tk.Menu(parent,tearoff=0)
        if menu:
            parent.insert_cascade(index,label=label,menu=menu,underline=amp_index)
        return menu
    #@+node:ekr.20081121110412.430: *6* disableMenu
    def disableMenu (self,menu,name):

        if not menu:
            return

        try:
            menu.entryconfig(name,state="disabled")
        except: 
            try:
                realName = self.getRealMenuName(name)
                realName = realName.replace("&","")
                menu.entryconfig(realName,state="disabled")
            except:
                g.pr("disableMenu menu,name:",menu,name)
                g.es_exception()
    #@+node:ekr.20081121110412.431: *6* enableMenu
    # Fail gracefully if the item name does not exist.

    def enableMenu (self,menu,name,val):

        if not menu:
            return

        state = g.choose(val,"normal","disabled")
        try:
            menu.entryconfig(name,state=state)
        except:
            try:
                realName = self.getRealMenuName(name)
                realName = realName.replace("&","")
                menu.entryconfig(realName,state=state)
            except:
                g.pr("enableMenu menu,name,val:",menu,name,val)
                g.es_exception()
    #@+node:ekr.20081121110412.432: *6* getMenuLabel
    def getMenuLabel (self,menu,name):

        '''Return the index of the menu item whose name (or offset) is given.
        Return None if there is no such menu item.'''

        try:
            index = menu.index(name)
        except:
            index = None

        return index
    #@+node:ekr.20081121110412.433: *6* setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        if not menu:
            return

        try:
            if type(name) == type(0):
                # "name" is actually an index into the menu.
                menu.entryconfig(name,label=label,underline=underline)
            else:
                # Bug fix: 2/16/03: use translated name.
                realName = self.getRealMenuName(name)
                realName = realName.replace("&","")
                # Bug fix: 3/25/03" use tranlasted label.
                label = self.getRealMenuName(label)
                label = label.replace("&","")
                menu.entryconfig(realName,label=label,underline=underline)
        except:
            if not g.app.unitTesting:
                g.pr("setMenuLabel menu,name,label:",menu,name,label)
                g.es_exception()
    #@+node:ekr.20081121110412.434: *4* getMacHelpMenu
    def getMacHelpMenu (self,table):

        defaultTable = [
                # &: a,b,c,d,e,f,h,l,m,n,o,p,r,s,t,u
                ('&About Leo...',           'about-leo'),
                ('Online &Home Page',       'open-online-home'),
                '*open-online-&tutorial',
                '*open-&users-guide',
                '-',
                ('Open Leo&Docs.leo',       'open-leoDocs-leo'),
                ('Open Leo&Plugins.leo',    'open-leoPlugins-leo'),
                ('Open Leo&Settings.leo',   'open-leoSettings-leo'),
                ('Open &myLeoSettings.leo', 'open-myLeoSettings-leo'),
                ('Open scr&ipts.leo',       'open-scripts-leo'),
                '-',
                '*he&lp-for-minibuffer',
                '*help-for-&command',
                '-',
                '*&apropos-autocompletion',
                '*apropos-&bindings',
                '*apropos-&debugging-commands',
                '*apropos-&find-commands',
                '-',
                '*pri&nt-bindings',
                '*print-c&ommands',
            ]

        try:
            topMenu = self.getMenu('top')
            # Use the name argument to create the special Macintosh Help menu.
            helpMenu = Tk.Menu(topMenu,name='help',tearoff=0)
            self.add_cascade(topMenu,label='Help',menu=helpMenu,underline=0)
            self.createMenuEntries(helpMenu,table or defaultTable)
            return helpMenu

        except Exception:
            g.trace('Can not get MacOS Help menu')
            g.es_exception()
            return None
    #@-others
#@+node:ekr.20081121110412.435: *3* class leoTkinterTree
class leoTkinterTree (leoFrame.leoTree):

    """Leo tkinter tree class."""

    callbacksInjected = False

    #@+<< about drawing >>
    #@+node:ekr.20081121110412.436: *4*   << About drawing >>
    #@+at
    # 
    # New in Leo 4.5: The 'Newest World Order':
    # 
    # - Redrawing the screen and setting focus only happen in c.outerUpdate.
    # - c.redraw only requests a redraw.
    # - c.redraw_now is equivalent to c.redraw() followed by c.outerUpdate.
    # - c.beginUpdate does nothing.  c.endUpdate(False) does nothing.
    # - c.endUpdate() is equivalent to c.redraw()
    # - There is no longer any need to ensure c.endUpdate is called for every c.beginUpdate.
    #   Thus, there is no need for the associated try/finally statements.
    #@-<< about drawing >>

    #@+others
    #@+node:ekr.20081121110412.442: *4*  Birth... (tkTree)
    #@+node:ekr.20081121110412.443: *5* __init__ (tkTree)
    def __init__(self,c,frame,canvas):

        # Init the base class.
        leoFrame.leoTree.__init__(self,frame)

        # Configuration and debugging settings.
        # These must be defined here to eliminate memory leaks.
        self.allow_clone_drags          = c.config.getBool('allow_clone_drags')
        self.center_selected_tree_node  = c.config.getBool('center_selected_tree_node')
        self.enable_drag_messages       = c.config.getBool("enable_drag_messages")
        self.expanded_click_area        = c.config.getBool('expanded_click_area')
        self.gc_before_redraw           = c.config.getBool('gc_before_redraw')

        self.headline_text_editing_foreground_color = c.config.getColor(
            'headline_text_editing_foreground_color')
        self.headline_text_editing_background_color = c.config.getColor(
            'headline_text_editing_background_color')
        self.headline_text_editing_selection_foreground_color = c.config.getColor(
            'headline_text_editing_selection_foreground_color')
        self.headline_text_editing_selection_background_color = c.config.getColor(
            'headline_text_editing_selection_background_color')
        self.headline_text_selected_foreground_color = c.config.getColor(
            "headline_text_selected_foreground_color")
        self.headline_text_selected_background_color = c.config.getColor(
            "headline_text_selected_background_color")
        self.headline_text_editing_selection_foreground_color = c.config.getColor(
            "headline_text_editing_selection_foreground_color")
        self.headline_text_editing_selection_background_color = c.config.getColor(
            "headline_text_editing_selection_background_color")
        self.headline_text_unselected_foreground_color = c.config.getColor(
            'headline_text_unselected_foreground_color')
        self.headline_text_unselected_background_color = c.config.getColor(
            'headline_text_unselected_background_color')

        self.idle_redraw = c.config.getBool('idle_redraw')
        self.initialClickExpandsOrContractsNode = c.config.getBool(
            'initialClickExpandsOrContractsNode')
        self.look_for_control_drag_on_mouse_down = c.config.getBool(
            'look_for_control_drag_on_mouse_down')
        self.select_all_text_when_editing_headlines = c.config.getBool(
            'select_all_text_when_editing_headlines')

        self.stayInTree     = c.config.getBool('stayInTreeAfterSelect')
        self.trace          = c.config.getBool('trace_tree')
        self.trace_alloc    = c.config.getBool('trace_tree_alloc')
        self.trace_chapters = c.config.getBool('trace_chapters')
        self.trace_edit     = c.config.getBool('trace_tree_edit')
        self.trace_gc       = c.config.getBool('trace_tree_gc')
        self.trace_redraw   = c.config.getBool('trace_tree_redraw')
        self.trace_select   = c.config.getBool('trace_select')
        self.trace_stats    = c.config.getBool('show_tree_stats')
        self.use_chapters   = c.config.getBool('use_chapters')

        # Objects associated with this tree.
        self.canvas = canvas

        #@+<< define drawing constants >>
        #@+node:ekr.20081121110412.444: *6* << define drawing constants >>
        self.box_padding = 5 # extra padding between box and icon
        self.box_width = 9 + self.box_padding
        self.icon_width = 20
        self.text_indent = 4 # extra padding between icon and tex

        self.hline_y = 7 # Vertical offset of horizontal line
        self.root_left = 7 + self.box_width
        self.root_top = 2

        self.default_line_height = 17 + 2 # default if can't set line_height from font.
        self.line_height = self.default_line_height
        #@-<< define drawing constants >>
        #@+<< old ivars >>
        #@+node:ekr.20081121110412.445: *6* << old ivars >>
        # Miscellaneous info.
        self.iconimages = {} # Image cache set by getIconImage().
        self.active = False # True if present headline is active
        self._editPosition = None # Returned by leoTree.editPosition()
        self.lineyoffset = 0 # y offset for this headline.
        self.lastClickFrameId = None # id of last entered clickBox.
        self.lastColoredText = None # last colored text widget.

        # Set self.font and self.fontName.
        self.setFontFromConfig()

        # Drag and drop
        self.drag_p = None
        self.controlDrag = False # True: control was down when drag started.

        # Keep track of popup menu so we can handle behavior better on Linux Context menu
        self.popupMenu = None

        # Incremental redraws:
        self.allocateOnlyVisibleNodes = False # True: enable incremental redraws.
        self.prevMoveToFrac = 0.0
        self.visibleArea = None
        self.expandedVisibleArea = None

        if self.allocateOnlyVisibleNodes:
            c.bind(self.frame.bar1,"<Button-1-ButtonRelease>", self.redraw_now)
        #@-<< old ivars >>
        #@+<< inject callbacks into the position class >>
        #@+node:ekr.20081121110412.446: *6* << inject callbacks into the position class >>
        # The new code injects 3 callbacks for the colorizer.

        if not leoTkinterTree.callbacksInjected: # Class var.
            leoTkinterTree.callbacksInjected = True
            self.injectCallbacks()
        #@-<< inject callbacks into the position class >>

        self.dragging = False
        self.generation = 0
        self.prevPositions = 0
        self.redrawing = False # Used only to disable traces.
        self.redrawCount = 0 # Count for debugging.
        self.revertHeadline = None # Previous headline text for abortEditLabel.

        # New in 4.4: We should stay in the tree to use per-pane bindings.
        self.textBindings = [] # Set in setBindings.
        self.textNumber = 0 # To make names unique.
        self.updateCount = 0 # Drawing is enabled only if self.updateCount <= 0
        self.verbose = True

        self.setEditPosition(None) # Set positions returned by leoTree.editPosition()

        # Keys are id's, values are positions...
        self.ids = {}
        self.iconIds = {}

        # Lists of visible (in-use) widgets...
        self.visibleBoxes = []
        self.visibleClickBoxes = []
        self.visibleIcons = []
        self.visibleLines = []
        self.visibleText  = {}
            # Pre 4.4b2: Keys are vnodes, values are Tk.Text widgets.
            #     4.4b2: Keys are p.key(), values are Tk.Text widgets.
        self.visibleUserIcons = []

        # Dictionaries of free, hidden widgets...
        # Keys are id's, values are widgets.
        self.freeBoxes = {}
        self.freeClickBoxes = {}
        self.freeIcons = {}
        self.freeLines = {}
        self.freeText = {} # New in 4.4b2: a list of free Tk.Text widgets

        self.freeUserIcons = {}

        self._block_canvas_menu = False
    #@+node:ekr.20081121110412.447: *5* tkTtree.setBindings & helper
    def setBindings (self,):

        '''Create master bindings for all headlines.'''

        tree = self ; k = self.c.k

        # g.trace('self',self,'canvas',self.canvas)

        tree.setBindingsHelper()

        tree.setCanvasBindings(self.canvas)

        k.completeAllBindingsForWidget(self.canvas)

        k.completeAllBindingsForWidget(self.bindingWidget)

    #@+node:ekr.20081121110412.448: *6* tkTree.setBindingsHelper
    def setBindingsHelper (self):

        tree = self ; c = tree.c ; k = c.k

        self.bindingWidget = w = g.app.gui.plainTextWidget(
            self.canvas,name='bindingWidget')

        c.bind(w,'<Key>',k.masterKeyHandler)

        table = [
            ('<Button-1>',       k.masterClickHandler,          tree.onHeadlineClick),
            ('<Button-3>',       k.masterClick3Handler,         tree.onHeadlineRightClick),
            ('<Double-Button-1>',k.masterDoubleClickHandler,    tree.onHeadlineClick),
            ('<Double-Button-3>',k.masterDoubleClick3Handler,   tree.onHeadlineRightClick),
        ]

        for a,handler,func in table:
            def treeBindingCallback(event,handler=handler,func=func):
                # g.trace('func',func)
                return handler(event,func)
            c.bind(w,a,treeBindingCallback)

        self.textBindings = w.bindtags()
    #@+node:ekr.20081121110412.449: *5* tkTree.setCanvasBindings
    def setCanvasBindings (self,canvas):

        c = self.c ; k = c.k

        c.bind(canvas,'<Key>',k.masterKeyHandler)
        c.bind(canvas,'<Button-1>',self.onTreeClick)
        c.bind(canvas,'<Button-3>',self.onTreeRightClick)
        # c.bind(canvas,'<FocusIn>',self.onFocusIn)

        #@+<< make bindings for tagged items on the canvas >>
        #@+node:ekr.20081121110412.450: *6* << make bindings for tagged items on the canvas >>
        where = g.choose(self.expanded_click_area,'clickBox','plusBox')

        table = (
            (where,    '<Button-1>',self.onClickBoxClick),
            ('iconBox','<Button-1>',self.onIconBoxClick),
            ('iconBox','<Double-1>',self.onIconBoxDoubleClick),
            ('iconBox','<Button-3>',self.onIconBoxRightClick),
            ('iconBox','<Double-3>',self.onIconBoxRightClick),
            ('iconBox','<B1-Motion>',self.onDrag),
            ('iconBox','<Any-ButtonRelease-1>',self.onEndDrag),

            ('plusBox','<Button-3>', self.onPlusBoxRightClick),
            ('plusBox','<Button-1>', self.onClickBoxClick),
            ('clickBox','<Button-3>',  self.onClickBoxRightClick),
        )
        for tag,event_kind,callback in table:
            c.tag_bind(canvas,tag,event_kind,callback)
        #@-<< make bindings for tagged items on the canvas >>
        #@+<< create baloon bindings for tagged items on the canvas >>
        #@+node:ekr.20081121110412.451: *6* << create baloon bindings for tagged items on the canvas >>
        if 0: # I find these very irritating.
            for tag,text in (
                # ('plusBox','plusBox'),
                ('iconBox','Icon Box'),
                ('selectBox','Click to select'),
                ('clickBox','Click to expand or contract'),
                # ('textBox','Headline'),
            ):
                # A fairly long wait is best.
                balloon = Pmw.Balloon(self.canvas,initwait=700)
                balloon.tagbind(self.canvas,tag,balloonHelp=text)
        #@-<< create baloon bindings for tagged items on the canvas >>
    #@+node:ekr.20081121110412.452: *4* Allocation...
    #@+node:ekr.20081121110412.453: *5* newBox
    def newBox (self,p,x,y,image):

        canvas = self.canvas ; tag = "plusBox"

        if self.freeBoxes:
            # theId = self.freeBoxes.pop(0)
            d = self.freeBoxes ; theId = d.keys()[0] ; del d[theId]
            canvas.coords(theId,x,y)
            canvas.itemconfigure(theId,image=image)
        else:
            theId = canvas.create_image(x,y,image=image,tag=tag)
            if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.h),align=-20)

        if theId not in self.visibleBoxes: 
            self.visibleBoxes.append(theId)

        if p:
            self.ids[theId] = p

        return theId
    #@+node:ekr.20081121110412.454: *5* newClickBox
    def newClickBox (self,p,x1,y1,x2,y2):

        canvas = self.canvas ; defaultColor = ""
        tag = g.choose(p.hasChildren(),'clickBox','selectBox')

        if self.freeClickBoxes:
            # theId = self.freeClickBoxes.pop(0)
            d = self.freeClickBoxes ; theId = d.keys()[0] ; del d[theId]
            canvas.coords(theId,x1,y1,x2,y2)
            canvas.itemconfig(theId,tag=tag)
        else:
            theId = self.canvas.create_rectangle(x1,y1,x2,y2,tag=tag)
            canvas.itemconfig(theId,fill=defaultColor,outline=defaultColor)
            if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.h),align=-20)

        if theId not in self.visibleClickBoxes:
            self.visibleClickBoxes.append(theId)
        if p:
            self.ids[theId] = p

        return theId
    #@+node:ekr.20081121110412.455: *5* newIcon
    def newIcon (self,p,x,y,image):

        canvas = self.canvas ; tag = "iconBox"

        if self.freeIcons:
            # theId = self.freeIcons.pop(0)
            d = self.freeIcons ; theId = d.keys()[0] ; del d[theId]
            canvas.itemconfigure(theId,image=image)
            canvas.coords(theId,x,y)
        else:
            theId = canvas.create_image(x,y,image=image,anchor="nw",tag=tag)
            if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.h),align=-20)

        if theId not in self.visibleIcons:
            self.visibleIcons.append(theId)

        if p:
            data = p,self.generation
            self.iconIds[theId] = data # Remember which vnode belongs to the icon.
            self.ids[theId] = p

        return theId
    #@+node:ekr.20081121110412.456: *5* newLine
    def newLine (self,p,x1,y1,x2,y2):

        canvas = self.canvas

        if self.freeLines:
            # theId = self.freeLines.pop(0)
            d = self.freeLines ; theId = d.keys()[0] ; del d[theId]
            canvas.coords(theId,x1,y1,x2,y2)
        else:
            theId = canvas.create_line(x1,y1,x2,y2,tag="lines",fill="gray50") # stipple="gray25")
            if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.h),align=-20)

        if p:
            self.ids[theId] = p

        if theId not in self.visibleLines:
            self.visibleLines.append(theId)

        return theId
    #@+node:ekr.20081121110412.457: *5* newText (tkTree) and helper
    def newText (self,p,x,y):

        canvas = self.canvas ; tag = "textBox"
        c = self.c ;  k = c.k
        if self.freeText:
            # w,theId = self.freeText.pop()
            d = self.freeText ; data = d.keys()[0] ; w,theId = data ; del d[data]
            canvas.coords(theId,x,y) # Make the window visible again.
                # theId is the id of the *window* not the text.
        else:
            # Tags are not valid in Tk.Text widgets.
            self.textNumber += 1
            w = g.app.gui.plainTextWidget(
                canvas,name='head-%d' % self.textNumber,
                state="normal",font=self.font,bd=0,relief="flat",height=1)
            w.bindtags(self.textBindings) # Set the bindings for this widget.

            if 0: # Crashes on XP.
                #@+<< patch by Maciej Kalisiak to handle scroll-wheel events >>
                #@+node:ekr.20081121110412.458: *6* << patch by Maciej Kalisiak  to handle scroll-wheel events >>
                def PropagateButton4(e):
                    canvas.event_generate("<Button-4>")
                    return "break"

                def PropagateButton5(e):
                    canvas.event_generate("<Button-5>")
                    return "break"

                def PropagateMouseWheel(e):
                    canvas.event_generate("<MouseWheel>")
                    return "break"

                instance_tag = w.bindtags()[0]
                w.bind_class(instance_tag, "<Button-4>", PropagateButton4)
                w.bind_class(instance_tag, "<Button-5>", PropagateButton5)
                w.bind_class(instance_tag, "<MouseWheel>",PropagateMouseWheel)
                #@-<< patch by Maciej Kalisiak to handle scroll-wheel events >>

            theId = canvas.create_window(x,y,anchor="nw",window=w,tag=tag)
            w.leo_window_id = theId # Never changes.

            if self.trace_alloc: g.trace('%3d %6s' % (theId,id(w)),align=-20)

        # Common configuration.
        if 0: # Doesn't seem to work.
            balloon = Pmw.Balloon(canvas,initwait=700)
            balloon.tagbind(canvas,theId,balloonHelp='Headline')

        if p:
            self.ids[theId] = p # Add the id of the *window*
            self.setHeadlineText(theId,w,p.h)
            w.configure(width=self.headWidth(p=p))
            w.leo_position = p # This p never changes.
                # *Required*: onHeadlineClick uses w.leo_position to get p.

            # Keys are p.key().  Entries are (w,theId)
            self.visibleText [p.key()] = w,theId
        else:
            g.trace('**** can not happen.  No p')

        return w
    #@+node:ekr.20081121110412.459: *6* tree.setHeadlineText
    def setHeadlineText (self,theId,w,s):

        """All changes to text widgets should come here."""

        # if self.trace_alloc: g.trace('%4d %6s %s' % (theId,self.textAddr(w),s),align=-20)

        state = w.cget("state")
        if state != "normal":
            w.configure(state="normal")
        w.delete(0,"end")
        # Important: do not allow newlines in headlines.
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]
        w.insert("end",s)
        # g.trace(repr(s))
        if state != "normal":
            w.configure(state=state)
    #@+node:ekr.20081121110412.460: *5* recycleWidgets
    def recycleWidgets (self):

        canvas = self.canvas

        for theId in self.visibleBoxes:
            # if theId not in self.freeBoxes:
                # self.freeBoxes.append(theId)
            self.freeBoxes[theId] = theId
            canvas.coords(theId,-100,-100)
        self.visibleBoxes = []

        for theId in self.visibleClickBoxes:
            self.freeClickBoxes[theId] = theId
            canvas.coords(theId,-100,-100,-100,-100)
        self.visibleClickBoxes = []

        for theId in self.visibleIcons:
            self.freeIcons[theId] = theId
            canvas.coords(theId,-100,-100)
        self.visibleIcons = []

        for theId in self.visibleLines:
            self.freeLines[theId] = theId
            canvas.coords(theId,-100,-100,-100,-100)
        self.visibleLines = []

        aList = self.visibleText.values()
        for data in aList:
            w,theId = data
            # assert theId == w.leo_window_id
            canvas.coords(theId,-100,-100)
            w.leo_position = None # Allow the position to be freed.
            self.freeText[data] = data
        self.visibleText = {}

        # g.trace('deleting visible user icons!')
        for theId in self.visibleUserIcons:
            # The present code does not recycle user Icons.
            self.canvas.delete(theId)
        self.visibleUserIcons = []
    #@+node:ekr.20081121110412.461: *5* destroyWidgets
    def destroyWidgets (self):

        self.ids = {}

        self.visibleBoxes = []
        self.visibleClickBoxes = []
        self.visibleIcons = []
        self.visibleLines = []
        self.visibleUserIcons = []

        self.visibleText = {}

        self.freeText = {}
        self.freeBoxes = {}
        self.freeClickBoxes = {}
        self.freeIcons = {}
        self.freeLines = {}

        self.canvas.delete("all")
    #@+node:ekr.20081121110412.462: *5* showStats
    def showStats (self):

        z = []
        for kind,a,b in (
            ('boxes',self.visibleBoxes,self.freeBoxes),
            ('clickBoxes',self.visibleClickBoxes,self.freeClickBoxes),
            ('icons',self.visibleIcons,self.freeIcons),
            ('lines',self.visibleLines,self.freeLines),
            ('tesxt',self.visibleText.values(),self.freeText),
        ):
            z.append('%10s used: %4d free: %4d' % (kind,len(a),len(b)))

        s = '\n' + '\n'.join(z)
        g.es_print('',s)
    #@+node:ekr.20081121110412.463: *4* Config & Measuring...
    #@+node:ekr.20081121110412.464: *5* tree.getFont,setFont,setFontFromConfig
    def getFont (self):

        return self.font

    def setFont (self,font=None, fontName=None):

        # ESSENTIAL: retain a link to font.
        if fontName:
            self.fontName = fontName
            self.font = tkFont.Font(font=fontName)
        else:
            self.fontName = None
            self.font = font

        self.setLineHeight(self.font)

    # Called by ctor and when config params are reloaded.
    def setFontFromConfig (self):
        c = self.c
        # g.trace()
        font = c.config.getFontFromParams(
            "headline_text_font_family", "headline_text_font_size",
            "headline_text_font_slant",  "headline_text_font_weight",
            c.config.defaultTreeFontSize)

        self.setFont(font)
    #@+node:ekr.20081121110412.465: *5* headWidth & widthInPixels
    def headWidth(self,p=None,s=''):

        """Returns the proper width of the entry widget for the headline."""

        if p: s = p.h

        return self.font.measure(s)/self.font.measure('0')+1


    def widthInPixels(self,s):

        s = g.toEncodedString(s)

        return self.font.measure(s)
    #@+node:ekr.20081121110412.466: *5* setLineHeight
    def setLineHeight (self,font):

        try:
            metrics = font.metrics()
            linespace = metrics ["linespace"]
            self.line_height = linespace + 5 # Same as before for the default font on Windows.
            # g.pr(metrics)
        except:
            self.line_height = self.default_line_height
            g.es("exception setting outline line height")
            g.es_exception()
    #@+node:ekr.20081121110412.467: *4* Debugging...
    #@+node:ekr.20081121110412.468: *5* textAddr
    def textAddr(self,w):

        """Return the address part of repr(Tk.Text)."""

        s = repr(w)
        i = s.find('id: ')
        if i != -1:
            return s[i+4:i+12].lower()
        else:
            return s
    #@+node:ekr.20081121110412.469: *5* traceIds (Not used)
    # Verbose tracing is much more useful than this because we can see the recent past.

    def traceIds (self,full=False):

        tree = self

        for theDict,tag,flag in ((tree.ids,"ids",True),(tree.iconIds,"icon ids",False)):
            g.pr('=' * 60)
            g.pr("\n%s..." % tag)
            for key in sorted(theDict):
                p = tree.ids.get(key)
                if p is None: # For lines.
                    g.pr("%3d None" % key)
                else:
                    g.pr("%3d" % key,p.h)
            if flag and full:
                g.pr('-' * 40)
                seenValues = {}
                for key in sorted(theDict):
                    value = theDict.get(key)
                    if value not in seenValues:
                        seenValues[value]=True
                        for item in theDict.items():
                            key,val = item
                            if val and val == value:
                                g.pr("%3d" % key,val.h)
    #@+node:ekr.20081121110412.470: *4* Drawing... (tkTree)
    #@+node:ekr.20090110073024.10: *5* Entry points (tkTree)
    #@+node:ekr.20081121110412.471: *6* tree.begin/endUpdate
    def beginUpdate (self):

        self.updateCount += 1
        # g.trace('tree',id(self),self.updateCount,g.callers())

    def endUpdate (self,flag,scroll=False):

        self.updateCount -= 1
        # g.trace(self.updateCount,'scroll',scroll,g.callers())

        if self.updateCount <= 0:
            if flag:
                self.redraw_now(scroll=scroll)
            if self.updateCount < 0:
                g.trace("Can't happen: negative updateCount",g.callers())
    #@+node:ekr.20081121110412.472: *6* tree.redraw_now & helper (tkTree)
    # New in 4.4b2: suppress scrolling by default.
    # New in 4.6: enable scrolling by default.

    def redraw_now (self,p=None,scroll=True,forceDraw=False):

        '''Redraw immediately.
        forceDraw is used to eliminate draws while dragging.'''

        trace = False and not g.unitTesting
        c = self.c

        if g.app.quitting or self.frame not in g.app.windowList:
            return
        if self.drag_p and not forceDraw:
            return

        if p is None:
            p = c.currentPosition()
        else:
            c.setCurrentPosition(p)

        if trace: g.trace(self.redrawCount,g.callers(8))

        if not g.app.unitTesting:
            if self.gc_before_redraw:
                g.collectGarbage()
            if g.app.trace_gc_verbose:
                if (self.redrawCount % 5) == 0:
                    g.printGcSummary()
            if self.trace_redraw or self.trace_alloc:
                # g.trace(self.redrawCount,g.callers())
                # g.trace(c.rootPosition().h,'canvas:',id(self.canvas),g.callers())
                if self.trace_stats:
                    g.print_stats()
                    g.clear_stats()

        # New in 4.4b2: Call endEditLabel, but suppress the redraw.
        if 0: #### A major change.
            self.beginUpdate()
            try:
                self.endEditLabel()
            finally:
                self.endUpdate(False)

        # Do the actual redraw. (c.redraw has called c.expandAllAncestors.)
        if self.idle_redraw:
            def idleRedrawCallback(event=None,self=self,scroll=scroll):
                self.redrawHelper(scroll=scroll,forceDraw=forceDraw)
            self.canvas.after_idle(idleRedrawCallback)
        else:
            self.redrawHelper(scroll=scroll,forceDraw=forceDraw)

        if g.app.unitTesting:
            self.canvas.update_idletasks() # Important for unit tests.

    redraw = redraw_now # Compatibility
    #@+node:ekr.20081121110412.473: *7* redrawHelper
    def redrawHelper (self,scroll=True,forceDraw=False):

        # This can be called at idle time, so there are shutdown issues.
        if g.app.quitting or self.frame not in g.app.windowList:
            return
        if self.drag_p and not forceDraw:
            return
        if not hasattr(self,'c'):
            return

        c = self.c ; trace = False
        oldcursor = self.canvas['cursor']
        self.canvas['cursor'] = "watch"

        if not g.doHook("redraw-entire-outline",c=c):

            c.setTopVnode(None)
            self.setVisibleAreaToFullCanvas()
            self.drawTopTree()
            # Set up the scroll region after the tree has been redrawn.
            bbox = self.canvas.bbox('all')
            if trace: g.trace('bbox',bbox,g.callers())
            if bbox is None:
                x0,y0,x1,y1 = 0,0,100,100
            else:
                x0, y0, x1, y1 = bbox
            self.canvas.configure(scrollregion=(0, 0, x1, y1))
            if scroll:
                self.canvas.update_idletasks() # Essential.
                self.scrollTo()

        g.doHook("after-redraw-outline",c=c)

        self.canvas['cursor'] = oldcursor
    #@+node:ekr.20090110134111.11: *6* redraw_after_contract
    def redraw_after_contract (self,p):

        self.redraw_now()
    #@+node:ekr.20090110073024.11: *6* redraw_after_head_changed (tkTree)
    def redraw_after_head_changed (self):

        # Fix bug 518823: 2010/02/16. Redraw the entire tree.
        # The changed node may be a non-cloned descendant of a cloned node.
        self.redraw_now()
    #@+node:ekr.20090110073024.13: *6* redraw_after_icons_changed
    def redraw_after_icons_changed (self):

        if g.unitTesting:
            # A terrible hack.  Don't switch edit widget.
            self.redrawCount += 1
        else:
            self.redraw_now()
    #@+node:ekr.20090110073024.12: *6* redraw_after_select
    def redraw_after_select (self,p,edit=False,editAll=False):

        self.redraw_now()
    #@+node:ekr.20081121110412.474: *5* idle_second_redraw
    def idle_second_redraw (self):

        c = self.c

        # Erase and redraw the entire tree the SECOND time.
        # This ensures that all visible nodes are allocated.
        c.setTopVnode(None)
        args = self.canvas.yview()
        self.setVisibleArea(args)

        if 0:
            self.canvas.delete("all")

        self.drawTopTree()

        if self.trace:
            g.trace(self.redrawCount)
    #@+node:ekr.20081121110412.475: *5* drawX...
    #@+node:ekr.20081121110412.476: *6* drawBox
    def drawBox (self,p,x,y):

        tree = self ; c = self.c
        y += 7 # draw the box at x, y+7

        theId = g.doHook("draw-outline-box",tree=tree,c=c,p=p,v=p,x=x,y=y)

        if theId is None:
            # if self.trace_gc: g.printNewObjects(tag='box 1')
            iconname = g.choose(p.isExpanded(),"minusnode.gif", "plusnode.gif")
            image = self.getIconImage(iconname)
            theId = self.newBox(p,x,y+self.lineyoffset,image)
            # if self.trace_gc: g.printNewObjects(tag='box 2')
            return theId
        else:
            return theId
    #@+node:ekr.20081121110412.477: *6* drawClickBox
    def drawClickBox (self,p,y):

        h = self.line_height

        # Define a slighly larger rect to catch clicks.
        if self.expanded_click_area:
            self.newClickBox(p,0,y,1000,y+h-2)
    #@+node:ekr.20081121110412.478: *6* drawIcon
    def drawIcon(self,p,x=None,y=None):

        """Draws icon for position p at x,y, or at p.v.iconx,p.v.icony if x,y = None,None"""

        # if self.trace_gc: g.printNewObjects(tag='icon 1')

        c = self.c ; v = p.v
        #@+<< compute x,y and iconVal >>
        #@+node:ekr.20081121110412.479: *7* << compute x,y and iconVal >>
        if x is None and y is None:
            try:
                x,y = v.iconx, v.icony
            except:
                # Inject the ivars.
                x,y = v.iconx, v.icony = 0,0
        else:
            # Inject the ivars.
            v.iconx, v.icony = x,y

        y += 2 # draw icon at y + 2

        # Always recompute v.iconVal.
        # This is an important drawing optimization.
        val = v.computeIcon()
        assert(0 <= val <= 15)
        # g.trace(v,val)
        #@-<< compute x,y and iconVal >>
        v.iconVal = val

        if not g.doHook("draw-outline-icon",tree=self,c=c,p=p,v=p,x=x,y=y):

            # Get the image.
            imagename = "box%02d.GIF" % val
            image = self.getIconImage(imagename)
            self.newIcon(p,x,y+self.lineyoffset,image)

        return 0,self.icon_width # dummy icon height,width
    #@+node:ekr.20081121110412.480: *6* drawLine
    def drawLine (self,p,x1,y1,x2,y2):

        theId = self.newLine(p,x1,y1,x2,y2)

        return theId
    #@+node:ekr.20081121110412.481: *6* drawNode & force_draw_node (good trace)
    def drawNode(self,p,x,y):

        c = self.c

        # g.trace(x,y,p,id(self.canvas))

        data = g.doHook("draw-outline-node",tree=self,c=c,p=p,v=p,x=x,y=y)
        if data is not None: return data

        if 1:
            self.lineyoffset = 0
        else:
            if hasattr(p.v,"unknownAttributes"):
                self.lineyoffset = p.v.unknownAttributes.get("lineYOffset",0)
            else:
                self.lineyoffset = 0

        # Draw the horizontal line.
        self.drawLine(p,
            x,y+7+self.lineyoffset,
            x+self.box_width,y+7+self.lineyoffset)

        if self.inVisibleArea(y):
            return self.force_draw_node(p,x,y)
        else:
            return self.line_height,0
    #@+node:ekr.20081121110412.482: *7* force_draw_node
    def force_draw_node(self,p,x,y):

        h = 0 # The total height of the line.
        indent = 0 # The amount to indent this line.

        h2,w2 = self.drawUserIcons(p,"beforeBox",x,y)
        h = max(h,h2) ; x += w2 ; indent += w2

        if p.hasChildren():
            self.drawBox(p,x,y)

        indent += self.box_width
        x += self.box_width # even if box isn't drawn.

        h2,w2 = self.drawUserIcons(p,"beforeIcon",x,y)
        h = max(h,h2) ; x += w2 ; indent += w2

        h2,w2 = self.drawIcon(p,x,y)
        h = max(h,h2) ; x += w2 ; indent += w2/2

        # Nothing after here affects indentation.
        h2,w2 = self.drawUserIcons(p,"beforeHeadline",x,y)
        h = max(h,h2) ; x += w2

        h2 = self.drawText(p,x,y)
        h = max(h,h2)
        x += self.widthInPixels(p.h)

        h2,w2 = self.drawUserIcons(p,"afterHeadline",x,y)
        h = max(h,h2)

        self.drawClickBox(p,y)

        return h,indent
    #@+node:ekr.20081121110412.483: *6* drawText
    def drawText(self,p,x,y):

        """draw text for position p at nominal coordinates x,y."""

        assert(p)

        c = self.c
        x += self.text_indent

        data = g.doHook("draw-outline-text-box",tree=self,c=c,p=p,v=p,x=x,y=y)
        if data is not None: return data

        self.newText(p,x,y+self.lineyoffset)

        self.configureTextState(p)

        return self.line_height
    #@+node:ekr.20081121110412.484: *6* drawUserIcons & helper
    def drawUserIcons(self,p,where,x,y):

        """Draw any icons specified by p.v.unknownAttributes["icons"]."""

        h,w = 0,0

        com = self.c.editCommands
        iconsList = com.getIconList(p)
        if not iconsList:
            return h,w

        try:
            for theDict in iconsList:
                h2,w2 = self.drawUserIcon(p,where,x,y,w,theDict)
                h = max(h,h2) ; w += w2
        except:
            g.es_exception()

        # g.trace(where,h,w)
        return h,w
    #@+node:ekr.20081121110412.485: *7* drawUserIcon
    def drawUserIcon (self,p,where,x,y,w2,theDict):

        c = self.c ; h,w = 0,0

        if where != theDict.get("where","beforeHeadline"):
            return h,w

        # if self.trace_gc: g.printNewObjects(tag='userIcon 1')

        # g.trace(where,x,y,theDict)

        #@+<< set offsets and pads >>
        #@+node:ekr.20081121110412.486: *8* << set offsets and pads >>
        xoffset = theDict.get("xoffset")
        try:    xoffset = int(xoffset)
        except: xoffset = 0

        yoffset = theDict.get("yoffset")
        try:    yoffset = int(yoffset)
        except: yoffset = 0

        xpad = theDict.get("xpad")
        try:    xpad = int(xpad)
        except: xpad = 0

        ypad = theDict.get("ypad")
        try:    ypad = int(ypad)
        except: ypad = 0
        #@-<< set offsets and pads >>
        theType = theDict.get("type")
        if theType == "icon":
            ### not ready yet.
            # s = theDict.get("icon")
            pass
        elif theType == "file":
            theFile = theDict.get("file")
            relPath = theDict.get('relPath')
            #@+<< draw the icon at file >>
            #@+node:ekr.20081121110412.487: *8* << draw the icon at file >>
            if relPath:
                fullname = g.os_path_join(g.app.loadDir,"..","Icons",relPath)
            else:
                fullname = g.os_path_join(g.app.loadDir,"..","Icons",theFile)
            fullname = g.os_path_normpath(fullname)

            # Bug fix: the key must include distinguish nodes.
            key = (fullname,p.v)
            image = self.iconimages.get(key)

            if not image:
                try:
                    from PIL import Image, ImageTk
                    image1 = Image.open(fullname)
                    image = ImageTk.PhotoImage(image1)
                    self.iconimages[key] = image
                except Exception:
                    #g.es_exception()
                    image = None

            if not image:
                try:
                    image = Tk.PhotoImage(master=self.canvas,file=fullname)
                    self.iconimages[key] = image
                except Exception:
                    #g.es_exception()
                    image = None

            if image:
                theId = self.canvas.create_image(
                    x+xoffset+w2,y+yoffset,
                    anchor="nw",image=image)

                tag='userIcon-%s' % theId
                self.canvas.itemconfigure(theId,tag=(tag,'userIcon')) #BJ
                self.ids[theId] = p.copy()

                def deleteButtonCallback(event=None,c=c,p=p,fullname=fullname,relPath=relPath):
                    #g.trace()
                    c.editCommands.deleteIconByName(p,fullname,relPath)
                    self._block_canvas_menu = True
                    return 'break'

                c.tag_bind(self.canvas,tag,'<3>',deleteButtonCallback)

                # assert(theId not in self.visibleIcons)
                self.visibleUserIcons.append(theId)

                h = image.height() + yoffset + ypad
                w = image.width()  + xoffset + xpad
            #@-<< draw the icon at file >>
        elif theType == "url":
            ## url = theDict.get("url")
            #@+<< draw the icon at url >>
            #@+node:ekr.20081121110412.488: *8* << draw the icon at url >>
            pass
            #@-<< draw the icon at url >>

        # Allow user to specify height, width explicitly.
        h = theDict.get("height",h)
        w = theDict.get("width",w)

        # if self.trace_gc: g.printNewObjects(tag='userIcon 2')

        return h,w
    #@+node:ekr.20081121110412.489: *6* drawTopTree (tk)
    def drawTopTree (self):

        """Draws the top-level tree, taking into account the hoist state."""

        c = self.c ; canvas = self.canvas
        trace = False or self.trace or self.trace_redraw

        self.redrawing = True

        # Recycle all widgets and clear all widget lists.
        self.recycleWidgets()
        # Clear all ids so invisible id's don't confuse eventToPosition & findPositionWithIconId
        self.ids = {}
        self.iconIds = {}
        self.generation += 1
        self.redrawCount += 1
        self.drag_p = None # Disable drags across redraws.
        self.dragging = False
        if trace:
            g.trace('redrawCount',self.redrawCount,g.callers(5))
                # 'len(c.hoistStack)',len(c.hoistStack))
            if 0:
                delta = g.app.positions - self.prevPositions
                g.trace("**** gen: %-3d positions: %5d +%4d" % (
                    self.generation,g.app.positions,delta),g.callers())

        self.prevPositions = g.app.positions
        if self.trace_gc: g.printNewObjects(tag='top 1')

        hoistFlag = c.hoistStack
        if c.hoistStack:
            bunch = c.hoistStack[-1] ; p = bunch.p
            h = p.h
            if len(c.hoistStack) == 1 and h.startswith('@chapter') and p.hasChildren():
                p = p.firstChild()
                hoistFlag = False
        else:
            p = c.rootPosition()

        self.drawTree(p,self.root_left,self.root_top,0,0,hoistFlag=hoistFlag)

        if self.trace_gc: g.printNewObjects(tag='top 2')
        if self.trace_stats: self.showStats()

        canvas.lower("lines")  # Lowest.
        canvas.lift("textBox") # Not the Tk.Text widget: it should be low.

        canvas.lift("clickBox")
        canvas.lift("clickExpandBox")
        canvas.lift("iconBox") # Higest. BJ:Not now
        canvas.lift("plusBox")
        canvas.lift("userIcon")
        self.redrawing = False
    #@+node:ekr.20081121110412.490: *6* drawTree
    def drawTree(self,p,x,y,h,level,hoistFlag=False):

        tree = self ; c = self.c
        yfirst = ylast = y ; h1 = None
        data = g.doHook("draw-sub-outline",tree=tree,
            c=c,p=p,v=p,x=x,y=y,h=h,level=level,hoistFlag=hoistFlag)
        if data is not None: return data

        while p: # Do not use iterator.
            # This is the ONLY copy of p that needs to be made;
            # no other drawing routine calls any p.moveTo method.
            const_p = p.copy()
            h,indent = self.drawNode(const_p,x,y)
            if h1 is None: h1 = h # Set h1 *after* calling drawNode.
            y += h ; ylast = y
            if p.isExpanded() and p.hasFirstChild():
                # Must make an additional copy here by calling firstChild.
                y = self.drawTree(p.firstChild(),x+indent,y,h,level+1)
            if hoistFlag: break
            else:         p = p.next()
        # Draw the vertical line.
        if h1 is None: h1 = h
        y2 = g.choose(level==0,yfirst+(h1-1)/2,yfirst-h1/2-1)
        self.drawLine(None,x,y2,x,ylast+self.hline_y-h)
        return y
    #@+node:ekr.20081121110412.491: *5* Helpers...
    #@+node:ekr.20081121110412.492: *6* getIconImage
    def getIconImage (self, name):

        # Return the image from the cache if possible.
        if name in self.iconimages:
            return self.iconimages[name]

        # g.trace(name)

        try:
            fullname = g.os_path_join(g.app.loadDir,"..","Icons",name)
            fullname = g.os_path_normpath(fullname)
            image = Tk.PhotoImage(master=self.canvas,file=fullname)
            self.iconimages[name] = image
            return image
        except:
            g.es("exception loading:",fullname)
            g.es_exception()
            return None
    #@+node:ekr.20081121110412.493: *6* inVisibleArea & inExpandedVisibleArea
    def inVisibleArea (self,y1):

        if self.allocateOnlyVisibleNodes:
            if self.visibleArea:
                vis1,vis2 = self.visibleArea
                y2 = y1 + self.line_height
                return y2 >= vis1 and y1 <= vis2
            else: return False
        else:
            return True # This forces all nodes to be allocated on all redraws.

    def inExpandedVisibleArea (self,y1):

        if self.expandedVisibleArea:
            vis1,vis2 = self.expandedVisibleArea
            y2 = y1 + self.line_height
            return y2 >= vis1 and y1 <= vis2
        else:
            return False
    #@+node:ekr.20081121110412.494: *6* numberOfVisibleNodes
    def numberOfVisibleNodes(self):

        c = self.c

        n = 0 ; p = self.c.rootPosition()
        while p:
            n += 1
            p.moveToVisNext(c)
        return n
    #@+node:ekr.20081121110412.495: *6* scrollTo
    def scrollTo(self,p=None):

        """Scrolls the canvas so that p is in view."""

        # This can be called at idle time, so there are shutdown issues.
        if g.app.quitting or self.drag_p or self.frame not in g.app.windowList:
            return
        if not hasattr(self,'c'):
            return

        c = self.c ; frame = c.frame ; trace = False
        if not p or not c.positionExists(p):
            p = c.currentPosition()
            if trace: g.trace('*** current position',p,p.stack)
        if not p or not c.positionExists(p):
            if trace: g.trace('current p does not exist',p)
            p = c.rootPosition()
        if not p or not c.positionExists(p):
            if trace: g.trace('no position')
            return
        try:
            if trace: g.trace('***',p,p.stack,'exists',c.positionExists(p))
            h1 = self.yoffset(p)
            if self.center_selected_tree_node: # New in Leo 4.4.3.
                #@+<< compute frac0 >>
                #@+node:ekr.20081121110412.496: *7* << compute frac0 >>
                # frac0 attempt to put the 
                scrollRegion = self.canvas.cget('scrollregion')
                geom = self.canvas.winfo_geometry()

                if scrollRegion and geom:
                    scrollRegion = scrollRegion.split(' ')
                    # if trace: g.trace('scrollRegion',repr(scrollRegion))
                    htot = int(scrollRegion[3])
                    wh,junk,junk = geom.split('+')
                    junk,h = wh.split('x')
                    if h: wtot = int(h)
                    else: wtot = 500
                    # if trace: g.trace('geom',geom,'wtot',wtot,'htot',htot)
                    if htot > 0.1:
                        frac0 = float(h1-wtot/2)/float(htot)
                        frac0 = max(min(frac0,1.0),0.0)
                    else:
                        frac0 = 0.0
                else:
                    frac0 = 0.0 ; htot = wtot = 0
                #@-<< compute frac0 >>
                delta = abs(self.prevMoveToFrac-frac0)
                if trace: g.trace('delta',delta)
                if delta > 0.0:
                    self.prevMoveToFrac = frac0
                    self.canvas.yview("moveto",frac0)
                    if trace: g.trace("frac0 %1.2f h1 %3d htot %3d wtot %3d" % (
                        frac0,h1,htot,wtot),g.callers())
            else:
                last = c.lastVisible()
                nextToLast = last.visBack(c)
                h2 = self.yoffset(last)
                #@+<< compute approximate line height >>
                #@+node:ekr.20081121110412.497: *7* << compute approximate line height >>
                if nextToLast: # 2/2/03: compute approximate line height.
                    lineHeight = h2 - self.yoffset(nextToLast)
                else:
                    lineHeight = 20 # A reasonable default.
                #@-<< compute approximate line height >>
                #@+<< Compute the fractions to scroll down/up >>
                #@+node:ekr.20081121110412.498: *7* << Compute the fractions to scroll down/up >>
                data = frame.canvas.leo_treeBar.get() # Get the previous values of the scrollbar.
                try: lo, hi = data
                except: lo,hi = 0.0,1.0

                # h1 and h2 are the y offsets of the present and last nodes.
                if h2 > 0.1:
                    frac = float(h1)/float(h2) # For scrolling down.
                    frac2 = float(h1+lineHeight/2)/float(h2) # For scrolling up.
                    frac2 = frac2 - (hi - lo)
                else:
                    frac = frac2 = 0.0 # probably any value would work here.

                frac =  max(min(frac,1.0),0.0)
                frac2 = max(min(frac2,1.0),0.0)
                #@-<< Compute the fractions to scroll down/up >>
                if frac <= lo: # frac is for scrolling down.
                    if self.prevMoveToFrac != frac:
                        self.prevMoveToFrac = frac
                        self.canvas.yview("moveto",frac)
                        if trace: g.trace("frac  %1.2f h1 %3d h2 %3d lo %1.2f hi %1.2f" % (
                            frac, h1,h2,lo,hi),g.callers())
                elif frac2 + (hi - lo) >= hi: # frac2 is for scrolling up.
                    if self.prevMoveToFrac != frac2:
                        self.prevMoveToFrac = frac2
                        self.canvas.yview("moveto",frac2)
                        if trace: g.trace("frac2 %1.2f h1 %3d h2 %3d lo %1.2f hi %1.2f" % (
                            frac2,h1,h2,lo,hi),g.callers())

            if self.allocateOnlyVisibleNodes:
                self.canvas.after_idle(self.idle_second_redraw)

            c.setTopVnode(p) # 1/30/04: remember a pseudo "top" node.

        except:
            g.es_exception()

    idle_scrollTo = scrollTo # For compatibility.
    #@+node:ekr.20081121110412.499: *6* yoffset (tkTree)
    #@+at We can't just return icony because the tree hasn't been redrawn yet.
    # For the same reason we can't rely on any TK canvas methods here.
    #@@c

    def yoffset(self,p1):
        # if not p1.isVisible(): g.pr("yoffset not visible:",p1)
        if not p1: return 0
        c = self.c
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            root = bunch.p.copy()
        else:
            root = self.c.rootPosition()
        if root:
            h,flag = self.yoffsetTree(root,p1,isTop=True)
            # flag can be False during initialization.
            # if not flag: g.pr("*** yoffset fails:",'root',root,'p1',p1,'returns',h)
            return h
        else:
            return 0

    def yoffsetTree(self,p,p1,isTop):
        c = self.c ; h = 0 ; trace = False ; verbose = True
        if trace: g.trace('entry','root',p,p.stack,'target',p1,p1.stack)
        if not c.positionExists(p):
            if trace: g.trace('*** does not exist',p.h)
            return h,False # An extra precaution.
        p = p.copy()
        if trace and verbose and isTop and c.hoistStack:
            g.trace('c.hoistStack',c.hoistStack[-1].p.h)
        if isTop and c.hoistStack:
            if p.firstChild():  theIter = [p.firstChild()]
            else:               theIter = []
        else:
            theIter = p.self_and_siblings()

        for p2 in theIter:
            if trace and p1.h == p2.h:
                g.trace('loop',p1,p2)
                g.trace(p1.stack,p2.stack)
            if p2 == p1:
                if trace and verbose: g.trace('returns',h,p1.h)
                return h, True
            h += self.line_height
            if p2.isExpanded() and p2.hasChildren():
                child = p2.firstChild()
                if trace and verbose: g.trace('recursive call')
                h2, flag = self.yoffsetTree(child,p1,isTop=False)
                h += h2
                if flag:
                    if trace and verbose: g.trace('returns',h,p1.h)
                    return h, True

        if trace: g.trace('not found',h,p1.h)
        return h, False
    #@+node:ekr.20081121110412.500: *5* tree.edraw_after methods (new)
    # We now use the definitions in the base leoTree class.

    # redraw_after_icons_changed  = redraw
    # redraw_after_clone          = redraw
    # redraw_after_contract       = redraw
    # redraw_after_delete         = redraw
    # redraw_after_expand         = redraw
    # redraw_after_insert         = redraw
    # redraw_after_move_down      = redraw
    # redraw_after_move_left      = redraw
    # redraw_after_move_right     = redraw
    # redraw_after_move_up        = redraw
    # redraw_after_select         = redraw
    #@+node:ekr.20081121110412.501: *4* Event handlers (tkTree)
    #@+node:ekr.20081121110412.502: *5* Helpers
    #@+node:ekr.20081121110412.503: *6* checkWidgetList
    def checkWidgetList (self,tag):

        return True # This will fail when the headline actually changes!
    #@+node:ekr.20081121110412.504: *6* dumpWidgetList
    def dumpWidgetList (self,tag):

        g.pr("\ncheckWidgetList: %s" % tag)

        for w in self.visibleText:

            p = w.leo_position
            if p:
                s = w.getAllText().strip()
                h = p.h.strip()

                addr = self.textAddr(w)
                g.pr("p:",addr,h)
                if h != s:
                    g.pr("w:",'*' * len(addr),s)
            else:
                g.pr("w.leo_position == None",w)
    #@+node:ekr.20081121110412.505: *6* tree.edit_widget
    def edit_widget (self,p):

        """Returns the Tk.Edit widget for position p."""

        return self.findEditWidget(p)
    #@+node:ekr.20081121110412.506: *6* eventToPosition
    def eventToPosition (self,event):

        canvas = self.canvas
        x,y = event.x,event.y
        x = canvas.canvasx(x) 
        y = canvas.canvasy(y)
        if self.trace: g.trace(x,y)
        item = canvas.find_overlapping(x,y,x,y)
        if not item: return None

        # Item may be a tuple, possibly empty.
        try:    theId = item[0]
        except: theId = item
        if not theId: return None

        p = self.ids.get(theId)

        # A kludge: p will be None for vertical lines.
        if not p:
            item = canvas.find_overlapping(x+1,y,x+1,y)
            try:    theId = item[0]
            except: theId = item
            if not theId:
                g.es_print('oops:','eventToPosition','failed')
                return None
            p = self.ids.get(theId)
            # g.trace("was vertical line",p)

        if self.trace and self.verbose:
            if p:
                w = self.findEditWidget(p)
                g.trace("%3d %3d %3d %d" % (theId,x,y,id(w)),p.h)
            else:
                g.trace("%3d %3d %3d" % (theId,x,y),None)

        # defensive programming: this copy is not needed.
        if p: return p.copy() # Make _sure_ nobody changes this table!
        else: return None
    #@+node:ekr.20081121110412.507: *6* findEditWidget (tkTree)
    def findEditWidget (self,p):

        """Return the Tk.Text item corresponding to p."""

        c = self.c ; trace = False

        # if trace: g.trace(g.callers())

        if p and c:
            # if trace: g.trace('h',p.h,'key',p.key())
            aTuple = self.visibleText.get(p.key())
            if aTuple:
                w,theId = aTuple
                # if trace: g.trace('id(p.v):',id(p.v),'%4d' % (theId),self.textAddr(w),p.h)
                return w
            else:
                if trace: g.trace('oops: not found',p,g.callers())
                return None

        if trace: g.trace('not found',p and p.h)
        return None
    #@+node:ekr.20081121110412.508: *6* findVnodeWithIconId
    def findPositionWithIconId (self,theId):

        # Due to an old bug, theId may be a tuple.
        try:
            data = self.iconIds.get(theId[0])
        except:
            data = self.iconIds.get(theId)

        if data:
            p,generation = data
            if generation==self.generation:
                if self.trace and self.verbose:
                    g.trace(theId,p.h)
                return p
            else:
                if self.trace and self.verbose:
                    g.trace("*** wrong generation: %d ***" % theId)
                return None
        else:
            if self.trace and self.verbose: g.trace(theId,None)
            return None
    #@+node:ekr.20081121110412.509: *5* Click Box...
    #@+node:ekr.20081121110412.510: *6* onClickBoxClick
    def onClickBoxClick (self,event,p=None):

        c = self.c ; p1 = c.currentPosition()

        if not p: p = self.eventToPosition(event)
        if not p: return

        c.setLog()

        if p and not g.doHook("boxclick1",c=c,p=p,v=p,event=event):
            c.endEditing()
            if p == p1 or self.initialClickExpandsOrContractsNode:
                if p.isExpanded(): p.contract()
                else:              p.expand()
            self.select(p)
            if c.frame.findPanel:
                c.frame.findPanel.handleUserClick(p)
            if self.stayInTree:
                c.treeWantsFocus()
            else:
                c.bodyWantsFocus()
        g.doHook("boxclick2",c=c,p=p,v=p,event=event)
        c.redraw()

        c.outerUpdate()
    #@+node:ekr.20081121110412.511: *6* onClickBoxRightClick
    def onClickBoxRightClick(self, event, p=None):
        #g.trace()
        return 'break'
    #@+node:ekr.20081121110412.512: *6* onPlusBoxRightClick
    def onPlusBoxRightClick (self,event,p=None):

        c = self.c

        self._block_canvas_menu = True

        if not p: p = self.eventToPosition(event)
        if not p: return

        self.OnActivateHeadline(p)
        self.endEditLabel()

        g.doHook('rclick-popup',c=c,p=p,event=event,context_menu='plusbox')

        c.outerUpdate()

        return 'break'
    #@+node:ekr.20081121110412.513: *5* Dragging (tkTree)
    #@+node:ekr.20081121110412.514: *6* endDrag
    def endDrag (self,event):

        """The official helper of the onEndDrag event handler."""

        c = self.c ; p = self.drag_p
        c.setLog()
        canvas = self.canvas
        if not event: return

        #@+<< set vdrag, childFlag >>
        #@+node:ekr.20081121110412.515: *7* << set vdrag, childFlag >>
        x,y = event.x,event.y
        canvas_x = canvas.canvasx(x)
        canvas_y = canvas.canvasy(y)

        theId = self.canvas.find_closest(canvas_x,canvas_y)
        # theId = self.canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)

        vdrag = self.findPositionWithIconId(theId)
        childFlag = vdrag and vdrag.hasChildren() and vdrag.isExpanded()
        #@-<< set vdrag, childFlag >>
        if self.allow_clone_drags:
            if not self.look_for_control_drag_on_mouse_down:
                self.controlDrag = c.frame.controlKeyIsDown

        redrawFlag = vdrag and vdrag.v != p.v
        if redrawFlag: # Disallow drag to joined node.
            #@+<< drag p to vdrag >>
            #@+node:ekr.20081121110412.516: *7* << drag p to vdrag >>
            # g.trace("*** end drag   ***",theId,x,y,p.h,vdrag.h)

            if self.controlDrag: # Clone p and move the clone.
                if childFlag:
                    c.dragCloneToNthChildOf(p,vdrag,0)
                else:
                    c.dragCloneAfter(p,vdrag)
            else: # Just drag p.
                if childFlag:
                    p = c.dragToNthChildOf(p,vdrag,0)
                else:
                    p = c.dragAfter(p,vdrag)
            #@-<< drag p to vdrag >>
        elif self.trace and self.verbose:
            g.trace("Cancel drag")

        # Reset the old cursor by brute force.
        self.canvas['cursor'] = "arrow"
        self.dragging = False
        self.drag_p = None

        # Must set self.drag_p = None first.
        if redrawFlag:
            c.redraw_now()
        c.recolor_now() # Dragging can affect coloring.

        # g.trace(redrawFlag)
    #@+node:ekr.20081121110412.517: *6* startDrag
    # This precomputes numberOfVisibleNodes(), a significant optimization.
    # We also indicate where findPositionWithIconId() should start looking for tree id's.

    def startDrag (self,event,p=None):

        """The official helper of the onDrag event handler."""

        c = self.c ; canvas = self.canvas

        if not p:
            assert(not self.drag_p)
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            theId = canvas.find_closest(x,y)
            # theId = canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)
            if theId is None: return
            try: theId = theId[0]
            except: pass
            p = self.ids.get(theId)
        if not p: return
        c.setLog()
        self.drag_p = p.copy() # defensive programming: not needed.
        self.dragging = True
        # g.trace("*** start drag ***",theId,self.drag_p.h)
        # Only do this once: greatly speeds drags.
        self.savedNumberOfVisibleNodes = self.numberOfVisibleNodes()
        # g.trace('self.controlDrag',self.controlDrag)
        if self.allow_clone_drags:
            self.controlDrag = c.frame.controlKeyIsDown
            if self.look_for_control_drag_on_mouse_down:
                if self.enable_drag_messages:
                    if self.controlDrag:
                        g.es("dragged node will be cloned")
                    else:
                        g.es("dragged node will be moved")
        else: self.controlDrag = False
        self.canvas['cursor'] = "hand2" # "center_ptr"
    #@+node:ekr.20081121110412.518: *6* onContinueDrag
    def onContinueDrag(self,event):

        c = self.c ; p = self.drag_p
        if not p: return

        try:
            canvas = self.canvas ; frame = c.frame
            if event:
                x,y = event.x,event.y
            else:
                x,y = frame.top.winfo_pointerx(),frame.top.winfo_pointery()
                # Stop the scrolling if we go outside the entire window.
                if x == -1 or y == -1: return 
            if self.dragging: # This gets cleared by onEndDrag()
                #@+<< scroll the canvas as needed >>
                #@+node:ekr.20081121110412.519: *7* << scroll the canvas as needed >>
                # Scroll the screen up or down one line if the cursor (y) is outside the canvas.
                h = canvas.winfo_height()

                if y < 0 or y > h:
                    lo, hi = frame.canvas.leo_treeBar.get()
                    n = self.savedNumberOfVisibleNodes
                    line_frac = 1.0 / float(n)
                    frac = g.choose(y < 0, lo - line_frac, lo + line_frac)
                    frac = min(frac,1.0)
                    frac = max(frac,0.0)
                    canvas.yview("moveto", frac)

                    # Queue up another event to keep scrolling while the cursor is outside the canvas.
                    lo, hi = frame.canvas.leo_treeBar.get()
                    if (y < 0 and lo > 0.1) or (y > h and hi < 0.9):
                        canvas.after_idle(self.onContinueDrag,None) # Don't propagate the event.
                #@-<< scroll the canvas as needed >>
        except:
            g.es_event_exception("continue drag")
    #@+node:ekr.20081121110412.520: *6* onDrag
    def onDrag(self,event):

        c = self.c ; p = self.drag_p
        if not event: return

        c.setLog()

        if not self.dragging:
            if not g.doHook("drag1",c=c,p=p,v=p,event=event):
                self.startDrag(event)
            g.doHook("drag2",c=c,p=p,v=p,event=event)

        if not g.doHook("dragging1",c=c,p=p,v=p,event=event):
            self.onContinueDrag(event)
        g.doHook("dragging2",c=c,p=p,v=p,event=event)
    #@+node:ekr.20081121110412.521: *6* onEndDrag
    def onEndDrag(self,event):

        """Tree end-of-drag handler called from vnode event handler."""

        c = self.c ; p = self.drag_p
        if not p: return

        c.setLog()

        if not g.doHook("enddrag1",c=c,p=p,v=p,event=event):
            self.endDrag(event)
        g.doHook("enddrag2",c=c,p=p,v=p,event=event)
    #@+node:ekr.20081121110412.522: *5* Icon Box...
    #@+node:ekr.20081121110412.523: *6* onIconBoxClick
    def onIconBoxClick (self,event,p=None):

        c = self.c ; tree = self

        if not p: p = self.eventToPosition(event)
        if not p:
            return

        c.setLog()

        if self.trace and self.verbose: g.trace()

        if not g.doHook("iconclick1",c=c,p=p,v=p,event=event):
            if event:
                self.onDrag(event)
            tree.endEditLabel()
            tree.select(p,scroll=False)
            if c.frame.findPanel:
                c.frame.findPanel.handleUserClick(p)
        g.doHook("iconclick2",c=c,p=p,v=p,event=event)

        return "break" # disable expanded box handling.
    #@+node:ekr.20081121110412.524: *6* onIconBoxRightClick
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        #g.trace()

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p:
            c.outerUpdate()
            return

        c.setLog()

        try:
            if not g.doHook("iconrclick1",c=c,p=p,v=p,event=event):
                self.OnActivateHeadline(p)
                self.endEditLabel()
                if not g.doHook('rclick-popup', c=c, p=p, event=event, context_menu='iconbox'):
                    self.OnPopup(p,event)
            g.doHook("iconrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")

        self._block_canvas_menu = True

        c.outerUpdate()
        return 'break'
    #@+node:ekr.20081121110412.525: *6* onIconBoxDoubleClick
    def onIconBoxDoubleClick (self,event,p=None):

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p:
            c.outerUpdate()
            return

        c.setLog()

        if self.trace and self.verbose: g.trace()

        try:
            if not g.doHook("icondclick1",c=c,p=p,v=p,event=event):
                self.endEditLabel() # Bug fix: 11/30/05
                self.OnIconDoubleClick(p) # Call the method in the base class.
            g.doHook("icondclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("icondclick")

        c.outerUpdate()
        return 'break'
    #@+node:ekr.20081121110412.526: *5* OnActivateHeadline (tkTree)
    def OnActivateHeadline (self,p,event=None):

        '''Handle common process when any part of a headline is clicked.'''

        # g.trace(p.h)

        returnVal = 'break' # Default: do nothing more.
        trace = False

        try:
            c = self.c
            c.setLog()
            #@+<< activate this window >>
            #@+node:ekr.20081121110412.527: *6* << activate this window >>
            if p == c.currentPosition():

                if trace: g.trace('current','active',self.active)
                self.editLabel(p) # sets focus.
                # If we are active, pass the event along so the click gets handled.
                # Otherwise, do *not* pass the event along so the focus stays the same.
                returnVal = g.choose(self.active,'continue','break')
                self.active = True
            else:
                if trace: g.trace("not current")
                self.select(p)
                w  = c.frame.body.bodyCtrl
                if c.frame.findPanel:
                    c.frame.findPanel.handleUserClick(p)
                if p.v.insertSpot != None:
                    spot = p.v.insertSpot
                    w.setInsertPoint(spot)
                    w.see(spot)
                else:
                    w.setInsertPoint(0)
                # An important detail.
                # The *canvas* (not the headline) gets the focus so that
                # tree bindings take priority over text bindings.
                c.treeWantsFocusNow() # Now. New in Leo 4.5.
                ### c.outerUpdate()
                self.active = False
                returnVal = 'break'
            #@-<< activate this window >>
        except:
            g.es_event_exception("activate tree")

        return returnVal
    #@+node:ekr.20081121110412.528: *5* Text Box...
    #@+node:ekr.20081121110412.529: *6* configureTextState
    def configureTextState (self,p):

        c = self.c

        if not p: return

        # g.trace(c.isCurrentPosition(p),self.c._currentPosition,p)

        if c.isCurrentPosition(p):
            if p == self.editPosition():
                self.setEditLabelState(p) # selected, editing.
            else:
                self.setSelectedLabelState(p) # selected, not editing.
        else:
            self.setUnselectedLabelState(p) # unselected
    #@+node:ekr.20081121110412.530: *6* onCtontrolT
    # This works around an apparent Tk bug.

    def onControlT (self,event=None):

        # If we don't inhibit further processing the Tx.Text widget switches characters!
        return "break"
    #@+node:ekr.20081121110412.531: *6* onHeadlineClick
    def onHeadlineClick (self,event,p=None):

        # g.trace('p',p)
        c = self.c ; w = event.widget

        if not p:
            try:
                p = w.leo_position
            except AttributeError:
                g.trace('*'*20,'oops')
        if not p: return 'break'

        # g.trace(g.app.gui.widget_name(w),p and p.h)

        c.setLog()

        try:
            if not g.doHook("headclick1",c=c,p=p,v=p,event=event):
                returnVal = self.OnActivateHeadline(p)
            g.doHook("headclick2",c=c,p=p,v=p,event=event)
        except:
            returnVal = 'break'
            g.es_event_exception("headclick")

        # 'continue' is sometimes correct here.
        # 'break' would make it impossible to unselect the headline text.
        # g.trace('returnVal',returnVal,'stayInTree',self.stayInTree)
        return returnVal
    #@+node:ekr.20081121110412.532: *6* onHeadlineRightClick
    def onHeadlineRightClick (self,event):

        """Handle a right click in any outline widget."""

        c = self.c ; w = event.widget

        try:
            p = w.leo_position
        except AttributeError:
            g.trace('*'*20,'oops')
            return 'break'

        c.setLog()

        try:
            if not g.doHook("headrclick1",c=c,p=p,v=p,event=event):
                self.OnActivateHeadline(p)
                self.endEditLabel()
                if not g.doHook('rclick-popup', c=c, p=p, event=event, context_menu='headline'):
                    self.OnPopup(p,event)
            g.doHook("headrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("headrclick")

        # 'continue' *is* correct here.
        # 'break' would make it impossible to unselect the headline text.

        return 'continue'
    #@+node:ekr.20081121110412.533: *5* tree.OnDeactivate
    def OnDeactivate (self,event=None):

        """Deactivate the tree pane, dimming any headline being edited."""

        tree = self ; c = self.c

        tree.endEditLabel()
        tree.dimEditLabel()
        c.outerUpdate()
    #@+node:ekr.20081121110412.534: *5* tree.OnPopup & allies
    def OnPopup (self,p,event):

        """Handle right-clicks in the outline.

        This is *not* an event handler: it is called from other event handlers."""

        # Note: "headrclick" hooks handled by vnode callback routine.

        if event != None:
            c = self.c
            c.setLog()

            if not g.doHook("create-popup-menu",c=c,p=p,v=p,event=event):
                self.createPopupMenu(event)
            if not g.doHook("enable-popup-menu-items",c=c,p=p,v=p,event=event):
                self.enablePopupMenuItems(p,event)
            if not g.doHook("show-popup-menu",c=c,p=p,v=p,event=event):
                self.showPopupMenu(event)

        return "break"
    #@+node:ekr.20081121110412.535: *6* OnPopupFocusLost
    #@+at
    # On Linux we must do something special to make the popup menu "unpost" if the
    # mouse is clicked elsewhere. So we have to catch the <FocusOut> event and
    # explicitly unpost. In order to process the <FocusOut> event, we need to be able
    # to find the reference to the popup window again, so this needs to be an
    # attribute of the tree object; hence, "self.popupMenu".
    # 
    # Aside: though Tk tries to be muli-platform, the interaction with different
    # window managers does cause small differences that will need to be compensated by
    # system specific application code. :-(
    #@@c

    # 20-SEP-2002 DTHEIN: This event handler is only needed for Linux.

    def OnPopupFocusLost(self,event=None):

        self.popupMenu.unpost()
    #@+node:ekr.20081121110412.536: *6* createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame


        self.popupMenu = menu = Tk.Menu(g.app.root, tearoff=0)

        # Add the Open With entries if they exist.
        if g.app.openWithTable:
            frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            table = (("-",None,None),)
            frame.menu.createMenuEntries(menu,table)

        #@+<< Create the menu table >>
        #@+node:ekr.20081121110412.537: *7* << Create the menu table >>
        table = (
            ("&Read @file Nodes",c.readAtFileNodes),
            ("&Write @file Nodes",c.fileCommands.writeAtFileNodes),
            ("-",None),
            ("&Tangle",c.tangle),
            ("&Untangle",c.untangle),
            ("-",None),
            ("Toggle Angle &Brackets",c.toggleAngleBrackets),
            ("-",None),
            ("Cut Node",c.cutOutline),
            ("Copy Node",c.copyOutline),
            ("&Paste Node",c.pasteOutline),
            ("&Delete Node",c.deleteOutline),
            ("-",None),
            ("&Insert Node",c.insertHeadline),
            ("&Clone Node",c.clone),
            ("Sort C&hildren",c.sortChildren),
            ("&Sort Siblings",c.sortSiblings),
            ("-",None),
            ("Contract Parent",c.contractParent),
        )
        #@-<< Create the menu table >>

        # New in 4.4.  There is no need for a dontBind argument because
        # Bindings from tables are ignored.
        frame.menu.createMenuEntries(menu,table)
    #@+node:ekr.20081121110412.538: *6* enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c ; menu = self.popupMenu

        #@+<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20081121110412.539: *7* << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        isAtFile = False
        isAtRoot = False

        for v2 in v.self_and_subtree():
            if isAtFile and isAtRoot:
                break
            if (v2.isAtFileNode() or
                v2.isAtAsisFileNode() or
                v2.isAtNoSentFileNode()
            ):
                isAtFile = True

            isRoot,junk = g.is_special(v2.bodyString(),0,"@root")
            if isRoot:
                isAtRoot = True
        #@-<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        isAtFile = g.choose(isAtFile,1,0)
        isAtRoot = g.choose(isAtRoot,1,0)
        canContract = v.parent() != None
        canContract = g.choose(canContract,1,0)

        enable = self.frame.menu.enableMenu

        for name in ("Read @file Nodes", "Write @file Nodes"):
            enable(menu,name,isAtFile)
        for name in ("Tangle", "Untangle"):
            enable(menu,name,isAtRoot)

        enable(menu,"Cut Node",c.canCutOutline())
        enable(menu,"Delete Node",c.canDeleteHeadline())
        enable(menu,"Paste Node",c.canPasteOutline())
        enable(menu,"Sort Children",c.canSortChildren())
        enable(menu,"Sort Siblings",c.canSortSiblings())
        enable(menu,"Contract Parent",c.canContractParent())
    #@+node:ekr.20081121110412.540: *6* showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        c = self.c ; menu = self.popupMenu

        g.app.gui.postPopupMenu(c, menu, event.x_root, event.y_root)

        self.popupMenu = None

        # Set the focus immediately so we know when we lose it.
        #c.widgetWantsFocus(menu)
    #@+node:ekr.20081121110412.541: *5* onTreeClick
    def onTreeClick (self,event=None):

        '''Handle an event in the tree canvas, outside of any tree widget.'''

        c = self.c

        # New in Leo 4.4.2: a kludge: disable later event handling after a double-click.
        # This allows focus to stick in newly-opened files opened by double-clicking an @url node.
        if c.doubleClickFlag:
            c.doubleClickFlag = False
        else:
            c.treeWantsFocus()

        g.app.gui.killPopupMenu()
        c.outerUpdate()

        return 'break'
    #@+node:ekr.20081121110412.542: *5* onTreeRightClick
    def onTreeRightClick (self,event=None):

        c = self.c

        if not c.exists: return

        if self._block_canvas_menu:
            self._block_canvas_menu = False
            return 'break'

        g.doHook('rclick-popup',c=c,event=event,context_menu='canvas')

        c.outerUpdate()
        return 'break'
    #@+node:ekr.20081121110412.543: *4* Incremental drawing...
    #@+node:ekr.20081121110412.544: *5* allocateNodes
    def allocateNodes(self,where,lines):

        """Allocate Tk widgets in nodes that will become visible as the result of an upcoming scroll"""

        assert(where in ("above","below"))

        # g.pr("allocateNodes: %d lines %s visible area" % (lines,where))

        # Expand the visible area: a little extra delta is safer.
        delta = lines * (self.line_height + 4)
        y1,y2 = self.visibleArea

        if where == "below":
            y2 += delta
        else:
            y1 = max(0.0,y1-delta)

        self.expandedVisibleArea=y1,y2
        # g.pr("expandedArea:   %5.1f %5.1f" % (y1,y2))

        # Allocate all nodes in expanded visible area.
        self.updatedNodeCount = 0
        self.updateTree(self.c.rootPosition(),self.root_left,self.root_top,0,0)
        # if self.updatedNodeCount: g.pr("updatedNodeCount:", self.updatedNodeCount)
    #@+node:ekr.20081121110412.545: *5* allocateNodesBeforeScrolling
    def allocateNodesBeforeScrolling (self, args):

        """Calculate the nodes that will become visible as the result of an upcoming scroll.

        args is the tuple passed to the Tk.Canvas.yview method"""

        if not self.allocateOnlyVisibleNodes: return

        # g.pr("allocateNodesBeforeScrolling:",self.redrawCount,args)

        assert(self.visibleArea)
        assert(len(args)==2 or len(args)==3)
        kind = args[0] ; n = args[1]
        lines = 2 # Update by 2 lines to account for rounding.
        if len(args) == 2:
            assert(kind=="moveto")
            frac1,frac2 = args
            if float(n) != frac1:
                where = g.choose(n<frac1,"above","below")
                self.allocateNodes(where=where,lines=lines)
        else:
            assert(kind=="scroll")
            linesPerPage = self.canvas.winfo_height()/self.line_height + 2
            n = int(n) ; assert(abs(n)==1)
            where = g.choose(n == 1,"below","above")
            lines = g.choose(args[2] == "pages",linesPerPage,lines)
            self.allocateNodes(where=where,lines=lines)
    #@+node:ekr.20081121110412.546: *5* updateNode
    def updateNode (self,p,x,y):

        """Draw a node that may have become visible as a result of a scrolling operation"""

        c = self.c

        if self.inExpandedVisibleArea(y):
            # This check is a major optimization.
            if not c.edit_widget(p):
                return self.force_draw_node(p,x,y)
            else:
                return self.line_height

        return self.line_height
    #@+node:ekr.20081121110412.547: *5* setVisibleAreaToFullCanvas
    def setVisibleAreaToFullCanvas(self):

        if self.visibleArea:
            y1,y2 = self.visibleArea
            y2 = max(y2,y1 + self.canvas.winfo_height())
            self.visibleArea = y1,y2
    #@+node:ekr.20081121110412.548: *5* setVisibleArea
    def setVisibleArea (self,args):

        r1,r2 = args
        r1,r2 = float(r1),float(r2)
        # g.pr("scroll ratios:",r1,r2)

        try:
            s = self.canvas.cget("scrollregion")
            x1,y1,x2,y2 = g.scanf(s,"%d %d %d %d")
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
        except:
            self.visibleArea = None
            return

        scroll_h = y2-y1
        # g.pr("height of scrollregion:", scroll_h)

        vy1 = y1 + (scroll_h*r1)
        vy2 = y1 + (scroll_h*r2)
        self.visibleArea = vy1,vy2
        # g.pr("setVisibleArea: %5.1f %5.1f" % (vy1,vy2))
    #@+node:ekr.20081121110412.549: *5* tree.updateTree
    def updateTree (self,v,x,y,h,level):

        yfirst = y
        if level==0: yfirst += 10
        while v:
            # g.trace(x,y,v)
            h,indent = self.updateNode(v,x,y)
            y += h
            if v.isExpanded() and v.firstChild():
                y = self.updateTree(v.firstChild(),x+indent,y,h,level+1)
            v = v.next()
        return y
    #@+node:ekr.20081121110412.550: *4* Selecting & editing... (tkTree)
    #@+node:ekr.20081121110412.551: *5* dimEditLabel, undimEditLabel
    # Convenience methods so the caller doesn't have to know the present edit node.

    def dimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)

    def undimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)
    #@+node:ekr.20081121110412.552: *5* tree.editLabel (tkTree)
    def editLabel (self,p,selectAll=False,selection=None):

        """Start editing p's headline."""

        trace = (False or self.trace_edit) and g.unitTesting
        c = self.c

        if p and p != self.editPosition():

            self.endEditLabel()
            # This redraw was formerly needed so that c.edit_widget(p)
            # would exist.  However, Leo's core now guarantees a redraw
            # before each call to c.editPosition.
            if 0:
                c.redraw()
                c.outerUpdate()

        self.setEditPosition(p) # That is, self._editPosition = p
        w = c.edit_widget(p)

        if p and w:
            if trace: g.trace('w',w,p)
            self.revertHeadline = p.h # New in 4.4b2: helps undo.
            self.setEditLabelState(p,selectAll=selectAll,selection=selection)
                # Sets the focus immediately.
            c.widgetWantsFocus(w)
            c.k.showStateAndMode(w)
        else:
            if trace: g.trace('*** Error: no edit widget for %s' % p)
    #@+node:ekr.20081121110412.553: *5* tree.set...LabelState
    #@+node:ekr.20081121110412.554: *6* setEditLabelState
    def setEditLabelState (self,p,selectAll=False,selection=None): # selected, editing

        c = self.c ; w = c.edit_widget(p)

        if p and w:
            c.widgetWantsFocusNow(w)
            self.setEditHeadlineColors(p)
            selectAll = selectAll or self.select_all_text_when_editing_headlines
            if selection:
                i,j,ins = selection
                w.setSelectionRange(i,j,insert=ins)
            elif selectAll:
                w.setSelectionRange(0,'end',insert='end')
            else:
                w.setInsertPoint('end') # Clears insert point.
        else:
            g.trace('no edit_widget')

    setNormalLabelState = setEditLabelState # For compatibility.
    #@+node:ekr.20081121110412.555: *6* setSelectedLabelState
    trace_n = 0

    def setSelectedLabelState (self,p): # selected, disabled

        c = self.c

        # g.trace(p,c.edit_widget(p))


        if p and c.edit_widget(p):

            if 0:
                g.trace(self.trace_n,c.edit_widget(p),p)
                # g.trace(g.callers(6))
                self.trace_n += 1

            self.setDisabledHeadlineColors(p)
    #@+node:ekr.20081121110412.556: *6* setUnselectedLabelState
    def setUnselectedLabelState (self,p): # not selected.

        c = self.c

        if p and c.edit_widget(p):
            self.setUnselectedHeadlineColors(p)
    #@+node:ekr.20081121110412.557: *6* setDisabledHeadlineColors
    def setDisabledHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if False or (self.trace and self.verbose):
            g.trace("%10s %d %s" % ("disabled",id(w),p.h))
            # import traceback ; traceback.print_stack(limit=6)

        fg = self.headline_text_selected_foreground_color or 'black'
        bg = self.headline_text_selected_background_color or 'grey80'
        selfg = self.headline_text_editing_selection_foreground_color
        selbg = self.headline_text_editing_selection_background_color

        try:
            w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg,
                selectbackground=bg,selectforeground=fg,highlightbackground=bg)
        except:
            g.es_exception()
    #@+node:ekr.20081121110412.558: *6* setEditHeadlineColors
    def setEditHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
                g.pr("%10s %d %s" % ("edit",id(2),p.h))

        fg    = self.headline_text_editing_foreground_color or 'black'
        bg    = self.headline_text_editing_background_color or 'white'
        selfg = self.headline_text_editing_selection_foreground_color or 'white'
        selbg = self.headline_text_editing_selection_background_color or 'black'

        try: # Use system defaults for selection foreground/background
            w.configure(state="normal",highlightthickness=1,
            fg=fg,bg=bg,selectforeground=selfg,selectbackground=selbg)
        except:
            g.es_exception()
    #@+node:ekr.20081121110412.559: *6* setUnselectedHeadlineColors
    def setUnselectedHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
                g.pr("%10s %d %s" % ("unselect",id(w),p.h))
                # import traceback ; traceback.print_stack(limit=6)

        fg = self.headline_text_unselected_foreground_color or 'black'
        bg = self.headline_text_unselected_background_color or 'white'

        try:
            w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg,
                selectbackground=bg,selectforeground=fg,highlightbackground=bg)
        except:
            g.es_exception()
    #@+node:ekr.20081121110412.560: *5* tree.setHeadline (tkTree)
    def setHeadline (self,p,s):

        '''Set the actual text of the headline widget.

        This is called from unit tests to restore the text before redrawing.'''

        w = self.edit_widget(p)
        if w:
            w.configure(state='normal')
            w.delete(0,'end')
            if s.endswith('\n') or s.endswith('\r'):
                s = s[:-1]
            w.insert(0,s)
            self.revertHeadline = s

        # else: g.trace('-'*20,'oops')
    #@-others
#@+node:ekr.20081121110412.307: *3* class leoTkinterTreeTab
class leoTkinterTreeTab (leoFrame.leoTreeTab):

    '''A class representing a tabbed outline pane drawn with Tkinter.'''

    #@+others
    #@+node:ekr.20081121110412.308: *4*  Birth & death
    #@+node:ekr.20081121110412.309: *5*  ctor (leoTreeTab)
    def __init__ (self,c,parentFrame,chapterController):

        leoFrame.leoTreeTab.__init__ (self,c,chapterController,parentFrame)
            # Init the base class.  Sets self.c, self.cc and self.parentFrame.

        self.tabNames = [] # The list of tab names.  Changes when tabs are renamed.

        self.createControl()
    #@+node:ekr.20081121110412.310: *5* tt.createControl
    def createControl (self):

        tt = self ; c = tt.c

        # Create the main container, possibly in a new row.
        tt.frame = c.frame.getNewIconFrame()

        # Create the chapter menu.
        self.chapterVar = var = Tk.StringVar()
        var.set('main')

        tt.chapterMenu = menu = Pmw.OptionMenu(tt.frame,
            labelpos = 'w', label_text = 'chapter',
            menubutton_textvariable = var,
            items = [],
            command = tt.selectTab,
        )
        menu.pack(side='left',padx=5)

        # Actually add tt.frame to the icon row.
        c.frame.addIconWidget(tt.frame)
    #@+node:ekr.20081121110412.311: *4* Tabs...
    #@+node:ekr.20081121110412.312: *5* tt.createTab
    def createTab (self,tabName,select=True):

        tt = self

        if tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@+node:ekr.20081121110412.313: *5* tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@+node:ekr.20081121110412.314: *5* tt.selectTab
    def selectTab (self,tabName):

        tt = self

        if tabName not in self.tabNames:
            tt.createTab(tabName)

        tt.cc.selectChapterByName(tabName)

        self.c.redraw()
        self.c.outerUpdate()
    #@+node:ekr.20081121110412.315: *5* tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self
        tt.chapterVar.set(tabName)
    #@+node:ekr.20081121110412.316: *5* tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt = self
        names = tt.tabNames[:]
        if 'main' in names: names.remove('main')
        names.sort()
        names.insert(0,'main')
    #@-others
#@+node:ekr.20081121110412.317: *3* class leoTkTextWidget (Tk.Text)
class leoTkTextWidget (Tk.Text):

    '''A class to wrap the Tk.Text widget.
    Translates Python (integer) indices to and from Tk (string) indices.

    This class inherits almost all tkText methods: you call use them as usual.'''

    # The signatures of tag_add and insert are different from the Tk.Text signatures.

    def __repr__(self):
        name = hasattr(self,'_name') and self._name or '<no name>'
        return 'leoTkTextWidget id: %s name: %s' % (id(self),name)

    #@+others
    #@+node:ekr.20081121110412.318: *4* bindings (not used)
    # Specify the names of widget-specific methods.
    # These particular names are the names of wx.TextCtrl methods.

    # def _appendText(self,s):            return self.widget.insert(s)
    # def _get(self,i,j):                 return self.widget.get(i,j)
    # def _getAllText(self):              return self.widget.get('1.0','end')
    # def _getFocus(self):                return self.widget.focus_get()
    # def _getInsertPoint(self):          return self.widget.index('insert')
    # def _getLastPosition(self):         return self.widget.index('end')
    # def _getSelectedText(self):         return self.widget.get('sel.start','sel.end')
    # def _getSelectionRange(self):       return self.widget.index('sel.start'),self.widget.index('sel.end')
    # def _hitTest(self,pos):             pass
    # def _insertText(self,i,s):          return self.widget.insert(i,s)
    # def _scrollLines(self,n):           pass
    # def _see(self,i):                   return self.widget.see(i)
    # def _setAllText(self,s):            self.widget.delete('1.0','end') ; self.widget.insert('1.0',s)
    # def _setBackgroundColor(self,color): return self.widget.configure(background=color)
    # def _setForegroundColor(self,color): return self.widget.configure(background=color)
    # def _setFocus(self):                return self.widget.focus_set()
    # def _setInsertPoint(self,i):        return self.widget.mark_set('insert',i)
    # def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)
    #@+node:ekr.20081121110412.319: *4* Index conversion (leoTextWidget)
    #@+node:ekr.20090320101733.12: *5* w.toPythonIndexToRowCol
    # New in Leo 4.6 b1.

    def toPythonIndexRowCol(self,index):

        w = self
        s = w.getAllText()
        i = w.toPythonIndex(index)
        row,col = g.convertPythonIndexToRowCol(s,i)
        return i,row,col
    #@+node:ekr.20081121110412.320: *5* w.toGuiIndex
    def toGuiIndex (self,i,s=None):
        '''Convert a Python index to a Tk index as needed.'''
        w = self
        if i is None:
            g.trace('can not happen: i is None',g.callers())
            return '1.0'
        elif type(i) == type(99):
            # The 's' arg supports the threaded colorizer.
            if s is None:
                # This *must* be 'end-1c', even if other code must change.
                s = Tk.Text.get(w,'1.0','end-1c')
            row,col = g.convertPythonIndexToRowCol(s,i)
            i = '%s.%s' % (row+1,col)
            # g.trace(len(s),i,repr(s))
        else:
            try:
                i = Tk.Text.index(w,i)
            except Exception:
                # g.es_exception()
                g.trace('Tk.Text.index failed:',repr(i),g.callers())
                i = '1.0'
        return i
    #@+node:ekr.20081121110412.321: *5* w.toPythonIndex
    def toPythonIndex (self,i):
        '''Convert a Tk index to a Python index as needed.'''
        w =self
        if i is None:
            g.trace('can not happen: i is None')
            return 0

        elif g.isString(i):
            s = Tk.Text.get(w,'1.0','end') # end-1c does not work.
            i = Tk.Text.index(w,i) # Convert to row/column form.
            row,col = i.split('.')
            row,col = int(row),int(col)
            row -= 1
            i = g.convertRowColToPythonIndex(s,row,col)
            #g.es_print('',i)
        return i
    #@+node:ekr.20081121110412.322: *5* w.rowColToGuiIndex
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return '%s.%s' % (row+1,col)
    #@+node:ekr.20100109114406.3729: *4* leoMoveCursorHelper (TK)
    def leoMoveCursorHelper (self,kind,extend=False,linesPerPage=15):

        '''Move the cursor in a QTextEdit.'''

        trace = False and not g.unitTesting
        w = self
        anchor = ins = Tk.Text.index(w,'insert')
        if hasattr(w,'leo_text_anchor') and w.leo_text_anchor:
            anchor = w.leo_text_anchor
        si,sj = ins.split('.')
        i,j = int(si),int(sj)
        d = {
            'exchange': True, # dummy
            'down':     '%s.%s' % (i+1,j),
            'end':      'end',
            'end-line': '%s.end' % (i),
            'home':     '1.0',
            'left':
                g.choose(j==0,
                    g.choose(i>1,'%s.end' % (i-1),'1.0'), # start of line.
                    '%s.%s' % (i,j-1)),
            'page-down':'%s.%s' % (i+linesPerPage,j),
            'page-up':  '%s.%s' % (max(1,i-linesPerPage),j),
            'right':
                g.choose(Tk.Text.compare(w,"%s.%s" % (i,j+1),">=",'%s.end' % (i)),
                    '%s.%s' % (i+1,0),
                    '%s.%s' % (i,j+1)),
            'start-line':'%s.0' % (i),
            'up':       '%s.%s' % (max(1,i-1),j),
        }

        kind = kind.lower()
        newIns = d.get(kind)
        if trace: g.trace('**Tk**',kind,'extend',extend,anchor,ins,newIns)

        if kind == 'exchange': # exchange-point-and-mark.
            if w.hasSelection():
                sel = Tk.Text.tag_ranges(w,"sel")
                i,j = sel
                # This is required for the unit test.
                anchor = g.choose(
                    hasattr(w,'leo_text_anchor') and w.leo_text_anchor,
                    w.leo_text_anchor,i)
                extend = True
                anchor,ins = ins,anchor
                newIns = ins
            else:
                w.leo_text_anchor = None
                return

        if newIns:
            Tk.Text.tag_remove(w,'sel','1.0','end')
            Tk.Text.mark_set(w,'insert',newIns)
            if extend:
                if Tk.Text.compare(w,anchor,'>',newIns):
                    Tk.Text.tag_add(w,'sel',newIns,anchor)
                else:
                    Tk.Text.tag_add(w,'sel',anchor,newIns)
                w.leo_text_anchor = anchor
            else:
                w.leo_text_anchor = None
        else:
            g.trace('can not happen: bad kind: %s' % kind)
    #@+node:ekr.20081121110412.323: *4* Wrapper methods (leoTextWidget)
    #@+node:ekr.20081121110412.324: *5* delete
    def delete(self,i,j=None):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            Tk.Text.delete(w,i)
        else:
            j = w.toGuiIndex(j)
            Tk.Text.delete(w,i,j)
    #@+node:ekr.20081121110412.325: *5* flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): # tkTextWidget.

        w = self

        def addFlashCallback(w,count,index):
            # g.trace(count,index)
            i,j = w.toGuiIndex(index),w.toGuiIndex(index+1)
            Tk.Text.tag_add(w,'flash',i,j)
            Tk.Text.after(w,delay,removeFlashCallback,w,count-1,index)

        def removeFlashCallback(w,count,index):
            # g.trace(count,index)
            Tk.Text.tag_remove(w,'flash','1.0','end')
            if count > 0:
                Tk.Text.after(w,delay,addFlashCallback,w,count,index)

        try:
            Tk.Text.tag_configure(w,'flash',foreground=fg,background=bg)
            addFlashCallback(w,flashes,i)
        except Exception:
            pass # g.es_exception()
    #@+node:ekr.20081121110412.326: *5* get
    def get(self,i,j=None):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            return Tk.Text.get(w,i)
        else:
            j = w.toGuiIndex(j)
            return Tk.Text.get(w,i,j)
    #@+node:ekr.20081121110412.327: *5* getAllText
    def getAllText (self): # tkTextWidget.

        """Return all the text of Tk.Text widget w converted to unicode."""

        w = self
        s = Tk.Text.get(w,"1.0","end-1c") # New in 4.4.1: use end-1c.

        if s is None:
            return g.u('')
        else:
            return g.toUnicode(s)
    #@+node:ekr.20081121110412.328: *5* getInsertPoint
    def getInsertPoint(self): # tkTextWidget.

        w = self
        i = Tk.Text.index(w,'insert')
        i = w.toPythonIndex(i)
        return i
    #@+node:ekr.20081121110412.329: *5* getName
    def getName (self):

        w = self
        return hasattr(w,'_name') and w._name or repr(w)
    #@+node:ekr.20081121110412.330: *5* getSelectedText
    def getSelectedText (self): # tkTextWidget.

        w = self
        i,j = w.getSelectionRange()
        if i != j:
            i,j = w.toGuiIndex(i),w.toGuiIndex(j)
            s = Tk.Text.get(w,i,j)
            return g.toUnicode(s)
        else:
            return g.u('')
    #@+node:ekr.20081121110412.331: *5* getSelectionRange
    def getSelectionRange (self,sort=True): # tkTextWidget.

        """Return a tuple representing the selected range.

        Return a tuple giving the insertion point if no range of text is selected."""

        w = self
        sel = Tk.Text.tag_ranges(w,"sel")
        if len(sel) == 2:
            i,j = sel
        else:
            i = j = Tk.Text.index(w,"insert")

        i,j = w.toPythonIndex(i),w.toPythonIndex(j)  
        if sort and i > j: i,j = j,i
        return i,j
    #@+node:ekr.20081121110412.332: *5* getWidth
    def getWidth (self):

        '''Return the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        return w.cget('width')
    #@+node:ekr.20081121110412.333: *5* getYScrollPosition
    def getYScrollPosition (self):

        w = self
        return w.yview()
    #@+node:ekr.20081121110412.334: *5* hasSelection
    def hasSelection (self):

        w = self
        i,j = w.getSelectionRange()
        return i != j
    #@+node:ekr.20081121110412.335: *5* indexIsVisible (tk)
    def indexIsVisible (self,i):

        w = self

        return w.dlineinfo(i)
    #@+node:ekr.20081121110412.336: *5* insert
    # The signature is more restrictive than the Tk.Text.insert method.

    def insert(self,i,s):

        w = self
        i = w.toGuiIndex(i)
        Tk.Text.insert(w,i,s)

    #@+node:ekr.20081121110412.338: *5* replace
    def replace (self,i,j,s): # tkTextWidget

        w = self
        i,j = w.toGuiIndex(i),w.toGuiIndex(j)

        Tk.Text.delete(w,i,j)
        Tk.Text.insert(w,i,s)
    #@+node:ekr.20081121110412.339: *5* see
    def see (self,i): # tkTextWidget.

        w = self
        i = w.toGuiIndex(i)
        Tk.Text.see(w,i)
    #@+node:ekr.20081121110412.340: *5* seeInsertPoint
    def seeInsertPoint (self): # tkTextWidget.

        w = self
        Tk.Text.see(w,'insert')
    #@+node:ekr.20081121110412.341: *5* selectAllText
    def selectAllText (self,insert=None): # tkTextWidget

        '''Select all text of the widget, *not* including the extra newline.'''

        w = self ; s = w.getAllText()
        if insert is None: insert = len(s)
        w.setSelectionRange(0,len(s),insert=insert)
    #@+node:ekr.20081121110412.342: *5* setAllText
    def setAllText (self,s,new_p=None): # tkTextWidget

        w = self

        state = Tk.Text.cget(w,"state")
        Tk.Text.configure(w,state="normal")

        Tk.Text.delete(w,'1.0','end')
        if s: Tk.Text.insert(w,'1.0',s) # The 'if s:' is a workaround for a fedora bug.

        Tk.Text.configure(w,state=state)
    #@+node:ekr.20081121110412.343: *5* setBackgroundColor & setForegroundColor
    def setBackgroundColor (self,color):

        w = self
        w.configure(background=color)

    def setForegroundColor (self,color):

        w = self
        w.configure(foreground=color)
    #@+node:ekr.20081121110412.344: *5* setInsertPoint
    def setInsertPoint (self,i): # tkTextWidget.

        w = self
        i = w.toGuiIndex(i)
        # g.trace(i,g.callers())
        Tk.Text.mark_set(w,'insert',i)
        w.leo_text_anchor = None

    #@+node:ekr.20081121110412.345: *5* setSelectionRange
    def setSelectionRange (self,i,j,insert=None): # tkTextWidget

        w = self

        i,j = w.toGuiIndex(i),w.toGuiIndex(j)

        # g.trace('i,j,insert',repr(i),repr(j),repr(insert),g.callers())

        # g.trace('i,j,insert',i,j,repr(insert))
        if Tk.Text.compare(w,i, ">", j): i,j = j,i
        Tk.Text.tag_remove(w,"sel","1.0",i)
        Tk.Text.tag_add(w,"sel",i,j)
        Tk.Text.tag_remove(w,"sel",j,"end")

        if insert is not None:
            w.setInsertPoint(insert)
    #@+node:ekr.20081121110412.346: *5* setWidth
    def setWidth (self,width):

        '''Set the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        w.configure(width=width)
    #@+node:ekr.20081121110412.347: *5* setYScrollPosition
    def setYScrollPosition (self,i):

        w = self
        w.yview('moveto',i)
    #@+node:ekr.20081121110412.348: *5* tag_add
    # The signature is slightly different than the Tk.Text.insert method.

    def tag_add(self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            Tk.Text.tag_add(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            Tk.Text.tag_add(w,tagName,i,j,*args)

    #@+node:ekr.20081121110412.349: *5* tag_ranges
    def tag_ranges(self,tagName):

        w = self
        aList = Tk.Text.tag_ranges(w,tagName)
        aList = [w.toPythonIndex(z) for z in aList]
        return tuple(aList)
    #@+node:ekr.20081121110412.350: *5* tag_remove
    # The signature is slightly different than the Tk.Text.insert method.

    def tag_remove (self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            Tk.Text.tag_remove(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            Tk.Text.tag_remove(w,tagName,i,j,*args)


    #@+node:ekr.20081121110412.351: *5* deleteTextSelection
    def deleteTextSelection (self): # tkTextWidget

        w = self
        sel = Tk.Text.tag_ranges(w,"sel")
        if len(sel) == 2:
            start,end = sel
            if Tk.Text.compare(w,start,"!=",end):
                Tk.Text.delete(w,start,end)
    #@+node:ekr.20081121110412.352: *5* xyToGui/PythonIndex
    def xyToGuiIndex (self,x,y): # tkTextWidget

        w = self
        return Tk.Text.index(w,"@%d,%d" % (x,y))

    def xyToPythonIndex(self,x,y): # tkTextWidget

        w = self
        i = Tk.Text.index(w,"@%d,%d" % (x,y))
        i = w.toPythonIndex(i)
        return i
    #@-others
#@-others
#@-leo

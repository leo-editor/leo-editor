#@+leo-ver=4-thin
#@+node:ekr.20080112145409.1:@thin leoGtkDialog.py
#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leo.core.leoGlobals as g
import string


import gtk
import cairo
import pango

#@+others
#@+node:ekr.20080112145409.2: class leoGtkDialog
class leoGtkDialog:
    """The base class for all Leo gtk dialogs"""
    #@    @+others
    #@+node:ekr.20080112145409.3:__init__ (tkDialog)
    def __init__(self,c,title="",resizeable=True,canClose=True,show=True):

        """Constructor for the leoGtkDialog class."""

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
        self.top = None # The toplevel widget.
        self.focus_widget = None # The widget to get the first focus.
        self.canClose = canClose
    #@-node:ekr.20080112145409.3:__init__ (tkDialog)
    #@+node:ekr.20080112145409.4:cancelButton, noButton, okButton, yesButton
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
    #@-node:ekr.20080112145409.4:cancelButton, noButton, okButton, yesButton
    #@+node:ekr.20080112145409.5:center
    def center(self):

        """Center any leoGtkDialog."""

        g.app.gui.center_dialog(self.top)
    #@-node:ekr.20080112145409.5:center
    #@+node:ekr.20080112145409.6:createButtons
    def createButtons (self,buttons):

        """Create a row of buttons.

        buttons is a list of dictionaries containing the properties of each button."""

        assert(self.frame)
        self.buttonsFrame = f = gtk.Frame(self.top)
        f.pack(side="top",padx=30)

        # Buttons is a list of dictionaries, with an empty dictionary at the end if there is only one entry.
        buttonList = []
        for d in buttons:
            text = d.get("text","<missing button name>")
            isDefault = d.get("default",False)
            underline = d.get("underline",0)
            command = d.get("command",None)
            bd = g.choose(isDefault,4,2)

            b = gtk.Button(f,width=6,text=text,bd=bd,underline=underline,command=command)
            b.pack(side="left",padx=5,pady=10)
            buttonList.append(b)

            if isDefault and command:
                self.defaultButtonCommand = command

        return buttonList
    #@-node:ekr.20080112145409.6:createButtons
    #@+node:ekr.20080112145409.7:createMessageFrame
    def createMessageFrame (self,message):

        """Create a frame containing a gtk.Label widget."""

        label = gtk.Label(self.frame,text=message)
        label.pack(pady=10)
    #@-node:ekr.20080112145409.7:createMessageFrame
    #@+node:ekr.20080112145409.8:createTopFrame
    def createTopFrame(self):

        """Create the top-level widget for a leoGtkDialog."""

        if g.app.unitTesting: return

        self.root = g.app.root
        # g.trace("leoGtkDialog",'root',self.root)

        self.top = gtk.Window() ### Tk.Toplevel(self.root)
        # self.top.title(self.title)

        if not self.resizeable:
            self.top.resizable(0,0) # neither height or width is resizable.

        self.frame = get.Frame() ### self.top)
        self.frame.pack(side="top",expand=1,fill="both")

        if not self.canClose:
            self.top.protocol("WM_DELETE_WINDOW", self.onClose)

        # Do this at idle time.
        def attachIconCallback(top=self.top):
            g.app.gui.attachLeoIcon(top)

        ### self.top.after_idle(attachIconCallback)
    #@-node:ekr.20080112145409.8:createTopFrame
    #@+node:ekr.20080112145409.9:onClose
    def onClose (self):

        """Disable all attempts to close this frame with the close box."""

        pass
    #@-node:ekr.20080112145409.9:onClose
    #@+node:ekr.20080112145409.10:run (gtkDialog)
    def run (self,modal):

        """Run a leoGtkDialog."""

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
            c.widgetWantsFocusNow(self.focus_widget)
            c.outerUpdate()

        self.root.wait_window(self.top)

        if self.modal:
            return self.answer
        else:
            return None
    #@-node:ekr.20080112145409.10:run (gtkDialog)
    #@-others
#@-node:ekr.20080112145409.2: class leoGtkDialog
#@+node:ekr.20080112145409.11:class gtkAboutLeo
class gtkAboutLeo (leoGtkDialog):

    """A class that creates the gtk About Leo dialog."""

    #@    @+others
    #@+node:ekr.20080112145409.12:gtkAboutLeo.__init__
    def __init__ (self,c,version,theCopyright,url,email):

        """Create a gtk About Leo dialog."""

        leoGtkDialog.__init__(self,c,"About Leo",resizeable=True) # Initialize the base class.

        if g.app.unitTesting: return

        self.copyright = theCopyright
        self.email = email
        self.url = url
        self.version = version

        c.inCommand = False # Allow the app to close immediately.

        self.createTopFrame()
        self.createFrame()
    #@-node:ekr.20080112145409.12:gtkAboutLeo.__init__
    #@+node:ekr.20080112145409.13:gtkAboutLeo.createFrame
    def createFrame (self):

        """Create the frame for an About Leo dialog."""

        if g.app.unitTesting: return

        frame = self.frame
        theCopyright = self.copyright ; email = self.email
        url = self.url ; version = self.version

        # Calculate the approximate height & width.
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

        # try:
            # bitmap_name = g.os_path_join(g.app.loadDir,"..","Icons","Leoapp.GIF") # 5/12/03
            # image = Tk.PhotoImage(file=bitmap_name)
            # w.image_create("1.0",image=image,padx=10)
        # except Exception:
            # pass # This can sometimes happen for mysterious reasons.

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
    #@-node:ekr.20080112145409.13:gtkAboutLeo.createFrame
    #@+node:ekr.20080112145409.14:gtkAboutLeo.onAboutLeoEmail
    def onAboutLeoEmail(self,event=None):

        """Handle clicks in the email link in an About Leo dialog."""

        try:
            import webbrowser
            webbrowser.open("mailto:" + self.email)
        except:
            g.es("not found:",self.email)
    #@-node:ekr.20080112145409.14:gtkAboutLeo.onAboutLeoEmail
    #@+node:ekr.20080112145409.15:gtkAboutLeo.onAboutLeoUrl
    def onAboutLeoUrl(self,event=None):

        """Handle clicks in the url link in an About Leo dialog."""

        try:
            import webbrowser
            webbrowser.open(self.url)
        except:
            g.es("not found:",self.url)
    #@-node:ekr.20080112145409.15:gtkAboutLeo.onAboutLeoUrl
    #@+node:ekr.20080112145409.16:gtkAboutLeo: setArrowCursor, setDefaultCursor
    def setArrowCursor (self,event=None):

        """Set the cursor to an arrow in an About Leo dialog."""

        self.text.configure(cursor="arrow")

    def setDefaultCursor (self,event=None):

        """Set the cursor to the default cursor in an About Leo dialog."""

        self.text.configure(cursor="xterm")
    #@-node:ekr.20080112145409.16:gtkAboutLeo: setArrowCursor, setDefaultCursor
    #@-others
#@-node:ekr.20080112145409.11:class gtkAboutLeo
#@+node:ekr.20080112145409.17:class gtkAskLeoID
class gtkAskLeoID (leoGtkDialog):

    """A class that creates the gtk About Leo dialog."""

    #@    @+others
    #@+node:ekr.20080112145409.18:gtkAskLeoID.__init__
    def __init__(self,c=None):

        """Create the Leo Id dialog."""

        # Initialize the base class: prevent clicks in the close box from closing.
        leoGtkDialog.__init__(self,c,"Enter unique id",resizeable=False,canClose=False)

        if g.app.unitTesting: return

        self.id_entry = None
        self.answer = None

        self.createTopFrame()
        c.bind(self.top,"<Key>", self.onKey)

        message = (
            "leoID.txt not found\n\n" +
            "Please enter an id that identifies you uniquely.\n" +
            "Your cvs login name is a good choice.\n\n" +
            "Your id must contain only letters and numbers\n" +
            "and must be at least 3 characters in length.")
        self.createFrame(message)
        self.focus_widget = self.id_entry

        buttons = {"text":"OK","command":self.onButton,"default":True}, # Singleton tuple.
        buttonList = self.createButtons(buttons)
        self.ok_button = buttonList[0]
        self.ok_button.configure(state="disabled")
    #@-node:ekr.20080112145409.18:gtkAskLeoID.__init__
    #@+node:ekr.20080112145409.19:gtkAskLeoID.createFrame
    def createFrame(self,message):

        """Create the frame for the Leo Id dialog."""

        if g.app.unitTesting: return

        f = self.frame

        label = gtk.Label(f,text=message)
        label.pack(pady=10)

        self.id_entry = text = gtk.Entry(f,width=20)
        text.pack()
    #@-node:ekr.20080112145409.19:gtkAskLeoID.createFrame
    #@+node:ekr.20080112145409.20:gtkAskLeoID.onButton
    def onButton(self):

        """Handle clicks in the Leo Id close button."""

        s = self.id_entry.get().strip()
        if len(s) < 3:  # Require at least 3 characters in an id.
            return

        self.answer = g.app.leoID = s

        self.top.destroy() # terminates wait_window
        self.top = None
    #@-node:ekr.20080112145409.20:gtkAskLeoID.onButton
    #@+node:ekr.20080112145409.21:gtkAskLeoID.onKey
    def onKey(self,event):

        """Handle keystrokes in the Leo Id dialog."""

        #@    << eliminate invalid characters >>
        #@+node:ekr.20080112145409.22:<< eliminate invalid characters >>
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
        #@-node:ekr.20080112145409.22:<< eliminate invalid characters >>
        #@nl
        #@    << enable the ok button if there are 3 or more valid characters >>
        #@+node:ekr.20080112145409.23:<< enable the ok button if there are 3 or more valid characters >>
        e = self.id_entry
        b = self.ok_button

        if len(e.get().strip()) >= 3:
            b.configure(state="normal")
        else:
            b.configure(state="disabled")
        #@-node:ekr.20080112145409.23:<< enable the ok button if there are 3 or more valid characters >>
        #@nl

        ch = event.char.lower()
        if ch in ('\n','\r'):
            self.onButton()
        return "break"
    #@-node:ekr.20080112145409.21:gtkAskLeoID.onKey
    #@-others
#@-node:ekr.20080112145409.17:class gtkAskLeoID
#@+node:ekr.20080112145409.24:class gtkAskOk
class gtkAskOk(leoGtkDialog):

    """A class that creates a gtk dialog with a single OK button."""

    #@    @+others
    #@+node:ekr.20080112145409.25:class gtkAskOk.__init__
    def __init__ (self,c,title,message=None,text="Ok",resizeable=False):

        """Create a dialog with one button"""

        leoGtkDialog.__init__(self,c,title,resizeable) # Initialize the base class.

        if g.app.unitTesting: return

        self.text = text
        self.createTopFrame()
        c.bind(self.top,"<Key>", self.onKey)

        if message:
            self.createMessageFrame(message)

        buttons = {"text":text,"command":self.okButton,"default":True}, # Singleton tuple.
        self.createButtons(buttons)
    #@-node:ekr.20080112145409.25:class gtkAskOk.__init__
    #@+node:ekr.20080112145409.26:class gtkAskOk.onKey
    def onKey(self,event):

        """Handle Key events in askOk dialogs."""

        ch = event.char.lower()

        if ch in (self.text[0].lower(),'\n','\r'):
            self.okButton()

        return "break"
    #@-node:ekr.20080112145409.26:class gtkAskOk.onKey
    #@-others
#@-node:ekr.20080112145409.24:class gtkAskOk
#@+node:ekr.20080112145409.27:class gtkAskOkCancelNumber
class  gtkAskOkCancelNumber (leoGtkDialog):

    """Create and run a modal gtk dialog to get a number."""

    #@    @+others
    #@+node:ekr.20080112145409.28:gtkAskOKCancelNumber.__init__
    def __init__ (self,c,title,message):

        """Create a number dialog"""

        leoGtkDialog.__init__(self,c,title,resizeable=False) # Initialize the base class.

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
    #@-node:ekr.20080112145409.28:gtkAskOKCancelNumber.__init__
    #@+node:ekr.20080112145409.29:gtkAskOKCancelNumber.createFrame
    def createFrame (self,message):

        """Create the frame for a number dialog."""

        if g.app.unitTesting: return

        c = self.c

        lab = gtk.Label(self.frame,text=message)
        lab.pack(pady=10,side="left")

        self.number_entry = w = gtk.Entry(self.frame,width=20)
        w.pack(side="left")

        c.set_focus(w)
    #@-node:ekr.20080112145409.29:gtkAskOKCancelNumber.createFrame
    #@+node:ekr.20080112145409.30:gtkAskOKCancelNumber.okButton, cancelButton
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
    #@-node:ekr.20080112145409.30:gtkAskOKCancelNumber.okButton, cancelButton
    #@+node:ekr.20080112145409.31:gtkAskOKCancelNumber.onKey
    def onKey (self,event):

        #@    << eliminate non-numbers >>
        #@+node:ekr.20080112145409.32:<< eliminate non-numbers >>
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
        #@-node:ekr.20080112145409.32:<< eliminate non-numbers >>
        #@nl

        ch = event.char.lower()

        if ch in ('o','\n','\r'):
            self.okButton()
        elif ch == 'c':
            self.cancelButton()

        return "break"
    #@-node:ekr.20080112145409.31:gtkAskOKCancelNumber.onKey
    #@-others
#@-node:ekr.20080112145409.27:class gtkAskOkCancelNumber
#@+node:ekr.20080112145409.33:class gtkAskOkCancelString
class  gtkAskOkCancelString (leoGtkDialog):

    """Create and run a modal gtk dialog to get a string."""

    #@    @+others
    #@+node:ekr.20080112145409.34:gtkAskOKCancelString.__init__
    def __init__ (self,c,title,message):

        """Create a number dialog"""

        leoGtkDialog.__init__(self,c,title,resizeable=False) # Initialize the base class.

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
    #@-node:ekr.20080112145409.34:gtkAskOKCancelString.__init__
    #@+node:ekr.20080112145409.35:gtkAskOkCancelString.createFrame
    def createFrame (self,message):

        """Create the frame for a number dialog."""

        if g.app.unitTesting: return

        c = self.c

        lab = gtk.Label(self.frame,text=message)
        lab.pack(pady=10,side="left")

        self.number_entry = w = gtk.Entry(self.frame,width=20)
        w.pack(side="left")

        c.set_focus(w)
    #@-node:ekr.20080112145409.35:gtkAskOkCancelString.createFrame
    #@+node:ekr.20080112145409.36:gtkAskOkCancelString.okButton, cancelButton
    def okButton(self):

        """Handle clicks in the ok button of a string dialog."""

        self.answer = self.number_entry.get().strip()
        self.top.destroy()

    def cancelButton(self):

        """Handle clicks in the cancel button of a string dialog."""

        self.answer=''
        self.top.destroy()
    #@-node:ekr.20080112145409.36:gtkAskOkCancelString.okButton, cancelButton
    #@+node:ekr.20080112145409.37:gtkAskOkCancelString.onKey
    def onKey (self,event):

        ch = event.char.lower()

        if ch in ('o','\n','\r'):
            self.okButton()
        elif ch == 'c':
            self.cancelButton()

        return "break"
    #@-node:ekr.20080112145409.37:gtkAskOkCancelString.onKey
    #@-others
#@-node:ekr.20080112145409.33:class gtkAskOkCancelString
#@+node:ekr.20080112145409.38:class gtkAskYesNo
class gtkAskYesNo (leoGtkDialog):

    """A class that creates a gtk dialog with two buttons: Yes and No."""

    #@    @+others
    #@+node:ekr.20080112145409.39:gtkAskYesNo.__init__
    def __init__ (self,c,title,message=None,resizeable=False):

        """Create a dialog having yes and no buttons."""

        leoGtkDialog.__init__(self,c,title,resizeable) # Initialize the base class.

        if g.app.unitTesting: return

        self.createTopFrame()
        c.bind(self.top,"<Key>",self.onKey)

        if message:
            self.createMessageFrame(message)

        buttons = (
            {"text":"Yes","command":self.yesButton,  "default":True},
            {"text":"No", "command":self.noButton} )
        self.createButtons(buttons)
    #@-node:ekr.20080112145409.39:gtkAskYesNo.__init__
    #@+node:ekr.20080112145409.40:gtkAskYesNo.onKey
    def onKey(self,event):

        """Handle keystroke events in dialogs having yes and no buttons."""

        ch = event.char.lower()

        if ch in ('y','\n','\r'):
            self.yesButton()
        elif ch == 'n':
            self.noButton()

        return "break"
    #@-node:ekr.20080112145409.40:gtkAskYesNo.onKey
    #@-others
#@-node:ekr.20080112145409.38:class gtkAskYesNo
#@+node:ekr.20080112145409.41:class gtkAskYesNoCancel
class gtkAskYesNoCancel(leoGtkDialog):

    """A class to create and run gtk dialogs having three buttons.

    By default, these buttons are labeled Yes, No and Cancel."""

    #@    @+others
    #@+node:ekr.20080112145409.42:askYesNoCancel.__init__
    def __init__ (self,c,title,
        message=None,
        yesMessage="Yes",
        noMessage="No",
        defaultButton="Yes",
        resizeable=False):

        """Create a dialog having three buttons."""

        leoGtkDialog.__init__(self,c,title,resizeable,canClose=False) # Initialize the base class.

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
    #@-node:ekr.20080112145409.42:askYesNoCancel.__init__
    #@+node:ekr.20080112145409.43:askYesNoCancel.onKey
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
    #@-node:ekr.20080112145409.43:askYesNoCancel.onKey
    #@+node:ekr.20080112145409.44:askYesNoCancel.noButton & yesButton
    def noButton(self):

        """Handle clicks in the 'no' (second) button in a dialog with three buttons."""

        self.answer=self.noMessage.lower()
        self.top.destroy()

    def yesButton(self):

        """Handle clicks in the 'yes' (first) button in a dialog with three buttons."""

        self.answer=self.yesMessage.lower()
        self.top.destroy()
    #@-node:ekr.20080112145409.44:askYesNoCancel.noButton & yesButton
    #@-others
#@-node:ekr.20080112145409.41:class gtkAskYesNoCancel
#@+node:ekr.20080112145409.45:class gtkListboxDialog
class gtkListBoxDialog (leoGtkDialog):

    """A base class for gtk dialogs containing a gtk Listbox"""

    #@    @+others
    #@+node:ekr.20080112145409.46:gtkListboxDialog.__init__
    def __init__ (self,c,title,label):

        """Constructor for the base listboxDialog class."""

        leoGtkDialog.__init__(self,c,title,resizeable=True) # Initialize the base class.

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
    #@-node:ekr.20080112145409.46:gtkListboxDialog.__init__
    #@+node:ekr.20080112145409.47:addStdButtons
    def addStdButtons (self,frame):

        """Add stanadard buttons to a listBox dialog."""

        # Create the ok and cancel buttons.
        self.ok = ok = gtk.Button(frame,text="Go",width=6,command=self.go)
        self.hide = hide = gtk.Button(frame,text="Hide",width=6,command=self.hide)

        ok.pack(side="left",pady=2,padx=5)
        hide.pack(side="left",pady=2,padx=5)
    #@-node:ekr.20080112145409.47:addStdButtons
    #@+node:ekr.20080112145409.48:createFrame
    def createFrame(self):

        """Create the essentials of a listBoxDialog frame

        Subclasses will add buttons to self.buttonFrame"""

        if g.app.unitTesting: return

        self.outerFrame = f = gtk.Frame(self.frame)
        f.pack(expand=1,fill="both")

        if self.label:
            labf = gtk.Frame(f)
            labf.pack(pady=2)
            lab = gtk.Label(labf,text=self.label)
            lab.pack()

        f2 = gtk.Frame(f)
        f2.pack(expand=1,fill="both")

        self.box = box = gtk.Listbox(f2,height=20,width=30)
        box.pack(side="left",expand=1,fill="both")

        bar = gtk.Scrollbar(f2)
        bar.pack(side="left", fill="y")

        bar.config(command=box.yview)
        box.config(yscrollcommand=bar.set)
    #@-node:ekr.20080112145409.48:createFrame
    #@+node:ekr.20080112145409.49:destroy
    def destroy (self,event=None):

        """Hide, do not destroy, a listboxDialog window

        subclasses may override to really destroy the window"""

        self.top.withdraw() # Don't allow this window to be destroyed.
    #@-node:ekr.20080112145409.49:destroy
    #@+node:ekr.20080112145409.50:hide
    def hide (self):

        """Hide a list box dialog."""

        self.top.withdraw()
    #@-node:ekr.20080112145409.50:hide
    #@+node:ekr.20080112145409.51:fillbox
    def fillbox(self,event=None):

        """Fill a listbox from information.

        Overridden by subclasses"""

        pass
    #@-node:ekr.20080112145409.51:fillbox
    #@+node:ekr.20080112145409.52:go
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
            c.frame.tree.expandAllAncestors(p)
            c.selectPosition(p,updateBeadList=True)
                # A case could be made for updateBeadList=False
            c.redraw()
    #@-node:ekr.20080112145409.52:go
    #@-others
#@-node:ekr.20080112145409.45:class gtkListboxDialog
#@+node:bob.20080116210510:class gtkFileDialog
#@-node:bob.20080116210510:class gtkFileDialog
#@-others
#@-node:ekr.20080112145409.1:@thin leoGtkDialog.py
#@-leo

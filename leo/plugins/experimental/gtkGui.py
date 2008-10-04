# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20080112150934:@thin experimental/gtkGui.py
#@@first

'''The plugin part of the gtk gui code.'''

# Important: Removed from leoPy.leo on 2008/10/4
# This code has not been tested since and will certainly not work as is.

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20081004102201.7:<< imports >>
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

try:
    import gtk
    import gobject
    import cairo
    import pango
except ImportError:
    gtk = None
    g.es_print('can not import gtk')
#@-node:ekr.20081004102201.7:<< imports >>
#@nl

#@+others
#@+node:ekr.20080112150934.1:init
def init():

    if g.app.unitTesting: # Not Ok for unit testing!
        return False

    if not gtk:
        return False

    if g.app.gui:
        return g.app.gui.guiName() == 'gtk'
    else:
        g.app.gui = leoGtkGui.gtkGui()
        # g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@-node:ekr.20080112150934.1:init
#@+node:ekr.20081004102201.8:gtkDialog
#@+node:ekr.20081004102201.9: class leoGtkDialog
class leoGtkDialog:
    """The base class for all Leo gtk dialogs"""
    #@    @+others
    #@+node:ekr.20081004102201.10:__init__ (tkDialog)
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
    #@-node:ekr.20081004102201.10:__init__ (tkDialog)
    #@+node:ekr.20081004102201.11:cancelButton, noButton, okButton, yesButton
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
    #@-node:ekr.20081004102201.11:cancelButton, noButton, okButton, yesButton
    #@+node:ekr.20081004102201.12:center
    def center(self):

        """Center any leoGtkDialog."""

        g.app.gui.center_dialog(self.top)
    #@-node:ekr.20081004102201.12:center
    #@+node:ekr.20081004102201.13:createButtons
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
    #@-node:ekr.20081004102201.13:createButtons
    #@+node:ekr.20081004102201.14:createMessageFrame
    def createMessageFrame (self,message):

        """Create a frame containing a gtk.Label widget."""

        label = gtk.Label(self.frame,text=message)
        label.pack(pady=10)
    #@-node:ekr.20081004102201.14:createMessageFrame
    #@+node:ekr.20081004102201.15:createTopFrame
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
    #@-node:ekr.20081004102201.15:createTopFrame
    #@+node:ekr.20081004102201.16:onClose
    def onClose (self):

        """Disable all attempts to close this frame with the close box."""

        pass
    #@-node:ekr.20081004102201.16:onClose
    #@+node:ekr.20081004102201.17:run (gtkDialog)
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
    #@-node:ekr.20081004102201.17:run (gtkDialog)
    #@-others
#@-node:ekr.20081004102201.9: class leoGtkDialog
#@+node:ekr.20081004102201.18:class gtkAboutLeo
class gtkAboutLeo (leoGtkDialog):

    """A class that creates the gtk About Leo dialog."""

    #@    @+others
    #@+node:ekr.20081004102201.19:gtkAboutLeo.__init__
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
    #@-node:ekr.20081004102201.19:gtkAboutLeo.__init__
    #@+node:ekr.20081004102201.20:gtkAboutLeo.createFrame
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
    #@-node:ekr.20081004102201.20:gtkAboutLeo.createFrame
    #@+node:ekr.20081004102201.21:gtkAboutLeo.onAboutLeoEmail
    def onAboutLeoEmail(self,event=None):

        """Handle clicks in the email link in an About Leo dialog."""

        try:
            import webbrowser
            webbrowser.open("mailto:" + self.email)
        except:
            g.es("not found:",self.email)
    #@-node:ekr.20081004102201.21:gtkAboutLeo.onAboutLeoEmail
    #@+node:ekr.20081004102201.22:gtkAboutLeo.onAboutLeoUrl
    def onAboutLeoUrl(self,event=None):

        """Handle clicks in the url link in an About Leo dialog."""

        try:
            import webbrowser
            webbrowser.open(self.url)
        except:
            g.es("not found:",self.url)
    #@-node:ekr.20081004102201.22:gtkAboutLeo.onAboutLeoUrl
    #@+node:ekr.20081004102201.23:gtkAboutLeo: setArrowCursor, setDefaultCursor
    def setArrowCursor (self,event=None):

        """Set the cursor to an arrow in an About Leo dialog."""

        self.text.configure(cursor="arrow")

    def setDefaultCursor (self,event=None):

        """Set the cursor to the default cursor in an About Leo dialog."""

        self.text.configure(cursor="xterm")
    #@-node:ekr.20081004102201.23:gtkAboutLeo: setArrowCursor, setDefaultCursor
    #@-others
#@-node:ekr.20081004102201.18:class gtkAboutLeo
#@+node:ekr.20081004102201.24:class gtkAskLeoID
class gtkAskLeoID (leoGtkDialog):

    """A class that creates the gtk About Leo dialog."""

    #@    @+others
    #@+node:ekr.20081004102201.25:gtkAskLeoID.__init__
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
    #@-node:ekr.20081004102201.25:gtkAskLeoID.__init__
    #@+node:ekr.20081004102201.26:gtkAskLeoID.createFrame
    def createFrame(self,message):

        """Create the frame for the Leo Id dialog."""

        if g.app.unitTesting: return

        f = self.frame

        label = gtk.Label(f,text=message)
        label.pack(pady=10)

        self.id_entry = text = gtk.Entry(f,width=20)
        text.pack()
    #@-node:ekr.20081004102201.26:gtkAskLeoID.createFrame
    #@+node:ekr.20081004102201.27:gtkAskLeoID.onButton
    def onButton(self):

        """Handle clicks in the Leo Id close button."""

        s = self.id_entry.get().strip()
        if len(s) < 3:  # Require at least 3 characters in an id.
            return

        self.answer = g.app.leoID = s

        self.top.destroy() # terminates wait_window
        self.top = None
    #@-node:ekr.20081004102201.27:gtkAskLeoID.onButton
    #@+node:ekr.20081004102201.28:gtkAskLeoID.onKey
    def onKey(self,event):

        """Handle keystrokes in the Leo Id dialog."""

        #@    << eliminate invalid characters >>
        #@+node:ekr.20081004102201.29:<< eliminate invalid characters >>
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
        #@-node:ekr.20081004102201.29:<< eliminate invalid characters >>
        #@nl
        #@    << enable the ok button if there are 3 or more valid characters >>
        #@+node:ekr.20081004102201.30:<< enable the ok button if there are 3 or more valid characters >>
        e = self.id_entry
        b = self.ok_button

        if len(e.get().strip()) >= 3:
            b.configure(state="normal")
        else:
            b.configure(state="disabled")
        #@-node:ekr.20081004102201.30:<< enable the ok button if there are 3 or more valid characters >>
        #@nl

        ch = event.char.lower()
        if ch in ('\n','\r'):
            self.onButton()
        return "break"
    #@-node:ekr.20081004102201.28:gtkAskLeoID.onKey
    #@-others
#@-node:ekr.20081004102201.24:class gtkAskLeoID
#@+node:ekr.20081004102201.31:class gtkAskOk
class gtkAskOk(leoGtkDialog):

    """A class that creates a gtk dialog with a single OK button."""

    #@    @+others
    #@+node:ekr.20081004102201.32:class gtkAskOk.__init__
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
    #@-node:ekr.20081004102201.32:class gtkAskOk.__init__
    #@+node:ekr.20081004102201.33:class gtkAskOk.onKey
    def onKey(self,event):

        """Handle Key events in askOk dialogs."""

        ch = event.char.lower()

        if ch in (self.text[0].lower(),'\n','\r'):
            self.okButton()

        return "break"
    #@-node:ekr.20081004102201.33:class gtkAskOk.onKey
    #@-others
#@-node:ekr.20081004102201.31:class gtkAskOk
#@+node:ekr.20081004102201.34:class gtkAskOkCancelNumber
class  gtkAskOkCancelNumber (leoGtkDialog):

    """Create and run a modal gtk dialog to get a number."""

    #@    @+others
    #@+node:ekr.20081004102201.35:gtkAskOKCancelNumber.__init__
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
    #@-node:ekr.20081004102201.35:gtkAskOKCancelNumber.__init__
    #@+node:ekr.20081004102201.36:gtkAskOKCancelNumber.createFrame
    def createFrame (self,message):

        """Create the frame for a number dialog."""

        if g.app.unitTesting: return

        c = self.c

        lab = gtk.Label(self.frame,text=message)
        lab.pack(pady=10,side="left")

        self.number_entry = w = gtk.Entry(self.frame,width=20)
        w.pack(side="left")

        c.set_focus(w)
    #@-node:ekr.20081004102201.36:gtkAskOKCancelNumber.createFrame
    #@+node:ekr.20081004102201.37:gtkAskOKCancelNumber.okButton, cancelButton
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
    #@-node:ekr.20081004102201.37:gtkAskOKCancelNumber.okButton, cancelButton
    #@+node:ekr.20081004102201.38:gtkAskOKCancelNumber.onKey
    def onKey (self,event):

        #@    << eliminate non-numbers >>
        #@+node:ekr.20081004102201.39:<< eliminate non-numbers >>
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
        #@-node:ekr.20081004102201.39:<< eliminate non-numbers >>
        #@nl

        ch = event.char.lower()

        if ch in ('o','\n','\r'):
            self.okButton()
        elif ch == 'c':
            self.cancelButton()

        return "break"
    #@-node:ekr.20081004102201.38:gtkAskOKCancelNumber.onKey
    #@-others
#@-node:ekr.20081004102201.34:class gtkAskOkCancelNumber
#@+node:ekr.20081004102201.40:class gtkAskOkCancelString
class  gtkAskOkCancelString (leoGtkDialog):

    """Create and run a modal gtk dialog to get a string."""

    #@    @+others
    #@+node:ekr.20081004102201.41:gtkAskOKCancelString.__init__
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
    #@-node:ekr.20081004102201.41:gtkAskOKCancelString.__init__
    #@+node:ekr.20081004102201.42:gtkAskOkCancelString.createFrame
    def createFrame (self,message):

        """Create the frame for a number dialog."""

        if g.app.unitTesting: return

        c = self.c

        lab = gtk.Label(self.frame,text=message)
        lab.pack(pady=10,side="left")

        self.number_entry = w = gtk.Entry(self.frame,width=20)
        w.pack(side="left")

        c.set_focus(w)
    #@-node:ekr.20081004102201.42:gtkAskOkCancelString.createFrame
    #@+node:ekr.20081004102201.43:gtkAskOkCancelString.okButton, cancelButton
    def okButton(self):

        """Handle clicks in the ok button of a string dialog."""

        self.answer = self.number_entry.get().strip()
        self.top.destroy()

    def cancelButton(self):

        """Handle clicks in the cancel button of a string dialog."""

        self.answer=''
        self.top.destroy()
    #@-node:ekr.20081004102201.43:gtkAskOkCancelString.okButton, cancelButton
    #@+node:ekr.20081004102201.44:gtkAskOkCancelString.onKey
    def onKey (self,event):

        ch = event.char.lower()

        if ch in ('o','\n','\r'):
            self.okButton()
        elif ch == 'c':
            self.cancelButton()

        return "break"
    #@-node:ekr.20081004102201.44:gtkAskOkCancelString.onKey
    #@-others
#@-node:ekr.20081004102201.40:class gtkAskOkCancelString
#@+node:ekr.20081004102201.45:class gtkAskYesNo
class gtkAskYesNo (leoGtkDialog):

    """A class that creates a gtk dialog with two buttons: Yes and No."""

    #@    @+others
    #@+node:ekr.20081004102201.46:gtkAskYesNo.__init__
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
    #@-node:ekr.20081004102201.46:gtkAskYesNo.__init__
    #@+node:ekr.20081004102201.47:gtkAskYesNo.onKey
    def onKey(self,event):

        """Handle keystroke events in dialogs having yes and no buttons."""

        ch = event.char.lower()

        if ch in ('y','\n','\r'):
            self.yesButton()
        elif ch == 'n':
            self.noButton()

        return "break"
    #@-node:ekr.20081004102201.47:gtkAskYesNo.onKey
    #@-others
#@-node:ekr.20081004102201.45:class gtkAskYesNo
#@+node:ekr.20081004102201.48:class gtkAskYesNoCancel
class gtkAskYesNoCancel(leoGtkDialog):

    """A class to create and run gtk dialogs having three buttons.

    By default, these buttons are labeled Yes, No and Cancel."""

    #@    @+others
    #@+node:ekr.20081004102201.49:askYesNoCancel.__init__
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
    #@-node:ekr.20081004102201.49:askYesNoCancel.__init__
    #@+node:ekr.20081004102201.50:askYesNoCancel.onKey
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
    #@-node:ekr.20081004102201.50:askYesNoCancel.onKey
    #@+node:ekr.20081004102201.51:askYesNoCancel.noButton & yesButton
    def noButton(self):

        """Handle clicks in the 'no' (second) button in a dialog with three buttons."""

        self.answer=self.noMessage.lower()
        self.top.destroy()

    def yesButton(self):

        """Handle clicks in the 'yes' (first) button in a dialog with three buttons."""

        self.answer=self.yesMessage.lower()
        self.top.destroy()
    #@-node:ekr.20081004102201.51:askYesNoCancel.noButton & yesButton
    #@-others
#@-node:ekr.20081004102201.48:class gtkAskYesNoCancel
#@+node:ekr.20081004102201.52:class gtkListboxDialog
class gtkListBoxDialog (leoGtkDialog):

    """A base class for gtk dialogs containing a gtk Listbox"""

    #@    @+others
    #@+node:ekr.20081004102201.53:gtkListboxDialog.__init__
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
    #@-node:ekr.20081004102201.53:gtkListboxDialog.__init__
    #@+node:ekr.20081004102201.54:addStdButtons
    def addStdButtons (self,frame):

        """Add stanadard buttons to a listBox dialog."""

        # Create the ok and cancel buttons.
        self.ok = ok = gtk.Button(frame,text="Go",width=6,command=self.go)
        self.hide = hide = gtk.Button(frame,text="Hide",width=6,command=self.hide)

        ok.pack(side="left",pady=2,padx=5)
        hide.pack(side="left",pady=2,padx=5)
    #@-node:ekr.20081004102201.54:addStdButtons
    #@+node:ekr.20081004102201.55:createFrame
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
    #@-node:ekr.20081004102201.55:createFrame
    #@+node:ekr.20081004102201.56:destroy
    def destroy (self,event=None):

        """Hide, do not destroy, a listboxDialog window

        subclasses may override to really destroy the window"""

        self.top.withdraw() # Don't allow this window to be destroyed.
    #@-node:ekr.20081004102201.56:destroy
    #@+node:ekr.20081004102201.57:hide
    def hide (self):

        """Hide a list box dialog."""

        self.top.withdraw()
    #@-node:ekr.20081004102201.57:hide
    #@+node:ekr.20081004102201.58:fillbox
    def fillbox(self,event=None):

        """Fill a listbox from information.

        Overridden by subclasses"""

        pass
    #@-node:ekr.20081004102201.58:fillbox
    #@+node:ekr.20081004102201.59:go
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
            c.selectPosition(p)
            c.redraw()
    #@-node:ekr.20081004102201.59:go
    #@-others
#@-node:ekr.20081004102201.52:class gtkListboxDialog
#@+node:ekr.20081004102201.60:class gtkFileDialog
#@-node:ekr.20081004102201.60:class gtkFileDialog
#@-node:ekr.20081004102201.8:gtkDialog
#@+node:ekr.20081004102201.61:gtkFind
#@+node:ekr.20081004102201.62:class underlinedGtkButton
class underlinedGtkButton:

    #@    @+others
    #@+node:ekr.20081004102201.63:__init__
    def __init__(self,buttonType,parent_widget,**keywords):

        self.buttonType = buttonType
        self.parent_widget = parent_widget
        self.hotKey = None
        text = keywords['text']

        #@    << set self.hotKey if '&' is in the string >>
        #@+node:ekr.20081004102201.64:<< set self.hotKey if '&' is in the string >>
        index = text.find('&')

        if index > -1:

            if index == len(text)-1:
                # The word ends in an ampersand.  Ignore it; there is no hot key.
                text = text[:-1]
            else:
                self.hotKey = text [index + 1]
                text = text[:index] + text[index+1:]
        #@-node:ekr.20081004102201.64:<< set self.hotKey if '&' is in the string >>
        #@nl

        # Create the button...
        if self.hotKey:
            keywords['text'] = text
            keywords['underline'] = index

        if buttonType.lower() == "button":
            self.button = gtk.Button(parent_widget,keywords)
        elif buttonType.lower() == "check":
            self.button = gtk.Checkbutton(parent_widget,keywords)
        elif buttonType.lower() == "radio":
            self.button = gtk.Radiobutton(parent_widget,keywords)
        else:
            g.trace("bad buttonType")

        self.text = text # for traces
    #@-node:ekr.20081004102201.63:__init__
    #@+node:ekr.20081004102201.65:bindHotKey
    def bindHotKey (self,widget):

        if self.hotKey:
            for key in (self.hotKey.lower(),self.hotKey.upper()):
                widget.bind("<Alt-%s>" % key,self.buttonCallback)
    #@-node:ekr.20081004102201.65:bindHotKey
    #@+node:ekr.20081004102201.66:buttonCallback
    # The hot key has been hit.  Call the button's command.

    def buttonCallback (self, event=None):

        # g.trace(self.text)
        self.button.invoke ()

        # See if this helps.
        return 'break'
    #@-node:ekr.20081004102201.66:buttonCallback
    #@-others
#@-node:ekr.20081004102201.62:class underlinedGtkButton
#@+node:ekr.20081004102201.67:class gtkFindTab (findTab)
class gtkFindTab (leoFind.findTab):

    '''A subclass of the findTab class containing all gtk code.'''

    #@    @+others
    #@+node:ekr.20081004102201.68: Birth
    if 0: # We can use the base-class ctor.

        def __init__ (self,c,parentFrame):

            leoFind.findTab.__init__(self,c,parentFrame)
                # Init the base class.
                # Calls initGui, createFrame, createBindings & init(c), in that order.
    #@+node:ekr.20081004102201.69:initGui
    def initGui (self):

        self.svarDict = {}

        for key in self.intKeys:
            self.svarDict[key] = gtk.IntVar()

        for key in self.newStringKeys:
            self.svarDict[key] = gtk.StringVar()

    #@-node:ekr.20081004102201.69:initGui
    #@+node:ekr.20081004102201.70:createFrame (tkFindTab)
    def createFrame (self,parentFrame):

        c = self.c

        # g.trace('findTab')

        #@    << Create the outer frames >>
        #@+node:ekr.20081004102201.71:<< Create the outer frames >>
        configName = 'log_pane_Find_tab_background_color'
        bg = c.config.getColor(configName) or 'MistyRose1'

        parentFrame.configure(background=bg)

        self.top = gtk.Frame(parentFrame,background=bg)
        self.top.pack(side='top',expand=0,fill='both',pady=5)
            # Don't expand, so the frame goes to the top.

        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(relief='flat',background=bg)
        #@-node:ekr.20081004102201.71:<< Create the outer frames >>
        #@nl
        #@    << Create the Find and Change panes >>
        #@+node:ekr.20081004102201.72:<< Create the Find and Change panes >>
        fc = gtk.Frame(outer, bd="1m",background=bg)
        fc.pack(anchor="n", fill="x", expand=1)

        # Removed unused height/width params: using fractions causes problems in some locales!
        fpane = gtk.Frame(fc, bd=1,background=bg)
        cpane = gtk.Frame(fc, bd=1,background=bg)

        fpane.pack(anchor="n", expand=1, fill="x")
        cpane.pack(anchor="s", expand=1, fill="x")

        # Create the labels and text fields...
        flab = gtk.Label(fpane, width=8, text="Find:",background=bg)
        clab = gtk.Label(cpane, width=8, text="Change:",background=bg)

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
        #@<< Bind Tab and control-tab >>
        #@+node:ekr.20081004102201.73:<< Bind Tab and control-tab >>
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
        #@-node:ekr.20081004102201.73:<< Bind Tab and control-tab >>
        #@nl

        if 0: # Add scrollbars.
            fBar = gtk.Scrollbar(fpane,name='findBar')
            cBar = gtk.Scrollbar(cpane,name='changeBar')

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
        #@-node:ekr.20081004102201.72:<< Create the Find and Change panes >>
        #@nl
        #@    << Create two columns of radio and checkboxes >>
        #@+node:ekr.20081004102201.74:<< Create two columns of radio and checkboxes >>
        columnsFrame = gtk.Frame(outer,relief="groove",bd=2,background=bg)

        columnsFrame.pack(expand=0,padx="7p",pady="2p")

        numberOfColumns = 2 # Number of columns
        columns = [] ; radioLists = [] ; checkLists = []
        for i in range(numberOfColumns):
            columns.append(gtk.Frame(columnsFrame,bd=1))
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
        #@-node:ekr.20081004102201.74:<< Create two columns of radio and checkboxes >>
        #@nl

        if  self.optionsOnly:
            buttons = []
        else:
            #@        << Create two columns of buttons >>
            #@+node:ekr.20081004102201.75:<< Create two columns of buttons >>
            # Create the alignment panes.
            buttons  = gtk.Frame(outer,background=bg)
            buttons1 = gtk.Frame(buttons,bd=1,background=bg)
            buttons2 = gtk.Frame(buttons,bd=1,background=bg)
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
            #@-node:ekr.20081004102201.75:<< Create two columns of buttons >>
            #@nl

        # Pack this last so buttons don't get squashed when frame is resized.
        self.outerScrolledFrame.pack(side='top',expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20081004102201.70:createFrame (tkFindTab)
    #@+node:ekr.20081004102201.76:createBindings (tkFindTab)
    def createBindings (self):

        c = self.c ; k = c.k

        def resetWrapCallback(event,self=self,k=k):
            self.resetWrap(event)
            return k.masterKeyHandler(event)

        def findButtonBindingCallback(event=None,self=self):
            self.findButton()
            return 'break'

        table = (
            ('<Button-1>',  k.masterClickHandler),
            ('<Double-1>',  k.masterClickHandler),
            ('<Button-3>',  k.masterClickHandler),
            ('<Double-3>',  k.masterClickHandler),
            ('<Key>',       resetWrapCallback),
            ('<Return>',    findButtonBindingCallback),
            ("<Escape>",    self.hideTab),
        )

        for w in (self.find_ctrl,self.change_ctrl):
            for event, callback in table:
                c.bind(w,event,callback)
    #@-node:ekr.20081004102201.76:createBindings (tkFindTab)
    #@+node:ekr.20081004102201.77:tkFindTab.init
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

        #@    << set find/change widgets >>
        #@+node:ekr.20081004102201.78:<< set find/change widgets >>
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
        #@-node:ekr.20081004102201.78:<< set find/change widgets >>
        #@nl
        #@    << set radio buttons from ivars >>
        #@+node:ekr.20081004102201.79:<< set radio buttons from ivars >>
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
        #@-node:ekr.20081004102201.79:<< set radio buttons from ivars >>
        #@nl
    #@-node:ekr.20081004102201.77:tkFindTab.init
    #@-node:ekr.20081004102201.68: Birth
    #@+node:ekr.20081004102201.80:Support for minibufferFind class (tkFindTab)
    #@+node:ekr.20081004102201.81:getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('%s = %s' % (ivar,val))
            return val
        else:
            g.trace('bad ivar name: %s' % ivar)
            return None
    #@-node:ekr.20081004102201.81:getOption
    #@+node:ekr.20081004102201.82:setOption
    def setOption (self,ivar,val):

        if ivar in self.intKeys:
            if val is not None:
                var = self.svarDict.get(ivar)
                var.set(val)
                # g.trace('%s = %s' % (ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20081004102201.82:setOption
    #@+node:ekr.20081004102201.83:toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20081004102201.83:toggleOption
    #@-node:ekr.20081004102201.80:Support for minibufferFind class (tkFindTab)
    #@-others
#@nonl
#@-node:ekr.20081004102201.67:class gtkFindTab (findTab)
#@+node:ekr.20081004102201.84:class gtkSpellTab
class gtkSpellTab:

    #@    @+others
    #@+node:ekr.20081004102201.85:gtkSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        self.c = c
        self.handler = handler
        self.tabName = tabName
        self.change_i, change_j = None,None
        self.createFrame()
        self.createBindings()
        self.fillbox([])
    #@-node:ekr.20081004102201.85:gtkSpellTab.__init__
    #@+node:ekr.20081004102201.86:createBindings
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

        c.bind(self.listBox,"<Double-1>",self.onChangeThenFindButton)
        c.bind(self.listBox,"<Button-1>",self.onSelectListBox)
        c.bind(self.listBox,"<Map>",self.onMap)
    #@nonl
    #@-node:ekr.20081004102201.86:createBindings
    #@+node:ekr.20081004102201.87:createFrame
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

        #@    << Create the outer frames >>
        #@+node:ekr.20081004102201.88:<< Create the outer frames >>
        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(
                relief='flat',background=bg)
        #@-node:ekr.20081004102201.88:<< Create the outer frames >>
        #@nl
        #@    << Create the text and suggestion panes >>
        #@+node:ekr.20081004102201.89:<< Create the text and suggestion panes >>
        f2 = gtk.Frame(outer,bg=bg)
        f2.pack(side='top',expand=0,fill='x')

        self.wordLabel = gtk.Label(f2,text="Suggestions for:")
        self.wordLabel.pack(side='left')

        if setFont:
            self.wordLabel.configure(font=('verdana',fontSize,'bold'))

        fpane = gtk.Frame(outer,bg=bg,bd=2)
        fpane.pack(side='top',expand=1,fill='both')

        self.listBox = gtk.Listbox(fpane,height=6,width=10,selectmode="single")
        self.listBox.pack(side='left',expand=1,fill='both')
        if setFont:
            self.listBox.configure(font=('verdana',fontSize,'normal'))

        listBoxBar = gtk.Scrollbar(fpane,name='listBoxBar')

        bar, txt = listBoxBar, self.listBox
        txt ['yscrollcommand'] = bar.set
        bar ['command'] = txt.yview
        bar.pack(side='right',fill='y')
        #@-node:ekr.20081004102201.89:<< Create the text and suggestion panes >>
        #@nl
        #@    << Create the spelling buttons >>
        #@+node:ekr.20081004102201.90:<< Create the spelling buttons >>
        # Create the alignment panes
        buttons1 = gtk.Frame(outer,bd=1,bg=bg)
        buttons2 = gtk.Frame(outer,bd=1,bg=bg)
        buttons3 = gtk.Frame(outer,bd=1,bg=bg)
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
                b = gtk.Button(frame,font=font,width=width,text=text,command=command)
            else:
                b = gtk.Button(frame,width=width,text=text,command=command)
            b.pack(side='left',expand=0,fill='none')
            buttonList.append(b)

        # Used to enable or disable buttons.
        (self.findButton,self.addButton,
         self.changeButton, self.changeFindButton,
         self.ignoreButton, self.hideButton) = buttonList
        #@-node:ekr.20081004102201.90:<< Create the spelling buttons >>
        #@nl

        # Pack last so buttons don't get squished.
        self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20081004102201.87:createFrame
    #@+node:ekr.20081004102201.91:Event handlers
    #@+node:ekr.20081004102201.92:onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20081004102201.92:onAddButton
    #@+node:ekr.20081004102201.93:onChangeButton & onChangeThenFindButton
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
    #@-node:ekr.20081004102201.93:onChangeButton & onChangeThenFindButton
    #@+node:ekr.20081004102201.94:onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocusNow()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20081004102201.94:onFindButton
    #@+node:ekr.20081004102201.95:onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20081004102201.95:onHideButton
    #@+node:ekr.20081004102201.96:onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
        self.change_i, self.change_j = None,None
    #@nonl
    #@-node:ekr.20081004102201.96:onIgnoreButton
    #@+node:ekr.20081004102201.97:onMap
    def onMap (self, event=None):
        """Respond to a gtk <Map> event."""

        # self.update(show= False, fill= False)
        self.updateButtons()
    #@-node:ekr.20081004102201.97:onMap
    #@+node:ekr.20081004102201.98:onSelectListBox
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
    #@-node:ekr.20081004102201.98:onSelectListBox
    #@-node:ekr.20081004102201.91:Event handlers
    #@+node:ekr.20081004102201.99:Helpers
    #@+node:ekr.20081004102201.100:bringToFront
    def bringToFront (self):

        # g.trace('tkSpellTab',g.callers())
        self.c.frame.log.selectTab('Spell')
    #@-node:ekr.20081004102201.100:bringToFront
    #@+node:ekr.20081004102201.101:fillbox
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
    #@-node:ekr.20081004102201.101:fillbox
    #@+node:ekr.20081004102201.102:getSuggestion
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
    #@-node:ekr.20081004102201.102:getSuggestion
    #@+node:ekr.20081004102201.103:updateButtons (spellTab)
    def updateButtons (self):

        """Enable or disable buttons in the Check Spelling dialog."""

        c = self.c ; w = c.frame.body.bodyCtrl

        start, end = w.getSelectionRange()
        state = g.choose(self.suggestions and start,"normal","disabled")

        self.changeButton.configure(state=state)
        self.changeFindButton.configure(state=state)

        # state = g.choose(self.c.undoer.canRedo(),"normal","disabled")
        # self.redoButton.configure(state=state)
        # state = g.choose(self.c.undoer.canUndo(),"normal","disabled")
        # self.undoButton.configure(state=state)

        self.addButton.configure(state='normal')
        self.ignoreButton.configure(state='normal')
    #@-node:ekr.20081004102201.103:updateButtons (spellTab)
    #@-node:ekr.20081004102201.99:Helpers
    #@-others
#@-node:ekr.20081004102201.84:class gtkSpellTab
#@-node:ekr.20081004102201.61:gtkFind
#@+node:ekr.20081004102201.104:gtkFrame
#@+node:ekr.20081004102201.105:class TestWindow
class TestWindow(gtk.DrawingArea):

    """A window with a cross, used for testing.

    The background and cross color can be set when
    it is created.

    """

    def __init__(self, bg=None, fg=None):

        """Construct a TestWindow.

        'bg': a named color indicating background color, defaults to 'white' if invalid.
        'fg': a named color indicating foreground color, defaults to 'black' if invalid.

        """

        super(TestWindow, self).__gobject_init__()


        self.set_size_request(10, 10)

        self.bg = leoColor.getCairo(bg, 'white')
        self.fg = leoColor.getCairo(fg, 'black')



    def do_expose_event(self, event):
        """Handle expose events for this window"""

        cr = self.window.cairo_create()

        w, h = self.window.get_size()


        cr.set_source_rgb(*self.bg)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        cr.set_source_rgb(*self.fg)

        cr.move_to(0, 0)
        cr.line_to(w, h)
        cr.move_to(w, 0)
        cr.line_to(0, h)
        cr.stroke()

        return True

gobject.type_register(TestWindow)
#@-node:ekr.20081004102201.105:class TestWindow
#@+node:ekr.20081004102201.106:== paned widget classes ==
#@+node:ekr.20081004102201.107:class panedMixin
class panedMixin:

    """Adds leo specific functionality to gtk.[VH]Paned widgets."""


    def __repr__(self):

        return '<%s: %s %s (%s)>' % (self.__class__.name, self.name, self.orientation, self.get_position)

    #@    @+others
    #@+node:ekr.20081004102201.108:__init__
    def __init__(self, c, name, orientation, ratio=0.5):

        """Initialize the widget with leo specific parameters.

        'name' Sets the "name" property of the widget to the string specified by name.
               This will allow the widget to be referenced in a GTK resource file.

        'orientation' A string describing this widgets orientation ('horizontal' or 'vertical')

        """
        self.c = c
        self.set_name(name)
        self.orientation = orientation
        self.ratio = ratio

        self.connect('notify::position', self.onPositionChanged)






    #@-node:ekr.20081004102201.108:__init__
    #@+node:ekr.20081004102201.109:setSplitRatio
    def setSplitRatio(self, ratio):
        """Set the split ratio to 'ratio'.

        'ratio' should be a float in the range from 0.0 to 1.0 inclusive.

        """

        self.__ratio = ratio

        #check to see if containing window has been mapped
        #if not then leave it to onMap to set splitter position.
        if not self.window:
            return

        w, h = self.window.get_size()

        size = g.choose(self.orientation == 'horizontal', w, h)
        self.set_position(int(size * ratio))

        #g.trace(self, ratio, size)
    #@nonl
    #@-node:ekr.20081004102201.109:setSplitRatio
    #@+node:ekr.20081004102201.110:getSplitRatio
    def getSplitRatio(self):

        """Get the current split ratio.

        If the window is not mapped then this can not be calculated so the
        value stored in self.__ratio is used as this is the ratio that will
        be set when the widget is mapped.

        """

        if not self.window:
            return self.__ratio

        w, h = self.window.get_size()
        size = g.choose(self.orientation == 'horizontal', w, h)

        self.__ratio = self.get_position()*1.0/size

        return self.__ratio 
    #@-node:ekr.20081004102201.110:getSplitRatio
    #@+node:ekr.20081004102201.111:resetSplitRatio
    def resetSplitRatio(self):

        self.setSplitRatio(self.__ratio)
    #@-node:ekr.20081004102201.111:resetSplitRatio
    #@+node:ekr.20081004102201.112:onPositionChanged
    def onPositionChanged(self, *args):

        """Respond to changes in the widgets 'position' property"""

        self.__ratio = self.getSplitRatio()
    #@-node:ekr.20081004102201.112:onPositionChanged
    #@+node:ekr.20081004102201.113:Property: ratio
    ratio = property(getSplitRatio, setSplitRatio)
    #@nonl
    #@-node:ekr.20081004102201.113:Property: ratio
    #@-others









#@-node:ekr.20081004102201.107:class panedMixin
#@+node:ekr.20081004102201.114:class VPaned (gtk.VPaned, panedMixin)
class VPaned(gtk.VPaned, panedMixin):
    """Subclass to add leo specific functionality to gtk.VPaned."""

    def __init__(self, c, name):

        gtk.VPaned.__gobject_init__(self)
        panedMixin.__init__(self, c, name, 'vertical')

gobject.type_register(VPaned)
#@-node:ekr.20081004102201.114:class VPaned (gtk.VPaned, panedMixin)
#@+node:ekr.20081004102201.115:class HPaned (gtk.HPaned, panedMixin)
class HPaned(gtk.HPaned, panedMixin):
    """Subclass to add leo specific functionality to gtk.HPaned."""

    def __init__(self, c, name):

        """Construct a new object"""

        gtk.VPaned.__gobject_init__(self)
        panedMixin.__init__(self, c, name, 'horizontal')

gobject.type_register(HPaned)
#@-node:ekr.20081004102201.115:class HPaned (gtk.HPaned, panedMixin)
#@-node:ekr.20081004102201.106:== paned widget classes ==
#@+node:ekr.20081004102201.116:class leoGtkFrame
class leoGtkFrame (leoFrame.leoFrame):

    #@    @+others
    #@+node:ekr.20081004102201.117: Birth & Death (gtkFrame)
    #@+node:ekr.20081004102201.118:__init__ (gtkFrame)
    def __init__(self,title,gui):

        #g.trace('gtkFrame',g.callers(20))

        # Init the base class.
        leoFrame.leoFrame.__init__(self,gui)

        self.use_chapters = False ###

        self.title = title

        leoGtkFrame.instances += 1

        self.c = None # Set in finishCreate.
        self.iconBarClass = self.gtkIconBarClass
        self.statusLineClass = self.gtkStatusLineClass
        #self.minibufferClass = self.gtkMinibufferClass

        self.iconBar = None

        self.trace_status_line = None # Set in finishCreate.

        #@    << set the leoGtkFrame ivars >>
        #@+node:ekr.20081004102201.119:<< set the leoGtkFrame ivars >> (removed frame.bodyCtrl ivar)
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
        #@-node:ekr.20081004102201.119:<< set the leoGtkFrame ivars >> (removed frame.bodyCtrl ivar)
        #@nl
    #@-node:ekr.20081004102201.118:__init__ (gtkFrame)
    #@+node:ekr.20081004102201.120:__repr__ (gtkFrame)
    def __repr__ (self):

        return "<leoGtkFrame: %s>" % self.title
    #@-node:ekr.20081004102201.120:__repr__ (gtkFrame)
    #@+node:ekr.20081004102201.121:gtkFrame.finishCreate & helpers
    def finishCreate (self,c):
        """Finish creating leoGtkFrame."""

        f = self ; f.c = c
        #g.trace('gtkFrame')

        self.trace_status_line = c.config.getBool('trace_status_line')
        self.use_chapters = False and c.config.getBool('use_chapters') ###
        self.use_chapter_tabs  = False and c.config.getBool('use_chapter_tabs') ###

        # This must be done after creating the commander.
        f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()

        f.createOuterFrames()

        ### f.createIconBar()

        f.createSplitterComponents()

        ### f.createStatusLine()

        f.createFirstTreeNode()
        f.menu = leoGtkMenu.leoGtkMenu(f)

            # c.finishCreate calls f.createMenuBar later. Why?

        c.setLog()
        g.app.windowList.append(f)

        c.initVersion()
        c.signOnWithVersion()

        f.miniBufferWidget = f.createMiniBufferWidget()

        def cbResetSplitRatio(f=f):
            if not f:
                g.trace('no frame')
            f and f.f1 and f.f1.resetSplitRatio()
            f and f.f2 and f.f2.resetSplitRatio()
            return True

        gobject.timeout_add(300, cbResetSplitRatio)

        c.bodyWantsFocusNow()

    #@+node:ekr.20081004102201.122:createOuterFrames
    def createOuterFrames (self):

        """Create the main window."""

        f = self ; c = f.c

        w = gtk.Window(gtk.WINDOW_TOPLEVEL)
        w.set_title("gtkLeo Demo")

        w.set_size_request(10, 10)
        #w.resize(400, 300)

        # mainVbox is the vertical box where all the componets are pack
        # starting with the menu and ending with the minibuffer.

        f.mainVBox = gtk.VBox()
        w.add(f.mainVBox)

        f.top = w

        def destroy_callback(widget,data=None):
            gtk.main_quit()  ### should call g.app.closeLeoWindow.

        w.connect(
            "destroy",
             destroy_callback
        )

        w.connect(
            'key-press-event', lambda w, event, self=f: self.toggleSplitDirection()
        )

        w.show_all()

    #@-node:ekr.20081004102201.122:createOuterFrames
    #@+node:ekr.20081004102201.123:createSplitterComponents (removed frame.bodyCtrl ivar)
    def createSplitterComponents (self):
        """Create the splitters and populate them with tree, body and log panels.""" 

        f = self ; c = f.c

        #g.trace()

        f.mainSplitterPanel = gtk.HBox()
        f.menuHolderPanel = gtk.VBox()

        f.mainVBox.pack_start(f.menuHolderPanel, False, False, 0)
        f.mainVBox.add(f.mainSplitterPanel)

        f.body = leoGtkBody(f,f.top)
        f.tree = leoGtkTree.leoGtkTree(c)
        f.log  = leoGtkLog(f,f.top)

        self.createLeoSplitters(f)

        # Configure.
        f.setTabWidth(c.tab_width)
        f.reconfigurePanes()
        f.body.setFontFromConfig()
        f.body.setColorFromConfig()

        f.top.show_all()
    #@-node:ekr.20081004102201.123:createSplitterComponents (removed frame.bodyCtrl ivar)
    #@+node:ekr.20081004102201.124:createFirstTreeNode
    def createFirstTreeNode (self):

        f = self ; c = f.c

        v = leoNodes.vnode(context=c)
        p = leoNodes.position(v)
        v.initHeadString("NewHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong: the node hasn't been linked yet.
        p._linkAsRoot(oldRoot=None)
        c.setRootPosition(p) # New in 4.4.2.
        c.editPosition(p)
    #@-node:ekr.20081004102201.124:createFirstTreeNode
    #@-node:ekr.20081004102201.121:gtkFrame.finishCreate & helpers
    #@+node:ekr.20081004102201.125:ignore
    if 0:
        #@    @+others
        #@+node:ekr.20081004102201.126:gtkFrame.createCanvas & helpers
        def createCanvas (self,parentFrame,pack=True):

            #g.trace()

            c = self.c

            scrolls = c.config.getBool('outline_pane_scrolls_horizontally')
            scrolls = g.choose(scrolls,1,0)
            canvas = self.createGtkTreeCanvas(parentFrame,scrolls,pack)
            self.setCanvasColorFromConfig(canvas)

            return canvas
        #@+node:ekr.20081004102201.127:f.createGtkTreeCanvas & callbacks
        def createGtkTreeCanvas (self,parentFrame,scrolls,pack):
            #g.trace()

            return self.tree.canvas

        #@-node:ekr.20081004102201.127:f.createGtkTreeCanvas & callbacks
        #@+node:ekr.20081004102201.128:f.setCanvasColorFromConfig
        def setCanvasColorFromConfig (self,canvas):

            c = self.c

            bg = c.config.getColor("outline_pane_background_color") or 'white'

            canvas.setBackgroundColor(bg)

        #@-node:ekr.20081004102201.128:f.setCanvasColorFromConfig
        #@-node:ekr.20081004102201.126:gtkFrame.createCanvas & helpers
        #@-others
    #@nonl
    #@-node:ekr.20081004102201.125:ignore
    #@+node:ekr.20081004102201.129:gtkFrame.createLeoSplitters & helpers
    #@+at 
    #@nonl
    # The key invariants used throughout this code:
    # 
    # 1. self.splitVerticalFlag tells the alignment of the main splitter and
    # 2. not self.splitVerticalFlag tells the alignment of the secondary 
    # splitter.
    # 
    # Only the general-purpose divideAnySplitter routine doesn't know about 
    # these
    # invariants. So most of this code is specialized for Leo's window. OTOH, 
    # creating
    # a single splitter window would be much easier than this code.
    #@-at
    #@@c

    def createLeoSplitters (self,parentFrame=None):

        """Create leo's main and secondary splitters and pack into mainSplitterPanel.

        f1 (splitter1) is the main splitter containing splitter2 and the body pane.
        f2 (splitter2) is the secondary splitter containing the tree and log panes.

        'parentFrame' is not used in gtk.

        """

        f= parentFrame
        c = f.c

        vertical = self.splitVerticalFlag

        f.f1 = self.createLeoGtkSplitter(f, vertical, 'splitter1')
        f.f2 = self.createLeoGtkSplitter(f, not vertical, 'splitter2')

        #f.f2.pack1(TestWindow('leo yellow', 'red'))
        #g.trace(f.tree.canvas.top)
        #f.f2.pack1(TestWindow('leo yellow', 'red'))

        f.f2.pack1(self.tree.canvas.top)
        #f.f2.pack2(TestWindow('leo pink', 'yellow'))

        f.f2.pack2(self.log.nb)
        f.f1.pack1(f.f2)

        #f.f1.pack2(TestWindow('leo blue', 'light green'))
        f.f1.pack2(self.body.bodyCtrl.widget)

        f.mainSplitterPanel.add(f.f1)

    #@+node:ekr.20081004102201.130:createLeoGtkSplitter
    def createLeoGtkSplitter (self,parent,verticalFlag,componentName):
        """Create gtk spitter component."""

        paned = g.choose(verticalFlag, VPaned, HPaned)
        return paned(parent.c, componentName)

    #@-node:ekr.20081004102201.130:createLeoGtkSplitter
    #@+node:ekr.20081004102201.131:bindBar
    def bindBar (self, bar, verticalFlag):

        NOTUSED()
    #@-node:ekr.20081004102201.131:bindBar
    #@+node:ekr.20081004102201.132:divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter (self, frac, verticalFlag, bar, pane1, pane2):

        NOTUSED()
    #@-node:ekr.20081004102201.132:divideAnySplitter
    #@+node:ekr.20081004102201.133:divideLeoSplitter
    # Divides the main or secondary splitter, using the key invariant.

    def divideLeoSplitter (self, verticalFlag, frac):
        """Divides the main or secondary splitter."""

        if self.splitVerticalFlag == verticalFlag:
            self.divideLeoSplitter1(frac)
            self.ratio = frac # Ratio of body pane to tree pane.
        else:
            self.divideLeoSplitter2(frac)
            self.secondary_ratio = frac # Ratio of tree pane to log pane.

    # Divides the main splitter.

    def divideLeoSplitter1 (self, frac, verticalFlag=None):
        """Divide the (tree/log)/body splitter."""
        self.f1.setSplitRatio(frac)

    # Divides the secondary splitter.

    def divideLeoSplitter2 (self, frac, verticalFlag=None):
        """Divide the tree/log splitter."""    
        self.f2.setSplitRatio(frac)

    #@-node:ekr.20081004102201.133:divideLeoSplitter
    #@+node:ekr.20081004102201.134:onDrag...
    def onDragMainSplitBar (self, event):
        self.onDragSplitterBar(event,self.splitVerticalFlag)

    def onDragSecondarySplitBar (self, event):
        self.onDragSplitterBar(event,not self.splitVerticalFlag)

    def onDragSplitterBar (self, event, verticalFlag):

        NOTUSED()
    #@-node:ekr.20081004102201.134:onDrag...
    #@+node:ekr.20081004102201.135:placeSplitter
    def placeSplitter (self,bar,pane1,pane2,verticalFlag):

        NOTUSED()

    #@-node:ekr.20081004102201.135:placeSplitter
    #@-node:ekr.20081004102201.129:gtkFrame.createLeoSplitters & helpers
    #@+node:ekr.20081004102201.136:Destroying the gtkFrame
    #@+node:ekr.20081004102201.137:destroyAllObjects
    def destroyAllObjects (self):

        """Clear all links to objects in a Leo window."""

        frame = self ; c = self.c ; tree = frame.tree ; body = self.body

        # g.printGcAll()

        # Do this first.
        #@    << clear all vnodes and tnodes in the tree >>
        #@+node:ekr.20081004102201.138:<< clear all vnodes and tnodes in the tree>>
        # Using a dict here is essential for adequate speed.
        vList = [] ; tDict = {}

        for p in c.allNodes_iter():
            vList.append(p.v)
            if p.v.t:
                key = id(p.v.t)
                if key not in tDict:
                    tDict[key] = p.v.t

        for key in tDict:
            g.clearAllIvars(tDict[key])

        for v in vList:
            g.clearAllIvars(v)

        vList = [] ; tDict = {} # Remove these references immediately.
        #@-node:ekr.20081004102201.138:<< clear all vnodes and tnodes in the tree>>
        #@nl

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

    #@-node:ekr.20081004102201.137:destroyAllObjects
    #@+node:ekr.20081004102201.139:destroyAllPanels
    def destroyAllPanels (self):

        """Destroy all panels attached to this frame."""

        panels = (self.comparePanel, self.colorPanel, self.findPanel, self.fontPanel, self.prefsPanel)

        for panel in panels:
            if panel:
                panel.top.destroy()
    #@-node:ekr.20081004102201.139:destroyAllPanels
    #@+node:ekr.20081004102201.140:destroySelf (gtkFrame)
    def destroySelf (self):

        # Remember these: we are about to destroy all of our ivars!
        top = self.top 
        c = self.c

        # Indicate that the commander is no longer valid.
        c.exists = False 

        # g.trace(self)

        # Important: this destroys all the objects of the commander too.
        self.destroyAllObjects()

        c.exists = False # Make sure this one ivar has not been destroyed.

        top.destroy()
    #@-node:ekr.20081004102201.140:destroySelf (gtkFrame)
    #@-node:ekr.20081004102201.136:Destroying the gtkFrame
    #@-node:ekr.20081004102201.117: Birth & Death (gtkFrame)
    #@+node:ekr.20081004102201.141:class gtkStatusLineClass
    class gtkStatusLineClass:

        '''A class representing the status line.'''

        #@    @+others
        #@+node:ekr.20081004102201.142: ctor
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
            self.statusFrame = gtk.Frame(parentFrame,bd=2)
            text = "line 0, col 0"
            width = len(text) + 4
            self.labelWidget = gtk.Label(self.statusFrame,text=text,width=width,anchor="w")
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
        #@-node:ekr.20081004102201.142: ctor
        #@+node:ekr.20081004102201.143:clear
        def clear (self):

            w = self.textWidget
            if not w: return

            w.configure(state="normal")
            w.delete(0,"end")
            w.configure(state="disabled")
        #@-node:ekr.20081004102201.143:clear
        #@+node:ekr.20081004102201.144:enable, disable & isEnabled
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
        #@nonl
        #@-node:ekr.20081004102201.144:enable, disable & isEnabled
        #@+node:ekr.20081004102201.145:get
        def get (self):

            w = self.textWidget
            if w:
                return w.getAllText()
            else:
                return ""
        #@-node:ekr.20081004102201.145:get
        #@+node:ekr.20081004102201.146:getFrame
        def getFrame (self):

            return self.statusFrame
        #@-node:ekr.20081004102201.146:getFrame
        #@+node:ekr.20081004102201.147:onActivate
        def onActivate (self,event=None):

            # Don't change background as the result of simple mouse clicks.
            background = self.statusFrame.cget("background")
            self.enable(background=background)
        #@-node:ekr.20081004102201.147:onActivate
        #@+node:ekr.20081004102201.148:pack & show
        def pack (self):

            if not self.isVisible:
                self.isVisible = True
                self.statusFrame.pack(fill="x",pady=1)

        show = pack
        #@-node:ekr.20081004102201.148:pack & show
        #@+node:ekr.20081004102201.149:put (leoGtkFrame:statusLineClass)
        def put(self,s,color=None):

            # g.trace('gtkStatusLine',self.textWidget,s)

            w = self.textWidget
            if not w:
                g.trace('gtkStatusLine','***** disabled')
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
        #@-node:ekr.20081004102201.149:put (leoGtkFrame:statusLineClass)
        #@+node:ekr.20081004102201.150:unpack & hide
        def unpack (self):

            if self.isVisible:
                self.isVisible = False
                self.statusFrame.pack_forget()

        hide = unpack
        #@-node:ekr.20081004102201.150:unpack & hide
        #@+node:ekr.20081004102201.151:update (statusLine)
        def update (self):

            c = self.c ; bodyCtrl = c.frame.body.bodyCtrl

            if g.app.killed or not self.isVisible:
                return

            s = bodyCtrl.getAllText()    
            index = bodyCtrl.getInsertPoint()
            row,col = g.convertPythonIndexToRowCol(s,index)
            if col > 0:
                s2 = s[index-col:index]
                s2 = g.toUnicode(s2,g.app.tkEncoding)
                col = g.computeWidth (s2,c.tab_width)

            # Important: this does not change the focus because labels never get focus.
            self.labelWidget.configure(text="line %d, col %d" % (row,col))
            self.lastRow = row
            self.lastCol = col
        #@-node:ekr.20081004102201.151:update (statusLine)
        #@-others
    #@-node:ekr.20081004102201.141:class gtkStatusLineClass
    #@+node:ekr.20081004102201.152:class gtkIconBarClass
    class gtkIconBarClass:

        '''A class representing the singleton Icon bar'''

        #@    @+others
        #@+node:ekr.20081004102201.153: ctor
        def __init__ (self,c,parentFrame):

            self.c = c

            self.buttons = {}
            self.iconFrame = w = gtk.Frame(parentFrame,height="5m",bd=2,relief="groove")
            self.c.frame.iconFrame = self.iconFrame
            self.font = None
            self.parentFrame = parentFrame
            self.visible = False
            self.show()
        #@-node:ekr.20081004102201.153: ctor
        #@+node:ekr.20081004102201.154:add
        def add(self,*args,**keys):

            """Add a button containing text or a picture to the icon bar.

            Pictures take precedence over text"""

            c = self.c ; f = self.iconFrame
            text = keys.get('text')
            imagefile = keys.get('imagefile')
            image = keys.get('image')
            command = keys.get('command')
            bg = keys.get('bg')

            if not imagefile and not image and not text: return

            # First define n.
            try:
                g.app.iconWidgetCount += 1
                n = g.app.iconWidgetCount
            except:
                n = g.app.iconWidgetCount = 1

            if not command:
                def command():
                    g.pr("command for widget %s" % (n))

            if imagefile or image:
                #@        << create a picture >>
                #@+node:ekr.20081004102201.155:<< create a picture >>
                try:
                    if imagefile:
                        # Create the image.  Throws an exception if file not found
                        imagefile = g.os_path_join(g.app.loadDir,imagefile)
                        imagefile = g.os_path_normpath(imagefile)
                        image = gtk.PhotoImage(master=g.app.root,file=imagefile)

                        # Must keep a reference to the image!
                        try:
                            refs = g.app.iconImageRefs
                        except:
                            refs = g.app.iconImageRefs = []

                        refs.append((imagefile,image),)

                    if not bg:
                        bg = f.cget("bg")

                    b = gtk.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
                    b.pack(side="left",fill="y")
                    return b

                except:
                    g.es_exception()
                    return None
                #@-node:ekr.20081004102201.155:<< create a picture >>
                #@nl
            elif text:
                b = gtk.Button(f,text=text,relief="groove",bd=2,command=command)
                if not self.font:
                    self.font = c.config.getFontFromParams(
                        "button_text_font_family", "button_text_font_size",
                        "button_text_font_slant",  "button_text_font_weight",)
                b.configure(font=self.font)
                # elif sys.platform.startswith('win'):
                    # width = max(6,len(text))
                    # b.configure(width=width,font=('verdana',7,'bold'))
                if bg: b.configure(bg=bg)
                b.pack(side="left", fill="none")
                return b

            return None
        #@-node:ekr.20081004102201.154:add
        #@+node:ekr.20081004102201.156:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            f = self.iconFrame

            for slave in f.pack_slaves():
                slave.destroy()
            self.visible = False

            f.configure(height="5m") # The default height.
            g.app.iconWidgetCount = 0
            g.app.iconImageRefs = []
        #@-node:ekr.20081004102201.156:clear
        #@+node:ekr.20081004102201.157:deleteButton (new in Leo 4.4.3)
        def deleteButton (self,w):

            w.pack_forget()
        #@-node:ekr.20081004102201.157:deleteButton (new in Leo 4.4.3)
        #@+node:ekr.20081004102201.158:getFrame
        def getFrame (self):

            return self.iconFrame
        #@-node:ekr.20081004102201.158:getFrame
        #@+node:ekr.20081004102201.159:pack (show)
        def pack (self):

            """Show the icon bar by repacking it"""

            if not self.visible:
                self.visible = True
                self.iconFrame.pack(fill="x",pady=2)

        show = pack
        #@-node:ekr.20081004102201.159:pack (show)
        #@+node:ekr.20081004102201.160:setCommandForButton (new in Leo 4.4.3)
        def setCommandForButton(self,b,command):

            b.configure(command=command)
        #@-node:ekr.20081004102201.160:setCommandForButton (new in Leo 4.4.3)
        #@+node:ekr.20081004102201.161:unpack (hide)
        def unpack (self):

            """Hide the icon bar by unpacking it.

            A later call to show will repack it in a new location."""

            if self.visible:
                self.visible = False
                self.iconFrame.pack_forget()

        hide = unpack
        #@-node:ekr.20081004102201.161:unpack (hide)
        #@-others
    #@-node:ekr.20081004102201.152:class gtkIconBarClass
    #@+node:ekr.20081004102201.162:Minibuffer methods
    #@+node:ekr.20081004102201.163:showMinibuffer
    def showMinibuffer (self):

        '''Make the minibuffer visible.'''

        frame = self

        if not frame.minibufferVisible:
            frame.minibufferFrame.pack(side='bottom',fill='x')
            frame.minibufferVisible = True
    #@-node:ekr.20081004102201.163:showMinibuffer
    #@+node:ekr.20081004102201.164:hideMinibuffer
    def hideMinibuffer (self):

        '''Hide the minibuffer.'''

        frame = self
        if frame.minibufferVisible:
            frame.minibufferFrame.pack_forget()
            frame.minibufferVisible = False
    #@-node:ekr.20081004102201.164:hideMinibuffer
    #@+node:ekr.20081004102201.165:f.createMiniBufferWidget
    def createMiniBufferWidget (self):

        '''Create the minbuffer below the status line.'''

        frame = self ; c = frame.c

        # frame.minibufferFrame = f = gtk.Frame(frame.outerFrame,relief='flat',borderwidth=0)
        # if c.showMinibuffer:
            # f.pack(side='bottom',fill='x')

        # lab = gtk.Label(f,text='mini-buffer',justify='left',anchor='nw',foreground='blue')
        # lab.pack(side='left')

        # label = g.app.gui.plainTextWidget(
            # f,height=1,relief='groove',background='lightgrey',name='minibuffer')
        # label.pack(side='left',fill='x',expand=1,padx=2,pady=1)

        # frame.minibufferVisible = c.showMinibuffer

        # return label
    #@-node:ekr.20081004102201.165:f.createMiniBufferWidget
    #@+node:ekr.20081004102201.166:f.setMinibufferBindings
    def setMinibufferBindings (self):

        '''Create bindings for the minibuffer..'''

        f = self ; c = f.c ; k = c.k ; w = f.miniBufferWidget

        # for kind,callback in (
            # ('<Key>',           k.masterKeyHandler),
            # ('<Button-1>',      k.masterClickHandler),
            # ('<Button-3>',      k.masterClick3Handler),
            # ('<Double-1>',      k.masterDoubleClickHandler),
            # ('<Double-3>',      k.masterDoubleClick3Handler),
        # ):
            # c.bind(w,kind,callback)

        # if 0:
            # if sys.platform.startswith('win'):
                # # Support Linux middle-button paste easter egg.
                # c.bind(w,"<Button-2>",frame.OnPaste)
    #@-node:ekr.20081004102201.166:f.setMinibufferBindings
    #@-node:ekr.20081004102201.162:Minibuffer methods
    #@+node:ekr.20081004102201.167:Configuration (gtkFrame)
    #@+node:ekr.20081004102201.168:reconfigureFromConfig (gtkFrame)
    def reconfigureFromConfig (self):

        frame = self ; c = frame.c

        frame.tree.setFontFromConfig()
        ### frame.tree.setColorFromConfig()

        frame.configureBarsFromConfig()

        frame.body.setFontFromConfig()
        frame.body.setColorFromConfig()

        frame.setTabWidth(c.tab_width)
        frame.log.setFontFromConfig()
        frame.log.setColorFromConfig()

        c.redraw_now()
    #@-node:ekr.20081004102201.168:reconfigureFromConfig (gtkFrame)
    #@+node:ekr.20081004102201.169:setInitialWindowGeometry (gtkFrame)
    def setInitialWindowGeometry(self):

        """Set the position and size of the frame to config params."""

        c = self.c

        h = c.config.getInt("initial_window_height") or 500
        w = c.config.getInt("initial_window_width") or 600
        x = c.config.getInt("initial_window_left") or 10
        y = c.config.getInt("initial_window_top") or 10

        if h and w and x and y:
            self.setTopGeometry(w,h,x,y)
    #@-node:ekr.20081004102201.169:setInitialWindowGeometry (gtkFrame)
    #@+node:ekr.20081004102201.170:setWrap (gtkFrame)
    def setWrap (self,p):

        c = self.c ; w = c.frame.body.bodyCtrl

        theDict = c.scanAllDirectives(p)
        if not theDict: return

        wrap = theDict.get("wrap")

        ### if self.body.wrapState == wrap: return

        self.body.wrapState = wrap
        # g.trace(wrap)

        ### Rewrite for gtk.
    #@nonl
    #@-node:ekr.20081004102201.170:setWrap (gtkFrame)
    #@+node:ekr.20081004102201.171:setTopGeometry (gtkFrame)
    def setTopGeometry(self,w,h,x,y,adjustSize=True):

        # Put the top-left corner on the screen.
        x = max(10,x) ; y = max(10,y)

        if adjustSize:
            top = self.top
            sw = gtk.gdk.screen_width()
            sh = gtk.gdk.screen_height()

            # Adjust the size so the whole window fits on the screen.
            w = min(sw-10,w)
            h = min(sh-10,h)

            # Adjust position so the whole window fits on the screen.
            if x + w > sw: x = 10
            if y + h > sh: y = 10

        self.top.resize(w,h)
        self.top.move(x,y)
    #@-node:ekr.20081004102201.171:setTopGeometry (gtkFrame)
    #@+node:ekr.20081004102201.172:reconfigurePanes (use config bar_width) (gtkFrame)
    def reconfigurePanes (self):

        c = self.c

        border = c.config.getInt('additional_body_text_border')
        if border == None: border = 0

        # The body pane needs a _much_ bigger border when tiling horizontally.
        border = g.choose(self.splitVerticalFlag,2+border,6+border)
        ### self.bodyCtrl.configure(bd=border)

        # The log pane needs a slightly bigger border when tiling vertically.
        border = g.choose(self.splitVerticalFlag,4,2) 
        ### self.log.configureBorder(border)
    #@-node:ekr.20081004102201.172:reconfigurePanes (use config bar_width) (gtkFrame)
    #@+node:ekr.20081004102201.173:resizePanesToRatio (gtkFrame)
    def resizePanesToRatio(self,ratio,ratio2):

        # g.trace(ratio,ratio2,g.callers())

        self.divideLeoSplitter(self.splitVerticalFlag,ratio)
        self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
    #@nonl
    #@-node:ekr.20081004102201.173:resizePanesToRatio (gtkFrame)
    #@-node:ekr.20081004102201.167:Configuration (gtkFrame)
    #@+node:ekr.20081004102201.174:Event handlers (gtkFrame)
    #@+node:ekr.20081004102201.175:frame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self):

        f = self ; c = f.c

        if c.inCommand:
            # g.trace('requesting window close')
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@-node:ekr.20081004102201.175:frame.OnCloseLeoEvent
    #@+node:ekr.20081004102201.176:frame.OnControlKeyUp/Down
    def OnControlKeyDown (self,event=None):

        self.controlKeyIsDown = True

    def OnControlKeyUp (self,event=None):

        self.controlKeyIsDown = False
    #@-node:ekr.20081004102201.176:frame.OnControlKeyUp/Down
    #@+node:ekr.20081004102201.177:OnActivateBody (gtkFrame)
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
    #@-node:ekr.20081004102201.177:OnActivateBody (gtkFrame)
    #@+node:ekr.20081004102201.178:OnActivateLeoEvent, OnDeactivateLeoEvent
    def OnActivateLeoEvent(self,event=None):

        '''Handle a click anywhere in the Leo window.'''

        self.c.setLog()

    def OnDeactivateLeoEvent(self,event=None):

        pass # This causes problems on the Mac.
    #@-node:ekr.20081004102201.178:OnActivateLeoEvent, OnDeactivateLeoEvent
    #@+node:ekr.20081004102201.179:OnActivateTree
    def OnActivateTree (self,event=None):

        try:
            frame = self ; c = frame.c
            c.setLog()

            if 0: # Do NOT do this here!
                # OnActivateTree can get called when the tree gets DE-activated!!
                c.bodyWantsFocus()

        except:
            g.es_event_exception("activate tree")
    #@-node:ekr.20081004102201.179:OnActivateTree
    #@+node:ekr.20081004102201.180:OnBodyClick, OnBodyRClick (Events)
    def OnBodyClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
                self.OnActivateBody(event=event)
            g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodyclick")

    def OnBodyRClick(self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if not g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
                pass # By default Leo does nothing.
            g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")
    #@-node:ekr.20081004102201.180:OnBodyClick, OnBodyRClick (Events)
    #@+node:ekr.20081004102201.181:OnBodyDoubleClick (Events)
    def OnBodyDoubleClick (self,event=None):

        try:
            c = self.c ; p = c.currentPosition()
            if event and not g.doHook("bodydclick1",c=c,p=p,v=p,event=event):
                c.editCommands.extendToWord(event) # Handles unicode properly.
            g.doHook("bodydclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("bodydclick")

        return "break" # Restore this to handle proper double-click logic.
    #@-node:ekr.20081004102201.181:OnBodyDoubleClick (Events)
    #@+node:ekr.20081004102201.182:OnMouseWheel (Tomaz Ficko)
    # Contributed by Tomaz Ficko.  This works on some systems.
    # On XP it causes a crash in tcl83.dll.  Clearly a Tk bug.

    def OnMouseWheel(self, event=None):

        # try:
            # if event.delta < 1:
                # self.canvas.yview(Tk.SCROLL, 1, Tk.UNITS)
            # else:
                # self.canvas.yview(Tk.SCROLL, -1, Tk.UNITS)
        # except:
            # g.es_event_exception("scroll wheel")

        return "break"
    #@-node:ekr.20081004102201.182:OnMouseWheel (Tomaz Ficko)
    #@-node:ekr.20081004102201.174:Event handlers (gtkFrame)
    #@+node:ekr.20081004102201.183:Gui-dependent commands
    #@+node:ekr.20081004102201.184:Minibuffer commands... (gtkFrame)

    #@+node:ekr.20081004102201.185:contractPane
    def contractPane (self,event=None):

        '''Contract the selected pane.'''

        f = self ; c = f.c
        w = c.get_requested_focus()
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.contractBodyPane()
        elif wname.startswith('log'):
            f.contractLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.contractOutlinePane()
    #@-node:ekr.20081004102201.185:contractPane
    #@+node:ekr.20081004102201.186:expandPane
    def expandPane (self,event=None):

        '''Expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus()
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.expandBodyPane()
        elif wname.startswith('log'):
            f.expandLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.expandOutlinePane()
    #@-node:ekr.20081004102201.186:expandPane
    #@+node:ekr.20081004102201.187:fullyExpandPane
    def fullyExpandPane (self,event=None):

        '''Fully expand the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus()
        wname = c.widget_name(w)

        # g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.fullyExpandBodyPane()
        elif wname.startswith('log'):
            f.fullyExpandLogPane()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.fullyExpandOutlinePane()
    #@-node:ekr.20081004102201.187:fullyExpandPane
    #@+node:ekr.20081004102201.188:hidePane
    def hidePane (self,event=None):

        '''Completely contract the selected pane.'''

        f = self ; c = f.c

        w = c.get_requested_focus()
        wname = c.widget_name(w)

        #g.trace(wname)
        if not w: return

        if wname.startswith('body'):
            f.hideBodyPane()
            c.treeWantsFocusNow()
        elif wname.startswith('log'):
            f.hideLogPane()
            c.bodyWantsFocusNow()
        elif wname.startswith('head') or wname.startswith('canvas'):
            f.hideOutlinePane()
            c.bodyWantsFocusNow()
    #@-node:ekr.20081004102201.188:hidePane
    #@+node:ekr.20081004102201.189:expand/contract/hide...Pane
    #@+at 
    #@nonl
    # The first arg to divideLeoSplitter means the following:
    # 
    #     f.splitVerticalFlag: use the primary   (tree/body) ratio.
    # not f.splitVerticalFlag: use the secondary (tree/log) ratio.
    #@-at
    #@@c

    def contractBodyPane (self,event=None):
        '''Contract the body pane.'''
        f = self ; r = min(1.0,f.ratio+0.1)
        f.divideLeoSplitter(f.splitVerticalFlag,r)

    def contractLogPane (self,event=None):
        '''Contract the log pane.'''
        f = self ; r = min(1.0,f.ratio+0.1)
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
        f = self ; r = max(0.0,f.ratio-0.1)
        f.divideLeoSplitter(not f.splitVerticalFlag,r)

    def expandOutlinePane (self,event=None):
        '''Expand the outline pane.'''
        self.contractBodyPane()
    #@-node:ekr.20081004102201.189:expand/contract/hide...Pane
    #@+node:ekr.20081004102201.190:fullyExpand/hide...Pane
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
    #@-node:ekr.20081004102201.190:fullyExpand/hide...Pane
    #@-node:ekr.20081004102201.184:Minibuffer commands... (gtkFrame)
    #@+node:ekr.20081004102201.191:Window Menu...
    #@+node:ekr.20081004102201.192:toggleActivePane
    def toggleActivePane (self,event=None):

        '''Toggle the focus between the outline and body panes.'''

        frame = self ; c = frame.c

        if c.get_focus() == frame.body.bodyCtrl: # 2007:10/25
            c.treeWantsFocusNow()
        else:
            c.endEditing()
            c.bodyWantsFocusNow()
    #@-node:ekr.20081004102201.192:toggleActivePane
    #@+node:ekr.20081004102201.193:cascade
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
    #@-node:ekr.20081004102201.193:cascade
    #@+node:ekr.20081004102201.194:equalSizedPanes
    def equalSizedPanes (self,event=None):

        '''Make the outline and body panes have the same size.'''

        frame = self
        frame.f1.ratio = 0.5
    #@-node:ekr.20081004102201.194:equalSizedPanes
    #@+node:ekr.20081004102201.195:hideLogWindow
    def hideLogWindow (self,event=None):

        frame = self
        frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
    #@-node:ekr.20081004102201.195:hideLogWindow
    #@+node:ekr.20081004102201.196:minimizeAll
    def minimizeAll (self,event=None):

        '''Minimize all Leo's windows.'''

        self.minimize(g.app.pythonFrame)
        for frame in g.app.windowList:
            self.minimize(frame)
            self.minimize(frame.findPanel)

    def minimize(self,frame):

        if frame:
            frame.top.iconify()
    #@-node:ekr.20081004102201.196:minimizeAll
    #@+node:ekr.20081004102201.197:toggleSplitDirection (gtkFrame)
    # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

    def toggleSplitDirection (self,event=None):

        f = self

        #g.trace(f, f.f1, f.f2)

        '''Toggle the split direction in the present Leo window.'''

        # Switch directions.
        c = self.c
        self.splitVerticalFlag = not self.splitVerticalFlag

        orientation = g.choose(self.splitVerticalFlag,"vertical","horizontal")

        c.config.set("initial_splitter_orientation","string",orientation)

        self.toggleGtkSplitDirection(self.splitVerticalFlag)
    #@+node:ekr.20081004102201.198:toggleGtkSplitDirection
    def toggleGtkSplitDirection (self,verticalFlag=None):
        """Strip the splitters and create new ones in the desired orientation.

        'verticalFlag' is not used in gtkGui.

        """

        f = self

        f.mainSplitterPanel.remove(f.f1)

        tree = f.f2.get_child1()
        f.f2.remove(tree)

        log = f.f2.get_child2()
        f.f2.remove(log)

        body = f.f1.get_child2()
        f.f1.remove(body)

        f.f1.remove(f.f2)

        f.f1 = f.f2 = None

        self.createLeoSplitters(f)

        f.f2.pack1(tree)
        f.f2.pack2(log)
        f.f1.pack1(f.f2)

        f.f1.pack2(body)

        f.top.show_all()

    #@-node:ekr.20081004102201.198:toggleGtkSplitDirection
    #@-node:ekr.20081004102201.197:toggleSplitDirection (gtkFrame)
    #@+node:ekr.20081004102201.199:resizeToScreen
    def resizeToScreen (self,event=None):

        '''Resize the Leo window so it fills the entire screen.'''

        self.top.maximize()
    #@-node:ekr.20081004102201.199:resizeToScreen
    #@-node:ekr.20081004102201.191:Window Menu...
    #@+node:ekr.20081004102201.200:Help Menu...
    #@+node:ekr.20081004102201.201:leoHelp
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
    #@+node:ekr.20081004102201.202:showProgressBar
    def showProgressBar (self,count,size,total):

        # g.trace("count,size,total:",count,size,total)
        if self.scale == None:
            #@        << create the scale widget >>
            #@+node:ekr.20081004102201.203:<< create the scale widget >>
            top = gtk.Window() # Tk.Toplevel()
            top.title("Download progress")
            # self.scale = scale = Tk.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
            # scale.pack()
            top.lift()
            #@-node:ekr.20081004102201.203:<< create the scale widget >>
            #@nl
        self.scale.set(count*size)
        self.scale.update_idletasks()
    #@-node:ekr.20081004102201.202:showProgressBar
    #@-node:ekr.20081004102201.201:leoHelp
    #@-node:ekr.20081004102201.200:Help Menu...
    #@-node:ekr.20081004102201.183:Gui-dependent commands
    #@+node:ekr.20081004102201.204:Gtk bindings... (gtkFrame)
    def bringToFront (self):
        self.top.present()


    def getFocus(self):
        """Returns the widget that has focus, or body if None."""
        g.trace()
        # try:
            # # This method is unreliable while focus is changing.
            # # The call to update_idletasks may help.  Or not.
            # self.top.update_idletasks()
            # f = self.top.focus_displayof()
        # except Exception:
            # f = None
        # if f:
            # return f
        # else:
            # return self.body.bodyCtrl

    def getTitle (self):
        return self.top and self.top.get_title() or '<no title>'

    def setTitle (self,title):
        return self.top.set_title(title)

    def get_window_info(self):
        g.trace()
        # return g.app.gui.get_window_info(self.top)

    def iconify(self):
        self.top.iconify()

    def deiconify (self):
        self.top.deiconify()

    def lift (self):
        self.top.present()

    def update (self):
        g.trace() # self.top.update()
    #@-node:ekr.20081004102201.204:Gtk bindings... (gtkFrame)
    #@+node:ekr.20081004102201.205:not used
    #@+node:ekr.20081004102201.206:configureBar (gtkFrame)
    def configureBar (self,bar,verticalFlag):

        return
    #@nonl
    #@-node:ekr.20081004102201.206:configureBar (gtkFrame)
    #@+node:ekr.20081004102201.207:configureBarsFromConfig (gtkFrame)
    def configureBarsFromConfig (self):

        return
    #@-node:ekr.20081004102201.207:configureBarsFromConfig (gtkFrame)
    #@+node:ekr.20081004102201.208:setTabWidth (gtkFrame)
    def setTabWidth (self, w):

        pass

        # try: # This can fail when called from scripts
            # # Use the present font for computations.
            # font = self.bodyCtrl.cget("font")
            # root = g.app.root # 4/3/03: must specify root so idle window will work properly.
            # font = gtkFont.Font(root=root,font=font)
            # tabw = font.measure(" " * abs(w)) # 7/2/02
            # self.bodyCtrl.configure(tabs=tabw)
            # self.tab_width = w
            # # g.trace(w,tabw)
        # except:
            # g.es_exception()
            # pass
    #@-node:ekr.20081004102201.208:setTabWidth (gtkFrame)
    #@+node:ekr.20081004102201.209:Delayed Focus (gtkFrame)
    #@+at 
    #@nonl
    # New in 4.3. The proper way to change focus is to call 
    # c.frame.xWantsFocus.
    # 
    # Important: This code never calls select, so there can be no race 
    # condition here
    # that alters text improperly.
    #@-at
    #@-node:ekr.20081004102201.209:Delayed Focus (gtkFrame)
    #@-node:ekr.20081004102201.205:not used
    #@-others
#@-node:ekr.20081004102201.116:class leoGtkFrame
#@+node:ekr.20081004102201.210:class leoGtkBody
class leoGtkBody (leoFrame.leoBody):

    ###

    # def __init__ (self,frame,parentFrame):
        # # g.trace('leoGtkBody')
        # leoFrame.leoBody.__init__(self,frame,parentFrame) # Init the base class.

    # # Birth, death & config...
    # def createBindings (self,w=None):         pass
    # def createControl (self,parentFrame,p):   pass
    # def setColorFromConfig (self,w=None):     pass
    # def setFontFromConfig (self,w=None):      pass

    # # Editor...
    # def createEditorLabel (self,pane):  pass
    # def setEditorColors (self,bg,fg):   pass

    # # Events...
    # def scheduleIdleTimeRoutine (self,function,*args,**keys): pass

    #@    @+others
    #@+node:ekr.20081004102201.211: Birth & death
    #@+node:ekr.20081004102201.212:gtkBody. __init__
    def __init__ (self,frame,parentFrame):

        #g.trace('leoGtkBody')

        # Call the base class constructor.
        leoFrame.leoBody.__init__(self,frame,parentFrame)

        c = self.c ; p = c.currentPosition()
        self.editor_name = None
        self.editor_v = None

        self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
        self.bodyCtrl = self.createControl(parentFrame,p)
        self.colorizer = leoColor.colorizer(c)
    #@-node:ekr.20081004102201.212:gtkBody. __init__
    #@+node:ekr.20081004102201.213:gtkBody.createBindings
    def createBindings (self,w=None):

        '''(gtkBody) Create gui-dependent bindings.
        These are *not* made in nullBody instances.'''

        frame = self.frame ; c = self.c ; k = c.k
        if not w: w = self.bodyCtrl

        # c.bind(w,'<Key>', k.masterKeyHandler)

        # for kind,func,handler in (
            # ('<Button-1>',  frame.OnBodyClick,          k.masterClickHandler),
            # ('<Button-3>',  frame.OnBodyRClick,         k.masterClick3Handler),
            # ('<Double-1>',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
            # ('<Double-3>',  None,                       k.masterDoubleClick3Handler),
            # ('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
        # ):
            # def bodyClickCallback(event,handler=handler,func=func):
                # return handler(event,func)

            # c.bind(w,kind,bodyClickCallback)
    #@nonl
    #@-node:ekr.20081004102201.213:gtkBody.createBindings
    #@+node:ekr.20081004102201.214:gtkBody.createControl
    def createControl (self,parentFrame,p):

        c = self.c

        g.trace('gtkBody')

        # New in 4.4.1: make the parent frame a PanedWidget.
        self.numberOfEditors = 1 ; name = '1'
        self.totalNumberOfEditors = 1

        orient = c.config.getString('editor_orientation') or 'horizontal'
        if orient not in ('horizontal','vertical'): orient = 'horizontal'

        # self.pb = pb = Pmw.PanedWidget(parentFrame,orient=orient)
        # parentFrame = pb.add(name)
        # pb.pack(expand=1,fill='both') # Must be done after the first page created.

        w = self.createTextWidget(parentFrame,p,name)
        self.editorWidgets[name] = w

        return w
    #@-node:ekr.20081004102201.214:gtkBody.createControl
    #@+node:ekr.20081004102201.215:gtkBody.createTextWidget
    def createTextWidget (self,parentFrame,p,name):

        c = self.c

        # parentFrame.configure(bg='LightSteelBlue1')

        wrap = c.config.getBool('body_pane_wraps')
        wrap = g.choose(wrap,"word","none")

        # # Setgrid=1 cause severe problems with the font panel.
        body = w = leoGtkTextWidget (c, name='body-pane',
            bd=2,bg="white",relief="flat",setgrid=0,wrap=wrap)

        bodyBar = None ###
        bodyXBar = None ###
        # bodyBar = Tk.Scrollbar(parentFrame,name='bodyBar')

        # def yscrollCallback(x,y,bodyBar=bodyBar,w=w):
            # # g.trace(x,y,g.callers())
            # if hasattr(w,'leo_scrollBarSpot'):
                # w.leo_scrollBarSpot = (x,y)
            # return bodyBar.set(x,y)

        # body['yscrollcommand'] = yscrollCallback # bodyBar.set

        # bodyBar['command'] =  body.yview
        # bodyBar.pack(side="right", fill="y")

        # # Always create the horizontal bar.
        # bodyXBar = Tk.Scrollbar(
            # parentFrame,name='bodyXBar',orient="horizontal")
        # body['xscrollcommand'] = bodyXBar.set
        # bodyXBar['command'] = body.xview

        # if wrap == "none":
            # # g.trace(parentFrame)
            # bodyXBar.pack(side="bottom", fill="x")

        # body.pack(expand=1,fill="both")

        # self.wrapState = wrap

        # if 0: # Causes the cursor not to blink.
            # body.configure(insertofftime=0)

        # # Inject ivars
        if name == '1':
            w.leo_p = w.leo_v = None # Will be set when the second editor is created.
        else:
            w.leo_p = p.copy()
            w.leo_v = w.leo_p.v
                # pychecker complains body.leo_p does not exist.
        w.leo_active = True
        w.leo_bodyBar = bodyBar
        w.leo_bodyXBar = bodyXBar
        w.leo_chapter = None
        w.leo_frame = parentFrame
        w.leo_name = name
        w.leo_label = None
        w.leo_label_s = None
        w.leo_scrollBarSpot = None
        w.leo_insertSpot = None
        w.leo_selection = None

        return w
    #@-node:ekr.20081004102201.215:gtkBody.createTextWidget
    #@-node:ekr.20081004102201.211: Birth & death
    #@+node:ekr.20081004102201.216:gtkBody.setColorFromConfig
    def setColorFromConfig (self,w=None):

        c = self.c
        if w is None: w = self.bodyCtrl

        return ###

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
    #@-node:ekr.20081004102201.216:gtkBody.setColorFromConfig
    #@+node:ekr.20081004102201.217:gtkBody.setFontFromConfig
    def setFontFromConfig (self,w=None):

        c = self.c

        if not w: w = self.bodyCtrl

        font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        ### w.configure(font=font)

        # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
    #@-node:ekr.20081004102201.217:gtkBody.setFontFromConfig
    #@+node:ekr.20081004102201.218:Focus (gtkBody)
    def hasFocus (self):

        return self.bodyCtrl == self.frame.top.focus_displayof()

    def setFocus (self):

        self.c.widgetWantsFocus(self.bodyCtrl)
    #@-node:ekr.20081004102201.218:Focus (gtkBody)
    #@+node:ekr.20081004102201.219:forceRecolor
    def forceFullRecolor (self):

        self.forceFullRecolorFlag = True
    #@-node:ekr.20081004102201.219:forceRecolor
    #@+node:ekr.20081004102201.220:Tk bindings (gtkBbody)
    #@+node:ekr.20081004102201.221:bind
    def bind (self,*args,**keys):

        pass
    #@-node:ekr.20081004102201.221:bind
    #@+node:ekr.20081004102201.222:Tags (Tk spelling) (gtkBody)
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
    #@-node:ekr.20081004102201.222:Tags (Tk spelling) (gtkBody)
    #@+node:ekr.20081004102201.223:Configuration (Tk spelling) (gtkBody)
    def cget(self,*args,**keys):

        body = self ; w = self.bodyCtrl
        val = w.cget(*args,**keys)

        if g.app.trace:
            g.trace(val,args,keys)

        return val

    def configure (self,*args,**keys):

        # g.trace(args,keys)

        body = self ; w = body.bodyCtrl
        return w.configure(*args,**keys)
    #@-node:ekr.20081004102201.223:Configuration (Tk spelling) (gtkBody)
    #@+node:ekr.20081004102201.224:Height & width (gtkBody)
    def getBodyPaneHeight (self):

        return self.bodyCtrl.winfo_height()

    def getBodyPaneWidth (self):

        return self.bodyCtrl.winfo_width()
    #@-node:ekr.20081004102201.224:Height & width (gtkBody)
    #@+node:ekr.20081004102201.225:Idle time... (gtkBody)
    def scheduleIdleTimeRoutine (self,function,*args,**keys):

        pass ### self.bodyCtrl.after_idle(function,*args,**keys)
    #@-node:ekr.20081004102201.225:Idle time... (gtkBody)
    #@+node:ekr.20081004102201.226:Menus (gtkBody)
    def bind (self,*args,**keys):

        pass ### return self.bodyCtrl.bind(*args,**keys)
    #@-node:ekr.20081004102201.226:Menus (gtkBody)
    #@+node:ekr.20081004102201.227:Text (now in base class) (gtkBody)
    # def getAllText (self):              return self.bodyCtrl.getAllText()
    # def getInsertPoint(self):           return self.bodyCtrl.getInsertPoint()
    # def getSelectedText (self):         return self.bodyCtrl.getSelectedText()
    # def getSelectionRange (self,sort=True): return self.bodyCtrl.getSelectionRange(sort)
    # def hasTextSelection (self):        return self.bodyCtrl.hasSelection()
    # # def scrollDown (self):            g.app.gui.yscroll(self.bodyCtrl,1,'units')
    # # def scrollUp (self):              g.app.gui.yscroll(self.bodyCtrl,-1,'units')
    # def see (self,index):               self.bodyCtrl.see(index)
    # def seeInsertPoint (self):          self.bodyCtrl.seeInsertPoint()
    # def selectAllText (self,event=None):
        # w = g.app.gui.eventWidget(event) or self.bodyCtrl
        # return w.selectAllText()
    # def setInsertPoint (self,pos):      return self.bodyCtrl.getInsertPoint(pos)
    # def setSelectionRange (self,sel):
        # i,j = sel
        # self.bodyCtrl.setSelectionRange(i,j)
    #@nonl
    #@-node:ekr.20081004102201.227:Text (now in base class) (gtkBody)
    #@-node:ekr.20081004102201.220:Tk bindings (gtkBbody)
    #@+node:ekr.20081004102201.228:Editors (gtkBody)
    #@+node:ekr.20081004102201.229:createEditorFrame
    def createEditorFrame (self,pane):

        f = gtk.Frame(pane)
        f.pack(side='top',expand=1,fill='both')
        return f
    #@-node:ekr.20081004102201.229:createEditorFrame
    #@+node:ekr.20081004102201.230:packEditorLabelWidget
    def packEditorLabelWidget (self,w):

        '''Create a gtk label widget.'''

        if not hasattr(w,'leo_label') or not w.leo_label:
            # g.trace('w.leo_frame',id(w.leo_frame))
            w.pack_forget()
            w.leo_label = gtk.Label(w.leo_frame)
            w.leo_label.pack(side='top')
            w.pack(expand=1,fill='both')
    #@nonl
    #@-node:ekr.20081004102201.230:packEditorLabelWidget
    #@+node:ekr.20081004102201.231:setEditorColors
    def setEditorColors (self,bg,fg):

        c = self.c ; d = self.editorWidgets

        ###

        # for key in d:
            # w2 = d.get(key)
            # # g.trace(id(w2),bg,fg)
            # try:
                # w2.configure(bg=bg,fg=fg)
            # except Exception:
                # g.es_exception()
                # pass
    #@-node:ekr.20081004102201.231:setEditorColors
    #@-node:ekr.20081004102201.228:Editors (gtkBody)
    #@-others
#@-node:ekr.20081004102201.210:class leoGtkBody
#@+node:ekr.20081004102201.232:== Leo Log (gtk) ==
#@+node:ekr.20081004102201.233:class LogTab
class LogTab(gtk.VBox):

    """A window used as pages in the gtkLogNotebook


    This window also manages a label wiget which can be used in
    gtk.Notebook tabs.

    """

    #@    @+others
    #@+node:ekr.20081004102201.234:__init__ (LogTab)
    def __init__(self, c,
         tabName,
         labelWidget=None,
         frameWidget=None
    ):

        """Construct a LogWindow based on a gtk.VBox widget

        tabName is the name to be used to identify this widget.

        labelWidget is the widget used as a label in notebook tabs.
            If this is None a gtk.Label widget will be used with
            its text set to tabName.

        frame widget is the initial widget to be packed into
            this VBox and may be None.

        """

        super(LogTab, self).__gobject_init__()

        self.c = c
        self.nb = None 

        self.set_size_request(10, 10)

        if frameWidget:
            self.add(frameWidget)

        self.tabName = tabName

        if not labelWidget:
            labelWidget = gtk.Label(tabName)

        self.labelWidget = labelWidget

        self.show_all()
    #@-node:ekr.20081004102201.234:__init__ (LogTab)
    #@-others


gobject.type_register(LogTab)
#@-node:ekr.20081004102201.233:class LogTab
#@+node:ekr.20081004102201.235:class _gtkLogNotebook (gtk.Notebook)
class _gtkLogNotebook (gtk.Notebook):

    """This is a wrapper around gtk.Notebook.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native Notebook object.

    Although little is being done with this at the moment, future
    enhancement may include the ability to hide tabs, to drag
    them from one notebook to another, and to pop the tabs out
    of the notebook into there own frame.

    """

    #@    @+others
    #@+node:ekr.20081004102201.236:__init__ (_gtkLogNotebook)
    def __init__ (self, c):

        """Create and wrap a gtk.Notebok. Do leo specific initailization."""

        gtk.Notebook.__gobject_init__(self)

        self.c = c
        self.tabNames = {}
    #@-node:ekr.20081004102201.236:__init__ (_gtkLogNotebook)
    #@+node:ekr.20081004102201.237:selectPage
    def selectpage(self, tabName):
        """Select the page in the notebook with name 'tabName'.

        A KeyError exception is raised if the tabName is not known.

        """

        tabCtrl = self.tabNames[tabName]

        self.set_current_page(self.page_num(tabCtrl))






    #@-node:ekr.20081004102201.237:selectPage
    #@+node:ekr.20081004102201.238:add
    def add(self, tab):
        """Add a tab as the last page in the notebook.

        'tab' may be an instance of LogTab or basestring.

        if 'tab' is a string a default LogTab will be constructed and returned
            with tab used as a tabName.

        if 'tab is a LogTab it must have tab.tabName set. If labelWidget is not
            set a gtk.Label will be used with its text set to tabName.

        either tab or a new instance of LogTab will be returned.

        """

        if isinstance(tab, basestring):
            tab = LogTab(self.c, tab)

        assert isinstance(tab, LogTab)

        tabName = tab.tabName

        tab.nb = self

        if not tab.labelWidget:
            tab.labelWidget = gtk.Label(tab.tabName)

        self.tabNames[tabName] = tab
        self.append_page(tab, tab.labelWidget)

        return tab




    #@-node:ekr.20081004102201.238:add
    #@+node:ekr.20081004102201.239:pageNames
    def pagenames(self):
        """Return a list of pagenames managed by this notebook."""

        return self.tabNames.keys()
    #@-node:ekr.20081004102201.239:pageNames
    #@-others

gobject.type_register(_gtkLogNotebook)
#@-node:ekr.20081004102201.235:class _gtkLogNotebook (gtk.Notebook)
#@+node:ekr.20081004102201.240:class leoGtkLog
class leoGtkLog (leoFrame.leoLog):

    """A class that represents the log pane of a gtk window."""

    #@    @+others
    #@+node:ekr.20081004102201.241:gtkLog Birth
    #@+node:ekr.20081004102201.242:gtkLog.__init__
    def __init__ (self,frame,parentFrame):
        """Create an instance of the leoGtkLog Adaptor class.

        All access to the funtions of this class should be via c.frame.log
        or the global methods provided.

        At the moment legCtrl is the notebook control but it should not be assumed
        that this is so 

        """

        g.trace("leoGtkLog")

        # Call the base class constructor and calls createControl.
        leoFrame.leoLog.__init__(self,frame,parentFrame)

        self.c = c = frame.c # Also set in the base constructor, but we need it here.

        self.wrap = g.choose(c.config.getBool('log_pane_wraps'),"word","none")


        self.nb = None      # _gtkLogNotebook that holds all the tabs.
        self.colorTagsDict = {} # Keys are page names.  Values are saved colorTags lists.
        self.menu = None # A menu that pops up on right clicks in the hull or in tabs.

        self.createControl(parentFrame)
        #self.setFontFromConfig()
        #self.setColorFromConfig()

    #@+at
    # #==
    #     self.c = c
    # 
    #     self.nb = gtk.Notebook()
    # 
    #     self.isNull = False
    #     self.logCtrl = None
    #     self.newlines = 0
    #     self.frameDict = {} # Keys are log names, values are None or 
    # wx.Frames.
    #     self.textDict = {}  # Keys are log names, values are None or Text 
    # controls.
    # 
    #     self.createInitialTabs()
    #     self.setFontFromConfig()
    # 
    # 
    #@-at
    #@-node:ekr.20081004102201.242:gtkLog.__init__
    #@+node:ekr.20081004102201.243:gtkLog.createControl
    def createControl (self,parentFrame):

        """Create the base gtkLog control.

        """

        c = self.c

        self.nb = _gtkLogNotebook(c)

        # menu = self.makeTabMenu(tabName=None)

        # def hullMenuCallback(event):
            # return self.onRightClick(event,menu)

        # c.bind(self.nb,'<Button-3>',hullMenuCallback)

        # self.nb.pack(fill='both',expand=1)

        # Create and activate the default tabs.
        return self.selectTab('Log')
    #@-node:ekr.20081004102201.243:gtkLog.createControl
    #@+node:ekr.20081004102201.244:gtkLog.finishCreate
    def finishCreate (self):

        # g.trace('gtkLog')

        c = self.c ; log = self

        #'c.searchCommands.openFindTab(show=False)
        #'c.spellCommands.openSpellTab()
        log.selectTab('Log')
    #@-node:ekr.20081004102201.244:gtkLog.finishCreate
    #@+node:ekr.20081004102201.245:gtkLog.createTextWidget
    def createTextWidget (self,parentFrame):

        c = self.c

        self.logNumber += 1

        log = g.app.gui.plainTextWidget(c,
            name="log-%d" % self.logNumber,
            setgrid=0,wrap=self.wrap,bd=2,bg="white",relief="flat"
        )

        # logBar = gtk.Scrollbar(parentFrame,name="logBar")

        # log['yscrollcommand'] = logBar.set
        # logBar['command'] = log.yview

        # logBar.pack(side="right", fill="y")
        # # rr 8/14/02 added horizontal elevator 
        # if self.wrap == "none": 
            # logXBar = gtk.Scrollbar( 
                # parentFrame,name='logXBar',orient="horizontal") 
            # log['xscrollcommand'] = logXBar.set 
            # logXBar['command'] = log.xview 
            # logXBar.pack(side="bottom", fill="x")
        # log.pack(expand=1, fill="both")

        return log
    #@-node:ekr.20081004102201.245:gtkLog.createTextWidget
    #@+node:ekr.20081004102201.246:gtkLog.makeTabMenu
    def makeTabMenu (self,tabName=None):

        '''Create a tab popup menu.'''

        # g.trace(tabName,g.callers())

        c = self.c
        # hull = self.nb.component('hull') # A Tk.Canvas.

        # menu = Tk.Menu(hull,tearoff=0)
        # c.add_command(menu,label='New Tab',command=self.newTabFromMenu)

        # if tabName:
            # # Important: tabName is the name when the tab is created.
            # # It is not affected by renaming, so we don't have to keep
            # # track of the correspondence between this name and what is in the label.
            # def deleteTabCallback():
                # return self.deleteTab(tabName)

            # label = g.choose(
                # tabName in ('Find','Spell'),'Hide This Tab','Delete This Tab')
            # c.add_command(menu,label=label,command=deleteTabCallback)

            # def renameTabCallback():
                # return self.renameTabFromMenu(tabName)

            # c.add_command(menu,label='Rename This Tab',command=renameTabCallback)

        # return menu
    #@-node:ekr.20081004102201.246:gtkLog.makeTabMenu
    #@-node:ekr.20081004102201.241:gtkLog Birth
    #@+node:ekr.20081004102201.247:Config & get/saveState
    #@+node:ekr.20081004102201.248:gtkLog.configureBorder & configureFont
    def configureBorder(self,border):

        self.logCtrl.configure(bd=border)

    def configureFont(self,font):

        self.logCtrl.configure(font=font)
    #@-node:ekr.20081004102201.248:gtkLog.configureBorder & configureFont
    #@+node:ekr.20081004102201.249:gtkLog.getFontConfig
    def getFontConfig (self):

        font = self.logCtrl.cget("font")
        # g.trace(font)
        return font
    #@-node:ekr.20081004102201.249:gtkLog.getFontConfig
    #@+node:ekr.20081004102201.250:gtkLog.restoreAllState
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
    #@-node:ekr.20081004102201.250:gtkLog.restoreAllState
    #@+node:ekr.20081004102201.251:gtkLog.saveAllState
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
    #@-node:ekr.20081004102201.251:gtkLog.saveAllState
    #@+node:ekr.20081004102201.252:gtkLog.setColorFromConfig
    def setColorFromConfig (self):

        c = self.c

        bg = c.config.getColor("log_pane_background_color") or 'white'

        try:
            self.logCtrl.configure(bg=bg)
        except:
            g.es("exception setting log pane background color")
            g.es_exception()
    #@-node:ekr.20081004102201.252:gtkLog.setColorFromConfig
    #@+node:ekr.20081004102201.253:gtkLog.setFontFromConfig
    def SetWidgetFontFromConfig (self,logCtrl=None):

        c = self.c

        if not logCtrl: logCtrl = self.logCtrl

        font = c.config.getFontFromParams(
            "log_text_font_family", "log_text_font_size",
            "log_text_font_slant", "log_text_font_weight",
            c.config.defaultLogFontSize)

        self.fontRef = font # ESSENTIAL: retain a link to font.
        ### logCtrl.configure(font=font)

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
    #@-node:ekr.20081004102201.253:gtkLog.setFontFromConfig
    #@-node:ekr.20081004102201.247:Config & get/saveState
    #@+node:ekr.20081004102201.254:Focus & update (gtkLog)
    #@+node:ekr.20081004102201.255:gtkLog.onActivateLog
    def onActivateLog (self,event=None):

        try:
            self.c.setLog()
            self.frame.tree.OnDeactivate()
            self.c.logWantsFocus()
        except:
            g.es_event_exception("activate log")
    #@-node:ekr.20081004102201.255:gtkLog.onActivateLog
    #@+node:ekr.20081004102201.256:gtkLog.hasFocus
    def hasFocus (self):

        return self.c.get_focus() == self.logCtrl
    #@-node:ekr.20081004102201.256:gtkLog.hasFocus
    #@+node:ekr.20081004102201.257:forceLogUpdate
    def forceLogUpdate (self,s):

        if sys.platform == "darwin": # Does not work on MacOS X.
            try:
                g.pr(s,newline=False) # Don't add a newline.
            except UnicodeError:
                # g.app may not be inited during scripts!
                g.pr(g.toEncodedString(s,'utf-8'))
        else:
            self.logCtrl.update_idletasks()
    #@-node:ekr.20081004102201.257:forceLogUpdate
    #@-node:ekr.20081004102201.254:Focus & update (gtkLog)
    #@+node:ekr.20081004102201.258:put & putnl (gtkLog)
    #@+at 
    #@nonl
    # Printing uses self.logCtrl, so this code need not concern itself
    # with which tab is active.
    # 
    # Also, selectTab switches the contents of colorTags, so that is not 
    # concern.
    # It may be that Pmw will allow us to dispense with the colorTags logic...
    #@-at
    #@+node:ekr.20081004102201.259:put
    # All output to the log stream eventually comes here.
    def put (self,s,color=None,tabName='Log'):

        c = self.c

        #g.pr('gtkLog.put', s, color, tabName #self.c.shortFileName(),tabName,g.callers())

        if g.app.quitting or not c or not c.exists:
            return

        if tabName:
            self.selectTab(tabName)

        if self.logCtrl:
            #@        << put s to log control >>
            #@+node:ekr.20081004102201.260:<< put s to log control >>
            # if color:
                # if color not in self.colorTags:
                    # self.colorTags.append(color)
                    # self.logCtrl.tag_config(color,foreground=color)
                # self.logCtrl.insert("end",s)
                # self.logCtrl.tag_add(color,"end-%dc" % (len(s)+1),"end-1c")
                # self.logCtrl.tag_add("black","end")
            # else:
                # self.logCtrl.insert("end",s)

            self.logCtrl.insert("end",s)
            self.logCtrl.see('end')
            #self.forceLogUpdate(s)
            #@-node:ekr.20081004102201.260:<< put s to log control >>
            #@nl
    #@nonl
    #@-node:ekr.20081004102201.259:put
    #@+node:ekr.20081004102201.261:putnl
    def putnl (self,tabName='Log'):


        if g.app.quitting:
            return

        if tabName:
            self.selectTab(tabName)

        if self.logCtrl:
            self.logCtrl.insert("end",'\n')
            self.logCtrl.see('end')
            # self.forceLogUpdate('\n')
    #@nonl
    #@-node:ekr.20081004102201.261:putnl
    #@-node:ekr.20081004102201.258:put & putnl (gtkLog)
    #@+node:ekr.20081004102201.262:Tab (GtkLog)
    #@+node:ekr.20081004102201.263:clearTab
    def clearTab (self,tabName,wrap='none'):

        self.selectTab(tabName,wrap=wrap)
        w = self.logCtrl
        w and w.delete(0,'end')
    #@-node:ekr.20081004102201.263:clearTab
    #@+node:ekr.20081004102201.264:createTab
    def createTab (self,tabName,createText=True,wrap='none'):

        g.trace(tabName,wrap)

        c = self.c ; k = c.k

        tabFrame = self.nb.add(tabName)

        #widget = TestWindow('leo pink', 'yellow')
        #tabFrame.add(widget)

        #self.textDict [tabName] = None
        #self.frameDict [tabName] = tabFrame

        # self.menu = self.makeTabMenu(tabName)
        if createText:
            #@        << Create the tab's text widget >>
            #@+node:ekr.20081004102201.265:<< Create the tab's text widget >>
            w = self.createTextWidget(tabFrame)

            # # Set the background color.
            # configName = 'log_pane_%s_tab_background_color' % tabName
            # bg = c.config.getColor(configName) or 'MistyRose1'

            # if wrap not in ('none','char','word'): wrap = 'none'
            # try: w.configure(bg=bg,wrap=wrap)
            # except Exception: pass # Could be a user error.

            # self.SetWidgetFontFromConfig(logCtrl=w)

            self.frameDict [tabName] = tabFrame
            self.textDict [tabName] = w
            tabFrame.add(w.widget)
            tabFrame.show_all()

            # # Switch to a new colorTags list.
            # if self.tabName:
                # self.colorTagsDict [self.tabName] = self.colorTags [:]

            #self.colorTags = ['black']
            #self.colorTagsDict [tabName] = self.colorTags
            #@-node:ekr.20081004102201.265:<< Create the tab's text widget >>
            #@nl
            # if tabName != 'Log':
                # # c.k doesn't exist when the log pane is created.
                # # k.makeAllBindings will call setTabBindings('Log')
                # self.setTabBindings(tabName)
        else:
            self.textDict [tabName] = None
            self.frameDict [tabName] = tabFrame


    #@-node:ekr.20081004102201.264:createTab
    #@+node:ekr.20081004102201.266:cycleTabFocus
    def cycleTabFocus (self,event=None,stop_w = None):

        '''Cycle keyboard focus between the tabs in the log pane.'''

        c = self.c ; d = self.frameDict # Keys are page names. Values are gtk.Frames.
        w = d.get(self.tabName)
        # g.trace(self.tabName,w)
        values = d.values()
        if self.numberOfVisibleTabs() > 1:
            i = i2 = values.index(w) + 1
            if i == len(values): i = 0
            tabName = d.keys()[i]
            self.selectTab(tabName)
            return 
    #@nonl
    #@-node:ekr.20081004102201.266:cycleTabFocus
    #@+node:ekr.20081004102201.267:deleteTab
    def deleteTab (self,tabName,force=False):

        if tabName == 'Log':
            pass

        elif tabName in ('Find','Spell') and not force:
            self.selectTab('Log')

        elif tabName in self.nb.pagenames():
            # # g.trace(tabName,force)
            self.nb.delete(tabName)
            # self.colorTagsDict [tabName] = []
            self.textDict [tabName] = None
            self.frameDict [tabName] = None
            self.tabName = None
            self.selectTab('Log')

        # New in Leo 4.4b1.
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20081004102201.267:deleteTab
    #@+node:ekr.20081004102201.268:hideTab
    def hideTab (self,tabName):

        self.selectTab('Log')
    #@-node:ekr.20081004102201.268:hideTab
    #@+node:ekr.20081004102201.269:getSelectedTab
    def getSelectedTab (self):

        return self.tabName
    #@-node:ekr.20081004102201.269:getSelectedTab
    #@+node:ekr.20081004102201.270:lower/raiseTab
    def lowerTab (self,tabName):

        # if tabName:
            # b = self.nb.tab(tabName) # b is a gtk.Button.
            # b.config(bg='grey80')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab (self,tabName):

        # if tabName:
            # b = self.nb.tab(tabName) # b is a gtk.Button.
            # b.config(bg='LightSteelBlue1')
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@-node:ekr.20081004102201.270:lower/raiseTab
    #@+node:ekr.20081004102201.271:numberOfVisibleTabs
    def numberOfVisibleTabs (self):

        return len([val for val in self.frameDict.values() if val != None])
    #@-node:ekr.20081004102201.271:numberOfVisibleTabs
    #@+node:ekr.20081004102201.272:renameTab
    def renameTab (self,oldName,newName):

        # g.trace('newName',newName)

        # label = self.nb.tab(oldName)
        # label.configure(text=newName)

        pass
    #@-node:ekr.20081004102201.272:renameTab
    #@+node:ekr.20081004102201.273:selectTab
    def selectTab (self,tabName,createText=True,wrap='none'):

        '''Create the tab if necessary and make it active.'''

        c = self.c

        tabFrame = self.frameDict.get(tabName)
        logCtrl = self.textDict.get(tabName)

        #g.trace(tabFrame, logCtrl)

        if not tabFrame or not logCtrl:
            self.createTab(tabName,createText=createText,wrap=wrap)

        self.nb.selectpage(tabName)

        # # Update the status vars.
        self.tabName = tabName
        self.logCtrl = self.textDict.get(tabName)
        self.tabFrame = self.frameDict.get(tabName)

        # if 0: # Absolutely do not do this here!  It is a cause of the 'sticky focus' problem.
            # c.widgetWantsFocusNow(self.logCtrl)
        return tabFrame
    #@-node:ekr.20081004102201.273:selectTab
    #@+node:ekr.20081004102201.274:setTabBindings
    def setTabBindings (self,tabName):

        c = self.c ; k = c.k
        # tab = self.nb.tab(tabName)
        # w = self.textDict.get(tabName)

        # # Send all event in the text area to the master handlers.
        # for kind,handler in (
            # ('<Key>',       k.masterKeyHandler),
            # ('<Button-1>',  k.masterClickHandler),
            # ('<Button-3>',  k.masterClick3Handler),
        # ):
            # c.bind(w,kind,handler)

        # # Clicks in the tab area are harmless: use the old code.
        # def tabMenuRightClickCallback(event,menu=self.menu):
            # return self.onRightClick(event,menu)

        # def tabMenuClickCallback(event,tabName=tabName):
            # return self.onClick(event,tabName)

        # c.bind(tab,'<Button-1>',tabMenuClickCallback)
        # c.bind(tab,'<Button-3>',tabMenuRightClickCallback)

        # k.completeAllBindingsForWidget(w)
    #@-node:ekr.20081004102201.274:setTabBindings
    #@+node:ekr.20081004102201.275:Tab menu callbacks & helpers
    #@+node:ekr.20081004102201.276:onRightClick & onClick
    def onRightClick (self,event,menu):

        c = self.c
        menu.post(event.x_root,event.y_root)


    def onClick (self,event,tabName):

        self.selectTab(tabName)
    #@-node:ekr.20081004102201.276:onRightClick & onClick
    #@+node:ekr.20081004102201.277:newTabFromMenu
    def newTabFromMenu (self,tabName='Log'):

        self.selectTab(tabName)

        # This is called by getTabName.
        def selectTabCallback (newName):
            return self.selectTab(newName)

        self.getTabName(selectTabCallback)
    #@-node:ekr.20081004102201.277:newTabFromMenu
    #@+node:ekr.20081004102201.278:renameTabFromMenu
    def renameTabFromMenu (self,tabName):

        if tabName in ('Log','Completions'):
            g.es('can not rename',tabName,'tab',color='blue')
        else:
            def renameTabCallback (newName):
                return self.renameTab(tabName,newName)

            self.getTabName(renameTabCallback)
    #@-node:ekr.20081004102201.278:renameTabFromMenu
    #@+node:ekr.20081004102201.279:getTabName
    def getTabName (self,exitCallback):

        canvas = self.nb.component('hull')

        # Overlay what is there!
        c = self.c
        f = gtk.Frame(canvas)
        f.pack(side='top',fill='both',expand=1)

        row1 = gtk.Frame(f)
        row1.pack(side='top',expand=0,fill='x',pady=10)
        row2 = gtk.Frame(f)
        row2.pack(side='top',expand=0,fill='x')

        gtk.Label(row1,text='Tab name').pack(side='left')

        e = gtk.Entry(row1,background='white')
        e.pack(side='left')

        def getNameCallback (event=None):
            s = e.get().strip()
            f.pack_forget()
            if s: exitCallback(s)

        def closeTabNameCallback (event=None):
            f.pack_forget()

        b = gtk.Button(row2,text='Ok',width=6,command=getNameCallback)
        b.pack(side='left',padx=10)

        b = gtk.Button(row2,text='Cancel',width=6,command=closeTabNameCallback)
        b.pack(side='left')

        g.app.gui.set_focus(c,e)
        c.bind(e,'<Return>',getNameCallback)
    #@-node:ekr.20081004102201.279:getTabName
    #@-node:ekr.20081004102201.275:Tab menu callbacks & helpers
    #@-node:ekr.20081004102201.262:Tab (GtkLog)
    #@+node:ekr.20081004102201.280:gtkLog color tab stuff
    def createColorPicker (self,tabName):

        log = self

        #@    << define colors >>
        #@+node:ekr.20081004102201.281:<< define colors >>
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
        #@-node:ekr.20081004102201.281:<< define colors >>
        #@nl

        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        colors = list(colors)
        bg = parent.cget('background')

        outer = gtk.Frame(parent,background=bg)
        outer.pack(side='top',fill='both',expand=1,pady=10)

        f = gtk.Frame(outer)
        f.pack(side='top',expand=0,fill='x')
        f1 = gtk.Frame(f) ; f1.pack(side='top',expand=0,fill='x')
        f2 = gtk.Frame(f) ; f2.pack(side='top',expand=1,fill='x')
        f3 = gtk.Frame(f) ; f3.pack(side='top',expand=1,fill='x')

        label = g.app.gui.plainTextWidget(f1,height=1,width=20)
        label.insert('1.0','Color name or value...')
        label.pack(side='left',pady=6)

        #@    << create optionMenu and callback >>
        #@+node:ekr.20081004102201.282:<< create optionMenu and callback >>
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
        #@-node:ekr.20081004102201.282:<< create optionMenu and callback >>
        #@nl
        #@    << create picker button and callback >>
        #@+node:ekr.20081004102201.283:<< create picker button and callback >>
        def pickerCallback ():
            rgb,val = gtkColorChooser.askcolor(parent=parent,initialcolor=f.cget('background'))
            if rgb or val:
                # label.configure(text=val)
                label.delete('1.0','end')
                label.insert('1.0',val)
                for theFrame in (parent,outer,f,f1,f2,f3):
                    theFrame.configure(background=val)

        b = gtk.Button(f3,text="Color Picker...",
            command=pickerCallback,background=bg)
        b.pack(side='left',pady=4)
        #@-node:ekr.20081004102201.283:<< create picker button and callback >>
        #@nl
    #@-node:ekr.20081004102201.280:gtkLog color tab stuff
    #@+node:ekr.20081004102201.284:gtkLog font tab stuff
    #@+node:ekr.20081004102201.285:createFontPicker
    def createFontPicker (self,tabName):

        log = self ; c = self.c
        parent = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        bg = parent.cget('background')
        font = self.getFont()
        #@    << create the frames >>
        #@+node:ekr.20081004102201.286:<< create the frames >>
        f = gtk.Frame(parent,background=bg) ; f.pack (side='top',expand=0,fill='both')
        f1 = gtk.Frame(f,background=bg)     ; f1.pack(side='top',expand=1,fill='x')
        f2 = gtk.Frame(f,background=bg)     ; f2.pack(side='top',expand=1,fill='x')
        f3 = gtk.Frame(f,background=bg)     ; f3.pack(side='top',expand=1,fill='x')
        f4 = gtk.Frame(f,background=bg)     ; f4.pack(side='top',expand=1,fill='x')
        #@-node:ekr.20081004102201.286:<< create the frames >>
        #@nl
        #@    << create the family combo box >>
        #@+node:ekr.20081004102201.287:<< create the family combo box >>
        names = gtkFont.families()
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
        #@-node:ekr.20081004102201.287:<< create the family combo box >>
        #@nl
        #@    << create the size entry >>
        #@+node:ekr.20081004102201.288:<< create the size entry >>
        gtk.Label(f2,text="Size:",width=10,background=bg).pack(side="left")

        sizeEntry = gtk.Entry(f2,width=4)
        sizeEntry.insert(0,'12')
        sizeEntry.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004102201.288:<< create the size entry >>
        #@nl
        #@    << create the weight combo box >>
        #@+node:ekr.20081004102201.289:<< create the weight combo box >>
        weightBox = Pmw.ComboBox(f3,
            labelpos="we",label_text="Weight:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['normal','bold'])

        weightBox.selectitem(0)
        weightBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004102201.289:<< create the weight combo box >>
        #@nl
        #@    << create the slant combo box >>
        #@+node:ekr.20081004102201.290:<< create the slant combo box>>
        slantBox = Pmw.ComboBox(f4,
            labelpos="we",label_text="Slant:",label_width=10,
            label_background=bg,
            arrowbutton_background=bg,
            scrolledlist_items=['roman','italic'])

        slantBox.selectitem(0)
        slantBox.pack(side="left",padx=2,pady=2)
        #@-node:ekr.20081004102201.290:<< create the slant combo box>>
        #@nl
        #@    << create the sample text widget >>
        #@+node:ekr.20081004102201.291:<< create the sample text widget >>
        self.sampleWidget = sample = g.app.gui.plainTextWidget(f,height=20,width=80,font=font)
        sample.pack(side='left')

        s = 'The quick brown fox\njumped over the lazy dog.\n0123456789'
        sample.insert(0,s)
        #@-node:ekr.20081004102201.291:<< create the sample text widget >>
        #@nl
        #@    << create and bind the callbacks >>
        #@+node:ekr.20081004102201.292:<< create and bind the callbacks >>
        def fontCallback(event=None):
            self.setFont(familyBox,sizeEntry,slantBox,weightBox,sample)

        for w in (familyBox,slantBox,weightBox):
            w.configure(selectioncommand=fontCallback)

        c.bind(sizeEntry,'<Return>',fontCallback)
        #@-node:ekr.20081004102201.292:<< create and bind the callbacks >>
        #@nl
        self.createBindings()
    #@-node:ekr.20081004102201.285:createFontPicker
    #@+node:ekr.20081004102201.293:createBindings (fontPicker)
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
    #@-node:ekr.20081004102201.293:createBindings (fontPicker)
    #@+node:ekr.20081004102201.294:getFont
    def getFont(self,family=None,size=12,slant='roman',weight='normal'):

        try:
            return gtkFont.Font(family=family,size=size,slant=slant,weight=weight)
        except Exception:
            g.es("exception setting font")
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20081004102201.294:getFont
    #@+node:ekr.20081004102201.295:setFont
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
    #@-node:ekr.20081004102201.295:setFont
    #@+node:ekr.20081004102201.296:hideFontTab
    def hideFontTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@-node:ekr.20081004102201.296:hideFontTab
    #@-node:ekr.20081004102201.284:gtkLog font tab stuff
    #@-others
#@-node:ekr.20081004102201.240:class leoGtkLog
#@-node:ekr.20081004102201.232:== Leo Log (gtk) ==
#@+node:ekr.20081004102201.297:class leoGtkTreeTab
class leoGtkTreeTab (leoFrame.leoTreeTab):

    '''A class representing a tabbed outline pane drawn with gtk.'''

    #@    @+others
    #@+node:ekr.20081004102201.298: Birth & death
    #@+node:ekr.20081004102201.299: ctor (leoTreeTab)
    def __init__ (self,c,parentFrame,chapterController):

        leoFrame.leoTreeTab.__init__ (self,c,chapterController,parentFrame)
            # Init the base class.  Sets self.c, self.cc and self.parentFrame.

        self.tabNames = [] # The list of tab names.  Changes when tabs are renamed.

        self.createControl()
    #@-node:ekr.20081004102201.299: ctor (leoTreeTab)
    #@+node:ekr.20081004102201.300:tt.createControl
    def createControl (self):

        tt = self ; c = tt.c

        # Create the main container.
        tt.frame = gtk.Frame(c.frame.iconFrame)
        tt.frame.pack(side="left")

        # Create the chapter menu.
        self.chapterVar = var = gtk.StringVar()
        var.set('main')

        tt.chapterMenu = menu = Pmw.OptionMenu(tt.frame,
            labelpos = 'w', label_text = 'chapter',
            menubutton_textvariable = var,
            items = [],
            command = tt.selectTab,
        )
        menu.pack(side='left',padx=5)
    #@nonl
    #@-node:ekr.20081004102201.300:tt.createControl
    #@-node:ekr.20081004102201.298: Birth & death
    #@+node:ekr.20081004102201.301:Tabs...
    #@+node:ekr.20081004102201.302:tt.createTab
    def createTab (self,tabName,select=True):

        tt = self

        if tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@-node:ekr.20081004102201.302:tt.createTab
    #@+node:ekr.20081004102201.303:tt.destroyTab
    def destroyTab (self,tabName):

        tt = self

        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@-node:ekr.20081004102201.303:tt.destroyTab
    #@+node:ekr.20081004102201.304:tt.selectTab
    def selectTab (self,tabName):

        tt = self

        if tabName not in self.tabNames:
            tt.createTab(tabName)

        tt.cc.selectChapterByName(tabName)
    #@-node:ekr.20081004102201.304:tt.selectTab
    #@+node:ekr.20081004102201.305:tt.setTabLabel
    def setTabLabel (self,tabName):

        tt = self
        tt.chapterVar.set(tabName)
    #@-node:ekr.20081004102201.305:tt.setTabLabel
    #@+node:ekr.20081004102201.306:tt.setNames
    def setNames (self):

        '''Recreate the list of items.'''

        tt = self
        names = tt.tabNames[:]
        if 'main' in names: names.remove('main')
        names.sort()
        names.insert(0,'main')
        tt.chapterMenu.setitems(names)
    #@-node:ekr.20081004102201.306:tt.setNames
    #@-node:ekr.20081004102201.301:Tabs...
    #@-others
#@nonl
#@-node:ekr.20081004102201.297:class leoGtkTreeTab
#@+node:ekr.20081004102201.307:== Leo Text Widget (gtk) ==
#@+node:ekr.20081004102201.308:class _gtkText
class _gtkText (gtk.TextView):

    """This is a wrapper around gtk.Notebook.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native Notebook object.

    """

    #@    @+others
    #@+node:ekr.20081004102201.309:__init__ (_gtkText)
    def __init__ (self, c, *args, **kw):

        """Create and wrap a gtk.TextView. Do leo specific initailization."""

        gtk.TextView.__gobject_init__(self)
        self.c = c
    #@nonl
    #@-node:ekr.20081004102201.309:__init__ (_gtkText)
    #@-others

gobject.type_register(_gtkText)
#@-node:ekr.20081004102201.308:class _gtkText
#@+node:ekr.20081004102201.310:class leoGtkTextWidget
class leoGtkTextWidget(leoFrame.baseTextWidget):

    '''A class to wrap the gtk.Text widget.'''

    def __repr__(self):
        name = hasattr(self,'_name') and self._name or '<no name>'
        return 'gtkTextWidget id: %s name: %s' % (id(self),name)

    #@    @+others
    #@+node:ekr.20081004102201.311:gtkTextWidget.__init__

    def __init__ (self, c, *args,**keys):

        self.c = c

        # Create the actual gui widget.
        self.widget = w = gtk.ScrolledWindow()
        w.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.textView = _gtkText(c, *args, **keys)
        self.textBuffer = buf = self.textView.get_buffer()

        w.add(self.textView)
        w.show_all()

        #create a mark with left gravity for our use
        self.iMark = buf.create_mark('iMark', buf.get_start_iter(), False)

        #create a mark with right gravity
        self.jMark = buf.create_mark('jMark', buf.get_end_iter(), True)

        ### To do: how an where to pack widget

        # Init the base class.
        name = keys.get('name') or '<unknown gtkTextWidget>'
        leoFrame.baseTextWidget.__init__(self,c=c,
            baseClassName='gtkTextWidget',name=name,widget=self.widget
        )

        # self.defaultFont = font = wx.Font(pointSize=10,
            # family = wx.FONTFAMILY_TELETYPE, # wx.FONTFAMILY_ROMAN,
            # style  = wx.FONTSTYLE_NORMAL,
            # weight = wx.FONTWEIGHT_NORMAL,)
    #@-node:ekr.20081004102201.311:gtkTextWidget.__init__
    #@+node:ekr.20081004102201.312:bindings (not used)
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
    # def _hitTest(self,pos):             pass ###
    # def _insertText(self,i,s):          return self.widget.insert(i,s)
    # def _scrollLines(self,n):           pass ###
    # def _see(self,i):                   return self.widget.see(i)
    # def _setAllText(self,s):            self.widget.delete('1.0','end') ; self.widget.insert('1.0',s)
    # def _setBackgroundColor(self,color): return self.widget.configure(background=color)
    # def _setForegroundColor(self,color): return self.widget.configure(background=color)
    # def _setFocus(self):                return self.widget.focus_set()
    # def _setInsertPoint(self,i):        return self.widget.mark_set('insert',i)
    # def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)
    #@-node:ekr.20081004102201.312:bindings (not used)
    #@+node:ekr.20081004102201.313:Index conversion (gtkTextWidget)
    #@+node:ekr.20081004102201.314:w.toGuiIndex

    def toGuiIndex (self,i,s=None):
        '''Convert a Python index to a tk index as needed.'''

        w = self
        if i is None:
            g.trace('can not happen: i is None',g.callers())
            return '1.0'
        elif type(i) == type(99):
            # The 's' arg supports the threaded colorizer.
            if s is None:
                # This *must* be 'end-1c', even if other code must change.
                s = '' ### s = gtk.Text.get(w,'1.0','end-1c')
            row,col = g.convertPythonIndexToRowCol(s,i)
            i = '%s.%s' % (row+1,col)
            # g.trace(len(s),i,repr(s))
        else:
            try:
                i = 0 ### i = gtk.Text.index(w,i)
            except Exception:
                # g.es_exception()
                g.trace('tk.Text.index failed:',repr(i),g.callers())
                i = '1.0'
        return i
    #@-node:ekr.20081004102201.314:w.toGuiIndex
    #@+node:ekr.20081004102201.315:toGtkIter
    def toGtkIter (self,i):
        '''Convert a tk index to gtk.TextIter as needed.'''

        try:
            i = int(i)
            return self.textBuffer.get_iter_at_offset(i)
        except ValueError:
            pass

        if i == 'end':
            return self.textBuffer.get_end_iter()


        if i is None:
            g.trace('can not happen: i is None')
            pos = 0

        elif isinstance(i, basestring):
            g.trace(i)
            s = self.getAllText()
            #i = '1.0' ### i = gtk.Text.index(w,i) # Convert to row/column form.
            row,col = i.split('.')
            row,col = int(row),int(col)
            row -= 1
            pos = g.convertRowColToPythonIndex(s,row,col)
            #g.es_print(i)

        return self.textBuffer.get_iter_at_offset(i)
    #@-node:ekr.20081004102201.315:toGtkIter
    #@+node:ekr.20081004102201.316:w.toPythonIndex
    def toPythonIndex (self,i):
        '''Convert a tk inde iter to a Python index as needed.'''

        w =self
        if i is None:
            g.trace('can not happen: i is None')
            return 0
        elif type(i) in (type('a'),type(u'a')):
            s = '' ### s = gtk.Text.get(w,'1.0','end') # end-1c does not work.
            i = '1.0' ### i = gtk.Text.index(w,i) # Convert to row/column form.
            row,col = i.split('.')
            row,col = int(row),int(col)
            row -= 1
            i = g.convertRowColToPythonIndex(s,row,col)
            #g.es_print(i)
        return i
    #@-node:ekr.20081004102201.316:w.toPythonIndex
    #@+node:ekr.20081004102201.317:w.rowColToGuiIndex
    # This method is called only from the colorizer.
    # It provides a huge speedup over naive code.

    def rowColToGuiIndex (self,s,row,col):

        return '%s.%s' % (row+1,col)
    #@nonl
    #@-node:ekr.20081004102201.317:w.rowColToGuiIndex
    #@-node:ekr.20081004102201.313:Index conversion (gtkTextWidget)
    #@+node:ekr.20081004102201.318:getName (gtkText)
    def getName (self):

        w = self
        return hasattr(w,'_name') and w._name or repr(w)
    #@nonl
    #@-node:ekr.20081004102201.318:getName (gtkText)
    #@+node:ekr.20081004102201.319:_setSelectionRange
    if 0:
        def _setSelectionRange (self,i,j,insert=None):

            w = self.widget

            i,j = w.toGuiIndex(i),w.toGuiIndex(j)

            # g.trace('i,j,insert',repr(i),repr(j),repr(insert),g.callers())

            # g.trace('i,j,insert',i,j,repr(insert))
            if w.compare(w,i, ">", j): i,j = j,i
            w.tag_remove(w,"sel","1.0",i)
            w.tag_add(w,"sel",i,j)
            w.tag_remove(w,"sel",j,"end")

            if insert is not None:
                w.setInsertPoint(insert)
    #@-node:ekr.20081004102201.319:_setSelectionRange
    #@+node:ekr.20081004102201.320:Wrapper methods (gtkTextWidget)
    #@+node:ekr.20081004102201.321:after_idle
    def after_idle(self,*args,**keys):

        pass
    #@-node:ekr.20081004102201.321:after_idle
    #@+node:ekr.20081004102201.322:bind
    def bind (self,*args,**keys):

        pass
    #@-node:ekr.20081004102201.322:bind
    #@+node:ekr.20081004102201.323:delete
    def delete(self,i,j=None):
        """Delete chars between i and j or single char at i if j is None."""

        b = self.textBuffer

        i = self.toGtkIter(i)

        if j is None:
            j = i + 1
        else:
            j = self.toGtkIter(j)

        self.textBuffer.delete(i, j)

    #@-node:ekr.20081004102201.323:delete
    #@+node:ekr.20081004102201.324:flashCharacter
    def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75): # gtkTextWidget.

        w = self

        # def addFlashCallback(w,count,index):
            # # g.trace(count,index)
            # i,j = w.toGuiIndex(index),w.toGuiIndex(index+1)
            # gtk.Text.tag_add(w,'flash',i,j)
            # gtk.Text.after(w,delay,removeFlashCallback,w,count-1,index)

        # def removeFlashCallback(w,count,index):
            # # g.trace(count,index)
            # gtk.Text.tag_remove(w,'flash','1.0','end')
            # if count > 0:
                # gtk.Text.after(w,delay,addFlashCallback,w,count,index)

        # try:
            # gtk.Text.tag_configure(w,'flash',foreground=fg,background=bg)
            # addFlashCallback(w,flashes,i)
        # except Exception:
            # pass ; g.es_exception()
    #@nonl
    #@-node:ekr.20081004102201.324:flashCharacter
    #@+node:ekr.20081004102201.325:get
    def get(self,i,j=None):
        """Get a range of text from i to j or just the char at i if j is None."""

        buf = self.textBuffer

        i = self.toGtkIter(i)


        if j is None:
            j = i + 1
        else:
            j = self.toGtkIter(j)

        return buf.get_text(i, j)
    #@-node:ekr.20081004102201.325:get
    #@+node:ekr.20081004102201.326:getAllText
    def getAllText (self):
        """Return all the text from the currently selected text buffer."""

        buf = self.textBuffer

        return buf.get_text(buf.get_start_iter(), buf.get_end_iter())


    #@-node:ekr.20081004102201.326:getAllText
    #@+node:ekr.20081004102201.327:getInsertPoint
    def getInsertPoint(self): # gtkTextWidget.

        buf = self.textBuffer

        return buf.get_iter_at_mark(buf.get_insert()).get_offset()
    #@-node:ekr.20081004102201.327:getInsertPoint
    #@+node:ekr.20081004102201.328:getSelectedText
    def getSelectedText (self): # gtkTextWidget.

        buf = self.textBuffer

        if not buf.get_has_selection():
            return u''

        i, j = buf.get_selection_bounds()

        return buf.get_text(i, j)
    #@nonl
    #@-node:ekr.20081004102201.328:getSelectedText
    #@+node:ekr.20081004102201.329:getSelectionRange
    def getSelectionRange (self,sort=True): # gtkTextWidget.

        """Return a tuple representing the selected range.

        Return a tuple giving the insertion point if no range of text is selected."""


        buf = self.textBuffer

        if buf.get_has_selection():

            i, j = buf.get_selection_bounds()
            i, j = i.get_offset(), j.get_offset()

        else:
            i = j = self.getInsertionPoint()

        if sort and i > j:
            i,j = j,i

        return self.toGuiIndex(i), self.toGuiIndex(j)
    #@-node:ekr.20081004102201.329:getSelectionRange
    #@+node:ekr.20081004102201.330:getYScrollPosition
    def getYScrollPosition (self):

         w = self
         return 0 ### return w.yview()
    #@-node:ekr.20081004102201.330:getYScrollPosition
    #@+node:ekr.20081004102201.331:getWidth
    def getWidth (self):

        '''Return the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        return 0 ### return w.cget('width')
    #@-node:ekr.20081004102201.331:getWidth
    #@+node:ekr.20081004102201.332:hasSelection
    def hasSelection (self):

        return self.textBuffer.get_has_selection()
    #@-node:ekr.20081004102201.332:hasSelection
    #@+node:ekr.20081004102201.333:insert

    def insert(self,i,s):
        """Insert a string s at position i."""

        i = self.toGtkIter(i)

        self.textBuffer.insert(i, s)

    #@-node:ekr.20081004102201.333:insert
    #@+node:ekr.20081004102201.334:indexIsVisible
    def indexIsVisible (self,i):

        w = self

        return True ### return w.dlineinfo(i)
    #@nonl
    #@-node:ekr.20081004102201.334:indexIsVisible
    #@+node:ekr.20081004102201.335:mark_set NO LONGER USED
    # def mark_set(self,markName,i):

        # w = self
        # i = w.toGuiIndex(i)
        # gtk.Text.mark_set(w,markName,i)
    #@-node:ekr.20081004102201.335:mark_set NO LONGER USED
    #@+node:ekr.20081004102201.336:replace
    def replace (self,i,j,s): # gtkTextWidget

        """ replace text between i an j with string s.

        i and j could be in 'r.c' form

        """
        w = self
        buf = w.textBuffer

        i = w.toGtkIter(i)

        if j is None:
            j = i + 1
        else:
            j = w.toGtkIter(j)

        buf.delete(i, j)
        buf.insert(i, s)


    #@-node:ekr.20081004102201.336:replace
    #@+node:ekr.20081004102201.337:see
    def see (self,i): # gtkTextWidget.
        """Scrolls the textview the minimum distance to place the position i onscreen."""

        w = self

        i = self.toGtkIter(i)

        w.textBuffer.move_mark(w.iMark, i)
        w.textView.scroll_mark_onscreen(w.iMark)
    #@-node:ekr.20081004102201.337:see
    #@+node:ekr.20081004102201.338:seeInsertPoint
    def seeInsertPoint (self): # gtkTextWidget.

        buf = self.textBuffer

        self.textView.scroll_mark_onscreen(buf.get_insert())
    #@-node:ekr.20081004102201.338:seeInsertPoint
    #@+node:ekr.20081004102201.339:selectAllText
    def selectAllText (self,insert=None): # gtkTextWidget

        '''Select all text of the widget, *not* including the extra newline.

        ??? what to do about insert, i don't know how to set the selection range
            without setting the insertion point.
        '''

        w = self

        buf = w.textBuffer

        start = buf.get_start_iter()
        end = buf.get_end_iter()

        end.backward_char()

        buf.select_range(start, end)


    #@-node:ekr.20081004102201.339:selectAllText
    #@+node:ekr.20081004102201.340:setAllText
    def setAllText (self,s): # gtkTextWidget

        self.textBuffer.set_text(s)

        # state = gtk.Text.cget(w,"state")
        # gtk.Text.configure(w,state="normal")

        # gtk.Text.delete(w,'1.0','end')
        # gtk.Text.insert(w,'1.0',s)

        # gtk.Text.configure(w,state=state)
    #@-node:ekr.20081004102201.340:setAllText
    #@+node:ekr.20081004102201.341:setBackgroundColor
    def setBackgroundColor (self,color):

        w = self
        w.configure(background=color)
    #@nonl
    #@-node:ekr.20081004102201.341:setBackgroundColor
    #@+node:ekr.20081004102201.342:setInsertPoint
    def setInsertPoint (self,i): # gtkTextWidget.
        """Set the insertion point.

        i is a python index.

        """
        w = self

        i = w.toGtkIter(i)
        w.textBuffer.place_cursor(i)

        # g.trace(i,g.callers())
        ### gtk.Text.mark_set(w,'insert',i)
    #@-node:ekr.20081004102201.342:setInsertPoint
    #@+node:ekr.20081004102201.343:setSelectionRange
    def setSelectionRange (self,i,j,insert=None): # gtkTextWidget

        """Select a range in the text buffer.

        i, j are pyton indexes

        ??? This uses the insertion point which can not be set seperatly.

        """
        w = self

        i = w.toGtkIter(i)
        j = w.toGtkIter(j)

        w.textBuffer.select_range(i, j)

        # g.trace('i,j,insert',repr(i),repr(j),repr(insert),g.callers())

        # g.trace('i,j,insert',i,j,repr(insert))

        ###
        # if gtk.Text.compare(w,i, ">", j): i,j = j,i
        # gtk.Text.tag_remove(w,"sel","1.0",i)
        # gtk.Text.tag_add(w,"sel",i,j)
        # gtk.Text.tag_remove(w,"sel",j,"end")

        # if insert is not None:
            # w.setInsertPoint(insert)
    #@-node:ekr.20081004102201.343:setSelectionRange
    #@+node:ekr.20081004102201.344:setYScrollPosition
    def setYScrollPosition (self,i):

         w = self
         w.yview('moveto',i)
    #@nonl
    #@-node:ekr.20081004102201.344:setYScrollPosition
    #@+node:ekr.20081004102201.345:setWidth
    def setWidth (self,width):

        '''Set the width of the widget.
        This is only called for headline widgets,
        and gui's may choose not to do anything here.'''

        w = self
        #w.configure(width=width)
    #@-node:ekr.20081004102201.345:setWidth
    #@+node:ekr.20081004102201.346:tag_add
    # The signature is slightly different than the gtk.Text.insert method.

    def tag_add(self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        # if j is None:
            # gtk.Text.tag_add(w,tagName,i,*args)
        # else:
            # j = w.toGuiIndex(j)
            # gtk.Text.tag_add(w,tagName,i,j,*args)

    #@-node:ekr.20081004102201.346:tag_add
    #@+node:ekr.20081004102201.347:tag_configure
    def tag_configure (self,*args,**keys):

        pass

    tag_config = tag_configure
    #@-node:ekr.20081004102201.347:tag_configure
    #@+node:ekr.20081004102201.348:tag_ranges
    def tag_ranges(self,tagName):

        w = self
        aList = [] ### aList = gtk.Text.tag_ranges(w,tagName)
        aList = [w.toPythonIndex(z) for z in aList]
        return tuple(aList)
    #@-node:ekr.20081004102201.348:tag_ranges
    #@+node:ekr.20081004102201.349:tag_remove
    def tag_remove (self,tagName,i,j=None,*args):

        w = self
        i = w.toGuiIndex(i)

        if j is None:
            pass ### gtk.Text.tag_remove(w,tagName,i,*args)
        else:
            j = w.toGuiIndex(j)
            ### gtk.Text.tag_remove(w,tagName,i,j,*args)


    #@-node:ekr.20081004102201.349:tag_remove
    #@+node:ekr.20081004102201.350:w.deleteTextSelection
    def deleteTextSelection (self): # gtkTextWidget


        self.textBuffer.delete_selection(False, False)


        # sel = gtk.Text.tag_ranges(w,"sel")
        # if len(sel) == 2:
            # start,end = sel
            # if gtk.Text.compare(w,start,"!=",end):
                # gtk.Text.delete(w,start,end)
    #@-node:ekr.20081004102201.350:w.deleteTextSelection
    #@+node:ekr.20081004102201.351:xyToGui/PythonIndex
    def xyToGuiIndex (self,x,y): # gtkTextWidget

        w = self
        return 0 ### return gtk.Text.index(w,"@%d,%d" % (x,y))

    def xyToPythonIndex(self,x,y): # gtkTextWidget

        w = self
        i = 0 ### i = gtk.Text.index(w,"@%d,%d" % (x,y))
        i = w.toPythonIndex(i)
        return i
    #@-node:ekr.20081004102201.351:xyToGui/PythonIndex
    #@-node:ekr.20081004102201.320:Wrapper methods (gtkTextWidget)
    #@-others
#@nonl
#@-node:ekr.20081004102201.310:class leoGtkTextWidget
#@-node:ekr.20081004102201.307:== Leo Text Widget (gtk) ==
#@-node:ekr.20081004102201.104:gtkFrame
#@+node:ekr.20081004102201.352:gtkGui
class gtkGui(leoGui.leoGui):

    """A class encapulating all calls to gtk."""

    #@    @+others
    #@+node:ekr.20081004102201.353:gtkGui birth & death (done)
    #@+node:ekr.20081004102201.354: gtkGui.__init__
    def __init__ (self):

        # Initialize the base class.
        leoGui.leoGui.__init__(self,'gtk')

        self.bodyTextWidget  = leoGtkFrame.leoGtkTextWidget
        self.plainTextWidget = leoGtkFrame.leoGtkTextWidget
        self.loadIcons()

        win32clipboar = None

        self.gtkClipboard = gtk.Clipboard()
    #@-node:ekr.20081004102201.354: gtkGui.__init__
    #@+node:ekr.20081004102201.355:createKeyHandlerClass (gtkGui)
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        import leo.core.leoGtkKeys as leoGtkKeys # Do this here to break any circular dependency.

        return leoGtkKeys.gtkKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@-node:ekr.20081004102201.355:createKeyHandlerClass (gtkGui)
    #@+node:ekr.20081004102201.356:runMainLoop (gtkGui)
    def runMainLoop(self):

        '''Start the gtk main loop.'''

        if self.script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=self.script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in gtkGui.runMainLoop')
        else:
            gtk.main()
    #@-node:ekr.20081004102201.356:runMainLoop (gtkGui)
    #@+node:ekr.20081004102201.357:Do nothings
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

    #@-node:ekr.20081004102201.357:Do nothings
    #@+node:ekr.20081004102201.358:Not used
    # The tkinter gui ctor calls these methods.
    # They are included here for reference.

    if 0:
        #@    @+others
        #@+node:ekr.20081004102201.359:gtkGui.setDefaultIcon
        def setDefaultIcon(self):

            """Set the icon to be used in all Leo windows.

            This code does nothing for Tk versions before 8.4.3."""

            gui = self

            try:
                version = gui.root.getvar("tk_patchLevel")
                # g.trace(repr(version),g.CheckVersion(version,"8.4.3"))
                if g.CheckVersion(version,"8.4.3") and sys.platform == "win32":

                    # gtk 8.4.3 or greater: load a 16 by 16 icon.
                    path = g.os_path_join(g.app.loadDir,"..","Icons")
                    if g.os_path_exists(path):
                        theFile = g.os_path_join(path,"LeoApp16.ico")
                        if g.os_path_exists(path):
                            self.bitmap = gtk.BitmapImage(theFile)
                        else:
                            g.es("","LeoApp16.ico","not in Icons directory",color="red")
                    else:
                        g.es("","Icons","directory not found:",path, color="red")
            except:
                g.pr("exception setting bitmap")
                import traceback ; traceback.print_exc()
        #@-node:ekr.20081004102201.359:gtkGui.setDefaultIcon
        #@+node:ekr.20081004102201.360:gtkGui.getDefaultConfigFont
        def getDefaultConfigFont(self,config):

            """Get the default font from a new text widget."""

            if not self.defaultFontFamily:
                # WARNING: retain NO references to widgets or fonts here!
                w = g.app.gui.plainTextWidget()
                fn = w.cget("font")
                font = gtkFont.Font(font=fn) 
                family = font.cget("family")
                self.defaultFontFamily = family[:]
                # g.pr('***** getDefaultConfigFont',repr(family))

            config.defaultFont = None
            config.defaultFontFamily = self.defaultFontFamily
        #@-node:ekr.20081004102201.360:gtkGui.getDefaultConfigFont
        #@-others
    #@-node:ekr.20081004102201.358:Not used
    #@-node:ekr.20081004102201.353:gtkGui birth & death (done)
    #@+node:ekr.20081004102201.361:gtkGui dialogs & panels (to do)
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        """Create and run a gtk About Leo dialog."""
        d = leoGtkDialog.gtkAboutLeo(c,version,theCopyright,url,email)
        return d.run(modal=False)

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        d = leoGtkDialog.gtkAskLeoID()
        return d.run(modal=True)

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        """Create and run a gtk an askOK dialog ."""
        d = leoGtkDialog.gtkAskOk(c,title,message,text)
        return d.run(modal=True)

    def runAskOkCancelNumberDialog(self,c,title,message):
        """Create and run askOkCancelNumber dialog ."""
        d = leoGtkDialog.gtkAskOkCancelNumber(c,title,message)
        return d.run(modal=True)

    def runAskOkCancelStringDialog(self,c,title,message):
        """Create and run askOkCancelString dialog ."""
        d = leoGtkDialog.gtkAskOkCancelString(c,title,message)
        return d.run(modal=True)

    def runAskYesNoDialog(self,c,title,message=None):
        """Create and run an askYesNo dialog."""
        d = leoGtkDialog.gtkAskYesNo(c,title,message)
        return d.run(modal=True)

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):
        """Create and run an askYesNoCancel dialog ."""
        d = leoGtkDialog.gtkAskYesNoCancel(
            c,title,message,yesMessage,noMessage,defaultButton)
        return d.run(modal=True)

    # The compare panel has no run dialog.

    # def runCompareDialog(self,c):
        # """Create and run an askYesNo dialog."""
        # if not g.app.unitTesting:
            # leoGtkCompareDialog(c)
    #@+node:ekr.20081004102201.362:gtkGui.createSpellTab
    def createSpellTab(self,c,spellHandler,tabName):

        return leoGtkFind.gtkSpellTab(c,spellHandler,tabName)
    #@-node:ekr.20081004102201.362:gtkGui.createSpellTab
    #@+node:ekr.20081004102201.363:gtkGui file dialogs (to do)
    # We no longer specify default extensions so that we can open and save files without extensions.
    #@+node:ekr.20081004102201.364:runFileDialog
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
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK
            )
        else:
            btns = (
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK
            )

        gtkaction = g.choose(
            action == 'save',
            gtk.FILE_CHOOSER_ACTION_SAVE, 
            gtk.FILE_CHOOSER_ACTION_OPEN
        )

        dialog = gtk.FileChooserDialog(
            title,
            None,
            gtkaction,
            btns
        )

        try:

            dialog.set_default_response(gtk.RESPONSE_OK)
            dialog.set_do_overwrite_confirmation(True)
            dialog.set_select_multiple(multiple)
            if initialdir:
                dialog.set_current_folder(initialdir)

            if filetypes:

                for name, patern in filetypes:
                    filter = gtk.FileFilter()
                    filter.set_name(name)
                    filter.add_pattern(patern)
                    dialog.add_filter(filter)

            response = dialog.run()
            g.pr('dialog response' , response)

            if response == gtk.RESPONSE_OK:

                if multiple:
                    result = dialog.get_filenames()
                else:
                    result = dialog.get_filename()

            elif response == gtk.RESPONSE_CANCEL:
                result = None

        finally:

            dialog.destroy()

        g.pr('dialog result' , result)

        return result
    #@-node:ekr.20081004102201.364:runFileDialog
    #@+node:ekr.20081004102201.365:runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an gtk open file dialog ."""

        return self.runFileDialog(
            title=title,
            filetypes=filetypes,
            action='open',
            multiple=multiple,
        )
    #@nonl
    #@-node:ekr.20081004102201.365:runOpenFileDialog
    #@+node:ekr.20081004102201.366:runSaveFileDialog
    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run an gtk save file dialog ."""

        return self.runFileDialog(
            title=title,
            filetypes=filetypes,
            action='save',
            initialfile=initialfile
        )
    #@nonl
    #@-node:ekr.20081004102201.366:runSaveFileDialog
    #@-node:ekr.20081004102201.363:gtkGui file dialogs (to do)
    #@+node:ekr.20081004102201.367:gtkGui panels (done)
    def createComparePanel(self,c):
        """Create a gtk color picker panel."""
        return None # This window is optional.

        ### If desired, this panel could be created as follows:
        # return leoGtkComparePanel.leoGtkComparePanel(c)

    def createFindPanel(self,c):
        """Create a hidden gtk find panel."""
        return None # This dialog is deprecated.

    def createFindTab (self,c,parentFrame):
        """Create a gtk find tab in the indicated frame."""
        return leoGtkFind.gtkFindTab(c,parentFrame)

    def createLeoFrame(self,title):
        """Create a new Leo frame."""
        gui = self
        return leoGtkFrame.leoGtkFrame(title,gui)
    #@-node:ekr.20081004102201.367:gtkGui panels (done)
    #@-node:ekr.20081004102201.361:gtkGui dialogs & panels (to do)
    #@+node:ekr.20081004102201.368:gtkGui utils (to do)
    #@+node:ekr.20081004102201.369:Clipboard (gtkGui)
    #@+node:ekr.20081004102201.370:replaceClipboardWith
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
    #@-node:ekr.20081004102201.370:replaceClipboardWith
    #@+node:ekr.20081004102201.371:getTextFromClipboard
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
    #@-node:ekr.20081004102201.371:getTextFromClipboard
    #@-node:ekr.20081004102201.369:Clipboard (gtkGui)
    #@+node:ekr.20081004102201.372:color (to do)
    # g.es calls gui.color to do the translation,
    # so most code in Leo's core can simply use Tk color names.

    def color (self,color):
        '''Return the gui-specific color corresponding to the gtk color name.'''
        return leoColor.getco

    #@-node:ekr.20081004102201.372:color (to do)
    #@+node:ekr.20081004102201.373:Dialog (these are optional)
    #@+node:ekr.20081004102201.374:get_window_info
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
    #@-node:ekr.20081004102201.374:get_window_info
    #@+node:ekr.20081004102201.375:center_dialog
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
    #@-node:ekr.20081004102201.375:center_dialog
    #@+node:ekr.20081004102201.376:create_labeled_frame
    # Returns frames w and f.
    # Typically the caller would pack w into other frames, and pack content into f.

    def create_labeled_frame (self,parent,
        caption=None,relief="groove",bd=2,padx=0,pady=0):

        # Create w, the master frame.
        w = gtk.Frame(parent)
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
        border = gtk.Frame(w,bd=bd,relief=relief) # padx=padx,pady=pady)
        border.grid(row=1,column=1,rowspan=5,columnspan=5,sticky="news")

        # Create the content frame, f, in the center of the grid.
        f = gtk.Frame(w,bd=bd)
        f.grid(row=3,column=3,sticky="news")

        # Add the caption.
        if caption and len(caption) > 0:
            caption = gtk.Label(parent,text=caption,highlightthickness=0,bd=0)
            # caption.tkraise(w)
            caption.grid(in_=w,row=0,column=2,rowspan=2,columnspan=3,padx=4,sticky="w")

        return w,f
    #@-node:ekr.20081004102201.376:create_labeled_frame
    #@-node:ekr.20081004102201.373:Dialog (these are optional)
    #@+node:ekr.20081004102201.377:Events (gtkGui) (to do)
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
    #@-node:ekr.20081004102201.377:Events (gtkGui) (to do)
    #@+node:ekr.20081004102201.378:Focus (to do)
    #@+node:ekr.20081004102201.379:gtkGui.get_focus
    def get_focus(self,c):

        """Returns the widget that has focus, or body if None."""

        return c.frame.top.focus_displayof()
    #@-node:ekr.20081004102201.379:gtkGui.get_focus
    #@+node:ekr.20081004102201.380:gtkGui.set_focus
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
    #@-node:ekr.20081004102201.380:gtkGui.set_focus
    #@-node:ekr.20081004102201.378:Focus (to do)
    #@+node:ekr.20081004102201.381:Font (to do)
    #@+node:ekr.20081004102201.382:gtkGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        family_name = family

        try:
            font = gtkFont.Font(family=family,size=size or defaultSize,slant=slant,weight=weight)
            return font
        except:
            g.es("exception setting font from","",family_name)
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@-node:ekr.20081004102201.382:gtkGui.getFontFromParams
    #@-node:ekr.20081004102201.381:Font (to do)
    #@+node:ekr.20081004102201.383:getFullVersion (to do)
    def getFullVersion (self,c):

        gtkLevel = '<gtkLevel>' ### c.frame.top.getvar("tk_patchLevel")

        return 'gtk %s' % (gtkLevel)
    #@-node:ekr.20081004102201.383:getFullVersion (to do)
    #@+node:ekr.20081004102201.384:Icons (to do)
    #@+node:ekr.20081004102201.385:attachLeoIcon
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
    #@+node:ekr.20081004102201.386:try to use the PIL and tkIcon packages to draw the icon
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
    #@-node:ekr.20081004102201.386:try to use the PIL and tkIcon packages to draw the icon
    #@+node:ekr.20081004102201.387:createLeoIcon (a helper)
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
    #@-node:ekr.20081004102201.387:createLeoIcon (a helper)
    #@-node:ekr.20081004102201.385:attachLeoIcon
    #@-node:ekr.20081004102201.384:Icons (to do)
    #@+node:ekr.20081004102201.388:Idle Time (to do)
    #@+node:ekr.20081004102201.389:gtkGui.setIdleTimeHook
    def setIdleTimeHook (self,idleTimeHookHandler):

        # if self.root:
            # self.root.after_idle(idleTimeHookHandler)

        pass
    #@nonl
    #@-node:ekr.20081004102201.389:gtkGui.setIdleTimeHook
    #@+node:ekr.20081004102201.390:setIdleTimeHookAfterDelay
    def setIdleTimeHookAfterDelay (self,idleTimeHookHandler):

        pass

        # if self.root:
            # g.app.root.after(g.app.idleTimeDelay,idleTimeHookHandler)
    #@-node:ekr.20081004102201.390:setIdleTimeHookAfterDelay
    #@-node:ekr.20081004102201.388:Idle Time (to do)
    #@+node:ekr.20081004102201.391:isTextWidget
    def isTextWidget (self,w):

        '''Return True if w is a Text widget suitable for text-oriented commands.'''

        return w and isinstance(w,leoFrame.baseTextWidget)
    #@-node:ekr.20081004102201.391:isTextWidget
    #@+node:ekr.20081004102201.392:makeScriptButton (to do)
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
        #@+node:ekr.20081004102201.393:<< create the button b >>
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
        #@-node:ekr.20081004102201.393:<< create the button b >>
        #@nl
        #@    << define the callbacks for b >>
        #@+node:ekr.20081004102201.394:<< define the callbacks for b >>
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
        #@-node:ekr.20081004102201.394:<< define the callbacks for b >>
        #@nl
        b.configure(command=executeScriptCallback)
        c.bind(b,'<3>',deleteButtonCallback)
        if shortcut:
            #@        << bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20081004102201.395:<< bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.es_print('bound @button',buttonText,'to',shortcut,color='blue')
            #@-node:ekr.20081004102201.395:<< bind the shortcut to executeScriptCallback >>
            #@nl
        #@    << create press-buttonText-button command >>
        #@+node:ekr.20081004102201.396:<< create press-buttonText-button command >>
        aList = [g.choose(ch.isalnum(),ch,'-') for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-node:ekr.20081004102201.396:<< create press-buttonText-button command >>
        #@nl
    #@-node:ekr.20081004102201.392:makeScriptButton (to do)
    #@-node:ekr.20081004102201.368:gtkGui utils (to do)
    #@+node:ekr.20081004102201.397:class leoKeyEvent (gtkGui) (to do)
    class leoKeyEvent:

        '''A gui-independent wrapper for gui events.'''

        def __init__ (self,event,c):

            # g.trace('leoKeyEvent(gtkGui)')
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

            return 'gtkGui.leoKeyEvent: char: %s, keysym: %s' % (repr(self.char),repr(self.keysym))
    #@nonl
    #@-node:ekr.20081004102201.397:class leoKeyEvent (gtkGui) (to do)
    #@+node:ekr.20081004102201.398:loadIcon
    def loadIcon(self, fname):

        try:
            icon = gtk.gdk.pixbuf_new_from_file(fname)
        except:
            icon = None

        if icon and icon.get_width()>0:
            return icon

        g.trace( 'Can not load icon from', fname)
    #@-node:ekr.20081004102201.398:loadIcon
    #@+node:ekr.20081004102201.399:loadIcons
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

    #@-node:ekr.20081004102201.399:loadIcons
    #@-others
#@-node:ekr.20081004102201.352:gtkGui
#@+node:ekr.20081004102201.400:gtkKeys
class gtkKeyHandlerClass (leoKeys.keyHandlerClass):

    '''gtk overrides of base keyHandlerClass.'''

    #@    @+others
    #@+node:ekr.20081004102201.401:ctor
    def __init__(self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

        # g.trace('gtkKeyHandlerClass',c)

        # Init the base class.
        leoKeys.keyHandlerClass.__init__(self,c,useGlobalKillbuffer,useGlobalRegisters)
    #@-node:ekr.20081004102201.401:ctor
    #@-others
#@-node:ekr.20081004102201.400:gtkKeys
#@+node:ekr.20081004102201.402:gkMenu
#@+node:ekr.20081004102201.403:== gtk menu wrappers and mixin ==
"""This is a collection of wrappers around gtk's menu related classes.

They are here to provide the opportunity for leo specific adaptions
to these classes.

These enhancements do not violate leos Adaptor class philosophy and they
are named whith a '_' prefix to indicate they are private to leoGtkMenu.
They should only be used internally or via calls to c.frame.menu.

These adaptions may seem like overkill, but, although the gtk menu system is very powerful,
it can sometimes be difficult to do simple things and these adaptations make
life easier even now.  When the time comes to extend the system to meet Terry's
needs for cleo, all this will make life much easier still. 

At the moment all these adaptations do is the following:

    A 'c' parameter is required and added to each item and menu
        so if we ever encounter one in the wild we will be able to trace
        it back to its commander.

    MenuItems *AND* SeparatorMenuItems gain a getLabel method backed up
        by a self__label ivar which stores the 'label' parameter used in
        its construction. This makes it easier to search through a list
        of menu items that includes separators without having to worry
        about the sort of item they contain.
"""

#@+node:ekr.20081004102201.404:_gtkMenuMixin
class _gtkMenuMixin:
    """This is a class to provide common leo specific functionality to gtk's menu objects."""


    #@    @+others
    #@+node:ekr.20081004102201.405:__init__ (_gtkMenuMixin)
    def __init__(self, c, label='', underline=None):

        """initialize leo specific features comon to gtk.Menu and gtk.MenuItem wrappers.

        See host classes for documentation.

        """

        self.c = c
        self._label = label
        self._underline = underline

        self.__markLabel()
    #@-node:ekr.20081004102201.405:__init__ (_gtkMenuMixin)
    #@+node:ekr.20081004102201.406:getLabel
    def getLabel(self):
        return self._label
    #@nonl
    #@-node:ekr.20081004102201.406:getLabel
    #@+node:ekr.20081004102201.407:getUnderline
    def getUnderline(self):
        return self._underline
    #@nonl
    #@-node:ekr.20081004102201.407:getUnderline
    #@+node:ekr.20081004102201.408:setLabel
    def setLabel(self, label, underline):

        self._label = label
        self._underline = underline
        self.__markLabel()

        if isinstance(self, _gtkMenuItem):
            self.get_child().set_text(self._markedLabel)

    #@-node:ekr.20081004102201.408:setLabel
    #@+node:ekr.20081004102201.409:__markLabel
    def __markLabel(self):

        underline = self._underline
        label = self._label

        if underline >-1:
            self._markedLabel = label[:underline] + '_' + label[underline:]
            self._use_underline = True
        else:
            self._markedLabel = label
            self._use_underline = False
    #@-node:ekr.20081004102201.409:__markLabel
    #@-others
#@-node:ekr.20081004102201.404:_gtkMenuMixin
#@+node:ekr.20081004102201.410:class _gtkMenu (gtk.Menu, _gtkMenuMixin)
class _gtkMenu (gtk.Menu, _gtkMenuMixin):

    """This is a wrapper around gtk.Menu.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native Menu object.

    """

    #@    @+others
    #@+node:ekr.20081004102201.411:__init__ (_gtkMenu)
    def __init__ (self, c, tearoff=0):

        """Create and wrap a gtk.Menu. Do leo specific initailization."""

        _gtkMenuMixin.__init__(self, c)
        gtk.Menu.__gobject_init__(self)


    #@-node:ekr.20081004102201.411:__init__ (_gtkMenu)
    #@-others

gobject.type_register(_gtkMenu)
#@-node:ekr.20081004102201.410:class _gtkMenu (gtk.Menu, _gtkMenuMixin)
#@+node:ekr.20081004102201.412:class _gtkMenuItem (gtk.MenuItem, _gtkMenuMixin)
class _gtkMenuItem(gtk.MenuItem, _gtkMenuMixin):

    """This is a wrapper around gtk.MenuItem.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native gtk.MenuItem object.

    """

    #@    @+others
    #@+node:ekr.20081004102201.413:__init__ (_gtkMenuItem)
    def __init__ (self,c, label=None, underline=None):

        """Create and wrap a gtk.MenuItem. Do leo specific initailization.

        'c' is the commander that owns this item

        'label' should be a string indicating the text that should appear in
            the items label.  It should not contain any accelerator marks.

        'underline' should be an integer index into label and indicates the
            position of the character that should be marked as an accelerator.

            If underline is -1, no accelerator mark will be used.

        """

        _gtkMenuMixin.__init__(self, c, label, underline=-1)
        gtk.MenuItem.__init__(self, self._markedLabel, self._use_underline)


    #@-node:ekr.20081004102201.413:__init__ (_gtkMenuItem)
    #@-others

# Can't seem to do this, __gobject_init__ takes no paramaters
#gobject.type_register(_gtkMenuItem)
#@-node:ekr.20081004102201.412:class _gtkMenuItem (gtk.MenuItem, _gtkMenuMixin)
#@+node:ekr.20081004102201.414:class _gtkSeparatorMenuItem
class _gtkSeparatorMenuItem(gtk.SeparatorMenuItem, _gtkMenuMixin):

    """This is a wrapper around gtk.SeparatorMenuItem.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native gtk.SeparatorMenuItem object.

    Seperators can be labeled and by default are labeled '-'. This makes
    it easier to search through a list of items for a specific menu.

    Having named seperators also offers the possibility of using seperators
    to provide named sections in menus. Although this would have to be back
    ported to tkLeo for it to be useful.

    """

    #@    @+others
    #@+node:ekr.20081004102201.415:__init__ (_gtkSeparatorMenuItem)
    def __init__ (self, c, label='-', underline=-1):

        """Create and wrap a gtk.SeparatorMenuItem. Do leo specific initailization.

        'c' is the commander that owns this item

        'label' should be a string indicating the text that should appear in
            the items label.  It should not contain any accelerator marks.

        'underline' should be an integer index into label and indicates the
            position of the character that should be marked as an accelerator.


        'underline' has no significance here but is provided for compatability
            with _gtkMenuItem.

        """
        _gtkMenuMixin.__init__(self, c, label, underline)
        gtk.SeparatorMenuItem.__gobject_init__(self)


    #@-node:ekr.20081004102201.415:__init__ (_gtkSeparatorMenuItem)
    #@-others

gobject.type_register(_gtkSeparatorMenuItem)
#@-node:ekr.20081004102201.414:class _gtkSeparatorMenuItem
#@+node:ekr.20081004102201.416:class _gtkMenuBar (gtk.Menubar, _gtkMenuMixin
class _gtkMenuBar(gtk.MenuBar, _gtkMenuMixin):

    """This is a wrapper around gtk.MenuBar.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native gtk.MenuBar object.

    """

    #@    @+others
    #@+node:ekr.20081004102201.417:__init__ (_gtkMenuBar)
    def __init__ (self,c):

        """Create and wrap a gtk.MenuBar. Do leo specific initailization."""

        _gtkMenuMixin.__init__(self, c)
        gtk.MenuBar.__gobject_init__(self)
    #@-node:ekr.20081004102201.417:__init__ (_gtkMenuBar)
    #@-others

gobject.type_register(_gtkMenuBar)
#@-node:ekr.20081004102201.416:class _gtkMenuBar (gtk.Menubar, _gtkMenuMixin
#@-node:ekr.20081004102201.403:== gtk menu wrappers and mixin ==
#@+node:ekr.20081004102201.418:class leoGtkMenu(leoMenu.leoMenu)
class leoGtkMenu(leoMenu.leoMenu):

    #@    @+others
    #@+node:ekr.20081004102201.419: leoGtkMenu.__init__
    def __init__ (self,frame):

        """Create an instance of leoMenu class adapted for the gtkGui."""

        leoMenu.leoMenu.__init__(self,frame)
    #@-node:ekr.20081004102201.419: leoGtkMenu.__init__
    #@+node:ekr.20081004102201.420:plugin menu stuff... (not ready yet)
    if 0:
        #@    @+others
        #@+node:ekr.20081004102201.421:createPluginMenu
        def createPluginMenu (self):

            top = self.getMenu('top')
            oline = self.getMenu('Outline')
            ind = top.getComponentIndex(oline) + 1
            import leo.core.leoGtkPluginManager as leoGtkPluginManager
            self.plugin_menu = pmenu = leoGtkPluginManager.createPluginsMenu()
            #self.plugin_menu = pmenu = gtk.JMenu( "Plugins" )
            top.add(pmenu,ind)
            #cpm = gtk.JMenuItem( "Plugin Manager" )
            #cpm.actionPerformed = self.createPluginManager
            #pmenu.add( cpm )
            #pmenu.addSeparator()


            #self.names_and_commands[ "Plugin Manager" ] = self.createPluginManager


        #@-node:ekr.20081004102201.421:createPluginMenu
        #@+node:ekr.20081004102201.422:createPluginManager
        def createPluginManager (self,event):

            import leo.core.leoGtkPluginManager as lspm
            lspm.topLevelMenu()

        #@-node:ekr.20081004102201.422:createPluginManager
        #@+node:ekr.20081004102201.423:getPluginMenu
        def getPluginMenu (self):

            return self.plugin_menu
        #@-node:ekr.20081004102201.423:getPluginMenu
        #@-others
    #@nonl
    #@-node:ekr.20081004102201.420:plugin menu stuff... (not ready yet)
    #@+node:ekr.20081004102201.424:oops
    def oops (self):

        g.pr("leoMenu oops:", g.callers(2), "should be overridden in subclass")
    #@nonl
    #@-node:ekr.20081004102201.424:oops
    #@+node:ekr.20081004102201.425:Menu methods (Tk names)
    #@+node:ekr.20081004102201.426:Not called
    def bind (self,bind_shortcut,callback):

        g.trace(bind_shortcut,callback)

    def delete (self,menu,readItemName):

        g.trace(menu,readItemName)

    def destroy (self,menu):

        g.trace(menu)
    #@-node:ekr.20081004102201.426:Not called
    #@+node:ekr.20081004102201.427:add_cascade
    def add_cascade (self,parent,label,menu,underline):

        """This is an adapter for insert_cascade(..,position=-1,..)."""

        self.insert_cascade(parent, -1, label, menu , underline)   
    #@-node:ekr.20081004102201.427:add_cascade
    #@+node:ekr.20081004102201.428:add_command
    def add_command (self,menu,**keys):

        c = self.c

        if not menu:
            return g.trace('Should not happen.  No menu')

        item = _gtkMenuItem(c, keys.get('label'), keys.get('underline'))

        menu.append(item)

        callback = keys.get('command')

        def menuCallback (event,callback=callback):
             callback() # All args were bound when the callback was created.


        item.connect('activate', menuCallback)
        item.show()
    #@-node:ekr.20081004102201.428:add_command
    #@+node:ekr.20081004102201.429:add_separator
    def add_separator(self,menu):

        c = self.c

        if not menu:
           return g.trace('Should not happen.  No menu')

        item = _gtkSeparatorMenuItem(c)
        item.show()
        menu.append(item)

    #@-node:ekr.20081004102201.429:add_separator
    #@+node:ekr.20081004102201.430:delete_range

    def delete_range (self,menu,n1,n2):
        """Delete a range of items in a menu.

        The effect will be akin to:

            delete menu[n1:n2]

        """
        if not menu:
            return g.trace('Should not happen.  No menu')

        if n1 > n2:
            n2, n1 = n1, n2

        items = menu.get_children()

        for item in items[n1:n2]:
            menu.remove(item)

    #@-node:ekr.20081004102201.430:delete_range
    #@+node:ekr.20081004102201.431:index & invoke
    # It appears wxWidgets can't invoke a menu programmatically.
    # The workaround is to change the unit test.

    def index (self,name):
        '''Return the menu item whose name is given.'''

    def invoke (self,i):
            '''Invoke the menu whose index is i'''
    #@-node:ekr.20081004102201.431:index & invoke
    #@+node:ekr.20081004102201.432:insert
    def insert (self,menuName,position,label,command,underline=True):

        """Insert a menu item with a command into a named menu.

        'menuName' is the name of the menu into which the item is to be inserted.

        'position' is the position in the position in the menu where the item is to be inserted.
            if 'position' is -1 then the item will be appended

        'label' is the text to be used as a label for the menu item.

        'command' is a python method or function which is to be called when the menu item is activated.

        'underline' if True, the first underscore in 'label' will mark the mnemonic. (default )

        """

        c = self.c

        menu = self.getMenu(menuName)

        item = _gtkMenuItem(c, label, underline)


        if position==-1:
            menu.append(item)
        else:
            menu.insert(item, position)


        def gtkMenuCallback (event,callback=command):
            callback() # All args were bound when the callback was created.


        item.connect('activate', gtkMenuCallback)
        item.show()

    #@-node:ekr.20081004102201.432:insert
    #@+node:ekr.20081004102201.433:insert_cascade
    def insert_cascade (self,parent,index,label,menu,underline):

        """Create a menu with the given parent menu.

        'parent' is the menu into which the cascade menu should be inserted.
            if this is None then the menubar will be used as the parent.

        'label' is the text to be used as the menus label.

        'index' is the position in the parent menu where this menu should
            be inserted.

        'menu' is the cascade menu that is to be inserted.

        'underline' if True, the first underscore in 'label' will mark the mnemonic.

        """

        c = self.c

        if not menu:
            return g.trace('Should not happen.  No menu')


        item = _gtkMenuItem(c, label, underline)
        item.set_submenu(menu)

        if not parent:
            parent = self.menuBar

        if index == -1:
            parent.append(item)
        else:
            parent.insert(item, index)

        item.show()
    #@-node:ekr.20081004102201.433:insert_cascade
    #@+node:ekr.20081004102201.434:new_menu
    def new_menu(self,parent,tearoff=0):
        return _gtkMenu(self.c)
    #@-node:ekr.20081004102201.434:new_menu
    #@-node:ekr.20081004102201.425:Menu methods (Tk names)
    #@+node:ekr.20081004102201.435:Menu methods (non-Tk names)
    #@+node:ekr.20081004102201.436:createMenuBar
    def createMenuBar(self,frame):

        c = self.c

        #g.trace(frame)

        self.menuBar = menuBar = _gtkMenuBar(c)

        self.createMenusFromTables()

        #self.createAcceleratorTables()


        panel = frame.menuHolderPanel
        panel.pack_start(menuBar, False, True, 0)
        panel.show_all()


        # menuBar.SetAcceleratorTable(wx.NullAcceleratorTable)

    #@-node:ekr.20081004102201.436:createMenuBar
    #@+node:ekr.20081004102201.437:createOpenWithMenuFromTable & helper
    def createOpenWithMenuFromTable (self,table):

        '''Entries in the table passed to createOpenWithMenuFromTable are
    tuples of the form (commandName,shortcut,data).

    - command is one of "os.system", "os.startfile", "os.spawnl", "os.spawnv" or "exec".
    - shortcut is a string describing a shortcut, just as for createMenuItemsFromTable.
    - data is a tuple of the form (command,arg,ext).

    Leo executes command(arg+path) where path is the full path to the temp file.
    If ext is not None, the temp file has the given extension.
    Otherwise, Leo computes an extension based on the @language directive in effect.'''
        g.trace()

        c = self.c
        g.app.openWithTable = table # Override any previous table.

        # Delete the previous entry.

        parent = self.getMenu("File")

        label = self.getRealMenuName("Open &With...")

        amp_index = label.find("&")
        label = label.replace("&","")

        ## FIXME to be gui independant
        index = 0;
        for item in parent.get_children():
            if item.getLabel() == 'Open With...':
                parent.remove(item)
                break
            index += 1

        # Create the Open With menu.
        openWithMenu = self.createOpenWithMenu(parent,label,index,amp_index)

        self.setMenu("Open With...",openWithMenu)
        # Create the menu items in of the Open With menu.
        for entry in table:
            if len(entry) != 3: # 6/22/03
                g.es("","createOpenWithMenuFromTable:","invalid data",color="red")
                return
        self.createOpenWithMenuItemsFromTable(openWithMenu,table)
    #@+node:ekr.20081004102201.438:createOpenWithMenuItemsFromTable
    def createOpenWithMenuItemsFromTable (self,menu,table):

        '''Create an entry in the Open with Menu from the table.

        Each entry should be a sequence with 2 or 3 elements.'''

        c = self.c ; k = c.k

        if g.app.unitTesting: return

        for data in table:
            #@        << get label, accelerator & command or continue >>
            #@+node:ekr.20081004102201.439:<< get label, accelerator & command or continue >>
            ok = (
                type(data) in (type(()), type([])) and
                len(data) in (2,3)
            )

            if ok:
                if len(data) == 2:
                    label,openWithData = data ; accelerator = None
                else:
                    label,accelerator,openWithData = data
                    accelerator = k.shortcutFromSetting(accelerator)
                    accelerator = accelerator and g.stripBrackets(k.prettyPrintKey(accelerator))
            else:
                g.trace('bad data in Open With table: %s' % repr(data))
                continue # Ignore bad data
            #@-node:ekr.20081004102201.439:<< get label, accelerator & command or continue >>
            #@nl
            # g.trace(label,accelerator)
            realLabel = self.getRealMenuName(label)
            underline=realLabel.find("&")
            realLabel = realLabel.replace("&","")
            callback = self.defineOpenWithMenuCallback(openWithData)

            c.add_command(menu,label=realLabel,
                accelerator=accelerator or '',
                command=callback,underline=underline)
    #@-node:ekr.20081004102201.438:createOpenWithMenuItemsFromTable
    #@-node:ekr.20081004102201.437:createOpenWithMenuFromTable & helper
    #@+node:ekr.20081004102201.440:defineMenuCallback
    def defineMenuCallback(self,command,name):
        """Define a menu callback to bind a command to a menu.

        'command' is the leo minibuffer command to be executed when
                   the menu item is activated

        'name' is the text that should appear in the as the menu's label.


        The first parameter of the callback must be 'event', and it must default to None.

        """
        def callback(event=None,self=self,command=command,label=name):
            self.c.doCommand(command,label,event)

        return callback
    #@-node:ekr.20081004102201.440:defineMenuCallback
    #@+node:ekr.20081004102201.441:defineOpenWithMenuCallback
    def defineOpenWithMenuCallback (self,command):

        # The first parameter must be event, and it must default to None.
        def wxOpenWithMenuCallback(event=None,command=command):
            try: self.c.openWith(data=command)
            except: g.pr(traceback.print_exc())

        return wxOpenWithMenuCallback
    #@-node:ekr.20081004102201.441:defineOpenWithMenuCallback
    #@+node:ekr.20081004102201.442:createOpenWithMenu
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create a submenu.'''
        menu = self.new_menu(parent)
        self.insert_cascade(parent, index, label=label,menu=menu,underline=amp_index)
        return menu
    #@-node:ekr.20081004102201.442:createOpenWithMenu
    #@+node:ekr.20081004102201.443:disableMenu
    def disableMenu (self,menu,name):

        g.trace('not implemented')
        return ###

        if not menu:
            g.trace("no menu",name)
            return

        realName = self.getRealMenuName(name)
        realName = realName.replace("&","")
        id = menu.FindItem(realName)
        if id:
            item = menu.FindItemById(id)
            item.Enable(0)
        else:
            g.trace("no item",name,val)
    #@-node:ekr.20081004102201.443:disableMenu
    #@+node:ekr.20081004102201.444:enableMenu
    def enableMenu (self,menu,name,val):

        g.trace('not implemented')
        return ###

        if not menu:
            g.trace("no menu",name,val)
            return

        realName = self.getRealMenuName(name)
        realName = realName.replace("&","")
        id = menu.FindItem(realName)
        if id:
            item = menu.FindItemById(id)
            val = g.choose(val,1,0)
            item.Enable(val)
        else:
            g.trace("no item",name,val)
    #@nonl
    #@-node:ekr.20081004102201.444:enableMenu
    #@+node:ekr.20081004102201.445:setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        if not menu:
            g.trace("no menu",name)
            return

        items = menu.get_children()

        if type(name) == type(0):
            # "name" is actually an index into the menu.
            if items and len(items) > name :
                item = items[name].GetId()
            else:
                item = None
        else:
            realName = self.getRealMenuName(name)
            realName = realName.replace("&","")
            for item in items:
                if item.getLabel() == realName:
                    break
            else:
                item = None      

        if item:
            label = self.getRealMenuName(label)
            label = label.replace("&","")
            # g.trace(name,label)
            item.setLabel(label, underline)
        else:
            g.trace("no item",name,label)
    #@-node:ekr.20081004102201.445:setMenuLabel
    #@-node:ekr.20081004102201.435:Menu methods (non-Tk names)
    #@-others
#@nonl
#@-node:ekr.20081004102201.418:class leoGtkMenu(leoMenu.leoMenu)
#@-node:ekr.20081004102201.402:gkMenu
#@+node:ekr.20081004102201.446:gtkTree
#@+node:ekr.20081004102201.448:class leoGtkTree (leoFrame.leoTree)
class leoGtkTree (leoFrame.leoTree):
    """Leo gtk tree class."""

    #@    @+others
    #@+node:ekr.20081004102201.449: Birth... (gtkTree)
    #@+node:ekr.20081004102201.450:__init__ (gtkTree)
    def __init__(self,c):

        #g.trace('>>', 'gtkTree', c)
        g.trace(g.callers())

        # Init the base class.
        leoFrame.leoTree.__init__(self,c.frame)

        #@    << set ivars >>
        #@+node:ekr.20081004102201.451:<< set ivars >>



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
        self.use_chapters   = False and c.config.getBool('use_chapters') ###



        #@<< define drawing constants >>
        #@+node:ekr.20081004102201.452:<< define drawing constants >>
        self.box_padding = 5 # extra padding between box and icon
        self.box_width = 9 + self.box_padding
        self.icon_width = 20
        self.text_indent = 4 # extra padding between icon and tex

        self.hline_y = 7 # Vertical offset of horizontal line ??
        self.root_left = 7 + self.box_width
        self.root_top = 2

        self.default_line_height = 17 + 2 # default if can't set line_height from font.
        self.line_height = self.default_line_height
        #@-node:ekr.20081004102201.452:<< define drawing constants >>
        #@nl
        #@<< old ivars >>
        #@+node:ekr.20081004102201.453:<< old ivars >>
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
        #@-node:ekr.20081004102201.453:<< old ivars >>
        #@nl
        #@<< inject callbacks into the position class >>
        #@+node:ekr.20081004102201.454:<< inject callbacks into the position class >>
        # The new code injects 3 callbacks for the colorizer.

        if 0 and not leoGtkTree.callbacksInjected: # Class var. ###
            leoGtkTree.callbacksInjected = True
            self.injectCallbacks()
        #@-node:ekr.20081004102201.454:<< inject callbacks into the position class >>
        #@nl

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
            # Pre 4.4b2: Keys are vnodes, values are gtk.Text widgets.
            #     4.4b2: Keys are p.key(), values are gtk.Text widgets.
        self.visibleUserIcons = []

        # Lists of free, hidden widgets...
        self.freeBoxes = []
        self.freeClickBoxes = []
        self.freeIcons = []
        self.freeLines = []
        self.freeText = [] # New in 4.4b2: a list of free gtk.Text widgets

        self.freeUserIcons = []


        #@-node:ekr.20081004102201.451:<< set ivars >>
        #@nl

        self.canvas = OutlineCanvasPanel(self, 'canvas')
    #@+node:ekr.20081004102201.455:NewHeadline
    #@-node:ekr.20081004102201.455:NewHeadline
    #@-node:ekr.20081004102201.450:__init__ (gtkTree)
    #@+node:ekr.20081004102201.456:gtkTtree.setBindings
    def setBindings (self):

        '''Create binding table for all canvas events.

        ??? I am not sure how best to emulate tk event system.
            I would be a happier using hitTest to determine where and
            what was it then hard coding the action sequence, that way
            we would know exactly what was happening and when.
        '''

        tree = self ; k = self.c.k ; canvas = self.canvas

        g.trace('leoGtkTree', tree, self.c, canvas)


        if 1:

            # g.trace('self',self,'canvas',canvas)

            #@        << create gtk mouse action table >>
            #@+node:ekr.20081004102201.457:<< create gtk mouse action table  >>
            self.gtkMouseActionTable = {
                'clickBox': {
                    '<Button-1>': self.onClickBoxClick,
                },

                'iconBox': {
                    '<Button-1>': self.onIconBoxClick,
                    '<Double-1>': self.onIconBoxDoubleClick,
                    '<Button-3>': self.onIconBoxRightClick,
                    '<Double-3>': self.onIconBoxRightClick,
                    '<Any-ButtonRelease-1>': self.onEndDrag,
                },

                # these to be set later.
                'headline': {
                    '<Button-1>': None,
                    '<Double-1>': None,
                    '<Button-3>': None,
                    '<Double-3>': None,
                } 
            }
            #@-node:ekr.20081004102201.457:<< create gtk mouse action table  >>
            #@nl
            #@        << add actions for headline mouse events >>
            #@+node:ekr.20081004102201.458:<< add actions for headline mouse events >>
            #self.bindingWidget = w = g.app.gui.plainTextWidget(
            #    self.canvas,name='bindingWidget')

            # c.bind(w,'<Key>',k.masterKeyHandler)

            table = (
                ('<Button-1>',  k.masterClickHandler,          tree.onHeadlineClick),
                ('<Button-3>',  k.masterClick3Handler,         tree.onHeadlineRightClick),
                ('<Double-1>',  k.masterDoubleClickHandler,    tree.onHeadlineClick),
                ('<Double-3>',  k.masterDoubleClick3Handler,   tree.onHeadlineRightClick),
            )

            actions = self.gtkMouseActionTable

            for a,handler,func in table:

                def treeBindingCallback(event,handler=handler,func=func):
                    g.trace('func',func, event.widget)
                    return handler(event,func)

                actions['headline'][a] = treeBindingCallback

            ### self.textBindings = w.bindtags()
            #@-node:ekr.20081004102201.458:<< add actions for headline mouse events >>
            #@nl

            #k.completeAllBindingsForWidget(canvas)

            #k.completeAllBindingsForWidget(self.bindingWidget)

    #@-node:ekr.20081004102201.456:gtkTtree.setBindings
    #@+node:ekr.20081004102201.459:gtkTree.setCanvasBindings
    def setCanvasBindings (self, canvas):

        NOTUSED()

        """Set binding for this canvas.

        In gtk this includes:

            setting self.mouseAtionTable to a dictionary of dictionaries.

            The top level dictionary keys are target names such as 'clickBox'
                the values are dictionareis whose keys represent event types
                and whose values are functions to call to handle that target
                event combination.

            e.g
                self.gtkMouseActionTable['clickBox']['<Button-1>']

        """

        k = self.c.k


        self.gtkMouseActionTable = {
            'plusBox': {
                '<Button-1>': self.onClickBoxClick,
            },

            'iconBox': {
                '<Button-1>': self.onIconBoxClick,
                '<Double-1>': self.onIconBoxDoubleClick,
                '<Button-3>': self.onIconBoxRightClick,
                '<Double-3>': self.onIconBoxRightClick,
                '<Any-ButtonRelease-1>': self.self.onEndDrag,
            }, 
        }


        if 0: ###

            c.bind(canvas,'<Key>',k.masterKeyHandler)
            c.bind(canvas,'<Button-1>',self.onTreeClick)

            #@        << make bindings for tagged items on the canvas >>
            #@+node:ekr.20081004102201.460:<< make bindings for tagged items on the canvas >>
            where = g.choose(self.expanded_click_area,'clickBox','plusBox')

            ###
            # table = (
                # (where,    '<Button-1>',self.onClickBoxClick),
                # ('iconBox','<Button-1>',self.onIconBoxClick),
                # ('iconBox','<Double-1>',self.onIconBoxDoubleClick),
                # ('iconBox','<Button-3>',self.onIconBoxRightClick),
                # ('iconBox','<Double-3>',self.onIconBoxRightClick),
                # ('iconBox','<B1-Motion>',self.onDrag),
                # ('iconBox','<Any-ButtonRelease-1>',self.onEndDrag),
            # )
            # for tag,event,callback in table:
                # c.tag_bind(canvas,tag,event,callback)
            #@-node:ekr.20081004102201.460:<< make bindings for tagged items on the canvas >>
            #@nl
            #@        << create baloon bindings for tagged items on the canvas >>
            #@+node:ekr.20081004102201.461:<< create baloon bindings for tagged items on the canvas >>
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
            #@-node:ekr.20081004102201.461:<< create baloon bindings for tagged items on the canvas >>
            #@nl
    #@-node:ekr.20081004102201.459:gtkTree.setCanvasBindings
    #@-node:ekr.20081004102201.449: Birth... (gtkTree)
    #@+node:ekr.20081004102201.462:onOutlineCanvasEvent
    def onOutlineCanvasEvent(self, target, eventType, event, p):
        """Handle events recieved from the outline canvas widget.

        ??? We need a clear declaration of the event sequence for
            mouse events on the canvas

        At the moment there are three levels,

            headline item
            headline
            canvas

            events on a headline item will:
                invoke specific events handlers bound to that item
                invoke more general event handlers bound to the headline
                invoke events bound to the canvas

            events on a headline will:
                invoke more general event handlers bound to the headline
                invoke events bound to the canvas

            events on a canvas will:
                invoke events bound on the canvas

            if an event handler returns true at any stage, all event handling will halt.

        """

        try:
            method = self.gtkMouseActionTable[target][eventType]
        except KeyError:
            method = None
            g.pr('no binding', target, eventType)

        result = False
        if method:
            result = method(event)

        if not result and target not in ('canvas', 'headline'):
            target = 'headline'
            result =  self.onOutlineCanvasEvent(target, eventType, event, p)           

        self.canvas.update()
        return result


    #@-node:ekr.20081004102201.462:onOutlineCanvasEvent
    #@+node:ekr.20081004102201.463:Allocation...(gtkTree)
    if 0:
        #TOEKR  can these be deleted?
        #@    @+others
        #@+node:ekr.20081004102201.464:newBox
        def newBox (self,p,x,y,image):

            canvas = self.canvas ; tag = "plusBox"

            if self.freeBoxes:
                theId = self.freeBoxes.pop(0)
                canvas.coords(theId,x,y)
                canvas.itemconfigure(theId,image=image)
            else:
                theId = canvas.create_image(x,y,image=image,tag=tag)
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if theId not in self.visibleBoxes: 
                self.visibleBoxes.append(theId)

            if p:
                self.ids[theId] = p

            return theId
        #@-node:ekr.20081004102201.464:newBox
        #@+node:ekr.20081004102201.465:newClickBox
        def newClickBox (self,p,x1,y1,x2,y2):

            canvas = self.canvas ; defaultColor = ""
            tag = g.choose(p.hasChildren(),'clickBox','selectBox')

            if self.freeClickBoxes:
                theId = self.freeClickBoxes.pop(0)
                canvas.coords(theId,x1,y1,x2,y2)
                canvas.itemconfig(theId,tag=tag)
            else:
                theId = self.canvas.create_rectangle(x1,y1,x2,y2,tag=tag)
                canvas.itemconfig(theId,fill=defaultColor,outline=defaultColor)
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if theId not in self.visibleClickBoxes:
                self.visibleClickBoxes.append(theId)
            if p:
                self.ids[theId] = p

            return theId
        #@-node:ekr.20081004102201.465:newClickBox
        #@+node:ekr.20081004102201.466:newIcon
        def newIcon (self,p,x,y,image):

            canvas = self.canvas ; tag = "iconBox"

            if self.freeIcons:
                theId = self.freeIcons.pop(0)
                canvas.itemconfigure(theId,image=image)
                canvas.coords(theId,x,y)
            else:
                theId = canvas.create_image(x,y,image=image,anchor="nw",tag=tag)
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if theId not in self.visibleIcons:
                self.visibleIcons.append(theId)

            if p:
                data = p,self.generation
                self.iconIds[theId] = data # Remember which vnode belongs to the icon.
                self.ids[theId] = p

            return theId
        #@-node:ekr.20081004102201.466:newIcon
        #@+node:ekr.20081004102201.467:newLine
        def newLine (self,p,x1,y1,x2,y2):

            canvas = self.canvas

            if self.freeLines:
                theId = self.freeLines.pop(0)
                canvas.coords(theId,x1,y1,x2,y2)
            else:
                theId = canvas.create_line(x1,y1,x2,y2,tag="lines",fill="gray50") # stipple="gray25")
                if self.trace_alloc: g.trace("%3d %s" % (theId,p and p.headString()),align=-20)

            if p:
                self.ids[theId] = p

            if theId not in self.visibleLines:
                self.visibleLines.append(theId)

            return theId
        #@-node:ekr.20081004102201.467:newLine
        #@+node:ekr.20081004102201.468:newText (gtkTree) and helper
        def newText (self,p,x,y):

            canvas = self.canvas ; tag = "textBox"
            c = self.c ;  k = c.k
            if self.freeText:
                w,theId = self.freeText.pop()
                canvas.coords(theId,x,y) # Make the window visible again.
                    # theId is the id of the *window* not the text.
            else:
                # Tags are not valid in gtk.Text widgets.
                self.textNumber += 1
                w = g.app.gui.plainTextWidget(
                    canvas,name='head-%d' % self.textNumber,
                    state="normal",font=self.font,bd=0,relief="flat",height=1)
                ### w.bindtags(self.textBindings) # Set the bindings for this widget.

                if 0: # Crashes on XP.
                    #@            << patch by Maciej Kalisiak to handle scroll-wheel events >>
                    #@+node:ekr.20081004102201.469:<< patch by Maciej Kalisiak  to handle scroll-wheel events >>
                    def PropagateButton4(e):
                        canvas.event_generate("<Button-4>")
                        return "break"

                    def PropagateButton5(e):
                        canvas.event_generate("<Button-5>")
                        return "break"

                    def PropagateMouseWheel(e):
                        canvas.event_generate("<MouseWheel>")
                        return "break"
                    #@-node:ekr.20081004102201.469:<< patch by Maciej Kalisiak  to handle scroll-wheel events >>
                    #@nl

                theId = canvas.create_window(x,y,anchor="nw",window=w,tag=tag)
                w.leo_window_id = theId # Never changes.

                if self.trace_alloc: g.trace('%3d %6s' % (theId,id(w)),align=-20)

            # Common configuration.
            if 0: # Doesn't seem to work.
                balloon = Pmw.Balloon(canvas,initwait=700)
                balloon.tagbind(canvas,theId,balloonHelp='Headline')

            if p:
                self.ids[theId] = p # Add the id of the *window*
                self.setHeadlineText(theId,w,p.headString())
                w.configure(width=self.headWidth(p=p))
                w.leo_position = p # This p never changes.
                    # *Required*: onHeadlineClick uses w.leo_position to get p.

                # Keys are p.key().  Entries are (w,theId)
                self.visibleText [p.key()] = w,theId
            else:
                g.trace('**** can not happen.  No p')

            return w
        #@+node:ekr.20081004102201.470:tree.setHeadlineText
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
        #@-node:ekr.20081004102201.470:tree.setHeadlineText
        #@-node:ekr.20081004102201.468:newText (gtkTree) and helper
        #@+node:ekr.20081004102201.471:recycleWidgets
        def recycleWidgets (self):

            canvas = self.canvas

            for theId in self.visibleBoxes:
                if theId not in self.freeBoxes:
                    self.freeBoxes.append(theId)
                canvas.coords(theId,-100,-100)
            self.visibleBoxes = []

            for theId in self.visibleClickBoxes:
                if theId not in self.freeClickBoxes:
                    self.freeClickBoxes.append(theId)
                canvas.coords(theId,-100,-100,-100,-100)
            self.visibleClickBoxes = []

            for theId in self.visibleIcons:
                if theId not in self.freeIcons:
                    self.freeIcons.append(theId)
                canvas.coords(theId,-100,-100)
            self.visibleIcons = []

            for theId in self.visibleLines:
                if theId not in self.freeLines:
                    self.freeLines.append(theId)
                canvas.coords(theId,-100,-100,-100,-100)
            self.visibleLines = []

            aList = self.visibleText.values()
            for data in aList:
                w,theId = data
                # assert theId == w.leo_window_id
                canvas.coords(theId,-100,-100)
                w.leo_position = None # Allow the position to be freed.
                if data not in self.freeText:
                    self.freeText.append(data)
            self.visibleText = {}

            for theId in self.visibleUserIcons:
                # The present code does not recycle user Icons.
                self.canvas.delete(theId)
            self.visibleUserIcons = []
        #@-node:ekr.20081004102201.471:recycleWidgets
        #@+node:ekr.20081004102201.472:destroyWidgets
        def destroyWidgets (self):

            self.ids = {}

            self.visibleBoxes = []
            self.visibleClickBoxes = []
            self.visibleIcons = []
            self.visibleLines = []
            self.visibleUserIcons = []

            self.visibleText = {}

            self.freeText = []
            self.freeBoxes = []
            self.freeClickBoxes = []
            self.freeIcons = []
            self.freeLines = []

            self.canvas.delete("all")
        #@-node:ekr.20081004102201.472:destroyWidgets
        #@+node:ekr.20081004102201.473:showStats
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
        #@-node:ekr.20081004102201.473:showStats
        #@-others
    #@nonl
    #@-node:ekr.20081004102201.463:Allocation...(gtkTree)
    #@+node:ekr.20081004102201.474:Config & Measuring...
    #@+node:ekr.20081004102201.475:tree.getFont,setFont,setFontFromConfig
    def getFont (self):

        return self.font

    def setFont (self,font=None, fontName=None):

        # ESSENTIAL: retain a link to font.
        if fontName:
            self.fontName = fontName
            self.font = gtkFont.Font(font=fontName)
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
    #@-node:ekr.20081004102201.475:tree.getFont,setFont,setFontFromConfig
    #@+node:ekr.20081004102201.476:headWidth & widthInPixels
    def headWidth(self,p=None,s=''):

        """Returns the proper width of the entry widget for the headline."""

        if p: s = p.headString()

        return self.font.measure(s)/self.font.measure('0')+1


    def widthInPixels(self,s):

        s = g.toEncodedString(s,g.app.tkEncoding)

        return self.font.measure(s)
    #@-node:ekr.20081004102201.476:headWidth & widthInPixels
    #@+node:ekr.20081004102201.477:setLineHeight
    def setLineHeight (self,font):

        pass ###

        # try:
            # metrics = font.metrics()
            # linespace = metrics ["linespace"]
            # self.line_height = linespace + 5 # Same as before for the default font on Windows.
            # # g.pr(metrics)
        # except:
            # self.line_height = self.default_line_height
            # g.es("exception setting outline line height")
            # g.es_exception()
    #@-node:ekr.20081004102201.477:setLineHeight
    #@-node:ekr.20081004102201.474:Config & Measuring...
    #@+node:ekr.20081004102201.478:Debugging...
    if 0:
        #@    @+others
        #@+node:ekr.20081004102201.479:textAddr
        def textAddr(self,w):

            """Return the address part of repr(gtk.Text)."""

            return repr(w)[-9:-1].lower()
        #@-node:ekr.20081004102201.479:textAddr
        #@+node:ekr.20081004102201.480:traceIds (Not used)
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
                        g.pr("%3d" % key,p.headString())
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
                                    g.pr("%3d" % key,val.headString())
        #@-node:ekr.20081004102201.480:traceIds (Not used)
        #@-others
        #TOEKR delete these?
    #@nonl
    #@-node:ekr.20081004102201.478:Debugging...
    #@+node:ekr.20081004102201.481:Drawing... (gtkTree)
    #@+node:ekr.20081004102201.482:tree.begin/endUpdate
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
    #@-node:ekr.20081004102201.482:tree.begin/endUpdate
    #@+node:ekr.20081004102201.483:tree.redraw_now & helper
    # New in 4.4b2: suppress scrolling by default.

    def redraw_now (self,scroll=False,forceDraw=False):

        '''Redraw immediately: used by Find so a redraw doesn't mess up selections in headlines.'''

        if g.app.quitting or self.frame not in g.app.windowList:
            return
        if self.drag_p and not forceDraw:
            return

        c = self.c

        # g.trace(g.callers())

        if not g.app.unitTesting:
            if self.gc_before_redraw:
                g.collectGarbage()
            if g.app.trace_gc_verbose:
                if (self.redrawCount % 5) == 0:
                    g.printGcSummary()
            if self.trace_redraw or self.trace_alloc:
                # g.trace(self.redrawCount,g.callers())
                # g.trace(c.rootPosition().headString(),'canvas:',id(self.canvas),g.callers())
                if self.trace_stats:
                    g.print_stats()
                    g.clear_stats()

        # New in 4.4b2: Call endEditLabel, but suppress the redraw.
        self.beginUpdate()
        try:
            self.endEditLabel()
        finally:
            self.endUpdate(False)

        # Do the actual redraw.
        self.expandAllAncestors(c.currentPosition())
        if self.idle_redraw:
            def idleRedrawCallback(event=None,self=self,scroll=scroll):
                self.redrawHelper(scroll=scroll)
            ### self.canvas.after_idle(idleRedrawCallback)
        else:
            self.redrawHelper(scroll=scroll)
        if g.app.unitTesting:
            self.canvas.update_idletasks() # Important for unit tests.
        c.masterFocusHandler()

    redraw = redraw_now # Compatibility
    #@+node:ekr.20081004102201.484:redrawHelper
    def redrawHelper (self,scroll=True,forceDraw=False):

        c = self.c

        if self.canvas:
            self.canvas.update()
        else:
            g.trace('No Canvas')

        ###

        # oldcursor = self.canvas['cursor']
        # self.canvas['cursor'] = "watch"

        # if not g.doHook("redraw-entire-outline",c=c):
            # c.setTopVnode(None)
            # self.setVisibleAreaToFullCanvas()
            # self.drawTopTree()
            # # Set up the scroll region after the tree has been redrawn.
            # bbox = self.canvas.bbox('all')
            # # g.trace('canvas',self.canvas,'bbox',bbox)
            # if bbox is None:
                # x0,y0,x1,y1 = 0,0,100,100
            # else:
                # x0, y0, x1, y1 = bbox
            # self.canvas.configure(scrollregion=(0, 0, x1, y1))
            # if scroll:
                # self.canvas.update_idletasks() # Essential.
                # self.scrollTo()

        g.doHook("after-redraw-outline",c=c)

        ### self.canvas['cursor'] = oldcursor
    #@-node:ekr.20081004102201.484:redrawHelper
    #@-node:ekr.20081004102201.483:tree.redraw_now & helper
    #@+node:ekr.20081004102201.485:idle_second_redraw
    def idle_second_redraw (self):

        c = self.c

        # Erase and redraw the entire tree the SECOND time.
        # This ensures that all visible nodes are allocated.
        c.setTopVnode(None)
        args = self.canvas.yview()
        self.setVisibleArea(args)

        if 0:
            self.deleteBindings()
            self.canvas.delete("all")

        self.drawTopTree()

        if self.trace:
            g.trace(self.redrawCount)
    #@-node:ekr.20081004102201.485:idle_second_redraw
    #@+node:ekr.20081004102201.486:drawX...
    ##
    #@nonl
    #@+node:ekr.20081004102201.487:drawBox
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
    #@-node:ekr.20081004102201.487:drawBox
    #@+node:ekr.20081004102201.488:drawClickBox
    def drawClickBox (self,p,y):

        h = self.line_height

        # Define a slighly larger rect to catch clicks.
        if self.expanded_click_area:
            self.newClickBox(p,0,y,1000,y+h-2)
    #@-node:ekr.20081004102201.488:drawClickBox
    #@+node:ekr.20081004102201.489:drawIcon
    def drawIcon(self,p,x=None,y=None):

        """Draws icon for position p at x,y, or at p.v.iconx,p.v.icony if x,y = None,None"""

        # if self.trace_gc: g.printNewObjects(tag='icon 1')

        c = self.c ; v = p.v
        #@    << compute x,y and iconVal >>
        #@+node:ekr.20081004102201.490:<< compute x,y and iconVal >>
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
        #@nonl
        #@-node:ekr.20081004102201.490:<< compute x,y and iconVal >>
        #@nl
        v.iconVal = val

        if not g.doHook("draw-outline-icon",tree=self,c=c,p=p,v=p,x=x,y=y):

            # Get the image.
            imagename = "box%02d.GIF" % val
            image = self.getIconImage(imagename)
            self.newIcon(p,x,y+self.lineyoffset,image)

        return 0,self.icon_width # dummy icon height,width
    #@-node:ekr.20081004102201.489:drawIcon
    #@+node:ekr.20081004102201.491:drawLine
    def drawLine (self,p,x1,y1,x2,y2):

        theId = self.newLine(p,x1,y1,x2,y2)

        return theId
    #@-node:ekr.20081004102201.491:drawLine
    #@+node:ekr.20081004102201.492:drawNode & force_draw_node (good trace)
    def drawNode(self,p,x,y):

        c = self.c

        # g.trace(x,y,p,id(self.canvas))

        data = g.doHook("draw-outline-node",tree=self,c=c,p=p,v=p,x=x,y=y)
        if data is not None: return data

        if 1:
            self.lineyoffset = 0
        else:
            if hasattr(p.v.t,"unknownAttributes"):
                self.lineyoffset = p.v.t.unknownAttributes.get("lineYOffset",0)
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
    #@+node:ekr.20081004102201.493:force_draw_node
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
        x += self.widthInPixels(p.headString())

        h2,w2 = self.drawUserIcons(p,"afterHeadline",x,y)
        h = max(h,h2)

        self.drawClickBox(p,y)

        return h,indent
    #@-node:ekr.20081004102201.493:force_draw_node
    #@-node:ekr.20081004102201.492:drawNode & force_draw_node (good trace)
    #@+node:ekr.20081004102201.494:drawText
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
    #@-node:ekr.20081004102201.494:drawText
    #@+node:ekr.20081004102201.495:drawUserIcons
    def drawUserIcons(self,p,where,x,y):

        """Draw any icons specified by p.v.t.unknownAttributes["icons"]."""

        h,w = 0,0 ; t = p.v.t

        if not hasattr(t,"unknownAttributes"):
            return h,w

        iconsList = t.unknownAttributes.get("icons")
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
    #@-node:ekr.20081004102201.495:drawUserIcons
    #@+node:ekr.20081004102201.496:drawUserIcon
    def drawUserIcon (self,p,where,x,y,w2,theDict):

        h,w = 0,0

        if where != theDict.get("where","beforeHeadline"):
            return h,w

        # if self.trace_gc: g.printNewObjects(tag='userIcon 1')

        # g.trace(where,x,y,theDict)

        #@    << set offsets and pads >>
        #@+node:ekr.20081004102201.497:<< set offsets and pads >>
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
        #@-node:ekr.20081004102201.497:<< set offsets and pads >>
        #@nl
        theType = theDict.get("type")
        if theType == "icon":
            if 0: # not ready yet.
                s = theDict.get("icon")
                #@            << draw the icon in string s >>
                #@+node:ekr.20081004102201.498:<< draw the icon in string s >>
                pass
                #@-node:ekr.20081004102201.498:<< draw the icon in string s >>
                #@nl
        elif theType == "file":
            theFile = theDict.get("file")
            #@        << draw the icon at file >>
            #@+node:ekr.20081004102201.499:<< draw the icon at file >>
            try:
                image = self.iconimages[theFile]
                # Get the image from the cache if possible.
            except KeyError:
                try:
                    fullname = g.os_path_join(g.app.loadDir,"..","Icons",theFile)
                    fullname = g.os_path_normpath(fullname)
                    image = gtk.PhotoImage(master=self.canvas,file=fullname)
                    self.iconimages[fullname] = image
                except:
                    #g.es("exception loading:",fullname)
                    #g.es_exception()
                    image = None

            if image:
                theId = self.canvas.create_image(
                    x+xoffset+w2,y+yoffset,
                    anchor="nw",image=image,tag="userIcon")
                self.ids[theId] = p
                # assert(theId not in self.visibleIcons)
                self.visibleUserIcons.append(theId)

                h = image.height() + yoffset + ypad
                w = image.width()  + xoffset + xpad
            #@-node:ekr.20081004102201.499:<< draw the icon at file >>
            #@nl
        elif theType == "url":
            ## url = theDict.get("url")
            #@        << draw the icon at url >>
            #@+node:ekr.20081004102201.500:<< draw the icon at url >>
            pass
            #@-node:ekr.20081004102201.500:<< draw the icon at url >>
            #@nl

        # Allow user to specify height, width explicitly.
        h = theDict.get("height",h)
        w = theDict.get("width",w)

        # if self.trace_gc: g.printNewObjects(tag='userIcon 2')

        return h,w
    #@-node:ekr.20081004102201.496:drawUserIcon
    #@+node:ekr.20081004102201.501:drawTopTree
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
            g.trace('redrawCount',self.redrawCount,g.callers()) # 'len(c.hoistStack)',len(c.hoistStack))
            if 0:
                delta = g.app.positions - self.prevPositions
                g.trace("**** gen: %-3d positions: %5d +%4d" % (
                    self.generation,g.app.positions,delta),g.callers())

        self.prevPositions = g.app.positions
        if self.trace_gc: g.printNewObjects(tag='top 1')

        hoistFlag = c.hoistStack
        if c.hoistStack:
            bunch = c.hoistStack[-1] ; p = bunch.p
            h = p.headString()
            if len(c.hoistStack) == 1 and h.startswith('@chapter') and p.hasChildren():
                p = p.firstChild()
                hoistFlag = False
        else:
            p = c.rootPosition()

        self.drawTree(p,self.root_left,self.root_top,0,0,hoistFlag=hoistFlag)

        if self.trace_gc: g.printNewObjects(tag='top 2')
        if self.trace_stats: self.showStats()

        canvas.lower("lines")  # Lowest.
        canvas.lift("textBox") # Not the gtk.Text widget: it should be low.
        canvas.lift("userIcon")
        canvas.lift("plusBox")
        canvas.lift("clickBox")
        canvas.lift("clickExpandBox")
        canvas.lift("iconBox") # Higest.

        self.redrawing = False
    #@-node:ekr.20081004102201.501:drawTopTree
    #@+node:ekr.20081004102201.502:drawTree
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
    #@-node:ekr.20081004102201.502:drawTree
    #@-node:ekr.20081004102201.486:drawX...
    #@+node:ekr.20081004102201.503:Helpers...
    #@+node:ekr.20081004102201.504:getIconImage
    def getIconImage (self, name):

        # Return the image from the cache if possible.
        if name in self.iconimages:
            return self.iconimages[name]

        # g.trace(name)

        try:
            fullname = g.os_path_join(g.app.loadDir,"..","Icons",name)
            fullname = g.os_path_normpath(fullname)
            image = gtk.PhotoImage(master=self.canvas,file=fullname)
            self.iconimages[name] = image
            return image
        except:
            g.es("exception loading:",fullname)
            g.es_exception()
            return None
    #@-node:ekr.20081004102201.504:getIconImage
    #@+node:ekr.20081004102201.505:inVisibleArea & inExpandedVisibleArea
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
    #@-node:ekr.20081004102201.505:inVisibleArea & inExpandedVisibleArea
    #@+node:ekr.20081004102201.506:numberOfVisibleNodes
    def numberOfVisibleNodes(self):

        c = self.c

        n = 0 ; p = self.c.rootPosition()
        while p:
            n += 1
            p.moveToVisNext(c)
        return n
    #@-node:ekr.20081004102201.506:numberOfVisibleNodes
    #@+node:ekr.20081004102201.507:scrollTo (gtkTree)
    def scrollTo(self,p=None):

        """Scrolls the canvas so that p is in view."""

        c = self.c ; frame = c.frame ; trace = True
        if not p or not c.positionExists(p):
            p = c.currentPosition()
        if not p or not c.positionExists(p):
            if trace: g.trace('current p does not exist',p)
            p = c.rootPosition()
        if not p or not c.positionExists(p):
            if trace: g.trace('no root position')
            return
        try:
            h1 = self.yoffset(p)
            if self.center_selected_tree_node: # New in Leo 4.4.3.
                #@            << compute frac0 >>
                #@+node:ekr.20081004102201.508:<< compute frac0 >>
                # frac0 attempt to put the 
                scrollRegion = self.canvas.cget('scrollregion')
                geom = self.canvas.winfo_geometry()

                if scrollRegion and geom:
                    scrollRegion = scrollRegion.split(' ')
                    # g.trace('scrollRegion',repr(scrollRegion))
                    htot = int(scrollRegion[3])
                    wh,junk,junk = geom.split('+')
                    junk,h = wh.split('x')
                    if h: wtot = int(h)
                    else: wtot = 500
                    # g.trace('geom',geom,'wtot',wtot)
                    if htot > 0.1:
                        frac0 = float(h1-wtot/2)/float(htot)
                        frac0 = max(min(frac0,1.0),0.0)
                    else:
                        frac0 = 0.0
                else:
                    frac0 = 0.0 ; htot = wtot = 0
                #@-node:ekr.20081004102201.508:<< compute frac0 >>
                #@nl
                delta = abs(self.prevMoveToFrac-frac0)
                # g.trace(delta)
                if delta > 0.0:
                    self.prevMoveToFrac = frac0
                    self.canvas.yview("moveto",frac0)
                    if trace: g.trace("frac0 %1.2f %3d %3d %3d" % (frac0,h1,htot,wtot))
            else:
                last = c.lastVisible()
                nextToLast = last.visBack(c)
                h2 = self.yoffset(last)
                #@            << compute approximate line height >>
                #@+node:ekr.20081004102201.509:<< compute approximate line height >>
                if nextToLast: # 2/2/03: compute approximate line height.
                    lineHeight = h2 - self.yoffset(nextToLast)
                else:
                    lineHeight = 20 # A reasonable default.
                #@-node:ekr.20081004102201.509:<< compute approximate line height >>
                #@nl
                #@            << Compute the fractions to scroll down/up >>
                #@+node:ekr.20081004102201.510:<< Compute the fractions to scroll down/up >>
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
                #@nonl
                #@-node:ekr.20081004102201.510:<< Compute the fractions to scroll down/up >>
                #@nl
                if frac <= lo: # frac is for scrolling down.
                    if self.prevMoveToFrac != frac:
                        self.prevMoveToFrac = frac
                        self.canvas.yview("moveto",frac)
                        if trace: g.trace("frac  %1.2f %3d %3d %1.2f %1.2f" % (frac, h1,h2,lo,hi))
                elif frac2 + (hi - lo) >= hi: # frac2 is for scrolling up.
                    if self.prevMoveToFrac != frac2:
                        self.prevMoveToFrac = frac2
                        self.canvas.yview("moveto",frac2)
                        if trace: g.trace("frac2 1.2f %3d %3d %1.2f %1.2f" % (frac2,h1,h2,lo,hi))

            if self.allocateOnlyVisibleNodes:
                pass ### self.canvas.after_idle(self.idle_second_redraw)

            c.setTopVnode(p) # 1/30/04: remember a pseudo "top" node.

        except:
            g.es_exception()

    idle_scrollTo = scrollTo # For compatibility.
    #@nonl
    #@-node:ekr.20081004102201.507:scrollTo (gtkTree)
    #@+node:ekr.20081004102201.511:yoffset (gtkTree)
    #@+at 
    #@nonl
    # We can't just return icony because the tree hasn't been redrawn yet.
    # For the same reason we can't rely on any gtk canvas methods here.
    #@-at
    #@@c

    def yoffset(self,p1):
        # if not p1.isVisible(): g.pr("yoffset not visible:",p1)
        if not p1: return 0
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            root = bunch.p.copy()
        else:
            root = self.c.rootPosition()
        if root:
            h,flag = self.yoffsetTree(root,p1)
            # flag can be False during initialization.
            # if not flag: g.pr("yoffset fails:",h,v1)
            return h
        else:
            return 0

    def yoffsetTree(self,p,p1):
        h = 0 ; trace = False
        if not self.c.positionExists(p):
            if trace: g.trace('does not exist',p.headString())
            return h,False # An extra precaution.
        p = p.copy()
        for p2 in p.self_and_siblings_iter():  # was p.siblings_iter
            g.pr("yoffsetTree:", p2)
            if p2 == p1:
                if trace: g.trace(p.headString(),p1.headString(),h)
                return h, True
            h += self.line_height
            if p2.isExpanded() and p2.hasChildren():
                child = p2.firstChild()
                h2, flag = self.yoffsetTree(child,p1)
                h += h2
                if flag:
                    if trace: g.trace(p.headString(),p1.headString(),h)
                    return h, True

        if trace: g.trace('not found',p.headString(),p1.headString())
        return h, False
    #@-node:ekr.20081004102201.511:yoffset (gtkTree)
    #@-node:ekr.20081004102201.503:Helpers...
    #@-node:ekr.20081004102201.481:Drawing... (gtkTree)
    #@+node:ekr.20081004102201.512:Event handlers (gtkTree)
    #@+node:ekr.20081004102201.513:Helpers
    #@+node:ekr.20081004102201.514:checkWidgetList
    def checkWidgetList (self,tag):

        return True # This will fail when the headline actually changes!

        for w in self.visibleText:

            p = w.leo_position
            if p:
                s = w.getAllText().strip()
                h = p.headString().strip()

                if h != s:
                    self.dumpWidgetList(tag)
                    return False
            else:
                self.dumpWidgetList(tag)
                return False

        return True
    #@-node:ekr.20081004102201.514:checkWidgetList
    #@+node:ekr.20081004102201.515:dumpWidgetList
    def dumpWidgetList (self,tag):

        g.pr("\ncheckWidgetList: %s" % tag)

        for w in self.visibleText:

            p = w.leo_position
            if p:
                s = w.getAllText().strip()
                h = p.headString().strip()

                addr = self.textAddr(w)
                g.pr("p:",addr,h)
                if h != s:
                    g.pr("w:",'*' * len(addr),s)
            else:
                g.pr("w.leo_position == None",w)
    #@-node:ekr.20081004102201.515:dumpWidgetList
    #@+node:ekr.20081004102201.516:tree.edit_widget
    def edit_widget (self,p):

        """Returns the gtk.Edit widget for position p."""

        return self.findEditWidget(p)
    #@nonl
    #@-node:ekr.20081004102201.516:tree.edit_widget
    #@+node:ekr.20081004102201.517:eventToPosition
    def eventToPosition (self,event):

        p = event.p
        if p:
            return p.copy()



        # canvas = self.canvas
        # x,y = event.x,event.y
        # x = canvas.canvasx(x) 
        # y = canvas.canvasy(y)
        # if self.trace: g.trace(x,y)
        # item = canvas.find_overlapping(x,y,x,y)
        # if not item: return None

        # # Item may be a tuple, possibly empty.
        # try:    theId = item[0]
        # except: theId = item
        # if not theId: return None

        # p = self.ids.get(theId)

        # # A kludge: p will be None for vertical lines.
        # if not p:
            # item = canvas.find_overlapping(x+1,y,x+1,y)
            # try:    theId = item[0]
            # except: theId = item
            # if not theId:
                # g.es_print('oops:','eventToPosition','failed')
                # return None
            # p = self.ids.get(theId)
            # # g.trace("was vertical line",p)

        # if self.trace and self.verbose:
            # if p:
                # w = self.findEditWidget(p)
                # g.trace("%3d %3d %3d %d" % (theId,x,y,id(w)),p.headString())
            # else:
                # g.trace("%3d %3d %3d" % (theId,x,y),None)

        # # defensive programming: this copy is not needed.
        # if p: return p.copy() # Make _sure_ nobody changes this table!
        # else: return None
    #@-node:ekr.20081004102201.517:eventToPosition
    #@+node:ekr.20081004102201.518:findEditWidget
    def findEditWidget (self,p):

        """Return the gtk.Text item corresponding to p."""

        c = self.c

        if p and c:
            aTuple = self.visibleText.get(p.key())
            if aTuple:
                w,theId = aTuple
                # g.trace('%4d' % (theId),self.textAddr(w),p.headString())
                return w
            else:
                # g.trace('oops: not found',p)
                return None

        # g.trace(not found',p.headString())
        return None
    #@-node:ekr.20081004102201.518:findEditWidget
    #@+node:ekr.20081004102201.519:findVnodeWithIconId
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
                    g.trace(theId,p.headString())
                return p
            else:
                if self.trace and self.verbose:
                    g.trace("*** wrong generation: %d ***" % theId)
                return None
        else:
            if self.trace and self.verbose: g.trace(theId,None)
            return None
    #@-node:ekr.20081004102201.519:findVnodeWithIconId
    #@-node:ekr.20081004102201.513:Helpers
    #@+node:ekr.20081004102201.520:Click Box...
    #@+node:ekr.20081004102201.521:onClickBoxClick
    def onClickBoxClick (self,event,p=None):
        """Respond to clicks on expand/contract button."""

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
    #@-node:ekr.20081004102201.521:onClickBoxClick
    #@-node:ekr.20081004102201.520:Click Box...
    #@+node:ekr.20081004102201.522:Dragging (gtkTree)
    #@+node:ekr.20081004102201.523:endDrag
    def endDrag (self,event):

        """The official helper of the onEndDrag event handler."""

        g.trace()
        return ###

        c = self.c ; p = self.drag_p
        c.setLog()
        canvas = self.canvas
        if not event: return

        #@    << set vdrag, childFlag >>
        #@+node:ekr.20081004102201.524:<< set vdrag, childFlag >>
        x,y = event.x,event.y
        canvas_x = canvas.canvasx(x)
        canvas_y = canvas.canvasy(y)

        theId = self.canvas.find_closest(canvas_x,canvas_y)
        # theId = self.canvas.find_overlapping(canvas_x,canvas_y,canvas_x,canvas_y)

        vdrag = self.findPositionWithIconId(theId)
        childFlag = vdrag and vdrag.hasChildren() and vdrag.isExpanded()
        #@-node:ekr.20081004102201.524:<< set vdrag, childFlag >>
        #@nl
        if self.allow_clone_drags:
            if not self.look_for_control_drag_on_mouse_down:
                self.controlDrag = c.frame.controlKeyIsDown

        redrawFlag = vdrag and vdrag.v.t != p.v.t
        if redrawFlag: # Disallow drag to joined node.
            #@        << drag p to vdrag >>
            #@+node:ekr.20081004102201.525:<< drag p to vdrag >>
            # g.trace("*** end drag   ***",theId,x,y,p.headString(),vdrag.headString())

            if self.controlDrag: # Clone p and move the clone.
                if childFlag:
                    c.dragCloneToNthChildOf(p,vdrag,0)
                else:
                    c.dragCloneAfter(p,vdrag)
            else: # Just drag p.
                if childFlag:
                    c.dragToNthChildOf(p,vdrag,0)
                else:
                    c.dragAfter(p,vdrag)
            #@-node:ekr.20081004102201.525:<< drag p to vdrag >>
            #@nl
        elif self.trace and self.verbose:
            g.trace("Cancel drag")

        # Reset the old cursor by brute force.
        self.canvas['cursor'] = "arrow"
        self.dragging = False
        self.drag_p = None
        # Must set self.drag_p = None first.
        if redrawFlag: c.redraw()
        c.recolor_now() # Dragging can affect coloring.
    #@-node:ekr.20081004102201.523:endDrag
    #@+node:ekr.20081004102201.526:startDrag
    # This precomputes numberOfVisibleNodes(), a significant optimization.
    # We also indicate where findPositionWithIconId() should start looking for tree id's.

    def startDrag (self,event,p=None):

        g.trace()
        return ###

        """The official helper of the onDrag event handler."""

        c = self.c ; canvas = self.canvas
        return ###

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
        # g.trace("*** start drag ***",theId,self.drag_p.headString())
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
    #@-node:ekr.20081004102201.526:startDrag
    #@+node:ekr.20081004102201.527:onContinueDrag
    def onContinueDrag(self,event):

        g.trace()###
        return

        p = self.drag_p
        if not p: return

        try:
            canvas = self.canvas ; frame = self.c.frame
            if event:
                x,y = event.x,event.y
            else:
                x,y = frame.top.winfo_pointerx(),frame.top.winfo_pointery()
                # Stop the scrolling if we go outside the entire window.
                if x == -1 or y == -1: return 
            if self.dragging: # This gets cleared by onEndDrag()
                #@            << scroll the canvas as needed >>
                #@+node:ekr.20081004102201.528:<< scroll the canvas as needed >>
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
                        pass ### canvas.after_idle(self.onContinueDrag,None) # Don't propagate the event.
                #@-node:ekr.20081004102201.528:<< scroll the canvas as needed >>
                #@nl
        except:
            g.es_event_exception("continue drag")
    #@-node:ekr.20081004102201.527:onContinueDrag
    #@+node:ekr.20081004102201.529:onDrag
    def onDrag(self,event):

        g.trace()
        return ###

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
    #@-node:ekr.20081004102201.529:onDrag
    #@+node:ekr.20081004102201.530:onEndDrag
    def onEndDrag(self,event):

        g.trace()
        return ###

        """Tree end-of-drag handler called from vnode event handler."""

        c = self.c ; p = self.drag_p
        if not p: return

        c.setLog()

        if not g.doHook("enddrag1",c=c,p=p,v=p,event=event):
            self.endDrag(event)
        g.doHook("enddrag2",c=c,p=p,v=p,event=event)
    #@-node:ekr.20081004102201.530:onEndDrag
    #@-node:ekr.20081004102201.522:Dragging (gtkTree)
    #@+node:ekr.20081004102201.531:Icon Box...
    #@+node:ekr.20081004102201.532:onIconBoxClick
    def onIconBoxClick (self,event,p=None):

        c = self.c ; tree = self

        if not p: p = self.eventToPosition(event)
        if not p: return

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
    #@-node:ekr.20081004102201.532:onIconBoxClick
    #@+node:ekr.20081004102201.533:onIconBoxRightClick
    def onIconBoxRightClick (self,event,p=None):

        """Handle a right click in any outline widget."""

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p: return

        c.setLog()

        try:
            if not g.doHook("iconrclick1",c=c,p=p,v=p,event=event):
                self.OnActivateHeadline(p)
                self.endEditLabel()
                self.OnPopup(p,event)
            g.doHook("iconrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("iconrclick")

        return 'break'
    #@-node:ekr.20081004102201.533:onIconBoxRightClick
    #@+node:ekr.20081004102201.534:onIconBoxDoubleClick
    def onIconBoxDoubleClick (self,event,p=None):

        c = self.c

        if not p: p = self.eventToPosition(event)
        if not p: return

        c.setLog()

        if self.trace and self.verbose: g.trace()

        try:
            if not g.doHook("icondclick1",c=c,p=p,v=p,event=event):
                self.endEditLabel() # Bug fix: 11/30/05
                self.OnIconDoubleClick(p) # Call the method in the base class.
            g.doHook("icondclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("icondclick")

        return 'break' # 11/19/06
    #@-node:ekr.20081004102201.534:onIconBoxDoubleClick
    #@-node:ekr.20081004102201.531:Icon Box...
    #@+node:ekr.20081004102201.535:OnActivateHeadline (gtkTree)
    def OnActivateHeadline (self,p,event=None):

        '''Handle common process when any part of a headline is clicked.'''

        # g.trace(p.headString())

        returnVal = 'break' # Default: do nothing more.
        trace = False

        try:
            c = self.c
            c.setLog()
            #@        << activate this window >>
            #@+node:ekr.20081004102201.536:<< activate this window >>
            if p == c.currentPosition():

                if trace: g.trace('current','active',self.active)
                self.editLabel(p) # sets focus.
                # If we are active, pass the event along so the click gets handled.
                # Otherwise, do *not* pass the event along so the focus stays the same.
                returnVal = g.choose(self.active,'continue','break')
                self.active = True
            else:
                if trace: g.trace("not current")
                self.select(p,scroll=False)
                w  = c.frame.body.bodyCtrl
                if c.frame.findPanel:
                    c.frame.findPanel.handleUserClick(p)
                if p.v.t.insertSpot != None:
                    spot = p.v.t.insertSpot
                    w.setInsertPoint(spot)
                    w.see(spot)
                else:
                    w.setInsertPoint(0)
                # An important detail.
                # The *canvas* (not the headline) gets the focus so that
                # tree bindings take priority over text bindings.
                c.treeWantsFocus()
                self.active = False
                returnVal = 'break'
            #@nonl
            #@-node:ekr.20081004102201.536:<< activate this window >>
            #@nl
        except:
            g.es_event_exception("activate tree")

        return returnVal
    #@-node:ekr.20081004102201.535:OnActivateHeadline (gtkTree)
    #@+node:ekr.20081004102201.537:Text Box...
    #@+node:ekr.20081004102201.538:configureTextState
    def configureTextState (self,p):

        c = self.c

        if not p: return

        # g.trace(p.headString(),self.c._currentPosition)

        if c.isCurrentPosition(p):
            if p == self.editPosition():
                self.setEditLabelState(p) # selected, editing.
            else:
                self.setSelectedLabelState(p) # selected, not editing.
        else:
            self.setUnselectedLabelState(p) # unselected
    #@-node:ekr.20081004102201.538:configureTextState
    #@+node:ekr.20081004102201.539:onCtontrolT
    # This works around an apparent gtk bug.

    def onControlT (self,event=None):

        # If we don't inhibit further processing the Tx.Text widget switches characters!
        return "break"
    #@-node:ekr.20081004102201.539:onCtontrolT
    #@+node:ekr.20081004102201.540:onHeadlineClick
    def onHeadlineClick (self,event,p=None):

        # g.trace('p',p)
        c = self.c ; w = event.widget

        if not p:
            try:
                p = w.leo_position
            except AttributeError:
                g.trace('*'*20,'oops')
        if not p: return 'break'

        # g.trace(g.app.gui.widget_name(w)) #p.headString())

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
    #@-node:ekr.20081004102201.540:onHeadlineClick
    #@+node:ekr.20081004102201.541:onHeadlineRightClick
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
                self.OnPopup(p,event)
            g.doHook("headrclick2",c=c,p=p,v=p,event=event)
        except:
            g.es_event_exception("headrclick")

        # 'continue' *is* correct here.
        # 'break' would make it impossible to unselect the headline text.
        return 'continue'
    #@-node:ekr.20081004102201.541:onHeadlineRightClick
    #@-node:ekr.20081004102201.537:Text Box...
    #@+node:ekr.20081004102201.542:tree.OnDeactivate
    def OnDeactivate (self,event=None):

        """Deactivate the tree pane, dimming any headline being edited."""

        tree = self ; c = self.c

        tree.endEditLabel()
        tree.dimEditLabel()
    #@-node:ekr.20081004102201.542:tree.OnDeactivate
    #@+node:ekr.20081004102201.543:tree.OnPopup & allies
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
    #@+node:ekr.20081004102201.544:OnPopupFocusLost
    #@+at 
    #@nonl
    # On Linux we must do something special to make the popup menu "unpost" if 
    # the mouse is clicked elsewhere.  So we have to catch the <FocusOut> 
    # event and explicitly unpost.  In order to process the <FocusOut> event, 
    # we need to be able to find the reference to the popup window again, so 
    # this needs to be an attribute of the tree object; hence, 
    # "self.popupMenu".
    # 
    # Aside: though gtk tries to be muli-platform, the interaction with 
    # different window managers does cause small differences that will need to 
    # be compensated by system specific application code. :-(
    #@-at
    #@@c

    # 20-SEP-2002 DTHEIN: This event handler is only needed for Linux.

    def OnPopupFocusLost(self,event=None):

        self.popupMenu.unpost()
    #@-node:ekr.20081004102201.544:OnPopupFocusLost
    #@+node:ekr.20081004102201.545:createPopupMenu
    def createPopupMenu (self,event):

        c = self.c ; frame = c.frame

        # If we are going to recreate it, we had better destroy it.
        if self.popupMenu:
            #self.popupMenu.destroy()
            self.popupMenu = None

        self.popupMenu = menu = frame.menu.getMenu()

        # Add the Open With entries if they exist.
        if g.app.openWithTable:
            frame.menu.createOpenWithMenuItemsFromTable(menu,g.app.openWithTable)
            table = (("-",None,None),)
            frame.menu.createMenuEntries(menu,table)

        #@    << Create the menu table >>
        #@+node:ekr.20081004102201.546:<< Create the menu table >>

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
        #@-node:ekr.20081004102201.546:<< Create the menu table >>
        #@nl

        # New in 4.4.  There is no need for a dontBind argument because
        # Bindings from tables are ignored.
        frame.menu.createMenuEntries(menu,table)
    #@-node:ekr.20081004102201.545:createPopupMenu
    #@+node:ekr.20081004102201.547:enablePopupMenuItems
    def enablePopupMenuItems (self,v,event):

        """Enable and disable items in the popup menu."""

        c = self.c ; menu = self.popupMenu

        #@    << set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@+node:ekr.20081004102201.548:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        isAtFile = False
        isAtRoot = False

        for v2 in v.self_and_subtree_iter():
            if isAtFile and isAtRoot:
                break
            if (v2.isAtFileNode() or
                v2.isAtNorefFileNode() or
                v2.isAtAsisFileNode() or
                v2.isAtNoSentFileNode()
            ):
                isAtFile = True

            isRoot,junk = g.is_special(v2.bodyString(),0,"@root")
            if isRoot:
                isAtRoot = True
        #@-node:ekr.20081004102201.548:<< set isAtRoot and isAtFile if v's tree contains @root or @file nodes >>
        #@nl
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
    #@-node:ekr.20081004102201.547:enablePopupMenuItems
    #@+node:ekr.20081004102201.549:showPopupMenu
    def showPopupMenu (self,event):

        """Show a popup menu."""

        g.trace()

        c = self.c ; menu = self.popupMenu

        menu.popup(None, None, None, event.button, event.time)

        # # Set the focus immediately so we know when we lose it.
        #c.widgetWantsFocus(menu)
    #@-node:ekr.20081004102201.549:showPopupMenu
    #@-node:ekr.20081004102201.543:tree.OnPopup & allies
    #@+node:ekr.20081004102201.550:onTreeClick
    def onTreeClick (self,event=None):

        '''Handle an event in the tree canvas, outside of any tree widget.'''

        c = self.c

        # New in Leo 4.4.2: a kludge: disable later event handling after a double-click.
        # This allows focus to stick in newly-opened files opened by double-clicking an @url node.
        if c.doubleClickFlag:
            c.doubleClickFlag = False
        else:
            c.treeWantsFocusNow()

        return 'break'
    #@-node:ekr.20081004102201.550:onTreeClick
    #@-node:ekr.20081004102201.512:Event handlers (gtkTree)
    #@+node:ekr.20081004102201.551:Incremental drawing...(gtkTree: not used)
    if 0:
        #@    @+others
        #@+node:ekr.20081004102201.552:allocateNodes
        def allocateNodes(self,where,lines):

            """Allocate gtk widgets in nodes that will become visible as the result of an upcoming scroll"""

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
        #@-node:ekr.20081004102201.552:allocateNodes
        #@+node:ekr.20081004102201.553:allocateNodesBeforeScrolling
        def allocateNodesBeforeScrolling (self, args):

            """Calculate the nodes that will become visible as the result of an upcoming scroll.

            args is the tuple passed to the gtk.Canvas.yview method"""

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
        #@-node:ekr.20081004102201.553:allocateNodesBeforeScrolling
        #@+node:ekr.20081004102201.554:updateNode
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
        #@-node:ekr.20081004102201.554:updateNode
        #@+node:ekr.20081004102201.555:setVisibleAreaToFullCanvas
        def setVisibleAreaToFullCanvas(self):

            if self.visibleArea:
                y1,y2 = self.visibleArea
                y2 = max(y2,y1 + self.canvas.winfo_height())
                self.visibleArea = y1,y2
        #@-node:ekr.20081004102201.555:setVisibleAreaToFullCanvas
        #@+node:ekr.20081004102201.556:setVisibleArea
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
        #@-node:ekr.20081004102201.556:setVisibleArea
        #@+node:ekr.20081004102201.557:tree.updateTree
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
        #@-node:ekr.20081004102201.557:tree.updateTree
        #@-others
    #@nonl
    #@-node:ekr.20081004102201.551:Incremental drawing...(gtkTree: not used)
    #@+node:ekr.20081004102201.558:Selecting & editing... (gtkTree)
    #@+node:ekr.20081004102201.559:dimEditLabel, undimEditLabel
    # Convenience methods so the caller doesn't have to know the present edit node.

    def dimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)

    def undimEditLabel (self):

        p = self.c.currentPosition()
        self.setSelectedLabelState(p)
    #@-node:ekr.20081004102201.559:dimEditLabel, undimEditLabel
    #@+node:ekr.20081004102201.560:tree.editLabel
    def editLabel (self,p,selectAll=False):

        """Start editing p's headline."""

        c = self.c
        trace = not g.app.unitTesting and (False or self.trace_edit)

        if p and p != self.editPosition():

            if trace:
                g.trace(p.headString(),g.choose(c.edit_widget(p),'','no edit widget'))

            self.endEditLabel()
            c.redraw()

        self.setEditPosition(p) # That is, self._editPosition = p

        if trace: g.trace(c.edit_widget(p))

        if p and c.edit_widget(p):
            self.revertHeadline = p.headString() # New in 4.4b2: helps undo.
            self.setEditLabelState(p,selectAll=selectAll) # Sets the focus immediately.
            c.headlineWantsFocus(p) # Make sure the focus sticks.
    #@-node:ekr.20081004102201.560:tree.editLabel
    #@+node:ekr.20081004102201.561:tree.set...LabelState
    #@+node:ekr.20081004102201.562:setEditLabelState
    def setEditLabelState (self,p,selectAll=False): # selected, editing

        c = self.c ; w = c.edit_widget(p)

        if p and w:
            # g.trace('*****',g.callers())
            c.widgetWantsFocusNow(w)
            self.setEditHeadlineColors(p)
            selectAll = selectAll or self.select_all_text_when_editing_headlines
            if selectAll:
                w.setSelectionRange(0,'end',insert='end')
            else:
                w.setInsertPoint('end') # Clears insert point.
        else:
            g.trace('no edit_widget')

    setNormalLabelState = setEditLabelState # For compatibility.
    #@-node:ekr.20081004102201.562:setEditLabelState
    #@+node:ekr.20081004102201.563:setSelectedLabelState
    def setSelectedLabelState (self,p): # selected, disabled

        # g.trace(p.headString(),g.callers())

        c = self.c

        if p and c.edit_widget(p):
            self.setDisabledHeadlineColors(p)
    #@-node:ekr.20081004102201.563:setSelectedLabelState
    #@+node:ekr.20081004102201.564:setUnselectedLabelState
    def setUnselectedLabelState (self,p): # not selected.

        c = self.c

        if p and c.edit_widget(p):
            self.setUnselectedHeadlineColors(p)
    #@-node:ekr.20081004102201.564:setUnselectedLabelState
    #@+node:ekr.20081004102201.565:setDisabledHeadlineColors
    def setDisabledHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
                g.trace("%10s %d %s" % ("disabled",id(w),p.headString()))
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
    #@-node:ekr.20081004102201.565:setDisabledHeadlineColors
    #@+node:ekr.20081004102201.566:setEditHeadlineColors
    def setEditHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
                g.pr("%10s %d %s" % ("edit",id(2),p.headString()))

        fg    = self.headline_text_editing_foreground_color or 'black'
        bg    = self.headline_text_editing_background_color or 'white'
        selfg = self.headline_text_editing_selection_foreground_color or 'white'
        selbg = self.headline_text_editing_selection_background_color or 'black'

        try: # Use system defaults for selection foreground/background
            w.configure(state="normal",highlightthickness=1,
            fg=fg,bg=bg,selectforeground=selfg,selectbackground=selbg)
        except:
            g.es_exception()
    #@-node:ekr.20081004102201.566:setEditHeadlineColors
    #@+node:ekr.20081004102201.567:setUnselectedHeadlineColors
    def setUnselectedHeadlineColors (self,p):

        c = self.c ; w = c.edit_widget(p)

        if self.trace and self.verbose:
            if not self.redrawing:
                g.pr("%10s %d %s" % ("unselect",id(w),p.headString()))
                # import traceback ; traceback.print_stack(limit=6)

        fg = self.headline_text_unselected_foreground_color or 'black'
        bg = self.headline_text_unselected_background_color or 'white'

        try:
            w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg,
                selectbackground=bg,selectforeground=fg,highlightbackground=bg)
        except:
            g.es_exception()
    #@-node:ekr.20081004102201.567:setUnselectedHeadlineColors
    #@-node:ekr.20081004102201.561:tree.set...LabelState
    #@+node:ekr.20081004102201.568:tree.setHeadline (gtkTree)
    def setHeadline (self,p,s):

        '''Set the actual text of the headline widget.

        This is called from the undo/redo logic to change the text before redrawing.'''

        w = self.edit_widget(p)
        if w:
            w.configure(state='normal')
            w.delete(0,'end')
            if s.endswith('\n') or s.endswith('\r'):
                s = s[:-1]
            w.insert(0,s)
            self.revertHeadline = s
            # g.trace(repr(s),w.getAllText())
        else:
            g.trace('-'*20,'oops')
    #@-node:ekr.20081004102201.568:tree.setHeadline (gtkTree)
    #@-node:ekr.20081004102201.558:Selecting & editing... (gtkTree)
    #@-others
#@-node:ekr.20081004102201.448:class leoGtkTree (leoFrame.leoTree)
#@+node:ekr.20081004102201.569:== Outline Canvas Widget ==
#@+node:ekr.20081004102201.570:class FakeEvent
class FakeEvent(object):

    def __init__(self, widget, rawEvent, p):

        self.widget = widget
        self.rawEvent = rawEvent
        self.p = p

#@-node:ekr.20081004102201.570:class FakeEvent
#@+node:ekr.20081004102201.571:class OutlineCanvasPanel

class OutlineCanvasPanel(gobject.GObject):
    """A widget to display and manipulate a leo outline.

    This class provides the public interface for the outline widget
    and handles the scroll bar interface.

    The actual drawing handled by OutlineCanvas.

    The actual base gui component is a gtk.Table which can be found
    in self.top

    NOTE: This class is a subclass of GObject because it offers
    the possibility of using custom events and gobject properties that 
    can issue custom events when they are changed.

    """

    #@    << gobject properties >>
    #@+node:ekr.20081004102201.572:<< gobject properties >>
    #@+at
    # This is where we declare out custom properties.
    # 
    # Remember that ALL children of this node are entries in a list
    # that initializes a dictionary.
    #@-at
    #@@c


    def do_get_property(self, property):

        return getattr(self, 'property_' + property.name.replace('-','_'))


    def do_set_property(self, property, value):

       setattr(self, 'property_' + property.name.replace('-','_'), value)



    __gproperties__ = {

        #@    @+others
        #@+node:ekr.20081004102201.573:canvas height
        'canvas-height' : (
            gobject.TYPE_PYOBJECT,
            'canvas height',
            'The height of the tree in its currently expanded state',
            gobject.PARAM_READWRITE
        ),

        #@-node:ekr.20081004102201.573:canvas height
        #@-others

    }

    #@-node:ekr.20081004102201.572:<< gobject properties >>
    #@nl
    #@    << gobject signals >>
    #@+node:ekr.20081004102201.574:<< gobject signals >>
    #@-node:ekr.20081004102201.574:<< gobject signals >>
    #@nl

    #@    @+others
    #@+node:ekr.20081004102201.575:onButtonPress
    def onButtonPress(self, w, event, *args):
        """Convert mouse button events into tk style events and pass up to leoTree.

        The outline canvas widget handles NO mouse events.

        """

        g.trace(event.x, event.y)

        codes = {
            gtk.gdk.BUTTON_PRESS: 'Button',
            gtk.gdk._2BUTTON_PRESS: 'Double',
            gtk.gdk._3BUTTON_PRESS: 'Triple',
            gtk.gdk.BUTTON_RELEASE: 'Any-ButtonRelease'
        }

        sp, target = self._canvas.hitTest(event.x, event.y)

        eventType = '<%s-%s>' % (codes[event.type], event.button)

        fakeEvent = FakeEvent(self, event, sp)

        self.leo_position = sp and sp.copy()

        self._leoTree.onOutlineCanvasEvent(target, eventType, fakeEvent, self.leo_position)

        return True

    #@-node:ekr.20081004102201.575:onButtonPress
    #@+node:ekr.20081004102201.576:__init__

    def __init__(self, leoTree, name):
        """Create an OutlineCanvasPanel instance."""

        gobject.GObject.__init__(self)

        g.trace('OutlineCanvasPanel', leoTree, name)

        self._leoTree = leoTree
        self.c = leoTree.c

        self._canvas = canvas = OutlineCanvas(self)
        self._canvas.connect('button_press_event', self.onButtonPress)

        self._table = self.top = gtk.Table(2,2)

        self._hscrollbar = gtk.HScrollbar()
        self._vscrollbar = gtk.VScrollbar()

        self._hadj = h = self._hscrollbar.get_adjustment()
        self._vadj = v = self._vscrollbar.get_adjustment()

        self._hscrollbar.set_range(0, 10)
        self._vscrollbar.set_range(0, 20)


        v.connect('value-changed', self.onScrollVertical)
        h.connect('value-changed', self.onScrollHorizontal)

        self._table.attach(self._hscrollbar, 0, 1, 1, 2, yoptions=0)
        self._table.attach(self._vscrollbar, 1, 2, 0, 1, xoptions=0)


        options = gtk.SHRINK | gtk.FILL | gtk.EXPAND
        self._table.attach(self._canvas, 0, 1, 0, 1, options, options)

        self._canvas.set_events(gtk.gdk.ALL_EVENTS_MASK)

        #@    << gproperty ivars >>
        #@+node:ekr.20081004102201.577:<< gproperty ivars >>
        self.property_canvas_height = 0
        #@nonl
        #@-node:ekr.20081004102201.577:<< gproperty ivars >>
        #@nl


        #self._entry = wx.TextCtrl(self._canvas,
        #    style = wx.SIMPLE_BORDER | wx.WANTS_CHARS
        #)

        #self._entry._virtualTop = -1000
        #self._entry.Hide()
        #self._canvas._widgets.append(self._entry)

        #self._canvas.update()


        # self.Bind(wx.EVT_SIZE, self.onSize)


        #self.SetBackgroundColour(self._leoTree.outline_pane_background_color)

        #self.Bind(wx.EVT_CHAR,
        #    lambda event, self=self._leoTree: onGlobalChar(self, event)
        #)

        #self.onScroll(wx.HORIZONTAL, 0)

    #@-node:ekr.20081004102201.576:__init__
    #@+node:ekr.20081004102201.578:showEntry
    showcount = 0
    def showEntry(self):

        # self.showcount +=1

        # g.trace(self.showcount, g.callers(20))

        entry = self._entry
        canvas = self._canvas

        ep = self._leoTree.editPosition()

        if not ep:
            return self.hideEntry()


        for sp in canvas._positions:
            if ep == sp:
                break
        else:
            return self.hideEntry()

        x, y, width, height = sp._textBoxRect
        #g.pr('	', x, y, width , height)

        entry._virtualTop = canvas._virtualTop + y -2

        entry.MoveXY(x - 2, y -2)
        entry.SetSize((max(width + 4, 100), -1))

        tw = self._leoTree.headlineTextWidget

        range = tw.getSelectionRange()
        tw.setInsertPoint(0)
        #tw.setInsertPoint(len(sp.headString()))
        tw.setSelectionRange(*range)
        entry.Show()
    #@-node:ekr.20081004102201.578:showEntry
    #@+node:ekr.20081004102201.579:hideEntry

    def hideEntry(self):

        entry = self._entry
        entry._virtualTop = -1000
        entry.MoveXY(0, -1000)

        entry.Hide()
    #@-node:ekr.20081004102201.579:hideEntry
    #@+node:ekr.20081004102201.580:getPositions

    def getPositions(self):
        return self._canvas._positions[:]
    #@nonl
    #@-node:ekr.20081004102201.580:getPositions
    #@+node:ekr.20081004102201.581:onScrollVertical
    def onScrollVertical(self, adjustment):
        """Handle changes in the position of the value of the vertical adustment."""

        self._canvas.vscrollTo(int(adjustment.value))
    #@nonl
    #@-node:ekr.20081004102201.581:onScrollVertical
    #@+node:ekr.20081004102201.582:onScrollHorizontal
    def onScrollHorizontal(self, adjustment):
        """Handle changes in the position of the value of the horizontal adustment."""

        self._canvas.hscrollTo(int(adjustment.value))
    #@-node:ekr.20081004102201.582:onScrollHorizontal
    #@+node:ekr.20081004102201.583:vscrollUpdate

    def vscrollUpdate(self):
        """Set the vertical scroll bar to match current conditions."""

        canvas = self._canvas

        oldtop = top = canvas._virtualTop
        canvasHeight = canvas.get_allocation().height
        treeHeight = canvas._treeHeight

        if (treeHeight - top) < canvasHeight:
            top = treeHeight - canvasHeight

        if top < 0 :
            top = 0

        if oldtop != top:
            canvas._virtualTop = top
            canvas.redraw()
            top = canvas._virtualTop

        #self.showEntry()

        self._vadj.set_all(
            top, #value
            0, #lower
            treeHeight, #upper
            canvasHeight * 0.1, #step_increment
            canvasHeight * 0.9, #page_increment
            canvasHeight #page-size
        )


    #@-node:ekr.20081004102201.583:vscrollUpdate
    #@+node:ekr.20081004102201.584:hscrollUpdate

    def hscrollUpdate(self):
        """Set the horizontal scroll bar to match current conditions."""

        canvas = self._canvas

        oldleft = left = canvas._virtualLeft
        canvasWidth = canvas.get_allocation().width
        treeWidth = canvas._treeWidth

        if (treeWidth - left) < canvasWidth:
            left = treeWidth - canvasWidth

        if left < 0 :
            left = 0

        if oldleft != left:
            canvas._virtualLeft = left
            canvas.redraw()
            left = canvas._virtualLeft

        #self.showEntry()

        self._hadj.set_all(
            left, #value
            0, #lower
            treeWidth, #upper
            canvasWidth * 0.1, #step_increment
            canvasWidth * 0.9, #page_increment
            canvasWidth #page-size
        )

    #@-node:ekr.20081004102201.584:hscrollUpdate
    #@+node:ekr.20081004102201.585:update

    def update(self):
        self._canvas.update()


    #@-node:ekr.20081004102201.585:update
    #@+node:ekr.20081004102201.586:redraw

    def redraw(self):
        self._canvas.redraw()
    #@nonl
    #@-node:ekr.20081004102201.586:redraw
    #@+node:ekr.20081004102201.587:refresh
    def refresh(self):
        self._canvas.refresh()
    #@nonl
    #@-node:ekr.20081004102201.587:refresh
    #@+node:ekr.20081004102201.588:GetName
    def GetName(self):
        return 'canvas'

    getName = GetName
    #@nonl
    #@-node:ekr.20081004102201.588:GetName
    #@-others

gobject.type_register(OutlineCanvasPanel)
#@-node:ekr.20081004102201.571:class OutlineCanvasPanel
#@+node:ekr.20081004102201.589:class OutlineCanvas
class OutlineCanvas(gtk.DrawingArea):
    """Implements a virtual view of a leo outline tree.

    The class uses an off-screen buffer for drawing which it
    blits to the window during paint calls for expose events, etc,

    A redraw is only required when the size of the canvas changes,
    a scroll event occurs, or if the outline changes.

    """

    #@    @+others
    #@+node:ekr.20081004102201.590:__init__
    def __init__(self, parent):
        """Create an OutlineCanvas instance."""

        #g.trace('OutlineCanvas')

        self.c = c = parent.c

        self._parent = parent
        #self.leoTree = parent.leoTree


        #@    << define ivars >>
        #@+node:ekr.20081004102201.591:<< define ivars >>
        #self._icons = icons

        self._widgets = []

        self.drag_p = None

        self._size =  [1000, 1000]

        self._virtualTop = 0
        self._virtualLeft = 0

        self._textIndent = 30

        self._xPad = 30
        self._yPad = 2

        self._treeHeight = 500
        self._treeWidth = 500

        self._positions = []

        self._fontHeight = None
        self._iconSize = [20, 11]

        self._clickBoxSize = None
        self._lineHeight =  10
        self._requestedLineHeight = 10

        self._yTextOffset = None
        self._yIconOffset = None

        self._clickBoxCenterOffset = None

        self._clickBoxOffset = None


        #@-node:ekr.20081004102201.591:<< define ivars >>
        #@nl

        gtk.DrawingArea.__init__(self)
        self._pangoLayout = self.create_pango_layout("Wq")


        # g.trace()


        self._font = pango.FontDescription('Sans 12')

        self._pangoLayout.set_font_description(self._font)


        self._buffer = None

        self.contextChanged()

        self.connect('map-event', self.onMap)


        # ??? diable keys for the time being
        self.connect('key-press-event', lambda *args: True)
        self.connect('key-release-event', lambda *args: True)


        #for o in (self, parent):
        #    
        #@nonl
        #@<< create  bindings >>
        #@+node:ekr.20081004102201.592:<< create bindings >>
        # onmouse = self._leoTree.onMouse

        # for e, s in (
           # ( wx.EVT_LEFT_DOWN,     'LeftDown'),
           # ( wx.EVT_LEFT_UP,       'LeftUp'),
           # ( wx.EVT_LEFT_DCLICK,   'LeftDoubleClick'),
           # ( wx.EVT_MIDDLE_DOWN,   'MiddleDown'),
           # ( wx.EVT_MIDDLE_UP,     'MiddleUp'),
           # ( wx.EVT_MIDDLE_DCLICK, 'MiddleDoubleClick'),
           # ( wx.EVT_RIGHT_DOWN,    'RightDown'),
           # ( wx.EVT_RIGHT_UP,      'RightUp'),
           # ( wx.EVT_RIGHT_DCLICK,  'RightDoubleClick'),
           # ( wx.EVT_MOTION,        'Motion')
        # ):
            # o.Bind(e, lambda event, type=s: onmouse(event, type))



        # #self.Bind(wx.EVT_KEY_UP, self._leoTree.onChar)
        # #self.Bind(wx.EVT_KEY_DOWN, lambda event: self._leoTree.onKeyDown(event))

        # self.Bind(wx.EVT_CHAR,
            # lambda event, self=self._leoTree: onGlobalChar(self, event)
        # )

        #@-node:ekr.20081004102201.592:<< create bindings >>
        #@nl

    #@+at
    # self.box_padding = 5 # extra padding between box and icon
    # self.box_width = 9 + self.box_padding
    # self.icon_width = 20
    # self.text_indent = 4 # extra padding between icon and tex
    # 
    # self.hline_y = 7 # Vertical offset of horizontal line
    # self.root_left = 7 + self.box_width
    # self.root_top = 2
    # 
    # self.default_line_height = 17 + 2 # default if can't set line_height 
    # from font.
    # self.line_height = self.default_line_height
    # 
    #@-at
    #@-node:ekr.20081004102201.590:__init__
    #@+node:ekr.20081004102201.593:hitTest
    def hitTest(self, xx, yy):
        """Trace for hitTest

        Rename folowwing hitTest to _hitTest, to enable trace.
        """
        result = self._hitTest(point)
        g.trace(result)
        return result

    def hitTest(self, xx, yy):
        """Returns a (position, item) tuple indecating where the hit occured.

        position indicates which headline was hit

        item indicates which portion of the headline that was hit.

        item is a string which can take the following values:

            + 'clickBox'
            + 'iconBox'
            + 'textBox'
            + 'beforeText-*'  (* is an number indicating which beforeText icon was hit)
            + 'headline' ( if on a headline but non of the others was hit.)
            + 'canvas'   ( The canvas was hit but there is no headline there.)




        """

        for sp in self._positions:

            if yy < (sp._top + self._lineHeight):

                x, y, w, h = sp._clickBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h):
                    return sp, 'clickBox'

                x, y, w, h = sp._iconBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h):
                    return sp, 'iconBox'

                x, y, w, h = sp._textBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h): 
                    return sp, 'textBox'

                if hasattr(sp, '_headStringIcons'):
                    i = -1
                    for x, y, w, h in sp._headStringIcons:
                        i += 1
                        if xx > x  and xx < (x + w) and yy > y and yy <(y + h):
                           return sp, 'beforeText-%s'%i

                return sp, 'headline'

        return None, 'canvas'

    #@-node:ekr.20081004102201.593:hitTest
    #@+node:ekr.20081004102201.594:_createNewBuffer
    def _createNewBuffer(self):
        """Create a new buffer for drawing."""


        if not self.window:
            g.trace('no window !!!!!!!!!!!!!!!!')
            g.trace(g.callers())
            return


        x, y, w, h = self.allocation

        # guard against negative or zero values at start up
        w = max(w, 1)
        h = max(h, 1)

        #g.trace('request new buffe:',w, h)


        if self._buffer:
            bw, bh = self._buffer.get_size()

            # only create a new buffer if the old one is too small
            if bw >= w and bh >= h:
                return

            # create a bigger buffer than requested to reduce the
            # number of requests when the splitter is being dragged slowly

            w = w + 100
            h = h + 100

        #g.trace('grant new buffer:', w, h)
        self._buffer = gtk.gdk.Pixmap(self.window, w, h)





    #@-node:ekr.20081004102201.594:_createNewBuffer
    #@+node:ekr.20081004102201.595:vscrollTo

    def vscrollTo(self, pos):
        """Scroll the canvas vertically to the specified position."""

        canvasHeight = self.get_allocation().height
        if (self._treeHeight - canvasHeight) < pos :
            pos = self._treeHeight - canvasHeight

        pos = max(0, pos)

        self._virtualTop = pos

        self.redraw()
    #@-node:ekr.20081004102201.595:vscrollTo
    #@+node:ekr.20081004102201.596:hscrollTo
    def hscrollTo(self, pos):
        """Scroll the canvas vertically to the specified position."""

        canvasWidth = self.get_allocation().width

        #g.trace(pos)

        if (self._treeWidth - canvasWidth) < pos :
            pos = min(0, self._treeWidth - canvasWidth)

        pos = max( 0, pos)

        self._virtualLeft = pos

        self.redraw()
    #@-node:ekr.20081004102201.596:hscrollTo
    #@+node:ekr.20081004102201.597:resize

    def resize(self):
        """Resize the outline canvas and, if required, create and draw on a new buffer."""

        c = self.c

        self._createNewBuffer()
        #self._parent.hscrollUpdate()
        self.draw()
        self.refresh()

        return True





    #@-node:ekr.20081004102201.597:resize
    #@+node:ekr.20081004102201.598:redraw
    def redraw(self):
        self.draw()
        self.refresh()
    #@-node:ekr.20081004102201.598:redraw
    #@+node:ekr.20081004102201.599:update

    def update(self):
        """Do a full update assuming the tree has been changed."""

        c = self.c

        canvasHeight = self.get_allocation().height

        hoistFlag = bool(self.c.hoistStack)

        if hoistFlag:
            stk = [self.c.hoistStack[-1].p]
        else:
            stk = [self.c.rootPosition()]

        #@    << find height of tree and position of currentNode >>
        #@+node:ekr.20081004102201.600:<< find height of tree and position of currentNode >>

        # Find the number of visible nodes in the outline.

        cp = c.currentPosition().copy()
        cpCount = None

        count = 0
        while stk:

            p = stk.pop()

            while p:


                if stk or not hoistFlag:
                    newp = p.next()
                else:
                    newp = None

                if cp and cp == p:
                    cpCount = count
                    cp = False

                count += 1

                #@        << if p.isExpanded() and p.hasFirstChild():>>
                #@+node:ekr.20081004102201.601:<< if p.isExpanded() and p.hasFirstChild():>>
                v=p.v
                if v.statusBits & v.expandedBit and v.hasChildren():
                #@nonl
                #@-node:ekr.20081004102201.601:<< if p.isExpanded() and p.hasFirstChild():>>
                #@nl
                    stk.append(newp)
                    p = p.firstChild()
                    continue

                p = newp

        lineHeight = self._lineHeight

        self._treeHeight = count * lineHeight

        self._parent.set_property('canvas-height', self._treeHeight)


        if cpCount is not None:
            cpTop = cpCount * lineHeight

            if cpTop < self._virtualTop:
                self._virtualTop = cpTop

            elif cpTop + lineHeight > self._virtualTop + canvasHeight:
                self._virtualTop += (cpTop + lineHeight) - (self._virtualTop + canvasHeight)



        #@-node:ekr.20081004102201.600:<< find height of tree and position of currentNode >>
        #@nl

        if (self._treeHeight - self._virtualTop) < canvasHeight:
            self._virtualTop = self._treeHeight - canvasHeight

        # if (self._treeHeight - self._virtualTop) < canvasHeight:
            # self._virtualTop = self._treeHeight - canvasHeight

        self.contextChanged()

        self.redraw()
        self._parent.vscrollUpdate()
        self._parent.hscrollUpdate()


    #@-node:ekr.20081004102201.599:update
    #@+node:ekr.20081004102201.602:onPaint

    def onPaint(self, *args):
        """Renders the off-screen buffer to the outline canvas."""



        if not self._buffer:
            return

        # w, h are needed because the buffer may be bigger than the window.
        w, h = self.window.get_size()

        #g.trace('size', w, h)

        # We use self.style.black_gc only because we need a gc, it has no relavence.

        self.window.draw_drawable(self.style.black_gc ,self._buffer, 0, 0, 0, 0, w, h)
    #@-node:ekr.20081004102201.602:onPaint
    #@+node:ekr.20081004102201.603:onMap
    def onMap(self, *args):
        self._createNewBuffer()
        self.update()
        self.connect('expose-event', self.onPaint)
        self.connect("size-allocate", self.onSize)
    #@-node:ekr.20081004102201.603:onMap
    #@+node:ekr.20081004102201.604:onSize
    def onSize(self, *args):
        """React to changes in the size of the outlines display area."""

        c = self.c

        self.resize()
        self._parent.vscrollUpdate()
        self._parent.hscrollUpdate()


    #@-node:ekr.20081004102201.604:onSize
    #@+node:ekr.20081004102201.605:refresh

    #def refresh(self):
        # """Renders the offscreen buffer to the outline canvas."""
        # return

        # #g.pr('refresh')
        # wx.ClientDC(self).BlitPointSize((0,0), self._size, self._buffer, (0, 0))

    refresh = onPaint
    #@nonl
    #@-node:ekr.20081004102201.605:refresh
    #@+node:ekr.20081004102201.606:contextChanged
    def contextChanged(self):
        """Adjust canvas attributes after a change in context.

        This should be called after setting or changing fonts or icon size or
        anything that effects the tree display.

        """

        self._pangoLayout.set_text('Wy')
        self._fontHeight = self._pangoLayout.get_pixel_size()[1]
        self._iconSize = (20, 11) #(icons[0].GetWidth(), icons[0].GetHeight())

        self._clickBoxSize = (9, 9) #(plusBoxIcon.GetWidth(), plusBoxIcon.GetHeight())

        self._lineHeight = max(
            self._fontHeight,
            self._iconSize[1],
            self._requestedLineHeight
        ) + 2 * self._yPad

        # y offsets

        self._yTextOffset = (self._lineHeight - self._fontHeight)//2

        self._yIconOffset = (self._lineHeight - self._iconSize[1])//2

        self._clickBoxCenterOffset = (
            -self._textIndent*2 + self._iconSize[0]//2,
            self._lineHeight//2
        )

        self._clickBoxOffset = (
            self._clickBoxCenterOffset[0] - self._clickBoxSize[0]//2,
            (self._lineHeight  - self._clickBoxSize[1])//2
        )


    #@-node:ekr.20081004102201.606:contextChanged
    #@+node:ekr.20081004102201.607:requestLineHeight
    def requestLineHeight(height):
        """Request a minimum height for lines."""

        assert int(height) and height < 200
        self.requestedHeight = height
        self.beginUpdate()
        self.endUpdate()
    #@-node:ekr.20081004102201.607:requestLineHeight
    #@+node:ekr.20081004102201.608:def draw

    def draw(self, *args):
        """Draw the outline on the off-screen buffer.

        This method needs to be as fast as possible.

        A lot of the original need for speed has gone now we
        are drawing off screen but it's still important to be fast.

        """
        c = self.c

        # Its not an error to have no buffer
        if self._buffer is None:
            g.trace('no buffer yet')
            return

        #@    << setup local variables >>
        #@+node:ekr.20081004102201.609:<< setup local variables >>
        # these are set to improve efficiancey


        outlineBackgroundCairoColor = leoColor.getCairo('leo yellow')
        selectedBackgroundCairoColor = leoColor.getCairo('grey90')
        headlineTextCairoColor = leoColor.getCairo('black')

        canvasWidth, canvasHeight = self.window.get_size()


        pangoLayout = self._pangoLayout


        top = self._virtualTop
        if top < 0:
            self._virtualTop = top = 0

        left = self._virtualLeft
        if left < 0:
            self._virtualLeft = left = 0   


        bottom = top + canvasHeight


        textIndent = self._textIndent
        treeWidth = self._treeWidth

        yPad = self._yPad
        xPad = self._xPad - left

        yIconOffset = self._yIconOffset

        yTextOffset = self._yTextOffset

        clickBoxOffset_x, clickBoxOffset_y = self._clickBoxOffset

        clickBoxCenterOffset_x, clickBoxCenterOffset_y = \
            self._clickBoxCenterOffset

        clickBoxSize_w, clickBoxSize_h = self._clickBoxSize

        iconSize_w, iconSize_h = self._iconSize

        lineHeight = self._lineHeight
        halfLineHeight = lineHeight//2


        # images
        gui = g.app.gui

        icons = gui.treeIcons
        globalImages = gui.globalImages
        plusBoxIcon = gui.plusBoxIcon
        minusBoxIcon = gui.minusBoxIcon

        currentPosition = c.currentPosition()

        #@-node:ekr.20081004102201.609:<< setup local variables >>
        #@nl

        cr = self._buffer.cairo_create()


        cr.rectangle(0, 0, canvasWidth, canvasHeight)
        cr.clip()


        #@    << draw background >>
        #@+node:ekr.20081004102201.610:<< draw background >>
        cr.set_source_rgb(*outlineBackgroundCairoColor)
        cr.rectangle(0, 0, canvasWidth, canvasHeight)
        cr.fill()
        #@-node:ekr.20081004102201.610:<< draw background >>
        #@nl

        #@    << draw tree >>
        #@+node:ekr.20081004102201.611:<< draw tree >>
        y = 0

        hoistFlag = bool(c.hoistStack)

        if hoistFlag:
            stk = [c.hoistStack[-1].p]
        else:
            stk = [c.rootPosition()]

        self._positions = positions = []

        #@+at
        # My original reason for writing the loop this way was to make it as 
        # fast as
        # possible. Perhaps I was being a bit too paranoid and we should 
        # change back to
        # more conventional iterations, on the other hand if it ain't broke 
        # don't fix it.
        #@-at
        #@@c


        while stk:

            p = stk.pop()

            while p:

                if stk or not hoistFlag:
                    newp = p.next()
                else:
                    newp = None

                mytop = y
                y = y + lineHeight

                if mytop > bottom:
                    # no need to draw any more
                    stk = []
                    p = None
                    break

                if y > top:

                    #this position is visible

                    sp = p.copy()

                    #@            << setup object >>
                    #@+node:ekr.20081004102201.612:<< set up object >>
                    # depth: the depth of indentation relative to the current hoist.
                    sp._depth = len(stk)


                    # _virtualTop: top of this line in virtual canvas coordinates
                    sp._virtualTop =  mytop

                    # _top: top of this line in real canvas coordinates
                    sp._top = mytop - top

                    # ??? maybe give each position it own pangoLayout?
                    pangoLayout.set_text(sp.headString())

                    textSize_w, textSize_h = pangoLayout.get_pixel_size()


                    # this should be _virtualLeft
                    xTextOffset = ((sp._depth +1) * textIndent) + xPad

                    textPos_x = xTextOffset
                    textPos_y =  sp._top + yTextOffset

                    iconPos_x = textPos_x - textIndent
                    iconPos_y = textPos_y + yIconOffset

                    clickBoxPos_x = textPos_x + clickBoxOffset_x
                    clickBoxPos_y = textPos_y + clickBoxOffset_y

                    sp._clickBoxCenter_x = clickBoxPos_x + clickBoxCenterOffset_x
                    sp._clickBoxCenter_y = clickBoxPos_y + clickBoxCenterOffset_y

                    sp._textBoxRect = [textPos_x, textPos_y, textSize_w, textSize_h]
                    sp._iconBoxRect = [iconPos_x, iconPos_y, iconSize_w, iconSize_h]
                    sp._clickBoxRect = [clickBoxPos_x, clickBoxPos_y, clickBoxSize_w, clickBoxSize_h]

                    sp._icon = icons[p.v.computeIcon()]


                    if sp.hasFirstChild():
                        sp._clickBoxIcon = plusBoxIcon
                        if sp.isExpanded():
                            sp._clickBoxIcon = minusBoxIcon
                    else:
                        sp._clickBoxIcon = None


                    if sp == currentPosition:
                        sp._current = True
                        #@    << set self._currentHighlightRect >>
                        #@+node:ekr.20081004102201.613:<< set self._currentHighlightRect >>
                        tx, ty, tw, th = sp._textBoxRect

                        sp._currentHighlightRect = [tx, ty-2, tw+6, th+4]
                        sp._textBoxRect[0] += 3
                        #@nonl
                        #@-node:ekr.20081004102201.613:<< set self._currentHighlightRect >>
                        #@nl
                    else:
                        sp._current = False
                    #@-node:ekr.20081004102201.612:<< set up object >>
                    #@nl

                    positions.append(sp)

                    treeWidth = max(
                        treeWidth,
                        textSize_w + xTextOffset + left
                    )

                #@        << if p.isExpanded() and p.hasFirstChild():>>
                #@+node:ekr.20081004102201.601:<< if p.isExpanded() and p.hasFirstChild():>>
                v=p.v
                if v.statusBits & v.expandedBit and v.hasChildren():
                #@nonl
                #@-node:ekr.20081004102201.601:<< if p.isExpanded() and p.hasFirstChild():>>
                #@nl
                    stk.append(newp)
                    p = p.firstChild()
                    continue

                p = newp

        if treeWidth > self._treeWidth:
            # theoretically this could be recursive ???
            # but its unlikely ...
            self._treeWidth = treeWidth
            self._parent.hscrollUpdate()

        if not positions:
            #g.trace('No positions!')
            return

        self._virtualTop =  positions[0]._virtualTop


        # try:
            # result = self._leoTree.drawTreeHook(self)
            # g.pr('result =', result)
        # except:
            # result = False
            # g.pr('result is False')

        # if hasattr(self._leoTree, 'drawTreeHook'):
            # try:
                # result = self._leoTree.drawTreeHook(self)
            # except:
                # result = False
        # else:
            # #g.pr('drawTreeHook not known')
            # result = None

        # if not result:

        #@<< draw headline icons and text >>
        #@+node:ekr.20081004102201.614:<< draw headline icons and text >>

        cr.update_layout(pangoLayout)

        for sp in positions:

            if 0: 
                #@        << draw before text icons >>
                #@+node:ekr.20081004102201.615:<< draw before text icons >>

                try:
                    headStringIcons = sp.v.t.unknownAttributes.get('icons', [])
                except:
                    headStringIcons = None

                sp._headStringIcons = hsi = []

                if headStringIcons:

                    x, y, w, h = sp._textBoxRect

                    for headStringIcon in headStringIcons:
                        try:
                            path = headStringIcon['relPath']

                            try:
                                image = globalImages[path]
                            except KeyError:
                                image = getImage(path)

                        except KeyError:
                            image = None

                        if image:

                            hsi.append((x, y, image.get_width(), image.get_height()))       

                            cr.set_source_pixbuf(image, x, y)
                            cr.paint()

                            x = x + image.get_width() + 5

                    # shift position of text and hightlight box to accomodate icons 
                    sp._currentPositionHighlightRect[0] = x - 3
                    sp._textBoxRect[0] = x
                #@-node:ekr.20081004102201.615:<< draw before text icons >>
                #@nl

            pangoLayout.set_text(sp.headString())

            if sp._current:

                cr.set_source_rgb(*selectedBackgroundCairoColor)
                cr.rectangle(*sp._currentHighlightRect)
                cr.fill()

            cr.set_source_rgb(*headlineTextCairoColor)
            x, y, w, h = sp._textBoxRect 

            #g.trace(x, y, w, h, sp.headString())

            cr.move_to(x, y)
            cr.show_layout(pangoLayout)

            #< < draw after text icons >>


        #@-node:ekr.20081004102201.614:<< draw headline icons and text >>
        #@nl
        #@<< draw lines >>
        #@+node:ekr.20081004102201.616:<< draw lines >>
        #@-node:ekr.20081004102201.616:<< draw lines >>
        #@nl
        #@<< draw bitmaps >>
        #@+node:ekr.20081004102201.617:<< draw bitmaps >>

        for sp in positions:

            x, y, w, h = sp._iconBoxRect

            cr.set_source_pixbuf(sp._icon,x,y)
            cr.paint()
            #cr.stroke()

            if sp._clickBoxIcon:
                x, y, w, h = sp._clickBoxRect
                cr.set_source_pixbuf(sp._clickBoxIcon, x, y)
                cr.paint()
        #@-node:ekr.20081004102201.617:<< draw bitmaps >>
        #@nl

        #@<< draw focus >>
        #@+node:ekr.20081004102201.618:<< draw focus >>
        if 0:
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            if self._leoTree.hasFocus():
                dc.SetPen(wx.BLACK_PEN)
            #else:
            #    dc.SetPen(wx.GREEN_PEN)
                dc.DrawRectanglePointSize( (0,0), self.GetSize())
        #@nonl
        #@-node:ekr.20081004102201.618:<< draw focus >>
        #@nl




        #@-node:ekr.20081004102201.611:<< draw tree >>
        #@nl

        #self._parent.showEntry()

        return True






    #@-node:ekr.20081004102201.608:def draw
    #@-others
#@-node:ekr.20081004102201.589:class OutlineCanvas
#@-node:ekr.20081004102201.569:== Outline Canvas Widget ==
#@-node:ekr.20081004102201.446:gtkTree
#@-others
#@-node:ekr.20080112150934:@thin experimental/gtkGui.py
#@-leo

# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20070215164948:@thin ironPythonGui.py
#@@first

"""A plugin to use IronPython and .Net Forms as Leo's gui."""

__version__ = '0.6'

# print 'IronPythonGui 1'

#@<< version history >>
#@+node:ekr.20070215164948.1:<< version history >>
#@@nocolor
#@+at
# - Work begins: February 15, 2007
#@-at
#@nonl
#@-node:ekr.20070215164948.1:<< version history >>
#@nl
#@<< imports >>
#@+node:ekr.20070215164948.2:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import sys
import System

import leo.core.leoGui as leoGui

# import Sytem.Windows.Forms

# sys.LoadAssemblyByName("System.Windows.Forms")
#@nonl
#@-node:ekr.20070215164948.2:<< imports >>
#@nl

# print 'IronPythonGui 2'

#@+others
#@+node:ekr.20070215164948.3:Module level
#@+node:ekr.20070215164948.4:init
def init ():

    ok = (
        not g.app.unitTesting
        and System is not None
        # and System.Windows.Forms is not None
    )

    print 'ironPythonGui: init ok:', ok

    if ok:
        g.app.gui = ironPythonGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)

    return ok
#@nonl
#@-node:ekr.20070215164948.4:init
#@-node:ekr.20070215164948.3:Module level
#@+node:ekr.20070215164948.5:ironPythonGui class
class ironPythonGui(leoGui.leoGui):

    #@    @+others
    #@+node:ekr.20070215164948.7:gui birth & death
    #@+node:ekr.20070215164948.8: ipGui.__init__
    def __init__ (self):

        # g.trace("ironPytonGui")

        # Initialize the base class.
        leoGui.leoGui.__init__(self,"IronPython")

        # self.bitmap_name = None
        # self.bitmap = None
        # self.focus_widget = None

        # self.plainTextWidget = plainTextWidget

        # self.use_stc = True # Unit tests fail regardless of this setting.
        # self.bodyTextWidget = g.choose(self.use_stc,stcWidget,richTextWidget)
        # self.plainTextWidget = plainTextWidget

        # self.findTabHandler = None
        # self.spellTabHandler = None
    #@-node:ekr.20070215164948.8: ipGui.__init__
    #@+node:ekr.20070215164948.9:ip.Gui.createKeyHandlerClass
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        return wxKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@nonl
    #@-node:ekr.20070215164948.9:ip.Gui.createKeyHandlerClass
    #@+node:ekr.20070215164948.10:ip.createRootWindow
    def createRootWindow(self):

        self.root = f = System.Windows.Forms.Form()

        def click(*args): print args
        f.Click += click

        if 0: # Not ready yet.
            self.getDefaultConfigFont(g.app.config)
            self.setEncoding()

        return f
    #@nonl
    #@-node:ekr.20070215164948.10:ip.createRootWindow
    #@+node:ekr.20070215164948.11:createLeoFrame
    def createLeoFrame(self,title):

        """Create a new Leo frame."""

        return None # ironPythonLeoFrame(title)
    #@nonl
    #@-node:ekr.20070215164948.11:createLeoFrame
    #@+node:ekr.20070215164948.12:destroySelf
    def destroySelf(self):

        pass # Nothing more needs to be done once all windows have been destroyed.
    #@nonl
    #@-node:ekr.20070215164948.12:destroySelf
    #@+node:ekr.20070215164948.13:finishCreate
    def finishCreate (self):

       pass # g.trace('ironPython gui')
    #@-node:ekr.20070215164948.13:finishCreate
    #@+node:ekr.20070215164948.14:killGui
    def killGui(self,exitFlag=True):

        """Destroy a gui and terminate Leo if exitFlag is True."""

        pass # Not ready yet.

    #@-node:ekr.20070215164948.14:killGui
    #@+node:ekr.20070215164948.15:recreateRootWindow
    def recreateRootWindow(self):

        """A do-nothing base class to create the hidden root window of a gui

        after a previous gui has terminated with killGui(False)."""

        pass
    #@-node:ekr.20070215164948.15:recreateRootWindow
    #@+node:ekr.20070215164948.16:runMainLoop
    def runMainLoop(self):

        '''Run IronPython's main loop.'''

        System.Windows.Forms.Application.Run(g.app.root)
    #@-node:ekr.20070215164948.16:runMainLoop
    #@-node:ekr.20070215164948.7:gui birth & death
    #@+node:ekr.20070215164948.17:gui dialogs
    #@+node:ekr.20070215164948.18:runAboutLeoDialog
    def runAboutLeoDialog(self,c,version,copyright,url,email):

        """Create and run a wxPython About Leo dialog."""

        if  g.app.unitTesting: return

        message = "%s\n\n%s\n\n%s\n\n%s" % (
            version.strip(),copyright.strip(),url.strip(),email.strip())

        wx.MessageBox(message,"About Leo",wx.Center,self.root)
    #@nonl
    #@-node:ekr.20070215164948.18:runAboutLeoDialog
    #@+node:ekr.20070215164948.19:runAskOkDialog
    def runAskOkDialog(self,c,title,message=None,text="Ok"):

        """Create and run a wxPython askOK dialog ."""

        if  g.app.unitTesting: return 'ok'

        d = wx.MessageDialog(self.root,message,"Leo",wx.OK)
        d.ShowModal()
        return "ok"
    #@nonl
    #@-node:ekr.20070215164948.19:runAskOkDialog
    #@+node:ekr.20070215164948.20:runAskLeoIDDialog
    def runAskLeoIDDialog(self):

        """Create and run a dialog to get g.app.LeoID."""

        if  g.app.unitTesting: return 'ekr'

        # to do
    #@nonl
    #@-node:ekr.20070215164948.20:runAskLeoIDDialog
    #@+node:ekr.20070215164948.21:runAskOkCancelNumberDialog (to do)
    def runAskOkCancelNumberDialog(self,c,title,message):

        """Create and run a wxPython askOkCancelNumber dialog ."""

        if g.app.unitTesting: return 666

        # to do.
    #@nonl
    #@-node:ekr.20070215164948.21:runAskOkCancelNumberDialog (to do)
    #@+node:ekr.20070215164948.22:runAskOkCancelStringDialog (to do)
    def runAskOkCancelStringDialog(self,c,title,message):

        """Create and run a wxPython askOkCancelNumber dialog ."""

        if  g.app.unitTesting: return 'xyzzy'

        # to do
    #@-node:ekr.20070215164948.22:runAskOkCancelStringDialog (to do)
    #@+node:ekr.20070215164948.23:runAskYesNoDialog
    def runAskYesNoDialog(self,c,title,message=None):

        """Create and run a wxPython askYesNo dialog."""

        if  g.app.unitTesting: return 'yes'

        d = wx.MessageDialog(self.root,message,"Leo",wx.YES_NO)
        answer = d.ShowModal()

        return g.choose(answer==wx.YES,"yes","no")
    #@nonl
    #@-node:ekr.20070215164948.23:runAskYesNoDialog
    #@+node:ekr.20070215164948.24:runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):

        """Create and run a wxPython askYesNoCancel dialog ."""

        if  g.app.unitTesting: return 'yes'

        d = wx.MessageDialog(self.root,message,"Leo",wx.YES_NO | wx.CANCEL)
        answer = d.ShowModal()

        if answer == wx.ID_YES:
            return "yes"
        elif answer == wx.ID_NO:
            return "no"
        else:
            assert(answer == wx.ID_CANCEL)
            return "cancel"
    #@nonl
    #@-node:ekr.20070215164948.24:runAskYesNoCancelDialog
    #@+node:ekr.20070215164948.25:runCompareDialog
    def runCompareDialog (self,c):

        if  g.app.unitTesting: return

        # To do
    #@nonl
    #@-node:ekr.20070215164948.25:runCompareDialog
    #@+node:ekr.20070215164948.26:runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension):

        """Create and run a wxPython open file dialog ."""

        if  g.app.unitTesting: return None

        wildcard = self.getWildcardList(filetypes)

        d = wx.FileDialog(
            parent=None, message=title,
            defaultDir="", defaultFile="",
            wildcard=wildcard,
            style= wx.OPEN | wx.CHANGE_DIR | wx.HIDE_READONLY)

        val = d.ShowModal()
        if val == wx.ID_OK:
            file = d.GetFilename()
            return file
        else:
            return None 
    #@-node:ekr.20070215164948.26:runOpenFileDialog
    #@+node:ekr.20070215164948.27:runSaveFileDialog
    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run a wxPython save file dialog ."""

        if  g.app.unitTesting: return None

        wildcard = self.getWildcardList(filetypes)

        d = wx.FileDialog(
            parent=None, message=title,
            defaultDir="", defaultFile="",
            wildcard=wildcard,
            style= wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)

        val = d.ShowModal()
        if val == wx.ID_OK:
            file = d.GetFilename()
            return file
        else:
            return None
    #@nonl
    #@-node:ekr.20070215164948.27:runSaveFileDialog
    #@+node:ekr.20070215164948.28:simulateDialog
    def simulateDialog (self,key,defaultVal=None):

        return defaultVal
    #@nonl
    #@-node:ekr.20070215164948.28:simulateDialog
    #@+node:ekr.20070215164948.29:getWildcardList
    def getWildcardList (self,filetypes):

        """Create a wxWindows wildcard string for open/save dialogs."""

        if not filetypes:
            return "*.leo"

        if 1: # Too bad: this is sooo wimpy.
                a,b = filetypes[0] 
                return b

        else: # This _sometimes_ works: wxWindows is driving me crazy!

            # wildcards = ["%s (%s)" % (a,b) for a,b in filetypes]
            wildcards = ["%s" % (b) for a,b in filetypes]
            wildcard = "|".join(wildcards)
            g.trace(wildcard)
            return wildcard
    #@nonl
    #@-node:ekr.20070215164948.29:getWildcardList
    #@-node:ekr.20070215164948.17:gui dialogs
    #@+node:ekr.20070215164948.30:gui events
    def event_generate(self,w,kind,*args,**keys):
        '''Generate an event.'''
        return w.event_generate(kind,*args,**keys)
    #@+node:ekr.20070215164948.31:class leoKeyEvent (wxGui)
    class leoKeyEvent:

        '''A gui-independent wrapper for gui events.'''

        def __init__ (self,event,c):
            gui = g.app.gui
            self.c              = c
            self.actualEvent    = event
            self.char           = gui.eventChar(event)
            self.keysym         = gui.eventKeysym(event)
            self.widget         = gui.eventWidget(event)
            self.x,self.y       = gui.eventXY(event)

            self.w = self.widget
    #@-node:ekr.20070215164948.31:class leoKeyEvent (wxGui)
    #@+node:ekr.20070215164948.32:wxKeyDict
    wxKeyDict = {
        # Keys are wxWidgets key codes.  Values are the standard (Tk) names.
        wx.WXK_DECIMAL  : '.',
        wx.WXK_BACK     : '\b', # 'BackSpace',
        wx.WXK_TAB      : '\t', # 'Tab',
        wx.WXK_RETURN   : '\n', # 'Return',
        wx.WXK_ESCAPE   : 'Escape',
        wx.WXK_SPACE    : ' ',
        wx.WXK_DELETE   : 'Delete',
        wx.WXK_LEFT     : 'Left',
        wx.WXK_UP       : 'Up',
        wx.WXK_RIGHT    : 'Right',
        wx.WXK_DOWN     : 'Down',
        wx.WXK_F1       : 'F1',
        wx.WXK_F2       : 'F2',
        wx.WXK_F3       : 'F3',
        wx.WXK_F4       : 'F4',
        wx.WXK_F5       : 'F5',
        wx.WXK_F6       : 'F6',
        wx.WXK_F7       : 'F7',
        wx.WXK_F8       : 'F8',
        wx.WXK_F9       : 'F9',
        wx.WXK_F10      : 'F10',
        wx.WXK_F11      : 'F11',
        wx.WXK_F12      : 'F12',
        wx.WXK_END                  : 'End',
        wx.WXK_HOME                 : 'Home',
        wx.WXK_PAGEUP               : 'Prior',
        wx.WXK_PAGEDOWN             : 'Next',
        wx.WXK_NUMPAD_DELETE        : 'Delete',
        wx.WXK_NUMPAD_SPACE         : ' ',
        wx.WXK_NUMPAD_TAB           : '\t', # 'Tab',
        wx.WXK_NUMPAD_ENTER         : '\n', # 'Return',
        wx.WXK_NUMPAD_PAGEUP        : 'Prior',
        wx.WXK_NUMPAD_PAGEDOWN      : 'Next',
        wx.WXK_NUMPAD_END           : 'End',
        wx.WXK_NUMPAD_BEGIN         : 'Home',
    }

    #@+at 
    #@nonl
    # These are by design not compatible with unicode characters.
    # If you want to get a unicode character from a key event use
    # wxKeyEvent::GetUnicodeKey instead.
    # 
    # WXK_START   = 300
    # WXK_LBUTTON
    # WXK_RBUTTON
    # WXK_CANCEL
    # WXK_MBUTTON
    # WXK_CLEAR
    # WXK_SHIFT
    # WXK_ALT
    # WXK_CONTROL
    # WXK_MENU
    # WXK_PAUSE
    # WXK_CAPITAL
    # WXK_SELECT
    # WXK_PRINT
    # WXK_EXECUTE
    # WXK_SNAPSHOT
    # WXK_INSERT
    # WXK_HELP
    # WXK_NUMPAD0
    # WXK_NUMPAD1
    # WXK_NUMPAD2
    # WXK_NUMPAD3
    # WXK_NUMPAD4
    # WXK_NUMPAD5
    # WXK_NUMPAD6
    # WXK_NUMPAD7
    # WXK_NUMPAD8
    # WXK_NUMPAD9
    # WXK_MULTIPLY
    # WXK_ADD
    # WXK_SEPARATOR
    # WXK_SUBTRACT
    # WXK_DECIMAL
    # WXK_DIVIDE
    # WXK_F13
    # WXK_F14
    # WXK_F15
    # WXK_F16
    # WXK_F17
    # WXK_F18
    # WXK_F19
    # WXK_F20
    # WXK_F21
    # WXK_F22
    # WXK_F23
    # WXK_F24
    # WXK_NUMLOCK
    # WXK_SCROLL
    # WXK_NUMPAD_F1,
    # WXK_NUMPAD_F2,
    # WXK_NUMPAD_F3,
    # WXK_NUMPAD_F4,
    # WXK_NUMPAD_HOME,
    # WXK_NUMPAD_LEFT,
    # WXK_NUMPAD_UP,
    # WXK_NUMPAD_RIGHT,
    # WXK_NUMPAD_DOWN,
    # WXK_NUMPAD_INSERT,
    # WXK_NUMPAD_EQUAL,
    # WXK_NUMPAD_MULTIPLY,
    # WXK_NUMPAD_ADD,
    # WXK_NUMPAD_SEPARATOR,
    # WXK_NUMPAD_SUBTRACT,
    # WXK_NUMPAD_DECIMAL,
    # WXK_NUMPAD_DIVIDE,
    # 
    # // the following key codes are only generated under Windows currently
    # WXK_WINDOWS_LEFT,
    # WXK_WINDOWS_RIGHT,
    # WXK_WINDOWS_MENU,
    # WXK_COMMAND,
    # 
    # // Hardware-specific buttons
    # WXK_SPECIAL1 = 193,
    # WXK_SPECIAL2,
    # WXK_SPECIAL3,
    # WXK_SPECIAL4,
    # WXK_SPECIAL5,
    # WXK_SPECIAL6,
    # WXK_SPECIAL7,
    # WXK_SPECIAL8,
    # WXK_SPECIAL9,
    # WXK_SPECIAL10,
    # WXK_SPECIAL11,
    # WXK_SPECIAL12,
    # WXK_SPECIAL13,
    # WXK_SPECIAL14,
    # WXK_SPECIAL15,
    # WXK_SPECIAL16,
    # WXK_SPECIAL17,
    # WXK_SPECIAL18,
    # WXK_SPECIAL19,
    # WXK_SPECIAL20
    #@-at
    #@nonl
    #@-node:ekr.20070215164948.32:wxKeyDict
    #@+node:ekr.20070215164948.33:eventChar & eventKeysym & helper
    def eventChar (self,event):

        '''Return the char field of an event, either a wx event or a converted Leo event.'''

        if hasattr(event,'char'):
            return event.char # A leoKeyEvent.
        else:
            return self.keysymHelper(event,kind='char')

    def eventKeysym (self,event):

        if hasattr(event,'keysym'):
            return event.keysym # A leoKeyEvent: we have already computed the result.
        else:
            return self.keysymHelper(event,kind='keysym')
    #@+node:ekr.20070215164948.34:keysymHelper
    def keysymHelper (self,event,kind):

        gui = self

        keycode = event.GetKeyCode()

        # g.trace(repr(keycode),kind)

        if keycode in (wx.WXK_SHIFT,wx.WXK_ALT,wx.WXK_CONTROL):
            return ''

        keysym = gui.wxKeyDict.get(keycode) or ''
        keyDownModifiers = hasattr(event,'keyDownModifiers') and event.keyDownModifiers or None
        alt = event.AltDown()     or keyDownModifiers == wx.MOD_ALT
        cmd = event.CmdDown()     or keyDownModifiers == wx.MOD_CMD
        ctrl = event.ControlDown()or keyDownModifiers == wx.MOD_CONTROL
        meta = event.MetaDown()   or keyDownModifiers == wx.MOD_META
        shift = event.ShiftDown() or keyDownModifiers == wx.MOD_SHIFT

        # Set the char field.
        char = keysym or ''
        if not char:
            # Avoid GetUnicodeKey if possible.  It crashes on '.' (!)
            try:
                char = chr(keycode)
            except ValueError:
                char = ''
        if not char and hasattr(event,'GetUnicodeKey'):
            i = event.GetUnicodeKey()
            if i is None: char = ''
            else:
                try:
                    char = unichr(i)
                except Exception:
                    g.es('No translation for', repr(i))
                    char = repr(i)

        # Adjust the case, but only for plain ascii characters characters.
        if len(char) == 1:
            if char.isalpha():
                if shift: # Case is also important for ctrl keys. # or alt or cmd or ctrl or meta:
                    char = char.upper()
                else:
                    char = char.lower()
            elif shift:
                char = self.getShiftChar(char)
            else:
                char = self.getUnshiftChar(char)

        # Create a value compatible with Leo's core.
        val = (
            g.choose(alt,'Alt+','') +
            # g.choose(cmd,'Cmd+','') +
            g.choose(ctrl,'Ctrl+','') +
            g.choose(meta,'Meta+','') +
            g.choose((alt or cmd or ctrl or meta) and shift,'Shift+','') +
            (char or '')
        )

        # if kind == 'char':  g.trace(repr(keycode),repr(val)) # Tracing just val can crash!
        return val
    #@-node:ekr.20070215164948.34:keysymHelper
    #@+node:ekr.20070215164948.35:getShiftChar
    def getShiftChar (self,char):

        d = {
            '1': '!',
            '2': '@',
            '3': '#',
            '4': '$',
            '5': '%',
            '6': '^',
            '7': '&',
            '8': '*',
            '9': '(',
            '0': ')',
            '-': '_',
            '=': '+',
            '[': '{',
            ']': '}',
            '\\': '|',
            ';': ':',
            "'": '"',
            ',': '<',
            '.': '>',
            '/': '?',
        }
        return d.get(char,char) # There must be a better way.
    #@nonl
    #@-node:ekr.20070215164948.35:getShiftChar
    #@+node:ekr.20070215164948.36:getUnshiftChar
    def getUnshiftChar (self,char):

        d = {
            '+': '='
        }
        return d.get(char,char)
    #@nonl
    #@-node:ekr.20070215164948.36:getUnshiftChar
    #@-node:ekr.20070215164948.33:eventChar & eventKeysym & helper
    #@+node:ekr.20070215164948.37:eventWidget
    def eventWidget (self,event):

        '''Return the widget field of an event.
        The event may be a wx event a converted Leo event or a manufactured event (a g.Bunch).'''

        if isinstance(event,self.leoKeyEvent): # a leoKeyEvent.
            return event.widget 
        elif isinstance(event,g.Bunch): # A manufactured event.
            if hasattr(event,'c'):
                return event.c.frame.body.bodyCtrl
            else:
                g.trace('k.generalModeHandler event')
                return None
        elif hasattr(event,'GetEventObject'): # A wx Event.
            return event.GetEventObject()
        else:
            g.trace('no event widget',event)
            return None
    #@-node:ekr.20070215164948.37:eventWidget
    #@+node:ekr.20070215164948.38:eventXY
    def eventXY (self,event,c=None):

        if hasattr(event,'x') and hasattr(event,'y'):
            return event.x,event.y
        if hasattr(event,'GetX') and hasattr(event,'GetY'):
            return event.GetX(),event.GetY()
        else:
            return 0,0
    #@-node:ekr.20070215164948.38:eventXY
    #@-node:ekr.20070215164948.30:gui events
    #@+node:ekr.20070215164948.39:gui panels (to do)
    #@+node:ekr.20070215164948.40:createColorPanel
    def createColorPanel(self,c):

        """Create Color panel."""

        g.trace("not ready yet")
    #@nonl
    #@-node:ekr.20070215164948.40:createColorPanel
    #@+node:ekr.20070215164948.41:createComparePanel
    def createComparePanel(self,c):

        """Create Compare panel."""

        g.trace("not ready yet")
    #@nonl
    #@-node:ekr.20070215164948.41:createComparePanel
    #@+node:ekr.20070215164948.42:createFindPanel
    def createFindPanel(self):

        """Create a hidden Find panel."""

        return wxFindFrame()
    #@nonl
    #@-node:ekr.20070215164948.42:createFindPanel
    #@+node:ekr.20070215164948.43:createFindTab
    def createFindTab (self,c,parentFrame):

        '''Create a wxWidgets find tab in the indicated frame.'''

        # g.trace(self.findTabHandler)

        if not self.findTabHandler:
            self.findTabHandler = wxFindTab(c,parentFrame)

        return self.findTabHandler
    #@-node:ekr.20070215164948.43:createFindTab
    #@+node:ekr.20070215164948.44:createFontPanel
    def createFontPanel(self,c):

        """Create a Font panel."""

        g.trace("not ready yet")
    #@nonl
    #@-node:ekr.20070215164948.44:createFontPanel
    #@+node:ekr.20070215164948.45:createSpellTab
    def createSpellTab (self,c,parentFrame):

        '''Create a wxWidgets spell tab in the indicated frame.'''

        if not self.spellTabHandler:
            self.spellTabHandler = wxSpellTab(c,parentFrame)

        return self.findTabHandler
    #@-node:ekr.20070215164948.45:createSpellTab
    #@+node:ekr.20070215164948.46:destroyLeoFrame (NOT USED)
    def destroyLeoFrame (self,frame):

        frame.Close()
    #@nonl
    #@-node:ekr.20070215164948.46:destroyLeoFrame (NOT USED)
    #@-node:ekr.20070215164948.39:gui panels (to do)
    #@+node:ekr.20070215164948.47:gui utils (must add several)
    #@+node:ekr.20070215164948.48:Clipboard
    def replaceClipboardWith (self,s):

        cb = wx.TheClipboard
        if cb.Open():
            cb.Clear()
            cb.SetData(wx.TextDataObject(s))
            cb.Close()

    def getTextFromClipboard (self):

        cb = wx.TheClipboard
        if cb.Open():
            data = wx.TextDataObject()
            ok = cb.GetData(data)
            cb.Close()
            return ok and data.GetText() or ''
        else:
            return ''
    #@-node:ekr.20070215164948.48:Clipboard
    #@+node:ekr.20070215164948.49:Constants
    # g.es calls gui.color to do the translation,
    # so most code in Leo's core can simply use Tk color names.

    def color (self,color):
        '''Return the gui-specific color corresponding to the Tk color name.'''
        return color # Do not call oops: this method is essential for the config classes.
    #@-node:ekr.20070215164948.49:Constants
    #@+node:ekr.20070215164948.50:Dialog
    #@+node:ekr.20070215164948.51:bringToFront
    def bringToFront (self,window):

        if window.IsIconized():
            window.Maximize()
        window.Raise()
        window.Show(True)
    #@nonl
    #@-node:ekr.20070215164948.51:bringToFront
    #@+node:ekr.20070215164948.52:get_window_info
    def get_window_info(self,window):

        # Get the information about top and the screen.
        x,y = window.GetPosition()
        w,h = window.GetSize()

        return w,h,x,y
    #@nonl
    #@-node:ekr.20070215164948.52:get_window_info
    #@+node:ekr.20070215164948.53:center_dialog
    def center_dialog(window):

        window.Center()
    #@nonl
    #@-node:ekr.20070215164948.53:center_dialog
    #@-node:ekr.20070215164948.50:Dialog
    #@+node:ekr.20070215164948.54:Focus
    #@+node:ekr.20070215164948.55:get_focus
    def get_focus(self,top):

        """Returns the widget that has focus, or body if None."""

        return self.focus_widget
    #@nonl
    #@-node:ekr.20070215164948.55:get_focus
    #@+node:ekr.20070215164948.56:set_focus
    def set_focus(self,c,w):

        """Set the focus of the widget in the given commander if it needs to be changed."""

        c.frame.setFocus(w)
    #@-node:ekr.20070215164948.56:set_focus
    #@-node:ekr.20070215164948.54:Focus
    #@+node:ekr.20070215164948.57:Font (wxGui) (to do)
    #@+node:ekr.20070215164948.58:getFontFromParams
    def getFontFromParams(self,family,size,slant,weight):

        ## g.trace(g.app.config.defaultFont)

        return g.app.config.defaultFont ##

        family_name = family

        try:
            font = tkFont.Font(family=family,size=size,slant=slant,weight=weight)
            #print family_name,family,size,slant,weight
            #print "actual_name:",font.cget("family")
            return font
        except:
            g.es("exception setting font from " + `family_name`)
            g.es("family,size,slant,weight:"+
                `family`+':'+`size`+':'+`slant`+':'+`weight`)
            g.es_exception()
            return g.app.config.defaultFont
    #@nonl
    #@-node:ekr.20070215164948.58:getFontFromParams
    #@-node:ekr.20070215164948.57:Font (wxGui) (to do)
    #@+node:ekr.20070215164948.59:Icons (wxGui) (to do)
    #@+node:ekr.20070215164948.60:attachLeoIcon
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
                #@            << try to use the PIL and tkIcon packages to draw the icon >>
                #@+node:ekr.20070215164948.61:<< try to use the PIL and tkIcon packages to draw the icon >>
                #@+at 
                #@nonl
                # This code requires Fredrik Lundh's PIL and tkIcon packages:
                # 
                # Download PIL    from 
                # http://www.pythonware.com/downloads/index.htm#pil
                # Download tkIcon from http://www.effbot.org/downloads/#tkIcon
                # 
                # Many thanks to Jonathan M. Gilligan for suggesting this 
                # code.
                #@-at
                #@@c

                import Image,tkIcon,_tkicon

                # Wait until the window has been drawn once before attaching the icon in OnVisiblity.
                def visibilityCallback(event,self=self,w=w):
                    try: self.leoIcon.attach(w.winfo_id())
                    except: pass
                # Don't use c.bind here: c is not available.
                w.bind("<Visibility>",visibilityCallback)
                if not self.leoIcon:
                    # Load a 16 by 16 gif.  Using .gif rather than an .ico allows us to specify transparency.
                    icon_file_name = os.path.join(g.app.loadDir,'..','Icons','LeoWin.gif')
                    icon_file_name = os.path.normpath(icon_file_name)
                    icon_image = Image.open(icon_file_name)
                    if 1: # Doesn't resize.
                        self.leoIcon = self.createLeoIcon(icon_image)
                    else: # Assumes 64x64
                        self.leoIcon = tkIcon.Icon(icon_image)
                #@nonl
                #@-node:ekr.20070215164948.61:<< try to use the PIL and tkIcon packages to draw the icon >>
                #@nl
            except:
                # traceback.print_exc()
                self.leoIcon = None
    #@nonl
    #@-node:ekr.20070215164948.60:attachLeoIcon
    #@+node:ekr.20070215164948.62:createLeoIcon
    # This code is adapted from tkIcon.__init__
    # Unlike the tkIcon code, this code does _not_ resize the icon file.

    def createLeoIcon (self,icon):

        try:
            import Image,tkIcon,_tkicon

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
    #@nonl
    #@-node:ekr.20070215164948.62:createLeoIcon
    #@-node:ekr.20070215164948.59:Icons (wxGui) (to do)
    #@+node:ekr.20070215164948.63:Idle time (wxGui) (to do)
    #@+node:ekr.20070215164948.64:setIdleTimeHook
    def setIdleTimeHook (self,idleTimeHookHandler,*args,**keys):

        pass # g.trace(idleTimeHookHandler)

    #@-node:ekr.20070215164948.64:setIdleTimeHook
    #@+node:ekr.20070215164948.65:setIdleTimeHookAfterDelay
    def setIdleTimeHookAfterDelay (self,idleTimeHookHandler,*args,**keys):

        g.trace(idleTimeHookHandler)
    #@nonl
    #@-node:ekr.20070215164948.65:setIdleTimeHookAfterDelay
    #@-node:ekr.20070215164948.63:Idle time (wxGui) (to do)
    #@+node:ekr.20070215164948.66:isTextWidget
    def isTextWidget (self,w):

        for theClass in (wx.TextCtrl,wx.richtext.RichTextCtrl,wx.stc.StyledTextCtrl):
            if isinstance(w,theClass):
                return True
        else:
            return False
    #@-node:ekr.20070215164948.66:isTextWidget
    #@+node:ekr.20070215164948.67:widget_name
    def widget_name (self,w):

        # First try the wxWindow.GetName method.
        # All wx Text widgets, including wx.stc.StyledControl, have this method.
        if hasattr(w,'GetName'):
            name = w.GetName()
        else:
            name = repr(w)
        return name
    #@-node:ekr.20070215164948.67:widget_name
    #@-node:ekr.20070215164948.47:gui utils (must add several)
    #@-others
#@nonl
#@-node:ekr.20070215164948.5:ironPythonGui class
#@-others
#@-node:ekr.20070215164948:@thin ironPythonGui.py
#@-leo

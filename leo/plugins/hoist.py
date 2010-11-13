#@+leo-ver=5-thin
#@+node:ekr.20040331072607: * @file hoist.py
"""Adds Hoist/De-Hoist buttons to the toolbar."""

#@+<< change history >>
#@+node:ekr.20040908093511: ** << change history >>
#@+at
# 
# 0.1: Original version by Davide Salomoni.
# 0.2 EKR: Color mod
# 0.3 DS:  Works with multiple open files.
# 0.4 EKR: 4.2 coding style, enable or disable buttons, support for unit tests.
# 0.5 EKR: Use constant size for non Windows platforms.
# 0.6: EKR:
#     - Added USE_SIZER and USE_FIXED_SIZES.
#       When USE_SIZER is False (recommended), the code creates buttons using c.frame.addIconButton.
# 0.7 EKR:
#     - Created a separate class for each commander.
#     - Simplified the code a bit: no need for independent callbacks.
# 0.8 EKR: Use g.importExtension to import Tkinter as Tk.
# 0.9 EKR: Make sure self.c == keywords.get('c') in all hook handlers.
# 1.0 EKR: Added support for chapters: don't allow a dehoist of an @chapter node.
# 1.1 EKR: Use hoist-changed hook rather than idle-time hook to update the widgets.
# 1.2 bobjack:
#     - bind hois/dehoist buttons together if Tk and toolbar.py is enabled
#@-<< change history >>

__version__ = "1.2"

# print('at top of hoist.py')

#@+<< imports >>
#@+node:ekr.20040908093511.1: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter')

import sys
#@-<< imports >>

activeHoistColor = "pink1" # The Tk color to use for the active hoist button.

# Set this to 0 if the sizing of the toolbar controls doesn't look good on your platform.
USE_SIZER = False
USE_FIXED_SIZES = sys.platform != "darwin"
SIZER_HEIGHT = 23 # was 25
SIZER_WIDTH = 55 # was 70


#@+others
#@+node:ekr.20070301070027: ** init
def init ():

    ok = Tk and g.app.gui.guiName() == "tkinter"

    if ok:
        g.registerHandler("after-create-leo-frame",onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20050104063423: ** onCreate
def onCreate (tag,keys):

    c = keys.get('c')
    # g.trace('hoist.py','c',c)
    if not (c and c.exists):
        return

    # Rewritten to avoid pylint complaint.
    if not hasattr(c,'theHoistButtonsController'):
        c.theHoistButtonsController = hoist = HoistButtons(c)

        useTkFrame = g.app.gui.guiName() == 'tkinter' and hasattr(c.frame, 'getIconButton')

        if useTkFrame:
            hoist.addFramedWidgets()
        else:
            hoist.addWidgets()

        g.registerHandler("hoist-changed", onHoistChanged)
#@+node:bobjack.20080503151427.7: ** onHoistChanged
def onHoistChanged(tag, keywords):

    c = keywords.get('c')  
    if not (c and c.exists and hasattr(c,"hoistStack")):
        return

    c.theHoistButtonsController.onHoistChanged(tag, keywords) 
#@+node:ekr.20040331072607.1: ** class HoistButtons
class HoistButtons:

    """Hoist/dehoist buttons for the toolbar."""

    #@+others
    #@+node:ekr.20040331072607.2: *3* __init__
    def __init__(self,c):

        self.c = c
        self.hoistButton = None
        self.deHoistButton = None
    #@+node:ekr.20040331072607.3: *3* _getSizer
    def _getSizer(self, parent, height, width):

        """Return a sizer object to force a Tk widget to be the right size"""

        if USE_FIXED_SIZES: 
            sizer = Tk.Frame(parent, height=height, width=width)
            sizer.pack_propagate(0) # don't shrink 
            sizer.pack(side="right")
            return sizer
        else:
            return parent
    #@+node:ekr.20040331072607.4: *3* addWidgets
    def addWidgets (self):

        """Add the widgets to the toolbar."""

        c = self.c ; toolbar = c.frame.iconBar
        if not toolbar: return

        buttons = []
        for text in ('Hoist','De-Hoist'):
            if USE_SIZER:
                parent = self._getSizer(toolbar,SIZER_HEIGHT,SIZER_WIDTH)
                b = Tk.Button(parent,text=text)
            else:
                b = c.frame.addIconButton(text=text)
            buttons.append(b)

        self.hoistButton,self.dehoistButton = b1,b2 = buttons

        for b,command in ((b1,c.hoist),(b2,c.dehoist)):

            def hoistPluginCallback(c=c,command=command):
                val = command(event=None)
                # Careful: func may destroy c.
                if c.exists: c.outerUpdate()
                return val

            b.configure(command=hoistPluginCallback)
            b.pack(side='left',fill='none')

        self.bgColor = b1.cget('background')
        self.activeBgColor = b1.cget('activebackground')
    #@+node:bobjack.20080503151427.6: *3* addFramedWidgets
    def addFramedWidgets (self):

        """Add the widgets to the toolbar."""

        c = self.c ; toolbar = c.frame.iconBar
        if not toolbar: return

        self.hoist_button_frame = bf = Tk.Frame(self.c.frame.top)

        buttons = []
        for text in ('Hoist','De-Hoist'):
            b = c.frame.getIconButton(text=text)
            buttons.append(b)

        self.hoistButton, self.dehoistButton = b1, b2 = buttons

        for b,command in ((b1,c.hoist),(b2,c.dehoist)):

            def hoistPluginCallback(c=c,command=command):
                val = command(event=None)
                # Careful: func may destroy c.
                if c.exists: c.outerUpdate()
                return val

            b.configure(command=hoistPluginCallback)

        #@+<< bind and pack buttons >>
        #@+node:bobjack.20080503151427.8: *4* << bind and pack buttons >>
        for btn in (b1, b2):
            btn.pack(in_=bf, side='left')

        bf.leoDragHandle = (b1, b2)
        self.c.frame.addIconWidget(bf)  
        #@-<< bind and pack buttons >>

        self.bgColor = b1.cget('background')
        self.activeBgColor = b1.cget('activebackground')
    #@+node:ekr.20040331072607.7: *3* onHoistChanged
    def onHoistChanged(self,tag,keywords):

        c = self.c

        if g.app.killed or g.app.unitTesting: return


        for b,f in (
            (self.hoistButton,c.canHoist),
            (self.dehoistButton,c.canDehoist),
        ):
            state = g.choose(f(),"normal","disabled")
            b.config(state=state)

        n = c.hoistLevel()
        if n > 0:
            self.hoistButton.config(bg=activeHoistColor,
                activebackground=activeHoistColor,
                text="Hoist %s" % n)
        else:
            self.hoistButton.config(bg=self.bgColor,
                activebackground=self.activeBgColor,
                text="Hoist")
    #@-others
#@-others
#@-leo

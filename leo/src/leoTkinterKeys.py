#@+leo-ver=4-thin
#@+node:ekr.20031218072017.4099:@thin leoTkinterKeys.py
"""Tkinter keystroke handling for Leo."""

#@@language python
#@@tabwidth -4
#@@pagewidth 80

import Tkinter as Tk
import leoKeys

class tkinterKeyHandlerClass (leoKeys.keyHandlerClass):
    '''Tkinter overrides of base keyHandlerClass.'''
    #@    @+others
    #@+node:ekr.20061031170011:tkKeys.ctor
    def __init__(self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

        # Init the base class.
        leoKeys.keyHandlerClass.__init__(self,c,useGlobalKillbuffer,useGlobalRegisters)

        # Create
        self.createTkIvars()
    #@-node:ekr.20061031170011:tkKeys.ctor
    #@+node:ekr.20061031170011.1:createTkIvars
    def createTkIvars(self):

        if not self.useTextWidget and self.widget:
            self.svar = Tk.StringVar()
            self.widget.configure(textvariable=self.svar)
        else:
            self.svar = None
    #@-node:ekr.20061031170011.1:createTkIvars
    #@+node:ekr.20070613190239:tkKeys.propagateKeyEvent
    def propagateKeyEvent (self,event):
        return 'continue'
    #@nonl
    #@-node:ekr.20070613190239:tkKeys.propagateKeyEvent
    #@-others
#@nonl
#@-node:ekr.20031218072017.4099:@thin leoTkinterKeys.py
#@-leo

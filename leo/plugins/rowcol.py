#@+leo-ver=5-thin
#@+node:ekr.20040108095351: * @file rowcol.py
"""Adds row/column indicators to the toolbar."""

#@@language python
#@@tabwidth -4

__plugin_name__ = "Row/Column indicators"
__version__ = "0.4"

#@+<< imports >>
#@+node:ekr.20040908094021.2: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@-<< imports >>
#@+<< version history >>
#@+node:ekr.20041120114651: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Initial version.
# 
# 0.2 EKR: Make sure this works properly with multiple windows.
# 0.3 EKR: Removed call to g.top.  We now test whether c is valid using hasattr(c,'frame')
# 0.4 EKR: set __plugin_name__ rather than __name__
#@-<< version history >>

#@+others
#@+node:ekr.20101110150056.9475: ** init
def init():

    ok = Tk and g.app.gui.guiName() == "tkinter"

    if ok:
        g.registerHandler("after-create-leo-frame",onCreate)
        g.plugin_signon("rowcol")

    return ok
#@+node:ekr.20041120114651.1: ** onCreate
def onCreate (tag,keywords):

    c = keywords.get("c")
    if c:
        rowCol = rowColClass(c)
        rowCol.addWidgets()
        g.registerHandler("idle",rowCol.update)
#@+node:ekr.20040108095351.1: ** class rowColClass
class rowColClass:

    """Class that puts row/column indicators in the status bar."""

    #@+others
    #@+node:ekr.20040108100040: *3* __init__
    def __init__ (self,c):

        self.c = c
        self.lastRow,self.lastCol = -1,-1
    #@+node:ekr.20040108095351.2: *3* addWidgets
    def addWidgets (self):

        c = self.c
        iconBar = c.frame.iconBar
        iconBarFrame = iconBar.getFrame()

        # Main container 
        self.frame = Tk.Frame(iconBarFrame) 
        self.frame.pack(side="left")

        text = "line 0, col 0"
        width = len(text) # Setting the width here prevents jitters.
        self.label = Tk.Label(self.frame,text=text,width=width,anchor="w")
        self.label.pack(side="left")

        # Update the row/column indicators immediately to reserve a place.
        self.update()
    #@+node:ekr.20040108095351.4: *3* update
    def update (self,*args,**keys):

        c = self.c

        # This is called at idle-time, and there can be problems when closing the window.
        if g.app.killed or not c or not hasattr(c,'frame'):
            return

        w = c.frame.body.bodyCtrl 
        tab_width = c.frame.tab_width

        s = w.getAllText()
        index = w.getInsertPoint()
        row,col = g.convertPythonIndexToRowCol(s,index)

        if col > 0:
            s2 = s[index-col:index]
            s2 = g.toUnicode(s2)
            col = g.computeWidth (s2,c.tab_width)

        if row != self.lastRow or col != self.lastCol:
            s = "line %d, col %d " % (row,col)
            self.label.configure(text=s)
            self.lastRow,self.lastCol = row,col

        if 0: # Done in idle handler.
            self.label.after(500,self.update)
    #@-others
#@-others
#@-leo

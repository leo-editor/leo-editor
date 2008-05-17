#@+leo-ver=4-thin
#@+node:ekr.20040831115238:@thin URLloader.py
"""This plugin uses Python's urllib module to download files and import them into Leo.
"""

#@@language python
#@@tabwidth -4

__version__ = ".5"
#@<< Change log >>
#@+node:ekr.20040831115918:<< Change log >>
#@+at
# 
# .2:  8/31/04 EKR:  Minor changes for 4.2 style.
# 
# .3 EKR:
#     - Changed 'new_c' logic to 'c' logic.
#     - Added init function.
# .4 EKR:
#     - Removed 'start2' hook and haveseen dict.
# .5 EKR:
#     - use c.frame.log.select.selectTab instead of TabbedLog plugin.
#@-at
#@nonl
#@-node:ekr.20040831115918:<< Change log >>
#@nl
#@<< imports >>
#@+node:ekr.20040831115918.1:<< imports >>
import leoGlobals as g
import leoPlugins

Tk  = g.importExtension('Tkinter',  pluginName=__name__,verbose=True)
Pmw = g.importExtension("Pmw",      pluginName=__name__,verbose=True)

import os
import urllib
import weakref
#@nonl
#@-node:ekr.20040831115918.1:<< imports >>
#@nl

#@+others
#@+node:ekr.20050311090939.7:init
def init ():

    ok = Tk and Pmw # Ok for unit test: adds tabbed pane to log.
    if not ok: return

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        leoPlugins.registerHandler(('new','open2'), addURLPane)
        g.plugin_signon( __name__ )

    return ok
#@nonl
#@-node:ekr.20050311090939.7:init
#@+node:ekr.20040831115238.1:addURLPane
def addURLPane (tag,keywords):

    c = keywords.get('c')
    if not c: return

    # New in Leo 4.4: the log is always tabbed.
    if 1: x = c.frame.log.selectTab('URLLoad')
    else: x = TabbedLog.getPane("URLLoad",c)

    ef = Pmw.EntryField(x,labelpos='n',label_text='URL:')
    e = ef.component('entry')
    e.configure(background='white',foreground='blue')
    ef.pack(expand=1,fill='x')
    b = Tk.Button(x,text='Load')
    b.pack()
    c.bind(b,'<Button-1>',lambda event,entry=e,c=c: load(event,entry,c))
#@nonl
#@-node:ekr.20040831115238.1:addURLPane
#@+node:ekr.20040831115238.2:load
def load( event, entry, c ):

    txt = entry.get()
    f = urllib.urlopen( txt )
    tname = os.tmpnam()
    tf = open( tname, 'w' )
    tf.write( f.read() )
    tf.close()
    f.close()

    c.importCommands.importFilesCommand( [ tname ], '@file')
    cv = c.currentVnode()
    cv = cv.nthChild( 0 )
    c.setHeadString(cv,txt )
    os.remove( tname )
#@nonl
#@-node:ekr.20040831115238.2:load
#@-others
#@nonl
#@-node:ekr.20040831115238:@thin URLloader.py
#@-leo

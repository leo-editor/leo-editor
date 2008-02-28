#@+leo-ver=4-thin
#@+node:ekr.20060328125925:@thin chapter_hoist.py
#@<< docstring >>
#@+node:ekr.20060328125925.1:<< docstring >>
"""A plugin to create hoist buttons.  It is kind of a Chapters lite plugin

This plugin puts two buttons in the icon area: a button called 'Save Hoist' and
a button called 'Dehoist'.

The 'Save Hoist' button hoists the presently selected node and creates a button
which can later rehoist the same node.

The 'Dehoist' button performs one level of dehoisting

Requires at least version 0.19 of mod_scripting
"""
#@nonl
#@-node:ekr.20060328125925.1:<< docstring >>
#@nl
#@<< imports >>
#@+node:ekr.20060328125925.2:<< imports >>
import leoGlobals as g
import leoPlugins
from mod_scripting import scriptingController

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@-node:ekr.20060328125925.2:<< imports >>
#@nl

__version__ = "0.4"
#@<< version history >>
#@+node:ekr.20060328125925.3:<< version history >>
#@+at
# 
# 0.1 btheado: initial creation.
# 0.2 EKR: changed to @thin.
# 0.3 EKR: init now succeeds for unit tests.
# 0.4 EKR: use new calling sequences for sc.createIconButton.
#          Among other things, this creates the save-hoist commnand.
#@-at
#@nonl
#@-node:ekr.20060328125925.3:<< version history >>
#@nl

#@+others
#@+node:ekr.20060328125925.4:init
def init ():

    ok = Tk is not None # OK for unit tests.

    if ok:
        if g.app.gui is None:
            g.app.createTkGui(__file__)

        ok = g.app.gui.guiName() == "tkinter"

        if ok:
            # Note: call onCreate _after_ reading the .leo file.
            # That is, the 'after-create-leo-frame' hook is too early!
            leoPlugins.registerHandler(('new','open2'),onCreate)
            g.plugin_signon(__name__)

    return ok
#@nonl
#@-node:ekr.20060328125925.4:init
#@+node:ekr.20060328125925.5:onCreate
def onCreate (tag, keys):

    """Handle the onCreate event in the chapterHoist plugin."""

    c = keys.get('c')

    if c:
        sc = scriptingController(c)
        ch = chapterHoist(sc,c)
#@-node:ekr.20060328125925.5:onCreate
#@+node:ekr.20060328125925.6:class chapterHoist
class chapterHoist:
    #@    @+others
    #@+node:ekr.20060328125925.7: ctor
    def __init__ (self,sc,c):
        self.createSaveHoistButton(sc,c)
        self.createDehoistButton(sc,c)
    #@-node:ekr.20060328125925.7: ctor
    #@+node:ekr.20060328125925.8:createSaveHoistButton
    def createSaveHoistButton(self,sc,c):

        def saveHoistCallback(event=None,self=self,sc=sc,c=c):
            self.createChapterHoistButton(sc,c,c.currentPosition())
            c.hoist()
            return 'break'

        b = sc.createIconButton(
            text='save-hoist',
            command = saveHoistCallback,
            shortcut = None,
            statusLine='Create hoist button current node',
            bg='LightSteelBlue1')

        return b
    #@nonl
    #@-node:ekr.20060328125925.8:createSaveHoistButton
    #@+node:ekr.20060328125925.9:createDehoistButton
    def createDehoistButton(self,sc,c):

        def dehoistCallback(event=None,c=c):
            c.dehoist()
            return 'break'

        b = sc.createIconButton(
            text='dehoist',
            command=dehoistCallback,
            shortcut=None,
            statusLine='Dehoist',
            bg='LightSteelBlue1')

        return b
    #@nonl
    #@-node:ekr.20060328125925.9:createDehoistButton
    #@+node:ekr.20060328125925.10:createChapterHoistButton
    def createChapterHoistButton (self,sc,c,p):

        '''Generates a hoist button for the headline at the given position'''    
        h = p.headString()
        buttonText = sc.getButtonText(h)
        statusLine = "Hoist %s" % h

        def hoistButtonCallback (event=None,self=self,c=c,p=p.copy()):
            while (c.canDehoist()):
                c.dehoist()
            c.selectPosition(p)
            c.hoist()
            return 'break'

        b = sc.createIconButton(
            text=buttonText,
            command=hoistButtonCallback,
            statusLine=statusLine,
            shortcut=None,
            bg='LightSteelBlue1')
    #@-node:ekr.20060328125925.10:createChapterHoistButton
    #@-others
#@nonl
#@-node:ekr.20060328125925.6:class chapterHoist
#@-others
#@nonl
#@-node:ekr.20060328125925:@thin chapter_hoist.py
#@-leo

#@+leo-ver=4-thin
#@+node:ekr.20060621123339:@thin examples/print_cp.py
#@<< docstring >>
#@+node:ekr.20060621123339.1:<< docstring >>
'''A plugin showing how to convert an @button node to a plugin.

This plugin register the 'print-cp' minibuffer command.'''
#@-node:ekr.20060621123339.1:<< docstring >>
#@nl

__version__ = '0.1'
#@<< version history >>
#@+node:ekr.20060621123339.2:<< version history >>
#@@killcolor
#@+at
# 
# v 0.1: Initial version.
#@-at
#@nonl
#@-node:ekr.20060621123339.2:<< version history >>
#@nl

#@<< imports >>
#@+node:ekr.20060621123339.3:<< imports >>
import leoGlobals as g
import leoPlugins

if 0:
    Pmw = g.importExtension('Pmw',    pluginName=__name__,verbose=True,required=True)
    Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

# Whatever other imports your plugins uses.
#@nonl
#@-node:ekr.20060621123339.3:<< imports >>
#@nl

#@+others
#@+node:ekr.20060621123339.4:init
def init ():

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        # leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        leoPlugins.registerHandler(('new','open2'),onCreate)

    return ok
#@nonl
#@-node:ekr.20060621123339.4:init
#@+node:ekr.20060621123339.5:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    thePluginController = pluginController(c)
#@nonl
#@-node:ekr.20060621123339.5:onCreate
#@+node:ekr.20060621123339.6:class pluginController
class pluginController:

    #@    @+others
    #@+node:ekr.20060621123339.7:__init__
    def __init__ (self,c):
        self.c = c
        c.k.registerCommand('print-cp',shortcut=None,func=self.print_cp)
        script = "c.k.simulateCommand('print-cp')"
        g.makeScriptButton(c,script=script,buttonText='Print c & p',bg='red')
    #@nonl
    #@-node:ekr.20060621123339.7:__init__
    #@+node:ekr.20060621124649:print_cp
    def print_cp (self,event=None):

        c = self.c ; p = c.currentPosition()
        g.es_print('c: %s' % (c.fileName()),color='red')
        g.es_print('p: %s' % (p.headString()),color='red')
    #@nonl
    #@-node:ekr.20060621124649:print_cp
    #@-others
#@nonl
#@-node:ekr.20060621123339.6:class pluginController
#@-others
#@nonl
#@-node:ekr.20060621123339:@thin examples/print_cp.py
#@-leo

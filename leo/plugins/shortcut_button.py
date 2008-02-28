#@+leo-ver=4-thin
#@+node:ekr.20060601151845:@thin shortcut_button.py
'''A plugin to create a 'Shortcut' button in the icon area.

Pressing the Shortcut button creates *another* button which when pressed will
select the presently selected node at the time the button was created.

This plugin requires that the mod_scripting plugin be enabled.'''

#@<< imports >>
#@+node:ekr.20060601151845.2:<< imports >>
import leoGlobals as g
import leoPlugins

import mod_scripting

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@nonl
#@-node:ekr.20060601151845.2:<< imports >>
#@nl

__version__ = "0.4"
#@<< version history >>
#@+node:ekr.20060601151845.3:<< version history >>
#@@nocolor
#@+at
# 
# 0.1 Initial version.  Suggested by Brian Theado.
# 0.2 EKR: Improved docstring.
# 0.3 EKR: Rewritten to used latest mod_scripting plugin.
# As a result, it creates the shortcut-button command, and commands for every 
# button created.
# 0.4 EKR: The created commands now have the form: go-x-node to reduce chance 
# of conflicts with other commands.
#@-at
#@nonl
#@-node:ekr.20060601151845.3:<< version history >>
#@nl

#@+others
#@+node:ekr.20060601151845.4:init
def init ():

    ok = Tk and mod_scripting and not g.app.unitTesting

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
#@-node:ekr.20060601151845.4:init
#@+node:ekr.20060601151845.5:onCreate
def onCreate (tag, keys):

    """Handle the onCreate event in the chapterHoist plugin."""

    c = keys.get('c')

    if c:
        sc = mod_scripting.scriptingController(c)
        ch = shortcutButton(sc,c)
#@nonl
#@-node:ekr.20060601151845.5:onCreate
#@+node:ekr.20060601151845.6:class shortcutButton
class shortcutButton:

    #@    @+others
    #@+node:ekr.20060601151845.7: ctor
    def __init__ (self,sc,c):

        self.createShortcutButtonButton(sc,c)
    #@-node:ekr.20060601151845.7: ctor
    #@+node:ekr.20060601153526:createShortcutButtonButton
    def createShortcutButtonButton(self,sc,c):

        def shortcutButtonButtonCallback(event=None,self=self,sc=sc,c=c):
            self.createShortcutButton(sc,c)
            return 'break'

        b = sc.createIconButton(
            text='shortcut',
            command=shortcutButtonButtonCallback,
            shortcut=None,
            statusLine='Create a shortcut button',
            bg='LightSteelBlue1')
    #@-node:ekr.20060601153526:createShortcutButtonButton
    #@+node:ekr.20060601151845.10:createShortcutButton
    def createShortcutButton (self,sc,c):

        '''Create a button which selects the present position (when the button was created).'''
        p = c.currentPosition() ; h = p.headString()
        commandName = 'go-%s-node' % h

        def shortcutButtonCallback (event=None,c=c,p=p):
            c.beginUpdate()
            try:
                c.selectPosition(p)
            finally:
                c.endUpdate()
            return 'break'

        b = sc.createIconButton(
            text=commandName,
            command=shortcutButtonCallback,
            shortcut=None,
            statusLine=commandName,
            bg='LightSteelBlue1')
    #@-node:ekr.20060601151845.10:createShortcutButton
    #@-others
#@nonl
#@-node:ekr.20060601151845.6:class shortcutButton
#@-others
#@nonl
#@-node:ekr.20060601151845:@thin shortcut_button.py
#@-leo

#@+leo-ver=4-thin
#@+node:ekr.20060601151845:@thin shortcut_button.py
#@<<docstring>>
#@+node:bobjack.20080614084120.6:<< docstring >>
'''A plugin to create a 'shortcut' button in the icon area.

Pressing the 'shortcut' button creates *another* button which when pressed will
select the presently selected node at the time the button was created.

This plugin requires that the mod_scripting plugin be enabled.

An @data shortcut_button_data may be used in @setting trees to control the colors
for the buttons and to set an rClick menu.

The colors and menus for the 'shortcut' button itself are set using::

    master-bg = <color>
    master-fg = <color>
    master-menu = <rclick menu name>


The colors and menus for the 'shortcut' button itself are set using::

    slave-bg = <color>
    slave-fg = <color>
    slave-menu = <rclick menu name>


The menus will be ignored if the rClick.py and toolbar.py plugins are not enabled.

'''
#@nonl
#@-node:bobjack.20080614084120.6:<< docstring >>
#@nl




#@<< imports >>
#@+node:ekr.20060601151845.2:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import mod_scripting

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@nonl
#@-node:ekr.20060601151845.2:<< imports >>
#@nl

__version__ = "0.5"
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
# 0.5 bobjack:
#     - Updated to be compatible with toolbar.py plugin extensions
#     - Added support for @data shortcut-button-data which allow
#       setting of forground/background colors and rClick menus
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

    """Handle the onCreate event in the shortcut_button plugin."""

    c = keys.get('c')

    if c and c.exists and not hasattr(c, 'theShortcutButtonController'):
        c.theShortcutButtonController = shortcutButton(c)
#@nonl
#@-node:ekr.20060601151845.5:onCreate
#@+node:ekr.20060601151845.6:class shortcutButton
class shortcutButton:

    #@    @+others
    #@+node:ekr.20060601151845.7: ctor
    def __init__ (self, c):

        self.c = c


        self.item_data = self.get_item_data()

        self.createShortcutButtonButton()



    #@-node:ekr.20060601151845.7: ctor
    #@+node:bobjack.20080613173457.11:get_item_data
    def get_item_data(self):

        c = self.c

        item_data = {}

        data = c.config.getData('shortcut_button_data') or {}

        for pair in data:

            if '=' in pair:
                k, v = pair.split('=', 1)
                k, v = k.strip(), v.strip()

                item_data[k] = v

        return item_data
    #@-node:bobjack.20080613173457.11:get_item_data
    #@+node:ekr.20060601153526:createShortcutButtonButton
    def createShortcutButtonButton(self):

        c = self.c
        sc = c.theScriptingController

        data = self.item_data

        kws = {
            'text': 'shortcut',
            'command': None,
            'shortcut': None,
            'statusLine': 'create a shortcut button',
            'bg':'LightSteelBlue1',
        }

        bg = data.get('master-bg')
        if bg:
            kws['bg'] = bg

        b = sc.createIconButton(**kws)

        fg = data.get('master-fg')
        if fg:
            b.configure(foreground=fg)

        def shortcutButtonButtonCallback(event=None,self=self, b=b):
            self.createShortcutButton(b)
            c.redraw()
            c.outerUpdate()
            #return 'break'

        b.configure(command=shortcutButtonButtonCallback)

        menu = data.get('master-menu')
        if menu:
            b.context_menu = menu
    #@-node:ekr.20060601153526:createShortcutButtonButton
    #@+node:ekr.20060601151845.10:createShortcutButton
    def createShortcutButton (self, b):

        '''Create a button which selects the present position (when the button was created).'''

        c = self.c

        data = self.item_data

        p = c.currentPosition()
        h = p.headString()

        commandName = 'go-%s-node' % h

        def shortcutButtonCallback (event=None,c=c,p=p):
            c.selectPosition(p)
            c.redraw()
            c.outerUpdate()
            #return 'break'

        kws = {
            'text': commandName,
            'command': shortcutButtonCallback,
            'shortcut': None,
            'statusLine': commandName,
            'bg':'LightSteelBlue1',
        }

        bg = data.get('slave-bg')
        if bg:
            kws['bg'] = bg

        try:
            bar = b.leoIconBar
        except AttributeError:
            bar = None

        bar = bar or c.frame.iconBar

        oldIconBar = c.frame.iconBar
        try:
            c.frame.iconBar = bar
            b = c.theScriptingController.createIconButton(**kws)

        finally:
            c.frame.iconBar = oldIconBar

        fg = data.get('slave-fg')
        if fg:
            b.configure(foreground=fg)

        menu = data.get('slave-menu')
        if menu:
            b.context_menu = menu
    #@-node:ekr.20060601151845.10:createShortcutButton
    #@-others
#@nonl
#@-node:ekr.20060601151845.6:class shortcutButton
#@-others
#@nonl
#@-node:ekr.20060601151845:@thin shortcut_button.py
#@-leo

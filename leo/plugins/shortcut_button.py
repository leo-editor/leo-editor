#@+leo-ver=5-thin
#@+node:ekr.20060601151845: * @file shortcut_button.py
#@+<<docstring>>
#@+node:bobjack.20080614084120.6: ** << docstring >>
''' Creates a 'shortcut' button in the icon area.

Pressing the 'shortcut' button creates *another* button which when pressed will
select the presently selected node at the time the button was created.

This plugin requires that the mod_scripting plugin be enabled. The toolbar.py
and rClick.py plugins are not required, but extra facilities are available
if they are enabled.

An @data shortcut_button_data may be used in @setting trees to control the colors
for the buttons and to set the name of the @popup menu to be used as a context menu.

If the following line appears::

    icon = <full or relative path to an icon>

then the requested icon will be shown instead of text in the master button.

The colors and menus for the 'shortcut' button itself are set using::

    master-bg = <color>
    master-fg = <color>
    master-menu = <@popup menu-name>

The menus will be ignored if the rClick.py and toolbar.py plugins are not enabled.

If the toolbar.py plugin is enabled then the following settings will be honored::

    iconbar = <name of an iconbar>
    hide = 

Iconbar gives the name of an iconbar to which the master button should initially be attached. 
If no name is given then the default 'iconbar' will be used. The iconbar will be created if it
does not already exist. 

If hide is left blank then any iconbar created will be shown initially, otherwise it will be
hidden. This has no effect if the iconbar already exists.

**Minibuffer Commands**

The following minibuffer commands are provided::

        If these commands are used in a button menu or an iconBar menu then the
        buttons will be created in the iconbar to which the menu or button
        is attached. Otherwise the button will be created in the default 'iconbar'. 

    create-shortcut-button

        Creates a duplicate of the master button, which when pressed
        will issue a create-shortcut command.

    create-shortcut

        Creates a slave button which when pressed will select the presently 
        selected node at the time the button was created.

'''
#@-<<docstring>>

#@+<< imports >>
#@+node:ekr.20060601151845.2: ** << imports >>
import leo.core.leoGlobals as g

import mod_scripting

try:
    import rClickBasePluginClasses as baseClasses
        # This requires Tk.
except ImportError:
    rClickBasePluginClasses = None
#@-<< imports >>

__version__ = "0.6"
#@+<< version history >>
#@+node:ekr.20060601151845.3: ** << version history >>
#@@nocolor
#@+at
# 
# 0.1 Initial version.  Suggested by Brian Theado.
# 0.2 EKR: Improved docstring.
# 0.3 EKR: Rewritten to used latest mod_scripting plugin.
# As a result, it creates the shortcut-button command, and commands for every button created.
# 0.4 EKR: The created commands now have the form: go-x-node to reduce chance of conflicts with other commands.
# 0.5 bobjack:
#     - Updated to be compatible with toolbar.py plugin extensions
#     - Added support for @data shortcut-button-data which allow
#       setting of forground/background colors and rClick menus
# 0.6 bobjack:
#     - added support for icon, iconbar and hide settings
#@-<< version history >>

#@+others
#@+node:ekr.20060601151845.4: ** init
def init ():

    ok = (
        rClickBasePluginClasses and mod_scripting and
        g.app.gui.guiName() == "tkinter" and
        not g.app.unitTesting
    )

    if ok:

        # Note: call onCreate _after_ reading the .leo file.
        # That is, the 'after-create-leo-frame' hook is too early!
        g.registerHandler(('new','open2'),onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20060601151845.5: ** onCreate
def onCreate (tag, keys):

    """Handle the onCreate event in the shortcut_button plugin."""

    c = keys.get('c')

    if c and c.exists and not hasattr(c, 'theShortcutButtonController'):
        c.theShortcutButtonController = shortcutButton(c)
#@+node:ekr.20060601151845.6: ** class shortcutButton
class shortcutButton(object):

    #@+others
    #@+node:ekr.20060601151845.7: *3*  ctor
    def __init__ (self, c):

        self.c = c

        try:
            self.iconBars = c.frame.iconBars
        except:
            self.iconBars = {}

        self.item_data = data = self.get_item_data()

        barName = data.get('iconbar')
        barHideOnStartup = data.get('hide')

        if barName and not barName in self.iconBars:

            try:
                bar = c.frame.getIconBar(barName=barName)
            except TypeError:
                bar = None

            if bar and barHideOnStartup:
                bar.hide()

        icon = data.get('icon')
        if icon:
            self.icon = baseClasses.getImage(icon)
        else:
            self.icon = None

        self.createShortcutButtonButton(barName)

        for command, method in [
            ('add-shortcut-button', self.addShortcutButton),
            ('shortcut-button-add-shortcut-button', self.addShortcutButton),

            ('add-shortcut', self.addShortcut),
            ('shortcut-button-add-shortcut', self.addShortcut)
        ]:

            c.k.registerCommand(command,shortcut=None,func=method,wrap=True)
    #@+node:bobjack.20080618205453.2: *3* add-shortcut-button
    def addShortcutButton(self, keywords):

        c = self.c

        phase = keywords.get('rc_phase')

        if phase not in ('invoke', 'minibuffer'):
            g.trace('wrong phase', phase)
            return

        barName = self.item_data.get('iconbar')
        bar = keywords.get('button') or keywords.get('bar')

        if bar:
            try:
                barName = bar.leoIconBar.barName
            except AttributeError:
                try:
                    barName = bar.barName 
                except:
                    barName = None

        self.createShortcutButtonButton(barName)
    #@+node:bobjack.20080618205453.3: *3* add-shortcut
    def addShortcut(self, keywords):

        phase = keywords.get('phase')

        if phase not in ('invoke', 'minibuffer'):
            return

        bar = keywords.get('bar')

        if bar:
            self.createShortcutButton(bar)
    #@+node:bobjack.20080613173457.11: *3* get_item_data
    def get_item_data(self):

        c = self.c

        item_data = {}

        data = c.config.getData('shortcut_button_data') or {}

        for pair in data:

            if '=' in pair:
                k, v = pair.split('=', 1)
                k, v = k.strip().lower(), v.strip()

                item_data[k] = v

        return item_data
    #@+node:ekr.20060601153526: *3* createShortcutButtonButton
    def createShortcutButtonButton(self, barName=None):

        c = self.c
        sc = c.theScriptingController

        data = self.item_data

        kws = {
            'text': 'shortcut',
            'command': None,
            'shortcut': None,
            'statusLine': 'Create a Shortcut Button',
            'bg':'LightSteelBlue1',
        }


        bg = data.get('master-bg')
        if bg:
            kws['bg'] = bg

        bar = self.iconBars.get(barName, c.frame.iconBar)

        oldIconBar = c.frame.iconBar
        try:
            c.frame.iconBar = bar
            b = sc.createIconButton(**kws)
        finally:
            c.frame.iconBar = oldIconBar

        fg = data.get('master-fg')
        if fg:
            b.configure(foreground=fg)

        def shortcutButtonButtonCallback(event=None,self=self, b=b):
            self.createShortcutButton(b)
            # Careful: func may destroy c.
            if c.exists: c.redraw_now()
            #return 'break'

        b.configure(command=shortcutButtonButtonCallback)

        menu = data.get('master-menu')
        if menu:
            b.context_menu = menu

        if self.icon:
            b.configure(image=self.icon)
    #@+node:ekr.20060601151845.10: *3* createShortcutButton
    def createShortcutButton (self, b):

        '''Create a button which selects the present position (when the button was created).'''

        c = self.c
        sc = c.theScriptingController

        data = self.item_data

        p = c.p
        h = p.h

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
            'statusLine': commandName[3:],
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
            b = sc.createIconButton(**kws)

        finally:
            c.frame.iconBar = oldIconBar

        fg = data.get('slave-fg')
        if fg:
            b.configure(foreground=fg)

        menu = data.get('slave-menu')
        if menu:
            b.context_menu = menu
    #@-others
#@-others
#@-leo

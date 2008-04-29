#@+leo-ver=4-thin
#@+node:bobjack.20080424190315.2:@thin toolbar.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:bobjack.20080424190906.12:<< docstring >>
"""A plugin to provide toolbar functionality for Leo.

The aim of this plugin is to provide scriptable toolbars in the same way that
rClick provides scriptable context menus, and using a similar api.

Backward compatability will be maintainid for the iconbar.

"""
#@nonl
#@-node:bobjack.20080424190906.12:<< docstring >>
#@nl

__version__ = "0.3"
__plugin_name__ = 'Toolbar Manager'



controllers = {}

#@<< version history >>
#@+node:bobjack.20080424190906.13:<< version history >>
#@+at
# 0.1 bobjack:
#     - initial version
# 0.2 bobjack:
#     - add toolbar-delete-button for use in button menus
#     - introduced onPreCreate module method
# 0.3 bobjack:
#     - added support for tooltips in @buttons
#     - fixed parameter bleed bug
#@-at
#@-node:bobjack.20080424190906.13:<< version history >>
#@nl
#@<< todo >>
#@+node:bobjack.20080424190906.14:<< todo >>
#@+at
#@-at
#@nonl
#@-node:bobjack.20080424190906.14:<< todo >>
#@nl
#@<< imports >>
#@+node:bobjack.20080424190906.15:<< imports >>
import leoGlobals as g
import leoPlugins
import leoTkinterFrame

import re
import sys
import os

Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

try:
    from PIL import Image
    from PIL import ImageTk
except ImportError:
    Image = ImageTk = None

mod_scripting = g.importExtension('mod_scripting',pluginName=__name__,verbose=True,required=True)
import leoTkinterFrame
#@-node:bobjack.20080424190906.15:<< imports >>
#@nl

#@<< required ivars >>
#@+node:bobjack.20080424195922.85:<< required ivars >>
#@+at
# This is a list of ivars that the pluginController must have and the type of 
# objects they are allowed to contain.
# 
#     (ivar, type)
# 
# where type may be a tuple and False indicates any type will do
# 
# The list is used by unit tests.
#@-at
#@@c

requiredIvars = (
    ('mb_retval', False),
    ('mb_keywords', False),
    ('commandList', (list, tuple)),
)
#@nonl
#@-node:bobjack.20080424195922.85:<< required ivars >>
#@nl


#@+others
#@+node:bobjack.20080424190906.6:Module-level
#@+node:bobjack.20080424190906.7:init
def init ():
    """Initialize and register plugin."""

    global old

    if not Tk:
        return False

    if g.app.unitTesting:
         return False

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        r = leoPlugins.registerHandler
        r('before-create-leo-frame',onPreCreate)
        r('after-create-leo-frame', onCreate)
        r('close-frame', onClose)

        g.app.gui.ScriptingControllerClass = ToolbarScriptingController

        leoTkinterFrame.leoTkinterFrame = ToolbarTkinterFrame



        g.plugin_signon(__name__)

    return ok
#@-node:bobjack.20080424190906.7:init
#@+node:bobjack.20080424195922.11:onPreCreate
def onPreCreate (tag, keys):
    """Replace iconBarClass with our own."""

    c = keys.get('c')
    if not (c and c.exists):
        return

    c.frame.iconBarClass = ToolbarTkIconBarClass
#@-node:bobjack.20080424195922.11:onPreCreate
#@+node:bobjack.20080426190702.6:onCreate
def onCreate (tag, keys):
    """Handle creation and initialization of the pluginController.

    Make sure the pluginController is created only once.
    """

    c = keys.get('c')
    if not (c and c.exists):
        return

    controller = controllers.get(c)
    if not controller:
        controllers[c] = controller = pluginController(c)
        controller.onCreate()

#@-node:bobjack.20080426190702.6:onCreate
#@+node:bobjack.20080424195922.10:onClose
def onClose (tag, keys):

    """Tell controller to clean up then destroy it."""

    c = keys.get('c')
    if not (c and c.exists):
        return

    controller = controllers.get(c)

    try: 
        del controllers[c]
    except KeyError:
        pass

    if not controller:
        return

    try:
        controller.onClose()
    finally:
        controller = None
#@-node:bobjack.20080424195922.10:onClose
#@+node:bobjack.20080428114659.2:class ToolbarTkinterFrame
class ToolbarTkinterFrame(leoTkinterFrame.leoTkinterFrame, object):

    #@    @+others
    #@+node:bobjack.20080428114659.3:def __init__
    def __init__(self, *args, **kw):

        self.iconBars= {}
        self.toolbarFrame = None
        super(ToolbarTkinterFrame, self).__init__(*args, **kw)
    #@-node:bobjack.20080428114659.3:def __init__
    #@+node:bobjack.20080428114659.4:createIconBar
    def createIconBar (self, name='iconbar'):

        frame = self.createToolbarFrame()

        if not name in self.iconBars:

            self.iconBars[name] = bar = self.iconBarClass(
                self.c, self.toolbarFrame, name=name
            )

        if name == 'iconbar':
            self.iconBar = self.iconBars[name]

        return self.iconBars[name]
    #@-node:bobjack.20080428114659.4:createIconBar
    #@+node:bobjack.20080428114659.5:createToolbarFrame
    def createToolbarFrame(self):

        if self.toolbarFrame:
            return self.toolbarFrame

        self.toolbarFrame = w = Tk.Frame(self.outerFrame)

        w.pack(fill='x')
    #@-node:bobjack.20080428114659.5:createToolbarFrame
    #@-others

#@-node:bobjack.20080428114659.2:class ToolbarTkinterFrame
#@+node:bobjack.20080425135232.6:class ToolbarScriptingController
scripting = mod_scripting.scriptingController
class ToolbarScriptingController(scripting, object):

    #@    @+others
    #@+node:bobjack.20080425135232.9:createAtButtonFromSettingHelper
    def createAtButtonFromSettingHelper(self,h,script,statusLine,shortcut,bg=None):

        data = self.getItemData(script)
        kw = {}
        if bg is not None:
            kw['bg'] = bg

        if data and 'tooltip' in data:
            statusLine = data['tooltip']
        scripting.createAtButtonFromSettingHelper(self,h,script,statusLine,shortcut,**kw)

    #@-node:bobjack.20080425135232.9:createAtButtonFromSettingHelper
    #@+node:bobjack.20080425135232.11:createAtButtonHelper
    def createAtButtonHelper(self, p, h, statusLine, shortcut, *args, **kw):

        data = self.getItemData(p.bodyString())

        for k in 'bg', 'verbose':
            if k in kw and kw[k] is None:
                del(kw[k])

        if data and 'tooltip' in data:
            statusLine = data['tooltip']


        scripting.createAtButtonHelper(self, p, h, statusLine, shortcut,  *args, **kw)
    #@-node:bobjack.20080425135232.11:createAtButtonHelper
    #@+node:bobjack.20080425135232.10:getItemData
    def getItemData(self, script):

        item_data = {}


        script = [ line.strip() for line in script.strip().splitlines() ]

        if not (script and script[0] == '@'):
            return {}

        while script:
            line = script.pop(0)

            if line == '@c':
                break 

            if not (line.startswith('@btn ') and '=' in line):
                continue

            key, value = line.split('=', 1)
            key, value = key[4:].strip(), value.strip()

            item_data[key] = value

        self.item_data = self.c.frame.iconBar.item_data = item_data

        return item_data
    #@-node:bobjack.20080425135232.10:getItemData
    #@+node:bobjack.20080428114659.18:getIconBar
    def getIconBar(self):

        return self.c.frame.iconBar


    def setIconBar(*args, **kw):
        pass

    iconBar = property(getIconBar, setIconBar)
    #@-node:bobjack.20080428114659.18:getIconBar
    #@+node:bobjack.20080426064755.77:deleteButton
    def deleteButton(self, button, event=None):

        """Delete the given button.

        This is called from callbacks, it is not a callback.

        """

        try:
            menu = button.context_menu
        except Exception:
            menu = None

        if event and menu:
            result = g.doHook(
                'rclick-popup',
                c=self.c, 
                event=event,
            )
            if result:
                return

        scripting.deleteButton(self, button)
    #@-node:bobjack.20080426064755.77:deleteButton
    #@+node:bobjack.20080428114659.12:createScriptButtonIconButton 'script-button' & callback
    def createScriptButtonIconButton (self, name='iconbar'):

        '''Create the 'script-button' button and the script-button command.'''

        c = self.c
        frame = c.frame

        def addScriptButtonCallback(event=None, self=self, name=name):
            return self.addScriptButtonCommand(event, name)

        self.createIconButton(
            text='script-button',
            command = addScriptButtonCallback,
            shortcut=None,
            statusLine='Make script button from selected node',
            bg="#ffffcc",
        )
    #@+node:bobjack.20080428114659.13:addScriptButtonCommand
    def addScriptButtonCommand (self,event=None, name='iconbar'):

        '''Called when the user presses the 'script-button' button or executes the script-button command.'''

        c = self.c
        frame = c.frame
        p = c.currentPosition();
        h = p.headString()

        buttonText = self.getButtonText(h)
        shortcut = self.getShortcut(h)
        statusLine = "Run Script: %s" % buttonText
        if shortcut:
            statusLine = statusLine + " @key=" + shortcut

        if name not in frame.iconBars:
            return

        oldIconBar = frame.iconBar
        try:
            frame.iconBar =  frame.iconBars[name]       
            b = self.createAtButtonHelper(
                p, h, statusLine, shortcut, bg='MistyRose1', verbose=True
            )
        finally:
            frame.iconBar = oldIconBar

        c.frame.bodyWantsFocus()
    #@-node:bobjack.20080428114659.13:addScriptButtonCommand
    #@-node:bobjack.20080428114659.12:createScriptButtonIconButton 'script-button' & callback
    #@-others
#@-node:bobjack.20080425135232.6:class ToolbarScriptingController
#@+node:bobjack.20080426064755.66:class ToolbarTkIconBarClass
iconbar = leoTkinterFrame.leoTkinterFrame.tkIconBarClass
class ToolbarTkIconBarClass(iconbar, object):

    '''A class representing the singleton Icon bar'''

    iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

    #@    @+others
    #@+node:bobjack.20080428114659.6:__init__
    def __init__ (self,c,parentFrame, name='iconBar'):

        self.name = name
        super(ToolbarTkIconBarClass, self).__init__(c, parentFrame)

        self.iconFrame.bind('<Button-3>', self.onRightClick)
    #@-node:bobjack.20080428114659.6:__init__
    #@+node:bobjack.20080428114659.9:onRightClick
    def onRightClick(self, event=None):

        g.doHook('rclick-popup', c=self.c, event=event,
            context_menu='default-iconbar-menu',
            toolbar=self,
        )
    #@-node:bobjack.20080428114659.9:onRightClick
    #@+node:bobjack.20080426064755.76:add
    def add(self,*args,**keys):

        try:
            data = self.item_data
        except:
            data = None

        btn = None
        try:
            #@        << pre create button >>
            #@+node:bobjack.20080426205344.2:<< pre create button >>
            if data:

                if 'bg' in data:
                    keys['bg'] = data['bg']

                if 'icon' in data:
                    image = self.getImage(data['icon'])
                    if image:
                        keys['image'] = image
                        if not 'bg' in keys:
                            keys['bg'] = ''
            #@-node:bobjack.20080426205344.2:<< pre create button >>
            #@nl
            btn = iconbar.add(self, *args, **keys)
            #@        << post create button >>
            #@+node:bobjack.20080426205344.3:<< post create button >>
            if data and btn:

                if 'fg' in data:
                    btn.configure(fg=data['fg'])

                if 'menu' in data:
                    btn.context_menu = data['menu']
            #@-node:bobjack.20080426205344.3:<< post create button >>
            #@nl

        finally:
            self.item_data = None

        return btn
    #@-node:bobjack.20080426064755.76:add
    #@+node:bobjack.20080426064755.79:getImage
    def getImage(self, path):

        """Use PIL to get an image suitable for displaying in menus."""

        c = self.c

        if not (Image and ImageTk):
            return None

        path = g.os_path_normpath(path)

        if not hasattr(self, 'iconCache'):
            self.iconCache = {}

        try:
            return self.iconCache[path]
        except KeyError:
            pass

        iconpath = g.os_path_join(self.iconBasePath, path)

        try:
            return self.iconCache[iconpath]
        except KeyError:
            pass

        try:
            image = Image.open(path)
        except:
            image = None

        if not image:

            try:
                image = Image.open(iconpath)
            except:
                image = None

        if not image:
            return None

        try:    
            image = ImageTk.PhotoImage(image)
        except:
            image = None

        if not image or not image.height():
            g.es('Bad Toolbar Icon: %s' % path)
            return None

        self.iconCache[path] = image

        return image

    #@-node:bobjack.20080426064755.79:getImage
    #@-others
#@-node:bobjack.20080426064755.66:class ToolbarTkIconBarClass
#@-node:bobjack.20080424190906.6:Module-level
#@+node:bobjack.20080424195922.12:class pluginController
class pluginController(object):

    """A per commander controller providing a toolbar manager."""

    commandList = (
        'toolbar-delete-button',
        'toolbar-add-iconbar',
        'toolbar-hide-iconbar',
        'toolbar-add-script-button',
        'toolbar-show-iconbar-menu',
    )

    #@    @+others
    #@+node:bobjack.20080424195922.13:__init__
    def __init__(self, c):

        """Initialize rclick functionality for this commander.

        This only initializes ivars, the proper setup must be done by calling the
        controllers onCreate method from the module level onCreate function. This is
        to make unit testing easier.

        """

        self.c = c

        self.mb_retval = None
        self.mb_keywords = None

        if hasattr(c.context_menus, 'default-iconbar-menu'):
            return

        items = [
            ('Add Bar', 'toolbar-add-iconbar'),
            ('Add Script-Button', 'toolbar-add-script-button'),
            ('-', ''),
            ('Hide', 'toolbar-hide-iconbar'),
            ('*', 'toolbar-show-iconbar-menu'),
        ]

        c.context_menus['default-iconbar-menu'] = items
    #@nonl
    #@+node:bobjack.20080424195922.14:onCreate
    def onCreate(self):

        c = self.c

        self.registerCommands()

        c.theToolbarController = self
    #@-node:bobjack.20080424195922.14:onCreate
    #@+node:bobjack.20080424195922.15:onClose
    def onClose(self):
        """Clean up and prepare to die."""

        return
    #@-node:bobjack.20080424195922.15:onClose
    #@+node:bobjack.20080424195922.16:createCommandCallbacks
    def createCommandCallbacks(self, commands):

        """Create command callbacks for the list of `commands`.

        Returns a list of tuples

            (command, methodName, callback)

        """

        lst = []
        for command in commands:

            methodName = command.replace('-','_')
            function = getattr(self, methodName)
            cm = self.c.theContextMenuController

            def cb(event, self=self, function=function):
                cm.mb_retval = function(cm.mb_keywords)

            lst.append((command, methodName, cb))

        return lst
    #@-node:bobjack.20080424195922.16:createCommandCallbacks
    #@+node:bobjack.20080424195922.17:registerCommands
    def registerCommands(self):

        """Create callbacks for minibuffer commands and register them."""

        c = self.c

        commandList = self.createCommandCallbacks(self.getCommandList())

        for cmd, methodName, function in commandList:
            c.k.registerCommand(cmd, shortcut=None, func=function)   
    #@-node:bobjack.20080424195922.17:registerCommands
    #@+node:bobjack.20080424195922.19:getCommandList
    def getCommandList(self):

        return self.commandList
    #@-node:bobjack.20080424195922.19:getCommandList
    #@-node:bobjack.20080424195922.13:__init__
    #@+node:bobjack.20080428114659.20:Generator Commands
    #@+node:bobjack.20080428114659.21:toolbar_show_iconbar_menu
    def toolbar_show_iconbar_menu(self, keywords):

        c = self.c
        frame = c.frame


        menu_table = keywords.get('rc_menu_table', None)

        barname = keywords.get('toolbar')

        names = frame.iconBars.keys()

        items = []
        while names:
            name = names.pop(0)

            if name == barname:
                continue

            bar = frame.iconBars[name]
            if not bar.visible:

                def show_iconbar_cb(c, keywords, bar=bar):
                    bar.show()

                items.append((name, show_iconbar_cb))

        if items:
            items = [('Show', items)]

        if menu_table is not None:
            menu_table[:0] = items  
    #@-node:bobjack.20080428114659.21:toolbar_show_iconbar_menu
    #@-node:bobjack.20080428114659.20:Generator Commands
    #@+node:bobjack.20080426190702.2:Invocation Commands
    #@+node:bobjack.20080426190702.3:toolbar_delete_button
    def toolbar_delete_button(self, keywords):
        """Minibuffer command to delete a toolbar button.

        For use only in rClick menus attached to toolbar buttons.

        """

        try:
            button = keywords['event'].widget
            self.c.theScriptingController.deleteButton(button)
        except:
            g.es('failed to delete button')    




    #@-node:bobjack.20080426190702.3:toolbar_delete_button
    #@+node:bobjack.20080428114659.11:toolbar_add_iconbar
    def toolbar_add_iconbar(self, keywords):
        """Minibuffer command to add a new iconBar."""

        c = self.c
        frame = c.frame

        try:
            bar = keywords.get('toolbar')
        except:
            bar = None

        name = ''
        if bar:
            name = bar.name

        if not name:
            name='iconbar'

        for i in range(1,100):
            newname = '%s.%s' %(name, i)
            if newname not in frame.iconBars:
                break

        frame.createIconBar(newname)






    #@-node:bobjack.20080428114659.11:toolbar_add_iconbar
    #@+node:bobjack.20080428114659.16:toolbar_hide_iconbar
    def toolbar_hide_iconbar(self, keywords):
        """Minibuffer command to hide an iconBar.

        This is only for use in context menus attached to iconBars.
        """

        c = self.c
        frame = c.frame

        g.trace()

        try:
            bar = keywords.get('toolbar')
        except:
            bar = None

        g.trace(bar)

        if not bar or not bar.name in frame.iconBars:
            return

        frame.iconBars[bar.name].hide()
    #@-node:bobjack.20080428114659.16:toolbar_hide_iconbar
    #@+node:bobjack.20080428114659.17:toolbar_add_script_button
    def toolbar_add_script_button(self, keywords):

        c = self.c
        frame = c.frame

        bar = keywords.get('toolbar')
        if not bar or bar.name not in frame.iconBars:
            return

        oldIconBar = frame.iconBar

        g.trace(bar.name)

        try:
            frame.iconBar = frame.iconBars[bar.name]
            sm = c.theScriptingController
            sm.createScriptButtonIconButton(bar.name) 
        finally:
            frame.iconBar = oldIconBar


    #@-node:bobjack.20080428114659.17:toolbar_add_script_button
    #@-node:bobjack.20080426190702.2:Invocation Commands
    #@-others

#@-node:bobjack.20080424195922.12:class pluginController
#@-others
#@-node:bobjack.20080424190315.2:@thin toolbar.py
#@-leo

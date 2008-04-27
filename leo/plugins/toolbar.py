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

    if not Tk:
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
#@+node:bobjack.20080425135232.6:class ToolbarScriptingController
scripting = mod_scripting.scriptingController
class ToolbarScriptingController(scripting):

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
    #@-others
#@-node:bobjack.20080425135232.6:class ToolbarScriptingController
#@+node:bobjack.20080426064755.66:class ToolbarTkIconBarClass
iconbar = leoTkinterFrame.leoTkinterFrame.tkIconBarClass
class ToolbarTkIconBarClass(iconbar):

    '''A class representing the singleton Icon bar'''

    iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

    #@    @+others
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
    #@+node:bobjack.20080426190702.2:Generator Commands
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
    #@-node:bobjack.20080426190702.2:Generator Commands
    #@-others

#@-node:bobjack.20080424195922.12:class pluginController
#@-others
#@-node:bobjack.20080424190315.2:@thin toolbar.py
#@-leo

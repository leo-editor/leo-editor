#@+leo-ver=4-thin
#@+node:bobjack.20080424190315.2:@thin toolbar.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:bobjack.20080424190906.12:<< docstring >>
#@@nocolor

"""A plugin to extend the functionality of Leo's iconbar.

This plugin provides mutltiple iconBars each of which can consist of a
number of slave iconBars.

Each iconBar is assigned a name, the default iconBar is called 'iconbar'. A
dictionary mapping names to iconBar objects is kept in *c.frame.iconBars* and
the default iconBar is also in *c.frame.iconBar*    


Any widget may be added to an iconBar but:

** ALL WIDGETS TO BE ADDED TO ICONBARS SHOULD HAVE c.frame.top AS THE PARENT. **

This will break some code but it can't be helped.

If widget.leoShow exists and is set to False then the widget will still be in
the list in its assigned packing order but it will not be seen. Any change to 
widget.leoShow must be followed by a call to bar.repackButtons() before the
change will take effect. 

enhanced @buttons nodes
-----------------------

iconBars
--------

Some convenience methods are availiable in c.frame, all of which can have
barName=<name of bar>. If no barName is supplied 'iconbar' will be used.

    createIconBar(barName='iconbar'):
        If an iconBar with barName already exists it will be returned, otherwise
        a new iconBar will be created, packed and returned.

    addIconButton(*args, **keys):
        creates and packs and returns an icon button. This is equivelent
        to addIconWidget(getIconButton)

    getIconButton(*args, **keys):
        creates and returns an icon button but does not pack it. Any barName
        will be ignored.

    addIconWidget(widget, barName='iconbar'):
        Adds any widget to the named iconBar.

The iconBars themsleves have the following public methods. Thes should be used
in preferenct to the above methods.

    getButton(*args, **keys)
        same as frame.getIconButton

    add(*args, **keys)
        same as frame.addIconButton

    repackButtons(buttons=None)

        if buttons is None then the current list of buttons is repacked.

        otherwise it must be a new list of buttons or other widgets to pack

    addWidget(widget, index=None, repack=True)

        Adds a widget to the list of widgets to be packed in this iconBar.

        repack is True by default causing repackButtons() to be called after
        adding the widget. If repack is set to False the script must call
        repackButtons() itself. Setting repack to False is usefull if you
        want to add several widgets, you can then call repackButtons() just
        once.

    removeWidget(widget, repack=True)
         removes the widget from the list and optionally repacks the iconBar.

    pack() aka show()
        Makes the toolbar visible if it is not already visible.

    unpack() aka hide()
        Makes the toolbar invisible if it was not already invisible.

The iconbars also have the following public properties.

    buttons:
        This provides a *copy* of the list of buttons/widgets contained in the toolbar.

        buttons = <list of widgets> is allowed and is the same as
        repackButtons(<list of widgets>)

        bar.buttons = bar.buttons[1:] is allowed and removes the first button

        but bar.buttons[1:] does nothing

    visible:
        tells if the bar is visible or not.

        visible = True | False hides or shows the toolbar. 
"""
#@-node:bobjack.20080424190906.12:<< docstring >>
#@nl

__version__ = "0.8"
__plugin_name__ = 'Toolbar Manager'
__plugin_id__ = 'Toolbar'

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
# O.4 bobjack:
#     - added support for multiple toolbars
# 0.5 bobjack:
#     - added toolbars overflow to other toolbars if they are
#       not wide enough to contain their buttons.
# 0.6 bobjack:
#     - refactoring
#     - make toolbar area collapse when no iconBars are visible
#     - add toggle-iconbar minibuffer / rClick menu command
#     - remove dependancy on rClick
#     - add drag drop in iconBars
# 0.7 bobjack:
#     - add support for leoDragHandle and leoDragMaster
# 0.8 bobjack:
#     - convert to use c.universallCallback via registerCommands( ... 
# wrap=True)
#     - seperate out icon and script button code and make these first class 
# objects
# 
# 
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
Pmw = g.importExtension("Pmw",pluginName=__name__,verbose=True,required=True)

try:
    from PIL import Image
    from PIL import ImageTk
except ImportError:
    Image = ImageTk = None

mod_scripting = g.importExtension('mod_scripting',pluginName=__name__,verbose=True,required=True)
import leoTkinterFrame
import leoTkinterTree
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
    ('commandList', (list, tuple)),
)
#@nonl
#@-node:bobjack.20080424195922.85:<< required ivars >>
#@nl

allowedButtonConfigItems = ('image', 'bg', 'fg', 'justify', 'padx', 'pady', 'relief', 'text', 'command', 'state')
iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')



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

    g.app.gui.ScriptingControllerClass = ToolbarScriptingController
    c.frame.iconBarClass = ToolbarTkIconBarClass
    leoTkinterFrame.leoTkinterTreeTab = ToolbarTkinterTreeTab

    if not hasattr(c.frame, 'iconBars'):
        c.frame.iconBars= {}
        c.frame.toolbarFrame = None
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
#@+node:bobjack.20080501055450.5:class ToolbarTkinterTreeTab
class ToolbarTkinterTreeTab (leoTkinterFrame.leoTkinterTreeTab):

    '''A class representing a tabbed outline pane drawn with Tkinter.'''

    #@    @+others
    #@+node:bobjack.20080501055450.8:tt.createControl
    def createControl (self):

        "Create and pack the Chapter Selector control."""

        tt = self ; c = tt.c

        # Create the main container.
        tt.frame = Tk.Frame(c.frame.top)

        # Create the chapter menu.
        self.chapterVar = var = Tk.StringVar()
        var.set('main')

        tt.chapterMenu = menu = Pmw.OptionMenu(tt.frame,
            labelpos = 'w', label_text = 'chapter',
            menubutton_textvariable = var,
            items = [],
            command = tt.selectTab,
        )
        menu.pack(side='left',padx=5)

        tt.frame.leoDragHandle = menu.component('label')

        c.frame.iconBar.addWidget(tt.frame)
    #@-node:bobjack.20080501055450.8:tt.createControl
    #@-others
#@nonl
#@-node:bobjack.20080501055450.5:class ToolbarTkinterTreeTab
#@+node:bobjack.20080428114659.2:class ToolbarTkinterFrame
class ToolbarTkinterFrame(leoTkinterFrame.leoTkinterFrame, object):

    #@    @+others
    #@+node:bobjack.20080429153129.29:Icon area convenience methods
    #@+node:bobjack.20080429153129.30:addIconButton
    def addIconButton (self,*args,**keys):

        """Create and add an icon button to the named toolbar.

        keys['barname'] gives the name of the toolbar to be uses if it is present
        outherwise 'iconbar' is used.

        """



        if 'barName' in keys:
            barName = keys['barName']
            del keys['barName']

        else:
             barName = 'iconbar'

        bar = self.createIconBar(barName)

        if bar:
            return bar.add(*args, **keys)
    #@-node:bobjack.20080429153129.30:addIconButton
    #@+node:bobjack.20080503151427.2:getIconButton
    def getIconButton (self,*args,**keys):

        """Create icon button but do not add it to a toolbar.

        keys['barname'] gives the name of the toolbar or the
        tollbar named 'iconbar' is used.

        """
        return self.iconBar.getButton(*args,**keys)

    createIconButton = getIconButton
    #@nonl
    #@-node:bobjack.20080503151427.2:getIconButton
    #@+node:bobjack.20080501055450.16:addIconWidget
    def addIconWidget (self, widget, barName='iconbar'):

        """Adds a widget to the named toolbar."""

        bar = self.createIconBar(barName)
        if bar:
            return bar.addWidget(widget)
    #@-node:bobjack.20080501055450.16:addIconWidget
    #@+node:bobjack.20080429153129.31:clearIconBar
    def clearIconBar (self, barName='iconbar'):

        """This removes all widgets from the named iconbar and calls their delete method."""

        self.iconBars[barName].clear()
    #@-node:bobjack.20080429153129.31:clearIconBar
    #@+node:bobjack.20080429153129.32:createIconBar
    def createIconBar (self, barName='iconbar',  slaveMaster=None):

        """Create and display new iconBar.

        If the iconbar exists it will be shown, if it is not shown already,
        and returned.

        Otherwise a new toolbar will be created, shown and returned.

        The bar will not be placed in self.iconBars if it is a slave bar.

        """

        frame = self.createToolbarFrame()

        if not barName in self.iconBars:

            bar = self.iconBarClass(
                self.c, frame, barName=barName, slaveMaster=slaveMaster
            )
            if not slaveMaster:
                self.iconBars[barName] = bar

        else:
            bar = self.iconBars[barName]

        if barName == 'iconbar':
            self.iconBar = bar

        return bar

    #@-node:bobjack.20080429153129.32:createIconBar
    #@+node:bobjack.20080429153129.33:getIconBar
    getIconBar = createIconBar
    #@nonl
    #@-node:bobjack.20080429153129.33:getIconBar
    #@+node:bobjack.20080429153129.34:getIconBarObject
    getIconBarObject = getIconBar
    #@nonl
    #@-node:bobjack.20080429153129.34:getIconBarObject
    #@+node:bobjack.20080429153129.35:hideIconBar
    def hideIconBar (self, barName='iconbar'):

        self.iconBars[barName].hide()
    #@-node:bobjack.20080429153129.35:hideIconBar
    #@-node:bobjack.20080429153129.29:Icon area convenience methods
    #@+node:bobjack.20080502134903.8:Properties
    #@+node:bobjack.20080502134903.9:getIconFrame
    def getIconFrame(self):

        try:
            return self.iconBar.iconFrame
        except Exception:
            pass

    def setIconFrame(self, value):
        pass

    iconFrame = property(getIconFrame, setIconFrame)
    #@-node:bobjack.20080502134903.9:getIconFrame
    #@-node:bobjack.20080502134903.8:Properties
    #@+node:bobjack.20080428114659.5:createToolbarFrame
    def createToolbarFrame(self):

        """Create and pack the frame that contains all the toolbars.

        If the frame already exists return it or create, pack and return
        a new frame.

        """

        if self.toolbarFrame:
            return self.toolbarFrame

        self.toolbarFrame = w = Tk.Frame(self.outerFrame)
        self.dummyToolbarFrame = Tk.Frame(w, height='1p')

        w.pack(fill='x')

        return self.toolbarFrame
    #@-node:bobjack.20080428114659.5:createToolbarFrame
    #@-others

#@-node:bobjack.20080428114659.2:class ToolbarTkinterFrame
#@+node:bobjack.20080506182829.14:class ToolbarIconFrame
class ToolbarIconFrame(object):

   #@   @+others
   #@+node:bobjack.20080506182829.15:__init__
   def __init__(c, top=None):

       self.c = c

       self.top = top or Tk.Frame(c.frame.top)


   #@-node:bobjack.20080506182829.15:__init__
   #@-others
#@-node:bobjack.20080506182829.14:class ToolbarIconFrame
#@+node:bobjack.20080506182829.16:class ToolbarIconButton
class ToolbarIconButton(Tk.Button, object):

    """
    text
    command
    shortcut
    statusLine, balloon, balloonText, tooltip
    bg, fg
    menu,
    imagefile, image, icon
    command
    font
    item_data
    """

    #@    @+others
    #@+node:bobjack.20080506182829.24:__init__
    def __init__(self, c, cnf={}, **keys ):

        """Create an iconBar button.

        cnf must be a dictionary if it is supplied at all.


        """
        if 0:
            print 'ToolbarIconButton.__init__'
            print '\t', cnf
            print '\t', keys

        self.c = c
        self.deleteOnRightClick = False
        self.balloonEnabled = False
        self.balloon = None

        self.keys = keys = self.mergeConfigSources(cnf, keys)

        #@    << setup menu >>
        #@+node:bobjack.20080507053105.4:<< setup menu >>
        if 'menu' in keys:
            self.context_menu = keys['menu']
            del keys['menu']
        #@nonl
        #@-node:bobjack.20080507053105.4:<< setup menu >>
        #@nl
        #@    << setup statusLine >>
        #@+node:bobjack.20080507053105.5:<< setup statusLine >>
        value = ''
        for key in ('statusLine', 'balloonText', 'balloon', 'tooltip'):
            if key in keys:
                s = keys[key]
                if s:
                    value = s
                del keys[key]

        self.statusLine = value

        if self.balloonEnabled and self.statusLine:
            self.createBalloon()
        #@-node:bobjack.20080507053105.5:<< setup statusLine >>
        #@nl
        #@    << setup image and relief >>
        #@+node:bobjack.20080506182829.31:<< setup image and relief >>


        imagefile = keys.get('imagefile')
        image = keys.get('image')
        icon = keys.get('icon')

        # for key in ('imagefile', 'image', 'icon'):
            # try:
                # del keys[key]
            # except KeyError:
                # pass

        if icon:
            imagefile = icon

        if not image and imagefile:
            image = self.getImage(imagefile)

        if image:
            keys['image'] = image
            keys['bd'] = 0
            if 'bg' not in keys:
                # get background of toolbar FIXME:
                pass
            keys['relief'] = 'flat'
            keys['image'] = image
        else:
            keys['relief'] = 'groove'
        #@-node:bobjack.20080506182829.31:<< setup image and relief >>
        #@nl
        #@    << setup command >>
        #@+node:bobjack.20080506182829.32:<< setup command >>
        command = keys.get('command')
        commandCallback = command

        if not command:
            def commandCallback():
                print "command for widget %s" % self

        elif isinstance(command, basestring):
            def commandCallback(c=self.c, command=command):
                c.executeMinibufferCommand(command)

        keys['command'] = commandCallback
        #@-node:bobjack.20080506182829.32:<< setup command >>
        #@nl
        #@    << setup font >>
        #@+node:bobjack.20080506182829.33:<< setup font >>

        if not hasattr(self, 'font'):
            self.font = None

        self.font = keys.get('font') or self.font or \
            self.c.config.getFontFromParams(
                "button_text_font_family", "button_text_font_size",
                "button_text_font_slant",  "button_text_font_weight",
            )

        keys['font'] = self.font
        #@-node:bobjack.20080506182829.33:<< setup font >>
        #@nl

        if 'bg' in keys and not keys['bg']:
            del keys['bg'] 

        kws = self.getButtonConfig(keys)    
        Tk.Button.__init__(self, c.frame.top, **kws)


        self.bind('<Button-3>', self.onRightClick)


    #@-node:bobjack.20080506182829.24:__init__
    #@+node:bobjack.20080507175534.2:attatchWidget
    def attatchWidget(self, bar='iconbar', index=None, createBar=True, showBar=True):

        """Attatach a widget to a bar.

        index:
            where to place the widget in the bar
        bar:
            The bar may be an iconbar object or the name of an iconBar.

        createBar:
            If bar is a sring and no bar with that name exists, then if this
            is True a new bar will be created.

        showBar:
            If the bar has been created then it will be shown if showBar == True

        """ 
        pass      
    #@+at            
    #     # TODO: not ready yet
    # 
    #     try:
    #         oldbar = self.leoIconBar
    #     except:
    #         oldbar = None
    # 
    #     if oldbar:
    #         oldbar.removeWidget(self)
    # 
    #     if isinstance(bar, basestring):
    #         bar = bar
    #         bar.addWidget(self)
    # 
    # 
    #@-at
    #@-node:bobjack.20080507175534.2:attatchWidget
    #@+node:bobjack.20080507175534.3:createBalloon (gui-dependent)
    def createBalloon (self, delay=100):

        'Create a balloon for a widget.'

        if not self.balloon:
            self.balloon = Pmw.Balloon(self, initwait=delay)


        self.balloon.bind(self, self.statusLine)
    #@-node:bobjack.20080507175534.3:createBalloon (gui-dependent)
    #@+node:bobjack.20080507053105.7:detatchWidget
    def detatchWidget(self):

        try:
            bar = self.leoIconBar
        except:
            bar = None

        if bar:
            self.leoIconBar.removeWidget(self)
    #@-node:bobjack.20080507053105.7:detatchWidget
    #@+node:bobjack.20080506182829.30:getImage
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

        iconpath = g.os_path_join(iconBasePath, path)

        try:
            return self.iconCache[iconpath]
        except KeyError:
            pass

        try:
            image = Image.open(path)
        except Exception:
            image = None

        if not image:

            try:
                image = Image.open(iconpath)
            except Exception:
                image = None

        if not image:
            return None

        try:    
            image = ImageTk.PhotoImage(image)
        except Exception:
            image = None

        if not image or not image.height():
            g.es('Bad Toolbar Icon: %s' % path)
            return None

        self.iconCache[path] = image

        return image

    #@-node:bobjack.20080506182829.30:getImage
    #@+node:bobjack.20080508051801.5:getButtonConfig
    def getButtonConfig(self, keys=None):

        """Select keys and values to pass on to Tk.Button."""

        if keys is None:
            keys = self.keys

        #print 'Items sent to Tk.Button'

        haveKeys = set(keys.keys())
        allowedKeys = set(allowedButtonConfigItems)

        sendkeys = [ k for k in haveKeys & allowedKeys]

        kws = {}
        for k in sendkeys:
            if isinstance(k, unicode):
                k = k.encode()
            kws[k] = keys[k]

        return kws
    #@-node:bobjack.20080508051801.5:getButtonConfig
    #@+node:bobjack.20080507053105.9:mergeConfigSources
    def mergeConfigSources(self, cnf, keys):

        """Merge and prioritize config sources.

        config sources are dictionaries cnf, keys and keys['item_data']

        Priority cnf < keys < item_data.
        """

        if 0:
            g.trace()
            print '\t', cnf
            print '\t', keys

        if cnf:
            for key, value in keys.iteritems():
                cnf[key] = value
            keys = keys = cnf

        if 'item_data' in keys:
            data = keys['item_data']
            del keys['item_data']
        else:
            data = {}

        self.item_data = data

        if data:
            for key, value in data.iteritems():
                keys[key] = value

        return keys
    #@-node:bobjack.20080507053105.9:mergeConfigSources
    #@+node:bobjack.20080507053105.6:onRightClick
    def onRightClick(self, event):

        try:
            menu = self.context_menu
        except Exception:
            menu = None

        if g.doHook('rclick-popup',
            c=self.c, event=event,
            button=self,
        ):
            return

        if self.deleteOnRightClick:
            self.deleteButton()

    #@-node:bobjack.20080507053105.6:onRightClick
    #@+node:bobjack.20080508051801.6:deleteButton
    def deleteButton(self, event=None):

        """Delete the given button.

        This method does not actually delete the button, override the method
        in derived classes to do that.

        """

        self.detatchWidget()

    #@-node:bobjack.20080508051801.6:deleteButton
    #@+node:bobjack.20080508051801.7:setCommand
    def setCommand(self, command):


        commandCallback = command

        if not command:
            def commandCallback():
                print "command for widget %s" % self

        if isinstance(command, basestring):

            def commandCallback(event, command=command):
                return self.c.executeMinibufferCommand(command)

        self.config(command=commandCallback) 
    #@-node:bobjack.20080508051801.7:setCommand
    #@-others
#@-node:bobjack.20080506182829.16:class ToolbarIconButton
#@+node:bobjack.20080506182829.18:class ToolbarScriptButton
class ToolbarScriptButton(ToolbarIconButton):

    #@    @+others
    #@+node:bobjack.20080506182829.19:__init__
    def __init__(self, c, cnf={}, **keys):

        self.c = c
        k = c.k

        keys = self.mergeConfigSources(cnf, keys)

        text = keys.get('text')
        #@    << command name >>
        #@+node:bobjack.20080507053105.11:<< command name >>
        self.commandName = commandName = self.cleanButtonText(text).lower()
        #@nonl
        #@-node:bobjack.20080507053105.11:<< command name >>
        #@nl
        #@    << truncate text >>
        #@+node:bobjack.20080507053105.10:<< truncate text >>

        self.truncatedText = truncatedText = self.truncateButtonText(commandName)
        keys['text'] = truncatedText
        #@-node:bobjack.20080507053105.10:<< truncate text >>
        #@nl
        #@    << register commands >>
        #@+node:bobjack.20080507053105.12:<< register commands >>
        deleteCommandName= 'delete-%s-button' % commandName

        k.registerCommand(deleteCommandName, shortcut=None,
            func=self.deleteButton, pane='button', verbose=False
        )

        shortcut = keys.get('shortcut')
        k.registerCommand( commandName,
            shortcut=shortcut,
            func=lambda event: self.invoke(),
            pane='button',
            verbose=shortcut,
        )
        #@nonl
        #@-node:bobjack.20080507053105.12:<< register commands >>
        #@nl

        ToolbarIconButton.__init__(self, c, keys)

        self.deleteOnRightClick = True

        self.baloonEnabled = True
        self.createBalloon()



    #@-node:bobjack.20080506182829.19:__init__
    #@+node:bobjack.20080507053105.13:Properties
    #@+node:bobjack.20080507175534.4:baloonEnabled


    #@-node:bobjack.20080507175534.4:baloonEnabled
    #@+node:bobjack.20080507053105.15:maxButtonSize
    def getMaxButtonSize(self):

        return self.c.theScriptingController.maxButtonSize

    maxButtonSize = property(getMaxButtonSize)
    #@-node:bobjack.20080507053105.15:maxButtonSize
    #@+node:bobjack.20080507053105.14:scriptingController
    def getScriptingController(self):

        return self.c.theScriptingController

    scriptingController = property(getScriptingController)
    #@-node:bobjack.20080507053105.14:scriptingController
    #@-node:bobjack.20080507053105.13:Properties
    #@+node:bobjack.20080506182829.36:cleanButtonText
    def cleanButtonText (self,s):

        '''Clean the text following @button or @command so that it is a valid name of a minibuffer command.'''

        import string

        # Strip @...@button.
        while s.startswith('@'):
            s = s[1:]
        if g.match_word(s,0,'button'):
            s = s[6:]
        i = s.find('@key')
        if i != -1:
            s = s[:i].strip()
        if 1: # Not great, but spaces, etc. interfere with tab completion.
            chars = g.toUnicode(string.letters + string.digits,g.app.tkEncoding)
            aList = [g.choose(ch in chars,ch,'-') for ch in g.toUnicode(s,g.app.tkEncoding)]
            s = ''.join(aList)
            s = s.replace('--','-')
        while s.startswith('-'):
            s = s[1:]
        while s.endswith('-'):
            s = s[:-1]
        return s
    #@-node:bobjack.20080506182829.36:cleanButtonText
    #@+node:bobjack.20080506182829.37:truncateButtonText
    def truncateButtonText (self,s, size=0):

        if not size:
            size = self.maxButtonSize

        size = max(size, 1)

        s = s[:size]
        if s.endswith('-'):
            s = s[:-1]
        return s.strip()
    #@-node:bobjack.20080506182829.37:truncateButtonText
    #@+node:bobjack.20080426064755.77:deleteButton
    def deleteButton(self, event=None):

        """Delete the given button.

        This is called from callbacks, it is not a callback.

        """

        super(self.__class__, self).deleteButton(event)

        self.scriptingController.deleteButton(self)
    #@nonl
    #@-node:bobjack.20080426064755.77:deleteButton
    #@-others


#@-node:bobjack.20080506182829.18:class ToolbarScriptButton
#@+node:bobjack.20080506182829.20:class ToolbarAddScriptButton
class ToolbarAddScriptButton(ToolbarScriptButton):

    #@    @+others
    #@+node:bobjack.20080506182829.21:__init__
    def __init__(self, c, *args, **kw):

        super(ToolbarAddScriptButton, self).__init__(c, *args, **kw)
    #@-node:bobjack.20080506182829.21:__init__
    #@-others
#@-node:bobjack.20080506182829.20:class ToolbarAddScriptButton
#@+node:bobjack.20080425135232.6:class ToolbarScriptingController
scripting = mod_scripting.scriptingController
class ToolbarScriptingController(scripting, object):

    #@    @+others
    #@+node:bobjack.20080506182829.12:createAtButtonFromSettingHelper & callback
    def createAtButtonFromSettingHelper (self,h,script,statusLine,shortcut,bg='LightSteelBlue2'):

        '''Create a button from an @button node.

        - Calls createIconButton to do all standard button creation tasks.
        - Binds button presses to a callback that executes the script.
        '''

        c = self.c
        k = c.k

        buttonText = self.cleanButtonText(h)

        data = self.getItemData(script)

        if data and 'tooltip' in data:
            statusLine = data['tooltip']


        # We must define the callback *after* defining b,
        # so set both command and shortcut to None here.

        b = self.createIconButton(
            text=h,
            command=None,
            shortcut=None,
            statusLine=statusLine,
            bg=bg,
            item_data=data,
        )

        if not b:
            return None

        # Now that b is defined we can define the callback.
        # Yes, the callback *does* use b (to delete b if requested by the script).

        def atSettingButtonCallback (
            event=None,
            self=self,
            b=b,
            script=script,
            buttonText=buttonText
        ):
            self.executeScriptFromSettingButton (b,script,buttonText)

        self.iconBar.setCommandForButton(b,atSettingButtonCallback)

        # At last we can define the command and use the shortcut.
        k.registerCommand(buttonText.lower(),
            shortcut=shortcut,func=atSettingButtonCallback,
            pane='button',verbose=False)

        return b
    #@+node:bobjack.20080506182829.13:executeScriptFromSettingButton
    def executeScriptFromSettingButton (self,b,script,buttonText):

        '''Called from callbacks to execute the script in node p.'''

        c = self.c

        if c.disableCommandsMessage:
            g.es(c.disableCommandsMessage,color='blue')
        else:
            g.app.scriptDict = {}
            c.executeScript(script=script,silent=True)
            # Remove the button if the script asks to be removed.
            if g.app.scriptDict.get('removeMe'):
                g.es("Removing '%s' button at its request" % buttonText)
                b.deleteButton()

        if 0: # Do *not* set focus here: the script may have changed the focus.
            c.frame.bodyWantsFocus()
    #@nonl
    #@-node:bobjack.20080506182829.13:executeScriptFromSettingButton
    #@-node:bobjack.20080506182829.12:createAtButtonFromSettingHelper & callback
    #@+node:bobjack.20080508051801.2:createAtButtonHelper & callback
    def createAtButtonHelper (self,p,h,statusLine,shortcut,bg='LightSteelBlue1',verbose=True):

        '''Create a button from an @button node.

        - Calls createIconButton to do all standard button creation tasks.
        - Binds button presses to a callback that executes the script in node p.
        '''
        c = self.c ; k = c.k

        item_data = self.getItemData(p.bodyString())

        buttonText = self.cleanButtonText(h)



        b = self.createIconButton(
            text=h,
            command=None,
            shortcut=None,
            statusLine=statusLine,
            bg=bg,
            item_data=item_data
        )

        if not b:
            return None

        def atButtonCallback (
            event=None,
            self=self,
            p=p.copy(),
            b=b,
            buttonText=buttonText
        ):
            self.executeScriptFromButton (p,b,buttonText)

        b.setCommand(atButtonCallback)

        # At last we can define the command and use the shortcut.
        k.registerCommand(buttonText.lower(),
            shortcut=shortcut,func=atButtonCallback,
            pane='button',verbose=verbose)

        return b
    #@+node:bobjack.20080508051801.3:executeScriptFromButton
    def executeScriptFromButton (self,p,b,buttonText):

        '''Called from callbacks to execute the script in node p.'''

        c = self.c

        if c.disableCommandsMessage:
            g.es(c.disableCommandsMessage,color='blue')
        else:
            g.app.scriptDict = {}
            c.executeScript(p=p,silent=True)
            # Remove the button if the script asks to be removed.
            if g.app.scriptDict.get('removeMe'):
                g.es("Removing '%s' button at its request" % buttonText)
                b.deleteButton()

        if 0: # Do *not* set focus here: the script may have changed the focus.
            c.frame.bodyWantsFocus()
    #@nonl
    #@-node:bobjack.20080508051801.3:executeScriptFromButton
    #@-node:bobjack.20080508051801.2:createAtButtonHelper & callback
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


        return item_data
    #@-node:bobjack.20080425135232.10:getItemData
    #@+node:bobjack.20080428114659.18:getIconBar
    def getIconBar(self):

        return self.c.frame.iconBar


    def setIconBar(*args, **kw):
        pass

    iconBar = property(getIconBar, setIconBar)
    #@-node:bobjack.20080428114659.18:getIconBar
    #@+node:bobjack.20080430160907.2:createIconButton

    def createIconButton (self,text,command,shortcut,statusLine,bg, **keys):

        '''Create an icon button.  All icon buttons get created using this utility.

        - Creates the actual button and its balloon.
        - Adds the button to buttonsDict.
        - Registers command with the shortcut.
        - Creates x amd delete-x-button commands, where x is the cleaned button name.
        - Binds a right-click in the button to a callback that deletes the button.'''

        c = self.c ; k = c.k

        cnf = {}
        for k, v in (
            ('text', text),
            ('command', command),
            ('shortcut', shortcut),
            ('statusLine', statusLine),
            ('bg', bg)
        ):
            cnf[k] = v

        b = ToolbarScriptButton(c, cnf, **keys)

        self.buttonsDict[b] = b.truncatedText
        self.iconBar.addWidget(b)
        return b
    #@-node:bobjack.20080430160907.2:createIconButton
    #@+node:bobjack.20080428114659.12:createScriptButtonIconButton 'script-button' & callback
    def createScriptButtonIconButton (self, barName='iconbar'):

        '''Create the 'script-button' button and the script-button command.'''

        c = self.c
        frame = c.frame


        b = self.createIconButton(
            text='script-button',
            command = None,
            shortcut=None,
            statusLine='Make script button from selected node',
            bg="#ffffcc",
        )

        def addScriptButtonCallback(event=None, self=self, b=b):
            return self.addScriptButtonCommand(event, b)

        b.configure(command=addScriptButtonCallback)
    #@+node:bobjack.20080428114659.13:addScriptButtonCommand
    def addScriptButtonCommand (self,event=None, b=None):

        """Convert the node into a script button and add it to an iconBar.

        b is the add-script-button that was clicked and the new script button
        will be added to the same iconBar.

        """ 

        c = self.c
        frame = c.frame
        p = c.currentPosition();
        h = p.headString()

        buttonText = self.getButtonText(h)
        shortcut = self.getShortcut(h)
        statusLine = "Run Script: %s" % buttonText
        if shortcut:
            statusLine = statusLine + "\@key=" + shortcut

        oldIconBar = frame.iconBar
        try:
            frame.iconBar =  b.leoIconBar       
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

    '''A class representing an iconBar.'''

    iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

    #@    @+others
    #@+node:bobjack.20080428114659.6:__init__
    def __init__(self, c, parentFrame, barName='iconBar', slaveMaster=None):

        """Initialize an iconBar."""

        self.c = c
        self.barName = barName    
        self.parentFrame = parentFrame

        self.inConfigure = False

        self.slaveMaster = slaveMaster
        self.slaveBar = None


        self.buttonCount = 0

        self.font = None

        self.inConfigure = False

        if not slaveMaster :
            #@        << define master iconBar stuff >>
            #@+node:bobjack.20080502134903.2:<< define master iconBar stuff >>
            # These are only valid for the first iconBar in a group of slaves.

            self._outerFrame = None     # control var for outerFrame property
            self._buttons = []          # control var for buttons list

            self.maxSlaves = 15
            self.nSlaves = 1 

            # The frame which will contain all slave iconBars
            self._outerFrame = w = Tk.Frame(
                self.parentFrame,          
                height="5m", bd=2, relief="groove"
            )
            w.leoIconBar = self


            #@-node:bobjack.20080502134903.2:<< define master iconBar stuff >>
            #@nl

        # Create the frame to hold buttons assigned to this slave bar.

        self.iconFrame = w = Tk.Frame(
            self.parentFrame,          
            height="5m",relief="flat",
        )
        w.leoIconBar = self
        w.bind('<Button-3>', self.onRightClick)
        w.bind('<Configure>', self.onConfigure)

        self.show()
        c.frame.top.update_idletasks()

    #@-node:bobjack.20080428114659.6:__init__
    #@+node:bobjack.20080508125414.5:Event Handlers
    #@+node:bobjack.20080428114659.9:onRightClick
    def onRightClick(self, event):

        """Respond to a right click on any of the components of the toolbar.

        The first bar in a list of bars is provided sent with through the hook, 
        the actual bar can be found in event.widget.
        """

        g.doHook('rclick-popup', c=self.c, event=event,
            context_menu='default-iconbar-menu', bar=self.barHead
        )
    #@-node:bobjack.20080428114659.9:onRightClick
    #@+node:bobjack.20080503090121.5:onPress
    def onPress(self, e):

        w = e.widget

        w = self.getDragMaster(w)

        try:
            flag = w.leoIconBar
        except AttributeError:
            flag = False

        if flag:
            self.c.theToolbarController.grabWidget = w

        try:
            w.balloon._leave(e)
        except Exception:
            pass

    #@-node:bobjack.20080503090121.5:onPress
    #@+node:bobjack.20080503090121.6:onRelease
    def onRelease(self, e):

        try:
            c = self.c
            controller = c.theToolbarController

            target = e.widget.winfo_containing(e.x_root, e.y_root)

            try:
                target = self.getDragMaster(target)
                tBar = target.leoIconBar
            except:
                tBar = None

            if tBar:
                source = controller.grabWidget

                if source and source is not target:
                    sBar = source.leoIconBar

                    if sBar.c is tBar.c:
                        sBar.removeWidget(source)
                        try:
                            index = tBar.buttons.index(target)
                        except:
                            index = None  
                        tBar.addWidget(source, index)

        finally:
            controller.grabWidget = None
    #@-node:bobjack.20080503090121.6:onRelease
    #@+node:bobjack.20080429153129.16:onConfigure
    def onConfigure(self, event=None):

        self.repackButtons()



    #@-node:bobjack.20080429153129.16:onConfigure
    #@+node:bobjack.20080506182829.2:getDragMaster
    def getDragMaster(self, w):

        if hasattr(w, 'leoDragMaster'):
            w = w.leoDragMaster

        return w
    #@-node:bobjack.20080506182829.2:getDragMaster
    #@-node:bobjack.20080508125414.5:Event Handlers
    #@+node:bobjack.20080430160907.4:Properties
    #@+node:bobjack.20080430160907.5:outerFrame
    def getOuterFrame(self):

        """Get the frame that contains this bar and its companion slaves."""

        return self.barHead._outerFrame

    def setOuterFrame(self, value):

       self.barHead._outerFrame = value

    outerFrame = property(getOuterFrame, setOuterFrame)
    #@-node:bobjack.20080430160907.5:outerFrame
    #@+node:bobjack.20080430064145.4:barHead
    def getBarHead(self):

        """Get the first bar for the list of bars of which this bar is a member."""

        bar = self
        while bar.slaveMaster:
            bar = bar.slaveMaster

        return bar

    barHead = property(getBarHead)

    #@-node:bobjack.20080430064145.4:barHead
    #@+node:bobjack.20080501113939.2:slaveBars

    def getSlaveBars(self):

        """Get a list of slave iconBars packed in this toolbar."""

        return [ bar.leoIconBar for bar in self.outerFrame.pack_slaves()]

    slaveBars = property(getSlaveBars)
    #@nonl
    #@-node:bobjack.20080501113939.2:slaveBars
    #@+node:bobjack.20080502134903.7:slaveBarFrames
    def getSlaveBarFrames(self):

        """Get a list of slave iconBar frames packed in this toolbar."""

        return [ bar for bar in self.outerFrame.pack_slaves()]

    slaveBarFrames = property(getSlaveBarFrames)
    #@nonl
    #@-node:bobjack.20080502134903.7:slaveBarFrames
    #@+node:bobjack.20080501055450.2:slaveButtons
    def getSlaveButtons(self):

        """Get a list of widgets packed in this iconBar."""

        return [ btn for btn in self.iconFrame.pack_slaves()]


    slaveButtons = property(getSlaveButtons)
    #@-node:bobjack.20080501055450.2:slaveButtons
    #@+node:bobjack.20080501113939.3:allSlaveButtons
    def getAllSlaveButtons(self,  shrink=False):

        """Make a list of all widgets packed in this set of toolbars."""

        buttons = []
        bar = self.barHead
        while bar:
            buttons += [ btn for btn in bar.iconFrame.pack_slaves()]
            bar = bar.slaveBar

        return buttons 

    allSlaveButtons = property(getAllSlaveButtons)
    #@-node:bobjack.20080501113939.3:allSlaveButtons
    #@+node:bobjack.20080501125812.5:buttons
    def getButtons(self):

        """Get the list of widgets that may appear in this toolbar."""

        return self.barHead._buttons[:]

    def setButtons(self, lst):

        """Set a new list of widgets to be displayed in this toolbar."""

        if not lst:
            lst = []
        self.repackButtons(lst)
        return

    buttons = property(getButtons, setButtons)
    #@-node:bobjack.20080501125812.5:buttons
    #@+node:bobjack.20080501181134.5:visible
    def getVisible(self):

        """Is the toolbar, of which this iconBar is a slave, packed."""

        barHead = self.barHead
        return barHead._outerFrame in barHead.parentFrame.pack_slaves()

    def setVisible(self, show):

        if show:
            self.show()
        else:
            self.hide()

    visible = property(getVisible, setVisible)
    #@-node:bobjack.20080501181134.5:visible
    #@-node:bobjack.20080430160907.4:Properties
    #@+node:bobjack.20080504034903.9:updateButtons
    def updateButtons(self, buttons, repack=True):

        """Update the iconBars button list to match buttons.

        Buttons no longer needed are removed, new buttons are added.

        """

        old = set(self.barHead._buttons)
        new = set(buttons)

        unchanged = old & new

        remove = old - new
        add = new -old

        for btn in remove:
            self.removeWidget(btn, repack=False)

        for btn in add:
            self.addWidget(btn, repack=False)

        self.barHead._buttons = buttons[:]

        if repack:
            self.repackButtons()
    #@-node:bobjack.20080504034903.9:updateButtons
    #@+node:bobjack.20080507083323.4:repackButons
    def repackButtons(self, buttons=None):

        bar = self.barHead

        if bar.inConfigure:
           return

        if buttons is not None:
            self.updateButtons(buttons, repack=False)

        try:
            bar.doRepackButtons()
        finally:
            bar.inConfigure = False
    #@+node:bobjack.20080430160907.12:doRepackButtons
    def doRepackButtons(self, trace=None):

        """Repack all the buttons in this toolbar.

        New slave iconBars will be created if needed to make sure all buttons are
        visible. Empty slaves will be hidden but not removed.

        """
        barHead = self.barHead
        barHead.inConfigure = True

        orphans = barHead._buttons[:]

        #@    << unpack all buttons >>
        #@+node:bobjack.20080501181134.2:<< unpack all buttons >>
        bar = barHead
        while bar and bar.buttonCount:
            [ btn.pack_forget() for btn in bar.iconFrame.pack_slaves()]
            bar.buttonCount = 0
            bar = bar.slaveBar

        #barHead.iconFrame.update_idletasks()

        #@-node:bobjack.20080501181134.2:<< unpack all buttons >>
        #@nl

        bar = barHead
        bars = bar.slaveBars

        #@    << repack all widgets >>
        #@+node:bobjack.20080502134903.4:<< repack all widgets >>

        while bar and orphans:
            orphans = bar.repackHelper(orphans)
            if bar not in bars and (bar.buttonCount or not bar.slaveMaster):
                bar.packSlaveBar()
            bar = bar.slaveBar
        #@nonl
        #@-node:bobjack.20080502134903.4:<< repack all widgets >>
        #@nl
        #@    << hide empty slave bars >>
        #@+node:bobjack.20080502134903.5:<< hide empty slave bars >>
        while bar :
            if bar in bars:
                bar.unpackSlaveBar()
            bar = bar.slaveBar
        #@-node:bobjack.20080502134903.5:<< hide empty slave bars >>
        #@nl
    #@+node:bobjack.20080429153129.24:repackHelper
    def repackHelper(self, orphans):

        """Pack as many 'orphan' buttons into this bar as possible

        Return a list of orphans that could not be packed.

        """

        iconFrame = self.iconFrame
        req = iconFrame.winfo_reqwidth
        actual = iconFrame.winfo_width

        while orphans:
            #@        << pack widgets untill full >>
            #@+node:bobjack.20080502134903.6:<< pack widgets untill full >>
            widget = orphans[0]

            try:
                show = widget.leoShow
            except Exception:
                widget.leoShow = show = True

            if show:
                widget.pack(in_=iconFrame, side="left")
                iconFrame.update_idletasks()

                if req() > actual():
                    #widget.pack_forget()
                    break

                self.buttonCount += 1

            orphans.pop(0)

            #@-node:bobjack.20080502134903.6:<< pack widgets untill full >>
            #@nl

        if len(orphans) and not self.buttonCount:
            # we must pack at least one widget even if its too big
            widget = orphans.pop(0)
            widget.pack(in_=iconFrame, side="left")
            self.buttonCount = 1

        if not self.slaveBar and orphans:
            self.slaveBar = self.createSlaveBar()

        return orphans

    #@-node:bobjack.20080429153129.24:repackHelper
    #@+node:bobjack.20080430064145.3:createSlaveBar
    def createSlaveBar(self):

        """Create a slave iconBar for this bar and home as many orphans as possible.

        It is an error to call this if the bar already has a slaveBar.
        """

        assert not self.slaveBar, 'Already have a slaveBar.'

        barHead = self.barHead
        if not barHead.nSlaves < barHead.maxSlaves:
            return
        barHead.nSlaves +=1

        barName = self.uniqueSlaveName()

        self.slaveBar = slaveBar = self.c.frame.createIconBar(
            barName, slaveMaster=self
        )

        return slaveBar 
    #@-node:bobjack.20080430064145.3:createSlaveBar
    #@-node:bobjack.20080430160907.12:doRepackButtons
    #@-node:bobjack.20080507083323.4:repackButons
    #@+node:bobjack.20080503151427.3:add
    def add(self,*args,**keys):
        """Create and pack an iconBar button."""

        return self.addWidget(self.getButton(*args, **keys))


    #@-node:bobjack.20080503151427.3:add
    #@+node:bobjack.20080430160907.11:addWidget
    def addWidget(self, widget, index=None, repack=True):

        """Add a widget to the iconBar.

        The widget must have c.frame.top as it parent.

        If the widget is already attached to an iconBar it will
        first be removed

        """

        try:
            #@        << remove from current bar >>
            #@+node:bobjack.20080508125414.13:<< remove from current bar >>
            try:
                bar = widget.leoIconBar
            except:
                bar = None

            if bar:
                bar.removeWidget(widget, repack=False)
            #@nonl
            #@-node:bobjack.20080508125414.13:<< remove from current bar >>
            #@nl

            barHead = self.barHead
            buttons = barHead._buttons

            #@        << validate index >>
            #@+node:bobjack.20080508125414.12:<< validate index >>
            if index is not None:
                try:
                    idx = int(index)
                except:
                    idx = None

                if idx is None:
                    if index in buttons:
                        idx = buttons.index(index)

                index = idx

                if index is None: g.es('Icon Bar index out of range')




            #@-node:bobjack.20080508125414.12:<< validate index >>
            #@nl

            #@        << bind widget and drag handles >>
            #@+node:bobjack.20080506090043.2:<< bind widget and drag handles >>

            widget.bind('<ButtonPress-1>', barHead.onPress)
            widget.bind('<ButtonRelease-1>', barHead.onRelease)

            try:
                drag = widget.leoDragHandle

            except AttributeError:
                drag = None

            if drag:
                if not isinstance(drag, (tuple, list)):
                    drag = (drag,)

                for dw in drag:

                    dw.leoSubWindow = True
                    dw.leoDragMaster = widget

                    dw.bind('<ButtonPress-1>', barHead.onPress )
                    dw.bind('<ButtonRelease-1>', barHead.onRelease)

            widget.c = self.c
            widget.leoIconBar = barHead
            #@-node:bobjack.20080506090043.2:<< bind widget and drag handles >>
            #@nl

            if index is not None:
                try:
                   buttons.insert(index, widget)
                except IndexError:
                    index = None

            if index is None:
                buttons.append(widget)

            if repack:
                self.repackButtons()

        finally:
            return widget

    #@-node:bobjack.20080430160907.11:addWidget
    #@+node:bobjack.20080501181134.3:removeWidget
    def removeWidget(self, widget, repack=True):

        """Remove widget from the list of manged widgets and repack the buttons."""

        try:
            barHead = self.barHead

            barHead._buttons.remove(widget)

            #@        << unbind widget and drag handles >>
            #@+node:bobjack.20080506090043.3:<< unbind widget and drag handles >>
            widget.unbind('<ButtonPress-1>')
            widget.unbind('<ButtonRelease-1>')

            try:
                drag = widget.leoDragHandlle
            except AttributeError:
                drag = None

            if drag:
                if not isinstance(drag, (tuple, list)):
                    drag = (drag,)

                for dragWidget in drag:
                    try:
                        del dw.leoSubWindow
                        del dw.leoDragMaster
                        dw.unbind('<ButtonPress-1>')
                        dw.unbind('<ButtonRelease-1>')
                    except AttributeError:
                        g.es_exception()

            #@-node:bobjack.20080506090043.3:<< unbind widget and drag handles >>
            #@nl

            widget.leoIconBar = None

            if repack:
                self.repackButtons()

        finally:
            pass

            return widget
    #@-node:bobjack.20080501181134.3:removeWidget
    #@+node:bobjack.20080508125414.4:clear
    def clear(self):

        """Delete all the widgets in the the icon bar"""

        buttons = self.buttons

        # This removes all the buttos from the iconbar.
        self.buttons = []

        for w in buttons:
            try:
                if hasattr(w, 'deleteWidget'):
                    w.deleteButton()
                else:
                    self.removeWidget(w)
            except:
                g.es_error('can\'t delete', str(w))
                pass
    #@-node:bobjack.20080508125414.4:clear
    #@+node:bobjack.20080426064755.76:getButton
    def getButton(self,*args,**keys):
        """Create an iconBar button."""


        if 'item_data' not in keys:
            try:
                data = self.item_data
            except Exception:
                data = {}
            keys['item_data'] = data


        try:
            btn = ToolbarIconButton(self.c, {}, **keys)
        finally:
            self.item_data = None



        return btn
    #@-node:bobjack.20080426064755.76:getButton
    #@+node:bobjack.20080429153129.36:pack (show)
    def pack (self):

        """Show the icon bar by repacking it"""

        if not self.visible:
            self.outerFrame.pack(fill="x", pady=2)
            self.barHead.packSlaveBar()

    show = pack
    #@-node:bobjack.20080429153129.36:pack (show)
    #@+node:bobjack.20080501181134.4:unpack (hide)
    def unpack (self):

        """Hide the icon bar by unpacking it"""

        dummy = self.c.frame.dummyToolbarFrame

        if self.visible:
            self.outerFrame.pack_forget()
            dummy.pack()
            dummy.update_idletasks()
            dummy.pack_forget()

    hide = unpack
    #@-node:bobjack.20080501181134.4:unpack (hide)
    #@+node:bobjack.20080504034903.2:packSlaveBar
    def packSlaveBar(self):

        if self.iconFrame in self.outerFrame.pack_slaves():
            return

        self.iconFrame.pack(in_=self.outerFrame, fill='x')
    #@-node:bobjack.20080504034903.2:packSlaveBar
    #@+node:bobjack.20080504034903.3:unpackSlaveBar
    def unpackSlaveBar(self):

        if not self.slaveMaster:
            return

        if self.iconFrame in self.outerFrame.pack_slaves():
            self.iconFrame.pack_forget()
    #@-node:bobjack.20080504034903.3:unpackSlaveBar
    #@+node:bobjack.20080429153129.26:packWidget
    def packWidget(self, w, **kws):

        if 'side' in kws:
            del kws['side']

        try:
            w.pack(in_=self.iconFrame, side="left", **kws)

        except Exception:
            g.trace('[%s] FAILED TO PACK: \n\tWIDGET:%r\n\tin FRAME:%r' %(self.barName, w, self.iconFrame))

        return w

    #@-node:bobjack.20080429153129.26:packWidget
    #@+node:bobjack.20080429153129.27:unpackWidget
    def unpackWidget(self, w):


        if w in self.iconFrame.pack_slaves():
            w.pack_forget()

        return w
    #@-node:bobjack.20080429153129.27:unpackWidget
    #@+node:bobjack.20080508125414.6:Utility
    #@+node:bobjack.20080506182829.30:getImage
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

        iconpath = g.os_path_join(iconBasePath, path)

        try:
            return self.iconCache[iconpath]
        except KeyError:
            pass

        try:
            image = Image.open(path)
        except Exception:
            image = None

        if not image:

            try:
                image = Image.open(iconpath)
            except Exception:
                image = None

        if not image:
            return None

        try:    
            image = ImageTk.PhotoImage(image)
        except Exception:
            image = None

        if not image or not image.height():
            g.es('Bad Toolbar Icon: %s' % path)
            return None

        self.iconCache[path] = image

        return image

    #@-node:bobjack.20080506182829.30:getImage
    #@+node:bobjack.20080430064145.5:uniqueSlaveName
    def uniqueSlaveName(self):

        """Return a unique name for a slaveBar of this iconBar."""

        return '%s-%02d-slave' % (self.barHead.barName, self.barHead.nSlaves)
    #@-node:bobjack.20080430064145.5:uniqueSlaveName
    #@-node:bobjack.20080508125414.6:Utility
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
        'toggle-iconbar',
        'toolbar-toggle-iconbar',
    )

    #@    @+others
    #@+node:bobjack.20080424195922.13:__init__
    def __init__(self, c):

        """Initialize toolbar functionality for this commander.

        This only initializes ivars, the proper setup must be done by calling the
        controllers onCreate method from the module level onCreate function. This is
        to make unit testing easier.

        """

        self.c = c


    #@+node:bobjack.20080424195922.14:onCreate
    def onCreate(self):

        c = self.c

        self.registerCommands()
        self.setDefaultContextMenus()


        setattr(c, 'the%sController'%__plugin_id__, self)

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

            lst.append((command, methodName, function))

        return lst
    #@-node:bobjack.20080424195922.16:createCommandCallbacks
    #@+node:bobjack.20080424195922.17:registerCommands
    def registerCommands(self):

        """Create callbacks for minibuffer commands and register them."""

        c = self.c

        commandList = self.createCommandCallbacks(self.getCommandList())

        for cmd, methodName, function in commandList:
            c.k.registerCommand(cmd, shortcut=None, func=function, wrap=True)   
    #@-node:bobjack.20080424195922.17:registerCommands
    #@+node:bobjack.20080424195922.19:getCommandList
    def getCommandList(self):

        return self.commandList
    #@-node:bobjack.20080424195922.19:getCommandList
    #@+node:bobjack.20080510064957.112:setDeafaultContextMenus
    def setDefaultContextMenus(self):

        c = self.c

        if not hasattr(c, 'context_menus'):
            c.context_menus = {}

        if 'default-iconbar-menu' in c.context_menus:
            return

        items = [
            ('Add Bar', 'toolbar-add-iconbar'),
            ('Add Script-Button', 'toolbar-add-script-button'),
            ('-', ''),
            ('*', 'toolbar-toggle-iconbar'),
            ('*', 'toolbar-show-iconbar-menu'),
        ]

        c.context_menus['default-iconbar-menu'] = items
    #@-node:bobjack.20080510064957.112:setDeafaultContextMenus
    #@-node:bobjack.20080424195922.13:__init__
    #@+node:bobjack.20080428114659.20:Generator Commands
    #@+node:bobjack.20080428114659.21:toolbar_show_iconbar_menu
    def toolbar_show_iconbar_menu(self, keywords):

        """Create a menu to show  hidden toolbars."""

        c = self.c
        frame = c.frame

        try:
            menu_table = keywords['rc_menu_table']
            bar = keywords['bar']
        except Exception:
            g.es_error('Command only for use in iconBar menus')
            return

        barName = bar and bar.barName or ''

        names = frame.iconBars.keys()

        items = []
        while names:
            name = names.pop(0)

            if name == barName:
                continue

            bar = frame.iconBars[name]

            if not bar.visible:

                def show_iconbar_cb(c, keywords, bar=bar):
                    bar.show()

                items.append((name, show_iconbar_cb))

        if items:
            items = [('Show', items)]
            menu_table[:0] = items  

    #@-node:bobjack.20080428114659.21:toolbar_show_iconbar_menu
    #@+node:bobjack.20080503040740.4:toolbar_toggle_iconbar
    def toolbar_toggle_iconbar(self, keywords):
        """Minibuffer command to toggle the visibility of an iconBar."""

        c = self.c
        frame = c.frame

        try:
            phase = keywords['rc_phase']
        except KeyError:
            phase = 'minibuffer'

        try:
            bar = keywords['bar']
            inBar = True
        except KeyError:
            inBar = False
            bar = frame.iconBar

        barShow = "Show IconBar\nicon=Tango/16x16/actions/add.png"
        barHide = "Hide IconBar\nicon=Tango/16x16/actions/remove.png"

        visible = bar.visible

        if phase == 'generate':

            label = visible and barHide or barShow
            menu_table = keywords['rc_menu_table']
            menu_table[:0] =  [(label, 'toggle-iconbar')]

        elif phase in ['invoke', 'minibuffer']:

            bar.visible = not visible

    toggle_iconbar = toolbar_toggle_iconbar

    #@-node:bobjack.20080503040740.4:toolbar_toggle_iconbar
    #@-node:bobjack.20080428114659.20:Generator Commands
    #@+node:bobjack.20080426190702.2:Invocation Commands
    #@+node:bobjack.20080426190702.3:toolbar_delete_button
    def toolbar_delete_button(self, keywords):
        """Minibuffer command to delete a toolbar button.

        For use only in rClick menus attached to toolbar buttons.

        """

        try:
           keywords['event'].widget.deleteButton()

        except Exception, e:
            g.es_error(e)
            g.es_error('failed to delete button')





    #@-node:bobjack.20080426190702.3:toolbar_delete_button
    #@+node:bobjack.20080428114659.11:toolbar_add_iconbar
    def toolbar_add_iconbar(self, keywords):
        """Minibuffer command to add a new iconBar."""

        c = self.c
        frame = c.frame

        try:
            bar = keywords['bar']
            barName = bar.barName 
        except KeyError:
             barName = 'iconbar'

        newbarName = self.uniqueBarName(barName)

        frame.createIconBar(newbarName)






    #@-node:bobjack.20080428114659.11:toolbar_add_iconbar
    #@+node:bobjack.20080428114659.16:toolbar_hide_iconbar
    def toolbar_hide_iconbar(self, keywords):
        """Minibuffer command to hide an iconBar.

        This is only for use in context menus attached to iconBars.
        """

        c = self.c
        frame = c.frame

        try:
            bar = keywords['bar']
        except KeyError:
            bar = frame.iconBars['iconbar']

        bar.hide()

    #@-node:bobjack.20080428114659.16:toolbar_hide_iconbar
    #@+node:bobjack.20080428114659.17:toolbar_add_script_button
    def toolbar_add_script_button(self, keywords):

        """Add a script-button to the selected iconBar.

        This is for use in iconBar rClick menus, but may also be used as a minibufer
        command, in which case it will always add the script button to the iconBar
        named 'iconbar' if it exists.

        """

        c = self.c
        frame = c.frame
        iconBars = frame.iconBars

        try:
            bar = keywords['bar']
            barName = bar.barName
        except KeyError:
            bar = iconBars['iconbar']
            barName = 'iconbar'

        oldIconBar = frame.iconBar

        try:
            frame.iconBar = bar
            sm = c.theScriptingController
            sm.createScriptButtonIconButton(barName) 
        finally:
            frame.iconBar = oldIconBar

    add_script_button = toolbar_add_script_button


    #@-node:bobjack.20080428114659.17:toolbar_add_script_button
    #@-node:bobjack.20080426190702.2:Invocation Commands
    #@+node:bobjack.20080429153129.28:Utility
    #@+node:bobjack.20080429153129.21:uniqueBarName
    def uniqueBarName(self, prefix):

        iconBars = self.c.frame.iconBars

        if not prefix in iconBars:
            return prefix

        for i in range(1,100):
            barName = '%s.%s' %(prefix, i)
            if barName not in iconBars:
                return barName

    #@-node:bobjack.20080429153129.21:uniqueBarName
    #@-node:bobjack.20080429153129.28:Utility
    #@-others

#@-node:bobjack.20080424195922.12:class pluginController
#@-others
#@-node:bobjack.20080424190315.2:@thin toolbar.py
#@-leo

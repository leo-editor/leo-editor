#@+leo-ver=5-thin
#@+node:bobjack.20080424190315.2: * @file toolbar.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:bobjack.20080424190906.12: ** << docstring >>
""" Enhances Leo's iconBar and script buttons.

This plugin provides:

    multiple iconBars each of which automatically collapse and
    expand so that all the buttons are always visible.

    drag and drop of buttons within and between iconBars.

    enhancements to Leo's buttons and @button settings to allow
    icons, menus, tooltips and text and background colors to be set
    in @button settings and scripts. 

**Enhanced script button and @button nodes**

If the toolbar.py plugin is enabled then a comment block can be added at the top
of the body of the @button node. (If toolbar.py is not enabled then these
comment blocks will of course simply be ignored.)

The header will also be honored if script-button is used to convert a node
to a button.

Within this block you may include lines starting with @btn to set extra
parameters for the button created.

Example 1::

    @
    @btn fg = yellow
    @btn bg = red
    @btn menu = my-button-menu
    @c

The created button would have yellow text on a red background and when the right
mouse button is clicked on it a popup menu will appear (if rClick.py is
enabled).

Example 2::

    @
    @btn icon = Tango/16x16/actions/add.png
    @btn menu = my-button-menu
    @btn bg =
    @btn tooltip = My First Icon Button
    @c

Here the button will only have an icon, not text. It still has a right click
menu. The line after the 'bg =' is left blank to suppress any default background
colors, without setting our own color.

Icons in buttons requires the Python Imaging Library to be installed on your computer.

The line containing the single @ must not be preceded by any other line except
blank lines.

**Toolbars** 

A toolbar is a collection of iconbars. At the moment only one toolbar is
available and it appears in the place where Leo's traditional iconbar appears.

Future plans include allowing toolbars to be placed anywhere, including in dialogs,
orientated vertically as well as horizontally. It will then be possible to drag and
drop iconbars within and between toolbars.

**Iconbars**

Each iconbar is assigned a name. The default iconBar is called 'iconbar'. A
dictionary mapping names to iconBar objects is kept in *c.frame.iconBars* and
the default iconBar is also in *c.frame.iconBar*    

Any widget may be added to an iconBar but:

    All widgets must have c.frame.top as the parent.

    Widgets can not be packed into the bars directly, they must be added
    through c.frame.addIconWidget or through <bar>.addWidget


This will break some plugins. If it breaks a plugin you are using report this
on the mailing list and it will be fixed.

If widget.leoShow exists and is set to False then the widget will still be in
the list in its assigned packing order but it will not be seen. Any change to 
widget.leoShow must be followed by a call to bar.repackButtons() before the
change will be seen. 

Some convenience methods are available in c.frame, all of which can have
barName=<name of bar>. If no barName is supplied 'iconbar' will be used.

    createIconBar(barName='iconbar'):
        If an iconBar with barName already exists it will be returned, otherwise
        a new iconBar will be created, packed and returned.

    addIconButton(\*args, \**keys):
        Creates and packs and returns an icon button. This is equivalent
        to c.frame.addIconWidget(c.frame.getIconButton(\*args, \**keys)

        barName: 'iconbar' may be in keys.

    getIconButton(\*args, \**keys):
        creates and returns an icon button but does not pack it. Any barName
        will be ignored.

    getIconWidgetFrame(\*args, \**keys): 

        Creates an enhanced Tk.Frame widget properly parented and with
        a few methods which make it easier to use than a straight Tk.Frame.

        args and keys are the same as for Tk.Frame except without the first
        (parent) arg which is not used as the Frame will always have c.frame.top
        as the parent as required by all widgets to be packed in an iconBar.

    addIconWidget(widget, barName='iconbar', index=None):

        Adds any widget or button to the named iconBar in the position indicated
        by index. If barName does not exist it is created.

        This method delegates to c.frame.iconBars[barName].addWidget

        The method is used to add buttons as well as other widgets because
        'addIconButton' is already taken and has a different meaning.

The iconBars themselves have the following public methods.

    getButton(\*args, \**keys)
        same as c.frame.getIconButton

    getWidgetFrame(\*args, \**keys)
        same as c.frame.getWidgetFrame

    add(\*args, \**keys)
        same as c.frame.addIconButton

    repackButtons(buttons=None)

        If buttons is None then the current list of buttons is repacked,
        otherwise it must be a list of buttons or other widgets to pack.

    addWidget(widget, index=None, repack=True)

        Adds a widget to the list of widgets to be packed in this iconBar.

        repack is True by default causing repackButtons() to be called after
        adding the widget. If repack is set to False the script must call
        repackButtons() itself. Setting repack to False is useful if you
        want to add several widgets, you can then call repackButtons() just
        once.

        If index is None or invalid the widget will be packed at the end
        of the iconBar.

    removeWidget(widget, repack=True)
         removes the widget from the list and optionally repacks the iconBar.

    show(show=True)
        Makes the toolbar visible if it is not already visible or vice versa
        if show is False.

     hide()
        Makes the toolbar invisible if it was not already invisible.

The iconbars also have the following public properties.

    bar.buttons

        This provides a shallow *copy* of the list of buttons/widgets contained
        in the iconBar. Changing this list has no effect on the iconBar.

        Using 'bar.buttons = <list of widgets>' is allowed and is the same as::

            bar.repackButtons(<list of widgets>)

        Commands of the following kind are allowed::

            bar.buttons = bar.buttons[1:]

        but the following will not work as expected::

            bar.buttons[1:]

    bar.visible

        tells if the bar is visible or not.

        'bar visible = True (or False)' show (or hides) the toolbar. 

        'bar.visible = not bar.visible' toggles the visibility of the toolbar

**Compound iconBar widgets and drag handles**

Compound widgets can be constructed using a Tkinter.Frame widget and packing
buttons (obtained, for example, from c.frame.getButton) and other components into it,
finally packing the frame into the iconBar using c.frame.addIconWidget or
bar.addWidget.

The following methods::

    c.frame.getIconWidgetFrame(\*args, \*keys) and 
    bar.getWidgetFram(\*args, \*keys)

return a Tk.Frame widget parented on c.frame.top and with a few extra
methods to make more advanced use easier.

See test/testToolbar.leo for demo's and howto's.
See test/testAtPopup.leo for examples of enhanced buttons.


"""
#@-<< docstring >>

__version__ = "0.14" # EKR
__plugin_name__ = 'Toolbar Manager'
__plugin_id__ = 'Toolbar'

controllers = {}

#@+<< version history >>
#@+node:bobjack.20080424190906.13: ** << version history >>
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
#     - remove dependency on rClick
#     - add drag drop in iconBars
# 0.7 bobjack:
#     - add support for leoDragHandle and leoDragMaster
# 0.8 bobjack:
#     - convert to use c.universallCallback via registerCommands( ... wrap=True)
#     - separate out icon and script button code and make these first class objects
# 0.9 bobjack:
#     - convert to use class based commands
# 0.10 bobjack:
#     - attempt to improve docstring
#     - add ToolbarIconWidgetFrame and convenience methods to make
#       creating compound widgets for the iconbars easier.
# 0.11 bobjack:
#     - use baseclasses in rclickPluginBaseClasses
# 0.12 EKR: add 'font' to list of allowed keys so that font settings are honored.
# 0.13 EKR: added support for @args list.
# 0.14 EKR: import tkGui as needed.
#@-<< version history >>
#@+<< todo >>
#@+node:bobjack.20080424190906.14: ** << todo >>
#@+at
# 
# Use a more efficent repack algorithm to reduce flicker. The current method is
# simple and safe. I have tried to optimize repack but keep running into
# special cases and instability.
#@-<< todo >>
#@+<< imports >>
#@+node:bobjack.20080424190906.15: ** << imports >>
import leo.core.leoGlobals as g

import leo.plugins.tkGui as tkGui
leoTkinterFrame = tkGui.leoTkinterFrame
leoTkinterTreeTab = tkGui.leoTkinterTreeTab

Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)
Pmw = g.importExtension("Pmw",pluginName=__name__,verbose=True,required=True)

from leo.plugins import mod_scripting

from leo.plugins import rClickBasePluginClasses as baseClasses
#@-<< imports >>

#@+<< required ivars >>
#@+node:bobjack.20080424195922.85: ** << required ivars >>
#@+at
# This is a list of ivars that the pluginController must have and the type of objects they are allowed to contain.
# 
#     (ivar, type)
# 
# where type may be a tuple and False indicates any type will do
# 
# The list is used by unit tests.
#@@c

requiredIvars = (
    ('commandList', (list, tuple)),
    ('commandPrefix', g.choose(g.isPython3,str,basestring)),
    ('grabWidget', False)
)
#@-<< required ivars >>

allowedButtonConfigItems = ('image', 'bg', 'fg', 'font','justify', 'padx', 'pady', 'relief', 'text', 'command', 'state')
iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

#@+others
#@+node:bobjack.20080424190906.6: ** Module-level
#@+node:bobjack.20080424190906.7: *3* init
def init ():
    """Initialize and register plugin."""

    ok = Tk and Pmw and g.app.gui.guiName() == "tkinter" and not g.app.unitTesting

    if ok:
        g.registerHandler('before-create-leo-frame',onPreCreate)
        g.registerHandler('after-create-leo-frame', onCreate)
        g.registerHandler('close-frame', onClose)

        tkGui.leoTkinterFrame = ToolbarTkinterFrame
        g.plugin_signon(__name__)

    return ok
#@+node:bobjack.20080424195922.11: *3* onPreCreate
def onPreCreate (tag, keys):
    """Replace iconBarClass with our own."""

    c = keys.get('c')
    if not (c and c.exists) or hasattr(c.frame, 'toolbarClass'):
        return

    g.app.gui.ScriptingControllerClass = ToolbarScriptingController
    c.frame.iconBarClass = ToolbarTkIconBarClass
    c.frame.toolbarClass = ToolbarTkToolbarClass

    tkGui.leoTkinterTreeTab = ToolbarTkinterTreeTab

    c.frame.iconBars= {}
    c.frame.toolbar = None
#@+node:bobjack.20080426190702.6: *3* onCreate
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

        c.theToolbarController = controller



#@+node:bobjack.20080424195922.10: *3* onClose
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
#@+node:bobjack.20080501055450.5: *3* class ToolbarTkinterTreeTab
class ToolbarTkinterTreeTab (leoTkinterTreeTab):

    '''A class representing a tabbed outline pane drawn with Tkinter.'''

    #@+others
    #@+node:bobjack.20080501055450.8: *4* tt.createControl
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
    #@-others
#@+node:bobjack.20080428114659.2: *3* class ToolbarTkinterFrame
class ToolbarTkinterFrame(leoTkinterFrame, object):

    #@+others
    #@+node:bobjack.20080429153129.29: *4* Icon area convenience methods
    #@+node:bobjack.20080429153129.30: *5* addIconButton
    def addIconButton (self,*args,**keys):

        """Create and add an icon button to the named toolbar.

        keys['barName'] gives the name of the iconBar to be uses if it is present
        outherwise 'iconbar' is used.

        If the iconBar does not exist it will be created.

        All arguments and keywords except 'barName' will be passed to iconBar.add.

        """

        if 'barName' in keys:
            barName = keys['barName']
            del keys['barName']
        else:
            barName = 'iconbar'

        bar = self.createIconBar(barName)

        if bar:
            return bar.add(*args, **keys)
    #@+node:bobjack.20080503151427.2: *5* getIconButton
    def getIconButton (self,*args,**keys):

        """Create an icon button but do not add it to a toolbar.

        If keys['barName'] is present it is removed from 'keys' but
        otherwise ignored.

        """
        if 'barName' in keys:
            barName = keys['barName']
            del keys['barName']

        bar = self.createIconBar('iconbar')

        if bar:
            return bar.getButton(*args,**keys)

    createIconButton = getIconButton
    #@+node:bobjack.20080501055450.16: *5* addIconWidget
    def addIconWidget (self, widget, barName='iconbar', index=None):

        """Adds a button or other widget to the named toolbar."""

        bar = self.createIconBar(barName)
        if bar:
            return bar.addWidget(widget, index=index)
    #@+node:bobjack.20080429153129.31: *5* clearIconBar
    def clearIconBar (self, barName='iconbar'):

        """This removes all widgets from the named iconbar and calls their delete method."""

        self.iconBars[barName].clear()
    #@+node:bobjack.20080429153129.32: *5* createIconBar
    def createIconBar (self, barName='iconbar',  slaveMaster=None):

        """Create and display a new iconBar.

        If the iconbar exists it will returned.

        Otherwise a new iconBar will be created, shown and returned.

        """

        toolbar = self.createToolbar()

        frame = toolbar.toolbarFrame

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

    #@+node:bobjack.20080429153129.33: *5* getIconBar
    getIconBar = createIconBar
    #@+node:bobjack.20080429153129.34: *5* getIconBarObject
    getIconBarObject = getIconBar
    #@+node:bobjack.20080429153129.35: *5* hideIconBar
    def hideIconBar (self, barName='iconbar'):

        """Remove an iconBar from the display."""

        self.iconBars[barName].hide()
    #@+node:bobjack.20080612150456.3: *5* getIconWidgetFrame
    def getIconWidgetFrame(self, *args, **keys):

        """Return a subclass of Tk.Frame.

        The frame is parented on c.frame.top and set up for packing
        into an iconBar. It may be used to hold several buttons or
        other widgets which are then treat as a single item

        """

        if 'barName' in keys:
            del keys['barName']

        bar = self.getIconBar('iconbar')

        if bar:
            return bar.getWidgetFrame(*args,**keys)
    #@+node:bobjack.20080502134903.8: *4* Properties
    #@+node:bobjack.20080502134903.9: *5* iconFrame
    def getIconFrame(self):

        try:
            return self.iconBar.iconFrame
        except Exception:
            pass

    def setIconFrame(self, value):
        pass

    iconFrame = property(getIconFrame, setIconFrame)
    #@+node:bobjack.20080616103714.6: *5* toolbarFrame
    def getToolbarFrame(self):

        try:
            return self.toolBar.toolbarFrame
        except Exception:
            pass

    toolbarFrame = property(getToolbarFrame)
    #@+node:bobjack.20080428114659.5: *4* createToolbar
    def createToolbar(self):

        """Create and pack the frame that contains all the toolbars.

        If the frame already exists return it or create, pack and return
        a new frame.

        """

        c = self.c

        # Rewrite to keepy pylint happy.
        if hasattr(self,'toolbar'):
            toolbar = getattr(self,'toolbar')
        else:
            toolbar = None

        # try:
            # toolbar = self.toolbar
        # except AttributeError:
            # toolbar = None

        if toolbar:
            return toolbar

        self.toolbar = w = ToolbarTkToolbarClass(c, self.outerFrame, toolbarName='toolbar')
        self.dummyToolbarFrame = Tk.Frame(w.toolbarFrame, height='1p')

        w.toolbarFrame.pack(fill='x')

        return self.toolbar
    #@-others

#@+node:bobjack.20080506182829.14: *3* class ToolbarIconWidgetFrame
class ToolbarIconWidgetFrame(Tk.Frame, object):

    """A subclass of Tk.Frame that is parented on c.frame.top.



    """

    #@+others
    #@+node:bobjack.20080506182829.15: *4* __init__
    def __init__(self, c, *args, **keys):

        self.c = c

        Tk.Frame.__init__(self, c.frame.top, *args, **keys)

        self.deleteOnRightClick = False
    #@+node:bobjack.20080612150456.4: *4* detachWidget
    def detachWidget(self):

        """Remove this widget from its containing iconBar."""

        try:
            bar = self.leoIconBar
        except:
            bar = None

        if bar:
            self.leoIconBar.removeWidget(self)

    removeWidget = detachWidget

    #@+node:bobjack.20080612150456.5: *4* deleteButton
    def deleteButton(self, event=None):

        """Delete the given button.

        This method does not actually delete the widget, override the method
        in a derived class to do that. 

        """

        self.detachWidget()


    #@-others
#@+node:bobjack.20080506182829.16: *3* class ToolbarIconButton
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

    #@+others
    #@+node:bobjack.20080506182829.24: *4* __init__
    def __init__(self, c, cnf={}, **keys ):

        """Create an iconBar button.

        cnf must be a dictionary if it is supplied at all.


        """
        if 0:
            g.pr('ToolbarIconButton.__init__')
            g.pr('\t', cnf)
            g.pr('\t', keys)

        self.c = c
        self.deleteOnRightClick = False
        self.balloonEnabled = False
        self.balloon = None

        self.keys = keys = self.mergeConfigSources(cnf, keys)

        #@+<< setup menu >>
        #@+node:bobjack.20080507053105.4: *5* << setup menu >>
        if 'menu' in keys:
            self.context_menu = keys['menu']
            del keys['menu']
        #@-<< setup menu >>
        #@+<< setup statusLine >>
        #@+node:bobjack.20080507053105.5: *5* << setup statusLine >>
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
        #@-<< setup statusLine >>
        #@+<< setup image and relief >>
        #@+node:bobjack.20080506182829.31: *5* << setup image and relief >>


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
            image = baseClasses.getImage(imagefile)

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
        #@-<< setup image and relief >>
        #@+<< setup command >>
        #@+node:bobjack.20080506182829.32: *5* << setup command >>
        command = keys.get('command')

        # Rewrite to keep pylint happy.
        # if command and isinstance(command, basestring):
        if command and g.isString(command):
            def commandCallback(c=self.c, command=command):
                c.executeMinibufferCommand(command)
        elif command:
            commandCallback = command
        else:
            def commandCallback():
                g.pr("command for widget %s" % self)

        # commandCallback = command

        # if not command:
            # def commandCallback():
                # g.pr("command for widget %s" % self)

        # elif isinstance(command, basestring):
            # def commandCallback(c=self.c, command=command):
                # c.executeMinibufferCommand(command)

        keys['command'] = commandCallback
        #@-<< setup command >>
        #@+<< setup font >>
        #@+node:bobjack.20080506182829.33: *5* << setup font >>
        if not hasattr(self, 'font'):
            self.font = None

        self.font = (
            keys.get('font') or
            self.font or
            self.c.config.getFontFromParams(
                "button_text_font_family", "button_text_font_size",
                "button_text_font_slant",  "button_text_font_weight",
            ))

        keys['font'] = self.font
        #@-<< setup font >>

        if 'bg' in keys and not keys['bg']:
            del keys['bg'] 

        kws = self.getButtonConfig(keys)    
        Tk.Button.__init__(self, c.frame.top, **kws)


        c.bind(self,'<Button-3>', self.onRightClick)


    #@+node:bobjack.20080507175534.2: *4* attachWidget
    def attachWidget(self, bar='iconbar', index=None, createBar=True, showBar=True):

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
    #@@c
    #@+node:bobjack.20080507175534.3: *4* createBalloon (gui-dependent)
    def createBalloon (self, delay=100):

        'Create a balloon for a widget.'

        if not self.balloon:
            self.balloon = Pmw.Balloon(self, initwait=delay)


        self.balloon.bind(self, self.statusLine)
    #@+node:bobjack.20080507053105.7: *4* detachWidget
    def detachWidget(self):

        try:
            bar = self.leoIconBar
        except:
            bar = None

        if bar:
            self.leoIconBar.removeWidget(self)

    removeWidget = detachWidget

    #@+node:bobjack.20080508051801.5: *4* getButtonConfig
    def getButtonConfig(self, keys=None):

        """Select keys and values to pass on to Tk.Button."""

        if keys is None:
            keys = self.keys

        haveKeys = set(keys.keys())
        allowedKeys = set(allowedButtonConfigItems)

        sendkeys = [ k for k in haveKeys & allowedKeys]

        kws = {}
        for k in sendkeys:
            # if isinstance(k,unicode):
                # k = k.encode()
            if g.isUnicode(k):
                k = g.toEncodedString(k)
            kws[k] = keys[k]

        return kws
    #@+node:bobjack.20080507053105.9: *4* mergeConfigSources
    def mergeConfigSources(self, cnf, keys):

        """Merge and prioritize config sources.

        config sources are dictionaries cnf, keys and keys['item_data']

        Priority cnf < keys < item_data.
        """

        if 0:
            g.trace()
            g.pr('\t', cnf)
            g.pr('\t', keys)

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
    #@+node:bobjack.20080507053105.6: *4* onRightClick
    def onRightClick(self, event):


        # if the button has a context menu, handle it and return

        if g.doHook('rclick-popup',
            c=self.c, event=event,
            button=self,
        ):
            return

        # otherwise, see if there a containing widget has a menu.

        if hasattr(event.widget, 'leoDragMaster'):

            dragMaster = event.widget.leoDragMaster
            if hasattr(dragMaster, 'context_menu'):

                if g.doHook('rclick-popup',
                    c=self.c, event=event,
                    button=dragMaster,
                    context_menu=dragMaster.context_menu
                ):
                    return

        else:
            dragMaster = self

        try:
            if dragMaster.deleteOnRightClick:
                dragMaster.deleteButton()     
        except AttributeError:
            pass

    #@+node:bobjack.20080508051801.6: *4* deleteButton
    def deleteButton(self, event=None):

        """Delete the given button.

        This method does not actually delete the button, override the method
        in derived classes to do that.

        """

        self.detachWidget()


    #@+node:bobjack.20080508051801.7: *4* setCommand
    def setCommand(self, command):

        # Rewrite to keep pylint happy.
        # if command and isinstance(command, basestring):
        if command and g.isString(command):
            def commandCallback(event,command=command):
                self.c.executeMinibufferCommand(command)
        elif command:
            commandCallback = command
        else:
            def commandCallback():
                g.pr("command for widget %s" % self)

        # commandCallback = command

        # if not command:
            # def commandCallback():
                # g.pr("command for widget %s" % self)

        # if isinstance(command, basestring):

            # def commandCallback(event, command=command):
                # return self.c.executeMinibufferCommand(command)

        self.config(command=commandCallback) 
    #@-others
#@+node:bobjack.20080506182829.18: *3* class ToolbarScriptButton
class ToolbarScriptButton(ToolbarIconButton):

    #@+others
    #@+node:bobjack.20080506182829.19: *4* __init__
    def __init__(self, c, cnf={}, **keys):

        self.c = c
        k = c.k

        keys = self.mergeConfigSources(cnf, keys)

        text = keys.get('text')
        #@+<< command name >>
        #@+node:bobjack.20080507053105.11: *5* << command name >>
        self.commandName = commandName = self.cleanButtonText(text).lower()
        #@-<< command name >>
        #@+<< truncate text >>
        #@+node:bobjack.20080507053105.10: *5* << truncate text >>

        self.truncatedText = truncatedText = self.truncateButtonText(commandName)
        keys['text'] = truncatedText
        #@-<< truncate text >>
        #@+<< register commands >>
        #@+node:bobjack.20080507053105.12: *5* << register commands >>
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
        #@-<< register commands >>

        ToolbarIconButton.__init__(self, c, keys)

        self.deleteOnRightClick = True

        self.baloonEnabled = True
        self.createBalloon()



    #@+node:bobjack.20080507053105.13: *4* Properties
    #@+node:bobjack.20080507175534.4: *5* baloonEnabled


    #@+node:bobjack.20080507053105.15: *5* maxButtonSize
    def getMaxButtonSize(self):

        return self.c.theScriptingController.maxButtonSize

    maxButtonSize = property(getMaxButtonSize)
    #@+node:bobjack.20080507053105.14: *5* scriptingController
    def getScriptingController(self):

        return self.c.theScriptingController

    scriptingController = property(getScriptingController)
    #@+node:bobjack.20080506182829.36: *4* cleanButtonText
    def cleanButtonText (self,s):

        '''Clean the text following @button or @command so that it is a valid name of a minibuffer command.'''

        import string

        # Strip @...@button.
        while s.startswith('@'):
            s = s[1:]
        if g.match_word(s,0,'button'):
            s = s[6:]
        for tag in ('@key','@args'):
            i = s.find(tag)
            if i != -1:
                s = s[:i].strip()
        if 1: # Not great, but spaces, etc. interfere with tab completion.
            chars = g.toUnicode(string.letters + string.digits)
            aList = [g.choose(ch in chars,ch,'-') for ch in g.toUnicode(s)]
            s = ''.join(aList)
            s = s.replace('--','-')
        while s.startswith('-'):
            s = s[1:]
        while s.endswith('-'):
            s = s[:-1]
        return s
    #@+node:bobjack.20080506182829.37: *4* truncateButtonText
    def truncateButtonText (self,s, size=0):

        if not size:
            size = self.maxButtonSize

        size = max(size, 1)

        s = s[:size]
        if s.endswith('-'):
            s = s[:-1]
        return s.strip()
    #@+node:bobjack.20080426064755.77: *4* deleteButton
    def deleteButton(self, event=None):

        """Delete the given button.

        This is called from callbacks, it is not a callback.

        """

        super(self.__class__, self).deleteButton(event)

        self.scriptingController.deleteButton(self)
    #@-others


#@+node:bobjack.20080506182829.20: *3* class ToolbarAddScriptButton
class ToolbarAddScriptButton(ToolbarScriptButton):

    #@+others
    #@+node:bobjack.20080506182829.21: *4* __init__
    def __init__(self, c, *args, **kw):

        super(ToolbarAddScriptButton, self).__init__(c, *args, **kw)
    #@-others
#@+node:bobjack.20080425135232.6: *3* class ToolbarScriptingController
scripting = mod_scripting.scriptingController

class ToolbarScriptingController(mod_scripting.scriptingController, object):

    #@+others
    #@+node:bobjack.20080506182829.12: *4* createAtButtonFromSettingHelper & callback (ToolbarScriptingController)
    def createAtButtonFromSettingHelper (self,h,script,statusLine,shortcut,bg='LightSteelBlue2'):

        '''Create a button from an @button node.

        - Calls createIconButton to do all standard button creation tasks.
        - Binds button presses to a callback that executes the script.
        '''

        c = self.c
        k = c.k

        buttonText = self.cleanButtonText(h)
        args = self.getArgs(h)
        g.trace('h',h,'args',args)

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
            args=args,
            b=b,
            script=script,
            buttonText=buttonText
        ):
            self.executeScriptFromSettingButton (args,b,script,buttonText)

        self.iconBar.setCommandForButton(b,atSettingButtonCallback)

        # At last we can define the command and use the shortcut.
        k.registerCommand(buttonText.lower(),
            shortcut=shortcut,func=atSettingButtonCallback,
            pane='button',verbose=False)

        return b
    #@+node:bobjack.20080506182829.13: *5* executeScriptFromSettingButton (ToolbarScriptingController)
    def executeScriptFromSettingButton (self,args,b,script,buttonText):

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
    #@+node:bobjack.20080508051801.2: *4* createAtButtonHelper & callback (ToolbarScriptingController)
    def createAtButtonHelper (self,p,h,statusLine,shortcut,bg='LightSteelBlue1',verbose=True):

        '''Create a button from an @button node.

        - Calls createIconButton to do all standard button creation tasks.
        - Binds button presses to a callback that executes the script in node p.
        '''
        c = self.c ; k = c.k

        item_data = self.getItemData(p.b)

        buttonText = self.cleanButtonText(h)
        args = self.getArgs(h)

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
            args=args,
            p=p.copy(),
            b=b,
            buttonText=buttonText
        ):
            self.executeScriptFromButton (p,args,b,buttonText)

        b.setCommand(atButtonCallback)

        # At last we can define the command and use the shortcut.
        k.registerCommand(buttonText.lower(),
            shortcut=shortcut,func=atButtonCallback,
            pane='button',verbose=verbose)

        return b
    #@+node:bobjack.20080508051801.3: *5* executeScriptFromButton (ToolbarScriptingController)
    def executeScriptFromButton (self,p,args,b,buttonText):

        '''Called from callbacks to execute the script in node p.'''

        c = self.c

        if c.disableCommandsMessage:
            g.es(c.disableCommandsMessage,color='blue')
        else:
            g.app.scriptDict = {}
            c.executeScript(args=args,p=p,silent=True)
            # Remove the button if the script asks to be removed.
            if g.app.scriptDict.get('removeMe'):
                g.es("Removing '%s' button at its request" % buttonText)
                b.deleteButton()

        if 0: # Do *not* set focus here: the script may have changed the focus.
            c.frame.bodyWantsFocus()
    #@+node:bobjack.20080425135232.10: *4* getItemData
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
    #@+node:bobjack.20080428114659.18: *4* getIconBar
    def getIconBar(self):

        return self.c.frame.iconBar


    def setIconBar(self,*args, **kw):
        pass

    iconBar = property(getIconBar, setIconBar)
    #@+node:bobjack.20080430160907.2: *4* createIconButton

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
    #@+node:bobjack.20080428114659.12: *4* createScriptButtonIconButton 'script-button' & callback
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
            val = self.addScriptButtonCommand(event, b)
            # Careful: func may destroy c.
            if c.exists: c.outerUpdate()
            return val

        b.configure(command=addScriptButtonCallback)
    #@+node:bobjack.20080428114659.13: *5* addScriptButtonCommand
    def addScriptButtonCommand (self,event=None, b=None):

        """Convert the node into a script button and add it to an iconBar.

        b is the add-script-button that was clicked and the new script button
        will be added to the same iconBar.

        """ 

        c = self.c
        frame = c.frame
        p = c.p
        h = p.h

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
    #@-others
#@+node:bobjack.20080426064755.66: *3* class ToolbarTkIconBarClass
iconbar = leoTkinterFrame.tkIconBarClass

class ToolbarTkIconBarClass(iconbar, object):

    '''A class representing an iconBar.'''

    iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

    barConfigCount = 0

    #@+others
    #@+node:bobjack.20080428114659.6: *4* __init__
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
        self.widgets_per_row = 20 # Used by tkGui.py

        if not slaveMaster :
            #@+<< define master iconBar stuff >>
            #@+node:bobjack.20080502134903.2: *5* << define master iconBar stuff >>
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


            #@-<< define master iconBar stuff >>

        # Create the frame to hold buttons assigned to this slave bar.

        self.iconFrame = self.top = w = Tk.Frame(
            self.parentFrame,          
            height="5m",relief="flat",
        )
        w.leoIconBar = self
        c.bind(w,'<Button-3>', self.onRightClick)

        if not slaveMaster:
            c.bind(w,'<Configure>', self.onConfigure)

        self.show()
        w.update_idletasks()
    #@+node:bobjack.20080508125414.5: *4* Event Handlers
    #@+node:bobjack.20080428114659.9: *5* onRightClick
    def onRightClick(self, event):

        """Respond to a right click on any of the components of the iconbar.

        The first bar in a set of slave bars is sent with the hook, 
        the actual slave bar can be found in event.widget.
        """

        #g.trace()

        w = event.widget

        w = self.getDragMaster(w)

        try:
            flag = w.leoIconBar
        except AttributeError:
            flag = False

        if flag:
            self.c.theToolbarController.grabWidget = w

            g.doHook('rclick-popup', c=self.c, event=event,
                context_menu='iconbar-menu', bar=self.barHead
            )
    #@+node:bobjack.20080503090121.5: *5* onPress
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

    #@+node:bobjack.20080503090121.6: *5* onRelease
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
    #@+node:bobjack.20080429153129.16: *5* onConfigure
    def onConfigure(self, event=None):

        #g.trace(self.configCount(), self.barHead.barName)

        self.repackButtons()

        self.configCount(1)

        #return True





    #@+node:bobjack.20080620224131.2: *5* configCount
    def configCount(self, i=0):

        ToolbarTkIconBarClass.barConfigCount += i

        return ToolbarTkIconBarClass.barConfigCount



    #@+node:bobjack.20080506182829.2: *5* getDragMaster
    def getDragMaster(self, w):

        if hasattr(w, 'leoDragMaster'):
            w = w.leoDragMaster

        return w
    #@+node:bobjack.20080430160907.4: *4* Properties
    #@+node:bobjack.20080430160907.5: *5* outerFrame
    def getOuterFrame(self):

        """Get the frame that contains this bar and its companion slaves."""

        return self.barHead._outerFrame

    def setOuterFrame(self, value):

        self.barHead._outerFrame = value

    outerFrame = property(getOuterFrame, setOuterFrame)
    #@+node:bobjack.20080430064145.4: *5* barHead
    def getBarHead(self):

        """Get the first bar for the list of bars of which this bar is a member."""

        bar = self
        while bar.slaveMaster:
            bar = bar.slaveMaster

        return bar

    barHead = property(getBarHead)

    #@+node:bobjack.20080501113939.2: *5* slaveBars

    def getSlaveBars(self):

        """Get a list of slave iconBars packed in this toolbar."""

        return [ bar.leoIconBar for bar in self.outerFrame.pack_slaves()]

    slaveBars = property(getSlaveBars)
    #@+node:bobjack.20080502134903.7: *5* slaveBarFrames
    def getSlaveBarFrames(self):

        """Get a list of slave iconBar frames packed in this toolbar."""

        return [ bar for bar in self.outerFrame.pack_slaves()]

    slaveBarFrames = property(getSlaveBarFrames)
    #@+node:bobjack.20080501055450.2: *5* slaveButtons
    def getSlaveButtons(self):

        """Get a list of widgets packed in this iconBar."""

        return [ btn for btn in self.iconFrame.pack_slaves()]


    slaveButtons = property(getSlaveButtons)
    #@+node:bobjack.20080501113939.3: *5* allSlaveButtons
    def getAllSlaveButtons(self,  shrink=False):

        """Make a list of all widgets packed in this set of toolbars."""

        buttons = []
        bar = self.barHead
        while bar:
            buttons += [ btn for btn in bar.iconFrame.pack_slaves()]
            bar = bar.slaveBar

        return buttons 

    allSlaveButtons = property(getAllSlaveButtons)
    #@+node:bobjack.20080501125812.5: *5* buttons
    def getButtons(self):

        """Get the list of widgets that may appear in this toolbar."""

        return self.barHead._buttons[:]

    def setButtons(self, lst):

        """Set a new list of widgets to be displayed in this toolbar."""

        self.repackButtons(lst)
        return

    buttons = property(getButtons, setButtons)

    #@+node:bobjack.20080501181134.5: *5* visible
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
    #@+node:bobjack.20080504034903.9: *4* updateButtons
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
    #@+node:bobjack.20080507083323.4: *4* repackButtons
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
    #@+node:bobjack.20080430160907.12: *5* doRepackButtons
    def doRepackButtons(self, trace=None):

        """Repack all the buttons in this toolbar.

        New slave iconBars will be created if needed to make sure all buttons are
        visible. Empty slaves will be hidden but not removed.

        """
        barHead = self.barHead
        barHead.inConfigure = True

        orphans = barHead._buttons[:]

        #@+<< unpack all buttons >>
        #@+node:bobjack.20080501181134.2: *6* << unpack all buttons >>

        bar = barHead
        while bar and bar.buttonCount:
            # Rewrite to keep pylint happy.
            # [ btn.pack_forget() for btn in bar.iconFrame.pack_slaves()]
            for z in  bar.iconFrame.pack_slaves():
                z.pack_forget()
            bar.buttonCount = 0
            bar = bar.slaveBar


        #@-<< unpack all buttons >>

        bar = barHead
        bars = bar.slaveBars

        #@+<< repack all widgets >>
        #@+node:bobjack.20080502134903.4: *6* << repack all widgets >>

        while bar and orphans:
            orphans = bar.repackHelper(orphans)
            if bar not in bars and (bar.buttonCount or not bar.slaveMaster):
                bar.packSlaveBar()
            bar = bar.slaveBar
        #@-<< repack all widgets >>
        #@+<< hide empty slave bars >>
        #@+node:bobjack.20080502134903.5: *6* << hide empty slave bars >>
        while bar :
            if bar in bars:
                bar.unpackSlaveBar()
            bar = bar.slaveBar
        #@-<< hide empty slave bars >>



    #@+node:bobjack.20080429153129.24: *6* repackHelper
    def repackHelper(self, orphans):

        """Pack as many 'orphan' buttons into this bar as possible

        Return a list of orphans that could not be packed.

        """

        iconFrame = self.iconFrame
        req = iconFrame.winfo_reqwidth
        actual = iconFrame.winfo_width

        while orphans:
            #@+<< pack widgets until full >>
            #@+node:bobjack.20080502134903.6: *7* << pack widgets until full >>
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

            #@-<< pack widgets until full >>

        if len(orphans) and not self.buttonCount:
            # we must pack at least one widget even if its too big
            widget = orphans.pop(0)
            widget.pack(in_=iconFrame, side="left")
            self.buttonCount = 1

        if not self.slaveBar and orphans:
            self.slaveBar = self.createSlaveBar()

        return orphans


    #@+node:bobjack.20080430064145.3: *6* createSlaveBar
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
    #@+node:bobjack.20080503151427.3: *4* add
    def add(self,*args,**keys):
        """Create and pack an iconBar button."""

        return self.addWidget(self.getButton(*args, **keys))


    #@+node:bobjack.20080430160907.11: *4* addWidget
    def addWidget(self, widget, index=None, repack=True):

        """Add a widget to the iconBar.

        The widget must have c.frame.top as it parent.

        If the widget is already attached to an iconBar it will
        first be removed

        """
        
        # 2011/04/27: Don't return inside a 'finally' block!
        c = self.c
        #@+<< remove from current bar >>
        #@+node:bobjack.20080508125414.13: *5* << remove from current bar >>
        try:
            bar = widget.leoIconBar
        except:
            bar = None

        if bar:
            bar.removeWidget(widget, repack=False)
        #@-<< remove from current bar >>

        barHead = self.barHead
        buttons = barHead._buttons

        #@+<< validate index >>
        #@+node:bobjack.20080508125414.12: *5* << validate index >>
        if index is not None:
            try:
                idx = int(index)
            except:
                idx = None

            if idx is None:
                if index in buttons:
                    idx = buttons.index(index)

            index = idx

            if index is None:
                g.es('Icon Bar index out of range')
        #@-<< validate index >>

        #@+<< bind widget and drag handles >>
        #@+node:bobjack.20080506090043.2: *5* << bind widget and drag handles >>
        c.bind(widget,'<ButtonPress-1>', barHead.onPress)
        c.bind(widget,'<ButtonRelease-1>', barHead.onRelease)

        try:
            drag = widget.leoDragHandle
        except AttributeError:
            drag = None

        if drag:
            if not isinstance(drag, (tuple, list)):
                drag = (drag,)

            for dw in drag:

                dw.leoDragMaster = widget

                c.bind(dw,'<ButtonPress-1>', barHead.onPress )
                c.bind(dw,'<ButtonRelease-1>', barHead.onRelease)

        widget.c = self.c
        widget.leoIconBar = barHead
        #@-<< bind widget and drag handles >>

        if index is not None:
            try:
                buttons.insert(index, widget)
            except IndexError:
                index = None

        if index is None:
            buttons.append(widget)

        if repack:
            self.repackButtons()

        return widget
    #@+node:bobjack.20080501181134.3: *4* removeWidget
    def removeWidget(self, widget, repack=True):

        """Remove widget from the list of manged widgets and repack the buttons."""

        # 2011/04/27: Don't return inside a 'finally' block!
        barHead = self.barHead
        barHead._buttons.remove(widget)
        #@+<< unbind widget and drag handles >>
        #@+node:bobjack.20080506090043.3: *5* << unbind widget and drag handles >>
        widget.unbind('<ButtonPress-1>')
        widget.unbind('<ButtonRelease-1>')

        try:
            drag = widget.leoDragHandlle
        except AttributeError:
            drag = None

        if drag:
            if not isinstance(drag, (tuple, list)):
                drag = (drag,)

            for dw in drag:
                try:
                    del dw.leoDragMaster
                    dw.unbind('<ButtonPress-1>')
                    dw.unbind('<ButtonRelease-1>')
                except AttributeError:
                    g.es_exception()

        #@-<< unbind widget and drag handles >>
        widget.leoIconBar = None

        if repack:
            self.repackButtons()

        return widget
    #@+node:bobjack.20080508125414.4: *4* clear
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
    #@+node:bobjack.20080426064755.76: *4* getButton
    def getButton(self,*args,**keys):
        """Create an iconBar button."""

        if 'item_data' not in keys:
            # use hasattr & getattr to keep pylint happy.
            if hasattr(self,'item_data'):
                data = getattr(self,'item_data')
            else:
                data = {}
            # try:
                # data = self.item_data
            # except Exception:
                # data = {}
            keys['item_data'] = data


        try:
            btn = ToolbarIconButton(self.c, {}, **keys)
        finally:
            self.item_data = None

        return btn
    #@+node:bobjack.20080612150456.6: *4* getWidgetFrame
    def getWidgetFrame(self, *args, **kw):

        return ToolbarIconWidgetFrame(self.c, *args, **kw)
    #@+node:bobjack.20080429153129.36: *4* pack (show)
    def pack (self, show=True):

        """Show the icon bar by repacking it"""

        if not show:
            return self.hide()

        if not self.visible:
            self.outerFrame.pack(fill="x", pady=1)
            self.barHead.packSlaveBar()

    show = pack
    #@+node:bobjack.20080501181134.4: *4* unpack (hide)
    def unpack (self):

        """Hide the icon bar by unpacking it"""

        dummy = self.c.frame.dummyToolbarFrame

        if self.visible:
            self.outerFrame.pack_forget()
            dummy.pack()
            dummy.update_idletasks()
            dummy.pack_forget()

    hide = unpack
    #@+node:bobjack.20080504034903.2: *4* packSlaveBar
    def packSlaveBar(self):

        if self.iconFrame in self.outerFrame.pack_slaves():
            return

        self.iconFrame.pack(in_=self.outerFrame, fill='x')
    #@+node:bobjack.20080504034903.3: *4* unpackSlaveBar
    def unpackSlaveBar(self):

        if not self.slaveMaster:
            return

        if self.iconFrame in self.outerFrame.pack_slaves():
            self.iconFrame.pack_forget()
    #@+node:bobjack.20080429153129.26: *4* packWidget
    def packWidget(self, w, **kws):

        if 'side' in kws:
            del kws['side']

        try:
            w.pack(in_=self.iconFrame, side="left", **kws)

        except Exception:
            g.trace('[%s] FAILED TO PACK: \n\tWIDGET:%r\n\tin FRAME:%r' %(self.barName, w, self.iconFrame))

        return w

    #@+node:bobjack.20080429153129.27: *4* unpackWidget
    def unpackWidget(self, w):


        if w in self.iconFrame.pack_slaves():
            w.pack_forget()

        return w
    #@+node:bobjack.20080508125414.6: *4* Utility
    #@+node:bobjack.20080614200920.16: *5* getImage
    def getImage(self, path, iconBasePath=None):

        return baseClasses.getImage(path, iconBasePath)
    #@+node:bobjack.20080430064145.5: *5* uniqueSlaveName
    def uniqueSlaveName(self):

        """Return a unique name for a slaveBar of this iconBar."""

        return '%s-%02d-slave' % (self.barHead.barName, self.barHead.nSlaves)
    #@-others
#@+node:bobjack.20080616103714.2: ** class ToolbarTkToolbarClass
class ToolbarTkToolbarClass(object):

    """A class that wraps a toolbar frame which holds a collection of iconBars."""

    #@+others
    #@+node:bobjack.20080616103714.3: *3* __init__
    def __init__(self, c, parentFrame=None, toolbarName='toolbar'):

        self.c = c
        self.toolbarName = toolbarName    
        self.parentFrame = parentFrame or c.frame.outerFrame


        self.toolbarFrame = w = Tk.Frame(
            self.parentFrame,          
            height="5m",relief="flat",
        )
    #@-others
#@+node:bobjack.20080511121543.9: ** class toolbarCommandClass
class toolbarCommandClass(baseClasses.pluginCommandClass):

    """Base class for all commands defined in the toolbar.py plugin."""


#@+node:bobjack.20080618115559.5: *3* Properties
#@+node:bobjack.20080618115559.6: *4* iconbars
def getIconBars(self):

    c = self.c

    if not (c and c.exists):
        return

    return self.c.frame.iconBars[:]

iconbars = property(getIconBars)

#@+node:bobjack.20080424195922.12: ** class pluginController
class pluginController(baseClasses.basePluginController):

    """A per commander controller providing a toolbar manager."""

    commandPrefix = 'toolbar'

    #@+<< command list >>
    #@+node:bobjack.20080617170156.2: *3* << command list >>
    commandList = (
        'toolbar-delete-button',
        'toolbar-add-iconbar',
        'toolbar-hide-iconbar',


        'add-script-button',
        'show-iconbar-menu',
        'hide-iconbar-menu',
        'toggle-iconbar-menu',
        'toggle-iconbar',
    )
    #@-<< command list >>
    #@+<< default context menus >>
    #@+node:bobjack.20080617170156.3: *3* << default context menus >>
    defaultContextMenus = {

        'default-iconbar-menu': [

            ('Add Bar', 'toolbar-add-iconbar'),
            ('Add Script-Button', 'add-script-button'),
            ('Add Shortcut Button', 'add-shortcut-button'),
            ('-', ''),
            ('*', 'toolbar-hide-iconbar-menu'),
            ('-', ''),
            ('*', 'toolbar-show-iconbar-menu'),
        ], 

        'iconbar-menu': [
            ('&', 'default-iconbar-menu')
        ]

    }
    #@-<< default context menus >>

    #@+others
    #@+node:bobjack.20080617170156.10: *3* postCreate
    def postCreate(self):

        self.grabWidget = None
    #@+node:bobjack.20080428114659.20: *3* Generator Commands
    #@+node:bobjack.20080618115559.10: *4* Hide/Show/Toggle Toolbar
    #@+node:bobjack.20080428114659.21: *5* toolbar-show-iconbar-menu
    class showIconbarMenuCommandClass(toolbarCommandClass):

        """Create a menu to show hidden toolbars."""

        #@+others
        #@-others

        def doCommand(self, keywords):

            c = self.c

            if not self.assertPhase('generate'):
                return

            items = []
            for name, bar in self.iconBars.iteritems():

                if bar.visible:
                    continue

                def show_iconbar_cb(c, keywords, barName=name, show=True):
                    self.showNamedBar(barName, show)

                items.append((self.showLabel % name, show_iconbar_cb))

            if items:
                self.menu_table[:0] = items  
    #@+node:bobjack.20080618115559.2: *5* toolbar-hide-iconbar-menu
    class hideIconbarMenuCommandClass(toolbarCommandClass):

        """Create a menu to hide visible toolbars."""

        #@+others
        #@-others

        def doCommand(self, keywords):

            c = self.c

            if not self.assertPhase('generate'):
                return

            items = []
            for name, bar in self.iconBars.iteritems():

                if not bar.visible:
                    continue

                def hide_iconbar_cb(c, keywords, barName=name, show=False):
                    self.showNamedBar(barName, show)

                items.append((self.hideLabel % name, hide_iconbar_cb))

            if items:
                self.menu_table[:0] = items  
    #@+node:bobjack.20080618115559.8: *5* toolbar-toggle-iconbar-menu
    class toggleIconbarMenuCommandClass(toolbarCommandClass):

        """Create a menu to toggle visibility of toolbars."""

        #@+others
        #@-others

        def doCommand(self, keywords):

            c = self.c

            if not self.assertPhase('generate'):
                return

            items = []
            for name, bar in c.frame.iconBars.iteritems():

                if bar.visible:
                    label = self.hideLabel
                    show = False
                else:
                    label = self.showLabel
                    show = True

                def toggle_iconbar_cb(c, keywords, barName=name, show=show):
                    self.showNamedBar(barName, show)

                items.append((label % name, toggle_iconbar_cb))

            if items:
                self.menu_table[:0] = items  
    #@+node:bobjack.20080503040740.4: *5* toolbar-toggle-iconbar
    class toggleIconbarCommandClass(toolbarCommandClass):

        """Minibuffer command to toggle the visibility of an iconBar."""

        #@+others
        #@-others

        def doCommand(self, keywords):

            c = self.c
            frame = c.frame

            phase = self.phase or 'minibuffer'

            try:
                bar = keywords['bar']
            except KeyError:
                bar = frame.iconBar


            if phase == 'generate':

                label = bar.visible and self.hideLabel or self.showLabel
                self.menu_table[:0] =  [(label % bar.barName, 'toggle-iconbar')]

            elif phase in ['invoke', 'minibuffer']:

                bar.visible = not bar.visible

    #@+node:bobjack.20080426190702.2: *3* Invocation Commands
    #@+node:bobjack.20080426190702.3: *4* toolbar-delete-button
    class deleteButtonCommandClass(toolbarCommandClass):
        """Command to delete a toolbar button.

        For use only in rClick menus attached to toolbar buttons.

        """

        #@+others
        #@-others

        def doCommand(self, keywords):

            #g.trace(self.__class__.__name__)

            if self.minibufferPhaseError():
                return

            try:
                keywords['button'].deleteButton()

            except Exception as e:
                g.es_error('failed to delete button')
                g.es_exception()
    #@+node:bobjack.20080428114659.11: *4* toolbar-add-iconbar
    class addIconbarCommandClass(toolbarCommandClass):

        """Command to add a new iconBar."""

        #@+others
        #@+node:bobjack.20080429153129.21: *5* uniqueBarName
        def uniqueBarName(self, prefix):

            iconBars = self.c.frame.iconBars

            if not prefix in iconBars:
                return prefix

            for i in range(1,100):
                barName = '%s.%s' %(prefix, i)
                if barName not in iconBars:
                    return barName

        #@-others

        def doCommand(self, keywords):

            c = self.c
            frame = c.frame

            try:
                bar = keywords['bar']
                barName = bar.barName 
            except KeyError:
                barName = 'iconbar'

            newbarName = self.uniqueBarName(barName)

            frame.createIconBar(newbarName)



    #@+node:bobjack.20080428114659.16: *4* toolbar-hide-iconbar
    class hideIconbarCommandClass(toolbarCommandClass):

        """Minibuffer command to hide an iconBar."""

        #@+others
        #@-others

        def doCommand(self, keywords):

            c = self.c
            frame = c.frame

            try:
                bar = keywords['bar']
            except KeyError:
                bar = frame.iconBars['iconbar']

            bar.hide()

    #@+node:bobjack.20080428114659.17: *4* toolbar-add-script-button
    class addScriptButtonCommandClass(toolbarCommandClass):

        """Add a script-button to the selected iconBar.

        This command is for use in in iconBar rClick menus, the script-button will
        be added to the bar that recieved the click.

        It may also be used as a minibufer command, in which case a script-button
        will be added to the default 'iconbar'.

        """
        #@+others
        #@-others

        def doCommand(self, keywords):

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

    #@+node:bobjack.20080429153129.28: *3* Utility
    #@-others

#@-others
#@-leo

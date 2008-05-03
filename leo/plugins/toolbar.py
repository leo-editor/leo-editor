#@+leo-ver=4-thin
#@+node:bobjack.20080507083323.2:@thin toolbar.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:bobjack.20080424190906.12:<< docstring >>
"""A plugin to extend the functionality of Leo's iconbar.

This plugin provides mutltiple iconBars each of which can consist of a
number of slave iconBars

Each iconBar is assigned a name, the default iconBar is called 'iconbar'.

A dictionary mapping namse to iconBar objects is kept in c.frame.iconBars.


The iconBars in this dictionary are the heads of linked lists of slave iconBars.

The slave iconBars have these properties.

    - barName

    - barHead: this points to the first bar in the list, the one that
      appears in the iconBars dict.

    - barMaster: this points back to the previous slave which is the
      master of this one.

    - barSlave: points forward to the next slave bar

    - iconFrame: the Frame object into which the widgets are packed.

    - buttonCount: the number of widgets packed into the frame.

    - 
"""
#@nonl
#@-node:bobjack.20080424190906.12:<< docstring >>
#@nl

__version__ = "0.6"
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
        leoTkinterFrame.leoTkinterTreeTab = ToolbarTkinterTreeTab
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
#@+node:bobjack.20080501055450.5:class ToolbarTkinterTreeTab
class ToolbarTkinterTreeTab (leoTkinterFrame.leoTkinterTreeTab):

    '''A class representing a tabbed outline pane drawn with Tkinter.'''

    #@    @+others
    #@+node:bobjack.20080501055450.8:tt.createControl
    def createControl (self):


        tt = self ; c = tt.c

        # Create the main container.
        tt.frame = Tk.Frame(c.frame.top)

        #c.frame.tt.frame.pack(side="left")
        c.frame.addIconWidget(tt.frame)

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
    #@-node:bobjack.20080501055450.8:tt.createControl
    #@-others
#@nonl
#@-node:bobjack.20080501055450.5:class ToolbarTkinterTreeTab
#@+node:bobjack.20080428114659.2:class ToolbarTkinterFrame
class ToolbarTkinterFrame(leoTkinterFrame.leoTkinterFrame, object):

    #@    @+others
    #@+node:bobjack.20080428114659.3:__init__
    def __init__(self, *args, **kw):

        self.iconBars= {}
        self.toolbarFrame = None
        super(ToolbarTkinterFrame, self).__init__(*args, **kw)
    #@-node:bobjack.20080428114659.3:__init__
    #@+node:bobjack.20080429153129.29:Icon area convenience methods
    #@+node:bobjack.20080429153129.30:addIconButton
    def addIconButton (self,*args,**keys):

        """Create and add an icon button to the named toolbar.

        keys['barname'] gives the name of the toolbar or the
        tollbar named 'iconbar' is used.

        """

        if 'barName' in keys:
            barName = keys['barName']
            del keys['barName']

        else:
             barName = 'iconbar'

        return self.iconBars[barName].add(*args,**keys)
    #@-node:bobjack.20080429153129.30:addIconButton
    #@+node:bobjack.20080501055450.16:addIconWidget
    def addIconWidget (self, widget, barName='iconbar'):

        """Adds a widget to the named toolbar."""

        return self.iconBars[barName].addWidget(widget)
    #@-node:bobjack.20080501055450.16:addIconWidget
    #@+node:bobjack.20080429153129.31:clearIconBar
    def clearIconBar (self, barName='iconbar'):

        self.iconBars[barName].clear()
    #@-node:bobjack.20080429153129.31:clearIconBar
    #@+node:bobjack.20080429153129.32:createIconBar
    def createIconBar (self, barName='iconbar', after=None, slaveMaster=None):

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
    #@+node:bobjack.20080502134903.10:New icon bar convenience methods
    #@+node:bobjack.20080502134903.11:getIconWidgets
    def getIconButtons(self, barName='iconbar '):

        return self.iconBars[barName].getButtons()
    #@-node:bobjack.20080502134903.11:getIconWidgets
    #@+node:bobjack.20080502134903.12:setIconWidgets
    #@-node:bobjack.20080502134903.12:setIconWidgets
    #@+node:bobjack.20080502134903.13:NewHeadline
    #@-node:bobjack.20080502134903.13:NewHeadline
    #@-node:bobjack.20080502134903.10:New icon bar convenience methods
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

        if hasattr(button, 'leoIconBar'):
            button.leoIconBar.removeWidget(button)

        scripting.deleteButton(self, button)
    #@-node:bobjack.20080426064755.77:deleteButton
    #@+node:bobjack.20080430160907.2:createIconButton
    def createIconButton (self,text,command,shortcut,statusLine,bg):

        '''Create an icon button.  All icon buttons get created using this utility.

        - Creates the actual button and its balloon.
        - Adds the button to buttonsDict.
        - Registers command with the shortcut.
        - Creates x amd delete-x-button commands, where x is the cleaned button name.
        - Binds a right-click in the button to a callback that deletes the button.'''

        c = self.c ; k = c.k

        # Create the button and add it to the buttons dict.
        commandName = self.cleanButtonText(text).lower()

        # Truncate only the text of the button, not the command name.
        truncatedText = self.truncateButtonText(commandName)
        if not truncatedText.strip():
            g.es_print('%s ignored: no cleaned text' % (text.strip() or ''),color='red')
            return None

        # Command may be None.
        b = self.iconBar.add(text=truncatedText,command=command,bg=bg)
        if not b: return None

        self.buttonsDict[b] = truncatedText

        if statusLine:
            self.createBalloon(b,statusLine)

        # Register the command name if it exists.
        if command:
            k.registerCommand(commandName,shortcut=shortcut,func=command,pane='button',verbose=shortcut)

        # Define the callback used to delete the button.
        def deleteButtonCallback(event=None,self=self,b=b):
            self.deleteButton(b, event=event)

        if self.gui.guiName() == 'tkinter':
            # Bind right-clicks to deleteButton.
            b.bind('<3>',deleteButtonCallback)

        # Register the delete-x-button command.
        deleteCommandName= 'delete-%s-button' % commandName
        k.registerCommand(deleteCommandName,shortcut=None,
            func=deleteButtonCallback,pane='button',verbose=False)
            # Reporting this command is way too annoying.

        return b
    #@nonl
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

        g.trace()

        w = e.widget        

        if hasattr(w, 'leoIconBar'):

            self.c.theToolbarController.grabWidget = w
    #@-node:bobjack.20080503090121.5:onPress
    #@+node:bobjack.20080503090121.6:onRelease
    def onRelease(self, e):


        try:

            c = self.c
            controller = c.theToolbarController

            target = e.widget.winfo_containing(e.x_root, e.y_root)

            try:
                tBar = target.leoIconBar
            except:
                tBar = None


            g.trace(tBar)
            if tBar:

                source = controller.grabWidget

                g.trace('tbar' , tBar)
                g.trace(source)


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



    #@+node:bobjack.20080507083323.4:repackButons
    def repackButtons(self, trace=None):

        bar = self.barHead

        if bar.inConfigure:
           return

        try:
            bar.doRepackButtons()
        finally:
            bar.inConfigure = False
    #@-node:bobjack.20080507083323.4:repackButons
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
            if bar not in bars and bar.buttonCount:
                bar.pack()
            bar = bar.slaveBar
        #@nonl
        #@-node:bobjack.20080502134903.4:<< repack all widgets >>
        #@nl
        #@    << hide empty slave bars >>
        #@+node:bobjack.20080502134903.5:<< hide empty slave bars >>
        while bar :
            if bar in bars:
                bar.iconFrame.pack_forget()
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
    #@-node:bobjack.20080429153129.16:onConfigure
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

        return self.barHead._buttons

    buttons = property(getButtons)
    #@-node:bobjack.20080501125812.5:buttons
    #@+node:bobjack.20080501181134.5:visible
    def getVisible(self):

        """Is the toolbar, of which this iconBar is a slave, packed."""

        barHead = self.barHead
        return barHead._outerFrame in barHead.parentFrame.pack_slaves()

    visible = property(getVisible)
    #@-node:bobjack.20080501181134.5:visible
    #@-node:bobjack.20080430160907.4:Properties
    #@+node:bobjack.20080426064755.76:add
    def add(self,*args,**keys):

        try:
            data = self.item_data
        except Exception:
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
            btn = self._add(self, *args, **keys)
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
    #@+node:bobjack.20080429153129.17:_add
    def _add(self,*args,**keys):

        """Add a button containing text or a picture to the icon bar.

        Pictures take precedence over text"""

        c = self.c ; f = c.frame.top
        text = keys.get('text')
        imagefile = keys.get('imagefile')
        image = keys.get('image')
        command = keys.get('command')
        bg = keys.get('bg')

        if not imagefile and not image and not text: return

        # First define n.
        try:
            g.app.iconWidgetCount += 1
            n = g.app.iconWidgetCount
        except Exception:
            n = g.app.iconWidgetCount = 1

        if not command:
            def commandCallback():
                print "command for widget %s" % (n)
            command = commandCallback

        if imagefile or image:
            #@        << create a picture >>
            #@+node:bobjack.20080429153129.18:<< create a picture >>
            try:
                if imagefile:
                    # Create the image.  Throws an exception if file not found
                    imagefile = g.os_path_join(g.app.loadDir,imagefile)
                    imagefile = g.os_path_normpath(imagefile)
                    image = Tk.PhotoImage(master=g.app.root,file=imagefile)

                    # Must keep a reference to the image!
                    try:
                        refs = g.app.iconImageRefs
                    except Exception:
                        refs = g.app.iconImageRefs = []

                    refs.append((imagefile,image),)

                if not bg:
                    bg = f.cget("bg")

                b = Tk.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
                self.addWidget(b)
                #b.pack(in_=self.iconFrame, side="left",fill="y")
                return b

            except Exception:
                g.es_exception()
                return None
            #@-node:bobjack.20080429153129.18:<< create a picture >>
            #@nl
        elif text:
            b = Tk.Button(f,text=text,relief="groove",bd=2,command=command)
            if not self.font:
                self.font = c.config.getFontFromParams(
                    "button_text_font_family", "button_text_font_size",
                    "button_text_font_slant",  "button_text_font_weight",)
            b.configure(font=self.font)
            # elif sys.platform.startswith('win'):
                # width = max(6,len(text))
                # b.configure(width=width,font=('verdana',7,'bold'))
            if bg: b.configure(bg=bg)

            self.addWidget(b)

            return b

        return None
    #@-node:bobjack.20080429153129.17:_add
    #@-node:bobjack.20080426064755.76:add
    #@+node:bobjack.20080430160907.11:addWidget
    def addWidget(self, widget, index=None):


        barHead = self.barHead
        buttons = barHead._buttons

        widget.bind('<ButtonPress-1>', barHead.onPress)
        widget.bind('<ButtonRelease-1>', barHead.onRelease)

        widget.leoIconBar = barHead


        try:
            index = int(index)
        except:
            index = None

        if index is not None and index>=0 and index<len(buttons):
            buttons.insert(index, widget)
        else:
            buttons.append(widget)

        self.repackButtons()

    #@-node:bobjack.20080430160907.11:addWidget
    #@+node:bobjack.20080501181134.3:removeWidget
    def removeWidget(self, widget):

        """Remove widget from the list of manged widgets and repack the buttons."""

        barHead = self.barHead

        barHead._buttons.remove(widget)

        widget.unbind('<ButtonPress-1>')
        widget.unbind('<ButtonRelease-1>')

        del widget.leoIconBar

        self.repackButtons()
    #@-node:bobjack.20080501181134.3:removeWidget
    #@+node:bobjack.20080429153129.36:pack (show)
    def pack (self, after=None):

        """Show the icon bar by repacking it"""

        outerFrame = self.outerFrame

        if not self.slaveMaster:

            toolbars = self.parentFrame.pack_slaves()

            if not outerFrame in toolbars:
                if after and after in toolbars:
                    outerFrame.pack(fill="x", pady=2, after=after)
                else:
                    outerFrame.pack(fill="x", pady=2)

        if self.iconFrame not in outerFrame.pack_slaves():
            self.iconFrame.pack(in_=outerFrame, fill='x')

    show = pack
    #@-node:bobjack.20080429153129.36:pack (show)
    #@+node:bobjack.20080501181134.4:unpack (hide)
    def unpack (self):

        """Hide the icon bar by unpacking it"""

        if self.visible:
            self.outerFrame.pack_forget()
            self.c.frame.dummyToolbarFrame.pack()
            self.iconFrame.update_idletasks()
            self.c.frame.dummyToolbarFrame.pack_forget()

    hide = unpack
    #@-node:bobjack.20080501181134.4:unpack (hide)
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

    #@-node:bobjack.20080426064755.79:getImage
    #@+node:bobjack.20080430064145.5:uniqueSlaveName
    def uniqueSlaveName(self):

        """Return a unique name for a slaveBar of this iconBar."""

        barHead = self.barHead
        name = self.barName
        return '%s-%02d-slave' % (name, barHead.nSlaves)
    #@-node:bobjack.20080430064145.5:uniqueSlaveName
    #@+node:bobjack.20080503090121.4:update
    #@-node:bobjack.20080503090121.4:update
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

        """Initialize rclick functionality for this commander.

        This only initializes ivars, the proper setup must be done by calling the
        controllers onCreate method from the module level onCreate function. This is
        to make unit testing easier.

        """

        self.c = c

        self.mb_retval = None
        self.mb_keywords = None

        if not hasattr(c, 'context_menus'):
            return

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

            cb = self.universalCommandCallback(function)

            lst.append((command, methodName, cb))

        return lst
    #@-node:bobjack.20080424195922.16:createCommandCallbacks
    #@+node:bobjack.20080503090121.2:universalCommandCallback
    def universalCommandCallback(self, function):

        """Create a universal command callback.

        Create and return a callback that wraps function and adapts
        the minibuffer command callback to a function that has the
        rClick type signature.

        When a function or method is wrapped in this way it can be
        used as a standard minibuffer command regardless of whether
        rclick is enabled or not and if its enabled then the
        command can be used for rClick either as a generator command
        or  an invocation

        """
        def minibufferCallback(event, function=function):

            try:
                cm = self.c.theContextMenuController
            except AttributeError:
                cm = None

            if cm:
                cm.mb_retval = function(cm.mb_keywords)
            else:
                keywords = {'mb_event': event}
                return function(keywords)

        return minibufferCallback
    #@-node:bobjack.20080503090121.2:universalCommandCallback
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

        visible = bar.visible

        barShow = "Show IconBar\nicon=Tango/16x16/actions/add.png"
        barHide = "Hide IconBar\nicon=Tango/16x16/actions/remove.png"

        if phase == 'generate':

            label = visible and barHide or barShow
            menu_table = keywords['rc_menu_table']
            menu_table[:0] =  [(label, 'toggle-iconbar')]

        elif phase in ['invoke', 'minibuffer']:

            if visible:
                bar.hide()
            else:
                bar.show()

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
            button = keywords['event'].widget
            self.c.theScriptingController.deleteButton(button)
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
#@-node:bobjack.20080507083323.2:@thin toolbar.py
#@-leo

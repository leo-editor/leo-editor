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
    #@+node:bobjack.20080428114659.3:def __init__
    def __init__(self, *args, **kw):

        self.iconBars= {}
        self.toolbarFrame = None
        super(ToolbarTkinterFrame, self).__init__(*args, **kw)
    #@-node:bobjack.20080428114659.3:def __init__
    #@+node:bobjack.20080429153129.29:Icon area convenience methods
    #@+node:bobjack.20080429153129.30:addIconButton
    def addIconButton (self,*args,**keys):

        barName = ''
        if 'barName' in keys:
            barName = keys['barName']
            del keys['barName']

        if not barName:
             barName = 'iconbar'

        if barName in self.iconBars:
            return self.iconBars[barName].add(*args,**keys)
    #@-node:bobjack.20080429153129.30:addIconButton
    #@+node:bobjack.20080501055450.16:addIconWidget
    def addIconWidget (self, widget, barName=''):

        if not barName:
             barName = 'iconbar'

        if barName in self.iconBars:
            return self.iconBars[barName].addWidget(widget)
    #@nonl
    #@-node:bobjack.20080501055450.16:addIconWidget
    #@+node:bobjack.20080429153129.31:clearIconBar
    def clearIconBar (self, barName='iconbar'):

        if barName in self.iconBars:
            self.iconBars[barName].clear()
    #@-node:bobjack.20080429153129.31:clearIconBar
    #@+node:bobjack.20080429153129.32:createIconBar
    def createIconBar (self, barName='iconbar', after=None, slaveMaster=None):

        frame = self.createToolbarFrame()

        if not barName in self.iconBars:

            self.iconBars[barName] = self.iconBarClass(
                self.c, frame, barName=barName, slaveMaster=slaveMaster
            )

        if barName == 'iconbar':
            self.iconBar = self.iconBars[barName]

        return self.iconBars[barName]

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

        if barName in self.iconBars:
            self.iconBars[barName].hide()
    #@-node:bobjack.20080429153129.35:hideIconBar
    #@-node:bobjack.20080429153129.29:Icon area convenience methods
    #@+node:bobjack.20080428114659.5:createToolbarFrame
    def createToolbarFrame(self):

        if self.toolbarFrame:
            return self.toolbarFrame

        self.toolbarFrame = w = Tk.Frame(self.outerFrame)

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
            g.trace('Exception')
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

        def addScriptButtonCallback(event=None, self=self, barName=barName):
            return self.addScriptButtonCommand(event, barName)

        self.createIconButton(
            text='script-button',
            command = addScriptButtonCallback,
            shortcut=None,
            statusLine='Make script button from selected node',
            bg="#ffffcc",
        )
    #@+node:bobjack.20080428114659.13:addScriptButtonCommand
    def addScriptButtonCommand (self,event=None, barName='iconbar'):

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

        if barName not in frame.iconBars:
            return

        oldIconBar = frame.iconBar
        try:
            frame.iconBar =  frame.iconBars[barName]       
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
    def __init__(self, c, parentFrame, barName='iconBar', after=None, slaveMaster=None):

        """Initialize an iconBar."""

        self.c = c
        self.barName = barName    
        self.parentFrame = parentFrame

        self._buttons = [] # control var for buttons dictionary

        self.slaveBar = None
        self.slaveMaster = slaveMaster
        self._outerFrame = None  # control var for outerFrame property

        self.font = None
        self.visible = False
        self.lastActual = 0
        self.enableConfigure = not slaveMaster

        self.xPad = 2

        if not slaveMaster :

            self.outerFrame = w = Tk.Frame(
                self.parentFrame,          
                height="5m", bd=2, relief="groove"
            )
            w.leoParent = self
            w.bind('<Button-3>', self.onToolbarRightClick)

        self.iconFrame = w = Tk.Frame(
            self.parentFrame,          
            height="5m",relief="flat",
        )
        w.leoParent = self
        w.bind('<Button-3>', self.onRightClick)

        self.c.frame.iconFrame = self.iconFrame #FIXME

        self.pack(after=after)
        c.frame.top.update_idletasks()

        if not slaveMaster:
            self.iconFrame.bind('<Configure>', self.onConfigure)

    #@-node:bobjack.20080428114659.6:__init__
    #@+node:bobjack.20080501125812.4:__len__
    def __len__(self):
        return len(self.barHead._buttons)
    #@nonl
    #@-node:bobjack.20080501125812.4:__len__
    #@+node:bobjack.20080428114659.9:onRightClick
    def onRightClick(self, event):

        """Respond to a right click on any of the components of the toolbar."""

        g.doHook('rclick-popup', c=self.c, event=event,
            context_menu='default-iconbar-menu', bar=self.barHead
        )
    #@-node:bobjack.20080428114659.9:onRightClick
    #@+node:bobjack.20080501125812.2:onToolbarRightClick
    def onToolbarRightClick(self, event):

        """Respond to a right click on the toolbar."""

        g.trace('############# toolbar clicked %s ###########'%event.widget.leoParent)


    #@-node:bobjack.20080501125812.2:onToolbarRightClick
    #@+node:bobjack.20080429153129.16:onConfigure
    def onConfigure(self, event):

        g.trace()

        self.repackButtons()


    #@+node:bobjack.20080430160907.12:repackButtons
    def repackButtons(self, trace=False):

        """Repack all the buttons in this toolbar.

        New slave iconBars will be created if needed to make sure all buttons are
        visible. Empty slaves will be hidden but not removed.

        """

        g.trace(trace)

        barHead = self.getBarHead()

        orphans = barHead._buttons[:]

        # unpack all widgets

        for widget in self.getAllSlaveButtons():
            widget.pack_forget()

        # repack all widgets

        bar = barHead
        while bar:
            orphans = bar.repackHelper(orphans)
            bar = bar.slaveBar

        # make sure all occupied slaves are packed

        bars = self.slaveBars
        bar = self
        while bar:
            if bar not in bars and bar.iconFrame.pack_slaves():
                bar.pack()
            bar = bar.slaveBar

        #make sure all empty slave bars are unpacked

        bar = self.barTail
        while bar :
            if bar in bars and not bar.iconFrame.pack_slaves():
                bar.iconFrame.pack_forget()
            bar = bar.slaveMaster
    #@+node:bobjack.20080429153129.24:repackHelper
    def repackHelper(self, orphans):

        """Pack as many 'orphan' buttons into this bar as possible

        Return a list of orphans that could not be packed.

        """

        iconFrame = self.iconFrame

        actual = iconFrame.winfo_width()
        req = 0

        nOrphans = len(orphans)
        for widget in orphans[:]:

            req += widget.winfo_width() + self.xPad

            if req > actual:
                break

            orphans.pop(0)
            widget.pack(in_=iconFrame, side="left")

        if nOrphans and nOrphans == len(orphans):
            # we must pack at least one widget even if its too big
            widget = orphans.pop(0)
            widget.pack(in_=iconFrame, side="left")

        if not self.slaveBar and orphans:
            self.slaveBar = self.createSlaveBar()

        return orphans

    #@-node:bobjack.20080429153129.24:repackHelper
    #@-node:bobjack.20080430160907.12:repackButtons
    #@+node:bobjack.20080430064145.3:createSlaveBar
    def createSlaveBar(self):

        """Create a slave iconBar for this bar and home as many orphans as possible.

        It is an error to call this if the bar already has a slaveBar.
        """

        assert not self.slaveBar, 'Already have a slaveBar.'

        barName = self.uniqueSlaveName()

        self.slaveBar = slaveBar = self.c.frame.createIconBar(
            barName, slaveMaster=self
        )

        return slaveBar 
    #@nonl
    #@-node:bobjack.20080430064145.3:createSlaveBar
    #@-node:bobjack.20080429153129.16:onConfigure
    #@+node:bobjack.20080430160907.4:Properties
    #@+node:bobjack.20080430160907.5:outerFrame
    def getOuterFrame(self):

        """Get the frame that contains this bar and its companion slaves."""

        return self.getBarHead()._outerFrame

    def setOuterFrame(self, value):

       self.getBarHead()._outerFrame = value

    outerFrame = property(getOuterFrame, setOuterFrame)
    #@-node:bobjack.20080430160907.5:outerFrame
    #@+node:bobjack.20080430064145.4:barHead
    def getBarHead(self):

        bar = self
        while bar.slaveMaster:
            bar = bar.slaveMaster

        return bar

    barHead = property(getBarHead)

    #@-node:bobjack.20080430064145.4:barHead
    #@+node:bobjack.20080430160907.10:barTail
    def getBarTail(self):

        bar = self
        while bar.slaveBar:
            bar = bar.slaveBar

        return bar


    barTail = property(getBarTail)

    #@-node:bobjack.20080430160907.10:barTail
    #@+node:bobjack.20080501125812.3:barEnd
    def getBarEnd(self):

        bar = lastBar = self
        while bar.slaveBar:
            bar = bar.slaveBar
            if not bar.slaveButtons:
                break
            lastBar = self

        return lastBar


    barEnd = property(getBarEnd)
    #@nonl
    #@-node:bobjack.20080501125812.3:barEnd
    #@+node:bobjack.20080501113939.2:slaveBars
    def getSlaveBars(self):

        """Get a list of slave iconBars packed in this toolbar."""

        return [ bar.leoParent for bar in self.outerFrame.pack_slaves()]


    slaveBars = property(getSlaveBars)
    #@-node:bobjack.20080501113939.2:slaveBars
    #@+node:bobjack.20080501055450.2:slaveButtons
    def getSlaveButtons(self):

        """Get a list of widgets packed in this iconBar."""

        # g.trace()
        # for i, w in enumerate(self.iconFrame.pack_slaves()):
            # print '\t', i, repr(w)

        return [ btn for btn in self.iconFrame.pack_slaves()]


    slaveButtons = property(getSlaveButtons)
    #@-node:bobjack.20080501055450.2:slaveButtons
    #@+node:bobjack.20080501113939.3:allSlaveButtons
    def getAllSlaveButtons(self,  shrink=False):

        """Make a list of all widgets in this toolbar and the bar each came from."""

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

        return self.barHead._buttons

    buttons = property(getButtons)
    #@-node:bobjack.20080501125812.5:buttons
    #@-node:bobjack.20080430160907.4:Properties
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
        except:
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
                    except:
                        refs = g.app.iconImageRefs = []

                    refs.append((imagefile,image),)

                if not bg:
                    bg = f.cget("bg")

                b = Tk.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
                self.addWidget(b)
                #b.pack(in_=self.iconFrame, side="left",fill="y")
                return b

            except:
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
    def addWidget(self, widget):

        g.trace(len(self.buttons))

        self.barHead._buttons.append(widget)
        self.repackButtons('addWidget')

    #@-node:bobjack.20080430160907.11:addWidget
    #@+node:bobjack.20080429153129.36:pack (show)
    def pack (self, after=None):

        """Show the icon bar by repacking it"""

        outerFrame = self.outerFrame

        if not self.slaveMaster:

            toolbars = self.parentFrame.pack_slaves()

            if not outerFrame in toolbars:
                self.visible = True
                if after and after in toolbars:
                    outerFrame.pack(fill="x", pady=2, after=after)
                else:
                    outerFrame.pack(fill="x", pady=2)

        if self.iconFrame not in outerFrame.pack_slaves():
            self.iconFrame.pack(in_=outerFrame, fill='x')

    show = pack
    #@-node:bobjack.20080429153129.36:pack (show)
    #@+node:bobjack.20080429153129.26:packWidget
    def packWidget(self, w, **kws):

        if 'side' in kws:
            del kws['side']

        try:
            w.pack(in_=self.iconFrame, side="left", **kws)

        except:
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
    #@+node:bobjack.20080430064145.5:uniqueSlaveName
    def uniqueSlaveName(self):

        """Return a unique name for a slaveBar of this iconBar."""

        c = self.c
        frame = c.frame

        name = self.barHead.barName

        for i in range(1,100):
            newbarName = '%s-%02d-slave' % (name,i)
            if not newbarName in frame.iconBars:
                return newbarName
    #@-node:bobjack.20080430064145.5:uniqueSlaveName
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

        barName = keywords.get('toolbar')

        names = frame.iconBars.keys()

        items = []
        while names:
            name = names.pop(0)

            if name.endswith('-slave') or name == barName:
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
            bar = keywords.get('bar')
        except:
            g.trace('error')
            bar = None

        barName = ''
        if bar:
            barName = bar.barName

        if not barName:
            barName='iconbar'

        newbarName = self.uniqueBarName(barName)

        if newbarName:
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
            keywords['bar'].hide()
        except:
            g.trace('error')
            pass

    #@-node:bobjack.20080428114659.16:toolbar_hide_iconbar
    #@+node:bobjack.20080428114659.17:toolbar_add_script_button
    def toolbar_add_script_button(self, keywords):

        """Add a sript-button to the selected iconBar.

        This is for use in iconBar rClick menus, but may
        also be used as a minibufer command, in which case
        it will always add the script button to the iconBar
        named 'iconbar' if it exists.
        """
        c = self.c
        frame = c.frame
        iconBars = frame.iconBars

        try:
            bar = keywords.get('bar')    
        except:
            g.trace('error')
            bar = None

        if not bar:
            bar = iconBars.get('iconbar')

        if not bar or bar.barName not in iconBars:
            return

        oldIconBar = frame.iconBar

        try:
            frame.iconBar = frame.iconBars[bar.barName]
            sm = c.theScriptingController
            sm.createScriptButtonIconButton(bar.barName) 
        finally:
            frame.iconBar = oldIconBar


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

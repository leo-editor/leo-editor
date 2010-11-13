#@+leo-ver=5-thin
#@+node:bobjack.20080619110105.2: * @file rClickBasePluginClasses.py
#@+<< docstring >>
#@+node:bobjack.20080614200920.8: ** << docstring >>
""" Provides base classes for plugins.

This is an experimental set of base classes for plugins.

They are primarily meant for use in rClick and toolbar 
but may be used in other plugins.

""" 
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = '0.2'
#@+<< version history >>
#@+node:bobjack.20080614200920.9: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 bobjack:
#     - initial version
# 0.2 bobjack:
#     - seperated defaultContextMenus data from setDefaultContextMenus method
#@-<< version history >>

#@+<< imports >>
#@+node:bobjack.20080614200920.10: ** << imports >>
import leo.core.leoGlobals as g

try:
    from PIL import Image
    from PIL import ImageTk
except ImportError:
    Image = ImageTk = None
#@-<< imports >>

iconCache = {}

defaultIconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

#@+others
#@+node:bobjack.20080614200920.11: ** init
def init ():
    """This is not a plugin so never allow it to load."""

    return False



#@+node:bobjack.20080614200920.13: ** getImage
def getImage(path, iconBasePath=None):

    """Use PIL to get an image suitable for displaying in menus."""

    iconBasePath = iconBasePath or defaultIconBasePath

    if not (Image and ImageTk):
        return None

    path = g.os_path_normpath(path)

    try:
        return iconCache[path]
    except KeyError:
        pass

    iconpath = g.os_path_join(iconBasePath, path)

    try:
        return iconCache[iconpath]
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

    if not image or not image.height() >0:
        g.es('Bad Icon: %s' % path)
        return None

    iconCache[path] = image

    return image

#@+node:bobjack.20080511155621.3: ** class pluginCommandClass
class pluginCommandClass(object):

    """Base class for commands defined in plugins."""


    showLabel = "Show %s\nicon=Tango/16x16/actions/add.png"
    hideLabel = "Hide %s\nicon=Tango/16x16/actions/remove.png"


    def __init__(self, controller, **keys):

        self.c = controller.c
        self.controller = controller
        self.keys = keys

        self.wrappedDoCommand = self.preDoCommand
        self.wrapCommand(self.c.universallCallback)


    def __call__(self, event):
        self.wrappedDoCommand(event)

    def wrapCommand(self, wrapper):
        self.wrappedDoCommand = wrapper(self.wrappedDoCommand)

    def preDoCommand(self, keywords):
        self.keywords = keywords
        self.doCommand(keywords)
        #g.trace(self.keywords)

    #@+others
    #@+node:bobjack.20080513085207.4: *3* Properties
    #@+node:bobjack.20080513085207.5: *4* phase
    def getPhase(self):

        return self.keywords.get('rc_phase')

    phase = property(getPhase)
    #@+node:bobjack.20080617170156.12: *4* menu_table
    def getMenuTable(self):

        return self.keywords.get('rc_menu_table')

    menu_table = menuTable = property(getMenuTable) 

    #@+node:bobjack.20080516105903.108: *4* item_data
    def getItemData(self):

        item_data = self.keywords.get('rc_item_data', None)
        if item_data is None:
            self.keywords['rc_item_data'] = item_data = {}
        return item_data

    item_data = property(getItemData)
    #@+node:bobjack.20080618115559.12: *4* iconBars
    def getIconBars(self):

        return self.c.frame.iconBars

    iconBars = property(getIconBars)
    #@+node:bobjack.20080513085207.6: *3* phaseError
    def phaseError(self):

        g.es_error('command not valid in phase: %s'%self.phase)
    #@+node:bobjack.20080618115559.11: *3* assertPhase
    def assertPhase(self, *args):

        if self.phase in args:
            return True

        self.phaseError()
    #@+node:bobjack.20080513085207.7: *3* minibufferPhaseError
    def minibufferPhaseError(self):

        if self.phase == 'minibuffer':
            self.phaseError()
            return True
    #@+node:bobjack.20080618115559.16: *3* showNamedBar
    def showNamedBar(self, barName='iconbar', show=True):

        bar = self.c.frame.iconBars.get(barName)

        if bar:
            bar.visible = show
    #@+node:bobjack.20080618181754.2: *3* getNamedBar
    def getNamedBar(self, barName='iconbar', show=True):

        return self.c.frame.iconBars.get(barName)
    #@-others
#@+node:bobjack.20080323045434.14: ** class basePluginController
class basePluginController(object):

    """A base class for per commander pluginControllers."""


    iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

    #@+others
    #@+node:bobjack.20080323045434.15: *3* __init__
    def __init__(self, c):

        """Initialize base functionality for this commander.

        This only initializes ivars, the proper setup must be done by calling onCreate
        in onCreate. This is to make unit testing easier.

        """

        self.c = c

        self.commandsDict = None

        try:
            cm = c.context_menus
        except:
            c.context_menus = {}
    #@+node:bobjack.20080423205354.3: *4* onCreate
    def onCreate(self):

        c = self.c

        self.preCreate()

        self.registerCommands()
        self.setDefaultContextMenus()

        self.postCreate()
    #@+node:bobjack.20080617170156.9: *4* preCreate
    def preCreate(self, *args, **kw):

        pass
    #@+node:bobjack.20080617170156.8: *4* postCreate
    def postCreate(self, *args, **kw):

        pass
    #@+node:bobjack.20080424195922.7: *4* onClose
    def onClose(self):
        """Clean up and prepare to die."""

        pass
    #@+node:bobjack.20080511155621.6: *4* getPublicCommands
    def getPublicCommands(self):

        """Create command instances for public commands provided by this plugin.

        Returns a dictionary {commandName: commandInstance, ...}

        """
        if self.commandsDict:
            return self.commandsDict

        commandsDict = {}

        for commandName in self.commandList:
            #@+<< get className from commandName >>
            #@+node:bobjack.20080512054154.2: *5* << get className from commandName >>
            # change my-command-name to myCommandNameCommandClass

            className = commandName.split('-')

            if className[0] == self.commandPrefix:
                alias = ''
                del className[0]
            else:
                alias = commandName
                commandName = self.commandPrefix + '-' + commandName

            for i in range(1, len(className)):
                className[i] = className[i].capitalize()

            className = ''.join(className) + 'CommandClass'
            #@-<< get className from commandName >>
            klass = getattr(self, className)

            cmd = klass(self)

            commandsDict[commandName] = cmd
            if alias:
                commandsDict[alias] = cmd

        self.commandsDict = commandsDict

        return commandsDict

    #@+node:bobjack.20080511155621.9: *4* registerCommands
    def registerCommands(self):

        """Create callbacks for minibuffer commands and register them."""

        c = self.c

        commandsDict = self.getPublicCommands()

        for commandName, cmd in commandsDict.iteritems():

            def rclickBaseCommandCallback(event, func=cmd):
                return func(event)

            c.k.registerCommand(commandName, shortcut=None, func=rclickBaseCommandCallback)   

    #@+node:bobjack.20080423205354.5: *4* getCommandList
    def getCommandList(self):

        return self.commandList
    #@+node:bobjack.20080617170156.4: *4* setDeafaultContextMenus
    def setDefaultContextMenus(self):

        """Set menus for context menus that have not been defined in @popup menus."""

        c = self.c

        for k, v in self.defaultContextMenus.iteritems():
            if k in c.context_menus:
                continue
            c.context_menus[k] = v

    #@+node:bobjack.20080617170156.5: *4* copyMenuTable
    def copyMenuTable(self, menu_table):

        """make a copy of the menu_table and make copies of its submenus.

        It is the menu lists that are being copied we are not deep copying
        objects contained in those lists.

        """

        def _deepcopy(menu):

            table = []
            for item in menu:
                label, cmd = item
                if isinstance(cmd, list):
                    cmd = _deepcopy(cmd)
                    item = (label, cmd)
                table.append(item)

            return table

        newtable =  _deepcopy(menu_table)

        return newtable

    #@+node:bobjack.20080614200920.14: *3* getImage
    def getImage(self, path, iconBasePath=None):

        return getImage(path, iconBasePath)
    #@-others

#@-others
#@-leo

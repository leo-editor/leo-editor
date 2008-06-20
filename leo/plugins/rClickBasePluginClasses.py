#@+leo-ver=4-thin
#@+node:bobjack.20080619110105.2:@thin rClickBasePluginClasses.py
#@<< docstring >>
#@+node:bobjack.20080614200920.8:<< docstring >>
"""Base classes for plugins.

This is an experimental set of base classes for plugins.

They are primarily meant for use in rClick and toolbar 
but may be used in other plugins.

""" 
#@nonl
#@-node:bobjack.20080614200920.8:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

__version__ = '0.1'
#@<< version history >>
#@+node:bobjack.20080614200920.9:<< version history >>
#@@killcolor
#@+at
# 
# 0.1 bobjack:
#     - initial version
#@-at
#@nonl
#@-node:bobjack.20080614200920.9:<< version history >>
#@nl

#@<< imports >>
#@+node:bobjack.20080614200920.10:<< imports >>
import leo.core.leoGlobals as g

try:
    from PIL import Image
    from PIL import ImageTk
except ImportError:
    Image = ImageTk = None
#@nonl
#@-node:bobjack.20080614200920.10:<< imports >>
#@nl

iconCache = {}

defaultIconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

#@+others
#@+node:bobjack.20080614200920.11:init
def init ():
    """This is not a plugin so never allow it to load."""

    return False



#@-node:bobjack.20080614200920.11:init
#@+node:bobjack.20080614200920.13:getImage
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

#@-node:bobjack.20080614200920.13:getImage
#@+node:bobjack.20080511155621.3:class pluginCommandClass
class pluginCommandClass(object):

    """Base class for commands defined in plugins."""

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

    #@    @+others
    #@+node:bobjack.20080513085207.4:Properties
    #@+node:bobjack.20080513085207.5:phase
    def getPhase(self):

        return self.keywords.get('rc_phase')

    phase = property(getPhase)
    #@-node:bobjack.20080513085207.5:phase
    #@+node:bobjack.20080516105903.108:item_data
    def getItemData(self):

        item_data = self.keywords.get('rc_item_data', None)
        if item_data is None:
            self.keywords['rc_item_data'] = item_data = {}
        return item_data

    item_data = property(getItemData)
    #@nonl
    #@-node:bobjack.20080516105903.108:item_data
    #@-node:bobjack.20080513085207.4:Properties
    #@+node:bobjack.20080513085207.6:phaseError
    def phaseError(self):

        g.es_error('command not valid in phase: %s'%self.phase)
    #@-node:bobjack.20080513085207.6:phaseError
    #@+node:bobjack.20080513085207.7:minibufferPhaseError
    def minibufferPhaseError(self):

        if self.phase == 'minibuffer':
            self.phaseError()
            return True
    #@-node:bobjack.20080513085207.7:minibufferPhaseError
    #@-others
#@-node:bobjack.20080511155621.3:class pluginCommandClass
#@+node:bobjack.20080323045434.14:class basePluginController
class basePluginController(object):

    """A base class for per commander pluginControllers."""


    iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

    #@    @+others
    #@+node:bobjack.20080323045434.15:__init__
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
    #@+node:bobjack.20080423205354.3:onCreate
    def onCreate(self):

        c = self.c

        self.registerCommands()
        self.setDefaultContextMenus()
    #@-node:bobjack.20080423205354.3:onCreate
    #@+node:bobjack.20080424195922.7:onClose
    def onClose(self):
        """Clean up and prepare to die."""

        pass
    #@-node:bobjack.20080424195922.7:onClose
    #@+node:bobjack.20080511155621.6:getPublicCommands
    def getPublicCommands(self):

        """Create command instances for public commands provided by this plugin.

        Returns a dictionary {commandName: commandInstance, ...}

        """
        if self.commandsDict:
            return self.commandsDict

        commandsDict = {}

        for commandName in self.commandList:
            #@        << get className from commandName >>
            #@+node:bobjack.20080512054154.2:<< get className from commandName >>
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
            #@-node:bobjack.20080512054154.2:<< get className from commandName >>
            #@nl
            klass = getattr(self, className)

            cmd = klass(self)

            commandsDict[commandName] = cmd
            if alias:
                commandsDict[alias] = cmd

        self.commandsDict = commandsDict

        return commandsDict

    #@-node:bobjack.20080511155621.6:getPublicCommands
    #@+node:bobjack.20080511155621.9:registerCommands
    def registerCommands(self):

        """Create callbacks for minibuffer commands and register them."""

        c = self.c

        commandsDict = self.getPublicCommands()

        for commandName, cmd in commandsDict.iteritems():

            def rclickBaseCommandCallback(event, func=cmd):
                return func(event)

            c.k.registerCommand(commandName, shortcut=None, func=rclickBaseCommandCallback)   

    #@-node:bobjack.20080511155621.9:registerCommands
    #@+node:bobjack.20080423205354.5:getCommandList
    def getCommandList(self):

        return self.commandList
    #@-node:bobjack.20080423205354.5:getCommandList
    #@+node:bobjack.20080516105903.77:setDeafaultContextMenus
    def setDefaultContextMenus(self):

        pass


    #@-node:bobjack.20080516105903.77:setDeafaultContextMenus
    #@-node:bobjack.20080323045434.15:__init__
    #@+node:bobjack.20080614200920.14:getImage
    def getImage(self, path, iconBasePath=None):

        return getImage(path, iconBasePath)
    #@nonl
    #@-node:bobjack.20080614200920.14:getImage
    #@-others

#@-node:bobjack.20080323045434.14:class basePluginController
#@-others
#@-node:bobjack.20080619110105.2:@thin rClickBasePluginClasses.py
#@-leo

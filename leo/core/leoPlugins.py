#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3439:@thin leoPlugins.py
"""Install and run Leo plugins.

On startup:
- doPlugins() calls loadHandlers() to import all
  mod_x.py files in the Leo directory.
- Imported files should register hook handlers using the
  registerHandler and registerExclusiveHandler functions.
  Only one "exclusive" function is allowed per hook.

After startup:
- doPlugins() calls doHandlersForTag() to handle the hook.
- The first non-None return is sent back to Leo.
"""

#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leo.core.leoGlobals as g
import glob

handlers = {}
loadedModulesFilesDict = {}
    # Keys are module names, values are the names of .leo files
    # containing @enabled-plugins nodes that caused the plugin to be loaded
loadedModules = {}
    # Keys are module names, values are modules.
loadingModuleNameStack = [] # The stack of module names.  Top is the module being loaded.

def init():
    global handlers,loadedModules,loadedModulesNameStack
    handlers = {}
    loadedModules = {} # Keys are module names, values are modules.
    loadingModuleNameStack = [] # The stack of module names.  Top is the module being loaded.

#@+others
#@+node:ktenney.20060628092017.1:baseLeoPlugin
class baseLeoPlugin(object):
    #@    <<docstring>>
    #@+node:ktenney.20060628092017.2:<<docstring>>
    """A Convenience class to simplify plugin authoring

    .. contents::

    Usage
    =====


    Initialization
    --------------

    - import the base class::

        from leoPlugins import leo.core.leoBasePlugin as leoBasePlugin

    - create a class which inherits from leoBasePlugin::

        class myPlugin(leoBasePlugin):

    - in the __init__ method of the class, call the parent constructor::

        def __init__(self, tag, keywords):
            leoBasePlugin.__init__(self, tag, keywords)

    - put the actual plugin code into a method; for this example, the work
      is done by myPlugin.handler()

    - put the class in a file which lives in the <LeoDir>/plugins directory
        for this example it is named myPlugin.py

    - add code to register the plugin::

        leoPlugins.registerHandler("after-create-leo-frame", Hello)

    Configuration
    -------------

    baseLeoPlugins has 3 *methods* for setting commands

    - setCommand::

            def setCommand(self, commandName, handler, 
                    shortcut = None, pane = 'all', verbose = True):

    - setMenuItem::

            def setMenuItem(self, menu, commandName = None, handler = None):

    - setButton::

            def setButton(self, buttonText = None, commandName = None, color = None):

    *variables*

    :commandName:  the string typed into minibuffer to execute the ``handler``

    :handler:  the method in the class which actually does the work

    :shortcut:  the key combination to activate the command

    :menu:  a string designating on of the menus ('File', Edit', 'Outline', ...)

    :buttonText:  the text to put on the button if one is being created.

    Example
    =======

    Contents of file ``<LeoDir>/plugins/hello.py``::

        class Hello(baseLeoPlugin):
            def __init__(self, tag, keywords):

                # call parent __init__
                baseLeoPlugin.__init__(self, tag, keywords)

                # if the plugin object defines only one command, 
                # just give it a name. You can then create a button and menu entry
                self.setCommand('Hello', self.hello)
                self.setButton()
                self.setMenuItem('Cmds')

                # create a command with a shortcut
                self.setCommand('Hola', self.hola, 'Alt-Ctrl-H')

                # create a button using different text than commandName
                self.setButton('Hello in Spanish')

                # create a menu item with default text
                self.setMenuItem('Cmds')

                # define a command using setMenuItem 
                self.setMenuItem('Cmds', 'Ciao baby', self.ciao)

            def hello(self, event):
                g.pr("hello from node %s" % self.c.currentPosition().h)

            def hola(self, event):
                g.pr("hola from node %s" % self.c.currentPosition().h)

            def ciao(self, event):
                g.pr("ciao baby (%s)" % self.c.currentPosition().h)


        leoPlugins.registerHandler("after-create-leo-frame", Hello)

    """
    #@-node:ktenney.20060628092017.2:<<docstring>>
    #@nl
    #@    <<baseLeoPlugin declarations>>
    #@+node:ktenney.20060628092017.3:<<baseLeoPlugin declarations>>
    import leo.core.leoGlobals as g
    #@-node:ktenney.20060628092017.3:<<baseLeoPlugin declarations>>
    #@nl
    #@    @+others
    #@+node:ktenney.20060628092017.4:__init__
    def __init__(self, tag, keywords):

        """Set self.c to be the ``commander`` of the active node
        """

        self.c = keywords['c']
        self.commandNames = []
    #@-node:ktenney.20060628092017.4:__init__
    #@+node:ktenney.20060628092017.5:setCommand
    def setCommand(self, commandName, handler, 
                    shortcut = None, pane = 'all', verbose = True):

        """Associate a command name with handler code, 
        optionally defining a keystroke shortcut
        """

        self.commandNames.append(commandName)

        self.commandName = commandName
        self.shortcut = shortcut
        self.handler = handler
        self.c.k.registerCommand (commandName, shortcut, handler, 
                                pane, verbose)
    #@-node:ktenney.20060628092017.5:setCommand
    #@+node:ktenney.20060628092017.6:setMenuItem
    def setMenuItem(self, menu, commandName = None, handler = None):

        """Create a menu item in 'menu' using text 'commandName' calling handler 'handler'
        if commandName and handler are none, use the most recently defined values
        """

        # setMenuItem can create a command, or use a previously defined one.
        if commandName is None:
            commandName = self.commandName
        # make sure commandName is in the list of commandNames                        
        else:
            if commandName not in self.commandNames:
                self.commandNames.append(commandName) 

        if handler is None:
            handler = self.handler

        table = ((commandName, None, handler),)
        self.c.frame.menu.createMenuItemsFromTable(menu, table)
    #@-node:ktenney.20060628092017.6:setMenuItem
    #@+node:ktenney.20060628092017.7:setButton
    def setButton(self, buttonText = None, commandName = None, color = None):

        """Associate an existing command with a 'button'
        """

        if buttonText is None:
            buttonText = self.commandName

        if commandName is None:
            commandName = self.commandName       
        else:
            if commandName not in self.commandNames:
                raise NameError("setButton error, %s is not a commandName" % commandName)

        if color is None:
            color = 'grey'
        script = "c.k.simulateCommand('%s')" % self.commandName
        g.app.gui.makeScriptButton(
            self.c,
            args=None,
            script=script, 
            buttonText = buttonText, bg = color)
    #@-node:ktenney.20060628092017.7:setButton
    #@-others
#@-node:ktenney.20060628092017.1:baseLeoPlugin
#@+node:ekr.20050102094729:callTagHandler
def callTagHandler (bunch,tag,keywords):

    handler = bunch.fn ; moduleName = bunch.moduleName

    # if tag != 'idle': g.pr('callTagHandler',tag,keywords.get('c'))

    # Make sure the new commander exists.
    if True: # tag == 'idle':
        for key in ('c','new_c'):
            c = keywords.get(key)
            if c:
                # Make sure c exists and has a frame.
                if not c.exists or not hasattr(c,'frame'):
                    g.pr('skipping tag %s: c does not exists or does not have a frame.' % tag)
                    return None

    # Calls to registerHandler from inside the handler belong to moduleName.
    global loadingModuleNameStack
    loadingModuleNameStack.append(moduleName)
    result = handler(tag,keywords)
    loadingModuleNameStack.pop()
    return result
#@-node:ekr.20050102094729:callTagHandler
#@+node:ekr.20031218072017.3442:doHandlersForTag
def doHandlersForTag (tag,keywords):

    """Execute all handlers for a given tag, in alphabetical order.

    All exceptions are caught by the caller, doHook."""

    global handlers

    if g.app.killed:
        return None

    if tag in handlers:
        bunches = handlers.get(tag)
        # Execute hooks in some random order.
        # Return if one of them returns a non-None result.
        for bunch in bunches:
            val = callTagHandler(bunch,tag,keywords)
            if val is not None:
                return val

    if 'all' in handlers:
        bunches = handlers.get('all')
        for bunch in bunches:
            callTagHandler(bunch,tag,keywords)

    return None
#@-node:ekr.20031218072017.3442:doHandlersForTag
#@+node:ekr.20041001161108:doPlugins
def doPlugins(tag,keywords):

    if g.app.killed:
        return

    if g.isPython3:
        g.trace('ignoring all plugins')
        return

    # g.trace(tag)
    if tag in ('start1','open0'):
        loadHandlers(tag)

    return doHandlersForTag(tag,keywords)
#@-node:ekr.20041001161108:doPlugins
#@+node:ekr.20041111124831:getHandlersForTag
def getHandlersForTag(tags):

    import types

    if type(tags) in (types.TupleType,types.ListType):
        result = []
        for tag in tags:
            aList = getHandlersForOneTag(tag) 
            result.extend(aList)
        return result
    else:
        return getHandlersForOneTag(tags)

def getHandlersForOneTag (tag):

    global handlers

    aList = handlers.get(tag,[])
    return aList
    # return [bunch.fn for bunch in aList]
#@-node:ekr.20041111124831:getHandlersForTag
#@+node:ekr.20041114113029:getPluginModule
def getPluginModule (moduleName):

    global loadedModules

    return loadedModules.get(moduleName)
#@-node:ekr.20041114113029:getPluginModule
#@+node:ekr.20041001160216:isLoaded
def isLoaded (name):

    if name.endswith('.py'): name = name[:-3]

    return name in g.app.loadedPlugins
#@-node:ekr.20041001160216:isLoaded
#@+node:ekr.20031218072017.3440:loadHandlers & helper
def loadHandlers(tag):

    """Load all enabled plugins from the plugins directory"""

    def pr (*args,**keys):
        if not g.app.unitTesting:
            g.es_print(*args,**keys)

    plugins_path = g.os_path_finalize_join(g.app.loadDir,"..","plugins")
    files = glob.glob(g.os_path_join(plugins_path,"*.py"))
    files = [g.os_path_finalize(theFile) for theFile in files]

    s = g.app.config.getEnabledPlugins()
    if not s: return

    if not g.app.silentMode:
        pr('@enabled-plugins found in %s' % (
            g.app.config.enabledPluginsFileName),color='blue')

    enabled_files = getEnabledFiles(s,plugins_path)

    # Load plugins in the order they appear in the enabled_files list.
    if files and enabled_files:
        for theFile in enabled_files:
            if theFile in files:
                loadOnePlugin(theFile)

    # Note: g.plugin_signon adds module names to g.app.loadedPlugins
    if 0:
        if g.app.loadedPlugins:
            pr("%d plugins loaded" % (len(g.app.loadedPlugins)), color="blue")
#@+node:ekr.20070224082131:getEnabledFiles
def getEnabledFiles (s,plugins_path):

    '''Return a list of plugins mentioned in non-comment lines of s.'''

    enabled_files = []
    for s in g.splitLines(s):
        s = s.strip()
        if s and not s.startswith('#'):
            path = g.os_path_finalize_join(plugins_path,s)
            enabled_files.append(path)

    return enabled_files
#@-node:ekr.20070224082131:getEnabledFiles
#@-node:ekr.20031218072017.3440:loadHandlers & helper
#@+node:ekr.20041113113140:loadOnePlugin
def loadOnePlugin (moduleOrFileName, verbose=False):

    global loadedModules,loadingModuleNameStack

    verbose = False or verbose or g.app.config.getBool(c=None,setting='trace_plugins')
    warn_on_failure = g.app.config.getBool(c=None,setting='warn_when_plugins_fail_to_load')

    if moduleOrFileName.endswith('.py'):
        moduleName = moduleOrFileName [:-3]
    else:
        moduleName = moduleOrFileName
    moduleName = g.shortFileName(moduleName)

    if isLoaded(moduleName):
        module = loadedModules.get(moduleName)
        if verbose:
            g.es_print('plugin',moduleName,'already loaded',color="blue")
        return module

    plugins_path = g.os_path_join(g.app.loadDir,"..","plugins")
    moduleName = g.toUnicode(moduleName,g.app.tkEncoding)

    # This import will typically result in calls to registerHandler.
    # if the plugin does _not_ use the init top-level function.
    loadingModuleNameStack.append(moduleName)
    result = g.importFromPath(moduleName,plugins_path,pluginName=moduleName,verbose=True)
    loadingModuleNameStack.pop()

    if result:
        loadingModuleNameStack.append(moduleName)
        if hasattr(result,'init'):
            try:
                # Indicate success only if init_result is True.
                init_result = result.init()
                # g.trace('result',result,'init_result',init_result)
                if init_result:
                    loadedModules[moduleName] = result
                    loadedModulesFilesDict[moduleName] = g.app.config.enabledPluginsFileName
                else:
                    if verbose and not g.app.initing:
                        g.es_print('loadOnePlugin: failed to load module',moduleName,color="red")
                    result = None
            except Exception:
                g.es('exception loading plugin',color='red')
                g.es_exception()
                result = None
        else:
            # No top-level init function.
            # Guess that the module was loaded correctly,
            # but do *not* load the plugin if we are unit testing.
            g.trace('no init()',moduleName)
            if g.app.unitTesting:
                result = None
                loadedModules[moduleName] = None
            else:
                loadedModules[moduleName] = result
        loadingModuleNameStack.pop()

    if g.unitTesting or g.app.batchMode or g.app.inBridge:
        pass
    elif result is None:
        if warn_on_failure or (verbose and not g.app.initing): # or not g.app.unitTesting:
            g.es_print('can not load enabled plugin:',moduleName,color="red")
    elif verbose:
        g.es_print('loaded plugin:',moduleName,color="blue")

    return result
#@-node:ekr.20041113113140:loadOnePlugin
#@+node:ekr.20050110191444:printHandlers
def printHandlers (c,moduleName=None):

    tabName = 'Plugins'
    c.frame.log.selectTab(tabName)

    if moduleName:
        s = 'handlers for %s...\n' % (moduleName)
    else:
        s = 'all plugin handlers...\n'
    g.es(s+'\n',tabName=tabName)

    data = []
    modules = {}
    for tag in handlers:
        bunches = handlers.get(tag)
        for bunch in bunches:
            name = bunch.moduleName
            tags = modules.get(name,[])
            tags.append(tag)
            modules[name] = tags

    n = 4
    for key in sorted(modules):
        tags = modules.get(key)
        if moduleName in (None,key):
            for tag in tags:
                n = max(n,len(tag))
                data.append((tag,key),)

    lines = ['%*s %s\n' % (-n,s1,s2) for (s1,s2) in data]
    g.es('',''.join(lines),tabName=tabName)

#@-node:ekr.20050110191444:printHandlers
#@+node:ekr.20070429090122:printPlugins
def printPlugins (c):

    tabName = 'Plugins'
    c.frame.log.selectTab(tabName)

    data = []
    data.append('enabled plugins...\n')
    for z in sorted(loadedModules):
        data.append(z)

    lines = ['%s\n' % (s) for s in data]
    g.es('',''.join(lines),tabName=tabName)
#@-node:ekr.20070429090122:printPlugins
#@+node:ekr.20081123080346.2:printPluginsInfo
def printPluginsInfo (c):

    '''Print the file name responsible for loading a plugin.

    This is the first .leo file containing an @enabled-plugins node
    that enables the plugin.'''

    d = loadedModulesFilesDict
    tabName = 'Plugins'
    c.frame.log.selectTab(tabName)

    data = []
    for z in g.app.loadedPlugins:
        print (z, d.get(z))

    data = [] ; n = 4
    for moduleName in d:
        fileName = d.get(moduleName)
        n = max(n,len(moduleName))
        data.append((moduleName,fileName),)

    lines = ['%*s %s\n' % (-n,s1,s2) for (s1,s2) in data]
    g.es('',''.join(lines),tabName=tabName)
#@-node:ekr.20081123080346.2:printPluginsInfo
#@+node:ekr.20031218072017.3444:registerExclusiveHandler
def registerExclusiveHandler(tags, fn):

    """ Register one or more exclusive handlers"""

    import types

    if type(tags) in (types.TupleType,types.ListType):
        for tag in tags:
            registerOneExclusiveHandler(tag,fn)
    else:
        registerOneExclusiveHandler(tags,fn)

def registerOneExclusiveHandler(tag, fn):

    """Register one exclusive handler"""

    global handlers, loadingModuleNameStack
    try:
        moduleName = loadingModuleNameStack[-1]
    except IndexError:
        moduleName = '<no module>'

    if 0:
        if g.app.unitTesting: g.pr('')
        g.pr('%6s %15s %25s %s' % (g.app.unitTesting,moduleName,tag,fn.__name__))

    if g.app.unitTesting: return

    if tag in handlers:
        g.es("*** Two exclusive handlers for","'%s'" % (tag))
    else:
        bunch = g.Bunch(fn=fn,moduleName=moduleName,tag='handler')
        handlers = [bunch]
#@-node:ekr.20031218072017.3444:registerExclusiveHandler
#@+node:ekr.20031218072017.3443:registerHandler
def registerHandler(tags,fn):

    """ Register one or more handlers"""

    import types

    if type(tags) in (types.TupleType,types.ListType):
        for tag in tags:
            registerOneHandler(tag,fn)
    else:
        registerOneHandler(tags,fn)

def registerOneHandler(tag,fn):

    """Register one handler"""

    global handlers, loadingModuleNameStack
    try:
        moduleName = loadingModuleNameStack[-1]
    except IndexError:
        moduleName = '<no module>'

    if 0:
        if g.app.unitTesting: g.pr('')
        g.pr('%6s %15s %25s %s' % (g.app.unitTesting,moduleName,tag,fn.__name__))

    items = handlers.get(tag,[])
    if fn not in items:

        bunch = g.Bunch(fn=fn,moduleName=moduleName,tag='handler')
        items.append(bunch)

    # g.trace(tag) ; g.printList(items)
    handlers[tag] = items
#@-node:ekr.20031218072017.3443:registerHandler
#@+node:ekr.20050110182317:unloadOnePlugin
def unloadOnePlugin (moduleOrFileName,verbose=False):

    if moduleOrFileName [-3:] == ".py":
        moduleName = moduleOrFileName [:-3]
    else:
        moduleName = moduleOrFileName
    moduleName = g.shortFileName(moduleName)

    if moduleName in g.app.loadedPlugins:
        if verbose:
            g.pr('unloading',moduleName)
        g.app.loadedPlugins.remove(moduleName)

    for tag in handlers:
        bunches = handlers.get(tag)
        bunches = [bunch for bunch in bunches if bunch.moduleName != moduleName]
        handlers[tag] = bunches
#@-node:ekr.20050110182317:unloadOnePlugin
#@+node:ekr.20041111123313:unregisterHandler
def unregisterHandler(tags,fn):

    import types

    if type(tags) in (types.TupleType,types.ListType):
        for tag in tags:
            unregisterOneHandler(tag,fn)
    else:
        unregisterOneHandler(tags,fn)

def unregisterOneHandler (tag,fn):

    global handlers

    if 1: # New code
        bunches = handlers.get(tag)
        bunches = [bunch for bunch in bunches if bunch.fn != fn]
        handlers[tag] = bunches
    else:
        fn_list = handlers.get(tag)
        if fn_list:
            while fn in fn_list:
                fn_list.remove(fn)
            handlers[tag] = fn_list
            # g.trace(handlers.get(tag))
#@-node:ekr.20041111123313:unregisterHandler
#@-others
#@-node:ekr.20031218072017.3439:@thin leoPlugins.py
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3439: * @thin leoPlugins.py
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
#@@pagewidth 70

import leo.core.leoGlobals as g
import glob
import bisect
import sys

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
    g.act_on_node = CommandChainDispatcher()
    g.visit_tree_item = CommandChainDispatcher()
    g.tree_popup_handlers = []

#@+others
#@+node:ktenney.20060628092017.1: ** baseLeoPlugin
class baseLeoPlugin(object):
    #@+<<docstring>>
    #@+node:ktenney.20060628092017.2: *3* <<docstring>>
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
                g.pr("hello from node %s" % self.c.p.h)

            def hola(self, event):
                g.pr("hola from node %s" % self.c.p.h)

            def ciao(self, event):
                g.pr("ciao baby (%s)" % self.c.p.h)


        leoPlugins.registerHandler("after-create-leo-frame", Hello)

    """
    #@-<<docstring>>
    #@+<<baseLeoPlugin declarations>>
    #@+node:ktenney.20060628092017.3: *3* <<baseLeoPlugin declarations>>
    import leo.core.leoGlobals as g
    #@-<<baseLeoPlugin declarations>>
    #@+others
    #@+node:ktenney.20060628092017.4: *3* __init__
    def __init__(self, tag, keywords):

        """Set self.c to be the ``commander`` of the active node
        """

        self.c = keywords['c']
        self.commandNames = []
    #@+node:ktenney.20060628092017.5: *3* setCommand
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
    #@+node:ktenney.20060628092017.6: *3* setMenuItem
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
    #@+node:ktenney.20060628092017.7: *3* setButton
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
    #@-others
#@+node:ekr.20050102094729: ** callTagHandler
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
    try:
        result = handler(tag,keywords)
    except:
        g.es("hook failed: %s, %s, %s" % (tag, handler, moduleName))
        g.es_exception()
        result = None
    loadingModuleNameStack.pop()
    return result
#@+node:ekr.20031218072017.3442: ** doHandlersForTag
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
#@+node:ekr.20041001161108: ** doPlugins
ignoringMessageGiven = False

def doPlugins(tag,keywords):

    global ignoringMessageGiven

    if g.app.killed:
        return

    if tag in ('start1','open0'):
        loadHandlers(tag)

    return doHandlersForTag(tag,keywords)
#@+node:ekr.20041111124831: ** getHandlersForTag
def getHandlersForTag(tags):

    import types

    if type(tags) in (type((),),type([])):
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
#@+node:ekr.20041114113029: ** getPluginModule
def getPluginModule (moduleName):

    global loadedModules

    return loadedModules.get(moduleName)
#@+node:ekr.20041001160216: ** isLoaded
def isLoaded (name):

    if name.endswith('.py'): name = name[:-3]

    return name in g.app.loadedPlugins
#@+node:ekr.20031218072017.3440: ** loadHandlers & helper
def loadHandlers(tag):

    """Load all enabled plugins from the plugins directory"""

    warn_on_failure = g.app.config.getBool(c=None,setting='warn_when_plugins_fail_to_load')

    def pr (*args,**keys):
        if not g.app.unitTesting:
            g.es_print(*args,**keys)

    #plugins_path = g.os_path_finalize_join(g.app.loadDir,"..","plugins")
    #files = glob.glob(g.os_path_join(plugins_path,"*.py"))
    #files = [g.os_path_finalize(theFile) for theFile in files]

    s = g.app.config.getEnabledPlugins()
    if not s: return

    if tag == 'open0' and not g.app.silentMode and not g.app.batchMode:
        s2 = '@enabled-plugins found in %s' % (
            g.app.config.enabledPluginsFileName)
        g.es_print(s2,color='blue')

    #enabled_files = getEnabledFiles(s)

    for plugin in s.splitlines():
        if plugin.strip() and not plugin.lstrip().startswith('#'):
            loadOnePlugin(plugin.strip(), tag = tag)
    # Load plugins in the order they appear in the enabled_files list.
    """
    if files and enabled_files:
        for theFile in enabled_files:
            if theFile in files:
                loadOnePlugin(theFile,tag=tag)
    """
    # Warn about any non-existent enabled file.
    """
    if warn_on_failure and tag == 'open0':
        for z in enabled_files:
            if z not in files:
                g.es_print('plugin does not exist:',
                    g.shortFileName(z),color="red")
    """
    # Note: g.plugin_signon adds module names to g.app.loadedPlugins
    if 0:
        if g.app.loadedPlugins:
            pr("%d plugins loaded" % (len(g.app.loadedPlugins)), color="blue")
#@+node:ekr.20070224082131: *3* getEnabledFiles
def getEnabledFiles (s,plugins_path = None):

    '''Return a list of plugins mentioned in non-comment lines of s.'''

    enabled_files = []
    for s in g.splitLines(s):
        s = s.strip()
        if s and not s.lstrip().startswith('#'):
            enabled_files.append(s)
            #path = g.os_path_finalize_join(plugins_path,s)

            #enabled_files.append(path)

    return enabled_files
#@+node:ekr.20041113113140: ** loadOnePlugin
def loadOnePlugin (moduleOrFileName,tag='open0',verbose=False):

    trace = False # and not g.unitTesting

    global loadedModules,loadingModuleNameStack

    # Prevent Leo from crashing if .leoID.txt does not exist.
    if g.app.config is None:
        print ('No g.app.config, making stub...')
        class StubConfig(g.nullObject):
            pass
        g.app.config = StubConfig()

    # Fixed reversion: do this after possibly creating stub config class.
    verbose = False or verbose or g.app.config.getBool(c=None,setting='trace_plugins')
    warn_on_failure = g.app.config.getBool(c=None,setting='warn_when_plugins_fail_to_load')

    if moduleOrFileName.startswith('@'):
        if trace: g.trace('ignoring Leo directive')
        return False # Allow Leo directives in @enabled-plugins nodes.

    if moduleOrFileName.endswith('.py'):
        moduleName = 'leo.plugins.' + moduleOrFileName [:-3]
    elif moduleOrFileName.startswith('leo.plugins.'):
        moduleName = moduleOrFileName
    else:
        moduleName = 'leo.plugins.' + moduleOrFileName

    if isLoaded(moduleName):
        module = loadedModules.get(moduleName)
        if trace or verbose:
            g.trace('plugin',moduleName,'already loaded',color="blue")
        return module

    assert g.app.loadDir

    moduleName = g.toUnicode(moduleName)

    # This import will typically result in calls to registerHandler.
    # if the plugin does _not_ use the init top-level function.
    loadingModuleNameStack.append(moduleName)

    try:
        toplevel = __import__(moduleName)
        # need to look up through sys.modules, __import__ returns toplevel package
        result = sys.modules[moduleName]

    except g.UiTypeException:
        if not g.unitTesting and not g.app.batchMode:
            g.es_print('Plugin %s does not support %s gui' % (
                moduleName,g.app.gui.guiName()))
        result = None

    except ImportError:
        if trace or tag == 'open0': # Just give the warning once.
            g.es_print('plugin does not exist:',moduleName,color='red')
        result = None

    except Exception as e:
        g.es_print('exception importing plugin ' + moduleName,color='red')
        g.es_exception()
        result = None

    loadingModuleNameStack.pop()

    if result:
        loadingModuleNameStack.append(moduleName)

        if tag == 'unit-test-load':
            pass # Keep the result, but do no more.
        elif hasattr(result,'init'):
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
                g.es_print('exception loading plugin',color='red')
                g.es_exception()
                result = None
        else:
            # No top-level init function.
            # Guess that the module was loaded correctly,
            # but do *not* load the plugin if we are unit testing.

            if g.app.unitTesting:
                result = None
                loadedModules[moduleName] = None
            else:
                g.trace('no init()',moduleName)
                loadedModules[moduleName] = result
        loadingModuleNameStack.pop()

    if g.app.batchMode or g.app.inBridge: # or g.unitTesting
        pass
    elif result:
        if trace or verbose:
            g.trace('loaded plugin:',moduleName,color="blue")
    else:
        if trace or warn_on_failure or (verbose and not g.app.initing):
            if trace or tag == 'open0':
                g.trace('can not load enabled plugin:',moduleName,color="red")

    return result
#@+node:ekr.20050110191444: ** printHandlers
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

#@+node:ekr.20070429090122: ** printPlugins
def printPlugins (c):

    tabName = 'Plugins'
    c.frame.log.selectTab(tabName)

    data = []
    data.append('enabled plugins...\n')
    for z in sorted(loadedModules):
        data.append(z)

    lines = ['%s\n' % (s) for s in data]
    g.es('',''.join(lines),tabName=tabName)
#@+node:ekr.20081123080346.2: ** printPluginsInfo
def printPluginsInfo (c):

    '''Print the file name responsible for loading a plugin.

    This is the first .leo file containing an @enabled-plugins node
    that enables the plugin.'''

    d = loadedModulesFilesDict
    tabName = 'Plugins'
    c.frame.log.selectTab(tabName)

    data = []
    # for z in g.app.loadedPlugins:
        # print (z, d.get(z))

    data = [] ; n = 4
    for moduleName in d:
        fileName = d.get(moduleName)
        n = max(n,len(moduleName))
        data.append((moduleName,fileName),)

    lines = ['%*s %s\n' % (-n,s1,s2) for (s1,s2) in data]
    g.es('',''.join(lines),tabName=tabName)
#@+node:ekr.20031218072017.3444: ** registerExclusiveHandler
def registerExclusiveHandler(tags, fn):

    """ Register one or more exclusive handlers"""

    import types

    if type(tags) in (type((),),type([])):
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
#@+node:ekr.20031218072017.3443: ** registerHandler
def registerHandler(tags,fn):

    """ Register one or more handlers"""

    import types

    if type(tags) in (type((),),type([])):
        for tag in tags:
            registerOneHandler(tag,fn)
    else:
        registerOneHandler(tags,fn)

def registerOneHandler(tag,fn):

    """Register one handler"""

    global generateEventsFlag,handlers,loadingModuleNameStack
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
#@+node:ekr.20050110182317: ** unloadOnePlugin
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
#@+node:ekr.20041111123313: ** unregisterHandler
def unregisterHandler(tags,fn):

    import types

    if type(tags) in (type((),),type([])):
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
#@+node:ville.20090222141717.2: ** TryNext (exception)
class TryNext(Exception):
    """Try next hook exception.

    Raise this in your hook function to indicate that the next hook handler
    should be used to handle the operation.  If you pass arguments to the
    constructor those arguments will be used by the next hook instead of the
    original ones.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
#@+node:ville.20090222141717.1: ** class CommandChainDispatcher
class CommandChainDispatcher:
    """ Dispatch calls to a chain of commands until some func can handle it

    Usage: instantiate, execute "add" to add commands (with optional
    priority), execute normally via f() calling mechanism.

    """
    def __init__(self,commands=None):
        if commands is None:
            self.chain = []
        else:
            self.chain = commands


    def __call__(self,*args, **kw):
        """ Command chain is called just like normal func. 

        This will call all funcs in chain with the same args as were given to this
        function, and return the result of first func that didn't raise
        TryNext """

        for prio,cmd in self.chain:
            #print "prio",prio,"cmd",cmd #dbg
            try:
                ret = cmd(*args, **kw)
                return ret
            except TryNext as exc:
                if exc.args or exc.kwargs:
                    args = exc.args
                    kw = exc.kwargs

        # if no function will accept it, raise TryNext up to the caller
        raise TryNext

    def __str__(self):
        return str(self.chain)

    def add(self, func, priority=0):
        """ Add a func to the cmd chain with given priority """
        bisect.insort(self.chain,(priority,func))

    def __iter__(self):
        """ Return all objects in chain.

        Handy if the objects are not callable.
        """
        return iter(self.chain)
#@-others
#@-leo

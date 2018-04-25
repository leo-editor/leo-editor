#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3439: * @file leoPlugins.py
'''Classes relating to Leo's plugin architecture.'''
import leo.core.leoGlobals as g
import sys
# Define modules that may be enabled by default
# but that mignt not load because imports may fail.
optional_modules = [
    'leo.plugins.livecode',
    'leo.plugins.cursesGui2',
]
#@+others
#@+node:ekr.20100908125007.6041: ** Top-level functions (leoPlugins.py)
def init():
    '''Init g.app.pluginsController.'''
    g.app.pluginsController = LeoPluginsController()

def registerHandler(tags, fn):
    '''A wrapper so plugins can still call leoPlugins.registerHandler.'''
    return g.app.pluginsController.registerHandler(tags, fn)
#@+node:ville.20090222141717.2: ** TryNext (exception)
class TryNext(Exception):
    """Try next hook exception.

    Raise this in your hook function to indicate that the next hook handler
    should be used to handle the operation.  If you pass arguments to the
    constructor those arguments will be used by the next hook instead of the
    original ones.
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.args = args
        self.kwargs = kwargs
#@+node:ekr.20100908125007.6033: ** class CommandChainDispatcher
class CommandChainDispatcher(object):
    """ Dispatch calls to a chain of commands until some func can handle it

    Usage: instantiate, execute "add" to add commands (with optional
    priority), execute normally via f() calling mechanism.

    """

    def __init__(self, commands=None):
        if commands is None:
            self.chain = []
        else:
            self.chain = commands

    def __call__(self, *args, **kw):
        """ Command chain is called just like normal func.

        This will call all funcs in chain with the same args as were given to this
        function, and return the result of first func that didn't raise
        TryNext """
        for prio, cmd in self.chain:
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
        # Fails in Python 3: func is not orderable.
        # bisect.insort(self.chain,(priority,func))
        self.chain.append((priority, func),)
        self.chain.sort(key=lambda z: z[0])

    def __iter__(self):
        """ Return all objects in chain.

        Handy if the objects are not callable.
        """
        return iter(self.chain)
#@+node:ekr.20100908125007.6009: ** class BaseLeoPlugin
class BaseLeoPlugin(object):
    #@+<<docstring>>
    #@+node:ekr.20100908125007.6010: *3* <<docstring>>
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

    BaseLeoPlugins has 3 *methods* for setting commands

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

        class Hello(BaseLeoPlugin):
            def __init__(self, tag, keywords):

                # call parent __init__
                BaseLeoPlugin.__init__(self, tag, keywords)

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
    #@+others
    #@+node:ekr.20100908125007.6012: *3* __init__ (BaseLeoPlugin)
    def __init__(self, tag, keywords):
        """Set self.c to be the ``commander`` of the active node
        """
        self.c = keywords['c']
        self.commandNames = []
    #@+node:ekr.20100908125007.6013: *3* setCommand
    def setCommand(self, commandName, handler,
                    shortcut='', pane='all', verbose=True):
        """Associate a command name with handler code,
        optionally defining a keystroke shortcut
        """
        self.commandNames.append(commandName)
        self.commandName = commandName
        self.shortcut = shortcut
        self.handler = handler
        self.c.k.registerCommand(commandName, handler,
            pane=pane, shortcut=shortcut, verbose=verbose)
    #@+node:ekr.20100908125007.6014: *3* setMenuItem
    def setMenuItem(self, menu, commandName=None, handler=None):
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
    #@+node:ekr.20100908125007.6015: *3* setButton
    def setButton(self, buttonText=None, commandName=None, color=None):
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
            buttonText=buttonText, bg=color)
    #@-others
#@+node:ekr.20100908125007.6007: ** class LeoPluginsController
class LeoPluginsController(object):
    '''The global plugins controller, g.app.pluginsController'''
    #@+others
    #@+node:ekr.20100909065501.5954: *3* plugins.Birth
    #@+node:ekr.20100908125007.6034: *4* plugins.ctor & reloadSettings
    def __init__(self):
        # g.trace('LeoPluginsController',g.callers())
        self.handlers = {}
        self.loadedModulesFilesDict = {}
            # Keys are regularized module names, values are the names of .leo files
            # containing @enabled-plugins nodes that caused the plugin to be loaded
        self.loadedModules = {}
            # Keys are regularized module names, values are modules.
        self.loadingModuleNameStack = []
            # The stack of module names.
            # The top is the module being loaded.
        self.signonModule = None # A hack for plugin_signon.
        # Settings.  Set these here in case finishCreate is never called.
        self.warn_on_failure = True
        assert(g)
        g.act_on_node = CommandChainDispatcher()
        g.visit_tree_item = CommandChainDispatcher()
        g.tree_popup_handlers = []
    #@+node:ekr.20100909065501.5974: *4* plugins.finishCreate & reloadSettings
    def finishCreate(self):
        self.reloadSettings()

    def reloadSettings(self):
        self.warn_on_failure = g.app.config.getBool(
            setting='warn_when_plugins_fail_to_load',
            default=True)
    #@+node:ekr.20100909065501.5952: *3* plugins.Event handlers
    #@+node:ekr.20161029060545.1: *4* plugins.on_idle
    def on_idle(self):
        '''Call all idle-time hooks.'''
        trace = False and not g.unitTesting
        if g.app.idle_time_hooks_enabled:
            for frame in g.app.windowList:
                c = frame.c
                # Do NOT compute c.currentPosition.
                # This would be a MAJOR leak of positions.
                if trace:
                    g.trace('(leoPlugins.py) calling g.doHook(c=%s)' % (
                        c.shortFileName()))
                g.doHook("idle", c=c)
    #@+node:ekr.20100908125007.6017: *4* plugins.doHandlersForTag & helper
    def doHandlersForTag(self, tag, keywords):
        """
        Execute all handlers for a given tag, in alphabetical order.
        The caller, doHook, catches all exceptions.
        """
        trace = False and not g.unitTesting
        traceIdle = True
        if g.app.killed:
            return None
        if trace and (traceIdle or tag != 'idle'):
            event_p = keywords.get('new_p') or keywords.get('p')
            g.trace(tag, event_p.h if event_p else '')
        # Execute hooks in some random order.
        # Return if one of them returns a non-None result.
        for bunch in self.handlers.get(tag, []):
            val = self.callTagHandler(bunch, tag, keywords)
            if val is not None:
                return val
        if 'all' in self.handlers:
            bunches = self.handlers.get('all')
            for bunch in bunches:
                self.callTagHandler(bunch, tag, keywords)
        return None
    #@+node:ekr.20100908125007.6016: *5* plugins.callTagHandler
    def callTagHandler(self, bunch, tag, keywords):
        '''Call the event handler.'''
        trace = False and not g.unitTesting
        traceIdle = True
        handler, moduleName = bunch.fn, bunch.moduleName
        if trace and (traceIdle or tag != 'idle'):
            c = keywords.get('c')
            name = moduleName; tag2 = 'leo.plugins.'
            if name.startswith(tag2): name = name[len(tag2):]
            g.trace('c: %s %23s : %s . %s' % (
                c and c.shortFileName() or '<no c>',
                tag, handler.__name__, name))
        # Make sure the new commander exists.
        for key in ('c', 'new_c'):
            c = keywords.get(key)
            if c:
                # Make sure c exists and has a frame.
                if not c.exists or not hasattr(c, 'frame'):
                    # g.pr('skipping tag %s: c does not exist or does not have a frame.' % tag)
                    return None
        # Calls to registerHandler from inside the handler belong to moduleName.
        self.loadingModuleNameStack.append(moduleName)
        try:
            result = handler(tag, keywords)
        except Exception:
            g.es("hook failed: %s, %s, %s" % (tag, handler, moduleName))
            g.es_exception()
            result = None
        self.loadingModuleNameStack.pop()
        return result
    #@+node:ekr.20100908125007.6018: *4* plugins.doPlugins (g.app.hookFunction)
    def doPlugins(self, tag, keywords):
        '''The default g.app.hookFunction.'''
        trace = False and not g.unitTesting
        trace_idle = True
        if g.app.killed:
            return
        if trace:
            if (
                (trace_idle and tag == 'idle') or
                (not trace_idle and tag != 'idle')
            ):
                g.trace(tag)
        if tag in ('start1', 'open0'):
            self.loadHandlers(tag, keywords)
        return self.doHandlersForTag(tag, keywords)
    #@+node:ekr.20100909065501.5950: *3* plugins.Information
    #@+node:ekr.20100908125007.6019: *4* plugins.getHandlersForTag
    def getHandlersForTag(self, tags):
        if isinstance(tags, (list, tuple)):
            result = []
            for tag in tags:
                aList = self.getHandlersForOneTag(tag)
                result.extend(aList)
            return result
        else:
            return self.getHandlersForOneTag(tags)

    def getHandlersForOneTag(self, tag):
        aList = self.handlers.get(tag, [])
        return aList
    #@+node:ekr.20100910075900.10204: *4* plugins.getLoadedPlugins
    def getLoadedPlugins(self):
        return list(self.loadedModules.keys())
    #@+node:ekr.20100908125007.6020: *4* plugins.getPluginModule
    def getPluginModule(self, moduleName):
        return self.loadedModules.get(moduleName)
    #@+node:ekr.20100908125007.6021: *4* plugins.isLoaded
    def isLoaded(self, fn):
        return self.regularizeName(fn) in self.loadedModules
    #@+node:ekr.20100908125007.6025: *4* plugins.printHandlers
    def printHandlers(self, c, moduleName=None):
        '''Print the handlers for each plugin.'''
        tabName = 'Plugins'
        c.frame.log.selectTab(tabName)
        if moduleName:
            s = 'handlers for %s...\n' % (moduleName)
        else:
            s = 'all plugin handlers...\n'
        g.es(s + '\n', tabName=tabName)
        data = []
        modules = {}
        for tag in self.handlers:
            bunches = self.handlers.get(tag)
            for bunch in bunches:
                name = bunch.moduleName
                tags = modules.get(name, [])
                tags.append(tag)
                modules[name] = tags
        n = 4
        for key in sorted(modules):
            tags = modules.get(key)
            if moduleName in (None, key):
                for tag in tags:
                    n = max(n, len(tag))
                    data.append((tag, key),)
        lines = ['%*s %s\n' % (-n, s1, s2) for(s1, s2) in data]
        g.es('', ''.join(lines), tabName=tabName)
    #@+node:ekr.20100908125007.6026: *4* plugins.printPlugins
    def printPlugins(self, c):
        '''Print all enabled plugins.'''
        tabName = 'Plugins'
        c.frame.log.selectTab(tabName)
        data = []
        data.append('enabled plugins...\n')
        for z in sorted(self.loadedModules):
            data.append(z)
        lines = ['%s\n' % (s) for s in data]
        g.es('', ''.join(lines), tabName=tabName)
    #@+node:ekr.20100908125007.6027: *4* plugins.printPluginsInfo
    def printPluginsInfo(self, c):
        '''Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.'''
        d = self.loadedModulesFilesDict
        tabName = 'Plugins'
        c.frame.log.selectTab(tabName)
        data = []; n = 4
        for moduleName in d:
            fileName = d.get(moduleName)
            n = max(n, len(moduleName))
            data.append((moduleName, fileName),)
        lines = ['%*s %s\n' % (-n, s1, s2) for(s1, s2) in data]
        g.es('', ''.join(lines), tabName=tabName)
    #@+node:ekr.20100909065501.5949: *4* plugins.regularizeName
    def regularizeName(self, fn):
        '''Return the name used as a key to this modules dictionaries.'''
        if fn.endswith('.py'):
            fn = "leo.plugins." + fn[: -3]
        return fn
    #@+node:ekr.20100909104341.5979: *4* plugins.setLoaded
    def setLoaded(self, fn, m):
        self.loadedModules[self.regularizeName(fn)] = m
    #@+node:ekr.20100909065501.5953: *3* plugins.Load & unload
    #@+node:ekr.20100908125007.6022: *4* plugins.loadHandlers
    def loadHandlers(self, tag, keys):
        '''
        Load all enabled plugins.

        Using a module name (without the trailing .py) allows a plugin to
        be loaded from outside the leo/plugins directory.
        '''

        def pr(*args, **keys):
            if not g.app.unitTesting:
                g.es_print(*args, **keys)

        s = g.app.config.getEnabledPlugins()
        if not s: return
        if tag == 'open0' and not g.app.silentMode and not g.app.batchMode:
            if 0:
                s2 = '@enabled-plugins found in %s' % (
                    g.app.config.enabledPluginsFileName)
                g.blue(s2)
        for plugin in s.splitlines():
            if plugin.strip() and not plugin.lstrip().startswith('#'):
                self.loadOnePlugin(plugin.strip(), tag=tag)
    #@+node:ekr.20100908125007.6024: *4* plugins.loadOnePlugin
    def loadOnePlugin(self, moduleOrFileName, tag='open0', verbose=False):
        '''
        Load one plugin from a file name or module.
        Use extensive tracing if --trace-plugins is in effect.

        Using a module name allows plugins to be loaded from outside the leo/plugins directory.
        '''
        global optional_modules
            # verbose is no longer used: all traces are verbose
        trace = 'plugins' in g.app.debug
            # This trace can be useful during unit testing.
            # The proper way to disable this while running unit tests
            # externally is to set g.app.trace_plugins off.

        def report(message):
            g.es_print('loadOnePlugin: %s' % message)

        if not g.app.enablePlugins:
            if trace: report('plugins disabled: %s' % moduleOrFileName)
            return None
        if moduleOrFileName.startswith('@'):
            if trace: report('ignoring Leo directive: %s' % moduleOrFileName)
            return None
                # Return None, not False, to keep pylint happy.
                # Allow Leo directives in @enabled-plugins nodes.
        moduleName = self.regularizeName(moduleOrFileName)
        if self.isLoaded(moduleName):
            module = self.loadedModules.get(moduleName)
            if trace: report('already loaded: %s' % moduleName)
            return module
        assert g.app.loadDir
        moduleName = g.toUnicode(moduleName)
        # This import will typically result in calls to registerHandler.
        # if the plugin does _not_ use the init top-level function.
        self.loadingModuleNameStack.append(moduleName)
        try:
            __import__(moduleName)
            # need to look up through sys.modules, __import__ returns toplevel package
            result = sys.modules[moduleName]
        except g.UiTypeException:
            if trace: report('plugin %s does not support %s gui' % (moduleName, g.app.gui.guiName()))
            result = None
        except ImportError:
            if trace or tag == 'open0': # Just give the warning once.
                report('error importing plugin: %s' % moduleName)
                g.es_exception()
            result = None
        except SyntaxError:
            if trace or tag == 'open0': # Just give the warning once.
                report('syntax error importing plugin: %s' % moduleName)
                # g.es_exception()
            result = None
        except Exception:
            if trace:
                report('exception importing plugin: %s' % moduleName)
                g.es_exception()
            result = None
        self.loadingModuleNameStack.pop()
        if result:
            self.signonModule = result # for self.plugin_signon.
            self.loadingModuleNameStack.append(moduleName)
            if tag == 'unit-test-load':
                pass # Keep the result, but do no more.
            elif hasattr(result, 'init'):
                try:
                    # Indicate success only if init_result is True.
                    init_result = result.init()
                    if init_result not in (True, False):
                        report('%s.init() did not return a bool' % moduleName)
                    if init_result:
                        self.loadedModules[moduleName] = result
                        self.loadedModulesFilesDict[moduleName] = g.app.config.enabledPluginsFileName
                    else:
                        if trace: # not g.app.initing:
                            report('%s.init() returned False' % moduleName)
                        result = None
                except Exception:
                    if trace:
                        report('exception loading plugin: %s' % moduleName)
                        g.es_exception()
                    result = None
            else:
                # No top-level init function.
                # Guess that the module was loaded correctly,
                # but do *not* load the plugin if we are unit testing.
                if g.app.unitTesting:
                    result = None
                    self.loadedModules[moduleName] = None
                else:
                    if trace: report('fyi: no top-level init() function in %s' % moduleName)
                    self.loadedModules[moduleName] = result
            self.loadingModuleNameStack.pop()
        if g.app.batchMode or g.app.inBridge or g.unitTesting:
            pass
        elif result:
            if trace: report('loaded: %s' % moduleName)
        elif trace or self.warn_on_failure:
            if trace or tag == 'open0':
                if not g.app.gui.guiName().startswith('curses'):
                    if moduleName not in optional_modules:
                        report('can not load enabled plugin: %s' % moduleName)
        return result
    #@+node:ekr.20031218072017.1318: *4* plugins.plugin_signon
    def plugin_signon(self, module_name, verbose=False):
        '''Print the plugin signon.'''
        # This is called from as the result of the imports
        # in self.loadOnePlugin
        m = self.signonModule
        if verbose:
            g.es('', "...%s.py v%s: %s" % (
                m.__name__, m.__version__, g.plugin_date(m)))
            g.pr(m.__name__, m.__version__)
        self.signonModule = None # Prevent double signons.
    #@+node:ekr.20100908125007.6030: *4* plugins.unloadOnePlugin
    def unloadOnePlugin(self, moduleOrFileName, verbose=False):
        moduleName = self.regularizeName(moduleOrFileName)
        if self.isLoaded(moduleName):
            if verbose:
                g.pr('unloading', moduleName)
            del self.loadedModules[moduleName]
        for tag in self.handlers:
            bunches = self.handlers.get(tag)
            bunches = [bunch for bunch in bunches if bunch.moduleName != moduleName]
            self.handlers[tag] = bunches
    #@+node:ekr.20100909065501.5951: *3* plugins.Registration
    #@+node:ekr.20100908125007.6028: *4* plugins.registerExclusiveHandler
    def registerExclusiveHandler(self, tags, fn):
        """ Register one or more exclusive handlers"""
        if isinstance(tags, (list, tuple)):
            for tag in tags:
                self.registerOneExclusiveHandler(tag, fn)
        else:
            self.registerOneExclusiveHandler(tags, fn)

    def registerOneExclusiveHandler(self, tag, fn):
        """Register one exclusive handler"""
        try:
            moduleName = self.loadingModuleNameStack[-1]
        except IndexError:
            moduleName = '<no module>'
        if 0:
            if g.app.unitTesting: g.pr('')
            g.pr('%6s %15s %25s %s' % (g.app.unitTesting, moduleName, tag, fn.__name__))
        if g.app.unitTesting: return
        if tag in self.handlers:
            g.es("*** Two exclusive handlers for", "'%s'" % (tag))
        else:
            bunch = g.Bunch(fn=fn, moduleName=moduleName, tag='handler')
            self.handlers[tag] = [bunch] # Vitalije
    #@+node:ekr.20100908125007.6029: *4* plugins.registerHandler & registerOneHandler
    def registerHandler(self, tags, fn):
        """ Register one or more handlers"""
        if isinstance(tags, (list, tuple)):
            for tag in tags:
                self.registerOneHandler(tag, fn)
        else:
            self.registerOneHandler(tags, fn)

    def registerOneHandler(self, tag, fn):
        """Register one handler"""
        try:
            moduleName = self.loadingModuleNameStack[-1]
        except IndexError:
            moduleName = '<no module>'
        if 0:
            if g.app.unitTesting: g.pr('')
            g.pr('%6s %15s %25s %s' % (g.app.unitTesting, moduleName, tag, fn.__name__))
        items = self.handlers.get(tag, [])
        functions = [z.fn for z in items]
        if fn not in functions: # Vitalije
            bunch = g.Bunch(fn=fn, moduleName=moduleName, tag='handler')
            items.append(bunch)
        self.handlers[tag] = items
    #@+node:ekr.20100908125007.6031: *4* plugins.unregisterHandler
    def unregisterHandler(self, tags, fn):
        if isinstance(tags, (list, tuple)):
            for tag in tags:
                self.unregisterOneHandler(tag, fn)
        else:
            self.unregisterOneHandler(tags, fn)

    def unregisterOneHandler(self, tag, fn):
        bunches = self.handlers.get(tag)
        bunches = [bunch for bunch in bunches if bunch and bunch.fn != fn]
        self.handlers[tag] = bunches
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

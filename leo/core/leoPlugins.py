#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3439: * @file leoPlugins.py
"""Classes relating to Leo's plugin architecture."""
#@+<< leoPlugins imports & annotations >>
#@+node:ekr.20220901071118.1: ** << leoPlugins imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import sys
from typing import Any, Iterator, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    # mypy doesn't seem to handle this.
    Keywords = dict[str, list[g.Bunch]]
    Tag_List = Any  # Union[str, Sequence[str]]
#@-<< leoPlugins imports & annotations >>

# Define modules that may be enabled by default
# but that might not load because imports may fail.
optional_modules = [
    'leo.plugins.livecode',
    'leo.plugins.cursesGui2',
]
#@+others
#@+node:ekr.20100908125007.6041: ** Top-level functions (leoPlugins.py)
def init() -> None:
    """Init g.app.pluginsController."""
    g.app.pluginsController = LeoPluginsController()

def registerHandler(tags: Tag_List, fn: Callable) -> None:
    """A wrapper so plugins can still call leoPlugins.registerHandler."""
    return g.app.pluginsController.registerHandler(tags, fn)
#@+node:ville.20090222141717.2: ** TryNext (Exception)
class TryNext(Exception):
    """Try next hook exception.

    Raise this in your hook function to indicate that the next hook handler
    should be used to handle the operation.  If you pass arguments to the
    constructor those arguments will be used by the next hook instead of the
    original ones.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.args = args
        self.kwargs = kwargs
#@+node:ekr.20100908125007.6033: ** class CommandChainDispatcher
class CommandChainDispatcher:
    """ Dispatch calls to a chain of commands until some func can handle it

    Usage: instantiate, execute "add" to add commands (with optional
    priority), execute normally via f() calling mechanism.

    """

    def __init__(self, commands: list[Any] = None) -> None:
        if commands is None:
            self.chain = []
        else:
            self.chain = commands

    def __call__(self, *args: Any, **kw: Any) -> None:
        """ Command chain is called just like normal func.

        This will call all funcs in chain with the same args as were given to this
        function, and return the result of first func that didn't raise
        TryNext """
        for _prio, cmd in self.chain:
            try:
                ret = cmd(*args, **kw)
                return ret
            except TryNext as exc:
                if exc.args or exc.kwargs:
                    args = exc.args
                    kw = exc.kwargs
        # if no function will accept it, raise TryNext up to the caller
        raise TryNext

    def __str__(self) -> str:
        return str(self.chain)

    def add(self, func: Callable, priority: int = 0) -> None:
        """ Add a func to the cmd chain with given priority """
        self.chain.append((priority, func),)
        self.chain.sort(key=lambda z: z[0])

    def __iter__(self) -> Iterator:
        """ Return all objects in chain.

        Handy if the objects are not callable.
        """
        return iter(self.chain)
#@+node:ekr.20100908125007.6009: ** class BaseLeoPlugin
class BaseLeoPlugin:
    #@+<<docstring>>
    #@+node:ekr.20100908125007.6010: *3* <<docstring>>
    """A Convenience class to simplify plugin authoring

    .. contents::

    Usage
    =====

    Initialization
    --------------

    - import the base class::

        from leoPlugins from leo.core import leoBasePlugin

    - create a class which inherits from leoBasePlugin::

        class myPlugin(leoBasePlugin):

    - in the __init__ method of the class, call the parent constructor::

        def __init__(self, tag: str, keywords: Keywords) -> None:
            super().__init__(tag, keywords)

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

            def setCommand(
        self,
        commandName: Any,
        handler: Callable,
        shortcut: Any=None,
        pane: str='all',
        verbose: bool=True,
    ) -> None:

    - setMenuItem::

            def setMenuItem(self, menu: Wrapper, commandName: Any=None, handler: Callable=None) -> None:

    - setButton::

            def setButton(self, buttonText: Any=None, commandName: Any=None, color: Any=None) -> None:

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
            def __init__(self, tag: str, keywords: Keywords) -> None:

                # call parent __init__
                super().__init__(tag, keywords)

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

            def hello(self, event: LeoKeyEvent) -> None:
                g.pr("hello from node %s" % self.c.p.h)

            def hola(self, event: LeoKeyEvent) -> None:
                g.pr("hola from node %s" % self.c.p.h)

            def ciao(self, event: LeoKeyEvent) -> None:
                g.pr("ciao baby (%s)" % self.c.p.h)

        leoPlugins.registerHandler("after-create-leo-frame", Hello)

    """
    #@-<<docstring>>
    #@+others
    #@+node:ekr.20100908125007.6012: *3* __init__ (BaseLeoPlugin)
    def __init__(self, tag: str, keywords: Keywords) -> None:
        """
        Ctor for the BaseLeoPlugin class.
        """
        # mypy can't infer the type of keywords['c'].
        self.c: Cmdr = keywords['c']  # type:ignore
        self.commandNames: list[str] = []
    #@+node:ekr.20100908125007.6013: *3* setCommand
    def setCommand(
        self,
        commandName: Any,
        handler: Callable,
        shortcut: str = '',
        pane: str = 'all',
        verbose: bool = True,
    ) -> None:
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
    def setMenuItem(self, menu: Wrapper, commandName: str = None, handler: Callable = None) -> None:
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
    def setButton(self, buttonText: str = None, commandName: str = None, color: str = None) -> None:
        """Associate an existing command with a 'button'
        """
        if buttonText is None:
            buttonText = self.commandName
        if commandName is None:
            commandName = self.commandName
        else:
            if commandName not in self.commandNames:
                raise NameError(f"setButton error, {commandName} is not a commandName")
        if color is None:
            color = 'grey'
        script = f"c.doCommandByName('{self.commandName}')"
        g.app.gui.makeScriptButton(
            self.c,
            args=None,
            script=script,
            buttonText=buttonText, bg=color)
    #@-others
#@+node:ekr.20100908125007.6007: ** class LeoPluginsController
class LeoPluginsController:
    """The global plugins controller, g.app.pluginsController"""
    #@+others
    #@+node:ekr.20100909065501.5954: *3* plugins.Birth
    #@+node:ekr.20100908125007.6034: *4* plugins.ctor & reloadSettings
    def __init__(self) -> None:

        # Keys are tags, values are lists of bunches.
        self.handlers: dict[str, list[g.Bunch]] = {}
        # Keys are regularized module names, values are the names of .leo files
        # containing @enabled-plugins nodes that caused the plugin to be loaded
        self.loadedModulesFilesDict: dict[str, str] = {}
        # Keys are regularized module names, values are modules.
        self.loadedModules: dict[str, Any] = {}
        # The stack of module names. The top is the module being loaded.
        self.loadingModuleNameStack: list[str] = []
        self.signonModule = None  # A hack for plugin_signon.
        # Settings.  Set these here in case finishCreate is never called.
        self.warn_on_failure = True
        g.act_on_node = CommandChainDispatcher()
        g.visit_tree_item = CommandChainDispatcher()
        g.tree_popup_handlers = []
    #@+node:ekr.20100909065501.5974: *4* plugins.finishCreate & reloadSettings
    def finishCreate(self) -> None:
        self.reloadSettings()

    def reloadSettings(self) -> None:
        self.warn_on_failure = g.app.config.getBool(
            'warn_when_plugins_fail_to_load', default=True)
    #@+node:ekr.20100909065501.5952: *3* plugins.Event handlers
    #@+node:ekr.20161029060545.1: *4* plugins.on_idle
    def on_idle(self) -> None:
        """Call all idle-time hooks."""
        if g.app.idle_time_hooks_enabled:
            for frame in g.app.windowList:
                c = frame.c
                # Do NOT compute c.currentPosition.
                # This would be a MAJOR leak of positions.
                g.doHook("idle", c=c)
    #@+node:ekr.20100908125007.6017: *4* plugins.doHandlersForTag & helper
    def doHandlersForTag(self, tag: str, keywords: Keywords) -> Any:
        """
        Execute all handlers for a given tag, in alphabetical order.
        The caller, doHook, catches all exceptions.
        """
        if g.app.killed:
            return None
        #
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
    def callTagHandler(self, bunch: Any, tag: str, keywords: Keywords) -> Any:
        """Call the event handler."""
        handler, moduleName = bunch.fn, bunch.moduleName
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
            g.es(f"hook failed: {tag}, {handler}, {moduleName}")
            g.es_exception()
            result = None
        self.loadingModuleNameStack.pop()
        return result
    #@+node:ekr.20100908125007.6018: *4* plugins.doPlugins (g.app.hookFunction)
    def doPlugins(self, tag: str, keywords: Keywords) -> Any:
        """The default g.app.hookFunction."""
        if g.app.killed:
            return None
        if tag in ('start1', 'open0'):
            self.loadHandlers(tag, keywords)
        return self.doHandlersForTag(tag, keywords)
    #@+node:ekr.20100909065501.5950: *3* plugins.Information
    #@+node:ekr.20100908125007.6019: *4* plugins.getHandlersForTag
    def getHandlersForTag(self, tags: list[str]) -> list[Any]:
        if isinstance(tags, (list, tuple)):
            result = []
            for tag in tags:
                aList = self.getHandlersForOneTag(tag)
                result.extend(aList)
            return result
        return self.getHandlersForOneTag(tags)

    def getHandlersForOneTag(self, tag: str) -> list[Any]:
        return self.handlers.get(tag, [])
    #@+node:ekr.20100910075900.10204: *4* plugins.getLoadedPlugins
    def getLoadedPlugins(self) -> list[str]:
        return list(self.loadedModules.keys())
    #@+node:ekr.20100908125007.6020: *4* plugins.getPluginModule
    def getPluginModule(self, moduleName: str) -> Any:
        return self.loadedModules.get(moduleName)
    #@+node:ekr.20100908125007.6021: *4* plugins.isLoaded
    def isLoaded(self, fn: str) -> bool:
        return self.regularizeName(fn) in self.loadedModules
    #@+node:ekr.20100908125007.6025: *4* plugins.printHandlers
    def printHandlers(self, c: Cmdr) -> None:
        """Print the handlers for each plugin."""
        tabName = 'Plugins'
        c.frame.log.selectTab(tabName)
        g.es_print('all plugin handlers...\n', tabName=tabName)
        data = []
        # keys are module names: values are lists of tags.
        modules_d: dict[str, list[str]] = {}
        for tag in self.handlers:
            bunches = self.handlers.get(tag)
            for bunch in bunches:
                fn = bunch.fn
                name = bunch.moduleName
                tags = modules_d.get(name, [])
                tags.append(tag)
                key = f"{name}.{fn.__name__}"
                modules_d[key] = tags
        n = 4
        for module in sorted(modules_d):
            tags = modules_d.get(module)
            for tag in tags:
                n = max(n, len(tag))
                data.append((tag, module),)
        lines = sorted(list(set(
            ["%*s %s\n" % (-n, s1, s2) for (s1, s2) in data])))
        g.es_print('', ''.join(lines), tabName=tabName)
    #@+node:ekr.20100908125007.6026: *4* plugins.printPlugins
    def printPlugins(self, c: Cmdr) -> None:
        """Print all enabled plugins."""
        tabName = 'Plugins'
        c.frame.log.selectTab(tabName)
        data = []
        data.append('enabled plugins...\n')
        for z in sorted(self.loadedModules):
            data.append(z)
        lines = [f"{z}\n" for z in data]
        g.es('', ''.join(lines), tabName=tabName)
    #@+node:ekr.20100908125007.6027: *4* plugins.printPluginsInfo
    def printPluginsInfo(self, c: Cmdr) -> None:
        """
        Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.
        """
        d = self.loadedModulesFilesDict
        tabName = 'Plugins'
        c.frame.log.selectTab(tabName)
        data = []
        n = 4
        for moduleName in d:
            fileName = d.get(moduleName)
            n = max(n, len(moduleName))
            data.append((moduleName, fileName),)
        lines = ["%*s %s\n" % (-n, s1, s2) for (s1, s2) in data]
        g.es('', ''.join(lines), tabName=tabName)
    #@+node:ekr.20100909065501.5949: *4* plugins.regularizeName
    def regularizeName(self, moduleOrFileName: str) -> str:
        """
        Return the module name used as a key to this modules dictionaries.

        We *must* allow .py suffixes, for compatibility with @enabled-plugins nodes.
        """
        if not moduleOrFileName.endswith(('py', 'pyw')):
            # A module name. Return it unchanged.
            return moduleOrFileName
        #
        # 1880: The legacy code implicitly assumed that os.path.dirname(fn) was empty!
        #       The new code explicitly ignores any directories in the path.
        fn = g.os_path_basename(moduleOrFileName)
        return "leo.plugins." + g.os_path_splitext(fn)[0]
    #@+node:ekr.20100909065501.5953: *3* plugins.Load & unload
    #@+node:ekr.20100908125007.6022: *4* plugins.loadHandlers
    def loadHandlers(self, tag: str, keywords: Keywords) -> None:
        """
        Load all enabled plugins.

        Using a module name (without the trailing .py) allows a plugin to
        be loaded from outside the leo/plugins directory.
        """

        def pr(*args: Any, **keywords: Keywords) -> None:
            if not g.unitTesting:
                g.es_print(*args, **keywords)

        s = g.app.config.getEnabledPlugins()
        if not s:
            return
        if tag == 'open0' and not g.app.silentMode and not g.app.batchMode:
            if 0:
                s2 = f"@enabled-plugins found in {g.app.config.enabledPluginsFileName}"
                g.blue(s2)
        for plugin in s.splitlines():
            if plugin.strip() and not plugin.lstrip().startswith('#'):
                self.loadOnePlugin(plugin.strip(), tag=tag)
    #@+node:ekr.20100908125007.6024: *4* plugins.loadOnePlugin & helper functions
    def loadOnePlugin(self, moduleOrFileName: Any, tag: str = 'open0', verbose: bool = False) -> Any:
        """
        Load one plugin from a file name or module.
        Use extensive tracing if --trace-plugins is in effect.

        Using a module name allows plugins to be loaded from outside the leo/plugins directory.
        """
        global optional_modules

        moduleName: str

        trace = verbose or 'plugins' in g.app.debug

        def report(message: str) -> None:
            if trace:
                g.es_print(f"loadOnePlugin: {message}")

        # Define local helper functions.
        #@+others
        #@+node:ekr.20180528160855.1: *5* function:callInitFunction
        def callInitFunction(result: Any) -> Any:
            """True to call the top-level init function."""
            try:
                # Indicate success only if init_result is True.
                # Careful: this may throw an exception.
                init_result = result.init()
                if init_result not in (True, False):
                    report(f"{moduleName}.init() did not return a bool")
                if init_result:
                    self.loadedModules[moduleName] = result
                    self.loadedModulesFilesDict[moduleName] = (
                        g.app.config.enabledPluginsFileName
                    )
                else:
                    report(f"{moduleName}.init() returned False")
                    result = None
            except Exception:
                report(f"exception loading plugin: {moduleName}")
                g.es_exception()
                result = None
            return result
        #@+node:ekr.20180528162604.1: *5* function:finishImport
        def finishImport(result: Any) -> Any:
            """Handle last-minute checks."""
            if tag == 'unit-test-load':
                return result  # Keep the result, but do no more.
            if hasattr(result, 'init'):
                return callInitFunction(result)
            #
            # No top-level init function.
            if g.unitTesting:
                # Do *not* load the module.
                self.loadedModules[moduleName] = None
                return None
            # Guess that the module was loaded correctly.
            report(f"fyi: no top-level init() function in {moduleName}")
            self.loadedModules[moduleName] = result
            return result
        #@+node:ekr.20180528160744.1: *5* function:loadOnePluginHelper
        def loadOnePluginHelper(moduleName: str) -> Any:
            result = None
            try:
                __import__(moduleName)
                # Look up through sys.modules, __import__ returns toplevel package
                result = sys.modules[moduleName]
            except g.UiTypeException:
                report(f"plugin {moduleName} does not support {g.app.gui.guiName()} gui")
            except ImportError:
                report(f"error importing plugin: {moduleName}")
            # except ModuleNotFoundError:
                # report('module not found: %s' % moduleName)
            except SyntaxError:
                report(f"syntax error importing plugin: {moduleName}")
            except Exception:
                report(f"exception importing plugin: {moduleName}")
                g.es_exception()
            return result
        #@+node:ekr.20180528162300.1: *5* function:reportFailedImport
        def reportFailedImport() -> None:
            """Report a failed import."""
            if g.app.batchMode or g.app.inBridge or g.unitTesting:
                return
            if (
                self.warn_on_failure and
                tag == 'open0' and
                not g.app.gui.guiName().startswith('curses') and
                moduleName not in optional_modules
            ):
                report(f"can not load enabled plugin: {moduleName}")
        #@-others
        if not g.app.enablePlugins:
            report(f"plugins disabled: {moduleOrFileName}")
            return None
        if moduleOrFileName.startswith('@'):
            report(f"ignoring Leo directive: {moduleOrFileName}")
            # Return None, not False, to keep pylint happy.
            # Allow Leo directives in @enabled-plugins nodes.
            return None
        moduleName = self.regularizeName(moduleOrFileName)
        if self.isLoaded(moduleName):
            module = self.loadedModules.get(moduleName)
            return module
        assert g.app.loadDir
        moduleName = g.toUnicode(moduleName)
        #
        # Try to load the plugin.
        try:
            self.loadingModuleNameStack.append(moduleName)
            result = loadOnePluginHelper(moduleName)
        finally:
            self.loadingModuleNameStack.pop()
        if not result:
            if trace:
                reportFailedImport()
            return None
        #
        # Last-minute checks.
        try:
            self.loadingModuleNameStack.append(moduleName)
            result = finishImport(result)
        finally:
            self.loadingModuleNameStack.pop()
        if result:
            # #1688: Plugins can update globalDirectiveList.
            #        Recalculate g.directives_pat.
            g.update_directives_pat()
            report(f"loaded: {moduleName}")
        self.signonModule = result  # for self.plugin_signon.
        return result
    #@+node:ekr.20031218072017.1318: *4* plugins.plugin_signon
    def plugin_signon(self, module_name: str, verbose: bool = False) -> None:
        """Print the plugin signon."""
        # This is called from as the result of the imports
        # in self.loadOnePlugin
        m = self.signonModule
        if verbose:
            g.es(f"...{m.__name__}.py v{m.__version__}: {g.plugin_date(m)}")
            g.pr(m.__name__, m.__version__)
        self.signonModule = None  # Prevent double signons.
    #@+node:ekr.20100908125007.6030: *4* plugins.unloadOnePlugin
    def unloadOnePlugin(self, moduleOrFileName: str, verbose: bool = False) -> None:
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
    def registerExclusiveHandler(self, tags: Tag_List, fn: Callable) -> None:
        """ Register one or more exclusive handlers"""
        if isinstance(tags, (list, tuple)):
            for tag in tags:
                self.registerOneExclusiveHandler(tag, fn)
        else:
            self.registerOneExclusiveHandler(tags, fn)

    def registerOneExclusiveHandler(self, tag: str, fn: Callable) -> None:
        """Register one exclusive handler"""
        try:
            moduleName = self.loadingModuleNameStack[-1]
        except IndexError:
            moduleName = '<no module>'
        # print(f"{g.unitTesting:6} {moduleName:15} {tag:25} {fn.__name__}")
        if g.unitTesting:
            return
        if tag in self.handlers:
            g.es(f"*** Two exclusive handlers for '{tag}'")
        else:
            bunch = g.Bunch(fn=fn, moduleName=moduleName, tag='handler')
            aList = self.handlers.get(tag, [])
            aList.append(bunch)
            self.handlers[tag] = aList
    #@+node:ekr.20100908125007.6029: *4* plugins.registerHandler & registerOneHandler
    def registerHandler(self, tags: Tag_List, fn: Callable) -> None:
        """ Register one or more handlers"""
        if isinstance(tags, (list, tuple)):
            for tag in tags:
                self.registerOneHandler(tag, fn)
        else:
            self.registerOneHandler(tags, fn)

    def registerOneHandler(self, tag: str, fn: Callable) -> None:
        """Register one handler"""
        try:
            moduleName = self.loadingModuleNameStack[-1]
        except IndexError:
            moduleName = '<no module>'
        # print(f"{g.unitTesting:6} {moduleName:15} {tag:25} {fn.__name__}")
        items = self.handlers.get(tag, [])
        functions = [z.fn for z in items]
        if fn not in functions:  # Vitalije
            bunch = g.Bunch(fn=fn, moduleName=moduleName, tag='handler')
            items.append(bunch)
        self.handlers[tag] = items
    #@+node:ekr.20100908125007.6031: *4* plugins.unregisterHandler
    def unregisterHandler(self, tags: Tag_List, fn: Callable) -> None:
        if isinstance(tags, (list, tuple)):
            for tag in tags:
                self.unregisterOneHandler(tag, fn)
        else:
            self.unregisterOneHandler(tags, fn)

    def unregisterOneHandler(self, tag: str, fn: Callable) -> None:
        bunches = self.handlers.get(tag)
        bunches = [bunch for bunch in bunches if bunch and bunch.fn != fn]
        self.handlers[tag] = bunches
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@-leo

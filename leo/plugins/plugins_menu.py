#@+leo-ver=5-thin
#@+node:EKR.20040517080555.2: * @file ../plugins/plugins_menu.py
#@+<< plugins_menu docstring >>
#@+node:ekr.20050101090207.9: ** << plugins_menu docstring >>
""" Creates a Plugins menu and adds all actives plugins to it.

Selecting these menu items will bring up a short **About Plugin** dialog
with the details of the plugin. In some circumstances a submenu will be created
instead and an 'About' menu entry will be created in this.

**INI files and the Properties Dialog**

If a file exists in the plugins directory with the same file name as the plugin
but with a .ini extension instead of .py, then a **Properties** item will be
created in a submenu. Selecting this item will pop up a Properties Dialog which
will allow the contents of this file to be edited.

The .ini file should be formated for use by the python ConfigParser class.

**Special Methods**

Certain methods defined at the top level are considered special.

cmd_XZY
    If a method is defined at the module level with a name of the form
    **cmd_XZY** then a menu item **XZY** will be created which will invoke
    **cmd_XZY** when it is selected. These menus will appear in a sub menu.

applyConfiguration

topLevelMenu
    This method, if it exists, will be called when the user clicks on the plugin
    name in the plugins menu (or the **About** item in its submenu), but only if
    the plugin was loaded properly and registered with g.plugin_signon.

**Special Variable Names**

Some names defined at the top level have special significance.

__plugin_name__
    This will be used to define the name of the plugin and will be used
    as a label for its menu entry.

__plugin_priority__
    Plugins can also attempt to select the order they will appear in the menu by
    defining a __plugin_prioriy__. The menu will be created with the highest
    priority items first. This behavior is not guaranteed since other plugins
    can define any priority. This priority does not affect the order of calling
    handlers.
    To change the order select a number outside the range 0-200 since this range
    is used internally for sorting alphabetically. Properties and INI files.

"""
#@-<< plugins_menu docstring >>
# Written by Paul A. Paterson.  Revised by Edward K. Ream.
# To do: add Revert button to each dialog.
# **Important**: this plugin is gui-independent.
#@+<< plugins_menu imports & annotations >>
#@+node:ekr.20050101090207.10: ** << plugins_menu imports & annotations >>
from __future__ import annotations
import configparser as ConfigParser
import os
from typing import Any, Sequence, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    Item = Any
    Group = Any
    Menu = Any
#@-<< plugins_menu imports & annotations >>

__plugin_name__ = "Plugins Menu"
__plugin_priority__ = -100
__plugin_group__ = "Core"

#@+others
#@+node:ekr.20060107091318: ** Functions
#@+node:EKR.20040517080555.24: *3* addPluginMenuItem
def addPluginMenuItem(plugin: PlugIn, c: Cmdr) -> None:
    """
    @param plugin:  Plugin object for one currently loaded plugin
    @param c:       Leo-editor "commander" for the current .leo file
    """
    plugin_name = plugin.name.split('.')[-1]  # TNB 20100304 strip module path
    table: Sequence
    if plugin.hastoplevel:
        # Check at runtime to see if the plugin has actually been loaded.
        # This prevents us from calling hasTopLevel() on unloaded plugins.

        def callback(event: Event, c: Cmdr = c, plugin: "PlugIn" = plugin) -> None:
            path, name = g.os_path_split(plugin.filename)
            name, ext = g.os_path_splitext(name)
            pc = g.app.pluginsController
            if pc and pc.isLoaded(name):
                plugin.hastoplevel(c)
            else:
                plugin.about()

        table = ((plugin_name, None, callback),)
        c.frame.menu.createMenuEntries(PluginDatabase.getMenu(plugin), table)
    elif plugin.hasconfig or plugin.othercmds:
        #@+<< Get menu location >>
        #@+node:pap.20050305153147: *4* << Get menu location >>
        if plugin.group:
            menu_location = plugin.group
        else:
            menu_location = "&Plugins"
        #@-<< Get menu location >>
        m = c.frame.menu.createNewMenu(plugin_name, menu_location)
        table = [("About...", None, plugin.about)]
        if plugin.hasconfig:
            table.append(("Properties...", None, plugin.properties))
        if plugin.othercmds:
            table.append(("-", None, None))
            items = []
            d = plugin.othercmds
            for cmd in list(d.keys()):
                fn = d.get(cmd)
                items.append((cmd, None, fn),)  # No need for a callback.
            table.extend(sorted(items))
        c.frame.menu.createMenuEntries(m, table)
    else:
        table = [(plugin_name, None, plugin.about)]
        c.frame.menu.createMenuEntries(PluginDatabase.getMenu(plugin), table)
#@+node:EKR.20040517080555.23: *3* createPluginsMenu & helper
def createPluginsMenu(tag: str, keywords: Any) -> None:
    """Create the plugins menu: calld from create-optional-menus hook."""
    c = keywords.get("c")
    if not c:
        return
    menu_name = keywords.get('menu_name', '&Plugins')
    pc = g.app.pluginsController
    lmd = pc.loadedModules
    if lmd:
        impModSpecList = list(lmd.keys())

        def key(aList: list) -> str:
            return aList.split('.')[-1].lower()

        impModSpecList.sort(key=key)  # type:ignore
        plgObList: list[PlugIn] = [PlugIn(lmd[impModSpec], c) for impModSpec in impModSpecList]
        c.pluginsMenu = pluginMenu = c.frame.menu.createNewMenu(menu_name)
        # 2013/12/13: Add any items in @menu plugins
        add_menu_from_settings(c)
        PluginDatabase.setMenu("Default", pluginMenu)
        # Add group menus
        for group_name in PluginDatabase.getGroups():
            PluginDatabase.setMenu(group_name,
                c.frame.menu.createNewMenu(group_name, menu_name))
        for plgObj in plgObList:
            addPluginMenuItem(plgObj, c)
#@+node:ekr.20131213072223.19531: *4* add_menu_from_settings
def add_menu_from_settings(c: Cmdr) -> None:
    # Add any items in @menu plugins
    aList = c.config.getMenusList()
    for z in aList:
        kind, val, val2 = z
        if kind.startswith('@menu'):
            name = kind[len('@menu') :].strip().strip('&')
            if name.lower() == 'plugins':
                table = []
                for kind2, val21, val22 in val:
                    if kind2 == '@item':
                        # Similar to createMenuFromConfigList.
                        name = str(val21)  # Item names must always be ascii.
                        if val21:
                            # Translated names can be unicode.
                            table.append((val21, name),)
                        else:
                            table.append(name)
                if table:
                    c.frame.menu.createMenuEntries(c.pluginsMenu, table)
                return
#@+node:ekr.20070302175530: *3* init
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    if g.unitTesting:
        return False
    if not g.app.gui:
        g.app.createDefaultGui()
    ok = g.app.gui.guiName() == 'qt'
    if ok:
        g.registerHandler("create-optional-menus", createPluginsMenu)
        g.plugin_signon(__name__)
    return ok
#@+node:pap.20050305152751: ** class PluginDatabase
class _PluginDatabase:
    """Stores information on Plugins"""
    #@+others
    #@+node:pap.20050305152751.1: *3* __init__
    def __init__(self) -> None:
        """Initialize"""
        self.plugins_by_group: dict[Group, list[Any]] = {}
        self.groups_by_plugin: dict[Any, list[Group]] = {}
        self.menus: dict[str, Menu] = {}
    #@+node:pap.20050305152751.2: *3* addPlugin
    def addPlugin(self, item: Item, group: Group) -> None:
        """Add a plugin"""
        if group:
            self.plugins_by_group.setdefault(group, []).append(item)
            self.groups_by_plugin[item] = group
    #@+node:pap.20050305152751.3: *3* getGroups
    def getGroups(self) -> list[Any]:
        """Return a list of groups"""
        groups = list(self.plugins_by_group.keys())
        groups.sort()
        return groups
    #@+node:pap.20050305153716: *3* setMenu
    def setMenu(self, name: str, menu: Menu) -> None:
        """Store the menu for this group"""
        self.menus[name] = menu
    #@+node:pap.20050305153716.1: *3* getMenu
    def getMenu(self, item: Item) -> Menu:
        """Get the menu for a particular item"""
        try:
            return self.menus[item.group]
        except KeyError:
            return self.menus["Default"]
    #@-others

PluginDatabase = _PluginDatabase()
#@+node:EKR.20040517080555.3: ** class PlugIn
class PlugIn:
    """A class to hold information about one plugin"""
    #@+others
    #@+node:EKR.20040517080555.4: *3* PlugIn.__init__ & helper
    def __init__(self, plgMod: Any, c: Cmdr = None) -> None:
        """
        @param plgMod: Module object for the plugin represented by this instance.
        @param c:  Leo-editor "commander" for the current .leo file
        """
        self.c = c
        self.mod = plgMod
        self.name = self.moduleName = None
        self.doc = self.version = None
        try:
            self.name = self.mod.__plugin_name__
        except AttributeError:
            self.name = self.getNiceName(self.mod.__name__)
        self.moduleName = self.mod.__name__
        self.group = getattr(self.mod, "__plugin_group__", None)
        PluginDatabase.addPlugin(self, self.group)
        try:
            self.priority = self.mod.__plugin_priority__
        except AttributeError:
            self.priority = 200 - ord(self.name[0])
        self.doc = self.mod.__doc__
        self.version = self.mod.__dict__.get("__version__", "<unknown>")
        # g.pr(self.version,g.shortFileName(filename))
        # Configuration...
        self.configfilename = "%s.ini" % os.path.splitext(plgMod.__file__)[0]
        # True if this can be configured.
        self.hasconfig = os.path.isfile(self.configfilename)
        # Look for an applyConfiguration function in the module.
        # This is used to apply changes in configuration from the properties window
        self.hasapply = hasattr(plgMod, "applyConfiguration")
        self.create_menu()  # Create menu items from cmd_* functions.
        # Use a toplevel menu item instead of the default About.
        try:
            self.hastoplevel = self.mod.__dict__["topLevelMenu"]
        except KeyError:
            self.hastoplevel = False
    #@+node:EKR.20040517080555.7: *4* create_menu (Plugin)
    def create_menu(self) -> None:
        """
        Add items in the main menu for each decorated command in this plugin.
        The g.command decorator sets func.is_command & func.command_name.
        """
        self.othercmds = {}
        for item in self.mod.__dict__.keys():
            func = self.mod.__dict__[item]
            if getattr(func, 'is_command', None):
                self.othercmds[func.command_name] = func
    #@+node:EKR.20040517080555.8: *3* PlugIn.about
    def about(self, event: Event = None) -> None:
        """Put information about this plugin in a scrolledMessage dialog."""
        c = self.c
        msg = self.doc.strip() + '\n' if self.doc else ''
        c.putHelpFor(msg, short_title=self.name)
    #@+node:pap.20050317183526: *3* PlugIn.getNiceName
    def getNiceName(self, name: str) -> str:
        """Return a nice version of the plugin name

        Historically some plugins had "at_" and "mod_" prefixes to their
        name which makes the name look a little ugly in the lists. There is
        no real reason why the majority of users need to know the underlying
        name so here we create a nice readable version.

        """
        lname = name.lower()
        if lname.startswith("at_"):
            name = name[3:]
        elif lname.startswith("mod_"):
            name = name[4:]
        return name.capitalize()
    #@+node:EKR.20040517080555.9: *3* PlugIn.properties
    def properties(self, event: Event = None) -> None:
        """Display a modal properties dialog for this plugin"""
        if self.hasapply:

            def callback(name: str, data: Any) -> None:
                self.updateConfiguration(data)
                self.mod.applyConfiguration(self.config)
                self.writeConfiguration()

            buttons = ['Apply']
        else:
            callback = None
            buttons = []
        self.config = config = ConfigParser.ConfigParser()
        config.read(self.configfilename)
        # Load config data into dictionary of dictianaries.
        # Do no allow for nesting of sections.
        data = {}
        for section in config.sections():
            options = {}
            for option in config.options(section):
                options[option] = config.get(section, option)
            data[section] = options
        # Save the original config data. This will not be changed.
        self.sourceConfig = data
        # Open a modal dialog and wait for it to return.
        # Provide the dialog with a callback for the 'Appply' function.
        title = "Properties of " + self.name
        result, data = g.app.gui.runPropertiesDialog(title, data, callback, buttons)
        if result != 'Cancel' and data:
            self.updateConfiguration(data)
            self.writeConfiguration()
    #@+node:bob.20071209102050: *3* PlugIn.updateConfiguration
    def updateConfiguration(self, data: Any) -> None:
        """Update the config object from the dialog 'data' structure"""
        # Should we clear the config object first?
        for section in data.keys():
            for option in data[section].keys():
                # This is configParser.set, not g.app.config.set, so it is ok.
                self.config.set(section, option, data[section][option])
    #@+node:bob.20071208033759: *3* PlugIn.writeConfiguration
    def writeConfiguration(self) -> None:
        """Write the configuration to a file."""
        f = open(self.configfilename, "w")
        try:
            self.config.write(f)
        except Exception:
            f.close()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

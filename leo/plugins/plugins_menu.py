#@+leo-ver=5-thin
#@+node:EKR.20040517080555.2: * @file plugins_menu.py
#@+<< docstring >>
#@+node:ekr.20050101090207.9: ** << docstring >>
''' Creates a Plugins menu and adds all actives plugins to it.

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

'''
#@-<< docstring >>

# Written by Paul A. Paterson.  Revised by Edward K. Ream.
# To do: add Revert button to each dialog.

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20050101090207.10: ** << imports >>
import leo.core.leoGlobals as g

# **Important**: this plugin is gui-independent.

if g.isPython3:
    import configparser as ConfigParser
else:
    import ConfigParser

import glob
import os
import sys
#@-<< imports >>
__version__ = "2.3"

__plugin_name__ = "Plugins Menu"
__plugin_priority__ = -100
__plugin_group__ = "Core"

#@+others
#@+node:ekr.20060107091318: ** Functions
#@+node:EKR.20040517080555.24: *3* addPluginMenuItem
def addPluginMenuItem (p,c):
    """
    @param p:  Plugin object for one currently loaded plugin
    @param c:  Leo-editor "commander" for the current .leo file
    """

    trace = False
    plugin_name = p.name.split('.')[-1]  # TNB 20100304 strip module path

    if p.hastoplevel:
        # Check at runtime to see if the plugin has actually been loaded.
        # This prevents us from calling hasTopLevel() on unloaded plugins.
        def callback (event,c=c,p=p):
            path, name = g.os_path_split(p.filename)
            name, ext = g.os_path_splitext(name)
            pc = g.app.pluginsController
            if pc and pc.isLoaded(name):
                p.hastoplevel(c)
            else:
                p.about()
        table = ((plugin_name,None,callback),)
        c.frame.menu.createMenuEntries(PluginDatabase.getMenu(p),table,dynamicMenu=True)
    elif p.hasconfig or p.othercmds:
        #@+<< Get menu location >>
        #@+node:pap.20050305153147: *4* << Get menu location >>
        if p.group:
            menu_location = p.group
        else:
            menu_location = "&Plugins"
        #@-<< Get menu location >>
        m = c.frame.menu.createNewMenu(plugin_name,menu_location)
        table = [("About...",None,p.about)]
        if p.hasconfig:
            table.append(("Properties...",None,p.properties))
        if p.othercmds:
            table.append(("-",None,None))
            items = []
            d = p.othercmds
            for cmd in list(d.keys()):
                fn = d.get(cmd)
                # New in 4.4: this callback gets called with an event arg.
                def cmd_callback (event,c=c,fn=fn):
                    fn(c)
                items.append((cmd,None,cmd_callback),)
            items.sort()
            table.extend(items)
        if trace: g.trace(table)
        c.frame.menu.createMenuEntries(m,table,dynamicMenu=True)
    else:
        table = ((plugin_name,None,p.about),)
        if trace: g.trace(plugin_name)
        c.frame.menu.createMenuEntries(PluginDatabase.getMenu(p),table,dynamicMenu=True)
#@+node:EKR.20040517080555.23: *3* createPluginsMenu
def createPluginsMenu (tag,keywords):

    c = keywords.get("c")
    if not c: return

    pc = g.app.pluginsController
    lmd = pc.loadedModules
    if lmd:
        impModSpecList = list(lmd.keys())
        def key(aList):
            return aList.split('.')[-1].lower()
        impModSpecList.sort(key=key)
        plgObList = [PlugIn(lmd[impModSpec], c) for impModSpec in impModSpecList]
        c.pluginsMenu = pluginMenu = c.frame.menu.createNewMenu("&Plugins")
        PluginDatabase.setMenu("Default", pluginMenu)
        # Add group menus
        for group_name in PluginDatabase.getGroups():
            PluginDatabase.setMenu(group_name,
                c.frame.menu.createNewMenu(group_name, "&Plugins"))

        for plgObj in plgObList:
            addPluginMenuItem(plgObj, c)
#@+node:ekr.20070302175530: *3* init
def init ():
    if g.app.unitTesting: return None

    if not g.app.gui:
        g.app.createDefaultGui()

    if g.app.gui.guiName() not in ('qt','qttabs',):
        return False

    g.registerHandler("create-optional-menus",createPluginsMenu)
    g.plugin_signon(__name__)

    return True
#@+node:pap.20050305152751: ** class PluginDatabase
class _PluginDatabase:
    """Stores information on Plugins"""

    #@+others
    #@+node:pap.20050305152751.1: *3* __init__
    def __init__(self):
        """Initialize"""
        self.plugins_by_group = {}
        self.groups_by_plugin = {}
        self.menus = {}
    #@+node:pap.20050305152751.2: *3* addPlugin
    def addPlugin(self, item, group):
        """Add a plugin"""
        if group:
            self.plugins_by_group.setdefault(group, []).append(item)
            self.groups_by_plugin[item] = group
    #@+node:pap.20050305152751.3: *3* getGroups
    def getGroups(self):
        """Return a list of groups"""
        groups = list(self.plugins_by_group.keys())
        groups.sort()
        return groups
    #@+node:pap.20050305153716: *3* setMenu
    def setMenu(self, name, menu):
        """Store the menu for this group"""
        self.menus[name] = menu
    #@+node:pap.20050305153716.1: *3* getMenu
    def getMenu(self, item):
        """Get the menu for a particular item"""
        try:
            return self.menus[item.group]
        except KeyError:
            return self.menus["Default"]
    #@-others

PluginDatabase = _PluginDatabase()
#@+node:EKR.20040517080555.3: ** class Plugin
class PlugIn:

    """A class to hold information about one plugin"""

    #@+others
    #@+node:EKR.20040517080555.4: *3* __init__
    def __init__(self, plgMod, c=None):
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
        #

        self.doc = self.mod.__doc__
        self.version = self.mod.__dict__.get("__version__","<unknown>") # EKR: 3/17/05
        # if self.version: g.pr(self.version,g.shortFileName(filename))

        #@+<< Check if this can be configured >>
        #@+node:EKR.20040517080555.5: *4* << Check if this can be configured >>
        # Look for a configuration file
        self.configfilename = "%s.ini" % os.path.splitext(plgMod.__file__)[0]
        self.hasconfig = os.path.isfile(self.configfilename)
        #@-<< Check if this can be configured >>
        #@+<< Check if this has an apply >>
        #@+node:EKR.20040517080555.6: *4* << Check if this has an apply >>
        #@+at Look for an apply function ("applyConfiguration") in the module.
        # 
        # This is used to apply changes in configuration from the properties window
        #@@c

        self.hasapply = hasattr(plgMod, "applyConfiguration")
        #@-<< Check if this has an apply >>
        #@+<< Look for additional commands >>
        #@+node:EKR.20040517080555.7: *4* << Look for additional commands >>
        #@+at Additional commands can be added to the plugin menu by having functions in the module called "cmd_whatever". These are added to the main menu and will be called when clicked
        #@@c

        self.othercmds = {}

        for item in self.mod.__dict__.keys():
            if item.startswith("cmd_"):
                self.othercmds[self.niceMenuName(item)] = self.mod.__dict__[item]

                # start of command name from module (plugin) name
                base = []
                for l in self.mod.__name__:
                    if base and base[-1] != '-' and l.isupper():
                        base.append('-')
                    base.append(l)
                base = ''.join(base).lower().replace('.py','').replace('_','-')

                base = base.split('.')[-1]  # TNB 20100304 strip module path

                # rest of name from item
                ltrs = []
                for l in item[4:]:
                    if ltrs and ltrs[-1] != '-' and l.isupper():
                        ltrs.append('-')
                    ltrs.append(l)
                name = base+'-'+''.join(ltrs).lower().replace('_','-')

                # make and create command
                cmd = self.mod.__dict__[item]
                def wrapped(kw, cmd=cmd):
                    return cmd(kw['c'])
                self.c.keyHandler.registerCommand(name, None, wrapped)
        #@-<< Look for additional commands >>
        #@+<< Look for toplevel menu item >>
        #@+node:pap.20041009131822: *4* << Look for toplevel menu item >>
        #@+at Check to see if there is a toplevel menu item - this will be used instead of the default About
        #@@c

        try:
            self.hastoplevel = self.mod.__dict__["topLevelMenu"]
        except KeyError:
            self.hastoplevel = False
        #@-<< Look for toplevel menu item >>
    #@+node:EKR.20040517080555.8: *3* about
    def about(self,event=None):

        """Put information about this plugin in a scrolledMessage dialog."""

        c = self.c
        if self.doc:
            msg = self.doc.strip()+'\n'
        else:
            msg = ''

        # 2011/10/20: runScrolledMessageDialog looks for a scrolledmessage hook.
        # Don't do it here.
        g.app.gui.runScrolledMessageDialog(
            c=c,
            flags='rst',
            label="Version: " + self.version,
            msg=msg,
            name='leo_system',
            short_title = self.name,
            title="About Plugin ( " + self.name + " )",
        )
    #@+node:pap.20050317183526: *3* getNiceName
    def getNiceName(self, name):
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
    #@+node:EKR.20040517080555.9: *3* properties
    def properties(self, event=None):

        """Display a modal properties dialog for this plugin"""

        if self.hasapply:

            def callback(name, data):
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
                #g.pr('config', section, option )
                options[option] = g.u(config.get(section,option))
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

    #@+node:bob.20071209102050: *3* updateConfiguration
    def updateConfiguration(self, data):
        """Update the config object from the dialog 'data' structure"""

        # Should we clear the config object first?


        for section in data.keys():
            for option in data[section].keys():
                # This is configParser.set, not g.app.config.set, so it is ok.
                self.config.set(section, option, data[section][option])
    #@+node:bob.20071208033759: *3* writeConfiguration
    def writeConfiguration(self):
        """Write the configuration to a file."""

        f = open(self.configfilename, "w")
        try:
            self.config.write(f)
        except:
            f.close()
    #@+node:pap.20051011215345: *3* niceMenuName
    @staticmethod
    def niceMenuName(name):
        """Return a nice version of the command name for the menu

        The command will be of the form::

            cmd_ThisIsIt

        We want to convert this to "This Is It".

        """
        text = ""
        for char in name[4:]:
            if char.isupper() and text:
                text += " "
            text += char
        return text
    #@-others

#@-others
#@-leo

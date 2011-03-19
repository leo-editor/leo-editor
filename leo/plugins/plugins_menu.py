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
if g.app.gui.guiName() == 'tkinter':
    if g.isPython3:
        Tk = None
    else:
        Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=False)

if g.isPython3:
    import configparser as ConfigParser
else:
    import ConfigParser

import glob
import os
import sys
#@-<< imports >>
__version__ = "2.2"
#@+<< version history >>
#@+node:ekr.20050101100033: ** << version history >>
#@@nocolor
#@+at
# 
# 1.4 EKR: Check at runtime to make sure that the plugin has been loaded before calling topLevelMenu function.
# 1.5 EKR:
# - Check for ImportError directly in Plugin.__init__.
#   Alas, this can not report import problems without more work.
#   This _really_ should be done, but it will have to wait.
#   As a workaround, plugins_manager.py now has an init method and reports its own import problems.
# 1.6 Paul Paterson:
# - Add support for plugin groups. Each group gets its own sub menu now
# - Set __plugin_group__ to "Core"
# 1.7 EKR: Set default version in Plugin.__init__ so plugins without version still appear in plugin menu.
# 1.8 Paul Paterson: Changed the names in the plugin menu to remove at_, mod_ and capitalized.
# 1.9 Paul Paterson:
# - Refactored to allow dynamically adding plugins to the menu after initial load
# - Reformatted menu items for cmd_ThisIsIt to be "This Is It"
# 1.10 EKR: Removed the g.app.dialog hack.
# 1.11 EKR: Added event arg to cmd_callback.  This was causing crashes in several plugins.
# 1.12 EKR: Fixed bug per http://sourceforge.net/forum/message.php?msg_id=3810157
# 1.13 EKR:
# - Always Plugin.name and Plugin.realname for use by createPluginsMenu.
# - Add plugins to Plugins menu *only* if they have been explicitly enabled.
#   This solves the HTTP mystery: HTTP was being imported by mod_scripting plugin.
# 1.14 EKR: Added init function.
# 1.15 plumloco: Separated out the gui elements of the 'properties' and 'about' dialogs to make the plugin gui independant.
# 1.16 bobjack:
# - Added 'Text to HTML' and 'RST to HTML' buttons to TkScrolledMessageDialog.
# - Converted docstring to RST.
# 2.0 EKR: Now works with Python 3.x.
# 2.2 SegundoBob:  Allow plugins not in leo/plugins.
#@-<< version history >>

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
            for cmd, fn in p.othercmds.iteritems():
                # New in 4.4: this callback gets called with an event arg.
                def cmd_callback (event,c=c,fn=fn):
                    fn(c)
                items.append((cmd,None,cmd_callback),)
            items.sort()
            table.extend(items)
        c.frame.menu.createMenuEntries(m,table,dynamicMenu=True)
    else:
        table = ((plugin_name,None,p.about),)
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
        #@+<< Add group menus >>
        #@+node:pap.20050305152223: *4* << Add group menus >>
        for group_name in PluginDatabase.getGroups():

            PluginDatabase.setMenu(
                group_name,
                c.frame.menu.createNewMenu(group_name, "&Plugins"))
        #@-<< Add group menus >>
        for plgObj in plgObList:
            addPluginMenuItem(plgObj, c)
#@+node:ekr.20070302175530: *3* init
def init ():
    if g.app.unitTesting: return None

    if not g.app.gui:
        g.app.createDefaultGui()

    if g.app.gui.guiName() not in ("tkinter",'qt'):
        return False

    g.registerHandler("create-optional-menus",createPluginsMenu)
    g.plugin_signon(__name__)

    if g.app.gui.guiName() == 'tkinter':
        g.app.gui.runPropertiesDialog = runPropertiesDialog
        g.app.gui.runScrolledMessageDialog = runScrolledMessageDialog

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

        if self.doc:
            msg = self.doc.strip()+'\n'
            # msg = msg.replace('\\n','\\\\n')
        else:
            msg = ''

        g.app.gui.runScrolledMessageDialog(
            short_title = self.name,
            title="About Plugin ( " + self.name + " )",
            label="Version: " + self.version,
            msg=msg,
            c=self.c,
            flags='rst',
            name='leo_system'
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

#@+node:EKR.20040517080555.10: ** class TkPropertiesDialog
class TkPropertiesDialog:

    """A class to create and run a Properties dialog"""

    #@+others
    #@+node:bob.20071208030419: *3* __init__
    def __init__(self, title, data, callback=None, buttons=[]):
        #@+<< docstring >>
        #@+node:bob.20071208211442: *4* << docstring >>
        """ Initializes and shows a Properties dialog.

            'buttons' should be a list of names for buttons.

            'callback' should be None or a function of the form:

                def cb(name, data)
                    ...
                    return 'close' # or anything other than 'close'

            where name is the name of the button clicked and data is
            a data structure representing the current state of the dialog.

            If a callback is provided then when a button (other than
            'OK' or 'Cancel') is clicked then the callback will be called
            with name and data as parameters.

                If the literal string 'close' is returned from the callback
                the dialog will be closed and self.result will be set to a
                tuple (button, data).

                If anything other than the literal string 'close' is returned
                from the callback, the dialog will continue to be displayed.

            If no callback is provided then when a button is clicked the
            dialog will be closed and self.result set to  (button, data).

            The 'ok' and 'cancel' buttons (which are always provided) behave as
            if no callback was supplied.

        """
        #@-<< docstring >>

        if buttons is None:
            buttons = []

        self.entries = []
        self.title = title
        self.callback = callback
        self.buttons = buttons
        self.data = data

        #@+<< create the frame from the configuration data >>
        #@+node:bob.20071208030419.2: *4* << Create the frame from the configuration data >>
        root = g.app.root

        #@+<< Create the top level and the main frame >>
        #@+node:bob.20071208030419.3: *5* << Create the top level and the main frame >>
        self.top = top = Tk.Toplevel(root)
        g.app.gui.attachLeoIcon(self.top)
        #top.title("Properties of "+ plugin.name)
        top.title(title)

        top.resizable(0,0) # neither height or width is resizable.

        self.frame = frame = Tk.Frame(top)
        frame.pack(side="top")
        #@-<< Create the top level and the main frame >>
        #@+<< Create widgets for each section and option >>
        #@+node:bob.20071208030419.4: *5* << Create widgets for each section and option >>
        # Create all the entry boxes on the screen to allow the user to edit the properties

        sections = data.keys()
        sections.sort()

        for section in sections:

            # Create a frame for the section.
            f = Tk.Frame(top, relief="groove",bd=2)
            f.pack(side="top",padx=5,pady=5)
            Tk.Label(f, text=section.capitalize()).pack(side="top")

            # Create an inner frame for the options.
            b = Tk.Frame(f)
            b.pack(side="top",padx=2,pady=2)

            options = data[section].keys()
            options.sort()

            row = 0
            # Create a Tk.Label and Tk.Entry for each option.
            for option in options:
                e = Tk.Entry(b)
                e.insert(0, data[section][option])
                Tk.Label(b, text=option).grid(row=row, column=0, sticky="e", pady=4)
                e.grid(row=row, column=1, sticky="ew", pady = 4)
                row += 1
                self.entries.append((section, option, e))
        #@-<< Create widgets for each section and option >>
        #@+<< Create the buttons >>
        #@+node:bob.20071208030419.5: *5* << Create the buttons >>
        box = Tk.Frame(top, borderwidth=5)
        box.pack(side="bottom")

        buttons.extend(("OK", "Cancel"))

        for name in buttons:
            Tk.Button(box,
                text=name,
                width=6,
                command=lambda self=self, name=name: self.onButton(name)
            ).pack(side="left",padx=5)

        #@-<< Create the buttons >>

        g.app.gui.center_dialog(top) # Do this after packing.
        top.grab_set() # Make the dialog a modal dialog.
        top.focus_force() # Get all keystrokes.

        self.result = ('Cancel', '')

        root.wait_window(top)
        #@-<< create the frame from the configuration data >>
    #@+node:EKR.20040517080555.17: *3* Event Handlers

    def onButton(self, name):
        """Event handler for all button clicks."""

        data = self.getData()
        self.result = (name, data)

        if name in ('OK', 'Cancel'):
            self.top.destroy()
            return

        if self.callback:
            retval = self.callback(name, data)
            if retval == 'close':
                self.top.destroy()
            else:
                self.result = ('Cancel', None)


    #@+node:EKR.20040517080555.18: *3* getData
    def getData(self):
        """Return the modified configuration."""

        data = {}
        for section, option, entry in self.entries:
            if section not in data:
                data[section] = {}
            s = entry.get()
            s = g.toEncodedString(s,"ascii",reportErrors=True) # Config params had better be ascii.
            data[section][option] = s

        return data


    #@-others
#@+node:EKR.20040517080555.19: ** class TkScrolledMessageDialog
class TkScrolledMessageDialog:

    """A class to create and run a Scrolled Message dialog for Tk"""

    default_buttons = ["Text to HTML", "RST to HTML", "Close"]

    #@+others
    #@+node:EKR.20040517080555.20: *3* __init__
    def __init__(self, title='Message', label= '', msg='', callback=None, buttons=None):

        """Create and run a modal dialog showing 'msg' in a scrollable window."""

        if buttons is None:
            buttons = []

        self.callback = callback
        self.title = title
        self.label = label
        self.msg = msg

        self.buttons = buttons or []

        self.buttons.extend(self.default_buttons)

        self.result = ('Cancel', None)

        root = g.app.root
        self.top = top = Tk.Toplevel(root)
        g.app.gui.attachLeoIcon(self.top)

        top.title(title)
        top.resizable(1,1) # height and width is resizable.

        frame = Tk.Frame(top)
        frame.pack(side="top", expand=True, fill='both')

        #@+<< Create the contents of the about box >>
        #@+node:EKR.20040517080555.21: *4* << Create the contents of the about box >>
        #Tk.Label(frame,text="Version " + version).pack()

        if label:
            Tk.Label(frame, text=label).pack()

        body = w = g.app.gui.plainTextWidget(
            frame,name='body-pane',
            bd=2,bg="white",relief="flat",setgrid=0,wrap='word')
        w.insert(0,msg)
        if 0: # prevents arrow keys from being visible.
            w.configure(state='disabled')
        w.setInsertPoint(0)
        w.see(0)

        bodyBar = Tk.Scrollbar(frame,name='bodyBar')
        body['yscrollcommand'] = bodyBar.set
        bodyBar['command'] = body.yview

        bodyBar.pack(side="right", fill="y")
        body.pack(expand=1,fill="both")

        def destroyCallback(event=None,top=top):
            self.result = ('Cancel', None)
            top.destroy()

        body.bind('<Return>',destroyCallback)

        g.app.gui.set_focus(None,body)
        #@-<< Create the contents of the about box >>

        self.create_the_buttons(top, self.buttons)

        g.app.gui.center_dialog(top) # Do this after packing.
        top.grab_set() # Make the dialog a modal dialog.
        top.focus_force() # Get all keystrokes.

        root.wait_window(top)
    #@+node:bobjack.20080320174907.4: *3* create_the_buttons
    def create_the_buttons(self, parent, buttons):

        """
        Create the TK buttons and pack them in a button box.
        """

        box = Tk.Frame(parent, borderwidth=5)
        box.pack(side="bottom")

        for name in buttons:
            Tk.Button(box,
                text=name,
                command=lambda self=self, name=name: self.onButton(name)
            ).pack(side="left",padx=5)
    #@+node:bobjack.20080320193548.2: *3* get_default_buttons
    #@+node:bob.20071209110304.1: *3* Event Handlers

    def onButton(self, name):
        """Event handler for all button clicks."""

        retval = ''

        if name in self.default_buttons:

            if name in ('Close'):
                self.top.destroy()
                return

            retval = self.show_message_as_html(name)

        elif self.callback:

            retval = self.callback(name) or ''

        if retval.lower() == 'close':
            self.top.destroy()
        else:
            self.result = ('Cancel', None)


    #@+node:bobjack.20080317174956.3: *3* show_message_as_html
    def show_message_as_html(self, name):

        try:
            import leo.plugins.leo_to_html as leo_to_html
        except ImportError:
            g.es('Can not import leo.plugins.leo_to_html as leo_to_html', color='red')
            return

        oHTML = leo_to_html.Leo_to_HTML(c=None) # no need for a commander

        oHTML.loadConfig()
        oHTML.silent = True 
        oHTML.myFileName = oHTML.title = self.title + ' ' + self.label

        if name.lower().startswith('text'):
            retval = self.show_text_message(oHTML)
        elif name.lower().startswith('rst'):
            retval = self.show_rst_message(oHTML)
        else:
            return

        return retval
    #@+node:bobjack.20080320174907.2: *3* show_rst_message
    def show_rst_message(self, oHTML):

        try:
            from docutils import core
        except ImportError:
            g.es('Can not import docutils', color='red')
            return

        overrides = {
            'doctitle_xform': False,
            'initial_header_level': 1
        }

        parts = core.publish_parts(
            source=self.msg,
            writer_name='html',
            settings_overrides=overrides
        )

        oHTML.xhtml = parts['whole']
        oHTML.show()

        return 'close'
    #@+node:bobjack.20080320174907.3: *3* show_text_message
    def show_text_message(self, oHTML):

        oHTML.xhtml = '<pre>' + self.msg + '</pre>'
        oHTML.applyTemplate()
        oHTML.show()

        return 'close'
    #@-others
#@+node:bob.20071208211442.1: ** runPropertiesDialog
def runPropertiesDialog(title='Properties', data={}, callback=None, buttons=None):
    """Dispay a modal TkPropertiesDialog"""


    dialog = TkPropertiesDialog(title, data, callback, buttons)

    return dialog.result 
#@+node:bob.20071209110304: ** runScrolledMessageDialog
def runScrolledMessageDialog(title='Message', label= '', msg='', callback=None, buttons=None, **kw):
    """Display a modal TkScrolledMessageDialog."""

    dialog = TkScrolledMessageDialog(title, label, msg, callback, buttons)

    return dialog.result
#@-others
#@-leo

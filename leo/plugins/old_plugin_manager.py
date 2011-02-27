#@+leo-ver=5-thin
#@+node:pap.20041006184225: * @file old_plugin_manager.py
"""
A plugin to manage Leo's Plugins:

- Enables and disables plugins.
- Shows plugin details.
- Checks for conflicting hook handlers.
- Checks for and updates plugins from the web.
"""

# This plugins has been disabled until it can be rewritten to handle @enabled-plugins nodes.

__version__ = "0.25"
__plugin_name__ = "Plugin Manager"
__plugin_priority__ = 10000
__plugin_requires__ = ["plugin_menu"]
__plugin_group__ = "Core"

#@+<< version history >>
#@+node:pap.20041006184225.2: ** << version history >>
#@+at
# 
# 0.1 Paul Paterson: Initial version
# 0.2 EKR:
# - The check for .ini files looks for the actual x.ini file.
#   (This required that spellpyx uses spellpyx.ini rather than mod_spelling.ini.)
# - Minor stylistic changes.
# 0.4 EKR:
# - Added USE_PRIORITY switch.
#   Priority is non-functional, and isn't needed.
#   Leo loads plugins in the order in which they appear in pluginsManager.txt.
#   Furthermore, this plugin preserves that order.
# 0.5 EKR: Make sure to do nothing if Pmw is not defined.
# 0.6 Paul Paterson:
# - Fixed incorrect detection of version if single quotes used
# - Now always detects a file as a plugin (previously only did this if it imported leoPlugins)
# - Fixed incorrect detection of handlers if single quotes used
# - Fixed incorrect detection of multiple handlers in a single line.
# 0.7 EKR:
# - The Sets module is not defined in Python 2.2.
#   This must be replaced.  This is too important a plugin for it not to work everywhere.
# - Added better import tests, and message when import fails.
# - Added an init method, although a simple raise would also work.
# 0.8 EKR:
# - Use g.importExtension rather than import to get sets module.
# 0.9 Paul Paterson:
# - Remove the "not referenced" status. All plugins are not active or inactive.
# - Changed the list view to have the status at the end of the line
# - Changed format of list view to be fixed font so that it looks cleaner
# - Also changed format of conflict list view
# - If a file contains "__not_a_plugin__ = True" then it will be omitted from the list
# - Now looks for and reports the __plugin_group__ in the view and list
# - Can now filter the plugins by their __plugin__group__
# - Set __plugin_group__ to "Core"
# - Renamed active/inactive to on/off as this works better with the groups
# - Added version history display to plugin view
# 0.10 Paul Paterson:
# - Changed the names in the plugin list view to remove at_, mod_ and capitalized
# - Remove dblClick event from plugin list - it wasn't doing anything
# - Can now be run stand-alone to aid in debugging problems
# 0.11 EKR: Use stand-alone leoGlobals module to simplify code.
# 0.12 EKR: Folded in some minor changes from Paul to support AutoTrees plugin.
# 0.13 Paul Paterson
# - Fixed path in installPlugin that ignore the local_paths setting
# - Generalized code to support LeoUpdate plugin.
# 0.14 EKR:
# - Several methods now return if get.keywords('c') is None.
#   This may fix some startup bugs, or not.
# 0.15 Paul Paterson:
# - Reorganized to speed loading of initial display
# - Added a "Close" button. Guess what it does?!
# - Added code to dynamically enable a plugin at runtime
# 0.16 Paul Paterson: Complete code to dynamically enable plugins
# 0.17 Paul Paterson:
# - Speeded up the getVersionHistory step of reading plugins
# - Allow specification of plugin load order.
# 0.18 EKR: Added g.app.dialogs hack to ensure dialog stays in front.
# 0.19 EKR: Removed call to Pmw.initialise [sic]. This is now done in Leo's core.
# 0.20 EKR: (removed g.top)
# - Init registers no hooks.
# - Added new 'c' arg to topLevelMenu.
# - ManagerDialog now remembers c (c will be None if called standalone).
# - Added ctor to LocalPluginCollection.
# - LocalPluginCollection uses self.c rather than g.top>
# - Can't enable plugins dynamically when called stand-alone.
# - Removed KEYWORDS hack.
# 0.21 EKR: Removed the g.app.dialog hack.
# 0.22 EKR: Just changed these comments.
# 0.23 EKR: Changed g.createStandAloneApp to createStandAloneTkApp to make clear the dependency.
# 0.24 EKR: Standalone version of the code now works again.
# 0.25 EKR: Define local_dict in base PluginList class.  This fixes a crasher.
#@-<< version history >>
#@+<< define importLeoGlobals >>
#@+node:ekr.20050329035844: ** << define importLeoGlobals >>
def importLeoGlobals():

    '''
    Try to import leo.core.leoGlobals as leoGlobals from the leo/src directory, assuming that
    the script using this function is in a subdirectory of the leo directory.
    '''

    plugins_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__),'..','src'))

    if plugins_path in sys.path:
        return None
    else:
        sys.path.append(plugins_path)
        try:
            import leo.core.leoGlobals as g
            return g
        except ImportError:
            g.pr('can not import leo.core.leoGlobals as leoGlobals from %s' % (plugins_path))
            return None
#@-<< define importLeoGlobals >>
#@+<< imports >>
#@+node:pap.20041006184225.3: ** << imports >>
#
# If these don't import then your Python install is hosed anyway so we don't
# protect the import statements
import fnmatch
import os
import re
import sha
import sys
import urllib
import threading
import webbrowser
import traceback
import time

try:
    import leo.core.leoGlobals as g
    standalone = False
except ImportError:
    standalone = True
    g = importLeoGlobals()

ok = g is not None
if ok:
    try:
        Pmw = g.importExtension("Pmw",    pluginName=__name__,verbose=True,required=True)
        Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)
    except SystemExit:
        raise
    except Exception:
        import sys
        s = 'plugins_manager.py: %s: %s' % (sys.exc_type,sys.exc_value)
        g.pr(s)
        ok = False
#@-<< imports >>
#@+<< todo >>
#@+node:pap.20041009141528: ** << todo >>
"""

Todo list:

- getting subset of plugins from CVS
- categorize plugins
- filter on categories
- size of plugin
- add required plugins to conflict check
- help for nomenclature

Done

- restore list top position when updating plugin list 
- proper view of remote file (colourized code)
- __requires__ list for plugins
- show __requires__
- proper dialog to show conflict list and error list from CVS

"""
#@-<< todo >>

USE_PRIORITY = False # True: show non-functional priority field.

#@+others
#@+node:ekr.20060107092833: ** Module-level Functions
#@+node:ekr.20050213122944: *3* init
def init():

    global ok

    ok = ok and g.app.gui.guiName() == "tkinter"

    # Ok for unit testing: adds menu.
    if ok:
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20041231134702: *3* topLevelMenu
# This is called from plugins_menu plugin.

# It should only be defined if the extension has been registered.

def topLevelMenu(c):

    """Manage the plugins"""

    dlg = ManagerDialog(c,True)
#@+node:pap.20041006193459: ** Error Classes
class InvalidPlugin(Exception):
    """The plugin is invalid"""

class InvalidCollection(Exception):
    """The plugin collection is invalid"""

class InvalidManager(Exception):
    """The enable manager is invalid"""
#@+node:pap.20050305144720: ** inColumns
def inColumns(data, columnwidths):
    """Return the items of data with the specified column widths

    The list of widths should be one less than the list of data, eg
        inColumns((10,20,30), (5,5))
    """
    format = ""
    for col in columnwidths:
        format += "%%-%ds" % col
    format += "%s"
    #
    return format % data
#@+node:pap.20041009140132: ** UI
#@+node:pap.20041008224318: *3* class PluginView
class PluginView(Tk.Frame):

    """Frame to display a plugin's information"""

    #@+others
    #@+node:pap.20041008224318.1: *4* PluginView.__init__
    def __init__(self, parent, file_text, *args, **kw):

        """Initialize the view"""

        Tk.Frame.__init__(self, parent, *args, **kw)

        self.file_text = file_text
        self.top = Tk.Frame(self)
        self.top.pack(side="top", fill="both", expand=1)
        self.bottom = Tk.Frame(self)
        self.bottom.pack(side="top", fill="both")

        #@+others
        #@+node:pap.20041008230728: *5* Name
        self.name = Pmw.EntryField(self.top,
            labelpos = 'w',label_text = 'Name:')

        self.name.pack(side="top", fill="x", expand=0)
        #@+node:pap.20041008230728.2: *5* Version
        self.version = Pmw.EntryField(self.top,
                labelpos = 'w',label_text = 'Version:')

        self.version.pack(side="top", fill="x", expand=0)
        #@+node:pap.20041008231028: *5* Status
        self.status = Pmw.EntryField(self.top,
                labelpos = 'w',
                label_text = 'Status:',
        )

        self.status.pack(side="top", fill="x", expand=0)
        #@+node:pap.20050305151106: *5* Group
        self.group = Pmw.EntryField(self.top,
                labelpos = 'w',label_text = 'Group:')

        self.group.pack(side="top", fill="x", expand=0)
        #@+node:pap.20041008230728.1: *5* Filename
        self.filename = Pmw.EntryField(self.top,
                labelpos = 'w',
                label_text = 'Filename:',
        )

        self.filename.pack(side="top", fill="x", expand=0)
        #@+node:pap.20041008231930: *5* Has INI
        self.has_ini = Pmw.EntryField(self.top,
                labelpos = 'w',
                label_text = 'Has INI:',
        )

        self.has_ini.pack(side="top", fill="x", expand=0)
        #@+node:pap.20041009135426: *5* Has Top level
        self.has_toplevel = Pmw.EntryField(self.top,
                labelpos = 'w',
                label_text = 'Has top level:',
        )

        self.has_toplevel.pack(side="top", fill="x", expand=0)
        #@+node:pap.20041009135426.1: *5* Priority
        if USE_PRIORITY:
            self.priority = Pmw.EntryField(self.top,
                labelpos = 'w',
                label_text = 'Priority:',
            )

            self.priority.pack(side="top", fill="x", expand=0)
        #@+node:pap.20041008231028.1: *5* Description & Versions
        self.text_panel = Pmw.NoteBook(self.top)
        self.text_panel.pack(side="top", fill='both', expand=1, padx=5, pady=5)

        description_panel = self.text_panel.add('Description')
        version_panel = remote_list_page = self.text_panel.add('Version History')

        #@+<< Description >>
        #@+node:pap.20050305170921: *6* << Description >>
        self.description = Pmw.ScrolledText(description_panel,
                # borderframe = 1,
                labelpos = 'n',
                label_text='%s Description' % self.file_text,
                columnheader = 0,
                rowheader = 0,
                rowcolumnheader = 0,
                usehullsize = 1,
                hull_width = 300,
                hull_height = 300,
                text_wrap='word',
                text_padx = 4,
                text_pady = 4,
        )
        self.description.pack(side="top", fill='both', expand=1)
        #@-<< Description >>
        #@+<< Version History >>
        #@+node:pap.20050305170921.1: *6* << Version History >>

        self.version_history = Pmw.ScrolledText(version_panel,
                # borderframe = 1,
                labelpos = 'n',
                label_text='%s History' % self.file_text,
                columnheader = 0,
                rowheader = 0,
                rowcolumnheader = 0,
                usehullsize = 1,
                hull_width = 300,
                hull_height = 300,
                text_wrap='word',
                text_padx = 4,
                text_pady = 4,
        )
        self.version_history.pack(side="top", fill='both', expand=1)
        #@-<< Version History >>
        #@+node:pap.20041008231028.2: *5* Commands
        self.commands = Pmw.ScrolledListBox(self.bottom,
                labelpos='n',
                label_text='Commands',
                listbox_height = 6,
                usehullsize = 1,
                hull_width = 150,
                hull_height = 100,
        )

        self.commands.pack(side="left", fill='both', expand=1)
        #@+node:pap.20041008231028.3: *5* Handlers
        self.handlers = Pmw.ScrolledListBox(self.bottom,
                labelpos='n',
                label_text='Hooks',
                listbox_height = 6,
                usehullsize = 1,
                hull_width = 150,
                hull_height = 100,
        )

        self.handlers.pack(side="left", fill='both', expand=1)
        #@+node:pap.20041009224739: *5* Requires
        self.requires = Pmw.ScrolledListBox(self.bottom,
                labelpos='n',
                label_text='Requires',
                listbox_height = 6,
                usehullsize = 1,
                hull_width = 150,
                hull_height = 100,
        )

        self.requires.pack(side="left", fill='both', expand=1)
        #@-others

        if USE_PRIORITY:
            Pmw.alignlabels([
                self.name, self.version, self.status, self.group,
                self.filename, self.has_ini, self.has_toplevel,
                self.priority, 
            ])
        else:
             Pmw.alignlabels([
                self.name, self.version, self.status, self.group,
                self.filename, self.has_ini, self.has_toplevel,
            ])
    #@+node:pap.20041008224625: *4* showPlugin
    def showPlugin(self, plugin):
        """Show a plugin"""
        # First make sure that the plugin details have been read
        plugin.ensureDetails()
        self.name.setentry(plugin.name)
        self.version.setentry(plugin.version)
        self.group.setentry(plugin.group)
        self.filename.setentry(g.os_path_abspath(plugin.filename)) # EKR
        self.status.setentry(plugin.enabled)
        self.has_ini.setentry(
            g.choose(plugin.has_config,"Yes","No"))
        self.has_toplevel.setentry(
            g.choose(plugin.has_toplevel,"Yes","No"))
        if USE_PRIORITY:
            self.priority.setentry(plugin.priority)
        self.description.settext(plugin.description.strip())
        self.version_history.settext(plugin.versions.strip())
        self.commands.setlist(plugin.commands)
        self.handlers.setlist(plugin.handlers)
        self.requires.setlist(plugin.requires)
    #@-others
#@+node:pap.20041008225226: *3* class PluginList
class PluginList(Tk.Frame):
    """Frame to display a list of plugins"""

    filter_options = []
    title = "List"
    secondtitle = "Groups"

    #@+others
    #@+node:pap.20041008225226.1: *4* __init__
    def __init__(self, parent, plugin_view, plugins, file_text="Plugin", *args, **kw):
        """Initialize the list"""
        Tk.Frame.__init__(self, parent, *args, **kw)

        self.local_dict = {}

        self.file_text = file_text

        self.box = Pmw.ScrolledListBox(self,
                labelpos='nw',
                label_text='%s:' % (self.title % self.file_text),
                listbox_height = 6,
                selectioncommand=self.onClick,
                usehullsize = 1,
                hull_width = 300,
                hull_height = 200,
        )

        self.box.component("listbox").configure(font=("Courier", 8))

        self.filter = Pmw.OptionMenu(self,
                labelpos = 'w',
                label_text = '%s:' % (self.title % self.file_text),
                items = self.filter_options,
                menubutton_width = 16,
                command=self.populateList,
        )    

        self.filter.pack(side="top")

        self.secondfilter = Pmw.OptionMenu(self,
                labelpos = 'w',
                label_text = '%s:' % self.secondtitle,
                items = ["All"],
                menubutton_width = 16,
                command=self.populateList,
        )    

        Pmw.alignlabels([self.filter, self.secondfilter])

        self.secondfilter.pack(side="top")

        self.box.pack(side="bottom", fill='both', expand=1)    

        self.plugin_view = plugin_view
        self.plugins = plugins
    #@+node:pap.20041006215903: *4* onClick
    def onClick(self):
        """Select an item in the list"""
        sels = self.box.getcurselection()
        if len(sels) == 0:
            pass
        else:
            self.plugin_view.showPlugin(self.local_dict[sels[0]])
    #@+node:pap.20041008223406: *4* populateList
    def populateList(self, filter=None):
        """Populate the plugin list"""
        if not self.plugins:
            self.box.setlist([])
            return
        #if filter is None:
        filter = self.filter.getcurselection()
        secondfilter = self.secondfilter.getcurselection()
        #
        # Get old selection so that we can restore it    
        current_text = self.box.getcurselection()
        if current_text:
            current_index = self.listitems.index(current_text[0])
        #
        # Show the list
        self.local_dict = dict([(self.plugins[name].asString(), self.plugins[name])
                                    for name in self.plugins])
        self.listitems = [self.plugins[name].asString() 
                            for name in self.plugins.sortedNames()
                            if filter in ("All", self.plugins[name].enabled) 
                            and secondfilter in ("All", self.plugins[name].group)]
        self.box.setlist(self.listitems)    
        #
        if current_text:
            try:
                self.box.setvalue((self.listitems[current_index],))
                self.box.component("listbox").see(current_index)
            except IndexError:
                pass # Sometimes the list is just different!
            else:
                self.onClick()
    #@+node:pap.20041008233733: *4* getSelectedPlugin
    def getSelectedPlugin(self):
        """Return the selected plugin"""
        sels = self.box.getcurselection()
        if len(sels) == 0:
            return None
        else:
            return self.local_dict[sels[0]]
    #@+node:pap.20050305160811: *4* setSecondFilterList
    def setSecondFilterList(self, list_items):
        """Set the items to use in the second filter list"""
        self.secondfilter.setitems(list_items)
    #@+node:pap.20050605192322: *4* getAllPlugins
    def getAllPlugins(self):
        """Return all the plugins"""
        return self.local_dict.values()
    #@-others




#@+node:pap.20051102233259: *3* class LoadOrderView
class LoadOrderView(Tk.Frame):
    """Shows the load order of items"""

    #@+others
    #@+node:pap.20051102233259.1: *4* __init__
    def __init__(self, parent, file_text="Plugin", collection=None, enabler=None, 
                 plugin_view=None, *args, **kw):
        """Initialise the view"""
        Tk.Frame.__init__(self, parent, *args, **kw)

        self.file_text = file_text
        self.collection = collection
        self.enabler = enabler
        self.plugin_view = plugin_view

        self.items = Pmw.ScrolledListBox(self,
                labelpos='nw',
                label_text='%s:' % self.file_text,
                selectioncommand = self.onClick,
                listbox_height = 6,
                usehullsize = 1,
                hull_width = 300,
                hull_height = 200,
        )

        self.items.component("listbox").configure(font=("Courier", 8))
        self.items.pack(side="top", fill='both', expand=1)    

        self.buttonBox = Pmw.ButtonBox(
            self,
            labelpos = 'w',
            label_text = 'Change Order',
            frame_borderwidth = 2,
            frame_relief = 'groove')

        self.buttonBox.add('First', command = self.moveFirst)
        self.buttonBox.add('Up', command = self.moveUp)
        self.buttonBox.add('Down', command = self.moveDown)
        self.buttonBox.add('Last', command = self.moveLast)
        self.buttonBox.add('Save', command = self.save)

        self.buttonBox.alignbuttons()

        self.buttonBox.pack(side="top", padx=5)    

    #@+node:pap.20051103000804: *4* initList
    def initList(self):
        """Initialise the members of the list"""
        self.items.setlist([self.collection[name].nicename for name in self.enabler.actives])
        self.local_dict = dict([(self.collection[name].nicename, self.collection[name])
                                    for name in self.collection])
    #@+node:pap.20051102233801: *4* moveFirst
    def moveFirst(self):
        """Move the plugin to the first"""
        item = self.getSelection()
        if item:
            self.enabler.actives.moveFirst(item.name)
            self.initList()
            self.items.setvalue([item.nicename])
    #@+node:pap.20051102233937: *4* moveUp
    def moveUp(self):
        """Move the plugin up one"""
        item = self.getSelection()
        if item:
            self.enabler.actives.moveUp(item.name)
            self.initList()
            self.items.setvalue([item.nicename])        
    #@+node:pap.20051102233937.1: *4* moveDown
    def moveDown(self):
        """Move the plugin down one"""
        item = self.getSelection()
        if item:
            self.enabler.actives.moveDown(item.name)
            self.initList()
            self.items.setvalue([item.nicename])        
    #@+node:pap.20051102233937.2: *4* moveLast
    def moveLast(self):
        """Move the plugin to the last"""
        item = self.getSelection()
        if item:
            self.enabler.actives.moveLast(item.name)
            self.initList()
            self.items.setvalue([item.nicename])
    #@+node:pap.20051103002306: *4* onClick
    def onClick(self):
        """Clicked on an item in the order view"""
        item = self.getSelection()
        if item:
            self.plugin_view.showPlugin(item)    
    #@+node:pap.20051103001707: *4* save
    def save(self):
        """Save the current order"""
        self.enabler.storeOrder()
    #@+node:pap.20051103002808: *4* getSelection
    def getSelection(self):
        """Return the selected plugin"""
        sels = self.items.getcurselection()
        if len(sels) == 0:
            return None
        else:
            return self.local_dict[sels[0]]

    #@-others
#@+node:pap.20041009013256: *3* class LocalPluginList
class LocalPluginList(PluginList):
    """A list showing plugins based on the local file system"""

    title = "Locally Installed %ss"
    filter_options = ['All', 'On', 'Off']
#@+node:pap.20041009013556: *3* class RemotePluginList
class RemotePluginList(PluginList):
    """A list showing plugins based on a remote file system"""

    title = "%ss on CVS"
    filter_options = ['All', 'Up to date', 'Update available', 'Changed', 'Not installed']
#@+node:pap.20041006215108: *3* class ManagerDialog
class ManagerDialog:
    """The dialog to show manager functions"""

    dialog_caption = "Plugin Manager"
    file_text = "Plugin"
    has_enable_buttons = True 
    has_conflict_buttons = True
    install_text = "Install"   
    #@+others
    #@+node:pap.20041006215108.1: *4* ManagerDialog._init__
    def __init__(self,c,show_order=False):
        """Initialise the dialog"""

        self.c = c # New in version 0.20 of this plugin.

        # This would be wrong: it would inhibit standalone operation!
        # if not c or not c.exists: return
        self.setPaths()
        #@+<< create top level window >>
        #@+node:ekr.20041010110321: *5* << create top level window >> ManagerDialog
        root = g.app.root

        if standalone:
            # Use the hidden root.
            self.top = top = root
        else:
            # Create a new toplevel.
            self.top = top = Tk.Toplevel(root)

        g.app.gui.attachLeoIcon(top)
        top.title(self.dialog_caption)
        #@-<< create top level window >>
        self.initLocalCollection()
        #@+<< create frames >>
        #@+node:ekr.20041010110321.1: *5* << create frames >>
        self.frame = frame = Tk.Frame(top)
        frame.pack(side="top", fill='both', expand=1, padx=5, pady=5)   

        self.upper = Tk.Frame(frame)
        self.upper.pack(side="top", fill='both', expand=1, padx=5, pady=5)

        self.lower = Tk.Frame(frame)
        self.lower.pack(side="top", fill='x', expand=0, padx=5)
        #@-<< create frames >>
        #@+<< create pluginView >>
        #@+node:pap.20041006223915.1: *5* << create pluginView >>
        self.plugin_view = PluginView(self.upper, self.file_text)

        self.plugin_view.pack(side="right", fill='both', expand=1, padx=5, pady=5)
        #@-<< create pluginView >>
        #@+<< create PluginList >>
        #@+node:pap.20041006223915: *5* << create PluginList >>
        self.notebook = notebook = Pmw.NoteBook(self.upper, raisecommand=self.selectPage)
        notebook.pack(side="left", fill='both', expand=1, padx=5, pady=5)

        self.local_list_page = local_list_page = notebook.add('Installed %ss' % self.file_text)
        self.remote_list_page = remote_list_page = notebook.add('CVS %ss' % self.file_text)
        notebook.tab('Installed %ss' % self.file_text).focus_set()
        #notebook.setnaturalsize()

        self.plugin_list = LocalPluginList(local_list_page, self.plugin_view, self.local, 
                                           self.file_text)
        self.plugin_list.pack(side="top", fill='both', expand=1)
        self.remote_plugin_list = RemotePluginList(remote_list_page, self.plugin_view, None,
                                                   self.file_text)
        self.remote_plugin_list.pack(side="top", fill='both', expand=1)

        self.plugin_list.setSecondFilterList(["All"] + self.local.getGroups())
        #@-<< create PluginList >>
        if show_order:
            #@+<< create order >>
            #@+node:pap.20051102225718: *5* << create order >>
            self.order_view_page = order_view_page = notebook.add('%s Load Order' % self.file_text)

            self.order_view = order_view = LoadOrderView(order_view_page, self.file_text, self.local, self.enable, self.plugin_view)
            order_view.pack(side="top", fill='both', expand=1)
            #@-<< create order >>
        #@+<< create local buttons >>
        #@+node:pap.20041006223915.2: *5* << create local buttons >>
        self.buttonBox = Pmw.ButtonBox(
            self.local_list_page,
            labelpos = 'nw',
            frame_borderwidth = 2,
            frame_relief = 'groove')

        # Add some buttons to the ButtonBox.
        if self.has_enable_buttons:
            self.buttonBox.add('Enable', command = self.enablePlugin)
            self.buttonBox.add('Disable', command = self.disablePlugin)
            #self.buttonBox.add('Check for Updates', command = self.checkUpdates)
        if self.has_conflict_buttons:
            self.buttonBox.add('Check Conflicts', command = self.checkConflicts)

        self.buttonBox.pack(side="top", padx=5)
        #@-<< create local buttons >>
        #@+<< create remote buttons >>
        #@+node:pap.20041009020000: *5* << create remote buttons >>
        self.buttonBox = Pmw.ButtonBox(
            self.remote_list_page,
            labelpos = 'nw',
            frame_borderwidth = 2,
            frame_relief = 'groove')

        # Add some buttons to the ButtonBox.
        self.buttonBox.add(self.install_text, command = self.installPlugin)
        self.buttonBox.add('View', command = self.viewPlugin)
        self.buttonBox.add('Check for Updates', command = self.checkUpdates)

        self.buttonBox.pack(side="top", padx=5)
        #@-<< create remote buttons >>
        #@+<< create message bar >>
        #@+node:pap.20041006224808: *5* << create message bar >>
        self.messagebar = Pmw.MessageBar(self.lower,
                entry_width = 40,
                entry_relief='groove',
                labelpos = 'w',
                label_text = 'Status:')

        self.messagebar.pack(side="left", fill='x', expand=1, padx=5, pady=1)


        self.donebutton = Tk.Button(self.lower, text="Close", 
                                    command=lambda : self.top.destroy())
        self.donebutton.pack(side="right", fill="none", expand=0)


        #@-<< create message bar >>
        self.plugin_list.populateList("All")

        if not standalone:
            top.grab_set() # Make the dialog a modal dialog.
            top.focus_force() # Get all keystrokes.
            root.wait_window(top)
        else:
            root.mainloop()
    #@+node:pap.20041006224151: *4* enablePlugin
    def enablePlugin(self):
        """Enable a plugin"""
        plugin = self.plugin_list.getSelectedPlugin()
        if not plugin: return

        self.local.enablePlugin(plugin,self.enable)
        self.plugin_list.populateList()
    #@+node:ekr.20050329080427: *4* setPaths
    def setPaths(self):
        """Set paths to the plugin locations"""
        self.local_path = g.os_path_join(g.app.loadDir,"..","plugins")
        # self.remote_path = r"cvs.sourceforge.net/viewcvs.py/leo/leo/plugins"
        self.remote_path = r"cvs.sourceforge.net/viewcvs.py/leo/leo/plugins"


    #@+node:pap.20041006224206: *4* disablePlugin
    def disablePlugin(self):
        """Disable a plugin"""
        plugin = self.plugin_list.getSelectedPlugin()
        if not plugin: return

        self.local.disablePlugin(plugin,self.enable)
        self.plugin_list.populateList()
    #@+node:pap.20041006221212: *4* initLocalCollection
    def initLocalCollection(self):
        """Initialize the local plugin collection"""

        # Get the local plugins information
        self.local = LocalPluginCollection(self.c)
        self.local.initFrom(self.local_path)

        # Get the active status of the plugins
        self.enable = EnableManager()
        self.enable.initFrom(self.local_path)
        self.local.setEnabledStateFrom(self.enable)
    #@+node:pap.20041006224216: *4* checkUpdates
    def checkUpdates(self):
        """Check for updates"""
        url = self.remote_path
        self.status_message = "Searching for file list"
        self.messagebar.message("busy", "Searching for file list")
        #@+<< define callbackPrint >>
        #@+node:ekr.20041010111700.1: *5* << define callbackPrint >>
        def callbackPrint(text):
            """A callback to send status information"""
            self.remote_plugin_list.populateList() 
            self.messagebar.message("busy", text)
            self.top.update()
        #@-<< define callbackPrint >>
        self.remote = CVSPluginCollection()
        self.remote_plugin_list.plugins = self.remote
        try: 
            errors = self.remote.initFrom(url,callbackPrint)    
        except Exception as err:
            #@+<< put up a  connection failed dialog >>
            #@+node:pap.20041009163613: *5* << put up a connection failed dialog >>
            dialog = Pmw.MessageDialog(self.top,
                title = 'CVS Error',
                defaultbutton = 0,
                message_text = 'Error retrieving CVS file information: %s' % err)
            dialog.iconname('CVS')      
            dialog.activate()
            #@-<< put up a  connection failed dialog >>
        else:
            if errors:
                #@+<< put up a file error dialog >>
                #@+node:pap.20041009163613.1: *5* << put up a file error dialog >>
                dialog = ListReportDialog('CVS File Errors',
                                          'Errors',
                                          ["%s - %s" % item for item in errors],
                                          500)

                #@-<< put up a file error dialog >>
        self.messagebar.resetmessages('busy')        
        self.remote.setEnabledStateFrom(self.local)
        self.remote_plugin_list.populateList()   
        self.remote_plugin_list.setSecondFilterList(["All"] + self.remote.getGroups()) 
    #@+node:pap.20041009020000.1: *4* installPlugin
    def installPlugin(self):
        """Install the selected plugin"""

        # Write the file
        plugin = self.remote_plugin_list.getSelectedPlugin()        
        if not plugin: return

        self.messagebar.message("busy", "Writing file")
        plugin.writeTo(self.local_path)
        self.messagebar.message("busy", "Scanning local plugins") 
        # Go and check local filesystem for all plugins   
        self.initLocalCollection()
        # View is still pointing to the old list, so switch it now
        self.plugin_list.plugins = self.local
        self.plugin_list.populateList()
        plugin.enabled = "Up to date"
        # Update the current list too
        self.remote_plugin_list.populateList()
        self.messagebar.resetmessages('busy')
    #@+node:pap.20041009020000.2: *4* viewPlugin
    def viewPlugin(self):
        """View the selected plugin in a web browser"""
        plugin = self.remote_plugin_list.getSelectedPlugin()
        if plugin:
            webbrowser.open(plugin.getViewFilename())
    #@+node:pap.20051103001158: *4* selectPage
    def selectPage(self, pagename):
        """Select a page in the tab view"""
        if pagename == "%s Load Order" % self.file_text:
            self.order_view.initList()
    #@+node:pap.20041009025708: *4* checkConflicts
    def checkConflicts(self):
        """Check for plugin conflicts"""
        plugin = self.plugin_list.getSelectedPlugin() 
        if not plugin:
            return 
        conflicts = self.local.getConflicts(plugin)
        if not conflicts:
            dialog = Pmw.MessageDialog(self.top,
                title = 'No conflicts',
                defaultbutton = 0,
                message_text = 'There are no conflicts for %s.' % plugin.name)
            dialog.iconname('Conflicts')
            dialog.activate()
        else:
            dialog = ListReportDialog(
                'Potential Conflicts for %s' % plugin.name,
                'Conflicts',
                [inColumns(item, [30]) for item in conflicts],
                400)
    #@-others
#@+node:pap.20041009233937: *3* class ListReportDialog
class ListReportDialog:
    """Shows a list of items to report to the user

    The list is a list of strings. It is assumed that the
    strings are of the format 'abc - xyz' and this control
    presents a filter list based on the list of distinct 
    values for abc.

    """

    #@+others
    #@+node:pap.20041009233937.1: *4* ListReportDialog.__init__
    def __init__(self, title, name, list_data, width=300):
        """Initialize the dialog"""

        #@+<< create the top level frames >>
        #@+node:ekr.20041010111700: *5* << create the top level frames >>
        root = g.app.root
        self.top = top = Tk.Toplevel(root)
        g.app.gui.attachLeoIcon(self.top)
        top.title(title)

        self.frame = frame = Tk.Frame(top)
        frame.pack(side="top", fill='both', expand=1, padx=5, pady=5)
        #@-<< create the top level frames >>
        filter_options = self.getFilterOptions(list_data)
        self.list_data = list_data
        self.list_data.sort()
        #@+<< create the ScrolledListBox >>
        #@+node:pap.20041009234256: *5* << create the ScrolledListBox >>
        self.box = Pmw.ScrolledListBox(frame,
                labelpos='nw',
                label_text=name,
                listbox_height = 6,
                usehullsize = 1,
                hull_width = width,
                hull_height = 200,
                items = list_data,
        )

        self.box.pack(side="bottom", fill='both', expand=1)    

        self.box.component("listbox").configure(font=("Courier", 10))
        #@-<< create the ScrolledListBox >>
        #@+<< create the OptionMenu >>
        #@+node:pap.20041009234256.1: *5* << create the OptionMenu >>
        self.filter = Pmw.OptionMenu(frame,
                labelpos = 'w',
                label_text = 'Filter:',
                items = filter_options,
                menubutton_width = 16,
                command=self.populateList,
        )    

        self.filter.pack(side="top")
        #@-<< create the OptionMenu >>

        top.grab_set() # Make the dialog a modal dialog.
        top.focus_force() # Get all keystrokes.
        root.wait_window(top)
    #@+node:pap.20041009234850: *4* getFilterOptions
    def getFilterOptions(self, list_data):
        """Return a list of filter items"""
        splitter = re.compile("\s{3,}")
        names = set()
        for item in list_data:
            names.add(splitter.split(item)[1].strip())
        name_list = list(names)
        name_list.sort()
        return ["All"] + name_list
    #@+node:pap.20041009235457: *4* populateList
    def populateList(self, filter):
        """Populate the list"""

        # Get old selection so that we can restore it    
        current_text = self.box.getcurselection()
        if current_text:
            current_index = self.list_data.index(current_text[0])

        listitems = [item for item in self.list_data
            if item.endswith("   %s" % filter) or filter == "All"]

        self.box.setlist(listitems)    

        if current_text:
            try:
                self.box.setvalue((listitems[current_index],))
                self.box.component("listbox").see(current_index)
            except IndexError:
                pass # Sometimes the list is just different!
    #@-others
#@+node:pap.20041009140132.1: ** Implementation
#@+node:pap.20051103001707.1: *3* class OrderedDict
class OrderedDict(list):
    """A dictionary that retains its order

    This is implemented as a list of (key, value) pairs
    and so is not suitable for large numbers of items.

    """

    #@+others
    #@+node:pap.20051103002042: *4* __init__
    def __init__(self, items=None):
        """Initialise"""
        if items is None:
            items = []
        self.items = items
    #@+node:pap.20051103001707.3: *4* __getitem__
    def __getitem__(self, name):
        """Return an item"""
        for key, value in self.items:
            if key == name:
                return value
        else:
            raise KeyError("Item '%s' not found" % name)
    #@+node:pap.20051104224633: *4* __setitem__
    def __setitem__(self, name, value):
        """Set an item"""
        self.items.append((name, value))
    #@+node:pap.20051103001922: *4* __iter__
    def __iter__(self):
        """Iterate over keys"""
        return iter(self.keys())
    #@+node:pap.20051103004807: *4* __contains__
    def __contains__(self, name):
        """Check for item inside"""
        try:
            dummy = self[name]
            return True
        except KeyError:
            return False
    #@+node:pap.20051104224544: *4* get
    def get(self, key, default=None):
        """Return the value"""
        try:
            self[key]
        except KeyError:
            return default
    #@+node:pap.20051103001743: *4* keys
    def keys(self):
        """Return the keys"""
        return [key for key, value in self.items]
    #@+node:pap.20051104221348: *4* values
    def values(self):
        """Return the values"""
        return [value for key, value in self.items]
    #@+node:pap.20051103003310: *4* moveFirst
    def moveFirst(self, name):
        """Move the named item to the front"""
        item = name, self[name]
        self.items.remove(item)
        self.items.insert(0, item)
    #@+node:pap.20051103004312: *4* moveUp
    def moveUp(self, name):
        """Move the named item up"""
        item = name, self[name]
        pos = self.items.index(item)
        if pos <> 0:
            self.items[pos], self.items[pos-1] = self.items[pos-1], self.items[pos]
    #@+node:pap.20051103004312.1: *4* moveDown
    def moveDown(self, name):
        """Move an item down in the list"""
        item = name, self[name]
        pos = self.items.index(item)
        if pos <> len(self.items)-1:
            self.items[pos], self.items[pos+1] = self.items[pos+1], self.items[pos]    
    #@+node:pap.20051103003447: *4* moveLast
    def moveLast(self, name):
        """Move the named item to the back"""
        item = name, self[name]
        self.items.remove(item)
        self.items.append(item)
    #@-others
#@+node:pap.20041006184225.6: *3* class Plugin
class Plugin:   
    """Represents a single plugin instance"""

    # Class properties.
    max_name_width = 30
    max_group_width = 10

    read_details_immediately = False

    #@+others
    #@+node:pap.20041006185727.1: *4* __init__
    def __init__(self):
        """Initialize the plugin"""
        self.filename = None
        self.name = None
        self.is_plugin = True # until proven False! speeds initial loading
        self.version = 'Unknown'
        self.description = ''
        self.handlers = []
        self.commands = []
        self.has_config = False
        self.can_read = False
        self.hash = None
        self.enabled = "Unknown"
        self.priority = None
        self.has_toplevel = False
        self.requires = []
        self.group = 'Unknown'
        self.versions = 'Unknown'
        self.contents_valid = False
        self.has_details = False
    #@+node:pap.20041006193013: *4* initFrom
    def initFrom(self, location):
        """Initialize the plugin from the specified location"""

        # Initial properties
        self.filename = location
        self.name = self.getName(location)
        self.nicename = self.getNiceName(self.name)

        # Get the contents of the file
        try:
            text = self.getContents()
            self.getSummary(text)
        except InvalidPlugin as err:
            g.pr('InvalidPlugin',str(err))
            self.description = str(err)
        except:
            g.es('Unexpected exception in initFrom')
            g.es_exception()
    #@+node:ekr.20041113095851: *4* Must be overridden in subclasses...
    #@+node:pap.20041006212105: *5* getName
    def getName(self, location):

        """Determine the plugin name from the location"""

        raise NotImplementedError("Must Override")
    #@+node:pap.20041006193239: *5* getContents
    def getContents(self):

        """Return the contents of the file"""

        raise NotImplementedError("Must override")    
    #@+node:pap.20050317183038: *4* getNiceName
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
    #@+node:pap.20051001230822: *4* getSummary
    def getSummary(self, text):
        """Get a summary of this plugin

        This is a quick method to get an overview of whether this 
        really is a plugin and some key information. The longer,
        more time consuming search is performed by the getDetails
        method.

        """
        self.is_plugin = not self.hasPattern(text, '__not_a_plugin__\s*=\s*True(?!")')
        self.version = self.getPattern(text, r'__version__\s*=\s*[\'"](.*?)[\'"]', "-")
        self.group = self.getPattern(text, r'__plugin_group__\s*=\s*[\'"](.*?)[\'"]', "-")
        self._plugin_text = text

        # Some plugins need to have their details read immediately
        if self.read_details_immediately:
            self.ensureDetails()
    #@+node:pap.20041006194759: *4* getDetails
    def getDetails(self):
        """Get the details of the plugin

        We look for
            __version__
            hooks
            config
            commands
        """
        self.has_details = True
        text = self._plugin_text
        # Allow both single and double triple-quoted strings.
        match1 = self.getMatch(text, r'"""(.*?)"""')
        match2 = self.getMatch(text, r"'''(.*?)'''")
        pat1 = match1 and match1.group(1)
        pat2 = match2 and match2.group(1)
        if pat1 and pat2:
            # Take the first pattern that appears.
            self.description = g.choose(match1.start() < match2.start(),pat1,pat2)
        else:
            # Take whatever.
            self.description = pat1 or pat2 or 'Unknown'
        # g.trace('%4d %s' % (len(self.description),self.name))
        self.commands = set(self.getPatterns(text, "def cmd_(\w*?)\("))
        # Get a list of the handlers
        handler_list = self.getPattern(text, r'registerHandler\((.*?)\)')
        if handler_list:
            self.handlers = set(self.getPatterns(handler_list, r'["\'](.*?)["\']'))
        else:
            self.handlers = set()
        # Look for the matching .ini file.
        ini_file_name = g.os_path_join(
            g.app.loadDir,"..","plugins",
            self.getName(self.filename)+".ini")
        ini_file_name = g.os_path_abspath(ini_file_name)
        self.has_config = g.os_path_exists(ini_file_name)
        self.hash = sha.sha(text).hexdigest()
        self.can_read = True
        if USE_PRIORITY:
            self.priority = self.getPattern(text, r'__plugin_priority__\s*=\s*(.*?)$', "-")
        self.has_toplevel = self.hasPattern(text, "def topLevelMenu")
        self.getVersionHistory(text)
    #@+node:pap.20041006200000: *4* hasPattern
    def hasPattern(self, text, pattern):

        """Return True if the text contains the pattern"""

        return self.getPattern(text, pattern) is not None
    #@+node:pap.20041009230351: *4* hasImport
    def hasImport(self, text, module_name):

        """Return True if the text includes an import of the module"""
        if self.hasPattern(text, "import %s" % module_name):
            return True

        if self.hasPattern(text, "from %s import" % module_name):
            return True

        return False
    #@+node:ekr.20050121183012: *4* getMatch (new)
    def getMatch(self, text, pattern):

        """Return a single match for the specified pattern in the text"""

        return re.search(pattern,text,re.MULTILINE + re.DOTALL)
    #@+node:pap.20041006194759.1: *4* getPattern
    def getPattern(self, text, pattern, default=None):

        """Return a single match for the specified pattern in the text or the default"""

        matches = self.getPatterns(text, pattern)
        if matches:
            return matches[0]
        else:
            return default
    #@+node:pap.20041006194917: *4* getPatterns
    def getPatterns(self, text, pattern):

        """Return all matches of the pattern in the text"""

        exp = re.compile(pattern, re.MULTILINE + re.DOTALL)

        return exp.findall(text)
    #@+node:pap.20041006220611: *4* asString
    def asString(self, detail=False):

        """Return a string representation"""

        if not detail:
            if self.version <> "-":
                body = "%(nicename)s (v%(version)s)" % self.__dict__
            else:
                body = "%(nicename)s" % self.__dict__                        
            return inColumns((body, self.group, self.enabled), [self.max_name_width, self.max_group_width])
        else:
            return (
                "Name: %(nicename)s\n"
                "Version: %(version)s\n"
                "Active: %(enabled)s\n"
                "File: %(filename)s\n"
                "\n"
                "Description:\n%(description)s\n\n"
                "Has config file: %(has_config)s\n"
                "Commands: %(commands)s\n"
                "Handlers: %(handlers)s\n" % self.__dict__
            )
    #@+node:pap.20041009023004: *4* writeTo
    def writeTo(self, location):

        """Write this plugin to the file location"""

        # Don't write if contents are invalid
        if not self.contents_valid:
            return 

        filename = os.path.join(location, "%s.py" % self.name)
        try:
            f = file(filename, "w")
        except (IOError, OSError) as err:
            raise InvalidPlugin(
                "Unable to open plugin file '%s': %s" % (filename, err))
        try:
            try:
                f.write(self.text)
            finally:
                f.close()
        except Exception as err:
            raise InvalidPlugin(
                "Unable to write plugin file '%s': %s" % (filename, err))
    #@+node:pap.20051001232117: *4* ensureDetails
    def ensureDetails(self):
        """Ensure that the details have been read for this plugin

        The details are read asynchronously but we may need to make
        sure that they are available. This method will cause the
        details to be read now if they haven't already.

        """
        if not self.has_details:
            self.getDetails()
    #@+node:pap.20050305165333: *4* getVersionHistory
    def getVersionHistory(self, text):
        """Try to extract the version history of this plugin

        This is all guesswork! We look for a Leo node called "Version history"
        or one called "Change log". If we find it then we assume that the contents
        are the version history.

        This only works if the plugin was developed in Leo as a @thin file.

        """
        extractor =r'.*\+node\S+?\<\< %s \>\>.*?\#\@\+at(.*)\#\@\-at.*\-node.*?\<\< %s \>\>.*'
        #
        # This Re is very slow on large files so we truncate since we are really pretty
        # sure that version history will be within the first 150 lines
        lines = "\n".join(text.split("\n")[:150])
        for name in ("version history", "change log"):
            searcher = re.compile(extractor % (name, name), re.DOTALL+re.M)
            match = searcher.match(lines)
            if match:
                version_text = match.groups()[0]
                self.versions = version_text.replace("#", "")
                return
    #@+node:pap.20041009225149: *4* getRequiredModules
    def getRequiredModules(self, plugin_collection):
        """Determine which modules are also required by this plugin

        We check for,
         - importing Tk and PMW
         - other plugins which are imported (using plugin_collection)
         - a __plugin_requires__ definition

        """
        requires = []
        #@+<< Check UI toolkits >>
        #@+node:pap.20041009230050: *5* << Check UI toolkits >>
        # Check for UI toolkits
        if self.hasImport(self.text, "Tkinter"):
            requires.append("Tkinter")

        if self.hasImport(self.text, "Pmw"):
            requires.append("Pmw")
        #@-<< Check UI toolkits >>
        #@+<< Check other plugins >>
        #@+node:pap.20041009230652: *5* << Check other plugins >>
        # Check for importing other plugin files

        imports = self.getPatterns(self.text, "import (\w+)") + \
                  self.getPatterns(self.text, "from (\w+) import")

        for module_name in imports:
            if module_name in plugin_collection and module_name <> self.name:
                requires.append(module_name)
        #@-<< Check other plugins >>
        #@+<< Directives >>
        #@+node:pap.20041009230953: *5* << Directives >>
        # Look for __plugin_requires__ directive

        directive_text = self.getPattern(self.text, r'__plugin_requires__\s*=\s*(.*?)$', "[]")

        try:
            directive = eval(directive_text)
        except:
            g.es("__plugin_requires__ not understood for %s: '%s'" % (
                    self.name, directive_text))    
        else: 
            # if isinstance(directive, (str,unicode)):
            if g.isString(directive):
                requires.append(directive)
            else:
                requires.extend(directive)
        #@-<< Directives >>
        self.requires = set(requires)
    #@-others
#@+node:pap.20041006192557: *3* class LocalPlugin(Plugin)
class LocalPlugin(Plugin):
    """A plugin on the local file system"""

    #@+others
    #@+node:pap.20041006212131: *4* getName
    def getName(self, location):

        """Determine the plugin name from the location"""

        # return os.path.split(os.path.splitext(location)[0])[1]
        head,ext = g.os_path_splitext(location)
        path,name = g.os_path_split(head)
        return name
    #@+node:pap.20041006193459.1: *4* getContents
    def getContents(self):

        """Return the contents of the file"""

        self.contents_valid = False

        try:
            f = file(self.filename, "r")
        except (IOError, OSError) as err:
            s = "Unable to open plugin file '%s': %s" % (self.name, err)
            g.pr(s)
            raise InvalidPlugin(s)
        try:
            try:
                self.text = text = f.read()
            finally:
                f.close()
        except Exception as err:
            s = "Unable to read plugin file '%s': %s" % (self.name, err)
            g.pr(s)
            raise InvalidPlugin(s)              

        self.contents_valid = True

        return text


    #@-others
#@+node:pap.20041006203049: *3* class CVSPlugin
class CVSPlugin(Plugin):
     """A plugin on CVS"""

     read_details_immediately = True

     #@+others
     #@+node:pap.20041006212238: *4* getName
     def getName(self, location):

         """Determine the plugin name from the location"""

         return re.match("(.*)/(.*?)\.py\?", location).groups()[1]
     #@+node:pap.20041006213006: *4* getContents
     def getContents(self):

         """Return the contents of the file"""

         self.contents_valid = False

         # Connect to CVS
         try:
             url = urllib.urlopen(self.filename)
         except Exception as err:
             raise InvalidPlugin("Could not get connection to CVS: %s" % err)

         # Get the page with file content
         try:
             try:
                 self.text = text = url.read()
             finally:
                 url.close()
         except Exception as err:
             raise InvalidPlugin("Could not read file '%s' from CVS: %s" % (self.filename, err))

         self.contents_valid = True

         return text        
     #@+node:pap.20041009224435: *4* getViewFilename
     def getViewFilename(self):

         """Return the url to view the file"""

         return self.filename.replace(r"/*checkout*", "") + "&view=markup"
     #@-others
#@+node:pap.20041006190628: *3* class PluginCollection
class PluginCollection(dict):

    """Represents a collection of plugins"""

    plugin_class = None
    background_pause = 0.05 # seconds to pause while getting details

    #@+others
    #@+node:pap.20041006192257: *4* __init__
    def __init__(self):
        """Initialize the plugin collection"""
    #@+node:pap.20041006191239: *4* initFrom
    def initFrom(self, location, callback=None):
        """Initialize the collection from the filesystem location.
        Returns a list of errors that occured.
        """
        if callback: callback("Looking for list of files")
        errors = []
        plugin_files = self.getFilesMatching(location)  
        for plugin_file in plugin_files:
            if callback: callback("Processing %s" % plugin_file)    
            plugin = self.plugin_class()
            # Get details
            try:
                plugin.initFrom(plugin_file)
            except Exception as err:
                errors.append((plugin_file, err))
            # Store anything that looks like a plugin
            if plugin.is_plugin:
                self[plugin.name] = plugin

        # Now we have to go back through and check for dependencies
        # We cannot do this up front because we need to know the names
        # of other plugins to detect the dependencies
        for plugin in self.values():
            plugin.getRequiredModules(self)

        # Kick-off a thread to get detailed information on the plugin
        # This can be time consuming so we don't try to do this on
        # the main thread
        handler = threading.Thread(target=self.getPluginDetails)
        handler.start()

        return errors

    #@+node:pap.20051001231439: *4* getPluginDetails
    def getPluginDetails(self):
        """Get detailed information on all the plugins

        This can be time consuming and so is normally done on a 
        separate thread. We do a lot of pausing here also
        to ensure that we don't block other things going on.

        """
        for plugin in self.values():
            time.sleep(self.background_pause)
            plugin.ensureDetails()
    #@+node:pap.20041006191829: *4* getAllFiles
    def getAllFiles(self, location):

        """Return all the files in the location"""

        raise NotImplementedError("Must override")    
    #@+node:pap.20041006221438: *4* sortedNames
    def sortedNames(self):

        """Return a list of the plugin names sorted alphabetically

        We use decorate, sort, undecorate to sort by the nice name!

        """

        names = [(item.nicename, item.name) for item in self.values()]
        names.sort()
        return [name[1] for name in names]
    #@+node:pap.20041008220723: *4* setEnabledStateFrom
    def setEnabledStateFrom(self, enabler):

        """Set the enabled state of each plugin using the enabler object"""
        for name in self:
            if name in enabler.actives:
                self[name].enabled = "On"
            else:
                self[name].enabled = "Off" 
    #@+node:pap.20041008233947: *4* enablePlugin
    def enablePlugin(self, plugin, enabler):
        """Enable a plugin"""
        plugin.enabled = "On"
        enabler.updateState(plugin)
    #@+node:pap.20041008234033: *4* disablePlugin
    def disablePlugin(self, plugin, enabler):
        """Enable a plugin"""
        plugin.enabled = "Off"
        enabler.updateState(plugin)
    #@+node:pap.20041009025708.1: *4* getConflicts
    def getConflicts(self, plugin):

        """Find conflicting hook handlers for this plugin"""

        conflicts = []
        for this_plugin in self.values():
            # g.trace(plugin.handlers,this_plugin.handlers)
            if this_plugin.name <> plugin.name:
                for conflict in plugin.handlers.intersection(this_plugin.handlers):
                    conflicts.append((this_plugin.name, conflict))

        return conflicts
    #@+node:pap.20050305161126: *4* getGroups
    def getGroups(self):
        """Return a list of the Plugin group names"""
        groups = list(set([plugin.group for plugin in self.values()]))
        groups.sort()
        return groups
    #@-others
#@+node:pap.20041006190817: *3* class LocalPluginCollection
class LocalPluginCollection(PluginCollection):
    """Represents a plugin collection based on the local file system"""

    plugin_class = LocalPlugin

    #@+others
    #@+node:ekr.20060107092833.1: *4* ctor
    # New in version 0.20

    def __init__ (self,c):

        self.c = c
    #@+node:pap.20041006191803: *4* getFilesMatching
    def getFilesMatching(self, location):

        """Return all the files matching the pattern"""

        return [filename for filename in self.getAllFiles(location)
                    if fnmatch.fnmatch(filename, "*.py")]
    #@+node:pap.20041006191803.1: *4* getAllFiles
    def getAllFiles(self, location):

        """Return all the files in the location"""

        return [os.path.join(location, filename) for filename in os.listdir(location)]
    #@+node:pap.20051002002852: *4* enablePlugin
    def enablePlugin(self, plugin, enabler):
        """Enable the plugin

        This adds the plugin to the list of plugins which will be
        started the next time that Leo runs and also tries to
        dynamically start the plugin. This may fail if the plugin
        needed to do something when Leo was first kicking off.

        We only try the dynamic start if we are running inside of
        Leo (ie not standalone) and we were able to import
        the leoPlugins module.

        """

        super(LocalPluginCollection, self).enablePlugin(plugin, enabler)

        if not self.c:
            g.es("Can not enable plugins dynaically when running stand-alone",
                color="blue")
            return

        try:
            g.loadOnePlugin(plugin.name)
            #@+<< Hooks to send >>
            #@+node:pap.20051007193759: *5* << Hooks to send >>
            # These are the hooks to send to dynamically enabled plugins 
            # to persuade them to start

            hook_list = [
                    'start1',
                    'before-create-leo-frame',
                    'unselect1',
                    'unselect2',
                    'select1',
                    'scan-directives',
                    'init-color-markup',
                    'select2',
                    'select3',
                    'unselect1',
                    'unselect2',
                    'select1',
                    'scan-directives',
                    'init-color-markup',
                    'select2',
                    'select3',
                    'menu1',
                    'menu2',
                    'create-optional-menus',
                    'after-create-leo-frame',
                    'new',
                    'start2',
                    'idle',
                    'redraw-entire-outline',
                    'draw-sub-outline',
                    'draw-outline-node',
                    'draw-outline-icon',
                    'draw-outline-text-box',
                    'after-redraw-outline',
                    ]
            #@-<< Hooks to send >>
            #@+<< Send hooks >>
            #@+node:pap.20051002004135: *5* << Send hooks >>
            # In order to simulate the startup process we need
            # to send a series of hooks to the plugin

            keys = {'c':self.c, 'new_c':self.c}

            for hook in hook_list:
                bunch = g.app.pluginsController.handlers.get(hook, [])
                for item in bunch:
                    if item.moduleName == plugin.name:
                        g.es("Sending '%s' to '%s'" % (hook, plugin.name), color="green")
                        item.fn(hook,keys)
            #@-<< Send hooks >>
            #@+<< Add plugin menu >>
            #@+node:pap.20051008005923: *5* << Add plugin menu >>
            # Add the menu item to the plugins menu
            import plugins_menu
            filename = plugins_menu.PluginDatabase.all_plugins[plugin.name]
            new_plugin = plugins_menu.PlugIn(filename)
            plugins_menu.addPluginMenuItem(new_plugin,self.c)
            #@-<< Add plugin menu >>
        except Exception as err:
            g.es("Failed to dynamically enable '%s': %s" % (plugin.name, err),
                 color="red")
        else:
            g.es("Dynamically enabled '%s'" % plugin.name, color="blue")
    #@-others
#@+node:pap.20041006201849: *3* class CVSPluginCollection
class CVSPluginCollection(PluginCollection):

    """Represents a plugin collection based located in a CVS repository"""

    plugin_class = CVSPlugin

    #@+others
    #@+node:pap.20041006202102: *4* getFilesMatching
    def getFilesMatching(self, location):
        """Return all the files in the location"""
        #
        # Find files
        text = self.getListingPage(location)
        cvs_host, _, cvs_location = location.split("/", 2)
        filename = re.compile(r'href="/viewcvs.py/(%s)/(.*?\.py\?rev=.*?)\&view=auto"' % cvs_location)
        return [r"http://%s/viewcvs.py/*checkout*/%s/%s" % (cvs_host, item[0], item[1])
                    for item in filename.findall(text)]
    #@+node:pap.20041006202703: *4* getListingPage
    def getListingPage(self, location):
        """Return the HTML page with files listed"""
        #
        # Connect to CVS
        try:
            url = urllib.urlopen(r"http://%s" % location)
        except Exception as err:
            raise InvalidCollection("Could not get connection to CVS: %s" % err)
        #
        # Get the page with files listed
        try:
            try:
                text = url.read()
            finally:
                url.close()
        except Exception as  err:
            raise InvalidCollection("Could not read from CVS: %s" % err)
        return text    
    #@+node:pap.20041009021201: *4* setEnabledStateFrom
    def setEnabledStateFrom(self, collection):
        """Set the enabled state based on another collection"""
        for plugin in self.values():
            try:
                local_version = collection[plugin.name]
            except KeyError:
                plugin.enabled = "Not installed"
            else:
                if local_version.version < plugin.version:
                    plugin.enabled = "Update available"
                elif local_version.hash <> plugin.hash:
                    plugin.enabled = "Changed"
                else:
                    plugin.enabled = "Up to date"
    #@-others
#@+node:pap.20041006232717: *3* class EnableManager
class EnableManager:

    """Manages the enabled/disabled status of plugins"""

    #@+others
    #@+node:pap.20041006232717.1: *4* initFrom
    def initFrom(self, location):
        """Initialize the manager from a folder"""
        manager_filename = os.path.join(location, "pluginsManager.txt")
        self.location = location

        # Get the text of the plugin manager file
        try:
            f = file(manager_filename, "r")
        except (IOError, OSError) as err:
            raise InvalidManager("Unable to open plugin manager file '%s': %s" % 
                                    (manager_filename, err))
        try:
            try:
                self.text = text = f.read()
            finally:
                f.close()
        except Exception as err:
            raise InvalidManager("Unable to read manager file '%s': %s" % 
                                    (manager_filename, err))              
        self.parseManagerText(text)
    #@+node:pap.20041009003552: *4* writeFile
    def writeFile(self, location):
        """Initialize the manager from a folder"""
        manager_filename = os.path.join(location, "pluginsManager.txt")

        # Get the text of the plugin manager file
        try:
            f = file(manager_filename, "w")
        except (IOError, OSError) as err:
            raise InvalidManager("Unable to open plugin manager file '%s': %s" % 
                                    (manager_filename, err))
        try:
            try:
                f.write(self.text)
            finally:
                f.close()
        except Exception as err:
            raise InvalidManager("Unable to write manager file '%s': %s" % 
                                    (manager_filename, err))              
        self.parseManagerText(self.text)
    #@+node:pap.20041008200028: *4* parseManagerText
    def parseManagerText(self, text):
        """Parse the text in the manager file"""

        # Regular expressions for scanning the file
        find_active = re.compile(r"^\s*?(\w+)\.py", re.MULTILINE)
        find_inactive = re.compile(r"^\s*?#\s*(\w+)\.py", re.MULTILINE)
        find_manager = re.compile(r"^\s*plugin_manager\.py", re.MULTILINE)

        if 1: # Put the first match in the starts dict.
            starts = OrderedDict()
            for kind,iter in (
                ('on',find_active.finditer(text)),
                ('off',find_inactive.finditer(text)),
            ):
                for match in iter:
                    name = match.groups()[0]
                    start = match.start()
                    if start != -1:
                        bunch = starts.get(name)
                        if not bunch or bunch.start > start:
                          starts[name] = g.Bunch(
                            kind=kind,name=name,start=start,match=match)

            self.actives = OrderedDict(
                [(bunch.name,bunch.match) for bunch in starts.values() if bunch.kind=='on'])

            self.inactives = OrderedDict(
                [(bunch.name,bunch.match) for bunch in starts.values() if bunch.kind=='off'])

            if 0: # debugging.
                starts2 = [(bunch.start,bunch.name,bunch.kind) for bunch in starts.values()]
                starts2.sort()
                g.trace(g.listToString(starts2,tag='starts2 list'))
                g.trace(g.dictToString(self.actives,tag='Active Plugins'))

        else: # Original code.
            # Get active plugin defintions
            self.actives = dict([(match.groups()[0], match) 
                for match in find_active.finditer(text)])

            # Get inactive plugin definitions
            self.inactives = dict([(match.groups()[0], match) 
                for match in find_inactive.finditer(text)])

        # List of all plugins
        self.all = {}
        self.all.update(self.actives)
        self.all.update(self.inactives)

        # Locaction of the plugin_manager.py plugin - this is where
        # we add additional files
        self.manager = find_manager.search(text)
    #@+node:pap.20041008234256: *4* updateState
    def updateState(self, plugin):
        """Update the state for the given plugin"""
        self._updateItemState(plugin.name, plugin.enabled)
    #@+node:pap.20051104222141: *4* _updateItemState
    def _updateItemState(self, name, state):
        """Update the state of an item"""
        # Get the filename for the new entry
        if state == "On":
            newentry = "%s.py" % name
        else:
            newentry = "#%s.py" % name 

        if name in self.all:
            # Plugin exists in the management file
            item = self.all[name]
            # TODO: Unicode issues with the following line??
            self.text = "%s%s%s" % (
                self.text[:item.start()],
                str(newentry),
                self.text[item.end():])      
        else:
            # Plugin doesn't exist - add it at a suitale place
            self.text = "%s%s\n%s" % (
                self.text[:self.manager.start()],
                str(newentry),
                self.text[self.manager.start():])

        self.writeFile(self.location)    
    #@+node:pap.20051104220845: *4* storeOrder
    def storeOrder(self):
        """Store the load order of plugins

        Order is stored by putting a section in the file delimited by
            # Load Order
            plugin1
            plugin2
            plugin3
            # Load Order

        We disable all plugins and insert them in the new section.
        We check to see if a load order exists and create it if not. 

        """
        #
        # Disable all active plugins
        active_plugins = self.actives.keys()
        for name in active_plugins:
            self._updateItemState(name, False)
        #
        # Look for an existing section and chop it out
        existing_parts = self.text.split("# Load Order")
        if len(existing_parts) == 3:
            self.text = "%s\n%s" % (existing_parts[0], existing_parts[2])
        #
        # Now add the section in at the end
        self.text = "# Load Order\n%s\n# Load Order%s" % (
                    "\n".join([("%s.py" % name) for name in active_plugins]),
                    self.text.strip())
        #
        # And store the new version
        self.writeFile(self.location)
        #
        # The active plugins will have been set to enabled by the writeFile
        # operation so we are now good to go again!
    #@-others
#@-others

if __name__ == "__main__":
    if ok:
        g.createStandAloneTkApp(pluginName=__name__)
        topLevelMenu(c=None)
#@-leo

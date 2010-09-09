#@+leo-ver=5-thin
#@+node:ekr.20060703162506: * @thin keybindings.py
#@+<< docstring >>
#@+node:pap.20060703102546.1: ** << docstring >>
"""KeyBindings - shows what key bindings are in effect.

The plugin allows you to explore the current bindings
and search for particular keys or bindings. You can also
see what commands are available but not bound currently.

The plugin includes a "Print" function to print out
a subset of the bindings so that you can create a handy
reference chart.

At a future time it might even allow editing!

"""
#@-<< docstring >>

__version__ = '0.2'
__plugin_name__ = "KeyBindings"
__plugin_priority__ = 1
__plugin_requires__ = ["plugin_menu"]
__plugin_group__ = "Helpers"


#@+<< version history >>
#@+node:pap.20060703102546.2: ** << version history >>
#@@killcolor
#@+at
# 
# Version 0.1 - (Paul Paterson) First created
# v 0.2 EKR: Use g.app.loadDir as a stable starting point for computing plugins directory.
#@-<< version history >>

#@+<< imports >>
#@+node:pap.20060703102546.3: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoEditCommands as leoEditCommands

Pmw = g.importExtension('Pmw',    pluginName=__name__,verbose=True,required=True)
Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

# Whatever other imports your plugins uses.
import fnmatch
import os
import webbrowser
#@-<< imports >>

thePluginController = None

#@+others
#@+node:pap.20060703102546.4: ** init
def init ():

    ok = Pmw and Tk

    if ok:
        if g.app.gui is None:
            g.app.createTkGui(__file__)

        ok = g.app.gui.guiName() == "tkinter"

        if ok:
            if 1: # Use this if you want to create the commander class before the frame is fully created.
                g.app.pluginsController.registerHandler('before-create-leo-frame',onCreate)
            else: # Use this if you want to create the commander class after the frame is fully created.
                g.app.pluginsController.registerHandler('after-create-leo-frame',onCreate)
            g.plugin_signon(__name__)

    return ok
#@+node:pap.20060703102546.5: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    global thePluginController
    thePluginController = pluginController(c)

#@+node:pap.20060703102832: ** topLevelMenu
# This is called from plugins_menu plugin.

def topLevelMenu(c):   
    """Show all key bindgins"""
    thePluginController.onClick()
#@+node:pap.20060703104701: ** inColumns
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
#@+node:pap.20060703103820: ** class KeyHandlerDialog
class KeyHandlerDialog:
    """The dialog to show the key handlers"""

    #@+others
    #@+node:pap.20060703103942: *3* __init__
    def __init__ (self,c):

        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.

        #@+<< Main window >>
        #@+node:pap.20060703130408: *4* << Main window >>
        root = g.app.root
        top = Tk.Toplevel(root)

        self.root = root
        self.top = top

        g.app.gui.attachLeoIcon(top)
        top.title("Leo Key Bindings")
        #@-<< Main window >>

        self.filter_pane = "Bound only"
        self.filter_keys = "*"
        self.filter_commands = "*"
        self.sort_by = "By key"

        self.getAllCommands()    
        self.populateKeys()

        #@+<< Frames >>
        #@+node:pap.20060703105742: *4* << Frames >>
        self.upper = Pmw.Group(top,
            tag_text='Filtering',
        )
        self.upper.pack(side="top", fill='both', expand=0, padx=5, pady=5)
        upper = self.upper.interior()

        self.middle = middle = Tk.Frame(top)
        self.middle.pack(side="top", fill='both', expand=1, padx=5, pady=5)

        #@-<< Frames >>
        #@+<< Filtering >>
        #@+node:pap.20060703112856: *4* << Filtering >>
        self.pane = Pmw.OptionMenu(upper,
                labelpos = 'w',
                label_text = 'Pane:',
                items = self.pane_list,
                menubutton_width = 16,
                command=self.filterPane,
        )    
        self.pane.pack(side="left")

        self.keys = Pmw.EntryField(upper,
                labelpos = 'w',
                value = '',
                label_text = 'Key:',
                modifiedcommand = self.filterKey)
        self.keys.pack(side="left", padx=10)

        self.commands = Pmw.EntryField(upper,
                labelpos = 'w',
                value = '',
                label_text = 'Commands:',
                modifiedcommand = self.filterCommands)
        self.commands.pack(side="left", padx=10)

        self.sorting = Pmw.OptionMenu(upper,
                labelpos = 'w',
                label_text = 'Sort:',
                items = ['By key', 'By command', 'By pane'],
                menubutton_width = 16,
                command = self.sortItems)
        self.sorting.pack(side="left", padx=10)


        self.printable = Tk.Button(upper, 
                text = "Print", 
                width = 16,
                command = self.printKeys)
        self.printable.pack(side="right", fill="none", expand=0, padx=20)


        #@-<< Filtering >>
        #@+<< List >>
        #@+node:pap.20060703123943: *4* << List >>
        self.box = Pmw.ScrolledListBox(middle,
                labelpos='nw',
                label_text='Active key bindings:',
                listbox_height = 6,
                selectioncommand=self.onClick,
                usehullsize = 1,
                hull_width = 300,
                hull_height = 600,
        )
        #@-<< List >>

        self.box.setlist(self.bindings)    
        self.box.component("listbox").configure(font=("Courier", 8))
        self.box.pack(side="bottom", fill='both', expand=1)    

        #top.grab_set() # Make the dialog a modal dialog.
        #top.focus_force() # Get all keystrokes.
        #root.wait_window(top)
    #@+node:pap.20060703104556: *3* populateKeys
    def populateKeys(self):
        """Populate the list of keys"""
        dct = self.c.keyHandler.masterBindingsDict
        bindings = []
        self.pane_list = ["Bound only", "Unbound only", "Show all", "---"] + dct.keys()
        #
        match = fnmatch.fnmatch
        #
        for pane in dct:
            if self.filter_pane in ("Show all", "Bound only", pane):
                for binding in dct[pane].values():
                    if match(binding.stroke, self.filter_keys) and match(binding.commandName, self.filter_commands):
                        bindings.append([
                            inColumns(
                                (binding.pane, binding.stroke, binding.commandName),
                                (10, 25)),
                            binding.stroke,
                            binding.commandName,
                            binding.pane,
                        ])

        if self.filter_pane in ("Show all", "Unbound only"):
            self.addUnboundCommands(bindings)

        sorter = {
            "By key" : lambda item1, item2 : cmp(item1[1], item2[1]),
            "By command" : lambda item1, item2 : cmp(item1[2], item2[2]),
            "By pane" : lambda item1, item2 : cmp(item1[3], item2[3]),
    }

        bindings.sort(sorter[self.sort_by])
        self.full_bindings = bindings

        self.bindings = [item[0] for item in bindings] 
    #@+node:pap.20060703104111: *3* onClick
    def onClick(self):
        """The menu item was clicked"""
        #import pdb; pdb.set_trace()
    #@+node:pap.20060703105742.1: *3* filterPane
    def filterPane(self, filter="Show all"):
        """Filter the list on panes"""
        self.filter_pane = filter
        self.populateKeys()
        self.box.setlist(self.bindings)
    #@+node:pap.20060703111744: *3* filterKey
    def filterKey(self):
        """Filter the list on the keystroke"""
        self.filter_keys = "*%s*" % self.keys.getvalue()
        self.populateKeys()
        self.box.setlist(self.bindings)
    #@+node:pap.20060703112417: *3* filterCommands
    def filterCommands(self):
        """Filter the list on the command"""
        self.filter_commands = "*%s*" % self.commands.getvalue()
        self.populateKeys()
        self.box.setlist(self.bindings)
    #@+node:pap.20060703113646: *3* sortItems
    def sortItems(self, sort="By key"):
        """Sort the items"""
        self.sort_by = sort
        self.populateKeys()
        self.box.setlist(self.bindings)
    #@+node:pap.20060703123659: *3* printKeys
    def printKeys(self):
        """Print the keys"""
        fname = os.path.abspath(g.os_path_join(g.app.loadDir,"..", "plugins", "keyreport.html"))
        f = file(fname, "w")
        report = ["<html><title>Leo Key Bindings</title><body>"
                  '<link type="text/css" rel="stylesheet" href="keys.css" />',
                  "<table>",
                    "<tr><th colspan=2>Report</th></tr>"
                    "<tr><td>Pane</td><td>%(filter_pane)s</td></tr>"
                    "<tr><td>Key filter</td><td>%(filter_keys)s</td></tr>"
                    "<tr><td>Command filter</td><td>%(filter_commands)s</td></tr>"
                    "<tr><td>Sorted</td><td>%(sort_by)s</td></tr>" 
                  "</table>" % self.__dict__,
                  "<table>",
                    "<tr><th>Pane</th><th>Key</th><th>Command</th></tr>",
        ]

        for item in self.full_bindings:
            _, key, command, pane = item
            report.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (pane, key, command))

        report.append("</table>")

        f.write("\n".join(report))
        f.close()

        webbrowser.open(fname)
    #@+node:pap.20060703131850: *3* getAllCommands
    def getAllCommands(self):
        """Get a list of all the command that Leo understands"""
        classes = [item[1](self.c) for item in leoEditCommands.classesList]
        self.all_commands = []
        for cls in classes:
            cls.finishCreate()
            self.all_commands.extend(cls.getPublicCommands().keys())
    #@+node:pap.20060703132904: *3* addUnboundCommands
    def addUnboundCommands(self, bindings):
        """Add the unbound commands in there"""
        match = fnmatch.fnmatch
        for cmd in self.all_commands:
            if match(cmd, self.filter_commands):
                bindings.append([
                    inColumns(
                        ("unbound", "no key", cmd),
                        (10, 25)),
                    "no key",
                    cmd,
                    "unbound",
                ])
    #@-others
#@+node:pap.20060703102546.6: ** class pluginController
class pluginController:

    #@+others
    #@+node:pap.20060703102546.7: *3* __init__
    def __init__ (self,c):

        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.


    #@+node:pap.20060703103603: *3* onClick
    def onClick(self):
        """The menu item was clicked"""
        dialog = KeyHandlerDialog(self.c)
    #@-others
#@-others
#@-leo

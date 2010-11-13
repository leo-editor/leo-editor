#@+leo-ver=5-thin
#@+node:pap.20050605183206: * @file leoupdate.py
#@+<< docstring >>
#@+node:pap.20050605183206.1: ** << docstring >>
""" Automatically updates Leo from the current CVS version
of the code stored on the SourceForge site. You can view individual
files and update your entire Leo installation directly without needing
a CVS client.

"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.3"
__plugin_name__ = "Leo Update"
__plugin_priority__ = 100
__plugin_group__ = "Core"
__plugin_requires__ = ["plugin_manager"]

#@+<< imports >>
#@+node:pap.20050605183206.2: ** << imports >>
import leo.core.leoGlobals as g

import re
import sys
import glob

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@-<< imports >>

#@+<< version history >>
#@+node:pap.20050605183206.3: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Paul Paterson: Initial version.
# 0.2 EKR: Added c arg to topLevelMenu.
# 0.2 EKR:
# - Fixed crasher related to new c arg.
# - Replaced SourceForge urls with tigris urls, but these do not work.
# 
#@-<< version history >>
#@+<< todo >>
#@+node:pap.20050605183206.4: ** << todo >>
"""

Todo list:

- allow individual update
- specific versions?

Done:

- scan CVS for files
- allow block update

"""
#@-<< todo >>

#@+others
#@+node:pap.20050605183206.5: ** Error Classes
class LeoUpdateError(Exception):
    """Something went wrong with the update"""

#@+node:pap.20050605183206.6: ** init
def init():

    ok = Tk and g.app.gui.guiName() == "tkinter"

    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)
    else:
        g.es("autotrees requires Tkinter",color='blue')

    return ok
#@+node:pap.20050605183206.7: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    global thePluginController
    thePluginController = LeoUpdater(c)
#@+node:pap.20050605183206.8: ** topLevelMenu
# This is called from plugins_menu plugin.

def topLevelMenu(c):   
    """Manage the tree handlers"""
    global thePluginController    
    thePluginController.showManagerDialog(c)
#@+node:pap.20050605183206.17: ** class LeoUpdater
class LeoUpdater:

    #@+others
    #@+node:pap.20050605183206.18: *3* __init__
    def __init__ (self,c):
        """Initialise the commander"""
        self.c = c
        # 
        # Get the manager
        try:
            self.plugin_manager = __import__("plugin_manager")
        except ImportError as err:
            g.es("LeoUpdate did not load plugin manager: %s" % (err,), color="red")
            self.plugin_manager = None
    #@+node:pap.20050605183206.27: *3* showManagerDialog
    def showManagerDialog(self,c):
        """Show the tree handler manager dialog"""
        if not self.plugin_manager:
            g.es("Plugin manager could not be loaded", color="red")
        else:
            #
            # The manager class is defined as a dynamic class because
            # we don't know if we will be able to import the 
            # base class!
            #@+<< class HandlerDialog >>
            #@+node:pap.20050605183206.28: *4* << class HandlerDialog >>
            class HandlerDialog(self.plugin_manager.ManagerDialog):
                """A dialog to manager leo files"""

                dialog_caption = "Leo File Manager"

                #@+others
                #@+node:pap.20050605184344: *5* initLocalCollection
                def initLocalCollection(self):
                    """Initialize the local file collection"""

                    # Get the local plugins information
                    self.local = plugin_manager.LocalPluginCollection(self.c)
                    self.local.initFrom(self.local_path)

                #@+node:pap.20050605183206.29: *5* setPaths
                def setPaths(self):
                    """Set paths to the plugin locations"""
                    self.local_path = g.os_path_join(g.app.loadDir,"..","src")
                    # self.remote_path = r"cvs.sourceforge.net/viewcvs.py/leo/leo/src"
                    self.remote_path = r'leo.tigris.org/source/browse/leo/src'
                    self.file_text = "File"
                    self.has_enable_buttons = False
                    self.has_conflict_buttons = False
                    self.install_text = "Install all"
                #@+node:pap.20050605192322.1: *5* installPlugin
                def installPlugin(self):
                    """Install all the files"""

                    # Write the files
                    for plugin in self.remote_plugin_list.getAllPlugins():     
                        self.messagebar.message("busy", "Writing file '%s'" % plugin.name)
                        plugin.writeTo(self.local_path)
                        plugin.enabled = "Up to date"

                    self.messagebar.message("busy", "Scanning local files") 
                    # Go and check local filesystem for all plugins   
                    self.initLocalCollection()
                    # View is still pointing to the old list, so switch it now
                    self.plugin_list.plugins = self.local
                    self.plugin_list.populateList()
                    # Update the current list too
                    self.remote_plugin_list.populateList()
                    self.messagebar.resetmessages('busy')

                #@-others
            #@-<< class HandlerDialog >>
            plugin_manager = self.plugin_manager
            dlg = HandlerDialog(c)    
    #@-others
#@-others

#@-leo

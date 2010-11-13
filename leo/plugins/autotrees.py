#@+leo-ver=5-thin
#@+node:ekr.20050329082101.115: * @file autotrees.py
#@+<< docstring >>
#@+node:ekr.20050329082101.116: ** << docstring >>
""" A helper plugin designed to make it easy to write
"handler" plugins to manage dynamic content in Leo outlines. AutoTrees provides:

- Convenient handler base classes which can be specialized for particular uses.

- A manager to turn handlers on and off.

- A set of example handlers to show the kinds of things that are possible.

AutoTrees doesn't do anything that you cannot do in other ways, but it does
provide a consistent way of adding dynamic content. This means that individual
plugin writers don't have to rewrite all the same kinds of code each time and
also makes it easier to maintain Leo, since it standardizes the way that certain
classes of plugin interact with the Leo core.

Why use this? I'm a plugin writer and I want to write a plugin to display
dynamic content, that is, content not directly contained in the .leo or derived
files, e.g.,

- email messages 
- news feeds
- news groups
- documentation
- remote files
- statistics
- file system data
- data base records

You can do this as a standard plugin, but as an AutoTrees handler you,

- don't need to write code that interacts with the tree (this is done for you)
- get centralized management
- can still do everything else you could as a normal plugin

Details.  AutoTrees is itself a plugin. When it starts it,

1. Scans the leo\plugins\trees folder to find handlers.

2. Activates specific handlers (this is managed via a plugin manager type window).

3. Waits for clicks and double-clicks on special nodes.

To create an AutoTree node, you add a node with @auto-my_handler. The @auto
tells the plugin to go and look for the "my_handler" handler, if it is enabled.
The handler is then called and this is then used to populate the node body and
child nodes below this node.

For example, for an @auto-rss node, the node headline is "@auto-rss
http://myurl/news.xml". The handler goes to the URL mentioned and downloads the
news stories. It then creates child nodes for each story and populates the
bodies.

For example handlers, see the source code in leoPlugins.leo
"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.2"
__plugin_name__ = "AutoTrees"
__plugin_priority__ = 100
__plugin_group__ = "Helpers"

#@+<< imports >>
#@+node:ekr.20050329082101.117: ** << imports >>
import leo.core.leoGlobals as g

import re
import sys
import glob

# Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

try:
    plugin_manager = __import__("plugin_manager")
except ImportError as err:
    # g.es("Autotrees did not load plugin manager: %s" % (err,), color="red")
    plugin_manager = None



#@-<< imports >>

#@+<< version history >>
#@+node:ekr.20050329082101.118: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Paul Paterson:
#     - Initial version
# 0.2 EKR:
#     - Set ok in init function.
# 0.3 EKR:
#     - Add c argument to topLevelMenu function and showManagerDialog ctor.
#@-<< version history >>
#@+<< todo >>
#@+node:ekr.20050329082101.119: ** << todo >>
#@@nocolor-node

#@+at
# 
# Todo list:
# 
# - periodic updates
# 
# Done:
# 
# - optional remove tree   
# - double click hook
# - remove old tree
# - populate new tree
# - scan for tree plugins
# - use plugin manager to manage
# - allow them to be turned off
#@-<< todo >>

thePluginController = None

#@+others
#@+node:ekr.20050329082101.120: ** Error Classes
class AutoTreeError(Exception):
    """Something went wrong with the tree"""

class BadHandler(AutoTreeError):
    """The handler could not be loaded"""
#@+node:ekr.20050329082101.121: ** init
def init():

    ok = plugin_manager is not None

    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)
    else:
        g.es_print('autotrees.py requires the plugins_manager plugin')

    return ok
#@+node:ekr.20050329082101.122: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    global thePluginController
    thePluginController = pluginController(c)
#@+node:ekr.20050329082101.123: ** topLevelMenu
# This is called from plugins_menu plugin.

def topLevelMenu(c):   
    """Manage the tree handlers"""
    global thePluginController    
    thePluginController.showManagerDialog(c)
#@+node:ekr.20050329082101.124: ** class TreeNode
class TreeNode:
    """Represents a child on the tree"""

    headline = "A headline"
    body = "A body"

    #@+others
    #@+node:ekr.20050329082101.125: *3* __init__
    def __init__(self, headline, body="", children=None):
        """Initialize the node"""
        self.headline = headline
        self.body = body
        self.children = children or []
    #@-others
#@+node:ekr.20050329082101.126: ** class BaseTreeHandler
class BaseTreeHandler:
    """Base handler for all trees"""

    # Set this to every event you want to handle
    handles = set(["icondclick1"])

    #@+others
    #@+node:ekr.20050329082101.127: *3* __init__
    def __init__(self,node):
        """Initialise the handler"""
        self.c = None # set in initFrom.
        self.node = node
    #@+node:ekr.20050329082101.128: *3* refresh
    def refresh(self):
        """Refresh the node"""
        #
        # Perform any pre-processing on the node
        self.preprocessNode()
        #
        # Add children
        self.addChildren(self.children, self.node)   
    #@+node:ekr.20050329082101.129: *3* preprocessNode
    def preprocessNode(self):
        """Pre-process the node

        Typically this will involve deleting the existing child nodes, and
        this is the default behaviour. However, a concrete handler could
        override this method to provide alternate behaviour.

        """
        while self.node.firstChild():
            self.node.firstChild().doDelete(self.node)
    #@+node:ekr.20050329082101.130: *3* initFrom
    def initFrom(self,c,parameter):
        """Perform any initialization here"""
        self.c = c
        self.children = []
    #@+node:ekr.20050329082101.131: *3* addChildren
    def addChildren(self, child_list, add_to_node):
        """Add all the children"""
        #import pdb; pdb.set_trace()
        c = self.c
        for child in child_list:
            new_node = add_to_node.insertAsLastChild()
            c.setHeadString(new_node,child.headline)
            c.setBodyString(new_node,child.body)
            self.addChildren(child.children, new_node)
    #@-others
#@+node:ekr.20050329082101.132: ** class pluginController
class pluginController:

    #@+others
    #@+node:ekr.20050329082101.133: *3* __init__
    def __init__ (self,c):
        """Initialise the commander"""
        self.c = c
        # Register handlers
        g.registerHandler("icondclick1", self.onIconDoubleClick)  
        g.registerHandler("headclick1", self.onHeadlineClick)  
        #
        # Prepare regular expressions
        self.getdetails = re.compile(r"@(\w+)-(\w+)\s+(.*)")
        #
        # Load tree handlers
        self.handlers = {}
        self.loadTreeHandlers()
    #@+node:ekr.20050329082101.134: *3* loadTreeHandlers
    def loadTreeHandlers(self):
        """Load all the handler for tree items"""
        #
        # Paths for key folders
        plugin_path = g.os_path_join(g.app.loadDir, "..", "plugins")
        self.handler_path = handler_path = g.os_path_join(g.app.loadDir, "..", "plugins", "trees")
        #
        if not g.os_path_isdir(handler_path):
            g.es("No tree handler folder found", color="red")
        else:
            g.es("Scanning for tree handlers", color="blue")
            #
            # Add folder locations to path
            old_path = sys.path[:]
            sys.path.insert(0, plugin_path)
            sys.path.insert(0, handler_path)
            #@+<< Get plugin manager module >>
            #@+node:ekr.20050329082101.135: *4* << Get plugin manager module >>
            # Get the manager
            try:
                self.plugin_manager = __import__("plugin_manager")
            except ImportError as err:
                g.es("Autotrees did not load plugin manager: %s" % (err,), color="red")
                self.plugin_manager = None
            #@-<< Get plugin manager module >>
            #@+<< Find all handlers >>
            #@+node:ekr.20050329082101.136: *4* << Find all handlers >>
            # Find all handlers
            for filename in glob.glob(g.os_path_join(handler_path, "*.py")):
                handler_name = g.os_path_splitext(g.os_path_split(filename)[1])[0]
                g.es("... looking in %s" % handler_name, color="blue")
                try:
                    self.loadHandlersFrom(handler_name)
                except BadHandler as err:
                    g.es("... unable to load '%s' handler: %s" % (handler_name, err), color="red")
            #@-<< Find all handlers >>
            # Restore
            sys.path = old_path
    #@+node:ekr.20050329082101.137: *3* loadHandlersFrom
    def loadHandlersFrom(self, name):
        """Load handlers from a module"""
        try:
            module = __import__(name)
        except Exception as err:
            raise BadHandler("Failed import: %s" % err)
        #
        # Look for handler classes
        for cls_name in dir(module):
            object = getattr(module, cls_name)
            try:
                is_handler = issubclass(object, BaseTreeHandler)
            except TypeError:
                is_handler = False
            if is_handler:
                g.es("... found handler '%s'" % (cls_name,), color="blue")
                self.handlers[cls_name.lower()] = object

    #@+node:ekr.20050329082101.138: *3* isActive
    def isActive(self, handler):
        """Return True if the named handler is active"""
        if self.plugin_manager:
            enable_manager = self.plugin_manager.EnableManager()
            enable_manager.initFrom(self.c,self.handler_path) 
            return handler.__module__ in enable_manager.actives
        else:
            return True   
    #@+node:ekr.20050329082101.139: *3* onHeadlineClick
    def onHeadlineClick(self, tag, keywords):
        """Handler the headline click event"""
        self.handleEvent("headclick1", tag, keywords)    
    #@+node:ekr.20050329082101.140: *3* onIconDoubleClick
    def onIconDoubleClick(self, tag, keywords):
        """Update the tree view"""
        self.handleEvent("icondclick1", tag, keywords)
    #@+node:ekr.20050329082101.141: *3* handleEvent
    def handleEvent(self, event_type, tag, keywords):
        """Handler a particular event"""
        #
        # Find the headline text
        node = keywords.get("p") or keywords.get("v")
        head = node.h.strip()
        match = self.getdetails.match(head)
        #
        # Is this an auto-tree?
        if match:
            node_type, handler_name, parameter = match.groups()
            if node_type.lower() == "auto":
                try:
                    handler_cls = self.handlers[handler_name.lower()]
                except KeyError:
                    g.es("No tree handler for '%s'" % (handler_name,), color="red")
                else:
                    handler = handler_cls(node)
                    if self.isActive(handler):                    
                        if event_type in handler.handles:
                            g.es("Handling '%s' with '%s'" % 
                                    (handler_name, parameter), color="blue")
                            handler.initFrom(self.c,parameter)
                            handler.refresh()
                        else:
                            g.es("'%s' not registered for '%s'" % 
                                    (handler_name, event_type), color="blue")
                    else:
                        g.es("Handler '%s' is disabled" % (handler_name,), color="red")    
    #@+node:ekr.20050329082101.142: *3* showManagerDialog
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
            #@+node:ekr.20050329082101.143: *4* << class HandlerDialog >>
            class HandlerDialog(self.plugin_manager.ManagerDialog):
                """A dialog to manager tree handlers"""

                dialog_caption = "AutoTree Handler Manager"

                #@+others
                #@+node:ekr.20060107092231: *5* ctor
                def __init__ (self,c):

                    self.c = c
                #@+node:ekr.20050329082101.144: *5* setPaths
                def setPaths(self):

                    """Set paths to the plugin locations"""
                    self.local_path = g.os_path_join(g.app.loadDir,"..","plugins","trees")
                    # self.remote_path = r"cvs.sourceforge.net/viewcvs.py/leo/leo/plugins/trees"
                    self.remote_path = r'leo.tigris.org/source/browse/leo/plugins/trees'
                #@-others
            #@-<< class HandlerDialog >>
            dlg = HandlerDialog(c)    
    #@-others
#@-others
#@-leo

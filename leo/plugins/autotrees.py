#@+leo-ver=4-thin
#@+node:ekr.20050329082101.115:@thin autotrees.py
#@<< docstring >>
#@+node:ekr.20050329082101.116:<< docstring >>
"""The AutoTrees plugin is a helper plugin designed to make it very easy to write
"hanlder" plugins to manage dynamic content in Leo outlines. AutoTrees provides:

- Convenient handler base classes which can be specialized for particular uses.

- A manager to turn handlers on and off.

- A set of example handlers to show the kinds of things that are possible.

AutoTrees doesn't do anything that you cannot do in other ways, but it does
provide a consistent way of adding dynamic content. This means that individual
plugin writers don't have to rewrite all the same kinds of code each time and
also makes it easier to maintain Leo, since it standardizes the way that certain
classes of plugin interact with the Leo core.

Why use this? I'm a plugin writer and I want to write a plugin to display
dynamic content - ie content not directly contained in the .leo or derived
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
#@-node:ekr.20050329082101.116:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

__version__ = "0.2"
__plugin_name__ = "AutoTrees"
__plugin_priority__ = 100
__plugin_group__ = "Helpers"

#@<< imports >>
#@+node:ekr.20050329082101.117:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
import re
import sys
import glob

Tk   = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
sets = g.importExtension('sets',pluginName=__name__,verbose=True)
#@nonl
#@-node:ekr.20050329082101.117:<< imports >>
#@nl

#@<< version history >>
#@+node:ekr.20050329082101.118:<< version history >>
#@@killcolor
#@+at
# 
# 0.1 Paul Paterson:
#     - Initial version
# 0.2 EKR:
#     - Set ok in init function.
#     - use g.importExtension to import sets.
# 0.3 EKR:
#     - Add c argument to topLevelMenu function and showManagerDialog ctor.
#@-at
#@nonl
#@-node:ekr.20050329082101.118:<< version history >>
#@nl
#@<< todo >>
#@+node:ekr.20050329082101.119:<< todo >>
"""

Todo list:

- periodic updates

Done:

- optional remove tree   
- double click hook
- remove old tree
- populate new tree
- scan for tree plugins
- use plugin manager to manage
- allow them to be turned off

"""
#@-node:ekr.20050329082101.119:<< todo >>
#@nl

#@+others
#@+node:ekr.20050329082101.120:Error Classes
class AutoTreeError(Exception):
    """Something went wrong with the tree"""

class BadHandler(AutoTreeError):
    """The handler could not be loaded"""
#@nonl
#@-node:ekr.20050329082101.120:Error Classes
#@+node:ekr.20050329082101.121:init
def init():

    ok = Tk and sets

    if ok:
        if g.app.gui is None:
            g.app.createTkGui(__file__)

        ok = g.app.gui.guiName() == "tkinter"

        if ok:
            if 0: # Use this if you want to create the commander class before the frame is fully created.
                leoPlugins.registerHandler('before-create-leo-frame',onCreate)
            else: # Use this if you want to create the commander class after the frame is fully created.
                leoPlugins.registerHandler('after-create-leo-frame',onCreate)
            g.plugin_signon(__name__)
        else:
            g.es("autotrees requires Tkinter",color='blue')

    return ok
#@nonl
#@-node:ekr.20050329082101.121:init
#@+node:ekr.20050329082101.122:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    global thePluginController
    thePluginController = pluginController(c)
#@nonl
#@-node:ekr.20050329082101.122:onCreate
#@+node:ekr.20050329082101.123:topLevelMenu
# This is called from plugins_menu plugin.

def topLevelMenu(c):   
    """Manage the tree handlers"""
    global thePluginController    
    thePluginController.showManagerDialog(c)
#@nonl
#@-node:ekr.20050329082101.123:topLevelMenu
#@+node:ekr.20050329082101.124:class TreeNode
class TreeNode:
    """Represents a child on the tree"""

    headline = "A headline"
    body = "A body"

    #@    @+others
    #@+node:ekr.20050329082101.125:__init__
    def __init__(self, headline, body="", children=None):
        """Initialize the node"""
        self.headline = headline
        self.body = body
        self.children = children or []
    #@nonl
    #@-node:ekr.20050329082101.125:__init__
    #@-others
#@-node:ekr.20050329082101.124:class TreeNode
#@+node:ekr.20050329082101.126:class BaseTreeHandler
class BaseTreeHandler:
    """Base handler for all trees"""

    # Set this to every event you want to handle
    handles = sets.Set(["icondclick1"])

    #@    @+others
    #@+node:ekr.20050329082101.127:__init__
    def __init__(self,node):
        """Initialise the handler"""
        self.c = None # set in initFrom.
        self.node = node
    #@nonl
    #@-node:ekr.20050329082101.127:__init__
    #@+node:ekr.20050329082101.128:refresh
    def refresh(self):
        """Refresh the node"""
        #
        # Perform any pre-processing on the node
        self.preprocessNode()
        #
        # Add children
        self.addChildren(self.children, self.node)   
    #@-node:ekr.20050329082101.128:refresh
    #@+node:ekr.20050329082101.129:preprocessNode
    def preprocessNode(self):
        """Pre-process the node

        Typically this will involve deleting the existing child nodes, and
        this is the default behaviour. However, a concrete handler could
        override this method to provide alternate behaviour.

        """
        while self.node.firstChild():
            self.node.firstChild().doDelete(self.node)
    #@-node:ekr.20050329082101.129:preprocessNode
    #@+node:ekr.20050329082101.130:initFrom
    def initFrom(self,c,parameter):
        """Perform any initialization here"""
        self.c = c
        self.children = []
    #@nonl
    #@-node:ekr.20050329082101.130:initFrom
    #@+node:ekr.20050329082101.131:addChildren
    def addChildren(self, child_list, add_to_node):
        """Add all the children"""
        #import pdb; pdb.set_trace()
        c = self.c
        for child in child_list:
            new_node = add_to_node.insertAsLastChild()
            c.setHeadString(new_node,child.headline)
            c.setBodyString(new_node,child.body)
            self.addChildren(child.children, new_node)
    #@-node:ekr.20050329082101.131:addChildren
    #@-others
#@-node:ekr.20050329082101.126:class BaseTreeHandler
#@+node:ekr.20050329082101.132:class pluginController
class pluginController:

    #@    @+others
    #@+node:ekr.20050329082101.133:__init__
    def __init__ (self,c):
        """Initialise the commander"""
        self.c = c
        # Register handlers
        leoPlugins.registerHandler("icondclick1", self.onIconDoubleClick)  
        leoPlugins.registerHandler("headclick1", self.onHeadlineClick)  
        #
        # Prepare regular expressions
        self.getdetails = re.compile(r"@(\w+)-(\w+)\s+(.*)")
        #
        # Load tree handlers
        self.handlers = {}
        self.loadTreeHandlers()
    #@nonl
    #@-node:ekr.20050329082101.133:__init__
    #@+node:ekr.20050329082101.134:loadTreeHandlers
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
            #@        << Get plugin manager module >>
            #@+node:ekr.20050329082101.135:<< Get plugin manager module >>
            # Get the manager
            try:
                self.plugin_manager = __import__("plugin_manager")
            except ImportError as err:
                g.es("Autotrees did not load plugin manager: %s" % (err,), color="red")
                self.plugin_manager = None
            #@-node:ekr.20050329082101.135:<< Get plugin manager module >>
            #@nl
            #@        << Find all handlers >>
            #@+node:ekr.20050329082101.136:<< Find all handlers >>
            # Find all handlers
            for filename in glob.glob(g.os_path_join(handler_path, "*.py")):
                handler_name = g.os_path_splitext(g.os_path_split(filename)[1])[0]
                g.es("... looking in %s" % handler_name, color="blue")
                try:
                    self.loadHandlersFrom(handler_name)
                except BadHandler as err:
                    g.es("... unable to load '%s' handler: %s" % (handler_name, err), color="red")
            #@nonl
            #@-node:ekr.20050329082101.136:<< Find all handlers >>
            #@nl
            # Restore
            sys.path = old_path
    #@-node:ekr.20050329082101.134:loadTreeHandlers
    #@+node:ekr.20050329082101.137:loadHandlersFrom
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

    #@-node:ekr.20050329082101.137:loadHandlersFrom
    #@+node:ekr.20050329082101.138:isActive
    def isActive(self, handler):
        """Return True if the named handler is active"""
        if self.plugin_manager:
            enable_manager = self.plugin_manager.EnableManager()
            enable_manager.initFrom(self.c,self.handler_path) 
            return handler.__module__ in enable_manager.actives
        else:
            return True   
    #@nonl
    #@-node:ekr.20050329082101.138:isActive
    #@+node:ekr.20050329082101.139:onHeadlineClick
    def onHeadlineClick(self, tag, keywords):
        """Handler the headline click event"""
        self.handleEvent("headclick1", tag, keywords)    
    #@-node:ekr.20050329082101.139:onHeadlineClick
    #@+node:ekr.20050329082101.140:onIconDoubleClick
    def onIconDoubleClick(self, tag, keywords):
        """Update the tree view"""
        self.handleEvent("icondclick1", tag, keywords)
    #@nonl
    #@-node:ekr.20050329082101.140:onIconDoubleClick
    #@+node:ekr.20050329082101.141:handleEvent
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
    #@nonl
    #@-node:ekr.20050329082101.141:handleEvent
    #@+node:ekr.20050329082101.142:showManagerDialog
    def showManagerDialog(self,c):
        """Show the tree handler manager dialog"""
        if not self.plugin_manager:
            g.es("Plugin manager could not be loaded", color="red")
        else:
            #
            # The manager class is defined as a dynamic class because
            # we don't know if we will be able to import the 
            # base class!
            #@        << class HandlerDialog >>
            #@+node:ekr.20050329082101.143:<< class HandlerDialog >>
            class HandlerDialog(self.plugin_manager.ManagerDialog):
                """A dialog to manager tree handlers"""

                dialog_caption = "AutoTree Handler Manager"

                #@    @+others
                #@+node:ekr.20060107092231:ctor
                def __init__ (self,c):

                    self.c = c
                #@nonl
                #@-node:ekr.20060107092231:ctor
                #@+node:ekr.20050329082101.144:setPaths
                def setPaths(self):

                    """Set paths to the plugin locations"""
                    self.local_path = g.os_path_join(g.app.loadDir,"..","plugins","trees")
                    # self.remote_path = r"cvs.sourceforge.net/viewcvs.py/leo/leo/plugins/trees"
                    self.remote_path = r'leo.tigris.org/source/browse/leo/plugins/trees'
                #@nonl
                #@-node:ekr.20050329082101.144:setPaths
                #@-others
            #@nonl
            #@-node:ekr.20050329082101.143:<< class HandlerDialog >>
            #@nl
            dlg = HandlerDialog(c)    
    #@-node:ekr.20050329082101.142:showManagerDialog
    #@-others
#@nonl
#@-node:ekr.20050329082101.132:class pluginController
#@-others
#@nonl
#@-node:ekr.20050329082101.115:@thin autotrees.py
#@-leo

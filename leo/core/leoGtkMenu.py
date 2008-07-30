# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20080112171213:@thin leoGtkMenu.py
#@@first

'''Leo's Gtk Gui module.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20080112171315:<< imports >>
import leo.core.leoGlobals as g

import gtk
import gobject

import leo.core.leoMenu as leoMenu
#@-node:ekr.20080112171315:<< imports >>
#@nl


#@+others
#@+node:bob.20080116062459:== gtk menu wrappers and mixin ==
"""This is a collection of wrappers around gtk's menu related classes.

They are here to provide the opportunity for leo specific adaptions
to these classes.

These enhancements do not violate leos Adaptor class philosophy and they
are named whith a '_' prefix to indicate they are private to leoGtkMenu.
They should only be used internally or via calls to c.frame.menu.

These adaptions may seem like overkill, but, although the gtk menu system is very powerful,
it can sometimes be difficult to do simple things and these adaptations make
life easier even now.  When the time comes to extend the system to meet Terry's
needs for cleo, all this will make life much easier still. 

At the moment all these adaptations do is the following:

    A 'c' parameter is required and added to each item and menu
        so if we ever encounter one in the wild we will be able to trace
        it back to its commander.

    MenuItems *AND* SeparatorMenuItems gain a getLabel method backed up
        by a self__label ivar which stores the 'label' parameter used in
        its construction. This makes it easier to search through a list
        of menu items that includes separators without having to worry
        about the sort of item they contain.
"""

#@+node:bob.20080116062459.1:_gtkMenuMixin
class _gtkMenuMixin:
    """This is a class to provide common leo specific functionality to gtk's menu objects."""


    #@    @+others
    #@+node:bob.20080116062459.2:__init__ (_gtkMenuMixin)
    def __init__(self, c, label='', underline=None):

        """initialize leo specific features comon to gtk.Menu and gtk.MenuItem wrappers.

        See host classes for documentation.

        """

        self.c = c
        self._label = label
        self._underline = underline

        self.__markLabel()
    #@-node:bob.20080116062459.2:__init__ (_gtkMenuMixin)
    #@+node:bob.20080117162206:getLabel
    def getLabel(self):
        return self._label
    #@nonl
    #@-node:bob.20080117162206:getLabel
    #@+node:bob.20080117174551:getUnderline
    def getUnderline(self):
        return self._underline
    #@nonl
    #@-node:bob.20080117174551:getUnderline
    #@+node:bob.20080118180107:setLabel
    def setLabel(self, label, underline):

        self._label = label
        self._underline = underline
        self.__markLabel()

        if isinstance(self, _gtkMenuItem):
            self.get_child().set_text(self._markedLabel)

    #@-node:bob.20080118180107:setLabel
    #@+node:bob.20080118180521:__markLabel
    def __markLabel(self):

        underline = self._underline
        label = self._label

        if underline >-1:
            self._markedLabel = label[:underline] + '_' + label[underline:]
            self._use_underline = True
        else:
            self._markedLabel = label
            self._use_underline = False
    #@-node:bob.20080118180521:__markLabel
    #@-others
#@-node:bob.20080116062459.1:_gtkMenuMixin
#@+node:bob.20080116062459.3:class _gtkMenu (gtk.Menu, _gtkMenuMixin)
class _gtkMenu (gtk.Menu, _gtkMenuMixin):

    """This is a wrapper around gtk.Menu.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native Menu object.

    """

    #@    @+others
    #@+node:bob.20080116062459.4:__init__ (_gtkMenu)
    def __init__ (self, c, tearoff=0):

        """Create and wrap a gtk.Menu. Do leo specific initailization."""

        _gtkMenuMixin.__init__(self, c)
        gtk.Menu.__gobject_init__(self)


    #@-node:bob.20080116062459.4:__init__ (_gtkMenu)
    #@-others

gobject.type_register(_gtkMenu)
#@-node:bob.20080116062459.3:class _gtkMenu (gtk.Menu, _gtkMenuMixin)
#@+node:bob.20080116062459.5:class _gtkMenuItem (gtk.MenuItem, _gtkMenuMixin)
class _gtkMenuItem(gtk.MenuItem, _gtkMenuMixin):

    """This is a wrapper around gtk.MenuItem.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native gtk.MenuItem object.

    """

    #@    @+others
    #@+node:bob.20080116062459.6:__init__ (_gtkMenuItem)
    def __init__ (self,c, label=None, underline=None):

        """Create and wrap a gtk.MenuItem. Do leo specific initailization.

        'c' is the commander that owns this item

        'label' should be a string indicating the text that should appear in
            the items label.  It should not contain any accelerator marks.

        'underline' should be an integer index into label and indicates the
            position of the character that should be marked as an accelerator.

            If underline is -1, no accelerator mark will be used.

        """

        _gtkMenuMixin.__init__(self, c, label, underline=-1)
        gtk.MenuItem.__init__(self, self._markedLabel, self._use_underline)


    #@-node:bob.20080116062459.6:__init__ (_gtkMenuItem)
    #@-others

# Can't seem to do this, __gobject_init__ takes no paramaters
#gobject.type_register(_gtkMenuItem)
#@-node:bob.20080116062459.5:class _gtkMenuItem (gtk.MenuItem, _gtkMenuMixin)
#@+node:bob.20080117161339:class _gtkSeparatorMenuItem
class _gtkSeparatorMenuItem(gtk.SeparatorMenuItem, _gtkMenuMixin):

    """This is a wrapper around gtk.SeparatorMenuItem.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native gtk.SeparatorMenuItem object.

    Seperators can be labeled and by default are labeled '-'. This makes
    it easier to search through a list of items for a specific menu.

    Having named seperators also offers the possibility of using seperators
    to provide named sections in menus. Although this would have to be back
    ported to tkLeo for it to be useful.

    """

    #@    @+others
    #@+node:bob.20080117161339.1:__init__ (_gtkSeparatorMenuItem)
    def __init__ (self, c, label='-', underline=-1):

        """Create and wrap a gtk.SeparatorMenuItem. Do leo specific initailization.

        'c' is the commander that owns this item

        'label' should be a string indicating the text that should appear in
            the items label.  It should not contain any accelerator marks.

        'underline' should be an integer index into label and indicates the
            position of the character that should be marked as an accelerator.


        'underline' has no significance here but is provided for compatability
            with _gtkMenuItem.

        """
        _gtkMenuMixin.__init__(self, c, label, underline)
        gtk.SeparatorMenuItem.__gobject_init__(self)


    #@-node:bob.20080117161339.1:__init__ (_gtkSeparatorMenuItem)
    #@-others

gobject.type_register(_gtkSeparatorMenuItem)
#@-node:bob.20080117161339:class _gtkSeparatorMenuItem
#@+node:bob.20080116063829:class _gtkMenuBar (gtk.Menubar, _gtkMenuMixin
class _gtkMenuBar(gtk.MenuBar, _gtkMenuMixin):

    """This is a wrapper around gtk.MenuBar.

    The purpose of this wrapper is to provide leo specific
    additions and modifications to the native gtk.MenuBar object.

    """

    #@    @+others
    #@+node:bob.20080116063829.1:__init__ (_gtkMenuBar)
    def __init__ (self,c):

        """Create and wrap a gtk.MenuBar. Do leo specific initailization."""

        _gtkMenuMixin.__init__(self, c)
        gtk.MenuBar.__gobject_init__(self)
    #@-node:bob.20080116063829.1:__init__ (_gtkMenuBar)
    #@-others

gobject.type_register(_gtkMenuBar)
#@-node:bob.20080116063829:class _gtkMenuBar (gtk.Menubar, _gtkMenuMixin
#@-node:bob.20080116062459:== gtk menu wrappers and mixin ==
#@+node:bob.20080116065711.1:class leoGtkMenu(leoMenu.leoMenu)
class leoGtkMenu(leoMenu.leoMenu):

    #@    @+others
    #@+node:ekr.20080112145409.174: leoGtkMenu.__init__
    def __init__ (self,frame):

        """Create an instance of leoMenu class adapted for the gtkGui."""

        leoMenu.leoMenu.__init__(self,frame)
    #@-node:ekr.20080112145409.174: leoGtkMenu.__init__
    #@+node:ekr.20080112145409.181:plugin menu stuff... (not ready yet)
    if 0:
        #@    @+others
        #@+node:ekr.20080112145409.182:createPluginMenu
        def createPluginMenu (self):

            top = self.getMenu('top')
            oline = self.getMenu('Outline')
            ind = top.getComponentIndex(oline) + 1
            import leo.core.leoGtkPluginManager as leoGtkPluginManager
            self.plugin_menu = pmenu = leoGtkPluginManager.createPluginsMenu()
            #self.plugin_menu = pmenu = gtk.JMenu( "Plugins" )
            top.add(pmenu,ind)
            #cpm = gtk.JMenuItem( "Plugin Manager" )
            #cpm.actionPerformed = self.createPluginManager
            #pmenu.add( cpm )
            #pmenu.addSeparator()


            #self.names_and_commands[ "Plugin Manager" ] = self.createPluginManager


        #@-node:ekr.20080112145409.182:createPluginMenu
        #@+node:ekr.20080112145409.183:createPluginManager
        def createPluginManager (self,event):

            import leo.core.leoGtkPluginManager as lspm
            lspm.topLevelMenu()

        #@-node:ekr.20080112145409.183:createPluginManager
        #@+node:ekr.20080112145409.184:getPluginMenu
        def getPluginMenu (self):

            return self.plugin_menu
        #@-node:ekr.20080112145409.184:getPluginMenu
        #@-others
    #@nonl
    #@-node:ekr.20080112145409.181:plugin menu stuff... (not ready yet)
    #@+node:ekr.20080112145409.195:oops
    def oops (self):

        g.pr("leoMenu oops:", g.callers(2), "should be overridden in subclass")
    #@nonl
    #@-node:ekr.20080112145409.195:oops
    #@+node:bob.20080115223114.11:Menu methods (Tk names)
    #@+node:bob.20080115223114.12:Not called
    def bind (self,bind_shortcut,callback):

        g.trace(bind_shortcut,callback)

    def delete (self,menu,readItemName):

        g.trace(menu,readItemName)

    def destroy (self,menu):

        g.trace(menu)
    #@-node:bob.20080115223114.12:Not called
    #@+node:bob.20080115223114.13:add_cascade
    def add_cascade (self,parent,label,menu,underline):

        """This is an adapter for insert_cascade(..,position=-1,..)."""

        self.insert_cascade(parent, -1, label, menu , underline)   
    #@-node:bob.20080115223114.13:add_cascade
    #@+node:bob.20080115223114.14:add_command
    def add_command (self,menu,**keys):

        c = self.c

        if not menu:
            return g.trace('Should not happen.  No menu')

        item = _gtkMenuItem(c, keys.get('label'), keys.get('underline'))

        menu.append(item)

        callback = keys.get('command')

        def menuCallback (event,callback=callback):
             callback() # All args were bound when the callback was created.


        item.connect('activate', menuCallback)
        item.show()
    #@-node:bob.20080115223114.14:add_command
    #@+node:bob.20080115223114.15:add_separator
    def add_separator(self,menu):

        c = self.c

        if not menu:
           return g.trace('Should not happen.  No menu')

        item = _gtkSeparatorMenuItem(c)
        item.show()
        menu.append(item)

    #@-node:bob.20080115223114.15:add_separator
    #@+node:bob.20080115223114.16:delete_range

    def delete_range (self,menu,n1,n2):
        """Delete a range of items in a menu.

        The effect will be akin to:

            delete menu[n1:n2]

        """
        if not menu:
            return g.trace('Should not happen.  No menu')

        if n1 > n2:
            n2, n1 = n1, n2

        items = menu.get_children()

        for item in items[n1:n2]:
            menu.remove(item)

    #@-node:bob.20080115223114.16:delete_range
    #@+node:bob.20080115223114.17:index & invoke
    # It appears wxWidgets can't invoke a menu programmatically.
    # The workaround is to change the unit test.

    def index (self,name):
        '''Return the menu item whose name is given.'''

    def invoke (self,i):
            '''Invoke the menu whose index is i'''
    #@-node:bob.20080115223114.17:index & invoke
    #@+node:bob.20080115223114.18:insert
    def insert (self,menuName,position,label,command,underline=True):

        """Insert a menu item with a command into a named menu.

        'menuName' is the name of the menu into which the item is to be inserted.

        'position' is the position in the position in the menu where the item is to be inserted.
            if 'position' is -1 then the item will be appended

        'label' is the text to be used as a label for the menu item.

        'command' is a python method or function which is to be called when the menu item is activated.

        'underline' if True, the first underscore in 'label' will mark the mnemonic. (default )

        """

        c = self.c

        menu = self.getMenu(menuName)

        item = _gtkMenuItem(c, label, underline)


        if position==-1:
            menu.append(item)
        else:
            menu.insert(item, position)


        def gtkMenuCallback (event,callback=command):
            callback() # All args were bound when the callback was created.


        item.connect('activate', gtkMenuCallback)
        item.show()

    #@-node:bob.20080115223114.18:insert
    #@+node:bob.20080115223114.19:insert_cascade
    def insert_cascade (self,parent,index,label,menu,underline):

        """Create a menu with the given parent menu.

        'parent' is the menu into which the cascade menu should be inserted.
            if this is None then the menubar will be used as the parent.

        'label' is the text to be used as the menus label.

        'index' is the position in the parent menu where this menu should
            be inserted.

        'menu' is the cascade menu that is to be inserted.

        'underline' if True, the first underscore in 'label' will mark the mnemonic.

        """

        c = self.c

        if not menu:
            return g.trace('Should not happen.  No menu')


        item = _gtkMenuItem(c, label, underline)
        item.set_submenu(menu)

        if not parent:
            parent = self.menuBar

        if index == -1:
            parent.append(item)
        else:
            parent.insert(item, index)

        item.show()
    #@-node:bob.20080115223114.19:insert_cascade
    #@+node:bob.20080115223114.20:new_menu
    def new_menu(self,parent,tearoff=0):
        return _gtkMenu(self.c)
    #@-node:bob.20080115223114.20:new_menu
    #@-node:bob.20080115223114.11:Menu methods (Tk names)
    #@+node:bob.20080115223114:Menu methods (non-Tk names)
    #@+node:bob.20080115223114.1:createMenuBar
    def createMenuBar(self,frame):

        c = self.c

        #g.trace(frame)

        self.menuBar = menuBar = _gtkMenuBar(c)

        self.createMenusFromTables()

        #self.createAcceleratorTables()


        panel = frame.menuHolderPanel
        panel.pack_start(menuBar, False, True, 0)
        panel.show_all()


        # menuBar.SetAcceleratorTable(wx.NullAcceleratorTable)

    #@-node:bob.20080115223114.1:createMenuBar
    #@+node:bob.20080115223114.2:createOpenWithMenuFromTable & helper
    def createOpenWithMenuFromTable (self,table):

        '''Entries in the table passed to createOpenWithMenuFromTable are
    tuples of the form (commandName,shortcut,data).

    - command is one of "os.system", "os.startfile", "os.spawnl", "os.spawnv" or "exec".
    - shortcut is a string describing a shortcut, just as for createMenuItemsFromTable.
    - data is a tuple of the form (command,arg,ext).

    Leo executes command(arg+path) where path is the full path to the temp file.
    If ext is not None, the temp file has the given extension.
    Otherwise, Leo computes an extension based on the @language directive in effect.'''
        g.trace()

        c = self.c
        g.app.openWithTable = table # Override any previous table.

        # Delete the previous entry.

        parent = self.getMenu("File")

        label = self.getRealMenuName("Open &With...")

        amp_index = label.find("&")
        label = label.replace("&","")

        ## FIXME to be gui independant
        index = 0;
        for item in parent.get_children():
            if item.getLabel() == 'Open With...':
                parent.remove(item)
                break
            index += 1

        # Create the Open With menu.
        openWithMenu = self.createOpenWithMenu(parent,label,index,amp_index)

        self.setMenu("Open With...",openWithMenu)
        # Create the menu items in of the Open With menu.
        for entry in table:
            if len(entry) != 3: # 6/22/03
                g.es("","createOpenWithMenuFromTable:","invalid data",color="red")
                return
        self.createOpenWithMenuItemsFromTable(openWithMenu,table)
    #@+node:bob.20080115223114.3:createOpenWithMenuItemsFromTable
    def createOpenWithMenuItemsFromTable (self,menu,table):

        '''Create an entry in the Open with Menu from the table.

        Each entry should be a sequence with 2 or 3 elements.'''

        c = self.c ; k = c.k

        if g.app.unitTesting: return

        for data in table:
            #@        << get label, accelerator & command or continue >>
            #@+node:bob.20080115223114.4:<< get label, accelerator & command or continue >>
            ok = (
                type(data) in (type(()), type([])) and
                len(data) in (2,3)
            )

            if ok:
                if len(data) == 2:
                    label,openWithData = data ; accelerator = None
                else:
                    label,accelerator,openWithData = data
                    accelerator = k.shortcutFromSetting(accelerator)
                    accelerator = accelerator and g.stripBrackets(k.prettyPrintKey(accelerator))
            else:
                g.trace('bad data in Open With table: %s' % repr(data))
                continue # Ignore bad data
            #@-node:bob.20080115223114.4:<< get label, accelerator & command or continue >>
            #@nl
            # g.trace(label,accelerator)
            realLabel = self.getRealMenuName(label)
            underline=realLabel.find("&")
            realLabel = realLabel.replace("&","")
            callback = self.defineOpenWithMenuCallback(openWithData)

            c.add_command(menu,label=realLabel,
                accelerator=accelerator or '',
                command=callback,underline=underline)
    #@-node:bob.20080115223114.3:createOpenWithMenuItemsFromTable
    #@-node:bob.20080115223114.2:createOpenWithMenuFromTable & helper
    #@+node:bob.20080115223114.5:defineMenuCallback
    def defineMenuCallback(self,command,name):
        """Define a menu callback to bind a command to a menu.

        'command' is the leo minibuffer command to be executed when
                   the menu item is activated

        'name' is the text that should appear in the as the menu's label.


        The first parameter of the callback must be 'event', and it must default to None.

        """
        def callback(event=None,self=self,command=command,label=name):
            self.c.doCommand(command,label,event)

        return callback
    #@-node:bob.20080115223114.5:defineMenuCallback
    #@+node:bob.20080115223114.6:defineOpenWithMenuCallback
    def defineOpenWithMenuCallback (self,command):

        # The first parameter must be event, and it must default to None.
        def wxOpenWithMenuCallback(event=None,command=command):
            try: self.c.openWith(data=command)
            except: g.pr(traceback.print_exc())

        return wxOpenWithMenuCallback
    #@-node:bob.20080115223114.6:defineOpenWithMenuCallback
    #@+node:bob.20080115223114.7:createOpenWithMenu
    def createOpenWithMenu(self,parent,label,index,amp_index):

        '''Create a submenu.'''
        menu = self.new_menu(parent)
        self.insert_cascade(parent, index, label=label,menu=menu,underline=amp_index)
        return menu
    #@-node:bob.20080115223114.7:createOpenWithMenu
    #@+node:bob.20080115223114.8:disableMenu
    def disableMenu (self,menu,name):

        g.trace('not implemented')
        return ###

        if not menu:
            g.trace("no menu",name)
            return

        realName = self.getRealMenuName(name)
        realName = realName.replace("&","")
        id = menu.FindItem(realName)
        if id:
            item = menu.FindItemById(id)
            item.Enable(0)
        else:
            g.trace("no item",name,val)
    #@-node:bob.20080115223114.8:disableMenu
    #@+node:bob.20080115223114.9:enableMenu
    def enableMenu (self,menu,name,val):

        g.trace('not implemented')
        return ###

        if not menu:
            g.trace("no menu",name,val)
            return

        realName = self.getRealMenuName(name)
        realName = realName.replace("&","")
        id = menu.FindItem(realName)
        if id:
            item = menu.FindItemById(id)
            val = g.choose(val,1,0)
            item.Enable(val)
        else:
            g.trace("no item",name,val)
    #@nonl
    #@-node:bob.20080115223114.9:enableMenu
    #@+node:bob.20080115223114.10:setMenuLabel
    def setMenuLabel (self,menu,name,label,underline=-1):

        if not menu:
            g.trace("no menu",name)
            return

        items = menu.get_children()

        if type(name) == type(0):
            # "name" is actually an index into the menu.
            if items and len(items) > name :
                item = items[name].GetId()
            else:
                item = None
        else:
            realName = self.getRealMenuName(name)
            realName = realName.replace("&","")
            for item in items:
                if item.getLabel() == realName:
                    break
            else:
                item = None      

        if item:
            label = self.getRealMenuName(label)
            label = label.replace("&","")
            # g.trace(name,label)
            item.setLabel(label, underline)
        else:
            g.trace("no item",name,label)
    #@-node:bob.20080115223114.10:setMenuLabel
    #@-node:bob.20080115223114:Menu methods (non-Tk names)
    #@-others
#@nonl
#@-node:bob.20080116065711.1:class leoGtkMenu(leoMenu.leoMenu)
#@-others
#@nonl
#@-node:ekr.20080112171213:@thin leoGtkMenu.py
#@-leo

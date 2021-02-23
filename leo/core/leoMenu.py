#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3749: * @file leoMenu.py
"""Gui-independent menu handling for Leo."""
from leo.core import leoGlobals as g
#@+others
#@+node:ekr.20031218072017.3750: ** class LeoMenu
class LeoMenu:
    """The base class for all Leo menus."""
    #@+others
    #@+node:ekr.20120124042346.12938: *3* LeoMenu.Birth
    def __init__(self, frame):
        self.c = frame.c
        self.enable_dict = {}  # Created by finishCreate.
        self.frame = frame
        self.isNull = False
        self.menus = {}  # Menu dictionary.
        self.menuShortcuts = {}

    def finishCreate(self):
        self.define_enable_dict()
    #@+node:ekr.20120124042346.12937: *4* LeoMenu.define_enable_table
    #@@nobeautify

    def define_enable_dict (self):

        # pylint: disable=unnecessary-lambda
        # The lambdas *are* necessary.
        c = self.c
        if not c.commandsDict:
            return # This is not an error: it happens during init.
        self.enable_dict = d = {

            # File menu...
                # 'revert':         True, # Revert is always enabled.
                # 'open-with':      True, # Open-With is always enabled.

            # Edit menu...
            'undo':                 c.undoer.canUndo,
            'redo':                 c.undoer.canRedo,
            'extract-names':        c.canExtractSectionNames,
            'extract':              c.canExtract,
            'match-brackets':       c.canFindMatchingBracket,

            # Top-level Outline menu...
            'cut-node':             c.canCutOutline,
            'delete-node':          c.canDeleteHeadline,
            'paste-node':           c.canPasteOutline,
            'paste-retaining-clones':   c.canPasteOutline,
            'clone-node':           c.canClone,
            'sort-siblings':        c.canSortSiblings,
            'hoist':                c.canHoist,
            'de-hoist':             c.canDehoist,

            # Outline:Expand/Contract menu...
            'contract-parent':      c.canContractParent,
            'contract-node':        lambda: c.p.hasChildren() and c.p.isExpanded(),
            'contract-or-go-left':  lambda: c.p.hasChildren() and c.p.isExpanded() or c.p.hasParent(),
            'expand-node':          lambda: c.p.hasChildren() and not c.p.isExpanded(),
            'expand-prev-level':    lambda: c.p.hasChildren() and c.p.isExpanded(),
            'expand-next-level':    lambda: c.p.hasChildren(),
            'expand-to-level-1':    lambda: c.p.hasChildren() and c.p.isExpanded(),
            'expand-or-go-right':   lambda: c.p.hasChildren(),

            # Outline:Move menu...
            'move-outline-down':    lambda: c.canMoveOutlineDown(),
            'move-outline-left':    lambda: c.canMoveOutlineLeft(),
            'move-outline-right':   lambda: c.canMoveOutlineRight(),
            'move-outline-up':      lambda: c.canMoveOutlineUp(),
            'promote':              lambda: c.canPromote(),
            'demote':               lambda: c.canDemote(),

            # Outline:Go To menu...
            'goto-prev-history-node':   lambda: c.nodeHistory.canGoToPrevVisited(),
            'goto-next-history-node':   lambda: c.nodeHistory.canGoToNextVisited(),
            'goto-prev-visible':        lambda: c.canSelectVisBack(),
            'goto-next-visible':        lambda: c.canSelectVisNext(),
            # These are too slow...
                # 'go-to-next-marked':  c.canGoToNextMarkedHeadline,
                # 'go-to-next-changed': c.canGoToNextDirtyHeadline,
            'goto-next-clone':          lambda: c.p.isCloned(),
            'goto-prev-node':           lambda: c.canSelectThreadBack(),
            'goto-next-node':           lambda: c.canSelectThreadNext(),
            'goto-parent':              lambda: c.p.hasParent(),
            'goto-prev-sibling':        lambda: c.p.hasBack(),
            'goto-next-sibling':        lambda: c.p.hasNext(),

            # Outline:Mark menu...
            'mark-subheads':            lambda: c.p.hasChildren(),
            # too slow...
                # 'mark-changed-items':   c.canMarkChangedHeadlines,
        }

        for i in range(1,9):
            d [f"expand-to-level-{i}"] = lambda: c.p.hasChildren()

        if 0: # Initial testing.
            commandKeys = list(c.commandsDict.keys())
            for key in sorted(d.keys()):
                if key not in commandKeys:
                    g.trace(f"*** bad entry for {key}")
    #@+node:ekr.20031218072017.3775: *3* LeoMenu.error and oops
    def oops(self):
        g.pr("LeoMenu oops:", g.callers(4), "should be overridden in subclass")

    def error(self, s):
        g.error('', s)
    #@+node:ekr.20031218072017.3781: *3* LeoMenu.Gui-independent menu routines
    #@+node:ekr.20060926213642: *4* LeoMenu.capitalizeMinibufferMenuName
    #@@nobeautify

    def capitalizeMinibufferMenuName(self, s, removeHyphens):
        result = []
        for i, ch in enumerate(s):
            prev =     s[i - 1] if i > 0 else ''
            prevprev = s[i - 2] if i > 1 else ''
            if (
                i == 0 or
                i == 1 and prev == '&' or
                prev == '-' or
                prev == '&' and prevprev == '-'
            ):
                result.append(ch.capitalize())
            elif removeHyphens and ch == '-':
                result.append(' ')
            else:
                result.append(ch)
        return ''.join(result)
    #@+node:ekr.20031218072017.3785: *4* LeoMenu.createMenusFromTables & helpers
    def createMenusFromTables(self):
        """(leoMenu) Usually over-ridden."""
        c = self.c
        aList = c.config.getMenusList()
        if aList:
            self.createMenusFromConfigList(aList)
        else:
            g.es_print('No @menu setting found')
    #@+node:ekr.20070926135612: *5* LeoMenu.createMenusFromConfigList & helpers
    def createMenusFromConfigList(self, aList):
        """
        Create menus from aList.
        The 'top' menu has already been created.
        """
        # Called from createMenuBar.
        c = self.c
        for z in aList:
            kind, val, val2 = z
            if kind.startswith('@menu'):
                name = kind[len('@menu') :].strip()
                if not self.handleSpecialMenus(name, parentName=None):
                    # Fix #528: Don't create duplicate menu items.
                    menu = self.createNewMenu(name)
                        # Create top-level menu.
                    if menu:
                        self.createMenuFromConfigList(name, val, level=0)
                    else:
                        g.trace('no menu', name)
            else:
                self.error(f"{kind} {val} not valid outside @menu tree")
        aList = c.config.getOpenWith()
        if aList:
            # a list of dicts.
            self.createOpenWithMenuFromTable(aList)
    #@+node:ekr.20070927082205: *6* LeoMenu.createMenuFromConfigList
    def createMenuFromConfigList(self, parentName, aList, level=0):
        """Build menu based on nested list

        List entries are either:

            ['@item', 'command-name', 'optional-view-name']

        or:

            ['@menu Submenu name', <nested list>, None]

        :param str parentName: name of menu under which to place this one
        :param list aList: list of entries as described above
        """
        parentMenu = self.getMenu(parentName)
        if not parentMenu:
            g.trace('NO PARENT', parentName, g.callers())
        table = []
        for z in aList:
            kind, val, val2 = z
            if kind.startswith('@menu'):
                # Menu names can be unicode without any problem.
                name = kind[5:].strip()
                if table:
                    self.createMenuEntries(parentMenu, table)
                if not self.handleSpecialMenus(name, parentName,
                    alt_name=val2,  #848.
                    table=table,
                ):
                    menu = self.createNewMenu(name, parentName)
                        # Create submenu of parent menu.
                    if menu:
                        # Partial fix for #528.
                        self.createMenuFromConfigList(name, val, level + 1)
                table = []
            elif kind == '@item':
                name = str(val)  # Item names must always be ascii.
                if val2:
                    # Translated names can be unicode.
                    table.append((val2, name),)
                else:
                    table.append(name)
            else:
                g.trace('can not happen: bad kind:', kind)
        if table:
            self.createMenuEntries(parentMenu, table)
    #@+node:ekr.20070927172712: *6* LeoMenu.handleSpecialMenus
    def handleSpecialMenus(self, name, parentName, alt_name=None, table=None):
        """
        Handle a special menu if name is the name of a special menu.
        return True if this method handles the menu.
        """
        c = self.c
        if table is None: table = []
        name2 = name.replace('&', '').replace(' ', '').lower()
        if name2 == 'plugins':
            # Create the plugins menu using a hook.
            g.doHook("create-optional-menus", c=c, menu_name=name)
            return True
        if name2.startswith('recentfiles'):
            # Just create the menu.
            # createRecentFilesMenuItems will create the contents later.
            g.app.recentFilesManager.recentFilesMenuName = alt_name or name
                #848
            self.createNewMenu(alt_name or name, parentName)
            return True
        if name2 == 'help' and g.isMac:
            helpMenu = self.getMacHelpMenu(table)
            return helpMenu is not None
        return False
    #@+node:ekr.20031218072017.3780: *4* LeoMenu.hasSelection
    # Returns True if text in the outline or body text is selected.

    def hasSelection(self):
        c = self.c; w = c.frame.body.wrapper
        if c.frame.body:
            first, last = w.getSelectionRange()
            return first != last
        return False
    #@+node:ekr.20051022053758.1: *3* LeoMenu.Helpers
    #@+node:ekr.20031218072017.3783: *4* LeoMenu.canonicalize*
    def canonicalizeMenuName(self, name):

        # #1121 & #1188. Allow Chinese characters in command names
        if g.isascii(name):
            return ''.join([ch for ch in name.lower() if ch.isalnum()])
        return name

    def canonicalizeTranslatedMenuName(self, name):

        # #1121 & #1188. Allow Chinese characters in command names
        if g.isascii(name):
            return ''.join([ch for ch in name.lower() if ch not in '& \t\n\r'])
        return ''.join([ch for ch in name if ch not in '& \t\n\r'])
    #@+node:ekr.20031218072017.1723: *4* LeoMenu.createMenuEntries & helpers
    def createMenuEntries(self, menu, table):
        """
        Create a menu entry from the table.
        
        This method shows the shortcut in the menu, but **never** binds any shortcuts.
        """
        c = self.c
        if g.app.unitTesting: return
        if not menu: return
        self.traceMenuTable(table)
        for data in table:
            label, command, done = self.getMenuEntryInfo(data, menu)
            if done:
                continue
            commandName = self.getMenuEntryBindings(command, label)
            if not commandName:
                continue
            masterMenuCallback = self.createMasterMenuCallback(command, commandName)
            realLabel = self.getRealMenuName(label)
            amp_index = realLabel.find("&")
            realLabel = realLabel.replace("&", "")
            # c.add_command ensures that c.outerUpdate is called.
            c.add_command(menu, label=realLabel,
                accelerator='',  # The accelerator is now computed dynamically.
                command=masterMenuCallback,
                commandName=commandName,
                underline=amp_index)
    #@+node:ekr.20111102072143.10016: *5* LeoMenu.createMasterMenuCallback
    def createMasterMenuCallback(self, command, commandName):
        """
        Create a callback for the given args.
        
        - If command is a string, it is treated as a command name.
        - Otherwise, it should be a callable representing the actual command.
        """
        c = self.c

        def getWidget():
            """Carefully return the widget that has focus."""
            w = c.frame.getFocus()
            if w and g.isMac:
                # Redirect (MacOS only).
                wname = c.widget_name(w)
                if wname.startswith('head'):
                    w = c.frame.tree.edit_widget(c.p)
            # Return a wrapper if possible.
            if not g.isTextWrapper(w):
                w = getattr(w, 'wrapper', w)
            return w

        if isinstance(command, str):
            
            def static_menu_callback():
                event = g.app.gui.create_key_event(c, w=getWidget())
                c.doCommandByName(commandName, event)

            return static_menu_callback
            
        # The command must be a callable.
        if not callable(command):

            def dummy_menu_callback(event=None):
                pass
        
            g.trace(f"bad command: {command!r}", color='red')
            return dummy_menu_callback

        # Create a command dynamically.

        def dynamic_menu_callback():
            event = g.app.gui.create_key_event(c, w=getWidget())
            return c.doCommand(command, commandName, event)  # #1595

        return dynamic_menu_callback
    #@+node:ekr.20111028060955.16568: *5* LeoMenu.getMenuEntryBindings
    def getMenuEntryBindings(self, command, label):
        """Compute commandName from command."""
        c = self.c
        if isinstance(command, str):
            # Command is really a command name.
            commandName = command
        else:
            # First, get the old-style name.
            # #1121: Allow Chinese characters in command names
            commandName = label.strip()
        command = c.commandsDict.get(commandName)
        return commandName
    #@+node:ekr.20111028060955.16565: *5* LeoMenu.getMenuEntryInfo
    def getMenuEntryInfo(self, data, menu):
        """
        Parse a single entry in the table passed to createMenuEntries.
        
        Table entries have the following formats:
            
        1. A string, used as the command name.
        2. A 2-tuple: (command_name, command_func)
        3. A 3-tuple: (command_name, menu_shortcut, command_func)
        
        Special case: If command_name is None or "-" it represents a menu separator.
        """
        done = False
        if isinstance(data, str):
            # A single string is both the label and the command.
            s = data
            removeHyphens = s and s[0] == '*'
            if removeHyphens: s = s[1:]
            label = self.capitalizeMinibufferMenuName(s, removeHyphens)
            command = s.replace('&', '').lower()
            if label == '-':
                self.add_separator(menu)
                done = True  # That's all.
        else:
            ok = isinstance(data, (list, tuple)) and len(data) in (2, 3)
            if ok:
                if len(data) == 2:
                    # Command can be a minibuffer-command name.
                    label, command = data
                else:
                    # Ignore shortcuts bound in menu tables.
                    label, junk, command = data
                if label in (None, '-'):
                    self.add_separator(menu)
                    done = True  # That's all.
            else:
                g.trace(f"bad data in menu table: {repr(data)}")
                done = True  # Ignore bad data
        return label, command, done
    #@+node:ekr.20111028060955.16563: *5* LeoMenu.traceMenuTable
    def traceMenuTable(self, table):

        trace = False and not g.unitTesting
        if not trace: return
        format = '%40s %s'
        g.trace('*' * 40)
        for data in table:
            if isinstance(data, (list, tuple)):
                n = len(data)
                if n == 2:
                    print(format % (data[0], data[1]))
                elif n == 3:
                    name, junk, func = data
                    print(format % (name, func and func.__name__ or '<NO FUNC>'))
            else:
                print(format % (data, ''))
    #@+node:ekr.20031218072017.3784: *4* LeoMenu.createMenuItemsFromTable
    def createMenuItemsFromTable(self, menuName, table):

        if g.app.gui.isNullGui:
            return
        try:
            menu = self.getMenu(menuName)
            if menu is None:
                return
            self.createMenuEntries(menu, table)
        except Exception:
            g.es_print("exception creating items for", menuName, "menu")
            g.es_exception()
        g.app.menuWarningsGiven = True
    #@+node:ekr.20031218072017.3804: *4* LeoMenu.createNewMenu
    def createNewMenu(self, menuName, parentName="top", before=None):
        try:
            parent = self.getMenu(parentName)  # parent may be None.
            menu = self.getMenu(menuName)
            if menu:
                # Not an error.
                # g.error("menu already exists:", menuName)
                return None  # Fix #528.
            menu = self.new_menu(parent, tearoff=0, label=menuName)
            self.setMenu(menuName, menu)
            label = self.getRealMenuName(menuName)
            amp_index = label.find("&")
            label = label.replace("&", "")
            if before:  # Insert the menu before the "before" menu.
                index_label = self.getRealMenuName(before)
                amp_index = index_label.find("&")
                index_label = index_label.replace("&", "")
                index = parent.index(index_label)
                self.insert_cascade(
                    parent, index=index, label=label, menu=menu, underline=amp_index)
            else:
                self.add_cascade(parent, label=label, menu=menu, underline=amp_index)
            return menu
        except Exception:
            g.es("exception creating", menuName, "menu")
            g.es_exception()
            return None
    #@+node:ekr.20031218072017.4116: *4* LeoMenu.createOpenWithMenuFromTable & helpers
    def createOpenWithMenuFromTable(self, table):
        """
        Table is a list of dictionaries, created from @openwith settings nodes.

        This menu code uses these keys:

            'name':     menu label.
            'shortcut': optional menu shortcut.

        efc.open_temp_file uses these keys:

            'args':     the command-line arguments to be used to open the file.
            'ext':      the file extension.
            'kind':     the method used to open the file, such as subprocess.Popen.
        """
        k = self.c.k
        if not table: return
        g.app.openWithTable = table  # Override any previous table.
        # Delete the previous entry.
        parent = self.getMenu("File")
        if not parent:
            if not g.app.batchMode:
                g.error('', 'createOpenWithMenuFromTable:', 'no File menu')
            return
        label = self.getRealMenuName("Open &With...")
        amp_index = label.find("&")
        label = label.replace("&", "")
        try:
            index = parent.index(label)
            parent.delete(index)
        except Exception:
            try:
                index = parent.index("Open With...")
                parent.delete(index)
            except Exception:
                g.trace('unexpected exception')
                g.es_exception()
                return
        # Create the Open With menu.
        openWithMenu = self.createOpenWithMenu(parent, label, index, amp_index)
        if not openWithMenu:
            g.trace('openWithMenu returns None')
            return
        self.setMenu("Open With...", openWithMenu)
        # Create the menu items in of the Open With menu.
        self.createOpenWithMenuItemsFromTable(openWithMenu, table)
        for d in table:
            k.bindOpenWith(d)
    #@+node:ekr.20051022043608.1: *5* LeoMenu.createOpenWithMenuItemsFromTable & callback
    def createOpenWithMenuItemsFromTable(self, menu, table):
        """
        Create an entry in the Open with Menu from the table, a list of dictionaries.

        Each dictionary d has the following keys:

        'args':     the command-line arguments used to open the file.
        'ext':      not used here: used by efc.open_temp_file.
        'kind':     not used here: used by efc.open_temp_file.
        'name':     menu label.
        'shortcut': optional menu shortcut.
        """
        c = self.c
        if g.app.unitTesting: return
        for d in table:
            label = d.get('name')
            args = d.get('args', [])
            accel = d.get('shortcut') or ''
            if label and args:
                realLabel = self.getRealMenuName(label)
                underline = realLabel.find("&")
                realLabel = realLabel.replace("&", "")
                callback = self.defineOpenWithMenuCallback(d)
                c.add_command(menu,
                    label=realLabel,
                    accelerator=accel,
                    command=callback,
                    underline=underline)
    #@+node:ekr.20031218072017.4118: *6* LeoMenu.defineOpenWithMenuCallback
    def defineOpenWithMenuCallback(self, d):
        # The first parameter must be event, and it must default to None.

        def openWithMenuCallback(event=None, self=self, d=d):
            return self.c.openWith(d=d)

        return openWithMenuCallback
    #@+node:tbrown.20080509212202.7: *4* LeoMenu.deleteRecentFilesMenuItems
    def deleteRecentFilesMenuItems(self, menu):
        """Delete recent file menu entries"""
        rf = g.app.recentFilesManager
        # Why not just delete all the entries?
        recentFiles = rf.getRecentFiles()
        toDrop = len(recentFiles) + len(rf.getRecentFilesTable())
        self.delete_range(menu, 0, toDrop)
        for i in rf.groupedMenus:
            menu = self.getMenu(i)
            if menu:
                self.destroy(menu)
                self.destroyMenu(i)
    #@+node:ekr.20031218072017.3805: *4* LeoMenu.deleteMenu
    def deleteMenu(self, menuName):
        try:
            menu = self.getMenu(menuName)
            if menu:
                self.destroy(menu)
                self.destroyMenu(menuName)
            else:
                g.es("can't delete menu:", menuName)
        except Exception:
            g.es("exception deleting", menuName, "menu")
            g.es_exception()
    #@+node:ekr.20031218072017.3806: *4* LeoMenu.deleteMenuItem
    def deleteMenuItem(self, itemName, menuName="top"):
        """Delete itemName from the menu whose name is menuName."""
        try:
            menu = self.getMenu(menuName)
            if menu:
                realItemName = self.getRealMenuName(itemName)
                self.delete(menu, realItemName)
            else:
                g.es("menu not found:", menuName)
        except Exception:
            g.es("exception deleting", itemName, "from", menuName, "menu")
            g.es_exception()
    #@+node:ekr.20031218072017.3782: *4* LeoMenu.get/setRealMenuName & setRealMenuNamesFromTable
    # Returns the translation of a menu name or an item name.

    def getRealMenuName(self, menuName):
        cmn = self.canonicalizeTranslatedMenuName(menuName)
        return g.app.realMenuNameDict.get(cmn, menuName)

    def setRealMenuName(self, untrans, trans):
        cmn = self.canonicalizeTranslatedMenuName(untrans)
        g.app.realMenuNameDict[cmn] = trans

    def setRealMenuNamesFromTable(self, table):
        try:
            for untrans, trans in table:
                self.setRealMenuName(untrans, trans)
        except Exception:
            g.es("exception in", "setRealMenuNamesFromTable")
            g.es_exception()
    #@+node:ekr.20031218072017.3807: *4* LeoMenu.getMenu, setMenu, destroyMenu
    def getMenu(self, menuName):
        cmn = self.canonicalizeMenuName(menuName)
        return self.menus.get(cmn)

    def setMenu(self, menuName, menu):
        cmn = self.canonicalizeMenuName(menuName)
        self.menus[cmn] = menu

    def destroyMenu(self, menuName):
        cmn = self.canonicalizeMenuName(menuName)
        del self.menus[cmn]
    #@+node:ekr.20031218072017.3808: *3* LeoMenu.Must be overridden in menu subclasses
    #@+node:ekr.20031218072017.3809: *4* LeoMenu.9 Routines with Tk spellings
    def add_cascade(self, parent, label, menu, underline):
        self.oops()

    def add_command(self, menu, **keys):
        self.oops()

    def add_separator(self, menu):
        self.oops()

    # def bind (self,bind_shortcut,callback):
    #     self.oops()

    def delete(self, menu, realItemName):
        self.oops()

    def delete_range(self, menu, n1, n2):
        self.oops()

    def destroy(self, menu):
        self.oops()

    def insert(
        self, menuName, position, label, command, underline=None):  # New in Leo 4.4.3 a1
        self.oops()

    def insert_cascade(self, parent, index, label, menu, underline):
        self.oops()

    def new_menu(self, parent, tearoff=0, label=''):
        # 2010: added label arg for pylint.
        self.oops()
    #@+node:ekr.20031218072017.3810: *4* LeoMenu.9 Routines with new spellings
    def activateMenu(self, menuName):  # New in Leo 4.4b2.
        self.oops()

    def clearAccel(self, menu, name):
        self.oops()

    def createMenuBar(self, frame):
        self.oops()

    def createOpenWithMenu(self, parent, label, index, amp_index):
        self.oops()

    def disableMenu(self, menu, name):
        self.oops()

    def enableMenu(self, menu, name, val):
        self.oops()

    def getMacHelpMenu(self, table):
        return None

    def getMenuLabel(self, menu, name):
        self.oops()

    def setMenuLabel(self, menu, name, label, underline=-1):
        self.oops()
    #@-others
#@+node:ekr.20031218072017.3811: ** class NullMenu
class NullMenu(LeoMenu):
    """A null menu class for testing and batch execution."""
    #@+others
    #@+node:ekr.20050104094308: *3* ctor (NullMenu)
    def __init__(self, frame):
        super().__init__(frame)
        self.isNull = True
    #@+node:ekr.20050104094029: *3* oops
    def oops(self):
        pass
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

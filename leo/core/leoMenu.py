#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3749: * @thin leoMenu.py
"""Gui-independent menu handling for Leo."""

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import leo.core.leoGlobals as g
import string
import sys

#@+others
#@+node:ekr.20031218072017.3750: ** class leoMenu
class leoMenu:

    """The base class for all Leo menus."""

    #@+others
    #@+node:ekr.20031218072017.3751: *3*  leoMenu.__init__
    def __init__ (self,frame):

        # g.trace('leoMenu',g.callers())

        self.c = c = frame.c
        self.frame = frame
        self.menus = {} # Menu dictionary.
        self.menuShortcuts = {}

        # static part of recent files menu
        self.recentFilesStatic = (
            ("Clear Recent Files",None,c.clearRecentFiles),
            ("Clean Recent Files",None,c.cleanRecentFiles),
            ("Sort Recent Files",None,c.sortRecentFiles),
            # ("-",None,None),
            )

        # To aid transition to emacs-style key handling.
        self.useCmdMenu = c.config.getBool('useCmdMenu')

        self.newBinding = True
            # True if using new binding scheme.
            # You can set this to False in an emergency to revert to the old way.

        if 0: # Must be done much later.
            self.defineMenuTables()
    #@+node:ekr.20031218072017.3775: *3* error and oops
    def oops (self):

        g.pr("leoMenu oops:", g.callers(4), "should be overridden in subclass")

    def error (self,s):

        g.es_print('',s,color='red')
    #@+node:ekr.20031218072017.3776: *3* Gui-independent menu enablers
    #@+node:ekr.20031218072017.3777: *4* updateAllMenus
    def updateAllMenus (self):

        """The Tk "postcommand" callback called when a click happens in any menu.

        Updates (enables or disables) all menu items."""

        # Allow the user first crack at updating menus.
        c = self.c

        if c and c.exists:
            c.setLog()
            p = c.p

            if not g.doHook("menu-update",c=c,p=p,v=p):
                self.updateFileMenu()
                self.updateEditMenu()
                self.updateOutlineMenu()
    #@+node:ekr.20031218072017.3778: *4* updateFileMenu
    def updateFileMenu (self):

        c = self.c ; frame = c.frame
        if not c: return

        try:
            enable = frame.menu.enableMenu
            menu = frame.menu.getMenu("File")
            if menu:
                enable(menu,"Revert To Saved", c.canRevert())
                enable(menu,"Open With...", g.app.hasOpenWithMenu)
        except:
            g.es("exception updating File menu")
            g.es_exception()
    #@+node:ekr.20031218072017.836: *4* updateEditMenu
    def updateEditMenu (self):

        c = self.c ; frame = c.frame
        w = c.frame.body.bodyCtrl
        if not c: return
        try:
            # Top level Edit menu...
            enable = frame.menu.enableMenu
            menu = frame.menu.getMenu("Edit")
            c.undoer.enableMenuItems()
            #@+        << enable cut/paste >>
            #@+node:ekr.20040130164211: *5* << enable cut/paste >>
            if frame.body.hasFocus():
                data = w.getSelectedText()
                canCut = data and len(data) > 0
            else:
                # This isn't strictly correct, but we can't get the Tk headline selection.
                canCut = True

            enable(menu,"Cut",canCut)
            enable(menu,"Copy",canCut)

            data = g.app.gui.getTextFromClipboard()
            canPaste = data and len(data) > 0
            enable(menu,"Paste",canPaste)
            #@-        << enable cut/paste >>
            if 0: # Always on for now.
                menu = frame.menu.getMenu("Find...")
                enable(menu,"Find Next",c.canFind())
                flag = c.canReplace()
                enable(menu,"Replace",flag)
                enable(menu,"Replace, Then Find",flag)
            # Edit Body submenu...
            menu = frame.menu.getMenu("Edit Body...")
            if menu:
                enable(menu,"Extract Section",c.canExtractSection())
                enable(menu,"Extract Names",c.canExtractSectionNames())
                enable(menu,"Extract",c.canExtract())
                enable(menu,"Match Brackets",c.canFindMatchingBracket())
        except:
            g.es("exception updating Edit menu")
            g.es_exception()
    #@+node:ekr.20031218072017.3779: *4* updateOutlineMenu
    def updateOutlineMenu (self):

        c = self.c ; frame = c.frame
        if not c: return

        p = c.p
        hasParent = p.hasParent()
        hasBack = p.hasBack()
        hasNext = p.hasNext()
        hasChildren = p.hasChildren()
        isExpanded = p.isExpanded()
        isCloned = p.isCloned()
        isMarked = p.isMarked()

        try:
            enable = frame.menu.enableMenu
            #@+        << enable top level outline menu >>
            #@+node:ekr.20040131171020: *5* << enable top level outline menu >>
            menu = frame.menu.getMenu("Outline")
            if menu:
                enable(menu,"Cut Node",c.canCutOutline())
                enable(menu,"Delete Node",c.canDeleteHeadline())
                enable(menu,"Paste Node",c.canPasteOutline())
                enable(menu,"Paste Node As Clone",c.canPasteOutline())
                enable(menu,"Clone Node",c.canClone()) # 1/31/04
                enable(menu,"Sort Siblings",c.canSortSiblings())
                enable(menu,"Hoist",c.canHoist())
                enable(menu,"De-Hoist",c.canDehoist())
            #@-        << enable top level outline menu >>
            #@+        << enable expand/contract submenu >>
            #@+node:ekr.20040131171020.1: *5* << enable expand/Contract submenu >>
            menu = frame.menu.getMenu("Expand/Contract...")
            if menu:
                enable(menu,"Contract Parent",c.canContractParent())
                enable(menu,"Contract Node",hasChildren and isExpanded)
                enable(menu,"Contract Or Go Left",(hasChildren and isExpanded) or hasParent)
                enable(menu,"Expand Node",hasChildren and not isExpanded)
                enable(menu,"Expand Prev Level",hasChildren and isExpanded)
                enable(menu,"Expand Next Level",hasChildren)
                enable(menu,"Expand To Level 1",hasChildren and isExpanded)
                enable(menu,"Expand Or Go Right",hasChildren)
                for i in range(2,9):
                    frame.menu.enableMenu(menu,"Expand To Level " + str(i), hasChildren)
            #@-        << enable expand/contract submenu >>
            #@+        << enable move submenu >>
            #@+node:ekr.20040131171020.2: *5* << enable move submenu >>
            menu = frame.menu.getMenu("Move...")
            if menu:
                enable(menu,"Move Down",c.canMoveOutlineDown())
                enable(menu,"Move Left",c.canMoveOutlineLeft())
                enable(menu,"Move Right",c.canMoveOutlineRight())
                enable(menu,"Move Up",c.canMoveOutlineUp())
                enable(menu,"Promote",c.canPromote())
                enable(menu,"Demote",c.canDemote())
            #@-        << enable move submenu >>
            #@+        << enable go to submenu >>
            #@+node:ekr.20040131171020.3: *5* << enable go to submenu >>
            menu = frame.menu.getMenu("Go To...")
            if menu:
                enable(menu,"Go To Prev Visited",c.nodeHistory.canGoToPrevVisited())
                enable(menu,"Go To Next Visited",c.nodeHistory.canGoToNextVisited())
                enable(menu,"Go To Prev Visible",c.canSelectVisBack())
                enable(menu,"Go To Next Visible",c.canSelectVisNext())
                if 0: # These are too slow.
                    enable(menu,"Go To Next Marked",c.canGoToNextMarkedHeadline())
                    enable(menu,"Go To Next Changed",c.canGoToNextDirtyHeadline())
                enable(menu,"Go To Next Clone",isCloned)
                enable(menu,"Go To Prev Node",c.canSelectThreadBack())
                enable(menu,"Go To Next Node",c.canSelectThreadNext())
                enable(menu,"Go To Parent",hasParent)
                enable(menu,"Go To Prev Sibling",hasBack)
                enable(menu,"Go To Next Sibling",hasNext)
            #@-        << enable go to submenu >>
            #@+        << enable mark submenu >>
            #@+node:ekr.20040131171020.4: *5* << enable mark submenu >>
            menu = frame.menu.getMenu("Mark/Unmark...")
            if menu:
                label = g.choose(isMarked,"Unmark","Mark")
                frame.menu.setMenuLabel(menu,0,label)
                enable(menu,"Mark Subheads",hasChildren)
                if 0: # These are too slow.
                    enable(menu,"Mark Changed Items",c.canMarkChangedHeadlines())
                    enable(menu,"Mark Changed Roots",c.canMarkChangedRoots())
                enable(menu,"Mark Clones",isCloned)
            #@-        << enable mark submenu >>
        except:
            g.es("exception updating Outline menu")
            g.es_exception()
    #@+node:ekr.20031218072017.3780: *4* hasSelection
    # Returns True if text in the outline or body text is selected.

    def hasSelection (self):

        c = self.c ; w = c.frame.body.bodyCtrl

        if c.frame.body:
            first,last = w.getSelectionRange()
            return first != last
        else:
            return False
    #@+node:ekr.20031218072017.3781: *3* Gui-independent menu routines
    #@+node:ekr.20060926213642: *4* capitalizeMinibufferMenuName
    def capitalizeMinibufferMenuName (self,s,removeHyphens):

        result = []
        for i in range(len(s)):
            ch = s[i]
            prev = i > 0 and s[i-1] or ''
            prevprev = i > 1 and s[i-2] or ''
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
    #@+node:ekr.20031218072017.3785: *4* createMenusFromTables & helpers
    def createMenusFromTables (self):

        c = self.c

        aList = c.config.getMenusList()
        if aList:
            self.createMenusFromConfigList(aList)
        else:
            self.defineMenuTables()

            self.createFileMenuFromTable()
            self.createEditMenuFromTable()
            self.createOutlineMenuFromTable()

            g.doHook("create-optional-menus",c=c)

            if self.useCmdMenu:
                self.createCmndsMenuFromTable()

            self.createWindowMenuFromTable()
            self.createHelpMenuFromTable()
    #@+node:ekr.20031218072017.3790: *5* createFileMenuFromTable
    def createFileMenuFromTable (self):

        c = self.c
        fileMenu = self.createNewMenu("&File")
        self.createMenuEntries(fileMenu,self.fileMenuTopTable)
        self.createNewMenu("Open &With...","File")
        self.createMenuEntries(fileMenu,self.fileMenuTop2Table)
        #@+    << create the recent files submenu >>
        #@+node:ekr.20031218072017.3791: *6* << create the recent files submenu >>
        self.createNewMenu("Recent &Files...","File")
        c.recentFiles = c.config.getRecentFiles()

        if 0: # Not needed, and causes problems in wxWindows...
            self.createRecentFilesMenuItems()
        #@-    << create the recent files submenu >>
        self.add_separator(fileMenu)
        #@+    << create the read/write submenu >>
        #@+node:ekr.20031218072017.3792: *6* << create the read/write submenu >>
        readWriteMenu = self.createNewMenu("&Read/Write...","File")

        self.createMenuEntries(readWriteMenu,self.fileMenuReadWriteMenuTable)
        #@-    << create the read/write submenu >>
        #@+    << create the tangle submenu >>
        #@+node:ekr.20031218072017.3793: *6* << create the tangle submenu >>
        tangleMenu = self.createNewMenu("Tan&gle...","File")

        self.createMenuEntries(tangleMenu,self.fileMenuTangleMenuTable)
        #@-    << create the tangle submenu >>
        #@+    << create the untangle submenu >>
        #@+node:ekr.20031218072017.3794: *6* << create the untangle submenu >>
        untangleMenu = self.createNewMenu("&Untangle...","File")

        self.createMenuEntries(untangleMenu,self.fileMenuUntangleMenuTable)
        #@-    << create the untangle submenu >>
        #@+    << create the import submenu >>
        #@+node:ekr.20031218072017.3795: *6* << create the import submenu >>
        importMenu = self.createNewMenu("&Import...","File")

        self.createMenuEntries(importMenu,self.fileMenuImportMenuTable)
        #@-    << create the import submenu >>
        #@+    << create the export submenu >>
        #@+node:ekr.20031218072017.3796: *6* << create the export submenu >>
        exportMenu = self.createNewMenu("&Export...","File")

        self.createMenuEntries(exportMenu,self.fileMenuExportMenuTable)
        #@-    << create the export submenu >>
        self.add_separator(fileMenu)
        self.createMenuEntries(fileMenu,self.fileMenuTop3MenuTable)
    #@+node:ekr.20031218072017.3786: *5* createEditMenuFromTable
    def createEditMenuFromTable (self):

        editMenu = self.createNewMenu("&Edit")
        self.createMenuEntries(editMenu,self.editMenuTopTable)

        #@+    << create the edit body submenu >>
        #@+node:ekr.20031218072017.3787: *6* << create the edit body submenu >>
        editBodyMenu = self.createNewMenu("Edit &Body...","Edit")

        self.createMenuEntries(editBodyMenu,self.editMenuEditBodyTable)
        #@-    << create the edit body submenu >>
        #@+    << create the edit headline submenu >>
        #@+node:ekr.20031218072017.3788: *6* << create the edit headline submenu >>
        editHeadlineMenu = self.createNewMenu("Edit &Headline...","Edit")

        self.createMenuEntries(editHeadlineMenu,self.editMenuEditHeadlineTable)
        #@-    << create the edit headline submenu >>
        #@+    << create the find submenu >>
        #@+node:ekr.20031218072017.3789: *6* << create the find submenu >>
        findMenu = self.createNewMenu("&Find...","Edit")

        self.createMenuEntries(findMenu,self.editMenuFindMenuTable)
        #@-    << create the find submenu >>

        self.createMenuEntries(editMenu,self.editMenuTop2Table)
    #@+node:ekr.20031218072017.3797: *5* createOutlineMenuFromTable
    def createOutlineMenuFromTable (self):

        outlineMenu = self.createNewMenu("&Outline")

        self.createMenuEntries(outlineMenu,self.outlineMenuTopMenuTable)

        #@+    << create check submenu >>
        #@+node:ekr.20040711140738.1: *6* << create check submenu >>
        checkOutlineMenu = self.createNewMenu("Chec&k...","Outline")

        self.createMenuEntries(checkOutlineMenu,self.outlineMenuCheckOutlineMenuTable)
        #@-    << create check submenu >>
        #@+    << create expand/contract submenu >>
        #@+node:ekr.20031218072017.3798: *6* << create expand/contract submenu >>
        expandMenu = self.createNewMenu("E&xpand/Contract...","Outline")

        self.createMenuEntries(expandMenu,self.outlineMenuExpandContractMenuTable)
        #@-    << create expand/contract submenu >>
        #@+    << create move submenu >>
        #@+node:ekr.20031218072017.3799: *6* << create move submenu >>
        moveSelectMenu = self.createNewMenu("&Move...","Outline")

        self.createMenuEntries(moveSelectMenu,self.outlineMenuMoveMenuTable)
        #@-    << create move submenu >>
        #@+    << create mark submenu >>
        #@+node:ekr.20031218072017.3800: *6* << create mark submenu >>
        markMenu = self.createNewMenu("M&ark/Unmark...","Outline")

        self.createMenuEntries(markMenu,self.outlineMenuMarkMenuTable)
        #@-    << create mark submenu >>
        #@+    << create goto submenu >>
        #@+node:ekr.20031218072017.3801: *6* << create goto submenu >>
        gotoMenu = self.createNewMenu("&Go To...","Outline")

        self.createMenuEntries(gotoMenu,self.outlineMenuGoToMenuTable)
        #@-    << create goto submenu >>
    #@+node:ekr.20050921103736: *5* createCmndsMenuFromTable
    def createCmndsMenuFromTable (self):

        cmdsMenu = self.createNewMenu('&Cmds')

        # Now in the minibuffer table.
            # Used in top table: q,u,x
            # self.createMenuEntries(cmdsMenu,self.cmdsMenuTopTable)

        for name,table in (
            # &: a,b,c,d,f,g,h,i,m,n,o,p,r,s,t,u
            ('&Abbrev...',          self.cmdsMenuAbbrevTable),
            ('Body E&ditors',       self.cmdsMenuBodyEditorsTable),
            ('&Buffers...',         self.cmdsMenuBuffersTable),
            ('&Chapters...',        self.cmdsMenuChaptersTable),
            ('C&ursor/Selection...',[]),
            ('&Focus...',           self.cmdsMenuFocusTable),
            ('&Macro...',           self.cmdsMenuMacroTable),
            ('M&inibuffer',         self.cmdsMenuMinibufferTable),
            #('&Panes...',           self.cmdsMenuPanesTable),
            ('&Pickers...',         self.cmdsMenuPickersTable),
            ('&Rectangles...',      self.cmdsMenuRectanglesTable),
            ('Re&gisters...',       self.cmdsMenuRegistersTable),
            ('R&un Script/Tests',   self.cmdsMenuRunTable),
            ('Scr&olling...',       self.cmdsMenuScrollTable),
            ('Spell C&heck...',     self.cmdsMenuSpellCheckTable),
            ('&Text Commands',      self.cmdsMenuTextTable),
            ('Toggle Setti&ngs',    self.cmdsMenuToggleTable),
        ):
            if table == self.cmdsMenuChaptersTable and not self.c.chapterController:
                continue
            menu = self.createNewMenu(name,'&Cmds')
            self.createMenuEntries(menu,table)

        for name,table in (
            # &: b,e,f,s,t,x
            ('Cursor &Back...',                     self.cursorMenuBackTable),
            ('Cursor Back &Extend Selection...',    self.cursorMeuuBackExtendTable),
            ('Cursor Extend &To...',                self.cursorMenuExtendTable),
            ('Cursor &Forward...',                  self.cursorMenuForwardTable),
            ('Cursor Forward E&xtend Selection...', self.cursorMenuForwardExtendTable),
        ):
            menu = self.createNewMenu(name,'C&ursor/Selection...')
            self.createMenuEntries(menu,table)
    #@+node:ekr.20031218072017.3802: *5* createWindowMenuFromTable
    def createWindowMenuFromTable (self):

        windowMenu = self.createNewMenu("&Window")

        self.createMenuEntries(windowMenu,self.windowMenuTopTable)
    #@+node:ekr.20031218072017.3803: *5* createHelpMenuFromTable
    def createHelpMenuFromTable (self):

        if sys.platform == 'darwin':
            pass # self.getMacHelpMenu(table)
        else:
            helpMenu = self.createNewMenu("&Help")
            self.createMenuEntries(helpMenu,self.helpMenuTable)
    #@+node:ekr.20070926135612: *5* createMenusFromConfigList & helpers
    def createMenusFromConfigList (self,aList):

        '''Create menus from aList instead of 'hard coded' menus.
        The 'top' menu has already been created.'''

        tag = '@menu'
        for z in aList:
            kind,val,val2 = z
            if kind.startswith(tag):
                name = kind[len(tag):].strip()
                if not self.handleSpecialMenus(name,parentName=None):
                    self.createNewMenu(name) # Create top-level menu.
                    self.createMenuFromConfigList(name,val,level=0)
            else:
                self.error('%s %s not valid outside @menu tree' % (kind,val))
    #@+node:ekr.20070927082205: *6* createMenuFromConfigList
    def createMenuFromConfigList (self,parentName,aList,level=0):

        table = [] ; parentMenu = self.getMenu(parentName)

        for z in aList:
            kind,val,val2 = z
            if kind.startswith('@menu'):
                # Menu names can be unicode without any problem.
                name = kind[5:].strip()
                if table:
                    self.createMenuEntries(parentMenu,table)
                if not self.handleSpecialMenus(name,parentName,table):
                    self.createNewMenu(name,parentName) # Create submenu of parent menu.
                    self.createMenuFromConfigList(name,val,level+1)
                table = []
            elif kind == '@item':
                name = str(val) # Item names must always be ascii.
                if val2:
                    # Translated names can be unicode.
                    table.append((val2,name),)
                else:
                    table.append(name)
            else:
                g.trace('can not happen: bad kind:',kind)

        if table:
            self.createMenuEntries(parentMenu,table)
    #@+node:ekr.20070927172712: *6* handleSpecialMenus
    def handleSpecialMenus (self,name,parentName,table=None):

        '''Handle a special menu if name is the name of a special menu.
        return True if this method handles the menu.'''

        c = self.c
        if table is None: table = []
        name2 = name.replace('&','').replace(' ','').lower()

        if name2 == 'plugins':
            # Create the plugins menu using a hook.
            g.doHook("create-optional-menus",c=c)
            return True
        elif name2.startswith('recentfiles'):
            # Just create the menu.  createRecentFilesMenuItems will be called later.
            self.createNewMenu(name,parentName)
            c.recentFiles = c.config.getRecentFiles()
            return True
        elif name2 == 'help' and sys.platform == 'darwin':
            helpMenu = self.getMacHelpMenu(table)
            return helpMenu is not None
        else:
            return False
    #@+node:ekr.20031218072017.3752: *4* defineMenuTables & helpers
    def defineMenuTables (self):

        self.defineEditMenuTables()
        self.defineFileMenuTables()
        self.defineOutlineMenuTables()
        self.defineWindowMenuTables()

        if self.useCmdMenu:
            self.defineCmdsMenuTables()

        self.defineHelpMenuTables()

    #@+node:ekr.20031218072017.3753: *5* defineEditMenuTables & helpers
    def defineEditMenuTables (self):

        self.defineEditMenuTopTable()
        self.defineEditMenuEditBodyTable()
        self.defineEditMenuEditHeadlineTable()
        self.defineEditMenuFindMenuTable()
        self.defineEditMenuTop2Table()
    #@+node:ekr.20031218072017.839: *6* defineEditMenuTopTable
    def defineEditMenuTopTable (self):

        self.editMenuTopTable = [
            # &: u,r reserved for undo/redo: a,d,p,t,y.
            # & (later): e,g,n,v.
            ("Can't Undo",'undo'),
            ("Can't Redo",'redo'), 
            '-',
            ('Cu&t','cut-text'),
            ('Cop&y','copy-text'),
            ('&Paste','paste-text'),
            ('&Delete','backward-delete-char'),
            ('Select &All','select-all'),
            '-',
        ]
    #@+node:ekr.20031218072017.3754: *6* defineEditMenuEditBodyTable
    def defineEditMenuEditBodyTable (self):

        self.editMenuEditBodyTable = [
            # Shortcuts a,b,d,e,i,l,m,n,r,s,t,u
            '*extract-&section',
            '*extract-&names',
            '*&extract',
            '-',
            '*convert-all-b&lanks',
            '*convert-all-t&abs',
            '*convert-&blanks',
            '*convert-&tabs',
            '*insert-body-&time',
            '*&reformat-paragraph',
            '-',
            '*&indent-region',
            '*&unindent-region',
            '*&match-brackets',
            '*add-comments',
            '*delete-comments',
        ]
    #@+node:ekr.20031218072017.3755: *6* defineEditMenuEditHeadlineTable
    def defineEditMenuEditHeadlineTable (self):

        self.editMenuEditHeadlineTable = [
            '*edit-&headline',
            '*&end-edit-headline',
            '*&abort-edit-headline',
            '*insert-headline-&time',
            '*toggle-&angle-brackets',
        ]
    #@+node:ekr.20031218072017.3756: *6* defineEditMenuFindMenuTable
    def defineEditMenuFindMenuTable (self):

        self.editMenuFindMenuTable = [
            # &: a,b,c,d,e,f,h,i,l,n,o,p,q,r,s,u,w,x
            '*&open-find-tab',
            '*&hide-find-tab',
            '*search-&with-present-options',
            '-',
            '*find-&next',
            '*find-&prev',
            '*&change',
            '*find-&all',
            '*clone-fi&nd-all',
            '*change-a&ll',
            '-',
            '*&find-character',
            '*find-character-extend-&selection',
            '*&backward-find-character',
            '*backward-find-character-&extend-selection',
            '-',
            '*&isearch-forward',
            '*isea&rch-backward',
            '*isearch-forward-rege&xp',
            '*isearch-backward-regex&p',
            '-',
            '*&query-replace',
            '*q&uery-replace-regex',
        ]
    #@+node:ekr.20031218072017.3757: *6* defineEditMenuTop2Table
    def defineEditMenuTop2Table (self):

        c = self.c

        try:        show = c.frame.body.getColorizer().showInvisibles
        except:     show = False
        label = g.choose(show,"Hide In&visibles","Show In&visibles")

        self.editMenuTop2Table = [
            '*&goto-global-line',
            '*&execute-script',
            (label,'toggle-invisibles'),
            ("Setti&ngs",'open-leoSettings-leo'),
        ]

        # Top-level shortcuts earlier: a,d,p,t,u,y,z
        # Top-level shortcuts here: e,g,n,v
    #@+node:ekr.20031218072017.3758: *5* defineFileMenuTables & helpers
    def defineFileMenuTables (self):

        self.defineFileMenuTopTable()
        self.defineFileMenuTop2Table()
        self.defineFileMenuReadWriteMenuTable()
        self.defineFileMenuTangleMenuTable()
        self.defineFileMenuUntangleMenuTable()
        self.defineFileMenuImportMenuTable()
        self.defineFileMenuExportMenuTable()
        self.defineFileMenuTop3MenuTable()
    #@+node:ekr.20031218072017.3759: *6* defineFileMenuTopTable
    def defineFileMenuTopTable (self):

        self.fileMenuTopTable = [
            '*&new',
            ('&Open...','open-outline'),
        ]
    #@+node:ekr.20031218072017.3760: *6* defineFileMenuTop2Table
    def defineFileMenuTop2Table (self):

        self.fileMenuTop2Table = [
            '-',
            ('&Close','close-window'),
            ('&Save','save-file'),
            ('Save &As','save-file-as'),
            ('Save As &Unzipped','save-file-as-unzipped'),
            ('Save As &Zipped','save-file-as-zipped'),
            ('Save &To','save-file-to'),
            ('Re&vert To Saved','revert'),
        ]
    #@+node:ekr.20031218072017.3761: *6* defineFileMenuReadWriteMenuTable
    def defineFileMenuReadWriteMenuTable (self):

        self.fileMenuReadWriteMenuTable = [
            '*&check-derived-file',
            '*check-leo-file',
            '-',
            '*&read-outline-only',
            '*write-&outline-only',
            '-',
            '*read-&file-into-node',
            '*writ&e-file-from-node',
            '-',
            ('Read @&auto Nodes','read-at-auto-nodes'),
            ('Write @a&uto Nodes','write-at-auto-nodes'),
            ('Write D&irty @a&uto Nodes','write-dirty-at-auto-nodes'),
            '-',
            ('Read @file &Nodes','read-at-file-nodes'),
            ('Write &Dirty @file Nodes','write-dirty-at-file-nodes'),
            ('Write &Missing @file Nodes','write-missing-at-file-nodes'),
            ('&Write @file Nodes','write-at-file-nodes'),
        ]

        # a,cd,e,f,i,l,m,n,o,r,u,w
    #@+node:ekr.20031218072017.3762: *6* defineFileMenuTangleMenuTable
    def defineFileMenuTangleMenuTable (self):

        self.fileMenuTangleMenuTable = [
            '*tangle-&all',
            '*tangle-&marked',
            '*&tangle',
        ]
    #@+node:ekr.20031218072017.3763: *6* defineFileMenuUntangleMenuTable
    def defineFileMenuUntangleMenuTable (self):

        self.fileMenuUntangleMenuTable = [
            '*untangle-&all',
            '*untangle-&marked',
            '*&untangle',
        ]
    #@+node:ekr.20031218072017.3764: *6* defineFileMenuImportMenuTable
    def defineFileMenuImportMenuTable (self):

        self.fileMenuImportMenuTable = [
            #&: c,d,f,n,o,r,
            '*import-&derived-file',
            ('Import To @&file','import-at-file'),
            ('Import To @&root','import-at-root'),
            '*import-&cweb-files',
            '*import-&noweb-files',
            '*import-flattened-&outline',
        ]
    #@+node:ekr.20031218072017.3765: *6* defineFileMenuExportMenuTable
    def defineFileMenuExportMenuTable (self):

        self.fileMenuExportMenuTable = [
            '*export-&headlines',
            '*outline-to-&cweb',
            '*outline-to-&noweb',
            '*&flatten-outline',
            '*&remove-sentinels',
            '*&weave',
        ]
    #@+node:ekr.20031218072017.3766: *6* defineFileMenuTop3MenuTable
    def defineFileMenuTop3MenuTable (self):

        self.fileMenuTop3MenuTable = [
            ('E&xit','exit-leo'),
        ]
    #@+node:ekr.20031218072017.3767: *5* defineOutlineMenuTables & helpers
    def defineOutlineMenuTables (self):

        self.defineOutlineMenuTopMenuTable()
        self.defineOutlineMenuCheckOutlineMenuTable()
        self.defineOutlineMenuExpandContractMenuTable()
        self.defineOutlineMenuMoveMenuTable()
        self.defineOutlineMenuMarkMenuTable()
        self.defineOutlineMenuGoToMenuTable()
    #@+node:ekr.20031218072017.3768: *6* defineOutlineMenuTopMenuTable
    def defineOutlineMenuTopMenuTable (self):

        self.outlineMenuTopMenuTable = [
            '*c&ut-node',
            '*c&opy-node',
            '*&paste-node',
            ('Pas&te Node As Clone','paste-retaining-clones'),
            '*&delete-node',
            '-',
            '*&insert-node',
            '*&clone-node',
            '*sort-childre&n',
            '*&sort-siblings',
            '-',
            '*&hoist',
            ('D&e-Hoist','de-hoist'), # To preserve the '-' in De-Hoist.
            '-',
        ]
        # Ampersand bindings:  a,b,c,d,e,h,i,n,o,p,t,s,y
        # Bindings for entries that go to submenus: a,g,k,m,x
    #@+node:ekr.20040711140738: *6* defineOutlineMenuCheckOutlineMenuTable
    def defineOutlineMenuCheckOutlineMenuTable (self):

        self.outlineMenuCheckOutlineMenuTable = [
            # &: a,c,d,l,o
            '*check-&outline',
            '*&dump-outline',
            '-',
            '*compare-&leo-files',
            '-',
            '*check-&all-python-code',
            '*&check-python-code',
        ]
    #@+node:ekr.20031218072017.3769: *6* defineOutlineMenuExpandContractMenuTable
    def defineOutlineMenuExpandContractMenuTable (self):

        self.outlineMenuExpandContractMenuTable = [
            '*&contract-all',
            '*contract-&node',
            '*contract-&parent',
            '*contract-or-go-&left',
            '-',
            '*expand-p&rev-level',
            '*expand-n&ext-level',
            '*expand-and-go-right',
            '*expand-or-go-right',
            '-',
            '*expand-to-level-&1',
            '*expand-to-level-&2',
            '*expand-to-level-&3',
            '*expand-to-level-&4',
            '*expand-to-level-&5',
            '*expand-to-level-&6',
            '*expand-to-level-&7',
            '*expand-to-level-&8',
            '-',
            '*expand-&all',
            '*expand-n&ode',
        ]
    #@+node:ekr.20031218072017.3770: *6* defineOutlineMenuMoveMenuTable
    def defineOutlineMenuMoveMenuTable (self):

        self.outlineMenuMoveMenuTable = [
            ('Move &Down','move-outline-down'),
            ('Move &Left','move-outline-left'),
            ('Move &Right','move-outline-right'),
            ('Move &Up','move-outline-up'),
            '-',
            '*&promote',
            '*&demote',
        ]
    #@+node:ekr.20031218072017.3771: *6* defineOutlineMenuMarkMenuTable
    def defineOutlineMenuMarkMenuTable (self):

        self.outlineMenuMarkMenuTable = [
            '*&mark',
            '*mark-&subheads',
            '*mark-changed-&items',
            '*mark-changed-&roots',
            '*mark-&clones',
            '*&unmark-all',
        ]
    #@+node:ekr.20031218072017.3772: *6* defineOutlineMenuGoToMenuTable
    def defineOutlineMenuGoToMenuTable (self):

        self.outlineMenuGoToMenuTable = [
            # &: a,b,c,d,e,f,g,h,i,l,m,n,o,p,r,s,t,v,
            ('Go To &First Node','goto-first-node'),
            ('Go To First V&isible','goto-first-visible-node'),
            ('Go To First Si&bling','goto-first-sibling'),
            '-',
            ('Go To Next C&hanged','goto-next-changed'),
            ('Go To Next &Clone','goto-next-clone'),
            ('Go To Next &Marked','goto-next-marked'),
            ('Go To Next N&ode','goto-next-node'),
            ('Go To Next &Sibling','goto-next-sibling'),
            ('Go To Next Visibl&e','goto-next-visible'),
            ('Go To Next Visite&d','go-forward'),
            '-',
            ('Go To P&arent','goto-parent'),
            '-',
            ('Go To &Prev Node','goto-prev-node'),
            ('Go To P&rev Sibling','goto-prev-sibling'),
            ('Go To Pre&v Visible','goto-prev-visible'),
            ('Go To Prev Visi&ted','go-back'),
            '-',
            ('Go To Last Node','goto-last-node'),
            ('Go To Last Siblin&g','goto-last-sibling'),
            ('Go To &Last Visible','goto-last-visible-node'),
        ]
    #@+node:ekr.20050921103230: *5* defineCmdsMenuTables & helpers
    def defineCmdsMenuTables (self):

        self.defineCmdsMenuAbbrevTable()
        self.defineCmdsMenuBodyEditorsTable()
        self.defineCmdsMenuBuffersTable()
        self.defineCmdsMenuChaptersTable()
        self.defineCmdsMenuCursorTable()
        self.defineCmdsMenuFocusTable()
        self.defineCmdsMenuMacroTable()
        self.defineCmdsMenuMinibufferTable()
        self.defineCmdsMenuPickersTable()
        self.defineCmdsMenuRectanglesTable()
        self.defineCmdsMenuRegistersTable()
        self.defineCmdsMenuRunTable()
        self.defineCmdsMenuScrollTable()
        self.defineCmdsMenuSpellCheckTable()
        self.defineCmdsMenuTextTable()
        self.defineCmdsMenuToggleTable()
    #@+node:ekr.20060117094955.1: *6* defineCmdsMenuAbbrevTable
    def defineCmdsMenuAbbrevTable (self):

        self.cmdsMenuAbbrevTable = [
            # &: a,e,i,k,l,r,w,v
            'abbre&v-mode',
            '-',
            '&list-abbrevs',
            '&read-abbrev-file',
            '&write-abbrev-file',
            '-',
            '&add-global-abbrev',
            '&inverse-add-global-abbrev',
            '&kill-all-abbrevs',
            # '-',
            # 'expand-abbrev', # Not a command
            # '&expand-region-abbrevs',
        ]
    #@+node:ekr.20060912093104: *6* defineCmdsMenuBodyEditorsTable
    def defineCmdsMenuBodyEditorsTable (self):

        self.cmdsMenuBodyEditorsTable = [
            # &: a,c,d
            '&add-editor',
            '&cycle-editor-focus',
            '&delete-editor',
        ]
    #@+node:ekr.20060117095212: *6* defineCmdsMenuBufferTable
    def defineCmdsMenuBuffersTable (self):

        self.cmdsMenuBuffersTable = [
            '&append-to-buffer',
            '&kill-buffer',
            'list-&buffers',
            '&list-buffers-alphabetically',
            '&prepend-to-buffer',
            '&rename-buffer',
            '&switch-to-buffer',
        ]
    #@+node:ekr.20070604205927: *6* defineCmdsMenuChaptersTable
    def defineCmdsMenuChaptersTable (self):

        self.cmdsMenuChaptersTable = [
            '&clone-node-to-chapter',
            'c&opy-node-to-chapter',
            'c&reate-chapter',
            '&move-node-to-chapter',
            '&remove-chapter',
            '&select-chapter',
        ]
    #@+node:ekr.20060924124119: *6* defineCmdsMenuCursorTable
    def defineCmdsMenuCursorTable (self):

        self.cursorMenuBackTable = [
            # &: b,c,l,p,s,v,w
            'back-&char',
            'back-&paragraph',
            'back-&sentence',
            'back-&word',
            '-',
            'beginning-of-&buffer',
            'beginning-of-&line',
            '-',
            'pre&vious-line',
        ]

        self.cursorMeuuBackExtendTable = [
            # &: b,c,l,p,s,v,w
            'back-&char-extend-selection',
            'back-&paragraph-extend-selection',
            'back-&sentence-extend-selection',
            'back-&word-extend-selection',
            '-',
            'beginning-of-&buffer-extend-selection',
            'beginning-of-&line-extend-selection',
            '-',
            'pre&vious-line-extend-selection',
        ]

        self.cursorMenuExtendTable = [
            # &: l,p,s,w
            'extend-to-&line',
            'extend-to-&paragraph',
            'extend-to-&sentence',
            'extend-to-&word',
        ]

        self.cursorMenuForwardTable = [
            # &: b,c,e,l,n,p,s,w
            'end-of-&buffer',
            'end-of-&line',
            '-',
            'forward-&char',
            'forward-&paragraph',
            'forward-&sentence',
            'forward-&end-word',
            'forward-&word',
            '-',
            '&next-line',
        ]

        self.cursorMenuForwardExtendTable = [
            # &: b,c,e,l,n,p,s,w
            'end-of-&buffer-extend-selection',
            'end-of-&line-extend-selection',
            '-',
            'forward-&char-extend-selection',
            'forward-&paragraph-extend-selection',
            'forward-&sentence-extend-selection',
            'forward-&end-word-extend-selection',
            'forward-&word-extend-selection',#
            '-',
            '&next-line-extend-selection',    
        ]
    #@+node:ekr.20060923060822: *6* defineCmdsMenuFocusTable
    def defineCmdsMenuFocusTable (self):

        self.cmdsMenuFocusTable = [
            '&cycle-all-focus',
            'focus-to-&body',          
            'focus-to-&log',             
            'focus-to-&minibuffer',     
            'focus-to-&tree',             
        ]
    #@+node:ekr.20060117114315: *6* defineCmdsMenuMacroTable
    def defineCmdsMenuMacroTable (self):

        self.cmdsMenuMacroTable = [
            '&load-file',
            '-',
            '&start-kbd-macro',
            # '&end-kbd-macro',
            '&name-last-kbd-macro',
            '-',
            '&call-last-kbd-macro',
            # '&insert-kbd-macro',
        ]
    #@+node:ekr.20061011084101.1: *6* defineCmdsMenuMinibufferTable
    def defineCmdsMenuMinibufferTable (self):

        self.cmdsMenuMinibufferTable = [
            # &: f,h,i,q,r,s,v
            '&full-command',
            'keyboard-&quit',
            '&repeat-complex-command',
            '&view-lossage',
            '-',
            '&show-mini-buffer',
            'h&ide-mini-buffer',
            '-',
            '&help-for-minibuffer',
        ]
    #@+node:ekr.20061011085641: *6* defineCmdsMenuPickersTable
    def defineCmdsMenuPickersTable (self):

        self. cmdsMenuPickersTable = [
            'show-&colors',
            'show-find-&options',
            'show-&fonts',
        ]
    #@+node:ekr.20060117095212.2: *6* defineCmdsMenuRectanglesTable
    def defineCmdsMenuRectanglesTable (self):

        self.cmdsMenuRectanglesTable = [
            '&clear-rectangle',
            'c&lose-rectangle',
            '&delete-rectangle',
            '&kill-rectangle',
            '&open-rectangle',
            '&string-rectangle',
            '&yank-rectangle',
        ]
    #@+node:ekr.20060117095212.1: *6* defineCmdsMenuRegistersTable
    def defineCmdsMenuRegistersTable (self):

        self.cmdsMenuRegistersTable = [
            # &: a,c,e,i,j,n,p,r,v
            '&append-to-register',
            'copy-r&ectangle-to-register',
            '&copy-to-register',
            'i&ncrement-register',
            '&insert-register',
            '&jump-to-register',
            # 'number-to-register',
            '&point-to-register',
            'p&repend-to-register',
            '&view-register',
        ]
    #@+node:ekr.20061119061958: *6* defineCmdsMenuRunTable
    def defineCmdsMenuRunTable (self):

        self.cmdsMenuRunTable = [
        # &: e,r
        '&execute-script',
        '&run-unit-tests',
        ]
    #@+node:ekr.20060923060822.1: *6* defineCmdsMenuScrollTable
    def defineCmdsMenuScrollTable (self):

        self.cmdsMenuScrollTable = [
            # &: c,d,e,f,l,o,p,r,v,x
            'scroll-outline-down-&line',
            'scroll-outline-down-&page',
            'scroll-outline-le&ft',
            'scroll-outline-&right',
            's&croll-outline-up-line',
            'scr&oll-outline-up-page',
            '-',
            'scroll-down-half-page',
            'scroll-down-line',
            'scroll-&down-page',
            'scroll-up-half-page',
            'scroll-up-line',
            'scroll-&up-page',
        ]
    #@+node:ekr.20060117095212.7: *6* defineCmdsMenuSpellCheckTable
    def defineCmdsMenuSpellCheckTable (self):

        self.cmdsMenuSpellCheckTable = [
            '&open-spell-tab',
            'spell-&change',
            'spell-change-&then-find',
            'spell-&find',
            'spell-&ignore',
        ]
    #@+node:ekr.20060924161901: *6* defineCmdsMenuTextTable
    def defineCmdsMenuTextTable (self):

        self.cmdsMenuTextTable = [
            # &: a,b,c,d,e,f,g,i,l,m,n,o,p,r,s,u
            '&beautify',
            'beautify-&all',
            '-',
            'center-&line',
            'center-&region',
            '-',
            '&capitalize-word',
            '&downcase-word',
            '&upcase-word',
            '-',
            'd&owncase-region',
            'u&pcase-region',
            '-',
            '&indent-region',
            'indent-r&elative',
            'indent-ri&gidly',
            'u&nindent-region',
            '-',
            'sort-colu&mns',
            'sort-&fields',
            '&sort-lines',
        ]
    #@+node:ekr.20060926161940: *6* defineCmdsMenuToggleTable
    def defineCmdsMenuToggleTable (self):

        self.cmdsMenuToggleTable = [
            # &: d,e,m,s,t,u,v
            'toggle-a&utocompleter',
            'toggle-call&tips',
            'toggle-&extend-mode',
            'toggle-input-&state',
            'toggle-in&visibles',
            'toggle-&mini-buffer',
            'toggle-split-&direction',
            '-',
            # &: a,b,c,f,h,i,r,w,x
            'toggle-find-&ignore-case-option',
            'toggle-find-in-&body-option',
            'toggle-find-in-&headline-option',
            'toggle-find-mark-&changes-option',
            'toggle-find-mark-&finds-option',
            'toggle-find-rege&x-option',
            'toggle-find-&reverse-option',
            'toggle-find-&word-option',
            'toggle-find-wrap-&around-option',
        ]
    #@+node:ekr.20031218072017.3773: *5* defineWindowMenuTables
    def defineWindowMenuTables (self):

        self.windowMenuTopTable = [
            # &: a,b,c,d,e,f,l,m,n,o,p,r,s,t,u,w,x,y
            '*&equal-sized-panes',
            '*&toggle-active-pane',
            '*toggle-&split-direction',
            '-',
            '*contract-&body-pane',
            '*contract-&log-pane',
            '*contract-&outline-pane',
            '*contract-&pane',
            '-',
            '*expand-bo&dy-pane',
            '*expand-lo&g-pane',
            '*expand-o&utline-pane',
            '*expand-pa&ne',
            '-',
            '*&fully-expand-body-pane',
            '*full&y-expand-log-pane',
            '*fully-e&xpand-outline-pane',
            '*fully-exp&and-pane',
            '-',
            '*&resize-to-screen',
            '*&cascade-windows',
            '*&minimize-all',
            '-',
            '*open-compare-window',
            '*open-python-&window',
        ]
    #@+node:ekr.20031218072017.3774: *5* defineHelpMenuTables
    def defineHelpMenuTables (self):

        self.helpMenuTable = [
            # &: a,b,c,d,e,f,h,l,m,n,o,p,r,s,t,u
            ('&About Leo...',           'about-leo'),
            ('Online &Home Page',       'open-online-home'),
            '*open-online-&tutorial',
            '*open-&users-guide',
            '-',
            ('Open Leo&Docs.leo',       'open-leoDocs-leo'),
            ('Open Leo&Plugins.leo',    'open-leoPlugins-leo'),
            ('Open Leo&Settings.leo',   'open-leoSettings-leo'),
            ('Open &myLeoSettings.leo', 'open-myLeoSettings-leo'),
            ('Open scr&ipts.leo',       'open-scripts-leo'),
            '-',
            '*he&lp-for-minibuffer',
            '*help-for-&command',
            '-',
            '*&apropos-autocompletion',
            '*apropos-&bindings',
            '*apropos-&debugging-commands',
            '*apropos-&find-commands',
            '-',
            '*pri&nt-bindings',
            '*print-c&ommands',
        ]
    #@+node:ekr.20051022053758.1: *3* Helpers
    #@+node:ekr.20031218072017.3783: *4* canonicalizeMenuName & cononicalizeTranslatedMenuName
    def canonicalizeMenuName (self,name):

        return ''.join([ch for ch in name.lower() if ch.isalnum()])

    def canonicalizeTranslatedMenuName (self,name):

        return ''.join([ch for ch in name.lower() if ch not in '& \t\n\r'])
    #@+node:ekr.20051022044950: *4* computeOldStyleShortcutKey
    def computeOldStyleShortcutKey (self,s):

        '''Compute the old-style shortcut key for @shortcuts entries.'''

        return ''.join([ch for ch in s.strip().lower() if ch.isalnum()])
    #@+node:ekr.20031218072017.1723: *4* createMenuEntries
    def createMenuEntries (self,menu,table,dynamicMenu=False):

        '''Create a menu entry from the table.
        New in 4.4: this method shows the shortcut in the menu,
        but this method **never** binds any shortcuts.'''

        c = self.c ; f = c.frame ; k = c.k
        if g.app.unitTesting: return

        trace = False
        for data in table:
            #@+        << get label & command or continue >>
            #@+node:ekr.20051021091958: *5* << get label & command or continue >>
            if g.isString(data):
                # New in Leo 4.4.2: Can use the same string for both the label and the command string.
                ok = True
                s = data
                removeHyphens = s and s[0]=='*'
                if removeHyphens: s = s[1:]
                label = self.capitalizeMinibufferMenuName(s,removeHyphens)
                command = s.replace('&','').lower()
                if label == '-':
                    self.add_separator(menu)
                    continue # That's all.
            else:
                ok = type(data) in (type(()), type([])) and len(data) in (2,3)
                if ok:
                    if len(data) == 2:
                        # New in 4.4b2: command can be a minibuffer-command name (a string)
                        label,command = data
                    else:
                        # New in 4.4: we ignore shortcuts bound in menu tables.
                        label,junk,command = data

                    if label in (None,'-'):
                        self.add_separator(menu)
                        continue # That's all.
                else:
                    g.trace('bad data in menu table: %s' % repr(data))
                    continue # Ignore bad data
            #@-        << get label & command or continue >>
            #@+        << compute commandName & accel from label & command >>
            #@+node:ekr.20031218072017.1725: *5* << compute commandName & accel from label & command >>
            # New in 4.4b2: command can be a minibuffer-command name (a string)
            minibufferCommand = type(command) == type('')
            accel = None
            if minibufferCommand:
                commandName = command 
                command = c.commandsDict.get(commandName)
                if command:
                    rawKey,bunchList = c.config.getShortcut(commandName)
                    # Pick the first entry that is not a mode.
                    for bunch in bunchList:
                        if not bunch.pane.endswith('-mode'):
                            accel = bunch and bunch.val
                            if bunch.pane  == 'text': break # New in Leo 4.4.2: prefer text bindings.
                else:
                    if not g.app.unitTesting and not dynamicMenu:
                        # Don't warn during unit testing.
                        # This may come from a plugin that normally isn't enabled.
                        if trace: g.trace('No inverse for %s' % commandName)
                    continue # There is no way to make this menu entry.
            else:
                # First, get the old-style name.
                commandName = self.computeOldStyleShortcutKey(label)
                rawKey,bunchList = c.config.getShortcut(commandName)
                for bunch in bunchList:
                    if not bunch.pane.endswith('-mode'):
                        if trace: g.trace('2','%20s' % (bunch.val),commandName)
                        accel = bunch and bunch.val ; break
                # Second, get new-style name.
                if not accel:
                    #@+        << compute emacs_name >>
                    #@+node:ekr.20051021100806.1: *6* << compute emacs_name >>
                    #@+at One not-so-horrible kludge remains.
                    # 
                    # The cut/copy/paste commands in the menu tables are not the same as the methods
                    # actually bound to cut/copy/paste-text minibuffer commands, so we must do a bit
                    # of extra translation to discover whether the user has overridden their
                    # bindings.
                    #@@c

                    if command in (f.OnCutFromMenu,f.OnCopyFromMenu,f.OnPasteFromMenu):
                        emacs_name = '%s-text' % commandName
                    else:
                        try: # User errors in the table can cause this.
                            emacs_name = k.inverseCommandsDict.get(command.__name__)
                        except Exception:
                            emacs_name = None
                    #@-        << compute emacs_name >>
                        # Contains the not-so-horrible kludge.
                    if emacs_name:
                        commandName = emacs_name
                        rawKey,bunchList = c.config.getShortcut(emacs_name)
                        # Pick the first entry that is not a mode.
                        for bunch in bunchList:
                            if not bunch.pane.endswith('-mode'):
                                accel = bunch.val
                                if trace: g.trace('3','%20s' % (bunch.val),commandName)
                                break
                    elif not dynamicMenu:
                        g.trace('No inverse for %s' % commandName)
            #@-        << compute commandName & accel from label & command >>
            # Bug fix: 2009/09/30: use canonical stroke.
            accelerator = k.shortcutFromSetting(accel,addKey=False) or ''
            stroke = k.shortcutFromSetting(accel,addKey=True) or ''
            if accelerator:
                accelerator = g.stripBrackets(k.prettyPrintKey(accelerator))
            if trace: # and commandName == 'add-comments':
                g.trace(bunch.val,repr(stroke),repr(accelerator),commandName)
            def masterMenuCallback (c=c,k=k,stroke=stroke,command=command,commandName=commandName,event=None):
                # if trace: g.trace('stroke',stroke)
                return k.masterMenuHandler(stroke,command,commandName)

            realLabel = self.getRealMenuName(label)
            amp_index = realLabel.find("&")
            realLabel = realLabel.replace("&","")
            if sys.platform == 'darwin':
                #@+            << clear accelerator if it is a plain key >>
                #@+node:ekr.20060216110502: *5* << clear accelerator if it is a plain key >>
                for z in ('Alt','Ctrl','Command'):
                    if accelerator.find(z) != -1:
                        break # Found.
                else:
                    accelerator = ''
                #@-            << clear accelerator if it is a plain key >>

            # c.add_command ensures that c.outerUpdate is called.
            if menu:
                c.add_command(menu,label=realLabel,
                    accelerator=accelerator,
                    command=masterMenuCallback,
                    underline=amp_index)
    #@+node:ekr.20031218072017.3784: *4* createMenuItemsFromTable
    def createMenuItemsFromTable (self,menuName,table,dynamicMenu=False):

        try:
            menu = self.getMenu(menuName)
            if menu == None:
                if not g.app.gui.isNullGui:
                    g.es_print("menu does not exist: ",menuName)
                return
            self.createMenuEntries(menu,table,dynamicMenu=dynamicMenu)
        except:
            g.es_print("exception creating items for",menuName,"menu")
            g.es_exception()

        g.app.menuWarningsGiven = True
    #@+node:ekr.20031218072017.3804: *4* createNewMenu
    def createNewMenu (self,menuName,parentName="top",before=None):

        try:
            parent = self.getMenu(parentName) # parent may be None.
            menu = self.getMenu(menuName)
            if menu:
                g.es("menu already exists:",menuName,color="red")
            else:
                menu = self.new_menu(parent,tearoff=0,label=menuName)
                self.setMenu(menuName,menu)
                label = self.getRealMenuName(menuName)
                amp_index = label.find("&")
                label = label.replace("&","")
                if before: # Insert the menu before the "before" menu.
                    index_label = self.getRealMenuName(before)
                    amp_index = index_label.find("&")
                    index_label = index_label.replace("&","")
                    index = parent.index(index_label)
                    self.insert_cascade(parent,index=index,label=label,menu=menu,underline=amp_index)
                else:
                    self.add_cascade(parent,label=label,menu=menu,underline=amp_index)
                return menu
        except:
            g.es("exception creating",menuName,"menu")
            g.es_exception()
            return None
    #@+node:ekr.20031218072017.4116: *4* createOpenWithMenuFromTable & helper (leoMenu)
    def createOpenWithMenuFromTable (self,table):

        '''Entries in the table passed to createOpenWithMenuFromTable are
    tuples of the form (commandName,shortcut,data).

    - command is one of "os.system", "os.startfile", "os.spawnl", "os.spawnv" or "exec".
    - shortcut is a string describing a shortcut, just as for createMenuItemsFromTable.
    - data is a tuple of the form (command,arg,ext).

    Leo executes command(arg+path) where path is the full path to the temp file.
    If ext is not None, the temp file has the given extension.
    Otherwise, Leo computes an extension based on the @language directive in effect.'''

        trace = False and not g.unitTesting
        c = self.c
        g.app.openWithTable = table # Override any previous table.
        # Delete the previous entry.
        parent = self.getMenu("File")
        if trace: g.trace('parent',parent)
        if not parent:
            if not g.app.batchMode:
                g.es('','createOpenWithMenuFromTable:','no File menu',color="red")
            return

        label = self.getRealMenuName("Open &With...")
        amp_index = label.find("&")
        label = label.replace("&","")
        try:
            index = parent.index(label)
            parent.delete(index)
        except:
            try:
                index = parent.index("Open With...")
                parent.delete(index)
            except:
                if trace:
                    g.trace('unexpected exception')
                    g.es_exception()
                return
        # Create the Open With menu.
        openWithMenu = self.createOpenWithMenu(parent,label,index,amp_index)
        if not openWithMenu:
            if trace: g.trace('openWithMenu returns None')
            return
        self.setMenu("Open With...",openWithMenu)
        # Create the menu items in of the Open With menu.
        for entry in table:
            if len(entry) != 3: # 6/22/03
                g.es('','createOpenWithMenuFromTable:','invalid data',color="red")
                return
        self.createOpenWithMenuItemsFromTable(openWithMenu,table)
        for entry in table:
            name,shortcut,data = entry
            c.k.bindOpenWith (shortcut,name,data)
    #@+node:ekr.20051022043608.1: *5* createOpenWithMenuItemsFromTable
    def createOpenWithMenuItemsFromTable (self,menu,table):

        '''Create an entry in the Open with Menu from the table.

        Each entry should be a sequence with 2 or 3 elements.'''

        c = self.c ; k = c.k

        if g.app.unitTesting: return

        for data in table:
            #@+        << get label, accelerator & command or continue >>
            #@+node:ekr.20051022043713.1: *6* << get label, accelerator & command or continue >>
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
            #@-        << get label, accelerator & command or continue >>
            # g.trace(label,accelerator)
            realLabel = self.getRealMenuName(label)
            underline=realLabel.find("&")
            realLabel = realLabel.replace("&","")
            callback = self.defineOpenWithMenuCallback(openWithData)

            c.add_command(menu,label=realLabel,
                accelerator=accelerator or '',
                command=callback,underline=underline)
    #@+node:ekr.20031218072017.2078: *4* createRecentFilesMenuItems (leoMenu)
    def createRecentFilesMenuItems (self):

        c = self.c
        recentFilesMenu = self.getMenu("Recent Files...")
        if not recentFilesMenu:
            g.trace('Recent Files Menu does not exist',g.callers())
            return

        # Delete all previous entries.
        self.deleteRecentFilesMenuItems(recentFilesMenu)

        # Create the static entries.
        table = self.recentFilesStatic

        self.createMenuEntries(recentFilesMenu,table)

        # Create all the other entries (a maximum of 36).
        accel_ch = string.digits + string.ascii_uppercase # Not a unicode problem.
        i = 0
        n = len(accel_ch)

        # see if we're grouping when files occur in more than one place
        rf_group = c.config.getBool("recent_files_group")
        rf_always = c.config.getBool("recent_files_group_always")
        groupedEntries = rf_group or rf_always

        if groupedEntries:  # if so, make dict of groups
            dirCount = {}
            for fileName in c.recentFiles[:n]:
                dirName, baseName = g.os_path_split(fileName)
                if baseName not in dirCount:
                    dirCount[baseName] = {'dirs':[], 'entry': None}
                dirCount[baseName]['dirs'].append(dirName)

        for name in c.recentFiles[:n]:
            if name.strip() == "": continue  # happens with empty list/new file
            def recentFilesCallback (event=None,c=c,name=name):
                c.openRecentFile(name)

            if groupedEntries:
                dirName, baseName = g.os_path_split(name)

                entry = dirCount[baseName]

                if len(entry['dirs']) > 1 or rf_always:  # sub menus
                    if entry['entry'] is None:
                        entry['entry'] = self.createNewMenu(baseName, "Recent Files...")
                        # acts as a flag for the need to create the menu
                    c.add_command(self.getMenu(baseName), label=dirName,
                        command=recentFilesCallback, underline=0)
                else:  # single occurence, no submenu
                    c.add_command(recentFilesMenu,label=baseName,command=recentFilesCallback,underline=0)
            else:  # original behavior
                label = "%s %s" % (accel_ch[i],g.computeWindowTitle(name))
                c.add_command(recentFilesMenu,label=label,command=recentFilesCallback,underline=0)
            i += 1

        if groupedEntries:  # store so we can delete them later
            self.groupedMenus = [i for i in dirCount
                                 if dirCount[i]['entry'] is not None]
    #@+node:tbrown.20080509212202.7: *4* deleteRecentFilesMenuItems
    def deleteRecentFilesMenuItems(self,menu):
        """Delete recent file menu entries"""

        toDrop = len(self.c.recentFiles)
        if hasattr(self, 'recentFilesStatic'):
            toDrop += len(self.recentFilesStatic)

        self.delete_range(menu,0,toDrop)

        if hasattr(self, 'groupedMenus'):
            for i in self.groupedMenus:
                menu = self.getMenu(i)
                if menu:
                    self.destroy(menu)
                    self.destroyMenu(i)
    #@+node:ekr.20031218072017.4117: *4* defineMenuCallback
    def defineMenuCallback(self,command,name,minibufferCommand):

        if minibufferCommand:

            # Create a dummy event as a signal to doCommand.
            event = g.Bunch(keysym='',char='',widget='')

            # The first parameter must be event, and it must default to None.
            def minibufferMenuCallback(event=event,self=self,command=command,label=name):
                c = self.c
                return c.doCommand(command,label,event)

            return minibufferMenuCallback

        else:

            # The first parameter must be event, and it must default to None.
            def legacyMenuCallback(event=None,self=self,command=command,label=name):
                c = self.c
                return c.doCommand(command,label)

            return legacyMenuCallback
    #@+node:ekr.20031218072017.4118: *4* defineOpenWithMenuCallback
    def defineOpenWithMenuCallback(self,data):

        # The first parameter must be event, and it must default to None.
        def openWithMenuCallback(event=None,self=self,data=data):
            return self.c.openWith(data=data)

        return openWithMenuCallback
    #@+node:ekr.20031218072017.3805: *4* deleteMenu
    def deleteMenu (self,menuName):

        try:
            menu = self.getMenu(menuName)
            if menu:
                self.destroy(menu)
                self.destroyMenu(menuName)
            else:
                g.es("can't delete menu:",menuName)
        except:
            g.es("exception deleting",menuName,"menu")
            g.es_exception()
    #@+node:ekr.20031218072017.3806: *4* deleteMenuItem
    def deleteMenuItem (self,itemName,menuName="top"):

        """Delete itemName from the menu whose name is menuName."""

        try:
            menu = self.getMenu(menuName)
            if menu:
                realItemName = self.getRealMenuName(itemName)
                self.delete(menu,realItemName)
            else:
                g.es("menu not found:",menuName)
        except:
            g.es("exception deleting",itemName,"from",menuName,"menu")
            g.es_exception()
    #@+node:ekr.20031218072017.3782: *4* get/setRealMenuName & setRealMenuNamesFromTable
    # Returns the translation of a menu name or an item name.

    def getRealMenuName (self,menuName):

        cmn = self.canonicalizeTranslatedMenuName(menuName)
        return g.app.realMenuNameDict.get(cmn,menuName)

    def setRealMenuName (self,untrans,trans):

        cmn = self.canonicalizeTranslatedMenuName(untrans)
        g.app.realMenuNameDict[cmn] = trans

    def setRealMenuNamesFromTable (self,table):

        try:
            for untrans,trans in table:
                self.setRealMenuName(untrans,trans)
        except:
            g.es("exception in","setRealMenuNamesFromTable")
            g.es_exception()
    #@+node:ekr.20031218072017.3807: *4* getMenu, setMenu, destroyMenu
    def getMenu (self,menuName):

        cmn = self.canonicalizeMenuName(menuName)
        # if cmn == 'openwith': g.trace('leoMenu',g.dictToString(self.menus))
        return self.menus.get(cmn)

    def setMenu (self,menuName,menu):

        cmn = self.canonicalizeMenuName(menuName)
        self.menus [cmn] = menu

    def destroyMenu (self,menuName):

        cmn = self.canonicalizeMenuName(menuName)
        del self.menus[cmn]
    #@+node:ekr.20031218072017.3808: *3* Must be overridden in menu subclasses
    #@+node:ekr.20031218072017.3809: *4* 9 Routines with Tk spellings
    def add_cascade (self,parent,label,menu,underline):
        self.oops()

    def add_command (self,menu,**keys):
        self.oops()

    def add_separator(self,menu):
        self.oops()

    def bind (self,bind_shortcut,callback):
        self.oops()

    def delete (self,menu,realItemName):
        self.oops()

    def delete_range (self,menu,n1,n2):
        self.oops()

    def destroy (self,menu):
        self.oops()

    def insert (self,menuName,position,label,command,underline=None): # New in Leo 4.4.3 a1
        self.oops()

    def insert_cascade (self,parent,index,label,menu,underline):
        self.oops()

    def new_menu(self,parent,tearoff=0,label=''): # 2010: added label arg for pylint.
        self.oops() ; return None
    #@+node:ekr.20031218072017.3810: *4* 9 Routines with new spellings
    def activateMenu (self,menuName): # New in Leo 4.4b2.
        self.oops()

    def clearAccel (self,menu,name):
        self.oops()

    def createMenuBar (self,frame):
        self.oops()

    def createOpenWithMenu (self,parent,label,index,amp_index):
        self.oops() ; return None

    def disableMenu (self,menu,name):
        self.oops()

    def enableMenu (self,menu,name,val):
        self.oops()

    def getMacHelpMenu (self,table):
        return None

    def getMenuLabel (self,menu):
        self.oops()

    def setMenuLabel (self,menu,name,label,underline=-1):
        self.oops()
    #@-others
#@+node:ekr.20031218072017.3811: ** class nullMenu
class nullMenu(leoMenu):

    """A null menu class for testing and batch execution."""

    #@+others
    #@+node:ekr.20050104094308: *3* ctor
    def __init__ (self,frame):

        # Init the base class.
        leoMenu.__init__(self,frame)
    #@+node:ekr.20050104094029: *3* oops
    def oops (self):

        # g.trace("leoMenu", g.callers())
        pass
    #@-others
#@-others
#@-leo

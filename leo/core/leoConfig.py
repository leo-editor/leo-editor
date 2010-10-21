#@+leo-ver=5-thin
#@+node:ekr.20041117062700: * @thin leoConfig.py
#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@+<< imports >>
#@+node:ekr.20041227063801: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui

import sys
import zipfile
#@-<< imports >>

#@+<< class parserBaseClass >>
#@+node:ekr.20041119203941.2: ** << class parserBaseClass >>
class parserBaseClass:

    """The base class for settings parsers."""

    #@+<< parserBaseClass data >>
    #@+node:ekr.20041121130043: *3* << parserBaseClass data >>
    # These are the canonicalized names.  Case is ignored, as are '_' and '-' characters.

    basic_types = [
        # Headlines have the form @kind name = var
        'bool','color','directory','int','ints',
        'float','path','ratio','shortcut','string','strings']

    control_types = [
        'abbrev','buttons','commands','data','enabledplugins','font',
        'if','ifgui','ifhostname','ifplatform','ignore','mode',
        'openwith','page','settings','shortcuts',
        'buttons','menus', # New in Leo 4.4.4.
        'menuat', 'popup', # New in Leo 4.4.8.
        ]

    # Keys are settings names, values are (type,value) tuples.
    settingsDict = {}
    #@-<< parserBaseClass data >>

    #@+others
    #@+node:ekr.20041119204700: *3*  ctor (parserBaseClass)
    def __init__ (self,c,localFlag):

        self.c = c
        self.localFlag = localFlag
            # True if this is the .leo file being opened,
            # as opposed to myLeoSettings.leo or leoSettings.leo.
        self.recentFiles = [] # List of recent files.
        self.shortcutsDict = {}
            # Keys are cononicalized shortcut names, values are bunches.
        self.openWithList = []
            # A list of dicts containing 'name','shortcut','command' keys.

        # Keys are canonicalized names.
        self.dispatchDict = {
            'abbrev':       self.doAbbrev, # New in 4.4.1 b2.
            'bool':         self.doBool,
            'buttons':      self.doButtons, # New in 4.4.4
            'color':        self.doColor,
            'commands':     self.doCommands, # New in 4.4.8.
            'data':         self.doData, # New in 4.4.6
            'directory':    self.doDirectory,
            'enabledplugins': self.doEnabledPlugins,
            'font':         self.doFont,
            'if':           self.doIf,
            # 'ifgui':        self.doIfGui,  # Removed in 4.4 b3.
            'ifhostname':   self.doIfHostname,
            'ifplatform':   self.doIfPlatform,
            'ignore':       self.doIgnore,
            'int':          self.doInt,
            'ints':         self.doInts,
            'float':        self.doFloat,
            'menus':        self.doMenus, # New in 4.4.4
            'menuat':       self.doMenuat,
            'popup': self.doPopup, # New in 4.4.8

            'mode':         self.doMode, # New in 4.4b1.
            'openwith':     self.doOpenWith, # New in 4.4.3 b1.
            'path':         self.doPath,
            'page':         self.doPage,
            'ratio':        self.doRatio,
            # 'shortcut':     self.doShortcut, # Removed in 4.4.1 b1.
            'shortcuts':    self.doShortcuts,
            'string':       self.doString,
            'strings':      self.doStrings,
        }

        self.debug_count = 0
    #@+node:ekr.20080514084054.4: *3* computeModeName (parserBaseClass)
    def computeModeName (self,name):

        s = name.strip().lower()
        j = s.find(' ')
        if j > -1: s = s[:j]
        if s.endswith('mode'):
            s = s[:-4].strip()
        if s.endswith('-'):
            s = s[:-1]

        i = s.find('::')
        if i > -1:
            # The actual mode name is everything up to the "::"
            # The prompt is everything after the prompt.
            s = s[:i]

        modeName = s + '-mode'
        return modeName
    #@+node:ekr.20060102103625: *3* createModeCommand (parserBaseClass)
    def createModeCommand (self,modeName,name,modeDict):

        modeName = 'enter-' + modeName.replace(' ','-')

        i = name.find('::')
        if i > -1:
            # The prompt is everything after the '::'
            prompt = name[i+2:].strip()
            modeDict ['*command-prompt*'] = prompt
            # g.trace('modeName',modeName,'*command-prompt*',prompt)

        # Save the info for k.finishCreate and k.makeAllBindings.
        d = g.app.config.modeCommandsDict

        # New in 4.4.1 b2: silently allow redefinitions of modes.
        d [modeName] = modeDict
    #@+node:ekr.20041120103012: *3* error
    def error (self,s):

        g.pr(s)

        # Does not work at present because we are using a null Gui.
        g.es(s,color="blue")
    #@+node:ekr.20041120094940: *3* kind handlers (parserBaseClass)
    #@+node:ekr.20060608221203: *4* doAbbrev
    def doAbbrev (self,p,kind,name,val):

        d = {}
        s = p.b
        lines = g.splitLines(s)
        for line in lines:
            line = line.strip()
            if line and not g.match(line,0,'#'):
                name,val = self.parseAbbrevLine(line)
                if name: d [val] = name

        self.set (p,'abbrev','abbrev',d)
    #@+node:ekr.20041120094940.1: *4* doBool
    def doBool (self,p,kind,name,val):

        if val in ('True','true','1'):
            self.set(p,kind,name,True)
        elif val in ('False','false','0'):
            self.set(p,kind,name,False)
        else:
            self.valueError(p,kind,name,val)
    #@+node:ekr.20070925144337: *4* doButtons
    def doButtons (self,p,kind,name,val):

        '''Handle an @buttons tree.'''

        aList = [] ; c = self.c ; tag = '@button'
        for p in p.unique_subtree():
            h = p.h
            if g.match_word(h,0,tag):
                # We can not assume that p will be valid when it is used.
                script = g.getScript(c,p,useSelectedText=False,forcePythonSentinels=True,useSentinels=True)
                aList.append((p.h,script),)

        # g.trace(g.listToString([h for h,script in aList]))

        # This setting is handled differently from most other settings,
        # because the last setting must be retrieved before any commander exists.
        g.app.config.atCommonButtonsList = aList
        g.app.config.buttonsFileName = c and c.shortFileName() or '<no settings file>'

    #@+node:ekr.20080312071248.6: *4* doCommands
    def doCommands (self,p,kind,name,val):

        '''Handle an @commands tree.'''

        aList = [] ; c = self.c ; tag = '@command'
        for p in p.subtree():
            h = p.h
            if g.match_word(h,0,tag):
                # We can not assume that p will be valid when it is used.
                script = g.getScript(c,p,useSelectedText=False,forcePythonSentinels=True,useSentinels=True)
                aList.append((p.h,script),)

        # g.trace(g.listToString(aList))

        # This setting is handled differently from most other settings,
        # because the last setting must be retrieved before any commander exists.
        g.app.config.atCommonCommandsList = aList


    #@+node:ekr.20041120094940.2: *4* doColor
    def doColor (self,p,kind,name,val):

        # At present no checking is done.
        val = val.lstrip('"').rstrip('"')
        val = val.lstrip("'").rstrip("'")

        self.set(p,kind,name,val)
    #@+node:ekr.20071214140900: *4* doData
    def doData (self,p,kind,name,val):

        s = p.b
        lines = g.splitLines(s)
        data = [z.strip() for z in lines if z.strip() and not z.startswith('#')]

        self.set(p,kind,name,data)
    #@+node:ekr.20041120094940.3: *4* doDirectory & doPath
    def doDirectory (self,p,kind,name,val):

        # At present no checking is done.
        self.set(p,kind,name,val)

    doPath = doDirectory
    #@+node:ekr.20070224075914: *4* doEnabledPlugins
    def doEnabledPlugins (self,p,kind,name,val):

        c = self.c
        s = p.b

        # This setting is handled differently from all other settings,
        # because the last setting must be retrieved before any commander exists.

        # g.trace('len(s)',len(s))

        # Set the global config ivars.
        g.app.config.enabledPluginsString = s
        g.app.config.enabledPluginsFileName = c and c.shortFileName() or '<no settings file>'
    #@+node:ekr.20041120094940.6: *4* doFloat
    def doFloat (self,p,kind,name,val):

        try:
            val = float(val)
            self.set(p,kind,name,val)
        except ValueError:
            self.valueError(p,kind,name,val)
    #@+node:ekr.20041120094940.4: *4* doFont
    def doFont (self,p,kind,name,val):

        trace = False

        if trace: g.trace(p and p.h,kind,name,self.c.mFileName)

        d = self.parseFont(p)

        # Set individual settings.
        for key in ('family','size','slant','weight'):
            data = d.get(key)
            if data is not None:
                name,val = data
                setKind = key
                self.set(p,setKind,name,val)
                if trace and val not in (None,'none','None'): g.trace(key,val)
    #@+node:ekr.20041120103933: *4* doIf
    def doIf(self,p,kind,name,val):

        g.trace("'if' not supported yet")
        return None
    #@+node:ekr.20041121125416: *4* doIfGui (can never work)
    #@+at
    # Alas, @if-gui can't be made to work. The problem is that plugins can
    # set g.app.gui, but plugins need settings so the leoSettings.leo files
    # must be parsed before g.app.gui.guiName() is known.
    #@@c

    if 0:

        def doIfGui (self,p,kind,name,val):

            if not g.app.gui or not g.app.gui.guiName():
                s = '@if-gui has no effect: g.app.gui not defined yet'
                g.es_print(s,color='blue')
                return "skip"
            elif g.app.gui.guiName().lower() == name.lower():
                return None
            else:
                return "skip"
    #@+node:dan.20080410121257.2: *4* doIfHostname
    def doIfHostname (self,p,kind,name,val):
        """headline: @ifhostname bob,!harry,joe

        Logical AND with the comma-separated list of host names, NO SPACES.

        descends this node iff:
            h = os.environ('HOSTNAME')
            h == 'bob' and h != 'harry' and h == 'joe'"""

        h = g.computeMachineName()
        names = name.split(',')

        for n in names:
            if (n[0] == '!' and h == n[1:]) or (h != n):
                # g.trace('skipping', name)
                return 'skip'

        return None

    #@+node:ekr.20041120104215: *4* doIfPlatform
    def doIfPlatform (self,p,kind,name,val):

        if sys.platform.lower() == name.lower():
            return None
        else:
            return "skip"
    #@+node:ekr.20041120104215.1: *4* doIgnore
    def doIgnore(self,p,kind,name,val):

        return "skip"
    #@+node:ekr.20041120094940.5: *4* doInt
    def doInt (self,p,kind,name,val):

        try:
            val = int(val)
            self.set(p,kind,name,val)
        except ValueError:
            self.valueError(p,kind,name,val)
    #@+node:ekr.20041217132253: *4* doInts
    def doInts (self,p,kind,name,val):

        '''We expect either:
        @ints [val1,val2,...]aName=val
        @ints aName[val1,val2,...]=val'''

        name = name.strip() # The name indicates the valid values.
        i = name.find('[')
        j = name.find(']')

        # g.trace(kind,name,val)

        if -1 < i < j:
            items = name[i+1:j]
            items = items.split(',')
            name = name[:i]+name[j+1:].strip()
            # g.trace(name,items)
            try:
                items = [int(item.strip()) for item in items]
            except ValueError:
                items = []
                self.valueError(p,'ints[]',name,val)
                return
            kind = "ints[%s]" % (','.join([str(item) for item in items]))
            try:
                val = int(val)
            except ValueError:
                self.valueError(p,'int',name,val)
                return
            if val not in items:
                self.error("%d is not in %s in %s" % (val,kind,name))
                return

            # g.trace(repr(kind),repr(name),val)

            # At present no checking is done.
            self.set(p,kind,name,val)
    #@+node:ekr.20070925144337.2: *4* doMenus & helpers (ParserBaseClass)
    def doMenus (self,p,kind,name,val):

        c = self.c ; aList = [] ; tag = '@menu' ; trace = False and g.isPython3
        p = p.copy() ; after = p.nodeAfterTree()
        if trace: g.trace('******',p.h,'after',after and after.h)
        while p and p != after:
            self.debug_count += 1
            h = p.h
            if g.match_word(h,0,tag):
                name = h[len(tag):].strip()
                if name:
                    for z in aList:
                        name2,junk,junk = z
                        if name2 == name:
                            self.error('Replacing previous @menu %s' % (name))
                            break
                    aList2 = []
                    kind = '%s %s' % (tag,name)
                    self.doItems(p,aList2)
                    aList.append((kind,aList2,None),)
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()

        # g.trace('localFlag',self.localFlag,c)
        if self.localFlag:
            self.set(p,kind='menus',name='menus',val=aList)
        else:
            if False and not g.app.unitTesting and not g.app.silentMode:
                s = 'using menus from: %s' % c.shortFileName()
                g.es_print(s,color='blue')
            g.app.config.menusList = aList
            g.app.config.menusFileName = c and c.shortFileName() or '<no settings file>'
    #@+node:ekr.20070926141716: *5* doItems
    def doItems (self,p,aList):

        trace = False and g.isPython3
        if trace: g.trace(p.h)
        p = p.copy()
        after = p.nodeAfterTree()
        p.moveToThreadNext()
        if trace: g.trace(self.debug_count,p.h,'after',after and after.h)
        while p and p != after:
            self.debug_count += 1
            h = p.h
            # if trace:
                # if p.h==after.h:
                    # val = p != after
                    # g.trace('*' * 10, 'terminating via headString',p,after)
                    # return
                # g.trace(self.debug_count,h)
                # if self.debug_count >= 1000:
                    # g.trace('*'*10,'terminating!') ; return
            for tag in ('@menu','@item'):
                if g.match_word(h,0,tag):
                    itemName = h[len(tag):].strip()
                    if itemName:
                        if tag == '@menu':
                            aList2 = []
                            kind = '%s %s' % (tag,itemName)
                            self.doItems(p,aList2)
                            aList.append((kind,aList2,None),)
                            p.moveToNodeAfterTree()
                            break
                        else:
                            kind = tag
                            head = itemName
                            body = p.b
                            aList.append((kind,head,body),)
                            p.moveToThreadNext()
                            break
            else:
                # g.trace('***skipping***',p.h)
                p.moveToThreadNext()
    #@+node:ekr.20070926142312: *5* dumpMenuList
    def dumpMenuList (self,aList,level=0):

        for z in aList:
            kind,val,val2 = z
            if kind == '@item':
                g.trace(level,kind,val,val2)
            else:
                g.pr('')
                g.trace(level,kind,'...')
                self.dumpMenuList(val,level+1)
    #@+node:ekr.20060102103625.1: *4* doMode (ParserBaseClass)
    def doMode(self,p,kind,name,val):

        '''Parse an @mode node and create the enter-<name>-mode command.'''

        c = self.c ; k = c.k ; name1 = name

        # g.trace('%20s' % (name),c.fileName())
        modeName = self.computeModeName(name)

        # Create a local shortcutsDict.
        old_d = self.shortcutsDict
        d = self.shortcutsDict = {}

        s = p.b
        lines = g.splitLines(s)
        for line in lines:
            line = line.strip()
            if line and not g.match(line,0,'#'):
                name,bunch = self.parseShortcutLine(line)
                if not name:
                    # An entry command: put it in the special *entry-commands* key.
                    aList = d.get('*entry-commands*',[])
                    aList.append(bunch.entryCommandName)
                    d ['*entry-commands*'] = aList
                elif bunch is not None:
                    # A regular shortcut.
                    bunch.val = k.strokeFromSetting(bunch.val)
                    bunch.pane = modeName
                    bunchList = d.get(name,[])
                    # Important: use previous bindings if possible.
                    key2,bunchList2 = c.config.getShortcut(name)
                    bunchList3 = [b for b in bunchList2 if b.pane != modeName]
                    if bunchList3:
                        # g.trace('inheriting',[b.val for b in bunchList3])
                        bunchList.extend(bunchList3)
                    bunchList.append(bunch)
                    d [name] = bunchList
                    self.set(p,"shortcut",name,bunchList)
                    self.setShortcut(name,bunchList)

        # Restore the global shortcutsDict.
        self.shortcutsDict = old_d

        # Create the command, but not any bindings to it.
        self.createModeCommand(modeName,name1,d)
    #@+node:ekr.20070411101643.1: *4* doOpenWith (ParserBaseClass)
    def doOpenWith (self,p,kind,name,val):

        # g.trace('kind',kind,'name',name,'val',val,'c',self.c)

        d = self.parseOpenWith(p)
        d['name']=name
        d['shortcut']=val
        name = kind = 'openwithtable'
        self.openWithList.append(d)
        self.set(p,kind,name,self.openWithList)
    #@+node:ekr.20041120104215.2: *4* doPage
    def doPage(self,p,kind,name,val):

        pass # Ignore @page this while parsing settings.
    #@+node:ekr.20041121125741: *4* doRatio
    def doRatio (self,p,kind,name,val):

        try:
            val = float(val)
            if 0.0 <= val <= 1.0:
                self.set(p,kind,name,val)
            else:
                self.valueError(p,kind,name,val)
        except ValueError:
            self.valueError(p,kind,name,val)
    #@+node:ekr.20041120105609: *4* doShortcuts (ParserBaseClass)
    def doShortcuts(self,p,kind,name,val,s=None):

        c = self.c ; d = self.shortcutsDict ; k = c.k
        trace = False or c.config.getBool('trace_bindings_verbose')
        munge = k.shortcutFromSetting
        if s is None: s = p.b
        lines = g.splitLines(s)
        for line in lines:
            line = line.strip()
            if line and not g.match(line,0,'#'):
                name,bunch = self.parseShortcutLine(line)
                # if name in ('save-file','enter-tree-save-file-mode'): g.pdb()
                if bunch is not None:
                    if bunch.val not in (None,'none','None'):
                        # A regular shortcut.
                        bunchList = d.get(name,[])
                        if bunch.pane in ('kill','Kill'):
                            if trace: g.trace('****** killing binding:',bunch.val,'to',name)
                            bunchList = [z for z in bunchList
                                if munge(z.val) != munge(bunch.val)]
                            # g.trace(bunchList)
                        else:
                            if trace: g.trace('%6s %20s %s' % (bunch.pane,bunch.val,name))
                            bunchList.append(bunch)
                        d [name] = bunchList
                        self.set(p,"shortcut",name,bunchList)
                        self.setShortcut(name,bunchList)
    #@+node:ekr.20041217132028: *4* doString
    def doString (self,p,kind,name,val):

        # At present no checking is done.
        self.set(p,kind,name,val)
    #@+node:ekr.20041120094940.8: *4* doStrings
    def doStrings (self,p,kind,name,val):

        '''We expect one of the following:
        @strings aName[val1,val2...]=val
        @strings [val1,val2,...]aName=val'''

        name = name.strip()
        i = name.find('[')
        j = name.find(']')

        if -1 < i < j:
            items = name[i+1:j]
            items = items.split(',')
            items = [item.strip() for item in items]
            name = name[:i]+name[j+1:].strip()
            kind = "strings[%s]" % (','.join(items))
            # g.trace(repr(kind),repr(name),val)

            # At present no checking is done.
            self.set(p,kind,name,val)
    #@+node:bobjack.20080324141020.4: *4* doPopup & helper
    def doPopup (self,p,kind,name,val):

        """
        Handle @popup menu items in @settings trees.
        """

        popupName = name
        popupType = val

        c = self.c ; aList = [] ; tag = '@menu'

        #g.trace(p, kind, name, val, c)

        aList = []
        p = p.copy()
        self.doPopupItems(p,aList)


        if not hasattr(g.app.config, 'context_menus'):
            g.app.config.context_menus = {}

        #if popupName in g.app.config.context_menus:
            #g.pr('*** duplicate popup ***', popupName)


        g.app.config.context_menus[popupName] = aList
    #@+node:bobjack.20080324141020.5: *5* doPopupItems
    def doPopupItems (self,p,aList):

        p = p.copy() ; after = p.nodeAfterTree()
        p.moveToThreadNext()
        while p and p != after:
            h = p.h
            for tag in ('@menu','@item'):
                if g.match_word(h,0,tag):
                    itemName = h[len(tag):].strip()
                    if itemName:
                        if tag == '@menu':
                            aList2 = []
                            kind = '%s' % itemName
                            body = p.b
                            self.doPopupItems(p,aList2)
                            aList.append((kind + '\n' + body, aList2),)
                            p.moveToNodeAfterTree()
                            break
                        else:
                            kind = tag
                            head = itemName
                            body = p.b
                            aList.append((head,body),)
                            p.moveToThreadNext()
                            break
            else:
                # g.trace('***skipping***',p.h)
                p.moveToThreadNext()
    #@+node:tbrown.20080514112857.124: *4* doMenuat
    def doMenuat (self,p,kind,name,val):

        if g.app.config.menusList:
            g.es_print("Patching menu tree: " + name)

            # get the patch fragment
            patch = []
            if p.hasChildren():
                # self.doMenus(p.copy().firstChild(),kind,name,val,storeIn=patch)
                self.doItems(p.copy(),patch)
                self.dumpMenuTree(patch)

            # setup        
            parts = name.split()
            if len(parts) != 3:
                parts.append('subtree')
            targetPath,mode,source = parts
            if not targetPath.startswith('/'): targetPath = '/'+targetPath

            ans = self.patchMenuTree(g.app.config.menusList, targetPath)

            if ans:
                g.es_print("Patching ("+mode+' '+source+") at "+targetPath)

                list_, idx = ans

                if mode not in ('copy', 'cut'):
                    if source != 'clipboard':
                        use = patch # [0][1]
                    else:
                        if isinstance(self.clipBoard, list):
                            use = self.clipBoard
                        else:
                            use = [self.clipBoard]
                    g.es_print(str(use))
                if mode == 'replace':
                    list_[idx] = use.pop(0)
                    while use:
                        idx += 1
                        list_.insert(idx, use.pop(0))
                elif mode == 'before':
                    while use:
                        list_.insert(idx, use.pop())
                elif mode == 'after':
                    while use:
                        list_.insert(idx+1, use.pop())
                elif mode == 'cut':
                    self.clipBoard = list_[idx]
                    del list_[idx]
                elif mode == 'copy':
                    self.clipBoard = list_[idx]
                    g.es_print(str(self.clipBoard))
                else:  # append
                    list_.extend(use)
            else:
                g.es_print("ERROR: didn't find menu path " + targetPath)

        else:
            g.es_print("ERROR: @menuat found but no menu tree to patch")
    #@+node:tbrown.20080514180046.9: *5* getName
    def getName(self, val, val2=None):
        if val2 and val2.strip(): val = val2
        val = val.split('\n',1)[0]
        for i in "*.-& \t\n":
            val = val.replace(i,'')
        return val.lower()
    #@+node:tbrown.20080514180046.2: *5* dumpMenuTree
    def dumpMenuTree (self,aList,level=0,path=''):

        for z in aList:
            kind,val,val2 = z
            if kind == '@item':
                name = self.getName(val, val2)
                g.es_print('%s %s (%s) [%s]' % ('    '*(level+0), val, val2, path+'/'+name))
            else:
                name = self.getName(kind.replace('@menu ',''))
                g.es_print('%s %s... [%s]' % ('    '*(level), kind, path+'/'+name))
                self.dumpMenuTree(val,level+1,path=path+'/'+name)
    #@+node:tbrown.20080514180046.8: *5* patchMenuTree
    def patchMenuTree(self, orig, targetPath, path=''):

        for n,z in enumerate(orig):
            kind,val,val2 = z
            if kind == '@item':
                name = self.getName(val, val2)
                curPath = path+'/'+name
                if curPath == targetPath:
                    g.es_print('Found '+targetPath)
                    return orig, n
            else:
                name = self.getName(kind.replace('@menu ',''))
                curPath = path+'/'+name
                if curPath == targetPath:
                    g.es_print('Found '+targetPath)
                    return orig, n
                ans = self.patchMenuTree(val, targetPath, path=path+'/'+name)
                if ans:
                    return ans

        return None
    #@+node:ekr.20041124063257: *3* munge
    def munge(self,s):

        return g.app.config.canonicalizeSettingName(s)
    #@+node:ekr.20041119204700.2: *3* oops
    def oops (self):
        g.pr("parserBaseClass oops:",
            g.callers(),
            "must be overridden in subclass")
    #@+node:ekr.20041213082558: *3* parsers
    #@+node:ekr.20041213083651: *4* fontSettingNameToFontKind
    def fontSettingNameToFontKind (self,name):

        s = name.strip()
        if s:
            for tag in ('_family','_size','_slant','_weight'):
                if s.endswith(tag):
                    return tag[1:]

        return None
    #@+node:ekr.20041213082558.1: *4* parseFont & helper
    def parseFont (self,p):

        d = {
            'comments': [],
            'family': None,
            'size': None,
            'slant': None,
            'weight': None,
        }

        s = p.b
        lines = g.splitLines(s)

        for line in lines:
            self.parseFontLine(line,d)

        comments = d.get('comments')
        d['comments'] = '\n'.join(comments)

        return d
    #@+node:ekr.20041213082558.2: *5* parseFontLine
    def parseFontLine (self,line,d):

        s = line.strip()
        if not s: return

        try:
            s = str(s)
        except UnicodeError:
            pass

        if g.match(s,0,'#'):
            s = s[1:].strip()
            comments = d.get('comments')
            comments.append(s)
            d['comments'] = comments
        else:
            # name is everything up to '='
            i = s.find('=')
            if i == -1:
                name = s ; val = None
            else:
                name = s[:i].strip()
                val = s[i+1:].strip()
                val = val.lstrip('"').rstrip('"')
                val = val.lstrip("'").rstrip("'")

            fontKind = self.fontSettingNameToFontKind(name)
            if fontKind:
                d[fontKind] = name,val # Used only by doFont.
    #@+node:ekr.20041119205148: *4* parseHeadline
    def parseHeadline (self,s):

        """Parse a headline of the form @kind:name=val
        Return (kind,name,val)."""

        kind = name = val = None

        if g.match(s,0,'@'):
            i = g.skip_id(s,1,chars='-')
            kind = s[1:i].strip()
            if kind:
                # name is everything up to '='
                j = s.find('=',i)
                if j == -1:
                    name = s[i:].strip()
                else:
                    name = s[i:j].strip()
                    # val is everything after the '='
                    val = s[j+1:].strip()

        # g.trace("%50s %10s %s" %(name,kind,val))
        return kind,name,val
    #@+node:ekr.20070411101643.2: *4* parseOpenWith & helper
    def parseOpenWith (self,p):

        d = {'command': None,}

        s = p.b
        lines = g.splitLines(s)

        for line in lines:
            self.parseOpenWithLine(line,d)

        return d
    #@+node:ekr.20070411101643.4: *5* parseOpenWithLine
    def parseOpenWithLine (self,line,d):

        s = line.strip()
        if not s: return

        try:
            s = str(s)
        except UnicodeError:
            pass

        if not g.match(s,0,'#'):
            d['command'] = s
    #@+node:ekr.20041120112043: *4* parseShortcutLine (g.app.config)
    def parseShortcutLine (self,s):

        '''Parse a shortcut line.  Valid forms:

        --> entry-command
        settingName = shortcut
        settingName ! paneName = shortcut
        command-name -> mode-name = binding
        command-name -> same = binding
        '''

        name = val = nextMode = None ; nextMode = 'none'
        i = g.skip_ws(s,0)

        if g.match(s,i,'-->'): # New in 4.4.1 b1: allow mode-entry commands.
            j = g.skip_ws(s,i+3)
            i = g.skip_id(s,j,'-')
            entryCommandName = s[j:i]
            return None,g.Bunch(entryCommandName=entryCommandName)

        j = i
        i = g.skip_id(s,j,'-') # New in 4.4: allow Emacs-style shortcut names.
        name = s[j:i]
        if not name: return None,None

        # New in Leo 4.4b2.
        i = g.skip_ws(s,i)
        if g.match(s,i,'->'): # New in 4.4: allow pane-specific shortcuts.
            j = g.skip_ws(s,i+2)
            i = g.skip_id(s,j)
            nextMode = s[j:i]

        i = g.skip_ws(s,i)
        if g.match(s,i,'!'): # New in 4.4: allow pane-specific shortcuts.
            j = g.skip_ws(s,i+1)
            i = g.skip_id(s,j)
            pane = s[j:i]
            if not pane.strip(): pane = 'all'
        else: pane = 'all'

        i = g.skip_ws(s,i)
        if g.match(s,i,'='):
            i = g.skip_ws(s,i+1)
            val = s[i:]

        # New in 4.4: Allow comments after the shortcut.
        # Comments must be preceded by whitespace.
        comment = ''
        if val:
            i = val.find('#')
            if i > 0 and val[i-1] in (' ','\t'):
                # comment = val[i:].strip()
                val = val[:i].strip()

        # g.trace(pane,name,val,s)
        return name,g.bunch(nextMode=nextMode,pane=pane,val=val)
    #@+node:ekr.20060608222828: *4* parseAbbrevLine (g.app.config)
    def parseAbbrevLine (self,s):

        '''Parse an abbreviation line:
        command-name = abbreviation
        return (command-name,abbreviation)
        '''

        i = j = g.skip_ws(s,0)
        i = g.skip_id(s,i,'-') # New in 4.4: allow Emacs-style shortcut names.
        name = s[j:i]
        if not name: return None,None

        i = g.skip_ws(s,i)
        if not g.match(s,i,'='): return None,None

        i = g.skip_ws(s,i+1)
        val = s[i:].strip()
        # Ignore comments after the shortcut.
        i = val.find('#')
        if i > -1: val = val[:i].strip()

        if val: return name,val
        else:   return None,None
    #@+node:ekr.20041120094940.9: *3* set (parserBaseClass)
    def set (self,p,kind,name,val):

        """Init the setting for name to val."""

        trace = False and not g.unitTesting
        if trace: g.trace(kind,name,val)

        c = self.c ; key = self.munge(name)

        # if kind and kind.startswith('setting'): g.trace("settingsParser %10s %15s %s" %(kind,val,name))
        d = self.settingsDict
        bunch = d.get(key)
        if bunch:
            # g.trace(key,bunch.val,bunch.path)
            path = bunch.path
            if c.os_path_finalize(c.mFileName) != c.os_path_finalize(path):
                g.es("over-riding setting:",name,"from",path)

        # N.B.  We can't use c here: it may be destroyed!
        # if key == 'shortcut':
            # g.trace('*****',key,val)

        d [key] = g.Bunch(path=c.mFileName,kind=kind,val=val,tag='setting')
    #@+node:ekr.20041227071423: *3* setShortcut (ParserBaseClass)
    def setShortcut (self,name,bunchList):

        c = self.c

        # None is a valid value for val.
        key = c.frame.menu.canonicalizeMenuName(name)
        rawKey = key.replace('&','')
        self.set(c,rawKey,"shortcut",bunchList)

        if 0:
            for b in bunchList:
                g.trace('%20s %45s %s' % (b.val,rawKey,b.pane))
    #@+node:ekr.20041119204700.1: *3* traverse (parserBaseClass)
    def traverse (self):

        c = self.c

        p = g.app.config.settingsRoot(c)
        if not p:
            # g.trace('no settings tree for %s' % c)
            return None

        self.settingsDict = {}
        self.shortcutsDict = {}
        after = p.nodeAfterTree()
        while p and p != after:
            result = self.visitNode(p)
            # if g.isPython3:
                # g.trace(result,p.h)
                # if p.h == 'Menus': g.pdb()
            if result == "skip":
                # g.es_print('skipping settings in',p.h,color='blue')
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        return self.settingsDict
    #@+node:ekr.20041120094940.10: *3* valueError
    def valueError (self,p,kind,name,val):

        """Give an error: val is not valid for kind."""

        self.error("%s is not a valid %s for %s" % (val,kind,name))
    #@+node:ekr.20041119204700.3: *3* visitNode (must be overwritten in subclasses)
    def visitNode (self,p):

        self.oops()
    #@-others
#@-<< class parserBaseClass >>

#@+others
#@+node:ekr.20041119203941: ** class configClass
class configClass:
    """A class to manage configuration settings."""
    #@+<< class data >>
    #@+node:ekr.20041122094813: *3* <<  class data >> (g.app.config)
    #@+others
    #@+node:ekr.20041117062717.1: *4* defaultsDict
    #@+at This contains only the "interesting" defaults.
    # Ints and bools default to 0, floats to 0.0 and strings to "".
    #@@c

    defaultBodyFontSize = g.choose(sys.platform=="win32",9,12)
    defaultLogFontSize  = g.choose(sys.platform=="win32",8,12)
    defaultMenuFontSize = g.choose(sys.platform=="win32",9,12)
    defaultTreeFontSize = g.choose(sys.platform=="win32",9,12)

    defaultsDict = {'_hash':'defaultsDict'}

    defaultsData = (
        # compare options...
        ("ignore_blank_lines","bool",True),
        ("limit_count","int",9),
        ("print_mismatching_lines","bool",True),
        ("print_trailing_lines","bool",True),
        # find/change options...
        ("search_body","bool",True),
        ("whole_word","bool",True),
        # Prefs panel.
        # ("default_target_language","language","python"),
        ("target_language","language","python"), # Bug fix: 6/20,2005.
        ("tab_width","int",-4),
        ("page_width","int",132),
        ("output_doc_chunks","bool",True),
        ("tangle_outputs_header","bool",True),
        # Syntax coloring options...
        # Defaults for colors are handled by leoColor.py.
        ("color_directives_in_plain_text","bool",True),
        ("underline_undefined_section_names","bool",True),
        # Window options...
        ("allow_clone_drags","bool",True),
        ("body_pane_wraps","bool",True),
        ("body_text_font_family","family","Courier"),
        ("body_text_font_size","size",defaultBodyFontSize),
        ("body_text_font_slant","slant","roman"),
        ("body_text_font_weight","weight","normal"),
        ("enable_drag_messages","bool",True),
        ("headline_text_font_family","string",None),
        ("headline_text_font_size","size",defaultLogFontSize),
        ("headline_text_font_slant","slant","roman"),
        ("headline_text_font_weight","weight","normal"),
        ("log_text_font_family","string",None),
        ("log_text_font_size","size",defaultLogFontSize),
        ("log_text_font_slant","slant","roman"),
        ("log_text_font_weight","weight","normal"),
        ("initial_window_height","int",600),
        ("initial_window_width","int",800),
        ("initial_window_left","int",10),
        ("initial_window_top","int",10),
        ("initial_splitter_orientation","string","vertical"),
        ("initial_vertical_ratio","ratio",0.5),
        ("initial_horizontal_ratio","ratio",0.3),
        ("initial_horizontal_secondary_ratio","ratio",0.5),
        ("initial_vertical_secondary_ratio","ratio",0.7),
        ("outline_pane_scrolls_horizontally","bool",False),
        ("split_bar_color","color","LightSteelBlue2"),
        ("split_bar_relief","relief","groove"),
        ("split_bar_width","int",7),
    )
    #@+node:ekr.20041118062709: *4* define encodingIvarsDict
    encodingIvarsDict = {'_hash':'encodingIvarsDict'}

    encodingIvarsData = (
        ("default_at_auto_file_encoding","string","utf-8"),
        ("default_derived_file_encoding","string","utf-8"),
        ("new_leo_file_encoding","string","UTF-8"),
            # Upper case for compatibility with previous versions.
        ("defaultEncoding","string",None),
            # Defaults to None so it doesn't override better defaults.
    )
    #@+node:ekr.20041117072055: *4* ivarsDict
    # Each of these settings sets the corresponding ivar.
    # Also, the c.configSettings settings class inits the corresponding commander ivar.
    ivarsDict = {'_hash':'ivarsDict'}

    ivarsData = (
        ("at_root_bodies_start_in_doc_mode","bool",True),
            # For compatibility with previous versions.
        ("create_nonexistent_directories","bool",False),
        ("output_initial_comment","string",""),
            # "" for compatibility with previous versions.
        ("output_newline","string","nl"),
        ("page_width","int","132"),
        ("read_only","bool",True),
            # Make sure we don't alter an illegal leoConfig.txt file!
        ("redirect_execute_script_output_to_log_pane","bool",False),
        ("relative_path_base_directory","string","!"),
        ("remove_sentinels_extension","string",".txt"),
        ("save_clears_undo_buffer","bool",False),
        ("stylesheet","string",None),
        ("tab_width","int",-4),
        ("target_language","language","python"), # Bug fix: added: 6/20/2005.
        ("trailing_body_newlines","string","asis"),
        ("use_plugins","bool",True),
            # New in 4.3: use_plugins = True by default.
        # use_pysco can not be set by 4.3:  config processing happens too late.
            # ("use_psyco","bool",False),
        ("undo_granularity","string","word"),
            # "char","word","line","node"
        ("write_strips_blank_lines","bool",False),
    )
    #@-others

    # List of dictionaries to search.  Order not too important.
    dictList = [ivarsDict,encodingIvarsDict,defaultsDict]

    # Keys are commanders.  Values are optionsDicts.
    localOptionsDict = {}

    localOptionsList = []

    # Keys are setting names, values are type names.
    warningsDict = {} # Used by get() or allies.
    #@-<< class data >>
    #@+others
    #@+node:ekr.20041117083202: *3* Birth... (g.app.config)
    #@+node:ekr.20041117062717.2: *4* ctor (configClass)
    def __init__ (self):

        # g.trace('g.app.config')
        self.atCommonButtonsList = [] # List of info for common @buttons nodes.
        self.atCommonCommandsList = [] # List of info for common @commands nodes.
        self.buttonsFileName = ''
        self.configsExist = False # True when we successfully open a setting file.
        self.defaultFont = None # Set in gui.getDefaultConfigFont.
        self.defaultFontFamily = None # Set in gui.getDefaultConfigFont.
        self.enabledPluginsFileName = None
        self.enabledPluginsString = '' 
        self.globalConfigFile = None # Set in initSettingsFiles
        self.homeFile = None # Set in initSettingsFiles
        self.inited = False
        self.menusList = []
        self.menusFileName = ''
        self.modeCommandsDict = {}
            # For use by @mode logic. Keys are command names, values are g.Bunches.
            # A special key: *mode-prompt* it the prompt to be given.
        self.myGlobalConfigFile = None
        self.myHomeConfigFile = None
        self.machineConfigFile = None
        self.recentFilesFiles = [] # List of g.Bunches describing .leoRecentFiles.txt files.
        self.write_recent_files_as_needed = False # Will be set later.
        self.silent = g.app.silentMode
        # g.trace('c.config.silent',self.silent)

        # Inited later...
        self.panes = None
        self.sc = None
        self.tree = None

        self.initDicts()
        self.initIvarsFromSettings()
        self.initSettingsFiles()
        self.initRecentFiles()
    #@+node:ekr.20041227063801.2: *4* initDicts
    def initDicts (self):

        # Only the settings parser needs to search all dicts.
        self.dictList = [self.defaultsDict]

        for key,kind,val in self.defaultsData:
            self.defaultsDict[self.munge(key)] = g.Bunch(
                setting=key,kind=kind,val=val,tag='defaults')

        for key,kind,val in self.ivarsData:
            self.ivarsDict[self.munge(key)] = g.Bunch(
                ivar=key,kind=kind,val=val,tag='ivars')

        for key,kind,val in self.encodingIvarsData:
            self.encodingIvarsDict[self.munge(key)] = g.Bunch(
                ivar=key,kind=kind,encoding=val,tag='encodings')
    #@+node:ekr.20041117065611.2: *4* initIvarsFromSettings & helpers
    def initIvarsFromSettings (self):

        trace = False and not g.unitTesting
        if trace: g.trace('-' * 20,g.callers())

        for ivar in self.encodingIvarsDict:
            if ivar != '_hash':
                self.initEncoding(ivar)

        for ivar in self.ivarsDict:
            if ivar != '_hash':
                self.initIvar(ivar)
    #@+node:ekr.20041117065611.1: *5* initEncoding
    def initEncoding (self,key):

        '''Init g.app.config encoding ivars during initialization.'''

        # N.B. The key is munged.
        bunch = self.encodingIvarsDict.get(key)
        encoding = bunch.encoding
        ivar = bunch.ivar
        # g.trace('g.app.config',ivar,encoding)
        setattr(self,ivar,encoding)

        if encoding and not g.isValidEncoding(encoding):
            g.es("g.app.config: bad encoding:","%s: %s" % (ivar,encoding))
    #@+node:ekr.20041117065611: *5* initIvar
    def initIvar(self,key):

        '''Init g.app.config ivars during initialization.

        This does NOT init the corresponding commander ivars.

        Such initing must be done in setIvarsFromSettings.'''

        trace = False and not g.unitTesting

        # N.B. The key is munged.
        bunch = self.ivarsDict.get(key)
        ivar = bunch.ivar # The actual name of the ivar.
        val = bunch.val

        if trace: g.trace('g.app.config',ivar,key,val)
        setattr(self,ivar,val)
    #@+node:ekr.20041117083202.2: *4* initRecentFiles
    def initRecentFiles (self):

        self.recentFiles = []
    #@+node:ekr.20041117083857: *4* initSettingsFiles
    def initSettingsFiles (self):

        """Set self.globalConfigFile, self.homeFile, self.myGlobalConfigFile,
        self.myHomeConfigFile, and self.machineConfigFile."""

        settingsFile = 'leoSettings.leo'
        mySettingsFile = 'myLeoSettings.leo'
        machineConfigFile = g.computeMachineName() + 'LeoSettings.leo'

        # New in Leo 4.5 b4: change homeDir to homeLeoDir
        for ivar,theDir,fileName in (
            ('globalConfigFile',    g.app.globalConfigDir,  settingsFile),
            ('homeFile',            g.app.homeLeoDir,       settingsFile),
            ('myGlobalConfigFile',  g.app.globalConfigDir,  mySettingsFile),
            #non-prefixed names take priority over prefixed names
            ('myHomeConfigFile',    g.app.homeLeoDir,   g.app.homeSettingsPrefix + mySettingsFile),
            ('myHomeConfigFile',    g.app.homeLeoDir,   mySettingsFile),
            ('machineConfigFile',   g.app.homeLeoDir,   g.app.homeSettingsPrefix + machineConfigFile),
            ('machineConfigFile',   g.app.homeLeoDir,   machineConfigFile),
        ):
            # The same file may be assigned to multiple ivars:
            # readSettingsFiles checks for such duplications.
            path = g.os_path_join(theDir,fileName)
            if g.os_path_exists(path):
                setattr(self,ivar,path)
            #else:
                #if the path does not exist, only set to None if the ivar isn't already set.
                #dan: IMO, it's better to set the defaults to None in configClass.__init__().
                #     This avoids the creation of ivars in odd (non __init__) places.
                #setattr(self,ivar, getattr(self,ivar,None))
        if 0:
            g.trace('global file:',self.globalConfigFile)
            g.trace('home file:',self.homeFile)
            g.trace('myGlobal file:',self.myGlobalConfigFile)
            g.trace('myHome file:',self.myHomeConfigFile)
    #@+node:ekr.20041117081009: *3* Getters... (g.app.config)
    #@+node:ekr.20041123070429: *4* canonicalizeSettingName (munge)
    def canonicalizeSettingName (self,name):

        if name is None:
            return None

        name = name.lower()
        for ch in ('-','_',' ','\n'):
            name = name.replace(ch,'')

        return g.choose(name,name,None)

    munge = canonicalizeSettingName
    #@+node:ekr.20041123092357: *4* config.findSettingsPosition
    # This was not used prior to Leo 4.5.

    def findSettingsPosition (self,c,setting):

        """Return the position for the setting in the @settings tree for c."""

        munge = self.munge

        root = self.settingsRoot(c)
        if not root:
            return c.nullPosition()

        setting = munge(setting)

        for p in root.subtree():
            #BJ munge will return None if a headstring is empty
            h = munge(p.h) or ''
            if h.startswith(setting):
                return p.copy()

        return c.nullPosition()
    #@+node:ekr.20051011105014: *4* exists (g.app.config)
    def exists (self,c,setting,kind):

        '''Return true if a setting of the given kind exists, even if it is None.'''

        if c:
            d = self.localOptionsDict.get(c.hash())
            if d:
                junk,found = self.getValFromDict(d,setting,kind)
                if found: return True

        for d in self.localOptionsList:
            junk,found = self.getValFromDict(d,setting,kind)
            if found: return True

        for d in self.dictList:
            junk,found = self.getValFromDict(d,setting,kind)
            if found: return True

        # g.trace('does not exist',setting,kind)
        return False
    #@+node:ekr.20041117083141: *4* get & allies (g.app.config)
    def get (self,c,setting,kind):

        """Get the setting and make sure its type matches the expected type."""

        trace = False and not g.unitTesting and setting == 'create_nonexistent_directories'
        if trace: g.pdb()

        isLeoSettings = c and c.shortFileName().endswith('leoSettings.leo')

        # New in Leo 4.6. Use settings in leoSettings.leo *last*.
        if c and not isLeoSettings:
            d = self.localOptionsDict.get(c.hash())
            if d:
                val,junk = self.getValFromDict(d,setting,kind)
                if val is not None:
                    # if setting == 'targetlanguage':
                        # g.trace(c.shortFileName(),setting,val,g.callers())
                    return val

        for d in self.localOptionsList:
            val,junk = self.getValFromDict(d,setting,kind)
            if val is not None:
                kind = d.get('_hash','<no hash>')
                # if setting == 'targetlanguage':
                    # g.trace(kind,setting,val,g.callers())
                return val

        for d in self.dictList:
            val,junk = self.getValFromDict(d,setting,kind)
            if val is not None:
                kind = d.get('_hash','<no hash>')
                # if setting == 'targetlanguage':
                    # g.trace(kind,setting,val,g.callers())
                return val

        # New in Leo 4.6. Use settings in leoSettings.leo *last*.
        if c and isLeoSettings:
            d = self.localOptionsDict.get(c.hash())
            if d:
                val,junk = self.getValFromDict(d,setting,kind)
                if val is not None:
                    # if setting == 'targetlanguage':
                        # g.trace(c.shortFileName(),setting,val,g.callers())
                    return val

        return None
    #@+node:ekr.20041121143823: *5* getValFromDict
    def getValFromDict (self,d,setting,requestedType,warn=True):

        '''Look up the setting in d. If warn is True, warn if the requested type
        does not (loosely) match the actual type.
        returns (val,exists)'''

        bunch = d.get(self.munge(setting))
        if not bunch: return None,False

        # g.trace(setting,requestedType,bunch.toString())
        val = bunch.val

        if g.isPython3:
            isNone = val in ('None','none','',None)
        else:
            isNone = val in (
                unicode('None'),unicode('none'),unicode(''),
                'None','none','',None)

        if not self.typesMatch(bunch.kind,requestedType):
            # New in 4.4: make sure the types match.
            # A serious warning: one setting may have destroyed another!
            # Important: this is not a complete test of conflicting settings:
            # The warning is given only if the code tries to access the setting.
            if warn:
                g.es_print('warning: ignoring',bunch.kind,'',setting,'is not',requestedType,color='red')
                g.es_print('there may be conflicting settings!',color='red')
            return None, False
        # elif val in (u'None',u'none','None','none','',None):
        elif isNone:
            return None, True # Exists, but is None
        else:
            # g.trace(setting,val)
            return val, True
    #@+node:ekr.20051015093141: *5* typesMatch
    def typesMatch (self,type1,type2):

        '''
        Return True if type1, the actual type, matches type2, the requeseted type.

        The following equivalences are allowed:

        - None matches anything.
        - An actual type of string or strings matches anything *except* shortcuts.
        - Shortcut matches shortcuts.
        '''

        shortcuts = ('shortcut','shortcuts',)

        return (
            type1 == None or type2 == None or
            type1.startswith('string') and type2 not in shortcuts or
            type1 == 'int' and type2 == 'size' or
            (type1 in shortcuts and type2 in shortcuts) or
            type1 == type2
        )
    #@+node:ekr.20060608224112: *4* getAbbrevDict
    def getAbbrevDict (self,c):

        """Search all dictionaries for the setting & check it's type"""

        d = self.get(c,'abbrev','abbrev')
        return d or {}
    #@+node:ekr.20041117081009.3: *4* getBool
    def getBool (self,c,setting,default=None):

        '''Return the value of @bool setting, or the default if the setting is not found.'''

        val = self.get(c,setting,"bool")

        if val in (True,False):
            return val
        else:
            return default
    #@+node:ekr.20070926082018: *4* getButtons
    def getButtons (self):

        '''Return a list of tuples (x,y) for common @button nodes.'''

        return g.app.config.atCommonButtonsList
    #@+node:ekr.20041122070339: *4* getColor
    def getColor (self,c,setting):

        '''Return the value of @color setting.'''

        return self.get(c,setting,"color")
    #@+node:ekr.20080312071248.7: *4* getCommonCommands
    def getCommonAtCommands (self):

        '''Return the list of tuples (headline,script) for common @command nodes.'''

        return g.app.config.atCommonCommandsList
    #@+node:ekr.20071214140900.1: *4* getData
    def getData (self,c,setting):

        '''Return a list of non-comment strings in the body text of @data setting.'''

        return self.get(c,setting,"data")
    #@+node:ekr.20041117093009.1: *4* getDirectory
    def getDirectory (self,c,setting):

        '''Return the value of @directory setting, or None if the directory does not exist.'''

        theDir = self.getString(c,setting)

        if g.os_path_exists(theDir) and g.os_path_isdir(theDir):
             return theDir
        else:
            return None
    #@+node:ekr.20070224075914.1: *4* getEnabledPlugins
    def getEnabledPlugins (self):

        '''Return the body text of the @enabled-plugins node.'''

        return g.app.config.enabledPluginsString
    #@+node:ekr.20041117082135: *4* getFloat
    def getFloat (self,c,setting):

        '''Return the value of @float setting.'''

        val = self.get(c,setting,"float")
        try:
            val = float(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20041117062717.13: *4* getFontFromParams (config)
    def getFontFromParams(self,c,family,size,slant,weight,defaultSize=12):

        """Compute a font from font parameters.

        Arguments are the names of settings to be use.
        Default to size=12, slant="roman", weight="normal".

        Return None if there is no family setting so we can use system default fonts."""

        family = self.get(c,family,"family")
        if family in (None,""):
            family = self.defaultFontFamily

        size = self.get(c,size,"size")
        if size in (None,0): size = defaultSize

        slant = self.get(c,slant,"slant")
        if slant in (None,""): slant = "roman"

        weight = self.get(c,weight,"weight")
        if weight in (None,""): weight = "normal"

        # g.trace(g.callers(3),family,size,slant,weight,g.shortFileName(c.mFileName))

        return g.app.gui.getFontFromParams(family,size,slant,weight)
    #@+node:ekr.20041117081513: *4* getInt
    def getInt (self,c,setting):

        '''Return the value of @int setting.'''

        val = self.get(c,setting,"int")
        try:
            val = int(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20041117093009.2: *4* getLanguage
    def getLanguage (self,c,setting):

        '''Return the setting whose value should be a language known to Leo.'''

        language = self.getString(c,setting)
        # g.trace(setting,language)

        return language
    #@+node:ekr.20070926070412: *4* getMenusList (c.config)
    def getMenusList (self,c):

        '''Return the list of entries for the @menus tree.'''

        aList = self.get(c,'menus','menus')
        # g.trace(aList and len(aList) or 0)

        return aList or g.app.config.menusList
    #@+node:ekr.20070411101643: *4* getOpenWith
    def getOpenWith (self,c):

        '''Return a list of dictionaries corresponding to @openwith nodes.'''

        val = self.get(c,'openwithtable','openwithtable')

        return val
    #@+node:ekr.20041122070752: *4* getRatio
    def getRatio (self,c,setting):

        '''Return the value of @float setting.

        Warn if the value is less than 0.0 or greater than 1.0.'''

        val = self.get(c,setting,"ratio")
        try:
            val = float(val)
            if 0.0 <= val <= 1.0:
                return val
            else:
                return None
        except TypeError:
            return None
    #@+node:ekr.20041117062717.11: *4* getRecentFiles
    def getRecentFiles (self):

        '''Return the list of recently opened files.'''

        return self.recentFiles
    #@+node:ekr.20080917061525.3: *4* getSettingSource (g.app.config)
    def getSettingSource (self,c,setting):

        '''return the name of the file responsible for setting.'''

        aList = [self.localOptionsDict.get(c.hash())]
        aList.extend(self.localOptionsList)
        aList.extend(self.dictList)

        for d in aList:
            if d:
                bunch = d.get(setting)
                if bunch is not None:
                    return bunch.path,bunch.val
        else:
            return 'unknown setting',None
    #@+node:ekr.20041117062717.14: *4* getShortcut (config)
    def getShortcut (self,c,shortcutName):

        '''Return rawKey,accel for shortcutName'''

        key = c.frame.menu.canonicalizeMenuName(shortcutName)
        key = key.replace('&','') # Allow '&' in names.

        bunchList = self.get(c,key,"shortcut")
        # g.trace('bunchList',bunchList)
        if bunchList:
            bunchList = [bunch for bunch in bunchList
                if bunch.val and bunch.val.lower() != 'none']
            return key,bunchList
        else:
            return key,[]
    #@+node:ekr.20041117081009.4: *4* getString
    def getString (self,c,setting):

        '''Return the value of @string setting.'''

        return self.get(c,setting,"string")
    #@+node:ekr.20041120074536: *4* settingsRoot
    def settingsRoot (self,c):

        '''Return the position of the @settings tree.'''

        # g.trace(c,c.rootPosition())

        for p in c.all_unique_positions():
            if p.h.rstrip() == "@settings":
                return p.copy()
        else:
            return c.nullPosition()
    #@+node:ekr.20100616083554.5922: *3* Iterators... (g.app.config)
    def config_iter(self,c):

        '''Letters:
          leoSettings.leo
        D default settings
        F loaded .leo File
        M myLeoSettings.leo
        '''

        names = [] # Already-handled settings names.
        result = []

        if c:
            d = self.localOptionsDict.get(c.hash())
            for name,val,letter in self.config_iter_helper(d,names):
                result.append((name,val,c,'F'),)

        for d in self.localOptionsList:
            for name,val,letter in self.config_iter_helper(d,names):
                result.append((name,val,None,letter),)

        for d in self.dictList:
            for name,val,letter in self.config_iter_helper(d,names):
                result.append((name,val,None,letter),)

        result.sort()
        for z in result:
            yield z

        raise StopIteration
    #@+node:ekr.20100616083554.5923: *4* config_iter_helper
    def config_iter_helper (self,d,names):

        if not d: return []

        result = []
        suppressKind = ('shortcut','shortcuts','openwithtable')
        suppressKeys = (None,'_hash','shortcut')
        theHash = d.get('_hash').lower()

        if theHash.endswith('myleosettings.leo'):
            letter = 'M'
        elif theHash.endswith('leosettings.leo'):
            letter = ' '
        else:
            letter = 'D' # Default setting.

        for key in d:
            if key not in suppressKeys and key not in names:
                bunch = d.get(key)
                if bunch and bunch.kind not in suppressKind:
                    names.append(key)
                    result.append((key,bunch.val,letter),)

        return result
    #@+node:ekr.20041118084146: *3* Setters (g.app.config)
    #@+node:ekr.20041118084146.1: *4* set (g.app.config)
    def set (self,c,setting,kind,val):

        '''Set the setting.  Not called during initialization.'''

        trace = False and not g.unitTesting # and setting == 'create_nonexistent_directories'
        # if trace: g.pdb()

        found = False ;  key = self.munge(setting)
        if trace: g.trace(setting,kind,val)

        if c:
            d = self.localOptionsDict.get(c.hash())
            found = True # Bug fix: 2010/08/30.

        if not found:
            theHash = c.hash()
            for d in self.localOptionsList:
                hash2 = d.get('_hash')
                if theHash == hash2:
                    found = True ; break

        if not found:
            d = self.dictList [0]

        d[key] = g.Bunch(setting=setting,kind=kind,val=val,tag='setting')

        if 0:
            dkind = d.get('_hash','<no hash: %s>' % c.hash())
            g.trace(dkind,setting,kind,val)
    #@+node:ekr.20041118084241: *4* setString
    def setString (self,c,setting,val):

        self.set(c,setting,"string",val)
    #@+node:ekr.20041228042224: *4* setIvarsFromSettings (g.app.config)
    def setIvarsFromSettings (self,c):

        '''Init g.app.config ivars or c's ivars from settings.

        - Called from readSettingsFiles with c = None to init g.app.config ivars.
        - Called from c.__init__ to init corresponding commmander ivars.'''

        trace = False and not g.unitTesting
        verbose = False

        if not self.inited: return

        # Ignore temporary commanders created by readSettingsFiles.
        if trace and verbose: g.trace('*' * 10)
        if trace: g.trace(
            'inited',self.inited,
            c and c.shortFileName() or '<no c>',g.callers(2))

        d = self.ivarsDict
        keys = list(d.keys())
        keys.sort()
        for key in keys:
            if key != '_hash':
                bunch = d.get(key)
                if bunch:
                    ivar = bunch.ivar # The actual name of the ivar.
                    kind = bunch.kind
                    val = self.get(c,key,kind) # Don't use bunch.val!
                    if c:
                        if trace and verbose: g.trace("%20s %s = %s" % (
                            g.shortFileName(c.mFileName),ivar,val))
                        setattr(c,ivar,val)
                    else:
                        if trace and verbose: g.trace("%20s %s = %s" % (
                            'g.app.config',ivar,val))
                        setattr(self,ivar,val)
    #@+node:ekr.20041201080436: *4* appendToRecentFiles (g.app.config)
    def appendToRecentFiles (self,files):

        files = [theFile.strip() for theFile in files]

        # g.trace(files)

        def munge(name):
            name = name or ''
            return g.os_path_normpath(name).lower()

        for name in files:
            # Remove all variants of name.
            for name2 in self.recentFiles[:]:
                if munge(name) == munge(name2):
                    self.recentFiles.remove(name2)

            self.recentFiles.append(name)
    #@+node:ekr.20041117093246: *3* Scanning @settings (g.app.config)
    #@+node:ekr.20041120064303: *4* readSettingsFiles & helpers (g.app.config)
    def readSettingsFiles (self,fileName,verbose=True):

        '''Read settings from one file or the standard settings files.'''

        trace = False and not g.unitTesting
        verbose = verbose or trace
        giveMessage = (verbose and not g.app.unitTesting and
            not self.silent and not g.app.batchMode)
        if trace: g.trace(fileName,g.callers())
        self.write_recent_files_as_needed = False # Will be set later.
        localConfigFile = self.getLocalConfigFile(fileName)
        table = self.defineSettingsTable(fileName,localConfigFile)
        for path,localFlag in table:
            assert path and g.os_path_exists(path)
            isZipped = path and zipfile.is_zipfile(path)
            isLeo = isZipped or path.endswith('.leo')
            if isLeo:
                if giveMessage:
                    s = 'reading settings in %s' % path
                    # This occurs early in startup, so use the following instead of g.es_print.
                    if not g.isPython3:
                        s = g.toEncodedString(s,'ascii')
                    g.es_print(s,color='blue')
                c = self.openSettingsFile(path)
                if c:
                    self.updateSettings(c,localFlag)
                    g.app.destroyWindow(c.frame)
                    self.write_recent_files_as_needed = c.config.getBool(
                        'write_recent_files_as_needed')

        self.readRecentFiles(localConfigFile)
        self.inited = True
        self.setIvarsFromSettings(None)
    #@+node:ekr.20101021041958.6008: *5* getLocalConfigFile
    # This can't be done in initSettingsFiles because
    # the local directory does not yet exist.

    def getLocalConfigFile (self,fileName):

        if not fileName:
            return None

        theDir = g.os_path_dirname(fileName)
        path = g.os_path_join(theDir,'leoSettings.leo')

        if g.os_path_exists(path):
            return path
        else:
            return None
    #@+node:ekr.20101021041958.6004: *5* defineSettingsTable
    def defineSettingsTable (self,fileName,localConfigFile):

        global_table = (
            (self.globalConfigFile,False),
            (self.homeFile,False),
            # (localConfigFile,False),
            (self.myGlobalConfigFile,False),
            (self.myHomeConfigFile,False),
            (self.machineConfigFile,False),
            # (myLocalConfigFile,False),
            # New in Leo 4.6: the -c file is in *addition* to other config files.
            (g.app.oneConfigFilename,False),
        )

        if fileName:
            path = g.os_path_finalize(fileName)
            theDir = g.os_path_dirname(fileName)
            myLocalConfigFile = g.os_path_join(theDir,'myLeoSettings.leo')
            local_table = (
                (localConfigFile,False),
                (myLocalConfigFile,False),
            )
            table1 = [z for z in global_table if z not in global_table]
            table1.append((path,True),)
        else:
            table1 = global_table

        seen = [] ; table = []
        for path,localFlag in table1:
            if path and g.os_path_exists(path):
                # Make sure we mark files seen no matter how they are specified.
                path = g.os_path_realpath(g.os_path_finalize(path))
                if path.lower() not in seen:
                    seen.append(path.lower())
                    table.append((path,localFlag),)
        # g.trace(table)
        return table
    #@+node:ekr.20041117085625: *5* openSettingsFile
    def openSettingsFile (self,path):

        theFile,isZipped = g.openLeoOrZipFile(path)
        if not theFile: return None

        # Similar to g.openWithFileName except it uses a null gui.
        # Changing g.app.gui here is a major hack.
        oldGui = g.app.gui
        g.app.gui = leoGui.nullGui("nullGui")
        c,frame = g.app.newLeoCommanderAndFrame(
            fileName=path,relativeFileName=None,
            initEditCommanders=False,updateRecentFiles=False)
        frame.log.enable(False)
        g.app.lockLog()
        ok = frame.c.fileCommands.open(
            theFile,path,readAtFileNodesFlag=False,silent=True) # closes theFile.
        g.app.unlockLog()
        c.openDirectory = frame.openDirectory = g.os_path_dirname(path)
        g.app.gui = oldGui
        return ok and c
    #@+node:ekr.20051013161232: *5* updateSettings
    def updateSettings (self,c,localFlag):

        # g.trace(localFlag,c)

        d = self.readSettings(c,localFlag)

        if d:
            d['_hash'] = theHash = c.hash()
            if localFlag:
                self.localOptionsDict[theHash] = d
            else:
                self.localOptionsList.insert(0,d)

        if 0: # Good trace.
            if localFlag:
                g.trace(c.fileName())
                g.trace(d and list(d.keys()))
    #@+node:ekr.20041117083857.1: *4* g.app.config.readSettings
    # Called to read all leoSettings.leo files.
    # Also called when opening an .leo file to read @settings tree.

    def readSettings (self,c,localFlag):

        """Read settings from a file that may contain an @settings tree."""

        trace = False and not g.unitTesting
        if trace: g.trace('=' * 20, c and c.fileName())

        # Create a settings dict for c for set()
        if c and self.localOptionsDict.get(c.hash()) is None:
            self.localOptionsDict[c.hash()] = {}

        parser = settingsTreeParser(c,localFlag)
        d = parser.traverse()

        return d
    #@+node:ekr.20050424114937.1: *3* Reading and writing .leoRecentFiles.txt (g.app.config)
    #@+node:ekr.20070224115832: *4* readRecentFiles & helpers
    def readRecentFiles (self,localConfigFile):

        '''Read all .leoRecentFiles.txt files.'''

        # The order of files in this list affects the order of the recent files list.
        seen = [] 
        localConfigPath = g.os_path_dirname(localConfigFile)
        for path in (
            g.app.homeLeoDir, # was homeDir
            g.app.globalConfigDir,
            localConfigPath,
        ):
            if path:
                path = g.os_path_realpath(g.os_path_finalize(path))
            if path and path not in seen:
                ok = self.readRecentFilesFile(path)
                if ok: seen.append(path)
        if not seen and self.write_recent_files_as_needed:
            self.createRecentFiles()
    #@+node:ekr.20061010121944: *5* createRecentFiles
    def createRecentFiles (self):

        '''Trye to reate .leoRecentFiles.txt in
        - the users home directory first,
        - Leo's config directory second.'''

        for theDir in (g.app.homeLeoDir,g.app.globalConfigDir): # homeLeoDir was g.app.homeDir.
            if theDir:
                try:
                    fileName = g.os_path_join(theDir,'.leoRecentFiles.txt')
                    f = open(fileName,'w')
                    f.close()
                    g.es_print('created',fileName,color='red')
                    return
                except Exception:
                    g.es_print('can not create',fileName,color='red')
                    g.es_exception()
    #@+node:ekr.20050424115658: *5* readRecentFilesFile
    def readRecentFilesFile (self,path):

        fileName = g.os_path_join(path,'.leoRecentFiles.txt')
        ok = g.os_path_exists(fileName)
        if ok:
            try:
                if g.isPython3:
                    f = open(fileName,encoding='utf-8',mode='r')
                else:
                    f = open(fileName,'r')
            except IOError:
                g.trace('can not open',fileName)
                return False
            if 0:
                if not g.unitTesting and not self.silent:
                    g.pr(('reading %s' % fileName))
            lines = f.readlines()
            if lines and self.munge(lines[0])=='readonly':
                lines = lines[1:]
            if lines:
                lines = [g.toUnicode(g.os_path_normpath(line)) for line in lines]
                self.appendToRecentFiles(lines)

        return ok
    #@+node:ekr.20050424114937.2: *4* writeRecentFilesFile & helper
    recentFileMessageWritten = False

    def writeRecentFilesFile (self,c):

        '''Write the appropriate .leoRecentFiles.txt file.'''

        tag = '.leoRecentFiles.txt'

        if g.app.unitTesting:
            return

        localFileName = c.fileName()
        if localFileName:
            localPath,junk = g.os_path_split(localFileName)
        else:
            localPath = None

        written = False
        seen = []
        for path in (localPath,g.app.globalConfigDir,g.app.homeLeoDir): # homeLeoDir was homeDir.
            if path:
                fileName = g.os_path_join(path,tag)
                if g.os_path_exists(fileName) and not fileName.lower() in seen:
                    seen.append(fileName.lower())
                    ok = self.writeRecentFilesFileHelper(fileName)
                    if not self.recentFileMessageWritten:
                        if ok:
                            g.pr('wrote recent file: %s' % fileName)
                            written = True
                        else:
                            g.pr('failed to recent file: %s' % (fileName),color='red')
                    # Bug fix: Leo 4.4.6: write *all* recent files.

        if written:
            self.recentFileMessageWritten = True
        else:
            pass # g.trace('----- not found: %s' % g.os_path_join(localPath,tag))
    #@+node:ekr.20050424131051: *5* writeRecentFilesFileHelper
    def writeRecentFilesFileHelper (self,fileName):

        # g.trace(g.toUnicode(fileName))

        # Don't update the file if it begins with read-only.
        theFile = None
        try:
            theFile = open(fileName)
            lines = theFile.readlines()
            if lines and self.munge(lines[0])=='readonly':
                # g.trace('read-only: %s' %fileName)
                return False
        except IOError:
            # The user may have erased a file.  Not an error.
            if theFile: theFile.close()

        theFile = None
        try:
            if g.isPython3:
                theFile = open(fileName,encoding='utf-8',mode='w')
            else:
                theFile = open(fileName,mode='w')
            if self.recentFiles:
                s = '\n'.join(self.recentFiles)
            else:
                s = '\n'
            if not g.isPython3:
                s = g.toEncodedString(s,reportErrors=True)
            theFile.write(s)

        except IOError:
            if 1: # The user may have erased a file.  Not an error.
                g.es_print('error writing',fileName,color='red')
                g.es_exception()
                return False

        except Exception:
            g.es('unexpected exception writing',fileName,color='red')
            g.es_exception()
            if g.unitTesting: raise
            return False

        if theFile:
            theFile.close()
            return True
        else:
            return False
    #@+node:ekr.20070418073400: *3* g.app.config.printSettings
    def printSettings (self,c):

        '''Prints the value of every setting, except key bindings and commands and open-with tables.
        The following shows where the active setting came from:

        -     leoSettings.leo,
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,

        '''

        legend = '''\
        legend:
        leoSettings.leo
    [D] default settings
    [F] loaded .leo File
    [M] myLeoSettings.leo
    '''
        legend = g.adjustTripleString(legend,c.tab_width)
        result = []
        for name,val,c,letter in self.config_iter(c):
            kind = g.choose(letter==' ','   ','[%s]' % (letter))
            result.append('%s %s = %s\n' % (kind,name,val))

        # Use a single g.es statement.
        result.append('\n'+legend)
        g.es('',''.join(result),tabName='Settings')
    #@-others
#@+node:ekr.20041119203941.3: ** class settingsTreeParser (parserBaseClass)
class settingsTreeParser (parserBaseClass):

    '''A class that inits settings found in an @settings tree.

    Used by read settings logic.'''

    #@+others
    #@+node:ekr.20041119204103: *3* ctor
    def __init__ (self,c,localFlag=True):

        # Init the base class.
        parserBaseClass.__init__(self,c,localFlag)
    #@+node:ekr.20041119204714: *3* visitNode (settingsTreeParser)
    def visitNode (self,p):

        """Init any settings found in node p."""

        # g.trace(p.h)

        munge = g.app.config.munge

        kind,name,val = self.parseHeadline(p.h)
        kind = munge(kind)

        if g.isPython3:
            isNone = val in ('None','none','',None)
        else:
            isNone = val in (
                unicode('None'),unicode('none'),unicode(''),
                'None','none','',None)

        if kind is None: # Not an @x node. (New in Leo 4.4.4)
            pass
        if kind == "settings":
            pass
        # elif kind in self.basic_types and val in (u'None',u'none','None','none','',None):
        elif kind in self.basic_types and isNone:
            # None is valid for all basic types.
            self.set(p,kind,name,None)
        elif kind in self.control_types or kind in self.basic_types:
            f = self.dispatchDict.get(kind)
            if f:
                try:
                    return f(p,kind,name,val)
                except Exception:
                    g.es_exception()
            else:
                g.pr("*** no handler",kind)

        return None
    #@-others
#@-others
#@-leo

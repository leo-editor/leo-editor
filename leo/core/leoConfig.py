#@+leo-ver=5-thin
#@+node:ekr.20130925160837.11429: * @file leoConfig.py
#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@+<< imports >>
#@+node:ekr.20041227063801: ** << imports >> (leoConfig)
import leo.core.leoGlobals as g

import sys
#@-<< imports >>

#@+<< class ParserBaseClass >>
#@+node:ekr.20041119203941.2: ** << class ParserBaseClass >>
class ParserBaseClass:

    """The base class for settings parsers."""

    #@+<< ParserBaseClass data >>
    #@+node:ekr.20041121130043: *3* << ParserBaseClass data >>
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
    #@-<< ParserBaseClass data >>

    #@+others
    #@+node:ekr.20041119204700: *3*  ctor (ParserBaseClass)
    def __init__ (self,c,localFlag):

        self.c = c
        self.localFlag = localFlag
            # True if this is the .leo file being opened,
            # as opposed to myLeoSettings.leo or leoSettings.leo.

        self.shortcutsDict = g.TypedDictOfLists(
            name='parser.shortcutsDict',
            keyType=type('shortcutName'),valType=g.ShortcutInfo)

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
            'popup':        self.doPopup, # New in 4.4.8
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
    #@+node:ekr.20080514084054.4: *3* computeModeName (ParserBaseClass)
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
    #@+node:ekr.20060102103625: *3* createModeCommand (ParserBaseClass)
    def createModeCommand (self,modeName,name,modeDict):

        modeName = 'enter-' + modeName.replace(' ','-')

        i = name.find('::')
        if i > -1:
            # The prompt is everything after the '::'
            prompt = name[i+2:].strip()
            modeDict ['*command-prompt*'] = g.ShortcutInfo(kind=prompt)

        # Save the info for k.finishCreate and k.makeAllBindings.
        d = g.app.config.modeCommandsDict

        # New in 4.4.1 b2: silently allow redefinitions of modes.
        d [modeName] = modeDict

    #@+node:ekr.20041120103012: *3* error (ParserBaseClass)
    def error (self,s):

        g.pr(s)

        # Does not work at present because we are using a null Gui.
        g.blue(s)
    #@+node:ekr.20041120094940: *3* kind handlers (ParserBaseClass)
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

        trace = False and not g.unitTesting
        aList = [] ; c = self.c ; tag = '@button'
        seen = []
        after = p.nodeAfterTree()
        while p and p != after:
            if p.v in seen:
                p.moveToNodeAfterTree()
            elif p.isAtIgnoreNode():
                seen.append(p.v)
                p.moveToNodeAfterTree()
            else:
                seen.append(p.v)
                if g.match_word(p.h,0,tag):
                    # We can not assume that p will be valid when it is used.
                    script = g.getScript(c,p,
                        useSelectedText=False,
                        forcePythonSentinels=True,
                        useSentinels=True)
                    aList.append((p.copy(),script),)
                p.moveToThreadNext()

        # This setting is handled differently from most other settings,
        # because the last setting must be retrieved before any commander exists.
        if aList:
            g.app.config.atCommonButtonsList.extend(aList)
                # Bug fix: 2011/11/24: Extend the list, don't replace it.
            g.app.config.buttonsFileName = c and c.shortFileName() or '<no settings file>'

        if trace: g.trace(len(aList),c.shortFileName())

        d,key = g.app.config.unitTestDict,'config.doButtons-file-names'
        aList = d.get(key,[])
        aList.append(c.shortFileName())
        d[key] = aList
    #@+node:ekr.20041120094940.2: *4* doColor
    def doColor (self,p,kind,name,val):

        # At present no checking is done.
        val = val.lstrip('"').rstrip('"')
        val = val.lstrip("'").rstrip("'")

        self.set(p,kind,name,val)
    #@+node:ekr.20080312071248.6: *4* doCommands
    def doCommands (self,p,kind,name,val):

        '''Handle an @commands tree.'''

        trace = False and not g.unitTesting
        aList = [] ; c = self.c ; tag = '@command'
        seen = []
        after = p.nodeAfterTree()
        while p and p != after:
            if p.v in seen:
                p.moveToNodeAfterTree()
            elif p.isAtIgnoreNode():
                seen.append(p.v)
                p.moveToNodeAfterTree()
            else:
                seen.append(p.v)
                if g.match_word(p.h,0,tag):
                    # We can not assume that p will be valid when it is used.
                    script = g.getScript(c,p,
                        useSelectedText=False,
                        forcePythonSentinels=True,
                        useSentinels=True)
                    aList.append((p.copy(),script),)
                p.moveToThreadNext()

        # This setting is handled differently from most other settings,
        # because the last setting must be retrieved before any commander exists.
        if aList:
            g.app.config.atCommonCommandsList.extend(aList)
                # Bug fix: 2011/11/24: Extend the list, don't replace it.
        if trace: g.trace(len(aList),c.shortFileName())

        d,key = g.app.config.unitTestDict,'config.doCommands-file-names'
        aList = d.get(key,[])
        aList.append(c.shortFileName())
        d[key] = aList
    #@+node:ekr.20071214140900: *4* doData
    def doData (self,p,kind,name,val):

        # New in Leo 4.11: do not strip lines.
        data = [z for z in g.splitLines(p.b) if not z.startswith('#')]
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

        # 2011/09/04: Remove comments, comment lines and blank lines.
        aList,lines = [],g.splitLines(s)
        for s in lines:
            i = s.find('#')
            if i > -1: s = s[:i]+'\n' # 2011/09/29: must add newline back in.
            if s.strip(): aList.append(s.lstrip())
        s = ''.join(aList)
        # g.trace('\n%s' % s)


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
                g.warning(s)
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

        lm = g.app.loadManager
        h = lm.computeMachineName()
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
    #@+node:tbrown.20080514112857.124: *4* doMenuat
    def doMenuat (self,p,kind,name,val):
        
        trace = False and not g.unitTesting

        if g.app.config.menusList:
            if trace: g.es_print("Patching menu tree: " + name)

            # get the patch fragment
            patch = []
            if p.hasChildren():
                # self.doMenus(p.copy().firstChild(),kind,name,val,storeIn=patch)
                self.doItems(p.copy(),patch)
                if trace: self.dumpMenuTree(patch)

            # setup        
            parts = name.split()
            if len(parts) != 3:
                parts.append('subtree')
            targetPath,mode,source = parts
            if not targetPath.startswith('/'):
                targetPath = '/'+targetPath
            ans = self.patchMenuTree(g.app.config.menusList, targetPath)
            if ans:
                if trace: g.es_print("Patching ("+mode+' '+source+") at "+targetPath)
                list_, idx = ans
                if mode not in ('copy', 'cut'):
                    if source != 'clipboard':
                        use = patch # [0][1]
                    else:
                        if isinstance(self.clipBoard, list):
                            use = self.clipBoard
                        else:
                            use = [self.clipBoard]
                    if trace: g.es_print(str(use))
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
                    if trace: g.es_print(str(self.clipBoard))
                else:  # append
                    list_.extend(use)
            else:
                g.es_print("ERROR: didn't find menu path " + targetPath)
        else:
            g.es_print("ERROR: @menuat found but no menu tree to patch")
    #@+node:tbrown.20080514180046.9: *5* getName (ParserBaseClass)
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

        if 1: # Prefer the legacy code now that the localFlag is set correctly.
            if self.localFlag:
                self.set(p,kind='menus',name='menus',val=aList)
            else:
                if False and not g.app.unitTesting and not g.app.silentMode:
                    s = 'using menus from: %s' % c.shortFileName()
                    g.blue(s)
                g.app.config.menusList = aList
                name = c.shortFileName() if c else '<no settings file>'
                g.app.config.menusFileName = name
        else:
            self.set(p,kind='menus',name='menus',val=aList)
            if not g.app.config.menusList:
                g.app.config.menusList = aList
                name = c.shortFileName() if c else '<no settings file>'
                g.app.config.menusFileName = name
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

        trace = False and not g.unitTesting
        c,k = self.c,self.c.k

        if g.new_modes:
            aList = []
            for line in g.splitLines(p.b):
                line = line.strip()
                if line and not g.match(line,0,'#'):
                    name2,si = self.parseShortcutLine('*mode-setting*',line)
                    aList.append((name2,si),)
            k.modeController.makeMode(name,aList)
        else:
            name1 = name

            # g.trace('%20s' % (name),c.fileName())
            modeName = self.computeModeName(name)

            d = g.TypedDictOfLists(
                name='modeDict for %s' % (modeName),
                keyType=type('commandName'),valType=g.ShortcutInfo)

            s = p.b
            lines = g.splitLines(s)
            for line in lines:
                line = line.strip()
                if line and not g.match(line,0,'#'):
                    name,si = self.parseShortcutLine('*mode-setting*',line)
                    assert g.isShortcutInfo(si),si
                    if not name:
                        # An entry command: put it in the special *entry-commands* key.
                        d.add('*entry-commands*',si)
                    elif si is not None:
                        # A regular shortcut.
                        si.pane = modeName
                        aList = d.get(name,[])
                        for z in aList:
                            assert g.isShortcutInfo(z),z
                        # Important: use previous bindings if possible.
                        key2,aList2 = c.config.getShortcut(name)
                        for z in aList2:
                            assert g.isShortcutInfo(z),z
                        aList3 = [z for z in aList2 if z.pane != modeName]
                        if aList3:
                            # g.trace('inheriting',[b.val for b in aList3])
                            aList.extend(aList3)
                        aList.append(si)
                        d.replace(name,aList)

                        if 0: #### Why would we want to do this????
                            #### Old code: we have to save/restore self.shortcutsDict.
                                #### self.set(p,"shortcut",name,aList)
                            # Set the entry directly.
                            d2 = self.shortcutsDict
                            gs = d2.get(key2)
                            if gs:
                                assert g.isGeneralSetting(gs)
                                path = gs.path
                                if c.os_path_finalize(c.mFileName) != c.os_path_finalize(path):
                                    g.es("over-riding setting:",name,"from",path)

                            # Important: we can't use c here: it may be destroyed!
                            d2 [key2] = g.GeneralSetting(
                                kind,path=c.mFileName,val=val,tag='setting')

                # Restore the global shortcutsDict.
                ##### self.shortcutsDict = old_d

                if trace: g.trace(d.dump())

                # Create the command, but not any bindings to it.
                self.createModeCommand(modeName,name1,d)
    #@+node:ekr.20070411101643.1: *4* doOpenWith (ParserBaseClass)
    def doOpenWith (self,p,kind,name,val):

        # g.trace(self.c.shortFileName(),'kind',kind,'name',name,'val',val)

        d = self.parseOpenWith(p)
        d['name']=name
        d['shortcut']=val
        # g.trace('command',d.get('command'))
        name = kind = 'openwithtable'
        self.openWithList.append(d)
        self.set(p,kind,name,self.openWithList)
    #@+node:ekr.20041120104215.2: *4* doPage
    def doPage(self,p,kind,name,val):

        pass # Ignore @page this while parsing settings.
    #@+node:bobjack.20080324141020.4: *4* doPopup & helper
    def doPopup (self,p,kind,name,val):

        """
        Handle @popup menu items in @settings trees.
        """

        popupName = name
        # popupType = val
        aList = []
        p = p.copy()
        self.doPopupItems(p,aList)
        if not hasattr(g.app.config, 'context_menus'):
            g.app.config.context_menus = {}
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
    def doShortcuts(self,p,kind,junk_name,junk_val,s=None):

        '''Handle an @shortcut or @shortcuts node.'''

        trace = False and not g.unitTesting
        c,d = self.c,self.shortcutsDict
        if s is None: s = p.b
        fn = d.name()
        for line in g.splitLines(s):
            line = line.strip()
            if line and not g.match(line,0,'#'):
                commandName,si = self.parseShortcutLine(fn,line)
                assert g.isShortcutInfo(si),si
                if si and si.stroke not in (None,'none','None'):
                    self.doOneShortcut(si,commandName,p)
        if trace: g.trace(
            len(list(self.shortcutsDict.keys())),c.shortFileName(),p.h)
    #@+node:ekr.20111020144401.9585: *5* doOneShortcut (ParserBaseClass)
    def doOneShortcut(self,si,commandName,p):

        '''Handle a regular shortcut.'''

        trace = False and not g.unitTesting

        d = self.shortcutsDict
        aList = d.get(commandName,[])
        aList.append(si)
        d [commandName] = aList

        if trace: g.trace(commandName,si)
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
    #@+node:ekr.20041124063257: *3* munge (ParserBaseClass)
    def munge(self,s):

        return g.app.config.canonicalizeSettingName(s)
    #@+node:ekr.20041119204700.2: *3* oops (ParserBaseClass)
    def oops (self):
        g.pr("ParserBaseClass oops:",
            g.callers(),
            "must be overridden in subclass")
    #@+node:ekr.20041213082558: *3* parsers (ParserBaseClass)
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

        d = {'command': None}
            # Old: command is a tuple.
            # New: d contains args, kind, etc tags.

        for line in g.splitLines(p.b):
            self.parseOpenWithLine(line,d)

        return d
    #@+node:ekr.20070411101643.4: *5* parseOpenWithLine
    def parseOpenWithLine (self,line,d):

        s = line.strip()
        if not s: return

        i = g.skip_ws(s,0)
        if g.match(s,i,'#'):
            return

        # try:
            # s = str(s)
        # except UnicodeError:
            # pass

        if 1: # new code
            j = g.skip_c_id(s,i)
            tag = s[i:j].strip()
            if not tag:
                g.es_print('@openwith lines must start with a tag: %s' % (s))
                return
            i = g.skip_ws(s,j)
            if not g.match(s,i,':'):
                g.es_print('colon must follow @openwith tag: %s' % (s))
                return
            i += 1
            val = s[i:].strip() or ''
                # An empty val is valid.
            if tag == 'arg':
                aList = d.get('args',[])
                aList.append(val)
                d['args'] = aList
            elif d.get(tag):
                g.es_print('ignoring duplicate definition of %s %s' % (tag,s))
            else:
                d[tag] = val
        else:
            d['command'] = s
    #@+node:ekr.20041120112043: *4* parseShortcutLine (ParserBaseClass)
    def parseShortcutLine (self,kind,s):

        '''Parse a shortcut line.  Valid forms:

        --> entry-command
        settingName = shortcut
        settingName ! paneName = shortcut
        command-name --> mode-name = binding
        command-name --> same = binding
        '''

        trace = False and not g.unitTesting and kind == '*mode-setting*'
        c,k = self.c,self.c.k
        assert c
        name = val = nextMode = None ; nextMode = 'none'
        i = g.skip_ws(s,0)

        if g.match(s,i,'-->'): # New in 4.4.1 b1: allow mode-entry commands.
            j = g.skip_ws(s,i+3)
            i = g.skip_id(s,j,'-')
            entryCommandName = s[j:i]
            if trace: g.trace('-->',entryCommandName)
            return None,g.ShortcutInfo('*entry-command*',commandName=entryCommandName)

        j = i
        i = g.skip_id(s,j,'-') # New in 4.4: allow Emacs-style shortcut names.
        name = s[j:i]
        if not name:
            if trace: g.trace('no name',repr(s))
            return None,None

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
        if val:
            i = val.find('#')
            if i > 0 and val[i-1] in (' ','\t'):
                val = val[:i].strip()
        stroke = k.strokeFromSetting(val)
        assert g.isStrokeOrNone(stroke),stroke
        si = g.ShortcutInfo(kind=kind,nextMode=nextMode,pane=pane,stroke=stroke)
        if trace: g.trace('%25s %s' % (name,si))
        return name,si
    #@+node:ekr.20060608222828: *4* parseAbbrevLine (ParserBaseClass)
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
    #@+node:ekr.20041120094940.9: *3* set (ParserBaseClass)
    def set (self,p,kind,name,val):

        """Init the setting for name to val."""

        trace = False and not g.unitTesting
        if trace: g.trace(kind,name,val)

        c = self.c

        # Note: when kind is 'shortcut', name is a command name.
        key = self.munge(name)

        # if kind and kind.startswith('setting'): g.trace("settingsParser %10s %15s %s" %(kind,val,name))
        d = self.settingsDict
        gs = d.get(key)
        if gs:
            assert isinstance(gs,g.GeneralSetting),gs
            path = gs.path
            if c.os_path_finalize(c.mFileName) != c.os_path_finalize(path):
                g.es("over-riding setting:",name,"from",path)

        # Important: we can't use c here: it may be destroyed!
        d [key] = g.GeneralSetting(kind,path=c.mFileName,val=val,tag='setting')
    #@+node:ekr.20041119204700.1: *3* traverse (ParserBaseClass)
    def traverse (self):

        trace = False and not g.unitTesting
        c,k = self.c,self.c.k

        self.settingsDict = g.TypedDict(
            name='settingsDict for %s' % (c.shortFileName()),
            keyType=type('settingName'),valType=g.GeneralSetting)

        self.shortcutsDict = g.TypedDictOfLists(
            name='shortcutsDict for %s' % (c.shortFileName()),
            keyType=type('s'), valType=g.ShortcutInfo)

        # This must be called after the outline has been inited.
        p = c.config.settingsRoot()
        if not p:
            # c.rootPosition() doesn't exist yet.
            # This is not an error.
            if trace:
                print('****************'
                    'ParserBaseClass.traverse: no settings tree for %s' % (
                        c.shortFileName()))
            return self.shortcutsDict,self.settingsDict

        after = p.nodeAfterTree()
        while p and p != after:
            result = self.visitNode(p)
            if result == "skip":
                # g.warning('skipping settings in',p.h)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        # Return the raw dict, unmerged.
        return self.shortcutsDict,self.settingsDict
    #@+node:ekr.20041120094940.10: *3* valueError
    def valueError (self,p,kind,name,val):

        """Give an error: val is not valid for kind."""

        self.error("%s is not a valid %s for %s" % (val,kind,name))
    #@+node:ekr.20041119204700.3: *3* visitNode (must be overwritten in subclasses)
    def visitNode (self,p):

        self.oops()
    #@-others
#@-<< class ParserBaseClass >>

#@+others
#@+node:ekr.20041119203941: ** class GlobalConfigManager
class GlobalConfigManager:
    """A class to manage configuration settings."""

    #@+<< GlobalConfigManager class data >>
    #@+node:ekr.20041122094813: *3* << GlobalConfigManager class data >>
    #@+others
    #@+node:ekr.20041117062717.1: *4* defaultsDict (GCM class data)
    #@+at This contains only the "interesting" defaults.
    # Ints and bools default to 0, floats to 0.0 and strings to "".
    #@@c

    defaultBodyFontSize = g.choose(sys.platform=="win32",9,12)
    defaultLogFontSize  = g.choose(sys.platform=="win32",8,12)
    defaultMenuFontSize = g.choose(sys.platform=="win32",9,12)
    defaultTreeFontSize = g.choose(sys.platform=="win32",9,12)

    defaultsDict = g.TypedDict(
        name='g.app.config.defaultsDict',
        keyType=type('key'),valType=g.GeneralSetting)

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
        ("initial_split_orientation","string","vertical"), # was initial_splitter_orientation.
        ("initial_vertical_ratio","ratio",0.5),
        ("initial_horizontal_ratio","ratio",0.3),
        ("initial_horizontal_secondary_ratio","ratio",0.5),
        ("initial_vertical_secondary_ratio","ratio",0.7),
        # ("outline_pane_scrolls_horizontally","bool",False),
        ("split_bar_color","color","LightSteelBlue2"),
        ("split_bar_relief","relief","groove"),
        ("split_bar_width","int",7),
    )
    #@+node:ekr.20041118062709: *4* define encodingIvarsDict (GCM class data)
    encodingIvarsDict = g.TypedDict(
        name='g.app.config.encodingIvarsDict',
        keyType=type('key'),valType=g.GeneralSetting)

    encodingIvarsData = (
        ("default_at_auto_file_encoding","string","utf-8"),
        ("default_derived_file_encoding","string","utf-8"),
        ("new_leo_file_encoding","string","UTF-8"),
            # Upper case for compatibility with previous versions.
        ("defaultEncoding","string",None),
            # Defaults to None so it doesn't override better defaults.
    )
    #@+node:ekr.20041117072055: *4* ivarsDict (GCM class data)
    # Each of these settings sets the corresponding ivar.
    # Also, the LocalConfigManager class inits the corresponding commander ivar.

    ivarsDict = g.TypedDict(
        name='g.app.config.ivarsDict',
        keyType=type('key'),valType=g.GeneralSetting)

    ivarsData = (
        ("at_root_bodies_start_in_doc_mode","bool",True),
            # For compatibility with previous versions.
        ("create_nonexistent_directories","bool",False),
        ("output_initial_comment","string",""),
            # "" for compatibility with previous versions.
        ("output_newline","string","nl"),
        ("page_width","int","132"),
        ("read_only","bool",True),
        ("redirect_execute_script_output_to_log_pane","bool",False),
        ("relative_path_base_directory","string","!"),
        ("remove_sentinels_extension","string",".txt"),
        ("save_clears_undo_buffer","bool",False),
        ("stylesheet","string",None),
        ("tab_width","int",-4),
        ("target_language","language","python"),
            # Bug fix: added: 6/20/2005.
        ("trailing_body_newlines","string","asis"),
        ("use_plugins","bool",True),
            # New in 4.3: use_plugins = True by default.
        # ("use_psyco","bool",False),
            # use_pysco can not be set by config code:
            # config processing happens too late.
        ("undo_granularity","string","word"),
            # "char","word","line","node"
        ("write_strips_blank_lines","bool",False),
    )
    #@-others
    #@-<< GlobalConfigManager class data >>

    #@+others
    #@+node:ekr.20041117083202: *3* gcm.Birth...
    #@+node:ekr.20041117062717.2: *4* gcm.ctor
    def __init__ (self):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('g.app.config.__init__')

        # Set later.  To keep pylint happy.
        if 0: # No longer needed, now that setIvarsFromSettings always sets gcm ivars.
            self.at_root_bodies_start_in_doc_mode = True
            self.default_derived_file_encoding = 'utf-8'
            self.output_newline = 'nl'
            self.redirect_execute_script_output_to_log_pane = True
            self.relative_path_base_directory = '!'

        self.use_plugins = False # Required to keep pylint happy.
        self.create_nonexistent_directories = False # Required to keep pylint happy.

        self.atCommonButtonsList = [] # List of info for common @buttons nodes.
        self.atCommonCommandsList = [] # List of info for common @commands nodes.
        self.atLocalButtonsList = [] # List of positions of @button nodes.
        self.atLocalCommandsList = [] # List of positions of @command nodes.

        self.buttonsFileName = ''
        self.configsExist = False # True when we successfully open a setting file.
        self.unitTestDict = {} # For unit testing: *not* the same as g.app.unitTestDict.
        self.defaultFont = None # Set in gui.getDefaultConfigFont.
        self.defaultFontFamily = None # Set in gui.getDefaultConfigFont.
        self.enabledPluginsFileName = None
        self.enabledPluginsString = '' 
        self.inited = False
        self.menusList = []
        self.menusFileName = ''
        if g.new_modes:
            pass # Use k.ModeController instead.
        else:
            self.modeCommandsDict = g.TypedDict(
                name = 'modeCommandsDict',
                keyType = type('commandName'),valType = g.TypedDictOfLists)

        # Inited later...
        self.panes = None
        self.sc = None
        self.tree = None

        self.initDicts()
        self.initIvarsFromSettings()
        self.initRecentFiles()
    #@+node:ekr.20041227063801.2: *4* gcm.initDicts
    def initDicts (self):

        # Only the settings parser needs to search all dicts.
        self.dictList = [self.defaultsDict]

        for key,kind,val in self.defaultsData:
            self.defaultsDict[self.munge(key)] = g.GeneralSetting(
                kind,setting=key,val=val,tag='defaults')

        for key,kind,val in self.ivarsData:
            self.ivarsDict[self.munge(key)] = g.GeneralSetting(
                kind,ivar=key,val=val,tag='ivars')

        for key,kind,val in self.encodingIvarsData:
            self.encodingIvarsDict[self.munge(key)] = g.GeneralSetting(
                kind,encoding=val,ivar=key,tag='encoding')
    #@+node:ekr.20041117065611.2: *4* gcm.initIvarsFromSettings & helpers
    def initIvarsFromSettings (self):

        for ivar in sorted(list(self.encodingIvarsDict.keys())):
            self.initEncoding(ivar)

        for ivar in sorted(list(self.ivarsDict.keys())):
            self.initIvar(ivar)
    #@+node:ekr.20041117065611.1: *5* initEncoding
    def initEncoding (self,key):

        '''Init g.app.config encoding ivars during initialization.'''

        # Important: The key is munged.
        gs = self.encodingIvarsDict.get(key)

        setattr(self,gs.ivar,gs.encoding)

        # g.trace(gs.ivar,gs.encoding)

        if gs.encoding and not g.isValidEncoding(gs.encoding):
            g.es("g.app.config: bad encoding:","%s: %s" % (gs.ivar,gs.encoding))
    #@+node:ekr.20041117065611: *5* initIvar
    def initIvar(self,key):

        '''Init g.app.config ivars during initialization.

        This does NOT init the corresponding commander ivars.

        Such initing must be done in setIvarsFromSettings.'''

        trace = False and not g.unitTesting # and key == 'outputnewline'

        # Important: the key is munged.
        d = self.ivarsDict
        gs = d.get(key)
        if trace:
            g.trace('g.app.config',gs.ivar,gs.val)
            # print('initIvar',self,gs.ivar,gs.val)

        setattr(self,gs.ivar,gs.val)
    #@+node:ekr.20041117083202.2: *4* gcm.initRecentFiles
    def initRecentFiles (self):

        self.recentFiles = []
    #@+node:ekr.20041228042224: *4* gcm.setIvarsFromSettings
    def setIvarsFromSettings (self,c):

        '''Init g.app.config ivars or c's ivars from settings.

        - Called from readSettingsFiles with c = None to init g.app.config ivars.
        - Called from c.__init__ to init corresponding commmander ivars.'''

        trace = False and not g.unitTesting
        verbose = True

        if not self.inited: return

        # Ignore temporary commanders created by readSettingsFiles.
        if trace and verbose: g.trace('*' * 10)
        if trace: g.trace(
            'inited',self.inited,c and c.shortFileName() or '<no c>')

        d = self.ivarsDict
        keys = list(d.keys())
        keys.sort()
        for key in keys:
            gs = d.get(key)
            if gs:
                assert isinstance(gs,g.GeneralSetting)
                ivar = gs.ivar # The actual name of the ivar.
                kind = gs.kind
                if c:
                    val = c.config.get(key,kind)
                else:
                    val = self.get(key,kind) # Don't use bunch.val!
                if c:
                    if trace and verbose: g.trace("%20s %s = %s" % (
                        g.shortFileName(c.mFileName),ivar,val))
                    setattr(c,ivar,val)
                if True: # Always set the global ivars.
                    if trace and verbose: g.trace("%20s %s = %s" % (
                        'g.app.config',ivar,val))
                    setattr(self,ivar,val)
    #@+node:ekr.20041117081009: *3* gcm.Getters...
    #@+node:ekr.20041123070429: *4* gcm.canonicalizeSettingName (munge)
    def canonicalizeSettingName (self,name):

        if name is None:
            return None

        name = name.lower()
        for ch in ('-','_',' ','\n'):
            name = name.replace(ch,'')

        return g.choose(name,name,None)

    munge = canonicalizeSettingName
    #@+node:ekr.20051011105014: *4* gcm.exists
    def exists (self,setting,kind):

        '''Return true if a setting of the given kind exists, even if it is None.'''

        lm = g.app.loadManager
        d = lm.globalSettingsDict
        if d:
            junk,found = self.getValFromDict(d,setting,kind)
            return found
        else:
            return False
    #@+node:ekr.20041117083141: *4* gcm.get & allies
    def get (self,setting,kind):

        """Get the setting and make sure its type matches the expected type."""

        trace = False and not g.unitTesting
        lm = g.app.loadManager

        # It *is* valid to call this method: it returns the global settings.
        # if c:
            # print('g.app.config.get ***** call c.config.getX when c is available')
            # print('g.app.config.get',setting,kind,g.callers())

        d = lm.globalSettingsDict
        if d:
            assert g.isTypedDict(d),d
            val,junk = self.getValFromDict(d,setting,kind)
            if trace:
                print('g.app.config.get %30s %s' % (setting,val))
            return val
        else:
            if trace:
                print('g.app.config.get %30s **no d, returning None' % (setting))
            return None
    #@+node:ekr.20041121143823: *5* gcm.getValFromDict
    def getValFromDict (self,d,setting,requestedType,warn=True):

        '''Look up the setting in d. If warn is True, warn if the requested type
        does not (loosely) match the actual type.
        returns (val,exists)'''

        gs = d.get(self.munge(setting))
        if not gs: return None,False
        assert isinstance(gs,g.GeneralSetting)

        # g.trace(setting,requestedType,gs.toString())
        val = gs.val

        # 2011/10/24: test for an explicit None.
        if g.isPython3:
            isNone = val in ('None','none','') # ,None)
        else:
            isNone = val in (
                unicode('None'),unicode('none'),unicode(''),
                'None','none','') #,None)

        if not self.typesMatch(gs.kind,requestedType):
            # New in 4.4: make sure the types match.
            # A serious warning: one setting may have destroyed another!
            # Important: this is not a complete test of conflicting settings:
            # The warning is given only if the code tries to access the setting.
            if warn:
                g.error('warning: ignoring',gs.kind,'',setting,'is not',requestedType)
                g.error('there may be conflicting settings!')
            return None, False
        # elif val in (u'None',u'none','None','none','',None):
        elif isNone:
            return '', True
                # 2011/10/24: Exists, a *user-defined* empty value.
        else:
            # g.trace(setting,val)
            return val, True
    #@+node:ekr.20051015093141: *5* gcm.typesMatch
    def typesMatch (self,type1,type2):

        '''
        Return True if type1, the actual type, matches type2, the requeseted type.

        The following equivalences are allowed:

        - None matches anything.
        - An actual type of string or strings matches anything *except* shortcuts.
        - Shortcut matches shortcuts.
        '''

        # The shortcuts logic no longer uses the get/set code.
        shortcuts = ('shortcut','shortcuts',)
        if type1 in shortcuts or type2 in shortcuts:
            g.trace('oops: type in shortcuts')

        return (
            type1 == None or type2 == None or
            type1.startswith('string') and type2 not in shortcuts or
            type1 == 'int' and type2 == 'size' or
            (type1 in shortcuts and type2 in shortcuts) or
            type1 == type2
        )
    #@+node:ekr.20060608224112: *4* gcm.getAbbrevDict
    def getAbbrevDict (self):

        """Search all dictionaries for the setting & check it's type"""

        d = self.get('abbrev','abbrev')
        return d or {}
    #@+node:ekr.20041117081009.3: *4* gcm.getBool
    def getBool (self,setting,default=None):

        '''Return the value of @bool setting, or the default if the setting is not found.'''

        val = self.get(setting,"bool")

        if val in (True,False):
            return val
        else:
            return default
    #@+node:ekr.20070926082018: *4* gcm.getButtons
    def getButtons (self):

        '''Return a list of tuples (x,y) for common @button nodes.'''

        return g.app.config.atCommonButtonsList
    #@+node:ekr.20041122070339: *4* gcm.getColor
    def getColor (self,setting):

        '''Return the value of @color setting.'''

        return self.get(setting,"color")
    #@+node:ekr.20080312071248.7: *4* gcm.getCommonCommands
    def getCommonAtCommands (self):

        '''Return the list of tuples (headline,script) for common @command nodes.'''

        return g.app.config.atCommonCommandsList
    #@+node:ekr.20071214140900.1: *4* gcm.getData
    def getData (self,setting):

        '''Return a list of non-comment strings in the body text of @data setting.'''

        return self.get(setting,"data")
    #@+node:ekr.20041117093009.1: *4* gcm.getDirectory
    def getDirectory (self,setting):

        '''Return the value of @directory setting, or None if the directory does not exist.'''

        # Fix https://bugs.launchpad.net/leo-editor/+bug/1173763
        theDir = self.get(setting,'directory')

        if g.os_path_exists(theDir) and g.os_path_isdir(theDir):
            return theDir
        else:
            return None
    #@+node:ekr.20070224075914.1: *4* gcm.getEnabledPlugins
    def getEnabledPlugins (self):

        '''Return the body text of the @enabled-plugins node.'''

        return g.app.config.enabledPluginsString
    #@+node:ekr.20041117082135: *4* gcm.getFloat
    def getFloat (self,setting):

        '''Return the value of @float setting.'''

        val = self.get(setting,"float")
        try:
            val = float(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20041117062717.13: *4* gcm.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        """Compute a font from font parameters.

        Arguments are the names of settings to be use.
        Default to size=12, slant="roman", weight="normal".

        Return None if there is no family setting so we can use system default fonts."""

        family = self.get(family,"family")
        if family in (None,""):
            family = self.defaultFontFamily

        size = self.get(size,"size")
        if size in (None,0): size = defaultSize

        slant = self.get(slant,"slant")
        if slant in (None,""): slant = "roman"

        weight = self.get(weight,"weight")
        if weight in (None,""): weight = "normal"

        # g.trace(g.callers(3),family,size,slant,weight)

        return g.app.gui.getFontFromParams(family,size,slant,weight)
    #@+node:ekr.20041117081513: *4* gcm.getInt
    def getInt (self,setting):

        '''Return the value of @int setting.'''

        val = self.get(setting,"int")
        try:
            val = int(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20041117093009.2: *4* gcm.getLanguage
    def getLanguage (self,setting):

        '''Return the setting whose value should be a language known to Leo.'''

        language = self.getString(setting)
        return language
    #@+node:ekr.20070926070412: *4* gcm.getMenusList
    def getMenusList (self):

        '''Return the list of entries for the @menus tree.'''

        aList = self.get('menus','menus')
        # g.trace(aList and len(aList) or 0)

        return aList or g.app.config.menusList
    #@+node:ekr.20070411101643: *4* gcm.getOpenWith
    def getOpenWith (self):

        '''Return a list of dictionaries corresponding to @openwith nodes.'''

        val = self.get('openwithtable','openwithtable')

        return val
    #@+node:ekr.20041122070752: *4* gcm.getRatio
    def getRatio (self,setting):

        '''Return the value of @float setting.

        Warn if the value is less than 0.0 or greater than 1.0.'''

        val = self.get(setting,"ratio")
        try:
            val = float(val)
            if 0.0 <= val <= 1.0:
                return val
            else:
                return None
        except TypeError:
            return None
    #@+node:ekr.20041117062717.11: *4* gcm.getRecentFiles
    def getRecentFiles (self):

        '''Return the list of recently opened files.'''

        return self.recentFiles
    #@+node:ekr.20041117081009.4: *4* gcm.getString
    def getString (self,setting):

        '''Return the value of @string setting.'''

        return self.get(setting,"string")
    #@+node:ekr.20120222103014.10314: *3* gcm.config_iter
    def config_iter(self,c):

        '''Letters:
          leoSettings.leo
        D default settings
        F loaded .leo File
        M myLeoSettings.leo
        '''

        lm = g.app.loadManager
        suppressKind = ('shortcut','shortcuts','openwithtable')
        suppressKeys = (None,'shortcut')

        d = c.config.settingsDict if c else lm.globalSettingsDict
        for key in sorted(list(d.keys())):
            if key not in suppressKeys:
                gs = d.get(key)
                assert g.isGeneralSetting(gs),gs
                if gs and gs.kind not in suppressKind:
                    letter = lm.computeBindingLetter(gs.path)
                    # g.trace('%3s %40s %s' % (letter,key,gs.val))
                    yield key,gs.val,c,letter
        # raise stopIteration
    #@-others
#@+node:ekr.20041118104831.1: ** class LocalConfigManager
class LocalConfigManager:

    """A class to hold config settings for commanders."""

    #@+others
    #@+node:ekr.20120215072959.12472: *3* c.config.Birth
    #@+node:ekr.20041118104831.2: *4* c.config.ctor
    def __init__ (self,c,previousSettings=None):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('c.config.__init__ %s' % (c and c.shortFileName()))
        self.c = c

        # The shortcuts and settings dicts, set in c.__init__
        # for local files.
        if previousSettings:
            # g.trace('(c.config.ctor)',previousSettings)
            self.settingsDict = previousSettings.settingsDict
            self.shortcutsDict = previousSettings.shortcutsDict
            assert g.isTypedDict(self.settingsDict)
            assert g.isTypedDictOfLists(self.shortcutsDict)
        else:
            lm = g.app.loadManager
            self.settingsDict  = d1 = lm.globalSettingsDict
            self.shortcutsDict = d2 = lm.globalShortcutsDict
            assert d1 is None or g.isTypedDict(d1),d1
            assert d2 is None or g.isTypedDictOfLists(d2),d2

        # Define these explicitly to eliminate a pylint warning.
        if 0:
            # No longer needed now that c.config.initIvar always sets
            # both c and c.config ivars.
            self.default_derived_file_encoding =\
                g.app.config.default_derived_file_encoding
            self.redirect_execute_script_output_to_log_pane =\
                g.app.config.redirect_execute_script_output_to_log_pane

        self.defaultBodyFontSize = g.app.config.defaultBodyFontSize
        self.defaultLogFontSize  = g.app.config.defaultLogFontSize
        self.defaultMenuFontSize = g.app.config.defaultMenuFontSize
        self.defaultTreeFontSize = g.app.config.defaultTreeFontSize

        for key in sorted(list(g.app.config.encodingIvarsDict.keys())):
            self.initEncoding(key)

        for key in sorted(list(g.app.config.ivarsDict.keys())):
            self.initIvar(key)
    #@+node:ekr.20041118104414: *4* c.config.initEncoding
    def initEncoding (self,key):

        # Important: the key is munged.
        gs = g.app.config.encodingIvarsDict.get(key)
        encodingName = gs.ivar
        encoding = self.get(encodingName,kind='string')

        # Use the global setting as a last resort.
        if encoding:
            # g.trace('c.config',c.shortFileName(),encodingName,encoding)
            setattr(self,encodingName,encoding)
        else:
            encoding = getattr(g.app.config,encodingName)
            # g.trace('g.app.config',c.shortFileName(),encodingName,encoding)
            setattr(self,encodingName,encoding)
        if encoding and not g.isValidEncoding(encoding):
            g.es("bad", "%s: %s" % (encodingName,encoding))
    #@+node:ekr.20041118104240: *4* c.config.initIvar
    def initIvar(self,key):

        trace = False and not g.unitTesting
        c = self.c

        # Important: the key is munged.
        gs = g.app.config.ivarsDict.get(key)
        ivarName = gs.ivar
        val = self.get(ivarName,kind=None)

        if val or not hasattr(self,ivarName):
            if trace: g.trace('c.config',c.shortFileName(),ivarName,val)
            # Set *both* the commander ivar and the c.config ivar.
            setattr(self,ivarName,val)
            setattr(c,ivarName,val)
    #@+node:ekr.20120215072959.12471: *3* c.config.Getters
    #@+node:ekr.20120215072959.12543: *4* c.config.Getters: redirect to g.app.config
    def getButtons (self):
        '''Return a list of tuples (x,y) for common @button nodes.'''
        return g.app.config.atCommonButtonsList # unusual.

    def getCommands (self):
        '''Return the list of tuples (headline,script) for common @command nodes.'''
        return g.app.config.atCommonCommandsList # unusual.

    def getEnabledPlugins (self):
        '''Return the body text of the @enabled-plugins node.'''
        return g.app.config.enabledPluginsString # unusual.

    def getRecentFiles (self):
        '''Return the list of recently opened files.'''
        return g.app.config.getRecentFiles() # unusual
    #@+node:ekr.20120215072959.12515: *4* c.config.Getters
    #@@nocolor-node

    #@+at Only the following need to be defined.
    # 
    #     get (self,setting,theType)
    #     getAbbrevDict (self)
    #     getBool (self,setting,default=None)
    #     getButtons (self)
    #     getColor (self,setting)
    #     getData (self,setting)
    #     getDirectory (self,setting)
    #     getFloat (self,setting)
    #     getFontFromParams (self,family,size,slant,weight,defaultSize=12)
    #     getInt (self,setting)
    #     getLanguage (self,setting)
    #     getMenusList (self)
    #     getOpenWith (self):
    #     getRatio (self,setting)
    #     getShortcut (self,commandName)
    #     getString (self,setting)
    #@+node:ekr.20120215072959.12519: *5* c.config.get & allies
    def get (self,setting,kind):

        """Get the setting and make sure its type matches the expected type."""

        trace = False and not g.unitTesting
        verbose = True
        d = self.settingsDict
        lm = g.app.loadManager
        if d:
            assert g.isTypedDict(d),d
            val,junk = self.getValFromDict(d,setting,kind)
            if trace and verbose and val is not None:
                # g.trace('%35s %20s %s' % (setting,val,g.callers(3)))
                g.trace('%40s %s' % (setting,val))
            return val
        else:
            if trace and lm.globalSettingsDict:
                g.trace('ignore: %40s %s' % (
                    setting,g.callers(2)))
            return None
    #@+node:ekr.20120215072959.12520: *6* getValFromDict
    def getValFromDict (self,d,setting,requestedType,warn=True):

        '''Look up the setting in d. If warn is True, warn if the requested type
        does not (loosely) match the actual type.
        returns (val,exists)'''

        gs = d.get(g.app.config.munge(setting))
        if not gs: return None,False
        assert g.isGeneralSetting(gs),gs
        val = gs.val

        # 2011/10/24: test for an explicit None.
        if g.isPython3:
            isNone = val in ('None','none','') # ,None)
        else:
            isNone = val in (
                unicode('None'),unicode('none'),unicode(''),
                'None','none','') #,None)

        if not self.typesMatch(gs.kind,requestedType):
            # New in 4.4: make sure the types match.
            # A serious warning: one setting may have destroyed another!
            # Important: this is not a complete test of conflicting settings:
            # The warning is given only if the code tries to access the setting.
            if warn:
                g.error('warning: ignoring',gs.kind,'',setting,'is not',requestedType)
                g.error('there may be conflicting settings!')
            return None, False
        elif isNone:
            return '', True
                # 2011/10/24: Exists, a *user-defined* empty value.
        else:
            return val, True
    #@+node:ekr.20120215072959.12521: *6* typesMatch
    def typesMatch (self,type1,type2):

        '''
        Return True if type1, the actual type, matches type2, the requeseted type.

        The following equivalences are allowed:

        - None matches anything.
        - An actual type of string or strings matches anything *except* shortcuts.
        - Shortcut matches shortcuts.
        '''

        # The shortcuts logic no longer uses the get/set code.
        shortcuts = ('shortcut','shortcuts',)
        if type1 in shortcuts or type2 in shortcuts:
            g.trace('oops: type in shortcuts')

        return (
            type1 == None or type2 == None or
            type1.startswith('string') and type2 not in shortcuts or
            type1 == 'int' and type2 == 'size' or
            (type1 in shortcuts and type2 in shortcuts) or
            type1 == type2
        )
    #@+node:ekr.20120215072959.12522: *5* c.config.getAbbrevDict
    def getAbbrevDict (self):

        """Search all dictionaries for the setting & check it's type"""

        d = self.get('abbrev','abbrev')
        return d or {}
    #@+node:ekr.20120215072959.12523: *5* c.config.getBool
    def getBool (self,setting,default=None):

        '''Return the value of @bool setting, or the default if the setting is not found.'''

        val = self.get(setting,"bool")

        if val in (True,False):
            return val
        else:
            return default
    #@+node:ekr.20120215072959.12525: *5* c.config.getColor
    def getColor (self,setting):

        '''Return the value of @color setting.'''

        return self.get(setting,"color")
    #@+node:ekr.20120215072959.12527: *5* c.config.getData
    def getData (self,setting,strip_data=True):

        '''Return a list of non-comment strings in the body text of @data setting.'''

        data =  self.get(setting,"data")
        # New in Leo 4.11: parser.doData strips only comments now.
        if data and strip_data:
            data = [z.strip() for z in data if z.strip()]
        return data
    #@+node:ekr.20120215072959.12528: *5* c.config.getDirectory
    def getDirectory (self,setting):

        '''Return the value of @directory setting, or None if the directory does not exist.'''

        # Fix https://bugs.launchpad.net/leo-editor/+bug/1173763
        theDir = self.get(setting,'directory')

        if g.os_path_exists(theDir) and g.os_path_isdir(theDir):
            return theDir
        else:
            return None
    #@+node:ekr.20120215072959.12530: *5* c.config.getFloat
    def getFloat (self,setting):

        '''Return the value of @float setting.'''

        val = self.get(setting,"float")
        try:
            val = float(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20120215072959.12531: *5* c.config.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        """Compute a font from font parameters.

        Arguments are the names of settings to be use.
        Default to size=12, slant="roman", weight="normal".

        Return None if there is no family setting so we can use system default fonts."""

        family = self.get(family,"family")
        if family in (None,""): family = g.app.config.defaultFontFamily

        size = self.get(size,"size")
        if size in (None,0): size = defaultSize

        slant = self.get(slant,"slant")
        if slant in (None,""): slant = "roman"

        weight = self.get(weight,"weight")
        if weight in (None,""): weight = "normal"

        # g.trace(family,size,slant,weight,g.shortFileName(self.c.mFileName))
        return g.app.gui.getFontFromParams(family,size,slant,weight)
    #@+node:ekr.20120215072959.12532: *5* c.config.getInt
    def getInt (self,setting):

        '''Return the value of @int setting.'''

        val = self.get(setting,"int")
        try:
            val = int(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20120215072959.12533: *5* c.config.getLanguage
    def getLanguage (self,setting):

        '''Return the setting whose value should be a language known to Leo.'''

        language = self.getString(setting)
        # g.trace(setting,language)

        return language
    #@+node:ekr.20120215072959.12534: *5* c.config.getMenusList
    def getMenusList (self):

        '''Return the list of entries for the @menus tree.'''

        aList = self.get('menus','menus')
        # g.trace(aList and len(aList) or 0)

        return aList or g.app.config.menusList
    #@+node:ekr.20120215072959.12535: *5* c.config.getOpenWith
    def getOpenWith (self):

        '''Return a list of dictionaries corresponding to @openwith nodes.'''

        val = self.get('openwithtable','openwithtable')

        return val
    #@+node:ekr.20120215072959.12536: *5* c.config.getRatio
    def getRatio (self,setting):

        '''Return the value of @float setting.

        Warn if the value is less than 0.0 or greater than 1.0.'''

        val = self.get(setting,"ratio")
        try:
            val = float(val)
            if 0.0 <= val <= 1.0:
                return val
            else:
                return None
        except TypeError:
            return None
    #@+node:ekr.20120215072959.12538: *5* c.config.getSettingSource
    def getSettingSource (self,setting):

        '''return the name of the file responsible for setting.'''

        c,d = self.c,self.settingsDict
        if d:
            assert g.isTypedDict(d),d
            si = d.get(setting)
            if si is None:
                return 'unknown setting',None
            else:
                assert g.isShortcutInfo(si)
                return si.path,si.val
        else:
            # lm.readGlobalSettingsFiles is opening a settings file.
            # lm.readGlobalSettingsFiles has not yet set lm.globalSettingsDict.
            assert d is None
            return None
    #@+node:ekr.20120215072959.12539: *5* c.config.getShortcut
    def getShortcut (self,commandName):

        '''Return rawKey,accel for shortcutName'''

        trace = False and not g.unitTesting
        c = self.c
        d = self.shortcutsDict

        if not c.frame.menu:
            g.trace('no menu: %s' % (commandName))
            return None,[]

        if d:
            assert g.isTypedDictOfLists(d),d
            key = c.frame.menu.canonicalizeMenuName(commandName)
            key = key.replace('&','') # Allow '&' in names.
            aList = d.get(commandName,[])
            if aList:
                for si in aList: assert g.isShortcutInfo(si),si 
                # It's very important to filter empty strokes here.
                aList = [si for si in aList
                    if si.stroke and si.stroke.lower() != 'none']
            if trace: g.trace(d,'\n',aList)
            return key,aList
        else:
            # lm.readGlobalSettingsFiles is opening a settings file.
            # lm.readGlobalSettingsFiles has not yet set lm.globalSettingsDict.
            return None,[]
    #@+node:ekr.20120215072959.12540: *5* c.config.getString
    def getString (self,setting):

        '''Return the value of @string setting.'''

        return self.get(setting,"string")
    #@+node:ekr.20120224140548.10528: *4* c.exists (new)
    def exists (self,c,setting,kind):

        '''Return true if a setting of the given kind exists, even if it is None.'''

        d = self.settingsDict
        if d:
            junk,found = self.getValFromDict(d,setting,kind)
            if found: return True
        return False
    #@+node:ekr.20041123092357: *4* c.config.findSettingsPosition & helper
    # This was not used prior to Leo 4.5.

    def findSettingsPosition (self,setting):

        """Return the position for the setting in the @settings tree for c."""

        munge = g.app.config.munge
        c = self.c

        root = self.settingsRoot()
        if not root:
            return c.nullPosition()

        setting = munge(setting)

        for p in root.subtree():
            #BJ munge will return None if a headstring is empty
            h = munge(p.h) or ''
            if h.startswith(setting):
                return p.copy()

        return c.nullPosition()
    #@+node:ekr.20041120074536: *5* c.config.settingsRoot
    def settingsRoot (self):

        '''Return the position of the @settings tree.'''

        # g.trace(c,c.rootPosition())

        c = self.c

        for p in c.all_unique_positions():
            if p.h.rstrip() == "@settings":
                return p.copy()
        else:
            return c.nullPosition()
    #@+node:ekr.20070418073400: *3* c.config.printSettings
    def printSettings (self):

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
        c = self.c
        legend = g.adjustTripleString(legend,c.tab_width)
        result = []
        for name,val,c,letter in g.app.config.config_iter(c):
            kind = g.choose(letter==' ','   ','[%s]' % (letter))
            result.append('%s %s = %s\n' % (kind,name,val))

        # Use a single g.es statement.
        result.append('\n'+legend)
        if g.unitTesting:
            pass # print(''.join(result))
        else:
            g.es('',''.join(result),tabName='Settings')
    #@+node:ekr.20120215072959.12475: *3* c.config.set
    def set (self,p,kind,name,val):

        """Init the setting for name to val."""

        trace = False and not g.unitTesting
        if trace: g.trace(kind,name,val)

        c = self.c

        # Note: when kind is 'shortcut', name is a command name.
        key = g.app.config.munge(name)

        # if kind and kind.startswith('setting'): g.trace("c.config %10s %15s %s" %(kind,val,name))
        d = self.settingsDict
        assert g.isTypedDict(d),d

        gs = d.get(key)
        if gs:
            assert g.isGeneralSetting(gs),gs
            path = gs.path
            if c.os_path_finalize(c.mFileName) != c.os_path_finalize(path):
                g.es("over-riding setting:",name,"from",path)

        gs = g.GeneralSetting(kind,path=c.mFileName,val=val,tag='setting')
        d.replace(key,gs)
    #@-others
#@+node:ekr.20041119203941.3: ** class SettingsTreeParser (ParserBaseClass)
class SettingsTreeParser (ParserBaseClass):

    '''A class that inits settings found in an @settings tree.

    Used by read settings logic.'''

    #@+others
    #@+node:ekr.20041119204103: *3* ctor (SettingsTreeParser)
    def __init__ (self,c,localFlag=True):

        # Init the base class.
        ParserBaseClass.__init__(self,c,localFlag)
    #@+node:ekr.20041119204714: *3* visitNode (SettingsTreeParser)
    def visitNode (self,p):

        """Init any settings found in node p."""

        # g.trace(p.h)

        p = p.copy()
            # Bug fix 2011/11/24
            # Ensure inner traversals don't change callers's p.

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

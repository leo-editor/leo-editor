#@+leo-ver=5-thin
#@+node:ekr.20130925160837.11429: * @file leoConfig.py
"""Configuration classes for Leo."""
#@+<< leoConfig imports & annotations >>
#@+node:ekr.20041227063801: ** << leoConfig imports & annotations >>
from __future__ import annotations
import os
import sys
import re
import textwrap
from typing import Any, Generator, Optional, TYPE_CHECKING
from leo.plugins.mod_scripting import build_rclick_tree
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    from leo.core.leoApp import PreviousSettings
    Setting = Any
    Widget = Any
#@-<< leoConfig imports & annotations >>
#@+<< class ParserBaseClass >>
#@+node:ekr.20041119203941.2: ** << class ParserBaseClass >>
class ParserBaseClass:
    """The base class for settings parsers."""
    #@+<< ParserBaseClass data >>
    #@+node:ekr.20041121130043: *3* << ParserBaseClass data >>
    # These are the canonicalized names.
    # Case is ignored, as are '_' and '-' characters.
    basic_types = [
        # Headlines have the form @kind name = var
        'bool',
        'color',
        'directory',
        'int',
        'ints',
        'float',
        'path',
        'ratio',
        'string',
        'strings',
    ]
    control_types = [
        'buttons',
        'commands',
        'data',
        'enabledplugins',
        'font',
        'ifenv',
        'ifhostname',
        'ifplatform',
        'ignore',
        'menus',
        'mode',
        'menuat',
        'openwith',
        'outlinedata',
        'popup',
        'settings',
        'shortcuts',
    ]
    # Keys are settings names, values are (type,value) tuples.
    settingsDict: dict[str, Any] = {}
    #@-<< ParserBaseClass data >>
    #@+others
    #@+node:ekr.20041119204700: *3*  pbc.ctor
    #@@nobeautify

    def __init__(self, c: Cmdr, localFlag: bool) -> None:
        """Ctor for the ParserBaseClass class."""
        self.c = c
        self.clipBoard: list[str] = []
        # True if this is the .leo file being opened,
        # as opposed to myLeoSettings.leo or leoSettings.leo.
        self.localFlag = localFlag
        self.shortcutsDict: dict[str, list[g.BindingInfo]] = g.SettingsDict('parser.shortcutsDict')
        # A list of dicts containing 'name','shortcut','command' keys.
        self.openWithList: list[dict[str, Any]] = []
        # Keys are canonicalized names.
        self.dispatchDict = {
            'bool':         self.doBool,
            'buttons':      self.doButtons, # New in 4.4.4
            'color':        self.doColor,
            'commands':     self.doCommands, # New in 4.4.8.
            'data':         self.doData, # New in 4.4.6
            'directory':    self.doDirectory,
            'enabledplugins': self.doEnabledPlugins,
            'font':         self.doFont,
            'ifenv':        self.doIfEnv, # New in 5.2 b1.
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
            'outlinedata':  self.doOutlineData, # New in 4.11.1.
            'path':         self.doPath,
            'ratio':        self.doRatio,
            'shortcuts':    self.doShortcuts,
            'string':       self.doString,
            'strings':      self.doStrings,
        }
        self.debug_count = 0
    #@+node:ekr.20080514084054.4: *3* pbc.computeModeName
    def computeModeName(self, name: str) -> str:
        s = name.strip().lower()
        j = s.find(' ')
        if j > -1:
            s = s[:j]
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
    #@+node:ekr.20060102103625: *3* pbc.createModeCommand
    def createModeCommand(self, modeName: str, name: str, modeDict: Any) -> None:
        modeName = 'enter-' + modeName.replace(' ', '-')
        i = name.find('::')
        if i > -1:
            # The prompt is everything after the '::'
            prompt = name[i + 2 :].strip()
            modeDict['*command-prompt*'] = g.BindingInfo(kind=prompt)
        # Save the info for k.finishCreate and k.makeAllBindings.
        d = g.app.config.modeCommandsDict
        # New in 4.4.1 b2: silently allow redefinitions of modes.
        d[modeName] = modeDict
    #@+node:ekr.20041120103012: *3* pbc.error
    def error(self, s: str) -> None:
        g.pr(s)
        # Does not work at present because we are using a null Gui.
        g.blue(s)
    #@+node:ekr.20041120094940: *3* pbc.kind handlers
    #@+node:ekr.20041120094940.1: *4* pbc.doBool
    def doBool(self, p: Position, kind: str, name: str, val: Any) -> None:
        if val in ('True', 'true', '1'):
            self.set(p, kind, name, True)
        elif val in ('False', 'false', '0'):
            self.set(p, kind, name, False)
        else:
            self.valueError(p, kind, name, val)
    #@+node:ekr.20070925144337: *4* pbc.doButtons
    def doButtons(self, p: Position, kind: str, name: str, val: Any) -> None:
        """Create buttons for each @button node in an @buttons tree."""
        c, tag = self.c, '@button'
        aList, seen = [], []
        after = p.nodeAfterTree()
        while p and p != after:
            if p.v in seen:
                p.moveToNodeAfterTree()
            elif p.isAtIgnoreNode():
                seen.append(p.v)
                p.moveToNodeAfterTree()
            else:
                seen.append(p.v)
                if g.match_word(p.h, 0, tag):
                    # We can not assume that p will be valid when it is used.
                    script = g.getScript(
                        c,
                        p,
                        useSelectedText=False,
                        forcePythonSentinels=True,
                        useSentinels=True)
                    # #2011: put rclicks in aList. Do not inject into command_p.
                    command_p = p.copy()
                    rclicks = build_rclick_tree(command_p, top_level=True)
                    aList.append((command_p, script, rclicks))
                p.moveToThreadNext()
        # This setting is handled differently from most other settings,
        # because the last setting must be retrieved before any commander exists.
        if aList:
            # Bug fix: 2011/11/24: Extend the list, don't replace it.
            g.app.config.atCommonButtonsList.extend(aList)
            g.app.config.buttonsFileName = (c.shortFileName() if c else '<no settings file>')
    #@+node:ekr.20041120094940.2: *4* pbc.doColor
    def doColor(self, p: Position, kind: str, name: str, val: Any) -> None:
        # At present no checking is done.
        val = val.lstrip('"').rstrip('"')
        val = val.lstrip("'").rstrip("'")
        self.set(p, kind, name, val)
    #@+node:ekr.20080312071248.6: *4* pbc.doCommands
    def doCommands(self, p: Position, kind: str, name: str, val: Any) -> None:
        """Handle an @commands tree."""
        c = self.c
        aList = []
        tag = '@command'
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
                if g.match_word(p.h, 0, tag):
                    # We can not assume that p will be valid when it is used.
                    script = g.getScript(c, p,
                        useSelectedText=False,
                        forcePythonSentinels=True,
                        useSentinels=True)
                    aList.append((p.copy(), script),)
                p.moveToThreadNext()
        # This setting is handled differently from most other settings,
        # because the last setting must be retrieved before any commander exists.
        if aList:
            # Bug fix: 2011/11/24: Extend the list, don't replace it.
            g.app.config.atCommonCommandsList.extend(aList)
    #@+node:ekr.20071214140900: *4* pbc.doData
    def doData(self, p: Position, kind: str, name: str, val: Any) -> None:
        # New in Leo 4.11: do not strip lines.
        # New in Leo 4.12.1: strip *nothing* here.
        # New in Leo 4.12.1: allow composition of nodes:
        # - Append all text in descendants in outline order.
        # - Ensure all fragments end with a newline.
        data = g.splitLines(p.b)
        for p2 in p.subtree():
            if p2.b and not p2.h.startswith('@'):
                data.extend(g.splitLines(p2.b))
                if not p2.b.endswith('\n'):
                    data.append('\n')
        self.set(p, kind, name, data)
    #@+node:ekr.20131114051702.16545: *4* pbc.doOutlineData & helper
    def doOutlineData(self, p: Position, kind: str, name: str, val: Any) -> str:
        # New in Leo 4.11: do not strip lines.
        data = self.getOutlineDataHelper(p)
        self.set(p, kind, name, data)
        return 'skip'
    #@+node:ekr.20131114051702.16546: *5* pbc.getOutlineDataHelper
    def getOutlineDataHelper(self, p: Position) -> str:
        c = self.c
        if not p:
            return None
        try:
            # Copy the entire tree to s.
            c.fileCommands.leo_file_encoding = 'utf-8'
            s = c.fileCommands.outline_to_clipboard_string(p)
            s = g.toUnicode(s, encoding='utf-8')
        except Exception:
            g.es_exception()
            s = None
        return s
    #@+node:ekr.20041120094940.3: *4* pbc.doDirectory & doPath
    def doDirectory(self, p: Position, kind: str, name: str, val: Any) -> None:
        # At present no checking is done.
        self.set(p, kind, name, val)

    doPath = doDirectory
    #@+node:ekr.20070224075914: *4* pbc.doEnabledPlugins
    def doEnabledPlugins(self, p: Position, kind: str, name: str, val: Any) -> None:
        c = self.c
        s = p.b
        # This setting is handled differently from all other settings,
        # because the last setting must be retrieved before any commander exists.
        # 2011/09/04: Remove comments, comment lines and blank lines.
        aList, lines = [], g.splitLines(s)
        for s in lines:
            i = s.find('#')
            if i > -1:
                s = s[:i] + '\n'  # 2011/09/29: must add newline back in.
            if s.strip():
                aList.append(s.lstrip())
        s = ''.join(aList)
        # Set the global config ivars.
        g.app.config.enabledPluginsString = s
        g.app.config.enabledPluginsFileName = c.shortFileName() if c else '<no settings file>'
    #@+node:ekr.20041120094940.6: *4* pbc.doFloat
    def doFloat(self, p: Position, kind: str, name: str, val: Any) -> None:
        try:
            val = float(val)
            self.set(p, kind, name, val)
        except ValueError:
            self.valueError(p, kind, name, val)
    #@+node:ekr.20041120094940.4: *4* pbc.doFont
    def doFont(self, p: Position, kind: str, name: str, val: Any) -> None:
        """Handle an @font node. Such nodes affect syntax coloring *only*."""
        d = self.parseFont(p)
        # Set individual settings.
        for key in ('family', 'size', 'slant', 'weight'):
            data = d.get(key)
            if data is not None:
                name, val = data
                setKind = key
                self.set(p, setKind, name, val)
    #@+node:ekr.20150426034813.1: *4* pbc.doIfEnv
    def doIfEnv(self, p: Position, kind: str, name: str, val: Any) -> str:
        """
        Support @ifenv in @settings trees.

        Enable descendant settings if the value of os.getenv is in any of the names.
        """
        aList = name.split(',')
        if not aList:
            return 'skip'
        name = aList[0]
        env = os.getenv(name)
        env = env.lower().strip() if env else 'none'
        for s in aList[1:]:
            if s.lower().strip() == env:
                return None
        return 'skip'
    #@+node:dan.20080410121257.2: *4* pbc.doIfHostname
    def doIfHostname(self, p: Position, kind: str, name: str, val: Any) -> str:
        """
        Support @ifhostname in @settings trees.

        Examples: Let h = os.environ('HOSTNAME')

        @ifhostname bob
            Enable descendant settings if h == 'bob'
        @ifhostname !harry
            Enable descendant settings if h != 'harry'
        """
        lm = g.app.loadManager
        h = lm.computeMachineName().strip()
        s = name.strip()
        if s.startswith('!'):
            if h == s[1:]:
                return 'skip'
        elif h != s:
            return 'skip'
        return None
    #@+node:ekr.20041120104215: *4* pbc.doIfPlatform
    def doIfPlatform(self, p: Position, kind: str, name: str, val: Any) -> str:
        """Support @ifplatform in @settings trees."""
        platform = sys.platform.lower()
        for s in name.split(','):
            if platform == s.lower():
                return None
        return "skip"
    #@+node:ekr.20041120104215.1: *4* pbc.doIgnore
    def doIgnore(self, p: Position, kind: str, name: str, val: Any) -> str:
        return "skip"
    #@+node:ekr.20041120094940.5: *4* pbc.doInt
    def doInt(self, p: Position, kind: str, name: str, val: Any) -> None:
        try:
            val = int(val)
            self.set(p, kind, name, val)
        except ValueError:
            self.valueError(p, kind, name, val)
    #@+node:ekr.20041217132253: *4* pbc.doInts
    def doInts(self, p: Position, kind: str, name: str, val: Any) -> None:
        """
        We expect either:
        @ints [val1,val2,...]aName=val
        @ints aName[val1,val2,...]=val
        """
        name = name.strip()  # The name indicates the valid values.
        i = name.find('[')
        j = name.find(']')
        if -1 < i < j:
            items_s = name[i + 1 : j]
            items = items_s.split(',')
            name = name[:i] + name[j + 1 :].strip()
            try:
                items = [int(item.strip()) for item in items]  # type:ignore
            except ValueError:
                items = []
                self.valueError(p, 'ints[]', name, val)
                return
            kind = f"ints[{','.join([str(item) for item in items])}]"
            try:
                val = int(val)
            except ValueError:
                self.valueError(p, 'int', name, val)
                return
            if val not in items:
                self.error(f"{val} is not in {kind} in {name}")
                return
            # At present no checking is done.
            self.set(p, kind, name, val)
    #@+node:tbrown.20080514112857.124: *4* pbc.doMenuat
    def doMenuat(self, p: Position, kind: str, name: str, val: Any) -> None:
        """Handle @menuat setting."""
        if g.app.config.menusList:
            # get the patch fragment
            patch: list[Any] = []
            if p.hasChildren():
                self.doItems(p.copy(), patch)
            # setup
            parts = name.split()
            if len(parts) != 3:
                parts.append('subtree')
            targetPath, mode, source = parts
            if not targetPath.startswith('/'):
                targetPath = '/' + targetPath
            is_local = 'leosettings' not in self.c.mFileName.lower()
            if is_local:
                mlist = g.app.config.menusList[:]
                self.c.config.set(None, 'menus', 'menus', mlist)
            else:
                mlist = g.app.config.menusList
            ans = self.patchMenuTree(mlist, targetPath)
            if ans:
                list_, idx = ans
                if mode not in ('copy', 'cut'):
                    if source != 'clipboard':
                        use = patch  # [0][1]
                    else:
                        if isinstance(self.clipBoard, list):
                            use = self.clipBoard
                        else:
                            use = [self.clipBoard]
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
                        list_.insert(idx + 1, use.pop())
                elif mode == 'cut':
                    self.clipBoard = list_[idx]
                    del list_[idx]
                elif mode == 'copy':
                    self.clipBoard = list_[idx]
                else:  # append
                    list_.extend(use)
            else:
                g.es_print("ERROR: didn't find menu path " + targetPath)
        elif g.app.inBridge:
            pass  # #48: Not an error.
        else:
            g.es_print("ERROR: @menuat found but no menu tree to patch")

    #@+node:tbrown.20080514180046.9: *5* pbc.getName
    def getName(self, val: str, val2: str = None) -> str:
        if val2 and val2.strip():
            val = val2
        val = val.split('\n', 1)[0]
        for i in "*.-& \t\n":
            val = val.replace(i, '')
        return val.lower()
    #@+node:tbrown.20080514180046.2: *5* pbc.dumpMenuTree
    def dumpMenuTree(self, aList: list, level: int = 0, path: str = '') -> None:
        for z in aList:
            kind, val, val2 = z
            pad = '    ' * level
            if kind == '@item':
                name = self.getName(val, val2)
                g.es_print(f"{pad} {val} ({val2}) [{path + '/' + name}]")
            else:
                name = self.getName(kind.replace('@menu ', ''))
                g.es_print(f"{pad} {kind}... [{path + '/' + name}]")
                self.dumpMenuTree(val, level + 1, path=path + '/' + name)
    #@+node:tbrown.20080514180046.8: *5* pbc.patchMenuTree
    def patchMenuTree(self, orig: list[Any], targetPath: str, path: str = '') -> Any:

        kind: str
        val: Any
        val2: Any
        for n, z in enumerate(orig):
            kind, val, val2 = z
            if kind == '@item':
                name = self.getName(val, val2)
                curPath = path + '/' + name
                if curPath == targetPath:
                    return orig, n
            else:
                name = self.getName(kind.replace('@menu ', ''))
                curPath = path + '/' + name
                if curPath == targetPath:
                    return orig, n
                ans = self.patchMenuTree(val, targetPath, path=path + '/' + name)
                if ans:
                    return ans
        return None
    #@+node:ekr.20070925144337.2: *4* pbc.doMenus & helper
    def doMenus(self, p: Position, kind: str, name: str, val: Any) -> None:
        c = self.c
        p = p.copy()
        aList: list[Any] = []  # This entire logic is mysterious, and likely buggy.
        after = p.nodeAfterTree()
        while p and p != after:
            self.debug_count += 1
            h = p.h
            if g.match_word(h, 0, '@menu'):
                name = h[len('@menu') :].strip()
                if name:
                    for z in aList:
                        name2, junk, junk = z
                        if name2 == name:
                            self.error(f"Replacing previous @menu {name}")
                            break
                    aList2: list[Any] = []  # Huh?
                    kind = f"{'@menu'} {name}"
                    self.doItems(p, aList2)
                    aList.append((kind, aList2, None),)
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()
        if self.localFlag:
            self.set(p, kind='menus', name='menus', val=aList)
        else:
            g.app.config.menusList = aList
            name = c.shortFileName() if c else '<no settings file>'
            g.app.config.menusFileName = name
    #@+node:ekr.20070926141716: *5* pbc.doItems
    def doItems(self, p: Position, aList: list) -> None:

        p = p.copy()
        after = p.nodeAfterTree()
        p.moveToThreadNext()
        while p and p != after:
            self.debug_count += 1
            h = p.h
            for tag in ('@menu', '@item', '@ifplatform'):
                if g.match_word(h, 0, tag):
                    itemName = h[len(tag) :].strip()
                    if itemName:
                        lines = [z for z in g.splitLines(p.b) if
                            z.strip() and not z.strip().startswith('#')]
                        # Only the first body line is significant.
                        # This allows following comment lines.
                        body = lines[0].strip() if lines else ''
                        if tag == '@menu':
                            aList2: list[Any] = []  # Huh?
                            kind = f"{tag} {itemName}"
                            self.doItems(p, aList2)  # Huh?
                            aList.append((kind, aList2, body),)  # #848: Body was None.
                            p.moveToNodeAfterTree()
                            break
                        else:
                            kind = tag
                            head = itemName
                            # We must not clean non-unicode characters!
                            aList.append((kind, head, body),)
                            p.moveToThreadNext()
                            break
            else:
                p.moveToThreadNext()
    #@+node:ekr.20060102103625.1: *4* pbc.doMode
    def doMode(self, p: Position, kind: str, name: str, val: Any) -> None:
        """Parse an @mode node and create the enter-<name>-mode command."""
        c = self.c
        name1 = name
        modeName = self.computeModeName(name)
        d: dict[str, list[g.BindingInfo]] = g.SettingsDict(f"modeDict for {modeName}")
        s = p.b
        lines = g.splitLines(s)
        for line in lines:
            line = line.strip()
            if line and not g.match(line, 0, '#'):
                name, bi = self.parseShortcutLine('*mode-setting*', line)
                if not name:
                    # An entry command: put it in the special *entry-commands* key.
                    d.add_to_list('*entry-commands*', bi)
                elif bi is not None:
                    # A regular shortcut.
                    bi.pane = modeName
                    aList: list[g.BindingInfo] = d.get(name, [])
                    # Important: use previous bindings if possible.
                    key2, aList2 = c.config.getShortcut(name)
                    aList3 = [z for z in aList2 if z.pane != modeName]
                    if aList3:
                        aList.extend(aList3)
                    aList.append(bi)
                    d[name] = aList
            # Restore the global shortcutsDict.
            # Create the command, but not any bindings to it.
            self.createModeCommand(modeName, name1, d)
    #@+node:ekr.20070411101643.1: *4* pbc.doOpenWith
    def doOpenWith(self, p: Position, kind: str, name: str, val: Any) -> None:

        d = self.parseOpenWith(p)
        d['name'] = name
        d['shortcut'] = val
        name = kind = 'openwithtable'
        self.openWithList.append(d)
        self.set(p, kind, name, self.openWithList)
    #@+node:bobjack.20080324141020.4: *4* pbc.doPopup & helper
    def doPopup(self, p: Position, kind: str, name: str, val: Any) -> None:
        """
        Handle @popup menu items in @settings trees.
        """
        popupName = name
        # popupType = val
        aList: list[Any] = []
        p = p.copy()
        self.doPopupItems(p, aList)
        if not hasattr(g.app.config, 'context_menus'):
            g.app.config.context_menus = {}
        g.app.config.context_menus[popupName] = aList
    #@+node:bobjack.20080324141020.5: *5* pbc.doPopupItems
    def doPopupItems(self, p: Position, aList: list) -> None:
        p = p.copy()
        after = p.nodeAfterTree()
        p.moveToThreadNext()
        while p and p != after:
            h = p.h
            for tag in ('@menu', '@item'):
                if g.match_word(h, 0, tag):
                    itemName = h[len(tag) :].strip()
                    if itemName:
                        if tag == '@menu':
                            aList2: list[Any] = []
                            kind = f"{itemName}"
                            body = p.b
                            self.doPopupItems(p, aList2)  # Huh?
                            aList.append((kind + '\n' + body, aList2),)
                            p.moveToNodeAfterTree()
                            break
                        else:
                            kind = tag
                            head = itemName
                            body = p.b
                            aList.append((head, body),)
                            p.moveToThreadNext()
                            break
            else:
                p.moveToThreadNext()
    #@+node:ekr.20041121125741: *4* pbc.doRatio
    def doRatio(self, p: Position, kind: str, name: str, val: Any) -> None:
        try:
            val = float(val)
            if 0.0 <= val <= 1.0:
                self.set(p, kind, name, val)
            else:
                self.valueError(p, kind, name, val)
        except ValueError:
            self.valueError(p, kind, name, val)
    #@+node:ekr.20041120105609: *4* pbc.doShortcuts
    def doShortcuts(self, p: Position, kind: str, junk_name: str, junk_val: Any, s: str = None) -> None:
        """Handle an @shortcut or @shortcuts node."""
        c, d = self.c, self.shortcutsDict
        if s is None:
            s = p.b
        fn = d.name()
        for line in g.splitLines(s):
            line = line.strip()
            if line and not g.match(line, 0, '#'):
                commandName, bi = self.parseShortcutLine(fn, line)
                if bi is None:  # Fix #718.
                    print(f"\nWarning: bad shortcut specifier: {line!r}\n")
                else:
                    if bi and bi.stroke not in (None, 'none', 'None'):
                        self.doOneShortcut(bi, commandName, p)
                    else:
                        # New in Leo 5.7: Add local assignments to None to c.k.killedBindings.
                        if c.config.isLocalSettingsFile():
                            c.k.killedBindings.append(commandName)
    #@+node:ekr.20111020144401.9585: *5* pbc.doOneShortcut
    def doOneShortcut(self, bi: Any, commandName: str, p: Position) -> None:
        """Handle a regular shortcut."""
        d = self.shortcutsDict
        aList: list[g.BindingInfo] = d.get(commandName, [])
        aList.append(bi)
        d[commandName] = aList
    #@+node:ekr.20041217132028: *4* pbc.doString
    def doString(self, p: Position, kind: str, name: str, val: Any) -> None:
        # At present no checking is done.
        self.set(p, kind, name, val)
    #@+node:ekr.20041120094940.8: *4* pbc.doStrings
    def doStrings(self, p: Position, kind: str, name: str, val: Any) -> None:
        """
        We expect one of the following:
        @strings aName[val1,val2...]=val
        @strings [val1,val2,...]aName=val
        """
        name = name.strip()
        i = name.find('[')
        j = name.find(']')
        if -1 < i < j:
            items_s = name[i + 1 : j]
            items = items_s.split(',')
            items = [item.strip() for item in items]
            name = name[:i] + name[j + 1 :].strip()
            kind = f"strings[{','.join(items)}]"
            # At present no checking is done.
            self.set(p, kind, name, val)
    #@+node:ekr.20041124063257: *3* pbc.munge
    def munge(self, s: str) -> str:
        return g.app.config.canonicalizeSettingName(s)
    #@+node:ekr.20041213082558: *3* pbc.parsers
    #@+node:ekr.20041213082558.1: *4* pbc.parseFont & helper
    def parseFont(self, p: Position) -> dict[str, Any]:
        d: dict[str, Any] = {
            'comments': [],
            'family': None,
            'size': None,
            'slant': None,
            'weight': None,
        }
        s = p.b
        lines = g.splitLines(s)
        for line in lines:
            self.parseFontLine(line, d)
        comments = d.get('comments')
        d['comments'] = '\n'.join(comments)
        return d
    #@+node:ekr.20041213082558.2: *5* pbc.parseFontLine
    def parseFontLine(self, line: str, d: dict[str, Any]) -> None:
        s = line.strip()
        if not s:
            return
        try:
            s = str(s)
        except UnicodeError:
            pass
        if g.match(s, 0, '#'):
            s = s[1:].strip()
            comments = d.get('comments')
            comments.append(s)
            d['comments'] = comments
            return
        # name is everything up to '='
        i = s.find('=')
        if i == -1:
            name = s
            val = None
        else:
            name = s[:i].strip()
            val = s[i + 1 :].strip().strip('"').strip("'")
        for tag in ('_family', '_size', '_slant', '_weight'):
            if name.endswith(tag):
                kind = tag[1:]
                d[kind] = name, val  # Used only by doFont.
                return
    #@+node:ekr.20041119205148: *4* pbc.parseHeadline
    def parseHeadline(self, s: str) -> tuple[str, str, Any]:
        """
        Parse a headline of the form @kind:name=val
        Return (kind,name,val).
        Leo 4.11.1: Ignore everything after @data name.
        """
        kind = name = val = None
        if g.match(s, 0, '@'):
            i = g.skip_id(s, 1, chars='-')
            i = g.skip_ws(s, i)
            kind = s[1:i].strip()
            if kind:
                # name is everything up to '='
                if kind == 'data':
                    # i = g.skip_ws(s,i)
                    j = s.find(' ', i)
                    if j == -1:
                        name = s[i:].strip()
                    else:
                        name = s[i:j].strip()
                else:
                    j = s.find('=', i)
                    if j == -1:
                        name = s[i:].strip()
                    else:
                        name = s[i:j].strip()
                        # val is everything after the '='
                        val = s[j + 1 :].strip()
        return kind, name, val
    #@+node:ekr.20070411101643.2: *4* pbc.parseOpenWith & helper
    def parseOpenWith(self, p: Position) -> dict[str, Any]:

        d = {'command': None}  # d contains args, kind, etc tags.
        for line in g.splitLines(p.b):
            self.parseOpenWithLine(line, d)
        return d
    #@+node:ekr.20070411101643.4: *5* pbc.parseOpenWithLine
    def parseOpenWithLine(self, line: str, d: dict[str, Any]) -> None:
        s = line.strip()
        if not s:
            return
        i = g.skip_ws(s, 0)
        if g.match(s, i, '#'):
            return
        j = g.skip_c_id(s, i)
        tag = s[i:j].strip()
        if not tag:
            g.es_print(f"@openwith lines must start with a tag: {s}")
            return
        i = g.skip_ws(s, j)
        if not g.match(s, i, ':'):
            g.es_print(f"colon must follow @openwith tag: {s}")
            return
        i += 1
        val = s[i:].strip() or ''  # An empty val is valid.
        if tag == 'arg':
            aList: list[Any] = d.get('args', [])
            aList.append(val)
            d['args'] = aList
        elif d.get(tag):
            g.es_print(f"ignoring duplicate definition of {tag} {s}")
        else:
            d[tag] = val
    #@+node:ekr.20041120112043: *4* pbc.parseShortcutLine
    def parseShortcutLine(self, kind: str, s: str) -> tuple[str, Any]:
        """Parse a shortcut line.  Valid forms:

        --> entry-command
        settingName = shortcut
        settingName ! paneName = shortcut
        command-name --> mode-name = binding
        command-name --> same = binding
        """
        s = s.replace('\x7f', '')  # Can happen on MacOS. Very weird.
        name = val = nextMode = None
        nextMode = 'none'
        i = g.skip_ws(s, 0)
        if g.match(s, i, '-->'):  # New in 4.4.1 b1: allow mode-entry commands.
            j = g.skip_ws(s, i + 3)
            i = g.skip_id(s, j, '-')
            entryCommandName = s[j:i]
            return None, g.BindingInfo('*entry-command*', commandName=entryCommandName)
        j = i
        i = g.skip_id(s, j, '-@')  # #718.
        name = s[j:i]
        # #718: Allow @button- and @command- prefixes.
        for tag in ('@button-', '@command-'):
            if name.startswith(tag):
                name = name[len(tag) :]
                break
        if not name:
            return None, None
        # New in Leo 4.4b2.
        i = g.skip_ws(s, i)
        if g.match(s, i, '->'):  # New in 4.4: allow pane-specific shortcuts.
            j = g.skip_ws(s, i + 2)
            i = g.skip_id(s, j)
            nextMode = s[j:i]
        i = g.skip_ws(s, i)
        if g.match(s, i, '!'):  # New in 4.4: allow pane-specific shortcuts.
            j = g.skip_ws(s, i + 1)
            i = g.skip_id(s, j)
            pane = s[j:i]
            if not pane.strip():
                pane = 'all'
        else:
            pane = 'all'
        i = g.skip_ws(s, i)
        if g.match(s, i, '='):
            i = g.skip_ws(s, i + 1)
            val = s[i:]
        # New in 4.4: Allow comments after the shortcut.
        # Comments must be preceded by whitespace.
        if val:
            i = val.find('#')
            if i > 0 and val[i - 1] in (' ', '\t'):
                val = val[:i].strip()
        if not val:
            return name, None
        stroke = g.KeyStroke(binding=val) if val else None
        bi = g.BindingInfo(kind=kind, nextMode=nextMode, pane=pane, stroke=stroke)
        return name, bi
    #@+node:ekr.20041120094940.9: *3* pbc.set
    def set(self, p: Position, kind: str, name: str, val: Any) -> None:
        """Init the setting for name to val."""
        c = self.c
        # Note: when kind is 'shortcut', name is a command name.
        key = self.munge(name)
        if key is None:
            g.es_print(f"Empty setting name in {p.h} in {c.fileName()}")
            parent = p.parent()
            while parent:
                g.trace('parent', parent.h)
                parent.moveToParent()
            return
        d = self.settingsDict
        gs = d.get(key)
        if gs:
            assert isinstance(gs, g.GeneralSetting), gs
            path = gs.path
            if g.finalize(c.mFileName) != g.finalize(path):
                g.es("over-riding setting:", name, "from", path)  # 1341
        # Important: we can't use c here: it may be destroyed!
        d[key] = g.GeneralSetting(kind,
            path=c.mFileName,
            tag='setting',
            source=p.h if p else '',
            unl=p.get_UNL() if p else '',
            val=val,
        )
    #@+node:ekr.20041119204700.1: *3* pbc.traverse
    def traverse(self) -> tuple[Any, Any]:
        """Traverse the entire settings tree."""
        c = self.c
        self.settingsDict: dict[str, list[g.GeneralSetting]] = g.SettingsDict(f"settingsDict for {c.shortFileName()}")
        self.shortcutsDict = g.SettingsDict(f"shortcutsDict for {c.shortFileName()}")
        # This must be called after the outline has been inited.
        p = c.config.settingsRoot()
        if not p:
            # c.rootPosition() doesn't exist yet.
            # This is not an error.
            return self.shortcutsDict, self.settingsDict
        after = p.nodeAfterTree()
        while p and p != after:
            result = self.visitNode(p)
            if result == "skip":
                # g.warning('skipping settings in',p.h)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        # Return the raw dict, unmerged.
        return self.shortcutsDict, self.settingsDict
    #@+node:ekr.20041120094940.10: *3* pbc.valueError
    def valueError(self, p: Position, kind: str, name: str, val: Any) -> None:
        """Give an error: val is not valid for kind."""
        self.error(f"{val} is not a valid {kind} for {name}")
    #@+node:ekr.20041119204700.3: *3* pbc.visitNode (must be overwritten in subclasses)
    def visitNode(self, p: Position) -> str:
        raise NotImplementedError
    #@-others
#@-<< class ParserBaseClass >>
#@+others
#@+node:ekr.20190905091614.1: ** class ActiveSettingsOutline
class ActiveSettingsOutline:

    def __init__(self, c: Cmdr) -> None:

        self.c = c
        self.start()
        self.create_outline()
    #@+others
    #@+node:ekr.20190905091614.2: *3* aso.start & helpers
    def start(self) -> None:
        """Do everything except populating the new outline."""
        # Copy settings.
        c = self.c
        settings = c.config.settingsDict
        shortcuts = c.config.shortcutsDict
        assert isinstance(settings, g.SettingsDict), repr(settings)
        assert isinstance(shortcuts, g.SettingsDict), repr(shortcuts)
        settings_copy = settings.copy()
        shortcuts_copy = shortcuts.copy()
        # Create the new commander.
        self.commander = self.new_commander()
        # Open hidden commanders for non-local settings files.
        self.load_hidden_commanders()
        # Create the ordered list of commander tuples, including the local .leo file.
        self.create_commanders_list()
        # Jam the old settings into the new commander.
        self.commander.config.settingsDict = settings_copy
        self.commander.config.shortcutsDict = shortcuts_copy
    #@+node:ekr.20190905091614.3: *4* aso.create_commanders_list
    def create_commanders_list(self) -> None:

        """Create the commanders list. Order matters."""
        lm = g.app.loadManager
        # The first element of each tuple must match the return values of c.config.getSource.
        # "local_file", "theme_file", "myLeoSettings", "leoSettings"

        self.commanders = [
            ('leoSettings', lm.leo_settings_c),
            ('myLeoSettings', lm.my_settings_c),
        ]
        if lm.theme_c:
            self.commanders.append(('theme_file', lm.theme_c),)
        if self.c.config.settingsRoot():
            self.commanders.append(('local_file', self.c),)
    #@+node:ekr.20190905091614.4: *4* aso.load_hidden_commanders
    def load_hidden_commanders(self) -> None:
        """
        Open hidden commanders for leoSettings.leo, myLeoSettings.leo and theme.leo.
        """
        lm = g.app.loadManager
        lm.readGlobalSettingsFiles()
        # Make sure to reload the local file.
        c = g.app.commanders()[0]
        fn = c.fileName()
        if fn:
            self.local_c = lm.openSettingsFile(fn)
    #@+node:ekr.20190905091614.5: *4* aso.new_commander
    def new_commander(self) -> Cmdr:
        """Create the new commander, and load all settings files."""
        lm = g.app.loadManager
        old_c = self.c

        # Save any changes so they can be seen.
        if old_c.isChanged():
            old_c.save()
        old_c.outerUpdate()

        # Suppress redraws until later.
        g.app.disable_redraw = True
        g.app.setLog(None)
        g.app.lockLog()

        # Switch to the new commander. Do *not* use previous settings.
        fileName = f"{old_c.fileName()}-active-settings"
        g.es(fileName, color='red')
        c = g.app.newCommander(fileName=fileName)

        # Restore the layout, if we have ever saved this file.
        if not old_c:
            c.frame.setInitialWindowGeometry()

        # #1340: Don't do this. It is no longer needed.
            # g.app.restoreWindowState(c)

        c.frame.resizePanesToRatio(c.frame.ratio, c.frame.secondary_ratio)
        c.clearChanged()  # Clears all dirty bits.

        # Finish.
        lm.finishOpen(c)
        return c
    #@+node:ekr.20190905091614.6: *3* aso.create_outline & helper
    def create_outline(self) -> None:
        """Create the summary outline"""
        c = self.commander
        #
        # Create the root node, with the legend in the body text.
        root = c.rootPosition()
        root.h = f"Legend for {self.c.shortFileName()}"
        root.b = self.legend()
        #
        # Create all the inner settings outlines.
        for kind, commander in self.commanders:
            p = root.insertAfter()
            p.h = g.shortFileName(commander.fileName())
            p.b = '@language rest\n@wrap\n'
            self.create_inner_outline(commander, kind, p)
        #
        # Clean all dirty/changed bits, so closing this outline won't prompt for a save.
        for v in c.all_nodes():
            v.clearDirty()
        c.setChanged()
        c.redraw()
    #@+node:ekr.20190905091614.7: *4* aso.legend
    def legend(self) -> str:
        """Compute legend for self.c"""
        c, lm = self.c, g.app.loadManager
        legend = f'''\
            @language rest

            legend:

                leoSettings.leo
             @  @button, @command, @mode
            [D] default settings
            [F] local file: {c.shortFileName()}
            [M] myLeoSettings.leo
            '''
        if lm.theme_path:
            legend = legend + f"[T] theme file: {g.shortFileName(lm.theme_path)}\n"
        return textwrap.dedent(legend)
    #@+node:ekr.20190905091614.8: *3* aso.create_inner_outline
    def create_inner_outline(self, c: Cmdr, kind: str, root: Position) -> None:
        """
        Create the outline for the given hidden commander, as descendants of root.
        """
        # Find the settings tree
        settings_root = c.config.settingsRoot()
        if not settings_root:
            # This should not be called if the local file has no @settings node.
            g.trace('no @settings node!!', c.shortFileName())
            return
        # Unify all settings.
        self.create_unified_settings(kind, root, settings_root)
        self.clean(root)
    #@+node:ekr.20190905091614.9: *3* aso.create_unified_settings
    def create_unified_settings(self, kind: str, root: Position, settings_root: Position) -> None:
        """Create the active settings tree under root."""
        c = self.commander
        lm = g.app.loadManager
        settings_pat = re.compile(r'^(@[\w-]+)(\s+[\w\-\.]+)?')
        valid_list = [
            '@bool', '@color', '@directory', '@encoding',
            '@int', '@float', '@ratio', '@string',
        ]
        d = self.filter_settings(kind)
        ignore, outline_data = None, None
        self.parents = [root]
        self.level = settings_root.level()
        for p in settings_root.subtree():
            #@+<< continue if we should ignore p >>
            #@+node:ekr.20190905091614.10: *4* << continue if we should ignore p >>
            if ignore:
                if p == ignore:
                    ignore = None
                else:
                    # g.trace('IGNORE', p.h)
                    continue
            if outline_data:
                if p == outline_data:
                    outline_data = None
                else:
                    self.add(p)
                    continue
            #@-<< continue if we should ignore p >>
            m = settings_pat.match(p.h)
            if not m:
                self.add(p, h='ORG:' + p.h)
                continue
            if m.group(2) and m.group(1) in valid_list:
                #@+<< handle a real setting >>
                #@+node:ekr.20190905091614.11: *4* << handle a real setting >>
                key = g.app.config.munge(m.group(2).strip())
                val = d.get(key)
                if isinstance(val, g.GeneralSetting):
                    self.add(p)
                else:
                    # Look at all the settings to discover where the setting is defined.
                    val = c.config.settingsDict.get(key)
                    if isinstance(val, g.GeneralSetting):
                        # Use self.c, not self.commander.
                        letter = lm.computeBindingLetter(self.c, val.path)
                        p.h = f"[{letter}] INACTIVE: {p.h}"
                        p.h = f"UNUSED: {p.h}"
                    self.add(p)
                #@-<< handle a real setting >>
                continue
            # Not a setting. Handle special cases.
            if m.group(1) == '@ignore':
                ignore = p.nodeAfterTree()
            elif m.group(1) in ('@data', '@outline-data'):
                outline_data = p.nodeAfterTree()
                self.add(p)
            else:
                self.add(p)
    #@+node:ekr.20190905091614.12: *3* aso.add
    def add(self, p: Position, h: str = None) -> None:
        """
        Add a node for p.

        We must *never* alter p in any way.
        Instead, the org flag tells whether the "ORG:" prefix.
        """
        if 0:
            pad = ' ' * p.level()
            print(pad, p.h)
        p_level = p.level()
        if p_level > self.level + 1:
            g.trace('OOPS', p.v.context.shortFileName(), self.level, p_level, p.h)
            return
        while p_level < self.level + 1 and len(self.parents) > 1:
            self.parents.pop()
            self.level -= 1
        parent = self.parents[-1]
        child = parent.insertAsLastChild()
        child.h = h or p.h
        child.b = p.b
        self.parents.append(child)
        self.level += 1
    #@+node:ekr.20190905091614.13: *3* aso.clean
    def clean(self, root: Position) -> None:
        """
        Remove all unnecessary nodes.
        Remove the "ORG:" prefix from remaining nodes.
        """
        self.clean_node(root)

    def clean_node(self, p: Position) -> None:
        """Remove p if it contains no children after cleaning its children."""
        tag = 'ORG:'
        # There are no clones, so deleting children in reverse preserves positions.
        for child in reversed(list(p.children())):
            self.clean_node(child)
        if p.h.startswith(tag):
            if p.hasChildren():
                p.h = p.h.lstrip(tag).strip()
            else:
                p.doDelete()
    #@+node:ekr.20190905091614.14: *3* aso.filter_settings
    def filter_settings(self, target_kind: str) -> dict[str, Any]:
        """Return a dict containing only settings defined in the file given by kind."""
        # Crucial: Always use the newly-created commander.
        #          It's settings are guaranteed to be correct.
        c = self.commander
        valid_kinds = ('local_file', 'theme_file', 'myLeoSettings', 'leoSettings')
        assert target_kind in valid_kinds, repr(target_kind)
        d = c.config.settingsDict
        result = {}
        for key in d.keys():
            gs = d.get(key)
            assert isinstance(gs, g.GeneralSetting), repr(gs)
            if not gs.kind:
                g.trace('OOPS: no kind', repr(gs))
                continue
            kind = c.config.getSource(setting=gs)
            if kind == 'ignore':
                g.trace('IGNORE:', kind, key)
                continue
            if kind == 'error':  # 2021/09/18.
                g.trace('ERROR:', kind, key)
                continue
            if kind == target_kind:
                result[key] = gs
        return result
    #@-others
#@+node:ekr.20041119203941: ** class GlobalConfigManager
class GlobalConfigManager:
    """A class to manage configuration settings."""

    #@+others
    #@+node:ekr.20041117062717.2: *3*  gcm.ctor
    def __init__(self) -> None:

        # List of info (command_p, script, rclicks) for common @buttons nodes.
        # where rclicks is a namedtuple('RClick', 'position,children')
        self.atCommonButtonsList: list[tuple[Cmdr, str, Any]] = []
        self.atCommonCommandsList: list[tuple[Cmdr, str]] = []  # List of info for common @commands nodes.
        self.atLocalButtonsList: list[Position] = []  # List of positions of @button nodes.
        self.atLocalCommandsList: list[Position] = []  # List of positions of @command nodes.
        self.buttonsFileName = ''
        self.configsExist = False  # True when we successfully open a setting file.
        self.default_derived_file_encoding = 'utf-8'
        self.enabledPluginsFileName = None
        self.enabledPluginsString = ''
        self.menusList: list[Any] = []
        self.menusFileName = ''
        self.modeCommandsDict: dict[str, g.SettingsDict] = g.SettingsDict('modeCommandsDict')
        self.panes = None
        self.recentFiles: list[str] = []
        self.sc = None
        self.tree = None
    #@+node:ekr.20120222103014.10314: *3* gcm.config_iter
    def config_iter(self, c: Cmdr) -> Generator:
        """Letters:
          leoSettings.leo
        D default settings
        F loaded .leo File
        M myLeoSettings.leo
        @ @button, @command, @mode.
        """
        lm = g.app.loadManager
        d = c.config.settingsDict if c else lm.globalSettingsDict
        limit = c.config.getInt('print-settings-at-data-limit')
        if limit is None:
            limit = 20  # A reasonable default.
        for key in sorted(list(d.keys())):
            gs = d.get(key)  # gs is a GeneralSetting or None
            if gs and gs.kind:
                letter = lm.computeBindingLetter(c, gs.path)
                val = gs.val
                if gs.kind == 'data':
                    # #748: Remove comments
                    aList = [' ' * 8 + z.rstrip() for z in val
                        if z.strip() and not z.strip().startswith('#')]
                    if not aList:
                        val = '[]'
                    elif limit == 0 or len(aList) < limit:
                        val = '\n    [\n' + '\n'.join(aList) + '\n    ]'
                        # The following doesn't work well.
                        # val = g.objToString(aList, indent=4)
                    else:
                        val = f"<{len(aList)} non-comment lines>"
                elif isinstance(val, str) and val.startswith('<?xml'):
                    val = '<xml>'
                key2 = f"@{gs.kind:<6} {key}"
                yield key2, val, c, letter
    #@+node:ekr.20041123070429: *3* gcm.canonicalizeSettingName (munge)
    def canonicalizeSettingName(self, name: str) -> str:
        if name is None:
            return None
        name = name.lower()
        for ch in ('-', '_', ' ', '\n'):
            name = name.replace(ch, '')
        return name if name else None

    munge = canonicalizeSettingName
    #@+node:ekr.20041117081009: *3* gcm.Getters...
    #@+node:ekr.20051011105014: *4* gcm.exists
    def exists(self, setting: str, kind: str) -> bool:
        """Return true if a setting of the given kind exists, even if it is None."""
        lm = g.app.loadManager
        d = lm.globalSettingsDict
        if d:
            junk, found = self.getValFromDict(d, setting, kind)
            return found
        return False
    #@+node:ekr.20041117083141: *4* gcm.get & allies
    def get(self, setting: str, kind: str) -> Any:
        """Get the setting and make sure its type matches the expected type."""
        # It *is* valid to call this method: it returns the global settings.
        lm = g.app.loadManager
        d = lm.globalSettingsDict
        if d:
            assert isinstance(d, g.SettingsDict), d.__class__.__name__
            val, junk = self.getValFromDict(d, setting, kind)
            return val
        return None
    #@+node:ekr.20041121143823: *5* gcm.getValFromDict
    def getValFromDict(self,
        d: Any, setting: str, requestedType: str, warn: bool = True,
    ) -> tuple[Any, bool]:
        """
        Look up the setting in d. If warn is True, warn if the requested type
        does not (loosely) match the actual type.
        returns (val,exists)
        """
        tag = 'gcm.getValFromDict'
        gs = d.get(self.munge(setting))
        if not gs:
            return None, False
        assert isinstance(gs, g.GeneralSetting), repr(gs)
        val = gs.val
        isNone = val in ('None', 'none', '')
        if not self.typesMatch(gs.kind, requestedType):
            # New in 4.4: make sure the types match.
            # A serious warning: one setting may have destroyed another!
            # Important: this is not a complete test of conflicting settings:
            # The warning is given only if the code tries to access the setting.
            if warn:
                g.error(
                    f"{tag}: ignoring '{setting}' setting.\n"
                    f"{tag}: '@{gs.kind}' is not '@{requestedType}'.\n"
                    f"{tag}: there may be conflicting settings!")
            return None, False
        if isNone:
            return '', True  # 2011/10/24: Exists, a *user-defined* empty value.
        return val, True
    #@+node:ekr.20051015093141: *5* gcm.typesMatch
    def typesMatch(self, type1: str, type2: str) -> bool:
        """
        Return True if type1, the actual type, matches type2, the requested type.

        The following equivalences are allowed:

        - None matches anything.
        - An actual type of string or strings matches anything *except* shortcuts.
        - Shortcut matches shortcuts.
        """
        # The shortcuts logic no longer uses the get/set code.
        shortcuts = ('shortcut', 'shortcuts',)
        if type1 in shortcuts or type2 in shortcuts:
            g.trace('oops: type in shortcuts')
        return (
            type1 is None
            or type2 is None
            or type1.startswith('string') and type2 not in shortcuts
            or type1 == 'language' and type2 == 'string'
            or type1 == 'int' and type2 == 'size'
            or (type1 in shortcuts and type2 in shortcuts)
            or type1 == type2
        )
    #@+node:ekr.20060608224112: *4* gcm.getAbbrevDict
    def getAbbrevDict(self) -> dict[str, Any]:
        """Search all dictionaries for the setting & check it's type"""
        d = self.get('abbrev', 'abbrev')
        return d or {}
    #@+node:ekr.20041117081009.3: *4* gcm.getBool
    def getBool(self, setting: str, default: bool = None) -> bool:
        """Return the value of @bool setting, or the default if the setting is not found."""
        val = self.get(setting, "bool")
        if val in (True, False):
            return val
        return default
    #@+node:ekr.20070926082018: *4* gcm.getButtons
    def getButtons(self) -> list:
        """Return a list of tuples for common @button nodes."""
        return g.app.config.atCommonButtonsList
    #@+node:ekr.20041122070339: *4* gcm.getColor
    def getColor(self, setting: str) -> str:
        """Return the value of @color setting."""
        col = self.get(setting, "color")
        while col and col.startswith('@'):
            col = self.get(col[1:], "color")
        return col
    #@+node:ekr.20080312071248.7: *4* gcm.getCommonCommands
    def getCommonAtCommands(self) -> list[tuple[str, str]]:
        """Return the list of tuples (headline,script) for common @command nodes."""
        return g.app.config.atCommonCommandsList
    #@+node:ekr.20071214140900.1: *4* gcm.getData & getOutlineData
    def getData(self,
        setting: str, strip_comments: bool = True, strip_data: bool = True,
    ) -> list[str]:
        """Return a list of non-comment strings in the body text of @data setting."""
        data = self.get(setting, "data") or []
        # New in Leo 4.12.1: add two keyword arguments, with legacy defaults.
        if data and strip_comments:
            data = [z for z in data if not z.strip().startswith('#')]
        if data and strip_data:
            data = [z.strip() for z in data if z.strip()]
        return data

    def getOutlineData(self, setting: str) -> None:
        """Return the pastable (xml text) of the entire @outline-data tree."""
        return self.get(setting, "outlinedata")
    #@+node:ekr.20041117093009.1: *4* gcm.getDirectory
    def getDirectory(self, setting: str) -> str:
        """Return the value of @directory setting, or None if the directory does not exist."""
        # Fix https://bugs.launchpad.net/leo-editor/+bug/1173763
        theDir = self.get(setting, 'directory')
        if g.os_path_exists(theDir) and g.os_path_isdir(theDir):
            return theDir
        return None
    #@+node:ekr.20070224075914.1: *4* gcm.getEnabledPlugins
    def getEnabledPlugins(self) -> str:
        """Return the body text of the @enabled-plugins node."""
        return g.app.config.enabledPluginsString
    #@+node:ekr.20041117082135: *4* gcm.getFloat
    def getFloat(self, setting: str) -> float:
        """Return the value of @float setting."""
        val = self.get(setting, "float")
        try:
            val = float(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20041117062717.13: *4* gcm.getFontFromParams
    def getFontFromParams(self,
        family: str, size: str, slant: str, weight: str, defaultSize: int = 12, tag: str = '',
    ) -> Any:
        """Compute a font from font parameters.

        Arguments are the names of settings to be use.
        Default to size=12, slant="roman", weight="normal".

        Return None if there is no family setting so we can use system default fonts."""
        family = self.get(family, "family")
        if family in (None, ""):
            family = None
        size = self.get(size, "size")
        if size in (None, 0):
            size = str(defaultSize)  # type:ignore
        slant = self.get(slant, "slant")
        if slant in (None, ""):
            slant = "roman"
        weight = self.get(weight, "weight")
        if weight in (None, ""):
            weight = "normal"
        return g.app.gui.getFontFromParams(family, size, slant, weight)
    #@+node:ekr.20041117081513: *4* gcm.getInt
    def getInt(self, setting: str) -> int:
        """Return the value of @int setting."""
        val = self.get(setting, "int")
        try:
            val = int(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20041117093009.2: *4* gcm.getLanguage
    def getLanguage(self, setting: str) -> str:
        """Return the setting whose value should be a language known to Leo."""
        language = self.getString(setting)
        return language
    #@+node:ekr.20070926070412: *4* gcm.getMenusList
    def getMenusList(self) -> list:
        """Return the list of entries for the @menus tree."""
        aList = self.get('menus', 'menus')
        # aList is typically empty.
        return aList or g.app.config.menusList
    #@+node:ekr.20070411101643: *4* gcm.getOpenWith
    def getOpenWith(self) -> list[dict[str, Any]]:
        """Return a list of dictionaries corresponding to @openwith nodes."""
        val = self.get('openwithtable', 'openwithtable')
        return val
    #@+node:ekr.20041122070752: *4* gcm.getRatio
    def getRatio(self, setting: str) -> Optional[float]:
        """
        Return the value of @float setting, or None if there is an error.
        """
        val = self.get(setting, "ratio")
        try:
            val = float(val)
            if 0.0 <= val <= 1.0:
                return val
        except TypeError:
            pass
        return None
    #@+node:ekr.20041117062717.11: *4* gcm.getRecentFiles
    def getRecentFiles(self) -> list[str]:
        """Return the list of recently opened files."""
        return self.recentFiles
    #@+node:ekr.20041117081009.4: *4* gcm.getString
    def getString(self, setting: str) -> str:
        """Return the value of @string setting."""
        return self.get(setting, "string")
    #@+node:ekr.20171115062202.1: *3* gcm.valueInMyLeoSettings
    def valueInMyLeoSettings(self, settingName: str) -> Any:
        """Return the value of the setting, if any, in myLeoSettings.leo."""
        lm = g.app.loadManager
        d = lm.globalSettingsDict
        gs = d.get(self.munge(settingName))  # A GeneralSetting.
        if gs:
            path = gs.path
            if path.find('myLeoSettings.leo') > -1:
                return gs.val
        return None
    #@-others
#@+node:ekr.20041118104831.1: ** class LocalConfigManager
class LocalConfigManager:
    """A class to hold config settings for commanders."""
    #@+others
    #@+node:ekr.20041118104831.2: *3*  c.config.ctor
    def __init__(self, c: Cmdr, previousSettings: PreviousSettings = None) -> None:
        self.c = c
        lm = g.app.loadManager
        if previousSettings:
            self.settingsDict = previousSettings.settingsDict
            self.shortcutsDict = previousSettings.shortcutsDict
            assert isinstance(self.settingsDict, g.SettingsDict), self.settingsDict.__class__.__name__
            assert isinstance(self.shortcutsDict, g.SettingsDict), self.shortcutsDict.__class__.__name__
        else:
            self.settingsDict = d1 = lm.globalSettingsDict
            self.shortcutsDict = d2 = lm.globalBindingsDict
            assert d1 is None or isinstance(d1, g.SettingsDict), d1.__class__.__name__
            assert d2 is None or isinstance(d2, g.SettingsDict), d2.__class__.__name__
        # Default encodings.
        self.default_at_auto_file_encoding = 'utf-8'
        self.default_derived_file_encoding = 'utf-8'
        self.new_leo_file_encoding = 'utf-8'
        # Default fonts.
        self.defaultBodyFontSize = 12  # 9 if sys.platform == "win32" else 12
        self.defaultLogFontSize = 12  # 8 if sys.platform == "win32" else 12
        self.defaultMenuFontSize = 12  # 9 if sys.platform == "win32" else 12
        self.defaultTreeFontSize = 12  # 9 if sys.platform == "win32" else 12
    #@+node:ekr.20190831030206.1: *3* c.config.createActivesSettingsOutline (new: #852)
    def createActivesSettingsOutline(self) -> None:
        """
        Create and open an outline, summarizing all presently active settings.

        The outline retains the organization of all active settings files.

        See #852: https://github.com/leo-editor/leo-editor/issues/852
        """
        ActiveSettingsOutline(self.c)
    #@+node:ekr.20190901181116.1: *3* c.config.getSource
    def getSource(self, setting: Setting) -> str:
        """
        Return a string representing the source file of the given setting,
        one of ("local_file", "theme_file", "myLeoSettings", "leoSettings", "ignore", "error")
        """
        if not isinstance(setting, g.GeneralSetting):
            return "error"
        try:
            path = setting.path
        except Exception:
            return "error"
        if not path:
            return "local_file"
        path = path.lower()
        for tag in ('myLeoSettings.leo', 'leoSettings.leo'):
            if path.endswith(tag.lower()):
                return tag[:-4]  # PR: #2422.
        theme_path = g.app.loadManager.theme_path
        if theme_path and g.shortFileName(theme_path.lower()) in path:
            return "theme_file"
        if path == 'register-command' or path.find('mode') > -1:
            return 'ignore'
        return "local_file"
    #@+node:ekr.20120215072959.12471: *3* c.config.Getters
    #@+node:ekr.20041123092357: *4* c.config.findSettingsPosition & helper
    # This was not used prior to Leo 4.5.

    def findSettingsPosition(self, setting: Setting) -> Position:
        """Return the position for the setting in the @settings tree for c."""
        munge = g.app.config.munge
        root = self.settingsRoot()
        if not root:
            return None
        setting = munge(setting)
        for p in root.subtree():
            # BJ munge will return None if a headstring is empty
            h = munge(p.h) or ''
            if h.startswith(setting):
                return p.copy()
        return None
    #@+node:ekr.20041120074536: *5* c.config.settingsRoot
    def settingsRoot(self) -> Position:
        """Return the position of the @settings tree."""
        c = self.c
        for p in c.all_unique_positions():
            # #1792: Allow comments after @settings.
            if g.match_word(p.h.rstrip(), 0, "@settings"):
                return p.copy()
        return None
    #@+node:ekr.20120215072959.12515: *4* c.config.Getters
    #@@nocolor-node
    #@+at Only the following need to be defined.
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
    #     getOutlineData (self)
    #     getOpenWith (self)
    #     getRatio (self,setting)
    #     getShortcut (self,commandName)
    #     getString (self,setting)
    #@+node:ekr.20120215072959.12519: *5* c.config.get & allies
    def get(self, setting: Setting, kind: str) -> Any:
        """Get the setting and make sure its type matches the expected type."""
        d = self.settingsDict
        if d:
            assert isinstance(d, g.SettingsDict), repr(d)
            val, junk = self.getValFromDict(d, setting, kind)
            return val
        return None
    #@+node:ekr.20120215072959.12520: *6* c.config.getValFromDict
    def getValFromDict(self,
        d: Any, setting: str, requestedType: str, warn: bool = True,
    ) -> tuple[Any, bool]:
        """
        Look up the setting in d. If warn is True, warn if the requested type
        does not (loosely) match the actual type.
        returns (val,exists)
        """
        tag = 'c.config.getValFromDict'
        gs = d.get(g.app.config.munge(setting))
        if not gs:
            return None, False
        assert isinstance(gs, g.GeneralSetting), repr(gs)
        val = gs.val
        isNone = val in ('None', 'none', '')
        if not self.typesMatch(gs.kind, requestedType):
            # New in 4.4: make sure the types match.
            # A serious warning: one setting may have destroyed another!
            # Important: this is not a complete test of conflicting settings:
            # The warning is given only if the code tries to access the setting.
            if warn:
                g.error(
                    f"{tag}: ignoring '{setting}' setting.\n"
                    f"{tag}: '@{gs.kind}' is not '@{requestedType}'.\n"
                    f"{tag}: there may be conflicting settings!")
            return None, False
        if isNone:
            return '', True  # 2011/10/24: Exists, a *user-defined* empty value.
        return val, True
    #@+node:ekr.20120215072959.12521: *6* c.config.typesMatch
    def typesMatch(self, type1: str, type2: str) -> bool:
        """
        Return True if type1, the actual type, matches type2, the requested type.

        The following equivalences are allowed:

        - None matches anything.
        - An actual type of string or strings matches anything *except* shortcuts.
        - Shortcut matches shortcuts.
        """
        # The shortcuts logic no longer uses the get/set code.
        shortcuts = ('shortcut', 'shortcuts',)
        if type1 in shortcuts or type2 in shortcuts:
            g.trace('oops: type in shortcuts')
        return (
            type1 is None
            or type2 is None
            or type1.startswith('string') and type2 not in shortcuts
            or type1 == 'language' and type2 == 'string'
            or type1 == 'int' and type2 == 'size'
            or (type1 in shortcuts and type2 in shortcuts)
            or type1 == type2
        )
    #@+node:ekr.20120215072959.12522: *5* c.config.getAbbrevDict
    def getAbbrevDict(self) -> dict[str, Any]:
        """Search all dictionaries for the setting & check it's type"""
        d = self.get('abbrev', 'abbrev')
        return d or {}
    #@+node:ekr.20120215072959.12523: *5* c.config.getBool
    def getBool(self, setting: str, default: bool = None) -> bool:
        """Return the value of @bool setting, or the default if the setting is not found."""
        val = self.get(setting, "bool")
        if val in (True, False):
            return val
        return default
    #@+node:ekr.20120215072959.12525: *5* c.config.getColor
    def getColor(self, setting: str) -> str:
        """Return the value of @color setting."""
        col = self.get(setting, "color")
        while col and col.startswith('@'):
            col = self.get(col[1:], "color")
        return col
    #@+node:ekr.20120215072959.12527: *5* c.config.getData
    def getData(self,
        setting: str,
        strip_comments: bool = True,
        strip_data: bool = True,
    ) -> list[str]:
        """Return a list of non-comment strings in the body text of @data setting."""
        # 904: Add local abbreviations to global settings.
        append = setting == 'global-abbreviations'
        if append:
            data0 = g.app.config.getData(setting,
                strip_comments=strip_comments,
                strip_data=strip_data,
            )
        data = self.get(setting, "data")
        # New in Leo 4.11: parser.doData strips only comments now.
        # New in Leo 4.12: parser.doData strips *nothing*.
        if isinstance(data, str):
            data = [data]
        if data and strip_comments:
            data = [z for z in data if not z.strip().startswith('#')]
        if data and strip_data:
            data = [z.strip() for z in data if z.strip()]
        if append and data != data0:
            if data:
                data.extend(data0)
            else:
                data = data0
        return data
    #@+node:ekr.20131114051702.16542: *5* c.config.getOutlineData
    def getOutlineData(self, setting: str) -> Any:
        """Return the pastable (xml) text of the entire @outline-data tree."""
        data = self.get(setting, "outlinedata")
        if setting == 'tree-abbreviations':
            # 904: Append local tree abbreviations to the global abbreviations.
            data0 = g.app.config.getOutlineData(setting)
            if data and data0 and data != data0:
                assert isinstance(data0, str)
                assert isinstance(data, str)
                # We can't merge the data here: they are .leo files!
                # abbrev.init_tree_abbrev_helper does the merge.
                data = [data0, data]
        return data
    #@+node:ekr.20120215072959.12528: *5* c.config.getDirectory
    def getDirectory(self, setting: str) -> str:
        """Return the value of @directory setting, or None if the directory does not exist."""
        # Fix https://bugs.launchpad.net/leo-editor/+bug/1173763
        theDir = self.get(setting, 'directory')
        if g.os_path_exists(theDir) and g.os_path_isdir(theDir):
            return theDir
        return None
    #@+node:ekr.20120215072959.12530: *5* c.config.getFloat
    def getFloat(self, setting: str) -> float:
        """Return the value of @float setting."""
        val = self.get(setting, "float")
        try:
            val = float(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20120215072959.12531: *5* c.config.getFontFromParams
    def getFontFromParams(self,
        family: str, size: str, slant: str, weight: str, defaultSize: int = 12, tag: str = '',
    ) -> Any:
        """
        Compute a font from font parameters. This should be used *only*
        by the syntax coloring code.  Otherwise, use Leo's style sheets.

        Arguments are the names of settings to be use.
        Default to size=12, slant="roman", weight="normal".

        Return None if there is no family setting so we can use system default fonts.
        """
        family = self.get(family, "family")
        size = self.get(size, "size")
        if size in (None, 0):
            size = str(defaultSize)  # type:ignore
        slant = self.get(slant, "slant")
        if slant in (None, ""):
            slant = "roman"
        weight = self.get(weight, "weight")
        if weight in (None, ""):
            weight = "normal"
        return g.app.gui.getFontFromParams(family, size, slant, weight)
    #@+node:ekr.20120215072959.12532: *5* c.config.getInt
    def getInt(self, setting: str) -> int:
        """Return the value of @int setting."""
        val = self.get(setting, "int")
        try:
            val = int(val)
            return val
        except TypeError:
            return None
    #@+node:ekr.20120215072959.12533: *5* c.config.getLanguage
    def getLanguage(self, setting: str) -> str:
        """Return the setting whose value should be a language known to Leo."""
        language = self.getString(setting)
        return language
    #@+node:ekr.20120215072959.12534: *5* c.config.getMenusList
    def getMenusList(self) -> list:
        """Return the list of entries for the @menus tree."""

        # Typically empty, unless there is an @menuat setting.
        aList = self.get('menus', 'menus')

        # Leo calls this method twice when loading an outline.
        if not hasattr(self.c, 'menulist_pass'):
            self.c.menulist_pass = 0
        self.c.menulist_pass += 1

        # Remove this outline's "doMenuat" settings so later outlines won't use them.
        if self.c.menulist_pass == 2:
            lm = g.app.loadManager
            lm.globalSettingsDict['menus'] = None
            self.set(None, 'menus', 'menus', None)
            self.c.menulist_pass = 0

        return aList or g.app.config.menusList
    #@+node:ekr.20120215072959.12535: *5* c.config.getOpenWith
    def getOpenWith(self) -> list[dict[str, Any]]:
        """Return a list of dictionaries corresponding to @openwith nodes."""
        val = self.get('openwithtable', 'openwithtable')
        return val
    #@+node:ekr.20120215072959.12536: *5* c.config.getRatio
    def getRatio(self, setting: str) -> Optional[float]:
        """
        Return the value of @float setting, or None if there is an error.
        """
        val = self.get(setting, "ratio")
        try:
            val = float(val)
            if 0.0 <= val <= 1.0:
                return val
        except TypeError:
            pass
        return None
    #@+node:ekr.20120215072959.12538: *5* c.config.getSettingSource
    def getSettingSource(self, setting: str) -> tuple[str, Any]:
        """return the name of the file responsible for setting."""
        d = self.settingsDict
        if d:
            assert isinstance(d, g.SettingsDict), repr(d)
            bi = d.get(setting)
            if bi is None:
                return 'unknown setting', None
            return bi.path, bi.val
        #
        # lm.readGlobalSettingsFiles is opening a settings file.
        # lm.readGlobalSettingsFiles has not yet set lm.globalSettingsDict.
        assert d is None
        return None
    #@+node:ekr.20120215072959.12539: *5* c.config.getShortcut
    no_menu_dict: dict[Cmdr, bool] = {}

    def getShortcut(self, commandName: str) -> tuple[str, list]:
        """Return rawKey,accel for shortcutName"""
        c = self.c
        d = self.shortcutsDict
        if not c.frame.menu:
            if c not in self.no_menu_dict:
                self.no_menu_dict[c] = True
                g.trace(f"no menu: {c.shortFileName()}:{commandName}")
            return None, []
        if d:
            assert isinstance(d, g.SettingsDict), repr(d)  # was TypedDictOfLists.
            key = c.frame.menu.canonicalizeMenuName(commandName)
            key = key.replace('&', '')  # Allow '&' in names.
            aList = d.get(commandName, [])
            if aList:  # A list of g.BindingInfo objects.
                # It's important to filter empty strokes here.
                aList = [z for z in aList
                    if z.stroke and z.stroke.lower() != 'none']
            return key, aList
        #
        # lm.readGlobalSettingsFiles is opening a settings file.
        # lm.readGlobalSettingsFiles has not yet set lm.globalSettingsDict.
        return None, []
    #@+node:ekr.20120215072959.12540: *5* c.config.getString
    def getString(self, setting: str) -> str:
        """Return the value of @string setting."""
        return self.get(setting, "string")
    #@+node:ekr.20120215072959.12543: *4* c.config.Getters: redirect to g.app.config
    def getButtons(self) -> list[tuple]:
        """Return a list of tuples (x, y) for common @button nodes."""
        return g.app.config.atCommonButtonsList  # unusual.

    def getCommands(self) -> list[tuple[Position, str]]:
        """Return the list of tuples (headline,script) for common @command nodes."""
        return g.app.config.atCommonCommandsList  # unusual.

    def getEnabledPlugins(self) -> str:
        """Return the body text of the @enabled-plugins node."""
        return g.app.config.enabledPluginsString  # unusual.

    def getRecentFiles(self) -> list[str]:
        """Return the list of recently opened files."""
        return g.app.config.getRecentFiles()  # unusual
    #@+node:ekr.20140114145953.16691: *4* c.config.isLocalSetting
    def isLocalSetting(self, setting: str, kind: str) -> bool:
        """Return True if the indicated setting comes from a local .leo file."""
        if not kind or kind in ('shortcut', 'shortcuts', 'openwithtable'):
            return False
        key = g.app.config.munge(setting)
        if key is None:
            return False
        if not self.settingsDict:
            return False
        gs = self.settingsDict.get(key)
        if not gs:
            return False
        assert isinstance(gs, g.GeneralSetting), repr(gs)
        path = gs.path.lower()
        for fn in ('myLeoSettings.leo', 'leoSettings.leo'):
            if path.endswith(fn.lower()):
                return False
        return True
    #@+node:ekr.20171119222458.1: *4* c.config.isLocalSettingsFile
    def isLocalSettingsFile(self) -> bool:
        """Return true if c is not leoSettings.leo or myLeoSettings.leo"""
        c = self.c
        fn = c.shortFileName().lower()
        for fn2 in ('leoSettings.leo', 'myLeoSettings.leo'):
            if fn.endswith(fn2.lower()):
                return False
        return True
    #@+node:ekr.20120224140548.10528: *4* c.config.exists
    def exists(self, setting: str, kind: str) -> bool:
        """Return true if a setting of the given kind exists, even if it is None."""
        d = self.settingsDict
        if d:
            junk, found = self.getValFromDict(d, setting, kind)
            if found:
                return True
        return False
    #@+node:ekr.20230306104439.1: *3* c.config.printColorSettings
    def printColorSettings(self) -> None:
        """
        Print the value of all @color settings.

        The following shows where the each setting comes from:

        -     leoSettings.leo,
        -  @  @button, @command, @mode.
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,
        - [T] theme .leo file.
        """
        legend = '''\
    legend:
        leoSettings.leo
     @  @button, @command, @mode
    [D] default settings
    [F] loaded .leo File
    [M] myLeoSettings.leo
    [T] theme .leo file.
    '''
        c = self.c
        if g.unitTesting:
            return
        legend = textwrap.dedent(legend)
        result = []
        for name, val, _c, letter in g.app.config.config_iter(c):
            if name.strip().startswith('@color'):
                kind = '   ' if letter == ' ' else f"[{letter}]"
                result.append(f"{kind} {name} = {val}\n")
        # Use a single g.es statement.
        result.append('\n' + legend)
        g.es_print('', ''.join(result), tabName='Settings')
    #@+node:ekr.20230306104456.1: *3* c.config.printFontSettings
    def printFontSettings(self) -> None:
        """
        Print the value of every @font setting.

        The following shows where the each setting comes from:

        -     leoSettings.leo,
        -  @  @button, @command, @mode.
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,
        - [T] theme .leo file.
        """
        legend = '''\
    legend:
        leoSettings.leo
     @  @button, @command, @mode
    [D] default settings
    [F] loaded .leo File
    [M] myLeoSettings.leo
    [T] theme .leo file.
    '''
        c = self.c
        if g.unitTesting:
            return
        legend = textwrap.dedent(legend)
        result = []
        for name, val, _c, letter in g.app.config.config_iter(c):
            #@verbatim
            # @font nodes set @family, @weight, @slant, @size settings.
            if name.strip().startswith(('@font', '@family', '@weight', '@slant', '@size')):
                kind = '   ' if letter == ' ' else f"[{letter}]"
                result.append(f"{kind} {name} = {val}\n")
        # Use a single g.es statement.
        result.append('\n' + legend)
        g.es_print('', ''.join(result), tabName='Settings')
    #@+node:ekr.20070418073400: *3* c.config.printSettings
    def printSettings(self) -> None:
        """
        Print the value of every setting, except key bindings, commands, and
        open-with tables.

        The following shows where the each setting comes from:

        -     leoSettings.leo,
        -  @  @button, @command, @mode.
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,
        - [T] theme .leo file.
        """
        legend = '''\
    legend:
        leoSettings.leo
     @  @button, @command, @mode
    [D] default settings
    [F] loaded .leo File
    [M] myLeoSettings.leo
    [T] theme .leo file.
    '''
        c = self.c
        if g.unitTesting:
            return
        legend = textwrap.dedent(legend)
        result = []
        for name, val, _c, letter in g.app.config.config_iter(c):
            kind = '   ' if letter == ' ' else f"[{letter}]"
            result.append(f"{kind} {name} = {val}\n")
        # Use a single g.es statement.
        result.append('\n' + legend)
        g.es_print('', ''.join(result), tabName='Settings')
    #@+node:ekr.20120215072959.12475: *3* c.config.set
    def set(self, p: Position, kind: str, name: str, val: Any, warn: bool = True) -> None:
        """
        Init the setting for name to val.

        The "p" arg is not used.
        """
        c = self.c
        # Note: when kind is 'shortcut', name is a command name.
        key = g.app.config.munge(name)
        d = self.settingsDict
        assert isinstance(d, g.SettingsDict), repr(d)
        gs = d.get(key)
        if gs:
            assert isinstance(gs, g.GeneralSetting), repr(gs)
            path = gs.path
            if warn and g.finalize(c.mFileName) != g.finalize(path):
                g.trace("over-riding setting:", name, "from", path)
        d[key] = g.GeneralSetting(
            kind,
            path=c.mFileName,
            source=p.h if p else '',
            val=val,
            tag='setting',
        )
    #@+node:ekr.20190905082644.1: *3* c.config.settingIsActiveInPath
    def settingIsActiveInPath(self, gs: str, target_path: str) -> bool:
        """Return True if settings file given by path actually defines the setting, gs."""
        assert isinstance(gs, g.GeneralSetting), repr(gs)
        return gs.path == target_path
    #@+node:ekr.20180121135120.1: *3* c.config.setUserSetting
    def setUserSetting(self, setting: str, value: str) -> None:
        """
        Find and set the indicated setting, either in the local file or in
        myLeoSettings.leo.
        """
        c = self.c
        fn = g.shortFileName(c.fileName())
        p = self.findSettingsPosition(setting)
        if not p:
            c = c.openMyLeoSettings()
            if not c:
                return
            fn = 'myLeoSettings.leo'
            p = c.config.findSettingsPosition(setting)
        if not p:
            root = c.config.settingsRoot()
            if not root:
                return
            fn = 'leoSettings.leo'
            p = c.config.findSettingsPosition(setting)
            if not p:
                p = root.insertAsLastChild()
        h = setting
        i = h.find('=')
        if i > -1:
            h = h[:i].strip()
        p.h = f"{h} = {value}"
        print(f"Updated `{setting}` in {fn}")  # #2390.
        #
        # Delay the second redraw until idle time.
        c.setChanged()
        p.setDirty()
        c.redraw_later()
    #@-others
#@+node:ekr.20041119203941.3: ** class SettingsTreeParser (ParserBaseClass)
class SettingsTreeParser(ParserBaseClass):
    """A class that inits settings found in an @settings tree.

    Used by read settings logic."""

    # def __init__(self, c, localFlag=True):
        # super().__init__(c, localFlag)
    #@+others
    #@+node:ekr.20041119204103: *3* ctor (SettingsTreeParser)
    #@+node:ekr.20041119204714: *3* visitNode (SettingsTreeParser)
    def visitNode(self, p: Position) -> str:
        """Init any settings found in node p."""
        p = p.copy()
        munge = g.app.config.munge
        kind, name, val = self.parseHeadline(p.h)
        kind = munge(kind)
        isNone = val in ('None', 'none', '', None)
        if kind is None:  # Not an @x node. (New in Leo 4.4.4)
            pass
        elif kind == "settings":
            pass
        elif kind in self.basic_types and isNone:
            # None is valid for all basic types.
            self.set(p, kind, name, None)
        elif kind in self.control_types or kind in self.basic_types:
            f = self.dispatchDict.get(kind)
            if f:
                try:
                    # mypy: can not call function of unknown type.
                    return f(p, kind, name, val)  # type:ignore
                except Exception:
                    g.es_exception()
            else:
                g.pr("*** no handler", kind)
        return None
    #@-others
#@+node:ekr.20171229131953.1: ** parseFont (leoConfig.py)
def parseFont(b: str) -> tuple[str, str, bool, bool, float]:
    family = None
    weight = None
    slant = None
    size = None
    settings_name = None
    for line in g.splitLines(b):
        line = line.strip()
        if line.startswith('#'):
            continue
        i = line.find('=')
        if i < 0:
            continue
        name = line[:i].strip()
        if name.endswith('_family'):
            family = line[i + 1 :].strip()
        elif name.endswith('_weight'):
            weight = line[i + 1 :].strip()
        elif name.endswith('_size'):
            size_s = line[i + 1 :].strip()
            try:
                size = float(size_s)
            except ValueError:
                size = 12.0
        elif name.endswith('_slant'):
            slant = line[i + 1 :].strip()
        if settings_name is None and name.endswith(
            ('_family', '_slant', '_weight', '_size')):
            settings_name = name.rsplit('_', 1)[0]
    return settings_name, family, weight == 'bold', slant in ('slant', 'italic'), size
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

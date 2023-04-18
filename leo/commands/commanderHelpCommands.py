#@+leo-ver=5-thin
#@+node:ekr.20171124073126.1: * @file ../commands/commanderHelpCommands.py
"""Help commands that used to be defined in leoCommands.py"""
#@+<< commanderHelpCommands imports & annotations >>
#@+node:ekr.20220826122759.1: ** << commanderHelpCommands imports & annotations >>
from __future__ import annotations
import os
import sys
import time
from typing import Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    Self = Cmdr  # For @g.commander_command
#@-<< commanderHelpCommands imports & annotations >>

#@+others
#@+node:ekr.20031218072017.2939: ** c_help.about (version number & date)
@g.commander_command('about-leo')
def about(self: Self, event: Event = None) -> None:
    """Bring up an About Leo Dialog."""
    c = self
    import datetime
    # Don't use triple-quoted strings or continued strings here.
    # Doing so would add unwanted leading tabs.
    version = g.app.signon + '\n\n'
    theCopyright = (
        "Copyright 1999-%s by Edward K. Ream\n" +
        "All Rights Reserved\n" +
        "Leo is distributed under the MIT License") % datetime.date.today().year
    url = "https://leo-editor.github.io/leo-editor/"
    email = "edreamleo@gmail.com"
    g.app.gui.runAboutLeoDialog(c, version, theCopyright, url, email)
#@+node:vitalije.20170713174950.1: ** c_help.editOneSetting
@g.commander_command('edit-setting')
def editOneSetting(self: Self, event: Event = None) -> None:
    """Opens correct dialog for selected setting type"""
    c, p = self, self.c.p
    func = None
    if p.h.startswith('@font'):
        func = c.commandsDict.get('show-fonts')
    elif p.h.startswith('@color '):
        func = c.commandsDict.get('show-color-wheel')
    elif p.h.startswith(('@shortcuts', '@button', '@command')):
        c.editShortcut()
        return
    else:
        g.es('not in a setting node')
        return
    if func:
        event = g.app.gui.create_key_event(c)
        func(event)
#@+node:vitalije.20170708172746.1: ** c_help.editShortcut
@g.commander_command('edit-shortcut')
def editShortcut(self: Self, event: Event = None) -> None:
    k = self.k
    if k.isEditShortcutSensible():
        # k.setState('input-shortcut', 'input-shortcut')
        k.setState('input-shortcut', 1, None)  # Experimental.
        g.es('Press desired key combination')
    else:
        g.es('No possible shortcut in selected body line/headline')
        g.es('Select @button, @command, @shortcuts or @mode node and run it again.')
#@+node:ekr.20171124093409.1: ** c_help.Open Leo files
#@+node:ekr.20031218072017.2940: *3* c_help.leoDocumentation
@g.commander_command('open-leo-docs-leo')
@g.commander_command('leo-docs-leo')
def leoDocumentation(self: Self, event: Event = None) -> None:
    """Open LeoDocs.leo in a new Leo window."""
    c = self
    name = "LeoDocs.leo"
    fileName = g.finalize_join(g.app.loadDir, "..", "doc", name)
    if g.os_path_exists(fileName):
        c2 = g.openWithFileName(fileName, old_c=c)
        if c2:
            return
    g.es("not found:", name)
#@+node:ekr.20090628075121.5994: *3* c_help.leoQuickStart
@g.commander_command('open-quickstart-leo')
@g.commander_command('leo-quickstart-leo')
def leoQuickStart(self: Self, event: Event = None) -> None:
    """Open quickstart.leo in a new Leo window."""
    c = self
    name = "quickstart.leo"
    fileName = g.finalize_join(g.app.loadDir, "..", "doc", name)
    if g.os_path_exists(fileName):
        c2 = g.openWithFileName(fileName, old_c=c)
        if c2:
            return
    g.es("not found:", name)
#@+node:ekr.20131028155339.17096: *3* c_help.openCheatSheet
@g.commander_command('open-cheat-sheet-leo')
@g.commander_command('leo-cheat-sheet')
@g.commander_command('cheat-sheet')
def openCheatSheet(self: Self, event: Event = None) -> None:
    """Open leo/doc/cheatSheet.leo"""
    c = self
    fn = g.finalize_join(g.app.loadDir, '..', 'doc', 'CheatSheet.leo')
    if not g.os_path_exists(fn):
        g.es(f"file not found: {fn}")
        return
    c2 = g.openWithFileName(fn, old_c=c)
    p = g.findNodeAnywhere(c2, "Leo's cheat sheet")
    if p:
        c2.selectPosition(p)
        p.expand()
    c2.redraw()
#@+node:lkj.20190714022527.1: *3* c_help.openDesktopIntegration
@g.commander_command('open-desktop-integration-leo')
@g.commander_command('desktop-integration-leo')
def openDesktopIntegration(self: Self, event: Event = None) -> None:
    """Open Desktop-integration.leo."""
    c = self
    fileName = g.finalize_join(g.app.loadDir, '..', 'scripts', 'desktop-integration.leo')
    if g.os_path_exists(fileName):
        c2 = g.openWithFileName(fileName, old_c=c)
        if c2:
            return
    g.es('not found:', fileName)
#@+node:ekr.20161025090405.1: *3* c_help.openLeoDist
@g.commander_command('open-leo-dist-leo')
@g.commander_command('leo-dist-leo')
def openLeoDist(self: Self, event: Event = None) -> None:
    """Open leoDist.leo in a new Leo window."""
    c = self
    name = "leoDist.leo"
    fileName = g.finalize_join(g.app.loadDir, "..", "dist", name)
    if g.os_path_exists(fileName):
        c2 = g.openWithFileName(fileName, old_c=c)
        if c2:
            return
    g.es("not found:", name)
#@+node:ekr.20151225193723.1: *3* c_help.openLeoPy
@g.commander_command('open-leo-py-leo')
@g.commander_command('leo-py-leo')
def openLeoPy(self: Self, event: Event = None) -> None:
    """Open leoPy.leo or LeoPyRef.leo in a new Leo window."""
    c = self
    names = ('leoPy.leo', 'LeoPyRef.leo',)  # Used in error message.
    for name in names:
        fileName = g.finalize_join(g.app.loadDir, "..", "core", name)
        # Only call g.openWithFileName if the file exists.
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName, old_c=c)
            if c2:
                return
    g.es('not found:', ', '.join(names))
#@+node:ekr.20201013105418.1: *3* c_help.openLeoPyRef
@g.commander_command('open-leo-py-ref-leo')
@g.commander_command('leo-py-ref-leo')
def openLeoPyRef(self: Self, event: Event = None) -> None:
    """Open leoPyRef.leo in a new Leo window."""
    c = self
    path = g.finalize_join(g.app.loadDir, "..", "core", "LeoPyRef.leo")
    if g.os_path_exists(path):
        c2 = g.openWithFileName(path, old_c=c)
        if c2:
            return
    g.es('LeoPyRef.leo not found')
#@+node:ekr.20061018094539: *3* c_help.openLeoScripts
@g.commander_command('open-scripts-leo')
@g.commander_command('leo-scripts-leo')
def openLeoScripts(self: Self, event: Event = None) -> None:
    """Open scripts.leo."""
    c = self
    fileName = g.finalize_join(g.app.loadDir, '..', 'scripts', 'scripts.leo')
    if g.os_path_exists(fileName):
        c2 = g.openWithFileName(fileName, old_c=c)
        if c2:
            return
    g.es('not found:', fileName)
#@+node:ekr.20031218072017.2943: *3* c_help.openLeoSettings & openMyLeoSettings & helper
@g.commander_command('open-leo-settings')
@g.commander_command('open-leo-settings-leo')  # #1343.
@g.commander_command('leo-settings')
def openLeoSettings(self: Self, event: Event = None) -> Optional[Cmdr]:
    """Open leoSettings.leo in a new Leo window."""
    c, lm = self, g.app.loadManager
    path = lm.computeLeoSettingsPath()
    if path:
        return g.openWithFileName(path, old_c=c)
    g.es('not found: leoSettings.leo')
    return None

@g.commander_command('open-my-leo-settings')
@g.commander_command('open-my-leo-settings-leo')  # #1343.
@g.commander_command('my-leo-settings')
def openMyLeoSettings(self: Self, event: Event = None) -> Cmdr:
    """Open myLeoSettings.leo in a new Leo window."""
    c, lm = self, g.app.loadManager
    path = lm.computeMyLeoSettingsPath()
    if path:
        return g.openWithFileName(path, old_c=c)
    g.es('not found: myLeoSettings.leo')
    return createMyLeoSettings(c)
#@+node:ekr.20141119161908.2: *4* function: c_help.createMyLeoSettings
def createMyLeoSettings(c: Cmdr) -> Optional[Cmdr]:
    """createMyLeoSettings - Return true if myLeoSettings.leo created ok
    """
    name = "myLeoSettings.leo"
    homeLeoDir = g.app.homeLeoDir
    loadDir = g.app.loadDir
    configDir = g.app.globalConfigDir
    # check it doesn't already exist
    for path in homeLeoDir, loadDir, configDir:
        fileName = g.os_path_join(path, name)
        if g.os_path_exists(fileName):
            return None
    ok = g.app.gui.runAskYesNoDialog(c,
        title='Create myLeoSettings.leo?',
        message=f"Create myLeoSettings.leo in {homeLeoDir}?",
    )
    if ok == 'no':
        return None
    # get '@enabled-plugins' from g.app.globalConfigDir
    fileName = g.os_path_join(configDir, "leoSettings.leo")
    leosettings = g.openWithFileName(fileName, old_c=c)
    enabledplugins = g.findNodeAnywhere(leosettings, '@enabled-plugins')
    if not enabledplugins:
        return None
    enabledplugins = enabledplugins.b
    leosettings.close()
    # now create "~/.leo/myLeoSettings.leo"
    fileName = g.os_path_join(homeLeoDir, name)
    c2 = g.openWithFileName(fileName, old_c=c)
    # add content to outline
    nd = c2.rootPosition()
    nd.h = "Settings README"
    nd.b = (
        "myLeoSettings.leo personal settings file created {time}\n\n"
        "Only nodes that are descendants of the @settings node are read.\n\n"
        "Only settings you need to modify should be in this file, do\n"
        "not copy large parts of leoSettings.py here.\n\n"
        "For more information see https://leo-editor.github.io/leo-editor/customizing.html"
        "".format(time=time.asctime())
    )
    nd = nd.insertAfter()
    nd.h = '@settings'
    nd = nd.insertAsNthChild(0)
    nd.h = '@enabled-plugins'
    nd.b = enabledplugins
    nd = nd.insertAfter()
    nd.h = '@keys'
    nd = nd.insertAsNthChild(0)
    nd.h = '@shortcuts'
    nd.b = (
        "# You can define keyboard shortcuts here of the form:\n"
        "#\n"
        "#    some-command Shift-F5\n"
    )
    c2.redraw()
    return c2
#@+node:ekr.20171124093507.1: ** c_help.Open Leo web pages
#@+node:ekr.20031218072017.2941: *3* c_help.leoHome
@g.commander_command('open-online-home')
def leoHome(self: Self, event: Event = None) -> None:
    """Open Leo's Home page in a web browser."""
    import webbrowser
    url = "https://leo-editor.github.io/leo-editor/"
    try:
        webbrowser.open_new(url)
    except Exception:
        g.es("not found:", url)
#@+node:ekr.20131213072223.19441: *3* c_help.openLeoTOC
@g.commander_command('open-online-toc')
def openLeoTOC(self: Self, event: Event = None) -> None:
    """Open Leo's tutorials page in a web browser."""
    import webbrowser
    url = "https://leo-editor.github.io/leo-editor/leo_toc.html"
    try:
        webbrowser.open_new(url)
    except Exception:
        g.es("not found:", url)
#@+node:ekr.20230104130712.1: *3* c_help.openLeoScriptingMiscellany
@g.commander_command('open-online-scripting-miscellany')
def openLeoScriptingMiscellany(self: Self, event: Event = None) -> None:
    """Open Leo's scripting miscellany page in a web browser."""
    import webbrowser
    url = "https://leo-editor.github.io/leo-editor/scripting-miscellany.html"
    try:
        webbrowser.open_new(url)
    except Exception:
        g.es("not found:", url)
#@+node:ekr.20131213072223.19435: *3* c_help.openLeoTutorials
@g.commander_command('open-online-tutorials')
def openLeoTutorials(self: Self, event: Event = None) -> None:
    """Open Leo's tutorials page in a web browser."""
    import webbrowser
    url = "https://leo-editor.github.io/leo-editor/tutorial.html"
    try:
        webbrowser.open_new(url)
    except Exception:
        g.es("not found:", url)
#@+node:ekr.20060613082924: *3* c_help.openLeoUsersGuide
@g.commander_command('open-users-guide')
def openLeoUsersGuide(self: Self, event: Event = None) -> None:
    """Open Leo's users guide in a web browser."""
    import webbrowser
    url = "https://leo-editor.github.io/leo-editor/usersguide.html"
    try:
        webbrowser.open_new(url)
    except Exception:
        g.es("not found:", url)
#@+node:ekr.20131213072223.19437: *3* c_help.openLeoVideos
@g.commander_command('open-online-videos')
def openLeoVideos(self: Self, event: Event = None) -> None:
    """Open Leo's videos page in a web browser."""
    import webbrowser
    url = "https://leo-editor.github.io/leo-editor/screencasts.html"
    try:
        webbrowser.open_new(url)
    except Exception:
        g.es("not found:", url)
#@+node:ekr.20031218072017.2932: ** c_help.openPythonWindow
@g.commander_command('open-python-window')
def openPythonWindow(self: Self, event: Event = None) -> None:
    """Open Python's Idle debugger in a separate process."""
    m = g.import_module('idlelib')
    if not m:
        g.trace('can not open idlelib')
        return
    idle_path = os.path.dirname(m.__file__)
    idle = g.os_path_join(idle_path, 'idle.py')
    args = [sys.executable, idle]
    if 1:  # Use present environment.
        os.spawnv(os.P_NOWAIT, sys.executable, args)
    else:  # Use a pristine environment.
        os.spawnve(os.P_NOWAIT, sys.executable, args, os.environ)
#@+node:ekr.20131213072223.19532: ** c_help.selectAtSettingsNode
@g.commander_command('open-local-settings')
def selectAtSettingsNode(self: Self, event: Event = None) -> None:
    """Select the @settings node, if there is one."""
    c = self
    p = c.config.settingsRoot()
    if p:
        c.selectPosition(p)
        c.redraw()
    else:
        g.es('no local @settings tree.')
#@-others
#@-leo

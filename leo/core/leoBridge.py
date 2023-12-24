#! /usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20070227091955.1: * @file leoBridge.py
#@@first
"""A module to allow full access to Leo commanders from outside Leo."""
#@@language python
#@@tabwidth -4
#@+<< about the leoBridge module >>
#@+node:ekr.20070227091955.2: ** << about the leoBridge module >>
#@@language rest
#@+at
# A **host** program is a Python program separate from Leo. Host programs may
# be created by Leo, but at the time they are run host programs must not be
# part of Leo in any way. So if they are run from Leo, they must be run in a
# separate process.
#
# The leoBridge module gives host programs access to all aspects of Leo,
# including all of Leo's source code, the contents of any .leo file, all
# configuration settings in .leo files, etc.
#
# Host programs will use the leoBridge module like this::
#
#     from leo.core import leoBridge
#     bridge = leoBridge.controller(gui='nullGui',verbose=False)
#     if bridge.isOpen():
#         g = bridge.globals()
#         c = bridge.openLeoFile(path)
#
# Notes:
#
# - The leoBridge module imports no modules at the top level.
#
# - leoBridge.controller creates a singleton *bridge controller* that grants
#   access to Leo's objects, including fully initialized g and c objects. In
#   particular, the g.app and g.app.gui vars are fully initialized.
#
# - By default, leoBridge.controller creates a null gui so that no Leo
#   windows appear on the screen.
#
# - As shown above, the host program should gain access to Leo's leoGlobals
#   module using bridge.globals(). The host program should not import
#   leo.core.leoGlobals as leoGlobals directly.
#
# - bridge.openLeoFile(path) returns a completely standard Leo commander.
#   Host programs can use these commanders as described in Leo's scripting
#   chapter.
#@-<< about the leoBridge module >>
#@+<< leoBridge imports & annotations >>
#@+node:ekr.20220901084154.1: ** << leoBridge imports & annotations >>
# This module must import *no* Leo modules at the outer level!
from __future__ import annotations
import os
import sys
import traceback
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
#@-<< leoBridge imports & annotations >>

gBridgeController = None  # The singleton bridge controller.
#@+others
#@+node:ekr.20070227092442: ** function: controller
def controller(
    gui: str = 'nullGui',
    loadPlugins: bool = True,
    readSettings: bool = True,
    silent: bool = False,
    tracePlugins: bool = False,
    useCaches: bool = True,
    verbose: bool = False,
) -> Any:
    """Create an singleton instance of a bridge controller."""
    global gBridgeController
    if not gBridgeController:
        gBridgeController = BridgeController(
            gui,
            loadPlugins,
            readSettings,
            silent,
            tracePlugins,
            useCaches,
            verbose)
    return gBridgeController
#@+node:ekr.20070227092442.2: ** class BridgeController
class BridgeController:
    """Creates a way for host programs to access Leo."""
    #@+others
    #@+node:ekr.20070227092442.3: *3* bridge.ctor
    def __init__(
        self,
        guiName: str,
        loadPlugins: bool,
        readSettings: bool,
        silent: bool,
        tracePlugins: bool,
        useCaches: bool,
        verbose: bool,
        vs_code_flag: bool = False,  # #2098.
    ) -> None:
        """Ctor for the BridgeController class."""
        self.g: Any = None  # leo.core.leoGlobals.  Hard to annotate.
        self.guiName = guiName or 'nullGui'
        self.loadPlugins = loadPlugins
        self.readSettings = readSettings
        self.silentMode = silent
        self.tracePlugins = tracePlugins
        self.useCaches = useCaches
        self.verbose = verbose
        self.vs_code_flag = vs_code_flag  # #2098
        self.mainLoop = False  # True only if a non-null-gui mainloop is active.
        self.initLeo()
    #@+node:ekr.20070227092442.4: *3* bridge.globals
    def globals(self) -> Any:
        """Return a fully initialized leoGlobals module."""
        return self.isOpen() and self.g
    #@+node:ekr.20070227093530: *3* bridge.initLeo & helpers
    def initLeo(self) -> None:
        """
        Init the Leo app to which this class gives access.
        This code is based on leo.run().
        """
        if not self.isValidPython():
            return
        #@+<< initLeo imports >>
        #@+node:ekr.20070227093629.1: *4* << initLeo imports >> initLeo (leoBridge)
        try:
            # #1472: Simplify import of g
            from leo.core import leoGlobals as g
            self.g = g
        except ImportError:
            print("Error importing leoGlobals.py")
        #
        # Create the application object.
        try:
            # Tell leoApp.createDefaultGui not to create a gui.
            # This module will create the gui later.
            g.in_bridge = self.vs_code_flag  # #2098.
            g.in_vs_code = True  # 2098.
            from leo.core import leoApp
            g.app = leoApp.LeoApp()
        except ImportError:
            print("Error importing leoApp.py")
        g.app.leoID = None
        if self.tracePlugins:
            g.app.debug.append('plugins')
        g.app.silentMode = self.silentMode
        #
        # Create the g.app.pluginsController here.
        from leo.core import leoPlugins
        leoPlugins.init()  # Necessary. Sets g.app.pluginsController.
        try:
            from leo.core import leoNodes
        except ImportError:
            print("Error importing leoNodes.py")
            traceback.print_exc()
        try:
            from leo.core import leoConfig
        except ImportError:
            print("Error importing leoConfig.py")
            traceback.print_exc()
        #@-<< initLeo imports >>
        g.app.recentFilesManager = leoApp.RecentFilesManager()
        g.app.loadManager = lm = leoApp.LoadManager()
        lm.computeStandardDirectories()
        # #2519: Call sys.exit if leoID does not exist.
        g.app.setLeoID(useDialog=False, verbose=True)
        # Can be done early. Uses only g.app.loadDir & g.app.homeDir.
        lm.createAllImporterData()  # #1965.
        g.app.inBridge = True  # Support for g.getScript.
        g.app.nodeIndices = leoNodes.NodeIndices(g.app.leoID)
        g.app.config = leoConfig.GlobalConfigManager()
        if self.useCaches:
            g.app.setGlobalDb()  # #556.
        else:
            g.app.db = g.NullObject()
            g.app.global_cacher = g.NullObject()
        if self.readSettings:
            # reads only standard settings files, using a null gui.
            # uses lm.files[0] to compute the local directory
            # that might contain myLeoSettings.leo.
            lm.readGlobalSettingsFiles()
        else:
            # Bug fix: 2012/11/26: create default global settings dicts.
            settings_d, bindings_d = lm.createDefaultSettingsDicts()
            lm.globalSettingsDict = settings_d
            lm.globalBindingsDict = bindings_d
        self.createGui()  # Create the gui *before* loading plugins.
        if self.verbose:
            self.reportDirectories()
        self.adjustSysPath()
        # Kill all event handling if plugins not loaded.
        if not self.loadPlugins:

            def dummyDoHook(tag: str, *args: Any, **keys: Any) -> None:
                pass

            g.doHook = dummyDoHook
        g.doHook("start1")  # Load plugins.
        g.app.computeSignon()
        g.app.initing = False
        g.doHook("start2", c=None, p=None, v=None, fileName=None)
    #@+node:ekr.20070302061713: *4* bridge.adjustSysPath
    def adjustSysPath(self) -> None:
        """Adjust sys.path to enable imports as usual with Leo."""
        g = self.g
        leoDirs = (  # 2008/7/30
            'config', 'doc', 'extensions', 'modes', 'plugins', 'core', 'test'
        )
        for theDir in leoDirs:
            path = os.path.normpath(os.path.join(g.app.loadDir, '..', theDir))
            if path not in sys.path:
                sys.path.insert(0, path)

        # #258: leoBridge does not work with @auto-md subtrees.
        for theDir in ('importers', 'writers'):
            path = os.path.normpath(os.path.join(g.app.loadDir, '..', 'plugins', theDir))
            if path not in sys.path:
                sys.path.insert(0, path)
    #@+node:ekr.20070227095743: *4* bridge.createGui
    def createGui(self) -> None:
        g = self.g
        if self.guiName == 'nullGui':
            g.app.gui = g.app.nullGui
            g.app.log = g.app.gui.log = log = g.app.nullLog
            log.isNull = False
            log.enabled = True  # Allow prints from NullLog.
            log.logInited = True  # Bug fix: 2012/10/17.
        else:
            assert False, f"leoBridge.py: unsupported gui: {self.guiName}"  # noqa
    #@+node:ekr.20070227093629.4: *4* bridge.isValidPython
    def isValidPython(self) -> bool:
        if sys.platform == 'cli':
            return True
        tag = 'leoBridge: isValidPython'
        try:
            # This will fail if True/False are not defined.
            from leo.core import leoGlobals as g

            # Set leoGlobals.g here, rather than in leoGlobals.py.
            leoGlobals = g
            leoGlobals.g = g
        except Exception as e:
            print(f"{tag}: can not import leoGlobals: {e}")
            return False

        message = (
            f"Leo requires Python {g.minimum_python_version} or higher"
            "You may download Python from http://python.org/download/"
        )

        try:
            if not g.isValidPython:
                print(message)
                g.app.gui.runAskOkDialog(
                    None, "Python version error", message=message, text="Exit")
            return g.isValidPython
        except Exception as e:
            print(f"{tag}: unexpected exception: {e}")
            return False
    #@+node:ekr.20070227093629.9: *4* bridge.reportDirectories
    def reportDirectories(self) -> None:
        if not self.silentMode:
            g = self.g
            for kind, theDir in (
                ("global config", g.app.globalConfigDir),
                ("home", g.app.homeDir),
            ):
                g.blue('', kind, 'directory', '', ':', theDir)
    #@+node:ekr.20070227093918: *3* bridge.isOpen
    def isOpen(self) -> bool:
        """Return True if the bridge is open."""
        g = self.g
        return bool(g and g.app and g.app.gui)
    #@+node:ekr.20070227092442.5: *3* bridge.openLeoFile & helpers
    def openLeoFile(self, fileName: str) -> Optional[Cmdr]:
        """Open a .leo file, or create a new Leo frame if no fileName is given."""
        g = self.g
        g.app.silentMode = self.silentMode
        useLog = False
        if not self.isOpen():
            return None
        if self.useCaches:
            self.reopen_cachers()
        else:
            g.app.db = g.NullObject()
        fileName = self.completeFileName(fileName)
        c = g.openWithFileName(fileName)  # #2489.
        # Leo 6.3: support leoInteg.
        g.app.windowList.append(c.frame)
        if not self.useCaches:
            c.db = g.NullObject()
        # New in Leo 5.1. An alternate fix for bug #130.
        # When using a bridge Leo might open a file, modify it,
        # close it, reopen it and change it all within one second.
        # In that case, this code must properly compute the next
        # available gnx by scanning the entire outline.
        g.app.nodeIndices.compute_last_index(c)
        if useLog:
            g.app.gui.log = log = c.frame.log
            log.isNull = False
            log.enabled = True
        return c
    #@+node:ekr.20070227093629.5: *4* bridge.completeFileName
    def completeFileName(self, fileName: str) -> str:
        g = self.g
        if not (fileName and fileName.strip()):
            return ''
        fileName = g.finalize_join(os.getcwd(), fileName)
        head, ext = g.os_path_splitext(fileName)
        if not ext:
            fileName = fileName + ".leo"
        return fileName
    #@+node:vitalije.20190923081235.1: *4* bridge.reopen_cachers
    def reopen_cachers(self) -> None:
        from leo.core import leoCache
        g = self.g
        try:
            g.app.db.get('dummy')
        except Exception:
            g.app.global_cacher = leoCache.GlobalCacher()
            g.app.db = g.app.global_cacher.db
    #@-others
#@-others
#@-leo

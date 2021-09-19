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
gBridgeController = None  # The singleton bridge controller.
# This module must import *no* modules at the outer level!
#@+others
#@+node:ekr.20070227092442: ** controller
def controller(
    gui='nullGui',
    loadPlugins=True,
    readSettings=True,
    silent=False,
    tracePlugins=False,
    useCaches=True,
    verbose=False
):
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
    def __init__(self,
        guiName, loadPlugins, readSettings, silent, tracePlugins, useCaches, verbose,
        vs_code_flag=False,  # #2098.
    ):
        """Ctor for the BridgeController class."""
        self.g = None
        self.gui = None
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
    def globals(self):
        """Return a fully initialized leoGlobals module."""
        return self.isOpen() and self.g
    #@+node:ekr.20070227093530: *3* bridge.initLeo & helpers
    def initLeo(self):
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
            g.in_bridge = self.vs_code_flag  # #2098.
                # Tell leoApp.createDefaultGui not to create a gui.
                # This module will create the gui later.
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
            import traceback; traceback.print_exc()
        try:
            from leo.core import leoConfig
        except ImportError:
            print("Error importing leoConfig.py")
            import traceback; traceback.print_exc()
        #@-<< initLeo imports >>
        g.app.recentFilesManager = leoApp.RecentFilesManager()
        g.app.loadManager = lm = leoApp.LoadManager()
        lm.computeStandardDirectories()
        if not g.app.setLeoID(useDialog=False, verbose=True):
            raise ValueError("unable to set LeoID.")
        lm.createAllImporterData()  # #1965.
            # Can be done early. Uses only g.app.loadDir & g.app.homeDir.
        g.app.inBridge = True  # Support for g.getScript.
        g.app.nodeIndices = leoNodes.NodeIndices(g.app.leoID)
        g.app.config = leoConfig.GlobalConfigManager()
        if self.useCaches:
            g.app.setGlobalDb()  # #556.
        else:
            g.app.db = g.NullObject()
            g.app.commander_cacher = g.NullObject()
            g.app.global_cacher = g.NullObject()
        if self.readSettings:
            lm.readGlobalSettingsFiles()
                # reads only standard settings files, using a null gui.
                # uses lm.files[0] to compute the local directory
                # that might contain myLeoSettings.leo.
        else:
            # Bug fix: 2012/11/26: create default global settings dicts.
            settings_d, bindings_d = lm.createDefaultSettingsDicts()
            lm.globalSettingsDict = settings_d
            lm.globalBindingsDict = bindings_d
        self.createGui()  # Create the gui *before* loading plugins.
        if self.verbose: self.reportDirectories()
        self.adjustSysPath()
        # Kill all event handling if plugins not loaded.
        if not self.loadPlugins:

            def dummyDoHook(tag, *args, **keys):
                pass

            g.doHook = dummyDoHook
        g.doHook("start1")  # Load plugins.
        g.app.computeSignon()
        g.app.initing = False
        g.doHook("start2", c=None, p=None, v=None, fileName=None)
    #@+node:ekr.20070302061713: *4* bridge.adjustSysPath
    def adjustSysPath(self):
        """Adjust sys.path to enable imports as usual with Leo."""
        import sys
        g = self.g
        leoDirs = (
            'config', 'doc', 'extensions', 'modes', 'plugins', 'core', 'test')  # 2008/7/30
        for theDir in leoDirs:
            path = g.os_path_finalize_join(g.app.loadDir, '..', theDir)
            if path not in sys.path:
                sys.path.append(path)
        # #258: leoBridge does not work with @auto-md subtrees.
        for theDir in ('importers', 'writers'):
            path = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins', theDir)
            if path not in sys.path:
                sys.path.append(path)
    #@+node:ekr.20070227095743: *4* bridge.createGui
    def createGui(self):
        g = self.g
        if self.guiName == 'nullGui':
            g.app.gui = g.app.nullGui
            g.app.log = g.app.gui.log = log = g.app.nullLog
            log.isNull = False
            log.enabled = True  # Allow prints from NullLog.
            log.logInited = True  # Bug fix: 2012/10/17.
        else:
            assert False, f"leoBridge.py: unsupported gui: {self.guiName}"
    #@+node:ekr.20070227093629.4: *4* bridge.isValidPython
    def isValidPython(self):
        import sys
        if sys.platform == 'cli':
            return True
        message = """\
    Leo requires Python 3.6 or higher.
    You may download Python from http://python.org/download/
    """
        try:
            # This will fail if True/False are not defined.
            from leo.core import leoGlobals as g
            # print('leoBridge:isValidPython:g',g)
            # Set leoGlobals.g here, rather than in leoGlobals.py.
            leoGlobals = g  # Don't set g.g, it would pollute the autocompleter.
            leoGlobals.g = g
        except ImportError:
            print("isValidPython: can not import leoGlobals")
            return 0
        except Exception:
            print(
                "isValidPytyhon: unexpected exception importing leoGlobals")
            import traceback; traceback.print_exc()
            return 0
        try:
            version = '.'.join([str(sys.version_info[i]) for i in (0, 1, 2)])
            ok = g.CheckVersion(version, '2.2.1')
            if not ok:
                print(message)
                g.app.gui.runAskOkDialog(
                    None, "Python version error", message=message, text="Exit")
            return ok
        except Exception:
            print("isValidPython: unexpected exception: g.CheckVersion")
            import traceback; traceback.print_exc()
            return 0
    #@+node:ekr.20070227093629.9: *4* bridge.reportDirectories
    def reportDirectories(self):
        if not self.silentMode:
            g = self.g
            for kind, theDir in (
                ("global config", g.app.globalConfigDir),
                ("home", g.app.homeDir),
            ):
                g.blue('', kind, 'directory', '', ':', theDir)
    #@+node:ekr.20070227093918: *3* bridge.isOpen
    def isOpen(self):
        """Return True if the bridge is open."""
        g = self.g
        return bool(g and g.app and g.app.gui)
    #@+node:ekr.20070227092442.5: *3* bridge.openLeoFile & helpers
    def openLeoFile(self, fileName):
        """Open a .leo file, or create a new Leo frame if no fileName is given."""
        g = self.g
        g.app.silentMode = self.silentMode
        useLog = False
        if self.isOpen():
            if self.useCaches:
                self.reopen_cachers()
            else:
                g.app.db = g.NullObject()
                    # g.TracingNullObject(tag='g.app.db')
            fileName = self.completeFileName(fileName)
            c = self.createFrame(fileName)
            # Leo 6.3: support leoInteg.
            g.app.windowList.append(c.frame)
            if not self.useCaches:
                c.db = g.NullObject()
                    # g.TracingNullObject(tag='c.db')
            g.app.nodeIndices.compute_last_index(c)
                # New in Leo 5.1. An alternate fix for bug #130.
                # When using a bridge Leo might open a file, modify it,
                # close it, reopen it and change it all within one second.
                # In that case, this code must properly compute the next
                # available gnx by scanning the entire outline.
            if useLog:
                g.app.gui.log = log = c.frame.log
                log.isNull = False
                log.enabled = True
            return c
        return None
    #@+node:ekr.20070227093629.5: *4* bridge.completeFileName
    def completeFileName(self, fileName):
        g = self.g
        if not (fileName and fileName.strip()): return ''
        import os
        fileName = g.os_path_finalize_join(os.getcwd(), fileName)
        head, ext = g.os_path_splitext(fileName)
        if not ext: fileName = fileName + ".leo"
        return fileName
    #@+node:ekr.20070227093629.6: *4* bridge.createFrame
    def createFrame(self, fileName):
        """Create a commander and frame for the given file.
        Create a new frame if the fileName is empty or non-exisent."""
        g = self.g
        if fileName.strip():
            if g.os_path_exists(fileName):
                # This takes a long time due to imports in c.__init__
                c = g.openWithFileName(fileName)
                if c:
                    return c
            elif not self.silentMode:
                print(f"file not found: {fileName}. creating new outline")
        # Create a new frame. Unlike leo.run, this is not a startup window.
        c = g.app.newCommander(fileName)
        frame = c.frame
        frame.createFirstTreeNode()  # 2013/09/27: bug fix.
        assert c.rootPosition()
        frame.setInitialWindowGeometry()
        frame.resizePanesToRatio(frame.ratio, frame.secondary_ratio)
        # Call the 'new' hook for compatibility with plugins.
        # 2011/11/07: Do this only if plugins have been loaded.
        g.doHook("new", old_c=None, c=c, new_c=c)
        return c
    #@+node:vitalije.20190923081235.1: *4* reopen_cachers
    def reopen_cachers(self):
        from leo.core import leoCache

        g = self.g
        try:
            g.app.db.get('dummy')
        except Exception:
            g.app.global_cacher = leoCache.GlobalCacher()
            g.app.db = g.app.global_cacher.db
            g.app.commander_cacher = leoCache.CommanderCacher()
            g.app.commander_db = g.app.commander_cacher.db
    #@-others
#@-others
#@-leo

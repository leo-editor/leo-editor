#! /usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20070227091955.1: * @file leoBridge.py
#@@first

'''A module to allow full access to Leo commanders from outside Leo.'''

#@@language python
#@@tabwidth -4

#@+<< about the leoBridge module >>
#@+node:ekr.20070227091955.2: ** << about the leoBridge module >>
#@@nocolor
#@+at
# 
# A **host** program is a Python program separate from Leo. Host programs may be
# created by Leo, but at the time they are run host programs are not part of Leo in
# any way. The leoBridge module gives host programs access to all aspects of Leo,
# including all of Leo's source code, the contents of any .leo file, all
# configuration settings in .leo files, etc.
# 
# Host programs will use the leoBridge module like this::
#     import leo.core.leoBridge as leoBridge
#     bridge = leoBridge.controller(gui='nullGui',verbose=False)
#     if bridge.isOpen():
#         g = bridge.globals()
#         c = bridge.openLeoFile(path)
# Notes:
# 
# - The leoBridge module imports no modules at the top level.
# 
# - leoBridge.controller creates a singleton *bridge controller* that grants
# access to Leo's objects, including fully initialized g and c objects. In
# particular, the g.app and g.app.gui vars are fully initialized.
# 
# - By default, leoBridge.controller creates a null gui so that no Leo windows
# appear on the screen.
# 
# - As shown above, the host program should gain access to Leo's leoGlobals module
# using bridge.globals(). The host program should not import leo.core.leoGlobals as leoGlobals directly.
# 
# - bridge.openLeoFile(path) returns a completely standard Leo commander. Host
# programs can use these commanders as described in Leo's scripting chapter.
#@-<< about the leoBridge module >>

gBridgeController = None # The singleton bridge controller.

# This module must import *no* modules at the outer level!

#@+others
#@+node:ekr.20070227092442: ** controller
def controller(gui='nullGui',loadPlugins=True,readSettings=True,silent=False,verbose=False):

    '''Create an singleton instance of a bridge controller.'''

    global gBridgeController

    if not gBridgeController:
        gBridgeController = bridgeController(gui,loadPlugins,readSettings,silent,verbose)

    return gBridgeController
#@+node:ekr.20070227092442.2: ** class bridgeController
class bridgeController:

    '''Creates a way for host programs to access Leo.'''

    #@+others
    #@+node:ekr.20070227092442.3: *3* ctor (bridgeController)
    def __init__ (self,guiName,loadPlugins,readSettings,silent,verbose):

        self.g = None
        self.gui = None
        self.guiName = guiName or 'nullGui'
        self.loadPlugins = loadPlugins
        self.readSettings = readSettings
        self.silent = silent
        self.verbose = verbose

        self.mainLoop = False # True only if a non-null-gui mainloop is active.

        self.initLeo()
    #@+node:ekr.20070227092442.4: *3* globals
    def globals (self):

        '''Return a fully initialized leoGlobals module.'''

        return self.isOpen() and self.g
    #@+node:ekr.20070227093530: *3* initLeo & helpers (bridgeController)
    def initLeo (self):

        '''Init the Leo app to which this class gives access.
        This code is based on leo.run().'''

        trace = False
        if not self.isValidPython(): return
        #@+<< initLeo imports >>
        #@+node:ekr.20070227093629.1: *4* << initLeo imports >>
        # Import leoGlobals, but do NOT set g.
        try:
            import leo.core.leoGlobals as leoGlobals
        except ImportError:
            print("Error importing leoGlobals.py")

        # Create the application object.
        try:
            import leo.core.leoApp as leoApp
            leoGlobals.app = leoApp.LeoApp()
        except ImportError:
            print("Error importing leoApp.py")

        # NOW we can set g.
        self.g = g = leoGlobals
        assert(g.app)
        g.app.leoID = None

        g.app.silentMode = self.silent # 2011/11/02.
        if trace:
            import sys
            g.trace(sys.argv)
            g.trace('g.app.silentMode',g.app.silentMode)
        # 2010/09/09: create the g.app.pluginsController here.
        import leo.core.leoPlugins as leoPlugins
        leoPlugins.init() # Necessary. Sets g.app.pluginsController.

        try:
            import leo.core.leoNodes as leoNodes
        except ImportError:
            print("Error importing leoNodes.py")
            import traceback ; traceback.print_exc()

        try:
            import leo.core.leoConfig as leoConfig
        except ImportError:
            print("Error importing leoConfig.py")
            import traceback ; traceback.print_exc()

        # Set leoGlobals.g here, rather than in leoGlobals.
        leoGlobals.g = leoGlobals
        #@-<< initLeo imports >>
        g.app.recentFilesManager = leoApp.RecentFilesManager()
        g.app.loadManager = lm = leoApp.LoadManager()
        g.app.loadManager.computeStandardDirectories()
        if not self.getLeoID(): return
        g.app.inBridge = True # Added 2007/10/21: support for g.getScript.
        g.app.nodeIndices = leoNodes.nodeIndices(g.app.leoID)
        g.app.config = leoConfig.GlobalConfigManager()

        if self.readSettings:
            lm.readGlobalSettingsFiles()
                # reads only standard settings files, using a null gui.
                # uses lm.files[0] to compute the local directory
                # that might contain myLeoSettings.leo.
        else:
            # Bug fix: 2012/11/26: create default global settings dicts.
            settings_d,shortcuts_d = lm.createDefaultSettingsDicts()
            lm.globalSettingsDict = settings_d
            lm.globalShortcutsDict = shortcuts_d

        self.createGui() # Create the gui *before* loading plugins.
        if self.verbose: self.reportDirectories()
        self.adjustSysPath()

        # 2011/11/07: Kill all event handling if plugins not loaded.
        if not self.loadPlugins:
            def dummyDoHook(tag,*args,**keys):
                pass
            g.doHook = dummyDoHook
        g.doHook("start1") # Load plugins.
        g.app.computeSignon()
        g.app.initing = False
        g.doHook("start2",c=None,p=None,v=None,fileName=None)
    #@+node:ekr.20070302061713: *4* adjustSysPath
    def adjustSysPath (self):

        '''Adjust sys.path to enable imports as usual with Leo.'''

        import sys

        g = self.g

        #g.trace('loadDir',g.app.loadDir)

        leoDirs = ('config','doc','extensions','modes','plugins','core','test') # 2008/7/30

        for theDir in leoDirs:
            path = g.os_path_finalize_join(g.app.loadDir,'..',theDir)
            if path not in sys.path:
                sys.path.append(path)
    #@+node:ekr.20070227095743: *4* createGui (bridgeController)
    def createGui (self):

        g = self.g

        if self.guiName == 'nullGui':
            g.app.gui = g.app.nullGui
            g.app.log = g.app.gui.log = log = g.app.nullLog
            log.isNull = False
            log.enabled = True # Allow prints from nullLog.
            log.logInited = True # Bug fix: 2012/10/17.
        elif self.guiName == 'qt':
            import leo.plugins.qtGui as qtGui
            g.app.gui = qtGui.leoQtGui()
            print('qtGui created')
        else:
            assert False,'leoBridge.py: unsupported gui: %s' % self.guiName

    #@+node:ekr.20070227093629.4: *4* isValidPython
    def isValidPython(self):

        import sys

        if sys.platform == 'cli':
            return True

        message = """\
    Leo requires Python 2.2.1 or higher.
    You may download Python from http://python.org/download/
    """
        try:
            # This will fail if True/False are not defined.
            import leo.core.leoGlobals as g
            # print('leoBridge:isValidPython:g',g)
            # Set leoGlobals.g here, rather than in leoGlobals.py.
            leoGlobals = g # Don't set g.g, it would pollute the autocompleter.
            leoGlobals.g = g
        except ImportError:
            print("isValidPython: can not import leo.core.leoGlobals as leoGlobals")
            return 0
        except:
            print("isValidPytyhon: unexpected exception: import leo.core.leoGlobals as leoGlobals.py as g")
            import traceback ; traceback.print_exc()
            return 0
        try:
            version = '.'.join([str(sys.version_info[i]) for i in (0,1,2)])
            ok = g.CheckVersion(version,'2.2.1')
            if not ok:
                print(message)
                g.app.gui.runAskOkDialog(None,"Python version error",message=message,text="Exit")
            return ok
        except:
            print("isValidPython: unexpected exception: g.CheckVersion")
            import traceback ; traceback.print_exc()
            return 0
    #@+node:ekr.20070227094232: *4* getLeoID
    def getLeoID (self):

        import os
        import sys

        g = self.g ; tag = ".leoID.txt"
        homeDir = g.app.homeLeoDir
        globalConfigDir = g.app.globalConfigDir
        loadDir = g.app.loadDir

        verbose = False and not g.app.unitTesting
        #@+<< try to get leoID from sys.leoID >>
        #@+node:ekr.20070227094232.1: *5* << try to get leoID from sys.leoID>>
        # This would be set by in Python's sitecustomize.py file.

        # Use hasattr & getattr to suppress pylint warning.
        # We also have to use a "non-constant" attribute to suppress another warning!

        nonConstantAttr = "leoID"

        if hasattr(sys,nonConstantAttr):
            g.app.leoID = getattr(sys,nonConstantAttr)
            if verbose and not g.app.silentMode:
                g.red("leoID=",g.app.leoID,spaces=False)
        #@-<< try to get leoID from sys.leoID >>
        if not g.app.leoID:
            #@+<< try to get leoID from "leoID.txt" >>
            #@+node:ekr.20070227094232.2: *5* << try to get leoID from "leoID.txt" >>
            for theDir in (homeDir,globalConfigDir,loadDir):
                # N.B. We would use the _working_ directory if theDir is None!
                if theDir:
                    try:
                        fn = g.os_path_join(theDir,tag)
                        f = open(fn,'r')
                        s = f.readline()
                        f.close()
                        if s and len(s) > 0:
                            g.app.leoID = s.strip()
                            if verbose and not g.app.silentMode:
                                g.red('leoID=',g.app.leoID,' (in ',theDir,')',spaces=False)
                            break
                        elif verbose:
                            g.red('empty ',tag,' (in ',theDir,')',spaces=False)
                    except IOError:
                        g.app.leoID = None
                    except Exception:
                        g.app.leoID = None
                        g.error('unexpected exception in app.setLeoID')
                        g.es_exception()
            #@-<< try to get leoID from "leoID.txt" >>
        if not g.app.leoID:
            #@+<< try to get leoID from os.getenv('USER') >>
            #@+node:ekr.20070227094232.3: *5* << try to get leoID from os.getenv('USER') >>
            try:
                theId = os.getenv('USER')
                if theId:
                    if verbose: g.red("using os.getenv('USER'):",repr(theId))
                    g.app.leoID = theId

            except Exception:
                pass
            #@-<< try to get leoID from os.getenv('USER') >>
        return g.app.leoID
    #@+node:ekr.20070227093629.9: *4* reportDirectories
    def reportDirectories (self):

        g = self.g

        for kind,theDir in (
            ("global config",g.app.globalConfigDir),
            ("home",g.app.homeDir),
        ):
            g.blue('',kind,'directory','',':',theDir)
    #@+node:ekr.20070227093918: *3* isOpen
    def isOpen (self):

        g = self.g

        return bool(g and g.app and g.app.gui)
    #@+node:ekr.20070227092442.5: *3* openLeoFile & helpers (bridgeController)
    def openLeoFile (self,fileName):

        '''Open a .leo file, or create a new Leo frame if no fileName is given.'''

        g = self.g

        useLog = False

        if self.isOpen():
            fileName = self.completeFileName(fileName)
            c = self.createFrame(fileName)

            if useLog:
                g.app.gui.log = log = c.frame.log
                log.isNull = False
                log.enabled = True
            return c
        else:
            return None
    #@+node:ekr.20070227093629.5: *4* completeFileName (leoBridge)
    def completeFileName (self,fileName):

        g = self.g

        if not (fileName and fileName.strip()): return ''

        import os

        fileName = g.os_path_finalize_join(os.getcwd(),fileName)
        head,ext = g.os_path_splitext(fileName)
        if not ext: fileName = fileName + ".leo"

        return fileName
    #@+node:ekr.20070227093629.6: *4* createFrame (leoBridge)
    def createFrame (self,fileName):

        '''Create a commander and frame for the given file.
        Create a new frame if the fileName is empty or non-exisent.'''

        trace = False
        g = self.g

        if fileName.strip():
            if g.os_path_exists(fileName):
                if trace:
                    import time ; t1 = time.time()
                # This takes a long time due to imports in c.__init__
                c = g.openWithFileName(fileName)
                if trace:
                    t2 = time.time()
                    g.trace('g.openWithFileName: %0.2fsec' % (t2-t1))
                if c: return c
            else:
                print('file not found: %s. creating new window' % (fileName))
        # Create a new frame. Unlike leo.run, this is not a startup window.
        c = g.app.newCommander(fileName)
        frame = c.frame
        frame.createFirstTreeNode() # 2013/09/27: bug fix.
        assert c.rootPosition()
        frame.setInitialWindowGeometry()
        frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio)
        # Call the 'new' hook for compatibility with plugins.
        # 2011/11/07: Do this only if plugins have been loaded.
        g.doHook("new",old_c=None,c=c,new_c=c)
        return c
    #@-others
#@-others
#@-leo

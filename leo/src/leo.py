#! /usr/bin/env python
#@+leo-ver=4-thin
#@+node:ekr.20031218072017.2605:@thin leo.py 
#@@first

"""Entry point for Leo in Python."""

#@@language python
#@@tabwidth -4

#@<< Import pychecker >>
#@+node:ekr.20031218072017.2606:<< Import pychecker >>
#@@color

# __pychecker__ = '--no-argsused'

# See pycheckrc file in leoDist.leo for a list of erroneous warnings to be suppressed.

# New in Leo 4.4.5: use pylint instead of pychecker.

# if 0: # Set to 1 for lint-like testing.
      # # Use t23.bat: only on Python 2.3.

    # try:
        # import pychecker.checker
        # # This works.  We may want to set options here...
        # # from pychecker import Config 
        # # print pychecker
        # print ; print "Warning (in leo.py): pychecker.checker running..." ; print
    # except Exception:
        # print ; print 'Can not import pychecker' ; print
#@-node:ekr.20031218072017.2606:<< Import pychecker >>
#@nl

# __pychecker__ = '--no-import --no-reimportself --no-reimport'
    # Suppress import errors: this module must do strange things with imports.

# Warning: do not import any Leo modules here!
# Doing so would make g.app invalid in the imported files.
import os
import sys
import Tkinter ; Tkinter.wantobjects = 0
    # An ugly hack for Tk/Tkinter 8.5
    # See http://sourceforge.net/forum/message.php?msg_id=4078577

#@+others
#@+node:ekr.20031218072017.1934:run
def run(fileName=None,pymacs=None,jyLeo=False,*args,**keywords):

    """Initialize and run Leo"""

    # __pychecker__ = '--no-argsused' # keywords not used.

    # print 'leo.py:run','fileName',fileName
    if not jyLeo and not isValidPython(): return
    #@    << import leoGlobals and leoApp >>
    #@+node:ekr.20041219072112:<< import leoGlobals and leoApp >>
    if jyLeo:

        print '*** starting jyLeo',sys.platform # will be something like java1.6.0_02

        ### This is a hack.
        ### The jyleo script in test.leo sets the cwd to g.app.loadDir
        ### Eventually, we will have to compute the equivalent here.

        path = os.path.join(os.getcwd()) ### ,'..','src')
        if path not in sys.path:
            print 'appending %s to sys.path' % path
            sys.path.append(path)
        if 0:
            print 'sys.path...'
            for s in sys.path: print s

    # Import leoGlobals, but do NOT set g.
    import leoGlobals
    import leoApp

    # Create the app.
    leoGlobals.app = leoApp.LeoApp()

    # **now** we can set g.
    g = leoGlobals
    assert(g.app)

    if jyLeo:
        startJyleo(g)
    #@-node:ekr.20041219072112:<< import leoGlobals and leoApp >>
    #@nl
    g.computeStandardDirectories()
    adjustSysPath(g)
    if pymacs:
        script = windowFlag = False
    else:
        script, windowFlag = getBatchScript() # Do early so we can compute verbose next.
    verbose = script is None
    g.app.batchMode = script is not None
    g.app.silentMode = '-silent' in sys.argv or '--silent' in sys.argv
    g.app.setLeoID(verbose=verbose) # Force the user to set g.app.leoID.
    #@    << import leoNodes and leoConfig >>
    #@+node:ekr.20041219072416.1:<< import leoNodes and leoConfig >>
    import leoNodes
    import leoConfig

    # try:
        # import leoNodes
    # except ImportError:
        # print "Error importing leoNodes.py"
        # import traceback ; traceback.print_exc()

    # try:
        # import leoConfig
    # except ImportError:
        # print "Error importing leoConfig.py"
        # import traceback ; traceback.print_exc()
    #@-node:ekr.20041219072416.1:<< import leoNodes and leoConfig >>
    #@nl
    g.app.nodeIndices = leoNodes.nodeIndices(g.app.leoID)
    g.app.config = leoConfig.configClass()
    fileName,relativeFileName = completeFileName(fileName)
    reportDirectories(verbose)
    # Read settings *after* setting g.app.config.
    # Read settings *before* opening plugins.  This means if-gui has effect only in per-file settings.
    g.app.config.readSettingsFiles(fileName,verbose)
    g.app.setEncoding()
    if pymacs:
        createNullGuiWithScript(None)
    elif jyLeo:
        import leoSwingGui
        g.app.gui = leoSwingGui.swingGui()
    elif script:
        if windowFlag:
            g.app.createTkGui() # Creates global windows.
            g.app.gui.setScript(script)
            sys.args = []
        else:
            createNullGuiWithScript(script)
        fileName = None
    # Load plugins. Plugins may create g.app.gui.
    g.doHook("start1")
    if g.app.killed: return # Support for g.app.forceShutdown.
    # Create the default gui if needed.
    if g.app.gui == None: g.app.createTkGui() # Creates global windows.
    # Initialize tracing and statistics.
    g.init_sherlock(args)
    if g.app and g.app.use_psyco: startPsyco()
    # Clear g.app.initing _before_ creating the frame.
    g.app.initing = False # "idle" hooks may now call g.app.forceShutdown.
    # Create the main frame.  Show it and all queued messages.
    c,frame = createFrame(fileName,relativeFileName)
    if not frame: return
    g.app.trace_gc          = c.config.getBool('trace_gc')
    g.app.trace_gc_calls    = c.config.getBool('trace_gc_calls')
    g.app.trace_gc_verbose  = c.config.getBool('trace_gc_verbose')
    if g.app.disableSave:
        g.es("disabling save commands",color="red")
    g.app.writeWaitingLog()
    p = c.currentPosition()
    g.doHook("start2",c=c,p=p,v=p,fileName=fileName)
    if c.config.getBool('allow_idle_time_hook'):
        g.enableIdleTimeHook()
    if not fileName:
        c.redraw_now()
    # Respect c's focus wishes if posssible.
    w = g.app.gui.get_focus(c)
    if w != c.frame.body.bodyCtrl and w != c.frame.tree.canvas:
        c.bodyWantsFocus()
        c.k.showStateAndMode(w)
    g.app.gui.runMainLoop()
#@-node:ekr.20031218072017.1934:run
#@+node:ekr.20070930060755:utils
#@+node:ekr.20070306085724:adjustSysPath
def adjustSysPath (g):

    '''Adjust sys.path to enable imports as usual with Leo.'''

    #g.trace('loadDir',g.app.loadDir)

    leoDirs = ('config','doc','extensions','modes','plugins','src','test')

    for theDir in leoDirs:
        path = g.os_path_abspath(
            g.os_path_join(g.app.loadDir,'..',theDir))
        if path not in sys.path:
            sys.path.append(path)
#@-node:ekr.20070306085724:adjustSysPath
#@+node:ekr.20041124083125:completeFileName (leo.py)
def completeFileName (fileName):

    import leoGlobals as g

    if not (fileName and fileName.strip()):
        return None,None

    # This does not depend on config settings.
    try:
        if sys.platform.lower().startswith('win'):
            fileName = g.toUnicode(fileName,'mbcs')
        else:
            fileName = g.toUnicode(fileName,'utf-8')
    except Exception: pass

    relativeFileName = fileName
    fileName = g.os_path_join(os.getcwd(),fileName)

    junk,ext = g.os_path_splitext(fileName)
    if not ext:
        fileName = fileName + ".leo"
        relativeFileName = relativeFileName + ".leo"

    return fileName,relativeFileName
#@-node:ekr.20041124083125:completeFileName (leo.py)
#@+node:ekr.20031218072017.1624:createFrame (leo.py)
def createFrame (fileName,relativeFileName):

    """Create a LeoFrame during Leo's startup process."""

    import leoGlobals as g

    # Try to create a frame for the file.
    if fileName and g.os_path_exists(fileName):
        ok, frame = g.openWithFileName(relativeFileName or fileName,None)
        if ok: return frame.c,frame

    # Create a _new_ frame & indicate it is the startup window.
    c,frame = g.app.newLeoCommanderAndFrame(
        fileName=fileName,
        relativeFileName=relativeFileName,
        initEditCommanders=True)
    assert frame.c == c and c.frame == frame
    frame.setInitialWindowGeometry()
    frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio)
    frame.startupWindow = True
    if c.chapterController:
        c.chapterController.finishCreate()
        c.setChanged(False) # Clear the changed flag set when creating the @chapters node.
    # Call the 'new' hook for compatibility with plugins.
    g.doHook("new",old_c=None,c=c,new_c=c)

    # New in Leo 4.4.8: create the menu as late as possible so it can use user commands.
    p = c.currentPosition()
    if not g.doHook("menu1",c=frame.c,p=p,v=p):
        frame.menu.createMenuBar(frame)
        c.updateRecentFiles(relativeFileName or fileName)
        g.doHook("menu2",c=frame.c,p=p,v=p)
        g.doHook("after-create-leo-frame",c=c)

    # Report the failure to open the file.
    if fileName:
        g.es("file not found:",fileName)

    return c,frame
#@-node:ekr.20031218072017.1624:createFrame (leo.py)
#@+node:ekr.20031218072017.1938:createNullGuiWithScript (leo.py)
def createNullGuiWithScript (script):

    import leoGlobals as g
    import leoGui

    g.app.batchMode = True
    g.app.gui = leoGui.nullGui("nullGui")
    g.app.gui.setScript(script)
#@-node:ekr.20031218072017.1938:createNullGuiWithScript (leo.py)
#@+node:ekr.20031218072017.1939:getBatchScript
def getBatchScript ():

    import leoGlobals as g
    windowFlag = False

    name = None ; i = 1 # Skip the dummy first arg.
    while i + 1 < len(sys.argv):
        arg = sys.argv[i].strip().lower()
        if arg in ("--script","-script"):
            name = sys.argv[i+1].strip() ; break
        if arg in ("--script-window","-script-window"):
            name = sys.argv[i+1].strip() ; windowFlag = True ; break
        i += 1

    if not name:
        return None, windowFlag
    name = g.os_path_join(g.app.loadDir,name)
    try:
        f = None
        try:
            f = open(name,'r')
            script = f.read()
            # g.trace("script",script)
        except IOError:
            g.es_print("can not open script file:",name, color="red")
            script = None
    finally:
        if f: f.close()

    # Bug fix 4/27/07: Don't put a return in a finally clause.
    return script, windowFlag
#@-node:ekr.20031218072017.1939:getBatchScript
#@+node:ekr.20071117060958:getFileName
def getFileName ():

    '''Return the filename.

    This is a hack for when Leo is started from a script that also starts IPython.'''

    # No imports here.
    # print 'leo.py:getFileName',sys.argv

    i = 1
    while i < len(sys.argv) and sys.argv[i].endswith('.py'):
        i += 1

    if sys.platform=="win32": # Windows
        result = ' '.join(sys.argv[i:])
    else:
        result = sys.argv[i]

    return result
#@-node:ekr.20071117060958:getFileName
#@+node:ekr.20031218072017.1936:isValidPython
def isValidPython():

    import traceback

    if sys.platform == 'cli':
        return True

    message = """\
Leo requires Python 2.2.1 or higher.
You may download Python from http://python.org/download/
"""
    try:
        # This will fail if True/False are not defined.
        import leoGlobals as g
    except ImportError:
        print "isValidPython: can not import leoGlobals"
        return 0
    except:
        print "isValidPytyhon: unexpected exception: import leoGlobals.py as g"
        traceback.print_exc()
        return 0
    try:
        version = '.'.join([str(sys.version_info[i]) for i in (0,1,2)])
        ok = g.CheckVersion(version,'2.2.1')
        if not ok:
            print message
            g.app.gui.runAskOkDialog(None,"Python version error",message=message,text="Exit")
        return ok
    except Exception:
        print "isValidPython: unexpected exception: g.CheckVersion"
        traceback.print_exc()
        return 0
#@-node:ekr.20031218072017.1936:isValidPython
#@+node:ekr.20031218072017.2607:profile_leo
#@+at 
#@nonl
# To gather statistics, do the following in a Python window, not idle:
# 
#     import leo
#     leo.profile_leo()  (this runs leo)
#     load leoDocs.leo (it is very slow)
#     quit Leo.
#@-at
#@@c

def profile_leo ():

    """Gather and print statistics about Leo"""

    import profile, pstats
    import leoGlobals as g

    # name = "c:/prog/test/leoProfile.txt"
    name = g.os_path_abspath(g.os_path_join(g.app.loadDir,'..','test','leoProfile.txt'))

    profile.run('leo.run()',name)

    p = pstats.Stats(name)
    p.strip_dirs()
    p.sort_stats('cum','file','name')
    p.print_stats()
#@-node:ekr.20031218072017.2607:profile_leo
#@+node:ekr.20041130093254:reportDirectories
def reportDirectories(verbose):

    import leoGlobals as g

    if verbose:
        for kind,theDir in (
            ("load",g.app.loadDir),
            ("global config",g.app.globalConfigDir),
            ("home",g.app.homeDir),
        ):
            g.es("%s dir:" % (kind),theDir,color="blue")
#@-node:ekr.20041130093254:reportDirectories
#@+node:ekr.20070930194949:startJyleo (leo.py)
def startJyleo (g):

    import leoSwingFrame
    import leoSwingUtils
    import java.awt as awt

    if 1:
        g.app.splash = None
    else:
        g.app.splash = splash = leoSwingFrame.leoSplash()
        awt.EventQueue.invokeAndWait(splash)

    gct = leoSwingUtils.GCEveryOneMinute()
    gct.run()

    tk = awt.Toolkit.getDefaultToolkit()
    tk.setDynamicLayout(True)
#@-node:ekr.20070930194949:startJyleo (leo.py)
#@+node:ekr.20040411081633:startPsyco
def startPsyco ():

    import leoGlobals as g

    try:
        import psyco
        if 0:
            theFile = r"c:\prog\test\psycoLog.txt"
            g.es("psyco now logging to:",theFile,color="blue")
            psyco.log(theFile)
            psyco.profile()
        psyco.full()
        g.es("psyco now running",color="blue")
    except ImportError:
        g.app.use_psyco = False
    except:
        print "unexpected exception importing psyco"
        g.es_exception()
        g.app.use_psyco = False
#@-node:ekr.20040411081633:startPsyco
#@-node:ekr.20070930060755:utils
#@-others

if __name__ == "__main__":

    # Keep pylint happy by not defining any symbols at the top level.
    if len(sys.argv) > 1:
        run(getFileName())
    else:
        run()
#@-node:ekr.20031218072017.2605:@thin leo.py 
#@-leo

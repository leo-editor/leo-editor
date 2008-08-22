#! /usr/bin/env python
#@+leo-ver=4-thin
#@+node:ekr.20031218072017.2605:@thin runLeo.py 
#@@first

"""Entry point for Leo in Python."""

#@@language python
#@@tabwidth -4

#@<< Import pychecker >>
#@+node:ekr.20031218072017.2606:<< Import pychecker >>
#@@color

__pychecker__ = '--no-argsused'

# See pycheckrc file in leoDist.leo for a list of erroneous warnings to be suppressed.

if 0: # Set to 1 for lint-like testing.
      # Use t23.bat: only on Python 2.3.

    try:
        import pychecker.checker
        print('\npychecker.checker running...')
    except Exception:
        print('\nCan not import pychecker\n')
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

    import pdb ; pdb = pdb.set_trace

    #@    << import leoGlobals and leoApp >>
    #@+node:ekr.20041219072112:<< import leoGlobals and leoApp >>
    if jyLeo:
        print('*** starting jyLeo',sys.platform) # will be something like java1.6.0_02

    # Add the current directory to sys.path *before* importing g.
    # This will fail if the current directory contains unicode characters...
    path = os.getcwd()
    if path not in sys.path:
        # print('appending %s to sys.path' % path)
        sys.path.append(path)

    # Import leoGlobals, but do NOT set g.
    import leo.core.leoGlobals as leoGlobals

    # Set leoGlobals.g here, rather than in leoGlobals.py.
    leoGlobals.g = leoGlobals

    import leo.core.leoApp as leoApp

    # Create the app.
    leoGlobals.app = leoApp.LeoApp()

    # **now** we can set g.
    g = leoGlobals
    assert(g.app)

    if jyLeo:
        startJyleo(g)
    #@-node:ekr.20041219072112:<< import leoGlobals and leoApp >>
    #@nl
    if not jyLeo and not isValidPython(): return
    g.computeStandardDirectories()
    adjustSysPath(g)
    script,windowFlag = scanOptions(g)
    if pymacs: script,windowFlag = None,False
    verbose = script is None
    g.app.setLeoID(verbose=verbose) # Force the user to set g.app.leoID.
    if not fileName:
        fileName = getFileName()

    #@    << import other early files >>
    #@+node:ekr.20041219072416.1:<< import other early files>>
    import leo.core.leoNodes as leoNodes
    import leo.core.leoConfig as leoConfig

    # There is a circular dependency between leoCommands and leoEditCommands.
    import leo.core.leoCommands as leoCommands

    # New in Leo 4.5 b3: make sure we call the new leoPlugins.init top-level function.
    # This prevents a crash when run is called repeatedly from IPython's lleo extension.
    import leo.core.leoPlugins as leoPlugins
    leoPlugins.init()
    #@-node:ekr.20041219072416.1:<< import other early files>>
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
        import leo.core.leoSwingGui as leoSwingGui
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
    if g.app.oneConfigFilename: g.es_print('--one-config option in effect',color='red')
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
    c.outerUpdate()
    g.app.gui.runMainLoop()
#@-node:ekr.20031218072017.1934:run
#@+node:ekr.20070930060755:utils
#@+node:ekr.20070306085724:adjustSysPath
def adjustSysPath (g):

    '''Adjust sys.path to enable imports as usual with Leo.'''

    #g.trace('loadDir',g.app.loadDir)

    leoDirs = ('config','doc','extensions','modes','plugins','core','test')

    for theDir in leoDirs:
        path = g.os_path_abspath(
            g.os_path_join(g.app.loadDir,'..',theDir))
        if path not in sys.path:
            sys.path.append(path)
#@-node:ekr.20070306085724:adjustSysPath
#@+node:ekr.20041124083125:completeFileName (leo.py)
def completeFileName (fileName):

    import leo.core.leoGlobals as g

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

    import leo.core.leoGlobals as g

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

    import leo.core.leoGlobals as g
    import leo.core.leoGui as leoGui

    g.app.batchMode = True
    g.app.gui = leoGui.nullGui("nullGui")
    g.app.gui.setScript(script)
#@-node:ekr.20031218072017.1938:createNullGuiWithScript (leo.py)
#@+node:ekr.20071117060958:getFileName
def getFileName ():

    '''Return the filename from sys.argv.'''

    # Put no imports here.
    return len(sys.argv) > 1 and sys.argv[-1]
#@-node:ekr.20071117060958:getFileName
#@+node:ekr.20031218072017.1936:isValidPython
def isValidPython():

    import traceback

    if sys.platform == 'cli':
        return True

    message = """\
Leo requires Python 2.4 or higher.
You may download Python from
http://python.org/download/
"""
    try:
        # This will fail if True/False are not defined.
        import leo.core.leoGlobals as g
    except ImportError:
        print("isValidPython: can not import leo.core.leoGlobals")
        return 0
    except:
        print("isValidPytyhon: unexpected exception: import leo.core.leoGlobals")
        traceback.print_exc()
        return 0
    try:
        version = '.'.join([str(sys.version_info[i]) for i in (0,1,2)])
        ok = g.CheckVersion(version,'2.4.0')
        if not ok:
            print(message)
            try:
                # g.app.gui does not exist yet.
                import Tkinter as Tk
                #@                << define emergency dialog class >>
                #@+node:ekr.20080822065427.8:<< define emergency dialog class >>
                class emergencyDialog:

                    """A class that creates an Tkinter dialog with a single OK button."""

                    #@    @+others
                    #@+node:ekr.20080822065427.9:__init__ (emergencyDialog)
                    def __init__(self,title,message):

                        """Constructor for the leoTkinterDialog class."""

                        self.answer = None # Value returned from run()
                        self.title = title
                        self.message=message

                        self.buttonsFrame = None # Frame to hold typical dialog buttons.
                        self.defaultButtonCommand = None  # Command to call when user closes the window by clicking the close box.
                        self.frame = None # The outermost frame.
                        self.root = None # Created in createTopFrame.
                        self.top = None # The toplevel Tk widget.

                        self.createTopFrame()
                        buttons = {"text":"OK","command":self.okButton,"default":True}, # Singleton tuple.
                        self.createButtons(buttons)
                        self.top.bind("<Key>", self.onKey)
                    #@-node:ekr.20080822065427.9:__init__ (emergencyDialog)
                    #@+node:ekr.20080822065427.12:createButtons
                    def createButtons (self,buttons):

                        """Create a row of buttons.

                        buttons is a list of dictionaries containing the properties of each button."""

                        assert(self.frame)
                        self.buttonsFrame = f = Tk.Frame(self.top)
                        f.pack(side="top",padx=30)

                        # Buttons is a list of dictionaries, with an empty dictionary at the end if there is only one entry.
                        buttonList = []
                        for d in buttons:
                            text = d.get("text","<missing button name>")
                            isDefault = d.get("default",False)
                            underline = d.get("underline",0)
                            command = d.get("command",None)
                            bd = g.choose(isDefault,4,2)

                            b = Tk.Button(f,width=6,text=text,bd=bd,underline=underline,command=command)
                            b.pack(side="left",padx=5,pady=10)
                            buttonList.append(b)

                            if isDefault and command:
                                self.defaultButtonCommand = command

                        return buttonList
                    #@-node:ekr.20080822065427.12:createButtons
                    #@+node:ekr.20080822065427.14:createTopFrame
                    def createTopFrame(self):

                        """Create the Tk.Toplevel widget for a leoTkinterDialog."""

                        self.root = Tk.Tk()
                        self.top = Tk.Toplevel(self.root)
                        self.top.title(self.title)
                        self.root.withdraw()

                        self.frame = Tk.Frame(self.top)
                        self.frame.pack(side="top",expand=1,fill="both")

                        label = Tk.Label(self.frame,text=message,bg='white')
                        label.pack(pady=10)
                    #@-node:ekr.20080822065427.14:createTopFrame
                    #@+node:ekr.20080822065427.10:okButton
                    def okButton(self):

                        """Do default click action in ok button."""

                        self.top.destroy()
                        self.top = None

                    #@-node:ekr.20080822065427.10:okButton
                    #@+node:ekr.20080822065427.21:onKey
                    def onKey(self,event):

                        """Handle Key events in askOk dialogs."""

                        self.okButton()

                        return "break"
                    #@-node:ekr.20080822065427.21:onKey
                    #@+node:ekr.20080822065427.16:run
                    def run (self):

                        """Run the modal emergency dialog."""

                        self.top.geometry("%dx%d%+d%+d" % (300,200,50,50))
                        self.top.lift()

                        self.top.grab_set() # Make the dialog a modal dialog.
                        self.root.wait_window(self.top)
                    #@-node:ekr.20080822065427.16:run
                    #@-others
                #@-node:ekr.20080822065427.8:<< define emergency dialog class >>
                #@nl
                d = emergencyDialog(title='Python Version Error',message=message)
                d.run()
            except Exception:
                pass
        return ok
    except Exception:
        print("isValidPython: unexpected exception: g.CheckVersion")
        traceback.print_exc()
        return 0
#@-node:ekr.20031218072017.1936:isValidPython
#@+node:ekr.20031218072017.2607:profile_leo
#@+at 
#@nonl
# To gather statistics, do the following in a Python window, not idle:
# 
#     import leo
#     import leo.core.runLeo as runLeo
#     runLeo.profile_leo()  (this runs leo)
#     load leoDocs.leo (it is very slow)
#     quit Leo.
#@-at
#@@c

def profile_leo ():

    """Gather and print statistics about Leo"""

    import cProfile as profile
    import pstats
    import leo.core.leoGlobals as g

    name = r"c:\leo.repo\trunk\leo\test\leoProfile.txt"
    # name = g.os_path_abspath(g.os_path_join(g.app.loadDir,'..','test','leoProfile.txt'))

    profile.run('leo.run()',name)

    p = pstats.Stats(name)
    p.strip_dirs()
    p.sort_stats('module','calls','time','name')
    reFiles='leoAtFile.py:|leoFileCommands.py:|leoGlobals.py|leoNodes.py:'
    p.print_stats(reFiles)
#@-node:ekr.20031218072017.2607:profile_leo
#@+node:ekr.20041130093254:reportDirectories
def reportDirectories(verbose):

    import leo.core.leoGlobals as g

    if verbose:
        for kind,theDir in (
            ("load",g.app.loadDir),
            ("global config",g.app.globalConfigDir),
            ("home",g.app.homeDir),
        ):
            g.es("%s dir:" % (kind),theDir,color="blue")
#@-node:ekr.20041130093254:reportDirectories
#@+node:ekr.20080521132317.2:scanOptions
def scanOptions(g):

    '''Handle all options and remove them from sys.argv.'''

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('--one-config',dest="one_config_path")
    parser.add_option('--silent',action="store_false",dest="silent")
    parser.add_option('--script',dest="script")
    parser.add_option('--script-window',dest="script_window")

    # Parse the options, and remove them from sys.argv.
    options, args = parser.parse_args()
    sys.argv = [sys.argv[0]] ; sys.argv.extend(args)
    # g.trace(sys.argv)

    # Handle the args...

    # --one-config
    path = options.one_config_path
    if path:
        path = g.os_path_abspath(g.os_path_join(os.getcwd(),path))
        if g.os_path_exists(path):
            g.app.oneConfigFilename = path
        else:
            g.es_print('Invalid option: file not found:',path,color='red')

    # --script
    script_path = options.script
    script_path_w = options.script_window
    if script_path and script_path_w:
        parser.error("--script and script-window are mutually exclusive")

    script_name = script_path or script_path_w
    if script_name:
        script_name = g.os_path_join(g.app.loadDir,script_name)
        try:
            f = None
            try:
                f = open(script_name,'r')
                script = f.read()
                # g.trace("script",script)
            except IOError:
                g.es_print("can not open script file:",script_name, color="red")
                script = None
        finally:
            if f: f.close()
    else:
        script = None

    # --silent
    g.app.silentMode = options.silent

    # Compute the return values.
    windowFlag = script and script_path_w
    return script, windowFlag
#@nonl
#@-node:ekr.20080521132317.2:scanOptions
#@+node:ekr.20070930194949:startJyleo (leo.py)
def startJyleo (g):

    import leo.core.leoSwingFrame as leoSwingFrame
    import leo.core.leoSwingUtils as leoSwingUtils
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

    import leo.core.leoGlobals as g

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
        g.pr("unexpected exception importing psyco")
        g.es_exception()
        g.app.use_psyco = False
#@-node:ekr.20040411081633:startPsyco
#@-node:ekr.20070930060755:utils
#@-others

if __name__ == "__main__":
    run()

#@-node:ekr.20031218072017.2605:@thin runLeo.py 
#@-leo

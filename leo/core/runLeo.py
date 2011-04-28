#! /usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2605: * @file runLeo.py 
#@@first

"""Entry point for Leo in Python."""

#@@language python
#@@tabwidth -4

#@+<< imports and inits >>
#@+node:ekr.20080921091311.1: ** << imports and inits >>
# import pdb ; pdb = pdb.set_trace
import optparse
import os
import sys
import traceback

try:
    import Tkinter ; Tkinter.wantobjects = 0
        # An ugly hack for Tk/Tkinter 8.5
        # See http://sourceforge.net/forum/message.php?msg_id=4078577
except ImportError:
    try:
        import tkinter ; tkinter.wantobject = 0
    except ImportError:
        pass

path = os.getcwd()
if path not in sys.path:
    # print('appending %s to sys.path' % path)
    sys.path.append(path)

# Import leoGlobals, but do NOT set g.
import leo.core.leoGlobals as leoGlobals

try:
    # This will fail if True/False are not defined.
    import leo.core.leoGlobals as g
except ImportError:
    print("runLeo.py: can not import leo.core.leoGlobals")
    raise
except Exception:
    print("runLeo.py: unexpected exception: import leo.core.leoGlobals")
    raise

# Set leoGlobals.g here, rather than in leoGlobals.py.
leoGlobals.g = leoGlobals

import leo.core.leoApp as leoApp

# Create the app.
leoGlobals.app = leoApp.LeoApp()

# **now** we can set g.
g = leoGlobals
assert(g.app)

# Do early inits
import leo.core.leoNodes as leoNodes
import leo.core.leoConfig as leoConfig

# There is a circular dependency between leoCommands and leoEditCommands.
import leo.core.leoCommands as leoCommands

# Make sure we call the new leoPlugins.init top-level function.
# This prevents a crash when run is called repeatedly from
# IPython's lleo extension.
import leo.core.leoPlugins as leoPlugins
leoPlugins.init()

# Do all other imports.
import leo.core.leoGui as leoGui
#@-<< imports and inits >>

#@+others
#@+node:ekr.20031218072017.2607: ** profile_leo
#@+at To gather statistics, do the following in a Python window, not idle:
# 
#     import leo
#     import leo.core.runLeo as runLeo
#     runLeo.profile_leo()  (this runs leo)
#     load leoDocs.leo (it is very slow)
#     quit Leo.
#@@c

def profile_leo ():

    """Gather and print statistics about Leo"""

    import cProfile as profile
    import pstats
    import leo.core.leoGlobals as g
    import os

    theDir = os.getcwd()

    # On Windows, name must be a plain string. An apparent cProfile bug.
    name = str(g.os_path_normpath(g.os_path_join(theDir,'leoProfile.txt')))
    print ('profiling to %s' % name)
    profile.run('import leo ; leo.run()',name)
    p = pstats.Stats(name)
    p.strip_dirs()
    p.sort_stats('module','calls','time','name')
    #reFiles='leoAtFile.py:|leoFileCommands.py:|leoGlobals.py|leoNodes.py:'
    #p.print_stats(reFiles)
    p.print_stats()

prof = profile_leo
#@+node:ekr.20031218072017.1934: ** run & helpers
def run(fileName=None,pymacs=None,*args,**keywords):

    """Initialize and run Leo"""

    trace = False # and not g.unitTesting
    if trace: print('runLeo.run: sys.argv %s' % sys.argv)

    # Phase 1: before loading plugins.
    # Scan options, set directories and read settings.
    if not isValidPython(): return

    files,options = doPrePluginsInit(fileName,pymacs)
    if options.get('exit'): return

    # Phase 2: load plugins: the gui has already been set.
    g.doHook("start1")
    if g.app.killed: return

    # Phase 3: after loading plugins. Create one or more frames.
    ok = doPostPluginsInit(args,files,options)
    if ok: g.app.gui.runMainLoop()
        # For scripts, the gui is a nullGui.
        # and the gui.setScript has already been called.
#@+node:ekr.20090519143741.5915: *3* doPrePluginsInit & helpers
def doPrePluginsInit(fileName,pymacs):

    ''' Scan options, set directories and read settings.'''

    trace = False
    g.computeStandardDirectories()
    adjustSysPath()
    options = scanOptions()

    # Post-process the options.
    fileName2 = options.get('fileName')
    if fileName2: fileName = fileName2

    if pymacs:
        options['script'] = script = None
        options['windowFlag'] = False
    else:
        script = options.get('script')
    verbose = script is None

    # Init the app.
    initApp(verbose)
    files = getFiles(fileName2)
    reportDirectories(verbose)

    # Read settings *after* setting g.app.config and *before* opening plugins.
    # This means if-gui has effect only in per-file settings.
    g.app.config.readSettingsFiles(None,verbose)
    for fn in files:
        g.app.config.readSettingsFiles(fn,verbose)

    if not files and not script:
        # This must be done *after* the standard settings have been read.
        fn = getDefaultFile()
        if fn:
            files = [fn]
            g.app.config.readSettingsFiles(fn,verbose=True)

    g.app.setGlobalDb()
    createGui(pymacs,options)

    # if no gui specified on command line, and qt not installed
    # set options['gui'] to 'tk' to match reality
    if g.app.guiArgName == 'tk':
        options['gui'] = 'tk'

    # We can't print the signon until we know the gui.
    g.app.computeSignon() # Set app.signon/signon2 for commanders.
    versionFlag = options.get('versionFlag')
    if versionFlag:
        print(g.app.signon)
    if versionFlag or not g.app.gui:
        options['exit'] = True

    return files,options
#@+node:ekr.20100914142850.5892: *4* createGui & helper
def createGui(pymacs,options):

    gui = options.get('gui')
    windowFlag = options.get('windowFlag')
    script = options.get('script')

    if g.app.gui:
        pass # initApp (setLeoID) created the gui.
    elif gui is None:
        if script and not windowFlag:
            # Always use null gui for scripts.
            g.app.createNullGuiWithScript(script)
        else:
            g.app.createDefaultGui(__file__)
    else:
        createSpecialGui(gui,pymacs,script,windowFlag)

#@+node:ekr.20080921060401.4: *4* createSpecialGui
def createSpecialGui(gui,pymacs,script,windowFlag):

    if pymacs:
        g.app.createNullGuiWithScript(script=None)
    elif script:
        if windowFlag:
            g.app.createDefaultGui()
            g.app.gui.setScript(script=script)
            sys.args = []
        else:
            g.app.createNullGuiWithScript(script=script)
    else:
        assert g.app.guiArgName
        g.app.createDefaultGui() 
#@+node:ekr.20070306085724: *4* adjustSysPath
def adjustSysPath ():

    '''Adjust sys.path to enable imports as usual with Leo.

    This method is no longer needed:

    1. g.importModule will import from the
       'external' or 'extensions' folders as needed
       without altering sys.path.

    2  Plugins now do fully qualified imports.
    '''
#@+node:ekr.20041124083125: *4* completeFileName
def completeFileName (fileName):

    trace = False
    if trace: print('completeFileName',fileName)

    if not (fileName and fileName.strip()):
        return None,None

    fileName = g.toUnicode(fileName)
    fileName = g.os_path_finalize(fileName)
    junk,ext = g.os_path_splitext(fileName)

    # Bug fix: don't add .leo to existing files.
    if g.os_path_exists(fileName):
        pass # use the fileName as is.
    elif ext != '.leo':
        fileName = fileName + ".leo"

    if trace: print('completeFileName',fileName)

    return fileName
#@+node:ekr.20101021101942.6010: *4* getDefaultFile
def getDefaultFile ():

    # Get the name of the workbook.
    fn = g.app.config.getString(c=None,setting='default_leo_file')
    fn = g.os_path_finalize(fn)
    if not fn: return

    # g.trace(g.os_path_exists(fn),fn)

    if g.os_path_exists(fn):
        return fn
    elif g.os_path_isabs(fn):
        # Create the file.
        g.es_print('Using default leo file name:\n%s' % (fn),color='red')
        return fn
    else:
        # It's too risky to open a default file if it is relative.
        return None
#@+node:ekr.20101020125657.5976: *4* getFiles
def getFiles(fileName):

    files = []
    if fileName:
        files.append(fileName)

    for arg in sys.argv[1:]:
        if not arg.startswith('-'):
            files.append(arg)

    files = [completeFileName(z) for z in files]
    return files
#@+node:ekr.20080921091311.2: *4* initApp
def initApp (verbose):

    assert g.app.guiArgName

    # Force the user to set g.app.leoID.
    g.app.setLeoID(verbose=verbose)
    g.app.config = leoConfig.configClass()
    g.app.nodeIndices = leoNodes.nodeIndices(g.app.leoID)
    g.app.pluginsController.finishCreate() # 2010/09/09
#@+node:ekr.20041130093254: *4* reportDirectories
def reportDirectories(verbose):

    if verbose:
        for kind,theDir in (
            ("load",g.app.loadDir),
            ("global config",g.app.globalConfigDir),
            ("home",g.app.homeDir),
        ):
            g.es("%s dir:" % (kind),theDir,color="blue")
#@+node:ekr.20091007103358.6061: *4* scanOptions
def scanOptions():

    '''Handle all options and remove them from sys.argv.'''
    trace = False

    # Note: this automatically implements the --help option.
    parser = optparse.OptionParser()
    add = parser.add_option
    add('-c', '--config', dest="one_config_path",
        help = 'use a single configuration file')
    add('--debug',        action="store_true",dest="debug",
        help = 'enable debugging support')
    add('-f', '--file',   dest="fileName",
        help = 'load a file at startup')
    add('--gui',
        help = 'gui to use (qt/tk/qttabs)')
    add('--minimized',    action="store_true",
        help = 'start minimized (Qt only)')
    add('--maximized',    action="store_true",
        help = 'start maximized (Qt only)')
    add('--fullscreen',   action="store_true",
        help = 'start fullscreen (Qt only)')
    add('--ipython',      action="store_true",dest="use_ipython",
        help = 'enable ipython support')
    add('--no-cache',     action="store_true",dest='no_cache',
        help = 'disable reading of cached files')
    add('--silent',       action="store_true",dest="silent",
        help = 'disable all log messages')
    add('--screen-shot',  dest='screenshot_fn',
        help = 'take a screen shot and then exit')
    add('--script',       dest="script",
        help = 'execute a script and then exit')
    add('--script-window',dest="script_window",
        help = 'open a window for scripts')
    add('--select',       dest='select',
        help='headline or gnx of node to select')
    add('--version',      action="store_true",dest="version",
        help='print version number and exit')
    add('--window-size',  dest='window_size',
        help='initial window size in height x width format')

    # Parse the options, and remove them from sys.argv.
    options, args = parser.parse_args()
    sys.argv = [sys.argv[0]] ; sys.argv.extend(args)
    if trace: print('scanOptions:',sys.argv)

    # Handle the args...

    # -c or --config
    path = options.one_config_path
    if path:
        path = g.os_path_finalize_join(os.getcwd(),path)
        if g.os_path_exists(path):
            g.app.oneConfigFilename = path
        else:
            g.es_print('Invalid -c option: file not found:',path,color='red')

    # --debug
    if options.debug:
        g.debug = True
        print('scanOptions: *** debug mode on')

    # -f or --file
    fileName = options.fileName
    if fileName:
        fileName = fileName.strip('"')
        if trace: print('scanOptions:',fileName)

    # --gui
    gui = options.gui

    if gui:
        gui = gui.lower()
        if gui == 'qttabs':
            gui = g.app.guiArgName = 'qt'
            g.app.qt_use_tabs = True
        elif gui in ('curses','tk','qt','null'): # 'wx',
            g.app.guiArgName = gui
            g.app.qt_use_tabs = False
        else:
            print('scanOptions: unknown gui: %s' % gui)
            g.app.guiArgName = gui = 'qt'
            g.app.qt_use_tabs = True
    else:
        gui = g.app.guiArgName = 'qt'
        g.app.qt_use_tabs = True

    assert gui == g.app.guiArgName

    # --minimized
    # --maximized
    # --fullscreen
    g.app.start_minimized = options.minimized
    g.app.start_maximized = options.maximized
    g.app.start_fullscreen = options.fullscreen

    # --ipython
    g.app.useIpython = options.use_ipython

    # --no-cache
    if options.no_cache:
        print('scanOptions: disabling caching')
        g.enableDB = False

    # --screen-shot=fn
    screenshot_fn = options.screenshot_fn
    if screenshot_fn:
        screenshot_fn = screenshot_fn.strip('"')
        if trace: print('scanOptions: screenshot_fn',screenshot_fn)

    # --script
    script_path = options.script
    script_path_w = options.script_window
    if script_path and script_path_w:
        parser.error("--script and script-window are mutually exclusive")

    script_name = script_path or script_path_w
    if script_name:
        script_name = g.os_path_finalize_join(g.app.loadDir,script_name)
        script,e = g.readFileIntoString(script_name,kind='script:')
        # print('script_name',repr(script_name))
    else:
        script = None
        # if trace: print('scanOptions: no script')

    # --select
    select = options.select
    if select:
        select = select.strip('"')
        if trace: print('scanOptions: select',repr(select))

    # --silent
    g.app.silentMode = options.silent
    # print('scanOptions: silentMode',g.app.silentMode)

    # --version: print the version and exit.
    versionFlag = options.version

    # --window-size
    windowSize = options.window_size
    if windowSize:
        if trace: print('windowSize',repr(windowSize))
        try:
            h,w = windowSize.split('x')
        except ValueError:
            windowSize = None
            g.trace('bad --window-size:',size)

    # Compute the return values.
    windowFlag = script and script_path_w
    return {
        'fileName':fileName,
        'gui':gui,
        'screenshot_fn':screenshot_fn,
        'script':script,
        'select':select,
        'version':versionFlag,
        'windowFlag':windowFlag,
        'windowSize':windowSize,
    }
#@+node:ekr.20090519143741.5917: *3* doPostPluginsInit & helpers (runLeo.py)
def doPostPluginsInit(args,files,options):

    '''Return True if the frame was created properly.'''

    g.init_sherlock(args)  # Init tracing and statistics.
    # if g.app and g.app.use_psyco: startPsyco()

    # Clear g.app.initing _before_ creating the frame.
    g.app.initing = False # "idle" hooks may now call g.app.forceShutdown.

    # Create the main frame.  Show it and all queued messages.
    c,c1,fileName = None,None,None
    for fileName in files:
        c,frame = createFrame(fileName,options)
        if frame:
            if not c1: c1 = c
        else:
            g.trace('createFrame failed',repr(fileName))
            return False
          
    # Put the focus in the first-opened file.  
    if not c:
        c,frame = createFrame(None,options)
        c1 = c
        if c and frame:
            fileName = c.fileName()
        else:
            g.trace('createFrame failed 2')
            return False
            
    # For qttabs gui, select the first-loaded tab.
    if hasattr(g.app.gui,'frameFactory'):
        factory = g.app.gui.frameFactory
        if factory and hasattr(factory,'setTabForCommander'):
            c = c1
            factory.setTabForCommander(c)

    # Do the final inits.
    c.setLog() # 2010/10/20
    g.app.logInited = True # 2010/10/20
    finishInitApp(c)
    p = c.p
    g.app.initComplete = True
    g.doHook("start2",c=c,p=p,v=p,fileName=fileName)
    if c.config.getBool('allow_idle_time_hook'):
        g.enableIdleTimeHook()
    initFocusAndDraw(c,fileName)

    screenshot_fn = options.get('screenshot_fn')
    if screenshot_fn:
        make_screen_shot(screenshot_fn)
        return False # Force an immediate exit.

    return True
#@+node:ekr.20031218072017.1624: *4* createFrame & helpers (runLeo.py)
def createFrame (fileName,options):

    """Create a LeoFrame during Leo's startup process."""
    
    # g.trace('(runLeo.py)',fileName)

    script = options.get('script')

    # Try to create a frame for the file.
    if fileName and g.os_path_exists(fileName):
        ok, frame = g.openWithFileName(fileName,None)
        c2 = frame.c
        select = options.get('select')
        windowSize = options.get('windowSize')
        if select: doSelect(c2,select)
        if windowSize: doWindowSize(c2,windowSize)
        if ok: return c2,frame

    # Create a _new_ frame & indicate it is the startup window.
    c,frame = g.app.newLeoCommanderAndFrame(
        fileName=fileName,
        initEditCommanders=True)

    if not script:
        g.app.writeWaitingLog(c) # 2009/12/22: fixes bug 448886

    assert frame.c == c and c.frame == frame
    frame.setInitialWindowGeometry()
    frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio)
    frame.startupWindow = True
    if c.chapterController:
        c.chapterController.finishCreate()
        c.setChanged(False)
            # Clear the changed flag set when creating the @chapters node.
    # Call the 'new' hook for compatibility with plugins.
    g.doHook("new",old_c=None,c=c,new_c=c)

    g.createMenu(c,fileName)
    g.finishOpen(c) # Calls c.redraw.

    # Report the failure to open the file.
    if fileName:
        g.es_print("file not found:",fileName,color='red')

    return c,frame
#@+node:ekr.20100913171604.5888: *5* doSelect
def doSelect (c,s):

    '''Select the node with key s.'''

    p = findNode(c,s)

    if p:
        c.selectPosition(p)
    else:
        g.es_print('--select: not found:',s)
#@+node:ekr.20100913171604.5885: *5* doWindowSize
def doWindowSize (c,windowSize):

    w = c.frame.top

    try:
        h,w2 = windowSize.split('x')
        h,w2 = int(h.strip()),int(w2.strip())
        w.resize(w2,h) # 2010/10/08.
        c.k.simulateCommand('equal-sized-panes')
        c.redraw()
        w.repaint() # Essential
    except Exception:
        print('doWindowSize:unexpected exception')
        g.es_exception()
#@+node:ekr.20100913171604.5889: *5* findNode
def findNode (c,s):

    s = s.strip()

    # First, assume s is a gnx.
    for p in c.all_unique_positions():
        if p.gnx.strip() == s:
            return p

    for p in c.all_unique_positions():
        # g.trace(p.h.strip())
        if p.h.strip() == s:
            return p

    return None
#@+node:ekr.20080921060401.5: *4* finishInitApp (runLeo.py)
def finishInitApp(c):

    g.app.trace_gc          = c.config.getBool('trace_gc')
    g.app.trace_gc_calls    = c.config.getBool('trace_gc_calls')
    g.app.trace_gc_verbose  = c.config.getBool('trace_gc_verbose')

    if g.app.disableSave:
        g.es("disabling save commands",color="red")
#@+node:ekr.20080921060401.6: *4* initFocusAndDraw
def initFocusAndDraw(c,fileName):

    w = g.app.gui.get_focus(c)

    if not fileName:
        c.redraw()

    # Respect c's focus wishes if posssible.
    if w != c.frame.body.bodyCtrl and w != c.frame.tree.canvas:
        c.bodyWantsFocus()
        c.k.showStateAndMode(w)

    c.outerUpdate()
#@+node:ekr.20100914142850.5894: *4* make_screen_shot
def make_screen_shot(fn):

    '''Create a screenshot of the present Leo outline and save it to path.'''

    # g.trace('runLeo.py',fn)

    if g.app.gui.guiName() == 'qt':
        m = g.loadOnePlugin('screenshots')
        m.make_screen_shot(fn)
#@+node:ekr.20031218072017.1936: *3* isValidPython
def isValidPython():

    if sys.platform == 'cli':
        return True

    minimum_python_version = '2.6'

    message = """\
Leo requires Python %s or higher.
You may download Python from
http://python.org/download/
""" % minimum_python_version

    try:
        version = '.'.join([str(sys.version_info[i]) for i in (0,1,2)])
        ok = g.CheckVersion(version,minimum_python_version)
        if not ok:
            print(message)
            try:
                # g.app.gui does not exist yet.
                import Tkinter as Tk
                #@+<< define emergency dialog class >>
                #@+node:ekr.20080822065427.8: *4* << define emergency dialog class >>
                class emergencyDialog:

                    """A class that creates an Tkinter dialog with a single OK button."""

                    #@+others
                    #@+node:ekr.20080822065427.9: *5* __init__ (emergencyDialog)
                    def __init__(self,title,message):

                        """Constructor for the leoTkinterDialog class."""

                        self.answer = None # Value returned from run()
                        self.title = title
                        self.message=message

                        self.buttonsFrame = None # Frame to hold typical dialog buttons.
                        self.defaultButtonCommand = None
                            # Command to call when user closes the window
                            # by clicking the close box.
                        self.frame = None # The outermost frame.
                        self.root = None # Created in createTopFrame.
                        self.top = None # The toplevel Tk widget.

                        self.createTopFrame()
                        buttons = {"text":"OK","command":self.okButton,"default":True},
                            # Singleton tuple.
                        self.createButtons(buttons)
                        self.top.bind("<Key>", self.onKey)
                    #@+node:ekr.20080822065427.12: *5* createButtons
                    def createButtons (self,buttons):

                        """Create a row of buttons.

                        buttons is a list of dictionaries containing
                        the properties of each button."""

                        assert(self.frame)
                        self.buttonsFrame = f = Tk.Frame(self.top)
                        f.pack(side="top",padx=30)

                        # Buttons is a list of dictionaries, with an empty dictionary
                        # at the end if there is only one entry.
                        buttonList = []
                        for d in buttons:
                            text = d.get("text","<missing button name>")
                            isDefault = d.get("default",False)
                            underline = d.get("underline",0)
                            command = d.get("command",None)
                            bd = g.choose(isDefault,4,2)

                            b = Tk.Button(f,width=6,text=text,bd=bd,
                                underline=underline,command=command)
                            b.pack(side="left",padx=5,pady=10)
                            buttonList.append(b)

                            if isDefault and command:
                                self.defaultButtonCommand = command

                        return buttonList
                    #@+node:ekr.20080822065427.14: *5* createTopFrame
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
                    #@+node:ekr.20080822065427.10: *5* okButton
                    def okButton(self):

                        """Do default click action in ok button."""

                        self.top.destroy()
                        self.top = None

                    #@+node:ekr.20080822065427.21: *5* onKey
                    def onKey(self,event):

                        """Handle Key events in askOk dialogs."""

                        self.okButton()

                        return "break"
                    #@+node:ekr.20080822065427.16: *5* run
                    def run (self):

                        """Run the modal emergency dialog."""

                        self.top.geometry("%dx%d%+d%+d" % (300,200,50,50))
                        self.top.lift()

                        self.top.grab_set() # Make the dialog a modal dialog.
                        self.root.wait_window(self.top)
                    #@-others
                #@-<< define emergency dialog class >>
                d = emergencyDialog(
                    title='Python Version Error',
                    message=message)
                d.run()
            except Exception:
                pass
        return ok
    except Exception:
        print("isValidPython: unexpected exception: g.CheckVersion")
        traceback.print_exc()
        return 0
#@-others

if __name__ == "__main__":
    run()

#@-leo

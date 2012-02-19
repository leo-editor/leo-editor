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

import os
import optparse
import sys
import traceback

path = os.getcwd()
if path not in sys.path:
    # print('appending %s to sys.path' % path)
    sys.path.append(path)

# Import leoGlobals, but do NOT set g.
import leo.core.leoGlobals as leoGlobals

# Set leoGlobals.g here, not in leoGlobals.py.
leoGlobals.g = leoGlobals

# Create g.app.
import leo.core.leoApp as leoApp
leoGlobals.app = leoApp.LeoApp()

# **now** we can set g.
g = leoGlobals
assert(g.app)

# initApp does other imports...
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

    # print('runLeo.run: sys.argv %s' % sys.argv)

    # Always create the load manager.
    assert g.app
    g.app.loadManager = leoApp.LoadManager(fileName,pymacs)
    
    # Phase 1: before loading plugins.
    # Scan options, set directories and read settings.
    if not isValidPython(): return
    files,options = doPrePluginsInit(fileName,pymacs)
    if options.get('version'):
        print(g.app.signon)
        return
    if options.get('exit'):
        return

    # Phase 2: load plugins: the gui has already been set.
    g.doHook("start1")
    if g.app.killed: return

    # Phase 3: after loading plugins. Create one or more frames.
    screenshot_fn = options.get('screenshot_fn')
    ok = doPostPluginsInit(files,screenshot_fn)
        
    if ok:
        g.es('') # Clears horizontal scrolling in the log pane.
        g.app.gui.runMainLoop()
        # For scripts, the gui is a nullGui.
        # and the gui.setScript has already been called.
#@+node:ekr.20090519143741.5915: *3* doPrePluginsInit & helpers (runLeo.py)
def doPrePluginsInit(fileName,pymacs):

    ''' Scan options, set directories and read settings.'''

    trace = False
    g.computeStandardDirectories()
    adjustSysPath()
    
    # Scan the options as early as possible.
    options = scanOptions()
    if options.get('version'):
        g.app.computeSignon()
        return [],options

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
    
    if g.new_config:
        lm = g.app.loadManager
        lm.init(files) #### Temporary: set lm.files
        lm.readGlobalSettingsFiles()
            # reads only standard settings files, using a null gui.
            # uses lm.files[0] to compute the local directory
            # that might contain myLeoSettings.leo.
    else:
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
    
    # Create the gui after reading options and settings.
    createGui(pymacs,options)

    # We can't print the signon until we know the gui.
    g.app.computeSignon() # Set app.signon/signon2 for commanders.
    versionFlag = options.get('versionFlag')
    if versionFlag:
        print(g.app.signon)
    if versionFlag or not g.app.gui:
        options['exit'] = True

    return files,options
#@+node:ekr.20100914142850.5892: *4* createGui (runLeo.py)
def createGui(pymacs,options):
    
    trace = (False or g.trace_startup) and not g.unitTesting
    if trace: print('\n==================== runLeo.py.createGui')

    gui_option = options.get('gui')
    windowFlag = options.get('windowFlag')
    script = options.get('script')

    if g.app.gui:
        if g.new_config:
            import leo.core.leoGui as leoGui
            assert isinstance(g.app.gui,leoGui.nullGui)
            g.app.gui = None # Enable g.app.createDefaultGui 
            g.app.createDefaultGui(__file__)
        else:
            pass # setLeoID created the gui.
            
    elif gui_option is None:
        if script and not windowFlag:
            # Always use null gui for scripts.
            g.app.createNullGuiWithScript(script)
        else:
            g.app.createDefaultGui(__file__)
    else:
        createSpecialGui(gui_option,pymacs,script,windowFlag)
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
        # assert g.app.guiArgName
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

    fileName = g.toUnicode(fileName)
    fileName = g.os_path_finalize(fileName)

    # 2011/10/12: don't add .leo to *any* file.
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
#@+node:ekr.20080921091311.2: *4* initApp (runLeo.py)
def initApp (verbose):
    
    assert g.app.loadManager
    
    import leo.core.leoConfig as leoConfig
    import leo.core.leoNodes as leoNodes
    import leo.core.leoPlugins as leoPlugins
    
    # Make sure we call the new leoPlugins.init top-level function.
    # This prevents a crash when run is called repeatedly from
    # IPython's lleo extension.
    leoPlugins.init()
    
    # Force the user to set g.app.leoID.
    g.app.setLeoID(verbose=verbose)
    
    # Create early classes *after* doing plugins.init()
    g.app.config = leoConfig.configClass()
    g.app.nodeIndices = leoNodes.nodeIndices(g.app.leoID)

    # Complete the plugins class last.
    g.app.pluginsController.finishCreate()
#@+node:ekr.20041130093254: *4* reportDirectories (runLeo.py)
def reportDirectories(verbose):

    if verbose:
        for kind,theDir in (
            ("load",g.app.loadDir),
            ("global config",g.app.globalConfigDir),
            ("home",g.app.homeDir),
        ):
            g.es("%s dir:" % (kind),theDir,color="blue")
#@+node:ekr.20091007103358.6061: *4* scanOptions (runLeo.py)
def scanOptions():

    '''Handle all options and remove them from sys.argv.'''
    trace = False
    
    # print('scanOptions',sys.argv)

    # Note: this automatically implements the --help option.
    parser = optparse.OptionParser()
    add = parser.add_option
    
    #### To be removed.
    # add('-c', '--config', dest="one_config_path",
        # help = 'use a single configuration file')
    # add('--debug',        action="store_true",dest="debug",
        # help = 'enable debugging support')
    # add('-f', '--file',   dest="fileName",
        # help = 'load a file at startup')
    add('--gui',
        help = 'gui to use (qt/qttabs)')
    add('--minimized',    action="store_true",
        help = 'start minimized')
    add('--maximized',    action="store_true",
        help = 'start maximized (Qt only)')
    add('--fullscreen',   action="store_true",
        help = 'start fullscreen (Qt only)')
    add('--ipython',      action="store_true",dest="use_ipython",
        help = 'enable ipython support')
    add('--no-cache',     action="store_true",dest='no_cache',
        help = 'disable reading of cached files')
    add('--no-splash',    action="store_true",dest='no_splash_screen',
        help = 'disable the splash screen')
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
    
    ####
    # path = options.one_config_path
    # if path:
        # path = g.os_path_finalize_join(os.getcwd(),path)
        # if g.os_path_exists(path):
            # g.app.oneConfigFilename = path
        # else:
            # g.es_print('Invalid -c option: file not found:',path,color='red')

    # --debug
    ####
    # if options.debug:
        # g.debug = True
        # print('scanOptions: *** debug mode on')

    # -f or --file
    ####
    # fileName = options.fileName
    # if fileName:
        # fileName = fileName.strip('"')
        # if trace: print('scanOptions:',fileName)

    # --gui
    gui = options.gui

    if gui:
        gui = gui.lower()
        if gui == 'qttabs':
            g.app.qt_use_tabs = True
        elif gui in ('curses','qt','null'):
            g.app.qt_use_tabs = False
        else:
            print('scanOptions: unknown gui: %s.  Using qt gui' % gui)
            gui = 'qt'
            g.app.qt_use_tabs = False
    elif sys.platform == 'darwin':
        gui = 'qt'
        g.app.qt_use_tabs = False
    else:
        gui = 'qttabs'
        g.app.qt_use_tabs = True

    assert gui
    g.app.guiArgName = gui # 2011/06/15

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
        if trace: print('scanOptions: disabling caching')
        g.enableDB = False
        
    # --no-splash
    # g.trace('--no-splash',options.no_splash_screen)
    g.app.use_splash_screen = not options.no_splash_screen

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
            g.trace('bad --window-size:',windowSize)

    # Compute the return values.
    windowFlag = script and script_path_w
    d = {
        'fileName': None, #### fileName,
        'gui':gui,
        'screenshot_fn':screenshot_fn,
        'script':script,
        'select':select,
        'version':versionFlag,
        'windowFlag':windowFlag,
        'windowSize':windowSize,
    }
    return d
#@+node:ekr.20090519143741.5917: *3* doPostPluginsInit & helpers (runLeo.py)
def doPostPluginsInit(files,screenshot_fn):

    '''Create a Leo window for each file in the files list.'''

    # Clear g.app.initing _before_ creating commanders.
    g.app.initing = False # "idle" hooks may now call g.app.forceShutdown.

    # Create the main frame.  Show it and all queued messages.
    
    if files:
        c1 = None
        for fn in files:
            c = g.openWithFileName(fn,old_c=None,force=True)
                # Will give a "not found" message.
            assert c
            if not c1: c1 = c
    else:
        # Create an empty frame.
        c1 = g.openWithFileName(None,old_c=None,force=True)
            
    # Put the focus in the first-opened file.
    fileName = files[0] if files else None
    c = c1
            
    # For qttabs gui, select the first-loaded tab.
    if hasattr(g.app.gui,'frameFactory'):
        factory = g.app.gui.frameFactory
        if factory and hasattr(factory,'setTabForCommander'):
            factory.setTabForCommander(c)

    # Do the final inits.
    g.app.logInited = True
    g.app.initComplete = True
    c.setLog()
    g.doHook("start2",c=c,p=c.p,v=c.p,fileName=fileName)
    g.enableIdleTimeHook(idleTimeDelay=500)
    initFocusAndDraw(c,fileName)

    if screenshot_fn:
        make_screen_shot(screenshot_fn)
        return False # Force an immediate exit.

    return True
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
#@+node:ekr.20120208064440.14030: *3* Common helpers
#@+node:ekr.20031218072017.1936: *3* isValidPython & emergency (Tk) dialog class
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

                        return # (for Tk) "break"
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

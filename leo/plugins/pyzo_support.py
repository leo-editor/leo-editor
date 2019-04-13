# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190410171646.1: * @file pyzo_support.py
#@@first
'''
pyzo_support.py: Allow access to pyzo features within Leo.

This plugin is active only if pyzo modules import successfully.

To do:
    1. Support pyzo file browser.
    2. Support pyzo shell & debugger.
'''
#@+<< copyright >>
#@+node:ekr.20190412042616.1: ** << copyright >>
#@+at
# This file uses code from pyzo. Here is the pyzo copyright notice:
# 
# Copyright (C) 2013-2018, the Pyzo development team
# 
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
# 
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< copyright >>
import sys
import leo.core.leoGlobals as g
#@+<< set switches >>
#@+node:ekr.20190410200749.1: ** << set switches >>
#
# Only my personal copy of pyzo supports these switches:
#
# --pyzo is part 1 of the two-step enabling of traces.
#
# The unpatch pyzo will say that the file '--pyzo' does not exist.
if '--pyzo' not in sys.argv:
    sys.argv.append('--pyzo')
#
# These switches are part 2 of two-step enabling of traces.
# My personal copy of pyzo uses `getattr(g, 'switch_name', None)`
# to avoid crashes in case these vars do not exist.
g.pyzo = True
g.pyzo_pdb = False
g.pyzo_trace = True
g.pyzo_trace_imports = True
#@-<< set switches >>
#@+others
#@+node:ekr.20190410171905.1: ** function: init
def init():
    '''Return True if the plugin has loaded successfully.'''
    if g.app.gui.guiName() != "qt":
        print('pyzo_support.py requires Qt gui')
        return False
    if not is_pyzo_loaded():
        print('pyzo_support.py requires pyzo')
        return False
    g.plugin_signon(__name__)
    # g.registerHandler('after-create-leo-frame',onCreate)
    return True
#@+node:ekr.20190410200453.1: ** function: is_pyzo_loaded
def is_pyzo_loaded():
    '''
    Return True if pyzo appears to be loaded,
    using the "lightest" possible imports.
    '''
    try:
        import pyzo
        assert pyzo
        from pyzo.tools import ToolManager
        assert ToolManager
        # Be explicit about where everything comes from...
            # import pyzo
            # import pyzo.core.editor
            # import pyzo.core.main
            # import pyzo.core.splash
            # import pyzo.util
        return True
    except Exception:
        g.es_exception()
        g.pyzo = False
        g.pyzo_trace = False
        g.pyzo_trace_imports = False
        return False
#@+node:ekr.20190413060717.1: ** function: import_pyzo
def import_pyzo():

    import sys
    use_main = False
    #@+<< set g.pyzo switches >>
    #@+node:ekr.20190413060813.2: *3* << set g.pyzo switches >>
    if '--pyzo' not in sys.argv:
        sys.argv.append('--pyzo')
    g.pyzo = True
    g.pyzo_pdb = False
    g.pyzo_trace = True
    g.pyzo_trace_imports = True
    #@-<< set g.pyzo switches >>
    try:
        if use_main:
            from pyzo.__main__ import main
        else:
            #@+<< pyzo/__init__.py imports >>
            #@+node:ekr.20190413060813.3: *3* << pyzo/__init__.py imports >>
            import os
            # import sys #EKR: imported above.
            import locale
            import traceback

            # Check Python version
            if sys.version < '3':
                raise RuntimeError('Pyzo requires Python 3.x to run.')

            # Make each OS find platform plugins etc.
            if hasattr(sys, 'frozen') and sys.frozen:
                app_dir = os.path.dirname(sys.executable)
                if sys.platform.startswith('win'):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = app_dir
                if sys.platform.startswith('linux'):
                    os.environ['QT_XKB_CONFIG_ROOT'] = '.'
                    os.environ['FONTCONFIG_FILE'] = os.path.join(
                        app_dir,
                        'source/pyzo/resources',
                        'fonts/linux_fonts.conf')

            # Import yoton as an absolute package
            from pyzo import yotonloader  # noqa
                # Inserts directory of yotonloader into sys.argv.
            from pyzo.util import paths

            # If there already is an instance of Pyzo, and the user is trying an
            # Pyzo command, we should send the command to the other process and quit.
            # We do this here, were we have not yet loaded Qt, so we are very light.
            from pyzo.core import commandline
            if commandline.is_our_server_running():
                print('Started our command server')
            else:
                # Handle command line args now
                res = commandline.handle_cmd_args()
                if res:
                    print(res)
                    sys.exit()
                else:
                    # No args, proceed with starting up
                    print('Our command server is *not* running')

            from pyzo.util import zon as ssdf  # zon is ssdf-light
            from pyzo.util.qt import QtCore, QtGui, QtWidgets

            # Import language/translation tools
            from pyzo.util._locale import translate, setLanguage  # noqa
            #@-<< pyzo/__init__.py imports >>
            #@+<< pyzo.__init__.py early bindings >>
            #@+node:ekr.20190413060813.4: *3* << pyzo.__init__.py early bindings >>
            # Set environ to let kernel know some stats about us
            os.environ['PYZO_PREFIX'] = sys.prefix
            _is_pyqt4 = hasattr(QtCore, 'PYQT_VERSION_STR')
            os.environ['PYZO_QTLIB'] = 'PyQt4' if _is_pyqt4 else 'PySide'
            #@-<< pyzo.__init__.py early bindings >>
            #@+others
            #@+node:ekr.20190413060813.5: *3* disabled
            if 0:
                #@+others
                #@+node:ekr.20190413060813.6: *4* pyzo_excepthook
                ## Install excepthook
                # In PyQt5 exceptions in Python will cuase an abort
                # http://pyqt.sourceforge.net/Docs/PyQt5/incompatibilities.html
                def pyzo_excepthook(type, value, tb):
                    out = 'Uncaught Python exception: ' + str(value) + '\n'
                    out += ''.join(traceback.format_list(traceback.extract_tb(tb)))
                    out += '\n'
                    sys.stderr.write(out)

                sys.excepthook = pyzo_excepthook
                #@+node:ekr.20190413060813.7: *4* resetConfig
                def resetConfig(preserveState=True):
                    """ resetConfig()
                    Deletes the config file to revert to default and prevent Pyzo from storing
                    its config on the next shutdown.
                    """
                    # Get filenames
                    configFileName2 = os.path.join(appDataDir, 'config.ssdf')
                    os.remove(configFileName2)
                    global _saveConfigFile
                    _saveConfigFile = False
                    print("Deleted user config file. Restart Pyzo to revert to the default config.")
                #@+node:ekr.20190413060813.8: *4* saveConfig (pyzo.__init__.py)
                def saveConfig():
                    """ saveConfig()
                    Save all configureations to file.
                    """

                    # Let the editorStack save its state
                    if editors:
                        editors.saveEditorState()

                    # Let the main window save its state
                    if main:
                        main.saveWindowState()

                    # Store config
                    if _saveConfigFile:
                        ssdf.save( os.path.join(appDataDir, "config.ssdf"), config )
                #@-others
            #@+node:ekr.20190413060813.9: *3* class MyApp(QtWidgets.QApplication)
            class MyApp(QtWidgets.QApplication):
                """ So we an open .py files on OSX.
                OSX is smart enough to call this on the existing process.
                """
                #@+others
                #@+node:ekr.20190413060813.10: *4* MyApp.event
                def event(self, event):
                    if isinstance(event, QtGui.QFileOpenEvent):
                        fname = str(event.file())
                        if fname and fname != 'pyzo':
                            sys.argv[1:] = []
                            sys.argv.append(fname)
                            res = commandline.handle_cmd_args()
                            if not commandline.is_our_server_running():
                                print(res)
                                sys.exit()
                    return QtWidgets.QApplication.event(self, event)
                #@-others
                
            assert MyApp ### pyflakes

            if not sys.platform.startswith('darwin'):
                MyApp = QtWidgets.QApplication  # noqa
            #@+node:ekr.20190413060813.11: *3* getResourceDirs
            def getResourceDirs():
                """ getResourceDirs()
                Get the directories to the resources: (pyzoDir, appDataDir).
                Also makes sure that the appDataDir has a "tools" directory and
                a style file.
                """

                #   # Get root of the Pyzo code. If frozen its in a subdir of the app dir
                #   pyzoDir = paths.application_dir()
                #   if paths.is_frozen():
                #       pyzoDir = os.path.join(pyzoDir, 'source')
                if 1:
                    ### Hack
                    g.trace('using static pyzoDir')
                    pyzoDir = r'C:\apps\pyzo\source\pyzo'
                else:
                    pyzoDir = os.path.abspath(os.path.dirname(__file__))
                if '.zip' in pyzoDir:
                    raise RuntimeError('The Pyzo package cannot be run from a zipfile.')

                # Get where the application data is stored (use old behavior on Mac)
                appDataDir = paths.appdata_dir('pyzo', roaming=True, macAsLinux=True)

                # Create tooldir if necessary
                toolDir = os.path.join(appDataDir, 'tools')
                if not os.path.isdir(toolDir):
                    os.mkdir(toolDir)

                return pyzoDir, appDataDir
            #@+node:ekr.20190413060813.12: *3* loadConfig (pyzo.__init__.py)
            def loadConfig(defaultsOnly=False):
                """ loadConfig(defaultsOnly=False)
                Load default and site-wide configuration file(s) and that of the user (if it exists).
                Any missing fields in the user config are set to the defaults.
                """

                # Function to insert names from one config in another
                def replaceFields(base, new):
                    for key in new:
                        if key in base and isinstance(base[key], ssdf.Struct):
                            replaceFields(base[key], new[key])
                        else:
                            base[key] = new[key]

                # Reset our pyzo.config structure
                ssdf.clear(config)

                # Load default and inject in the pyzo.config
                fname = os.path.join(pyzoDir, 'resources', 'defaultConfig.ssdf')
                defaultConfig = ssdf.load(fname)
                replaceFields(config, defaultConfig)

                # Platform specific keybinding: on Mac, Ctrl+Tab (actually Cmd+Tab) is a system shortcut
                if sys.platform == 'darwin':
                    config.shortcuts2.view__select_previous_file = 'Alt+Tab,'

                # Load site-wide config if it exists and inject in pyzo.config
                fname = os.path.join(pyzoDir, 'resources', 'siteConfig.ssdf')
                if os.path.isfile(fname):
                    try:
                        siteConfig = ssdf.load(fname)
                        replaceFields(config, siteConfig)
                    except Exception:
                        t = 'Error while reading config file %r, maybe its corrupt?'
                        print(t % fname)
                        raise

                # Load user config and inject in pyzo.config
                fname = os.path.join(appDataDir, "config.ssdf")
                if os.path.isfile(fname):
                    try:
                        userConfig = ssdf.load(fname)
                        replaceFields(config, userConfig)
                    except Exception:
                        t = 'Error while reading config file %r, maybe its corrupt?'
                        print(t % fname)
                        raise
            #@+node:ekr.20190413060813.13: *3* start (pyzo.__init__.py) (starts logging)
            def start():
                """ Run Pyzo.
                """
                if g and getattr(g, 'pyzo_trace', None):
                    print('==== pyzo/__init__.py:start')

                # Do some imports
                from pyzo.core import pyzoLogging  # noqa - to start logging asap
                assert pyzoLogging ### pyflakes
                from pyzo.core.main import MainWindow
                # print('start (__init__.py)') # EKR: prints to stdout *and* log.

                # Apply users' preferences w.r.t. date representation etc
                # this is required for e.g. strftime("%c")
                # Just using '' does not seem to work on OSX. Thus
                # this odd loop.
                #locale.setlocale(locale.LC_ALL, "")
                for x in ('', 'C', 'en_US', 'en_US.utf8', 'en_US.UTF-8'):
                    try:
                        locale.setlocale(locale.LC_ALL, x)
                        break
                    except locale.Error:
                        pass

                # Set to be aware of the systems native colors, fonts, etc.
                QtWidgets.QApplication.setDesktopSettingsAware(True)
                
                # Instantiate the application.
                QtWidgets.qApp = MyApp(sys.argv)  # QtWidgets.QApplication([])

                # Choose language, get locale
                appLocale = setLanguage(config.settings.language)

                # Create main window, using the selected locale
                MainWindow(None, appLocale)

                # Enter the main loop
                QtWidgets.qApp.exec_()
            #@-others
            #@+<< pyzo.__init__.py late bindings >>
            #@+node:ekr.20190413060813.14: *3* << pyzo.__init__.py late bindings >>
            ## Init

            # List of names that are later overriden (in main.py)
            editors = None # The editor stack instance
            shells = None # The shell stack instance
            main = None # The mainwindow
            icon = None # The icon
            parser = None # The source parser
            status = None # The statusbar (or None)

            # Get directories of interest
            pyzoDir, appDataDir = getResourceDirs()

            # Whether the config file should be saved
            _saveConfigFile = True

            # Create ssdf in module namespace, and fill it
            config = ssdf.new()
            loadConfig()

            # Init default style name (set in main.restorePyzoState())
            defaultQtStyleName = ''

            #@-<< pyzo.__init__.py late bindings >>
            #@+<< keep pyflakes happy >>
            #@+node:ekr.20190413060813.15: *3* << keep pyflakes happy >>
            if 0:
                # Imports...
                print(translate)
                print(yotonloader)
                
                # Module vars...
                print(defaultQtStyleName)
                print(parser)
                print(icon)
                print(shells)
                print(status)
                # print(pyzo.core.logging)
            #@-<< keep pyflakes happy >>
        g.trace('Done')
    except Exception:
        g.es_exception()
#@+node:ekr.20190413055311.1: ** function: start_pyzo
def start_pyzo():

    import sys
    use_main = False
    #@+<< set g.pyzo switches >>
    #@+node:ekr.20190413055331.2: *3* << set g.pyzo switches >>
    if '--pyzo' not in sys.argv:
        sys.argv.append('--pyzo')
    g.pyzo = True
    g.pyzo_pdb = False
    g.pyzo_trace = True
    g.pyzo_trace_imports = True
    #@-<< set g.pyzo switches >>
    try:
        if use_main:
            from pyzo.__main__ import main
            main()
        else:
            #@+<< pyzo/__init__.py imports >>
            #@+node:ekr.20190413055331.3: *3* << pyzo/__init__.py imports >>
            import os
            # import sys #EKR: imported above.
            import locale
            import traceback

            # Check Python version
            if sys.version < '3':
                raise RuntimeError('Pyzo requires Python 3.x to run.')

            # Make each OS find platform plugins etc.
            if hasattr(sys, 'frozen') and sys.frozen:
                app_dir = os.path.dirname(sys.executable)
                if sys.platform.startswith('win'):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = app_dir
                if sys.platform.startswith('linux'):
                    os.environ['QT_XKB_CONFIG_ROOT'] = '.'
                    os.environ['FONTCONFIG_FILE'] = os.path.join(
                        app_dir,
                        'source/pyzo/resources',
                        'fonts/linux_fonts.conf')

            # Import yoton as an absolute package
            from pyzo import yotonloader  # noqa
                # Inserts directory of yotonloader into sys.argv.
            from pyzo.util import paths

            # If there already is an instance of Pyzo, and the user is trying an
            # Pyzo command, we should send the command to the other process and quit.
            # We do this here, were we have not yet loaded Qt, so we are very light.
            from pyzo.core import commandline
            if commandline.is_our_server_running():
                print('Started our command server')
            else:
                # Handle command line args now
                res = commandline.handle_cmd_args()
                if res:
                    print(res)
                    sys.exit()
                else:
                    # No args, proceed with starting up
                    print('Our command server is *not* running')

            from pyzo.util import zon as ssdf  # zon is ssdf-light
            from pyzo.util.qt import QtCore, QtGui, QtWidgets

            # Import language/translation tools
            from pyzo.util._locale import translate, setLanguage  # noqa
            #@-<< pyzo/__init__.py imports >>
            #@+<< pyzo.__init__.py early bindings >>
            #@+node:ekr.20190413055331.4: *3* << pyzo.__init__.py early bindings >>
            # Set environ to let kernel know some stats about us
            os.environ['PYZO_PREFIX'] = sys.prefix
            _is_pyqt4 = hasattr(QtCore, 'PYQT_VERSION_STR')
            os.environ['PYZO_QTLIB'] = 'PyQt4' if _is_pyqt4 else 'PySide'
            #@-<< pyzo.__init__.py early bindings >>
            #@+others
            #@+node:ekr.20190413055331.7: *3* disabled
            if 0:
                #@+others
                #@+node:ekr.20190413055331.8: *4* pyzo_excepthook
                ## Install excepthook
                # In PyQt5 exceptions in Python will cuase an abort
                # http://pyqt.sourceforge.net/Docs/PyQt5/incompatibilities.html
                def pyzo_excepthook(type, value, tb):
                    out = 'Uncaught Python exception: ' + str(value) + '\n'
                    out += ''.join(traceback.format_list(traceback.extract_tb(tb)))
                    out += '\n'
                    sys.stderr.write(out)

                sys.excepthook = pyzo_excepthook
                #@+node:ekr.20190413055331.9: *4* resetConfig
                def resetConfig(preserveState=True):
                    """ resetConfig()
                    Deletes the config file to revert to default and prevent Pyzo from storing
                    its config on the next shutdown.
                    """
                    # Get filenames
                    configFileName2 = os.path.join(appDataDir, 'config.ssdf')
                    os.remove(configFileName2)
                    global _saveConfigFile
                    _saveConfigFile = False
                    print("Deleted user config file. Restart Pyzo to revert to the default config.")
                #@+node:ekr.20190413055331.10: *4* saveConfig (pyzo.__init__.py)
                def saveConfig():
                    """ saveConfig()
                    Save all configureations to file.
                    """

                    # Let the editorStack save its state
                    if editors:
                        editors.saveEditorState()

                    # Let the main window save its state
                    if main:
                        main.saveWindowState()

                    # Store config
                    if _saveConfigFile:
                        ssdf.save( os.path.join(appDataDir, "config.ssdf"), config )
                #@-others
            #@+node:ekr.20190413055331.11: *3* class MyApp(QtWidgets.QApplication)
            class MyApp(QtWidgets.QApplication):
                """ So we an open .py files on OSX.
                OSX is smart enough to call this on the existing process.
                """
                #@+others
                #@+node:ekr.20190413055331.12: *4* MyApp.event
                def event(self, event):
                    if isinstance(event, QtGui.QFileOpenEvent):
                        fname = str(event.file())
                        if fname and fname != 'pyzo':
                            sys.argv[1:] = []
                            sys.argv.append(fname)
                            res = commandline.handle_cmd_args()
                            if not commandline.is_our_server_running():
                                print(res)
                                sys.exit()
                    return QtWidgets.QApplication.event(self, event)
                #@-others
                
            assert MyApp ### pyflakes

            if not sys.platform.startswith('darwin'):
                MyApp = QtWidgets.QApplication  # noqa
            #@+node:ekr.20190413055331.13: *3* getResourceDirs
            def getResourceDirs():
                """ getResourceDirs()
                Get the directories to the resources: (pyzoDir, appDataDir).
                Also makes sure that the appDataDir has a "tools" directory and
                a style file.
                """

                #   # Get root of the Pyzo code. If frozen its in a subdir of the app dir
                #   pyzoDir = paths.application_dir()
                #   if paths.is_frozen():
                #       pyzoDir = os.path.join(pyzoDir, 'source')
                if 1:
                    ### Hack
                    g.trace('using static pyzoDir')
                    pyzoDir = r'C:\apps\pyzo\source\pyzo'
                else:
                    pyzoDir = os.path.abspath(os.path.dirname(__file__))
                if '.zip' in pyzoDir:
                    raise RuntimeError('The Pyzo package cannot be run from a zipfile.')

                # Get where the application data is stored (use old behavior on Mac)
                appDataDir = paths.appdata_dir('pyzo', roaming=True, macAsLinux=True)

                # Create tooldir if necessary
                toolDir = os.path.join(appDataDir, 'tools')
                if not os.path.isdir(toolDir):
                    os.mkdir(toolDir)

                return pyzoDir, appDataDir
            #@+node:ekr.20190413055331.14: *3* loadConfig (pyzo.__init__.py)
            def loadConfig(defaultsOnly=False):
                """ loadConfig(defaultsOnly=False)
                Load default and site-wide configuration file(s) and that of the user (if it exists).
                Any missing fields in the user config are set to the defaults.
                """

                # Function to insert names from one config in another
                def replaceFields(base, new):
                    for key in new:
                        if key in base and isinstance(base[key], ssdf.Struct):
                            replaceFields(base[key], new[key])
                        else:
                            base[key] = new[key]

                # Reset our pyzo.config structure
                ssdf.clear(config)

                # Load default and inject in the pyzo.config
                fname = os.path.join(pyzoDir, 'resources', 'defaultConfig.ssdf')
                defaultConfig = ssdf.load(fname)
                replaceFields(config, defaultConfig)

                # Platform specific keybinding: on Mac, Ctrl+Tab (actually Cmd+Tab) is a system shortcut
                if sys.platform == 'darwin':
                    config.shortcuts2.view__select_previous_file = 'Alt+Tab,'

                # Load site-wide config if it exists and inject in pyzo.config
                fname = os.path.join(pyzoDir, 'resources', 'siteConfig.ssdf')
                if os.path.isfile(fname):
                    try:
                        siteConfig = ssdf.load(fname)
                        replaceFields(config, siteConfig)
                    except Exception:
                        t = 'Error while reading config file %r, maybe its corrupt?'
                        print(t % fname)
                        raise

                # Load user config and inject in pyzo.config
                fname = os.path.join(appDataDir, "config.ssdf")
                if os.path.isfile(fname):
                    try:
                        userConfig = ssdf.load(fname)
                        replaceFields(config, userConfig)
                    except Exception:
                        t = 'Error while reading config file %r, maybe its corrupt?'
                        print(t % fname)
                        raise
            #@+node:ekr.20190413055331.15: *3* start (pyzo.__init__.py) (starts logging)
            def start():
                """ Run Pyzo.
                """
                if g and getattr(g, 'pyzo_trace', None):
                    print('==== pyzo/__init__.py:start')

                # Do some imports
                from pyzo.core import pyzoLogging  # noqa - to start logging asap
                assert pyzoLogging ### pyflakes
                from pyzo.core.main import MainWindow
                # print('start (__init__.py)') # EKR: prints to stdout *and* log.

                # Apply users' preferences w.r.t. date representation etc
                # this is required for e.g. strftime("%c")
                # Just using '' does not seem to work on OSX. Thus
                # this odd loop.
                #locale.setlocale(locale.LC_ALL, "")
                for x in ('', 'C', 'en_US', 'en_US.utf8', 'en_US.UTF-8'):
                    try:
                        locale.setlocale(locale.LC_ALL, x)
                        break
                    except locale.Error:
                        pass

                # Set to be aware of the systems native colors, fonts, etc.
                QtWidgets.QApplication.setDesktopSettingsAware(True)
                
                # Instantiate the application.
                QtWidgets.qApp = MyApp(sys.argv)  # QtWidgets.QApplication([])

                # Choose language, get locale
                appLocale = setLanguage(config.settings.language)

                # Create main window, using the selected locale
                MainWindow(None, appLocale)

                # Enter the main loop
                QtWidgets.qApp.exec_()
            #@-others
            #@+<< pyzo.__init__.py late bindings >>
            #@+node:ekr.20190413055331.5: *3* << pyzo.__init__.py late bindings >>
            ## Init

            # List of names that are later overriden (in main.py)
            editors = None # The editor stack instance
            shells = None # The shell stack instance
            main = None # The mainwindow
            icon = None # The icon
            parser = None # The source parser
            status = None # The statusbar (or None)

            # Get directories of interest
            pyzoDir, appDataDir = getResourceDirs()

            # Whether the config file should be saved
            _saveConfigFile = True

            # Create ssdf in module namespace, and fill it
            config = ssdf.new()
            loadConfig()

            # Init default style name (set in main.restorePyzoState())
            defaultQtStyleName = ''

            #@-<< pyzo.__init__.py late bindings >>
            #@+<< keep pyflakes happy >>
            #@+node:ekr.20190413055620.1: *3* << keep pyflakes happy >>
            if 0:
                # Imports...
                print(translate)
                print(yotonloader)
                
                # Module vars...
                print(defaultQtStyleName)
                print(parser)
                print(icon)
                print(shells)
                print(status)
                # print(pyzo.core.logging)
            #@-<< keep pyflakes happy >>
            start() # __main__.py: main just calls pyzo.start.
        g.trace('Done')
    except Exception:
        g.es_exception()

    
    
#@+node:ekr.20190413074155.1: ** function: open_file_browser
# function: open_file_browser
class ConfigShim(object):
    pass

def open_file_browser(use_main_imports, use_pyzo_config, use_pyzo_logging):
    '''A test bed for importing pyzo's file browser.'''
    # Prefer explicit imports to implicit.
    import sys
    #@+<< set g.pyzo switches >>
    #@+node:ekr.20190413074155.3: *3* << set g.pyzo switches >>
    if '--pyzo' not in sys.argv:
        sys.argv.append('--pyzo')
    g.pyzo = True
    g.pyzo_pdb = False
    g.pyzo_trace = True
    g.pyzo_trace_imports = True
    #@-<< set g.pyzo switches >>
    try:
        if use_main_imports:
            from pyzo.__main__ import main
        else:
            #@+<< pyzo/__init__.py imports >>
            #@+node:ekr.20190413074155.4: *3* << pyzo/__init__.py imports >>
            import os
            # import sys #EKR: imported above.
            import locale
            import traceback

            # Check Python version
            if sys.version < '3':
                raise RuntimeError('Pyzo requires Python 3.x to run.')

            # Make each OS find platform plugins etc.
            if hasattr(sys, 'frozen') and sys.frozen:
                app_dir = os.path.dirname(sys.executable)
                if sys.platform.startswith('win'):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = app_dir
                if sys.platform.startswith('linux'):
                    os.environ['QT_XKB_CONFIG_ROOT'] = '.'
                    os.environ['FONTCONFIG_FILE'] = os.path.join(
                        app_dir,
                        'source/pyzo/resources',
                        'fonts/linux_fonts.conf')

            # Import yoton as an absolute package
            from pyzo import yotonloader  # noqa
                # Inserts directory of yotonloader into sys.argv.
            from pyzo.util import paths

            # If there already is an instance of Pyzo, and the user is trying an
            # Pyzo command, we should send the command to the other process and quit.
            # We do this here, were we have not yet loaded Qt, so we are very light.
            from pyzo.core import commandline
            if commandline.is_our_server_running():
                print('Started our command server')
            else:
                # Handle command line args now
                res = commandline.handle_cmd_args()
                if res:
                    print(res)
                    sys.exit()
                else:
                    # No args, proceed with starting up
                    print('Our command server is *not* running')

            from pyzo.util import zon as ssdf  # zon is ssdf-light
            from pyzo.util.qt import QtCore, QtGui, QtWidgets

            # Import language/translation tools
            from pyzo.util._locale import translate, setLanguage  # noqa
            #@-<< pyzo/__init__.py imports >>
            #@+<< pyzo.__init__.py early bindings >>
            #@+node:ekr.20190413074155.5: *3* << pyzo.__init__.py early bindings >>
            # Set environ to let kernel know some stats about us
            os.environ['PYZO_PREFIX'] = sys.prefix
            _is_pyqt4 = hasattr(QtCore, 'PYQT_VERSION_STR')
            os.environ['PYZO_QTLIB'] = 'PyQt4' if _is_pyqt4 else 'PySide'
            #@-<< pyzo.__init__.py early bindings >>
            #@+others
            #@+node:ekr.20190413074155.12: *3* getResourceDirs
            def getResourceDirs():
                """ getResourceDirs()
                Get the directories to the resources: (pyzoDir, appDataDir).
                Also makes sure that the appDataDir has a "tools" directory and
                a style file.
                """

                #   # Get root of the Pyzo code. If frozen its in a subdir of the app dir
                #   pyzoDir = paths.application_dir()
                #   if paths.is_frozen():
                #       pyzoDir = os.path.join(pyzoDir, 'source')
                if 1:
                    ### Hack
                    g.trace('using static pyzoDir')
                    pyzoDir = r'C:\apps\pyzo\source\pyzo'
                else:
                    pyzoDir = os.path.abspath(os.path.dirname(__file__))
                if '.zip' in pyzoDir:
                    raise RuntimeError('The Pyzo package cannot be run from a zipfile.')

                # Get where the application data is stored (use old behavior on Mac)
                appDataDir = paths.appdata_dir('pyzo', roaming=True, macAsLinux=True)

                # Create tooldir if necessary
                toolDir = os.path.join(appDataDir, 'tools')
                if not os.path.isdir(toolDir):
                    os.mkdir(toolDir)

                return pyzoDir, appDataDir
            #@+node:ekr.20190413074155.13: *3* loadConfig (pyzo.__init__.py)
            def loadConfig(defaultsOnly=False):
                """ loadConfig(defaultsOnly=False)
                Load default and site-wide configuration file(s) and that of the user (if it exists).
                Any missing fields in the user config are set to the defaults.
                """

                # Function to insert names from one config in another
                def replaceFields(base, new):
                    for key in new:
                        if key in base and isinstance(base[key], ssdf.Struct):
                            replaceFields(base[key], new[key])
                        else:
                            base[key] = new[key]

                # Reset our pyzo.config structure
                ssdf.clear(config)

                # Load default and inject in the pyzo.config
                fname = os.path.join(pyzoDir, 'resources', 'defaultConfig.ssdf')
                defaultConfig = ssdf.load(fname)
                replaceFields(config, defaultConfig)

                # Platform specific keybinding: on Mac, Ctrl+Tab (actually Cmd+Tab) is a system shortcut
                if sys.platform == 'darwin':
                    config.shortcuts2.view__select_previous_file = 'Alt+Tab,'

                # Load site-wide config if it exists and inject in pyzo.config
                fname = os.path.join(pyzoDir, 'resources', 'siteConfig.ssdf')
                if os.path.isfile(fname):
                    try:
                        siteConfig = ssdf.load(fname)
                        replaceFields(config, siteConfig)
                    except Exception:
                        t = 'Error while reading config file %r, maybe its corrupt?'
                        print(t % fname)
                        raise

                # Load user config and inject in pyzo.config
                fname = os.path.join(appDataDir, "config.ssdf")
                if os.path.isfile(fname):
                    try:
                        userConfig = ssdf.load(fname)
                        replaceFields(config, userConfig)
                    except Exception:
                        t = 'Error while reading config file %r, maybe its corrupt?'
                        print(t % fname)
                        raise
            #@-others
            #@+<< pyzo.__init__.py late bindings >>
            #@+node:ekr.20190413074155.6: *3* << pyzo.__init__.py late bindings >> (use_pyzo_config)
            ## Init

            # List of names that are later overriden (in main.py)
            editors = None # The editor stack instance
            shells = None # The shell stack instance
            main = None # The mainwindow
            icon = None # The icon
            parser = None # The source parser
            status = None # The statusbar (or None)

            # Get directories of interest
            pyzoDir, appDataDir = getResourceDirs()

            # Create ssdf in module namespace, and fill it
            if use_pyzo_config:
                _saveConfigFile = True
                config = ssdf.new()
                loadConfig()
            else:
                config = ConfigShim() # g.TracingNullObject(tag='config shim')

            # Init default style name (set in main.restorePyzoState())
            defaultQtStyleName = ''
            #@-<< pyzo.__init__.py late bindings >>
            #@afterref
 # use_config
        if use_pyzo_logging:
            from pyzo.core import pyzoLogging
                # Importing this module actually starts logging.
            assert pyzoLogging
        #@+<< import the file browser >>
        #@+node:ekr.20190413074155.8: *3* << import the file browser >>
        #@+<< unused imports >>
        #@+node:ekr.20190413074155.9: *4* << unused imports >>
        # import pyzo.tools as tools
        # assert tools

        # From pyzoFileBrowser/__init__.py
            # import os.path as op
            # import pyzo
            # from pyzo.util import zon as ssdf
            # from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa
            # from .browser import Browser
            # from .utils import cleanpath, isdir

        # From pyzoFileBroswer/browser.py imports
            # import sys
            # import os.path as op
            # import pyzo
            # from pyzo import translate
            # from pyzo.util import zon as ssdf
            # from . import QtCore, QtGui, QtWidgets
            # from . import proxies
            # from .tree import Tree
            # from .utils import cleanpath, isdir
        #@-<< unused imports >>
        #
        # Prerequisites...
        import pyzo.core.main as main
        main.loadIcons()
        main.loadFonts()
        #
        # Load order of imports is important.
        # The imports must exist, so keep pyflakes happy with asserts.
        from pyzo.core.menu import Menu
        assert Menu
        from pyzo.tools.pyzoFileBrowser.tree import Tree
        assert Tree
        import pyzo.core.icons as icons
        assert icons
        from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
        #@-<< import the file browser >>
        #@+<< keep pyflakes happy >>
        #@+node:ekr.20190413074155.10: *3* << keep pyflakes happy >>
        if 0:
            # Imports...
            print(translate)
            print(yotonloader)
            
            # Module vars...
            print(defaultQtStyleName)
            print(icon)
            print(parser)
            print(shells)
            print(status)
            
            # pyzo.__init__.py
            print(_saveConfigFile)
            print(editors)
            print(locale)
            print(QtCore, QtGui, QtWidgets)
            print(setLanguage)
            print(traceback)
        #@-<< keep pyflakes happy >>
        file_browser = PyzoFileBrowser(parent=None)
        file_browser.show()
        return file_browser
    except Exception:
        g.es_exception()
        return None
#@-others
#@-leo

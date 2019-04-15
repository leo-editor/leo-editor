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
import os
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
_saveConfigFile = False
#@+others
#@+node:ekr.20190415051706.1: **  top-level functions
#@+node:ekr.20190410171905.1: *3* init (pyzo_support.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    if g.app.gui.guiName() != "qt":
        print('pyzo_support.py requires Qt gui')
        return False
    ###
        # This obscures testing of pyzo imports.
        # if not is_pyzo_loaded():
            # print('pyzo_support.py requires pyzo')
            # return False
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190415051754.1: *3* onCreate (pyzo_support.py)
def onCreate(tag, keys):
    c = keys.get('c')
    if c:
        c.pyzoController = PyzoController(c)

    
#@+node:ekr.20190414034531.1: ** class ConfigShim
class ConfigShim(object):
    # pylint: disable=no-member
    pass
#@+node:ekr.20190415051335.1: ** class PyzoController
class PyzoController (object):
    '''A per-commander controller providing pyzo support.'''
    
    def __init__(self, c):
        # g.pr('PyzoController.__init__')
        self.c = c
        self.use_config = True
            # True: use pyzo's config.
            # False: use ConfigShim class.
        self.widgets = []
            # Permanent references, to prevent widgets from disappearing.
        #
        # Copies of imported names.
        self.PyzoFileBrowser = None

    #@+others
    #@+node:ekr.20190415061516.1: *3* pz.do_pyzo imports
    def do_pyzo_imports(self):
        
        # Prefer explicit imports to implicit.
        #
        #@+<< pyzo/__init__.py imports >>
        #@+node:ekr.20190415051125.5: *4* << pyzo/__init__.py imports >>
        import os
        # import sys #EKR: imported above.
        import locale
        import traceback

        self.placate_pyflakes (locale, traceback)

        # Check Python version
        if sys.version < '3':
            raise RuntimeError('Pyzo requires Python 3.x to run.')

        # Make each OS find platform plugins etc.
        # pylint: disable=no-member
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
            
        # from pyzo.util import paths

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

        self.placate_pyflakes(QtCore, QtGui, QtWidgets, setLanguage, translate, yotonloader)
        #@-<< pyzo/__init__.py imports >>
        #@+<< pyzo.__init__.py early bindings >>
        #@+node:ekr.20190415051125.6: *4* << pyzo.__init__.py early bindings >>
        # Set environ to let kernel know some stats about us
        os.environ['PYZO_PREFIX'] = sys.prefix
        _is_pyqt4 = hasattr(QtCore, 'PYQT_VERSION_STR')
        os.environ['PYZO_QTLIB'] = 'PyQt4' if _is_pyqt4 else 'PySide'
        #@-<< pyzo.__init__.py early bindings >>
        #@+others
        #@+node:ekr.20190415051125.12: *4* function: loadConfig (pyzo.__init__.py)
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
                # pylint: disable=no-member
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
        #@+node:ekr.20190415051125.7: *4* << pyzo.__init__.py late bindings >>
        ## Init

        # List of names that are later overriden (in main.py)
        editors = None # The editor stack instance
        shells = None # The shell stack instance
        main = None # The mainwindow
        icon = None # The icon
        parser = None # The source parser
        status = None # The statusbar (or None)

        self.placate_pyflakes(editors, icon, parser, shells, status)

        # Get directories of interest
        pyzoDir, appDataDir = self.getResourceDirs()

        # Create ssdf in module namespace, and fill it
        if self.use_config:
            _saveConfigFile = True
            config = ssdf.new()
            loadConfig()
        else:
            config = ConfigShim() # g.TracingNullObject(tag='config shim')

        # Init default style name (set in main.restorePyzoState())
        defaultQtStyleName = ''

        self.placate_pyflakes(_saveConfigFile, defaultQtStyleName)
        #@-<< pyzo.__init__.py late bindings >>
        #@+<< imports from start >>
        #@+node:ekr.20190415051125.8: *4* << imports from start >>
        from pyzo.core import pyzoLogging

        self.placate_pyflakes(pyzoLogging)
        #@-<< imports from start >>
        #@+<< import the file browser >>
        #@+node:ekr.20190415051125.9: *4* << import the file browser >>
        #
        # Prerequisites...
        import pyzo.core.main as main
        main.loadIcons()
        main.loadFonts()
        from pyzo.core.menu import Menu
        from pyzo.tools.pyzoFileBrowser.tree import Tree
        import pyzo.core.icons as icons
        from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser

        self.PyzoFileBrowser = PyzoFileBrowser

        self.placate_pyflakes(icons, Menu, Tree)

        #@-<< import the file browser >>
    #@+node:ekr.20190415051125.11: *3* pz.getResourceDirs
    def getResourceDirs(self):
        """
        getResourceDirs()
        Get the directories to the resources: (pyzoDir, appDataDir).
        Also makes sure that the appDataDir has a "tools" directory and
        a style file.
        """
        
        from pyzo.util import paths

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
    #@+node:ekr.20190415051125.13: *3* pz.monkey_patch
    def monkey_patch(self):
        
        from pyzo.tools.pyzoFileBrowser.tree import FileItem

        def patchedOnActivated(self, c=self.c):
            # todo: someday we should be able to simply pass the proxy object to the editors
            # so that we can open files on any file system
            path = self.path()
            g.trace(path)
            ext = os.path.splitext(path)[1]
            if ext == '.leo': ### not in ['.pyc','.pyo','.png','.jpg','.ico']:
                g.openWithFileName(path, old_c=c)
        
        FileItem.onActivated = patchedOnActivated
    #@+node:ekr.20190413074155.1: *3* pz.open_file_browser
    def open_file_browser(self):
        '''A test bed for importing pyzo's file browser.'''
        #@+<< set g.pyzo switches >>
        #@+node:ekr.20190415051125.3: *4* << set g.pyzo switches >>
        import sys
        if '--pyzo' not in sys.argv:
            sys.argv.append('--pyzo')
        g.pyzo = True
        g.pyzo_pdb = False
        g.pyzo_trace = True
        g.pyzo_trace_imports = True
        #@-<< set g.pyzo switches >>
        try:
            self.do_pyzo_imports()
            self.monkey_patch()
            w = self.PyzoFileBrowser(parent=None)
            w.show()
            self.widgets.append(w)
            print('Done')
        except Exception:
            g.es_exception()
    #@+node:ekr.20190415053931.1: *3* pz.placate_pyflakes
    def placate_pyflakes(self, *args, **keys):
        '''Prevent a pyflakes complaint'''
        pass
    #@-others
#@-others
#@-leo

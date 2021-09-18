# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2608: * @file leoApp.py
#@@first
#@+<< imports >>
#@+node:ekr.20120219194520.10463: ** << imports >> (leoApp)
import importlib
import io
import optparse
import os
import sqlite3
import subprocess
import string
import sys
import time
import traceback
from typing import Any, Dict
import zipfile
import platform
from leo.core import leoGlobals as g
from leo.core import leoExternalFiles
StringIO = io.StringIO
#@-<< imports >>
#@+others
#@+node:ekr.20150509193629.1: ** cmd (decorator)
def cmd(name):
    """Command decorator for the LeoApp class."""
    return g.new_cmd_decorator(name, ['g', 'app'])
#@+node:ekr.20161026122804.1: ** class IdleTimeManager
class IdleTimeManager:
    """
    A singleton class to manage idle-time handling. This class handles all
    details of running code at idle time, including running 'idle' hooks.

    Any code can call g.app.idleTimeManager.add_callback(callback) to cause
    the callback to be called at idle time forever.
    """

    def __init__(self):
        """Ctor for IdleTimeManager class."""
        self.callback_list = []
        self.timer = None
    #@+others
    #@+node:ekr.20161026125611.1: *3* itm.add_callback
    def add_callback(self, callback):
        """Add a callback to be called at every idle time."""
        self.callback_list.append(callback)
    #@+node:ekr.20161026124810.1: *3* itm.on_idle
    on_idle_count = 0

    def on_idle(self, timer):
        """IdleTimeManager: Run all idle-time callbacks."""
        if not g.app: return
        if g.app.killed: return
        if not g.app.pluginsController:
            g.trace('No g.app.pluginsController', g.callers())
            timer.stop()
            return  # For debugger.
        self.on_idle_count += 1
        # Handle the registered callbacks.
        for callback in self.callback_list:
            try:
                callback()
            except Exception:
                g.es_exception()
                g.es_print(f"removing callback: {callback}")
                self.callback_list.remove(callback)
        # Handle idle-time hooks.
        g.app.pluginsController.on_idle()
    #@+node:ekr.20161028034808.1: *3* itm.start
    def start(self):
        """Start the idle-time timer."""
        self.timer = g.IdleTime(
            self.on_idle,
            delay=500,
            tag='IdleTimeManager.on_idle')
        if self.timer:
            self.timer.start()
    #@-others
#@+node:ekr.20120209051836.10241: ** class LeoApp
class LeoApp:
    """A class representing the Leo application itself.

    Ivars of this class are Leo's global variables."""
    #@+others
    #@+node:ekr.20150509193643.1: *3* app.Birth & startup
    #@+node:ekr.20031218072017.1416: *4* app.__init__ (helpers contain language dicts)
    def __init__(self):
        """
        Ctor for LeoApp class. These ivars are Leo's global vars.

        leoGlobals.py contains global switches to be set by hand.
        """
        #@+<< LeoApp: command-line arguments >>
        #@+node:ekr.20161028035755.1: *5* << LeoApp: command-line arguments >>
        self.batchMode = False
            # True: run in batch mode.
        self.debug = []
            # A list of switches to be enabled.
        self.diff = False
            # True: run Leo in diff mode.
        self.enablePlugins = True
            # True: run start1 hook to load plugins. --no-plugins
        self.failFast = False
            # True: Use the failfast option in unit tests.
        self.gui = None
            # The gui class.
        self.guiArgName = None
            # The gui name given in --gui option.
        self.ipython_inited = False
            # True if leoIpython.py imports succeeded.
        self.isTheme = False
            # True: load files as theme files (ignore myLeoSettings.leo).
        self.listen_to_log_flag = False
            # True: execute listen-to-log command.
        self.qt_use_tabs = False
            # True: using qt gui: allow tabbed main window.
        self.loaded_session = False
            # Set by startup logic to True if no files specified on the command line.
        self.silentMode = False
            # True: no signon.
        self.start_fullscreen = False
            # For qt_frame plugin.
        self.start_maximized = False
            # For qt_frame plugin.
        self.start_minimized = False
            # For qt_frame plugin.
        self.trace_binding = None
            # The name of a binding to trace, or None.
        self.trace_setting = None
            # The name of a setting to trace, or None.
        self.translateToUpperCase = False
            # Never set to True.
        self.useIpython = False
            # True: add support for IPython.
        self.use_psyco = False
            # True: use psyco optimization.
        self.use_splash_screen = True
            # True: put up a splash screen.
        #@-<< LeoApp: command-line arguments >>
        #@+<< LeoApp: Debugging & statistics >>
        #@+node:ekr.20161028035835.1: *5* << LeoApp: Debugging & statistics >>
        self.count = 0
            # General purpose debugging count.
        self.debug_dict = {}
            # For general use.
        self.disable_redraw = False
            # True: disable all redraws.
        self.disableSave = False
            # May be set by plugins.
        self.idle_timers = []
            # A list of IdleTime instances, so they persist.
        self.log_listener = None
            # The process created by the 'listen-for-log' command.
        self.positions = 0
            # The number of positions generated.
        self.scanErrors = 0
            # The number of errors seen by g.scanError.
        self.structure_errors = 0
            # Set by p.safeMoveToThreadNext.
        self.statsDict = {}
            # dict used by g.stat, g.clear_stats, g.print_stats.
        self.statsLockout = False
            # A lockout to prevent unbound recursion while gathering stats.
        self.validate_outline = False
            # True: enables c.validate_outline. (slow)
        #@-<< LeoApp: Debugging & statistics >>
        #@+<< LeoApp: error messages >>
        #@+node:ekr.20161028035902.1: *5* << LeoApp: error messages >>
        self.menuWarningsGiven = False
            # True: supress warnings in menu code.
        self.unicodeErrorGiven = True
            # True: suppres unicode tracebacks.
        #@-<< LeoApp: error messages >>
        #@+<< LeoApp: global directories >>
        #@+node:ekr.20161028035924.1: *5* << LeoApp: global directories >>
        self.extensionsDir = None
            # The leo/extensions directory
        self.globalConfigDir = None
            # leo/config directory
        self.globalOpenDir = None
            # The directory last used to open a file.
        self.homeDir = None
            # The user's home directory.
        self.homeLeoDir = None
            # The user's home/.leo directory.
        self.leoEditorDir = None
            # The leo-editor directory.
        self.loadDir = None
            # The leo/core directory.
        self.machineDir = None
            # The machine-specific directory.
        #@-<< LeoApp: global directories >>
        #@+<< LeoApp: global data >>
        #@+node:ekr.20161028035956.1: *5* << LeoApp: global data >>
        self.atAutoNames = set()
            # The set of all @auto spellings.
        self.atFileNames = set()
            # The set of all built-in @<file> spellings.

        self.globalKillBuffer = []
            # The global kill buffer.
        self.globalRegisters = {}
            # The global register list.
        self.leoID = None
            # The id part of gnx's.
        self.loadedThemes = []
            # List of loaded theme.leo files.
            # This is used by the 'new' command.
        self.lossage = []
            # List of last 100 keystrokes.
        self.paste_c = None
            # The commander that pasted the last outline.
        self.spellDict = None
            # The singleton PyEnchant spell dict.
        self.numberOfUntitledWindows = 0
            # Number of opened untitled windows.
        self.windowList = []
            # Global list of all frames.
        self.realMenuNameDict = {}
            # Translations of menu names.
        #@-<< LeoApp: global data >>
        #@+<< LeoApp: global controller/manager objects >>
        #@+node:ekr.20161028040028.1: *5* << LeoApp: global controller/manager objects >>
        # Most of these are defined in initApp.
        self.backgroundProcessManager = None
            # The singleton BackgroundProcessManager instance.
        self.commander_cacher = None
            # The singleton leoCacher.CommanderCacher instance.
        self.commander_db = None
            # The singleton db, managed by g.app.commander_cacher.
        self.config = None
            # The singleton leoConfig instance.
        self.db = None
            # The singleton global db, managed by g.app.global_cacher.
        self.externalFilesController = None
            # The singleton ExternalFilesController instance.
        self.global_cacher = None
            # The singleton leoCacher.GlobalCacher instance.
        self.idleTimeManager = None
            # The singleton IdleTimeManager instance.
        self.ipk = None
            # python kernel instance
        self.loadManager = None
            # The singleton LoadManager instance.
        # self.logManager = None
            # The singleton LogManager instance.
        # self.openWithManager = None
            # The singleton OpenWithManager instance.
        self.nodeIndices = None
            # The singleton nodeIndices instance.
        self.pluginsController = None
            # The singleton PluginsManager instance.
        self.sessionManager = None
            # The singleton SessionManager instance.
        # The Commands class...
        self.commandName = None
            # The name of the command being executed.
        self.commandInterruptFlag = False
            # True: command within a command.
        #@-<< LeoApp: global controller/manager objects >>
        #@+<< LeoApp: global reader/writer data >>
        #@+node:ekr.20170302075110.1: *5* << LeoApp: global reader/writer data >>
        # From leoAtFile.py.
        self.atAutoWritersDict = {}
        self.writersDispatchDict = {}
        # From leoImport.py
        self.atAutoDict = {}
            # Keys are @auto names, values are scanner classes.
        self.classDispatchDict = {}
        #@-<< LeoApp: global reader/writer data >>
        #@+<< LeoApp: global status vars >>
        #@+node:ekr.20161028040054.1: *5* << LeoApp: global status vars >>
        self.already_open_files = []
            # A list of file names that *might* be open in another
            # copy of Leo.
        self.dragging = False
            # True: dragging.
        self.inBridge = False
            # True: running from leoBridge module.
        self.inScript = False
            # True: executing a script.
        self.initing = True
            # True: we are initiing the app.
        self.initComplete = False
            # True: late bindings are not allowed.
        self.initStyleFlag = False
            # True: setQtStyle called.
        self.killed = False
            # True: we are about to destroy the root window.
        self.openingSettingsFile = False
            # True, opening a settings file.
        self.preReadFlag = False
            # True: we are pre-reading a settings file.
        self.quitting = False
            # True: quitting.  Locks out some events.
        self.restarting = False
            # True: restarting all of Leo. #1240.
        self.reverting = False
            # True: executing the revert command.
        self.syntax_error_files = []
        #@-<< LeoApp: global status vars >>
        #@+<< LeoApp: the global log >>
        #@+node:ekr.20161028040141.1: *5* << LeoApp: the global log >>
        # To be moved to the LogManager.
        self.log = None
            # The LeoFrame containing the present log.
        self.logInited = False
            # False: all log message go to logWaiting list.
        self.logIsLocked = False
            # True: no changes to log are allowed.
        self.logWaiting = []
            # List of tuples (s, color, newline) waiting to go to a log.
        self.printWaiting = []
            # Queue of messages to be sent to the printer.
        self.signon = ''
        self.signon1 = ''
        self.signon2 = ''
        #@-<< LeoApp: the global log >>
        #@+<< LeoApp: global theme data >>
        #@+node:ekr.20180319152119.1: *5* << LeoApp: global theme data >>
        self.theme_directory = None
            # The directory from which the theme file was loaded, if any.
            # Set only by LM.readGlobalSettingsFiles.
            # Used by the StyleSheetManager class.
        #@-<< LeoApp: global theme data >>
        #@+<< LeoApp: global types >>
        #@+node:ekr.20161028040204.1: *5* << LeoApp: global types >>
        from leo.core import leoFrame
        from leo.core import leoGui
        self.nullGui = leoGui.NullGui()
        self.nullLog = leoFrame.NullLog()
        #@-<< LeoApp: global types >>
        #@+<< LeoApp: plugins and event handlers >>
        #@+node:ekr.20161028040229.1: *5* << LeoApp: plugins and event handlers >>
        self.hookError = False
            # True: suppress further calls to hooks.
            # g.doHook sets g.app.hookError on all exceptions.
            # Scripts may reset g.app.hookError to try again.
        self.hookFunction = None
            # Application wide hook function.
        self.idle_time_hooks_enabled = True
            # True: idle-time hooks are enabled.
        #@-<< LeoApp: plugins and event handlers >>
        #@+<< LeoApp: scripting ivars >>
        #@+node:ekr.20161028040303.1: *5* << LeoApp: scripting ivars >>
        self.searchDict = {}
            # For communication between find/change scripts.
        self.scriptDict = {}
            # For use by scripts. Cleared before running each script.
        self.scriptResult = None
            # For use by leoPymacs.
        self.permanentScriptDict = {}
            # For use by scrips. Never cleared automatically.
        #@-<< LeoApp: scripting ivars >>
        #@+<< LeoApp: unit testing ivars >>
        #@+node:ekr.20161028040330.1: *5* << LeoApp: unit testing ivars >>
        self.isExternalUnitTest = False
            # True: we are running a unit test externally.
        self.runningAllUnitTests = False
            # True: we are running all unit tests (Only for local tests).
        self.suppressImportChecks = False
            # Used only in basescanner.py
            # True: suppress importCommands.check
        self.unitTestDict = {}
            # For communication between unit tests and code.
        self.unitTestGui = None
            # A way to override the gui in external unit tests.
        self.unitTesting = False
            # True if unit testing.
        self.unitTestMenusDict = {}
            # Created in LeoMenu.createMenuEntries for a unit test.
            # keys are command names. values are sets of strokes.
        #@-<< LeoApp: unit testing ivars >>
        # Define all global data.
        self.init_at_auto_names()
        self.init_at_file_names()
        self.define_global_constants()
        self.define_language_delims_dict()
        self.define_language_extension_dict()
        self.define_extension_dict()
        self.define_delegate_language_dict()
    #@+node:ekr.20141102043816.5: *5* app.define_delegate_language_dict
    def define_delegate_language_dict(self):
        self.delegate_language_dict = {
            # Keys are new language names.
            # Values are existing languages in leo/modes.
            "less": "css",
            "hbs": "html",
            "handlebars": "html",
            #"rust": "c",
            # "vue": "c",
        }
    #@+node:ekr.20120522160137.9911: *5* app.define_extension_dict
    #@@nobeautify

    def define_extension_dict(self):

        # Keys are extensions, values are languages
        self.extension_dict = {
            # "ada":    "ada",
            "ada":      "ada95", # modes/ada95.py exists.
            "ahk":      "autohotkey",
            "aj":       "aspect_j",
            "apdl":     "apdl",
            "as":       "actionscript", # jason 2003-07-03
            "asp":      "asp",
            "awk":      "awk",
            "b":        "b",
            "bas":      "rapidq", # fil 2004-march-11
            "bash":     "shellscript",
            "bat":      "batch",
            "bbj":      "bbj",
            "bcel":     "bcel",
            "bib":      "bibtex",
            "c":        "c",
            "c++":      "cplusplus",
            "cbl":      "cobol", # Only one extension is valid: .cob
            "cfg":      "config",
            "cfm":      "coldfusion",
            "clj":      "clojure", # 2013/09/25: Fix bug 879338.
            "cljs":     "clojure",
            "cljc":     "clojure",
            "ch":       "chill", # Other extensions, .c186,.c286
            "coffee":   "coffeescript",
            "conf":     "apacheconf",
            "cpp":      "cplusplus", # 2020/08/12: was cpp.
            "css":      "css",
            "d":        "d",
            "dart":     "dart",
            "e":        "eiffel",
            "el":       "elisp",
            "eml":      "mail",
            "erl":      "erlang",
            "ex":       "elixir",
            "f":        "fortran",
            "f90":      "fortran90",
            "factor":   "factor",
            "forth":    "forth",
            "g":        "antlr",
            "go":       "go",
            "groovy":   "groovy",
            "h":        "c", # 2012/05/23.
            "handlebars": "html", # McNab.
            "hbs":      "html", # McNab.
            "hs":       "haskell",
            "html":     "html",
            "hx":       "haxe",
            "i":        "swig",
            "i4gl":     "i4gl",
            "icn":      "icon",
            "idl":      "idl",
            "inf":      "inform",
            "info":     "texinfo",
            "ini":      "ini",
            "io":       "io",
            "ipynb":    "jupyter",
            "iss":      "inno_setup",
            "java":     "java",
            "jhtml":    "jhtml",
            "jmk":      "jmk",
            "js":       "javascript", # For javascript import test.
            "jsp":      "javaserverpage",
            "json":     "json",
            # "jsp":      "jsp",
            "ksh":      "kshell",
            "kv":       "kivy", # PeckJ 2014/05/05
            "latex":    "latex",
            "less":     "css", # McNab
            "lua":      "lua", # ddm 13/02/06
            "ly":       "lilypond",
            "m":        "matlab",
            "mak":      "makefile",
            "md":       "md", # PeckJ 2013/02/07
            "ml":       "ml",
            "mm":       "objective_c", # Only one extension is valid: .m
            "mod":      "modula3",
            "mpl":      "maple",
            "mqsc":     "mqsc",
            "nqc":      "nqc",
            "nsi":      "nsi", # EKR: 2010/10/27
            # "nsi":      "nsis2",
            "nw":       "noweb",
            "occ":      "occam",
            "otl":      "vimoutline", # TL 8/25/08 Vim's outline plugin
            "p":        "pascal",
            # "p":      "pop11", # Conflicts with pascal.
            "php":      "php",
            "pike":     "pike",
            "pl":       "perl",
            "pl1":      "pl1",
            "po":       "gettext",
            "pod":      "perlpod",
            "pov":      "povray",
            "prg":      "foxpro",
            "pro":      "prolog",
            "ps":       "postscript",
            "psp":      "psp",
            "ptl":      "ptl",
            "py":       "python",
            "pyx":      "cython", # Other extensions, .pyd,.pyi
            # "pyx":    "pyrex",
            # "r":      "r", # modes/r.py does not exist.
            "r":        "rebol", # jason 2003-07-03
            "rb":       "ruby", # thyrsus 2008-11-05
            "rest":     "rst",
            "rex":      "objectrexx",
            "rhtml":    "rhtml",
            "rib":      "rib",
            "rs":       "rust", # EKR: 2019/08/11
            "sas":      "sas",
            "scala":    "scala",
            "scm":      "scheme",
            "scpt":     "applescript",
            "sgml":     "sgml",
            "sh":       "shell", # DS 4/1/04. modes/shell.py exists.
            "shtml":    "shtml",
            "sm":       "smalltalk",
            "splus":    "splus",
            "sql":      "plsql", # qt02537 2005-05-27
            "sqr":      "sqr",
            "ss":       "ssharp",
            "ssi":      "shtml",
            "sty":      "latex",
            "tcl":      "tcl", # modes/tcl.py exists.
            # "tcl":    "tcltk",
            "tex":      "latex",
            # "tex":      "tex",
            "tpl":      "tpl",
            "ts":       "typescript",
            "txt":      "plain",
            # "txt":      "text",
            # "txt":      "unknown", # Set when @comment is seen.
            "uc":       "uscript",
            "v":        "verilog",
            "vbs":      "vbscript",
            "vhd":      "vhdl",
            "vhdl":     "vhdl",
            "vim":      "vim",
            "vtl":      "velocity",
            "w":        "cweb",
            "wiki":     "moin",
            "xml":      "xml",
            "xom":      "omnimark",
            "xsl":      "xsl",
            "yaml":     "yaml",
            "vue":      "javascript",
            "zpt":      "zpt",
        }

        # These aren't real languages, or have no delims...
            # cvs_commit, dsssl, embperl, freemarker, hex, jcl,
            # patch, phpsection, progress, props, pseudoplain,
            # relax_ng_compact, rtf, svn_commit.

        # These have extensions which conflict with other languages.
            # assembly_6502:    .asm or .a or .s
            # assembly_macro32: .asm or .a
            # assembly_mcs51:   .asm or .a
            # assembly_parrot:  .asm or .a
            # assembly_r2000:   .asm or .a
            # assembly_x86:     .asm or .a
            # squidconf:        .conf
            # rpmspec:          .rpm

        # Extra language extensions, used to associate extensions with mode files.
        # Used by importCommands.languageForExtension.
        # Keys are extensions, values are corresponding mode file (without .py)
        # A value of 'none' is a signal to unit tests that no extension file exists.
        self.extra_extension_dict = {
            'pod'   : 'perl',
            'unknown_language': 'none',
            'w'     : 'none', # cweb
        }
    #@+node:ekr.20031218072017.1417: *5* app.define_global_constants
    def define_global_constants(self):
        # self.prolog_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        self.prolog_prefix_string = "<?xml version=\"1.0\" encoding="
        self.prolog_postfix_string = "?>"
        self.prolog_namespace_string = 'xmlns:leo="http://edreamleo.org/namespaces/leo-python-editor/1.1"'
    #@+node:ekr.20120522160137.9909: *5* app.define_language_delims_dict
    #@@nobeautify

    def define_language_delims_dict(self):

        self.language_delims_dict = {
            # Internally, lower case is used for all language names.
            # Keys are languages, values are 1,2 or 3-tuples of delims.
            "actionscript"       : "// /* */", # jason 2003-07-03
            "ada"                : "--",
            "ada95"              : "--",
            "ahk"                : ";",
            "antlr"              : "// /* */",
            "apacheconf"         : "#",
            "apdl"               : "!",
            "applescript"        : "-- (* *)",
            "asp"                : "<!-- -->",
            "aspect_j"           : "// /* */",
            "assembly_6502"      : ";",
            "assembly_macro32"   : ";",
            "assembly_mcs51"     : ";",
            "assembly_parrot"    : "#",
            "assembly_r2000"     : "#",
            "assembly_x86"       : ";",
            "autohotkey"         : "; /* */", # TL - AutoHotkey language
            "awk"                : "#",
            "b"                  : "// /* */",
            "batch"              : "REM_", # Use the REM hack.
            "bbj"                : "/* */",
            "bcel"               : "// /* */",
            "bibtex"             : "%",
            "c"                  : "// /* */", # C, C++ or objective C.
            "chill"              : "/* */",
            "clojure"            : ";", # 2013/09/25: Fix bug 879338.
            "cobol"              : "*",
            "coldfusion"         : "<!-- -->",
            "coffeescript"       : "#", # 2016/02/26.
            "config"             : "#", # Leo 4.5.1
            "cplusplus"          : "// /* */",
            "cpp"                : "// /* */",# C++.
            "csharp"             : "// /* */", # C#
            "css"                : "/* */", # 4/1/04
            "cweb"               : "@q@ @>", # Use the "cweb hack"
            "cython"             : "#",
            "d"                  : "// /* */",
            "dart"               : "// /* */", # Leo 5.0.
            "doxygen"            : "#",
            "eiffel"             : "--",
            "elisp"              : ";",
            "erlang"             : "%",
            "elixir"             : "#",
            "factor"             : "!_ ( )", # Use the rem hack.
            "forth"              : "\\_ _(_ _)", # Use the "REM hack"
            "fortran"            : "C",
            "fortran90"          : "!",
            "foxpro"             : "&&",
            "gettext"            : "# ",
            "go"                 : "//",
            "groovy"             : "// /* */",
            "handlebars"         : "<!-- -->", # McNab: delegate to html.
            "haskell"            : "--_ {-_ _-}",
            "haxe"               : "// /* */",
            "hbs"                : "<!-- -->", # McNab: delegate to html.
            "html"               : "<!-- -->",
            "i4gl"               : "-- { }",
            "icon"               : "#",
            "idl"                : "// /* */",
            "inform"             : "!",
            "ini"                : ";",
            "inno_setup"         : ";",
            "interlis"           : "/* */",
            "io"                 : "// */",
            "java"               : "// /* */",
            "javascript"         : "// /* */", # EKR: 2011/11/12: For javascript import test.
            "javaserverpage"     : "<%-- --%>", # EKR: 2011/11/25 (See also, jsp)
            "jhtml"              : "<!-- -->",
            "jmk"                : "#",
            "json"               : "#", # EKR: 2020/07/27: Json has no delims. This is a dummy entry.
            "jsp"                : "<%-- --%>",
            "jupyter"            : "<%-- --%>", # Default to markdown?
            "kivy"               : "#", # PeckJ 2014/05/05
            "kshell"             : "#", # Leo 4.5.1.
            "latex"              : "%",
            "less"               : "/* */", # NcNab: delegate to css.
            "lilypond"           : "% %{ %}",
            "lisp"               : ";", # EKR: 2010/09/29
            "lotos"              : "(* *)",
            "lua"                : "--", # ddm 13/02/06
            "mail"               : ">",
            "makefile"           : "#",
            "maple"              : "//",
            "markdown"           : "<!-- -->", # EKR, 2018/03/03: html comments.
            "matlab"             : "%", # EKR: 2011/10/21
            "md"                 : "<!-- -->", # PeckJ: 2013/02/08
            "ml"                 : "(* *)",
            "modula3"            : "(* *)",
            "moin"               : "##",
            "mqsc"               : "*",
            "netrexx"            : "-- /* */",
            "noweb"              : "%", # EKR: 2009-01-30. Use Latex for doc chunks.
            "nqc"                : "// /* */",
            "nsi"                : ";", # EKR: 2010/10/27
            "nsis2"              : ";",
            "objective_c"        : "// /* */",
            "objectrexx"         : "-- /* */",
            "occam"              : "--",
            "omnimark"           : ";",
            "pandoc"             : "<!-- -->",
            "pascal"             : "// { }",
            "perl"               : "#",
            "perlpod"            : "# __=pod__ __=cut__", # 9/25/02: The perlpod hack.
            "php"                : "// /* */", # 6/23/07: was "//",
            "pike"               : "// /* */",
            "pl1"                : "/* */",
            "plain"              : "#", # We must pick something.
            "plsql"              : "-- /* */", # SQL scripts qt02537 2005-05-27
            "pop11"              : ";;; /* */",
            "postscript"         : "%",
            "povray"             : "// /* */",
            "powerdynamo"        : "// <!-- -->",
            "prolog"             : "% /* */",
            "psp"                : "<!-- -->",
            "ptl"                : "#",
            "pvwave"             : ";",
            "pyrex"              : "#",
            "python"             : "#",
            "r"                  : "#",
            "rapidq"             : "'", # fil 2004-march-11
            "rebol"              : ";", # jason 2003-07-03
            "redcode"            : ";",
            "rest"               : ".._",
            "rhtml"              : "<%# %>",
            "rib"                : "#",
            "rpmspec"            : "#",
            "rst"                : ".._",
            "rust"               : "// /* */",
            "ruby"               : "#", # thyrsus 2008-11-05
            "rview"              : "// /* */",
            "sas"                : "* /* */",
            "scala"              : "// /* */",
            "scheme"             : "; #| |#",
            "sdl_pr"             : "/* */",
            "sgml"               : "<!-- -->",
            "shell"              : "#",     # shell scripts
            "shellscript"        : "#",
            "shtml"              : "<!-- -->",
            "smalltalk"          : '" "', # Comments are enclosed in double quotes(!!)
            "smi_mib"            : "--",
            "splus"              : "#",
            "sqr"                : "!",
            "squidconf"          : "#",
            "ssharp"             : "#",
            "swig"               : "// /* */",
            "tcl"                : "#",
            "tcltk"              : "#",
            "tex"                : "%", # Bug fix: 2008-1-30: Fixed Mark Edginton's bug.
            "text"               : "#", # We must pick something.
            "texinfo"            : "@c",
            "tpl"                : "<!-- -->",
            "tsql"               : "-- /* */",
            "typescript"         : "// /* */", # For typescript import test.
            "unknown"            : "#", # Set when @comment is seen.
            "unknown_language"   : '#--unknown-language--', # For unknown extensions in @shadow files.
            "uscript"            : "// /* */",
            "vbscript"           : "'",
            "velocity"           : "## #* *#",
            "verilog"            : "// /* */",
            "vhdl"               : "--",
            "vim"                : "\"",
            "vimoutline"         : "#", # TL 8/25/08 Vim's outline plugin
            "xml"                : "<!-- -->",
            "xsl"                : "<!-- -->",
            "xslt"               : "<!-- -->",
            "yaml"               : "#",
            "zpt"                : "<!-- -->",

            # These aren't real languages, or have no delims...
            # "cvs_commit"         : "",
            # "dsssl"              : "; <!-- -->",
            # "embperl"            : "<!-- -->",  # Internal colorizing state.
            # "freemarker"         : "",
            # "hex"                : "",
            # "jcl"                : "",
            # "patch"              : "",
            # "phpsection"         : "<!-- -->",  # Internal colorizing state.
            # "props"              : "#",         # Unknown language.
            # "pseudoplain"        : "",
            # "relax_ng_compact"   : "#",         # An xml schema.
            # "rtf"                : "",
            # "svn_commit"         : "",
        }
    #@+node:ekr.20120522160137.9910: *5* app.define_language_extension_dict
    #@@nobeautify

    def define_language_extension_dict(self):

        # Used only by g.app.externalFilesController.get_ext.

        # Keys are languages, values are extensions.
        self.language_extension_dict = {
            "actionscript"  : "as", # jason 2003-07-03
            "ada"           : "ada",
            "ada95"         : "ada",
            "ahk"           : "ahk",
            "antlr"         : "g",
            "apacheconf"    : "conf",
            "apdl"          : "apdl",
            "applescript"   : "scpt",
            "asp"           : "asp",
            "aspect_j"      : "aj",
            "autohotkey"    : "ahk", # TL - AutoHotkey language
            "awk"           : "awk",
            "b"             : "b",
            "batch"         : "bat", # Leo 4.5.1.
            "bbj"           : "bbj",
            "bcel"          : "bcel",
            "bibtex"        : "bib",
            "c"             : "c",
            "chill"         : "ch",  # Only one extension is valid: .c186, .c286
            "clojure"       : "clj", # 2013/09/25: Fix bug 879338.
            "cobol"         : "cbl", # Only one extension is valid: .cob
            "coldfusion"    : "cfm",
            "coffeescript"  : "coffee",
            "config"        : "cfg",
            "cplusplus"     : "c++",
            "cpp"           : "cpp",
            "css"           : "css", # 4/1/04
            "cweb"          : "w",
            "cython"        : "pyx", # Only one extension is valid at present: .pyi, .pyd.
            "d"             : "d",
            "dart"          : "dart",
            "eiffel"        : "e",
            "elisp"         : "el",
            "erlang"        : "erl",
            "elixir"        : "ex",
            "factor"        : "factor",
            "forth"         : "forth",
            "fortran"       : "f",
            "fortran90"     : "f90",
            "foxpro"        : "prg",
            "gettext"       : "po",
            "go"            : "go",
            "groovy"        : "groovy",
            "haskell"       : "hs",
            "haxe"          : "hx",
            "html"          : "html",
            "i4gl"          : "i4gl",
            "icon"          : "icn",
            "idl"           : "idl",
            "inform"        : "inf",
            "ini"           : "ini",
            "inno_setup"    : "iss",
            "io"            : "io",
            "java"          : "java",
            "javascript"    : "js", # EKR: 2011/11/12: For javascript import test.
            "javaserverpage": "jsp", # EKR: 2011/11/25
            "jhtml"         : "jhtml",
            "jmk"           : "jmk",
            "json"          : "json",
            "jsp"           : "jsp",
            "jupyter"       : "ipynb",
            "kivy"          : "kv", # PeckJ 2014/05/05
            "kshell"        : "ksh", # Leo 4.5.1.
            "latex"         : "tex", # 1/8/04
            "lilypond"      : "ly",
            "lua"           : "lua", # ddm 13/02/06
            "mail"          : "eml",
            "makefile"      : "mak",
            "maple"         : "mpl",
            "matlab"        : "m",
            "md"            : "md", # PeckJ: 2013/02/07
            "ml"            : "ml",
            "modula3"       : "mod",
            "moin"          : "wiki",
            "mqsc"          : "mqsc",
            "noweb"         : "nw",
            "nqc"           : "nqc",
            "nsi"           : "nsi", # EKR: 2010/10/27
            "nsis2"         : "nsi",
            "objective_c"   : "mm", # Only one extension is valid: .m
            "objectrexx"    : "rex",
            "occam"         : "occ",
            "omnimark"      : "xom",
            "pascal"        : "p",
            "perl"          : "pl",
            "perlpod"       : "pod",
            "php"           : "php",
            "pike"          : "pike",
            "pl1"           : "pl1",
            "plain"         : "txt",
            "plsql"         : "sql", # qt02537 2005-05-27
            # "pop11"       : "p", # Conflicts with pascall.
            "postscript"    : "ps",
            "povray"        : "pov",
            "prolog"        : "pro",
            "psp"           : "psp",
            "ptl"           : "ptl",
            "pyrex"         : "pyx",
            "python"        : "py",
            "r"             : "r",
            "rapidq"        : "bas", # fil 2004-march-11
            "rebol"         : "r", # jason 2003-07-03
            "rhtml"         : "rhtml",
            "rib"           : "rib",
            "rst"           : "rest",
            "ruby"          : "rb", # thyrsus 2008-11-05
            "rust"          : "rs", # EKR: 2019/08/11
            "sas"           : "sas",
            "scala"         : "scala",
            "scheme"        : "scm",
            "sgml"          : "sgml",
            "shell"         : "sh", # DS 4/1/04
            "shellscript"   : "bash",
            "shtml"         : "ssi", # Only one extension is valid: .shtml
            "smalltalk"     : "sm",
            "splus"         : "splus",
            "sqr"           : "sqr",
            "ssharp"        : "ss",
            "swig"          : "i",
            "tcl"           : "tcl",
            "tcltk"         : "tcl",
            "tex"           : "tex",
            "texinfo"       : "info",
            "text"          : "txt",
            "tpl"           : "tpl",
            "tsql"          : "sql", # A guess.
            "typescript"    : "ts",
            "unknown"       : "txt", # Set when @comment is seen.
            "uscript"       : "uc",
            "vbscript"      : "vbs",
            "velocity"      : "vtl",
            "verilog"       : "v",
            "vhdl"          : "vhd", # Only one extension is valid: .vhdl
            "vim"           : "vim",
            "vimoutline"    : "otl", # TL 8/25/08 Vim's outline plugin
            "xml"           : "xml",
            "xsl"           : "xsl",
            "xslt"          : "xsl",
            "yaml"          : "yaml",
            "zpt"           : "zpt",
        }

        # These aren't real languages, or have no delims...
            # cvs_commit, dsssl, embperl, freemarker, hex, jcl,
            # patch, phpsection, progress, props, pseudoplain,
            # relax_ng_compact, rtf, svn_commit.

        # These have extensions which conflict with other languages.
            # assembly_6502:    .asm or .a or .s
            # assembly_macro32: .asm or .a
            # assembly_mcs51:   .asm or .a
            # assembly_parrot:  .asm or .a
            # assembly_r2000:   .asm or .a
            # assembly_x86:     .asm or .a
            # squidconf:        .conf
            # rpmspec:          .rpm
    #@+node:ekr.20140729162415.18086: *5* app.init_at_auto_names
    def init_at_auto_names(self):
        """Init the app.atAutoNames set."""
        self.atAutoNames = set([
            "@auto-rst", "@auto",
        ])
    #@+node:ekr.20140729162415.18091: *5* app.init_at_file_names
    def init_at_file_names(self):
        """Init the app.atFileNames set."""
        self.atFileNames = set([
            "@asis",
            "@edit",
            "@file-asis", "@file-thin", "@file-nosent", "@file",
            "@clean", "@nosent",
            "@shadow",
            "@thin",
        ])
    #@+node:ekr.20090717112235.6007: *4* app.computeSignon & printSignon
    def computeSignon(self):
        from leo.core import leoVersion
        app = self
        guiVersion = ', ' + app.gui.getFullVersion() if app.gui else ''
        leoVer = leoVersion.version
        n1, n2, n3, junk1, junk2 = sys.version_info
        if sys.platform.startswith('win'):
            sysVersion = 'Windows '
            try:
                # peckj 20140416: determine true OS architecture
                # the following code should return the proper architecture
                # regardless of whether or not the python architecture matches
                # the OS architecture (i.e. python 32-bit on windows 64-bit will return 64-bit)
                v = platform.win32_ver()
                release, winbuild, sp, ptype = v
                true_platform = os.environ['PROCESSOR_ARCHITECTURE']
                try:
                    true_platform = os.environ['PROCESSOR_ARCHITEw6432']
                except KeyError:
                    pass
                sysVersion = f"Windows {release} {true_platform} (build {winbuild}) {sp}"
            except Exception:
                pass
        else: sysVersion = sys.platform
        branch, junk_commit = g.gitInfo()
        author, commit, date = g.getGitVersion()
        # Compute g.app.signon.
        signon = [f"Leo {leoVer}"]
        if branch:
            signon.append(f", {branch} branch")
        if commit:
            signon.append(', build ' + commit)
        if date:
            signon.append('\n' + date)
        app.signon = ''.join(signon)
        # Compute g.app.signon1.
        app.signon1 = f"Python {n1}.{n2}.{n3}{guiVersion}\n{sysVersion}"

    def printSignon(self, verbose=False):
        """Print a minimal sigon to the log."""
        app = self
        if app.silentMode:
            return
        if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
            print('Note: sys.stdout.encoding is not UTF-8')
            print(f"Encoding is: {sys.stdout.encoding!r}")
            print('See: https://stackoverflow.com/questions/14109024')
            print('')
        print(app.signon)
        if verbose:
            print(app.signon1)
    #@+node:ekr.20100831090251.5838: *4* app.createXGui
    #@+node:ekr.20100831090251.5840: *5* app.createCursesGui
    def createCursesGui(self, fileName='', verbose=False):
        try:
            import curses
            assert curses
        except Exception:
            # g.es_exception()
            print('can not import curses.')
            if g.isWindows:
                print('Windows: pip install windows-curses')
            sys.exit()
        try:
            from leo.plugins import cursesGui2
            ok = cursesGui2.init()
            if ok:
                g.app.gui = cursesGui2.LeoCursesGui()
        except Exception:
            g.es_exception()
            print('can not create curses gui.')
            sys.exit()
    #@+node:ekr.20181031160401.1: *5* app.createBrowserGui
    def createBrowserGui(self, fileName='', verbose=False):
        app = self
        try:
            from flexx import flx
            assert flx
        except Exception:
            g.es_exception()
            print('can not import flexx')
            sys.exit(1)
        try:
            from leo.plugins import leoflexx
            assert leoflexx
        except Exception:
            g.es_exception()
            print('can not import leo.plugins.leoflexx')
            sys.exit(1)
        g.app.gui = leoflexx.LeoBrowserGui(gui_name=app.guiArgName)
    #@+node:ekr.20090619065122.8593: *5* app.createDefaultGui
    def createDefaultGui(self, fileName='', verbose=False):
        """A convenience routines for plugins to create the default gui class."""
        app = self
        argName = app.guiArgName
        if g.in_bridge:
            return  # The bridge will create the gui later.
        if app.gui:
            return  # This method can be called twice if we had to get .leoID.txt.
        assert argName != 'qttabs'
            # For compatibility with g.assertUi('qt')
        if argName == 'qt':
            app.createQtGui(fileName, verbose=verbose)
        elif argName == 'null':
            g.app.gui = g.app.nullGui
        elif argName.startswith('browser'):
            app.createBrowserGui()
        elif argName in ('console', 'curses'):
            app.createCursesGui()
        elif argName == 'text':
            app.createTextGui()
        if not app.gui:
            print('createDefaultGui: Leo requires Qt to be installed.')
    #@+node:ekr.20031218072017.1938: *5* app.createNullGuiWithScript
    def createNullGuiWithScript(self, script=None):
        app = self
        app.batchMode = True
        app.gui = g.app.nullGui
        app.gui.setScript(script)
    #@+node:ekr.20090202191501.1: *5* app.createQtGui
    def createQtGui(self, fileName='', verbose=False):
        # Do NOT omit fileName param: it is used in plugin code.
        """A convenience routines for plugins to create the Qt gui class."""
        app = self
        try:
            from leo.core.leoQt import Qt
            assert Qt
        except Exception:
            # #1215: Raise an emergency dialog.
            message = 'Can not Import Qt'
            print(message)
            try:
                d = g.EmergencyDialog(title=message, message=message)
                d.run()
            except Exception:
                g.es_exception()
            sys.exit(1)
        try:
            from leo.plugins import qt_gui
        except Exception:
            g.es_exception()
            print('can not import leo.plugins.qt_gui')
            sys.exit(1)
        try:
            from leo.plugins.editpane.editpane import edit_pane_test_open, edit_pane_csv
            g.command('edit-pane-test-open')(edit_pane_test_open)
            g.command('edit-pane-csv')(edit_pane_csv)
        except ImportError:
            print('Failed to import editpane')
        #
        # Complete the initialization.
        qt_gui.init()
        if app.gui and fileName and verbose:
            print(f"Qt Gui created in {fileName}")
    #@+node:ekr.20170419093747.1: *5* app.createTextGui (was createCursesGui)
    def createTextGui(self, fileName='', verbose=False):
        app = self
        app.pluginsController.loadOnePlugin('leo.plugins.cursesGui', verbose=verbose)
    #@+node:ekr.20090126063121.3: *5* app.createWxGui
    def createWxGui(self, fileName='', verbose=False):
        # Do NOT omit fileName param: it is used in plugin code.
        """A convenience routines for plugins to create the wx gui class."""
        app = self
        app.pluginsController.loadOnePlugin('leo.plugins.wxGui', verbose=verbose)
        if fileName and verbose:
            print(f"wxGui created in {fileName}")
    #@+node:ville.20090620122043.6275: *4* app.setGlobalDb
    def setGlobalDb(self):
        """ Create global pickleshare db

        Usable by::

            g.app.db['hello'] = [1,2,5]

        """
        # Fixes bug 670108.
        from leo.core import leoCache
        g.app.global_cacher = leoCache.GlobalCacher()
        g.app.db = g.app.global_cacher.db
        g.app.commander_cacher = leoCache.CommanderCacher()
        g.app.commander_db = g.app.commander_cacher.db
    #@+node:ekr.20031218072017.1978: *4* app.setLeoID & helpers
    def setLeoID(self, useDialog=True, verbose=True):
        """Get g.app.leoID from various sources."""
        self.leoID = None
        assert self == g.app
        verbose = verbose and not g.unitTesting and not self.silentMode
        table = (self.setIDFromSys, self.setIDFromFile, self.setIDFromEnv,)
        for func in table:
            func(verbose)
            if self.leoID:
                return self.leoID
        if useDialog:
            self.setIdFromDialog()
            if self.leoID:
                self.setIDFile()
        return self.leoID
    #@+node:ekr.20191017061451.1: *5* app.cleanLeoID
    def cleanLeoID(self, id_, tag):
        """#1404: Make sure that the given Leo ID will not corrupt a .leo file."""
        old_id = id_ if isinstance(id_, str) else repr(id_)
        try:
            id_ = id_.replace('.', '').replace(',', '').replace('"', '').replace("'", '')
            # Remove *all* whitespace: https://stackoverflow.com/questions/3739909
            id_ = ''.join(id_.split())
        except Exception:
            g.es_exception()
            id_ = ''
        if len(id_) < 3:
            g.EmergencyDialog(
                title=f"Invalid Leo ID: {tag}",
                message=(
                    f"Invalid Leo ID: {old_id!r}\n\n"
                    "Your id should contain only letters and numbers\n"
                    "and must be at least 3 characters in length."))
        return id_
    #@+node:ekr.20031218072017.1979: *5* app.setIDFromSys
    def setIDFromSys(self, verbose):
        """
        Attempt to set g.app.leoID from sys.leoID.

        This might be set by in Python's sitecustomize.py file.
        """
        id_ = getattr(sys, "leoID", None)
        if id_:
            # Careful: periods in the id field of a gnx will corrupt the .leo file!
            id_ = self.cleanLeoID(id_, 'sys.leoID')
                # cleanLeoID raises a warning dialog.
            if len(id_) > 2:
                self.leoID = id_
                if verbose:
                    g.red("leoID=", self.leoID, spaces=False)
    #@+node:ekr.20031218072017.1980: *5* app.setIDFromFile
    def setIDFromFile(self, verbose):
        """Attempt to set g.app.leoID from leoID.txt."""
        tag = ".leoID.txt"
        for theDir in (self.homeLeoDir, self.globalConfigDir, self.loadDir):
            if not theDir:
                continue  # Do not use the current directory!
            fn = g.os_path_join(theDir, tag)
            try:
                with open(fn, 'r') as f:
                    s = f.readline().strip()
                if not s:
                    continue
                # #1404: Ensure valid ID.
                id_ = self.cleanLeoID(s, tag)
                    # cleanLeoID raises a warning dialog.
                if len(id_) > 2:
                    self.leoID = id_
                    return
            except IOError:
                pass
            except Exception:
                g.error('unexpected exception in app.setLeoID')
                g.es_exception()
    #@+node:ekr.20060211140947.1: *5* app.setIDFromEnv
    def setIDFromEnv(self, verbose):
        """Set leoID from environment vars."""
        try:
            id_ = os.getenv('USER')
            if id_:
                if verbose:
                    g.blue("setting leoID from os.getenv('USER'):", repr(id_))
                # Careful: periods in the gnx would corrupt the .leo file!
                id_ = self.cleanLeoID(id_, "os.getenv('USER')")
                    # cleanLeoID raises a warning dialog.
                if len(id_) > 2:
                    self.leoID = id_
        except Exception:
            pass
    #@+node:ekr.20031218072017.1981: *5* app.setIdFromDialog
    def setIdFromDialog(self):
        """Get leoID from a Tk dialog."""
        #
        # Don't put up a splash screen: it would obscure the coming dialog.
        self.use_splash_screen = False
        #
        # Get the id, making sure it is at least three characters long.
        while True:
            dialog = g.TkIDDialog()
            dialog.run()
            # #1404: Make sure the id will not corrupt the .leo file.
            id_ = self.cleanLeoID(dialog.val, "")
            if id_ and len(id_) > 2:
                break
        #
        # Put result in g.app.leoID.
        self.leoID = id_
        g.blue('leoID=', repr(self.leoID), spaces=False)
    #@+node:ekr.20031218072017.1982: *5* app.setIDFile
    def setIDFile(self):
        """Create leoID.txt."""
        tag = ".leoID.txt"
        for theDir in (self.homeLeoDir, self.globalConfigDir, self.loadDir):
            if theDir:
                try:
                    fn = g.os_path_join(theDir, tag)
                    with open(fn, 'w') as f:
                        f.write(self.leoID)
                    if g.os_path_exists(fn):
                        g.error('', tag, 'created in', theDir)
                        return
                except IOError:
                    pass
                g.error('can not create', tag, 'in', theDir)
    #@+node:ekr.20031218072017.1847: *4* app.setLog, lockLog, unlocklog
    def setLog(self, log):
        """set the frame to which log messages will go"""
        if not self.logIsLocked:
            self.log = log

    def lockLog(self):
        """Disable changes to the log"""
        # print("app.lockLog:")
        self.logIsLocked = True

    def unlockLog(self):
        """Enable changes to the log"""
        # print("app.unlockLog:")
        self.logIsLocked = False
    #@+node:ekr.20031218072017.2619: *4* app.writeWaitingLog
    def writeWaitingLog(self, c):
        """Write all waiting lines to the log."""
        #
        # Do not call g.es, g.es_print, g.pr or g.trace here!
        app = self
        if not c or not c.exists:
            return
        if g.unitTesting:
            app.logWaiting = []
            g.app.setLog(None)  # Prepare to requeue for other commanders.
            return
        # Write the signon to the log: similar to self.computeSignon().
        table = [
            ('Leo Log Window', 'red'),
            (app.signon, None),
            (app.signon1, None),
        ]
        table.reverse()
        c.setLog()
        app.logInited = True  # Prevent recursive call.
        if not app.silentMode:
            # Write the signon.
            for s, color in table:
                if s:
                    app.logWaiting.insert(0, (s, color, True),)
            # Write all the queued log entries.
            for msg in app.logWaiting:
                s, color, newline = msg[:3]
                kwargs = {} if len(msg) < 4 else msg[3]
                kwargs = {
                    k: v for k, v in kwargs.items() if k not in ('color', 'newline')}
                g.es('', s, color=color, newline=newline, **kwargs)
            if hasattr(c.frame.log, 'scrollToEnd'):
                g.app.gui.runAtIdle(c.frame.log.scrollToEnd)
        app.logWaiting = []
        # Essential when opening multiple files...
        g.app.setLog(None)
    #@+node:ekr.20180924093227.1: *3* app.c property
    @property
    def c(self):
        return self.log and self.log.c
    #@+node:ekr.20171127111053.1: *3* app.Closing
    #@+node:ekr.20031218072017.2609: *4* app.closeLeoWindow
    def closeLeoWindow(self, frame, new_c=None, finish_quit=True):
        """
        Attempt to close a Leo window.

        Return False if the user veto's the close.

        finish_quit - usually True, close Leo when last file closes, but
                      False when closing an already-open-elsewhere file
                      during initial load, so UI remains for files
                      further along the command line.
        """
        c = frame.c
        if 'shutdown' in g.app.debug:
            g.trace(f"changed: {c.changed} {c.shortFileName()}")
        c.endEditing()  # Commit any open edits.
        if c.promptingForClose:
            # There is already a dialog open asking what to do.
            return False
        g.app.recentFilesManager.writeRecentFilesFile(c)
            # Make sure .leoRecentFiles.txt is written.
        if c.changed:
            c.promptingForClose = True
            veto = frame.promptForSave()
            c.promptingForClose = False
            if veto: return False
        g.app.setLog(None)  # no log until we reactive a window.
        g.doHook("close-frame", c=c)
        #
        # Save the window state for *all* open files.
        g.app.commander_cacher.commit()
            # store cache, but don't close it.
        # This may remove frame from the window list.
        if frame in g.app.windowList:
            g.app.destroyWindow(frame)
            g.app.windowList.remove(frame)
        else:
            # #69.
            g.app.forgetOpenFile(fn=c.fileName(), force=True)
        if g.app.windowList:
            c2 = new_c or g.app.windowList[0].c
            g.app.selectLeoWindow(c2)
        elif finish_quit and not g.app.unitTesting:
            g.app.finishQuit()
        return True  # The window has been closed.
    #@+node:ekr.20031218072017.2612: *4* app.destroyAllOpenWithFiles
    def destroyAllOpenWithFiles(self):
        """Remove temp files created with the Open With command."""
        if 'shutdown' in g.app.debug:
            g.pr('destroyAllOpenWithFiles')
        if g.app.externalFilesController:
            g.app.externalFilesController.shut_down()
            g.app.externalFilesController = None
    #@+node:ekr.20031218072017.2615: *4* app.destroyWindow
    def destroyWindow(self, frame):
        """Destroy all ivars in a Leo frame."""
        if 'shutdown' in g.app.debug:
            g.pr(f"destroyWindow:  {frame.c.shortFileName()}")
        if g.app.externalFilesController:
            g.app.externalFilesController.destroy_frame(frame)
        if frame in g.app.windowList:
            # g.pr('destroyWindow', (g.app.windowList)
            g.app.forgetOpenFile(frame.c.fileName())
        # force the window to go away now.
        # Important: this also destroys all the objects of the commander.
        frame.destroySelf()
    #@+node:ekr.20031218072017.1732: *4* app.finishQuit
    def finishQuit(self):
        # forceShutdown may already have fired the "end1" hook.
        assert self == g.app, repr(g.app)
        trace = 'shutdown' in g.app.debug
        if trace:
            g.pr('finishQuit: killed:', g.app.killed)
        if not g.app.killed:
            g.doHook("end1")
            g.app.global_cacher.commit_and_close()
            g.app.commander_cacher.commit()
            g.app.commander_cacher.close()
        if g.app.ipk:
            g.app.ipk.cleanup_consoles()
        g.app.destroyAllOpenWithFiles()
        if hasattr(g.app, 'pyzo_close_handler'):
            # pylint: disable=no-member
            g.app.pyzo_close_handler()
        g.app.killed = True
            # Disable all further hooks and events.
            # Alas, "idle" events can still be called
            # even after the following code.
        if g.app.gui:
            g.app.gui.destroySelf()
                # Calls qtApp.quit()
    #@+node:ekr.20031218072017.2616: *4* app.forceShutdown
    def forceShutdown(self):
        """
        Forces an immediate shutdown of Leo at any time.

        In particular, may be called from plugins during startup.
        """
        trace = 'shutdown' in g.app.debug
        app = self
        if trace:
            g.pr('forceShutdown')
        for c in app.commanders():
            app.forgetOpenFile(c.fileName(), force=True)
        # Wait until everything is quiet before really quitting.
        if trace: g.pr('forceShutdown: before end1')
        g.doHook("end1")
        if trace: g.pr('forceShutdown: after end1')
        self.log = None  # Disable writeWaitingLog
        self.killed = True  # Disable all further hooks.
        for w in self.windowList[:]:
            if trace: g.pr(f"forceShutdown: {w}")
            self.destroyWindow(w)
        if trace: g.pr('before finishQuit')
        self.finishQuit()
    #@+node:ekr.20031218072017.2617: *4* app.onQuit
    @cmd('exit-leo')
    @cmd('quit-leo')
    def onQuit(self, event=None):
        """Exit Leo, prompting to save unsaved outlines first."""
        if 'shutdown' in g.app.debug:
            g.trace()
        g.app.quitting = True
        if g.app.loaded_session and g.app.sessionManager:
            g.app.sessionManager.save_snapshot()
        while g.app.windowList:
            w = g.app.windowList[0]
            if not g.app.closeLeoWindow(w):
                break
        if g.app.windowList:
            g.app.quitting = False  # If we get here the quit has been disabled.
    #@+node:ville.20090602181814.6219: *3* app.commanders
    def commanders(self):
        """ Return list of currently active controllers """
        return [f.c for f in g.app.windowList]
    #@+node:ekr.20120427064024.10068: *3* app.Detecting already-open files
    #@+node:ekr.20120427064024.10064: *4* app.checkForOpenFile
    def checkForOpenFile(self, c, fn):
        """Warn if fn is already open and add fn to already_open_files list."""
        d, tag = g.app.db, 'open-leo-files'
        if g.app.reverting:
            # #302: revert to saved doesn't reset external file change monitoring
            g.app.already_open_files = []
        if (d is None or
            g.app.unitTesting or
            g.app.batchMode or
            g.app.reverting or
            g.app.inBridge
        ):
            return
        # #1519: check os.path.exists.
        aList = g.app.db.get(tag) or []  # A list of normalized file names.
        if any(os.path.exists(z) and os.path.samefile(z, fn) for z in aList):
            # The file may be open in another copy of Leo, or not:
            # another Leo may have been killed prematurely.
            # Put the file on the global list.
            # A dialog will warn the user such files later.
            fn = os.path.normpath(fn)
            if fn not in g.app.already_open_files:
                g.es('may be open in another Leo:', color='red')
                g.es(fn)
                g.app.already_open_files.append(fn)
        else:
            g.app.rememberOpenFile(fn)
    #@+node:ekr.20120427064024.10066: *4* app.forgetOpenFile
    def forgetOpenFile(self, fn, force=False):
        """Forget the open file, so that is no longer considered open."""
        trace = 'shutdown' in g.app.debug
        d, tag = g.app.db, 'open-leo-files'
        if not d or not fn:
            # #69.
            return
        if not force and (
            d is None or g.app.unitTesting or g.app.batchMode or g.app.reverting):
            return
        aList = d.get(tag) or []
        fn = os.path.normpath(fn)
        if fn in aList:
            aList.remove(fn)
            if trace:
                g.pr(f"forgetOpenFile: {g.shortFileName(fn)}")
            d[tag] = aList
        # elif trace: g.pr(f"forgetOpenFile: did not remove: {fn}")
    #@+node:ekr.20120427064024.10065: *4* app.rememberOpenFile
    def rememberOpenFile(self, fn):

        #
        # Do not call g.trace, etc. here.
        d, tag = g.app.db, 'open-leo-files'
        if d is None or g.app.unitTesting or g.app.batchMode or g.app.reverting:
            pass
        elif g.app.preReadFlag:
            pass
        else:
            aList = d.get(tag) or []
            # It's proper to add duplicates to this list.
            aList.append(os.path.normpath(fn))
            d[tag] = aList
    #@+node:ekr.20150621062355.1: *4* app.runAlreadyOpenDialog
    def runAlreadyOpenDialog(self, c):
        """Warn about possibly already-open files."""
        if g.app.already_open_files:
            aList = sorted(set(g.app.already_open_files))
            g.app.already_open_files = []
            g.app.gui.dismiss_splash_screen()
            message = (
                'The following files may already be open\n'
                'in another copy of Leo:\n\n' +
                '\n'.join(aList))
            g.app.gui.runAskOkDialog(c,
                title='Already Open Files',
                message=message,
                text="Ok")
    #@+node:ekr.20171127111141.1: *3* app.Import utils
    #@+node:ekr.20140727180847.17985: *4* app.scanner_for_at_auto
    def scanner_for_at_auto(self, c, p, **kwargs):
        """A factory returning a scanner function for p, an @auto node."""
        d = g.app.atAutoDict
        for key in d:
            # pylint: disable=cell-var-from-loop
            aClass = d.get(key)
            if aClass and g.match_word(p.h, 0, key):

                def scanner_for_at_auto_cb(c, parent, s, **kwargs):
                    try:
                        ic = c.importCommands
                        scanner = aClass(importCommands=ic, **kwargs)
                        return scanner.run(s, parent)
                    except Exception:
                        g.es_print('Exception running', aClass.__name__)
                        g.es_exception()
                        return None

                scanner_for_at_auto_cb.scanner_name = aClass.__name__  # type:ignore
                    # For traces in ic.createOutline.
                return scanner_for_at_auto_cb
        return None
    #@+node:ekr.20140130172810.15471: *4* app.scanner_for_ext
    def scanner_for_ext(self, c, ext, **kwargs):
        """A factory returning a scanner function for the given file extension."""
        aClass = g.app.classDispatchDict.get(ext)
        if aClass:

            def scanner_for_ext_cb(c, parent, s, **kwargs):
                try:
                    ic = c.importCommands
                    scanner = aClass(importCommands=ic, **kwargs)
                    return scanner.run(s, parent)
                except Exception:
                    g.es_print('Exception running', aClass.__name__)
                    g.es_exception()
                    return None

            scanner_for_ext_cb.scanner_name = aClass.__name__  # type:ignore
                # For traces in ic.createOutline.
            return scanner_for_ext_cb
        return None
    #@+node:ekr.20170429152049.1: *3* app.listenToLog
    @cmd('listen-to-log')
    @cmd('log-listen')
    def listenToLog(self, event=None):
        """
        A socket listener, listening on localhost. See:
        https://docs.python.org/2/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

        Start this listener first, then start the broadcaster.

        leo/plugins/cursesGui2.py is a typical broadcaster.
        """
        app = self
        # Kill any previous listener.
        if app.log_listener:
            g.es_print('Killing previous listener')
            try:
                app.log_listener.kill()
            except Exception:
                g.es_exception()
            app.log_listener = None
        # Start a new listener.
        g.es_print('Starting log_listener.py')
        path = g.os_path_finalize_join(app.loadDir,
            '..', 'external', 'log_listener.py')
        app.log_listener = subprocess.Popen(
            [sys.executable, path],
            shell=False,
            universal_newlines=True,
        )
    #@+node:ekr.20171118024827.1: *3* app.makeAllBindings
    def makeAllBindings(self):
        """
        LeoApp.makeAllBindings:

        Call c.k.makeAllBindings for all open commanders c.
        """
        app = self
        for c in app.commanders():
            c.k.makeAllBindings()
    #@+node:ekr.20031218072017.2188: *3* app.newCommander
    def newCommander(self, fileName,
        gui=None,
        parentFrame=None,
        previousSettings=None,
        relativeFileName=None,
    ):
        """Create a commander and its view frame for the Leo main window."""
        # Create the commander and its subcommanders.
        # This takes about 3/4 sec when called by the leoBridge module.
        # Timeit reports 0.0175 sec when using a nullGui.
        from leo.core import leoCommands
        c = leoCommands.Commands(fileName,
            gui=gui,
            parentFrame=parentFrame,
            previousSettings=previousSettings,
            relativeFileName=relativeFileName,
        )
        return c
    #@+node:ekr.20120304065838.15588: *3* app.selectLeoWindow
    def selectLeoWindow(self, c):
        frame = c.frame
        frame.deiconify()
        frame.lift()
        c.setLog()
        master = getattr(frame.top, 'leo_master', None)
        if master:
            # master is a TabbedTopLevel.
            # Selecting the new tab ensures focus is set.
            master.select(c)
        if 1:
            c.initialFocusHelper()
        else:
            c.bodyWantsFocus()
        c.outerUpdate()
    #@-others
#@+node:ekr.20120209051836.10242: ** class LoadManager
class LoadManager:
    """A class to manage loading .leo files, including configuration files."""
    #@+others
    #@+node:ekr.20120214060149.15851: *3*  LM.ctor
    def __init__(self):

        #
        # Global settings & shortcuts dicts...
        # The are the defaults for computing settings and shortcuts for all loaded files.
        #
        self.globalSettingsDict = None
            # A g.TypedDict: the join of settings in leoSettings.leo & myLeoSettings.leo
        self.globalBindingsDict = None
            # A g.TypedDict: the join of shortcuts in leoSettings.leo & myLeoSettings.leo.
        #
        # LoadManager ivars corresponding to user options...
        #
        self.files = []
            # List of files to be loaded.
        self.options = {}
            # Dictionary of user options. Keys are option names.
        self.old_argv = []
            # A copy of sys.argv for debugging.
        self.more_cmdline_files = False
            # True when more files remain on the command line to be
            # loaded.  If the user is answering "No" to each file as Leo asks
            # "file already open, open again", this must be False for
            # a complete exit to be appropriate (finish_quit=True param for
            # closeLeoWindow())
        #
        # Themes.
        self.leo_settings_c = None
        self.leo_settings_path = None
        self.my_settings_c = None
        self.my_settings_path = None
        self.theme_c = None
            # #1374.
        self.theme_path = None
    #@+node:ekr.20120211121736.10812: *3* LM.Directory & file utils
    #@+node:ekr.20120219154958.10481: *4* LM.completeFileName
    def completeFileName(self, fileName):
        fileName = g.toUnicode(fileName)
        fileName = g.os_path_finalize(fileName)
        # 2011/10/12: don't add .leo to *any* file.
        return fileName
    #@+node:ekr.20120209051836.10372: *4* LM.computeLeoSettingsPath
    def computeLeoSettingsPath(self):
        """Return the full path to leoSettings.leo."""
        # lm = self
        join = g.os_path_finalize_join
        settings_fn = 'leoSettings.leo'
        table = (
            # First, leoSettings.leo in the home directories.
            join(g.app.homeDir, settings_fn),
            join(g.app.homeLeoDir, settings_fn),
            # Last, leoSettings.leo in leo/config directory.
            join(g.app.globalConfigDir, settings_fn)
        )
        for path in table:
            if g.os_path_exists(path):
                break
        else:
            path = None
        return path
    #@+node:ekr.20120209051836.10373: *4* LM.computeMyLeoSettingsPath
    def computeMyLeoSettingsPath(self):
        """
        Return the full path to myLeoSettings.leo.

        The "footnote": Get the local directory from lm.files[0]
        """
        lm = self
        join = g.os_path_finalize_join
        settings_fn = 'myLeoSettings.leo'
        # This seems pointless: we need a machine *directory*.
        # For now, however, we'll keep the existing code as is.
        machine_fn = lm.computeMachineName() + settings_fn
        # First, compute the directory of the first loaded file.
        # All entries in lm.files are full, absolute paths.
        localDir = g.os_path_dirname(lm.files[0]) if lm.files else ''
        table = (
            # First, myLeoSettings.leo in the local directory
            join(localDir, settings_fn),
            # Next, myLeoSettings.leo in the home directories.
            join(g.app.homeDir, settings_fn),
            join(g.app.homeLeoDir, settings_fn),
            # Next, <machine-name>myLeoSettings.leo in the home directories.
            join(g.app.homeDir, machine_fn),
            join(g.app.homeLeoDir, machine_fn),
            # Last, leoSettings.leo in leo/config directory.
            join(g.app.globalConfigDir, settings_fn),
        )
        for path in table:
            if g.os_path_exists(path):
                break
        else:
            path = None
        return path
    #@+node:ekr.20120209051836.10252: *4* LM.computeStandardDirectories & helpers
    def computeStandardDirectories(self):
        """
        Compute the locations of standard directories and
        set the corresponding ivars.
        """
        lm = self
        join = os.path.join
        g.app.loadDir = lm.computeLoadDir()
        g.app.globalConfigDir = lm.computeGlobalConfigDir()
        g.app.homeDir = lm.computeHomeDir()
        g.app.homeLeoDir = lm.computeHomeLeoDir()
        g.app.leoDir = lm.computeLeoDir()
        # These use g.app.loadDir...
        g.app.extensionsDir = join(g.app.loadDir, '..', 'extensions')
        g.app.leoEditorDir = join(g.app.loadDir, '..', '..')
        g.app.testDir = join(g.app.loadDir, '..', 'test')
    #@+node:ekr.20120209051836.10253: *5* LM.computeGlobalConfigDir
    def computeGlobalConfigDir(self):
        leo_config_dir = getattr(sys, 'leo_config_directory', None)
        if leo_config_dir:
            theDir = leo_config_dir
        else:
            theDir = os.path.join(g.app.loadDir, "..", "config")
        if theDir:
            theDir = os.path.abspath(theDir)
        if not theDir or not g.os_path_exists(theDir) or not g.os_path_isdir(theDir):
            theDir = None
        return theDir
    #@+node:ekr.20120209051836.10254: *5* LM.computeHomeDir
    def computeHomeDir(self):
        """Returns the user's home directory."""
        home = os.path.expanduser("~")
            # Windows searches the HOME, HOMEPATH and HOMEDRIVE
            # environment vars, then gives up.
        if home and len(home) > 1 and home[0] == '%' and home[-1] == '%':
            # Get the indirect reference to the true home.
            home = os.getenv(home[1:-1], default=None)
        if home:
            # Important: This returns the _working_ directory if home is None!
            # This was the source of the 4.3 .leoID.txt problems.
            home = g.os_path_finalize(home)
            if (not g.os_path_exists(home) or not g.os_path_isdir(home)):
                home = None
        return home
    #@+node:ekr.20120209051836.10260: *5* LM.computeHomeLeoDir
    def computeHomeLeoDir(self):
        # lm = self
        homeLeoDir = g.os_path_finalize_join(g.app.homeDir, '.leo')
        if g.os_path_exists(homeLeoDir):
            return homeLeoDir
        ok = g.makeAllNonExistentDirectories(homeLeoDir)
        return homeLeoDir if ok else ''  # #1450
    #@+node:ekr.20120209051836.10255: *5* LM.computeLeoDir
    def computeLeoDir(self):
        # lm = self
        loadDir = g.app.loadDir
        return g.os_path_dirname(loadDir)
            # We don't want the result in sys.path
    #@+node:ekr.20120209051836.10256: *5* LM.computeLoadDir
    def computeLoadDir(self):
        """Returns the directory containing leo.py."""
        try:
            # Fix a hangnail: on Windows the drive letter returned by
            # __file__ is randomly upper or lower case!
            # The made for an ugly recent files list.
            path = g.__file__  # was leo.__file__
            if path:
                # Possible fix for bug 735938:
                # Do the following only if path exists.
                #@+<< resolve symlinks >>
                #@+node:ekr.20120209051836.10257: *6* << resolve symlinks >>
                if path.endswith('pyc'):
                    srcfile = path[:-1]
                    if os.path.islink(srcfile):
                        path = os.path.realpath(srcfile)
                #@-<< resolve symlinks >>
                if sys.platform == 'win32':
                    if len(path) > 2 and path[1] == ':':
                        # Convert the drive name to upper case.
                        path = path[0].upper() + path[1:]
                path = g.os_path_finalize(path)
                loadDir = g.os_path_dirname(path)
            else: loadDir = None
            if (
                not loadDir or
                not g.os_path_exists(loadDir) or
                not g.os_path_isdir(loadDir)
            ):
                loadDir = os.getcwd()
                # From Marc-Antoine Parent.
                if loadDir.endswith("Contents/Resources"):
                    loadDir += "/leo/plugins"
                else:
                    g.pr("Exception getting load directory")
            loadDir = g.os_path_finalize(loadDir)
            return loadDir
        except Exception:
            print("Exception getting load directory")
            raise
    #@+node:ekr.20120213164030.10697: *5* LM.computeMachineName
    def computeMachineName(self):
        """Return the name of the current machine, i.e, HOSTNAME."""
        # This is prepended to leoSettings.leo or myLeoSettings.leo
        # to give the machine-specific setting name.
        # How can this be worth doing??
        try:
            name = os.getenv('HOSTNAME')
            if not name:
                name = os.getenv('COMPUTERNAME')
            if not name:
                import socket
                name = socket.gethostname()
        except Exception:
            name = ''
        return name
    #@+node:ekr.20180318120148.1: *4* LM.computeThemeDirectories
    def computeThemeDirectories(self):
        """
        Return a list of *existing* directories that might contain theme .leo files.
        """
        join = g.os_path_finalize_join
        home = g.app.homeDir
        leo = join(g.app.loadDir, '..')
        table = [
            home,
            join(home, 'themes'),
            join(home, '.leo'),
            join(home, '.leo', 'themes'),
            join(leo, 'themes'),
        ]
        return [g.os_path_normslashes(z) for z in table if g.os_path_exists(z)]
            # Make sure home has normalized slashes.
    #@+node:ekr.20180318133620.1: *4* LM.computeThemeFilePath & helper
    def computeThemeFilePath(self):
        """
        Return the absolute path to the theme .leo file, resolved using the search order for themes.

        1. Use the --theme command-line option if it exists.

        2. Otherwise, preload the first .leo file.
           Load the file given by @string theme-name setting.

        3. Finally, look up the @string theme-name in the already-loaded, myLeoSettings.leo.
           Load the file if setting exists.  Otherwise return None.
        """
        trace = 'themes' in g.app.db
        lm = self
        resolve = self.resolve_theme_path
        #
        # Step 1: Use the --theme command-line options if it exists
        path = resolve(lm.options.get('theme_path'), tag='--theme')
        if path:
            # Caller (LM.readGlobalSettingsFiles) sets lm.theme_path
            if trace: g.trace('--theme:', path)
            return path
        #
        # Step 2: look for the @string theme-name setting in the first loaded file.
        path = lm.files and lm.files[0]
        if path and g.os_path_exists(path):
            # Tricky: we must call lm.computeLocalSettings *here*.
            theme_c = lm.openSettingsFile(path)
            if theme_c:
                settings_d, junk_shortcuts_d = lm.computeLocalSettings(
                    c=theme_c,
                    settings_d=lm.globalSettingsDict,
                    bindings_d=lm.globalBindingsDict,
                    localFlag=False,
                )
                setting = settings_d.get_string_setting('theme-name')
                if setting:
                    tag = theme_c.shortFileName()
                    path = resolve(setting, tag=tag)
                    if path:
                        # Caller (LM.readGlobalSettingsFiles) sets lm.theme_path
                        if trace: g.trace("First loaded file", theme_c.shortFileName(), path)
                        return path
        #
        # Step 3: use the @string theme-name setting in myLeoSettings.leo.
        # Note: the setting should *never* appear in leoSettings.leo!
        setting = lm.globalSettingsDict.get_string_setting('theme-name')
        tag = 'myLeoSettings.leo'
        path = resolve(setting, tag=tag)
        if trace: g.trace("myLeoSettings.leo", path)
        return path
    #@+node:ekr.20180321124503.1: *5* LM.resolve_theme_path
    def resolve_theme_path(self, fn, tag):
        """Search theme directories for the given .leo file."""
        if not fn or fn.lower().strip() == 'none':
            return None
        if not fn.endswith('.leo'):
            fn += '.leo'
        for directory in self.computeThemeDirectories():
            path = g.os_path_join(directory, fn)
                # Normalizes slashes, etc.
            if g.os_path_exists(path):
                return path
        print(f"theme .leo file not found: {fn}")
        return None
    #@+node:ekr.20120211121736.10772: *4* LM.computeWorkbookFileName
    def computeWorkbookFileName(self):
        """
        Return full path to the workbook.

        Return None if testing, or in batch mode, or if the containing
        directory does not exist.
        """
        # lm = self
        # Never create a workbook during unit tests or in batch mode.
        if g.unitTesting or g.app.batchMode:
            return None
        fn = g.app.config.getString(setting='default_leo_file') or '~/.leo/workbook.leo'
        fn = g.os_path_finalize(fn)
        directory = g.os_path_finalize(os.path.dirname(fn))
        # #1415.
        return fn if os.path.exists(directory) else None
    #@+node:ekr.20120219154958.10485: *4* LM.reportDirectories
    def reportDirectories(self):
        """Report directories."""
        # The cwd changes later, so it would be misleading to report it here.
        for kind, theDir in (
            ('home', g.app.homeDir),
            ('leo-editor', g.app.leoEditorDir),
            ('load', g.app.loadDir),
            ('config', g.app.globalConfigDir),
        ):
            # g.blue calls g.es_print, and that's annoying.
            g.es(f"{kind:>10}:", os.path.normpath(theDir), color='blue')
    #@+node:ekr.20120215062153.10740: *3* LM.Settings
    #@+node:ekr.20120130101219.10182: *4* LM.computeBindingLetter
    def computeBindingLetter(self, c, path):
        lm = self
        if not path:
            return 'D'
        path = path.lower()
        table = (
            ('M', 'myLeoSettings.leo'),
            (' ', 'leoSettings.leo'),
            ('F', c.shortFileName()),
        )
        for letter, path2 in table:
            if path2 and path.endswith(path2.lower()):
                return letter
        if lm.theme_path and path.endswith(lm.theme_path.lower()):
            return 'T'
        if path == 'register-command' or path.find('mode') > -1:
            return '@'
        return 'D'
    #@+node:ekr.20120223062418.10421: *4* LM.computeLocalSettings
    def computeLocalSettings(self, c, settings_d, bindings_d, localFlag):
        """
        Merge the settings dicts from c's outline into *new copies of*
        settings_d and bindings_d.
        """
        lm = self
        shortcuts_d2, settings_d2 = lm.createSettingsDicts(c, localFlag)
        assert bindings_d
        assert settings_d
        if settings_d2:
            if g.app.trace_setting:
                key = g.app.config.munge(g.app.trace_setting)
                val = settings_d2.d.get(key)
                if val:
                    fn = g.shortFileName(val.path)
                    g.es_print(
                        f"--trace-setting: in {fn:20}: "
                        f"@{val.kind} {g.app.trace_setting}={val.val}")
            settings_d = settings_d.copy()
            settings_d.update(settings_d2)
        if shortcuts_d2:
            bindings_d = lm.mergeShortcutsDicts(c, bindings_d, shortcuts_d2, localFlag)
        return settings_d, bindings_d
    #@+node:ekr.20121126202114.3: *4* LM.createDefaultSettingsDicts
    def createDefaultSettingsDicts(self):
        """Create lm.globalSettingsDict & lm.globalBindingsDict."""
        settings_d = g.app.config.defaultsDict
        assert isinstance(settings_d, g.TypedDict), settings_d
        settings_d.setName('lm.globalSettingsDict')
        bindings_d = g.TypedDict(  # was TypedDictOfLists.
            name='lm.globalBindingsDict',
            keyType=type('s'),
            valType=g.BindingInfo,
        )
        return settings_d, bindings_d
    #@+node:ekr.20120214165710.10726: *4* LM.createSettingsDicts
    def createSettingsDicts(self, c, localFlag):

        from leo.core import leoConfig
        if c:
            parser = leoConfig.SettingsTreeParser(c, localFlag)
                # returns the *raw* shortcutsDict, not a *merged* shortcuts dict.
            shortcutsDict, settingsDict = parser.traverse()
            return shortcutsDict, settingsDict
        return None, None
    #@+node:ekr.20120223062418.10414: *4* LM.getPreviousSettings
    def getPreviousSettings(self, fn):
        """
        Return the settings in effect for fn. Typically, this involves
        pre-reading fn.
        """
        lm = self
        settingsName = f"settings dict for {g.shortFileName(fn)}"
        shortcutsName = f"shortcuts dict for {g.shortFileName(fn)}"
        # A special case: settings in leoSettings.leo do *not* override
        # the global settings, that is, settings in myLeoSettings.leo.
        isLeoSettings = g.shortFileName(fn).lower() == 'leosettings.leo'
        exists = g.os_path_exists(fn)
        if fn and exists and lm.isLeoFile(fn) and not isLeoSettings:
            # Open the file usinging a null gui.
            try:
                g.app.preReadFlag = True
                c = lm.openSettingsFile(fn)
            finally:
                g.app.preReadFlag = False
            # Merge the settings from c into *copies* of the global dicts.
            d1, d2 = lm.computeLocalSettings(c,
                lm.globalSettingsDict,
                lm.globalBindingsDict,
                localFlag=True)
                    # d1 and d2 are copies.
            d1.setName(settingsName)
            d2.setName(shortcutsName)
            return PreviousSettings(d1, d2)
        #
        # The file does not exist, or is not valid.
        # Get the settings from the globals settings dicts.
        d1 = lm.globalSettingsDict.copy(settingsName)
        d2 = lm.globalBindingsDict.copy(shortcutsName)
        return PreviousSettings(d1, d2)
    #@+node:ekr.20120214132927.10723: *4* LM.mergeShortcutsDicts & helpers
    def mergeShortcutsDicts(self, c, old_d, new_d, localFlag):
        """
        Create a new dict by overriding all shortcuts in old_d by shortcuts in new_d.

        Both old_d and new_d remain unchanged.
        """
        lm = self
        if not old_d: return new_d
        if not new_d: return old_d
        bi_list = new_d.get(g.app.trace_setting)
        if bi_list:
            # This code executed only if g.app.trace_setting exists.
            for bi in bi_list:
                fn = bi.kind.split(' ')[-1]
                stroke = c.k.prettyPrintKey(bi.stroke)
                if bi.pane and bi.pane != 'all':
                    pane = f" in {bi.pane} panes"
                else:
                    pane = ''
        inverted_old_d = lm.invert(old_d)
        inverted_new_d = lm.invert(new_d)
        # #510 & #327: always honor --trace-binding here.
        if g.app.trace_binding:
            binding = g.app.trace_binding
            # First, see if the binding is for a command. (Doesn't work for plugin commands).
            if localFlag and binding in c.k.killedBindings:
                g.es_print(
                    f"--trace-binding: {c.shortFileName()} "
                    f"sets {binding} to None")
            elif localFlag and binding in c.commandsDict:
                d = c.k.computeInverseBindingDict()
                g.trace(
                    f"--trace-binding: {c.shortFileName():20} "
                    f"binds {binding} to {d.get(binding) or []}")
            else:
                binding = g.app.trace_binding
                stroke = g.KeyStroke(binding)
                bi_list = inverted_new_d.get(stroke)
                if bi_list:
                    print('')
                    for bi in bi_list:
                        fn = bi.kind.split(' ')[-1]  # bi.kind #
                        stroke2 = c.k.prettyPrintKey(stroke)
                        if bi.pane and bi.pane != 'all':
                            pane = f" in {bi.pane} panes"
                        else:
                            pane = ''
                        g.es_print(
                            f"--trace-binding: {fn:20} binds {stroke2} "
                            f"to {bi.commandName:>20}{pane}")
                    print('')
        # Fix bug 951921: check for duplicate shortcuts only in the new file.
        lm.checkForDuplicateShortcuts(c, inverted_new_d)
        inverted_old_d.update(inverted_new_d)  # Updates inverted_old_d in place.
        result = lm.uninvert(inverted_old_d)
        return result
    #@+node:ekr.20120311070142.9904: *5* LM.checkForDuplicateShortcuts
    def checkForDuplicateShortcuts(self, c, d):
        """
        Check for duplicates in an "inverted" dictionary d
        whose keys are strokes and whose values are lists of BindingInfo nodes.

        Duplicates happen only if panes conflict.
        """
        # lm = self
        # Fix bug 951921: check for duplicate shortcuts only in the new file.
        for ks in sorted(list(d.keys())):
            duplicates, panes = [], ['all']
            aList = d.get(ks)
                # A list of bi objects.
            aList2 = [z for z in aList if not z.pane.startswith('mode')]
            if len(aList) > 1:
                for bi in aList2:
                    if bi.pane in panes:
                        duplicates.append(bi)
                    else:
                        panes.append(bi.pane)
            if duplicates:
                bindings = list(set([z.stroke.s for z in duplicates]))
                if len(bindings) == 1:
                    kind = 'duplicate, (not conflicting)'
                else:
                    kind = 'conflicting'
                g.es_print(f"{kind} key bindings in {c.shortFileName()}")
                for bi in aList2:
                    g.es_print(f"{bi.pane:6} {bi.stroke.s} {bi.commandName}")
    #@+node:ekr.20120214132927.10724: *5* LM.invert
    def invert(self, d):
        """
        Invert a shortcut dict whose keys are command names,
        returning a dict whose keys are strokes.
        """
        result = g.TypedDict(  # was TypedDictOfLists.
            name=f"inverted {d.name()}",
            keyType=g.KeyStroke,
            valType=g.BindingInfo,
        )
        for commandName in d.keys():
            for bi in d.get(commandName, []):
                stroke = bi.stroke  # This is canonicalized.
                bi.commandName = commandName  # Add info.
                assert stroke
                result.add_to_list(stroke, bi)
        return result
    #@+node:ekr.20120214132927.10725: *5* LM.uninvert
    def uninvert(self, d):
        """
        Uninvert an inverted shortcut dict whose keys are strokes,
        returning a dict whose keys are command names.
        """
        assert d.keyType == g.KeyStroke, d.keyType
        result = g.TypedDict(  # was TypedDictOfLists.
            name=f"uninverted {d.name()}",
            keyType=type('commandName'),
            valType=g.BindingInfo,
        )
        for stroke in d.keys():
            for bi in d.get(stroke, []):
                commandName = bi.commandName
                assert commandName
                result.add_to_list(commandName, bi)
        return result
    #@+node:ekr.20120222103014.10312: *4* LM.openSettingsFile
    def openSettingsFile(self, fn):
        """
        Open a settings file with a null gui.  Return the commander.

        The caller must init the c.config object.
        """
        lm = self
        if not fn:
            return None
        theFile = lm.openAnyLeoFile(fn)
        if not theFile:
            return None  # Fix #843.
        if not any([g.app.unitTesting, g.app.silentMode, g.app.batchMode]):
            # This occurs early in startup, so use the following.
            s = f"reading settings in {os.path.normpath(fn)}"
            if 'startup' in g.app.debug:
                print(s)
            g.es(s, color='blue')
            # A useful trace.
            # g.trace('%20s' % g.shortFileName(fn), g.callers(3))
        # Changing g.app.gui here is a major hack.  It is necessary.
        oldGui = g.app.gui
        g.app.gui = g.app.nullGui
        c = g.app.newCommander(fn)
        frame = c.frame
        frame.log.enable(False)
        g.app.lockLog()
        g.app.openingSettingsFile = True
        try:
            ok = c.fileCommands.openLeoFile(theFile, fn,
                    readAtFileNodesFlag=False, silent=True)
                        # closes theFile.
        finally:
            g.app.openingSettingsFile = False
        g.app.unlockLog()
        c.openDirectory = frame.openDirectory = g.os_path_dirname(fn)
        g.app.gui = oldGui
        return c if ok else None
    #@+node:ekr.20120213081706.10382: *4* LM.readGlobalSettingsFiles
    def readGlobalSettingsFiles(self):
        """
        Read leoSettings.leo and myLeoSettings.leo using a null gui.

        New in Leo 6.1: this sets ivars for the ActiveSettingsOutline class.
        """
        trace = 'themes' in g.app.debug
        lm = self
        # Open the standard settings files with a nullGui.
        # Important: their commanders do not exist outside this method!
        old_commanders = g.app.commanders()
        lm.leo_settings_path = lm.computeLeoSettingsPath()
        lm.my_settings_path = lm.computeMyLeoSettingsPath()
        lm.leo_settings_c = lm.openSettingsFile(self.leo_settings_path)
        lm.my_settings_c = lm.openSettingsFile(self.my_settings_path)
        commanders = [lm.leo_settings_c, lm.my_settings_c]
        commanders = [z for z in commanders if z]
        settings_d, bindings_d = lm.createDefaultSettingsDicts()
        for c in commanders:
            # Merge the settings dicts from c's outline into
            # *new copies of* settings_d and bindings_d.
            settings_d, bindings_d = lm.computeLocalSettings(
                c, settings_d, bindings_d, localFlag=False)
        # Adjust the name.
        bindings_d.setName('lm.globalBindingsDict')
        lm.globalSettingsDict = settings_d
        lm.globalBindingsDict = bindings_d
        # Add settings from --theme or @string theme-name files.
        # This must be done *after* reading myLeoSettigns.leo.
        lm.theme_path = lm.computeThemeFilePath()
        if lm.theme_path:
            lm.theme_c = lm.openSettingsFile(lm.theme_path)
            if lm.theme_c:
                # Merge theme_c's settings into globalSettingsDict.
                settings_d, junk_shortcuts_d = lm.computeLocalSettings(
                    lm.theme_c, settings_d, bindings_d, localFlag=False)
                lm.globalSettingsDict = settings_d
                # Set global vars
                g.app.theme_directory = g.os_path_dirname(lm.theme_path)
                    # Used by the StyleSheetManager.
                if trace: g.trace('g.app.theme_directory', g.app.theme_directory)
        # Clear the cache entries for the commanders.
        # This allows this method to be called outside the startup logic.
        for c in commanders:
            if c not in old_commanders:
                g.app.forgetOpenFile(c.fileName())
    #@+node:ekr.20120214165710.10838: *4* LM.traceSettingsDict
    def traceSettingsDict(self, d, verbose=False):
        if verbose:
            print(d)
            for key in sorted(list(d.keys())):
                gs = d.get(key)
                print(f"{key:35} {g.shortFileName(gs.path):17} {gs.val}")
            if d: print('')
        else:
            # print(d)
            print(f"{d.name} {len(d.d.keys())}")
    #@+node:ekr.20120214165710.10822: *4* LM.traceShortcutsDict
    def traceShortcutsDict(self, d, verbose=False):
        if verbose:
            print(d)
            for key in sorted(list(d.keys())):
                val = d.get(key)
                # print('%20s %s' % (key,val.dump()))
                print(f"{key:35} {[z.stroke for z in val]}")
            if d: print('')
        else:
            print(d)
    #@+node:ekr.20120219154958.10452: *3* LM.load & helpers
    def load(self, fileName=None, pymacs=None):
        """This is Leo's main startup method."""
        lm = self
        #
        # Phase 1: before loading plugins.
        # Scan options, set directories and read settings.
        t1 = time.process_time()
        print('')  # Give some separation for the coming traces.
        if not lm.isValidPython():
            return
        lm.doPrePluginsInit(fileName, pymacs)
            # sets lm.options and lm.files
        g.app.computeSignon()
        g.app.printSignon()
        if lm.options.get('version'):
            return
        if not g.app.gui:
            return
        g.app.disable_redraw = True
            # Disable redraw until all files are loaded.
        #
        # Phase 2: load plugins: the gui has already been set.
        t2 = time.process_time()
        g.doHook("start1")
        t3 = time.process_time()
        if g.app.killed:
            return
        g.app.idleTimeManager.start()
        #
        # Phase 3: after loading plugins. Create one or more frames.
        t3 = time.process_time()
        if lm.options.get('script') and not self.files:
            ok = True
        else:
            ok = lm.doPostPluginsInit()
            # Fix #579: Key bindings don't take for commands defined in plugins
            g.app.makeAllBindings()
            if ok and g.app.diff:
                lm.doDiff()
        if not ok:
            return
        g.es('')  # Clears horizontal scrolling in the log pane.
        if g.app.listen_to_log_flag:
            g.app.listenToLog()
        if 'startup' in g.app.debug:
            t4 = time.process_time()
            print('')
            g.es_print(f"settings:{t2 - t1:5.2f} sec")
            g.es_print(f" plugins:{t3 - t2:5.2f} sec")
            g.es_print(f"   files:{t4 - t3:5.2f} sec")
            g.es_print(f"   total:{t4 - t1:5.2f} sec")
            print('')
        # #1128: support for restart-leo.
        if not g.app.start_minimized:
            try:  # Careful: we may be unit testing.
                g.app.log.c.frame.bringToFront()
            except Exception:
                pass
        g.app.gui.runMainLoop()
        # For scripts, the gui is a nullGui.
        # and the gui.setScript has already been called.
    #@+node:ekr.20150225133846.7: *4* LM.doDiff
    def doDiff(self):
        """Support --diff option after loading Leo."""
        if len(self.old_argv[2:]) == 2:
            pass  # c.editFileCommands.compareAnyTwoFiles gives a message.
        else:
            # This is an unusual situation.
            g.es('--diff mode. sys.argv[2:]...', color='red')
            for z in self.old_argv[2:]:
                g.es(g.shortFileName(z) if z else repr(z), color='blue')
        commanders = g.app.commanders()
        if len(commanders) == 2:
            c = commanders[0]
            c.editFileCommands.compareAnyTwoFiles(event=None)
    #@+node:ekr.20120219154958.10487: *4* LM.doPostPluginsInit & helpers
    def doPostPluginsInit(self):
        """Create a Leo window for each file in the lm.files list."""
        # Clear g.app.initing _before_ creating commanders.
        lm = self
        g.app.initing = False  # "idle" hooks may now call g.app.forceShutdown.
        # Create the main frame.Show it and all queued messages.
        c = c1 = fn = None
        if lm.files:
            try:  # #1403.
                for n, fn in enumerate(lm.files):
                    lm.more_cmdline_files = n < len(lm.files) - 1
                    c = lm.loadLocalFile(fn, gui=g.app.gui, old_c=None)
                        # Returns None if the file is open in another instance of Leo.
                    if c and not c1:  # #1416:
                        c1 = c
            except Exception:
                g.es_print(f"Unexpected exception reading {fn!r}")
                g.es_exception()
                c = None
        # Load (and save later) a session *only* if the command line contains no files.
        g.app.loaded_session = not lm.files
        if g.app.sessionManager and g.app.loaded_session:
            try:  # #1403.
                aList = g.app.sessionManager.load_snapshot()
                if aList:
                    g.app.sessionManager.load_session(c1, aList)
                    # #659.
                    if g.app.windowList:
                        c = c1 = g.app.windowList[0].c
                    else:
                        c = c1 = None
            except Exception:
                g.es_print('Can not load session')
                g.es_exception()
        # Enable redraws.
        g.app.disable_redraw = False
        if not c1:
            try:  # #1403.
                c1 = lm.openEmptyWorkBook()
                    # Calls LM.loadLocalFile.
            except Exception:
                g.es_print('Can not create empty workbook')
                g.es_exception()
        c = c1
        if not c:
            # Leo is out of options: Force an immediate exit.
            return False
        # #199.
        g.app.runAlreadyOpenDialog(c1)
        #
        # Final inits...
        # For qt gui, select the first-loaded tab.
        if hasattr(g.app.gui, 'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory, 'setTabForCommander'):
                factory.setTabForCommander(c)
        g.app.logInited = True
        g.app.initComplete = True
        c.setLog()
        c.redraw()
        g.doHook("start2", c=c, p=c.p, fileName=c.fileName())
        c.initialFocusHelper()
        screenshot_fn = lm.options.get('screenshot_fn')
        if screenshot_fn:
            lm.make_screen_shot(screenshot_fn)
            return False  # Force an immediate exit.
        return True
    #@+node:ekr.20120219154958.10489: *5* LM.make_screen_shot
    def make_screen_shot(self, fn):
        """Create a screenshot of the present Leo outline and save it to path."""
        if g.app.gui.guiName() == 'qt':
            m = g.loadOnePlugin('screenshots')
            m.make_screen_shot(fn)
    #@+node:ekr.20131028155339.17098: *5* LM.openEmptyWorkBook
    def openEmptyWorkBook(self):
        """Open an empty frame and paste the contents of CheatSheet.leo into it."""
        lm = self
        # Create an empty frame.
        fn = lm.computeWorkbookFileName()
        if not fn:
            return None  # #1415
        c = lm.loadLocalFile(fn, gui=g.app.gui, old_c=None)
        if not c:
            return None  # #1201: AttributeError below.
        # Open the cheatsheet, but not in batch mode.
        if not g.app.batchMode and not g.os_path_exists(fn):
            # #933: Save clipboard.
            old_clipboard = g.app.gui.getTextFromClipboard()
            # Paste the contents of CheetSheet.leo into c.
            c2 = c.openCheatSheet(redraw=False)
            if c2:
                for p2 in c2.rootPosition().self_and_siblings():
                    c2.setCurrentPosition(p2)  # 1380
                    c2.copyOutline()
                    p = c.pasteOutline()
                    # #1380 & #1381: Add guard & use vnode methods to prevent redraw.
                    if p:
                        c.setCurrentPosition(p)  # 1380
                        p.v.contract()
                        p.v.clearDirty()
                c2.close(new_c=c)
                # Delete the dummy first node.
                root = c.rootPosition()
                root.doDelete(newNode=root.next())
                c.target_language = 'rest'
                    # Settings not parsed the first time.
                c.clearChanged()
                c.redraw(c.rootPosition())  # # 1380: Select the root.
            # #933: Restore clipboard
            g.app.gui.replaceClipboardWith(old_clipboard)
        return c
    #@+node:ekr.20120219154958.10477: *4* LM.doPrePluginsInit & helpers
    def doPrePluginsInit(self, fileName, pymacs):
        """ Scan options, set directories and read settings."""
        lm = self
        lm.computeStandardDirectories()
        lm.adjustSysPath()
            # A do-nothing.
        # Scan the options as early as possible.
        lm.options = options = lm.scanOptions(fileName, pymacs)
            # also sets lm.files.
        if options.get('version'):
            return
        script = options.get('script')
        verbose = script is None
        # Init the app.
        lm.initApp(verbose)
        g.app.setGlobalDb()
        if verbose:
            lm.reportDirectories()
        # Read settings *after* setting g.app.config and *before* opening plugins.
        # This means if-gui has effect only in per-file settings.
        lm.readGlobalSettingsFiles()
            # reads only standard settings files, using a null gui.
            # uses lm.files[0] to compute the local directory
            # that might contain myLeoSettings.leo.
        # Read the recent files file.
        localConfigFile = lm.files[0] if lm.files else None
        g.app.recentFilesManager.readRecentFiles(localConfigFile)
        # Create the gui after reading options and settings.
        lm.createGui(pymacs)
        # We can't print the signon until we know the gui.
        g.app.computeSignon()  # Set app.signon/signon1 for commanders.
    #@+node:ekr.20170302093006.1: *5* LM.createAllImporterData & helpers
    def createAllImporterData(self):
        """
        New in Leo 5.5:

        Create global data structures describing importers and writers.
        """
        assert g.app.loadDir
            # This is the only data required.
        self.createWritersData()
            # Was an AtFile method.
        self.createImporterData()
            # Was a LeoImportCommands method.
    #@+node:ekr.20140724064952.18037: *6* LM.createImporterData & helper
    def createImporterData(self):
        """Create the data structures describing importer plugins."""
        # Allow plugins to be defined in ~/.leo/plugins.
        plugins1 = g.os_path_finalize_join(g.app.homeDir, '.leo', 'plugins')
        plugins2 = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
        for kind, plugins in (('home', plugins1), ('leo', plugins2)):
            pattern = g.os_path_finalize_join(
                g.app.loadDir, '..', 'plugins', 'importers', '*.py')
            for fn in g.glob_glob(pattern):
                sfn = g.shortFileName(fn)
                if sfn != '__init__.py':
                    try:
                        module_name = sfn[:-3]
                        # Important: use importlib to give imported modules
                        # their fully qualified names.
                        m = importlib.import_module(
                            f"leo.plugins.importers.{module_name}")
                        self.parse_importer_dict(sfn, m)
                        # print('createImporterData', m.__name__)
                    except Exception:
                        g.warning(f"can not import leo.plugins.importers.{module_name}")
    #@+node:ekr.20140723140445.18076: *7* LM.parse_importer_dict
    def parse_importer_dict(self, sfn, m):
        """
        Set entries in g.app.classDispatchDict, g.app.atAutoDict and
        g.app.atAutoNames using entries in m.importer_dict.
        """
        importer_d = getattr(m, 'importer_dict', None)
        if importer_d:
            at_auto = importer_d.get('@auto', [])
            scanner_class = importer_d.get('class', None)
            # scanner_name = scanner_class.__name__
            extensions = importer_d.get('extensions', [])
            if at_auto:
                # Make entries for each @auto type.
                d = g.app.atAutoDict
                for s in at_auto:
                    d[s] = scanner_class
                    g.app.atAutoDict[s] = scanner_class
                    g.app.atAutoNames.add(s)
            if extensions:
                # Make entries for each extension.
                d = g.app.classDispatchDict
                for ext in extensions:
                    d[ext] = scanner_class
        elif sfn not in (
            # These are base classes, not real plugins.
            'basescanner.py',
            'linescanner.py',
        ):
            g.warning(f"leo/plugins/importers/{sfn} has no importer_dict")
    #@+node:ekr.20140728040812.17990: *6* LM.createWritersData & helper
    def createWritersData(self):
        """Create the data structures describing writer plugins."""
        trace = False and 'createWritersData' not in g.app.debug_dict
            # Do *not* remove this trace.
        if trace:
            # Suppress multiple traces.
            g.app.debug_dict['createWritersData'] = True
        g.app.writersDispatchDict = {}
        g.app.atAutoWritersDict = {}
        plugins1 = g.os_path_finalize_join(g.app.homeDir, '.leo', 'plugins')
        plugins2 = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
        for kind, plugins in (('home', plugins1), ('leo', plugins2)):
            pattern = g.os_path_finalize_join(g.app.loadDir,
                '..', 'plugins', 'writers', '*.py')
            for fn in g.glob_glob(pattern):
                sfn = g.shortFileName(fn)
                if sfn != '__init__.py':
                    try:
                        # Important: use importlib to give imported modules their fully qualified names.
                        m = importlib.import_module(f"leo.plugins.writers.{sfn[:-3]}")
                        self.parse_writer_dict(sfn, m)
                    except Exception:
                        g.es_exception()
                        g.warning(f"can not import leo.plugins.writers.{sfn}")
        if trace:
            g.trace('LM.writersDispatchDict')
            g.printDict(g.app.writersDispatchDict)
            g.trace('LM.atAutoWritersDict')
            g.printDict(g.app.atAutoWritersDict)
        # Creates problems: See #40.
    #@+node:ekr.20140728040812.17991: *7* LM.parse_writer_dict
    def parse_writer_dict(self, sfn, m):
        """
        Set entries in g.app.writersDispatchDict and g.app.atAutoWritersDict
        using entries in m.writers_dict.
        """
        writer_d = getattr(m, 'writer_dict', None)
        if writer_d:
            at_auto = writer_d.get('@auto', [])
            scanner_class = writer_d.get('class', None)
            extensions = writer_d.get('extensions', [])
            if at_auto:
                # Make entries for each @auto type.
                d = g.app.atAutoWritersDict
                for s in at_auto:
                    aClass = d.get(s)
                    if aClass and aClass != scanner_class:
                        g.trace(
                            f"{sfn}: duplicate {s} class {aClass.__name__} "
                            f"in {m.__file__}:")
                    else:
                        d[s] = scanner_class
                        g.app.atAutoNames.add(s)
            if extensions:
                # Make entries for each extension.
                d = g.app.writersDispatchDict
                for ext in extensions:
                    aClass = d.get(ext)
                    if aClass and aClass != scanner_class:
                        g.trace(f"{sfn}: duplicate {ext} class", aClass, scanner_class)
                    else:
                        d[ext] = scanner_class
        elif sfn not in ('basewriter.py',):
            g.warning(f"leo/plugins/writers/{sfn} has no writer_dict")
    #@+node:ekr.20120219154958.10478: *5* LM.createGui
    def createGui(self, pymacs):
        lm = self
        gui_option = lm.options.get('gui')
        windowFlag = lm.options.get('windowFlag')
        script = lm.options.get('script')
        if g.app.gui:
            if g.app.gui == g.app.nullGui:
                g.app.gui = None  # Enable g.app.createDefaultGui
                g.app.createDefaultGui(__file__)
            else:
                pass
                # This can happen when launching Leo from IPython.
                # This can also happen when leoID does not exist.
        elif gui_option is None:
            if script and not windowFlag:
                # Always use null gui for scripts.
                g.app.createNullGuiWithScript(script)
            else:
                g.app.createDefaultGui(__file__)
        else:
            lm.createSpecialGui(gui_option, pymacs, script, windowFlag)
    #@+node:ekr.20120219154958.10479: *5* LM.createSpecialGui
    def createSpecialGui(self, gui, pymacs, script, windowFlag):
        # lm = self
        if pymacs:
            g.app.createNullGuiWithScript(script=None)
        elif script:
            if windowFlag:
                g.app.createDefaultGui()
                g.app.gui.setScript(script=script)
                sys.argv = []  # 2021/06/24: corrected by mypy.
            else:
                g.app.createNullGuiWithScript(script=script)
        else:
            g.app.createDefaultGui()
    #@+node:ekr.20120219154958.10480: *5* LM.adjustSysPath
    def adjustSysPath(self):
        """
        Adjust sys.path to enable imports as usual with Leo.

        This method is no longer needed:
        """
        pass
    #@+node:ekr.20120219154958.10482: *5* LM.getDefaultFile
    def getDefaultFile(self):
        # Get the name of the workbook.
        fn = g.app.config.getString('default-leo-file')
        fn = g.os_path_finalize(fn)
        if not fn:
            return None
        if g.os_path_exists(fn):
            return fn
        if g.os_path_isabs(fn):
            # Create the file.
            g.error(f"Using default leo file name:\n{fn}")
            return fn
        # It's too risky to open a default file if it is relative.
        return None
    #@+node:ekr.20120219154958.10484: *5* LM.initApp
    def initApp(self, verbose):

        self.createAllImporterData()
            # Can be done early. Uses only g.app.loadDir & g.app.homeDir.
        assert g.app.loadManager
        from leo.core import leoBackground
        from leo.core import leoConfig
        from leo.core import leoNodes
        from leo.core import leoPlugins
        from leo.core import leoSessions
        # Import leoIPython only if requested.  The import is quite slow.
        self.setStdStreams()
        if g.app.useIpython:
            from leo.core import leoIPython
                # This launches the IPython Qt Console.  It *is* required.
            assert leoIPython  # suppress pyflakes/flake8 warning.
        # Make sure we call the new leoPlugins.init top-level function.
        leoPlugins.init()
        # Force the user to set g.app.leoID.
        g.app.setLeoID(verbose=verbose)
        # Create early classes *after* doing plugins.init()
        g.app.idleTimeManager = IdleTimeManager()
        g.app.backgroundProcessManager = leoBackground.BackgroundProcessManager()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController()
        g.app.recentFilesManager = RecentFilesManager()
        g.app.config = leoConfig.GlobalConfigManager()
        g.app.nodeIndices = leoNodes.NodeIndices(g.app.leoID)
        g.app.sessionManager = leoSessions.SessionManager()
        # Complete the plugins class last.
        g.app.pluginsController.finishCreate()
    #@+node:ekr.20120219154958.10486: *5* LM.scanOptions & helpers
    def scanOptions(self, fileName, pymacs):
        """Handle all options, remove them from sys.argv and set lm.options."""
        lm = self
        table = (
            '--dock',
            '--global-docks',  # #1643. use --use-docks instead.
            '--init-docks',
            '--no-cache',
            '--no-dock',  # #1171 and #1514: use --use-docks instead.
            '--session-restore',
            '--session-save',
            '--use-docks',
        )
        trace_m = '''abbrev,beauty,cache,coloring,drawing,events,focus,git,
          gnx,importers,ipython,keys,layouts,plugins,save,select,
          shutdown,size,speed,startup,themes,undo,verbose,zoom'''
        for bad_option in table:
            if bad_option in sys.argv:
                sys.argv.remove(bad_option)
                print(f"Ignoring the unused/deprecated {bad_option} option")
        lm.old_argv = sys.argv[:]
        parser = optparse.OptionParser(
            usage="usage: launchLeo.py [options] file1, file2, ...")
            # Automatically implements the --help option.
        #
        # Parse the options, and remove them from sys.argv.
        self.addOptionsToParser(parser, trace_m)
        options, args = parser.parse_args()
        sys.argv = [sys.argv[0]]
        sys.argv.extend(args)
        # Handle simple args...
        self.doSimpleOptions(options, trace_m)
        # Compute the lm.files ivar.
        lm.files = lm.computeFilesList(options, fileName)
        script = None if pymacs else self.doScriptOption(options, parser)
        d = {
            'gui': lm.doGuiOption(options),
            'load_type': lm.doLoadTypeOption(options),
            'screenshot_fn': lm.doScreenShotOption(options),
                # --screen-shot=fn
            'script': script,
            'select': options.select and options.select.strip('"'),
                # --select=headline
            'theme_path': options.theme,
                # --theme=name
            'version': options.version,
                # --version: print the version and exit.
            'windowFlag': script and options.script_window,
            'windowSize': lm.doWindowSizeOption(options),
            'windowSpot': lm.doWindowSpotOption(options),
        }
        return d
    #@+node:ekr.20180312150559.1: *6* LM.addOptionsToParser
    #@@nobeautify

    def addOptionsToParser(self, parser, trace_m):

        add = parser.add_option

        def add_bool(option, help, dest=None):
            add(option, action='store_true', dest=dest, help=help)

        def add_other(option, help, dest=None, m=None):
            add(option, dest=dest, help=help, metavar=m)

        add_bool('--diff',          'use Leo as an external git diff')
        add_bool('--fullscreen',    'start fullscreen')
        add_bool('--ipython',       'enable ipython support')
        add_bool('--fail-fast',     'stop unit tests after the first failure')
        add_other('--gui',          'gui to use (qt/console/null)')
        add_bool('--listen-to-log', 'start log_listener.py on startup')
        add_other('--load-type',    '@<file> type for non-outlines', m='TYPE')
        add_bool('--maximized',     'start maximized')
        add_bool('--minimized',     'start minimized')
        add_bool('--no-plugins',    'disable all plugins')
        add_bool('--no-splash',     'disable the splash screen')
        add_other('--screen-shot',  'take a screen shot and then exit', m='PATH')
        add_other('--script',       'execute a script and then exit', m="PATH")
        add_bool('--script-window', 'execute script using default gui')
        add_other('--select',       'headline or gnx of node to select', m='ID')
        add_bool('--silent',        'disable all log messages')
        add_other('--theme',        'use the named theme file', m='NAME')
        add_other('--trace',        'add one or more strings to g.app.debug', m=trace_m)
        add_other('--trace-binding', 'trace commands bound to a key', m='KEY')
        add_other('--trace-setting', 'trace where named setting is set', m="NAME")
        add_other('--window-size',  'initial window size (height x width)', m='SIZE')
        add_other('--window-spot',  'initial window position (top x left)', m='SPOT')
        # Multiple bool values.
        add('-v', '--version', action='store_true',
            help='print version number and exit')
    #@+node:ekr.20120219154958.10483: *6* LM.computeFilesList
    def computeFilesList(self, options, fileName):
        """Return the list of files on the command line."""
        lm = self
        files = []
        if fileName:
            files.append(fileName)
        for arg in sys.argv[1:]:
            if arg and not arg.startswith('-'):
                files.append(arg)
        result = []
        for z in files:
            # Fix #245: wrong: result.extend(glob.glob(lm.completeFileName(z)))
            aList = g.glob_glob(lm.completeFileName(z))
            if aList:
                result.extend(aList)
            else:
                result.append(z)
        return [g.os_path_normslashes(z) for z in result]
    #@+node:ekr.20180312150805.1: *6* LM.doGuiOption
    def doGuiOption(self, options):
        gui = options.gui
        if gui:
            gui = gui.lower()
            # #1171: retire non-tabbed qt gui.
            if gui in ('qt', 'qttabs'):
                gui = 'qt'  # For compatibilty with g.UiTypeException
            elif gui.startswith('browser'):
                pass
            elif gui in ('console', 'curses', 'text', 'null'):
                pass
            else:
                print(f"scanOptions: unknown gui: {gui}.  Using qt gui")
                gui = 'qt'
        else:
            gui = 'qt'
        assert gui
        assert gui != 'qttabs'  # For compatibilty with g.UiTypeException
        g.app.qt_use_tabs = gui == 'qt'
        g.app.guiArgName = gui
        return gui
    #@+node:ekr.20180312152329.1: *6* LM.doLoadTypeOption
    def doLoadTypeOption(self, options):

        s = options.load_type
        s = s.lower() if s else 'edit'
        return '@' + s
    #@+node:ekr.20180312152609.1: *6* LM.doScreenShotOption
    def doScreenShotOption(self, options):

        # --screen-shot=fn
        s = options.screen_shot
        if s:
            s = s.strip('"')
        return s
    #@+node:ekr.20180312153008.1: *6* LM.doScriptOption
    def doScriptOption(self, options, parser):

        # --script
        script = options.script
        if script:
            # #1090: use cwd, not g.app.loadDir, to find scripts.
            fn = g.os_path_finalize_join(os.getcwd(), script)
            script, e = g.readFileIntoString(fn, kind='script:', verbose=False)
            if not script:
                print(f"script not found: {fn}")
                sys.exit(1)
        else:
            script = None
        return script
    #@+node:ekr.20180312151544.1: *6* LM.doSimpleOptions
    def doSimpleOptions(self, options, trace_m):
        """These args just set g.app ivars."""
        # --fail-fast
        g.app.failFast = options.fail_fast
        # --fullscreen
        g.app.start_fullscreen = options.fullscreen
        # --git-diff
        g.app.diff = options.diff
        # --listen-to-log
        g.app.listen_to_log_flag = options.listen_to_log
        # --ipython
        g.app.useIpython = options.ipython
        # --maximized
        g.app.start_maximized = options.maximized
        # --minimized
        g.app.start_minimized = options.minimized
        # --no-plugins
        if options.no_plugins:
            g.app.enablePlugins = False
        # --no-splash: --minimized disables the splash screen
        g.app.use_splash_screen = not options.no_splash and not options.minimized
        # --silent
        g.app.silentMode = options.silent
        # --trace=...
        valid = trace_m.replace(' ', '').replace('\n', '').split(',')
        # g.trace('valid', valid)
        if options.trace:
            values = options.trace.lstrip('(').lstrip('[').rstrip(')').rstrip(']')
            for val in values.split(','):
                if val in valid:
                    g.app.debug.append(val)
                else:
                    g.es_print(f"unknown --trace value: {val}")
        #
        # These are not bool options.
        # --trace-binding
        g.app.trace_binding = options.trace_binding
            # g.app.config does not exist yet.
        #
        # --trace-setting=setting
        g.app.trace_setting = options.trace_setting
            # g.app.config does not exist yet.
    #@+node:ekr.20190923170528.1: *6* LM.doWindowSpotOption
    def doWindowSpotOption(self, options):

        # --window-spot
        spot = options.window_spot
        if spot:
            try:
                top, left = spot.split('x')
                spot = int(top), int(left)
            except ValueError:
                print('scanOptions: bad --window-spot:', spot)
                spot = None

        return spot
    #@+node:ekr.20180312154839.1: *6* LM.doWindowSizeOption
    def doWindowSizeOption(self, options):

        # --window-size
        windowSize = options.window_size
        if windowSize:
            try:
                h, w = windowSize.split('x')
                windowSize = int(h), int(w)
            except ValueError:
                windowSize = None
                print('scanOptions: bad --window-size:', windowSize)
        return windowSize
    #@+node:ekr.20160718072648.1: *5* LM.setStdStreams
    def setStdStreams(self):
        """
        Make sure that stdout and stderr exist.
        This is an issue when running Leo with pythonw.exe.
        """
        # Define class LeoStdOut
        #@+others
        #@+node:ekr.20160718091844.1: *6* class LeoStdOut
        class LeoStdOut:
            """A class to put stderr & stdout to Leo's log pane."""

            def __init__(self, kind):
                self.kind = kind
                g.es_print = self.write
                g.pr = self.write

            def flush(self, *args, **keys):
                pass
            #@+others
            #@+node:ekr.20160718102306.1: *7* LeoStdOut.write
            def write(self, *args, **keys):
                """Put all non-keyword args to the log pane, as in g.es."""
                #
                # Tracing will lead to unbounded recursion unless
                # sys.stderr has been redirected on the command line.
                app = g.app
                if not app or app.killed: return
                if app.gui and app.gui.consoleOnly: return
                log = app.log
                # Compute the effective args.
                d = {
                    'color': None,
                    'commas': False,
                    'newline': True,
                    'spaces': True,
                    'tabName': 'Log',
                }
                # Handle keywords for g.pr and g.es_print.
                d = g.doKeywordArgs(keys, d)
                color = d.get('color')
                if color == 'suppress':
                    return
                if log and color is None:
                    color = g.actualColor('black')
                color = g.actualColor(color)
                tabName = d.get('tabName') or 'Log'
                newline = d.get('newline')
                s = g.translateArgs(args, d)
                if app.batchMode:
                    if log:
                        log.put(s)
                elif log and app.logInited:
                    # from_redirect is the big difference between this and g.es.
                    log.put(s, color=color, tabName=tabName, from_redirect=True)
                else:
                    app.logWaiting.append((s, color, newline),)
            #@-others
        #@-others
        if not sys.stdout:
            sys.stdout = sys.__stdout__ = LeoStdOut('stdout')  # type:ignore
        if not sys.stderr:
            sys.stderr = sys.__stderr__ = LeoStdOut('stderr')  # type:ignore
    #@+node:ekr.20120219154958.10491: *4* LM.isValidPython
    def isValidPython(self):
        if sys.platform == 'cli':
            return True
        message = (
            f"Leo requires Python {g.minimum_python_version} or higher"
            f"You may download Python from http://python.org/download/")
        try:
            version = '.'.join([str(sys.version_info[i]) for i in (0, 1, 2)])
            ok = g.CheckVersion(version, g.minimum_python_version)
            if not ok:
                print(message)
                try:
                    # g.app.gui does not exist yet.
                    d = g.EmergencyDialog(
                        title='Python Version Error',
                        message=message)
                    d.run()
                except Exception:
                    g.es_exception()
            return ok
        except Exception:
            print("isValidPython: unexpected exception: g.CheckVersion")
            traceback.print_exc()
            return 0
    #@+node:ekr.20120223062418.10393: *4* LM.loadLocalFile & helper
    def loadLocalFile(self, fn, gui, old_c):
        """Completely read a file, creating the corresonding outline.

        1. If fn is an existing .leo, .db or .leojs file, read it twice:
        the first time with a NullGui to discover settings,
        the second time with the requested gui to create the outline.

        2. If fn is an external file:
        get settings from the leoSettings.leo and myLeoSetting.leo, then
        create a "wrapper" outline continain an @file node for the external file.

        3. If fn is empty:
        get settings from the leoSettings.leo and myLeoSetting.leo or default settings,
        or open an empty outline.
        """
        lm = self
        # Step 1: Return if the file is already open.
        fn = g.os_path_finalize(fn)
        if fn:
            c = lm.findOpenFile(fn)
            if c:
                return c
        #
        # Step 2: get the previous settings.
        # For .leo files (and zipped .leo files) this pre-reads the file in a null gui.
        # Otherwise, get settings from leoSettings.leo, myLeoSettings.leo, or default settings.
        previousSettings = lm.getPreviousSettings(fn)
        #
        # Step 3: open the outline in the requested gui.
        # For .leo files (and zipped .leo file) this opens the file a second time.
        c = lm.openFileByName(fn, gui, old_c, previousSettings)
        return c
    #@+node:ekr.20120223062418.10394: *5* LM.openFileByName & helpers
    def openFileByName(self, fn, gui, old_c, previousSettings):
        """Read the local file whose full path is fn using the given gui.
        fn may be a Leo file (including .leo or zipped file) or an external file.

        This is not a pre-read: the previousSettings always exist and
        the commander created here persists until the user closes the outline.

        Reads the entire outline if fn exists and is a .leo file or zipped file.
        Creates an empty outline if fn is a non-existent Leo file.
        Creates an wrapper outline if fn is an external file, existing or not.
        """
        lm = self
        # Disable the log.
        g.app.setLog(None)
        g.app.lockLog()
        # Create the a commander for the .leo file.
        # Important.  The settings don't matter for pre-reads!
        # For second read, the settings for the file are *exactly* previousSettings.
        c = g.app.newCommander(fileName=fn, gui=gui, previousSettings=previousSettings)
        # Open the file, if possible.
        g.doHook('open0')
        theFile = lm.openAnyLeoFile(fn)
        if isinstance(theFile, sqlite3.Connection):
            # this commander is associated with sqlite db
            c.sqlite_connection = theFile
        # Enable the log.
        g.app.unlockLog()
        c.frame.log.enable(True)
        # Phase 2: Create the outline.
        g.doHook("open1", old_c=None, c=c, new_c=c, fileName=fn)
        if theFile:
            readAtFileNodesFlag = bool(previousSettings)
            # The log is not set properly here.
            ok = lm.readOpenedLeoFile(c, fn, readAtFileNodesFlag, theFile)
                # Call c.fileCommands.openLeoFile to read the .leo file.
            if not ok: return None
        else:
            # Create a wrapper .leo file if:
            # a) fn is a .leo file that does not exist or
            # b) fn is an external file, existing or not.
            lm.initWrapperLeoFile(c, fn)
        g.doHook("open2", old_c=None, c=c, new_c=c, fileName=fn)
        # Phase 3: Complete the initialization.
        g.app.writeWaitingLog(c)
        c.setLog()
        lm.createMenu(c, fn)
        lm.finishOpen(c)
        return c
    #@+node:ekr.20120223062418.10405: *6* LM.createMenu
    def createMenu(self, c, fn=None):
        # lm = self
        # Create the menu as late as possible so it can use user commands.
        if not g.doHook("menu1", c=c, p=c.p, v=c.p):
            c.frame.menu.createMenuBar(c.frame)
            g.app.recentFilesManager.updateRecentFiles(fn)
            g.doHook("menu2", c=c, p=c.p, v=c.p)
            g.doHook("after-create-leo-frame", c=c)
            g.doHook("after-create-leo-frame2", c=c)
            # Fix bug 844953: tell Unity which menu to use.
                # c.enableMenuBar()
    #@+node:ekr.20120223062418.10406: *6* LM.findOpenFile
    def findOpenFile(self, fn):

        def munge(name):
            return g.os_path_normpath(name or '').lower()

        for frame in g.app.windowList:
            c = frame.c
            if g.os_path_realpath(munge(fn)) == g.os_path_realpath(munge(c.mFileName)):
                # Don't call frame.bringToFront(), it breaks --minimize
                c.setLog()
                # Selecting the new tab ensures focus is set.
                master = getattr(frame.top, 'leo_master', None)
                if master:  # master is a TabbedTopLevel.
                    master.select(frame.c)
                c.outerUpdate()
                return c
        return None
    #@+node:ekr.20120223062418.10407: *6* LM.finishOpen
    def finishOpen(self, c):
        # lm = self
        k = c.k
        assert k
        # New in Leo 4.6: provide an official way for very late initialization.
        c.frame.tree.initAfterLoad()
        c.initAfterLoad()
        # chapterController.finishCreate must be called after the first real redraw
        # because it requires a valid value for c.rootPosition().
        if c.chapterController: c.chapterController.finishCreate()
        if k: k.setDefaultInputState()
        c.initialFocusHelper()
        if k: k.showStateAndMode()
        c.frame.initCompleteHint()
        c.outerUpdate()
            # #181: Honor focus requests.
    #@+node:ekr.20120223062418.10408: *6* LM.initWrapperLeoFile
    def initWrapperLeoFile(self, c, fn):
        """
        Create an empty file if the external fn is empty.

        Otherwise, create an @edit or @file node for the external file.
        """
        # lm = self
        # Use the config params to set the size and location of the window.
        frame = c.frame
        frame.setInitialWindowGeometry()
        frame.deiconify()
        frame.lift()
        # #1570: Resize the _new_ frame.
        frame.splitVerticalFlag, r1, r2 = frame.initialRatios()
        frame.resizePanesToRatio(r1, r2)
        if not g.os_path_exists(fn):
            p = c.rootPosition()
            # Create an empty @edit node unless fn is an .leo file.
            # Fix #1070: Use "newHeadline", not fn.
            p.h = "newHeadline" if fn.endswith('.leo') else f"@edit {fn}"
            c.selectPosition(p)
        elif c.looksLikeDerivedFile(fn):
            # 2011/10/10: Create an @file node.
            p = c.importCommands.importDerivedFiles(parent=c.rootPosition(),
                paths=[fn], command=None)  # Not undoable.
            if p and p.hasBack():
                p.back().doDelete()
                p = c.rootPosition()
            if not p: return None
        else:
            # Create an @<file> node.
            p = c.rootPosition()
            if p:
                load_type = self.options['load_type']
                p.setHeadString(f"{load_type} {fn}")
                c.refreshFromDisk()
                c.selectPosition(p)

        # Fix critical bug 1184855: data loss with command line 'leo somefile.ext'
        # Fix smallish bug 1226816 Command line "leo xxx.leo" creates file xxx.leo.leo.
        c.mFileName = fn if fn.endswith('.leo') else f"{fn}.leo"
        c.wrappedFileName = fn
        c.frame.title = c.computeWindowTitle(c.mFileName)
        c.frame.setTitle(c.frame.title)
        # chapterController.finishCreate must be called after the first real redraw
        # because it requires a valid value for c.rootPosition().
        if c.config.getBool('use-chapters') and c.chapterController:
            c.chapterController.finishCreate()
        frame.c.clearChanged()
            # Mark the outline clean.
            # This makes it easy to open non-Leo files for quick study.
        return c
    #@+node:ekr.20120223062418.10419: *6* LM.isLeoFile & LM.isZippedFile
    def isLeoFile(self, fn):
        if not fn:
            return False
        return zipfile.is_zipfile(fn) or fn.endswith(('.leo', 'db', '.leojs'))

    def isZippedFile(self, fn):
        return fn and zipfile.is_zipfile(fn)
    #@+node:ekr.20120224161905.10030: *6* LM.openAnyLeoFile
    def openAnyLeoFile(self, fn):
        """Open a .leo, .leojs or .db file."""
        lm = self
        if fn.endswith('.db'):
            return sqlite3.connect(fn)
        if lm.isLeoFile(fn) and g.os_path_exists(fn):
            if lm.isZippedFile(fn):
                theFile = lm.openZipFile(fn)
            else:
                theFile = lm.openLeoFile(fn)
        else:
            theFile = None
        return theFile
    #@+node:ekr.20120223062418.10416: *6* LM.openLeoFile
    def openLeoFile(self, fn):
        # lm = self
        try:
            theFile = open(fn, 'rb')
            return theFile
        except IOError:
            # Do not use string + here: it will fail for non-ascii strings!
            if not g.unitTesting:
                g.error("can not open:", fn)
            return None
    #@+node:ekr.20120223062418.10410: *6* LM.openZipFile
    def openZipFile(self, fn):
        # lm = self
        try:
            theFile = zipfile.ZipFile(fn, 'r')
            if not theFile: return None
            # Read the file into an StringIO file.
            aList = theFile.namelist()
            name = aList and len(aList) == 1 and aList[0]
            if not name: return None
            s = theFile.read(name)
            s2 = g.toUnicode(s, 'utf-8')
            return StringIO(s2)
        except IOError:
            # Do not use string + here: it will fail for non-ascii strings!
            if not g.unitTesting:
                g.error("can not open:", fn)
            return None
    #@+node:ekr.20120223062418.10412: *6* LM.readOpenedLeoFile
    def readOpenedLeoFile(self, c, fn, readAtFileNodesFlag, theFile):
        # New in Leo 4.10: The open1 event does not allow an override of the init logic.
        assert theFile
        # lm = self
        ok = c.fileCommands.openLeoFile(theFile, fn,
            readAtFileNodesFlag=readAtFileNodesFlag)
                # closes file.
        if ok:
            if not c.openDirectory:
                theDir = g.os_path_finalize(g.os_path_dirname(fn))  # 1341
                c.openDirectory = c.frame.openDirectory = theDir
        else:
            g.app.closeLeoWindow(c.frame, finish_quit=False)
                # #970: Never close Leo here.
        return ok
    #@+node:ekr.20160430063406.1: *3* LM.revertCommander
    def revertCommander(self, c):
        """Revert c to the previously saved contents."""
        lm = self
        fn = c.mFileName
        # Re-read the file.
        theFile = lm.openAnyLeoFile(fn)
        if theFile:
            c.fileCommands.initIvars()
            c.fileCommands.getLeoFile(theFile, fn, checkOpenFiles=False)
                # Closes the file.
    #@-others
#@+node:ekr.20120223062418.10420: ** class PreviousSettings
class PreviousSettings:
    """
    A class holding the settings and shortcuts dictionaries
    that are computed in the first pass when loading local
    files and passed to the second pass.
    """

    def __init__(self, settingsDict, shortcutsDict):
        assert isinstance(settingsDict, g.TypedDict), repr(settingsDict)
        assert isinstance(shortcutsDict, g.TypedDict), repr(shortcutsDict)
            # was TypedDictOfLists.
        self.settingsDict = settingsDict
        self.shortcutsDict = shortcutsDict

    def __repr__(self):
        return (
            f"<PreviousSettings\n"
            f"{self.settingsDict}\n"
            f"{self.shortcutsDict}\n>")

    __str__ = __repr__
#@+node:ekr.20120225072226.10283: ** class RecentFilesManager
class RecentFilesManager:
    """A class to manipulate leoRecentFiles.txt."""

    def __init__(self):

        self.edit_headline = 'Recent files. Do not change this headline!'
            # Headline used by
        self.groupedMenus = []
            # Set in rf.createRecentFilesMenuItems.
        self.recentFiles = []
            # List of g.Bunches describing .leoRecentFiles.txt files.
        self.recentFilesMenuName = 'Recent Files'
            # May be changed later.
        self.recentFileMessageWritten = False
            # To suppress all but the first message.
        self.write_recent_files_as_needed = False
            # Will be set later.
    #@+others
    #@+node:ekr.20041201080436: *3* rf.appendToRecentFiles
    def appendToRecentFiles(self, files):
        rf = self
        files = [theFile.strip() for theFile in files]

        def munge(name):
            return g.os_path_normpath(name or '').lower()

        for name in files:
            # Remove all variants of name.
            for name2 in rf.recentFiles[:]:
                if munge(name) == munge(name2):
                    rf.recentFiles.remove(name2)
            rf.recentFiles.append(name)
    #@+node:ekr.20120225072226.10289: *3* rf.cleanRecentFiles
    def cleanRecentFiles(self, c):
        """
        Remove items from the recent files list that no longer exist.

        This almost never does anything because Leo's startup logic removes
        nonexistent files from the recent files list.
        """
        result = [z for z in self.recentFiles if g.os_path_exists(z)]
        if result != self.recentFiles:
            for path in result:
                self.updateRecentFiles(path)
            self.writeRecentFilesFile(c, force=True)
    #@+node:ekr.20180212141017.1: *3* rf.demangleRecentFiles
    def demangleRecentFiles(self, c, data):
        """Rewrite recent files based on c.config.getData('path-demangle')"""
        changes = []
        replace = None
        for line in data:
            text = line.strip()
            if text.startswith('REPLACE: '):
                replace = text.split(None, 1)[1].strip()
            if text.startswith('WITH:') and replace is not None:
                with_ = text[5:].strip()
                changes.append((replace, with_))
                g.es(f"{replace} -> {with_}")
        orig = [z for z in self.recentFiles if z.startswith("/")]
        self.recentFiles = []
        for i in orig:
            t = i
            for change in changes:
                t = t.replace(*change)
            self.updateRecentFiles(t)
        self.writeRecentFilesFile(c, force=True)
            # Force the write message.
    #@+node:ekr.20120225072226.10297: *3* rf.clearRecentFiles
    def clearRecentFiles(self, c):
        """Clear the recent files list, then add the present file."""
        rf = self; u = c.undoer; menu = c.frame.menu
        bunch = u.beforeClearRecentFiles()
        recentFilesMenu = menu.getMenu(self.recentFilesMenuName)
        menu.deleteRecentFilesMenuItems(recentFilesMenu)
        rf.recentFiles = [c.fileName()]
        for frame in g.app.windowList:
            rf.createRecentFilesMenuItems(frame.c)
        u.afterClearRecentFiles(bunch)
        # Write the file immediately.
        rf.writeRecentFilesFile(c, force=True)
            # Force the write message.
    #@+node:ekr.20120225072226.10301: *3* rf.createRecentFilesMenuItems
    def createRecentFilesMenuItems(self, c):
        rf = self
        menu = c.frame.menu
        recentFilesMenu = menu.getMenu(self.recentFilesMenuName)
        if not recentFilesMenu:
            return
        # Delete all previous entries.
        menu.deleteRecentFilesMenuItems(recentFilesMenu)
        # Create the permanent (static) menu entries.
        table = rf.getRecentFilesTable()
        menu.createMenuEntries(recentFilesMenu, table)
        # Create all the other entries (a maximum of 36).
        accel_ch = string.digits + string.ascii_uppercase  # Not a unicode problem.
        i = 0
        n = len(accel_ch)
        # see if we're grouping when files occur in more than one place
        rf_group = c.config.getBool("recent-files-group")
        rf_always = c.config.getBool("recent-files-group-always")
        groupedEntries = rf_group or rf_always
        if groupedEntries:  # if so, make dict of groups
            dirCount: Dict[str, Any] = {}
            for fileName in rf.getRecentFiles()[:n]:
                dirName, baseName = g.os_path_split(fileName)
                if baseName not in dirCount:
                    dirCount[baseName] = {'dirs': [], 'entry': None}
                dirCount[baseName]['dirs'].append(dirName)
        for name in rf.getRecentFiles()[:n]:
            # pylint: disable=cell-var-from-loop
            if name.strip() == "":
                continue  # happens with empty list/new file

            def recentFilesCallback(event=None, c=c, name=name):
                c.openRecentFile(fn=name)

            if groupedEntries:
                dirName, baseName = g.os_path_split(name)
                entry = dirCount[baseName]
                if len(entry['dirs']) > 1 or rf_always:  # sub menus
                    if entry['entry'] is None:
                        entry['entry'] = menu.createNewMenu(baseName, "Recent Files...")
                        # acts as a flag for the need to create the menu
                    c.add_command(menu.getMenu(baseName), label=dirName,
                        command=recentFilesCallback, underline=0)
                else:  # single occurence, no submenu
                    c.add_command(recentFilesMenu, label=baseName,
                        command=recentFilesCallback, underline=0)
            else:  # original behavior
                label = f"{accel_ch[i]} {g.computeWindowTitle(name)}"
                c.add_command(recentFilesMenu, label=label,
                    command=recentFilesCallback, underline=0)
            i += 1
        if groupedEntries:  # store so we can delete them later
            rf.groupedMenus = [z for z in dirCount
                if dirCount[z]['entry'] is not None]
    #@+node:vitalije.20170703115609.1: *3* rf.editRecentFiles
    def editRecentFiles(self, c):
        """
        Dump recentFiles into new node appended as lastTopLevel, selects it and
        request focus in body.

        NOTE: command write-edited-recent-files assume that headline of this
        node is not changed by user.
        """
        rf = self
        p1 = c.lastTopLevel().insertAfter()
        p1.h = self.edit_headline
        p1.b = '\n'.join(rf.recentFiles)
        c.redraw()
        c.selectPosition(p1)
        c.redraw()
        c.bodyWantsFocusNow()
        g.es('edit list and run write-rff to save recentFiles')
    #@+node:ekr.20120225072226.10286: *3* rf.getRecentFiles
    def getRecentFiles(self):
        # Fix #299: Leo loads a deleted file.
        self.recentFiles = [z for z in self.recentFiles
            if g.os_path_exists(z)]
        return self.recentFiles
    #@+node:ekr.20120225072226.10304: *3* rf.getRecentFilesTable
    def getRecentFilesTable(self):
        return (
            "*clear-recent-files",
            "*clean-recent-files",
            "*demangle-recent-files",
            "*sort-recent-files",
            ("-", None, None),
        )
    #@+node:ekr.20070224115832: *3* rf.readRecentFiles & helpers
    def readRecentFiles(self, localConfigFile):
        """Read all .leoRecentFiles.txt files."""
        # The order of files in this list affects the order of the recent files list.
        rf = self
        seen = []
        localConfigPath = g.os_path_dirname(localConfigFile)
        for path in (g.app.homeLeoDir, g.app.globalConfigDir, localConfigPath):
            if path:
                path = g.os_path_realpath(g.os_path_finalize(path))
            if path and path not in seen:
                ok = rf.readRecentFilesFile(path)
                if ok: seen.append(path)
        if not seen and rf.write_recent_files_as_needed:
            rf.createRecentFiles()
    #@+node:ekr.20061010121944: *4* rf.createRecentFiles
    def createRecentFiles(self):
        """
        Try to create .leoRecentFiles.txt, in the users home directory, or in
        Leo's config directory if that fails.
        """
        for theDir in (g.app.homeLeoDir, g.app.globalConfigDir):
            if theDir:
                fn = g.os_path_join(theDir, '.leoRecentFiles.txt')
                try:
                    with open(fn, 'w'):
                        g.red('created', fn)
                        return
                except IOError:
                    g.error('can not create', fn)
                    g.es_exception()
    #@+node:ekr.20050424115658: *4* rf.readRecentFilesFile
    def readRecentFilesFile(self, path):

        fileName = g.os_path_join(path, '.leoRecentFiles.txt')
        if not g.os_path_exists(fileName):
            return False
        try:
            with io.open(fileName, encoding='utf-8', mode='r') as f:
                try:  # Fix #471.
                    lines = f.readlines()
                except Exception:
                    lines = None
        except IOError:
            # The file exists, so FileNotFoundError is not possible.
            g.trace('can not open', fileName)
            return False
        if lines and self.sanitize(lines[0]) == 'readonly':
            lines = lines[1:]
        if lines:
            lines = [g.toUnicode(g.os_path_normpath(line)) for line in lines]
            self.appendToRecentFiles(lines)
        return True
    #@+node:ekr.20120225072226.10285: *3* rf.sanitize
    def sanitize(self, name):
        """Return a sanitized file name."""
        if name is None:
            return None
        name = name.lower()
        for ch in ('-', '_', ' ', '\n'):
            name = name.replace(ch, '')
        return name or None
    #@+node:ekr.20120215072959.12478: *3* rf.setRecentFiles
    def setRecentFiles(self, files):
        """Update the recent files list."""
        rf = self
        rf.appendToRecentFiles(files)
    #@+node:ekr.20120225072226.10293: *3* rf.sortRecentFiles
    def sortRecentFiles(self, c):
        """Sort the recent files list."""
        rf = self

        def key(path):
            # Sort only the base name.  That's what will appear in the menu.
            s = g.os_path_basename(path)
            return s.lower() if sys.platform.lower().startswith('win') else s

        aList = sorted(rf.recentFiles, key=key)
        rf.recentFiles = []
        for z in reversed(aList):
            rf.updateRecentFiles(z)
        rf.writeRecentFilesFile(c, force=True)
            # Force the write message.
    #@+node:ekr.20031218072017.2083: *3* rf.updateRecentFiles
    def updateRecentFiles(self, fileName):
        """Create the RecentFiles menu.  May be called with Null fileName."""
        rf = self
        if g.app.unitTesting: return

        def munge(name):
            return g.os_path_finalize(name or '').lower()

        def munge2(name):
            return g.os_path_finalize_join(g.app.loadDir, name or '')

        # Update the recent files list in all windows.

        if fileName:
            for frame in g.app.windowList:
                # Remove all versions of the file name.
                for name in rf.recentFiles:
                    if (
                        munge(fileName) == munge(name) or
                        munge2(fileName) == munge2(name)
                    ):
                        rf.recentFiles.remove(name)
                rf.recentFiles.insert(0, fileName)
                # Recreate the Recent Files menu.
                rf.createRecentFilesMenuItems(frame.c)
        else:
            for frame in g.app.windowList:
                rf.createRecentFilesMenuItems(frame.c)
    #@+node:vitalije.20170703115616.1: *3* rf.writeEditedRecentFiles
    def writeEditedRecentFiles(self, c):
        """
        Write content of "edit_headline" node as recentFiles and recreates
        menues.
        """
        rf = self; p = c.p
        p = g.findNodeAnywhere(c, self.edit_headline)
        if p:
            files = [z for z in p.b.splitlines() if z and g.os_path_exists(z)]
            rf.recentFiles = files
            rf.writeRecentFilesFile(c, force=False)
            rf.updateRecentFiles(None)
            c.selectPosition(p)
            c.deleteOutline()
        else:
            g.red('not found:', self.edit_headline)
    #@+node:ekr.20050424114937.2: *3* rf.writeRecentFilesFile & helper
    def writeRecentFilesFile(self, c, force=False):
        """
        Write the appropriate .leoRecentFiles.txt file.

        Write a message if force is True, or if it hasn't been written yet.
        """
        tag = '.leoRecentFiles.txt'
        rf = self
        # tag:#661. Do nothing if in leoBride.
        if g.app.unitTesting or g.app.inBridge:
            return
        localFileName = c.fileName()
        if localFileName:
            localPath, junk = g.os_path_split(localFileName)
        else:
            localPath = None
        written = False
        seen = []
        for path in (localPath, g.app.globalConfigDir, g.app.homeLeoDir):
            if path:
                fileName = g.os_path_join(path, tag)
                if g.os_path_exists(fileName) and fileName.lower() not in seen:
                    seen.append(fileName.lower())
                    ok = rf.writeRecentFilesFileHelper(fileName)
                    if force or not rf.recentFileMessageWritten:
                        if ok:
                            if not g.app.silentMode:
                                # Fix #459:
                                g.es_print(f"wrote recent file: {fileName}")
                            written = True
                        else:
                            g.error(f"failed to write recent file: {fileName}")
                    # Bug fix: Leo 4.4.6: write *all* recent files.
        if written:
            rf.recentFileMessageWritten = True
        else:
            # Attempt to create .leoRecentFiles.txt in the user's home directory.
            if g.app.homeLeoDir:
                fileName = g.os_path_finalize_join(g.app.homeLeoDir, tag)
                if not g.os_path_exists(fileName):
                    g.red(f"creating: {fileName}")
                rf.writeRecentFilesFileHelper(fileName)
    #@+node:ekr.20050424131051: *4* rf.writeRecentFilesFileHelper
    def writeRecentFilesFileHelper(self, fileName):
        # Don't update the file if it begins with read-only.
        #
        # Part 1: Return False if the first line is "readonly".
        #         It's ok if the file doesn't exist.
        if g.os_path_exists(fileName):
            with io.open(fileName, encoding='utf-8', mode='r') as f:
                try:
                    # Fix #471.
                    lines = f.readlines()
                except Exception:
                    lines = None
                if lines and self.sanitize(lines[0]) == 'readonly':
                    return False
        # Part 2: write the files.
        try:
            with io.open(fileName, encoding='utf-8', mode='w') as f:
                s = '\n'.join(self.recentFiles) if self.recentFiles else '\n'
                f.write(g.toUnicode(s))
                return True
        except IOError:
            g.error('error writing', fileName)
            g.es_exception()
        except Exception:
            g.error('unexpected exception writing', fileName)
            g.es_exception()
            if g.unitTesting: raise
        return False
    #@-others
#@+node:ekr.20150514125218.1: ** Top-level-commands
#@+node:ekr.20150514125218.2: *3* ctrl-click-at-cursor
@g.command('ctrl-click-at-cursor')
def ctrlClickAtCursor(event):
    """Simulate a control-click at the cursor."""
    c = event.get('c')
    if c:
        g.openUrlOnClick(event)
#@+node:ekr.20180213045148.1: *3* demangle-recent-files
@g.command('demangle-recent-files')
def demangle_recent_files_command(event):
    """
    Path demangling potentially alters the paths in the recent files list
    according to find/replace patterns in the @data path-demangle setting.
    For example:

        REPLACE: .gnome-desktop
        WITH: My Desktop

    The default setting specifies no patterns.
    """
    c = event and event.get('c')
    if c:
        data = c.config.getData('path-demangle')
        if data:
            g.app.recentFilesManager.demangleRecentFiles(c, data)
        else:
            g.es_print('No patterns in @data path-demangle')
#@+node:ekr.20150514125218.3: *3* enable/disable/toggle-idle-time-events
@g.command('disable-idle-time-events')
def disable_idle_time_events(event):
    """Disable default idle-time event handling."""
    g.app.idle_time_hooks_enabled = False

@g.command('enable-idle-time-events')
def enable_idle_time_events(event):
    """Enable default idle-time event handling."""
    g.app.idle_time_hooks_enabled = True

@g.command('toggle-idle-time-events')
def toggle_idle_time_events(event):
    """Toggle default idle-time event handling."""
    g.app.idle_time_hooks_enabled = not g.app.idle_time_hooks_enabled
#@+node:ekr.20150514125218.4: *3* join-leo-irc
@g.command('join-leo-irc')
def join_leo_irc(event=None):
    """Open the web page to Leo's irc channel on freenode.net."""
    import webbrowser
    webbrowser.open("http://webchat.freenode.net/?channels=%23leo&uio=d4")
#@+node:ekr.20150514125218.5: *3* open-url
@g.command('open-url')
def openUrl(event=None):
    """
    Open the url in the headline or body text of the selected node.

    Use the headline if it contains a valid url.
    Otherwise, look *only* at the first line of the body.
    """
    c = event.get('c')
    if c:
        g.openUrl(c.p)
#@+node:ekr.20150514125218.6: *3* open-url-under-cursor
@g.command('open-url-under-cursor')
def openUrlUnderCursor(event=None):
    """Open the url under the cursor."""
    return g.openUrlOnClick(event)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

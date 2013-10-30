# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2608: * @file leoApp.py
#@@first

#@@language python
#@@tabwidth -4
#@@pagewidth 60

#@+<< imports >>
#@+node:ekr.20120219194520.10463: ** << imports >> (leoApp)
import leo.core.leoGlobals as g

import os
import optparse
import string
import sys
import traceback
import zipfile

if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO
#@-<< imports >>

#@+others
#@+node:ekr.20120209051836.10241: ** class LeoApp
class LeoApp:

    """A class representing the Leo application itself.

    Ivars of this class are Leo's global variables."""

    #@+others
    #@+node:ekr.20031218072017.1416: *3* app.__init__
    def __init__(self):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('leoApp.__init__')

        # These ivars are Leo's global vars.
        # leoGlobals.py contains global switches to be set by hand.

        # Command-line arguments...
        self.batchMode = False          # True: run in batch mode.
        self.enablePlugins = True       # True: run start1 hook to load plugins. --no-plugins
        self.gui = None                 # The gui class.
        self.guiArgName = None          # The gui name given in --gui option.
        self.qt_use_tabs = False        # True: allow tabbed main window.
        self.restore_session = False    # True: restore session on startup.
        self.save_session = False       # True: save session on close.
        self.silentMode = False         # True: no signon.
        self.start_fullscreen = False   # For qtGui plugin.
        self.start_maximized = False    # For qtGui plugin.
        self.start_minimized = False    # For qtGui plugin.
        self.translateToUpperCase = False # Never set to True.
        self.useIpython = False         # True: add support for IPython.
        self.use_psyco = False          # True: use psyco optimization.
        self.use_splash_screen = True   # True: put up a splash screen.

        # Debugging & statistics...
        self.count = 0                  # General purpose debugging count.
        self.debug = False              # Enable debugging. (Can be slow.)
        self.debugSwitch = 0            # 0: Brief; 1: Full.
        self.disable_redraw = False     # True: disable all redraws.
        self.disableSave = False        # May be set by plugins.
        self.positions = 0              # The number of positions generated.
        self.scanErrors = 0             # The number of errors seen by g.scanError.
        self.statsDict = {}             # dict used by g.stat, g.clear_stats, g.print_stats.

        # Error messages...
        self.atPathInBodyWarning = None # Set by get_directives_dict.
        self.menuWarningsGiven = False  # True: supress warnings in menu code.
        self.unicodeErrorGiven = True   # True: suppres unicode tracebacks.

        # Global directories...
        self.extensionsDir = None   # The leo/extensions directory
        self.globalConfigDir = None # leo/config directory
        self.globalOpenDir = None   # The directory last used to open a file.
        self.homeDir = None         # The user's home directory.
        self.homeLeoDir = None      # The user's home/.leo directory.
        self.loadDir = None         # The leo/core directory.
        self.machineDir = None      # The machine-specific directory.

        # Global data...
        self.globalKillBuffer = []      # The global kill buffer.
        self.globalRegisters = {}       # The global register list.
        self.leoID = None               # The id part of gnx's.
        self.lossage = []               # List of last 100 keystrokes.
        self.numberOfUntitledWindows=0  # Number of opened untitled windows.
        self.windowList = []            # Global list of all frames.
        self.realMenuNameDict = {}      # Translations of menu names.

        # Global controller/manager objects...
        self.config = None              # The singleton leoConfig instance.
        self.db = None                  # The singleton leoCacher instance.
        self.loadManager = None         # The singleton LoadManager instance.
        # self.logManager = None        # The singleton LogManager instance.
        # self.openWithManager = None   # The singleton OpenWithManager instance.
        self.nodeIndices = None         # The singleton nodeIndices instance.
        self.pluginsController = None   # The singleton PluginsManager instance.
        self.sessionManager = None      # The singleton SessionManager instance.

        # Global status vars...

        if 1: #### To be moved to the Commands class...
            self.commandName = None         # The name of the command being executed.
            self.commandInterruptFlag=False # True: command within a command.

        # self.dragging = False           # True: dragging.
        self.inBridge = False           # True: running from leoBridge module.
        self.inScript = False           # True: executing a script.
        self.initing  = True            # True: we are initiing the app.
        self.killed   = False           # True: we are about to destroy the root window.
        self.preReadFlag = False        # True: we are pre-reading a settings file.
        self.quitting = False           # True: quitting.  Locks out some events.
        self.reverting = False          # True: executing the revert command.

        #### To be moved to the LogManager.

        # The global log...
        self.log = None                 # The LeoFrame containing the present log.
        self.logInited = False          # False: all log message go to logWaiting list.
        self.logIsLocked = False        # True: no changes to log are allowed.
        self.logWaiting = []            # List of messages waiting to go to a log.
        self.printWaiting = []          # Queue of messages to be sent to the printer.
        self.signon = ''
        self.signon2 = ''
        self.signon_printed = False

        # Global types.
        import leo.core.leoFrame as leoFrame
        import leo.core.leoGui as leoGui
        self.nullGui = leoGui.nullGui()
        self.nullLog = leoFrame.nullLog()

        #### To be moved to OpenWithManager.

        # Open with data...
        self.hasOpenWithMenu = False    # True: open with plugin has been loaded.
        self.openWithFiles = []         # List of data used by Open With command.
        self.openWithFileNum = 0        # Number of Open-With temp file names.
        self.openWithTable = None       # Passed to createOpenWithMenuFromTable.

        #### To be moved to to the pluginsController.

        # Plugins and event handlers...
        self.afterHandler = None
        self.hookError = False      # True: suppress further calls to hooks.
        self.hookFunction = None    # Application wide hook function.
        self.idle_imported = False  # True: we have done an import idle
        self.idleTimeDelay = 100    # Delay in msec between calls to "idle time" hook.
        self.idleTimeHook = False   # True: the global idleTimeHookHandler will reshedule itself.

        # Support for scripting...
        self.searchDict = {}          # For communication between find/change scripts.
        self.scriptDict = {}          # For use by scripts. Cleared before running each script.
        self.permanentScriptDict = {} # For use by scrips. Never cleared automatically.

        # Unit testing...
        self.isExternalUnitTest = False # True: we are running a unit test externally.
        self.runningAllUnitTests = False# True: we are running all unit tests (Only for local tests).
        self.unitTestDict = {}          # For communication between unit tests and code.
        self.unitTestGui = None         # A way to override the gui in external unit tests.
        self.unitTesting = False        # True if unit testing.
        self.unitTestMenusDict = {}
            # Created in leoMenu.createMenuEntries for a unit test.
            # keys are command names. values are sets of strokes.

        # Define all global data.        
        self.define_global_constants()
        self.define_language_delims_dict()
        self.define_language_extension_dict()
        self.define_extension_dict()
        self.global_commands_dict = {}

        self.ipk = None   # python kernel instance
    #@+node:ekr.20031218072017.1417: *4* app.define_global_constants
    def define_global_constants(self):

        # self.prolog_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

        self.prolog_prefix_string = "<?xml version=\"1.0\" encoding="
        self.prolog_postfix_string = "?>"
        self.prolog_namespace_string = \
            'xmlns:leo="http://edreamleo.org/namespaces/leo-python-editor/1.1"'
    #@+node:ekr.20120522160137.9909: *4* app.define_language_delims_dict
    def define_language_delims_dict(self):

        self.language_delims_dict = {
            # Internally, lower case is used for all language names.
            # Keys are languages, values are 1,2 or 3-tuples of delims.
            "actionscript"       : "// /* */", #jason 2003-07-03
            "ada"                : "--",
            "ada95"              : "--",
            "ahk"                : ";",
            "antlr"              : "// /* */",
            "apacheconf"         : "#",
            "apdl"               : "!",
            "applescript"        : "-- (* *)",
            "asp"                : "<!-- -->",
            "aspect_j"           : "// /* */",
            "assembly_macro32"   : ";",
            "assembly_mcs51"     : ";",
            "assembly_parrot"    : "#",
            "assembly_r2000"     : "#",
            "assembly_x86"       : ";",
            "autohotkey"         : "; /* */", #TL - AutoHotkey language
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
            "config"             : "#", # Leo 4.5.1
            "cplusplus"          : "// /* */",
            "cpp"                : "// /* */",# C++.
            "csharp"             : "// /* */", # C#
            "css"                : "/* */", # 4/1/04
            "cweb"               : "@q@ @>", # Use the "cweb hack"
            "cython"             : "#",
            "d"                  : "// /* */",
            "doxygen"            : "#",
            "eiffel"             : "--",
            "elisp"              : ";",
            "erlang"             : "%",
            "factor"             : "! ( )",
            "forth"              : "\\_ _(_ _)", # Use the "REM hack"
            "fortran"            : "C",
            "fortran90"          : "!",
            "foxpro"             : "&&",
            "gettext"            : "# ",
            "groovy"             : "// /* */",
            "haskell"            : "--_ {-_ _-}",
            "haxe"               : "// /* */",
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
            "jsp"                : "<%-- --%>",
            "kshell"             : "#", # Leo 4.5.1.
            "latex"              : "%",
            "lilypond"           : "% %{ %}",
            "lisp"               : ";", # EKR: 2010/09/29
            "lotos"              : "(* *)",
            "lua"                : "--", # ddm 13/02/06
            "mail"               : ">",
            "makefile"           : "#",
            "maple"              : "//",
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
            "vimoutline"         : "#", #TL 8/25/08 Vim's outline plugin
            "xml"                : "<!-- -->",
            "xsl"                : "<!-- -->",
            "xslt"               : "<!-- -->",
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
    #@+node:ekr.20120522160137.9910: *4* app.define_language_extension_dict
    def define_language_extension_dict (self):

        # Used only by c.getOpenWithExt.

        # Keys are languages, values are extensions.
        self.language_extension_dict = {
            "actionscript"  : "as", #jason 2003-07-03
            "ada"           : "ada",
            "ada95"         : "ada",
            "ahk"           : "ahk",
            "antlr"         : "g",
            "apacheconf"    : "conf",
            "apdl"          : "apdl",
            "applescript"   : "scpt",
            "asp"           : "asp",
            "aspect_j"      : "aj",
            "autohotkey"    : "ahk", #TL - AutoHotkey language
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
            "config"        : "cfg",
            "cplusplus"     : "c++",
            "cpp"           : "cpp",
            "css"           : "css", # 4/1/04
            "cweb"          : "w",
            "cython"        : "pyx", # Only one extension is valid at present: .pyi, .pyd.
            "d"             : "d",
            "eiffel"        : "e",
            "elisp"         : "el",
            "erlang"        : "erl",
            "factor"        : "factor",
            "forth"         : "forth",
            "fortran"       : "f",
            "fortran90"     : "f90",
            "foxpro"        : "prg",
            "gettext"       : "po",
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
            "jsp"           : "jsp",
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
            "sas"           : "sas",
            "scala"         : "scala",
            "scheme"        : "scm",
            "sgml"          : "sgml",
            "shell"         : "sh", # DS 4/1/04
            "shellscript"   : "sh",
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
            "vimoutline"    : "otl", #TL 8/25/08 Vim's outline plugin
            "xml"           : "xml",
            "xsl"           : "xsl",
            "xslt"          : "xsl",
            "zpt"           : "zpt",
        }

        # These aren't real languages, or have no delims...
            # cvs_commit, dsssl, embperl, freemarker, hex, jcl,
            # patch, phpsection, progress, props, pseudoplain,
            # relax_ng_compact, rtf, svn_commit.

        # These have extensions which conflict with other languages.
            # assembly_macro32: .asm or .a
            # assembly_mcs51:   .asm or .a
            # assembly_parrot:  .asm or .a
            # assembly_r2000:   .asm or .a
            # assembly_x86:     .asm or .a
            # squidconf:        .conf
            # rpmspec:          .rpm
    #@+node:ekr.20120522160137.9911: *4* app.define_extension_dict
    def define_extension_dict(self):

        # Keys are extensions, values are languages
        self.extension_dict = {
            # "ada":    "ada",
            "ada":      "ada95", # modes/ada95.py exists.
            "ahk":      "autohotkey",
            "aj":       "aspect_j",
            "apdl":     "apdl",
            "as":       "actionscript", #jason 2003-07-03
            "asp":      "asp",
            "awk":      "awk",
            "b":        "b",
            "bas":      "rapidq", # fil 2004-march-11
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
            "ch":       "chill", # Other extensions, .c186,.c286
            "conf":     "apacheconf",
            "cpp":      "cpp",
            "css":      "css",
            "d":        "d",
            "e":        "eiffel",
            "el":       "elisp",
            "eml":      "mail",
            "erl":      "erlang",
            "f":        "fortran",
            "f90":      "fortran90",
            "factor":   "factor",
            "forth":    "forth",
            "g":        "antlr",
            "groovy":   "groovy",
            "h":        "c", # 2012/05/23.
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
            "iss":      "inno_setup",
            "java":     "java",
            "jhtml":    "jhtml",
            "jmk":      "jmk",
            "js":       "javascript", # For javascript import test.
            "jsp":      "javaserverpage",
            # "jsp":      "jsp",
            "ksh":      "kshell", # Leo 4.5.1.
            "lua":      "lua", # ddm 13/02/06
            "ly":       "lilypond",
            "m":        "matlab", # EKR: 2011/10/21
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
            "otl":      "vimoutline", #TL 8/25/08 Vim's outline plugin
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
            "sas":      "sas",
            "scala":    "scala",
            "scm":      "scheme",
            "scpt":     "applescript",
            "sgml":     "sgml",
            "sh":       "shell", # DS 4/1/04. modes/shell.py exists.
            # "sh":     "shellscript",
            "shtml":    "shtml",
            "sm":       "smalltalk",
            "splus":    "splus",
            "sql":      "plsql", # qt02537 2005-05-27
            "sqr":      "sqr",
            "ss":       "ssharp",
            "ssi":      "shtml",
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
            "zpt":      "zpt",
        }

        # These aren't real languages, or have no delims...
            # cvs_commit, dsssl, embperl, freemarker, hex, jcl,
            # patch, phpsection, progress, props, pseudoplain,
            # relax_ng_compact, rtf, svn_commit.

        # These have extensions which conflict with other languages.
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

    #@+node:ekr.20031218072017.2609: *3* app.closeLeoWindow
    def closeLeoWindow (self,frame,new_c=None):

        """Attempt to close a Leo window.

        Return False if the user veto's the close."""

        trace = False and not g.unitTesting
        c = frame.c

        if trace: g.trace(frame.c,g.callers())

        c.endEditing() # Commit any open edits.

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

        g.app.setLog(None) # no log until we reactive a window.

        g.doHook("close-frame",c=c)
            # This may remove frame from the window list.

        if frame in g.app.windowList:
            g.app.destroyWindow(frame)

        if g.app.windowList:
            c2 = new_c or g.app.windowList[0].c
            g.app.selectLeoWindow(c2)

        elif not g.app.unitTesting:
            g.app.finishQuit()

        return True # The window has been closed.
    #@+node:ville.20090602181814.6219: *3* app.commanders
    def commanders(self):
        """ Return list of currently active controllers """

        return [f.c for f in g.app.windowList]    
    #@+node:ekr.20090717112235.6007: *3* app.computeSignon
    def computeSignon (self):

        app = self

        import leo.core.leoVersion as leoVersion
        build,date  = leoVersion.build,leoVersion.date
        guiVersion  = app.gui and app.gui.getFullVersion() or 'no gui!'
        leoVer      = leoVersion.version
        n1,n2,n3,junk,junk=sys.version_info

        if sys.platform.startswith('win'):
            sysVersion = 'Windows '
            try:
                v = os.sys.getwindowsversion()
                sysVersion += ', '.join([str(z) for z in v])
            except Exception:
                pass

        else: sysVersion = sys.platform

        app.signon = 'Leo %s, build %s, %s' % (
            leoVer,build,date)
        app.signon2 = 'Python %s.%s.%s, %s\n%s' % (
            n1,n2,n3,guiVersion,sysVersion)
    #@+node:ekr.20100831090251.5838: *3* app.createXGui
    #@+node:ekr.20100831090251.5840: *4* app.createCursesGui
    def createCursesGui (self,fileName='',verbose=False):

        app = self

        app.pluginsController.loadOnePlugin('leo.plugins.cursesGui',verbose=verbose)
    #@+node:ekr.20090619065122.8593: *4* app.createDefaultGui
    def createDefaultGui (self,fileName='',verbose=False):

        """A convenience routines for plugins to create the default gui class."""

        app = self ; argName = app.guiArgName

        # This method can be called twice if we had to get .leoID.txt.
        if app.gui: return

        if argName in ('qt','qttabs'): # 2011/06/15.
            app.createQtGui(fileName,verbose=verbose)
        elif argName == 'null':
            g.app.gui = g.app.nullGui
        elif argName == 'curses':
            app.createCursesGui()

        if not app.gui:
            print('Leo requires Qt to be installed.')
    #@+node:ekr.20031218072017.1938: *4* app.createNullGuiWithScript
    def createNullGuiWithScript (self,script=None):

        app = self

        app.batchMode = True
        app.gui = g.app.nullGui
        app.gui.setScript(script)
    #@+node:ekr.20090202191501.1: *4* app.createQtGui
    def createQtGui (self,fileName='',verbose=False):

        # Do NOT omit fileName param: it is used in plugin code.

        """A convenience routines for plugins to create the Qt gui class."""

        app = self
        try:
            # Take care to try the same imports as in qtGui.py.
            import PyQt4.QtCore
            import PyQt4.QtGui            
            import leo.plugins.qtGui as qtGui
            if 0: g.trace(PyQt4) # To remove a pyflakes warning.
        except ImportError:
            qtGui = None

        if qtGui:
            qtGui.init()
            if app.gui and fileName and verbose:
                print('qtGui created in %s' % fileName)
    #@+node:ekr.20090126063121.3: *4* app.createWxGui
    def createWxGui (self,fileName='',verbose=False):

        # Do NOT omit fileName param: it is used in plugin code.

        """A convenience routines for plugins to create the wx gui class."""

        app = self

        app.pluginsController.loadOnePlugin ('leo.plugins.wxGui',verbose=verbose)

        if fileName and verbose:

            print('wxGui created in %s' % fileName)
    #@+node:ekr.20031218072017.2612: *3* app.destroyAllOpenWithFiles
    def destroyAllOpenWithFiles (self):

        """Try to remove temp files created with the Open With command.

        This may fail if the files are still open.

        Called by g.app.finishQuit"""

        # We can't use g.es here because the log stream no longer exists.

        for theDict in self.openWithFiles[:]:
            g.app.destroyOpenWithFileWithDict(theDict)

        # Delete the list so the gc can recycle Leo windows!
        g.app.openWithFiles = []
    #@+node:ekr.20031218072017.2613: *3* app.destroyOpenWithFilesForFrame
    def destroyOpenWithFilesForFrame (self,frame):

        """Close all "Open With" files associated with frame

        Called by app.destroyWindow.
        """

        # Make a copy of the list: it may change in the loop.
        openWithFiles = g.app.openWithFiles

        for theDict in openWithFiles[:]: # 6/30/03
            c = theDict.get("c")
            if c.frame == frame:
                g.app.destroyOpenWithFileWithDict(theDict)
    #@+node:ekr.20031218072017.2614: *3* app.destroyOpenWithFileWithDict
    def destroyOpenWithFileWithDict (self,theDict):

        '''
        A helper for app.destroyAllOpenWithFiles and
        app.destroyOpenWithFilesForFrame.
        '''

        path = theDict.get("path")
        if path and g.os_path_exists(path):
            try:
                os.remove(path)
                g.pr("deleting temp file: %s" % g.shortFileName(path))
            except:
                g.pr("can not delete temp file: %s" % path)

        # Remove theDict from the list so the gc can recycle the Leo window!
        g.app.openWithFiles.remove(theDict)
    #@+node:ekr.20031218072017.2615: *3* app.destroyWindow
    def destroyWindow (self,frame):

        # g.trace(frame in g.app.windowList,frame)
        g.app.destroyOpenWithFilesForFrame(frame)

        if frame in g.app.windowList:
            # g.trace(g.app.windowList)
            g.app.windowList.remove(frame)
            g.app.forgetOpenFile(frame.c.fileName())

        # force the window to go away now.
        # Important: this also destroys all the objects of the commander.
        frame.destroySelf()
    #@+node:ekr.20031218072017.1732: *3* app.finishQuit
    def finishQuit(self):

        # forceShutdown may already have fired the "end1" hook.
        if not g.app.killed:
            g.doHook("end1")
        if g.app.ipk:
            g.app.ipk.cleanup_consoles()
        self.destroyAllOpenWithFiles()
        if g.app.gui:
            g.app.gui.destroySelf()
        # Don't use g.trace!
        # print('app.finishQuit: setting g.app.killed',g.callers())
        g.app.killed = True
            # Disable all further hooks and events.
            # Alas, "idle" events can still be called
            # even after the following code.
        if g.app.afterHandler:
            g.app.afterHandler = None
    #@+node:ekr.20031218072017.2616: *3* app.forceShutdown
    def forceShutdown (self):

        """Forces an immediate shutdown of Leo at any time.

        In particular, may be called from plugins during startup."""

        # Wait until everything is quiet before really quitting.
        g.doHook("end1")

        self.log = None # Disable writeWaitingLog
        self.killed = True # Disable all further hooks.

        for w in self.windowList[:]:
            self.destroyWindow(w)

        self.finishQuit()
    #@+node:ekr.20031218072017.2188: *3* app.newCommander
    def newCommander(self,fileName,relativeFileName=None,gui=None,previousSettings=None):

        """Create a commander and its view frame for the Leo main window."""

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('g.app.newCommander: %s %s' % (repr(fileName),repr(relativeFileName)))

        # Create the commander and its subcommanders.
        # This takes about 3/4 sec when called by the leoBridge module.
        import leo.core.leoCommands as leoCommands

        return leoCommands.Commands(fileName,relativeFileName,gui,previousSettings)
    #@+node:ekr.20031218072017.2617: *3* app.onQuit
    def onQuit (self,event=None):

        '''Exit Leo, prompting to save unsaved outlines first.'''

        g.app.quitting = True

        # Don't use g.trace here.
        # print('onQuit',g.app.save_session,g.app.sessionManager)

        if g.app.save_session and g.app.sessionManager:
            g.app.sessionManager.save_snapshot()

        while g.app.windowList:
            w = g.app.windowList[0]
            if not g.app.closeLeoWindow(w):
                break

        if g.app.windowList:
            g.app.quitting = False # If we get here the quit has been disabled.
    #@+node:ekr.20120304065838.15588: *3* app.selectLeoWindow
    def selectLeoWindow (self,c):

        trace = False and not g.unitTesting
        assert c
        if trace: g.trace(c.frame.title)
        frame = c.frame
        frame.deiconify()
        frame.lift()
        c.setLog()
        master = hasattr(frame.top,'leo_master') and frame.top.leo_master
        if master: # 2011/11/21: selecting the new tab ensures focus is set.
            # frame.top.leo_master is a TabbedTopLevel.
            master.select(c)
        c.bodyWantsFocus()
        c.outerUpdate()
    #@+node:ville.20090620122043.6275: *3* app.setGlobalDb
    def setGlobalDb(self):
        """ Create global pickleshare db

        Usable by::

            g.app.db['hello'] = [1,2,5]

        """

        # Fixes bug 670108.
        import leo.core.leoCache as leoCache
        g.app.db = leoCache.cacher().initGlobalDB()
    #@+node:ekr.20031218072017.1978: *3* app.setLeoID
    def setLeoID (self,verbose=True):

        tag = ".leoID.txt"
        homeLeoDir = g.app.homeLeoDir
        globalConfigDir = g.app.globalConfigDir
        loadDir = g.app.loadDir

        verbose = not g.app.unitTesting
        #@+<< return if we can set leoID from sys.leoID >>
        #@+node:ekr.20031218072017.1979: *4* << return if we can set leoID from sys.leoID>>
        # This would be set by in Python's sitecustomize.py file.

        # Use hasattr & getattr to suppress pylint warning.
        # Use a "non-constant" attribute to suppress another warning!

        nonConstantAttr = "leoID"

        if hasattr(sys,nonConstantAttr):
            g.app.leoID = getattr(sys,nonConstantAttr)
            if verbose and not g.app.silentMode and not g.app.unitTesting:
                g.red("leoID=",g.app.leoID,spaces=False)
            # Careful: periods in the id field of a gnx will corrupt the .leo file!
            g.app.leoID = g.app.leoID.replace('.','-')
            return
        else:
            g.app.leoID = None
        #@-<< return if we can set leoID from sys.leoID >>
        #@+<< return if we can set leoID from "leoID.txt" >>
        #@+node:ekr.20031218072017.1980: *4* << return if we can set leoID from "leoID.txt" >>
        for theDir in (homeLeoDir,globalConfigDir,loadDir):
            # N.B. We would use the _working_ directory if theDir is None!
            if theDir:
                try:
                    fn = g.os_path_join(theDir,tag)
                    f = open(fn,'r')
                    s = f.readline()
                    f.close()
                    if s and len(s) > 0:
                        g.app.leoID = s.strip()
                        # Careful: periods in the id field of a gnx
                        # will corrupt the .leo file!
                        g.app.leoID = g.app.leoID.replace('.','-')
                        if verbose and not g.app.silentMode and not g.app.unitTesting:
                            g.red('leoID=',g.app.leoID,' (in ',theDir,')',spaces=False)
                        return
                    elif verbose and not g.app.unitTesting:
                        g.red('empty ',tag,' (in ',theDir,')',spaces=False)
                except IOError:
                    g.app.leoID = None
                except Exception:
                    g.app.leoID = None
                    g.error('unexpected exception in app.setLeoID')
                    g.es_exception()
        #@-<< return if we can set leoID from "leoID.txt" >>
        #@+<< return if we can set leoID from os.getenv('USER') >>
        #@+node:ekr.20060211140947.1: *4* << return if we can set leoID from os.getenv('USER') >>
        try:
            theId = os.getenv('USER')
            if theId:
                if verbose and not g.app.unitTesting:
                    g.blue("setting leoID from os.getenv('USER'):",
                        repr(theId))
                g.app.leoID = theId
                # Careful: periods in the id field of a gnx
                # will corrupt the .leo file!
                g.app.leoID = g.app.leoID.replace('.','-')
                return

        except Exception:
            pass
        #@-<< return if we can set leoID from os.getenv('USER') >>
        #@+<< put up a dialog requiring a valid id >>
        #@+node:ekr.20031218072017.1981: *4* << put up a dialog requiring a valid id >>
        # 2011/06/13: Don't put up a splash screen.
        # It would obscure the coming dialog.
        g.app.use_splash_screen = False

        # New in 4.1: get an id for gnx's.  Plugins may set g.app.leoID.
        if g.app.gui is None:
            # Create the Qt gui if it exists.
            g.app.createDefaultGui(fileName='g.app.setLeoId',verbose=True)

        if g.app.gui is None: # Neither gui could be created: this should never happen.
            print("Please enter LeoID (e.g. your username, 'johndoe'...)")
            if g.isPython3: # 2010/02/04.
                leoid = input('LeoID: ')
            else:
                leoid = raw_input('LeoID: ')
        else:
            leoid = g.app.gui.runAskLeoIDDialog()

        # Bug fix: 2/6/05: put result in g.app.leoID.
        g.app.leoID = leoid

        # Careful: periods in the id field of a gnx will corrupt the .leo file!
        g.app.leoID = g.app.leoID.replace('.','-')

        # g.trace(g.app.leoID)
        g.blue('leoID=',repr(g.app.leoID),spaces=False)
        #@-<< put up a dialog requiring a valid id >>
        #@+<< attempt to create leoID.txt >>
        #@+node:ekr.20031218072017.1982: *4* << attempt to create leoID.txt >> (changed)
        for theDir in (homeLeoDir,globalConfigDir,loadDir):
            # N.B. We would use the _working_ directory if theDir is None!
            if theDir:
                try:
                    fn = g.os_path_join(theDir,tag)
                    f = open(fn,'w')
                    s = g.app.leoID
                    if not g.isPython3: # 2010/08/27
                        s = g.toEncodedString(s,encoding='utf-8',reportErrors=True)
                    f.write(s)
                    f.close()
                    if g.os_path_exists(fn):
                        g.error('',tag,'created in',theDir)
                        return
                except IOError:
                    pass

                g.error('can not create',tag,'in',theDir)
        #@-<< attempt to create leoID.txt >>
    #@+node:ekr.20031218072017.1847: *3* app.setLog, lockLog, unlocklog
    def setLog (self,log):

        """set the frame to which log messages will go"""

        # print("app.setLog:",log)
        if not self.logIsLocked:
            self.log = log

    def lockLog(self):
        """Disable changes to the log"""
        self.logIsLocked = True

    def unlockLog(self):
        """Enable changes to the log"""
        self.logIsLocked = False
    #@+node:ekr.20031218072017.2619: *3* app.writeWaitingLog
    def writeWaitingLog (self,c):

        trace = False
        app = self

        if trace:
            # Do not call g.es, g.es_print, g.pr or g.trace here!
            print('** writeWaitingLog','silent',app.silentMode,c.shortFileName())
            # print('writeWaitingLog',g.callers())
            # import sys ; print('writeWaitingLog: argv',sys.argv)

        if not c or not c.exists:
            return

        if g.unitTesting:
            app.printWaiting = []
            app.logWaiting = []
            g.app.setLog(None) # Prepare to requeue for other commanders.
            return

        table = [
            ('Leo Log Window','red'),
            (app.signon,None),
            (app.signon2,None),
        ]
        table.reverse()

        c.setLog() # 2010/10/20
        app.logInited = True # Prevent recursive call.

        if not app.signon_printed:
            app.signon_printed = True
            if not app.silentMode: # 2011/11/02:
                print('')
                print('** isPython3: %s' % g.isPython3)
                if not g.enableDB:
                    print('** caching disabled')
                print(app.signon)
                print(app.signon2)
        if not app.silentMode: # 2011/11/02:
            for s in app.printWaiting:
                print(s)
        app.printWaiting = []

        if not app.silentMode:  # 2011/11/02:
            for s,color in table:
                app.logWaiting.insert(0,(s+'\n',color),)
            for s,color in app.logWaiting:
                g.es('',s,color=color,newline=0)
                    # The caller must write the newlines.
        app.logWaiting = []

        # Essential when opening multiple files...
        g.app.setLog(None) 
    #@+node:ekr.20120427064024.10068: *3* app.Detecting already-open files
    #@+node:ekr.20120427064024.10064: *4* app.checkForOpenFile
    def checkForOpenFile (self,c,fn):

        d,tag = g.app.db,'open-leo-files'

        if d is None or g.app.unitTesting or g.app.batchMode or g.app.reverting:
            return True
        else:
            aList = d.get(tag) or []
            if fn in aList:
                result = g.app.gui.runAskYesNoDialog(c,
                    title='Open Leo File Again?',
                    message='%s is already open.  Open it again?' % (fn),
                )
                if result == 'yes':
                    clear = g.app.gui.runAskYesNoDialog(c,
                        title='Reset open count?',
                        message='Reset open count for %s?' \
                            "\nSay yes if you know this outline" \
                            "\nis not really open elsewhere"% (fn),
                    )
                    if clear == 'yes':
                        d[tag] = [i for i in d[tag] if i != fn]
                        # IMPORTANT - rest of load process will add another
                        # entry for this Leo instance, don't do it here
                return result == 'yes'
            else:
                return True
    #@+node:ekr.20120427064024.10066: *4* app.forgetOpenFile
    def forgetOpenFile (self,fn):

        trace = False and not g.unitTesting
        d,tag = g.app.db,'open-leo-files'

        if d is None or g.app.unitTesting or g.app.batchMode or g.app.reverting:
            pass
        else:
            aList = d.get(tag) or []
            if fn in aList:
                aList.remove(fn)
                if trace:
                    g.trace('removed: %s' % (fn),g.callers())
                    for z in aList:
                        print('  %s' % (z))
                d[tag] = aList
            else:
                if trace: g.trace('did not remove: %s' % (fn))
    #@+node:ekr.20120427064024.10065: *4* app.rememberOpenFile
    def rememberOpenFile(self,fn):

        trace = False and not g.unitTesting
        d,tag = g.app.db,'open-leo-files'

        if d is None or g.app.unitTesting or g.app.batchMode or g.app.reverting:
            pass
        elif g.app.preReadFlag:
            pass
        else:
            aList = d.get(tag) or []
            # It's proper to add duplicates to this list.
            aList.append(fn)
            if trace:
                # Trace doesn't work well while initing.
                print('rememberOpenFile:added: %s' % (fn))
                for z in aList:
                    print('  %s' % (z))
            d[tag] = aList
    #@-others
#@+node:ekr.20120209051836.10242: ** class LoadManager
class LoadManager:

    '''A class to manage loading .leo files, including configuration files.'''

    #@+others
    #@+node:ekr.20120214060149.15851: *3*  LM.ctor
    def __init__ (self):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('LoadManager.__init__')

        # Global settings & shortcuts dicts.
        # The are the defaults for computing settings and shortcuts for all loaded files.
        self.globalSettingsDict = None
            # A g.TypedDict containing the merger of default settings,
            # settings in leoSettings.leo and settings in myLeoSettings.leo
        self.globalShortcutsDict = None
            # A g.TypedDictOfLists containg the merger of shortcuts in
            # leoSettings.leo and settings in myLeoSettings.leo.

        # LoadManager ivars corresponding to user options....
        self.files = []
            # List of files to be loaded.
        self.options = {}
            # Dictionary of user options. Keys are option names.

        if 0: # use lm.options.get instead.
            self.script = None          # The fileName of a script, or None.
            self.script_name = None
            self.script_path = None
            self.script_path_w = None
            self.screenshot_fn = None
            self.selectHeadline = None
            self.versionFlag = False
            self.windowFlag = False
            self.windowSize = None

        # Ivars of *other* classes corresponding to command-line arguments...
            # g.app.batchMode           Set in createNullGuiWithScript
            # g.app.gui = None          The gui class.
            # g.app.guiArgName          The gui name given in --gui option.
            # g.app.qt_use_tabs                
            # g.app.silentMode         
            # g.app.start_fullscreen   
            # g.app.start_maximized    .
            # g.app.start_minimized
            # g.app.useIpython
            # g.app.use_splash_screen
            # g.enableDB                --no-cache
    #@+node:ekr.20120211121736.10812: *3* LM.Directory & file utils
    #@+node:ekr.20120219154958.10481: *4* LM.completeFileName
    def completeFileName (self,fileName):

        fileName = g.toUnicode(fileName)
        fileName = g.os_path_finalize(fileName)

        # 2011/10/12: don't add .leo to *any* file.
        return fileName
    #@+node:ekr.20120209051836.10372: *4* LM.computeLeoSettingsPath
    def computeLeoSettingsPath (self):

        '''Return the full path to leoSettings.leo.'''

        trace = False
        # lm = self
        join = g.os_path_finalize_join
        settings_fn = 'leoSettings.leo'
        table = (
            # First, leoSettings.leo in the home directories.
            join(g.app.homeDir,     settings_fn),
            join(g.app.homeLeoDir,  settings_fn),
            # Last, leoSettings.leo in leo/config directory.
            join(g.app.globalConfigDir, settings_fn)
        )
        for path in table:
            if trace: print('computeLeoSettingsPath',g.os_path_exists(path),repr(path))
            if g.os_path_exists(path):
                break
        else:
            path = None
        return path
    #@+node:ekr.20120209051836.10373: *4* LM.computeMyLeoSettingsPath
    def computeMyLeoSettingsPath (self):

        '''Return the full path to myLeoSettings.leo.

        The "footnote": Get the local directory from lm.files[0]'''

        trace = False
        lm = self
        join = g.os_path_finalize_join
        settings_fn = 'myLeoSettings.leo'

        # This seems pointless: we need a machine *directory*.
        # For now, however, we'll keep the existing code as is.
        machine_fn = lm.computeMachineName() + settings_fn

        # First, compute the directory of the first loaded file.
        # All entries in lm.files are full, absolute paths.
        localDir = g.os_path_dirname(lm.files[0]) if lm.files else None

        table = (
            # First, myLeoSettings.leo in the local directory
            join(localDir,          settings_fn),

            # Next, myLeoSettings.leo in the home directories.
            join(g.app.homeDir,     settings_fn),
            join(g.app.homeLeoDir,  settings_fn),

            # Next, <machine-name>myLeoSettings.leo in the home directories.
            join(g.app.homeDir,     machine_fn),
            join(g.app.homeLeoDir,  machine_fn),

            # Last, leoSettings.leo in leo/config directory.
            join(g.app.globalConfigDir, settings_fn),
        )

        for path in table:
            if trace: print('computeMyLeoSettingsPath',g.os_path_exists(path),repr(path))
            if g.os_path_exists(path):
                break
        else:
            path = None

        return path
    #@+node:ekr.20120209051836.10252: *4* LM.computeStandardDirectories & helpers
    def computeStandardDirectories(self):

        '''Compute the locations of standard directories and
        set the corresponding ivars.'''

        lm = self

        g.app.loadDir           = lm.computeLoadDir()
        g.app.leoDir            = lm.computeLeoDir()
        g.app.homeDir           = lm.computeHomeDir()
        g.app.homeLeoDir        = lm.computeHomeLeoDir()
        g.app.globalConfigDir   = lm.computeGlobalConfigDir()

        g.app.extensionsDir = g.os_path_finalize_join(g.app.loadDir,'..','extensions')
        g.app.testDir       = g.os_path_finalize_join(g.app.loadDir,'..','test')
    #@+node:ekr.20120209051836.10253: *5* lm.computeGlobalConfigDir
    def computeGlobalConfigDir(self):

        # lm = self

        # To avoid pylint complaints that sys.leo_config_directory does not exist.
        leo_config_dir = (
            hasattr(sys,'leo_config_directory') and
            getattr(sys,'leo_config_directory') or None)
        if leo_config_dir:
            theDir = leo_config_dir
        else:
            theDir = g.os_path_join(g.app.loadDir,"..","config")
        if theDir:
            theDir = g.os_path_finalize(theDir)
        if (
            not theDir or
            not g.os_path_exists(theDir) or
            not g.os_path_isdir(theDir)
        ):
            theDir = None
        return theDir
    #@+node:ekr.20120209051836.10254: *5* lm.computeHomeDir
    def computeHomeDir(self):

        """Returns the user's home directory."""

        home = os.path.expanduser("~")
            # Windows searches the HOME, HOMEPATH and HOMEDRIVE
            # environment vars, then gives up.

        if home and len(home) > 1 and home[0]=='%' and home[-1]=='%':
            # Get the indirect reference to the true home.
            home = os.getenv(home[1:-1],default=None)

        if home:
            # Important: This returns the _working_ directory if home is None!
            # This was the source of the 4.3 .leoID.txt problems.
            home = g.os_path_finalize(home)
            if (
                not g.os_path_exists(home) or
                not g.os_path_isdir(home)
            ):
                home = None

        # g.trace(home)
        return home
    #@+node:ekr.20120209051836.10260: *5* lm.computeHomeLeoDir
    def computeHomeLeoDir (self):

        # lm = self
        homeLeoDir = g.os_path_finalize_join(g.app.homeDir,'.leo')
        if not g.os_path_exists(homeLeoDir):
            g.makeAllNonExistentDirectories(homeLeoDir,force=True)
        return homeLeoDir
    #@+node:ekr.20120209051836.10255: *5* lm.computeLeoDir
    def computeLeoDir (self):

        # lm = self
        loadDir = g.app.loadDir
        return g.os_path_dirname(loadDir)
            # We don't want the result in sys.path
    #@+node:ekr.20120209051836.10256: *5* lm.computeLoadDir
    def computeLoadDir(self):

        """Returns the directory containing leo.py."""

        import sys

        try:
            # Fix a hangnail: on Windows the drive letter returned by
            # __file__ is randomly upper or lower case!
            # The made for an ugly recent files list.
            path = g.__file__ # was leo.__file__
            # g.trace(repr(path))
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
                if sys.platform=='win32':
                    if len(path) > 2 and path[1]==':':
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
            # g.trace(loadDir)
            return loadDir
        except:
            print("Exception getting load directory")
            raise
    #@+node:ekr.20120213164030.10697: *5* lm.computeMachineName
    def computeMachineName(self):

        '''Return the name of the current machine, i.e, HOSTNAME.'''

        # This is prepended to leoSettings.leo or myLeoSettings.leo
        # to give the machine-specific setting name.
        # How can this be worth doing??

        try:
            import os
            name = os.getenv('HOSTNAME')
            if not name:
                name = os.getenv('COMPUTERNAME')
            if not name:
                import socket
                name = socket.gethostname()
        except Exception:
            name = ''

        # g.trace(name)

        return name
    #@+node:ekr.20120211121736.10772: *4* LM.computeWorkbookFileName
    def computeWorkbookFileName (self):

        # lm = self

        # Get the name of the workbook.
        fn = g.app.config.getString(setting='default_leo_file')
            # The default is ~/.leo/workbook.leo
        fn = g.os_path_finalize(fn)
        if not fn: return
        if g.os_path_exists(fn):
            return fn
        elif g.os_path_isabs(fn):
            # Create the file.
            g.error('Using default leo file name:\n%s' % (fn))
            return fn
        else:
            # It's too risky to open a default file if it is relative.
            return None
    #@+node:ekr.20120219154958.10485: *4* LM.reportDirectories
    def reportDirectories(self,verbose):

        if not verbose: return

        if 1: # old

            if verbose:
                for kind,theDir in (
                    ("load",g.app.loadDir),
                    ("global config",g.app.globalConfigDir),
                    ("home",g.app.homeDir),
                ):
                    g.blue("%s dir:" % (kind),theDir)

        else:
            aList = (
                'homeDir','homeLeoDir',
                'leoDir','loadDir',
                'extensionsDir','globalConfigDir')

            for ivar in aList:
                val = getattr(g.app,ivar)
                g.trace('%20s' % (ivar),val)

    #@+node:ekr.20120215062153.10740: *3* LM.Settings
    #@+node:ekr.20120130101219.10182: *4* lm.computeBindingLetter
    def computeBindingLetter(self,kind):

        # lm = self
        if not kind:
            return 'D'
        table = (
            ('M','myLeoSettings.leo'),
            (' ','leoSettings.leo'),
            ('F','.leo'),
        )
        for letter,kind2 in table:
            if kind.lower().endswith(kind2.lower()):
                return letter
        else:
            return 'D' if kind.find('mode') == -1 else '@'
    #@+node:ekr.20120223062418.10421: *4* lm.computeLocalSettings (where the crash happened)
    def computeLocalSettings (self,c,settings_d,shortcuts_d,localFlag):

        '''Merge the settings dicts from c's outline into *new copies of*
        settings_d and shortcuts_d.'''

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: g.trace('lm.computeLocalSettings: %s\n%s\n%s' % (
            c.shortFileName(),settings_d,shortcuts_d))

        lm = self

        shortcuts_d2,settings_d2 = lm.createSettingsDicts(c,localFlag)

        assert shortcuts_d
        assert settings_d

        if settings_d2:
            settings_d = settings_d.copy()
            settings_d.update(settings_d2)

        if shortcuts_d2:
            shortcuts_d = lm.mergeShortcutsDicts(c,shortcuts_d,shortcuts_d2)

        return settings_d,shortcuts_d
    #@+node:ekr.20121126202114.3: *4* lm.createDefaultSettingsDicts (New)
    def createDefaultSettingsDicts(self):

        '''Create lm.globalSettingsDict & lm.globalShortcutsDict.'''

        settings_d = g.app.config.defaultsDict
        assert isinstance(settings_d,g.TypedDict),settings_d
        settings_d.setName('lm.globalSettingsDict')

        shortcuts_d = g.TypedDictOfLists(
            name='lm.globalShortcutsDict',
            keyType=type('s'), valType=g.ShortcutInfo)

        return settings_d,shortcuts_d
    #@+node:ekr.20120214165710.10726: *4* lm.createSettingsDicts
    def createSettingsDicts(self,c,localFlag):

        import leo.core.leoConfig as leoConfig

        parser = leoConfig.SettingsTreeParser(c,localFlag)
            # returns the *raw* shortcutsDict, not a *merged* shortcuts dict.

        shortcutsDict,settingsDict = parser.traverse()

        return shortcutsDict,settingsDict
    #@+node:ekr.20120223062418.10414: *4* LM.getPreviousSettings
    def getPreviousSettings (self,fn):

        '''Return the settings in effect for fn.  Typically,
        this involves pre-reading fn.'''

        lm = self
        settingsName  = 'settings dict for %s' % g.shortFileName(fn)
        shortcutsName = 'shortcuts dict for %s' % g.shortFileName(fn)

        # A special case: settings in leoSettings.leo do *not* override
        # the global settings, that is, settings in myLeoSettings.leo.
        isLeoSettings = g.shortFileName(fn).lower()=='leosettings.leo'

        if fn and lm.isLeoFile(fn) and not isLeoSettings and g.os_path_exists(fn):
            # Open the file usinging a null gui.
            try:
                g.app.preReadFlag = True
                c = lm.openSettingsFile(fn)
            finally:
                g.app.preReadFlag = False

            # Merge the settings from c into *copies* of the global dicts.
            d1,d2 = lm.computeLocalSettings(c,
                lm.globalSettingsDict,lm.globalShortcutsDict,localFlag=True)
                    # d1 and d2 are copies.
            d1.setName(settingsName)
            d2.setName(shortcutsName)
        else:
            # Get the settings from the globals settings dicts.
            d1 = lm.globalSettingsDict.copy(settingsName)
            d2 = lm.globalShortcutsDict.copy(shortcutsName)

        return PreviousSettings(d1,d2)
    #@+node:ekr.20120214132927.10723: *4* lm.mergeShortcutsDicts & helpers
    def mergeShortcutsDicts (self,c,old_d,new_d):

        '''Create a new dict by overriding all shortcuts in old_d by shortcuts in new_d.

        Both old_d and new_d remain unchanged.'''

        trace = False and not g.unitTesting
        lm = self

        if not old_d: return new_d
        if not new_d: return old_d

        if trace:
            new_n,old_n = len(list(new_d.keys())),len(list(old_d.keys()))
            g.trace('new %4s %s %s' % (new_n,id(new_d),new_d.name()))
            g.trace('old %4s %s %s' % (old_n,id(old_d),old_d.name()))

        inverted_old_d = lm.invert(old_d)
        inverted_new_d = lm.invert(new_d)

        # Fix bug 951921: check for duplicate shortcuts only in the new file.
        lm.checkForDuplicateShortcuts(c,inverted_new_d)

        inverted_old_d.update(inverted_new_d) # Updates inverted_old_d in place.
        result = lm.uninvert(inverted_old_d)

        return result
    #@+node:ekr.20120311070142.9904: *5* lm.checkForDuplicateShortcuts
    def checkForDuplicateShortcuts (self,c,d):

        '''Check for duplicates in an "inverted" dictionary d
        whose keys are strokes and whose values are lists of ShortcutInfo nodes.

        Duplicates happen only if panes conflict.
        '''

        # lm = self

        # Fix bug 951921: check for duplicate shortcuts only in the new file.
        for ks in sorted(list(d.keys())):
            conflict,panes = False,['all']
            aList = d.get(ks)
            aList2 = [si for si in aList if not si.pane.startswith('mode')]
            if len(aList) > 1:
                for si in aList2:
                    if si.pane in panes:
                        conflict = True ; break
                    else:
                        panes.append(si.pane)
            if conflict:
                g.es_print('conflicting key bindings in %s' % (c.shortFileName()))
                for si in aList2:
                    g.es_print('%6s %s %s' % (si.pane,si.stroke.s,si.commandName))
    #@+node:ekr.20120214132927.10724: *5* lm.invert
    def invert (self,d):

        '''Invert a shortcut dict whose keys are command names,
        returning a dict whose keys are strokes.'''

        trace = False and not g.unitTesting ; verbose = True
        if trace: g.trace('*'*40,d.name())

        result = g.TypedDictOfLists(
            name='inverted %s' % d.name(),
            keyType = g.KeyStroke,
            valType = g.ShortcutInfo)

        for commandName in d.keys():
            for si in d.get(commandName,[]):
                # This assert can fail if there is an exception in the ShortcutInfo ctor.
                assert isinstance(si,g.ShortcutInfo),si

                stroke = si.stroke # This is canonicalized.
                si.commandName = commandName # Add info.
                assert stroke
                if trace and verbose:
                    g.trace('%40s %s' % (commandName,stroke))
                result.add(stroke,si)

        if trace: g.trace('returns  %4s %s %s' % (
            len(list(result.keys())),id(d),result.name()))
        return result
    #@+node:ekr.20120214132927.10725: *5* lm.uninvert
    def uninvert (self,d):

        '''Uninvert an inverted shortcut dict whose keys are strokes,
        returning a dict whose keys are command names.'''

        trace = False and not g.unitTesting ; verbose = True
        if trace and verbose: g.trace('*'*40)

        assert d.keyType == g.KeyStroke,d.keyType
        result = g.TypedDictOfLists(
            name='uninverted %s' % d.name(),
            keyType = type('commandName'),
            valType = g.ShortcutInfo)

        for stroke in d.keys():
            for si in d.get(stroke,[]):
                assert isinstance(si,g.ShortcutInfo),si
                commandName = si.commandName
                if trace and verbose:
                    g.trace('uninvert %20s %s' % (stroke,commandName))
                assert commandName
                result.add(commandName,si)

        if trace: g.trace('returns %4s %s %s' % (
            len(list(result.keys())),id(d),result.name()))
        return result
    #@+node:ekr.20120222103014.10312: *4* lm.openSettingsFile
    def openSettingsFile (self,fn):

        '''Open a settings file with a null gui.  Return the commander.

        The caller must init the c.config object.'''

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('lm.openSettingsFile: g.app.gui: %s' % (
            g.shortFileName(fn)))

        lm = self
        if not fn: return None

        giveMessage = (
            not g.app.unitTesting and
            not g.app.silentMode and
            not g.app.batchMode)
            # and not g.app.inBridge
        def message(s):
            # This occurs early in startup, so use the following.
            if not giveMessage: return
            if not g.isPython3:
                s = g.toEncodedString(s,'ascii')
            g.blue(s)

        theFile = lm.openLeoOrZipFile(fn)

        if theFile:
            message('reading settings in %s' % (fn))

        # Changing g.app.gui here is a major hack.  It is necessary.
        oldGui = g.app.gui
        g.app.gui = g.app.nullGui
        c = g.app.newCommander(fn)
        frame = c.frame
        frame.log.enable(False)
        g.app.lockLog()
        ok = c.fileCommands.openLeoFile(theFile,fn,
            readAtFileNodesFlag=False,silent=True)
                # closes theFile.
        g.app.unlockLog()
        c.openDirectory = frame.openDirectory = g.os_path_dirname(fn)
        g.app.gui = oldGui
        return ok and c or None
    #@+node:ekr.20120213081706.10382: *4* lm.readGlobalSettingsFiles (changed)
    def readGlobalSettingsFiles (self):

        '''Read leoSettings.leo and myLeoSettings.leo using a null gui.'''

        trace = (False or g.trace_startup) and not g.unitTesting
        verbose = False
        tag = 'lm.readGlobalSettingsFiles'
        lm = self

        if trace and g.trace_startup:
            print('\n<<<<< %s' % tag)

        # Open the standard settings files with a nullGui.
        # Important: their commanders do not exist outside this method!
        commanders = [
            lm.openSettingsFile(path) for path in (
                lm.computeLeoSettingsPath(),
                lm.computeMyLeoSettingsPath())]

        settings_d,shortcuts_d = lm.createDefaultSettingsDicts()

        for c in commanders:
            if c:
                settings_d,shortcuts_d = lm.computeLocalSettings(
                    c,settings_d,shortcuts_d,localFlag=False)

        # Adjust the name.
        shortcuts_d.setName('lm.globalShortcutsDict')

        if trace:
            if verbose:
                for c in commanders:
                    print(c)
            lm.traceSettingsDict(settings_d,verbose)
            lm.traceShortcutsDict(shortcuts_d,verbose)
            print('\n>>>>>%s...' % tag)

        lm.globalSettingsDict = settings_d
        lm.globalShortcutsDict = shortcuts_d
    #@+node:ekr.20120214165710.10838: *4* lm.traceSettingsDict
    def traceSettingsDict (self,d,verbose=False):

        if verbose:
            print(d)
            for key in sorted(list(d.keys())):
                gs = d.get(key)
                print('%35s %17s %s' % (key,g.shortFileName(gs.path),gs.val))
            if d: print('')
        else:
            print(d)
    #@+node:ekr.20120214165710.10822: *4* lm.traceShortcutsDict
    def traceShortcutsDict (self,d,verbose=False):

        if verbose:
            print(d)
            for key in sorted(list(d.keys())):
                val = d.get(key)
                # print('%20s %s' % (key,val.dump()))
                print('%35s %s' % (key,[z.stroke for z in val]))
            if d: print('')
        else:
            print(d)
    #@+node:ekr.20120219154958.10452: *3* LM.load
    def load (self,fileName=None,pymacs=None):

        '''Load the indicated file'''
        lm = self
        # Phase 1: before loading plugins.
        # Scan options, set directories and read settings.
        if not lm.isValidPython(): return
        lm.doPrePluginsInit(fileName,pymacs)
            # sets lm.options and lm.files
        if lm.options.get('version'):
            print(g.app.signon)
            return
        if not g.app.gui:
            return
        # Phase 2: load plugins: the gui has already been set.
        g.doHook("start1")
        if g.app.killed: return
        # Phase 3: after loading plugins. Create one or more frames.
        ok = lm.doPostPluginsInit()
        if ok:
            g.es('') # Clears horizontal scrolling in the log pane.
            g.app.gui.runMainLoop()
            # For scripts, the gui is a nullGui.
            # and the gui.setScript has already been called.
    #@+node:ekr.20120219154958.10477: *4* LM.doPrePluginsInit & helpers
    def doPrePluginsInit(self,fileName,pymacs):

        ''' Scan options, set directories and read settings.'''

        # trace = False
        lm = self
        lm.computeStandardDirectories()
        lm.adjustSysPath()

        # Scan the options as early as possible.
        lm.options = options = lm.scanOptions(fileName,pymacs)
            # also sets lm.files.

        if options.get('version'):
            g.app.computeSignon()
            return

        script = options.get('script')
        verbose = script is None

        # Init the app.
        lm.initApp(verbose)
        lm.reportDirectories(verbose)

        # Read settings *after* setting g.app.config and *before* opening plugins.
        # This means if-gui has effect only in per-file settings.
        lm.readGlobalSettingsFiles()
            # reads only standard settings files, using a null gui.
            # uses lm.files[0] to compute the local directory
            # that might contain myLeoSettings.leo.

        # Read the recent files file.
        localConfigFile = lm.files[0] if lm.files else None
        g.app.recentFilesManager.readRecentFiles(localConfigFile)

        g.app.setGlobalDb()

        # Create the gui after reading options and settings.
        lm.createGui(pymacs)

        # We can't print the signon until we know the gui.
        g.app.computeSignon() # Set app.signon/signon2 for commanders.
    #@+node:ekr.20120219154958.10478: *5* LM.createGui
    def createGui(self,pymacs):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('\n==================== LM.createGui')

        lm = self

        gui_option = lm.options.get('gui')
        windowFlag = lm.options.get('windowFlag')
        script     = lm.options.get('script')

        if g.app.gui:
            if g.app.gui == g.app.nullGui:
                g.app.gui = None # Enable g.app.createDefaultGui 
                g.app.createDefaultGui(__file__)
            else:
                # This can happen when launching Leo from IPython.
                g.trace('g.app.gui',g.app.gui)
        elif gui_option is None:
            if script and not windowFlag:
                # Always use null gui for scripts.
                g.app.createNullGuiWithScript(script)
            else:
                g.app.createDefaultGui(__file__)
        else:
            lm.createSpecialGui(gui_option,pymacs,script,windowFlag)
    #@+node:ekr.20120219154958.10479: *5* LM.createSpecialGui
    def createSpecialGui(self,gui,pymacs,script,windowFlag):

        # lm = self

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
    #@+node:ekr.20120219154958.10480: *5* LM.adjustSysPath
    def adjustSysPath (self):

        '''Adjust sys.path to enable imports as usual with Leo.

        This method is no longer needed:

            1. g.importModule will import from the
               'external' or 'extensions' folders as needed
               without altering sys.path.

            2.  Plugins now do fully qualified imports.
        '''

        pass
    #@+node:ekr.20120219154958.10482: *5* LM.getDefaultFile
    def getDefaultFile (self):

        # Get the name of the workbook.
        fn = g.app.config.getString('default_leo_file')
        fn = g.os_path_finalize(fn)
        if not fn: return
        # g.trace(g.os_path_exists(fn),fn)
        if g.os_path_exists(fn):
            return fn
        elif g.os_path_isabs(fn):
            # Create the file.
            g.error('Using default leo file name:\n%s' % (fn))
            return fn
        else:
            # It's too risky to open a default file if it is relative.
            return None
    #@+node:ekr.20120219154958.10484: *5* LM.initApp
    def initApp (self,verbose):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('LM.initApp')
        assert g.app.loadManager
        import leo.core.leoConfig as leoConfig
        import leo.core.leoNodes as leoNodes
        import leo.core.leoPlugins as leoPlugins
        import leo.core.leoSessions as leoSessions
        # Import leoIPython only if requested.  The import is quite slow.
        if g.app.useIpython:
            import leo.core.leoIPython as leoIPython
        # Make sure we call the new leoPlugins.init top-level function.
        leoPlugins.init()
        # Force the user to set g.app.leoID.
        g.app.setLeoID(verbose=verbose)
        # Create early classes *after* doing plugins.init()
        g.app.recentFilesManager = RecentFilesManager()
        g.app.config = leoConfig.GlobalConfigManager()
        g.app.nodeIndices = leoNodes.nodeIndices(g.app.leoID)
        g.app.sessionManager = leoSessions.SessionManager()
        # Complete the plugins class last.
        g.app.pluginsController.finishCreate()
    #@+node:ekr.20120219154958.10486: *5* LM.scanOptions & helper
    def scanOptions(self,fileName,pymacs):

        '''Handle all options, remove them from sys.argv and set lm.options.'''

        trace = False
        lm = self
        # print('scanOptions',sys.argv)

        # Note: this automatically implements the --help option.
        parser = optparse.OptionParser()
        add = parser.add_option
        add('--fullscreen', action="store_true",
            help = 'start fullscreen')
        add('--ipython',    action="store_true",dest="use_ipython",
            help = 'enable ipython support')
        add('--gui',
            help = 'gui to use (qt/qttabs)')
        add('--maximized', action="store_true",
            help = 'start maximized')
        add('--minimized', action="store_true",
            help = 'start minimized')
        add('--no-cache', action="store_true", dest='no_cache',
            help = 'disable reading of cached files')
        add('--no-plugins', action="store_true", dest='no_plugins',
            help = 'disable all plugins')
        add('--no-splash', action="store_true", dest='no_splash_screen',
            help = 'disable the splash screen')
        add('--screen-shot', dest='screenshot_fn',
            help = 'take a screen shot and then exit')
        add('--script', dest="script",
            help = 'execute a script and then exit')
        add('--script-window',dest="script_window",
            help = 'open a window for scripts')
        add('--select', dest='select',
            help='headline or gnx of node to select')
        add('--session-restore', action="store_true", dest='session_restore',
            help = 'restore previously saved session tabs at startup')
        add('--session-save', action="store_true", dest='session_save',
            help = 'save session tabs on exit')
        add('--silent', action="store_true", dest="silent",
            help = 'disable all log messages')
        add('-v', '--version', action="store_true", dest="version",
            help='print version number and exit')
        add('--window-size', dest='window_size',
            help='initial window size (height x width)')

        # Parse the options, and remove them from sys.argv.
        options, args = parser.parse_args()
        sys.argv = [sys.argv[0]] ; sys.argv.extend(args)
        if trace:
            # print('scanOptions:',sys.argv)
            g.trace('options',options)

        # Handle the args...
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
        g.app.guiArgName = gui
        # --ipython
        g.app.useIpython = options.use_ipython
        if trace: g.trace('g.app.useIpython',g.app.useIpython)
        # --fullscreen
        # --minimized
        # --maximized
        g.app.start_fullscreen = options.fullscreen
        g.app.start_maximized = options.maximized
        g.app.start_minimized = options.minimized
        # --no-cache
        if options.no_cache:
            if trace: print('scanOptions: disabling caching')
            g.enableDB = False
        # --no-plugins
        if options.no_plugins:
            if trace: print('scanOptions: disabling plugins')
            g.app.enablePlugins = False
        # --no-splash: --minimized disables the splash screen
        g.app.use_splash_screen = (
            not options.no_splash_screen and
            not options.minimized)
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
        # --session-restore & --session-save
        g.app.restore_session = bool(options.session_restore)
        g.app.save_session = bool(options.session_save)
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
                windowSize = int(h),int(w)
            except ValueError:
                windowSize = None
                g.trace('bad --window-size:',windowSize)
        # Compute lm.files
        lm.files = lm.computeFilesList(fileName)
        # Post-process the options.
        if pymacs:
            script = None
            windowFlag = None
        # Compute the return values.
        windowFlag = script and script_path_w
        d = {
            'gui':gui,
            'screenshot_fn':screenshot_fn,
            'script':script,
            'select':select,
            'version':versionFlag,
            'windowFlag':windowFlag,
            'windowSize':windowSize,
        }
        if trace: g.trace(d)
        return d
    #@+node:ekr.20120219154958.10483: *6* LM.computeFilesList
    def computeFilesList(self,fileName):

        lm = self
        files = []
        if fileName:
            files.append(fileName)

        for arg in sys.argv[1:]:
            if arg and not arg.startswith('-'):
                files.append(arg)

        return [lm.completeFileName(z) for z in files]
    #@+node:ekr.20120219154958.10487: *4* LM.doPostPluginsInit & helpers
    def doPostPluginsInit(self):

        '''Create a Leo window for each file in the lm.files list.'''

        # Clear g.app.initing _before_ creating commanders.
        lm = self
        g.app.initing = False # "idle" hooks may now call g.app.forceShutdown.
        # Create the main frame.  Show it and all queued messages.
        # g.trace(lm.files)
        if lm.files:
            # A terrible kludge for Linux only:
            # When using tabs, the first tab has no menu, so
            # create a temp tab during loading and then delete it.
            kludge = sys.platform.lower().startswith('linux') and g.app.qt_use_tabs
            c1 = None
            if kludge:
                c0 = g.app.newCommander(fileName='loading...',gui=g.app.gui,
                    previousSettings=None)
            for fn in lm.files:
                c = lm.loadLocalFile(fn,gui=g.app.gui,old_c=None)
                    # Will give a "not found" message.
                # This can fail if the file is open in another instance of Leo.
                # assert c
                if not c1: c1 = c
                if kludge:
                    # Now destroy the dummy frame, leaving menus in all real frames.
                    g.app.destroyWindow(c0.frame)
                    kludge = False
        else:
            c = c1 = None
        if g.app.restore_session:
            m = g.app.sessionManager
            if m:
                aList = m.load_snapshot()
                if aList:
                    m.load_session(c1,aList)
                    c = c1 = g.app.windowList[0].c
        if not g.app.windowList:
            c1 = lm.openEmptyWorkBook()
        # Put the focus in the first-opened file.
        fileName = lm.files[0] if lm.files else None
        c = c1
        # For qttabs gui, select the first-loaded tab.
        if hasattr(g.app.gui,'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory,'setTabForCommander'):
                factory.setTabForCommander(c)
        # Fix bug 844953: tell Unity which menu to use.
        c.enableMenuBar()
        # Do the final inits.
        g.app.logInited = True
        g.app.initComplete = True
        c.setLog()
        # print('doPostPluginsInit: ***** set log')
        g.doHook("start2",c=c,p=c.p,v=c.p,fileName=fileName)
        g.enableIdleTimeHook(idleTimeDelay=500)
        lm.initFocusAndDraw(c,fileName)
        screenshot_fn = lm.options.get('screenshot_fn')
        if screenshot_fn:
            lm.make_screen_shot(screenshot_fn)
            return False # Force an immediate exit.
        return True
    #@+node:ekr.20120219154958.10488: *5* LM.initFocusAndDraw
    def initFocusAndDraw(self,c,fileName):

        w = g.app.gui.get_focus(c)

        if not fileName:
            c.redraw()

        # Respect c's focus wishes if posssible.
        if w != c.frame.body.bodyCtrl and w != c.frame.tree.canvas:
            c.bodyWantsFocus()
            c.k.showStateAndMode(w)

        c.outerUpdate()
    #@+node:ekr.20120219154958.10489: *5* LM.make_screen_shot
    def make_screen_shot(self,fn):

        '''Create a screenshot of the present Leo outline and save it to path.'''

        # g.trace('runLeo.py',fn)

        if g.app.gui.guiName() == 'qt':
            m = g.loadOnePlugin('screenshots')
            m.make_screen_shot(fn)
    #@+node:ekr.20131028155339.17098: *5* LM.openEmptyWorkBook
    def openEmptyWorkBook(self):
        '''Open an empty frame and paste the contents of CheatSheet.leo into it.'''
        lm = self
        # Create an empty frame.
        fn = lm.computeWorkbookFileName()
        c = lm.loadLocalFile(fn,gui=g.app.gui,old_c=None)
        # Open the cheatsheet.
        if not g.os_path_exists(fn):
            # Paste the contents of CheetSheet.leo into c1.
            c2 = c.openCheatSheet(redraw=False)
            if c2:
                for p2 in c2.rootPosition().self_and_siblings():
                    c2.selectPosition(p2)
                    c2.copyOutline()
                    p = c.pasteOutline()
                    c.selectPosition(p)
                    p.contract()
                    p.clearDirty()
                c2.close(new_c=c)
                root = c.rootPosition()
                if root.h == g.shortFileName(fn):
                    root.doDelete(newNode=root.next())
                p = g.findNodeAnywhere(c,"Leo's cheat sheet")
                if p:
                    c.selectPosition(p,enableRedrawFlag=False)
                    # p.expand()
                c.target_language = 'rest'
                    # Settings not parsed the first time.
                c.setChanged(False)
                c.redraw()
        return c
    #@+node:ekr.20120219154958.10491: *4* LM.isValidPython & emergency (Tk) dialog class
    def isValidPython(self):

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
                    #@+node:ekr.20120219154958.10492: *5* << define emergency dialog class >>
                    class emergencyDialog:

                        """A class that creates an Tkinter dialog with a single OK button."""

                        #@+others
                        #@+node:ekr.20120219154958.10493: *6* __init__ (emergencyDialog)
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
                        #@+node:ekr.20120219154958.10494: *6* createButtons
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
                        #@+node:ekr.20120219154958.10495: *6* createTopFrame
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
                        #@+node:ekr.20120219154958.10496: *6* okButton
                        def okButton(self):

                            """Do default click action in ok button."""

                            self.top.destroy()
                            self.top = None

                        #@+node:ekr.20120219154958.10497: *6* onKey
                        def onKey(self,event):

                            """Handle Key events in askOk dialogs."""

                            self.okButton()

                            return # (for Tk) "break"
                        #@+node:ekr.20120219154958.10498: *6* run
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
    #@+node:ekr.20120223062418.10393: *4* LM.loadLocalFile & helper
    def loadLocalFile (self,fn,gui,old_c):

        '''Completely read a file, creating the corresonding outline.

        1. If fn is an existing .leo file (possibly zipped), read it twice:
        the first time with a nullGui to discover settings,
        the second time with the requested gui to create the outline.

        2. If fn is an external file:
        get settings from the leoSettings.leo and myLeoSetting.leo, then
        create a "wrapper" outline continain an @file node for the external file.

        3. If fn is empty:
        get settings from the leoSettings.leo and myLeoSetting.leo or default settings,
        or open an empty outline.
        '''

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('lm.loadLocalFile: %s' % (fn))
        lm = self
        # Step 0: Return if the file is already open.
        fn = g.os_path_finalize(fn)
        if fn:
            c = lm.findOpenFile(fn)
            if c:
                if trace: g.trace('Already open: %s' % (fn))
                return c
        # Step 1: get the previous settings.
        # For .leo files (and zipped .leo files) this pre-reads the file in a null gui.
        # Otherwise, get settings from leoSettings.leo, myLeoSettings.leo, or default settings.
        previousSettings = lm.getPreviousSettings(fn)
        # Step 2: open the outline in the requested gui.
        # For .leo files (and zipped .leo file) this opens the file a second time.
        c = lm.openFileByName(fn,gui,old_c,previousSettings)
        return c
    #@+node:ekr.20120223062418.10394: *5* LM.openFileByName & helpers
    def openFileByName (self,fn,gui,old_c,previousSettings):

        '''Read the local file whose full path is fn using the given gui.
        fn may be a Leo file (including .leo or zipped file) or an external file.

        This is not a pre-read: the previousSettings always exist and
        the commander created here persists until the user closes the outline.

        Reads the entire outline if fn exists and is a .leo file or zipped file.
        Creates an empty outline if fn is a non-existent Leo file.
        Creates an wrapper outline if fn is an external file, existing or not.
        '''

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('lm.openFileByName: %s' % (g.shortFileName(fn)))   
        lm = self

        # Disable the log.
        g.app.setLog(None)
        g.app.lockLog()

        # Create the a commander for the .leo file.
        # Important.  The settings don't matter for pre-reads!
        # For second read, the settings for the file are *exactly* previousSettings.
        c = g.app.newCommander(fileName=fn,gui=gui,
            previousSettings=previousSettings)
        assert c

        # Open the file, if possible.
        g.doHook('open0')
        theFile = lm.openLeoOrZipFile(fn)

        # Enable the log.
        g.app.unlockLog()
        c.frame.log.enable(True)

        # Phase 2: Create the outline.
        g.doHook("open1",old_c=None,c=c,new_c=c,fileName=fn)
        if theFile:
            readAtFileNodesFlag = bool(previousSettings)
            ### The log is not set properly here. ###
            ok = lm.readOpenedLeoFile(c,gui,fn,readAtFileNodesFlag,theFile)
                # Call c.fileCommands.openLeoFile to read the .leo file.
            if not ok: return None
        else:
            # Create a wrapper .leo file if:
            # a) fn is a .leo file that does not exist or
            # b) fn is an external file, existing or not.
            lm.initWrapperLeoFile(c,fn)
        g.doHook("open2",old_c=None,c=c,new_c=c,fileName=fn)

        # Phase 3: Complete the initialization.
        g.app.writeWaitingLog(c)
        c.setLog()
        lm.createMenu(c,fn)
        lm.finishOpen(c)
        return c
    #@+node:ekr.20120223062418.10405: *6* LM.createMenu
    def createMenu(self,c,fn=None):

        # lm = self

        # Create the menu as late as possible so it can use user commands.
        if not g.doHook("menu1",c=c,p=c.p,v=c.p):
            c.frame.menu.createMenuBar(c.frame)
            g.app.recentFilesManager.updateRecentFiles(fn)
            g.doHook("menu2",c=c,p=c.p,v=c.p)
            g.doHook("after-create-leo-frame",c=c)
            g.doHook("after-create-leo-frame2",c=c)

            # Fix bug 844953: tell Unity which menu to use.
            c.enableMenuBar()
    #@+node:ekr.20120223062418.10406: *6* LM.findOpenFile
    def findOpenFile(self,fn):

        # lm = self

        def munge(name):
            return g.os_path_normpath(name or '').lower()

        for frame in g.app.windowList:
            c = frame.c
            if g.os_path_realpath(munge(fn)) == g.os_path_realpath(munge(c.mFileName)):
                frame.bringToFront()
                c.setLog()
                # 2011/11/21: selecting the new tab ensures focus is set.
                master = hasattr(frame.top,'leo_master') and frame.top.leo_master
                if master: # frame.top.leo_master is a TabbedTopLevel.
                    master.select(frame.c)
                c.outerUpdate()
                return c

        return None
    #@+node:ekr.20120223062418.10407: *6* LM.finishOpen
    def finishOpen(self,c):

        # lm = self
        k = c.k
        assert k

        # New in Leo 4.6: provide an official way for very late initialization.
        c.frame.tree.initAfterLoad()
        c.initAfterLoad()
        c.redraw()

        # chapterController.finishCreate must be called after the first real redraw
        # because it requires a valid value for c.rootPosition().
        if c.chapterController: c.chapterController.finishCreate()
        if k: k.setDefaultInputState()
        c.initialFocusHelper()
        if k: k.showStateAndMode()
        c.frame.initCompleteHint()

    #@+node:ekr.20120223062418.10408: *6* LM.initWrapperLeoFile
    def initWrapperLeoFile (self,c,fn):
        '''
        Create an empty file if the external fn is empty.

        Otherwise, create an @edit or @file node for the external file.
        '''
        # lm = self
        # Use the config params to set the size and location of the window.
        frame = c.frame
        frame.setInitialWindowGeometry()
        frame.deiconify()
        frame.lift()
        frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio)
            # Resize the _new_ frame.
        if not g.os_path_exists(fn):
            p = c.rootPosition()
            # Create an empty @edit node unless fn is an .leo file.
            p.h = g.shortFileName(fn) if fn.endswith('.leo') else '@edit %s' % fn
            c.selectPosition(p)
        elif c.looksLikeDerivedFile(fn):
            # 2011/10/10: Create an @file node.
            p = c.importCommands.importDerivedFiles(parent=c.rootPosition(),
                paths=[fn],command=None) # Not undoable.
            if not p: return None
        else:
            # Create an @edit node.
            s,e = g.readFileIntoString(fn)
            if s is None: return None
            p = c.rootPosition()
            if p:
                p.setHeadString('@edit %s' % fn)
                p.setBodyString(s)
                c.selectPosition(p)
        # Fix critical bug 1184855: data loss with command line 'leo somefile.ext'
        # 2013/09/25: Fix smallish bug 1226816 Command line "leo xxx.leo" creates file xxx.leo.leo.
        c.mFileName = fn if fn.endswith('.leo') else '%s.leo' % (fn)
        c.frame.title = c.computeWindowTitle(c.mFileName)
        c.frame.setTitle(c.frame.title)
        # chapterController.finishCreate must be called after the first real redraw
        # because it requires a valid value for c.rootPosition().
        if c.config.getBool('use_chapters') and c.chapterController:
            c.chapterController.finishCreate()
        frame.c.setChanged(False)
            # Mark the outline clean.
            # This makes it easy to open non-Leo files for quick study.
        return c
    #@+node:ekr.20120223062418.10419: *6* LM.isLeoFile & LM.isZippedFile
    def isLeoFile(self,fn):

        return fn and (zipfile.is_zipfile(fn) or fn.endswith('.leo'))

    def isZippedFile(self,fn):

        return fn and zipfile.is_zipfile(fn)
    #@+node:ekr.20120224161905.10030: *6* LM.openLeoOrZipFile
    def openLeoOrZipFile (self,fn):

        lm = self

        zipped = lm.isZippedFile(fn)

        if lm.isLeoFile(fn) and g.os_path_exists(fn):
            if zipped:
                theFile = lm.openZipFile(fn)
            else:
                theFile = lm.openLeoFile(fn)
        else:
            theFile = None

        return theFile
    #@+node:ekr.20120223062418.10416: *6* LM.openLeoFile
    def openLeoFile (self,fn):

        # lm = self
        try:
            theFile = open(fn,'rb')
            return theFile
        except IOError:
            # Do not use string + here: it will fail for non-ascii strings!
            if not g.unitTesting:
                g.error("can not open:",fn)
            return None
    #@+node:ekr.20120223062418.10410: *6* LM.openZipFile
    def openZipFile (self,fn):

        # lm = self
        try:
            theFile = zipfile.ZipFile(fn,'r')
            if not theFile: return None

            # Read the file into an StringIO file.
            aList = theFile.namelist()
            name = aList and len(aList) == 1 and aList[0]
            if not name: return None
            s = theFile.read(name)
            if g.isPython3: s = g.ue(s,'utf-8')
            return StringIO(s)

        except IOError:
            # Do not use string + here: it will fail for non-ascii strings!
            if not g.unitTesting:
                g.error("can not open:",fn)
            return None
    #@+node:ekr.20120223062418.10412: *6* LM.readOpenedLeoFile
    def readOpenedLeoFile(self,c,gui,fn,readAtFileNodesFlag,theFile):

        # New in Leo 4.10: The open1 event does not allow an override of the init logic.
        assert theFile
        # lm = self
        ok = c.fileCommands.openLeoFile(theFile,fn,
            readAtFileNodesFlag=readAtFileNodesFlag)
                # closes file.
        if ok:
            if not c.openDirectory:
                theDir = c.os_path_finalize(g.os_path_dirname(fn))
                c.openDirectory = c.frame.openDirectory = theDir 
        else:
            g.app.closeLeoWindow(c.frame)
        return ok
    #@-others

#@+node:ekr.20120211121736.10831: ** class LogManager
class LogManager:

    '''A class to handle the global log, and especially
    switching the log from commander to commander.'''

    def __init__ (self):

        trace = (False or g.trace_startup) and not g.unitTesting
        if trace: print('LogManager.__init__',g.callers())

        self.log = None             # The LeoFrame containing the present log.
        self.logInited = False      # False: all log message go to logWaiting list.
        self.logIsLocked = False    # True: no changes to log are allowed.
        self.logWaiting = []        # List of messages waiting to go to a log.
        self.printWaiting = []      # Queue of messages to be sent to the printer.
        self.signon_printed = False # True: the global signon has been printed.

    #@+others
    #@+node:ekr.20120211121736.10834: *3* LogM.setLog, lockLog, unlocklog
    def setLog (self,log):

        """set the frame to which log messages will go"""

        # print("app.setLog:",log,g.callers())
        if not self.logIsLocked:
            self.log = log

    def lockLog(self):
        """Disable changes to the log"""
        self.logIsLocked = True

    def unlockLog(self):
        """Enable changes to the log"""
        self.logIsLocked = False
    #@+node:ekr.20120211121736.10836: *3* LogM.writeWaitingLog
    def writeWaitingLog (self,c):

        trace = False
        lm = self

        if trace:
            # Do not call g.es, g.es_print, g.pr or g.trace here!
            print('** writeWaitingLog','silent',g.app.silentMode,c.shortFileName())
            # print('writeWaitingLog',g.callers())
            # import sys ; print('writeWaitingLog: argv',sys.argv)

        if not c or not c.exists:
            return

        if g.unitTesting:
            lm.printWaiting = []
            lm.logWaiting = []
            g.app.setLog(None) # Prepare to requeue for other commanders.
            return

        table = [
            ('Leo Log Window','red'),
            (g.app.signon,'black'),
            (g.app.signon2,'black'),
        ]
        table.reverse()

        c.setLog() # 2010/10/20
        lm.logInited = True # Prevent recursive call.

        if not lm.signon_printed:
            lm.signon_printed = True
            if not g.app.silentMode: # 2011/11/02:
                print('')
                print('** isPython3: %s' % g.isPython3)
                if not g.enableDB:
                    print('** caching disabled')
                print(g.app.signon)
                print(g.app.signon2)
        if not g.app.silentMode: # 2011/11/02:
            for s in lm.printWaiting:
                print(s)
        lm.printWaiting = []

        if not g.app.silentMode:  # 2011/11/02:
            for s,color in table:
                lm.logWaiting.insert(0,(s+'\n',color),)
            for s,color in lm.logWaiting:
                g.es('',s,color=color,newline=0)
                    # The caller must write the newlines.
        lm.logWaiting = []

        # Essential when opening multiple files...
        lm.setLog(None) 
    #@-others
#@+node:ekr.20120223062418.10420: ** class PreviousSettings
class PreviousSettings:

    '''A class holding the settings and shortcuts dictionaries
    that are computed in the first pass when loading local
    files and passed to the second pass.'''

    def __init__ (self,settingsDict,shortcutsDict):

        assert g.isTypedDict(settingsDict)
        assert g.isTypedDictOfLists(shortcutsDict)

        self.settingsDict = settingsDict
        self.shortcutsDict = shortcutsDict

    def __repr__ (self):

        return '<PreviousSettings\n%s\n%s\n>' % (
            self.settingsDict,self.shortcutsDict)

    __str__ = __repr__
#@+node:ekr.20120225072226.10283: ** class RecentFilesManager
class RecentFilesManager:

    '''A class to manipulate leoRecentFiles.txt.'''

    def __init__ (self):

        self.groupedMenus = []
            # Set in rf.createRecentFilesMenuItems.
        self.recentFiles = []
            # List of g.Bunches describing .leoRecentFiles.txt files.
        self.recentFileMessageWritten = False
            # To suppress all but the first message.
        self.write_recent_files_as_needed = False
            # Will be set later.

    #@+others
    #@+node:ekr.20041201080436: *3* rf.appendToRecentFiles
    def appendToRecentFiles (self,files):

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
    def cleanRecentFiles(self,c):

        '''Removed items from the recent files list that are no longer valid.'''

        rf = self

        dat = c.config.getData('path-demangle')
        if not dat:
            g.es('No @data path-demangle setting')
            return

        changes = []
        replace = None
        for line in dat:
            text = line.strip()
            if text.startswith('REPLACE: '):
                replace = text.split(None, 1)[1].strip()
            if text.startswith('WITH:') and replace is not None:
                with_ = text[5:].strip()
                changes.append((replace, with_))
                g.es('%s -> %s' % changes[-1])

        orig = [z for z in rf.recentFiles if z.startswith("/")]

        rf.recentFiles = []

        for i in orig:
            t = i
            for change in changes:
                t = t.replace(*change)
            rf.updateRecentFiles(t)

        rf.writeRecentFilesFile(c,force=True)
            # Force the write message.
    #@+node:ekr.20120225072226.10297: *3* rf.clearRecentFiles
    def clearRecentFiles (self,c):

        """Clear the recent files list, then add the present file."""

        rf = self ; u = c.undoer ; menu = c.frame.menu

        bunch = u.beforeClearRecentFiles()

        recentFilesMenu = menu.getMenu("Recent Files...")
        menu.deleteRecentFilesMenuItems(recentFilesMenu)

        rf.recentFiles = [c.fileName()]
        for frame in g.app.windowList:
            rf.createRecentFilesMenuItems(frame.c)

        u.afterClearRecentFiles(bunch)

        # Write the file immediately.
        rf.writeRecentFilesFile(c,force=True)
            # Force the write message.
    #@+node:ekr.20120225072226.10301: *3* rf.createRecentFilesMenuItems
    def createRecentFilesMenuItems (self,c):

        rf = self
        menu = c.frame.menu

        recentFilesMenu = menu.getMenu("Recent Files...")

        if not recentFilesMenu and not g.unitTesting:
            # g.trace('Recent Files Menu does not exist',g.callers())
            return

        # Delete all previous entries.
        menu.deleteRecentFilesMenuItems(recentFilesMenu)

        # Create the permanent (static) menu entries.
        table = rf.getRecentFilesTable()
        menu.createMenuEntries(recentFilesMenu,table)

        # Create all the other entries (a maximum of 36).
        accel_ch = string.digits + string.ascii_uppercase # Not a unicode problem.
        i = 0
        n = len(accel_ch)

        # see if we're grouping when files occur in more than one place
        rf_group = c.config.getBool("recent_files_group")
        rf_always = c.config.getBool("recent_files_group_always")
        groupedEntries = rf_group or rf_always

        if groupedEntries:  # if so, make dict of groups
            dirCount = {}
            for fileName in rf.getRecentFiles()[:n]:
                dirName, baseName = g.os_path_split(fileName)
                if baseName not in dirCount:
                    dirCount[baseName] = {'dirs':[], 'entry': None}
                dirCount[baseName]['dirs'].append(dirName)

        for name in rf.getRecentFiles()[:n]:
            if name.strip() == "":
                continue  # happens with empty list/new file

            def recentFilesCallback (event=None,c=c,name=name):
                c.openRecentFile(name)

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
                    c.add_command(recentFilesMenu,label=baseName,
                        command=recentFilesCallback,underline=0)

            else:  # original behavior
                label = "%s %s" % (accel_ch[i],g.computeWindowTitle(name))
                c.add_command(recentFilesMenu,label=label,
                    command=recentFilesCallback,underline=0)
            i += 1

        if groupedEntries:  # store so we can delete them later
            rf.groupedMenus = [z for z in dirCount
                if dirCount[z]['entry'] is not None]
    #@+node:ekr.20120225072226.10286: *3* rf.getRecentFiles
    def getRecentFiles (self):

        return self.recentFiles
    #@+node:ekr.20120225072226.10304: *3* rf.getRecentFilesTable
    def getRecentFilesTable (self):

        return (
            "*clear-recent-files",
            "*clean-recent-files",
            "*sort-recent-files",
            # ("-",None,None),
        )
    #@+node:ekr.20070224115832: *3* rf.readRecentFiles & helpers
    def readRecentFiles (self,localConfigFile):

        '''Read all .leoRecentFiles.txt files.'''

        # The order of files in this list affects the order of the recent files list.
        rf = self
        seen = [] 
        localConfigPath = g.os_path_dirname(localConfigFile)

        for path in (
            g.app.homeLeoDir,
            g.app.globalConfigDir,
            localConfigPath,
        ):
            if path:
                path = g.os_path_realpath(g.os_path_finalize(path))
            if path and path not in seen:
                ok = rf.readRecentFilesFile(path)
                if ok: seen.append(path)

        if not seen and rf.write_recent_files_as_needed:
            rf.createRecentFiles()
    #@+node:ekr.20061010121944: *4* rf.createRecentFiles
    def createRecentFiles (self):

        '''Trye to reate .leoRecentFiles.txt in
        - the users home directory first,
        - Leo's config directory second.'''

        for theDir in (g.app.homeLeoDir,g.app.globalConfigDir):
            if theDir:
                try:
                    fn = g.os_path_join(theDir,'.leoRecentFiles.txt')
                    f = open(fn,'w')
                    f.close()
                    g.red('created',fn)
                    return
                except Exception:
                    g.error('can not create',fn)
                    g.es_exception()
    #@+node:ekr.20050424115658: *4* rf.readRecentFilesFile
    def readRecentFilesFile (self,path):

        trace = False and not g.unitTesting
        rf = self
        fileName = g.os_path_join(path,'.leoRecentFiles.txt')
        ok = g.os_path_exists(fileName)
        if ok:
            try:
                if g.isPython3:
                    f = open(fileName,encoding='utf-8',mode='r')
                else:
                    f = open(fileName,'r')
            except IOError:
                g.trace('can not open',fileName)
                return False

            if trace: g.trace(('reading %s' % fileName))
            lines = f.readlines()
            if lines and rf.sanitize(lines[0])=='readonly':
                lines = lines[1:]
            if lines:
                lines = [g.toUnicode(g.os_path_normpath(line)) for line in lines]
                rf.appendToRecentFiles(lines)

        return ok
    #@+node:ekr.20120225072226.10285: *3* rf.sanitize
    def sanitize (self,name):

        '''Return a sanitized file name.'''

        if name is None:
            return None

        name = name.lower()
        for ch in ('-','_',' ','\n'):
            name = name.replace(ch,'')

        return name or None
    #@+node:ekr.20120215072959.12478: *3* rf.setRecentFiles
    def setRecentFiles (self,files):

        '''Update the recent files list.'''

        rf = self
        rf.appendToRecentFiles(files)
    #@+node:ekr.20120225072226.10293: *3* rf.sortRecentFiles
    def sortRecentFiles(self,c):

        '''Sort the recent files list.'''

        rf = self

        aList = rf.recentFiles
        aList.sort(key=lambda s: g.os_path_basename(s).lower()) 
        aList.reverse()

        rf.recentFiles = []
        for z in aList:
            rf.updateRecentFiles(z)

        rf.writeRecentFilesFile(c,force=True)
            # Force the write message.
    #@+node:ekr.20031218072017.2083: *3* rf.updateRecentFiles
    def updateRecentFiles (self,fileName):

        """Create the RecentFiles menu.  May be called with Null fileName."""

        rf = self

        if g.app.unitTesting: return

        def munge(name):
            return g.os_path_finalize(name or '').lower()
        def munge2(name):
            return g.os_path_finalize_join(g.app.loadDir,name or '')

        # Update the recent files list in all windows.
        if fileName:
            for frame in g.app.windowList:
                # Remove all versions of the file name.
                for name in rf.recentFiles:
                    if (munge(fileName) == munge(name) or
                        munge2(fileName) == munge2(name)
                    ):
                        rf.recentFiles.remove(name)
                rf.recentFiles.insert(0,fileName)
                # Recreate the Recent Files menu.
                rf.createRecentFilesMenuItems(frame.c)
        else:
            for frame in g.app.windowList:
                rf.createRecentFilesMenuItems(frame.c)
    #@+node:ekr.20050424114937.2: *3* rf.writeRecentFilesFile & helper
    def writeRecentFilesFile (self,c,force=False):
        '''
        Write the appropriate .leoRecentFiles.txt file.

        Write a message if force is True, or if it hasn't been written yet.
        
        '''

        tag = '.leoRecentFiles.txt'
        rf = self
        if g.app.unitTesting:
            return
        localFileName = c.fileName()
        if localFileName:
            localPath,junk = g.os_path_split(localFileName)
        else:
            localPath = None
        written = False
        seen = []
        for path in (localPath,g.app.globalConfigDir,g.app.homeLeoDir):
            if path:
                fileName = g.os_path_join(path,tag)
                if g.os_path_exists(fileName) and not fileName.lower() in seen:
                    seen.append(fileName.lower())
                    ok = rf.writeRecentFilesFileHelper(fileName)
                    if force or not rf.recentFileMessageWritten:
                        if ok:
                            g.pr('wrote recent file: %s' % fileName)
                            written = True
                        else:
                            g.error('failed to write recent file: %s' % (fileName))
                    # Bug fix: Leo 4.4.6: write *all* recent files.

        if written:
            rf.recentFileMessageWritten = True
        else:
            # Attempt to create .leoRecentFiles.txt in the user's home directory.
            if g.app.homeLeoDir:
                fileName = g.os_path_finalize_join(g.app.homeLeoDir,tag)
                if not g.os_path_exists(fileName):
                    g.red('creating: %s' % (fileName))
                rf.writeRecentFilesFileHelper(fileName)
    #@+node:ekr.20050424131051: *4* rf.writeRecentFilesFileHelper
    def writeRecentFilesFileHelper (self,fileName):

        # Don't update the file if it begins with read-only.
        trace = False and not g.unitTesting
        rf = self
        theFile = None
        try:
            theFile = open(fileName)
            lines = theFile.readlines()
            if lines and rf.sanitize(lines[0])=='readonly':
                if trace: g.trace('read-only: %s' %fileName)
                return False
        except IOError:
            # The user may have erased a file.  Not an error.
            pass
        finally:
            if theFile: theFile.close()
        theFile = None
        try:
            if g.isPython3:
                theFile = open(fileName,encoding='utf-8',mode='w')
            else:
                theFile = open(fileName,mode='w')
            if rf.recentFiles:
                s = '\n'.join(rf.recentFiles)
            else:
                s = '\n'
            if not g.isPython3:
                s = g.toEncodedString(s,reportErrors=True)
            theFile.write(s)
        except IOError:
            # The user may have erased a file.  Not an error.
            g.error('error writing',fileName)
            g.es_exception()
            theFile = None
        except Exception:
            g.error('unexpected exception writing',fileName)
            g.es_exception()
            theFile = None
            if g.unitTesting: raise
        finally:
            if theFile:
                theFile.close()
        return bool(theFile)
    #@-others
#@-others
#@-leo

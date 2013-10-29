#@+leo-ver=5-thin
#@+node:ekr.20100221142603.5638: * @file ../../pylint-leo.py
#@@language python

import optparse
import os
import sys

#@+others
#@+node:ekr.20100221142603.5640: ** getCoreList
def getCoreList():

    return (
        'runLeo',
        'leoApp',
        'leoAtFile',
        'leoBridge',
        'leoCache',
        'leoChapters',
        'leoCommands',
        'leoConfig',
        'leoEditCommands',
        'leoFileCommands',
            # E1120: no value passed for param.
            # E1101: Class 'str' has no 'maketrans' member
        'leoFind',
        'leoFrame',
            # R0923: Interface not implemented.
        'leoGlobals', 
            # E0611: no name 'parse' in urllib.
            # E1103: Instance of 'ParseResult' has no 'xxx' member,
        'leoGui',
        'leoImport',
        'leoIPython',
        'leoKeys',
        'leoMenu',
            # W0108: Lambda may not be necessary (it is).
        'leoNodes',
        'leoPlugins',
        'leoRst', 
        'leoSessions',
        'leoShadow',
        'leoTangle',
        'leoTest',
        'leoUndo',
            # WO511: TODO 
    )
#@+node:ekr.20120528063627.10138: ** getGuiPluginsList
def getGuiPluginsList ():

    return (
        'baseNativeTree',
        'nested_splitter',
        'qtGui',
    )
#@+node:ekr.20100221142603.5641: ** getPassList
def getPassList():

    return (
        '__init__','FileActions',
        # 'UNL', # in plugins table.
        'active_path','add_directives','attrib_edit',
        'backlink','base64Packager','baseNativeTree','bibtex','bookmarks',
        'codewisecompleter','colorize_headlines','contextmenu',
        'ctagscompleter','cursesGui','datenodes','debugger_pudb',
        'detect_urls','dtest','empty_leo_file','enable_gc','initinclass',
        'leo_to_html','leo_interface','leo_pdf','leo_to_rtf',
        'leoOPML','leoremote','lineNumbers',
        'macros','mime','mod_autosave','mod_framesize','mod_leo2ascd',
        # 'mod_scripting', # in plugins table.
        'mod_speedups','mod_timestamp',
        'nav_buttons','nav_qt','niceNosent','nodeActions','nodebar',
        'open_shell','open_with','outline_export','quit_leo',
        'paste_as_headlines','plugins_menu','pretty_print','projectwizard',
        'qt_main','qt_quicksearch','qtframecommands',
        'quickMove','quicksearch','redirect_to_log','rClickBasePluginClasses',
        'run_nodes', # Changed thread.allocate_lock to threading.lock().acquire()
        'rst3',
        # 'scrolledmessage', # No longer exists.
        'setHomeDirectory','slideshow','spydershell','startfile',
        'testRegisterCommand','todo',
        # 'toolbar', # in plugins table.
        'trace_gc_plugin','trace_keys','trace_tags',
        'vim','xemacs',
    )
#@+node:ekr.20100221142603.5642: ** getPluginsList
def getPluginsList():

    return (
        'baseNativeTree',
        'bookmarks',
        # 'internal_ipkernel.py',
        # 'mod_http',
        'mod_scripting',
            # E0611:489:scriptingController.runDebugScriptCommand:
            # No name 'leoScriptModule' in module 'leo.core'
        'nested_splitter',
        'qtGui',
            # E1101:7584:leoQtGui.embed_ipython: Module 'IPython' has no 'ipapi' member
            # E0611: No name 'xxx' in module 'urllib'
            # W0233: __init__ method from a non direct base class 'QDateTimeEdit' is called
            # R0923: Interface not implemented
        # 'toolbar',
            # Dangerous: many erroneous E1101 errors
            # Harmless: W0221: Arguments number differs from overridden method
            # Harmless: W0511: Fixme and to-do.
        'vim.py',
        'viewrendered.py',
            # Dangerous: PyQt4.phonon has no x member.
        'xemacs.py',
    )
#@+node:ekr.20120225032124.17089: ** getRecentCoreList (pylint-leo.py)
def getRecentCoreList():

    return (
        # 'runLeo',
        # 'leoApp',
        'leoAtFile',
        # 'leoBridge',
        # 'leoCache',
        # 'leoChapters',
        # 'leoCommands',
        # 'leoConfig',
        # 'leoEditCommands',
        'leoFileCommands',
        # 'leoFind',
        # 'leoFrame',
        # 'leoGlobals',
        # 'leoGui',
        # 'leoImport',
        # 'leoIPython',
        # 'leoKeys',
        # 'leoMenu',
        # 'leoNodes',
        # 'leoPlugins',
        # 'leoRst',
        # 'leoSessions',
        'leoShadow',
        # 'leoTangle',
        # 'leoTest',
        # 'leoUndo',
)
#@+node:ekr.20120528063627.10137: ** getRecentPluginsList
def getRecentPluginsList ():

    return (
        # 'baseNativeTree',
        # 'contextmenu',
        # 'codewisecompleter',
        # 'internal_ipkernel.py',
        # 'mod_scripting',
        # 'nested_splitter',
        'qtGui',
        # 'plugins_menu',
        # 'screencast',
        # 'viewrendered',
    )
#@+node:ekr.20100221142603.5643: ** getTkPass
def getTkPass():

    return (
        # 'EditAttributes','Library',
        # 'URLloader','UniversalScrolling','UASearch',
        # 'autotrees','chapter_hoist','cleo','dump_globals',
        # 'expfolder','geotag','graphed','groupOperations',
        # 'hoist','import_cisco_config',
        # 'keybindings','leoupdate',
        # 'maximizeNewWindows', 'mnplugins','mod_labels',
        # 'mod_read_dir_outline','mod_tempfname','multifile',
        # 'newButtons','nodeActions','nodenavigator',
        # 'open_with','pie_menus','pluginsTest',
        # 'read_only_nodes','rClick',
        # 'scheduler','searchbar','searchbox','shortcut_button',
        # 'script_io_to_body',
        # 'templates','textnode','tkGui','toolbar',
        # 'xcc_nodes',
   )
#@+node:ekr.20100221142603.5644: ** run (pylint-leo.py)
# Important: I changed lint.py:Run.__init__ so pylint can handle more than one file.
# From: sys.exit(self.linter.msg_status)
# To:   print('EKR: exit status',self.linter.msg_status)

def run(theDir,fn,rpython=False):

    fn = os.path.join('leo',theDir,fn)
    rc_fn = os.path.abspath(os.path.join('leo','test','pylint-leo-rc.txt'))
    assert os.path.exists(rc_fn)
    # print('run:scope:%s' % scope)

    args = ['--rcfile=%s' % (rc_fn)]
    args.append('--disable=I0011')
        # We never want to see the I0011 message: locally disabling n.
    # if rpython: args.append('--rpython-mode') # Probably does not exist.
    fn = os.path.abspath(fn)
    if not fn.endswith('.py'): fn = fn+'.py'
    args.append(fn)

    if os.path.exists(fn):
        print('pylint-leo.py: %s' % fn)
        if True and scope == 'stc-test':
            import leo.core.leoGlobals as g
            print('pylint-leo.py: enabling Sherlock traces')
            sherlock = g.SherlockTracer(show_return=True,verbose=True, # verbose: show filenames.
                patterns=[ 
                #@+<< Sherlock patterns for pylint >>
                #@+node:ekr.20130111060235.10182: *3* << Sherlock patterns for pylint >>
                # Enable everything.
                '+.*',

                # Disable entire files.
                # '-:.*\\lib\\.*', # Disables everything.

                # Pylint files.
                #'-:.*base.py',
                #'-:.*bases.py',
                '-:.*builder.py',
                '-:.*__init__.py',
                '-:.*format.py',
                '-:.*interface.py', # implements
                '-:.*rebuilder.py',
                #'-:.*scoped_nodes',
                # General library files.
                '-:.*leoGlobals.py',
                '-:.*codecs.py',
                '-:.*config.py',
                '-:.*configuration.py',
                '-:.*ConfigParser.py',
                '-:.*copy\.py',
                '-:.*gettext.py',
                '-:.*genericpath.py',
                '-:.*graph.py',
                '-:.*locale.py',
                '-:.*optik_ext.py',
                '-:.*optparse.py',
                '-:.*os.py',
                '-:.*ntpath.py',
                '-:.*pickle.py',
                '-:.*re.py',
                '-:.*similar.py',
                '-:.*shlex.py',
                '-:.*sre_compile.py',
                '-:.*sre_parse.py',
                '-:.*string_escape.py',
                '-:.*text.py',
                '-:.*threading.py',
                '-:.*tokenize.py',
                '-:.*utils.py',

                # Enable entire files.
                # '+:.*base.py',
                # '+:.*bases.py',
                # '+:.*classes.py',
                # '+:.*design_analysis.py',
                # '+:.*format.py',
                # '+:.*inference.py',
                # '+:.*logging.py',
                # '+:.*mixins.py',
                # '+:.*newstyle.py',
                # '+:.*node_classes.py',
                # '+:.*protocols.py',
                # '+:.*scoped_nodes.py',
                # '+:.*typecheck.py',
                # '+:.*variables.py',

                # Disable individual methods.
                '-close', # __init__.py
                '-collect_block_lines', '-\<genexpr\>','-.*option.*','-.*register_checker','-set_reporter', # lint.py
                '-frame','-root','-scope', # scoped_nodes
                '-register', # various files.

                # '-abspath','-normpath','-isstring','-normalize',
                # '-splitext','-_splitext','-splitdrive','-splitstrip',
                # '-.*option.*','-get','-set_option',
                # '-unquote','-convert','-interpolate','-_call_validator', # compile stuff.
                # '-_compile.*','-compile_.*','-_code','-identifyfunction', # compile stuff.
                # '-_parse.*','-set_parser','-set_conflict_handler',
                # '-append','-match',
                # '-isbasestring',
                # '-save.*','-memoize','-put',

                # '-persistent_id',
                # '-__next',
                # '-nodes_of_class',
                # '-__.*',
                # '-_check.*',
                # '-_.*',
                # '-load_.*',
                #@-<< Sherlock patterns for pylint >>
                #@afterref
 ])
            sherlock.run()
            lint.Run(args)
            sherlock.stop()
        else:
            lint.Run(args)
    else:
        print('file not found:',fn)
#@+node:ekr.20120307142211.9886: ** scanOptions
def scanOptions():

    '''Handle all options, remove them from sys.argv.'''
    
    global g_option_fn

    # This automatically implements the -h (--help) option.
    parser = optparse.OptionParser()
    add = parser.add_option
    add('-a', action='store_true', help = 'all')
    add('-c', action='store_true', help = 'core')
    add('-e', action='store_true', help = 'external')
    add('-f', dest='filename',     help = 'filename',)
    add('-g', action='store_true', help = 'gui plugins')
    add('-p', action='store_true', help = 'plugins')
    add('-r', action='store_true', help = 'recent')
    #add('-s', action='store_true', help = 'suppressions')
    add('-t', action='store_true', help = 'static type checking')
    add('--tt',action='store_true', help = 'stc test')

    # Parse the options.
    options,args = parser.parse_args()
    if   options.a: return 'all'
    elif options.c: return 'core'
    elif options.e: return 'external'
    elif options.filename:
        fn = options.filename
        if fn.startswith('='): fn = fn[1:]
        g_option_fn = fn.strip('"')
        return 'file'
    elif options.g: return 'gui'
    elif options.p: return 'plugins'
    elif options.r: return 'recent'
    # elif options.s: return 'suppressions'
    elif options.t: return 'stc'
    elif options.tt:return 'stc-test'
    else:           return 'all'
#@-others

g_option_fn = None
scope = scanOptions()
coreList            = getCoreList()
externalList        = ('lproto',) # 'ipy_leo',
guiPluginsList      = getGuiPluginsList()
passList            = getPassList()
pluginsList         = getPluginsList()
recentCoreList      = getRecentCoreList()
recentPluginsList   = getRecentPluginsList()
tkPass              = getTkPass()
if scope == 'all':
    tables_table = (
        (coreList,'core'),
        # (guiPluginsList,'plugins'),
        (pluginsList,'plugins'),
        (externalList,'external'),
    )
elif scope == 'core':
    tables_table =  (
        (coreList,'core'),
        (guiPluginsList,'plugins'),
        (externalList,'external'),
    )
elif scope == 'external':
    tables_table = (
        (externalList,'external'),
    )
elif scope == 'file':
    tables_table = (
        ([g_option_fn],'core'), # Default is a core file.
    )
elif scope == 'gui':
    tables_table = (
        (guiPluginsList,'plugins'),
)
elif scope == 'plugins':
    tables_table = (
        (pluginsList,'plugins'),
        # (passList,'plugins'),
    )
elif scope == 'recent':
    tables_table = (
        (recentCoreList,'core'),
        (recentPluginsList,'plugins'),
    )
elif scope == 'stc':
    tables_table = (
        (['statictypechecking',],r'c:\leo.repo\static-type-checking'),
    )
elif scope == 'stc-test':
    tables_table = (
        (['pylint_test.py',],r'c:\leo.repo\static-type-checking\test\pylint'),
    )
else:
    print('bad scope',scope)
    tables_table = ()

if tables_table and sys.platform.startswith('win'):
    if scope != 'file':
        os.system('cls')

from pylint import lint
    # Use the version of pylint in python26/Lib/site-packages.
    # Do the import *after* clearing the console.

# print(lint)

for table,theDir in tables_table:
    for fn in table:
        run(theDir,fn)
#@-leo

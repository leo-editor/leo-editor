#@+leo-ver=5-thin
#@+node:ekr.20100221142603.5638: * @file ../../pylint-leo.py
'''
This file runs pylint on predefined lists of files.

The -r option no longer exists. Instead, use Leo's pylint command to run
pylint on all Python @<file> nodes in a given tree.

On windows, the following .bat file runs this file::
    python27 pylint-leo.py %*

On Ubuntu, the following alias runs this file::
    pylint="python27 pylint-leo.py"
'''
#@@language python
# pylint: disable=invalid-name
    # pylint-leo isn't a valid module name, but it isn't a module.
import leo.core.leoGlobals as g
import glob
import optparse
import os
import sys
import time
#@+others
#@+node:ekr.20100221142603.5640: ** getCoreList
def getCoreList():
    
    pattern = g.os_path_finalize_join('.','leo','core','leo*.py')
    aList = [
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py']
    aList.extend([
         'runLeo.py',
    ])
    return sorted(aList)
#@+node:ekr.20140528065727.17960: ** getExternalList
def getExternalList():
    '''Return list of files in leo/external'''
    return [
        # 'ipy_leo',
        'leosax',
        'lproto',
    ]
#@+node:ekr.20120528063627.10138: ** getGuiPluginsList
def getGuiPluginsList ():
    
    pattern = g.os_path_finalize_join('.','leo','plugins','qt_*.py')
    aList = [
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py']
    aList.extend([
        'free_layout',
        'nested_splitter',
    ])
    if 'qt_main.py' in aList:
        # Auto-generated file.
        aList.remove('qt_main.py')
    return sorted(aList)
#@+node:ekr.20140727180847.17983: ** getModesList
def getModesList():
    pattern = g.os_path_finalize_join('.','leo','modes','*.py')
    return [
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py']
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
        'qt_main','qt_quicksearch','qt_commands',
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
    '''Return a list of all important plugins.'''
    aList = []
    # g.app.loadDir does not exist: use '.' instead.
    for theDir in ('','importers','writers'):
        pattern = g.os_path_finalize_join('.','leo','plugins',theDir,'*.py')
        for fn in glob.glob(pattern):
            sfn = g.shortFileName(fn)
            if sfn != '__init__.py':
                sfn = os.sep.join([theDir,sfn]) if theDir else sfn
                aList.append(sfn)
    remove = [
        'free_layout.py',       # Gui-related.
        'gtkDialogs.py',        # Many errors, not important.
        'leofts.py',            # Not (yet) in leoPlugins.leo.
        'nested_splitter.py',   # Gui-related.
        'qtGui.py',             # Dummy file
        'qt_main.py',           # Created automatically.
    ]
    aList = sorted([z for z in aList if z not in remove])
    # Remove all gui related items.
    for z in sorted(aList):
        if z.startswith('qt_'):
            aList.remove(z)
    # g.trace('\n'.join(aList))
    return aList
#@+node:ekr.20140331201252.16861: ** getTable
def getTable(scope):
    
    d = {
        'all': (
            (coreList,'core'),
            (guiPluginsList,'plugins'),
            (pluginsList,'plugins'),
            (externalList,'external'),
        ),
        'core': (
            (coreList,'core'),
            (guiPluginsList,'plugins'),
            (externalList,'external'),
        ),
        'external': (
            (externalList,'external'),
        ),
        'file': (
            ([g_option_fn],''), # Default directory is the leo directory (was leo/core)
        ),
        'gui': (
            (guiPluginsList,'plugins'),
        ),
        'modes': (
            (modesList,'modes'),
        ),
        'plugins': (
            (pluginsList,'plugins'),
            # (passList,'plugins'),
        ),
    }
    tables_table = d.get(scope)
    if not tables_table:
        print('bad scope',scope)
        tables_table = ()
    return tables_table
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
#@+node:ekr.20140331201252.16859: ** main
def main(tables_table):
    
    if tables_table and sys.platform.startswith('win'):
        if False and scope != 'file':
            g.cls()
    # Do these imports **after** clearing the screen.
    from pylint import lint
        # in pythonN/Lib/site-packages.
    t = 0.0
    for table,theDir in tables_table:
        for fn in table:
            t += run(theDir,fn)
    print('time: %5.2f sec.' % t)
#@+node:ekr.20140526142452.17594: ** report_version
def report_version():
    try:
        from pylint import lint
        rc_fn = os.path.abspath(os.path.join('leo','test','pylint-leo-rc.txt'))
        rc_fn = rc_fn.replace('\\','/')
        lint.Run(["--rcfile=%s" % (rc_fn),'--version',])
    except ImportError:
        g.trace('can not import pylint')
#@+node:ekr.20100221142603.5644: ** run (pylint-leo.py)
def run(theDir,fn,rpython=False):
    '''Run pylint on fn.'''
    fn = os.path.join('leo',theDir,fn)
    rc_fn = os.path.abspath(os.path.join('leo','test','pylint-leo-rc.txt'))
    # print('run:scope:%s' % scope)
    fn = os.path.abspath(fn)
    if not fn.endswith('.py'): fn = fn+'.py'
    if not os.path.exists(rc_fn):
        print('pylint rc file not found: %s' % (rc_fn))
        return
    if not os.path.exists(fn):
        print('file not found: %s' % (fn))
        return
    # Report the file name and one level of directory.
    path = g.os_path_dirname(fn)
    dirs = path.split(os.sep)
    theDir = dirs and dirs[-1] or ''
    print('pylint-leo.py: %s%s%s' % (theDir,os.sep,g.shortFileName(fn)))
    # Create the required args.
    args = ','.join([
        "fn=r'%s'" % (fn),
        "rc=r'%s'" % (rc_fn),
    ])
    if scope == 'stc-test': # The --tt option.
        # Report that Sherlock is enabled.
        print('pylint-leo.py --tt: enabling Sherlock traces')
        print('pylint-leo.py --tt: patterns contained in plyint-leo.py')
        # Report the source code.
        s = open(fn).read()
        print('pylint-leo.py: source:\n\n%s\n' % s)
        # Add the optional Sherlock args.
        dots = True
        patterns=[ 
        #@+<< Sherlock patterns for pylint >>
        #@+node:ekr.20130111060235.10182: *3* << Sherlock patterns for pylint >>
        # Note:  A leading * is never valid: change to .*

        '+.*infer*',
            # '+.*infer_name',
            '+.*infer_stmts',
            
        '+YES::__init__',

        ###'+TypeChecker::add_message',
            # '+.*add_message',
            # '+PyLinter::add_message',
            # '+TextReporter::add_message'

        # '+.*visit*',
            # '+TypeChecker::visit_getattr',
            # '+.*visit_class',
            # '+Basic*::visit_*',
            
        # '+.*__init__',
            # '+Instance::__init__',
            # '+Class::__init__',
            # '+Module::__init__',
            # '+Function::__init__',

        ###'+:.*typecheck.py',
        ###'+:.*inference.py',
        ###'+:.*variables.py',

        ###### Old traces

        # '+:.*bases.py',
        # '+.*path_raise_wrapper',

        # Enable everything.
        # # '+.*',

        # # Disable entire files.
        # # '-:.*\\lib\\.*', # Disables everything.

        # # Pylint files.
        # #'-:.*base.py',
        # #'-:.*bases.py',
        # '-:.*builder.py',
        # '-:.*__init__.py',
        # '-:.*format.py',
        # '-:.*interface.py', # implements
        # '-:.*rebuilder.py',
        # #'-:.*scoped_nodes',
        # # General library files.
        # '-:.*leoGlobals.py',
        # '-:.*codecs.py',
        # '-:.*config.py',
        # '-:.*configuration.py',
        # '-:.*ConfigParser.py',
        # '-:.*copy\.py',
        # '-:.*gettext.py',
        # '-:.*genericpath.py',
        # '-:.*graph.py',
        # '-:.*locale.py',
        # '-:.*optik_ext.py',
        # '-:.*optparse.py',
        # '-:.*os.py',
        # '-:.*ntpath.py',
        # '-:.*pickle.py',
        # '-:.*re.py',
        # '-:.*similar.py',
        # '-:.*shlex.py',
        # '-:.*sre_compile.py',
        # '-:.*sre_parse.py',
        # '-:.*string_escape.py',
        # '-:.*text.py',
        # '-:.*threading.py',
        # '-:.*tokenize.py',
        # '-:.*utils.py',

        # # Enable entire files.
        # # '+:.*base.py',
        # # '+:.*bases.py',
        # # '+:.*classes.py',
        # # '+:.*design_analysis.py',
        # # '+:.*format.py',
        # # '+:.*inference.py',
        # # '+:.*logging.py',
        # # '+:.*mixins.py',
        # # '+:.*newstyle.py',
        # # '+:.*node_classes.py',
        # # '+:.*protocols.py',
        # # '+:.*scoped_nodes.py',
        # # '+:.*typecheck.py',
        # # '+:.*variables.py',

        # # Disable individual methods.
        # '-close', # __init__.py
        # '-collect_block_lines', '-\<genexpr\>','-.*option.*','-.*register_checker','-set_reporter', # lint.py
        # '-frame','-root','-scope', # scoped_nodes
        # '-register', # various files.

        # # '-abspath','-normpath','-isstring','-normalize',
        # # '-splitext','-_splitext','-splitdrive','-splitstrip',
        # # '-.*option.*','-get','-set_option',
        # # '-unquote','-convert','-interpolate','-_call_validator', # compile stuff.
        # # '-_compile.*','-compile_.*','-_code','-identifyfunction', # compile stuff.
        # # '-_parse.*','-set_parser','-set_conflict_handler',
        # # '-append','-match',
        # # '-isbasestring',
        # # '-save.*','-memoize','-put',

        # # '-persistent_id',
        # # '-__next',
        # # '-nodes_of_class',
        # # '-__.*',
        # # '-_check.*',
        # # '-_.*',
        # # '-load_.*',
        #@-<< Sherlock patterns for pylint >>
        #@afterref
 ]
        show_return = True
        stats_patterns = [ 
        #@+<< Sherlock stats patterns for pylint >>
        #@+node:ekr.20140327164521.16846: *3* << Sherlock stats patterns for pylint >>
        # '+.*__init__',
            # astroid.bases.py
            '+BoundMethod::__init__',
            '+InferenceContext::__init__',
            '+Instance::__init__',
            '+UnboundMethod::__init__',
            # astroid.node_classes.py
            '+Arguments::__init__',
            '+CallFunc::__init__',
            '+Const::__init__',
            # astroid.scoped_nods.py
            '+Class::__init__',
            '+Function::__init__',
            '+Module::__init__',
        #@-<< Sherlock stats patterns for pylint >>
        #@afterref
 ]
        verbose = True
        args = args + ',' + ','.join([
            'dots=%s' % (dots),
            'patterns=%s' % (patterns),
            'sherlock=True',
            'show_return=%s' % (show_return),
            'stats_patterns=%s' % (stats_patterns),
            'verbose=%s' % (verbose),
        ])
    # Execute the command in a separate process.
    command = '%s -c "import leo.core.leoGlobals as g; g.run_pylint(%s)"' % (
        sys.executable,args)
    t1 = time.clock()
    g.execute_shell_commands(command)
    t2 = time.clock()
    return t2-t1 
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
    add('-f', dest='filename',     help = 'filename, relative to leo folder')
    add('-g', action='store_true', help = 'gui plugins')
    add('-m', action='store_true', help = 'modes')
    add('-p', action='store_true', help = 'plugins')
    # add('-r', action='store_true', help = 'recent')
    # add('-s', action='store_true', help = 'suppressions')
    # add('-t', action='store_true', help = 'stc')
    # add('--tt',action='store_true', help = 'stc test')
    add('-v',action='store_true',  help = 'report pylint version')

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
    elif options.m: return 'modes'
    elif options.p: return 'plugins'
    # elif options.r: return 'recent'
    # elif options.s: return 'suppressions'
    # elif options.t: return 'stc'
    # elif options.tt:return 'stc-test'
    elif options.v: return 'version'
    else:           return 'all'
#@-others
g_option_fn = None
scope = scanOptions()
coreList            = getCoreList()
externalList        = getExternalList()
guiPluginsList      = getGuiPluginsList()
modesList           = getModesList()
passList            = getPassList()
pluginsList         = getPluginsList()
tkPass              = getTkPass()
if scope == 'version':
    report_version()
else:
    tables_table = getTable(scope)
    main(tables_table)
#@-leo

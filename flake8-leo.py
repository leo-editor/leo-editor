#@+leo-ver=5-thin
#@+node:ekr.20160517182239.1: * @file ../../flake8-leo.py
'''
This file runs flake8 on predefined lists of files.

On windows, the following .bat file runs this file::
    python flake8-leo.py %*

On Ubuntu, the following alias runs this file::
    pyflake="python pyflake-leo.py"
'''
#@@language python
# pylint: disable=invalid-name
    # flake8-leo isn't a valid module name, but it isn't a module.
import leo.core.leoGlobals as g
import flake8
import glob
import optparse
import os
import sys
import time
#@+others
#@+node:ekr.20160517182239.2: ** getCommandList
def getCommandList():
    '''Return list of all command modules in leo/commands.'''
    pattern = g.os_path_finalize_join('.', 'leo', 'commands', '*.py')
    return sorted([
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py'])
#@+node:ekr.20160517182239.3: ** getCoreList
def getCoreList():
    pattern = g.os_path_finalize_join('.', 'leo', 'core', 'leo*.py')
    # pattern = g.os_path_finalize_join('leo','core','leo*.py')
    aList = [
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py']
    aList.extend([
         'runLeo.py',
    ])
    return sorted(aList)
#@+node:ekr.20160517182239.4: ** getExternalList
def getExternalList():
    '''Return list of files in leo/external'''
    return [
        # 'ipy_leo',
        'leosax',
        'lproto',
    ]
#@+node:ekr.20160517182239.5: ** getGuiPluginsList
def getGuiPluginsList():
    pattern = g.os_path_finalize_join('.', 'leo', 'plugins', 'qt_*.py')
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
#@+node:ekr.20160517182239.6: ** getModesList
def getModesList():
    pattern = g.os_path_finalize_join('.', 'leo', 'modes', '*.py')
    return [
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py']
#@+node:ekr.20160517182239.7: ** getPassList
def getPassList():
    return (
        '__init__', 'FileActions',
        # 'UNL', # in plugins table.
        'active_path', 'add_directives', 'attrib_edit',
        'backlink', 'base64Packager', 'baseNativeTree', 'bibtex', 'bookmarks',
        'codewisecompleter', 'colorize_headlines', 'contextmenu',
        'ctagscompleter', 'cursesGui', 'datenodes', 'debugger_pudb',
        'detect_urls', 'dtest', 'empty_leo_file', 'enable_gc', 'initinclass',
        'leo_to_html', 'leo_interface', 'leo_pdf', 'leo_to_rtf',
        'leoOPML', 'leoremote', 'lineNumbers',
        'macros', 'mime', 'mod_autosave', 'mod_framesize', 'mod_leo2ascd',
        # 'mod_scripting', # in plugins table.
        'mod_speedups', 'mod_timestamp',
        'nav_buttons', 'nav_qt', 'niceNosent', 'nodeActions', 'nodebar',
        'open_shell', 'open_with', 'outline_export', 'quit_leo',
        'paste_as_headlines', 'plugins_menu', 'pretty_print', 'projectwizard',
        'qt_main', 'qt_quicksearch', 'qt_commands',
        'quickMove', 'quicksearch', 'redirect_to_log', 'rClickBasePluginClasses',
        'run_nodes', # Changed thread.allocate_lock to threading.lock().acquire()
        'rst3',
        # 'scrolledmessage', # No longer exists.
        'setHomeDirectory', 'slideshow', 'spydershell', 'startfile',
        'testRegisterCommand', 'todo',
        # 'toolbar', # in plugins table.
        'trace_gc_plugin', 'trace_keys', 'trace_tags',
        'vim', 'xemacs',
    )
#@+node:ekr.20160517182239.8: ** getPluginsList
def getPluginsList():
    '''Return a list of all important plugins.'''
    aList = []
    # g.app.loadDir does not exist: use '.' instead.
    for theDir in ('', 'importers', 'writers'):
        pattern = g.os_path_finalize_join('.', 'leo', 'plugins', theDir, '*.py')
        for fn in glob.glob(pattern):
            sfn = g.shortFileName(fn)
            if sfn != '__init__.py':
                sfn = os.sep.join([theDir, sfn]) if theDir else sfn
                aList.append(sfn)
    remove = [
        'free_layout.py', # Gui-related.
        'gtkDialogs.py', # Many errors, not important.
        'leofts.py', # Not (yet) in leoPlugins.leo.
        'nested_splitter.py', # Gui-related.
        'qtGui.py', # Dummy file
        'qt_main.py', # Created automatically.
    ]
    aList = sorted([z for z in aList if z not in remove])
    # Remove all gui related items.
    for z in sorted(aList):
        if z.startswith('qt_'):
            aList.remove(z)
    # g.trace('\n'.join(aList))
    return aList
#@+node:ekr.20160517182239.9: ** getTable
def getTable(scope):
    d = {
        'all': (
            (coreList, 'core'),
            (commandList, 'commands'),
            (guiPluginsList, 'plugins'),
            (pluginsList, 'plugins'),
            (externalList, 'external'),
        ),
        'commands': (
            (commandList, 'commands'),
        ),
        'core': (
            (coreList, 'core'),
            (commandList, 'commands'),
            (guiPluginsList, 'plugins'),
            (externalList, 'external'),
        ),
        'external': (
            (externalList, 'external'),
        ),
        'file': (
            ([g_option_fn], ''),
                # Default directory is the leo directory (was leo/core)
        ),
        'gui': (
            (guiPluginsList, 'plugins'),
        ),
        'modes': (
            (modesList, 'modes'),
        ),
        'plugins': (
            (pluginsList, 'plugins'),
            # (passList,'plugins'),
        ),
    }
    tables_table = d.get(scope)
    if not tables_table:
        print('bad scope', scope)
        tables_table = ()
    return tables_table
#@+node:ekr.20160517182239.10: ** main & helpers
def main(tables_table, silent):
    '''Call run on all tables in tables_table.'''
    from flake8 import engine
    style = engine.get_style_guide(
        parse_argv=False,
        config_file=get_flake8_config(),
    )
    if style:
        t1 = time.clock()
        n = 0
        for table, dir_ in tables_table:
            n += len(table)
            check_all(dir_, table, style)
        t2 = time.clock()
        print('%s file%s, time: %5.2f sec.' % (n, g.plural(n), t2-t1))
#@+node:ekr.20160517222900.1: *3* get_home
def get_home():
    """Returns the user's home directory."""
    home = g.os_path_expanduser("~")
        # Windows searches the HOME, HOMEPATH and HOMEDRIVE
        # environment vars, then gives up.
    if home and len(home) > 1 and home[0] == '%' and home[-1] == '%':
        # Get the indirect reference to the true home.
        home = os.getenv(home[1: -1], default=None)
    if home:
        # Important: This returns the _working_ directory if home is None!
        # This was the source of the 4.3 .leoID.txt problems.
        home = g.os_path_finalize(home)
        if (
            not g.os_path_exists(home) or
            not g.os_path_isdir(home)
        ):
            home = None
    return home
#@+node:ekr.20160517222236.1: *3* get_flake8_config
def get_flake8_config():
    '''Return the path to the flake8 configuration file.'''
    join = g.os_path_finalize_join
    homeDir = get_home()
    loadDir = g.os_path_finalize_join(g.__file__, '..', '..')
    # g.trace('home', homeDir, 'loadDir', loadDir)
    table = (
        homeDir,
        join(homeDir, '.leo'),
        join(loadDir, '..', '..', 'leo', 'test'),
    )
    for base in ('flake8', 'flake8.txt'):
        for path in table:
            fn = g.os_path_abspath(join(path, base))
            if g.os_path_exists(fn):
                # g.trace('found:', fn)
                return fn
    print('no flake8 configuration file found in\n%s' % (
        '\n'.join(table)))
    return None
#@+node:ekr.20160517222332.1: *3* check_all
def check_all(dir_, files, style):
    '''Run flake8 on all paths.'''
    from flake8 import main
    loadDir = g.os_path_finalize_join(g.__file__, '..', '..')
    paths = []
    for fn in files:
        if dir_:
            fn = g.os_path_join(loadDir, dir_, fn)
        else:
            fn = g.os_path_join(loadDir, fn)
        fn = g.os_path_abspath(fn)
        if not fn.endswith('.py'):
            fn = fn+'.py'
        paths.append(fn)
    report = style.check_files(paths=paths)
    # Set statistics here, instead of from the command line.
    options = style.options
    options.statistics = True
    options.total_errors = True
    # options.benchmark = True
    main.print_report(report, style)
#@+node:ekr.20160517182239.11: ** report_version
def report_version():
    try:
        import flake8
        print('flake8 version: %s' % flake8.__version__)
    except ImportError:
        g.trace('can not import flake8')
#@+node:ekr.20160517182239.15: ** scanOptions
def scanOptions():
    '''Handle all options, remove them from sys.argv.'''
    global g_option_fn
    # This automatically implements the -h (--help) option.
    parser = optparse.OptionParser()
    add = parser.add_option
    add('-a', action='store_true', help='all')
    add('-c', action='store_true', help='core')
    add('-e', action='store_true', help='external')
    add('-f', dest='filename', help='filename, relative to leo folder')
    add('-g', action='store_true', help='gui plugins')
    add('-m', action='store_true', help='modes')
    add('-p', action='store_true', help='plugins')
    add('-s', action='store_true', help='silent')
    add('-u', action='store_true', help='user commands')
    add('-v', '--version', dest='v',
        action='store_true', help='report flake8 version')
    # Parse the options.
    options, args = parser.parse_args()
    silent = options.s
    if options.a: scope = 'all'
    elif options.c: scope = 'core'
    elif options.e: scope = 'external'
    elif options.filename:
        fn = options.filename
        if fn.startswith('='): fn = fn[1:]
        g_option_fn = fn.strip('"')
        scope = 'file'
    elif options.g: scope = 'gui'
    elif options.m: scope = 'modes'
    elif options.p: scope = 'plugins'
    elif options.s: scope = 'silent'
    elif options.u: scope = 'commands'
    elif options.v: scope = 'version'
    else: scope = 'all'
    return scope, silent
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@@nobeautify
g_option_fn     = None
scope, silent   = scanOptions()
commandList     = getCommandList()
coreList        = getCoreList()
externalList    = getExternalList()
guiPluginsList  = getGuiPluginsList()
modesList       = getModesList()
passList        = getPassList()
pluginsList     = getPluginsList()
if scope == 'version':
    report_version()
else:
    tables_table = getTable(scope)
    main(tables_table, silent)
#@@beautify
#@-leo

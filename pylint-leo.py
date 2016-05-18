#@+leo-ver=5-thin
#@+node:ekr.20100221142603.5638: * @file ../../pylint-leo.py
'''
This file runs pylint on predefined lists of files.

The -r option no longer exists. Instead, use Leo's pylint command to run
pylint on all Python @<file> nodes in a given tree.

On windows, the following .bat file runs this file::
    python2 pylint-leo.py %*

On Ubuntu, the following alias runs this file::
    pylint="python2 pylint-leo.py"
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
#@+node:ekr.20150514101801.1: ** getCommandList
def getCommandList():
    '''Return list of all command modules in leo/commands.'''
    pattern = g.os_path_finalize_join('.', 'leo', 'commands', '*.py')
    return sorted([
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py'])
#@+node:ekr.20100221142603.5640: ** getCoreList
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
#@+node:ekr.20140528065727.17960: ** getExternalList
def getExternalList():
    '''Return list of files in leo/external'''
    return [
        # 'ipy_leo',
        'leosax',
        'lproto',
    ]
#@+node:ekr.20120528063627.10138: ** getGuiPluginsList
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
#@+node:ekr.20140727180847.17983: ** getModesList
def getModesList():
    pattern = g.os_path_finalize_join('.', 'leo', 'modes', '*.py')
    return [
        g.shortFileName(fn)
            for fn in glob.glob(pattern)
                if g.shortFileName(fn) != '__init__.py']
#@+node:ekr.20100221142603.5641: ** getPassList
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
#@+node:ekr.20100221142603.5642: ** getPluginsList
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
#@+node:ekr.20140331201252.16861: ** getTable
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
#@+node:ekr.20140331201252.16859: ** main & helpers
def main(tables_table, silent):
    '''Call run on all tables in tables_table.'''
    try:
        from pylint import lint
        assert lint
    except ImportError:
        print('pylint-leo.py: can not import pylint')
        return
    t1 = time.clock()
    n = 0
    for table, theDir in tables_table:
        for fn in table:
            n += 1
            run(theDir, fn, silent)
    t2 = time.clock()
    print('%s file%s, time: %5.2f sec.' % (n, g.plural(n), t2-t1))
#@+node:ekr.20100221142603.5644: *3* run (pylint-leo.py)
#@@nobeautify

def run(theDir,fn,silent,rpython=False):
    '''Run pylint on fn.'''
    trace = False and not g.unitTesting
    # theDir is empty for the -f option.
    from pylint import lint
    assert lint
    if theDir:
        fn = os.path.join('leo',theDir,fn)
    rc_fn = os.path.abspath(os.path.join('leo','test','pylint-leo-rc.txt'))
    fn = os.path.abspath(fn)
    if not fn.endswith('.py'):
        fn = fn+'.py'
    if not os.path.exists(rc_fn):
        print('pylint rc file not found: %s' % (rc_fn))
        return 0.0
    if not os.path.exists(fn):
        print('file not found: %s' % (fn))
        return
    # Report the file name and one level of directory.
    path = g.os_path_dirname(fn)
    dirs = path.split(os.sep)
    theDir = dirs and dirs[-1] or ''
    if not silent:
        print('pylint-leo.py: %s%s%s' % (theDir,os.sep,g.shortFileName(fn)))
    
    # Call pylint in a subprocess so Pylint doesn't abort *this* process.
    args = ','.join([
        "fn=r'%s'" % (fn),
        "rc=r'%s'" % (rc_fn),
    ])
    if 0: # Prints error number.
        args.append('--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}')
    command = '%s -c "import leo.core.leoGlobals as g; g.run_pylint(%s)"' % (
        sys.executable, args)
    t1 = time.clock()
    g.execute_shell_commands(command)
    t2 = time.clock()
    if trace:
        g.trace('%4.2f %s' % (t2-t1, g.shortFileName(fn)))
#@+node:ekr.20140526142452.17594: ** report_version
def report_version():
    try:
        from pylint import lint
        rc_fn = os.path.abspath(os.path.join('leo', 'test', 'pylint-leo-rc.txt'))
        rc_fn = rc_fn.replace('\\', '/')
        lint.Run(["--rcfile=%s" % (rc_fn), '--version',])
    except ImportError:
        g.trace('can not import pylint')
#@+node:ekr.20120307142211.9886: ** scanOptions
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
    add('-v', action='store_true', help='report pylint version')
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
    # elif options.r: scope = 'recent'
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

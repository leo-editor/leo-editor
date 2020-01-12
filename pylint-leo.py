#@+leo-ver=5-thin
#@+node:ekr.20100221142603.5638: * @file ../../pylint-leo.py
"""
This file runs pylint on predefined lists of files.

The -r option no longer exists. Instead, use Leo's pylint command to run
pylint on all Python @<file> nodes in a given tree.

On windows, the following .bat file runs this file::
    python2 pylint-leo.py %*

On Ubuntu, the following alias runs this file::
    pylint="python2 pylint-leo.py"
"""
#@@language python
# pylint: disable=invalid-name
    # pylint-leo isn't a valid module name, but it isn't a module.
from __future__ import print_function
import leo.core.leoGlobals as g
import leo.core.leoTest as leoTest
import shlex
import optparse
import os
import subprocess
import sys
import time
#@+others
#@+node:ekr.20140331201252.16859: ** main (pylint-leo.py)
def main(files, verbose):
    """Call run on all tables in tables_table."""
    n = len(files)
    print('pylint: %s file%s' % (n, g.plural(n)))
    try:
        from pylint import lint
        assert lint
    except ImportError:
        print('pylint-leo.py: can not import pylint')
        return
    t1 = time.time()
    for fn in files:
        run(fn, verbose)
        if not verbose and sys.platform.startswith('win'):
            print('.',sep='', end='')
    t2 = time.time()
    print('%s file%s, time: %5.2f sec.' % (n, g.plural(n), t2-t1))
#@+node:ekr.20100221142603.5644: ** run (pylint-leo.py)
#@@nobeautify

def run(fn, verbose):
    """Run pylint on fn."""
    # theDir is empty for the -f option.
    from pylint import lint
    assert lint
    # Note: g.app does not exist.
    base_dir = os.path.dirname(__file__)
    home_dir = os.path.expanduser('~')
    rc_fn = 'pylint-leo-rc.txt'
    table = (
        os.path.abspath(os.path.join(home_dir, '.leo', rc_fn)),
        os.path.abspath(os.path.join(base_dir, 'leo', 'test', rc_fn)),
    )
    for rc_fn in table:
        if os.path.exists(rc_fn):
            break
    else:
        print('pylint-leo.py: %s not found in leo/test or ~/.leo.' % (rc_fn))
        return
    if not os.path.exists(fn):
        print('pylint-leo.py: file not found: %s' % (fn))
        return
    if verbose:
        path = g.os_path_dirname(fn)
        dirs = path.split(os.sep)
        theDir = dirs and dirs[-1] or ''
        print('pylint-leo.py: %s%s%s' % (theDir,os.sep,g.shortFileName(fn)))
    # Call pylint in a subprocess so Pylint doesn't abort *this* process.
    if 1: # Invoke pylint directly.
        # Escaping args is harder here because we are creating an args array.
        is_win = sys.platform.startswith('win')
        args =  ','.join(["'--rcfile=%s'" % (rc_fn), "'%s'" % (fn)])
        if is_win:
            args = args.replace('\\','\\\\')
        command = '%s -c "from pylint import lint; args=[%s]; lint.Run(args)"' % (
            sys.executable, args)
        if not is_win:
            command = shlex.split(command)
    else:
        # Use g.run_pylint.
        args = ','.join(["fn=r'%s'" % (fn), "rc=r'%s'" % (rc_fn)])
        command = '%s -c "import leo.core.leoGlobals as g; g.run_pylint(%s)"' % (
            sys.executable, args)
    # If shell is True, it is recommended to pass args as a string rather than as a sequence.
    proc = subprocess.Popen(command, shell=False)
    proc.communicate()
        # Wait: Not waiting is confusing for the user.
#@+node:ekr.20140526142452.17594: ** report_version (pylint-leo.py)
def report_version():
    try:
        from pylint import lint
    except ImportError:
        g.trace('can not import pylint')
    table = (
        os.path.abspath(os.path.expanduser('~/.leo/pylint-leo-rc.txt')),
        os.path.abspath(os.path.join('leo', 'test', 'pylint-leo-rc.txt')),
    )
    for rc_fn in table:
        try:
            rc_fn = rc_fn.replace('\\', '/')
            lint.Run(["--rcfile=%s" % (rc_fn), '--version',])
        except OSError:
            pass
    g.trace('no rc file found in')
    g.printList(table)

#@+node:ekr.20120307142211.9886: ** scanOptions (pylint-leo.py)
def scanOptions():
    """Handle all options, remove them from sys.argv."""
    global g_option_fn
    # This automatically implements the -h (--help) option.
    parser = optparse.OptionParser()
    add = parser.add_option
    add('-a', action='store_true',  help='all')
    add('-c', action='store_true',  help='core')
    add('-e', action='store_true',  help='external')
    add('-f', dest='filename',      help='filename, relative to leo folder')
    add('-g', action='store_true',  help='gui plugins')
    add('-m', action='store_true',  help='modes')
    add('-p', action='store_true',  help='plugins')
    add('-u', action='store_true',  help='user commands')
    add('-v', action='store_true',  help='report pylint version')
    add('--verbose', action='store_true',  help='verbose output')
    # Parse the options.
    options, args = parser.parse_args()
    if options.v:
        # -v anywhere just prints the version.
        return 'version', False
    verbose = options.verbose
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
    elif options.u: scope = 'commands'
    elif options.v: scope = 'version'
    else: scope = 'all'
    return scope, verbose
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@@nobeautify
g_option_fn = None
scope, verbose = scanOptions()
if scope == 'version':
    report_version()
else:
    files = leoTest.LinterTable().get_files_for_scope(scope, fn=g_option_fn)
    main(files, verbose)
#@@beautify
#@-leo

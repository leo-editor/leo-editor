#@+leo-ver=5-thin
#@+node:ekr.20160518000549.1: * @file ../../pyflakes-leo.py
'''
This file runs pyflakes on predefined lists of files.

On windows, the following .bat file runs this file::
    python pyflakes-leo.py %*

On Ubuntu, the following alias runs this file::
    pyflake="python pyflake-leo.py"
'''
#@@language python
# pylint: disable=invalid-name
    # pyflakes-leo isn't a valid module name, but it isn't a module.
import leo.core.leoGlobals as g
import leo.core.leoTest as leoTest
import optparse
import os
import sys
import time
#@+others
#@+node:ekr.20160518000549.10: ** main & helpers
def main(tables_table, silent):
    '''Call run on all tables in tables_table.'''    
    t1 = time.clock()
    n = 0
    for table, dir_ in tables_table:
        n += len(table)
        check_all(dir_, table, silent)
    t2 = time.clock()
    print('%s file%s, time: %5.2f sec.' % (n, g.plural(n), t2-t1))
#@+node:ekr.20160518000549.11: *3* get_home
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
#@+node:ekr.20160518000741.1: *3* check_all
def check_all(dir_, files, silent):
    '''Run pyflakes on fn.'''
    from pyflakes import api, reporter
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
    for fn in paths:
        # Report the file name.
        sfn = g.shortFileName(fn)
        if not silent:
            print('pyflakes: %s' % sfn)
        s = g.readFileIntoEncodedString(fn, silent=False)
        if not s.strip():
            return
        r = reporter.Reporter(
            errorStream=sys.stderr,
            warningStream=sys.stderr,
            )
        api.check(s, sfn, r)
#@+node:ekr.20160518000549.14: ** report_version
def report_version():
    try:
        import flake8
        print('flake8 version: %s' % flake8.__version__)
    except ImportError:
        g.trace('can not import flake8')
#@+node:ekr.20160518000549.15: ** scanOptions
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
g_option_fn = None
scope, silent = scanOptions()
table = leoTest.LinterTable().get_table(scope, fn=g_option_fn)
if scope == 'version':
    report_version()
else:
    main(table, silent)
#@-leo

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
#@@tabwidth -4
# pylint: disable=invalid-name
    # pyflakes-leo isn't a valid module name, but it isn't a module.
import leo.core.leoGlobals as g
import leo.core.leoTest as leoTest
from pyflakes import api, reporter
import optparse
# import os
import sys
import time
#@+others
#@+node:ekr.20160518000549.10: ** main (pyflakes-leo.py)
def main(files):
    '''Call run on all tables in tables_table.'''
    t1 = time.time()
    for fn in files:
        # Report the file name.
        assert g.os_path_exists(fn), fn
        sfn = g.shortFileName(fn)
        s = g.readFileIntoEncodedString(fn)
        if s and s.strip():
            r = reporter.Reporter(
                errorStream=sys.stderr,
                warningStream=sys.stderr,
                )
            api.check(s, sfn, r)
    t2 = time.time()
    n = len(files)
    print('%s file%s, time: %5.2f sec.' % (n, g.plural(n), t2-t1))
#@+node:ekr.20160518000549.14: ** report_version
def report_version():
    try:
        import flake8
        print('flake8 version: %s' % flake8.__version__)
    except Exception:
        g.trace('can not import flake8')
#@+node:ekr.20160518000549.15: ** scanOptions
def scanOptions():
    '''Handle all options, remove them from sys.argv.'''
    global g_option_fn
    # This automatically implements the -h (--help) option.
    parser = optparse.OptionParser()
    add = parser.add_option
    add('-a', action='store_true', help='all (default)')
    add('-c', action='store_true', help='core')
    add('-e', action='store_true', help='external')
    add('-f', dest='filename', help='filename, relative to leo folder')
    add('-g', action='store_true', help='gui plugins')
    add('-m', action='store_true', help='modes')
    add('-p', action='store_true', help='plugins')
    # add('-s', action='store_true', help='silent')
    add('-u', action='store_true', help='user commands')
    add('-v', '--version', dest='v',
        action='store_true', help='report pyflakes version')
    # Parse the options.
    options, args = parser.parse_args()
    # silent = options.s
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
    # elif options.s: scope = 'silent'
    elif options.u: scope = 'commands'
    elif options.v: scope = 'version'
    else: scope = 'all'
    return scope
#@-others
g_option_fn = None
scope = scanOptions()
if scope == 'version':
    report_version()
else:
    files = leoTest.LinterTable().get_files_for_scope(scope, fn=g_option_fn)
    main(files)
#@-leo

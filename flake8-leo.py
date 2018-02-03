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
#@@tabwidth -4
# pylint: disable=invalid-name
    # flake8-leo isn't a valid module name, but it isn't a module.
import leo.core.leoGlobals as g
import leo.core.leoTest as leoTest
import optparse
import os
import time
#@+others
#@+node:ekr.20160517182239.10: ** main & helpers
def main(files):
    '''Call run on all tables in tables_table.'''
    try:
        from flake8 import engine
    except Exception:
        print('can not import flake8')
    config_file = get_flake8_config()
    if config_file:
        style = engine.get_style_guide(
            parse_argv=False, config_file=config_file)
        t1 = time.time()
        check_all(files, style)
        t2 = time.time()
        n = len(files)
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
    trace = False and not g.unitTesting
    join = g.os_path_finalize_join
    homeDir = get_home()
    loadDir = g.os_path_finalize_join(g.__file__, '..', '..')
    base_table = ('flake8', 'flake8.txt')
    dir_table = (
        homeDir,
        join(homeDir, '.leo'),
        join(loadDir, '..', '..', 'leo', 'test'),
    )
    for base in base_table:
        for path in dir_table:
            fn = g.os_path_abspath(join(path, base))
            if g.os_path_exists(fn):
                if trace: g.trace('found:', fn)
                return fn
    print('no flake8 configuration file found in\n%s' % (
        '\n'.join(dir_table)))
    return None
#@+node:ekr.20160517222332.1: *3* check_all
def check_all(files, style):
    '''Run flake8 on all paths.'''
    from flake8 import main
    # loadDir = g.os_path_finalize_join(g.__file__, '..', '..')
    # paths = []
    # for fn in files:
        # if dir_:
            # fn = g.os_path_join(loadDir, dir_, fn)
        # else:
            # fn = g.os_path_join(loadDir, fn)
        # fn = g.os_path_abspath(fn)
        # if not fn.endswith('.py'):
            # fn = fn+'.py'
        # if g.os_path_exists(fn):
            # # Make *sure* that we check files only once.
            # if fn in seen:
                # g.trace('already seen:', fn)
            # else:
                # seen.add(fn)
                # paths.append(fn)
        # else:
            # print('does not exist: %s' % (fn))

    # Set statistics here, instead of from the command line.
    # options = style.options
    # options.statistics = True
    # options.total_errors = True
    # options.benchmark = True
    report = style.check_files(paths=files)
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
    # add('-s', action='store_true', help='silent')
    add('-u', action='store_true', help='user commands')
    add('-v', '--version', dest='v',
        action='store_true', help='report flake8 version')
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

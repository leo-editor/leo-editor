# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161021090740.1: * @file ../commands/checkerCommands.py
#@@first
"""Commands that invoke external checkers"""
#@+<< checkerCommands imports >>
#@+node:ekr.20161021092038.1: ** << checkerCommands imports >>
import os
import shlex
import sys
import time
#
# Third-party imports.
# pylint: disable=import-error
try:
    from mypy import api as mypy_api
except Exception:
    mypy_api = None
try:
    import flake8
    # #2248: Import only flake8.
except ImportError:
    flake8 = None  # type:ignore
try:
    import mypy
except Exception:
    mypy = None  # type:ignore
try:
    import pyflakes
    from pyflakes import api, reporter
except Exception:
    pyflakes = None  # type:ignore
try:
    # pylint: disable=import-error
    from pylint import lint
except Exception:
    lint = None  # type:ignore
#
# Leo imports.
from leo.core import leoGlobals as g
#@-<< checkerCommands imports >>
#@+others
#@+node:ekr.20161021091557.1: **  Commands
#@+node:ekr.20190608084751.1: *3* find-long-lines
@g.command('find-long-lines')
def find_long_lines(event):
    """Report long lines in the log, with clickable links."""
    c = event and event.get('c')
    if not c:
        return
    #@+others # helper functions
    #@+node:ekr.20190609135639.1: *4* function: get_root
    def get_root(p):
        """Return True if p is any @<file> node."""
        for parent in p.self_and_parents():
            if parent.anyAtFileNodeName():
                return parent
        return None
    #@+node:ekr.20190608084751.2: *4* function: in_no_pylint
    def in_nopylint(p):
        """Return p if p is controlled by @nopylint."""
        for parent in p.self_and_parents():
            if '@nopylint' in parent.h:
                return True
        return False
    #@-others
    log = c.frame.log
    max_line = c.config.getInt('max-find-long-lines-length') or 110
    count, files, ignore = 0, [], []
    for p in c.all_unique_positions():
        if in_nopylint(p):
            continue
        root = get_root(p)
        if not root:
            continue
        if root.v not in files:
            files.append(root.v)
        for i, s in enumerate(g.splitLines(p.b)):
            if len(s) > max_line:
                if not root:
                    if p.v not in ignore:
                        ignore.append(p.v)
                        g.es_print('no root', p.h)
                else:
                    count += 1
                    short_s = g.truncate(s, 30)
                    g.es('')
                    g.es_print(root.h)
                    g.es_print(p.h)
                    print(short_s)
                    unl = p.get_UNL()
                    log.put(short_s.strip() + '\n', nodeLink=f"{unl}::{i + 1}")  # Local line.
                break
    g.es_print(
        f"found {count} long line{g.plural(count)} "
        f"longer than {max_line} characters in "
        f"{len(files)} file{g.plural(len(files))}")
#@+node:ekr.20190615180048.1: *3* find-missing-docstrings
@g.command('find-missing-docstrings')
def find_missing_docstrings(event):
    """Report missing docstrings in the log, with clickable links."""
    c = event and event.get('c')
    if not c:
        return
    #@+others # Define functions
    #@+node:ekr.20190615181104.1: *4* function: has_docstring
    def has_docstring(lines, n):
        """
        Returns True if function/method/class whose definition
        starts on n-th line in lines has a docstring
        """
        # By Виталије Милошевић.
        for line in lines[n:]:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            if s.startswith(('"""', "'''")):
                return True
        return False
    #@+node:ekr.20190615181104.2: *4* function: is_a_definition
    def is_a_definition(line):
        """Return True if line is a definition line."""
        # By Виталије Милошевић.
        # It may be useful to skip __init__ methods because their docstring
        # is usually docstring of the class
        return (
            line.startswith(('def ', 'class ')) and
            not line.partition(' ')[2].startswith('__init__')
        )
    #@+node:ekr.20190615182754.1: *4* function: is_root
    def is_root(p):
        """
        A predicate returning True if p is an @<file> node that is not under @nopylint.
        """
        for parent in p.self_and_parents():
            if g.match_word(parent.h, 0, '@nopylint'):
                return False
        return p.isAnyAtFileNode() and p.h.strip().endswith('.py')
    #@-others
    log = c.frame.log
    count, files, found, t1 = 0, 0, [], time.process_time()
    for root in g.findRootsWithPredicate(c, c.p, predicate=is_root):
        files += 1
        for p in root.self_and_subtree():
            lines = p.b.split('\n')
            for i, line in enumerate(lines):
                if is_a_definition(line) and not has_docstring(lines, i):
                    count += 1
                    if root.v not in found:
                        found.append(root.v)
                        g.es_print('')
                        g.es_print(root.h)
                    print(line)
                    unl = p.get_UNL()
                    log.put(line.strip() + '\n', nodeLink=f"{unl}::{i + 1}")  # Local line.
                    break
    g.es_print('')
    g.es_print(
        f"found {count} missing docstring{g.plural(count)} "
        f"in {files} file{g.plural(files)} "
        f"in {time.process_time() - t1:5.2f} sec.")
#@+node:ekr.20160517133001.1: *3* flake8-files command
@g.command('flake8-files')
def flake8_command(event):
    """
    Run flake8 on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    """
    tag = 'flake8-files'
    if not flake8:
        g.es_print(f"{tag} can not import flake8")
        return
    c = event and event.get('c')
    if not c or not c.p:
        return
    python = sys.executable
    for root in g.findRootsWithPredicate(c, c.p):
        path = g.fullPath(c, root)
        if path and os.path.exists(path):
            g.es_print(f"{tag}: {path}")
            g.execute_shell_commands(f'&"{python}" -m flake8 "{path}"')
        else:
            g.es_print(f"{tag}: file not found:{path}")
#@+node:ekr.20161026092059.1: *3* kill-pylint
@g.command('kill-pylint')
@g.command('pylint-kill')
def kill_pylint(event):
    """Kill any running pylint processes and clear the queue."""
    g.app.backgroundProcessManager.kill('pylint')
#@+node:ekr.20210302111730.1: *3* mypy command
@g.command('mypy')
def mypy_command(event):
    """
    Run mypy on all @<file> nodes of the selected tree, or the first
    @<file> node in an ancestor. Running mypy on a single file usually
    suffices.

    For example, in LeoPyRef.leo, you can run mypy on most of Leo's files
    by running this command with the following node selected:

      `@edit ../../launchLeo.py`

    Unlike running mypy outside of Leo, Leo's mypy command creates
    clickable links in Leo's log pane for each error. See g.mypy_pat.

    Settings
    --------

    @data mypy-arguments
    @int mypy-link-limit = 0
    @string mypy-config-file=''

    See leoSettings.leo for details.
    """
    c = event and event.get('c')
    if not c:
        return
    if c.isChanged():
        c.save()
    if mypy_api:
        MypyCommand(c).run(c.p)
    else:
        g.es_print('can not import mypy')
#@+node:ekr.20160516072613.1: *3* pyflakes command
@g.command('pyflakes')
def pyflakes_command(event):
    """
    Run pyflakes on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    """
    c = event and event.get('c')
    if not c:
        return
    if c.isChanged():
        c.save()
    if not pyflakes:
        g.es_print('can not import pyflakes')
        return
    ok = PyflakesCommand(c).run(c.p)
    if ok:
        g.es('OK: pyflakes')
#@+node:ekr.20150514125218.7: *3* pylint command
last_pylint_path = None

@g.command('pylint')
def pylint_command(event):
    """
    Run pylint on all nodes of the selected tree,
    or the first @<file> node in an ancestor,
    or the last checked @<file> node.
    """
    global last_pylint_path
    c = event and event.get('c')
    if c:
        if c.isChanged():
            c.save()
        data = PylintCommand(c).run(last_path=last_pylint_path)
        if data:
            path, p = data
            last_pylint_path = path
#@+node:ekr.20210302111917.1: ** class MypyCommand
class MypyCommand:
    """A class to run mypy on all Python @<file> nodes in c.p's tree."""

    # See g.mypy_pat for the regex that creates clickable links.

    def __init__(self, c):
        """ctor for MypyCommand class."""
        self.c = c
        self.link_limit = None  # Set in check_file.
        self.unknown_path_names = []

    #@+others
    #@+node:ekr.20210302111935.3: *3* mypy.check_all
    def check_all(self, roots):
        """Run mypy on all files in paths."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        self.unknown_path_names = []
        for root in roots:
            fn = os.path.normpath(g.fullPath(c, root))
            self.check_file(fn, root)


    #@+node:ekr.20210727212625.1: *3* mypy.check_file
    def check_file(self, fn, root):
        """Run mypy on one file."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        command = f"{sys.executable} -m mypy {fn}"
        bpm = g.app.backgroundProcessManager
        bpm.start_process(c, command,
            fn=fn,
            kind='mypy',
            link_pattern=g.mypy_pat,
            link_root=root,
        )

    #@+node:ekr.20210302111935.7: *3* mypy.run (entry)
    def run(self, p):
        """Run mypy on all Python @<file> nodes in c.p's tree."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        root = p.copy()
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)
        roots = g.findRootsWithPredicate(c, root, predicate=None)
        g.printObj([z.h for z in roots], tag='mypy.run')
        self.check_all(roots)
    #@-others
#@+node:ekr.20160516072613.2: ** class PyflakesCommand
class PyflakesCommand:
    """A class to run pyflakes on all Python @<file> nodes in c.p's tree."""

    def __init__(self, c):
        """ctor for PyflakesCommand class."""
        self.c = c
        self.seen = []  # List of checked paths.

    #@+others
    #@+node:ekr.20171228013818.1: *3* class PyflakesCommand.LogStream
    class LogStream:

        """A log stream for pyflakes."""

        def __init__(self, fn_n=0, roots=None):
            self.fn_n = fn_n
            self.roots = roots

        def write(self, s):
            fn_n, roots = self.fn_n, self.roots
            if not s.strip():
                return
            g.pr(s)
            # It *is* useful to send pyflakes errors to the console.
            if roots:
                try:
                    root = roots[fn_n]
                    line = int(s.split(':')[1])
                    unl = root.get_UNL()
                    g.es(s, nodeLink=f"{unl}::{(-line)}")  # Global line
                except(IndexError, TypeError, ValueError):
                    # in case any assumptions fail
                    g.es(s)
            else:
                g.es(s)
    #@+node:ekr.20160516072613.6: *3* pyflakes.check_all
    def check_all(self, roots):
        """Run pyflakes on all files in paths."""
        total_errors = 0
        for i, root in enumerate(roots):
            fn = self.finalize(root)
            sfn = g.shortFileName(fn)
            # #1306: nopyflakes
            if any(z.strip().startswith('@nopyflakes') for z in g.splitLines(root.b)):
                continue
            # Report the file name.
            s = g.readFileIntoEncodedString(fn)
            if s and s.strip():
                # Send all output to the log pane.
                r = reporter.Reporter(
                    errorStream=self.LogStream(i, roots),
                    warningStream=self.LogStream(i, roots),
                )
                errors = api.check(s, sfn, r)
                total_errors += errors
        return total_errors
    #@+node:ekr.20171228013625.1: *3* pyflakes.check_script
    def check_script(self, p, script):
        """Call pyflakes to check the given script."""
        try:
            from pyflakes import api, reporter
        except Exception:  # ModuleNotFoundError
            return True  # Pretend all is fine.
        # #1306: nopyflakes
        lines = g.splitLines(p.b)
        for line in lines:
            if line.strip().startswith('@nopyflakes'):
                return True
        r = reporter.Reporter(
            errorStream=self.LogStream(),
            warningStream=self.LogStream(),
        )
        errors = api.check(script, '', r)
        return errors == 0
    #@+node:ekr.20170220114553.1: *3* pyflakes.finalize
    def finalize(self, p):
        """Finalize p's path."""
        c = self.c
        # Use os.path.normpath to give system separators.
        return os.path.normpath(g.fullPath(c, p))  # #1914.
    #@+node:ekr.20160516072613.5: *3* pyflakes.run
    def run(self, p):
        """Run Pyflakes on all Python @<file> nodes in p's tree."""
        ok = True
        if not pyflakes:
            return ok
        c = self.c
        root = p
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)
        roots = g.findRootsWithPredicate(c, root, predicate=None)
        if roots:
            # These messages are important for clarity.
            total_errors = self.check_all(roots)
            if total_errors > 0:
                g.es(f"ERROR: pyflakes: {total_errors} error{g.plural(total_errors)}")
            ok = total_errors == 0
        else:
            ok = True
        return ok
    #@-others
#@+node:ekr.20150514125218.8: ** class PylintCommand
class PylintCommand:
    """A class to run pylint on all Python @<file> nodes in c.p's tree."""

    def __init__(self, c):
        self.c = c
        self.data = None  # Data for the *running* process.
        self.rc_fn = None  # Name of the rc file.
    #@+others
    #@+node:ekr.20150514125218.11: *3* 1. pylint.run
    def run(self, last_path=None):
        """Run Pylint on all Python @<file> nodes in c.p's tree."""
        c, root = self.c, self.c.p
        if not lint:
            g.es_print('pylint is not installed')
            return False
        self.rc_fn = self.get_rc_file()
        if not self.rc_fn:
            return False
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)

        # Ignore @nopylint trees.

        def predicate(p):
            for parent in p.self_and_parents():
                if g.match_word(parent.h, 0, '@nopylint'):
                    return False
            return p.isAnyAtFileNode() and p.h.strip().endswith(('.py', '.pyw'))  # #2354.

        roots = g.findRootsWithPredicate(c, root, predicate=predicate)
        data = [(self.get_fn(p), p.copy()) for p in roots]
        data = [z for z in data if z[0] is not None]
        if not data and last_path:
            # Default to the last path.
            fn = last_path
            for p in c.all_positions():
                if p.isAnyAtFileNode() and g.fullPath(c, p) == fn:
                    data = [(fn, p.copy())]
                    break
        if not data:
            g.es('pylint: no files found', color='red')
            return None
        for fn, p in data:
            self.run_pylint(fn, p)
        # #1808: return the last data file.
        return data[-1] if data else False
    #@+node:ekr.20150514125218.10: *3* 3. pylint.get_rc_file
    def get_rc_file(self):
        """Return the path to the pylint configuration file."""
        base = 'pylint-leo-rc.txt'
        table = (
            # In ~/.leo
            g.os_path_finalize_join(g.app.homeDir, '.leo', base),
            # In leo/test
            g.os_path_finalize_join(g.app.loadDir, '..', '..', 'leo', 'test', base),
        )
        for fn in table:
            fn = g.os_path_abspath(fn)
            if g.os_path_exists(fn):
                return fn
        table_s = '\n'.join(table)
        g.es_print(f"no pylint configuration file found in\n{table_s}")
        return None
    #@+node:ekr.20150514125218.9: *3* 4. pylint.get_fn
    def get_fn(self, p):
        """
        Finalize p's file name.
        Return if p is not an @file node for a python file.
        """
        c = self.c
        fn = p.isAnyAtFileNode()
        if not fn:
            g.trace(f"not an @<file> node: {p.h!r}")
            return None
        return g.fullPath(c, p)  # #1914
    #@+node:ekr.20150514125218.12: *3* 5. pylint.run_pylint
    def run_pylint(self, fn, p):
        """Run pylint on fn with the given pylint configuration file."""
        c, rc_fn = self.c, self.rc_fn
        #
        # Invoke pylint directly.
        is_win = sys.platform.startswith('win')
        args = ','.join([f"'--rcfile={rc_fn}'", f"'{fn}'"])
        if is_win:
            args = args.replace('\\', '\\\\')
        command = (
            f'{sys.executable} -c "from pylint import lint; args=[{args}]; lint.Run(args)"')
        if not is_win:
            command = shlex.split(command)  # type:ignore
        #
        # Run the command using the BPM.
        bpm = g.app.backgroundProcessManager
        bpm.start_process(c, command,
            fn=fn,
            kind='pylint',
            link_pattern=g.pylint_pat,
            link_root=p,
        )
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@-leo

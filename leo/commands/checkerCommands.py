# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161021090740.1: * @file ../commands/checkerCommands.py
#@@first
"""Commands that invoke external checkers"""
#@+<< imports >>
#@+node:ekr.20161021092038.1: ** << imports >> checkerCommands.py
import leo.core.leoGlobals as g
try:
    # pylint: disable=import-error
        # We can't assume the user has this.
    import flake8
except Exception: # May not be ImportError.
    flake8 = None
try:
    import pyflakes
except ImportError:
    pyflakes = None
import shlex
import sys
import time
#@-<< imports >>
#@+others
#@+node:ekr.20161021091557.1: **  Commands
#@+node:ekr.20171211055756.1: *3* checkConventions (checkerCommands.py)
@g.command('check-conventions')
@g.command('cc')
def checkConventions(event):
    """Experimental script to test Leo's convensions."""
    c = event.get('c')
    if c:
        if c.changed: c.save()
        import imp
        import leo.core.leoCheck as leoCheck
        imp.reload(leoCheck)
        leoCheck.ConventionChecker(c).check()
#@+node:ekr.20190608084751.1: *3* find-long-lines
@g.command('find-long-lines')
def find_long_lines(event):
    """Report long lines in the log, with clickable links."""
    c = event.get('c')
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
                    g.es_clickable_link(c, p, line_number=i, message=short_s)
                break
    g.es_print(
        f"found {count} long line{g.plural(count)} "
        f"longer than {max_line} characters in "
        f"{len(files)} file{g.plural(len(files))}")
#@+node:ekr.20190615180048.1: *3* find-missing-docstrings
@g.command('find-missing-docstrings')
def find_missing_docstrings(event):
    """Report missing docstrings in the log, with clickable links."""
    c = event.get('c')
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
    #@+node:ekr.20190615180900.1: *4* function: clickable_link 
    def clickable_link(p, i):
        """Return a clickable link to line i of p.b."""
        link = p.get_UNL(with_proto=True, with_count=True, with_index=True)
        return f"{link},{i}"
    #@-others

    count, found, t1 = 0, [], time.process_time()
    for root in g.findRootsWithPredicate(c, c.p, predicate=is_root):
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
                    g.es(line, nodeLink=clickable_link(p, i + 1))
                    break
    g.es_print('')
    g.es_print('found %s missing docstring%s in %s file%s in %5.2f sec.' % (
        count, g.plural(count),
        len(found), g.plural(len(found)),
        (time.process_time() - t1)))
#@+node:ekr.20160517133001.1: *3* flake8 command
@g.command('flake8')
def flake8_command(event):
    """
    Run flake8 on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    """
    c = event.get('c')
    if c:
        if c.isChanged():
            c.save()
        if flake8:
            Flake8Command(c).run()
        else:
            g.es_print('can not import flake8')
#@+node:ekr.20161026092059.1: *3* kill-pylint
@g.command('kill-pylint')
@g.command('pylint-kill')
def kill_pylint(event):
    """Kill any running pylint processes and clear the queue."""
    g.app.backgroundProcessManager.kill('pylint')
#@+node:ekr.20160516072613.1: *3* pyflakes command
@g.command('pyflakes')
def pyflakes_command(event):
    """
    Run pyflakes on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    """
    c = event.get('c')
    if c:
        if c.isChanged():
            c.save()
        if pyflakes:
            PyflakesCommand(c).run(force=True)
        else:
            g.es_print('can not import pyflakes')
#@+node:ekr.20150514125218.7: *3* pylint command
@g.command('pylint')
def pylint_command(event):
    """
    Run pylint on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    """
    c = event.get('c')
    if c:
        if c.isChanged():
            c.save()
        PylintCommand(c).run()
#@+node:ekr.20160517133049.1: ** class Flake8Command
class Flake8Command:
    """A class to run flake8 on all Python @<file> nodes in c.p's tree."""

    def __init__(self, c, quiet=False):
        """ctor for Flake8Command class."""
        self.c = c
        self.quiet = quiet
        self.seen = [] # List of checked paths.

    #@+others
    #@+node:ekr.20160517133049.2: *3* flake8.check_all
    def check_all(self, paths):
        """Run flake8 on all paths."""
        try:
            # pylint: disable=import-error
                # We can't assume the user has this.
            from flake8 import engine, main
        except Exception:
            return
        config_file = self.get_flake8_config()
        if config_file:
            style = engine.get_style_guide(
                parse_argv=False,
                config_file=config_file,
            )
            report = style.check_files(paths=paths)
            # Set statistics here, instead of from the command line.
            options = style.options
            options.statistics = True
            options.total_errors = True
            # options.benchmark = True
            main.print_report(report, style)
    #@+node:ekr.20160517133049.3: *3* flake8.find
    def find(self, p):
        """Return True and add p's path to self.seen if p is a Python @<file> node."""
        c = self.c
        found = False
        if p.isAnyAtFileNode():
            aList = g.get_directives_dict_list(p)
            path = c.scanAtPathDirectives(aList)
            fn = p.anyAtFileNodeName()
            if fn.endswith('.py'):
                fn = g.os_path_finalize_join(path, fn)
                if fn not in self.seen:
                    self.seen.append(fn)
                    found = True
        return found
    #@+node:ekr.20160517133049.4: *3* flake8.get_flake8_config
    def get_flake8_config(self):
        """Return the path to the pylint configuration file."""
        join = g.os_path_finalize_join
        dir_table = (
            g.app.homeDir,
            join(g.app.homeDir, '.leo'),
            join(g.app.loadDir, '..', '..', 'leo', 'test'),
        )
        for base in ('flake8', 'flake8.txt'):
            for path in dir_table:
                fn = g.os_path_abspath(join(path, base))
                if g.os_path_exists(fn):
                    return fn
        if not g.unitTesting:
            g.es_print('no flake8 configuration file found in\n%s' % (
                '\n'.join(dir_table)))
        return None
    #@+node:ekr.20160517133049.5: *3* flake8.run
    def run(self, p=None):
        """Run flake8 on all Python @<file> nodes in c.p's tree."""
        c = self.c
        root = p or c.p
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)
        # Run flake8 on all Python @<file> nodes in root's tree.
        t1 = time.time()
        found = False
        for p in root.self_and_subtree():
            found |= self.find(p)
        # Look up the tree if no @<file> nodes were found.
        if not found:
            for p in root.parents():
                if self.find(p):
                    found = True
                    break
        # If still not found, expand the search if root is a clone.
        if not found:
            isCloned = any([p.isCloned() for p in root.self_and_parents()])
            if isCloned:
                for p in c.all_positions():
                    if p.isAnyAtFileNode():
                        isAncestor = any([z.v == root.v for z in p.self_and_subtree()])
                        if isAncestor and self.find(p):
                            break
        paths = list(set(self.seen))
        if paths:
            self.check_all(paths)
        g.es_print(f"flake8: {len(paths)} file{g.plural(paths)} in {g.timeSince(t1)}")
    #@-others
#@+node:ekr.20160516072613.2: ** class PyflakesCommand
class PyflakesCommand:
    """A class to run pyflakes on all Python @<file> nodes in c.p's tree."""

    def __init__(self, c):
        """ctor for PyflakesCommand class."""
        self.c = c
        self.seen = [] # List of checked paths.

    #@+others
    #@+node:ekr.20171228013818.1: *3* class LogStream
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
                    unl = root.get_UNL(with_proto=True, with_count=True)
                    g.es(s, nodeLink=f"{unl},{(-line)}")
                except(IndexError, TypeError, ValueError):
                    # in case any assumptions fail
                    g.es(s)
            else:
                g.es(s)
    #@+node:ekr.20160516072613.6: *3* pyflakes.check_all
    def check_all(self, log_flag, pyflakes_errors_only, roots):
        """Run pyflakes on all files in paths."""
        try:
            from pyflakes import api, reporter
        except Exception: # ModuleNotFoundError
            return True # Pretend all is fine.
        total_errors = 0
        for i, root in enumerate(roots):
            fn = self.finalize(root)
            sfn = g.shortFileName(fn)
            # #1306: nopyflakes
            if any([z.strip().startswith('@nopyflakes') for z in g.splitLines(root.b)]):
                continue
            # Report the file name.
            s = g.readFileIntoEncodedString(fn)
            if s and s.strip():
                if not pyflakes_errors_only:
                    g.es(f"Pyflakes: {sfn}")
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
        except Exception: # ModuleNotFoundError
            return True # Pretend all is fine.
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
        aList = g.get_directives_dict_list(p)
        path = self.c.scanAtPathDirectives(aList)
        path = c.expand_path_expression(path) # #1341.
        fn = p.anyAtFileNodeName()
        fn = c.expand_path_expression(fn) # #1341.
        return g.os_path_finalize_join(path, fn)
    #@+node:ekr.20160516072613.3: *3* pyflakes.find (no longer used)
    def find(self, p):
        """Return True and add p's path to self.seen if p is a Python @<file> node."""
        c = self.c
        found = False
        if p.isAnyAtFileNode():
            aList = g.get_directives_dict_list(p)
            path = c.scanAtPathDirectives(aList)
            fn = p.anyAtFileNodeName()
            if fn.endswith('.py'):
                fn = g.os_path_finalize_join(path, fn)
                if fn not in self.seen:
                    self.seen.append(fn)
                    found = True
        return found
    #@+node:ekr.20160516072613.5: *3* pyflakes.run
    def run(self, p=None, force=False, pyflakes_errors_only=False):
        """Run Pyflakes on all Python @<file> nodes in c.p's tree."""
        c = self.c
        root = p or c.p
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)
        t1 = time.time()
        roots = g.findRootsWithPredicate(c, root, predicate=None)
        if roots:
            # These messages are important for clarity.
            log_flag = not force
            total_errors = self.check_all(log_flag, pyflakes_errors_only, roots)
            if total_errors > 0:
                g.es(f"ERROR: pyflakes: {total_errors} error{g.plural(total_errors)}")
            elif force:
                g.es(f"OK: pyflakes: {len(roots)} file{g.plural(roots)} in {g.timeSince(t1)}")
            elif not pyflakes_errors_only:
                g.es('OK: pyflakes')
            ok = total_errors == 0
        else:
            ok = True
        return ok
    #@-others
#@+node:ekr.20150514125218.8: ** class PylintCommand
class PylintCommand:
    """A class to run pylint on all Python @<file> nodes in c.p's tree."""

    regex = r'^.*:([0-9]+):[0-9]+:.*?(\(.*\))\s*$'
        # m.group(1) is the line number.
        # m.group(2) is the (unused) test name.

    # Example message: file-name:3966:12: R1705:xxxx (no-else-return)

    def __init__(self, c):
        self.c = c
        self.data = None # Data for the *running* process.
        self.rc_fn = None # Name of the rc file.

    #@+others
    #@+node:ekr.20150514125218.11: *3* 1. pylint.run
    def run(self):
        """Run Pylint on all Python @<file> nodes in c.p's tree."""
        c, root = self.c, self.c.p
        if not self.import_lint():
            return
        self.rc_fn = self.get_rc_file()
        if not self.rc_fn:
            return
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)

        # Ignore @nopylint trees.

        def predicate(p):
            for parent in p.self_and_parents():
                if g.match_word(parent.h, 0, '@nopylint'):
                    return False
            return p.isAnyAtFileNode() and p.h.strip().endswith('.py')

        roots = g.findRootsWithPredicate(c, root, predicate=predicate)
        data = [(self.get_fn(p), p.copy()) for p in roots]
        data = [z for z in data if z[0] is not None]
        if not data:
            g.es('pylint: no files found', color='red')
            return
        for fn, p in data:
            self.run_pylint(fn, p)
    #@+node:ekr.20190605183824.1: *3* 2. pylint.import_lint
    def import_lint(self):
        """Make sure lint can be imported."""
        try:
            from pylint import lint
            g.placate_pyflakes(lint)
            return True
        except ImportError:
            g.es_print('pylint is not installed')
            return False
    #@+node:ekr.20150514125218.10: *3* 3. pylint.get_rc_file
    def get_rc_file(self):
        """Return the path to the pylint configuration file."""
        base = 'pylint-leo-rc.txt'
        table = (
            g.os_path_finalize_join(g.app.homeDir, '.leo', base),
                # In ~/.leo
            g.os_path_finalize_join(g.app.loadDir, '..', '..', 'leo', 'test', base),
                # In leo/test
        )
        for fn in table:
            fn = g.os_path_abspath(fn)
            if g.os_path_exists(fn):
                return fn
        g.es_print('no pylint configuration file found in\n%s' % (
            '\n'.join(table)))
        return None
    #@+node:ekr.20150514125218.9: *3* 4. pylint.get_fn
    def get_fn(self, p):
        """
        Finalize p's file name.
        Return if p is not an @file node for a python file.
        """
        c = self.c
        if not p.isAnyAtFileNode():
            g.trace('not an @<file> node: %r' % p.h)
            return None
        # #67.
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        fn = p.anyAtFileNodeName()
        if not fn.endswith('.py'):
            g.trace('not a python file: %r' % p.h)
            return None
        return g.os_path_finalize_join(path, fn)
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
        command = (f'{sys.executable} -c "from pylint import lint; args=[{args}]; lint.Run(args)"')
        if not is_win:
            command = shlex.split(command)
        #
        # Run the command using the BPM.
        bpm = g.app.backgroundProcessManager
        bpm.start_process(c, command,
            fn=fn,
            kind='pylint',
            link_pattern=self.regex,
            link_root=p,
        )

        # Old code: Invoke g.run_pylint.
            # args = ["fn=r'%s'" % (fn), "rc=r'%s'" % (rc_fn),]
            # # When shell is True, it's recommended to pass a string, not a sequence.
            # command = '%s -c "import leo.core.leoGlobals as g; g.run_pylint(%s)"' % (
                # sys.executable, ','.join(args))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

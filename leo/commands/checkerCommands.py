# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161021090740.1: * @file ../commands/checkerCommands.py
#@@first
'''Commands that invoke external checkers'''
#@+<< imports >>
#@+node:ekr.20161021092038.1: ** << imports >> checkerCommands.py
import leo.core.leoGlobals as g
try:
    import flake8
except ImportError:
    flake8 = None
try:
    import pyflakes
except ImportError:
    pyflakes = None
import os
import shlex
import subprocess
import sys
import time
#@-<< imports >>
# Global data to queue pylint commands.
g_pylint_fn = None
    # The name of the file being checked.
g_pylint_list = []
    # List of callbacks to check files.
g_pylint_pid = None
    # The id of the of the running pylint checker process.
#@+others
#@+node:ekr.20161021091557.1: **  Commands
#@+node:ekr.20161026092059.1: *3* kill-pylint
@g.command('kill-pylint')
@g.command('pylint-kill')
def kill_pylint(event):
    '''Kill any running pylint processes and clear the queue.'''
    global g_pylint_fn, g_pylint_list, g_pylint_pid
    g_pylint_list = []
    if g_pylint_pid:
        g.es_print('killing checker for', g_pylint_fn)
        g_pylint_pid.kill()
        g_pylint_pid = None
    g.es_print('pylint finished')
#@+node:ekr.20160517133001.1: *3* flake8 command
@g.command('flake8')
def flake8_command(event):
    '''
    Run flake8 on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    '''
    c = event.get('c')
    if c:
        if c.isChanged():
            c.save()
        if flake8:
            Flake8Command(c).run()
        else:
            g.es_print('can not import flake8')
#@+node:ekr.20150514125218.7: *3* pylint command
@g.command('pylint')
def pylint_command(event):
    '''
    Run pylint on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    '''
    c = event.get('c')
    if c:
        if c.isChanged():
            c.save()
        PylintCommand(c).run()
#@+node:ekr.20160516072613.1: *3* pyflakes command
@g.command('pyflakes')
def pyflakes_command(event):
    '''
    Run pyflakes on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    '''
    c = event.get('c')
    if c:
        if c.isChanged():
            c.save()
        if pyflakes:
            PyflakesCommand(c).run(force=True)
        else:
            g.es_print('can not import pyflakes')
#@+node:ekr.20161026130259.1: ** Callbacks
#@+node:ekr.20161026130310.1: *3* on_idle (checkerCommands)
def on_idle():
    '''The idle-time callback for leo.commands.checkerCommands.'''
    trace = False and not g.unitTesting
    global g_pylint_list, g_pylint_pid
    if g_pylint_list or g_pylint_pid:
        if trace: g.trace('(checkerCommands)')
        pylint_idle_time_callback()
#@+node:ekr.20161026085610.1: *3* pylint_idle_time_callback
def pylint_idle_time_callback():
    '''Handle idle-time processing.'''
    trace = False and not g.unitTesting
    global g_pylint_list, g_pylint_pid
    trace_inactive = False
    trace_running = False
    if trace and (trace_inactive or g_pylint_pid is not None):
        g.trace(len(g_pylint_list), g_pylint_pid)
    if g_pylint_pid or g_pylint_list:
        if g_pylint_pid.poll() is not None:
            # The previous process has finished.
            if g_pylint_list:
                pylint_callback = g_pylint_list.pop(0)
                pylint_callback()
            else:
                g_pylint_pid = None
                g.es_print('pylint finished')
        elif trace and trace_running:
            g.trace('Running: ', g_pylint_pid)
    elif trace and trace_inactive:
        g.trace('Pylint inactive')
#@+node:ekr.20160517133049.1: ** class Flake8Command
class Flake8Command(object):
    '''A class to run flake8 on all Python @<file> nodes in c.p's tree.'''

    def __init__(self, c, quiet=False):
        '''ctor for Flake8Command class.'''
        self.c = c
        self.quiet = quiet
        self.seen = [] # List of checked paths.

    #@+others
    #@+node:ekr.20160517133049.2: *3* flake8.check_all
    def check_all(self, paths):
        '''Run flake8 on all paths.'''
        from flake8 import engine, main
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
        '''Return True and add p's path to self.seen if p is a Python @<file> node.'''
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
        '''Return the path to the pylint configuration file.'''
        trace = False and not g.unitTesting
        join = g.os_path_finalize_join
        dir_table = (
            g.app.homeDir,
            join(g.app.homeDir, '.leo'),
            join(g.app.loadDir, '..', '..', 'leo', 'test'),
        )
        if g.isPython3:
            base_table = ('flake8', 'flake8.txt')
        else:
            base_table = ('flake8',)
        for base in base_table:
            for path in dir_table:
                fn = g.os_path_abspath(join(path, base))
                if g.os_path_exists(fn):
                    if trace: g.trace('found:', fn)
                    return fn
        if not g.unitTesting:
            g.es_print('no flake8 configuration file found in\n%s' % (
                '\n'.join(dir_table)))
        return None
    #@+node:ekr.20160517133049.5: *3* flake8.run
    def run(self, p=None):
        '''Run flake8 on all Python @<file> nodes in c.p's tree.'''
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
            # g.trace(isCloned,root.h)
            if isCloned:
                for p in c.all_positions():
                    if p.isAnyAtFileNode():
                        isAncestor = any([z.v == root.v for z in p.self_and_subtree()])
                        # g.trace(isAncestor,p.h)
                        if isAncestor and self.find(p):
                            break
        paths = list(set(self.seen))
        if paths:
            self.check_all(paths)
        g.es_print('flake8: %s file%s in %s' % (
            len(paths), g.plural(paths), g.timeSince(t1)))
    #@-others
#@+node:ekr.20160516072613.2: ** class PyflakesCommand
class PyflakesCommand(object):
    '''A class to run pyflakes on all Python @<file> nodes in c.p's tree.'''

    def __init__(self, c):
        '''ctor for PyflakesCommand class.'''
        self.c = c
        self.seen = [] # List of checked paths.

    #@+others
    #@+node:ekr.20160516072613.6: *3* pyflakes.check_all
    def check_all(self, paths):
        '''Run pyflakes on fn.'''
        from pyflakes import api, reporter
        total_errors = 0
        for fn in sorted(paths):
            # Report the file name.
            sfn = g.shortFileName(fn)
            s = g.readFileIntoEncodedString(fn, silent=False)
            if not s.strip():
                return
            if 1:
                # Send all output to the log pane.
                class LogStream:
                    def write(self, s):
                        if s.strip():
                            g.es_print(s)

                r = reporter.Reporter(
                    errorStream=LogStream(),
                    warningStream=LogStream(),
                )
            else:
                r = reporter.Reporter(
                    errorStream=sys.stderr,
                    warningStream=sys.stderr,
                    )
            errors = api.check(s, sfn, r)
            if False and errors:
                # Annoying.
                print('%s error%s in %s' % (errors, g.plural(errors), fn))
            total_errors += errors
        return total_errors
    #@+node:ekr.20160516072613.3: *3* pyflakes.find
    def find(self, p):
        '''Return True and add p's path to self.seen if p is a Python @<file> node.'''
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
    def run(self, p=None, force=False):
        '''Run Pyflakes on all Python @<file> nodes in c.p's tree.'''
        c = self.c
        root = p or c.p
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)
        # Run pyflakes on all Python @<file> nodes in root's tree.
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
            total_errors = self.check_all(paths)
            if total_errors or force:
                g.es_print('pyflakes: %s file%s in %s' % (
                    len(paths), g.plural(paths), g.timeSince(t1)))
    #@-others
#@+node:ekr.20150514125218.8: ** class PylintCommand
class PylintCommand(object):
    '''A class to run pylint on all Python @<file> nodes in c.p's tree.'''

    def __init__(self, c):
        '''ctor for PylintCommand class.'''
        self.c = c
        self.seen = [] # List of checked vnodes.
        self.wait = False
            # Waiting has several advantages:
            # 1. output is shown in the log pane.
            # 2. Total timing statistics can be shown,
            #    so it is always clear when the command has ended.
            # Not waiting *does* works, but the user can't
            # see when the command has ended.

    #@+others
    #@+node:ekr.20150514125218.9: *3* pylint.check
    def check(self, p, rc_fn):
        '''Check a single node.  Return True if it is a Python @<file> node.'''
        c = self.c
        found = False
        if p.isAnyAtFileNode():
            # Fix bug: https://github.com/leo-editor/leo-editor/issues/67
            aList = g.get_directives_dict_list(p)
            path = c.scanAtPathDirectives(aList)
            fn = p.anyAtFileNodeName()
            if fn.endswith('.py'):
                fn = g.os_path_finalize_join(path, fn)
                if p.v not in self.seen:
                    self.seen.append(p.v)
                    self.run_pylint(fn, rc_fn)
                    found = True
        return found
    #@+node:ekr.20150514125218.10: *3* pylint.get_rc_file
    def get_rc_file(self):
        '''Return the path to the pylint configuration file.'''
        trace = False and not g.unitTesting
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
                if trace: g.trace('found:', fn)
                return fn
        g.es_print('no pylint configuration file found in\n%s' % (
            '\n'.join(table)))
        return None
    #@+node:ekr.20150514125218.11: *3* pylint.run
    def run(self):
        '''Run Pylint on all Python @<file> nodes in c.p's tree.'''
        c, root = self.c, self.c.p
        rc_fn = self.get_rc_file()
        if not rc_fn:
            return
        # Make sure Leo is on sys.path.
        leo_path = g.os_path_finalize_join(g.app.loadDir, '..')
        if leo_path not in sys.path:
            sys.path.append(leo_path)
        # Run lint on all Python @<file> nodes in root's tree.
        t1 = time.time()
        found = False
        for p in root.self_and_subtree():
            found |= self.check(p, rc_fn)
        # Look up the tree if no @<file> nodes were found.
        if not found:
            for p in root.parents():
                if self.check(p, rc_fn):
                    found = True
                    break
        # If still not found, expand the search if root is a clone.
        if not found:
            isCloned = any([p.isCloned() for p in root.self_and_parents()])
            # g.trace(isCloned,root.h)
            if isCloned:
                for p in c.all_positions():
                    if p.isAnyAtFileNode():
                        isAncestor = any([z.v == root.v for z in p.self_and_subtree()])
                        # g.trace(isAncestor,p.h)
                        if isAncestor and self.check(p, rc_fn):
                            break
        if self.wait:
            g.es_print('pylint done %s' % g.timeSince(t1))
    #@+node:ekr.20150514125218.12: *3* pylint.run_pylint
    def run_pylint(self, fn, rc_fn):
        '''Run pylint on fn with the given pylint configuration file.'''
        trace = False and not g.unitTesting
        global g_pylint_fn, g_pylint_list, g_pylint_pid
        if not os.path.exists(fn):
            print('file not found:', fn)
            return
        if 1: # Invoke pylint directly.
            # Escaping args is harder here because we are creating an args array.
            is_win = sys.platform.startswith('win')
            args =  ','.join(["'--rcfile=%s'" % (rc_fn), "'%s'" % (fn),])
            if is_win:
                args = args.replace('\\','\\\\')
            command = '%s -c "from pylint import lint; args=[%s]; lint.Run(args)"' % (
                sys.executable, args)
            if not is_win:
                command = shlex.split(command)
        else:
            # Invoke g.run_pylint.
            args = ["fn=r'%s'" % (fn), "rc=r'%s'" % (rc_fn),]
            # When shell is True, it's recommended to pass a string, not a sequence.
            command = '%s -c "import leo.core.leoGlobals as g; g.run_pylint(%s)"' % (
                sys.executable, ','.join(args))
        if self.wait:
            g.es_print(g.shortFileName(fn))
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                shell=False,
                universal_newlines=True, # Converts stdout to unicode
            )
            stdout_data, stderr_data = proc.communicate()
            for s in g.splitLines(stdout_data):
                if s.strip():
                    g.es_print(s.rstrip())
        elif g_pylint_pid:
            # A pylint checker is already active.
            if trace: g.trace('===== Adding callback', g.shortFileName(fn))

            def pylint_callback(fn=fn):
                global g_pylint_fn, g_pylint_list, g_pylint_pid
                g_pylint_fn = fn
                g.es_print(g.shortFileName(fn))
                if g_pylint_pid:
                    if trace: g.es_print('===== Killing:', g_pylint_pid)
                    g_pylint_pid.kill()
                g_pylint_pid = subprocess.Popen(
                    command,
                    shell=False,
                    universal_newlines=True,
                )
                if trace: g.es_print('===== Starting:',
                    g.shortFileName(fn), g_pylint_pid)

            g_pylint_list.append(pylint_callback)
        else:
            g_pylint_pid = subprocess.Popen(
                command,
                shell=False,
                universal_newlines=True,
            )
            if trace: g.es_print('===== Starting:',
                g.shortFileName(fn), g_pylint_pid)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@-leo

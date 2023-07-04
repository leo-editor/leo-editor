#@+leo-ver=5-thin
#@+node:ekr.20161021090740.1: * @file ../commands/checkerCommands.py
"""Commands that invoke external checkers"""
#@+<< checkerCommands imports >>
#@+node:ekr.20161021092038.1: ** << checkerCommands imports >>
from __future__ import annotations
import os
import re
import shlex
import sys
import tempfile
import time
from typing import Any, Optional, TYPE_CHECKING
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
#@+<< checkerCommands annotations >>
#@+node:ekr.20220826075856.1: ** << checkerCommands annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
Event = Any
#@-<< checkerCommands annotations >>
#@+others
#@+node:ekr.20161021091557.1: **  Commands
#@+node:ekr.20230104132446.1: *3* check-nodes
@g.command('check-nodes')
def check_nodes(event: Event) -> None:
    """
    Find **dubious* nodes, that is, nodes that:

    - contain multiple defs.
    - start with leading blank lines.
    - are non-organizer nodes containing no body text.

    Especially useful when using @clean nodes in a collaborative
    environment. Leo's @clean update algorithm will update @clean nodes
    when others have added, deleted or moved code, but the update algorithm
    won't assign changed code to the optimal nodes. This script highligts
    nodes that needed attention.

    Settings: You can customize the behavior of this command with @data nodes:

    - @data check-nodes-ok-patterns

      The body of the @data node contains a list of regexes (strings), one per line.
      This command compiles each regex as if it were a raw string.
      Headlines matching any of these compiled regexes are not considered dubious.
      The defaults ignore unit tests::
        .*test_
        .*Test

    - @data check-nodes-ok-prefixes

      The body ot the @data node contains a list of strings, one per line.
      Headlines starting with any of these strings are not considered dubious.
      The defaults ignore top-level @<file> nodes and marker nodes::

        @
        **
        ==
        --

    - @data check-nodes-suppressions

      The body ot the @data node contains a list of strings, one per line.
      Headlines that match these suppressions *exactly* are not considered dubious.
      Default: None.
    """
    CheckNodes().check(event)
#@+node:ekr.20190608084751.1: *3* find-long-lines
@g.command('find-long-lines')
def find_long_lines(event: Event) -> None:
    """
    Report long lines in c.p's tree.
    Generate clickable links in the log.
    """
    c = event and event.get('c')
    if not c:
        return
    #@+others # helper functions
    #@+node:ekr.20190609135639.1: *4* function: get_root
    def get_root(p: Position) -> Optional[Position]:
        """Return True if p is any @<file> node."""
        for parent in p.self_and_parents():
            if parent.anyAtFileNodeName():
                return parent
        return None
    #@+node:ekr.20190608084751.2: *4* function: in_no_pylint
    def in_nopylint(p: Position) -> bool:
        """Return p if p is controlled by @nopylint."""
        for parent in p.self_and_parents():
            if '@nopylint' in parent.h:
                return True
        return False
    #@-others
    log = c.frame.log
    max_line = c.config.getInt('max-find-long-lines-length') or 110
    count, files, ignore = 0, [], []
    for p in c.p.self_and_subtree():
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
def find_missing_docstrings(event: Event) -> None:
    """Report missing docstrings in the log, with clickable links."""
    c = event and event.get('c')
    if not c:
        return
    #@+others # Define functions
    #@+node:ekr.20190615181104.1: *4* function: has_docstring
    def has_docstring(lines: list[str], n: int) -> bool:
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
    def is_a_definition(line: Any) -> bool:
        """Return True if line is a definition line."""
        # By Виталије Милошевић.
        # It may be useful to skip __init__ methods because their docstring
        # is usually docstring of the class
        return (
            line.startswith(('def ', 'class ')) and
            not line.partition(' ')[2].startswith('__init__')
        )
    #@+node:ekr.20190615182754.1: *4* function: is_root
    def is_root(p: Position) -> bool:
        """
        A predicate returning True if p is an @<file> node that is not under @nopylint.
        """
        for parent in p.self_and_parents():
            if g.match_word(parent.h, 0, '@nopylint'):
                return False
        return p.isAnyAtFileNode() and p.h.strip().endswith(('py', 'pyw'))
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
def flake8_command(event: Event) -> None:
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
        path = c.fullPath(root)
        if path and os.path.exists(path):
            # g.es_print(f"{tag}: {path}")
            g.execute_shell_commands(f'&"{python}" -m flake8 "{path}"')
        else:
            g.es_print(f"{tag}: file not found:{path}")
#@+node:ekr.20161026092059.1: *3* kill-pylint
@g.command('kill-pylint')
@g.command('pylint-kill')
def kill_pylint(event: Event) -> None:
    """Kill any running pylint processes and clear the queue."""
    g.app.backgroundProcessManager.kill('pylint')
#@+node:ekr.20210302111730.1: *3* mypy command
@g.command('mypy')
def mypy_command(event: Event) -> None:
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
def pyflakes_command(event: Event) -> None:
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
last_pylint_path: str = None

@g.command('pylint')
def pylint_command(event: Event) -> None:
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
            path, p = data  # pylint: disable=unpacking-non-sequence
            last_pylint_path = path
#@+node:ekr.20230221105941.1: ** class CheckNodes
class CheckNodes:

    def_pattern = re.compile(r'^def\b')
    ok_head_patterns: list[re.Pattern]
    ok_head_prefixes: list[str]
    suppressions: list[str]

    #@+others
    #@+node:ekr.20230221110024.1: *3* CheckNodes.check
    def check(self, event: Event) -> None:

        self.c = c = event and event.get('c')
        if not c:
            return
        self.get_data()
        self.clones = [z.copy() for z in c.all_unique_positions() if self.is_dubious_node(z)]
        # Report.
        self.count = count = len(self.clones)
        g.es(f"{count} dubious node{g.plural(count)}")
        if not count:
            return
        dubious = self.create_dubious_nodes()
        c.setChanged()
        c.selectPosition(dubious)
        c.redraw()
    #@+node:ekr.20230104142059.1: *3* CheckNodes.create_dubious_nodes
    def create_dubious_nodes(self) -> Position:
        c = self.c
        u = c.undoer
        # Create the top-level node.
        undoData = u.beforeInsertNode(c.p)
        dubious = c.lastTopLevel().insertAfter()
        dubious.h = f"{self.count} dubious nodes{g.plural(self.count)}"
        # Clone nodes as children of the top-level node.
        for p in self.clones:
            # Create the clone directly as a child of found.
            p2 = p.copy()
            n = dubious.numberOfChildren()
            p2._linkCopiedAsNthChild(dubious, n)
        # Sort the clones in place, without undo.
        dubious.v.children.sort(key=lambda v: v.h.lower())
        u.afterInsertNode(dubious, 'check-nodes', undoData)
        return dubious
    #@+node:ekr.20230104142418.1: *3* CheckNodes.get_data
    def get_data(self) -> None:
        """
        Get user data from @data nodes.
        """
        c = self.c
        self.ok_head_prefixes = c.config.getData('check-nodes-ok-prefixes') or []
        self.suppressions = c.config.getData('check-nodes-suppressions') or []
        # Compile all regex patterns.
        self.ok_head_patterns = []
        for s in c.config.getData('check-nodes-ok-patterns') or []:
            try:
                self.ok_head_patterns.append(re.compile(fr"{s}"))
            except Exception:
                g.es_print('Bad pattern in @data check-nodes-ok-patterns')
                g.es_print(repr(s))

    #@+node:ekr.20230104141545.1: *3* CheckNodes.is_dubious_node
    def is_dubious_node(self, p: Position) -> bool:

        lines = p.b.splitlines()
        stripped_lines = p.b.strip().splitlines()
        too_many_defs = (
            p.h not in self.suppressions
            and not p.h.startswith('class') and '@others' not in p.b
            and not any(z.match(p.h) for z in self.ok_head_patterns)
            and sum(1 for s in lines if self.def_pattern.match(s)) > 1
        )
        leading_blank_line = p.b.strip() and not lines[0].strip()
        empty_body = (
            not p.b.strip()
            and not p.hasChildren()
            and not any(p.h.startswith(z) for z in self.ok_head_prefixes)
        )
        trailing_class_or_def = (
            len(stripped_lines) > 1
            and stripped_lines[-1].startswith(('class ', 'def '))
        )
        return any((too_many_defs, leading_blank_line, empty_body, trailing_class_or_def))
    #@-others
#@+node:ekr.20210302111917.1: ** class MypyCommand
class MypyCommand:
    """A class to run mypy on all Python @<file> nodes in c.p's tree."""

    # See g.mypy_pat for the regex that creates clickable links.

    def __init__(self, c: Cmdr) -> None:
        """ctor for MypyCommand class."""
        self.c = c
        self.link_limit = None  # Set in check_file.
        self.unknown_path_names: list[str] = []

    #@+others
    #@+node:ekr.20210302111935.3: *3* mypy.check_all
    def check_all(self, roots: Any) -> None:
        """Run mypy on all files in paths."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        self.unknown_path_names = []
        for root in roots:
            fn = os.path.normpath(c.fullPath(root))
            self.check_file(fn, root)
    #@+node:ekr.20210727212625.1: *3* mypy.check_file
    def check_file(self, fn: str, root: Position) -> None:
        """Run mypy on one file."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        command = f"{sys.executable} -m mypy {fn}".split()
        bpm = g.app.backgroundProcessManager
        bpm.start_process(c, command, fn=fn, kind='mypy')
    #@+node:ekr.20210302111935.7: *3* mypy.run (entry)
    def run(self, p: Position) -> None:
        """Run mypy on all Python @<file> nodes in c.p's tree."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        root = p.copy()
        # Make sure the parent of the leo directory is on sys.path.
        path = os.path.normpath(os.path.join(g.app.loadDir, '..', '..'))
        if path not in sys.path:
            sys.path.insert(0, path)
        roots = g.findRootsWithPredicate(c, root, predicate=None)
        self.check_all(roots)
    #@-others
#@+node:ekr.20221128123238.1: ** class Flake8Command
class Flake8Command:
    """A class to run flake8 on all Python @<file> nodes in c.p's tree."""

    def __init__(self, c: Cmdr) -> None:
        """ctor for Flake8Command class."""
        self.c = c
        self.seen: list[str] = []  # List of checked paths.

    #@+others
    #@+node:ekr.20221128123523.3: *3* flake8.check_all
    def check_all(self, roots: list[Position]) -> None:
        """Run flake8 on all files in paths."""
        c, tag = self.c, 'flake8'
        for root in roots:
            path = c.fullPath(root)
            if path and os.path.exists(path):
                # g.es_print(f"{tag}: {path}")
                g.execute_shell_commands(f'&"{sys.executable}" -m flake8 "{path}"')
            else:
                g.es_print(f"{tag}: file not found: {path}")

    #@+node:ekr.20221128123523.6: *3* flake8.run
    def run(self, p: Position) -> None:
        """
        Run flake8 on all Python @<file> nodes in p's tree.
        """
        c, root = self.c, p
        if not flake8:
            return
        # Make sure the parent of the leo directory is on sys.path.
        path = os.path.normpath(os.path.join(g.app.loadDir, '..', '..'))
        if path not in sys.path:
            sys.path.insert(0, path)
        roots = g.findRootsWithPredicate(c, root, predicate=None)
        if roots:
            self.check_all(roots)
    #@-others
#@+node:ekr.20160516072613.2: ** class PyflakesCommand
class PyflakesCommand:
    """A class to run pyflakes on all Python @<file> nodes in c.p's tree."""

    def __init__(self, c: Cmdr) -> None:
        """ctor for PyflakesCommand class."""
        self.c = c
        self.seen: list[str] = []  # List of checked paths.

    #@+others
    #@+node:ekr.20171228013818.1: *3* class PyflakesCommand.LogStream
    class LogStream:

        """A log stream for pyflakes."""

        def __init__(self, fn_n: int = 0, roots: list[Position] = None) -> None:
            self.fn_n = fn_n
            self.roots = roots

        def write(self, s: str) -> None:
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
    def check_all(self, roots: list[Position]) -> int:
        """Run pyflakes on all files in paths."""
        c = self.c
        total_errors = 0
        for i, root in enumerate(roots):
            fn = os.path.normpath(c.fullPath(root))
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
                errors = api.check(g.toUnicode(s), sfn, r)
                total_errors += errors
        return total_errors
    #@+node:ekr.20171228013625.1: *3* pyflakes.check_script
    def check_script(self, p: Position, script: str) -> bool:
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
    #@+node:ekr.20160516072613.5: *3* pyflakes.run
    def run(self, p: Position) -> bool:
        """Run Pyflakes on all Python @<file> nodes in p's tree."""
        c, root = self.c, p
        if not pyflakes:
            return True
        # Make sure the parent of the leo directory is on sys.path.
        path = os.path.normpath(os.path.join(g.app.loadDir, '..', '..'))
        if path not in sys.path:
            sys.path.insert(0, path)
        roots = g.findRootsWithPredicate(c, root, predicate=None)
        if not roots:
            return True
        total_errors = self.check_all(roots)
        if total_errors > 0:
            # This message is important for clarity.
            g.es(f"ERROR: pyflakes: {total_errors} error{g.plural(total_errors)}")
        return total_errors == 0
    #@-others
#@+node:ekr.20150514125218.8: ** class PylintCommand
class PylintCommand:
    """A class to run pylint on all Python @<file> nodes in c.p's tree."""

    def __init__(self, c: Cmdr) -> None:
        self.c = c
        self.rc_fn: str = None  # Name of the rc file.
    #@+others
    #@+node:ekr.20150514125218.11: *3* 1. pylint.run
    def run(self, last_path: str = None) -> Optional[tuple[str, Position]]:
        """Run Pylint on all Python @<file> nodes in c.p's tree."""
        c, root = self.c, self.c.p
        if not lint:
            g.es_print('pylint is not installed')
            return None
        self.rc_fn = self.get_rc_file()
        if not self.rc_fn:
            return None
        # Make sure the parent of the leo directory is on sys.path.
        path = os.path.normpath(os.path.join(g.app.loadDir, '..', '..'))
        if path not in sys.path:
            sys.path.insert(0, path)

        # Ignore @nopylint trees.
        def predicate(p: Position) -> bool:
            for parent in p.self_and_parents():
                if g.match_word(parent.h, 0, '@nopylint'):
                    return False
            return p.isAnyAtFileNode() and p.h.strip().endswith(('.py', '.pyw'))  # #2354.

        data: list[tuple[str, Position]] = []
        is_at_file = False
        roots = g.findRootsWithPredicate(c, root, predicate=predicate)
        if roots:
            roots = g.findRootsWithPredicate(c, root, predicate=predicate)
            data = [(self.get_fn(p), p.copy()) for p in roots]
            data = [z for z in data if z[0] is not None]
            is_at_file = True
        else:
            last_path = None
        if not data:
            if last_path:
                # Default to the last path.
                fn = last_path
                for p in c.all_positions():
                    if p.isAnyAtFileNode() and c.fullPath(p) == fn:
                        data = [(fn, p.copy())]
                        break
            else:
                g.trace('pylint: not an external file, using temp file')
                script = g.getScript(c, c.p, False, False)
                fd, fn = tempfile.mkstemp(suffix='.py', prefix="")
                with os.fdopen(fd, 'w') as f:
                    f.write(script)
                data = [(fn, c.p.copy())]

        for fn, p in data:
            self.run_pylint(fn, p)
        # #1808: return the last data file.
        return data[-1] if data and is_at_file else None
    #@+node:ekr.20150514125218.10: *3* 3. pylint.get_rc_file
    def get_rc_file(self) -> Optional[str]:
        """Return the path to the pylint configuration file."""
        c = self.c
        base1 = '.pylintrc'  # Standard name.
        base2 = 'pylint-leo-rc.txt'  # Leo-centric name
        local_dir = g.os_path_dirname(c.fileName())
        table = (
            # In the directory containing the outline.
            g.finalize_join(local_dir, base1),
            g.finalize_join(local_dir, base2),
            # In ~/.leo
            g.finalize_join(g.app.homeDir, '.leo', base1),
            g.finalize_join(g.app.homeDir, '.leo', base2),
            # In leo/test
            g.finalize_join(g.app.loadDir, '..', '..', 'leo', 'test', base2),
            g.finalize_join(g.app.loadDir, '..', '..', 'leo', 'test', base2),
        )
        for fn in table:
            fn = g.os_path_abspath(fn)
            if g.os_path_exists(fn):
                print(f"pylint: {fn}")
                return fn
        table_s = '\n'.join(table)
        g.es_print(f"no pylint configuration file found in\n{table_s}")
        # g.es_print('Not found: .pylintrc and pylint-leo-rc.txt')
        return None
    #@+node:ekr.20150514125218.9: *3* 4. pylint.get_fn
    def get_fn(self, p: Position) -> Optional[str]:
        """
        Finalize p's file name.
        Return if p is not an @file node for a python file.
        """
        c = self.c
        fn = p.isAnyAtFileNode()
        if not fn:
            g.trace(f"not an @<file> node: {p.h!r}")
            return None
        return c.fullPath(p)  # #1914
    #@+node:ekr.20150514125218.12: *3* 5. pylint.run_pylint
    def run_pylint(self, fn: str, p: Position) -> None:
        """Run pylint on fn with the given pylint configuration file."""
        c, rc_fn = self.c, self.rc_fn

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
        bpm.start_process(c, command, fn=fn, kind='pylint')
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@-leo

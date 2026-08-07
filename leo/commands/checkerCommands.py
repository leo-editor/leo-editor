# @+leo-ver=5-thin
# @+node:ekr.20161021090740.1: * @file ../commands/checkerCommands.py
"""Commands that invoke external checkers"""

# @+<< checkerCommands imports >>
# @+node:ekr.20161021092038.1: ** << checkerCommands imports >>
from __future__ import annotations
import os
import re
import subprocess
import sys
import time
from typing import TYPE_CHECKING

# Third-party imports.
try:
    import mypy
    from mypy import api as mypy_api
except Exception:
    mypy = None  # type:ignore
    mypy_api = None  # type:ignore

try:
    import ruff
except Exception:
    ruff = None  # type:ignore

# Leo imports.
from leo.core import leoGlobals as g

# @-<< checkerCommands imports >>
# @+<< checkerCommands annotations >>
# @+node:ekr.20220826075856.1: ** << checkerCommands annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position


# @-<< checkerCommands annotations >>
# @+others
# @+node:ekr.20161021091557.1: **  Commands
# @+node:ekr.20230104132446.1: *3* check-nodes
@g.command('check-nodes')
def check_nodes(event: LeoKeyEvent | None = None) -> None:
    """
    Find **dubious* nodes, that is, nodes that:

    - contain multiple defs.
    - start with leading blank lines.
    - are non-organizer nodes containing no body text.

    Especially useful when using @clean nodes in a collaborative
    environment. Leo's @clean update algorithm will update @clean nodes
    when others have added, deleted or moved code, but the update algorithm
    won't assign changed code to the optimal nodes. This script highlights
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

      The body of the @data node contains a list of strings, one per line.
      Headlines starting with any of these strings are not considered dubious.
      The defaults ignore top-level @<file> nodes and marker nodes::

        @
        **
        ==
        --

    - @data check-nodes-suppressions

      The body of the @data node contains a list of strings, one per line.
      Headlines that match these suppressions *exactly* are not considered dubious.
      Default: None.
    """
    c = event.c if event else None
    if not c:
        return
    CheckNodes(c).check(event)


# @+node:ekr.20190608084751.1: *3* find-long-lines
@g.command('find-long-lines')
def find_long_lines(event: LeoKeyEvent | None = None) -> None:
    """
    Report long lines in c.p's tree.
    Generate clickable links in the log.
    """
    c = event.c if event else None
    if not c:
        return

    # @+others # helper functions
    # @+node:ekr.20190609135639.1: *4* function: get_root
    def get_root(p: Position) -> Position | None:
        """Return True if p is any @<file> node."""
        for parent in p.self_and_parents():
            if parent.anyAtFileNodeName():
                return parent
        return None

    # @+node:ekr.20190608084751.2: *4* function: in_no_pylint
    def in_nopylint(p: Position) -> bool:
        """Return p if p is controlled by @nopylint."""
        for parent in p.self_and_parents():
            if '@nopylint' in parent.h:
                return True
        return False

    # @-others
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
        f"{len(files)} file{g.plural(len(files))}"
    )


# @+node:ekr.20190615180048.1: *3* find-missing-docstrings
@g.command('find-missing-docstrings')
def find_missing_docstrings(event: LeoKeyEvent | None = None) -> None:
    """Report missing docstrings in the log, with clickable links."""
    c = event.c if event else None
    if not c:
        return

    # @+others # Define functions
    # @+node:ekr.20190615181104.1: *4* function: has_docstring
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

    # @+node:ekr.20190615181104.2: *4* function: is_a_definition
    def is_a_definition(line: str) -> bool:
        """Return True if line is a definition line."""
        # By Виталије Милошевић.
        # It may be useful to skip __init__ methods because their docstring
        # is usually docstring of the class
        return (
            line.startswith(('def ', 'class '))
            and not line.partition(' ')[2].startswith('__init__')
        )  # fmt: skip

    # @+node:ekr.20190615182754.1: *4* function: is_root
    def is_root(p: Position) -> bool:
        """
        A predicate returning True if p is an @<file> node that is not under @nopylint.
        """
        for parent in p.self_and_parents():
            if g.match_word(parent.h, 0, '@nopylint'):
                return False
        return p.isAnyAtFileNode() and p.h.strip().endswith(('py', 'pyw'))

    # @-others
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
        f"in {time.process_time() - t1:5.2f} sec."
    )


# @+node:ekr.20210302111730.1: *3* mypy command
@g.command('mypy')
def mypy_command(event: LeoKeyEvent | None = None) -> None:
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
    c = event.c if event else None
    if not c:
        return
    if c.isChanged():
        c.save()
    if mypy_api:
        MypyCommand(c).run(c.p)
    else:
        g.es_print('can not import mypy')


# @+node:vv.20260807120000.1: *3* ruff command
@g.command('ruff')
def ruff_command(event: LeoKeyEvent | None = None) -> None:
    """
    Run ruff on all @<file> nodes of the selected tree, or the first
    @<file> node in an ancestor.

    Unlike running ruff outside of Leo, Leo's ruff command creates
    clickable links in Leo's log pane for each error. See g.ruff_pat.
    """
    c = event.c if event else None
    if not c:
        return
    if c.isChanged():
        c.save()
    if ruff:
        RuffCommand(c).run(c.p)
    else:
        g.es_print('can not import ruff')


# @+node:ekr.20230221105941.1: ** class CheckNodes
class CheckNodes:
    def_pattern = re.compile(r'^def\b')
    ok_head_patterns: list[re.Pattern]
    ok_head_prefixes: list[str]
    suppressions: list[str]

    def __init__(self, c: Cmdr) -> None:
        """ctor for CheckNodes class."""
        self.c = c

    # @+others
    # @+node:ekr.20230221110024.1: *3* CheckNodes.check
    def check(self, event: LeoKeyEvent | None = None) -> None:
        c = self.c
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

    # @+node:ekr.20230104142059.1: *3* CheckNodes.create_dubious_nodes
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

    # @+node:ekr.20230104142418.1: *3* CheckNodes.get_data
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
                self.ok_head_patterns.append(re.compile(rf"{s}"))
            except Exception:
                g.es_print('Bad pattern in @data check-nodes-ok-patterns')
                g.es_print(repr(s))

    # @+node:ekr.20230104141545.1: *3* CheckNodes.is_dubious_node
    def is_dubious_node(self, p: Position) -> bool:
        lines = p.b.splitlines()
        stripped_lines = p.b.strip().splitlines()
        too_many_defs = (
            p.h not in self.suppressions
            and not p.h.startswith('class')
            and '@others' not in p.b
            and not any(z.match(p.h) for z in self.ok_head_patterns)
            and sum(1 for s in lines if self.def_pattern.match(s)) > 1
        )
        leading_blank_line = p.b.strip() and not lines[0].strip()
        empty_body = (
            not p.b.strip()
            and not p.hasChildren()
            and not any(p.h.startswith(z)
            for z in self.ok_head_prefixes)
        )  # fmt: skip
        trailing_class_or_def = (
            len(stripped_lines) > 1
            and stripped_lines[-1].startswith(('class ', 'def '))
        )  # fmt: skip
        return any((too_many_defs, leading_blank_line, empty_body, trailing_class_or_def))

    # @-others


# @+node:ekr.20210302111917.1: ** class MypyCommand
class MypyCommand:
    """A class to run mypy on all Python @<file> nodes in c.p's tree."""

    # See g.mypy_pat for the regex that creates clickable links.

    def __init__(self, c: Cmdr) -> None:
        """ctor for MypyCommand class."""
        self.c = c
        self.link_limit = None  # Set in check_file.
        self.unknown_path_names: list[str] = []

    # @+others
    # @+node:ekr.20210302111935.3: *3* mypy.check_all
    def check_all(self, roots: list[Position]) -> None:
        """Run mypy on all files in paths."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        self.unknown_path_names = []
        for root in roots:
            fn = os.path.normpath(c.fullPath(root))
            self.check_file(fn, root)

    # @+node:ekr.20210727212625.1: *3* mypy.check_file
    def check_file(self, fn: str, root: Position) -> None:
        """Run mypy on one file."""
        c = self.c
        if not mypy:
            print('install mypy with `pip install mypy`')
            return
        command = f"{sys.executable} -m mypy {fn}"
        bpm = g.app.backgroundProcessManager
        bpm.start_process(c, command, fn=fn, kind='mypy')

    # @+node:ekr.20210302111935.7: *3* mypy.run (entry)
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

    # @-others


# @+node:vv.20260807120000.2: ** class RuffCommand
class RuffCommand:
    """A class to run ruff on all Python @<file> nodes in c.p's tree."""

    # See g.ruff_pat for the regex that creates clickable links.

    def __init__(self, c: Cmdr) -> None:
        """ctor for RuffCommand class."""
        self.c = c

    # @+others
    # @+node:vv.20260807120000.3: *3* ruff.check_all
    def check_all(self, roots: list[Position]) -> None:
        """Run ruff on all files in roots."""
        c = self.c
        for root in roots:
            fn = os.path.normpath(c.fullPath(root))
            self.check_file(fn, root)

    # @+node:vv.20260807120000.4: *3* ruff.check_file
    def check_file(self, fn: str, root: Position) -> None:
        """Run ruff on one file."""
        c = self.c
        if not ruff:
            print('install ruff with `pip install ruff`')
            return
        command = f"{sys.executable} -m ruff check --output-format=concise {fn}"
        bpm = g.app.backgroundProcessManager
        bpm.start_process(c, command, fn=fn, kind='ruff')

    # @+node:vv.20260807120000.5: *3* ruff.run (entry)
    def run(self, p: Position) -> None:
        """Run ruff on all Python @<file> nodes in c.p's tree."""
        c = self.c
        if not ruff:
            print('install ruff with `pip install ruff`')
            return
        root = p.copy()
        # Make sure the parent of the leo directory is on sys.path.
        path = os.path.normpath(os.path.join(g.app.loadDir, '..', '..'))
        if path not in sys.path:
            sys.path.insert(0, path)
        roots = g.findRootsWithPredicate(c, root, predicate=None)
        self.check_all(roots)

    # @+node:vv.20260807120000.6: *3* ruff.check_on_write (sync, for on-write checking)
    def check_on_write(self, root: Position) -> bool:
        """
        Run ruff synchronously on root's file. Return True if ruff reports no errors.

        Unlike check_file (which uses the BackgroundProcessManager so the GUI
        doesn't block while checking a whole tree), this runs in the foreground:
        it's used for run-ruff-on-write, which checks a single just-saved file
        and needs a real pass/fail result before the write completes.
        """
        c = self.c
        if not ruff:
            return True
        fn = os.path.normpath(c.fullPath(root))
        command = [sys.executable, '-m', 'ruff', 'check', '--output-format=concise', fn]
        result = subprocess.run(command, capture_output=True, text=True)
        s = (result.stdout + result.stderr).strip()
        if s:
            if not c.frame.log.put_html_links(s):
                g.es(s)
        return result.returncode == 0

    # @-others


# @-others
# @@language python
# @@tabwidth -4
# @@pagewidth 70

# @-leo

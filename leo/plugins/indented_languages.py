#@+leo-ver=5-thin
#@+node:ekr.20230917013414.1: * @file ../plugins/indented_languages.py
"""
A plugin that creates **study outlines** in which indentation replaces curly brackets.
"""
import re
from typing import Any, Optional
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
from leo.plugins.importers.c import C_Importer
from leo.plugins.importers.elisp import Elisp_Importer
from leo.plugins.importers.typescript import TS_Importer

#@+others
#@+node:ekr.20230917084259.1: ** top-level
#@+node:ekr.20230917015308.1: *3* init (indented_languages.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    # g.registerHandler('after-create-leo-frame', onCreate)
    # g.registerHandler('after-reading-external-file', onAfterRead)
    # g.registerHandler('before-writing-external-file', onBeforeWrite)
    return True
#@+node:ekr.20231022071443.1: *3* commands (indented_languages.py)
@g.command('import-to-indented-c')
def import_to_indented_c(event: Any) -> None:
    """The import-to-indented-c command."""
    c = event.get('c')
    if c:
        Indented_C(c).do_import()

@g.command('import-to-indented-elisp')
def import_to_indented_elisp(event: Any) -> None:
    """The import-to-indented-elisp command."""
    c = event.get('c')
    if c:
        Indented_Lisp(c).do_import()

@g.command('import-to-indented-typescript')
def import_to_indented_typescript(event: Any) -> None:
    """The import-to-indented-typescript command."""
    c = event.get('c')
    if c:
        Indented_TypeScript(c).do_import()


#@+node:ekr.20231022073438.1: **  class Indented_Importer
class Indented_Importer:
    """The base class for all indented importers."""

    extentions: list[str] = None  # The file extension for the language.
    language: str = None  # The name of the language.
    importer_class: Any = None  # The importer class

    def __init__(self, c):
        self.c = c
        self.importer = self.importer_class(c)  # pylint: disable=not-callable

    #@+others
    #@+node:ekr.20231022073537.1: *3* indented_i.do_import (driver)
    def do_import(self) -> Optional[Position]:
        """
        Base_Indented_Importer.do_import: Create a top-level node containing study outlines for all files in
        c.p and its descendants.

        Return the top-level node for unit tests.
        """
        c, p, u = self.c, self.c.p, self.c.undoer

        assert self.extentions

        def predicate(p: Position) -> bool:
            return self.isAtFileNode(p) and p.h.strip().endswith(tuple(self.extentions))

        roots: list[Position] = g.findRootsWithPredicate(c, p, predicate)  # Removes duplicates
        if not roots:
            return None

        # Undoably create top-level organizer node and import all files.
        try:
            ### g.app.disable_redraw = True
            last = c.lastTopLevel()
            c.selectPosition(last)
            undoData = u.beforeInsertNode(last)
            # Always create a new last top-level node.
            parent = last.insertAfter()
            parent.v.h = 'indented files'
            for root in roots:
                self.import_one_file(root, parent)
            u.afterInsertNode(parent, 'recursive-import', undoData)
        except Exception:
            g.es_print(f"Exception in {self.__class__.__name__}")
            g.es_exception()
        finally:
            ### g.app.disable_redraw = False
            for p2 in parent.self_and_subtree(copy=False):
                p2.contract()
            c.redraw(parent)
        return parent
    #@+node:ekr.20231022100000.1: *3* indented_i.import_one_file
    def import_one_file(self, p: Position, parent: Position) -> None:
        """
        Indented_Importer.import_one_file: common setup code.

        p is an @<file> node.

        - Create a parallel tree as the last child of parent.
        - Indent all the nodes of the parallel tree.
        """
        file_name = self.atFileName(p)

        # Create root, a parallel outline.
        root = p.copyWithNewVnodes()
        n = parent.numberOfChildren()
        root._linkAsNthChild(parent, n)
        root.h = file_name

        # Indent the parallel outline.
        self.indent_outline(root)
    #@+node:ekr.20231022073306.6: *3* indented_i.indent_node
    curlies_pat = re.compile(r'{|}')
    close_curly_pat = re.compile(r'}')
    semicolon_pat = re.compile(r'}\s*;')

    def indent_node(self, p: Position) -> None:
        """
        Remove curly brackets from p.b.

        Do not remove matching brackets if ';' follows the closing bracket.
        """

        tag=f"{g.my_name()}"

        lines = g.splitLines(p.b)
        guide_lines = self.importer.make_guide_lines(lines)

        ### g.printObj(guide_lines, tag=f"{g.my_name()}: guide_lines for {p.h}")

        # The stack contains tuples(curly_bracket, line_number, column_number) for each curly bracket.
        # Note: adding a 'level' entry to these tuples would be tricky.
        stack: list[tuple[str, int, int]] = []
        info: dict[tuple, tuple] = {}  # Keys and values are tuples, as above.

        # Pass 1: Create the info dict.
        level = 0  # To check for unmatched braces.
        for line_number, line in enumerate(guide_lines):
            last_column = 0
            for m in re.finditer(self.curlies_pat, line):
                curly = m.group(0)
                column_number = m.start()
                assert last_column == 0 or last_column < column_number, f"{tag} unexpected column"
                assert 0 <= column_number < len(line), f"{tag} column out of range"
                last_column = column_number
                # g.trace(f" {curly} level: {level} column: {column_number:3} line: {line_number:3} {line!r}")
                if curly == '{':
                    stack.append((curly, line_number, column_number))
                else:
                    assert curly == '}', f"{tag}: not }}"
                    assert stack, f"{tag}: stack underflow"
                    top = stack.pop()
                    top_curly, top_line_number, top_column_number = top
                    assert top_curly == '{', f"{tag} stack mismatch"
                    this_info = (curly, line_number, column_number)
                    info [top] = this_info
                    info [this_info] = top
                level += (1 if curly == '{' else -1)
        assert level == 0, f"{tag} unmatched brackets"

        # Pass 2: Make the substitutions when '}' is seen.
        result_lines = []  # Must be empty here.
        for line_number, line in enumerate(guide_lines):

            if '}' not in line:
                # No substitution is possible.
                result_lines.append(lines[line_number])
                continue

            # Don't make the substitution if '};' appears on the line.
            if self.semicolon_pat.search(line):
                # g.trace('Skip };', repr(line))
                result_lines.append(lines[line_number])
                continue

            for m in re.finditer(self.close_curly_pat, line):
                column_number = m.start()
                this_info = ('}', line_number, column_number)
                assert this_info in info, f"no matching info: {this_info}"
                match_curly, match_line, match_column = info [this_info]
                assert match_curly == '{', f"{tag}: wrong matching curly bracket"

                # Don't make the substitution if the match is on the same line.
                if match_line == line_number:
                    # g.trace('Same line', repr(line))
                    result_lines.append(lines[line_number])
                    break

                if 0:
                    print('')
                    print(f"{tag} Remove")
                    print(f"matching: {{ line: {match_line:3} column: {match_column:2} {guide_lines[match_line]!r}")
                    print(f"    this: }} line: {line_number:3} column: {column_number:2} {line!r}")

                # Replace the previous line in result_lines, *not* lines.
                s = result_lines[match_line]
                new_line = s[:match_column] + ' ' + s[match_column + 1:]
                result_lines[match_line] = new_line.rstrip() + '\n' if new_line.strip() else '\n'

                # Append this *real* line to result_lines.
                s = lines[line_number]
                this_line = s[:column_number] + ' ' + s[column_number + 1:]
                result_lines.append(this_line.rstrip() + '\n' if this_line.strip() else '\n')

        # Remove multiple blank lines. Some will be added later.
        new_result_lines: list[str] = []
        for i, line in enumerate(result_lines):
            if 0 < i - 1 < len(new_result_lines) and line == '\n' and new_result_lines[i-1] == '\n':
                pass
            else:
                new_result_lines.append(line)
        result_lines = new_result_lines

        # Set the result
        p.b = ''.join(result_lines).rstrip() + '\n\n'
    #@+node:ekr.20231022073306.3: *3* indented_i.indent_outline
    def indent_outline(self, root: Position) -> None:
        """
        Indent the body text of root and all its descendants.
        """
        for p in root.self_and_subtree():
            self.indent_node(p)
    #@+node:ekr.20231022150031.1: *3* indented_i.isAtFileNode & atFileName
    def isAtFileNode(self, p: Position) -> bool:
        return p.h.startswith(('@@file ', '@@clean ', '@file ', '@clean '))

    def atFileName(self, p: Position) -> str:
        assert self.isAtFileNode(p), repr(p.h)
        i = p.h.find(' ')
        assert i > -1, p.h
        return p.h[i:].strip()
    #@-others
#@+node:ekr.20231022080007.1: ** class Indented_C
class Indented_C(Indented_Importer):
    """A class to support indented C files."""

    extentions: list[str] = ['.c', '.cpp', '.cc']
    importer_class = C_Importer
    language = 'c'
#@+node:ekr.20230917083456.1: ** class Indented_Lisp
class Indented_Lisp(Indented_Importer):
    """A class to support indented Lisp files."""

    extentions: list[str] = ['.el', '.scm']
    importer_class = Elisp_Importer
    language = 'lisp'
#@+node:ekr.20231022073306.1: ** class Indented_TypeScript
class Indented_TypeScript(Indented_Importer):
    """A class to support indented Typescript files."""

    extentions: list[str] = ['.ts',]
    language = 'typescript'
    importer_class = TS_Importer
#@-others
#@-leo

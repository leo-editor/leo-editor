#@+leo-ver=5-thin
#@+node:ekr.20230917013414.1: * @file ../plugins/indented_typescript.py
"""
A plugin to edit typescript files using indentation instead of curly brackets.

- The ``open2`` event handler deletes curly brackets,
  after checking that nothing (except comments?) follows curly brackets.
- The ``read1`` event handler inserts curly brackets based on indentation.

Both event handlers will do a check similar to Python's tabnanny module.
"""
import re
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position, VNode
from leo.plugins.importers.typescript import TS_Importer

#@+others
#@+node:ekr.20230917084259.1: ** top-level (indented_typescript.py)
#@+node:ekr.20230917015308.1: *3* init (indented_typescript.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    g.registerHandler('before-create-leo-frame', onCreate)
    g.registerHandler('after-reading-external-file', onAfterRead)
    g.registerHandler('before-writing-external-file', onBeforeWrite)
    return True
#@+node:ekr.20230917084347.1: *3* event handlers (indented_typescript.py)
def onCreate(tag: str, keys: Any) -> None:
    """Instantiate an IndentedTypeScript instance for c."""
    c=keys.get('c')
    if c:
        gControllers[c.hash()] = IndentedTypeScript(c)
    else:
        g.trace(f"Can not happen. c: {c!r}")

def onAfterRead(tag: str, kwargs: Any) -> None:
    """after-reading-external-file event handler for indented_typescript.py"""
    c, p = kwargs.get('c'), kwargs.get('p')
    if c and p:
        controller = gControllers.get(c.hash())
        controller.after_read(c, p)
    else:
        g.trace(f"Can not happen. c: {c!r} p: {p!r}")

def onBeforeWrite(tag: str, kwargs: Any) -> None:
    """before-writing-external-file event handler for indented_typescript.py"""
    c, p = kwargs.get('c'), kwargs.get('p')
    if c and p:
        controller = gControllers.get(c.hash())
        controller.before_write(c, p)
    else:
        g.trace(f"Can not happen. c: {c!r} p: {p!r}")
#@+node:ekr.20230917083456.1: ** class IndentedTypeScript
class IndentedTypeScript:
    """A class to support indented typescript files."""

    def __init__(self, c: Cmdr) -> None:
        self.c = c
        self.importer = TS_Importer(c)

    #@+others
    #@+node:ekr.20230917091730.1: *3* IndentedTS.after_read
    def after_read(self, c: Cmdr, p: Position) -> None:
        """Remove curly brackets from the file given by p.h."""
        
        # Compute the indentation only once.
        indent = g.scanAllAtTabWidthDirectives(c, p) or -4

        # Backup all bodies in case there is an error.
        backup_d: dict[VNode, str] = {}  # Keys are vnodes, values are p.b.
        for p2 in p.self_and_subtree():
            if p2.gnx not in backup_d:
                backup_d [p2.v] = p.b
        
        # Handle each node separately.
        try:
            seen: dict[str, bool] = {}  # Keys are gnxs, values are True.
            for p2 in p.self_and_subtree():
                if p2.gnx not in seen:
                    seen [p2.gnx] = True
                    self.do_remove_brackets(indent, p2)
        except Exception as e:
            # Restore all body text.
            for v in backup_d:
                v.b = backup_d [v]
            g.es_print(f"Error in indented_typescript plugin: {e}.")
            g.es_print(f"No changes made to {p.h} and its subtree.")
                    
    #@+node:ekr.20230917091801.1: *3* IndentedTS.before_write
    def before_write(self, c, p):
        assert c == self.c
        assert p.isAnyAtFileNode(), p.h
        if not p.h.strip().endswith('.ts'):
            g.trace(f"Not a .ts file: {p.h}")
            return
        g.trace(p.h)
    #@+node:ekr.20230917184608.1: *3* IndentedTS.do_remove_brackets (top level)
    def do_remove_brackets(self, indent: int, p: Position) -> None:
        """
        The top-level driver for each node.
        
        Using guide lines, remove most curly brackets from p.b.
        """
        contents = p.b
        if not contents.strip():
            g.trace('Empty!', p.h)
            return
        lines = g.splitLines(contents)
        guide_lines = self.importer.make_guide_lines(lines)
        assert lines and len(lines) == len(guide_lines)
        
        # These may raise TypeError.
        self.check_brackets(guide_lines, p)
        self.check_indentation(guide_lines, indent, p)
        self.remove_brackets(guide_lines, lines, p)
    #@+node:ekr.20230917185546.1: *4* IndentedTS.check_brackets
    # No need to worry about comments in guide lines.
    bracket_pat = re.compile(r'^\s*}.*?{\s*$')
    matched_bracket_pat = re.compile(r'{.*?}\s*')

    def check_brackets(self, guide_lines: list[str], p: Position) -> None:
        """
        Check that all lines contain at most one unmatched '{' or '}'.
        If '}' precedes '{' then only whitespace may appear before '}' and after '{'.
        Raise TypeError if there is a problem.
        """
        trace = False
        for i, line0 in enumerate(guide_lines):
            line = re.sub(self.matched_bracket_pat, '', line0)
            if trace and line != line0:
                g.trace(f"Sub0: Line {i:4}: {line0.strip()}")
                g.trace(f"Sub1: Line {i:4}: {line.strip()}")
            n1 = line.count('{')
            n2 = line.count('}')
            if n1 > 1 or n2 > 1:
                raise TypeError(f"Too many curly brackets in line {i:4}: {line.strip()}")
            if n1 == 1 and n2 == 1 and line.find('{') > line.find('}'):
                m = self.bracket_pat.match(line)
                if not m:
                    raise TypeError(
                        f"{p.h}: Too invalid curly brackets in line {i:4}: {line.strip()}")
                if trace:
                    g.trace(f"Good: Line {i:4}: {line.strip()}")
    #@+node:ekr.20230919030308.1: *4* IndentedTS.check_indentation
    def check_indentation(self, guide_lines: list[str], indent: int, p: Position) -> None:
        """
        Check indentation and correct it if possible. Raise TypeError if not.
        
        Relax the checks for parenthesized lines.
        """
        # trace = False and p.h.endswith('indented_typescript_test.ts')
        # if trace:
            # g.printObj(guide_lines, tag=f"check_indentation: {p.h}")

        ws_char = ' ' if indent < 0 else '\t'
        ws_pat = re.compile(fr'^[{ws_char}]*')
        curly_pat1, curly_pat2 = re.compile(r'{'), re.compile(r'}')
        paren_pat1, paren_pat2 = re.compile(r'\('), re.compile(r'\)')
        indent_s = ws_char * abs(indent)
        indent_n = len(indent_s)
        assert indent_n > 0, f"check_indentation: can not happen: indent_n: {indent_n} {indent_s!r}"
        
        # The main loop.
        curlies, parens = 0, 0
        for i, line in enumerate(guide_lines):
            m = ws_pat.match(line)
            assert m, 'check_indentation: can not happen: ws_pat does not match'
            lws_s = m.group(0)
            lws = len(lws_s)

            # g.trace('lws', lws, '{', curlies, '(', parens, repr(line))
            
            # Check leading whitepace.
            lws_level, lws_remainder = divmod(lws, abs(indent))
            if parens and lws_remainder:
                # Just issue a warning
                g.trace(f"Unusual lws in parens: {line!r}")
            elif not parens and line.strip():
                # The lws should be the same as the curly braces level.
                # Look-ahead to see if *this* line decreases the curly braces level.
                curlies2 = curlies
                for m in re.finditer(curly_pat2, line):
                    curlies2 -= 1
                if curlies2 > 0 and lws_level != curlies2 or lws_remainder:
                    message = f"Bad indentation: bracket level: {curlies2}, line: {line!r}"
                    print(message)
                    raise TypeError(message)
            # Compute levels for the next line.
            for m in re.finditer(curly_pat1, line):
                curlies += 1
            for m in re.finditer(curly_pat2, line):
                curlies -= 1
            for m in re.finditer(paren_pat1, line):
                parens += 1
            for m in re.finditer(paren_pat2, line):
                parens -= 1
    #@+node:ekr.20230917184851.1: *4* IndentedTS.find_matching_brackets (to do)
    def find_matching_brackets(self, guide_lines: list[str], p: Position) -> list[tuple[int, int]]:
        """
        To do.
        """
        ### To do.
        g.printObj(guide_lines, tag=f"find_matching_brackets: {p.h}")
        return []
    #@+node:ekr.20230919030850.1: *4* IndentedTS.remove_brackets (to do)
    def remove_brackets(self,
        guide_lines: list[str],
        lines: list[str],
        p: Position,
    ) -> None:
        """
        Remove curly brackets from p.b.
        Raise TypeError if there is a problem.
        """
        if p.h.endswith('indented_typescript_test.ts'):
            # g.printObj(guide_lines, tag=f"remove_brackets: {p.h}")
            g.trace('To do')
    #@-others
#@-others

gControllers: dict[str, IndentedTypeScript] = {}  # keys are c.hash()
#@-leo

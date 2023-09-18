#@+leo-ver=5-thin
#@+node:ekr.20230917013414.1: * @file ../plugins/indented_typescript.py
"""
A plugin to edit typescript files using indentation instead of curly brackets.

- The ``open2`` event handler deletes curly brackets,
  after checking that nothing (except comments?) follows curly brackets.
- The ``read1`` event handler inserts curly brackets based on indentation.

Both event handlers will do a check similar to Python's tabnanny module.
"""
import os
import re
from typing import Any, Optional
from leo.core import leoGlobals as g
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.typescript import TS_Importer
assert g

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
        # g.trace(c.shortFileName(), g.callers())
        gControllers[c.hash()] = IndentedTypeScript(c)

def onAfterRead(tag: str, kwargs: Any) -> None:
    """after-read-external-file event handler for indented_typescript.py"""
    c, p = kwargs.get('c'), kwargs.get('p')
    if c and p:
        controller = gControllers.get(c.hash())
        controller.after_read(c, p)

def onBeforeWrite(tag: str, kwargs: Any) -> None:
    """before-writing-external-file event handler for indented_typescript.py"""
    c, p = kwargs.get('c'), kwargs.get('p')
    if c and p:
        controller = gControllers.get(c.hash())
        controller.before_write(c, p)
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
        contents = self.read(p)
        if not contents:
            return
        lines = g.splitLines(contents)
        guide_lines = self.importer.make_guide_lines(lines)
        assert lines and len(lines) == len(guide_lines)
        file_name = g.shortFileName(self.p_to_path(p))
        g.trace(f"{file_name} {len(contents)} chars, {len(lines)} lines")
        if not self.check_guide_lines(guide_lines):
            return
        result_lines = self.remove_brackets(guide_lines, lines)
        g.printObj(result_lines, tag='result lines')
    #@+node:ekr.20230917091801.1: *3* IndentedTS.before_write
    def before_write(self, c, p):
        assert c == self.c
        assert p.isAnyAtFileNode(), p.h
        if not p.h.strip().endswith('.ts'):
            g.trace(f"Not a .ts file: {p.h}")
            return
        g.trace(p.h)
        
    #@+node:ekr.20230917185546.1: *3* IndentedTS.check_guide_lines
    # No need to worry about comments in guide lines.
    bracket_pat = re.compile(r'^\s*}.*?{\s*$')
    matched_bracket_pat = re.compile(r'{.*?}\s*')

    def check_guide_lines(self, guide_lines: list[str]) -> bool:
        """
        Check that all lines contain at most one unmatched '{' or '}'.
        If '}' preceeds '{' then only whitespace may appear before '}' and after '{'.
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
                g.trace(f"Oops: line {i:4}: {line.strip()}")
                return False
            if n1 == 1 and n2 == 1 and line.find('{') > line.find('}'):
                m = self.bracket_pat.match(line)
                if trace and m:
                    g.trace(f"Good: Line {i:4}: {line.strip()}")
                if not m:
                    g.trace(f"Oops: Line {i:4}: {line.strip()}")
                    return False
        return True
    #@+node:ekr.20230917184851.1: *3* IndentedTS.find_matching_brackets
    def find_matching_brackets(self, guide_lines: list[str]) -> tuple[int, int]:
        pass
    #@+node:ekr.20230917182442.1: *3* IndentedTS.p_to_path
    def p_to_path(self, p: Position) -> Optional[str]:
        """
        Compute a path to a .ts file from p.h.
        """
        if not p.isAnyAtFileNode():
            g.trace(f"Not an @<file> node: {p.h}")
            return None
        if not p.h.strip().endswith('.ts'):
            g.trace(f"Not a .ts file: {p.h}")
            return None
        path = p.anyAtFileNodeName()
        return path
    #@+node:ekr.20230917181942.1: *3* IndentedTS.read
    def read(self, p: Position) -> Optional[str]:
        """Return the contents of the given file."""
        path = self.p_to_path(p)
        if not path:
            return None
        if not os.path.exists(path):
            g.trace(f"File not found: {path!r}")
            return None
        try:
            with open(path, 'r') as f:
                contents = f.read()
            return contents
        except Exception:
            g.trace(f"Exception opening: {path!r}")
            g.es_exception()
            return None
    #@+node:ekr.20230917184608.1: *3* IndentedTS.remove_brackets
    def remove_brackets(self, guide_lines: list[str], lines: list[str]) -> list[str]:
        """
        Using the guide lines, remove curly brackets from lines.
        Do not remove curly brackets if:
        - the matched pair is in the same line.
        - ';' follows '}'
        """
        result_lines: list[str] = []
        return result_lines
    #@-others
#@-others

gControllers: dict[str, IndentedTypeScript] = {}  # keys are c.hash()
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18152: * @file ../plugins/importers/typescript.py
"""The @auto importer for TypeScript."""
import re
from typing import Any, Dict, List
from leo.core import leoGlobals as g  # Required.
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20161118093751.1: ** class TS_Importer(Importer)
class TS_Importer(Importer):

    #@+<< define non-function patterns >>
    #@+node:ekr.20200817090227.1: *3* << define non-function patterns >>
    non_function_patterns = (

        re.compile(r'catch\s*\(.*\)'),
    )
    #@-<< define non-function patterns >>
    #@+<< define function patterns >>
    #@+node:ekr.20180523172655.1: *3* << define function patterns >>
    kinds = r'(async|public|private|static)'
    #
    # The pattern table. Order matters!
    function_patterns = (
        (1, re.compile(r'(interface\s+\w+)')),  # interface name
        (1, re.compile(r'(class\s+\w+)')),  # class name
        (1, re.compile(r'export\s+(class\s+\w+)')),  # export class name
        (1, re.compile(r'export\s+enum\s+(\w+)')),  # function name
        (1, re.compile(r'export\s+const\s+enum\s+(\w+)')),  # function name
        (1, re.compile(r'export\s+function\s+(\w+)')),  # function name
        (1, re.compile(r'export\s+interface\s+(\w+)')),  # interface name
        (1, re.compile(r'function\s+(\w+)')),  # function name
        (1, re.compile(r'(constructor).*{')),  # constructor ... {
        # kind function name
        (2, re.compile(r'%s\s*function\s+(\w+)' % kinds)),
        # kind kind function name
        (3, re.compile(r'%s\s+%s\s+function\s+(\w+)' % (kinds, kinds))),
        # Bare functions last...
        # kind kind name (...) {
        (3, re.compile(r'%s\s+%s\s+(\w+)\s*\(.*\).*{' % (kinds, kinds))),
        # name (...) {
        (2, re.compile(r'%s\s+(\w+)\s*\(.*\).*{' % kinds)),
        # #1619: Don't allow completely bare functions.
        # (1,  re.compile(r'(\w+)\s*\(.*\).*{')),
            # name (...) {
    )
    #@-<< define function patterns >>

    def __init__(self, c: Cmdr) -> None:
        """The ctor for the TS_ImportController class."""
        # Init the base class.
        super().__init__(
            c,
            language='typescript',  # Case is important.
            state_class=Typescript_ScanState,
        )

    #@+others
    #@+node:ekr.20190830160459.1: *3* ts_i.add_class_names
    def add_class_names(self, p: Position) -> None:
        """Add class names to headlines for all descendant nodes."""
        ###
    #@+node:ekr.20161118093751.5: *3* ts_i.compute_headline
    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):
            return s
        # Try to match patterns.
        for group_n, pattern in self.function_patterns:
            m = pattern.match(s)
            if m:
                # g.trace('group %s: %s' % (group_n, m.group(group_n)))
                return m.group(group_n)
        # Final cleanups, if nothing matches.
        for ch in '{(=':
            if s.endswith(ch):
                s = s[:-1].strip()
        s = s.replace('  ', ' ')
        s = s.replace(' (', '(')
        return g.truncate(s, 100)
    #@+node:ekr.20161118093751.2: *3* ts_i.skip_possible_regex
    def skip_possible_regex(self, s: str, i: int) -> int:
        """look ahead for a regex /"""
        assert s[i] in '=(', repr(s[i])
        i += 1
        while i < len(s) and s[i] in ' \t':
            i += 1
        if i < len(s) and s[i] == '/':
            i += 1
            while i < len(s):
                progress = i
                ch = s[i]
                if ch == '\\':
                    i += 2
                elif ch == '/':
                    i += 1
                    break
                else:
                    i += 1
                assert progress < i

        return i - 1
    #@+node:ekr.20180523170649.1: *3* ts_i.starts_block
    def starts_block(self, i: int, lines: List[str], new_state: Any, prev_state: Any) -> bool:
        """True if the new state starts a block."""
        if new_state.level() <= prev_state.level():
            return False
        line = lines[i].strip()
        for word in ('do', 'else', 'for', 'if', 'switch', 'try', 'while'):
            if line.startswith(word):
                return False
        # #1617: Chained calls look like functions, but aren't.
        for pattern in self.non_function_patterns:
            if pattern.match(line) is not None:
                return False
        for group_n, pattern in self.function_patterns:
            if pattern.match(line) is not None:
                return True
        return False
    #@-others
#@+node:ekr.20161118071747.14: ** class Typescript_ScanState
class Typescript_ScanState:
    """A class representing the state of the typescript line-oriented scan."""

    def __init__(self, d: Dict=None) -> None:
        """Typescript_ScanState ctor."""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    #@+others
    #@+node:ekr.20161118071747.15: *3* typescript_state.__repr__
    def __repr__(self) -> str:
        """ts_state.__repr__"""
        return '<TS_State %r curlies: %s>' % (self.context, self.curlies)

    __str__ = __repr__
    #@+node:ekr.20220731103111.1: *3* typescript_state.in_context
    def in_context(self) -> bool:
        return bool(self.context)
    #@+node:ekr.20161118082821.1: *3* typescript_state.is_ws_line
    ws_pattern = re.compile(r'^\s*$|^\s*#')

    def is_ws_line(self, s: str) -> bool:
        """Return True if s is nothing but whitespace and single-line comments."""
        return bool(self.ws_pattern.match(s))
    #@+node:ekr.20161119115736.1: *3* typescript_state.level
    def level(self) -> int:
        """Typescript_ScanState.level."""
        return self.curlies
    #@+node:ekr.20161118072957.1: *3* typescript_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Typescript_ScanState: Update the state using the given scan_tuple.
        """
        self.context = data.context
        self.curlies += data.delta_c
        return data.i
    #@-others
#@-others
importer_dict = {
    'func': TS_Importer.do_import(),
    'extensions': ['.ts',],
}
#@@language python
#@@tabwidth -4
#@-leo

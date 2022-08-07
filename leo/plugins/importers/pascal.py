#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18147: * @file ../plugins/importers/pascal.py
"""The @auto importer for the pascal language."""
import re
from typing import Any, Dict, List
from leo.core import leoGlobals as g  # Required.
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20161126171035.2: ** class Pascal_Importer
class Pascal_Importer(Importer):
    """The importer for the pascal lanuage."""

    pascal_start_pat1 = re.compile(r'^(function|procedure)\s+([\w_.]+)\s*\((.*)\)\s*\;\s*\n')
    pascal_start_pat2 = re.compile(r'^interface\b')

    def __init__(self, importCommands, **kwargs):
        """Pascal_Importer.__init__"""
        super().__init__(
            importCommands,
            language='pascal',
            state_class=Pascal_ScanState,
            strict=False,
        )

    #@+others
    #@+node:ekr.20161126171035.4: *3* pascal_i.compute_headline
    pascal_clean_pattern = re.compile(r'^(function|procedure)\s+([\w_.]+)')

    def compute_headline(self, s, p=None):
        """Return a cleaned up headline s."""
        m = self.pascal_clean_pattern.match(s)
        return '%s %s' % (m.group(1), m.group(2)) if m else s.strip()
    #@+node:ekr.20161129024448.1: *3* pascal_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == ('//', '{', '}'), f"pascal: {comment!r} {block1!r} {block2!r}"

        d: Dict[str, List[Any]]

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None)],
                '"':    [('len', '"', context == '"')],
                "'":    [('len', "'", context == "'")],
                '}':    [('len', '{', True)],
            }
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '/':    [('all', '//', context, None)],  # Single-line comment.
                '\\':   [('len+1', '\\', context, None)],
                '"':    [('len', '"', '"', None)],
                "'":    [('len', "'", "'", None)],
                '{':    [('len', '{', context, (1,0,0))],
                '}':    [('len', '}', context, (-1,0,0))],
                '(':    [('len', '(', context, (0,1,0))],
                ')':    [('len', ')', context, (0,-1,0))],
                '[':    [('len', '[', context, (0,0,1))],
                ']':    [('len', ']', context, (0,0,-1))],
            }
        return d
    #@+node:ekr.20220804120455.1: *3* pascal_i.gen_lines_prepass
    def gen_lines_prepass(self) -> None:
        """Update scan_state.decl_level for all scan states."""
        lines, line_states = self.lines, self.line_states
        begin_level, nesting_level = 0, 0
        for i, line in enumerate(lines):
            state = line_states[i]
            if line.isspace() or state.in_context():
                state.decl_level = nesting_level
                continue
            m = self.pascal_start_pat1.match(line) or self.pascal_start_pat2.match(line)
            if m:
                nesting_level += 1
                state.decl_level = nesting_level
            elif g.match_word(line.lstrip(), 0, 'begin'):
                begin_level += 1
                state.decl_level = nesting_level  # The 'end' is part of the block.
            elif g.match_word(line.lstrip(), 0, 'end'):
                if begin_level > 0:
                    begin_level -= 1
                else:
                    state.decl_level = nesting_level  # The 'end' is part of the block.
                    nesting_level -= 1
            else:
                state.decl_level = nesting_level
    #@-others
#@+node:ekr.20161126171035.6: ** class class Pascal_ScanState
class Pascal_ScanState:
    """A class representing the state of the pascal line-oriented scan."""

    def __init__(self, d=None):
        """Pascal_ScanState.__init__"""
        self.decl_level = 0  # A hack, for self.level()
        if d:
            prev = d.get('prev')
            self.context = prev.context
        else:
            self.context = ''

    def __repr__(self):
        """Pascal_ScanState.__repr__"""
        return "Pascal_ScanState context: %r" % (self.context)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20220804080833.1: *3* pascal_state.in_context
    def in_context(self) -> bool:
        return bool(self.context)
    #@+node:ekr.20161126171035.7: *3* pascal_state.level
    def level(self) -> int:
        """Pascal_ScanState.level."""
        return self.decl_level

    #@+node:ekr.20161126171035.8: *3* pascal_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Pascal_ScanState.update: Update the state using given scan_tuple.
        """
        self.context = data.context
        return data.i
    #@-others
#@-others
importer_dict = {
    'func': Pascal_Importer.do_import(),
    'extensions': ['.pas'],
}
#@@language python
#@@tabwidth -4


#@-leo

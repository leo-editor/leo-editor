#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18141: * @file ../plugins/importers/elisp.py
"""The @auto importer for the elisp language."""
import re
from typing import Any, Dict, List, Optional
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20161127184128.2: ** class Elisp_Importer(Importer)
class Elisp_Importer(Importer):
    """The importer for the elisp lanuage."""

    elisp_defun_pattern = re.compile(r'^\s*\(\s*defun\s+([\w_-]+)')

    def __init__(self, c):
        """Elisp_Importer.__init__"""
        # Init the base class.
        super().__init__(
            c,
            language='lisp',
            state_class=Elisp_ScanState,
        )

    #@+others
    #@+node:ekr.20170205195239.1: *3* elisp_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """elisp state dictionary for the given context."""
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == (';', '', ''), f"elisp: {comment!r} {block1!r} {block2!r}"

        d: Dict[str, List[Any]]

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None)],
                '"':    [('len', '"', context == '"')],
                # "'":    [('len', "'",    context == "'"),],
            }
        else:
            # Not in any context.
            d = {
                # key    kind   pattern   new-ctx  deltas
                ';':    [('all', comment, context, None)],
                '\\':   [('len+1', '\\', context, None)],
                '"':    [('len', '"', '"', None)],
                # "'":    [('len', "'", "'",     None),],
                '{':    [('len', '{', context, (1,0,0))],
                '}':    [('len', '}', context, (-1,0,0))],
                '(':    [('len', '(', context, (0,1,0))],
                ')':    [('len', ')', context, (0,-1,0))],
                '[':    [('len', '[', context, (0,0,1))],
                ']':    [('len', ']', context, (0,0,-1))],
            }
        return d
    #@+node:ekr.20161127184128.4: *3* elisp_i.compute_headline
    def compute_headline(self, s: str):
        """Return a cleaned up headline s."""
        m = self.elisp_defun_pattern.match(s)
        if m and m.group(1):
            return 'defun %s' % m.group(1)
        return s.strip()
    #@+node:ekr.20220804055254.1: *3* elisp_i.new_starts_block
    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        lines, line_states = self.lines, self.line_states
        line = lines[i]
        if line.isspace() or line_states[i].context:
            return None
        if self.elisp_defun_pattern.match(line):
            return i + 1
        return None
    #@-others
#@+node:ekr.20161127184128.6: ** class Elisp_ScanState
class Elisp_ScanState:
    """A class representing the state of the elisp line-oriented scan."""

    def __init__(self, d: Dict=None) -> None:
        """Elisp_ScanState.__init__"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.parens = prev.parens
        else:
            self.context = ''
            self.parens = 0

    def __repr__(self) -> None:
        """Elisp_ScanState.__repr__"""
        return "Elisp_ScanState context: %r parens: %s" % (
            self.context, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20220731123531.1: *3* elisp_state.in_context
    def in_context(self) -> bool:
        return bool(self.context or self.parens)
    #@+node:ekr.20161127184128.7: *3* elisp_state.level
    def level(self) -> int:
        """Elisp_ScanState.level."""
        return self.parens

    #@+node:ekr.20161127184128.8: *3* elisp_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Elisp_ScanState.update: Update the state using given scan_tuple.
        """
        self.context = data.context
        self.parens += data.delta_p
        return data.i
    #@-others
#@-others
importer_dict = {
    'func': Elisp_Importer.do_import(),  # Also clojure, clojurescript
    'extensions': ['.el', '.clj', '.cljs', '.cljc',],
}
#@@language python
#@@tabwidth -4
#@-leo

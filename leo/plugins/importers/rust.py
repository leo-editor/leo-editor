#@+leo-ver=5-thin
#@+node:ekr.20200316100818.1: * @file ../plugins/importers/rust.py
"""The @auto importer for rust."""
import re
from typing import Any, Dict, List
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20200316101240.2: ** class Rust_Importer
class Rust_Importer(Importer):

    def __init__(self, c):
        """rust_Importer.__init__"""
        # Init the base class.
        super().__init__(
            c,
            language='rust',
            state_class=Rust_ScanState,
        )
        self.headline = None

    #@+others
    #@+node:ekr.20200317114526.1: *3* rust_i.compute_headline
    arg_pat = re.compile(r'(\(.*?\))')
    type_pat = re.compile(r'(\s*->.*)')
    life_pat = re.compile(r'(\<.*\>)')
    body_pat = re.compile(r'(\{.*\})')

    def compute_headline(self, s: str):
        """
        Remove argument list and return value.
        """
        s = s.strip()
        m = self.func_pattern.match(s)
        if not m:
            return s
        g1 = m.group(1) or ''
        g2 = m.group(2) or ''
        head = f"{g1} {g2}".strip()
        # Remove the argument list and return value.
        tail = m.group(3) or ''.strip()
        tail = re.sub(self.arg_pat, '', tail, count=1)
        tail = re.sub(self.type_pat, '', tail, count=1)
        tail = re.sub(self.body_pat, '', tail, count=1)
        # Clean lifetime specs except for impl.
        if not head.startswith('impl'):
            tail = re.sub(self.life_pat, '', tail, count=1)
        # Remove trailing '(' or '{'
        tail = tail.strip()
        while tail.endswith(('{', '(', ',', ')')):
            tail = tail[:-1].rstrip()
        # Remove trailing '>' sometimes.
        while '<' not in tail and tail.endswith('>'):
            tail = tail[:-1].rstrip()
        return f"{head} {tail}".strip().replace('  ', ' ')
    #@+node:ekr.20200316101240.4: *3* rust_i.match_start_patterns
    # compute_headline also uses this pattern.
    func_pattern = re.compile(r'\s*(pub )?\s*(enum|fn|impl|mod|struct|trait)\b(.*)')

    def match_start_patterns(self, line):
        """
        True if line matches any block-starting pattern.
        If true, set self.headline.
        """
        m = self.func_pattern.match(line)
        if m:
            self.headline = line.strip()
        return bool(m)
    #@+node:ekr.20200316101240.6: *3* rust_i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        """True if the new state starts a block."""
        self.headline = None
        line = lines[i]
        if prev_state.context:
            return False
        if not self.match_start_patterns(line):
            return False
        # Must not be a complete statement.
        if line.find(';') > -1:
            return False
        return True
    #@+node:ekr.20200316114132.1: *3* rust_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == ('//', '/*', '*/'), f"rust: {comment!r} {block1!r} {block2!r}"

        # About context dependent lifetime tokens:
        # https://doc.rust-lang.org/stable/reference/tokens.html#lifetimes-and-loop-labels
        #
        # It looks like we can just ignore 'x' and 'x tokens.
        d: Dict[str, List[Any]]

        if context:
            d = {
                # key    kind  pattern  ends?
                '\\':   [('len+1', '\\', None)],
                '"':    [('len',   '"', context == '"')],
                # "'":    [('len', "'", context == "'"),],
                '*':    [('len', '*/', context == '/*')],
            }
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '/':    [
                    ('all', '//', context, None),
                    ('len', '/*', '/*', None),
                ],
                '\\':   [('len+1', '\\', context, None)],
                '"':    [('len', '"', '"',     None)],
                # "'":    [('len', "'", "'",     None)],
                '{':    [('len', '{', context, (1,0,0))],
                '}':    [('len', '}', context, (-1,0,0))],
                '(':    [('len', '(', context, (0,1,0))],
                ')':    [('len', ')', context, (0,-1,0))],
                '[':    [('len', '[', context, (0,0,1))],
                ']':    [('len', ']', context, (0,0,-1))],
            }
        return d
    #@-others
#@+node:ekr.20200316101240.7: ** class Rust_ScanState
class Rust_ScanState:
    """A class representing the state of the line-oriented scan for rust."""

    def __init__(self, d=None):
        """Rust_ScanSate ctor"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
            self.parens = prev.parens
        else:
            self.context = ''
            self.curlies = 0
            self.parens = 0

    def __repr__(self):
        """Rust_ScanState.__repr__"""
        return (
            f"<Rust_ScanState "
            f"context: {self.context!r} "
            f"curlies: {self.curlies} "
            f"parens: {self.parens}>")

    __str__ = __repr__

    #@+others
    #@+node:ekr.20200316101240.8: *3* rust_state.level
    def level(self) -> int:
        """Rust_ScanState.level."""
        return self.curlies  # (self.curlies, self.parens)
    #@+node:ekr.20200316101240.9: *3* rust_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Rust_ScanState: Update the state using given scan_tuple.
        """
        self.context = data.context
        self.curlies += data.delta_c
        self.parens += data.delta_p
        return data.i
    #@-others

#@-others
importer_dict = {
    'func': Rust_Importer.do_import(),
    'extensions': ['.rs',],
}
#@@language python
#@@tabwidth -4
#@-leo

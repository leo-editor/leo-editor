#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18148: * @file ../plugins/importers/php.py
"""The @auto importer for the php language."""
import re
from typing import Any, Dict, List
from leo.core import leoGlobals as g  # required
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20161129213243.2: ** class Php_Importer
class Php_Importer(Importer):
    """The importer for the php lanuage."""

    def __init__(self, c):
        """Php_Importer.__init__"""
        super().__init__(
            c,
            language='php',
            state_class=Php_ScanState,
        )
        self.here_doc_pattern = re.compile(r'<<<\s*([\w_]+)')
        self.here_doc_target = None

    #@+others
    #@+node:ekr.20161129213243.4: *3* php_i.compute_headline
    def compute_headline(self, s: str):
        """Return a cleaned up headline s."""
        return s.rstrip('{').strip()
    #@+node:ekr.20161129213808.1: *3* php_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == ('//', '/*', '*/'), f"php: {comment!r} {block1!r} {block2!r}"

        d: Dict[str, List[Any]]

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None)],
                '"':    [('len', '"',    context == '"')],
                "'":    [('len', "'",    context == "'")],
                '*':    [('len', '*/', True)],  # #1717.
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
                '<':    [('<<<', '<<<', '<<<', None)],
                '"':    [('len', '"', '"',     None)],
                "'":    [('len', "'", "'",     None)],
                '{':    [('len', '{', context, (1,0,0))],
                '}':    [('len', '}', context, (-1,0,0))],
                '(':    [('len', '(', context, (0,1,0))],
                ')':    [('len', ')', context, (0,-1,0))],
                '[':    [('len', '[', context, (0,0,1))],
                ']':    [('len', ']', context, (0,0,-1))],
            }
        return d
    #@+node:ekr.20161129214803.1: *3* php_i.scan_dict (supports here docs)
    def scan_dict(self, context, i, s, d):
        """
        i.scan_dict: Scan at position i of s with the give context and dict.
        Return the 6-tuple: (new_context, i, delta_c, delta_p, delta_s, bs_nl)
        """
        found = False
        delta_c = delta_p = delta_s = 0
        if self.here_doc_target:
            assert i == 0, repr(i)
            n = len(self.here_doc_target)
            if self.here_doc_target.lower() == s[:n].lower():
                self.here_doc_target = None
                i = n
                return scan_tuple('', i, 0, 0, 0, False)
            # Skip the rest of the line
            return scan_tuple('', len(s), 0, 0, 0, False)
        ch = s[i]  # For traces.
        aList = d.get(ch)
        if aList and context:
            # In context.
            for data in aList:
                kind, pattern, ends = data
                if self.match(s, i, pattern):
                    if ends is None:
                        found = True
                        new_context = context
                        break
                    elif ends:
                        found = True
                        new_context = ''
                        break
                    else:
                        pass  # Ignore this match.
        elif aList:
            # Not in context.
            for data in aList:
                kind, pattern, new_context, deltas = data
                if self.match(s, i, pattern):
                    found = True
                    if deltas:
                        delta_c, delta_p, delta_s = deltas
                    break
        if found:
            if kind == 'all':
                i = len(s)
            elif kind == 'len+1':
                i += (len(pattern) + 1)
            elif kind == '<<<':  # Special flag for here docs.
                new_context = context  # here_doc_target is a another kind of context.
                m = self.here_doc_pattern.match(s[i:])
                if m:
                    i = len(s)  # Skip the rest of the line.
                    self.here_doc_target = '%s;' % m.group(1)
                else:
                    i += 3
            else:
                assert kind == 'len', (kind, self.name)
                i += len(pattern)
            bs_nl = pattern == '\\\n'
            return scan_tuple(new_context, i, delta_c, delta_p, delta_s, bs_nl)
        #
        # No match: stay in present state. All deltas are zero.
        new_context = context
        return scan_tuple(new_context, i + 1, 0, 0, 0, False)
    #@+node:ekr.20161130044051.1: *3* php_i.skip_heredoc_string (not used)
    # EKR: This is Dave Hein's heredoc code from the old PHP scanner.
    # I have included it for reference in case heredoc problems arise.
    #
    # php_i.scan dict uses r'<<<\s*([\w_]+)' instead of the more complex pattern below.
    # This is likely good enough. Importers can assume that code is well formed.

    def skip_heredoc_string(self, s, i):
        #@+<< skip_heredoc docstrig >>
        #@+node:ekr.20161130044051.2: *4* << skip_heredoc docstrig >>
        #@@nocolor-node
        """
        08-SEP-2002 DTHEIN:  added function skip_heredoc_string
        A heredoc string in PHP looks like:

          <<<EOS
          This is my string.
          It is mine. I own it.
          No one else has it.
          EOS

        It begins with <<< plus a token (naming same as PHP variable names).
        It ends with the token on a line by itself (must start in first position.
        """
        #@-<< skip_heredoc docstrig >>
        j = i
        assert g.match(s, i, "<<<")
        m = re.match(r"\<\<\<([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)", s[i:])
        if m is None:
            i += 3
            return i
        # 14-SEP-2002 DTHEIN: needed to add \n to find word, not just string
        delim = m.group(1) + '\n'
        i = g.skip_line(s, i)  # 14-SEP-2002 DTHEIN: look after \n, not before
        n = len(s)
        while i < n and not g.match(s, i, delim):
            i = g.skip_line(s, i)  # 14-SEP-2002 DTHEIN: move past \n
        if i >= n:
            g.scanError("Run on string: " + s[j:i])
        elif g.match(s, i, delim):
            i += len(delim)
        return i
    #@-others
#@+node:ekr.20161129213243.6: ** class Php_ScanState
class Php_ScanState:
    """A class representing the state of the php line-oriented scan."""

    def __init__(self, d: Dict=None) -> None:
        """Php_ScanState.__init__"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self) -> str:
        """Php_ScanState.__repr__"""
        return "Php_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20220731103148.1: *3* php_state.in_context
    def in_context(self) -> bool:
        return bool(self.context)
    #@+node:ekr.20161129213243.7: *3* php_state.level
    def level(self) -> int:
        """Php_ScanState.level."""
        return self.curlies

    #@+node:ekr.20161129213243.8: *3* php_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Php_ScanState.update: Update the state using given scan_tuple.
        """
        if 'importers' in g.app.debug:
            g.trace(
                f"context: {data.context!s} "
                f"delta_c: {data.delta_c} "
                f"delta_s: {data.delta_s} "
                f"bs_nl: {data.bs_nl}")
        # All ScanState classes must have a context ivar.
        self.context = data.context
        self.curlies += data.delta_c
        return data.i
    #@-others
#@-others
importer_dict = {
    'func': Php_Importer.do_import(),
    'extensions': ['.php'],
}
#@@language python
#@@tabwidth -4
#@-leo

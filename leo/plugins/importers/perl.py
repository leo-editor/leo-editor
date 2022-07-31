#@+leo-ver=5-thin
#@+node:ekr.20161027100313.1: * @file ../plugins/importers/perl.py
"""The @auto importer for Perl."""
import re
from typing import Any, Dict, List
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20161027094537.13: ** class Perl_Importer
class Perl_Importer(Importer):
    """A scanner for the perl language."""

    def __init__(self, importCommands, **kwargs):
        """The ctor for the Perl_ImportController class."""
        super().__init__(
            importCommands,
            language='perl',
            state_class=Perl_ScanState,
        )

    #@+others
    #@+node:ekr.20161027183713.1: *3* perl_i.clean_headline
    def clean_headline(self, s, p=None):
        """Return a cleaned up headline s."""
        m = re.match(r'sub\s+(\w+)', s)
        return 'sub ' + m.group(1) if m else s
    #@+node:ekr.20161129024520.1: *3* perl_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == ('#', '', ''), f"perl: {comment!r} {block1!r} {block2!r}"

        d: Dict[str, List[Any]]

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None),],
                '=':    [('len', '=cut', context == '=')],
                '/':    [('len', '/',    context == '/')],
                '"':    [('len', '"',    context == '"')],
                "'":    [('len', "'",    context == "'")],
            }
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':[('len+1', '\\', context, None)],
                '#':    [('all', '#', context, None)],
                '=':    [('len', '=', context, None)],
                't':    [('len', 'tr///', '/', None)],
                's':    [('len', 's///',  '/', None)],
                'm':    [('len', 'm//',   '/', None)],
                '/':    [('len', '/',     '/', None)],
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
    #@+node:ekr.20161027094537.12: *3* perl_i.skip_regex
    def skip_regex(self, s, i, pattern):
        """look ahead for a regex /"""
        assert self.match(s, i, pattern)
        i += len(pattern)
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
        return i
    #@-others
#@+node:ekr.20161105095705.1: ** class Perl_ScanState
class Perl_ScanState:
    """A class representing the state of the perl line-oriented scan."""

    def __init__(self, d=None):
        """Perl_ScanState ctor."""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
            self.parens = prev.parens
        else:
            self.context = ''
            self.curlies = self.parens = 0

    def __repr__(self):
        """Perl_ScanState.__repr__"""
        return 'Perl_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115617.1: *3* perl_state.level
    def level(self) -> int:
        """Perl_ScanState.level."""
        return self.curlies  # (self.curlies, self.parens)
    #@+node:ekr.20161119050522.1: *3* perl_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Perl_ScanState: Update the state using given scan_tuple.
        """
        self.context = data.context
        self.curlies += data.delta_c
        self.parens += data.delta_p
        return data.i
    #@-others

#@-others
importer_dict = {
    'func': Perl_Importer.do_import(),
    'extensions': ['.pl',],
}
#@@language python
#@@tabwidth -4
#@-leo

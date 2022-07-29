#@+leo-ver=5-thin
#@+node:ekr.20160505094722.1: * @file ../plugins/importers/coffeescript.py
"""The @auto importer for coffeescript."""
import re
from typing import Any, Dict, List, Optional
from leo.core import leoGlobals as g
assert g  ###
from leo.plugins.importers import linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20160505094722.2: ** class Coffeescript_Importer(Importer)
class Coffeescript_Importer(Importer):

    #@+others
    #@+node:ekr.20160505101118.1: *3* coffee_i.__init__
    def __init__(self, importCommands, **kwargs):
        """Ctor for CoffeeScriptScanner class."""
        super().__init__(
            importCommands,
            language='coffeescript',
            state_class=Coffeescript_ScanState,
            strict=True
        )
    #@+node:ekr.20220729104712.1: *3* coffee_i.clean_headline
    def clean_headline(self, s, p=None):
        """
        Coffeescript_Importer.clean_headline.

        Don't strip arguments.
        """
        return s.strip()
    #@+node:ekr.20161129024357.1: *3* coffee_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == ('#', '', ''), f"coffeescript: {comment!r} {block1!r} {block2!r}"

        d: Dict[str, List[Any]]

        if context:
            d = {
                # key   kind   pattern  ends?
                '\\':   [('len+1', '\\', None),],
                '#':    [('len', '###', context == '###')],
                '"':    [('len', '"', context == '"')],
                "'":    [('len', "'", context == "'")],
            }
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':   [('len+1', '\\', context, None)],
                '#':    [
                            ('len','###','###', None), # Docstring
                            ('all', '#', context, None),
                        ],
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
    #@+node:ekr.20161118134555.7: *3* coffee_i.new_starts_block
    pattern_table = [
        re.compile(r'^\s*class'),
        re.compile(r'^\s*(.+):(.*)->'),
        re.compile(r'^\s*(.+)=(.*)->'),
    ]

    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        lines, line_states = self.lines, self.line_states
        line = lines[i]
        if line.isspace() or line_states[i].in_context():
            return None
        prev_state = line_states[i - 1] if i > 0 else self.state_class()
        if prev_state.in_context():
            return None
        line = lines[i]
        for pattern in self.pattern_table:
            if pattern.match(line):
                self.headline = self.clean_headline(line)
                return i + 1
        return None
    #@-others
    @classmethod
    def do_import(cls):
        def f(c, s, parent):
            return cls(c.importCommands).run(s, parent)
        return f
#@+node:ekr.20161110045131.1: ** class Coffeescript_ScanState
class Coffeescript_ScanState:
    """A class representing the state of the coffeescript line-oriented scan."""

    def __init__(self, d=None):
        """Coffeescript_ScanState ctor."""
        if d:
            indent = d.get('indent')
            is_ws_line = d.get('is_ws_line')
            prev = d.get('prev')
            assert indent is not None and is_ws_line is not None
            self.bs_nl = False
            self.context = prev.context
            self.indent = prev.indent if prev.bs_nl else indent
        else:
            self.bs_nl = False
            self.context = ''
            self.indent = 0

    #@+others
    #@+node:ekr.20161118064325.1: *3* cs_state.__repr__
    def __repr__(self):
        """CS_State.__repr__"""
        return '<CSState %r indent: %s>' % (self.context, self.indent)

    __str__ = __repr__
    #@+node:ekr.20161119115413.1: *3* cs_state.level
    def level(self):
        """Coffeescript_ScanState.level."""
        return self.indent
    #@+node:ekr.20161118140100.1: *3* cs_state.in_context
    def in_context(self):
        """True if in a special context."""
        return self.context or self.bs_nl
    #@+node:ekr.20161119052920.1: *3* cs_state.update
    def update(self, data):
        """
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        """
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        # self.curlies += delta_c
        # self.parens += delta_p
        # self.squares += delta_s
        return i

    #@-others
#@-others
importer_dict = {
    'func': Coffeescript_Importer.do_import(),
    'extensions': ['.coffee',],
}
#@@language python
#@@tabwidth -4
#@-leo

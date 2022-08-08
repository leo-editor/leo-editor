#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18143: * @file ../plugins/importers/java.py
"""The @auto importer for the java language."""
import re
from typing import Dict, Optional
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20161126161824.2: ** class Java_Importer
class Java_Importer(Importer):
    """The importer for the java lanuage."""

    def __init__(self, c):
        """Java_Importer.__init__"""
        super().__init__(
            c,
            language='java',
            state_class=Java_ScanState,
        )

    # Used in multiple methods.
    java_keywords = (
        '(break|case|catch|continue|default|do|else|enum|' +
        'finally|for|goto|if|new|return|' +
        'sizeof|strictfp|struct|super|switch|this|throw|throws|try|while)'
    )
    java_types_list = (
        '(abstract|boolean|byte|char|const|double|extends|final|float|int|' +
        'interface|long|native|package|private|protected|public|' +
        'short|static|transient|void|volatile)'
    )
    # 'signed|typedef|union|unsigned)'
    java_types_pattern = re.compile(java_types_list)
    java_keywords_pattern = re.compile(java_keywords)

    #@+others
    #@+node:ekr.20161205042019.2: *3* java_i.match_name_patterns
    java_name_pattern = re.compile(r'\s*([\w:]+)')

    def match_name_patterns(self, line):
        """Set self.headline if the line defines a typedef name."""
        m = self.java_name_pattern.match(line)
        if m:
            word = m.group(1)
            if not self.java_types_pattern.match(word):
                self.headline = word
    #@+node:ekr.20161205042019.3: *3* java_i.match_start_patterns
    # Define patterns that can start a block
    java_class_pattern = re.compile(r'\s*(%s\s*)*\s*class\s+(\w+)' % (java_types_list))
    java_func_pattern = re.compile(r'\s*(%s\s*)+\s*([\w:]+)' % (java_types_list))

    def match_start_patterns(self, line):
        """
        True if line matches any block-starting pattern.
        If true, set self.headline.
        """
        m = self.java_class_pattern.match(line)
        if m:
            self.headline = line
            return True
        m = self.java_func_pattern.match(line)
        if m:
            i = line.find('(')
            self.headline = line[:i] if i > -1 else line
            return True
        return False
    #@+node:ekr.20161205042019.5: *3* java_i.new_starts_block
    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        i0, lines, line_states = i, self.lines, self.line_states
        line = lines[i]
        if (
            line.isspace()
            or ';' in line  # Must not be a complete statement.
            or line_states[i].context
            or self.java_keywords_pattern.match(line)
            or not self.match_start_patterns(line)
        ):
            return None
        # Set self.headline.
        # Scan ahead at most 10 lines until an open { is seen.
        while i < len(lines) and i <= i0 + 10:
            prev_state = line_states[i - 1] if i > 0 else self.state_class()
            this_state = line_states[i]
            if this_state.level() > prev_state.level():
                return i + 1
            i += 1
        return None
    #@-others
#@+node:ekr.20161126161824.6: ** class class Java_ScanState
class Java_ScanState:
    """A class representing the state of the java line-oriented scan."""

    def __init__(self, d: Dict=None) -> None:
        """Java_ScanState.__init__"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self) -> None:
        """Java_ScanState.__repr__"""
        return "Java_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20220731102742.1: *3* java_state.in_context
    def in_context(self) -> bool:
        return bool(self.context)
    #@+node:ekr.20161126161824.7: *3* java_state.level
    def level(self) -> int:
        """Java_ScanState.level."""
        return self.curlies

    #@+node:ekr.20161126161824.8: *3* java_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Java_ScanState.update: Update the state using the given scan_tuple.
        """
        self.context = data.context
        self.curlies += data.delta_c
        return data.i
    #@-others
#@-others
importer_dict = {
    'func': Java_Importer.do_import(),
    'extensions': ['.java'],
}
#@@language python
#@@tabwidth -4
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
"""The @auto importer for the C language and other related languages."""
import re
from typing import Optional
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
assert g
Importer = linescanner.Importer
Target = linescanner.Target
class_or_def_tuple = linescanner.class_or_def_tuple
NEW_GEN_LINES = linescanner.NEW_GEN_LINES  ###
#@+others
#@+node:ekr.20140723122936.17928: ** class C_Importer
class C_Importer(Importer):

    # For cleaning headlines.
    c_name_pattern = re.compile(r'\s*([\w:]+)')

    #@+others
    #@+node:ekr.20200819073508.1: *3* c_i.clean_headline
    def clean_headline(self, s, p=None):
        """
        Adjust headline for templates.
        """
        i = s.find('(')
        if i > -1:
            s = s[:i]
        # if s.startswith('template') and len(lines) > 1:
            # line = lines[1]
            # # Filter out all keywords and cruft.
            # # This isn't perfect, but it's a good start.
            # for z in self.type_keywords:
                # line = re.sub(fr"\b{z}\b", '', line)
            # for ch in '()[]{}=':
                # line = line.replace(ch, '')
            # return line.strip()
        return s.strip()
    #@+node:ekr.20200819144754.1: *3* c_i.ctor
    def __init__(self, importCommands, **kwargs):
        """C_Importer.__init__"""
        # Init the base class.
        super().__init__(
            importCommands,
            language='c',
            state_class=C_ScanState,
        )
        self.headline = None

        # #545: Support @data c_import_typedefs.
        self.type_keywords = [
            'auto', 'bool', 'char', 'const', 'double',
            'extern', 'float', 'int', 'register',
            'signed', 'short', 'static', 'typedef',
            'union', 'unsigned', 'void', 'volatile',
        ]
        aSet = set(
            self.type_keywords +
            (self.c.config.getData('c_import_typedefs') or [])
        )
        self.c_type_names = f"({'|'.join(list(aSet))})"
        self.c_types_pattern = re.compile(self.c_type_names)
        self.c_class_pattern = re.compile(r'\s*(%s\s*)*\s*class\s+(\w+)' % (self.c_type_names))
        self.c_func_pattern = re.compile(r'\s*(%s\s*)+\s*([\w:]+)' % (self.c_type_names))
        self.c_keywords = '(%s)' % '|'.join([
            'break', 'case', 'continue', 'default', 'do', 'else', 'enum',
            'for', 'goto', 'if', 'return', 'sizeof', 'struct', 'switch', 'while',
        ])
        self.c_keywords_pattern = re.compile(self.c_keywords)
    #@+node:ekr.20220728060001.1: *3* c_i.get_class_or_def
    def get_class_or_def(self, i: int) -> class_or_def_tuple:
        """
        C_Importer.get_class_or_def, based on Vitalije's python importer.

        Look for a def or class at self.lines[i]
        Return None or a class_or_def_tuple describing the class or def.
        """
        self.headline =  ''  # Set in helpers.
        lines = self.lines

        # Return if lines[i] does not start a block.
        first_body_line = self.new_starts_block(i)
        if first_body_line is None:
            return None

        # Compute declaration data.
        decl_line = i
        decl_indent = self.get_int_lws(self.lines[i])

        # Scan to the end of the block.
        i = self.new_skip_block(first_body_line)

        # Calculate the indentation of the first non-blank body line.
        j = first_body_line
        while j <= i < len(lines):
            if not lines[j].isspace():
                body_indent = self.get_int_lws(lines[j])
                break
            j += 1
        else:
            body_indent = 0

        # Include all following blank lines.
        while i < len(lines) and lines[i].isspace():
            i += 1

        # Return the description of the unit.
        return class_or_def_tuple(
            body_indent = body_indent,
            body_line1 = i,
            decl_indent = decl_indent,
            decl_line1 = decl_line - self.get_intro(decl_line, decl_indent),
            kind = '',  # Not used.
            name = self.headline,
        )
    #@+node:ekr.20161204173153.1: *3* c_i.match_name_patterns
    def match_name_patterns(self, line):
        """Set self.headline if the line defines a typedef name."""
        m = self.c_name_pattern.match(line)
        if m:
            word = m.group(1)
            if not self.c_types_pattern.match(word):
                self.headline = word
    #@+node:ekr.20161204165700.1: *3* c_i.match_start_patterns
    # Patterns that can start a block
    c_extern_pattern = re.compile(r'\s*extern\s+(\"\w+\")')
    c_template_pattern = re.compile(r'\s*template\s*<(.*?)>\s*$')
    c_typedef_pattern = re.compile(r'\s*(\w+)\s*\*\s*$')

    def match_start_patterns(self, line):
        """
        True if line matches any block-starting pattern.
        If true, set self.headline.
        """
        trace = False  ###
        m = self.c_extern_pattern.match(line)
        if m:
            self.headline = line.strip()
            if trace: g.trace('extern:', repr(line))  ###
            return True
        # #1626
        m = self.c_template_pattern.match(line)
        if m:
            self.headline = line.strip()
            if trace: g.trace('template:', repr(line))  ###
            return True
        m = self.c_class_pattern.match(line)
        if m:
            prefix = f"{m.group(1).strip()} " if m.group(1) else ''
            name = m.group(3)
            self.headline = f"{prefix}class {name}"
            if trace: g.trace('class', line)
            return True
        m = self.c_func_pattern.match(line)
        if m:
            if self.c_types_pattern.match(m.group(3)):
                if trace: g.trace('func and types:', repr(line))  ###
                return True
            name = m.group(3)
            prefix = f"{m.group(1).strip()} " if m.group(1) else ''
            self.headline = f"{prefix}{name}"
            if trace: g.trace('func', repr(line))
            return True
        m = self.c_typedef_pattern.match(line)
        if m:
            # Does not set self.headline.
            if trace: g.trace('typedef:', repr(line))  ###
            return True
        m = self.c_types_pattern.match(line)
        if trace and m: g.trace('type:', repr(line))  ###
        return bool(m)
    #@+node:ekr.20220728070521.1: *3* c_i.new_skip_block
    def new_skip_block(self, i: int) -> int:
        """Return the index of line after the last line of the block."""
        lines, line_states = self.lines, self.line_states
        state1 = line_states[i]  # The opening state
        ### g.trace(i, state1, repr(lines[i]))
        while i < len(lines):
            i += 1
            ### g.trace(i, line_states[i], repr(lines[i]))
            if line_states[i].level() < state1.level():
                return i + 1
        return len(lines)

    #@+node:ekr.20220728055719.1: *3* c_i.new_starts_block
    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        i0, lines, line_states = i, self.lines, self.line_states
        line = lines[i]
        if (
            line.isspace()
            or line_states[i].context
            or line.find(';') > -1 # One-line declaration.
            or self.c_keywords_pattern.match(line)  # A statement.
            or not self.match_start_patterns(line)
        ):
            return None
        # Try again to set self.headline.
        if not self.headline and i0 + 1 < len(lines):
            self.headline = f"{lines[i0].strip()} {lines[i0+1].strip()}"
        # Now clean the headline.
        if self.headline:
            self.headline = self.clean_headline(self.headline)
        # Scan ahead at most 10 lines until an open { is seen.
        while i < len(lines) and i <= i0 + 10:
            prev_state = line_states[i - 1] if i > 0 else self.ScanState()
            this_state = line_states[i]
            if this_state.level() > prev_state.level():
                return i + 1
            i += 1
        return None
    #@-others
#@+node:ekr.20161108223159.1: ** class C_ScanState
class C_ScanState:
    """A class representing the state of the C line-oriented scan."""

    def __init__(self, d=None):
        """C_ScanSate ctor"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        """C_ScanState.__repr__"""
        return 'C_ScanState context: %r curlies: %s' % (self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115315.1: *3* c_state.level
    def level(self):
        """C_ScanState.level."""
        return self.curlies
    #@+node:ekr.20161118051111.1: *3* c_state.update
    def update(self, data):
        """
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        """
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c
        return i

    #@-others

#@-others
importer_dict = {
    'func': C_Importer.do_import(),
    'extensions': ['.c', '.cc', '.c++', '.cpp', '.cxx', '.h', '.h++',],
}
#@@language python
#@@tabwidth -4
#@-leo

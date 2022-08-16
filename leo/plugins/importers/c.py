#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
"""The @auto importer for the C language and other related languages."""
import re
from typing import Optional
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20140723122936.17928: ** class C_Importer
class C_Importer(Importer):

    # #545: Support @data c_import_typedefs.
    type_keywords = [
        'auto', 'bool', 'char', 'const', 'double',
        'extern', 'float', 'int', 'register',
        'signed', 'short', 'static', 'typedef',
        'union', 'unsigned', 'void', 'volatile',
    ]

    #@+others
    #@+node:ekr.20200819144754.1: *3* c_i.ctor
    def __init__(self, c: Cmdr) -> None:
        """C_Importer.__init__"""

        # Init the base class.
        super().__init__(c, language='c')

        # These must be defined here because they use configuration data..
        aSet = set(self.type_keywords + (c.config.getData('c_import_typedefs') or []))
        self.c_type_names = f"({'|'.join(list(aSet))})"
        self.c_types_pattern = re.compile(self.c_type_names)
        self.c_class_pattern = re.compile(r'\s*(%s\s*)*\s*class\s+(\w+)' % (self.c_type_names))
        self.c_func_pattern = re.compile(r'\s*(%s\s*)+\s*([\w:]+)' % (self.c_type_names))
        self.c_keywords = '(%s)' % '|'.join([
            'break', 'case', 'continue', 'default', 'do', 'else', 'enum',
            'for', 'goto', 'if', 'return', 'sizeof', 'struct', 'switch', 'while',
        ])
        self.c_keywords_pattern = re.compile(self.c_keywords)
    #@+node:ekr.20220728055719.1: *3* c_i.new_starts_block & helper
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
            or line.find(';') > -1  # One-line declaration.
            or self.c_keywords_pattern.match(line)  # A statement.
            or not self.match_start_patterns(line)
        ):
            return None
        # Try to set self.headline.
        if not self.headline and i0 + 1 < len(lines):
            self.headline = f"{lines[i0].strip()} {lines[i0+1].strip()}"
        # Now clean the headline.
        if self.headline:
            self.headline = self.compute_headline(self.headline)
        # Scan ahead at most 10 lines until an open { is seen.
        while i < len(lines) and i <= i0 + 10:
            prev_state = line_states[i - 1] if i > 0 else self.state_class()
            this_state = line_states[i]
            if this_state.level > prev_state.level:
                return i + 1
            i += 1
        return None  # pragma: no cover
    #@+node:ekr.20161204165700.1: *4* c_i.match_start_patterns
    # Patterns that can start a block
    c_extern_pattern = re.compile(r'\s*extern\s+(\"\w+\")')
    c_template_pattern = re.compile(r'\s*template\s*<(.*?)>\s*$')
    c_typedef_pattern = re.compile(r'\s*(\w+)\s*\*\s*$')

    def match_start_patterns(self, line: str) -> bool:
        """
        True if line matches any block-starting pattern.
        If true, set self.headline.
        """
        m = self.c_extern_pattern.match(line)
        if m:
            self.headline = line.strip()
            return True
        # #1626
        m = self.c_template_pattern.match(line)
        if m:
            self.headline = line.strip()
            return True
        m = self.c_class_pattern.match(line)
        if m:
            prefix = f"{m.group(1).strip()} " if m.group(1) else ''
            name = m.group(3)
            self.headline = f"{prefix}class {name}"
            return True
        m = self.c_func_pattern.match(line)
        if m:
            if self.c_types_pattern.match(m.group(3)):
                return True
            name = m.group(3)
            prefix = f"{m.group(1).strip()} " if m.group(1) else ''
            self.headline = f"{prefix}{name}"
            return True
        m = self.c_typedef_pattern.match(line)
        if m:
            # Does not set self.headline.
            return True
        m = self.c_types_pattern.match(line)
        return bool(m)
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for c."""
    C_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.c', '.cc', '.c++', '.cpp', '.cxx', '.h', '.h++',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file ../plugins/importers/javascript.py
"""The @auto importer for JavaScript."""
import re
from leo.core import leoGlobals as g  # Required
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer(Importer)
class JS_Importer(Importer):

    def __init__(self, c: Cmdr) -> None:
        """The ctor for the JS_ImportController class."""
        # Init the base class.
        super().__init__(c, language='javascript')

    #@+others
    #@+node:ekr.20161101183354.1: *3* js_i.compute_headline
    clean_regex_list1 = [
        # (function name (
        re.compile(r'\s*\(?(function\b\s*[\w]*)\s*\('),
        # name: (function (
        re.compile(r'\s*(\w+\s*\:\s*\(*\s*function\s*\()'),
        # const|let|var name = .* =>
        re.compile(r'\s*(?:const|let|var)\s*(\w+\s*(?:=\s*.*)=>)'),
    ]
    clean_regex_list2 = [
        re.compile(r'(.*\=)(\s*function)'),  # .* = function
    ]
    clean_regex_list3 = [
        re.compile(r'(.*\=\s*new\s*\w+)\s*\(.*(=>)'),  # .* = new name .* =>
        re.compile(r'(.*)\=\s*\(.*(=>)'),  # .* = ( .* =>
        re.compile(r'(.*)\((\s*function)'),  # .* ( function
        re.compile(r'(.*)\(.*(=>)'),  # .* ( .* =>
        re.compile(r'(.*)(\(.*\,\s*function)'),  # .* \( .*, function
    ]
    clean_regex_list4 = [
        re.compile(r'(.*)\(\s*(=>)'),  # .* ( =>
    ]

    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):  # pragma: no cover (missing test)
            return s
        for ch in '{(=':
            if s.endswith(ch):
                s = s[:-1].strip()
        # First regex cleanup. Use \1.
        for pattern in self.clean_regex_list1:
            m = pattern.match(s)
            if m:
                s = m.group(1)
                break
        # Second regex cleanup. Use \1 + \2
        for pattern in self.clean_regex_list2:
            m = pattern.match(s)
            if m:
                s = m.group(1) + m.group(2)
                break
        # Third regex cleanup. Use \1 + ' ' + \2
        for pattern in self.clean_regex_list3:
            m = pattern.match(s)
            if m:
                s = m.group(1) + ' ' + m.group(2)
                break
        # Fourth cleanup. Use \1 + ' ' + \2 again
        for pattern in self.clean_regex_list4:  # pragma: no cover (mysterious)
            m = pattern.match(s)
            if m:
                s = m.group(1) + ' ' + m.group(2)
                break
        # Final whitespace cleanups.
        s = s.replace('  ', ' ')
        s = s.replace(' (', '(')
        return g.truncate(s, 100)
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for javascript."""
    JS_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.js',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo

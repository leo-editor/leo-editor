#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18137: * @file ../plugins/importers/xml.py
"""The @auto importer for the xml language."""
import re
from typing import List, Optional, Tuple
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161121204146.3: ** class Xml_Importer(Importer)
class Xml_Importer(Importer):
    """The importer for the xml lanuage."""

    def __init__(self, c: Cmdr, tags_setting: str = 'import_xml_tags') -> None:
        """Xml_Importer.__init__"""
        # Init the base class.
        super().__init__(c, language='xml')
        self.tags_setting = tags_setting
        self.start_tags = self.add_tags()
        # A closing tag decrements state.tag_level only if the top is an opening tag.
        # self.stack: List[str] = []  # Stack of tags.
        # self.void_tags = ['<?xml', '!doctype']
        # self.tag_warning_given = False  # True: a structure error has been detected.

    #@+others
    #@+node:ekr.20161121204918.1: *3* xml_i.add_tags
    def add_tags(self) -> List[str]:
        """Add items to self.class/functionTags and from settings."""
        c, setting = self.c, self.tags_setting
        aList = c.config.getData(setting) or []
        aList = [z.lower() for z in aList]
        return aList
    #@+node:ekr.20170416082422.1: *3* xml_i.compute_headline
    def compute_headline(self, s: str) -> str:
        """xml and html: Return a cleaned up headline s."""
        m = re.match(r'\s*(<[^>]+>)', s)
        return m.group(1) if m else s.strip()
    #@+node:ekr.20220801080949.1: *3* xml_i.get_intro
    def get_intro(self, row: int, col: int) -> int:
        """
        Return the number of preceeding lines that should be added to this class or def.
        """
        return 0
    #@+node:ekr.20220801082146.1: *3* xml_i.new_starts_block
    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        lines, states = self.lines, self.line_states
        prev_state = states[i - 1] if i > 0 else self.state_class()
        this_state = states[i]
        if lines[i].isspace() or this_state.context:
            return None
        if this_state.level > prev_state.level:
            return i + 1
        return None
    #@+node:ekr.20220815111538.1: *3* xml_i.update_level
    ch_pattern = re.compile(r'([\!\?]?[\w\_\.\:\-]+)', re.UNICODE)

    def update_level(self, i: int, level: int, line: str) -> Tuple[int, int]:
        """
        XML_Importer.update_level.  Overrides Importer.update_level.

        Update level at line[i] and return (i, level).
        """
        if line[i] != '<':
            return i + 1, level  # Make progress.
        # Scan the tag.
        end_tag = line.find('</', i) == i
        i += (2 if end_tag else 1)  # Ensure progress, whatever happens.
        m = self.ch_pattern.match(line, i)
        if not m:  # pragma: no cover (missing test)
            # All other '<' characters should have had xml/html escapes applied to them.
            self.error(f"missing tag in position {i} of {line!r}")
            return i, level
        tag = m.group(0).lower()
        i += len(tag)
        if tag in self.start_tags:
            level = level - 1 if end_tag else level + 1
        return i, level
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for xml."""
    Xml_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.xml',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4

#@-leo

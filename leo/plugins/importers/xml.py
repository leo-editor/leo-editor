#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18137: * @file ../plugins/importers/xml.py
"""The @auto importer for the xml language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g  # Required.
from leo.plugins.importers.base_importer import Block, Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161121204146.3: ** class Xml_Importer(Importer)
class Xml_Importer(Importer):
    """The importer for the xml language."""

    language = 'xml'
    minimum_block_size = 2  # Helps handle one-line elements.

    # xml_i.add_tags defines all patterns.
    block_patterns: tuple = None
    end_patterns: tuple = None
    start_patterns: tuple = None

    def __init__(self, c: Cmdr, tags_setting: str = 'import_xml_tags') -> None:
        """Xml_Importer.__init__"""
        super().__init__(c)
        self.add_tags(tags_setting)

    #@+others
    #@+node:ekr.20161121204918.1: *3* xml_i.add_tags
    def add_tags(self, setting: str) -> list[str]:
        """
        Add items to self.class/functionTags and from settings.
        """

        # Get the tags from the settings.
        tags = self.c.config.getData(setting) or []

        # Allow both upper and lower case tags.
        tags = [z.lower() for z in tags] + [z.upper() for z in tags]

        # m.group(1) must be the tag name.
        self.block_patterns = tuple([
            (tag, re.compile(fr"\s*<({tag})")) for tag in tags
        ])
        self.start_patterns = tuple(re.compile(fr"\s*<({tag})") for tag in tags)
        self.end_patterns = tuple(re.compile(fr"\s*</({tag})>") for tag in tags)
        return tags
    #@+node:ekr.20230519053541.1: *3* xml_i.compute_headline
    def compute_headline(self, block: Block) -> str:
        """Xml_Importer.compute_headline."""
        n = max(block.start, block.start_body - 1)
        s = block.lines[n].strip()

        # Truncate the headline if necessary.
        return g.truncate(s, 120)
    #@+node:ekr.20230518081757.1: *3* xml_i.find_end_of_block
    def find_end_of_block(self, i1: int, i2: int) -> int:
        """
        i is the index of the line *following* the start of the block.

        Return the index of the start of next block.
        """
        # Get the tag that started the block
        tag_stack: list[str] = []
        tag1: str = None
        line = self.guide_lines[i1 - 1]
        for pattern in self.start_patterns:
            if m := pattern.match(line):
                tag1 = m.group(1).lower()
                tag_stack.append(tag1)
                break
        else:
            raise ImportError('No opening tag')
        i = i1
        while i < i2:
            line = self.guide_lines[i]
            i += 1
            # Push start patterns.
            for pattern in self.start_patterns:
                if m := pattern.match(line):
                    tag = m.group(1).lower()
                    tag_stack.append(tag)
                    break
            for pattern in self.end_patterns:
                if m := pattern.match(line):
                    end_tag = m.group(1).lower()
                    while tag_stack:
                        tag = tag_stack.pop()
                        if tag == end_tag:
                            if not tag_stack:
                                return i
                            break
                    else:
                        return i1  # Don't create a block.
        return i1  # Don't create a block.
    #@+node:ekr.20230126034427.1: *3* xml_i.preprocess_lines
    tag_name_pat = re.compile(r'</?([a-zA-Z]+)')

    # Match two adjacent elements. Don't match comments.
    adjacent_tags_pat = re.compile(r'(.*?)(<[^!].*?>)\s*(<[^!].*?>)')

    def preprocess_lines(self, lines: list[str]) -> list[str]:
        """
        Xml_Importer.preprocess_lines.

        Ensure that closing tags are followed by a newline.

        Importer.import_from_string calls this method before generating lines.
        """

        def repl(m: re.Match) -> str:
            """
                Split lines, adding leading whitespace to the second line.
                *Don't* separate tags if the tags open and close the same element.
            """
            m2 = self.tag_name_pat.match(m.group(2))
            m3 = self.tag_name_pat.match(m.group(3))
            tag_name2 = m2 and m2.group(1) or ''
            tag_name3 = m3 and m3.group(1) or ''
            same_element = (
                tag_name2 == tag_name3
                and not m.group(2).startswith('</')
                and m.group(3).startswith('</')
            )
            lws = g.get_leading_ws(m.group(1))
            sep = '' if same_element else '\n' + lws
            return m.group(1) + m.group(2).rstrip() + sep + m.group(3)

        result_lines = []
        for i, line in enumerate(lines):
            s = re.sub(self.adjacent_tags_pat, repl, line)
            result_lines.extend(g.splitLines(s))
        return result_lines
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

#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18137: * @file ../plugins/importers/xml.py
"""The @auto importer for the xml language."""
from __future__ import annotations
import re
from typing import List, Tuple, TYPE_CHECKING
from leo.core import leoGlobals as g  # Required.
from leo.plugins.importers.linescanner import Importer, ImporterError

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161121204146.3: ** class Xml_Importer(Importer)
class Xml_Importer(Importer):
    """The importer for the xml lanuage."""

    language = 'xml'
    
    # xml_i.add_tags defines all patterns.
    block_patterns: Tuple = None
    end_patterns: Tuple = None
    start_patterns: Tuple = None

    def __init__(self, c: Cmdr, tags_setting: str = 'import_xml_tags') -> None:
        """Xml_Importer.__init__"""
        super().__init__(c)
        self.add_tags(tags_setting)

    #@+others
    #@+node:ekr.20161121204918.1: *3* xml_i.add_tags
    def add_tags(self, setting) -> List[str]:
        """Add items to self.class/functionTags and from settings."""

        # Get the tags from the settings.
        tags = self.c.config.getData(setting) or []
        
        # Allow both upper and lower case tags.
        tags = [z.lower() for z in tags] + [z.upper() for z in tags]
        
        # m.group(1) must be the tag name.
        self.block_patterns = tuple([
            (tag, re.compile(fr"<({tag})")) for tag in tags
        ])
        self.start_patterns = tuple(re.compile(fr"<({tag})") for tag in tags)
        self.end_patterns = tuple(re.compile(fr".*?</({tag})>") for tag in tags)
            
        ### g.printObj(self.block_patterns, tag='add_tags: block_patterns')
        g.printObj(self.start_patterns, tag='add_tags: start_patterns')
        g.printObj(self.end_patterns, tag='add_tags: end_patterns')
        return tags
    #@+node:ekr.20230126034427.1: *3* xml.preprocess_lines
    tag_name_pat = re.compile(r'</?([a-zA-Z]+)')

    # Match two adjacent elements. Don't match comments.
    adjacent_tags_pat = re.compile(r'(.*?)(<[^!].*?>)\s*(<[^!].*?>)')

    def preprocess_lines(self, lines: List[str]) -> List[str]:
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
        g.printObj(result_lines, tag=g.caller())  ###
        return result_lines
    #@+node:ekr.20230518081757.1: *3* xml_i.find_end_of_block
    def find_end_of_block(self, i1: int, i2: int) -> int:
        """
        i is the index of the line *following* the start of the block.

        Return the index of the start of next block.
        """
        i = i1
        tag_stack: List[str] = []
        g.trace('ENTRY', i -1, self.lines[i-1].rstrip())  ###
        assert i1 > 0
        # Push the opening pattern from the previous line.
        line = self.guide_lines[i-1]
        for pattern in self.start_patterns:
            m = pattern.match(line)
            if m:
                tag = m.group(1)
                g.trace('PUSH', tag)
                tag_stack.append(tag)
                break
            else:
                message = 'Can not happen: no open tag'
                g.trace(message)
                raise ImporterError(message)
        while i < i2:
            ignore_flag = False
            line = self.guide_lines[i]
            i += 1
            # Push start patterns that are *not* closed on the same line.
            for pattern in self.start_patterns:
                m = pattern.match(line)
                if m:
                    tag = m.group(1)
                    # Do nothing if the line also contains the same end pattern.
                    ### if tag == 'div':  g.pdb()  ###
                    for end_pattern in self.end_patterns:
                        m2 = end_pattern.match(line)
                        if m2:
                            tag2 = m2.group(1)
                            if tag2 == tag:
                                g.trace('--- ignore', tag, tag2)
                                ignore_flag = True
                                break
                    if not ignore_flag:
                        g.trace('PUSH', tag)
                        tag_stack.append(tag)
                    break
            if ignore_flag:
                continue
            for pattern in self.end_patterns:
                m = pattern.match(line)
                if m:
                    tag = m.group(1)
                    g.trace(' POP', tag)
                    if not tag_stack:
                        message = 'Tag_stack underflow. Input error?'
                        g.trace(message)
                        raise ImporterError(message)
                    start_tag = tag_stack.pop()
                    if start_tag != tag:
                        message =  f"Tag stack mismatch: expected {tag!r}, got {start_tag!r}"
                        g.trace(message)
                        raise ImporterError(message + '\nInput error?')
                    if not tag_stack:
                        g.trace('FOUND', i1, i)
                        g.printObj(self.lines[i1:i])
                        return i  # Found matching tag.
                    break  # Continue scanning for matching tag.   
        g.printObj(tag_stack, tag='FAIL! find_end_of_block. tag_stack')
        return i2
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

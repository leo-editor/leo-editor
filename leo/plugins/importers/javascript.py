#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file ../plugins/importers/javascript.py
"""The @auto importer for JavaScript."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer(Importer)
class JS_Importer(Importer):

    language = 'javascript'

    # These patterns won't find all functions, but they are a reasonable start.

    # Group 1 must be the block name.
    block_patterns: tuple = (
        # (? function name ( .*? {
        ('function', re.compile(r'\s*?\(?function\b\s*([\w\.]*)\s*\(.*?\{')),

        # name: ( function ( .*? {
        ('function', re.compile(r'\s*([\w.]+)\s*\:\s*\(*\s*function\s*\(.*?{')),

        # var name = ( function ( .*? {
        ('function', re.compile(r'\s*\bvar\s+([\w\.]+)\s*=\s*\(*\s*function\s*\(.*?{')),

        # name = ( function ( .*? {
        ('function', re.compile(r'\s*([\w\.]+)\s*=\s*\(*\s*function\s*\(.*?{')),

        # ('const', re.compile(r'\s*\bconst\s*(\w+)\s*=.*?=>')),
        # ('let', re.compile(r'\s*\blet\s*(\w+)\s*=.*?=>')),
    )

    #@+others
    #@+node:ekr.20230919103544.1: *3* js_i.delete_comments_and_strings
    def delete_comments_and_strings(self, lines: list[str]) -> list[str]:
        """
        JS_Importer.delete_comments_and_strings.

        This method also replaces *apparent* regular expressions with spaces.

        In general, tokenizing Javascript is context dependent(!!), but it
        would be unbearable to include a full JS tokenizer.
        """
        string_delims = self.string_list
        line_comment, start_comment, end_comment = g.set_delims_from_language(self.language)
        target = ''  # The string ending a multi-line comment or string.
        escape = '\\'
        result = []
        for line in lines:
            result_line, skip_count = [], 0
            for i, ch in enumerate(line):
                # g.trace(f"{i:3} {ch!r:4} skip: {skip_count} target: {target!r:4}")
                if ch == '\n':
                    break  # Avoid appending the newline twice.
                elif skip_count > 0:
                    # Replace the character with a blank.
                    result_line.append(' ')
                    skip_count -= 1
                elif ch == escape:  # #3620: test for escape before testing for target.
                    assert skip_count == 0
                    result_line.append(' ')
                    skip_count = 1
                elif target:
                    result_line.append(' ')
                    # Clear the target, but skip any remaining characters of the target.
                    if g.match(line, i, target):
                        skip_count = max(0, (len(target) - 1))
                        target = ''
                elif line_comment and line.startswith(line_comment, i):
                    # Skip the rest of the line. It can't contain significant characters.
                    break
                elif any(g.match(line, i, z) for z in string_delims):
                    # Allow multi-character string delimiters.
                    result_line.append(' ')
                    for z in string_delims:
                        if g.match(line, i, z):
                            target = z
                            skip_count = max(0, (len(z) - 1))
                            break
                elif start_comment and g.match(line, i, start_comment):
                    result_line.append(' ')
                    target = end_comment
                    skip_count = max(0, len(start_comment) - 1)
                elif ch == '/':
                    j = line.find('/', i + 1)
                    if j > -1:
                        # An *apparent* regular expression.
                        result_line.append(' ')
                        skip_count = j - i + 1
                    else:
                        result_line.append(ch)
                else:
                    result_line.append(ch)

            # End the line and append it to the result.
            # Strip trailing whitespace. It can't affect significant characters.
            end_s = '\n' if line.endswith('\n') else ''
            result.append(''.join(result_line).rstrip() + end_s)
        assert len(result) == len(lines)  # A crucial invariant.
        return result
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

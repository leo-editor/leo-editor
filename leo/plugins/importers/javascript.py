#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file ../plugins/importers/javascript.py
"""The @auto importer for JavaScript."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
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

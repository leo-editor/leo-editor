#@+leo-ver=5-thin
#@+node:ekr.20231012140553.1: * @file ../plugins/importers/scheme.py
"""The @auto importer for the scheme language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.elisp import Elisp_Importer
# from leo.core import leoGlobals as g

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20231012140553.2: ** class Scheme_Importer(Elisp_Importer)
class Scheme_Importer(Elisp_Importer):
    """The importer for the Scheme language."""

    language = 'scheme'

    block_patterns: tuple = (
        # ( define name
        ('define-library', re.compile(r'\s*\(\s*\bdefine-library\s*\(?\s*([\w_-]+)')),
        ('define-module', re.compile(r'\s*\(\s*\bdefine-module\s*\(?\s*([\w_-]+)')),
        ('define-public', re.compile(r'\s*\(\s*\bdefine-public\s*\(?\s*([\w_-]+)')),
        ('define', re.compile(r'\s*\(\s*\bdefine\s*\(?([\w_-]+)')),
    )
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for scheme."""
    Scheme_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.scm',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo

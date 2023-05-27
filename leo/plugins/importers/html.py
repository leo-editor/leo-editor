#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18138: * @file ../plugins/importers/html.py
"""The @auto importer for HTML."""
from __future__ import annotations
from typing import TYPE_CHECKING
from leo.plugins.importers.xml import Xml_Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20140723122936.18136: ** class Html_Importer(Xml_Importer)
class Html_Importer(Xml_Importer):

    language = 'html'

    def __init__(self, c: Cmdr) -> None:
        """Html_Importer.__init__"""
        super().__init__(c, tags_setting='import_html_tags')
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for html."""
    Html_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.html', '.htm',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo

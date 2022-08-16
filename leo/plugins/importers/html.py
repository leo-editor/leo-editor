#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18138: * @file ../plugins/importers/html.py
"""The @auto importer for HTML."""
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.xml import Xml_Importer
#@+others
#@+node:ekr.20140723122936.18136: ** class Html_Importer(Xml_Importer)
class Html_Importer(Xml_Importer):

    def __init__(self, c: Cmdr) -> None:
        """Html_Importer.__init__"""
        super().__init__(c, tags_setting='import_html_tags')
        self.name = 'html'
        # self.void_tags = [
            # # A small kludge: add !DOCTYPE.
            # '!doctype',
            # # void elements in HTML 4.01/XHTML 1.0 Strict:
            # 'area', 'base', 'br', 'col', 'hr', 'img', 'input', 'link', 'meta', 'param',
            # # void elements in HTML5:
            # 'command', 'keygen', 'source',
        # ]
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

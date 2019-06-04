#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18138: * @file importers/html.py
'''The @auto importer for HTML.'''
import leo.plugins.importers.xml as xml
Xml_Importer = xml.Xml_Importer
#@+others
#@+node:ekr.20140723122936.18136: ** class Html_Importer(Xml_Importer)
class Html_Importer(Xml_Importer):

    def __init__(self, importCommands, **kwargs):
        '''Html_Importer.__init__'''
        super().__init__(importCommands,
            tags_setting='import_html_tags')
        self.name = 'html'
        self.void_tags = [
            # A small kludge: add !DOCTYPE.
            '!doctype',
            # void elements in HTML 4.01/XHTML 1.0 Strict:
            'area', 'base', 'br', 'col', 'hr', 'img', 'input', 'link', 'meta', 'param',
            # void elements in HTML5:
            'command', 'keygen', 'source',
        ]
#@-others
importer_dict = {
    'class': Html_Importer,
    'extensions': ['.html', '.htm',],
}
#@@language python
#@@tabwidth -4
#@-leo

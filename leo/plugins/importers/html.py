#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18138: * @file importers/html.py
'''The @auto importer for HTML.'''
import leo.plugins.importers.xml as xml
Xml_Importer = xml.Xml_Importer
#@+others
#@+node:ekr.20140723122936.18136: ** class Html_Importer(Xml_Importer)
class Html_Importer(Xml_Importer):

    def __init__(self, importCommands, atAuto):
        '''Html_Importer.__init__'''
        # Init the base class.
        Xml_Importer.__init__(self,
            importCommands,
            atAuto,
            tags_setting='import_html_tags',
        )
        self.name = 'html'
#@-others
importer_dict = {
    'class': Html_Importer,
    'extensions': ['.html', '.htm',],
}
#@@language python
#@@tabwidth -4
#@-leo

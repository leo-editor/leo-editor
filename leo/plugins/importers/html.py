#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18138: * @file importers/html.py
'''The @auto importer for HTML.'''
import leo.core.leoImport as leoImport
import leo.plugins.importers.xml as xml
XmlScanner = xml.XmlScanner
#@+others
#@+node:ekr.20140723122936.18136: ** class HtmlScanner (XmlScanner)
class HtmlScanner (XmlScanner):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        XmlScanner.__init__(self,importCommands,atAuto,tags_setting='import_html_tags')

    #@+others
    #@-others
#@-others
importer_dict = {
    'class': HtmlScanner,
    'extensions': ['.html',],
    'name': 'HTML',
}
#@-leo

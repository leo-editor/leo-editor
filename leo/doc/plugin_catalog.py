#@+leo-ver=5-thin
#@+node:ekr.20101112045055.5064: * @file plugin_catalog.py
#@@language python

#@+<< docstring >>
#@+node:ekr.20111018061632.15902: ** << docstring >>
"""
Extract plugin status and docs. from docstrings

:last_update: 20100301
:plugin_status: initial development
:gui: qt
:maintainer: terry_n_brown@yahoo.com

Generate merged documentation from plugins (or any .py files).

E.g.::

    python doc/plugin_catalog.py \
      --css-file=.../Sphinx-0.6.5/sphinx/themes/sphinxdoc/static/sphinxdoc.css \
      plugins/ doc/plugin_docs.html

Options:
  -h, --help            show this help message and exit
  --location=LOCATION   Add a location to the list to search
  --css-file=CSS_FILE   Use this CSS file in the HTML output
  --max-files=MAX_FILES
                        Stop after this many files, mainly for testing
  --include-contents    Include table of contents (the summary is more useful)
  --no-summary          Don't generate the summary
  --show-paths          Show paths to .py files, useful for resolving RST
                        errors
  --output=OUTPUT       Filename for the html output
  --xml-output=XML_OUTPUT
                        Filename for optional xml output, mainly for testing

TODO

 - Design encoding of plugin status in rst docstring

   - interface (qt)
   - maintained / working / old / broken
   - maintainer

 - List of commands provided by plugin (or command pattern, e.g active-path-\*)
 - List of semantic tags provided by plugin (@bookmark...)

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20111018061632.15903: ** << imports >>
import os
import sys
import ast
import time
from copy import deepcopy
import optparse

try:
    ok = True
    from docutils.core import publish_doctree, publish_from_doctree
    from docutils import nodes
    from docutils.transforms.parts import Contents
    from docutils.utils import SystemMessage
except Exception:
    sys.stderr.write('plugin_catalog.py: can not import docutils\n')
    ok = False
#@-<< imports >>

#@+others
#@+node:tbrown.20111018094615.23242: ** err
def err(s):
    sys.stderr.write(s)
    sys.stderr.flush()
#@+node:ekr.20111018061632.15913: ** class PluginCatalog
class PluginCatalog(object):
    
    """see module docs. and make_parser()"""
    
    #@+others
    #@+node:ekr.20111018061632.15906: *3* __init__
    def __init__(self, opt):

        """opt - see make_parser() or --help"""

        self.opt = opt
        self.id_num = 0  # for generating ids for the doctree
        self.document = None
    #@+node:ekr.20111018061632.15910: *3* add_ids
    def add_ids(self, node, depth=0):

        """Recursively add ids starting with 'lid' to doctree node.

        Always id the top level node, and also document, section, and topic
        nodes below it."""

        if hasattr(node, 'tagname'):
            if depth == 0 or node.tagname in ('document', 'section', 'topic'):
                if True or not node['ids']:
                    self.id_num += 1
                    node['ids'].append('lid'+str(self.id_num))
            for child in node:
                self.add_ids(child, depth+1)
    #@+node:ekr.20111018061632.15911: *3* first_text
    def first_text(self, node):

        """find first paragraph to use as a summary"""

        if node.tagname == 'paragraph':
            return deepcopy(node)
        else:
            for child in node:
                if hasattr(child, 'tagname'):
                    ans = self.first_text(child)
                    if ans:
                        return ans

        return None
    #@+node:ekr.20111018061632.15907: *3* get_doc_strings
    def get_doc_strings(self):

        """collect docstrings in .py files in specified locations"""

        doc_strings = []
        cnt = 0
        opt = self.opt  

        for loc in opt.location:

            for path, dummy, files in os.walk(loc):
                break  # only want the first answer

            for file_name in sorted(files, key=lambda x:x.lower()):
                if not file_name.lower().endswith('.py'):
                    continue

                file_path = os.path.join(path, file_name)

                doc_string = None

                src = open(file_path).read()
                src = src.replace('\r\n', '\n').replace('\r','\n')+'\n'
                try:
                    ast_info = ast.parse(src)
                    doc_string = ast.get_docstring(ast_info)
                except SyntaxError:
                    doc_string = "**SYNTAX ERROR IN MODULE SOURCE**"

                if not doc_string and file_name != '__init__.py':
                    doc_string = "**NO DOCSTRING**"

                if not doc_string:
                    continue  # don't whine about __init__.py

                if opt.show_paths:
                    err("Processing: '%s'\n" % file_path)
                try:
                    doc_tree = publish_doctree(doc_string)
                except SystemMessage:
                    doc_tree = publish_doctree("""
                    Docutils could not parse docstring

                    RST error level SEVERE/4 or higher in '%s'""" %
                        file_path)

                doc_strings.append( (file_name, file_path, doc_tree) )

                cnt += 1
                if opt.max_files and cnt == opt.max_files:
                    break

        return doc_strings
    #@+node:ekr.20111018061632.15908: *3* make_document
    def make_document(self, doc_strings):
        
        """make doctree representation of collected fragments"""

        opt = self.opt  

        big_doc = publish_doctree("")
        self.document = big_doc
        big_doc += nodes.title(text="Plugins listing generated %s" %
            time.asctime())

        contents = nodes.container()
        if opt.include_contents:
            big_doc += nodes.topic('', nodes.title(text='Contents'), contents)

        if not opt.no_summary:
            def_list = nodes.definition_list()
            alpha_list = nodes.paragraph()
            big_doc += nodes.section('', nodes.title(text="Plugins summary"),
                alpha_list, def_list)

        last_alpha = ''

        for doc in doc_strings:
            
            section = nodes.section()
            big_doc += section
            section += nodes.title(text=doc[0])

            self.add_ids(section)

            if not opt.no_summary:
                firstpara = (self.first_text(doc[2]) or
                    nodes.paragraph(text='No summary found'))
                reference = nodes.reference('', refid=section['ids'][0],
                    name = doc[0], anonymous=1)
                reference += nodes.Text(doc[0])
                def_list += nodes.definition_list_item('',
                    nodes.term('', '', reference),
                    nodes.definition('', firstpara)
                )

                # add letter quick index entry if needed
                if doc[0][0].upper() != last_alpha:
                    last_alpha = doc[0][0].upper()
                    self.add_ids(reference)
                    alpha_list += nodes.reference('',
                        nodes.Text(last_alpha+' '),
                        refid=reference['ids'][0], name = doc[0], anonymous=1)

            for element in doc[2]:
                # if the docstring has titles, we need another level
                if element.tagname == 'title':
                    subsection = nodes.section() 
                    section += subsection
                    section = subsection
                    break

            for element in doc[2]:
                try:
                    section += element.deepcopy()
                except TypeError:
                    err(
                        'Element.deepcopy() failed, dropped element for %s\n' %
                        doc[0])

        if opt.include_contents:
            contents.details = {'text': 'Contents here'}

            self.add_ids(big_doc)
            transform = Contents(big_doc, contents)
            transform.apply()

        return big_doc
        
    #@+node:ekr.20111018061632.15905: *3* make_parser
    @staticmethod
    def make_parser():
        """Return an optparse.OptionParser"""

        parser = optparse.OptionParser("Usage: plug_catalog.py [options] dir1 [dir2 ...] output.html")

        parser.add_option("--location", action="append", type="string",
            help="Add a location to the list to search", default=[])
        parser.add_option("--css-file", type="string",
            help="Use this CSS file in the HTML output")
        parser.add_option("--max-files", type="int",
            help="Stop after this many files, mainly for testing")
        parser.add_option("--include-contents", action="store_true", 
            default=False,
            help="Include table of contents (the summary is more useful)")
        parser.add_option("--no-summary", action="store_true", default=False,
            help="Don't generate the summary")
        parser.add_option("--show-paths", action="store_true", default=False,
            help="Show paths to .py files, useful for resolving RST errors")
        parser.add_option("--output", type="string", default=None,
            help="Filename for the html output")
        parser.add_option("--xml-output", type="string", default=None,
            help="Filename for optional xml output, mainly for testing")

        return parser
    #@+node:ekr.20111018061632.15909: *3* run
    def run(self):

        """run with the supplied options, see make_parser()"""

        opt = self.opt  

        doc_strings = self.get_doc_strings()

        big_doc = self.make_document(doc_strings)

        settings_overrides = {}
        if opt.css_file:
            settings_overrides['stylesheet_path'] = opt.css_file

        open(opt.output, 'wb').write(
            publish_from_doctree(big_doc, writer_name='html',
                settings_overrides = settings_overrides)
        )
        err("Wrote '%s'\n" % opt.output)

        if opt.xml_output:
            open(opt.xml_output, 'wb').write(
                publish_from_doctree(big_doc, writer_name='xml',
                    settings_overrides = {'indents': True})
            )
            err("Wrote '%s'\n" % opt.xml_output)
    #@-others
#@+node:ekr.20111018061632.15912: ** main
def main():
    
    """create and run a PluginCatalog"""
    
    opts, args = PluginCatalog.make_parser().parse_args()

    if args and not opts.output:
        opts.output = args[-1]
        del args[-1]

    opts.location.extend(args)

    plugin_catalog = PluginCatalog(opts)
    plugin_catalog.run()
#@-others

if __name__ == "__main__":
    if ok:
        main()
#@-leo


"""
Extract plugin status and docs. from docstrings

last_update: 20100301
plugin_status: inital development
gui: qt and tk
maintainer: terry_n_brown@yahoo.com

plugin_catalog.py searches for module docstrings like this one in the .py files
in .../leo/plugins/ or another location.

.. leo_plugin_auto_doc
"""

"""
TODO

- List of provided commands (or command pattern, e.g active-path-*)
- Introduced semantic tags (@bookmark...)
"""

import os
import ast
from docutils.core import publish_doctree, publish_from_doctree
from docutils import nodes
from docutils.transforms.parts import Contents
import time
from copy import deepcopy
import optparse
import sys

class PluginCatalog(object):
    """see module docs. and make_parser()"""

    @staticmethod
    def make_parser():
        """Return an optparse.OptionParser"""

        parser = optparse.OptionParser()

        parser.add_option("--location", action="append", type="string",
            help="REQUIRED, add a location to the list to search")
        parser.add_option("--css-file", type="string",
            help="Use this CSS file in the HTML output")
        parser.add_option("--max-files", type="int",
            help="Stope after this many files, mainly for testing")
        parser.add_option("--include-contents", action="store_true", default=False,
            help="Include table of contents (the summary is more useful)")
        parser.add_option("--no-summary", action="store_true", default=False,
            help="Don't generate the summary")
        parser.add_option("--output", type="string",
            help="REQUIRED, filename for the html output")
        parser.add_option("--xml-output", type="string", default=None,
            help="Filename for optional xml output, mainly for testing")

        return parser

    def __init__(self, opt):
        """opt - see make_parser()"""

        self.id_num = 0  # for generating ids for the doctree

    def run(self):
        """run with the supplied options"""

        doc_strings = []
        cnt = 0

        for loc in opt.location:

            path, dirs, files = os.walk(loc).next()

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

                # sys.stderr.write('%s\n' % file_path)
                doc_tree = publish_doctree(doc_string)

                doc_strings.append( (file_name, file_path, doc_tree) )

                cnt += 1
                if opt.max_files and cnt == opt.max_files:
                    break

        big_doc = publish_doctree("")
        self.document = big_doc
        big_doc += nodes.title(text="Plugins listing generated %s" %
            time.asctime())

        contents = nodes.container()
        if opt.include_contents:
            big_doc += nodes.topic('',nodes.title(text='Contents'), contents)

        if not opt.no_summary:
            def_list = nodes.definition_list()
            big_doc += nodes.section('', nodes.title(text="Plugins summary"),
                def_list)

        for doc in doc_strings:
            section = nodes.section()
            big_doc += section
            title = nodes.title(text=doc[0])
            section += title

            self.add_ids(section)

            if not opt.no_summary:
                firstpara = (self.first_text(doc[2]) or
                    nodes.paragraph(text='No summary found'))
                refid=section['ids'][0]
                reference=nodes.reference('', refid=refid, name=doc[0], anonymous=1)
                reference += nodes.Text(doc[0])
                def_list += nodes.definition_list_item('',
                    nodes.term('', '', reference),
                    nodes.definition('', firstpara)
                )

            for element in doc[2]:
                # if the docstring has titles, we need another level
                if element.tagname == 'title':
                    subsection = nodes.section() 
                    section += subsection
                    section = subsection
                    break

            for element in doc[2]:
                section += element.deepcopy()

        if opt.include_contents:
            contents.details = {'text': 'Contents here'}

            self.add_ids(big_doc)
            transform = Contents(big_doc, contents)
            transform.apply()

        settings_overrides = {}
        if opt.css_file:
            settings_overrides['stylesheet_path'] = opt.css_file
        open(opt.output, 'w').write(
          publish_from_doctree(big_doc, writer_name='html',
              settings_overrides = settings_overrides)
        )

        if opt.xml_output:
            open(opt.xml_output, 'w').write(
              publish_from_doctree(big_doc, writer_name='xml',
                  settings_overrides = {'indents': True})
            )

    def add_ids(self, node):
        """recursively add ids starting with 'lid' to doctree node"""
        if hasattr(node, 'tagname'):
            if node.tagname in ('document', 'section', 'topic'):
                if True or not node['ids']:
                    self.id_num += 1
                    node['ids'].append('lid'+str(self.id_num))
            for child in node:
                self.add_ids(child)

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



if __name__ == "__main__":

    opt, arg = PluginCatalog.make_parser().parse_args()

    pc = PluginCatalog(opt)
    pc.run()


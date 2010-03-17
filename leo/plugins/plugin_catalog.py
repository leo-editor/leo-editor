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

opt = type('o', (), {})
opt.include_contents = False

#from xml.etree import ElementTree
#from copy import deepcopy

class PluginCatalog(object):
    """see module docs."""

    def __init__(self, locations=[]):
        """locations - places to search for leo modules"""

        doc_strings = []

        for path, dirs, files in os.walk("plugins"):

            cnt = 0
            for file_name in sorted(files, key=lambda x:x.lower()):
                if not file_name.lower().endswith('.py'):
                    continue

                file_path = os.path.join(path, file_name)

                print file_path

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

                print doc_string

                if not doc_string:
                    continue

                #X xml_string = publish_string(doc_string,
                #X     writer_name = 'xml',
                #X     # settings_overrides = {'indents': True},
                #X )

                #X    doc = ElementTree.fromstring(xml_string)

                doc_tree = publish_doctree(doc_string)

                doc_strings.append( (file_name, file_path, doc_tree) )

                cnt += 1
                # if cnt == 10: break

            break

        #X big_doc = ElementTree.fromstring("<document/>")
        #X for doc in doc_strings:
        #X     element = ElementTree.SubElement(big_doc,'section')
        #X     ElementTree.SubElement(element, 'title').text = doc[1]
        #X     for child in doc[2].getchildren():
        #X         element.append(deepcopy(child))

        #X    ElementTree.ElementTree(big_doc).write(open('pcat.xml', 'w'))

        # big_doc = nodes.document(None, None)
        big_doc = publish_doctree("")
        self.document = big_doc
        big_doc += nodes.title(text="Plugins listing generated %s" %
            time.asctime())

        contents = nodes.container()
        if opt.include_contents:
            big_doc += nodes.topic('',nodes.title(text='Contents'), contents)

        def_list = nodes.definition_list()
        big_doc += nodes.section('', nodes.title(text="Plugins summary"),
            def_list)

        self.id_num = 0

        for doc in doc_strings:
            section = nodes.section()
            big_doc += section
            title = nodes.title(text=doc[0])
            section += title

            # self.add_ids(doc[2])
            self.add_ids(section)

            firstpara = (self.first_text(doc[2]) or
                nodes.paragraph(text='No summary found'))
            refid=section['ids'][0]
            print refid,doc[0]
            reference=nodes.reference('', refid=refid, name=doc[0], anonymous=1)
            reference += nodes.Text(doc[0])
            def_list += nodes.definition_list_item('',
                nodes.term('', '', reference),
                nodes.definition('', firstpara)
            )

            for element in doc[2]:
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

        open('d.html', 'w').write(
          publish_from_doctree(big_doc, writer_name='html',
              settings_overrides = {'stylesheet_path': "/home/tbrown/Desktop/Package/Sphinx-0.6.5/sphinx/themes/sphinxdoc/static/sphinxdoc.css"})
        )
        open('pcat.xml', 'w').write(
          publish_from_doctree(big_doc, writer_name='xml',
              settings_overrides = {'indents': True})
        )

        print len(def_list)

    def add_ids(self, node):
        if hasattr(node, 'tagname'):
            if node.tagname in ('document', 'section', 'topic'):
                if True or not node['ids']:
                    self.id_num += 1
                    node['ids'].append('lid'+str(self.id_num))
            for child in node:
                self.add_ids(child)
    def first_text(self, node):

        if node.tagname == 'paragraph':
            return deepcopy(node)
        else:
            for child in node:
                if hasattr(child, 'tagname'):
                    ans = self.first_text(child)
                    if ans:
                        return ans

        return None


PluginCatalog()

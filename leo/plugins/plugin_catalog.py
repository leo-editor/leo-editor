"""
plugin_catalog.py - extract plugin status and docs. from docstring
==================================================================

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
from xml.etree import ElementTree
from copy import deepcopy

class PluginCatalog(object):
    """see module docs."""

    def __init__(self, locations=[]):
        """locations - places to search for leo modules"""

        doc_strings = []

        for path, dirs, files in os.walk("plugins"):

            cnt = 0
            for file_name in sorted(files):
                if not file_name.lower().endswith('.py'):
                    continue

                file_path = os.path.join(path, file_name)

                print file_path

                src = open(file_path).read()
                src = src.replace('\r\n', '\n').replace('\r','\n')+'\n'
                try:
                    ast_info = ast.parse(src)
                    doc_string = ast.get_docstring(ast_info)
                except SyntaxError:
                    doc_string = "**SYNTAX ERROR IN MODULE SOURCE**"

                if not doc_string:
                    doc_string = "**NO DOCSTRING**"

                print doc_string

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
        for doc in doc_strings:
            section = nodes.section()
            big_doc += section
            section += nodes.title(text=doc[0])

            for element in doc[2]:
                if element.tagname == 'title':
                    subsection = nodes.section() 
                    section += subsection
                    section = subsection
                    break

            for element in doc[2]:
                section += element.deepcopy()

        open('d.html', 'w').write(
          publish_from_doctree(big_doc, writer_name='html')
        )
        open('pcat.xml', 'w').write(
          publish_from_doctree(big_doc, writer_name='xml',
              settings_overrides = {'indents': True})
        )

PluginCatalog()

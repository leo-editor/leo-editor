#@+leo-ver=5-thin
#@+node:tbrown.20110428144124.29061: * @file ../plugins/xml_edit.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:tbrown.20110428102237.20322: ** xml_edit declarations
""" Provides commands (Alt-x) for importing and exporting XML from a Leo
outline. These commands are to XML what ``@auto-rst`` is to
reStructuredText.

``xml2leo`` imports an .xml file into the node following the currently
selected node.  ``leo2xml`` exports the current subtree to an .xml file
the user selects.

``xml_validate``, if executed on the top node in the
Leo xml tree, reports any errors in XML generation or DTD validation,
based on the DTD referenced from the XML itself.  If there's no DTD
it reports that as an error.

``leo2xml2leo`` takes the selected Leo subtree representing an XML file,
converts it to XML internally, and then creates a new Leo subtree from
that XML after the original, with 'NEW ' at the start of the top node's
name.  This updates all the headlines, so that the convenience only
previews (see below) are updated.  The original can be deleted if the
new subtree seems correct.

Conventions
===========

This is a valid XML file::

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE dml SYSTEM "dml.dtd">
    <?xml-stylesheet href="common.css"?>
    <dml xmlns='http://example.com/' xmlns:other='http://other.com/'/>
      <block type='example'>Here's <other:b>some</other:b> text</block>
    </dml>
    <!-- This is the last line -->

Note the processing instruction (xml-stylesheet), the DTD (DOCTYPE),
the trailing comment (after the closing tag), and the pernicious
mixed content (three separate pieces of text in the ``<block/>`` element).
These commands attempt to deal with all of this.

 - A top level Leo node is created to hold these top level parts.  Its
   headline is the basename of the file.
 - The xml declaration is placed in the body of
   this top level Leo node
 - Below that, in the same body text, appears a simple namespace map::

     http://example.com/
     other: http://other.com/
     ...

   i.e. the default namespace first, and then any prefixed name spaces.
 - Below that, in the same body text, appears the ``DOCTYPE`` declaration
 - Children are added to this top level Leo node to represent the
   top level elements in the xml file.  Headlines have the following
   meanings:

       - ``? pi-target some="other" __CHK`` - i.e. questionmark,
         space, name of processing instruction target, start of processing
         instruction content.  Only the questionmark, which indicates
         the processing instruction, and the first word, which indicates
         the processing instruction target, matter.  The remainder is just
         a convenience preview of the processing instruction content, which
         is the Leo node's body text.

       - ``# This is *really* imp`` - i.e. hash,
         space, start of comment content.  Only the hash, which indicates
         the comment, matters.  The remainder is just
         a convenience preview of the comment content, which
         is the Leo node's body text.

       - ``tagname name_attribute start of element text`` - i.e. the name
         of an element followed by a convenience preview of the element's
         text content.  If the element has a ``name`` attribute that's
         included at the start of the text preview.  Only the first word
         matters, it's the name of the element.
 - Element's text is placed in the Leo node's body.  If the element has
   tailing text (the ``" text"`` tailing the ``<other:b/>`` element
   in the above example), that occurs in the Leo node's body separated
   by the `tailing text sentinel`::

       @________________________________TAIL_TEXT________________________________@

 - Element's attributes are stored in a dict ``p.v.u['_XML']['_edit']``
   on the Leo node. ``'_XML'`` is the uA prefix for these commands, and
   ``'_edit'`` is used by the ``attrib_edit`` plugin to identify
   attributes it should present to the user for editing. The
   ``attrib_edit`` plugin **should be enabled** and its ``v.u mode``
   activated (through its submenu on the Plugins menu). The attribute
   edit panel initially appears as a tab in the log pane, although it
   can be moved around by right clicking on the pane dividers if the
   ``viewrendered`` and ``free_layout`` plugins are enabled.

"""

# broad-exception-raised: Not valid in later pylints.

import os
import traceback  # for XML parse error display
from typing import Any
from lxml import etree
from leo.core import leoGlobals as g

# top level entry in uA
uAxml = '_XML'

tail_sentinel = """
@________________________________TAIL_TEXT________________________________@
"""

# for file open/save dialog
filetypes = [
    ("XML files", "*.xml"),
    ("All files", "*"),
]

# xml namespace mapping from prefix to full namespace
NSMAP: dict[str, Any] = {}

#@+node:tbrown.20110428102237.20325: ** append_element
def append_element(xml_node, to_leo_node):
    """handle appending xml_node which may be Element, Comment, or
    ProcessingInstruction.  Recurses for Element.
    """
    if isinstance(xml_node, etree._Comment):
        leo_node = to_leo_node.insertAsLastChild()
        leo_node.h = "# %s" % ' '.join(xml_node.text.split())[:40]
        leo_node.b = xml_node.text

    elif isinstance(xml_node, etree._ProcessingInstruction):
        leo_node = to_leo_node.insertAsLastChild()
        r = [xml_node.target] + xml_node.text.split()[:40]
        leo_node.h = "? %s" % ' '.join(r)
        leo_node.b = xml_node.text

    elif isinstance(xml_node, etree._Element):
        leo_node = to_leo_node.insertAsLastChild()

        name = [get_tag(xml_node)]
        if xml_node.get('name'):
            name.append(xml_node.get('name'))
        if xml_node.xpath("./*[name()='name']"):
            name.append(xml_node.xpath("./*[name()='name']")[0].text or '')
        if xml_node.text:  # first 9 words from text
            name.extend(xml_node.text.split(None, 10)[:9])

        leo_node.h = ' '.join(name)[:40]
        if xml_node.text is not None:
            leo_node.b = xml_node.text

        if xml_node.tail and xml_node.tail.strip():
            leo_node.b += tail_sentinel + xml_node.tail

        for k in sorted(xml_node.attrib.keys()):
            if uAxml not in leo_node.v.u:
                leo_node.v.u[uAxml] = {}
            if '_edit' not in leo_node.v.u[uAxml]:
                leo_node.v.u[uAxml]['_edit'] = {}
            aname = get_tag(xml_node, k)
            leo_node.v.u[uAxml]['_edit'][aname] = xml_node.get(k)

        for xml_child in xml_node:
            append_element(xml_child, leo_node)

#@+node:tbrown.20110429155827.20762: ** cd_here
def cd_here(c, p):
    """attempt to cd to the directory in effect at p according
    to Leo's @path concept
    """
    try:
        os.chdir(c.getNodePath(p))
    except Exception:
        pass  # well, at least we tried
#@+node:tbrown.20110428102237.20327: ** get_element
def get_element(leo_node):
    """recursively read from leo nodes and write into an Element tree
    """
    # comment
    if leo_node.h[:2] == '# ':
        return etree.Comment(leo_node.b)

    # processing instruction
    if leo_node.h[:2] == '? ':
        target = leo_node.h.split()[1]
        return etree.ProcessingInstruction(target, leo_node.b)

    # regular element
    ele = etree.Element(make_tag(leo_node.h.split()[0]), nsmap=NSMAP)
    if uAxml in leo_node.v.u and '_edit' in leo_node.v.u[uAxml]:
        d = leo_node.v.u[uAxml]['_edit']
        for k in d:
            ele.set(make_tag(k), d[k])

    if tail_sentinel in leo_node.b:
        ele.text, ele.tail = leo_node.b.split(tail_sentinel, 1)
    else:
        ele.text = leo_node.b

    for child in leo_node.children():
        ele.append(get_element(child))

    return ele

#@+node:tbrown.20110428102237.20323: ** get_tag
def get_tag(xml_node, attrib=None):
    """replace {http://full.name.space.com/}element with fns:element
    """
    if attrib:
        name = attrib
    else:
        name = xml_node.tag
    for k, v in xml_node.nsmap.items():
        NSMAP[k] = v
        x = "{%s}" % v
        r = k + ":" if k else ""
        if name.startswith(x):
            name = name.replace(x, r)
            # don't break here, this loop also updates NSMAP for later
    return name

#@+node:ekr.20110523130519.18190: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    return True
#@+node:tbrown.20110428102237.20329: ** leo2xml
@g.command('leo2xml')
def leo2xml(event):
    """wrapper to write xml for current node
    """

    c = event['c']
    p = c.p

    ans = xml_for_subtree(p)

    cd_here(c, p)
    file_name = g.app.gui.runSaveFileDialog(
        c, title="Open", filetypes=filetypes, defaultextension=".xml")
    if not file_name:
        raise ImportError("No file selected")

    open(file_name, 'w').write(ans)

    c.redraw()
#@+node:tbrown.20110501200908.19857: ** leo2xml2leo
@g.command('leo2xml2leo')
def leo2xml2leo(event):
    """wrapper to cycle leo->xml->leo, mostly to clean up headers
    """

    c = event['c']
    p = c.p
    oh = p.h

    xml_ = xml_for_subtree(p)
    if xml_.startswith('<?xml '):
        # Unicode strings with encoding declaration are not supported
        # so cut off the xml declaration
        xml_ = xml_.split('\n', 1)[1]

    nd = xml2leo({'c': c}, from_string=xml_)

    nd.h = 'NEW ' + oh

    c.selectPosition(nd)
    c.redraw()
#@+node:tbrown.20110428102237.20324: ** make_tag
def make_tag(tag):
    """replace  fns:element with {http://full.name.space.com/}element
    """
    if ':' not in tag or '{' in tag:
        # 'xml:space' becomes '{http://www.w3.org/XML/1998/namespace}space'
        return tag

    ns, tag = tag.split(':', 1)

    return '{%s}%s' % (NSMAP[ns], tag)
#@+node:tbrown.20110428102237.20326: ** xml2leo
@g.command('xml2leo')
def xml2leo(event, from_string=None):
    """handle import of an .xml file, places new subtree after c.p
    """
    c = event['c']
    p = c.p

    if from_string:
        parser_func = etree.fromstring
        file_name = from_string
    else:
        parser_func = etree.parse
        cd_here(c, p)
        file_name = g.app.gui.runOpenFileDialog(
                c, title="Open", filetypes=filetypes, defaultextension=".xml")

        if not file_name:
            raise ImportError("No file selected")

    try:
        xml_ = parser_func(file_name)
    except etree.XMLSyntaxError:
        xml_ = parser_func(file_name, parser=etree.HTMLParser())
    except Exception:
        g.es("Failed to read '%s'" % file_name)
        raise

    if from_string:
        # etree.fromstring and etree.parse return Element and
        # ElementTree respectively
        xml_ = etree.ElementTree(xml_)

    nd = p.insertAfter()
    nd.h = os.path.basename(file_name)

    # the root Element isn't necessarily the first thing in the XML file
    # move to the beginning of the list to capture preceding comments
    # and processing instructions
    toplevel = xml_.getroot()
    while toplevel.getprevious() is not None:
        toplevel = toplevel.getprevious()

    # move through list, covering root Element and any  comments
    # or processing instructions which follow it
    while toplevel is not None:
        append_element(toplevel, nd)
        toplevel = toplevel.getnext()

    nd.b = '<?xml version="%s"?>\n' % (xml_.docinfo.xml_version or '1.0')
    if xml_.docinfo.encoding:
        nd.b = '<?xml version="%s" encoding="%s"?>\n' % (
        xml_.docinfo.xml_version or '1.0', xml_.docinfo.encoding)
    if NSMAP:
        for k in sorted(NSMAP):
            if k:
                nd.b += "%s: %s\n" % (k, NSMAP[k])
            else:
                nd.b += "%s\n" % NSMAP[k]
    nd.b += xml_.docinfo.doctype + '\n'

    c.redraw()

    return nd
#@+node:tbrown.20110428102237.20328: ** xml_for_subtree
def xml_for_subtree(nd):
    """get the xml for the subtree at nd
    """
    lines = nd.b.split('\n')

    line0 = 0
    while line0 < len(lines) and not lines[line0].strip():
        line0 += 1

    xml_dec = None
    if line0 < len(lines) and lines[line0].startswith('<?xml '):
        xml_dec = lines.pop(0)

    while lines and lines[0].strip() and not lines[0].startswith('<'):
        kv = lines.pop(0).split(': ', 1)
        if len(kv) == 1:
            NSMAP[None] = kv[0]
        else:
            NSMAP[kv[0]] = kv[1]

    dtd = '\n'.join(lines).strip()

    elements = [get_element(i) for i in nd.children()]

    ans = []
    if xml_dec is not None:
        ans.append(xml_dec)
    if dtd:
        ans.append(dtd)

    for ele in elements:
        ans.append(etree.tostring(ele, pretty_print=True))

    ans = [g.toUnicode(z) for z in ans]  # EKR: 2011/04/29

    return '\n'.join(ans)
#@+node:tbrown.20110429140247.20760: ** xml_validate
@g.command('xml-validate')
def xml_validate(event):
    """Perform DTD validation on the xml and return error output
    or an empty string if there is none"""

    c = event['c']
    p = c.p

    # first just try and create the XML
    try:
        xml_ = xml_for_subtree(p)
    except ValueError:
        g.es('ERROR generating XML')
        g.es(traceback.format_exc())
        return

    g.es('XML generated, attempting DTD validation')

    if xml_.startswith('<?xml '):
        # Unicode strings with encoding declaration are not supported
        # so cut off the xml declaration
        xml_ = xml_.split('\n', 1)[1]

    # set cwd so local .dtd files can be found
    cd_here(c, p)

    # make xml indented because for some unknown reason pretty_print=True
    # in xml_for_subtree doesn't work
    # etree.fromstring only returns the root node,
    # losing the DTD, so etree.parse instead
    from io import StringIO
    xml_ = StringIO(xml_)
    xml_ = etree.tostring(etree.parse(xml_), pretty_print=True)

    parser = etree.XMLParser(dtd_validation=True)
    try:
        etree.fromstring(xml_, parser=parser)
        g.es('No errors found')
    except etree.XMLSyntaxError as xse:
        g.es('ERROR validating XML')
        g.es(str(xse))

        # seems XMLSyntaxError doesn't set lineno?  Get from message
        lineno = int(str(xse).split()[-3].strip(',')) - 1
        xml_text = xml_.split('\n')
        for i in range(max(0, lineno - 6), min(len(xml_text), lineno + 3)):
            g.es("%d%s %s" % (i, ':' if i != lineno else '*', xml_text[i]))

#@-others
#@-leo

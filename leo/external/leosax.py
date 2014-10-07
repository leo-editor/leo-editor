#@+leo-ver=5-thin
#@+node:ekr.20120519121124.9919: * @file ../external/leosax.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20120519121124.9920: ** leosax declarations
"""Read .leo files into a simple python data structure with
h, b, u (unknown attribs), gnx and children information.
Clones and derived files are ignored.  Useful for scanning
multiple .leo files quickly.
"""

from __future__ import print_function

from xml.sax.handler import ContentHandler
from xml.sax import parse
from pickle import loads
from binascii import unhexlify

#@+node:ekr.20120519121124.9921: ** class LeoNode
class LeoNode:
    """Representation of a Leo node.  Root node has itself as parent.

    :IVariables:
        children
          python list of children
        u
          unknownAttributes dict (decoded)
        h
          headline
        b
          body text
        gnx
          node id
        parent
          node's parent
        path
          list of nodes that lead to this one from root, including this one
    """
    #@+others
    #@+node:ekr.20120519121124.9922: *3* __init__

    def __init__(self):
        """Set ivars"""
        self.children = []
        self.u = {}
        self.unknownAttributes = self.u  # for compatibility
        self.h = []
        self.b = []
        self.gnx = None
        self.parent = self
        self.path = []

    #@+node:ekr.20120519121124.9923: *3* __str__
    def __str__(self, level=0):
        """Return long text representation of node and
        descendents with indentation"""
        ans = [("%s%s (%s)" % ('  '*(level-1), self.h, self.gnx))[:78]]
        for k in self.u:
            s = self.u[k]
            ans.append(("%s@%s: %s"%('  '*(level+1), k, repr(s)))[:78])
        for line in self.b[:5]:
            ans.append(('  '*(level+1) + '|' + line)[:78])
        for c in self.children:
            ans.append(c.__str__(level=level+1))
        return '\n'.join(ans)

    #@+node:ekr.20120519121124.9924: *3* UNL
    def UNL(self):
        """Return the UNL string leading to this node"""
        return '-->'.join([i.h for i in self.path])

    #@+node:ekr.20120519121124.9925: *3* flat
    def flat(self):
        """iterate this node and all its descendants in a flat list, 
        useful for finding things and building an UNL based view"""
        if self.parent != self:
            yield(self)
        for i in self.children:
            for j in i.flat():
                yield j

    #@-others
#@+node:ekr.20120519121124.9926: ** class LeoReader
class LeoReader(ContentHandler):
    """Read .leo files into a simple python data structure with
    h, b, u (unknown attribs), gnx and children information.
    Clones and derived files are ignored.  Useful for scanning
    multiple .leo files quickly.

    :IVariables:
        root
          root node
        cur
          used internally during SAX read
        idx
          mapping from gnx to node
        `in_`
          name of XML element we're current in, used for SAX read
        in_attr
          attributes of element tag we're currentl in, used for SAX read
        path
          list of nodes leading to current node

    """
    #@+others
    #@+node:ekr.20120519121124.9927: *3* __init__


    def __init__(self, *args, **kwargs):
        """Set ivars"""
        ContentHandler.__init__(self, *args, **kwargs)
        self.root = LeoNode()

        self.root.h = 'ROOT'  
        # changes type from [] to str, done by endElement() for other vnodes

        self.cur = self.root
        self.idx = {}
        self.in_ = None
        self.in_attrs = {}
        self.path = []

    #@+node:ekr.20120519121124.9928: *3* startElement
    def startElement(self, name, attrs):
        """collect information from v and t elements"""
        self.in_ = name
        self.in_attrs = attrs

        if name == 'v':
            nd = LeoNode()
            self.cur.children.append(nd)
            nd.parent = self.cur
            self.cur = nd
            self.idx[attrs['t']] = nd
            nd.gnx = attrs['t']
            self.path.append(nd)
            nd.path = self.path[:]

        if name == 't':
            for k in attrs.keys():
                if k == 'tx':
                    continue
                self.idx[attrs['tx']].u[k] = attrs[k]

    #@+node:ekr.20120519121124.9929: *3* endElement
    def endElement(self, name):
        """decode unknownAttributes when t element is done"""

        self.in_ = None
        # could maintain a stack, but we only need to know for
        # character collection, so it doesn't matter

        if name == 'v':
            self.cur.h = ''.join(self.cur.h)
            self.cur = self.cur.parent
            if self.path:
                del self.path[-1]

        if name == 't':
            nd = self.idx[self.in_attrs['tx']]
            for k in nd.u:
                s = nd.u[k]
                if not k.startswith('str_'):
                    try:
                        s = loads(unhexlify(s))
                    except Exception:
                        pass

                nd.u[k] = s

    #@+node:ekr.20120519121124.9930: *3* characters
    def characters(self, content):
        """collect body text and headlines"""

        if self.in_ == 'vh':
            self.cur.h.append(content)

        if self.in_ == 't':
            self.idx[self.in_attrs['tx']].b.append(content)

    #@-others
#@+node:ekr.20120519121124.9931: ** get_leo_data
def get_leo_data(source):
    """Return the root node for the specificed .leo file (path or file)"""
    parser = LeoReader()
    parse(source, parser)
    return parser.root

#@-others
if __name__ == '__main__':
    import sys
    import os
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        wb = sys.argv[1]
    else:
        wb = os.path.expanduser(
            os.path.join('~', '.leo', 'workbook.leo')
        )
    leo_data = get_leo_data(wb)
    print(leo_data)
#@-leo

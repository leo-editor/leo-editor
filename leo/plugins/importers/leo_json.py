#@+leo-ver=5-thin
#@+node:ekr.20160504080826.1: * @file ../plugins/importers/leo_json.py
"""The @auto importer for .json files."""
#
# This module must **not** be named json, to avoid conflicts with the json standard library.
import json
from typing import  Dict
from leo.core import leoGlobals as g
from leo.core import leoNodes
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position, VNode

#@+others
#@+node:ekr.20160504080826.2: ** class JSON_Scanner
class JSON_Scanner:
    """A class to read .json files."""
    # Not a subclass of the Importer class.
    #@+others
    #@+node:ekr.20160504080826.3: *3* json.__init__
    def __init__(self, c: Cmdr) -> None:
        """The ctor for the JSON_Scanner class."""
        self.c = c
        # Keys are gnx's. Values are vnode_dicts.
        self.gnx_dict: Dict[str, Dict] = {}
        self.language = 'json'
        self.tab_width = c.tab_width
        # Keys are gnx's. Values are already-created vnodes.
        self.vnodes_dict: Dict[str, VNode] = {}
    #@+node:ekr.20160504093537.1: *3* json.create_nodes
    def create_nodes(self, parent: Position, parent_d: Dict) -> None:
        """Create the tree of nodes rooted in parent."""
        d = self.gnx_dict
        for child_gnx in parent_d.get('children'):
            d2 = d.get(child_gnx)
            if child_gnx in self.vnodes_dict:
                # It's a clone.
                v = self.vnodes_dict.get(child_gnx)
                n = parent.numberOfChildren()
                child = leoNodes.Position(v)
                child._linkAsNthChild(parent, n)
                # Don't create children again.
            else:
                child = parent.insertAsLastChild()
                child.h = d2.get('h') or '<**no h**>'
                child.b = d2.get('b') or ''
                if d2.get('gnx'):
                    child.v.findIndex = gnx = d2.get('gnx')
                    self.vnodes_dict[gnx] = child.v
                if d2.get('ua'):
                    child.u = d2.get('ua')
                self.create_nodes(child, d2)
    #@+node:ekr.20161015213011.1: *3* json.report
    def report(self, s: str) -> None:
        """Issue a message."""
        g.es_print(s)
    #@+node:ekr.20160504092347.1: *3* json.import_from_string
    def import_from_string(self, parent: Position, s: str) -> None:
        """JSON_Scanner.import_from_string."""
        self.scan(s, parent)
        # Importers should never dirty the outline.
        # #1451: Do not change the outline's change status.
        for p in parent.self_and_subtree():
            p.clearDirty()
    #@+node:ekr.20160504092347.3: *4* json.checkBlanksAndTabs
    def checkBlanksAndTabs(self, s: str) -> bool:
        """Check for intermixed blank & tabs."""
        # Do a quick check for mixed leading tabs/blanks.
        blanks = tabs = 0
        for line in g.splitLines(s):
            lws = line[0 : g.skip_ws(line, 0)]
            blanks += lws.count(' ')
            tabs += lws.count('\t')
        ok = blanks == 0 or tabs == 0
        if not ok:
            self.report('intermixed blanks and tabs')
        return ok
    #@+node:ekr.20160504092347.4: *4* json.regularizeWhitespace
    def regularizeWhitespace(self, s: str) -> str:
        """Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        This is only called for strict languages."""
        changed = False
        lines = g.splitLines(s)
        result = []
        tab_width = self.tab_width
        if tab_width < 0:  # Convert tabs to blanks.
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tab_width)
                s = g.computeLeadingWhitespace(w, -abs(tab_width)) + line[i:]  # Use negative width.
                if s != line:
                    changed = True
                result.append(s)
        elif tab_width > 0:  # Convert blanks to tabs.
            for line in lines:
                s = g.optimizeLeadingWhitespace(line, abs(tab_width))  # Use positive width.
                if s != line:
                    changed = True
                result.append(s)
        if changed:
            action = 'tabs converted to blanks' if self.tab_width < 0 else 'blanks converted to tabs'
            message = 'inconsistent leading whitespace. %s' % action
            self.report(message)
        return ''.join(result)
    #@+node:ekr.20160504082809.1: *3* json.scan
    def scan(self, s: str, parent: Position) -> bool:
        """Create an outline from a MindMap (.csv) file."""
        # pylint: disable=no-member
        # pylint confuses this module with the stdlib json module
        c = self.c
        self.gnx_dict = {}
        try:
            d = json.loads(s)
            for d2 in d.get('nodes', []):
                gnx = d2.get('gnx')
                self.gnx_dict[gnx] = d2
            top_d = d.get('top')
            if top_d:
                # Don't set parent.h or parent.gnx or parent.v.u.
                parent.b = top_d.get('b') or ''
                self.create_nodes(parent, top_d)
                c.redraw()
            return bool(top_d)
        except Exception:
            # Fix #1098
            try:
                obj = json.loads(s)
            except Exception:
                g.error('Bad .json file: %s' % parent.h)
                g.es_exception()
                obj = s
            parent.b = g.objToString(obj)
            c.redraw()
            return True
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for .JSON files."""
    JSON_Scanner(c).import_from_string(parent, s)

importer_dict = {
    '@auto': ['@auto-json',],
    'func': do_import,
    'extensions': ['.json',],
}
#@@language python
#@@tabwidth -4
#@-leo

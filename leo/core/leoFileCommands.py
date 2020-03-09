#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3018: * @file leoFileCommands.py
"""Classes relating to reading and writing .leo files."""
#@+<< imports >>
#@+node:ekr.20050405141130: ** << imports >> (leoFileCommands)
import xml.etree.ElementTree as ElementTree
try:
    # IronPython has problems with this.
    import xml.sax
    import xml.sax.saxutils
except Exception:
    pass
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes
import binascii
from collections import defaultdict
import difflib
import time
import io
StringIO = io.StringIO
BytesIO = io.BytesIO
import os
import pickle
import tempfile
import zipfile
import sqlite3
import hashlib
from contextlib import contextmanager
#@-<< imports >>
PRIVAREA = '---begin-private-area---'
#@+others
#@+node:ekr.20060918164811: ** class BadLeoFile
class BadLeoFile(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return "Bad Leo File:" + self.message
#@+node:ekr.20180602062323.1: ** class FastRead
class FastRead:

    nativeVnodeAttributes = (
        'a',
        'descendentTnodeUnknownAttributes',
        'descendentVnodeUnknownAttributes',
        'expanded', 'marks', 't', 'tnodeList',
    )

    def __init__(self, c, gnx2vnode):
        self.c = c
        self.gnx2vnode = gnx2vnode
    #@+others
    #@+node:ekr.20180604110143.1: *3* fast.readFile/FromClipboard & helper
    def readFile(self, path):
        """Read the file, change splitter ratiors, and return its hidden vnode."""
        with open(path, 'rb') as f:
            s = f.read()
        v, g_element = self.readWithElementTree(path, s)
        if not v:  # #1510.
            return None
        self.scanGlobals(g_element)
            # Fix #1047: only this method changes splitter sizes.
        #
        # Fix bug #1111: ensure that all outlines have at least one node.
        if not v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            v.children = [new_vnode]
        return v

    def readFileFromClipboard(self, s):
        """
        Recreate a file from a string s, and return its hidden vnode.
        
        Unlike readFile above, this does not affect splitter sizes.
        """
        v, g_element = self.readWithElementTree(path=None, s=s)
        if not v:  # #1510.
            return None
        #
        # Fix bug #1111: ensure that all outlines have at least one node.
        if not v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            v.children = [new_vnode]
        return v
    #@+node:ekr.20180602062323.7: *4* fast.readWithElementTree & helpers
    # #1510: https://en.wikipedia.org/wiki/Valid_characters_in_XML.
    translate_table = {z: None for z in range(20) if chr(z) not in '\t\r\n'}

    def readWithElementTree(self, path, s):

        contents = g.toUnicode(s)
        contents = contents.translate(self.translate_table)
            # Fix #1036 and #1046.
        try:
            xroot = ElementTree.fromstring(contents)
        except Exception as e:
            # #970: Just report failure here.
            if path:
                message = f"bad .leo file: {g.shortFileName(path)}"
            else:
                message = 'The clipboard is not a vaild .leo file'
            g.es_print('\n' + message, color='red')
            g.es_print(g.toUnicode(e))
            print('')
            # #1510: Return a tuple.
            return None, None
        g_element = xroot.find('globals')
        v_elements = xroot.find('vnodes')
        t_elements = xroot.find('tnodes')
        gnx2body, gnx2ua = self.scanTnodes(t_elements)
        hidden_v = self.scanVnodes(gnx2body, self.gnx2vnode, gnx2ua, v_elements)
        self.handleBits()
        return hidden_v, g_element
    #@+node:ekr.20180624125321.1: *5* fast.handleBits (reads c.db)
    def handleBits(self):
        """Restore the expanded and marked bits from c.db."""
        c, fc = self.c, self.c.fileCommands
        expanded = c.db.get('expanded')
        marked = c.db.get('marked')
        expanded = expanded.split(',') if expanded else []
        marked = marked.split(',') if marked else []
        fc.descendentExpandedList = expanded
        fc.descendentMarksList = marked
    #@+node:ekr.20180606041211.1: *5* fast.resolveUa & helper
    def resolveUa(self, attr, val, kind=None):  # Kind is for unit testing.
        """Parse an unknown attribute in a <v> or <t> element."""
        try:
            val = g.toEncodedString(val)
        except Exception:
            g.es_print('unexpected exception converting hexlified string to string')
            g.es_exception()
            return None
        # Leave string attributes starting with 'str_' alone.
        if attr.startswith('str_'):
            if isinstance(val, (str, bytes)):
                return g.toUnicode(val)
        try:
            binString = binascii.unhexlify(val)
                # Throws a TypeError if val is not a hex string.
        except Exception:
            # Assume that Leo 4.1 or above wrote the attribute.
            if g.unitTesting:
                assert kind == 'raw', f"unit test failed: kind={kind}"
            else:
                g.trace(f"can not unhexlify {attr}={val}")
            return val
        try:
            # No change needed to support protocols.
            val2 = pickle.loads(binString)
            return val2
        except Exception:
            try:
                val2 = pickle.loads(binString, encoding='bytes')
                val2 = self.bytesToUnicode(val2)
                return val2
            except Exception:
                g.trace(f"can not unpickle {attr}={val}")
                return val
    #@+node:ekr.20180606044154.1: *6* fast.bytesToUnicode
    def bytesToUnicode(self, ob):
        """
        Recursively convert bytes objects in strings / lists / dicts to str
        objects, thanks to TNT
        http://stackoverflow.com/questions/22840092
        Needed for reading Python 2.7 pickles in Python 3.4.
        """
        # This is simpler than using isinstance.
        # pylint: disable=unidiomatic-typecheck
        t = type(ob)
        if t in (list, tuple):
            l = [str(i, 'utf-8') if type(i) is bytes else i for i in ob]
            l = [self.bytesToUnicode(i)
                    if type(i) in (list, tuple, dict) else i
                        for i in l]
            ro = tuple(l) if t is tuple else l
        elif t is dict:
            byte_keys = [i for i in ob if type(i) is bytes]
            for bk in byte_keys:
                v = ob[bk]
                del(ob[bk])
                ob[str(bk, 'utf-8')] = v
            for k in ob:
                if type(ob[k]) is bytes:
                    ob[k] = str(ob[k], 'utf-8')
                elif type(ob[k]) in (list, tuple, dict):
                    ob[k] = self.bytesToUnicode(ob[k])
            ro = ob
        elif t is bytes:  # TNB added this clause
            ro = str(ob, 'utf-8')
        else:
            ro = ob
        return ro
    #@+node:ekr.20180605062300.1: *5* fast.scanGlobals & helper
    def scanGlobals(self, g_element):
        """Get global data from the cache, with reasonable defaults."""
        c = self.c
        d = self.getGlobalData()
        windowSize = g.app.loadManager.options.get('windowSize')
        windowSpot = g.app.loadManager.options.get('windowSpot')
        if windowSize is not None:
            h, w = windowSize  # checked in LM.scanOption.
        else:
            w, h = d.get('width'), d.get('height')
        if windowSpot is None:
            x, y = d.get('left'), d.get('top')
        else:
            y, x = windowSpot  # #1263: (top, left)
        if 'size' in g.app.debug:
            g.trace(w, h, x, y, c.shortFileName())
        #
        # #1189: Must be done *after* restoring geometry.
        #        Was done in TabbedFrameFactory.createMaster.
        if g.app.use_global_docks:
            mf = getattr(g.app.gui, 'main_window', None)
            if not mf:
                return
            g.app.gui.set_top_geometry(w, h, x, y)
            r1, r2 = d.get('r1'), d.get('r2')
            c.frame.resizePanesToRatio(r1, r2)
        else:
            # c.frame may be a NullFrame.
            c.frame.setTopGeometry(w, h, x, y)
            r1, r2 = d.get('r1'), d.get('r2')
            c.frame.resizePanesToRatio(r1, r2)
            frameFactory = getattr(g.app.gui, 'frameFactory', None)
            if not frameFactory:
                return
            assert frameFactory is not None
            mf = frameFactory.masterFrame
        if g.app.start_minimized:
            mf.showMinimized()
        elif g.app.start_maximized:
            # #1189: fast.scanGlobals calls showMaximized later.
            mf.showMaximized()
        elif g.app.start_fullscreen:
            mf.showFullScreen()
        else:
            mf.show()
    #@+node:ekr.20180708060437.1: *6* fast.getGlobalData
    def getGlobalData(self):
        """Return a dict containing all global data."""
        c = self.c
        try:
            window_pos = c.db.get('window_position')
            r1 = float(c.db.get('body_outline_ratio', '0.5'))
            r2 = float(c.db.get('body_secondary_ratio', '0.5'))
            top, left, height, width = window_pos
            return {
                'top': int(top),
                'left': int(left),
                'height': int(height),
                'width': int(width),
                'r1': r1,
                'r2': r2,
            }
        except Exception:
            pass
        # Use reasonable defaults.
        return {
            'top': 50, 'left': 50,
            'height': 500, 'width': 800,
            'r1': 0.5, 'r2': 0.5,
        }
    #@+node:ekr.20180602062323.8: *5* fast.scanTnodes
    def scanTnodes(self, t_elements):

        gnx2body, gnx2ua = {}, defaultdict(dict)
        for e in t_elements:
            # First, find the gnx.
            gnx = e.attrib['tx']
            gnx2body[gnx] = e.text or ''
            # Next, scan for uA's for this gnx.
            for key, val in e.attrib.items():
                if key != 'tx':
                    gnx2ua[gnx][key] = self.resolveUa(key, val)
        return gnx2body, gnx2ua
    #@+node:ekr.20180602062323.9: *5* fast.scanVnodes & helper
    def scanVnodes(self, gnx2body, gnx2vnode, gnx2ua, v_elements):

        c, fc = self.c, self.c.fileCommands
        #@+<< define v_element_visitor >>
        #@+node:ekr.20180605102822.1: *6* << define v_element_visitor >>
        def v_element_visitor(parent_e, parent_v):
            """Visit the given element, creating or updating the parent vnode."""
            for e in parent_e:
                assert e.tag in ('v', 'vh'), e.tag
                if e.tag == 'vh':
                    parent_v._headString = g.toUnicode(e.text or '')
                    continue
                gnx = e.attrib['t']
                v = gnx2vnode.get(gnx)
                if v:
                    # A clone
                    parent_v.children.append(v)
                    v.parents.append(parent_v)
                    # The body overrides any previous body text.
                    body = g.toUnicode(gnx2body.get(gnx) or '')
                    assert g.isUnicode(body), body.__class__.__name__
                    v._bodyString = body
                else:
                    #@+<< Make a new vnode, linked to the parent >>
                    #@+node:ekr.20180605075042.1: *7* << Make a new vnode, linked to the parent >>
                    v = leoNodes.VNode(context=c, gnx=gnx)
                    gnx2vnode[gnx] = v
                    parent_v.children.append(v)
                    v.parents.append(parent_v)
                    body = g.toUnicode(gnx2body.get(gnx) or '')
                    assert g.isUnicode(body), body.__class__.__name__
                    v._bodyString = body
                    v._headString = 'PLACE HOLDER'
                    #@-<< Make a new vnode, linked to the parent >>
                    #@+<< handle all other v attributes >>
                    #@+node:ekr.20180605075113.1: *7* << handle all other v attributes >>
                    # Like fc.handleVnodeSaxAttrutes.
                    #
                    # The native attributes of <v> elements are a, t, vtag, tnodeList,
                    # marks, expanded, and descendentTnode/VnodeUnknownAttributes.
                    d = e.attrib
                    s = d.get('tnodeList', '')
                    tnodeList = s and s.split(',')
                    if tnodeList:
                        # This tnodeList will be resolved later.
                        v.tempTnodeList = tnodeList
                    s = d.get('descendentTnodeUnknownAttributes')
                    if s:
                        aDict = fc.getDescendentUnknownAttributes(s, v=v)
                        if aDict:
                            fc.descendentTnodeUaDictList.append(aDict)
                    s = d.get('descendentVnodeUnknownAttributes')
                    if s:
                        aDict = fc.getDescendentUnknownAttributes(s, v=v)
                        if aDict:
                            fc.descendentVnodeUaDictList.append((v, aDict),)
                    #
                    # Handle vnode uA's
                    uaDict = gnx2ua[gnx]
                        # gnx2ua is a defaultdict(dict)
                        # It might already exists because of tnode uA's.
                    for key, val in d.items():
                        if key not in self.nativeVnodeAttributes:
                            uaDict[key] = self.resolveUa(key, val)
                    if uaDict:
                        v.unknownAttributes = uaDict
                    #@-<< handle all other v attributes >>
                    # Handle all inner elements.
                    v_element_visitor(e, v)

        #@-<< define v_element_visitor >>
        #
        # Create the hidden root vnode.

        gnx = 'hidden-root-vnode-gnx'
        hidden_v = leoNodes.VNode(context=c, gnx=gnx)
        hidden_v._headString = '<hidden root vnode>'
        gnx2vnode[gnx] = hidden_v
        #
        # Traverse the tree of v elements.
        v_element_visitor(v_elements, hidden_v)
        return hidden_v
    #@-others
#@+node:ekr.20160514120347.1: ** class FileCommands
class FileCommands:
    """A class creating the FileCommands subcommander."""
    #@+others
    #@+node:ekr.20090218115025.4: *3* fc.Birth
    #@+node:ekr.20150509194827.1: *4* fc.cmd (decorator)
    def cmd(name):
        """Command decorator for the FileCommands class."""
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'fileCommands',])
    #@+node:ekr.20031218072017.3019: *4* fc.ctor
    def __init__(self, c):
        """Ctor for FileCommands class."""
        self.c = c
        self.frame = c.frame
        self.nativeTnodeAttributes = ('tx',)
        self.nativeVnodeAttributes = (
            'a',
            'descendentTnodeUnknownAttributes',
            'descendentVnodeUnknownAttributes',  # New in Leo 4.5.
            'expanded', 'marks', 't', 'tnodeList',
            # 'vtag',
        )
        self.initIvars()
    #@+node:ekr.20090218115025.5: *4* fc.initIvars
    def initIvars(self):
        """Init ivars of the FileCommands class."""
        # General...
        c = self.c
        self.mFileName = ""
        self.fileDate = -1
        self.leo_file_encoding = c.config.new_leo_file_encoding
        # For reading...
        self.checking = False  # True: checking only: do *not* alter the outline.
        self.descendentExpandedList = []
        self.descendentMarksList = []
        self.forbiddenTnodes = []
        self.descendentTnodeUaDictList = []
        self.descendentVnodeUaDictList = []
        self.ratio = 0.5
        self.currentVnode = None
        # For writing...
        self.read_only = False
        self.rootPosition = None
        self.outputFile = None
        self.openDirectory = None
        self.putCount = 0
        self.toString = False
        self.usingClipboard = False
        self.currentPosition = None
        # New in 3.12...
        self.copiedTree = None
        self.gnxDict = {}
            # keys are gnx strings as returned by canonicalTnodeIndex.
            # Values are vnodes.
            # 2011/12/10: This dict is never re-inited.
        self.vnodesDict = {}
            # keys are gnx strings; values are ignored
    #@+node:ekr.20031218072017.3020: *3* fc.Reading
    #@+node:ekr.20060919104836: *4*  fc.Reading Top-level
    #@+node:ekr.20031218072017.1559: *5* fc.Paste
    #@+node:ekr.20180709205603.1: *6* fc.getLeoOutlineFromClipBoard
    def getLeoOutlineFromClipboard(self, s):
        """Read a Leo outline from string s in clipboard format."""
        c = self.c
        current = c.p
        if not current:
            g.trace('no c.p')
            return None
        self.initReadIvars()
        # Save the hidden root's children.
        old_children = c.hiddenRootNode.children
        # Save and clear gnxDict.
        oldGnxDict = self.gnxDict
        self.gnxDict = {}
        s = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            # This encoding must match the encoding used in putLeoOutline.
        hidden_v = FastRead(c, self.gnxDict).readFileFromClipboard(s)
        v = hidden_v.children[0]
        v.parents = []
        # Restore the hidden root's children
        c.hiddenRootNode.children = old_children
        if not v:
            return g.es("the clipboard is not valid ", color="blue")
        # Create the position.
        p = leoNodes.Position(v)
        # Do *not* adjust links when linking v.
        if current.hasChildren() and current.isExpanded():
            p._linkCopiedAsNthChild(current, 0)
        else:
            p._linkCopiedAfter(current)
        assert not p.isCloned(), g.objToString(p.v.parents)
        self.gnxDict = oldGnxDict
        self.reassignAllIndices(p)
        c.selectPosition(p)
        self.initReadIvars()
        return p

    getLeoOutline = getLeoOutlineFromClipboard  # for compatibility
    #@+node:ekr.20180709205640.1: *6* fc.getLeoOutlineFromClipBoardRetainingClones
    def getLeoOutlineFromClipboardRetainingClones(self, s):
        """Read a Leo outline from string s in clipboard format."""
        c = self.c
        current = c.p
        if not current:
            return g.trace('no c.p')
        self.initReadIvars()
        # Save the hidden root's children.
        old_children = c.hiddenRootNode.children
        # All pasted nodes should already have unique gnx's.
        ni = g.app.nodeIndices
        for v in c.all_unique_nodes():
            ni.check_gnx(c, v.fileIndex, v)
        s = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            # This encoding must match the encoding used in putLeoOutline.
        hidden_v = FastRead(c, self.gnxDict).readFileFromClipboard(s)
        v = hidden_v.children[0]
        v.parents.remove(hidden_v)
        # Restore the hidden root's children
        c.hiddenRootNode.children = old_children
        if not v:
            return g.es("the clipboard is not valid ", color="blue")
        # Create the position.
        p = leoNodes.Position(v)
        # Do *not* adjust links when linking v.
        if current.hasChildren() and current.isExpanded():
            if not self.checkPaste(current, p):
                return None
            p._linkCopiedAsNthChild(current, 0)
        else:
            if not self.checkPaste(current.parent(), p):
                return None
            p._linkCopiedAfter(current)
        # Fix #862: paste-retaining-clones can corrupt the outline.
        self.linkChildrenToParents(p)
        c.selectPosition(p)
        self.initReadIvars()
        return p
    #@+node:ekr.20080410115129.1: *6* fc.checkPaste
    def checkPaste(self, parent, p):
        """Return True if p may be pasted as a child of parent."""
        if not parent:
            return True
        parents = list(parent.self_and_parents())
        for p in p.self_and_subtree(copy=False):
            for z in parents:
                if p.v == z.v:
                    g.warning('Invalid paste: nodes may not descend from themselves')
                    return False
        return True
    #@+node:ekr.20180424123010.1: *6* fc.linkChildrenToParents
    def linkChildrenToParents(self, p):
        """
        Populate the parent links in all children of p.
        """
        for child in p.children():
            if not child.v.parents:
                child.v.parents.append(p.v)
            self.linkChildrenToParents(child)
    #@+node:ekr.20180425034856.1: *6* fc.reassignAllIndices
    def reassignAllIndices(self, p):
        """Reassign all indices in p's subtree."""
        ni = g.app.nodeIndices
        for p2 in p.self_and_subtree(copy=False):
            v = p2.v
            index = ni.getNewIndex(v)
            if 'gnx' in g.app.debug:
                g.trace('**reassigning**', index, v)
    #@+node:ekr.20031218072017.1553: *5* fc.getLeoFile & helpers (read main line)
    def getLeoFile(self,
        theFile,
        fileName,
        readAtFileNodesFlag=True,
        silent=False,
        checkOpenFiles=True,
    ):
        """
            Read a .leo file.
            The caller should follow this with a call to c.redraw().
        """
        fc, c = self, self.c
        t1 = time.time()
        c.clearChanged()  # May be set when reading @file nodes.
        fc.warnOnReadOnlyFiles(fileName)
        fc.checking = False
        fc.mFileName = c.mFileName
        fc.initReadIvars()
        recoveryNode = None
        try:
            c.loading = True  # disable c.changed
            if not silent and checkOpenFiles:
                # Don't check for open file when reverting.
                g.app.checkForOpenFile(c, fileName)
            #
            # Read the .leo file and create the outline.
            if fileName.endswith('.db'):
                v = fc.retrieveVnodesFromDb(theFile) or fc.initNewDb(theFile)
            else:
                v = FastRead(c, self.gnxDict).readFile(fileName)
                if v:
                    c.hiddenRootNode = v
            if v:
                fc.resolveTnodeLists()
                    # Do this before reading external files.
                c.setFileTimeStamp(fileName)
                if readAtFileNodesFlag:
                    # c.redraw()
                        # Does not work.
                        # Redraw before reading the @file nodes so the screen isn't blank.
                        # This is important for big files like LeoPy.leo.
                    recoveryNode = fc.readExternalFiles(fileName)
        finally:
            p = recoveryNode or c.p or c.lastTopLevel()
                # lastTopLevel is a better fallback, imo.
            c.selectPosition(p)
            c.redraw_later()
                # Delay the second redraw until idle time.
                # This causes a slight flash, but corrects a hangnail.
            c.checkOutline()
                # Must be called *after* ni.end_holding.
            c.loading = False
                # reenable c.changed
            if not isinstance(theFile, sqlite3.Connection):
                theFile.close()
                # Fix bug https://bugs.launchpad.net/leo-editor/+bug/1208942
                # Leo holding directory/file handles after file close?
        if c.changed:
            fc.propegateDirtyNodes()
        fc.initReadIvars()
        t2 = time.time()
        g.es(f"read outline in {t2 - t1:2.2f} seconds")
        return v, c.frame.ratio
    #@+node:ekr.20100205060712.8314: *6* fc.handleNodeConflicts
    def handleNodeConflicts(self):
        """Create a 'Recovered Nodes' node for each entry in c.nodeConflictList."""
        c = self.c
        if not c.nodeConflictList:
            return None
        if not c.make_node_conflicts_node:
            s = f"suppressed {len(c.nodeConflictList)} node conflicts"
            g.es(s, color='red')
            g.pr('\n' + s + '\n')
            return None
        # Create the 'Recovered Nodes' node.
        last = c.lastTopLevel()
        root = last.insertAfter()
        root.setHeadString('Recovered Nodes')
        root.expand()
        # For each conflict, create one child and two grandchildren.
        for bunch in c.nodeConflictList:
            tag = bunch.get('tag') or ''
            gnx = bunch.get('gnx') or ''
            fn = bunch.get('fileName') or ''
            b1, h1 = bunch.get('b_old'), bunch.get('h_old')
            b2, h2 = bunch.get('b_new'), bunch.get('h_new')
            root_v = bunch.get('root_v') or ''
            child = root.insertAsLastChild()
            h = f'Recovered node "{h1}" from {g.shortFileName(fn)}'
            child.setHeadString(h)
            if b1 == b2:
                lines = [
                    'Headline changed...',
                    f"{tag} gnx: {gnx} root: {(root_v and root.v)!r}",
                    f"old headline: {h1}",
                    f"new headline: {h2}",
                ]
                child.setBodyString('\n'.join(lines))
            else:
                line1 = f"{tag} gnx: {gnx} root: {root_v and root.v!r}\nDiff...\n"
                d = difflib.Differ().compare(g.splitLines(b1), g.splitLines(b2))
                    # 2017/06/19: reverse comparison order.
                diffLines = [z for z in d]
                lines = [line1]
                lines.extend(diffLines)
                # There is less need to show trailing newlines because
                # we don't report changes involving only trailing newlines.
                child.setBodyString(''.join(lines))
                n1 = child.insertAsNthChild(0)
                n2 = child.insertAsNthChild(1)
                n1.setHeadString('old:' + h1)
                n1.setBodyString(b1)
                n2.setHeadString('new:' + h2)
                n2.setBodyString(b2)
        return root
    #@+node:ekr.20100124110832.6212: *6* fc.propegateDirtyNodes
    def propegateDirtyNodes(self):
        fc = self; c = fc.c
        aList = [z for z in c.all_positions() if z.isDirty()]
        for p in aList:
            p.setAllAncestorAtFileNodesDirty()
    #@+node:ekr.20120212220616.10537: *6* fc.readExternalFiles
    def readExternalFiles(self, fileName):
        """Read all external files."""
        c, fc = self.c, self
        c.atFileCommands.readAll(c.rootPosition(), force=False)
        recoveryNode = fc.handleNodeConflicts()
        # Do this after reading external files.
        # The descendent nodes won't exist unless we have read
        # the @thin nodes!
        fc.restoreDescendentAttributes()
        fc.setPositionsFromVnodes()
        return recoveryNode
    #@+node:ekr.20031218072017.1554: *6* fc.warnOnReadOnlyFiles
    def warnOnReadOnlyFiles(self, fileName):
        # os.access may not exist on all platforms.
        try:
            self.read_only = not os.access(fileName, os.W_OK)
        except AttributeError:
            self.read_only = False
        except UnicodeError:
            self.read_only = False
        if self.read_only and not g.unitTesting:
            g.error("read only:", fileName)
    #@+node:ekr.20031218072017.3029: *5* fc.readAtFileNodes
    def readAtFileNodes(self):
        c = self.c; p = c.p
        c.endEditing()
        c.atFileCommands.readAll(p, force=True)
        c.redraw()
        # Force an update of the body pane.
        c.setBodyString(p, p.b)
        c.frame.body.onBodyChanged(undoType=None)
    #@+node:ekr.20031218072017.2297: *5* fc.openLeoFile
    def openLeoFile(self, theFile, fileName, readAtFileNodesFlag=True, silent=False):
        """Open a Leo file."""
        c, frame = self.c, self.c.frame
        # Set c.openDirectory
        theDir = g.os_path_dirname(fileName)
        if theDir:
            c.openDirectory = c.frame.openDirectory = theDir
        # Fix #1437 when opening completely new outline
        # there is no sense in keeping the old values in gnxDict
        self.gnxDict = {}
        # Get the file.
        ok, ratio = self.getLeoFile(
            theFile, fileName,
            readAtFileNodesFlag=readAtFileNodesFlag,
            silent=silent,
        )
        if ok:
            frame.resizePanesToRatio(ratio, frame.secondary_ratio)
        return ok
    #@+node:ekr.20031218072017.3030: *5* fc.readOutlineOnly
    def readOutlineOnly(self, theFile, fileName):
        c = self.c
        #@+<< Set the default directory >>
        #@+node:ekr.20071211134300: *6* << Set the default directory >> (fc.readOutlineOnly)
        #@@language rest
        #@+at
        # The most natural default directory is the directory containing the .leo file
        # that we are about to open. If the user has specified the "Default Directory"
        # preference that will over-ride what we are about to set.
        #@@c
        #@@language python

        theDir = g.os_path_dirname(fileName)
        if theDir:
            c.openDirectory = c.frame.openDirectory = theDir
        #@-<< Set the default directory >>
        ok, ratio = self.getLeoFile(theFile, fileName, readAtFileNodesFlag=False)
        c.redraw()
        c.frame.deiconify()
        junk, junk, secondary_ratio = self.frame.initialRatios()
        c.frame.resizePanesToRatio(ratio, secondary_ratio)
        return ok
    #@+node:vitalije.20170831144643.1: *5* fc.updateFromRefFile
    def updateFromRefFile(self):
        """Updates public part of outline from the specified file."""
        fc = self; c = self.c
        #@+others
        #@+node:vitalije.20170831144827.2: *6* get_ref_filename
        def get_ref_filename():
            for v in priv_vnodes():
                return g.splitLines(v.b)[0].strip()
        #@+node:vitalije.20170831144827.4: *6* pub_vnodes
        def pub_vnodes():
            for v in c.hiddenRootNode.children:
                if v.h == PRIVAREA:
                    break
                yield v
        #@+node:vitalije.20170831144827.5: *6* priv_vnodes
        def priv_vnodes():
            pub = True
            for v in c.hiddenRootNode.children:
                if v.h == PRIVAREA:
                    pub = False
                if pub: continue
                yield v
        #@+node:vitalije.20170831144827.6: *6* pub_gnxes
        def sub_gnxes(children):
            for v in children:
                yield v.gnx
                for gnx in sub_gnxes(v.children):
                    yield gnx

        def pub_gnxes():
            return sub_gnxes(pub_vnodes())

        def priv_gnxes():
            return sub_gnxes(priv_vnodes())
        #@+node:vitalije.20170831144827.7: *6* restore_priv
        def restore_priv(prdata, topgnxes):
            vnodes = []
            for row in prdata:
                (gnx, h, b, children, parents, iconVal, statusBits, ua) = row
                v = leoNodes.VNode(context=c, gnx=gnx)
                v._headString = h
                v._bodyString = b
                v.children = children
                v.parents = parents
                v.iconVal = iconVal
                v.statusBits = statusBits
                v.u = ua
                vnodes.append(v)
            pv = lambda x: fc.gnxDict.get(x, c.hiddenRootNode)
            for v in vnodes:
                v.children = [pv(x) for x in v.children]
                v.parents = [pv(x) for x in v.parents]
            for gnx in topgnxes:
                v = fc.gnxDict[gnx]
                c.hiddenRootNode.children.append(v)
        #@+node:vitalije.20170831144827.8: *6* priv_data
        def priv_data(gnxes):
            dbrow = lambda v: (
                        v.gnx,
                        v.h,
                        v.b,
                        [x.gnx for x in v.children],
                        [x.gnx for x in v.parents],
                        v.iconVal,
                        v.statusBits,
                        v.u
                    )
            return tuple(dbrow(fc.gnxDict[x]) for x in gnxes)
        #@+node:vitalije.20170831144827.9: *6* nosqlite_commander
        @contextmanager
        def nosqlite_commander(fname):
            oldname = c.mFileName
            conn = getattr(c, 'sqlite_connection', None)
            c.sqlite_connection = None
            c.mFileName = fname
            yield c
            if c.sqlite_connection:
                c.sqlite_connection.close()
            c.mFileName = oldname
            c.sqlite_connection = conn
        #@-others
        pubgnxes = set(pub_gnxes())
        privgnxes = set(priv_gnxes())
        privnodes = priv_data(privgnxes - pubgnxes)
        toppriv = [v.gnx for v in priv_vnodes()]
        fname = get_ref_filename()
        with nosqlite_commander(fname):
            theFile = open(fname, 'rb')
            fc.initIvars()
            fc.getLeoFile(theFile, fname, checkOpenFiles=False)
        restore_priv(privnodes, toppriv)
        c.redraw()
    #@+node:vitalije.20170831154734.1: *5* fc.setReferenceFile
    def setReferenceFile(self, fileName):
        c = self.c
        for v in c.hiddenRootNode.children:
            if v.h == PRIVAREA:
                v.b = fileName
                break
        else:
            v = c.rootPosition().insertBefore().v
            v.h = PRIVAREA
            v.b = fileName
            c.redraw()
        g.es('set reference file:', g.shortFileName(fileName))
    #@+node:ekr.20060919133249: *4* fc.Reading Common
    # Methods common to both the sax and non-sax code.
    #@+node:ekr.20031218072017.2004: *5* fc.canonicalTnodeIndex
    def canonicalTnodeIndex(self, index):
        """Convert Tnnn to nnn, leaving gnx's unchanged."""
        # index might be Tnnn, nnn, or gnx.
        if index is None:
            g.trace('Can not happen: index is None')
            return None
        junk, theTime, junk = g.app.nodeIndices.scanGnx(index, 0)
        if theTime is None:  # A pre-4.1 file index.
            if index[0] == "T":
                index = index[1:]
        return index
    #@+node:ekr.20040701065235.1: *5* fc.getDescendentAttributes
    def getDescendentAttributes(self, s, tag=""):
        """s is a list of gnx's, separated by commas from a <v> or <t> element.
        Parses s into a list.

        This is used to record marked and expanded nodes.
        """
        gnxs = s.split(',')
        result = [gnx for gnx in gnxs if len(gnx) > 0]
        return result
    #@+node:EKR.20040627114602: *5* fc.getDescendentUnknownAttributes
    # Pre Leo 4.5 Only @thin vnodes had the descendentTnodeUnknownAttributes field.
    # New in Leo 4.5: @thin & @shadow vnodes have descendentVnodeUnknownAttributes field.

    def getDescendentUnknownAttributes(self, s, v=None):
        """Unhexlify and unpickle t/v.descendentUnknownAttribute field."""
        try:
            # Changed in version 3.2: Accept only bytestring or bytearray objects as input.
            s = g.toEncodedString(s)  # 2011/02/22
            bin = binascii.unhexlify(s)
                # Throws a TypeError if val is not a hex string.
            val = pickle.loads(bin)
            return val
        except Exception:
            g.es_exception()
            g.trace('Can not unpickle', type(s), v and v.h, s[:40])
            return None
    #@+node:vitalije.20180304190953.1: *5* fc.getPos/VnodeFromClipboard
    def getPosFromClipboard(self, s):
        """A utility called from init_tree_abbrev."""
        v = self.getVnodeFromClipboard(s)
        return leoNodes.Position(v)

    def getVnodeFromClipboard(self, s):
        """Called only from getPosFromClipboard."""
        c = self.c
        self.initReadIvars()
        oldGnxDict = self.gnxDict
        self.gnxDict = {}  # Fix #943
        try:
            # This encoding must match the encoding used in putLeoOutline.
            s = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            v = FastRead(c, {}).readFileFromClipboard(s)
            if not v:
                return g.es("the clipboard is not valid ", color="blue")
        finally:
            self.gnxDict = oldGnxDict
        return v
    #@+node:ekr.20060919142200.1: *5* fc.initReadIvars
    def initReadIvars(self):
        self.descendentTnodeUaDictList = []
        self.descendentVnodeUaDictList = []
        self.descendentExpandedList = []
        self.descendentMarksList = []
            # 2011/12/10: never re-init this dict.
            # self.gnxDict = {}
        self.c.nodeConflictList = []  # 2010/01/05
        self.c.nodeConflictFileName = None  # 2010/01/05
    #@+node:EKR.20040627120120: *5* fc.restoreDescendentAttributes
    def restoreDescendentAttributes(self):
        """Called from fc.readExternalFiles."""
        c = self.c
        for resultDict in self.descendentTnodeUaDictList:
            for gnx in resultDict:
                tref = self.canonicalTnodeIndex(gnx)
                v = self.gnxDict.get(tref)
                if v:
                    v.unknownAttributes = resultDict[gnx]
                    v._p_changed = 1
        # New in Leo 4.5: keys are archivedPositions, values are attributes.
        for root_v, resultDict in self.descendentVnodeUaDictList:
            for key in resultDict:
                v = self.resolveArchivedPosition(key, root_v)
                if v:
                    v.unknownAttributes = resultDict[key]
                    v._p_changed = 1
        marks = {}; expanded = {}
        for gnx in self.descendentExpandedList:
            tref = self.canonicalTnodeIndex(gnx)
            v = self.gnxDict.get(gnx)
            if v:
                expanded[v] = v
        for gnx in self.descendentMarksList:
            tref = self.canonicalTnodeIndex(gnx)
            v = self.gnxDict.get(gnx)
            if v: marks[v] = v
        if marks or expanded:
            for p in c.all_unique_positions():
                if marks.get(p.v):
                    p.v.initMarkedBit()
                        # This was the problem: was p.setMark.
                        # There was a big performance bug in the mark hook in the Node Navigator plugin.
                if expanded.get(p.v):
                    p.expand()
    #@+node:vitalije.20170630152841.1: *5* fc.retrieveVnodesFromDb
    def retrieveVnodesFromDb(self, conn):
        """
        Recreates tree from the data contained in table vnodes.
        
        This method follows behavior of readSaxFile.
        """

        c, fc = self.c, self
        sql = '''select gnx, head, 
             body,
             children,
             parents,
             iconVal,
             statusBits,
             ua from vnodes'''
        vnodes = []
        try:
            for row in conn.execute(sql):
                (gnx, h, b, children, parents, iconVal, statusBits, ua) = row
                try:
                    ua = pickle.loads(g.toEncodedString(ua))
                except ValueError:
                    ua = None
                v = leoNodes.VNode(context=c, gnx=gnx)
                v._headString = h
                v._bodyString = b
                v.children = children.split()
                v.parents = parents.split()
                v.iconVal = iconVal
                v.statusBits = statusBits
                v.u = ua
                vnodes.append(v)
        except sqlite3.Error as er:
            if er.args[0].find('no such table') < 0:
                # there was an error raised but it is not the one we expect
                g.internalError(er)
            # there is no vnodes table
            return None

        rootChildren = [x for x in vnodes if 'hidden-root-vnode-gnx' in x.parents]
        if not rootChildren:
            g.trace('there should be at least one top level node!')
            return None

        findNode = lambda x: fc.gnxDict.get(x, c.hiddenRootNode)

        # let us replace every gnx with the corresponding vnode
        for v in vnodes:
            v.children = [findNode(x) for x in v.children]
            v.parents = [findNode(x) for x in v.parents]
        c.hiddenRootNode.children = rootChildren
        (w, h, x, y, r1, r2, encp) = fc.getWindowGeometryFromDb(conn)
        c.frame.setTopGeometry(w, h, x, y)
        c.frame.resizePanesToRatio(r1, r2)
        p = fc.decodePosition(encp)
        c.setCurrentPosition(p)
        return rootChildren[0]
    #@+node:vitalije.20170815162307.1: *6* fc.initNewDb
    def initNewDb(self, conn):
        """ Initializes tables and returns None"""
        fc = self; c = self.c
        v = leoNodes.VNode(context=c)
        c.hiddenRootNode.children = [v]
        (w, h, x, y, r1, r2, encp) = fc.getWindowGeometryFromDb(conn)
        c.frame.setTopGeometry(w, h, x, y)
        c.frame.resizePanesToRatio(r1, r2)
        c.sqlite_connection = conn
        fc.exportToSqlite(c.mFileName)
        return v
    #@+node:vitalije.20170630200802.1: *6* fc.getWindowGeometryFromDb
    def getWindowGeometryFromDb(self, conn):
        geom = (600, 400, 50, 50, 0.5, 0.5, '')
        keys = ('width', 'height', 'left', 'top',
                  'ratio', 'secondary_ratio',
                  'current_position')
        try:
            d = dict(
                conn.execute(
                '''select * from extra_infos 
                where name in (?, ?, ?, ?, ?, ?, ?)''',
                keys,
            ).fetchall(),
            )
            geom = (d.get(*x) for x in zip(keys, geom))
        except sqlite3.OperationalError:
            pass
        return geom
    #@+node:ekr.20031218072017.3032: *3* fc.Writing
    #@+node:ekr.20070413045221.2: *4*  fc.Top-level
    #@+node:ekr.20070413061552: *5* fc.putSavedMessage
    def putSavedMessage(self, fileName):
        c = self.c
        # #531: Optionally report timestamp...
        if c.config.getBool('log-show-save-time', default=False):
            format = c.config.getString('log-timestamp-format') or "%H:%M:%S"
            timestamp = time.strftime(format) + ' '
        else:
            timestamp = ''
        zipMark = '[zipped] ' if c.isZipped else ''
        g.es(f"{timestamp} saved: {zipMark}{g.shortFileName(fileName)}")
    #@+node:ekr.20031218072017.1720: *5* fc.save
    def save(self, fileName, silent=False):
        c = self.c
        p = c.p
        # New in 4.2.  Return ok flag so shutdown logic knows if all went well.
        ok = g.doHook("save1", c=c, p=p, fileName=fileName)
        if ok is None:
            c.endEditing()  # Set the current headline text.
            self.setDefaultDirectoryForNewFiles(fileName)
            g.app.commander_cacher.save(c, fileName, changeName=True)
            ok = c.checkFileTimeStamp(fileName)
            if ok:
                if c.sqlite_connection:
                    c.sqlite_connection.close()
                    c.sqlite_connection = None
                ok = self.write_Leo_file(fileName, False)  # outlineOnlyFlag
            if ok:
                if not silent:
                    self.putSavedMessage(fileName)
                c.clearChanged()  # Clears all dirty bits.
                if c.config.save_clears_undo_buffer:
                    g.es("clearing undo")
                    c.undoer.clearUndoState()
            c.redraw_after_icons_changed()
        g.doHook("save2", c=c, p=p, fileName=fileName)
        return ok
    #@+node:vitalije.20170831135146.1: *5* fc.save_ref
    def save_ref(self):
        """Saves reference outline file"""
        c = self.c
        p = c.p
        fc = self
        #@+others
        #@+node:vitalije.20170831135535.1: *6* putVnodes2
        def putVnodes2():
            """Puts all <v> elements in the order in which they appear in the outline."""
            c.clearAllVisited()
            fc.put("<vnodes>\n")
            # Make only one copy for all calls.
            fc.currentPosition = c.p
            fc.rootPosition = c.rootPosition()
            fc.vnodesDict = {}
            ref_fname = None
            for p in c.rootPosition().self_and_siblings(copy=False):
                if p.h == PRIVAREA:
                    ref_fname = p.b.split('\n', 1)[0].strip()
                    break
                # An optimization: Write the next top-level node.
                fc.putVnode(p, isIgnore=p.isAtIgnoreNode())
            fc.put("</vnodes>\n")
            return ref_fname
        #@+node:vitalije.20170831135447.1: *6* getPublicLeoFile
        def getPublicLeoFile():
            fc.outputFile = g.FileLikeObject()
            fc.putProlog()
            fc.putHeader()
            fc.putGlobals()
            fc.putPrefs()
            fc.putFindSettings()
            fname = putVnodes2()
            fc.putTnodes()
            fc.putPostlog()
            return fname, fc.outputFile.getvalue()
        #@-others
        c.endEditing()
        for v in c.hiddenRootNode.children:
            if v.h == PRIVAREA:
                fileName = g.splitLines(v.b)[0].strip()
                break
        else:
            fileName = c.mFileName
        # New in 4.2.  Return ok flag so shutdown logic knows if all went well.
        ok = g.doHook("save1", c=c, p=p, fileName=fileName)
        if ok is None:
            fileName, content = getPublicLeoFile()
            fileName = g.os_path_finalize_join(c.openDirectory, fileName)
            with open(fileName, 'w', encoding="utf-8", newline='\n') as out:
                out.write(content)
            g.es('updated reference file:',
                  g.shortFileName(fileName))
        g.doHook("save2", c=c, p=p, fileName=fileName)
        return ok
    #@+node:ekr.20031218072017.3043: *5* fc.saveAs
    def saveAs(self, fileName):
        c = self.c
        p = c.p
        if not g.doHook("save1", c=c, p=p, fileName=fileName):
            c.endEditing()  # Set the current headline text.
            if c.sqlite_connection:
                c.sqlite_connection.close()
                c.sqlite_connection = None
            self.setDefaultDirectoryForNewFiles(fileName)
            g.app.commander_cacher.save(c, fileName, changeName=True)
            # Disable path-changed messages in writeAllHelper.
            c.ignoreChangedPaths = True
            try:
                if self.write_Leo_file(fileName, outlineOnlyFlag=False):
                    c.clearChanged()  # Clears all dirty bits.
                    self.putSavedMessage(fileName)
            finally:
                c.ignoreChangedPaths = False  # #1367.
            c.redraw_after_icons_changed()
        g.doHook("save2", c=c, p=p, fileName=fileName)
    #@+node:ekr.20031218072017.3044: *5* fc.saveTo
    def saveTo(self, fileName, silent=False):
        c = self.c
        p = c.p
        if not g.doHook("save1", c=c, p=p, fileName=fileName):
            c.endEditing()  # Set the current headline text.
            if c.sqlite_connection:
                c.sqlite_connection.close()
                c.sqlite_connection = None
            self.setDefaultDirectoryForNewFiles(fileName)
            g.app.commander_cacher.save(c, fileName, changeName=False)
            # Disable path-changed messages in writeAllHelper.
            c.ignoreChangedPaths = True
            try:
                self.write_Leo_file(fileName, outlineOnlyFlag=False)
            finally:
                c.ignoreChangedPaths = False
            if not silent:
                self.putSavedMessage(fileName)
            c.redraw_after_icons_changed()
        g.doHook("save2", c=c, p=p, fileName=fileName)
    #@+node:ekr.20050404190914.2: *4* fc.deleteFileWithMessage
    def deleteFileWithMessage(self, fileName, unused_kind):
        try:
            os.remove(fileName)
            return True
        except Exception:
            if self.read_only:
                g.error("read only")
            if not g.unitTesting:
                g.error("exception deleting backup file:", fileName)
                g.es_exception(full=False)
            return False
    #@+node:ekr.20031218072017.1470: *4* fc.put & helpers
    def put(self, s):
        """Put string s to self.outputFile. All output eventually comes here."""
        # Improved code: self.outputFile (a cStringIO object) always exists.
        if s:
            self.putCount += 1
            self.outputFile.write(s)
    #@+node:ekr.20141020112451.18329: *5* put_dquote
    def put_dquote(self):
        self.put('"')
    #@+node:ekr.20141020112451.18330: *5* put_dquoted_bool
    def put_dquoted_bool(self, b):
        if b: self.put('"1"')
        else: self.put('"0"')
    #@+node:ekr.20141020112451.18331: *5* put_flag
    def put_flag(self, a, b):
        if a:
            self.put(" "); self.put(b); self.put('="1"')
    #@+node:ekr.20141020112451.18332: *5* put_in_dquotes
    def put_in_dquotes(self, a):
        self.put('"')
        if a: self.put(a)  # will always be True if we use backquotes.
        else: self.put('0')
        self.put('"')
    #@+node:ekr.20141020112451.18333: *5* put_nl
    def put_nl(self):
        self.put("\n")
    #@+node:ekr.20141020112451.18334: *5* put_tab
    def put_tab(self):
        self.put("\t")
    #@+node:ekr.20141020112451.18335: *5* put_tabs
    def put_tabs(self, n):
        while n > 0:
            self.put("\t")
            n -= 1
    #@+node:ekr.20031218072017.1971: *4* fc.putClipboardHeader
    def putClipboardHeader(self):
        # Put the minimal header.
        self.put('<leo_header file_format="2"/>\n')
    #@+node:ekr.20040324080819.1: *4* fc.putLeoFile & helpers
    def putLeoFile(self):
        self.putProlog()
        self.putHeader()
        self.putGlobals()
        self.putPrefs()
        self.putFindSettings()
        self.putVnodes()
        self.putTnodes()
        self.putPostlog()
    #@+node:ekr.20031218072017.3035: *5* fc.putFindSettings
    def putFindSettings(self):
        # New in 4.3:  These settings never get written to the .leo file.
        self.put("<find_panel_settings/>")
        self.put_nl()
    #@+node:ekr.20031218072017.3037: *5* fc.putGlobals (sets window_position)
    def putGlobals(self):
        """Put a vestigial <globals> element, and write global data to the cache."""
        trace = 'cache' in g.app.debug
        c = self.c
        self.put("<globals/>\n")
        if not c.mFileName:
            return
        c.db['body_outline_ratio'] = str(c.frame.ratio)
        c.db['body_secondary_ratio'] = str(c.frame.secondary_ratio)
        w, h, l, t = c.frame.get_window_info()
        c.db['window_position'] = str(t), str(l), str(h), str(w)
        if trace:
            g.trace(f"\nset c.db for {c.shortFileName()}")
            print('window_position:', c.db['window_position'])
    #@+node:ekr.20031218072017.3041: *5* fc.putHeader
    def putHeader(self):
        tnodes = 0; clone_windows = 0  # Always zero in Leo2.
        if 0:  # For compatibility with versions before Leo 4.5.
            self.put("<leo_header")
            self.put(" file_format="); self.put_in_dquotes("2")
            self.put(" tnodes="); self.put_in_dquotes(str(tnodes))
            self.put(" max_tnode_index="); self.put_in_dquotes(str(0))
            self.put(" clone_windows="); self.put_in_dquotes(str(clone_windows))
            self.put("/>"); self.put_nl()
        else:
            self.put('<leo_header file_format="2"/>\n')
    #@+node:ekr.20031218072017.3042: *5* fc.putPostlog
    def putPostlog(self):
        self.put("</leo_file>"); self.put_nl()
    #@+node:ekr.20031218072017.2066: *5* fc.putPrefs
    def putPrefs(self):
        # New in 4.3:  These settings never get written to the .leo file.
        self.put("<preferences/>")
        self.put_nl()
    #@+node:ekr.20031218072017.1246: *5* fc.putProlog
    def putProlog(self):
        """Put the prolog of the xml file."""
        tag = 'http://leoeditor.com/namespaces/leo-python-editor/1.1'
        self.putXMLLine()
        # Put "created by Leo" line.
        self.put('<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->')
        self.put_nl()
        self.putStyleSheetLine()
        # Put the namespace
        self.put(f'<leo_file xmlns:leo="{tag}" >')
        self.put_nl()
    #@+node:ekr.20031218072017.1248: *5* fc.putStyleSheetLine
    def putStyleSheetLine(self):
        """
        Put the xml stylesheet line.

        Leo 5.3:
        - Use only the stylesheet setting, ignoreing c.frame.stylesheet.
        - Write no stylesheet element if there is no setting.

        The old way made it almost impossible to delete stylesheet element.
        """
        c = self.c
        sheet = (c.config.getString('stylesheet') or '').strip()
        # sheet2 = c.frame.stylesheet and c.frame.stylesheet.strip() or ''
        # sheet = sheet or sheet2
        if sheet:
            s = f"<?xml-stylesheet {sheet} ?>"
            self.put(s)
            self.put_nl()
    #@+node:ekr.20031218072017.1577: *5* fc.putTnode
    def putTnode(self, v):
        # Call put just once.
        gnx = v.fileIndex
        # pylint: disable=consider-using-ternary
        ua = hasattr(v, 'unknownAttributes') and self.putUnknownAttributes(v) or ''
        b = v.b
        body = xml.sax.saxutils.escape(b) if b else ''
        self.put(f'<t tx="{gnx}"{ua}>{body}</t>\n')
    #@+node:ekr.20031218072017.1575: *5* fc.putTnodes
    def putTnodes(self):
        """Puts all tnodes as required for copy or save commands"""
        self.put("<tnodes>\n")
        self.putReferencedTnodes()
        self.put("</tnodes>\n")
    #@+node:ekr.20031218072017.1576: *6* fc.putReferencedTnodes
    def putReferencedTnodes(self):
        """Put all referenced tnodes."""
        c = self.c
        if self.usingClipboard:  # write the current tree.
            theIter = self.currentPosition.self_and_subtree(copy=False)
        else:  # write everything
            theIter = c.all_unique_positions(copy=False)
        # Populate tnodes
        tnodes = {}
        for p in theIter:
            # Make *sure* the file index has the proper form.
            # pylint: disable=unbalanced-tuple-unpacking
            index = p.v.fileIndex
            tnodes[index] = p.v
        # Put all tnodes in index order.
        for index in sorted(tnodes):
            v = tnodes.get(index)
            if v:
                # Write only those tnodes whose vnodes were written.
                # **Note**: @<file> trees are not written unless they contain clones.
                if v.isWriteBit():
                    self.putTnode(v)
            else:
                g.trace('can not happen: no VNode for', repr(index))
                # This prevents the file from being written.
                raise BadLeoFile(f"no VNode for {repr(index)}")
    #@+node:ekr.20031218072017.1863: *5* fc.putVnode & helper
    def putVnode(self, p, isIgnore=False):
        """Write a <v> element corresponding to a VNode."""
        fc = self
        v = p.v
        #
        # Precompute constants.
        isAuto = p.isAtAutoNode() and p.atAutoNodeName().strip()
        isEdit = p.isAtEditNode() and p.atEditNodeName().strip() and not p.hasChildren()
            # Write the entire @edit tree if it has children.
        isFile = p.isAtFileNode()
        isShadow = p.isAtShadowFileNode()
        isThin = p.isAtThinFileNode()
        #
        # Set forcewrite.
        if isIgnore or p.isAtIgnoreNode():
            forceWrite = True
        elif isAuto or isEdit or isFile or isShadow or isThin:
            forceWrite = False
        else:
            forceWrite = True
        #
        # Set the write bit if necessary.
        gnx = v.fileIndex
        if forceWrite or self.usingClipboard:
            v.setWriteBit()  # 4.2: Indicate we wrote the body text.

        attrs = fc.compute_attribute_bits(forceWrite, p)
        #
        # Write the node.
        v_head = f'<v t="{gnx}"{attrs}>'
        if gnx in fc.vnodesDict:
            fc.put(v_head + '</v>\n')
        else:
            fc.vnodesDict[gnx] = True
            v_head += f"<vh>{xml.sax.saxutils.escape(p.v.headString() or '')}</vh>"
            # New in 4.2: don't write child nodes of @file-thin trees
            # (except when writing to clipboard)
            if p.hasChildren() and (forceWrite or self.usingClipboard):
                fc.put(f"{v_head}\n")
                # This optimization eliminates all "recursive" copies.
                p.moveToFirstChild()
                while 1:
                    fc.putVnode(p, isIgnore)
                    if p.hasNext(): p.moveToNext()
                    else: break
                p.moveToParent()  # Restore p in the caller.
                fc.put('</v>\n')
            else:
                fc.put(f"{v_head}</v>\n")  # Call put only once.
    #@+node:ekr.20031218072017.1865: *6* fc.compute_attribute_bits
    def compute_attribute_bits(self, forceWrite, p):
        """Return the initial values of v's attributes."""
        attrs = []
        if p.hasChildren() and not forceWrite and not self.usingClipboard:
            # Fix #526: do this for @auto nodes as well.
            attrs.append(self.putDescendentVnodeUas(p))
            # Fix #1023: never put marked/expanded bits.
                # attrs.append(self.putDescendentAttributes(p))
        return ''.join(attrs)
    #@+node:ekr.20031218072017.1579: *5* fc.putVnodes & helper
    new = True

    def putVnodes(self, p=None):
        """Puts all <v> elements in the order in which they appear in the outline."""
        c = self.c
        c.clearAllVisited()
        self.put("<vnodes>\n")
        # Make only one copy for all calls.
        self.currentPosition = p or c.p
        self.rootPosition = c.rootPosition()
        self.vnodesDict = {}
        if self.usingClipboard:
            self.expanded_gnxs, self.marked_gnxs = set(), set()
                # These will be ignored.
            self.putVnode(self.currentPosition)
                # Write only current tree.
        else:
            for p in c.rootPosition().self_and_siblings():
                self.putVnode(p, isIgnore=p.isAtIgnoreNode())
            # Fix #1018: scan *all* nodes.
            self.setCachedBits()
        self.put("</vnodes>\n")
    #@+node:ekr.20190328160622.1: *6* fc.setCachedBits
    def setCachedBits(self):
        """
        Set the cached expanded and marked bits for *all* nodes.
        Also cache the current position.
        """
        trace = 'cache' in g.app.debug
        c = self.c
        if not c.mFileName:
            return  # New.
        current = [str(z) for z in self.currentPosition.archivedPosition()]
        expanded = [v.gnx for v in c.all_unique_nodes() if v.isExpanded()]
        marked = [v.gnx for v in c.all_unique_nodes() if v.isMarked()]
        c.db['expanded'] = ','.join(expanded)
        c.db['marked'] = ','.join(marked)
        c.db['current_position'] = ','.join(current)
        if trace:
            g.trace(f"\nset c.db for {c.shortFileName()}")
            print('expanded:', expanded)
            print('marked:', marked)
            print('current_position:', current)
            print('')
    #@+node:ekr.20031218072017.1247: *5* fc.putXMLLine
    def putXMLLine(self):
        """Put the **properly encoded** <?xml> element."""
        # Use self.leo_file_encoding encoding.
        self.put(
            f"{g.app.prolog_prefix_string}"
            f'"{self.leo_file_encoding}"'
            f"{g.app.prolog_postfix_string}\n")
    #@+node:ekr.20031218072017.1573: *4* fc.putLeoOutline (to clipboard)
    def putLeoOutline(self, p=None):
        """
        Return a string, *not unicode*, encoded with self.leo_file_encoding,
        suitable for pasting to the clipboard.
        """
        try:
            # g.trace(g.callers(2))
            # Save
            tua = self.descendentTnodeUaDictList
            vua = self.descendentVnodeUaDictList
            gnxDict = self.gnxDict
            vnodesDict = self.vnodesDict
            # Paste.
            p = p or self.c.p
            self.outputFile = g.FileLikeObject()
            self.usingClipboard = True
            self.putProlog()
            self.putClipboardHeader()
            self.putVnodes(p)
            self.putTnodes()
            self.putPostlog()
            s = self.outputFile.getvalue()
            self.outputFile = None
        finally:
            # Restore
            self.descendentTnodeUaDictList = tua
            self.descendentVnodeUaDictList = vua
            self.gnxDict = gnxDict
            self.vnodesDict = vnodesDict
            self.usingClipboard = False
        return s
    #@+node:ekr.20031218072017.3046: *4* fc.write_Leo_file & helpers
    def write_Leo_file(self, fileName, outlineOnlyFlag, toString=False, toOPML=False):
        """Write the .leo file."""
        c, fc = self.c, self
        structure_errors = c.checkOutline()
        if structure_errors:
            g.error('Major structural errors! outline not written')
            return False

        if not outlineOnlyFlag or toOPML:
            g.app.recentFilesManager.writeRecentFilesFile(c)
            fc.writeAllAtFileNodesHelper()  # Ignore any errors.

        if fc.isReadOnly(fileName):
            return False

        if fileName and fileName.endswith('.db'):
            return fc.exportToSqlite(fileName)

        try:
            fc.putCount = 0
            fc.toString = toString
            if toString:
                ok = fc.writeToStringHelper(fileName)
            else:
                ok = fc.writeToFileHelper(fileName, toOPML)
        finally:
            fc.outputFile = None
            fc.toString = False
        return ok

    write_LEO_file = write_Leo_file  # For compatibility with old plugins.
    #@+node:ekr.20040324080359.1: *5* fc.isReadOnly
    def isReadOnly(self, fileName):
        # self.read_only is not valid for Save As and Save To commands.
        if g.os_path_exists(fileName):
            try:
                if not os.access(fileName, os.W_OK):
                    g.error("can not write: read only:", fileName)
                    return True
            except Exception:
                pass  # os.access() may not exist on all platforms.
        return False
    #@+node:ekr.20100119145629.6114: *5* fc.writeAllAtFileNodesHelper
    def writeAllAtFileNodesHelper(self):
        """Write all @<file> nodes and set orphan bits."""
        c = self.c
        try:
            # 2010/01/19: Do *not* signal failure here.
            # This allows Leo to quit properly.
            c.atFileCommands.writeAll(all=False)
            return True
        except Exception:
            # Work around bug 1260415: https://bugs.launchpad.net/leo-editor/+bug/1260415
            g.es_error("exception writing external files")
            g.es_exception()
            g.es('Internal error writing one or more external files.', color='red')
            g.es('Please report this error to:', color='blue')
            g.es('https://groups.google.com/forum/#!forum/leo-editor', color='blue')
            g.es('All changes will be lost unless you', color='red')
            g.es('can save each changed file.', color='red')
            return False
    #@+node:ekr.20100119145629.6111: *5* fc.writeToFileHelper & helpers
    def writeToFileHelper(self, fileName, toOPML):
        c = self.c; toZip = c.isZipped
        ok, backupName = self.createBackupFile(fileName)
        if not ok: return False
        fileName, theActualFile = self.createActualFile(fileName, toOPML, toZip)
        if not theActualFile: return False
        self.mFileName = fileName
        self.outputFile = StringIO()  # Always write to a string.
        try:
            if toOPML:
                if hasattr(c, 'opmlController'):
                    c.opmlController.putToOPML(owner=self)
                else:
                    # This is not likely ever to be called.
                    g.trace('leoOPML plugin not active.')
            else:
                self.putLeoFile()
            s = self.outputFile.getvalue()
            g.app.write_Leo_file_string = s  # 2010/01/19: always set this.
            if toZip:
                self.writeZipFile(s)
            else:
                s = bytes(s, self.leo_file_encoding, 'replace')
                theActualFile.write(s)
                theActualFile.close()
                c.setFileTimeStamp(fileName)
                # raise AttributeError # To test handleWriteLeoFileException.
                # Delete backup file.
                if backupName and g.os_path_exists(backupName):
                    self.deleteFileWithMessage(backupName, 'backup')
            return True
        except Exception:
            self.handleWriteLeoFileException(fileName, backupName, theActualFile)
            return False
    #@+node:ekr.20100119145629.6106: *6* fc.createActualFile
    def createActualFile(self, fileName, toOPML, toZip):
        if toZip:
            self.toString = True
            theActualFile = None
        else:
            try:
                # 2010/01/21: always write in binary mode.
                theActualFile = open(fileName, 'wb')
            except Exception:
                g.es(f"can not create {fileName}")
                g.es_exception()
                theActualFile = None
        return fileName, theActualFile
    #@+node:ekr.20031218072017.3047: *6* fc.createBackupFile
    def createBackupFile(self, fileName):
        """
            Create a closed backup file and copy the file to it,
            but only if the original file exists.
        """
        if g.os_path_exists(fileName):
            fd, backupName = tempfile.mkstemp(text=False)
            f = open(fileName, 'rb')  # rb is essential.
            s = f.read()
            f.close()
            try:
                try:
                    os.write(fd, s)
                finally:
                    os.close(fd)
                ok = True
            except Exception:
                g.error('exception creating backup file')
                g.es_exception()
                ok, backupName = False, None
            if not ok and self.read_only:
                g.error("read only")
        else:
            ok, backupName = True, None
        return ok, backupName
    #@+node:ekr.20100119145629.6108: *6* fc.handleWriteLeoFileException
    def handleWriteLeoFileException(self, fileName, backupName, theActualFile):
        c = self.c
        g.es("exception writing:", fileName)
        g.es_exception(full=True)
        if theActualFile:
            theActualFile.close()
        # Delete fileName.
        if fileName and g.os_path_exists(fileName):
            self.deleteFileWithMessage(fileName, '')
        # Rename backupName to fileName.
        if backupName and g.os_path_exists(backupName):
            g.es("restoring", fileName, "from", backupName)
            # No need to create directories when restoring.
            g.utils_rename(c, backupName, fileName)
        else:
            g.error('backup file does not exist!', repr(backupName))
    #@+node:ekr.20100119145629.6110: *5* fc.writeToStringHelper
    def writeToStringHelper(self, fileName):
        try:
            self.mFileName = fileName
            self.outputFile = StringIO()
            self.putLeoFile()
            s = self.outputFile.getvalue()
            g.app.write_Leo_file_string = s
            return True
        except Exception:
            g.es("exception writing:", fileName)
            g.es_exception(full=True)
            g.app.write_Leo_file_string = ''
            return False
    #@+node:ekr.20070412095520: *5* fc.writeZipFile
    def writeZipFile(self, s):
        # The name of the file in the archive.
        contentsName = g.toEncodedString(
            g.shortFileName(self.mFileName),
            self.leo_file_encoding, reportErrors=True)
        # The name of the archive itself.
        fileName = g.toEncodedString(
            self.mFileName,
            self.leo_file_encoding, reportErrors=True)
        # Write the archive.
        theFile = zipfile.ZipFile(fileName, 'w', zipfile.ZIP_DEFLATED)
        theFile.writestr(contentsName, s)
        theFile.close()
    #@+node:vitalije.20170630172118.1: *5* fc.exportToSqlite
    def exportToSqlite(self, fileName):
        """Dump all vnodes to sqlite database. Returns True on success."""
        # fc = self
        c = self.c; fc = self
        if c.sqlite_connection is None:
            c.sqlite_connection = sqlite3.connect(fileName,
                                        isolation_level='DEFERRED')
        conn = c.sqlite_connection

        def dump_u(v):
            try:
                s = pickle.dumps(v.u, protocol=1)
            except pickle.PicklingError:
                s = ''
                g.trace('unpickleable value', repr(v.u))
            return s

        dbrow = lambda v: (
                v.gnx,
                v.h,
                v.b,
                ' '.join(x.gnx for x in v.children),
                ' '.join(x.gnx for x in v.parents),
                v.iconVal,
                v.statusBits,
                dump_u(v)
            )
        ok = False
        try:
            fc.prepareDbTables(conn)
            fc.exportDbVersion(conn)
            fc.exportVnodesToSqlite(conn, (dbrow(v) for v in c.all_unique_nodes()))
            fc.exportGeomToSqlite(conn)
            fc.exportHashesToSqlite(conn)
            conn.commit()
            ok = True
        except sqlite3.Error as e:
            g.internalError(e)
        return ok
    #@+node:vitalije.20170705075107.1: *6* fc.decodePosition
    def decodePosition(self, s):
        """Creates position from its string representation encoded by fc.encodePosition."""
        fc = self
        if not s:
            return fc.c.rootPosition()
        sep = '<->'
        comma = ','
        stack = [x.split(comma) for x in s.split(sep)]
        stack = [(fc.gnxDict[x], int(y)) for x, y in stack]
        v, ci = stack[-1]
        p = leoNodes.Position(v, ci, stack[:-1])
        return p
    #@+node:vitalije.20170705075117.1: *6* fc.encodePosition
    def encodePosition(self, p):
        """New schema for encoding current position hopefully simplier one."""
        jn = '<->'
        mk = '%s,%s'
        res = [mk % (x.gnx, y) for x, y in p.stack]
        res.append(mk % (p.gnx, p._childIndex))
        return jn.join(res)
    #@+node:vitalije.20170811130512.1: *6* fc.prepareDbTables
    def prepareDbTables(self, conn):
        conn.execute('''drop table if exists vnodes;''')
        conn.execute(
            '''
            create table if not exists vnodes(
                gnx primary key,
                head,
                body,
                children,
                parents,
                iconVal,
                statusBits,
                ua);''',
        )
        conn.execute(
            '''create table if not exists extra_infos(name primary key, value)''')
    #@+node:vitalije.20170701161851.1: *6* fc.exportVnodesToSqlite
    def exportVnodesToSqlite(self, conn, rows):
        conn.executemany(
            '''insert into vnodes
            (gnx, head, body, children, parents,
                iconVal, statusBits, ua)
            values(?,?,?,?,?,?,?,?);''',
            rows,
        )
    #@+node:vitalije.20170701162052.1: *6* fc.exportGeomToSqlite
    def exportGeomToSqlite(self, conn):
        c = self.c
        data = zip(
            (
                'width', 'height', 'left', 'top',
                'ratio', 'secondary_ratio',
                'current_position'
            ),
            c.frame.get_window_info() +
            (
                c.frame.ratio, c.frame.secondary_ratio,
                self.encodePosition(c.p)
            )
        )
        conn.executemany('replace into extra_infos(name, value) values(?, ?)', data)
    #@+node:vitalije.20170811130559.1: *6* fc.exportDbVersion
    def exportDbVersion(self, conn):
        conn.execute(
            "replace into extra_infos(name, value) values('dbversion', ?)", ('1.0',))
    #@+node:vitalije.20170701162204.1: *6* fc.exportHashesToSqlite
    def exportHashesToSqlite(self, conn):
        c = self.c

        def md5(x):
            try:
                s = open(x, 'rb').read()
            except Exception:
                return ''
            s = s.replace(b'\r\n', b'\n')
            return hashlib.md5(s).hexdigest()

        files = set()

        p = c.rootPosition()
        while p:
            if p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            elif p.isAtAutoNode() or p.isAtFileNode():
                fn = c.getNodeFileName(p)
                files.add((fn, 'md5_' + p.gnx))
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        conn.executemany(
            'replace into extra_infos(name, value) values(?,?)',
            map(lambda x: (x[1], md5(x[0])), files))
    #@+node:ekr.20031218072017.2012: *4* fc.writeAtFileNodes
    @cmd('write-at-file-nodes')
    def writeAtFileNodes(self, event=None):
        """Write all @file nodes in the selected outline."""
        c = self.c
        c.init_error_dialogs()
        c.atFileCommands.writeAll(all=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20031218072017.1666: *4* fc.writeDirtyAtFileNodes
    @cmd('write-dirty-at-file-nodes')
    def writeDirtyAtFileNodes(self, event=None):
        """Write all changed @file Nodes."""
        c = self.c
        c.init_error_dialogs()
        c.atFileCommands.writeAll(dirty=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20080801071227.6: *4* fc.writeDirtyAtShadowNodes
    def writeDirtyAtShadowNodes(self, event=None):
        """Write all changed @shadow Nodes."""
        self.c.atFileCommands.writeDirtyAtShadowNodes()
    #@+node:ekr.20031218072017.2013: *4* fc.writeMissingAtFileNodes
    @cmd('write-missing-at-file-nodes')
    def writeMissingAtFileNodes(self, event=None):
        """Write all @file nodes for which the corresponding external file does not exist."""
        c = self.c
        if c.p:
            c.atFileCommands.writeMissing(c.p)
    #@+node:ekr.20031218072017.3050: *4* fc.writeOutlineOnly
    @cmd('write-outline-only')
    def writeOutlineOnly(self, event=None):
        """Write the entire outline without writing any derived files."""
        c = self.c
        c.endEditing()
        self.write_Leo_file(self.mFileName, outlineOnlyFlag=True)
        g.blue('done')
    #@+node:ekr.20080805114146.2: *3* fc.Utils
    #@+node:ekr.20061006104837.1: *4* fc.archivedPositionToPosition
    def archivedPositionToPosition(self, s):
        """Convert an archived position (a string) to a position."""
        return self.c.archivedPositionToPosition(s)
    #@+node:ekr.20031218072017.1570: *4* fc.assignFileIndices & compactFileIndices
    def assignFileIndices(self):
        """Assign a file index to all tnodes"""
        pass  # No longer needed: we assign indices as needed.

    # Indices are now immutable, so there is no longer any difference between these two routines.

    compactFileIndices = assignFileIndices
    #@+node:ekr.20080805085257.1: *4* fc.createUaList
    def createUaList(self, aList):
        """
        Given aList of pairs (p,torv), return a list of pairs (torv,d)
        where d contains all picklable items of torv.unknownAttributes.
        """
        result = []
        for p, torv in aList:
            if isinstance(torv.unknownAttributes, dict):
                # Create a new dict containing only entries that can be pickled.
                d = dict(torv.unknownAttributes)  # Copy the dict.
                for key in d:
                    # Just see if val can be pickled.  Suppress any error.
                    ok = self.pickle(torv=torv, val=d.get(key), tag=None)
                    if not ok:
                        del d[key]
                        g.warning("ignoring bad unknownAttributes key", key, "in", p.h)
                if d:
                    result.append((torv, d),)
            else:
                g.warning("ignoring non-dictionary uA for", p)
        return result
    #@+node:ekr.20080805085257.2: *4* fc.pickle
    def pickle(self, torv, val, tag):
        """Pickle val and return the hexlified result."""
        try:
            s = pickle.dumps(val, protocol=1)
            s2 = binascii.hexlify(s)
            s3 = g.toUnicode(s2, 'utf-8')
            field = f' {tag}="{s3}"'
            return field
        except pickle.PicklingError:
            if tag:  # The caller will print the error if tag is None.
                g.warning("ignoring non-pickleable value", val, "in", torv)
            return ''
        except Exception:
            g.error("fc.pickle: unexpected exception in", torv)
            g.es_exception()
            return ''
    #@+node:ekr.20080805071954.2: *4* fc.putDescendentVnodeUas
    def putDescendentVnodeUas(self, p):
        """
        Return the a uA field for descendent VNode attributes,
        suitable for reconstituting uA's for anonymous vnodes.
        """
        #
        # Create aList of tuples (p,v) having a valid unknownAttributes dict.
        # Create dictionary: keys are vnodes, values are corresonding archived positions.
        pDict = {}; aList = []
        for p2 in p.self_and_subtree(copy=False):
            if hasattr(p2.v, "unknownAttributes"):
                aList.append((p2.copy(), p2.v),)
                pDict[p2.v] = p2.archivedPosition(root_p=p)
        # Create aList of pairs (v,d) where d contains only pickleable entries.
        if aList: aList = self.createUaList(aList)
        if not aList: return ''
        # Create d, an enclosing dict to hold all the inner dicts.
        d = {}
        for v, d2 in aList:
            aList2 = [str(z) for z in pDict.get(v)]
            key = '.'.join(aList2)
            d[key] = d2
        # Pickle and hexlify d
        # pylint: disable=consider-using-ternary
        return d and self.pickle(
            torv=p.v, val=d, tag='descendentVnodeUnknownAttributes') or ''
    #@+node:ekr.20050418161620.2: *4* fc.putUaHelper
    def putUaHelper(self, torv, key, val):
        """Put attribute whose name is key and value is val to the output stream."""
        # New in 4.3: leave string attributes starting with 'str_' alone.
        if key.startswith('str_'):
            if isinstance(val, (str, bytes)):
                val = g.toUnicode(val)
                attr = f' {key}="{xml.sax.saxutils.escape(val)}"'
                return attr
            g.trace(type(val), repr(val))
            g.warning("ignoring non-string attribute", key, "in", torv)
            return ''
        return self.pickle(torv=torv, val=val, tag=key)
    #@+node:EKR.20040526202501: *4* fc.putUnknownAttributes
    def putUnknownAttributes(self, torv):
        """Put pickleable values for all keys in torv.unknownAttributes dictionary."""
        attrDict = torv.unknownAttributes
        if isinstance(attrDict, dict):
            val = ''.join(
                [self.putUaHelper(torv, key, val)
                    for key, val in attrDict.items()])
            return val
        g.warning("ignoring non-dictionary unknownAttributes for", torv)
        return ''
    #@+node:ekr.20080805132422.3: *4* fc.resolveArchivedPosition
    def resolveArchivedPosition(self, archivedPosition, root_v):
        """
        Return a VNode corresponding to the archived position relative to root
        node root_v.
        """

        def oops(message):
            """Give an error only if no file errors have been seen."""
            return None

        try:
            aList = [int(z) for z in archivedPosition.split('.')]
            aList.reverse()
        except Exception:
            return oops(f'"{archivedPosition}"')
        if not aList:
            return oops('empty')
        last_v = root_v
        n = aList.pop()
        if n != 0:
            return oops(f'root index="{n}"')
        while aList:
            n = aList.pop()
            children = last_v.children
            if n < len(children):
                last_v = children[n]
            else:
                return oops(f'bad index="{n}", len(children)="{len(children)}"')
        return last_v
    #@+node:ekr.20060919110638.11: *4* fc.resolveTnodeLists
    def resolveTnodeLists(self):
        """
        Called *before* reading external files.
        """
        c = self.c
        for p in c.all_unique_positions(copy=False):
            if hasattr(p.v, 'tempTnodeList'):
                result = []
                for tnx in p.v.tempTnodeList:
                    index = self.canonicalTnodeIndex(tnx)
                    # new gnxs:
                    index = g.toUnicode(index)
                    v = self.gnxDict.get(index)
                    if v:
                        result.append(v)
                    else:
                        g.trace(f"*** No VNode for {tnx}")
                if result:
                    p.v.tnodeList = result
                delattr(p.v, 'tempTnodeList')
    #@+node:ekr.20031218072017.3045: *4* fc.setDefaultDirectoryForNewFiles
    def setDefaultDirectoryForNewFiles(self, fileName):
        """Set c.openDirectory for new files for the benefit of leoAtFile.scanAllDirectives."""
        c = self.c
        if not c.openDirectory:
            theDir = g.os_path_dirname(fileName)
            if theDir and g.os_path_isabs(theDir) and g.os_path_exists(theDir):
                c.openDirectory = c.frame.openDirectory = theDir
    #@+node:ekr.20060919110638.13: *4* fc.setPositionsFromVnodes
    def setPositionsFromVnodes(self):

        c, root = self.c, self.c.rootPosition()
        if c.sqlite_connection:
            # position is already selected
            return
        current, str_pos = None, None
        if c.mFileName:
            str_pos = c.db.get('current_position')
        if str_pos is None:
            d = root.v.u
            if d: str_pos = d.get('str_leo_pos')
        if str_pos is not None:
            current = self.archivedPositionToPosition(str_pos)
        c.setCurrentPosition(current or c.rootPosition())
    #@-others
#@+node:ekr.20180708114847.1: ** dump-clone-parents
@g.command('dump-clone-parents')
def dump_clone_parents(event):
    c = event.get('c')
    if not c:
        return
    print('dump-clone-parents...')
    d = c.fileCommands.gnxDict
    for gnx in d:
        v = d.get(gnx)
        if len(v.parents) > 1:
            print(v.h)
            g.printObj(v.parents)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

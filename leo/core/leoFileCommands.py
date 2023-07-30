#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3018: * @file leoFileCommands.py
"""Classes relating to reading and writing .leo files."""
#@+<< leoFileCommands imports >>
#@+node:ekr.20050405141130: ** << leoFileCommands imports >>
from __future__ import annotations
import binascii
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
import difflib
import hashlib
import io
import json
import os
import pickle
import shutil
import sqlite3
import tempfile
import time
from typing import Any, Optional, Union, TYPE_CHECKING
import zipfile
import xml.etree.ElementTree as ElementTree
import xml.sax
import xml.sax.saxutils
from leo.core import leoGlobals as g
from leo.core import leoNodes
#@-<< leoFileCommands imports >>
#@+<< leoFileCommands annotations >>
#@+node:ekr.20220819121640.1: ** << leoFileCommands annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode

#@-<< leoFileCommands annotations >>
#@+others
#@+node:ekr.20150509194827.1: ** cmd (decorator)
def cmd(name: Any) -> Callable:
    """Command decorator for the FileCommands class."""
    return g.new_cmd_decorator(name, ['c', 'fileCommands',])
#@+node:ekr.20210316035506.1: **  commands (leoFileCommands.py)
#@+node:ekr.20180708114847.1: *3* dump-clone-parents
@g.command('dump-clone-parents')
def dump_clone_parents(event: Event) -> None:
    """Print the parent vnodes of all cloned vnodes."""
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
#@+node:ekr.20210309114903.1: *3* dump-gnx-dict
@g.command('dump-gnx-dict')
def dump_gnx_dict(event: Event) -> None:
    """Dump c.fileCommands.gnxDict."""
    c = event.get('c')
    if not c:
        return
    d = c.fileCommands.gnxDict
    g.printObj(d, tag='gnxDict')
#@+node:felix.20220618222639.1: ** class SetEncoder
class SetJSONEncoder(json.JSONEncoder):
    # Used to encode JSON in leojs files
    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
#@+node:ekr.20060918164811: ** class BadLeoFile
class BadLeoFile(Exception):

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return "Bad Leo File:" + self.message
#@+node:ekr.20180602062323.1: ** class FastRead
class FastRead:

    nativeVnodeAttributes = (
        'a',
        'descendentTnodeUnknownAttributes',
        'descendentVnodeUnknownAttributes',
        'expanded', 'marks', 't',
        # 'tnodeList',  # Removed in Leo 4.7.
    )

    def __init__(self, c: Cmdr, gnx2vnode: dict[str, VNode]) -> None:
        self.c = c
        self.gnx2vnode = gnx2vnode

    #@+others
    #@+node:ekr.20180604110143.1: *3* fast.readFile
    def readFile(self, theFile: Any, path: str) -> VNode:
        """Read the file, change splitter ratios, and return its hidden vnode."""
        s = theFile.read()
        v, g_element = self.readWithElementTree(path, s)
        if not v:  # #1510.
            return None
        # #1047: only this method changes splitter sizes.
        self.scanGlobals(g_element)
        #
        # #1111: ensure that all outlines have at least one node.
        if not v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            v.children = [new_vnode]
        return v

    #@+node:felix.20220618164929.1: *3* fast.readJsonFile
    def readJsonFile(self, theFile: Any, path: str) -> Optional[VNode]:
        """Read the leojs JSON file, change splitter ratios, and return its hidden vnode."""
        s = theFile.read()
        v, g_dict = self.readWithJsonTree(path, s)
        if not v:  # #1510.
            return None
        # #1047: only this method changes splitter sizes.
        self.scanJsonGlobals(g_dict)
        #
        # #1111: ensure that all outlines have at least one node.
        if not v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            v.children = [new_vnode]
        return v

    #@+node:ekr.20210316035646.1: *3* fast.readFileFromClipboard
    def readFileFromClipboard(self, s_or_b: Union[bytes, str]) -> Optional[VNode]:
        """
        Recreate a file from a string s_or_b, and return its hidden vnode.

        Unlike readFile above, this does not affect splitter sizes.
        """
        hidden_v, g_element = self.readWithElementTree(path=None, s_or_b=s_or_b)
        if not hidden_v:
            return None
        #
        # Ensure that all outlines have at least one node.
        if not hidden_v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            hidden_v.children = [new_vnode]
        return hidden_v
    #@+node:ekr.20180602062323.7: *3* fast.readWithElementTree & helpers
    # #1510: https://en.wikipedia.org/wiki/Valid_characters_in_XML.
    translate_dict = {z: None for z in range(20) if chr(z) not in '\t\r\n'}

    def readWithElementTree(self, path: str, s_or_b: Union[str, bytes]) -> tuple[VNode, Any]:

        contents = g.toUnicode(s_or_b)
        table = contents.maketrans(self.translate_dict)  # type:ignore #1510.
        contents = contents.translate(table)  # #1036, #1046.
        try:
            xroot = ElementTree.fromstring(contents)
        except Exception as e:
            # #970: Report failure here.
            if path:
                message = f"bad .leo file: {g.shortFileName(path)}"
            else:
                message = 'The clipboard is not a valid .leo file'
            g.es_print('\n' + message, color='red')
            g.es_print(g.toUnicode(e))
            print('')
            return None, None  # #1510: Return a tuple.
        g_element = xroot.find('globals')
        v_elements = xroot.find('vnodes')
        t_elements = xroot.find('tnodes')
        gnx2body, gnx2ua = self.scanTnodes(t_elements)
        hidden_v = self.scanVnodes(gnx2body, self.gnx2vnode, gnx2ua, v_elements)
        self.updateBodies(gnx2body, self.gnx2vnode)
        self.handleBits()
        return hidden_v, g_element
    #@+node:ekr.20180624125321.1: *4* fast.handleBits (reads c.db)
    def handleBits(self) -> None:
        """Restore the expanded and marked bits from c.db."""
        c, fc = self.c, self.c.fileCommands
        expanded = c.db.get('expanded')
        marked = c.db.get('marked')
        expanded = expanded.split(',') if expanded else []
        marked = marked.split(',') if marked else []
        fc.descendentExpandedList = expanded
        fc.descendentMarksList = marked
    #@+node:ekr.20180606041211.1: *4* fast.resolveUa
    def resolveUa(self, attr: Any, val: Any, kind: str = None) -> Any:  # Kind is for unit testing.
        """Parse an unknown attribute in a <v> or <t> element."""
        try:
            val = g.toEncodedString(val)
        except Exception:
            g.es_print('unexpected exception converting hexlified string to string')
            g.es_exception()
            return ''
        # Leave string attributes starting with 'str_' alone.
        if attr.startswith('str_'):
            if isinstance(val, (str, bytes)):
                return g.toUnicode(val)
        # Support JSON encoded attributes
        if attr.startswith('json_'):
            if isinstance(val, (str, bytes)):
                try:
                    return json.loads(g.toUnicode(val))
                except json.JSONDecodeError:
                    # fall back to standard handling
                    g.trace(f"attribute not JSON encoded {attr}={g.toUnicode(val)}")
        try:
            # Throws a TypeError if val is not a hex string.
            binString = binascii.unhexlify(val)
        except Exception:
            # Assume that Leo 4.1 or above wrote the attribute.
            if g.unitTesting:
                assert kind == 'raw', f"unit test failed: kind={kind}"
            else:
                g.trace(f"can not unhexlify {attr}={val}")
            return ''
        try:
            # No change needed to support protocols.
            return pickle.loads(binString)
        except Exception:
            try:
                val2 = pickle.loads(binString, encoding='bytes')
                return g.toUnicode(val2)
            except Exception:
                g.trace(f"can not unpickle {attr}={val}")
                return ''
    #@+node:ekr.20180605062300.1: *4* fast.scanGlobals & helper
    def scanGlobals(self, g_element: Any) -> None:
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
    #@+node:ekr.20180708060437.1: *5* fast.getGlobalData
    def getGlobalData(self) -> dict[str, Any]:
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
    #@+node:ekr.20180602062323.8: *4* fast.scanTnodes
    def scanTnodes(self, t_elements: Any) -> tuple[dict[str, str], dict[str, Any]]:

        gnx2body: dict[str, str] = {}
        gnx2ua: dict[str, dict] = defaultdict(dict)
        for e in t_elements:
            # First, find the gnx.
            gnx = e.attrib['tx']
            gnx2body[gnx] = e.text or ''
            # Next, scan for uA's for this gnx.
            for key, val in e.attrib.items():
                if key != 'tx':
                    s: Optional[str] = self.resolveUa(key, val)
                    if s:
                        gnx2ua[gnx][key] = s
        return gnx2body, gnx2ua
    #@+node:ekr.20180602062323.9: *4* fast.scanVnodes & helper
    def scanVnodes(self,
        gnx2body: dict[str, str],
        gnx2vnode: dict[str, VNode],
        gnx2ua: dict[str, Any],
        v_elements: Any,
    ) -> VNode:

        c, fc = self.c, self.c.fileCommands
        #@+<< define v_element_visitor >>
        #@+node:ekr.20180605102822.1: *5* << define v_element_visitor >>
        def v_element_visitor(parent_e: Any, parent_v: VNode) -> None:
            """Visit the given element, creating or updating the parent vnode."""
            for e in parent_e:
                assert e.tag in ('v', 'vh'), e.tag
                if e.tag == 'vh':
                    parent_v._headString = g.toUnicode(e.text or '')
                    continue
                # #1581: Attempt to handle old Leo outlines.
                try:
                    gnx = e.attrib['t']
                    v = gnx2vnode.get(gnx)
                except KeyError:
                    # g.trace('no "t" attrib')
                    gnx = None
                    v = None
                if v:
                    # A clone
                    parent_v.children.append(v)
                    v.parents.append(parent_v)
                    # The body overrides any previous body text.
                    body = g.toUnicode(gnx2body.get(gnx) or '')
                    assert isinstance(body, str), body.__class__.__name__
                    v._bodyString = body
                else:
                    #@+<< Make a new vnode, linked to the parent >>
                    #@+node:ekr.20180605075042.1: *6* << Make a new vnode, linked to the parent >>
                    v = leoNodes.VNode(context=c, gnx=gnx)
                    gnx2vnode[gnx] = v
                    parent_v.children.append(v)
                    v.parents.append(parent_v)
                    body = g.toUnicode(gnx2body.get(gnx) or '')
                    assert isinstance(body, str), body.__class__.__name__
                    v._bodyString = body
                    v._headString = 'PLACE HOLDER'
                    #@-<< Make a new vnode, linked to the parent >>
                    #@+<< handle all other v attributes >>
                    #@+node:ekr.20180605075113.1: *6* << handle all other v attributes >>
                    # FastRead.nativeVnodeAttributes defines the native attributes of <v> elements.
                    d = e.attrib
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
                    uaDict = gnx2ua[gnx]  # A defaultdict(dict)
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
    #@+node:ekr.20230724092804.1: *4* fast.updateBodies
    def updateBodies(self, gnx2body: dict[str, str], gnx2vnode: dict[str, VNode]) -> None:
        """Update bodies to enforce the "pasted wins" policy."""
        for gnx in gnx2body:
            body = gnx2body[gnx]
            try:
                v = gnx2vnode[gnx]
                v.b = body
            except KeyError:
                pass
    #@+node:felix.20220621221215.1: *3* fast.readFileFromJsonClipboard
    def readFileFromJsonClipboard(self, s: str) -> VNode:
        """
        Recreate a file from a JSON string s, and return its hidden vnode.
        """
        v, unused = self.readWithJsonTree(path=None, s=s)
        if not v:  # #1510.
            return None
        #
        # #1111: ensure that all outlines have at least one node.
        if not v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            v.children = [new_vnode]
        return v
    #@+node:felix.20220618165345.1: *3* fast.readWithJsonTree & helpers
    def readWithJsonTree(self, path: str, s: str) -> tuple[VNode, Any]:
        try:
            d = json.loads(s)
        except Exception:
            g.trace(f"Error converting JSON from  .leojs file: {path}")
            g.es_exception()
            return None, None

        try:
            g_element = d.get('globals', {})  # globals is optional
            v_elements = d.get('vnodes')
            t_elements = d.get('tnodes')
            gnx2ua: dict = defaultdict(dict)
            gnx2ua.update(d.get('uas', {}))  # User attributes in their own dict for leojs files
            gnx2body = self.scanJsonTnodes(t_elements)
            hidden_v = self.scanJsonVnodes(gnx2body, self.gnx2vnode, gnx2ua, v_elements)
            self.updateBodies(gnx2body, self.gnx2vnode)
            self.handleBits()
        except Exception:
            g.trace(f"Error .leojs JSON is not valid: {path}")
            g.es_exception()
            return None, None

        return hidden_v, g_element

    #@+node:felix.20220618181309.1: *4* fast.scanJsonGlobals
    def scanJsonGlobals(self, json_d: dict) -> None:
        """Set the geometries from the globals dict."""
        c = self.c

        def toInt(x: int, default: int) -> int:
            try:
                return int(x)
            except Exception:
                return default

        # Priority 1: command-line args
        windowSize = g.app.loadManager.options.get('windowSize')
        windowSpot = g.app.loadManager.options.get('windowSpot')
        #
        # Priority 2: The cache.
        db_top, db_left, db_height, db_width = c.db.get('window_position', (None, None, None, None))
        #
        # Priority 3: The globals dict in the .leojs file.
        #             Leo doesn't write the globals element, but leoInteg might.

        # height & width
        height, width = windowSize or (None, None)
        if height is None:
            height, width = json_d.get('height'), json_d.get('width')
        if height is None:
            height, width = db_height, db_width
        height, width = toInt(height, 500), toInt(width, 800)
        #
        # top, left.
        top, left = windowSpot or (None, None)
        if top is None:
            top, left = json_d.get('top'), json_d.get('left')
        if top is None:
            top, left = db_top, db_left
        top, left = toInt(top, 50), toInt(left, 50)
        #
        # r1, r2.
        r1 = float(c.db.get('body_outline_ratio', '0.5'))
        r2 = float(c.db.get('body_secondary_ratio', '0.5'))
        if 'size' in g.app.debug:
            g.trace(width, height, left, top, c.shortFileName())
        # c.frame may be a NullFrame.
        c.frame.setTopGeometry(width, height, left, top)
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

    #@+node:felix.20220618174623.1: *4* fast.scanJsonTnodes
    def scanJsonTnodes(self, t_elements: Any) -> dict[str, str]:

        gnx2body: dict[str, str] = {}

        for gnx, body in t_elements.items():
            gnx2body[gnx] = body or ''

        return gnx2body

    #@+node:felix.20220618174639.1: *4* scanJsonVnodes & helper
    def scanJsonVnodes(self,
        gnx2body: dict[str, str],
        gnx2vnode: dict[str, VNode],
        gnx2ua: dict[str, Any],
        v_elements: Any,
    ) -> Optional[VNode]:

        c, fc = self.c, self.c.fileCommands

        def v_element_visitor(parent_e: Any, parent_v: VNode) -> None:
            """Visit the given element, creating or updating the parent vnode."""
            for i, v_dict in enumerate(parent_e):
                # Get the gnx.
                gnx = v_dict.get('gnx')
                if not gnx:
                    g.trace("Bad .leojs file: no gnx in v_dict")
                    g.printObj(v_dict)
                    return
                #
                # Create the vnode.
                assert len(parent_v.children) == i, (i, parent_v, parent_v.children)

                try:
                    v = gnx2vnode.get(gnx)
                except KeyError:
                    # g.trace('no "t" attrib')
                    gnx = None
                    v = None
                if v:
                    # A clone
                    parent_v.children.append(v)
                    v.parents.append(parent_v)
                    # The body overrides any previous body text.
                    body = g.toUnicode(gnx2body.get(gnx) or '')
                    assert isinstance(body, str), body.__class__.__name__
                    v._bodyString = body
                else:
                    v = leoNodes.VNode(context=c, gnx=gnx)
                    gnx2vnode[gnx] = v
                    parent_v.children.append(v)
                    v.parents.append(parent_v)

                    v._headString = v_dict.get('vh', '')
                    v._bodyString = gnx2body.get(gnx, '')
                    v.statusBits = v_dict.get('status', 0)  # Needed ?
                    if v.isExpanded():
                        fc.descendentExpandedList.append(gnx)
                    if v.isMarked():
                        fc.descendentMarksList.append(gnx)
                    #

                    # Handle vnode uA's
                    uaDict = gnx2ua[gnx]  # A defaultdict(dict)

                    if uaDict:
                        v.unknownAttributes = uaDict

                    # Recursively create the children.
                    v_element_visitor(v_dict.get('children', []), v)

        gnx = 'hidden-root-vnode-gnx'
        hidden_v = leoNodes.VNode(context=c, gnx=gnx)
        hidden_v._headString = '<hidden root vnode>'
        gnx2vnode[gnx] = hidden_v
        #
        # Traverse the tree of v elements.
        v_element_visitor(v_elements, hidden_v)

        # add all possible UAs for external files loading process to add UA's.
        fc.descendentTnodeUaDictList.append(gnx2ua)
        return hidden_v
    #@-others
#@+node:ekr.20160514120347.1: ** class FileCommands
class FileCommands:
    """A class creating the FileCommands subcommander."""
    #@+others
    #@+node:ekr.20090218115025.4: *3* fc.Birth
    #@+node:ekr.20031218072017.3019: *4* fc.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for FileCommands class."""
        self.c = c
        self.frame = c.frame
        self.nativeTnodeAttributes = ('tx',)
        self.nativeVnodeAttributes = (
            'a',
            'descendentTnodeUnknownAttributes',
            'descendentVnodeUnknownAttributes',  # New in Leo 4.5.
            'expanded', 'marks', 't',
            # 'tnodeList',  # Removed in Leo 4.7.
        )
        self.initIvars()
    #@+node:ekr.20090218115025.5: *4* fc.initIvars
    def initIvars(self) -> None:
        """Init ivars of the FileCommands class."""
        # General...
        c = self.c
        self.mFileName = ""
        self.fileDate = -1
        self.leo_file_encoding = c.config.new_leo_file_encoding
        # For reading...
        self.checking = False  # True: checking only: do *not* alter the outline.
        self.descendentExpandedList: list[str] = []  # List of gnx's.
        self.descendentMarksList: list[str] = []  # List of gnx's.
        self.descendentTnodeUaDictList: list[Any] = []
        self.descendentVnodeUaDictList: list[Any] = []
        self.ratio = 0.5
        self.currentVnode: VNode = None
        # For writing...
        self.read_only = False
        self.rootPosition: Position = None
        self.outputFile: io.StringIO = None
        self.openDirectory: str = None
        self.usingClipboard = False
        self.currentPosition: Position = None
        # New in 3.12...
        self.copiedTree: Position = None
        # fc.gnxDict is never re-inited.
        self.gnxDict: dict[str, VNode] = {}  # Keys are gnx strings. Values are vnodes.
        self.vnodesDict: dict[str, Any] = {}  # keys are gnx strings; values are ignored
    #@+node:ekr.20210316042224.1: *3* fc: Commands
    #@+node:ekr.20031218072017.2012: *4* write-at-file-nodes
    @cmd('write-at-file-nodes')
    def writeAtFileNodes(self, event: Event = None) -> None:
        """Write all @file nodes in the selected outline."""
        c = self.c
        c.endEditing()
        c.init_error_dialogs()
        c.atFileCommands.writeAll(all=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20031218072017.1666: *4* write-dirty-at-file-nodes
    @cmd('write-dirty-at-file-nodes')
    def writeDirtyAtFileNodes(self, event: Event = None) -> None:
        """Write all changed @file Nodes."""
        c = self.c
        c.endEditing()
        c.init_error_dialogs()
        c.atFileCommands.writeAll(dirty=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20031218072017.2013: *4* write-missing-at-file-nodes
    @cmd('write-missing-at-file-nodes')
    def writeMissingAtFileNodes(self, event: Event = None) -> None:
        """Write all @file nodes for which the corresponding external file does not exist."""
        c = self.c
        c.endEditing()
        c.atFileCommands.writeMissing(c.p)
    #@+node:ekr.20031218072017.3050: *4* write-outline-only
    @cmd('write-outline-only')
    def writeOutlineOnly(self, event: Event = None) -> None:
        """Write the entire outline without writing any derived files."""
        c = self.c
        c.endEditing()
        self.writeOutline(fileName=self.mFileName)

    #@+node:ekr.20230406053535.1: *4* write-zip-archive
    @cmd('write-zip-archive')
    def writeZipArchive(self, event: Event = None) -> None:
        """
        Write a .zip file containing this .leo file and all external files.

        Write to os.environ['LEO_ARCHIVE'] or the directory containing this .leo file.
        """
        c = self.c
        leo_file = c.fileName()
        if not leo_file:
            print('Please save this outline first')
            return

        # Compute the timestamp.
        timestamp = datetime.now().timestamp()
        time = datetime.fromtimestamp(timestamp)
        time_s = time.strftime('%Y-%m-%d-%H-%M-%S')

        # Compute archive_name.
        archive_name = None
        try:
            directory = os.environ['LEO_ARCHIVE']
            if not os.path.exists(directory):
                g.es_print(f"Not found: {directory!r}")
                archive_name = rf"{directory}{os.sep}{g.shortFileName(leo_file)}-{time_s}.zip"
        except KeyError:
            pass
        if not archive_name:
            archive_name = rf"{leo_file}-{time_s}.zip"

        # Write the archive.
        try:
            n = 1
            with zipfile.ZipFile(archive_name, 'w') as f:
                f.write(leo_file)
                for p in c.all_unique_positions():
                    if p.isAnyAtFileNode():
                        fn = c.fullPath(p)
                        if os.path.exists(fn):
                            n += 1
                            f.write(fn)
            print(f"Wrote {archive_name} containing {n} file{g.plural(n)}")
        except Exception:
            g.es_print(f"Error writing {archive_name}")
            g.es_exception()

    #@+node:ekr.20210316034350.1: *3* fc: File Utils
    #@+node:ekr.20031218072017.3047: *4* fc.createBackupFile
    def createBackupFile(self, fileName: str) -> tuple[bool, str]:
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
    #@+node:ekr.20050404190914.2: *4* fc.deleteBackupFile
    def deleteBackupFile(self, fileName: str) -> None:
        try:
            os.remove(fileName)
        except Exception:
            if self.read_only:
                g.error("read only")
            g.error("exception deleting backup file:", fileName)
            g.es_exception()
    #@+node:ekr.20100119145629.6108: *4* fc.handleWriteLeoFileException
    def handleWriteLeoFileException(self, fileName: str, backupName: str, f: Any) -> None:
        """Report an exception. f is an open file, or None."""
        # c = self.c
        g.es("exception writing:", fileName)
        g.es_exception()
        if f:
            f.close()
        # Delete fileName.
        if fileName and g.os_path_exists(fileName):
            self.deleteBackupFile(fileName)
        # Rename backupName to fileName.
        if backupName and g.os_path_exists(backupName):
            g.es("restoring", fileName, "from", backupName)
            # No need to create directories when restoring.
            src, dst = backupName, fileName
            try:
                shutil.move(src, dst)
            except Exception:
                g.error('exception renaming', src, 'to', dst)
                g.es_exception()
        else:
            g.error('backup file does not exist!', repr(backupName))
    #@+node:ekr.20040324080359.1: *4* fc.isReadOnly
    def isReadOnly(self, fileName: str) -> bool:
        # self.read_only is not valid for Save As and Save To commands.
        if g.os_path_exists(fileName):
            try:
                if not os.access(fileName, os.W_OK):
                    g.error("can not write: read only:", fileName)
                    return True
            except Exception:
                pass  # os.access() may not exist on all platforms.
        return False
    #@+node:ekr.20031218072017.3045: *4* fc.setDefaultDirectoryForNewFiles
    def setDefaultDirectoryForNewFiles(self, fileName: str) -> None:
        """Set c.openDirectory for new files for the benefit of leoAtFile.scanAllDirectives."""
        c = self.c
        if not c.openDirectory:
            theDir = g.os_path_dirname(fileName)
            if theDir and g.os_path_isabs(theDir) and g.os_path_exists(theDir):
                c.openDirectory = c.frame.openDirectory = theDir
    #@+node:ekr.20031218072017.1554: *4* fc.warnOnReadOnlyFiles
    def warnOnReadOnlyFiles(self, fileName: str) -> None:
        # os.access may not exist on all platforms.
        try:
            self.read_only = not os.access(fileName, os.W_OK)
        except AttributeError:
            self.read_only = False
        except UnicodeError:
            self.read_only = False
        if self.read_only and not g.unitTesting:
            g.error("read only:", fileName)
    #@+node:ekr.20031218072017.3020: *3* fc: Reading
    #@+node:ekr.20031218072017.1559: *4* fc: Paste
    #@+node:ekr.20080410115129.1: *5* fc.checkPaste
    def checkPaste(self, parent: Position, p: Position) -> bool:
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
    #@+node:ekr.20180709205603.1: *5* fc.getLeoOutlineFromClipBoard
    def getLeoOutlineFromClipboard(self, s: str) -> Optional[Position]:
        """Read a Leo outline from string s in clipboard format."""
        c = self.c
        current = c.p
        if not current:
            g.trace('no c.p')
            return None
        self.initReadIvars()

        # Save and clear gnxDict.
        oldGnxDict = self.gnxDict
        self.gnxDict = {}
        if s.lstrip().startswith("{"):
            # Maybe JSON
            hidden_v = FastRead(c, self.gnxDict).readFileFromJsonClipboard(s)
        else:
            # This encoding must match the encoding used in outline_to_clipboard_string.
            s_bytes = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            hidden_v = FastRead(c, self.gnxDict).readFileFromClipboard(s_bytes)
        v = hidden_v.children[0]
        v.parents = []
        if not v:
            g.es("the clipboard is not valid ", color="blue")
            return None

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
    #@+node:ekr.20180709205640.1: *5* fc.getLeoOutlineFromClipBoardRetainingClones
    def getLeoOutlineFromClipboardRetainingClones(self, s: str) -> Optional[Position]:
        """Read a Leo outline from string s in clipboard format."""
        c = self.c
        current = c.p
        if not current:
            g.trace('no c.p')
            return None
        self.initReadIvars()

        # All pasted nodes should already have unique gnx's.
        ni = g.app.nodeIndices
        for v in c.all_unique_nodes():
            ni.check_gnx(c, v.fileIndex, v)

        if s.lstrip().startswith("{"):
            # Maybe JSON
            hidden_v = FastRead(c, self.gnxDict).readFileFromJsonClipboard(s)
        else:
            # This encoding must match the encoding used in outline_to_clipboard_string.
            s_bytes = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            hidden_v = FastRead(c, self.gnxDict).readFileFromClipboard(s_bytes)

        v = hidden_v.children[0]
        v.parents.remove(hidden_v)
        if not v:
            g.es("the clipboard is not valid ", color="blue")
            return None

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

        # Automatically correct any link errors!
        errors = c.checkOutline()
        if errors > 0:
            return None
        c.selectPosition(p)
        self.initReadIvars()
        return p
    #@+node:ekr.20180425034856.1: *5* fc.reassignAllIndices
    def reassignAllIndices(self, p: Position) -> None:
        """Reassign all indices in p's subtree."""
        ni = g.app.nodeIndices
        for p2 in p.self_and_subtree(copy=False):
            v = p2.v
            index = ni.getNewIndex(v)
            if 'gnx' in g.app.debug:
                g.trace('**reassigning**', index, v)
    #@+node:ekr.20060919104836: *4* fc: Read Top-level
    #@+node:ekr.20031218072017.1553: *5* fc.getLeoFile (read switch)
    def getLeoFile(
        self,
        theFile: Any,
        fileName: str,
        readAtFileNodesFlag: bool = True,
        silent: bool = False,
        checkOpenFiles: bool = True,
    ) -> tuple[VNode, float]:
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
            # Read the .leo file and create the outline.
            if fileName.endswith('.db'):
                v = fc.retrieveVnodesFromDb(theFile) or fc.initNewDb(theFile)
            elif fileName.endswith('.leojs'):
                v = FastRead(c, self.gnxDict).readJsonFile(theFile, fileName)
                if v:
                    c.hiddenRootNode = v
            else:
                v = FastRead(c, self.gnxDict).readFile(theFile, fileName)
                if v:
                    c.hiddenRootNode = v
            if v:
                c.setFileTimeStamp(fileName)
                if readAtFileNodesFlag:
                    recoveryNode = fc.readExternalFiles()
        finally:
            # lastTopLevel is a better fallback, imo.
            p = recoveryNode or c.p or c.lastTopLevel()
            c.selectPosition(p)
            # Delay the second redraw until idle time.
            # This causes a slight flash, but corrects a hangnail.
            c.redraw_later()
            c.checkOutline()  # Must be called *after* ni.end_holding.
            c.loading = False  # reenable c.changed
            if not isinstance(theFile, sqlite3.Connection):
                # Fix bug https://bugs.launchpad.net/leo-editor/+bug/1208942
                # Leo holding directory/file handles after file close?
                theFile.close()
        if c.changed:
            fc.propagateDirtyNodes()
        fc.initReadIvars()
        t2 = time.time()
        g.es(f"read outline in {t2 - t1:2.2f} seconds")
        return v, c.frame.ratio
    #@+node:ekr.20031218072017.2297: *5* fc.openLeoFile
    def openLeoFile(self,
        theFile: Any,
        fileName: str,
        readAtFileNodesFlag: bool = True,
        silent: bool = False,
    ) -> VNode:
        """
        Open a Leo file.

        readAtFileNodesFlag: False when reading settings files.
        silent:              True when creating hidden commanders.
        """
        c, frame = self.c, self.c.frame
        # Set c.openDirectory
        theDir = g.os_path_dirname(fileName)
        if theDir:
            c.openDirectory = c.frame.openDirectory = theDir
        # Get the file.
        self.gnxDict = {}  # #1437
        v, ratio = self.getLeoFile(
            theFile, fileName,
            readAtFileNodesFlag=readAtFileNodesFlag,
            silent=silent,
        )
        if v:
            frame.resizePanesToRatio(ratio, frame.secondary_ratio)
        return v
    #@+node:ekr.20120212220616.10537: *5* fc.readExternalFiles & helper
    def readExternalFiles(self) -> Optional[Position]:
        """
        Read all external files in the outline.

        A helper for fc.getLeoFile.
        """
        c, fc = self.c, self
        c.atFileCommands.readAll(c.rootPosition())
        recoveryNode = fc.handleNodeConflicts()
        #
        # Do this after reading external files.
        # The descendent nodes won't exist unless we have read
        # the @thin nodes!
        fc.restoreDescendentAttributes()
        fc.setPositionsFromVnodes()
        return recoveryNode
    #@+node:ekr.20100205060712.8314: *6* fc.handleNodeConflicts
    def handleNodeConflicts(self) -> Optional[Position]:
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
                # 2017/06/19: reverse comparison order.
                d = difflib.Differ().compare(g.splitLines(b1), g.splitLines(b2))
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
    #@+node:ekr.20031218072017.3030: *5* fc.readOutlineOnly
    def readOutlineOnly(self, theFile: Any, fileName: str) -> VNode:
        c = self.c
        # Set c.openDirectory
        theDir = g.os_path_dirname(fileName)
        if theDir:
            c.openDirectory = c.frame.openDirectory = theDir
        v, ratio = self.getLeoFile(theFile, fileName, readAtFileNodesFlag=False)
        c.redraw()
        c.frame.deiconify()
        junk, junk, secondary_ratio = self.frame.initialRatios()
        c.frame.resizePanesToRatio(ratio, secondary_ratio)
        return v
    #@+node:vitalije.20170630152841.1: *5* fc.retrieveVnodesFromDb & helpers
    def retrieveVnodesFromDb(self, conn: Any) -> VNode:
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

        def findNode(x: VNode) -> VNode:
            return fc.gnxDict.get(x, c.hiddenRootNode)  # type:ignore

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
    def initNewDb(self, conn: Any) -> VNode:
        """ Initializes tables and returns None"""
        c, fc = self.c, self
        v = leoNodes.VNode(context=c)
        c.hiddenRootNode.children = [v]
        (w, h, x, y, r1, r2, encp) = fc.getWindowGeometryFromDb(conn)
        c.frame.setTopGeometry(w, h, x, y)
        c.frame.resizePanesToRatio(r1, r2)
        c.sqlite_connection = conn
        fc.exportToSqlite(c.mFileName)
        return v
    #@+node:vitalije.20170630200802.1: *6* fc.getWindowGeometryFromDb
    def getWindowGeometryFromDb(self, conn: Any) -> tuple:
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
            # mypy complained that geom must be a tuple, not a generator.
            geom = tuple(d.get(*x) for x in zip(keys, geom))  # type:ignore
        except sqlite3.OperationalError:
            pass
        return geom
    #@+node:ekr.20060919133249: *4* fc: Read Utils
    # Methods common to both the sax and non-sax code.
    #@+node:ekr.20061006104837.1: *5* fc.archivedPositionToPosition
    def archivedPositionToPosition(self, s: str) -> Position:
        """Convert an archived position (a string) to a position."""
        return self.c.archivedPositionToPosition(s)
    #@+node:ekr.20040701065235.1: *5* fc.getDescendentAttributes
    def getDescendentAttributes(self, s: str, tag: str = "") -> list[str]:
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

    def getDescendentUnknownAttributes(self, s: str, v: VNode = None) -> Any:
        """Unhexlify and unpickle t/v.descendentUnknownAttribute field."""
        try:
            # Changed in version 3.2: Accept only bytestring or bytearray objects as input.
            s_bytes = g.toEncodedString(s)  # 2011/02/22
            # Throws a TypeError if val is not a hex string.
            bin = binascii.unhexlify(s_bytes)
            val = pickle.loads(bin)
            return val
        except Exception:
            g.es_exception()
            g.trace('Can not unpickle', s.__class__.__name__, v and v.h, s[:40])
            return None
    #@+node:vitalije.20180304190953.1: *5* fc.getPos/VnodeFromClipboard
    def getPosFromClipboard(self, s: str) -> Position:
        """A utility called from init_tree_abbrev."""
        v = self.getVnodeFromClipboard(s)
        return leoNodes.Position(v)

    def getVnodeFromClipboard(self, s: str) -> Optional[VNode]:
        """Called only from getPosFromClipboard."""
        c = self.c
        self.initReadIvars()
        oldGnxDict = self.gnxDict
        self.gnxDict = {}  # Fix #943
        try:
            # This encoding must match the encoding used in outline_to_clipboard_string.
            s_bytes = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            v = FastRead(c, {}).readFileFromClipboard(s_bytes)
            if not v:
                g.es("the clipboard is not valid ", color="blue")
                return None
        finally:
            self.gnxDict = oldGnxDict
        return v
    #@+node:ekr.20060919142200.1: *5* fc.initReadIvars
    def initReadIvars(self) -> None:
        self.descendentTnodeUaDictList = []
        self.descendentVnodeUaDictList = []
        self.descendentExpandedList = []
        # 2011/12/10: never re-init this dict.
        # self.gnxDict = {}
        self.descendentMarksList = []
        self.c.nodeConflictList = []  # 2010/01/05
        self.c.nodeConflictFileName = None  # 2010/01/05
    #@+node:ekr.20100124110832.6212: *5* fc.propagateDirtyNodes
    def propagateDirtyNodes(self) -> None:
        c = self.c
        aList = [z for z in c.all_positions() if z.isDirty()]
        for p in aList:
            p.setAllAncestorAtFileNodesDirty()
    #@+node:ekr.20080805132422.3: *5* fc.resolveArchivedPosition
    def resolveArchivedPosition(self, archivedPosition: Any, root_v: Any) -> Optional[VNode]:
        """
        Return a VNode corresponding to the archived position relative to root
        node root_v.
        """

        def oops(message: str) -> None:
            """Raise an exception during unit tests."""
            if g.unitTesting:
                raise AssertionError(message)
        try:
            aList = [int(z) for z in archivedPosition.split('.')]
            aList.reverse()
        except Exception:
            oops(f"Unexpected exception: {archivedPosition!r}")
            return None
        if not aList:
            oops('empty')
            return None
        last_v = root_v
        n = aList.pop()
        if n < 0:
            oops(f"Negative root index: {n!r}: {archivedPosition}")
            return None
        while aList:
            n = aList.pop()
            children = last_v.children
            if n < len(children):
                last_v = children[n]
            else:
                oops(f"bad index={n!r}, len(children)={len(children)}")
                return None
        return last_v
    #@+node:EKR.20040627120120: *5* fc.restoreDescendentAttributes
    def restoreDescendentAttributes(self) -> None:
        """Called from fc.readExternalFiles."""
        c = self.c
        for resultDict in self.descendentTnodeUaDictList:
            for gnx in resultDict:
                v = self.gnxDict.get(gnx)
                if v:
                    v.unknownAttributes = resultDict[gnx]
                    v._p_changed = True
        # New in Leo 4.5: keys are archivedPositions, values are attributes.
        for root_v, resultDict in self.descendentVnodeUaDictList:
            for key in resultDict:
                v = self.resolveArchivedPosition(key, root_v)
                if v:
                    v.unknownAttributes = resultDict[key]
                    v._p_changed = True
        expanded, marks = {}, {}
        for gnx in self.descendentExpandedList:
            v = self.gnxDict.get(gnx)
            if v:
                expanded[v] = v
        for gnx in self.descendentMarksList:
            v = self.gnxDict.get(gnx)
            if v:
                marks[v] = v
        if marks or expanded:
            for p in c.all_unique_positions():
                if marks.get(p.v):
                    # This was the problem: was p.setMark.
                    # There was a big performance bug in the mark hook in the Node Navigator plugin.
                    p.v.initMarkedBit()
                if expanded.get(p.v):
                    p.expand()
    #@+node:ekr.20060919110638.13: *5* fc.setPositionsFromVnodes
    def setPositionsFromVnodes(self) -> None:

        c, root = self.c, self.c.rootPosition()
        if c.sqlite_connection:
            # position is already selected
            return
        current, str_pos = None, None
        if c.mFileName:
            str_pos = c.db.get('current_position')
        if str_pos is None:
            d = root.v.u
            if d:
                str_pos = d.get('str_leo_pos')
        if str_pos is not None:
            current = self.archivedPositionToPosition(str_pos)
        c.setCurrentPosition(current or c.rootPosition())
    #@+node:ekr.20031218072017.3032: *3* fc: Writing
    #@+node:ekr.20070413045221.2: *4* fc: Writing save*
    #@+node:ekr.20031218072017.1720: *5* fc.save
    def save(self, fileName: str, silent: bool = False) -> bool:
        """fc.save: A helper for c.save."""
        c = self.c
        p = c.p
        # New in 4.2.  Return ok flag so shutdown logic knows if all went well.
        ok = g.doHook("save1", c=c, p=p, fileName=fileName)
        if ok is None:
            c.endEditing()  # Set the current headline text.
            self.setDefaultDirectoryForNewFiles(fileName)
            g.app.commander_cacher.save(c, fileName)
            ok = c.checkFileTimeStamp(fileName)
            if ok:
                if c.sqlite_connection:
                    c.sqlite_connection.close()
                    c.sqlite_connection = None
                ok = self.write_Leo_file(fileName)
            if ok:
                if not silent:
                    self.putSavedMessage(fileName)
                c.clearChanged()  # Clears all dirty bits.
                if c.config.getBool('save-clears-undo-buffer'):
                    g.es("clearing undo")
                    c.undoer.clearUndoState()
        g.doHook("save2", c=c, p=p, fileName=fileName)
        return ok
    #@+node:ekr.20031218072017.3043: *5* fc.saveAs
    def saveAs(self, fileName: str) -> None:
        """fc.saveAs: A helper for c.saveAs."""
        c = self.c
        p = c.p
        if not g.doHook("save1", c=c, p=p, fileName=fileName):
            c.endEditing()  # Set the current headline text.
            if c.sqlite_connection:
                c.sqlite_connection.close()
                c.sqlite_connection = None
            self.setDefaultDirectoryForNewFiles(fileName)
            g.app.commander_cacher.save(c, fileName)
            # Disable path-changed messages in writeAllHelper.
            c.ignoreChangedPaths = True
            try:
                if self.write_Leo_file(fileName):
                    c.clearChanged()  # Clears all dirty bits.
                    self.putSavedMessage(fileName)
            finally:
                c.ignoreChangedPaths = False  # #1367.
        g.doHook("save2", c=c, p=p, fileName=fileName)
    #@+node:ekr.20031218072017.3044: *5* fc.saveTo
    def saveTo(self, fileName: str, silent: bool = False) -> None:
        """fc.saveTo: A helper for c.saveTo."""
        c = self.c
        p = c.p
        if not g.doHook("save1", c=c, p=p, fileName=fileName):
            c.endEditing()  # Set the current headline text.
            if c.sqlite_connection:
                c.sqlite_connection.close()
                c.sqlite_connection = None
            self.setDefaultDirectoryForNewFiles(fileName)
            g.app.commander_cacher.commit()  # Commit, but don't save file name.
            # Disable path-changed messages in writeAllHelper.
            c.ignoreChangedPaths = True
            try:
                self.write_Leo_file(fileName)
            finally:
                c.ignoreChangedPaths = False
            if not silent:
                self.putSavedMessage(fileName)
        g.doHook("save2", c=c, p=p, fileName=fileName)
    #@+node:ekr.20210316034237.1: *4* fc: Writing top-level
    #@+node:vitalije.20170630172118.1: *5* fc.exportToSqlite & helpers
    def exportToSqlite(self, fileName: str) -> bool:
        """Dump all vnodes to sqlite database. Returns True on success."""
        c, fc = self.c, self
        if c.sqlite_connection is None:
            c.sqlite_connection = sqlite3.connect(fileName, isolation_level='DEFERRED')
        conn = c.sqlite_connection

        def dump_u(v: VNode) -> bytes:
            try:
                s = pickle.dumps(v.u, protocol=1)
            except pickle.PicklingError:
                s = b''  # 2021/06/25: fixed via mypy complaint.
                g.trace('unpickleable value', repr(v.u))
            return s

        def dbrow(v: VNode) -> tuple:
            return (
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
            conn.close()
            c.sqlite_connection = None
            ok = True
        except sqlite3.Error as e:
            g.internalError(e)
        return ok
    #@+node:vitalije.20170705075107.1: *6* fc.decodePosition
    def decodePosition(self, s: str) -> Position:
        """Creates position from its string representation encoded by fc.encodePosition."""
        fc = self
        if not s:
            return fc.c.rootPosition()
        sep = '<->'
        comma = ','
        stack1 = [x.split(comma) for x in s.split(sep)]
        stack = [(fc.gnxDict[x], int(y)) for x, y in stack1]
        v, ci = stack[-1]
        p = leoNodes.Position(v, ci, stack[:-1])
        return p
    #@+node:vitalije.20170705075117.1: *6* fc.encodePosition
    def encodePosition(self, p: Position) -> str:
        """New schema for encoding current position hopefully simpler one."""
        jn = '<->'
        mk = '%s,%s'
        res = [mk % (x.gnx, y) for x, y in p.stack]
        res.append(mk % (p.gnx, p._childIndex))
        return jn.join(res)
    #@+node:vitalije.20170811130512.1: *6* fc.prepareDbTables
    def prepareDbTables(self, conn: Any) -> None:
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
    def exportVnodesToSqlite(self, conn: Any, rows: Any) -> None:
        conn.executemany(
            '''insert into vnodes
            (gnx, head, body, children, parents,
                iconVal, statusBits, ua)
            values(?,?,?,?,?,?,?,?);''',
            rows,
        )
    #@+node:vitalije.20170701162052.1: *6* fc.exportGeomToSqlite
    def exportGeomToSqlite(self, conn: Any) -> None:
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
    def exportDbVersion(self, conn: Any) -> None:
        conn.execute(
            "replace into extra_infos(name, value) values('dbversion', ?)", ('1.0',))
    #@+node:vitalije.20170701162204.1: *6* fc.exportHashesToSqlite
    def exportHashesToSqlite(self, conn: Any) -> None:
        c = self.c

        def md5(x: str) -> str:
            try:
                s = open(x, 'rb').read()
            except Exception:
                return ''
            s = s.replace(b'\r\n', b'\n')
            return hashlib.md5(s).hexdigest()  # A string

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
    #@+node:ekr.20031218072017.1573: *5* fc.outline_to_clipboard_string
    def outline_to_clipboard_string(self, p: Position = None) -> str:
        """
        Return a string suitable for pasting to the clipboard.
        """
        # Save
        tua = self.descendentTnodeUaDictList
        vua = self.descendentVnodeUaDictList
        gnxDict = self.gnxDict
        vnodesDict = self.vnodesDict
        try:
            self.usingClipboard = True
            if self.c.config.getBool('json-outline-clipboard', default=False):
                d = self.leojs_outline_dict(p or self.c.p)
                s = json.dumps(d, indent=2, cls=SetJSONEncoder)
            else:
                self.outputFile = io.StringIO()
                self.putProlog()
                self.putHeader()
                self.put_v_elements(p or self.c.p)
                self.put_t_elements()
                self.putPostlog()
                s = self.outputFile.getvalue()
                self.outputFile = None
        finally:  # Restore
            self.descendentTnodeUaDictList = tua
            self.descendentVnodeUaDictList = vua
            self.gnxDict = gnxDict
            self.vnodesDict = vnodesDict
            self.usingClipboard = False
        return s
    #@+node:felix.20230326001957.1: *5* fc.outline_to_clipboard_json_string
    def outline_to_clipboard_json_string(self, p: Position = None) -> str:
        """
        Return a JSON string suitable for pasting to the clipboard.
        """
        # Save
        tua = self.descendentTnodeUaDictList
        vua = self.descendentVnodeUaDictList
        gnxDict = self.gnxDict
        vnodesDict = self.vnodesDict
        try:
            self.usingClipboard = True
            d = self.leojs_outline_dict(p or self.c.p)  # Checks for illegal ua's
            s = json.dumps(d, indent=2, cls=SetJSONEncoder)
        finally:  # Restore
            self.descendentTnodeUaDictList = tua
            self.descendentVnodeUaDictList = vua
            self.gnxDict = gnxDict
            self.vnodesDict = vnodesDict
            self.usingClipboard = False
        return s
    #@+node:ekr.20040324080819.1: *5* fc.outline_to_xml_string
    def outline_to_xml_string(self) -> str:
        """Write the outline in .leo (XML) format to a string."""
        self.outputFile = io.StringIO()
        self.putProlog()
        self.putHeader()
        self.putGlobals()
        self.putPrefs()
        self.putFindSettings()
        self.put_v_elements()
        self.put_t_elements()
        self.putPostlog()
        s = self.outputFile.getvalue()
        self.outputFile = None
        return s
    #@+node:ekr.20031218072017.3046: *5* fc.write_Leo_file
    def write_Leo_file(self, fileName: str) -> bool:
        """Write all external files and the .leo file itself."""
        c, fc = self.c, self
        g.app.recentFilesManager.writeRecentFilesFile(c)
        fc.writeAllAtFileNodes()
        return fc.writeOutline(fileName)  # Calls c.checkOutline.

    write_LEO_file = write_Leo_file  # For compatibility with old plugins.
    #@+node:ekr.20210316050301.1: *5* fc.write_leojs & helpers
    def write_leojs(self, fileName: str) -> bool:
        """Write the outline in .leojs (JSON) format."""
        c = self.c
        ok, backupName = self.createBackupFile(fileName)
        if not ok:
            return False
        try:
            f = open(fileName, 'wb')  # Must write bytes.
        except Exception:
            g.es(f"can not open {fileName}")
            g.es_exception()
            return False
        try:
            # Create the dict corresponding to the JSON.
            d = self.leojs_outline_dict()  # Checks for illegal ua's
            # Convert the dict to JSON.
            json_s = json.dumps(d, indent=2, cls=SetJSONEncoder)
            # Write bytes.
            f.write(bytes(json_s, self.leo_file_encoding, 'replace'))
            f.close()
            g.app.commander_cacher.save(c, fileName)
            c.setFileTimeStamp(fileName)
            # Delete backup file.
            if backupName and g.os_path_exists(backupName):
                self.deleteBackupFile(backupName)
            self.mFileName = fileName
            return True
        except Exception:
            self.handleWriteLeoFileException(fileName, backupName, f)
            return False
    #@+node:ekr.20210316095706.1: *6* fc.leojs_outline_dict
    def leojs_outline_dict(self, p: Position = None) -> dict[str, Any]:
        """Return a dict representing the outline."""
        c = self.c
        uas = {}
        # holds all gnx found so far, to exclude adding headlines of already defined gnx.
        gnxSet: set[str] = set()
        if self.usingClipboard:  # write the currently selected subtree ONLY.
            # Node to be root of tree to be put on clipboard
            sp = p or c.p  # Selected Position: sp
            # build uas dict
            for p in sp.self_and_subtree():
                if hasattr(p.v, 'unknownAttributes') and len(p.v.unknownAttributes.keys()):
                    try:
                        json.dumps(p.v.unknownAttributes, skipkeys=True, cls=SetJSONEncoder)  # If this test passes ok
                        uas[p.v.gnx] = p.v.unknownAttributes  # Valid UA's as-is. UA's are NOT encoded.
                    except TypeError:
                        g.trace(f"Can not serialize uA for {p.h}", g.callers(6))
                        g.printObj(p.v.unknownAttributes)

            # result for specific starting p
            result = {
                    'leoHeader': {'fileFormat': 2},
                    'vnodes': [
                        self.leojs_vnode(sp, gnxSet)
                    ],
                    'tnodes': {p.v.gnx: p.v._bodyString for p in sp.self_and_subtree() if p.v._bodyString}
                }

        else:  # write everything from the top node 'c.rootPosition()'
            # build uas dict
            for v in c.all_unique_nodes():
                if hasattr(v, 'unknownAttributes') and len(v.unknownAttributes.keys()):
                    try:
                        # If this passes, the (unencoded) uAs are valid json.
                        json.dumps(v.unknownAttributes, skipkeys=True, cls=SetJSONEncoder)
                        uas[v.gnx] = v.unknownAttributes
                    except TypeError:
                        g.trace(f"Can not serialize uA for {v.h}", g.callers(6))
                        g.printObj(v.unknownAttributes)

            # result for whole outline
            result = {
                    'leoHeader': {'fileFormat': 2},
                    'vnodes': [
                        self.leojs_vnode(p, gnxSet) for p in c.rootPosition().self_and_siblings()
                    ],
                    'tnodes': {
                        v.gnx: v._bodyString for v in c.all_unique_nodes() if (v._bodyString and v.isWriteBit())
                    }
                }
        self.leojs_globals()  # Call only to set db like non-json save file.
        # uas could be empty. Only add it if needed
        if uas:
            result["uas"] = uas

        if not self.usingClipboard:
            self.currentPosition = p or c.p
            self.setCachedBits()
        return result
    #@+node:ekr.20210316092313.1: *6* fc.leojs_globals (sets window_position)
    def leojs_globals(self) -> Optional[dict[str, Any]]:
        """Put json representation of Leo's cached globals."""
        c = self.c
        width, height, left, top = c.frame.get_window_info()
        if 1:  # Write to the cache, not the file.
            d = None
            c.db['body_outline_ratio'] = str(c.frame.ratio)
            c.db['body_secondary_ratio'] = str(c.frame.secondary_ratio)
            c.db['window_position'] = str(top), str(left), str(height), str(width)
            if 'size' in g.app.debug:
                g.trace('set window_position:', c.db['window_position'], c.shortFileName())
        else:
            d = {
                'body_outline_ratio': c.frame.ratio,
                'body_secondary_ratio': c.frame.secondary_ratio,
                'globalWindowPosition': {
                    'top': top,
                    'left': left,
                    'width': width,
                    'height': height,
                },
            }
        return d
    #@+node:ekr.20210316085413.2: *6* fc.leojs_vnodes
    def leojs_vnode(self, p: Position, gnxSet: Any, isIgnore: bool = False) -> dict[str, Any]:
        """Return a jsonized vnode."""
        c = self.c
        fc = self
        v = p.v
        # Precompute constants.
        # Write the entire @edit tree if it has children.
        isAuto = p.isAtAutoNode() and p.atAutoNodeName().strip()
        isEdit = p.isAtEditNode() and p.atEditNodeName().strip() and not p.hasChildren()
        isFile = p.isAtFileNode()
        isShadow = p.isAtShadowFileNode()
        isThin = p.isAtThinFileNode()
        # Set forceWrite.
        if isIgnore or p.isAtIgnoreNode():
            forceWrite = True
        elif isAuto or isEdit or isFile or isShadow or isThin:
            forceWrite = False
        else:
            forceWrite = True
        # Set the write bit if necessary.
        if forceWrite or self.usingClipboard:
            v.setWriteBit()  # 4.2: Indicate we wrote the body text.

        status = 0
        if v.isMarked():
            status |= v.markedBit
        if p.isExpanded():
            status |= v.expandedBit
        if p == c.p:
            status |= v.selectedBit

        children: list[dict[str, Any]] = []  # Start empty

        if p.hasChildren() and (forceWrite or self.usingClipboard):
            # This optimization eliminates all "recursive" copies.
            p.moveToFirstChild()
            while 1:
                children.append(fc.leojs_vnode(p, gnxSet, isIgnore))
                if p.hasNext():
                    p.moveToNext()
                else:
                    break
            p.moveToParent()  # Restore p in the caller.

        # At least will contain  the gnx
        result: dict[str, Any] = {
            'gnx': v.fileIndex,
        }

        if v.fileIndex not in gnxSet:
            result['vh'] = v._headString  # Not a clone so far so add his headline text
            gnxSet.add(v.fileIndex)
            if children:
                result['children'] = children

        # Else, just add status if needed
        if status:
            result['status'] = status

        return result
    #@+node:ekr.20100119145629.6111: *5* fc.write_xml_file
    def write_xml_file(self, fileName: str) -> bool:
        """Write the outline in .leo (XML) format."""
        c = self.c
        ok, backupName = self.createBackupFile(fileName)
        if not ok:
            return False
        try:
            f = open(fileName, 'wb')  # Must write bytes.
        except Exception:
            g.es(f"can not open {fileName}")
            return False
        self.mFileName = fileName
        try:
            s = self.outline_to_xml_string()
            # Write bytes.
            f.write(bytes(s, self.leo_file_encoding, 'replace'))
            f.close()
            c.setFileTimeStamp(fileName)
            # Delete backup file.
            if backupName and g.os_path_exists(backupName):
                self.deleteBackupFile(backupName)
            return True
        except Exception:
            self.handleWriteLeoFileException(fileName, backupName, f)
            return False
    #@+node:ekr.20100119145629.6114: *5* fc.writeAllAtFileNodes
    def writeAllAtFileNodes(self) -> bool:
        """Write all @<file> nodes and set orphan bits."""
        c = self.c
        try:
            # To allow Leo to quit properly, do *not* signal failure here.
            c.atFileCommands.writeAll(all=False)
            return True
        except Exception:
            # #1260415: https://bugs.launchpad.net/leo-editor/+bug/1260415
            g.es_error("exception writing external files")
            g.es_exception()
            g.es('Internal error writing one or more external files.', color='red')
            g.es('Please report this error to:', color='blue')
            g.es('https://groups.google.com/forum/#!forum/leo-editor', color='blue')
            g.es('All changes will be lost unless you', color='red')
            g.es('can save each changed file.', color='red')
            return False
    #@+node:ekr.20210316041806.1: *5* fc.writeOutline (write switch)
    def writeOutline(self, fileName: str) -> bool:

        c = self.c
        errors = c.checkOutline()
        if errors:
            g.error('Structure errors in outline! outline not written')
            return False
        if self.isReadOnly(fileName):
            return False
        if fileName.endswith('.db'):
            return self.exportToSqlite(fileName)
        if fileName.endswith('.leojs'):
            return self.write_leojs(fileName)
        return self.write_xml_file(fileName)
    #@+node:ekr.20070412095520: *5* fc.writeZipFile
    def writeZipFile(self, s: str) -> None:
        """Write string s as a .zip file."""
        # The name of the file in the archive.
        contentsName = g.toEncodedString(
            g.shortFileName(self.mFileName),
            self.leo_file_encoding, reportErrors=True)
        # The name of the archive itself.
        fileName = g.toEncodedString(
            self.mFileName,
            self.leo_file_encoding, reportErrors=True)
        # Write the archive.
        # These mypy complaints look valid.
        theFile = zipfile.ZipFile(fileName, 'w', zipfile.ZIP_DEFLATED)  # type:ignore
        theFile.writestr(contentsName, s)  # type:ignore
        theFile.close()
    #@+node:ekr.20210316034532.1: *4* fc.Writing Utils
    #@+node:ekr.20080805085257.2: *5* fc.pickle
    def pickle(self, torv: Any, val: Any, tag: str) -> str:
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
    #@+node:ekr.20031218072017.1470: *5* fc.put
    def put(self, s: str) -> None:
        """Put string s to self.outputFile. All output eventually comes here."""
        if s:
            self.outputFile.write(s)
    #@+node:ekr.20080805071954.2: *5* fc.putDescendentVnodeUas & helper
    def putDescendentVnodeUas(self, p: Position) -> str:
        """
        Return the a uA field for descendent VNode attributes,
        suitable for reconstituting uA's for anonymous vnodes.
        """
        # z
        # Create aList of tuples (p,v) having a valid unknownAttributes dict.
        # Create dictionary: keys are vnodes, values are corresponding archived positions.
        aList = []
        pDict = {}
        for p2 in p.self_and_subtree(copy=False):
            if hasattr(p2.v, "unknownAttributes"):
                aList.append((p2.copy(), p2.v),)
                pDict[p2.v] = p2.archivedPosition(root_p=p)
        # Create aList of pairs (v,d) where d contains only pickleable entries.
        if aList:
            aList = self.createUaList(aList)
        if not aList:
            return ''
        # Create d, an enclosing dict to hold all the inner dicts.
        d = {}
        for v, d2 in aList:
            aList2 = [str(z) for z in pDict.get(v)]
            key = '.'.join(aList2)
            d[key] = d2
        # Pickle and hexlify d
        if not d:
            return ''
        return self.pickle(torv=p.v, val=d, tag='descendentVnodeUnknownAttributes')
    #@+node:ekr.20080805085257.1: *6* fc.createUaList
    def createUaList(self, aList: list) -> list[tuple[Any, dict]]:
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
    #@+node:ekr.20031218072017.3035: *5* fc.putFindSettings
    def putFindSettings(self) -> None:
        # New in 4.3:  These settings never get written to the .leo file.
        self.put("<find_panel_settings/>\n")
    #@+node:ekr.20031218072017.3037: *5* fc.putGlobals (sets window_position)
    def putGlobals(self) -> None:
        """Put a vestigial <globals> element, and write global data to the cache."""
        trace = 'cache' in g.app.debug
        c = self.c
        self.put("<globals/>\n")
        if not c.mFileName:
            return
        c.db['body_outline_ratio'] = str(c.frame.ratio)
        c.db['body_secondary_ratio'] = str(c.frame.secondary_ratio)
        w, h, left, t = c.frame.get_window_info()
        c.db['window_position'] = str(t), str(left), str(h), str(w)
        if trace:
            g.trace(f"\nset c.db for {c.shortFileName()}")
            print('window_position:', c.db['window_position'])
    #@+node:ekr.20031218072017.3041: *5* fc.putHeader
    def putHeader(self) -> None:
        self.put('<leo_header file_format="2"/>\n')
    #@+node:ekr.20031218072017.3042: *5* fc.putPostlog
    def putPostlog(self) -> None:
        self.put("</leo_file>\n")
    #@+node:ekr.20031218072017.2066: *5* fc.putPrefs
    def putPrefs(self) -> None:
        # New in 4.3:  These settings never get written to the .leo file.
        self.put("<preferences/>\n")
    #@+node:ekr.20031218072017.1246: *5* fc.putProlog
    def putProlog(self) -> None:
        """
        Put the prolog of the xml file.
        """
        tag = 'http://leo-editor.github.io/leo-editor/namespaces/leo-python-editor/1.1'
        self.putXMLLine()
        # Put "created by Leo" line.
        self.put('<!-- Created by Leo: https://leo-editor.github.io/leo-editor/leo_toc.html -->\n')
        self.putStyleSheetLine()
        # Put the namespace
        self.put(f'<leo_file xmlns:leo="{tag}" >\n')
    #@+node:ekr.20070413061552: *5* fc.putSavedMessage
    def putSavedMessage(self, fileName: str) -> None:
        c = self.c
        # #531: Optionally report timestamp...
        if c.config.getBool('log-show-save-time', default=False):
            format = c.config.getString('log-timestamp-format') or "%H:%M:%S"
            timestamp = time.strftime(format) + ' '
        else:
            timestamp = ''
        g.es(f"{timestamp}saved: {g.shortFileName(fileName)}")
    #@+node:ekr.20031218072017.1248: *5* fc.putStyleSheetLine
    def putStyleSheetLine(self) -> None:
        """
        Put the xml stylesheet line.

        Leo 5.3:
        - Use only the stylesheet setting, ignoring c.frame.stylesheet.
        - Write no stylesheet element if there is no setting.

        The old way made it almost impossible to delete stylesheet element.
        """
        c = self.c
        sheet = (c.config.getString('stylesheet') or '').strip()
        # sheet2 = c.frame.stylesheet and c.frame.stylesheet.strip() or ''
        # sheet = sheet or sheet2
        if sheet:
            self.put(f"<?xml-stylesheet {sheet} ?>\n")

    #@+node:ekr.20031218072017.1577: *5* fc.put_t_element
    def put_t_element(self, v: VNode) -> None:
        b, gnx = v.b, v.fileIndex
        ua = self.putUnknownAttributes(v)
        body = xml.sax.saxutils.escape(b) if b else ''
        self.put(f'<t tx="{gnx}"{ua}>{body}</t>\n')
    #@+node:ekr.20031218072017.1575: *5* fc.put_t_elements
    def put_t_elements(self) -> None:
        """Put all <t> elements as required for copy or save commands"""
        self.put("<tnodes>\n")
        self.putReferencedTElements()
        self.put("</tnodes>\n")
    #@+node:ekr.20031218072017.1576: *6* fc.putReferencedTElements
    def putReferencedTElements(self) -> None:
        """Put <t> elements for all referenced vnodes."""
        c = self.c
        if self.usingClipboard:  # write the current tree.
            theIter = self.currentPosition.self_and_subtree(copy=False)
        else:  # write everything
            theIter = c.all_unique_positions(copy=False)
        # Populate the vnodes dict.
        vnodes = {}
        for p in theIter:
            # Make *sure* the file index has the proper form.
            # pylint: disable=unbalanced-tuple-unpacking
            index = p.v.fileIndex
            vnodes[index] = p.v
        # Put all vnodes in index order.
        for index in sorted(vnodes):
            v = vnodes.get(index)
            if v:
                # Write <t> elements only for vnodes that will be written.
                # For example, vnodes in external files will be written
                #              only if the vnodes are cloned outside the file.
                if v.isWriteBit():
                    self.put_t_element(v)
            else:
                g.trace('can not happen: no VNode for', repr(index))
                # This prevents the file from being written.
                raise BadLeoFile(f"no VNode for {repr(index)}")
    #@+node:ekr.20050418161620.2: *5* fc.putUaHelper
    def putUaHelper(self, torv: Any, key: str, val: Any) -> str:
        """Put attribute whose name is key and value is val to the output stream."""
        # New in 4.3: leave string attributes starting with 'str_' alone.
        if key.startswith('str_'):
            if isinstance(val, (str, bytes)):
                val = g.toUnicode(val)
                attr = f' {key}={xml.sax.saxutils.quoteattr(val)}'
                return attr
            g.trace(type(val), repr(val))
            g.warning("ignoring non-string attribute", key, "in", torv)
            return ''
        # Support JSON encoded attributes
        if key.startswith('json_'):
            try:
                val = json.dumps(val, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
            except TypeError:
                # fall back to pickle
                g.trace(type(val), repr(val))
                g.warning("pickling JSON incompatible attribute", key, "in", torv)
            else:
                attr = f' {key}={xml.sax.saxutils.quoteattr(val)}'
                return attr
        return self.pickle(torv=torv, val=val, tag=key)
    #@+node:EKR.20040526202501: *5* fc.putUnknownAttributes
    def putUnknownAttributes(self, v: VNode) -> str:
        """Put pickleable values for all keys in v.unknownAttributes dictionary."""
        if not hasattr(v, 'unknownAttributes'):
            return ''
        attrDict = v.unknownAttributes
        if isinstance(attrDict, dict):
            val = ''.join(
                [self.putUaHelper(v, key, val)
                    for key, val in sorted(attrDict.items())])
            return val
        g.warning("ignoring non-dictionary unknownAttributes for", v)
        return ''
    #@+node:ekr.20031218072017.1863: *5* fc.put_v_element & helper
    def put_v_element(self, p: Position, isIgnore: bool = False) -> None:
        """Write a <v> element corresponding to a VNode."""
        fc = self
        v = p.v
        # Precompute constants.
        # Write the entire @edit tree if it has children.
        isAuto = p.isAtAutoNode() and p.atAutoNodeName().strip()
        isEdit = p.isAtEditNode() and p.atEditNodeName().strip() and not p.hasChildren()
        isFile = p.isAtFileNode()
        isShadow = p.isAtShadowFileNode()
        isThin = p.isAtThinFileNode()
        # Set forcewrite.
        if isIgnore or p.isAtIgnoreNode():
            forceWrite = True
        elif isAuto or isEdit or isFile or isShadow or isThin:
            forceWrite = False
        else:
            forceWrite = True
        # Set the write bit if necessary.
        gnx = v.fileIndex
        if forceWrite or self.usingClipboard:
            v.setWriteBit()  # 4.2: Indicate we wrote the body text.

        attrs = fc.compute_attribute_bits(forceWrite, p)
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
                    fc.put_v_element(p, isIgnore)
                    if p.hasNext():
                        p.moveToNext()
                    else:
                        break
                p.moveToParent()  # Restore p in the caller.
                fc.put('</v>\n')
            else:
                fc.put(f"{v_head}</v>\n")  # Call put only once.
    #@+node:ekr.20031218072017.1865: *6* fc.compute_attribute_bits
    def compute_attribute_bits(self, forceWrite: Any, p: Position) -> str:
        """Return the initial values of v's attributes."""
        attrs = []
        if p.hasChildren() and not forceWrite and not self.usingClipboard:
            # Fix #526: do this for @auto nodes as well.
            attrs.append(self.putDescendentVnodeUas(p))
        return ''.join(attrs)
    #@+node:ekr.20031218072017.1579: *5* fc.put_v_elements & helper
    def put_v_elements(self, p: Position = None) -> None:
        """Puts all <v> elements in the order in which they appear in the outline."""
        c = self.c
        c.clearAllVisited()
        self.put("<vnodes>\n")
        # Make only one copy for all calls.
        self.currentPosition = p or c.p
        self.rootPosition = c.rootPosition()
        self.vnodesDict = {}
        if self.usingClipboard:
            self.put_v_element(self.currentPosition)  # Write only current tree.
        else:
            for p in c.rootPosition().self_and_siblings():
                self.put_v_element(p, isIgnore=p.isAtIgnoreNode())
            # #1018: scan *all* nodes.
            self.setCachedBits()
        self.put("</vnodes>\n")
    #@+node:ekr.20190328160622.1: *6* fc.setCachedBits
    def setCachedBits(self) -> None:
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
    def putXMLLine(self) -> None:
        """Put the **properly encoded** <?xml> element."""
        # Use self.leo_file_encoding encoding.
        self.put(
            f"{g.app.prolog_prefix_string}"
            f'"{self.leo_file_encoding}"'
            f"{g.app.prolog_postfix_string}\n")
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

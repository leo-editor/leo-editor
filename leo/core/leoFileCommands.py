#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3018: * @file leoFileCommands.py
'''Classes relating to reading and writing .leo files.'''
#@+<< imports >>
#@+node:ekr.20050405141130: ** << imports >> (leoFileCommands)
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes
import binascii
import difflib
import time
if g.isPython3:
    import io # Python 3.x
    StringIO = io.StringIO
    BytesIO = io.BytesIO
else:
    import cStringIO # Python 2.x
    StringIO = cStringIO.StringIO
import os
import pickle
import string
import sys
import tempfile
import zipfile
try:
    # IronPython has problems with this.
    import xml.sax
    import xml.sax.saxutils
except Exception:
    pass
import sqlite3
import hashlib
from contextlib import contextmanager
PRIVAREA = '---begin-private-area---'
#@-<< imports >>
#@+others
#@+node:ekr.20060918164811: ** Exception classes
class BadLeoFile(Exception):

    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message) # Init the base class.

    def __str__(self):
        return "Bad Leo File:" + self.message

class InvalidPaste(Exception):
    pass
#@+node:ekr.20060919110638.19: ** class SaxContentHandler (XMLGenerator)
if sys.platform != 'cli':

    class SaxContentHandler(xml.sax.saxutils.XMLGenerator):
        '''A sax content handler class that reads Leo files.'''
        #@+others
        #@+node:ekr.20060919110638.20: *3*  sax.__init__ & helpers
        def __init__(self, c, fileName, silent, inClipboard):
            '''Ctor for SaxContentHandler class.'''
            self.c = c
            self.fileName = fileName
            self.silent = silent
            self.inClipboard = inClipboard
            out = sys.stdout if sys.stdout else g.fileLikeObject()
                # Fix the exceedingly strange problem with Python 3.x and pythonw.exe.
                # The sax ctor throws an exception in Python 3.x if sys.stdout is None.
                # The workaround is use a disposable output stream in that case.
            xml.sax.saxutils.XMLGenerator.__init__(self, out=out)
                # Init the base class.
            #@+<< define dispatch dict >>
            #@+node:ekr.20060919110638.21: *4* << define dispatch dict >>
            #@@nobeautify

            # There is no need for an 'end' method if all info is carried in attributes.
            self.dispatchDict = {
                'change_string':               (None,None),
                'find_panel_settings':         (None,None),
                'find_string':                 (None,None),
                'globals':                     (self.startGlobals,None),
                'global_log_window_position':  (None,None), # The position of the log window is no longer used.
                'global_window_position':      (self.startWinPos,None),
                'leo_file':                    (None,None),
                'leo_header':                  (self.startLeoHeader,None),
                'preferences':                 (None,None),
                't':                           (self.startTnode,self.endTnode),
                'tnodes':                      (None,None),
                'v':                           (self.startVnode,self.endVnode),
                'vh':                          (self.startVH,self.endVH),
                'vnodes':                      (self.startVnodes,None), # Causes window to appear.
            }
            #@-<< define dispatch dict >>
            self.printElements = [] # 'all', 'v'
            # Global attributes of the .leo file...
            # self.body_outline_ratio = '0.5'
            self.global_window_position = {}
            self.encoding = 'utf-8'
            # Semantics...
            self.content = None
            self.elementStack = []
            self.errors = 0
            self.tnxToListDict = {}
                # Keys are tnx's (strings)
                # Values are *lists* of SaxNodeClass objects.
            self.level = 0
            self.node = None
            self.nodeList = [] # List of SaxNodeClass objects with the present VNode.
            self.nodeStack = []
            self.ratio = self.secondary_ratio = 0.5
            self.rootNode = None # a sax node.
            self.trace = False # True and g.unitTesting
        #@+node:ekr.20060919110638.29: *3*  sax.Do nothing
        def endElementNS(self, unused_name, unused_qname):
            g.trace(unused_name)

        def endDocument(self):
            pass

        def ignorableWhitespace(self, unused_whitespace):
            pass

        def skippedEntity(self, name):
            g.trace(name)

        def startElementNS(self, unused_name, unused_qname, unused_attrs):
            g.trace(unused_name)

        def startDocument(self):
            pass
        #@+node:ekr.20060919134313: *3*  sax.Utils
        #@+node:ekr.20060919110638.23: *4* attrsToList
        def attrsToList(self, attrs):
            '''Convert the attributes to a list of g.Bunches.

            attrs: an Attributes item passed to startElement.'''
            return [
                g.Bunch(name=name, val=attrs.getValue(name))
                    for name in attrs.getNames()]
        #@+node:ekr.20060919110638.26: *4* error
        def error(self, message):
            g.pr('\n\nXML error: %s\n' % (message))
            self.errors += 1
        #@+node:ekr.20060919110638.27: *4* inElement
        def inElement(self, name):
            return self.elementStack and name in self.elementStack
        #@+node:ekr.20060919110638.28: *4* printStartElement
        def printStartElement(self, name, attrs):
            indent = '\t' * self.level or ''
            if attrs.getLength() > 0:
                g.pr('%s<%s %s>' % (
                    indent,
                    self.clean(name).strip(),
                    self.attrsToString(attrs, sep=' ')),
                    newline=False)
            else:
                g.pr('%s<%s>' % (
                    indent,
                    self.clean(name).strip()),
                    newline=False)
            if name.lower() in ['v', 't', 'vnodes', 'tnodes',]:
                g.pr('')
        #@+node:ekr.20060919110638.24: *5* attrsToString
        def attrsToString(self, attrs, sep='\n'):
            '''Convert the attributes to a string.

            attrs: an Attributes item passed to startElement.

            sep: the separator charater between attributes.'''
            result = [
                '%s="%s"' % (bunch.name, bunch.val)
                for bunch in self.attrsToList(attrs)
            ]
            return sep.join(result)
        #@+node:ekr.20060919110638.25: *5* clean
        def clean(self, s):
            return g.toEncodedString(s, "ascii")
        #@+node:ekr.20060919110638.30: *3* sax.characters
        def characters(self, content):
            '''Handle the characters element.'''
            if content and not g.isUnicode(content):
                g.trace('Non-unicode content', repr(content))
                content = g.toUnicode(content)
            content = content.replace('\r', '')
            if not content:
                return
            elementName = self.elementStack[-1].lower() if self.elementStack else '<no element name>'
            # if self.trace: g.trace(elementName,content.strip())
            if elementName in ('t', 'vh'):
                # if elementName == 'vh': g.trace(elementName,repr(content))
                self.content.append(content)
            elif content.strip():
                g.pr('unexpected content:', elementName, repr(content))
        #@+node:ekr.20060919110638.31: *3* sax.endElement & helpers
        def endElement(self, name):
            '''Handle the end of any xml element.'''
            name = name.lower()
            if name in self.printElements or 'all' in self.printElements:
                indent = '\t' * (self.level - 1) or ''
                g.pr('%s</%s>' % (indent, self.clean(name).strip()))
            data = self.dispatchDict.get(name)
            if data is None:
                if 1: g.trace('unknown end element', name)
            else:
                junk, func = data
                if func:
                    func()
            name2 = self.elementStack.pop()
            assert name == name2
            # if self.trace: g.trace('** pop',name2)
        #@+node:ekr.20060919110638.32: *4* sax.endTnode
        def endTnode(self):
            '''Handle the end of a <tnode> element.'''
            trace = (False or self.trace) and not g.unitTesting
            # trace = trace and self.fileName.endswith('clone-test.leo')
            for sax_node in self.nodeList:
                sax_node.bodyString = ''.join(self.content)
                if trace: g.trace(repr(sax_node))
            self.content = []
        #@+node:ekr.20060919110638.33: *4* sax.endVnode
        def endVnode(self):
            '''Handle the end of a <vnode> element.'''
            self.level -= 1
            self.node = self.nodeStack.pop()
            # if self.trace: g.trace(repr(self.node))
        #@+node:ekr.20060919110638.34: *4* sax.endVH
        def endVH(self):
            '''Handle the end of a <vh> element.'''
            if self.node:
                self.node.headString = ''.join(self.content)
                # if self.trace: g.trace(repr(self.node))
            self.content = []
        #@+node:ekr.20060919110638.45: *3* sax.getRootNode
        def getRootNode(self):
            if self.trace:
                g.trace()
                self.rootNode.dump()
                for child in self.rootNode.children:
                    child.dump()
            return self.rootNode
        #@+node:ekr.20061004054323: *3* sax.processingInstruction (stylesheet)
        def processingInstruction(self, target, data):
            '''
            sax: handle an xml processing instruction.
            We expect the target to be 'xml-stylesheet'.
            '''
            trace = False and not g.unitTesting
            if target == 'xml-stylesheet':
                # A strange hack.  Don't set this for settings files.
                # This looks like a strange sax interaction.
                sfn = (self.c.shortFileName() or '').strip().lower()
                if sfn.endswith('leosettings.leo') or sfn.endswith('myleosettings.leo'):
                    pass
                else:
                    self.c.frame.stylesheet = data
                    if trace: g.trace(self.c.shortFileName(), repr(data))
                # g.warning('','%s: %s' % (target,data))
            else:
                g.trace(target, data)
        #@+node:ekr.20060919110638.35: *3* sax.startElement & helpers
        def startElement(self, name, attrs):
            name = name.lower()
            if name in self.printElements or 'all' in self.printElements:
                self.printStartElement(name, attrs)
            self.elementStack.append(name)
            # if self.trace: g.trace('**push',name)
            data = self.dispatchDict.get(name)
            if data is None:
                if 1: g.trace('unknown start element', name)
            else:
                func, junk = data
                if func:
                    func(attrs)
        #@+node:ekr.20060919110638.36: *4* sax.getWindowPositionAttributes
        def getWindowPositionAttributes(self, attrs):
            trace = False and not g.unitTesting
            c = self.c
            d = {}
            windowSize = g.app.loadManager.options.get('windowSize')
            if windowSize is not None:
                h, w = windowSize # checked in LM.scanOption.
                d['height'] = h
                d['width'] = w
                for bunch in self.attrsToList(attrs):
                    name = bunch.name; val = bunch.val
                    if name in ('top', 'left'):
                        try:
                            d[name] = int(val)
                        except ValueError:
                            d[name] = 50 # A reasonable default.
                if trace: g.trace(d)
            elif g.enableDB and c.mFileName:
                d = c.cacher.getCachedWindowPositionDict(c.mFileName)
            if not d and c.fixed and c.fixedWindowPosition:
                width, height, left, top = c.fixedWindowPosition
                d = {'top': top, 'left': left, 'width': width, 'height': height}
            if not d:
                for bunch in self.attrsToList(attrs):
                    name = bunch.name; val = bunch.val
                    if name in ('top', 'left', 'width', 'height'):
                        try:
                            d[name] = int(val)
                        except ValueError:
                            d[name] = 100 # A reasonable default.
                    else:
                        g.trace(name, len(val))
            if trace: g.trace(c.mFileName, d)
            return d # Assigned to self.global_window_position
        #@+node:ekr.20060919110638.37: *4* sax.startGlobals
        def startGlobals(self, attrs):
            trace = False and not g.unitTesting
            c = self.c
            if self.inClipboard:
                return
            if trace: g.trace(c.mFileName)
            use_db = g.enableDB and c.mFileName
            if use_db:
                ratio, ratio2 = c.cacher.getCachedGlobalFileRatios()
                if trace: g.trace(ratio, ratio2)
                self.ratio, self.secondary_ratio = ratio, ratio2
            else:
                try:
                    for bunch in self.attrsToList(attrs):
                        name = bunch.name; val = bunch.val
                        if name == 'body_outline_ratio':
                            self.ratio = float(val)
                        elif name == 'body_secondary_ratio':
                            self.secondary_ratio = float(val)
                    if trace: g.trace('** not cached:', '%1.2f %1.2f' % (
                        self.ratio, self.secondary_ratio))
                except Exception:
                    pass
        #@+node:ekr.20060919110638.38: *4* sax.startWinPos
        def startWinPos(self, attrs):
            self.global_window_position = self.getWindowPositionAttributes(attrs)
        #@+node:ekr.20060919110638.39: *4* sax.startLeoHeader
        def startLeoHeader(self, unused_attrs):
            self.tnxToListDict = {}
        #@+node:ekr.20060919110638.40: *4* sax.startVH
        def startVH(self, unused_attrs):
            self.content = []
        #@+node:ekr.20060919112118: *4* sax.startVnodes
        def startVnodes(self, unused_attrs):
            if self.inClipboard:
                return # No need to do anything to the main window.
            c = self.c; d = self.global_window_position
            w = d.get('width', 700)
            h = d.get('height', 500)
            x = d.get('left', 50)
            y = d.get('top', 50)
            # g.trace(d,w,h,x,y)
            # Redraw the window before writing into it.
            # Honor --minimized, --maximized or --fullscreen.
            # 2013/10/25: do set the geometry for minimized windows.
            if g.app.start_minimized:
                c.frame.setTopGeometry(w, h, x, y)
            elif not g.app.start_maximized and not g.app.start_fullscreen:
                c.frame.setTopGeometry(w, h, x, y)
                c.frame.deiconify()
                c.frame.lift()
            # Causes window to appear.
            if c.frame.top:
                c.frame.resizePanesToRatio(self.ratio, self.secondary_ratio)
            if not self.silent and not g.unitTesting:
                g.es("reading:", self.fileName)
        #@+node:ekr.20060919110638.41: *4* sax.startTnode
        def startTnode(self, attrs):
            if not self.inElement('tnodes'):
                self.error('<t> outside <tnodes>')
            self.content = []
            self.tnodeAttributes(attrs)
        #@+node:ekr.20060919110638.42: *5* sax.tnodeAttributes (SaxContentHandler)
        def tnodeAttributes(self, attrs):
            # The VNode must have a tx attribute to associate content
            # with the proper node.
            trace = False and not g.unitTesting
            verbose = False
            node = self.node
            self.nodeList = []
            val = None
            # Step one: find the tx attribute
            for bunch in self.attrsToList(attrs):
                name = bunch.name; val = bunch.val
                if name == 'tx':
                    # 2010/02/03: This code formerly did something
                    # different when unit testing just to support a unit test.
                    # Hahaha.  The unit test *caused* the bug!
                    self.nodeList = self.tnxToListDict.get(val, [])
                    if trace and verbose: g.trace('tx', self.nodeList)
                    break
            if not self.nodeList:
                self.error('Bad leo file: no node for <t tx=%s>' % (val))
                return
            # Step two: find all the other attributes:
            for bunch in self.attrsToList(attrs):
                name = bunch.name; val = bunch.val
                if name != 'tx':
                    # Huge bug fix: 2009/7/1: was node == self.node.
                    for node in self.nodeList:
                        if trace: g.trace('%s %s=%s...' % (node, name, val[: 20]))
                        node.tnodeAttributes[name] = val
            # if not self.nodeList:
                # self.error('Bad leo file: no tx attribute for VNode')
        #@+node:ekr.20060919110638.43: *4* sax.startVnode
        def startVnode(self, attrs):
            if not self.inElement('vnodes'):
                self.error('<v> outside <vnodes>')
            if self.rootNode:
                parent = self.node
            else:
                self.rootNode = parent = SaxNodeClass() # The dummy parent node.
                parent.headString = 'dummyNode'
            self.node = SaxNodeClass()
            parent.children.append(self.node)
            self.vnodeAttributes(attrs)
            self.nodeStack.append(parent)
            return parent
        #@+node:ekr.20060919110638.44: *5* sax.vnodeAttributes
        # The native attributes of <v> elements are a, t, vtag, tnodeList,
        # marks, expanded and descendentTnodeUnknownAttributes.

        def vnodeAttributes(self, attrs):
            node = self.node
            for bunch in self.attrsToList(attrs):
                name = bunch.name; val = bunch.val
                if name == 't':
                    aList = self.tnxToListDict.get(val, [])
                    aList.append(self.node)
                    self.tnxToListDict[val] = aList
                    node.tnx = str(val) # nodeIndices.toString returns a string.
                else:
                    node.attributes[name] = val
        #@-others
#@+node:ekr.20060919110638.15: ** class SaxNodeClass
if sys.platform != 'cli':

    class SaxNodeClass:
        '''A class representing one <v> element.

        Use getters to access the attributes, properties and rules of this mode.
        '''
        #@+others
        #@+node:ekr.20060919110638.16: *3*  node.__init__
        def __init__(self):
            self.attributes = {}
            self.bodyString = ''
            self.headString = ''
            self.children = []
            self.tnodeAttributes = {}
            self.tnodeList = []
            self.tnx = None
        #@+node:ekr.20060919110638.17: *3*  node.__str__ & __repr__
        def __str__(self):
            return '<v:%s %s %s>' % (id(self), self.headString, len(self.bodyString))

        __repr__ = __str__
        #@+node:ekr.20060919110638.18: *3* node.dump
        def dump(self):
            g.pr('\nnode: %s tnx: %s len(body): %d %s' % (
                id(self), self.tnx, len(self.bodyString), self.headString))
            g.pr('children:', g.listToString(self.children))
            g.pr('attrs:', list(self.attributes.values()))
        #@-others
#@+node:ekr.20160514120347.1: ** class FileCommands
class FileCommands(object):
    """A class creating the FileCommands subcommander."""
    #@+others
    #@+node:ekr.20090218115025.4: *3* fc.Birth
    #@+node:ekr.20150509194827.1: *4* fc.cmd (decorator)
    def cmd(name):
        '''Command decorator for the FileCommands class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'fileCommands',])
    #@+node:ekr.20031218072017.3019: *4* fc.ctor
    def __init__(self, c):
        '''Ctor for FileCommands class.'''
        # g.trace("__init__", "FileCommands.__init__")
        self.c = c
        self.frame = c.frame
        self.nativeTnodeAttributes = ('tx',)
        self.nativeVnodeAttributes = (
            'a',
            'descendentTnodeUnknownAttributes',
            'descendentVnodeUnknownAttributes', # New in Leo 4.5.
            'expanded', 'marks', 't', 'tnodeList',
            # 'vtag',
        )
        self.initIvars()
    #@+node:ekr.20090218115025.5: *4* fc.initIvars
    def initIvars(self):
        '''Init ivars of the FileCommands class.'''
        # General...
        c = self.c
        self.mFileName = ""
        self.fileDate = -1
        self.leo_file_encoding = c.config.new_leo_file_encoding
            # The bin param doesn't exist in Python 2.3;
            # the protocol param doesn't exist in earlier versions of Python.
            # version = '.'.join([str(sys.version_info[i]) for i in (0,1)])
        # For reading...
        self.checking = False # True: checking only: do *not* alter the outline.
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
    #@+node:ekr.20070919133659.1: *5* fc.checkLeoFile
    @cmd('check-leo-file')
    def checkLeoFile(self, event=None):
        '''The check-leo-file command.'''
        fc = self; c = fc.c; p = c.p
        # Put the body (minus the @nocolor) into the file buffer.
        s = p.b; tag = '@nocolor\n'
        if s.startswith(tag): s = s[len(tag):]
        # Do a trial read.
        self.checking = True
        self.initReadIvars()
        c.loading = True # disable c.changed
        try:
            try:
                theFile = g.app.loadManager.openLeoOrZipFile(c.mFileName)
                self.readSaxFile(
                    theFile, fileName='check-leo-file',
                    silent=False, inClipboard=False, reassignIndices=False)
                g.blue('check-leo-file passed')
            except Exception:
                junk, message, junk = sys.exc_info()
                # g.es_exception()
                g.error('check-leo-file failed:', str(message))
        finally:
            self.checking = False
            c.loading = False # reenable c.changed
    #@+node:vitalije.20180304190953.1: *5* fc.getVnodeFromClipboard
    def getVnodeFromClipboard(self, s):
        c = self.c
        self.initReadIvars()
        # Save the hidden root's children.
        children = c.hiddenRootNode.children
        oldGnxDict = self.gnxDict
        self.gnxDict = {}
        self.usingClipboard = True
        try:
            # This encoding must match the encoding used in putLeoOutline.
            s = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            # readSaxFile modifies the hidden root.
            v = self.readSaxFile(
                theFile=None, fileName='<clipboard>',
                silent=True, # don't tell about stylesheet elements.
                inClipboard=True, reassignIndices=True, s=s)
            if not v:
                return g.es("the clipboard is not valid ", color="blue")
        finally:
            self.usingClipboard = False
            self.gnxDict = oldGnxDict
        # Restore the hidden root's children
        c.hiddenRootNode.children = children
        # Unlink v from the hidden root.
        v.parents.remove(c.hiddenRootNode)
        return v

    def getPosFromClipboard(self, s):
        v = self.getVnodeFromClipboard(s)
        return leoNodes.Position(v)
    #@+node:ekr.20031218072017.1559: *5* fc.getLeoOutlineFromClipboard & helpers
    def getLeoOutlineFromClipboard(self, s, reassignIndices=True):
        '''Read a Leo outline from string s in clipboard format.'''
        c = self.c
        current = c.p
        if not current:
            g.trace('no c.p')
            return None
        check = not reassignIndices
        self.initReadIvars()
        # Save the hidden root's children.
        children = c.hiddenRootNode.children
        #
        # Save and clear gnxDict.
        # This ensures that new indices will be used for all nodes.
        if reassignIndices:
            oldGnxDict = self.gnxDict
            self.gnxDict = {}
        else:
            # All pasted nodes should already have unique gnx's.
            ni = g.app.nodeIndices
            for v in c.all_unique_nodes():
                ni.check_gnx(c, v.fileIndex, v)
        self.usingClipboard = True
        try:
            # This encoding must match the encoding used in putLeoOutline.
            s = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            # readSaxFile modifies the hidden root.
            v = self.readSaxFile(
                theFile=None, fileName='<clipboard>',
                silent=True, # don't tell about stylesheet elements.
                inClipboard=True, reassignIndices=reassignIndices, s=s)
            if not v:
                return g.es("the clipboard is not valid ", color="blue")
        finally:
            self.usingClipboard = False
        # Restore the hidden root's children
        c.hiddenRootNode.children = children
        # Unlink v from the hidden root.
        v.parents.remove(c.hiddenRootNode)
        p = leoNodes.Position(v)
        #
        # Important: we must not adjust links when linking v
        # into the outline.  The read code has already done that.
        if current.hasChildren() and current.isExpanded():
            if check and not self.checkPaste(current, p):
                return None
            p._linkAsNthChild(current, 0, adjust=False)
        else:
            if check and not self.checkPaste(current.parent(), p):
                return None
            p._linkAfter(current, adjust=False)
        if reassignIndices:
            self.gnxDict = oldGnxDict
            self.reassignAllIndices(p)
        else:
            # Fix #862: paste-retaining-clones can corrupt the outline.
            self.linkChildrenToParents(p)
        c.selectPosition(p)
        self.initReadIvars()
        return p

    getLeoOutline = getLeoOutlineFromClipboard # for compatibility
    #@+node:ekr.20080410115129.1: *6* fc.checkPaste
    def checkPaste(self, parent, p):
        '''Return True if p may be pasted as a child of parent.'''
        if not parent:
            return True
        parents = list(parent.self_and_parents())
        for p in p.self_and_subtree():
            for z in parents:
                if p.v == z.v:
                    g.warning('Invalid paste: nodes may not descend from themselves')
                    return False
        return True
    #@+node:ekr.20180424123010.1: *6* fc.linkChildrenToParents
    def linkChildrenToParents(self, p):
        '''
        Populate the parent links in all children of p.
        '''
        for child in p.children():
            if not child.v.parents:
                child.v.parents.append(p.v)
            self.linkChildrenToParents(child)
    #@+node:ekr.20180425034856.1: *6* fc.reassignAllIndices
    def reassignAllIndices(self, p):
        '''Reassign all indices in p's subtree.'''
        c = self.c
        ni = g.app.nodeIndices
        for p2 in p.self_and_subtree():
            v = p2.v
            index = ni.getNewIndex(v)
            if 'gnx' in g.app.debug:
                g.trace(c.shortFileName(), '**reassigning**', index, v)
    #@+node:ekr.20031218072017.1553: *5* fc.getLeoFile & helpers
    def getLeoFile(self,
        theFile,
        fileName,
        readAtFileNodesFlag=True,
        silent=False,
        checkOpenFiles=True,
    ):
        '''
            Read a .leo file.
            The caller should follow this with a call to c.redraw().
        '''
        trace = False and not g.unitTesting
        fc, c = self, self.c
        t1 = time.time()
        c.setChanged(False) # May be set when reading @file nodes.
        fc.warnOnReadOnlyFiles(fileName)
        fc.checking = False
        fc.mFileName = c.mFileName
        fc.initReadIvars()
        recoveryNode = None
        try:
            c.loading = True # disable c.changed
            if not silent and checkOpenFiles:
                # Don't check for open file when reverting.
                g.app.checkForOpenFile(c, fileName)
            ok = fc.getLeoFileHelper(theFile, fileName, silent)
                # Read the .leo file and create the outline.
            if ok:
                fc.resolveTnodeLists()
                    # Do this before reading external files.
                c.setFileTimeStamp(fileName)
                if readAtFileNodesFlag:
                    # Redraw before reading the @file nodes so the screen isn't blank.
                    # This is important for big files like LeoPy.leo.
                    c.redraw()
                    recoveryNode = fc.readExternalFiles(fileName)
        finally:
            if trace: g.trace(
                recoveryNode and recoveryNode.h,
                c.p and c.p.h)
            p = recoveryNode or c.p or c.lastTopLevel()
                # lastTopLevel is a better fallback, imo.
            # New in Leo 5.3. Delay the second redraw until idle time.
            # This causes a slight flash, but corrects a hangnail.

            def handler(timer, c=c, p=c.p):
                c.initialFocusHelper()
                c.redraw(p)
                c.k.showStateAndMode()
                c.outerUpdate()
                timer.stop()

            timer = g.IdleTime(handler, delay=0, tag='getLeoFile')
            if timer:
                timer.start()
            else:
                # Defensive code:
                c.selectPosition(p)
                c.initialFocusHelper()
                c.k.showStateAndMode()
                c.outerUpdate()

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
        c.setChanged(c.changed) # Refresh the changed marker.
        fc.initReadIvars()
        t2 = time.time()
        g.es('read outline in %2.2f seconds' % (t2 - t1))
        return ok, c.frame.ratio
    #@+node:ekr.20090526081836.5841: *6* fc.getLeoFileHelper
    def getLeoFileHelper(self, theFile, fileName, silent):
        '''Read the .leo file and create the outline.'''
        c, fc = self.c, self
        try:
            ok = True
            v = fc.readSaxFile(
                theFile,
                fileName,
                silent,
                inClipboard=False,
                reassignIndices=False,
            )
            if v:
                # readSaxFile sets c.hiddenRootNode.
                pass
            else:
                # v is None for minimal .leo files.
                v = leoNodes.VNode(context=c)
                v.setHeadString('created root node')
                p = leoNodes.Position(v)
                p._linkAsRoot(oldRoot=None)
                c.changed = False
        except BadLeoFile:
            junk, message, junk = sys.exc_info()
            if not silent:
                g.es_exception()
                c.alert(fc.mFileName + " is not a valid Leo file: " + str(message))
            ok = False
        return ok
    #@+node:ekr.20100205060712.8314: *6* fc.handleNodeConflicts
    def handleNodeConflicts(self):
        '''Create a 'Recovered Nodes' node for each entry in c.nodeConflictList.'''
        c = self.c
        if not c.nodeConflictList:
            return None
        if not c.make_node_conflicts_node:
            s = 'suppressed %s node conflicts' % len(c.nodeConflictList)
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
            h = 'Recovered node "%s" from %s' % (h1, g.shortFileName(fn))
            child.setHeadString(h)
            if b1 == b2:
                lines = [
                    'Headline changed...'
                    '%s gnx: %s root: %r' % (tag, gnx, root_v and root.v),
                    'old headline: %s' % (h1),
                    'new headline: %s' % (h2),
                ]
                child.setBodyString('\n'.join(lines))
            else:
                line1 = '%s gnx: %s root: %r\nDiff...\n' % (tag, gnx, root_v and root.v)
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
        '''Read all external files.'''
        c, fc = self.c, self
        c.atFileCommands.readAll(c.rootVnode(), force=False)
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
        '''Open a Leo file.'''
        c, frame = self.c, self.c.frame
        # Set c.openDirectory
        theDir = g.os_path_dirname(fileName)
        if theDir:
            c.openDirectory = c.frame.openDirectory = theDir
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
        #@+at
        # The most natural default directory is the directory containing the .leo file
        # that we are about to open. If the user has specified the "Default Directory"
        # preference that will over-ride what we are about to set.
        #@@c
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
        '''Updates public part of outline from the specified file.'''
        fc = self; c = self.c
        #@+others
        #@+node:vitalije.20170831144827.2: *6* get_ref_filename
        def get_ref_filename():
            for v in priv_vnodes():
                return g.splitLines(v.b)[0].strip()
        #@+node:vitalije.20170831144827.3: *6* createSaxChildren2
        def createSaxChildren2(sax_node, parent_v):
            children = []
            for sax_child in sax_node.children:
                tnx = sax_child.tnx
                v = fc.gnxDict.get(tnx)
                if v: # A clone.
                    ### v = fc.createSaxVnode(sax_child, parent_v, v=v)
                    fc.updateSaxClone(sax_child, parent_v, v)
                else:
                    v = fc.createSaxVnode(sax_child, parent_v)
                    createSaxChildren2(sax_child, v)
                children.append(v)
            return children
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
                (gnx,
                    h,
                    b,
                    children,
                    parents,
                    iconVal,
                    statusBits,
                    ua) = row
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
            dbrow = lambda v:(
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
        if theTime is None: # A pre-4.1 file index.
            if index[0] == "T":
                index = index[1:]
        return index
    #@+node:ekr.20040701065235.1: *5* fc.getDescendentAttributes
    def getDescendentAttributes(self, s, tag=""):
        '''s is a list of gnx's, separated by commas from a <v> or <t> element.
        Parses s into a list.

        This is used to record marked and expanded nodes.
        '''
        gnxs = s.split(',')
        result = [gnx for gnx in gnxs if len(gnx) > 0]
        # g.trace(tag,result)
        return result
    #@+node:EKR.20040627114602: *5* fc.getDescendentUnknownAttributes
    # Pre Leo 4.5 Only @thin vnodes had the descendentTnodeUnknownAttributes field.
    # New in Leo 4.5: @thin & @shadow vnodes have descendentVnodeUnknownAttributes field.

    def getDescendentUnknownAttributes(self, s, v=None):
        '''Unhexlify and unpickle t/v.descendentUnknownAttribute field.'''
        try:
            # Changed in version 3.2: Accept only bytestring or bytearray objects as input.
            s = g.toEncodedString(s) # 2011/02/22
            bin = binascii.unhexlify(s)
                # Throws a TypeError if val is not a hex string.
            val = pickle.loads(bin)
            return val
        except Exception:
            g.es_exception()
            g.trace('Can not unpickle', type(s), v and v.h, s[: 40])
            return None
    #@+node:ekr.20060919142200.1: *5* fc.initReadIvars
    def initReadIvars(self):
        self.descendentTnodeUaDictList = []
        self.descendentVnodeUaDictList = []
        self.descendentExpandedList = []
        self.descendentMarksList = []
            # 2011/12/10: never re-init this dict.
            # self.gnxDict = {}
            # g.trace('*** clearing gnxDict',g.callers())
        self.c.nodeConflictList = [] # 2010/01/05
        self.c.nodeConflictFileName = None # 2010/01/05
    #@+node:EKR.20040627120120: *5* fc.restoreDescendentAttributes
    def restoreDescendentAttributes(self):

        trace = False and not g.unitTesting
        trace_dict = False
        trace_expanded = False
        trace_marks = False
        c = self.c
        for resultDict in self.descendentTnodeUaDictList:
            if trace and trace_dict: g.trace('t.dict', resultDict)
            for gnx in resultDict:
                tref = self.canonicalTnodeIndex(gnx)
                v = self.gnxDict.get(tref)
                if v:
                    v.unknownAttributes = resultDict[gnx]
                    v._p_changed = 1
                elif trace:
                    g.error(
                        'restoreDescendantAttributes: '
                        'can not find VNode (duA): gnx = %s' % (gnx))
        # New in Leo 4.5: keys are archivedPositions, values are attributes.
        for root_v, resultDict in self.descendentVnodeUaDictList:
            if trace and trace_dict: g.trace('v.dict', resultDict)
            for key in resultDict:
                v = self.resolveArchivedPosition(key, root_v)
                if v:
                    v.unknownAttributes = resultDict[key]
                    v._p_changed = 1
                elif trace:
                    g.error(
                        'restoreDescendantAttributes: '
                        'can not find VNode (duA): archivedPosition: %s, root_v: %s' % (
                            key, root_v))
        marks = {}; expanded = {}
        for gnx in self.descendentExpandedList:
            tref = self.canonicalTnodeIndex(gnx)
            v = self.gnxDict.get(gnx)
            if v:
                expanded[v] = v
                # if trace: g.trace('expanded',v)
            elif trace and trace_expanded:
                g.error(
                    'restoreDescendantAttributes: '
                    'can not find VNode (expanded): gnx = %s, tref: %s' % (gnx, tref))
                # This doesn't help, because it is never written.
                # The real answer would be to delete the "offending" uA.
                    # self.descendentExpandedList.remove(gnx)
        for gnx in self.descendentMarksList:
            tref = self.canonicalTnodeIndex(gnx)
            v = self.gnxDict.get(gnx)
            if v: marks[v] = v
            elif trace and trace_marks:
                g.error(
                    'restoreDescendantAttributes: '
                    'can not find VNode (marks): gnx = %s tref: %s' % (gnx, tref))
                # This doesn't help, because it is never written.
                # The real answer would be to delete the "offending" uA.
                    # self.descendentMarksList.remove(gnx)
        if marks or expanded:
            # g.trace('marks',len(marks),'expanded',len(expanded))
            for p in c.all_unique_positions():
                if marks.get(p.v):
                    p.v.initMarkedBit()
                        # This was the problem: was p.setMark.
                        # There was a big performance bug in the mark hook in the Node Navigator plugin.
                if expanded.get(p.v):
                    p.expand()
                    # if trace: g.trace('expand',p.h)
    #@+node:ekr.20060919104530: *4* fc.Reading Sax
    #@+node:ekr.20090525144314.6526: *5* fc.cleanSaxInputString
    def cleanSaxInputString(self, s):
        '''Clean control characters from s.
        s may be a bytes or a (unicode) string.'''
        # Note: form-feed ('\f') is 12 decimal.
        badchars = [chr(ch) for ch in range(32)]
        badchars.remove('\t')
        badchars.remove('\r')
        badchars.remove('\n')
        flatten = ''.join(badchars)
        pad = ' ' * len(flatten)
        # pylint: disable=no-member
        # Class 'str' has no 'maketrans' member
        if g.isPython3:
            flatten = bytes(flatten, 'utf-8')
            pad = bytes(pad, 'utf-8')
            transtable = bytes.maketrans(flatten, pad)
        else:
            transtable = string.maketrans(flatten, pad)
        return s.translate(transtable)
    # for i in range(32): print i,repr(chr(i))
    #@+node:ekr.20060919110638.5: *5* fc.createSaxChildren & helpers
    def createSaxChildren(self, sax_node, parent_v):
        '''Create vnodes for all children in sax_node.children.'''
        children = []
        for sax_child in sax_node.children:
            tnx = sax_child.tnx
            v = self.gnxDict.get(tnx)
            if v: # A clone. Don't look at the children.
                self.updateSaxClone(sax_child, parent_v, v)
            else:
                v = self.createSaxVnode(sax_child, parent_v)
                self.createSaxChildren(sax_child, v)
            children.append(v)
        parent_v.children = children
        for child in children:
            child.parents.append(parent_v)
        return children
    #@+node:ekr.20060919110638.7: *6* fc.createSaxVnode & helpers
    def createSaxVnode(self, sax_node, parent_v):
        '''Create a vnode, or use an existing vnode.'''
        c = self.c
        at = c.atFileCommands
        #
        # Fix #158: Corrupt .leo files cause Leo to hang.
        # Explicitly test against None: tnx could be 0.
        if sax_node.tnx is None:
            gnx = None
        else:
            gnx = g.toUnicode(self.canonicalTnodeIndex(sax_node.tnx))
        #
        # Allocate and init a new vnode.
        v = leoNodes.VNode(context=c, gnx=gnx)
        v.setBodyString(sax_node.bodyString)
        at.bodySetInited(v)
        v.setHeadString(sax_node.headString)
        self.handleVnodeSaxAttributes(sax_node, v)
        self.handleTnodeSaxAttributes(sax_node, v)
        return v
    #@+node:ekr.20060919110638.8: *7* fc.handleTnodeSaxAttributes
    def handleTnodeSaxAttributes(self, sax_node, v):

        d = sax_node.tnodeAttributes
        aDict = {}
        for key in d:
            val = g.toUnicode(d.get(key))
            val2 = self.getSaxUa(key, val)
            aDict[key] = val2
        if aDict:
            v.unknownAttributes = aDict
    #@+node:ekr.20061004053644: *7* fc.handleVnodeSaxAttributes
    def handleVnodeSaxAttributes(self, sax_node, v):
        '''
        The native attributes of <v> elements are a, t, vtag, tnodeList,
        marks, expanded, and descendentTnode/VnodeUnknownAttributes.
        '''
        d = sax_node.attributes
        s = d.get('a')
        if s:
            if 'M' in s: v.setMarked()
            if 'E' in s: v.expand()
            if 'O' in s: v.setOrphan()
            if 'V' in s: self.currentVnode = v
        s = d.get('tnodeList', '')
        tnodeList = s and s.split(',')
        if tnodeList:
            # This tnodeList will be resolved later.
            v.tempTnodeList = tnodeList
        s = d.get('descendentTnodeUnknownAttributes')
        if s:
            aDict = self.getDescendentUnknownAttributes(s, v=v)
            if aDict:
                self.descendentTnodeUaDictList.append(aDict)
        s = d.get('descendentVnodeUnknownAttributes')
        if s:
            aDict = self.getDescendentUnknownAttributes(s, v=v)
            if aDict:
                self.descendentVnodeUaDictList.append((v, aDict),)
        s = d.get('expanded')
        if s:
            aList = self.getDescendentAttributes(s, tag="expanded")
            self.descendentExpandedList.extend(aList)
        s = d.get('marks')
        if s:
            aList = self.getDescendentAttributes(s, tag="marks")
            self.descendentMarksList.extend(aList)
        aDict = {}
        for key in d:
            if key in self.nativeVnodeAttributes:
                pass # This is not a bug.
            else:
                val = d.get(key)
                val2 = self.getSaxUa(key, val)
                aDict[key] = val2
        if aDict:
            v.unknownAttributes = aDict
    #@+node:ekr.20180424120245.1: *6* fc.updateSaxClone
    def updateSaxClone(self, sax_node, parent_v, v):
        '''
        Update the body text of v. It overrides any previous body text.
        '''
        at = self.c.atFileCommands
        b = sax_node.bodyString
        if v.b != b:
            v.setBodyString(b)
            at.bodySetInited(v)
        #
        # New in Leo 5.7.2. Don't call these
            # self.handleVnodeSaxAttributes(sax_node, v)
            # self.handleTnodeSaxAttributes(sax_node, v)
    #@+node:ekr.20060919110638.2: *5* fc.dumpSaxTree
    def dumpSaxTree(self, root, dummy):
        if not root:
            g.pr('dumpSaxTree: empty tree')
            return
        if not dummy:
            root.dump()
        for child in root.children:
            self.dumpSaxTree(child, dummy=False)
    #@+node:tbrown.20140615093933.89639: *5* fc.bytes_to_unicode
    def bytes_to_unicode(self, ob):
        """recursively convert bytes objects in strings / lists / dicts to str
        objects, thanks to TNT
        http://stackoverflow.com/questions/22840092/unpickling-data-from-python-2-with-unicode-strings-in-python-3

        Needed for reading Python 2.7 pickles in Python 3.4 in getSaxUa()
        """
        # pylint: disable=unidiomatic-typecheck
        # This is simpler than using isinstance.
        t = type(ob)
        if t in (list, tuple):
            l = [str(i, 'utf-8') if type(i) is bytes else i for i in ob]
            l = [self.bytes_to_unicode(i) if type(i) in (list, tuple, dict) else i
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
                    ob[k] = self.bytes_to_unicode(ob[k])
            ro = ob
        elif t is bytes: # TNB added this clause
            ro = str(ob, 'utf-8')
        else:
            ro = ob
        return ro
    #@+node:ekr.20061003093021: *5* fc.getSaxUa
    def getSaxUa(self, attr, val, kind=None): # Kind is for unit testing.
        """Parse an unknown attribute in a <v> or <t> element.
        The unknown tag has been pickled and hexlify'd.
        """
        try:
            # val = str(val)
            val = g.toEncodedString(val) # 2011/02/22.
        except Exception:
            g.es_print('unexpected exception converting hexlified string to string')
            g.es_exception()
            return None
        # New in 4.3: leave string attributes starting with 'str_' alone.
        if attr.startswith('str_'):
            if g.isString(val) or g.isBytes(val):
                return g.toUnicode(val)
        # New in 4.3: convert attributes starting with 'b64_' using the base64 conversion.
        if 0: # Not ready yet.
            if attr.startswith('b64_'):
                try: pass
                except Exception: pass
        try:
            binString = binascii.unhexlify(val) # Throws a TypeError if val is not a hex string.
        except Exception:
            # Python 2.x throws TypeError
            # Python 3.x throws binascii.Error
            # Assume that Leo 4.1 wrote the attribute.
            if g.unitTesting:
                assert kind == 'raw', 'unit test failed: kind=' % repr(kind)
            else:
                g.trace('can not unhexlify %s=%s' % (attr, val))
            return val
        try:
            # No change needed to support protocols.
            val2 = pickle.loads(binString)
            # g.trace('v.3 val:',val2)
            return val2
        except(pickle.UnpicklingError, ImportError, AttributeError, ValueError, TypeError):
            try:
                # for python 2.7 in python 3.4
                # pylint: disable=unexpected-keyword-arg
                val2 = pickle.loads(binString, encoding='bytes')
                val2 = self.bytes_to_unicode(val2)
                return val2
            except(pickle.UnpicklingError, ImportError, AttributeError, ValueError, TypeError):
                g.trace('can not unpickle %s=%s' % (attr, val))
                return val
    #@+node:ekr.20060919110638.14: *5* fc.parse_leo_file
    def parse_leo_file(self, theFile, inputFileName, silent, inClipboard, s=None):
        c = self.c
        # Fix #434: Potential bug in settings.
        if not theFile and not s:
            return None
        try:
            if g.isPython3:
                if theFile:
                    # Use the open binary file, opened by the caller.
                    s = theFile.read() # isinstance(s, bytes)
                    s = self.cleanSaxInputString(s)
                    theFile = BytesIO(s)
                else:
                    s = str(s, encoding='utf-8')
                    s = self.cleanSaxInputString(s)
                    theFile = StringIO(s)
            else:
                if theFile: s = theFile.read()
                s = self.cleanSaxInputString(s)
                theFile = cStringIO.StringIO(s)
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_external_ges, 1)
                # Include external general entities, esp. xml-stylesheet lines.
            if 0: # Expat does not read external features.
                parser.setFeature(xml.sax.handler.feature_external_pes, 1)
                    # Include all external parameter entities
                    # Hopefully the parser can figure out the encoding from the <?xml> element.
            # It's very hard to do anything meaningful wih an exception.
            handler = SaxContentHandler(c, inputFileName, silent, inClipboard)
            parser.setContentHandler(handler)
            parser.parse(theFile) # expat does not support parseString
            # g.trace('parsing done')
            sax_node = handler.getRootNode()
        except Exception:
            g.error('error parsing', inputFileName)
            g.es_exception()
            sax_node = None
        return sax_node
    #@+node:ekr.20060919110638.3: *5* fc.readSaxFile
    def readSaxFile(self, theFile, fileName, silent, inClipboard, reassignIndices, s=None):
        '''Read the entire .leo file using the sax parser.'''
        dump = False and not g.unitTesting
        fc = self; c = fc.c

        if fileName.endswith('.db'):
            return fc.retrieveVnodesFromDb(theFile) or fc.initNewDb(theFile)
        #
        # Pass one: create the intermediate nodes.
        saxRoot = fc.parse_leo_file(theFile, fileName,
            silent=silent, inClipboard=inClipboard, s=s)
        if not saxRoot:
            return None
        #
        # Pass two: create the tree of vnodes from the intermediate nodes.
        if dump: fc.dumpSaxTree(saxRoot, dummy=True)
        parent_v = c.hiddenRootNode
        children = fc.createSaxChildren(saxRoot, parent_v)
        assert c.hiddenRootNode.children == children
        v = children[0] if children else None
        return v
       
            
                
    #@+node:ekr.20060919110638.11: *5* fc.resolveTnodeLists
    def resolveTnodeLists(self):
        '''
        Called *before* reading external files.
        '''
        trace = False and not g.unitTesting
        c = self.c
        for p in c.all_unique_positions():
            if hasattr(p.v, 'tempTnodeList'):
                # g.trace(p.v.headString())
                result = []
                for tnx in p.v.tempTnodeList:
                    index = self.canonicalTnodeIndex(tnx)
                    # new gnxs:
                    index = g.toUnicode(index)
                    v = self.gnxDict.get(index)
                    if v:
                        if trace: g.trace(tnx, v)
                        result.append(v)
                    else:
                        g.trace('*** No VNode for %s' % tnx)
                if result:
                    p.v.tnodeList = result
                    # g.trace('*** tnodeList for',p.h,result)
                delattr(p.v, 'tempTnodeList')
    #@+node:ekr.20080805132422.3: *5* fc.resolveArchivedPosition
    def resolveArchivedPosition(self, archivedPosition, root_v):
        '''
        Return a VNode corresponding to the archived position relative to root
        node root_v.
        '''
        trace = False and not g.unitTesting

        def oops(message):
            '''Give an error only if no file errors have been seen.'''
            if trace and self.c.atFileCommands.errors == 0:
                g.error('bad archived position: %s' % (message))
            return None

        try:
            aList = [int(z) for z in archivedPosition.split('.')]
            aList.reverse()
        except Exception:
            return oops('"%s"' % archivedPosition)
        if not aList:
            return oops('empty')
        last_v = root_v
        n = aList.pop()
        if n != 0:
            return oops('root index="%s"' % n)
        while aList:
            n = aList.pop()
            children = last_v.children
            if n < len(children):
                last_v = children[n]
            else:
                return oops('bad index="%s", len(children)="%s"' % (n, len(children)))
        return last_v
    #@+node:vitalije.20170630152841.1: *5* fc.retrieveVnodesFromDb
    def retrieveVnodesFromDb(self, conn):
        '''Recreates tree from the data contained in table vnodes. This
           method follows behavior of readSaxFile.'''

        fc = self; c = fc.c
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
                (gnx,
                    h,
                    b,
                    children,
                    parents,
                    iconVal,
                    statusBits,
                    ua) = row
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
        c.frame.setTopGeometry(w, h, x, y, adjustSize=True)
        c.frame.resizePanesToRatio(r1, r2)
        p = fc.decodePosition(encp)
        c.setCurrentPosition(p)
        return rootChildren[0]
    #@+node:vitalije.20170815162307.1: *6* fc.initNewDb
    def initNewDb(self, conn):
        ''' Initializes tables and returns None'''
        fc = self; c = self.c
        v = leoNodes.VNode(context=c)
        c.hiddenRootNode.children = [v]
        (w, h, x, y, r1, r2, encp) = fc.getWindowGeometryFromDb(conn)
        c.frame.setTopGeometry(w, h, x, y, adjustSize=True)
        c.frame.resizePanesToRatio(r1, r2)
        c.sqlite_connection = conn
        fc.exportToSqlite(c.mFileName)
        return v
    #@+node:vitalije.20170630200802.1: *6* fc.getWindowGeometryFromDb
    def getWindowGeometryFromDb(self, conn):
        geom = (600, 400, 50, 50 , 0.5, 0.5, '')
        keys = (  'width', 'height', 'left', 'top',
                  'ratio', 'secondary_ratio',
                  'current_position')
        try:
            d = dict(conn.execute('''select * from extra_infos 
                where name in (?, ?, ?, ?, ?, ?, ?)''', keys).fetchall())
            geom = (d.get(*x) for x in zip(keys, geom))
        except sqlite3.OperationalError:
            pass
        return geom
    #@+node:ekr.20060919110638.13: *5* fc.setPositionsFromVnodes & helper (sax read)
    def setPositionsFromVnodes(self):
        trace = False and not g.unitTesting
        c, root = self.c, self.c.rootPosition()
        if c.sqlite_connection:
            # position is already selected
            return
        current, str_pos = None, None
        use_db = g.enableDB and c.mFileName
        if use_db:
            str_pos = c.cacher.getCachedStringPosition()
            if trace: g.trace('cached str_pos', str_pos)
        if not str_pos:
            d = root.v.u
            if trace: g.trace(d)
            if d: str_pos = d.get('str_leo_pos')
            if trace: g.trace('p.v.u', str_pos)
        if str_pos:
            current = self.archivedPositionToPosition(str_pos)
            if trace: g.trace(current and current.h)
        elif trace:
            g.trace('no str_pos!')
        c.setCurrentPosition(current or c.rootPosition())
    #@+node:ekr.20061006104837.1: *6* fc.archivedPositionToPosition
    def archivedPositionToPosition(self, s):
        trace = False and not g.unitTesting
        c = self.c
        s = g.toUnicode(s) # 2011/02/25
        aList = s.split(',')
        try:
            aList = [int(z) for z in aList]
        except Exception:
            if trace: g.trace('not all ints:', aList)
            aList = None
        if not aList: return None
        p = c.rootPosition(); level = 0
        while level < len(aList):
            i = aList[level]
            while i > 0:
                if p.hasNext():
                    p.moveToNext()
                    i -= 1
                else:
                    # g.trace('oops: bad archived position. no sibling:',aList,p.h,c)
                    return None
            level += 1
            if level < len(aList):
                p.moveToFirstChild()
                # g.trace('level',level,'index',aList[level],p.h)
        return p
    #@+node:ekr.20031218072017.3032: *3* fc.Writing
    #@+node:ekr.20070413045221.2: *4*  fc.Top-level
    #@+node:ekr.20031218072017.1720: *5* fc.save
    def save(self, fileName, silent=False):
        c = self.c
        p = c.p
        # New in 4.2.  Return ok flag so shutdown logic knows if all went well.
        ok = g.doHook("save1", c=c, p=p, fileName=fileName)
        if ok is None:
            c.endEditing() # Set the current headline text.
            self.setDefaultDirectoryForNewFiles(fileName)
            c.cacher.save(fileName, changeName=True)
            ok = c.checkFileTimeStamp(fileName)
            if ok:
                if c.sqlite_connection:
                    c.sqlite_connection.close()
                    c.sqlite_connection = None
                ok = self.write_Leo_file(fileName, False) # outlineOnlyFlag
            if ok:
                if not silent:
                    self.putSavedMessage(fileName)
                c.setChanged(False) # Clears all dirty bits.
                if c.config.save_clears_undo_buffer:
                    g.es("clearing undo")
                    c.undoer.clearUndoState()
            c.redraw_after_icons_changed()
        g.doHook("save2", c=c, p=p, fileName=fileName)
        return ok
    #@+node:vitalije.20170831135146.1: *5* fc.save_ref
    def save_ref(self):
        '''Saves reference outline file'''
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
            for p in c.rootPosition().self_and_siblings():
                if p.h == PRIVAREA:
                    ref_fname = p.b.split('\n',1)[0].strip()
                    break
                # New in Leo 4.4.2 b2 An optimization:
                fc.putVnode(p, isIgnore=p.isAtIgnoreNode()) # Write the next top-level node.
            fc.put("</vnodes>\n")
            return ref_fname
        #@+node:vitalije.20170831135447.1: *6* getPublicLeoFile
        def getPublicLeoFile():
            fc.outputFile = g.FileLikeObject()
            fc.updateFixedStatus()
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
            with open(fileName, 'w') as out:
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
            c.endEditing() # Set the current headline text.
            if c.sqlite_connection:
                c.sqlite_connection.close()
                c.sqlite_connection = None
            self.setDefaultDirectoryForNewFiles(fileName)
            c.cacher.save(fileName, changeName=True)
            # Disable path-changed messages in writeAllHelper.
            c.ignoreChangedPaths = True
            try:
                if self.write_Leo_file(fileName, outlineOnlyFlag=False):
                    c.setChanged(False) # Clears all dirty bits.
                    self.putSavedMessage(fileName)
            finally:
                c.ignoreChangedPaths = True
            c.redraw_after_icons_changed()
        g.doHook("save2", c=c, p=p, fileName=fileName)
    #@+node:ekr.20031218072017.3044: *5* fc.saveTo
    def saveTo(self, fileName, silent=False):
        c = self.c
        p = c.p
        if not g.doHook("save1", c=c, p=p, fileName=fileName):
            c.endEditing() # Set the current headline text.
            if c.sqlite_connection:
                c.sqlite_connection.close()
                c.sqlite_connection = None
            self.setDefaultDirectoryForNewFiles(fileName)
            c.cacher.save(fileName, changeName=False)
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
    #@+node:ekr.20070413061552: *5* fc.putSavedMessage
    def putSavedMessage(self, fileName):
        c = self.c
        # #531: Optionally report timestamp...
        if c.config.getBool('log_show_save_time', default=False):
            format = c.config.getString('log_timestamp_format') or "%H:%M:%S"
            timestamp = time.strftime(format) + ' '
        else:
            timestamp = ''
        zipMark = '[zipped] ' if c.isZipped else ''
        g.es("%ssaved: %s%s" % (timestamp, zipMark, g.shortFileName(fileName)))
    #@+node:ekr.20050404190914.2: *4* fc.deleteFileWithMessage
    def deleteFileWithMessage(self, fileName, unused_kind):
        try:
            os.remove(fileName)
        except Exception:
            if self.read_only:
                g.error("read only")
            if not g.unitTesting:
                g.error("exception deleting backup file:", fileName)
                g.es_exception(full=False)
            return False
    #@+node:ekr.20031218072017.1470: *4* fc.put & helpers
    def put(self, s):
        '''Put string s to self.outputFile. All output eventually comes here.'''
        # Improved code: self.outputFile (a cStringIO object) always exists.
        if s:
            # if g.unitTesting: g.trace(g.callers(1),repr(s))
            self.putCount += 1
            if not g.isPython3:
                s = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
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
        if a: self.put(a) # will always be True if we use backquotes.
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
        # Put the minimum header for sax.
        self.put('<leo_header file_format="2"/>\n')
    #@+node:ekr.20040324080819.1: *4* fc.putLeoFile & helpers
    def putLeoFile(self):
        self.updateFixedStatus()
        self.putProlog()
        self.putHeader()
        self.putGlobals()
        self.putPrefs()
        self.putFindSettings()
        #start = g.getTime()
        self.putVnodes()
        #start = g.printDiffTime("vnodes ",start)
        self.putTnodes()
        #start = g.printDiffTime("tnodes ",start)
        self.putPostlog()
    #@+node:ekr.20031218072017.3035: *5* fc.putFindSettings
    def putFindSettings(self):
        # New in 4.3:  These settings never get written to the .leo file.
        self.put("<find_panel_settings/>")
        self.put_nl()
    #@+node:ekr.20031218072017.3037: *5* fc.putGlobals
    # Changed for Leo 4.0.

    def putGlobals(self):
        trace = False and not g.unitTesting
        c = self.c
        use_db = g.enableDB and c.mFileName
        if use_db:
            if trace: g.trace(c.mFileName)
            c.cacher.setCachedGlobalsElement(c.mFileName)
        # Always put positions, to trigger sax methods.
        self.put("<globals")
        #@+<< put the body/outline ratios >>
        #@+node:ekr.20031218072017.3038: *6* << put the body/outline ratios >>
        self.put(" body_outline_ratio=")
        self.put_in_dquotes("0.5" if c.fixed or use_db else "%1.2f" % (
            c.frame.ratio))
        self.put(" body_secondary_ratio=")
        self.put_in_dquotes("0.5" if c.fixed or use_db else "%1.2f" % (
            c.frame.secondary_ratio))
        if trace: g.trace('fixed or use_db', c.fixed or use_db,
            '%1.2f %1.2f' % (c.frame.ratio, c.frame.secondary_ratio))
        #@-<< put the body/outline ratios >>
        self.put(">"); self.put_nl()
        #@+<< put the position of this frame >>
        #@+node:ekr.20031218072017.3039: *6* << put the position of this frame >>
        # New in Leo 4.5: support fixed .leo files.
        if c.fixed or use_db:
            width, height, left, top = 700, 500, 50, 50
                # Put fixed, immutable, reasonable defaults.
                # Leo 4.5 and later will ignore these when reading.
                # These should be reasonable defaults so that the
                # file will be opened properly by older versions
                # of Leo that do not support fixed .leo files.
        else:
            width, height, left, top = c.frame.get_window_info()
        # g.trace(width,height,left,top)
        self.put_tab()
        self.put("<global_window_position")
        self.put(" top="); self.put_in_dquotes(str(top))
        self.put(" left="); self.put_in_dquotes(str(left))
        self.put(" height="); self.put_in_dquotes(str(height))
        self.put(" width="); self.put_in_dquotes(str(width))
        self.put("/>"); self.put_nl()
        #@-<< put the position of this frame >>
        #@+<< put the position of the log window >>
        #@+node:ekr.20031218072017.3040: *6* << put the position of the log window >>
        top = left = height = width = 0 # no longer used
        self.put_tab()
        self.put("<global_log_window_position")
        self.put(" top="); self.put_in_dquotes(str(top))
        self.put(" left="); self.put_in_dquotes(str(left))
        self.put(" height="); self.put_in_dquotes(str(height))
        self.put(" width="); self.put_in_dquotes(str(width))
        self.put("/>"); self.put_nl()
        #@-<< put the position of the log window >>
        self.put("</globals>"); self.put_nl()
    #@+node:ekr.20031218072017.3041: *5* fc.putHeader
    def putHeader(self):
        tnodes = 0; clone_windows = 0 # Always zero in Leo2.
        if 1: # For compatibility with versions before Leo 4.5.
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
        '''Put the prolog of the xml file.'''
        tag = 'http://leoeditor.com/namespaces/leo-python-editor/1.1'
        self.putXMLLine()
        # Put "created by Leo" line.
        self.put('<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->')
        self.put_nl()
        self.putStyleSheetLine()
        # Put the namespace
        self.put('<leo_file xmlns:leo="%s" >' % tag)
        self.put_nl()
    #@+node:ekr.20031218072017.1248: *5* fc.putStyleSheetLine
    def putStyleSheetLine(self):
        '''
        Put the xml stylesheet line.

        Leo 5.3:
        - Use only the stylesheet setting, ignoreing c.frame.stylesheet.
        - Write no stylesheet element if there is no setting.

        The old way made it almost impossible to delete stylesheet element.
        '''
        trace = False and not g.unitTesting
        c = self.c
        sheet = (c.config.getString('stylesheet') or '').strip()
        # sheet2 = c.frame.stylesheet and c.frame.stylesheet.strip() or ''
        # sheet = sheet or sheet2
        if sheet:
            s = '<?xml-stylesheet %s ?>' % sheet
            if trace: g.trace(c.shortFileName(), s)
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
        self.put('<t tx="%s"%s>%s</t>\n' % (gnx, ua, body))
    #@+node:ekr.20031218072017.1575: *5* fc.putTnodes
    def putTnodes(self):
        """Puts all tnodes as required for copy or save commands"""
        self.put("<tnodes>\n")
        self.putReferencedTnodes()
        self.put("</tnodes>\n")
    #@+node:ekr.20031218072017.1576: *6* fc.putReferencedTnodes
    def putReferencedTnodes(self):
        '''Put all referenced tnodes.'''
        c = self.c
        if self.usingClipboard: # write the current tree.
            theIter = self.currentPosition.self_and_subtree()
        else: # write everything
            theIter = c.all_unique_positions()
        # Populate tnodes
        tnodes = {}
        for p in theIter:
            # Make *sure* the file index has the proper form.
            # pylint: disable=unbalanced-tuple-unpacking
            index = p.v.fileIndex
            tnodes[index] = p.v
        # Put all tnodes in index order.
        for index in sorted(tnodes):
            # g.trace(index)
            v = tnodes.get(index)
            if v:
                # Write only those tnodes whose vnodes were written.
                # **Note**: @<file> trees are not written unless they contain clones.
                if v.isWriteBit():
                    self.putTnode(v)
            else:
                g.trace('can not happen: no VNode for', repr(index))
                # This prevents the file from being written.
                raise BadLeoFile('no VNode for %s' % repr(index))
    #@+node:ekr.20031218072017.1863: *5* fc.putVnode & helper
    def putVnode(self, p, isIgnore=False):
        """Write a <v> element corresponding to a VNode."""
        fc = self
        v = p.v
        isAuto = p.isAtAutoNode() and p.atAutoNodeName().strip()
        isEdit = p.isAtEditNode() and p.atEditNodeName().strip() and not p.hasChildren()
            # 2010/09/02: @edit nodes must not have children.
            # If they do, the entire tree is written to the outline.
        isFile = p.isAtFileNode()
        isShadow = p.isAtShadowFileNode()
        isThin = p.isAtThinFileNode()
        isOrphan = p.isOrphan()
        if not isIgnore:
            isIgnore = p.isAtIgnoreNode()
        # 2010/10/22: force writes of orphan @edit, @auto and @shadow trees.
        if isIgnore: forceWrite = True # Always write full @ignore trees.
        elif isAuto: forceWrite = isOrphan # Force write of orphan @auto trees.
        elif isEdit: forceWrite = isOrphan # Force write of orphan @edit trees.
        elif isFile: forceWrite = isOrphan # Force write of orphan @file trees.
        elif isShadow: forceWrite = isOrphan # Force write of @shadow trees.
        elif isThin: forceWrite = isOrphan # Force write of  orphan @thin trees.
        else: forceWrite = True # Write all other @<file> trees.
        gnx = v.fileIndex
        if forceWrite or self.usingClipboard:
            v.setWriteBit() # 4.2: Indicate we wrote the body text.
        attrs = fc.compute_attribute_bits(forceWrite, p)
        # Write the node.
        v_head = '<v t="%s"%s>' % (gnx, attrs)
        if gnx in fc.vnodesDict:
            fc.put(v_head + '</v>\n')
        else:
            fc.vnodesDict[gnx] = True
            v_head += '<vh>%s</vh>' % (xml.sax.saxutils.escape(p.v.headString() or ''))
            # New in 4.2: don't write child nodes of @file-thin trees
            # (except when writing to clipboard)
            if p.hasChildren() and (forceWrite or self.usingClipboard):
                fc.put('%s\n' % v_head)
                # This optimization eliminates all "recursive" copies.
                p.moveToFirstChild()
                while 1:
                    fc.putVnode(p, isIgnore)
                    if p.hasNext(): p.moveToNext()
                    else: break
                p.moveToParent() # Restore p in the caller.
                fc.put('</v>\n')
            else:
                fc.put('%s</v>\n' % v_head) # Call put only once.
    #@+node:ekr.20031218072017.1865: *6* fc.compute_attribute_bits
    def compute_attribute_bits(self, forceWrite, p):
        '''Return the initial values of v's attributes.'''
        c, v = self.c, p.v
        attrs = []
        # New in Leo 4.5: support fixed .leo files.
        if not c.fixed:
            bits = []
            if v.isExpanded() and v.hasChildren() and c.putBitsFlag:
                bits.append("E")
            if v.isMarked():
                bits.append("M")
            if bits:
                attrs.append(' a="%s"' % ''.join(bits))
        # Put the archived *current* position in the *root* position's <v> element.
        if p == self.rootPosition:
            aList = [str(z) for z in self.currentPosition.archivedPosition()]
            d = v.u
            str_pos = ','.join(aList)
            if d.get('str_leo_pos'):
                del d['str_leo_pos']
            # Don't write the current position if we can cache it.
            if g.enableDB and c.mFileName:
                c.cacher.setCachedStringPosition(str_pos)
            elif c.fixed:
                pass
            else:
                d['str_leo_pos'] = str_pos
            v.u = d
        elif hasattr(v, "unknownAttributes"):
            d = v.unknownAttributes
            if d and not c.fixed and d.get('str_leo_pos'):
                # g.trace("clearing str_leo_pos",v)
                del d['str_leo_pos']
                v.unknownAttributes = d
        # Append unKnownAttributes to attrs
        if p.hasChildren() and not forceWrite and not self.usingClipboard:
            # Fix #526: do this for @auto nodes as well.
            attrs.append(self.putDescendentVnodeUas(p))
            attrs.append(self.putDescendentAttributes(p))
        return ''.join(attrs)
    #@+node:ekr.20031218072017.1579: *5* fc.putVnodes
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
            self.putVnode(self.currentPosition) # Write only current tree.
        else:
            for p in c.rootPosition().self_and_siblings():
                # New in Leo 4.4.2 b2 An optimization:
                self.putVnode(p, isIgnore=p.isAtIgnoreNode()) # Write the next top-level node.
        self.put("</vnodes>\n")
    #@+node:ekr.20031218072017.1247: *5* fc.putXMLLine
    def putXMLLine(self):
        '''Put the **properly encoded** <?xml> element.'''
        # Use self.leo_file_encoding encoding.
        self.put('%s"%s"%s\n' % (
            g.app.prolog_prefix_string,
            self.leo_file_encoding,
            g.app.prolog_postfix_string))
    #@+node:ekr.20031218072017.1573: *4* fc.putLeoOutline (to clipboard)
    def putLeoOutline(self, p=None):
        '''
        Return a string, *not unicode*, encoded with self.leo_file_encoding,
        suitable for pasting to the clipboard.
        '''
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
        self.usingClipboard = False
        return s
    #@+node:ekr.20031218072017.3046: *4* fc.write_Leo_file & helpers
    def write_Leo_file(self, fileName, outlineOnlyFlag, toString=False, toOPML=False):
        '''Write the .leo file.'''
        c, fc = self.c, self
        structure_errors = c.checkOutline()
        if structure_errors:
            g.error('Major structural errors! outline not written')
            return False

        if not outlineOnlyFlag or toOPML:
            g.app.recentFilesManager.writeRecentFilesFile(c)
            fc.writeAllAtFileNodesHelper() # Ignore any errors.

        if fc.isReadOnly(fileName):
            return False

        if g.SQLITE and fileName and fileName.endswith('.db'):
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

    write_LEO_file = write_Leo_file # For compatibility with old plugins.
    #@+node:ekr.20040324080359.1: *5* fc.isReadOnly
    def isReadOnly(self, fileName):
        # self.read_only is not valid for Save As and Save To commands.
        if g.os_path_exists(fileName):
            try:
                if not os.access(fileName, os.W_OK):
                    g.error("can not write: read only:", fileName)
                    return True
            except Exception:
                pass # os.access() may not exist on all platforms.
        return False
    #@+node:ekr.20100119145629.6114: *5* fc.writeAllAtFileNodesHelper
    def writeAllAtFileNodesHelper(self):
        '''Write all @<file> nodes and set orphan bits.'''
        c = self.c
        try:
            # 2010/01/19: Do *not* signal failure here.
            # This allows Leo to quit properly.
            c.atFileCommands.writeAll()
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
        self.outputFile = StringIO() # Always write to a string.
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
            g.app.write_Leo_file_string = s # 2010/01/19: always set this.
            if toZip:
                self.writeZipFile(s)
            else:
                if g.isPython3:
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
            self.handleWriteLeoFileException(
                fileName, backupName, theActualFile)
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
            except IOError:
                g.es('can not open %s' % fileName)
                g.es_exception()
                theActualFile = None
        return fileName, theActualFile
    #@+node:ekr.20031218072017.3047: *6* fc.createBackupFile
    def createBackupFile(self, fileName):
        '''
            Create a closed backup file and copy the file to it,
            but only if the original file exists.
        '''
        if g.os_path_exists(fileName):
            fd, backupName = tempfile.mkstemp(text=False)
            f = open(fileName, 'rb') # rb is essential.
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
        '''Dump all vnodes to sqlite database. Returns True on success.'''
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
        dbrow = lambda v:(
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
        '''Creates position from its string representation encoded by fc.encodePosition.'''
        fc = self
        if not s:
            return fc.c.rootPosition()
        sep = g.u('<->')
        comma = g.u(',')
        stack = [x.split(comma) for x in s.split(sep)]
        stack = [(fc.gnxDict[x], int(y)) for x,y in stack]
        v, ci = stack[-1]
        p = leoNodes.Position(v, ci, stack[:-1])
        return p
    #@+node:vitalije.20170705075117.1: *6* fc.encodePosition
    def encodePosition(self, p):
        '''New schema for encoding current position hopefully simplier one.'''
        jn = g.u('<->')
        mk = g.u('%s,%s')
        res = [mk%(x.gnx, y) for x,y in p.stack]
        res.append(mk%(p.gnx, p._childIndex))
        return jn.join(res)
    #@+node:vitalije.20170811130512.1: *6* fc.prepareDbTables
    def prepareDbTables(self, conn):
        conn.execute('''drop table if exists vnodes;''')
        conn.execute('''
            create table if not exists vnodes(
                gnx primary key,
                head,
                body,
                children,
                parents,
                iconVal,
                statusBits,
                ua);''')
        conn.execute('''create table if not exists extra_infos(name primary key, value)''')
    #@+node:vitalije.20170701161851.1: *6* fc.exportVnodesToSqlite
    def exportVnodesToSqlite(self, conn, rows):
        conn.executemany('''insert into vnodes
            (gnx, head, body, children, parents,
                iconVal, statusBits, ua)
            values(?,?,?,?,?,?,?,?);''', rows)
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
        conn.execute("replace into extra_infos(name, value) values('dbversion', ?)", ('1.0',))
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
                files.add((fn, 'md5_'+p.gnx))
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        # pylint: disable=deprecated-lambda
        conn.executemany(
            'replace into extra_infos(name, value) values(?,?)',
            map(lambda x:(x[1], md5(x[0])), files))

    #@+node:ekr.20031218072017.2012: *4* fc.writeAtFileNodes
    @cmd('write-at-file-nodes')
    def writeAtFileNodes(self, event=None):
        '''Write all @file nodes in the selected outline.'''
        c = self.c
        c.init_error_dialogs()
        c.atFileCommands.writeAll(writeAtFileNodesFlag=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20080801071227.5: *4* fc.writeAtShadowNodes
    def writeAtShadowNodes(self, event=None):
        '''Write all @file nodes in the selected outline.'''
        c = self.c
        c.init_error_dialogs()
        c.atFileCommands.writeAll(writeAtFileNodesFlag=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20031218072017.1666: *4* fc.writeDirtyAtFileNodes
    @cmd('write-dirty-at-file-nodes')
    def writeDirtyAtFileNodes(self, event=None):
        '''Write all changed @file Nodes.'''
        c = self.c
        c.init_error_dialogs()
        c.atFileCommands.writeAll(writeDirtyAtFileNodesFlag=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20080801071227.6: *4* fc.writeDirtyAtShadowNodes
    def writeDirtyAtShadowNodes(self, event=None):
        '''Write all changed @shadow Nodes.'''
        self.c.atFileCommands.writeDirtyAtShadowNodes()
    #@+node:ekr.20031218072017.2013: *4* fc.writeMissingAtFileNodes
    @cmd('write-missing-at-file-nodes')
    def writeMissingAtFileNodes(self, event=None):
        '''Write all @file nodes for which the corresponding external file does not exist.'''
        c = self.c
        if c.p:
            c.atFileCommands.writeMissing(c.p)
    #@+node:ekr.20031218072017.3050: *4* fc.writeOutlineOnly
    @cmd('write-outline-only')
    def writeOutlineOnly(self, event=None):
        '''Write the entire outline without writing any derived files.'''
        c = self.c
        c.endEditing()
        self.write_Leo_file(self.mFileName, outlineOnlyFlag=True)
        g.blue('done')
    #@+node:ekr.20080805114146.2: *3* fc.Utils
    #@+node:ekr.20031218072017.1570: *4* fc.assignFileIndices & compactFileIndices
    def assignFileIndices(self):
        """Assign a file index to all tnodes"""
        pass # No longer needed: we assign indices as needed.
    # Indices are now immutable, so there is no longer any difference between these two routines.

    compactFileIndices = assignFileIndices
    #@+node:ekr.20080805085257.1: *4* fc.createUaList
    def createUaList(self, aList):
        '''Given aList of pairs (p,torv), return a list of pairs (torv,d)
        where d contains all picklable items of torv.unknownAttributes.'''
        result = []
        for p, torv in aList:
            if isinstance(torv.unknownAttributes, dict):
                # Create a new dict containing only entries that can be pickled.
                d = dict(torv.unknownAttributes) # Copy the dict.
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
        '''Pickle val and return the hexlified result.'''
        trace = False and g.unitTesting
        try:
            s = pickle.dumps(val, protocol=1)
            s2 = binascii.hexlify(s)
            s3 = g.ue(s2, 'utf-8')
            if trace: g.trace('\n',
                type(val), val, '\n', type(s), repr(s), '\n',
                type(s2), s2, '\n', type(s3), s3)
            field = ' %s="%s"' % (tag, s3)
            return field
        except pickle.PicklingError:
            if tag: # The caller will print the error if tag is None.
                g.warning("ignoring non-pickleable value", val, "in", torv)
            return ''
        except Exception:
            g.error("fc.pickle: unexpected exception in", torv)
            g.es_exception()
            return ''
    #@+node:ekr.20040701065235.2: *4* fc.putDescendentAttributes
    def putDescendentAttributes(self, p):

        # Create lists of all tnodes whose vnodes are marked or expanded.
        marks = []; expanded = []
        for p in p.subtree():
            v = p.v
            if p.isMarked() and p.v not in marks:
                marks.append(v)
            if p.hasChildren() and p.isExpanded() and v not in expanded:
                expanded.append(v)
        result = []
        for theList, tag in ((marks, "marks"), (expanded, "expanded")):
            if theList:
                sList = []
                for v in theList:
                    sList.append("%s," % v.fileIndex)
                s = ''.join(sList)
                # g.trace(tag,[str(p.h) for p in theList])
                result.append('\n%s="%s"' % (tag, s))
        return ''.join(result)
    #@+node:ekr.20080805071954.2: *4* fc.putDescendentVnodeUas
    def putDescendentVnodeUas(self, p):
        '''Return the a uA field for descendent VNode attributes,
        suitable for reconstituting uA's for anonymous vnodes.'''
        trace = False
        if trace: g.trace(p.h)
        # Create aList of tuples (p,v) having a valid unknownAttributes dict.
        # Create dictionary: keys are vnodes, values are corresonding archived positions.
        pDict = {}; aList = []
        for p2 in p.self_and_subtree():
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
            # g.trace(aList2)
            key = '.'.join(aList2)
            d[key] = d2
        if trace: g.trace(p.h, g.dictToString(d))
        # Pickle and hexlify d
        # pylint: disable=consider-using-ternary
        return d and self.pickle(
            torv=p.v, val=d, tag='descendentVnodeUnknownAttributes') or ''
    #@+node:ekr.20050418161620.2: *4* fc.putUaHelper
    def putUaHelper(self, torv, key, val):
        '''Put attribute whose name is key and value is val to the output stream.'''
        # New in 4.3: leave string attributes starting with 'str_' alone.
        if key.startswith('str_'):
            if g.isString(val) or g.isBytes(val):
                val = g.toUnicode(val)
                attr = ' %s="%s"' % (key, xml.sax.saxutils.escape(val))
                return attr
            else:
                g.trace(type(val), repr(val))
                g.warning("ignoring non-string attribute", key, "in", torv)
                return ''
        else:
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
        else:
            g.warning("ignoring non-dictionary unknownAttributes for", torv)
            return ''
    #@+node:ekr.20031218072017.3045: *4* fc.setDefaultDirectoryForNewFiles
    def setDefaultDirectoryForNewFiles(self, fileName):
        """Set c.openDirectory for new files for the benefit of leoAtFile.scanAllDirectives."""
        c = self.c
        if not c.openDirectory:
            theDir = g.os_path_dirname(fileName)
            if theDir and g.os_path_isabs(theDir) and g.os_path_exists(theDir):
                c.openDirectory = c.frame.openDirectory = theDir
    #@+node:ekr.20080412172151.2: *4* fc.updateFixedStatus
    def updateFixedStatus(self):
        c = self.c
        p = c.config.findSettingsPosition('@bool fixedWindow')
        if p:
            import leo.core.leoConfig as leoConfig
            parser = leoConfig.SettingsTreeParser(c)
            kind, name, val = parser.parseHeadline(p.h)
            if val and val.lower() in ('true', '1'):
                val = True
            else:
                val = False
            c.fixed = val
        # g.trace('c.fixed',c.fixed)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

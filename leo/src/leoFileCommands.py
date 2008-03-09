#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3018:@thin leoFileCommands.py
#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20050405141130:<< imports >>
import leoGlobals as g

if g.app and g.app.use_psyco:
    # print "enabled psyco classes",__file__
    try: from psyco.classes import *
    except ImportError: pass

import leoNodes

import binascii
import cStringIO
import os
import pickle
import string
import sys
import zipfile

try:
    # IronPython has problems with this.
    import xml.sax
    import xml.sax.saxutils
except Exception:
    pass

# The following is sometimes used.
# __pychecker__ = '--no-import'
# import time
#@nonl
#@-node:ekr.20050405141130:<< imports >>
#@nl

#@<< define exception classes >>
#@+node:ekr.20060918164811:<< define exception classes >>
class BadLeoFile(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self,message) # Init the base class.
    def __str__(self):
        return "Bad Leo File:" + self.message

class invalidPaste(Exception):
    pass
#@nonl
#@-node:ekr.20060918164811:<< define exception classes >>
#@nl

if sys.platform != 'cli':
    #@    << define sax classes >>
    #@+node:ekr.20060919145406:<< define sax classes >>
    #@+others
    #@+node:ekr.20060919110638.19:class saxContentHandler (XMLGenerator)
    class saxContentHandler (xml.sax.saxutils.XMLGenerator):

        '''A sax content handler class that reads Leo files.'''

        #@    @+others
        #@+node:ekr.20060919110638.20: __init__ & helpers
        def __init__ (self,c,fileName,silent):

            self.c = c
            self.fileName = fileName
            self.silent = silent

            # Init the base class.
            xml.sax.saxutils.XMLGenerator.__init__(self)

            #@    << define dispatch dict >>
            #@+node:ekr.20060919110638.21:<< define dispatch dict >>
            # There is no need for an 'end' method if all info is carried in attributes.

            self.dispatchDict = {
                'find_panel_settings':         (None,None),
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
            #@nonl
            #@-node:ekr.20060919110638.21:<< define dispatch dict >>
            #@nl

            self.printElements = [] # 'all', 'v'

            # Global attributes of the .leo file...
            # self.body_outline_ratio = '0.5'
            self.global_window_position = {}
            self.encoding = 'utf-8' 

            # Semantics...
            self.content = None
            self.currentNode = None
            self.elementStack = []
            self.errors = 0
            self.tnxToListDict = {} # Keys are tnx's (strings), values are *lists* of saxNodeClass objects.
            self.level = 0
            self.node = None
            self.nodeList = [] # List of saxNodeClass objects with the present tnode.
            self.nodeStack = []
            self.rootNode = None
            self.topNode = None
        #@nonl
        #@-node:ekr.20060919110638.20: __init__ & helpers
        #@+node:ekr.20060919110638.29: Do nothing
        def endElementNS(self,unused_name,unused_qname):
            g.trace(unused_name)

        def endDocument(self):
            pass

        def ignorableWhitespace(self,unused_whitespace):
            pass

        def skippedEntity(self,name):
            g.trace(name)

        def startElementNS(self,unused_name,unused_qname,unused_attrs):
            g.trace(unused_name)

        def startDocument(self):
            pass
        #@nonl
        #@-node:ekr.20060919110638.29: Do nothing
        #@+node:ekr.20060919134313: Utils
        #@+node:ekr.20060919110638.23:attrsToList
        def attrsToList (self,attrs):

            '''Convert the attributes to a list of g.Bunches.

            attrs: an Attributes item passed to startElement.'''

            if 1:
                for name in attrs.getNames():
                    val = attrs.getValue(name)
                    if type(val) != type(u''):
                        g.trace('Non-unicode attribute',name,val)

            # g.trace(g.listToString([repr() for name in attrs.getNames()]))

            return [
                g.Bunch(name=name,val=attrs.getValue(name))
                    for name in attrs.getNames()]
        #@nonl
        #@-node:ekr.20060919110638.23:attrsToList
        #@+node:ekr.20060919110638.26:error
        def error (self, message):

            print
            print
            print 'XML error: %s' % (message)
            print

            self.errors += 1
        #@nonl
        #@-node:ekr.20060919110638.26:error
        #@+node:ekr.20060919110638.27:inElement
        def inElement (self,name):

            return self.elementStack and name in self.elementStack
        #@nonl
        #@-node:ekr.20060919110638.27:inElement
        #@+node:ekr.20060919110638.28:printStartElement
        def printStartElement(self,name,attrs):

            indent = '\t' * self.level or ''

            if attrs.getLength() > 0:
                print '%s<%s %s>' % (
                    indent,
                    self.clean(name).strip(),
                    self.attrsToString(attrs,sep=' ')),
            else:
                print '%s<%s>' % (
                    indent,
                    self.clean(name).strip()),

            if name.lower() in ['v','t','vnodes','tnodes',]:
                print
        #@nonl
        #@+node:ekr.20060919110638.24:attrsToString
        def attrsToString (self,attrs,sep='\n'):

            '''Convert the attributes to a string.

            attrs: an Attributes item passed to startElement.

            sep: the separator charater between attributes.'''

            result = [
                '%s="%s"' % (bunch.name,bunch.val)
                for bunch in self.attrsToList(attrs)
            ]

            return sep.join(result)
        #@nonl
        #@-node:ekr.20060919110638.24:attrsToString
        #@+node:ekr.20060919110638.25:clean
        def clean(self,s):

            return g.toEncodedString(s,"ascii")
        #@nonl
        #@-node:ekr.20060919110638.25:clean
        #@-node:ekr.20060919110638.28:printStartElement
        #@-node:ekr.20060919134313: Utils
        #@+node:ekr.20060919110638.30:characters
        def characters(self,content):

            if content and type(content) != type(u''):
                g.trace('Non-unicode content',repr(content))

            content = content.replace('\r','')
            if not content: return

            elementName = self.elementStack and self.elementStack[-1].lower() or '<no element name>'

            if elementName in ('t','vh'):
                # if elementName == 'vh': g.trace(elementName,repr(content))
                self.content.append(content)

            elif content.strip():
                print 'unexpected content:',elementName,repr(content)
        #@nonl
        #@-node:ekr.20060919110638.30:characters
        #@+node:ekr.20060919110638.31:endElement & helpers
        def endElement(self,name):

            name = name.lower()
            if name in self.printElements or 'all' in self.printElements:
                indent = '\t' * (self.level-1) or ''
                print '%s</%s>' % (indent,self.clean(name).strip())

            data = self.dispatchDict.get(name)

            if data is None:
                if 0:
                    g.trace('unknown element',name)
            else:
                junk,func = data
                if func:
                    func()

            name2 = self.elementStack.pop()
            assert name == name2
        #@nonl
        #@+node:ekr.20060919110638.32:endTnode
        def endTnode (self):

            for node in self.nodeList:
                node.bodyString = ''.join(self.content)

            self.content = []
        #@nonl
        #@-node:ekr.20060919110638.32:endTnode
        #@+node:ekr.20060919110638.33:endVnode
        def endVnode (self):

            self.level -= 1
            self.node = self.nodeStack.pop()
        #@nonl
        #@-node:ekr.20060919110638.33:endVnode
        #@+node:ekr.20060919110638.34:endVH
        def endVH (self):

            if self.node:
                self.node.headString = ''.join(self.content)

            self.content = []
        #@nonl
        #@-node:ekr.20060919110638.34:endVH
        #@-node:ekr.20060919110638.31:endElement & helpers
        #@+node:ekr.20060919110638.45:getters
        def getCurrentNode (self):
            return self.currentNode

        def getRootNode (self):
            return self.rootNode

        def getTopNode (self):
            return self.topNode
        #@nonl
        #@-node:ekr.20060919110638.45:getters
        #@+node:ekr.20061004054323:processingInstruction (stylesheet)
        def processingInstruction (self,target,data):

            if target == 'xml-stylesheet':
                self.c.frame.stylesheet = data
                if not self.silent:
                    g.es('','%s: %s' % (target,data),color='blue')
            else:
                g.trace(target,data)
        #@nonl
        #@-node:ekr.20061004054323:processingInstruction (stylesheet)
        #@+node:ekr.20060919110638.35:startElement & helpers
        def startElement(self,name,attrs):

            name = name.lower()
            if name in self.printElements or 'all' in self.printElements:
                self.printStartElement(name,attrs)

            self.elementStack.append(name)

            data = self.dispatchDict.get(name)

            if data is None:
                if 0:
                    g.trace('unknown element',name)
            else:
                func,junk = data
                if func:
                    func(attrs)
        #@nonl
        #@+node:ekr.20060919110638.36:getPositionAttributes
        def getPositionAttributes (self,attrs):

            d = {}

            for bunch in self.attrsToList(attrs):
                name = bunch.name ; val = bunch.val
                if name in ('top','left','width','height'):
                    try:
                        d[name] = int(val)
                    except ValueError:
                        d[name] = 100 # A reasonable emergency default.
                else:
                    g.trace(name,len(val))

            return d
        #@nonl
        #@-node:ekr.20060919110638.36:getPositionAttributes
        #@+node:ekr.20060919110638.37:startGlobals
        def startGlobals (self,attrs):

            for bunch in self.attrsToList(attrs):
                name = bunch.name ; val = bunch.val

                if name == 'body_outline_ratio':
                    # self.body_outline_ratio = val
                    self.c.ratio = val
                    # g.trace(name,val)
                elif 0:
                    g.trace(name,len(val))
        #@nonl
        #@-node:ekr.20060919110638.37:startGlobals
        #@+node:ekr.20060919110638.38:startWinPos
        def startWinPos (self,attrs):

            self.global_window_position = self.getPositionAttributes(attrs)
        #@nonl
        #@-node:ekr.20060919110638.38:startWinPos
        #@+node:ekr.20060919110638.39:startLeoHeader
        def startLeoHeader (self,unused_attrs):

            self.tnxToListDict = {}
        #@-node:ekr.20060919110638.39:startLeoHeader
        #@+node:ekr.20060919110638.40:startVH
        def startVH (self,unused_attrs):

            self.content = []
        #@nonl
        #@-node:ekr.20060919110638.40:startVH
        #@+node:ekr.20060919112118:startVnodes
        def startVnodes (self,unused_attrs):

            # __pychecker__ = '--no-argsused'

            c = self.c ; d = self.global_window_position

            w = d.get('width',700)
            h = d.get('height',500)
            x = d.get('left',50)
            y = d.get('top',50)
            # g.trace(d,w,h,x,y)

            # Redraw the window before writing into it.
            c.frame.setTopGeometry(w,h,x,y)
            c.frame.deiconify()
            c.frame.lift()
            c.frame.update()

            # Causes window to appear.
            # g.trace('ratio',c.frame.ratio,c.frame.secondary_ratio)
            c.frame.resizePanesToRatio(c.frame.ratio,c.frame.secondary_ratio)
            if not self.silent and not g.unitTesting:
                g.es("reading:",self.fileName)
        #@nonl
        #@-node:ekr.20060919112118:startVnodes
        #@+node:ekr.20060919110638.41:startTnode
        def startTnode (self,attrs):

            if not self.inElement('tnodes'):
                self.error('<t> outside <tnodes>')

            self.content = []

            self.tnodeAttributes(attrs)
        #@nonl
        #@+node:ekr.20060919110638.42:tnodeAttributes
        def tnodeAttributes (self,attrs):

            # The tnode must have a tx attribute to associate content with the proper node.

            node = self.node
            self.nodeList = []

            for bunch in self.attrsToList(attrs):
                name = bunch.name ; val = bunch.val
                if name == 'tx':
                    self.nodeList = self.tnxToListDict.get(val,[])
                    if not self.nodeList:
                        self.error('Bad leo file: no node for <t tx=%s>' % (val))
                else:
                    node.tnodeAttributes[name] = val

            if not self.nodeList:
                self.error('Bad leo file: no tx attribute for tnode')
        #@nonl
        #@-node:ekr.20060919110638.42:tnodeAttributes
        #@-node:ekr.20060919110638.41:startTnode
        #@+node:ekr.20060919110638.43:startVnode
        def startVnode (self,attrs):

            if not self.inElement('vnodes'):
                self.error('<v> outside <vnodes>')

            if self.rootNode:
                parent = self.node
            else:
                self.rootNode = parent = saxNodeClass() # The dummy parent node.
                parent.headString = 'dummyNode'

            self.node = saxNodeClass()

            parent.children.append(self.node)
            self.vnodeAttributes(attrs)
            self.nodeStack.append(parent)

            return parent
        #@nonl
        #@+node:ekr.20060919110638.44:vnodeAttributes
        # The native attributes of <v> elements are a, t, vtag, tnodeList,
        # marks, expanded and descendentTnodeUnknownAttributes.

        def vnodeAttributes (self,attrs):

            node = self.node

            for bunch in self.attrsToList(attrs):
                name = bunch.name ; val = bunch.val
                if name == 't':
                    aList = self.tnxToListDict.get(val,[])
                    aList.append(self.node)
                    self.tnxToListDict[val] = aList
                    node.tnx = str(val) # nodeIndices.toString returns a string.
                else:
                    node.attributes[name] = val
        #@nonl
        #@-node:ekr.20060919110638.44:vnodeAttributes
        #@-node:ekr.20060919110638.43:startVnode
        #@-node:ekr.20060919110638.35:startElement & helpers
        #@-others
    #@nonl
    #@-node:ekr.20060919110638.19:class saxContentHandler (XMLGenerator)
    #@+node:ekr.20060919110638.15:class saxNodeClass
    class saxNodeClass:

        '''A class representing one <v> element.

        Use getters to access the attributes, properties and rules of this mode.'''

        #@    @+others
        #@+node:ekr.20060919110638.16: node.__init__
        def __init__ (self):

            self.attributes = {}
            self.bodyString = ''
            self.headString = ''
            self.children = []
            self.tnodeAttributes = {}
            self.tnodeList = []
            self.tnx = None
        #@nonl
        #@-node:ekr.20060919110638.16: node.__init__
        #@+node:ekr.20060919110638.17: node.__str__ & __repr__
        def __str__ (self):

            return '<v: %s>' % self.headString

        __repr__ = __str__
        #@nonl
        #@-node:ekr.20060919110638.17: node.__str__ & __repr__
        #@+node:ekr.20060919110638.18:node.dump
        def dump (self):

            print
            print 'node: tnx: %s body: %d %s' % (self.tnx,len(self.bodyString),self.headString)
            print 'children:',g.listToString([child for child in self.children])
            print 'attrs:',self.attributes.values()
        #@nonl
        #@-node:ekr.20060919110638.18:node.dump
        #@-others
    #@nonl
    #@-node:ekr.20060919110638.15:class saxNodeClass
    #@-others
    #@nonl
    #@-node:ekr.20060919145406:<< define sax classes >>
    #@nl

class baseFileCommands:
    """A base class for the fileCommands subcommander."""
    #@    @+others
    #@+node:ekr.20031218072017.3019:leoFileCommands._init_
    def __init__(self,c):

        # g.trace("__init__", "fileCommands.__init__")
        self.c = c
        self.frame = c.frame

        self.use_new_positions = False

        # New positions require the sax-based read code.
        self.use_sax = self.use_new_positions or c.config.getBool('use_sax_based_read')

        self.nativeTnodeAttributes = ('tx',)
        self.nativeVnodeAttributes = (
            'a','descendentTnodeUnknownAttributes',
            'expanded','marks','t','tnodeList',
            # 'vtag',
        )
        self.initIvars()

    def initIvars(self):

        # General
        c = self.c
        self.mFileName = ""
        self.fileDate = -1
        self.leo_file_encoding = c.config.new_leo_file_encoding
        # For reading
        self.checking = False # True: checking only: do *not* alter the outline.
        self.descendentExpandedList = []
        self.descendentMarksList = []
        self.forbiddenTnodes = []
        self.descendentUnknownAttributesDictList = []
        self.ratio = 0.5
        if self.use_sax:
            self.currentVnode = None
            self.rootVnode = None
        else:
            self.fileBuffer = None
            self.fileIndex = 0
            self.currentVnodeStack = [] # A stack of vnodes giving the current position.
            self.topVnodeStack     = [] # A stack of vnodes giving the top position.
            self.topPosition = None
        # For writing
        self.read_only = False
        self.rootPosition = None
        self.outputFile = None
        self.openDirectory = None
        self.putCount = 0
        self.topVnode = None
        self.toString = False
        self.usingClipboard = False
        self.currentPosition = None
        # New in 3.12
        self.copiedTree = None
        self.tnodesDict = {}
            # keys are gnx strings as returned by canonicalTnodeIndex.
            # Values are gnx's.
    #@nonl
    #@-node:ekr.20031218072017.3019:leoFileCommands._init_
    #@+node:ekr.20031218072017.3020:Reading
    #@+node:ekr.20060919104836: Top-level
    #@+node:ekr.20070919133659.1:checkLeoFile (fileCommands)
    def checkLeoFile (self,event=None):

        fc = self ; c = fc.c ; p = c.currentPosition()

        # Put the body (minus the @nocolor) into the file buffer.
        s = p.bodyString() ; tag = '@nocolor\n'
        if s.startswith(tag): s = s[len(tag):]
        self.fileBuffer = s ; self.fileIndex = 0

        # Do a trial read.
        self.checking = True
        self.initReadIvars()
        c.loading = True # disable c.changed
        try:
            try:
                self.getAllLeoElements(fileName='check-leo-file',silent=False)
                g.es_print('check-leo-file passed',color='blue')
            except BadLeoFile, message:
                # g.es_exception()
                g.es_print('check-leo-file failed:',str(message),color='red')
        finally:
            self.checking = False
            c.loading = False # reenable c.changed
    #@-node:ekr.20070919133659.1:checkLeoFile (fileCommands)
    #@+node:ekr.20031218072017.1559:getLeoOutlineFromClipboard & helpers
    def getLeoOutlineFromClipboard (self,s,reassignIndices=True):

        '''Read a Leo outline from string s in clipboard format.'''

        try:
            v = self.getLeoOutlineHelper(s,reassignIndices,checking=True)
            v = self.getLeoOutlineHelper(s,reassignIndices,checking=False)
        except invalidPaste:
            v = None
            g.es("invalid Paste As Clone",color="blue")
        except BadLeoFile:
            v = None
            g.es("the clipboard is not valid ",color="blue")

        return v

    getLeoOutline = getLeoOutlineFromClipboard # for compatibility
    #@nonl
    #@+node:ekr.20031218072017.1557:finishPaste
    def finishPaste(self,reassignIndices=True):

        """Finish pasting an outline from the clipboard.

        Retain clone links if reassignIndices is False."""

        c = self.c
        current = c.currentPosition()
        if reassignIndices:
            #@        << reassign tnode indices >>
            #@+node:ekr.20031218072017.1558:<< reassign tnode indices >>
            # We must *reassign* indices here so no "False clones" are created.

            nodeIndices = g.app.nodeIndices

            current.clearVisitedInTree()

            for p in current.self_and_subtree_iter():
                t = p.v.t
                if not t.isVisited():
                    t.setVisited()
                    t.fileIndex = nodeIndices.getNewIndex()
            #@-node:ekr.20031218072017.1558:<< reassign tnode indices >>
            #@nl
        c.selectPosition(current)
        return current
    #@-node:ekr.20031218072017.1557:finishPaste
    #@+node:ekr.20060826052453.1:getLeoOutlineHelper
    def getLeoOutlineHelper (self,s,reassignIndices,checking):

        self.checking = checking
        self.usingClipboard = True
        self.fileBuffer = s ; self.fileIndex = 0
        self.descendentUnknownAttributesDictList = []
        v = None

        self.tnodesDict = {}
        if not reassignIndices:
            #@        << recreate tnodesDict >>
            #@+node:EKR.20040610134756:<< recreate tnodesDict >>
            nodeIndices = g.app.nodeIndices

            self.tnodesDict = {}

            for t in self.c.all_unique_tnodes_iter():
                if hasattr(t,'fileIndex'):
                    tref = t.fileIndex
                    if nodeIndices.isGnx(tref):
                        tref = nodeIndices.toString(tref)
                    self.tnodesDict[tref] = t

            if 0:
                print '-'*40
                for key in self.tnodesDict.keys():
                    print key,self.tnodesDict[key]
            #@-node:EKR.20040610134756:<< recreate tnodesDict >>
            #@nl
        try:
            self.getXmlVersionTag()
            self.getXmlStylesheetTag()
            self.getTag("<leo_file>")
            self.getClipboardHeader()
            self.getDummyElements()
            self.getVnodes(reassignIndices)
            self.getTnodes()
            self.getTag("</leo_file>")
            if not checking:
                v = self.finishPaste(reassignIndices)
        finally:
            self.fileBuffer = None ; self.fileIndex = 0
            self.usingClipboard = False
            self.tnodesDict = {}
        return v
    #@-node:ekr.20060826052453.1:getLeoOutlineHelper
    #@+node:ekr.20031218072017.3022:getClipboardHeader
    def getClipboardHeader (self):

        if self.getOpenTag("<leo_header"):
            return # <leo_header> or <leo_header/> has been seen.

        while 1:
            if self.matchTag("file_format="):
                self.getDquote() ; self.getLong() ; self.getDquote()
            elif self.matchTag("tnodes="):
                self.getDquote() ; self.getLong() ; self.getDquote() # no longer used
            elif self.matchTag("max_tnode_index="):
                self.getDquote() ; self.getLong() ; self.getDquote() # no longer used
            elif self.matchTag("></leo_header>"): # new in 4.2: allow this form.
                break
            else:
                self.getTag("/>")
                break
    #@nonl
    #@-node:ekr.20031218072017.3022:getClipboardHeader
    #@-node:ekr.20031218072017.1559:getLeoOutlineFromClipboard & helpers
    #@+node:ekr.20031218072017.1553:getLeoFile
    # The caller should enclose this in begin/endUpdate.

    def getLeoFile (self,theFile,fileName,readAtFileNodesFlag=True,silent=False):

        c = self.c
        c.setChanged(False) # May be set when reading @file nodes.
        #@    << warn on read-only files >>
        #@+node:ekr.20031218072017.1554:<< warn on read-only files >>
        # os.access may not exist on all platforms.

        try:
            self.read_only = not os.access(fileName,os.W_OK)
        except AttributeError:
            self.read_only = False
        except UnicodeError:
            self.read_only = False

        if self.read_only:
            g.es("read only:",fileName,color="red")
        #@-node:ekr.20031218072017.1554:<< warn on read-only files >>
        #@nl
        self.checking = False
        self.mFileName = c.mFileName
        self.initReadIvars()
        c.loading = True # disable c.changed

        try:
            ok = True
            # t1 = time.clock()
            if self.use_sax:
                v = self.readSaxFile(theFile,fileName,silent)
                if v: # v == None for minimal .leo files.
                    c.setRootVnode(v)
                    self.rootVnode = v
                else:
                    self.rootVnode = c.rootPosition().v
            else:
                self.getAllLeoElements(fileName,silent)
            # t2 = time.clock()
            # g.trace('time',t2-t1)
        except BadLeoFile, message:
            if not silent:
                g.es_exception()
                g.alert(self.mFileName + " is not a valid Leo file: " + str(message))
            ok = False

        # New in Leo 4.2.2: before reading derived files.
        if self.use_sax:
            self.resolveTnodeLists()
        if ok and readAtFileNodesFlag:
            # Redraw before reading the @file nodes so the screen isn't blank.
            # This is important for big files like LeoPy.leo.
            c.redraw_now()
            c.atFileCommands.readAll(c.rootVnode(),partialFlag=False)

        # Do this after reading derived files.
        if readAtFileNodesFlag:
            # The descendent nodes won't exist unless we have read the @thin nodes!
            self.restoreDescendentAttributes()
        if self.use_sax:
            self.setPositionsFromVnodes()
        else:
            if not self.usingClipboard:
                self.setPositionsFromStacks()
            if not c.currentPosition():
                c.setCurrentPosition(c.rootPosition())

        c.selectVnode(c.currentPosition()) # load body pane
        c.loading = False # reenable c.changed
        c.setChanged(c.changed) # Refresh the changed marker.
        self.initReadIvars()
        return ok, self.ratio
    #@nonl
    #@-node:ekr.20031218072017.1553:getLeoFile
    #@+node:ekr.20031218072017.2009:newTnode
    def newTnode(self,index):

        if self.tnodesDict.has_key(index):
            g.es("bad tnode index:",str(index),"using empty text.")
            return leoNodes.tnode()
        else:
            # Create the tnode.  Use the _original_ index as the key in tnodesDict.
            t = leoNodes.tnode()
            self.tnodesDict[index] = t

            if type(index) not in (type(""),type(u"")):
                g.es("newTnode: unexpected index type:",type(index),index,color="red")

            # Convert any pre-4.1 index to a gnx.
            junk,theTime,junk = gnx = g.app.nodeIndices.scanGnx(index,0)
            if theTime != None:
                t.setFileIndex(gnx)

            return t
    #@-node:ekr.20031218072017.2009:newTnode
    #@+node:ekr.20031218072017.3029:readAtFileNodes (fileCommands)
    def readAtFileNodes (self):

        c = self.c ; p = c.currentPosition()

        c.beginUpdate()
        try:
            c.atFileCommands.readAll(p,partialFlag=True)
        finally:
            c.endUpdate()

        # Force an update of the body pane.
        c.setBodyString(p,p.bodyString())
        c.frame.body.onBodyChanged(undoType=None)
    #@-node:ekr.20031218072017.3029:readAtFileNodes (fileCommands)
    #@+node:ekr.20031218072017.2297:open (leoFileCommands)
    def open(self,theFile,fileName,readAtFileNodesFlag=True,silent=False):

        c = self.c ; frame = c.frame
        if not self.use_sax:
            #@        << read the entire file into the buffer >>
            #@+node:ekr.20070412103240:<< read the entire file into the buffer >>
            isZipped = zipfile.is_zipfile(fileName)

            if isZipped:
                aList = theFile.infolist()
                contentsName = aList[0].filename
                self.fileBuffer = theFile.read(contentsName)
            else:
                self.fileBuffer = theFile.read()
            #@-node:ekr.20070412103240:<< read the entire file into the buffer >>
            #@nl
            theFile.close()
            self.fileIndex = 0
        #@    << Set the default directory >>
        #@+node:ekr.20031218072017.2298:<< Set the default directory >>
        #@+at 
        #@nonl
        # The most natural default directory is the directory containing the 
        # .leo file that we are about to open.  If the user has specified the 
        # "Default Directory" preference that will over-ride what we are about 
        # to set.
        #@-at
        #@@c

        theDir = g.os_path_dirname(fileName)

        if len(theDir) > 0:
            c.openDirectory = theDir
        #@-node:ekr.20031218072017.2298:<< Set the default directory >>
        #@nl
        self.topPosition = None
        ok, ratio = self.getLeoFile(
            theFile,fileName,
            readAtFileNodesFlag=readAtFileNodesFlag,
            silent=silent)
        frame.resizePanesToRatio(ratio,frame.secondary_ratio)
        if 0: # 1/30/04: this is useless.
            if self.topPosition: 
                c.setTopVnode(self.topPosition)
        if not self.use_sax: # Delete the file buffer
            self.fileBuffer = ""
        return ok
    #@nonl
    #@-node:ekr.20031218072017.2297:open (leoFileCommands)
    #@+node:ekr.20031218072017.3030:readOutlineOnly
    def readOutlineOnly (self,theFile,fileName):

        c = self.c
        # Read the entire file into the buffer
        self.fileBuffer = theFile.read() ; theFile.close()
        self.fileIndex = 0
        #@    << Set the default directory >>
        #@+node:ekr.20071211134300:<< Set the default directory >>
        #@+at 
        #@nonl
        # The most natural default directory is the directory containing the 
        # .leo file that we are about to open.  If the user has specified the 
        # "Default Directory" preference that will over-ride what we are about 
        # to set.
        #@-at
        #@@c

        theDir = g.os_path_dirname(fileName)

        if len(theDir) > 0:
            c.openDirectory = theDir
        #@-node:ekr.20071211134300:<< Set the default directory >>
        #@nl
        c.beginUpdate()
        try:
            ok, ratio = self.getLeoFile(theFile,fileName,readAtFileNodesFlag=False)
        finally:
            c.endUpdate()
        c.frame.deiconify()
        junk,junk,secondary_ratio = self.frame.initialRatios()
        c.frame.resizePanesToRatio(ratio,secondary_ratio)
        if 0: # 1/30/04: this is useless.
            # This should be done after the pane size has been set.
            if self.topPosition:
                c.frame.tree.setTopPosition(self.topPosition)
                c.redraw_now()
        # delete the file buffer
        self.fileBuffer = ""
        return ok
    #@-node:ekr.20031218072017.3030:readOutlineOnly
    #@-node:ekr.20060919104836: Top-level
    #@+node:ekr.20060919133249:Common
    # Methods common to both the sax and non-sax code.
    #@nonl
    #@+node:ekr.20031218072017.2004:canonicalTnodeIndex
    def canonicalTnodeIndex(self,index):

        """Convert Tnnn to nnn, leaving gnx's unchanged."""

        # index might be Tnnn, nnn, or gnx.
        junk,theTime,junk = g.app.nodeIndices.scanGnx(index,0)
        if theTime == None: # A pre-4.1 file index.
            if index[0] == "T":
                index = index[1:]

        return index
    #@-node:ekr.20031218072017.2004:canonicalTnodeIndex
    #@+node:ekr.20040701065235.1:getDescendentAttributes
    def getDescendentAttributes (self,s,tag=""):

        '''s is a list of gnx's, separated by commas from a <v> or <t> element.
        Parses s into a list.

        This is used to record marked and expanded nodes.
        '''

        # __pychecker__ = '--no-argsused' # tag used only for debugging.

        gnxs = s.split(',')
        result = [gnx for gnx in gnxs if len(gnx) > 0]
        # g.trace(tag,result)
        return result
    #@-node:ekr.20040701065235.1:getDescendentAttributes
    #@+node:EKR.20040627114602:getDescendentUnknownAttributes
    # Only @thin vnodes have the descendentTnodeUnknownAttributes field.
    # The question is: what are we to do about this?

    def getDescendentUnknownAttributes (self,s):

        try:
            bin = binascii.unhexlify(s) # Throws a TypeError if val is not a hex string.
            val = pickle.loads(bin)
            return val

        except (TypeError,pickle.UnpicklingError,ImportError):
            g.trace('Can not unpickle',s)
            return None
    #@-node:EKR.20040627114602:getDescendentUnknownAttributes
    #@+node:ekr.20060919142200.1:initReadIvars
    def initReadIvars (self):

        self.descendentUnknownAttributesDictList = []
        self.descendentExpandedList = []
        self.descendentMarksList = []
        self.tnodesDict = {}
    #@nonl
    #@-node:ekr.20060919142200.1:initReadIvars
    #@+node:EKR.20040627120120:restoreDescendentAttributes
    def restoreDescendentAttributes (self):

        c = self.c ; verbose = True 

        for resultDict in self.descendentUnknownAttributesDictList:
            for gnx in resultDict.keys():
                tref = self.canonicalTnodeIndex(gnx)
                t = self.tnodesDict.get(tref)
                if t:
                    t.unknownAttributes = resultDict[gnx]
                    t._p_changed = 1
                elif verbose:
                    g.trace('can not find tnode (duA): gnx = %s' % gnx,color='red')
        marks = {} ; expanded = {}
        for gnx in self.descendentExpandedList:
            tref = self.canonicalTnodeIndex(gnx)
            t = self.tnodesDict.get(gnx)
            if t: expanded[t]=t
            elif verbose:
                g.trace('can not find tnode (expanded): gnx = %s, tref: %s' % (gnx,tref),color='red')

        for gnx in self.descendentMarksList:
            tref = self.canonicalTnodeIndex(gnx)
            t = self.tnodesDict.get(gnx)
            if t: marks[t]=t
            elif verbose:
                g.trace('can not find tnode (marks): gnx = %s tref: %s' % (gnx,tref),color='red')

        if marks or expanded:
            # g.trace('marks',len(marks),'expanded',len(expanded))
            for p in c.all_positions_iter():
                if marks.get(p.v.t):
                    p.v.initMarkedBit()
                        # This was the problem: was p.setMark.
                        # There was a big performance bug in the mark hook in the Node Navigator plugin.
                if expanded.get(p.v.t):
                    p.expand()
    #@-node:EKR.20040627120120:restoreDescendentAttributes
    #@-node:ekr.20060919133249:Common
    #@+node:ekr.20031218072017.3021:Non-sax
    #@+node:ekr.20040326052245:convertStackToPosition
    def convertStackToPosition (self,stack):

        c = self.c ; p2 = None
        if not stack: return None

        for p in c.allNodes_iter():
            if p.v == stack[0]:
                p2 = p.copy()
                for n in xrange(len(stack)):
                    if not p2: break
                    # g.trace("compare",n,p2.v,stack[n])
                    if p2.v != stack[n]:
                        p2 = None
                    elif n + 1 == len(stack):
                        break
                    else:
                        p2.moveToParent()
                if p2:
                    return p

        return None
    #@-node:ekr.20040326052245:convertStackToPosition
    #@+node:ekr.20031218072017.1243:get, match & skip (basic)
    #@+node:ekr.20031218072017.1244:get routines (basic)
    #@+node:EKR.20040526204706:getBool
    def getBool (self):

        self.skipWs() # guarantees at least one more character.
        ch = self.fileBuffer[self.fileIndex]
        if ch == '0':
            self.fileIndex += 1 ; return False
        elif ch == '1':
            self.fileIndex += 1 ; return True
        else:
            raise BadLeoFile("expecting bool constant")
    #@-node:EKR.20040526204706:getBool
    #@+node:EKR.20040526204706.1:getDouble
    def getDouble (self):

        self.skipWs()
        i = self.fileIndex ; buf = self.fileBuffer
        floatChars = 'eE.+-'
        n = len(buf)
        while i < n and (buf[i].isdigit() or buf[i] in floatChars):
            i += 1
        if i == self.fileIndex:
            raise BadLeoFile("expecting float constant")
        val = float(buf[self.fileIndex:i])
        self.fileIndex = i
        return val
    #@-node:EKR.20040526204706.1:getDouble
    #@+node:EKR.20040526204706.2:getDqBool
    def getDqBool (self):

        self.getDquote()
        val = self.getBool()
        self.getDquote()
        return val
    #@-node:EKR.20040526204706.2:getDqBool
    #@+node:EKR.20040526204706.3:getDqString
    def getDqString (self):

        self.getDquote()
        i = self.fileIndex
        self.fileIndex = j = string.find(self.fileBuffer,'"',i)
        if j == -1: raise BadLeoFile("unterminated double quoted string")
        s = self.fileBuffer[i:j]
        self.getDquote()
        return s
    #@-node:EKR.20040526204706.3:getDqString
    #@+node:EKR.20040526204706.4:getDquote
    def getDquote (self):

        self.getTag('"')
    #@-node:EKR.20040526204706.4:getDquote
    #@+node:ekr.20031218072017.3024:getEscapedString
    def getEscapedString (self):

        # The next '<' begins the ending tag.
        i = self.fileIndex
        self.fileIndex = j = string.find(self.fileBuffer,'<',i)
        if j == -1:
            print self.fileBuffer[i:]
            raise BadLeoFile("unterminated escaped string")
        else:
            # Allocates memory
            return self.xmlUnescape(self.fileBuffer[i:j])
    #@-node:ekr.20031218072017.3024:getEscapedString
    #@+node:EKR.20040526204706.5:getIndex
    def getIndex (self):

        val = self.getLong()
        if val < 0: raise BadLeoFile("expecting index")
        return val
    #@-node:EKR.20040526204706.5:getIndex
    #@+node:EKR.20040526204706.6:getLong
    def getLong (self):

        self.skipWs() # guarantees at least one more character.
        i = self.fileIndex
        if self.fileBuffer[i] == u'-':
            i += 1
        n = len(self.fileBuffer)
        while i < n and self.fileBuffer[i].isdigit():
            i += 1
        if i == self.fileIndex:
            raise BadLeoFile("expecting int constant")
        val = int(self.fileBuffer[self.fileIndex:i])
        self.fileIndex = i
        return val
    #@-node:EKR.20040526204706.6:getLong
    #@+node:EKR.20040526204706.7:getOpenTag
    def getOpenTag (self,tag):

        """
        Look ahead for collapsed tag: tag may or may not end in ">"
        Skips tag and /> if found, otherwise does not alter index.
        Returns True if the closing part was found.
        Throws BadLeoFile if the tag does not exist.
        """

        if tag[-1] == ">":
            # Only the tag itself or a collapsed tag are valid.
            if self.matchTag(tag):
                return False # Not a collapsed tag.
            elif self.matchTag(tag[:-1]):
                # It must be a collapsed tag.
                self.skipWs()
                if self.matchTag("/>"):
                    return True
            print "getOpenTag(", tag, ") failed:"
            raise BadLeoFile("expecting" + tag)
        else:
            # The tag need not be followed by "/>"
            if self.matchTag(tag):
                old_index = self.fileIndex
                self.skipWs()
                if self.matchTag("/>"):
                    return True
                else:
                    self.fileIndex = old_index
                    return False
            else:
                print "getOpenTag(", tag, ") failed:"
                raise BadLeoFile("expecting" + tag)
    #@-node:EKR.20040526204706.7:getOpenTag
    #@+node:EKR.20040526204706.8:getStringToTag
    def getStringToTag (self,tag):

        buf = self.fileBuffer
        blen = len(buf) ; tlen = len(tag)
        i = j = self.fileIndex
        while i < blen:
            if tag == buf[i:i+tlen]:
                self.fileIndex = i
                return buf[j:i]
            else: i += 1

        raise BadLeoFile("expecting string terminated by " + tag)
    #@-node:EKR.20040526204706.8:getStringToTag
    #@+node:EKR.20040526204706.9:getTag
    def getTag (self,tag):

        """
        Look ahead for closing />
        Return True if found.
        """

        if self.matchTag(tag):
            return
        else:
            print "getTag(", tag, ") failed:"
            raise BadLeoFile("expecting" + tag)
    #@-node:EKR.20040526204706.9:getTag
    #@+node:EKR.20040526204036:getUnknownTag
    def getUnknownTag(self):

        self.skipWsAndNl() # guarantees at least one more character.
        tag = self.getStringToTag('=')
        if not tag:
            print "getUnknownTag failed"
            raise BadLeoFile("unknown tag not followed by '='")

        self.fileIndex += 1
        val = self.getDqString()
        # g.trace(tag,val)
        return tag,val
    #@-node:EKR.20040526204036:getUnknownTag
    #@-node:ekr.20031218072017.1244:get routines (basic)
    #@+node:ekr.20031218072017.1245:match routines
    def matchChar (self,ch):
        self.skipWs() # guarantees at least one more character.
        if ch == self.fileBuffer[self.fileIndex]:
            self.fileIndex += 1 ; return True
        else: return False

    # Warning: does not check for end-of-word,
    # so caller must match prefixes first.
    def matchTag (self,tag):
        self.skipWsAndNl() # guarantees at least one more character.
        i = self.fileIndex
        if tag == self.fileBuffer[i:i+len(tag)]:
            self.fileIndex += len(tag)
            return True
        else:
            return False

    def matchTagWordIgnoringCase (self,tag):
        self.skipWsAndNl() # guarantees at least one more character.
        i = self.fileIndex
        tag = string.lower(tag)
        j = g.skip_c_id(self.fileBuffer,i)
        word = self.fileBuffer[i:j]
        word = string.lower(word)
        if tag == word:
            self.fileIndex += len(tag)
            return True
        else:
            return False
    #@-node:ekr.20031218072017.1245:match routines
    #@+node:ekr.20031218072017.3027:skipWs
    def skipWs (self):

        while self.fileIndex < len(self.fileBuffer):
            ch = self.fileBuffer[self.fileIndex]
            if ch == ' ' or ch == '\t':
                self.fileIndex += 1
            else: break

        # The caller is entitled to get the next character.
        if  self.fileIndex >= len(self.fileBuffer):
            raise BadLeoFile("")
    #@-node:ekr.20031218072017.3027:skipWs
    #@+node:ekr.20031218072017.3028:skipWsAndNl
    def skipWsAndNl (self):

        while self.fileIndex < len(self.fileBuffer):
            ch = self.fileBuffer[self.fileIndex]
            if ch == ' ' or ch == '\t' or ch == '\r' or ch == '\n':
                self.fileIndex += 1
            else: break

        # The caller is entitled to get the next character.
        if  self.fileIndex >= len(self.fileBuffer):
            raise BadLeoFile("")
    #@-node:ekr.20031218072017.3028:skipWsAndNl
    #@+node:ekr.20031218072017.3031:xmlUnescape
    def xmlUnescape(self,s):

        if s:
            s = string.replace(s, '\r', '')
            s = string.replace(s, "&lt;", '<')
            s = string.replace(s, "&gt;", '>')
            s = string.replace(s, "&amp;", '&')
        return s
    #@-node:ekr.20031218072017.3031:xmlUnescape
    #@-node:ekr.20031218072017.1243:get, match & skip (basic)
    #@+node:ekr.20031218072017.1555:getAllLeoElements
    def getAllLeoElements (self,fileName,silent):
        c = self.c

        self.getXmlVersionTag()
        self.getXmlStylesheetTag()

        self.getTag("<leo_file>") # Must match exactly.
        self.getLeoHeader()
        self.getGlobals()
        self.getPrefs()
        self.getFindPanelSettings()

        # Causes window to appear.
        c.frame.resizePanesToRatio(c.frame.ratio,c.frame.secondary_ratio)
        if not silent and not g.unitTesting:
            g.es("reading:",fileName)

        self.getVnodes()
        self.getTnodes()
        self.getCloneWindows()
        self.getTag("</leo_file>")
    #@nonl
    #@-node:ekr.20031218072017.1555:getAllLeoElements
    #@+node:ekr.20031218072017.3023:getCloneWindows
    # For compatibility with old file formats.

    def getCloneWindows (self):

        if not self.matchTag("<clone_windows>"):
            return # <clone_windows/> seen.

        while self.matchTag("<clone_window vtag=\"V"):
            self.getLong() ; self.getDquote() ; self.getTag(">")
            if not self.getOpenTag("<global_window_position"):
                self.getTag("<global_window_position")
                self.getPosition()
                self.getTag("/>")
            self.getTag("</clone_window>")
        self.getTag("</clone_windows>")
    #@-node:ekr.20031218072017.3023:getCloneWindows
    #@+node:ekr.20061209141653:getDummyElements
    def getDummyElements (self):

        # New in Leo 4.4.3: Ignore the dummy elements that allow
        # Pasted Leo outlines to be valid .leo files.
        while 1:
            for tag in ('<globals','<preferences','<find_panel_settings'):
                if self.matchTag(tag) and self.matchTag('/>'):
                    break
            else:
                break
    #@-node:ekr.20061209141653:getDummyElements
    #@+node:ekr.20031218072017.2064:getFindPanelSettings
    def getFindPanelSettings (self):

        if self.getOpenTag("<find_panel_settings"):
            return # <find_panel_settings/> seen.

        # New in 4.3: ignore all pre-4.3 find settings.
        while 1:
            if   self.matchTag("batch="):           self.getDqBool()
            elif self.matchTag("ignore_case="):     self.getDqBool()
            elif self.matchTag("mark_changes="):    self.getDqBool()
            elif self.matchTag("mark_finds="):      self.getDqBool()
            elif self.matchTag("node_only="):       self.getDqBool()
            elif self.matchTag("pattern_match="):   self.getDqBool()
            elif self.matchTag("reverse="):         self.getDqBool()
            elif self.matchTag("script_change="):   self.getDqBool()
            elif self.matchTag("script_search="):   self.getDqBool()
            elif self.matchTag("search_headline="): self.getDqBool()
            elif self.matchTag("search_body="):     self.getDqBool()
            elif self.matchTag("selection_only="):  self.getDqBool()
            elif self.matchTag("suboutline_only="): self.getDqBool()
            elif self.matchTag("whole_word="):      self.getDqBool()
            elif self.matchTag("wrap="):            self.getDqBool()
            elif self.matchTag(">"): break
            else: self.getUnknownTag() # Ignore all other tags.
        # Allow only <find_string> or <find_string/>
        if self.getOpenTag("<find_string>"): 
            pass
        else:
            self.getEscapedString() ; self.getTag("</find_string>")
        # Allow only <change_string> or <change_string/>
        if self.getOpenTag("<change_string>"): 
            pass
        else:
            self.getEscapedString() ; self.getTag("</change_string>")
        self.getTag("</find_panel_settings>")
    #@-node:ekr.20031218072017.2064:getFindPanelSettings
    #@+node:ekr.20031218072017.2306:getGlobals
    def getGlobals (self):

        if self.getOpenTag("<globals"):
            # <globals/> seen: set reasonable defaults:
            self.ratio = 0.5
            y,x,h,w = 50,50,500,700
        else:
            self.getTag("body_outline_ratio=\"")
            self.ratio = self.getDouble() ; self.getDquote() ; self.getTag(">")

            self.getTag("<global_window_position")
            y,x,h,w = self.getPosition()
            self.getTag("/>")

            self.getTag("<global_log_window_position")
            self.getPosition()
            self.getTag("/>") # no longer used.

            self.getTag("</globals>")

        # Redraw the window before writing into it.
        self.frame.setTopGeometry(w,h,x,y)
        self.frame.deiconify()
        self.frame.lift()
        self.frame.update()
    #@-node:ekr.20031218072017.2306:getGlobals
    #@+node:ekr.20031218072017.1970:getLeoHeader
    def getLeoHeader (self):

        if self.getOpenTag("<leo_header"):
            return # <leo_header/> seen.

        # New in version 1.7: attributes may appear in any order.
        while 1:
            if self.matchTag("file_format="):
                self.getDquote() ; self.getLong() ; self.getDquote()
            elif self.matchTag("tnodes="):
                self.getDquote() ; self.getLong() ; self.getDquote()
            elif self.matchTag("max_tnode_index="):
                self.getDquote() ; self.getLong() ; self.getDquote()
            elif self.matchTag("clone_windows="):
                self.getDquote() ; self.getLong() ; self.getDquote() # no longer used.
            elif self.matchTag("></leo_header>"): # new in 4.2: allow this form.
                break
            else:
                self.getTag("/>")
                break
    #@-node:ekr.20031218072017.1970:getLeoHeader
    #@+node:ekr.20031218072017.3025:getPosition
    def getPosition (self):

        top = left = height = width = 0
        # New in version 1.7: attributes may appear in any order.
        while 1:
            if self.matchTag("top=\""):
                top = self.getLong() ; self.getDquote()
            elif self.matchTag("left=\""):
                left = self.getLong() ; self.getDquote()
            elif self.matchTag("height=\""):
                height = self.getLong() ; self.getDquote()
            elif self.matchTag("width=\""):
                width = self.getLong() ; self.getDquote()
            else: break
        return top, left, height, width
    #@-node:ekr.20031218072017.3025:getPosition
    #@+node:ekr.20031218072017.2062:getPrefs
    # Note: Leo 4.3 does not write these settings to local .leo files.
    # Instead, corresponding settings are contained in leoConfig.leo files.

    def getPrefs (self):

        c = self.c

        if self.getOpenTag("<preferences"):
            return # <preferences/> seen

        table = (
            ("allow_rich_text",None,None), # Ignored.
            ("tab_width","tab_width",self.getLong),
            ("page_width","page_width",self.getLong),
            ("tangle_bat","tangle_batch_flag",self.getBool),
            ("untangle_bat","untangle_batch_flag",self.getBool),
            ("output_doc_chunks","output_doc_flag",self.getBool),
            ("noweb_flag",None,None), # Ignored.
            ("extended_noweb_flag",None,None), # Ignored.
            ("defaultTargetLanguage","target_language",self.getTargetLanguage),
            ("use_header_flag","use_header_flag",self.getBool))

        done = False
        while 1:
            found = False
            for tag,var,f in table:
                if self.matchTag("%s=" % tag):
                    if var:
                        self.getDquote() ; val = f() ; self.getDquote()
                        setattr(c,var,val)
                        # g.trace(var,val)
                    else:
                        self.getDqString()
                    found = True ; break
            if not found:
                if self.matchTag("/>"):
                    done = True ; break
                if self.matchTag(">"):
                    break
                else: # New in 4.1: ignore all other tags.
                    self.getUnknownTag()

        if not done:
            while 1:
                if self.matchTag("<defaultDirectory>"):
                    # New in version 0.16.
                    c.tangle_directory = self.getEscapedString()
                    self.getTag("</defaultDirectory>")
                    if not g.os_path_exists(c.tangle_directory):
                        g.es("default tangle directory not found:",c.tangle_directory)
                elif self.matchTag("<TSyntaxMemo_options>"):
                    self.getEscapedString() # ignored
                    self.getTag("</TSyntaxMemo_options>")
                else: break
            self.getTag("</preferences>")
    #@+node:ekr.20031218072017.2063:getTargetLanguage
    def getTargetLanguage (self):

        # Must match longer tags before short prefixes.
        for name in g.app.language_delims_dict.keys():
            if self.matchTagWordIgnoringCase(name):
                language = name.replace("/","")
                # self.getDquote()
                return language

        return "c" # default
    #@-node:ekr.20031218072017.2063:getTargetLanguage
    #@-node:ekr.20031218072017.2062:getPrefs
    #@+node:ekr.20031218072017.3026:getSize (not used!)
    def getSize (self):

        # New in version 1.7: attributes may appear in any order.
        height = 0 ; width = 0
        while 1:
            if self.matchTag("height=\""):
                height = self.getLong() ; self.getDquote()
            elif self.matchTag("width=\""):
                width = self.getLong() ; self.getDquote()
            else: break
        return height, width
    #@-node:ekr.20031218072017.3026:getSize (not used!)
    #@+node:ekr.20031218072017.1561:getTnode
    def getTnode (self):

        # we have already matched <t.
        index = -1 ; attrDict = {}

        # New in Leo 4.4: support collapsed tnodes.
        if self.matchTag('/>'): # A collapsed tnode.
            return

        # Attributes may appear in any order.
        while 1:
            if self.matchTag("tx="):
                # New for 4.1.  Read either "Tnnn" or "gnx".
                index = self.getDqString()
            elif self.matchTag("rtf=\"1\""): pass # ignored
            elif self.matchTag("rtf=\"0\""): pass # ignored
            elif self.matchTag(">"):         break
            else: # New for 4.0: allow unknown attributes.
                # New in 4.2: allow pickle'd and hexlify'ed values.
                attr,val = self.getUa("tnode")
                if attr: attrDict[attr] = val

        # index might be Tnnn, nnn, or gnx.
        junk,theTime,junk = g.app.nodeIndices.scanGnx(index,0)
        if theTime == None: # A pre-4.1 file index.
            if index[0] == "T":
                index = index[1:]

        index = self.canonicalTnodeIndex(index)
        t = self.tnodesDict.get(index)
        if t:
            #@        << handle unknown attributes >>
            #@+node:ekr.20031218072017.1564:<< handle unknown attributes >>
            keys = attrDict.keys()
            if keys:
                t.unknownAttributes = attrDict
                t._p_changed = 1
                if 0: # For debugging.
                    g.es_print("unknown attributes for tnode",color = "blue")
                    for key in keys:
                        g.es_print('',"%s = %s" % (key,attrDict.get(key)))
            #@-node:ekr.20031218072017.1564:<< handle unknown attributes >>
            #@nl
            s = self.getEscapedString()
            t.setTnodeText(s,encoding=self.leo_file_encoding)
        else:
            g.es("no tnode with index:",str(index),"the text will be discarded")
        self.getTag("</t>")
    #@-node:ekr.20031218072017.1561:getTnode
    #@+node:ekr.20031218072017.2008:getTnodeList (4.0,4.2)
    def getTnodeList (self,s):

        """Parse a list of tnode indices in string s."""

        # Remember: entries in the tnodeList correspond to @+node sentinels, _not_ to tnodes!

        fc = self

        indexList = s.split(',') # The list never ends in a comma.
        tnodeList = []
        for index in indexList:
            index = self.canonicalTnodeIndex(index)
            t = fc.tnodesDict.get(index)
            if not t:
                # Not an error: create a new tnode and put it in fc.tnodesDict.
                # g.trace("not allocated: %s" % index)
                t = self.newTnode(index)
            tnodeList.append(t)

        # if tnodeList: g.trace(len(tnodeList))
        return tnodeList
    #@-node:ekr.20031218072017.2008:getTnodeList (4.0,4.2)
    #@+node:ekr.20031218072017.1560:getTnodes
    def getTnodes (self):

        # A slight change: we require a tnodes element.  But Leo always writes this.
        if self.getOpenTag("<tnodes>"):
            return # <tnodes/> seen.

        while self.matchTag("<t"):
            self.getTnode()

        self.getTag("</tnodes>")
    #@-node:ekr.20031218072017.1560:getTnodes
    #@+node:EKR.20040526204036.1:getUa (non-sax)
    # changed for 4.3.

    def getUa(self,unused_nodeType):

        """Parse an unknown attribute in a <v> or <t> element."""

        # New in 4.2.  The unknown tag has been pickled and hexlify'd.
        attr,val = self.getUnknownTag()
        # g.trace(attr,repr(val))
        if not attr:
            return None,None

        # New in 4.3: leave string attributes starting with 'str_' alone.
        if attr.startswith('str_') and type(val) == type(''):
            # g.trace(attr,val)
            return attr,val

        # New in 4.3: convert attributes starting with 'b64_' using the base64 conversion.
        if 0: # Not ready yet.
            if attr.startswith('b64_'):
                try: pass
                except Exception: pass

        try:
            binString = binascii.unhexlify(val) # Throws a TypeError if val is not a hex string.
        except TypeError:
            # Assume that Leo 4.1 wrote the attribute.
            # g.trace('4.1 val:',val2)
            return attr,val
        try:
            # No change needed to support protocols.
            val2 = pickle.loads(binString)
            # g.trace('v.3 val:',val2)
            return attr,val2
        except (pickle.UnpicklingError,ImportError):
            return attr,val
        except Exception:
            return attr,val # New in Leo 4.4.5.
    #@-node:EKR.20040526204036.1:getUa (non-sax)
    #@+node:ekr.20031218072017.1566:getVnode & helpers
    # changed for 4.2 & 4.4
    def getVnode (self,parent,back,skip,appendToCurrentStack,appendToTopStack):

        v = None
        setCurrent = setExpanded = setMarked = setOrphan = setTop = False
        tref = -1 ; headline = '' ; tnodeList = None ; attrDict = {}

        # we have already matched <v.

        # New in Leo 4.4: support collapsed tnodes.
        if self.matchTag('/>'): # A collapsed vnode.
            v,skip2 = self.createVnode(parent,back,tref,headline,attrDict)
            if self.checking: return None
            else: return v

        while 1:
            if self.matchTag("a=\""):
                #@            << Handle vnode attribute bits >>
                #@+node:ekr.20031218072017.1567:<< Handle vnode attribute bits  >>
                # The a=" has already been seen.
                while 1:
                    if   self.matchChar('C'): pass # Not used: clone bits are recomputed later.
                    elif self.matchChar('D'): pass # Not used.
                    elif self.matchChar('E'): setExpanded = True
                    elif self.matchChar('M'): setMarked = True
                    elif self.matchChar('O'): setOrphan = True
                    elif self.matchChar('T'): setTop = True
                    elif self.matchChar('V'): setCurrent = True
                    else: break

                self.getDquote()
                #@-node:ekr.20031218072017.1567:<< Handle vnode attribute bits  >>
                #@nl
            elif self.matchTag("t="):
                # New for 4.1.  Read either "Tnnn" or "gnx".
                tref = index = self.getDqString()
                if self.usingClipboard:
                    #@                << raise invalidPaste if the tnode is in self.forbiddenTnodes >>
                    #@+node:ekr.20041023110111:<< raise invalidPaste if the tnode is in self.forbiddenTnodes >>
                    # Bug fix in 4.3 a1: make sure we have valid paste.
                    junk,theTime,junk = g.app.nodeIndices.scanGnx(index,0)
                    if not theTime and index[0] == "T":
                        index = index[1:]

                    index = self.canonicalTnodeIndex(index)
                    t = self.tnodesDict.get(index)

                    if t in self.forbiddenTnodes:
                        # g.trace(t)
                        raise invalidPaste
                    #@-node:ekr.20041023110111:<< raise invalidPaste if the tnode is in self.forbiddenTnodes >>
                    #@nl
            elif self.matchTag("vtag=\"V"):
                self.getIndex() ; self.getDquote() # ignored
            elif self.matchTag("tnodeList="):
                s = self.getDqString()
                tnodeList = self.getTnodeList(s) # New for 4.0
            elif self.matchTag("descendentTnodeUnknownAttributes="):
                # New for 4.2, deprecated for 4.3?
                s = self.getDqString()
                theDict = self.getDescendentUnknownAttributes(s)
                if theDict:
                    self.descendentUnknownAttributesDictList.append(theDict)
            elif self.matchTag("expanded="): # New in 4.2
                s = self.getDqString()
                self.descendentExpandedList.extend(self.getDescendentAttributes(s,tag="expanded"))
            elif self.matchTag("marks="): # New in 4.2.
                s = self.getDqString()
                self.descendentMarksList.extend(self.getDescendentAttributes(s,tag="marks"))
            elif self.matchTag(">"):
                break
            else: # New for 4.0: allow unknown attributes.
                # New in 4.2: allow pickle'd and hexlify'ed values.
                attr,val = self.getUa("vnode")
                if attr: attrDict[attr] = val
        # Headlines are optional.
        if self.matchTag("<vh>"):
            headline = self.getEscapedString() ; self.getTag("</vh>")
        # g.trace("skip:",skip,"parent:",parent,"back:",back,"headline:",headline)
        if skip:
            v = self.getExistingVnode(tref,headline)
            if v: # Bug fix: 4/18/05: The headline may change during paste as clone.
                v.initHeadString(headline,encoding=self.leo_file_encoding)
        if v is None:
            v,skip2 = self.createVnode(parent,back,tref,headline,attrDict)
            if not self.checking:
                skip = skip or skip2
                if tnodeList:
                    v.t.tnodeList = tnodeList # New for 4.0, 4.2: now in tnode.

        if not self.checking:
            #@        << Set the remembered status bits >>
            #@+node:ekr.20031218072017.1568:<< Set the remembered status bits >>
            if setCurrent:
                self.currentVnodeStack = [v]

            if setTop:
                self.topVnodeStack = [v]

            if setExpanded:
                v.initExpandedBit()

            if setMarked:
                v.initMarkedBit() # 3/25/03: Do not call setMarkedBit here!

            if setOrphan:
                v.setOrphan()
            #@-node:ekr.20031218072017.1568:<< Set the remembered status bits >>
            #@nl

        # Recursively create all nested nodes.
        parent = v ; back = None
        while self.matchTag("<v"):
            append1 = appendToCurrentStack and len(self.currentVnodeStack) == 0
            append2 = appendToTopStack and len(self.topVnodeStack) == 0
            back = self.getVnode(parent,back,skip,
                appendToCurrentStack=append1,appendToTopStack=append2)

        if not self.checking:
            #@        << Append to current or top stack >>
            #@+node:ekr.20040326055828:<< Append to current or top stack >>
            if not setCurrent and len(self.currentVnodeStack) > 0 and appendToCurrentStack:
                #g.trace("append current",v)
                self.currentVnodeStack.append(v)

            if not setTop and len(self.topVnodeStack) > 0 and appendToTopStack:
                #g.trace("append top",v)
                self.topVnodeStack.append(v)
            #@-node:ekr.20040326055828:<< Append to current or top stack >>
            #@nl

        # End this vnode.
        self.getTag("</v>")
        return v
    #@nonl
    #@+node:ekr.20031218072017.1860:createVnode
    # (changed for 4.2) sets skip

    def createVnode (self,parent,back,tref,headline,attrDict):

        # g.trace(parent,headline)
        v = None ; c = self.c
        # Shared tnodes are placed in the file even if empty.
        if tref == -1:
            t = leoNodes.tnode()
        else:
            tref = self.canonicalTnodeIndex(tref)
            t = self.tnodesDict.get(tref)
            if not t:
                t = self.newTnode(tref)

        if self.checking: return None,False

        if back: # create v after back.
            v = back.insertAfter(t)
        elif parent: # create v as the parent's first child.
            v = parent.insertAsNthChild(0,t)
        else: # create a root vnode
            v = leoNodes.vnode(t)
            v.moveToRoot(oldRoot=None)
            c.setRootVnode(v) # New in Leo 4.4.2.

        if v not in v.t.vnodeList:
            v.t.vnodeList.append(v) # New in 4.2.

        skip = len(v.t.vnodeList) > 1
        v.initHeadString(headline,encoding=self.leo_file_encoding)
        #@    << handle unknown vnode attributes >>
        #@+node:ekr.20031218072017.1861:<< handle unknown vnode attributes >>
        keys = attrDict.keys()
        if keys:
            v.unknownAttributes = attrDict
            v._p_changed = 1

            if 0: # For debugging.
                g.es_print("unknown attributes for",v.headString(),color="blue")
                for key in keys:
                    g.es_print('',"%s = %s" % (key,attrDict.get(key)))
        #@-node:ekr.20031218072017.1861:<< handle unknown vnode attributes >>
        #@nl
        # g.trace(skip,tref,v,v.t,len(v.t.vnodeList))
        return v,skip
    #@nonl
    #@-node:ekr.20031218072017.1860:createVnode
    #@+node:ekr.20040326063413:getExistingVnode
    def getExistingVnode (self,tref,headline):

        assert(tref > -1)
        tref = self.canonicalTnodeIndex(tref)
        t = self.tnodesDict.get(tref)
        try:
            return t.vnodeList[0]
        except (IndexError,AttributeError):
            g.es("missing vnode:",headline,color="red")
            g.es("probably an outline topology error.")
            return None
    #@-node:ekr.20040326063413:getExistingVnode
    #@-node:ekr.20031218072017.1566:getVnode & helpers
    #@+node:ekr.20031218072017.1565:getVnodes
    def getVnodes (self,reassignIndices=True):

        c = self.c

        if self.getOpenTag("<vnodes>"):
            return # <vnodes/> seen.

        self.forbiddenTnodes = []
        back = parent = None # This routine _must_ work on vnodes!
        self.currentVnodeStack = []
        self.topVnodeStack = []

        if self.usingClipboard:
            oldRoot = c.rootPosition()
            oldCurrent = c.currentPosition()
            if not reassignIndices:
                #@            << set self.forbiddenTnodes to tnodes than must not be pasted >>
                #@+node:ekr.20041023105832:<< set self.forbiddenTnodes to tnodes than must not be pasted >>
                self.forbiddenTnodes = []

                for p in oldCurrent.self_and_parents_iter():
                    if p.v.t not in self.forbiddenTnodes:
                        self.forbiddenTnodes.append(p.v.t)

                # g.trace("forbiddenTnodes",self.forbiddenTnodes)
                #@-node:ekr.20041023105832:<< set self.forbiddenTnodes to tnodes than must not be pasted >>
                #@nl

        while self.matchTag("<v"):
            append1 = not self.usingClipboard and len(self.currentVnodeStack) == 0
            append2 = not self.usingClipboard and len(self.topVnodeStack) == 0
            back = self.getVnode(parent,back,skip=False,
                appendToCurrentStack=append1,appendToTopStack=append2)

        if self.usingClipboard and not self.checking:
            # Link in the pasted nodes after the current position.
            newRoot = c.rootPosition()
            c.setRootPosition(oldRoot)
            newRoot.v.linkAfter(oldCurrent.v)
            newCurrent = oldCurrent.copy()
            newCurrent.v = newRoot.v
            c.setCurrentPosition(newCurrent)

        self.getTag("</vnodes>")
    #@-node:ekr.20031218072017.1565:getVnodes
    #@+node:ekr.20031218072017.1249:getXmlStylesheetTag
    def getXmlStylesheetTag (self):

        """Parses the optional xml stylesheet string, and sets the corresponding config option.

        For example, given: <?xml_stylesheet s?> the config option is s."""

        c = self.c
        tag = "<?xml-stylesheet "

        if self.matchTag(tag):
            s = self.getStringToTag("?>")
            # print "reading:", tag + s + "?>"
            c.frame.stylesheet = s
            self.getTag("?>")
    #@-node:ekr.20031218072017.1249:getXmlStylesheetTag
    #@+node:ekr.20031218072017.1468:getXmlVersionTag
    # Parses the encoding string, and sets self.leo_file_encoding.

    def getXmlVersionTag (self):

        self.getTag(g.app.prolog_prefix_string)
        encoding = self.getDqString()
        self.getTag(g.app.prolog_postfix_string)

        if g.isValidEncoding(encoding):
            self.leo_file_encoding = encoding
            # g.trace('self.leo_file_encoding:',encoding, color="blue")
        else:
            g.es("invalid encoding in .leo file:",encoding,color="red")
    #@-node:ekr.20031218072017.1468:getXmlVersionTag
    #@+node:ekr.20040326054052:setPositionsFromStacks (silly)
    def setPositionsFromStacks (self):

        c = self.c

        current = self.convertStackToPosition(self.currentVnodeStack)

        if current:
            # g.trace('using convertStackToPosition',current)
            c.setCurrentPosition(current)
        else:
            # g.trace(self.currentVnodeStack)
            c.setCurrentPosition(c.rootPosition())

        # At present this is useless: the drawing code doesn't set the top position properly.
        if 0:
            top = self.convertStackToPosition(self.topVnodeStack)
            if top:
                c.setTopPosition(top)
    #@nonl
    #@-node:ekr.20040326054052:setPositionsFromStacks (silly)
    #@-node:ekr.20031218072017.3021:Non-sax
    #@+node:ekr.20060919104530:Sax
    #@+node:ekr.20060919110638.4:createSaxVnodes & helpers
    def createSaxVnodes (self, dummyRoot):

        '''**Important**: this method and its helpers are low-level code
        corresponding to link/unlink methods in leoNodes.py.
        Modify this with extreme care.'''

        children = self.createSaxChildren(dummyRoot,parent_v = None)
        firstChild = children and children[0]

        return firstChild
    #@nonl
    #@+node:ekr.20060919110638.5:createSaxChildren
    # node is a saxNodeClass object, parent_v is a vnode.

    def createSaxChildren (self, node, parent_v):

        result = []

        for child in node.children:
            tnx = child.tnx
            t = self.tnodesDict.get(tnx)
            if t:
                # A clone.  Create a new clone node, but share the subtree, i.e., the tnode.
                v = self.createSaxVnode(child,parent_v,t=t)
                # g.trace('clone',id(child),child.headString,'t',v.t)
            else:
                v = self.createSaxVnodeTree(child,parent_v)
            result.append(v)

        self.linkSiblings(result)
        if parent_v: self.linkParentAndChildren(parent_v,result)
        return result
    #@nonl
    #@-node:ekr.20060919110638.5:createSaxChildren
    #@+node:ekr.20060919110638.6:createSaxVnodeTree
    def createSaxVnodeTree (self,node,parent_v):

        v = self.createSaxVnode(node,parent_v)

        self.createSaxChildren(node,v)

        return v
    #@nonl
    #@-node:ekr.20060919110638.6:createSaxVnodeTree
    #@+node:ekr.20060919110638.7:createSaxVnode
    def createSaxVnode (self,node,parent_v,t=None):

        h = node.headString
        b = node.bodyString

        if not t:
            t = leoNodes.tnode(bodyString=b,headString=h)
            if node.tnx:
                t.fileIndex = g.app.nodeIndices.scanGnx(node.tnx,0)
        v = leoNodes.vnode(t)
        v.t.vnodeList.append(v)
        v._parent = parent_v

        index = self.canonicalTnodeIndex(node.tnx)
        self.tnodesDict [index] = t

        # g.trace('tnx','%-22s' % (index),'v',id(v),'v.t',id(v.t),'body','%-4d' % (len(b)),h)

        self.handleVnodeSaxAttributes(node,v)
        self.handleTnodeSaxAttributes(node,t)

        return v
    #@nonl
    #@+node:ekr.20060919110638.8:handleTnodeSaxAttributes
    def handleTnodeSaxAttributes (self,node,t):

        d = node.tnodeAttributes

        aDict = {}
        for key in d.keys():
            val = d.get(key)
            val2 = self.getSaxUa(key,val)
            aDict[key] = val2

        if aDict:
            # g.trace('uA',aDict)
            t.unknownAttributes = aDict
    #@nonl
    #@-node:ekr.20060919110638.8:handleTnodeSaxAttributes
    #@+node:ekr.20061004053644:handleVnodeSaxAttributes
    # The native attributes of <v> elements are a, t, vtag, tnodeList,
    # marks, expanded and descendentTnodeUnknownAttributes.

    def handleVnodeSaxAttributes (self,node,v):

        d = node.attributes
        s = d.get('a')
        if s:
            # g.trace('%s a=%s %s' % (id(node),s,v.headString()))
            # 'C' (clone) and 'D' bits are not used.
            if 'M' in s: v.setMarked()
            if 'E' in s: v.expand()
            if 'O' in s: v.setOrphan()
            if 'T' in s: self.topVnode = v
            if 'V' in s:
                # g.trace('setting currentVnode',v,color='red')
                self.currentVnode = v

        s = d.get('tnodeList','')
        tnodeList = s and s.split(',')
        if tnodeList:
            # This tnode list will be resolved later.
            # g.trace('found tnodeList',v.headString(),tnodeList)
            v.tempTnodeList = tnodeList

        s = d.get('descendentTnodeUnknownAttributes') # Correct: only tnode have descendent uA's.
        if s: 
            aDict = self.getDescendentUnknownAttributes(s)
            if aDict:
                # g.trace('descendentUaDictList',aDict)
                self.descendentUnknownAttributesDictList.append(aDict)

        s = d.get('expanded')
        if s:
            aList = self.getDescendentAttributes(s,tag="expanded")
            # g.trace('expanded list',len(aList))
            self.descendentExpandedList.extend(aList)

        s = d.get('marks')
        if s:
            aList = self.getDescendentAttributes(s,tag="marks")
            # g.trace('marks list',len(aList))
            self.descendentMarksList.extend(aList)

        aDict = {}
        for key in d.keys():
            if key in self.nativeVnodeAttributes:
                if 0: g.trace('****ignoring***',key,d.get(key))
            else:
                val = d.get(key)
                val2 = self.getSaxUa(key,val)
                aDict[key] = val2
                # g.trace(key,val,val2)
        if aDict:
            # g.trace('uA',aDict)
            v.unknownAttributes = aDict
    #@nonl
    #@-node:ekr.20061004053644:handleVnodeSaxAttributes
    #@-node:ekr.20060919110638.7:createSaxVnode
    #@+node:ekr.20060919110638.9:linkParentAndChildren
    def linkParentAndChildren (self, parent_v, children):

        # if children: g.trace(parent_v,len(children))

        firstChild_v = children and children[0] or None

        parent_v.t._firstChild = firstChild_v

        for child in children:
            child._parent = parent_v

        v = parent_v
        if v not in v.t.vnodeList:
            v.t.vnodeList.append(v)
    #@nonl
    #@-node:ekr.20060919110638.9:linkParentAndChildren
    #@+node:ekr.20060919110638.10:linkSiblings
    def linkSiblings (self, sibs):

        '''Set the v._back and v._next links for all vnodes v in sibs.'''

        n = len(sibs)

        for i in xrange(n):
            v = sibs[i]
            v._back = (i-1 >= 0 and sibs[i-1]) or None
            v._next = (i+1 <  n and sibs[i+1]) or None
    #@nonl
    #@-node:ekr.20060919110638.10:linkSiblings
    #@-node:ekr.20060919110638.4:createSaxVnodes & helpers
    #@+node:ekr.20060919110638.2:dumpSaxTree
    def dumpSaxTree (self,root,dummy):

        if not root:
            print 'dumpSaxTree: empty tree'
            return
        if not dummy:
            root.dump()
        for child in root.children:
            self.dumpSaxTree(child,dummy=False)
    #@nonl
    #@-node:ekr.20060919110638.2:dumpSaxTree
    #@+node:ekr.20061003093021:getSaxUa
    def getSaxUa(self,attr,val):

        """Parse an unknown attribute in a <v> or <t> element.
        The unknown tag has been pickled and hexlify'd.
        """

        try:
            val = str(val)
        except UnicodeError:
            g.es_print('unexpected exception converting hexlified string to string')
            g.es_exception()

        # g.trace(attr,repr(val))

        # New in 4.3: leave string attributes starting with 'str_' alone.
        if attr.startswith('str_') and type(val) == type(''):
            # g.trace(attr,val)
            return val

        # New in 4.3: convert attributes starting with 'b64_' using the base64 conversion.
        if 0: # Not ready yet.
            if attr.startswith('b64_'):
                try: pass
                except Exception: pass

        try:
            binString = binascii.unhexlify(val) # Throws a TypeError if val is not a hex string.
        except TypeError:
            # Assume that Leo 4.1 wrote the attribute.
            g.trace('can not unhexlify',val)
            return val
        try:
            # No change needed to support protocols.
            val2 = pickle.loads(binString)
            # g.trace('v.3 val:',val2)
            return val2
        except (pickle.UnpicklingError,ImportError):
            g.trace('can not unpickle',val)
            return val
    #@-node:ekr.20061003093021:getSaxUa
    #@+node:ekr.20060919110638.14:parse_leo_file
    def parse_leo_file (self,theFile,inputFileName,silent):

        c = self.c

        try:
            # Use cStringIo to avoid a crash in sax when inputFileName has unicode characters.
            s = theFile.read()
            theFile = cStringIO.StringIO(s)
            # g.trace(repr(inputFileName))
            node = None
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_external_ges,1)
                # Include external general entities, esp. xml-stylesheet lines.
            if 0: # Expat does not read external features.
                parser.setFeature(xml.sax.handler.feature_external_pes,1)
                    # Include all external parameter entities
                    # Hopefully the parser can figure out the encoding from the <?xml> element.
            handler = saxContentHandler(c,inputFileName,silent)
            parser.setContentHandler(handler)
            parser.parse(theFile) # expat does not support parseString
            node = handler.getRootNode()
        except xml.sax.SAXParseException:
            g.es_print('error parsing',inputFileName,color='red')
            g.es_exception()
        except Exception:
            g.es_print('unexpected exception parsing',inputFileName,color='red')
            g.es_exception()

        return node
    #@nonl
    #@-node:ekr.20060919110638.14:parse_leo_file
    #@+node:ekr.20060919110638.3:readSaxFile
    def readSaxFile (self,theFile,fileName,silent):

        # Pass one: create the intermediate nodes.
        dummyRoot = self.parse_leo_file(theFile,fileName,silent=silent)

        # self.dumpSaxTree(dummyRoot,dummy=True)

        # Pass two: create the tree of vnodes and tnodes from the intermediate nodes.
        v = dummyRoot and self.createSaxVnodes(dummyRoot)
        return v
    #@nonl
    #@-node:ekr.20060919110638.3:readSaxFile
    #@+node:ekr.20060919110638.11:resolveTnodeLists
    def resolveTnodeLists (self):

        c = self.c

        for p in c.allNodes_iter():
            if hasattr(p.v,'tempTnodeList'):
                # g.trace(p.v.headString())
                result = []
                for tnx in p.v.tempTnodeList:
                    index = self.canonicalTnodeIndex(tnx)
                    t = self.tnodesDict.get(index)
                    if t:
                        # g.trace(tnx,t)
                        result.append(t)
                    else:
                        g.trace('No tnode for %s' % tnx)
                p.v.t.tnodeList = result
                delattr(p.v,'tempTnodeList')
    #@nonl
    #@-node:ekr.20060919110638.11:resolveTnodeLists
    #@+node:ekr.20060919110638.13:setPositionsFromVnodes & helper
    def setPositionsFromVnodes (self):

        c = self.c ; p = c.rootPosition()

        current = None
        d = hasattr(p.v,'unknownAttributes') and p.v.unknownAttributes
        if d:
            s = d.get('str_leo_pos')
            if s:
                current = self.archivedPositionToPosition(s)

        c.setCurrentPosition(current or c.rootPosition())
    #@nonl
    #@+node:ekr.20061006104837.1:archivedPositionToPosition
    def archivedPositionToPosition (self,s):

        c = self.c
        aList = s.split(',')
        try:
            aList = [int(z) for z in aList]
        except Exception:
            g.trace('oops: bad archived position:',aList)
            aList = None
        if not aList: return None
        p = c.rootPosition() ; level = 0
        while level < len(aList):
            i = aList[level]
            while i > 0:
                if p.hasNext():
                    p.moveToNext()
                    i -= 1
                else:
                    g.trace('oops: bad archived position:',aList)
                    return None
            level += 1
            if level < len(aList):
                p.moveToFirstChild()
                # g.trace('level',level,'index',aList[level],p.headString())
        return p
    #@nonl
    #@-node:ekr.20061006104837.1:archivedPositionToPosition
    #@-node:ekr.20060919110638.13:setPositionsFromVnodes & helper
    #@-node:ekr.20060919104530:Sax
    #@-node:ekr.20031218072017.3020:Reading
    #@+node:ekr.20031218072017.3032:Writing
    #@+node:ekr.20070413045221.2:Top-level  (leoFileCommands)
    #@+node:ekr.20031218072017.1720:save (fileCommands)
    def save(self,fileName):

        c = self.c ; v = c.currentVnode()

        # New in 4.2.  Return ok flag so shutdown logic knows if all went well.
        ok = g.doHook("save1",c=c,p=v,v=v,fileName=fileName)
        # redraw_flag = g.app.gui.guiName() == 'tkinter'
        if ok is None:
            c.beginUpdate()
            try:
                c.endEditing()# Set the current headline text.
                self.setDefaultDirectoryForNewFiles(fileName)
                ok = self.write_Leo_file(fileName,False) # outlineOnlyFlag
                if ok:
                    c.setChanged(False) # Clears all dirty bits.
                    self.putSavedMessage(fileName)
                    if c.config.save_clears_undo_buffer:
                        g.es("clearing undo")
                        c.undoer.clearUndoState()
            finally:
                c.endUpdate() # We must redraw in order to clear dirty node icons.
        g.doHook("save2",c=c,p=v,v=v,fileName=fileName)
        return ok
    #@-node:ekr.20031218072017.1720:save (fileCommands)
    #@+node:ekr.20031218072017.3043:saveAs
    def saveAs(self,fileName):

        c = self.c ; v = c.currentVnode()

        if not g.doHook("save1",c=c,p=v,v=v,fileName=fileName):
            c.beginUpdate()
            try:
                c.endEditing() # Set the current headline text.
                self.setDefaultDirectoryForNewFiles(fileName)
                if self.write_Leo_file(fileName,False): # outlineOnlyFlag
                    c.setChanged(False) # Clears all dirty bits.
                    self.putSavedMessage(fileName)
            finally:
                c.endUpdate() # We must redraw in order to clear dirty node icons.
        g.doHook("save2",c=c,p=v,v=v,fileName=fileName)
    #@-node:ekr.20031218072017.3043:saveAs
    #@+node:ekr.20031218072017.3044:saveTo
    def saveTo (self,fileName):

        c = self.c ; v = c.currentVnode()

        if not g.doHook("save1",c=c,p=v,v=v,fileName=fileName):
            c.beginUpdate()
            try:
                c.endEditing()# Set the current headline text.
                self.setDefaultDirectoryForNewFiles(fileName)
                self.write_Leo_file(fileName,False) # outlineOnlyFlag
                self.putSavedMessage(fileName)
            finally:
                c.endUpdate() # We must redraw in order to clear dirty node icons.
        g.doHook("save2",c=c,p=v,v=v,fileName=fileName)
    #@-node:ekr.20031218072017.3044:saveTo
    #@+node:ekr.20070413061552:putSavedMessage
    def putSavedMessage (self,fileName):

        c = self.c

        zipMark = g.choose(c.isZipped,'[zipped] ','')

        g.es("saved:","%s%s" % (zipMark,g.shortFileName(fileName)))
    #@nonl
    #@-node:ekr.20070413061552:putSavedMessage
    #@-node:ekr.20070413045221.2:Top-level  (leoFileCommands)
    #@+node:ekr.20031218072017.1570:assignFileIndices & compactFileIndices
    def assignFileIndices (self):

        """Assign a file index to all tnodes"""

        pass # No longer needed: we assign indices as needed.

    # Indices are now immutable, so there is no longer any difference between these two routines.
    compactFileIndices = assignFileIndices
    #@-node:ekr.20031218072017.1570:assignFileIndices & compactFileIndices
    #@+node:ekr.20050404190914.2:deleteFileWithMessage
    def deleteFileWithMessage(self,fileName,unused_kind):

        try:
            os.remove(fileName)

        except Exception:
            if self.read_only:
                g.es("read only",color="red")
            if not g.unitTesting:
                g.es("exception deleting backup file:",fileName)
                g.es_exception(full=False)
            return False
    #@-node:ekr.20050404190914.2:deleteFileWithMessage
    #@+node:ekr.20031218072017.1470:put
    def put (self,s):

        '''Put string s to self.outputFile. All output eventually comes here.'''

        # Improved code: self.outputFile (a cStringIO object) always exists.
        if s:
            self.putCount += 1
            s = g.toEncodedString(s,self.leo_file_encoding,reportErrors=True)
            self.outputFile.write(s)

    def put_dquote (self):
        self.put('"')

    def put_dquoted_bool (self,b):
        if b: self.put('"1"')
        else: self.put('"0"')

    def put_flag (self,a,b):
        if a:
            self.put(" ") ; self.put(b) ; self.put('="1"')

    def put_in_dquotes (self,a):
        self.put('"')
        if a: self.put(a) # will always be True if we use backquotes.
        else: self.put('0')
        self.put('"')

    def put_nl (self):
        self.put("\n")

    def put_tab (self):
        self.put("\t")

    def put_tabs (self,n):
        while n > 0:
            self.put("\t")
            n -= 1
    #@nonl
    #@-node:ekr.20031218072017.1470:put
    #@+node:ekr.20040324080819.1:putLeoFile & helpers
    def putLeoFile (self):

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
    #@+node:ekr.20031218072017.3035:putFindSettings
    def putFindSettings (self):

        # New in 4.3:  These settings never get written to the .leo file.
        self.put("<find_panel_settings/>")
        self.put_nl()
    #@-node:ekr.20031218072017.3035:putFindSettings
    #@+node:ekr.20031218072017.3037:putGlobals
    # Changed for Leo 4.0.

    def putGlobals (self):

        c = self.c
        self.put("<globals")
        #@    << put the body/outline ratio >>
        #@+node:ekr.20031218072017.3038:<< put the body/outline ratio >>
        # Puts an innumerate number of digits

        self.put(" body_outline_ratio=")
        self.put_in_dquotes(str(c.frame.ratio))
        #@-node:ekr.20031218072017.3038:<< put the body/outline ratio >>
        #@nl
        self.put(">") ; self.put_nl()
        #@    << put the position of this frame >>
        #@+node:ekr.20031218072017.3039:<< put the position of this frame >>
        width,height,left,top = c.frame.get_window_info()

        self.put_tab()
        self.put("<global_window_position")
        self.put(" top=") ; self.put_in_dquotes(str(top))
        self.put(" left=") ; self.put_in_dquotes(str(left))
        self.put(" height=") ; self.put_in_dquotes(str(height))
        self.put(" width=") ; self.put_in_dquotes(str(width))
        self.put("/>") ; self.put_nl()
        #@-node:ekr.20031218072017.3039:<< put the position of this frame >>
        #@nl
        #@    << put the position of the log window >>
        #@+node:ekr.20031218072017.3040:<< put the position of the log window >>
        top = left = height = width = 0 # no longer used
        self.put_tab()
        self.put("<global_log_window_position")
        self.put(" top=") ; self.put_in_dquotes(str(top))
        self.put(" left=") ; self.put_in_dquotes(str(left))
        self.put(" height=") ; self.put_in_dquotes(str(height))
        self.put(" width=") ; self.put_in_dquotes(str(width))
        self.put("/>") ; self.put_nl()
        #@-node:ekr.20031218072017.3040:<< put the position of the log window >>
        #@nl
        self.put("</globals>") ; self.put_nl()
    #@-node:ekr.20031218072017.3037:putGlobals
    #@+node:ekr.20031218072017.3041:putHeader
    def putHeader (self):

        tnodes = 0 ; clone_windows = 0 # Always zero in Leo2.

        self.put("<leo_header")
        self.put(" file_format=") ; self.put_in_dquotes("2")
        self.put(" tnodes=") ; self.put_in_dquotes(str(tnodes))
        self.put(" max_tnode_index=") ; self.put_in_dquotes(str(0))
        self.put(" clone_windows=") ; self.put_in_dquotes(str(clone_windows))
        self.put("/>") ; self.put_nl()
    #@-node:ekr.20031218072017.3041:putHeader
    #@+node:ekr.20031218072017.3042:putPostlog
    def putPostlog (self):

        self.put("</leo_file>") ; self.put_nl()
    #@-node:ekr.20031218072017.3042:putPostlog
    #@+node:ekr.20031218072017.2066:putPrefs
    def putPrefs (self):

        # New in 4.3:  These settings never get written to the .leo file.
        self.put("<preferences/>")
        self.put_nl()
    #@-node:ekr.20031218072017.2066:putPrefs
    #@+node:ekr.20031218072017.1246:putProlog & helpers
    def putProlog (self):

        c = self.c

        self.putXMLLine()

        if c.config.stylesheet or c.frame.stylesheet:
            self.putStyleSheetLine()

        self.put("<leo_file>") ; self.put_nl()
    #@+node:ekr.20031218072017.1247:putXMLLine
    def putXMLLine (self):

        '''Put the **properly encoded** <?xml> element.'''

        # Use self.leo_file_encoding encoding.
        self.put('%s"%s"%s\n' % (
            g.app.prolog_prefix_string,
            self.leo_file_encoding,
            g.app.prolog_postfix_string))
    #@nonl
    #@-node:ekr.20031218072017.1247:putXMLLine
    #@+node:ekr.20031218072017.1248:putStyleSheetLine
    def putStyleSheetLine (self):

        c = self.c

        # The stylesheet in the .leo file takes precedence over the default stylesheet.
        self.put("<?xml-stylesheet ")
        self.put(c.frame.stylesheet or c.config.stylesheet)
        self.put("?>")
        self.put_nl()
    #@nonl
    #@-node:ekr.20031218072017.1248:putStyleSheetLine
    #@-node:ekr.20031218072017.1246:putProlog & helpers
    #@+node:ekr.20031218072017.1577:putTnode
    def putTnode (self,t):

        # New in Leo 4.4.8.  Assign v.t.fileIndex here as needed.
        if not t.fileIndex:
            g.trace('can not happen: no index for tnode',t)
            t.fileIndex = g.app.nodeIndices.getNewIndex()

        # New in Leo 4.4.2 b2: call put just once.
        gnx = g.app.nodeIndices.toString(t.fileIndex)
        ua = hasattr(t,'unknownAttributes') and self.putUnknownAttributes(t) or ''
        body = t.bodyString and xml.sax.saxutils.escape(t.bodyString) or ''
        self.put('<t tx="%s"%s>%s</t>\n' % (gnx,ua,body))
    #@-node:ekr.20031218072017.1577:putTnode
    #@+node:ekr.20031218072017.1575:putTnodes
    def putTnodes (self):

        """Puts all tnodes as required for copy or save commands"""

        c = self.c

        self.put("<tnodes>\n")
        #@    << write only those tnodes that were referenced >>
        #@+node:ekr.20031218072017.1576:<< write only those tnodes that were referenced >>
        if self.usingClipboard: # write the current tree.
            theIter = c.currentPosition().self_and_subtree_iter()
        else: # write everything
            theIter = c.allNodes_iter()

        # Populate tnodes
        tnodes = {}

        for p in theIter:
            index = p.v.t.fileIndex
            if index:
                tnodes[index] = p.v.t
            else:
                g.trace('can not happen: no p.v.t.fileIndex for',p.headString())

        # Put all tnodes in index order.
        keys = tnodes.keys() ; keys.sort()
        for index in keys:
            # g.trace(index)
            t = tnodes.get(index)
            if not t:
                g.trace('can not happen: no tnode for',index)
            # Write only those tnodes whose vnodes were written.
            if t.isWriteBit():
                self.putTnode(t)
        #@nonl
        #@-node:ekr.20031218072017.1576:<< write only those tnodes that were referenced >>
        #@nl
        self.put("</tnodes>\n")
    #@-node:ekr.20031218072017.1575:putTnodes
    #@+node:EKR.20040526202501:putUnknownAttributes & helper
    def putUnknownAttributes (self,torv):

        """Put pickleable values for all keys in torv.unknownAttributes dictionary."""

        attrDict = torv.unknownAttributes
        if type(attrDict) != type({}):
            g.es("ignoring non-dictionary unknownAttributes for",torv,color="blue")
            return ''
        else:
            return ''.join([self.putUaHelper(torv,key,val) for key,val in attrDict.items()])
    #@nonl
    #@+node:ekr.20050418161620.2:putUaHelper
    def putUaHelper (self,torv,key,val):

        '''Put attribute whose name is key and value is val to the output stream.'''

        # g.trace(key,repr(val),g.callers())

        # New in 4.3: leave string attributes starting with 'str_' alone.
        if key.startswith('str_'):
            if type(val) == type(''):
                attr = ' %s="%s"' % (key,xml.sax.saxutils.escape(val))
                return attr
            else:
                g.es("ignoring non-string attribute",key,"in",torv,color="blue")
                return ''
        try:
            version = '.'.join([str(sys.version_info[i]) for i in (0,1)])
            python23 = g.CheckVersion(version,'2.3')
            try:
                if python23:
                    # Protocol argument is new in Python 2.3
                    # Use protocol 1 for compatibility with bin.
                    s = pickle.dumps(val,protocol=1)
                else:
                    s = pickle.dumps(val,bin=True)
                attr = ' %s="%s"' % (key,binascii.hexlify(s))
                return attr
            except Exception:
                g.es('putUaHelper: unexpected pickling exception',color='red')
                g.es_exception()
                return ''
        except pickle.PicklingError:
            # New in 4.2 beta 1: keep going after error.
            g.es("ignoring non-pickleable attribute",key,"in",torv,color="blue")
            return ''
    #@-node:ekr.20050418161620.2:putUaHelper
    #@-node:EKR.20040526202501:putUnknownAttributes & helper
    #@+node:ekr.20031218072017.1579:putVnodes & helpers
    def putVnodes (self):

        """Puts all <v> elements in the order in which they appear in the outline."""

        c = self.c
        c.clearAllVisited()

        self.put("<vnodes>\n")

        # Make only one copy for all calls.
        self.currentPosition = c.currentPosition() 
        self.rootPosition    = c.rootPosition()
        self.topPosition     = c.topPosition()

        if self.usingClipboard:
            self.putVnode(self.currentPosition) # Write only current tree.
        else:
            for p in c.rootPosition().self_and_siblings_iter():
                # New in Leo 4.4.2 b2 An optimization:
                self.putVnode(p,isIgnore=p.isAtIgnoreNode()) # Write the next top-level node.

        self.put("</vnodes>\n")
    #@nonl
    #@+node:ekr.20031218072017.1863:putVnode (3.x and 4.x)
    def putVnode (self,p,isIgnore=False):

        """Write a <v> element corresponding to a vnode."""

        fc = self ; c = fc.c ; v = p.v
        # Not writing @auto nodes is way too dangerous.
        isAuto = p.isAtAutoNode() and p.atAutoNodeName().strip()
        isThin = p.isAtThinFileNode()
        isOrphan = p.isOrphan()
        if not isIgnore: isIgnore = p.isAtIgnoreNode()

        # forceWrite = isIgnore or not isThin or (isThin and isOrphan)
        if isIgnore: forceWrite = True      # Always write full @ignore trees.
        elif isAuto: forceWrite = False     # Never write non-ignored @auto trees.
        elif isThin: forceWrite = isOrphan  # Only write orphan @thin trees.
        else:        forceWrite = True      # Write all other @file trees.

        #@    << Set gnx = tnode index >>
        #@+node:ekr.20031218072017.1864:<< Set gnx = tnode index >>
        # New in Leo 4.4.8.  Assign v.t.fileIndex here as needed.
        if not v.t.fileIndex:
            v.t.fileIndex = g.app.nodeIndices.getNewIndex()

        gnx = g.app.nodeIndices.toString(v.t.fileIndex)

        if forceWrite or self.usingClipboard:
            v.t.setWriteBit() # 4.2: Indicate we wrote the body text.
        #@-node:ekr.20031218072017.1864:<< Set gnx = tnode index >>
        #@nl
        attrs = []
        #@    << Append attribute bits to attrs >>
        #@+node:ekr.20031218072017.1865:<< Append attribute bits to attrs >>
        # These string catenations are benign because they rarely happen.
        attr = ""
        if v.isExpanded(): attr += "E"
        if v.isMarked():   attr += "M"
        if v.isOrphan():   attr += "O"

        # No longer a bottleneck now that we use p.equal rather than p.__cmp__
        # Almost 30% of the entire writing time came from here!!!
        if not self.use_sax:
            if p.equal(self.topPosition):     attr += "T" # was a bottleneck
            if p.equal(self.currentPosition): attr += "V" # was a bottleneck

        if attr:
            attrs.append(' a="%s"' % attr)

        # Put the archived *current* position in the *root* positions <v> element.
        if self.use_sax and p.equal(self.rootPosition):
            aList = [str(z) for z in self.currentPosition.archivedPosition()]
            d = hasattr(v,'unKnownAttributes') and v.unknownAttributes or {}
            d['str_leo_pos'] = ','.join(aList)
            # g.trace(aList,d)
            v.unknownAttributes = d
        #@nonl
        #@-node:ekr.20031218072017.1865:<< Append attribute bits to attrs >>
        #@nl
        #@    << Append tnodeList and unKnownAttributes to attrs >>
        #@+node:ekr.20040324082713:<< Append tnodeList and unKnownAttributes to attrs>>
        # Write the tnodeList only for @file nodes.
        # New in 4.2: tnode list is in tnode.

        # Debugging.
        # if v.isAnyAtFileNode():
            # if hasattr(v.t,"tnodeList"):
                # g.trace(v.headString(),len(v.t.tnodeList))
            # else:
                # g.trace(v.headString(),"no tnodeList")

        if hasattr(v.t,"tnodeList") and len(v.t.tnodeList) > 0 and v.isAnyAtFileNode():
            if isThin:
                if g.app.unitTesting:
                    g.app.unitTestDict["warning"] = True
                g.es("deleting tnode list for",p.headString(),color="blue")
                # This is safe: cloning can't change the type of this node!
                delattr(v.t,"tnodeList")
            else:
                attrs.append(fc.putTnodeList(v)) # New in 4.0

        if hasattr(v,"unknownAttributes"): # New in 4.0
            attrs.append(self.putUnknownAttributes(v))

        if p.hasChildren() and not forceWrite and not self.usingClipboard:
            # We put the entire tree when using the clipboard, so no need for this.
            attrs.append(self.putDescendentUnknownAttributes(p))
            attrs.append(self.putDescendentAttributes(p))
        #@nonl
        #@-node:ekr.20040324082713:<< Append tnodeList and unKnownAttributes to attrs>>
        #@nl
        attrs = ''.join(attrs)
        v_head = '<v t="%s"%s><vh>%s</vh>' % (gnx,attrs,xml.sax.saxutils.escape(p.v.headString()or''))
        # The string catentation is faster than repeated calls to fc.put.
        if not self.usingClipboard:
            #@        << issue informational messages >>
            #@+node:ekr.20040702085529:<< issue informational messages >>
            if isOrphan and isThin:
                g.es("writing erroneous:",p.headString(),color="blue")
                p.clearOrphan()
            #@-node:ekr.20040702085529:<< issue informational messages >>
            #@nl
        # New in 4.2: don't write child nodes of @file-thin trees (except when writing to clipboard)
        if p.hasChildren() and (forceWrite or self.usingClipboard):
            fc.put('%s\n' % v_head)
            # This optimization eliminates all "recursive" copies.
            p.moveToFirstChild()
            while 1:
                fc.putVnode(p,isIgnore)
                if p.hasNext(): p.moveToNext()
                else:           break
            p.moveToParent() # Restore p in the caller.
            fc.put('</v>\n')
        else:
            fc.put('%s</v>\n' % v_head) # Call put only once.
    #@-node:ekr.20031218072017.1863:putVnode (3.x and 4.x)
    #@+node:ekr.20031218072017.2002:putTnodeList (4.0,4.2)
    def putTnodeList (self,v):

        """Put the tnodeList attribute of a tnode."""

        # Remember: entries in the tnodeList correspond to @+node sentinels, _not_ to tnodes!
        nodeIndices = g.app.nodeIndices
        tnodeList = v.t.tnodeList

        if tnodeList:
            # g.trace("%4d" % len(tnodeList),v)
            for t in tnodeList:
                try: # Will fail for None or any pre 4.1 file index.
                    junk,junk,junk = t.fileIndex
                except Exception:
                    gnx = nodeIndices.getNewIndex()
                    # Apparent bug fix: Leo 4.4.8, 2008-3-8: use t, not v.t here!
                    t.setFileIndex(gnx) # Don't convert to string until the actual write.
            s = ','.join([nodeIndices.toString(t.fileIndex) for t in tnodeList])
            return ' tnodeList="%s"' % (s)
        else:
            return ''
    #@nonl
    #@-node:ekr.20031218072017.2002:putTnodeList (4.0,4.2)
    #@+node:ekr.20040701065235.2:putDescendentAttributes
    def putDescendentAttributes (self,p):

        nodeIndices = g.app.nodeIndices

        # Create lists of all tnodes whose vnodes are marked or expanded.
        marks = [] ; expanded = []
        for p in p.subtree_iter():
            t = p.v.t
            if p.isMarked() and p.v.t not in marks:
                marks.append(t)
            if p.hasChildren() and p.isExpanded() and t not in expanded:
                expanded.append(t)

        result = []
        for theList,tag in ((marks,"marks"),(expanded,"expanded")):
            if theList:
                sList = []
                for t in theList:
                    # New in Leo 4.4.8.  Assign t.fileIndex here as needed.
                    if not t.fileIndex:
                        t.fileIndex = g.app.nodeIndices.getNewIndex()
                    gnx = t.fileIndex
                    sList.append("%s," % nodeIndices.toString(gnx))
                s = string.join(sList,'')
                # g.trace(tag,[str(p.headString()) for p in theList])
                result.append('\n%s="%s"' % (tag,s))

        return ''.join(result)
    #@-node:ekr.20040701065235.2:putDescendentAttributes
    #@+node:EKR.20040627113418:putDescendentUnknownAttributes
    def putDescendentUnknownAttributes (self,p):

        # pychecker complains about dumps.

        # The bin param doesn't exist in Python 2.3;
        # the protocol param doesn't exist in earlier versions of Python.
        version = '.'.join([str(sys.version_info[i]) for i in (0,1)])
        python23 = g.CheckVersion(version,'2.3')

        # Create a list of all tnodes having a valid unknownAttributes dict.
        tnodes = []
        tnodesData = []
        for p2 in p.subtree_iter():
            t = p2.v.t
            if hasattr(t,"unknownAttributes"):
                if t not in tnodes :
                    # g.trace(p2.headString(),t)
                    tnodes.append(t) # Bug fix: 10/4/06.
                    tnodesData.append((p2,t),)

        # Create a list of pairs (t,d) where d contains only pickleable entries.
        data = []
        for p,t in tnodesData:
            if type(t.unknownAttributes) != type({}):
                g.es("ignoring non-dictionary unknownAttributes for",p,color="blue")
            else:
                # Create a new dict containing only entries that can be pickled.
                d = dict(t.unknownAttributes) # Copy the dict.

                for key in d.keys():
                    try:
                        # We don't actually save the pickled values here.
                        if python23:
                            pickle.dumps(d[key],protocol=1) # Requires Python 2.3
                        else:
                            pickle.dumps(d[key],bin=True) # Requires earlier versions of Python.
                    except pickle.PicklingError:
                        del d[key]
                        g.es("ignoring bad unknownAttributes key",key,"in",p,color="blue")
                    except Exception:
                        del d[key]
                        g.es('putDescendentUnknownAttributes: unexpected pickling exception',color='red')
                        g.es_exception()
                data.append((t,d),)

        # Create resultDict, an enclosing dict to hold all the data.
        resultDict = {}
        nodeIndices = g.app.nodeIndices
        for t,d in data:
            # New in Leo 4.4.8.  Assign v.t.fileIndex here as needed.
            if not t.fileIndex:
                t.fileIndex = g.app.nodeIndices.getNewIndex()
            gnx = nodeIndices.toString(t.fileIndex)
            resultDict[gnx]=d

        if 0:
            print "resultDict..."
            for key in resultDict:
                print repr(key),repr(resultDict.get(key))

        # Pickle and hexlify resultDict.
        if resultDict:
            try:
                tag = "descendentTnodeUnknownAttributes"
                if python23:
                    s = pickle.dumps(resultDict,protocol=1) # Requires Python 2.3
                    # g.trace('protocol=1')
                else:
                    s = pickle.dumps(resultDict,bin=True) # Requires Earlier version of Python.
                    # g.trace('bin=True')
                field = ' %s="%s"' % (tag,binascii.hexlify(s))
                return field
            except pickle.PicklingError:
                g.trace("putDescendentUnknownAttributes can't happen 1",color="red")
            except Exception:
                g.es("putDescendentUnknownAttributes can't happen 2",color='red')
                g.es_exception()
        return ''
    #@-node:EKR.20040627113418:putDescendentUnknownAttributes
    #@-node:ekr.20031218072017.1579:putVnodes & helpers
    #@-node:ekr.20040324080819.1:putLeoFile & helpers
    #@+node:ekr.20031218072017.1573:putLeoOutline (to clipboard) & helper
    # Writes a Leo outline to s in a format suitable for pasting to the clipboard.

    def putLeoOutline (self):

        self.outputFile = g.fileLikeObject()
        self.usingClipboard = True

        self.putProlog()
        self.putClipboardHeader()
        self.putVnodes()
        self.putTnodes()
        self.putPostlog()

        s = self.outputFile.getvalue()
        self.outputFile = None
        self.usingClipboard = False
        return s
    #@+node:ekr.20031218072017.1971:putClipboardHeader
    def putClipboardHeader (self):

        c = self.c ; tnodes = 0
        #@    << count the number of tnodes >>
        #@+node:ekr.20031218072017.1972:<< count the number of tnodes >>
        c.clearAllVisited()

        for p in c.currentPosition().self_and_subtree_iter():
            t = p.v.t
            if t and not t.isWriteBit():
                t.setWriteBit()
                tnodes += 1
        #@-node:ekr.20031218072017.1972:<< count the number of tnodes >>
        #@nl
        self.put('<leo_header file_format="1" tnodes=')
        self.put_in_dquotes(str(tnodes))
        self.put(" max_tnode_index=")
        self.put_in_dquotes(str(tnodes))
        self.put("/>") ; self.put_nl()

        # New in Leo 4.4.3: Add dummy elements so copied nodes form a valid .leo file.
        self.put('<globals/>\n')
        self.put('<preferences/>\n')
        self.put('<find_panel_settings/>\n')
    #@-node:ekr.20031218072017.1971:putClipboardHeader
    #@-node:ekr.20031218072017.1573:putLeoOutline (to clipboard) & helper
    #@+node:ekr.20060919064401:putToOPML
    # All elements and attributes prefixed by ':' are leo-specific.
    # All other elements and attributes are specified by the OPML 1 spec.

    def putToOPML (self):

        '''Should be overridden by the opml plugin.'''

        return None
    #@nonl
    #@-node:ekr.20060919064401:putToOPML
    #@+node:ekr.20031218072017.3045:setDefaultDirectoryForNewFiles
    def setDefaultDirectoryForNewFiles (self,fileName):

        """Set c.openDirectory for new files for the benefit of leoAtFile.scanAllDirectives."""

        c = self.c

        if not c.openDirectory or len(c.openDirectory) == 0:
            theDir = g.os_path_dirname(fileName)

            if len(theDir) > 0 and g.os_path_isabs(theDir) and g.os_path_exists(theDir):
                c.openDirectory = theDir
    #@-node:ekr.20031218072017.3045:setDefaultDirectoryForNewFiles
    #@+node:ekr.20031218072017.3046:write_Leo_file
    def write_Leo_file(self,fileName,outlineOnlyFlag,toString=False,toOPML=False):

        c = self.c
        self.putCount = 0
        self.toString = toString
        theActualFile = None
        toZip = False

        if not outlineOnlyFlag or toOPML:
            # Update .leoRecentFiles.txt if possible.
            g.app.config.writeRecentFilesFile(c)
            #@        << write all @file nodes >>
            #@+node:ekr.20040324080359:<< write all @file nodes >>
            try:
                # Write all @file nodes and set orphan bits.
                # An important optimization: we have already assign the file indices.
                c.atFileCommands.writeAll()
            except Exception:
                g.es_error("exception writing derived files")
                g.es_exception()
                return False
            #@-node:ekr.20040324080359:<< write all @file nodes >>
            #@nl
        #@    << return if the .leo file is read-only >>
        #@+node:ekr.20040324080359.1:<< return if the .leo file is read-only >>
        # self.read_only is not valid for Save As and Save To commands.

        if g.os_path_exists(fileName):
            try:
                if not os.access(fileName,os.W_OK):
                    g.es("can not create: read only:",fileName,color="red")
                    return False
            except Exception:
                pass # os.access() may not exist on all platforms.
        #@-node:ekr.20040324080359.1:<< return if the .leo file is read-only >>
        #@nl
        try:
            #@        << create backup file >>
            #@+node:ekr.20031218072017.3047:<< create backup file >>
            backupName = None

            # rename fileName to fileName.bak if fileName exists.
            if not toString and g.os_path_exists(fileName):
                backupName = g.os_path_join(g.app.loadDir,fileName)
                backupName = fileName + ".bak"
                if g.os_path_exists(backupName):
                    g.utils_remove(backupName)
                ok = g.utils_rename(c,fileName,backupName)
                if not ok:
                    if self.read_only:
                        g.es("read only",color="red")
                    return False
            #@nonl
            #@-node:ekr.20031218072017.3047:<< create backup file >>
            #@nl
            self.mFileName = fileName
            if toOPML:
                #@            << ensure that filename ends with .opml >>
                #@+node:ekr.20060919070145:<< ensure that filename ends with .opml >>
                if not self.mFileName.endswith('opml'):
                    self.mFileName = self.mFileName + '.opml'
                fileName = self.mFileName
                #@nonl
                #@-node:ekr.20060919070145:<< ensure that filename ends with .opml >>
                #@nl
            self.outputFile = cStringIO.StringIO()
            #@        << create theActualFile >>
            #@+node:ekr.20060929103258:<< create theActualFile >>
            if toString:
                theActualFile = None
            elif c.isZipped:
                self.toString = toString = True
                theActualFile = None
                toZip = True
            else:
                theActualFile = open(fileName, 'wb')
            #@-node:ekr.20060929103258:<< create theActualFile >>
            #@nl
            # t1 = time.clock()
            if toOPML:
                self.putToOPML()
            else:
                # An important optimization: we have already assign the file indices.
                self.putLeoFile()
            # t2 = time.clock()
            s = self.outputFile.getvalue()
            # g.trace(self.leo_file_encoding)
            if toZip:
                self.writeZipFile(s)
            elif toString:
                # For support of chapters plugin.
                g.app.write_Leo_file_string = s
            else:
                theActualFile.write(s)
                theActualFile.close()
                #@            << delete backup file >>
                #@+node:ekr.20031218072017.3048:<< delete backup file >>
                if backupName and g.os_path_exists(backupName):

                    self.deleteFileWithMessage(backupName,'backup')
                #@-node:ekr.20031218072017.3048:<< delete backup file >>
                #@nl
                # t3 = time.clock()
                # g.es_print('len',len(s),'putCount',self.putCount) # 'put',t2-t1,'write&close',t3-t2)
            self.outputFile = None
            self.toString = False
            return True
        except Exception:
            g.es("exception writing:",fileName)
            g.es_exception(full=True)
            if theActualFile: theActualFile.close()
            self.outputFile = None
            if backupName:
                #@            << delete fileName >>
                #@+node:ekr.20050405103712:<< delete fileName >>
                if fileName and g.os_path_exists(fileName):

                    self.deleteFileWithMessage(fileName,'')
                #@-node:ekr.20050405103712:<< delete fileName >>
                #@nl
                #@            << rename backupName to fileName >>
                #@+node:ekr.20050405103712.1:<< rename backupName to fileName >>
                if backupName:
                    g.es("restoring",fileName,"from",backupName)
                    g.utils_rename(c,backupName,fileName)
                #@-node:ekr.20050405103712.1:<< rename backupName to fileName >>
                #@nl
            self.toString = False
            return False

    write_LEO_file = write_Leo_file # For compatibility with old plugins.
    #@+node:ekr.20070412095520:writeZipFile
    def writeZipFile (self,s):

        # The name of the file in the archive.
        contentsName = g.toEncodedString(
            g.shortFileName(self.mFileName),
            self.leo_file_encoding,reportErrors=True)

        # The name of the archive itself.
        fileName = g.toEncodedString(
            self.mFileName,
            self.leo_file_encoding,reportErrors=True)

        # Write the archive.
        theFile = zipfile.ZipFile(fileName,'w',zipfile.ZIP_DEFLATED)
        theFile.writestr(contentsName,s)
        theFile.close()
    #@-node:ekr.20070412095520:writeZipFile
    #@-node:ekr.20031218072017.3046:write_Leo_file
    #@+node:ekr.20031218072017.2012:writeAtFileNodes
    def writeAtFileNodes (self,event=None):

        '''Write all @file nodes in the selected outline.'''

        c = self.c

        changedFiles = c.atFileCommands.writeAll(writeAtFileNodesFlag=True)

        if changedFiles:
            g.es("auto-saving outline",color="blue")
            c.save() # Must be done to set or clear tnodeList.
    #@-node:ekr.20031218072017.2012:writeAtFileNodes
    #@+node:ekr.20031218072017.1666:writeDirtyAtFileNodes
    def writeDirtyAtFileNodes (self,event=None):

        '''Write all changed @file Nodes.'''

        c = self.c

        changedFiles = c.atFileCommands.writeAll(writeDirtyAtFileNodesFlag=True)

        if changedFiles:
            g.es("auto-saving outline",color="blue")
            c.save() # Must be done to set or clear tnodeList.
    #@-node:ekr.20031218072017.1666:writeDirtyAtFileNodes
    #@+node:ekr.20031218072017.2013:writeMissingAtFileNodes
    def writeMissingAtFileNodes (self,event=None):

        '''Write all missing @file nodes.'''

        c = self.c ; at = c.atFileCommands ; p = c.currentPosition()

        if p:
            changedFiles = at.writeMissing(p)
            if changedFiles:
                g.es("auto-saving outline",color="blue")
                c.save() # Must be done to set or clear tnodeList.
    #@-node:ekr.20031218072017.2013:writeMissingAtFileNodes
    #@+node:ekr.20031218072017.3050:writeOutlineOnly
    def writeOutlineOnly (self,event=None):

        '''Write the entire outline without writing any derived files.'''

        c = self.c
        c.endEditing()
        self.write_Leo_file(self.mFileName,outlineOnlyFlag=True)
        g.es('done',color='blue')
    #@-node:ekr.20031218072017.3050:writeOutlineOnly
    #@-node:ekr.20031218072017.3032:Writing
    #@-others

class fileCommands (baseFileCommands):
    """A class creating the fileCommands subcommander."""
    pass
#@nonl
#@-node:ekr.20031218072017.3018:@thin leoFileCommands.py
#@-leo

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
import re

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
        def __init__ (self,c,fileName,silent,inClipboard):

            self.c = c
            self.fileName = fileName
            self.silent = silent
            self.inClipboard = inClipboard

            # Init the base class.
            xml.sax.saxutils.XMLGenerator.__init__(self)

            #@    << define dispatch dict >>
            #@+node:ekr.20060919110638.21:<< define dispatch dict >>
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
            self.elementStack = []
            self.errors = 0
            self.tnxToListDict = {} # Keys are tnx's (strings), values are *lists* of saxNodeClass objects.
            self.level = 0
            self.node = None
            self.nodeList = [] # List of saxNodeClass objects with the present tnode.
            self.nodeStack = []
            self.rootNode = None # a sax node.
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

            if 0: # check for non-unicode attributes.
                for name in attrs.getNames():
                    val = attrs.getValue(name)
                    if type(val) != type(u''):
                        g.trace('Non-unicode attribute',name,val)

            # g.trace(g.listToString([repr(z) for z in attrs.getNames()]))

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
                if 1: g.trace('unknown end element',name)
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
        #@+node:ekr.20060919110638.45:getRootNode
        def getRootNode (self):
            return self.rootNode
        #@-node:ekr.20060919110638.45:getRootNode
        #@+node:ekr.20061004054323:processingInstruction (stylesheet)
        def processingInstruction (self,target,data):

            if target == 'xml-stylesheet':
                self.c.frame.stylesheet = data
                if False and not self.silent:
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
                if 1: g.trace('unknown start element',name)
            else:
                func,junk = data
                if func:
                    func(attrs)
        #@nonl
        #@+node:ekr.20060919110638.36:getPositionAttributes
        def getPositionAttributes (self,attrs):

            c = self.c

            if c.fixed and c.fixedWindowPosition:
                width,height,left,top = c.fixedWindowPosition
                d = {'top':top,'left':left,'width':width,'height':height}
            else:
                d = {}
                for bunch in self.attrsToList(attrs):
                    name = bunch.name ; val = bunch.val
                    if name in ('top','left','width','height'):
                        try:
                            d[name] = int(val)
                        except ValueError:
                            d[name] = 100 # A reasonable default.
                    else:
                        g.trace(name,len(val))

            return d
        #@-node:ekr.20060919110638.36:getPositionAttributes
        #@+node:ekr.20060919110638.37:startGlobals
        def startGlobals (self,attrs):

            for bunch in self.attrsToList(attrs):
                name = bunch.name ; val = bunch.val

                if name == 'body_outline_ratio':
                    # self.body_outline_ratio = val
                    if not self.inClipboard:
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

            if self.inClipboard:
                return # No need to do anything to the main window.

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
            print 'node: tnx: %s len(body): %d %s' % (
                self.tnx,len(self.bodyString),self.headString)
            print 'children:',g.listToString(self.children)
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

        self.currentVnode = None
        self.rootVnode = None

        # For writing
        self.read_only = False
        self.rootPosition = None
        self.outputFile = None
        self.openDirectory = None
        self.putCount = 0
        # self.topVnode = None
        self.toString = False
        self.usingClipboard = False
        self.currentPosition = None
        # New in 3.12
        self.copiedTree = None
        self.tnodesDict = {}
            # keys are gnx strings as returned by canonicalTnodeIndex.
            # Values are gnx's.
    #@-node:ekr.20031218072017.3019:leoFileCommands._init_
    #@+node:ekr.20031218072017.3020:Reading
    #@+node:ekr.20060919104836: Top-level
    #@+node:ekr.20070919133659.1:checkLeoFile (fileCommands)
    def checkLeoFile (self,event=None):

        '''The check-leo-file command.'''

        fc = self ; c = fc.c ; p = c.currentPosition()

        # Put the body (minus the @nocolor) into the file buffer.
        s = p.bodyString() ; tag = '@nocolor\n'
        if s.startswith(tag): s = s[len(tag):]
        # self.fileBuffer = s ; self.fileBufferIndex = 0

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

        c = self.c ; current = c.currentPosition() ; check = not reassignIndices

        # Save the hidden root's children.
        children = c.hiddenRootNode.t.children

        # Always recreate the tnodesDict
        self.tnodesDict = {}
        if not reassignIndices:
            x = g.app.nodeIndices
            for t in c.all_unique_tnodes_iter():
                index = x.toString(t.fileIndex)
                self.tnodesDict[index] = t

        self.usingClipboard = True
        try:
            # This encoding must match the encoding used in putLeoOutline.
            s = g.toEncodedString(s,self.leo_file_encoding,reportErrors=True)

            # readSaxFile modifies the hidden root.
            v = self.readSaxFile(
                theFile=None, fileName='<clipboard>',
                silent=True, # don't tell about stylesheet elements.
                inClipboard=True, reassignIndices=reassignIndices,s=s)
            if not v:
                return g.es("the clipboard is not valid ",color="blue")
        finally:
            self.usingClipboard = False

            # Restore the hidden root's children
            c.hiddenRootNode.t.children = children

        p = leoNodes.position(v)
        if current.hasChildren() and current.isExpanded():
            if check and not self.checkPaste(current,p): return None
            p._linkAsNthChild(current,0)
        else:
            if check and not self.checkPaste(current.parent(),p): return None
            p._linkAfter(current)

        if reassignIndices:
            for p2 in p.self_and_subtree_iter():
                p2.v.t.fileIndex = None

        self.initAllParents()

        if c.config.getBool('check_outline_after_read'):
            c.checkOutline(event=None,verbose=True,unittest=False,full=True)

        c.selectPosition(p)
        return p

    getLeoOutline = getLeoOutlineFromClipboard # for compatibility
    #@+node:ekr.20080410115129.1:checkPaste
    def checkPaste (self,parent,p):

        '''Return True if p may be pasted as a child of parent.'''

        if not parent: return True

        parents = [z.copy() for z in parent.self_and_parents_iter()]

        for p in p.self_and_subtree_iter():
            for z in parents:
                # g.trace(p.headString(),id(p.v.t),id(z.v.t))
                if p.v.t == z.v.t:
                    g.es('Invalid paste: nodes may not descend from themselves',color="blue")
                    return False

        return True
    #@-node:ekr.20080410115129.1:checkPaste
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
            v = self.readSaxFile(theFile,fileName,silent,inClipboard=False,reassignIndices=False)
            if v: # v is None for minimal .leo files.
                c.setRootVnode(v)
                self.rootVnode = v
            else:
                t = leoNodes.tnode(headString='created root node')
                v = leoNodes.vnode(context=c,t=t)
                p = leoNodes.position(v)
                p._linkAsRoot(oldRoot=None)
                self.rootVnode = v
                c.setRootPosition(p)
                c.changed = False
        except BadLeoFile, message:
            if not silent:
                g.es_exception()
                g.alert(self.mFileName + " is not a valid Leo file: " + str(message))
            ok = False

        # Do this before reading derived files.
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

        self.setPositionsFromVnodes()
        c.selectVnode(c.currentPosition()) # load body pane

        self.initAllParents()

        if c.config.getBool('check_outline_after_read'):
            c.checkOutline(event=None,verbose=True,unittest=False,full=True)

        c.loading = False # reenable c.changed
        c.setChanged(c.changed) # Refresh the changed marker.
        self.initReadIvars()
        return ok, self.ratio
    #@-node:ekr.20031218072017.1553:getLeoFile
    #@+node:ekr.20080428055516.3:initAllParents
    def initAllParents(self):

        '''Properly init the parents list of all vnodes.'''

        # An important point: the iter below does not depend on any parent list.

        c = self.c ; trace = False

        if trace:
            import time
            t1 = time.time()

        # This takes about 0.15 sec for this file.
        c.hiddenRootNode._computeParentsOfChildren()

        for v in c.all_unique_vnodes_iter():
            v._computeParentsOfChildren()

        if trace:
            t2 = time.time()
            g.trace(t2-t1)
    #@-node:ekr.20080428055516.3:initAllParents
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
                t.fileIndex = gnx

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

        ok, ratio = self.getLeoFile(
            theFile,fileName,
            readAtFileNodesFlag=readAtFileNodesFlag,
            silent=silent)
        frame.resizePanesToRatio(ratio,frame.secondary_ratio)

        return ok
    #@-node:ekr.20031218072017.2297:open (leoFileCommands)
    #@+node:ekr.20031218072017.3030:readOutlineOnly
    def readOutlineOnly (self,theFile,fileName):

        c = self.c

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

        c = self.c ; verbose = True and not g.unitTesting

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
            for p in c.all_positions_with_unique_vnodes_iter():
                if marks.get(p.v.t):
                    p.v.initMarkedBit()
                        # This was the problem: was p.setMark.
                        # There was a big performance bug in the mark hook in the Node Navigator plugin.
                if expanded.get(p.v.t):
                    p.expand()
    #@-node:EKR.20040627120120:restoreDescendentAttributes
    #@-node:ekr.20060919133249:Common
    #@+node:ekr.20060919104530:Sax (reading)
    #@+node:ekr.20060919110638.4:createSaxVnodes & helpers
    def createSaxVnodes (self,saxRoot,reassignIndices):

        '''**Important**: this method and its helpers are low-level code
        corresponding to link/unlink methods in leoNodes.py.
        Modify this with extreme care.'''


        parent_v = self.c.hiddenRootNode

        children = self.createSaxChildren(saxRoot,parent_v=parent_v)

        return children
    #@+node:ekr.20060919110638.5:createSaxChildren
    def createSaxChildren (self, sax_node, parent_v):

        children = []

        for child in sax_node.children:
            tnx = child.tnx
            t = self.tnodesDict.get(tnx)
            if t:
                # A clone.  Create a new clone vnode, but share the subtree, i.e., the tnode.
                # g.trace('**clone',v)
                v = self.createSaxVnode(child,parent_v,t=t)
            else:
                v = self.createSaxVnodeTree(child,parent_v)

            # Add all items in v.t.vnodeList to parents of grandchildren.
            v._computeParentsOfChildren()

            children.append(v)

        self._linkParentAndChildren(parent_v,children)

        return children
    #@-node:ekr.20060919110638.5:createSaxChildren
    #@+node:ekr.20060919110638.6:createSaxVnodeTree
    def createSaxVnodeTree (self,sax_node,parent_v):

        v = self.createSaxVnode(sax_node,parent_v)

        self.createSaxChildren(sax_node,v)

        return v
    #@nonl
    #@-node:ekr.20060919110638.6:createSaxVnodeTree
    #@+node:ekr.20060919110638.7:createSaxVnode
    def createSaxVnode (self,sax_node,parent_v,t=None):

        c = self.c
        trace = False and self.usingClipboard
        h = sax_node.headString
        b = sax_node.bodyString

        if t:
            if trace: g.trace('clone',t,h)
        else:
            t = leoNodes.tnode(bodyString=b,headString=h)
            if trace: g.trace('     ',t,h)

            if sax_node.tnx:
                t.fileIndex = g.app.nodeIndices.scanGnx(sax_node.tnx,0)

        v = leoNodes.vnode(context=c,t=t)
        v.t.vnodeList.append(v)

        index = self.canonicalTnodeIndex(sax_node.tnx)

        self.tnodesDict [index] = t

        # g.trace('tnx','%-22s' % (index),'v',id(v),'v.t',id(v.t),'body','%-4d' % (len(b)),h)

        self.handleVnodeSaxAttributes(sax_node,v)
        self.handleTnodeSaxAttributes(sax_node,t)

        return v
    #@+node:ekr.20060919110638.8:handleTnodeSaxAttributes
    def handleTnodeSaxAttributes (self,sax_node,t):

        d = sax_node.tnodeAttributes

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

    def handleVnodeSaxAttributes (self,sax_node,v):

        d = sax_node.attributes
        s = d.get('a')
        if s:
            # g.trace('%s a=%s %s' % (id(sax_node),s,v.headString()))
            # 'C' (clone) and 'D' bits are not used.
            if 'M' in s: v.setMarked()
            if 'E' in s: v.expand()
            if 'O' in s: v.setOrphan()
            # if 'T' in s: self.topVnode = v
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
    #@+node:ekr.20060919110638.9:p._linkParentAndChildren
    def _linkParentAndChildren (self, parent_v, children):

        # if children: g.trace(parent_v,len(children))

        # Add parent_v to it's tnode's vnodeList.
        if parent_v not in parent_v.t.vnodeList:
            parent_v.t.vnodeList.append(parent_v)

        # Set parent_v's children.
        parent_v.t.children = children

        # Make parent_v a parent of each child.
        parent_v._computeParentsOfChildren()

    #@-node:ekr.20060919110638.9:p._linkParentAndChildren
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
    def parse_leo_file (self,theFile,inputFileName,silent,inClipboard,s=None):

        c = self.c
        # g.trace('hiddenRootNode',c.hiddenRootNode)

        try:
            # Use cStringIo to avoid a crash in sax when inputFileName has unicode characters.
            if theFile:
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
            handler = saxContentHandler(c,inputFileName,silent,inClipboard)
            parser.setContentHandler(handler)
            parser.parse(theFile) # expat does not support parseString
            sax_node = handler.getRootNode()
        except xml.sax.SAXParseException:
            g.es_print('error parsing',inputFileName,color='red')
            g.es_exception()
        except Exception:
            g.es_print('unexpected exception parsing',inputFileName,color='red')
            g.es_exception()

        return sax_node
    #@nonl
    #@-node:ekr.20060919110638.14:parse_leo_file
    #@+node:ekr.20060919110638.3:readSaxFile
    def readSaxFile (self,theFile,fileName,silent,inClipboard,reassignIndices,s=None):

        # Pass one: create the intermediate nodes.
        saxRoot = self.parse_leo_file(theFile,fileName,
            silent=silent,inClipboard=inClipboard,s=s)

        # self.dumpSaxTree(saxRoot,dummy=True)

        # Pass two: create the tree of vnodes and tnodes from the intermediate nodes.
        if saxRoot:
            children = self.createSaxVnodes(saxRoot,reassignIndices=reassignIndices)
            # g.trace('children',children)
            self.c.hiddenRootNode.t.children = children
            v = children and children[0] or None
            return v
        else:
            return None
    #@-node:ekr.20060919110638.3:readSaxFile
    #@+node:ekr.20060919110638.11:resolveTnodeLists
    def resolveTnodeLists (self):

        c = self.c

        for p in c.all_positions_with_unique_vnodes_iter():
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
            # g.trace('oops: bad archived position. not an int:',aList,c)
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
                    # g.trace('oops: bad archived position. no sibling:',aList,p.headString(),c)
                    return None
            level += 1
            if level < len(aList):
                p.moveToFirstChild()
                # g.trace('level',level,'index',aList[level],p.headString())
        return p
    #@nonl
    #@-node:ekr.20061006104837.1:archivedPositionToPosition
    #@-node:ekr.20060919110638.13:setPositionsFromVnodes & helper
    #@-node:ekr.20060919104530:Sax (reading)
    #@-node:ekr.20031218072017.3020:Reading
    #@+node:ekr.20031218072017.3032:Writing
    #@+node:ekr.20070413045221.2: Top-level  (leoFileCommands)
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
                self.putSavedMessage(fileName)
                if ok:
                    c.setChanged(False) # Clears all dirty bits.
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
    #@-node:ekr.20070413045221.2: Top-level  (leoFileCommands)
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

        # New in Leo 4.5: support fixed .leo files.
        self.put_in_dquotes(
            str(g.choose(c.fixed,0.5,c.frame.ratio)))
        #@-node:ekr.20031218072017.3038:<< put the body/outline ratio >>
        #@nl
        self.put(">") ; self.put_nl()
        #@    << put the position of this frame >>
        #@+node:ekr.20031218072017.3039:<< put the position of this frame >>
        # New in Leo 4.5: support fixed .leo files.

        if c.fixed:
            width,height,left,top = 700,500,50,50
                # Put fixed, immutable, reasonable defaults.
                # Leo 4.5 and later will ignore these when reading.
                # These should be reasonable defaults so that the
                # file will be opened properly by older versions
                # of Leo that do not support fixed .leo files.
        else:
            width,height,left,top = c.frame.get_window_info()

        # g.trace(width,height,left,top)

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

        if 1: # For compatibility with versions before Leo 4.5.
            self.put("<leo_header")
            self.put(" file_format=") ; self.put_in_dquotes("2")
            self.put(" tnodes=") ; self.put_in_dquotes(str(tnodes))
            self.put(" max_tnode_index=") ; self.put_in_dquotes(str(0))
            self.put(" clone_windows=") ; self.put_in_dquotes(str(clone_windows))
            self.put("/>") ; self.put_nl()

        else:
            self.put('<leo_header file_format="2"/>\n')
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
        body = t._bodyString and xml.sax.saxutils.escape(t._bodyString) or ''
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
            theIter = c.all_positions_with_unique_tnodes_iter()

        # Populate tnodes
        tnodes = {}
        nodeIndices = g.app.nodeIndices
        for p in theIter:
            # New in Leo 4.4.8: assign file indices here.
            if not p.v.t.fileIndex:
                p.v.t.fileIndex = nodeIndices.getNewIndex()
            tnodes[p.v.t.fileIndex] = p.v.t

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

            val = ''.join([self.putUaHelper(torv,key,val) for key,val in attrDict.items()])
            # g.trace(torv,attrDict,g.callers())
            return val
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
        # self.topPosition     = c.topPosition()

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
        # New in Leo 4.5: support fixed .leo files.
        if not c.fixed:
            if v.isExpanded() and v.hasChildren(): attr += "E"
            if v.isMarked():   attr += "M"
            if v.isOrphan():   attr += "O"

            # No longer a bottleneck now that we use p.equal rather than p.__cmp__
            # Almost 30% of the entire writing time came from here!!!
            # if not self.use_sax:
                # if p.equal(self.topPosition):     attr += "T" # was a bottleneck
                # if p.equal(self.currentPosition): attr += "V" # was a bottleneck

            if attr:
                attrs.append(' a="%s"' % attr)

        # Put the archived *current* position in the *root* positions <v> element.
        if p == self.rootPosition:
            aList = [str(z) for z in self.currentPosition.archivedPosition()]
            d = hasattr(v,'unKnownAttributes') and v.unknownAttributes or {}
            if not c.fixed:
                d['str_leo_pos'] = ','.join(aList)
            # g.trace(aList,d)
            v.unknownAttributes = d
        elif hasattr(v,"unknownAttributes"):
            d = v.unknownAttributes
            if d and not c.fixed and d.get('str_leo_pos'):
                # g.trace("clearing str_leo_pos",v)
                del d['str_leo_pos']
                v.unknownAttributes = d
        #@-node:ekr.20031218072017.1865:<< Append attribute bits to attrs >>
        #@nl
        #@    << Append tnodeList and unKnownAttributes to attrs >>
        #@+node:ekr.20040324082713:<< Append tnodeList and unKnownAttributes to attrs>>
        # Write the tnodeList only for @file nodes.
        # New in 4.2: tnode list is in tnode.

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
                    # t.setFileIndex(gnx) # Don't convert to string until the actual write.
                    t.fileIndex = gnx
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
    def putLeoOutline (self):

        '''Return a string, *not unicode*, encoded with self.leo_file_encoding,
        suitable for pasting to the clipboard.'''

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

        if 1: # Put the minimum header for sax.
            self.put('<leo_header file_format="2"/>\n')

        else: # Put the header for the old read code.
            #@        << count the number of tnodes >>
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
    #@+node:ekr.20080412172151.2:updateFixedStatus
    def updateFixedStatus (self):

        c = self.c
        p = g.app.config.findSettingsPosition(c,'@bool fixedWindow')
        if p:
            import leoConfig
            parser = leoConfig.settingsTreeParser(c)
            kind,name,val = parser.parseHeadline(p.headString())
            if val and val.lower() in ('true','1'):
                val = True
            else:
                val = False
            c.fixed = val

        # g.trace('c.fixed',c.fixed)
    #@-node:ekr.20080412172151.2:updateFixedStatus
    #@+node:ekr.20031218072017.3046:write_Leo_file
    def write_Leo_file(self,fileName,outlineOnlyFlag,toString=False,toOPML=False):

        c = self.c
        self.putCount = 0
        self.toString = toString
        theActualFile = None
        toZip = False
        atOk = True

        if not outlineOnlyFlag or toOPML:
            # Update .leoRecentFiles.txt if possible.
            g.app.config.writeRecentFilesFile(c)
            #@        << write all @file nodes >>
            #@+node:ekr.20040324080359:<< write all @file nodes >>
            try:
                # Write all @file nodes and set orphan bits.
                # An important optimization: we have already assign the file indices.
                changedFiles,atOk = c.atFileCommands.writeAll()
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
                    g.es("can not write: read only:",fileName,color="red")
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
            return atOk
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

        changedFiles,atOk = c.atFileCommands.writeAll(writeAtFileNodesFlag=True)

        if changedFiles:
            g.es("auto-saving outline",color="blue")
            c.save() # Must be done to set or clear tnodeList.
    #@-node:ekr.20031218072017.2012:writeAtFileNodes
    #@+node:ekr.20031218072017.1666:writeDirtyAtFileNodes
    def writeDirtyAtFileNodes (self,event=None):

        '''Write all changed @file Nodes.'''

        c = self.c

        changedFiles,atOk = c.atFileCommands.writeAll(writeDirtyAtFileNodesFlag=True)

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

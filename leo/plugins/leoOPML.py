#@+leo-ver=5-thin
#@+node:ekr.20101110092851.5742: * @file leoOPML.py
#@+<< docstring >>
#@+node:ekr.20060904103412.1: ** << docstring >>
r'''A plugin to read and write Leo outlines in .opml (http://en.wikipedia.org/wiki/OPML) format.

Warning: the OPML plugin is not fully functional at present. Use with caution.

The OPML plugin creates two new commands that read and write Leo outlines in OPML format.
The read-opml-file command creates a Leo outline from an .opml file.
The write-opml-file command writes the present Leo outline to an .opml file.

Various settings control what gets written to .opml files, and in what format.
As usual, you specify settings for the OPML plugin using leoSettings.leo.
The settings for the OPML are found in the node: @settings-->Plugins-->opml plugin

Here are the settings that control the format of .opml files. The default values are shown.

- @string opml_namespace = leo:com:leo-opml-version-1

The namespace urn for the xmlns attribute of <opml> elements.
This value typically is not used, but it should refer to Leo in some way.

- @bool opml_use_outline_elements = True

- If True, Leo writes body text to <leo:body> elements nested in <outline> elements.
Otherwise, Leo writes body text to leo:body attributes of <outline> elements.

- @string opml_version = 2.0

The opml version string written to the <OPML> element.
Use 2.0 unless there is a specific reason to use 1.0.

- @bool opml_write_body_text = True

Leo writes body text to the OPML file only if this is True.

- @bool opml_write_leo_details = True

If True, Leo writes the native attributes of Leo's <v> elements as attributes of
the opml <outline> elements. The native attributes of <v> elements are a,
descendentTnodeUnknownAttributes, expanded, marks, t, and tnodeList.

- @bool opml_write_leo_globals_attributes = True

If True, Leo writes body_outline_ratio` and global_window_position attributes to
the <head> element of the .opml file.

- @bool opml_write_ua_attributes

If True, write unknownAttributes  **NOTE** ua_attributes are not currently read from opml

- @bool opml_expand_ua_dictionary

If True, expand an unknownAttriubte 'x' of type dict to 'ua_x_key0', 'ua_x_key1' etc.
**WARNING** using this feature may prevent reading these ua_attributes from opml,
if that feature is implemented in the future.

- @bool opml_skip_ua_dictionary_blanks

If True, when expanding as above, skip blank dict entries.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@+<< to do >>
#@+node:ekr.20060920112018: ** << to do >>
#@@nocolor
#@+at
# 
# - Enhance open/save commands when this plugin is active.
# 
# - read/write uA's.
#@-<< to do >>

__version__ = '0.93'

# For traces.
printElements = [] # ['all','outline','head','body',]

#@+<< version history >>
#@+node:ekr.20060904103412.2: ** << version history >>
#@@killcolor
#@+at
# 
# 0.01 EKR: Initial version.
# 0.02 EKR: This plugin overrides leoFileCommands.fileCommands.putToOPML.
# - Changes to Leo's core:
#     - Added toOPML=False keyword argument to write_Leo_file.
#     - Added dummy putToOPML method.
# 0.03 EKR: Use SAX to read .opml files.  Parsing works.  More semantics are needed.
# 0.04 EKR: Simplified the code.
# 0.05 EKR: Outline created with proper headlines: (wrote & debugged createVnodes & helpers)
# 0.06 EKR: Rewrote createChildren.  It's simpler and appears to handle clones properly.
# 0.07 EKR: Revised code using saxRead plugin as a model.
# All strings are now assumed to be unicode.
# 0.08 EKR: Leo can now read and write body and headline text properly.
# - Use xml.sax.saxutils to quote attributes properly.
# - Improved error handling in parse_opml_file.
# 0.1 EKR: Write and read a attributes (marks, expanded, etc.)
# 0.1.1 EKR: Added resolveTnodeLists and related logic.
# 0.1.2 EKR: Moved parse_opml_file into opmlController class, as is done in the saxRead plugin.
# 0.2 EKR: Moved putToOPML and its helpers to Leo's core, so there is no need to subclass any fileCommands class.
# Future plugins could customize these methods, but configuration settings would be better.
# 0.3 EKR: Do not call toUnicode: sax should already have done that.
# 0.4 EKR: No change to opml plugin, but defined fc.attributeEscape to convert newlines to '&#10;\n'
# This overcomes the sax parser's tendency to strip newlines from attributes.  Sheesh.
# 0.5 EKR: Added support for namespaces.  The beginnings of opml settings.
# 0.6 EKR: Moved write code back into plugin.  It is more convenient and flexible.
# - Added support for opml_use_outline_elements, opml_write_leo_details and opml_write_body_text
#   settings in leoSettings.leo.
# - The read code no longer requires tnx fields.
# 0.7 EKR: Support for opml_version.  Reading and writing works (except for tnodeLists) regardless of settings.
# 0.8 EKR: This plugin now creates the read/write-opml-file commands.
# 0.9 EKR: Improved docstring.
# 0.91 EKR: reading derived files appears to work:
# - create c.fileCommands.tnodeDict before calling c.atFileCommands.readAll.
# - Properly init t.fileIndex to an actual gnx using scanGnx.
# 0.92 EKR: Support for opml_write_leo_globals_attributes setting:
# - Read and write leo:body_outline_ratio attribute and <leo:global_window_position> element.
# 0.93 EKR: Support opml_read_derived_files & opml_write_derived_files
# 0.94 TNB: write unknownAttributes, use leo: rather than just : for namespace, tweaked SAX content reading
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20060904103412.3: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import leo.core.leoNodes as leoNodes
import leo.core.leoFileCommands as leoFileCommands

import xml.sax
import xml.sax.saxutils
#@-<< imports >>

#@+others
#@+node:ekr.20060904132527.9: ** Module level
#@+node:ekr.20060904103412.4: *3* init
def init ():

    # Override the base class
    leoPlugins.registerHandler('start1',onStart2)

    # Register the commands.
    leoPlugins.registerHandler(('open2','new'),onCreate)

    g.plugin_signon(__name__)

    return True
#@+node:ekr.20060904103412.5: *3* onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if c:
        opmlController(c)
#@+node:ekr.20060919172012: *3* onStart2
def onStart2 (tag,keys):

    # Override the fileCommands class by opmlFileCommandsClass.
    leoFileCommands.fileCommands = opmlFileCommandsClass
#@+node:ekr.20060919172012.1: ** class opmlFileCommandsClass (fileCommands)
class opmlFileCommandsClass (leoFileCommands.fileCommands):

    '''An subclass of Leo's core fileCommands class that
    should do *nothing* other than override putToOPML.'''

    #@+others
    #@+node:ekr.20060919172012.2: *3* putToOPML & helpers
    # All elements and attributes prefixed by 'leo:' are leo-specific.
    # All other elements and attributes are specified by the OPML 1 spec.

    def putToOPML (self):

        c = self.c

        for ivar in (
            'opml_use_outline_elements',
            'opml_write_derived_files',
            'opml_write_leo_details',
            'opml_write_leo_globals_attributes',
            'opml_write_body_text',
            'opml_write_ua_attributes',
            'opml_expand_ua_dictionary',
            'opml_skip_ua_dictionary_blanks',
        ):
            setattr(self,ivar,c.config.getBool(ivar))

        self.putXMLLine()
        self.putOPMLProlog()
        self.putOPMLHeader()
        self.putOPMLNodes()
        self.putOPMLPostlog()
    #@+node:ekr.20060919172012.3: *4* putOPMLProlog
    def putOPMLProlog (self):

        s   = self.c.config.getString('opml_namespace') or 'leo:com:leo-opml'
        ver = self.c.config.getString('opml_version') or '2.0'

        self.put('<opml version="%s" xmlns:leo="%s">' % (ver,s))
    #@+node:ekr.20060919172012.4: *4* putOPMLHeader
    def putOPMLHeader (self):

        '''Put the OPML header, including attributes for globals, prefs and  find settings.'''

        c = self.c ; indent = ' ' * 4

        if self.opml_write_leo_globals_attributes:
            self.put('\n<head leo:body_outline_ratio="%s">' % str(c.frame.ratio))

            width,height,left,top = c.frame.get_window_info()

            self.put('\n%s<leo:global_window_position' % indent)
            self.put(' top="%s" left="%s" height="%s" width="%s"/>' % (
                str(top),str(left),str(height),str(width)))

            self.put('\n</head>')
        else:
            self.put('\n<head/>')

    #@+node:ekr.20060919172012.5: *4* putOPMLNodes
    def putOPMLNodes (self):

        c = self.c ; root = c.rootPosition()

        self.put('\n<body>')

        for p in root.self_and_siblings_iter():
            self.putOPMLNode(p)

        self.put('\n</body>')
    #@+node:ekr.20060919172012.6: *4* putOPMLNode
    def putOPMLNode (self,p):

        c = self.c
        indent = ' ' * (4 * p.level()) # Always use 4-space indents.
        body = p.bodyString() or '' ; head = p.headString() or ''
        attrFormat = ' %s="%s"'

        self.put('\n%s<outline' % indent)

        if self.opml_write_leo_details: # Put leo-specific attributes.
            for name,val in (
                ('leo:t', g.app.nodeIndices.toString(p.v.t.fileIndex)),
                ('leo:a', self.aAttributes(p)),
                ('leo:tnodeList',self.tnodeListAttributes(p)),
            ):
                if val: self.put(attrFormat % (name,val))

            data = self.uAAttributes(p)
            if data:
                # for name,val in data.iteritems():
                for name in list(data.keys()):
                    val = data.get(name)
                    self.put(attrFormat % (name,val))

        self.put(attrFormat % ('text',self.attributeEscape(head)))    

        closed = False
        if body and self.opml_write_body_text:
            if self.opml_use_outline_elements:
                self.put('>') ; closed = True
                self.put('<leo:body>%s</leo:body>' % xml.sax.saxutils.escape(body))
            else:
                self.put(attrFormat % ('leo:body',self.attributeEscape(body)))

        if p.hasChildren():
            if not closed:
                self.put('>') ; closed = True
            for p2 in p.children_iter():
                self.putOPMLNode(p2)

        if closed:
            self.put('\n%s</outline>' % indent)
            # self.put('</outline>\n')
        else:
            self.put('/>')
    #@+node:ekr.20060919172012.7: *5* attributeEscape
    def attributeEscape(self,s):

        # Unlike xml.sax.saxutils.escape, replace " by &quot; and replace newlines by character reference.
        s = s or ''
        return (
            s.replace('&','&amp;')
            .replace('<','&lt;')
            .replace('>','&gt;')
            .replace('"','&quot;')
            .replace('\n','&#10;\n')
        )
    #@+node:ekr.20060919172012.8: *5* aAttributes
    def aAttributes (self,p):

        c = self.c
        attr = []

        if p.isExpanded():          attr.append('E')
        if p.isMarked():            attr.append('M')
        if c.isCurrentPosition(p):  attr.append('V')

        #if p.v.isOrphan():              attr.append('O')
        #if p.equal(self.topPosition):   attr.append('T')

        return ''.join(attr)
    #@+node:ekr.20060919172012.9: *5* tnodeListAttributes
    # Based on fileCommands.putTnodeList.

    def tnodeListAttributes (self,p):

        '''Put the tnodeList attribute of p.v.t'''

        # Remember: entries in the tnodeList correspond to @+node sentinels, _not_ to tnodes!

        if not hasattr(p.v.t,'tnodeList') or not p.v.t.tnodeList:
            return None

        # g.trace('tnodeList',p.v.t.tnodeList)

        # Assign fileIndices.
        for t in p.v.t.tnodeList:
            try: # Will fail for None or any pre 4.1 file index.
                theId,time,n = p.v.t.fileIndex
            except:
                g.trace("assigning gnx for ",p.v.t)
                gnx = g.app.nodeIndices.getNewIndex()
                p.v.t.setFileIndex(gnx) # Don't convert to string until the actual write.

        s = ','.join([g.app.nodeIndices.toString(t.fileIndex) for t in p.v.t.tnodeList])
        return s
    #@+node:tbrown.20061004094757: *5* uAAttributes
    def uAAttributes(self, p):
        """write unknownAttributes with various levels of expansion"""
        data = {}
        if self.opml_write_ua_attributes and hasattr(p.v, 'unknownAttributes'):
            # for uak, uav in p.v.unknownAttributes.iteritems():
            d = p.u
            for uak in list(d.keys()):
                uav = d.get(uak)
                if self.opml_expand_ua_dictionary and type(uav) == type({}):
                    # for uakc, uavc in uav.iteritems():
                    for uakc in list(uav.keys()):
                        uavc = uav.get(uakc)
                        if str(uavc)!='' or not self.opml_skip_ua_dictionary_blanks:
                            data['leo:ua_'+uak+'_'+uakc] = self.attributeEscape(str(uavc))
                else:
                    data['leo:ua_'+uak] = self.attributeEscape(str(uav))
        return data
    #@+node:ekr.20060919172012.11: *4* putOPMLPostlog
    def putOPMLPostlog (self):

        self.put('\n</opml>\n')
    #@-others
#@+node:ekr.20060904103412.6: ** class opmlController
class opmlController:

    #@+others
    #@+node:ekr.20060904103412.7: *3* __init__
    def __init__ (self,c):

        self.c = c

        c.opmlCommands = self
        c.k.registerCommand('read-opml-file',None,self.readOpmlCommand,pane='all',verbose=False)
        c.k.registerCommand('write-opml-file',None,self.writeOpmlCommand,pane='all',verbose=False)

        self.opml_read_derived_files  = c.config.getBool('opml_read_derived_files')
        self.opml_write_derived_files = c.config.getBool('opml_write_derived_files')

        self.currentVnode = None
        self.topVnode = None

        self.generatedTnxs = {}  # Keys are tnx's (strings).  Values are vnodes.
    #@+node:ekr.20060904103412.8: *3* createCommands (not used)
    def createCommands (self):

        c = self.c
        c.opmlCommands = self

        if 0:
            for name,func in (
                ('read-opml-file',  self.readFile),
                ('write-opml-file', self.writeFile),
            ):
                c.k.registerCommand (name,shortcut=None,func=func,pane='all',verbose=False)
    #@+node:ekr.20060914163456: *3* createVnodes & helpers
    def createVnodes (self, dummyRoot):

        '''**Important**: this method and its helpers are low-level code
        corresponding to link/unlink methods in leoNodes.py.
        Modify this with extreme care.'''

        self.generatedTnxs = {}

        children = self.createChildren(dummyRoot,parent_v = None)
        firstChild = children and children[0]

        return firstChild
    #@+node:ekr.20060914171659.2: *4* createChildren
    # node is a nodeClass object, parent_v is a vnode.

    def createChildren (self, node, parent_v):

        result = []

        for child in node.children:
            tnx = child.tnx
            v = tnx and self.generatedTnxs.get(tnx)
            if v:
                # A clone.  Create a new clone node, but share the subtree, i.e., the tnode.
                # g.trace('clone',child.headString)
                v = self.createVnode(child,parent_v,t=v.t)
            else:
                v = self.createVnodeTree(child,parent_v)
                if tnx: self.generatedTnxs [tnx] = v
            result.append(v)

        self.linkSiblings(result)
        if parent_v: self.linkParentAndChildren(parent_v,result)
        return result
    #@+node:ekr.20060914171659: *4* createVnodeTree
    def createVnodeTree (self,node,parent_v):

        v = self.createVnode(node,parent_v)

        # To do: create the children only if v is not a clone.
        self.createChildren(node,v)

        return v
    #@+node:ekr.20060914171659.1: *4* createVnode & helpers
    def createVnode (self,node,parent_v,t=None):

        h = node.headString
        b = node.bodyString
        if not node.tnx or not t:
            t = leoNodes.tnode(bodyString=b,headString=h)
            if node.tnx:
                t.fileIndex = g.app.nodeIndices.scanGnx(node.tnx,0)
        v = leoNodes.vnode(t)
        v.t.vnodeList.append(v)
        v._parent = parent_v

        self.handleVnodeAttributes(node,v)

        return v
    #@+node:ekr.20060917213611: *5* handleVnodeAttributes
    def handleVnodeAttributes (self,node,v):

        a = node.attributes.get('leo:a')
        if a:
            # 'C' (clone) and 'D' bits are not used.
            if 'M' in a: v.setMarked()
            if 'E' in a: v.expand()
            if 'O' in a: v.setOrphan()
            if 'T' in a: self.topVnode = v
            if 'V' in a: self.currentVnode = v

        s = node.attributes.get('leo:tnodeList')
        tnodeList = s and s.split(',')
        if tnodeList:
            # This tnode list will be resolved later.
            # g.trace('found tnodeList',v.headString(),len(tnodeList))
            v.tempTnodeList = tnodeList
    #@+node:ekr.20060914174806: *4* linkParentAndChildren
    def linkParentAndChildren (self, parent_v, children):

        # if children: g.trace(parent_v,len(children))

        firstChild_v = children and children[0] or None

        parent_v.t._firstChild = firstChild_v

        for child in children:
            child._parent = parent_v

        v = parent_v
        if v not in v.t.vnodeList:
            v.t.vnodeList.append(v)
    #@+node:ekr.20060914165257: *4* linkSiblings
    def linkSiblings (self, sibs):

        '''Set the v._back and v._next links for all vnodes v in sibs.'''

        n = len(sibs)

        for i in xrange(n):
            v = sibs[i]
            v._back = (i-1 >= 0 and sibs[i-1]) or None
            v._next = (i+1 <  n and sibs[i+1]) or None
    #@+node:ekr.20060913220707: *3* dumpTree
    def dumpTree (self,root,dummy):

        if not dummy:
            root.dump()
        for child in root.children:
            self.dumpTree(child,dummy=False)
    #@+node:ekr.20060904134958.116: *3* parse_opml_file
    def parse_opml_file (self,inputFileName):

        if not inputFileName or not inputFileName.endswith('.opml'):
            return None

        c = self.c
        path = g.os_path_normpath(g.os_path_join(g.app.loadDir,inputFileName))

        try: f = open(path)
        except IOError:
            g.trace('can not open %s'%path)
            return None
        try:
            try:
                node = None
                parser = xml.sax.make_parser()
                # Do not include external general entities.
                # The actual feature name is "http://xml.org/sax/features/external-general-entities"
                parser.setFeature(xml.sax.handler.feature_external_ges,0)
                handler = contentHandler(c,inputFileName)
                parser.setContentHandler(handler)
                parser.parse(f)
                node = handler.getNode()
            except xml.sax.SAXParseException:
                g.es_print('Error parsing %s' % (inputFileName),color='red')
                g.es_exception()
                return None
            except Exception:
                g.es_print('Unexpected exception parsing %s' % (inputFileName),color='red')
                g.es_exception()
                return None
        finally:
            f.close()
            return node
    #@+node:ekr.20060904103721: *3* readFile
    def readFile (self,fileName):

        if not fileName: return

        c = self.c

        # Pass one: create the intermediate nodes.
        self.dummyRoot = dummyRoot = self.parse_opml_file(fileName)

        # self.dumpTree(dummyRoot,dummy=True)

        # Pass two: create the tree of vnodes and tnodes from the intermediate nodes.
        v = self.createVnodes(dummyRoot)
        if v:
            c2 = c.new()
            c2.setRootVnode(v)
            if self.opml_read_derived_files:
                at = c2.atFileCommands
                c2.fileCommands.tnodesDict = self.createTnodesDict()
                # g.trace('c2',id(c2),'tnodesDict',id(c2.fileCommands.tnodesDict))
                self.resolveTnodeLists(c2)
                if self.opml_read_derived_files:
                    c2.atFileCommands.readAll(c2.rootPosition())
            c2.checkOutline()
            self.setCurrentPosition(c2)
            c2.redraw()
            return c2 # for testing.
    #@+node:ekr.20060921153603: *4* createTnodesDict
    def createTnodesDict (self):

        ''' c.tnodesDict by from self.generatedTnxs
        by onverting vnode entries to tnodes.'''

        d = {}

        for key in self.generatedTnxs.keys():
            v = self.generatedTnxs.get(key)
            # g.trace('v.t',id(v.t),'fileIndex',v.t.fileIndex,v.headString()[:20])
            d[key] = v.t

        return d
    #@+node:ekr.20060917214140: *4* setCurrentPosition
    def setCurrentPosition (self,c):

        v = self.currentVnode
        if not v: return

        for p in c.allNodes_iter():
            if p.v == v:
                c.selectPosition(p)
                break
    #@+node:ekr.20060918132045: *4* resolveTnodeLists
    def resolveTnodeLists (self,c):

        for p in c.allNodes_iter():
            if hasattr(p.v,'tempTnodeList'):
                result = []
                for tnx in p.v.tempTnodeList:
                    v = self.generatedTnxs.get(tnx)
                    if v:
                        # g.trace('found',v,tnx,v.t)
                        result.append(v.t)
                    else:
                        g.trace('No tnode for %s' % tnx)
                p.v.t.tnodeList = result
                delattr(p.v,'tempTnodeList')
    #@+node:ekr.20060919201810: *3* readOpmlCommand
    def readOpmlCommand (self,event=None):

        '''Open a Leo window containing the contents of an .opml file.'''

        c = self.c

        fileName = g.app.gui.runOpenFileDialog(
            title = "Read OPML",
            filetypes = [("OPML files","*.opml"), ("All files","*")],
            defaultextension = ".opml")
        c.bringToFront()

        if fileName and len(fileName) > 0:
            c2 = self.readFile(fileName)
        else:
            c.bodyWantsFocus()
    #@+node:ekr.20060904103721.1: *3* writeFile
    def writeFile (self,fileName):

        if not fileName: return

        self.c.fileCommands.write_Leo_file(
            fileName,
            outlineOnlyFlag=not self.opml_write_derived_files,
            toString=False,toOPML=True)

        g.es_print('wrote %s' % fileName)
    #@+node:ekr.20060919201330: *3* writeOpmlCommand
    def writeOpmlCommand (self,event=None):

        '''Save a Leo outline to an OPMLfile.'''

        c = self.c

        if g.app.disableSave:
            g.es("Save commands disabled",color="purple")
            return

        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""

        initialfile = g.ensure_extension(c.mFileName, ".opml")

        # set local fileName, _not_ c.mFileName
        fileName = g.app.gui.runSaveFileDialog(
            initialfile = initialfile,
            title="Write OPML",
            filetypes=[("OPML files", "*.opml")],
            defaultextension=".opml")
        c.bringToFront()

        if fileName:
            fileName = g.ensure_extension(fileName, ".opml")
            c.opmlCommands.writeFile(fileName)
    #@-others
#@+node:ekr.20060904141220: ** class nodeClass
class nodeClass:

    '''A class representing one outline element.

    Use getters to access the attributes, properties and rules of this mode.'''

    #@+others
    #@+node:ekr.20060904141220.1: *3*  node.__init__
    def __init__ (self):

        self.attributes = {}
        self.bodyString = ''
        self.headString = ''
        self.children = []
        self.tnx = None
    #@+node:ekr.20060904141220.2: *3*  node.__str__ & __repr__
    def __str__ (self):

        return '<node: %s>' % self.headString

    __repr__ = __str__
    #@+node:ekr.20060913220507: *3* dump
    def dump (self):

        print()
        print('node: tnx: %s %s' % (self.tnx,self.headString))
        print('children:',[child for child in self.children])
        print('attrs:',self.attributes.values())
    #@-others
#@+node:ekr.20060904134958.164: ** class contentHandler (XMLGenerator)
class contentHandler (xml.sax.saxutils.XMLGenerator):

    '''A sax content handler class that reads OPML files.'''

    #@+others
    #@+node:ekr.20060904134958.165: *3*  __init__ & helpers
    def __init__ (self,c,inputFileName):

        self.c = c
        self.inputFileName = inputFileName

        # Init the base class.
        xml.sax.saxutils.XMLGenerator.__init__(self)

        #@+<< define dispatch dict >>
        #@+node:ekr.20060917185525: *4* << define dispatch dict >>
        # There is no need for an 'end' method if all info is carried in attributes.

        self.dispatchDict = {
            'body':                     (None,None),
            'head':                     (self.startHead,None),
            'opml':                     (None,None),
            'outline':                  (self.startOutline,self.endOutline),
            'leo:body':                    (self.startBodyText,self.endBodyText),
            'leo:global_window_position':  (self.startWinPos,None)
        }
        #@-<< define dispatch dict >>

        # Semantics.
        self.content = []
        self.elementStack = []
        self.errors = 0
        self.level = 0
        self.node = None
        self.nodeStack = []
        self.ratio = 0.5 # body-outline ratio.
        self.rootNode = None
    #@+node:ekr.20060904134958.166: *3* helpers
    #@+node:ekr.20060904134958.167: *4* attrsToList
    def attrsToList (self,attrs):

        '''Convert the attributes to a list of g.Bunches.

        attrs: an Attributes item passed to startElement.'''

        return [g.Bunch(name=name,val=attrs.getValue(name)) for name in attrs.getNames()]
    #@+node:ekr.20060904134958.170: *4* error
    def error (self, message):

        print()
        print()
        print('XML error: %s' % (message))
        print()

        self.errors += 1
    #@+node:ekr.20060917185525.1: *4* inElement
    def inElement (self,name):

        return self.elementStack and name in self.elementStack
    #@+node:ekr.20060904134958.171: *4* printStartElement & helpers
    def printStartElement(self,name,attrs):

        indent = '\t' * self.level or ''

        if attrs.getLength() > 0:
            print('%s<%s %s>' % (
                indent,
                self.clean(name).strip(),
                self.attrsToString(attrs,sep=' ')))
        else:
            print('%s<%s>' % (
                indent,
                self.clean(name).strip()))

        if name.lower() in ['outline','head','body',]:
            print
    #@+node:ekr.20060904134958.168: *5* attrsToString
    def attrsToString (self,attrs,sep='\n'):

        '''Convert the attributes to a string.

        attrs: an Attributes item passed to startElement.

        sep: the separator charater between attributes.'''

        result = [
            '%s="%s"' % (bunch.name,bunch.val)
            for bunch in self.attrsToList(attrs)
        ]

        return sep.join(result)
    #@+node:ekr.20060904134958.169: *5* clean
    def clean(self,s):

        return g.toEncodedString(s,"ascii")
    #@+node:ekr.20060904134958.174: *3*  Do nothing...
    #@+node:ekr.20060904134958.175: *4* other methods
    def ignorableWhitespace(self):
        g.trace()

    def processingInstruction (self,target,data):
        g.trace()

    def skippedEntity(self,name):
        g.trace(name)

    def startElementNS(self,name,qname,attrs):
        g.trace(name)

    def endElementNS(self,name,qname):
        g.trace(name)
    #@+node:ekr.20060904134958.176: *4* endDocument
    def endDocument(self):

        pass


    #@+node:ekr.20060904134958.177: *4* startDocument
    def startDocument(self):

        pass
    #@+node:ekr.20060904134958.178: *3* characters
    def characters(self,content):

        name = self.elementStack and self.elementStack[-1].lower() or '<no element name>'

        # Opml elements should not have content: everything is carried in attributes.

        if name == 'leo:body':
            if self.node:
                self.content.append(content)
            else:
                self.error('No node for leo:body content')
        else:
            if content.strip():
                print('content:',name,repr(content))
    #@+node:ekr.20060904134958.179: *3* endElement & helpers
    def endElement(self,name):

        name = name.lower()
        if name in printElements or 'all' in printElements:
            indent = '\t' * (self.level-1) or ''
            print('%s</%s>' % (indent,self.clean(name).strip()))

        data = self.dispatchDict.get(name)

        if data is None:
            g.trace('unknown element',name)
        else:
            junk,func = data
            if func:
                func()

        name2 = self.elementStack.pop()
        assert name == name2
    #@+node:ekr.20060919193501: *4* endBodyText
    def endBodyText (self):

        '''End a <leo:body> element.'''

        if self.content:
            self.node.bodyString = ''.join(self.content)

        self.content = []
    #@+node:ekr.20060917185948: *4* endOutline
    def endOutline (self):

        self.level -= 1
        self.node = self.nodeStack.pop()
    #@+node:ekr.20060904134958.180: *3* startElement & helpers
    def startElement(self,name,attrs):

        name = name.lower()
        if name in printElements or 'all' in printElements:
            self.printStartElement(name,attrs)

        self.elementStack.append(name)

        data = self.dispatchDict.get(name)

        if data is None:
            g.trace('unknown element',name)
        else:
            func,junk = data
            if func:
                func(attrs)
    #@+node:ekr.20060919193501.1: *4* startBodyText
    def startBodyText (self,attrs):

        '''Start a <leo:body> element.'''

        self.content = []
    #@+node:ekr.20060922072852: *4* startHead
    def startHead (self,attrs):

        if not self.inElement('opml'):
            self.error('<head> outside <opml>')

        self.doHeadAttributes(attrs)
    #@+node:ekr.20060922072852.1: *5* doHeadAttributes
    def doHeadAttributes (self,attrs):

        ratio = 0.5

        for bunch in self.attrsToList(attrs):
            name = bunch.name ; val = bunch.val
            if name == 'leo:body_outline_ratio':
                try:
                    ratio = float(val)
                    # g.trace(ratio)
                except ValueError:
                    pass

        self.ratio = ratio
    #@+node:ekr.20060917190349: *4* startOutline
    def startOutline (self,attrs):

        if self.inElement('head'):     self.error('<outline> inside <head>')
        if not self.inElement('body'): self.error('<outline> outside <body>')

        self.level += 1

        if self.rootNode:
            parent = self.node
        else:
            self.rootNode = parent = nodeClass() # The dummy parent node.
            parent.headString = 'dummyNode'

        self.node = nodeClass()
        parent.children.append(self.node)
        self.doOutlineAttributes(attrs)
        self.nodeStack.append(parent)
    #@+node:ekr.20060904141220.34: *5* doOutlineAttributes
    def doOutlineAttributes (self,attrs):

        node = self.node

        for bunch in self.attrsToList(attrs):
            name = bunch.name ; val = bunch.val

            if name == 'text': # Text is the 'official' opml attribute for headlines.
                node.headString = val
            elif name == 'leo:body':
                #g.trace(repr(val))
                #g.es_dump (val[:30])
                node.bodyString = val
            elif name == 'leo:t':
                node.tnx = val
            else:
                node.attributes[name] = val
    #@+node:ekr.20060922071010: *4* startWinPos
    def startWinPos (self,attrs):

        if not self.inElement('head'):
            self.error('<leo:global_window_position> outside <body>')

        self.doGlobalWindowAttributes(attrs)
    #@+node:ekr.20060922071010.1: *5* doGlobalWindowAttributes
    def doGlobalWindowAttributes (self,attrs):

        c = self.c
        top = 50 ; left = 50 ; height = 500 ; width = 700 # Reasonable defaults.

        try:
            for bunch in self.attrsToList(attrs):
                name = bunch.name ; val = bunch.val
                if   name == 'top':    top = int(val)
                elif name == 'left':   left = int(val)
                elif name == 'height': height = int(val)
                elif name == 'width':  width = int(val)
        except ValueError:
            pass

        # g.trace(top,left,height,width)
        c.frame.setTopGeometry(width,height,left,top)
        c.frame.deiconify()
        c.frame.lift()
        c.frame.update()
    #@+node:ekr.20060904134958.183: *3* getNode
    def getNode (self):

        return self.rootNode
    #@-others
#@-others
#@-leo

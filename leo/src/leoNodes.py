#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3320:@thin leoNodes.py
#@@language python
#@@tabwidth -4
#@@pagewidth 80

# __pychecker__ = '--no-reuseattr' # Suppress warnings about redefining vnode and tnode classes.

use_zodb = False

#@<< imports >>
#@+node:ekr.20060904165452.1:<< imports >>
if use_zodb:
    # It may be important to import ZODB first.
    try:
        import ZODB
        import ZODB.FileStorage
    except ImportError:
        ZODB = None
else:
    ZODB = None

import leoGlobals as g

if g.app and g.app.use_psyco:
    # print "enabled psyco classes",__file__
    try: from psyco.classes import *
    except ImportError: pass

import string
import time
#@nonl
#@-node:ekr.20060904165452.1:<< imports >>
#@nl

#@+others
#@+node:ekr.20031218072017.3321:class tnode
if use_zodb and ZODB:
    class baseTnode (ZODB.Persistence.Persistent):
        pass
else:
    class baseTnode (object):
        pass

class tnode (baseTnode):
    """A class that implements tnodes."""
    #@    << tnode constants >>
    #@+node:ekr.20031218072017.3322:<< tnode constants >>
    dirtyBit    = 0x01
    richTextBit = 0x02 # Determines whether we use <bt> or <btr> tags.
    visitedBit  = 0x04
    writeBit    = 0x08 # Set: write the tnode.
    #@-node:ekr.20031218072017.3322:<< tnode constants >>
    #@nl
    #@    @+others
    #@+node:ekr.20031218072017.2006:t.__init__
    # All params have defaults, so t = tnode() is valid.

    def __init__ (self,bodyString=None,headString=None):

        # To support ZODB the code must set t._p_changed = 1 whenever
        # t.vnodeList, t.unknownAttributes or any mutable tnode object changes.

        self.cloneIndex = 0 # For Pre-3.12 files.  Zero for @file nodes
        self.fileIndex = None # The immutable file index for this tnode.
        self.insertSpot = None # Location of previous insert point.
        self.scrollBarSpot = None # Previous value of scrollbar position.
        self.selectionLength = 0 # The length of the selected body text.
        self.selectionStart = 0 # The start of the selected body text.
        self.statusBits = 0 # status bits

        # Convert everything to unicode...
        self._headString = g.toUnicode(headString,g.app.tkEncoding)
        self._bodyString = g.toUnicode(bodyString,g.app.tkEncoding)

        self.children = [] # List of all children of this node.
        self.parents = [] # List of all parents of this node.
        self.vnodeList = []
            # List of all vnodes pointing to this tnode.
            # v is a clone iff len(v.t.vnodeList) > 1.
    #@nonl
    #@-node:ekr.20031218072017.2006:t.__init__
    #@+node:ekr.20031218072017.3323:t.__repr__ & t.__str__
    def __repr__ (self):

        return "<tnode %d>" % (id(self))

    __str__ = __repr__
    #@-node:ekr.20031218072017.3323:t.__repr__ & t.__str__
    #@+node:ekr.20060908205857:t.__hash__ (only for zodb)
    if use_zodb and ZODB:

        # The only required property is that objects
        # which compare equal have the same hash value.

        def __hash__(self):

            return hash(g.app.nodeIndices.toString(self.fileIndex))
    #@-node:ekr.20060908205857:t.__hash__ (only for zodb)
    #@+node:ekr.20031218072017.3325:Getters
    #@+node:EKR.20040625161602:t.bodyString
    def getBody (self):

        return self._bodyString

    bodyString = getBody
    bodyText = getBody
    #@-node:EKR.20040625161602:t.bodyString
    #@+node:ekr.20031218072017.3326:t.hasBody
    def hasBody (self):

        '''Return True if this tnode contains body text.'''

        s = self._bodyString

        return s and len(s) > 0
    #@-node:ekr.20031218072017.3326:t.hasBody
    #@+node:ekr.20031218072017.3327:t.Status bits
    #@+node:ekr.20031218072017.3328:isDirty
    def isDirty (self):

        return (self.statusBits & self.dirtyBit) != 0
    #@-node:ekr.20031218072017.3328:isDirty
    #@+node:ekr.20031218072017.3329:isRichTextBit
    def isRichTextBit (self):

        return (self.statusBits & self.richTextBit) != 0
    #@-node:ekr.20031218072017.3329:isRichTextBit
    #@+node:ekr.20031218072017.3330:isVisited
    def isVisited (self):

        return (self.statusBits & self.visitedBit) != 0
    #@-node:ekr.20031218072017.3330:isVisited
    #@+node:EKR.20040503094727:isWriteBit
    def isWriteBit (self):

        return (self.statusBits & self.writeBit) != 0
    #@-node:EKR.20040503094727:isWriteBit
    #@-node:ekr.20031218072017.3327:t.Status bits
    #@-node:ekr.20031218072017.3325:Getters
    #@+node:ekr.20031218072017.3331:Setters
    #@+node:ekr.20031218072017.1484:Setting body text
    #@+node:ekr.20031218072017.1485:setTnodeText
    # This sets the text in the tnode from the given string.

    def setTnodeText (self,s,encoding="utf-8"):

        """Set the body text of a tnode to the given string."""

        s = g.toUnicode(s,encoding,reportErrors=True)

        # DANGEROUS:  This automatically converts everything when reading files.

            # New in Leo 4.4.2: self.c does not exist!
            # This must be done in the Commands class.
            # option = self.c.config.trailing_body_newlines

            # if option == "one":
                # s = s.rstrip() + '\n'
            # elif option == "zero":
                # s = s.rstrip()

        self._bodyString = s

        # g.trace(len(s),g.callers())
    #@-node:ekr.20031218072017.1485:setTnodeText
    #@+node:ekr.20031218072017.1486:setSelection
    def setSelection (self,start,length):

        self.selectionStart = start
        self.selectionLength = length
    #@-node:ekr.20031218072017.1486:setSelection
    #@-node:ekr.20031218072017.1484:Setting body text
    #@+node:ekr.20031218072017.3332:Status bits
    #@+node:ekr.20031218072017.3333:clearDirty
    def clearDirty (self):

        self.statusBits &= ~ self.dirtyBit
    #@-node:ekr.20031218072017.3333:clearDirty
    #@+node:ekr.20031218072017.3334:clearRichTextBit
    def clearRichTextBit (self):

        self.statusBits &= ~ self.richTextBit
    #@-node:ekr.20031218072017.3334:clearRichTextBit
    #@+node:ekr.20031218072017.3335:clearVisited
    def clearVisited (self):

        self.statusBits &= ~ self.visitedBit
    #@-node:ekr.20031218072017.3335:clearVisited
    #@+node:EKR.20040503093844:clearWriteBit
    def clearWriteBit (self):

        self.statusBits &= ~ self.writeBit
    #@-node:EKR.20040503093844:clearWriteBit
    #@+node:ekr.20031218072017.3336:setDirty
    def setDirty (self):

        self.statusBits |= self.dirtyBit
    #@-node:ekr.20031218072017.3336:setDirty
    #@+node:ekr.20031218072017.3337:setRichTextBit
    def setRichTextBit (self):

        self.statusBits |= self.richTextBit
    #@-node:ekr.20031218072017.3337:setRichTextBit
    #@+node:ekr.20031218072017.3338:setVisited
    def setVisited (self):

        self.statusBits |= self.visitedBit
    #@-node:ekr.20031218072017.3338:setVisited
    #@+node:EKR.20040503094727.1:setWriteBit
    def setWriteBit (self):

        self.statusBits |= self.writeBit
    #@-node:EKR.20040503094727.1:setWriteBit
    #@-node:ekr.20031218072017.3332:Status bits
    #@+node:ekr.20031218072017.3339:setCloneIndex (used in 3.x)
    def setCloneIndex (self, index):

        self.cloneIndex = index
    #@-node:ekr.20031218072017.3339:setCloneIndex (used in 3.x)
    #@+node:ekr.20031218072017.3340:setFileIndex
    def setFileIndex (self, index):

        self.fileIndex = index
    #@-node:ekr.20031218072017.3340:setFileIndex
    #@+node:ekr.20050418101546:t.setHeadString (new in 4.3)
    def setHeadString (self,s,encoding="utf-8"):

        t = self

        s = g.toUnicode(s,encoding,reportErrors=True)
        t._headString = s
    #@-node:ekr.20050418101546:t.setHeadString (new in 4.3)
    #@-node:ekr.20031218072017.3331:Setters
    #@-others
#@nonl
#@-node:ekr.20031218072017.3321:class tnode
#@+node:ekr.20031218072017.3341:class vnode
if use_zodb and ZODB:
    class baseVnode (ZODB.Persistence.Persistent):
        pass
else:
    class baseVnode (object):
        pass

class vnode (baseVnode):
    #@    << vnode constants >>
    #@+node:ekr.20031218072017.951:<< vnode constants >>
    # Define the meaning of status bits in new vnodes.

    # Archived...
    clonedBit   = 0x01 # True: vnode has clone mark.

    # not used = 0x02
    expandedBit = 0x04 # True: vnode is expanded.
    markedBit   = 0x08 # True: vnode is marked
    orphanBit   = 0x10 # True: vnode saved in .leo file, not derived file.
    selectedBit = 0x20 # True: vnode is current vnode.
    topBit      = 0x40 # True: vnode was top vnode when saved.

    # Not archived...
    dirtyBit    = 0x060
    richTextBit = 0x080 # Determines whether we use <bt> or <btr> tags.
    visitedBit  = 0x100
    #@-node:ekr.20031218072017.951:<< vnode constants >>
    #@nl
    #@    @+others
    #@+node:ekr.20031218072017.3342:Birth & death
    #@+node:ekr.20031218072017.3344:v.__init__
    def __init__ (self,context,t):

        assert(t)

        # To support ZODB the code must set v._p_changed = 1 whenever
        # v.unknownAttributes or any mutable vnode object changes.

        self.context = context # The context containing context.hiddenRootNode.
            # Required for trees, so we can compute top-level siblings.
            # It is named .context rather than .c to emphasize its limited usage.

        self.iconVal = 0
        self.t = t # The tnode.
        self.statusBits = 0 # status bits
    #@-node:ekr.20031218072017.3344:v.__init__
    #@+node:ekr.20031218072017.3345:v.__repr__ & v.__str__
    def __repr__ (self):

        if self.t:
            return "<vnode %d:'%s'>" % (id(self),self.cleanHeadString())
        else:
            return "<vnode %d:NULL tnode>" % (id(self))

    __str__ = __repr__
    #@-node:ekr.20031218072017.3345:v.__repr__ & v.__str__
    #@+node:ekr.20040312145256:v.dump
    def dumpLink (self,link):
        return g.choose(link,link,"<none>")

    def dump (self,label=""):

        v = self

        if label:
            print '-'*10,label,v
        else:
            print "self    ",v.dumpLink(v)
            print "len(vnodeList)",len(v.t.vnodeList)
            print 'len(parents)',len(v.t.parents)
            print 'len(children)',len(v.t.children)

        if 1:
            print "t",v.dumpLink(v.t)
            print "vnodeList", g.listToString(v.t.vnodeList)
            print 'parents',g.listToString(v.t.parents)
            print 'children',g.listToString(v.t.children)
    #@-node:ekr.20040312145256:v.dump
    #@+node:ekr.20060910100316:v.__hash__ (only for zodb)
    if use_zodb and ZODB:
        def __hash__(self):
            return self.t.__hash__()
    #@nonl
    #@-node:ekr.20060910100316:v.__hash__ (only for zodb)
    #@-node:ekr.20031218072017.3342:Birth & death
    #@+node:ekr.20031218072017.3346:v.Comparisons
    #@+node:ekr.20040705201018:v.findAtFileName
    def findAtFileName (self,names):

        """Return the name following one of the names in nameList.
        Return an empty string."""

        h = self.headString()

        if not g.match(h,0,'@'):
            return ""

        i = g.skip_id(h,1,'-')
        word = h[:i]
        if word in names and g.match_word(h,0,word):
            name = h[i:].strip()
            # g.trace(word,name)
            return name
        else:
            return ""
    #@-node:ekr.20040705201018:v.findAtFileName
    #@+node:ekr.20031218072017.3350:anyAtFileNodeName
    def anyAtFileNodeName (self):

        """Return the file name following an @file node or an empty string."""

        names = (
            "@auto",
            "@file",
            "@thin",   "@file-thin",   "@thinfile",
            "@asis",   "@file-asis",   "@silentfile",
            "@noref",  "@file-noref",  "@rawfile",
            "@nosent", "@file-nosent", "@nosentinelsfile")

        return self.findAtFileName(names)
    #@-node:ekr.20031218072017.3350:anyAtFileNodeName
    #@+node:ekr.20031218072017.3348:at...FileNodeName
    # These return the filename following @xxx, in v.headString.
    # Return the the empty string if v is not an @xxx node.

    def atAutoNodeName (self):
        # h = self.headString() ; tag = '@auto'
        # # Prevent conflicts with autotrees plugin: don't allow @auto-whatever to match.
        # return g.match_word(h,0,tag) and not g.match(h,0,tag+'-') and h[len(tag):].strip()
        names = ("@auto",)
        return self.findAtFileName(names)

    def atFileNodeName (self):
        names = ("@file",)
        return self.findAtFileName(names)

    def atNoSentinelsFileNodeName (self):
        names = ("@nosent", "@file-nosent", "@nosentinelsfile")
        return self.findAtFileName(names)

    def atRawFileNodeName (self):
        names = ("@noref", "@file-noref", "@rawfile")
        return self.findAtFileName(names)

    def atSilentFileNodeName (self):
        names = ("@asis", "@file-asis", "@silentfile")
        return self.findAtFileName(names)

    def atThinFileNodeName (self):
        names = ("@thin", "@file-thin", "@thinfile")
        return self.findAtFileName(names)

    # New names, less confusing
    atNoSentFileNodeName  = atNoSentinelsFileNodeName
    atNorefFileNodeName   = atRawFileNodeName
    atAsisFileNodeName    = atSilentFileNodeName
    #@-node:ekr.20031218072017.3348:at...FileNodeName
    #@+node:EKR.20040430152000:isAtAllNode
    def isAtAllNode (self):

        """Returns True if the receiver contains @others in its body at the start of a line."""

        flag, i = g.is_special(self.t._bodyString,0,"@all")
        return flag
    #@-node:EKR.20040430152000:isAtAllNode
    #@+node:ekr.20040326031436:isAnyAtFileNode
    def isAnyAtFileNode (self):

        """Return True if v is any kind of @file or related node."""

        # This routine should be as fast as possible.
        # It is called once for every vnode when writing a file.

        h = self.headString()
        return h and h[0] == '@' and self.anyAtFileNodeName()
    #@-node:ekr.20040326031436:isAnyAtFileNode
    #@+node:ekr.20040325073709:isAt...FileNode (vnode)
    def isAtAutoNode (self):
        return g.choose(self.atAutoNodeName(),True,False)

    def isAtFileNode (self):
        return g.choose(self.atFileNodeName(),True,False)

    def isAtNoSentinelsFileNode (self):
        return g.choose(self.atNoSentinelsFileNodeName(),True,False)

    def isAtRawFileNode (self): # @file-noref
        return g.choose(self.atRawFileNodeName(),True,False)

    def isAtSilentFileNode (self): # @file-asis
        return g.choose(self.atSilentFileNodeName(),True,False)

    def isAtThinFileNode (self):
        return g.choose(self.atThinFileNodeName(),True,False)

    # New names, less confusing:
    isAtNoSentFileNode = isAtNoSentinelsFileNode
    isAtNorefFileNode  = isAtRawFileNode
    isAtAsisFileNode   = isAtSilentFileNode
    #@-node:ekr.20040325073709:isAt...FileNode (vnode)
    #@+node:ekr.20031218072017.3351:isAtIgnoreNode
    def isAtIgnoreNode (self):

        """Returns True if the receiver contains @ignore in its body at the start of a line."""

        flag, i = g.is_special(self.t._bodyString, 0, "@ignore")
        return flag
    #@-node:ekr.20031218072017.3351:isAtIgnoreNode
    #@+node:ekr.20031218072017.3352:isAtOthersNode
    def isAtOthersNode (self):

        """Returns True if the receiver contains @others in its body at the start of a line."""

        flag, i = g.is_special(self.t._bodyString,0,"@others")
        return flag
    #@-node:ekr.20031218072017.3352:isAtOthersNode
    #@+node:ekr.20031218072017.3353:matchHeadline
    def matchHeadline (self,pattern):

        """Returns True if the headline matches the pattern ignoring whitespace and case.

        The headline may contain characters following the successfully matched pattern."""

        v = self

        h = g.toUnicode(v.headString(),'utf-8')
        h = h.lower().replace(' ','').replace('\t','')

        pattern = g.toUnicode(pattern,'utf-8')
        pattern = pattern.lower().replace(' ','').replace('\t','')

        return h.startswith(pattern)
    #@-node:ekr.20031218072017.3353:matchHeadline
    #@-node:ekr.20031218072017.3346:v.Comparisons
    #@+node:ekr.20031218072017.3359:v.Getters
    #@+node:ekr.20031218072017.3360:v.Children
    #@+node:ekr.20031218072017.3362:v.firstChild
    def firstChild (self):

        v = self
        return v.t.children and v.t.children[0]
    #@-node:ekr.20031218072017.3362:v.firstChild
    #@+node:ekr.20040307085922:v.hasChildren & hasFirstChild
    def hasChildren (self):

        v = self
        return len(v.t.children) > 0

    hasFirstChild = hasChildren
    #@-node:ekr.20040307085922:v.hasChildren & hasFirstChild
    #@+node:ekr.20031218072017.3364:v.lastChild
    def lastChild (self):

        v = self
        return v.t.children and v.t.children[-1] or None
    #@-node:ekr.20031218072017.3364:v.lastChild
    #@+node:ekr.20031218072017.3365:v.nthChild
    # childIndex and nthChild are zero-based.

    def nthChild (self, n):

        v = self

        if 0 <= n < len(v.t.children):
            return v.t.children[n]
        else:
            return None
    #@-node:ekr.20031218072017.3365:v.nthChild
    #@+node:ekr.20031218072017.3366:v.numberOfChildren
    def numberOfChildren (self):

        v = self
        return len(v.t.children)
    #@-node:ekr.20031218072017.3366:v.numberOfChildren
    #@-node:ekr.20031218072017.3360:v.Children
    #@+node:ekr.20031218072017.3367:v.Status Bits
    #@+node:ekr.20031218072017.3368:v.isCloned
    def isCloned (self):

        return len(self.t.vnodeList) > 1
    #@-node:ekr.20031218072017.3368:v.isCloned
    #@+node:ekr.20031218072017.3369:isDirty
    def isDirty (self):

        return self.t.isDirty()
    #@-node:ekr.20031218072017.3369:isDirty
    #@+node:ekr.20031218072017.3370:isExpanded
    def isExpanded (self):

        return ( self.statusBits & self.expandedBit ) != 0
    #@-node:ekr.20031218072017.3370:isExpanded
    #@+node:ekr.20031218072017.3371:isMarked
    def isMarked (self):

        return ( self.statusBits & vnode.markedBit ) != 0
    #@-node:ekr.20031218072017.3371:isMarked
    #@+node:ekr.20031218072017.3372:isOrphan
    def isOrphan (self):

        return ( self.statusBits & vnode.orphanBit ) != 0
    #@-node:ekr.20031218072017.3372:isOrphan
    #@+node:ekr.20031218072017.3373:isSelected
    def isSelected (self):

        return ( self.statusBits & vnode.selectedBit ) != 0
    #@-node:ekr.20031218072017.3373:isSelected
    #@+node:ekr.20031218072017.3374:isTopBitSet
    def isTopBitSet (self):

        return ( self.statusBits & self.topBit ) != 0
    #@-node:ekr.20031218072017.3374:isTopBitSet
    #@+node:ekr.20031218072017.3376:isVisited
    def isVisited (self):

        return ( self.statusBits & vnode.visitedBit ) != 0
    #@-node:ekr.20031218072017.3376:isVisited
    #@+node:ekr.20031218072017.3377:status
    def status (self):

        return self.statusBits
    #@-node:ekr.20031218072017.3377:status
    #@-node:ekr.20031218072017.3367:v.Status Bits
    #@+node:ekr.20031218072017.3378:v.bodyString
    def bodyString (self):

        # This message should never be printed and we want to avoid crashing here!
        if not g.isUnicode(self.t._bodyString):
            s = "v.bodyString: Leo internal error: not unicode:" + repr(self.t._bodyString)
            g.es_print('',s,color="red")

        # Make _sure_ we return a unicode string.
        return g.toUnicode(self.t._bodyString,g.app.tkEncoding)
    #@-node:ekr.20031218072017.3378:v.bodyString
    #@+node:ekr.20031218072017.1581:v.headString & v.cleanHeadString
    def headString (self):

        """Return the headline string."""

        # This message should never be printed and we want to avoid crashing here!
        if not g.isUnicode(self.t._headString):
            s = "Leo internal error: not unicode:" + repr(self.t._headString)
            g.es_print('',s,color="red")

        # Make _sure_ we return a unicode string.
        return g.toUnicode(self.t._headString,g.app.tkEncoding)

    def cleanHeadString (self):

        s = self.headString()
        return g.toEncodedString(s,"ascii") # Replaces non-ascii characters by '?'
    #@-node:ekr.20031218072017.1581:v.headString & v.cleanHeadString
    #@+node:ekr.20040323100443:v.directParents
    def directParents (self):

        """(New in 4.2) Return a list of all direct parent vnodes of a vnode.

        This is NOT the same as the list of ancestors of the vnode."""

        v = self
        return v.t.parents
    #@-node:ekr.20040323100443:v.directParents
    #@-node:ekr.20031218072017.3359:v.Getters
    #@+node:ekr.20031218072017.3384:v.Setters
    #@+node:ekr.20031218072017.3386: v.Status bits
    #@+node:ekr.20031218072017.3389:clearClonedBit
    def clearClonedBit (self):

        self.statusBits &= ~ self.clonedBit
    #@-node:ekr.20031218072017.3389:clearClonedBit
    #@+node:ekr.20031218072017.3390:v.clearDirty
    def clearDirty (self):

        v = self
        v.t.clearDirty()
    #@nonl
    #@-node:ekr.20031218072017.3390:v.clearDirty
    #@+node:ekr.20031218072017.3391:v.clearMarked
    def clearMarked (self):

        self.statusBits &= ~ self.markedBit
    #@-node:ekr.20031218072017.3391:v.clearMarked
    #@+node:ekr.20031218072017.3392:clearOrphan
    def clearOrphan (self):

        self.statusBits &= ~ self.orphanBit
    #@-node:ekr.20031218072017.3392:clearOrphan
    #@+node:ekr.20031218072017.3393:clearVisited
    def clearVisited (self):

        self.statusBits &= ~ self.visitedBit
    #@-node:ekr.20031218072017.3393:clearVisited
    #@+node:ekr.20031218072017.3395:contract & expand & initExpandedBit
    def contract(self):

        self.statusBits &= ~ self.expandedBit

        # g.trace(self.statusBits)

    def expand(self):

        self.statusBits |= self.expandedBit

        # g.trace(self,g.callers())

        # g.trace(self.statusBits)

    def initExpandedBit (self):

        self.statusBits |= self.expandedBit
    #@-node:ekr.20031218072017.3395:contract & expand & initExpandedBit
    #@+node:ekr.20031218072017.3396:initStatus
    def initStatus (self, status):

        self.statusBits = status
    #@-node:ekr.20031218072017.3396:initStatus
    #@+node:ekr.20031218072017.3397:setClonedBit & initClonedBit
    def setClonedBit (self):

        self.statusBits |= self.clonedBit

    def initClonedBit (self, val):

        if val:
            self.statusBits |= self.clonedBit
        else:
            self.statusBits &= ~ self.clonedBit
    #@-node:ekr.20031218072017.3397:setClonedBit & initClonedBit
    #@+node:ekr.20031218072017.3398:v.setMarked & initMarkedBit
    def setMarked (self):

        self.statusBits |= self.markedBit

    def initMarkedBit (self):

        self.statusBits |= self.markedBit
    #@-node:ekr.20031218072017.3398:v.setMarked & initMarkedBit
    #@+node:ekr.20031218072017.3399:setOrphan
    def setOrphan (self):

        self.statusBits |= self.orphanBit
    #@-node:ekr.20031218072017.3399:setOrphan
    #@+node:ekr.20031218072017.3400:setSelected (vnode)
    # This only sets the selected bit.

    def setSelected (self):

        self.statusBits |= self.selectedBit
    #@-node:ekr.20031218072017.3400:setSelected (vnode)
    #@+node:ekr.20031218072017.3401:t.setVisited
    # Compatibility routine for scripts

    def setVisited (self):

        self.statusBits |= self.visitedBit
    #@-node:ekr.20031218072017.3401:t.setVisited
    #@-node:ekr.20031218072017.3386: v.Status bits
    #@+node:ekr.20031218072017.3385:v.computeIcon & setIcon
    def computeIcon (self):

        val = 0 ; v = self
        if v.t.hasBody(): val += 1
        if v.isMarked(): val += 2
        if v.isCloned(): val += 4
        if v.isDirty(): val += 8
        return val

    def setIcon (self):

        pass # Compatibility routine for old scripts
    #@-node:ekr.20031218072017.3385:v.computeIcon & setIcon
    #@+node:ekr.20040315032144:v.initHeadString
    def initHeadString (self,s,encoding="utf-8"):

        v = self
        s = g.toUnicode(s,encoding,reportErrors=True)
        v.t._headString = s

        # g.trace(g.callers(5))
    #@-node:ekr.20040315032144:v.initHeadString
    #@+node:ekr.20031218072017.3402:v.setSelection
    def setSelection (self, start, length):

        self.t.setSelection ( start, length )
    #@-node:ekr.20031218072017.3402:v.setSelection
    #@+node:ekr.20040315042106:v.setTnodeText
    def setTnodeText (self,s,encoding="utf-8"):

        return self.t.setTnodeText(s,encoding)

    setHeadText = setTnodeText
    setHeadString = setTnodeText
    #@-node:ekr.20040315042106:v.setTnodeText
    #@-node:ekr.20031218072017.3384:v.Setters
    #@+node:ekr.20040301071824:v.Link/Unlink/Insert methods (used by file read logic)
    # These remain in 4.2: the file read logic calls these before creating positions.
    #@+node:ekr.20031218072017.3421:v.insertAsNthChild (used by 3.x read logic)
    def insertAsNthChild (self,n,t=None):

        """Inserts a new node as the the nth child of the receiver.
        The receiver must have at least n-1 children"""

        v = self

        if not t:
            t = tnode(headString="NewHeadline")

        v2 = vnode(context=v.context,t=t)
        v2.linkAsNthChild(self,n)

        return v2
    #@-node:ekr.20031218072017.3421:v.insertAsNthChild (used by 3.x read logic)
    #@+node:ekr.20031218072017.3425:v.linkAsNthChild (used by 4.x read logic)
    def linkAsNthChild (self,parent_v,n):

        """Links self as the n'th child of vnode pv"""

        # Similar to p.linkAsNthChild.
        v = self

         # Add v to it's tnode's vnodeList.
        if v not in v.t.vnodeList:
            v.t.vnodeList.append(v)
            v.t._p_changed = 1 # Support for tnode class.

        # Add v to parent_v's children.
        parent_v.t.children.insert(n,v)
        parent_v._p_changed = 1

        # Add parent_v to v's parents.
        if not parent_v in v.t.parents:
            v.t.parents.append(parent_v)
            v._p_changed = 1
    #@-node:ekr.20031218072017.3425:v.linkAsNthChild (used by 4.x read logic)
    #@+node:ekr.20080418124036.1:v.moveToRoot (used by non-sax copy outline logic)
    def moveToRoot (self,oldRoot=None):

        v = self
        context = v.context
        hiddenRootNode = context.hiddenRootNode

        if oldRoot: oldRootNode = oldRoot.v
        else:       oldRootNode = None

        # Init v.t.vnodeList
        v.t.vnodeList = [v]

        # Init v.t.parents to the hidden root node.
        v.t.parents = [hiddenRootNode]
        v._p_changed = 1

        # Init hiddenRootNode's children to v.
        hiddenRootNode.t.children = [v]

        # Link in the rest of the tree only when oldRoot != None.
        if oldRoot:
            hiddenRootNode.t.children.append(oldRootNode)
            oldRootNode.parents = [hiddenRootNode]
            oldRootNode.t.vnodeList = [oldRootNode]
    #@-node:ekr.20080418124036.1:v.moveToRoot (used by non-sax copy outline logic)
    #@-node:ekr.20040301071824:v.Link/Unlink/Insert methods (used by file read logic)
    #@-others
#@nonl
#@-node:ekr.20031218072017.3341:class vnode
#@+node:ekr.20031218072017.1991:class nodeIndices
# Indices are Python dicts containing 'id','loc','time' and 'n' keys.

class nodeIndices (object):

    """A class to implement global node indices (gnx's)."""

    #@    @+others
    #@+node:ekr.20031218072017.1992:nodeIndices.__init__
    def __init__ (self,id):

        """ctor for nodeIndices class"""

        self.userId = id
        self.defaultId = id

        # A Major simplification: Only assign the timestamp once.
        self.setTimeStamp()
        self.lastIndex = 0
    #@-node:ekr.20031218072017.1992:nodeIndices.__init__
    #@+node:ekr.20031218072017.1993:areEqual
    def areEqual (self,gnx1,gnx2):

        """Return True if all fields of gnx1 and gnx2 are equal"""

        # works whatever the format of gnx1 and gnx2.
        # This should never throw an exception.
        return gnx1 == gnx2
    #@-node:ekr.20031218072017.1993:areEqual
    #@+node:ekr.20031218072017.1994:get/setDefaultId
    # These are used by the fileCommands read/write code.

    def getDefaultId (self):

        """Return the id to be used by default in all gnx's"""
        return self.defaultId

    def setDefaultId (self,theId):

        """Set the id to be used by default in all gnx's"""
        self.defaultId = theId
    #@-node:ekr.20031218072017.1994:get/setDefaultId
    #@+node:ekr.20031218072017.1995:getNewIndex
    def getNewIndex (self):

        '''Create a new gnx.'''

        self.lastIndex += 1
        d = (self.userId,self.timeString,self.lastIndex)
        # g.trace(d)
        return d
    #@-node:ekr.20031218072017.1995:getNewIndex
    #@+node:ekr.20031218072017.1996:isGnx
    def isGnx (self,gnx):
        try:
            theId,t,n = gnx
            return t != None
        except Exception:
            return False
    #@-node:ekr.20031218072017.1996:isGnx
    #@+node:ekr.20031218072017.1997:scanGnx
    def scanGnx (self,s,i):

        """Create a gnx from its string representation"""

        if type(s) not in (type(""),type(u"")):
            g.es("scanGnx: unexpected index type:",type(s),'',s,color="red")
            return None,None,None

        s = s.strip()

        theId,t,n = None,None,None
        i,theId = g.skip_to_char(s,i,'.')
        if g.match(s,i,'.'):
            i,t = g.skip_to_char(s,i+1,'.')
            if g.match(s,i,'.'):
                i,n = g.skip_to_char(s,i+1,'.')
        # Use self.defaultId for missing id entries.
        if theId == None or len(theId) == 0:
            theId = self.defaultId
        # Convert n to int.
        if n:
            try: n = int(n)
            except Exception: pass

        return theId,t,n
    #@-node:ekr.20031218072017.1997:scanGnx
    #@+node:ekr.20031218072017.1998:setTimeStamp
    def setTimestamp (self):

        """Set the timestamp string to be used by getNewIndex until further notice"""

        self.timeString = time.strftime(
            "%Y%m%d%H%M%S", # Help comparisons; avoid y2k problems.
            time.localtime())

        # g.trace(self.timeString,self.lastIndex,g.callers(4))

    setTimeStamp = setTimestamp
    #@-node:ekr.20031218072017.1998:setTimeStamp
    #@+node:ekr.20031218072017.1999:toString
    def toString (self,index):

        """Convert a gnx (a tuple) to its string representation"""

        try:
            theId,t,n = index
            if n in (None,0,'',):
                return "%s.%s" % (theId,t)
            else:
                return "%s.%s.%d" % (theId,t,n)
        except Exception:
            if not g.app.unitTesting:
                g.trace('unusual gnx',repr(index),g.callers()) 
            try:
                theId,t,n = self.getNewIndex()
                if n in (None,0,'',):
                    return "%s.%s" % (theId,t)
                else:
                    return "%s.%s.%d" % (theId,t,n)
            except Exception:
                g.trace('double exception: returning original index')
                return repr(index)
    #@nonl
    #@-node:ekr.20031218072017.1999:toString
    #@-others
#@-node:ekr.20031218072017.1991:class nodeIndices
#@+node:ekr.20031218072017.889:class position
#@<< about the position class >>
#@+node:ekr.20031218072017.890:<< about the position class >>
#@@killcolor
#@+at
# 
# A position marks the spot in a tree traversal. A position p consists of a 
# vnode
# p.v, a child index p._childIndex, and a stack of tuples (v,childIndex), one 
# for
# each ancestor **at the spot in tree traversal. Positions p has a unique set 
# of
# parents.
# 
# The p.moveToX methods may return a null (invalid) position p with p.v = 
# None.
# 
# The tests "if p" or "if not p" are the _only_ correct way to test whether a
# position p is valid. In particular, tests like "if p is None" or "if p is 
# not
# None" will not work properly.
#@-at
#@-node:ekr.20031218072017.890:<< about the position class >>
#@nl

# Positions should *never* be saved by the ZOBD.

class basePosition (object):
    #@    @+others
    #@+node:ekr.20040228094013: p.ctor & other special methods...
    #@+node:ekr.20080416161551.190: p.__init__
    def __init__ (self,v,childIndex=0,stack=None,trace=False):

        '''Create a new position with the given childIndex and parent stack.'''

        # __pychecker__ = '--no-argsused' # trace not used.

        # To support ZODB the code must set v._p_changed = 1
        # whenever any mutable vnode object changes.

        self._childIndex = childIndex
        self.v = v

        # New in Leo 4.5: stack entries are tuples (v,childIndex).
        if stack:
            self.stack = stack[:] # Creating a copy here is safest and best.
        else:
            self.stack = []

        g.app.positions += 1

        # if g.app.tracePositions and trace: g.trace(g.callers())
    #@-node:ekr.20080416161551.190: p.__init__
    #@+node:ekr.20080416161551.186:p.__cmp__, equal and isEqual
    def __cmp__(self,p2):

        """Return 0 if two postions are equivalent."""

        p1 = self

        # g.trace(p1.headString(),p2 and p2.headString())

        if p2 is None or p2.v is None:
            if p1.v is None: return 0 # equal
            else:            return 1 # not equal
        elif p1.v == p2.v and p1._childIndex == p2._childIndex and p1.stack == p2.stack:
            return 0 # equal
        else:
            return 1 # not equal

    # isEqual and equal are deprecated.

    def isEqual (self,p2):

        p1 = self
        if p2 is None or p2.v is None:
            return p1.v is None
        else:
            return p1.v == p2.v and p1._childIndex == p2._childIndex and p1.stack == p2.stack

    equal = isEqual
    #@-node:ekr.20080416161551.186:p.__cmp__, equal and isEqual
    #@+node:ekr.20040117170612:p.__getattr__  ON:  must be ON if use_plugins
    if 1: # Good for compatibility, bad for finding conversion problems.

        def __getattr__ (self,attr):

            """Convert references to p.t into references to p.v.t.

            N.B. This automatically keeps p.t in synch with p.v.t."""

            if attr=="t":
                return self.v.t
            else:
                # New in 4.3: _silently_ raise the attribute error.
                # This allows plugin code to use hasattr(p,attr) !
                if 0:
                    print "unknown position attribute:",attr
                    import traceback ; traceback.print_stack()
                raise AttributeError,attr
    #@nonl
    #@-node:ekr.20040117170612:p.__getattr__  ON:  must be ON if use_plugins
    #@+node:ekr.20040117173448:p.__nonzero__
    #@+at
    # Tests such as 'if p' or 'if not p' are the _only_ correct ways to test 
    # whether a position p is valid.
    # In particular, tests like 'if p is None' or 'if p is not None' will not 
    # work properly.
    #@-at
    #@@c

    def __nonzero__ ( self):

        """Return True if a position is valid."""

        # if g.app.trace: "__nonzero__",self.v

        return self.v is not None
    #@-node:ekr.20040117173448:p.__nonzero__
    #@+node:ekr.20040301205720:p.__str__ and p.__repr__
    def __str__ (self):

        p = self

        if p.v:
            return "<pos %d lvl: %d [%d] %s>" % (id(p),p.level(),len(p.stack),p.cleanHeadString())
        else:
            return "<pos %d        [%d] None>" % (id(p),len(p.stack))

    __repr__ = __str__
    #@-node:ekr.20040301205720:p.__str__ and p.__repr__
    #@+node:ekr.20061006092649:p.archivedPosition
    def archivedPosition (self):

        '''Return a representation of a position suitable for use in .leo files.'''

        p = self
        aList = [z._childIndex for z in p.self_and_parents_iter()]
        aList.reverse()
        return aList
    #@nonl
    #@-node:ekr.20061006092649:p.archivedPosition
    #@+node:ekr.20040117171654:p.copy
    # Using this routine can generate huge numbers of temporary positions during a tree traversal.

    def copy (self):

        """"Return an independent copy of a position."""

        # if g.app.tracePositions: g.trace(g.callers())

        return position(self.v,self._childIndex,self.stack,trace=False)
    #@-node:ekr.20040117171654:p.copy
    #@+node:ekr.20040310153624:p.dump & p.vnodeListIds
    def dumpLink (self,link):

        return g.choose(link,link,"<none>")

    def dump (self,label=""):

        p = self
        print '-'*10,label,p
        if p.v:
            p.v.dump() # Don't print a label

    def vnodeListIds (self):

        p = self
        return [id(v) for v in p.v.t.vnodeList]
    #@-node:ekr.20040310153624:p.dump & p.vnodeListIds
    #@+node:ekr.20080416161551.191:p.key
    def key (self):

        p = self

        vList = [z[0] for z in p.stack]

        return '%s:%s.%s' % (
            id(p.v),
            p._childIndex,
            ','.join([str(id(z)) for z in vList])
        )
    #@-node:ekr.20080416161551.191:p.key
    #@-node:ekr.20040228094013: p.ctor & other special methods...
    #@+node:ekr.20040306212636:p.Getters
    #@+node:ekr.20040306210951: vnode proxies (no change)
    #@+node:ekr.20040306211032:p.Comparisons
    def anyAtFileNodeName         (self): return self.v.anyAtFileNodeName()
    def atAutoNodeName            (self): return self.v.atAutoNodeName()
    def atFileNodeName            (self): return self.v.atFileNodeName()
    def atNoSentinelsFileNodeName (self): return self.v.atNoSentinelsFileNodeName()
    def atRawFileNodeName         (self): return self.v.atRawFileNodeName()
    def atSilentFileNodeName      (self): return self.v.atSilentFileNodeName()
    def atThinFileNodeName        (self): return self.v.atThinFileNodeName()

    # New names, less confusing
    atNoSentFileNodeName  = atNoSentinelsFileNodeName
    atNorefFileNodeName   = atRawFileNodeName
    atAsisFileNodeName    = atSilentFileNodeName

    def isAnyAtFileNode         (self): return self.v.isAnyAtFileNode()
    def isAtAllNode             (self): return self.v.isAtAllNode()
    def isAtAutoNode            (self): return self.v.isAtAutoNode()
    def isAtFileNode            (self): return self.v.isAtFileNode()
    def isAtIgnoreNode          (self): return self.v.isAtIgnoreNode()
    def isAtNoSentinelsFileNode (self): return self.v.isAtNoSentinelsFileNode()
    def isAtOthersNode          (self): return self.v.isAtOthersNode()
    def isAtRawFileNode         (self): return self.v.isAtRawFileNode()
    def isAtSilentFileNode      (self): return self.v.isAtSilentFileNode()
    def isAtThinFileNode        (self): return self.v.isAtThinFileNode()

    # New names, less confusing:
    isAtNoSentFileNode = isAtNoSentinelsFileNode
    isAtNorefFileNode  = isAtRawFileNode
    isAtAsisFileNode   = isAtSilentFileNode

    # Utilities.
    def matchHeadline (self,pattern): return self.v.matchHeadline(pattern)
    #@-node:ekr.20040306211032:p.Comparisons
    #@+node:ekr.20040306220230:p.Headline & body strings
    def bodyString (self):

        return self.v.bodyString()

    def headString (self):

        return self.v.headString()

    def cleanHeadString (self):

        return self.v.cleanHeadString()
    #@-node:ekr.20040306220230:p.Headline & body strings
    #@+node:ekr.20040306214401:p.Status bits
    def isDirty     (self): return self.v.isDirty()
    def isExpanded  (self): return self.v.isExpanded()
    def isMarked    (self): return self.v.isMarked()
    def isOrphan    (self): return self.v.isOrphan()
    def isSelected  (self): return self.v.isSelected()
    def isTopBitSet (self): return self.v.isTopBitSet()
    def isVisited   (self): return self.v.isVisited()
    def status      (self): return self.v.status()
    #@-node:ekr.20040306214401:p.Status bits
    #@-node:ekr.20040306210951: vnode proxies (no change)
    #@+node:ekr.20040306214240.2:children & parents (changed)
    #@+node:ekr.20040326064330:p.childIndex (changed)
    def childIndex(self):

        p = self
        return p._childIndex


        # p = self ; v = p.v

        # # This is time-critical code!

        # # 3/25/04: Much faster code:
        # if not v or not v._back:
            # return 0

        # n = 0 ; v = v._back
        # while v:
            # n += 1
            # v = v._back

        # return n
    #@-node:ekr.20040326064330:p.childIndex (changed)
    #@+node:ekr.20040323160302:p.directParents
    def directParents (self):

        return self.v.directParents()
    #@-node:ekr.20040323160302:p.directParents
    #@+node:ekr.20040306214240.3:p.hasChildren & p.numberOfChildren (changed)
    def hasChildren (self):

        p = self
        return len(p.v.t.children) > 0

    hasFirstChild = hasChildren

    def numberOfChildren (self):

        p = self
        return len(p.v.t.children)
    #@-node:ekr.20040306214240.3:p.hasChildren & p.numberOfChildren (changed)
    #@-node:ekr.20040306214240.2:children & parents (changed)
    #@+node:ekr.20031218072017.915:p.getX & vnode compatibility traversal routines (no change)
    # These methods are useful abbreviations.
    # Warning: they make copies of positions, so they should be used _sparingly_

    def getBack          (self): return self.copy().moveToBack()
    def getFirstChild    (self): return self.copy().moveToFirstChild()
    def getLastChild     (self): return self.copy().moveToLastChild()
    def getLastNode      (self): return self.copy().moveToLastNode()
    def getLastVisible   (self): return self.copy().moveToLastVisible()
    def getNext          (self): return self.copy().moveToNext()
    def getNodeAfterTree (self): return self.copy().moveToNodeAfterTree()
    def getNthChild    (self,n): return self.copy().moveToNthChild(n)
    def getParent        (self): return self.copy().moveToParent()
    def getThreadBack    (self): return self.copy().moveToThreadBack()
    def getThreadNext    (self): return self.copy().moveToThreadNext()

    # New in Leo 4.4.3 b2: add c args.
    def getVisBack (self,c): return self.copy().moveToVisBack(c)
    def getVisNext (self,c): return self.copy().moveToVisNext(c)

    # These are efficient enough now that iterators are the normal way to traverse the tree!

    back          = getBack
    firstChild    = getFirstChild
    lastChild     = getLastChild
    lastNode      = getLastNode
    lastVisible   = getLastVisible # New in 4.2 (was in tk tree code).
    next          = getNext
    nodeAfterTree = getNodeAfterTree
    nthChild      = getNthChild
    parent        = getParent
    threadBack    = getThreadBack
    threadNext    = getThreadNext
    visBack       = getVisBack
    visNext       = getVisNext

    # New in Leo 4.4.3:
    hasVisBack = visBack
    hasVisNext = visNext
    #@nonl
    #@-node:ekr.20031218072017.915:p.getX & vnode compatibility traversal routines (no change)
    #@+node:ekr.20080416161551.192:p.hasX (test)
    def hasBack(self):
        p = self
        return p.v and p._childIndex > 0

    def hasNext(self):
        p = self
        try:
            parent_v = p.parentNode(includeHiddenRootNode=True)
                # Returns None if p.v is None.
            return p.v and parent_v and p._childIndex+1 < len(parent_v.t.children)
        except Exception:
            g.trace('*** Unexpected exception')
            g.es_exception()
            return None

    def hasParent(self):
        p = self
        return p.v and len(p.stack) > 0

    def hasThreadBack(self):
        p = self
        return p.hasParent() or p.hasBack() # Much cheaper than computing the actual value.
    #@+node:ekr.20080416161551.193:hasThreadNext (the only complex hasX method)
    def hasThreadNext (self):

        p = self
        if not p.v: return False

        if p.hasChildren() or p.hasNext(): return True

        n = len(p.stack) -1
        while n >= 0:
            v,childIndex = p.stack[n]
            # See how many children v's parent has.
            if n == 0:
                parent_v = v.context.hiddenRootNode
            else:
                parent_v,junk = p.stack[n-1]
            if len(parent_v.t.children) > childIndex+1:
                # v has a next sibling.
                return True
            n -= 1
        return False
    #@-node:ekr.20080416161551.193:hasThreadNext (the only complex hasX method)
    #@-node:ekr.20080416161551.192:p.hasX (test)
    #@+node:ekr.20060920203352:p.findRootPosition (no change)
    def findRootPosition (self):

        p = self.copy()
        while p.hasParent():
            p.moveToParent()
        while p.hasBack():
            p.moveToBack()
        return p
    #@nonl
    #@-node:ekr.20060920203352:p.findRootPosition (no change)
    #@+node:ekr.20080416161551.194:p.isAncestorOf (test)
    def isAncestorOf (self, p2):

        p = self ; v = p.v

        for z in p2.stack:
            v2,junk = z
            if v2 == v:
                return True

        return False

        # # Avoid calling p.copy() or copying the stack.
        # v2 = p2.v ; n = len(p2.stack)-1
            # # Major bug fix 7/22/04: changed len(p.stack) to len(p2.stack.)
        # v2,n = p2.vParentWithStack(v2,p2.stack,n)
        # while v2:
            # if v2 == p.v:
                # return True
            # v2,n = p2.vParentWithStack(v2,p2.stack,n)

        # return False
    #@-node:ekr.20080416161551.194:p.isAncestorOf (test)
    #@+node:ekr.20040306215056:p.isCloned (no change)
    def isCloned (self):

        p = self
        return len(p.v.t.vnodeList) > 1
    #@-node:ekr.20040306215056:p.isCloned (no change)
    #@+node:ekr.20040307104131.2:p.isRoot (no change)
    def isRoot (self):

        p = self

        return not p.hasParent() and not p.hasBack()
    #@-node:ekr.20040307104131.2:p.isRoot (no change)
    #@+node:ekr.20080416161551.196:p.isVisible  (test)
    def isVisible (self,c):

        p = self
        trace = False
        limit,limitIsVisible = c.visLimit()
        limit_v = limit and limit.v or None
        if p.v == limit_v:
            if trace: g.trace('*** at limit','limitIsVisible',limitIsVisible,p.v.headString())
            return limitIsVisible

        # It's much easier with a full stack.
        n = len(p.stack)-1
        while n >= 0:
            progress = n
            # v,n = p.vParentWithStack(v,p.stack,n)
            v,junk = p.stack[n]
            if v == limit_v:  # We are at a descendant of limit.
                if trace: g.trace('*** descendant of limit',
                    'limitIsVisible',limitIsVisible,
                    'limit.isExpanded()',limit.isExpanded(),'v',v)
                if limitIsVisible:
                    return limit.isExpanded()
                else: # Ignore the expansion state of @chapter nodes.
                    return True
            if not v.isExpanded():
                if trace: g.trace('*** non-limit parent is not expanded',v)
                return False
            n -= 1
            assert progress > n

        return True


    # def isVisible (self,c):

        # """Return True if all of a position's parents are expanded."""

        # # v.isVisible no longer exists.
        # p = self ; cc = c.chapterController ; trace = False
        # limit,limitIsVisible = c.visLimit()
        # limit_v = limit and limit.v or None
        # if p.v == limit_v:
            # if trace: g.trace('*** at limit','limitIsVisible',limitIsVisible,p.v.headString())
            # return limitIsVisible

        # # Avoid calling p.copy() or copying the stack.
        # v = p.v ; n = len(p.stack)-1

        # v,n = p.vParentWithStack(v,p.stack,n)
        # while v:
            # if v == limit_v:  # We are at a descendant of limit.
                # if trace: g.trace('*** descendant of limit',
                    # 'limitIsVisible',limitIsVisible,
                    # 'limit.isExpanded()',limit.isExpanded(),'v',v)
                # if limitIsVisible:
                    # return limit.isExpanded()
                # else: # Ignore the expansion state of @chapter nodes.
                    # return True
            # if not v.isExpanded():
                # if trace: g.trace('*** non-limit parent is not expanded',v)
                # return False
            # v,n = p.vParentWithStack(v,p.stack,n)

        # return True
    #@-node:ekr.20080416161551.196:p.isVisible  (test)
    #@+node:ekr.20080416161551.197:p.level & simpleLevel (test)
    def level (p):
        return p.v and len(p.stack) or 0

    simpleLevel = level
    #@-node:ekr.20080416161551.197:p.level & simpleLevel (test)
    #@-node:ekr.20040306212636:p.Getters
    #@+node:ekr.20040305222924:p.Setters
    #@+node:ekr.20040306220634:p.Vnode proxies
    #@+node:ekr.20040306220634.9: Status bits (position)
    # Clone bits are no longer used.
    # Dirty bits are handled carefully by the position class.

    def clearMarked  (self): return self.v.clearMarked()
    def clearOrphan  (self): return self.v.clearOrphan()
    def clearVisited (self): return self.v.clearVisited()

    def contract (self): return self.v.contract()
    def expand   (self): return self.v.expand()

    def initExpandedBit    (self): return self.v.initExpandedBit()
    def initMarkedBit      (self): return self.v.initMarkedBit()
    def initStatus (self, status): return self.v.initStatus(status)

    def setMarked   (self): return self.v.setMarked()
    def setOrphan   (self): return self.v.setOrphan()
    def setSelected (self): return self.v.setSelected()
    def setVisited  (self): return self.v.setVisited()
    #@-node:ekr.20040306220634.9: Status bits (position)
    #@+node:ekr.20040306220634.8:p.computeIcon & p.setIcon
    def computeIcon (self):

        return self.v.computeIcon()

    def setIcon (self):

        pass # Compatibility routine for old scripts
    #@-node:ekr.20040306220634.8:p.computeIcon & p.setIcon
    #@+node:ekr.20040306220634.29:p.setSelection
    def setSelection (self,start,length):

        return self.v.setSelection(start,length)
    #@-node:ekr.20040306220634.29:p.setSelection
    #@+node:ekr.20040315034158:p.setTnodeText
    def setTnodeText (self,s,encoding="utf-8"):

        return self.v.setTnodeText(s,encoding)
    #@-node:ekr.20040315034158:p.setTnodeText
    #@-node:ekr.20040306220634:p.Vnode proxies
    #@+node:ekr.20040315031401:p.Head & body text
    #@+node:ekr.20040305222924.1:p.setHeadString & p.initHeadString
    def setHeadString (self,s,encoding="utf-8"):

        p = self
        p.v.initHeadString(s,encoding)
        p.setDirty()

    def initHeadString (self,s,encoding="utf-8"):

        p = self
        p.v.initHeadString(s,encoding)
    #@-node:ekr.20040305222924.1:p.setHeadString & p.initHeadString
    #@+node:ekr.20040315031445:p.scriptSetBodyString
    def scriptSetBodyString (self,s,encoding="utf-8"):

        """Update the body string for the receiver.

        Should be called only from scripts: does NOT update body text."""

        self.v.t._bodyString = g.toUnicode(s,encoding)
    #@-node:ekr.20040315031445:p.scriptSetBodyString
    #@-node:ekr.20040315031401:p.Head & body text
    #@+node:ekr.20040312015908:p.Visited bits
    #@+node:ekr.20040306220634.17:p.clearVisitedInTree
    # Compatibility routine for scripts.

    def clearVisitedInTree (self):

        for p in self.self_and_subtree_iter():
            p.clearVisited()
    #@-node:ekr.20040306220634.17:p.clearVisitedInTree
    #@+node:ekr.20031218072017.3388:p.clearAllVisitedInTree (4.2)
    def clearAllVisitedInTree (self):

        for p in self.self_and_subtree_iter():
            p.v.clearVisited()
            p.v.t.clearVisited()
            p.v.t.clearWriteBit()
    #@-node:ekr.20031218072017.3388:p.clearAllVisitedInTree (4.2)
    #@-node:ekr.20040312015908:p.Visited bits
    #@+node:ekr.20040305162628:p.Dirty bits
    #@+node:ekr.20040311113514:p.clearDirty
    def clearDirty (self):

        p = self
        p.v.clearDirty()
    #@-node:ekr.20040311113514:p.clearDirty
    #@+node:ekr.20040318125934:p.findAllPotentiallyDirtyNodes
    def findAllPotentiallyDirtyNodes(self):

        p = self 

        # Start with all nodes in the vnodeList.
        nodes = []
        newNodes = p.v.t.vnodeList[:]

        # Add nodes until no more are added.
        while newNodes:
            addedNodes = []
            nodes.extend(newNodes)
            for v in newNodes:
                for v2 in v.t.vnodeList:
                    if v2 not in nodes and v2 not in addedNodes:
                        addedNodes.append(v2)
                    for v3 in v2.directParents():
                        if v3 not in nodes and v3 not in addedNodes:
                            addedNodes.append(v3)
            newNodes = addedNodes[:]

        # g.trace(len(nodes))
        return nodes
    #@-node:ekr.20040318125934:p.findAllPotentiallyDirtyNodes
    #@+node:ekr.20040702104823:p.inAtIgnoreRange
    def inAtIgnoreRange (self):

        """Returns True if position p or one of p's parents is an @ignore node."""

        p = self

        for p in p.self_and_parents_iter():
            if p.isAtIgnoreNode():
                return True

        return False
    #@-node:ekr.20040702104823:p.inAtIgnoreRange
    #@+node:ekr.20040303214038:p.setAllAncestorAtFileNodesDirty
    def setAllAncestorAtFileNodesDirty (self,setDescendentsDirty=False):

        p = self
        dirtyVnodeList = []

        # Calculate all nodes that are joined to p or parents of such nodes.
        nodes = p.findAllPotentiallyDirtyNodes()

        if setDescendentsDirty:
            # N.B. Only mark _direct_ descendents of nodes.
            # Using the findAllPotentiallyDirtyNodes algorithm would mark way too many nodes.
            for p2 in p.subtree_iter():
                # Only @thin nodes need to be marked.
                if p2.v not in nodes and p2.isAtThinFileNode():
                    nodes.append(p2.v)

        dirtyVnodeList = [v for v in nodes
            if not v.t.isDirty() and v.isAnyAtFileNode()]
        changed = len(dirtyVnodeList) > 0

        for v in dirtyVnodeList:
            v.t.setDirty() # Do not call v.setDirty here!

        return dirtyVnodeList
    #@nonl
    #@-node:ekr.20040303214038:p.setAllAncestorAtFileNodesDirty
    #@+node:ekr.20040303163330:p.setDirty
    def setDirty (self,setDescendentsDirty=True):

        '''Mark a node and all ancestor @file nodes dirty.'''

        p = self ; dirtyVnodeList = []

        # g.trace(p.headString(),g.callers())

        if not p.v.t.isDirty():
            p.v.t.setDirty()
            dirtyVnodeList.append(p.v)

        # Important: this must be called even if p.v is already dirty.
        # Typing can change the @ignore state!
        dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty(setDescendentsDirty)
        dirtyVnodeList.extend(dirtyVnodeList2)

        return dirtyVnodeList
    #@-node:ekr.20040303163330:p.setDirty
    #@-node:ekr.20040305162628:p.Dirty bits
    #@-node:ekr.20040305222924:p.Setters
    #@+node:ekr.20040315023430:P.File Conversion
    #@+at
    # - convertTreeToString and moreHead can't be vnode methods because they 
    # uses level().
    # - moreBody could be anywhere: it may as well be a postion method.
    #@-at
    #@+node:ekr.20040315023430.1:convertTreeToString
    def convertTreeToString (self):

        """Convert a positions  suboutline to a string in MORE format."""

        p = self ; level1 = p.level()

        array = []
        for p in p.self_and_subtree_iter():
            array.append(p.moreHead(level1)+'\n')
            body = p.moreBody()
            if body:
                array.append(body +'\n')

        return ''.join(array)
    #@-node:ekr.20040315023430.1:convertTreeToString
    #@+node:ekr.20040315023430.2:moreHead
    def moreHead (self, firstLevel,useVerticalBar=False):

        """Return the headline string in MORE format."""

        # useVerticalBar is unused, but it would be useful in over-ridden methods.
        # __pychecker__ = '--no-argsused'

        p = self
        level = self.level() - firstLevel
        plusMinus = g.choose(p.hasChildren(), "+", "-")

        return "%s%s %s" % ('\t'*level,plusMinus,p.headString())
    #@-node:ekr.20040315023430.2:moreHead
    #@+node:ekr.20040315023430.3:moreBody
    #@+at 
    #     + test line
    #     - test line
    #     \ test line
    #     test line +
    #     test line -
    #     test line \
    #     More lines...
    #@-at
    #@@c

    def moreBody (self):

        """Returns the body string in MORE format.  

        Inserts a backslash before any leading plus, minus or backslash."""

        p = self ; array = []
        lines = string.split(p.bodyString(),'\n')
        for s in lines:
            i = g.skip_ws(s,0)
            if i < len(s) and s[i] in ('+','-','\\'):
                s = s[:i] + '\\' + s[i:]
            array.append(s)
        return '\n'.join(array)
    #@-node:ekr.20040315023430.3:moreBody
    #@-node:ekr.20040315023430:P.File Conversion
    #@+node:ekr.20040305162628.1:p.Iterators
    #@+at 
    #@nonl
    # A crucial optimization:
    # 
    # Iterators make no copies at all if they would return an empty sequence.
    #@-at
    #@@c

    #@+others
    #@+node:EKR.20040529103843:p.tnodes_iter
    # def tnodes_iter(self):

        # """Return all tnode's in a positions subtree."""

        # p = self
        # for p in p.self_and_subtree_iter():
            # yield p.v.t

    class tnodes_iter_class:

        """Returns a list of positions in a subtree, possibly including the root of the subtree."""

        #@    @+others
        #@+node:ekr.20070930191649.1:__init__ & __iter__ (p.tnodes_iter)
        def __init__(self,p):

            # g.trace('p.tnodes_iter.__init','p',p)

            self.first = p.copy()
            self.p = None

        def __iter__(self):

            return self
        #@-node:ekr.20070930191649.1:__init__ & __iter__ (p.tnodes_iter)
        #@+node:ekr.20070930191649.2:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None
            elif self.p:
                self.p.moveToThreadNext()

            if self.p:
                return self.p.v.t

            else: raise StopIteration
        #@-node:ekr.20070930191649.2:next
        #@-others

    def tnodes_iter (self):

        p = self
        return self.tnodes_iter_class(p)
    #@-node:EKR.20040529103843:p.tnodes_iter
    #@+node:ekr.20070930191632:p.unique_tnodes_iter
    # def unique_tnodes_iter(self):

        # """Return all unique tnode's in a positions subtree."""

        # p = self
        # marks = {}
        # for p in p.self_and_subtree_iter():
            # if p.v.t not in marks:
                # marks[p.v.t] = p.v.t
                # yield p.v.t

    class unique_tnodes_iter_class:

        """Returns a list of positions in a subtree, possibly including the root of the subtree."""

        #@    @+others
        #@+node:ekr.20070930192032.1:__init__ & __iter__ (p.unique_tnodes_iter)
        def __init__(self,p):

            # g.trace('p.unique_tnodes_iter.__init','p',p,)

            self.d = {}
            self.first = p.copy()
            self.p = None

        def __iter__(self):

            return self
        #@-node:ekr.20070930192032.1:__init__ & __iter__ (p.unique_tnodes_iter)
        #@+node:ekr.20070930192032.2:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None

            while self.p:
                self.p.moveToThreadNext()
                if not self.p:
                    break
                elif not self.d.get(self.p.v.t):
                    self.d [self.p.v.t] = True
                    return self.p.v.t

            else: raise StopIteration
        #@-node:ekr.20070930192032.2:next
        #@-others

    def unique_tnodes_iter (self):

        p = self
        return self.unique_tnodes_iter_class(p)
    #@-node:ekr.20070930191632:p.unique_tnodes_iter
    #@+node:EKR.20040529103945:p.vnodes_iter
    # def vnodes_iter(self):

        # """Return all vnode's in a positions subtree."""

        # p = self
        # for p in p.self_and_subtree_iter():
            # yield p.v

    class vnodes_iter_class:

        """Returns a list of positions in a subtree, possibly including the root of the subtree."""

        #@    @+others
        #@+node:ekr.20070930192339.1:__init__ & __iter__ (p.tnodes_iter)
        def __init__(self,p):

            # g.trace('p.tnodes_iter.__init','p',p)

            self.first = p.copy()
            self.p = None

        def __iter__(self):

            return self
        #@-node:ekr.20070930192339.1:__init__ & __iter__ (p.tnodes_iter)
        #@+node:ekr.20070930192339.2:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None
            elif self.p:
                self.p.moveToThreadNext()

            if self.p:
                return self.p.v

            else: raise StopIteration
        #@-node:ekr.20070930192339.2:next
        #@-others

    def vnodes_iter (self):

        p = self
        return self.vnodes_iter_class(p)


    #@-node:EKR.20040529103945:p.vnodes_iter
    #@+node:ekr.20070930191632.1:p.unique_vnodes_iter
    # def unique_vnodes_iter(self):

        # """Return all unique vnode's in a positions subtree."""

        # p = self
        # marks = {}
        # for p in p.self_and_subtree_iter():
            # if p.v not in marks:
                # marks[p.v] = p.v
                # yield p.v

    class unique_vnodes_iter_class:

        """Returns a list of positions in a subtree, possibly including the root of the subtree."""

        #@    @+others
        #@+node:ekr.20070930192441.1:__init__ & __iter__ (p.unique_vnodes_iter)
        def __init__(self,p):

            # g.trace('p.unique_tnodes_iter.__init','p',p,)

            self.d = {}
            self.first = p.copy()
            self.p = None

        def __iter__(self):

            return self
        #@-node:ekr.20070930192441.1:__init__ & __iter__ (p.unique_vnodes_iter)
        #@+node:ekr.20070930192441.2:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None

            while self.p:
                self.p.moveToThreadNext()
                if not self.p:
                    break
                elif not self.d.get(self.p.v.t):
                    self.d [self.p.v.t] = True
                    return self.p.v

            else: raise StopIteration
        #@-node:ekr.20070930192441.2:next
        #@-others

    def unique_vnodes_iter (self):

        p = self
        return self.unique_vnodes_iter_class(p)
    #@-node:ekr.20070930191632.1:p.unique_vnodes_iter
    #@+node:ekr.20040305173559:p.subtree_iter
    class subtree_iter_class:

        """Returns a list of positions in a subtree, possibly including the root of the subtree."""

        #@    @+others
        #@+node:ekr.20040305173559.1:__init__ & __iter__
        def __init__(self,p,copy,includeSelf):

            if includeSelf:
                self.first = p.copy()
                self.after = p.nodeAfterTree()
            elif p.hasChildren():
                self.first = p.copy().moveToFirstChild() 
                self.after = p.nodeAfterTree()
            else:
                self.first = None
                self.after = None

            self.p = None
            self.copy = copy

        def __iter__(self):

            return self
        #@-node:ekr.20040305173559.1:__init__ & __iter__
        #@+node:ekr.20040305173559.2:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None

            elif self.p:
                self.p.moveToThreadNext()

            if self.p and self.p != self.after:
                if self.copy: return self.p.copy()
                else:         return self.p
            else:
                raise StopIteration
        #@-node:ekr.20040305173559.2:next
        #@-others

    def subtree_iter (self,copy=False):

        return self.subtree_iter_class(self,copy,includeSelf=False)

    def self_and_subtree_iter (self,copy=False):

        return self.subtree_iter_class(self,copy,includeSelf=True)
    #@-node:ekr.20040305173559:p.subtree_iter
    #@+node:ekr.20040305172211.1:p.children_iter
    class children_iter_class:

        """Returns a list of children of a position."""

        #@    @+others
        #@+node:ekr.20040305172211.2:__init__ & __iter__
        def __init__(self,p,copy):

            if p.hasChildren():
                self.first = p.copy().moveToFirstChild()
            else:
                self.first = None

            self.p = None
            self.copy = copy

        def __iter__(self):

            return self
        #@-node:ekr.20040305172211.2:__init__ & __iter__
        #@+node:ekr.20040305172211.3:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None

            elif self.p:
                self.p.moveToNext()

            if self.p:
                if self.copy: return self.p.copy()
                else:         return self.p
            else: raise StopIteration
        #@-node:ekr.20040305172211.3:next
        #@-others

    def children_iter (self,copy=False):

        return self.children_iter_class(self,copy)
    #@-node:ekr.20040305172211.1:p.children_iter
    #@+node:ekr.20040305172855:p.parents_iter
    class parents_iter_class:

        """Returns a list of positions of a position."""

        #@    @+others
        #@+node:ekr.20040305172855.1:__init__ & __iter__
        def __init__(self,p,copy,includeSelf):

            if includeSelf:
                self.first = p.copy()
            elif p.hasParent():
                self.first = p.copy().moveToParent()
            else:
                self.first = None

            self.p = None
            self.copy = copy

        def __iter__(self):

            return self
        #@-node:ekr.20040305172855.1:__init__ & __iter__
        #@+node:ekr.20040305172855.2:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None

            elif self.p:
                self.p.moveToParent()

            if self.p:
                if self.copy: return self.p.copy()
                else:         return self.p
            else:
                raise StopIteration
        #@-node:ekr.20040305172855.2:next
        #@-others

    def parents_iter (self,copy=False):

        return self.parents_iter_class(self,copy,includeSelf=False)

    def self_and_parents_iter(self,copy=False):

        return self.parents_iter_class(self,copy,includeSelf=True)
    #@-node:ekr.20040305172855:p.parents_iter
    #@+node:ekr.20040305173343:p.siblings_iter
    class siblings_iter_class:

        '''Returns a list of siblings of a position, including the position itself!'''

        #@    @+others
        #@+node:ekr.20040305173343.1:__init__ & __iter__
        def __init__(self,p,copy,following):

            # We always include p, even if following is True.

            if following:
                self.first = p.copy()
            else:
                p = p.copy()
                while p.hasBack():
                    p.moveToBack()
                self.first = p

            self.p = None
            self.copy = copy

        def __iter__(self):

            return self
        #@-node:ekr.20040305173343.1:__init__ & __iter__
        #@+node:ekr.20040305173343.2:next
        def next(self):

            if self.first:
                self.p = self.first
                self.first = None

            elif self.p:
                self.p.moveToNext()

            if self.p:
                if self.copy: return self.p.copy()
                else:         return self.p
            else: raise StopIteration
        #@-node:ekr.20040305173343.2:next
        #@-others

    def siblings_iter (self,copy=False,following=False):

        return self.siblings_iter_class(self,copy,following)

    self_and_siblings_iter = siblings_iter

    def following_siblings_iter (self,copy=False):

        return self.siblings_iter_class(self,copy,following=True)
    #@-node:ekr.20040305173343:p.siblings_iter
    #@-others
    #@-node:ekr.20040305162628.1:p.Iterators
    #@+node:ekr.20040303175026:p.Moving, Inserting, Deleting, Cloning, Sorting
    #@+node:ekr.20040303175026.8:p.clone
    def clone (self):

        """Create a clone of back.

        Returns the newly created position."""

        p = self ; context = p.v.context

        p2 = p.copy()
        p2.v = vnode(context=context,t=p2.v.t)
        p2.linkAfter(p)
        assert (p.v.t == p2.v.t)

        return p2
    #@-node:ekr.20040303175026.8:p.clone
    #@+node:ekr.20040303175026.9:p.copyTreeAfter, copyTreeTo
    # These used by unit tests and by the group_operations plugin.

    def copyTreeAfter(self):
        p = self
        p2 = p.insertAfter()
        p.copyTreeFromSelfTo(p2)
        return p2

    def copyTreeFromSelfTo(self,p2):
        p = self
        p2.v.t._headString = p.headString()
        p2.v.t._bodyString = p.bodyString()
        for child in p.children_iter(copy=True):
            child2 = p2.insertAsLastChild()
            child.copyTreeFromSelfTo(child2)
    #@-node:ekr.20040303175026.9:p.copyTreeAfter, copyTreeTo
    #@+node:ekr.20040303175026.2:p.doDelete
    #@+at 
    #@nonl
    # This is the main delete routine.  It deletes the receiver's entire tree 
    # from the screen.  Because of the undo command we never actually delete 
    # vnodes or tnodes.
    #@-at
    #@@c

    def doDelete (self):

        """Deletes position p from the outline."""

        p = self
        p.setDirty() # Mark @file nodes dirty!
        p.unlink()
        p.deleteLinksInTree()
    #@-node:ekr.20040303175026.2:p.doDelete
    #@+node:ekr.20040303175026.3:p.insertAfter
    def insertAfter (self,t=None):

        """Inserts a new position after self.

        Returns the newly created position."""

        p = self ; context = p.v.context
        p2 = self.copy()

        if not t:
            t = tnode(headString="NewHeadline")

        p2.v = vnode(context=context,t=t)
        p2.v.iconVal = 0
        p2.linkAfter(p)

        return p2
    #@-node:ekr.20040303175026.3:p.insertAfter
    #@+node:ekr.20040303175026.4:p.insertAsLastChild
    def insertAsLastChild (self,t=None):

        """Inserts a new vnode as the last child of self.

        Returns the newly created position."""

        p = self
        n = p.numberOfChildren()

        if not t:
            t = tnode(headString="NewHeadline")

        return p.insertAsNthChild(n,t)
    #@-node:ekr.20040303175026.4:p.insertAsLastChild
    #@+node:ekr.20040303175026.5:p.insertAsNthChild (no change)
    def insertAsNthChild (self,n,t=None):

        """Inserts a new node as the the nth child of self.
        self must have at least n-1 children.

        Returns the newly created position."""

        p = self ; context = p.v.context
        p2 = self.copy()

        if not t:
            t = tnode(headString="NewHeadline")

        p2.v = vnode(context=context,t=t)
        p2.v.iconVal = 0
        p2.linkAsNthChild(p,n)

        return p2
    #@-node:ekr.20040303175026.5:p.insertAsNthChild (no change)
    #@+node:ekr.20040310062332.1:p.invalidOutline
    def invalidOutline (self, message):

        p = self

        if p.hasParent():
            node = p.parent()
        else:
            node = p

        g.alert("invalid outline: %s\n%s" % (message,node))
    #@-node:ekr.20040310062332.1:p.invalidOutline
    #@+node:ekr.20040303175026.10:p.moveAfter
    def moveAfter (self,a):

        """Move a position after position a."""

        p = self # Do NOT copy the position!
        p.unlink()
        p.linkAfter(a)

        return p
    #@nonl
    #@-node:ekr.20040303175026.10:p.moveAfter
    #@+node:ekr.20040306060312:p.moveToFirst/LastChildOf
    def moveToFirstChildOf (self,parent):

        """Move a position to the first child of parent."""

        p = self # Do NOT copy the position!
        p.unlink()
        p.linkAsNthChild(parent,0)
        return p


    def moveToLastChildOf (self,parent):

        """Move a position to the last child of parent."""

        p = self # Do NOT copy the position!
        p.unlink()
        n = parent.numberOfChildren()
        p.linkAsNthChild(parent,n)
        return p
    #@-node:ekr.20040306060312:p.moveToFirst/LastChildOf
    #@+node:ekr.20040303175026.11:p.moveToNthChildOf
    def moveToNthChildOf (self,parent,n):

        """Move a position to the nth child of parent."""

        p = self # Do NOT copy the position!
        p.unlink()
        p.linkAsNthChild(parent,n)

        return p
    #@nonl
    #@-node:ekr.20040303175026.11:p.moveToNthChildOf
    #@+node:ekr.20040303175026.6:p.moveToRoot
    def moveToRoot (self,oldRoot=None):

        '''Moves a position to the root position.

        Important: oldRoot must the previous root position if it exists.'''

        p = self # Do NOT copy the position!
        p.unlink()
        p.linkAsRoot(oldRoot)

        return p
    #@-node:ekr.20040303175026.6:p.moveToRoot
    #@+node:ekr.20040303175026.13:p.validateOutlineWithParent
    # This routine checks the structure of the receiver's tree.

    def validateOutlineWithParent (self,pv):

        p = self
        result = True # optimists get only unpleasant surprises.
        parent = p.getParent()
        childIndex = p._childIndex

        # g.trace(p,parent,pv)
        #@    << validate parent ivar >>
        #@+node:ekr.20040303175026.14:<< validate parent ivar >>
        if parent != pv:
            p.invalidOutline( "Invalid parent link: " + repr(parent))
        #@-node:ekr.20040303175026.14:<< validate parent ivar >>
        #@nl
        #@    << validate childIndex ivar >>
        #@+node:ekr.20040303175026.15:<< validate childIndex ivar >>
        if pv:
            if childIndex < 0:
                p.invalidOutline ( "missing childIndex" + childIndex )
            elif childIndex >= pv.numberOfChildren():
                p.invalidOutline ( "missing children entry for index: " + childIndex )
        elif childIndex < 0:
            p.invalidOutline ( "negative childIndex" + childIndex )
        #@-node:ekr.20040303175026.15:<< validate childIndex ivar >>
        #@nl
        #@    << validate x ivar >>
        #@+node:ekr.20040303175026.16:<< validate x ivar >>
        if not p.v.t and pv:
            self.invalidOutline ( "Empty t" )
        #@-node:ekr.20040303175026.16:<< validate x ivar >>
        #@nl

        # Recursively validate all the children.
        for child in p.children_iter():
            r = child.validateOutlineWithParent(p)
            if not r: result = False

        return result
    #@-node:ekr.20040303175026.13:p.validateOutlineWithParent
    #@-node:ekr.20040303175026:p.Moving, Inserting, Deleting, Cloning, Sorting
    #@+node:ekr.20080416161551.199:p.moveToX
    #@+at
    # These routines change self to a new position "in place".
    # That is, these methods must _never_ call p.copy().
    # 
    # When moving to a nonexistent position, these routines simply set p.v = 
    # None,
    # leaving the p.stack unchanged. This allows the caller to "undo" the 
    # effect of
    # the invalid move by simply restoring the previous value of p.v.
    # 
    # These routines all return self on exit so the following kind of code 
    # will work:
    #     after = p.copy().moveToNodeAfterTree()
    #@-at
    #@+node:ekr.20080416161551.200:p.moveToBack
    def moveToBack (self):

        """Move self to its previous sibling."""

        p = self ; n = p._childIndex

        parent_v = p.parentNode(includeHiddenRootNode = True)
            # Returns None if p.v is None.

        # Do not assume n is in range: this is used by positionExists.
        if parent_v and p.v and 0 < n <= len(parent_v.t.children):
            p._childIndex -= 1
            p.v = parent_v.t.children[n-1]
        else:
            p.v = None

        return p
    #@-node:ekr.20080416161551.200:p.moveToBack
    #@+node:ekr.20080416161551.201:p.moveToFirstChild
    def moveToFirstChild (self):

        """Move a position to it's first child's position."""

        p = self

        if p.v and p.v.t.children:
            p.stack.append((p.v,p._childIndex),)
            p.v = p.v.t.children[0]
            p._childIndex = 0
        else:
            p.v = None

        return p
    #@nonl
    #@-node:ekr.20080416161551.201:p.moveToFirstChild
    #@+node:ekr.20080416161551.202:p.moveToLastChild
    def moveToLastChild (self):

        """Move a position to it's last child's position."""

        p = self

        if p.v and p.v.t.children:
            p.stack.append((p.v,p._childIndex),)
            n = len(p.v.t.children)
            p.v = p.v.t.children[n-1]
            p._childIndex = n-1
        else:
            p.v = None

        return p
    #@-node:ekr.20080416161551.202:p.moveToLastChild
    #@+node:ekr.20080416161551.203:p.moveToLastNode
    def moveToLastNode (self):

        """Move a position to last node of its tree.

        N.B. Returns p if p has no children."""

        p = self

        # Huge improvement for 4.2.
        while p.hasChildren():
            p.moveToLastChild()

        return p
    #@-node:ekr.20080416161551.203:p.moveToLastNode
    #@+node:ekr.20080416161551.204:p.moveToNext
    def moveToNext (self):

        """Move a position to its next sibling."""

        p = self ; n = p._childIndex

        parent_v = p.parentNode(includeHiddenRootNode = True)
            # Returns None if p.v is None.
        if not p.v: g.trace('parent_v',parent_v,'p.v',p.v)

        if p.v and parent_v and len(parent_v.t.children) > n+1:
            p._childIndex = n+1
            p.v = parent_v.t.children[n+1]
        else:
            p.v = None

        return p
    #@-node:ekr.20080416161551.204:p.moveToNext
    #@+node:ekr.20080416161551.205:p.moveToNodeAfterTree
    def moveToNodeAfterTree (self):

        """Move a position to the node after the position's tree."""

        p = self

        while p:
            if p.hasNext():
                p.moveToNext()
                break
            p.moveToParent()

        return p
    #@-node:ekr.20080416161551.205:p.moveToNodeAfterTree
    #@+node:ekr.20080416161551.206:p.moveToNthChild
    def moveToNthChild (self,n):

        p = self

        if p.v and len(p.v.t.children) > n:
            p.stack.append((p.v,p._childIndex),)
            p.v = p.v.t.children[n]
            p._childIndex = n
        else:
            p.v = None

        return p
    #@-node:ekr.20080416161551.206:p.moveToNthChild
    #@+node:ekr.20080416161551.207:p.moveToParent
    def moveToParent (self):

        """Move a position to its parent position."""

        p = self

        if p.v and p.stack:
            p.v,p._childIndex = p.stack.pop()
        else:
            p.v = None

        return p
    #@-node:ekr.20080416161551.207:p.moveToParent
    #@+node:ekr.20080416161551.208:p.moveToThreadBack
    def moveToThreadBack (self):

        """Move a position to it's threadBack position."""

        p = self

        if p.hasBack():
            p.moveToBack()
            p.moveToLastNode()
        else:
            p.moveToParent()

        return p
    #@-node:ekr.20080416161551.208:p.moveToThreadBack
    #@+node:ekr.20080416161551.209:p.moveToThreadNext
    def moveToThreadNext (self):

        """Move a position to threadNext position."""

        p = self

        if p.v:
            if p.v.t.children:
                p.moveToFirstChild()
            elif p.hasNext():
                p.moveToNext()
            else:
                p.moveToParent()
                while p:
                    if p.hasNext():
                        p.moveToNext()
                        break #found
                    p.moveToParent()
                # not found.

        return p
    #@-node:ekr.20080416161551.209:p.moveToThreadNext
    #@+node:ekr.20080416161551.210:p.moveToVisBack
    def moveToVisBack (self,c):

        """Move a position to the position of the previous visible node."""

        p = self ; limit,limitIsVisible = c.visLimit() ; trace = False

        def checkLimit (p):
            '''Return done, return-val'''
            if limit:
                if limit == p:
                    if trace: g.trace('at limit',p)
                    return True,g.choose(limitIsVisible and p.isVisible(c),p,None)
                elif limit.isAncestorOf(p):
                    return False,None
                else:
                    if trace: g.trace('outside limit tree')
                    return True,None
            else:
                return False,None

        while p:
            # Short-circuit if possible.
            back = p.back()
            if back and (not back.hasChildren() or not back.isExpanded()):
                p.moveToBack()
            else:
                p.moveToThreadBack()
            if p:
                if trace: g.trace('*p',p.headString())
                done,val = checkLimit(p)
                if done: return val
                if p.isVisible(c):
                    return p
        else:
            # assert not p.
            return p
    #@nonl
    #@-node:ekr.20080416161551.210:p.moveToVisBack
    #@+node:ekr.20080416161551.211:p.moveToVisNext
    def moveToVisNext (self,c):

        """Move a position to the position of the next visible node."""

        p = self ; limit,limitIsVisible = c.visLimit() ; trace = False

        def checkLimit (p):
            '''Return done, return-val'''
            if limit:
                # Unlike moveToVisBack, being at the limit does not terminate.
                if limit == p:
                    return False, None
                elif limit.isAncestorOf(p):
                    return False,None
                else:
                    if trace: g.trace('outside limit tree')
                    return True,None
            else:
                return False,None

        while p:
            # Short-circuit if possible.
            if p.hasNext() and (not p.hasChildren() or not p.isExpanded()):
                p.moveToNext()
            else:
                p.moveToThreadNext()
            if p:
                if trace: g.trace('*p',p.headString())
                done,val = checkLimit(p)
                if done: return val
                if p.isVisible(c):
                    return p.copy()
        else:
            # assert not p.
            return p
    #@nonl
    #@-node:ekr.20080416161551.211:p.moveToVisNext
    #@-node:ekr.20080416161551.199:p.moveToX
    #@+node:ekr.20040228094013.1:p.utils... (test)
    #@+node:ekr.20080416161551.212:p.parentNode (New, test)
    def parentNode (self,includeHiddenRootNode=False):

        '''return a new position representing the parent position.

        This is always inexpensive.'''

        p = self

        if p.v:
            data = p.stack and p.stack[-1]
            if data:
                v, junk = data
                return v
            elif includeHiddenRootNode:
                return p.v.context.hiddenRootNode
            else:
                return None
        else:
            return None
    #@-node:ekr.20080416161551.212:p.parentNode (New, test)
    #@+node:ekr.20040409203454:p.restoreLinksInTree (no change)
    def restoreLinksInTree (self):

        """Restore links when undoing a delete node operation."""

        root = p = self

        if p.v not in p.v.t.vnodeList:
            p.v.t.vnodeList.append(p.v)
            p.v.t._p_changed = 1 # Support for tnode class.

        for p in root.children_iter():
            p.restoreLinksInTree()
    #@-node:ekr.20040409203454:p.restoreLinksInTree (no change)
    #@+node:ekr.20040409203454.1:p.deleteLinksInTree & allies (????)
    def deleteLinksInTree (self):

        """Delete and otherwise adjust links when deleting node."""

        root = self

        root.deleteLinksInSubtree()

        for p in root.children_iter():
            p.adjustParentLinksInSubtree(parent=root)
    #@+node:ekr.20040410170806:p.deleteLinksInSubtree
    def deleteLinksInSubtree (self):

        root = p = self

        # Delete p.v from the vnodeList
        if p.v in p.v.t.vnodeList:
            # g.trace('**** remove p.v from %s' % p.headString())
            p.v.t.vnodeList.remove(p.v)
            p.v.t._p_changed = 1  # Support for tnode class.
            assert(p.v not in p.v.t.vnodeList)
        else:
            # g.trace("not in vnodeList",p.v,p.vnodeListIds())
            pass

        if len(p.v.t.vnodeList) == 0:
            # This node is not shared by other nodes.
            for p in root.children_iter():
                p.deleteLinksInSubtree()
    #@-node:ekr.20040410170806:p.deleteLinksInSubtree
    #@+node:ekr.20040410170806.1:p.adjustParentLinksInSubtree
    def adjustParentLinksInSubtree (self,parent):

        root = p = self

        # assert(parent)

        # if p.v._parent and parent.v.t.vnodeList and p.v._parent not in parent.v.t.vnodeList:
            # # g.trace('**** adjust parent in %s' % p.headString())
            # p.v._parent = parent.v.t.vnodeList[0]

        # for p in root.children_iter():
            # p.adjustParentLinksInSubtree(parent=root)
    #@-node:ekr.20040410170806.1:p.adjustParentLinksInSubtree
    #@-node:ekr.20040409203454.1:p.deleteLinksInTree & allies (????)
    #@-node:ekr.20040228094013.1:p.utils... (test)
    #@+node:ekr.20080416161551.213:p.Link/Unlink methods
    # These remain in 4.2:  linking and unlinking does not depend on position.

    # These are private routines:  the position class does not define proxies for these.
    #@+node:ekr.20080416161551.214:p.linkAfter
    def linkAfter (self,p_after):

        '''Link self after p_after.'''

        p = self
        parent_v = p_after.parentNode(includeHiddenRootNode=True)
            # Returns None if p.v is None

        # Init the ivars.
        p.stack = p_after.stack[:]
        p._childIndex = p_after._childIndex + 1

        # Add v to it's tnode's vnodeList.
        if p.v not in p.v.t.vnodeList:
            p.v.t.vnodeList.append(p.v)
            p.v.t._p_changed = 1 # Support for tnode class.

        # Add p.v to parent_v's children.
        parent_v.t.children.insert(p_after._childIndex+1,p.v)
        parent_v._p_changed = 1

        # Add parent_v to p.v.t.parents.
        if not parent_v in p.v.t.parents:
            p.v.t.parents.append(parent_v)
            p.v._p_changed = 1
    #@-node:ekr.20080416161551.214:p.linkAfter
    #@+node:ekr.20080416161551.215:p.linkAsNthChild
    def linkAsNthChild (self,parent,n):

        p = self
        parent_v = parent.v

        # Init the ivars.
        p.stack = parent.stack[:]
        p.stack.append((parent_v,parent._childIndex),)
        p._childIndex = n

        # Add p.v to it's tnode's vnodeList.
        if p.v not in p.v.t.vnodeList:
            p.v.t.vnodeList.append(p.v)
            p.v.t._p_changed = 1 # Support for tnode class.

        # Add p.v to parent_v's children.
        parent_v.t.children.insert(n,p.v)
        parent_v._p_changed = 1

        # Add parent_v to p.v's parents.
        if not parent_v in p.v.t.parents:
            p.v.t.parents.append(parent_v)
            p.v._p_changed = 1
    #@-node:ekr.20080416161551.215:p.linkAsNthChild
    #@+node:ekr.20080416161551.216:p.linkAsRoot
    def linkAsRoot (self,oldRoot):

        """Link self as the root node."""

        p = self
        assert(p.v)

        hiddenRootNode = p.v.context.hiddenRootNode

        if oldRoot: oldRootNode = oldRoot.v
        else:       oldRootNode = None

        # Init the ivars.
        p.stack = []
        p._childIndex = 0

        # Init p.v.t.vnodeList
        p.v.t.vnodeList = [p.v]

        # Init p.v.t.parents to the hidden root node.
        p.v.t.parents = [hiddenRootNode]
        p.v._p_changed = 1

        # Init hiddenRootNode's children to p.v.
        hiddenRootNode.t.children = [p.v]

        # Link in the rest of the tree only when oldRoot != None.
        # Otherwise, we are calling this routine from init code and
        # we want to start with a pristine tree.
        if oldRoot:
            hiddenRootNode.t.children.append(oldRootNode)
            oldRootNode.parents = [hiddenRootNode]
            oldRootNode.t.vnodeList = [oldRootNode]
    #@-node:ekr.20080416161551.216:p.linkAsRoot
    #@+node:ekr.20080416161551.217:p.unlink
    def unlink (self):

        p = self ; n = p._childIndex
        parent_v = p.parentNode(includeHiddenRootNode=True)
            # returns None if p.v is None
        assert(p.v)
        assert(parent_v)

        # Remove v from it's tnode's vnodeList.
        if p.v in p.v.t.vnodeList:
            p.v.t.vnodeList.remove(p.v)
            p.v.t._p_changed = 1 # Support for tnode class.

        # Delete p.v from parent_v's children.
        del parent_v.t.children[n:n+1]
        parent_v._p_changed = 1

        # Delete parent_v from p.v's parents.
        if parent_v in p.v.t.parents:
            p.v.t.parents.remove(parent_v)
            p.v._p_changed = 1 # Support for tnode class.

    #@-node:ekr.20080416161551.217:p.unlink
    #@-node:ekr.20080416161551.213:p.Link/Unlink methods
    #@-others

class position (basePosition):
    pass
#@nonl
#@-node:ekr.20031218072017.889:class position
#@-others
#@nonl
#@-node:ekr.20031218072017.3320:@thin leoNodes.py
#@-leo

# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20041005105605.1:@thin leoAtFile.py
#@@first
    # Needed because of unicode characters in tests.

"""Classes to read and write @file nodes."""

#@@language python
#@@tabwidth -4
#@@pagewidth 80

# __pychecker__ = '--no-reimport --no-constCond -- no-constant1'
    # Reimports needed in test methods.
    # Disable checks for if 0, if 1.

#@<< imports >>
#@+node:ekr.20041005105605.2:<< imports >>
import leoGlobals as g

if g.app and g.app.use_psyco:
    # print "enabled psyco classes",__file__
    try: from psyco.classes import *
    except ImportError: pass

import leoNodes
import os
import string
import time
#@-node:ekr.20041005105605.2:<< imports >>
#@nl

class atFile:

    """The class implementing the atFile subcommander."""

    #@    << define class constants >>
    #@+node:ekr.20041005105605.5:<< define class constants >>
    # These constants must be global to this module because they are shared by several classes.

    # The kind of at_directives.
    noDirective     =  1 # not an at-directive.
    allDirective    =  2 # at-all (4.2)
    docDirective    =  3 # @doc.
    atDirective     =  4 # @<space> or @<newline>
    codeDirective   =  5 # @code
    cDirective      =  6 # @c<space> or @c<newline>
    othersDirective =  7 # at-others
    miscDirective   =  8 # All other directives
    rawDirective    =  9 # @raw
    endRawDirective = 10 # @end_raw

    # The kind of sentinel line.
    noSentinel   = 20 # Not a sentinel
    endAt        = 21 # @-at
    endBody      = 22 # @-body
    # not used   = 23
    endDoc       = 24 # @-doc
    endLeo       = 25 # @-leo
    endNode      = 26 # @-node
    endOthers    = 27 # @-others

    # not used     = 40
    startAt        = 41 # @+at
    startBody      = 42 # @+body
    startDoc       = 43 # @+doc
    startLeo       = 44 # @+leo
    startNode      = 45 # @+node
    startOthers    = 46 # @+others

    startComment   = 60 # @comment
    startDelims    = 61 # @delims
    startDirective = 62 # @@
    startRef       = 63 # @< < ... > >
    startVerbatim  = 64 # @verbatim
    startVerbatimAfterRef = 65 # @verbatimAfterRef (3.0 only)

    # New in 4.x. Paired
    endAll         = 70 # at-all (4.2)
    endMiddle      = 71 # at-middle (4.2)
    startAll       = 72 # at+all (4.2)
    startMiddle    = 73 # at+middle (4.2)

    # New in 4.x.  Unpaired.
    startAfterRef  = 80 # @afterref (4.0)
    startClone     = 81 # @clone (4.2)
    startNl        = 82 # @nl (4.0)
    startNonl      = 83 # @nonl (4.0)
    #@-node:ekr.20041005105605.5:<< define class constants >>
    #@nl
    #@    << define sentinelDict >>
    #@+node:ekr.20041005105605.6:<< define sentinelDict >>
    sentinelDict = {

        # Unpaired sentinels: 3.x and 4.x.
        "@comment" : startComment,
        "@delims" :  startDelims,
        "@verbatim": startVerbatim,

        # Unpaired sentinels: 3.x only.
        "@verbatimAfterRef": startVerbatimAfterRef,

        # Unpaired sentinels: 4.x only.
        "@afterref" : startAfterRef,
        "@clone"    : startClone,
        "@nl"       : startNl,
        "@nonl"     : startNonl,

        # Paired sentinels: 3.x only.
        "@+body":   startBody,   "@-body":   endBody,

        # Paired sentinels: 3.x and 4.x.
        "@+all":    startAll,    "@-all":    endAll,
        "@+at":     startAt,     "@-at":     endAt,
        "@+doc":    startDoc,    "@-doc":    endDoc,
        "@+leo":    startLeo,    "@-leo":    endLeo,
        "@+middle": startMiddle, "@-middle": endMiddle,
        "@+node":   startNode,   "@-node":   endNode,
        "@+others": startOthers, "@-others": endOthers,
    }
    #@-node:ekr.20041005105605.6:<< define sentinelDict >>
    #@nl

    #@    @+others
    #@+node:ekr.20041005105605.7:Birth & init
    #@+node:ekr.20041005105605.8:atFile.__init__ & initIvars
    def __init__(self,c):

        # Note: Pychecker complains if we assign to at.x instead of self.x.

        # **Warning**: all these ivars must **also** be inited in initCommonIvars.
        self.c = c
        self.debug = False
        self.fileCommands = c.fileCommands
        self.testing = False # True: enable additional checks.
        self.errors = 0 # Make sure at.error() works even when not inited.
        # New in Leo 4.4a5: For createThinChild4 (LeoUser).
        self._forcedGnxPositionList = []
            # Must be here, putting it in initReadIvars doesn't work.

        #@    << define the dispatch dictionary used by scanText4 >>
        #@+node:ekr.20041005105605.9:<< define the dispatch dictionary used by scanText4 >>
        self.dispatch_dict = {
            # Plain line.
            self.noSentinel: self.readNormalLine,
            # Starting sentinels...
            self.startAll:    self.readStartAll,
            self.startAt:     self.readStartAt,
            self.startDoc:    self.readStartDoc,
            self.startLeo:    self.readStartLeo,
            self.startMiddle: self.readStartMiddle,
            self.startNode:   self.readStartNode,
            self.startOthers: self.readStartOthers,
            # Ending sentinels...
            self.endAll:    self.readEndAll,
            self.endAt:     self.readEndAt,
            self.endDoc:    self.readEndDoc,
            self.endLeo:    self.readEndLeo,
            self.endMiddle: self.readEndMiddle,
            self.endNode:   self.readEndNode,
            self.endOthers: self.readEndOthers,
            # Non-paired sentinels.
            self.startAfterRef:  self.readAfterRef,
            self.startClone:     self.readClone,
            self.startComment:   self.readComment,
            self.startDelims:    self.readDelims,
            self.startDirective: self.readDirective,
            self.startNl:        self.readNl,
            self.startNonl:      self.readNonl,
            self.startRef:       self.readRef,
            self.startVerbatim:  self.readVerbatim,
            # Ignored 3.x sentinels
            self.endBody:               self.ignoreOldSentinel,
            self.startBody:             self.ignoreOldSentinel,
            self.startVerbatimAfterRef: self.ignoreOldSentinel }
        #@-node:ekr.20041005105605.9:<< define the dispatch dictionary used by scanText4 >>
        #@nl
    #@-node:ekr.20041005105605.8:atFile.__init__ & initIvars
    #@+node:ekr.20041005105605.10:initCommonIvars
    def initCommonIvars (self):

        """Init ivars common to both reading and writing.

        The defaults set here may be changed later."""

        # Note: Pychecker complains if about module attributes if we assign at.x instead of self.x.

        c = self.c

        if self.testing:
            # Save "permanent" ivars
            fileCommands = self.fileCommands
            dispatch_dict = self.dispatch_dict
            _forcedGnxPositionList = self._forcedGnxPositionList
            # Clear all ivars.
            g.clearAllIvars(self)
            # Restore permanent ivars
            self.testing = True
            self.c = c
            self.fileCommands = fileCommands
            self.dispatch_dict = dispatch_dict
            self._forcedGnxPositionList = _forcedGnxPositionList

        #@    << set defaults for arguments and options >>
        #@+node:ekr.20041005105605.11:<< set defaults for arguments and options >>
        # These may be changed in initReadIvars or initWriteIvars.

        # Support of output_newline option.
        self.output_newline = g.getOutputNewline(c=c)

        # Set by scanHeader when reading and scanAllDirectives when writing.
        self.at_auto_encoding = c.config.default_at_auto_file_encoding
        self.encoding = c.config.default_derived_file_encoding
        self.endSentinelComment = ""
        self.startSentinelComment = ""

        # Set by scanAllDirectives when writing.
        self.default_directory = None
        self.page_width = None
        self.tab_width  = None
        self.startSentinelComment = ""
        self.endSentinelComment = ""
        self.language = None
        #@-node:ekr.20041005105605.11:<< set defaults for arguments and options >>
        #@nl
        #@    << init common ivars >>
        #@+node:ekr.20041005105605.12:<< init common ivars >>
        # These may be set by initReadIvars or initWriteIvars.

        self.errors = 0
        self.inCode = True
        self.indent = 0  # The unit of indentation is spaces, not tabs.
        self.pending = []
        self.raw = False # True: in @raw mode
        self.root = None # The root of tree being read or written.
        self.root_seen = False # True: root vnode has been handled in this file.
        self.toString = False # True: sring-oriented read or write.
        #@-node:ekr.20041005105605.12:<< init common ivars >>
        #@nl
    #@-node:ekr.20041005105605.10:initCommonIvars
    #@+node:ekr.20041005105605.13:initReadIvars
    def initReadIvars(self,root,fileName,
        importFileName=None,
        perfectImportRoot=None,
        thinFile=False):

        importing = importFileName is not None

        self.initCommonIvars()

        #@    << init ivars for reading >>
        #@+node:ekr.20041005105605.14:<< init ivars for reading >>
        self.cloneSibCount = 0 # n > 1: Make sure n cloned sibs exists at next @+node sentinel
        self.correctedLines = 0
        self.docOut = [] # The doc part being accumulated.
        self.done = False # True when @-leo seen.
        self.endSentinelStack = []
        self.importing = False
        self.importRootSeen = False
        self.indentStack = []
        self.inputFile = None
        self.lastLines = [] # The lines after @-leo
        self.lastThinNode = None # Used by createThinChild4.
        self.leadingWs = ""
        self.lineNumber = 0 # New in Leo 4.4.8.
        self.out = None
        self.outStack = []
        self.rootSeen = False
        self.tnodeList = []
        self.tnodeListIndex = 0
        self.t = None
        self.tStack = []
        self.thinNodeStack = [] # Used by createThinChild4.
        self.updateWarningGiven = False
        #@-node:ekr.20041005105605.14:<< init ivars for reading >>
        #@nl

        self.scanDefaultDirectory(root,importing=importing)
        if self.errors: return

        # Init state from arguments.
        self.perfectImportRoot = perfectImportRoot
        self.importing = importing
        self.root = root
        self.targetFileName = fileName
        self.thinFile = thinFile
    #@-node:ekr.20041005105605.13:initReadIvars
    #@+node:ekr.20041005105605.15:initWriteIvars
    def initWriteIvars(self,root,targetFileName,
        nosentinels=False,
        thinFile=False,
        scriptWrite=False,
        toString=False,
        forcePythonSentinels=None,
        write_strips_blank_lines=None,
    ):

        self.initCommonIvars()
        #@    << init ivars for writing >>
        #@+node:ekr.20041005105605.16:<< init ivars for writing >>>
        #@+at
        # When tangling, we first write to a temporary output file. After 
        # tangling is
        # temporary file. Otherwise we delete the old target file and rename 
        # the temporary
        # file to be the target file.
        #@-at
        #@@c

        self.docKind = None
        self.explicitLineEnding = False # True: an @lineending directive specifies the ending.
        self.fileChangedFlag = False # True: the file has actually been updated.
        self.shortFileName = "" # short version of file name used for messages.
        self.thinFile = False
        self.force_newlines_in_at_nosent_bodies = self.c.config.getBool('force_newlines_in_at_nosent_bodies')

        if toString:
            self.outputFile = g.fileLikeObject()
            self.stringOutput = ""
            self.targetFileName = self.outputFileName = "<string-file>"
        else:
            self.outputFile = None # The temporary output file.
            self.stringOutput = None
            self.targetFileName = self.outputFileName = u""
        #@-node:ekr.20041005105605.16:<< init ivars for writing >>>
        #@nl

        if write_strips_blank_lines is None:
            self.write_strips_blank_lines = self.c.config.getBool('write_strips_blank_lines')
        else:
            self.write_strips_blank_lines = write_strips_blank_lines

        if forcePythonSentinels is None:
            forcePythonSentinels = scriptWrite

        if root:
            self.scanAllDirectives(root,
                scripting=scriptWrite,
                forcePythonSentinels=forcePythonSentinels)

        # g.trace(forcePythonSentinels,self.startSentinelComment,self.endSentinelComment)

        if forcePythonSentinels:
            # Force Python comment delims for g.getScript.
            self.startSentinelComment = "#"
            self.endSentinelComment = None

        # Init state from arguments.
        self.targetFileName = targetFileName
        self.sentinels = not nosentinels
        self.thinFile = thinFile
        self.toString = toString
        self.root = root

        # Ignore config settings for unit testing.
        if toString and g.app.unitTesting: self.output_newline = '\n'

        # Init all other ivars even if there is an error.
        if not self.errors and self.root:
            self.root.v.t.tnodeList = []
            self.root.v.t._p_changed = True
    #@-node:ekr.20041005105605.15:initWriteIvars
    #@-node:ekr.20041005105605.7:Birth & init
    #@+node:ekr.20041005105605.17:Reading...
    #@+node:ekr.20041005105605.18:Reading (top level)
    #@+at
    # 
    # All reading happens in the readOpenFile logic, so plugins should need to
    # override only this method.
    #@-at
    #@+node:ekr.20070919133659:checkDerivedFile (atFile)
    def checkDerivedFile (self, event=None):  # based on atFile.read

        at = self ; c = at.c ; p = c.currentPosition() ; s = p.bodyString()

        # Create a dummy vnode as the root.
        fileName='check-derived-file'
        root_t = leoNodes.tnode()
        root_v = leoNodes.vnode(root_t)
        root = leoNodes.position(root_v)
        theFile = g.fileLikeObject(fromString=s)
        thinFile = at.scanHeaderForThin (theFile,fileName)
        # g.trace('thinFile',thinFile)
        at.initReadIvars(root,fileName,thinFile=thinFile)
        if at.errors: return
        at.openFileForReading(fileName,fromString=s)
        if not at.inputFile: return
        at.readOpenFile(root,at.inputFile,fileName)
        at.inputFile.close()
        if at.errors == 0:
            g.es_print('check-derived-file passed',color='blue')
    #@-node:ekr.20070919133659:checkDerivedFile (atFile)
    #@+node:ekr.20041005105605.19:openFileForReading (atFile)
    def openFileForReading(self,fileName,fromString=False):

        at = self

        if fromString:
            at.inputFile = g.fileLikeObject(fromString=fromString)
        else:
            fn = g.os_path_join(at.default_directory,fileName)
            fn = g.os_path_normpath(fn)
            try:
                # Open the file in binary mode to allow 0x1a in bodies & headlines.
                at.inputFile = self.openForRead(fn,'rb') #bwm
                #@            << warn on read-only file >>
                #@+node:ekr.20041005105605.20:<< warn on read-only file >>
                # os.access() may not exist on all platforms.
                try:
                    read_only = not os.access(fn,os.W_OK)
                except AttributeError:
                    read_only = False 

                if read_only:
                    g.es("read only:",fn,color="red")
                #@-node:ekr.20041005105605.20:<< warn on read-only file >>
                #@nl
            except IOError:
                at.error("can not open: '@file %s'" % (fn))
                at.inputFile = None
    #@-node:ekr.20041005105605.19:openFileForReading (atFile)
    #@+node:bwmulder.20041231170726:openForRead
    def openForRead(self, *args, **kw):
        """
        Hook for the mod_shadow plugin.
        """
        return open(*args, **kw)
    #@-node:bwmulder.20041231170726:openForRead
    #@+node:bwmulder.20050101094804:openForWrite
    def openForWrite(self, *args, **kw):
        """
        Hook for the mod_shadow plugin
        """
        return open(*args, **kw)
    #@-node:bwmulder.20050101094804:openForWrite
    #@+node:ekr.20041005105605.21:read
    # The caller must enclose this code in beginUpdate/endUpdate.
    # Reads @thin, @file and @noref trees.

    def read(self,root,importFileName=None,thinFile=False,fromString=None):

        """Read any derived file."""

        at = self ; c = at.c
        if 0:
            p = c.currentPosition()
            g.trace('1',p,p.v._parent,p.v._parent and p.v._parent.t.vnodeList)
        #@    << set fileName >>
        #@+node:ekr.20041005105605.22:<< set fileName >>
        if fromString:
            fileName = "<string-file>"
        elif importFileName:
            fileName = importFileName
        elif root.isAnyAtFileNode():
            fileName = root.anyAtFileNodeName()
        else:
            fileName = None

        if not fileName:
            at.error("Missing file name.  Restoring @file tree from .leo file.")
            return False
        #@-node:ekr.20041005105605.22:<< set fileName >>
        #@nl
        at.initReadIvars(root,fileName,importFileName=importFileName,thinFile=thinFile)
        if at.errors: return False
        at.openFileForReading(fileName,fromString=fromString)
        if not at.inputFile: return False
        if not g.unitTesting:
            g.es("reading:",root.headString())
        root.clearVisitedInTree()
        at.scanAllDirectives(root,importing=at.importing,reading=True)
        at.readOpenFile(root,at.inputFile,fileName)
        if 0:
            p = c.currentPosition()
            g.trace('2',p,p.v._parent,p.v._parent and p.v._parent.t.vnodeList)
        at.inputFile.close()
        root.clearDirty() # May be set dirty below.
        if at.errors == 0:
            #@        << advise user to delete all unvisited nodes >>
            #@+node:ekr.20071105164407:<< advise user to delete all unvisited nodes >>
            resurrected = 0
            for p in root.self_and_subtree_iter():

                if not p.v.t.isVisited():
                    g.es('resurrected node:',p.headString(),color='blue')
                    g.es('in file:',fileName,color='blue')
                    resurrected += 1

            if resurrected:
                g.es('you may want to delete ressurected nodes')

            #@-node:ekr.20071105164407:<< advise user to delete all unvisited nodes >>
            #@nl
        if at.errors == 0 and not at.importing:
            # Package this as a method for use by mod_labels plugin.
            self.copyAllTempBodyStringsToTnodes(root,thinFile)

        #@    << delete all tempBodyStrings >>
        #@+node:ekr.20041005105605.25:<< delete all tempBodyStrings >>
        for p in c.allNodes_iter():

            if hasattr(p.v.t,"tempBodyString"):
                delattr(p.v.t,"tempBodyString")
        #@-node:ekr.20041005105605.25:<< delete all tempBodyStrings >>
        #@nl
        return at.errors == 0
    #@-node:ekr.20041005105605.21:read
    #@+node:ekr.20041005105605.26:readAll (atFile)
    def readAll(self,root,partialFlag=False,forceGnx=False):

        """Scan vnodes, looking for @file nodes to read."""

        at = self ; c = at.c
        if partialFlag:
            # Capture the current headline only if we aren't doing the initial read.
            c.endEditing() 
        anyRead = False
        p = root.copy()
        if partialFlag: after = p.nodeAfterTree()
        else: after = c.nullPosition()
        while p and not p.equal(after): # Don't use iterator.
            # g.trace(p.headString())
            if p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            elif p.isAtThinFileNode():
                anyRead = True
                if forceGnx: # New in Leo 4.4.2 b1: support for sax read.
                    at.forceGnxOnPosition(p)
                at.read(p,thinFile=True)
                p.moveToNodeAfterTree()
            elif p.isAtAutoNode():
                # g.trace('@auto',p.headString(),'name',p.atAutoNodeName())
                fileName = p.atAutoNodeName()
                at.readOneAtAutoNode (fileName,p)
                p.moveToNodeAfterTree()
            elif p.isAtFileNode() or p.isAtNorefFileNode():
                anyRead = True
                wasOrphan = p.isOrphan()
                ok = at.read(p)
                if wasOrphan and not partialFlag and not ok:
                    # Remind the user to fix the problem.
                    p.setDirty()
                    c.setChanged(True)
                p.moveToNodeAfterTree()
            else: p.moveToThreadNext()
        # Clear all orphan bits.
        for p in c.allNodes_iter():
            p.v.clearOrphan()

        if partialFlag and not anyRead:
            g.es("no @file nodes in the selected tree")
    #@-node:ekr.20041005105605.26:readAll (atFile)
    #@+node:ekr.20070909100252:readOneAtAutoNode (atFile)
    def readOneAtAutoNode (self,fileName,p):

        at = self ; c = at.c ; ic = c.importCommands

        oldChanged = c.isChanged()
        at.scanDefaultDirectory(p,importing=True) # Set default_directory
        fileName = g.os_path_join(at.default_directory,fileName)
        # g.trace(fileName)

        if not g.unitTesting:
            g.es("reading:",p.headString())

        # Delete all children.
        c.beginUpdate()
        try:
            while p.hasChildren():
                p.firstChild().doDelete()
        finally:
            c.endUpdate(False)

        ic.createOutline(fileName,parent=p.copy(),atAuto=True)

        if ic.errors:
            g.es_print('errors inhibited read @auto',fileName,color='red')

        if ic.errors or not g.os_path_exists(fileName):
            #c.setBodyString(p,'')
            p.clearDirty()
            c.setChanged(oldChanged)
    #@-node:ekr.20070909100252:readOneAtAutoNode (atFile)
    #@+node:ekr.20041005105605.27:readOpenFile
    def readOpenFile(self,root,theFile,fileName):

        """Read an open derived file, either 3.x or 4.x."""

        at = self

        firstLines,read_new,junk = at.scanHeader(theFile,fileName)

        if read_new:
            lastLines = at.scanText4(theFile,fileName,root)
        else:
            lastLines = at.scanText3(theFile,root,[],at.endLeo)

        if root:
            root.v.t.setVisited() # Disable warning about set nodes.

        #@    << handle first and last lines >>
        #@+node:ekr.20041005105605.28:<< handle first and last lines >>
        try:
            body = root.v.t.tempBodyString
        except Exception:
            body = ""

        lines = body.split('\n')
        at.completeFirstDirectives(lines,firstLines)
        at.completeLastDirectives(lines,lastLines)
        s = '\n'.join(lines).replace('\r', '')
        root.v.t.tempBodyString = s
        #@-node:ekr.20041005105605.28:<< handle first and last lines >>
        #@nl
    #@-node:ekr.20041005105605.27:readOpenFile
    #@+node:ekr.20050103163224:scanHeaderForThin
    def scanHeaderForThin (self,theFile,fileName):

        '''Scan the header of a derived file and return True if it is a thin file.

        N.B. We are not interested in @first lines, so any encoding will do.'''

        at = self

        # The encoding doesn't matter.  No error messages are given.
        at.encoding = at.c.config.default_derived_file_encoding

        junk,junk,isThin = at.scanHeader(theFile,fileName)

        return isThin
    #@-node:ekr.20050103163224:scanHeaderForThin
    #@-node:ekr.20041005105605.18:Reading (top level)
    #@+node:ekr.20041005105605.29:Reading (3.x)
    #@+node:ekr.20041005105605.30:createNthChild3
    #@+at 
    #@nonl
    # Sections appear in the derived file in reference order, not tree order.  
    # Therefore, when we insert the nth child of the parent there is no 
    # guarantee that the previous n-1 children have already been inserted. And 
    # it won't work just to insert the nth child as the last child if there 
    # aren't n-1 previous siblings.  For example, if we insert the third child 
    # followed by the second child followed by the first child the second and 
    # third children will be out of order.
    # 
    # To ensure that nodes are placed in the correct location we create 
    # "dummy" children as needed as placeholders.  In the example above, we 
    # would insert two dummy children when inserting the third child.  When 
    # inserting the other two children we replace the previously inserted 
    # dummy child with the actual children.
    # 
    # vnode child indices are zero-based.  Here we use 1-based indices.
    # 
    # With the "mirroring" scheme it is a structure error if we ever have to 
    # create dummy vnodes.  Such structure errors cause a second pass to be 
    # made, with an empty root.  This second pass will generate other 
    # structure errors, which are ignored.
    #@-at
    #@@c
    def createNthChild3(self,n,parent,headline):

        """Create the nth child of the parent."""

        at = self
        assert(n > 0)

        if at.importing:
            return at.createImportedNode(at.root,headline)

        # Create any needed dummy children.
        dummies = n - parent.numberOfChildren() - 1
        if dummies > 0:
            if 0: # CVS produces to many errors for this to be useful.
                g.es("dummy created")
            at.errors += 1
        while dummies > 0:
            dummies -= 1
            dummy = parent.insertAsLastChild(leoNodes.tnode())
            # The user should never see this headline.
            dummy.initHeadString("Dummy")

        if n <= parent.numberOfChildren():
            #@        << check the headlines >>
            #@+node:ekr.20041005105605.31:<< check the headlines >>
            # 1/24/03: A kludgy fix to the problem of headlines containing comment delims.

            result = parent.nthChild(n-1)
            resulthead = result.headString()

            if headline.strip() != resulthead.strip():
                start = at.startSentinelComment
                end = at.endSentinelComment
                if end and len(end) > 0:
                    # 1/25/03: The kludgy fix.
                    # Compare the headlines without the delims.
                    h1 =   headline.replace(start,"").replace(end,"")
                    h2 = resulthead.replace(start,"").replace(end,"")
                    if h1.strip() == h2.strip():
                        # 1/25/03: Another kludge: use the headline from the outline, not the derived file.
                        headline = resulthead
                    else:
                        at.errors += 1
                else:
                    at.errors += 1
            #@-node:ekr.20041005105605.31:<< check the headlines >>
            #@nl
        else:
            # This is using a dummy; we should already have bumped errors.
            result = parent.insertAsLastChild(leoNodes.tnode())
        result.initHeadString(headline)

        result.setVisited() # Suppress all other errors for this node.
        result.t.setVisited() # Suppress warnings about unvisited nodes.
        return result
    #@-node:ekr.20041005105605.30:createNthChild3
    #@+node:ekr.20041005105605.32:handleLinesFollowingSentinel
    def handleLinesFollowingSentinel (self,lines,sentinel,comments = True):

        """convert lines following a sentinel to a single line"""

        at = self
        m = " following" + sentinel + " sentinel"
        start = at.startSentinelComment
        end   = at.endSentinelComment

        if len(lines) == 1: # The expected case.
            s = lines[0]
        elif len(lines) == 5:
            at.readError("potential cvs conflict" + m)
            s = lines[1]
            g.es("using",s)
        else:
            at.readError("unexpected lines" + m)
            g.es('',len(lines), "lines",m)
            s = "bad " + sentinel
            if comments: s = start + ' ' + s

        if comments:
            #@        << remove the comment delims from s >>
            #@+node:ekr.20041005105605.33:<< remove the comment delims from s >>
            # Remove the starting comment and the blank.
            # 5/1/03: The starting comment now looks like a sentinel, to warn users from changing it.
            comment = start + '@ '
            if g.match(s,0,comment):
                s = s[len(comment):]
            else:
                at.readError("expecting comment" + m)

            # Remove the trailing comment.
            if len(end) == 0:
                s = string.strip(s[:-1])
            else:
                k = s.rfind(end)
                s = string.strip(s[:k]) # works even if k == -1
            #@-node:ekr.20041005105605.33:<< remove the comment delims from s >>
            #@nl

        # Undo the cweb hack: undouble @ signs if the opening comment delim ends in '@'.
        if start[-1:] == '@':
            s = s.replace('@@','@')

        return s
    #@-node:ekr.20041005105605.32:handleLinesFollowingSentinel
    #@+node:ekr.20041005105605.34:readLinesToNextSentinel
    # We expect only a single line, and more may exist if cvs detects a conflict.
    # We accept the first line even if it looks like a sentinel.
    # 5/1/03: The starting comment now looks like a sentinel, to warn users from changing it.

    def readLinesToNextSentinel (self,theFile):

        """read lines following multiline sentinels"""

        at = self
        lines = []
        start = at.startSentinelComment + '@ '
        nextLine = at.readLine(theFile)
        while nextLine and len(nextLine) > 0:
            if len(lines) == 0:
                lines.append(nextLine)
                nextLine = at.readLine(theFile)
            else:
                # 5/1/03: looser test then calling sentinelKind3.
                s = nextLine ; i = g.skip_ws(s,0)
                if g.match(s,i,start):
                    lines.append(nextLine)
                    nextLine = at.readLine(theFile)
                else: break

        return nextLine,lines
    #@-node:ekr.20041005105605.34:readLinesToNextSentinel
    #@+node:ekr.20041005105605.35:scanDoc3
    # Scans the doc part and appends the text out.
    # s,i point to the present line on entry.

    def scanDoc3(self,theFile,s,i,out,kind):

        at = self
        endKind = g.choose(kind ==at.startDoc,at.endDoc,at.endAt)
        single = len(at.endSentinelComment) == 0
        #@    << Skip the opening sentinel >>
        #@+node:ekr.20041005105605.36:<< Skip the opening sentinel >>
        assert(g.match(s,i,g.choose(kind == at.startDoc, "+doc", "+at")))

        out.append(g.choose(kind == at.startDoc, "@doc", "@"))
        s = at.readLine(theFile)
        #@-node:ekr.20041005105605.36:<< Skip the opening sentinel >>
        #@nl
        #@    << Skip an opening block delim >>
        #@+node:ekr.20041005105605.37:<< Skip an opening block delim >>
        if not single:
            j = g.skip_ws(s,0)
            if g.match(s,j,at.startSentinelComment):
                s = at.readLine(theFile)
        #@-node:ekr.20041005105605.37:<< Skip an opening block delim >>
        #@nl
        nextLine = None ; kind = at.noSentinel
        while len(s) > 0:
            #@        << set kind, nextLine >>
            #@+node:ekr.20041005105605.38:<< set kind, nextLine >>
            #@+at 
            #@nonl
            # For non-sentinel lines we look ahead to see whether the next 
            # line is a sentinel.
            #@-at
            #@@c

            assert(nextLine==None)

            kind = at.sentinelKind3(s)

            if kind == at.noSentinel:
                j = g.skip_ws(s,0)
                blankLine = s[j] == '\n'
                nextLine = at.readLine(theFile)
                nextKind = at.sentinelKind3(nextLine)
                if blankLine and nextKind == endKind:
                    kind = endKind # stop the scan now
            #@-node:ekr.20041005105605.38:<< set kind, nextLine >>
            #@nl
            if kind == endKind: break
            #@        << Skip the leading stuff >>
            #@+node:ekr.20041005105605.39:<< Skip the leading stuff >>
            # Point i to the start of the real line.

            if single: # Skip the opening comment delim and a blank.
                i = g.skip_ws(s,0)
                if g.match(s,i,at.startSentinelComment):
                    i += len(at.startSentinelComment)
                    if g.match(s,i," "): i += 1
            else:
                i = at.skipIndent(s,0, at.indent)
            #@-node:ekr.20041005105605.39:<< Skip the leading stuff >>
            #@nl
            #@        << Append s to out >>
            #@+node:ekr.20041005105605.40:<< Append s to out >>
            # Append the line with a newline if it is real

            line = s[i:-1] # remove newline for rstrip.

            if line == line.rstrip():
                # no trailing whitespace: the newline is real.
                out.append(line + '\n')
            else:
                # trailing whitespace: the newline is not real.
                out.append(line)
            #@-node:ekr.20041005105605.40:<< Append s to out >>
            #@nl
            if nextLine:
                s = nextLine ; nextLine = None
            else: s = at.readLine(theFile)
        if kind != endKind:
            at.readError("Missing " + at.sentinelName(endKind) + " sentinel")
        #@    << Remove a closing block delim from out >>
        #@+node:ekr.20041005105605.41:<< Remove a closing block delim from out >>
        # This code will typically only be executed for HTML files.

        if not single:

            delim = at.endSentinelComment
            n = len(delim)

            # Remove delim and possible a leading newline.
            s = string.join(out,"")
            s = s.rstrip()
            if s[-n:] == delim:
                s = s[:-n]
            if s[-1] == '\n':
                s = s[:-1]

            # Rewrite out in place.
            del out[:]
            out.append(s)
        #@-node:ekr.20041005105605.41:<< Remove a closing block delim from out >>
        #@nl
    #@-node:ekr.20041005105605.35:scanDoc3
    #@+node:ekr.20041005105605.42:scanText3
    def scanText3 (self,theFile,p,out,endSentinelKind,nextLine=None):

        """Scan a 3.x derived file recursively."""

        # __pychecker__ = '--maxbranches=100 --maxlines=500'

        at = self
        lastLines = [] # The lines after @-leo
        lineIndent = 0 ; linep = 0 # Changed only for sentinels.
        self.lineNumber = 0
        while 1:
            #@        << put the next line into s >>
            #@+node:ekr.20041005105605.43:<< put the next line into s >>
            if nextLine:
                s = nextLine ; nextLine = None
            else:
                s = at.readLine(theFile)
                if len(s) == 0: break
            #@-node:ekr.20041005105605.43:<< put the next line into s >>
            #@nl
            self.lineNumber += 1
            #@        << set kind, nextKind >>
            #@+node:ekr.20041005105605.44:<< set kind, nextKind >>
            #@+at 
            #@nonl
            # For non-sentinel lines we look ahead to see whether the next 
            # line is a sentinel.  If so, the newline that ends a non-sentinel 
            # line belongs to the next sentinel.
            #@-at
            #@@c

            assert(nextLine==None)

            kind = at.sentinelKind3(s)

            if kind == at.noSentinel:
                nextLine = at.readLine(theFile)
                nextKind = at.sentinelKind3(nextLine)
            else:
                nextLine = nextKind = None

            # nextLine != None only if we have a non-sentinel line.
            # Therefore, nextLine == None whenever scanText3 returns.
            #@-node:ekr.20041005105605.44:<< set kind, nextKind >>
            #@nl
            if kind != at.noSentinel:
                #@            << set lineIndent, linep and leading_ws >>
                #@+node:ekr.20041005105605.45:<< Set lineIndent, linep and leading_ws >>
                #@+at 
                #@nonl
                # lineIndent is the total indentation on a sentinel line.  The 
                # first "self.indent" portion of that must be removed when 
                # recreating text.  leading_ws is the remainder of the leading 
                # whitespace.  linep points to the first "real" character of a 
                # line, the character following the "indent" whitespace.
                #@-at
                #@@c

                # Point linep past the first self.indent whitespace characters.
                if at.raw: # 10/15/02
                    linep =0
                else:
                    linep = at.skipIndent(s,0,at.indent)

                # Set lineIndent to the total indentation on the line.
                lineIndent = 0 ; i = 0
                while i < len(s):
                    if s[i] == '\t': lineIndent += (abs(at.tab_width) - (lineIndent % abs(at.tab_width)))
                    elif s[i] == ' ': lineIndent += 1
                    else: break
                    i += 1
                # g.trace("lineIndent,s:",lineIndent,s)

                # Set leading_ws to the additional indentation on the line.
                leading_ws = s[linep:i]
                #@-node:ekr.20041005105605.45:<< Set lineIndent, linep and leading_ws >>
                #@nl
                i = at.skipSentinelStart3(s,0)
            #@        << handle the line in s >>
            #@+node:ekr.20041005105605.46:<< handle the line in s >>
            if kind == at.noSentinel:
                #@    << append non-sentinel line >>
                #@+node:ekr.20041005105605.47:<< append non-sentinel line >>
                # We don't output the trailing newline if the next line is a sentinel.
                if at.raw: # 10/15/02
                    i = 0
                else:
                    i = at.skipIndent(s,0,at.indent)

                assert(nextLine != None)

                if nextKind == at.noSentinel:
                    line = s[i:]
                    out.append(line)
                else:
                    line = s[i:-1] # don't output the newline
                    out.append(line)
                #@-node:ekr.20041005105605.47:<< append non-sentinel line >>
                #@nl
            #@<< handle common sentinels >>
            #@+node:ekr.20041005105605.48:<< handle common sentinels >>
            elif kind in (at.endAt, at.endBody,at.endDoc,at.endLeo,at.endNode,at.endOthers):
                #@    << handle an ending sentinel >>
                #@+node:ekr.20041005105605.49:<< handle an ending sentinel >>
                # g.trace("end sentinel:", at.sentinelName(kind))

                if kind == endSentinelKind:
                    if kind == at.endLeo:
                        # Ignore everything after @-leo.
                        # Such lines were presumably written by @last.
                        while 1:
                            s = at.readLine(theFile)
                            if len(s) == 0: break
                            lastLines.append(s) # Capture all trailing lines, even if empty.
                    elif kind == at.endBody:
                        at.raw = False
                    # nextLine != None only if we have a non-sentinel line.
                    # Therefore, nextLine == None whenever scanText3 returns.
                    assert(nextLine==None)
                    return lastLines # End the call to scanText3.
                else:
                    # Tell of the structure error.
                    name = at.sentinelName(kind)
                    expect = at.sentinelName(endSentinelKind)
                    at.readError("Ignoring " + name + " sentinel.  Expecting " + expect)
                #@-node:ekr.20041005105605.49:<< handle an ending sentinel >>
                #@nl
            elif kind == at.startBody:
                #@    << scan @+body >>
                #@+node:ekr.20041005105605.50:<< scan @+body >> 3.x
                assert(g.match(s,i,"+body"))

                child_out = [] ; child = p.copy() # Do not change out or p!
                oldIndent = at.indent ; at.indent = lineIndent
                at.scanText3(theFile,child,child_out,at.endBody)

                # Set the body, removing cursed newlines.
                # This must be done here, not in the @+node logic.
                body = string.join(child_out, "")
                body = body.replace('\r', '')
                body = g.toUnicode(body,g.app.tkEncoding) # 9/28/03

                if at.importing:
                    child.t.bodyString = body
                else:
                    child.t.tempBodyString = body

                at.indent = oldIndent
                #@-node:ekr.20041005105605.50:<< scan @+body >> 3.x
                #@nl
            elif kind == at.startNode:
                #@    << scan @+node >>
                #@+node:ekr.20041005105605.51:<< scan @+node >>
                assert(g.match(s,i,"+node:"))
                i += 6

                childIndex = 0 ; cloneIndex = 0
                #@<< Set childIndex >>
                #@+node:ekr.20041005105605.52:<< Set childIndex >>
                i = g.skip_ws(s,i) ; j = i
                while i < len(s) and s[i].isdigit():
                    i += 1

                if j == i:
                    at.readError("Implicit child index in @+node")
                    childIndex = 0
                else:
                    childIndex = int(s[j:i])

                if g.match(s,i,':'):
                    i += 1 # Skip the ":".
                else:
                    at.readError("Bad child index in @+node")
                #@-node:ekr.20041005105605.52:<< Set childIndex >>
                #@nl
                #@<< Set cloneIndex >>
                #@+node:ekr.20041005105605.53:<< Set cloneIndex >>
                while i < len(s) and s[i] != ':' and not g.is_nl(s,i):
                    if g.match(s,i,"C="):
                        # set cloneIndex from the C=nnn, field
                        i += 2 ; j = i
                        while i < len(s) and s[i].isdigit():
                            i += 1
                        if j < i:
                            cloneIndex = int(s[j:i])
                    else: i += 1 # Ignore unknown status bits.

                if g.match(s,i,":"):
                    i += 1
                else:
                    at.readError("Bad attribute field in @+node")
                #@-node:ekr.20041005105605.53:<< Set cloneIndex >>
                #@nl
                headline = ""
                #@<< Set headline and ref >>
                #@+node:ekr.20041005105605.54:<< Set headline and ref >>
                # Set headline to the rest of the line.
                # 6/22/03: don't strip leading whitespace.
                if len(at.endSentinelComment) == 0:
                    headline = s[i:-1].rstrip()
                else:
                    # 10/24/02: search from the right, not the left.
                    k = s.rfind(at.endSentinelComment,i)
                    headline = s[i:k].rstrip() # works if k == -1

                # 10/23/02: The cweb hack: undouble @ signs if the opening comment delim ends in '@'.
                if at.startSentinelComment[-1:] == '@':
                    headline = headline.replace('@@','@')

                # Set reference if it exists.
                i = g.skip_ws(s,i)
                #@nonl
                #@-node:ekr.20041005105605.54:<< Set headline and ref >>
                #@nl

                # print childIndex,headline

                if childIndex == 0: # The root node.
                    if not at.importing:
                        #@        << Check the filename in the sentinel >>
                        #@+node:ekr.20041005105605.55:<< Check the filename in the sentinel >>
                        h = headline.strip()

                        if h[:5] == "@file":
                            i,junk,junk = g.scanAtFileOptions(h)
                            fileName = string.strip(h[i:])
                            if fileName != at.targetFileName:
                                at.readError("File name in @node sentinel does not match file's name")
                        elif h[:8] == "@rawfile":
                            fileName = string.strip(h[8:])
                            if fileName != at.targetFileName:
                                at.readError("File name in @node sentinel does not match file's name")
                        else:
                            at.readError("Missing @file in root @node sentinel")
                        #@-node:ekr.20041005105605.55:<< Check the filename in the sentinel >>
                        #@nl
                    # Put the text of the root node in the current node.
                    at.scanText3(theFile,p,out,at.endNode)
                    p.v.t.setCloneIndex(cloneIndex)
                    # if cloneIndex > 0: g.trace("clone index:",cloneIndex,p)
                else:
                    # NB: this call to createNthChild3 is the bottleneck!
                    child = at.createNthChild3(childIndex,p,headline)
                    child.t.setCloneIndex(cloneIndex)
                    # if cloneIndex > 0: g.trace("cloneIndex,child:"cloneIndex,child)
                    at.scanText3(theFile,child,out,at.endNode)

                #@<< look for sentinels that may follow a reference >>
                #@+node:ekr.20041005105605.56:<< look for sentinels that may follow a reference >>
                s = at.readLine(theFile)
                kind = at.sentinelKind3(s)

                if len(s) > 1 and kind == at.startVerbatimAfterRef:
                    s = at.readLine(theFile)
                    # g.trace("verbatim:",repr(s))
                    out.append(s)
                elif len(s) > 1 and at.sentinelKind3(s) == at.noSentinel:
                    out.append(s)
                else:
                    nextLine = s # Handle the sentinel or blank line later.
                #@-node:ekr.20041005105605.56:<< look for sentinels that may follow a reference >>
                #@nl
                #@-node:ekr.20041005105605.51:<< scan @+node >>
                #@nl
            elif kind == at.startRef:
                #@    << scan old ref >>
                #@+node:ekr.20041005105605.57:<< scan old ref >> (3.0)
                #@+at 
                #@nonl
                # The sentinel contains an @ followed by a section name in 
                # angle brackets.  This code is different from the code for 
                # the @@ sentinel: the expansion of the reference does not 
                # include a trailing newline.
                #@-at
                #@@c

                assert(g.match(s,i,"<<"))

                if len(at.endSentinelComment) == 0:
                    line = s[i:-1] # No trailing newline
                else:
                    k = s.find(at.endSentinelComment,i)
                    line = s[i:k] # No trailing newline, whatever k is.

                # 10/30/02: undo cweb hack here
                start = at.startSentinelComment
                if start and len(start) > 0 and start[-1] == '@':
                    line = line.replace('@@','@')

                out.append(line)
                #@-node:ekr.20041005105605.57:<< scan old ref >> (3.0)
                #@nl
            elif kind == at.startAt:
                #@    << scan @+at >>
                #@+node:ekr.20041005105605.58:<< scan @+at >>
                assert(g.match(s,i,"+at"))
                at.scanDoc3(theFile,s,i,out,kind)
                #@-node:ekr.20041005105605.58:<< scan @+at >>
                #@nl
            elif kind == at.startDoc:
                #@    << scan @+doc >>
                #@+node:ekr.20041005105605.59:<< scan @+doc >>
                assert(g.match(s,i,"+doc"))
                at.scanDoc3(theFile,s,i,out,kind)
                #@-node:ekr.20041005105605.59:<< scan @+doc >>
                #@nl
            elif kind == at.startOthers:
                #@    << scan @+others >>
                #@+node:ekr.20041005105605.60:<< scan @+others >>
                assert(g.match(s,i,"+others"))

                # Make sure that the generated at-others is properly indented.
                out.append(leading_ws + "@others")

                at.scanText3(theFile,p,out,at.endOthers)
                #@-node:ekr.20041005105605.60:<< scan @+others >>
                #@nl
            #@-node:ekr.20041005105605.48:<< handle common sentinels >>
            #@nl
            #@<< handle rare sentinels >>
            #@+node:ekr.20041005105605.61:<< handle rare sentinels >>
            elif kind == at.startComment:
                #@    << scan @comment >>
                #@+node:ekr.20041005105605.62:<< scan @comment >>
                assert(g.match(s,i,"comment"))

                # We need do nothing more to ignore the comment line!
                #@-node:ekr.20041005105605.62:<< scan @comment >>
                #@nl
            elif kind == at.startDelims:
                #@    << scan @delims >>
                #@+node:ekr.20041005105605.63:<< scan @delims >>
                assert(g.match(s,i-1,"@delims"))

                # Skip the keyword and whitespace.
                i0 = i-1
                i = g.skip_ws(s,i-1+7)

                # Get the first delim.
                j = i
                while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
                    i += 1

                if j < i:
                    at.startSentinelComment = s[j:i]
                    # print "delim1:", at.startSentinelComment

                    # Get the optional second delim.
                    j = i = g.skip_ws(s,i)
                    while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
                        i += 1
                    end = g.choose(j<i,s[j:i],"")
                    i2 = g.skip_ws(s,i)
                    if end == at.endSentinelComment and (i2 >= len(s) or g.is_nl(s,i2)):
                        at.endSentinelComment = "" # Not really two params.
                        line = s[i0:j]
                        line = line.rstrip()
                        out.append(line+'\n')
                    else:
                        at.endSentinelComment = end
                        # print "delim2:",end
                        line = s[i0:i]
                        line = line.rstrip()
                        out.append(line+'\n')
                else:
                    at.readError("Bad @delims")
                    # Append the bad @delims line to the body text.
                    out.append("@delims")
                #@-node:ekr.20041005105605.63:<< scan @delims >>
                #@nl
            elif kind == at.startDirective:
                #@    << scan @@ >>
                #@+node:ekr.20041005105605.64:<< scan @@ >>
                # The first '@' has already been eaten.
                assert(g.match(s,i,"@"))

                if g.match_word(s,i,"@raw"):
                    at.raw = True
                elif g.match_word(s,i,"@end_raw"):
                    at.raw = False

                e = at.endSentinelComment
                s2 = s[i:]
                if len(e) > 0:
                    k = s.rfind(e,i)
                    if k != -1:
                        s2 = s[i:k] + '\n'

                start = at.startSentinelComment
                if start and len(start) > 0 and start[-1] == '@':
                    s2 = s2.replace('@@','@')
                out.append(s2)
                # g.trace(s2)
                #@-node:ekr.20041005105605.64:<< scan @@ >>
                #@nl
            elif kind == at.startLeo:
                #@    << scan @+leo >>
                #@+node:ekr.20041005105605.65:<< scan @+leo >>
                assert(g.match(s,i,"+leo"))
                at.readError("Ignoring unexpected @+leo sentinel")
                #@-node:ekr.20041005105605.65:<< scan @+leo >>
                #@nl
            elif kind == at.startVerbatim:
                #@    << scan @verbatim >>
                #@+node:ekr.20041005105605.66:<< scan @verbatim >>
                assert(g.match(s,i,"verbatim"))

                # Skip the sentinel.
                s = at.readLine(theFile) 

                # Append the next line to the text.
                i = at.skipIndent(s,0,at.indent)
                out.append(s[i:])
                #@-node:ekr.20041005105605.66:<< scan @verbatim >>
                #@nl
            #@-node:ekr.20041005105605.61:<< handle rare sentinels >>
            #@nl
            else:
                #@    << warn about unknown sentinel >>
                #@+node:ekr.20041005105605.67:<< warn about unknown sentinel >>
                j = i
                i = g.skip_line(s,i)
                line = s[j:i]
                at.readError("Unknown sentinel: " + line)
                #@-node:ekr.20041005105605.67:<< warn about unknown sentinel >>
                #@nl
            #@-node:ekr.20041005105605.46:<< handle the line in s >>
            #@nl
        #@    << handle unexpected end of text >>
        #@+node:ekr.20041005105605.68:<< handle unexpected end of text >>
        # Issue the error.
        name = at.sentinelName(endSentinelKind)
        at.readError("Unexpected end of file. Expecting " + name + "sentinel" )
        #@-node:ekr.20041005105605.68:<< handle unexpected end of text >>
        #@nl
        assert(len(s)==0 and nextLine==None) # We get here only if readline fails.
        return lastLines # We get here only if there are problems.
    #@-node:ekr.20041005105605.42:scanText3
    #@+node:ekr.20041005105605.69:sentinelKind3
    def sentinelKind3(self,s):

        """This method tells what kind of sentinel appears in line s.

        Typically s will be an empty line before the actual sentinel,
        but it is also valid for s to be an actual sentinel line.

        Returns (kind, s, emptyFlag), where emptyFlag is True if
        kind == at.noSentinel and s was an empty line on entry."""

        at = self
        i = g.skip_ws(s,0)
        if g.match(s,i,at.startSentinelComment):
            i += len(at.startSentinelComment)
        else:
            return at.noSentinel

        # 10/30/02: locally undo cweb hack here
        start = at.startSentinelComment
        if start and len(start) > 0 and start[-1] == '@':
            s = s[:i] + string.replace(s[i:],'@@','@')

        # Do not skip whitespace here!
        if g.match(s,i,"@<<"): return at.startRef
        if g.match(s,i,"@@"):   return at.startDirective
        if not g.match(s,i,'@'): return at.noSentinel
        j = i # start of lookup
        i += 1 # skip the at sign.
        if g.match(s,i,'+') or g.match(s,i,'-'):
            i += 1
        i = g.skip_c_id(s,i)
        key = s[j:i]
        if len(key) > 0 and at.sentinelDict.has_key(key):
            # g.trace("found:",key)
            return at.sentinelDict[key]
        else:
            # g.trace("not found:",key)
            return at.noSentinel
    #@-node:ekr.20041005105605.69:sentinelKind3
    #@+node:ekr.20041005105605.70:skipSentinelStart3
    def skipSentinelStart3(self,s,i):

        """Skip the start of a sentinel."""

        at = self
        start = at.startSentinelComment
        assert(start and len(start)>0)

        if g.is_nl(s,i): i = g.skip_nl(s,i)

        i = g.skip_ws(s,i)
        assert(g.match(s,i,start))
        i += len(start)

        # 7/8/02: Support for REM hack
        i = g.skip_ws(s,i)
        assert(i < len(s) and s[i] == '@')
        return i + 1
    #@-node:ekr.20041005105605.70:skipSentinelStart3
    #@-node:ekr.20041005105605.29:Reading (3.x)
    #@+node:ekr.20041005105605.71:Reading (4.x)
    #@+node:ekr.20041005105605.72:createThinChild4
    def createThinChild4 (self,gnxString,headline):

        """Find or create a new *vnode* whose parent (also a vnode) is at.lastThinNode."""

        at = self ; c = at.c ; indices = g.app.nodeIndices
        last = at.lastThinNode ; lastIndex = last.t.fileIndex
        gnx = indices.scanGnx(gnxString,0)

        # New in Leo 4.4a5: Solve Read @file nodes problem (by LeoUser)
        if self._forcedGnxPositionList and last in self._forcedGnxPositionList:
            last.fileIndex = lastIndex =  gnx
            self._forcedGnxPositionList.remove(last)

        if 0:
            g.trace("last",last,last.t.fileIndex)
            g.trace("args",indices.areEqual(gnx,last.t.fileIndex),gnxString,headline)

        # See if there is already a child with the proper index.
        child = at.lastThinNode.firstChild()
        while child and not indices.areEqual(gnx,child.t.fileIndex):
            child = child.next()

        if at.cloneSibCount > 1:
            n = at.cloneSibCount ; at.cloneSibCount = 0
            if child: clonedSibs,junk = at.scanForClonedSibs(child)
            else: clonedSibs = 0
            copies = n - clonedSibs
            # g.trace(copies,headline)
        else:
            if indices.areEqual(gnx,lastIndex):
                last.t.setVisited() # Supress warning/deletion of unvisited nodes.
                return last
            if child:
                child.t.setVisited() # Supress warning/deletion of unvisited nodes.
                return child
            copies = 1 # Create exactly one copy.

        while copies > 0:
            copies -= 1
            # Create the tnode only if it does not already exist.
            tnodesDict = c.fileCommands.tnodesDict
            t = tnodesDict.get(gnxString)
            if t:
                if indices.areEqual(t.fileIndex,gnx):
                    pass
                else:
                    g.trace('can not happen: t.fileIndex: %s gnx: %s' % (t.fileIndex,gnx))
                    # g.trace('not created, should already exist',gnxString)
            else:
                t = leoNodes.tnode(bodyString=None,headString=headline)
                t.fileIndex = gnx
                tnodesDict[gnxString] = t
            parent = at.lastThinNode
            child = leoNodes.vnode(t)
            t.vnodeList.append(child)
            child.linkAsNthChild(parent,parent.numberOfChildren())
            # g.trace('creating last child %s\nof parent%s\n' % (child,parent))

        child.t.setVisited() # Supress warning/deletion of unvisited nodes.
        return child
    #@-node:ekr.20041005105605.72:createThinChild4
    #@+node:ekr.20041005105605.73:findChild4
    def findChild4 (self,headline):

        """Return the next tnode in at.root.t.tnodeList."""

        # __pychecker__ = '--no-argsused' # headline might be used for debugging.

        # Note: tnodeLists are used _only_ when reading @file (not @thin) nodes.
        # tnodeLists compensate (a hack) for not having gnx's in derived files! 

        at = self ; v = at.root.v

        if not hasattr(v.t,"tnodeList"):
            at.readError("no tnodeList for " + repr(v))
            g.es("write the @file node or use the Import Derived File command")
            g.trace("no tnodeList for ",v)
            return None

        if at.tnodeListIndex >= len(v.t.tnodeList):
            at.readError("bad tnodeList index: %d, %s" % (at.tnodeListIndex,repr(v)))
            g.trace("bad tnodeList index",at.tnodeListIndex,len(v.t.tnodeList),v)
            return None

        t = v.t.tnodeList[at.tnodeListIndex]
        assert(t)
        at.tnodeListIndex += 1

        # Get any vnode joined to t.
        try:
            v = t.vnodeList[0]
        except Exception:
            at.readError("No vnodeList for tnode: %s" % repr(t))
            g.trace(at.tnodeListIndex)
            return None

        # Don't check the headline.  It simply causes problems.
        t.setVisited() # Supress warning/deletion of unvisited nodes.
        return t
    #@-node:ekr.20041005105605.73:findChild4
    #@+node:ekr.20041005105605.74:scanText4 & allies
    def scanText4 (self,theFile,fileName,p,verbose=False):

        """Scan a 4.x derived file non-recursively."""

        # __pychecker__ = '--no-argsused' # fileName,verbose might be used for debugging.

        at = self
        #@    << init ivars for scanText4 >>
        #@+node:ekr.20041005105605.75:<< init ivars for scanText4 >>
        # Unstacked ivars...
        at.cloneSibCount = 0
        at.done = False
        at.inCode = True
        at.indent = 0 # Changed only for sentinels.
        at.lastLines = [] # The lines after @-leo
        at.leadingWs = ""
        at.lineNumber = 0
        at.root = p.copy() # Bug fix: 12/10/05
        at.rootSeen = False
        at.updateWarningGiven = False

        # Stacked ivars...
        at.endSentinelStack = [at.endLeo] # We have already handled the @+leo sentinel.
        at.out = [] ; at.outStack = []
        at.t = p.v.t ; at.tStack = []
        at.lastThinNode = p.v ; at.thinNodeStack = [p.v]

        if 0: # Useful for debugging.
            if hasattr(p.v.t,"tnodeList"):
                g.trace("len(tnodeList)",len(p.v.t.tnodeList),p.v)
            else:
                g.trace("no tnodeList",p.v)

        # g.trace(at.startSentinelComment)
        #@-node:ekr.20041005105605.75:<< init ivars for scanText4 >>
        #@nl
        while at.errors == 0 and not at.done:
            s = at.readLine(theFile)
            self.lineNumber += 1
            if len(s) == 0: break
            kind = at.sentinelKind4(s)
            # g.trace(at.sentinelName(kind),s.strip())
            if kind == at.noSentinel:
                i = 0
            else:
                i = at.skipSentinelStart4(s,0)
            func = at.dispatch_dict[kind]
            func(s,i)

        if at.errors == 0 and not at.done:
            #@        << report unexpected end of text >>
            #@+node:ekr.20041005105605.76:<< report unexpected end of text >>
            assert(at.endSentinelStack)

            at.readError(
                "Unexpected end of file. Expecting %s sentinel" %
                at.sentinelName(at.endSentinelStack[-1]))
            #@-node:ekr.20041005105605.76:<< report unexpected end of text >>
            #@nl

        return at.lastLines
    #@+node:ekr.20041005105605.77:readNormalLine
    def readNormalLine (self,s,i):

        at = self

        if at.inCode:
            if not at.raw:
                s = g.removeLeadingWhitespace(s,at.indent,at.tab_width)
            at.out.append(s)
        else:
            #@        << Skip the leading stuff >>
            #@+node:ekr.20041005105605.78:<< Skip the leading stuff >>
            if len(at.endSentinelComment) == 0:
                # Skip the single comment delim and a blank.
                i = g.skip_ws(s,0)
                if g.match(s,i,at.startSentinelComment):
                    i += len(at.startSentinelComment)
                    if g.match(s,i," "): i += 1
            else:
                i = at.skipIndent(s,0,at.indent)
            #@-node:ekr.20041005105605.78:<< Skip the leading stuff >>
            #@nl
            #@        << Append s to docOut >>
            #@+node:ekr.20041005105605.79:<< Append s to docOut >>
            line = s[i:-1] # remove newline for rstrip.

            if line == line.rstrip():
                # no trailing whitespace: the newline is real.
                at.docOut.append(line + '\n')
            else:
                # trailing whitespace: the newline is fake.
                at.docOut.append(line)
            #@-node:ekr.20041005105605.79:<< Append s to docOut >>
            #@nl
    #@-node:ekr.20041005105605.77:readNormalLine
    #@+node:ekr.20041005105605.80:start sentinels
    #@+node:ekr.20041005105605.81:readStartAll (4.2)
    def readStartAll (self,s,i):

        """Read an @+all sentinel."""

        at = self
        j = g.skip_ws(s,i)
        leadingWs = s[i:j]
        if leadingWs:
            assert(g.match(s,j,"@+all"))
        else:
            assert(g.match(s,j,"+all"))

        # Make sure that the generated at-all is properly indented.
        at.out.append(leadingWs + "@all\n")

        at.endSentinelStack.append(at.endAll)
    #@-node:ekr.20041005105605.81:readStartAll (4.2)
    #@+node:ekr.20041005105605.82:readStartAt & readStartDoc
    def readStartAt (self,s,i):
        """Read an @+at sentinel."""
        at = self ; assert(g.match(s,i,"+at"))
        if 0:# new code: append whatever follows the sentinel.
            i += 3 ; j = at.skipToEndSentinel(s,i) ; follow = s[i:j]
            at.out.append('@' + follow) ; at.docOut = []
        else:
            i += 3 ; j = g.skip_ws(s,i) ; ws = s[i:j]
            at.docOut = ['@' + ws + '\n'] # This newline may be removed by a following @nonl
        at.inCode = False
        at.endSentinelStack.append(at.endAt)

    def readStartDoc (self,s,i):
        """Read an @+doc sentinel."""
        at = self ; assert(g.match(s,i,"+doc"))
        if 0: # new code: append whatever follows the sentinel.
            i += 4 ; j = at.skipToEndSentinel(s,i) ; follow = s[i:j]
            at.out.append('@' + follow) ; at.docOut = []
        else:
            i += 4 ; j = g.skip_ws(s,i) ; ws = s[i:j]
            at.docOut = ["@doc" + ws + '\n'] # This newline may be removed by a following @nonl
        at.inCode = False
        at.endSentinelStack.append(at.endDoc)

    def skipToEndSentinel(self,s,i):
        at = self
        end = at.endSentinelComment
        if end:
            j = s.find(end,i)
            if j == -1:
                return g.skip_to_end_of_line(s,i)
            else:
                return j
        else:
            return g.skip_to_end_of_line(s,i)
    #@-node:ekr.20041005105605.82:readStartAt & readStartDoc
    #@+node:ekr.20041005105605.83:readStartLeo
    def readStartLeo (self,s,i):

        """Read an unexpected @+leo sentinel."""

        at = self
        assert(g.match(s,i,"+leo"))
        at.readError("Ignoring unexpected @+leo sentinel")
    #@-node:ekr.20041005105605.83:readStartLeo
    #@+node:ekr.20041005105605.84:readStartMiddle
    def readStartMiddle (self,s,i):

        """Read an @+middle sentinel."""

        at = self

        at.readStartNode(s,i,middle=True)
    #@-node:ekr.20041005105605.84:readStartMiddle
    #@+node:ekr.20041005105605.85:readStartNode (4.x)
    def readStartNode (self,s,i,middle=False):

        """Read an @+node or @+middle sentinel."""

        at = self
        if middle:
            assert(g.match(s,i,"+middle:"))
            i += 8
        else:
            assert(g.match(s,i,"+node:"))
            i += 6

        if at.thinFile:
            #@        << set gnx and bump i >>
            #@+node:ekr.20041005105605.86:<< set gnx and bump i >>
            # We have skipped past the opening colon of the gnx.
            j = s.find(':',i)
            if j == -1:
                g.trace("no closing colon",g.get_line(s,i))
                at.readError("Expecting gnx in @+node sentinel")
                return # 5/17/04
            else:
                gnx = s[i:j]
                i = j + 1 # Skip the i
            #@-node:ekr.20041005105605.86:<< set gnx and bump i >>
            #@nl
        #@    << Set headline, undoing the CWEB hack >>
        #@+node:ekr.20041005105605.87:<< Set headline, undoing the CWEB hack >>
        # Set headline to the rest of the line.
        # Don't strip leading whitespace."

        if len(at.endSentinelComment) == 0:
            headline = s[i:-1].rstrip()
        else:
            k = s.rfind(at.endSentinelComment,i)
            headline = s[i:k].rstrip() # works if k == -1

        # Undo the CWEB hack: undouble @ signs if the opening comment delim ends in '@'.
        if at.startSentinelComment[-1:] == '@':
            headline = headline.replace('@@','@')
        #@-node:ekr.20041005105605.87:<< Set headline, undoing the CWEB hack >>
        #@nl
        if not at.root_seen:
            at.root_seen = True
            #@        << Check the filename in the sentinel >>
            #@+node:ekr.20041005105605.88:<< Check the filename in the sentinel >>
            if 0: # This doesn't work so well in cooperative environments.
                if not at.importing:

                    h = headline.strip()

                    if h[:5] == "@file":
                        i,junk,junk = g.scanAtFileOptions(h)
                        fileName = string.strip(h[i:])
                        if fileName != at.targetFileName:
                            at.readError("File name in @node sentinel does not match file's name")
                    elif h[:8] == "@rawfile":
                        fileName = string.strip(h[8:])
                        if fileName != at.targetFileName:
                            at.readError("File name in @node sentinel does not match file's name")
                    else:
                        at.readError("Missing @file in root @node sentinel")
            #@-node:ekr.20041005105605.88:<< Check the filename in the sentinel >>
            #@nl

        i,newIndent = g.skip_leading_ws_with_indent(s,0,at.tab_width)
        at.indentStack.append(at.indent) ; at.indent = newIndent

        at.outStack.append(at.out) ; at.out = []
        at.tStack.append(at.t)

        if at.importing:
            p = at.createImportedNode(at.root,headline)
            at.t = p.v.t
        elif at.thinFile:
            at.thinNodeStack.append(at.lastThinNode)
            at.lastThinNode = v = at.createThinChild4(gnx,headline)
            at.t = v.t
        else:
            at.t = at.findChild4(headline)

        at.endSentinelStack.append(at.endNode)
    #@-node:ekr.20041005105605.85:readStartNode (4.x)
    #@+node:ekr.20041005105605.89:readStartOthers
    def readStartOthers (self,s,i):

        """Read an @+others sentinel."""

        at = self
        j = g.skip_ws(s,i)
        leadingWs = s[i:j]
        if leadingWs:
            assert(g.match(s,j,"@+others"))
        else:
            assert(g.match(s,j,"+others"))

        # Make sure that the generated at-others is properly indented.
        at.out.append(leadingWs + "@others\n")

        at.endSentinelStack.append(at.endOthers)
    #@-node:ekr.20041005105605.89:readStartOthers
    #@-node:ekr.20041005105605.80:start sentinels
    #@+node:ekr.20041005105605.90:end sentinels
    #@+node:ekr.20041005105605.91:readEndAll (4.2)
    def readEndAll (self,unused_s,unused_i):

        """Read an @-all sentinel."""

        # __pychecker__ = '--no-argsused' # s,i not used, but must be present.

        at = self
        at.popSentinelStack(at.endAll)
    #@-node:ekr.20041005105605.91:readEndAll (4.2)
    #@+node:ekr.20041005105605.92:readEndAt & readEndDoc
    def readEndAt (self,unused_s,unused_i):

        """Read an @-at sentinel."""

        # __pychecker__ = '--no-argsused' # s,i not used, but must be present.

        at = self
        at.readLastDocLine("@")
        at.popSentinelStack(at.endAt)
        at.inCode = True

    def readEndDoc (self,unused_s,unused_i):

        """Read an @-doc sentinel."""

        # __pychecker__ = '--no-argsused' # s,i not used, but must be present.

        at = self
        at.readLastDocLine("@doc")
        at.popSentinelStack(at.endDoc)
        at.inCode = True
    #@-node:ekr.20041005105605.92:readEndAt & readEndDoc
    #@+node:ekr.20041005105605.93:readEndLeo
    def readEndLeo (self,unused_s,unused_i):

        """Read an @-leo sentinel."""

        # __pychecker__ = '--no-argsused' # i not used, but must be present.

        at = self

        # Ignore everything after @-leo.
        # Such lines were presumably written by @last.
        while 1:
            s = at.readLine(at.inputFile)
            if len(s) == 0: break
            at.lastLines.append(s) # Capture all trailing lines, even if empty.

        at.done = True
    #@-node:ekr.20041005105605.93:readEndLeo
    #@+node:ekr.20041005105605.94:readEndMiddle
    def readEndMiddle (self,s,i):

        """Read an @-middle sentinel."""

        at = self

        at.readEndNode(s,i,middle=True)
    #@-node:ekr.20041005105605.94:readEndMiddle
    #@+node:ekr.20041005105605.95:readEndNode (4.x)
    def readEndNode (self,unused_s,unused_i,middle=False):

        """Handle end-of-node processing for @-others and @-ref sentinels."""

        # __pychecker__ = '--no-argsused' # s,i not used, but must be present.

        at = self ; c = at.c

        # End raw mode.
        at.raw = False

        # Set the temporary body text.
        s = ''.join(at.out)
        s = g.toUnicode(s,g.app.tkEncoding) # 9/28/03

        if at.importing:
            at.t.bodyString = s
        elif middle: 
            pass # Middle sentinels never alter text.
        else:
            if hasattr(at.t,"tempBodyString") and s != at.t.tempBodyString:
                old = at.t.tempBodyString
            elif at.t.hasBody() and s != at.t.getBody():
                old = at.t.getBody()
            else:
                old = None
            # 9/4/04: Suppress this warning for the root: @first complicates matters.
            if old and not g.app.unitTesting and at.t != at.root.t:
                #@            << indicate that the node has been changed >>
                #@+node:ekr.20041005105605.96:<< indicate that the node has been changed >>
                if at.perfectImportRoot:
                    #@    << bump at.correctedLines and tell about the correction >>
                    #@+node:ekr.20041005105605.97:<< bump at.correctedLines and tell about the correction >>
                    # Report the number of corrected nodes.
                    at.correctedLines += 1

                    found = False
                    for p in at.perfectImportRoot.self_and_subtree_iter():
                        if p.v.t == at.t:
                            found = True ; break

                    if found:
                        if 0: # For debugging.
                            print ; print '-' * 40
                            print "old",len(old)
                            for line in g.splitLines(old):
                                #line = line.replace(' ','< >').replace('\t','<TAB>')
                                print repr(str(line))
                            print ; print '-' * 40
                            print "new",len(s)
                            for line in g.splitLines(s):
                                #line = line.replace(' ','< >').replace('\t','<TAB>')
                                print repr(str(line))
                            print ; print '-' * 40
                    else:
                        # This should never happen.
                        g.es("correcting hidden node: t=",repr(at.t),color="red")
                    #@-node:ekr.20041005105605.97:<< bump at.correctedLines and tell about the correction >>
                    #@nl
                    # p.setMarked()
                    at.t.bodyString = s # Just setting at.t.tempBodyString won't work here.
                    at.t.setDirty() # Mark the node dirty.  Ancestors will be marked dirty later.
                    at.c.setChanged(True)
                else:
                    if 0: # New in 4.4.1 final.  This warning can be very confusing.
                        if not at.updateWarningGiven:
                            at.updateWarningGiven = True
                            # print "***",at.t,at.root.t
                            g.es("warning: updating changed text in",at.root.headString(),color="blue")
                    # Just set the dirty bit. Ancestors will be marked dirty later.
                    at.t.setDirty()
                    if 1: # We must avoid the full setChanged logic here!
                        c.changed = True
                    else: # Far too slow for mass changes.
                        at.c.setChanged(True)
                #@nonl
                #@-node:ekr.20041005105605.96:<< indicate that the node has been changed >>
                #@nl
            at.t.tempBodyString = s

        # Indicate that the tnode has been set in the derived file.
        at.t.setVisited()

        # End the previous node sentinel.
        at.indent = at.indentStack.pop()
        at.out = at.outStack.pop()
        at.t = at.tStack.pop()
        if at.thinFile and not at.importing:
            at.lastThinNode = at.thinNodeStack.pop()

        at.popSentinelStack(at.endNode)
    #@-node:ekr.20041005105605.95:readEndNode (4.x)
    #@+node:ekr.20041005105605.98:readEndOthers
    def readEndOthers (self,unused_s,unused_i):

        """Read an @-others sentinel."""

        # __pychecker__ = '--no-argsused' # s,i unused, but must be present.

        at = self
        at.popSentinelStack(at.endOthers)
    #@-node:ekr.20041005105605.98:readEndOthers
    #@+node:ekr.20041005105605.99:readLastDocLine
    def readLastDocLine (self,tag):

        """Read the @c line that terminates the doc part.
        tag is @doc or @."""

        at = self
        end = at.endSentinelComment
        start = at.startSentinelComment
        s = ''.join(at.docOut)

        # Remove the @doc or @space.  We'll add it back at the end.
        if g.match(s,0,tag):
            s = s[len(tag):]
        else:
            at.readError("Missing start of doc part")
            return

        # Bug fix: Append any whitespace following the tag to tag.
        while s and s[0] in (' ','\t'):
            tag = tag + s[0] ; s = s[1:]

        if end:
            # Remove leading newline.
            if s[0] == '\n': s = s[1:]
            # Remove opening block delim.
            if g.match(s,0,start):
                s = s[len(start):]
            else:
                at.readError("Missing open block comment")
                g.trace('tag',repr(tag),'start',repr(start),'s',repr(s))
                return
            # Remove trailing newline.
            if s[-1] == '\n': s = s[:-1]
            # Remove closing block delim.
            if s[-len(end):] == end:
                s = s[:-len(end)]
            else:
                at.readError("Missing close block comment")
                g.trace(s)
                g.trace(end)
                g.trace(start)
                return

        at.out.append(tag + s)
        at.docOut = []
    #@-node:ekr.20041005105605.99:readLastDocLine
    #@-node:ekr.20041005105605.90:end sentinels
    #@+node:ekr.20041005105605.100:Unpaired sentinels
    #@+node:ekr.20041005105605.101:ignoreOldSentinel
    def  ignoreOldSentinel (self,s,unused_i):

        """Ignore an 3.x sentinel."""

        # __pychecker__ = '--no-argsused' # i unused, but must be present.

        g.es("ignoring 3.x sentinel:",s.strip(),color="blue")
    #@-node:ekr.20041005105605.101:ignoreOldSentinel
    #@+node:ekr.20041005105605.102:readAfterRef
    def  readAfterRef (self,s,i):

        """Read an @afterref sentinel."""

        at = self
        assert(g.match(s,i,"afterref"))

        # Append the next line to the text.
        s = at.readLine(at.inputFile)
        at.out.append(s)
    #@-node:ekr.20041005105605.102:readAfterRef
    #@+node:ekr.20041005105605.103:readClone
    def readClone (self,s,i):

        at = self ; tag = "clone"

        assert(g.match(s,i,tag))

        # Skip the tag and whitespace.
        i = g.skip_ws(s,i+len(tag))

        # Get the clone count.
        junk,val = g.skip_long(s,i)

        if val == None:
            at.readError("Invalid count in @clone sentinel")
        else:
            at.cloneSibCount = val
    #@-node:ekr.20041005105605.103:readClone
    #@+node:ekr.20041005105605.104:readComment
    def readComment (self,s,i):

        """Read an @comment sentinel."""

        assert(g.match(s,i,"comment"))

        # Just ignore the comment line!
    #@-node:ekr.20041005105605.104:readComment
    #@+node:ekr.20041005105605.105:readDelims
    def readDelims (self,s,i):

        """Read an @delims sentinel."""

        at = self
        assert(g.match(s,i-1,"@delims"))

        # Skip the keyword and whitespace.
        i0 = i-1
        i = g.skip_ws(s,i-1+7)

        # Get the first delim.
        j = i
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
            i += 1

        if j < i:
            at.startSentinelComment = s[j:i]
            # print "delim1:", at.startSentinelComment

            # Get the optional second delim.
            j = i = g.skip_ws(s,i)
            while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
                i += 1
            end = g.choose(j<i,s[j:i],"")
            i2 = g.skip_ws(s,i)
            if end == at.endSentinelComment and (i2 >= len(s) or g.is_nl(s,i2)):
                at.endSentinelComment = "" # Not really two params.
                line = s[i0:j]
                line = line.rstrip()
                at.out.append(line+'\n')
            else:
                at.endSentinelComment = end
                # print "delim2:",end
                line = s[i0:i]
                line = line.rstrip()
                at.out.append(line+'\n')
        else:
            at.readError("Bad @delims")
            # Append the bad @delims line to the body text.
            at.out.append("@delims")
    #@-node:ekr.20041005105605.105:readDelims
    #@+node:ekr.20041005105605.106:readDirective (@@)
    def readDirective (self,s,i):

        """Read an @@sentinel."""

        at = self
        assert(g.match(s,i,"@")) # The first '@' has already been eaten.

        # g.trace(g.get_line(s,i))

        if g.match_word(s,i,"@raw"):
            at.raw = True
        elif g.match_word(s,i,"@end_raw"):
            at.raw = False

        e = at.endSentinelComment
        s2 = s[i:]
        if len(e) > 0:
            k = s.rfind(e,i)
            if k != -1:
                s2 = s[i:k] + '\n'

        start = at.startSentinelComment
        if start and len(start) > 0 and start[-1] == '@':
            s2 = s2.replace('@@','@')

        if 0: # New in 4.2.1: never change comment delims here...
            if g.match_word(s,i,"@language"):
                #@            << handle @language >>
                #@+node:ekr.20041005105605.107:<< handle @language >>
                # Skip the keyword and whitespace.
                i += len("@language")
                i = g.skip_ws(s,i)
                j = g.skip_c_id(s,i)
                language = s[i:j]

                delim1,delim2,delim3 = g.set_delims_from_language(language)

                g.trace(g.get_line(s,i))
                g.trace(delim1,delim2,delim3)

                # Returns a tuple (single,start,end) of comment delims
                if delim1:
                    at.startSentinelComment = delim1
                    at.endSentinelComment = "" # Must not be None.
                elif delim2 and delim3:
                    at.startSentinelComment = delim2
                    at.endSentinelComment = delim3
                else:
                    line = g.get_line(s,i)
                    g.es("ignoring bad @language sentinel:",line,color="red")
                #@-node:ekr.20041005105605.107:<< handle @language >>
                #@nl
            elif g.match_word(s,i,"@comment"):
                #@            << handle @comment >>
                #@+node:ekr.20041005105605.108:<< handle @comment >>
                j = g.skip_line(s,i)
                line = s[i:j]
                delim1,delim2,delim3 = g.set_delims_from_string(line)

                #g.trace(g.get_line(s,i))
                #g.trace(delim1,delim2,delim3)

                # Returns a tuple (single,start,end) of comment delims
                if delim1:
                    self.startSentinelComment = delim1
                    self.endSentinelComment = "" # Must not be None.
                elif delim2 and delim3:
                    self.startSentinelComment = delim2
                    self.endSentinelComment = delim3
                else:
                    line = g.get_line(s,i)
                    g.es("ignoring bad @comment sentinel:",line,color="red")
                #@-node:ekr.20041005105605.108:<< handle @comment >>
                #@nl

        at.out.append(s2)
    #@-node:ekr.20041005105605.106:readDirective (@@)
    #@+node:ekr.20041005105605.109:readNl
    def readNl (self,s,i):

        """Handle an @nonl sentinel."""

        at = self
        assert(g.match(s,i,"nl"))

        if at.inCode:
            at.out.append('\n')
        else:
            at.docOut.append('\n')
    #@-node:ekr.20041005105605.109:readNl
    #@+node:ekr.20041005105605.110:readNonl
    def readNonl (self,s,i):

        """Handle an @nonl sentinel."""

        at = self
        assert(g.match(s,i,"nonl"))

        if at.inCode:
            s = ''.join(at.out)
            if s and s[-1] == '\n':
                at.out = [s[:-1]]
            else:
                g.trace("out:",s)
                at.readError("unexpected @nonl directive in code part")
        else:
            s = ''.join(at.pending)
            if s:
                if s and s[-1] == '\n':
                    at.pending = [s[:-1]]
                else:
                    g.trace("docOut:",s)
                    at.readError("unexpected @nonl directive in pending doc part")
            else:
                s = ''.join(at.docOut)
                if s and s[-1] == '\n':
                    at.docOut = [s[:-1]]
                else:
                    g.trace("docOut:",s)
                    at.readError("unexpected @nonl directive in doc part")
    #@-node:ekr.20041005105605.110:readNonl
    #@+node:ekr.20041005105605.111:readRef
    #@+at 
    #@nonl
    # The sentinel contains an @ followed by a section name in angle 
    # brackets.  This code is different from the code for the @@ sentinel: the 
    # expansion of the reference does not include a trailing newline.
    #@-at
    #@@c

    def readRef (self,s,i):

        """Handle an @<< sentinel."""

        at = self
        j = g.skip_ws(s,i)
        assert(g.match(s,j,"<<"))

        if len(at.endSentinelComment) == 0:
            line = s[i:-1] # No trailing newline
        else:
            k = s.find(at.endSentinelComment,i)
            line = s[i:k] # No trailing newline, whatever k is.

        # Undo the cweb hack.
        start = at.startSentinelComment
        if start and len(start) > 0 and start[-1] == '@':
            line = line.replace('@@','@')

        at.out.append(line)
    #@-node:ekr.20041005105605.111:readRef
    #@+node:ekr.20041005105605.112:readVerbatim
    def readVerbatim (self,s,i):

        """Read an @verbatim sentinel."""

        at = self
        assert(g.match(s,i,"verbatim"))

        # Append the next line to the text.
        s = at.readLine(at.inputFile) 
        i = at.skipIndent(s,0,at.indent)
        at.out.append(s[i:])
    #@-node:ekr.20041005105605.112:readVerbatim
    #@-node:ekr.20041005105605.100:Unpaired sentinels
    #@+node:ekr.20041005105605.113:badEndSentinel, push/popSentinelStack
    def badEndSentinel (self,expectedKind):

        """Handle a mismatched ending sentinel."""

        at = self
        assert(at.endSentinelStack)
        s = "Ignoring %s sentinel.  Expecting %s" % (
            at.sentinelName(at.endSentinelStack[-1]),
            at.sentinelName(expectedKind))
        at.readError(s)

    def popSentinelStack (self,expectedKind):

        """Pop an entry from endSentinelStack and check it."""

        at = self
        if at.endSentinelStack and at.endSentinelStack[-1] == expectedKind:
            at.endSentinelStack.pop()
        else:
            at.badEndSentinel(expectedKind)
    #@-node:ekr.20041005105605.113:badEndSentinel, push/popSentinelStack
    #@-node:ekr.20041005105605.74:scanText4 & allies
    #@+node:ekr.20041005105605.114:sentinelKind4
    def sentinelKind4(self,s):

        """Return the kind of sentinel at s."""

        at = self

        i = g.skip_ws(s,0)
        if g.match(s,i,at.startSentinelComment): 
            i += len(at.startSentinelComment)
        else:
            return at.noSentinel

        # Locally undo cweb hack here
        start = at.startSentinelComment
        if start and len(start) > 0 and start[-1] == '@':
            s = s[:i] + string.replace(s[i:],'@@','@')

        # 4.0: Look ahead for @[ws]@others and @[ws]<<
        if g.match(s,i,"@"):
            j = g.skip_ws(s,i+1)
            if j > i+1:
                # g.trace(ws,s)
                if g.match(s,j,"@+others"):
                    return at.startOthers
                elif g.match(s,j,"<<"):
                    return at.startRef
                else:
                    # No other sentinels allow whitespace following the '@'
                    return at.noSentinel

        # Do not skip whitespace here!
        if g.match(s,i,"@<<"): return at.startRef
        if g.match(s,i,"@@"):   return at.startDirective
        if not g.match(s,i,'@'): return at.noSentinel
        j = i # start of lookup
        i += 1 # skip the at sign.
        if g.match(s,i,'+') or g.match(s,i,'-'):
            i += 1
        i = g.skip_c_id(s,i)
        key = s[j:i]
        if len(key) > 0 and at.sentinelDict.has_key(key):
            return at.sentinelDict[key]
        else:
            return at.noSentinel
    #@-node:ekr.20041005105605.114:sentinelKind4
    #@+node:ekr.20041005105605.115:skipSentinelStart4
    def skipSentinelStart4(self,s,i):

        """Skip the start of a sentinel."""

        start = self.startSentinelComment
        assert(start and len(start)>0)

        i = g.skip_ws(s,i)
        assert(g.match(s,i,start))
        i += len(start)

        # 7/8/02: Support for REM hack
        i = g.skip_ws(s,i)
        assert(i < len(s) and s[i] == '@')
        return i + 1
    #@-node:ekr.20041005105605.115:skipSentinelStart4
    #@-node:ekr.20041005105605.71:Reading (4.x)
    #@+node:ekr.20041005105605.116:Reading utils...
    #@+node:ekr.20041005105605.117:completeFirstDirectives
    # 14-SEP-2002 DTHEIN: added for use by atFile.read()

    # this function scans the lines in the list 'out' for @first directives
    # and appends the corresponding line from 'firstLines' to each @first 
    # directive found.  NOTE: the @first directives must be the very first
    # lines in 'out'.
    def completeFirstDirectives(self,out,firstLines):

        tag = "@first"
        foundAtFirstYet = 0
        outRange = range(len(out))
        j = 0
        for k in outRange:
            # skip leading whitespace lines
            if (not foundAtFirstYet) and (len(out[k].strip()) == 0): continue
            # quit if something other than @first directive
            i = 0
            if not g.match(out[k],i,tag): break
            foundAtFirstYet = 1
            # quit if no leading lines to apply
            if j >= len(firstLines): break
            # make the new @first directive
            #18-SEP-2002 DTHEIN: remove trailing newlines because they are inserted later
            # 21-SEP-2002 DTHEIN: no trailing whitespace on empty @first directive
            leadingLine = " " + firstLines[j]
            out[k] = tag + leadingLine.rstrip() ; j += 1
    #@-node:ekr.20041005105605.117:completeFirstDirectives
    #@+node:ekr.20041005105605.118:completeLastDirectives
    # 14-SEP-2002 DTHEIN: added for use by atFile.read()

    # this function scans the lines in the list 'out' for @last directives
    # and appends the corresponding line from 'lastLines' to each @last 
    # directive found.  NOTE: the @last directives must be the very last
    # lines in 'out'.
    def completeLastDirectives(self,out,lastLines):

        tag = "@last"
        foundAtLastYet = 0
        outRange = range(-1,-len(out),-1)
        j = -1
        for k in outRange:
            # skip trailing whitespace lines
            if (not foundAtLastYet) and (len(out[k].strip()) == 0): continue
            # quit if something other than @last directive
            i = 0
            if not g.match(out[k],i,tag): break
            foundAtLastYet = 1
            # quit if no trailing lines to apply
            if j < -len(lastLines): break
            # make the new @last directive
            #18-SEP-2002 DTHEIN: remove trailing newlines because they are inserted later
            # 21-SEP-2002 DTHEIN: no trailing whitespace on empty @last directive
            trailingLine = " " + lastLines[j]
            out[k] = tag + trailingLine.rstrip() ; j -= 1
    #@-node:ekr.20041005105605.118:completeLastDirectives
    #@+node:ekr.20050301105854:copyAllTempBodyStringsToTnodes
    def  copyAllTempBodyStringsToTnodes (self,root,thinFile):

        c = self.c
        for p in root.self_and_subtree_iter():
            try: s = p.v.t.tempBodyString
            except Exception: s = ""
            old_body = p.bodyString()
            if s != old_body:
                if 0: # For debugging.
                    print ; print "changed: " + p.headString()
                    print ; print "new:",s
                    print ; print "old:",p.bodyString()
                if thinFile:
                    p.v.setTnodeText(s)
                    if p.v.isDirty():
                        p.setAllAncestorAtFileNodesDirty()
                else:
                    c.setBodyString(p,s) # Sets c and p dirty.

                if not thinFile or (thinFile and p.v.isDirty()):
                    # New in Leo 4.3: support for mod_labels plugin:
                    try:
                        c.mod_label_controller.add_label(p,"before change:",old_body)
                    except Exception:
                        pass
                    g.es("changed:",p.headString(),color="blue")
                    p.setMarked()
    #@-node:ekr.20050301105854:copyAllTempBodyStringsToTnodes
    #@+node:ekr.20041005105605.119:createImportedNode
    def createImportedNode (self,root,headline):

        at = self

        if at.importRootSeen:
            p = root.insertAsLastChild()
            p.initHeadString(headline)
        else:
            # Put the text into the already-existing root node.
            p = root
            at.importRootSeen = True

        p.v.t.setVisited() # Suppress warning about unvisited node.
        return p
    #@-node:ekr.20041005105605.119:createImportedNode
    #@+node:ekr.20041005105605.120:parseLeoSentinel
    def parseLeoSentinel (self,s):

        at = self ; c = at.c
        new_df = False ; valid = True ; n = len(s)
        start = '' ; end = '' ; isThinDerivedFile = False
        encoding_tag = "-encoding="
        version_tag = "-ver="
        tag = "@+leo"
        thin_tag = "-thin"
        #@    << set the opening comment delim >>
        #@+node:ekr.20041005105605.121:<< set the opening comment delim >>
        # s contains the tag
        i = j = g.skip_ws(s,0)

        # The opening comment delim is the initial non-tag
        while i < n and not g.match(s,i,tag) and not g.is_nl(s,i):
            i += 1

        if j < i:
            start = s[j:i]
        else:
            valid = False

        #@-node:ekr.20041005105605.121:<< set the opening comment delim >>
        #@nl
        #@    << make sure we have @+leo >>
        #@+node:ekr.20041005105605.122:<< make sure we have @+leo >>
        #@+at 
        #@nonl
        # REM hack: leading whitespace is significant before the @+leo.  We do 
        # this so that sentinelKind need not skip whitespace following 
        # self.startSentinelComment.  This is correct: we want to be as 
        # restrictive as possible about what is recognized as a sentinel.  
        # This minimizes false matches.
        #@-at
        #@@c

        if 0: # Make leading whitespace significant.
            i = g.skip_ws(s,i)

        if g.match(s,i,tag):
            i += len(tag)
        else: valid = False
        #@-node:ekr.20041005105605.122:<< make sure we have @+leo >>
        #@nl
        #@    << read optional version param >>
        #@+node:ekr.20041005105605.123:<< read optional version param >>
        new_df = g.match(s,i,version_tag)

        if new_df:
            # Pre Leo 4.4.1: Skip to the next minus sign or end-of-line.
            # Leo 4.4.1 +:   Skip to next minus sign, end-of-line, or non numeric character.
            # This is required to handle trailing comment delims properly.
            i += len(version_tag)
            j = i
            while i < len(s) and (s[i] == '.' or s[i].isdigit()):
                i += 1

            if j < i:
                pass
            else:
                valid = False
        #@-node:ekr.20041005105605.123:<< read optional version param >>
        #@nl
        #@    << read optional thin param >>
        #@+node:ekr.20041005105605.124:<< read optional thin param >>
        if g.match(s,i,thin_tag):
            i += len(tag)
            isThinDerivedFile = True
        #@-node:ekr.20041005105605.124:<< read optional thin param >>
        #@nl
        #@    << read optional encoding param >>
        #@+node:ekr.20041005105605.125:<< read optional encoding param >>
        # Set the default encoding
        at.encoding = c.config.default_derived_file_encoding

        if g.match(s,i,encoding_tag):
            # Read optional encoding param, e.g., -encoding=utf-8,
            i += len(encoding_tag)
            # Skip to the next end of the field.
            j = s.find(",.",i)
            if j > -1:
                # The encoding field was written by 4.2 or after:
                encoding = s[i:j]
                i = j + 2 # 6/8/04, 1/11/05 (was i = j + 1)
            else:
                # The encoding field was written before 4.2.
                j = s.find('.',i)
                if j > -1:
                    encoding = s[i:j]
                    i = j + 1 # 6/8/04
                else:
                    encoding = None
            # g.trace("encoding:",encoding)
            if encoding:
                if g.isValidEncoding(encoding):
                    at.encoding = encoding
                else:
                    g.es_print("bad encoding in derived file:",encoding)
            else:
                valid = False
        #@-node:ekr.20041005105605.125:<< read optional encoding param >>
        #@nl
        #@    << set the closing comment delim >>
        #@+node:ekr.20041005105605.126:<< set the closing comment delim >>
        # The closing comment delim is the trailing non-whitespace.
        i = j = g.skip_ws(s,i)
        while i < n and not g.is_ws(s[i]) and not g.is_nl(s,i):
            i += 1
        end = s[j:i]
        #@-node:ekr.20041005105605.126:<< set the closing comment delim >>
        #@nl
        return valid,new_df,start,end,isThinDerivedFile
    #@-node:ekr.20041005105605.120:parseLeoSentinel
    #@+node:ekr.20041005105605.127:readError
    def readError(self,message):

        # This is useful now that we don't print the actual messages.
        if self.errors == 0:
            self.printError("----- read error. line: %s, file: %s" % (
                self.lineNumber,self.targetFileName,))

        # g.trace(self.root,g.callers())
        self.error(message)

        # Bug fix: 12/10/05: Delete all of root's tree.
        self.root.v.t._firstChild = None
        self.root.setOrphan()
        self.root.setDirty()
    #@-node:ekr.20041005105605.127:readError
    #@+node:ekr.20041005105605.128:readLine
    def readLine (self,theFile):

        """Reads one line from file using the present encoding"""

        s = g.readlineForceUnixNewline(theFile) # calls theFile.readline
        u = g.toUnicode(s,self.encoding)
        return u
    #@-node:ekr.20041005105605.128:readLine
    #@+node:ekr.20041005105605.129:scanHeader  (3.x and 4.x)
    def scanHeader(self,theFile,fileName):

        """Scan the @+leo sentinel.

        Sets self.encoding, and self.start/endSentinelComment.

        Returns (firstLines,new_df,isThinDerivedFile) where:
        firstLines        contains all @first lines,
        new_df            is True if we are reading a new-format derived file.
        isThinDerivedFile is True if the file is an @thin file."""

        at = self
        firstLines = [] # The lines before @+leo.
        tag = "@+leo"
        valid = True ; new_df = False ; isThinDerivedFile = False
        #@    << skip any non @+leo lines >>
        #@+node:ekr.20041005105605.130:<< skip any non @+leo lines >>
        #@+at 
        #@nonl
        # Queue up the lines before the @+leo.  These will be used to add as 
        # parameters to the @first directives, if any.  Empty lines are 
        # ignored (because empty @first directives are ignored). NOTE: the 
        # function now returns a list of the lines before @+leo.
        # 
        # We can not call sentinelKind here because that depends on the 
        # comment delimiters we set here.  @first lines are written 
        # "verbatim", so nothing more needs to be done!
        #@-at
        #@@c

        s = at.readLine(theFile)
        while len(s) > 0:
            j = s.find(tag)
            if j != -1: break
            firstLines.append(s) # Queue the line
            s = at.readLine(theFile)

        n = len(s)
        valid = n > 0
        #@-node:ekr.20041005105605.130:<< skip any non @+leo lines >>
        #@nl
        if valid:
            valid,new_df,start,end,isThinDerivedFile = at.parseLeoSentinel(s)
        if valid:
            at.startSentinelComment = start
            at.endSentinelComment = end
            # g.trace('start',repr(start),'end',repr(end))
        else:
            at.error("Bad @+leo sentinel in: %s" % fileName)
        # g.trace("start,end",repr(at.startSentinelComment),repr(at.endSentinelComment))
        return firstLines,new_df,isThinDerivedFile
    #@-node:ekr.20041005105605.129:scanHeader  (3.x and 4.x)
    #@+node:ekr.20041005105605.131:skipIndent
    # Skip past whitespace equivalent to width spaces.

    def skipIndent(self,s,i,width):

        ws = 0 ; n = len(s)
        while i < n and ws < width:
            if   s[i] == '\t': ws += (abs(self.tab_width) - (ws % abs(self.tab_width)))
            elif s[i] == ' ':  ws += 1
            else: break
            i += 1
        return i
    #@-node:ekr.20041005105605.131:skipIndent
    #@-node:ekr.20041005105605.116:Reading utils...
    #@-node:ekr.20041005105605.17:Reading...
    #@+node:ekr.20041005105605.132:Writing...
    #@+node:ekr.20041005105605.133:Writing (top level)
    #@+node:ekr.20041005105605.134:Don't override in plugins
    # Plugins probably should not need to override these methods.
    #@+node:ekr.20041005105605.135:closeWriteFile
    # 4.0: Don't use newline-pending logic.

    def closeWriteFile (self):

        at = self

        if at.outputFile:
            at.outputFile.flush()
            if self.toString:
                self.stringOutput = self.outputFile.get()
            at.outputFile.close()
            at.outputFile = None
    #@-node:ekr.20041005105605.135:closeWriteFile
    #@+node:ekr.20041005105605.136:norefWrite
    def norefWrite(self,root,toString=False):

        at = self ; c = at.c
        c.endEditing() # Capture the current headline.

        try:
            targetFileName = root.atNorefFileNodeName()
            at.initWriteIvars(root,targetFileName,nosentinels=False,toString=toString)
            if at.errors: return
            if not at.openFileForWriting(root,targetFileName,toString):
                return
            #@        << write root's tree >>
            #@+node:ekr.20041005105605.137:<< write root's tree >>
            #@<< put all @first lines in root >>
            #@+node:ekr.20041005105605.138:<< put all @first lines in root >>
            #@+at 
            #@nonl
            # Write any @first lines.  These lines are also converted to 
            # @verbatim lines, so the read logic simply ignores lines 
            # preceding the @+leo sentinel.
            #@-at
            #@@c

            s = root.v.t.bodyString
            tag = "@first"
            i = 0
            while g.match(s,i,tag):
                i += len(tag)
                i = g.skip_ws(s,i)
                j = i
                i = g.skip_to_end_of_line(s,i)
                # Write @first line, whether empty or not
                line = s[j:i]
                at.putBuffered(line) ; at.onl()
                i = g.skip_nl(s,i)
            #@-node:ekr.20041005105605.138:<< put all @first lines in root >>
            #@nl
            at.putOpenLeoSentinel("@+leo-ver=4")
            #@<< put optional @comment sentinel lines >>
            #@+node:ekr.20041005105605.139:<< put optional @comment sentinel lines >>
            s2 = c.config.output_initial_comment
            if s2:
                lines = string.split(s2,"\\n")
                for line in lines:
                    line = line.replace("@date",time.asctime())
                    if len(line)> 0:
                        at.putSentinel("@comment " + line)
            #@-node:ekr.20041005105605.139:<< put optional @comment sentinel lines >>
            #@nl

            for p in root.self_and_subtree_iter():
                #@    << Write p's node >>
                #@+node:ekr.20041005105605.140:<< Write p's node >>
                at.putOpenNodeSentinel(p)

                s = p.bodyString()

                if self.write_strips_blank_lines:
                    s = self.cleanLines(p,s)

                if s:
                    s = g.toEncodedString(s,at.encoding,reportErrors=True)
                    at.outputStringWithLineEndings(s)

                # Put an @nonl sentinel if s does not end in a newline.
                if s and s[-1] != '\n':
                    at.onl_sent() ; at.putSentinel("@nonl")

                at.putCloseNodeSentinel(p)
                #@-node:ekr.20041005105605.140:<< Write p's node >>
                #@nl

            at.putSentinel("@-leo")
            #@<< put all @last lines in root >>
            #@+node:ekr.20041005105605.141:<< put all @last lines in root >>
            #@+at 
            #@nonl
            # Write any @last lines.  These lines are also converted to 
            # @verbatim lines, so the read logic simply ignores lines 
            # following the @-leo sentinel.
            #@-at
            #@@c

            tag = "@last"
            lines = string.split(root.v.t.bodyString,'\n')
            n = len(lines) ; j = k = n - 1
            # Don't write an empty last line.
            if j >= 0 and len(lines[j])==0:
                j = k = n - 2
            # Scan backwards for @last directives.
            while j >= 0:
                line = lines[j]
                if g.match(line,0,tag): j -= 1
                else: break
            # Write the @last lines.
            for line in lines[j+1:k+1]:
                i = len(tag) ; i = g.skip_ws(line,i)
                at.putBuffered(line[i:]) ; at.onl()
            #@-node:ekr.20041005105605.141:<< put all @last lines in root >>
            #@nl
            #@-node:ekr.20041005105605.137:<< write root's tree >>
            #@nl
            at.closeWriteFile()
            at.replaceTargetFileIfDifferent()
            root.clearOrphan() ; root.clearDirty()
        except Exception:
            at.writeException(root)

    rawWrite = norefWrite
    #@-node:ekr.20041005105605.136:norefWrite
    #@+node:ekr.20041005105605.142:openFileForWriting & openFileForWritingHelper
    def openFileForWriting (self,root,fileName,toString):

        at = self
        at.outputFile = None

        if toString:
            at.shortFileName = g.shortFileName(fileName)
            at.outputFileName = "<string: %s>" % at.shortFileName
            at.outputFile = g.fileLikeObject()
        else:
            at.openFileForWritingHelper(fileName)

        # New in 4.3 b2: root may be none when writing from a string.
        if root:
            if at.outputFile:
                root.clearOrphan()
            else:
                root.setOrphan()
                root.setDirty()

        return at.outputFile is not None
    #@+node:ekr.20041005105605.143:openFileForWritingHelper
    def openFileForWritingHelper (self,fileName):

        at = self ; c = at.c

        try:
            at.shortFileName = g.shortFileName(fileName)
            fileName = g.os_path_join(at.default_directory,fileName)
            at.targetFileName = g.os_path_normpath(fileName)
            path = g.os_path_dirname(at.targetFileName)
            if not path or not g.os_path_exists(path):
                if path:
                    path = g.makeAllNonExistentDirectories(path,c=c)
                if not path or not g.os_path_exists(path):
                    path = g.os_path_dirname(at.targetFileName)
                    at.writeError("path does not exist: " + path)
                    return
        except Exception:
            at.exception("exception creating path: %s" % repr(path))
            g.es_exception()
            return

        if g.os_path_exists(at.targetFileName):
            try:
                if not os.access(at.targetFileName,os.W_OK):
                    at.writeError("can not create: read only: " + at.targetFileName)
                    return
            except AttributeError: pass # os.access() may not exist on all platforms.

        try:
            at.outputFileName = at.targetFileName + ".tmp"
            at.outputFile = self.openForWrite(at.outputFileName,'wb') # bwm
            if not at.outputFile:
                at.writeError("can not create " + at.outputFileName)
        except Exception:
            at.exception("exception creating:" + at.outputFileName)
    #@-node:ekr.20041005105605.143:openFileForWritingHelper
    #@-node:ekr.20041005105605.142:openFileForWriting & openFileForWritingHelper
    #@+node:ekr.20041005105605.144:write
    # This is the entry point to the write code.  root should be an @file vnode.

    def write(self,root,
        nosentinels=False,
        thinFile=False,
        scriptWrite=False,
        toString=False,
        write_strips_blank_lines=None,
    ):

        """Write a 4.x derived file."""

        at = self ; c = at.c
        c.endEditing() # Capture the current headline.

        #@    << set at.targetFileName >>
        #@+node:ekr.20041005105605.145:<< set at.targetFileName >>
        if toString:
            at.targetFileName = "<string-file>"
        elif nosentinels:
            at.targetFileName = root.atNoSentFileNodeName()
        elif thinFile:
            at.targetFileName = root.atThinFileNodeName()
        else:
            at.targetFileName = root.atFileNodeName()
        #@-node:ekr.20041005105605.145:<< set at.targetFileName >>
        #@nl
        at.initWriteIvars(root,at.targetFileName,
            nosentinels=nosentinels,thinFile=thinFile,
            scriptWrite=scriptWrite,toString=toString,
            write_strips_blank_lines=write_strips_blank_lines)
        if not at.openFileForWriting(root,at.targetFileName,toString):
            if root: root.setDirty() # Make _sure_ we try to rewrite this file.
            return

        try:
            at.writeOpenFile(root,nosentinels=nosentinels,toString=toString)
            if toString:
                at.closeWriteFile() # sets self.stringOutput
                # Major bug: failure to clear this wipes out headlines!
                # Minor bug: sometimes this causes slight problems...
                at.root.v.t.tnodeList = []
                at.root.v.t._p_changed = True
            else:
                at.closeWriteFile()
                #@            << set dirty and orphan bits on error >>
                #@+node:ekr.20041005105605.146:<< set dirty and orphan bits on error >>
                # Setting the orphan and dirty flags tells Leo to write the tree..

                if at.errors > 0 or at.root.isOrphan():
                    root.setOrphan()
                    root.setDirty() # Make _sure_ we try to rewrite this file.
                    os.remove(at.outputFileName) # Delete the temp file.
                    g.es("not written:",at.outputFileName)
                else:
                    root.clearOrphan()
                    root.clearDirty()
                    at.replaceTargetFileIfDifferent()
                #@-node:ekr.20041005105605.146:<< set dirty and orphan bits on error >>
                #@nl
        except Exception:
            if toString:
                at.exception("exception preprocessing script")
                at.root.v.t.tnodeList = []
                at.root.v.t._p_changed = True
            else:
                at.writeException() # Sets dirty and orphan bits.
    #@-node:ekr.20041005105605.144:write
    #@+node:ekr.20041005105605.147:writeAll (atFile)
    def writeAll(self,
        writeAtFileNodesFlag=False,
        writeDirtyAtFileNodesFlag=False,
        toString=False,
    ):

        """Write @file nodes in all or part of the outline"""

        at = self ; c = at.c
        writtenFiles = [] # Files that might be written again.
        mustAutoSave = False

        if writeAtFileNodesFlag:
            # Write all nodes in the selected tree.
            p = c.currentPosition()
            after = p.nodeAfterTree()
        else:
            # Write dirty nodes in the entire outline.
            p =  c.rootPosition()
            after = c.nullPosition()

        #@    << Clear all orphan bits >>
        #@+node:ekr.20041005105605.148:<< Clear all orphan bits >>
        #@+at 
        #@nonl
        # We must clear these bits because they may have been set on a 
        # previous write.
        # Calls to atFile::write may set the orphan bits in @file nodes.
        # If so, write_Leo_file will write the entire @file tree.
        #@-at
        #@@c

        for v2 in p.self_and_subtree_iter():
            v2.clearOrphan()
        #@-node:ekr.20041005105605.148:<< Clear all orphan bits >>
        #@nl
        while p and p != after:
            if p.isAnyAtFileNode() or p.isAtIgnoreNode():
                #@            << handle v's tree >>
                #@+node:ekr.20041005105605.149:<< handle v's tree >>
                if p.v.isDirty() or writeAtFileNodesFlag or p.v.t in writtenFiles:

                    at.fileChangedFlag = False
                    autoSave = False

                    # Tricky: @ignore not recognised in @silentfile nodes.
                    if p.isAtAsisFileNode():
                        at.asisWrite(p,toString=toString)
                        writtenFiles.append(p.v.t) ; autoSave = True
                    elif p.isAtIgnoreNode():
                        pass
                    elif p.isAtAutoNode():
                        at.writeOneAtAutoNode(p,toString=toString,force=False)
                        writtenFiles.append(p.v.t)
                    elif p.isAtNorefFileNode():
                        at.norefWrite(p,toString=toString)
                        writtenFiles.append(p.v.t) ; autoSave = True
                    elif p.isAtNoSentFileNode():
                        at.write(p,nosentinels=True,toString=toString)
                        writtenFiles.append(p.v.t) # No need for autosave
                    elif p.isAtThinFileNode():
                        at.write(p,thinFile=True,toString=toString)
                        writtenFiles.append(p.v.t) # No need for autosave.
                    elif p.isAtFileNode():
                        at.write(p,toString=toString)
                        writtenFiles.append(p.v.t) ; autoSave = True

                    if at.fileChangedFlag and autoSave: # Set by replaceTargetFileIfDifferent.
                        mustAutoSave = True
                #@-node:ekr.20041005105605.149:<< handle v's tree >>
                #@nl
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        #@    << say the command is finished >>
        #@+node:ekr.20041005105605.150:<< say the command is finished >>
        if writeAtFileNodesFlag or writeDirtyAtFileNodesFlag:
            if len(writtenFiles) > 0:
                g.es("finished")
            elif writeAtFileNodesFlag:
                g.es("no @file nodes in the selected tree")
            else:
                g.es("no dirty @file nodes")
        #@-node:ekr.20041005105605.150:<< say the command is finished >>
        #@nl
        return mustAutoSave
    #@-node:ekr.20041005105605.147:writeAll (atFile)
    #@+node:ekr.20070806105859:writeAtAutoNodes & writeDirtyAtFileNodes (atFile) & helpers
    def writeAtAutoNodes (self,event=None):

        '''Write all @auto nodes in the selected outline.'''

        at = self
        at.writeAtAutoNodesHelper(writeDirtyOnly=False)

    def writeDirtyAtAutoNodes (self,event=None):

        '''Write all dirty @auto nodes in the selected outline.'''

        at = self
        at.writeAtAutoNodesHelper(writeDirtyOnly=True)
    #@nonl
    #@+node:ekr.20070806140208:writeAtAutoNodesHelper
    def writeAtAutoNodesHelper(self,toString=False,writeDirtyOnly=True):

        """Write @auto nodes in the selected outline"""

        at = self ; c = at.c
        p = c.currentPosition() ; after = p.nodeAfterTree()
        found = False

        while p and p != after:
            if p.isAtAutoNode() and not p.isAtIgnoreNode() and (p.isDirty() or not writeDirtyOnly):
                ok = at.writeOneAtAutoNode(p,toString=toString,force=True)
                if ok:
                    found = True
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()

        if found:
            g.es("finished")
        elif writeDirtyOnly:
            g.es("no dirty @auto nodes in the selected tree")
        else:
            g.es("no @auto nodes in the selected tree")
    #@-node:ekr.20070806140208:writeAtAutoNodesHelper
    #@+node:ekr.20070806141607:writeOneAtAutoNode & helpers
    def writeOneAtAutoNode(self,p,toString,force):

        '''Write p, an @auto node.

        File indices *must* have already been assigned.'''

        at = self ; c = at.c ; root = p.copy()

        fileName = p.atAutoNodeName()
        if not fileName: return False

        at.scanDefaultDirectory(p,importing=True) # Set default_directory
        fileName = g.os_path_join(at.default_directory,fileName)
        exists = g.os_path_exists(fileName)

        if not toString and not self.shouldWriteAtAutoNode(p,exists,force):
            return False

        # This code is similar to code in at.write.
        c.endEditing() # Capture the current headline.
        at.targetFileName = g.choose(toString,"<string-file>",fileName)
        at.initWriteIvars(root,at.targetFileName,
            nosentinels=True,thinFile=False,scriptWrite=False,
            toString=toString,write_strips_blank_lines=False)

        ok = at.openFileForWriting (root,fileName=fileName,toString=toString)
        if ok:
            at.writeOpenFile(root,nosentinels=True,toString=toString,atAuto=True)
            at.closeWriteFile() # Sets stringOutput if toString is True.
            if at.errors == 0:
                at.replaceTargetFileIfDifferent()
            else:
                g.es("not written:",at.outputFileName)
        elif not toString:
            root.setDirty() # Make _sure_ we try to rewrite this file.
            g.es("not written:",at.outputFileName)

        return ok
    #@+node:ekr.20071019141745:shouldWriteAtAutoNode
    #@+at 
    #@nonl
    # Much thought went into this decision tree:
    # 
    # - We do not want decisions to depend on past history.  That's too 
    # confusing.
    # - We must ensure that the file will be written if the user does 
    # significant work.
    # - We must ensure that the user can create an @auto x node at any time
    #   without risk of of replacing x with empty or insignificant 
    # information.
    # - We want the user to be able to create an @auto node which will be 
    # populated the next time the .leo file is opened.
    # - We don't want minor import imperfections to be written to the @auto 
    # file.
    # - The explicit commands that read and write @auto trees must always be 
    # honored.
    #@-at
    #@@c

    def shouldWriteAtAutoNode (self,p,exists,force):

        '''Return True if we should write the @auto node at p.'''

        if force: # We are executing write-at-auto-node or write-dirty-at-auto-nodes.
            return True
        elif not exists: # We can write a non-existent file without danger.
            return True
        elif not p.isDirty(): # There is nothing new to write.
            return False
        elif not self.isSignificantAtAutoTree(p): # There is noting of value to write.
            g.es_print(p.headString(),'not written:',color='red')
            g.es_print('no children and less than 10 characters (excluding directives)',color='red')
            return False
        else: # The @auto tree is dirty and contains significant info.
            return True
    #@-node:ekr.20071019141745:shouldWriteAtAutoNode
    #@+node:ekr.20070909103844:isSignificantAtAutoTree
    def isSignificantAtAutoTree (self,p):

        '''Return True if p's tree has a significant amount of information.'''

        s = p.bodyString()

        # Remove all blank lines and all Leo directives.
        lines = []
        for line in g.splitLines(s):
            if not line.strip():
                pass
            elif line.startswith('@'):
                i = 1 ; j = g.skip_id(line,i,chars='-')
                word = s[i:j]
                if not (word and word in g.globalDirectiveList):
                    lines.append(line)
            else:
                lines.append(line)

        s2 = ''.join(lines)
        # g.trace('s2',s2)

        return p.hasChildren() or len(s2.strip()) >= 10
    #@-node:ekr.20070909103844:isSignificantAtAutoTree
    #@-node:ekr.20070806141607:writeOneAtAutoNode & helpers
    #@-node:ekr.20070806105859:writeAtAutoNodes & writeDirtyAtFileNodes (atFile) & helpers
    #@+node:ekr.20050506084734:writeFromString
    # This is at.write specialized for scripting.

    def writeFromString(self,root,s,forcePythonSentinels=True,useSentinels=True):

        """Write a 4.x derived file from a string.

        This is used by the scripting logic."""

        at = self ; c = at.c
        c.endEditing() # Capture the current headline, but don't change the focus!

        at.initWriteIvars(root,"<string-file>",
            nosentinels=not useSentinels,thinFile=False,scriptWrite=True,toString=True,
            forcePythonSentinels=forcePythonSentinels)

        try:
            at.openFileForWriting(root,at.targetFileName,toString=True)
            # Simulate writing the entire file so error recovery works.
            at.writeOpenFile(root,nosentinels=not useSentinels,toString=True,fromString=s)
            at.closeWriteFile()
            # Major bug: failure to clear this wipes out headlines!
            # Minor bug: sometimes this causes slight problems...
            if root:
                root.v.t.tnodeList = []
                root.v.t._p_changed = True
        except Exception:
            at.exception("exception preprocessing script")

        return at.stringOutput
    #@-node:ekr.20050506084734:writeFromString
    #@+node:ekr.20041005105605.151:writeMissing
    def writeMissing(self,p,toString=False):

        at = self ; c = at.c
        writtenFiles = False ; changedFiles = False

        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after: # Don't use iterator.
            if p.isAtAsisFileNode() or (p.isAnyAtFileNode() and not p.isAtIgnoreNode()):
                at.targetFileName = p.anyAtFileNodeName()
                if at.targetFileName:
                    at.targetFileName = g.os_path_join(self.default_directory,at.targetFileName)
                    at.targetFileName = g.os_path_normpath(at.targetFileName)
                    if not g.os_path_exists(at.targetFileName):
                        at.openFileForWriting(p,at.targetFileName,toString)
                        if at.outputFile:
                            #@                        << write the @file node >>
                            #@+node:ekr.20041005105605.152:<< write the @file node >>
                            if p.isAtAsisFileNode():
                                at.asisWrite(p)
                            elif p.isAtNorefFileNode():
                                at.norefWrite(p)
                            elif p.isAtNoSentFileNode():
                                at.write(p,nosentinels=True)
                            elif p.isAtFileNode():
                                at.write(p)
                            else: assert(0)

                            writtenFiles = True

                            if at.fileChangedFlag: # Set by replaceTargetFileIfDifferent.
                                changedFiles = True
                            #@-node:ekr.20041005105605.152:<< write the @file node >>
                            #@nl
                            at.closeWriteFile()
                p.moveToNodeAfterTree()
            elif p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        if writtenFiles > 0:
            g.es("finished")
        else:
            g.es("no @file node in the selected tree")

        return changedFiles # So caller knows whether to do an auto-save.
    #@-node:ekr.20041005105605.151:writeMissing
    #@-node:ekr.20041005105605.134:Don't override in plugins
    #@+node:ekr.20041005105605.153:Override in plugins...
    #@+at
    # 
    # All writing eventually goes through the asisWrite or writeOpenFile 
    # methods, so
    # plugins should need only to override these two methods.
    # 
    # In particular, plugins should not need to override the write, writeAll 
    # or
    # writeMissing methods.
    #@-at
    #@+node:ekr.20041005105605.154:asisWrite
    def asisWrite(self,root,toString=False):

        at = self ; c = at.c
        c.endEditing() # Capture the current headline.

        try:
            targetFileName = root.atAsisFileNodeName()
            at.initWriteIvars(root,targetFileName,toString=toString)
            if at.errors: return
            if not at.openFileForWriting(root,targetFileName,toString): return
            for p in root.self_and_subtree_iter():
                #@            << Write p's headline if it starts with @@ >>
                #@+node:ekr.20041005105605.155:<< Write p's headline if it starts with @@ >>
                s = p.headString()

                if g.match(s,0,"@@"):
                    s = s[2:]
                    if s and len(s) > 0:
                        s = g.toEncodedString(s,at.encoding,reportErrors=True) # 3/7/03
                        at.outputFile.write(s)
                #@-node:ekr.20041005105605.155:<< Write p's headline if it starts with @@ >>
                #@nl
                #@            << Write p's body >>
                #@+node:ekr.20041005105605.156:<< Write p's body >>
                s = p.bodyString()

                if self.write_strips_blank_lines:
                    s = self.cleanLines(p,s)

                if s:
                    s = g.toEncodedString(s,at.encoding,reportErrors=True) # 3/7/03
                    at.outputStringWithLineEndings(s)
                #@-node:ekr.20041005105605.156:<< Write p's body >>
                #@nl
            at.closeWriteFile()
            at.replaceTargetFileIfDifferent()
            root.clearOrphan() ; root.clearDirty()
        except Exception:
            at.writeException(root)

    silentWrite = asisWrite # Compatibility with old scripts.
    #@-node:ekr.20041005105605.154:asisWrite
    #@+node:ekr.20041005105605.157:writeOpenFile
    # New in 4.3: must be inited before calling this method.
    # New in 4.3 b2: support for writing from a string.

    def writeOpenFile(self,root,nosentinels=False,toString=False,fromString='',atAuto=False):

        """Do all writes except asis writes."""

        at = self ; s = g.choose(fromString,fromString,root.v.t.bodyString)

        root.clearAllVisitedInTree() # Clear both vnode and tnode bits.
        root.clearVisitedInTree()

        at.putAtFirstLines(s)
        at.putOpenLeoSentinel("@+leo-ver=4")
        at.putInitialComment()
        at.putOpenNodeSentinel(root)
        at.putBody(root,fromString=fromString)
        at.putCloseNodeSentinel(root)
        at.putSentinel("@-leo")
        root.setVisited()
        at.putAtLastLines(s)

        if atAuto or (not toString and not nosentinels):
            at.warnAboutOrphandAndIgnoredNodes()
    #@-node:ekr.20041005105605.157:writeOpenFile
    #@-node:ekr.20041005105605.153:Override in plugins...
    #@-node:ekr.20041005105605.133:Writing (top level)
    #@+node:ekr.20041005105605.160:Writing 4.x
    #@+node:ekr.20041005105605.161:putBody
    # oneNodeOnly is no longer used, but it might be used in the future?

    def putBody(self,p,oneNodeOnly=False,fromString=''):

        """ Generate the body enclosed in sentinel lines."""

        at = self

        # New in 4.3 b2: get s from fromString if possible.
        s = g.choose(fromString,fromString,p.bodyString())

        p.v.t.setVisited() # Suppress orphans check.
        p.v.setVisited() # Make sure v is never expanded again.
        if not at.thinFile:
            p.v.t.setWriteBit() # Mark the tnode to be written.
        if not at.thinFile and not s: return

        inCode = True
        #@    << Make sure all lines end in a newline >>
        #@+node:ekr.20041005105605.162:<< Make sure all lines end in a newline >>
        #@+at
        # 
        # If we add a trailing newline, we'll generate an @nonl sentinel 
        # below.
        # 
        # - We always ensure a newline in @file and @thin trees.
        # - This code is not used used in @asis trees.
        # - New in Leo 4.4.3 b1: We add a newline in @nosent trees unless
        #   @bool force_newlines_in_at_nosent_bodies = False
        #@-at
        #@@c

        if s:
            trailingNewlineFlag = s[-1] == '\n'
            if (at.sentinels or at.force_newlines_in_at_nosent_bodies) and not trailingNewlineFlag:
                # g.trace('Added newline',repr(s))
                s = s + '\n'
        else:
            trailingNewlineFlag = True # don't need to generate an @nonl
        #@-node:ekr.20041005105605.162:<< Make sure all lines end in a newline >>
        #@nl
        if self.write_strips_blank_lines:
            s = self.cleanLines(p,s)
        i = 0
        while i < len(s):
            next_i = g.skip_line(s,i)
            assert(next_i > i)
            kind = at.directiveKind4(s,i)
            #@        << handle line at s[i] >>
            #@+node:ekr.20041005105605.163:<< handle line at s[i]  >>
            if kind == at.noDirective:
                if not oneNodeOnly:
                    if inCode:
                        hasRef,n1,n2 = at.findSectionName(s,i)
                        if hasRef and not at.raw:
                            at.putRefLine(s,i,n1,n2,p)
                        else:
                            at.putCodeLine(s,i)
                    else:
                        at.putDocLine(s,i)
            elif kind in (at.docDirective,at.atDirective):
                assert(not at.pending)
                if not inCode: # Bug fix 12/31/04: handle adjacent doc parts.
                    at.putEndDocLine() 
                at.putStartDocLine(s,i,kind)
                inCode = False
            elif kind in (at.cDirective,at.codeDirective):
                # Only @c and @code end a doc part.
                if not inCode:
                    at.putEndDocLine() 
                at.putDirective(s,i)
                inCode = True
            elif kind == at.allDirective:
                if not oneNodeOnly:
                    if inCode: at.putAtAllLine(s,i,p)
                    else: at.putDocLine(s,i)
            elif kind == at.othersDirective:
                if not oneNodeOnly:
                    if inCode: at.putAtOthersLine(s,i,p)
                    else: at.putDocLine(s,i)
            elif kind == at.rawDirective:
                at.raw = True
                at.putSentinel("@@raw")
            elif kind == at.endRawDirective:
                at.raw = False
                at.putSentinel("@@end_raw")
                i = g.skip_line(s,i)
            elif kind == at.miscDirective:
                # g.trace('miscDirective')
                at.putDirective(s,i)
            else:
                assert(0) # Unknown directive.
            #@-node:ekr.20041005105605.163:<< handle line at s[i]  >>
            #@nl
            i = next_i
        if not inCode:
            at.putEndDocLine()
        if at.sentinels and not trailingNewlineFlag:
            at.putSentinel("@nonl")
    #@-node:ekr.20041005105605.161:putBody
    #@+node:ekr.20041005105605.164:writing code lines...
    #@+node:ekr.20041005105605.165:@all
    #@+node:ekr.20041005105605.166:putAtAllLine
    def putAtAllLine (self,s,i,p):

        """Put the expansion of @others."""

        at = self
        j,delta = g.skip_leading_ws_with_indent(s,i,at.tab_width)
        at.putLeadInSentinel(s,i,j,delta)

        at.indent += delta
        if at.leadingWs:
            at.putSentinel("@" + at.leadingWs + "@+all")
        else:
            at.putSentinel("@+all")

        for child in p.children_iter():
            at.putAtAllChild(child)

        at.putSentinel("@-all")
        at.indent -= delta
    #@-node:ekr.20041005105605.166:putAtAllLine
    #@+node:ekr.20041005105605.167:putatAllBody
    def putAtAllBody(self,p):

        """ Generate the body enclosed in sentinel lines."""

        at = self ; s = p.bodyString()

        p.v.setVisited()   # Make sure v is never expanded again.
        p.v.t.setVisited() # Use the tnode for the orphans check.
        if not at.thinFile and not s: return
        inCode = True
        #@    << Make sure all lines end in a newline >>
        #@+node:ekr.20041005105605.168:<< Make sure all lines end in a newline >>
        # 11/20/03: except in nosentinel mode.
        # 1/30/04: and especially in scripting mode.
        # If we add a trailing newline, we'll generate an @nonl sentinel below.

        if s:
            trailingNewlineFlag = s and s[-1] == '\n'
            if at.sentinels and not trailingNewlineFlag:
                s = s + '\n'
        else:
            trailingNewlineFlag = True # don't need to generate an @nonl
        #@-node:ekr.20041005105605.168:<< Make sure all lines end in a newline >>
        #@nl
        i = 0
        while i < len(s):
            next_i = g.skip_line(s,i)
            assert(next_i > i)
            if inCode:
                # Use verbatim sentinels to write all directives.
                at.putCodeLine(s,i)
            else:
                at.putDocLine(s,i)
            i = next_i

        if not inCode:
            at.putEndDocLine()
        if at.sentinels and not trailingNewlineFlag:
            at.putSentinel("@nonl")
    #@-node:ekr.20041005105605.167:putatAllBody
    #@+node:ekr.20041005105605.169:putAtAllChild
    #@+at
    # This code puts only the first of two or more cloned siblings, preceding 
    # the
    # clone with an @clone n sentinel.
    # 
    # This is a debatable choice: the cloned tree appears only once in the 
    # derived
    # file. This should be benign; the text created by @all is likely to be 
    # used only
    # for recreating the outline in Leo. The representation in the derived 
    # file
    # doesn't matter much.
    #@-at
    #@@c

    def putAtAllChild(self,p):

        at = self

        clonedSibs,thisClonedSibIndex = at.scanForClonedSibs(p.v)
        if clonedSibs > 1:
            if thisClonedSibIndex == 1:
                at.putSentinel("@clone %d" % (clonedSibs))
            else: return # Don't write second or greater trees.

        at.putOpenNodeSentinel(p,inAtAll=True) # Suppress warnings about @file nodes.
        at.putAtAllBody(p) 

        for child in p.children_iter():
            at.putAtAllChild(child)

        at.putCloseNodeSentinel(p)
    #@-node:ekr.20041005105605.169:putAtAllChild
    #@-node:ekr.20041005105605.165:@all
    #@+node:ekr.20041005105605.170:@others
    #@+node:ekr.20041005105605.171:inAtOthers
    def inAtOthers(self,p):

        """Returns True if p should be included in the expansion of the at-others directive

        in the body text of p's parent."""

        # Return False if this has been expanded previously.
        if  p.v.isVisited():
            # g.trace("previously visited",p.v)
            return False

        # Return False if this is a definition node.
        h = p.headString() ; i = g.skip_ws(h,0)
        isSection,junk = self.isSectionName(h,i)
        if isSection:
            # g.trace("is section",p)
            return False

        # Return False if p's body contains an @ignore directive.
        if p.isAtIgnoreNode():
            # g.trace("is @ignore",p)
            return False
        else:
            # g.trace("ok",p)
            return True
    #@-node:ekr.20041005105605.171:inAtOthers
    #@+node:ekr.20041005105605.172:putAtOthersChild
    def putAtOthersChild(self,p):

        at = self

        clonedSibs,thisClonedSibIndex = at.scanForClonedSibs(p.v)
        if clonedSibs > 1 and thisClonedSibIndex == 1:
            at.writeError("Cloned siblings are not valid in @thin trees")

        at.putOpenNodeSentinel(p)
        at.putBody(p) 

        # Insert expansions of all children.
        for child in p.children_iter():
            if at.inAtOthers(child):
                at.putAtOthersChild(child)

        at.putCloseNodeSentinel(p)
    #@-node:ekr.20041005105605.172:putAtOthersChild
    #@+node:ekr.20041005105605.173:putAtOthersLine
    def putAtOthersLine (self,s,i,p):

        """Put the expansion of @others."""

        at = self
        j,delta = g.skip_leading_ws_with_indent(s,i,at.tab_width)
        at.putLeadInSentinel(s,i,j,delta)

        at.indent += delta
        if at.leadingWs:
            at.putSentinel("@" + at.leadingWs + "@+others")
        else:
            at.putSentinel("@+others")

        for child in p.children_iter():
            if at.inAtOthers(child):
                at.putAtOthersChild(child)

        at.putSentinel("@-others")
        at.indent -= delta
    #@-node:ekr.20041005105605.173:putAtOthersLine
    #@-node:ekr.20041005105605.170:@others
    #@+node:ekr.20041005105605.174:putCodeLine (leoAtFile)
    def putCodeLine (self,s,i):

        '''Put a normal code line.'''

        at = self

        # Put @verbatim sentinel if required.
        k = g.skip_ws(s,i)
        if g.match(s,k,self.startSentinelComment + '@'):
            self.putSentinel('@verbatim')

        j = g.skip_line(s,i)
        line = s[i:j]

        # g.trace('atRaw',at.raw,'line',repr(line),g.callers(4))

        if self.write_strips_blank_lines:
            # Don't put any whitespace in otherwise blank lines.
            if line.strip(): # The line has non-empty content.
                if not at.raw:
                    at.putIndent(at.indent)

                if line[-1:]=='\n':
                    at.os(line[:-1])
                    at.onl()
                else:
                    at.os(line)
            elif line and line[-1] == '\n':
                at.onl()
            else:
                g.trace('Can not happen: completely empty line')
        else:
            # Don't put leading indent if the line is empty!
            if line.strip() and not at.raw: 
                at.putIndent(at.indent)

            if line[-1:]=='\n':
                at.os(line[:-1])
                at.onl()
            else:
                at.os(line)
    #@-node:ekr.20041005105605.174:putCodeLine (leoAtFile)
    #@+node:ekr.20041005105605.175:putRefLine & allies
    #@+node:ekr.20041005105605.176:putRefLine
    def putRefLine(self,s,i,n1,n2,p):

        """Put a line containing one or more references."""

        at = self

        # Compute delta only once.
        delta = self.putRefAt(s,i,n1,n2,p,delta=None)
        if delta is None: return # 11/23/03

        while 1:
            i = n2 + 2
            hasRef,n1,n2 = at.findSectionName(s,i)
            if hasRef:
                self.putAfterMiddleRef(s,i,n1,delta)
                self.putRefAt(s,n1,n1,n2,p,delta)
            else:
                break

        self.putAfterLastRef(s,i,delta)
    #@-node:ekr.20041005105605.176:putRefLine
    #@+node:ekr.20041005105605.177:putRefAt
    def putRefAt (self,s,i,n1,n2,p,delta):

        """Put a reference at s[n1:n2+2] from p."""

        at = self ; c = at.c ; name = s[n1:n2+2]

        ref = g.findReference(c,name,p)
        if not ref:
            if not g.unitTesting:
                at.writeError(
                    "undefined section: %s\n\treferenced from: %s" %
                        ( name,p.headString()))
            return None

        # Expand the ref.
        if not delta:
            junk,delta = g.skip_leading_ws_with_indent(s,i,at.tab_width)

        at.putLeadInSentinel(s,i,n1,delta)

        inBetween = []
        if at.thinFile: # @+-middle used only in thin files.
            parent = ref.parent()
            while parent != p:
                inBetween.append(parent)
                parent = parent.parent()

        at.indent += delta

        if at.leadingWs:
            at.putSentinel("@" + at.leadingWs + name)
        else:
            at.putSentinel("@" + name)

        if inBetween:
            # Bug fix: reverse the +middle sentinels, not the -middle sentinels.
            inBetween.reverse()
            for p2 in inBetween:
                at.putOpenNodeSentinel(p2,middle=True)

        at.putOpenNodeSentinel(ref)
        at.putBody(ref)
        at.putCloseNodeSentinel(ref)

        if inBetween:
            inBetween.reverse()
            for p2 in inBetween:
                at.putCloseNodeSentinel(p2,middle=True)

        at.indent -= delta

        return delta
    #@-node:ekr.20041005105605.177:putRefAt
    #@+node:ekr.20041005105605.178:putAfterLastRef
    def putAfterLastRef (self,s,start,delta):

        """Handle whatever follows the last ref of a line."""

        at = self

        j = g.skip_ws(s,start)

        if j < len(s) and s[j] != '\n':
            end = g.skip_line(s,start)
            after = s[start:end] # Ends with a newline only if the line did.
            # Temporarily readjust delta to make @afterref look better.
            at.indent += delta
            at.putSentinel("@afterref")
            at.os(after)
            if at.sentinels and after and after[-1] != '\n':
                at.onl() # Add a newline if the line didn't end with one.
            at.indent -= delta
        else:
            # Temporarily readjust delta to make @nl look better.
            at.indent += delta
            at.putSentinel("@nl")
            at.indent -= delta
    #@-node:ekr.20041005105605.178:putAfterLastRef
    #@+node:ekr.20041005105605.179:putAfterMiddleef
    def putAfterMiddleRef (self,s,start,end,delta):

        """Handle whatever follows a ref that is not the last ref of a line."""

        at = self

        if start < end:
            after = s[start:end]
            at.indent += delta
            at.putSentinel("@afterref")
            at.os(after) ; at.onl_sent() # Not a real newline.
            at.putSentinel("@nonl")
            at.indent -= delta
    #@-node:ekr.20041005105605.179:putAfterMiddleef
    #@-node:ekr.20041005105605.175:putRefLine & allies
    #@-node:ekr.20041005105605.164:writing code lines...
    #@+node:ekr.20041005105605.180:writing doc lines...
    #@+node:ekr.20041005105605.181:putBlankDocLine
    def putBlankDocLine (self):

        at = self

        at.putPending(split=False)

        if not at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.startSentinelComment) ; at.oblank()

        at.onl()
    #@-node:ekr.20041005105605.181:putBlankDocLine
    #@+node:ekr.20041005105605.182:putStartDocLine
    def putStartDocLine (self,s,i,kind):

        """Write the start of a doc part."""

        at = self ; at.docKind = kind

        sentinel = g.choose(kind == at.docDirective,"@+doc","@+at")
        directive = g.choose(kind == at.docDirective,"@doc","@")

        if 0: # New code: put whatever follows the directive in the sentinel
            # Skip past the directive.
            i += len(directive)
            j = g.skip_to_end_of_line(s,i)
            follow = s[i:j]

            # Put the opening @+doc or @-doc sentinel, including whatever follows the directive.
            at.putSentinel(sentinel + follow)

            # Put the opening comment if we are using block comments.
            if at.endSentinelComment:
                at.putIndent(at.indent)
                at.os(at.startSentinelComment) ; at.onl()
        else: # old code.
            # Skip past the directive.
            i += len(directive)

            # Get the trailing whitespace.
            j = g.skip_ws(s,i)
            ws = s[i:j]

            # Put the opening @+doc or @-doc sentinel, including trailing whitespace.
            at.putSentinel(sentinel + ws)

            # Put the opening comment.
            if at.endSentinelComment:
                at.putIndent(at.indent)
                at.os(at.startSentinelComment) ; at.onl()

            # Put an @nonl sentinel if there is significant text following @doc or @.
            if not g.is_nl(s,j):
                # Doesn't work if we are using block comments.
                at.putSentinel("@nonl")
                at.putDocLine(s,j)
    #@-node:ekr.20041005105605.182:putStartDocLine
    #@+node:ekr.20041005105605.183:putDocLine
    def putDocLine (self,s,i):

        """Handle one line of a doc part.

        Output complete lines and split long lines and queue pending lines.
        Inserted newlines are always preceded by whitespace."""

        at = self
        j = g.skip_line(s,i)
        s = s[i:j]

        if at.endSentinelComment:
            leading = at.indent
        else:
            leading = at.indent + len(at.startSentinelComment) + 1

        if not s or s[0] == '\n':
            # A blank line.
            at.putBlankDocLine()
        else:
            #@        << append words to pending line, splitting the line if needed >>
            #@+node:ekr.20041005105605.184:<< append words to pending line, splitting the line if needed >>
            #@+at 
            #@nonl
            # All inserted newlines are preceeded by whitespace:
            # we remove trailing whitespace from lines that have not been 
            # split.
            #@-at
            #@@c

            i = 0
            while i < len(s):

                # Scan to the next word.
                word1 = i # Start of the current word.
                word2 = i = g.skip_ws(s,i)
                while i < len(s) and s[i] not in (' ','\t'):
                    i += 1
                word3 = i = g.skip_ws(s,i)
                # g.trace(s[word1:i])

                if leading + word3 - word1 + len(''.join(at.pending)) >= at.page_width:
                    if at.pending:
                        # g.trace("splitting long line.")
                        # Ouput the pending line, and start a new line.
                        at.putPending(split=True)
                        at.pending = [s[word2:word3]]
                    else:
                        # Output a long word on a line by itself.
                        # g.trace("long word:",s[word2:word3])
                        at.pending = [s[word2:word3]]
                        at.putPending(split=True)
                else:
                    # Append the entire word to the pending line.
                    # g.trace("appending",s[word1:word3])
                    at.pending.append(s[word1:word3])

            # Output the remaining line: no more is left.
            at.putPending(split=False)
            #@-node:ekr.20041005105605.184:<< append words to pending line, splitting the line if needed >>
            #@nl
    #@-node:ekr.20041005105605.183:putDocLine
    #@+node:ekr.20041005105605.185:putEndDocLine
    def putEndDocLine (self):

        """Write the conclusion of a doc part."""

        at = self

        at.putPending(split=False)

        # Put the closing delimiter if we are using block comments.
        if at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.endSentinelComment)
            at.onl() # Note: no trailing whitespace.

        sentinel = g.choose(at.docKind == at.docDirective,"@-doc","@-at")
        at.putSentinel(sentinel)
    #@-node:ekr.20041005105605.185:putEndDocLine
    #@+node:ekr.20041005105605.186:putPending
    def putPending (self,split):

        """Write the pending part of a doc part.

        We retain trailing whitespace iff the split flag is True."""

        at = self ; s = ''.join(at.pending) ; at.pending = []

        # g.trace("split",s)

        # Remove trailing newline temporarily.  We'll add it back later.
        if s and s[-1] == '\n':
            s = s[:-1]

        if not split:
            s = s.rstrip()
            if not s:
                return

        at.putIndent(at.indent)

        if not at.endSentinelComment:
            at.os(at.startSentinelComment) ; at.oblank()

        at.os(s) ; at.onl()
    #@-node:ekr.20041005105605.186:putPending
    #@-node:ekr.20041005105605.180:writing doc lines...
    #@-node:ekr.20041005105605.160:Writing 4.x
    #@+node:ekr.20041005105605.187:Writing 4,x sentinels...
    #@+node:ekr.20041005105605.188:nodeSentinelText 4.x
    def nodeSentinelText(self,p):

        """Return the text of a @+node or @-node sentinel for p."""

        at = self ; h = p.headString()
        #@    << remove comment delims from h if necessary >>
        #@+node:ekr.20041005105605.189:<< remove comment delims from h if necessary >>
        #@+at 
        #@nonl
        # Bug fix 1/24/03:
        # 
        # If the present @language/@comment settings do not specify a 
        # single-line comment we remove all block comment delims from h.  This 
        # prevents headline text from interfering with the parsing of node 
        # sentinels.
        #@-at
        #@@c

        start = at.startSentinelComment
        end = at.endSentinelComment

        if end and len(end) > 0:
            h = h.replace(start,"")
            h = h.replace(end,"")
        #@-node:ekr.20041005105605.189:<< remove comment delims from h if necessary >>
        #@nl

        if at.thinFile:
            if not p.v.t.fileIndex:
                p.v.t.fileIndex = g.app.nodeIndices.getNewIndex()
            gnx = g.app.nodeIndices.toString(p.v.t.fileIndex)
            return "%s:%s" % (gnx,h)
        else:
            return h
    #@-node:ekr.20041005105605.188:nodeSentinelText 4.x
    #@+node:ekr.20041005105605.190:putLeadInSentinel 4.x
    def putLeadInSentinel (self,s,i,j,delta):

        """Generate @nonl sentinels as needed to ensure a newline before a group of sentinels.

        Set at.leadingWs as needed for @+others and @+<< sentinels.

        i points at the start of a line.
        j points at @others or a section reference.
        delta is the change in at.indent that is about to happen and hasn't happened yet."""

        at = self
        at.leadingWs = "" # Set the default.
        if i == j:
            return # The @others or ref starts a line.

        k = g.skip_ws(s,i)
        if j == k:
            # Only whitespace before the @others or ref.
            at.leadingWs = s[i:j] # Remember the leading whitespace, including its spelling.
        else:
            # g.trace("indent",self.indent)
            self.putIndent(self.indent) # 1/29/04: fix bug reported by Dan Winkler.
            at.os(s[i:j]) ; at.onl_sent() # 10/21/03
            at.indent += delta # Align the @nonl with the following line.
            at.putSentinel("@nonl")
            at.indent -= delta # Let the caller set at.indent permanently.
    #@-node:ekr.20041005105605.190:putLeadInSentinel 4.x
    #@+node:ekr.20041005105605.191:putCloseNodeSentinel 4.x
    def putCloseNodeSentinel(self,p,middle=False):

        at = self

        s = self.nodeSentinelText(p)

        if middle:
            at.putSentinel("@-middle:" + s)
        else:
            at.putSentinel("@-node:" + s)
    #@-node:ekr.20041005105605.191:putCloseNodeSentinel 4.x
    #@+node:ekr.20041005105605.192:putOpenLeoSentinel 4.x
    def putOpenLeoSentinel(self,s):

        """Write @+leo sentinel."""

        at = self

        if not at.sentinels:
            return # Handle @nosentinelsfile.

        if at.thinFile:
            s = s + "-thin"

        encoding = at.encoding.lower()
        if encoding != "utf-8":
            # New in 4.2: encoding fields end in ",."
            s = s + "-encoding=%s,." % (encoding)

        at.putSentinel(s)
    #@-node:ekr.20041005105605.192:putOpenLeoSentinel 4.x
    #@+node:ekr.20041005105605.193:putOpenNodeSentinel (sets tnodeList) 4.x
    def putOpenNodeSentinel(self,p,inAtAll=False,middle=False):

        """Write @+node sentinel for p."""

        at = self

        if not inAtAll and p.isAtFileNode() and p != at.root:
            at.writeError("@file not valid in: " + p.headString())
            return

        # g.trace(at.thinFile,p)

        s = at.nodeSentinelText(p)

        if middle:
            at.putSentinel("@+middle:" + s)
        else:
            at.putSentinel("@+node:" + s)

        if not at.thinFile:
            # Append the n'th tnode to the root's tnode list.
            # It may not exist when executing scripts.
            try:
                # Pychecker doesn't like so many references in a row...
                t = at.root.v.t
                t.tnodeList.append(p.v.t)
                t._p_changed = True
            except AttributeError:
                pass # Do nothing.  We are creating a script.
    #@-node:ekr.20041005105605.193:putOpenNodeSentinel (sets tnodeList) 4.x
    #@+node:ekr.20041005105605.194:putSentinel (applies cweb hack) 4.x
    # This method outputs all sentinels.

    def putSentinel(self,s):

        "Write a sentinel whose text is s, applying the CWEB hack if needed."

        at = self

        if not at.sentinels:
            return # Handle @file-nosent

        at.putIndent(at.indent)
        at.os(at.startSentinelComment)
        #@    << apply the cweb hack to s >>
        #@+node:ekr.20041005105605.195:<< apply the cweb hack to s >>
        #@+at 
        #@nonl
        # The cweb hack:
        # 
        # If the opening comment delim ends in '@', double all '@' signs 
        # except the first, which is "doubled" by the trailing '@' in the 
        # opening comment delimiter.
        #@-at
        #@@c

        start = at.startSentinelComment
        if start and start[-1] == '@':
            assert(s and s[0]=='@')
            s = s.replace('@','@@')[1:]
        #@-node:ekr.20041005105605.195:<< apply the cweb hack to s >>
        #@nl
        at.os(s)
        if at.endSentinelComment:
            at.os(at.endSentinelComment)
        at.onl()
    #@-node:ekr.20041005105605.194:putSentinel (applies cweb hack) 4.x
    #@-node:ekr.20041005105605.187:Writing 4,x sentinels...
    #@+node:ekr.20041005105605.196:Writing 4.x utils...
    #@+node:ekr.20041005105605.197:compareFiles
    # This routine is needed to handle cvs stupidities.

    def compareFiles (self,path1,path2,ignoreLineEndings):

        """Compare two text files ignoring line endings."""

        try:
            # Opening both files in text mode converts all line endings to '\n'.
            mode = g.choose(ignoreLineEndings,"r","rb")
            f1 = open(path1,mode)
            f2 = open(path2,mode)
            equal = f1.read() == f2.read()
            f1.close() ; f2.close()
            return equal
        except IOError:
            return False # Should never happen
    #@-node:ekr.20041005105605.197:compareFiles
    #@+node:ekr.20041005105605.198:directiveKind4
    def directiveKind4(self,s,i):

        """Return the kind of at-directive or noDirective."""

        at = self
        n = len(s)
        if i >= n or s[i] != '@':
            j = g.skip_ws(s,i)
            if g.match_word(s,j,"@others"):
                return at.othersDirective
            elif g.match_word(s,j,"@all"):
                return at.allDirective
            else:
                return at.noDirective

        table = (
            ("@all",at.allDirective),
            ("@c",at.cDirective),
            ("@code",at.codeDirective),
            ("@doc",at.docDirective),
            ("@end_raw",at.endRawDirective),
            ("@others",at.othersDirective),
            ("@raw",at.rawDirective))

        # Rewritten 6/8/2005.
        if i+1 >= n or s[i+1] in (' ','\t','\n'):
            # Bare '@' not recognized in cweb mode.
            return g.choose(at.language=="cweb",at.noDirective,at.atDirective)
        if not s[i+1].isalpha():
            return at.noDirective # Bug fix: do NOT return miscDirective here!
        if at.language=="cweb" and g.match_word(s,i,'@c'):
            return at.noDirective

        for name,directive in table:
            if g.match_word(s,i,name):
                return directive

        # New in Leo 4.4.3: add support for add_directives plugin.
        for name in g.globalDirectiveList:
            if g.match_word(s,i+1,name):
                return at.miscDirective

        return at.noDirective
    #@-node:ekr.20041005105605.198:directiveKind4
    #@+node:ekr.20041005105605.199:hasSectionName
    def findSectionName(self,s,i):

        end = s.find('\n',i)
        if end == -1:
            n1 = s.find("<<",i)
            n2 = s.find(">>",i)
        else:
            n1 = s.find("<<",i,end)
            n2 = s.find(">>",i,end)

        ok = -1 < n1 < n2

        # New in Leo 4.4.3: warn on extra brackets.
        if ok:
            for ch,j in (('<',n1+2),('>',n2+2)):
                if g.match(s,j,ch):
                    line = g.get_line(s,i)
                    g.es('dubious brackets in',line)
                    break

        return ok, n1, n2
    #@-node:ekr.20041005105605.199:hasSectionName
    #@+node:ekr.20041005105605.200:isSectionName
    # returns (flag, end). end is the index of the character after the section name.

    def isSectionName(self,s,i):

        if not g.match(s,i,"<<"):
            return False, -1
        i = g.find_on_line(s,i,">>")
        if i:
            return True, i + 2
        else:
            return False, -1
    #@-node:ekr.20041005105605.200:isSectionName
    #@+node:ekr.20041005105605.201:os and allies
    # Note:  self.outputFile may be either a fileLikeObject or a real file.
    #@+node:ekr.20041005105605.202:oblank, oblanks & otabs
    def oblank(self):
        self.os(' ')

    def oblanks (self,n):
        self.os(' ' * abs(n))

    def otabs(self,n):
        self.os('\t' * abs(n))
    #@-node:ekr.20041005105605.202:oblank, oblanks & otabs
    #@+node:ekr.20041005105605.203:onl & onl_sent
    def onl(self):

        """Write a newline to the output stream."""

        self.os(self.output_newline)

    def onl_sent(self):

        """Write a newline to the output stream, provided we are outputting sentinels."""

        if self.sentinels:
            self.onl()
    #@-node:ekr.20041005105605.203:onl & onl_sent
    #@+node:ekr.20041005105605.204:os
    def os (self,s):

        """Write a string to the output stream.

        All output produced by leoAtFile module goes here."""

        at = self

        if s and at.outputFile:
            try:
                s = g.toEncodedString(s,at.encoding,reportErrors=True)
                at.outputFile.write(s)
            except Exception:
                at.exception("exception writing:" + s)
    #@-node:ekr.20041005105605.204:os
    #@-node:ekr.20041005105605.201:os and allies
    #@+node:ekr.20041005105605.205:outputStringWithLineEndings
    # Write the string s as-is except that we replace '\n' with the proper line ending.

    def outputStringWithLineEndings (self,s):

        # Calling self.onl() runs afoul of queued newlines.
        self.os(s.replace('\n',self.output_newline))
    #@-node:ekr.20041005105605.205:outputStringWithLineEndings
    #@+node:ekr.20050506090446.1:putAtFirstLines
    def putAtFirstLines (self,s):

        '''Write any @firstlines from string s.
        These lines are converted to @verbatim lines,
        so the read logic simply ignores lines preceding the @+leo sentinel.'''

        at = self ; tag = "@first"

        i = 0
        while g.match(s,i,tag):
            i += len(tag)
            i = g.skip_ws(s,i)
            j = i
            i = g.skip_to_end_of_line(s,i)
            # Write @first line, whether empty or not
            line = s[j:i]
            at.os(line) ; at.onl()
            i = g.skip_nl(s,i)
    #@-node:ekr.20050506090446.1:putAtFirstLines
    #@+node:ekr.20050506090955:putAtLastLines
    def putAtLastLines (self,s):

        '''Write any @last lines from string s.
        These lines are converted to @verbatim lines,
        so the read logic simply ignores lines following the @-leo sentinel.'''

        at = self ; tag = "@last"

        # Use g.splitLines to preserve trailing newlines.
        lines = g.splitLines(s)
        n = len(lines) ; j = k = n - 1

        # Scan backwards for @last directives.
        while j >= 0:
            line = lines[j]
            if g.match(line,0,tag): j -= 1
            elif not line.strip():
                j -= 1
            else: break

        # Write the @last lines.
        for line in lines[j+1:k+1]:
            if g.match(line,0,tag):
                i = len(tag) ; i = g.skip_ws(line,i)
                at.os(line[i:])
    #@-node:ekr.20050506090955:putAtLastLines
    #@+node:ekr.20071117152308:putBuffered
    def putBuffered (self,s):

        '''Put s, converting all tabs to blanks as necessary.'''

        if not s: return

        w = self.tab_width
        if w < 0:
            result = []
            lines = s.split('\n')
            for line in lines:
                line2 = [] ; j = 0
                for ch in line:
                    j += 1
                    if ch == '\t':
                        w2 = g.computeWidth(s[:j],w)
                        w3 = (abs(w) - (w2 % abs(w)))
                        line2.append(' ' * w3)
                    else:
                        line2.append(ch)
                result.append(''.join(line2))
            s = '\n'.join(result)

        self.os(s)
    #@-node:ekr.20071117152308:putBuffered
    #@+node:ekr.20041005105605.206:putDirective  (handles @delims,@comment,@language) 4.x
    #@+at 
    #@nonl
    # It is important for PHP and other situations that @first and @last 
    # directives get translated to verbatim lines that do _not_ include what 
    # follows the @first & @last directives.
    #@-at
    #@@c

    def putDirective(self,s,i):

        """Output a sentinel a directive or reference s."""

        tag = "@delims"
        assert(i < len(s) and s[i] == '@')
        k = i
        j = g.skip_to_end_of_line(s,i)
        directive = s[i:j]

        if g.match_word(s,k,"@delims"):
            #@        << handle @delims >>
            #@+node:ekr.20041005105605.207:<< handle @delims >>
            # Put a space to protect the last delim.
            self.putSentinel(directive + " ") # 10/23/02: put @delims, not @@delims

            # Skip the keyword and whitespace.
            j = i = g.skip_ws(s,k+len(tag))

            # Get the first delim.
            while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
                i += 1
            if j < i:
                self.startSentinelComment = s[j:i]
                # Get the optional second delim.
                j = i = g.skip_ws(s,i)
                while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
                    i += 1
                self.endSentinelComment = g.choose(j<i, s[j:i], "")
            else:
                self.writeError("Bad @delims directive")
            #@-node:ekr.20041005105605.207:<< handle @delims >>
            #@nl
        elif g.match_word(s,k,"@language"):
            #@        << handle @language >>
            #@+node:ekr.20041005105605.208:<< handle @language >>
            self.putSentinel("@" + directive)

            if 0: # Bug fix: Leo 4.4.1
                # Do not scan the @language directive here!
                # These ivars have already been scanned by the init code.

                # Skip the keyword and whitespace.
                i = k + len("@language")
                i = g.skip_ws(s,i)
                j = g.skip_c_id(s,i)
                language = s[i:j]

                delim1,delim2,delim3 = g.set_delims_from_language(language)

                # g.trace(delim1,delim2,delim3)

                # Returns a tuple (single,start,end) of comment delims
                if delim1:
                    self.startSentinelComment = delim1
                    self.endSentinelComment = ""
                elif delim2 and delim3:
                    self.startSentinelComment = delim2
                    self.endSentinelComment = delim3
                else:
                    line = g.get_line(s,i)
                    g.es("ignoring bad @language directive:",line,color="blue")
            #@-node:ekr.20041005105605.208:<< handle @language >>
            #@nl
        elif g.match_word(s,k,"@comment"):
            #@        << handle @comment >>
            #@+node:ekr.20041005105605.209:<< handle @comment >>
            self.putSentinel("@" + directive)

            if 0: # Bug fix: Leo 4.4.1
                # Do not scan the @comment directive here!
                # These ivars have already been scanned by the init code.

                # g.trace(delim1,delim2,delim3)

                j = g.skip_line(s,i)
                line = s[i:j]
                delim1,delim2,delim3 = g.set_delims_from_string(line)

                # Returns a tuple (single,start,end) of comment delims
                if delim1:
                    self.startSentinelComment = delim1
                    self.endSentinelComment = None
                elif delim2 and delim3:
                    self.startSentinelComment = delim2
                    self.endSentinelComment = delim3
                else:
                    g.es("ignoring bad @comment directive:",line,color="blue")
            #@-node:ekr.20041005105605.209:<< handle @comment >>
            #@nl
        elif g.match_word(s,k,"@last"):
            self.putSentinel("@@last") # 10/27/03: Convert to an verbatim line _without_ anything else.
        elif g.match_word(s,k,"@first"):
            self.putSentinel("@@first") # 10/27/03: Convert to an verbatim line _without_ anything else.
        else:
            self.putSentinel("@" + directive)

        i = g.skip_line(s,k)
        return i
    #@-node:ekr.20041005105605.206:putDirective  (handles @delims,@comment,@language) 4.x
    #@+node:ekr.20041005105605.210:putIndent
    def putIndent(self,n):

        """Put tabs and spaces corresponding to n spaces, assuming that we are at the start of a line."""

        if n != 0:
            w = self.tab_width
            if w > 1:
                q,r = divmod(n,w) 
                self.otabs(q) 
                self.oblanks(r)
            else:
                self.oblanks(n)
    #@-node:ekr.20041005105605.210:putIndent
    #@+node:ekr.20041005105605.211:putInitialComment
    def putInitialComment (self):

        c = self.c
        s2 = c.config.output_initial_comment
        if s2:
            lines = string.split(s2,"\\n")
            for line in lines:
                line = line.replace("@date",time.asctime())
                if len(line)> 0:
                    self.putSentinel("@comment " + line)
    #@+node:ekr.20041005105605.212:replaceTargetFileIfDifferent
    def replaceTargetFileIfDifferent (self):

        '''Create target file as follows:
        1. If target file does not exist, rename output file to target file.
        2. If target file is identical to output file, remove the output file.
        3. If target file is different from output file,
           remove target file, then rename output file to be target file.'''

        assert(self.outputFile is None)

        self.fileChangedFlag = False

        if self.toString: return self.fileChangedFlag

        if g.os_path_exists(self.targetFileName):
            if (
                #@            << files are identical >>
                #@+node:ekr.20050104131343:<< files are identical >>
                self.compareFiles(
                    self.outputFileName,
                    self.targetFileName,
                    not self.explicitLineEnding)
                #@-node:ekr.20050104131343:<< files are identical >>
                #@nl
            ):
                self.remove(self.outputFileName)
                g.es('unchanged:',self.shortFileName)
                return False
            else:
                #@            << report if the files differ only in line endings >>
                #@+node:ekr.20041019090322:<< report if the files differ only in line endings >>
                if (
                    self.explicitLineEnding and
                    self.compareFiles(
                        self.outputFileName,
                        self.targetFileName,
                        ignoreLineEndings=True)):

                    g.es("correcting line endings in:",self.targetFileName,color="blue")
                #@-node:ekr.20041019090322:<< report if the files differ only in line endings >>
                #@nl
                mode = self.stat(self.targetFileName)
                ok = self.rename(self.outputFileName,self.targetFileName,mode)
                if ok:
                    g.es('wrote:    ',self.shortFileName)
                    self.fileChangedFlag = True
                return True # bwm
        else:
            # Rename the output file.
            ok = self.rename(self.outputFileName,self.targetFileName)
            if ok:
                g.es('created:  ',self.targetFileName)
                self.fileChangedFlag = True
            return False
    #@-node:ekr.20041005105605.212:replaceTargetFileIfDifferent
    #@-node:ekr.20041005105605.211:putInitialComment
    #@+node:ekr.20041005105605.216:warnAboutOrpanAndIgnoredNodes
    # Called from writeOpenFile.

    def warnAboutOrphandAndIgnoredNodes (self):

        # Always warn, even when language=="cweb"
        at = self ; root = at.root

        for p in root.self_and_subtree_iter():
            if not p.v.t.isVisited(): # Check tnode bit, not vnode bit.
                at.writeError("Orphan node:  " + p.headString())
                if p.hasParent():
                    g.es("parent node:",p.parent().headString(),color="blue")
                if not at.thinFile and p.isAtIgnoreNode():
                    at.writeError("@ignore node: " + p.headString())

        if at.thinFile:
            p = root.copy() ; after = p.nodeAfterTree()
            while p and p != after:
                if p.isAtAllNode():
                    p.moveToNodeAfterTree()
                else:
                    if p.isAtIgnoreNode():
                        at.writeError("@ignore node: " + p.headString())
                    p.moveToThreadNext()
    #@-node:ekr.20041005105605.216:warnAboutOrpanAndIgnoredNodes
    #@+node:ekr.20041005105605.217:writeError
    def writeError(self,message=None):

        if self.errors == 0:
            g.es_error("errors writing: " + self.targetFileName)

        self.error(message)
        self.root.setOrphan()
        self.root.setDirty()
    #@-node:ekr.20041005105605.217:writeError
    #@+node:ekr.20041005105605.218:writeException
    def writeException (self,root=None):

        g.es("exception writing:",self.targetFileName,color="red")
        g.es_exception()

        if self.outputFile:
            self.outputFile.flush()
            self.outputFile.close()
            self.outputFile = None

        if self.outputFileName != None:
            try: # Just delete the temp file.
                os.remove(self.outputFileName)
            except Exception:
                g.es("exception deleting:",self.outputFileName,color="red")
                g.es_exception()

        if root:
            # Make sure we try to rewrite this file.
            root.setOrphan()
            root.setDirty()
    #@-node:ekr.20041005105605.218:writeException
    #@-node:ekr.20041005105605.196:Writing 4.x utils...
    #@-node:ekr.20041005105605.132:Writing...
    #@+node:ekr.20041005105605.219:Uilites... (atFile)
    #@+node:ekr.20041005105605.220:atFile.error
    def error(self,message):

        if message:
            self.printError(message)

        self.errors += 1

        # g.trace('errors',self.errors)
    #@-node:ekr.20041005105605.220:atFile.error
    #@+node:ekr.20051219122720:atFile.forceGnxOnPosition
    def forceGnxOnPosition (self,p):

        # g.trace(p.headString())

        self._forcedGnxPositionList.append(p.v)
    #@-node:ekr.20051219122720:atFile.forceGnxOnPosition
    #@+node:ekr.20050206085258:atFile.printError
    def printError (self,message):

        '''Print an error message that may contain non-ascii characters.'''

        if self.errors == 0:
            g.es_error(message)
        else:
            try:
                print message
            except UnicodeError:
                print g.toEncodedString(message,'ascii')
    #@+node:ekr.20070621091727:@@test printError
    # We typically don't enable this test.

    if g.unitTesting:

        c,p = g.getTestVars() # Optional: prevents pychecker warnings.
        at = c.atFileCommands
        at.errors = 0
        at.printError(
            "test of printError: Ᾱ(U+1FB9: Greek Capital Letter Alpha With Macron)")
    #@-node:ekr.20070621091727:@@test printError
    #@-node:ekr.20050206085258:atFile.printError
    #@+node:ekr.20041005105605.222:atFile.scanAllDirectives
    #@+at 
    #@nonl
    # Once a directive is seen, no other related directives in nodes further 
    # up the tree have any effect.  For example, if an @color directive is 
    # seen in node p, no @color or @nocolor directives are examined in any 
    # ancestor of p.
    # 
    # This code is similar to Commands.scanAllDirectives, but it has been 
    # modified for use by the atFile class.
    #@-at
    #@@c

    def scanAllDirectives(self,p,scripting=False,importing=False,reading=False,forcePythonSentinels=False):

        """Scan position p and p's ancestors looking for directives,
        setting corresponding atFile ivars.
        """

        # __pychecker__ = '--maxlines=400'
        # g.stat()

        c = self.c
        #@    << Set ivars >>
        #@+node:ekr.20041005105605.223:<< Set ivars >>
        self.page_width = self.c.page_width
        self.tab_width  = self.c.tab_width

        self.default_directory = None # 8/2: will be set later.

        if c.target_language:
            c.target_language = c.target_language.lower() # 6/20/05
        delim1, delim2, delim3 = g.set_delims_from_language(c.target_language)
        self.language = c.target_language

        self.encoding = c.config.default_derived_file_encoding
        self.output_newline = g.getOutputNewline(c=self.c) # Init from config settings.
        #@-node:ekr.20041005105605.223:<< Set ivars >>
        #@nl
        #@    << Set path from @file node >>
        #@+node:ekr.20041005105605.224:<< Set path from @file node >> in scanDirectory in leoGlobals.py
        # An absolute path in an @file node over-rides everything else.
        # A relative path gets appended to the relative path by the open logic.

        name = p.anyAtFileNodeName() # 4/28/04

        theDir = g.choose(name,g.os_path_dirname(name),None)

        if theDir and len(theDir) > 0 and g.os_path_isabs(theDir):
            if g.os_path_exists(theDir):
                self.default_directory = theDir
            else: # 9/25/02
                self.default_directory = g.makeAllNonExistentDirectories(theDir,c=c)
                if not self.default_directory:
                    self.error("Directory \"%s\" does not exist" % theDir)
        #@-node:ekr.20041005105605.224:<< Set path from @file node >> in scanDirectory in leoGlobals.py
        #@nl
        old = {}
        for p in p.self_and_parents_iter():
            theDict = g.get_directives_dict(p)
            #@        << Test for @path >>
            #@+node:ekr.20041005105605.225:<< Test for @path >> (atFile.scanAllDirectives)
            # We set the current director to a path so future writes will go to that directory.

            if not self.default_directory and not old.has_key("path") and theDict.has_key("path"):

                path = theDict["path"]
                path = g.computeRelativePath(path)
                if path and len(path) > 0:
                    base = g.getBaseDirectory(c) # returns "" on error.
                    path = g.os_path_join(base,path)
                    if g.os_path_isabs(path):
                        #@            << handle absolute path >>
                        #@+node:ekr.20041005105605.227:<< handle absolute path >>
                        # path is an absolute path.

                        if g.os_path_exists(path):
                            self.default_directory = path
                        else:
                            self.default_directory = g.makeAllNonExistentDirectories(path,c=c)
                            if not self.default_directory:
                                self.error("invalid @path: %s" % path)
                        #@-node:ekr.20041005105605.227:<< handle absolute path >>
                        #@nl
                    else:
                        self.error("ignoring bad @path: %s" % path)
                else:
                    self.error("ignoring empty @path")
            #@-node:ekr.20041005105605.225:<< Test for @path >> (atFile.scanAllDirectives)
            #@nl
            #@        << Test for @encoding >>
            #@+node:ekr.20041005105605.228:<< Test for @encoding >>
            if not old.has_key("encoding") and theDict.has_key("encoding"):

                e = g.scanAtEncodingDirective(theDict)
                if e:
                    self.encoding = e
            #@-node:ekr.20041005105605.228:<< Test for @encoding >>
            #@nl
            #@        << Test for @comment and @language >>
            #@+node:ekr.20041005105605.229:<< Test for @comment and @language >>
            # 10/17/02: @language and @comment may coexist in @file trees.
            # For this to be effective the @comment directive should follow the @language directive.

            # 1/23/05: Any previous @language or @comment prevents processing up the tree.
            # This code is now like the code in tangle.scanAlldirectives.

            if old.has_key("comment") or old.has_key("language"):
                pass # Do nothing more.

            elif theDict.has_key("comment"):
                z = theDict["comment"]
                delim1, delim2, delim3 = g.set_delims_from_string(z)

            elif theDict.has_key("language"):
                z = theDict["language"]
                self.language,delim1,delim2,delim3 = g.set_language(z,0)
            #@-node:ekr.20041005105605.229:<< Test for @comment and @language >>
            #@nl
            #@        << Test for @header and @noheader >>
            #@+node:ekr.20041005105605.230:<< Test for @header and @noheader >>
            # EKR: 10/10/02: perform the sames checks done by tangle.scanAllDirectives.
            if theDict.has_key("header") and theDict.has_key("noheader"):
                g.es("conflicting @header and @noheader directives")
            #@-node:ekr.20041005105605.230:<< Test for @header and @noheader >>
            #@nl
            #@        << Test for @lineending >>
            #@+node:ekr.20041005105605.231:<< Test for @lineending >>
            if not old.has_key("lineending") and theDict.has_key("lineending"):

                lineending = g.scanAtLineendingDirective(theDict)
                if lineending:
                    self.explicitLineEnding = True
                    self.output_newline = lineending
            #@-node:ekr.20041005105605.231:<< Test for @lineending >>
            #@nl
            #@        << Test for @pagewidth >>
            #@+node:ekr.20041005105605.232:<< Test for @pagewidth >>
            if theDict.has_key("pagewidth") and not old.has_key("pagewidth"):

                w = g.scanAtPagewidthDirective(theDict,issue_error_flag=True)
                if w and w > 0:
                    self.page_width = w
            #@-node:ekr.20041005105605.232:<< Test for @pagewidth >>
            #@nl
            #@        << Test for @tabwidth >>
            #@+node:ekr.20041005105605.233:<< Test for @tabwidth >>
            if theDict.has_key("tabwidth") and not old.has_key("tabwidth"):

                w = g.scanAtTabwidthDirective(theDict,issue_error_flag=True)
                if w and w != 0:
                    self.tab_width = w
            #@-node:ekr.20041005105605.233:<< Test for @tabwidth >>
            #@nl
            old.update(theDict)
        #@    << Set current directory >>
        #@+node:ekr.20041005105605.234:<< Set current directory >> (atFile.scanAllDirectives)
        # This code is executed if no valid absolute path was specified in the @file node or in an @path directive.

        if c.frame and not self.default_directory:
            base = g.getBaseDirectory(c) # returns "" on error.
            for theDir in (c.tangle_directory,c.frame.openDirectory,c.openDirectory):
                if theDir and len(theDir) > 0:
                    theDir = g.os_path_join(base,theDir)
                    if g.os_path_isabs(theDir): # Errors may result in relative or invalid path.
                        if g.os_path_exists(theDir):
                            self.default_directory = theDir ; break
                        else: # 9/25/02
                            self.default_directory = g.makeAllNonExistentDirectories(theDir,c=c)

        if not self.default_directory and not scripting and not importing:
            # This should never happen: c.openDirectory should be a good last resort.
            g.trace()
            self.error("No absolute directory specified anywhere.")
            self.default_directory = ""
        #@-node:ekr.20041005105605.234:<< Set current directory >> (atFile.scanAllDirectives)
        #@nl
        if not importing and not reading:
            # 5/19/04: don't override comment delims when reading!
            #@        << Set comment strings from delims >>
            #@+node:ekr.20041005105605.235:<< Set comment strings from delims >>
            if forcePythonSentinels:
                # Force Python language.
                delim1,delim2,delim3 = g.set_delims_from_language("python")
                self.language = "python"

            # Use single-line comments if we have a choice.
            # delim1,delim2,delim3 now correspond to line,start,end
            if delim1:
                self.startSentinelComment = delim1
                self.endSentinelComment = "" # Must not be None.
            elif delim2 and delim3:
                self.startSentinelComment = delim2
                self.endSentinelComment = delim3
            else: # Emergency!
                # assert(0)
                g.es("unknown language: using Python comment delimiters")
                g.es("c.target_language:",c.target_language)
                g.es('','delim1,delim2,delim3:','',delim1,'',delim2,'',delim3)
                self.startSentinelComment = "#" # This should never happen!
                self.endSentinelComment = ""

            # g.trace(repr(self.startSentinelComment),repr(self.endSentinelComment))
            #@-node:ekr.20041005105605.235:<< Set comment strings from delims >>
            #@nl
        # For unit testing.
        return {
            "encoding"  : self.encoding,
            "language"  : self.language,
            "lineending": self.output_newline,
            "pagewidth" : self.page_width,
            "path"      : self.default_directory,
            "tabwidth"  : self.tab_width,
        }
    #@-node:ekr.20041005105605.222:atFile.scanAllDirectives
    #@+node:ekr.20041005105605.236:atFile.scanDefaultDirectory
    def scanDefaultDirectory(self,p,importing=False):

        """Set default_directory ivar by looking for @path directives."""

        at = self ; c = at.c
        at.default_directory = None
        #@    << Set path from @file node >>
        #@+node:ekr.20041005105605.237:<< Set path from @file node >>
        # An absolute path in an @file node over-rides everything else.
        # A relative path gets appended to the relative path by the open logic.

        name = p.anyAtFileNodeName()

        theDir = g.choose(name,g.os_path_dirname(name),None)

        # g.trace('at.default_directory',at.default_directory)
        # g.trace('theDir',theDir)

        if theDir and g.os_path_isabs(theDir):
            if g.os_path_exists(theDir):
                at.default_directory = theDir
            else:
                at.default_directory = g.makeAllNonExistentDirectories(theDir,c=c)
                if not at.default_directory:
                    at.error("Directory \"%s\" does not exist" % theDir)
        #@-node:ekr.20041005105605.237:<< Set path from @file node >>
        #@nl
        if at.default_directory:
            return

        for p in p.self_and_parents_iter():
            theDict = g.get_directives_dict(p)
            if theDict.has_key("path"):
                #@            << handle @path >>
                #@+node:ekr.20041005105605.238:<< handle @path >>
                # We set the current director to a path so future writes will go to that directory.

                path = theDict["path"]
                path = g.computeRelativePath (path)

                if path:
                    base = g.getBaseDirectory(c) # returns "" on error.
                    path = g.os_path_join(base,path)

                    if g.os_path_isabs(path):
                        #@        << handle absolute path >>
                        #@+node:ekr.20041005105605.240:<< handle absolute path >>
                        # path is an absolute path.

                        if g.os_path_exists(path):
                            at.default_directory = path
                        else:
                            at.default_directory = g.makeAllNonExistentDirectories(path,c=c)
                            if not at.default_directory:
                                at.error("invalid @path: %s" % path)
                        #@-node:ekr.20041005105605.240:<< handle absolute path >>
                        #@nl
                    else:
                        at.error("ignoring bad @path: %s" % path)
                else:
                    at.error("ignoring empty @path")
                #@-node:ekr.20041005105605.238:<< handle @path >>
                #@nl
                return

        #@    << Set current directory >>
        #@+node:ekr.20041005105605.241:<< Set current directory >>
        # This code is executed if no valid absolute path was specified in the @file node or in an @path directive.

        assert(not at.default_directory)

        if c.frame :
            base = g.getBaseDirectory(c) # returns "" on error.
            for theDir in (c.tangle_directory,c.frame.openDirectory,c.openDirectory):
                if theDir and len(theDir) > 0:
                    theDir = g.os_path_join(base,theDir)
                    if g.os_path_isabs(theDir): # Errors may result in relative or invalid path.
                        if g.os_path_exists(theDir):
                            at.default_directory = theDir ; break
                        else:
                            at.default_directory = g.makeAllNonExistentDirectories(theDir,c=c)
        #@-node:ekr.20041005105605.241:<< Set current directory >>
        #@nl
        if not at.default_directory and not importing:
            # This should never happen: c.openDirectory should be a good last resort.
            at.error("No absolute directory specified anywhere.")
            at.default_directory = ""
    #@-node:ekr.20041005105605.236:atFile.scanDefaultDirectory
    #@+node:ekr.20070529083836:cleanLines
    def cleanLines (self,p,s):

        '''Return a copy of s, with all trailing whitespace removed.
        If a change was made, update p's body text and set c dirty.'''

        c = self.c ; cleanLines = [] ; changed = False
        lines = g.splitLines(s)
        for line in lines:
            if line.strip():
                cleanLines.append(line)
            elif line.endswith('\n'):
                cleanLines.append('\n')
                if line != '\n': changed = True
            else:
                cleanLines.append('')
                if line != '': changed = True
        s = g.joinLines(cleanLines)

        if changed and not g.app.unitTesting:
            p.setTnodeText(s)
            c.setBodyString(p,s)
            c.setChanged(True)

        return s
    #@nonl
    #@-node:ekr.20070529083836:cleanLines
    #@+node:ekr.20041005105605.221:exception
    def exception (self,message):

        self.error(message)
        g.es_exception()
    #@-node:ekr.20041005105605.221:exception
    #@+node:ekr.20050104131929:file operations...
    #@+at 
    #@nonl
    # The difference, if any, between these methods and the corresponding 
    # g.utils_x
    # functions is that these methods may call self.error.
    #@-at
    #@+node:ekr.20050104131820:chmod
    def chmod (self,fileName,mode):

        # Do _not_ call self.error here.
        return g.utils_chmod(fileName,mode)
    #@-node:ekr.20050104131820:chmod
    #@+node:ekr.20050104131929.1:atFile.rename
    #@<< about os.rename >>
    #@+node:ekr.20050104131929.2:<< about os.rename >>
    #@+at 
    #@nonl
    # Here is the Python 2.4 documentation for rename (same as Python 2.3)
    # 
    # Rename the file or directory src to dst.  If dst is a directory, OSError 
    # will be raised.
    # 
    # On Unix, if dst exists and is a file, it will be removed silently if the 
    # user
    # has permission. The operation may fail on some Unix flavors if src and 
    # dst are
    # on different filesystems. If successful, the renaming will be an atomic
    # operation (this is a POSIX requirement).
    # 
    # On Windows, if dst already exists, OSError will be raised even if it is 
    # a file;
    # there may be no way to implement an atomic rename when dst names an 
    # existing
    # file.
    #@-at
    #@-node:ekr.20050104131929.2:<< about os.rename >>
    #@nl

    def rename (self,src,dst,mode=None,verbose=True):

        '''remove dst if it exists, then rename src to dst.

        Change the mode of the renamed file if mode is given.

        Return True if all went well.'''

        c = self.c
        head,junk=g.os_path_split(dst)
        if head and len(head) > 0:
            g.makeAllNonExistentDirectories(head,c=c)

        if g.os_path_exists(dst):
            if not self.remove(dst,verbose=verbose):
                return False

        try:
            os.rename(src,dst)
            if mode != None:
                self.chmod(dst,mode)
            return True
        except Exception:
            if verbose:
                self.error("exception renaming: %s to: %s" % (
                    self.outputFileName,self.targetFileName))
                g.es_exception()
            return False
    #@-node:ekr.20050104131929.1:atFile.rename
    #@+node:ekr.20050104132018:remove
    def remove (self,fileName,verbose=True):

        try:
            os.remove(fileName)
            return True
        except Exception:
            if verbose:
                self.error("exception removing: %s" % fileName)
                g.es_exception()
            return False
    #@-node:ekr.20050104132018:remove
    #@+node:ekr.20050104132026:stat
    def stat (self,fileName):

        '''Return the access mode of named file, removing any setuid, setgid, and sticky bits.'''

        # Do _not_ call self.error here.
        return g.utils_stat(fileName)
    #@-node:ekr.20050104132026:stat
    #@-node:ekr.20050104131929:file operations...
    #@+node:ekr.20041005105605.242:scanForClonedSibs (reading & writing)
    def scanForClonedSibs (self,v):

        """Scan the siblings of vnode v looking for clones of v.
        Return the number of cloned sibs and n where p is the n'th cloned sibling."""

        clonedSibs = 0 # The number of cloned siblings of p, including p.
        thisClonedSibIndex = 0 # Position of p in list of cloned siblings.

        if v and v.isCloned():
            sib = v
            while sib.back():
                sib = sib.back()
            while sib:
                if sib.t == v.t:
                    clonedSibs += 1
                    if sib == v:
                        thisClonedSibIndex = clonedSibs
                sib = sib.next()

        # g.trace(clonedSibs,thisClonedSibIndex)

        return clonedSibs,thisClonedSibIndex
    #@-node:ekr.20041005105605.242:scanForClonedSibs (reading & writing)
    #@+node:ekr.20041005105605.243:sentinelName
    # Returns the name of the sentinel for warnings.

    def sentinelName(self, kind):

        at = self

        sentinelNameDict = {
            at.noSentinel:    "<no sentinel>",
            at.startAt:       "@+at",     at.endAt:     "@-at",
            at.startBody:     "@+body",   at.endBody:   "@-body", # 3.x only.
            at.startDoc:      "@+doc",    at.endDoc:    "@-doc",
            at.startLeo:      "@+leo",    at.endLeo:    "@-leo",
            at.startNode:     "@+node",   at.endNode:   "@-node",
            at.startOthers:   "@+others", at.endOthers: "@-others",
            at.startAll:      "@+all",    at.endAll:    "@-all", # 4.x
            at.startMiddle:   "@+middle", at.endMiddle: "@-middle", # 4.x
            at.startAfterRef: "@afterref", # 4.x
            at.startComment:  "@comment",
            at.startDelims:   "@delims",
            at.startDirective:"@@",
            at.startNl:       "@nl",   # 4.x
            at.startNonl:     "@nonl", # 4.x
            at.startClone:    "@clone", # 4.2
            at.startRef:      "@<<",
            at.startVerbatim: "@verbatim",
            at.startVerbatimAfterRef: "@verbatimAfterRef" } # 3.x only.

        return sentinelNameDict.get(kind,"<unknown sentinel!>")
    #@-node:ekr.20041005105605.243:sentinelName
    #@-node:ekr.20041005105605.219:Uilites... (atFile)
    #@-others
#@-node:ekr.20041005105605.1:@thin leoAtFile.py
#@-leo

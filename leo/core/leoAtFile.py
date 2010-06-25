# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20041005105605.1:@thin leoAtFile.py
#@@first
    # Needed because of unicode characters in tests.

"""Classes to read and write @file nodes."""

#@@language python
#@@tabwidth -4
#@@pagewidth 60

new_read = False
    # Marks code that reads simplified sentinels.
    # Eventually, Leo will always read simplified sentinels.
new_write = False
    # Enable writing simplified sentinels.

#@<< imports >>
#@+node:ekr.20041005105605.2:<< imports >>
import leo.core.leoGlobals as g

if g.app and g.app.use_psyco:
    # print("enabled psyco classes",__file__)
    try: from psyco.classes import *
    except ImportError: pass

import leo.core.leoNodes as leoNodes

# import hashlib
import os
import sys
import time

#@-node:ekr.20041005105605.2:<< imports >>
#@nl

class atFile:

    """The class implementing the atFile subcommander."""

    #@    << define class constants >>
    #@+node:ekr.20041005105605.5:<< define class constants >>
    # These constants must be global to this module
    # because they are shared by several classes.

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

    # New in 4.8.
    endRef         = 84 # @-<<
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
    #@+node:ekr.20041005105605.7:at.Birth & init
    #@+node:ekr.20041005105605.8:atFile.__init__
    def __init__(self,c):

        # **Warning**: all these ivars must **also** be inited in initCommonIvars.
        self.c = c
        self.debug = False
        self.fileCommands = c.fileCommands
        self.testing = False # True: enable additional checks.
        self.errors = 0 # Make sure at.error() works even when not inited.

        # User options.
        self.checkPythonCodeOnWrite = c.config.getBool(
            'check-python-code-on-write',default=True)
        self.underindentEscapeString = c.config.getString(
            'underindent-escape-string') or '\\-'

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
            self.startVerbatimAfterRef: self.ignoreOldSentinel,
            # New 4.8 sentinels
            self.endRef: self.readEndRef,
        }
        #@-node:ekr.20041005105605.9:<< define the dispatch dictionary used by scanText4 >>
        #@nl
    #@-node:ekr.20041005105605.8:atFile.__init__
    #@+node:ekr.20041005105605.10:initCommonIvars
    def initCommonIvars (self):

        """Init ivars common to both reading and writing.

        The defaults set here may be changed later."""

        c = self.c

        if self.testing:
            # Save "permanent" ivars
            fileCommands = self.fileCommands
            dispatch_dict = self.dispatch_dict
            # Clear all ivars.
            g.clearAllIvars(self)
            # Restore permanent ivars
            self.testing = True
            self.c = c
            self.fileCommands = fileCommands
            self.dispatch_dict = dispatch_dict

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
        self.root = None # The root (a position) of tree being read or written.
        self.root_seen = False # True: root vnode has been handled in this file.
        self.toString = False # True: sring-oriented read or write.
        self.writing_to_shadow_directory = False
        #@nonl
        #@-node:ekr.20041005105605.12:<< init common ivars >>
        #@nl
    #@-node:ekr.20041005105605.10:initCommonIvars
    #@+node:ekr.20041005105605.13:initReadIvars
    def initReadIvars(self,root,fileName,
        importFileName=None,
        perfectImportRoot=None,
        atShadow=False,
    ):

        importing = importFileName is not None

        self.initCommonIvars()

        #@    << init ivars for reading >>
        #@+node:ekr.20041005105605.14:<< init ivars for reading >>
        self.atAllFlag = False # True if @all seen.
        self.cloneSibCount = 0
            # n > 1: Make sure n cloned sibs exists at next @+node sentinel
        self.correctedLines = 0
        self.docOut = [] # The doc part being accumulated.
        self.done = False # True when @-leo seen.
        self.endSentinelStack = []
        self.endSentinelNodeStack = [] # Not used in the old scheme.
            # In the simplified sentinel scheme, these two stacks
            # have the same size. In effect, they form a single stack.
            # The old scheme creates entries for +node sentinels.
            # The new scheme does not.
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
        self.readVersion = '' # New in Leo 4.8: "4" or "5" for new-style thin files.
        self.rootSeen = False
        self.tnodeList = []
            # Needed until old-style @file nodes are no longer supported.
        self.tnodeListIndex = 0
        self.v = None
        self.tStack = []
        self.thinNodeStack = []
            # Used by createThinChild4.
            # Entries are vnodes.
            # This stack and the indentStack always have the same number of entries.
            # In effect, they form a single stack.
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
        self.thinFile = False # 2010/01/22: was thinFile
        self.atShadow = atShadow
    #@-node:ekr.20041005105605.13:initReadIvars
    #@+node:ekr.20041005105605.15:initWriteIvars
    def initWriteIvars(self,root,targetFileName,
        atAuto=False,
        atEdit=False,
        atShadow=False,
        nosentinels=False,
        thinFile=False,
        scriptWrite=False,
        toString=False,
        forcePythonSentinels=None,
    ):

        self.initCommonIvars()
        #@    << init ivars for writing >>
        #@+node:ekr.20041005105605.16:<< init ivars for writing >>>
        #@+at
        # When tangling, we first write to a temporary 
        # output file. After tangling is
        # temporary file. Otherwise we delete the old 
        # target file and rename the
        # temporary file to be the target file.
        #@-at
        #@@c

        self.docKind = None
        self.explicitLineEnding = False
            # True: an @lineending directive specifies the ending.
        self.fileChangedFlag = False # True: the file has actually been updated.
        self.atAuto = atAuto
        self.atEdit = atEdit
        self.atShadow = atShadow
        self.shortFileName = "" # short version of file name used for messages.
        self.thinFile = False
        self.force_newlines_in_at_nosent_bodies = self.c.config.getBool(
            'force_newlines_in_at_nosent_bodies')

        if toString:
            self.outputFile = g.fileLikeObject()
            self.stringOutput = ""
            self.targetFileName = self.outputFileName = "<string-file>"
        else:
            self.outputFile = None # The temporary output file.
            self.stringOutput = None
            self.targetFileName = self.outputFileName = g.u('')
        #@-node:ekr.20041005105605.16:<< init ivars for writing >>>
        #@nl

        if forcePythonSentinels is None:
            forcePythonSentinels = scriptWrite

        if root:
            self.scanAllDirectives(root,
                scripting=scriptWrite,
                forcePythonSentinels=forcePythonSentinels,
                issuePathWarning=True)

        # g.trace(forcePythonSentinels,
        #    self.startSentinelComment,self.endSentinelComment)

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
            if hasattr(self.root.v,'tnodeList'):
                delattr(self.root.v,'tnodeList')
            self.root.v._p_changed = True
    #@-node:ekr.20041005105605.15:initWriteIvars
    #@-node:ekr.20041005105605.7:at.Birth & init
    #@+node:ekr.20041005105605.17:at.Reading
    #@+node:ekr.20041005105605.18:Reading (top level)
    #@+at
    # 
    # All reading happens in the readOpenFile logic, so 
    # plugins should need to
    # override only this method.
    #@-at
    #@+node:ekr.20070919133659:checkDerivedFile (atFile)
    def checkDerivedFile (self, event=None):

        at = self ; c = at.c ; p = c.p

        if not p.isAtFileNode() and not p.isAtThinFileNode():
            return g.es('Please select an @thin or @file node',color='red')

        fn = p.anyAtFileNodeName()
        path = g.os_path_dirname(c.mFileName)
        fn = g.os_path_finalize_join(g.app.loadDir,path,fn)
        if not g.os_path_exists(fn):
            return g.es_print('file not found: %s' % (fn),color='red')

        s,e = g.readFileIntoString(fn)
        if s is None: return

        # Create a dummy, unconnected, vnode as the root.
        root_v = leoNodes.vnode(context=c)
        root = leoNodes.position(root_v)
        theFile = g.fileLikeObject(fromString=s)
        # 2010/01/22: readOpenFiles now determines whether a file is thin or not.
        at.initReadIvars(root,fn)
        if at.errors: return
        at.openFileForReading(fromString=s)
        if not at.inputFile: return
        at.readOpenFile(root,at.inputFile,fn)
        at.inputFile.close()
        if at.errors == 0:
            g.es_print('check-derived-file passed',color='blue')
    #@-node:ekr.20070919133659:checkDerivedFile (atFile)
    #@+node:ekr.20041005105605.19:openFileForReading (atFile) helper
    def openFileForReading(self,fromString=False):

        '''Open the file given by at.root.
        This will be the private file for @shadow nodes.'''

        trace = False and not g.app.unitTesting
        verbose = False
        at = self ; c = at.c

        if fromString:
            if at.atShadow:
                return at.error(
                    'can not call at.read from string for @shadow files')
            at.inputFile = g.fileLikeObject(fromString=fromString)
            fn = None
        else:
            fn = at.fullPath(self.root)
                # Returns full path, including file name.
            at.setPathUa(self.root,fn) # Remember the full path to this node.
            if trace: g.trace(fn)

            if at.atShadow:
                x = at.c.shadowController
                # readOneAtShadowNode should already have checked these.
                shadow_fn     = x.shadowPathName(fn)
                shadow_exists = g.os_path_exists(shadow_fn) and \
                    g.os_path_isfile(shadow_fn)
                if not shadow_exists:
                    g.trace('can not happen: no private file',
                        shadow_fn,g.callers())
                    return at.error(
                        'can not happen: private file does not exist: %s' % (
                            shadow_fn))
                # This method is the gateway to the shadow algorithm.
                x.updatePublicAndPrivateFiles(fn,shadow_fn)
                fn = shadow_fn

            try:
                # Open the file in binary mode to allow 0x1a in bodies & headlines.
                if trace and verbose and at.atShadow:
                    g.trace('opening %s file: %s' % (
                        g.choose(at.atShadow,'private','public'),fn))
                at.inputFile = open(fn,'rb')
                at.warnOnReadOnlyFile(fn)
            except IOError:
                at.error("can not open: '@file %s'" % (fn))
                at.inputFile = None
                fn = None

        return fn
    #@-node:ekr.20041005105605.19:openFileForReading (atFile) helper
    #@+node:ekr.20041005105605.21:read (atFile) & helpers
    def read(self,root,importFileName=None,
        fromString=None,atShadow=False,force=False
    ):

        """Read an @thin or @file tree."""

        trace = False and not g.unitTesting
        if trace: g.trace(root.h,len(root.b))
        at = self ; c = at.c
        fileName = at.initFileName(fromString,importFileName,root)
        if not fileName:
            at.error("Missing file name.  Restoring @file tree from .leo file.")
            return False
        at.initReadIvars(root,fileName,
            importFileName=importFileName,atShadow=atShadow)
        if at.errors:
            return False
        fileName = at.openFileForReading(fromString=fromString)
        if fileName and at.inputFile:
            c.setFileTimeStamp(fileName)
        else:
            return False
        root.v.at_read = True # Remember that we have read this file.

        # Get the file from the cache if possible.
        s,loaded,fileKey = c.cacher.readFile(fileName,root)
        # 2010/02/24: Never read an external file
        # with file-like sentinels from the cache.
        isFileLike = loaded and at.isFileLike(s)
        if not loaded or isFileLike:
            # if trace: g.trace('file-like file',fileName)
            force = True # Disable caching.
        if loaded and not force:
            if trace: g.trace('in cache',fileName)
            at.inputFile.close()
            root.clearDirty()
            return True
        if not g.unitTesting:
            g.es("reading:",root.h)
        if isFileLike:
            if g.unitTesting:
                if 0: print("converting @file format in",root.h)
                g.app.unitTestDict['read-convert']=True
            else:
                g.es("converting @file format in",root.h,color='red')
        root.clearVisitedInTree()
        d = at.scanAllDirectives(root,importing=at.importing,reading=True)
        thinFile = at.readOpenFile(root,at.inputFile,fileName,deleteNodes=True)
        at.inputFile.close()
        root.clearDirty() # May be set dirty below.
        if at.errors == 0:
            at.warnAboutUnvisitedNodes(root)
            at.deleteTnodeList(root)
        if at.errors == 0 and not at.importing:
            # Used by mod_labels plugin.
            self.copyAllTempBodyStringsToTnodes(root,thinFile)
        at.deleteAllTempBodyStrings()
        if isFileLike:
            # 2010/02/24: Make the root @file node dirty so it will
            # be written automatically when saving the file.
            root.setDirty()
            c.setChanged(True) # Essential, to keep dirty bit set.
        if at.errors == 0 and not isFileLike:
            c.cacher.writeFile(root,fileKey)

        if trace: g.trace('root.isDirty',root.isDirty())

        return at.errors == 0
    #@+node:ekr.20041005105605.25:deleteAllTempBodyStrings
    def deleteAllTempBodyStrings(self):

        for v in self.c.all_unique_nodes():
            if hasattr(v,"tempBodyString"):
                delattr(v,"tempBodyString")
            if hasattr(v,"tempBodyList"):
                delattr(v,"tempBodyList")
    #@-node:ekr.20041005105605.25:deleteAllTempBodyStrings
    #@+node:ekr.20100122130101.6174:deleteTnodeList
    def deleteTnodeList (self,p): # atFile method.

        '''Remove p's tnodeList.'''

        v = p.v

        if hasattr(v,"tnodeList"):

            if False: # Not an error, but a useful trace.
                s = "deleting tnodeList for " + repr(v)
                g.es_print(s,color="blue")

            delattr(v,"tnodeList")
            v._p_changed = True
    #@-node:ekr.20100122130101.6174:deleteTnodeList
    #@+node:ekr.20041005105605.22:initFileName
    def initFileName (self,fromString,importFileName,root):

        if fromString:
            fileName = "<string-file>"
        elif importFileName:
            fileName = importFileName
        elif root.isAnyAtFileNode():
            fileName = root.anyAtFileNodeName()
        else:
            fileName = None

        return fileName
    #@-node:ekr.20041005105605.22:initFileName
    #@+node:ekr.20100224050618.11547:at.isFileLike
    def isFileLike (self,s):

        '''Return True if s has file-like sentinels.'''

        trace = False and not g.unitTesting
        at = self ; tag = "@+leo"
        s = g.toUnicode(s)
        i = s.find(tag)
        if i == -1:
            if trace: g.trace('found: False',repr(s))
            return True # Don't use the cashe.
        else:
            j,k = g.getLine(s,i)
            line = s[j:k]
            valid,new_df,start,end,isThin = \
                at.parseLeoSentinel(line)
            if trace: g.trace('found: True isThin:',
                isThin,repr(line))
            return not isThin
    #@-node:ekr.20100224050618.11547:at.isFileLike
    #@+node:ekr.20071105164407:warnAboutUnvisitedNodes
    def warnAboutUnvisitedNodes (self,root):

        resurrected = 0

        for p in root.self_and_subtree():
            if not p.v.isVisited():
                g.trace('**** not visited',p.v,p.h)
                g.es('resurrected node:',p.h,color='blue')
                g.es('in file:',root.h,color='blue')
                resurrected += 1

        if resurrected:
            g.es('you may want to delete ressurected nodes')
    #@-node:ekr.20071105164407:warnAboutUnvisitedNodes
    #@-node:ekr.20041005105605.21:read (atFile) & helpers
    #@+node:ekr.20041005105605.26:readAll (atFile)
    def readAll(self,root,partialFlag=False):

        """Scan vnodes, looking for @<file> nodes to read."""

        use_tracer = False
        if use_tracer: tt = g.startTracer()

        at = self ; c = at.c
        force = partialFlag
        if partialFlag:
            # Capture the current headline only if
            # we aren't doing the initial read.
            c.endEditing() 
        anyRead = False
        p = root.copy()

        scanned_tnodes = set()

        if partialFlag: after = p.nodeAfterTree()    
        else: after = c.nullPosition()

        while p and p != after:
            gnx = p.gnx
            #skip clones
            if gnx in scanned_tnodes:
                p.moveToNodeAfterTree()
                continue
            scanned_tnodes.add(gnx)

            if not p.h.startswith('@'):
                p.moveToThreadNext()
            elif p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            elif p.isAtThinFileNode():
                anyRead = True
                at.read(p,force=force)
                p.moveToNodeAfterTree()
            elif p.isAtAutoNode():
                fileName = p.atAutoNodeName()
                at.readOneAtAutoNode (fileName,p)
                p.moveToNodeAfterTree()
            elif p.isAtEditNode():
                fileName = p.atEditNodeName()
                at.readOneAtEditNode (fileName,p)
                p.moveToNodeAfterTree()
            elif p.isAtShadowFileNode():
                fileName = p.atShadowFileNodeName()
                at.readOneAtShadowNode (fileName,p)
                p.moveToNodeAfterTree()
            elif p.isAtFileNode():
                anyRead = True
                wasOrphan = p.isOrphan()
                ok = at.read(p,force=force)
                if wasOrphan and not partialFlag and not ok:
                    # Remind the user to fix the problem.
                    p.setDirty() # Expensive, but it can't be helped.
                    c.setChanged(True)
                p.moveToNodeAfterTree()
            else: p.moveToThreadNext()
        # Clear all orphan bits.
        for v in c.all_unique_nodes():
            v.clearOrphan()

        if partialFlag and not anyRead:
            g.es("no @<file> nodes in the selected tree")

        if use_tracer: tt.stop()
    #@-node:ekr.20041005105605.26:readAll (atFile)
    #@+node:ekr.20070909100252:readOneAtAutoNode (atFile)
    def readOneAtAutoNode (self,fileName,p):

        at = self ; c = at.c ; ic = c.importCommands

        oldChanged = c.isChanged()
        at.scanDefaultDirectory(p,importing=True) # Set default_directory
        fileName = c.os_path_finalize_join(at.default_directory,fileName)

        # Remember that we have read this file.
        p.v.at_read = True # Create the attribute

        s,ok,fileKey = c.cacher.readFile(fileName,p)
        if ok: return

        if not g.unitTesting:
            g.es("reading:",p.h)

        ic.createOutline(fileName,parent=p.copy(),atAuto=True)

        if ic.errors:
            # Note: the file contains an @ignore,
            # so no unintended write can happen.
            g.es_print('errors inhibited read @auto',fileName,color='red')

        if ic.errors or not g.os_path_exists(fileName):
            p.clearDirty()
            c.setChanged(oldChanged)
        else:
            c.cacher.writeFile(p,fileKey)
            g.doHook('after-auto', p = p)  # call after-auto callbacks
    #@-node:ekr.20070909100252:readOneAtAutoNode (atFile)
    #@+node:ekr.20090225080846.3:readOneAtEditNode (atFile)
    def readOneAtEditNode (self,fn,p):

        at = self ; c = at.c ; ic = c.importCommands
        oldChanged = c.isChanged()
        at.scanDefaultDirectory(p,importing=True) # Set default_directory
        fn = c.os_path_finalize_join(at.default_directory,fn)
        junk,ext = g.os_path_splitext(fn)

        if not g.unitTesting:
            g.es("reading @edit:", g.shortFileName(fn))

        s,e = g.readFileIntoString(fn,kind='@edit')
        if s is None: return
        encoding = g.choose(e is None,'utf-8',e)

        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()

        changed = c.isChanged()
        head = ''
        ext = ext.lower()
        if ext in ('.html','.htm'):   head = '@language html\n'
        elif ext in ('.txt','.text'): head = '@nocolor\n'
        else:
            language = ic.languageForExtension(ext)
            if language and language != 'unknown_language':
                head = '@language %s\n' % language
            else:
                head = '@nocolor\n'

        p.b = g.u(head) + g.toUnicode(s,encoding=encoding,reportErrors='True')

        if not changed: c.setChanged(False)
        g.doHook('after-edit',p=p)
    #@-node:ekr.20090225080846.3:readOneAtEditNode (atFile)
    #@+node:ekr.20041005105605.27:readOpenFile
    def readOpenFile(self,root,theFile,fileName,deleteNodes=False):

        '''Read an open derived file.

        Leo 4.5 and later can only read 4.x derived files.'''

        at = self

        firstLines,read_new,thinFile = at.scanHeader(theFile,fileName)
        at.thinFile = thinFile
            # 2010/01/22: use *only* the header to set self.thinFile.

        if deleteNodes and at.shouldDeleteChildren(root,thinFile):
            root.v.at_read = True # Create the attribute for all clones.
            while root.hasChildren():
                root.firstChild().doDelete()

        if read_new:
            lastLines = at.scanText4(theFile,fileName,root)
        else:
            firstLines = [] ; lastLines = []
            if at.atShadow:
                g.trace(g.callers())
                g.trace('invalid @shadow private file',fileName)
                at.error('invalid @shadow private file',fileName)
            else:
                at.error('can not read 3.x derived file',fileName)
                g.es('you may upgrade these file using Leo 4.0 through 4.4.x')
                g.trace('root',root and root.h,fileName)

        if root:
            root.v.setVisited() # Disable warning about set nodes.

        #@    << handle first and last lines >>
        #@+node:ekr.20041005105605.28:<< handle first and last lines >>
        try:
            body = root.v.tempBodyString
        except Exception:
            body = ""

        lines = body.split('\n')
        at.completeFirstDirectives(lines,firstLines)
        at.completeLastDirectives(lines,lastLines)
        s = '\n'.join(lines).replace('\r', '')
        root.v.tempBodyString = s
        #@-node:ekr.20041005105605.28:<< handle first and last lines >>
        #@nl

        return thinFile
    #@+node:ekr.20100122130101.6175:shouldDeleteChildren
    def shouldDeleteChildren (self,root,thinFile):

        '''Return True if we should delete all children before a read.'''

        # Delete all children except for old-style @file nodes

        if root.isAtNoSentFileNode():
            return False
        elif root.isAtFileNode() and not thinFile:
            return False
        else:
            return True
    #@-node:ekr.20100122130101.6175:shouldDeleteChildren
    #@-node:ekr.20041005105605.27:readOpenFile
    #@+node:ekr.20080801071227.7:readAtShadowNodes (atFile)
    def readAtShadowNodes (self,p):

        '''Read all @shadow nodes in the p's tree.'''

        at = self ; after = p.nodeAfterTree()
        p = p.copy() # Don't change p in the caller.

        while p and p != after: # Don't use iterator.
            if p.isAtShadowFileNode():
                fileName = p.atShadowFileNodeName()
                at.readOneAtShadowNode (fileName,p)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@-node:ekr.20080801071227.7:readAtShadowNodes (atFile)
    #@+node:ekr.20080711093251.7:readOneAtShadowNode (atFile) & helper
    def readOneAtShadowNode (self,fn,p):

        at = self ; c = at.c ; x = c.shadowController

        if not fn == p.atShadowFileNodeName():
            return at.error('can not happen: fn: %s != atShadowNodeName: %s' % (
                fn, p.atShadowFileNodeName()))

        at.scanDefaultDirectory(p,importing=True) # Sets at.default_directory

        fn = c.os_path_finalize_join(at.default_directory,fn)
        shadow_fn     = x.shadowPathName(fn)
        shadow_exists = g.os_path_exists(shadow_fn) and g.os_path_isfile(shadow_fn)

        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()

        if shadow_exists:
            at.read(p,atShadow=True)
        else:
            if not g.unitTesting: g.es("reading:",p.h)
            ok = at.importAtShadowNode(fn,p)
            if ok:
                # Create the private file automatically.
                at.writeOneAtShadowNode(p,toString=False,force=True)
    #@+node:ekr.20080712080505.1:importAtShadowNode
    def importAtShadowNode (self,fn,p):

        at = self ; c = at.c  ; ic = c.importCommands
        oldChanged = c.isChanged()

        # Delete all the child nodes.
        while p.hasChildren():
            p.firstChild().doDelete()

        # Import the outline, exactly as @auto does.
        ic.createOutline(fn,parent=p.copy(),atAuto=True,atShadow=True)

        if ic.errors:
            g.es_print('errors inhibited read @shadow',fn,color='red')

        if ic.errors or not g.os_path_exists(fn):
            p.clearDirty()
            c.setChanged(oldChanged)

        # else: g.doHook('after-shadow', p = p)

        return ic.errors == 0
    #@-node:ekr.20080712080505.1:importAtShadowNode
    #@-node:ekr.20080711093251.7:readOneAtShadowNode (atFile) & helper
    #@-node:ekr.20041005105605.18:Reading (top level)
    #@+node:ekr.20041005105605.71:Reading (4.x)
    #@+node:ekr.20041005105605.72:at.createThinChild4
    def createThinChild4 (self,gnxString,headline):

        """Find or create a new *vnode* whose parent (also a vnode)
        is at.lastThinNode. This is called only for @thin trees."""

        trace = False and not g.unitTesting
        verbose = False
        at = self ; c = at.c ; indices = g.app.nodeIndices
        last = at.lastThinNode
        lastIndex = last.fileIndex
        gnx = indices.scanGnx(gnxString,0)

        if trace and verbose: g.trace("last %s, gnx %s %s" % (
            last,gnxString,headline))

        parent = at.lastThinNode # A vnode.
        children = parent.children
        for child in children:
            if gnx == child.fileIndex:
                break
        else:
            child = None

        if at.cloneSibCount > 1:
            n = at.cloneSibCount ; at.cloneSibCount = 0
            if child: clonedSibs,junk = at.scanForClonedSibs(parent,child)
            else: clonedSibs = 0
            copies = n - clonedSibs
            if trace: g.trace(copies,headline)
        else:
            if gnx == lastIndex:
                last.setVisited()
                    # Supress warning/deletion of unvisited nodes.
                if trace:g.trace('found last',last)
                return last
            if child:
                child.setVisited()
                    # Supress warning/deletion of unvisited nodes.
                if trace: g.trace('found child',child)
                return child
            copies = 1 # Create exactly one copy.

        while copies > 0:
            copies -= 1
            # Create the vnode only if it does not already exist.
            gnxDict = c.fileCommands.gnxDict
            v = gnxDict.get(gnxString)
            if v:
                if gnx != v.fileIndex:
                    g.trace('can not happen: v.fileIndex: %s gnx: %s' % (
                        v.fileIndex,gnx))
            else:
                v = leoNodes.vnode(context=c)
                v._headString = headline # Allowed use of v._headString.
                v.fileIndex = gnx
                gnxDict[gnxString] = v

            child = v
            child._linkAsNthChild(parent,parent.numberOfChildren())

        if trace: g.trace('new node: %s' % child)
        child.setVisited() # Supress warning/deletion of unvisited nodes.
        return child
    #@-node:ekr.20041005105605.72:at.createThinChild4
    #@+node:ekr.20041005105605.73:findChild4
    def findChild4 (self,headline):

        """Return the next vnode in at.root.tnodeLisft.
        This is called only for @file nodes"""

        # tnodeLists are used *only* when reading @file (not @thin) nodes.
        # tnodeLists compensate for not having gnx's in derived files! 

        trace = False and not g.unitTesting
        at = self ; v = at.root.v

        # if not g.unitTesting:
            # if headline.startswith('@file'):
                # g.es_print('Warning: @file logic',headline)

        if trace: g.trace('%s %s %s' % (
            at.tnodeListIndex,
            v.tnodeList[at.tnodeListIndex],headline))

        if not hasattr(v,"tnodeList"):
            at.readError("no tnodeList for " + repr(v))
            g.es("write the @file node or use the Import Derived File command")
            g.trace("no tnodeList for ",v,g.callers())
            return None

        if at.tnodeListIndex >= len(v.tnodeList):
            at.readError("bad tnodeList index: %d, %s" % (
                at.tnodeListIndex,repr(v)))
            g.trace("bad tnodeList index",
                at.tnodeListIndex,len(v.tnodeList),v)
            return None

        v = v.tnodeList[at.tnodeListIndex]
        assert(v)
        at.tnodeListIndex += 1

        # Don't check the headline.  It simply causes problems.
        v.setVisited() # Supress warning/deletion of unvisited nodes.
        return v
    #@-node:ekr.20041005105605.73:findChild4
    #@+node:ekr.20041005105605.74:scanText4 & allies
    def scanText4 (self,theFile,fileName,p,verbose=False):

        """Scan a 4.x derived file non-recursively."""

        trace = False and not g.unitTesting
        verbose = False
        at = self ; newNode = new_read and at.readVersion == '5'
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
        at.endSentinelNodeStack = [None]
        at.out = [] ; at.outStack = []
        at.v = p.v
        at.tStack = []
        # New code: always identify root @thin node with self.root:
        at.lastThinNode = None
        at.thinNodeStack = []
        #@nonl
        #@-node:ekr.20041005105605.75:<< init ivars for scanText4 >>
        #@nl
        if trace: g.trace('filename:',fileName)
        try:
            while at.errors == 0 and not at.done:
                s = at.readLine(theFile)
                if trace and verbose: g.trace(repr(s))
                at.lineNumber += 1
                if len(s) == 0:
                    if newNode:
                        at.do_eof()
                        at.done = True
                    break
                kind = at.sentinelKind4(s)
                if kind == at.noSentinel:
                    i = 0
                else:
                    i = at.skipSentinelStart4(s,0)
                func = at.dispatch_dict[kind]
                if trace: g.trace('%15s %16s %s' % (
                    at.sentinelName(kind),func.__name__,repr(s)))
                func(s,i)
        except AssertionError:
            junk, message, junk = sys.exc_info()
            at.error('unexpected assertion failure in',fileName,'\n',message)
            if g.unitTesting:
                raise

        if at.errors == 0 and not at.done:
            #@        << report unexpected end of text >>
            #@+node:ekr.20041005105605.76:<< report unexpected end of text >>
            assert at.endSentinelStack,'empty sentinel stack'

            at.readError(
                "Unexpected end of file. Expecting %s sentinel" %
                at.sentinelName(at.endSentinelStack[-1]))
            #@-node:ekr.20041005105605.76:<< report unexpected end of text >>
            #@nl

        return at.lastLines
    #@+node:ekr.20041005105605.77:readNormalLine & appendToDocPart
    def readNormalLine (self,s,i): # i not used.

        at = self

        if at.inCode:
            if not at.raw:
                s = g.removeLeadingWhitespace(s,at.indent,at.tab_width)
            ### at.out.append(s)
            at.appendToOut(s)
        else:
            at.appendToDocPart(s)
    #@+node:ekr.20100624082003.5942:appendToDocPart
    def appendToDocPart (self,s):

        trace = False and not g.unitTesting
        at = self

        # Skip the leading stuff
        if len(at.endSentinelComment) == 0:
            # Skip the single comment delim and a blank.
            i = g.skip_ws(s,0)
            if g.match(s,i,at.startSentinelComment):
                i += len(at.startSentinelComment)
                if g.match(s,i," "): i += 1
        else:
            i = at.skipIndent(s,0,at.indent)

        # Append s to docOut.
        line = s[i:-1] # remove newline for rstrip.

        if line == line.rstrip():
            # no trailing whitespace: the newline is real.
            at.docOut.append(line + '\n')
        else:
            # trailing whitespace: the newline is fake.
            at.docOut.append(line)

        if trace: g.trace(repr(line))
    #@-node:ekr.20100624082003.5942:appendToDocPart
    #@-node:ekr.20041005105605.77:readNormalLine & appendToDocPart
    #@+node:ekr.20041005105605.80:start sentinels
    #@+node:ekr.20041005105605.81:at.readStartAll
    def readStartAll (self,s,i):

        """Read an @+all sentinel."""

        at = self
        j = g.skip_ws(s,i)
        leadingWs = s[i:j]
        if leadingWs:
            assert g.match(s,j,"@+all"),'missing @+all'
        else:
            assert g.match(s,j,"+all"),'missing +all'

        # g.trace('root_seen',at.root_seen,at.root.h,repr(s))
        at.atAllFlag = True

        # Make sure that the generated at-all is properly indented.

        ### at.out.append(leadingWs + "@all\n")
        at.appendToOut(leadingWs + "@all\n")

        at.endSentinelStack.append(at.endAll)
        at.endSentinelNodeStack.append(at.v)
    #@-node:ekr.20041005105605.81:at.readStartAll
    #@+node:ekr.20041005105605.85:at.readStartNode & helpers
    def readStartNode (self,s,i,middle=False):

        """Read an @+node or @+middle sentinel."""

        trace = True and not g.unitTesting
        at = self ; newNode = new_read and at.readVersion == '5'
        #@    << check the sentinel and bump i>>
        #@+node:ekr.20100625085138.5956:<< check the sentinel and bump i>>
        if newNode:
            assert g.match(s,i,"+node"),'bad start node sentinel'
            i += 1
        elif middle:
            assert g.match(s,i,"+middle:"),'missing +middle'
            i += 8
        else:
            assert g.match(s,i,"+node:"),'missing +node'
            i += 6
        #@nonl
        #@-node:ekr.20100625085138.5956:<< check the sentinel and bump i>>
        #@nl
        # Get the gnx and the headline.
        if at.thinFile:
            gnx,i,level,ok = at.parseThinNodeSentinel(s,i)
            if not ok: return
        headline = at.getNodeHeadline(s,i)
        if not at.root_seen:
            at.root_seen = True

        i,newIndent = g.skip_leading_ws_with_indent(s,0,at.tab_width)
        at.indentStack.append(at.indent) ; at.indent = newIndent

        at.outStack.append(at.out)
        at.out = []
        at.tStack.append(at.v)

        if at.importing:
            p = at.createImportedNode(at.root,headline)
            at.v = p.v
        elif at.thinFile:
            at.v = at.createNewThinNode(gnx,headline,level)
        else:
            at.v = at.findChild4(headline)

        if not newNode:
            at.endSentinelStack.append(at.endNode)
    #@+node:ekr.20100625085138.5957:createNewThinNode & closePreviousNode
    def createNewThinNode (self,gnx,headline,level):

        trace = False and not g.unitTesting
        at = self ; newNode = new_read and at.readVersion == '5'

        if at.thinNodeStack:
            if newNode:
                oldLevel = len(at.thinNodeStack)
                newLevel = level - 1
                assert newLevel >= 0
                at.closePreviousNode(oldLevel,newLevel)
            else:
                at.thinNodeStack.append(at.lastThinNode)

            v = at.createThinChild4(gnx,headline)

            if newNode:
                at.thinNodeStack.append(v)
                if trace: g.trace(
                    '** oldLvl: %s, newLvl: %s, v: %s, last: %s, stack: \n%s\n' % (
                    oldLevel,newLevel,v.h,at.lastThinNode.h,
                    [z.h for z in at.thinNodeStack]))
        else:
            v = at.root.v
            at.thinNodeStack.append(v)
        at.lastThinNode = v

        return v
    #@+node:ekr.20100624082003.5944:closePreviousNode
    def closePreviousNode (self,oldLevel,newLevel):

        trace = False and not g.unitTesting
        at = self

        if trace: g.trace('******',
            [at.sentinelName(z) for z in at.endSentinelStack])

        if newLevel <= oldLevel:
            # Pretend we have seen -node sentinels.
            for z in range(oldLevel - newLevel):
                at.readEndNode('',0)
            at.lastThinNode = at.thinNodeStack[newLevel-1]
        else:
            at.lastThinNode = at.thinNodeStack[-1]
    #@-node:ekr.20100624082003.5944:closePreviousNode
    #@-node:ekr.20100625085138.5957:createNewThinNode & closePreviousNode
    #@+node:ekr.20100625085138.5955:getNodeHeadline
    def getNodeHeadline (self,s,i):

        '''Set headline to the rest of the line.
        Don't strip leading whitespace.'''

        at = self

        if len(at.endSentinelComment) == 0:
            headline = s[i:-1].rstrip()
        else:
            k = s.rfind(at.endSentinelComment,i)
            headline = s[i:k].rstrip() # works if k == -1

        # Undo the CWEB hack: undouble @ signs if\
        # the opening comment delim ends in '@'.
        if at.startSentinelComment[-1:] == '@':
            headline = headline.replace('@@','@')

        return headline
    #@-node:ekr.20100625085138.5955:getNodeHeadline
    #@+node:ekr.20100625085138.5953:parseThinNodeSentinel
    def parseThinNodeSentinel (self,s,i):

        at = self ; newNode = new_read and at.readVersion == '5'

        j = s.find(':',i)
        if j == -1:
            g.trace("no closing colon",g.get_line(s,i))
            at.readError("Expecting gnx in @+node sentinel")
            return None,None,None,False

        gnx = s[i:j]

        if newNode:
            if not g.match(s,j,': '):
                at.readError('Expecting space after gnx')
                return None,None,None,False
            i = j + 2
            level = 0
            while i < len(s) and s[i] == '*':
                i += 1
                level += 1
            if level == 0:
                at.readError('No level stars')
                return None,None,None,False
            if not g.match(s,i,' '):
                at.readError('No space after level stars')
                return None,None,None,False
            i += 1
        else:
            i = j + 1 # Skip the i
            level = 0

        return gnx,i,level,True
    #@-node:ekr.20100625085138.5953:parseThinNodeSentinel
    #@-node:ekr.20041005105605.85:at.readStartNode & helpers
    #@+node:ekr.20041005105605.111:readRef (paired using new sentinels)
    #@+at
    # The sentinel contains an @ followed by a section 
    # name in angle brackets.
    # This code is different from the code for the @@ 
    # sentinel: the expansion
    # of the reference does not include a trailing 
    # newline.
    #@-at
    #@@c

    def readRef (self,s,i):

        """Handle an @<< sentinel."""

        at = self ; newNode = new_read and at.readVersion == '5'

        if newNode:
            assert g.match(s,i,"+")
            i += 1 # Skip the new plus sign.
        j = g.skip_ws(s,i)
        assert g.match(s,j,"<<"),'missing @<< sentinel'

        if len(at.endSentinelComment) == 0:
            line = s[i:-1] # No trailing newline
        else:
            k = s.find(at.endSentinelComment,i)
            line = s[i:k] # No trailing newline, whatever k is.

        if new_read and at.readVersion == '5':
            # Put the newline back: there is no longer an @nl sentinel.
            line = line + '\n'

        # Undo the cweb hack.
        start = at.startSentinelComment
        if start and len(start) > 0 and start[-1] == '@':
            line = line.replace('@@','@')

        ### at.out.append(line)
        at.appendToOut(line)

        if newNode:
            at.endSentinelStack.append(at.endRef)
            at.endSentinelNodeStack.append(at.v)
    #@-node:ekr.20041005105605.111:readRef (paired using new sentinels)
    #@+node:ekr.20041005105605.82:readStartAt/Doc & helper
    #@+node:ekr.20100624082003.5938:readStartAt
    def readStartAt (self,s,i):

        """Read an @+at sentinel."""

        at = self ; newNode = new_read and at.readVersion == '5'

        assert g.match(s,i,"+at"),'missing +at'
        i += 3

        if newNode: # Append whatever follows the sentinel.
            j = at.skipToEndSentinel(s,i)
            follow = s[i:j]
            ### at.out.append('@' + follow)
            at.appendToOut('@' + follow)
            at.docOut = []
            at.inCode = False
        else:
            j = g.skip_ws(s,i)
            ws = s[i:j]
            at.docOut = ['@' + ws + '\n']
                # This newline may be removed by a following @nonl
            at.inCode = False
            at.endSentinelStack.append(at.endAt)
    #@-node:ekr.20100624082003.5938:readStartAt
    #@+node:ekr.20100624082003.5939:readStartDoc
    def readStartDoc (self,s,i):

        """Read an @+doc sentinel."""

        at = self ; newNode = new_read and at.readVersion == '5'

        assert g.match(s,i,"+doc"),'missing +doc'
        i += 4

        if newNode: # Append whatever follows the sentinel.
            j = at.skipToEndSentinel(s,i)
            follow = s[i:j]
            ### at.out.append('@' + follow)
            at.appendToOut('@' + follow)
            at.docOut = []
            at.inCode = False
        else:
            j = g.skip_ws(s,i)
            ws = s[i:j]
            at.docOut = ["@doc" + ws + '\n']
                # This newline may be removed by a following @nonl

            at.inCode = False
            at.endSentinelStack.append(at.endDoc)
    #@-node:ekr.20100624082003.5939:readStartDoc
    #@+node:ekr.20100624082003.5940:skipToEndSentinel
    def skipToEndSentinel(self,s,i):

        '''Skip to the end of the sentinel line.'''

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
    #@-node:ekr.20100624082003.5940:skipToEndSentinel
    #@-node:ekr.20041005105605.82:readStartAt/Doc & helper
    #@+node:ekr.20041005105605.83:readStartLeo
    def readStartLeo (self,s,i):

        """Read an unexpected @+leo sentinel."""

        at = self
        assert g.match(s,i,"+leo"),'missing +leo sentinel'
        at.readError("Ignoring unexpected @+leo sentinel")
    #@-node:ekr.20041005105605.83:readStartLeo
    #@+node:ekr.20041005105605.84:readStartMiddle
    def readStartMiddle (self,s,i):

        """Read an @+middle sentinel."""

        at = self

        at.readStartNode(s,i,middle=True)
    #@-node:ekr.20041005105605.84:readStartMiddle
    #@+node:ekr.20041005105605.89:readStartOthers
    def readStartOthers (self,s,i):

        """Read an @+others sentinel."""

        at = self

        j = g.skip_ws(s,i)
        leadingWs = s[i:j]

        if leadingWs:
            assert g.match(s,j,"@+others"),'missing @+others'
        else:
            assert g.match(s,j,"+others"),'missing +others'

        # Make sure that the generated at-others is properly indented.
        ### at.out.append(leadingWs + "@others\n")
        at.appendToOut(leadingWs + "@others\n")

        at.endSentinelStack.append(at.endOthers)
        at.endSentinelNodeStack.append(at.v)
    #@-node:ekr.20041005105605.89:readStartOthers
    #@-node:ekr.20041005105605.80:start sentinels
    #@+node:ekr.20041005105605.90:end sentinels
    #@+node:ekr.20100517130356.5810:do_eof
    def do_eof(self):

        trace = True and not g.unitTesting
        at = self

        # Make sure we there is an -leo sentinel.
        at.popSentinelStack(at.endLeo)

        # while at.endSentinelStack:
            # n = len(at.endSentinelStack)
            # top  = at.endSentinelStack and at.endSentinelStack[-1]
            # if trace: g.trace(at.sentinelName(top))
            # if top == at.endLeo:
                # at.readEndLeo(s='',i=0)
                # at.popSentinelStack(at.endLeo)
                # break 
            # else:
                # g.trace('unexpected top: %s' % at.sentinelName(top))
                # break
    #@-node:ekr.20100517130356.5810:do_eof
    #@+node:ekr.20041005105605.91:readEndAll
    def readEndAll (self,unused_s,unused_i):

        """Read an @-all sentinel."""

        at = self
        at.popSentinelStack(at.endAll)
    #@-node:ekr.20041005105605.91:readEndAll
    #@+node:ekr.20041005105605.92:readEndAt & readEndDoc
    def readEndAt (self,unused_s,unused_i):

        """Read an @-at sentinel."""

        at = self
        at.readLastDocLine("@")
        at.popSentinelStack(at.endAt)
        at.inCode = True

    def readEndDoc (self,unused_s,unused_i):

        """Read an @-doc sentinel."""

        at = self
        at.readLastDocLine("@doc")
        at.popSentinelStack(at.endDoc)
        at.inCode = True
    #@-node:ekr.20041005105605.92:readEndAt & readEndDoc
    #@+node:ekr.20041005105605.93:readEndLeo
    def readEndLeo (self,unused_s,unused_i):

        """Read an @-leo sentinel."""

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
    #@+node:ekr.20041005105605.95:at.readEndNode
    def readEndNode (self,unused_s,unused_i,middle=False):

        """Handle end-of-node processing for @-others and @-ref sentinels."""

        trace = False and not g.unitTesting
        at = self ; c = at.c
        newNode = new_read and at.readVersion == '5'

        # End raw mode.
        at.raw = False

        # Set the temporary body text.
        s = ''.join(at.out)
        s = g.toUnicode(s)

        # g.trace(repr(s))

        if at.importing:
            at.v._bodyString = s # Allowed use of _bodyString.
        elif middle: 
            pass # Middle sentinels never alter text.
        else:
            if at.v == at.root.v:
                old = None # Don't issue warnings for the root.
            elif hasattr(at.v,"tempBodyString") and s != at.v.tempBodyString:
                old = at.v.tempBodyString
            elif at.v.hasBody() and s != at.v.getBody():
                old = at.v.getBody()
            else:
                old = None

            if old:
                #@            << indicate that the node has been changed >>
                #@+node:ekr.20041005105605.96:<< indicate that the node has been changed >>
                if at.perfectImportRoot:
                    #@    << bump at.correctedLines and tell about the correction >>
                    #@+node:ekr.20041005105605.97:<< bump at.correctedLines and tell about the correction >>
                    # Report the number of corrected nodes.
                    at.correctedLines += 1

                    found = False
                    for p in at.perfectImportRoot.self_and_subtree():
                        if p.v == at.v:
                            found = True ; break

                    if found:
                        if 0: # For debugging.
                            g.pr('\n','-' * 40)
                            g.pr("old",len(old))
                            for line in g.splitLines(old):
                                #line = line.replace(' ','< >').replace('\t','<TAB>')
                                g.pr(repr(str(line)))
                            g.pr('\n','-' * 40)
                            g.pr("new",len(s))
                            for line in g.splitLines(s):
                                #line = line.replace(' ','< >').replace('\t','<TAB>')
                                g.pr(repr(str(line)))
                            g.pr('\n','-' * 40)
                    else:
                        # This should never happen.
                        g.es("correcting hidden node: v=",repr(at.v),color="red")
                    #@-node:ekr.20041005105605.97:<< bump at.correctedLines and tell about the correction >>
                    #@nl
                    at.v._bodyString = s # Allowed use of _bodyString.
                        # Just setting at.v.tempBodyString won't work here.
                    at.v.setDirty()
                        # Mark the node dirty. Ancestors will be marked dirty later.
                    at.c.setChanged(True)
                else:
                    # 2010/02/05: removed special case for @all.
                    c.nodeConflictList.append(g.bunch(
                        tag='(uncached)',
                        gnx=at.v.gnx,
                        fileName = at.root.h,
                        b_old=old,
                        b_new=s,
                        h_old=at.v._headString,
                        h_new=at.v._headString,
                    ))

                    g.es_print("uncached read node changed",at.v.h,color="red")

                    at.v.setDirty()
                        # Just set the dirty bit. Ancestors will be marked dirty later.
                    c.changed = True
                        # Important: the dirty bits won't stick unless we set c.changed here.
                        # Do *not* call c.setChanged(True) here: that would be too slow.
                #@-node:ekr.20041005105605.96:<< indicate that the node has been changed >>
                #@nl

            # 2010/02/05: *always* update the text.
            at.v.tempBodyString = s

        # Indicate that the vnode has been set in the derived file.
        at.v.setVisited()
        # g.trace('visit',at.v)

        # End the previous node sentinel.
        at.indent = at.indentStack.pop()
        at.out = at.outStack.pop()
        at.v = at.tStack.pop()
        if at.thinFile and not at.importing:
            at.lastThinNode = at.thinNodeStack.pop()

        if not newNode:
            at.popSentinelStack(at.endNode)
    #@-node:ekr.20041005105605.95:at.readEndNode
    #@+node:ekr.20041005105605.98:readEndOthers
    def readEndOthers (self,unused_s,unused_i):

        """Read an @-others sentinel."""

        at = self ; newNode = new_read and at.readVersion == '5'

        at.popSentinelStack(at.endOthers)

        if newNode:
            at.v = at.endSentinelNodeStack.pop()
            # g.trace(at.v.h)
    #@nonl
    #@-node:ekr.20041005105605.98:readEndOthers
    #@+node:ekr.20100625140824.5968:readEndRef
    def readEndRef (self,unused_s,unused_i):

        at = self ; newNode = new_read and at.readVersion == '5'

        at.popSentinelStack(at.endRef)

        if newNode:
            at.v = at.endSentinelNodeStack.pop()
            # g.trace(at.v.h)
    #@-node:ekr.20100625140824.5968:readEndRef
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

        ### at.out.append(tag + s)
        at.appendToOut(tag + s)
        at.docOut = []
    #@-node:ekr.20041005105605.99:readLastDocLine
    #@-node:ekr.20041005105605.90:end sentinels
    #@+node:ekr.20041005105605.100:Unpaired sentinels
    # Ooops: shadow files are cleared if there is a read error!!
    #@nonl
    #@+node:ekr.20041005105605.101:ignoreOldSentinel
    def  ignoreOldSentinel (self,s,unused_i):

        """Ignore an 3.x sentinel."""

        g.es("ignoring 3.x sentinel:",s.strip(),color="blue")
    #@-node:ekr.20041005105605.101:ignoreOldSentinel
    #@+node:ekr.20041005105605.102:readAfterRef
    def  readAfterRef (self,s,i):

        """Read an @afterref sentinel."""

        at = self
        assert g.match(s,i,"afterref"),'missing afterref'

        # Append the next line to the text.
        s = at.readLine(at.inputFile)
        ### at.out.append(s)
        at.appendToOut(s)
    #@-node:ekr.20041005105605.102:readAfterRef
    #@+node:ekr.20041005105605.103:readClone
    def readClone (self,s,i):

        at = self ; tag = "clone"

        assert g.match(s,i,tag),'missing clone sentinel'

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

        assert g.match(s,i,"comment"),'missing comment sentinel'

        # Just ignore the comment line!
    #@-node:ekr.20041005105605.104:readComment
    #@+node:ekr.20041005105605.105:readDelims
    def readDelims (self,s,i):

        """Read an @delims sentinel."""

        at = self
        assert g.match(s,i-1,"@delims"),'missing @delims'

        # Skip the keyword and whitespace.
        i0 = i-1
        i = g.skip_ws(s,i-1+7)

        # Get the first delim.
        j = i
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
            i += 1

        if j < i:
            at.startSentinelComment = s[j:i]
            # g.pr("delim1:", at.startSentinelComment)

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
                ### at.out.append(line+'\n')
                at.appendToOut(line+'\n')
            else:
                at.endSentinelComment = end
                # g.pr("delim2:",end)
                line = s[i0:i]
                line = line.rstrip()
                ### at.out.append(line+'\n')
                at.appendToOut(line+'\n')
        else:
            at.readError("Bad @delims")
            # Append the bad @delims line to the body text.
            # at.out.append("@delims")
            at.appendToOut("@delims")
    #@-node:ekr.20041005105605.105:readDelims
    #@+node:ekr.20041005105605.106:readDirective (@@)
    def readDirective (self,s,i):

        """Read an @@sentinel."""

        trace = False and not g.unitTesting
        at = self ; newNode = new_read and at.readVersion == '5'
        assert g.match(s,i,"@"),'missing @@ sentinel'
            # The first '@' has already been eaten.

        if trace: g.trace(repr(s[i:]))
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

                if trace:
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

        # An @c ends the doc part when using new sentinels.
        if newNode and s2 in ('@c','@c\n'):
            if at.docOut:
                at.appendToOut(''.join(at.docOut))
            at.inCode = True # End the doc part.

        ### at.out.append(s2)
        at.appendToOut(s2)
    #@-node:ekr.20041005105605.106:readDirective (@@)
    #@+node:ekr.20041005105605.109:readNl
    def readNl (self,s,i):

        """Handle an @nonl sentinel."""

        at = self
        assert g.match(s,i,"nl"),'missing nl sentinel'

        if at.inCode:
            ### at.out.append('\n')
            at.appendToOut('\n')
        else:
            at.docOut.append('\n')
    #@-node:ekr.20041005105605.109:readNl
    #@+node:ekr.20041005105605.110:readNonl
    def readNonl (self,s,i):

        """Handle an @nonl sentinel."""

        at = self
        assert g.match(s,i,"nonl"),'missing nonl sentinel'

        if at.inCode:
            s = ''.join(at.out)
            # 2010/01/07: protect against a mostly-harmless read error.
            if s:
                if s[-1] == '\n':
                    at.out = [s[:-1]] # Do not use at.appendToOut here!
                else:
                    g.trace("out:",s)
                    at.readError("unexpected @nonl directive in code part")
        else:
            s = ''.join(at.pending)
            if s:
                if s[-1] == '\n':
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
    #@+node:ekr.20041005105605.112:readVerbatim
    def readVerbatim (self,s,i):

        """Read an @verbatim sentinel."""

        at = self
        assert g.match(s,i,"verbatim"),'missing verbatim sentinel'

        # Append the next line to the text.
        s = at.readLine(at.inputFile) 
        i = at.skipIndent(s,0,at.indent)
        # Do **not** insert the verbatim line itself!
            # at.out.append("@verbatim\n")
        ### at.out.append(s[i:])
        at.appendToOut(s[i:])
    #@-node:ekr.20041005105605.112:readVerbatim
    #@-node:ekr.20041005105605.100:Unpaired sentinels
    #@+node:ekr.20041005105605.113:badEndSentinel, popSentinelStack
    def badEndSentinel (self,expectedKind):

        """Handle a mismatched ending sentinel."""

        at = self
        assert at.endSentinelStack,'empty sentinel stack'
        s = "(badEndSentinel) Ignoring %s sentinel.  Expecting %s" % (
            at.sentinelName(at.endSentinelStack[-1]),
            at.sentinelName(expectedKind))
        at.readError(s)

    def popSentinelStack (self,expectedKind):

        """Pop an entry from endSentinelStack and check it."""

        at = self
        if at.endSentinelStack and at.endSentinelStack[-1] == expectedKind:
            at.endSentinelStack.pop()
        else:
            if 1: g.trace('%s\n%s' % (
                [at.sentinelName(z) for z in at.endSentinelStack],
                g.callers(4)))
            at.badEndSentinel(expectedKind)
    #@-node:ekr.20041005105605.113:badEndSentinel, popSentinelStack
    #@-node:ekr.20041005105605.74:scanText4 & allies
    #@+node:ekr.20041005105605.114:sentinelKind4 & helper (read logic)
    def sentinelKind4(self,s):

        """Return the kind of sentinel at s."""

        trace = False and not g.unitTesting
        at = self

        val = at.sentinelKind4_helper(s)

        if trace: g.trace('%-20s %s' % (
            at.sentinelName(val),s.rstrip()))

        return val
    #@+node:ekr.20100518083515.5896:sentinelKind4_helper
    def sentinelKind4_helper(self,s):

        at = self
        i = g.skip_ws(s,0)
        if g.match(s,i,at.startSentinelComment): 
            i += len(at.startSentinelComment)
        else:
            return at.noSentinel

        # Locally undo cweb hack here
        start = at.startSentinelComment
        if start and len(start) > 0 and start[-1] == '@':
            s = s[:i] + s[i:].replace('@@','@')

        # New sentinels.
        if g.match(s,i,"@+"):
            if g.match(s,i+2,"others"):
                return at.startOthers
            elif g.match(s,i+2,"<<"):
                return at.startRef
            else:
                j = g.skip_ws(s,i+2)
                if g.match(s,j,"<<"):
                    return at.startRef
        elif g.match(s,i,"@-"):
            if g.match(s,i+2,"others"):
                return at.endOthers
            elif g.match(s,i+2,"<<"):
                return at.endRef
            else:
                j = g.skip_ws(s,i+2)
                if g.match(s,j,"<<"):
                    return at.endRef
        # Old sentinels.
        elif g.match(s,i,"@"):
            j = g.skip_ws(s,i+1)
            if j > i+1:
                if g.match(s,j,"@+others"):
                    return at.startOthers
                elif g.match(s,j,"@-others"):
                    return at.endOthers
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
        if len(key) > 0 and key in at.sentinelDict:
            return at.sentinelDict[key]
        else:
            return at.noSentinel
    #@-node:ekr.20100518083515.5896:sentinelKind4_helper
    #@-node:ekr.20041005105605.114:sentinelKind4 & helper (read logic)
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
    #@+node:ekr.20100625092449.5963:at.appendToOut
    def appendToOut (self,s):

        '''Append s to at.out.'''

        at = self ; newNode = new_read and at.readVersion == '5'
        trace = False and newNode  and not g.unitTesting

        if newNode:
            if not at.v: at.v = at.root.v
            if hasattr(at.v,"tempBodyList"):
                at.v.tempBodyList.append(s)
            else:
                at.v.tempBodyList = [s]
        else:
            at.out.append(s)

        if trace: g.trace('code: %5s' % (at.inCode),at.v.h,repr(s))
    #@-node:ekr.20100625092449.5963:at.appendToOut
    #@+node:ekr.20041005105605.120:at.parseLeoSentinel
    def parseLeoSentinel (self,s):

        trace = False and not g.unitTesting
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
        # REM hack: leading whitespace is significant 
        # before the
        # @+leo. We do this so that sentinelKind need not 
        # skip
        # whitespace following self.startSentinelComment. 
        # This is
        # correct: we want to be as restrictive as 
        # possible about what
        # is recognized as a sentinel. This minimizes 
        # false matches.
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
            # Leo 4.4.1 +:   Skip to next minus sign, end-of-line,
            #                or non numeric character.
            # This is required to handle trailing comment delims properly.
            i += len(version_tag)
            j = i
            while i < len(s) and (s[i] == '.' or s[i].isdigit()):
                i += 1
            at.readVersion = s[j:i] # 2010/05/18.

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
        if trace and not new_df:
            g.trace('not new_df(!)',repr(s))
        if trace: g.trace('valid',valid,'isThin',isThinDerivedFile)
        return valid,new_df,start,end,isThinDerivedFile
    #@-node:ekr.20041005105605.120:at.parseLeoSentinel
    #@+node:ekr.20041005105605.129:at.scanHeader
    def scanHeader(self,theFile,fileName):

        """Scan the @+leo sentinel.

        Sets self.encoding, and self.start/endSentinelComment.

        Returns (firstLines,new_df,isThinDerivedFile) where:
        firstLines        contains all @first lines,
        new_df            is True if we are reading a new-format derived file.
        isThinDerivedFile is True if the file is an @thin file."""

        trace = False
        at = self
        firstLines = [] # The lines before @+leo.
        tag = "@+leo"
        valid = True ; new_df = False ; isThinDerivedFile = False
        #@    << skip any non @+leo lines >>
        #@+node:ekr.20041005105605.130:<< skip any non @+leo lines >>
        #@+at 
        #@nonl
        # Queue up the lines before the @+leo.
        # 
        # These will be used to add as parameters to the 
        # @first directives, if any.
        # Empty lines are ignored (because empty @first 
        # directives are ignored).
        # NOTE: the function now returns a list of the 
        # lines before @+leo.
        # 
        # We can not call sentinelKind here because that 
        # depends on
        # the comment delimiters we set here.
        # 
        # at-first lines are written "verbatim", so 
        # nothing more needs to be done!
        #@-at
        #@@c

        s = at.readLine(theFile)
        if trace: g.trace('first line',repr(s))
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
            at.error("No @+leo sentinel in: %s" % fileName)
        # g.trace("start,end",repr(at.startSentinelComment),repr(at.endSentinelComment))
        return firstLines,new_df,isThinDerivedFile
    #@-node:ekr.20041005105605.129:at.scanHeader
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
        for p in root.self_and_subtree():
            if hasattr(p.v,'tempBodyString'):
                s = p.v.tempBodyString
            else:
                s = ''
            if hasattr(p.v,'tempBodyList'):
                s = s + ''.join(p.v.tempBodyList)
            # try: s = p.v.tempBodyString
            # except Exception: s = ""
            old_body = p.b
            if s != old_body:
                if thinFile:
                    p.v.setBodyString(s)
                    if p.v.isDirty():
                        p.setAllAncestorAtFileNodesDirty()
                else:
                    c.setBodyString(p,s) # Sets c and p dirty.

                if p.v.isDirty():
                    # New in Leo 4.3: support for mod_labels plugin:
                    try:
                        c.mod_label_controller.add_label(p,"before change:",old_body)
                    except Exception:
                        pass
                    # 2010/02/05: This warning is given elsewhere.
                    # g.es("changed:",p.h,color="blue")
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

        p.v.setVisited() # Suppress warning about unvisited node.
        return p
    #@-node:ekr.20041005105605.119:createImportedNode
    #@+node:ekr.20041005105605.127:readError
    def readError(self,message):

        # This is useful now that we don't print the actual messages.
        if self.errors == 0:
            self.printError("----- read error. line: %s, file: %s" % (
                self.lineNumber,self.targetFileName,))

        # g.trace(self.root,g.callers())
        self.error(message)

        # Delete all of root's tree.
        self.root.v.children = []
        self.root.setOrphan()
        self.root.setDirty()
    #@-node:ekr.20041005105605.127:readError
    #@+node:ekr.20041005105605.128:readLine
    def readLine (self,theFile):

        """Reads one line from file using the present encoding"""

        s = g.readlineForceUnixNewline(theFile) # calls theFile.readline
        # g.trace(repr(s),g.callers(4))
        u = g.toUnicode(s,self.encoding)
        return u
    #@-node:ekr.20041005105605.128:readLine
    #@+node:ekr.20050103163224:scanHeaderForThin (used by import code)
    # Note: Import code uses this.

    def scanHeaderForThin (self,theFile,fileName):

        '''Scan the header of a derived file and return True if it is a thin file.

        N.B. We are not interested in @first lines, so any encoding will do.'''

        at = self

        # The encoding doesn't matter.  No error messages are given.
        at.encoding = at.c.config.default_derived_file_encoding

        junk,junk,isThin = at.scanHeader(theFile,fileName)

        return isThin
    #@-node:ekr.20050103163224:scanHeaderForThin (used by import code)
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
    #@-node:ekr.20041005105605.17:at.Reading
    #@+node:ekr.20041005105605.132:at.Writing
    #@+node:ekr.20041005105605.133:Writing (top level)
    #@+node:ekr.20041005105605.154:asisWrite
    def asisWrite(self,root,toString=False):

        at = self ; c = at.c
        c.endEditing() # Capture the current headline.

        try:
            # Note: @asis always writes all nodes,
            # so there can be no orphan or ignored nodes.
            targetFileName = root.atAsisFileNodeName()
            at.initWriteIvars(root,targetFileName,toString=toString)
            if at.errors: return
            if not at.openFileForWriting(root,targetFileName,toString):
                # openFileForWriting calls root.setDirty() if there are errors.
                return
            for p in root.self_and_subtree():
                #@            << Write p's headline if it starts with @@ >>
                #@+node:ekr.20041005105605.155:<< Write p's headline if it starts with @@ >>
                s = p.h

                if g.match(s,0,"@@"):
                    s = s[2:]
                    if s and len(s) > 0:
                        s = g.toEncodedString(s,at.encoding,reportErrors=True) # 3/7/03
                        at.outputFile.write(s)
                #@-node:ekr.20041005105605.155:<< Write p's headline if it starts with @@ >>
                #@nl
                #@            << Write p's body >>
                #@+node:ekr.20041005105605.156:<< Write p's body >>
                s = p.b

                if s:
                    s = g.toEncodedString(s,at.encoding,reportErrors=True) # 3/7/03
                    at.outputStringWithLineEndings(s)
                #@-node:ekr.20041005105605.156:<< Write p's body >>
                #@nl
            at.closeWriteFile()
            at.replaceTargetFileIfDifferent(root) # Sets/clears dirty and orphan bits.
        except Exception:
            at.writeException(root) # Sets dirty and orphan bits.

    silentWrite = asisWrite # Compatibility with old scripts.
    #@-node:ekr.20041005105605.154:asisWrite
    #@+node:ekr.20041005105605.142:openFileForWriting & openFileForWritingHelper
    def openFileForWriting (self,root,fileName,toString):

        at = self
        at.outputFile = None

        if toString:
            at.shortFileName = g.shortFileName(fileName)
            at.outputFileName = "<string: %s>" % at.shortFileName
            at.outputFile = g.fileLikeObject()
        else:
            ok = at.openFileForWritingHelper(fileName)

            # New in Leo 4.4.8: set dirty bit if there are errors.
            if not ok: at.outputFile = None

        # New in 4.3 b2: root may be none when writing from a string.
        if root:
            if at.outputFile:
                root.clearOrphan()
            else:
                root.setOrphan()
                root.setDirty()

        return at.outputFile is not None
    #@+node:ekr.20041005105605.143:openFileForWritingHelper & helper
    def openFileForWritingHelper (self,fileName):

        '''Open the file and return True if all went well.'''

        at = self ; c = at.c

        try:
            at.shortFileName = g.shortFileName(fileName)
            at.targetFileName = c.os_path_finalize_join(at.default_directory,fileName)
            path = g.os_path_dirname(at.targetFileName)
            if not path or not g.os_path_exists(path):
                if path:
                    path = g.makeAllNonExistentDirectories(path,c=c)
                if not path or not g.os_path_exists(path):
                    path = g.os_path_dirname(at.targetFileName)
                    at.writeError("path does not exist: " + path)
                    return False
        except Exception:
            at.exception("exception creating path: %s" % repr(path))
            g.es_exception()
            return False

        if g.os_path_exists(at.targetFileName):
            try:
                if not os.access(at.targetFileName,os.W_OK):
                    at.writeError("can not open: read only: " + at.targetFileName)
                    return False
            except AttributeError:
                pass # os.access() may not exist on all platforms.

        try:
            at.outputFileName = at.targetFileName + ".tmp"
            kind,at.outputFile = self.openForWrite(at.outputFileName,'wb')
            if not at.outputFile:
                kind = g.choose(kind=='check',
                    'did not overwrite','can not create')
                at.writeError("%s %s" % (kind,at.outputFileName))
                return False
        except Exception:
            at.exception("exception creating:" + at.outputFileName)
            return False

        return True
    #@+node:bwmulder.20050101094804:openForWrite (atFile)
    def openForWrite (self, filename, wb='wb'):

        '''Open a file for writes, handling shadow files.'''

        trace = False and not g.unitTesting
        at = self ; c = at.c ; x = c.shadowController

        try:
            shadow_filename = x.shadowPathName(filename)
            self.writing_to_shadow_directory = os.path.exists(shadow_filename)
            open_file_name       = g.choose(self.writing_to_shadow_directory,shadow_filename,filename)
            self.shadow_filename = g.choose(self.writing_to_shadow_directory,shadow_filename,None)

            if self.writing_to_shadow_directory:
                if trace: g.trace(filename,shadow_filename)
                x.message('writing %s' % shadow_filename)
                return 'shadow',open(open_file_name,wb)
            else:
                ok = c.checkFileTimeStamp(at.targetFileName)
                return 'check',ok and open(open_file_name,wb)

        except IOError:
            if not g.app.unitTesting:
                g.es_print('openForWrite: exception opening file: %s' % (open_file_name),color='red')
                g.es_exception()
            return 'error',None
    #@-node:bwmulder.20050101094804:openForWrite (atFile)
    #@-node:ekr.20041005105605.143:openFileForWritingHelper & helper
    #@-node:ekr.20041005105605.142:openFileForWriting & openFileForWritingHelper
    #@+node:ekr.20041005105605.144:write & helper (atFile)
    def write (self,root,
        kind = '@unknown', # Should not happen.
        nosentinels = False,
        thinFile = False,
        scriptWrite = False,
        toString = False,
    ):
        """Write a 4.x derived file.
        root is the position of an @<file> node"""

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
            if not at.targetFileName:
                # We have an @file node.
                at.targetFileName = root.atFileNodeName()
        else:
            at.targetFileName = root.atFileNodeName()
        #@-node:ekr.20041005105605.145:<< set at.targetFileName >>
        #@nl
        at.initWriteIvars(root,at.targetFileName,
            nosentinels = nosentinels, thinFile = thinFile,
            scriptWrite = scriptWrite, toString = toString)

        # "look ahead" computation of eventual fileName.
        eventualFileName = c.os_path_finalize_join(
            at.default_directory,at.targetFileName)
        exists = g.os_path_exists(eventualFileName)
        # g.trace('eventualFileName',eventualFileName,
            # 'at.targetFileName',at.targetFileName)

        if not scriptWrite and not toString:
            if nosentinels:
                if not self.shouldWriteAtNosentNode(root,exists):
                    return
            elif not hasattr(root.v,'at_read') and exists:
                # Prompt if writing a new @file or @thin node would
                # overwrite an existing file.
                ok = self.promptForDangerousWrite(eventualFileName,kind)
                if ok:
                    root.v.at_read = True # Create the attribute for all clones.
                else:
                    g.es("not written:",eventualFileName)
                    return

        if not at.openFileForWriting(root,at.targetFileName,toString):
            # openFileForWriting calls root.setDirty() if there are errors.
            return

        try:
            at.writeOpenFile(root,nosentinels=nosentinels,toString=toString)
            assert root==at.root
            if toString:
                at.closeWriteFile() # sets self.stringOutput
                # Major bug: failure to clear this wipes out headlines!
                # Minor bug: sometimes this causes slight problems...
                if hasattr(self.root.v,'tnodeList'):
                    delattr(self.root.v,'tnodeList')
                root.v._p_changed = True
            else:
                at.closeWriteFile()
                if at.errors > 0 or root.isOrphan():
                    #@                << set dirty and orphan bits >>
                    #@+node:ekr.20041005105605.146:<< set dirty and orphan bits >>
                    # Setting the orphan and dirty flags tells Leo to write the tree..
                    root.setOrphan()
                    root.setDirty()
                    # Delete the temp file.
                    self.remove(at.outputFileName) 

                    #@-node:ekr.20041005105605.146:<< set dirty and orphan bits >>
                    #@nl
                    g.es("not written:",at.outputFileName)
                else:
                    at.replaceTargetFileIfDifferent(root)
                        # Sets/clears dirty and orphan bits.

        except Exception:
            if hasattr(self.root.v,'tnodeList'):
                delattr(self.root.v,'tnodeList')
            if toString:
                at.exception("exception preprocessing script")
                root.v._p_changed = True
            else:
                at.writeException() # Sets dirty and orphan bits.
    #@+node:ekr.20080620095343.1:shouldWriteAtNosentNode
    #@+at 
    #@nonl
    # Much thought went into this decision tree:
    # 
    # - We do not want decisions to depend on past 
    # history.That ' s too confusing.
    # - We must ensure that the file will be written if 
    # the user does significant work.
    # - We must ensure that the user can create an @auto x 
    # node at any time
    #   without risk of of replacing x with empty or 
    # insignificant information.
    # - We want the user to be able to create an @auto 
    # node which will be populated the next time the.leo 
    # file is opened.
    # - We don't want minor import imperfections to be 
    # written to the @auto file.
    # - The explicit commands that read and write @auto 
    # trees must always be honored.
    #@-at
    #@@c

    def shouldWriteAtNosentNode (self,p,exists):

        '''Return True if we should write the @auto node at p.'''

        if not exists: # We can write a non-existent file without danger.
            return True
        elif self.isSignificantTree(p):
            return True # Assume the tree contains what should be written.
        else:
            g.es_print(p.h,'not written:',color='red')
            g.es_print('no children and less than 10 characters (excluding directives)',color='blue')
            return False
    #@-node:ekr.20080620095343.1:shouldWriteAtNosentNode
    #@-node:ekr.20041005105605.144:write & helper (atFile)
    #@+node:ekr.20041005105605.147:writeAll (atFile) & helper
    def writeAll(self,
        writeAtFileNodesFlag=False,
        writeDirtyAtFileNodesFlag=False,
        toString=False
    ):

        """Write @file nodes in all or part of the outline"""

        trace = False and not g.unitTesting
        at = self ; c = at.c
        if trace: scanAtPathDirectivesCount = c.scanAtPathDirectivesCount
        writtenFiles = [] # Files that might be written again.
        force = writeAtFileNodesFlag

        if writeAtFileNodesFlag:
            # The Write @<file> Nodes command.
            # Write all nodes in the selected tree.
            p = c.p
            after = p.nodeAfterTree()
        else:
            # Write dirty nodes in the entire outline.
            p =  c.rootPosition()
            after = c.nullPosition()

        #@    << Clear all orphan bits >>
        #@+node:ekr.20041005105605.148:<< Clear all orphan bits >>
        #@+at 
        #@nonl
        # We must clear these bits because they may have 
        # been set on a previous write.
        # Calls to atFile::write may set the orphan bits 
        # in @file nodes.
        # If so, write_Leo_file will write the entire 
        # @file tree.
        #@-at
        #@@c

        for v2 in p.self_and_subtree():
            v2.clearOrphan()
        #@-node:ekr.20041005105605.148:<< Clear all orphan bits >>
        #@nl
        while p and p != after:
            if p.isAnyAtFileNode() or p.isAtIgnoreNode():
                self.writeAllHelper(p,force,toString,writeAtFileNodesFlag,writtenFiles)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        #@    << say the command is finished >>
        #@+node:ekr.20041005105605.150:<< say the command is finished >>
        if writeAtFileNodesFlag or writeDirtyAtFileNodesFlag:
            if len(writtenFiles) > 0:
                g.es("finished")
            elif writeAtFileNodesFlag:
                g.es("no @<file> nodes in the selected tree")
            else:
                g.es("no dirty @<file> nodes")
        #@-node:ekr.20041005105605.150:<< say the command is finished >>
        #@nl
        if trace: g.trace('%s calls to c.scanAtPathDirectives()' % (
            c.scanAtPathDirectivesCount-scanAtPathDirectivesCount))

    #@+node:ekr.20041005105605.149:writeAllHelper (atFile)
    def writeAllHelper (self,p,
        force,toString,writeAtFileNodesFlag,writtenFiles
    ):

        trace = False and not g.unitTesting
        at = self ; c = at.c

        if p.isAtIgnoreNode() and not p.isAtAsisFileNode():
            pathChanged = False
        else:
            oldPath = at.getPathUa(p).lower()
            newPath = at.fullPath(p).lower()
            pathChanged = oldPath and oldPath != newPath
            # 2010/01/27: suppress this message during save-as and save-to commands.
            if pathChanged and not c.ignoreChangedPaths:
                at.setPathUa(p,newPath) # Remember that we have changed paths.
                g.es_print('path changed for',p.h,color='blue')
                if trace: g.trace('p %s\noldPath %s\nnewPath %s' % (
                    p.h,repr(oldPath),repr(newPath)))

        if p.v.isDirty() or pathChanged or writeAtFileNodesFlag or p.v in writtenFiles:

            # Tricky: @ignore not recognised in @asis nodes.
            if p.isAtAsisFileNode():
                at.asisWrite(p,toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtIgnoreNode():
                pass
            elif p.isAtAutoNode():
                at.writeOneAtAutoNode(p,toString=toString,force=force)
                writtenFiles.append(p.v)
            elif p.isAtEditNode():
                at.writeOneAtEditNode(p,toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtNoSentFileNode():
                at.write(p,kind='@nosent',nosentinels=True,toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtShadowFileNode():
                at.writeOneAtShadowNode(p,toString=toString,force=force or pathChanged)
                writtenFiles.append(p.v)
            elif p.isAtThinFileNode():
                at.write(p,kind='@thin',thinFile=True,toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtFileNode():
                # Write old @file nodes using @thin format.
                at.write(p,kind='@file',thinFile=True,toString=toString)
                writtenFiles.append(p.v)
    #@-node:ekr.20041005105605.149:writeAllHelper (atFile)
    #@-node:ekr.20041005105605.147:writeAll (atFile) & helper
    #@+node:ekr.20070806105859:writeAtAutoNodes & writeDirtyAtAutoNodes (atFile) & helpers
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
        p = c.p ; after = p.nodeAfterTree()
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
    #@+node:ekr.20070806141607:writeOneAtAutoNode & helpers (atFile)
    def writeOneAtAutoNode(self,p,toString,force):

        '''Write p, an @auto node.

        File indices *must* have already been assigned.'''

        at = self ; c = at.c ; root = p.copy()

        fileName = p.atAutoNodeName()
        if not fileName and not toString: return False

        at.scanDefaultDirectory(p,importing=True) # Set default_directory
        fileName = c.os_path_finalize_join(at.default_directory,fileName)
        exists = g.os_path_exists(fileName)

        if not toString and not self.shouldWriteAtAutoNode(p,exists,force):
            return False

        # Prompt if writing a new @auto node would overwrite an existing file.
        if (not toString and not hasattr(p.v,'at_read') and
            g.os_path_exists(fileName)
        ):
            ok = self.promptForDangerousWrite(fileName,kind='@auto')
            if ok:
                p.v.at_read = True # Create the attribute
            else:
                g.es("not written:",fileName)
                return False

        # This code is similar to code in at.write.
        c.endEditing() # Capture the current headline.
        at.targetFileName = g.choose(toString,"<string-file>",fileName)
        at.initWriteIvars(root,at.targetFileName,
            atAuto=True,
            nosentinels=True,thinFile=False,scriptWrite=False,
            toString=toString)

        ok = at.openFileForWriting (root,fileName=fileName,toString=toString)
        isAtAutoRst = root.isAtAutoRstNode()
        if ok:
            if isAtAutoRst:
                ok2 = c.rstCommands.writeAtAutoFile(root,fileName,self.outputFile)
                if not ok2: at.errors += 1
            else:
                at.writeOpenFile(root,nosentinels=True,toString=toString)
            at.closeWriteFile() # Sets stringOutput if toString is True.
            # g.trace('at.errors',at.errors)
            if at.errors == 0:
                # g.trace('toString',toString,'force',force,'isAtAutoRst',isAtAutoRst)
                at.replaceTargetFileIfDifferent(root,ignoreBlankLines=isAtAutoRst)
                    # Sets/clears dirty and orphan bits.
            else:
                g.es("not written:",at.outputFileName)
                root.setDirty() # New in Leo 4.4.8.

        elif not toString:
            root.setDirty() # Make _sure_ we try to rewrite this file.
            g.es("not written:",at.outputFileName)

        return ok
    #@+node:ekr.20071019141745:shouldWriteAtAutoNode
    #@+at 
    #@nonl
    # Much thought went into this decision tree:
    # 
    # - We do not want decisions to depend on past 
    # history.  That's too confusing.
    # - We must ensure that the file will be written if 
    # the user does significant work.
    # - We must ensure that the user can create an @auto x 
    # node at any time
    #   without risk of of replacing x with empty or 
    # insignificant information.
    # - We want the user to be able to create an @auto 
    # node which will be populated the next time the .leo 
    # file is opened.
    # - We don't want minor import imperfections to be 
    # written to the @auto file.
    # - The explicit commands that read and write @auto 
    # trees must always be honored.
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
        elif not self.isSignificantTree(p): # There is noting of value to write.
            g.es_print(p.h,'not written:',color='red')
            g.es_print('no children and less than 10 characters (excluding directives)',color='red')
            return False
        else: # The @auto tree is dirty and contains significant info.
            return True
    #@-node:ekr.20071019141745:shouldWriteAtAutoNode
    #@-node:ekr.20070806141607:writeOneAtAutoNode & helpers (atFile)
    #@-node:ekr.20070806105859:writeAtAutoNodes & writeDirtyAtAutoNodes (atFile) & helpers
    #@+node:ekr.20080711093251.3:writeAtShadowdNodes & writeDirtyAtShadowNodes (atFile) & helpers
    def writeAtShadowNodes (self,event=None):

        '''Write all @shadow nodes in the selected outline.'''

        at = self
        return at.writeAtShadowNodesHelper(writeDirtyOnly=False)

    def writeDirtyAtShadowNodes (self,event=None):

        '''Write all dirty @shadow nodes in the selected outline.'''

        at = self
        return at.writeAtShadowNodesHelper(writeDirtyOnly=True)
    #@nonl
    #@+node:ekr.20080711093251.4:writeAtShadowNodesHelper
    def writeAtShadowNodesHelper(self,toString=False,writeDirtyOnly=True):

        """Write @shadow nodes in the selected outline"""

        at = self ; c = at.c
        p = c.p ; after = p.nodeAfterTree()
        found = False

        while p and p != after:
            if p.atShadowFileNodeName() and not p.isAtIgnoreNode() and (p.isDirty() or not writeDirtyOnly):
                ok = at.writeOneAtShadowNode(p,toString=toString,force=True)
                if ok:
                    found = True
                    g.es('wrote %s' % p.atShadowFileNodeName(),color='blue')
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()

        if found:
            g.es("finished")
        elif writeDirtyOnly:
            g.es("no dirty @shadow nodes in the selected tree")
        else:
            g.es("no @shadow nodes in the selected tree")

        return found
    #@-node:ekr.20080711093251.4:writeAtShadowNodesHelper
    #@+node:ekr.20080711093251.5:writeOneAtShadowNode & helpers
    def writeOneAtShadowNode(self,p,toString,force):

        '''Write p, an @shadow node.

        File indices *must* have already been assigned.'''

        trace = False and not g.unitTesting
        at = self ; c = at.c ; root = p.copy() ; x = c.shadowController

        fn = p.atShadowFileNodeName()
        if trace: g.trace(p.h,fn)
        if not fn:
            g.es_print('can not happen: not an @shadow node',p.h,color='red')
            return False

        # A hack to support unknown extensions.
        self.adjustTargetLanguage(fn) # May set c.target_language.

        fn = at.fullPath(p)
        at.default_directory = g.os_path_dirname(fn)
        exists = g.os_path_exists(fn)
        if trace: g.trace('exists %s fn %s' % (exists,fn))

        # Bug fix 2010/01/18: Make sure we can compute the shadow directory.
        private_fn = x.shadowPathName(fn)
        if not private_fn:
            return False

        if not toString and not self.shouldWriteAtShadowNode(p,exists,force,fn):
            if trace: g.trace('ignoring',fn)
            return False

        c.endEditing() # Capture the current headline.
        at.initWriteIvars(root,targetFileName=None, # Not used.
            atShadow=True,
            nosentinels=None, # set below.  Affects only error messages (sometimes).
            thinFile=True, # New in Leo 4.5 b2: private files are thin files.
            scriptWrite=False,
            toString=False, # True: create a fileLikeObject.  This is done below.
            forcePythonSentinels=True) # A hack to suppress an error message.
                # The actual sentinels will be set below.

        # Bug fix: Leo 4.5.1: use x.markerFromFileName to force the delim to match
        #                     what is used in x.propegate changes.
        marker = x.markerFromFileName(fn)
        at.startSentinelComment,at.endSentinelComment=marker.getDelims()

        if g.app.unitTesting: ivars_dict = g.getIvarsDict(at)

        # Write the public and private files to public_s and private_s strings.
        data = []
        for sentinels in (False,True):
            theFile = at.openStringFile(fn)
            at.sentinels = sentinels
            at.writeOpenFile(root,
                nosentinels=not sentinels,toString=False)
                # nosentinels only affects error messages, and then only if atAuto is True.
            s = at.closeStringFile(theFile)
            data.append(s)

        # Set these new ivars for unit tests.
        at.public_s, at.private_s = data

        if g.app.unitTesting:
            exceptions = ('public_s','private_s','sentinels','stringOutput')
            assert g.checkUnchangedIvars(at,ivars_dict,exceptions)

        if at.errors == 0 and not toString:
            # Write the public and private files.
            if trace: g.trace('writing',fn)
            x.makeShadowDirectory(fn) # makeShadowDirectory takes a *public* file name.
            at.replaceFileWithString(private_fn,at.private_s)
            at.replaceFileWithString(fn,at.public_s)

        self.checkPythonCode(root,s=at.private_s,targetFn=fn)

        if at.errors == 0:
            root.clearOrphan()
            root.clearDirty()
        else:
            g.es("not written:",at.outputFileName,color='red')
            root.setDirty() # New in Leo 4.4.8.

        return at.errors == 0
    #@+node:ekr.20080711093251.6:shouldWriteAtShadowNode
    #@+at 
    #@nonl
    # Much thought went into this decision tree:
    # 
    # - We do not want decisions to depend on past 
    # history.  That's too confusing.
    # - We must ensure that the file will be written if 
    # the user does significant work.
    # - We must ensure that the user can create an @shadow 
    # x node at any time
    #   without risk of of replacing x with empty or 
    # insignificant information.
    # - We want the user to be able to create an @shadow 
    # node which will be populated the next time the .leo 
    # file is opened.
    # - We don't want minor import imperfections to be 
    # written to the @shadow file.
    # - The explicit commands that read and write @shadow 
    # trees must always be honored.
    #@-at
    #@@c

    def shouldWriteAtShadowNode (self,p,exists,force,fn):

        '''Return True if we should write the @shadow node at p.'''

        at = self ; x = at.c.shadowController

        if force: # We are executing write-at-shadow-node or write-dirty-at-shadow-nodes.
            return True
        elif not exists: # We can write a non-existent file without danger.
            return True
        elif not p.isDirty(): # There is nothing new to write.
            return False
        elif not self.isSignificantTree(p): # There is noting of value to write.
            g.es_print(p.h,'not written:',color='red')
            g.es_print('no children and less than 10 characters (excluding directives)',color='red')
            return False
        else: # The @shadow tree is dirty and contains significant info.
            return True
    #@-node:ekr.20080711093251.6:shouldWriteAtShadowNode
    #@+node:ekr.20080819075811.13:adjustTargetLanguage
    def adjustTargetLanguage (self,fn):

        """Use the language implied by fn's extension if
        there is a conflict between it and c.target_language."""

        at = self ; c = at.c

        if c.target_language:
            junk,target_ext = g.os_path_splitext(fn)  
        else:
            target_ext = ''

        junk,ext = g.os_path_splitext(fn)

        if ext:
            if ext.startswith('.'): ext = ext[1:]

            language = g.app.extension_dict.get(ext)
            if language:
                c.target_language = language
            else:
                # An unknown language.
                pass # Use the default language, **not** 'unknown_language'
    #@-node:ekr.20080819075811.13:adjustTargetLanguage
    #@-node:ekr.20080711093251.5:writeOneAtShadowNode & helpers
    #@-node:ekr.20080711093251.3:writeAtShadowdNodes & writeDirtyAtShadowNodes (atFile) & helpers
    #@+node:ekr.20050506084734:writeFromString (atFile)
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
            ok = at.openFileForWriting(root,at.targetFileName,toString=True)
            if g.app.unitTesting: assert ok # string writes never fail.
            # Simulate writing the entire file so error recovery works.
            at.writeOpenFile(root,nosentinels=not useSentinels,toString=True,fromString=s)
            at.closeWriteFile()
            # Major bug: failure to clear this wipes out headlines!
            # Minor bug: sometimes this causes slight problems...
            if root:
                if hasattr(self.root.v,'tnodeList'):
                    delattr(self.root.v,'tnodeList')
                root.v._p_changed = True
        except Exception:
            at.exception("exception preprocessing script")

        return at.stringOutput
    #@-node:ekr.20050506084734:writeFromString (atFile)
    #@+node:ekr.20041005105605.151:writeMissing
    def writeMissing(self,p,toString=False):

        at = self ; c = at.c
        writtenFiles = False

        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after: # Don't use iterator.
            if p.isAtAsisFileNode() or (p.isAnyAtFileNode() and not p.isAtIgnoreNode()):
                at.targetFileName = p.anyAtFileNodeName()
                if at.targetFileName:
                    at.targetFileName = c.os_path_finalize_join(
                        self.default_directory,at.targetFileName)
                    if not g.os_path_exists(at.targetFileName):
                        ok = at.openFileForWriting(p,at.targetFileName,toString)
                        # openFileForWriting calls p.setDirty() if there are errors.
                        if ok:
                            #@                        << write the @file node >>
                            #@+node:ekr.20041005105605.152:<< write the @file node >> (writeMissing)
                            if p.isAtAsisFileNode():
                                at.asisWrite(p)
                            elif p.isAtNoSentFileNode():
                                at.write(p,kind='@nosent',nosentinels=True)
                            elif p.isAtFileNode():
                                at.write(p,kind='@file')
                            else: assert(0)

                            writtenFiles = True
                            #@-node:ekr.20041005105605.152:<< write the @file node >> (writeMissing)
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
    #@-node:ekr.20041005105605.151:writeMissing
    #@+node:ekr.20090225080846.5:writeOneAtEditNode
    # Similar to writeOneAtAutoNode.

    def writeOneAtEditNode(self,p,toString,force=False):

        '''Write p, an @edit node.

        File indices *must* have already been assigned.'''

        at = self ; c = at.c ; root = p.copy()

        fn = p.atEditNodeName()

        if fn:
            at.scanDefaultDirectory(p,importing=True) # Set default_directory
            fn = c.os_path_finalize_join(at.default_directory,fn)
            exists = g.os_path_exists(fn)
            if not self.shouldWriteAtEditNode(p,exists,force):
                return False
        elif not toString:
            return False

        # This code is similar to code in at.write.
        c.endEditing() # Capture the current headline.
        at.targetFileName = g.choose(toString,"<string-file>",fn)
        at.initWriteIvars(root,at.targetFileName,
            atAuto=True,
            atEdit=True,
            nosentinels=True,thinFile=False,scriptWrite=False,
            toString=toString)

        ok = at.openFileForWriting(root,fileName=fn,toString=toString)
        if ok:
            at.writeOpenFile(root,nosentinels=True,toString=toString)
            at.closeWriteFile() # Sets stringOutput if toString is True.
            if at.errors == 0:
                at.replaceTargetFileIfDifferent(root) # Sets/clears dirty and orphan bits.
            else:
                g.es("not written:",at.outputFileName)
                root.setDirty()

        elif not toString:
            root.setDirty() # Make _sure_ we try to rewrite this file.
            g.es("not written:",at.outputFileName)

        return ok
    #@+node:ekr.20090225080846.6:shouldWriteAtEditNode
    #@+at 
    #@nonl
    # Much thought went into this decision tree:
    # 
    # - We do not want decisions to depend on past 
    # history.  That's too confusing.
    # - We must ensure that the file will be written if 
    # the user does significant work.
    # - We must ensure that the user can create an @edit x 
    # node at any time
    #   without risk of of replacing x with empty or 
    # insignificant information.
    # - We want the user to be able to create an @edit 
    # node which will be read
    #   the next time the .leo file is opened.
    # - We don't want minor import imperfections to be 
    # written to the @edit file.
    # - The explicit commands that read and write @edit 
    # trees must always be honored.
    #@-at
    #@@c

    def shouldWriteAtEditNode (self,p,exists,force):

        '''Return True if we should write the @auto node at p.'''

        if force: # We are executing write-at-auto-node or write-dirty-at-auto-nodes.
            return True
        elif not exists: # We can write a non-existent file without danger.
            return True
        elif not p.isDirty(): # There is nothing new to write.
            return False
        elif not self.isSignificantTree(p): # There is noting of value to write.
            g.es_print(p.h,'not written:',color='red')
            g.es_print('no children and less than 10 characters (excluding directives)',color='red')
            return False
        else: # The @auto tree is dirty and contains significant info.
            return True
    #@-node:ekr.20090225080846.6:shouldWriteAtEditNode
    #@-node:ekr.20090225080846.5:writeOneAtEditNode
    #@+node:ekr.20041005105605.157:writeOpenFile
    # New in 4.3: must be inited before calling this method.
    # New in 4.3 b2: support for writing from a string.

    def writeOpenFile(self,root,
        nosentinels=False,toString=False,fromString=''):

        """Do all writes except asis writes."""

        at = self
        s = g.choose(fromString,fromString,root.v.b)
        root.clearAllVisitedInTree()
        at.putAtFirstLines(s)
        at.putOpenLeoSentinel("@+leo-ver=%s" % (
            g.choose(new_write,5,4)))
        at.putInitialComment()
        at.putOpenNodeSentinel(root)
        at.putBody(root,fromString=fromString)
        at.putCloseNodeSentinel(root)
        if not new_write:
            at.putSentinel("@-leo")
        root.setVisited()
        at.putAtLastLines(s)
        if not toString:
            at.warnAboutOrphandAndIgnoredNodes()
    #@-node:ekr.20041005105605.157:writeOpenFile
    #@-node:ekr.20041005105605.133:Writing (top level)
    #@+node:ekr.20041005105605.160:Writing 4.x
    #@+node:ekr.20041005105605.161:putBody
    # oneNodeOnly is no longer used, but it might be used in the future?

    def putBody(self,p,oneNodeOnly=False,fromString=''):

        """ Generate the body enclosed in sentinel lines."""

        trace = False and not g.unitTesting
        at = self

        # New in 4.3 b2: get s from fromString if possible.
        s = g.choose(fromString,fromString,p.b)

        p.v.setVisited()
        # g.trace('visit',p.h)
            # Make sure v is never expanded again.
            # Suppress orphans check.
        if not at.thinFile:
            p.v.setWriteBit() # Mark the vnode to be written.
        if not at.thinFile and not s: return

        inCode = True
        #@    << Make sure all lines end in a newline >>
        #@+node:ekr.20041005105605.162:<< Make sure all lines end in a newline >>
        #@+at
        # 
        # If we add a trailing newline, we'll generate an 
        # @nonl sentinel below.
        # 
        # - We always ensure a newline in @file and @thin 
        # trees.
        # - This code is not used used in @asis trees.
        # - New in Leo 4.4.3 b1: We add a newline in 
        # @nosent trees unless
        #   @bool force_newlines_in_at_nosent_bodies = 
        # False
        #@-at
        #@@c

        if s:
            trailingNewlineFlag = s[-1] == '\n'
            if not trailingNewlineFlag:
                if (at.sentinels or 
                    (not at.atAuto and at.force_newlines_in_at_nosent_bodies)
                ):
                    # g.trace('Added newline',repr(s))
                    s = s + '\n'
        else:
            trailingNewlineFlag = True # don't need to generate an @nonl
        #@-node:ekr.20041005105605.162:<< Make sure all lines end in a newline >>
        #@nl
        s = self.cleanLines(p,s)
        i = 0
        while i < len(s):
            next_i = g.skip_line(s,i)
            assert(next_i > i)
            kind = at.directiveKind4(s,i)
            #@        << handle line at s[i] >>
            #@+node:ekr.20041005105605.163:<< handle line at s[i]  >>
            if trace: g.trace(kind,repr(s[i:next_i]))

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
            elif kind == at.startVerbatim:
                at.putSentinel("@verbatim")
                at.putIndent(at.indent)
                i = next_i
                next_i = g.skip_line(s,i)
                at.os(s[i:next_i])
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
        if new_write:
            pass
        elif not trailingNewlineFlag:
            if at.sentinels:
                at.putSentinel("@nonl")
            elif at.atAuto and not at.atEdit:
                # New in Leo 4.6 rc1: ensure all @auto nodes end in a newline!
                at.onl()
    #@-node:ekr.20041005105605.161:putBody
    #@+node:ekr.20041005105605.164:writing code lines...
    #@+node:ekr.20041005105605.165:@all
    #@+node:ekr.20041005105605.166:putAtAllLine
    def putAtAllLine (self,s,i,p):

        """Put the expansion of @all."""

        at = self
        j,delta = g.skip_leading_ws_with_indent(s,i,at.tab_width)
        at.putLeadInSentinel(s,i,j,delta)

        at.indent += delta
        if at.leadingWs:
            at.putSentinel("@" + at.leadingWs + "@+all")
        else:
            at.putSentinel("@+all")

        for child in p.children():
            at.putAtAllChild(child)

        at.putSentinel("@-all")
        at.indent -= delta
    #@-node:ekr.20041005105605.166:putAtAllLine
    #@+node:ekr.20041005105605.167:putatAllBody
    def putAtAllBody(self,p):

        """ Generate the body enclosed in sentinel lines."""

        at = self ; s = p.b

        p.v.setVisited()
        # g.trace('visit',p.h)
            # Make sure v is never expanded again.
            # Suppress orphans check.

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
        if at.sentinels and not trailingNewlineFlag and not new_write:
            at.putSentinel("@nonl")
    #@-node:ekr.20041005105605.167:putatAllBody
    #@+node:ekr.20041005105605.169:putAtAllChild
    #@+at
    # This code puts only the first of two or more cloned 
    # siblings, preceding the
    # clone with an @clone n sentinel.
    # 
    # This is a debatable choice: the cloned tree appears 
    # only once in the external
    # file. This should be benign; the text created by 
    # @all is likely to be used only
    # for recreating the outline in Leo. The 
    # representation in the derived file
    # doesn't matter much.
    #@-at
    #@@c

    def putAtAllChild(self,p):

        at = self

        parent_v = p._parentVnode()

        if False: # 2010/01/23: This generates atFile errors about orphan nodes.
            clonedSibs,thisClonedSibIndex = at.scanForClonedSibs(parent_v,p.v)
            if clonedSibs > 1:
                at.putSentinel("@clone %d" % (clonedSibs))
            else:
                g.trace('**** ignoring',p.h)
                p.v.setVisited() # 2010/01/23
                return # Don't write second or greater trees.

        at.putOpenNodeSentinel(p,inAtAll=True) # Suppress warnings about @file nodes.
        at.putAtAllBody(p) 

        for child in p.children():
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
        h = p.h ; i = g.skip_ws(h,0)
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

        parent_v = p._parentVnode()
        clonedSibs,thisClonedSibIndex = at.scanForClonedSibs(parent_v,p.v)
        if clonedSibs > 1 and thisClonedSibIndex == 1:
            at.writeError("Cloned siblings are not valid in @thin trees")
            g.es_print(p.h,color='red')

        at.putOpenNodeSentinel(p)
        at.putBody(p) 

        # Insert expansions of all children.
        for child in p.children():
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

        lws = at.leadingWs or ''

        if at.leadingWs:
            # Note: there are *two* at signs here.
            at.putSentinel("@" + lws + "@+others")
        else:
            at.putSentinel("@+others")

        for child in p.children():
            if at.inAtOthers(child):
                at.putAtOthersChild(child)

        if new_write:
            # This is a more consistent convention.
            at.putSentinel("@" + lws + "@-others")
        else:
            at.putSentinel("@-others")
        at.indent -= delta
    #@-node:ekr.20041005105605.173:putAtOthersLine
    #@-node:ekr.20041005105605.170:@others
    #@+node:ekr.20041005105605.174:putCodeLine (leoAtFile)
    def putCodeLine (self,s,i):

        '''Put a normal code line.'''

        trace = False and not g.unitTesting
        at = self

        # Put @verbatim sentinel if required.
        k = g.skip_ws(s,i)
        if g.match(s,k,self.startSentinelComment + '@'):
            self.putSentinel('@verbatim')

        j = g.skip_line(s,i)
        line = s[i:j]

        if trace: g.trace(self.atShadow,repr(line))

        # Don't put any whitespace in otherwise blank lines.
        if line.strip(): # The line has non-empty content.
            if not at.raw:
                at.putIndent(at.indent,line)

            if line[-1:]=='\n':
                at.os(line[:-1])
                at.onl()
            else:
                at.os(line)
        elif line and line[-1] == '\n':
            at.onl()
        else:
            g.trace('Can not happen: completely empty line')

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
                        ( name,p.h))
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

        lws = at.leadingWs or ''
        if new_write:
            at.putSentinel("@+" + lws + name)
        else:
            at.putSentinel("@" + lws + name)

        ### if new_write:
            ### # This sentinel is required to handle the lws properly.
            # at.putSentinel("@+" + lws + name)
        ### else:
            ### at.putSentinel("@" + lws + name)
        ### elif at.leadingWs:
            ### at.putSentinel("@" + at.leadingWs + name)
        ### else:
            ### at.putSentinel("@" + name)

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

        if new_write:
            at.putSentinel("@-" + lws + name)

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
            if new_write:
                pass
            else:
                # Temporarily readjust delta to make @nl look better.
                at.indent += delta
                if not new_write:
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
            if not new_write:
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

        if new_write: # Put whatever follows the directive in the sentinel
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
                if not new_write:
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
            # All inserted newlines are preceeded by 
            # whitespace:
            # we remove trailing whitespace from lines 
            # that have not been split.
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

        if new_write:
            pass
        else:
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

        at = self ; h = p.h
        #@    << remove comment delims from h if necessary >>
        #@+node:ekr.20041005105605.189:<< remove comment delims from h if necessary >>
        #@+at 
        #@nonl
        # Bug fix 1/24/03:
        # 
        # If the present @language/@comment settings do 
        # not specify a single-line comment we remove all 
        # block comment delims from h.  This prevents 
        # headline text from interfering with the parsing 
        # of node sentinels.
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
            gnx = g.app.nodeIndices.toString(p.v.fileIndex)
            if new_write:
                level = 1 + p.level() - self.root.level()
                stars = '*' * level
                if 1: # Put the gnx in the traditional place.
                    return "%s: %s %s" % (gnx,stars,h)
                else: # Hide the gnx to the right.
                    pad = max(1,100-len(stars)-len(h)) * ' '
                    return '%s %s%s::%s' % (stars,h,pad,gnx)
            else:
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
            if not new_write:
                at.putSentinel("@nonl")
            at.indent -= delta # Let the caller set at.indent permanently.
    #@-node:ekr.20041005105605.190:putLeadInSentinel 4.x
    #@+node:ekr.20041005105605.191:putCloseNodeSentinel 4.x
    def putCloseNodeSentinel(self,p,middle=False):

        at = self

        if new_write:
            return

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
    #@+node:ekr.20041005105605.193:putOpenNodeSentinel
    def putOpenNodeSentinel(self,p,inAtAll=False,middle=False):

        """Write @+node sentinel for p."""

        at = self

        if not inAtAll and p.isAtFileNode() and p != at.root:
            at.writeError("@file not valid in: " + p.h)
            return

        # g.trace(at.thinFile,p)

        s = at.nodeSentinelText(p)

        if new_write:
            at.putSentinel('@+node %s' % s)
        elif middle:
            at.putSentinel("@+middle:" + s)
        else:
            at.putSentinel("@+node:" + s)

        # Leo 4.7 b2: we never write tnodeLists.
    #@-node:ekr.20041005105605.193:putOpenNodeSentinel
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
        # If the opening comment delim ends in '@', double 
        # all '@' signs except the first, which is 
        # "doubled" by the trailing '@' in the opening 
        # comment delimiter.
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
    #@+node:ekr.20090514111518.5661:checkPythonCode (leoAtFile) & helpers
    def checkPythonCode (self,root,s=None,targetFn=None):

        c = self.c

        if not targetFn: targetFn = self.targetFileName

        if targetFn and targetFn.endswith('.py') and self.checkPythonCodeOnWrite:

            if not s:
                s,e = g.readFileIntoString(self.outputFileName)
                if s is None: return

            # It's too slow to check each node separately.
            ok = self.checkPythonSyntax(root,s)

            # Syntax checking catches most indentation problems.
            if False and ok: self.tabNannyNode(root,s)
    #@+node:ekr.20090514111518.5663:checkPythonSyntax (leoAtFile)
    def checkPythonSyntax (self,p,body,supress=False):

        try:
            ok = True
            if not g.isPython3:
                body = g.toEncodedString(body)
            body = body.replace('\r','')
            fn = '<node: %s>' % p.h
            compile(body + '\n',fn,'exec')
        except SyntaxError:
            if not supress:
                self.syntaxError(p,body)
            ok = False
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            ok = False
        return ok
    #@+node:ekr.20090514111518.5666:syntaxError (leoAtFile)
    def syntaxError(self,p,body):

        g.es_print("Syntax error in: %s" % (p.h),color="red")
        typ,val,tb = sys.exc_info()
        message = hasattr(val,'message') and val.message
        if message: g.es_print(message)
        if val is None: return
        lines = g.splitLines(body)
        n = val.lineno
        offset = val.offset or 0
        if n is None:return
        i = val.lineno-1
        for j in range(max(0,i-3),min(i+3,len(lines)-1)):
            g.es_print('%5s:%s %s' % (
                j,g.choose(j==i,'*',' '),lines[j].rstrip()))
            if j == i:
                g.es_print(' '*(7+offset)+'^')
    #@nonl
    #@-node:ekr.20090514111518.5666:syntaxError (leoAtFile)
    #@-node:ekr.20090514111518.5663:checkPythonSyntax (leoAtFile)
    #@+node:ekr.20090514111518.5665:tabNannyNode (leoAtFile)
    def tabNannyNode (self,p,body,suppress=False):

        import parser,tabnanny,tokenize

        try:
            readline = g.readLinesClass(body).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))
        except parser.ParserError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.es("ParserError in",p.h,color="red")
                g.es('',str(msg))
        except IndentationError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.es("IndentationError in",p.h,color="red")
                g.es('',str(msg))
        except tokenize.TokenError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.es("TokenError in",p.h,color="red")
                g.es('',str(msg))
        except tabnanny.NannyNag:
            junk, nag, junk = sys.exc_info()
            if suppress:
                raise
            else:
                badline = nag.get_lineno()
                line    = nag.get_line()
                message = nag.get_msg()
                g.es("indentation error in",p.h,"line",badline,color="red")
                g.es(message)
                line2 = repr(str(line))[1:-1]
                g.es("offending line:\n",line2)
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            if suppress: raise
    #@nonl
    #@-node:ekr.20090514111518.5665:tabNannyNode (leoAtFile)
    #@-node:ekr.20090514111518.5661:checkPythonCode (leoAtFile) & helpers
    #@+node:ekr.20080712150045.3:closeStringFile
    def closeStringFile (self,theFile):

        at = self

        if theFile:
            theFile.flush()
            s = at.stringOutput = theFile.get()
            theFile.close()
            at.outputFile = None

            # at.outputFileName = u''
            if g.isPython3:
                at.outputFileName = ''
            else:
                at.outputFileName = unicode('')

            at.shortFileName = ''
            at.targetFileName = None
            return s
        else:
            return None
    #@-node:ekr.20080712150045.3:closeStringFile
    #@+node:ekr.20041005105605.135:closeWriteFile
    # 4.0: Don't use newline-pending logic.

    def closeWriteFile (self):

        at = self

        if at.outputFile:
            # g.trace('**closing',at.outputFileName,at.outputFile)
            at.outputFile.flush()
            if at.toString:
                at.stringOutput = self.outputFile.get()
            at.outputFile.close()
            at.outputFile = None
            return at.stringOutput
        else:
            return None
    #@-node:ekr.20041005105605.135:closeWriteFile
    #@+node:ekr.20041005105605.197:compareFiles
    def compareFiles (self,path1,path2,ignoreLineEndings,ignoreBlankLines=False):

        """Compare two text files."""
        at = self

        # We can't use 'U' mode because of encoding issues (Python 2.x only).
        s1,e = g.readFileIntoString(path1,mode='rb',raw=True)
        if s1 is None:
            g.internalError('empty compare file: %s' % path1)
            return False
        s2,e = g.readFileIntoString(path2,mode='rb',raw=True)
        if s2 is None:
            g.internalError('empty compare file: %s' % path2)
            return False
        equal = s1 == s2

        # 2010/03/29: Make sure both strings are unicode.
        # This is requred to handle binary files in Python 3.x.
        s1 = g.toUnicode(s1,encoding=at.encoding)
        s2 = g.toUnicode(s2,encoding=at.encoding)

        if ignoreBlankLines and not equal:
            s1 = g.removeBlankLines(s1)
            s2 = g.removeBlankLines(s2)
            equal = s1 == s2

        if ignoreLineEndings and not equal:
            # Wrong: equivalent to ignoreBlankLines!
                # s1 = s1.replace('\n','').replace('\r','')
                # s2 = s2.replace('\n','').replace('\r','')
            s1 = s1.replace('\r','')
            s2 = s2.replace('\r','')
            equal = s1 == s2
        # g.trace('equal',equal,'ignoreLineEndings',ignoreLineEndings,'encoding',at.encoding)
        return equal
    #@nonl
    #@-node:ekr.20041005105605.197:compareFiles
    #@+node:ekr.20041005105605.198:directiveKind4 (write logic)
    def directiveKind4(self,s,i):

        """Return the kind of at-directive or noDirective."""

        trace = False and not g.unitTesting
        at = self
        n = len(s)

        if trace and s.startswith('@'): g.trace(s.rstrip())

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
            ("@raw",at.rawDirective),
            ("@verbatim",at.startVerbatim))

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
    #@-node:ekr.20041005105605.198:directiveKind4 (write logic)
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
        if i > -1:
            return True, i + 2
        else:
            return False, -1
    #@-node:ekr.20041005105605.200:isSectionName
    #@+node:ekr.20070909103844:isSignificantTree
    def isSignificantTree (self,p):

        '''Return True if p's tree has a significant amount of information.'''

        trace = False and not g.unitTesting
        s = p.b

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
        val = p.hasChildren() or len(s2.strip()) >= 10
        if trace: g.trace(val,p.h)
        return val
    #@-node:ekr.20070909103844:isSignificantTree
    #@+node:ekr.20080712150045.2:openStringFile
    def openStringFile (self,fn):

        at = self

        at.shortFileName = g.shortFileName(fn)
        at.outputFileName = "<string: %s>" % at.shortFileName
        at.outputFile = g.fileLikeObject()
        at.targetFileName = "<string-file>"

        return at.outputFile
    #@-node:ekr.20080712150045.2:openStringFile
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

        trace = False and not g.unitTesting
        at = self ; tag = self.underindentEscapeString
        f = at.outputFile

        if s and f:
            try:
                if s.startswith(tag):
                    junk,s = self.parseUnderindentTag(s)
                # Bug fix: this must be done last.
                s = g.toEncodedString(s,at.encoding,reportErrors=True)
                if trace: g.trace(repr(s),g.callers(5))
                f.write(s)
            except Exception:
                at.exception("exception writing:" + s)
    #@-node:ekr.20041005105605.204:os
    #@-node:ekr.20041005105605.201:os and allies
    #@+node:ekr.20041005105605.205:outputStringWithLineEndings
    # Write the string s as-is except that we replace '\n' with the proper line ending.

    def outputStringWithLineEndings (self,s):
        at = self

        # Calling self.onl() runs afoul of queued newlines.
        if g.isPython3:
            s = g.ue(s,at.encoding)

        s = s.replace('\n',at.output_newline)
        self.os(s)

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
    # It is important for PHP and other situations that 
    # @first and @last directives get translated to 
    # verbatim lines that do _not_ include what follows 
    # the @first & @last directives.
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
    def putIndent(self,n,s=''):

        """Put tabs and spaces corresponding to n spaces,
        assuming that we are at the start of a line.

        Remove extra blanks if the line starts with the underindentEscapeString"""

        # g.trace(repr(s))
        tag = self.underindentEscapeString

        if s.startswith(tag):
            n2,s2 = self.parseUnderindentTag(s)
            if n2 >= n: return
            elif n > 0: n -= n2
            else:       n += n2

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
            lines = s2.split("\\n")
            for line in lines:
                line = line.replace("@date",time.asctime())
                if len(line)> 0:
                    self.putSentinel("@comment " + line)
    #@-node:ekr.20041005105605.211:putInitialComment
    #@+node:ekr.20080712150045.1:replaceFileWithString (atFile)
    def replaceFileWithString (self,fn,s):

        '''Replace the file with s if s is different from theFile's contents.

        Return True if theFile was changed.
        '''

        at = self ; testing = g.app.unitTesting

        # g.trace('fn',fn,'s','\n',s)
        # g.trace(g.callers())

        exists = g.os_path_exists(fn)

        if exists: # Read the file.  Return if it is the same.
            s2,e = g.readFileIntoString(fn)
            if s is None:
                return False
            if s == s2:
                if not testing: g.es('unchanged:',fn)
                return False

        # Issue warning if directory does not exist.
        theDir = g.os_path_dirname(fn)
        if theDir and not g.os_path_exists(theDir):
            if not g.unitTesting:
                g.es('not written: %s directory not found' % fn,color='red')
            return False

        # Replace
        try:
            f = open(fn,'wb')
            if g.isPython3:
                s = g.toEncodedString(s,encoding=self.encoding)
            f.write(s)
            f.close()
            if not testing:
                if exists:
                    g.es('wrote:    ',fn)
                else:
                    # g.trace('created:',fn,g.callers())
                    g.es('created:',fn)
            return True
        except IOError:
            at.error('unexpected exception writing file: %s' % (fn))
            g.es_exception()
            return False
    #@-node:ekr.20080712150045.1:replaceFileWithString (atFile)
    #@+node:ekr.20041005105605.212:replaceTargetFileIfDifferent (atFile)
    def replaceTargetFileIfDifferent (self,root,ignoreBlankLines=False):

        '''Create target file as follows:
        1. If target file does not exist, rename output file to target file.
        2. If target file is identical to output file, remove the output file.
        3. If target file is different from output file,
           remove target file, then rename output file to be target file.

        Return True if the original file was changed.
        '''

        trace = False and not g.unitTesting
        c = self.c

        assert(self.outputFile is None)

        if self.toString:
            # Do *not* change the actual file or set any dirty flag.
            self.fileChangedFlag = False
            return False

        if root:
            # The default: may be changed later.
            root.clearOrphan()
            root.clearDirty()

        if trace: g.trace(
            'ignoreBlankLines',ignoreBlankLines,
            'target exists',g.os_path_exists(self.targetFileName),
            self.outputFileName,self.targetFileName)

        if g.os_path_exists(self.targetFileName):
            if self.compareFiles(
                self.outputFileName,
                self.targetFileName,
                ignoreLineEndings=not self.explicitLineEnding,
                ignoreBlankLines=ignoreBlankLines):
                # Files are identical.
                ok = self.remove(self.outputFileName)
                if trace: g.trace('files are identical')
                if ok:
                    g.es('unchanged:',self.shortFileName)
                else:
                    g.es('error writing',self.shortFileName,color='red')
                    g.es('not written:',self.shortFileName)
                    if root: root.setDirty() # New in 4.4.8.
                self.fileChangedFlag = False
                return False
            else:
                # A mismatch.
                self.checkPythonCode(root)
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
                    c.setFileTimeStamp(self.targetFileName)
                    g.es('wrote:',self.shortFileName)
                else:
                    g.es('error writing',self.shortFileName,color='red')
                    g.es('not written:',self.shortFileName)
                    if root: root.setDirty() # New in 4.4.8.

                self.fileChangedFlag = ok
                return ok
        else:
            # Rename the output file.
            ok = self.rename(self.outputFileName,self.targetFileName)
            if ok:
                c.setFileTimeStamp(self.targetFileName)
                g.es('created:',self.targetFileName)
            else:
                # self.rename gives the error.
                if root: root.setDirty() # New in 4.4.8.

            # No original file to change. Return value tested by a unit test.
            self.fileChangedFlag = False 
            return False
    #@-node:ekr.20041005105605.212:replaceTargetFileIfDifferent (atFile)
    #@+node:ekr.20041005105605.216:warnAboutOrpanAndIgnoredNodes
    # Called from writeOpenFile.

    def warnAboutOrphandAndIgnoredNodes (self):

        # Always warn, even when language=="cweb"
        at = self ; root = at.root

        for p in root.self_and_subtree():
            if not p.v.isVisited():
                at.writeError("Orphan node:  " + p.h)
                if p.hasParent():
                    g.es("parent node:",p.parent().h,color="blue")
                if not at.thinFile and p.isAtIgnoreNode():
                    at.writeError("@ignore node: " + p.h)

        if at.thinFile:
            p = root.copy() ; after = p.nodeAfterTree()
            while p and p != after:
                if p.isAtAllNode():
                    p.moveToNodeAfterTree()
                else:
                    if p.isAtIgnoreNode():
                        at.writeError("@ignore node: " + p.h)
                    p.moveToThreadNext()
    #@-node:ekr.20041005105605.216:warnAboutOrpanAndIgnoredNodes
    #@+node:ekr.20041005105605.217:writeError
    def writeError(self,message=None):

        if self.errors == 0:
            g.es_error("errors writing: " + self.targetFileName)
            g.trace(g.callers(5))

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

        if self.outputFileName:
            self.remove(self.outputFileName)

        if root:
            # Make sure we try to rewrite this file.
            root.setOrphan()
            root.setDirty()
    #@-node:ekr.20041005105605.218:writeException
    #@-node:ekr.20041005105605.196:Writing 4.x utils...
    #@-node:ekr.20041005105605.132:at.Writing
    #@+node:ekr.20041005105605.219:at.Utilites
    #@+node:ekr.20041005105605.220:atFile.error & printError
    def error(self,*args):

        at = self
        if True: # args:
            at.printError(*args)
        at.errors += 1

    def printError (self,*args):

        '''Print an error message that may contain non-ascii characters.'''

        at = self
        keys = {'color': g.choose(at.errors,'blue','red')}
        g.es_print_error(*args,**keys)
    #@-node:ekr.20041005105605.220:atFile.error & printError
    #@+node:ekr.20080923070954.4:atFile.scanAllDirectives
    def scanAllDirectives(self,p,
        scripting=False,importing=False,
        reading=False,forcePythonSentinels=False,
        createPath=True,
        issuePathWarning=False,
    ):

        '''Scan p and p's ancestors looking for directives,
        setting corresponding atFile ivars.'''

        trace = False and not g.unitTesting
        at = self ; c = self.c
        g.app.atPathInBodyWarning = None
        #@    << set ivars >>
        #@+node:ekr.20080923070954.14:<< Set ivars >>
        self.page_width = self.c.page_width
        self.tab_width  = self.c.tab_width

        self.default_directory = None # 8/2: will be set later.

        # g.trace(c.target_language)

        if c.target_language:
            c.target_language = c.target_language.lower()

        delims = g.set_delims_from_language(c.target_language)
        at.language = c.target_language

        at.encoding = c.config.default_derived_file_encoding
        at.output_newline = g.getOutputNewline(c=self.c) # Init from config settings.
        #@-node:ekr.20080923070954.14:<< Set ivars >>
        #@nl
        lang_dict = {'language':at.language,'delims':delims,}
        table = (
            ('encoding',    at.encoding,    g.scanAtEncodingDirectives),
            ('lang-dict',   lang_dict,      g.scanAtCommentAndAtLanguageDirectives),
            ('lineending',  None,           g.scanAtLineendingDirectives),
            ('pagewidth',   c.page_width,   g.scanAtPagewidthDirectives),
            ('path',        None,           c.scanAtPathDirectives),
            ('tabwidth',    c.tab_width,    g.scanAtTabwidthDirectives),
        )

        # Set d by scanning all directives.
        aList = g.get_directives_dict_list(p)
        d = {}
        for key,default,func in table:
            val = func(aList)
            d[key] = g.choose(val is None,default,val)

        if issuePathWarning and g.app.atPathInBodyWarning:
            g.es('warning: ignoring @path directive in',
                g.app.atPathInBodyWarning,color='red')

        # Post process.
        lang_dict       = d.get('lang-dict')
        delims          = lang_dict.get('delims')
        lineending      = d.get('lineending')
        if lineending:
            at.explicitLineEnding = True
            at.output_newline = lineending
        else:
            at.output_newline = g.getOutputNewline(c=c) # Init from config settings.

        at.encoding             = d.get('encoding')
        at.language             = lang_dict.get('language')
        at.page_width           = d.get('pagewidth')
        at.default_directory    = d.get('path')
        at.tab_width            = d.get('tabwidth')

        if not importing and not reading:
            # Don't override comment delims when reading!
            #@        << set comment strings from delims >>
            #@+node:ekr.20080923070954.13:<< Set comment strings from delims >>
            if forcePythonSentinels:
                # Force Python language.
                delim1,delim2,delim3 = g.set_delims_from_language("python")
                self.language = "python"
            else:
                delim1,delim2,delim3 = delims

            # Use single-line comments if we have a choice.
            # delim1,delim2,delim3 now correspond to line,start,end
            if delim1:
                at.startSentinelComment = delim1
                at.endSentinelComment = "" # Must not be None.
            elif delim2 and delim3:
                at.startSentinelComment = delim2
                at.endSentinelComment = delim3
            else: # Emergency!
                # assert(0)
                if not g.app.unitTesting:
                    g.es_print("unknown language: using Python comment delimiters")
                    g.es_print("c.target_language:",c.target_language)
                    g.es_print('','delim1,delim2,delim3:','',delim1,'',delim2,'',delim3)
                at.startSentinelComment = "#" # This should never happen!
                at.endSentinelComment = ""

            # g.trace(repr(self.startSentinelComment),repr(self.endSentinelComment))
            #@-node:ekr.20080923070954.13:<< Set comment strings from delims >>
            #@nl

        # For unit testing.
        d = {
            "all"       : all,
            "encoding"  : at.encoding,
            "language"  : at.language,
            "lineending": at.output_newline,
            "pagewidth" : at.page_width,
            "path"      : at.default_directory,
            "tabwidth"  : at.tab_width,
        }
        if trace: g.trace(d)
        return d
    #@-node:ekr.20080923070954.4:atFile.scanAllDirectives
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
            p.setBodyString(s)
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
    # The difference, if any, between these methods and 
    # the corresponding g.utils_x
    # functions is that these methods may call self.error.
    #@-at
    #@+node:ekr.20050104131820:chmod
    def chmod (self,fileName,mode):

        # Do _not_ call self.error here.
        return g.utils_chmod(fileName,mode)
    #@-node:ekr.20050104131820:chmod
    #@+node:ekr.20050104131929.1:atFile.rename
    #@+
    #@nonl
    #@<< about os.rename >>
    #@+node:ekr.20050104131929.2:<< about os.rename >>
    #@+at 
    #@nonl
    # Here is the Python 2.4 documentation for rename 
    # (same as Python 2.3)
    # 
    # Rename the file or directory src to dst.  If dst is 
    # a directory, OSError will be raised.
    # 
    # On Unix, if dst exists and is a file, it will be 
    # removed silently if the user
    # has permission. The operation may fail on some Unix 
    # flavors if src and dst are
    # on different filesystems. If successful, the 
    # renaming will be an atomic
    # operation (this is a POSIX requirement).
    # 
    # On Windows, if dst already exists, OSError will be 
    # raised even if it is a file;
    # there may be no way to implement an atomic rename 
    # when dst names an existing
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
    #@+node:ekr.20050104132018:atFile.remove
    def remove (self,fileName,verbose=True):

        try:
            os.remove(fileName)
            return True
        except Exception:
            if verbose:
                self.error("exception removing: %s" % fileName)
                g.es_exception()
                g.trace(g.callers(5))
            return False
    #@-node:ekr.20050104132018:atFile.remove
    #@+node:ekr.20050104132026:stat
    def stat (self,fileName):

        '''Return the access mode of named file, removing any setuid, setgid, and sticky bits.'''

        # Do _not_ call self.error here.
        return g.utils_stat(fileName)
    #@-node:ekr.20050104132026:stat
    #@-node:ekr.20050104131929:file operations...
    #@+node:ekr.20090530055015.6050:fullPath (leoAtFile)
    def fullPath (self,p,simulate=False):

        '''Return the full path (including fileName) in effect at p.

        Neither the path nor the fileName will be created if it does not exist.
        '''

        at = self ; c = at.c
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList,createPath=False)
        if simulate: # for unit tests.
            fn = p.h
        else:
            fn = p.anyAtFileNodeName()
        if fn:
            path = g.os_path_finalize_join(path,fn)
        else:
            g.trace('can not happen: not an @<file> node:',g.callers(4))
            for p2 in p.self_and_parents():
                g.trace(p2.h)
            path = ''

        # g.trace(p.h,repr(path))
        return path
    #@-node:ekr.20090530055015.6050:fullPath (leoAtFile)
    #@+node:ekr.20090530055015.6023:get/setPathUa (leoAtFile)
    def getPathUa (self,p):

        if hasattr(p.v,'tempAttributes'):
            d = p.v.tempAttributes.get('read-path',{})
            return d.get('path')
        else:
            return ''

    def setPathUa (self,p,path):

        if not hasattr(p.v,'tempAttributes'):
            p.v.tempAttributes = {}

        d = p.v.tempAttributes.get('read-path',{})
        d['path'] = path
        p.v.tempAttributes ['read-path'] = d
    #@-node:ekr.20090530055015.6023:get/setPathUa (leoAtFile)
    #@+node:ekr.20081216090156.4:parseUnderindentTag
    def parseUnderindentTag (self,s):

        tag = self.underindentEscapeString
        s2 = s[len(tag):]

        # To be valid, the escape must be followed by at least one digit.
        i = 0
        while i < len(s2) and s2[i].isdigit():
            i += 1

        if i > 0:
            n = int(s2[:i])
            return n,s2[i:]
        else:
            return 0,s
    #@-node:ekr.20081216090156.4:parseUnderindentTag
    #@+node:ekr.20090712050729.6017:promptForDangerousWrite
    def promptForDangerousWrite (self,fileName,kind):

        c = self.c

        if g.app.unitTesting:
            val = g.app.unitTestDict.get('promptForDangerousWrite')
            return val in (None,True)

        # g.trace(timeStamp, timeStamp2)
        message = '%s %s\n%s\n%s' % (
            kind, fileName,
            g.tr('already exists.'),
            g.tr('Overwrite this file?'))

        ok = g.app.gui.runAskYesNoCancelDialog(c,
            title = 'Overwrite existing file?',
            message = message)

        return ok == 'yes'
    #@-node:ekr.20090712050729.6017:promptForDangerousWrite
    #@+node:ekr.20041005105605.236:scanDefaultDirectory (leoAtFile)
    def scanDefaultDirectory(self,p,importing=False):

        """Set the default_directory ivar by looking for @path directives."""

        at = self ; c = at.c

        at.default_directory,error = g.setDefaultDirectory(c,p,importing)

        if error: at.error(error)
    #@-node:ekr.20041005105605.236:scanDefaultDirectory (leoAtFile)
    #@+node:ekr.20041005105605.242:scanForClonedSibs (reading & writing)
    def scanForClonedSibs (self,parent_v,v):

        """Scan the siblings of vnode v looking for clones of v.
        Return the number of cloned sibs and n where p is the n'th cloned sibling."""

        clonedSibs = 0 # The number of cloned siblings of p, including p.
        thisClonedSibIndex = 0 # Position of p in list of cloned siblings.

        if v and v.isCloned():
            for sib in parent_v.children:
                if sib == v:
                    clonedSibs += 1
                    if sib == v:
                        thisClonedSibIndex = clonedSibs

        return clonedSibs,thisClonedSibIndex
    #@-node:ekr.20041005105605.242:scanForClonedSibs (reading & writing)
    #@+node:ekr.20041005105605.243:sentinelName
    # Returns the name of the sentinel for warnings.

    def sentinelName(self, kind):

        at = self

        sentinelNameDict = {
            at.endAll:        "@-all", # 4.x
            at.endAt:         "@-at",
            at.endBody:       "@-body", # 3.x only.
            at.endDoc:        "@-doc",
            at.endLeo:        "@-leo",
            at.endMiddle:     "@-middle", # 4.x
            at.endNode:       "@-node",
            at.endOthers:     "@-others",
            at.endRef:        "@-<<", # 4.8
            at.noSentinel:    "<no sentinel>",
            at.startAt:       "@+at",
            at.startBody:     "@+body",
            at.startDoc:      "@+doc",
            at.startLeo:      "@+leo",
            at.startNode:     "@+node",
            at.startOthers:   "@+others",
            at.startAll:      "@+all",    
            at.startMiddle:   "@+middle", 
            at.startAfterRef: "@afterref", # 4.x
            at.startComment:  "@comment",
            at.startDelims:   "@delims",
            at.startDirective:"@@",
            at.startNl:       "@nl",   # 4.x
            at.startNonl:     "@nonl", # 4.x
            at.startClone:    "@clone", # 4.2
            at.startRef:      "@<<",
            at.startVerbatim: "@verbatim",
            at.startVerbatimAfterRef: "@verbatimAfterRef", # 3.x only.
        } 

        return sentinelNameDict.get(kind,"<unknown sentinel: %s>" % kind)
    #@-node:ekr.20041005105605.243:sentinelName
    #@+node:ekr.20041005105605.20:warnOnReadOnlyFile
    def warnOnReadOnlyFile (self,fn):

        # os.access() may not exist on all platforms.
        try:
            read_only = not os.access(fn,os.W_OK)
        except AttributeError:
            read_only = False 

        if read_only:
            g.es("read only:",fn,color="red")
    #@-node:ekr.20041005105605.20:warnOnReadOnlyFile
    #@-node:ekr.20041005105605.219:at.Utilites
    #@-others
#@-node:ekr.20041005105605.1:@thin leoAtFile.py
#@-leo

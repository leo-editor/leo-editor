# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20041005105605.1: * @file leoAtFile.py
#@@first
    # Needed because of unicode characters in tests.

"""Classes to read and write @file nodes."""

#@@language python
#@@tabwidth -4
#@@pagewidth 60

allow_cloned_sibs = True # True: allow cloned siblings in @file nodes.
# new_write = True # True: new write code: convert to unicode only once.
# new_read = True # True: read the entire file at once, and set at.read_lines.
use_stringio = False # True: use cstringio instead of g.fileLikeObject. 
    # or base g.fileLikeObject on cstringio.

#@+<< imports >>
#@+node:ekr.20041005105605.2: ** << imports >> (leoAtFile)
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes
import os
import sys
import time
#@-<< imports >>

class atFile:

    """The class implementing the atFile subcommander."""

    #@+<< define class constants >>
    #@+node:ekr.20041005105605.5: ** << define class constants >>
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
    #@-<< define class constants >>
    #@+<< define sentinelDict >>
    #@+node:ekr.20041005105605.6: ** << define sentinelDict >>
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
    #@-<< define sentinelDict >>

    #@+others
    #@+node:ekr.20041005105605.7: ** at.Birth & init
    #@+node:ekr.20041005105605.8: *3*  atFile.ctor
    # Note: g.getScript also call the at.__init__ and at.finishCreate().

    def __init__(self,c):

        # **Warning**: all these ivars must **also** be inited in initCommonIvars.
        self.c = c
        self.debug = False
        self.fileCommands = c.fileCommands
        self.errors = 0 # Make sure at.error() works even when not inited.

        # **Only** at.writeAll manages these flags.
        # promptForDangerousWrite sets cancelFlag and yesToAll only if canCancelFlag is True.
        self.canCancelFlag = False
        self.cancelFlag = False
        self.yesToAll = False

        # User options.
        self.checkPythonCodeOnWrite = c.config.getBool(
            'check-python-code-on-write',default=True)
        self.underindentEscapeString = c.config.getString(
            'underindent-escape-string') or '\\-'

        self.dispatch_dict = self.defineDispatchDict()
            # Define the dispatch dictionary used by scanText4.
    #@+node:ekr.20041005105605.9: *3* at.defineDispatchDict
    def defineDispatchDict(self):

        '''Return the dispatch dictionary used by scanText4.'''

        return  {
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
    #@+node:ekr.20041005105605.10: *3* at.initCommonIvars
    def initCommonIvars (self):

        """Init ivars common to both reading and writing.

        The defaults set here may be changed later."""

        at = self ; c = at.c

        at.at_auto_encoding = c.config.default_at_auto_file_encoding
        at.default_directory = None
        at.encoding = c.config.default_derived_file_encoding
        at.endSentinelComment = ""
        at.errors = 0
        at.inCode = True
        at.indent = 0  # The unit of indentation is spaces, not tabs.
        at.language = None
        at.output_newline = g.getOutputNewline(c=c)
        at.page_width = None
        at.pending = []
        at.raw = False # True: in @raw mode
        at.root = None # The root (a position) of tree being read or written.
        at.root_seen = False # True: root vnode has been handled in this file.
        at.startSentinelComment = ""
        at.startSentinelComment = ""
        at.tab_width  = None
        at.toString = False # True: sring-oriented read or write.
        at.writing_to_shadow_directory = False
    #@+node:ekr.20041005105605.13: *3* at.initReadIvars
    def initReadIvars(self,root,fileName,
        importFileName=None,
        perfectImportRoot=None,
        atShadow=False,
    ):
        at = self
        at.initCommonIvars()
        at.bom_encoding = None
            # The encoding implied by any BOM (set by g.stripBOM)
        at.cloneSibCount = 0
            # n > 1: Make sure n cloned sibs exists at next @+node sentinel
        at.correctedLines = 0
            # For perfect import.
        at.docOut = [] # The doc part being accumulated.
        at.done = False # True when @-leo seen.
        at.endSentinelIndentStack = []
            # Restored indentation for @-others and @-<< sentinels.
            # Used only when readVersion5.
        at.endSentinelStack = []
            # Contains entries for +node sentinels only when not readVersion5
        at.endSentinelLevelStack = []
            # The saved level, len(at.thinNodeStack), for @-others and @-<< sentinels.
            # Used only when readVersion5.
        at.endSentinelNodeStack = []
            # Used only when readVersion5.
        at.fromString = False
        at.importing = bool(importFileName)
        at.importRootSeen = False
        at.indentStack = []
        at.inputFile = None
        at.lastLines = [] # The lines after @-leo
        at.lastRefNode = None
            # The previous reference node, for at.readAfterRef.
            # No stack is needed because -<< sentinels restore at.v
            # to the node needed by at.readAfterRef.
        at.lastThinNode = None
            # The last thin node at this level.
            # Used by createThinChild4.
        at.leadingWs = ""
        at.lineNumber = 0 # New in Leo 4.4.8.
        at.out = None
        at.outStack = []
        at.perfectImportRoot = perfectImportRoot
        at.read_i = 0
        at.read_lines = []
        at.readVersion = ''
            # New in Leo 4.8: "4" or "5" for new-style thin files.
        at.readVersion5 = False
            # synonym for at.readVersion >= '5' and not atShadow.
            # set by at.parseLeoSentinel()
        at.root = root
        at.rootSeen = False
        at.atShadow = atShadow
        at.targetFileName = fileName
        at.tnodeList = []
            # Needed until old-style @file nodes are no longer supported.
        at.tnodeListIndex = 0
        at.v = None
        at.vStack = [] # Stack of at.v values.
        if allow_cloned_sibs:
            at.thinChildIndexStack = [] # 2013/01/20: number of siblings at this level.
        at.thinFile = False # 2010/01/22: was thinFile
        at.thinNodeStack = [] # Entries are vnodes.
        at.updateWarningGiven = False
    #@+node:ekr.20041005105605.15: *3* at.initWriteIvars
    def initWriteIvars(self,root,targetFileName,
        atAuto=False,atEdit=False,atShadow=False,
        forcePythonSentinels=None,
        nosentinels=False,
        perfectImportFlag = False,
        scriptWrite=False,
        thinFile=False,
        toString=False,
    ):
        at,c = self,self.c
        assert root
        self.initCommonIvars()

        assert at.checkPythonCodeOnWrite is not None
        assert at.underindentEscapeString is not None

        at.atAuto = atAuto
        at.atEdit = atEdit
        at.atShadow = atShadow
        # at.default_directory: set by scanAllDirectives()
        at.docKind = None
        if forcePythonSentinels:
            at.endSentinelComment = None
        # else: at.endSentinelComment set by initCommonIvars.
        # at.encoding: set by scanAllDirectives() below.
        # at.explicitLineEnding # True: an @lineending directive specifies the ending.
            # Set by scanAllDirectives() below.
        at.fileChangedFlag = False # True: the file has actually been updated.
        at.force_newlines_in_at_nosent_bodies = c.config.getBool(
            'force_newlines_in_at_nosent_bodies')
        if forcePythonSentinels is None:
            forcePythonSentinels = scriptWrite
        # at.language:      set by scanAllDirectives() below.
        # at.outputFile:    set below.
        # at.outputNewline: set below.
        if forcePythonSentinels:
            # Force Python comment delims for g.getScript.
            at.startSentinelComment = "#"
        # else:                 set by initCommonIvars.
        # at.stringOutput:      set below.
        # at.outputFileName:    set below.
        # at.output_newline:    set by scanAllDirectives() below.
        # at.page_width:        set by scanAllDirectives() below.
        at.outputContents = None
        at.perfectImportFlag = perfectImportFlag
        at.sentinels = not nosentinels
        at.shortFileName = ""   # For messages.
        at.root = root
        # at.tab_width:         set by scanAllDirectives() below.
        at.targetFileName = targetFileName
            # Must be None for @shadow.
        at.thinFile = thinFile
        at.toString = toString
        at.writeVersion5 = not atShadow

        at.scanAllDirectives(root,
            scripting=scriptWrite,
            forcePythonSentinels=forcePythonSentinels,
            issuePathWarning=True,
        )
        # Sets the following ivars:
            # at.default_directory
            # at.encoding
            # at.explicitLineEnding
            # at.language
            # at.output_newline
            # at.page_width
            # at.tab_width

        # 2011/10/21: Encoding directive overrides everything else.
        if at.language == 'python':
            encoding = g.getPythonEncodingFromString(root.b)
            if encoding:
                at.encoding = encoding
                # g.trace('scanned encoding',encoding)
        if toString:
            at.outputFile = g.fileLikeObject()
            if g.app.unitTesting:
                at.output_newline = '\n'
            # else: at.output_newline set in initCommonIvars.
            at.stringOutput = ""
            at.outputFileName = "<string-file>"
        else:
            # at.outputNewline set in initCommonIvars.
            at.outputFile = None
            at.stringOutput = None
            at.outputFileName = g.u('')

        # Init all other ivars even if there is an error.
        if not at.errors and at.root:
            if hasattr(at.root.v,'tnodeList'):
                delattr(at.root.v,'tnodeList')
            at.root.v._p_changed = True
    #@+node:ekr.20130911110233.11286: *3* at.initReadLine
    def initReadLine(self,s):
        
        '''Init the ivars so that at.readLine will read all of s.'''
        
        # This is part of the new_read logic.
        at = self
        at.read_i = 0
        at.read_lines = g.splitLines(s)
    #@+node:ekr.20041005105605.17: ** at.Reading
    #@+<< about new sentinels >>
    #@+node:ekr.20100619222623.5918: *3* << about new sentinels >>
    #@@nocolor-node
    #@+at
    # 
    # Surprisingly, it's easier to read new sentinels than to read old sentinels:
    # 
    # - There must be closing sentinels for section references and the @all and
    #   @others directives, collectively known as **embedding constructs.** Indeed,
    #   these constructs do not terminate the node in which they appear, so without a
    #   closing sentinel there would be no way to know where the construct ended and
    #   the following lines of the enclosing node began.
    # 
    # - The read code "accumulates" body text of node v in v.tempBodyList, a list of
    #   lines. A post-pass assigns v.tempBodyString = ''.join(v.tempBodyList). This
    #   assignment **terminates** the node.
    # 
    # - The new read code *never* terminates the body text of a node until the
    #   post-pass. This is the crucial simplification that allows the read code not to
    #   need @-node sentinels.
    # 
    # - An older version of the body text exists for v iff v has the tempBodyString
    #   attribute. It is *essential* not to create this attribute until finalizing v.
    #   The read code warns (creates a "Recovered Nodes" node) if the previous value
    #   of v.tempBodyString does not match ''.join(tempBodyList) when v is terminated.
    # 
    # - The read code for new sentinels creates nodes using the node-level stars, by
    #   making the new node at level N a child of of the previous node at level N-1.
    # 
    # Other notes.
    # 
    # - Leo no longer maintains the "spelling" of whitespace before embedding constructs.
    #   This can never cause any harm.
    # 
    # - Leo does not write @nonl or @nl sentinels when writing new sentinels. In
    #   effect, this "regularizes" body text so that it always ends with at least one
    #   blank. Again, this can never cause any harm, because nodes must be terminated
    #   (in the external file), by a newline the precedes the next sentinel.
    #   Eliminating @nonl and @nl sentinels simplifies the appearance of the external
    #   file and reduces spurious sccs diffs.
    # 
    # - Leo always writes private @shadow files using old sentines. This guarantees
    #   permanent compatibility with older versions of Leo.
    #@-<< about new sentinels >>
    #@+node:ekr.20041005105605.18: *3* Reading (top level)
    #@+at All reading happens in the readOpenFile logic, so plugins
    # should need to override only this method.
    #@+node:ekr.20070919133659: *4* at.checkDerivedFile
    def checkDerivedFile (self, event=None):

        '''Make sure an external file written by Leo may be read properly.'''

        at = self ; c = at.c ; p = c.p

        if not p.isAtFileNode() and not p.isAtThinFileNode():
            return g.red('Please select an @thin or @file node')

        fn = p.anyAtFileNodeName()
        path = g.os_path_dirname(c.mFileName)
        fn = g.os_path_finalize_join(g.app.loadDir,path,fn)
        if not g.os_path_exists(fn):
            return g.error('file not found: %s' % (fn))

        s,e = g.readFileIntoString(fn)
        if s is None: return

        # Create a dummy, unconnected, vnode as the root.
        root_v = leoNodes.vnode(context=c)
        root = leoNodes.position(root_v)
        # 2010/01/22: readOpenFiles now determines whether a file is thin or not.
        at.initReadIvars(root,fn)
        if at.errors: return
        at.openFileForReading(fromString=s)
        if not at.inputFile: return
        at.readOpenFile(root,at.inputFile,fn)
        at.inputFile.close()
        if at.errors == 0:
            g.blue('check-derived-file passed')
    #@+node:ekr.20041005105605.19: *4* at.openFileForReading
    def openFileForReading(self,fromString=False):

        '''Open the file given by at.root.
        This will be the private file for @shadow nodes.'''

        trace = False and not g.app.unitTesting
        at = self
        if fromString:
            if at.atShadow:
                return at.error(
                    'can not call at.read from string for @shadow files')
            at.inputFile = g.fileLikeObject(fromString=fromString)
            fn = None
        else:
            fn = at.fullPath(at.root)
                # Returns full path, including file name.
            at.setPathUa(at.root,fn)
                # Remember the full path to this node.
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
                if trace:
                    g.trace('         fn:       ',fn)
                    g.trace('reading: shadow_fn:',shadow_fn)
                x.updatePublicAndPrivateFiles(at.root,fn,shadow_fn)
                fn = shadow_fn
            try:
                # Open the file in binary mode to allow 0x1a in bodies & headlines.
                at.inputFile = f = open(fn,'rb')
                s = f.read()
                at.bom_encoding,s = g.stripBOM(s)
                e = at.bom_encoding or at.encoding
                s = g.toUnicode(s,e)
                s = s.replace('\r\n','\n')
                at.read_lines = g.splitLines(s)
                if trace: g.trace(at.bom_encoding,fn)
                at.warnOnReadOnlyFile(fn)
            except IOError:
                at.error("can not open: '@file %s'" % (fn))
                at.inputFile = None
                fn = None
        return fn
    #@+node:ekr.20041005105605.21: *4* at.read & helpers
    def read(self,root,importFileName=None,
        fromString=None,atShadow=False,force=False
    ):

        """Read an @thin or @file tree."""

        trace = False and not g.unitTesting
        if trace: g.trace(root.h)
        at = self ; c = at.c
        fileName = at.initFileName(fromString,importFileName,root)
        if not fileName:
            at.error("Missing file name.  Restoring @file tree from .leo file.")
            return False
        # Fix bug 760531: always mark the root as read, even if there was an error.
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(at.fullPath(root),root)

        # Bug fix 2011/05/23: Restore orphan trees from the outline.
        if root.isOrphan():
            g.es("reading:",root.h)
            # g.warning('The outline contains an orphan node!\nRetaining the outline')
            g.error('orphan node in',root.h)
            g.blue('retaining the data from the .leo file')
            return False
        at.initReadIvars(root,fileName,
            importFileName=importFileName,atShadow=atShadow)
        at.fromString = fromString
        if at.errors:
            if trace: g.trace('Init error')
            return False
        fileName = at.openFileForReading(fromString=fromString)
            # For @shadow files, calls x.updatePublicAndPrivateFiles.
        if fileName and at.inputFile:
            c.setFileTimeStamp(fileName)
        elif fromString: # 2010/09/02.
            pass
        else:
            if trace: g.trace('No inputFile')
            return False

        # Get the file from the cache if possible.
        if fromString:
            s,loaded,fileKey = fromString,False,None
        else:
            s,loaded,fileKey = c.cacher.readFile(fileName,root)
        # Never read an external file with file-like sentinels from the cache.
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
                g.red("converting @file format in",root.h)
        root.clearVisitedInTree()

        at.scanAllDirectives(root,importing=at.importing,reading=True)
            # Sets the following ivars:
                # at.default_directory
                # at.encoding: **Important**: changed later
                #     by readOpenFile/at.scanHeader.
                # at.explicitLineEnding
                # at.language
                # at.output_newline
                # at.page_width
                # at.tab_width

        if trace: g.trace(repr(at.encoding),fileName)
        thinFile = at.readOpenFile(root,at.inputFile,fileName,deleteNodes=True)
            # Calls at.scanHeader, which sets at.encoding.
        at.inputFile.close()
        root.clearDirty() # May be set dirty below.
        if at.errors == 0:
            at.deleteUnvisitedNodes(root)
            at.deleteTnodeList(root)
        if at.errors == 0 and not at.importing:
            # Used by mod_labels plugin.
            at.copyAllTempBodyStringsToVnodes(root,thinFile)
        at.deleteAllTempBodyStrings()
        if isFileLike and at.errors == 0: # Old-style sentinels.
            # 2010/02/24: Make the root @file node dirty so it will
            # be written automatically when saving the file.
            # Do *not* set the orphan bit here!
            root.clearOrphan()
            root.setDirty()
            c.setChanged(True) # Essential, to keep dirty bit set.
        elif at.errors > 0:
            # 2010/10/22: Dirty bits are *always* cleared.
            # Only the orphan bit is preserved.
            # root.setDirty() # 2011/06/17: Won't be preserved anyway
            root.setOrphan()
            # c.setChanged(True) # 2011/06/17.
        else:
            root.clearOrphan()
        if at.errors == 0 and not isFileLike and not fromString:
            c.cacher.writeFile(root,fileKey)

        if trace: g.trace('at.errors',at.errors)
        return at.errors == 0
    #@+node:ekr.20041005105605.25: *5* at.deleteAllTempBodyStrings
    def deleteAllTempBodyStrings(self):

        for v in self.c.all_unique_nodes():
            if hasattr(v,"tempBodyString"):
                delattr(v,"tempBodyString")
            if hasattr(v,"tempBodyList"):
                delattr(v,"tempBodyList")
    #@+node:ekr.20100122130101.6174: *5* at.deleteTnodeList
    def deleteTnodeList (self,p): # atFile method.

        '''Remove p's tnodeList.'''

        v = p.v

        if hasattr(v,"tnodeList"):

            if False: # Not an error, but a useful trace.
                g.blue("deleting tnodeList for " + repr(v))

            delattr(v,"tnodeList")
            v._p_changed = True
    #@+node:ekr.20071105164407: *5* at.deleteUnvisitedNodes & helpers
    def deleteUnvisitedNodes (self,root):

        '''Delete unvisited nodes in root's subtree, not including root.

        Actually, instead of deleting the nodes, we move them to be children of the
        'Resurrected Nodes' r.
        '''

        at = self
        # Find the unvisited nodes.
        aList = [z.copy() for z in root.subtree() if not z.isVisited()]
        if aList:
            r = at.createResurrectedNodesNode()
            assert r not in aList
            callback=at.defineResurrectedNodeCallback(r,root)
            # Move the nodes using the callback.
            at.c.deletePositionsInList(aList,callback)
    #@+node:ekr.20100803073751.5817: *6* createResurrectedNodesNode
    def createResurrectedNodesNode(self):

        '''Create a 'Resurrected Nodes' node as the last top-level node.'''

        at = self ; c = at.c ; tag = 'Resurrected Nodes'
        # Find the last top-level node.
        last = c.rootPosition()
        while last.hasNext():
            last.moveToNext()
        # Create the node after last if it doesn't exist.
        if last.h == tag:
            p = last
        else:
            p = last.insertAfter()
            p.setHeadString(tag)
        p.expand()
        return p
    #@+node:ekr.20100803073751.5818: *6* defineResurrectedNodeCallback **
    def defineResurrectedNodeCallback (self,r,root):
        '''Define a callback that moves node p as r's last child.'''
        
        trace = True and not g.unitTesting

        def callback(p,r=r.copy(),root=root):
            '''The resurrected nodes callback.'''
            child = r.insertAsLastChild()
            child.h = 'From %s' % root.h
            v = p.v
            if 1: # new code: based on vnodes.
                import leo.core.leoNodes as leoNodes
                for parent_v in v.parents:
                    assert isinstance(parent_v,leoNodes.vnode),parent_v
                    if v in parent_v.children:
                        childIndex = parent_v.children.index(v)
                        if trace: g.trace('*moving*',parent_v,childIndex,v)
                        v._cutLink(childIndex,parent_v)
                        v._addLink(len(child.v.children),child.v)
                    else:
                        # This would be surprising.
                        g.trace('**already deleted**',parent_v,v)
            else: # old code, based on positions.
                p.moveToLastChildOf(child)
            if not g.unitTesting:
                g.error('resurrected node:',v.h)
                g.blue('in file:',root.h)
        
        return callback
    #@+node:ekr.20041005105605.22: *5* at.initFileName
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
    #@+node:ekr.20100224050618.11547: *5* at.isFileLike
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
    #@+node:ekr.20041005105605.26: *4* at.readAll
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
        c.init_error_dialogs()

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
                if p.isAnyAtFileNode() :
                    c.ignored_at_file_nodes.append(p.h)
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
                    # However, the dirty bit gets cleared.
                    # p.setDirty() # 2011/06/17: won't be preserved anyway.
                        # Expensive, but it can't be helped.
                    p.setOrphan() # 2010/10/22: the dirty bit gets cleared.
                    # c.setChanged(True) # 2011/06/17
                p.moveToNodeAfterTree()
            else:
                if p.isAtAsisFileNode() or p.isAtNoSentFileNode():
                    at.rememberReadPath(at.fullPath(p),p)
                p.moveToThreadNext()

        # 2010/10/22: Preserve the orphan bits: the dirty bits will be cleared!
        #for v in c.all_unique_nodes():
        #    v.clearOrphan()

        if partialFlag and not anyRead and not g.unitTesting:
            g.es("no @<file> nodes in the selected tree")

        if use_tracer: tt.stop()

        c.raise_error_dialogs()  # 2011/12/17
    #@+node:ekr.20080801071227.7: *4* at.readAtShadowNodes
    def readAtShadowNodes (self,p):

        '''Read all @shadow nodes in the p's tree.'''

        at = self
        after = p.nodeAfterTree()
        p = p.copy() # Don't change p in the caller.
        while p and p != after: # Don't use iterator.
            if p.isAtShadowFileNode():
                fileName = p.atShadowFileNodeName()
                at.readOneAtShadowNode (fileName,p)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20070909100252: *4* at.readOneAtAutoNode
    def readOneAtAutoNode (self,fileName,p):

        at,c,ic = self,self.c,self.c.importCommands
        oldChanged = c.isChanged()
        at.default_directory = g.setDefaultDirectory(c,p,importing=True)
        fileName = c.os_path_finalize_join(at.default_directory,fileName)
        if not g.os_path_exists(fileName):
            g.error('not found: @auto %s' % (fileName))
            return
        # Remember that we have seen the @auto node.
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fileName,p)
        s,ok,fileKey = c.cacher.readFile(fileName,p)
        if ok:
            g.doHook('after-auto',c=c,p=p)
                # call after-auto callbacks
                # 2011/09/30: added call to g.doHook here.
            return
        if not g.unitTesting:
            g.es("reading:",p.h)
        try:
            # 2012/04/09: catch failed asserts in the import code.
            ic.createOutline(fileName,parent=p.copy(),atAuto=True)
        except AssertionError:
            ic.errors += 1
        if ic.errors:
            # Read the entire file into the node.
            g.error('errors inhibited read @auto %s' % (fileName))
            if 0:
                g.es_print('reading entire file into @auto node.')
                at.readOneAtEditNode(fileName,p)
        if ic.errors or not g.os_path_exists(fileName):
            p.clearDirty()
            c.setChanged(oldChanged)
        else:
            c.cacher.writeFile(p,fileKey)
            g.doHook('after-auto',c=c,p=p)
    #@+node:ekr.20090225080846.3: *4* at.readOneAtEditNode
    def readOneAtEditNode (self,fn,p):

        at = self
        c = at.c
        ic = c.importCommands
        at.default_directory = g.setDefaultDirectory(c,p,importing=True)
        fn = c.os_path_finalize_join(at.default_directory,fn)
        junk,ext = g.os_path_splitext(fn)

        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fn,p)

        if not g.unitTesting:
            g.es("reading: @edit %s" % (g.shortFileName(fn)))

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
    #@+node:ekr.20080711093251.7: *4* at.readOneAtShadowNode
    def readOneAtShadowNode (self,fn,p,force=False):

        trace = False and not g.unitTesting
        at = self ; c = at.c ; x = c.shadowController

        if not fn == p.atShadowFileNodeName():
            return at.error('can not happen: fn: %s != atShadowNodeName: %s' % (
                fn, p.atShadowFileNodeName()))

        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fn,p)

        at.default_directory = g.setDefaultDirectory(c,p,importing=True)
        fn = c.os_path_finalize_join(at.default_directory,fn)
        shadow_fn     = x.shadowPathName(fn)
        shadow_exists = g.os_path_exists(shadow_fn) and g.os_path_isfile(shadow_fn)

        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()

        if trace:
            g.trace('shadow_exists',shadow_exists,shadow_fn)

        if shadow_exists:
            at.read(p,atShadow=True,force=force)
        else:
            if not g.unitTesting: g.es("reading:",p.h)
            ok = at.importAtShadowNode(fn,p)
            if ok:
                # Create the private file automatically.
                at.writeOneAtShadowNode(p,toString=False,force=True)
    #@+node:ekr.20080712080505.1: *5* at.importAtShadowNode
    def importAtShadowNode (self,fn,p):

        at = self ; c = at.c  ; ic = c.importCommands
        oldChanged = c.isChanged()

        # Delete all the child nodes.
        while p.hasChildren():
            p.firstChild().doDelete()

        # Import the outline, exactly as @auto does.
        ic.createOutline(fn,parent=p.copy(),atAuto=True,atShadow=True)

        if ic.errors:
            g.error('errors inhibited read @shadow',fn)

        if ic.errors or not g.os_path_exists(fn):
            p.clearDirty()
            c.setChanged(oldChanged)

        # else: g.doHook('after-shadow', p = p)

        return ic.errors == 0
    #@+node:ekr.20041005105605.27: *4* at.readOpenFile & helpers
    def readOpenFile(self,root,theFile,fileName,deleteNodes=False):

        '''Read an open derived file.

        Leo 4.5 and later can only read 4.x derived files.'''

        trace = False and not g.unitTesting
        at = self
        firstLines,read_new,thinFile = at.scanHeader(theFile,fileName)
            # Important: this sets at.encoding, used by at.readLine.
        at.thinFile = thinFile
            # 2010/01/22: use *only* the header to set self.thinFile.
        if deleteNodes and at.shouldDeleteChildren(root,thinFile):
            # Fix bug 889175: Remember the full fileName.
            at.rememberReadPath(fileName,root)
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
                # g.es('you may upgrade these file using Leo 4.0 through 4.4.x')
                g.es("Please use Leo's import command to read the file")
                # g.trace('root',root and root.h,fileName)
        if root:
            root.v.setVisited() # Disable warning about set nodes.
        #@+<< handle first and last lines >>
        #@+node:ekr.20041005105605.28: *5* << handle first and last lines >> (at.readOpenFile)
        # The code below only deals with the root node!
        # We terminate the root's body text if it exists.
        # This is a hack to allow us to handle @first and @last.
        v = root.v
        tempString = hasattr(v,'tempBodyString') and v.tempBodyString or ''
        tempList = hasattr(v,'tempBodyList') and ''.join(v.tempBodyList) or ''

        if at.readVersion5:
            if hasattr(v,'tempBodyList'):
                body = tempList
                delattr(v,'tempBodyList') # So the change below "takes".
            elif hasattr(v,'tempBodyString'):
                body = tempString
                delattr(v,'tempBodyString')
            else:
                body = ''
        else:
            body = tempString

        lines = body.split('\n')

        at.completeFirstDirectives(lines,firstLines)
        at.completeLastDirectives(lines,lastLines)

        s = '\n'.join(lines).replace('\r', '')

        # *Always* put the temp body text into at.v.tempBodyString.
        v.tempBodyString = s
        #@-<< handle first and last lines >>
        if trace: g.trace(at.encoding,fileName) # root.v.tempBodyString)
        return thinFile
    #@+node:ekr.20100122130101.6175: *5* at.shouldDeleteChildren
    def shouldDeleteChildren (self,root,thinFile):

        '''Return True if we should delete all children before a read.'''

        # Delete all children except for old-style @file nodes

        if root.isAtNoSentFileNode():
            return False
        elif root.isAtFileNode() and not thinFile:
            return False
        else:
            return True
    #@+node:ekr.20041005105605.117: *5* at.completeFirstDirective
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
    #@+node:ekr.20041005105605.118: *5* at.completeLastDirectives
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
    #@+node:ekr.20041005105605.71: *3* Reading (4.x)
    #@+node:ekr.20041005105605.73: *4* at.findChild4
    def findChild4 (self,headline):

        """Return the next vnode in at.root.tnodeList.
        This is called only for **legacy** @file nodes"""

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
    #@+node:ekr.20130911110233.11284: *4* at.readFileToUnicode & helpers
    def readFileToUnicode(self,fn):
        
        '''Read the file into a unicode string s and return same.
        
        Set at.encoding and init at.readLines if all went well.
        
        Return None on failure.
        '''
        
        # This is part of the new_read logic.
        at = self
        s = at.openFileHelper(fn)
        if s is not None:
            e,s = g.stripBOM(s)
            if e:
                # The BOM determines the encoding unambiguously.
                s = g.toUnicode(s,encoding=e)
            else:
                # Get the encoding from the header, or the default encoding.
                if g.isPython3: # Must convert s to unicode first.
                    s = g.toUnicode(s,'ascii',reportErrors=False)
                e = at.getEncodingFromHeader(fn,s)
                s = g.toUnicode(s,encoding=e)
            at.encoding = e
            at.initReadLine(s)
        return s
    #@+node:ekr.20130911110233.11285: *5* at.openFileHelper
    def openFileHelper(self,fn):
        
        at = self
        s = None
        try:
            f = open(fn,'rb')
            s = f.read()
            f.close()
        except IOError:
            at.error('can not open %s' % (fn))
        except Exception:
            at.error('Exception reading %s' % (fn))
            g.es_exception()
        return s
    #@+node:ekr.20130911110233.11287: *5* at.getEncodingFromHeader
    def getEncodingFromHeader(self,fn,s):
        
        ''' Return the encoding given in the @+leo sentinel, if the sentinel is
        present, or the default external encoding otherwise.
        
        '''
        
        at = self
        if at.errors:
            g.trace('can not happen: at.errors > 0')
            e = at.encoding
        else:
            at.initReadLine(s)
            default_encoding = at.encoding
            assert default_encoding
            at.encoding = None
            # Execute scanHeader merely to set at.encoding.
            at.scanHeader(None,fn,giveErrors=False)
            e = at.encoding or default_encoding
        assert e
        return e
    #@+node:ekr.20041005105605.74: *4* at.scanText4 & allies
    def scanText4 (self,theFile,fileName,p,verbose=False):

        """Scan a 4.x derived file non-recursively."""

        at = self
        trace = False and at.readVersion5 and not g.unitTesting
        verbose = False
        #@+<< init ivars for scanText4 >>
        #@+node:ekr.20041005105605.75: *5* << init ivars for scanText4 >>
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
        at.vStack = []

        # New code: always identify root @thin node with self.root:
        if allow_cloned_sibs:
            at.thinChildIndexStack = []
        at.lastThinNode = None
        at.thinNodeStack = []
        #@-<< init ivars for scanText4 >>
        if trace: g.trace('filename:',fileName)
        try:
            while at.errors == 0 and not at.done:
                s = at.readLine() ### theFile)
                if trace and verbose: g.trace(repr(s))
                at.lineNumber += 1
                if len(s) == 0:
                    # An error.  We expect readEndLeo to set at.done.
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
            at.error('scanText4: unexpected assertion failure in',
                g.choose(at.fromString,'fromString',fileName),
                '\n',message)
            g.trace(g.callers(5))
            raise
        except Exception:
            # Work around bug https://bugs.launchpad.net/leo-editor/+bug/1074812
            # Crashes in the scanning logic may arise from corrupted external files.
            at.error('The input file appears to be corrupted.')
        if at.errors == 0 and not at.done:
            #@+<< report unexpected end of text >>
            #@+node:ekr.20041005105605.76: *5* << report unexpected end of text >>
            assert at.endSentinelStack,'empty sentinel stack'

            at.readError(
                "Unexpected end of file. Expecting %s sentinel" %
                at.sentinelName(at.endSentinelStack[-1]))
            #@-<< report unexpected end of text >>
        return at.lastLines
    #@+node:ekr.20041005105605.77: *5* at.readNormalLine & appendToDocPart
    def readNormalLine (self,s,i=0): # i not used.

        at = self

        # g.trace('inCode',at.inCode,repr(s))

        if at.inCode:
            if not at.raw:
                # 2012/06/05: Major bug fix: insert \\-n. for underindented lines.
                n = g.computeLeadingWhitespaceWidth(s,at.tab_width)
                if n < at.indent:
                    # g.trace('n: %s at.indent: %s\n%s' % (n,at.indent,repr(s)))
                    if s.strip():
                        s = r'\\-%s.%s' % (at.indent-n,s.lstrip())
                    else:
                        s = '\n' if s.endswith('\n') else ''
                else: # Legacy
                    s = g.removeLeadingWhitespace(s,at.indent,at.tab_width)
            at.appendToOut(s)
        else:
            at.appendToDocPart(s)
    #@+node:ekr.20100624082003.5942: *6* at.appendToDocPart
    def appendToDocPart (self,s):

        at = self
        trace = False and at.readVersion5 and not g.unitTesting

        # Skip the leading stuff
        if len(at.endSentinelComment) == 0:
            # Skip the single comment delim and a blank.
            i = g.skip_ws(s,0)
            if g.match(s,i,at.startSentinelComment):
                i += len(at.startSentinelComment)
                if g.match(s,i," "): i += 1
        else:
            i = at.skipIndent(s,0,at.indent)

        if at.readVersion5:
            # Append the line to docOut.
            line = s[i:]
            at.docOut.append(line)
        else:
            # Append line to docOut, possibly stripping the newline.
            line = s[i:-1] # remove newline for rstrip.

            if line == line.rstrip():
                # no trailing whitespace: the newline is real.
                at.docOut.append(line + '\n')
            else:
                # trailing whitespace: the newline is fake.
                at.docOut.append(line)

        if trace: g.trace(repr(line))
    #@+node:ekr.20041005105605.80: *5* start sentinels
    #@+node:ekr.20041005105605.81: *6* at.readStartAll
    def readStartAll (self,s,i):

        """Read an @+all sentinel."""

        at = self
        j = g.skip_ws(s,i)
        leadingWs = s[i:j]

        if leadingWs:
            assert g.match(s,j,"@+all"),'missing @+all'
        else:
            assert g.match(s,j,"+all"),'missing +all'

        # Make sure that the generated at-all is properly indented.
        # New code (for both old and new sentinels).
        # Regularize the whitespace preceding the @all directive.
        junk_i,w = g.skip_leading_ws_with_indent(s,0,at.tab_width)
        lws2 = g.computeLeadingWhitespace(max(0,w-at.indent),at.tab_width)
        at.appendToOut(lws2 + "@all\n")

        at.endSentinelStack.append(at.endAll)
        if at.readVersion5:
            at.endSentinelNodeStack.append(at.v)
            at.endSentinelLevelStack.append(len(at.thinNodeStack))
    #@+node:ekr.20041005105605.85: *6* at.readStartNode & helpers
    def readStartNode (self,s,i,middle=False):

        """Read an @+node or @+middle sentinel."""

        at = self
        gnx,headline,i,level,ok = at.parseNodeSentinel(s,i,middle)
        if not ok: return
        at.root_seen = True

        # Switch context.
        if at.readVersion5:
            # Terminate the *previous* doc part if it exists.
            if at.docOut:
                at.appendToOut(''.join(at.docOut))
                at.docOut = []
            # Important: with new sentinels we *never*
            # terminate nodes until the post-pass.
        else:
            assert not at.docOut,'not at.docOut' # Cleared by @-node sentinel.
            at.outStack.append(at.out)
            at.out = []

        at.inCode = True
        at.raw = False # End raw mode.

        at.vStack.append(at.v)

        at.indentStack.append(at.indent)
        i,at.indent = g.skip_leading_ws_with_indent(s,0,at.tab_width)

        if at.importing:
            p = at.createImportedNode(at.root,headline)
            at.v = p.v
        elif at.thinFile:
            at.v = at.createNewThinNode(gnx,headline,level)
        else:
            at.v = at.findChild4(headline)

        if not at.v:
            return # 2010/08/02: This can happen when reading strange files.

        if allow_cloned_sibs:
            assert at.v == at.root.v or at.v.isVisited(),at.v.h

        at.v.setVisited()
            # Indicate that the vnode has been set in the external file.

        if not at.readVersion5:
            at.endSentinelStack.append(at.endNode)
    #@+node:ekr.20100625085138.5957: *7* at.createNewThinNode & helpers
    def createNewThinNode (self,gnx,headline,level):

        at = self

        if at.thinNodeStack:
            if at.readVersion5:
                v = self.createV5ThinNode(gnx,headline,level)
            else:
                at.thinNodeStack.append(at.lastThinNode)
                v = at.old_createThinChild4(gnx,headline)
        else:
            v = at.root.v
            if allow_cloned_sibs and at.readVersion5:
                at.thinChildIndexStack.append(0)
            at.thinNodeStack.append(v)

        at.lastThinNode = v
        return v
    #@+node:ekr.20130121102015.10272: *8* at.createV5ThinNode
    def createV5ThinNode(self,gnx,headline,level):

        at = self
        trace = False and not g.unitTesting # at.readVersion5 and 
        oldLevel = len(at.thinNodeStack)
        newLevel = level
        assert oldLevel >= 1
        assert newLevel >= 1
        # The invariant: top of at.thinNodeStack after changeLevel is the parent.
        at.changeLevel(oldLevel,newLevel-1)
        if allow_cloned_sibs:
            parent = at.thinNodeStack[-1]
            n = at.thinChildIndexStack[-1]
            if trace: g.trace(oldLevel,newLevel-1,n,parent.h,headline)
            v = at.new_createThinChild4(gnx,headline,n,parent)
            at.thinChildIndexStack[-1]=n+1
            at.thinNodeStack.append(v)
            at.thinChildIndexStack.append(0)
            at.lastThinNode = v
            # Ensure that the body text is set only once.
            if v.isVisited():
                if hasattr(v,'tempBodyList'):
                    delattr(v,'tempBodyList')
            else:
                # This is the only place we call v.setVisited in the read logic.
                v.setVisited()
        else:
            v = at.old_createThinChild4(gnx,headline)
            at.thinNodeStack.append(v)
        # Common exit code. 
        # Terminate a previous clone if it exists.
        # Do not use the full terminateNode logic!
        if hasattr(v,'tempBodyList'):
            # To keep pylint happy.
            v.tempBodyString = ''.join(getattr(v,'tempBodyList'))
            delattr(v,'tempBodyList')
        else:
            # Major bug fix: 2010/07/6:
            # Do *not* create v.tempBodyString here!
            # That would tell at.copyAllTempBodyStringsToVnodes
            # that an older (empty) version exists!
            pass
        return v
    #@+node:ekr.20130121075058.10245: *8* at.old_createThinChild4
    def old_createThinChild4 (self,gnxString,headline):

        """Find or create a new *vnode* whose parent (also a vnode)
        is at.lastThinNode. This is called only for @thin trees."""

        trace = False and not g.unitTesting
        verbose = True
        at = self ; c = at.c
        indices = g.app.nodeIndices
        gnx = indices.scanGnx(gnxString,0)
        gnxDict = c.fileCommands.gnxDict

        last = at.lastThinNode # A vnode.
        lastIndex = last.fileIndex
        if trace and verbose: g.trace("last %s, gnx %s %s" % (
            last and last.h,gnxString,headline))
        parent = last
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
            v = gnxDict.get(gnxString)
            if v:
                if gnx != v.fileIndex:
                    g.internalError('v.fileIndex: %s gnx: %s' % (
                        v.fileIndex,gnx))
            else:
                v = leoNodes.vnode(context=c)
                v._headString = headline # Allowed use of v._headString.
                v.fileIndex = gnx
                gnxDict[gnxString] = v

            child = v
            child._linkAsNthChild(parent,parent.numberOfChildren())

        if trace: g.trace('new node: %s' % child.h)
        child.setVisited() # Supress warning/deletion of unvisited nodes.
        return child
    #@+node:ekr.20130121075058.10246: *8* at.new_createThinChild4
    def new_createThinChild4 (self,gnxString,headline,n,parent):

        """Find or create a new *vnode* whose parent (also a vnode)
        is at.lastThinNode. This is called only for @thin trees."""

        trace = False and not g.unitTesting
        at = self ; c = at.c ; indices = g.app.nodeIndices
        if trace: g.trace(n,len(parent.children),parent.h,' -> ',headline)
            # at.thinChildIndexStack,[z.h for z in at.thinNodeStack],
            
        gnx = indices.scanGnx(gnxString,0)
        gnxDict = c.fileCommands.gnxDict
        v = gnxDict.get(gnxString)
        if v:
            if gnx == v.fileIndex:
                # Always use v.h, regardless of headline.
                if trace and v.h != headline:
                    g.trace('read error v.h: %s headline: %s' % (v.h,headline))
                child = v
                if n >= len(parent.children):
                    child._linkAsNthChild(parent,n)
                    if trace: g.trace('OLD n: %s parent: %s -> %s\n' % (n,parent.h,child.h))
                else:
                    if trace: g.trace('DUP n: %s parent: %s -> %s\n' % (n,parent.h,child.h))
            else:
                gnx_s = g.app.nodeIndices.toString(gnx)
                g.internalError('v.fileIndex: %s gnx: %s' % (v.fileIndex,gnx_s))
                return None
        else:
            v = leoNodes.vnode(context=c)
            v._headString = headline # Allowed use of v._headString.
            v.fileIndex = gnx
            gnxDict[gnxString] = v
            child = v
            child._linkAsNthChild(parent,n)
            if trace: g.trace('NEW n: %s parent: %s -> %s\n' % (n,parent.h,child.h))

        return child
    #@+node:ekr.20100625184546.5979: *7* at.parseNodeSentinel & helpers
    def parseNodeSentinel (self,s,i,middle):

        at = self

        if middle:
            assert g.match(s,i,"+middle:"),'missing +middle'
            i += 8
        else:
            if not g.match(s,i,'+node:'): g.trace(repr(s[i:i+40]),g.callers(5))
            assert g.match(s,i,"+node:"),'missing +node:'
            i += 6

        # Get the gnx and the headline.
        if at.thinFile:
            gnx,i,level,ok = at.parseThinNodeSentinel(s,i)
            if not ok: return None,None,None,False
        else:
            gnx,level = None,None

        headline = at.getNodeHeadline(s,i)
        return gnx,headline,i,level,True
    #@+node:ekr.20100625085138.5955: *8* at.getNodeHeadline
    def getNodeHeadline (self,s,i):

        '''Set headline to the rest of the line.
        Don't strip leading whitespace.'''

        at = self

        if len(at.endSentinelComment) == 0:
            h = s[i:-1].rstrip()
        else:
            k = s.rfind(at.endSentinelComment,i)
            h = s[i:k].rstrip() # works if k == -1

        # Undo the CWEB hack: undouble @ signs if\
        # the opening comment delim ends in '@'.
        if at.startSentinelComment[-1:] == '@':
            h = h.replace('@@','@')

        return h
    #@+node:ekr.20100625085138.5953: *8* at.parseThinNodeSentinel
    def parseThinNodeSentinel (self,s,i):

        at = self

        def oops(message):
            if g.unitTesting: g.trace(message,repr(s))
            else: at.readError(message)
            return None,None,None,False

        j = s.find(':',i)
        if j == -1:
            return oops('Expecting gnx in @+node sentinel')
        else:
            gnx = s[i:j]

        if at.readVersion5:
            if not g.match(s,j,': '):
                return oops('Expecting space after gnx')
            i = j + 2
            if not g.match(s,i,'*'):
                return oops('No level stars')
            i += 1
            if g.match(s,i,' '):
                level = 1 ; i += 1
            elif g.match(s,i,'* '):
                level = 2 ; i += 2
            else:
                # The level stars have the form *N*.
                level = 0  ; j = i
                while i < len(s) and s[i].isdigit():
                    i += 1
                if i > j:
                    level = int(s[j:i])
                else:
                    return oops('No level number')
                if g.match(s,i,'* '):
                    i += 2
                else:
                    return oops('No space after level stars')
        else: # not readVersion5.
            i = j + 1 # Skip the gnx.
            level = 0

        return gnx,i,level,True
    #@+node:ekr.20041005105605.111: *6* at.readRef (paired using new sentinels)
    #@+at The sentinel contains an @ followed by a section name in angle brackets.
    # This code is different from the code for the @@ sentinel: the expansion
    # of the reference does not include a trailing newline.
    #@@c

    def readRef (self,s,i):

        """Handle an @<< sentinel."""

        at = self

        if at.readVersion5:
            assert g.match(s,i,"+"),'g.match(s,i,"+")'
            i += 1 # Skip the new plus sign.

            # New in Leo 4.8: Ignore the spellling in leadingWs.
            # Instead, compute lws2, the regularized leading whitespace.
            junk_i,w = g.skip_leading_ws_with_indent(s,0,at.tab_width)
            lws2 = g.computeLeadingWhitespace(max(0,w-at.indent),at.tab_width)
        else:
            lws2 = ''

        j = g.skip_ws(s,i)
        assert g.match(s,j,"<<"),'missing @<< sentinel'

        # g.trace(repr(at.endSentinelComment))
        if len(at.endSentinelComment) == 0:
            if at.readVersion5:
                line = lws2 + s[i:]
            else:
                line = s[i:-1] # No trailing newline
        else:
            k = s.find(at.endSentinelComment,i)
            if at.readVersion5:
                line = lws2 + s[i:k] + '\n' # Restore the newline.
            else:
                line = s[i:k] # No trailing newline, whatever k is.
            # g.trace(repr(line))

        # Undo the cweb hack.
        start = at.startSentinelComment
        if start and len(start) > 0 and start[-1] == '@':
            line = line.replace('@@','@')

        at.appendToOut(line)

        if at.readVersion5:
            # g.trace(at.indent,repr(line))
            at.endSentinelLevelStack.append(len(at.thinNodeStack))
            at.endSentinelIndentStack.append(at.indent)
            at.endSentinelStack.append(at.endRef)
            at.endSentinelNodeStack.append(at.v)
        else:
            pass # There is no paired @-ref sentinel.
    #@+node:ekr.20041005105605.82: *6* at.readStartAt/Doc & helpers
    #@+node:ekr.20100624082003.5938: *7* readStartAt
    def readStartAt (self,s,i):

        """Read an @+at sentinel."""

        at = self
        assert g.match(s,i,"+at"),'missing +at'
        i += 3

        if at.readVersion5: # Append whatever follows the sentinel.
            j = at.skipToEndSentinel(s,i)
            follow = s[i:j]
            at.appendToOut('@' + follow + '\n')
            at.docOut = []
            at.inCode = False
        else:
            j = g.skip_ws(s,i)
            ws = s[i:j]
            at.docOut = ['@' + ws + '\n']
                # This newline may be removed by a following @nonl
            at.inCode = False
            at.endSentinelStack.append(at.endAt)
    #@+node:ekr.20100624082003.5939: *7* readStartDoc
    def readStartDoc (self,s,i):

        """Read an @+doc sentinel."""

        at = self
        assert g.match(s,i,"+doc"),'missing +doc'
        i += 4

        if at.readVersion5: # Append whatever follows the sentinel.
            j = at.skipToEndSentinel(s,i)
            follow = s[i:j]+'\n'
            at.appendToOut('@' + follow + '\n')
            at.docOut = []
            at.inCode = False
        else:
            j = g.skip_ws(s,i)
            ws = s[i:j]
            at.docOut = ["@doc" + ws + '\n']
                # This newline may be removed by a following @nonl
            at.inCode = False
            at.endSentinelStack.append(at.endDoc)
    #@+node:ekr.20100624082003.5940: *7* skipToEndSentinel
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
    #@+node:ekr.20041005105605.83: *6* at.readStartLeo
    def readStartLeo (self,s,i):

        """Read an unexpected @+leo sentinel."""

        at = self
        assert g.match(s,i,"+leo"),'missing +leo sentinel'
        at.readError("Ignoring unexpected @+leo sentinel")
    #@+node:ekr.20041005105605.84: *6* at.readStartMiddle
    def readStartMiddle (self,s,i):

        """Read an @+middle sentinel."""

        at = self

        at.readStartNode(s,i,middle=True)
    #@+node:ekr.20041005105605.89: *6* at.readStartOthers
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
        # New code (for both old and new sentinels).
        # Regularize the whitespace preceding the @others directive.
        junk_i,w = g.skip_leading_ws_with_indent(s,0,at.tab_width)
        lws2 = g.computeLeadingWhitespace(max(0,w-at.indent),at.tab_width)
        at.appendToOut(lws2 + "@others\n")

        if at.readVersion5:
            at.endSentinelIndentStack.append(at.indent)
            at.endSentinelStack.append(at.endOthers)
            at.endSentinelNodeStack.append(at.v)
            at.endSentinelLevelStack.append(len(at.thinNodeStack))
        else:
            at.endSentinelStack.append(at.endOthers)
    #@+node:ekr.20041005105605.90: *5* end sentinels
    #@+node:ekr.20041005105605.91: *6* at.readEndAll
    def readEndAll (self,unused_s,unused_i):

        """Read an @-all sentinel."""

        at = self
        at.popSentinelStack(at.endAll)

        if at.readVersion5:

            # Restore the node containing the @all directive.
            # *Never* terminate new-sentinel nodes until the post-pass.
            at.raw = False # End raw mode: 2011/06/13.
            oldLevel = len(at.thinNodeStack)
            newLevel = at.endSentinelLevelStack.pop()
            at.v = at.endSentinelNodeStack.pop() # Bug fix: 2011/06/13.
            at.changeLevel(oldLevel,newLevel)

            # g.trace('oldLevel',oldLevel,'newLevel',newLevel,'at.v',at.v)
    #@+node:ekr.20041005105605.92: *6* at.readEndAt & readEndDoc
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
    #@+node:ekr.20041005105605.93: *6* at.readEndLeo
    def readEndLeo (self,unused_s,unused_i):

        """Read an @-leo sentinel."""

        at = self

        # Ignore everything after @-leo.
        # Such lines were presumably written by @last.
        while 1:
            s = at.readLine() ### at.inputFile)
            if len(s) == 0: break
            at.lastLines.append(s) # Capture all trailing lines, even if empty.

        at.done = True
    #@+node:ekr.20041005105605.94: *6* at.readEndMiddle
    def readEndMiddle (self,s,i):

        """Read an @-middle sentinel."""

        at = self

        at.readEndNode(s,i,middle=True)
    #@+node:ekr.20041005105605.95: *6* at.readEndNode
    def readEndNode (self,unused_s,unused_i,middle=False):

        """Handle @-node sentinels."""

        at = self

        assert not at.readVersion5,'not at.readVersion5'
            # Must not be called for new sentinels.

        at.raw = False # End raw mode.

        at.terminateNode(middle)
            # Set the body text and warn about changed text.
            # This must not be called when handling new sentinels!

        # End the previous node sentinel.
        at.indent = at.indentStack.pop()
        at.out = at.outStack.pop()
        at.docOut = []
        at.v = at.vStack.pop()

        if at.thinFile and not at.importing:
            at.lastThinNode = at.thinNodeStack.pop()

        at.popSentinelStack(at.endNode)
    #@+node:ekr.20041005105605.98: *6* at.readEndOthers
    def readEndOthers (self,unused_s,unused_i):

        """Read an @-others sentinel."""

        at = self

        at.popSentinelStack(at.endOthers)

        if at.readVersion5:
            # g.trace(at.readVersion5,repr(at.docOut))
            # Terminate the *previous* doc part if it exists.
            if at.docOut:
                s = ''.join(at.docOut)
                s = at.massageAtDocPart(s) # 2011/05/24
                at.appendToOut(s)
                at.docOut = []

            # 2010/10/21: Important bug fix: always enter code mode.
            at.inCode = True

            # Restore the node continain the @others directive.
            # *Never* terminate new-sentinel nodes until the post-pass.
            at.raw = False # End raw mode.
            at.v = at.endSentinelNodeStack.pop()
            at.indent = at.endSentinelIndentStack.pop()
            oldLevel = len(at.thinNodeStack)
            newLevel = at.endSentinelLevelStack.pop()
            at.changeLevel(oldLevel,newLevel)
    #@+node:ekr.20100625140824.5968: *6* at.readEndRef
    def readEndRef (self,unused_s,unused_i):

        """Read an @-<< sentinel."""

        at = self

        at.popSentinelStack(at.endRef)

        if at.readVersion5:
            # Terminate the *previous* doc part if it exists.
            if at.docOut:
                at.appendToOut(''.join(at.docOut))
                at.docOut = []

            # 2010/10/21: Important bug fix: always enter code mode.
            at.inCode = True

            # Restore the node containing the section reference.
            # *Never* terminate new-sentinel nodes until the post-pass.
            at.raw = False # End raw mode.
            at.lastRefNode = at.v # A kludge for at.readAfterRef
            at.v = at.endSentinelNodeStack.pop()
            at.indent = at.endSentinelIndentStack.pop()
            oldLevel = len(at.thinNodeStack)
            newLevel = at.endSentinelLevelStack.pop()
            at.changeLevel(oldLevel,newLevel)
    #@+node:ekr.20041005105605.99: *6* at.readLastDocLine (old sentinels only)
    def readLastDocLine (self,tag):

        """Read the @c line that terminates the doc part.
        tag is @doc or @.

        Not used when reading new sentinels.
        """

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

        at.appendToOut(tag + s)
        at.docOut = []
    #@+node:ekr.20041005105605.100: *5* Unpaired sentinels
    # Ooops: shadow files are cleared if there is a read error!!
    #@+node:ekr.20041005105605.101: *6* at.ignoreOldSentinel
    def  ignoreOldSentinel (self,s,unused_i):

        """Ignore an 3.x sentinel."""

        g.warning("ignoring 3.x sentinel:",s.strip())
    #@+node:ekr.20041005105605.102: *6* at.readAfterRef
    def  readAfterRef (self,s,i):

        """Read an @afterref sentinel."""

        at = self
        trace = False and not g.unitTesting
        assert g.match(s,i,"afterref"),'missing afterref'

        # Append the next line to the text.
        s = at.readLine() ### at.inputFile)

        v = at.lastRefNode
        hasList = hasattr(v,'tempBodyList')
        # g.trace('hasList',hasList,'v',v and v.h)

        if at.readVersion5:
            if hasList and at.v.tempBodyList:
                # Remove the trailing newline.
                s2 = at.v.tempBodyList[-1]
                if s2.endswith('\n'): s2 = s2[:-1]
                at.v.tempBodyList[-1] = s2
                if trace: g.trace('v: %30s %s' % (at.v.h,repr(s2+s)))

        at.appendToOut(s)
    #@+node:ekr.20041005105605.103: *6* at.readClone
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
    #@+node:ekr.20041005105605.104: *6* at.readComment
    def readComment (self,s,i):

        """Read an @comment sentinel."""

        assert g.match(s,i,"comment"),'missing comment sentinel'

        # Just ignore the comment line!
    #@+node:ekr.20041005105605.105: *6* at.readDelims
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
                at.appendToOut(line+'\n')
            else:
                at.endSentinelComment = end
                line = s[i0:i]
                line = line.rstrip()
                at.appendToOut(line+'\n')
        else:
            at.readError("Bad @delims")
            at.appendToOut("@delims")
    #@+node:ekr.20041005105605.106: *6* at.readDirective (@@)
    def readDirective (self,s,i):

        """Read an @@sentinel."""

        trace = False and not g.unitTesting
        at = self
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
                #@+<< handle @language >>
                #@+node:ekr.20041005105605.107: *7* << handle @language >>
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
                    g.error("ignoring bad @language sentinel:",line)
                #@-<< handle @language >>
            elif g.match_word(s,i,"@comment"):
                #@+<< handle @comment >>
                #@+node:ekr.20041005105605.108: *7* << handle @comment >>
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
                    g.error("ignoring bad @comment sentinel:",line)
                #@-<< handle @comment >>

        # An @c or @code ends the doc part when using new sentinels.
        if (
            at.readVersion5 and s2.startswith('@c') and
            (g.match_word(s2,0,'@c') or g.match_word(s2,0,'@code'))
        ):
            if at.docOut:
                s = ''.join(at.docOut)
                s = at.massageAtDocPart(s) # 2011/05/24
                at.appendToOut(s)
                at.docOut = []
            at.inCode = True # End the doc part.

        at.appendToOut(s2)
    #@+node:ekr.20041005105605.109: *6* at.readNl
    def readNl (self,s,i):

        """Handle an @nonl sentinel."""

        at = self
        assert g.match(s,i,"nl"),'missing nl sentinel'

        if at.inCode:
            at.appendToOut('\n')
        else:
            at.docOut.append('\n')
    #@+node:ekr.20041005105605.110: *6* at.readNonl
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
    #@+node:ekr.20041005105605.112: *6* at.readVerbatim
    def readVerbatim (self,s,i):

        """Read an @verbatim sentinel."""

        at = self
        assert g.match(s,i,"verbatim"),'missing verbatim sentinel'

        # Append the next line to the text.
        s = at.readLine() ### at.inputFile) 
        i = at.skipIndent(s,0,at.indent)
        # Do **not** insert the verbatim line itself!
            # at.appendToOut("@verbatim\n")
        at.appendToOut(s[i:])
    #@+node:ekr.20041005105605.113: *5* at.badEndSentinel, popSentinelStack
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
    #@+node:ekr.20130121102851.10249: *5* at.changeLevel
    # Called from various methods.

    def changeLevel (self,oldLevel,newLevel):

        '''Update data structures when changing node level.

        The key invariant: on exit, the top of at.thinNodeStack is the new parent node.'''

        at = self
        # Crucial: we must be using new-style sentinels.
        assert at.readVersion5,'at.readVersion5'
        assert at.thinFile,'at.thinFile'
        assert not at.importing,'not at.importing'
        if newLevel > oldLevel:
            assert newLevel == oldLevel + 1,'newLevel == oldLevel + 1'
        else:
            while oldLevel > newLevel:
                oldLevel -= 1
                if allow_cloned_sibs:
                    at.thinChildIndexStack.pop()
                at.indentStack.pop()
                at.thinNodeStack.pop()
                at.vStack.pop()
            assert oldLevel == newLevel,'oldLevel: %s newLevel: %s' % (oldLevel,newLevel)
            assert len(at.thinNodeStack) == newLevel,'len(at.thinNodeStack) == newLevel'

        # The last node is the node at the top of the stack.
        # This node will be the parent of any newly created node.
        at.lastThinNode = at.thinNodeStack[-1]
    #@+node:ekr.20110523201030.18288: *5* at.massageAtDocPart (new)
    def massageAtDocPart (self,s):

        '''Compute the final @doc part when block comments are used.'''

        at = self

        if at.endSentinelComment:
            ok1 = s.startswith(at.startSentinelComment+'\n')
            ok2 = s.endswith(at.endSentinelComment+'\n')
            if ok1 and ok2:
                n1 = len(at.startSentinelComment)
                n2 = len(at.endSentinelComment)
                s = s[n1+1:-(n2+1)]
            else:
                at.error('invalid @doc part...\n%s' % repr(s))

        # g.trace(repr(s))
        return s
    #@+node:ekr.20041005105605.114: *4* at.sentinelKind4 & helper (read logic)
    def sentinelKind4(self,s):

        """Return the kind of sentinel at s."""

        trace = False and not g.unitTesting
        verbose = False
        at = self

        val = at.sentinelKind4_helper(s)

        if trace and (verbose or val != at.noSentinel):
            g.trace('%-20s %s' % (
                at.sentinelName(val),s.rstrip()))

        return val
    #@+node:ekr.20100518083515.5896: *5* sentinelKind4_helper
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
    #@+node:ekr.20041005105605.115: *4* at.skipSentinelStart4
    def skipSentinelStart4(self,s,i):

        """Skip the start of a sentinel."""

        start = self.startSentinelComment
        assert start and len(start)>0,'skipSentinelStart4 1'

        i = g.skip_ws(s,i)
        assert g.match(s,i,start),'skipSentinelStart4 2'
        i += len(start)

        # 7/8/02: Support for REM hack
        i = g.skip_ws(s,i)
        assert i < len(s) and s[i] == '@','skipSentinelStart4 3'
        return i + 1
    #@+node:ekr.20041005105605.116: *3* Reading utils...
    #@+node:ekr.20100625092449.5963: *4* at.appendToOut
    def appendToOut (self,s):

        '''Append s to at.out (old sentinels) or
           at.v.tempBodyList (new sentinels).'''

        at = self
        trace = False and at.readVersion5 and not g.unitTesting

        if at.readVersion5:
            if not at.v: at.v = at.root.v
            if hasattr(at.v,"tempBodyList"):
                at.v.tempBodyList.append(s)
            else:
                at.v.tempBodyList = [s]
        else:
            at.out.append(s)

        if trace:
            g.trace('%4s %25s %s' % (
                g.choose(at.inCode,'code','doc'),at.v.h,repr(s)))
    #@+node:ekr.20050301105854: *4* at.copyAllTempBodyStringsToVnodes
    def copyAllTempBodyStringsToVnodes (self,root,thinFile):

        trace = False and not g.unitTesting
        if trace: g.trace('*****',root.h)
        at = self ; c = at.c
        for p in root.self_and_subtree():
            hasList = hasattr(p.v,'tempBodyList')
            hasString = hasattr(p.v,'tempBodyString')
            if not hasString and not hasList:
                continue # Bug fix 2010/07/06: do nothing!
            # Terminate the node if v.tempBodyList exists.
            if hasList:
                at.terminateNode(v=p.v)
                    # Sets v.tempBodyString and clears v.tempBodyList.
                assert not hasattr(p.v,'tempBodyList'),'copyAllTempBodyStringsToVnodes 1'
                assert hasattr(p.v,'tempBodyString'),'copyAllTempBodyStringsToVnodes 2'
            s = p.v.tempBodyString
            delattr(p.v,'tempBodyString') # essential.
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
                    # This warning is given elsewhere.
                    # g.warning("changed:",p.h)
    #@+node:ekr.20041005105605.119: *4* at.createImportedNode
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
    #@+node:ekr.20041005105605.120: *4* at.parseLeoSentinel
    def parseLeoSentinel (self,s):

        trace = False and not g.unitTesting
        at = self ; c = at.c
        new_df = False ; valid = True ; n = len(s)
        start = '' ; end = '' ; isThinDerivedFile = False
        encoding_tag = "-encoding="
        version_tag = "-ver="
        tag = "@+leo"
        thin_tag = "-thin"
        #@+<< set the opening comment delim >>
        #@+node:ekr.20041005105605.121: *5* << set the opening comment delim >>
        # s contains the tag
        i = j = g.skip_ws(s,0)

        # The opening comment delim is the initial non-tag
        while i < n and not g.match(s,i,tag) and not g.is_nl(s,i):
            i += 1

        if j < i:
            start = s[j:i]
        else:
            if trace: g.trace('no opening delim')
            valid = False

        #@-<< set the opening comment delim >>
        #@+<< make sure we have @+leo >>
        #@+node:ekr.20041005105605.122: *5* << make sure we have @+leo >>
        #@+at
        # REM hack: leading whitespace is significant before the
        # @+leo. We do this so that sentinelKind need not skip
        # whitespace following self.startSentinelComment. This is
        # correct: we want to be as restrictive as possible about what
        # is recognized as a sentinel. This minimizes false matches.
        #@@c

        if 0: # Make leading whitespace significant.
            i = g.skip_ws(s,i)

        if g.match(s,i,tag):
            i += len(tag)
        else:
            if trace: g.trace('no @+leo')
            valid = False
        #@-<< make sure we have @+leo >>
        #@+<< read optional version param >>
        #@+node:ekr.20041005105605.123: *5* << read optional version param >>
        new_df = g.match(s,i,version_tag)

        if trace and not new_df:
            g.trace('not new_df',repr(s[0:100]))

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
            at.readVersion5 = at.readVersion >= '5'

            if j < i:
                pass
            else:
                if trace: g.trace('no version')
                valid = False
        #@-<< read optional version param >>
        #@+<< read optional thin param >>
        #@+node:ekr.20041005105605.124: *5* << read optional thin param >>
        if g.match(s,i,thin_tag):
            i += len(tag)
            isThinDerivedFile = True
        #@-<< read optional thin param >>
        #@+<< read optional encoding param >>
        #@+node:ekr.20041005105605.125: *5* << read optional encoding param >>
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
                if trace: g.trace('no encoding')
                valid = False
        #@-<< read optional encoding param >>
        #@+<< set the closing comment delim >>
        #@+node:ekr.20041005105605.126: *5* << set the closing comment delim >>
        # The closing comment delim is the trailing non-whitespace.
        i = j = g.skip_ws(s,i)
        while i < n and not g.is_ws(s[i]) and not g.is_nl(s,i):
            i += 1
        end = s[j:i]
        #@-<< set the closing comment delim >>
        if trace:
            g.trace('valid',valid,'isThin',isThinDerivedFile)
        return valid,new_df,start,end,isThinDerivedFile
    #@+node:ekr.20041005105605.127: *4* at.readError
    def readError(self,message):

        # This is useful now that we don't print the actual messages.
        if self.errors == 0:
            self.printError("----- read error. line: %s, file: %s" % (
                self.lineNumber,self.targetFileName,))

        # g.trace(self.root,g.callers())
        self.error(message)

        # Delete all of root's tree.
        self.root.v.children = []
        self.root.setDirty()
            # 2010/10/22: the dirty bit gets cleared later, though.
        self.root.setOrphan()

    #@+node:ekr.20041005105605.128: *4* at.readLine (unused args when new_read is True)
    # theFile & fileName not used when new_read is True.
        
    def readLine (self): ### ,theFile,fileName=None):

        """Reads one line from file using the present encoding.
        Returns at.read_lines[at.read_i++]
        """

        trace = False and not g.unitTesting
        at = self
        if at.read_i < len(at.read_lines):
            s = at.read_lines[at.read_i]
            at.read_i += 1
            if trace: g.trace(at.read_i-1,repr(s))
            return s
        else:
            return '' # Not an error.
    #@+node:ekr.20041005105605.129: *4* at.scanHeader
    def scanHeader(self,theFile,fileName,giveErrors=True):

        """Scan the @+leo sentinel.

        Sets self.encoding, and self.start/endSentinelComment.

        Returns (firstLines,new_df,isThinDerivedFile) where:
        firstLines        contains all @first lines,
        new_df            is True if we are reading a new-format derived file.
        isThinDerivedFile is True if the file is an @thin file."""

        trace = False and not g.unitTesting
        # if trace: g.trace('=====',fileName)
        at = self
        firstLines = [] # The lines before @+leo.
        tag = "@+leo"
        valid = True ; new_df = False ; isThinDerivedFile = False
        #@+<< skip any non @+leo lines >>
        #@+node:ekr.20041005105605.130: *5* << skip any non @+leo lines >>
        #@+at Queue up the lines before the @+leo.
        # 
        # These will be used to add as parameters to the @first directives, if any.
        # Empty lines are ignored (because empty @first directives are ignored).
        # NOTE: the function now returns a list of the lines before @+leo.
        # 
        # We can not call sentinelKind here because that depends on
        # the comment delimiters we set here.
        # 
        # at-first lines are written "verbatim", so nothing more needs to be done!
        #@@c

        s = at.readLine() ### theFile,fileName)
        if trace: g.trace(fileName,'first line',repr(s))
        while s and s.find(tag) == -1:
            firstLines.append(s) # Queue the line
            s = at.readLine() ### theFile,fileName)

        n = len(s)
        valid = n > 0
        #@-<< skip any non @+leo lines >>
        if valid:
            valid,new_df,start,end,isThinDerivedFile = at.parseLeoSentinel(s)
        if valid:
            at.startSentinelComment = start
            at.endSentinelComment = end
            # g.trace('start',repr(start),'end',repr(end))
        elif giveErrors:
            at.error("No @+leo sentinel in: %s" % fileName)
            g.trace(g.callers())
        # g.trace("start,end",repr(at.startSentinelComment),repr(at.endSentinelComment))
        # g.trace(fileName,firstLines)
        return firstLines,new_df,isThinDerivedFile
    #@+node:ekr.20050103163224: *4* at.scanHeaderForThin (used by import code)
    def scanHeaderForThin (self,fileName):

        '''Return true if the derived file is a thin file.
        
        This is a kludgy method used only by the import code.'''

        at = self
        s = at.readFileToUnicode(fileName)
            # inits at.readLine.
        junk,junk,isThin = at.scanHeader(None,None)
            # scanHeader uses at.readline instead of its args.
        return isThin
    #@+node:ekr.20041005105605.131: *4* at.skipIndent
    # Skip past whitespace equivalent to width spaces.

    def skipIndent(self,s,i,width):

        ws = 0 ; n = len(s)
        while i < n and ws < width:
            if   s[i] == '\t': ws += (abs(self.tab_width) - (ws % abs(self.tab_width)))
            elif s[i] == ' ':  ws += 1
            else: break
            i += 1
        return i
    #@+node:ekr.20100628072537.5814: *4* at.terminateNode & helpers
    def terminateNode (self,middle=False,v=None):

        '''Set the body text of at.v, and issue warning if it has changed.

        This is called as follows:

        old sentinels: when handling a @-node sentinel.
        new sentinels: from the post-pass when v.tempBodyList exists.'''

        at = self
        trace = False and at.readVersion5 and not g.unitTesting
        postPass = v is not None
            # A little kludge: v is given only when this is called
            # from copyAllTempBodyStringsToVnodes.
        if not v: v = at.v

        if at.readVersion5:
            # A vital assertion.
            # We must *never* terminate a node before the post pass.
            assert postPass,'terminateNode'

        # Get the temp attributes.
        # hasString  = hasattr(v,'tempBodyString')
        # tempString = hasString and v.tempBodyString or ''
        hasList    = hasattr(v,'tempBodyList')
        tempList   = hasList and ''.join(v.tempBodyList) or ''

        # Compute the new text.
        new = g.choose(at.readVersion5,tempList,''.join(at.out))
        new = g.toUnicode(new)
        if trace: g.trace('%28s %s' % (v.h,repr(new)))

        if at.importing:
            v._bodyString = new # Allowed use of _bodyString.
        elif middle: 
            pass # Middle sentinels never alter text.
        else:
            at.terminateBody(v,postPass)

        # *Always delete tempBodyList.  Do not leave this lying around!
        if hasattr(v,'tempBodyList'): delattr(v,'tempBodyList')
    #@+node:ekr.20100628124907.5816: *5* at.indicateNodeChanged
    def indicateNodeChanged (self,old,new,postPass,v):

        at = self ; c = at.c

        if at.perfectImportRoot:
            if not postPass:
                at.correctedLines += 1
                at.reportCorrection(old,new,v)
                v._bodyString = new # Allowed use of _bodyString.
                    # Just setting v.tempBodyString won't work here.
                v.setDirty()
                    # Mark the node dirty. Ancestors will be marked dirty later.
                c.setChanged(True)
        else:
            # Do nothing if only trailing whitespace is involved.
            if new.endswith('\n') and old == new[:-1]: return
            if old.endswith('\n') and new == old[:-1]: return
            # if old == new.rstrip(): return
            # if new == old.rstrip(): return

            c.nodeConflictList.append(g.bunch(
                tag='(uncached)',
                gnx=v.gnx,
                fileName = at.root.h,
                b_old=old,
                b_new=new,
                h_old=v._headString,
                h_new=v._headString,
            ))

            if not g.unitTesting:
                g.error("uncached read node changed",v.h)

            v.setDirty()
                # Just set the dirty bit. Ancestors will be marked dirty later.
            c.changed = True
                # Important: the dirty bits won't stick unless we set c.changed here.
                # Do *not* call c.setChanged(True) here: that would be too slow.
    #@+node:ekr.20100628124907.5818: *5* at.reportCorrection
    def reportCorrection (self,old,new,v):

        at = self
        found = False
        for p in at.perfectImportRoot.self_and_subtree():
            if p.v == v:
                found = True ; break

        if found:
            if 0: # For debugging.
                g.pr('\n','-' * 40)
                g.pr("old",len(old))
                for line in g.splitLines(old):
                    #line = line.replace(' ','< >').replace('\t','<TAB>')
                    g.pr(repr(str(line)))
                g.pr('\n','-' * 40)
                g.pr("new",len(new))
                for line in g.splitLines(new):
                    #line = line.replace(' ','< >').replace('\t','<TAB>')
                    g.pr(repr(str(line)))
                g.pr('\n','-' * 40)
        else:
            # This should never happen.
            g.error("correcting hidden node: v=",repr(v))
    #@+node:ekr.20100702062857.5824: *5* at.terminateBody
    def terminateBody (self,v,postPass=False):

        '''Terminate the scanning of body text for node v.'''

        trace = False and not g.unitTesting
        at = self

        hasString  = hasattr(v,'tempBodyString')
        hasList    = hasattr(v,'tempBodyList')
        tempString = hasString and v.tempBodyString or ''
        tempList   = hasList and ''.join(v.tempBodyList) or ''

        # The old temp text is *always* in tempBodyString.
        new = g.choose(at.readVersion5,tempList,''.join(at.out))
        new = g.toUnicode(new)
        old = tempString or v.getBody()
            # v.getBody returns v._bodyString.

        # Warn if the body text has changed.
        # Don't warn about the root node.
        if v != at.root.v and old != new:
            if postPass:
                warn = old # The previous text must exist.
            else:
                warn = old and new # Both must exit.
            if warn:
                at.indicateNodeChanged(old,new,postPass,v)

        # *Always* put the new text into tempBodyString.
        v.tempBodyString = new

        if trace: g.trace(
            v.gnx,
            'tempString %3s getBody %3s old %3s new %3s' % (
                len(tempString),len(v.getBody()),len(old),len(new)),
            v.h,at.root.h)
            # '\n* callers',g.callers(4))

        # *Always delete tempBodyList.  Do not leave this lying around!
        if hasList: delattr(v,'tempBodyList')
    #@+node:ekr.20041005105605.132: ** at.Writing
    #@+node:ekr.20041005105605.133: *3* Writing (top level)
    #@+node:ekr.20041005105605.154: *4* at.asisWrite
    def asisWrite(self,root,toString=False):

        at = self ; c = at.c
        c.endEditing() # Capture the current headline.
        c.init_error_dialogs()
        try:
            # Note: @asis always writes all nodes,
            # so there can be no orphan or ignored nodes.
            targetFileName = root.atAsisFileNodeName()
            at.initWriteIvars(root,targetFileName,toString=toString)
            # "look ahead" computation of eventual fileName.
            eventualFileName = c.os_path_finalize_join(
                at.default_directory,at.targetFileName)
            if at.shouldPromptForDangerousWrite(eventualFileName,root):
                # Prompt if writing a new @asis node would overwrite the existing file.
                ok = self.promptForDangerousWrite(eventualFileName,kind='@asis')
                if ok:
                    # Fix bug 889175: Remember the full fileName.
                    at.rememberReadPath(eventualFileName,root)
                else:
                    g.es("not written:",eventualFileName)
                    return
            if at.errors: return
            if not at.openFileForWriting(root,targetFileName,toString):
                # openFileForWriting calls root.setDirty() if there are errors.
                return

            for p in root.self_and_subtree():
                #@+<< Write p's headline if it starts with @@ >>
                #@+node:ekr.20041005105605.155: *5* << Write p's headline if it starts with @@ >>
                s = p.h
                if g.match(s,0,"@@"):
                    s = s[2:]
                    if s and len(s) > 0:
                        at.outputFile.write(s)
                #@-<< Write p's headline if it starts with @@ >>
                #@+<< Write p's body >>
                #@+node:ekr.20041005105605.156: *5* << Write p's body >>
                s = p.b

                if s:
                    s = g.toEncodedString(s,at.encoding,reportErrors=True) # 3/7/03
                    at.outputStringWithLineEndings(s)
                #@-<< Write p's body >>
            at.closeWriteFile()
            at.replaceTargetFileIfDifferent(root) # Sets/clears dirty and orphan bits.

        except Exception:
            at.writeException(root) # Sets dirty and orphan bits.

    silentWrite = asisWrite # Compatibility with old scripts.
    #@+node:ekr.20041005105605.142: *4* at.openFileForWriting & helper
    def openFileForWriting (self,root,fileName,toString):

        trace = False and not g.unitTesting
        at = self
        at.outputFile = None
        if toString:
            at.shortFileName = g.shortFileName(fileName)
            at.outputFileName = "<string: %s>" % at.shortFileName
            at.outputFile = g.fileLikeObject()
        else:
            ok = at.openFileForWritingHelper(fileName)
            # New in Leo 4.4.8: set dirty bit if there are errors.
            if not ok:
                at.outputFile = None
        if trace:
            g.trace('root',repr(root and root.h),'outputFile',repr(at.outputFile))
        # New in 4.3 b2: root may be none when writing from a string.
        if root:
            if at.outputFile:
                root.clearOrphan()
            else:
                root.setOrphan()
                root.setDirty()
        return at.outputFile is not None
    #@+node:ekr.20041005105605.143: *5* at.openFileForWritingHelper & helper
    def openFileForWritingHelper (self,fileName):

        '''Open the file and return True if all went well.'''

        at = self ; c = at.c
        try:
            at.shortFileName = g.shortFileName(fileName)
            at.targetFileName = c.os_path_finalize_join(
                at.default_directory,fileName)
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
            at.outputFileName = None
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
    #@+node:bwmulder.20050101094804: *6* at.openForWrite
    def openForWrite (self, filename, wb='wb'):

        '''Open a file for writes, handling shadow files.'''

        trace = False and not g.unitTesting
        at = self ; c = at.c ; x = c.shadowController
        try:
            # 2011/10/11: in "quick edit/save" mode the .leo file may not have a name.
            if c.fileName():
                shadow_filename = x.shadowPathName(filename)
                self.writing_to_shadow_directory = os.path.exists(shadow_filename)
                open_file_name = g.choose(
                    self.writing_to_shadow_directory,shadow_filename,filename)
                self.shadow_filename = g.choose(
                    self.writing_to_shadow_directory,shadow_filename,None)
            else:
                self.writing_to_shadow_directory = False
                open_file_name = filename
            if self.writing_to_shadow_directory:
                if trace: g.trace(filename,shadow_filename)
                x.message('writing %s' % shadow_filename)
                f = g.fileLikeObject()
                return 'shadow',f
            else:
                ok = c.checkFileTimeStamp(at.targetFileName)
                if ok:
                    f = g.fileLikeObject()
                else:
                    f = None
                # return 'check',ok and open(open_file_name,wb)
                return 'check',f
        except IOError:
            if not g.app.unitTesting:
                g.error('openForWrite: exception opening file: %s' % (open_file_name))
                g.es_exception()
            return 'error',None
    #@+node:ekr.20041005105605.144: *4* at.write & helper
    def write (self,root,
        kind = '@unknown', # Should not happen.
        nosentinels = False,
        perfectImportFlag = False,
        scriptWrite = False,
        thinFile = False,
        toString = False,
    ):
        """Write a 4.x derived file.
        root is the position of an @<file> node"""

        trace = False and not g.unitTesting
        at = self ; c = at.c
        c.endEditing() # Capture the current headline.
        #@+<< set at.targetFileName >>
        #@+node:ekr.20041005105605.145: *5* << set at.targetFileName >>
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
        #@-<< set at.targetFileName >>
        at.initWriteIvars(root,at.targetFileName,
            perfectImportFlag = perfectImportFlag,
            nosentinels = nosentinels,
            thinFile = thinFile,
            scriptWrite = scriptWrite,
            toString = toString,
        )
        # "look ahead" computation of eventual fileName.
        eventualFileName = c.os_path_finalize_join(
            at.default_directory,at.targetFileName)
        if trace:
            g.trace('default_dir',
                g.os_path_exists(at.default_directory),
                at.default_directory)
            g.trace('eventual_fn',eventualFileName)
        if not scriptWrite and not toString:
            if at.shouldPromptForDangerousWrite(eventualFileName,root):
                # Prompt if writing a new @file or @thin node would
                # overwrite an existing file.
                ok = self.promptForDangerousWrite(eventualFileName,kind)
                if ok:
                    at.rememberReadPath(eventualFileName,root)
                else:
                    g.es("not written:",eventualFileName)
                    #@+<< set dirty and orphan bits >>
                    #@+node:ekr.20041005105605.146: *5* << set dirty and orphan bits >>
                    # Setting the orphan and dirty flags tells Leo to write the tree.
                    # However, the dirty bits get cleared if we are called from the save command.
                    root.setOrphan()
                    root.setDirty()
                    # Delete the temp file.
                    if at.outputFileName:
                        self.remove(at.outputFileName) 

                    #@-<< set dirty and orphan bits >>
                    #@afterref
 # 2010/10/21.
                    return
        if not at.openFileForWriting(root,at.targetFileName,toString):
            # openFileForWriting calls root.setDirty() if there are errors.
            if trace: g.trace('open failed',eventualFileName)
            return
        try:
            at.writeOpenFile(root,nosentinels=nosentinels,toString=toString)
            assert root==at.root,'write'
            if toString:
                at.closeWriteFile()
                    # sets at.stringOutput and at.outputContents
                # Major bug: failure to clear this wipes out headlines!
                # Minor bug: sometimes this causes slight problems...
                if hasattr(self.root.v,'tnodeList'):
                    delattr(self.root.v,'tnodeList')
                root.v._p_changed = True
            else:
                at.closeWriteFile()
                if at.errors > 0 or root.isOrphan():
                    #@+<< set dirty and orphan bits >>
                    #@+node:ekr.20041005105605.146: *5* << set dirty and orphan bits >>
                    # Setting the orphan and dirty flags tells Leo to write the tree.
                    # However, the dirty bits get cleared if we are called from the save command.
                    root.setOrphan()
                    root.setDirty()
                    # Delete the temp file.
                    if at.outputFileName:
                        self.remove(at.outputFileName) 

                    #@-<< set dirty and orphan bits >>
                    g.es("not written:",g.shortFileName(at.targetFileName))
                else:
                    # Fix bug 889175: Remember the full fileName.
                    at.rememberReadPath(eventualFileName,root)
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
    #@+node:ekr.20041005105605.147: *4* at.writeAll & helper
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
        # This is the *only* place where these are set.
        # promptForDangerousWrite sets cancelFlag only if canCancelFlag is True.
        at.canCancelFlag = True
        at.cancelFlag = False
        at.yesToAll = False
        if writeAtFileNodesFlag:
            # The Write @<file> Nodes command.
            # Write all nodes in the selected tree.
            p = c.p
            after = p.nodeAfterTree()
        else:
            # Write dirty nodes in the entire outline.
            p =  c.rootPosition()
            after = c.nullPosition()
        at.clearAllOrphanBits(p)
        while p and p != after:
            if p.isAtIgnoreNode() and not p.isAtAsisFileNode():
                if p.isAnyAtFileNode() :
                    c.ignored_at_file_nodes.append(p.h)
                # Note: @ignore not honored in @asis nodes.
                p.moveToNodeAfterTree() # 2011/10/08: Honor @ignore!
            elif p.isAnyAtFileNode():
                self.writeAllHelper(p,force,toString,writeAtFileNodesFlag,writtenFiles)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        # Make *sure* these flags are cleared for other commands.
        at.canCancelFlag = False
        at.cancelFlag = False
        at.yesToAll = False
        #@+<< say the command is finished >>
        #@+node:ekr.20041005105605.150: *5* << say the command is finished >>
        if not g.unitTesting:
            if writeAtFileNodesFlag or writeDirtyAtFileNodesFlag:
                if len(writtenFiles) > 0:
                    g.es("finished")
                elif writeAtFileNodesFlag:
                    g.es("no @<file> nodes in the selected tree")
                else:
                    g.es("no dirty @<file> nodes")
        #@-<< say the command is finished >>
        if trace: g.trace('%s calls to c.scanAtPathDirectives()' % (
            c.scanAtPathDirectivesCount-scanAtPathDirectivesCount))
    #@+node:ekr.20041005105605.148: *5* at.clearAllOrphanBits
    def clearAllOrphanBits (self,p):

        '''Clear orphan bits for all nodes *except* orphan @file nodes.'''

        # 2011/06/15: Important bug fix: retain orphan bits for @file nodes.
        for p2 in p.self_and_subtree():
            if p2.isOrphan():
                if p2.isAnyAtFileNode():
                    # g.trace('*** retaining orphan bit',p2.h)
                    pass
                else:
                    p2.clearOrphan()
    #@+node:ekr.20041005105605.149: *5* at.writeAllHelper
    def writeAllHelper (self,p,
        force,toString,writeAtFileNodesFlag,writtenFiles
    ):

        trace = False and not g.unitTesting
        at = self ; c = at.c

        if p.isAtIgnoreNode() and not p.isAtAsisFileNode():
            pathChanged = False
        else:
            oldPath = g.os_path_normcase(at.getPathUa(p))
            newPath = g.os_path_normcase(at.fullPath(p))
            pathChanged = oldPath and oldPath != newPath
            # 2010/01/27: suppress this message during save-as and save-to commands.
            if pathChanged and not c.ignoreChangedPaths:
                # g.warning('path changed for',p.h)
                # if trace: g.trace('p %s\noldPath %s\nnewPath %s' % (
                    # p.h,repr(oldPath),repr(newPath)))
                ok = self.promptForDangerousWrite(
                    fileName=None,
                    kind=None,
                    message='%s\n%s' % (
                        g.tr('path changed for %s' % (p.h)),
                        g.tr('write this file anyway?')))
                if ok:
                    at.setPathUa(p,newPath) # Remember that we have changed paths.
                else:
                    return
        if (p.v.isDirty() or
            # p.v.isOrphan() or # 2011/06/17.
            pathChanged or
            writeAtFileNodesFlag or
            p.v in writtenFiles
        ):
            # Tricky: @ignore not recognised in @asis nodes.
            if p.isAtAsisFileNode():
                at.asisWrite(p,toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtIgnoreNode():
                pass # Handled in caller.
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
    #@+node:ekr.20070806105859: *4* at.writeAtAutoNodes & writeDirtyAtAutoNodes & helpers
    def writeAtAutoNodes (self,event=None):

        '''Write all @auto nodes in the selected outline.'''

        at = self ; c = at.c
        c.init_error_dialogs()
        at.writeAtAutoNodesHelper(writeDirtyOnly=False)
        c.raise_error_dialogs(kind='write')

    def writeDirtyAtAutoNodes (self,event=None):

        '''Write all dirty @auto nodes in the selected outline.'''

        at = self ; c = at.c
        c.init_error_dialogs()
        at.writeAtAutoNodesHelper(writeDirtyOnly=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20070806140208: *5* at.writeAtAutoNodesHelper
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

        if not g.unitTesting:
            if found:
                g.es("finished")
            elif writeDirtyOnly:
                g.es("no dirty @auto nodes in the selected tree")
            else:
                g.es("no @auto nodes in the selected tree")
    #@+node:ekr.20070806141607: *5* at.writeOneAtAutoNode
    def writeOneAtAutoNode(self,p,toString,force):

        '''Write p, an @auto node.

        File indices *must* have already been assigned.'''

        at = self ; c = at.c ; root = p.copy()
        fileName = p.atAutoNodeName()
        if not fileName and not toString:
            return False
        at.default_directory = g.setDefaultDirectory(c,p,importing=True)
        fileName = c.os_path_finalize_join(at.default_directory,fileName)
        if not toString and at.shouldPromptForDangerousWrite(fileName,root):
            # Prompt if writing a new @auto node would overwrite the existing file.
            ok = self.promptForDangerousWrite(fileName,kind='@auto')
            if not ok:
                g.es("not written:",fileName)
                return
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fileName,root)
        # This code is similar to code in at.write.
        c.endEditing() # Capture the current headline.
        at.targetFileName = g.choose(toString,"<string-file>",fileName)
        at.initWriteIvars(root,at.targetFileName,
            atAuto=True,
            nosentinels=True,thinFile=False,scriptWrite=False,
            toString=toString)
        ok = at.openFileForWriting (root,fileName=fileName,toString=toString)
        if ok:
            isAtAutoOtl = root.isAtAutoOtlNode() # For traces.
            isAtAutoRst = root.isAtAutoRstNode() # For traces.
            if isAtAutoRst:
                ok2 = c.rstCommands.writeAtAutoFile(root,fileName,at.outputFile)
                if not ok2: at.errors += 1
            elif isAtAutoOtl:
                ok2 = at.writeAtAutoOtlFile(root)
                if not ok2: at.errors += 1
            else:
                at.writeOpenFile(root,nosentinels=True,toString=toString)
            at.closeWriteFile()
                # Sets stringOutput if toString is True.
            if at.errors == 0:
                # g.trace('toString',toString,'force',force,'isAtAutoRst',isAtAutoRst)
                at.replaceTargetFileIfDifferent(root,ignoreBlankLines=isAtAutoRst)
                    # Sets/clears dirty and orphan bits.
            else:
                g.es("not written:",fileName)
                root.setDirty() # New in Leo 4.4.8.
                root.setOrphan() # 2010/10/22.
        elif not toString:
            root.setDirty() # Make _sure_ we try to rewrite this file.
            root.setOrphan() # 2010/10/22.
            g.es("not written:",fileName)
        return ok
    #@+node:ekr.20080711093251.3: *4* at.writeAtShadowNodes & writeDirtyAtShadowNodes & helpers
    def writeAtShadowNodes (self,event=None):

        '''Write all @shadow nodes in the selected outline.'''

        at = self ; c = at.c
        c.init_error_dialogs()
        val = at.writeAtShadowNodesHelper(writeDirtyOnly=False)
        c.raise_error_dialogs(kind='write')
        return val

    def writeDirtyAtShadowNodes (self,event=None):

        '''Write all dirty @shadow nodes in the selected outline.'''

        at = self ; c = at.c
        c.init_error_dialogs()
        val =  at.writeAtShadowNodesHelper(writeDirtyOnly=True)
        c.raise_error_dialogs(kind='write')
        return val
    #@+node:ekr.20080711093251.4: *5* at.writeAtShadowNodesHelper
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
                    g.blue('wrote %s' % p.atShadowFileNodeName())
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()

        if not g.unitTesting:
            if found:
                g.es("finished")
            elif writeDirtyOnly:
                g.es("no dirty @shadow nodes in the selected tree")
            else:
                g.es("no @shadow nodes in the selected tree")

        return found
    #@+node:ekr.20080711093251.5: *5* at.writeOneAtShadowNode & helpers
    def writeOneAtShadowNode(self,p,toString,force):

        '''Write p, an @shadow node.

        File indices *must* have already been assigned.'''

        trace = False and not g.unitTesting
        at = self ; c = at.c ; x = c.shadowController
        root = p.copy() 
        fn = p.atShadowFileNodeName()
        if trace: g.trace(p.h,fn)
        if not fn:
            g.error('can not happen: not an @shadow node',p.h)
            return False
        # A hack to support unknown extensions.
        self.adjustTargetLanguage(fn) # May set c.target_language.
        fn = at.fullPath(p)
        at.default_directory = g.os_path_dirname(fn)
        # Bug fix 2010/01/18: Make sure we can compute the shadow directory.
        private_fn = x.shadowPathName(fn)
        if not private_fn:
            return False
        if not toString and at.shouldPromptForDangerousWrite(fn,root):
            # Prompt if writing a new @shadow node would overwrite the existing public file.
            ok = self.promptForDangerousWrite(fn,kind='@shadow')
            if ok:
                # Fix bug 889175: Remember the full fileName.
                at.rememberReadPath(fn,root)
            else:
                g.es("not written:",fn)
                return
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
        if g.app.unitTesting:
            ivars_dict = g.getIvarsDict(at)
        # Write the public and private files to public_s and private_s strings.
        data = []
        for sentinels in (False,True):
            # 2011/09/09: specify encoding explicitly.
            theFile = at.openStringFile(fn,encoding=at.encoding)
            at.sentinels = sentinels
            at.writeOpenFile(root,
                nosentinels=not sentinels,toString=False)
                # nosentinels only affects error messages, and then only if atAuto is True.
            s = at.closeStringFile(theFile)
            data.append(s)
        # Set these new ivars for unit tests.
        at.public_s, at.private_s = data
        if g.app.unitTesting:
            exceptions = ('public_s','private_s','sentinels','stringOutput','outputContents')
            assert g.checkUnchangedIvars(at,ivars_dict,exceptions),'writeOneAtShadowNode'
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
            g.error("not written:",at.outputFileName)
            root.setDirty() # New in Leo 4.4.8.
            root.setOrphan() # 2010/10/22.
        return at.errors == 0
    #@+node:ekr.20080819075811.13: *6* adjustTargetLanguage
    def adjustTargetLanguage (self,fn):

        """Use the language implied by fn's extension if
        there is a conflict between it and c.target_language."""

        at = self
        c = at.c
        junk,ext = g.os_path_splitext(fn)

        if ext:
            if ext.startswith('.'): ext = ext[1:]

            language = g.app.extension_dict.get(ext)
            if language:
                c.target_language = language
            else:
                # An unknown language.
                pass # Use the default language, **not** 'unknown_language'
    #@+node:ekr.20050506084734: *4* at.writeFromString
    # This is at.write specialized for scripting.

    def writeFromString(self,root,s,forcePythonSentinels=True,useSentinels=True):

        """Write a 4.x derived file from a string.

        This is used by the scripting logic."""

        at = self ; c = at.c
        c.endEditing()
            # Capture the current headline, but don't change the focus!
        at.initWriteIvars(root,"<string-file>",
            nosentinels=not useSentinels,thinFile=False,scriptWrite=True,toString=True,
            forcePythonSentinels=forcePythonSentinels)
        try:
            ok = at.openFileForWriting(root,at.targetFileName,toString=True)
            if g.app.unitTesting: assert ok,'writeFromString' # string writes never fail.
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
    #@+node:ekr.20041005105605.151: *4* at.writeMissing
    def writeMissing(self,p,toString=False):

        at = self ; c = at.c
        writtenFiles = False
        c.init_error_dialogs()
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
                            #@+<< write the @file node >>
                            #@+node:ekr.20041005105605.152: *5* << write the @file node >> (writeMissing)
                            if p.isAtAsisFileNode():
                                at.asisWrite(p)
                            elif p.isAtNoSentFileNode():
                                at.write(p,kind='@nosent',nosentinels=True)
                            elif p.isAtFileNode():
                                at.write(p,kind='@file')
                            else: assert 0,'writeMissing'

                            writtenFiles = True
                            #@-<< write the @file node >>
                            at.closeWriteFile()
                p.moveToNodeAfterTree()
            elif p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        if not g.unitTesting:
            if writtenFiles > 0:
                g.es("finished")
            else:
                g.es("no @file node in the selected tree")

        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20090225080846.5: *4* at.writeOneAtEditNode
    def writeOneAtEditNode(self,p,toString,force=False):

        '''Write one @edit node.'''

        at = self ; c = at.c
        root = p.copy()
        c.endEditing()
        c.init_error_dialogs()
        fn = p.atEditNodeName()
        if not fn and not toString: return False

        if p.hasChildren():
            g.error('@edit nodes must not have children')
            g.es('To save your work, convert @edit to @auto or @thin')
            return False
        at.default_directory = g.setDefaultDirectory(c,p,importing=True)
        fn = c.os_path_finalize_join(at.default_directory,fn)
        if not force and at.shouldPromptForDangerousWrite(fn,root):
            # Prompt if writing a new @edit node would overwrite the existing file.
            ok = self.promptForDangerousWrite(fn,kind='@edit')
            if ok:
                # Fix bug 889175: Remember the full fileName.
                at.rememberReadPath(fn,root)
            else:
                g.es("not written:",fn)
                return False
        at.targetFileName = fn
        at.initWriteIvars(root,at.targetFileName,
            atAuto=True, atEdit=True,
            nosentinels=True,thinFile=False,
            scriptWrite=False,toString=toString)
        # Compute the file's contents.
        # Unlike the @nosent file logic it does not add a final newline.
        contents = ''.join([s for s in g.splitLines(p.b)
            if at.directiveKind4(s,0) == at.noDirective])
        if toString:
            at.stringOutput = contents
            return True
        ok = at.openFileForWriting(root,fileName=fn,toString=False)
        if ok:
            self.os(contents)
            at.closeWriteFile()
        if ok and at.errors == 0:
            at.replaceTargetFileIfDifferent(root) # Sets/clears dirty and orphan bits.
        else:
            g.es("not written:",at.targetFileName) # 2010/10/22
            root.setDirty()
            root.setOrphan() # 2010/10/22
        c.raise_error_dialogs(kind='write')
        return ok
    #@+node:ekr.20041005105605.157: *4* at.writeOpenFile
    # New in 4.3: must be inited before calling this method.
    # New in 4.3 b2: support for writing from a string.

    def writeOpenFile(self,root,
        nosentinels=False,toString=False,fromString=''):

        """Do all writes except asis writes."""

        at = self
        s = g.choose(fromString,fromString,root.v.b)
        root.clearAllVisitedInTree()
        at.putAtFirstLines(s)
        at.putOpenLeoSentinel("@+leo-ver=%s" % (5 if at.writeVersion5 else 4))
            # g.choose(at.writeVersion5,5,4)))
                # Use version 4 for @shadow, verion 5 otherwise.
        at.putInitialComment()
        at.putOpenNodeSentinel(root)
        at.putBody(root,fromString=fromString)
        at.putCloseNodeSentinel(root)
        # The -leo sentinel is required to handle @last.
        at.putSentinel("@-leo")
        root.setVisited()
        at.putAtLastLines(s)
        if not toString:
            at.warnAboutOrphandAndIgnoredNodes()
    #@+node:ekr.20120518080359.10006: *4* at.writeAtAutoOtlFile
    def writeAtAutoOtlFile (self,root):

        """Write all the *descendants* of an @auto-otl node."""

        at = self

        def put(s):
            '''Take care with output newlines.'''
            at.os(s[:-1] if s.endswith('\n') else s)
            at.onl()

        for child in root.children():
            n = child.level()
            for p in child.self_and_subtree():
                indent = '\t'*(p.level()-n)
                put('%s%s' % (indent,p.h))
                for s in p.b.splitlines(False):
                    put('%s: %s' % (indent,s))

        root.setVisited()
        return True
    #@+node:ekr.20041005105605.160: *3* Writing 4.x
    #@+node:ekr.20041005105605.161: *4* at.putBody
    # oneNodeOnly is no longer used, but it might be used in the future?

    def putBody(self,p,oneNodeOnly=False,fromString=''):

        '''Generate the body enclosed in sentinel lines.
        Return True if the body contains an @others line.'''

        trace = False and not g.unitTesting
        at = self
        at_comment_seen,at_delims_seen,at_warning_given=False,False,False
            # 2011/05/25: warn if a node contains both @comment and @delims.
        has_at_others = False

        # New in 4.3 b2: get s from fromString if possible.
        s = g.choose(fromString,fromString,p.b)

        p.v.setVisited()
        if trace: g.trace('visit',p.h)
            # Make sure v is never expanded again.
            # Suppress orphans check.
        if not at.thinFile:
            p.v.setWriteBit() # Mark the vnode to be written.
        if not at.thinFile and not s: return

        inCode = True
        #@+<< Make sure all lines end in a newline >>
        #@+node:ekr.20041005105605.162: *5* << Make sure all lines end in a newline >>
        #@+at If we add a trailing newline, we'll generate an @nonl sentinel below.
        # 
        # - We always ensure a newline in @file and @thin trees.
        # - This code is not used used in @asis trees.
        # - New in Leo 4.4.3 b1: We add a newline in @nosent trees unless
        #   @bool force_newlines_in_at_nosent_bodies = False
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
        #@-<< Make sure all lines end in a newline >>
        at.raw = False # 2007/07/04: Bug fix exposed by new sentinels.
        i = 0
        while i < len(s):
            next_i = g.skip_line(s,i)
            assert next_i > i,'putBody'
            kind = at.directiveKind4(s,i)
            #@+<< handle line at s[i] >>
            #@+node:ekr.20041005105605.163: *5* << handle line at s[i] >> (putBody)
            if trace: g.trace(repr(s[i:next_i]))

            if kind == at.noDirective:
                if not oneNodeOnly:
                    if inCode:
                        if at.raw or at.atAuto or at.perfectImportFlag:
                            # 2011/12/14: Ignore references in @auto.
                            # 2012/06/02: Needed for import checks.
                            at.putCodeLine(s,i)
                        else:
                            hasRef,n1,n2 = at.findSectionName(s,i)
                            if hasRef:
                                at.putRefLine(s,i,n1,n2,p)
                            else:
                                at.putCodeLine(s,i)
                    else:
                        at.putDocLine(s,i)
            elif at.raw:
                if kind == at.endRawDirective and not at.perfectImportFlag:
                    at.raw = False
                    at.putSentinel("@@end_raw")
                    i = g.skip_line(s,i)
                else:
                    # Fix bug 784920: @raw mode does not ignore directives 
                    at.putCodeLine(s,i)
            elif kind in (at.docDirective,at.atDirective):
                assert not at.pending,'putBody at.pending'
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
                    if inCode:
                        if p == self.root:
                            at.putAtAllLine(s,i,p)
                        else:
                            at.error('@all not valid in: %s' % (p.h))
                    else: at.putDocLine(s,i)
            elif kind == at.othersDirective:
                if not oneNodeOnly:
                    if inCode:
                        if has_at_others:
                            at.error('multiple @others in: %s' % (p.h))
                        else:
                            at.putAtOthersLine(s,i,p)
                            has_at_others = True
                    else:
                        at.putDocLine(s,i)
            elif kind == at.rawDirective:
                at.raw = True
                at.putSentinel("@@raw")
            elif kind == at.endRawDirective:
                # Fix bug 784920: @raw mode does not ignore directives 
                at.error('unmatched @end_raw directive: %s' % p.h)
                # at.raw = False
                # at.putSentinel("@@end_raw")
                # i = g.skip_line(s,i)
            elif kind == at.startVerbatim:
                # Fix bug 778204: @verbatim not a valid Leo directive.
                if g.unitTesting:
                    # A hack: unit tests for @shadow use @verbatim as a kind of directive.
                    pass
                elif not at.perfectImportFlag:
                    g.trace(at.atShadow)
                    at.error('@verbatim is not a Leo directive: %s' % p.h)
                if 0: # Old code.  This is wrong: @verbatim is not a directive!
                    at.putSentinel("@verbatim")
                    at.putIndent(at.indent)
                    i = next_i
                    next_i = g.skip_line(s,i)
                    at.os(s[i:next_i])
            elif kind == at.miscDirective:
                # Fix bug 583878: Leo should warn about @comment/@delims clashes.
                if g.match_word(s,i,'@comment'):
                    at_comment_seen = True
                elif g.match_word(s,i,'@delims'):
                    at_delims_seen = True
                if at_comment_seen and at_delims_seen and not at_warning_given:
                    at_warning_given = True
                    at.error('@comment and @delims in node %s' % p.h)
                at.putDirective(s,i)
            else:
                at.error('putBody: can not happen: unknown directive kind: %s' % kind)
            #@-<< handle line at s[i] >>
            i = next_i
        if not inCode:
            at.putEndDocLine()

        if not trailingNewlineFlag:
            if at.writeVersion5:
                if at.sentinels:
                    pass # Never write @nonl
                elif at.atAuto and not at.atEdit:
                    at.onl() # 2010/08/01: bug fix: ensure newline here.
            else:
                if at.sentinels:
                    at.putSentinel("@nonl")
                elif at.atAuto and not at.atEdit:
                    # Ensure all @auto nodes end in a newline!
                    at.onl()

        return has_at_others # 2013/01/19: for new @others logic.
    #@+node:ekr.20041005105605.164: *4* writing code lines...
    #@+node:ekr.20041005105605.165: *5* @all
    #@+node:ekr.20041005105605.166: *6* putAtAllLine
    def putAtAllLine (self,s,i,p):

        """Put the expansion of @all."""

        at = self
        j,delta = g.skip_leading_ws_with_indent(s,i,at.tab_width)
        at.putLeadInSentinel(s,i,j,delta)

        at.indent += delta
        lws = at.leadingWs or ''

        if at.writeVersion5 or not lws:
            at.putSentinel("@+all")
        else:
            at.putSentinel("@" + at.leadingWs + "@+all") 

        for child in p.children():
            at.putAtAllChild(child)

        at.putSentinel("@-all")
        at.indent -= delta
    #@+node:ekr.20041005105605.167: *6* putatAllBody
    def putAtAllBody(self,p):

        """ Generate the body enclosed in sentinel lines."""

        at = self ; s = p.b

        p.v.setVisited()
        # g.trace('visit',p.h)
            # Make sure v is never expanded again.
            # Suppress orphans check.

        if not at.thinFile and not s: return
        inCode = True
        #@+<< Make sure all lines end in a newline >>
        #@+node:ekr.20041005105605.168: *7* << Make sure all lines end in a newline >>
        # 11/20/03: except in nosentinel mode.
        # 1/30/04: and especially in scripting mode.
        # If we add a trailing newline, we'll generate an @nonl sentinel below.

        if s:
            trailingNewlineFlag = s and s[-1] == '\n'
            if at.sentinels and not trailingNewlineFlag:
                s = s + '\n'
        else:
            trailingNewlineFlag = True # don't need to generate an @nonl
        #@-<< Make sure all lines end in a newline >>
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
        if at.sentinels and not trailingNewlineFlag and not at.writeVersion5:
            at.putSentinel("@nonl")
    #@+node:ekr.20041005105605.169: *6* putAtAllChild
    #@+at This code puts only the first of two or more cloned siblings, preceding the
    # clone with an @clone n sentinel.
    # 
    # This is a debatable choice: the cloned tree appears only once in the external
    # file. This should be benign; the text created by @all is likely to be used only
    # for recreating the outline in Leo. The representation in the derived file
    # doesn't matter much.
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
    #@+node:ekr.20041005105605.170: *5* @others (write)
    #@+node:ekr.20041005105605.173: *6* putAtOthersLine & helpers
    def putAtOthersLine (self,s,i,p):

        """Put the expansion of @others."""

        at = self
        j,delta = g.skip_leading_ws_with_indent(s,i,at.tab_width)
        at.putLeadInSentinel(s,i,j,delta)

        at.indent += delta

        lws = at.leadingWs or ''

        if at.writeVersion5 or not lws:
            # Never write lws in new sentinels.
            at.putSentinel("@+others")
        else:
            # Use the old (bizarre) convention when writing old sentinels.
            # Note: there are *two* at signs here.
            at.putSentinel("@" + lws + "@+others")

        if allow_cloned_sibs:
            for child in p.children():
                p = child.copy()
                after = p.nodeAfterTree()
                while p and p != after:
                    if at.validInAtOthers(p):
                        at.putOpenNodeSentinel(p)
                        at_others_flag = at.putBody(p)
                        at.putCloseNodeSentinel(p)
                        if at_others_flag:
                            p.moveToNodeAfterTree()
                        else:
                            p.moveToThreadNext()
                    else:
                        p.moveToNodeAfterTree()
        else:
            for child in p.children():
                # g.trace(child.h)
                if at.validInAtOthers(child):
                    at.putAtOthersChild(child)

        # This is the same in both old and new sentinels.
        at.putSentinel("@-others")
        at.indent -= delta
    #@+node:ekr.20041005105605.172: *7* putAtOthersChild
    def putAtOthersChild(self,p):

        at = self
        parent_v = p._parentVnode()

        if not allow_cloned_sibs:
            clonedSibs,thisClonedSibIndex = at.scanForClonedSibs(parent_v,p.v)
            if clonedSibs > 1 and thisClonedSibIndex == 1:
                at.writeError("Cloned siblings are not valid in @thin trees")
                g.error(p.h)

        at.putOpenNodeSentinel(p)
        at.putBody(p)

        if not allow_cloned_sibs:
            # Insert expansions of all children.
            for child in p.children():
                # g.trace(child.h)
                if at.validInAtOthers(child):
                    at.putAtOthersChild(child)

        at.putCloseNodeSentinel(p)
    #@+node:ekr.20041005105605.171: *7* validInAtOthers (write)
    def validInAtOthers(self,p):

        """Returns True if p should be included in the expansion of the at-others directive

        in the body text of p's parent."""

        trace = False and not g.unitTesting
        at = self
        if not allow_cloned_sibs and p.v.isVisited():
            if trace: g.trace("previously visited",p.v.h)
            return False
        i = g.skip_ws(p.h,0)
        isSection,junk = at.isSectionName(p.h,i)
        if isSection:
            return False # A section definition node.
        elif at.sentinels or at.atAuto or at.toString:
            # @ignore must not stop expansion here!
            return True
        elif p.isAtIgnoreNode():
            g.error('did not write @ignore node',p.v.h)
            return False
        else:
            return True
    #@+node:ekr.20041005105605.174: *5* putCodeLine (leoAtFile)
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
        if trace: g.trace(repr(line))
        # Don't put any whitespace in otherwise blank lines.
        if len(line) > 1: # Preserve *anything* the user puts on the line!!!
            if not at.raw:
                at.putIndent(at.indent,line)
            if line[-1:]=='\n':
                # g.trace(repr(line))
                at.os(line[:-1])
                at.onl()
            else:
                at.os(line)
        elif line and line[-1] == '\n':
            at.onl()
        elif line:
            at.os(line) # Bug fix: 2013/09/16
        else:
            g.trace('Can not happen: completely empty line')

    #@+node:ekr.20041005105605.175: *5* putRefLine & allies
    #@+node:ekr.20041005105605.176: *6* putRefLine
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
    #@+node:ekr.20041005105605.177: *6* putRefAt
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
        if at.writeVersion5:
            at.putSentinel("@+" + name)
        else:
            at.putSentinel("@" + lws + name)

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

        if at.writeVersion5:
            at.putSentinel("@-" + name)

        at.indent -= delta

        return delta
    #@+node:ekr.20041005105605.178: *6* putAfterLastRef
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
            if at.writeVersion5:
                pass # Never write @nl sentinels.
            else:
                # Temporarily readjust delta to make @nl look better.
                at.indent += delta
                at.putSentinel("@nl")
                at.indent -= delta
    #@+node:ekr.20041005105605.179: *6* putAfterMiddleRef
    def putAfterMiddleRef (self,s,start,end,delta):

        """Handle whatever follows a ref that is not the last ref of a line."""

        at = self

        if start < end:
            after = s[start:end]
            at.indent += delta
            at.putSentinel("@afterref")
            at.os(after) ; at.onl_sent() # Not a real newline.
            if at.writeVersion5:
                pass # Never write @nonl sentinels.
            else:
                at.putSentinel("@nonl")
            at.indent -= delta
    #@+node:ekr.20041005105605.180: *4* writing doc lines...
    #@+node:ekr.20041005105605.181: *5* putBlankDocLine
    def putBlankDocLine (self):

        at = self

        at.putPending(split=False)

        if not at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.startSentinelComment) ; at.oblank()

        at.onl()
    #@+node:ekr.20041005105605.183: *5* putDocLine
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
        elif at.writeVersion5:
            #@+<< write the line as is >>
            #@+node:ekr.20100629190353.5831: *6* << write the line as is >>
            at.putIndent(at.indent)

            if not at.endSentinelComment:
                at.os(at.startSentinelComment) ; at.oblank()

            at.os(s)
            if not s.endswith('\n'): at.onl()
            #@-<< write the line as is >>
        else:
            #@+<< append words to pending line, splitting the line if needed >>
            #@+node:ekr.20041005105605.184: *6* << append words to pending line, splitting the line if needed >>
            #@+at All inserted newlines are preceeded by whitespace:
            # we remove trailing whitespace from lines that have not been split.
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
            #@-<< append words to pending line, splitting the line if needed >>
    #@+node:ekr.20041005105605.185: *5* putEndDocLine
    def putEndDocLine (self):

        """Write the conclusion of a doc part."""

        at = self

        at.putPending(split=False)

        # Put the closing delimiter if we are using block comments.
        if at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.endSentinelComment)
            at.onl() # Note: no trailing whitespace.

        if at.writeVersion5:
            pass # Never write @-doc or @-at sentinels.
        else:
            sentinel = g.choose(at.docKind == at.docDirective,"@-doc","@-at")
            at.putSentinel(sentinel)
    #@+node:ekr.20041005105605.186: *5* putPending (old only)
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
    #@+node:ekr.20041005105605.182: *5* putStartDocLine
    def putStartDocLine (self,s,i,kind):

        """Write the start of a doc part."""

        at = self ; at.docKind = kind

        sentinel = g.choose(kind == at.docDirective,"@+doc","@+at")
        directive = g.choose(kind == at.docDirective,"@doc","@")

        if at.writeVersion5: # Put whatever follows the directive in the sentinel
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
    #@+node:ekr.20041005105605.187: *3* Writing 4,x sentinels...
    #@+node:ekr.20041005105605.188: *4* nodeSentinelText 4.x
    def nodeSentinelText(self,p):

        """Return the text of a @+node or @-node sentinel for p."""

        at = self ; h = p.h
        #@+<< remove comment delims from h if necessary >>
        #@+node:ekr.20041005105605.189: *5* << remove comment delims from h if necessary >>
        #@+at Bug fix 1/24/03:
        # 
        # If the present @language/@comment settings do not specify a single-line comment
        # we remove all block comment delims from h. This prevents headline text from
        # interfering with the parsing of node sentinels.
        #@@c

        start = at.startSentinelComment
        end = at.endSentinelComment

        if end and len(end) > 0:
            h = h.replace(start,"")
            h = h.replace(end,"")
        #@-<< remove comment delims from h if necessary >>

        if at.thinFile:
            gnx = g.app.nodeIndices.toString(p.v.fileIndex)
            if at.writeVersion5:
                level = 1 + p.level() - self.root.level()
                stars = '*' * level
                if 1: # Put the gnx in the traditional place.
                    if level > 2:
                        return "%s: *%s* %s" % (gnx,level,h)
                    else:
                        return "%s: %s %s" % (gnx,stars,h)
                else: # Hide the gnx to the right.
                    pad = max(1,100-len(stars)-len(h)) * ' '
                    return '%s %s%s::%s' % (stars,h,pad,gnx)
            else:
                return "%s:%s" % (gnx,h)
        else:
            return h
    #@+node:ekr.20041005105605.190: *4* putLeadInSentinel 4.x
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
            self.putIndent(at.indent) # 1/29/04: fix bug reported by Dan Winkler.
            at.os(s[i:j]) ; at.onl_sent() # 10/21/03
            if at.writeVersion5:
                pass # Never write @nonl sentinels.
            else:
                at.indent += delta # Align the @nonl with the following line.
                at.putSentinel("@nonl")
                at.indent -= delta # Let the caller set at.indent permanently.
    #@+node:ekr.20041005105605.191: *4* putCloseNodeSentinel 4.x
    def putCloseNodeSentinel(self,p,middle=False):

        at = self

        if at.writeVersion5:
            at.raw = False # Bug fix: 2010/07/04
            return # Never write @-node or @-middle sentinels.

        s = self.nodeSentinelText(p)

        if middle:
            at.putSentinel("@-middle:" + s)
        else:
            at.putSentinel("@-node:" + s)
    #@+node:ekr.20041005105605.192: *4* putOpenLeoSentinel 4.x
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
    #@+node:ekr.20041005105605.193: *4* putOpenNodeSentinel
    def putOpenNodeSentinel(self,p,inAtAll=False,middle=False):

        """Write @+node sentinel for p."""

        at = self

        if not inAtAll and p.isAtFileNode() and p != at.root and not at.toString:
            at.writeError("@file not valid in: " + p.h)
            return

        # g.trace(at.thinFile,p)

        s = at.nodeSentinelText(p)

        if middle:
            at.putSentinel("@+middle:" + s)
        else:
            at.putSentinel("@+node:" + s)

        # Leo 4.7 b2: we never write tnodeLists.
    #@+node:ekr.20041005105605.194: *4* putSentinel (applies cweb hack) 4.x
    # This method outputs all sentinels.

    def putSentinel(self,s):

        "Write a sentinel whose text is s, applying the CWEB hack if needed."

        at = self

        if not at.sentinels:
            return # Handle @file-nosent

        at.putIndent(at.indent)
        at.os(at.startSentinelComment)
        #@+<< apply the cweb hack to s >>
        #@+node:ekr.20041005105605.195: *5* << apply the cweb hack to s >>
        #@+at The cweb hack:
        # 
        # If the opening comment delim ends in '@', double all '@' signs except the first,
        # which is "doubled" by the trailing '@' in the opening comment delimiter.
        #@@c

        start = at.startSentinelComment
        if start and start[-1] == '@':
            assert(s and s[0]=='@')
            s = s.replace('@','@@')[1:]
        #@-<< apply the cweb hack to s >>
        at.os(s)
        if at.endSentinelComment:
            at.os(at.endSentinelComment)
        at.onl()
    #@+node:ekr.20041005105605.196: *3* Writing 4.x utils...
    #@+node:ekr.20090514111518.5661: *4* checkPythonCode (leoAtFile) & helpers
    def checkPythonCode (self,root,s=None,targetFn=None):

        at = self

        if not targetFn:
            targetFn = at.targetFileName
        if targetFn and targetFn.endswith('.py') and at.checkPythonCodeOnWrite:
            if not s:
                s = at.outputContents
                if not s: return
            # It's too slow to check each node separately.
            ok = at.checkPythonSyntax(root,s)
            # Syntax checking catches most indentation problems.
            # if ok: at.tabNannyNode(root,s)
    #@+node:ekr.20090514111518.5663: *5* checkPythonSyntax (leoAtFile)
    def checkPythonSyntax (self,p,body,supress=False):

        at = self

        try:
            ok = True
            if not g.isPython3:
                body = g.toEncodedString(body)
            body = body.replace('\r','')
            fn = '<node: %s>' % p.h
            compile(body + '\n',fn,'exec')
        except SyntaxError:
            if not supress:
                at.syntaxError(p,body)
            ok = False
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            ok = False
        return ok
    #@+node:ekr.20090514111518.5666: *6* syntaxError (leoAtFile)
    def syntaxError(self,p,body):

        g.error("Syntax error in: %s" % (p.h))
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
    #@+node:ekr.20090514111518.5665: *5* tabNannyNode (leoAtFile)
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
                g.error("ParserError in",p.h)
                g.es('',str(msg))
        except IndentationError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.error("IndentationError in",p.h)
                g.es('',str(msg))
        except tokenize.TokenError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.error("TokenError in",p.h)
                g.es('',str(msg))
        except tabnanny.NannyNag:
            junk, nag, junk = sys.exc_info()
            if suppress:
                raise
            else:
                badline = nag.get_lineno()
                line    = nag.get_line()
                message = nag.get_msg()
                g.error("indentation error in",p.h,"line",badline)
                g.es(message)
                line2 = repr(str(line))[1:-1]
                g.es("offending line:\n",line2)
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            if suppress: raise
    #@+node:ekr.20080712150045.3: *4* closeStringFile
    def closeStringFile (self,theFile):

        at = self
        if theFile:
            theFile.flush()
            s = at.stringOutput = theFile.get()
            at.outputContents = s
            theFile.close()
            at.outputFile = None
            at.outputFileName = '' if g.isPython3 else unicode('')
            at.shortFileName = ''
            at.targetFileName = None
            return s
        else:
            return None
    #@+node:ekr.20041005105605.135: *4* closeWriteFile
    # 4.0: Don't use newline-pending logic.

    def closeWriteFile (self):

        at = self
        if at.outputFile:
            # g.trace('**closing',at.outputFileName,at.outputFile)
            at.outputFile.flush()
            at.outputContents = at.outputFile.get()
            if at.toString:
                at.stringOutput = at.outputFile.get()
            at.outputFile.close()
            at.outputFile = None
            return at.stringOutput
        else:
            return None
    #@+node:ekr.20041005105605.197: *4* compareFiles
    def compareFiles (self,path1,path2,ignoreLineEndings,ignoreBlankLines=False):

        """Compare two text files."""
        trace = False and not g.unitTesting
        at = self
        # We can't use 'U' mode because of encoding issues (Python 2.x only).
        s1 = at.outputContents
        e1 = at.encoding
        if trace: g.trace('type(s1)',type(s1))
        if s1 is None:
            g.internalError('empty compare file: %s' % path1)
            return False
        s2,e2 = g.readFileIntoString(path2,mode='rb',raw=True)
        if s2 is None:
            g.internalError('empty compare file: %s' % path2)
            return False
        # 2013/10/28: fix bug #1243855: @auto-rst doesn't save text 
        # Make sure both strings are unicode.
        # This is requred to handle binary files in Python 3.x.
        if not g.isUnicode(s1):
            s1 = g.toUnicode(s1,encoding=e1)
        if not g.isUnicode(s2):
            s2 = g.toUnicode(s2,encoding=e2)
        equal = s1 == s2
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
        if trace: g.trace('equal',equal)
        return equal
    #@+node:ekr.20041005105605.198: *4* directiveKind4 (write logic)
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
    #@+node:ekr.20041005105605.199: *4* at.findSectionName
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
    #@+node:ekr.20041005105605.200: *4* at.isSectionName
    # returns (flag, end). end is the index of the character after the section name.

    def isSectionName(self,s,i):
        
        # 2013/08/01: bug fix: allow leading periods.
        while i < len(s) and s[i] == '.':
            i += 1
        if not g.match(s,i,"<<"):
            return False, -1
        i = g.find_on_line(s,i,">>")
        if i > -1:
            return True, i + 2
        else:
            return False, -1
    #@+node:ekr.20070909103844: *4* isSignificantTree
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
    #@+node:ekr.20080712150045.2: *4* at.openStringFile
    def openStringFile (self,fn,encoding='utf-8'):

        at = self
        at.shortFileName = g.shortFileName(fn)
        at.outputFileName = "<string: %s>" % at.shortFileName
        at.outputFile = g.fileLikeObject(encoding=encoding)
        at.targetFileName = "<string-file>"
        return at.outputFile
    #@+node:ekr.20041005105605.201: *4* os and allies
    # Note:  self.outputFile may be either a fileLikeObject or a real file.
    #@+node:ekr.20041005105605.202: *5* oblank, oblanks & otabs
    def oblank(self):
        self.os(' ')

    def oblanks (self,n):
        self.os(' ' * abs(n))

    def otabs(self,n):
        self.os('\t' * abs(n))
    #@+node:ekr.20041005105605.203: *5* onl & onl_sent
    def onl(self):

        """Write a newline to the output stream."""
        
        self.os('\n') # not self.output_newline

    def onl_sent(self):

        """Write a newline to the output stream, provided we are outputting sentinels."""

        if self.sentinels:
            self.onl()
    #@+node:ekr.20041005105605.204: *5* os
    def os (self,s):

        """Write a string to the output stream.

        All output produced by leoAtFile module goes here."""

        trace = False and not g.unitTesting
        at = self
        tag = self.underindentEscapeString
        f = at.outputFile
        assert isinstance(f,g.fileLikeObject),f
        if s and f:
            try:
                if s.startswith(tag):
                    junk,s = self.parseUnderindentTag(s)
                # Bug fix: this must be done last.
                # Convert everything to unicode.
                # We expect plain text coming only from sentinels.
                if not g.isUnicode(s):
                    s = g.toUnicode(s,'ascii')
                if trace: g.trace(at.encoding,f,repr(s))
                f.write(s)
            except Exception:
                at.exception("exception writing:" + s)
    #@+node:ekr.20041005105605.205: *4* outputStringWithLineEndings
    # Write the string s as-is except that we replace '\n' with the proper line ending.

    def outputStringWithLineEndings (self,s):
        at = self

        # Calling self.onl() runs afoul of queued newlines.
        if g.isPython3:
            s = g.ue(s,at.encoding)

        s = s.replace('\n',at.output_newline)
        self.os(s)

    #@+node:ekr.20050506090446.1: *4* putAtFirstLines
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
    #@+node:ekr.20050506090955: *4* putAtLastLines
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
    #@+node:ekr.20071117152308: *4* putBuffered
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
    #@+node:ekr.20041005105605.206: *4* putDirective  (handles @delims,@comment,@language) 4.x
    #@+at It is important for PHP and other situations that \@first
    # and \@last directives get translated to verbatim lines that
    # do _not_ include what follows the @first & @last directives.
    #@@c

    def putDirective(self,s,i):

        """Output a sentinel a directive or reference s."""

        tag = "@delims"
        assert(i < len(s) and s[i] == '@')
        k = i
        j = g.skip_to_end_of_line(s,i)
        directive = s[i:j]

        if g.match_word(s,k,"@delims"):
            #@+<< handle @delims >>
            #@+node:ekr.20041005105605.207: *5* << handle @delims >>
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
            #@-<< handle @delims >>
        elif g.match_word(s,k,"@language"):
            #@+<< handle @language >>
            #@+node:ekr.20041005105605.208: *5* << handle @language >>
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
                    g.warning("ignoring bad @language directive:",line)
            #@-<< handle @language >>
        elif g.match_word(s,k,"@comment"):
            #@+<< handle @comment >>
            #@+node:ekr.20041005105605.209: *5* << handle @comment >>
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
                    g.warning("ignoring bad @comment directive:",line)
            #@-<< handle @comment >>
        elif g.match_word(s,k,"@last"):
            self.putSentinel("@@last") # 10/27/03: Convert to an verbatim line _without_ anything else.
        elif g.match_word(s,k,"@first"):
            self.putSentinel("@@first") # 10/27/03: Convert to an verbatim line _without_ anything else.
        else:
            self.putSentinel("@" + directive)

        i = g.skip_line(s,k)
        return i
    #@+node:ekr.20041005105605.210: *4* putIndent
    def putIndent(self,n,s=''):

        """Put tabs and spaces corresponding to n spaces,
        assuming that we are at the start of a line.

        Remove extra blanks if the line starts with the underindentEscapeString"""

        tag = self.underindentEscapeString
        if s.startswith(tag):
            n2,s2 = self.parseUnderindentTag(s)
            if n2 >= n: return
            elif n > 0: n -= n2
            else:       n += n2
        if n > 0:
            w = self.tab_width
            if w > 1:
                q,r = divmod(n,w) 
                self.otabs(q) 
                self.oblanks(r)
            else:
                self.oblanks(n)
    #@+node:ekr.20041005105605.211: *4* putInitialComment
    def putInitialComment (self):

        c = self.c
        s2 = c.config.output_initial_comment
        if s2:
            lines = s2.split("\\n")
            for line in lines:
                line = line.replace("@date",time.asctime())
                if len(line)> 0:
                    self.putSentinel("@comment " + line)
    #@+node:ekr.20080712150045.1: *4* replaceFileWithString (atFile)
    def replaceFileWithString (self,fn,s):

        '''Replace the file with s if s is different from theFile's contents.

        Return True if theFile was changed.
        
        This is used only by the @shadow logic.
        '''

        trace = False and not g.unitTesting
        at = self
        exists = g.os_path_exists(fn)
        if exists: # Read the file.  Return if it is the same.
            s2,e = g.readFileIntoString(fn)
            if s is None:
                return False
            if s == s2:
                if not g.unitTesting: g.es('unchanged:',fn)
                return False
        # Issue warning if directory does not exist.
        theDir = g.os_path_dirname(fn)
        if theDir and not g.os_path_exists(theDir):
            if not g.unitTesting:
                g.error('not written: %s directory not found' % fn)
            return False
        # Replace
        try:
            f = open(fn,'wb')
            # 2013/10/28: Fix bug 1243847: unicode error when saving @shadow nodes.
            # Call g.toEncodedString regardless of Python version.
            s = g.toEncodedString(s,encoding=self.encoding)
            f.write(s)
            f.close()
            if g.unitTesting:
                if trace: g.trace('*****',fn)
            else:
                if exists:
                    g.es('wrote:    ',fn)
                else:
                    g.es('created:',fn)
            return True
        except IOError:
            at.error('unexpected exception writing file: %s' % (fn))
            g.es_exception()
            return False
    #@+node:ekr.20041005105605.212: *4* replaceTargetFileIfDifferent (atFile)
    def replaceTargetFileIfDifferent (self,root,ignoreBlankLines=False):

        '''Create target file as follows:
        1. If target file does not exist, rename output file to target file.
        2. If target file is identical to output file, remove the output file.
        3. If target file is different from output file,
           remove target file, then rename output file to be target file.

        Return True if the original file was changed.
        '''

        trace = False and not g.unitTesting
        at = self ; c = at.c
        if at.toString:
            # Do *not* change the actual file or set any dirty flag.
            at.fileChangedFlag = False
            return False
        if root:
            # The default: may be changed later.
            root.clearOrphan()
            root.clearDirty()
        # Fix bug 1132821: Leo replaces a soft link with a real file.
        if at.outputFileName:
            at.outputFileName = g.os_path_realpath(at.outputFileName)
        if at.targetFileName:
            at.targetFileName = g.os_path_realpath(at.targetFileName)
        if trace: g.trace(
            'ignoreBlankLines',ignoreBlankLines,
            'target exists',g.os_path_exists(at.targetFileName),
            at.outputFileName,at.targetFileName)
        if g.os_path_exists(at.targetFileName):
            if at.compareFiles(
                at.outputFileName,
                at.targetFileName,
                ignoreLineEndings=not at.explicitLineEnding,
                ignoreBlankLines=ignoreBlankLines
            ):
                # Files are identical.
                if trace: g.trace('files are identical')
                if not g.unitTesting:
                    g.es('unchanged:',at.shortFileName)
                at.fileChangedFlag = False
                return False
            else:
                # A mismatch.
                at.checkPythonCode(root)
                #@+<< report if the files differ only in line endings >>
                #@+node:ekr.20041019090322: *5* << report if the files differ only in line endings >>
                if (
                    at.explicitLineEnding and
                    at.compareFiles(
                        at.outputFileName,
                        at.targetFileName,
                        ignoreLineEndings=True)
                ):
                    g.warning("correcting line endings in:",at.targetFileName)
                #@-<< report if the files differ only in line endings >>
                mode = at.stat(at.targetFileName)
                s = at.outputContents
                ok = at.create(at.targetFileName,s)
                if ok:
                    c.setFileTimeStamp(at.targetFileName)
                    if not g.unitTesting:
                        g.es('wrote:',at.shortFileName)
                else:
                    g.error('error writing',at.shortFileName)
                    g.es('not written:',at.shortFileName)
                    if root:
                        root.setDirty() # New in 4.4.8.
                        root.setOrphan() # 2010/10/22.
                at.fileChangedFlag = ok
                return ok
        else:
            s = at.outputContents
            ok = self.create(at.targetFileName,s)
            if ok:
                c.setFileTimeStamp(at.targetFileName)
                if not g.unitTesting:
                    g.es('created:',at.targetFileName)
                if root:
                    # Fix bug 889175: Remember the full fileName.
                    at.rememberReadPath(at.targetFileName,root)
            else:
                # at.rename gives the error.
                if root:
                    root.setDirty() # New in 4.4.8.
                    root.setOrphan() # 2010/10/22.
            # No original file to change. Return value tested by a unit test.
            at.fileChangedFlag = False 
            return False
    #@+node:ekr.20041005105605.216: *4* at.warnAboutOrpanAndIgnoredNodes
    # Called from writeOpenFile.

    def warnAboutOrphandAndIgnoredNodes (self):

        # Always warn, even when language=="cweb"
        at = self ; root = at.root

        if at.errors: return # No need to repeat this.

        for p in root.self_and_subtree():
            if not p.v.isVisited():
                at.writeError("Orphan node:  " + p.h)
                if p.hasParent():
                    g.blue("parent node:",p.parent().h)
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
    #@+node:ekr.20041005105605.217: *4* writeError
    def writeError(self,message=None):

        at = self

        # Don't give errors for this particular file during unit testing.
        h = 'nonexistent-directory/orphan-bit-test.txt'

        if g.unitTesting and at.targetFileName.replace('\\','/').endswith(h):
            at.errors += 1
        else:
            if at.errors == 0:
                g.es_error("errors writing: " + at.targetFileName)
                # g.trace(g.callers(5))
            at.error(message)

        at.root.setDirty()
        at.root.setOrphan()
    #@+node:ekr.20041005105605.218: *4* writeException
    def writeException (self,root=None):

        at = self
        g.error("exception writing:",at.targetFileName)
        g.es_exception()
        if at.outputFile:
            at.outputFile.flush()
            at.outputFile.close()
            at.outputFile = None
        if at.outputFileName:
            at.remove(at.outputFileName)
        if root:
            # Make sure we try to rewrite this file.
            root.setOrphan()
            root.setDirty()
    #@+node:ekr.20041005105605.219: ** at.Utilites
    #@+node:ekr.20041005105605.220: *3* at.error & printError
    def error(self,*args):

        at = self
        if True: # args:
            at.printError(*args)
        at.errors += 1

    def printError (self,*args):

        '''Print an error message that may contain non-ascii characters.'''

        at = self
        # keys = {'color': g.choose(at.errors,'blue','red')}
        # g.es_print_error(*args,**keys)
        if at.errors:
            g.error(*args)
        else:
            g.warning(*args)
    #@+node:ekr.20041005105605.221: *3* at.exception
    def exception (self,message):

        self.error(message)
        g.es_exception()
    #@+node:ekr.20050104131929: *3* at.file operations...
    #@+at The difference, if any, between these methods and the corresponding g.utils_x
    # functions is that these methods may call self.error.
    #@+node:ekr.20050104131820: *4* chmod
    def chmod (self,fileName,mode):

        # Do _not_ call self.error here.
        return g.utils_chmod(fileName,mode)
    #@+node:ekr.20130910100653.11323: *4* create (Leo 4.11)
    def create(self,fn,s):
        
        '''Create a file whose contents are s.'''
        
        at = self
        # This is part of the new_write logic.
        # This is the only call to g.toEncodedString in the new_write logic.
        # 2013/10/28: fix bug 1243847: unicode error when saving @shadow nodes
        if g.isUnicode(s):
            s = g.toEncodedString(s,encoding=at.encoding)
        try:
            f = open(fn,'wb') # Must be 'wb' to preserve line endings.
            if at.output_newline != '\n':
                s = s.replace('\r','').replace('\n',at.output_newline)
            f.write(s)
            f.close()
        except Exception:
            f = None
            g.es_exception()
            g.error('error writing',fn)
            g.es('not written:',fn)
        return bool(f)
    #@+node:ekr.20050104131929.1: *4* atFile.rename
    #@+<< about os.rename >>
    #@+node:ekr.20050104131929.2: *5* << about os.rename >>
    #@+at Here is the Python 2.4 documentation for rename (same as Python 2.3)
    # 
    # Rename the file or directory src to dst.  If dst is a directory, OSError will be raised.
    # 
    # On Unix, if dst exists and is a file, it will be removed silently if the user
    # has permission. The operation may fail on some Unix flavors if src and dst are
    # on different filesystems. If successful, the renaming will be an atomic
    # operation (this is a POSIX requirement).
    # 
    # On Windows, if dst already exists, OSError will be raised even if it is a file;
    # there may be no way to implement an atomic rename when dst names an existing
    # file.
    #@-<< about os.rename >>

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
    #@+node:ekr.20050104132018: *4* atFile.remove
    def remove (self,fileName,verbose=True):

        if not fileName:
            g.trace('No file name',g.callers())
            return False
        try:
            os.remove(fileName)
            return True
        except Exception:
            if verbose:
                self.error("exception removing: %s" % fileName)
                g.es_exception()
                g.trace(g.callers(5))
            return False
    #@+node:ekr.20050104132026: *4* stat
    def stat (self,fileName):

        '''Return the access mode of named file, removing any setuid, setgid, and sticky bits.'''

        # Do _not_ call self.error here.
        return g.utils_stat(fileName)
    #@+node:ekr.20090530055015.6050: *3* at.fullPath
    def fullPath (self,p,simulate=False):

        '''Return the full path (including fileName) in effect at p.

        Neither the path nor the fileName will be created if it does not exist.
        '''

        at = self ; c = at.c
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        if simulate: # for unit tests.
            fn = p.h
        else:
            fn = p.anyAtFileNodeName()
        if fn:
            path = g.os_path_finalize_join(path,fn)
        else:
            g.trace('can not happen: not an @<file> node',g.callers())
            for p2 in p.self_and_parents():
                g.trace('  %s' % p2.h)
            path = ''
        # g.trace(p.h,repr(path))
        return path
    #@+node:ekr.20090530055015.6023: *3* at.get/setPathUa
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
    #@+node:ekr.20081216090156.4: *3* at.parseUnderindentTag
    # Important: this is part of the *write* logic.
    # It is called from at.os and at.putIndent.

    def parseUnderindentTag (self,s):

        tag = self.underindentEscapeString
        s2 = s[len(tag):]

        # To be valid, the escape must be followed by at least one digit.
        i = 0
        while i < len(s2) and s2[i].isdigit():
            i += 1

        if i > 0:
            n = int(s2[:i])
            # Bug fix: 2012/06/05: remove any period following the count.
            # This is a new convention.
            if i < len(s2) and s2[i] == '.':
                i += 1
            return n,s2[i:]
        else:
            return 0,s
    #@+node:ekr.20090712050729.6017: *3* at.promptForDangerousWrite
    def promptForDangerousWrite(self,fileName,kind,message=None):

        at = self ; c = at.c
        if g.app.unitTesting:
            val = g.app.unitTestDict.get('promptForDangerousWrite')
            return val in (None,True)
        if at.cancelFlag:
            assert at.canCancelFlag
            return False
        if at.yesToAll:
            assert at.canCancelFlag
            return True
        if message is None:
            message = '%s %s\n%s\n%s' % (
                kind, fileName,
                g.tr('already exists.'),
                g.tr('Overwrite this file?'))
        result = g.app.gui.runAskYesNoCancelDialog(c,
                title = 'Overwrite existing file?',
                yesToAllMessage="Yes To &All",
                message = message)
        if at.canCancelFlag:
            # We are in the writeAll logic so these flags can be set.
            if result == 'cancel':
                at.cancelFlag = True
            elif result == 'yes-to-all':
                at.yesToAll = True
        return result in ('yes','yes-to-all')
    #@+node:ekr.20120112084820.10001: *3* at.rememberReadPath
    def rememberReadPath(self,fn,p):

        v = p.v

        if not hasattr(v,'at_read'):
            v.at_read = []

        if not fn in v.at_read:
            v.at_read.append(fn)
    #@+node:ekr.20080923070954.4: *3* at.scanAllDirectives
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
        #@+<< set ivars >>
        #@+node:ekr.20080923070954.14: *4* << Set ivars >>
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
        #@-<< set ivars >>
        lang_dict = {'language':at.language,'delims':delims,}
        table = (
            ('encoding',    at.encoding,    g.scanAtEncodingDirectives),
            # ('lang-dict',   lang_dict,      g.scanAtCommentAndAtLanguageDirectives),
            ('lang-dict',   None,           g.scanAtCommentAndAtLanguageDirectives),
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
            g.error('warning: ignoring @path directive in',g.app.atPathInBodyWarning)

        # Post process.
        lineending  = d.get('lineending')
        lang_dict = d.get('lang-dict')
        if lang_dict:
            delims      = lang_dict.get('delims')
            at.language = lang_dict.get('language')
        else:
            # 2011/10/10:
            # No language directive.  Look for @<file> nodes.
            language = g.getLanguageFromAncestorAtFileNode(p) or 'python'
            delims   = g.set_delims_from_language(language)

        at.encoding             = d.get('encoding')
        at.explicitLineEnding   = bool(lineending)
        at.output_newline       = lineending or g.getOutputNewline(c=c)
        at.page_width           = d.get('pagewidth')
        at.default_directory    = d.get('path')
        at.tab_width            = d.get('tabwidth')

        if not importing and not reading:
            # Don't override comment delims when reading!
            #@+<< set comment strings from delims >>
            #@+node:ekr.20080923070954.13: *4* << Set comment strings from delims >>
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
            #@-<< set comment strings from delims >>

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
    #@+node:ekr.20041005105605.242: *3* at.scanForClonedSibs (reading & writing)
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
    #@+node:ekr.20041005105605.243: *3* at.sentinelName
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
    #@+node:ekr.20120110174009.9965: *3* at.shouldPromptForDangerousWrite
    def shouldPromptForDangerousWrite(self,fn,p):

        '''Return True if a prompt should be issued
        when writing p (an @<file> node) to fn.
        '''

        if not g.os_path_exists(fn):
            return False
                # No danger of overwriting fn.
        elif hasattr(p.v,'at_read'):
            return fn not in p.v.at_read
                # The path is new.
        else:
            return True
                # The file was never read.
    #@+node:ekr.20041005105605.20: *3* at.warnOnReadOnlyFile
    def warnOnReadOnlyFile (self,fn):

        # os.access() may not exist on all platforms.
        try:
            read_only = not os.access(fn,os.W_OK)
        except AttributeError:
            read_only = False 

        if read_only:
            g.error("read only:",fn)
    #@-others
#@-leo

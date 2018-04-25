# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150323150718.1: * @file leoAtFile.py
#@@first
    # Needed because of unicode characters in tests.
"""Classes to read and write @file nodes."""
#@+<< imports >>
#@+node:ekr.20041005105605.2: ** << imports >> (leoAtFile)
import leo.core.leoGlobals as g
import leo.core.leoBeautify as leoBeautify
import leo.core.leoNodes as leoNodes
# import glob
# import importlib
import os
import re
import sys
import time
import hashlib
import sqlite3
#@-<< imports >>
#@+others
#@+node:ekr.20160514120655.1: ** class AtFile
class AtFile(object):
    """A class implementing the atFile subcommander."""
    #@+<< define class constants >>
    #@+node:ekr.20131224053735.16380: *3* << define class constants >>
    #@@nobeautify

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
    #@+node:ekr.20041005105605.6: *3* << define sentinelDict >>
    #@@nobeautify

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
    #@+node:ekr.20041005105605.7: *3* at.Birth & init
    #@+node:ekr.20041005105605.8: *4* at.ctor & helpers
    # Note: g.getScript also call the at.__init__ and at.finishCreate().

    def __init__(self, c):
        '''ctor for atFile class.'''
        # **Warning**: all these ivars must **also** be inited in initCommonIvars.
        self.c = c
        self.encoding = 'utf-8' # 2014/08/13
        self.fileCommands = c.fileCommands
        self.errors = 0 # Make sure at.error() works even when not inited.
        # **Only** at.writeAll manages these flags.
        # promptForDangerousWrite sets cancelFlag and yesToAll only if canCancelFlag is True.
        self.canCancelFlag = False
        self.cancelFlag = False
        self.yesToAll = False
        # User options: set in reloadSettings.
        self.checkPythonCodeOnWrite = False
        self.runPyFlakesOnWrite = False
        self.underindentEscapeString = '\\-'
        self.reloadSettings()
        # Define the dispatch dictionary used by scanText4.
        self.dispatch_dict = self.defineDispatchDict()
    #@+node:ekr.20041005105605.9: *5* at.defineDispatchDict
    #@@nobeautify

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
    #@+node:ekr.20171113152939.1: *5* at.reloadSettings
    def reloadSettings(self):
        '''AtFile.reloadSettings'''
        c = self.c
        self.checkPythonCodeOnWrite = c.config.getBool(
            'check-python-code-on-write', default=True)
        self.runPyFlakesOnWrite = c.config.getBool(
            'run-pyflakes-on-write', default=False)
        self.underindentEscapeString = c.config.getString(
            'underindent-escape-string') or '\\-'
    #@+node:ekr.20150509194251.1: *4* at.cmd (decorator)
    def cmd(name):
        '''Command decorator for the AtFileCommands class.'''
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'atFileCommands',])
    #@+node:ekr.20041005105605.10: *4* at.initCommonIvars
    def initCommonIvars(self):
        """
        Init ivars common to both reading and writing.

        The defaults set here may be changed later.
        """
        at = self
        c = at.c
        at.at_auto_encoding = c.config.default_at_auto_file_encoding
        at.default_directory = None
        at.encoding = c.config.default_derived_file_encoding
        at.endSentinelComment = ""
        at.errors = 0
        at.inCode = True
        at.indent = 0 # The unit of indentation is spaces, not tabs.
        at.language = None
        at.output_newline = g.getOutputNewline(c=c)
        at.page_width = None
        at.pending = []
        at.raw = False # True: in @raw mode
        at.root = None # The root (a position) of tree being read or written.
        at.startSentinelComment = ""
        at.startSentinelComment = ""
        at.tab_width = c.tab_width or -4
        at.toString = False # True: sring-oriented read or write.
        at.writing_to_shadow_directory = False
    #@+node:ekr.20041005105605.13: *4* at.initReadIvars
    def initReadIvars(self, root, fileName,
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
        at.thinChildIndexStack = [] # number of siblings at this level.
        at.thinFile = False
            # True if the external file uses new-style sentinels.
        at.thinNodeStack = [] # Entries are vnodes.
        at.updateWarningGiven = False
    #@+node:ekr.20041005105605.15: *4* at.initWriteIvars
    def initWriteIvars(self, root, targetFileName,
        atEdit=False,
        atShadow=False,
        forcePythonSentinels=False, # Was None
        nosentinels=False,
        toString=False,
    ):
        at, c = self, self.c
        assert root
        self.initCommonIvars()
        assert at.checkPythonCodeOnWrite is not None
        assert at.underindentEscapeString is not None
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
        at.sameFiles = 0
        at.sentinels = not nosentinels
        at.shortFileName = "" # For messages.
        at.root = root
        # at.tab_width:         set by scanAllDirectives() below.
        at.targetFileName = targetFileName
            # Must be None for @shadow.
        at.thinFile = True
        at.toString = toString
        at.scanAllDirectives(root, forcePythonSentinels=forcePythonSentinels)
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
            at.outputFile = g.FileLikeObject()
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
            if hasattr(at.root.v, 'tnodeList'):
                delattr(at.root.v, 'tnodeList')
            at.root.v._p_changed = True
    #@+node:ekr.20130911110233.11286: *4* at.initReadLine
    def initReadLine(self, s):
        '''Init the ivars so that at.readLine will read all of s.'''
        at = self
        at.read_i = 0
        at.read_lines = g.splitLines(s)
        at._file_bytes = g.toEncodedString(s)
    #@+node:ekr.20041005105605.17: *3* at.Reading

    #@+node:ekr.20041005105605.18: *4* at.Reading (top level)
    #@+at All reading happens in the readOpenFile logic, so plugins
    # should need to override only this method.
    #@+node:ekr.20070919133659: *5* at.checkDerivedFile
    @cmd('check-derived-file')
    def checkDerivedFile(self, event=None):
        '''Make sure an external file written by Leo may be read properly.'''
        at = self; c = at.c; p = c.p
        if not p.isAtFileNode() and not p.isAtThinFileNode():
            return g.red('Please select an @thin or @file node')
        fn = p.anyAtFileNodeName()
        path = g.os_path_dirname(c.mFileName)
        fn = g.os_path_finalize_join(g.app.loadDir, path, fn)
        if not g.os_path_exists(fn):
            return g.error('file not found: %s' % (fn))
        s, e = g.readFileIntoString(fn)
        if s is None: return
        # Create a dummy, unconnected, VNode as the root.
        root_v = leoNodes.VNode(context=c)
        root = leoNodes.Position(root_v)
        # 2010/01/22: readOpenFiles now determines whether a file is thin or not.
        at.initReadIvars(root, fn)
        if at.errors: return
        at.openFileForReading(fromString=s)
        if not at.inputFile: return
        at.readOpenFile(root, fn)
        at.inputFile.close()
        if at.errors == 0:
            g.blue('check-derived-file passed')
    #@+node:ekr.20041005105605.19: *5* at.openFileForReading & helper
    def openFileForReading(self, fromString=False):
        '''
        Open the file given by at.root.
        This will be the private file for @shadow nodes.
        '''
        at, c = self, self.c
        if fromString:
            if at.atShadow:
                return at.error(
                    'can not call at.read from string for @shadow files')
            at.inputFile = g.FileLikeObject(fromString=fromString)
            at.initReadLine(fromString) # 2014/10/07
            fn = None
        else:
            fn = g.fullPath(c, at.root)
                # Returns full path, including file name.
            at.setPathUa(at.root, fn)
                # Remember the full path to this node.
            if at.atShadow:
                fn = at.openAtShadowFileForReading(fn)
                if not fn: return None
            try:
                # Open the file in binary mode to allow 0x1a in bodies & headlines.
                at.inputFile = open(fn, 'rb')
                at.readFileToUnicode(fn)
                    # Sets at.encoding...
                    #   From the BOM, if present.
                    #   Otherwise from the header, if it has -encoding=
                    #   Otherwise, uses existing value of at.encoding.
                    # Then does:
                    #    s = s.replace('\r\n','\n')
                    #    at.initReadLine(s)
                at.warnOnReadOnlyFile(fn)
            except IOError:
                at.error("can not open: '@file %s'" % (fn))
                at.inputFile = None
                at._file_bytes = g.toEncodedString('')
                fn = None
        return fn
    #@+node:ekr.20150204165040.4: *6* at.openAtShadowFileForReading
    def openAtShadowFileForReading(self, fn):
        '''Open an @shadow for reading and return shadow_fn.'''
        trace = False and not g.app.unitTesting
        at = self
        x = at.c.shadowController
        # readOneAtShadowNode should already have checked these.
        shadow_fn = x.shadowPathName(fn)
        shadow_exists = (g.os_path_exists(shadow_fn) and
            g.os_path_isfile(shadow_fn))
        if not shadow_exists:
            g.trace('can not happen: no private file',
                shadow_fn, g.callers())
            at.error('can not happen: private file does not exist: %s' % (
                shadow_fn))
            return None
        # This method is the gateway to the shadow algorithm.
        if trace:
            g.trace('         fn:       ', fn)
            g.trace('reading: shadow_fn:', shadow_fn)
        x.updatePublicAndPrivateFiles(at.root, fn, shadow_fn)
        return shadow_fn
    #@+node:ekr.20041005105605.21: *5* at.read & helpers
    def read(self, root, importFileName=None,
        fromString=None, atShadow=False, force=False
    ):
        """Read an @thin or @file tree."""
        trace = False and not g.unitTesting
        at, c = self, self.c
        fileName = at.initFileName(fromString, importFileName, root)
        sfn = g.shortFileName(fileName)
        if not fileName:
            at.error("Missing file name.  Restoring @file tree from .leo file.")
            return False
        at.rememberReadPath(g.fullPath(c, root), root)
            # Fix bug 760531: always mark the root as read, even if there was an error.
            # Fix bug 889175: Remember the full fileName.
        root.clearOrphan()
            # 2015/04/17: Clear the bit and continue so that the
            # outline can be updated from the external file.
        at.initReadIvars(root, fileName,
            importFileName=importFileName, atShadow=atShadow)

        at.fromString = fromString
        if at.errors:
            if trace: g.trace('Init error')
            return False

        fileName = at.openFileForReading(fromString=fromString)
            # For @shadow files, calls x.updatePublicAndPrivateFiles.
            # Calls at.initReadLine(s), where s is the file contents.
            # This will be used only if not cached.

        if fileName and at.inputFile:
            c.setFileTimeStamp(fileName)
        elif fromString: # 2010/09/02.
            pass
        else:
            if trace: g.trace('No inputFile')
            return False
        if g.SQLITE and c.sqlite_connection:
            loaded = at.checkExternalFileAgainstDb(root)
            if loaded: return True
            s, loaded, fileKey, force = at._file_bytes, False, None, True
        elif fromString or not g.enableDB:
            s, loaded, fileKey = fromString, False, None
        else:
            s, loaded, fileKey = c.cacher.readFile(fileName, root)
        # Never read an external file with file-like sentinels from the cache.
        isFileLike = loaded and at.isFileLike(s)
        if not loaded or isFileLike:
            # if trace: g.trace('file-like file',fileName)
            force = True # Disable caching.
        if loaded and not force:
            if trace:
                g.trace('cache hit', fileKey, sfn)
            at.inputFile.close()
            root.clearDirty()
            return True
        if not g.unitTesting:
            if trace:
                if g.enableDB:
                    g.trace('cache miss', sfn)
                else:
                    g.trace('caching disabled', sfn)
            g.es_print("reading:", g.os_path_normslashes(root.h))
        if isFileLike:
            if g.unitTesting:
                if 0: print("converting @file format in", root.h)
                g.app.unitTestDict['read-convert'] = True
            else:
                g.red("converting @file format in", root.h)
        root.clearVisitedInTree()
        at.scanAllDirectives(root, importing=at.importing, reading=True)
            # Sets the following ivars:
                # at.default_directory
                # at.encoding: **changed later** by readOpenFile/at.scanHeader.
                # at.explicitLineEnding
                # at.language
                # at.output_newline
                # at.page_width
                # at.tab_width
        thinFile = at.readOpenFile(root, fileName, deleteNodes=True)
            # Calls at.scanHeader, which sets at.encoding.
        at.inputFile.close()
        root.clearDirty() # May be set dirty below.
        if at.errors == 0:
            at.deleteUnvisitedNodes(root)
            at.deleteTnodeList(root)
        if at.errors == 0 and not at.importing:
            # Used by mod_labels plugin.
            at.readPostPass(root, thinFile)
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
        # There will be an internal error if fileKey is None.
        # This is not the cause of the bug.
        write_to_cache = (not (g.SQLITE and c.sqlite_connection)
            and at.errors == 0 and not isFileLike and not fromString)
        if write_to_cache:
            c.cacher.writeFile(root, fileKey)
        if trace: g.trace('at.errors', at.errors)
        return at.errors == 0
    #@+node:ekr.20041005105605.25: *6* at.deleteAllTempBodyStrings
    def deleteAllTempBodyStrings(self):
        '''Delete all temp attributes.'''
        at = self
        at.clearAllBodyInited()
    #@+node:ekr.20100122130101.6174: *6* at.deleteTnodeList
    def deleteTnodeList(self, p): # AtFile method.
        '''Remove p's tnodeList.'''
        v = p.v
        if hasattr(v, "tnodeList"):
            if False: # Not an error, but a useful trace.
                g.blue("deleting tnodeList for " + repr(v))
            delattr(v, "tnodeList")
            v._p_changed = True
    #@+node:ekr.20071105164407: *6* at.deleteUnvisitedNodes & helpers
    def deleteUnvisitedNodes(self, root, redraw=True):
        '''
        Delete unvisited nodes in root's subtree, not including root.

        Before Leo 5.6: Move unvisited node to be children of the 'Resurrected
        Nodes'.
        '''
        at = self
        # Find the unvisited nodes.
        aList = [z for z in root.subtree() if not z.isVisited()]
        if aList:
            # new-read: Never create resurrected nodes.
                # r = at.createResurrectedNodesNode()
                # assert r not in aList
                # callback = at.defineResurrectedNodeCallback(r, root)
                # # Move the nodes using the callback.
                # at.c.deletePositionsInList(aList, callback)
            at.c.deletePositionsInList(aList, redraw=redraw)
    #@+node:ekr.20100803073751.5817: *7* createResurrectedNodesNode
    def createResurrectedNodesNode(self):
        '''Create a 'Resurrected Nodes' node as the last top-level node.'''
        at = self; c = at.c; tag = 'Resurrected Nodes'
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
    #@+node:ekr.20100803073751.5818: *7* defineResurrectedNodeCallback
    def defineResurrectedNodeCallback(self, r, root):
        '''Define a callback that moves node p as r's last child.'''
        trace = False and not g.unitTesting

        def callback(p, r=r.copy(), root=root):
            '''The resurrected nodes callback.'''
            child = r.insertAsLastChild()
            child.h = 'From %s' % root.h
            v = p.v
            if 1: # new code: based on vnodes.
                import leo.core.leoNodes as leoNodes
                for parent_v in v.parents:
                    assert isinstance(parent_v, leoNodes.VNode), parent_v
                    if v in parent_v.children:
                        childIndex = parent_v.children.index(v)
                        if trace: g.trace('*moving*', parent_v, childIndex, v)
                        v._cutLink(childIndex, parent_v)
                        v._addLink(len(child.v.children), child.v)
                    else:
                        # This would be surprising.
                        g.trace('**already deleted**', parent_v, v)
            else: # old code, based on positions.
                p.moveToLastChildOf(child)
            if not g.unitTesting:
                g.error('resurrected node:', v.h)
                g.blue('in file:', root.h)

        return callback
    #@+node:ekr.20041005105605.22: *6* at.initFileName
    def initFileName(self, fromString, importFileName, root):
        '''Return the fileName to be used in messages.'''
        at = self
        if fromString:
            fileName = "<string-file>"
        elif importFileName:
            fileName = importFileName
        elif root.isAnyAtFileNode():
            fileName = root.anyAtFileNodeName()
        else:
            fileName = None
        if fileName:
            # Fix bug 102: call the commander method, not the global funtion.
            fileName = at.c.os_path_finalize(fileName)
        return fileName
    #@+node:ekr.20100224050618.11547: *6* at.isFileLike
    def isFileLike(self, s):
        '''Return True if s has file-like sentinels.'''
        trace = False and not g.unitTesting
        at = self; tag = "@+leo"
        s = g.toUnicode(s)
        i = s.find(tag)
        if i == -1:
            if trace: g.trace('found: False', repr(s))
            return True # Don't use the cache.
        else:
            j, k = g.getLine(s, i)
            line = s[j: k]
            valid, new_df, start, end, isThin = at.parseLeoSentinel(line)
            if trace: g.trace('found: True isThin:',
                isThin, repr(line))
            return not isThin
    #@+node:vitalije.20170701155512.1: *6* at.checkExternalFileAgainstDb
    #@+at
    #     This method assumes that file was already read and that
    #     at.initReadLine was called, which did set at._file_bytes to
    #     content of file as encoded string.
    # 
    #     This is also true if we are reading fromString.
    #@@c
    def checkExternalFileAgainstDb(self, root):
        '''Returns True if file is not modified since last save in db.
           Otherwise returns False.'''
        conn = self.c.sqlite_connection
        if conn is None: return False
        hx = hashlib.md5(self._file_bytes).hexdigest()
        try:
            hx2 = conn.execute(
                    '''select value from extra_infos
                            where name=?''',
                    ('md5_' + root.gnx,)
                ).fetchone()
        except sqlite3.OperationalError:
            hx2 = False
        return hx2 and hx2[0] == hx
    #@+node:ekr.20041005105605.26: *5* at.readAll
    def readAll(self, root, force=False):
        """Scan positions, looking for @<file> nodes to read."""
        at, c = self, self.c
        use_tracer = False
        if use_tracer: tt = g.startTracer()
        if force:
            # Capture the current headline only if
            # we aren't doing the initial read.
            c.endEditing()
        t1 = time.time()
        nRead = 0
        p = root.copy()
        scanned_tnodes = set()
        c.init_error_dialogs()
        after = p.nodeAfterTree() if force else None
        while p and p != after:
            data = (p.gnx, g.fullPath(c, p))
            #skip clones referring to exactly the same paths.
            if data in scanned_tnodes:
                p.moveToNodeAfterTree()
                continue
            scanned_tnodes.add(data)
            if not p.h.startswith('@'):
                p.moveToThreadNext()
            elif p.isAtIgnoreNode():
                if p.isAnyAtFileNode():
                    c.ignored_at_file_nodes.append(p.h)
                p.moveToNodeAfterTree()
            elif p.isAtThinFileNode():
                nRead += 1
                at.read(p, force=force)
                p.moveToNodeAfterTree()
            elif p.isAtAutoNode():
                nRead += 1
                fileName = p.atAutoNodeName()
                at.readOneAtAutoNode(fileName, p)
                p.moveToNodeAfterTree()
            elif p.isAtEditNode():
                nRead += 1
                fileName = p.atEditNodeName()
                at.readOneAtEditNode(fileName, p)
                p.moveToNodeAfterTree()
            elif p.isAtShadowFileNode():
                nRead += 1
                fileName = p.atShadowFileNodeName()
                at.readOneAtShadowNode(fileName, p)
                p.moveToNodeAfterTree()
            elif p.isAtFileNode():
                nRead += 1
                at.read(p, force=force)
                p.moveToNodeAfterTree()
            elif p.isAtAsisFileNode() or p.isAtNoSentFileNode():
                at.rememberReadPath(g.fullPath(c, p), p)
                p.moveToNodeAfterTree()
            elif p.isAtCleanNode():
                nRead += 1
                at.readOneAtCleanNode(p)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        if not g.unitTesting:
            if nRead:
                t2 = time.time()
                g.es('read %s files in %2.2f seconds' % (nRead, t2 - t1))
            elif force:
                g.es("no @<file> nodes in the selected tree")
        if use_tracer: tt.stop()
        c.raise_error_dialogs()
    #@+node:ekr.20080801071227.7: *5* at.readAtShadowNodes
    def readAtShadowNodes(self, p):
        '''Read all @shadow nodes in the p's tree.'''
        at = self
        after = p.nodeAfterTree()
        p = p.copy() # Don't change p in the caller.
        while p and p != after: # Don't use iterator.
            if p.isAtShadowFileNode():
                fileName = p.atShadowFileNodeName()
                at.readOneAtShadowNode(fileName, p)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20070909100252: *5* at.readOneAtAutoNode
    def readOneAtAutoNode(self, fileName, p):
        '''Read an @auto file into p. Return the *new* position.'''
        trace = False and not g.unitTesting
        at, c, ic = self, self.c, self.c.importCommands
        oldChanged = c.isChanged()
        at.default_directory = g.setDefaultDirectory(c, p, importing=True)
        fileName = c.os_path_finalize_join(at.default_directory, fileName)
        if not g.os_path_exists(fileName):
            g.error('not found: %r' % (p.h), nodeLink=p.get_UNL(with_proto=True))
            return p
        # Remember that we have seen the @auto node.
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fileName, p)
        s, ok, fileKey = c.cacher.readFile(fileName, p)
        if ok:
            if trace: g.trace('unchanged:', p.h)
            # Even if the file is in the cache, the @persistence node may be different.
            if c.persistenceController:
                c.persistenceController.update_after_read_foreign_file(p)
            g.doHook('after-auto', c=c, p=p)
                # call after-auto callbacks
                # 2011/09/30: added call to g.doHook here.
            return p
        if not g.unitTesting:
            g.es("reading:", p.h)
        try:
            # For #451: return p.
            old_p = p.copy()
            at.scanAllDirectives(
                p,
                forcePythonSentinels=False,
                importing=True,
                reading=True,
            )
            p.v.b = '' # Required for @auto API checks.
            p.deleteAllChildren()
            p = ic.createOutline(fileName, parent=p.copy())
            # Do *not* select a postion here.
            # That would improperly expand nodes.
                # c.selectPosition(p)
            if trace: g.trace(at.language, p.h)
        except Exception:
            p = old_p
            ic.errors += 1
            g.es_print('Unexpected exception importing', fileName)
            g.es_exception()
        if ic.errors:
            g.error('errors inhibited read @auto %s' % (fileName))
        elif c.persistenceController:
            c.persistenceController.update_after_read_foreign_file(p)
        # Finish.
        if ic.errors or not g.os_path_exists(fileName):
            p.clearDirty()
            c.setChanged(oldChanged)
        else:
            c.cacher.writeFile(p, fileKey)
            g.doHook('after-auto', c=c, p=p)
        return p
    #@+node:ekr.20090225080846.3: *5* at.readOneAtEditNode
    def readOneAtEditNode(self, fn, p):
        at = self
        c = at.c
        ic = c.importCommands
        at.default_directory = g.setDefaultDirectory(c, p, importing=True)
        fn = c.os_path_finalize_join(at.default_directory, fn)
        junk, ext = g.os_path_splitext(fn)
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fn, p)
        if not g.unitTesting:
            g.es("reading: @edit %s" % (g.shortFileName(fn)))
        s, e = g.readFileIntoString(fn, kind='@edit')
        if s is None: return
        encoding = 'utf-8' if e is None else e
        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()
        changed = c.isChanged()
        head = ''
        ext = ext.lower()
        if ext in ('.html', '.htm'): head = '@language html\n'
        elif ext in ('.txt', '.text'): head = '@nocolor\n'
        else:
            language = ic.languageForExtension(ext)
            if language and language != 'unknown_language':
                head = '@language %s\n' % language
            else:
                head = '@nocolor\n'
        p.b = g.u(head) + g.toUnicode(s, encoding=encoding, reportErrors='True')
        if not changed: c.setChanged(False)
        g.doHook('after-edit', p=p)
    #@+node:ekr.20150204165040.5: *5* at.readOneAtCleanNode & helpers
    def readOneAtCleanNode(self, root):
        '''Update the @clean/@nosent node at root.'''
        trace = False and not g.unitTesting
        at, c, x = self, self.c, self.c.shadowController
        fileName = g.fullPath(c, root)
        if not g.os_path_exists(fileName):
            g.es_print('not found: %s' % (fileName), color='red',
                nodeLink=root.get_UNL(with_proto=True))
            return
        at.rememberReadPath(fileName, root)
        # Set at.encoding first.
        at.initReadIvars(root, fileName)
            # Must be called before at.scanAllDirectives.
        at.scanAllDirectives(root)
            # Sets at.startSentinelComment/endSentinelComment.
        new_public_lines = at.read_at_clean_lines(fileName)
        old_private_lines = self.write_at_clean_sentinels(root)
        marker = x.markerFromFileLines(old_private_lines, fileName)
        old_public_lines, junk = x.separate_sentinels(old_private_lines, marker)
        if old_public_lines:
            new_private_lines = x.propagate_changed_lines(
                new_public_lines, old_private_lines, marker, p=root)
        else:
            if trace: g.trace('*** no previous lines.' '')
            new_private_lines = []
            root.b = ''.join(new_public_lines)
            root.clearOrphan()
            return True
        if trace:
            self.dump(new_public_lines, 'new public')
            self.dump(old_private_lines, 'old private')
            self.dump(new_private_lines, 'new private')
        if new_private_lines == old_private_lines:
            if trace: g.trace('lines match')
            return True
        if not g.unitTesting:
            g.es("updating:", root.h)
        # The following is like at.read() w/o caching logic.
        root.clearVisitedInTree()
        # Init the input stream used by read-open file.
        # g.trace('\nnew_private_lines...\n',''.join(new_private_lines))
        at.read_lines = new_private_lines
        at.read_ptr = 0
        # Read the file using the @file read logic.
        # g.trace('***',repr(at.startSentinelComment),repr(at.endSentinelComment))
        thinFile = at.readOpenFile(root, fileName, deleteNodes=True)
        root.clearDirty()
        if at.errors == 0:
            at.deleteUnvisitedNodes(root)
            at.deleteTnodeList(root)
            at.readPostPass(root, thinFile)
                # Used by mod_labels plugin: May set c dirty.
            root.clearOrphan()
        else:
            root.setOrphan()
        at.deleteAllTempBodyStrings()
        return at.errors == 0
    #@+node:ekr.20150204165040.7: *6* at.dump_lines
    def dump(self, lines, tag):
        '''Dump all lines.'''
        print('***** %s lines...\n' % tag)
        for s in lines:
            print(s.rstrip())
    #@+node:ekr.20150204165040.8: *6* at.read_at_clean_lines
    def read_at_clean_lines(self, fn):
        '''Return all lines of the @clean/@nosent file at fn.'''
        at = self
        s = at.openFileHelper(fn)
            # Use the standard helper. Better error reporting.
            # Important: uses 'rb' to open the file.
        s = g.toUnicode(s, encoding=at.encoding)
        s = s.replace('\r\n', '\n')
            # Suppress meaningless "node changed" messages.
        return g.splitLines(s)
    #@+node:ekr.20150204165040.9: *6* at.write_at_clean_sentinels
    def write_at_clean_sentinels(self, root):
        '''
        Return all lines of the @clean tree as if it were
        written as an @file node.
        '''
        at = self.c.atFileCommands
        at.write(root,
            kind='@nosent',
            nosentinels=False,
            toString=True,
        )
        s = g.toUnicode(at.stringOutput, encoding=at.encoding)
        return g.splitLines(s)
    #@+node:ekr.20080711093251.7: *5* at.readOneAtShadowNode
    def readOneAtShadowNode(self, fn, p, force=False):
        trace = False and not g.unitTesting
        at = self; c = at.c; x = c.shadowController
        if not fn == p.atShadowFileNodeName():
            return at.error('can not happen: fn: %s != atShadowNodeName: %s' % (
                fn, p.atShadowFileNodeName()))
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fn, p)
        at.default_directory = g.setDefaultDirectory(c, p, importing=True)
        fn = c.os_path_finalize_join(at.default_directory, fn)
        shadow_fn = x.shadowPathName(fn)
        shadow_exists = g.os_path_exists(shadow_fn) and g.os_path_isfile(shadow_fn)
        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()
        if trace:
            g.trace('shadow_exists', shadow_exists, shadow_fn)
        if shadow_exists:
            at.read(p, atShadow=True, force=force)
        else:
            if not g.unitTesting: g.es("reading:", p.h)
            ok = at.importAtShadowNode(fn, p)
            if ok:
                # Create the private file automatically.
                at.writeOneAtShadowNode(p, toString=False, force=True)
    #@+node:ekr.20080712080505.1: *6* at.importAtShadowNode
    def importAtShadowNode(self, fn, p):
        at = self; c = at.c; ic = c.importCommands
        oldChanged = c.isChanged()
        # Delete all the child nodes.
        while p.hasChildren():
            p.firstChild().doDelete()
        # Import the outline, exactly as @auto does.
        ic.createOutline(fn, parent=p.copy(), atShadow=True)
        if ic.errors:
            g.error('errors inhibited read @shadow', fn)
        if ic.errors or not g.os_path_exists(fn):
            p.clearDirty()
            c.setChanged(oldChanged)
        # else: g.doHook('after-shadow', p = p)
        return ic.errors == 0
    #@+node:ekr.20041005105605.27: *5* at.readOpenFile & helpers
    def readOpenFile(self, root, fileName, deleteNodes=False):
        '''
        Read an open derived file.
        Leo 4.5 and later can only read 4.x derived files.
        '''
        trace = False and not g.unitTesting
        at = self
        firstLines, read_new, thinFile = at.scanHeader(fileName)
            # Important: this sets at.encoding, used by at.readLine.
        at.thinFile = thinFile
            # 2010/01/22: use *only* the header to set self.thinFile.
        if trace: g.trace('1', root.gnx, root.h)
        if deleteNodes and at.shouldDeleteChildren(root, thinFile):
            # Fix bug 889175: Remember the full fileName.
            at.rememberReadPath(fileName, root)
            while root.hasChildren():
                root.firstChild().doDelete()
        if read_new:
            lastLines = at.scanText4(fileName, root)
        else:
            firstLines = []; lastLines = []
            if at.atShadow:
                g.trace(g.callers())
                g.trace('invalid @shadow private file', fileName)
                at.error('invalid @shadow private file', fileName)
            else:
                at.error('can not read 3.x derived file', fileName)
                # g.es('you may upgrade these file using Leo 4.0 through 4.4.x')
                g.es("Please use Leo's import command to read the file")
                # g.trace('root',root and root.h,fileName)
        if root:
            root.v.setVisited() # Disable warning about set nodes.
        at.completeRootNode(firstLines, lastLines, root)
        if trace:
            g.trace('2', root.gnx, root.h)
            # g.trace(at.encoding,fileName)
        return thinFile
    #@+node:ekr.20041005105605.28: *6* at.completeRootNode & helpers
    def completeRootNode(self, firstLines, lastLines, root):
        '''Terminate the root's body text, handling @first and @last.'''
        at = self
        v = root.v
        lines = v.tempBodyList if hasattr(v, 'tempBodyList') else []
        at.completeFirstDirectives(lines, firstLines)
        at.completeLastDirectives(lines, lastLines)
        v.tempBodyList = lines
            # Don't set v.b here: at.readPostPass uses v.tempBodyList.
    #@+node:ekr.20041005105605.117: *7* at.completeFirstDirective
    def completeFirstDirectives(self, out, firstLines):
        '''
        14-SEP-2002 DTHEIN

        Scans the lines in the list 'out' for @first directives, appending the
        corresponding line from 'firstLines' to each @first directive found.

        NOTE: the @first directives must be the very first lines in 'out'.
        '''
        trace = False and not g.unitTesting
        if not firstLines:
            return
        found, j, tag = False, 0, "@first"
        for k, s in enumerate(out):
            # Skip leading whitespace lines.
            if not found and s.isspace():
                continue
            # Quit if something other than @first directive.
            if not g.match(s, 0, tag):
                break
            found = True
            # Quit if no leading lines to apply.
            if j >= len(firstLines):
                break
            # Make the  @first directive.
            leadingLine = " " + firstLines[j]
            out[k] = tag + leadingLine.rstrip() + '\n'
            j += 1
            if trace: g.trace(repr(s))
    #@+node:ekr.20041005105605.118: *7* at.completeLastDirectives
    def completeLastDirectives(self, out, lastLines):
        '''
        14-SEP-2002 DTHEIN.

        Scans the lines in the list 'out' for @last directives, appending the
        corresponding line from 'lastLines' to each @last directive found.

        NOTE: the @last directives must be the very last lines in 'out'.
        '''
        trace = False and not g.unitTesting
        if not lastLines:
            return
        found, j, tag = False, -1, "@last"
        for k in range(-1, -len(out), -1):
            # Skip trailing whitespace lines.
            if not found and not out[k].strip():
                continue
            # Quit if something other than @last directive.
            if not g.match(out[k], 0, tag):
                break
            found = True
            # Quit if no trailing lines to apply.
            if j < -len(lastLines):
                break
            # Make the @last directive.
            trailingLine = " " + lastLines[j]
            out[k] = tag + trailingLine.rstrip() + '\n'
            j -= 1
            if trace: g.trace(repr(out[k]))
    #@+node:ekr.20100122130101.6175: *6* at.shouldDeleteChildren
    def shouldDeleteChildren(self, root, thinFile):
        '''Return True if we should delete all children before a read.'''
        # Delete all children except for old-style @file nodes
        if root.isAtFileNode() and not thinFile:
            return False
        else:
            return True
    #@+node:ekr.20041005105605.71: *4* at.Reading (4.x)
    #@+node:ekr.20041005105605.73: *5* at.findChild4 (legacy only)
    def findChild4(self, headline):
        """
        Return the next VNode in at.root.tnodeList.
        Called only for **legacy** @file nodes.

        tnodeLists are used *only* when reading @file (not @thin) nodes.
        tnodeLists compensate for not having gnx's in derived files!
        """
        trace = True and not g.unitTesting
        at = self; v = at.root.v
        if trace: g.trace('legacy file', headline)
        # if not g.unitTesting:
            # if headline.startswith('@file'):
                # g.es_print('Warning: @file logic',headline)
        if trace: g.trace('%s %s %s' % (
            at.tnodeListIndex,
            v.tnodeList[at.tnodeListIndex], headline))
        if not hasattr(v, "tnodeList"):
            at.readError("no tnodeList for " + repr(v))
            g.es("write the @file node or use the Import Derived File command")
            g.trace("no tnodeList for ", v, g.callers())
            return None
        if at.tnodeListIndex >= len(v.tnodeList):
            at.readError("bad tnodeList index: %d, %s" % (
                at.tnodeListIndex, repr(v)))
            g.trace("bad tnodeList index",
                at.tnodeListIndex, len(v.tnodeList), v)
            return None
        v = v.tnodeList[at.tnodeListIndex]
        assert(v)
        at.tnodeListIndex += 1
        # Don't check the headline.  It simply causes problems.
        v.setVisited() # Supress warning/deletion of unvisited nodes.
        return v
    #@+node:ekr.20130911110233.11284: *5* at.readFileToUnicode & helpers
    def readFileToUnicode(self, fn):
        '''
        Carefully sets at.encoding, then uses at.encoding to convert the file
        to a unicode string. Calls at.initReadLine if all went well.

        Sets at.encoding as follows:
        1. Use the BOM, if present. This unambiguously determines the encoding.
        2. Use the -encoding= field in the @+leo header, if present and valid.
        3. Otherwise, uses existing value of at.encoding, which comes from:
            A. An @encoding directive, found by at.scanAllDirectives.
            B. The value of c.config.default_derived_file_encoding.

        Returns the string, or None on failure.

        This method is now part of the main @file read code.
        at.openFileForReading calls this method to read all @file nodes.
        Previously only at.scanHeaderForThin (import code) called this method.
        '''
        at = self
        # g.trace('=====', at.errors)
        s = at.openFileHelper(fn)
        if s is not None:
            e, s = g.stripBOM(s)
            if e:
                # The BOM determines the encoding unambiguously.
                s = g.toUnicode(s, encoding=e)
            else:
                # Get the encoding from the header, or the default encoding.
                s_temp = g.toUnicode(s, 'ascii', reportErrors=False)
                e = at.getEncodingFromHeader(fn, s_temp)
                # g.trace(e,g.shortFileName(fn))
                s = g.toUnicode(s, encoding=e)
            s = s.replace('\r\n', '\n')
            at.encoding = e
            at.initReadLine(s)
        return s
    #@+node:ekr.20130911110233.11285: *6* at.openFileHelper
    def openFileHelper(self, fn):
        '''Open a file, reporting all exceptions.'''
        at = self
        s = None
        try:
            f = open(fn, 'rb')
            s = f.read()
            f.close()
        except IOError:
            at.error('can not open %s' % (fn))
        except Exception:
            at.error('Exception reading %s' % (fn))
            g.es_exception()
        return s
    #@+node:ekr.20130911110233.11287: *6* at.getEncodingFromHeader
    def getEncodingFromHeader(self, fn, s):
        '''
        Return the encoding given in the @+leo sentinel, if the sentinel is
        present, or the previous value of at.encoding otherwise.
        '''
        at = self
        if at.errors:
            g.trace('can not happen: at.errors > 0')
            e = at.encoding
            if g.unitTesting: assert False, g.callers()
                # This can happen when the showTree command in a unit test is left on.
                # A @file/@clean node is created which refers to a non-existent file.
                # It's surprisingly difficult to set at.error=0 safely elsewhere.
                # Otoh, I'm not sure why this test here is ever really useful.
        else:
            at.initReadLine(s)
            old_encoding = at.encoding
            assert old_encoding
            at.encoding = None
            # Execute scanHeader merely to set at.encoding.
            at.scanHeader(fn, giveErrors=False)
            e = at.encoding or old_encoding
        assert e
        return e
    #@+node:ekr.20050301105854: *5* at.readPostPass & helpers
    def readPostPass(self, root, thinFile):
        '''Post-process all vnodes.'''
        at = self
        seen = {}
        for p in root.self_and_subtree():
            v = p.v
            if v.gnx not in seen:
                seen[v.gnx] = v
                at.terminateNode(postPass=True, v=v)
                # new-read: at.terminateNode has done all the work.
                if hasattr(v, 'tempBodyList'):
                    delattr(v, 'tempBodyList')
                if hasattr(v, 'tempRoots'):
                    delattr(v, 'tempRoots')
    #@+node:ekr.20150309154506.27: *6* at.handleChangedNode
    def handleChangedNode(self, new_body, old_body, p, thinFile):
        '''Set ancestor files dirty and support mod_labels plugin.'''
        trace = False and not g.unitTesting
        c = self.c
        if thinFile: # Expected.
            if trace: g.trace('****', p.h)
            p.v.setBodyString(new_body)
            if p.v.isDirty():
                p.setAllAncestorAtFileNodesDirty()
        else:
            c.setBodyString(p, new_body) # Sets c and p dirty.
        if p.v.isDirty():
            # New in Leo 4.3: support for mod_labels plugin:
            try:
                c.mod_label_controller.add_label(p, "before change:", old_body)
            except Exception:
                pass
            # This warning is given elsewhere.
            # g.warning("changed:",p.h)
    #@+node:ekr.20100628072537.5814: *6* at.terminateNode & helpers
    def terminateNode(self, middle=False, postPass=True, v=None):
        '''
        Set the body text of at.v, and issue warning if it has changed.

        This is called as follows:

        old sentinels: when handling a @-node sentinel.
        new sentinels: from the post-pass when v.tempBodyList exists.
        '''
        at = self
        trace = False and at.readVersion5 and not g.unitTesting
        if not v: v = at.v
        # Compute the new text.
        if at.readVersion5:
            s = ''.join(v.tempBodyList) if hasattr(v, 'tempBodyList') else ''
        else:
            s = ''.join(at.out)
        s = g.toUnicode(s)
        if trace: g.trace('%28s %s' % (v.h, repr(s)))
        if at.importing:
            v._bodyString = s # Allowed use of _bodyString.
        elif middle:
            pass # Middle sentinels never alter text.
        else:
            at.terminateBody(v, postPass)
        # Delete tempBodyList.
        if hasattr(v, 'tempBodyList'): delattr(v, 'tempBodyList')
    #@+node:ekr.20100628124907.5816: *7* at.indicateNodeChanged
    def indicateNodeChanged(self, old, new, postPass, v):
        '''
        Add an entry to c.nodeConflictList.
        Called only from at.terminateBody.
        '''
        trace = False and not g.unitTesting
        at, c = self, self.c
        debug = False # Debug perfect import.
        # Ignore *all* trailing whitespace.
        if new.rstrip() == old.rstrip():
            return
        if at.perfectImportRoot:
            if not postPass:
                at.correctedLines += 1
                if debug:
                    at.reportCorrection(old, new, v)
                v.setDirty()
                    # Just mark the vnode dirty.
                    # Ancestors will be marked dirty later.
                c.setChanged(True)
            return
        if c.make_node_conflicts_node:
            if trace:
                g.es_print('Creating recovered node', v.h)
            c.nodeConflictList.append(g.bunch(
                tag='(uncached)',
                gnx=v.gnx,
                fileName=at.root.h,
                b_old=old,
                b_new=new,
                h_old=v._headString,
                h_new=v._headString,
                root_v = at.root and at.root.v,
            ))
        # Always do this.
        v.setDirty()
            # Just set the dirty bit. Ancestors will be marked dirty later.
        c.changed = True
            # Important: the dirty bits won't stick unless we set c.changed here.
            # Do *not* call c.setChanged(True) here: that would be too slow.
    #@+node:ekr.20100628124907.5818: *7* at.reportCorrection
    def reportCorrection(self, old, new, v):
        '''Debugging only. Report changed perfect import lines.'''
        at = self
        found = any([p.v == v for p in at.perfectImportRoot.self_and_subtree()])
        if found:
            g.pr('\n', '-' * 40)
            g.pr("old", len(old))
            for line in g.splitLines(old):
                line = line.replace(' ', '< >').replace('\t', '<TAB>').replace('\n', '<NL>')
                g.pr(repr(str(line)))
            g.pr('\n', '-' * 40)
            g.pr("new", len(new))
            for line in g.splitLines(new):
                #line = line.replace(' ','< >').replace('\t','<TAB>')
                g.pr(repr(str(line)))
            g.pr('\n', '-' * 40)
        else:
            # This should never happen.
            g.error("correcting hidden node: v=", repr(v))
    #@+node:ekr.20100702062857.5824: *7* at.terminateBody (sets tempRoots)
    def terminateBody(self, v, postPass=False):
        '''Terminate scanning of body text for node v. Set v.b.'''
        trace = False and not g.unitTesting
        at = self
        if at.readVersion5:
            new = ''.join(v.tempBodyList) if hasattr(v, 'tempBodyList') else ''
        else:
            new = ''.join(at.out)
        new = g.toUnicode(new)
        # new-read: at.createThinChild4 creates v.tempRoots.
        # *Do* allow changes to the root node.
        if hasattr(v, 'tempRoots'):
            if trace:
                g.trace('tempRoots: %20s %s' % (
                    v.h,
                    list([g.shortFileName(z) for z in v.tempRoots]),
                ))
            old = v.bodyString()
            if old != new:
                # This *always* creates a recovered node.
                at.indicateNodeChanged(old, new, postPass, v)
                # The last external file wins.
                v.setBodyString(new)
        else:
            # No other @file node has set this node.
            # Just replace the body string
            v.tempRoots = set()
            v.setBodyString(new)
        v.tempRoots.add(self.root.h)
        at.bodySetInited(v)
            # Note: the sax code also sets this, so we can't use
            # this "bit" in place of v.tempRoots.
    #@+node:ekr.20041005105605.74: *5* at.scanText4 & allies
    def scanText4(self, fileName, p, verbose=False):
        """Scan a 4.x derived file non-recursively."""
        at = self
        trace = False and not g.unitTesting
        verbose = True
        at.initScanText4(p)
        if trace:
            print('')
            g.trace('filename:', fileName)
        try:
            while at.errors == 0 and not at.done:
                s = at.readLine()
                if trace and verbose: g.trace(repr(s))
                at.lineNumber += 1
                if not s:
                    # An error.  We expect readEndLeo to set at.done.
                    break
                kind = at.sentinelKind4(s)
                if kind == at.noSentinel:
                    i = 0
                else:
                    i = at.skipSentinelStart4(s, 0)
                func = at.dispatch_dict[kind]
                if trace: g.trace('%15s %16s %s' % (
                    at.sentinelName(kind), func.__name__, repr(s)))
                func(s, i)
        except AssertionError:
            junk, message, junk = sys.exc_info()
            at.error('scanText4: unexpected assertion failure in',
                'fromString' if at.fromString else fileName,
                '\n', message)
            g.trace(g.callers(5))
            raise
        except Exception:
            # Work around bug https://bugs.launchpad.net/leo-editor/+bug/1074812
            # Crashes in the scanning logic may arise from corrupted external files.
            at.error('The input file appears to be corrupted.')
            g.es_exception()
        if at.errors == 0 and not at.done:
            assert at.endSentinelStack, 'empty sentinel stack'
            at.readError(
                "Unexpected end of file. Expecting %s sentinel" %
                at.sentinelName(at.endSentinelStack[-1]))
        return at.lastLines
    #@+node:ekr.20041005105605.75: *6* at.initScanText4
    def initScanText4(self, p):
        '''Init all ivars for at.scanText4().'''
        at = self
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
        at.endSentinelNodeStack = [None]
        at.endSentinelStack = [at.endLeo] # We have already handled the @+leo sentinel.
        at.lastThinNode = None
        at.out = []
        at.outStack = []
        at.thinChildIndexStack = []
        at.thinNodeStack = []
        at.v1 = p.v
        at.v = p.v
        at.vStack = []
    #@+node:ekr.20041005105605.77: *6* at.readNormalLine & appendToDocPart
    def readNormalLine(self, s, i=0): # i not used.
        at = self
        # g.trace('inCode',at.inCode,repr(s))
        if at.inCode:
            if not at.raw:
                # 2012/06/05: Major bug fix: insert \\-n. for underindented lines.
                n = g.computeLeadingWhitespaceWidth(s, at.tab_width)
                if n < at.indent:
                    # g.trace('n: %s at.indent: %s\n%s' % (n,at.indent,repr(s)))
                    if s.strip():
                        s = r'\\-%s.%s' % (at.indent - n, s.lstrip())
                    else:
                        s = '\n' if s.endswith('\n') else ''
                else: # Legacy
                    s = g.removeLeadingWhitespace(s, at.indent, at.tab_width)
            at.appendToOut(s)
        else:
            at.appendToDocPart(s)
    #@+node:ekr.20100624082003.5942: *7* at.appendToDocPart
    def appendToDocPart(self, s):
        '''Append the next line of the @doc part to docOut.'''
        at = self
        trace = False and at.readVersion5 and not g.unitTesting
        # Skip the leading stuff
        if at.endSentinelComment:
            i = at.skipIndent(s, 0, at.indent)
        else:
            # Skip the single comment delim and a blank.
            i = g.skip_ws(s, 0)
            if g.match(s, i, at.startSentinelComment):
                i += len(at.startSentinelComment)
                if g.match(s, i, " "): i += 1
        if at.readVersion5:
            # Append the line to docOut.
            line = s[i:]
            at.docOut.append(line)
        else:
            # Append line to docOut, possibly stripping the newline.
            line = s[i: -1] # remove newline for rstrip.
            if line == line.rstrip():
                # no trailing whitespace: the newline is real.
                at.docOut.append(line + '\n')
            else:
                # trailing whitespace: the newline is fake.
                at.docOut.append(line)
        if trace: g.trace(repr(line))
    #@+node:ekr.20041005105605.80: *6* start sentinels
    #@+node:ekr.20041005105605.81: *7* at.readStartAll
    def readStartAll(self, s, i):
        """Read an @+all sentinel."""
        at = self
        j = g.skip_ws(s, i)
        leadingWs = s[i: j]
        if leadingWs:
            assert g.match(s, j, "@+all"), 'missing @+all'
        else:
            assert g.match(s, j, "+all"), 'missing +all'
        # Make sure that the generated at-all is properly indented.
        # New code (for both old and new sentinels).
        # Regularize the whitespace preceding the @all directive.
        junk_i, w = g.skip_leading_ws_with_indent(s, 0, at.tab_width)
        lws2 = g.computeLeadingWhitespace(max(0, w - at.indent), at.tab_width)
        at.appendToOut(lws2 + "@all\n")
        at.endSentinelStack.append(at.endAll)
        if at.readVersion5:
            at.endSentinelNodeStack.append(at.v)
            at.endSentinelLevelStack.append(len(at.thinNodeStack))
    #@+node:ekr.20041005105605.85: *7* at.readStartNode & helpers
    def readStartNode(self, s, i, middle=False):
        """
        Read an @+node or @+middle sentinel.
        This will terminate the previous node.
        """
        trace = False and not g.unitTesting
        at = self
        gnx, headline, i, level, ok = at.parseNodeSentinel(s, i, middle)
        # trace = trace and headline.startswith('ic.appendStringToBody')
        if trace: g.trace(gnx, headline)
        if at.v1:
            # Fix bug 169: https://github.com/leo-editor/leo-editor/issues/169
            # import-file does not preserve gnx of root @file node
            # g.trace(at.v1.fileIndex,'-->',gnx,at.v1.h)
            at.v1.fileIndex = gnx
            at.v1 = None
        if not ok: return
        # Switch context.
        if at.readVersion5:
            # Terminate the *previous* doc part if it exists.
            if at.docOut:
                at.appendToOut(''.join(at.docOut))
                at.docOut = []
            # Important: with new sentinels we *never*
            # terminate nodes until the post-pass.
        else:
            assert not at.docOut, 'not at.docOut' # Cleared by @-node sentinel.
            at.outStack.append(at.out)
            at.out = []
        at.inCode = True
        at.raw = False # End raw mode.
        at.vStack.append(at.v)
        at.indentStack.append(at.indent)
        i, at.indent = g.skip_leading_ws_with_indent(s, 0, at.tab_width)
        if at.importing:
            p = at.createImportedNode(at.root, headline)
            at.v = p.v
        elif at.thinFile:
            at.v = at.createNewThinNode(gnx, headline, level)
        else:
            at.v = at.findChild4(headline)
        if not at.v:
            return # This can happen when reading strange files.
        assert at.v == at.root.v or at.v.isVisited(), at.v.h
        at.v.setVisited()
            # Indicate that the VNode has been set in the external file.
        if not at.readVersion5:
            at.endSentinelStack.append(at.endNode)
    #@+node:ekr.20100625085138.5957: *8* at.createNewThinNode & helpers
    def createNewThinNode(self, gnx, headline, level):
        '''Create a new (new-style) vnode.'''
        at = self
        # testFile = at.targetFileName.endswith('clone-revert-test.txt')
        # trace = (False and testFile) and not g.unitTesting
        trace = False and not g.unitTesting
        if trace:
            g.trace('v5: %s level: %2s %-24s %s' % (at.readVersion5, level, gnx, headline))
            g.trace(at.thinNodeStack)
        if at.thinNodeStack:
            if at.readVersion5: # Expected.
                v = self.createV5ThinNode(gnx, headline, level)
            else: # Legacy files.
                at.thinNodeStack.append(at.lastThinNode)
                v = at.old_createThinChild4(gnx, headline)
        else:
            v = at.root.v
            if at.readVersion5:
                at.thinChildIndexStack.append(0)
            at.thinNodeStack.append(v)
        at.lastThinNode = v
        return v
    #@+node:ekr.20130121102015.10272: *9* at.createV5ThinNode
    def createV5ThinNode(self, gnx, headline, level):
        '''Create a version 5 vnode.'''
        at = self
        trace = False and not g.unitTesting
        oldLevel = len(at.thinNodeStack)
        newLevel = level
        assert oldLevel >= 1
        assert newLevel >= 1
        # The invariant: top of at.thinNodeStack after changeLevel is the parent.
        at.changeLevel(oldLevel, newLevel - 1)
        parent = at.thinNodeStack[-1]
        n = at.thinChildIndexStack[-1]
        if trace: g.trace(oldLevel, newLevel - 1, n, parent.h, headline)
        v = at.new_createThinChild4(gnx, headline, n, parent)
        at.thinChildIndexStack[-1] = n + 1
        at.thinNodeStack.append(v)
        at.thinChildIndexStack.append(0)
        at.lastThinNode = v
        # Ensure that the body text is set only once.
        if v.isVisited():
            if hasattr(v, 'tempBodyList'):
                delattr(v, 'tempBodyList')
        else:
            # This is the only place we call v.setVisited in the read logic.
            v.setVisited()
        return v
    #@+node:ekr.20130121075058.10246: *9* at.new_createThinChild4
    def new_createThinChild4(self, gnxString, headline, n, parent):
        """
        Find or create a new *vnode* whose parent (also a vnode)
        is at.lastThinNode. This is called only for @thin trees.
        """
        c = self.c
        gnx = gnxString = g.toUnicode(gnxString)
        gnxDict = c.fileCommands.gnxDict
        v = gnxDict.get(gnxString)
        if v and gnx != v.fileIndex:
            g.internalError('v.fileIndex: %s gnx: %s' % (v.fileIndex, gnx))
            return None
        if v:
            # new-read: Always honor the healine.
            v.h = headline
            child = v
            if n >= len(parent.children):
                child._linkAsNthChild(parent, n)
        else:
            v = leoNodes.VNode(context=c, gnx=gnx)
            v._headString = headline # Allowed use of v._headString.
            gnxDict[gnxString] = v
            if 'gnx' in g.app.debug:
                g.trace(c.shortFileName(), gnxString, v)
            child = v
            child._linkAsNthChild(parent, n)
        return child
    #@+node:ekr.20130121075058.10245: *9* at.old_createThinChild4
    def old_createThinChild4(self, gnxString, headline):
        """
        Find or create a new *vnode* whose parent (also a vnode)
        is at.lastThinNode. This is called only for @thin trees.
        """
        trace = False and not g.unitTesting
        verbose = True
        at = self; c = at.c
        gnx = gnxString = g.toUnicode(gnxString)
        gnxDict = c.fileCommands.gnxDict
        last = at.lastThinNode # A VNode.
        lastIndex = last.fileIndex
        if trace and verbose: g.trace("last %s, gnx %s %s" % (
            last and last.h, gnxString, headline))
        parent = last
        children = parent.children
        for child in children:
            if gnx == child.fileIndex:
                break
        else:
            child = None
        if at.cloneSibCount > 1:
            n = at.cloneSibCount; at.cloneSibCount = 0
            if child: clonedSibs, junk = at.scanForClonedSibs(parent, child)
            else: clonedSibs = 0
            copies = n - clonedSibs
            if trace: g.trace(copies, headline)
        else:
            if gnx == lastIndex:
                last.setVisited()
                    # Supress warning/deletion of unvisited nodes.
                if trace: g.trace('found last', last)
                return last
            if child:
                child.setVisited()
                    # Supress warning/deletion of unvisited nodes.
                if trace: g.trace('found child', child)
                return child
            copies = 1 # Create exactly one copy.
        while copies > 0:
            copies -= 1
            # Create the VNode only if it does not already exist.
            v = gnxDict.get(gnxString)
            if v:
                if gnx != v.fileIndex:
                    g.internalError('v.fileIndex: %s gnx: %s' % (
                        v.fileIndex, gnx))
            else:
                v = leoNodes.VNode(context=c, gnx=gnx)
                v._headString = headline # Allowed use of v._headString.
                gnxDict[gnxString] = v
                if 'gnx' in g.app.debug:
                    g.trace(c.shortFileName(), gnxString, v)
            child = v
            child._linkAsNthChild(parent, parent.numberOfChildren())
        if trace: g.trace('new node: %s' % child.h)
        child.setVisited() # Supress warning/deletion of unvisited nodes.
        return child
    #@+node:ekr.20100625184546.5979: *8* at.parseNodeSentinel & helpers
    def parseNodeSentinel(self, s, i, middle):
        at = self
        if middle:
            assert g.match(s, i, "+middle:"), 'missing +middle'
            i += 8
        else:
            if not g.match(s, i, '+node:'): g.trace(repr(s[i: i + 40]), g.callers(5))
            assert g.match(s, i, "+node:"), 'missing +node:'
            i += 6
        # Get the gnx and the headline.
        if at.thinFile:
            gnx, i, level, ok = at.parseThinNodeSentinel(s, i)
            if not ok:
                # Bug fix: 2014/03/26: return 5-tuple
                return None, None, None, None, False
        else:
            gnx, level = None, None
        headline = at.getNodeHeadline(s, i)
        return gnx, headline, i, level, True
    #@+node:ekr.20100625085138.5955: *9* at.getNodeHeadline
    def getNodeHeadline(self, s, i):
        '''Set headline to the rest of the line.
        Don't strip leading whitespace.'''
        at = self
        if at.endSentinelComment:
            k = s.rfind(at.endSentinelComment, i)
            h = s[i: k].rstrip() # works if k == -1
        else:
            h = s[i: -1].rstrip()
        # Undo the CWEB hack: undouble @ signs if\
        # the opening comment delim ends in '@'.
        if at.startSentinelComment[-1:] == '@':
            h = h.replace('@@', '@')
        return h
    #@+node:ekr.20100625085138.5953: *9* at.parseThinNodeSentinel
    def parseThinNodeSentinel(self, s, i):
        at = self

        def oops(message):
            if g.unitTesting: g.trace(message, repr(s))
            else: at.readError(message)
            return None, None, None, False

        j = s.find(':', i)
        if j == -1:
            return oops('Expecting gnx in @+node sentinel')
        else:
            gnx = s[i: j]
        if at.readVersion5:
            if not g.match(s, j, ': '):
                return oops('Expecting space after gnx')
            i = j + 2
            if not g.match(s, i, '*'):
                return oops('No level stars')
            i += 1
            if g.match(s, i, ' '):
                level = 1; i += 1
            elif g.match(s, i, '* '):
                level = 2; i += 2
            else:
                # The level stars have the form *N*.
                level = 0; j = i
                while i < len(s) and s[i].isdigit():
                    i += 1
                if i > j:
                    level = int(s[j: i])
                else:
                    return oops('No level number')
                if g.match(s, i, '* '):
                    i += 2
                else:
                    return oops('No space after level stars')
        else: # not readVersion5.
            i = j + 1 # Skip the gnx.
            level = 0
        return gnx, i, level, True
    #@+node:ekr.20041005105605.111: *7* at.readRef (paired using new sentinels)
    #@+at The sentinel contains an @ followed by a section name in angle brackets.
    # This code is different from the code for the @@ sentinel: the expansion
    # of the reference does not include a trailing newline.
    #@@c

    def readRef(self, s, i):
        """Handle an @<< sentinel."""
        at = self
        if at.readVersion5:
            assert g.match(s, i, "+"), 'g.match(s,i,"+")'
            i += 1 # Skip the new plus sign.
            # New in Leo 4.8: Ignore the spellling in leadingWs.
            # Instead, compute lws2, the regularized leading whitespace.
            junk_i, w = g.skip_leading_ws_with_indent(s, 0, at.tab_width)
            lws2 = g.computeLeadingWhitespace(max(0, w - at.indent), at.tab_width)
        else:
            lws2 = ''
        j = g.skip_ws(s, i)
        assert g.match(s, j, "<<"), 'missing @<< sentinel'
        if at.endSentinelComment:
            k = s.find(at.endSentinelComment, i)
            if at.readVersion5:
                line = lws2 + s[i: k] + '\n' # Restore the newline.
            else:
                line = s[i: k] # No trailing newline, whatever k is.
        else:
            if at.readVersion5:
                line = lws2 + s[i:]
            else:
                line = s[i: -1] # No trailing newline
        # Undo the cweb hack.
        start = at.startSentinelComment
        if start and start[-1] == '@':
            line = line.replace('@@', '@')
        at.appendToOut(line)
        if at.readVersion5:
            # g.trace(at.indent,repr(line))
            at.endSentinelLevelStack.append(len(at.thinNodeStack))
            at.endSentinelIndentStack.append(at.indent)
            at.endSentinelStack.append(at.endRef)
            at.endSentinelNodeStack.append(at.v)
        else:
            pass # There is no paired @-ref sentinel.
    #@+node:ekr.20041005105605.82: *7* at.readStartAt/Doc & helpers
    #@+node:ekr.20100624082003.5938: *8* readStartAt
    def readStartAt(self, s, i):
        """Read an @+at sentinel."""
        at = self
        assert g.match(s, i, "+at"), 'missing +at'
        i += 3
        if at.readVersion5: # Append whatever follows the sentinel.
            j = at.skipToEndSentinel(s, i)
            follow = s[i: j]
            at.appendToOut('@' + follow + '\n')
            at.docOut = []
            at.inCode = False
        else:
            j = g.skip_ws(s, i)
            ws = s[i: j]
            at.docOut = ['@' + ws + '\n']
                # This newline may be removed by a following @nonl
            at.inCode = False
            at.endSentinelStack.append(at.endAt)
    #@+node:ekr.20100624082003.5939: *8* readStartDoc
    def readStartDoc(self, s, i):
        """Read an @+doc sentinel."""
        at = self
        assert g.match(s, i, "+doc"), 'missing +doc'
        i += 4
        if at.readVersion5: # Append whatever follows the sentinel.
            j = at.skipToEndSentinel(s, i)
            follow = s[i: j] + '\n'
            at.appendToOut('@' + follow + '\n')
            at.docOut = []
            at.inCode = False
        else:
            j = g.skip_ws(s, i)
            ws = s[i: j]
            at.docOut = ["@doc" + ws + '\n']
                # This newline may be removed by a following @nonl
            at.inCode = False
            at.endSentinelStack.append(at.endDoc)
    #@+node:ekr.20100624082003.5940: *8* skipToEndSentinel
    def skipToEndSentinel(self, s, i):
        '''Skip to the end of the sentinel line.'''
        at = self
        end = at.endSentinelComment
        if end:
            j = s.find(end, i)
            if j == -1:
                return g.skip_to_end_of_line(s, i)
            else:
                return j
        else:
            return g.skip_to_end_of_line(s, i)
    #@+node:ekr.20041005105605.83: *7* at.readStartLeo
    def readStartLeo(self, s, i):
        """Read an unexpected @+leo sentinel."""
        at = self
        assert g.match(s, i, "+leo"), 'missing +leo sentinel'
        at.readError("Ignoring unexpected @+leo sentinel")
    #@+node:ekr.20041005105605.84: *7* at.readStartMiddle
    def readStartMiddle(self, s, i):
        """Read an @+middle sentinel."""
        at = self
        at.readStartNode(s, i, middle=True)
        g.warning('Warning: file contains @+middle sentinel')
    #@+node:ekr.20041005105605.89: *7* at.readStartOthers
    def readStartOthers(self, s, i):
        """Read an @+others sentinel."""
        at = self
        j = g.skip_ws(s, i)
        leadingWs = s[i: j]
        if leadingWs:
            assert g.match(s, j, "@+others"), 'missing @+others'
        else:
            assert g.match(s, j, "+others"), 'missing +others'
        # Make sure that the generated at-others is properly indented.
        # New code (for both old and new sentinels).
        # Regularize the whitespace preceding the @others directive.
        junk_i, w = g.skip_leading_ws_with_indent(s, 0, at.tab_width)
        lws2 = g.computeLeadingWhitespace(max(0, w - at.indent), at.tab_width)
        at.appendToOut(lws2 + "@others\n")
        if at.readVersion5:
            at.endSentinelIndentStack.append(at.indent)
            at.endSentinelStack.append(at.endOthers)
            at.endSentinelNodeStack.append(at.v)
            at.endSentinelLevelStack.append(len(at.thinNodeStack))
        else:
            at.endSentinelStack.append(at.endOthers)
    #@+node:ekr.20041005105605.90: *6* end sentinels
    #@+node:ekr.20041005105605.91: *7* at.readEndAll
    def readEndAll(self, unused_s, unused_i):
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
            at.changeLevel(oldLevel, newLevel)
            # g.trace('oldLevel',oldLevel,'newLevel',newLevel,'at.v',at.v)
    #@+node:ekr.20041005105605.92: *7* at.readEndAt & readEndDoc
    def readEndAt(self, unused_s, unused_i):
        """Read an @-at sentinel."""
        at = self
        at.readLastDocLine("@")
        at.popSentinelStack(at.endAt)
        at.inCode = True

    def readEndDoc(self, unused_s, unused_i):
        """Read an @-doc sentinel."""
        at = self
        at.readLastDocLine("@doc")
        at.popSentinelStack(at.endDoc)
        at.inCode = True
    #@+node:ekr.20041005105605.93: *7* at.readEndLeo
    def readEndLeo(self, unused_s, unused_i):
        """Read an @-leo sentinel."""
        at = self
        # Ignore everything after @-leo.
        # Such lines were presumably written by @last.
        while 1:
            s = at.readLine()
            if not s: break
            at.lastLines.append(s) # Capture all trailing lines, even if empty.
        at.done = True
    #@+node:ekr.20041005105605.94: *7* at.readEndMiddle
    def readEndMiddle(self, s, i):
        """Read an @-middle sentinel."""
        at = self
        at.readEndNode(s, i, middle=True)
    #@+node:ekr.20041005105605.95: *7* at.readEndNode (old sentinels only)
    def readEndNode(self, unused_s, unused_i, middle=False):
        """
        Handle old-style @-node sentinels.
        In the new scheme, only the post-pass terminates nodes.
        """
        at = self
        assert not at.readVersion5, 'not at.readVersion5'
            # Must not be called for new sentinels.
        at.raw = False # End raw mode.
        at.terminateNode(middle=middle, postPass=False)
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
    #@+node:ekr.20041005105605.98: *7* at.readEndOthers
    def readEndOthers(self, unused_s, unused_i):
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
            at.changeLevel(oldLevel, newLevel)
    #@+node:ekr.20100625140824.5968: *7* at.readEndRef
    def readEndRef(self, unused_s, unused_i):
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
            at.changeLevel(oldLevel, newLevel)
    #@+node:ekr.20041005105605.99: *7* at.readLastDocLine (old sentinels only)
    def readLastDocLine(self, tag):
        """Read the @c line that terminates the doc part.
        tag is @doc or @.

        Not used when reading new sentinels.
        """
        at = self
        end = at.endSentinelComment
        start = at.startSentinelComment
        s = ''.join(at.docOut)
        # Remove the @doc or @space.  We'll add it back at the end.
        if g.match(s, 0, tag):
            s = s[len(tag):]
        else:
            at.readError("Missing start of doc part")
            return
        # Bug fix: Append any whitespace following the tag to tag.
        while s and s[0] in (' ', '\t'):
            tag = tag + s[0]; s = s[1:]
        if end:
            # Remove leading newline.
            if s[0] == '\n': s = s[1:]
            # Remove opening block delim.
            if g.match(s, 0, start):
                s = s[len(start):]
            else:
                at.readError("Missing open block comment")
                g.trace('tag', repr(tag), 'start', repr(start), 's', repr(s))
                return
            # Remove trailing newline.
            if s[-1] == '\n': s = s[: -1]
            # Remove closing block delim.
            if s[-len(end):] == end:
                s = s[: -len(end)]
            else:
                at.readError("Missing close block comment")
                g.trace(s)
                g.trace(end)
                g.trace(start)
                return
        at.appendToOut(tag + s)
        at.docOut = []
    #@+node:ekr.20041005105605.100: *6* Unpaired sentinels
    # Ooops: shadow files are cleared if there is a read error!!
    #@+node:ekr.20041005105605.101: *7* at.ignoreOldSentinel
    def ignoreOldSentinel(self, s, unused_i):
        """Ignore an 3.x sentinel."""
        g.warning("ignoring 3.x sentinel:", s.strip())
    #@+node:ekr.20041005105605.102: *7* at.readAfterRef
    def readAfterRef(self, s, i):
        """Read an @afterref sentinel."""
        at = self
        trace = False and not g.unitTesting
        assert g.match(s, i, "afterref"), 'missing afterref'
        # Append the next line to the text.
        s = at.readLine()
        v = at.lastRefNode
        hasList = hasattr(v, 'tempBodyList')
        # g.trace('hasList',hasList,'v',v and v.h)
        if at.readVersion5:
            if hasList and at.v.tempBodyList:
                # Remove the trailing newline.
                s2 = at.v.tempBodyList[-1]
                if s2.endswith('\n'): s2 = s2[: -1]
                at.v.tempBodyList[-1] = s2
                if trace: g.trace('v: %30s %s' % (at.v.h, repr(s2 + s)))
        at.appendToOut(s)
    #@+node:ekr.20041005105605.103: *7* at.readClone
    def readClone(self, s, i):
        at = self; tag = "clone"
        assert g.match(s, i, tag), 'missing clone sentinel'
        # Skip the tag and whitespace.
        i = g.skip_ws(s, i + len(tag))
        # Get the clone count.
        junk, val = g.skip_long(s, i)
        if val is None:
            at.readError("Invalid count in @clone sentinel")
        else:
            at.cloneSibCount = val
    #@+node:ekr.20041005105605.104: *7* at.readComment
    def readComment(self, s, i):
        """Read an @comment sentinel."""
        assert g.match(s, i, "comment"), 'missing comment sentinel'
        # Just ignore the comment line!
    #@+node:ekr.20041005105605.105: *7* at.readDelims
    def readDelims(self, s, i):
        """Read an @delims sentinel."""
        at = self
        assert g.match(s, i - 1, "@delims"), 'missing @delims'
        # Skip the keyword and whitespace.
        i0 = i - 1
        i = g.skip_ws(s, i - 1 + 7)
        # Get the first delim.
        j = i
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
            i += 1
        if j < i:
            at.startSentinelComment = s[j: i]
            # Get the optional second delim.
            j = i = g.skip_ws(s, i)
            while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
                i += 1
            end = s[j: i] if j < i else ""
            i2 = g.skip_ws(s, i)
            if end == at.endSentinelComment and (i2 >= len(s) or g.is_nl(s, i2)):
                at.endSentinelComment = "" # Not really two params.
                line = s[i0: j]
                line = line.rstrip()
                at.appendToOut(line + '\n')
            else:
                at.endSentinelComment = end
                line = s[i0: i]
                line = line.rstrip()
                at.appendToOut(line + '\n')
        else:
            at.readError("Bad @delims")
            at.appendToOut("@delims")
    #@+node:ekr.20041005105605.106: *7* at.readDirective (@@)
    def readDirective(self, s, i):
        """Read an @@sentinel."""
        at = self
        assert g.match(s, i, "@"), 'missing @@ sentinel'
            # The first '@' has already been eaten.
        if g.match_word(s, i, "@raw"):
            at.raw = True
        elif g.match_word(s, i, "@end_raw"):
            at.raw = False
        e = at.endSentinelComment
        s2 = s[i:]
        if e:
            k = s.rfind(e, i)
            if k != -1:
                s2 = s[i: k] + '\n'
        start = at.startSentinelComment
        if start and start[-1] == '@':
            s2 = s2.replace('@@', '@')
        # An @c or @code ends the doc part when using new sentinels.
        if (
            at.readVersion5 and s2.startswith('@c') and
            (g.match_word(s2, 0, '@c') or g.match_word(s2, 0, '@code'))
        ):
            if at.docOut:
                s = ''.join(at.docOut)
                s = at.massageAtDocPart(s)
                at.appendToOut(s)
                at.docOut = []
            at.inCode = True # End the doc part.
        at.appendToOut(s2)
    #@+node:ekr.20041005105605.109: *7* at.readNl
    def readNl(self, s, i):
        """Handle an @nonl sentinel."""
        at = self
        assert g.match(s, i, "nl"), 'missing nl sentinel'
        if at.inCode:
            at.appendToOut('\n')
        else:
            at.docOut.append('\n')
    #@+node:ekr.20041005105605.110: *7* at.readNonl
    def readNonl(self, s, i):
        """Handle an @nonl sentinel."""
        at = self
        assert g.match(s, i, "nonl"), 'missing nonl sentinel'
        if at.inCode:
            s = ''.join(at.out)
            # 2010/01/07: protect against a mostly-harmless read error.
            if s:
                if s[-1] == '\n':
                    at.out = [s[: -1]] # Do not use at.appendToOut here!
                else:
                    g.trace("out:", s)
                    at.readError("unexpected @nonl directive in code part")
        else:
            s = ''.join(at.pending)
            if s:
                if s[-1] == '\n':
                    at.pending = [s[: -1]]
                else:
                    g.trace("docOut:", s)
                    at.readError("unexpected @nonl directive in pending doc part")
            else:
                s = ''.join(at.docOut)
                if s and s[-1] == '\n':
                    at.docOut = [s[: -1]]
                else:
                    g.trace("docOut:", s)
                    at.readError("unexpected @nonl directive in doc part")
    #@+node:ekr.20041005105605.112: *7* at.readVerbatim
    def readVerbatim(self, s, i):
        """Read an @verbatim sentinel."""
        at = self
        assert g.match(s, i, "verbatim"), 'missing verbatim sentinel'
        # Append the next line to the text.
        s = at.readLine()
        i = at.skipIndent(s, 0, at.indent)
        # Do **not** insert the verbatim line itself!
            # at.appendToOut("@verbatim\n")
        at.appendToOut(s[i:])
    #@+node:ekr.20041005105605.113: *6* at.badEndSentinel, popSentinelStack
    def badEndSentinel(self, expectedKind):
        """Handle a mismatched ending sentinel."""
        at = self
        assert at.endSentinelStack, 'empty sentinel stack'
        s = "(badEndSentinel) Ignoring %s sentinel.  Expecting %s" % (
            at.sentinelName(at.endSentinelStack[-1]),
            at.sentinelName(expectedKind))
        at.readError(s)

    def popSentinelStack(self, expectedKind):
        """Pop an entry from endSentinelStack and check it."""
        at = self
        if at.endSentinelStack and at.endSentinelStack[-1] == expectedKind:
            at.endSentinelStack.pop()
        else:
            if 1: g.trace('%s\n%s' % (
                [at.sentinelName(z) for z in at.endSentinelStack],
                g.callers(4)))
            at.badEndSentinel(expectedKind)
    #@+node:ekr.20130121102851.10249: *6* at.changeLevel
    def changeLevel(self, oldLevel, newLevel):
        '''
        Update data structures when changing node level.

        The key invariant: on exit, the top of at.thinNodeStack is the new parent node.
        '''
        at = self
        # Crucial: we must be using new-style sentinels.
        assert at.readVersion5, 'at.readVersion5'
        assert at.thinFile, 'at.thinFile'
        assert not at.importing, 'not at.importing'
            # We can be importing when using the import-file command.
        if newLevel > oldLevel:
            # A possible fix for bug #289.
            if newLevel != oldLevel + 1:
                # g.trace('expected level %s got level %s' % (
                #    oldLevel + 1, newLevel), g.callers())
                newLevel = oldLevel + 1
            # assert newLevel == oldLevel + 1, 'newLevel == oldLevel + 1'
        else:
            while oldLevel > newLevel:
                oldLevel -= 1
                at.thinChildIndexStack.pop()
                at.indentStack.pop()
                at.thinNodeStack.pop()
                at.vStack.pop()
            assert oldLevel == newLevel, 'oldLevel: %s newLevel: %s' % (oldLevel, newLevel)
            assert len(at.thinNodeStack) == newLevel, 'len(at.thinNodeStack) == newLevel'
        # The last node is the node at the top of the stack.
        # This node will be the parent of any newly created node.
        at.lastThinNode = at.thinNodeStack[-1]
    #@+node:ekr.20110523201030.18288: *6* at.massageAtDocPart (new)
    def massageAtDocPart(self, s):
        '''Compute the final @doc part when block comments are used.'''
        at = self
        if at.endSentinelComment:
            ok1 = s.startswith(at.startSentinelComment + '\n')
            ok2 = s.endswith(at.endSentinelComment + '\n')
            if ok1 and ok2:
                n1 = len(at.startSentinelComment)
                n2 = len(at.endSentinelComment)
                s = s[n1 + 1: -(n2 + 1)]
            else:
                at.error('invalid @doc part...\n%s' % repr(s))
        # g.trace(repr(s))
        return s
    #@+node:ekr.20041005105605.114: *5* at.sentinelKind4 & helper (read logic)
    def sentinelKind4(self, s):
        """Return the kind of sentinel at s."""
        trace = False and not g.unitTesting
        verbose = False
        at = self
        val = at.sentinelKind4_helper(s)
        if trace and (verbose or val != at.noSentinel):
            g.trace('%-20s %s' % (
                at.sentinelName(val), s.rstrip()))
        return val
    #@+node:ekr.20100518083515.5896: *6* sentinelKind4_helper
    def sentinelKind4_helper(self, s):
        at = self
        i = g.skip_ws(s, 0)
        if g.match(s, i, at.startSentinelComment):
            i += len(at.startSentinelComment)
        else:
            return at.noSentinel
        # Locally undo cweb hack here
        start = at.startSentinelComment
        if start and start[-1] == '@':
            s = s[: i] + s[i:].replace('@@', '@')
        # New sentinels.
        if g.match(s, i, "@+"):
            if g.match(s, i + 2, "others"):
                return at.startOthers
            elif g.match(s, i + 2, "<<"):
                return at.startRef
            else:
                j = g.skip_ws(s, i + 2)
                if g.match(s, j, "<<"):
                    return at.startRef
        elif g.match(s, i, "@-"):
            if g.match(s, i + 2, "others"):
                return at.endOthers
            elif g.match(s, i + 2, "<<"):
                return at.endRef
            else:
                j = g.skip_ws(s, i + 2)
                if g.match(s, j, "<<"):
                    return at.endRef
        # Old sentinels.
        elif g.match(s, i, "@"):
            j = g.skip_ws(s, i + 1)
            if j > i + 1:
                if g.match(s, j, "@+others"):
                    return at.startOthers
                elif g.match(s, j, "@-others"):
                    return at.endOthers
                elif g.match(s, j, "<<"):
                    return at.startRef
                else:
                    # No other sentinels allow whitespace following the '@'
                    return at.noSentinel
        # Do not skip whitespace here!
        if g.match(s, i, "@<<"): return at.startRef
        if g.match(s, i, "@@"): return at.startDirective
        if not g.match(s, i, '@'): return at.noSentinel
        j = i # start of lookup
        i += 1 # skip the at sign.
        if g.match(s, i, '+') or g.match(s, i, '-'):
            i += 1
        i = g.skip_c_id(s, i)
        key = s[j: i]
        if key and key in at.sentinelDict:
            return at.sentinelDict[key]
        else:
            return at.noSentinel
    #@+node:ekr.20041005105605.115: *5* at.skipSentinelStart4
    def skipSentinelStart4(self, s, i):
        """Skip the start of a sentinel."""
        start = self.startSentinelComment
        assert start, 'skipSentinelStart4 1'
        i = g.skip_ws(s, i)
        assert g.match(s, i, start), 'skipSentinelStart4 2'
        i += len(start)
        # 7/8/02: Support for REM hack
        i = g.skip_ws(s, i)
        assert i < len(s) and s[i] == '@', 'skipSentinelStart4 3'
        return i + 1
    #@+node:ekr.20041005105605.116: *4* at.Reading utils...
    #@+node:ekr.20100625092449.5963: *5* at.appendToOut
    def appendToOut(self, s):
        '''Append s to at.out (old sentinels) or
           at.v.tempBodyList (new sentinels).'''
        at = self
        trace = False and at.readVersion5 and not g.unitTesting
        if at.readVersion5:
            if not at.v: at.v = at.root.v
            if hasattr(at.v, "tempBodyList"):
                at.v.tempBodyList.append(s)
            else:
                at.v.tempBodyList = [s]
        else:
            at.out.append(s)
        if trace:
            g.trace('%4s %25s %s' % (
                'code' if at.inCode else 'doc', at.v.h, repr(s)))
    #@+node:ekr.20150310141151.5: *5* at.body inited accessors
    def bodyIsInited(self, v):
        '''Return True if v.b has been inited.'''
        c = self.c
        return hasattr(c, 'bodyInitedDict') and v.gnx in c.bodyInitedDict

    def bodySetInited(self, v):
        '''Indicate that v.b has been inited.'''
        c = self.c
        if not hasattr(c, 'bodyInitedDict'):
            c.bodyInitedDict = {}
        c.bodyInitedDict[v.gnx] = True

    def clearAllBodyInited(self):
        '''Clear all v.b inited bits.'''
        c = self.c
        if hasattr(c, 'bodyInitedDict'):
            delattr(c, 'bodyInitedDict')
    #@+node:ekr.20041005105605.119: *5* at.createImportedNode
    def createImportedNode(self, root, headline):
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
    #@+node:ekr.20041005105605.120: *5* at.parseLeoSentinel
    if 1: # Experimental. All unit tests pass.

        def parseLeoSentinel(self, s):
            '''
            Parse the sentinel line s.
            If the sentinel is valid, set at.encoding, at.readVersion, at.readVersion5.
            '''
            trace = False and not g.unitTesting
            at, c = self, self.c
            # Set defaults.
            encoding = c.config.default_derived_file_encoding
            readVersion, readVersion5 = None, None
            new_df, start, end, isThin = False, '', '', False
            # Example: \*@+leo-ver=5-thin-encoding=utf-8,.*/
            pattern = re.compile(r'(.+)@\+leo(-ver=([0123456789]+))?(-thin)?(-encoding=(.*)(\.))?(.*)')
                # The old code weirdly allowed '.' in version numbers.
            m = pattern.match(s)
            valid = bool(m)
            if valid:
                # set start delim: whitespace before @+leo is significant.
                # group(1): \*
                start = m.group(1)
                valid = bool(start)
            if valid:
                # set new_df
                # group(2): -ver=5
                new_df = bool(m.group(2))
                if new_df:
                    # Set the version number.
                    # group(3): 5
                    if m.group(3):
                        readVersion = m.group(3)
                        readVersion5 = readVersion >= '5'
                    else:
                        valid = False
            if valid:
                # set isThin
                # group(4): -thin
                isThin = bool(m.group(4))
            if valid and m.group(5):
                # set encoding.
                # group(5): -encoding=utf-8,.
                # group(6): utf-8,
                # group(7): .
                encoding = m.group(6)
                if encoding and encoding.endswith(','):
                    # Leo 4.2 or after.
                    encoding = encoding[:-1]
                if not g.isValidEncoding(encoding):
                    g.es_print("bad encoding in derived file:", encoding)
                    valid = False
            if valid:
                # set end.
                # group(8): */
                end = m.group(8)
            if valid:
                at.encoding = encoding
                at.readVersion = readVersion
                at.readVersion5 = readVersion5
            if trace:
                g.trace(s)
                g.trace('valid: %s, isThin: %s, encoding: %r, start: %r, end: %r' % (
                    valid, isThin, encoding, start, end))
            return valid, new_df, start, end, isThin

    else:

        def parseLeoSentinel(self, s):
            trace = False and not g.unitTesting
            at = self; c = at.c
            new_df = False; valid = True; n = len(s)
            start = ''; end = ''; isThinDerivedFile = False
            encoding_tag = "-encoding="
            version_tag = "-ver="
            tag = "@+leo"
            thin_tag = "-thin"
            #@+<< set the opening comment delim >>
            #@+node:ekr.20041005105605.121: *6* << set the opening comment delim >>
            # s contains the tag
            i = j = g.skip_ws(s, 0)
            # The opening comment delim is the initial non-tag
            while i < n and not g.match(s, i, tag) and not g.is_nl(s, i):
                i += 1
            if j < i:
                start = s[j: i]
            else:
                if trace: g.trace('no opening delim')
                valid = False
            #@-<< set the opening comment delim >>
            #@+<< make sure we have @+leo >>
            #@+node:ekr.20041005105605.122: *6* << make sure we have @+leo >>
            #@+at
            # REM hack: leading whitespace is significant before the
            # @+leo. We do this so that sentinelKind need not skip
            # whitespace following self.startSentinelComment. This is
            # correct: we want to be as restrictive as possible about what
            # is recognized as a sentinel. This minimizes false matches.
            #@@c
            if 0: # Make leading whitespace significant.
                i = g.skip_ws(s, i)
            if g.match(s, i, tag):
                i += len(tag)
            else:
                if trace: g.trace('no @+leo')
                valid = False
            #@-<< make sure we have @+leo >>
            #@+<< read optional version param >>
            #@+node:ekr.20041005105605.123: *6* << read optional version param >>
            new_df = g.match(s, i, version_tag)
            if trace and not new_df:
                g.trace('not new_df', repr(s[0: 100]))
            if new_df:
                # Pre Leo 4.4.1: Skip to the next minus sign or end-of-line.
                # Leo 4.4.1 +:   Skip to next minus sign, end-of-line,
                #                or non numeric character.
                # This is required to handle trailing comment delims properly.
                i += len(version_tag)
                j = i
                while i < len(s) and (s[i] == '.' or s[i].isdigit()):
                    i += 1
                at.readVersion = s[j: i] # 2010/05/18.
                at.readVersion5 = at.readVersion >= '5'
                if j < i:
                    pass
                else:
                    if trace: g.trace('no version')
                    valid = False
            #@-<< read optional version param >>
            #@+<< read optional thin param >>
            #@+node:ekr.20041005105605.124: *6* << read optional thin param >>
            if g.match(s, i, thin_tag):
                i += len(tag)
                isThinDerivedFile = True
            #@-<< read optional thin param >>
            #@+<< read optional encoding param >>
            #@+node:ekr.20041005105605.125: *6* << read optional encoding param >>
            # Set the default encoding
            at.encoding = c.config.default_derived_file_encoding
            if g.match(s, i, encoding_tag):
                # Read optional encoding param, e.g., -encoding=utf-8,
                i += len(encoding_tag)
                # Skip to the next end of the field.
                j = s.find(",.", i)
                if j > -1:
                    # The encoding field was written by 4.2 or after:
                    encoding = s[i: j]
                    i = j + 2 # 6/8/04, 1/11/05 (was i = j + 1)
                else:
                    # The encoding field was written before 4.2.
                    j = s.find('.', i)
                    if j > -1:
                        encoding = s[i: j]
                        i = j + 1 # 6/8/04
                    else:
                        encoding = None
                # g.trace("encoding:",encoding)
                if encoding:
                    if g.isValidEncoding(encoding):
                        at.encoding = encoding
                    else:
                        g.es_print("bad encoding in derived file:", encoding)
                else:
                    if trace: g.trace('no encoding')
                    valid = False
            #@-<< read optional encoding param >>
            #@+<< set the closing comment delim >>
            #@+node:ekr.20041005105605.126: *6* << set the closing comment delim >>
            # The closing comment delim is the trailing non-whitespace.
            i = j = g.skip_ws(s, i)
            while i < n and not g.is_ws(s[i]) and not g.is_nl(s, i):
                i += 1
            end = s[j: i]
            #@-<< set the closing comment delim >>
            if trace:
                g.trace(s)
                g.trace('valid', valid, 'isThin', isThinDerivedFile, 'encoding', at.encoding)
            return valid, new_df, start, end, isThinDerivedFile
    #@+node:ekr.20041005105605.127: *5* at.readError
    def readError(self, message):
        # This is useful now that we don't print the actual messages.
        if self.errors == 0:
            self.printError("----- read error. line: %s, file: %s" % (
                self.lineNumber, self.targetFileName,))
        # g.trace(self.root,g.callers())
        self.error(message)
        # Delete all of root's tree.
        self.root.v.children = []
        self.root.setDirty()
            # 2010/10/22: the dirty bit gets cleared later, though.
        self.root.setOrphan()
    #@+node:ekr.20041005105605.128: *5* at.readLine
    def readLine(self):
        """
        Read one line from file using the present encoding.
        Returns at.read_lines[at.read_i++]
        """
        trace = False and not g.unitTesting
        at = self
        if at.read_i < len(at.read_lines):
            s = at.read_lines[at.read_i]
            at.read_i += 1
            if trace: g.trace(at.read_i - 1, repr(s))
            return s
        else:
            return '' # Not an error.
    #@+node:ekr.20041005105605.129: *5* at.scanHeader
    def scanHeader(self, fileName, giveErrors=True):
        """
        Scan the @+leo sentinel.

        Sets self.encoding, and self.start/endSentinelComment.

        Returns (firstLines,new_df,isThinDerivedFile) where:
        firstLines        contains all @first lines,
        new_df            is True if we are reading a new-format derived file.
        isThinDerivedFile is True if the file is an @thin file.
        """
        at = self
        new_df, isThinDerivedFile = False, False
        firstLines = [] # The lines before @+leo.
        s = self.scanFirstLines(firstLines)
        valid = len(s) > 0
        if valid:
            valid, new_df, start, end, isThinDerivedFile = at.parseLeoSentinel(s)
        if valid:
            at.startSentinelComment = start
            at.endSentinelComment = end
            # g.trace('start',repr(start),'end',repr(end))
        elif giveErrors:
            at.error("No @+leo sentinel in: %s" % fileName)
            g.trace(g.callers())
        # g.trace("start,end",repr(at.startSentinelComment),repr(at.endSentinelComment))
        # g.trace(fileName,firstLines)
        return firstLines, new_df, isThinDerivedFile
    #@+node:ekr.20041005105605.130: *6* at.scanFirstLines
    def scanFirstLines(self, firstLines):
        '''
        Append all lines before the @+leo line to firstLines.

        Empty lines are ignored because empty @first directives are
        ignored.

        We can not call sentinelKind here because that depends on the comment
        delimiters we set here.
        '''
        at = self
        s = at.readLine()
        while s and s.find("@+leo") == -1:
            firstLines.append(s)
            s = at.readLine()
        return s
    #@+node:ekr.20050103163224: *5* at.scanHeaderForThin (import code)
    def scanHeaderForThin(self, fileName):
        '''
        Return true if the derived file is a thin file.

        This is a kludgy method used only by the import code.'''
        at = self
        at.readFileToUnicode(fileName)
            # inits at.readLine.
        junk, junk, isThin = at.scanHeader(None)
            # scanHeader uses at.readline instead of its args.
            # scanHeader also sets at.encoding.
        return isThin
    #@+node:ekr.20041005105605.131: *5* at.skipIndent
    # Skip past whitespace equivalent to width spaces.

    def skipIndent(self, s, i, width):
        ws = 0; n = len(s)
        while i < n and ws < width:
            if s[i] == '\t': ws += (abs(self.tab_width) - (ws % abs(self.tab_width)))
            elif s[i] == ' ': ws += 1
            else: break
            i += 1
        return i
    #@+node:ekr.20041005105605.132: *3* at.Writing
    #@+node:ekr.20041005105605.133: *4* Writing (top level)
    #@+node:ekr.20041005105605.154: *5* at.asisWrite & helper
    def asisWrite(self, root, toString=False):
        at = self; c = at.c
        c.endEditing() # Capture the current headline.
        c.init_error_dialogs()
        try:
            # Note: @asis always writes all nodes,
            # so there can be no orphan or ignored nodes.
            targetFileName = root.atAsisFileNodeName()
            at.initWriteIvars(root, targetFileName, toString=toString)
            # "look ahead" computation of eventual fileName.
            eventualFileName = c.os_path_finalize_join(
                at.default_directory, at.targetFileName)
            if at.shouldPromptForDangerousWrite(eventualFileName, root):
                # Prompt if writing a new @asis node would overwrite the existing file.
                ok = self.promptForDangerousWrite(eventualFileName, kind='@asis')
                if ok:
                    # Fix bug 889175: Remember the full fileName.
                    at.rememberReadPath(eventualFileName, root)
                else:
                    g.es("not written:", eventualFileName)
                    return
            if at.errors: return
            if not at.openFileForWriting(root, targetFileName, toString):
                # openFileForWriting calls root.setDirty() if there are errors.
                return
            for p in root.self_and_subtree():
                at.writeAsisNode(p)
            at.closeWriteFile()
            at.replaceTargetFileIfDifferent(root) # Sets/clears dirty and orphan bits.
        except Exception:
            at.writeException(root) # Sets dirty and orphan bits.

    silentWrite = asisWrite # Compatibility with old scripts.
    #@+node:ekr.20170331141933.1: *6* at.writeAsisNode
    def writeAsisNode(self, p):
        '''Write the p's node to an @asis file.'''
        at = self
        # Write the headline only if it starts with '@@'.
        s = p.h
        if g.match(s, 0, "@@"):
            s = s[2:]
            if s:
                at.outputFile.write(s)
        # Write the body.
        s = p.b
        if s:
            s = g.toEncodedString(s, at.encoding, reportErrors=True)
            at.outputStringWithLineEndings(s)

    #@+node:ekr.20041005105605.142: *5* at.openFileForWriting & helper
    def openFileForWriting(self, root, fileName, toString):
        trace = False and not g.unitTesting
        at = self
        at.outputFile = None
        if toString:
            at.shortFileName = g.shortFileName(fileName)
            at.outputFileName = "<string: %s>" % at.shortFileName
            at.outputFile = g.FileLikeObject()
        else:
            ok = at.openFileForWritingHelper(fileName)
            # New in Leo 4.4.8: set dirty bit if there are errors.
            if not ok:
                at.outputFile = None
        if trace:
            g.trace('root', repr(root and root.h), 'outputFile', repr(at.outputFile))
        # New in 4.3 b2: root may be none when writing from a string.
        if root:
            if at.outputFile:
                root.clearOrphan()
            else:
                root.setOrphan()
                root.setDirty()
        return at.outputFile is not None
    #@+node:ekr.20041005105605.143: *6* at.openFileForWritingHelper & helper
    def openFileForWritingHelper(self, fileName):
        '''Open the file and return True if all went well.'''
        at = self; c = at.c
        try:
            at.shortFileName = g.shortFileName(fileName)
            at.targetFileName = c.os_path_finalize_join(
                at.default_directory, fileName)
            path = g.os_path_dirname(at.targetFileName)
            if not path or not g.os_path_exists(path):
                if path:
                    path = g.makeAllNonExistentDirectories(path, c=c)
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
                if not os.access(at.targetFileName, os.W_OK):
                    at.writeError("can not open: read only: " + at.targetFileName)
                    return False
            except AttributeError:
                pass # os.access() may not exist on all platforms.
        try:
            old_output_fn = at.outputFileName
                # Fix bug: https://bugs.launchpad.net/leo-editor/+bug/1260547
            at.outputFileName = None
            kind, at.outputFile = self.openForWrite(at.outputFileName, 'wb')
            if not at.outputFile:
                kind = 'did not overwrite' if kind == 'check' else 'can not create'
                at.writeError("%s %s" % (kind, old_output_fn))
                return False
        except Exception:
            at.exception("exception creating:" + old_output_fn)
            return False
        return True
    #@+node:bwmulder.20050101094804: *7* at.openForWrite
    def openForWrite(self, filename, wb='wb'):
        '''Open a file for writes, handling shadow files.'''
        trace = False and not g.unitTesting
        at = self; c = at.c; x = c.shadowController
        try:
            # 2011/10/11: in "quick edit/save" mode the .leo file may not have a name.
            if c.fileName():
                shadow_filename = x.shadowPathName(filename)
                self.writing_to_shadow_directory = os.path.exists(shadow_filename)
                open_file_name = shadow_filename if self.writing_to_shadow_directory else filename
                self.shadow_filename = shadow_filename if self.writing_to_shadow_directory else None
            else:
                self.writing_to_shadow_directory = False
                open_file_name = filename
            if self.writing_to_shadow_directory:
                if trace: g.trace(filename, shadow_filename)
                x.message('writing %s' % shadow_filename)
                f = g.FileLikeObject()
                return 'shadow', f
            else:
                ok = c.checkFileTimeStamp(at.targetFileName)
                if ok:
                    f = g.FileLikeObject()
                else:
                    f = None
                # return 'check',ok and open(open_file_name,wb)
                return 'check', f
        except IOError:
            if not g.app.unitTesting:
                g.error('openForWrite: exception opening file: %s' % (open_file_name))
                g.es_exception()
            return 'error', None
    #@+node:ekr.20041005105605.144: *5* at.write & helpers
    def write(self,
        root,
        kind='@unknown', # Should not happen.
        nosentinels=False,
        toString=False,
    ):
        """Write a 4.x derived file.
        root is the position of an @<file> node"""
        trace = False and not g.unitTesting
        at = self; c = at.c
        c.endEditing() # Capture the current headline.
        at.setTargetFileName(root, toString)
        at.initWriteIvars(
            root,
            at.targetFileName,
            nosentinels=nosentinels,
            toString=toString,
        )
        # "look ahead" computation of eventual fileName.
        eventualFileName = c.os_path_finalize_join(
            at.default_directory, at.targetFileName)
        if trace:
            g.trace('default_dir',
                g.os_path_exists(at.default_directory),
                at.default_directory)
            g.trace('eventual_fn', eventualFileName)
        if not toString:
            if at.shouldPromptForDangerousWrite(eventualFileName, root):
                # Prompt if writing a new @file or @thin node would
                # overwrite an existing file.
                ok = self.promptForDangerousWrite(eventualFileName, kind)
                if ok:
                    at.rememberReadPath(eventualFileName, root)
                else:
                    g.es("not written:", eventualFileName)
                    at.setDirtyOrphanBits(root)
                    return
        if not at.openFileForWriting(root, at.targetFileName, toString):
            # openFileForWriting calls root.setDirty() if there are errors.
            if trace: g.trace('open failed', eventualFileName)
            return
        try:
            at.writeOpenFile(root, nosentinels=nosentinels, toString=toString)
            assert root == at.root, 'write'
            if toString:
                at.closeWriteFile()
                    # sets at.stringOutput and at.outputContents
                # Major bug: failure to clear this wipes out headlines!
                # Minor bug: sometimes this causes slight problems...
                if hasattr(self.root.v, 'tnodeList'):
                    delattr(self.root.v, 'tnodeList')
                root.v._p_changed = True
            else:
                at.closeWriteFile()
                if at.errors > 0 or root.isOrphan():
                    at.setDirtyOrphanBits(root)
                    g.es("not written:", g.shortFileName(at.targetFileName))
                else:
                    # Fix bug 889175: Remember the full fileName.
                    at.rememberReadPath(eventualFileName, root)
                    at.replaceTargetFileIfDifferent(root)
                        # Sets/clears dirty and orphan bits.
                    # Leo 5.6: update the cache *here*, not just when reading.
                    fileKey = c.cacher.fileKey(eventualFileName, at.outputContents)
                    if trace: g.trace(g.shortFileName(eventualFileName), fileKey)
                    c.cacher.writeFile(at.root, fileKey)
        except Exception:
            if hasattr(self.root.v, 'tnodeList'):
                delattr(self.root.v, 'tnodeList')
            if toString:
                at.exception("exception preprocessing script")
                root.v._p_changed = True
            else:
                at.writeException() # Sets dirty and orphan bits.
    #@+node:ekr.20140630081820.16722: *6* at.setTargetFileName
    def setTargetFileName(self, root, toString):
        '''Set the target file name for at.write.'''
        at = self
        if toString:
            at.targetFileName = "<string-file>"
        else:
            at.targetFileName = root.anyAtFileNodeName()
    #@+node:ekr.20140630081820.16723: *6* at.setDirtyOrphanBits
    def setDirtyOrphanBits(self, root):
        '''
        Setting the orphan and dirty flags tells Leo to write the tree.
        However, the dirty bits get cleared if we are called from the save command.
        '''
        at = self
        root.setOrphan()
        root.setDirty()
        # Delete the temp file.
        if at.outputFileName:
            self.remove(at.outputFileName)
    #@+node:ekr.20041005105605.147: *5* at.writeAll & helpers
    def writeAll(self,
        writeAtFileNodesFlag=False,
        writeDirtyAtFileNodesFlag=False,
        toString=False
    ):
        """Write @file nodes in all or part of the outline"""
        trace = False and not g.unitTesting
        at = self; c = at.c
        if trace: scanAtPathDirectivesCount = c.scanAtPathDirectivesCount
        writtenFiles = [] # Files that might be written again.
        at.sameFiles = 0
        force = writeAtFileNodesFlag
        # This is the *only* place where these are set.
        # promptForDangerousWrite sets cancelFlag only if canCancelFlag is True.
        at.canCancelFlag = True
        at.cancelFlag = False
        at.yesToAll = False
        if writeAtFileNodesFlag:
            # The Write @<file> Nodes command.
            # Write all nodes in the selected tree.
            root = c.p
            p = c.p
            after = p.nodeAfterTree()
        else:
            # Write dirty nodes in the entire outline.
            root = c.rootPosition()
            p = c.rootPosition()
            after = None
        at.clearAllOrphanBits(p)
        # Leo 5.6: write files only once.
        seen = set()
        while p and p != after:
            if p.isAtIgnoreNode() and not p.isAtAsisFileNode():
                if p.isAnyAtFileNode():
                    c.ignored_at_file_nodes.append(p.h)
                # Note: @ignore not honored in @asis nodes.
                p.moveToNodeAfterTree() # 2011/10/08: Honor @ignore!
            elif p.isAnyAtFileNode():
                data = p.v, g.fullPath(c, p)
                if data not in seen:
                    seen.add(data)
                    try:
                        self.writeAllHelper(p, root, force, toString, writeAtFileNodesFlag, writtenFiles)
                    except Exception:
                        # Fix bug 1260415: https://bugs.launchpad.net/leo-editor/+bug/1260415
                        # Give a more urgent, more specific, more helpful message.
                        g.es_exception()
                        g.es('Internal error writing: %s' % (p.h), color='red')
                        g.es('Please report this error to:', color='blue')
                        g.es('https://groups.google.com/forum/#!forum/leo-editor', color='blue')
                        g.es('Warning: changes to this file will be lost', color='red')
                        g.es('unless you can save the file successfully.', color='red')
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        # Make *sure* these flags are cleared for other commands.
        at.canCancelFlag = False
        at.cancelFlag = False
        at.yesToAll = False
        # say the command is finished.
        if not g.unitTesting:
            if writeAtFileNodesFlag or writeDirtyAtFileNodesFlag:
                if writtenFiles:
                    report = c.config.getBool('report_unchanged_files', default=True)
                    if report:
                        g.es("finished")
                    elif at.sameFiles:
                        g.es('finished. %s unchanged files' % at.sameFiles)
                elif writeAtFileNodesFlag:
                    g.warning("no @<file> nodes in the selected tree")
                    # g.es("to write an unchanged @auto node,\nselect it directly.")
                else:
                    g.es("no dirty @<file> nodes")
        if c.isChanged():
            # Save the outline if only persistence data nodes are dirty.
            self.saveOutlineIfPossible()
        if trace: g.trace('%s calls to c.scanAtPathDirectives()' % (
            c.scanAtPathDirectivesCount - scanAtPathDirectivesCount))
    #@+node:ekr.20041005105605.148: *6* at.clearAllOrphanBits
    def clearAllOrphanBits(self, p):
        '''Clear orphan bits for all nodes *except* orphan @file nodes.'''
        # 2011/06/15: Important bug fix: retain orphan bits for @file nodes.
        for p2 in p.self_and_subtree():
            if p2.isOrphan():
                if p2.isAnyAtFileNode():
                    # g.trace('*** retaining orphan bit',p2.h)
                    pass
                else:
                    p2.clearOrphan()
    #@+node:ekr.20041005105605.149: *6* at.writeAllHelper & helper
    def writeAllHelper(self, p, root,
        force, toString, writeAtFileNodesFlag, writtenFiles
    ):
        '''
        Write one file for the at.writeAll.
        Do *not* write @auto files unless p == root.
        This prevents the write-all command from needlessly updating
        the @persistence data, thereby annoyingly changing the .leo file.
        '''
        trace = False and not g.unitTesting
        at, c = self, self.c
        at.root = root # 2014/10/21
        if not force and p.v not in writtenFiles:
            at.autoBeautify(p)
        if p.isAtIgnoreNode() and not p.isAtAsisFileNode():
            pathChanged = False
        else:
            oldPath = g.os_path_normcase(at.getPathUa(p))
            newPath = g.os_path_normcase(g.fullPath(c, p))
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
                    at.setPathUa(p, newPath) # Remember that we have changed paths.
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
                at.asisWrite(p, toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtIgnoreNode():
                pass # Handled in caller.
            elif p.isAtAutoNode():
                at.writeOneAtAutoNode(p, toString=toString, force=force)
                writtenFiles.append(p.v)
                # Do *not* clear the dirty bits the entries in @persistence tree here!
            elif p.isAtCleanNode():
                at.write(p, kind='@clean', nosentinels=True, toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtEditNode():
                at.writeOneAtEditNode(p, toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtNoSentFileNode():
                at.write(p, kind='@nosent', nosentinels=True, toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtShadowFileNode():
                at.writeOneAtShadowNode(p, toString=toString, force=force or pathChanged)
                writtenFiles.append(p.v)
            elif p.isAtThinFileNode():
                at.write(p, kind='@thin', toString=toString)
                writtenFiles.append(p.v)
            elif p.isAtFileNode():
                at.write(p, kind='@file', toString=toString)
                writtenFiles.append(p.v)
            if p.v in writtenFiles:
                # Clear the dirty bits in all descendant nodes.
                # However, persistence data may still have to be written.
                # This can not be helped.
                if trace: g.trace('clearing', p.h)
                for p2 in p.self_and_subtree():
                    p2.v.clearDirty()
    #@+node:ekr.20150602204757.1: *7* at.autoBeautify
    def autoBeautify(self, p):
        '''Auto beautify p's tree if allowed by settings and directives.'''
        c = self.c
        try:
            if not p.isDirty():
                return
            if leoBeautify.should_kill_beautify(p):
                return
            if c.config.getBool('tidy-autobeautify'):
                # g.trace(p.h)
                leoBeautify.beautifyPythonTree(event={'c': c, 'p0': p.copy()})
        except Exception:
            g.es('unexpected exception')
            g.es_exception()
    #@+node:ekr.20140727075002.18108: *6* at.saveOutlineIfPossible
    def saveOutlineIfPossible(self):
        '''Save the outline if only persistence data nodes are dirty.'''
        trace = False and not g.unitTesting
        c = self.c
        changed_positions = [p for p in c.all_unique_positions() if p.v.isDirty()]
        at_persistence = c.persistenceController and c.persistenceController.has_at_persistence_node()
        if at_persistence:
            changed_positions = [p for p in changed_positions
                if not at_persistence.isAncestorOf(p)]
        if changed_positions:
            if trace: g.trace('still changed', [p.h for p in changed_positions])
        else:
            # g.warning('auto-saving @persistence tree.')
            c.setChanged(False)
            c.redraw()
    #@+node:ekr.20070806105859: *5* at.writeAtAutoNodes & writeDirtyAtAutoNodes & helpers
    @cmd('write-at-auto-nodes')
    def writeAtAutoNodes(self, event=None):
        '''Write all @auto nodes in the selected outline.'''
        at = self; c = at.c
        c.init_error_dialogs()
        at.writeAtAutoNodesHelper(writeDirtyOnly=False)
        c.raise_error_dialogs(kind='write')

    @cmd('write-dirty-at-auto-nodes')
    def writeDirtyAtAutoNodes(self, event=None):
        '''Write all dirty @auto nodes in the selected outline.'''
        at = self; c = at.c
        c.init_error_dialogs()
        at.writeAtAutoNodesHelper(writeDirtyOnly=True)
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20070806140208: *6* at.writeAtAutoNodesHelper
    def writeAtAutoNodesHelper(self, toString=False, writeDirtyOnly=True):
        """Write @auto nodes in the selected outline"""
        at = self; c = at.c
        p = c.p; after = p.nodeAfterTree()
        found = False
        while p and p != after:
            if p.isAtAutoNode() and not p.isAtIgnoreNode() and (p.isDirty() or not writeDirtyOnly):
                ok = at.writeOneAtAutoNode(p, toString=toString, force=True)
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
    #@+node:ekr.20070806141607: *6* at.writeOneAtAutoNode & helpers
    def writeOneAtAutoNode(self,
        p,
        force=False,
        toString=False,
        trialWrite=False,
            # Set only by Importer.trial_write.
            # Suppresses call to update_before_write_foreign_file below.
    ):
        '''
        Write p, an @auto node.
        File indices *must* have already been assigned.
        '''
        trace = False and not g.unitTesting
        at, c = self, self.c
        root = p.copy()
        fileName = p.atAutoNodeName()
        if not fileName and not toString:
            if trace: g.trace('not an @auto node', p.h)
            return False
        at.default_directory = g.setDefaultDirectory(c, p, importing=True)
        fileName = c.os_path_finalize_join(at.default_directory, fileName)
        if not toString and at.shouldPromptForDangerousWrite(fileName, root):
            # Prompt if writing a new @auto node would overwrite the existing file.
            ok = self.promptForDangerousWrite(fileName, kind='@auto')
            if not ok:
                g.es("not written:", fileName)
                return False
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fileName, root)
        # This code is similar to code in at.write.
        c.endEditing() # Capture the current headline.
        at.targetFileName = "<string-file>" if toString else fileName
        at.initWriteIvars(
            root,
            at.targetFileName,
            nosentinels=True,
            toString=toString,
        )
        if c.persistenceController and not trialWrite:
            c.persistenceController.update_before_write_foreign_file(root)
        ok = at.openFileForWriting(root, fileName=fileName, toString=toString)
        if ok:
            # Dispatch the proper writer.
            junk, ext = g.os_path_splitext(fileName)
            writer = at.dispatch(ext, root)
            if trace: g.trace('writer', repr(writer), fileName)
            if writer:
                writer(root)
            elif root.isAtAutoRstNode():
                # An escape hatch: fall back to the theRst writer
                # if there is no rst writer plugin.
                if trace: g.trace('@auto-rst', fileName)
                ok2 = c.rstCommands.writeAtAutoFile(root, fileName, at.outputFile)
                if not ok2: at.errors += 1
            else:
                if trace: g.trace('at.writeOpenFile', fileName)
                # leo 5.6: allow undefined section references in all @auto files.
                ivar = 'allow_undefined_refs'
                try:
                    setattr(at, ivar, True)
                    at.writeOpenFile(root, nosentinels=True, toString=toString)
                finally:
                    if hasattr(at, ivar):
                        delattr(at, ivar)
            at.closeWriteFile()
                # Sets stringOutput if toString is True.
            if at.errors == 0:
                # g.trace('toString',toString,'force',force,'isAtAutoRst',isAtAutoRst)
                isAtAutoRst = root.isAtAutoRstNode()
                at.replaceTargetFileIfDifferent(root, ignoreBlankLines=isAtAutoRst)
                    # Sets/clears dirty and orphan bits.
            else:
                g.es("not written:", fileName)
                root.setDirty() # New in Leo 4.4.8.
                root.setOrphan() # 2010/10/22.
        elif not toString:
            root.setDirty() # Make _sure_ we try to rewrite this file.
            root.setOrphan() # 2010/10/22.
            g.es("not written:", fileName)
        return ok
    #@+node:ekr.20140728040812.17993: *7* at.dispatch & helpers
    def dispatch(self, ext, p):
        '''Return the correct writer function for p, an @auto node.'''
        at = self
        # Match @auto type before matching extension.
        return at.writer_for_at_auto(p) or at.writer_for_ext(ext)
    #@+node:ekr.20140728040812.17995: *8* at.writer_for_at_auto
    def writer_for_at_auto(self, root):
        '''A factory returning a writer function for the given kind of @auto directive.'''
        trace = False # and g.unitTesting
        at = self
        d = g.app.atAutoWritersDict
        # if trace: g.trace(g.shortFileName(root.h), '\n'+','.join(sorted(d)))
        for key in d.keys():
            aClass = d.get(key)
            if aClass and g.match_word(root.h, 0, key):

                def writer_for_at_auto_cb(root):
                    # pylint: disable=cell-var-from-loop
                    try:
                        if trace: g.trace('    INSTANTIATE:', aClass)
                        writer = aClass(at.c)
                        s = writer.write(root)
                        return s
                    except Exception:
                        g.es_exception()
                        return None

                if trace:
                    g.trace('    FOUND:', g.shortFileName(root.h), aClass)
                    g.trace(g.callers())
                return writer_for_at_auto_cb
        if trace: g.trace('   NOT FOUND:', g.shortFileName(root.h))
        return None
    #@+node:ekr.20140728040812.17997: *8* at.writer_for_ext
    def writer_for_ext(self, ext):
        '''A factory returning a writer function for the given file extension.'''
        trace = False # and not g.unitTesting
        at = self
        d = g.app.writersDispatchDict
        aClass = d.get(ext)
        # if trace: g.trace('ext', ext, 'aClass', repr(aClass), '\n'+','.join(sorted(d)))
        if aClass:

            def writer_for_ext_cb(root):
                try:
                    if trace:
                        g.trace('        FOUND:', g.shortFileName(root.h), aClass)
                        g.trace(g.callers())
                    return aClass(at.c).write(root)
                except Exception:
                    g.es_exception()
                    return None

            return writer_for_ext_cb
        else:
            if trace: g.trace('       NOT FOUND:', 'ext:', repr(ext))
            return None
    #@+node:ekr.20080711093251.3: *5* at.writeAtShadowNodes & writeDirtyAtShadowNodes & helpers
    @cmd('write-at-shadow-nodes')
    def writeAtShadowNodes(self, event=None):
        '''Write all @shadow nodes in the selected outline.'''
        at = self; c = at.c
        c.init_error_dialogs()
        val = at.writeAtShadowNodesHelper(writeDirtyOnly=False)
        c.raise_error_dialogs(kind='write')
        return val

    @cmd('write-dirty-at-shadow-nodes')
    def writeDirtyAtShadowNodes(self, event=None):
        '''Write all dirty @shadow nodes in the selected outline.'''
        at = self; c = at.c
        c.init_error_dialogs()
        val = at.writeAtShadowNodesHelper(writeDirtyOnly=True)
        c.raise_error_dialogs(kind='write')
        return val
    #@+node:ekr.20080711093251.4: *6* at.writeAtShadowNodesHelper
    def writeAtShadowNodesHelper(self, toString=False, writeDirtyOnly=True):
        """Write @shadow nodes in the selected outline"""
        at = self; c = at.c
        p = c.p; after = p.nodeAfterTree()
        found = False
        while p and p != after:
            if p.atShadowFileNodeName() and not p.isAtIgnoreNode() and (p.isDirty() or not writeDirtyOnly):
                ok = at.writeOneAtShadowNode(p, toString=toString, force=True)
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
    #@+node:ekr.20080711093251.5: *6* at.writeOneAtShadowNode & helpers
    def writeOneAtShadowNode(self, p, toString, force):
        '''
        Write p, an @shadow node.
        File indices *must* have already been assigned.
        '''
        trace = False and not g.unitTesting
        at, c, x = self, self.c, self.c.shadowController
        root = p.copy()
        fn = p.atShadowFileNodeName()
        if trace: g.trace(p.h, fn)
        if not fn:
            g.error('can not happen: not an @shadow node', p.h)
            return False
        # A hack to support unknown extensions.
        self.adjustTargetLanguage(fn) # May set c.target_language.
        fn = g.fullPath(c, p)
        at.default_directory = g.os_path_dirname(fn)
        # Bug fix 2010/01/18: Make sure we can compute the shadow directory.
        private_fn = x.shadowPathName(fn)
        if not private_fn:
            return False
        if not toString and at.shouldPromptForDangerousWrite(fn, root):
            # Prompt if writing a new @shadow node would overwrite the existing public file.
            ok = self.promptForDangerousWrite(fn, kind='@shadow')
            if ok:
                # Fix bug 889175: Remember the full fileName.
                at.rememberReadPath(fn, root)
            else:
                g.es("not written:", fn)
                return
        c.endEditing() # Capture the current headline.
        at.initWriteIvars(
            root,
            targetFileName=None, # Not used.
            atShadow=True,
            nosentinels=None,
                # set below.  Affects only error messages (sometimes).
            toString=False,
                # True: create a FileLikeObject below.
            forcePythonSentinels=True,
                # A hack to suppress an error message.
                # The actual sentinels will be set below.
        )
        #
        # Bug fix: Leo 4.5.1:
        # use x.markerFromFileName to force the delim to match
        # what is used in x.propegate changes.
        marker = x.markerFromFileName(fn)
        at.startSentinelComment, at.endSentinelComment = marker.getDelims()
        if g.app.unitTesting:
            ivars_dict = g.getIvarsDict(at)
        # Write the public and private files to public_s and private_s strings.
        data = []
        for sentinels in (False, True):
            # Specify encoding explicitly.
            theFile = at.openStringFile(fn, encoding=at.encoding)
            at.sentinels = sentinels
            at.writeOpenFile(root,
                nosentinels=not sentinels, toString=False)
                    # nosentinels only affects error messages.
            s = at.closeStringFile(theFile)
            data.append(s)
        # Set these new ivars for unit tests.
        # data has exactly two elements.
        # pylint: disable=unbalanced-tuple-unpacking
        at.public_s, at.private_s = data
        if g.app.unitTesting:
            exceptions = ('public_s', 'private_s', 'sentinels', 'stringOutput', 'outputContents')
            assert g.checkUnchangedIvars(at, ivars_dict, exceptions), 'writeOneAtShadowNode'
        if at.errors == 0 and not toString:
            # Write the public and private files.
            if trace: g.trace('writing', fn)
            x.makeShadowDirectory(fn)
                # makeShadowDirectory takes a *public* file name.
            at.replaceFileWithString(private_fn, at.private_s)
            at.replaceFileWithString(fn, at.public_s)
        self.checkPythonCode(root, s=at.private_s, targetFn=fn)
        if at.errors == 0:
            root.clearOrphan()
            root.clearDirty()
        else:
            g.error("not written:", at.outputFileName)
            root.setDirty()
            root.setOrphan()
        return at.errors == 0
    #@+node:ekr.20080819075811.13: *7* adjustTargetLanguage
    def adjustTargetLanguage(self, fn):
        """Use the language implied by fn's extension if
        there is a conflict between it and c.target_language."""
        at = self
        c = at.c
        junk, ext = g.os_path_splitext(fn)
        if ext:
            if ext.startswith('.'): ext = ext[1:]
            language = g.app.extension_dict.get(ext)
            if language:
                c.target_language = language
            else:
                # An unknown language.
                pass # Use the default language, **not** 'unknown_language'
    #@+node:ekr.20050506084734: *5* at.writeFromString
    def writeFromString(self, root, s, forcePythonSentinels=True, useSentinels=True):
        """
        Write a 4.x derived file from a string.

        This is at.write specialized for scripting.
        """
        at = self; c = at.c
        c.endEditing()
            # Capture the current headline, but don't change the focus!
        at.initWriteIvars(root, "<string-file>",
            nosentinels=not useSentinels,
            toString=True,
            forcePythonSentinels=forcePythonSentinels,
        )
        try:
            ok = at.openFileForWriting(root, at.targetFileName, toString=True)
            if g.app.unitTesting:
                assert ok, 'writeFromString' # string writes never fail.
            # Simulate writing the entire file so error recovery works.
            at.writeOpenFile(root,
                nosentinels=not useSentinels,
                toString=True,
                fromString=s,
            )
            at.closeWriteFile()
            # Major bug: failure to clear this wipes out headlines!
            # Minor bug: sometimes this causes slight problems...
            if root:
                if hasattr(self.root.v, 'tnodeList'):
                    delattr(self.root.v, 'tnodeList')
                root.v._p_changed = True
        except Exception:
            at.exception("exception preprocessing script")
        return at.stringOutput
    #@+node:ekr.20041005105605.151: *5* at.writeMissing & helper
    def writeMissing(self, p, toString=False):
        at = self; c = at.c
        writtenFiles = False
        c.init_error_dialogs()
        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after: # Don't use iterator.
            if p.isAtAsisFileNode() or (p.isAnyAtFileNode() and not p.isAtIgnoreNode()):
                at.targetFileName = p.anyAtFileNodeName()
                if at.targetFileName:
                    at.targetFileName = c.os_path_finalize_join(
                        self.default_directory, at.targetFileName)
                    if not g.os_path_exists(at.targetFileName):
                        ok = at.openFileForWriting(p, at.targetFileName, toString)
                                # calls p.setDirty() if there are errors.
                        if ok:
                            at.writeMissingNode(p)
                            writtenFiles = True
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
    #@+node:ekr.20041005105605.152: *6* at.writeMissingNode
    def writeMissingNode(self, p):

        at = self
        if p.isAtAsisFileNode():
            at.asisWrite(p)
        elif p.isAtNoSentFileNode():
            at.write(p, kind='@nosent', nosentinels=True)
        elif p.isAtFileNode():
            at.write(p, kind='@file')
        else:
            g.trace('can not happen: unknown @file node')
    #@+node:ekr.20090225080846.5: *5* at.writeOneAtEditNode
    def writeOneAtEditNode(self, p, toString, force=False):
        '''Write one @edit node.'''
        at = self; c = at.c
        root = p.copy()
        c.endEditing()
        c.init_error_dialogs()
        fn = p.atEditNodeName()
        if not fn and not toString:
            return False
        if p.hasChildren():
            g.error('@edit nodes must not have children')
            g.es('To save your work, convert @edit to @auto, @file or @clean')
            return False
        at.default_directory = g.setDefaultDirectory(c, p, importing=True)
        fn = c.os_path_finalize_join(at.default_directory, fn)
        if not force and at.shouldPromptForDangerousWrite(fn, root):
            # Prompt if writing a new @edit node would overwrite the existing file.
            ok = self.promptForDangerousWrite(fn, kind='@edit')
            if ok:
                # Fix bug 889175: Remember the full fileName.
                at.rememberReadPath(fn, root)
            else:
                g.es("not written:", fn)
                return False
        at.targetFileName = fn
        at.initWriteIvars(root, at.targetFileName,
            atEdit=True,
            nosentinels=True,
            toString=toString,
        )
        # Compute the file's contents.
        # Unlike the @clean/@nosent file logic, it does not add a final newline.
        contents = ''.join([s for s in g.splitLines(p.b)
            if at.directiveKind4(s, 0) == at.noDirective])
        if toString:
            at.stringOutput = contents
            return True
        ok = at.openFileForWriting(root, fileName=fn, toString=False)
        if ok:
            self.os(contents)
            at.closeWriteFile()
        if ok and at.errors == 0:
            at.replaceTargetFileIfDifferent(root) # Sets/clears dirty and orphan bits.
        else:
            g.es("not written:", at.targetFileName) # 2010/10/22
            root.setDirty()
            root.setOrphan() # 2010/10/22
        c.raise_error_dialogs(kind='write')
        return ok
    #@+node:ekr.20041005105605.157: *5* at.writeOpenFile
    def writeOpenFile(self, root, nosentinels=False, toString=False, fromString=''):
        """Do all writes except asis writes."""
        at = self
        s = fromString if fromString else root.v.b
        root.clearAllVisitedInTree()
        at.putAtFirstLines(s)
        at.putOpenLeoSentinel("@+leo-ver=5")
        at.putInitialComment()
        at.putOpenNodeSentinel(root)
        at.putBody(root, fromString=fromString)
        at.putCloseNodeSentinel(root)
        # The -leo sentinel is required to handle @last.
        at.putSentinel("@-leo")
        root.setVisited()
        at.putAtLastLines(s)
        if not toString:
            at.warnAboutOrphandAndIgnoredNodes()
    #@+node:ekr.20041005105605.160: *4* Writing 4.x
    #@+node:ekr.20041005105605.161: *5* at.putBody & helpers
    def putBody(self, p, fromString=''):
        '''
        Generate the body enclosed in sentinel lines.
        Return True if the body contains an @others line.
        '''
        at = self
        # New in 4.3 b2: get s from fromString if possible.
        s = fromString if fromString else p.b
        p.v.setVisited()
            # Make sure v is never expanded again.
            # Suppress orphans check.
        s, trailingNewlineFlag = at.ensureTrailingNewline(s)
        at.raw = False # Bug fix.
        i = 0
        status = g.Bunch(
            at_comment_seen = False,
            at_delims_seen = False,
            at_warning_given = False,
            has_at_others = False,
            in_code = True,
        )
        while i < len(s):
            next_i = g.skip_line(s, i)
            assert next_i > i, 'putBody'
            kind = at.directiveKind4(s, i)
            at.putLine(i, kind, p, s, status)
            i = next_i
        # pylint: disable=no-member
            # g.bunch *does* have .in_code and has_at_others members.
        if not status.in_code:
            at.putEndDocLine()
        if not trailingNewlineFlag:
            if at.sentinels:
                pass # Never write @nonl
            elif not at.atEdit:
                at.onl()
        return status.has_at_others
    #@+node:ekr.20041005105605.162: *6* at.ensureTrailingNewline
    def ensureTrailingNewline(self, s):
        '''
        Ensure a trailing newline in s.
        If we add a trailing newline, we'll generate an @nonl sentinel below.

        - We always ensure a newline in @file and @thin trees.
        - This code is not used used in @asis trees.
        - New in Leo 4.4.3 b1: We add a newline in @clean/@nosent trees unless
          @bool force_newlines_in_at_nosent_bodies = False
        '''
        at = self
        if s:
            trailingNewlineFlag = s[-1] == '\n'
            if not trailingNewlineFlag:
                if at.sentinels or at.force_newlines_in_at_nosent_bodies:
                    # g.trace('Added newline',repr(s))
                    s = s + '\n'
        else:
            trailingNewlineFlag = True # don't need to generate an @nonl
        return s, trailingNewlineFlag
    #@+node:ekr.20041005105605.163: *6* at.putLine
    def putLine(self, i, kind, p, s, status):
        '''Put the line at s[i:] of the given kind, updating the status.'''
        at = self
        if kind == at.noDirective:
            if status.in_code:
                if at.raw:
                    at.putCodeLine(s, i)
                else:
                    name, n1, n2 = at.findSectionName(s, i)
                    if name:
                        at.putRefLine(s, i, n1, n2, name, p)
                    else:
                        at.putCodeLine(s, i)
            else:
                at.putDocLine(s, i)
        elif at.raw:
            if kind == at.endRawDirective:
                at.raw = False
                at.putSentinel("@@end_raw")
            else:
                # Fix bug 784920: @raw mode does not ignore directives
                at.putCodeLine(s, i)
        elif kind in (at.docDirective, at.atDirective):
            assert not at.pending, 'putBody at.pending'
            if not status.in_code:
                # Bug fix 12/31/04: handle adjacent doc parts.
                at.putEndDocLine()
            at.putStartDocLine(s, i, kind)
            status.in_code = False
        elif kind in (at.cDirective, at.codeDirective):
            # Only @c and @code end a doc part.
            if not status.in_code:
                at.putEndDocLine()
            at.putDirective(s, i)
            status.in_code = True
        elif kind == at.allDirective:
            if status.in_code:
                if p == self.root:
                    at.putAtAllLine(s, i, p)
                else:
                    at.error('@all not valid in: %s' % (p.h))
            else: at.putDocLine(s, i)
        elif kind == at.othersDirective:
            if status.in_code:
                if status.has_at_others:
                    at.error('multiple @others in: %s' % (p.h))
                else:
                    at.putAtOthersLine(s, i, p)
                    status.has_at_others = True
            else:
                at.putDocLine(s, i)
        elif kind == at.rawDirective:
            at.raw = True
            at.putSentinel("@@raw")
        elif kind == at.endRawDirective:
            # Fix bug 784920: @raw mode does not ignore directives
            at.error('unmatched @end_raw directive: %s' % p.h)
        elif kind == at.startVerbatim:
            # Fix bug 778204: @verbatim not a valid Leo directive.
            if g.unitTesting:
                # A hack: unit tests for @shadow use @verbatim as a kind of directive.
                pass
            else:
                at.error('@verbatim is not a Leo directive: %s' % p.h)
        elif kind == at.miscDirective:
            # Fix bug 583878: Leo should warn about @comment/@delims clashes.
            if g.match_word(s, i, '@comment'):
                status.at_comment_seen = True
            elif g.match_word(s, i, '@delims'):
                status.at_delims_seen = True
            if (
                status.at_comment_seen and
                status.at_delims_seen and not
                status.at_warning_given
            ):
                status.at_warning_given = True
                at.error('@comment and @delims in node %s' % p.h)
            at.putDirective(s, i)
        else:
            at.error('putBody: can not happen: unknown directive kind: %s' % kind)
    #@+node:ekr.20041005105605.164: *5* writing code lines...
    #@+node:ekr.20041005105605.165: *6* at.@all
    #@+node:ekr.20041005105605.166: *7* at.putAtAllLine
    def putAtAllLine(self, s, i, p):
        """Put the expansion of @all."""
        at = self
        j, delta = g.skip_leading_ws_with_indent(s, i, at.tab_width)
        at.putLeadInSentinel(s, i, j, delta)
        at.indent += delta
        at.putSentinel("@+all")
        for child in p.children():
            at.putAtAllChild(child)
        at.putSentinel("@-all")
        at.indent -= delta
    #@+node:ekr.20041005105605.167: *7* at.putAtAllBody
    def putAtAllBody(self, p):
        """ Generate the body enclosed in sentinel lines."""
        at = self
        s = p.b
        p.v.setVisited()
            # Make sure v is never expanded again.
            # Suppress orphans check.
        if at.sentinels and s and s[-1] != '\n':
            s = s + '\n'
        i, inCode = 0, True
        while i < len(s):
            next_i = g.skip_line(s, i)
            assert(next_i > i)
            if inCode:
                # Use verbatim sentinels to write all directives.
                at.putCodeLine(s, i)
            else:
                at.putDocLine(s, i)
            i = next_i
        if not inCode:
            at.putEndDocLine()
    #@+node:ekr.20041005105605.169: *7* at.putAtAllChild
    #@+at This code puts only the first of two or more cloned siblings, preceding the
    # clone with an @clone n sentinel.
    # 
    # This is a debatable choice: the cloned tree appears only once in the external
    # file. This should be benign; the text created by @all is likely to be used only
    # for recreating the outline in Leo. The representation in the derived file
    # doesn't matter much.
    #@@c

    def putAtAllChild(self, p):
        at = self
        parent_v = p._parentVnode()
        if False: # 2010/01/23: This generates AtFile errors about orphan nodes.
            clonedSibs, thisClonedSibIndex = at.scanForClonedSibs(parent_v, p.v)
            if clonedSibs > 1:
                at.putSentinel("@clone %d" % (clonedSibs))
            else:
                g.trace('**** ignoring', p.h)
                p.v.setVisited() # 2010/01/23
                return # Don't write second or greater trees.
        at.putOpenNodeSentinel(p, inAtAll=True) # Suppress warnings about @file nodes.
        at.putAtAllBody(p)
        for child in p.children():
            at.putAtAllChild(child)
        at.putCloseNodeSentinel(p)
    #@+node:ekr.20041005105605.170: *6* at.@others (write)
    #@+node:ekr.20041005105605.173: *7* putAtOthersLine & helpers
    def putAtOthersLine(self, s, i, p):
        """Put the expansion of @others."""
        at = self
        j, delta = g.skip_leading_ws_with_indent(s, i, at.tab_width)
        at.putLeadInSentinel(s, i, j, delta)
        at.indent += delta
        at.putSentinel("@+others")
            # Never write lws in new sentinels.
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
        # This is the same in both old and new sentinels.
        at.putSentinel("@-others")
        at.indent -= delta
    #@+node:ekr.20041005105605.172: *8* putAtOthersChild
    def putAtOthersChild(self, p):
        at = self
        at.putOpenNodeSentinel(p)
        at.putBody(p)
        at.putCloseNodeSentinel(p)
    #@+node:ekr.20041005105605.171: *8* validInAtOthers (write)
    def validInAtOthers(self, p):
        """
        Return True if p should be included in the expansion of the @others
        directive in the body text of p's parent.
        """
        at = self
        i = g.skip_ws(p.h, 0)
        isSection, junk = at.isSectionName(p.h, i)
        if isSection:
            return False # A section definition node.
        elif at.sentinels or at.toString:
            # @ignore must not stop expansion here!
            return True
        elif p.isAtIgnoreNode():
            g.error('did not write @ignore node', p.v.h)
            return False
        else:
            return True
    #@+node:ekr.20041005105605.174: *6* at.putCodeLine
    def putCodeLine(self, s, i):
        '''Put a normal code line.'''
        trace = False and not g.unitTesting
        at = self
        # Put @verbatim sentinel if required.
        k = g.skip_ws(s, i)
        if g.match(s, k, self.startSentinelComment + '@'):
            self.putSentinel('@verbatim')
        j = g.skip_line(s, i)
        line = s[i: j]
        if trace: g.trace(repr(line))
        # Don't put any whitespace in otherwise blank lines.
        if len(line) > 1: # Preserve *anything* the user puts on the line!!!
            if not at.raw:
                at.putIndent(at.indent, line)
            if line[-1:] == '\n':
                # g.trace(repr(line))
                at.os(line[: -1])
                at.onl()
            else:
                at.os(line)
        elif line and line[-1] == '\n':
            at.onl()
        elif line:
            at.os(line) # Bug fix: 2013/09/16
        else:
            g.trace('Can not happen: completely empty line')
    #@+node:ekr.20041005105605.176: *6* at.putRefLine & helpers
    def putRefLine(self, s, i, n1, n2, name, p):
        """Put a line containing one or more references."""
        at = self
        ref = at.findReference(name, p)
        if not ref:
            if hasattr(at, 'allow_undefined_refs'):
                # Allow apparent section reference: just write the line.
                at.putCodeLine(s, i)
            return
        # Compute delta only once.
        junk, delta = g.skip_leading_ws_with_indent(s, i, at.tab_width)
        # Write the lead-in sentinel only once.
        at.putLeadInSentinel(s, i, n1, delta)
        self.putRefAt(name, ref, delta)
        while 1:
            progress = i
            i = n2
            name, n1, n2 = at.findSectionName(s, i)
            if name:
                ref = at.findReference(name, p)
                    # Issues error if not found.
                if ref:
                    middle_s = s[i:n1]
                    self.putAfterMiddleRef(middle_s, delta)
                    self.putRefAt(name, ref, delta)
            else: break
            assert progress < i
        self.putAfterLastRef(s, i, delta)
    #@+node:ekr.20131224085853.16443: *7* at.findReference
    def findReference(self, name, p):
        '''Find a reference to name.  Raise an error if not found.'''
        at = self
        ref = g.findReference(name, p)
        if not ref and not hasattr(at, 'allow_undefined_refs'):
            # Do give this error even if unit testing.
            at.writeError(
                "undefined section: %s\n\treferenced from: %s" % (
                    g.truncate(name, 60), g.truncate(p.h, 60)))
        return ref
    #@+node:ekr.20041005105605.199: *7* at.findSectionName
    def findSectionName(self, s, i):
        '''
        Return n1, n2 representing a section name.
        The section name, *including* brackes is s[n1:n2]
        '''
        end = s.find('\n', i)
        if end == -1:
            n1 = s.find("<<", i)
            n2 = s.find(">>", i)
        else:
            n1 = s.find("<<", i, end)
            n2 = s.find(">>", i, end)
        ok = -1 < n1 < n2
        if ok:
            # Warn on extra brackets.
            for ch, j in (('<', n1 + 2), ('>', n2 + 2)):
                if g.match(s, j, ch):
                    line = g.get_line(s, i)
                    g.es('dubious brackets in', line)
                    break
            name = s[n1:n2+2]
            return name, n1, n2+2
        else:
            return None, n1, len(s)
    #@+node:ekr.20041005105605.178: *7* at.putAfterLastRef
    def putAfterLastRef(self, s, start, delta):
        """Handle whatever follows the last ref of a line."""
        at = self
        j = g.skip_ws(s, start)
        if j < len(s) and s[j] != '\n':
            # Temporarily readjust delta to make @afterref look better.
            at.indent += delta
            at.putSentinel("@afterref")
            end = g.skip_line(s, start)
            after = s[start: end]
            at.os(after)
            if at.sentinels and after and after[-1] != '\n':
                at.onl() # Add a newline if the line didn't end with one.
            at.indent -= delta
    #@+node:ekr.20041005105605.179: *7* at.putAfterMiddleRef
    def putAfterMiddleRef(self, s, delta):
        """Handle whatever follows a ref that is not the last ref of a line."""
        at = self
        if s:
            at.indent += delta
            at.putSentinel("@afterref")
            at.os(s)
            at.onl_sent() # Not a real newline.
            at.indent -= delta
    #@+node:ekr.20041005105605.177: *7* at.putRefAt
    def putRefAt(self, name, ref, delta):
        at = self
        # Fix #132: Section Reference causes clone...
        # https://github.com/leo-editor/leo-editor/issues/132
        # Never put any @+middle or @-middle sentinels.
        at.indent += delta
        at.putSentinel("@+" + name)
        at.putOpenNodeSentinel(ref)
        at.putBody(ref)
        at.putCloseNodeSentinel(ref)
        at.putSentinel("@-" + name)
        at.indent -= delta
    #@+node:ekr.20041005105605.180: *5* writing doc lines...
    #@+node:ekr.20041005105605.181: *6* at.putBlankDocLine
    def putBlankDocLine(self):
        at = self
        at.putPending(split=False)
        if not at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.startSentinelComment); at.oblank()
        at.onl()
    #@+node:ekr.20041005105605.183: *6* at.putDocLine
    def putDocLine(self, s, i):
        """
        Handle one line of a doc part.

        Output complete lines and split long lines and queue pending lines.
        Inserted newlines are always preceded by whitespace.
        """
        at = self
        j = g.skip_line(s, i)
        s = s[i: j]
        # if at.endSentinelComment:
            # leading = at.indent
        # else:
            # leading = at.indent + len(at.startSentinelComment) + 1
        if not s or s[0] == '\n':
            # A blank line.
            at.putBlankDocLine()
        else:
            # Write the line as it is.
            at.putIndent(at.indent)
            if not at.endSentinelComment:
                at.os(at.startSentinelComment)
                at.oblank()
            at.os(s)
            if not s.endswith('\n'):
                at.onl()
    #@+node:ekr.20041005105605.185: *6* at.putEndDocLine
    def putEndDocLine(self):
        """Write the conclusion of a doc part."""
        at = self
        at.putPending(split=False)
        # Put the closing delimiter if we are using block comments.
        if at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.endSentinelComment)
            at.onl() # Note: no trailing whitespace.
    #@+node:ekr.20041005105605.186: *6* at.putPending (old only)
    def putPending(self, split):
        """Write the pending part of a doc part.

        We retain trailing whitespace iff the split flag is True."""
        at = self; s = ''.join(at.pending); at.pending = []
        # g.trace("split",s)
        # Remove trailing newline temporarily.  We'll add it back later.
        if s and s[-1] == '\n':
            s = s[: -1]
        if not split:
            s = s.rstrip()
            if not s:
                return
        at.putIndent(at.indent)
        if not at.endSentinelComment:
            at.os(at.startSentinelComment); at.oblank()
        at.os(s); at.onl()
    #@+node:ekr.20041005105605.182: *6* at.putStartDocLine
    def putStartDocLine(self, s, i, kind):
        """Write the start of a doc part."""
        at = self
        at.docKind = kind
        sentinel = "@+doc" if kind == at.docDirective else "@+at"
        directive = "@doc" if kind == at.docDirective else "@"
        # Put whatever follows the directive in the sentinel.
        # Skip past the directive.
        i += len(directive)
        j = g.skip_to_end_of_line(s, i)
        follow = s[i: j]
        # Put the opening @+doc or @-doc sentinel, including whatever follows the directive.
        at.putSentinel(sentinel + follow)
        # Put the opening comment if we are using block comments.
        if at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.startSentinelComment); at.onl()
    #@+node:ekr.20041005105605.187: *4* Writing 4,x sentinels...
    #@+node:ekr.20041005105605.188: *5* at.nodeSentinelText & helper
    def nodeSentinelText(self, p):
        """Return the text of a @+node or @-node sentinel for p."""
        at = self
        h = at.removeCommentDelims(p)
        if getattr(at, 'at_shadow_test_hack', False):
            # A hack for @shadow unit testing.
            # see AtShadowTestCase.makePrivateLines.
            return h
        else:
            gnx = p.v.fileIndex
            level = 1 + p.level() - self.root.level()
            stars = '*' * level
            if 1: # Put the gnx in the traditional place.
                if level > 2:
                    return "%s: *%s* %s" % (gnx, level, h)
                else:
                    return "%s: %s %s" % (gnx, stars, h)
            else: # Hide the gnx to the right.
                pad = max(1, 100 - len(stars) - len(h)) * ' '
                return '%s %s%s::%s' % (stars, h, pad, gnx)
    #@+node:ekr.20041005105605.189: *6* at.removeCommentDelims
    def removeCommentDelims(self, p):
        '''
        If the present @language/@comment settings do not specify a single-line comment
        we remove all block comment delims from h. This prevents headline text from
        interfering with the parsing of node sentinels.
        '''
        at = self
        start = at.startSentinelComment
        end = at.endSentinelComment
        h = p.h
        if end:
            h = h.replace(start, "")
            h = h.replace(end, "")
        return h
    #@+node:ekr.20041005105605.190: *5* at.putLeadInSentinel
    def putLeadInSentinel(self, s, i, j, delta):
        """
        Set at.leadingWs as needed for @+others and @+<< sentinels.

        i points at the start of a line.
        j points at @others or a section reference.
        delta is the change in at.indent that is about to happen and hasn't happened yet.
        """
        at = self
        at.leadingWs = "" # Set the default.
        if i == j:
            return # The @others or ref starts a line.
        k = g.skip_ws(s, i)
        if j == k:
            # Only whitespace before the @others or ref.
            at.leadingWs = s[i: j] # Remember the leading whitespace, including its spelling.
        else:
            self.putIndent(at.indent) # 1/29/04: fix bug reported by Dan Winkler.
            at.os(s[i: j])
            at.onl_sent()
    #@+node:ekr.20041005105605.191: *5* at.putCloseNodeSentinel
    def putCloseNodeSentinel(self, p):
        '''End a node.'''
        at = self
        at.raw = False # Bug fix: 2010/07/04
    #@+node:ekr.20041005105605.192: *5* at.putOpenLeoSentinel 4.x
    def putOpenLeoSentinel(self, s):
        """Write @+leo sentinel."""
        at = self
        if at.sentinels or hasattr(at, 'force_sentinels'):
            s = s + "-thin"
            encoding = at.encoding.lower()
            if encoding != "utf-8":
                # New in 4.2: encoding fields end in ",."
                s = s + "-encoding=%s,." % (encoding)
            at.putSentinel(s)
    #@+node:ekr.20041005105605.193: *5* at.putOpenNodeSentinel
    def putOpenNodeSentinel(self, p, inAtAll=False):
        """Write @+node sentinel for p."""
        at = self
        if not inAtAll and p.isAtFileNode() and p != at.root and not at.toString:
            at.writeError("@file not valid in: " + p.h)
            return
        s = at.nodeSentinelText(p)
        at.putSentinel("@+node:" + s)
        # Leo 4.7 b2: we never write tnodeLists.
    #@+node:ekr.20041005105605.194: *5* at.putSentinel (applies cweb hack) 4.x
    # This method outputs all sentinels.

    def putSentinel(self, s):
        "Write a sentinel whose text is s, applying the CWEB hack if needed."
        at = self
        if at.sentinels or hasattr(at, 'force_sentinels'):
            at.putIndent(at.indent)
            at.os(at.startSentinelComment)
            # apply the cweb hack to s. If the opening comment delim ends in '@',
            # double all '@' signs except the first.
            start = at.startSentinelComment
            if start and start[-1] == '@':
                s = s.replace('@', '@@')[1:]
            at.os(s)
            if at.endSentinelComment:
                at.os(at.endSentinelComment)
            at.onl()
    #@+node:ekr.20041005105605.196: *4* Writing 4.x utils...
    #@+node:ekr.20090514111518.5661: *5* at.checkPythonCode & helpers
    def checkPythonCode(self, root, s=None, targetFn=None, pyflakes_errors_only=False):
        '''Perform python-related checks on root.'''
        at = self
        if not targetFn:
            targetFn = at.targetFileName
        if targetFn and targetFn.endswith('.py') and at.checkPythonCodeOnWrite:
            if not s:
                s = at.outputContents
                if not s: return
            # It's too slow to check each node separately.
            if pyflakes_errors_only:
                ok = True
            else:
                ok = at.checkPythonSyntax(root, s)
            # Syntax checking catches most indentation problems.
                # if ok: at.tabNannyNode(root,s)
            if ok and at.runPyFlakesOnWrite and not g.unitTesting:
                ok2 = self.runPyflakes(root, pyflakes_errors_only=pyflakes_errors_only)
            else:
                ok2 = True
            if not ok or not ok2:
                g.app.syntax_error_files.append(g.shortFileName(targetFn))
    #@+node:ekr.20090514111518.5663: *6* at.checkPythonSyntax
    def checkPythonSyntax(self, p, body, supress=False):
        at = self
        try:
            ok = True
            if not g.isPython3:
                body = g.toEncodedString(body)
            body = body.replace('\r', '')
            fn = '<node: %s>' % p.h
            compile(body + '\n', fn, 'exec')
        except SyntaxError:
            if not supress:
                at.syntaxError(p, body)
            ok = False
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            ok = False
        return ok
    #@+node:ekr.20090514111518.5666: *7* at.syntaxError (leoAtFile)
    def syntaxError(self, p, body):
        '''Report a syntax error.'''
        g.error("Syntax error in: %s" % (p.h))
        typ, val, tb = sys.exc_info()
        message = hasattr(val, 'message') and val.message
        if message: g.es_print(message)
        if val is None: return
        lines = g.splitLines(body)
        n = val.lineno
        offset = val.offset or 0
        if n is None: return
        i = val.lineno - 1
        for j in range(max(0, i - 2), min(i + 2, len(lines) - 1)):
            if j == i:
                mark = '*'
                node_link = "%s,-%d" % (
                    p.get_UNL(with_proto=True, with_count=True), j+1)
            else:
                mark = ' '
                node_link = None
            text = '%5s:%s %s' % (j+1, mark, lines[j].rstrip())
            g.es_print(text, nodeLink=node_link)
            if j == i:
                g.es_print(' ' * (7 + offset) + '^')
    #@+node:ekr.20161021084954.1: *6* at.runPyflakes
    def runPyflakes(self, root, pyflakes_errors_only):
        '''Run pyflakes on the selected node.'''
        try:
            import leo.commands.checkerCommands as checkerCommands
            if checkerCommands.pyflakes:
                x = checkerCommands.PyflakesCommand(self.c)
                ok = x.run(p=root,pyflakes_errors_only=pyflakes_errors_only)
                return ok
            else:
                return True # Suppress error if pyflakes can not be imported.
        except Exception:
            g.es_exception()
    #@+node:ekr.20090514111518.5665: *6* at.tabNannyNode
    def tabNannyNode(self, p, body, suppress=False):
        import parser
        import tabnanny
        import tokenize
        try:
            readline = g.ReadLinesClass(body).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))
        except parser.ParserError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.error("ParserError in", p.h)
                g.es('', str(msg))
        except IndentationError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.error("IndentationError in", p.h)
                g.es('', str(msg))
        except tokenize.TokenError:
            junk, msg, junk = sys.exc_info()
            if suppress:
                raise
            else:
                g.error("TokenError in", p.h)
                g.es('', str(msg))
        except tabnanny.NannyNag:
            junk, nag, junk = sys.exc_info()
            if suppress:
                raise
            else:
                badline = nag.get_lineno()
                line = nag.get_line()
                message = nag.get_msg()
                g.error("indentation error in", p.h, "line", badline)
                g.es(message)
                line2 = repr(str(line))[1: -1]
                g.es("offending line:\n", line2)
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            if suppress: raise
    #@+node:ekr.20080712150045.3: *5* at.closeStringFile
    def closeStringFile(self, theFile):
        at = self
        if theFile:
            theFile.flush()
            s = at.stringOutput = theFile.get()
            at.outputContents = s
            theFile.close()
            at.outputFile = None
            at.outputFileName = g.u('')
            at.shortFileName = ''
            at.targetFileName = None
            return s
        else:
            return None
    #@+node:ekr.20041005105605.135: *5* at.closeWriteFile
    # 4.0: Don't use newline-pending logic.

    def closeWriteFile(self):
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
    #@+node:ekr.20041005105605.197: *5* at.compareFiles
    def compareFiles(self, path1, path2, ignoreLineEndings, ignoreBlankLines=False):
        """Compare two text files."""
        trace = False and not g.unitTesting
        at = self
        # We can't use 'U' mode because of encoding issues (Python 2.x only).
        s1 = at.outputContents
        e1 = at.encoding
        if trace: g.trace('type(s1)', type(s1))
        if s1 is None:
            g.internalError('empty compare file: %s' % path1)
            return False
        s2 = g.readFileIntoEncodedString(path2)
        e2 = None
        if s2 is None:
            g.internalError('empty compare file: %s' % path2)
            return False
        # 2013/10/28: fix bug #1243855: @auto-rst doesn't save text
        # Make sure both strings are unicode.
        # This is requred to handle binary files in Python 3.x.
        if not g.isUnicode(s1):
            s1 = g.toUnicode(s1, encoding=e1)
        if not g.isUnicode(s2):
            s2 = g.toUnicode(s2, encoding=e2)
        equal = s1 == s2
        if ignoreBlankLines and not equal:
            s1 = g.removeBlankLines(s1)
            s2 = g.removeBlankLines(s2)
            equal = s1 == s2
        if ignoreLineEndings and not equal:
            # Wrong: equivalent to ignoreBlankLines!
                # s1 = s1.replace('\n','').replace('\r','')
                # s2 = s2.replace('\n','').replace('\r','')
            s1 = s1.replace('\r', '')
            s2 = s2.replace('\r', '')
            equal = s1 == s2
        if trace: g.trace('equal', equal)
        return equal
    #@+node:ekr.20041005105605.198: *5* at.directiveKind4 (write logic, changed)
    # These patterns exclude constructs such as @encoding.setter or @encoding(whatever)
    # However, they must allow @language python, @nocolor-node, etc.
    at_directive_kind_pattern = re.compile(r'\s*@([\w-]+)\s*')

    def directiveKind4(self, s, i):
        """Return the kind of at-directive or noDirective."""
        trace = False and not g.unitTesting
        at = self
        n = len(s)
        if trace and s.startswith('@'): g.trace(s.rstrip())
        if i >= n or s[i] != '@':
            j = g.skip_ws(s, i)
            if g.match_word(s, j, "@others"):
                return at.othersDirective
            elif g.match_word(s, j, "@all"):
                return at.allDirective
            else:
                return at.noDirective
        table = (
            ("@all", at.allDirective),
            ("@c", at.cDirective),
            ("@code", at.codeDirective),
            ("@doc", at.docDirective),
            ("@end_raw", at.endRawDirective),
            ("@others", at.othersDirective),
            ("@raw", at.rawDirective),
            ("@verbatim", at.startVerbatim))
        # Rewritten 6/8/2005.
        if i + 1 >= n or s[i + 1] in (' ', '\t', '\n'):
            # Bare '@' not recognized in cweb mode.
            return at.noDirective if at.language == "cweb" else at.atDirective
        if not s[i + 1].isalpha():
            return at.noDirective # Bug fix: do NOT return miscDirective here!
        if at.language == "cweb" and g.match_word(s, i, '@c'):
            return at.noDirective
        for name, directive in table:
            if g.match_word(s, i, name):
                return directive
        # New in Leo 4.4.3: add support for add_directives plugin.
        # 2017/01/23: Use regex to properly distinguish between Leo directives
        # and python decorators.
        s2 = s[i:]
        m = self.at_directive_kind_pattern.match(s2)
        if m:
            word = m.group(1)
            if word not in g.globalDirectiveList:
                return at.noDirective
            s3 = s2[m.end(1):]
            if s3 and s3[0] in ".(":
                return at.noDirective
            else:
                return at.miscDirective
        return at.noDirective
    #@+node:ekr.20041005105605.200: *5* at.isSectionName
    # returns (flag, end). end is the index of the character after the section name.

    def isSectionName(self, s, i):
        # 2013/08/01: bug fix: allow leading periods.
        while i < len(s) and s[i] == '.':
            i += 1
        if not g.match(s, i, "<<"):
            return False, -1
        i = g.find_on_line(s, i, ">>")
        if i > -1:
            return True, i + 2
        else:
            return False, -1
    #@+node:ekr.20070909103844: *5* at.isSignificantTree (not used!)
    def isSignificantTree(self, p):
        '''Return True if p's tree has a significant amount of information.'''
        trace = False and not g.unitTesting
        s = p.b
        # Remove all blank lines and all Leo directives.
        lines = []
        for line in g.splitLines(s):
            if not line.strip():
                pass
            elif line.startswith('@'):
                i = 1; j = g.skip_id(line, i, chars='-')
                word = s[i: j]
                if not (word and word in g.globalDirectiveList):
                    lines.append(line)
            else:
                lines.append(line)
        s2 = ''.join(lines)
        val = p.hasChildren() or len(s2.strip()) >= 10
        if trace: g.trace(val, p.h)
        return val
    #@+node:ekr.20080712150045.2: *5* at.openStringFile
    def openStringFile(self, fn, encoding='utf-8'):
        at = self
        at.shortFileName = g.shortFileName(fn)
        at.outputFileName = "<string: %s>" % at.shortFileName
        at.outputFile = g.FileLikeObject(encoding=encoding)
        at.targetFileName = "<string-file>"
        return at.outputFile
    #@+node:ekr.20041005105605.201: *5* at.os and allies
    # Note:  self.outputFile may be either a FileLikeObject or a real file.
    #@+node:ekr.20041005105605.202: *6* at.oblank, oblanks & otabs
    def oblank(self):
        self.os(' ')

    def oblanks(self, n):
        self.os(' ' * abs(n))

    def otabs(self, n):
        self.os('\t' * abs(n))
    #@+node:ekr.20041005105605.203: *6* at.onl & onl_sent
    def onl(self):
        """Write a newline to the output stream."""
        self.os('\n') # not self.output_newline

    def onl_sent(self):
        """Write a newline to the output stream, provided we are outputting sentinels."""
        if self.sentinels:
            self.onl()
    #@+node:ekr.20041005105605.204: *6* at.os
    def os(self, s):
        """Write a string to the output stream.

        All output produced by leoAtFile module goes here."""
        trace = False and not g.unitTesting
        at = self
        tag = self.underindentEscapeString
        f = at.outputFile
        assert isinstance(f, g.FileLikeObject), f
        if s and f:
            try:
                if s.startswith(tag):
                    junk, s = self.parseUnderindentTag(s)
                # Bug fix: this must be done last.
                # Convert everything to unicode.
                # We expect plain text coming only from sentinels.
                if not g.isUnicode(s):
                    s = g.toUnicode(s, 'ascii')
                if trace: g.trace(at.encoding, f, repr(s))
                f.write(s)
            except Exception:
                at.exception("exception writing:" + s)
    #@+node:ekr.20041005105605.205: *5* at.outputStringWithLineEndings
    # Write the string s as-is except that we replace '\n' with the proper line ending.

    def outputStringWithLineEndings(self, s):
        at = self
        # Calling self.onl() runs afoul of queued newlines.
        if g.isPython3:
            s = g.ue(s, at.encoding)
        s = s.replace('\n', at.output_newline)
        self.os(s)
    #@+node:ekr.20050506090446.1: *5* at.putAtFirstLines
    def putAtFirstLines(self, s):
        '''Write any @firstlines from string s.
        These lines are converted to @verbatim lines,
        so the read logic simply ignores lines preceding the @+leo sentinel.'''
        at = self; tag = "@first"
        i = 0
        while g.match(s, i, tag):
            i += len(tag)
            i = g.skip_ws(s, i)
            j = i
            i = g.skip_to_end_of_line(s, i)
            # Write @first line, whether empty or not
            line = s[j: i]
            at.os(line); at.onl()
            i = g.skip_nl(s, i)
    #@+node:ekr.20050506090955: *5* at.putAtLastLines
    def putAtLastLines(self, s):
        '''Write any @last lines from string s.
        These lines are converted to @verbatim lines,
        so the read logic simply ignores lines following the @-leo sentinel.'''
        at = self; tag = "@last"
        # Use g.splitLines to preserve trailing newlines.
        lines = g.splitLines(s)
        n = len(lines); j = k = n - 1
        # Scan backwards for @last directives.
        while j >= 0:
            line = lines[j]
            if g.match(line, 0, tag): j -= 1
            elif not line.strip():
                j -= 1
            else: break
        # Write the @last lines.
        for line in lines[j + 1: k + 1]:
            if g.match(line, 0, tag):
                i = len(tag); i = g.skip_ws(line, i)
                at.os(line[i:])
    #@+node:ekr.20071117152308: *5* at.putBuffered
    def putBuffered(self, s):
        '''Put s, converting all tabs to blanks as necessary.'''
        if not s: return
        w = self.tab_width
        if w < 0:
            result = []
            lines = s.split('\n')
            for line in lines:
                line2 = []; j = 0
                for ch in line:
                    j += 1
                    if ch == '\t':
                        w2 = g.computeWidth(s[: j], w)
                        w3 = (abs(w) - (w2 % abs(w)))
                        line2.append(' ' * w3)
                    else:
                        line2.append(ch)
                result.append(''.join(line2))
            s = '\n'.join(result)
        self.os(s)
    #@+node:ekr.20041005105605.206: *5* at.putDirective 4.x & helper
    def putDirective(self, s, i):
        r'''
        Output a sentinel a directive or reference s.

        It is important for PHP and other situations that \@first and \@last
        directives get translated to verbatim lines that do *not* include what
        follows the @first & @last directives.
        '''
        at = self
        # assert(i < len(s) and s[i] == '@')
        k = i
        j = g.skip_to_end_of_line(s, i)
        directive = s[i: j]
        if g.match_word(s, k, "@delims"):
            at.putDelims(directive, s, k)
        elif g.match_word(s, k, "@language"):
            self.putSentinel("@" + directive)
        elif g.match_word(s, k, "@comment"):
            self.putSentinel("@" + directive)
        elif g.match_word(s, k, "@last"):
            self.putSentinel("@@last")
                # Convert to an verbatim line _without_ anything else.
        elif g.match_word(s, k, "@first"):
            self.putSentinel("@@first")
                # Convert to an verbatim line _without_ anything else.
        else:
            self.putSentinel("@" + directive)
        i = g.skip_line(s, k)
        return i
    #@+node:ekr.20041005105605.207: *6* at.putDelims
    def putDelims(self, directive, s, k):
        '''Put an @delims directive.'''
        at = self
        # Put a space to protect the last delim.
        at.putSentinel(directive + " ") # 10/23/02: put @delims, not @@delims
        # Skip the keyword and whitespace.
        j = i = g.skip_ws(s, k + len("@delims"))
        # Get the first delim.
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
            i += 1
        if j < i:
            at.startSentinelComment = s[j: i]
            # Get the optional second delim.
            j = i = g.skip_ws(s, i)
            while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
                i += 1
            at.endSentinelComment = s[j: i] if j < i else ""
        else:
            at.writeError("Bad @delims directive")
    #@+node:ekr.20041005105605.210: *5* at.putIndent
    def putIndent(self, n, s=''):
        """Put tabs and spaces corresponding to n spaces,
        assuming that we are at the start of a line.

        Remove extra blanks if the line starts with the underindentEscapeString"""
        tag = self.underindentEscapeString
        if s.startswith(tag):
            n2, s2 = self.parseUnderindentTag(s)
            if n2 >= n: return
            elif n > 0: n -= n2
            else: n += n2
        if n > 0:
            w = self.tab_width
            if w > 1:
                q, r = divmod(n, w)
                self.otabs(q)
                self.oblanks(r)
            else:
                self.oblanks(n)
    #@+node:ekr.20041005105605.211: *5* at.putInitialComment
    def putInitialComment(self):
        c = self.c
        s2 = c.config.output_initial_comment
        if s2:
            lines = s2.split("\\n")
            for line in lines:
                line = line.replace("@date", time.asctime())
                if line:
                    self.putSentinel("@comment " + line)
    #@+node:ekr.20080712150045.1: *5* at.replaceFileWithString
    def replaceFileWithString(self, fn, s):
        '''
        Replace the file with s if s is different from theFile's contents.

        Return True if theFile was changed.

        This is used only by the @shadow logic.
        '''
        trace = False and not g.unitTesting
        at, c = self, self.c
        exists = g.os_path_exists(fn)
        if exists: # Read the file.  Return if it is the same.
            s2, e = g.readFileIntoString(fn)
            if s is None:
                return False
            if s == s2:
                report = c.config.getBool('report_unchanged_files', default=True)
                if report and not g.unitTesting:
                    g.es('unchanged:', fn)
                return False
        # Issue warning if directory does not exist.
        theDir = g.os_path_dirname(fn)
        if theDir and not g.os_path_exists(theDir):
            if not g.unitTesting:
                g.error('not written: %s directory not found' % fn)
            return False
        # Replace
        try:
            f = open(fn, 'wb')
            # 2013/10/28: Fix bug 1243847: unicode error when saving @shadow nodes.
            # Call g.toEncodedString regardless of Python version.
            s = g.toEncodedString(s, encoding=self.encoding)
            f.write(s)
            f.close()
            if g.unitTesting:
                if trace: g.trace('*****', fn)
            else:
                if exists:
                    g.es('wrote:    ', fn)
                else:
                    g.es('created:', fn)
            return True
        except IOError:
            at.error('unexpected exception writing file: %s' % (fn))
            g.es_exception()
            return False
    #@+node:ekr.20041005105605.212: *5* at.replaceTargetFileIfDifferent
    def replaceTargetFileIfDifferent(self, root, ignoreBlankLines=False):
        '''Create target file as follows:
        1. If target file does not exist, rename output file to target file.
        2. If target file is identical to output file, remove the output file.
        3. If target file is different from output file,
           remove target file, then rename output file to be target file.

        Return True if the original file was changed.
        '''
        trace = False and not g.unitTesting
        at = self; c = at.c
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
            'ignoreBlankLines', ignoreBlankLines,
            'target exists', g.os_path_exists(at.targetFileName),
            at.outputFileName, at.targetFileName)
        # #531: Optionally report timestamp...
        if c.config.getBool('log_show_save_time', default=False):
            format = c.config.getString('log_timestamp_format') or "%H:%M:%S"
            timestamp = time.strftime(format) + ' '
        else:
            timestamp = ''
        if g.os_path_exists(at.targetFileName):
            if at.compareFiles(
                at.outputFileName,
                at.targetFileName,
                ignoreLineEndings=not at.explicitLineEnding,
                ignoreBlankLines=ignoreBlankLines
            ):
                # Files are identical.
                if trace: g.trace('files are identical')
                report = c.config.getBool('report_unchanged_files', default=True)
                at.sameFiles += 1
                if report and not g.unitTesting:
                    g.es('%sunchanged: %s' % (timestamp, at.shortFileName))
                at.fileChangedFlag = False
                # Leo 5.6: Check unchanged files.
                at.checkPythonCode(root, pyflakes_errors_only=True)
                return False
            else:
                # A mismatch. Report if the files differ only in line endings.
                if (
                    at.explicitLineEnding and
                    at.compareFiles(
                        at.outputFileName,
                        at.targetFileName,
                        ignoreLineEndings=True)
                ):
                    g.warning("correcting line endings in:", at.targetFileName)
                s = at.outputContents
                ok = at.create(at.targetFileName, s)
                if ok:
                    c.setFileTimeStamp(at.targetFileName)
                    if not g.unitTesting:
                        g.es('%swrote: %s' % (timestamp, at.shortFileName))
                else:
                    g.error('error writing', at.shortFileName)
                    g.es('not written:', at.shortFileName)
                    if root:
                        root.setDirty() # New in 4.4.8.
                        root.setOrphan() # 2010/10/22.
                at.checkPythonCode(root)
                    # Bug fix: check *after* writing the file.
                at.fileChangedFlag = ok
                return ok
        else:
            s = at.outputContents
            ok = self.create(at.targetFileName, s)
            if ok:
                c.setFileTimeStamp(at.targetFileName)
                if not g.unitTesting:
                    g.es('%screated: %s' % (timestamp, at.targetFileName))
                if root:
                    # Fix bug 889175: Remember the full fileName.
                    at.rememberReadPath(at.targetFileName, root)
            else:
                # at.rename gives the error.
                if root:
                    root.setDirty() # New in 4.4.8.
                    root.setOrphan() # 2010/10/22.
            # No original file to change. Return value tested by a unit test.
            at.fileChangedFlag = False
            at.checkPythonCode(root)
            return False
    #@+node:ekr.20041005105605.216: *5* at.warnAboutOrpanAndIgnoredNodes
    # Called from writeOpenFile.

    def warnAboutOrphandAndIgnoredNodes(self):
        # Always warn, even when language=="cweb"
        at, root = self, self.root
        if at.errors:
            return # No need to repeat this.
        for p in root.self_and_subtree():
            if not p.v.isVisited():
                at.writeError("Orphan node:  " + p.h)
                if p.hasParent():
                    g.blue("parent node:", p.parent().h)
        p = root.copy()
        after = p.nodeAfterTree()
        while p and p != after:
            if p.isAtAllNode():
                p.moveToNodeAfterTree()
            else:
                if p.isAtIgnoreNode():
                    at.writeError("@ignore node: " + p.h)
                p.moveToThreadNext()
    #@+node:ekr.20041005105605.217: *5* at.writeError
    def writeError(self, message=None):
        '''Issue an error while writing an @<file> node.'''
        at = self
        if at.errors == 0:
            g.es_error("errors writing: " + at.targetFileName)
        at.error(message)
        at.root.setDirty()
        at.root.setOrphan()
    #@+node:ekr.20041005105605.218: *5* at.writeException
    def writeException(self, root=None):
        at = self
        g.error("exception writing:", at.targetFileName)
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
    #@+node:ekr.20041005105605.219: *3* at.Utilites
    #@+node:ekr.20041005105605.220: *4* at.error & printError
    def error(self, *args):
        at = self
        if True: # args:
            at.printError(*args)
        at.errors += 1

    def printError(self, *args):
        '''Print an error message that may contain non-ascii characters.'''
        at = self
        if at.errors:
            g.error(*args)
        else:
            g.warning(*args)
    #@+node:ekr.20041005105605.221: *4* at.exception
    def exception(self, message):
        self.error(message)
        g.es_exception()
    #@+node:ekr.20050104131929: *4* at.file operations...
    #@+at The difference, if any, between these methods and the corresponding g.utils_x
    # functions is that these methods may call self.error.
    #@+node:ekr.20050104131820: *5* at.chmod
    def chmod(self, fileName, mode):
        # Do _not_ call self.error here.
        return g.utils_chmod(fileName, mode)
    #@+node:ekr.20130910100653.11323: *5* at.create
    def create(self, fn, s):
        '''Create a file whose contents are s.'''
        at = self
        # 2015/07/15: do this before converting to encoded string.
        if at.output_newline != '\n':
            s = s.replace('\r', '').replace('\n', at.output_newline)
        # This is part of the new_write logic.
        # This is the only call to g.toEncodedString in the new_write logic.
        # 2013/10/28: fix bug 1243847: unicode error when saving @shadow nodes
        if g.isUnicode(s):
            s = g.toEncodedString(s, encoding=at.encoding)
        try:
            f = open(fn, 'wb') # Must be 'wb' to preserve line endings.
            f.write(s)
            f.close()
        except Exception:
            f = None
            g.es_exception()
            g.error('error writing', fn)
            g.es('not written:', fn)
        return bool(f)
    #@+node:ekr.20050104131929.1: *5* at.rename
    #@+<< about os.rename >>
    #@+node:ekr.20050104131929.2: *6* << about os.rename >>
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

    def rename(self, src, dst, mode=None, verbose=True):
        '''
        Remove dst if it exists, then rename src to dst.
        Change the mode of the renamed file if mode is given.
        Return True if all went well.
        '''
        c = self.c
        head, junk = g.os_path_split(dst)
        if head:
            g.makeAllNonExistentDirectories(head, c=c)
        if g.os_path_exists(dst):
            if not self.remove(dst, verbose=verbose):
                return False
        try:
            os.rename(src, dst)
            if mode is not None:
                self.chmod(dst, mode)
            return True
        except Exception:
            if verbose:
                self.error("exception renaming: %s to: %s" % (
                    self.outputFileName, self.targetFileName))
                g.es_exception()
            return False
    #@+node:ekr.20050104132018: *5* at.remove
    def remove(self, fileName, verbose=True):
        if not fileName:
            g.trace('No file name', g.callers())
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
    #@+node:ekr.20050104132026: *5* at.stat
    def stat(self, fileName):
        '''Return the access mode of named file, removing any setuid, setgid, and sticky bits.'''
        # Do _not_ call self.error here.
        return g.utils_stat(fileName)
    #@+node:ekr.20090530055015.6023: *4* at.get/setPathUa
    def getPathUa(self, p):
        if hasattr(p.v, 'tempAttributes'):
            d = p.v.tempAttributes.get('read-path', {})
            return d.get('path')
        else:
            return ''

    def setPathUa(self, p, path):
        if not hasattr(p.v, 'tempAttributes'):
            p.v.tempAttributes = {}
        d = p.v.tempAttributes.get('read-path', {})
        d['path'] = path
        p.v.tempAttributes['read-path'] = d
    #@+node:ekr.20081216090156.4: *4* at.parseUnderindentTag
    # Important: this is part of the *write* logic.
    # It is called from at.os and at.putIndent.

    def parseUnderindentTag(self, s):
        tag = self.underindentEscapeString
        s2 = s[len(tag):]
        # To be valid, the escape must be followed by at least one digit.
        i = 0
        while i < len(s2) and s2[i].isdigit():
            i += 1
        if i > 0:
            n = int(s2[: i])
            # Bug fix: 2012/06/05: remove any period following the count.
            # This is a new convention.
            if i < len(s2) and s2[i] == '.':
                i += 1
            return n, s2[i:]
        else:
            return 0, s
    #@+node:ekr.20090712050729.6017: *4* at.promptForDangerousWrite
    def promptForDangerousWrite(self, fileName, kind, message=None):
        '''Raise a dialog asking the user whether to overwrite an existing file.'''
        trace = False and not g.unitTesting
        at, c, root = self, self.c, self.root
        if g.app.unitTesting:
            val = g.app.unitTestDict.get('promptForDangerousWrite')
            return val in (None, True)
        if at.cancelFlag:
            assert at.canCancelFlag
            return False
        if at.yesToAll:
            assert at.canCancelFlag
            return True
        if root and root.h.startswith('@auto-rst'):
            # Fix bug 50: body text lost switching @file to @auto-rst
            # Refuse to convert any @<file> node to @auto-rst.
            d = root.v.at_read if hasattr(root.v, 'at_read') else {}
            aList = sorted(d.get(fileName, []))
            for h in aList:
                if not h.startswith('@auto-rst'):
                    g.es('can not convert @file to @auto-rst!', color='red')
                    g.es('reverting to:', h)
                    root.h = h
                    c.redraw()
                    return False
        if message is None:
            message = '%s %s\n%s\n%s' % (
                kind, g.splitLongFileName(fileName),
                g.tr('already exists.'),
                g.tr('Overwrite this file?'))
        if trace: g.trace(c.shortFileName(), fileName, g.callers())
        result = g.app.gui.runAskYesNoCancelDialog(c,
            title='Overwrite existing file?',
            yesToAllMessage="Yes To &All",
            message=message,
            cancelMessage="&Cancel (No To All)",
        )
        if at.canCancelFlag:
            # We are in the writeAll logic so these flags can be set.
            if result == 'cancel':
                at.cancelFlag = True
            elif result == 'yes-to-all':
                at.yesToAll = True
        return result in ('yes', 'yes-to-all')
    #@+node:ekr.20120112084820.10001: *4* at.rememberReadPath
    def rememberReadPath(self, fn, p):
        '''
        Remember the files that have been read *and*
        the full headline (@<file> type) that caused the read.
        '''
        # g.trace(p.h,id(p.v),fn,g.callers())
        v = p.v
        # Fix bug #50: body text lost switching @file to @auto-rst
        if not hasattr(v, 'at_read'):
            v.at_read = {}
        d = v.at_read
        aSet = d.get(fn, set())
        aSet.add(p.h)
        d[fn] = aSet
    #@+node:ekr.20080923070954.4: *4* at.scanAllDirectives
    def scanAllDirectives(self,
        p,
        forcePythonSentinels=False,
        importing=False,
        issuePathWarning=False,
        reading=False,
    ):
        '''
        Scan p and p's ancestors looking for directives,
        setting corresponding AtFile ivars.
        '''
        trace = False and not g.unitTesting
        at, c = self, self.c
        g.app.atPathInBodyWarning = None
        #@+<< set ivars >>
        #@+node:ekr.20080923070954.14: *5* << Set ivars >> (at.scanAllDirectives)
        at.page_width = c.page_width
        at.tab_width = c.tab_width
        at.default_directory = None # 8/2: will be set later.
        if c.target_language:
            c.target_language = c.target_language.lower()
        delims = g.set_delims_from_language(c.target_language)
        at.language = c.target_language
        at.encoding = c.config.default_derived_file_encoding
        at.output_newline = g.getOutputNewline(c=c) # Init from config settings.
        #@-<< set ivars >>
        lang_dict = {'language': at.language, 'delims': delims,}
        table = (
            ('encoding', at.encoding, g.scanAtEncodingDirectives),
            # ('lang-dict',   lang_dict,      g.scanAtCommentAndAtLanguageDirectives),
            ('lang-dict', None, g.scanAtCommentAndAtLanguageDirectives),
            ('lineending', None, g.scanAtLineendingDirectives),
            ('pagewidth', c.page_width, g.scanAtPagewidthDirectives),
            ('path', None, c.scanAtPathDirectives),
            ('tabwidth', c.tab_width, g.scanAtTabwidthDirectives),
        )
        # Set d by scanning all directives.
        aList = g.get_directives_dict_list(p)
        d = {}
        for key, default, func in table:
            val = func(aList)
            d[key] = default if val is None else val
        # Post process.
        lineending = d.get('lineending')
        lang_dict = d.get('lang-dict')
        if lang_dict:
            delims = lang_dict.get('delims')
            at.language = lang_dict.get('language')
            if trace: g.trace('1', at.language, delims)
        else:
            # No language directive.  Look for @<file> nodes.
            language = g.getLanguageFromAncestorAtFileNode(p) or 'python'
            delims = g.set_delims_from_language(language)
            if trace: g.trace('2', repr(language), delims)
        at.encoding = d.get('encoding')
        at.explicitLineEnding = bool(lineending)
        at.output_newline = lineending or g.getOutputNewline(c=c)
        at.page_width = d.get('pagewidth')
        at.default_directory = d.get('path')
        at.tab_width = d.get('tabwidth')
        if not importing and not reading:
            # Don't override comment delims when reading!
            #@+<< set comment strings from delims >>
            #@+node:ekr.20080923070954.13: *5* << Set comment strings from delims >> (at.scanAllDirectives)
            if forcePythonSentinels:
                # Force Python language.
                delim1, delim2, delim3 = g.set_delims_from_language("python")
                self.language = "python"
            else:
                delim1, delim2, delim3 = delims
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
                # 2016/11/25: Issue an error only if at.language has been set.
                # This suppresses a message from the markdown importer.
                if not g.app.unitTesting and at.language:
                    g.trace(repr(at.language), g.callers())
                    g.es_print("unknown language: using Python comment delimiters")
                    g.es_print("c.target_language:", c.target_language)
                at.startSentinelComment = "#" # This should never happen!
                at.endSentinelComment = ""
            # g.trace(repr(self.startSentinelComment),repr(self.endSentinelComment))
            #@-<< set comment strings from delims >>
        # For unit testing.
        d = {
            "all": all,
            "encoding": at.encoding,
            "language": at.language,
            "lineending": at.output_newline,
            "pagewidth": at.page_width,
            "path": at.default_directory,
            "tabwidth": at.tab_width,
        }
        if trace:
            # g.trace('forcePythonSentinels', forcePythonSentinels)
            g.trace('returns', d.get('language'), p.h, g.callers())
        return d
    #@+node:ekr.20041005105605.242: *4* at.scanForClonedSibs (reading & writing)
    def scanForClonedSibs(self, parent_v, v):
        """Scan the siblings of VNode v looking for clones of v.
        Return the number of cloned sibs and n where p is the n'th cloned sibling."""
        clonedSibs = 0 # The number of cloned siblings of p, including p.
        thisClonedSibIndex = 0 # Position of p in list of cloned siblings.
        if v and v.isCloned():
            for sib in parent_v.children:
                if sib == v:
                    clonedSibs += 1
                    if sib == v:
                        thisClonedSibIndex = clonedSibs
        return clonedSibs, thisClonedSibIndex
    #@+node:ekr.20041005105605.243: *4* at.sentinelName
    #@@nobeautify

    def sentinelName(self, kind):
        '''Returns the name of the sentinel for warnings..'''
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
    #@+node:ekr.20120110174009.9965: *4* at.shouldPromptForDangerousWrite
    def shouldPromptForDangerousWrite(self, fn, p):
        '''
        Return True if a prompt should be issued
        when writing p (an @<file> node) to fn.
        '''
        trace = False and not g.unitTesting
        if not g.os_path_exists(fn):
            # No danger of overwriting fn.
            return False
        elif hasattr(p.v, 'at_read'):
            # Fix bug #50: body text lost switching @file to @auto-rst
            d = p.v.at_read
            if trace: g.trace(fn, p.h, '\n d:', d, '\n', g.callers())
            aSet = d.get(fn, set())
            return p.h not in aSet
        else:
            return True
                # The file was never read.
    #@+node:ekr.20041005105605.20: *4* at.warnOnReadOnlyFile
    def warnOnReadOnlyFile(self, fn):
        # os.access() may not exist on all platforms.
        try:
            read_only = not os.access(fn, os.W_OK)
        except AttributeError:
            read_only = False
        if read_only:
            g.error("read only:", fn)
    #@-others

atFile = AtFile # compatibility
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo

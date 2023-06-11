#@+leo-ver=5-thin
#@+node:ekr.20150323150718.1: * @file leoAtFile.py
"""Classes to read and write @file nodes."""
#@+<< leoAtFile imports & annotations >>
#@+node:ekr.20041005105605.2: ** << leoAtFile imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import io
import os
import re
import sys
import tabnanny
import time
import tokenize
from typing import Any, Optional, Union, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoNodes

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode
#@-<< leoAtFile imports & annotations >>

#@+others
#@+node:ekr.20150509194251.1: ** cmd (decorator)
def cmd(name: str) -> Callable:  # pragma: no cover
    """Command decorator for the AtFileCommands class."""
    return g.new_cmd_decorator(name, ['c', 'atFileCommands'])
#@+node:ekr.20160514120655.1: ** class AtFile
class AtFile:
    """A class implementing the atFile subcommander."""
    #@+<< define class constants >>
    #@+node:ekr.20131224053735.16380: *3* << define class constants >>
    #@@nobeautify

    # directives...
    noDirective     =  1  # not an at-directive.
    allDirective    =  2  # at-all (4.2)
    docDirective    =  3  # @doc.
    atDirective     =  4  # @<space> or @<newline>
    codeDirective   =  5  # @code
    cDirective      =  6  # @c<space> or @c<newline>
    othersDirective =  7  # at-others
    miscDirective   =  8  # All other directives
    startVerbatim   =  9  # @verbatim  Not a real directive. Used to issue warnings.
    #@-<< define class constants >>
    #@+others
    #@+node:ekr.20041005105605.7: *3* at.Birth & init
    #@+node:ekr.20041005105605.8: *4* at.ctor & helpers
    # Note: g.getScript also call the at.__init__ and at.finishCreate().

    def __init__(self, c: Cmdr) -> None:
        """ctor for atFile class."""
        # **Warning**: all these ivars must **also** be inited in initCommonIvars.
        self.c: Cmdr = c
        self.encoding = 'utf-8'  # 2014/08/13
        self.fileCommands = c.fileCommands
        self.errors = 0  # Make sure at.error() works even when not inited.
        # #2276: allow different section delims.
        self.section_delim1 = '<<'
        self.section_delim2 = '>>'
        # **Only** at.writeAll manages these flags.
        self.unchangedFiles = 0
        # promptForDangerousWrite sets cancelFlag and yesToAll only if canCancelFlag is True.
        self.canCancelFlag = False
        self.cancelFlag = False
        self.yesToAll = False
        # User options: set in reloadSettings.
        self.checkPythonCodeOnWrite = False
        self.runFlake8OnWrite = False
        self.runPyFlakesOnWrite = False
        self.reloadSettings()
    #@+node:ekr.20171113152939.1: *5* at.reloadSettings
    def reloadSettings(self) -> None:
        """AtFile.reloadSettings"""
        c = self.c
        self.checkPythonCodeOnWrite = c.config.getBool(
            'check-python-code-on-write', default=True)
        self.runFlake8OnWrite = c.config.getBool(
            'run-flake8-on-write', default=False)
        self.runPyFlakesOnWrite = c.config.getBool(
            'run-pyflakes-on-write', default=False)
    #@+node:ekr.20041005105605.10: *4* at.initCommonIvars
    def initCommonIvars(self) -> None:
        """
        Init ivars common to both reading and writing.

        The defaults set here may be changed later.
        """
        c = self.c
        self.at_auto_encoding = c.config.default_at_auto_file_encoding
        self.encoding = c.config.default_derived_file_encoding
        self.endSentinelComment = ""
        self.errors = 0
        self.inCode = True
        self.indent = 0  # The unit of indentation is spaces, not tabs.
        self.language: str = None
        self.output_newline = g.getOutputNewline(c=c)
        self.page_width: int = None
        self.root: Position = None  # The root (a position) of tree being read or written.
        self.startSentinelComment = ""
        self.endSentinelComment = ""
        self.tab_width: int = c.tab_width or -4
        self.writing_to_shadow_directory = False
    #@+node:ekr.20041005105605.13: *4* at.initReadIvars
    def initReadIvars(self, root: Position, fileName: str) -> None:

        self.initCommonIvars()
        self.bom_encoding = None  # The encoding implied by any BOM (set by g.stripBOM)
        self.cloneSibCount = 0  # n > 1: Make sure n cloned sibs exists at next @+node sentinel
        self.correctedLines = 0  # For perfect import.
        self.docOut: list[str] = []  # The doc part being accumulated.
        self.done = False  # True when @-leo seen.
        self.fromString = ''
        self.importRootSeen = False
        self.lastLines: list[str] = []  # The lines after @-leo
        self.leadingWs = ""
        self.lineNumber = 0  # New in Leo 4.4.8.
        self.read_i = 0
        self.read_lines: list[str] = []
        self.readVersion = ''  # "5" for new-style thin files.
        self.readVersion5 = False  # Synonym for self.readVersion >= '5'
        self.root = root
        self.rootSeen = False
        self.targetFileName = fileName  # For self.writeError only.
        self.v = None
        self.updateWarningGiven = False
    #@+node:ekr.20041005105605.15: *4* at.initWriteIvars
    def initWriteIvars(self, root: Position) -> Optional[str]:
        """
        Compute default values of all write-related ivars.
        Return the finalized name of the output file.
        """
        at, c = self, self.c
        if not c or not c.config:
            return None  # pragma: no cover
        make_dirs = c.config.getBool('create-nonexistent-directories', default=False)
        assert root
        self.initCommonIvars()
        assert at.checkPythonCodeOnWrite is not None
        #
        # Copy args
        at.root = root
        at.sentinels = True
        #
        # Override initCommonIvars.
        if g.unitTesting:
            at.output_newline = '\n'
        #
        # Set other ivars.
        at.force_newlines_in_at_nosent_bodies = c.config.getBool(
            'force-newlines-in-at-nosent-bodies')
            # For at.putBody only.
        at.outputList = []  # For stream output.
        # Sets the following ivars:
        # at.encoding
        # at.explicitLineEnding
        # at.language
        # at.output_newline
        # at.page_width
        # at.tab_width
        at.scanAllDirectives(root)
        #
        # Overrides of at.scanAllDirectives...
        if at.language == 'python':
            # Encoding directive overrides everything else.
            encoding = g.getPythonEncodingFromString(root.b)
            if encoding:
                at.encoding = encoding
        #
        # Clean root.v.
        if not at.errors and at.root:
            at.root.v._p_changed = True
        #
        # #1907: Compute the file name and create directories as needed.
        targetFileName = g.os_path_realpath(c.fullPath(root))
        at.targetFileName = targetFileName  # For at.writeError only.
        #
        # targetFileName can be empty for unit tests & @command nodes.
        if not targetFileName:  # pragma: no cover
            targetFileName = root.h if g.unitTesting else None
            at.targetFileName = targetFileName  # For at.writeError only.
            return targetFileName
        #
        # #2276: scan for section delims
        at.scanRootForSectionDelims(root)
        #
        # Do nothing more if the file already exists.
        if os.path.exists(targetFileName):
            return targetFileName
        #
        # Create directories if enabled.
        root_dir = g.os_path_dirname(targetFileName)
        if make_dirs and root_dir:  # pragma: no cover
            ok = g.makeAllNonExistentDirectories(root_dir)
            if not ok:
                g.error(f"Error creating directories: {root_dir}")
                return None
        #
        # Return the target file name, regardless of future problems.
        return targetFileName
    #@+node:ekr.20041005105605.17: *3* at.Reading
    #@+node:ekr.20041005105605.18: *4* at.Reading (top level)
    #@+node:ekr.20070919133659: *5* at.checkExternalFile
    @cmd('check-external-file')
    def checkExternalFile(self, event: Event = None) -> None:  # pragma: no cover
        """Make sure an external file written by Leo may be read properly."""
        c, p = self.c, self.c.p
        if not p.isAtFileNode() and not p.isAtThinFileNode():
            g.red('Please select an @thin or @file node')
            return
        fn = c.fullPath(p)  # #1910.
        if not g.os_path_exists(fn):
            g.red(f"file not found: {fn}")
            return
        s, e = g.readFileIntoString(fn)
        if s is None:
            g.red(f"empty file: {fn}")
            return
        #
        # Create a dummy, unconnected, VNode as the root.
        root_v = leoNodes.VNode(context=c)
        root = leoNodes.Position(root_v)
        FastAtRead(c, gnx2vnode={}).read_into_root(s, fn, root)
    #@+node:ekr.20041005105605.19: *5* at.openFileForReading & helper
    def openFileForReading(self, fromString: str = None) -> Union[tuple[str, str], tuple[None, None]]:
        """
        Open the file given by at.root.
        This will be the private file for @shadow nodes.
        """
        at, c = self, self.c
        is_at_shadow = self.root.isAtShadowFileNode()
        if fromString:  # pragma: no cover
            if is_at_shadow:  # pragma: no cover
                at.error('can not call at.read from string for @shadow files')
                return None, None
            at.initReadLine(fromString)
            return None, None
        #
        # Not from a string. Carefully read the file.
        # Returns full path, including file name.
        fn = g.fullPath(c, at.root)
        # Remember the full path to this node.
        at.setPathUa(at.root, fn)
        if is_at_shadow:  # pragma: no cover
            fn = at.openAtShadowFileForReading(fn)
            if not fn:
                return None, None
        assert fn
        try:
            # Sets at.encoding, regularizes whitespace and calls at.initReadLines.
            s = at.readFileToUnicode(fn)
            # #1466.
            if s is None:  # pragma: no cover
                # The error has been given.
                at._file_bytes = g.toEncodedString('')
                return None, None
            at.warnOnReadOnlyFile(fn)
        except Exception:  # pragma: no cover
            at.error(f"unexpected exception opening: '@file {fn}'")
            at._file_bytes = g.toEncodedString('')
            fn, s = None, None
        return fn, s
    #@+node:ekr.20150204165040.4: *6* at.openAtShadowFileForReading
    def openAtShadowFileForReading(self, fn: str) -> Optional[str]:  # pragma: no cover
        """Open an @shadow for reading and return shadow_fn."""
        at = self
        x = at.c.shadowController
        # readOneAtShadowNode should already have checked these.
        shadow_fn = x.shadowPathName(fn)
        shadow_exists = (g.os_path_exists(shadow_fn) and g.os_path_isfile(shadow_fn))
        if not shadow_exists:
            g.trace('can not happen: no private file',
                shadow_fn, g.callers())
            at.error(f"can not happen: private file does not exist: {shadow_fn}")
            return None
        # This method is the gateway to the shadow algorithm.
        x.updatePublicAndPrivateFiles(at.root, fn, shadow_fn)
        return shadow_fn
    #@+node:ekr.20041005105605.21: *5* at.read & helpers
    def read(self, root: Position, fromString: str = None) -> bool:
        """Read an @thin or @file tree."""
        at, c = self, self.c
        fileName = c.fullPath(root)
        if not fileName:  # pragma: no cover
            at.error("Missing file name. Restoring @file tree from .leo file.")
            return False
        # Fix bug 760531: always mark the root as read, even if there was an error.
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(c.fullPath(root), root)
        at.initReadIvars(root, fileName)
        at.fromString = fromString
        if at.errors:
            return False  # pragma: no cover
        fileName, file_s = at.openFileForReading(fromString=fromString)
        # #1798:
        if file_s is None:
            return False  # pragma: no cover
        #
        # Set the time stamp.
        if fileName:
            c.setFileTimeStamp(fileName)
        elif not fileName and not fromString and not file_s:  # pragma: no cover
            return False
        root.clearVisitedInTree()
        # Sets the following ivars:
        # at.encoding: **changed later** by readOpenFile/at.scanHeader.
        # at.explicitLineEnding
        # at.language
        # at.output_newline
        # at.page_width
        # at.tab_width
        at.scanAllDirectives(root)
        gnx2vnode = c.fileCommands.gnxDict
        contents = fromString or file_s
        FastAtRead(c, gnx2vnode).read_into_root(contents, fileName, root)
        root.clearDirty()
        return True
    #@+node:ekr.20071105164407: *6* at.deleteUnvisitedNodes
    def deleteUnvisitedNodes(self, root: Position) -> None:  # pragma: no cover
        """
        Delete unvisited nodes in root's subtree, not including root.

        Before Leo 5.6: Move unvisited node to be children of the 'Resurrected
        Nodes'.
        """
        at, c = self, self.c
        # Find the unvisited nodes.
        aList = [z for z in root.subtree() if not z.isVisited()]
        if aList:
            at.c.deletePositionsInList(aList)
            c.redraw()

    #@+node:ekr.20041005105605.26: *5* at.readAll & helpers
    def readAll(self, root: Position) -> None:
        """Scan positions, looking for @<file> nodes to read."""
        at, c = self, self.c
        old_changed = c.changed
        t1 = time.time()
        c.init_error_dialogs()
        files = at.findFilesToRead(root, all=True)
        for p in files:
            at.readFileAtPosition(p)
        for p in files:
            p.v.clearDirty()
        if not g.unitTesting and files:  # pragma: no cover
            t2 = time.time()
            g.es(f"read {len(files)} files in {t2 - t1:2.2f} seconds")
        c.changed = old_changed
        c.raise_error_dialogs()
    #@+node:ekr.20190108054317.1: *6* at.findFilesToRead
    def findFilesToRead(self, root: Position, all: bool) -> list[Position]:  # pragma: no cover

        c = self.c
        p = root.copy()
        scanned_nodes: set[tuple[str, str]] = set()
        files: list[Position] = []
        after = None if all else p.nodeAfterTree()
        while p and p != after:
            data = (p.gnx, c.fullPath(p))
            # skip clones referring to exactly the same paths.
            if data in scanned_nodes:
                p.moveToNodeAfterTree()
                continue
            scanned_nodes.add(data)
            if not p.h.startswith('@'):
                p.moveToThreadNext()
            elif p.isAtIgnoreNode():
                if p.isAnyAtFileNode():
                    c.ignored_at_file_nodes.append(p.h)
                p.moveToNodeAfterTree()
            elif (
                p.isAtThinFileNode() or
                p.isAtAutoNode() or
                p.isAtEditNode() or
                p.isAtShadowFileNode() or
                p.isAtFileNode() or
                p.isAtCleanNode()  # 1134.
            ):
                files.append(p.copy())
                p.moveToNodeAfterTree()
            elif p.isAtAsisFileNode() or p.isAtNoSentFileNode():
                # Note (see #1081): @asis and @nosent can *not* be updated automatically.
                # Doing so using refresh-from-disk will delete all child nodes.
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        return files
    #@+node:ekr.20190108054803.1: *6* at.readFileAtPosition
    def readFileAtPosition(self, p: Position) -> None:  # pragma: no cover
        """Read the @<file> node at p."""
        at, c, fileName = self, self.c, p.anyAtFileNodeName()
        if p.isAtThinFileNode() or p.isAtFileNode():
            at.read(p)
        elif p.isAtAutoNode():
            at.readOneAtAutoNode(p)
        elif p.isAtEditNode():
            at.readOneAtEditNode(fileName, p)
        elif p.isAtShadowFileNode():
            at.readOneAtShadowNode(fileName, p)
        elif p.isAtAsisFileNode() or p.isAtNoSentFileNode():
            at.rememberReadPath(c.fullPath(p), p)
        elif p.isAtCleanNode():
            at.readOneAtCleanNode(p)
    #@+node:ekr.20220121052056.1: *5* at.readAllSelected
    def readAllSelected(self, root: Position) -> None:  # pragma: no cover
        """Read all @<file> nodes in root's tree."""
        at, c = self, self.c
        old_changed = c.changed
        t1 = time.time()
        c.init_error_dialogs()
        files = at.findFilesToRead(root, all=False)
        for p in files:
            at.readFileAtPosition(p)
        for p in files:
            p.v.clearDirty()
        if not g.unitTesting:  # pragma: no cover
            if files:
                t2 = time.time()
                g.es(f"read {len(files)} files in {t2 - t1:2.2f} seconds")
            else:
                g.es("no @<file> nodes in the selected tree")
        c.changed = old_changed
        c.raise_error_dialogs()
    #@+node:ekr.20080801071227.7: *5* at.readAtShadowNodes
    def readAtShadowNodes(self, p: Position) -> None:  # pragma: no cover
        """Read all @shadow nodes in the p's tree."""
        at = self
        after = p.nodeAfterTree()
        p = p.copy()  # Don't change p in the caller.
        while p and p != after:  # Don't use iterator.
            if p.isAtShadowFileNode():
                fileName = p.atShadowFileNodeName()
                at.readOneAtShadowNode(fileName, p)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20070909100252: *5* at.readOneAtAutoNode
    def readOneAtAutoNode(self, p: Position) -> Position:  # pragma: no cover
        """Read an @auto file into p. Return the *new* position."""
        at, c, ic = self, self.c, self.c.importCommands
        fileName = c.fullPath(p)
        if not g.os_path_exists(fileName):
            g.error(f"not found: {p.h!r}", nodeLink=p.get_UNL())
            return p
        # Remember that we have seen the @auto node.
        # #889175: Remember the full fileName.
        at.rememberReadPath(fileName, p)
        old_p = p.copy()
        try:
            at.scanAllDirectives(p)
            p.v.b = ''  # Required for @auto API checks.
            p.v._deleteAllChildren()
            p = ic.createOutline(parent=p.copy())
            # Do *not* call c.selectPosition(p) here.
            # That would improperly expand nodes.
        except Exception:
            p = old_p
            ic.errors += 1
            g.es_print('Unexpected exception importing', fileName)
            g.es_exception()
        if ic.errors:
            g.error(f"errors inhibited read @auto {fileName}")
        elif c.persistenceController:
            c.persistenceController.update_after_read_foreign_file(p)
        # Finish.
        if ic.errors or not g.os_path_exists(fileName):
            p.clearDirty()
        else:
            g.doHook('after-auto', c=c, p=p)
        return p  # For #451: return p.
    #@+node:ekr.20090225080846.3: *5* at.readOneAtEditNode
    def readOneAtEditNode(self, fn: str, p: Position) -> None:  # pragma: no cover
        at = self
        c = at.c
        ic = c.importCommands
        # #1521
        fn = c.fullPath(p)
        junk, ext = g.os_path_splitext(fn)
        # Fix bug 889175: Remember the full fileName.
        at.rememberReadPath(fn, p)
        # if not g.unitTesting: g.es("reading: @edit %s" % (g.shortFileName(fn)))
        s, e = g.readFileIntoString(fn, kind='@edit')
        if s is None:
            return
        encoding = 'utf-8' if e is None else e
        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()
        head = ''
        ext = ext.lower()
        if ext in ('.html', '.htm'):
            head = '@language html\n'
        elif ext in ('.txt', '.text'):
            head = '@nocolor\n'
        else:
            language = ic.languageForExtension(ext)
            if language and language != 'unknown_language':
                head = f"@language {language}\n"
            else:
                head = '@nocolor\n'
        p.b = head + g.toUnicode(s, encoding=encoding, reportErrors=True)
        g.doHook('after-edit', p=p)
    #@+node:ekr.20190201104956.1: *5* at.readOneAtAsisNode
    def readOneAtAsisNode(self, fn: str, p: Position) -> None:  # pragma: no cover
        """Read one @asis node. Used only by refresh-from-disk"""
        at, c = self, self.c
        fn = c.fullPath(p)
        junk, ext = g.os_path_splitext(fn)
        # Remember the full fileName.
        at.rememberReadPath(fn, p)
        # if not g.unitTesting: g.es("reading: @asis %s" % (g.shortFileName(fn)))
        s, e = g.readFileIntoString(fn, kind='@edit')
        if s is None:
            return
        encoding = 'utf-8' if e is None else e
        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()
        old_body = p.b
        p.b = g.toUnicode(s, encoding=encoding, reportErrors=True)
        if not c.isChanged() and p.b != old_body:
            c.setChanged()
    #@+node:ekr.20150204165040.5: *5* at.readOneAtCleanNode & helpers
    def readOneAtCleanNode(self, root: Position) -> bool:  # pragma: no cover
        """Update the @clean/@nosent node at root."""
        at, c, x = self, self.c, self.c.shadowController
        fileName = c.fullPath(root)
        if not g.os_path_exists(fileName):
            g.es_print(f"not found: {fileName}", color='red', nodeLink=root.get_UNL())
            return False
        at.rememberReadPath(fileName, root)
        # Must be called before at.scanAllDirectives.
        at.initReadIvars(root, fileName)
        # Sets at.startSentinelComment/endSentinelComment.
        at.scanAllDirectives(root)
        new_public_lines = at.read_at_clean_lines(fileName)
        old_private_lines = self.write_at_clean_sentinels(root)
        marker = x.markerFromFileLines(old_private_lines, fileName)
        old_public_lines, junk = x.separate_sentinels(old_private_lines, marker)
        if old_public_lines:
            new_private_lines = x.propagate_changed_lines(
                new_public_lines, old_private_lines, marker, p=root)
        else:
            new_private_lines = []
            root.b = ''.join(new_public_lines)
            return True
        if new_private_lines == old_private_lines:
            return True
        if not g.unitTesting:
            g.es("updating:", root.h)
        root.clearVisitedInTree()
        gnx2vnode = at.fileCommands.gnxDict
        contents = ''.join(new_private_lines)
        FastAtRead(c, gnx2vnode).read_into_root(contents, fileName, root)
        return True  # Errors not detected.
    #@+node:ekr.20150204165040.7: *6* at.dump_lines
    def dump(self, lines: list[str], tag: Any) -> None:  # pragma: no cover
        """Dump all lines."""
        print(f"***** {tag} lines...\n")
        for s in lines:
            print(s.rstrip())
    #@+node:ekr.20150204165040.8: *6* at.read_at_clean_lines
    def read_at_clean_lines(self, fn: str) -> list[str]:  # pragma: no cover
        """Return all lines of the @clean/@nosent file at fn."""
        at = self
        # Use the standard helper. Better error reporting.
        # Important: uses 'rb' to open the file.
        s: str
        s_bytes: bytes = at.openFileHelper(fn)
        # #1798.
        if not s_bytes:
            s = ''
        else:
            s = g.toUnicode(s_bytes, encoding=at.encoding)
            s = s.replace('\r\n', '\n')  # Suppress meaningless "node changed" messages.
        return g.splitLines(s)
    #@+node:ekr.20150204165040.9: *6* at.write_at_clean_sentinels
    def write_at_clean_sentinels(self, root: Position) -> list[str]:  # pragma: no cover
        """
        Return all lines of the @clean tree as if it were
        written as an @file node.
        """
        at = self
        result = at.atFileToString(root, sentinels=True)
        s = g.toUnicode(result, encoding=at.encoding)
        return g.splitLines(s)
    #@+node:ekr.20080711093251.7: *5* at.readOneAtShadowNode & helper
    def readOneAtShadowNode(self, fn: str, p: Position) -> None:  # pragma: no cover

        at, c = self, self.c
        x = c.shadowController
        if not fn == p.atShadowFileNodeName():
            at.error(
                f"can not happen: fn: {fn} != atShadowNodeName: "
                f"{p.atShadowFileNodeName()}")
            return
        fn = c.fullPath(p)
        # #889175: Remember the full fileName.
        at.rememberReadPath(fn, p)
        shadow_fn = x.shadowPathName(fn)
        shadow_exists = g.os_path_exists(shadow_fn) and g.os_path_isfile(shadow_fn)
        # Delete all children.
        while p.hasChildren():
            p.firstChild().doDelete()
        if shadow_exists:
            at.read(p)
        else:
            ok = at.importAtShadowNode(p)
            if ok:
                # Create the private file automatically.
                at.writeOneAtShadowNode(p)
    #@+node:ekr.20080712080505.1: *6* at.importAtShadowNode
    def importAtShadowNode(self, p: Position) -> bool:  # pragma: no cover
        c, ic = self.c, self.c.importCommands
        fn = c.fullPath(p)
        if not g.os_path_exists(fn):
            g.error(f"not found: {p.h!r}", nodeLink=p.get_UNL())
            return False
        # Delete all the child nodes.
        while p.hasChildren():
            p.firstChild().doDelete()
        # Import the outline, exactly as @auto does.
        ic.createOutline(parent=p.copy())
        if ic.errors:
            g.error('errors inhibited read @shadow', fn)
        if ic.errors or not g.os_path_exists(fn):
            p.clearDirty()
        return ic.errors == 0
    #@+node:ekr.20180622110112.1: *4* at.fast_read_into_root
    def fast_read_into_root(self,
        c: Cmdr,
        contents: str,
        gnx2vnode: dict[str, VNode],
        path: str, root: Position,
    ) -> bool:  # pragma: no cover
        """A convenience wrapper for FastAtRead.read_into_root()"""
        return FastAtRead(c, gnx2vnode).read_into_root(contents, path, root)
    #@+node:ekr.20041005105605.116: *4* at.Reading utils...
    #@+node:ekr.20041005105605.119: *5* at.createImportedNode
    def createImportedNode(self, root: Position, headline: str) -> Position:  # pragma: no cover
        at = self
        if at.importRootSeen:
            p = root.insertAsLastChild()
            p.initHeadString(headline)
        else:
            # Put the text into the already-existing root node.
            p = root
            at.importRootSeen = True
        p.v.setVisited()  # Suppress warning about unvisited node.
        return p
    #@+node:ekr.20130911110233.11286: *5* at.initReadLine
    def initReadLine(self, s: str) -> None:
        """Init the ivars so that at.readLine will read all of s."""
        at = self
        at.read_i = 0
        at.read_lines = g.splitLines(s)
        at._file_bytes = g.toEncodedString(s)
    #@+node:ekr.20041005105605.120: *5* at.parseLeoSentinel
    def parseLeoSentinel(self, s: str) -> tuple[bool, bool, str, str, bool]:
        """
        Parse the sentinel line s.
        If the sentinel is valid, set at.encoding, at.readVersion, at.readVersion5.
        """
        at, c = self, self.c
        # Set defaults.
        encoding = c.config.default_derived_file_encoding
        readVersion, readVersion5 = None, None
        new_df, start, end, isThin = False, '', '', False
        # Example: \*@+leo-ver=5-thin-encoding=utf-8,.*/
        pattern = re.compile(
            r'(.+)@\+leo(-ver=([0123456789]+))?(-thin)?(-encoding=(.*)(\.))?(.*)')
            # The old code weirdly allowed '.' in version numbers.
            # group 1: opening delim
            # group 2: -ver=
            # group 3: version number
            # group(4): -thin
            # group(5): -encoding=utf-8,.
            # group(6): utf-8,
            # group(7): .
            # group(8): closing delim.
        m = pattern.match(s)
        valid = bool(m)
        if valid:
            start = m.group(1)  # start delim
            valid = bool(start)
        if valid:
            new_df = bool(m.group(2))  # -ver=
            if new_df:
                # Set the version number.
                if m.group(3):
                    readVersion = m.group(3)
                    readVersion5 = readVersion >= '5'
                else:
                    valid = False  # pragma: no cover
        if valid:
            # set isThin
            isThin = bool(m.group(4))
        if valid and m.group(5):
            # set encoding.
            encoding = m.group(6)
            if encoding and encoding.endswith(','):
                # Leo 4.2 or after.
                encoding = encoding[:-1]
            if not g.isValidEncoding(encoding):  # pragma: no cover
                g.es_print("bad encoding in derived file:", encoding)
                valid = False
        if valid:
            end = m.group(8)  # closing delim
        if valid:
            at.encoding = encoding
            at.readVersion = readVersion
            at.readVersion5 = readVersion5
        return valid, new_df, start, end, isThin
    #@+node:ekr.20130911110233.11284: *5* at.readFileToUnicode & helpers
    def readFileToUnicode(self, fileName: str) -> Optional[str]:  # pragma: no cover
        """
        Carefully sets at.encoding, then uses at.encoding to convert the file
        to a unicode string.

        Sets at.encoding as follows:
        1. Use the BOM, if present. This unambiguously determines the encoding.
        2. Use the -encoding= field in the @+leo header, if present and valid.
        3. Otherwise, uses existing value of at.encoding, which comes from:
            A. An @encoding directive, found by at.scanAllDirectives.
            B. The value of c.config.default_derived_file_encoding.

        Returns the string, or None on failure.
        """
        at = self
        s: str
        s_bytes = at.openFileHelper(fileName)  # Catches all exceptions.
        # #1798.
        if not s_bytes:
            return None  # Not ''.
        e, s_bytes = g.stripBOM(s_bytes)
        if e:
            # The BOM determines the encoding unambiguously.
            s = g.toUnicode(s_bytes, encoding=e)
        else:
            # Get the encoding from the header, or the default encoding.
            s_temp = g.toUnicode(s_bytes, 'ascii', reportErrors=False)
            e = at.getEncodingFromHeader(fileName, s_temp)
            s = g.toUnicode(s_bytes, encoding=e)
        s = s.replace('\r\n', '\n')
        at.encoding = e
        at.initReadLine(s)
        return s
    #@+node:ekr.20130911110233.11285: *6* at.openFileHelper
    def openFileHelper(self, fileName: str) -> bytes:  # *not* str!
        """Open a file, reporting all exceptions."""
        at = self
        # #1798: return None as a flag on any error.
        s = None
        try:
            with open(fileName, 'rb') as f:
                s = f.read()
        except IOError:  # pragma: no cover
            at.error(f"can not open {fileName}")
        except Exception:  # pragma: no cover
            at.error(f"Exception reading {fileName}")
            g.es_exception()
        return s
    #@+node:ekr.20130911110233.11287: *6* at.getEncodingFromHeader
    def getEncodingFromHeader(self, fileName: str, s: str) -> str:
        """
        Return the encoding given in the @+leo sentinel, if the sentinel is
        present, or the previous value of at.encoding otherwise.
        """
        at = self
        if at.errors:  # pragma: no cover
            g.trace('can not happen: at.errors > 0', g.callers())
            e = at.encoding
            if g.unitTesting:
                assert False, g.callers()  # noqa
        else:
            at.initReadLine(s)
            old_encoding = at.encoding
            assert old_encoding
            at.encoding = None
            # Execute scanHeader merely to set at.encoding.
            at.scanHeader(fileName, giveErrors=False)
            e = at.encoding or old_encoding
        assert e
        return e
    #@+node:ekr.20041005105605.128: *5* at.readLine
    def readLine(self) -> str:
        """
        Read one line from file using the present encoding.
        Returns at.read_lines[at.read_i++]
        """
        # This is an old interface, now used only by at.scanHeader.
        # For now, it's not worth replacing.
        at = self
        if at.read_i < len(at.read_lines):
            s = at.read_lines[at.read_i]
            at.read_i += 1
            return s
        # Not an error.
        return ''  # pragma: no cover
    #@+node:ekr.20041005105605.129: *5* at.scanHeader
    def scanHeader(self, fileName: str, giveErrors: bool = True) -> tuple[list[str], bool, bool]:
        """
        Scan the @+leo sentinel, using the old readLine interface.

        Sets self.encoding, and self.start/endSentinelComment.

        Returns (firstLines,new_df,isThinDerivedFile) where:
        firstLines        contains all @first lines,
        new_df            is True if we are reading a new-format derived file.
        isThinDerivedFile is True if the file is an @thin file.
        """
        at = self
        new_df, isThinDerivedFile = False, False
        firstLines: list[str] = []  # The lines before @+leo.
        s = self.scanFirstLines(firstLines)
        valid = len(s) > 0
        if valid:
            valid, new_df, start, end, isThinDerivedFile = at.parseLeoSentinel(s)
        if valid:
            at.startSentinelComment = start
            at.endSentinelComment = end
        elif giveErrors:  # pragma: no cover
            at.error(f"No @+leo sentinel in: {fileName}")
            g.trace(g.callers())
        return firstLines, new_df, isThinDerivedFile
    #@+node:ekr.20041005105605.130: *6* at.scanFirstLines
    def scanFirstLines(self, firstLines: list[str]) -> str:  # pragma: no cover
        """
        Append all lines before the @+leo line to firstLines.

        Empty lines are ignored because empty @first directives are
        ignored.

        We can not call sentinelKind here because that depends on the comment
        delimiters we set here.
        """
        at = self
        s = at.readLine()
        while s and s.find("@+leo") == -1:
            firstLines.append(s)
            s = at.readLine()
        return s
    #@+node:ekr.20050103163224: *5* at.scanHeaderForThin (import code)
    def scanHeaderForThin(self, fileName: str) -> bool:  # pragma: no cover
        """
        Return true if the derived file is a thin file.

        This is a kludgy method used only by the import code."""
        at = self
        # Set at.encoding, regularize whitespace and call at.initReadLines.
        at.readFileToUnicode(fileName)
        # scanHeader uses at.readline instead of its args.
        # scanHeader also sets at.encoding.
        junk1, junk2, isThin = at.scanHeader(None)
        return isThin
    #@+node:ekr.20041005105605.132: *3* at.Writing
    #@+node:ekr.20041005105605.133: *4* Writing (top level)
    #@+node:ekr.20190111153551.1: *5* at.commands
    #@+node:ekr.20070806105859: *6* at.writeAtAutoNodes
    @cmd('write-at-auto-nodes')
    def writeAtAutoNodes(self, event: Event = None) -> None:  # pragma: no cover
        """Write all @auto nodes in the selected outline."""
        at, c, p = self, self.c, self.c.p
        c.init_error_dialogs()
        after, found = p.nodeAfterTree(), False
        while p and p != after:
            if p.isAtAutoNode() and not p.isAtIgnoreNode():
                ok = at.writeOneAtAutoNode(p)
                if ok:
                    found = True
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()
        if g.unitTesting:
            return
        if found:
            g.es("finished")
        else:
            g.es("no @auto nodes in the selected tree")
        c.raise_error_dialogs(kind='write')

    #@+node:ekr.20220120072251.1: *6* at.writeDirtyAtAutoNodes
    @cmd('write-dirty-at-auto-nodes')  # pragma: no cover
    def writeDirtyAtAutoNodes(self, event: Event = None) -> None:
        """Write all dirty @auto nodes in the selected outline."""
        at, c, p = self, self.c, self.c.p
        c.init_error_dialogs()
        after, found = p.nodeAfterTree(), False
        while p and p != after:
            if p.isAtAutoNode() and not p.isAtIgnoreNode() and p.isDirty():
                ok = at.writeOneAtAutoNode(p)
                if ok:
                    found = True
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()
        if g.unitTesting:
            return
        if found:
            g.es("finished")
        else:
            g.es("no dirty @auto nodes in the selected tree")
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20080711093251.3: *6* at.writeAtShadowNodes
    @cmd('write-at-shadow-nodes')
    def writeAtShadowNodes(self, event: Event = None) -> bool:  # pragma: no cover
        """Write all @shadow nodes in the selected outline."""
        at, c, p = self, self.c, self.c.p
        c.init_error_dialogs()
        after, found = p.nodeAfterTree(), False
        while p and p != after:
            if p.atShadowFileNodeName() and not p.isAtIgnoreNode():
                ok = at.writeOneAtShadowNode(p)
                if ok:
                    found = True
                    g.blue(f"wrote {p.atShadowFileNodeName()}")
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()
        if g.unitTesting:
            return found
        if found:
            g.es("finished")
        else:
            g.es("no @shadow nodes in the selected tree")
        c.raise_error_dialogs(kind='write')
        return found

    #@+node:ekr.20220120072917.1: *6* at.writeDirtyAtShadowNodes
    @cmd('write-dirty-at-shadow-nodes')
    def writeDirtyAtShadowNodes(self, event: Event = None) -> bool:  # pragma: no cover
        """Write all @shadow nodes in the selected outline."""
        at, c, p = self, self.c, self.c.p
        c.init_error_dialogs()
        after, found = p.nodeAfterTree(), False
        while p and p != after:
            if p.atShadowFileNodeName() and not p.isAtIgnoreNode() and p.isDirty():
                ok = at.writeOneAtShadowNode(p)
                if ok:
                    found = True
                    g.blue(f"wrote {p.atShadowFileNodeName()}")
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            else:
                p.moveToThreadNext()
        if g.unitTesting:
            return found
        if found:
            g.es("finished")
        else:
            g.es("no dirty @shadow nodes in the selected tree")
        c.raise_error_dialogs(kind='write')
        return found

    #@+node:ekr.20041005105605.157: *5* at.putFile
    def putFile(self, root: Position, fromString: str = '', sentinels: bool = True) -> None:
        """Write the contents of the file to the output stream."""
        at = self
        s = fromString if fromString else root.v.b
        root.clearAllVisitedInTree()
        at.putAtFirstLines(s)
        at.putOpenLeoSentinel("@+leo-ver=5")
        at.putInitialComment()
        at.putOpenNodeSentinel(root)
        at.putBody(root, fromString=fromString)
        # The -leo sentinel is required to handle @last.
        at.putSentinel("@-leo")
        root.setVisited()
        at.putAtLastLines(s)
    #@+node:ekr.20041005105605.147: *5* at.writeAll & helpers
    def writeAll(self, all: bool = False, dirty: bool = False) -> None:
        """Write @file nodes in all or part of the outline"""
        at = self
        # This is the *only* place where these are set.
        # promptForDangerousWrite sets cancelFlag only if canCancelFlag is True.
        at.unchangedFiles = 0
        at.canCancelFlag = True
        at.cancelFlag = False
        at.yesToAll = False
        files, root = at.findFilesToWrite(all)
        for p in files:
            try:
                at.writeAllHelper(p, root)
            except Exception:  # pragma: no cover
                at.internalWriteError(p)
        # Make *sure* these flags are cleared for other commands.
        at.canCancelFlag = False
        at.cancelFlag = False
        at.yesToAll = False
        # Say the command is finished.
        at.reportEndOfWrite(files, all, dirty)
        # #2338: Never call at.saveOutlineIfPossible().
    #@+node:ekr.20190108052043.1: *6* at.findFilesToWrite
    def findFilesToWrite(self, force: bool) -> tuple[list[Position], Position]:  # pragma: no cover
        """
        Return a list of files to write.
        We must do this in a prepass, so as to avoid errors later.
        """
        trace = 'save' in g.app.debug and not g.unitTesting
        if trace:
            g.trace(f"writing *{'selected' if force else 'all'}* files")
        c = self.c
        if force:
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
        seen = set()
        files: list[Position] = []
        while p and p != after:
            if p.isAtIgnoreNode() and not p.isAtAsisFileNode():
                # Honor @ignore in *body* text, but *not* in @asis nodes.
                if p.isAnyAtFileNode():
                    c.ignored_at_file_nodes.append(p.h)
                p.moveToNodeAfterTree()
            elif p.isAnyAtFileNode():
                data = p.v, c.fullPath(p)
                if data in seen:
                    if trace and force:
                        g.trace('Already seen', p.h)
                else:
                    seen.add(data)
                    files.append(p.copy())
                # Don't scan nested trees???
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        # When scanning *all* nodes, we only actually write dirty nodes.
        if not force:
            files = [z for z in files if z.isDirty()]
        if trace:
            g.printObj([z.h for z in files], tag='Files to be saved')
        return files, root
    #@+node:ekr.20190108053115.1: *6* at.internalWriteError
    def internalWriteError(self, p: Position) -> None:  # pragma: no cover
        """
        Fix bug 1260415: https://bugs.launchpad.net/leo-editor/+bug/1260415
        Give a more urgent, more specific, more helpful message.
        """
        g.es_exception()
        g.es(f"Internal error writing: {p.h}", color='red')
        g.es('Please report this error to:', color='blue')
        g.es('https://groups.google.com/forum/#!forum/leo-editor', color='blue')
        g.es('Warning: changes to this file will be lost', color='red')
        g.es('unless you can save the file successfully.', color='red')
    #@+node:ekr.20190108112519.1: *6* at.reportEndOfWrite
    def reportEndOfWrite(self, files: list[Position], all: bool, dirty: bool) -> None:  # pragma: no cover

        at = self
        if g.unitTesting:
            return
        if files:
            n = at.unchangedFiles
            g.es(f"finished: {n} unchanged file{g.plural(n)}")
        elif all:
            g.warning("no @<file> nodes in the selected tree")
        elif dirty:
            g.es("no dirty @<file> nodes in the selected tree")
    #@+node:ekr.20041005105605.149: *6* at.writeAllHelper & helper
    def writeAllHelper(self, p: Position, root: Position) -> None:
        """
        Write one file for at.writeAll.

        Do *not* write @auto files unless p == root.

        This prevents the write-all command from needlessly updating
        the @persistence data, thereby annoyingly changing the .leo file.
        """
        at = self
        at.root = root
        if p.isAtIgnoreNode():  # pragma: no cover
            # Should have been handled in findFilesToWrite.
            g.trace(f"Can not happen: {p.h} is an @ignore node")
            return
        try:
            at.writePathChanged(p)
        except IOError:  # pragma: no cover
            return
        table = (
            (p.isAtAsisFileNode, at.asisWrite),
            (p.isAtAutoNode, at.writeOneAtAutoNode),
            (p.isAtCleanNode, at.writeOneAtCleanNode),
            (p.isAtEditNode, at.writeOneAtEditNode),
            (p.isAtFileNode, at.writeOneAtFileNode),
            (p.isAtNoSentFileNode, at.writeOneAtNosentNode),
            (p.isAtShadowFileNode, at.writeOneAtShadowNode),
            (p.isAtThinFileNode, at.writeOneAtFileNode),
        )
        for pred, func in table:
            if pred():
                func(p)  # type:ignore
                break
        else:  # pragma: no cover
            g.trace(f"Can not happen: {p.h}")
            return
        #
        # Clear the dirty bits in all descendant nodes.
        # The persistence data may still have to be written.
        for p2 in p.self_and_subtree(copy=False):
            p2.v.clearDirty()
    #@+node:ekr.20190108105509.1: *7* at.writePathChanged
    def writePathChanged(self, p: Position) -> None:  # pragma: no cover
        """
        raise IOError if p's path has changed *and* user forbids the write.
        """
        at, c = self, self.c
        #
        # Suppress this message during save-as and save-to commands.
        if c.ignoreChangedPaths:
            return  # pragma: no cover
        oldPath = g.os_path_normcase(at.getPathUa(p))
        newPath = g.os_path_normcase(c.fullPath(p))
        try:  # #1367: samefile can throw an exception.
            changed = oldPath and not os.path.samefile(oldPath, newPath)
        except Exception:
            changed = True
        if not changed:
            return
        ok = at.promptForDangerousWrite(
            fileName=None,
            message=(
                f"{g.tr('path changed for %s' % (p.h))}\n"
                f"{g.tr('write this file anyway?')}"
            ),
        )
        if not ok:
            raise IOError
        at.setPathUa(p, newPath)  # Remember that we have changed paths.
    #@+node:ekr.20190109172025.1: *5* at.writeAtAutoContents
    def writeAtAutoContents(self, fileName: str, root: Position) -> str:  # pragma: no cover
        """Common helper for atAutoToString and writeOneAtAutoNode."""
        at, c = self, self.c
        # Dispatch the proper writer.
        junk, ext = g.os_path_splitext(fileName)
        writer = at.dispatch(ext, root)
        if writer:
            at.outputList = []
            writer(root)
            return '' if at.errors else ''.join(at.outputList)
        if root.isAtAutoRstNode():
            # An escape hatch: fall back to the theRst writer
            # if there is no rst writer plugin.
            at.outputFile = io.StringIO()
            ok = c.rstCommands.writeAtAutoFile(root, fileName, at.outputFile)
            if not ok:
                return ''
            s = at.outputFile.getvalue()
            at.outputFile.close()
            return s
        # leo 5.6: allow undefined section references in all @auto files.
        try:
            g.app.allow_undefined_refs = True
            at.outputList = []
            at.putFile(root, sentinels=False)
            return '' if at.errors else ''.join(at.outputList)
        except Exception:
            return None
        finally:
            g.app.allow_undefined_refs = False
    #@+node:ekr.20190111153522.1: *5* at.writeX...
    #@+node:ekr.20041005105605.154: *6* at.asisWrite & helper
    def asisWrite(self, root: Position) -> None:  # pragma: no cover
        at, c = self, self.c
        try:
            c.endEditing()
            c.init_error_dialogs()
            fileName = at.initWriteIvars(root)
            # #1450.
            if not fileName or not at.precheck(fileName, root):
                at.addToOrphanList(root)
                return
            at.outputList = []
            for p in root.self_and_subtree(copy=False):
                at.writeAsisNode(p)
            if not at.errors:
                contents = ''.join(at.outputList)
                at.replaceFile(contents, at.encoding, fileName, root)
        except Exception:
            at.writeException(fileName, root)

    silentWrite = asisWrite  # Compatibility with old scripts.
    #@+node:ekr.20170331141933.1: *7* at.writeAsisNode
    def writeAsisNode(self, p: Position) -> None:  # pragma: no cover
        """Write the p's node to an @asis file."""
        at = self

        def put(s: str) -> None:
            """Append s to self.output_list."""
            # #1480: Avoid calling at.os().
            s = g.toUnicode(s, at.encoding, reportErrors=True)
            at.outputList.append(s)

        # Write the headline only if it starts with '@@'.

        s = p.h
        if g.match(s, 0, "@@"):
            s = s[2:]
            if s:
                put('\n')  # Experimental.
                put(s)
                put('\n')
        # Write the body.
        s = p.b
        if s:
            put(s)
    #@+node:ekr.20041005105605.151: *6* at.writeMissing & helper
    def writeMissing(self, p: Position) -> None:  # pragma: no cover
        at, c = self, self.c
        writtenFiles = False
        c.init_error_dialogs()
        # #1450.
        at.initWriteIvars(root=p.copy())
        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after:  # Don't use iterator.
            if (
                p.isAtAsisFileNode() or (p.isAnyAtFileNode() and not p.isAtIgnoreNode())
            ):
                fileName = p.anyAtFileNodeName()
                if fileName:
                    fileName = c.fullPath(p)  # #1914.
                    if at.precheck(fileName, p):
                        at.writeMissingNode(p)
                        writtenFiles = True
                    else:
                        at.addToOrphanList(p)
                p.moveToNodeAfterTree()
            elif p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        if not g.unitTesting:
            if writtenFiles:
                g.es("finished")
            else:
                g.es("no @file node in the selected tree")
        c.raise_error_dialogs(kind='write')
    #@+node:ekr.20041005105605.152: *7* at.writeMissingNode
    def writeMissingNode(self, p: Position) -> None:  # pragma: no cover

        at = self
        table = (
            (p.isAtAsisFileNode, at.asisWrite),
            (p.isAtAutoNode, at.writeOneAtAutoNode),
            (p.isAtCleanNode, at.writeOneAtCleanNode),
            (p.isAtEditNode, at.writeOneAtEditNode),
            (p.isAtFileNode, at.writeOneAtFileNode),
            (p.isAtNoSentFileNode, at.writeOneAtNosentNode),
            (p.isAtShadowFileNode, at.writeOneAtShadowNode),
            (p.isAtThinFileNode, at.writeOneAtFileNode),
        )
        for pred, func in table:
            if pred():
                func(p)  # type:ignore
                return
        g.trace(f"Can not happen unknown @<file> kind: {p.h}")
    #@+node:ekr.20070806141607: *6* at.writeOneAtAutoNode & helpers
    def writeOneAtAutoNode(self, p: Position) -> bool:  # pragma: no cover
        """
        Write p, an @auto node.
        File indices *must* have already been assigned.
        Return True if the node was written successfully.
        """
        at, c = self, self.c
        root = p.copy()
        try:
            c.endEditing()
            if not p.atAutoNodeName():
                return False
            fileName = at.initWriteIvars(root)
            at.sentinels = False
            # #1450.
            if not fileName or not at.precheck(fileName, root):
                at.addToOrphanList(root)
                return False
            if c.persistenceController:
                c.persistenceController.update_before_write_foreign_file(root)
            contents = at.writeAtAutoContents(fileName, root)
            if contents is None:
                g.es("not written:", fileName)
                at.addToOrphanList(root)
                return False
            at.replaceFile(contents, at.encoding, fileName, root,
                ignoreBlankLines=root.isAtAutoRstNode())
            return True
        except Exception:
            at.writeException(fileName, root)
            return False
    #@+node:ekr.20140728040812.17993: *7* at.dispatch & helpers
    def dispatch(self, ext: str, p: Position) -> Optional[Callable]:  # pragma: no cover
        """Return the correct writer function for p, an @auto node."""
        at = self
        # Match @auto type before matching extension.
        return at.writer_for_at_auto(p) or at.writer_for_ext(ext)
    #@+node:ekr.20140728040812.17995: *8* at.writer_for_at_auto
    def writer_for_at_auto(self, root: Position) -> Optional[Callable]:  # pragma: no cover
        """A factory returning a writer function for the given kind of @auto directive."""
        at = self
        d = g.app.atAutoWritersDict
        for key in d:
            aClass = d.get(key)
            if aClass and g.match_word(root.h, 0, key):

                def writer_for_at_auto_cb(root: Position) -> Optional[str]:
                    # pylint: disable=cell-var-from-loop
                    try:
                        writer = aClass(at.c)  # noqa
                        s = writer.write(root)
                        return s
                    except Exception:
                        g.es_exception()
                        return None

                return writer_for_at_auto_cb
        return None
    #@+node:ekr.20140728040812.17997: *8* at.writer_for_ext
    def writer_for_ext(self, ext: str) -> Optional[Callable]:  # pragma: no cover
        """A factory returning a writer function for the given file extension."""
        at = self
        d = g.app.writersDispatchDict
        aClass = d.get(ext)
        if aClass:

            def writer_for_ext_cb(root: Position) -> Optional[str]:
                try:
                    return aClass(at.c).write(root)
                except Exception:
                    g.es_exception()
                    return None

            return writer_for_ext_cb

        return None
    #@+node:ekr.20210501064359.1: *6* at.writeOneAtCleanNode
    def writeOneAtCleanNode(self, root: Position) -> None:  # pragma: no cover
        """Write one @clean file..
        root is the position of an @clean node.
        """
        at, c = self, self.c
        try:
            c.endEditing()
            fileName = at.initWriteIvars(root)
            at.sentinels = False
            if not fileName or not at.precheck(fileName, root):
                return
            at.outputList = []
            at.putFile(root, sentinels=False)
            at.warnAboutOrphandAndIgnoredNodes()
            if at.errors:
                g.es("not written:", g.shortFileName(fileName))
                at.addToOrphanList(root)
            else:
                contents = ''.join(at.outputList)
                at.replaceFile(contents, at.encoding, fileName, root)
        except Exception:
            at.writeException(fileName, root)
    #@+node:ekr.20090225080846.5: *6* at.writeOneAtEditNode
    def writeOneAtEditNode(self, p: Position) -> bool:  # pragma: no cover
        """Write one @edit node."""
        at, c = self, self.c
        root = p.copy()
        try:
            c.endEditing()
            c.init_error_dialogs()
            if not p.atEditNodeName():
                return False
            if p.hasChildren():
                g.error('@edit nodes must not have children')
                g.es('To save your work, convert @edit to @auto, @file or @clean')
                return False
            fileName = at.initWriteIvars(root)
            at.sentinels = False
            # #1450.
            if not fileName or not at.precheck(fileName, root):
                at.addToOrphanList(root)
                return False
            contents = ''.join([s for s in g.splitLines(p.b)
                if at.directiveKind4(s, 0) == at.noDirective])
            at.replaceFile(contents, at.encoding, fileName, root)
            c.raise_error_dialogs(kind='write')
            return True
        except Exception:
            at.writeException(fileName, root)
            return False
    #@+node:ekr.20210501075610.1: *6* at.writeOneAtFileNode
    def writeOneAtFileNode(self, root: Position) -> None:  # pragma: no cover
        """Write @file or @thin file."""
        at, c = self, self.c
        try:
            c.endEditing()
            fileName = at.initWriteIvars(root)
            at.sentinels = True
            if not fileName or not at.precheck(fileName, root):
                # Raise dialog warning of data loss.
                at.addToOrphanList(root)
                return
            at.outputList = []
            at.putFile(root, sentinels=True)
            at.warnAboutOrphandAndIgnoredNodes()
            if at.errors:
                g.es("not written:", g.shortFileName(fileName))
                at.addToOrphanList(root)
            else:
                contents = ''.join(at.outputList)
                at.replaceFile(contents, at.encoding, fileName, root)
        except Exception:
            at.writeException(fileName, root)
    #@+node:ekr.20210501065352.1: *6* at.writeOneAtNosentNode
    def writeOneAtNosentNode(self, root: Position) -> None:  # pragma: no cover
        """Write one @nosent node.
        root is the position of an @<file> node.
        sentinels will be False for @clean and @nosent nodes.
        """
        at, c = self, self.c
        try:
            c.endEditing()
            fileName = at.initWriteIvars(root)
            at.sentinels = False
            if not fileName or not at.precheck(fileName, root):
                return
            at.outputList = []
            at.putFile(root, sentinels=False)
            at.warnAboutOrphandAndIgnoredNodes()
            if at.errors:
                g.es("not written:", g.shortFileName(fileName))
                at.addToOrphanList(root)
            else:
                contents = ''.join(at.outputList)
                at.replaceFile(contents, at.encoding, fileName, root)
        except Exception:
            at.writeException(fileName, root)
    #@+node:ekr.20080711093251.5: *6* at.writeOneAtShadowNode & helper
    def writeOneAtShadowNode(self, p: Position, testing: bool = False) -> bool:  # pragma: no cover
        """
        Write p, an @shadow node.
        File indices *must* have already been assigned.

        testing: set by unit tests to suppress the call to at.precheck.
                 Testing is not the same as g.unitTesting.
        """
        at, c = self, self.c
        root = p.copy()
        x = c.shadowController
        try:
            c.endEditing()  # Capture the current headline.
            fn = p.atShadowFileNodeName()
            assert fn, p.h
            # A hack to support unknown extensions. May set c.target_language.
            self.adjustTargetLanguage(fn)
            full_path = c.fullPath(p)
            at.initWriteIvars(root)
            # Force python sentinels to suppress an error message.
            # The actual sentinels will be set below.
            at.endSentinelComment = None
            at.startSentinelComment = "#"
            # Make sure we can compute the shadow directory.
            private_fn = x.shadowPathName(full_path)
            if not private_fn:
                return False
            if not testing and not at.precheck(full_path, root):
                return False
            #
            # Bug fix: Leo 4.5.1:
            # use x.markerFromFileName to force the delim to match
            # what is used in x.propegate changes.
            marker = x.markerFromFileName(full_path)
            at.startSentinelComment, at.endSentinelComment = marker.getDelims()
            if g.unitTesting:
                ivars_dict = g.getIvarsDict(at)
            #
            # Write the public and private files to strings.

            def put(sentinels: bool) -> str:
                at.outputList = []
                at.sentinels = sentinels
                at.putFile(root, sentinels=sentinels)
                return '' if at.errors else ''.join(at.outputList)

            at.public_s = put(False)
            at.private_s = put(True)
            at.warnAboutOrphandAndIgnoredNodes()
            if g.unitTesting:
                exceptions = ('public_s', 'private_s', 'sentinels', 'outputList')
                assert g.checkUnchangedIvars(
                    at, ivars_dict, exceptions), 'writeOneAtShadowNode'
            if not at.errors:
                # Write the public and private files.
                # makeShadowDirectory takes a *public* file name.
                x.makeShadowDirectory(full_path)
                x.replaceFileWithString(at.encoding, private_fn, at.private_s)
                x.replaceFileWithString(at.encoding, full_path, at.public_s)
            at.checkPythonCode(contents=at.private_s, fileName=full_path, root=root)
            if at.errors:
                g.error("not written:", full_path)
                at.addToOrphanList(root)
            else:
                root.clearDirty()
            return not at.errors
        except Exception:
            at.writeException(full_path, root)
            return False
    #@+node:ekr.20080819075811.13: *7* at.adjustTargetLanguage
    def adjustTargetLanguage(self, fn: str) -> None:  # pragma: no cover
        """Use the language implied by fn's extension if
        there is a conflict between it and c.target_language."""
        at = self
        c = at.c
        junk, ext = g.os_path_splitext(fn)
        if ext:
            if ext.startswith('.'):
                ext = ext[1:]
            language = g.app.extension_dict.get(ext)
            if language:
                c.target_language = language
            else:
                # An unknown language.
                # Use the default language, **not** 'unknown_language'
                pass
    #@+node:ekr.20190111153506.1: *5* at.XToString
    #@+node:ekr.20190109160056.1: *6* at.atAsisToString
    def atAsisToString(self, root: Position) -> str:  # pragma: no cover
        """Write the @asis node to a string."""
        # pylint: disable=used-before-assignment
        at, c = self, self.c
        try:
            c.endEditing()
            fileName = at.initWriteIvars(root)
            at.outputList = []
            for p in root.self_and_subtree(copy=False):
                at.writeAsisNode(p)
            return '' if at.errors else ''.join(at.outputList)
        except Exception:
            at.writeException(fileName, root)
            return ''
    #@+node:ekr.20190109160056.2: *6* at.atAutoToString
    def atAutoToString(self, root: Position) -> str:  # pragma: no cover
        """Write the root @auto node to a string, and return it."""
        at, c = self, self.c
        try:
            c.endEditing()
            fileName = at.initWriteIvars(root)
            at.sentinels = False
            # #1450.
            if not fileName:
                at.addToOrphanList(root)
                return ''
            return at.writeAtAutoContents(fileName, root) or ''
        except Exception:
            at.writeException(fileName, root)
            return ''
    #@+node:ekr.20190109160056.3: *6* at.atEditToString
    def atEditToString(self, root: Position) -> str:  # pragma: no cover
        """Write one @edit node."""
        at, c = self, self.c
        try:
            c.endEditing()
            if root.hasChildren():
                g.error('@edit nodes must not have children')
                g.es('To save your work, convert @edit to @auto, @file or @clean')
                return ''
            fileName = at.initWriteIvars(root)
            at.sentinels = False
            # #1450.
            if not fileName:
                at.addToOrphanList(root)
                return ''
            contents = ''.join([
                s for s in g.splitLines(root.b) if at.directiveKind4(s, 0) == at.noDirective
            ])
            return contents
        except Exception:
            at.writeException(fileName, root)
            return ''
    #@+node:ekr.20190109142026.1: *6* at.atFileToString
    def atFileToString(self, root: Position, sentinels: bool = True) -> str:  # pragma: no cover
        """Write an external file to a string, and return its contents."""
        at, c = self, self.c
        try:
            c.endEditing()
            at.initWriteIvars(root)
            at.sentinels = sentinels
            at.outputList = []
            at.putFile(root, sentinels=sentinels)
            assert root == at.root, 'write'
            contents = '' if at.errors else ''.join(at.outputList)
            return contents
        except Exception:
            at.exception("exception preprocessing script")
            root.v._p_changed = True
            return ''
    #@+node:ekr.20050506084734: *6* at.stringToString
    def stringToString(self,
        root: Position,
        s: str,
        forcePythonSentinels: bool = True,
        sentinels: bool = True,
    ) -> str:  # pragma: no cover
        """
        Write an external file from a string.

        This is at.write specialized for scripting.
        """
        at, c = self, self.c
        try:
            c.endEditing()
            at.initWriteIvars(root)
            if forcePythonSentinels:
                at.endSentinelComment = None
                at.startSentinelComment = "#"
                at.language = "python"
            at.sentinels = sentinels
            at.outputList = []
            at.putFile(root, fromString=s, sentinels=sentinels)
            contents = '' if at.errors else ''.join(at.outputList)
            # Major bug: failure to clear this wipes out headlines!
            #            Sometimes this causes slight problems...
            if root:
                root.v._p_changed = True
            return contents
        except Exception:
            at.exception("exception preprocessing script")
            return ''
    #@+node:ekr.20041005105605.160: *4* Writing helpers
    #@+node:ekr.20041005105605.161: *5* at.putBody & helper
    def putBody(self, p: Position, fromString: str = '') -> bool:
        """
        Generate the body enclosed in sentinel lines.
        Return True if the body contains an @others line.
        """
        at = self
        #
        # New in 4.3 b2: get s from fromString if possible.
        s = fromString if fromString else p.b
        # Make sure v is never expanded again.
        # Suppress orphans check.
        p.v.setVisited()
        #
        # #1048 & #1037: regularize most trailing whitespace.
        if s and (at.sentinels or at.force_newlines_in_at_nosent_bodies):
            if not s.endswith('\n'):
                s = s + '\n'


        class Status:
            at_comment_seen = False
            at_delims_seen = False
            at_warning_given = False
            has_at_others = False
            in_code = True


        i = 0
        status = Status()
        while i < len(s):
            next_i = g.skip_line(s, i)
            assert next_i > i, 'putBody'
            kind = at.directiveKind4(s, i)
            at.putLine(i, kind, p, s, status)
            i = next_i
        if not status.in_code:
            at.putEndDocLine()
        return status.has_at_others
    #@+node:ekr.20041005105605.163: *6* at.putLine
    def putLine(self, i: int, kind: int, p: Position, s: str, status: Any) -> None:
        """Put the line at s[i:] of the given kind, updating the status."""
        at = self
        if kind == at.noDirective:
            if status.in_code:
                # Important: the so-called "name" must include brackets.
                name, n1, n2 = at.findSectionName(s, i, p)
                if name:
                    at.putRefLine(s, i, n1, n2, name, p)
                else:
                    at.putCodeLine(s, i)
            else:
                at.putDocLine(s, i)
        elif kind in (at.docDirective, at.atDirective):
            if not status.in_code:
                # Bug fix 12/31/04: handle adjacent doc parts.
                at.putEndDocLine()
            at.putStartDocLine(s, i, kind)
            status.in_code = False
        elif kind in (at.cDirective, at.codeDirective):
            # Only @c and @code end a doc part.
            if not status.in_code:
                at.putEndDocLine()
            at.putDirective(s, i, p)
            status.in_code = True
        elif kind == at.allDirective:
            if status.in_code:
                if p == self.root:
                    at.putAtAllLine(s, i, p)
                else:
                    at.error(f"@all not valid in: {p.h}")  # pragma: no cover
            else:
                at.putDocLine(s, i)
        elif kind == at.othersDirective:
            if status.in_code:
                if status.has_at_others:
                    at.error(f"multiple @others in: {p.h}")  # pragma: no cover
                else:
                    at.putAtOthersLine(s, i, p)
                    status.has_at_others = True
            else:
                at.putDocLine(s, i)
        elif kind == at.startVerbatim:  # pragma: no cover
            # Fix bug 778204: @verbatim not a valid Leo directive.
            if g.unitTesting:
                # A hack: unit tests for @shadow use @verbatim as a kind of directive.
                pass
            else:
                at.error(f"@verbatim is not a Leo directive: {p.h}")
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
            ):  # pragma: no cover
                status.at_warning_given = True
                at.error(f"@comment and @delims in node {p.h}")
            at.putDirective(s, i, p)
        else:
            at.error(f"putBody: can not happen: unknown directive kind: {kind}")  # pragma: no cover
    #@+node:ekr.20041005105605.164: *5* writing code lines...
    #@+node:ekr.20041005105605.165: *6* at: @all
    #@+node:ekr.20041005105605.166: *7* at.putAtAllLine
    def putAtAllLine(self, s: str, i: int, p: Position) -> None:
        """Put the expansion of @all."""
        at = self
        j, delta = g.skip_leading_ws_with_indent(s, i, at.tab_width)
        k = g.skip_to_end_of_line(s, i)
        at.putLeadInSentinel(s, i, j)
        at.indent += delta
        # s[j:k] starts with '@all'
        at.putSentinel("@+" + s[j + 1 : k].strip())
        for child in p.children():
            at.putAtAllChild(child)
        at.putSentinel("@-all")
        at.indent -= delta
    #@+node:ekr.20041005105605.167: *7* at.putAtAllBody
    def putAtAllBody(self, p: Position) -> None:
        """ Generate the body enclosed in sentinel lines."""
        at = self
        s = p.b
        # Make sure v is never expanded again.
        # Suppress orphans check.
        p.v.setVisited()
        if at.sentinels and s and s[-1] != '\n':
            s = s + '\n'
        i = 0
        # Leo 6.6. This code never changes at.in_code status!
        while i < len(s):
            next_i = g.skip_line(s, i)
            assert next_i > i
            at.putCodeLine(s, i)
            i = next_i
    #@+node:ekr.20041005105605.169: *7* at.putAtAllChild
    def putAtAllChild(self, p: Position) -> None:
        """
        This code puts only the first of two or more cloned siblings, preceding
        the clone with an @clone n sentinel.

        This is a debatable choice: the cloned tree appears only once in the
        external file. This should be benign; the text created by @all is
        likely to be used only for recreating the outline in Leo. The
        representation in the derived file doesn't matter much.
        """
        at = self
        # Suppress warnings about @file nodes.
        at.putOpenNodeSentinel(p, inAtAll=True)
        at.putAtAllBody(p)
        for child in p.children():
            at.putAtAllChild(child)  # pragma: no cover (recursive call)
    #@+node:ekr.20041005105605.170: *6* at: @others
    #@+node:ekr.20041005105605.173: *7* at.putAtOthersLine & helper
    def putAtOthersLine(self, s: str, i: int, p: Position) -> None:
        """Put the expansion of @others."""
        at = self
        j, delta = g.skip_leading_ws_with_indent(s, i, at.tab_width)
        k = g.skip_to_end_of_line(s, i)
        at.putLeadInSentinel(s, i, j)
        at.indent += delta
        # s[j:k] starts with '@others'
        # Never write lws in new sentinels.
        at.putSentinel("@+" + s[j + 1 : k].strip())
        for child in p.children():
            p = child.copy()
            after = p.nodeAfterTree()
            while p and p != after:
                if at.validInAtOthers(p):
                    at.putOpenNodeSentinel(p)
                    at_others_flag = at.putBody(p)
                    if at_others_flag:
                        p.moveToNodeAfterTree()
                    else:
                        p.moveToThreadNext()
                else:
                    p.moveToNodeAfterTree()
        # This is the same in both old and new sentinels.
        at.putSentinel("@-others")
        at.indent -= delta
    #@+node:ekr.20041005105605.171: *8* at.validInAtOthers
    def validInAtOthers(self, p: Position) -> bool:
        """
        Return True if p should be included in the expansion of the @others
        directive in the body text of p's parent.
        """
        at = self
        i = g.skip_ws(p.h, 0)
        isSection, junk = at.isSectionName(p.h, i)
        if isSection:
            return False  # A section definition node.
        if at.sentinels:
            #@verbatim
            # @ignore must not stop expansion here!
            return True
        if p.isAtIgnoreNode():  # pragma: no cover
            g.error('did not write @ignore node', p.v.h)
            return False
        return True
    #@+node:ekr.20041005105605.199: *6* at.findSectionName
    def findSectionName(self, s: str, i: int, p: Position) -> tuple[str, int, int]:
        """
        Return n1, n2 representing a section name.

        Return the reference, *including* brackets.
        """
        at = self

        def is_space(i1: int, i2: int) -> bool:
            """A replacement for s[i1 : i2] that doesn't create any substring."""
            return i == j or all(s[z] in ' \t\n' for z in range(i1, i2))

        end = s.find('\n', i)
        j = len(s) if end == -1 else end
        # Careful: don't look beyond the end of the line!
        if end == -1:
            n1 = s.find(at.section_delim1, i)
            n2 = s.find(at.section_delim2, i)
        else:
            n1 = s.find(at.section_delim1, i, end)
            n2 = s.find(at.section_delim2, i, end)
        n3 = n2 + len(at.section_delim2)
        if -1 < n1 < n2:  # A *possible* section reference.
            if is_space(i, n1) and is_space(n3, j):  # A *real* section reference.
                return s[n1:n3], n1, n3
            # An apparent section reference.
            if 'sections' in g.app.debug and not g.unitTesting:  # pragma: no cover
                i1, i2 = g.getLine(s, i)
                g.es_print('Ignoring apparent section reference:', color='red')
                g.es_print('Node: ', p.h)
                g.es_print('Line: ', s[i1:i2].rstrip())
        return None, 0, 0
    #@+node:ekr.20041005105605.174: *6* at.putCodeLine
    def putCodeLine(self, s: str, i: int) -> None:
        """Put a normal code line."""
        at = self
        j = g.skip_line(s, i)
        k = g.skip_ws(s, i)
        line = s[i:j]

        def put_verbatim_sentinel() -> None:
            """
            Put an @verbatim sentinel. *Always* use black-compatible indentation.
            """
            if at.root.isAtCleanNode():
                # #2996. Adding an @verbatim sentinel interferes with the @clean algorithm.
                return
            ws = s[i:k]
            self.putIndent(len(ws))
            self.putSentinel("@verbatim")

        # Put an @verbatim sentinel if the next line looks like another sentinel.
        if at.language == 'python':  # New in Leo 6.7.2.
            # Python sentinels *only* may contain a space between '#' and '@'
            if g.match(s, k, '#@') or g.match(s, k, '# @'):
                put_verbatim_sentinel()
        elif g.match(s, k, self.startSentinelComment + "@"):
            put_verbatim_sentinel()

        # Don't put any whitespace in otherwise blank lines.
        if len(line) > 1:  # Preserve *anything* the user puts on the line!!!
            at.putIndent(at.indent, line)
            if line[-1:] == '\n':
                at.os(line[:-1])
                at.onl()
            else:
                at.os(line)
        elif line and line[-1] == '\n':
            at.onl()
        elif line:
            at.os(line)  # Bug fix: 2013/09/16
        else:
            g.trace('Can not happen: completely empty line')  # pragma: no cover
    #@+node:ekr.20041005105605.176: *6* at.putRefLine
    def putRefLine(self, s: str, i: int, n1: int, n2: int, name: str, p: Position) -> None:
        """
        Put a line containing one or more references.

        Important: the so-called name *must* include brackets.
        """
        at = self
        ref = g.findReference(name, p)
        if ref:
            junk, delta = g.skip_leading_ws_with_indent(s, i, at.tab_width)
            at.putLeadInSentinel(s, i, n1)
            at.indent += delta
            at.putSentinel("@+" + name)
            at.putOpenNodeSentinel(ref)
            at.putBody(ref)
            at.putSentinel("@-" + name)
            at.indent -= delta
            return
        if g.app.allow_undefined_refs:  # pragma: no cover
            p.v.setVisited()  # #2311
            # Allow apparent section reference: just write the line.
            at.putCodeLine(s, i)
        else:  # pragma: no cover
            # Do give this error even if unit testing.
            at.writeError(
                f"undefined section: {g.truncate(name, 60)}\n"
                f"  referenced from: {g.truncate(p.h, 60)}")
    #@+node:ekr.20041005105605.180: *5* writing doc lines...
    #@+node:ekr.20041005105605.181: *6* at.putBlankDocLine
    def putBlankDocLine(self) -> None:
        at = self
        if not at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.startSentinelComment)
            # #1496: Retire the @doc convention.
            #        Remove the blank.
            # at.oblank()
        at.onl()
    #@+node:ekr.20041005105605.183: *6* at.putDocLine
    def putDocLine(self, s: str, i: int) -> None:
        """Handle one line of a doc part."""
        at = self
        j = g.skip_line(s, i)
        s = s[i:j]
        #
        # #1496: Retire the @doc convention:
        #        Strip all trailing ws here.
        if not s.strip():
            # A blank line.
            at.putBlankDocLine()
            return
        # Write the line as it is.
        at.putIndent(at.indent)
        if not at.endSentinelComment:
            at.os(at.startSentinelComment)
            # #1496: Retire the @doc convention.
            #        Leave this blank. The line is not blank.
            at.oblank()
        at.os(s)
        if not s.endswith('\n'):
            at.onl()  # pragma: no cover
    #@+node:ekr.20041005105605.185: *6* at.putEndDocLine
    def putEndDocLine(self) -> None:
        """Write the conclusion of a doc part."""
        at = self
        # Put the closing delimiter if we are using block comments.
        if at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.endSentinelComment)
            at.onl()  # Note: no trailing whitespace.
    #@+node:ekr.20041005105605.182: *6* at.putStartDocLine
    def putStartDocLine(self, s: str, i: int, kind: Any) -> None:
        """Write the start of a doc part."""
        at = self
        sentinel = "@+doc" if kind == at.docDirective else "@+at"
        directive = "@doc" if kind == at.docDirective else "@"
        # Put whatever follows the directive in the sentinel.
        # Skip past the directive.
        i += len(directive)
        j = g.skip_to_end_of_line(s, i)
        follow = s[i:j]
        # Put the opening @+doc or @-doc sentinel, including whatever follows the directive.
        at.putSentinel(sentinel + follow)
        # Put the opening comment if we are using block comments.
        if at.endSentinelComment:
            at.putIndent(at.indent)
            at.os(at.startSentinelComment)
            at.onl()
    #@+node:ekr.20041005105605.187: *4* Writing sentinels...
    #@+node:ekr.20041005105605.188: *5* at.nodeSentinelText & helper
    def nodeSentinelText(self, p: Position) -> str:
        """Return the text of a @+node or @-node sentinel for p."""
        at = self
        h = at.removeCommentDelims(p)
        if getattr(at, 'at_shadow_test_hack', False):  # pragma: no cover
            # A hack for @shadow unit testing.
            # see AtShadowTestCase.makePrivateLines.
            return h
        gnx = p.v.fileIndex
        level = 1 + p.level() - self.root.level()
        if level > 2:
            return f"{gnx}: *{level}* {h}"
        return f"{gnx}: {'*' * level} {h}"
    #@+node:ekr.20041005105605.189: *6* at.removeCommentDelims
    def removeCommentDelims(self, p: Position) -> str:
        """
        If the present @language/@comment settings do not specify a single-line comment
        we remove all block comment delims from h. This prevents headline text from
        interfering with the parsing of node sentinels.
        """
        at = self
        start = at.startSentinelComment
        end = at.endSentinelComment
        h = p.h
        if end:
            h = h.replace(start, "")
            h = h.replace(end, "")
        return h
    #@+node:ekr.20041005105605.190: *5* at.putLeadInSentinel
    def putLeadInSentinel(self, s: str, i: int, j: int) -> None:
        """
        Set at.leadingWs as needed for @+others and @+<< sentinels.

        i points at the start of a line.
        j points at @others or a section reference.
        """
        at = self
        at.leadingWs = ""  # Set the default.
        if i == j:
            return  # The @others or ref starts a line.
        k = g.skip_ws(s, i)
        if j == k:
            # Remember the leading whitespace, including its spelling.
            at.leadingWs = s[i:j]
        else:
            self.putIndent(at.indent)  # 1/29/04: fix bug reported by Dan Winkler.
            at.os(s[i:j])
            at.onl_sent()
    #@+node:ekr.20041005105605.192: *5* at.putOpenLeoSentinel 4.x
    def putOpenLeoSentinel(self, s: str) -> None:
        """Write @+leo sentinel."""
        at = self
        if at.sentinels or g.app.force_at_auto_sentinels:
            s = s + "-thin"
            encoding = at.encoding.lower()
            if encoding != "utf-8":  # pragma: no cover
                # New in 4.2: encoding fields end in ",."
                s = s + f"-encoding={encoding},."
            at.putSentinel(s)
    #@+node:ekr.20041005105605.193: *5* at.putOpenNodeSentinel
    def putOpenNodeSentinel(self, p: Position, inAtAll: bool = False) -> None:
        """Write @+node sentinel for p."""
        # Note: lineNumbers.py overrides this method.
        at = self
        if not inAtAll and p.isAtFileNode() and p != at.root:  # pragma: no cover
            at.writeError("@file not valid in: " + p.h)
            return
        s = at.nodeSentinelText(p)
        at.putSentinel("@+node:" + s)
        # Leo 4.7: we never write tnodeLists.
    #@+node:ekr.20041005105605.194: *5* at.putSentinel (applies cweb hack) 4.x
    def putSentinel(self, s: str) -> None:
        """
        Write a sentinel whose text is s, applying the CWEB hack if needed.

        This method outputs all sentinels.
        """
        at = self
        if at.sentinels or g.app.force_at_auto_sentinels:
            at.putIndent(at.indent)
            at.os(at.startSentinelComment)
            # #2194. #2983: Put Black sentinels if --black-sentinels is in effect.
            if g.app.write_black_sentinels:
                at.os(' ')
            # Apply the cweb hack to s:
            #   If the opening comment delim ends in '@',
            #   double all '@' signs except the first.
            start = at.startSentinelComment
            if start and start[-1] == '@':
                s = s.replace('@', '@@')[1:]
            at.os(s)
            if at.endSentinelComment:
                at.os(at.endSentinelComment)
            at.onl()
    #@+node:ekr.20041005105605.196: *4* Writing utils...
    #@+node:ekr.20181024134823.1: *5* at.addToOrphanList
    def addToOrphanList(self, root: Position) -> None:  # pragma: no cover
        """Mark the root as erroneous for c.raise_error_dialogs()."""
        c = self.c
        # Fix #1050:
        root.setOrphan()
        c.orphan_at_file_nodes.append(root.h)
    #@+node:ekr.20220120210617.1: *5* at.checkUnchangedFiles
    def checkUnchangedFiles(self, contents: str, fileName: str, root: Position) -> None:  # pragma: no cover
        at = self
        ok1 = ok2 = True
        if g.unitTesting:
            return
        is_python = fileName and fileName.endswith(('py', 'pyw'))
        if not contents or not is_python:
            return

        if at.runFlake8OnWrite:
            ok1 = self.runFlake8(root)
        if at.runPyFlakesOnWrite:
            ok2 = self.runPyflakes(root)
        if not ok1 or not ok2:
            g.app.syntax_error_files.append(g.shortFileName(fileName))
    #@+node:ekr.20090514111518.5661: *5* at.checkPythonCode & helpers
    def checkPythonCode(self, contents: str, fileName: str, root: Position) -> None:  # pragma: no cover
        """Perform python-related checks on root."""
        if not g.app.log:
            return  # We are auto-saving.
        at = self
        is_python = fileName and fileName.endswith(('py', 'pyw'))

        if g.unitTesting or not contents or not is_python:
            return
        ok = True
        if at.checkPythonCodeOnWrite:
            ok = at.checkPythonSyntax(root, contents)
        if ok and at.runPyFlakesOnWrite:  # Creates clickable links.
            ok = self.runPyflakes(root)
        if ok and at.runFlake8OnWrite:  # Does *not* create clickable links.
            ok = self.runFlake8(root)
        if not ok:
            g.app.syntax_error_files.append(g.shortFileName(fileName))
    #@+node:ekr.20090514111518.5663: *6* at.checkPythonSyntax
    def checkPythonSyntax(self, p: Position, body: Any) -> bool:
        at = self
        try:
            body = body.replace('\r', '')
            fn = f"<node: {p.h}>"
            compile(body + '\n', fn, 'exec')
            return True
        except SyntaxError:  # pragma: no cover
            if not g.unitTesting:
                at.syntaxError(p, body)
        except Exception:  # pragma: no cover
            g.trace("unexpected exception")
            g.es_exception()
        return False
    #@+node:ekr.20090514111518.5666: *7* at.syntaxError (leoAtFile)
    def syntaxError(self, p: Position, body: Any) -> None:  # pragma: no cover
        """Report a syntax error."""
        g.error(f"Syntax error in: {p.h}")
        typ, val, tb = sys.exc_info()
        message = hasattr(val, 'message') and val.message
        if message:
            g.es_print(message)
        if val is None:
            return
        lines = g.splitLines(body)
        n = val.lineno
        offset = val.offset or 0
        if n is None:
            return
        i = val.lineno - 1
        for j in range(max(0, i - 2), min(i + 2, len(lines) - 1)):
            line = lines[j].rstrip()
            if j == i:
                unl = p.get_UNL()
                g.es_print(f"{j+1:5}:* {line}", nodeLink=f"{unl}::-{j+1}")  # Global line.
                g.es_print(' ' * (7 + offset) + '^')
            else:
                g.es_print(f"{j+1:5}: {line}")
    #@+node:ekr.20221128123139.1: *6* at.runFlake8
    def runFlake8(self, root: Position) -> bool:  # pragma: no cover
        """Run flake8 on the selected node."""
        try:
            from leo.commands import checkerCommands
            if checkerCommands.flake8:
                x = checkerCommands.Flake8Command(self.c)
                x.run(root)
                return True
            return True  # Suppress error if pyflakes can not be imported.
        except Exception:
            g.es_exception()
            return True  # Pretend all is well
    #@+node:ekr.20161021084954.1: *6* at.runPyflakes
    def runPyflakes(self, root: Position) -> bool:  # pragma: no cover
        """Run pyflakes on the selected node."""
        try:
            from leo.commands import checkerCommands
            if checkerCommands.pyflakes:
                x = checkerCommands.PyflakesCommand(self.c)
                ok = x.run(root)
                return ok
            return True  # Suppress error if pyflakes can not be imported.
        except Exception:
            g.es_exception()
            return True  # Pretend all is well
    #@+node:ekr.20041005105605.198: *5* at.directiveKind4 (write logic)
    # These patterns exclude constructs such as @encoding.setter or @encoding(whatever)
    # However, they must allow @language python, @nocolor-node, etc.

    at_directive_kind_pattern = re.compile(r'\s*@([\w-]+)\s*')

    def directiveKind4(self, s: str, i: int) -> int:
        """
        Return the kind of at-directive or noDirective.

        Potential simplifications:
        - Using strings instead of constants.
        - Using additional regex's to recognize directives.
        """
        at = self
        n = len(s)
        if i >= n or s[i] != '@':
            j = g.skip_ws(s, i)
            if g.match_word(s, j, "@others"):
                return at.othersDirective
            if g.match_word(s, j, "@all"):
                return at.allDirective
            return at.noDirective
        table = (
            ("@all", at.allDirective),
            ("@c", at.cDirective),
            ("@code", at.codeDirective),
            ("@doc", at.docDirective),
            ("@others", at.othersDirective),
            ("@verbatim", at.startVerbatim))
            # ("@end_raw", at.endRawDirective),  # #2276.
            # ("@raw", at.rawDirective),  # #2276
        # Rewritten 6/8/2005.
        if i + 1 >= n or s[i + 1] in (' ', '\t', '\n'):
            # Bare '@' not recognized in cweb mode.
            return at.noDirective if at.language == "cweb" else at.atDirective
        if not s[i + 1].isalpha():
            return at.noDirective  # Bug fix: do NOT return miscDirective here!
        if at.language == "cweb" and g.match_word(s, i, '@c'):
            return at.noDirective
        # When the language is elixir, @doc followed by a space and string delimiter
        # needs to be treated as plain text; the following does not enforce the
        # 'string delimiter' part of that.  An @doc followed by something other than
        # a space will fall through to usual Leo @doc processing.
        if at.language == "elixir" and g.match_word(s, i, '@doc '):  # pragma: no cover
            return at.noDirective
        for name, directive in table:
            if g.match_word(s, i, name):
                return directive
        # Support for add_directives plugin.
        # Use regex to properly distinguish between Leo directives
        # and python decorators.
        s2 = s[i:]
        m = self.at_directive_kind_pattern.match(s2)
        if m:
            word = m.group(1)
            if word not in g.globalDirectiveList:
                return at.noDirective
            s3 = s2[m.end(1) :]
            if s3 and s3[0] in ".(":
                return at.noDirective
            return at.miscDirective
        # An unusual case.
        return at.noDirective  # pragma: no cover
    #@+node:ekr.20041005105605.200: *5* at.isSectionName
    # returns (flag, end). end is the index of the character after the section name.

    def isSectionName(self, s: str, i: int) -> tuple[bool, int]:  # pragma: no cover

        at = self
        # Allow leading periods.
        while i < len(s) and s[i] == '.':
            i += 1
        if not g.match(s, i, at.section_delim1):
            return False, -1
        i = g.find_on_line(s, i, at.section_delim2)
        if i > -1:
            return True, i + len(at.section_delim2)
        return False, -1
    #@+node:ekr.20190111112442.1: *5* at.isWritable
    def isWritable(self, path: Any) -> bool:  # pragma: no cover
        """Return True if the path is writable."""
        try:
            # os.access() may not exist on all platforms.
            ok = os.access(path, os.W_OK)
        except AttributeError:
            return True
        if not ok:
            g.es('read only:', repr(path), color='red')
        return ok
    #@+node:ekr.20041005105605.201: *5* at.os and allies
    #@+node:ekr.20041005105605.202: *6* at.oblank, oblanks & otabs
    def oblank(self) -> None:
        self.os(' ')

    def oblanks(self, n: int) -> None:  # pragma: no cover
        self.os(' ' * abs(n))

    def otabs(self, n: int) -> None:  # pragma: no cover
        self.os('\t' * abs(n))
    #@+node:ekr.20041005105605.203: *6* at.onl & onl_sent
    def onl(self) -> None:
        """Write a newline to the output stream."""
        self.os('\n')  # **not** self.output_newline

    def onl_sent(self) -> None:
        """Write a newline to the output stream, provided we are outputting sentinels."""
        if self.sentinels:
            self.onl()
    #@+node:ekr.20041005105605.204: *6* at.os
    def os(self, s: str) -> None:
        """
        Append a string to at.outputList.

        All output produced by leoAtFile module goes here.
        """
        at = self
        s = g.toUnicode(s, at.encoding)
        at.outputList.append(s)
    #@+node:ekr.20041005105605.205: *5* at.outputStringWithLineEndings
    def outputStringWithLineEndings(self, s: str) -> None:  # pragma: no cover
        """
        Write the string s as-is except that we replace '\n' with the proper line ending.

        Calling self.onl() runs afoul of queued newlines.
        """
        at = self
        s = g.toUnicode(s, at.encoding)
        s = s.replace('\n', at.output_newline)
        self.os(s)
    #@+node:ekr.20190111045822.1: *5* at.precheck (calls shouldPrompt...)
    def precheck(self, fileName: str, root: Position) -> bool:  # pragma: no cover
        """
        Check whether a dirty, potentially dangerous, file should be written.

        Return True if so.  Return False *and* issue a warning otherwise.
        """
        at = self
        #
        # #1450: First, check that the directory exists.
        theDir = g.os_path_dirname(fileName)
        if theDir and not g.os_path_exists(theDir):
            at.error(f"Directory not found:\n{theDir}")
            return False
        #
        # Now check the file.
        if not at.shouldPromptForDangerousWrite(fileName, root):
            # Fix bug 889175: Remember the full fileName.
            at.rememberReadPath(fileName, root)
            return True
        #
        # Prompt if the write would overwrite the existing file.
        ok = self.promptForDangerousWrite(fileName)
        if ok:
            # Fix bug 889175: Remember the full fileName.
            at.rememberReadPath(fileName, root)
            return True
        #
        # Fix #1031: do not add @ignore here!
        g.es("not written:", fileName)
        return False
    #@+node:ekr.20050506090446.1: *5* at.putAtFirstLines
    def putAtFirstLines(self, s: str) -> None:
        """
        Write any @firstlines from string s.
        These lines are converted to @verbatim lines,
        so the read logic simply ignores lines preceding the @+leo sentinel.
        """
        at = self
        tag = "@first"
        i = 0
        while g.match(s, i, tag):
            i += len(tag)
            i = g.skip_ws(s, i)
            j = i
            i = g.skip_to_end_of_line(s, i)
            # Write @first line, whether empty or not
            line = s[j:i]
            at.os(line)
            at.onl()
            i = g.skip_nl(s, i)
    #@+node:ekr.20050506090955: *5* at.putAtLastLines
    def putAtLastLines(self, s: str) -> None:
        """
        Write any @last lines from string s.
        These lines are converted to @verbatim lines,
        so the read logic simply ignores lines following the @-leo sentinel.
        """
        at = self
        tag = "@last"
        # Use g.splitLines to preserve trailing newlines.
        lines = g.splitLines(s)
        n = len(lines)
        j = k = n - 1
        # Scan backwards for @last directives.
        while j >= 0:
            line = lines[j]
            if g.match(line, 0, tag):
                j -= 1
            elif not line.strip():
                j -= 1
            else:
                break  # pragma: no cover (coverage bug)
        # Write the @last lines.
        for line in lines[j + 1 : k + 1]:
            if g.match(line, 0, tag):
                i = len(tag)
                i = g.skip_ws(line, i)
                at.os(line[i:])
    #@+node:ekr.20041005105605.206: *5* at.putDirective & helper
    def putDirective(self, s: str, i: int, p: Position) -> int:
        r"""
        Output a sentinel a directive or reference s.

        It is important for PHP and other situations that \@first and \@last
        directives get translated to verbatim lines that do *not* include what
        follows the @first & @last directives.
        """
        at = self
        k = i
        j = g.skip_to_end_of_line(s, i)
        directive = s[i:j]
        if g.match_word(s, k, "@delims"):
            at.putDelims(directive, s, k)
        elif g.match_word(s, k, "@language"):
            self.putSentinel("@" + directive)
        elif g.match_word(s, k, "@comment"):
            self.putSentinel("@" + directive)
        elif g.match_word(s, k, "@last"):
            # #1307.
            if p.isAtCleanNode():  # pragma: no cover
                at.error(f"ignoring @last directive in {p.h!r}")
                g.es_print('@last is not valid in @clean nodes')
            # #1297.
            elif g.app.inScript or g.unitTesting or p.isAnyAtFileNode():
                # Convert to an verbatim line _without_ anything else.
                self.putSentinel("@@last")
            else:
                at.error(f"ignoring @last directive in {p.h!r}")  # pragma: no cover
        elif g.match_word(s, k, "@first"):
            # #1307.
            if p.isAtCleanNode():  # pragma: no cover
                at.error(f"ignoring @first directive in {p.h!r}")
                g.es_print('@first is not valid in @clean nodes')
            # #1297.
            elif g.app.inScript or g.unitTesting or p.isAnyAtFileNode():
                # Convert to an verbatim line _without_ anything else.
                self.putSentinel("@@first")
            else:
                at.error(f"ignoring @first directive in {p.h!r}")  # pragma: no cover
        else:
            self.putSentinel("@" + directive)
        i = g.skip_line(s, k)
        return i
    #@+node:ekr.20041005105605.207: *6* at.putDelims
    def putDelims(self, directive: str, s: str, k: int) -> None:
        """Put an @delims directive."""
        at = self
        # Put a space to protect the last delim.
        at.putSentinel(directive + " ")  # 10/23/02: put @delims, not @@delims
        # Skip the keyword and whitespace.
        j = i = g.skip_ws(s, k + len("@delims"))
        # Get the first delim.
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
            i += 1
        if j < i:
            at.startSentinelComment = s[j:i]
            # Get the optional second delim.
            j = i = g.skip_ws(s, i)
            while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s, i):
                i += 1
            at.endSentinelComment = s[j:i] if j < i else ""
        else:
            at.writeError("Bad @delims directive")  # pragma: no cover
    #@+node:ekr.20041005105605.210: *5* at.putIndent
    def putIndent(self, n: int, s: str = '') -> None:  # pragma: no cover
        """Put tabs and spaces corresponding to n spaces,
        assuming that we are at the start of a line.
        """
        if n > 0:
            w = self.tab_width
            if w > 1:
                q, r = divmod(n, w)
                self.otabs(q)
                self.oblanks(r)
            else:
                self.oblanks(n)
    #@+node:ekr.20041005105605.211: *5* at.putInitialComment
    def putInitialComment(self) -> None:  # pragma: no cover
        c = self.c
        s2 = c.config.getString('output-initial-comment') or ''
        if s2.strip():
            lines = s2.split("\\n")
            for line in lines:
                line = line.replace("@date", time.asctime())
                if line:
                    self.putSentinel("@comment " + line)
    #@+node:ekr.20190111172114.1: *5* at.replaceFile & helpers
    def replaceFile(self,
        contents: str,
        encoding: str,
        fileName: str,
        root: Position,
        ignoreBlankLines: bool = False,
    ) -> bool:
        """
        Write or create the given file from the contents.
        Return True if the original file was changed.
        """
        at, c = self, self.c
        if root:
            root.clearDirty()
        #
        # Create the timestamp (only for messages).
        if c.config.getBool('log-show-save-time', default=False):  # pragma: no cover
            format = c.config.getString('log-timestamp-format') or "%H:%M:%S"
            timestamp = time.strftime(format) + ' '
        else:
            timestamp = ''
        #
        # Adjust the contents.
        assert isinstance(contents, str), g.callers()
        if at.output_newline != '\n':  # pragma: no cover
            contents = contents.replace('\r', '').replace('\n', at.output_newline)
        #
        # If file does not exist, create it from the contents.
        fileName = g.os_path_realpath(fileName)
        sfn = g.shortFileName(fileName)
        if not g.os_path_exists(fileName):
            ok = g.writeFile(contents, encoding, fileName)
            if ok:
                c.setFileTimeStamp(fileName)
                if not g.unitTesting:
                    g.es(f"{timestamp}created: {fileName}")  # pragma: no cover
                if root:
                    # Fix bug 889175: Remember the full fileName.
                    at.rememberReadPath(fileName, root)
                    at.checkPythonCode(contents, fileName, root)
            else:
                at.addToOrphanList(root)  # pragma: no cover
            # No original file to change. Return value tested by a unit test.
            return False  # No change to original file.
        #
        # Compare the old and new contents.
        old_contents = g.readFileIntoUnicodeString(fileName,
            encoding=at.encoding, silent=True)
        if not old_contents:
            old_contents = ''
        unchanged = (
            contents == old_contents
            or (not at.explicitLineEnding and at.compareIgnoringLineEndings(old_contents, contents))
            or ignoreBlankLines and at.compareIgnoringBlankLines(old_contents, contents))
        if unchanged:
            at.unchangedFiles += 1
            if not g.unitTesting and c.config.getBool(
                'report-unchanged-files', default=True):
                g.es(f"{timestamp}unchanged: {sfn}")  # pragma: no cover
            # Check unchanged files.
            at.checkUnchangedFiles(contents, fileName, root)
            return False  # No change to original file.
        #
        # Warn if we are only adjusting the line endings.
        if at.explicitLineEnding:  # pragma: no cover
            ok = (
                at.compareIgnoringLineEndings(old_contents, contents) or
                ignoreBlankLines and at.compareIgnoringLineEndings(
                old_contents, contents))
            if not ok:
                g.warning("correcting line endings in:", fileName)
        #
        # Write a changed file.
        ok = g.writeFile(contents, encoding, fileName)
        if ok:
            c.setFileTimeStamp(fileName)
            if not g.unitTesting:
                g.es(f"{timestamp}wrote: {sfn}")  # pragma: no cover
        else:  # pragma: no cover
            g.error('error writing', sfn)
            g.es('not written:', sfn)
            at.addToOrphanList(root)
        # Check *after* writing the file.
        at.checkPythonCode(contents, fileName, root)
        return ok
    #@+node:ekr.20190114061452.27: *6* at.compareIgnoringBlankLines
    def compareIgnoringBlankLines(self, s1: str, s2: str) -> bool:  # pragma: no cover
        """Compare two strings, ignoring blank lines."""
        if s1 == s2:
            return True
        s1 = g.removeBlankLines(s1)
        s2 = g.removeBlankLines(s2)
        return s1 == s2
    #@+node:ekr.20190114061452.28: *6* at.compareIgnoringLineEndings
    def compareIgnoringLineEndings(self, s1: str, s2: str) -> bool:  # pragma: no cover
        """Compare two strings, ignoring line endings."""
        if s1 == s2:
            return True
        # Wrong: equivalent to ignoreBlankLines!
            # s1 = s1.replace('\n','').replace('\r','')
            # s2 = s2.replace('\n','').replace('\r','')
        s1 = s1.replace('\r', '')
        s2 = s2.replace('\r', '')
        return s1 == s2
    #@+node:ekr.20211029052041.1: *5* at.scanRootForSectionDelims
    def scanRootForSectionDelims(self, root: Position) -> None:
        """
        Scan root.b for an "@section-delims" directive.
        Set section_delim1 and section_delim2 ivars.
        """
        at = self
        # Set defaults.
        at.section_delim1 = '<<'
        at.section_delim2 = '>>'
        # Scan root.b.
        lines = []
        for s in g.splitLines(root.b):
            m = g.g_section_delims_pat.match(s)
            if m:
                lines.append(s)
                at.section_delim1 = m.group(1)
                at.section_delim2 = m.group(2)
        # Disallow multiple directives.
        if len(lines) > 1:  # pragma: no cover
            at.error(f"Multiple @section-delims directives in {root.h}")
            g.es_print('using default delims')
            at.section_delim1 = '<<'
            at.section_delim2 = '>>'
    #@+node:ekr.20090514111518.5665: *5* at.tabNannyNode
    def tabNannyNode(self, p: Position, body: str) -> None:
        try:
            readline = g.ReadLinesClass(body).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))
        except IndentationError:  # pragma: no cover
            if g.unitTesting:
                raise
            junk2, msg, junk = sys.exc_info()
            g.error("IndentationError in", p.h)
            g.es('', str(msg))
        except tokenize.TokenError:  # pragma: no cover
            if g.unitTesting:
                raise
            junk3, msg, junk = sys.exc_info()
            g.error("TokenError in", p.h)
            g.es('', str(msg))
        except tabnanny.NannyNag:  # pragma: no cover
            if g.unitTesting:
                raise
            junk4, nag, junk = sys.exc_info()
            badline = nag.get_lineno()
            line = nag.get_line()
            message = nag.get_msg()
            g.error("indentation error in", p.h, "line", badline)
            g.es(message)
            line2 = repr(str(line))[1:-1]
            g.es("offending line:\n", line2)
        except Exception:  # pragma: no cover
            g.trace("unexpected exception")
            g.es_exception()
            raise
    #@+node:ekr.20041005105605.216: *5* at.warnAboutOrpanAndIgnoredNodes
    # Called from putFile.

    def warnAboutOrphandAndIgnoredNodes(self) -> None:  # pragma: no cover
        # Always warn, even when language=="cweb"
        at, root = self, self.root
        if at.errors:
            return  # No need to repeat this.
        for p in root.self_and_subtree(copy=False):
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
                # #1050: test orphan bit.
                if p.isOrphan():
                    at.writeError("Orphan node: " + p.h)
                    if p.hasParent():
                        g.blue("parent node:", p.parent().h)
                p.moveToThreadNext()
    #@+node:ekr.20041005105605.217: *5* at.writeError
    def writeError(self, message: str) -> None:  # pragma: no cover
        """Issue an error while writing an @<file> node."""
        at = self
        if at.errors == 0:
            fn = at.targetFileName or 'unnamed file'
            g.es_error(f"errors writing: {fn}")
        at.error(message)
        at.addToOrphanList(at.root)
    #@+node:ekr.20041005105605.218: *5* at.writeException
    def writeException(self, fileName: str, root: Position) -> None:  # pragma: no cover
        at = self
        g.error("exception writing:", fileName)
        g.es_exception()
        if getattr(at, 'outputFile', None):
            at.outputFile.flush()
            at.outputFile.close()
            at.outputFile = None
        at.remove(fileName)
        at.addToOrphanList(root)
    #@+node:ekr.20041005105605.219: *3* at.Utilities
    #@+node:ekr.20041005105605.220: *4* at.error & printError
    def error(self, *args: Any) -> None:  # pragma: no cover
        at = self
        at.printError(*args)
        at.errors += 1

    def printError(self, *args: Any) -> None:  # pragma: no cover
        """Print an error message that may contain non-ascii characters."""
        at = self
        if at.errors:
            g.error(*args)
        else:
            g.warning(*args)
    #@+node:ekr.20041005105605.221: *4* at.exception
    def exception(self, message: str) -> None:  # pragma: no cover
        self.error(message)
        g.es_exception()
    #@+node:ekr.20050104131929: *4* at.file operations...
    # Error checking versions of corresponding functions in Python's os module.
    #@+node:ekr.20050104131820: *5* at.chmod
    def chmod(self, fileName: str, mode: Any) -> None:  # pragma: no cover
        # Do _not_ call self.error here.
        if mode is None:
            return
        try:
            os.chmod(fileName, mode)
        except Exception:
            g.es("exception in os.chmod", fileName)
            g.es_exception()

    #@+node:ekr.20050104132018: *5* at.remove
    def remove(self, fileName: str) -> bool:  # pragma: no cover
        if not fileName:
            g.trace('No file name', g.callers())
            return False
        try:
            os.remove(fileName)
            return True
        except Exception:
            if not g.unitTesting:
                self.error(f"exception removing: {fileName}")
                g.es_exception()
            return False
    #@+node:ekr.20050104132026: *5* at.stat
    def stat(self, fileName: str) -> Any:  # pragma: no cover
        """Return the access mode of named file, removing any setuid, setgid, and sticky bits."""
        # Do _not_ call self.error here.
        try:
            mode = (os.stat(fileName))[0] & (7 * 8 * 8 + 7 * 8 + 7)  # 0777
        except Exception:
            mode = None
        return mode

    #@+node:ekr.20090530055015.6023: *4* at.get/setPathUa
    def getPathUa(self, p: Position) -> str:
        if hasattr(p.v, 'tempAttributes'):
            d = p.v.tempAttributes.get('read-path', {})
            return d.get('path')  # type:ignore
        return ''

    def setPathUa(self, p: Position, path: Any) -> None:
        if not hasattr(p.v, 'tempAttributes'):
            p.v.tempAttributes = {}
        d = p.v.tempAttributes.get('read-path', {})
        d['path'] = path
        p.v.tempAttributes['read-path'] = d
    #@+node:ekr.20090712050729.6017: *4* at.promptForDangerousWrite
    def promptForDangerousWrite(self, fileName: str, message: str = None) -> bool:  # pragma: no cover
        """Raise a dialog asking the user whether to overwrite an existing file."""
        at, c, root = self, self.c, self.root
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
            message = (
                f"{g.splitLongFileName(fileName)}\n"
                f"{g.tr('already exists.')}\n"
                f"{g.tr('Overwrite this file?')}")
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
    def rememberReadPath(self, fn: str, p: Position) -> None:
        """
        Remember the files that have been read *and*
        the full headline (@<file> type) that caused the read.
        """
        v = p.v
        # Fix bug #50: body text lost switching @file to @auto-rst
        if not hasattr(v, 'at_read'):
            v.at_read = {}  # pragma: no cover
        d = v.at_read
        aSet = d.get(fn, set())
        aSet.add(p.h)
        d[fn] = aSet
    #@+node:ekr.20080923070954.4: *4* at.scanAllDirectives
    def scanAllDirectives(self, p: Position) -> dict[str, Any]:
        """
        Scan p and p's ancestors looking for directives,
        setting corresponding AtFile ivars.
        """
        at, c = self, self.c
        d = c.scanAllDirectives(p)
        #
        # Language & delims: Tricky.
        lang_dict = d.get('lang-dict') or {}
        delims, language = None, None
        if lang_dict:
            # There was an @delims or @language directive.
            language = lang_dict.get('language')
            delims = lang_dict.get('delims')
        if not language:
            # No language directive.  Look for @<file> nodes.
            # Do *not* use d.get('language')!
            language = g.getLanguageFromAncestorAtFileNode(p) or 'python'
        at.language = language
        if not delims:
            delims = g.set_delims_from_language(language)
        #
        # Previously, setting delims was sometimes skipped, depending on kwargs.
        #@+<< Set comment strings from delims >>
        #@+node:ekr.20080923070954.13: *5* << Set comment strings from delims >> (at.scanAllDirectives)
        delim1, delim2, delim3 = delims
        # Use single-line comments if we have a choice.
        # delim1,delim2,delim3 now correspond to line,start,end
        if delim1:
            at.startSentinelComment = delim1
            at.endSentinelComment = ""  # Must not be None.
        elif delim2 and delim3:
            at.startSentinelComment = delim2
            at.endSentinelComment = delim3
        else:  # pragma: no cover
            #
            # Emergency!
            #
            # Issue an error only if at.language has been set.
            # This suppresses a message from the markdown importer.
            if not g.unitTesting and at.language:
                g.trace(repr(at.language), g.callers())
                g.es_print("unknown language: using Python comment delimiters")
                g.es_print("c.target_language:", c.target_language)
            at.startSentinelComment = "#"  # This should never happen!
            at.endSentinelComment = ""
        #@-<< Set comment strings from delims >>
        #
        # Easy cases
        at.encoding = d.get('encoding') or c.config.default_derived_file_encoding
        lineending = d.get('lineending')
        at.explicitLineEnding = bool(lineending)
        at.output_newline = lineending or g.getOutputNewline(c=c)
        at.page_width = d.get('pagewidth') or c.page_width
        at.tab_width = d.get('tabwidth') or c.tab_width
        return {
            "encoding": at.encoding,
            "language": at.language,
            "lineending": at.output_newline,
            "pagewidth": at.page_width,
            "path": d.get('path'),
            "tabwidth": at.tab_width,
        }
    #@+node:ekr.20120110174009.9965: *4* at.shouldPromptForDangerousWrite
    def shouldPromptForDangerousWrite(self, fn: str, p: Position) -> bool:  # pragma: no cover
        """
        Return True if Leo should warn the user that p is an @<file> node that
        was not read during startup. Writing that file might cause data loss.

        See #50: https://github.com/leo-editor/leo-editor/issues/50
        """
        trace = 'save' in g.app.debug
        sfn = g.shortFileName(fn)
        c = self.c
        efc = g.app.externalFilesController
        if p.isAtNoSentFileNode():
            # #1450.
            # No danger of overwriting a file.
            # It was never read.
            return False
        if not g.os_path_exists(fn):
            # No danger of overwriting fn.
            if trace:
                g.trace('Return False: does not exist:', sfn)
            return False
        # #1347: Prompt if the external file is newer.
        if efc:
            # Like c.checkFileTimeStamp.
            if c.sqlite_connection and c.mFileName == fn:
                # sqlite database file is never actually overwritten by Leo,
                # so do *not* check its timestamp.
                pass
            elif efc.has_changed(fn):
                if trace:
                    g.trace('Return True: changed:', sfn)
                return True
        if hasattr(p.v, 'at_read'):
            # Fix bug #50: body text lost switching @file to @auto-rst
            d = p.v.at_read
            for k in d:
                # Fix bug # #1469: make sure k still exists.
                if (
                    os.path.exists(k) and os.path.samefile(k, fn)
                    and p.h in d.get(k, set())
                ):
                    d[fn] = d[k]
                    if trace:
                        g.trace('Return False: in p.v.at_read:', sfn)
                    return False
            aSet = d.get(fn, set())
            if trace:
                g.trace(f"Return {p.h} not in aSet(): {sfn}")
            return p.h not in aSet
        if trace:
            g.trace('Return True: never read:', sfn)
        return True  # The file was never read.
    #@+node:ekr.20041005105605.20: *4* at.warnOnReadOnlyFile
    def warnOnReadOnlyFile(self, fn: str) -> None:
        # os.access() may not exist on all platforms.
        try:
            read_only = not os.access(fn, os.W_OK)
        except AttributeError:  # pragma: no cover
            read_only = False
        if read_only:
            g.error("read only:", fn)  # pragma: no cover
    #@-others
atFile = AtFile  # compatibility
#@+node:ekr.20180602102448.1: ** class FastAtRead
class FastAtRead:
    """
    Read an external file, created from an @file tree.
    This is Vitalije's code, edited by EKR.
    """

    #@+others
    #@+node:ekr.20211030193146.1: *3* fast_at.__init__
    def __init__(self, c: Cmdr, gnx2vnode: dict[str, VNode]) -> None:

        self.c = c
        assert gnx2vnode is not None
        self.gnx2vnode: dict[str, VNode] = gnx2vnode  # The global fc.gnxDict. Keys are gnx's, values are vnodes.
        self.path: str = None
        self.root: Position = None
        # compiled patterns...
        self.after_pat: re.Pattern = None
        self.all_pat: re.Pattern = None
        self.code_pat: re.Pattern = None
        self.comment_pat: re.Pattern = None
        self.delims_pat: re.Pattern = None
        self.doc_pat: re.Pattern = None
        self.first_pat: re.Pattern = None
        self.last_pat: re.Pattern = None
        self.node_start_pat: re.Pattern = None
        self.others_pat: re.Pattern = None
        self.ref_pat: re.Pattern = None
        self.section_delims_pat: re.Pattern = None
    #@+node:ekr.20180602103135.3: *3* fast_at.get_patterns
    #@@nobeautify

    def get_patterns(self, comment_delims: Any) -> None:
        """Create regex patterns for the given comment delims."""
        # This must be a function, because of @comments & @delims.
        comment_delim_start, comment_delim_end = comment_delims
        delim1 = re.escape(comment_delim_start)
        delim2 = re.escape(comment_delim_end or '')
        ref = g.angleBrackets(r'(.*)')
        table = (
            # Note: Do *not* alter these regexes to handle black-compatible sentinels!
            #       delim1 *already* contains the trailing blank!

            # These patterns must be mutually exclusive.
            ('after',       fr'^\s*{delim1}@afterref{delim2}$'),             # @afterref
            ('all',         fr'^(\s*){delim1}@(\+|-)all\b(.*){delim2}$'),    # @all
            ('code',        fr'^\s*{delim1}@@c(ode)?{delim2}$'),             # @c and @code
            ('comment',     fr'^\s*{delim1}@@comment(.*){delim2}'),          # @comment
            ('delims',      fr'^\s*{delim1}@delims(.*){delim2}'),            # @delims
            ('doc',         fr'^\s*{delim1}@\+(at|doc)?(\s.*?)?{delim2}\n'), # @doc or @
            ('first',       fr'^\s*{delim1}@@first{delim2}$'),               # @first
            ('last',        fr'^\s*{delim1}@@last{delim2}$'),                # @last
            #@verbatim
            # @node
            ('node_start',  fr'^(\s*){delim1}@\+node:([^:]+): \*(\d+)?(\*?) (.*){delim2}$'),
            ('others',      fr'^(\s*){delim1}@(\+|-)others\b(.*){delim2}$'), # @others
            ('ref',         fr'^(\s*){delim1}@(\+|-){ref}\s*{delim2}$'),     # section ref
            #@verbatim
            # @section-delims
            ('section_delims', fr'^\s*{delim1}@@section-delims[ \t]+([^ \w\n\t]+)[ \t]+([^ \w\n\t]+)[ \t]*{delim2}$'),
        )
        # Set the ivars.
        for (name, pattern) in table:
            ivar = f"{name}_pat"
            assert hasattr(self, ivar), ivar
            setattr(self, ivar, re.compile(pattern))
    #@+node:ekr.20180602103135.2: *3* fast_at.scan_header
    header_pattern = re.compile(
        r'''
        ^(.+)@\+leo
        (-ver=(\d+))?
        (-thin)?
        (-encoding=(.*)(\.))?
        (.*)$''',
        re.VERBOSE,
    )

    def scan_header(self, lines: Any) -> Optional[tuple[Any, Any, Any]]:
        """
        Scan for the header line, which follows any @first lines.
        Return (delims, first_lines, i+1) or None

        Important: delims[0] will end with a blank when reading a file with blackened sentinels!
                   This fact eliminates all special cases in scan_lines!
        """
        first_lines: list[str] = []
        i = 0  # To keep some versions of pylint happy.
        for i, line in enumerate(lines):
            m = self.header_pattern.match(line)
            if m:
                delims = m.group(1), m.group(8) or ''
                return delims, first_lines, i + 1
            first_lines.append(line)
        return None  # pragma: no cover (defensive)
    #@+node:ekr.20180602103135.8: *3* fast_at.scan_lines
    def scan_lines(self, comment_delims: Any, first_lines: Any, lines: Any, path: Any, start: Any) -> None:
        """Scan all lines of the file, creating vnodes."""
        #@+<< init scan_lines >>
        #@+node:ekr.20180602103135.9: *4* << init scan_lines >>
        #
        # Simple vars...
        afterref = False  # True: the next line follows @afterref.
        clone_v: VNode = None  # The root of the clone tree.
        # The start/end *comment* delims.
        # Important: scan_header ends comment_delim1 with a blank when using black sentinels.
        comment_delim1, comment_delim2 = comment_delims
        doc_skip = (comment_delim1 + '\n', comment_delim2 + '\n')  # To handle doc parts.
        first_i = 0  # Index into first array.
        in_doc = False  # True: in @doc parts.
        is_cweb = comment_delim1 == '@q@' and comment_delim2 == '@>'  # True: cweb hack in effect.
        indent = 0  # The current indentation.
        level_stack: list[tuple[VNode, VNode]] = []
        n_last_lines = 0  # The number of @@last directives seen.
        root_gnx_adjusted = False  # True: suppress final checks.
        # #1065 so reads will not create spurious child nodes.
        root_seen = False  # False: The next +@node sentinel denotes the root, regardless of gnx.
        section_delim1 = '<<'
        section_delim2 = '>>'
        section_reference_seen = False
        sentinel = comment_delim1 + '@'
        # The stack is updated when at+others, at+<section>, or at+all is seen.
        stack: list[tuple[str, int, str]] = []  # Entries are (gnx, indent, body)
        verbatim_line = comment_delim1 + '@verbatim' + comment_delim2
        verbatim = False  # True: the next line must be added without change.
        #
        # Init the parent vnode.
        #
        root_gnx = gnx = self.root.gnx
        context = self.c
        parent_v = self.root.v
        root_v = parent_v  # Does not change.
        level_stack.append((root_v, None))
        #
        # Init the gnx dict last.
        #
        gnx2vnode = self.gnx2vnode  # Keys are gnx's, values are vnodes.
        gnx2body = {}  # Keys are gnxs, values are list of body lines.
        gnx2vnode[gnx] = parent_v  # Add gnx to the keys
        # Add gnx to the keys.
        # Body is the list of lines presently being accumulated.
        gnx2body[gnx] = body = first_lines
        #
        # Set the patterns
        self.get_patterns(comment_delims)
        #@-<< init scan_lines >>
        i = 0  # To keep pylint happy.
        for i, line in enumerate(lines[start:]):
            # Strip the line only once.
            strip_line = line.strip()
            if afterref:
                #@+<< handle afterref line>>
                #@+node:ekr.20211102052251.1: *4* << handle afterref line >>
                if body:  # a list of lines.
                    body[-1] = body[-1].rstrip() + line
                else:
                    body = [line]  # pragma: no cover
                afterref = False
                #@-<< handle afterref line>>
                continue
            if verbatim:
                #@+<< handle verbatim line >>
                #@+node:ekr.20211102052518.1: *4* << handle verbatim line >>
                # Previous line was verbatim *sentinel*. Append this line as it is.

                # 2022/12/02: Bug fix: adjust indentation.
                if indent and line[:indent].isspace() and len(line) > indent:
                    line = line[indent:]

                body.append(line)
                verbatim = False
                #@-<< handle verbatim line >>
                continue
            if strip_line == verbatim_line:  # <delim>@verbatim
                verbatim = True
                continue
            #@+<< finalize line >>
            #@+node:ekr.20180602103135.10: *4* << finalize line >>
            # Undo the cweb hack.
            if is_cweb and line.startswith(sentinel):
                line = line[: len(sentinel)] + line[len(sentinel) :].replace('@@', '@')
            # Adjust indentation.
            if indent and line[:indent].isspace() and len(line) > indent:
                line = line[indent:]
            #@-<< finalize line >>
            if not in_doc and not strip_line.startswith(sentinel):  # Faster than a regex!
                body.append(line)
                continue
            # These three sections might clear in_doc.
            #@+<< handle @others >>
            #@+node:ekr.20180602103135.14: *4* << handle @others >>
            m = self.others_pat.match(line)
            if m:
                in_doc = False
                if m.group(2) == '+':  # opening sentinel
                    body.append(f"{m.group(1)}@others{m.group(3) or ''}\n")
                    stack.append((gnx, indent, body))
                    indent += m.end(1)  # adjust current indentation
                else:  # closing sentinel.
                    # m.group(2) is '-' because the pattern matched.
                    try:
                        gnx, indent, body = stack.pop()
                    except IndexError:  # pragma: no cover
                        # #2624: This can happen during git-diff.
                        pass
                continue
            #@-<< handle @others >>
            #@+<< handle section refs >>
            #@+node:ekr.20180602103135.18: *4* << handle section refs >>
            # Note: scan_header sets *comment* delims, not *section* delims.
            # This section coordinates with the section that handles @section-delims.
            m = self.ref_pat.match(line)
            if m:
                in_doc = False
                if m.group(2) == '+':
                    # Any later @section-delims directive is a serious error.
                    # This kind of error should have been caught by Leo's atFile write logic.
                    section_reference_seen = True
                    # open sentinel.
                    body.append(m.group(1) + section_delim1 + m.group(3) + section_delim2 + '\n')
                    stack.append((gnx, indent, body))
                    indent += m.end(1)
                elif stack:
                    # m.group(2) is '-' because the pattern matched.
                    gnx, indent, body = stack.pop()  # #1232: Only if the stack exists.
                continue  # 2021/10/29: *always* continue.
            #@-<< handle section refs >>
            #@+<< handle node_start >>
            #@+node:ekr.20180602103135.19: *4* << handle node_start >>
            m = self.node_start_pat.match(line)
            if m:
                in_doc = False
                gnx, head = m.group(2), m.group(5)
                # m.group(3) is the level number, m.group(4) is the number of stars.
                level = int(m.group(3)) if m.group(3) else 1 + len(m.group(4))
                v = gnx2vnode.get(gnx)
                #
                # Case 1: The root @file node. Don't change the headline.
                if not root_seen and not v and not g.unitTesting:
                    # Don't warn about a gnx mismatch in the root.
                    root_gnx_adjusted = True  # pragma: no cover
                if not root_seen:
                    # Fix #1064: The node represents the root, regardless of the gnx!
                    root_seen = True
                    clone_v = None
                    gnx2body[gnx] = body = []
                    # This case can happen, but not in unit tests.
                    if not v:  # pragma: no cover
                        # Fix #1064.
                        v = root_v
                        # This message is annoying when using git-diff.
                            # if gnx != root_gnx:
                                # g.es_print("using gnx from external file: %s" % (v.h), color='blue')
                        gnx2vnode[gnx] = v
                        v.fileIndex = gnx
                    v.children = []
                    continue
                #
                # Case 2: We are scanning the descendants of a clone.
                parent_v, clone_v = level_stack[level - 2]
                if v and clone_v:
                    # The last version of the body and headline wins..
                    gnx2body[gnx] = body = []
                    v._headString = head
                    # Update the level_stack.
                    level_stack = level_stack[: level - 1]
                    level_stack.append((v, clone_v))
                    # Always clear the children!
                    v.children = []
                    parent_v.children.append(v)
                    continue
                #
                # Case 3: we are not already scanning the descendants of a clone.
                if v:
                    # The *start* of a clone tree. Reset the children.
                    clone_v = v
                    v.children = []
                else:
                    # Make a new vnode.
                    v = leoNodes.VNode(context=context, gnx=gnx)
                #
                # The last version of the body and headline wins.
                gnx2vnode[gnx] = v
                gnx2body[gnx] = body = []
                v._headString = head
                #
                # Update the stack.
                level_stack = level_stack[: level - 1]
                level_stack.append((v, clone_v))
                #
                # Update the links.
                assert v != root_v
                parent_v.children.append(v)
                v.parents.append(parent_v)
                continue
            #@-<< handle node_start >>
            if in_doc:
                #@+<< handle @c or @code >>
                #@+node:ekr.20211031033532.1: *4* << handle @c or @code >>
                # When delim_end exists the doc block:
                # - begins with the opening delim, alone on its own line
                # - ends with the closing delim, alone on its own line.
                # Both of these lines should be skipped.
                #
                # #1496: Retire the @doc convention.
                #        An empty line is no longer a sentinel.
                if comment_delim2 and line in doc_skip:
                    # doc_skip is (comment_delim1 + '\n', delim_end + '\n')
                    continue
                #
                # Check for @c or @code.
                m = self.code_pat.match(line)
                if m:
                    in_doc = False
                    body.append('@code\n' if m.group(1) else '@c\n')
                    continue
                #@-<< handle @c or @code >>
            else:
                #@+<< handle @ or @doc >>
                #@+node:ekr.20211031033754.1: *4* << handle @ or @doc >>
                m = self.doc_pat.match(line)
                if m:
                    #@verbatim
                    # @+at or @+doc?
                    doc = '@doc' if m.group(1) == 'doc' else '@'
                    doc2 = m.group(2) or ''  # Trailing text.
                    if doc2:
                        body.append(f"{doc}{doc2}\n")
                    else:
                        body.append(doc + '\n')
                    # Enter @doc mode.
                    in_doc = True
                    continue
                #@-<< handle @ or @doc >>
            if line.startswith(comment_delim1 + '@-leo'):  # Faster than a regex!
                # The @-leo sentinel adds *nothing* to the text.
                i += 1
                break
            # Order doesn't matter.
            #@+<< handle @all >>
            #@+node:ekr.20180602103135.13: *4* << handle @all >>
            m = self.all_pat.match(line)
            if m:
                #@verbatim
                # @all tells Leo's *write* code not to check for undefined sections.
                # Here, in the read code, we merely need to add it to the body.
                # Pushing and popping the stack may not be necessary, but it can't hurt.
                if m.group(2) == '+':  # opening sentinel
                    body.append(f"{m.group(1)}@all{m.group(3) or ''}\n")
                    stack.append((gnx, indent, body))
                else:  # closing sentinel.
                    # m.group(2) is '-' because the pattern matched.
                    gnx, indent, body = stack.pop()
                    gnx2body[gnx] = body
                continue
            #@-<< handle @all >>
            #@+<< handle afterref >>
            #@+node:ekr.20180603063102.1: *4* << handle afterref >>
            m = self.after_pat.match(line)
            if m:
                afterref = True
                continue
            #@-<< handle afterref >>
            #@+<< handle @first and @last >>
            #@+node:ekr.20180606053919.1: *4* << handle @first and @last >>
            m = self.first_pat.match(line)
            if m:
                # pylint: disable=no-else-continue
                if 0 <= first_i < len(first_lines):
                    body.append('@first ' + first_lines[first_i])
                    first_i += 1
                    continue
                else:  # pragma: no cover
                    g.trace(f"\ntoo many @first lines: {path}")
                    print('@first is valid only at the start of @<file> nodes\n')
                    g.printObj(first_lines, tag='first_lines')
                    g.printObj(lines[start : i + 2], tag='lines[start:i+2]')
                    continue
            m = self.last_pat.match(line)
            if m:
                # Just increment the count of the expected last lines.
                # We'll fill in the @last line directives after we see the @-leo directive.
                n_last_lines += 1
                continue
            #@-<< handle @first and @last >>
            #@+<< handle @comment >>
            #@+node:ekr.20180621050901.1: *4* << handle @comment >>
            # https://leo-editor.github.io/leo-editor/directives.html#part-4-dangerous-directives
            m = self.comment_pat.match(line)
            if m:
                # <1, 2 or 3 comment delims>
                delims = m.group(1).strip()
                # Whatever happens, retain the @delims line.
                body.append(f"@comment {delims}\n")
                delim1, delim2, delim3 = g.set_delims_from_string(delims)
                # delim1 is always the single-line delimiter.
                if delim1:
                    comment_delim1, comment_delim2 = delim1, ''
                else:
                    comment_delim1, comment_delim2 = delim2, delim3
                #
                # Within these delimiters:
                # - double underscores represent a newline.
                # - underscores represent a significant space,
                comment_delim1 = comment_delim1.replace('__', '\n').replace('_', ' ')
                comment_delim2 = comment_delim2.replace('__', '\n').replace('_', ' ')
                # Recalculate all delim-related values
                doc_skip = (comment_delim1 + '\n', comment_delim2 + '\n')
                is_cweb = comment_delim1 == '@q@' and comment_delim2 == '@>'
                sentinel = comment_delim1 + '@'
                #
                # Recalculate the patterns.
                comment_delims = comment_delim1, comment_delim2
                self.get_patterns(comment_delims)
                continue
            #@-<< handle @comment >>
            #@+<< handle @delims >>
            #@+node:ekr.20180608104836.1: *4* << handle @delims >>
            m = self.delims_pat.match(line)
            if m:
                # Get 1 or 2 comment delims
                # Whatever happens, retain the original @delims line.
                delims = m.group(1).strip()
                body.append(f"@delims {delims}\n")
                #
                # Parse the delims.
                self.delims_pat = re.compile(r'^([^ ]+)\s*([^ ]+)?')
                m2 = self.delims_pat.match(delims)
                if not m2:  # pragma: no cover
                    g.trace(f"Ignoring invalid @delims: {line!r}")
                    continue
                comment_delim1 = m2.group(1)
                comment_delim2 = m2.group(2) or ''
                #
                # Within these delimiters:
                # - double underscores represent a newline.
                # - underscores represent a significant space,
                comment_delim1 = comment_delim1.replace('__', '\n').replace('_', ' ')
                comment_delim2 = comment_delim2.replace('__', '\n').replace('_', ' ')
                # Recalculate all delim-related values
                doc_skip = (comment_delim1 + '\n', comment_delim2 + '\n')
                is_cweb = comment_delim1 == '@q@' and comment_delim2 == '@>'
                sentinel = comment_delim1 + '@'
                #
                # Recalculate the patterns
                comment_delims = comment_delim1, comment_delim2
                self.get_patterns(comment_delims)
                continue
            #@-<< handle @delims >>
            #@+<< handle @section-delims >>
            #@+node:ekr.20211030033211.1: *4* << handle @section-delims >>
            m = self.section_delims_pat.match(line)
            if m:
                if section_reference_seen:  # pragma: no cover
                    # This is a serious error.
                    # This kind of error should have been caught by Leo's atFile write logic.
                    g.es_print('section-delims seen after a section reference', color='red')
                else:
                    # Carefully update the section reference pattern!
                    section_delim1 = d1 = re.escape(m.group(1))
                    section_delim2 = d2 = re.escape(m.group(2) or '')
                    self.ref_pat = re.compile(fr'^(\s*){comment_delim1}@(\+|-){d1}(.*){d2}\s*{comment_delim2}$')
                body.append(f"@section-delims {m.group(1)} {m.group(2)}\n")
                continue
            #@-<< handle @section-delims >>
            # These sections must be last, in this order.
            #@+<< handle remaining @@ lines >>
            #@+node:ekr.20180603135602.1: *4* << handle remaining @@ lines >>
            #@verbatim
            # @first, @last, @delims and @comment generate @@ sentinels,
            # So this must follow all of those.
            if line.startswith(comment_delim1 + '@@'):
                ii = len(comment_delim1) + 1  # on second '@'
                jj = line.rfind(comment_delim2) if comment_delim2 else -1
                body.append(line[ii:jj] + '\n')
                continue
            #@-<< handle remaining @@ lines >>
            if in_doc:
                #@+<< handle remaining @doc lines >>
                #@+node:ekr.20180606054325.1: *4* << handle remaining @doc lines >>
                if comment_delim2:
                    # doc lines are unchanged.
                    body.append(line)
                    continue

                #    with --black-sentinels: comment_delim1 ends with a blank.
                # without --black-sentinels: comment_delim1 does *not* end with a blank.

                tail = line.lstrip()[len(comment_delim1.rstrip()) + 1 :]
                if tail.strip():
                    body.append(tail)
                else:
                    body.append('\n')
                continue
                #@-<< handle remaining @doc lines >>
            #@+<< handle remaining @ lines >>
            #@+node:ekr.20180602103135.17: *4* << handle remaining @ lines >>
            # Handle an apparent sentinel line.
            # This *can* happen after the git-diff or refresh-from-disk commands.
            #
            if 1:  # pragma: no cover (defensive)

                # This assert verifies the short-circuit test.
                assert strip_line.startswith(sentinel), repr(line)

                # Defensive: make *sure* we ignore verbatim lines.
                if strip_line == verbatim_line:
                    g.trace('Ignore bad @verbatim sentinel', repr(line))
                else:
                    # A useful trace.
                    g.trace(
                        f"{g.shortFileName(self.path)}: "
                        f"warning: inserting unexpected line: {line.rstrip()!r}"
                    )
                    # #2213: *Do* insert the line, with a warning.
                    body.append(line)
            #@-<< handle remaining @ lines >>
        else:
            # No @-leo sentinel!
            return  # pragma: no cover
        #@+<< final checks >>
        #@+node:ekr.20211104054823.1: *4* << final checks >>
        if g.unitTesting:
            # Unit tests must use the proper value for root.gnx.
            assert not root_gnx_adjusted
            assert not stack, stack
            assert root_gnx == gnx, (root_gnx, gnx)
        elif root_gnx_adjusted:  # pragma: no cover
            pass  # Don't check!
        elif stack:  # pragma: no cover
            g.error('scan_lines: Stack should be empty')
            g.printObj(stack, tag='stack')
        elif root_gnx != gnx:  # pragma: no cover
            g.error('scan_lines: gnx error')
            g.es_print(f"root_gnx: {root_gnx} != gnx: {gnx}")
        #@-<< final checks >>
        #@+<< insert @last lines >>
        #@+node:ekr.20211103101453.1: *4* << insert @last lines >>
        tail_lines = lines[start + i :]
        if tail_lines:
            # Convert the trailing lines to @last directives.
            last_lines = [f"@last {z.rstrip()}\n" for z in tail_lines]
            # Add the lines to the dictionary of lines.
            gnx2body[gnx] = gnx2body[gnx] + last_lines
            # Warn if there is an unexpected number of last lines.
            if n_last_lines != len(last_lines):  # pragma: no cover
                n1 = n_last_lines
                n2 = len(last_lines)
                g.trace(f"Expected {n1} trailing line{g.plural(n1)}, got {n2}")
        #@-<< insert @last lines >>
        #@+<< post pass: set all body text>>
        #@+node:ekr.20211104054426.1: *4* << post pass: set all body text>>
        # Set the body text.
        assert root_v.gnx in gnx2vnode, root_v
        assert root_v.gnx in gnx2body, root_v
        for key in gnx2body:
            body = gnx2body.get(key)
            v = gnx2vnode.get(key)
            assert v, (key, v)
            v._bodyString = g.toUnicode(''.join(body))
        #@-<< post pass: set all body text>>
    #@+node:ekr.20180603170614.1: *3* fast_at.read_into_root
    def read_into_root(self, contents: str, path: str, root: Position) -> bool:
        """
        Parse the file's contents, creating a tree of vnodes
        anchored in root.v.
        """
        self.path = path
        self.root = root
        sfn = g.shortFileName(path)
        contents = contents.replace('\r', '')
        lines = g.splitLines(contents)
        data = self.scan_header(lines)
        if not data:  # pragma: no cover
            g.trace(f"Invalid external file: {sfn}")
            return False
        # Clear all children.
        # Previously, this had been done in readOpenFile.
        root.v._deleteAllChildren()
        comment_delims, first_lines, start_i = data
        self.scan_lines(comment_delims, first_lines, lines, path, start_i)
        return True
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo

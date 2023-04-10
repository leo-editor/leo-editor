#@+leo-ver=5-thin
#@+node:ekr.20180212072657.2: * @file leoCompare.py
"""Leo's base compare class."""
#@+<< leoCompare imports & annotations >>
#@+node:ekr.20220901161941.1: ** << leoCompare imports & annotations >>
from __future__ import annotations
import difflib
import filecmp
import os
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode
#@-<< leoCompare imports & annotations >>

#@+others
#@+node:ekr.20031218072017.3633: ** class LeoCompare
class BaseLeoCompare:
    """The base class for Leo's compare code."""
    #@+others
    #@+node:ekr.20031218072017.3634: *3* compare.__init__
    # All these ivars are known to the LeoComparePanel class.

    def __init__(
        self,  # Keyword arguments are much convenient and more clear for scripts.
        commands: Cmdr = None,
        appendOutput: bool = False,
        ignoreBlankLines: bool = True,
        ignoreFirstLine1: bool = False,
        ignoreFirstLine2: bool = False,
        ignoreInteriorWhitespace: bool = False,
        ignoreLeadingWhitespace: bool = True,
        ignoreSentinelLines: bool = False,
        limitCount: int = 0,  # Zero means don't stop.
        limitToExtension: str = ".py",  # For directory compares.
        makeWhitespaceVisible: bool = True,
        printBothMatches: bool = False,
        printMatches: bool = False,
        printMismatches: bool = True,
        printTrailingMismatches: bool = False,
        outputFileName: str = None,
    ) -> None:
        # It is more convenient for the LeoComparePanel to set these directly.
        self.c = commands
        self.appendOutput = appendOutput
        self.ignoreBlankLines = ignoreBlankLines
        self.ignoreFirstLine1 = ignoreFirstLine1
        self.ignoreFirstLine2 = ignoreFirstLine2
        self.ignoreInteriorWhitespace = ignoreInteriorWhitespace
        self.ignoreLeadingWhitespace = ignoreLeadingWhitespace
        self.ignoreSentinelLines = ignoreSentinelLines
        self.limitCount = limitCount
        self.limitToExtension = limitToExtension
        self.makeWhitespaceVisible = makeWhitespaceVisible
        self.printBothMatches = printBothMatches
        self.printMatches = printMatches
        self.printMismatches = printMismatches
        self.printTrailingMismatches = printTrailingMismatches
        # For communication between methods...
        self.outputFileName = outputFileName
        self.fileName1 = None
        self.fileName2 = None
        # Open files...
        self.outputFile: BinaryIO = None
    #@+node:ekr.20031218072017.3635: *3* compare_directories (entry)
    # We ignore the filename portion of path1 and path2 if it exists.

    def compare_directories(self, path1: str, path2: str) -> None:
        # Ignore everything except the directory name.
        dir1 = g.os_path_dirname(path1)
        dir2 = g.os_path_dirname(path2)
        dir1 = g.os_path_normpath(dir1)
        dir2 = g.os_path_normpath(dir2)
        if dir1 == dir2:
            self.show("Please pick distinct directories.")
            return
        try:
            list1 = os.listdir(dir1)
        except Exception:
            self.show("invalid directory:" + dir1)
            return
        try:
            list2 = os.listdir(dir2)
        except Exception:
            self.show("invalid directory:" + dir2)
            return
        if self.outputFileName:
            self.openOutputFile()
        ok = self.outputFileName is None or self.outputFile
        if not ok:
            return
        # Create files and files2, the lists of files to be compared.
        files1 = []
        files2 = []
        for f in list1:
            junk, ext = g.os_path_splitext(f)
            if self.limitToExtension:
                if ext == self.limitToExtension:
                    files1.append(f)
            else:
                files1.append(f)
        for f in list2:
            junk, ext = g.os_path_splitext(f)
            if self.limitToExtension:
                if ext == self.limitToExtension:
                    files2.append(f)
            else:
                files2.append(f)
        # Compare the files and set the yes, no and missing lists.
        missing1, missing2, no, yes = [], [], [], []
        for f1 in files1:
            head, f2 = g.os_path_split(f1)
            if f2 in files2:
                try:
                    name1 = g.os_path_join(dir1, f1)
                    name2 = g.os_path_join(dir2, f2)
                    val = filecmp.cmp(name1, name2, 0)
                    if val:
                        yes.append(f1)
                    else:
                        no.append(f1)
                except Exception:
                    self.show("exception in filecmp.cmp")
                    g.es_exception()
                    missing1.append(f1)
            else:
                missing1.append(f1)
        for f2 in files2:
            head, f1 = g.os_path_split(f2)
            if f1 not in files1:
                missing2.append(f1)
        # Print the results.
        for kind, files in (
            ("----- matches --------", yes),
            ("----- mismatches -----", no),
            ("----- not found 1 ------", missing1),
            ("----- not found 2 ------", missing2),
        ):
            self.show(kind)
            for f in files:
                self.show(f)
        if self.outputFile:
            self.outputFile.close()
            self.outputFile = None
    #@+node:ekr.20031218072017.3636: *3* compare_files (entry)
    def compare_files(self, name1: str, name2: str) -> None:
        if name1 == name2:
            self.show("File names are identical.\nPlease pick distinct files.")
            return
        self.compare_two_files(name1, name2)
    #@+node:ekr.20180211123531.1: *3* compare_list_of_files (entry for scripts)
    def compare_list_of_files(self, aList1: List[str]) -> None:

        aList = list(set(aList1))
        while len(aList) > 1:
            path1 = aList[0]
            for path2 in aList[1:]:
                g.trace('COMPARE', path1, path2)
                self.compare_two_files(path1, path2)
    #@+node:ekr.20180211123741.1: *3* compare_two_files
    def compare_two_files(self, name1: str, name2: str) -> None:
        """A helper function."""
        f1 = f2 = None
        try:
            f1 = self.doOpen(name1)
            f2 = self.doOpen(name2)
            if self.outputFileName:
                self.openOutputFile()
            ok = self.outputFileName is None or self.outputFile
            ok1 = 1 if ok and ok != 0 else 0
            if f1 and f2 and ok1:
                # Don't compare if there is an error opening the output file.
                self.compare_open_files(f1, f2, name1, name2)
        except Exception:
            self.show("exception comparing files")
            g.es_exception()
        try:
            if f1:
                f1.close()
            if f2:
                f2.close()
            if self.outputFile:
                self.outputFile.close()
                self.outputFile = None
        except Exception:
            self.show("exception closing files")
            g.es_exception()
    #@+node:ekr.20031218072017.3637: *3* compare_lines
    def compare_lines(self, s1: str, s2: str) -> bool:
        if self.ignoreLeadingWhitespace:
            s1 = s1.lstrip()
            s2 = s2.lstrip()
        if self.ignoreInteriorWhitespace:
            k1 = g.skip_ws(s1, 0)
            k2 = g.skip_ws(s2, 0)
            ws1 = s1[:k1]
            ws2 = s2[:k2]
            tail1 = s1[k1:]
            tail2 = s2[k2:]
            tail1 = tail1.replace(" ", "").replace("\t", "")
            tail2 = tail2.replace(" ", "").replace("\t", "")
            s1 = ws1 + tail1
            s2 = ws2 + tail2
        return s1 == s2
    #@+node:ekr.20031218072017.3638: *3* compare_open_files
    def compare_open_files(self, f1: Any, f2: Any, name1: str, name2: str) -> None:
        # self.show("compare_open_files")
        lines1 = 0
        lines2 = 0
        mismatches = 0
        printTrailing = True
        sentinelComment1 = sentinelComment2 = None
        if self.openOutputFile():
            self.show("1: " + name1)
            self.show("2: " + name2)
            self.show("")
        s1 = s2 = None
        #@+<< handle opening lines >>
        #@+node:ekr.20031218072017.3639: *4* << handle opening lines >>
        if self.ignoreSentinelLines:
            s1 = g.readlineForceUnixNewline(f1)
            lines1 += 1
            s2 = g.readlineForceUnixNewline(f2)
            lines2 += 1
            # Note: isLeoHeader may return None.
            sentinelComment1 = self.isLeoHeader(s1)
            sentinelComment2 = self.isLeoHeader(s2)
            if not sentinelComment1:
                self.show("no @+leo line for " + name1)
            if not sentinelComment2:
                self.show("no @+leo line for " + name2)
        if self.ignoreFirstLine1:
            if s1 is None:
                g.readlineForceUnixNewline(f1)
                lines1 += 1
            s1 = None
        if self.ignoreFirstLine2:
            if s2 is None:
                g.readlineForceUnixNewline(f2)
                lines2 += 1
            s2 = None
        #@-<< handle opening lines >>
        while 1:
            if s1 is None:
                s1 = g.readlineForceUnixNewline(f1)
                lines1 += 1
            if s2 is None:
                s2 = g.readlineForceUnixNewline(f2)
                lines2 += 1
            #@+<< ignore blank lines and/or sentinels >>
            #@+node:ekr.20031218072017.3640: *4* << ignore blank lines and/or sentinels >>
            # Completely empty strings denotes end-of-file.
            if s1:
                if self.ignoreBlankLines and s1.isspace():
                    s1 = None
                    continue
                if self.ignoreSentinelLines and sentinelComment1 and self.isSentinel(
                    s1, sentinelComment1):
                    s1 = None
                    continue
            if s2:
                if self.ignoreBlankLines and s2.isspace():
                    s2 = None
                    continue
                if self.ignoreSentinelLines and sentinelComment2 and self.isSentinel(
                    s2, sentinelComment2):
                    s2 = None
                    continue
            #@-<< ignore blank lines and/or sentinels >>
            n1 = len(s1)
            n2 = len(s2)
            if n1 == 0 and n2 != 0:
                self.show("1.eof***:")
            if n2 == 0 and n1 != 0:
                self.show("2.eof***:")
            if n1 == 0 or n2 == 0:
                break
            match = self.compare_lines(s1, s2)
            if not match:
                mismatches += 1
            #@+<< print matches and/or mismatches >>
            #@+node:ekr.20031218072017.3641: *4* << print matches and/or mismatches >>
            if self.limitCount == 0 or mismatches <= self.limitCount:
                if match and self.printMatches:
                    if self.printBothMatches:
                        z1 = "1." + str(lines1)
                        z2 = "2." + str(lines2)
                        self.dump(z1.rjust(6) + ' :', s1)
                        self.dump(z2.rjust(6) + ' :', s2)
                    else:
                        self.dump(str(lines1).rjust(6) + ' :', s1)
                if not match and self.printMismatches:
                    z1 = "1." + str(lines1)
                    z2 = "2." + str(lines2)
                    self.dump(z1.rjust(6) + '*:', s1)
                    self.dump(z2.rjust(6) + '*:', s2)
            #@-<< print matches and/or mismatches >>
            #@+<< warn if mismatch limit reached >>
            #@+node:ekr.20031218072017.3642: *4* << warn if mismatch limit reached >>
            if self.limitCount > 0 and mismatches >= self.limitCount:
                if printTrailing:
                    self.show("")
                    self.show("limit count reached")
                    self.show("")
                    printTrailing = False
            #@-<< warn if mismatch limit reached >>
            s1 = s2 = None  # force a read of both lines.
        #@+<< handle reporting after at least one eof is seen >>
        #@+node:ekr.20031218072017.3643: *4* << handle reporting after at least one eof is seen >>
        if n1 > 0:
            lines1 += self.dumpToEndOfFile("1.", f1, s1, lines1, printTrailing)
        if n2 > 0:
            lines2 += self.dumpToEndOfFile("2.", f2, s2, lines2, printTrailing)
        self.show("")
        self.show("lines1:" + str(lines1))
        self.show("lines2:" + str(lines2))
        self.show("mismatches:" + str(mismatches))
        #@-<< handle reporting after at least one eof is seen >>
    #@+node:ekr.20031218072017.3644: *3* compare.filecmp
    def filecmp(self, f1: Any, f2: Any) -> bool:
        val = filecmp.cmp(f1, f2)
        if val:
            self.show("equal")
        else:
            self.show("*** not equal")
        return val
    #@+node:ekr.20031218072017.3645: *3* compare.utils...
    #@+node:ekr.20031218072017.3646: *4* compare.doOpen
    def doOpen(self, name: str) -> Optional[Any]:
        try:
            f = open(name, 'r')
            return f
        except Exception:
            self.show("can not open:" + '"' + name + '"')
            return None
    #@+node:ekr.20031218072017.3647: *4* compare.dump
    def dump(self, tag: str, s: str) -> None:
        compare = self
        out = tag
        for ch in s[:-1]:  # don't print the newline
            if compare.makeWhitespaceVisible:
                if ch == '\t':
                    out += "["
                    out += "t"
                    out += "]"
                elif ch == ' ':
                    out += "["
                    out += " "
                    out += "]"
                else:
                    out += ch
            else:
                out += ch
        self.show(out)
    #@+node:ekr.20031218072017.3648: *4* compare.dumpToEndOfFile
    def dumpToEndOfFile(self, tag: str, f: Any, s: str, line: int, printTrailing: bool) -> int:
        trailingLines = 0
        while 1:
            if not s:
                s = g.readlineForceUnixNewline(f)
            if not s:
                break
            trailingLines += 1
            if self.printTrailingMismatches and printTrailing:
                z = tag + str(line)
                tag2 = z.rjust(6) + "+:"
                self.dump(tag2, s)
            s = None
        self.show(tag + str(trailingLines) + " trailing lines")
        return trailingLines
    #@+node:ekr.20031218072017.3649: *4* compare.isLeoHeader & isSentinel
    #@+at These methods are based on AtFile.scanHeader(). They are simpler
    # because we only care about the starting sentinel comment: any line
    # starting with the starting sentinel comment is presumed to be a
    # sentinel line.
    #@@c

    def isLeoHeader(self, s: str) -> Optional[str]:
        tag = "@+leo"
        j = s.find(tag)
        if j > 0:
            i = g.skip_ws(s, 0)
            if i < j:
                return s[i:j]
        return None

    def isSentinel(self, s: str, sentinelComment: str) -> bool:
        i = g.skip_ws(s, 0)
        return g.match(s, i, sentinelComment)
    #@+node:ekr.20031218072017.1144: *4* compare.openOutputFile
    def openOutputFile(self) -> bool:  # Bug fix: return a bool.
        if self.outputFileName is None:
            return False
        theDir, name = g.os_path_split(self.outputFileName)
        if not theDir:
            self.show("empty output directory")
            return False
        if not name:
            self.show("empty output file name")
            return False
        if not g.os_path_exists(theDir):
            self.show("output directory not found: " + theDir)
            return False
        try:
            if self.appendOutput:
                self.show("appending to " + self.outputFileName)
                self.outputFile = open(self.outputFileName, "ab")  # type:ignore
            else:
                self.show("writing to " + self.outputFileName)
                self.outputFile = open(self.outputFileName, "wb")  # type:ignore
            return True
        except Exception:
            self.outputFile = None
            self.show("exception opening output file")
            g.es_exception()
            return False
    #@+node:ekr.20031218072017.3650: *4* compare.show
    def show(self, s: str) -> None:
        # g.pr(s)
        if self.outputFile:
            # self.outputFile is opened in 'wb' mode.
            self.outputFile.write(g.toEncodedString(s + '\n'))
        elif self.c:
            g.es(s)
        else:
            g.pr(s)
            g.pr('')
    #@+node:ekr.20031218072017.3651: *4* compare.showIvars
    def showIvars(self) -> None:
        self.show("fileName1:" + str(self.fileName1))
        self.show("fileName2:" + str(self.fileName2))
        self.show("outputFileName:" + str(self.outputFileName))
        self.show("limitToExtension:" + str(self.limitToExtension))
        self.show("")
        self.show("ignoreBlankLines:" + str(self.ignoreBlankLines))
        self.show("ignoreFirstLine1:" + str(self.ignoreFirstLine1))
        self.show("ignoreFirstLine2:" + str(self.ignoreFirstLine2))
        self.show("ignoreInteriorWhitespace:" + str(self.ignoreInteriorWhitespace))
        self.show("ignoreLeadingWhitespace:" + str(self.ignoreLeadingWhitespace))
        self.show("ignoreSentinelLines:" + str(self.ignoreSentinelLines))
        self.show("")
        self.show("limitCount:" + str(self.limitCount))
        self.show("printMatches:" + str(self.printMatches))
        self.show("printMismatches:" + str(self.printMismatches))
        self.show("printTrailingMismatches:" + str(self.printTrailingMismatches))
    #@-others

class LeoCompare(BaseLeoCompare):
    """
    A class containing Leo's compare code.

    These are not very useful comparisons.
    """
    pass
#@+node:ekr.20180211170333.1: ** class CompareLeoOutlines
class CompareLeoOutlines:
    """
    A class to do outline-oriented diffs of two or more .leo files.
    Similar to GitDiffController, adapted for use by scripts.
    """

    def __init__(self, c: Cmdr) -> None:
        """Ctor for the LeoOutlineCompare class."""
        self.c = c
        self.file_node: Position = None
        self.root: Position = None
        self.path1: str = None
        self.path2: str = None
    #@+others
    #@+node:ekr.20180211170333.2: *3* loc.diff_list_of_files (entry)
    def diff_list_of_files(self, aList: List[str], visible: bool = True) -> None:
        """The main entry point for scripts."""
        if len(aList) < 2:
            g.trace('Not enough files in', repr(aList))
            return
        c, u = self.c, self.c.undoer
        undoType = 'Diff Leo files'
        u.beforeChangeGroup(c.p, undoType)

        self.root = self.create_root(aList)  # creates it's own undo bead

        self.visible = visible
        while len(aList) > 1:
            path1 = aList[0]
            aList = aList[1:]
            for path2 in aList:
                undoData = u.beforeChangeTree(self.root)
                self.diff_two_files(path1, path2)  # adds to self.root
                u.afterChangeTree(self.root, undoType, undoData)

        u.afterChangeGroup(c.p, undoType=undoType)
        self.finish()
    #@+node:ekr.20180211170333.3: *3* loc.diff_two_files
    def diff_two_files(self, fn1: str, fn2: str) -> None:
        """Create an outline describing the git diffs for fn."""
        self.path1, self.path2 = fn1, fn2
        s1 = self.get_file(fn1)
        s2 = self.get_file(fn2)
        lines1 = g.splitLines(s1)
        lines2 = g.splitLines(s2)
        diff_list = list(difflib.unified_diff(lines1, lines2, fn1, fn2))
        diff_list.insert(0, '@language patch\n')
        self.file_node = self.create_file_node(diff_list, fn1, fn2)
        # These will be left open
        c1 = self.open_outline(fn1)
        c2 = self.open_outline(fn2)
        if c1 and c2:
            self.make_diff_outlines(c1, c2)
            self.file_node.b = (
                f"{self.file_node.b.rstrip()}\n"
                f"@language {c2.target_language}\n")
    #@+node:ekr.20180211170333.4: *3* loc.Utils
    #@+node:ekr.20180211170333.5: *4* loc.compute_dicts
    def compute_dicts(self, c1: Cmdr, c2: Cmdr) -> Tuple[Dict, Dict, Dict]:
        """Compute inserted, deleted, changed dictionaries."""
        d1 = {v.fileIndex: v for v in c1.all_unique_nodes()}
        d2 = {v.fileIndex: v for v in c2.all_unique_nodes()}
        added = {key: d2.get(key) for key in d2 if not d1.get(key)}
        deleted = {key: d1.get(key) for key in d1 if not d2.get(key)}
        changed = {}
        for key in d1:
            if key in d2:
                v1 = d1.get(key)
                v2 = d2.get(key)
                assert v1 and v2
                assert v1.context != v2.context
                if v1.h != v2.h or v1.b != v2.b:
                    changed[key] = (v1, v2)
        return added, deleted, changed
    #@+node:ekr.20180211170333.6: *4* loc.create_compare_node
    def create_compare_node(self, c1: Cmdr, c2: Cmdr, d: Dict[str, Tuple[VNode, VNode]], kind: str) -> None:
        """Create nodes describing the changes."""
        if not d:
            return
        parent = self.file_node.insertAsLastChild()
        parent.setHeadString(kind)
        for key in d:
            if kind.lower() == 'changed':
                v1, v2 = d.get(key)
                # Organizer node: contains diff
                organizer = parent.insertAsLastChild()
                organizer.h = v2.h
                body = list(difflib.unified_diff(
                    g.splitLines(v1.b),
                    g.splitLines(v2.b),
                    self.path1,
                    self.path2,
                ))
                if ''.join(body).strip():
                    body.insert(0, '@language patch\n')
                    body.append(f"@language {c2.target_language}\n")
                else:
                    body = ['Only headline has changed']
                organizer.b = ''.join(body)
                # Node 1:
                p1 = organizer.insertAsLastChild()
                p1.h = '1:' + v1.h
                p1.b = v1.b
                # Node 2:
                assert v1.fileIndex == v2.fileIndex
                p2 = organizer.insertAsLastChild()
                p2.h = '2:' + v2.h
                p2.b = v2.b
            else:
                v = d.get(key)
                p = parent.insertAsLastChild()
                p.h = v.h
                p.b = v.b
    #@+node:ekr.20180211170333.7: *4* loc.create_file_node
    def create_file_node(self, diff_list: List, fn1: str, fn2: str) -> Position:
        """Create an organizer node for the file."""
        p = self.root.insertAsLastChild()
        p.h = f"{g.shortFileName(fn1).strip()}, {g.shortFileName(fn2).strip()}"
        p.b = ''.join(diff_list)
        return p
    #@+node:ekr.20180211170333.8: *4* loc.create_root
    def create_root(self, aList: List[str]) -> Position:
        """Create the top-level organizer node describing all the diffs."""
        c, u = self.c, self.c.undoer
        undoType = 'Create diff root node'  # Same undoType is reused for all inner undos
        c.selectPosition(c.lastTopLevel())  # pre-select to help undo-insert
        undoData = u.beforeInsertNode(c.p)  # c.p is subject of 'insertAfter'

        p = c.lastTopLevel().insertAfter()
        p.h = 'diff-leo-files'
        p.b = '\n'.join(aList) + '\n'

        u.afterInsertNode(p, undoType, undoData)
        return p
    #@+node:ekr.20180211170333.10: *4* loc.finish
    def finish(self) -> None:
        """Finish execution of this command."""
        c = self.c
        if hasattr(g.app.gui, 'frameFactory'):
            tff = g.app.gui.frameFactory
            tff.setTabForCommander(c)
        c.selectPosition(self.root)
        self.root.expand()
        c.bodyWantsFocus()
        c.redraw()
    #@+node:ekr.20180211170333.11: *4* loc.get_file
    def get_file(self, path: str) -> str:
        """Return the contents of the file whose path is given."""
        with open(path, 'rb') as f:
            s = f.read()
        return g.toUnicode(s).replace('\r', '')
    #@+node:ekr.20180211170333.13: *4* loc.make_diff_outlines
    def make_diff_outlines(self, c1: Cmdr, c2: Cmdr) -> None:
        """Create an outline-oriented diff from the outlines c1 and c2."""
        added, deleted, changed = self.compute_dicts(c1, c2)
        table = (
            (added, 'Added'),
            (deleted, 'Deleted'),
            (changed, 'Changed'))
        for d, kind in table:
            self.create_compare_node(c1, c2, d, kind)
    #@+node:ekr.20180211170333.14: *4* loc.open_outline
    def open_outline(self, fn: str) -> Cmdr:
        """
        Find the commander for fn, creating a new outline tab if necessary.

        Using open commanders works because we always read entire .leo files.
        """
        for frame in g.app.windowList:
            if frame.c.fileName() == fn:
                return frame.c
        gui = None if self.visible else g.app.nullGui
        return g.openWithFileName(fn, gui=gui)
    #@-others
#@+node:ekr.20180214041049.1: ** Top-level commands and helpers
#@+node:ekr.20180213104556.1: *3* @g.command(diff-and-open-leo-files)
@g.command('diff-and-open-leo-files')
def diff_and_open_leo_files(event: Event) -> None:
    """
    Open a dialog prompting for two or more .leo files.

    Opens all the files and creates a top-level node in c's outline showing
    the diffs of those files, two at a time.
    """
    diff_leo_files_helper(event,
        title="Diff And Open Leo Files",
        visible=True,
    )
#@+node:ekr.20180213040339.1: *3* @g.command(diff-leo-files)
@g.command('diff-leo-files')
def diff_leo_files(event: Event) -> None:
    """
    Open a dialog prompting for two or more .leo files.

    Creates a top-level node showing the diffs of those files, two at a time.
    """
    diff_leo_files_helper(event,
        title="Diff Leo Files",
        visible=False,
    )
#@+node:ekr.20160331191740.1: *3* @g.command(diff-marked-nodes)
@g.command('diff-marked-nodes')
def diffMarkedNodes(event: Event) -> None:
    """
    When two or more nodes are marked, this command creates a
    "diff marked node" as the last top-level node. The body of
    this node contains "diff n" nodes, one for each pair of compared
    nodes.

    Each diff n contains the diffs between the two diffed nodes, that is,
    difflib.Differ().compare(p1.b, p2.b).

    The children of the diff n are clones of the two compared nodes.
    """
    c = event and event.get('c')
    if not c:
        return
    u = c.undoer
    undoType = 'Diff marked nodes'  # Same undoType is reused for all inner undos

    aList = [z for z in c.all_unique_positions() if z.isMarked()]
    n = 0
    if len(aList) >= 2:
        u.beforeChangeGroup(c.p, undoType)  # going to perform many operations

        c.selectPosition(c.lastTopLevel())  # pre-select to help undo-insert
        undoData = u.beforeInsertNode(c.p)  # c.p is subject of 'insertAfter'
        root = c.lastTopLevel().insertAfter()
        root.h = 'diff marked nodes'
        root.b = '\n'.join([z.h for z in aList]) + '\n'
        u.afterInsertNode(root, 'Create diff root node', undoData)

        while len(aList) > 1:
            n += 1
            p1, p2 = aList[0], aList[1]
            aList = aList[1:]
            lines = difflib.Differ().compare(
                g.splitLines(p1.b.rstrip() + '\n'),
                g.splitLines(p2.b.rstrip() + '\n'))

            undoData = u.beforeInsertNode(c.p)  # c.p is subject of 'insertAfter'
            p = root.insertAsLastChild()
            # p.h = 'Compare: %s, %s' % (g.truncate(p1.h, 22), g.truncate(p2.h, 22))
            p.h = f"diff {n}"
            p.b = f"1: {p1.h}\n2: {p2.h}\n{''.join(list(lines))}"
            u.afterInsertNode(p, undoType, undoData)

            undoData = u.beforeChangeTree(p)
            for p3 in (p1, p2):
                clone = p3.clone()
                clone.moveToLastChildOf(p)
            u.afterChangeTree(p, undoType, undoData)

        root.expand()
        # c.unmarkAll()
        c.selectPosition(root)
        # Add the changes to the outer undo group.
        u.afterChangeGroup(c.p, undoType=undoType)
        c.redraw()
    else:
        g.es_print('Please mark at least 2 nodes')
#@+node:ekr.20180213104627.1: *3* diff_leo_files_helper
def diff_leo_files_helper(event: Event, title: str, visible: bool) -> None:
    """Prompt for a list of Leo files to open."""
    c = event and event.get('c')
    if not c:
        return
    types = [
        ("Leo files", "*.leo *.leojs *.db"),
        ("All files", "*"),
    ]
    paths = g.app.gui.runOpenFileDialog(c,
        title=title,
        filetypes=types,
        defaultextension=".leo",
        multiple=True,
    )
    c.bringToFront()
    # paths = [z for z in paths if g.os_path_exists(z)]
    if len(paths) > 1:
        CompareLeoOutlines(c).diff_list_of_files(paths, visible=visible)
    elif len(paths) == 1:
        g.es_print('Please pick two or more .leo files')
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

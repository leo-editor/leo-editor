#@+leo-ver=5-thin
#@+node:ekr.20150624112334.1: * @file ../commands/gotoCommands.py
"""Leo's goto commands."""
#@+<< gotoCommands imports & annotations >>
#@+node:ekr.20220827065126.1: ** << gotoCommands imports & annotations >>
from __future__ import annotations
import re
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
#@-<< gotoCommands imports & annotations >>

#@+others
#@+node:ekr.20150625050355.1: ** class GoToCommands
class GoToCommands:
    """A class implementing goto-global-line."""

    def __init__(self, c: Cmdr) -> None:
        """Ctor for GoToCommands class."""
        self.c = c

    #@+others
    #@+node:ekr.20100216141722.5622: *3* goto.find_file_line
    def find_file_line(self, n: int, p: Position = None) -> tuple[Position, int]:
        """
        Place the cursor on the n'th line (one-based) of an external file.

        Return (p, offset) if found or (None, -1) if not found.
        """
        c = self.c
        if n < 0:
            return None, -1
        p = p or c.p
        root, fileName = self.find_root(p)
        if not root:
            return self.find_script_line(n, p)
        # Step 1: Get the lines of external files *with* sentinels,
        #         even if the actual external file actually contains no sentinels.
        sentinels = root.isAtFileNode()
        s = self.get_external_file_with_sentinels(root)
        # Special case empty files.
        if not s.strip():
            return p, 0
        lines = g.splitLines(s)
        # Step 2: scan the lines for line n.
        if sentinels:
            # All sentinels count as real lines.
            gnx, h, offset = self.scan_sentinel_lines(lines, n, root)
        else:
            # Not all sentinels count as real lines.
            gnx, h, offset = self.scan_nonsentinel_lines(lines, n, root)
        if gnx:
            p = self.find_gnx2(root, gnx, h)
            if p:
                self.success(n, offset, p)
                return p, offset
        self.fail(lines, n, root)
        return None, -1
    #@+node:ekr.20160921210529.1: *3* goto.find_node_start
    def find_node_start(self, p: Position, s: str = None) -> Optional[int]:
        """Return the global line number of the first line of p.b"""
        # See #283.
        root, fileName = self.find_root(p)
        if not root:
            return None
        assert root.isAnyAtFileNode()
        contents = self.get_external_file_with_sentinels(root) if s is None else s
        delim1, delim2 = self.get_delims(root)
        # Match only the node with the correct gnx.
        node_pat = re.compile(r'\s*%s@\+node:%s:' % (
            re.escape(delim1), re.escape(p.gnx)))
        for i, s in enumerate(g.splitLines(contents)):
            if node_pat.match(s):
                return i + 1
        # #3010: Special case for .vue files.
        #        Also look for nodes delimited by "//"
        if root.h.endswith('.vue'):
            node_pat2 = re.compile(r'\s*%s@\+node:%s:' % (
            re.escape('//'), re.escape(p.gnx)))
        for i, s in enumerate(g.splitLines(contents)):
            if node_pat2.match(s):
                return i + 1
        return None
    #@+node:ekr.20150622140140.1: *3* goto.find_script_line
    def find_script_line(self, n: int, root: Position) -> tuple[Position, int]:
        """
        Go to line n (zero based) of the script with the given root.
        Return (p, offset) if found or (None, -1) otherwise.
        """
        c = self.c
        if n < 0:
            return None, -1
        script = g.getScript(c, root, useSelectedText=False)
        lines = g.splitLines(script)
        # Script lines now *do* have gnx's.
        gnx, h, offset = self.scan_sentinel_lines(lines, n, root)
        if gnx:
            p = self.find_gnx2(root, gnx, h)
            if p:
                self.success(n, offset, p)
                return p, offset
        self.fail(lines, n, root)
        return None, -1
    #@+node:ekr.20181003080042.1: *3* goto.node_offset_to_file_line
    def node_offset_to_file_line(self, target_offset: int, target_p: Position, root: Position) -> int:
        """
        Given a zero-based target_offset within target_p.b, return the line
        number of the corresponding line within root's file.
        """
        delim1, delim2 = self.get_delims(root)
        file_s = self.get_external_file_with_sentinels(root)
        gnx, h, n, node_offset, target_gnx = None, None, -1, None, target_p.gnx
        stack: list[tuple[str, str, int]] = []
        for s in g.splitLines(file_s):
            n += 1  # All lines contribute to the file's line count.
            if self.is_sentinel(delim1, delim2, s):
                s2 = s.strip()[len(delim1) :]  # Works for blackened sentinels.
                # Common code for the visible sentinels.
                if s2.startswith(('@+others', '@+<<', '@@'),):
                    if target_offset == node_offset and gnx == target_gnx:
                        return n
                    if node_offset is not None:
                        node_offset += 1
                # These sentinels change nodes...
                if s2.startswith('@+node'):
                    gnx, h = self.get_script_node_info(s, delim2)
                    node_offset = 0
                elif s2.startswith('@-node'):
                    gnx = node_offset = None
                elif s2.startswith(('@+others', '@+<<'),):
                    stack.append((gnx, h, node_offset))
                    gnx, node_offset = None, None
                elif s2.startswith(('@-others', '@-<<'),):
                    gnx, h, node_offset = stack.pop()
            else:
                # All non-sentinel lines are visible.
                if target_offset == node_offset and gnx == target_gnx:
                    return n
                if node_offset is not None:
                    node_offset += 1
        g.trace('\nNot found', target_offset, target_gnx)
        return None
    #@+node:ekr.20150624085605.1: *3* goto.scan_nonsentinel_lines
    def scan_nonsentinel_lines(self, lines: list[str], n: int, root: Position) -> tuple[str, str, int]:
        """
        Scan a list of lines containing sentinels, looking for the node and
        offset within the node of the n'th (one-based) line.

        Only non-sentinel lines increment the global line count, but
        @+node sentinels reset the offset within the node.

        Return gnx, h, offset:
        gnx:    the gnx of the #@+node
        h:      the headline of the #@+node
        offset: the offset of line n within the node.
        """
        delim1, delim2 = self.get_delims(root)
        count, gnx, h, offset = 0, root.gnx, root.h, 0
        stack = [(gnx, h, offset),]
        for s in lines:
            is_sentinel = self.is_sentinel(delim1, delim2, s)
            if is_sentinel:
                s2 = s.strip()[len(delim1) :]  # Works for blackened sentinels.
                if s2.startswith('@+node'):
                    # Invisible, but resets the offset.
                    offset = 0
                    gnx, h = self.get_script_node_info(s, delim2)
                elif s2.startswith('@+others') or s2.startswith('@+<<'):
                    stack.append((gnx, h, offset),)
                    #@verbatim
                    # @others is visible in the outline, but *not* in the file.
                    offset += 1
                elif s2.startswith('@-others') or s2.startswith('@-<<'):
                    gnx, h, offset = stack.pop()
                    #@verbatim
                    # @-others is invisible.
                    offset += 1
                elif s2.startswith('@@'):
                    # Directives are visible in the outline, but *not* in the file.
                    offset += 1
                else:
                    # All other sentinels are invisible to the user.
                    offset += 1
            else:
                # Non-sentinel lines are visible both in the outline and the file.
                count += 1
                offset += 1
            if count == n:
                # Count is the real, one-based count.
                break
        else:
            gnx, h, offset = None, None, -1
        return gnx, h, offset
    #@+node:ekr.20150623175314.1: *3* goto.scan_sentinel_lines
    def scan_sentinel_lines(self, lines: list[str], n: int, root: Position) -> tuple[str, str, int]:
        """
        Scan a list of lines containing sentinels, looking for the node and
        offset within the node of the n'th (one-based) line.

        Return gnx, h, offset:
        gnx:    the gnx of the #@+node
        h:      the headline of the #@+node
        offset: the offset of line n within the node.
        """
        delim1, delim2 = self.get_delims(root)
        gnx, h, offset = root.gnx, root.h, 0
        stack = [(gnx, h, offset),]
        for i, s in enumerate(lines):
            if self.is_sentinel(delim1, delim2, s):
                s2 = s.strip()[len(delim1) :]  # Works for blackened sentinels.
                if s2.startswith('@+node'):
                    offset = 0
                    gnx, h = self.get_script_node_info(s, delim2)
                elif s2.startswith('@+others') or s2.startswith('@+<<'):
                    stack.append((gnx, h, offset),)
                    offset += 1
                elif s2.startswith('@-others') or s2.startswith('@-<<'):
                    gnx, h, offset = stack.pop()
                    offset += 1
                else:
                    offset += 1
            else:
                offset += 1
            if i + 1 == n:  # Bug fix 2017/04/01: n is one based.
                break
        else:
            gnx, h, offset = None, None, -1
        return gnx, h, offset
    #@+node:ekr.20150624142449.1: *3* goto.Utils
    #@+node:ekr.20150625133523.1: *4* goto.fail
    def fail(self, lines: Any, n: int, root: Position) -> None:
        """Select the last line of the last node of root's tree."""
        c = self.c
        w = c.frame.body.wrapper
        c.selectPosition(root)
        c.redraw()
        # Don't warn if there is no line 0.
        if not g.unitTesting and abs(n) > 0:
            if len(lines) < n:
                g.warning('only', len(lines), 'lines')
            else:
                g.warning('line', n, 'not found')
        c.frame.clearStatusLine()
        c.frame.putStatusLine(f"goto-global-line not found: {n}")
        # Put the cursor on the last line of body text.
        w.setInsertPoint(len(root.b))
        c.bodyWantsFocus()
        w.seeInsertPoint()
    #@+node:ekr.20100216141722.5626: *4* goto.find_gnx & find_gnx2
    def find_gnx(
        self,
        root: Position,
        gnx: str, vnodeName: str,
    ) -> tuple[Position, bool]:  # Retain find_gnx for compatibility.
        """
        Scan root's tree for a node with the given gnx and vnodeName.
        return (p, True) if found or (None, False) otherwise.
        """
        p = self.find_gnx2(root, gnx, vnodeName)
        return p, bool(p)

    def find_gnx2(self, root: Position, gnx: str, vnodeName: str) -> Optional[Position]:
        """
        Scan root's tree for a node with the given gnx and vnodeName.
        return a copy of the position or None.
        """
        if not gnx:
            return None  # Should never happen.
        gnx = g.toUnicode(gnx)
        for p in root.self_and_subtree(copy=False):
            if p.matchHeadline(vnodeName):
                if p.v.fileIndex == gnx:
                    return p.copy()
        return None
    #@+node:ekr.20100216141722.5627: *4* goto.find_root
    def find_root(self, p: Position) -> tuple[Position, str]:
        """
        Find the closest ancestor @<file> node, except @all nodes and @edit nodes.
        return root, fileName.
        """
        c = self.c
        p1 = p.copy()
        # Look up the tree for the first @file node.
        for p in p.self_and_parents(copy=False):
            if not p.isAtAllNode():
                fileName = p.anyAtFileNodeName()
                if fileName:
                    return p.copy(), fileName
        # Search the entire tree for cloned nodes.
        for p in c.all_positions():
            if p.v == p1.v and p != p1:
                # Found a cloned position.
                for p2 in p.self_and_parents():
                    if not p2.isAtAllNode():
                        fileName = p2.anyAtFileNodeName()
                        if fileName:
                            return p2.copy(), fileName
        return None, None
    #@+node:ekr.20150625123747.1: *4* goto.get_delims
    def get_delims(self, root: Position) -> tuple[str, str]:
        """Return the delimiters in effect at root."""
        c = self.c
        old_target_language = c.target_language
        try:
            c.target_language = g.getLanguageAtPosition(c, root)
            d = c.scanAllDirectives(root)
        finally:
            c.target_language = old_target_language
        delims1, delims2, delims3 = d.get('delims')
        if delims1:
            return delims1, None
        return delims2, delims3
    #@+node:ekr.20150624143903.1: *4* goto.get_external_file_with_sentinels
    def get_external_file_with_sentinels(self, root: Position) -> str:
        """
        root is an @<file> node. If root is an @auto node, return the result of
        writing the file *with* sentinels, even if the external file normally
        would *not* have sentinels.
        """
        c = self.c
        if root.isAtAutoNode():
            # Special case @auto nodes:
            # Leo does not write sentinels in the root @auto node.
            try:
                g.app.force_at_auto_sentinels = True
                s = c.atFileCommands.atAutoToString(root)
            finally:
                g.app.force_at_auto_sentinels = True
            return s
        return g.composeScript(  # Fix # 429.
            c=c,
            p=root,
            s=root.b,
            forcePythonSentinels=False,  # See #247.
            useSentinels=True)
    #@+node:ekr.20150623175738.1: *4* goto.get_script_node_info
    def get_script_node_info(self, s: str, delim2: Any) -> tuple[str, str]:
        """Return the gnx and headline of a #@+node."""
        i = s.find(':', 0)
        j = s.find(':', i + 1)
        if i == -1 or j == -1:
            g.error("bad @+node sentinel", s)
            return None, None
        gnx = s[i + 1 : j]
        h = s[j + 1 :]
        h = self.remove_level_stars(h).strip()
        if delim2:
            h = h.rstrip(delim2)
        return gnx, h
    #@+node:ekr.20150625124027.1: *4* goto.is_sentinel
    def is_sentinel(self, delim1: str, delim2: str, s: str) -> bool:
        """Return True if s is a sentinel line with the given delims."""
        # Leo 6.7.2: Use g.is_sentinel, which handles blackened sentinels properly.
        delims: tuple
        if delim1 and delim2:
            delims = (None, delim1, delim2)
        else:
            delims = (delim1, None, None)
        return g.is_sentinel(line=s, delims=delims)
    #@+node:ekr.20100728074713.5843: *4* goto.remove_level_stars
    def remove_level_stars(self, s: str) -> str:
        i = g.skip_ws(s, 0)
        # Remove leading stars.
        while i < len(s) and s[i] == '*':
            i += 1
        # Remove optional level number.
        while i < len(s) and s[i].isdigit():
            i += 1
        # Remove trailing stars.
        while i < len(s) and s[i] == '*':
            i += 1
        # Remove one blank.
        if i < len(s) and s[i] == ' ':
            i += 1
        return s[i:]
    #@+node:ekr.20100216141722.5638: *4* goto.success
    def success(self, n: int, n2: int, p: Position) -> None:
        """Place the cursor on line n2 of p.b."""
        c = self.c
        w = c.frame.body.wrapper
        # Select p and make it visible.
        c.selectPosition(p)
        c.redraw(p)
        # Put the cursor on line n2 of the body text.
        s = w.getAllText()
        ins = g.convertRowColToPythonIndex(s, n2 - 1, 0)
        c.frame.clearStatusLine()
        c.frame.putStatusLine(f"goto-global-line found: {n2}")
        w.setInsertPoint(ins)
        c.bodyWantsFocus()
        w.seeInsertPoint()
    #@-others
#@+node:ekr.20180517041303.1: ** show-file-line
@g.command('show-file-line')
def show_file_line(event: Event) -> None:
    """
    Prints the external file line number that corresponds to
    the line the cursor is relatively positioned in Leo's body.
    """
    c = event.get('c')
    if not c:
        return
    w = c.frame.body.wrapper
    if not w:
        return
    n0 = GoToCommands(c).find_node_start(p=c.p)
    if n0 is None:
        g.es_print('Line not found')
        return
    i = w.getInsertPoint()
    s = w.getAllText()
    row, col = g.convertPythonIndexToRowCol(s, i)
    g.es_print('line', 1 + n0 + row)
#@-others
#@-leo

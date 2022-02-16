# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150624112334.1: * @file ../commands/gotoCommands.py
#@@first
"""Leo's goto commands."""
import re
from leo.core import leoGlobals as g
#@+others
#@+node:ekr.20150625050355.1: ** class GoToCommands
class GoToCommands:
    """A class implementing goto-global-line."""
    #@+others
    #@+node:ekr.20100216141722.5621: *3* goto.ctor
    def __init__(self, c):
        """Ctor for GoToCommands class."""
        self.c = c
    #@+node:ekr.20100216141722.5622: *3* goto.find_file_line
    def find_file_line(self, n, p=None):
        """
        Place the cursor on the n'th line (one-based) of an external file.
        Return (p, offset, found) for unit testing.
        """
        c = self.c
        if n < 0:
            return None, -1, False
        p = p or c.p
        root, fileName = self.find_root(p)
        if root:
            # Step 1: Get the lines of external files *with* sentinels,
            # even if the actual external file actually contains no sentinels.
            sentinels = root.isAtFileNode()
            s = self.get_external_file_with_sentinels(root)
            lines = g.splitLines(s)
            # Step 2: scan the lines for line n.
            if sentinels:
                # All sentinels count as real lines.
                gnx, h, offset = self.scan_sentinel_lines(lines, n, root)
            else:
                # Not all sentinels cound as real lines.
                gnx, h, offset = self.scan_nonsentinel_lines(lines, n, root)
            p, found = self.find_gnx(root, gnx, h)
            if gnx and found:
                self.success(n, offset, p)
                return p, offset, True
            self.fail(lines, n, root)
            return None, -1, False
        return self.find_script_line(n, p)
    #@+node:ekr.20160921210529.1: *3* goto.find_node_start
    def find_node_start(self, p, s=None):
        """Return the global line number of the first line of p.b"""
        # See #283.
        root, fileName = self.find_root(p)
        if not root:
            return None
        assert root.isAnyAtFileNode()
        if s is None:
            s = self.get_external_file_with_sentinels(root)
        delim1, delim2 = self.get_delims(root)
        # Match only the node with the correct gnx.
        node_pat = re.compile(r'\s*%s@\+node:%s:' % (
            re.escape(delim1), re.escape(p.gnx)))
        for i, s in enumerate(g.splitLines(s)):
            if node_pat.match(s):
                return i + 1
        return None
    #@+node:ekr.20150622140140.1: *3* goto.find_script_line
    def find_script_line(self, n, root):
        """
        Go to line n (zero based) of the script with the given root.
        Return p, offset, found for unit testing.
        """
        c = self.c
        if n < 0:
            return None, -1, False
        script = g.getScript(c, root, useSelectedText=False)
        lines = g.splitLines(script)
        # Script lines now *do* have gnx's.
        gnx, h, offset = self.scan_sentinel_lines(lines, n, root)
        p, found = self.find_gnx(root, gnx, h)
        if gnx and found:
            self.success(n, offset, p)
            return p, offset, True
        self.fail(lines, n, root)
        return None, -1, False
    #@+node:ekr.20181003080042.1: *3* goto.node_offset_to_file_line
    def node_offset_to_file_line(self, target_offset, target_p, root):
        """
        Given a zero-based target_offset within target_p.b, return the line
        number of the corresponding line within root's file.
        """
        delim1, delim2 = self.get_delims(root)
        file_s = self.get_external_file_with_sentinels(root)
        gnx, h, n, node_offset, target_gnx = None, None, -1, None, target_p.gnx
        stack = []
        for s in g.splitLines(file_s):
            n += 1  # All lines contribute to the file's line count.
            # g.trace('%4s %4r %40r %s' % (n, node_offset, h, s.rstrip()))
            if self.is_sentinel(delim1, delim2, s):
                s2 = s.strip()[len(delim1) :]
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
                    stack.append([gnx, h, node_offset])
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
    def scan_nonsentinel_lines(self, lines, n, root):
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
                s2 = s.strip()[len(delim1) :]
                if s2.startswith('@+node'):
                    # Invisible, but resets the offset.
                    offset = 0
                    gnx, h = self.get_script_node_info(s, delim2)
                elif s2.startswith('@+others') or s2.startswith('@+<<'):
                    stack.append((gnx, h, offset),)
                    # @others is visible in the outline, but *not* in the file.
                    offset += 1
                elif s2.startswith('@-others') or s2.startswith('@-<<'):
                    gnx, h, offset = stack.pop()
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
    def scan_sentinel_lines(self, lines, n, root):
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
                s2 = s.strip()[len(delim1) :]
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
    def fail(self, lines, n, root):
        """Select the last line of the last node of root's tree."""
        c = self.c
        w = c.frame.body.wrapper
        c.selectPosition(root)
        c.redraw()
        if not g.unitTesting:
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
    #@+node:ekr.20100216141722.5626: *4* goto.find_gnx
    def find_gnx(self, root, gnx, vnodeName):
        """
        Scan root's tree for a node with the given gnx and vnodeName.
        return (p,found)
        """
        if gnx:
            gnx = g.toUnicode(gnx)
            for p in root.self_and_subtree(copy=False):
                if p.matchHeadline(vnodeName):
                    if p.v.fileIndex == gnx:
                        return p.copy(), True
            return None, False
        return root, False
    #@+node:ekr.20100216141722.5627: *4* goto.find_root
    def find_root(self, p):
        """
        Find the closest ancestor @<file> node, except @all nodes and @edit nodes.
        return root, fileName.
        """
        c = self.c
        p1 = p.copy()
        # First look for ancestor @file node.
        for p in p.self_and_parents(copy=False):
            if not p.isAtEditNode() and not p.isAtAllNode():
                fileName = p.anyAtFileNodeName()
                if fileName:
                    return p.copy(), fileName
        # Search the entire tree for joined nodes.
        # Bug fix: Leo 4.5.1: *must* search *all* positions.
        for p in c.all_positions():
            if p.v == p1.v and p != p1:
                # Found a joined position.
                for p2 in p.self_and_parents():
                    fileName = not p2.isAtAllNode() and p2.anyAtFileNodeName()
                    if fileName:
                        return p2.copy(), fileName
        return None, None
    #@+node:ekr.20150625123747.1: *4* goto.get_delims
    def get_delims(self, root):
        """Return the deliminters in effect at root."""
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
    def get_external_file_with_sentinels(self, root):
        """
        root is an @<file> node.

        Return the result of writing the file *with* sentinels, even if the
        external file would normally *not* have sentinels.
        """
        c = self.c
        if root.isAtAutoNode():
            # Special case @auto nodes:
            # Leo does not write sentinels in the root @auto node.
            at = c.atFileCommands
            ivar = 'force_sentinels'
            try:
                setattr(at, ivar, True)
                s = at.atAutoToString(root)
            finally:
                if hasattr(at, ivar):
                    delattr(at, ivar)
            return s
        return g.composeScript(  # Fix # 429.
            c=c,
            p=root,
            s=root.b,
            forcePythonSentinels=False,  # See #247.
            useSentinels=True)
    #@+node:ekr.20150623175738.1: *4* goto.get_script_node_info
    def get_script_node_info(self, s, delim2):
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
    def is_sentinel(self, delim1, delim2, s):
        """Return True if s is a sentinel line with the given delims."""
        assert delim1
        i = s.find(delim1 + '@')
        if delim2:
            j = s.find(delim2)
            return -1 < i < j
        return -1 < i
    #@+node:ekr.20100728074713.5843: *4* goto.remove_level_stars
    def remove_level_stars(self, s):
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
    def success(self, n, n2, p):
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
def show_file_line(event):
    c = event.get('c')
    if not c:
        return
    w = c.frame.body.wrapper
    if not w:
        return
    n0 = GoToCommands(c).find_node_start(p=c.p)
    if n0 is None:
        return
    i = w.getInsertPoint()
    s = w.getAllText()
    row, col = g.convertPythonIndexToRowCol(s, i)
    g.es_print(1 + n0 + row)
#@-others
#@-leo

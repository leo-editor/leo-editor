# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150624112334.1: * @file ../commands/gotoCommands.py
#@@first
'''Leo's goto commands.'''
import leo.core.leoGlobals as g
import os

class Found(Exception):
    '''An exception thrown when the target line is found.'''

    def __init__(self, i, p):
        self.i = i
        self.p = p

    def __str__(self):
        return "Found line at %s in %s" % (self.i, self.p.h)

class GoToCommands:
    '''A class implementing goto-global-line.'''
    #@+others
    #@+node:ekr.20100216141722.5621: ** goto.ctor
    def __init__(self, c):
        '''Ctor for GoToCommands class.'''
        # g.trace('(c.gotoLineNumber)')
        self.c = c
        self.n = 0
            # The number of effective lines seen so far.
        self.p = c.p.copy()
        self.isAtAuto = False
        self.target = 0
            # The target line number.
        self.trace = False
            # set in countLines.
    #@+node:ekr.20100216141722.5622: ** goto.go
    def go(self, n, p=None):
        '''Place the cursor on the n'th line of a derived file'''
        c = self.c
        if n < 0: return
        ###
        # if scriptData:
            # fileName, lines, p, root = self.setup_script(scriptData)
        # else:
            # if not p: p = c.p
            # fileName, lines, n, root = self.setup_file(n, p)
        if not p: p = c.p
        fileName, isScript, lines, n, root = self.setup_file(n, p)
        self.isAtAuto = root and root.isAtAutoNode()
        isRaw = not root or (
            root.isAtEditNode() or root.isAtAsisFileNode() or
            root.isAtAutoNode() or root.isAtNoSentFileNode() or
            root.isAtCleanNode())
        ### ignoreSentinels = root and root.isAtNoSentFileNode()
        if not root:
            ### if scriptData: root = p.copy()
            ### else: root = c.p
            root = c.p
        if isRaw and not isScript:
            p, n2, found = self.countLines(root, n)
            n2 += 1 # Convert to one-based.
        else:
            vnodeName, gnx, n2, delim = self.findVnode(root, lines, n)
            p, found = self.findGnx(delim, root, gnx, vnodeName)
        self.showResults(found, p or root, n, n2, lines)
        return found
    #@+node:ekr.20150622140140.1: ** goto.go_script_line & helpers
    def go_script_line(self, n, root):
        '''Go to line n (zero based) of the script with the given root.'''
        trace = False and not g.unitTesting
        c = self.c
        if n < 0:
            return False
        else:
            script = g.getScript(c, root, useSelectedText=False)
            lines = g.splitLines(script)
            if trace:
                aList = ['%3s %s' % (i, s) for i, s in enumerate(lines)]
                g.trace('n: %s script: ...\n%s' % (n, ''.join(aList)))
            # Script lines now *do* have gnx's.
            delim = '#@'
            n = max(0, n - 1) # Convert to zero based.
            gnx, h, n2 = self.scan_script_lines(delim, lines, n, root)
            p, found = self.findGnx(delim, root, gnx, h)
            self.showResults(found, p or root, n, n2, lines)
            return found
    #@+node:ekr.20150622145749.1: *3* goto.adjust_script_n
    def adjust_script_n(self, lines, n):
        '''
        n is a line number for a script *with* sentinels.
        
        Return the corresonding line number *not counting* sentinels.
        '''
        trace = True and not g.unitTesting
        real = 0 # The number of real lines (in the outline)
        for i, s in enumerate(lines):
            s = s.strip()
            if s.startswith('#@'):
                for tag in ('#@verbatim', '#@+others', '#@+<<'):
                    # These *do* correspond to source lines.
                    if s.startswith(tag):
                        if trace: g.trace(s)
                        real += 1
                        break
                # else: g.trace('skip', s.rstrip())
            else:
                if trace: g.trace(s)
                real += 1
            if i >= n:
                break
        if trace: g.trace('n', n, 'i', i, 'real', real)
        return real
    #@+node:ekr.20150623175738.1: *3* goto.get_script_node_info
    def get_script_node_info(self, s):
        '''Return the gnx and headline of a #@+node.'''
        i = s.find(':', 0)
        j = s.find(':', i + 1)
        if i == -1 or j == -1:
            g.error("bad @+node sentinel", s)
            return None, None
        else:
            gnx = s[i + 1: j]
            h = s[j + 1:]
            h = self.removeLevelStars(h).strip()
            # g.trace(gnx, h, s.rstrip())
            return gnx, h
    #@+node:ekr.20150623175314.1: *3* goto.scan_script_lines
    def scan_script_lines(self, delim, lines, n, root):
        '''
        Scan a list of lines containing sentinels, looking for the node and
        offset within the node of the n'th (zero-based) line.
        
        Return gnx, h, offset:
        gnx:    the gnx of the #@+node
        h:      the headline of the #@+node
        offset: the offset of line n within the node.
        '''
        trace = False and not g.unitTesting
        gnx, h, offset = root.gnx, root.h, 0
        stack = [(gnx, h, offset),]
        for i, s in enumerate(lines):
            if trace: g.trace(s.rstrip())
            if s.startswith(delim + '+node'):
                offset = 0
                gnx, h = self.get_script_node_info(s)
                if trace: g.trace('node', gnx, h)
            elif s.startswith(delim + '+others') or s.startswith(delim + '+<<'):
                stack.append((gnx, h, offset),)
                offset += 1
            elif s.startswith(delim + '-others') or s.startswith(delim + '-<<'):
                gnx, h, offset = stack.pop()
                offset += 1
            else:
                offset += 1
            if trace: g.trace(i, offset, h, '\n')
            if i == n:
                break
        if trace: g.trace('gnx', gnx, 'h', h, 'offset', offset)
        return gnx, h, offset
    #@+node:ekr.20150624085605.1: *3* goto.scan_nonsentinel_lines
    def scan_nonsentinel_lines(self, delim, lines, n, root):
        '''
        Scan a list of lines containing sentinels, looking for the node and
        offset within the node of the n'th (zero-based) line.  Only lines
        that appear in the outline increment count.
        
        Return gnx, h, offset:
        gnx:    the gnx of the #@+node
        h:      the headline of the #@+node
        offset: the offset of line n within the node.
        '''
        trace = True and not g.unitTesting
        count, gnx, h, offset = 0, root.gnx, root.h, 0
        stack = [(gnx, h, offset),]
        for s in lines:
            if trace: g.trace(s.rstrip())
            if s.startswith(delim + '+node'):
                offset = 0
                    # The node delim does not appear in the outline.
                gnx, h = self.get_script_node_info(s)
                if trace: g.trace('node', gnx, h)
            elif s.startswith(delim + '+others') or s.startswith(delim + '+<<'):
                stack.append((gnx, h, offset),)
                count += 1
                offset += 1
                    # The directive or section reference *does* appear in the outine.
            elif s.startswith(delim + '-others') or s.startswith(delim + '-<<'):
                gnx, h, offset = stack.pop()
                # These do *not* appear in the outline.
            elif s.startswith(delim + 'verbatim'):
                pass # Only the following line appears in the outline.
            else:
                # All other lines, including Leo directives, do appear in the outline.
                count += 1
                offset += 1
            if trace: g.trace(count, offset, h, '\n')
            if count == n:
                break
        if trace: g.trace('gnx', gnx, 'h', h, 'offset', offset)
        return gnx, h, offset
    #@+node:ekr.20100216141722.5623: ** goto.countLines & helpers
    def countLines(self, root, n):
        '''
        Scan through root's outline, looking for line n (one based).
        Return (p,i,found)
            p: the found node.
            i: the zero-based offset of the line within the node.
            found: True if the line n was found.
        '''
        self.trace = True and not g.unitTesting
        self.target = max(0, n - 1)
            # Invariant: the target never changes!
        self.n = 0
            # The number of "effective" lines seen in the outline.
        if self.trace: g.trace('n (zero-based):', n, root.h)
        try:
            self.countBodyLines(root)
            p, i, found = None, -1, False
        except Found as e:
            p, i, found = e.p, e.i, True
        return p, i, found
    #@+node:ekr.20100216141722.5624: *3* goto.countBodyLines
    def countBodyLines(self, p):
        '''
        Scan p.b, incrementing self.n, looking for self.target.
        
        raise Found(i,p) if the target line is found.
        '''
        if not p: return
        if self.trace: g.trace('=' * 10, self.n, p.h)
        ao = False # True: @others has been seen in this node.
        for i, line in enumerate(g.splitLines(p.b)):
            if self.trace: g.trace('i %3s n %3s %s' % (i, self.n, line.rstrip()))
            ref = self.findDefinition(line, p)
            if line.strip().startswith('@'):
                ao = self.countDirectiveLines(ao, i, line, p)
            elif ref:
                self.countBodyLines(ref)
            elif self.n == self.target:
                if self.trace: g.trace('Found! n: %s i: %s in: %s' % (self.n, i, p.h))
                raise Found(i, p)
            else:
                self.n += 1
        if not ao:
            self.countChildLines(p)
    #@+node:ekr.20100216141722.5625: *3* goto.countChildLines
    def countChildLines(self, p):
        '''
        Scan p's children, incrementing self.n, looking for self.target.
        Skip section defintion nodes.
        
        raise Found(i,p) if the target line is found.
        '''
        if self.trace:
            g.trace('-' * 10, self.n, p.h)
        for child in p.children():
            if self.trace: g.trace('child: %s' % child.h)
            if self.sectionName(child.h):
                pass # Assume the node will be expanded via a section reference.
            else:
                self.countBodyLines(child)
    #@+node:ekr.20150306083738.11: *3* goto.countDirectiveLines
    def countDirectiveLines(self, ao, i, line, p):
        '''Handle a possible Leo directive, including @others.'''
        if line.strip().startswith('@others'):
            if not ao and p.hasChildren():
                ao = True # We have seen @others in p.
                self.countChildLines(p)
            else:
                pass # silently ignore erroneous @others.
        else:
            s = line.strip()
            k = g.skip_id(s, 1)
            word = s[1: k]
            # Fix bug 138: Treat a bare '@' as a Leo directive.
            if not word or word in g.globalDirectiveList:
                pass # A regular directive: don't change effective_n.
            else:
                # Fix bug 1182864: goto-global-line cmd bug.
                # Count everything (like decorators) that is not a Leo directive.
                if self.n == self.target:
                    if self.trace:
                        g.trace('Found in @others! n: %s i: %s %s\n%s' % (
                            self.n, i, line, p.h))
                    raise Found(i, p)
                else:
                    self.n += 1
        return ao
    #@+node:ekr.20150306124034.6: *3* goto.findDefinition
    def findDefinition(self, line, p):
        '''
        Return the section definition node corresponding to the section
        reference in the given line of p.b.
        '''
        name = self.sectionName(line)
        ref = name and g.findReference(self.c, name, p)
        if name and not ref:
            g.error('section reference not found: %s' % (g.angleBrackets(name)))
        return ref
    #@+node:ekr.20150306124034.7: *3* goto.sectionName
    def sectionName(self, line):
        '''Return the first section reference in line.'''
        i = line.find('<<')
        j = line.find('>>')
        return line[i: j + 2] if -1 < i < j else None
    #@+node:ekr.20100216141722.5626: ** goto.findGnx
    def findGnx(self, delim, root, gnx, vnodeName):
        '''
        Scan root's tree for a node with the given gnx and vnodeName.
        return (p,found)
        '''
        trace = False and not g.unitTesting
        if delim and gnx:
            assert g.isString(gnx)
            gnx = g.toUnicode(gnx)
            for p in root.self_and_subtree():
                if p.matchHeadline(vnodeName):
                    if p.v.fileIndex == gnx:
                        return p.copy(), True
            if trace: g.trace('not found! %s, %s' % (gnx, repr(vnodeName)))
            return None, False
        else:
            return root, False
    #@+node:ekr.20100216141722.5627: ** goto.findRoot
    def findRoot(self, p):
        '''Find the closest ancestor @<file> node, except @all nodes.

        return root, fileName.'''
        c = self.c; p1 = p.copy()
        # First look for ancestor @file node.
        for p in p.self_and_parents():
            fileName = not p.isAtAllNode() and p.anyAtFileNodeName()
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
    #@+node:ekr.20100216141722.5628: ** goto.findVnode & helpers
    def findVnode(self, root, lines, n):
        '''Search the lines of a derived file containing sentinels for a VNode.
        return (vnodeName,gnx,offset,delim):

        vnodeName:  the name found in the previous @+body sentinel.
        gnx:        the gnx of the found node.
        offset:     the offset within the node of the desired line.
        delim:      the comment delim from the @+leo sentinel.
        '''
        trace = True and not g.unitTesting
        trace_lines = False
        # c = self.c
        if trace and trace_lines: g.trace('lines...\n', g.listToString(lines))
        gnx = None
        delim, readVersion5, thinFile = self.setDelimFromLines(lines)
        if not delim:
            g.es('no sentinels in:', root.h)
            return None, None, None, None
        nodeLine, offset = self.findNodeSentinel(delim, lines, n)
        if nodeLine == -1:
            if n < len(lines):
                # The line precedes the first @+node sentinel
                g.trace('no @+node!!')
            return root.h, gnx, 1, delim
        s = lines[nodeLine]
        gnx, vnodeName = self.getNodeLineInfo(readVersion5, s, thinFile)
        if delim and vnodeName:
            if trace: g.trace('offset: %s, vnodeName: %s' % (offset, vnodeName))
            return vnodeName, gnx, offset, delim
        else:
            g.es("bad @+node sentinel")
            return None, None, None, None
    #@+node:ekr.20100216141722.5629: *3* goto.findNodeSentinel & helper
    def findNodeSentinel(self, delim, lines, n):
        '''
        Scan backwards from the line n, looking for an @-body line. When found,
        get the VNode's name from that line and set p to the indicated VNode. This
        will fail if VNode names have been changed, and that can't be helped.

        We compute the offset of the requested line **within the found node**.
        '''
        # c = self.c
        offset = 0 # This is essentially the Tk line number.
        nodeSentinelLine = -1
        line = n - 1 # Start with the requested line.
        while len(lines) > line >= 0 and nodeSentinelLine == -1:
            progress = line
            s = lines[line]
            i = g.skip_ws(s, 0)
            if g.match(s, i, delim):
                line, nodeSentinelLine, offset = self.handleDelim(
                    delim, s, i, line, lines, n, offset)
            else:
                line -= 1
            assert nodeSentinelLine > -1 or line < progress
        return nodeSentinelLine, offset
    #@+node:ekr.20100216141722.5630: *4* goto.handleDelim
    def handleDelim(self, delim, s, i, line, lines, n, offset):
        '''Handle the delim while scanning backward.'''
        trace = False and not g.unitTesting
        # c = self.c
        if line == n:
            g.es("line", str(n), "is a sentinel line")
        i += len(delim)
        nodeSentinelLine = -1
        # This code works for both old and new sentinels.
        if g.match(s, i, "-node"):
            # The end of a nested section.
            old_line = line
            line = self.skipToMatchingNodeSentinel(lines, line, delim)
            assert line < old_line
            if trace: g.trace('found', repr(lines[line]))
            nodeSentinelLine = line
            offset = n - line
        elif g.match(s, i, "+node"):
            if trace: g.trace('found', repr(lines[line]))
            nodeSentinelLine = line
            offset = n - line
        elif g.match(s, i, "<<") or g.match(s, i, "@first"):
            line -= 1
        else:
            line -= 1
            nodeSentinelLine = -1
        return line, nodeSentinelLine, offset
    #@+node:ekr.20100216141722.5631: *3* goto.getNodeLineInfo & helper
    def getNodeLineInfo(self, readVersion5, s, thinFile):
        i = 0; gnx = None; vnodeName = None
        if thinFile:
            # gnx is lies between the first and second ':':
            i = s.find(':', i)
            if i > 0:
                i += 1
                j = s.find(':', i)
                if j > 0: gnx = s[i: j]
                else: i = len(s) # Force an error.
            else:
                i = len(s) # Force an error.
        # old sentinels: VNode name is everything following the first or second':'
        i = s.find(':', i)
        if i > -1:
            vnodeName = s[i + 1:].strip()
            if readVersion5: # new sentinels: remove level stars.
                vnodeName = self.removeLevelStars(vnodeName)
        else:
            vnodeName = None
            g.error("bad @+node sentinel")
        return gnx, vnodeName
    #@+node:ekr.20100728074713.5843: *4* goto.removeLevelStars
    def removeLevelStars(self, s):
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
    #@+node:ekr.20100216141722.5632: *3* goto.setDelimFromLines
    def setDelimFromLines(self, lines):
        c = self.c; at = c.atFileCommands
        # Find the @+leo line.
        i = 0
        while i < len(lines) and lines[i].find("@+leo") == -1:
            i += 1
        leoLine = i # Index of the line containing the leo sentinel
        # Set delim and thinFile from the @+leo line.
        delim, thinFile = None, False
        if leoLine < len(lines):
            s = lines[leoLine]
            valid, newDerivedFile, start, end, thinFile = at.parseLeoSentinel(s)
            readVersion5 = at.readVersion5
            # New in Leo 4.5.1: only support 4.x files.
            if valid and newDerivedFile:
                delim = start + '@'
        else:
            readVersion5 = False
        return delim, readVersion5, thinFile
    #@+node:ekr.20100216141722.5633: *3* goto.skipToMatchingNodeSentinel (no longer used)
    def skipToMatchingNodeSentinel(self, lines, n, delim):
        s = lines[n]
        i = g.skip_ws(s, 0)
        assert(g.match(s, i, delim))
        i += len(delim)
        if g.match(s, i, "+node"):
            start = "+node"; end = "-node"; delta = 1
        else:
            assert(g.match(s, i, "-node"))
            start = "-node"; end = "+node"; delta = -1
        # Scan to matching @+-node delim.
        n += delta; level = 0
        while 0 <= n < len(lines):
            s = lines[n]; i = g.skip_ws(s, 0)
            if g.match(s, i, delim):
                i += len(delim)
                if g.match(s, i, start):
                    level += 1
                elif g.match(s, i, end):
                    if level == 0: break
                    else: level -= 1
            n += delta
        # g.trace(n)
        return n
    #@+node:ekr.20100216141722.5634: ** goto.getFileLines
    def getFileLines(self, root, fileName):
        '''Read the file into lines.'''
        c = self.c
        isAtEdit = root.isAtEditNode()
        isAtNoSent = root.isAtNoSentFileNode()
        if isAtNoSent or isAtEdit:
            # Write a virtual file containing sentinels.
            at = c.atFileCommands
            kind = '@nosent' if isAtNoSent else '@edit'
            at.write(root, kind=kind, nosentinels=False, toString=True)
            lines = g.splitLines(at.stringOutput)
        else:
            # Calculate the full path.
            path = g.scanAllAtPathDirectives(c, root)
            # g.trace('path',path,'fileName',fileName)
            fileName = c.os_path_finalize_join(path, fileName)
            lines = self.openFile(fileName)
        return lines
    #@+node:ekr.20100216141722.5635: ** goto.openFile
    def openFile(self, filename):
        """
        Open a file and check if a shadow file exists.
        Construct a line mapping. This ivar is empty if no shadow file exists.
        Otherwise it contains a mapping, shadow file number -> real file number.
        """
        c = self.c; x = c.shadowController
        try:
            shadow_filename = x.shadowPathName(filename)
            if os.path.exists(shadow_filename):
                fn = shadow_filename
                lines = open(shadow_filename).readlines()
                x.line_mapping = x.push_filter_mapping(
                    lines,
                    x.markerFromFileLines(lines, shadow_filename))
            else:
                # Just open the original file.  This is not an error!
                fn = filename
                c.line_mapping = []
                lines = open(filename).readlines()
        except Exception:
            # Make sure failures to open a file generate clear messages.
            g.error('can not open', fn)
            # g.es_exception()
            lines = []
        return lines
    #@+node:ekr.20100216141722.5636: ** goto.setup_file
    def setup_file(self, n, p):
        '''Return (fileName, isScript, lines, n, root) where:

        lines are the lines to be scanned.
        n is the effective line number (munged for @shadow nodes).
        '''
        c = self.c; x = c.shadowController
        root, fileName = self.findRoot(p)
        if root and fileName:
            c.shadowController.line_mapping = [] # Set by open.
            lines = self.getFileLines(root, fileName)
                # This will set x.line_mapping for @shadow files.
            if len(x.line_mapping) > n:
                n = x.line_mapping[n]
        else:
            if not g.unitTesting:
                g.warning("no ancestor @<file node>: using script line numbers")
            lines = g.getScript(c, p, useSelectedText=False)
            lines = g.splitLines(lines)
        isScript = root and fileName
        return fileName, isScript, lines, n, root
    #@+node:ekr.20100216141722.5637: ** goto.setup_script (to be deleted)
    def setup_script(self, scriptData):
        # c = self.c
        p = scriptData.get('p')
        root, fileName = self.findRoot(p)
        lines = scriptData.get('lines')
        return fileName, lines, p, root
    #@+node:ekr.20100216141722.5638: ** goto.showResults
    def showResults(self, found, p, n, n2, lines):
        '''Place the cursor on line n2 of p.b.'''
        trace = False and not g.unitTesting
        c = self.c
        w = c.frame.body.wrapper
        # Select p and make it visible.
        if found:
            if c.p.isOutsideAnyAtFileTree():
                p = c.findNodeOutsideAnyAtFileTree(p)
        else:
            p = c.p
        c.redraw(p)
        # Put the cursor on line n2 of the body text.
        s = w.getAllText()
        if found:
            ins = g.convertRowColToPythonIndex(s, n2 - 1, 0)
        else:
            ins = len(s)
            if not g.unitTesting:
                if len(lines) < n:
                    g.warning('only', len(lines), 'lines')
                else:
                    g.warning('line', n, 'not found')
        if trace:
            i, j = g.getLine(s, ins)
            g.trace('found: %5s %2s %2s %15s %s' % (
                found, n, n2, p.h, repr(s[i: j])))
        w.setInsertPoint(ins)
        c.bodyWantsFocus()
        w.seeInsertPoint()
    #@-others
#@-leo

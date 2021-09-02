# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210902092024.1: * @file ../unittests/core/test_leoShadow.py
#@@first
"""Tests of leoShapdw.py"""
### import os
### import tempfile
### import textwrap
from leo.core import leoGlobals as g
### from leo.core import leoBridge
from leo.core.leoShadow import ShadowController
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20080709062932.2: ** class TestShadow (LeoUnitTest)
class TestShadow(LeoUnitTest):
    """
    Support @shadow-test nodes.

    These nodes should have two descendant nodes: 'before' and 'after'.
    """
    #@+others
    #@+node:ekr.20080709062932.6: *3* TestShadow.__init__
    def __init__(self, c, p, delims=None): ###, shadowController, trace=False):
        """Ctor for AtShadowTestCase class."""
        super().__init__()
        self.c = c
        self.p = p.copy()
        ### self.shadowController = x = shadowController
        ### self.trace = trace
        # Hard value for now.
        if delims is None:
            delims = '#', '', ''
        self.shadow_controller = ShadowController(c)
        self.marker = self.shadow_controller.Marker(delims)
            ### self.marker = shadowController.marker = shadowController.Marker(delims)
                # 2015/04/03: tricky: set *both* ivars.
                # This bug became apparent because unitTest.leo no longer
                # pre-loads any @shadow files.
        # For teardown...
        self.ok = True
    #@+node:ekr.20080709062932.8: *3* TestShadow.setUp & helpers
    def setUp(self):
        """AtShadowTestCase.setup."""
        c, p = self.c, self.p
        old = self.findNode(c, p, 'old')
        new = self.findNode(c, p, 'new')
        self.old_private_lines = self.makePrivateLines(old)
        self.new_private_lines = self.makePrivateLines(new)
        self.old_public_lines = self.makePublicLines(self.old_private_lines)
        self.new_public_lines = self.makePublicLines(self.new_private_lines)
        # Change node:new to node:old in all sentinel lines.
        self.expected_private_lines = self.mungePrivateLines(
            self.new_private_lines, 'node:new', 'node:old')
    #@+node:ekr.20080709062932.19: *4* findNode (AtShadowTestCase)
    def findNode(self, c, p, headline):
        """Return the node in p's subtree with given headline."""
        p = g.findNodeInTree(c, p, headline)
        if not p:
            g.es_print('can not find', headline)
            assert False
        return p
    #@+node:ekr.20080709062932.20: *4* createSentinelNode (AtShadowTestCase)
    def createSentinelNode(self, root, p):
        """Write p's tree to a string, as if to a file."""
        h = p.h
        p2 = root.insertAsLastChild()
        p2.setHeadString(h + '-sentinels')
        return p2
    #@+node:ekr.20080709062932.21: *4* makePrivateLines (AtShadowTestCase)
    def makePrivateLines(self, p):
        """Return a list of the lines of p containing sentinels."""
        at = self.c.atFileCommands
        # A hack: we want to suppress gnx's *only* in @+node sentinels,
        # but we *do* want sentinels elsewhere.
        at.at_shadow_test_hack = True
        try:
            s = at.atFileToString(p, sentinels=True)
        finally:
            at.at_shadow_test_hack = False
        return g.splitLines(s)
    #@+node:ekr.20080709062932.22: *4* makePublicLines (AtShadowTestCase)
    def makePublicLines(self, lines):
        """Return the public lines in lines."""
        ### x = self.shadowController
        lines, junk = self.shadow_controller.separate_sentinels(lines, self.marker)
        return lines
    #@+node:ekr.20080709062932.23: *4* mungePrivateLines (AtShadowTestCase)
    def mungePrivateLines(self, lines, find, replace):
        """Change the 'find' the 'replace' pattern in sentinel lines."""
        ### x = self.shadowController
        marker = self.marker
        i, results = 0, []
        while i < len(lines):
            line = lines[i]
            if marker.isSentinel(line):
                new_line = line.replace(find, replace)
                results.append(new_line)
                if marker.isVerbatimSentinel(line):
                    i += 1
                    if i < len(lines):
                        line = lines[i]
                        results.append(line)
                    else:
                        self.shadow_controller.verbatim_error()
            else:
                results.append(line)
            i += 1
        return results
    #@+node:ekr.20080709062932.10: *3* TestShadow.runTest
    def runTest(self, define_g=True):
        """AtShadowTestCase.runTest."""
        x = self.shadow_controller
        ### x.trace = self.trace
        p = self.p.copy()
        results = x.propagate_changed_lines(
            self.new_public_lines, self.old_private_lines, self.marker, p=p)
        if results != self.expected_private_lines:
            g.pr(p.h)
            for aList, tag in (
                (results, 'results'),
                (self.expected_private_lines, 'expected_private_lines')
            ):
                g.pr(f"{tag}...")
                for i, line in enumerate(aList):
                    g.pr(f"{i:3} {line!r}")
                g.pr('-' * 40)
            assert results == self.expected_private_lines
        assert self.ok
        return self.ok
    #@-others
#@-others
#@-leo

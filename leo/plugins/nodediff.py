#@+leo-ver=5-thin
#@+node:peckj.20140113150237.7083: * @file ../plugins/nodediff.py
#@+<< docstring >>
#@+node:peckj.20140113131037.5792: ** << docstring >>
"""Provides commands to run text diffs on node bodies within Leo.

By Jacob M. Peck

Configuration Settings
======================

This plugin is configured with the following @settings:

@string node-diff-style
-----------------------
One of 'compare', 'ndiff', or 'unified_diff'.  Chooses which diff output method
difflib uses to provide the diff.  Defaults to 'compare'.

The various diff output methods are explained in the difflib documentation.

Commands
========

This plugin defines the following commands:

diff-marked
-----------
Runs a diff on the marked nodes.  Only works if there are exactly two nodes
marked in the current outline.

diff-selected
-------------
Runs a diff on the selected nodes.  Only works if there are exactly two selected
nodes in the current outline.

diff-subtree
------------
Runs a diff on the children of the currently selected node.  Only works if the
selected node has exactly two children.

diff-saved
----------
Runs a diff on the current node and the same node in the .leo file on disk,
i.e. changes in the node since last save.  **This does not work** for
derived @<files> (@auto, @edit, etc.), only nodes which are part of the
Leo outline itself.

diff-vcs
----------
Runs a diff on the current node and the same node in the most recent commit of
the .leo file to a VCS like git or bzr (currently only git and bzr supported),
i.e. changes in the node since last commit.  **This does not work** for
derived @<files> (@auto, @edit, etc.), only nodes which are part of the
Leo outline itself.

Common Usage
============
For those who don't use marked nodes for much else, the 'diff-marked' option
is probably the best.  Mark two nodes and then execute 'diff-marked'.

The 'diff-subtree' option is the second most common option, and makes a lot
of sense for those who use clones regularly.  Create an organizer node and
clone your two nodes to be diffed under that organizer node, then select
the organizer node and execute 'diff-subtree'.

The 'diff-selected' option is for those who use the mouse.  Using Ctrl+click
or Shift+click, select exactly two nodes in the outline pane, and then execute
'diff-selected'.

Scripting
=========
nodediff.py can be used by scripts to run any of the three styles of diff.
The following are available to scripts, and all of them take a list of two
positions as input::

    c.theNodeDiffController.run_compare()
    c.theNodeDiffController.run_ndiff()
    c.theNodeDiffController.run_unified_diff()

"""
#@-<< docstring >>

# By JMP.

#@+<< imports >>
#@+node:peckj.20140113131037.5794: ** << imports >>
import difflib
from io import StringIO
import subprocess

from leo.core import leoGlobals as g
from leo.external import leosax
#@-<< imports >>

#@+others
#@+node:peckj.20140113131037.5795: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.app.gui is None:
        g.app.createQtGui(__file__)
    ok = g.app.gui.guiName().startswith('qt')
    if ok:
        g.registerHandler(('new', 'open2'), onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('Error loading plugin nodediff.py', color='red')
    return ok
#@+node:peckj.20140113131037.5796: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return

    theNodeDiffController = NodeDiffController(c)
    c.theNodeDiffController = theNodeDiffController
#@+node:peckj.20140113131037.5797: ** class NodeDiffController
class NodeDiffController:

    #@+others
    #@+node:peckj.20140113131037.5798: *3* __init__ & reloadSettings (NodeDiffController, nodediff.py)
    def __init__(self, c):
        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.
        self.tab_name = 'NodeDiff'
        self.valid_styles = {
            'compare': self.run_compare,
            'ndiff': self.run_ndiff,
            'unified_diff': self.run_unified_diff,
        }
        # Settings
        self.reloadSettings()
        # register commands
        c.k.registerCommand('diff-marked', self.run_diff_on_marked)
        c.k.registerCommand('diff-selected', self.run_diff_on_selected)
        c.k.registerCommand('diff-subtree', self.run_diff_on_subtree)
        c.k.registerCommand('diff-saved', self.run_diff_on_saved)
        c.k.registerCommand('diff-vcs', self.run_diff_on_vcs)

    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.diff_style = c.config.getString('node-diff-style') or 'compare'
        if self.diff_style not in self.valid_styles.keys():
            self.diff_style = 'compare'
    #@+node:peckj.20140113131037.5802: *3* getters
    #@+node:peckj.20140113131037.5799: *4* get_selection
    def get_selection(self):
        s = self.c.getSelectedPositions()
        return s if len(s) == 2 else None
    #@+node:peckj.20140113131037.5800: *4* get_marked
    def get_marked(self):
        m = [n.copy() for n in self.c.all_positions() if n.isMarked()]
        return m if len(m) == 2 else None
    #@+node:peckj.20140113131037.5801: *4* get_subtree
    def get_subtree(self):
        st = [p.copy() for p in self.c.p.children()]
        return st if len(st) == 2 else None
    #@+node:peckj.20140113131037.5803: *3* differs
    #@+node:peckj.20140113131037.5804: *4* run_compare
    def run_compare(self, l):
        g.app.log.deleteTab(self.tab_name)
        n1 = l[0]
        n2 = l[1]
        d = difflib.Differ()
        diff = d.compare(n1.b.splitlines(), n2.b.splitlines())
        g.es('Node 1: %s' % n1.h, color='blue', tabName=self.tab_name)
        g.es('Node 2: %s' % n2.h, color='blue', tabName=self.tab_name)
        for l in diff:
            color = None
            if l.startswith('+'):
                color = 'forestgreen'
            if l.startswith('-'):
                color = 'red'
            if l.startswith('?'):
                color = 'grey'
            if color is not None:
                g.es(l, color=color, tabName=self.tab_name)
            else:
                g.es(l, tabName=self.tab_name)
    #@+node:peckj.20140113131037.5805: *4* run_ndiff
    def run_ndiff(self, l):
        g.app.log.deleteTab(self.tab_name)
        n1 = l[0]
        n2 = l[1]
        diff = difflib.ndiff(n1.b.splitlines(), n2.b.splitlines())
        g.es('Node 1: %s' % n1.h, color='blue', tabName=self.tab_name)
        g.es('Node 2: %s' % n2.h, color='blue', tabName=self.tab_name)
        for l in diff:
            color = None
            if l.startswith('+'):
                color = 'forestgreen'
            if l.startswith('-'):
                color = 'red'
            if l.startswith('?'):
                color = 'grey'
            if color is not None:
                g.es(l, color=color, tabName=self.tab_name)
            else:
                g.es(l, tabName=self.tab_name)
    #@+node:peckj.20140113131037.5806: *4* run_unified_diff
    def run_unified_diff(self, l):
        g.app.log.deleteTab(self.tab_name)
        n1 = l[0]
        n2 = l[1]
        diff = difflib.unified_diff(n1.b.splitlines(), n2.b.splitlines())
        g.es('Node 1: %s' % n1.h, color='blue', tabName=self.tab_name)
        g.es('Node 2: %s' % n2.h, color='blue', tabName=self.tab_name)
        for l in diff:
            color = None
            if l.startswith('+'):
                color = 'forestgreen'
            if l.startswith('-'):
                color = 'red'
            if color is not None:
                g.es(l, color=color, tabName=self.tab_name)
            else:
                g.es(l, tabName=self.tab_name)
    #@+node:peckj.20140113131037.5810: *4* run_appropriate_diff
    def run_appropriate_diff(self, ns):
        self.valid_styles[self.diff_style](ns)
    #@+node:peckj.20140113135910.5814: *3* commands
    #@+node:peckj.20140113131037.5807: *4* run_diff_on_marked
    # for command 'diff-marked'
    def run_diff_on_marked(self, event=None):
        """Runs a diff on the marked nodes.  Will only work if exactly 2 marked nodes exist in the outline."""
        ns = self.get_marked()
        if ns is None:
            g.es('nodediff.py: Make sure that exactly two nodes are marked.', color='red')
            return
        self.run_appropriate_diff(ns)
    #@+node:peckj.20140113131037.5808: *4* run_diff_on_selected
    # for command 'diff-selected'
    def run_diff_on_selected(self, event=None):
        """Runs a diff on the selected nodes.  Will only work if exactly two nodes are selected."""
        ns = self.get_selection()
        if ns is None:
            g.es('nodediff.py: Make sure that exactly two nodes are selected.', color='red')
            return
        self.run_appropriate_diff(ns)
    #@+node:peckj.20140113131037.5809: *4* run_diff_on_subtree
    # for command 'diff-subtree'
    def run_diff_on_subtree(self, event=None):
        """
        Runs a diff on the children of the currently selected node.
        Will only work if the node has exactly two children.
        """
        ns = self.get_subtree()
        if ns is None:
            g.es('nodediff.py: Make sure that the selected node has exactly two children.',
                color='red')
            return
        self.run_appropriate_diff(ns)
    #@+node:tbrown.20140118145024.25546: *4* run_diff_on_saved
    def run_diff_on_saved(self, event=None):
        """run_diff_on_saved - compare current node content to saved
        content

        :Parameters:
        - `event`: Leo event
        """
        c = self.c
        gnx = c.p.gnx
        tree = leosax.get_leo_data(c.fileName())
        for node in tree.flat():
            if node.gnx == gnx:
                node.b = ''.join(node.b)
                self.run_appropriate_diff([node, c.p])
                return
        g.es("Node (gnx) not found in saved file")
    #@+node:tbrown.20140118145024.25562: *4* run_diff_on_vcs
    def run_diff_on_vcs(self, event=None):
        """run_diff_on_vcs - try and check out the previous version of the Leo
        file and compare a node with the same gnx in that file with the
        current node

        :Parameters:
        - `event`: Leo event
        """

        c = self.c

        dir_, filename = g.os_path_split(c.fileName())
        relative_path: list[str] = []  # path from top of repo. to .leo file

        mode = None  # mode is which VCS to use
        # given A=/a/b/c/d/e, B=file.leo adjust to A=/a/b/c, B=d/e/file.leo
        # so that A is the path to the repo. and B the path in the repo. to
        # the .leo file
        path = dir_
        while not mode:
            for vcs in 'git', 'bzr':
                if g.os_path_exists(g.os_path_join(path, '.' + vcs)):
                    mode = vcs
                    break
            else:
                path, subpath = g.os_path_split(path)
                if not subpath:
                    break
                relative_path[0:0] = [subpath]

        if not mode:
            g.es("No supported VCS found in '%s'" % dir_)
            return

        gnx = c.p.gnx

        if mode == 'git':
            cmd = [
                'git',
                '--work-tree=%s' % path,
                'show',
                'HEAD:%s' % g.os_path_join(*(relative_path + [filename])),
            ]

        if mode == 'bzr':
            cmd = [
                'bzr', 'cat',
                '--revision=revno:-1',
                c.fileName(),  # path,
                # g.os_path_join( *(relative_path + [filename]) ),
            ]

        cmd = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        data, err = cmd.communicate()

        aFile = StringIO(data)
        tree = leosax.get_leo_data(aFile)
        for node in tree.flat():
            if node.gnx == gnx:
                node.b = ''.join(node.b)
                self.run_appropriate_diff([node, c.p])
                return
        g.es("Node (gnx) not found in previous version")

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

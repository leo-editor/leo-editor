#@+leo-ver=5-thin
#@+node:ekr.20150514041209.1: * @file ../commands/editFileCommands.py
"""Leo's file-editing commands."""
#@+<< editFileCommands imports & annotations >>
#@+node:ekr.20170806094317.4: ** << editFileCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import difflib
import io
import os
import re
from typing import Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoCommands
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode
#@-<< editFileCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the EditFileCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'editFileCommands',])

#@+others
#@+node:ekr.20210307060752.1: ** class ConvertAtRoot
class ConvertAtRoot:
    """
    A class to convert @root directives to @clean nodes:

    - Change @root directive in body to @clean in the headline.
    - Make clones of section references defined outside of @clean nodes,
      moving them so they are children of the nodes that reference them.
    """

    errors = 0
    root = None  # Root of @root tree.
    root_pat = re.compile(r'^@root\s+(.+)$', re.MULTILINE)
    section_pat = re.compile(r'\s*<\<.+>\>')
    units: list[Position] = []  # List of positions containing @unit.

    #@+others
    #@+node:ekr.20210308044128.1: *3* atRoot.check_move
    def check_clone_move(self, p: Position, parent: Position) -> bool:
        """
        Return False if p or any of p's descendants is a clone of parent
        or any of parents ancestors.
        """
        # Like as checkMoveWithParentWithWarning without warning.
        clonedVnodes = {}
        for ancestor in parent.self_and_parents(copy=False):
            if ancestor.isCloned():
                v = ancestor.v
                clonedVnodes[v] = v
        if not clonedVnodes:
            return True
        for p in p.self_and_subtree(copy=False):
            if p.isCloned() and clonedVnodes.get(p.v):
                return False
        return True
    #@+node:ekr.20210307060752.2: *3* atRoot.convert_file
    def convert_file(self, c: Cmdr) -> None:
        """Convert @root to @clean in the the .leo file at the given path."""
        self.find_all_units(c)
        for p in c.all_positions():
            m = self.root_pat.search(p.b)
            path = m and m.group(1)
            if path:
                # Weird special case. Don't change section definition!
                if self.section_pat.match(p.h):
                    print(f"\nCan not create @clean node: {p.h}\n")
                    self.errors += 1
                else:
                    self.root = p.copy()
                    p.h = f"@clean {path}"
                self.do_root(p)
                self.root = None
        #
        # Check the results.
        link_errors = c.checkOutline(check_links=True)
        self.errors += link_errors
        print(f"{self.errors} error{g.plural(self.errors)} in {c.shortFileName()}")
        c.redraw()
        # if not self.errors: self.dump(c)
    #@+node:ekr.20210308045306.1: *3* atRoot.dump
    def dump(self, c: Cmdr) -> None:
        print(f"Dump of {c.shortFileName()}...")
        for p in c.all_positions():
            print(' ' * 2 * p.level(), p.h)
    #@+node:ekr.20210307075117.1: *3* atRoot.do_root
    def do_root(self, p: Position) -> None:
        """
        Make all necessary clones for section definitions.
        """
        for p in p.self_and_subtree():
            self.make_clones(p)
    #@+node:ekr.20210307085034.1: *3* atRoot.find_all_units
    def find_all_units(self, c: Cmdr) -> None:
        """Scan for all @unit nodes."""
        for p in c.all_positions():
            if '@unit' in p.b:
                self.units.append(p.copy())
    #@+node:ekr.20210307082125.1: *3* atRoot.find_section
    def find_section(self, root: Position, section_name: str) -> Optional[Position]:
        """Find the section definition node in root's subtree for the given section."""

        def munge(s: str) -> str:
            return s.strip().replace(' ', '').lower()

        for p in root.subtree():
            if munge(p.h).startswith(munge(section_name)):
                return p
        return None
    #@+node:ekr.20210307075325.1: *3* atRoot.make_clones
    def make_clones(self, p: Position) -> None:
        """Make clones for all undefined sections in p.b."""
        for s in g.splitLines(p.b):
            m = self.section_pat.match(s)
            if m:
                section_name = g.angleBrackets(m.group(1).strip())
                section_p = self.make_clone(p, section_name)
                if not section_p:
                    print(f"MISSING: {section_name:30} {p.h}")
                    self.errors += 1
    #@+node:ekr.20210307080500.1: *3* atRoot.make_clone
    def make_clone(self, p: Position, section_name: str) -> Optional[Position]:
        """Make c clone for section, if necessary."""

        def clone_and_move(parent: Position, section_p: Position) -> None:
            clone = section_p.clone()
            if self.check_clone_move(clone, parent):
                print(f"  CLONE: {section_p.h:30} parent: {parent.h}")
                clone.moveToLastChildOf(parent)
            else:
                print(f"Can not clone: {section_p.h:30} parent: {parent.h}")
                clone.doDelete()
                self.errors += 1
        #
        # First, look in p's subtree.
        section_p = self.find_section(p, section_name)
        if section_p:
            # g.trace('FOUND', section_name)
            # Already defined in a good place.
            return section_p
        #
        # Finally, look in the @unit tree.
        for unit_p in self.units:
            section_p = self.find_section(unit_p, section_name)
            if section_p:
                clone_and_move(p, section_p)
                return section_p
        return None
    #@-others
#@+node:ekr.20170806094319.14: ** class EditFileCommandsClass
class EditFileCommandsClass(BaseEditCommandsClass):
    """A class to load files into buffers and save buffers to files."""
    #@+others
    #@+node:ekr.20210308051724.1: *3* efc.convert-at-root
    @cmd('convert-at-root')
    def convert_at_root(self, event: Event = None) -> None:
        #@+<< convert-at-root docstring >>
        #@+node:ekr.20210309035627.1: *4* << convert-at-root docstring >>
        #@@wrap
        """
        The convert-at-root command converts @root to @clean throughout the
        outline.

        This command is not perfect. You will need to adjust the outline by hand if
        the command reports errors. I recommend using git diff to ensure that the
        resulting external files are roughly equivalent after running this command.

        This command attempts to do the following:

        - For each node with an @root <path> directive in the body, change the head to
          @clean <path>. The command does *not* change the headline if the node is
          a section definition node. In that case, the command reports an error.

        - Clones and moves nodes as needed so that section definition nodes appear
          as descendants of nodes containing section references. To find section
          definition nodes, the command looks in all @unit trees. After finding the
          required definition node, the command makes a clone of the node and moves
          the clone so it is the last child of the node containing the section
          references. This move may fail. If so, the command reports an error.
        """
        #@-<< convert-at-root docstring >>
        c = event.get('c')
        if not c:
            return
        ConvertAtRoot().convert_file(c)
    #@+node:ekr.20170806094319.11: *3* efc.clean-at-clean commands
    #@+node:ekr.20170806094319.5: *4* efc.cleanAtCleanFiles
    @cmd('clean-at-clean-files')
    def cleanAtCleanFiles(self, event: Event) -> None:
        """Adjust whitespace in all @clean files."""
        c = self.c
        undoType = 'clean-at-clean-files'
        c.undoer.beforeChangeGroup(c.p, undoType, verboseUndoGroup=True)
        total = 0
        for p in c.all_unique_positions():
            if p.isAtCleanNode():
                n = 0
                for p2 in p.subtree():
                    bunch2 = c.undoer.beforeChangeNodeContents(p2)
                    if self.cleanAtCleanNode(p2):
                        n += 1
                        total += 1
                        c.undoer.afterChangeNodeContents(p2, undoType, bunch2)
                g.es_print(f"{n} node{g.plural(n)} {p.h}")
        # Call this only once, at end.
        c.undoer.afterChangeGroup(c.p, undoType)
        if total == 0:
            g.es("Command did not find any whitespace to adjust")
        g.es_print(f"{total} total node{g.plural(total)}")
    #@+node:ekr.20170806094319.8: *4* efc.cleanAtCleanNode
    def cleanAtCleanNode(self, p: Position) -> bool:
        """Adjust whitespace in p, part of an @clean tree."""
        s = p.b.strip()
        if not s or p.h.strip().startswith('<<'):
            return False
        ws = '\n\n' if g.match_word(s, 0, 'class') else '\n'
        s2 = ws + s + ws
        changed = s2 != p.b
        if changed:
            p.b = s2
            p.setDirty()
        return changed
    #@+node:ekr.20170806094319.10: *4* efc.cleanAtCleanTree
    @cmd('clean-at-clean-tree')
    def cleanAtCleanTree(self, event: Event) -> None:
        """
        Clean whitespace in the nearest @clean tree.

        This command is not undoable.
        """
        c = self.c
        # Look for an @clean node.
        for p in c.p.self_and_parents(copy=False):
            if p.isAtCleanNode():
                break
        else:
            g.es_print('no @clean node found', p.h, color='blue')
            return
        # pylint: disable=undefined-loop-variable
        # p is certainly defined here.
        n = 0
        for p2 in p.subtree():
            if self.cleanAtCleanNode(p2):
                n += 1
        if n > 0:
            c.setChanged()
            c.undoer.clearAndWarn('clean-at-clean-tree')
        g.es_print(f"{n} node{g.plural(n)} cleaned")
    #@+node:ekr.20170806094317.6: *3* efc.compareAnyTwoFiles & helpers
    @cmd('file-compare-two-leo-files')
    @cmd('compare-two-leo-files')
    def compareAnyTwoFiles(self, event: Event) -> None:
        """Compare two files."""
        c = c1 = self.c
        w = c.frame.body.wrapper
        commanders = g.app.commanders()
        if g.app.diff:
            if len(commanders) == 2:
                c1, c2 = commanders
                fn1 = g.shortFileName(c1.wrappedFileName) or c1.shortFileName()
                fn2 = g.shortFileName(c2.wrappedFileName) or c2.shortFileName()
                g.es('--diff auto compare', color='red')
                g.es(fn1)
                g.es(fn2)
            else:
                g.es('expecting two .leo files')
                return
        else:
            # Prompt for the file to be compared with the present outline.
            filetypes = [("Leo files", "*.leo *.leojs *.db"), ("All files", "*"),]
            fileName = g.app.gui.runOpenFileDialog(c,
                title="Compare Leo Files", filetypes=filetypes, defaultextension='.leo')
            if not fileName:
                return
            # Read the file into the hidden commander.
            c2 = g.createHiddenCommander(fileName)
            if not c2:
                return
        # Compute the inserted, deleted and changed dicts.
        d1 = self.createFileDict(c1)
        d2 = self.createFileDict(c2)
        inserted, deleted, changed = self.computeChangeDicts(d1, d2)
        # Create clones of all inserted, deleted and changed dicts.
        self.createAllCompareClones(c1, c2, inserted, deleted, changed)
        # Fix bug 1231656: File-Compare-Leo-Files leaves other file open-count incremented.
        if not g.app.diff:
            g.app.forgetOpenFile(fn=c2.fileName())
            c2.frame.destroySelf()
            g.app.gui.set_focus(c, w)
    #@+node:ekr.20170806094317.9: *4* efc.computeChangeDicts
    def computeChangeDicts(self, d1: dict, d2: dict) -> tuple[dict, dict, dict]:
        """
        Compute inserted, deleted, changed dictionaries.

        New in Leo 4.11: show the nodes in the *invisible* file, d2, if possible.
        """
        inserted = {}
        for key in d2:
            if not d1.get(key):
                inserted[key] = d2.get(key)
        deleted = {}
        for key in d1:
            if not d2.get(key):
                deleted[key] = d1.get(key)
        changed = {}
        for key in d1:
            if d2.get(key):
                p1 = d1.get(key)
                p2 = d2.get(key)
                if p1.h != p2.h or p1.b != p2.b:
                    changed[key] = p2  # Show the node in the *other* file.
        return inserted, deleted, changed
    #@+node:ekr.20170806094317.11: *4* efc.createAllCompareClones & helper
    def createAllCompareClones(self,
        c1: Cmdr,
        c2: Cmdr,
        inserted: dict,
        deleted: dict,
        changed: dict,
    ) -> None:
        """Create the comparison trees."""
        c = self.c  # Always use the visible commander
        assert c == c1
        # Create parent node at the start of the outline.
        u, undoType = c.undoer, 'Compare Two Files'
        u.beforeChangeGroup(c.p, undoType)
        undoData = u.beforeInsertNode(c.p)
        parent = c.p.insertAfter()
        parent.setHeadString(undoType)
        u.afterInsertNode(parent, undoType, undoData)
        # Use the wrapped file name if possible.
        fn1 = g.shortFileName(c1.wrappedFileName) or c1.shortFileName()
        fn2 = g.shortFileName(c2.wrappedFileName) or c2.shortFileName()
        for d, kind in (
            (deleted, f"not in {fn2}"),
            (inserted, f"not in {fn1}"),
            (changed, f"changed: as in {fn2}"),
        ):
            self.createCompareClones(d, kind, parent)
        c.selectPosition(parent)
        u.afterChangeGroup(parent, undoType)
        c.redraw()
    #@+node:ekr.20170806094317.12: *5* efc.createCompareClones
    def createCompareClones(self, d: dict[str, str], kind: str, parent: Position) -> None:
        if d:
            c = self.c  # Use the visible commander.
            parent = parent.insertAsLastChild()
            parent.setHeadString(kind)
            for key in d:
                p = d.get(key)
                if not kind.endswith('.leo') and p.isAnyAtFileNode():
                    # Don't make clones of @<file> nodes for wrapped files.
                    pass
                elif p.v.context == c:
                    clone = p.clone()
                    clone.moveToLastChildOf(parent)
                else:
                    # Fix bug 1160660: File-Compare-Leo-Files creates "other file" clones.
                    copy = p.copyTreeAfter()
                    copy.moveToLastChildOf(parent)
                    for p2 in copy.self_and_subtree(copy=False):
                        p2.v.context = c
    #@+node:ekr.20170806094317.17: *4* efc.createFileDict
    def createFileDict(self, c: Cmdr) -> dict[str, Position]:
        """Create a dictionary of all relevant positions in commander c."""
        d: dict[str, Position] = {}
        for p in c.all_positions():
            d[p.v.fileIndex] = p.copy()
        return d
    #@+node:ekr.20170806094317.19: *4* efc.dumpCompareNodes
    def dumpCompareNodes(self,
        fileName1: str,
        fileName2: str,
        inserted: dict,
        deleted: dict,
        changed: dict,
    ) -> None:
        for d, kind in (
            (inserted, f"inserted (only in {fileName1})"),
            (deleted, f"deleted  (only in {fileName2})"),
            (changed, 'changed'),
        ):
            g.pr('\n', kind)
            for key in d:
                p = d.get(key)
                g.pr(f"{key:>32} {p.h}")
    #@+node:ekr.20170806094319.3: *3* efc.compareTrees
    def compareTrees(self, p1: Position, p2: Position, tag: str) -> None:


        class CompareTreesController:
            #@+others
            #@+node:ekr.20170806094318.18: *4* ct.compare
            def compare(self, d1: dict, d2: dict, root: Position) -> Position:
                """Compare dicts d1 and d2."""
                for h in sorted(d1.keys()):
                    p1, p2 = d1.get(h), d2.get(h)
                    if h in d2:
                        lines1, lines2 = g.splitLines(p1.b), g.splitLines(p2.b)
                        aList = list(difflib.unified_diff(lines1, lines2, 'vr1', 'vr2'))
                        if aList:
                            p = root.insertAsLastChild()
                            p.h = h
                            p.b = ''.join(aList)
                            p1.clone().moveToLastChildOf(p)
                            p2.clone().moveToLastChildOf(p)
                    elif p1.b.strip():
                        # Only in p1 tree, and not an organizer node.
                        p = root.insertAsLastChild()
                        p.h = h + f"({p1.h} only)"
                        p1.clone().moveToLastChildOf(p)
                for h in sorted(d2.keys()):
                    p2 = d2.get(h)
                    if h not in d1 and p2.b.strip():
                        # Only in p2 tree, and not an organizer node.
                        p = root.insertAsLastChild()
                        p.h = h + f"({p2.h} only)"
                        p2.clone().moveToLastChildOf(p)
                return root
            #@+node:ekr.20170806094318.19: *4* ct.run
            def run(self, c: Cmdr, p1: Position, p2: Position, tag: str) -> None:
                """Main line."""
                self.c = c
                root = c.p.insertAfter()
                root.h = tag
                d1 = self.scan(p1)
                d2 = self.scan(p2)
                self.compare(d1, d2, root)
                c.p.contract()
                root.expand()
                c.selectPosition(root)
                c.redraw()
            #@+node:ekr.20170806094319.2: *4* ct.scan
            def scan(self, p1: Position) -> dict[str, Position]:
                """
                Create a dict of the methods in p1.
                Keys are headlines, stripped of prefixes.
                Values are copies of positions.
                """
                d: dict[str, Position] = {}
                for p in p1.self_and_subtree(copy=False):
                    h = p.h.strip()
                    i = h.find('.')
                    if i > -1:
                        h = h[i + 1 :].strip()
                    if h in d:
                        g.es_print('duplicate', p.h)
                    else:
                        d[h] = p.copy()
                return d
            #@-others

        CompareTreesController().run(self.c, p1, p2, tag)
    #@+node:ekr.20170806094318.1: *3* efc.deleteFile
    @cmd('file-delete')
    def deleteFile(self, event: Event) -> None:
        """Prompt for the name of a file and delete it."""
        k = self.c.k
        k.setLabelBlue('Delete File: ')
        k.extendLabel(os.getcwd() + os.sep)
        k.get1Arg(event, handler=self.deleteFile1)

    def deleteFile1(self, event: Event) -> None:
        k = self.c.k
        k.keyboardQuit()
        k.clearState()
        try:
            os.remove(k.arg)
            k.setStatusLabel(f"Deleted: {k.arg}")
        except Exception:
            k.setStatusLabel(f"Not Deleted: {k.arg}")
    #@+node:ekr.20170806094318.3: *3* efc.diff (file-diff-files)
    @cmd('file-diff-files')
    def diff(self, event: Event = None) -> None:
        """Creates a node and puts the diff between 2 files into it."""
        c = self.c
        fn = self.getReadableTextFile()
        if not fn:
            return
        fn2 = self.getReadableTextFile()
        if not fn2:
            return
        s1, e = g.readFileIntoString(fn)
        if s1 is None:
            return
        s2, e = g.readFileIntoString(fn2)
        if s2 is None:
            return
        lines1, lines2 = g.splitLines(s1), g.splitLines(s2)
        aList = difflib.ndiff(lines1, lines2)
        p = c.p.insertAfter()
        p.h = 'diff'
        p.b = ''.join(aList)
        c.redraw()
    #@+node:ekr.20170806094318.6: *3* efc.getReadableTextFile
    def getReadableTextFile(self) -> str:
        """Prompt for a text file."""
        c = self.c
        fn = g.app.gui.runOpenFileDialog(c,
            title='Open Text File',
            filetypes=[("Text", "*.txt"), ("All files", "*")],
            defaultextension=".txt")
        return fn
    #@+node:ekr.20170819035801.90: *3* efc.gitDiff (gd & git-diff)
    @cmd('git-diff')
    @cmd('gd')
    def gitDiff(self, event: Event = None) -> None:
        """Produce a Leonine git diff."""
        GitDiffController(c=self.c).git_diff(rev1='HEAD')
    #@+node:ekr.20201215093414.1: *3* efc.gitDiffPR (git-diff-pr & git-diff-pull-request)
    @cmd('git-diff-pull-request')
    @cmd('git-diff-pr')
    def gitDiffPullRequest(self, event: Event = None) -> None:
        """
        Produce a Leonine diff of pull request in the current branch.
        """
        GitDiffController(c=self.c).diff_pull_request()
    #@+node:ekr.20170806094318.7: *3* efc.insertFile
    @cmd('file-insert')
    def insertFile(self, event: Event) -> None:
        """
        Prompt for the name of a file.
        Insert the file's contents in the body at the insertion point.
        """
        w = self.editWidget(event)
        if not w:
            return
        fn = self.getReadableTextFile()
        if not fn:
            return
        s, e = g.readFileIntoString(fn)
        if s:
            self.beginCommand(w, undoType='insert-file')
            i = w.getInsertPoint()
            w.insert(i, s)
            w.seeInsertPoint()
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20170806094318.9: *3* efc.makeDirectory
    @cmd('directory-make')
    def makeDirectory(self, event: Event) -> None:
        """Prompt for the name of a directory and create it."""
        k = self.c.k
        k.setLabelBlue('Make Directory: ')
        k.extendLabel(os.getcwd() + os.sep)
        k.get1Arg(event, handler=self.makeDirectory1)

    def makeDirectory1(self, event: Event) -> None:
        k = self.c.k
        k.keyboardQuit()
        k.clearState()
        try:
            os.mkdir(k.arg)
            k.setStatusLabel(f"Created: {k.arg}")
        except Exception:
            k.setStatusLabel(f"Not Created: {k.arg}")
    #@+node:ekr.20170806094318.12: *3* efc.openOutlineByName
    @cmd('file-open-by-name')
    def openOutlineByName(self, event: Event) -> None:
        """file-open-by-name: Prompt for the name of a Leo outline and open it."""
        c, k = self.c, self.c.k
        fileName = ''.join(k.givenArgs)
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if fileName and g.os_path_exists(fileName):
            g.openWithFileName(fileName, old_c=c)
        else:
            k.setLabelBlue('Open Leo Outline: ')
            k.getFileName(event, callback=self.openOutlineByNameFinisher)

    def openOutlineByNameFinisher(self, fn: str) -> None:
        c = self.c
        if fn and g.os_path_exists(fn) and not g.os_path_isdir(fn):
            c2 = g.openWithFileName(fn, old_c=c)
            try:
                g.app.gui.runAtIdle(c2.treeWantsFocusNow)
            except Exception:
                pass
        else:
            g.es(f"ignoring: {fn}")
    #@+node:ekr.20170806094318.14: *3* efc.removeDirectory
    @cmd('directory-remove')
    def removeDirectory(self, event: Event) -> None:
        """Prompt for the name of a directory and delete it."""
        k = self.c.k
        k.setLabelBlue('Remove Directory: ')
        k.extendLabel(os.getcwd() + os.sep)
        k.get1Arg(event, handler=self.removeDirectory1)

    def removeDirectory1(self, event: Event) -> None:
        k = self.c.k
        k.keyboardQuit()
        k.clearState()
        try:
            os.rmdir(k.arg)
            k.setStatusLabel(f"Removed: {k.arg}")
        except Exception:
            k.setStatusLabel(f"Not Removed: {k.arg}")
    #@+node:ekr.20170806094318.15: *3* efc.saveFile (save-file-by-name)
    @cmd('file-save-by-name')
    @cmd('save-file-by-name')
    def saveFile(self, event: Event) -> None:
        """Prompt for the name of a file and put the body text of the selected node into it.."""
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        fileName = g.app.gui.runSaveFileDialog(c,
            title='save-file',
            filetypes=[("Text", "*.txt"), ("All files", "*")],
            defaultextension=".txt")
        if fileName:
            try:
                s = w.getAllText()
                with open(fileName, 'w') as f:
                    f.write(s)
            except IOError:
                g.es('can not create', fileName)
    #@+node:ekr.20170806094319.15: *3* efc.toggleAtAutoAtEdit & helpers
    @cmd('toggle-at-auto-at-edit')
    def toggleAtAutoAtEdit(self, event: Event) -> None:
        """Toggle between @auto and @edit, preserving insert point, etc."""
        p = self.c.p
        if p.isAtEditNode():
            self.toAtAuto(p)
            return
        for p in p.self_and_parents():
            if p.isAtAutoNode():
                self.toAtEdit(p)
                return
        g.es_print('Not in an @auto or @edit tree.', color='blue')
    #@+node:ekr.20170806094319.17: *4* efc.toAtAuto
    def toAtAuto(self, p: Position) -> None:
        """Convert p from @edit to @auto."""
        c = self.c
        # Change the headline.
        p.h = '@auto' + p.h[5:]
        # Compute the position of the present line within the file.
        w = c.frame.body.wrapper
        ins = w.getInsertPoint()
        row, col = g.convertPythonIndexToRowCol(p.b, ins)
        # Ignore *preceding* directive lines.
        directives = [z for z in g.splitLines(c.p.b)[:row] if g.isDirective(z)]
        row -= len(directives)
        row = max(0, row)
        # Reload the file, creating new nodes.
        c.selectPosition(p)
        c.refreshFromDisk()
        # Restore the line in the proper node.
        c.gotoCommands.find_file_line(row + 1)
        p.setDirty()
        c.setChanged()
        c.redraw()
        c.bodyWantsFocus()
    #@+node:ekr.20170806094319.19: *4* efc.toAtEdit
    def toAtEdit(self, p: Position) -> None:
        """Convert p from @auto to @edit."""
        c = self.c
        w = c.frame.body.wrapper
        p.h = '@edit' + p.h[5:]
        # Compute the position of the present line within the *selected* node c.p
        ins = w.getInsertPoint()
        row, col = g.convertPythonIndexToRowCol(c.p.b, ins)
        # Ignore directive lines.
        directives = [z for z in g.splitLines(c.p.b)[:row] if g.isDirective(z)]
        row -= len(directives)
        row = max(0, row)
        # Count preceding lines from p to c.p, again ignoring directives.
        for p2 in p.self_and_subtree(copy=False):
            if p2 == c.p:
                break
            lines = [z for z in g.splitLines(p2.b) if not g.isDirective(z)]
            row += len(lines)
        # Reload the file into a single node.
        c.selectPosition(p)
        c.refreshFromDisk()
        # Restore the line in the proper node.
        ins = g.convertRowColToPythonIndex(p.b, row + 1, 0)
        w.setInsertPoint(ins)
        p.setDirty()
        c.setChanged()
        c.redraw()
        c.bodyWantsFocus()
    #@-others
#@+node:ekr.20170806094320.13: ** class GitDiffController
class GitDiffController:
    """A class to do git diffs."""

    def __init__(self, c: Cmdr) -> None:
        self.c = c
        self.file_node: Position = None
        self.root: Position = None
    #@+others
    #@+node:ekr.20180510095544.1: *3* gdc.Entries...
    #@+node:ekr.20170806094320.6: *4* gdc.diff_file
    def diff_file(self, fn: str, rev1: str = 'HEAD', rev2: str = '') -> None:
        """
        Create an outline describing the git diffs for fn.
        """
        c = self.c
        directory = self.get_directory()
        if not directory:
            return
        s1 = self.get_file_from_rev(rev1, fn)
        s2 = self.get_file_from_rev(rev2, fn)
        lines1 = g.splitLines(s1)
        lines2 = g.splitLines(s2)
        diff_list = list(difflib.unified_diff(
            lines1,
            lines2,
            rev1 or 'uncommitted',
            rev2 or 'uncommitted',
        ))
        diff_list.insert(0, '@ignore\n@nosearch\n@language patch\n')
        self.file_node = self.create_file_node(diff_list, fn)
        # #1777: The file node will contain the entire added/deleted file.
        if not s1:
            self.file_node.h = f"Added: {self.file_node.h}"
            return
        if not s2:
            self.file_node.h = f"Deleted: {self.file_node.h}"
            return
        # Finish.
        path = g.finalize_join(directory, fn)  # #1781: bug fix.
        c1 = c2 = None
        if fn.endswith('.leo'):
            c1 = self.make_leo_outline(fn, path, s1, rev1)
            c2 = self.make_leo_outline(fn, path, s2, rev2)
        else:
            root = self.find_file(fn)
            if c.looksLikeDerivedFile(path):
                c1 = self.make_at_file_outline(fn, s1, rev1)
                c2 = self.make_at_file_outline(fn, s2, rev2)
            elif root:
                c1 = self.make_at_clean_outline(fn, root, s1, rev1)
                c2 = self.make_at_clean_outline(fn, root, s2, rev2)
        if c1 and c2:
            self.make_diff_outlines(c1, c2, fn, rev1, rev2)
            self.file_node.b = (
                f"{self.file_node.b.rstrip()}\n"
                f"@language {c2.target_language}\n")
    #@+node:ekr.20201208115447.1: *4* gdc.diff_pull_request
    def diff_pull_request(self) -> None:
        """
        Create a Leonine version of the diffs that would be
        produced by a pull request between two branches.
        """
        directory = self.get_directory()
        if not directory:
            return
        aList = g.execGitCommand("git rev-parse devel", directory)
        if aList:
            devel_rev = aList[0]
            devel_rev = devel_rev[:8]
            g.trace('devel_rev', devel_rev)
            self.diff_two_revs(
                rev1=devel_rev,  # Before: Latest devel commit.
                rev2='HEAD',  # After: Latest branch commit
            )
        else:
            g.es_print('FAIL: git rev-parse devel')
    #@+node:ekr.20180506064102.10: *4* gdc.diff_two_branches
    def diff_two_branches(self, branch1: str, branch2: str, fn: str) -> None:
        """Create an outline describing the git diffs for fn."""
        c = self.c
        u, undoType = c.undoer, 'diff-two-branches'
        if not self.get_directory():
            return
        c.selectPosition(c.lastTopLevel())
        undoData = u.beforeInsertNode(c.p)
        self.root = p = c.lastTopLevel().insertAfter()
        p.h = f"git-diff-branches {branch1} {branch2}"
        s1 = self.get_file_from_branch(branch1, fn)
        s2 = self.get_file_from_branch(branch2, fn)
        lines1 = g.splitLines(s1)
        lines2 = g.splitLines(s2)
        diff_list = list(difflib.unified_diff(lines1, lines2, branch1, branch2,))
        diff_list.insert(0, '@ignore\n@nosearch\n@language patch\n')
        self.file_node = self.create_file_node(diff_list, fn)
        if c.looksLikeDerivedFile(fn):
            c1 = self.make_at_file_outline(fn, s1, branch1)
            c2 = self.make_at_file_outline(fn, s2, branch2)
        else:
            root = self.find_file(fn)
            if root:
                c1 = self.make_at_clean_outline(fn, root, s1, branch1)
                c2 = self.make_at_clean_outline(fn, root, s2, branch2)
            else:
                c1 = c2 = None
        if c1 and c2:
            self.make_diff_outlines(c1, c2, fn)
            self.file_node.b = f"{self.file_node.b.rstrip()}\n@language {c2.target_language}\n"
        u.afterInsertNode(self.root, undoType, undoData)
        self.finish()
    #@+node:ekr.20180507212821.1: *4* gdc.diff_two_revs
    def diff_two_revs(self, rev1: str = 'HEAD', rev2: str = '') -> None:
        """
        Create an outline describing the git diffs for all files changed
        between rev1 and rev2.
        """
        c, u = self.c, self.c.undoer

        if not self.get_directory():
            return
        # Get list of changed files.
        files = self.get_files(rev1, rev2)
        n = len(files)
        message = f"diffing {n} file{g.plural(n)}"
        if not g.unitTesting:
            if n > 5:
                message += ". This may take awhile..."
            g.es_print(message)
        c.selectPosition(c.lastTopLevel())  # pre-select to help undo-insert

        # Create the root node.
        undoData = u.beforeInsertNode(c.p)  # c.p is subject of 'insertAfter'
        self.root = c.lastTopLevel().insertAfter()
        self.root.h = f"git diff revs: {rev1} {rev2}"
        self.root.b = '@ignore\n@nosearch\n'

        # Create diffs of all files.
        for fn in files:
            self.diff_file(fn=fn, rev1=rev1, rev2=rev2)

        u.afterInsertNode(self.root, 'diff-two-revs', undoData)
        self.finish()
    #@+node:ekr.20170806094320.12: *4* gdc.git_diff & helper
    def git_diff(self, rev1: str = 'HEAD', rev2: str = '') -> None:
        """The main line of the git diff command."""
        if not self.get_directory():
            return
        # Diff the given revs.
        ok = self.diff_revs(rev1, rev2)
        if ok:
            return
        # Go back at most 5 revs...
        n1, n2 = 1, 0
        while n1 <= 5:
            ok = self.diff_revs(
                rev1=f"HEAD@{{{n1}}}",
                rev2=f"HEAD@{{{n2}}}")
            if ok:
                return
            n1, n2 = n1 + 1, n2 + 1
        if not ok:
            g.es_print('no changed readable files from HEAD@{1}..HEAD@{5}')
    #@+node:ekr.20170820082125.1: *5* gdc.diff_revs
    def diff_revs(self, rev1: str, rev2: str) -> bool:
        """
        A helper for Leo's git-diff command

        Diff all files given by rev1 and rev2.
        """
        c = self.c
        u = c.undoer
        undoType = 'git-diff-revs'
        files = self.get_files(rev1, rev2)
        if not files:
            return False
        c.selectPosition(c.lastTopLevel())
        undoData = u.beforeInsertNode(c.p)
        self.root = self.create_root(rev1, rev2)
        for fn in files:
            self.diff_file(fn=fn, rev1=rev1, rev2=rev2)
        u.afterInsertNode(self.root, undoType, undoData)
        self.finish()
        return True
    #@+node:ekr.20180510095801.1: *3* gdc.Utils
    #@+node:ekr.20170806191942.2: *4* gdc.create_compare_node
    def create_compare_node(self,
        c1: Cmdr,
        c2: Cmdr,
        d: dict[str, tuple[VNode, VNode]],
        kind: str,
        rev1: str,
        rev2: str,
    ) -> None:
        """Create nodes describing the changes."""
        if not d:
            return
        parent = self.file_node.insertAsLastChild()
        parent.setHeadString(f"diff: {kind}")
        for key in d:
            if kind.lower() == 'changed':
                v1, v2 = d.get(key)
                # Organizer node: contains diff
                organizer = parent.insertAsLastChild()
                organizer.h = f"diff: {v2.h}"
                body = list(difflib.unified_diff(
                    g.splitLines(v1.b),
                    g.splitLines(v2.b),
                    rev1 or 'uncommitted',
                    rev2 or 'uncommitted',
                ))
                if ''.join(body).strip():
                    body.insert(0, '@ignore\n@nosearch\n@language patch\n')
                    body.append(f"@language {c2.target_language}\n")
                else:
                    body = ['Only headline has changed']
                organizer.b = ''.join(body)
                # Node 2: Old node
                p2 = organizer.insertAsLastChild()
                p2.h = 'Old:' + v1.h
                p2.b = v1.b
                # Node 3: New node
                assert v1.fileIndex == v2.fileIndex
                p_in_c = self.find_gnx(self.c, v1.fileIndex)
                if p_in_c:  # Make a clone, if possible.
                    p3 = p_in_c.clone()
                    p3.moveToLastChildOf(organizer)
                else:
                    p3 = organizer.insertAsLastChild()
                    p3.h = 'New:' + v2.h
                    p3.b = v2.b
            elif kind.lower() == 'added':
                v = d.get(key)
                new_p = self.find_gnx(self.c, v.fileIndex)
                if new_p:  # Make a clone, if possible.
                    p = new_p.clone()
                    p.moveToLastChildOf(parent)
                    # #2950: do not change p.b.
                else:
                    p = parent.insertAsLastChild()
                    p.h = v.h
                    p.b = v.b
            else:
                v = d.get(key)
                p = parent.insertAsLastChild()
                p.h = v.h
                p.b = v.b
    #@+node:ekr.20170806094321.1: *4* gdc.create_file_node
    def create_file_node(self, diff_list: list[str], fn: str) -> Position:
        """Create an organizer node for the file."""
        p = self.root.insertAsLastChild()
        p.h = 'diff: ' + fn.strip()
        p.b = ''.join(diff_list)
        return p
    #@+node:ekr.20170806094320.18: *4* gdc.create_root
    def create_root(self, rev1: str, rev2: str) -> Position:
        """Create the top-level organizer node describing the git diff."""
        c = self.c
        r1, r2 = rev1 or '', rev2 or ''
        p = c.lastTopLevel().insertAfter()
        p.h = f"git diff {r1} {r2}"
        p.b = '@ignore\n@nosearch\n'
        if r1 and r2:
            p.b += (
                f"{r1}={self.get_revno(r1)}\n"
                f"{r2}={self.get_revno(r2)}")
        else:
            p.b += f"{r1}={self.get_revno(r1)}"
        return p
    #@+node:ekr.20170806094320.7: *4* gdc.find_file
    def find_file(self, fn: str) -> Optional[Position]:
        """Return the @<file> node matching fn."""
        c = self.c
        fn = g.os_path_basename(fn)
        for p in c.all_unique_positions():
            if p.isAnyAtFileNode():
                fn2 = p.anyAtFileNodeName()
                if fn2.endswith(fn):
                    return p
        return None
    #@+node:ekr.20170806094321.3: *4* gdc.find_git_working_directory
    def find_git_working_directory(self, directory: str) -> Optional[str]:
        """Return the git working directory, starting at directory."""
        while directory:
            if g.os_path_exists(g.finalize_join(directory, '.git')):
                return directory
            path2 = g.finalize_join(directory, '..')
            if path2 == directory:
                break
            directory = path2
        return None
    #@+node:ekr.20170819132219.1: *4* gdc.find_gnx
    def find_gnx(self, c: Cmdr, gnx: str) -> Optional[Position]:
        """Return a position in c having the given gnx."""
        for p in c.all_unique_positions():
            if p.v.fileIndex == gnx:
                return p
        return None
    #@+node:ekr.20170806094321.5: *4* gdc.finish
    def finish(self) -> None:
        """Finish execution of this command."""
        c = self.c
        c.selectPosition(self.root)
        self.root.expand()
        c.redraw(self.root)
        c.treeWantsFocusNow()
    #@+node:ekr.20210819080657.1: *4* gdc.get_directory
    def get_directory(self) -> Optional[str]:
        """
        #2143.
        Resolve filename to the nearest directory containing a .git directory.
        """
        c = self.c
        filename = c.fileName()
        if not filename:
            print('git-diff: outline has no name')
            return None
        directory = os.path.dirname(filename)
        if directory and not os.path.isdir(directory):
            directory = os.path.dirname(directory)
        if not directory:
            print(f"git-diff: outline has no directory. filename: {filename!r}")
            return None
        # Does path/../ref exist?
        base_directory = g.gitHeadPath(directory)
        if not base_directory:
            print(f"git-diff: no .git directory: {directory!r} filename: {filename!r}")
            return None
        # This should guarantee that the directory contains a .git directory.
        directory = g.finalize_join(base_directory, '..', '..')
        return directory
    #@+node:ekr.20180506064102.11: *4* gdc.get_file_from_branch
    def get_file_from_branch(self, branch: str, fn: str) -> str:
        """Get the file from the head of the given branch."""
        # #2143
        directory = self.get_directory()
        if not directory:
            return ''
        command = f"git show {branch}:{fn}"
        lines = g.execGitCommand(command, directory)
        s = ''.join(lines)
        return g.toUnicode(s).replace('\r', '')
    #@+node:ekr.20170806094320.15: *4* gdc.get_file_from_rev
    def get_file_from_rev(self, rev: str, fn: str) -> str:
        """Get the file from the given rev, or the working directory if None."""
        # #2143
        directory = self.get_directory()
        if not directory:
            return ''
        path = g.finalize_join(directory, fn)
        if rev:
            # Get the file using git.
            # Use the file name, not the path.
            command = f"git show {rev}:{fn}"
            lines = g.execGitCommand(command, directory)
            return g.toUnicode(''.join(lines)).replace('\r', '')
        try:
            with open(path, 'rb') as f:
                b = f.read()
            return g.toUnicode(b).replace('\r', '')
        except Exception:
            g.es_print('Can not read', path)
            g.es_exception()
            return ''
    #@+node:ekr.20170806094320.9: *4* gdc.get_files
    def get_files(self, rev1: str, rev2: str) -> list[str]:
        """Return a list of changed files."""
        # #2143
        directory = self.get_directory()
        if not directory:
            return []
        command = f"git diff --name-only {(rev1 or '')} {(rev2 or '')}"
        # #1781: Allow diffs of .leo files.
        return [
            z.strip() for z in g.execGitCommand(command, directory)
                if not z.strip().endswith(('.db', '.zip'))
        ]
    #@+node:ekr.20170821052348.1: *4* gdc.get_revno
    def get_revno(self, revspec: str, abbreviated: bool = True) -> str:
        """Return the abbreviated hash for the given revision spec."""
        if not revspec:
            return 'uncommitted'
        # Return only the abbreviated hash for the revspec.
        format_s = 'h' if abbreviated else 'H'
        command = f"git show --format=%{format_s} --no-patch {revspec}"
        directory = self.get_directory()
        lines = g.execGitCommand(command, directory=directory)
        return ''.join(lines).strip()
    #@+node:ekr.20170820084258.1: *4* gdc.make_at_clean_outline
    def make_at_clean_outline(self, fn: str, root: Position, s: str, rev: str) -> Cmdr:
        """
        Create a hidden temp outline from lines without sentinels.
        root is the @<file> node for fn.
        s is the contents of the (public) file, without sentinels.
        """
        # A specialized version of at.readOneAtCleanNode.
        hidden_c = leoCommands.Commands(fn, gui=g.app.nullGui)
        at = hidden_c.atFileCommands
        x = hidden_c.shadowController
        hidden_c.frame.createFirstTreeNode()
        hidden_root = hidden_c.rootPosition()
        # copy root to hidden root, including gnxs.
        root.copyTreeFromSelfTo(hidden_root, copyGnxs=True)
        hidden_root.h = fn + ':' + rev if rev else fn
        # Set at.encoding first.
        # Must be called before at.scanAllDirectives.
        at.initReadIvars(hidden_root, fn)
        # Sets at.startSentinelComment/endSentinelComment.
        at.scanAllDirectives(hidden_root)
        new_public_lines = g.splitLines(s)
        old_private_lines = at.write_at_clean_sentinels(hidden_root)
        marker = x.markerFromFileLines(old_private_lines, fn)
        old_public_lines, junk = x.separate_sentinels(old_private_lines, marker)
        if old_public_lines:
            # Fix #1136: The old lines might not exist.
            new_private_lines = x.propagate_changed_lines(
                new_public_lines, old_private_lines, marker, p=hidden_root)
            at.fast_read_into_root(
                c=hidden_c,
                contents=''.join(new_private_lines),
                gnx2vnode={},
                path=fn,
                root=hidden_root,
            )
        return hidden_c
    #@+node:ekr.20170806094321.7: *4* gdc.make_at_file_outline
    def make_at_file_outline(self, fn: str, s: str, rev: str) -> Cmdr:
        """Create a hidden temp outline from lines."""
        # A specialized version of atFileCommands.read.
        hidden_c = leoCommands.Commands(fn, gui=g.app.nullGui)
        at = hidden_c.atFileCommands
        hidden_c.frame.createFirstTreeNode()
        root = hidden_c.rootPosition()
        root.h = fn + ':' + rev if rev else fn
        at.initReadIvars(root, fn)
        if at.errors > 0:
            g.trace('***** errors')
            return None
        at.fast_read_into_root(
            c=hidden_c,
            contents=s,
            gnx2vnode={},
            path=fn,
            root=root,
        )
        return hidden_c
    #@+node:ekr.20170806125535.1: *4* gdc.make_diff_outlines & helper
    def make_diff_outlines(self,
        c1: Cmdr,
        c2: Cmdr,
        fn: str,
        rev1: str = '',
        rev2: str = '',
    ) -> None:
        """Create an outline-oriented diff from the *hidden* outlines c1 and c2."""
        added, deleted, changed = self.compute_dicts(c1, c2)
        table = (
            (added, 'Added'),
            (deleted, 'Deleted'),
            (changed, 'Changed'))
        for d, kind in table:
            self.create_compare_node(c1, c2, d, kind, rev1, rev2)
    #@+node:ekr.20170806191707.1: *5* gdc.compute_dicts
    def compute_dicts(self, c1: Cmdr, c2: Cmdr) -> tuple[dict, dict, dict]:
        """Compute inserted, deleted, changed dictionaries."""
        # Special case the root: only compare the body text.
        root1, root2 = c1.rootPosition().v, c2.rootPosition().v
        root1.h = root2.h
        if 0:
            g.trace('c1...')
            for p in c1.all_positions():
                print(f"{len(p.b):4} {p.h}")
            g.trace('c2...')
            for p in c2.all_positions():
                print(f"{len(p.b):4} {p.h}")
        d1 = {v.fileIndex: v for v in c1.all_unique_nodes()}
        d2 = {v.fileIndex: v for v in c2.all_unique_nodes()}
        added = {key: d2.get(key) for key in d2 if not d1.get(key)}
        deleted = {key: d1.get(key) for key in d1 if not d2.get(key)}
        # Remove the root from the added and deleted dicts.
        if root2.fileIndex in added:
            del added[root2.fileIndex]
        if root1.fileIndex in deleted:
            del deleted[root1.fileIndex]
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
    #@+node:ekr.20201215050832.1: *4* gdc.make_leo_outline
    def make_leo_outline(self, fn: str, path: str, s: str, rev: str) -> Cmdr:
        """Create a hidden temp outline for the .leo file in s."""
        hidden_c = leoCommands.Commands(fn, gui=g.app.nullGui)
        hidden_c.frame.createFirstTreeNode()
        root = hidden_c.rootPosition()
        root.h = fn + ':' + rev if rev else fn
        hidden_c.fileCommands.getLeoFile(
            theFile=io.StringIO(initial_value=s),
            fileName=path,
            readAtFileNodesFlag=False,
            silent=False,
            checkOpenFiles=False,
        )
        return hidden_c
    #@-others
#@-others
#@@language python
#@-leo

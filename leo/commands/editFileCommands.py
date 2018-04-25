# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514041209.1: * @file ../commands/editFileCommands.py
#@@first
'''Leo's file-editing commands.'''
#@+<< imports >>
#@+node:ekr.20170806094317.4: ** << imports >> (editFileCommands.py)
import difflib
import os
import leo.core.leoGlobals as g
import leo.core.leoCommands as leoCommands
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    '''Command decorator for the EditFileCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'editFileCommands',])

#@+others
#@+node:ekr.20170806094319.14: ** class EditFileCommandsClass
class EditFileCommandsClass(BaseEditCommandsClass):
    '''A class to load files into buffers and save buffers to files.'''
    #@+others
    #@+node:ekr.20170806094319.11: *3* efc.clean-at-clean commands
    #@+node:ekr.20170806094319.5: *4* efc.cleanAtCleanFiles
    @cmd('clean-at-clean-files')
    def cleanAtCleanFiles(self, event):
        '''Adjust whitespace in all @clean files.'''
        c = self.c
        undoType = 'clean-@clean-files'
        c.undoer.beforeChangeGroup(c.p, undoType, verboseUndoGroup=True)
        total = 0
        for p in c.all_unique_positions():
            if g.match_word(p.h, 0, '@clean') and p.h.rstrip().endswith('.py'):
                n = 0
                for p2 in p.subtree():
                    bunch2 = c.undoer.beforeChangeNodeContents(p2, oldBody=p2.b)
                    if self.cleanAtCleanNode(p2, undoType):
                        n += 1
                        total += 1
                        c.undoer.afterChangeNodeContents(p2, undoType, bunch2)
                g.es_print('%s node%s %s' % (n, g.plural(n), p.h))
        if total > 0:
            c.undoer.afterChangeGroup(c.p, undoType)
        g.es_print('%s total node%s' % (total, g.plural(total)))
    #@+node:ekr.20170806094319.8: *4* efc.cleanAtCleanNode
    def cleanAtCleanNode(self, p, undoType):
        '''Adjust whitespace in p, part of an @clean tree.'''
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
    def cleanAtCleanTree(self, event):
        '''
        Adjust whitespace in the nearest @clean tree,
        searching c.p and its ancestors.
        '''
        c = self.c
        # Look for an @clean node.
        for p in c.p.self_and_parents():
            if g.match_word(p.h, 0, '@clean') and p.h.rstrip().endswith('.py'):
                break
        else:
            g.es_print('no an @clean node found', p.h, color='blue')
            return
        # pylint: disable=undefined-loop-variable
        # p is certainly defined here.
        bunch = c.undoer.beforeChangeTree(p)
        n = 0
        undoType = 'clean-@clean-tree'
        for p2 in p.subtree():
            if self.cleanAtCleanNode(p2, undoType):
                n += 1
        if n > 0:
            c.setChanged(True)
            c.undoer.afterChangeTree(p, undoType, bunch)
        g.es_print('%s node%s cleaned' % (n, g.plural(n)))
    #@+node:ekr.20170806094317.6: *3* efc.compareAnyTwoFiles & helpers
    @cmd('file-compare-two-leo-files')
    @cmd('compare-two-leo-files')
    def compareAnyTwoFiles(self, event):
        '''Compare two files.'''
        trace = False and not g.unitTesting
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
            filetypes = [("Leo files", "*.leo"), ("All files", "*"),]
            fileName = g.app.gui.runOpenFileDialog(c,
                title="Compare .leo Files", filetypes=filetypes, defaultextension='.leo')
            if not fileName: return
            # Read the file into the hidden commander.
            c2 = self.createHiddenCommander(fileName)
            if not c2: return
        # Compute the inserted, deleted and changed dicts.
        d1 = self.createFileDict(c1)
        d2 = self.createFileDict(c2)
        inserted, deleted, changed = self.computeChangeDicts(d1, d2)
        if trace: self.dumpCompareNodes(fileName, c1.mFileName, inserted, deleted, changed)
        # Create clones of all inserted, deleted and changed dicts.
        self.createAllCompareClones(c1, c2, inserted, deleted, changed)
        # Fix bug 1231656: File-Compare-Leo-Files leaves other file open-count incremented.
        if not g.app.diff:
            g.app.forgetOpenFile(fn=c2.fileName(), force=True)
            c2.frame.destroySelf()
            g.app.gui.set_focus(c, w)
    #@+node:ekr.20170806094317.9: *4* efc.computeChangeDicts
    def computeChangeDicts(self, d1, d2):
        '''
        Compute inserted, deleted, changed dictionaries.

        New in Leo 4.11: show the nodes in the *invisible* file, d2, if possible.
        '''
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
                    changed[key] = p2 # Show the node in the *other* file.
        return inserted, deleted, changed
    #@+node:ekr.20170806094317.11: *4* efc.createAllCompareClones & helper
    def createAllCompareClones(self, c1, c2, inserted, deleted, changed):
        '''Create the comparison trees.'''
        c = self.c # Always use the visible commander
        assert c == c1
        # Create parent node at the start of the outline.
        u, undoType = c.undoer, 'Compare Two Files'
        u.beforeChangeGroup(c.p, undoType)
        undoData = u.beforeInsertNode(c.p)
        parent = c.p.insertAfter()
        parent.setHeadString(undoType)
        u.afterInsertNode(parent, undoType, undoData, dirtyVnodeList=[])
        # Use the wrapped file name if possible.
        fn1 = g.shortFileName(c1.wrappedFileName) or c1.shortFileName()
        fn2 = g.shortFileName(c2.wrappedFileName) or c2.shortFileName()
        for d, kind in (
            (deleted, 'not in %s' % fn2),
            (inserted, 'not in %s' % fn1),
            (changed, 'changed: as in %s' % fn2),
        ):
            self.createCompareClones(d, kind, parent)
        c.selectPosition(parent)
        u.afterChangeGroup(parent, undoType, reportFlag=True)
        c.redraw()
    #@+node:ekr.20170806094317.12: *5* efc.createCompareClones
    def createCompareClones(self, d, kind, parent):
        if d:
            c = self.c # Use the visible commander.
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
                    for p2 in copy.self_and_subtree():
                        p2.v.context = c
    #@+node:ekr.20170806094317.15: *4* efc.createHiddenCommander
    def createHiddenCommander(self, fn):
        '''Read the file into a hidden commander (Similar to g.openWithFileName).'''
        import leo.core.leoCommands as leoCommands
        lm = g.app.loadManager
        c2 = leoCommands.Commands(fn, gui=g.app.nullGui)
        theFile = lm.openLeoOrZipFile(fn)
        if theFile:
            c2.fileCommands.openLeoFile(theFile, fn, readAtFileNodesFlag=True, silent=True)
            return c2
        else:
            return None
    #@+node:ekr.20170806094317.17: *4* efc.createFileDict
    def createFileDict(self, c):
        '''Create a dictionary of all relevant positions in commander c.'''
        d = {}
        for p in c.all_positions():
            d[p.v.fileIndex] = p.copy()
        return d
    #@+node:ekr.20170806094317.19: *4* efc.dumpCompareNodes
    def dumpCompareNodes(self, fileName1, fileName2, inserted, deleted, changed):
        for d, kind in (
            (inserted, 'inserted (only in %s)' % (fileName1)),
            (deleted, 'deleted  (only in %s)' % (fileName2)),
            (changed, 'changed'),
        ):
            g.pr('\n', kind)
            for key in d:
                p = d.get(key)
                if g.isPython3:
                    g.pr('%-32s %s' % (key, p.h))
                else:
                    g.pr('%-32s %s' % (key, g.toEncodedString(p.h, 'ascii')))
    #@+node:ekr.20170806094319.3: *3* efc.compareTrees
    def compareTrees(self, p1, p2, tag):

        class CompareTreesController:
            #@+others
            #@+node:ekr.20170806094318.18: *4* ct.compare
            def compare(self, d1, d2, p1, p2, root):
                '''Compare dicts d1 and d2.'''
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
                        p.h = h + '(%s only)' % p1.h
                        p1.clone().moveToLastChildOf(p)
                for h in sorted(d2.keys()):
                    p2 = d2.get(h)
                    if h not in d1 and p2.b.strip():
                        # Only in p2 tree, and not an organizer node.
                        p = root.insertAsLastChild()
                        p.h = h + '(%s only)' % p2.h
                        p2.clone().moveToLastChildOf(p)
                return root
            #@+node:ekr.20170806094318.19: *4* ct.run
            def run(self, c, p1, p2, tag):
                '''Main line.'''
                self.c = c
                root = c.p.insertAfter()
                root.h = tag
                d1 = self.scan(p1)
                d2 = self.scan(p2)
                self.compare(d1, d2, p1, p2, root)
                c.p.contract()
                root.expand()
                c.selectPosition(root)
                c.redraw()
            #@+node:ekr.20170806094319.2: *4* ct.scan
            def scan(self, p1):
                '''
                Create a dict of the methods in p1.
                Keys are headlines, stripped of prefixes.
                Values are copies of positions.
                '''
                d = {} #
                for p in p1.self_and_subtree():
                    h = p.h.strip()
                    i = h.find('.')
                    if i > -1:
                        h = h[i + 1:].strip()
                    if h in d:
                        g.es_print('duplicate', p.h)
                    else:
                        d[h] = p.copy()
                return d
            #@-others

        CompareTreesController().run(self.c, p1, p2, tag)
    #@+node:ekr.20170806094318.1: *3* efc.deleteFile
    @cmd('file-delete')
    def deleteFile(self, event):
        '''Prompt for the name of a file and delete it.'''
        k = self.c.k
        k.setLabelBlue('Delete File: ')
        k.extendLabel(os.getcwd() + os.sep)
        k.get1Arg(event, handler=self.deleteFile1)

    def deleteFile1(self, event):
        k = self.c.k
        k.keyboardQuit()
        k.clearState()
        try:
            os.remove(k.arg)
            k.setStatusLabel('Deleted: %s' % k.arg)
        except Exception:
            k.setStatusLabel('Not Deleted: %s' % k.arg)
    #@+node:ekr.20170806094318.3: *3* efc.diff
    @cmd('file-diff-files')
    def diff(self, event=None):
        '''Creates a node and puts the diff between 2 files into it.'''
        c = self.c
        fn = self.getReadableTextFile()
        if not fn: return
        fn2 = self.getReadableTextFile()
        if not fn2: return
        s1, e = g.readFileIntoString(fn)
        if s1 is None: return
        s2, e = g.readFileIntoString(fn2)
        if s2 is None: return
        lines1, lines2 = g.splitLines(s1), g.splitLines(s2)
        aList = difflib.ndiff(lines1, lines2)
        p = c.p.insertAfter()
        p.h = 'diff'
        p.b = ''.join(aList)
        c.redraw()
    #@+node:ekr.20170806094318.6: *3* efc.getReadableTextFile
    def getReadableTextFile(self):
        '''Prompt for a text file.'''
        c = self.c
        fn = g.app.gui.runOpenFileDialog(c,
            title='Open Text File',
            filetypes=[("Text", "*.txt"), ("All files", "*")],
            defaultextension=".txt")
        return fn
    #@+node:ekr.20170819035801.90: *3* efc.gitDiff
    @cmd('git-diff')
    @cmd('gd')
    def gitDiff(self, event):

        GitDiffController(self.c, 'HEAD').run()
    #@+node:ekr.20170806094318.7: *3* efc.insertFile
    @cmd('file-insert')
    def insertFile(self, event):
        '''Prompt for the name of a file and put the selected text into it.'''
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
    def makeDirectory(self, event):
        '''Prompt for the name of a directory and create it.'''
        k = self.c.k
        k.setLabelBlue('Make Directory: ')
        k.extendLabel(os.getcwd() + os.sep)
        k.get1Arg(event, handler=self.makeDirectory1)

    def makeDirectory1(self, event):
        k = self.c.k
        k.keyboardQuit()
        k.clearState()
        try:
            os.mkdir(k.arg)
            k.setStatusLabel("Created: %s" % k.arg)
        except Exception:
            k.setStatusLabel("Not Created: %s" % k.arg)
    #@+node:ekr.20170806094318.12: *3* efc.openOutlineByName
    @cmd('file-open-by-name')
    def openOutlineByName(self, event):
        '''file-open-by-name: Prompt for the name of a Leo outline and open it.'''
        c, k = self.c, self.c.k
        fileName = ''.join(k.givenArgs)
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if fileName and g.os_path_exists(fileName):
            g.openWithFileName(fileName, old_c=c)
        else:
            k.setLabelBlue('Open Leo Outline: ')
            k.getFileName(event, callback=self.openOutlineByNameFinisher)

    def openOutlineByNameFinisher(self, fn):
        c = self.c
        if fn and g.os_path_exists(fn) and not g.os_path_isdir(fn):
            c2 = g.openWithFileName(fn, old_c=c)
            try:
                g.app.gui.runAtIdle(c2.treeWantsFocusNow)
            except Exception:
                pass
        else:
            g.es('ignoring: %s' % fn)
    #@+node:ekr.20170806094318.14: *3* efc.removeDirectory
    @cmd('directory-remove')
    def removeDirectory(self, event):
        '''Prompt for the name of a directory and delete it.'''
        k = self.c.k
        k.setLabelBlue('Remove Directory: ')
        k.extendLabel(os.getcwd() + os.sep)
        k.get1Arg(event, handler=self.removeDirectory1)

    def removeDirectory1(self, event):
        k = self.c.k
        k.keyboardQuit()
        k.clearState()
        try:
            os.rmdir(k.arg)
            k.setStatusLabel('Removed: %s' % k.arg)
        except Exception:
            k.setStatusLabel('Not Removed: %s' % k.arg)
    #@+node:ekr.20170806094318.15: *3* efc.saveFile
    @cmd('file-save')
    def saveFile(self, event):
        '''Prompt for the name of a file and put the body text of the selected node into it..'''
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile=None,
            title='save-file',
            filetypes=[("Text", "*.txt"), ("All files", "*")],
            defaultextension=".txt")
        if fileName:
            try:
                f = open(fileName, 'w')
                s = w.getAllText()
                if not g.isPython3: # 2010/08/27
                    s = g.toEncodedString(s, encoding='utf-8', reportErrors=True)
                f.write(s)
                f.close()
            except IOError:
                g.es('can not create', fileName)
    #@+node:ekr.20170806094319.15: *3* efc.toggleAtAutoAtEdit & helpers
    @cmd('toggle-at-auto-at-edit')
    def toggleAtAutoAtEdit(self, event):
        '''Toggle between @auto and @edit, preserving insert point, etc.'''
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
    def toAtAuto(self, p):
        '''Convert p from @edit to @auto.'''
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
        c.gotoCommands.find_file_line(row+1)
        p.setDirty()
        c.setChanged()
        c.redraw()
        c.bodyWantsFocus()
    #@+node:ekr.20170806094319.19: *4* efc.toAtEdit
    def toAtEdit(self, p):
        '''Convert p from @auto to @edit.'''
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
        for p2 in p.self_and_subtree():
            if p2 == c.p:
                break
            lines = [z for z in g.splitLines(p2.b) if not g.isDirective(z)]
            row += len(lines)
        # Reload the file into a single node.
        c.selectPosition(p)
        c.refreshFromDisk()
        # Restore the line in the proper node.
        ins = g.convertRowColToPythonIndex(p.b, row+1, 0)
        w.setInsertPoint(ins)
        p.setDirty()
        c.setChanged()
        c.redraw()
        c.bodyWantsFocus()
    #@-others
#@+node:ekr.20170806094320.13: ** class GitDiffController
class GitDiffController:
    '''A class to do git diffs.'''
    #@+others
    #@+node:ekr.20170806094320.4: *3* gdc.__init__ & helper
    def __init__ (self, c, rev1=None, rev2=None):
        '''Ctor for the GitDiffController class.'''
        self.c = c
        self.file_node = None
        self.old_dir = g.os_path_abspath('.')
        self.repo_dir = self.find_git_working_directory()
        self.rev1 = rev1
        self.rev2 = rev2
        self.root = None
    #@+node:ekr.20170806094321.3: *4* gdc.find_git_working_directory
    def find_git_working_directory(self):
        '''Return the git working directory.'''
        path = g.os_path_abspath('.')
        while path:
            if g.os_path_exists(g.os_path_finalize_join(path, '.git')):
                return path
            path = g.os_path_finalize_join(path, '..')
        return None
    #@+node:ekr.20170806094320.6: *3* gdc.diff_file & helpers
    def diff_file(self, fn):
        '''Create an outline describing the git diffs for fn.'''
        c = self.c
        s1 = self.get_file_from_rev(self.rev1, fn)
        s2 = self.get_file_from_rev(self.rev2, fn)
        lines1 = g.splitLines(s1)
        lines2 = g.splitLines(s2)
        diff_list = list(difflib.unified_diff(
            lines1,
            lines2,
            self.rev1 or 'uncommitted',
            self.rev2 or 'uncommitted',
        ))
        diff_list.insert(0, '@language patch\n')
        self.file_node = self.create_file_node(diff_list, fn)
        if c.looksLikeDerivedFile(fn):
            c1 = self.make_at_file_outline(fn, s1, self.rev1)
            c2 = self.make_at_file_outline(fn, s2, self.rev2)
        else:
            root = self.find_file(fn)
            if root:
                c1 = self.make_at_clean_outline(fn, root, s1, self.rev1)
                c2 = self.make_at_clean_outline(fn, root, s2, self.rev2)
            else:
                # This warning is silly.
                # g.es_print('No outline for', fn)
                c1 = c2 = None
        if c1 and c2:
            self.make_diff_outlines(fn, c1, c2)
            self.file_node.b = '%s\n@language %s\n' % (
                self.file_node.b.rstrip(), c2.target_language)
    #@+node:ekr.20170806191707.1: *4* gdc.compute_dicts
    def compute_dicts(self, c1, c2):
        '''Compute inserted, deleted, changed dictionaries.'''
        # Special case the root: only compare the body text.
        c1.rootPosition().v.h = c2.rootPosition().v.h
        d1 = {v.fileIndex: v for v in c1.all_unique_nodes()} 
        d2 = {v.fileIndex: v for v in c2.all_unique_nodes()}
        added   = {key: d2.get(key) for key in d2 if not d1.get(key)}
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
    #@+node:ekr.20170806191942.2: *4* gdc.create_compare_node
    def create_compare_node(self, c1, c2, d, kind):
        '''Create nodes describing the changes.'''
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
                    self.rev1 or 'uncommitted',
                    self.rev2 or 'uncommitted',
                ))
                if ''.join(body).strip():
                    body.insert(0, '@language patch\n')
                    body.append('@language %s\n' % (c2.target_language))
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
                if p_in_c: # Make a clone, if possible.
                    p3 = p_in_c.clone()
                    p3.moveToLastChildOf(organizer)
                else:
                    p3 = organizer.insertAsLastChild()
                    p3.h = 'New:' + v2.h
                    p3.b = v2.b
            else:
                v = d.get(key)
                p = parent.insertAsLastChild()
                p.h = v.h
                p.b = v.b
    #@+node:ekr.20170806094321.1: *4* gdc.create_file_node
    def create_file_node(self, diff_list, fn):
        '''Create an organizer node for the file.'''
        p = self.root.insertAsLastChild()
        p.h = fn.strip()
        p.b = ''.join(diff_list)
        return p
    #@+node:ekr.20170806094320.7: *4* gdc.find_file
    def find_file(self, fn):
        '''Return the @<file> node matching fn.'''
        c = self.c
        fn = g.os_path_basename(fn)
        for p in c.all_unique_positions():
            if p.isAnyAtFileNode():
                fn2 = p.anyAtFileNodeName()
                if fn2.endswith(fn):
                    return p
        return None
    #@+node:ekr.20170806094320.15: *4* gdc.get_file_from_rev
    def get_file_from_rev(self, rev, fn):
        '''Get the file from the given rev, or the working directory if None.'''
        if rev:
            # Get the file using git.
            command = 'git show %s:%s' % (rev, fn)
            lines = g.execGitCommand(command, self.repo_dir)
            s = ''.join(lines)
        else:
            # Get the file from the working directory.
            path = g.os_path_finalize_join(self.repo_dir, fn)
            if g.os_path_exists(path):
                try:
                    with open(path, 'rb') as f: # Was 'r'
                        s = f.read()
                except Exception:
                    g.es_print('Can not read', path)
                    g.es_exception()
                    s = ''
            else:
                g.trace('not found:', path)
                s = ''
        return g.toUnicode(s).replace('\r','')
    #@+node:ekr.20170806094321.7: *4* gdc.make_at_file_outline
    def make_at_file_outline(self, fn, s, rev):
        '''Create a hidden temp outline from lines.'''
        # A specialized version of atFileCommands.read.
        hidden_c = leoCommands.Commands(fn, gui=g.app.nullGui)
        at = hidden_c.atFileCommands
        hidden_c.frame.createFirstTreeNode()
        root = hidden_c.rootPosition()
        root.h = fn + ':' + rev if rev else fn
        at.initReadIvars(root, fn, importFileName=None, atShadow=None)
        at.fromString = s
        if at.errors > 0:
            g.trace('***** errors')
            return None
        at.inputFile = g.FileLikeObject(fromString=at.fromString)
        at.initReadLine(at.fromString)
        at.readOpenFile(root, fn, deleteNodes=True)
        at.inputFile.close()
        # Complete the read.
        for p in root.self_and_subtree():
            p.b = ''.join(getattr(p.v, 'tempBodyList', []))
        at.scanAllDirectives(root, importing=False, reading=True)
        return hidden_c
    #@+node:ekr.20170806125535.1: *4* gdc.make_diff_outlines
    def make_diff_outlines(self, fn, c1, c2):
        '''Create an outline-oriented diff from the *hidden* outlines c1 and c2.'''
        added, deleted, changed = self.compute_dicts(c1, c2)
        table = (
            (added, 'Added'),
            (deleted, 'Deleted'),
            (changed, 'Changed'))
        for d, kind in table:
            self.create_compare_node(c1, c2, d, kind)
    #@+node:ekr.20170819132219.1: *4* gdc.find_gnx
    def find_gnx(self, c, gnx):
        '''Return a position in c having the given gnx.'''
        for p in c.all_unique_positions():
            if p.v.fileIndex == gnx:
                return p
        return None
    #@+node:ekr.20170821052348.1: *4* gdc.get_revno
    def get_revno(self, revspec, abbreviated=True):
        '''Return the abbreviated hash the given revision spec.'''
        if revspec:
            # Return only the abbreviated hash for the revspec.
            command = 'git show --format=%%%s --no-patch %s' % (
                'h' if abbreviated else 'H',
                revspec)
            lines = g.execGitCommand(command, self.repo_dir)
            return ''.join(lines).strip()
        else:
            return 'uncommitted'
    #@+node:ekr.20170820084258.1: *4* gdc.make_at_clean_outline
    def make_at_clean_outline(self, fn, root, s, rev):
        '''
        Create a hidden temp outline from lines without sentinels.
        root is the @<file> node for fn.
        s is the contents of the (public) file, without sentinels.
        '''
        # A specialized version of at.readOneAtCleanNode.
        trace = False and not g.unitTesting
        hidden_c = leoCommands.Commands(fn, gui=g.app.nullGui)
        at = hidden_c.atFileCommands
        x = hidden_c.shadowController
        hidden_c.frame.createFirstTreeNode()
        hidden_root = hidden_c.rootPosition()
        # copy root to hidden root, including gnxs.
        root.copyTreeFromSelfTo(hidden_root, copyGnxs=True)
        hidden_root.h = fn + ':' + rev if rev else fn
        # Set at.encoding first.
        at.initReadIvars(hidden_root, fn)
            # Must be called before at.scanAllDirectives.
        at.scanAllDirectives(hidden_root)
            # Sets at.startSentinelComment/endSentinelComment.
        new_public_lines = g.splitLines(s)
        old_private_lines = at.write_at_clean_sentinels(hidden_root)
        marker = x.markerFromFileLines(old_private_lines, fn)
        old_public_lines, junk = x.separate_sentinels(old_private_lines, marker)
        assert old_public_lines
        new_private_lines = x.propagate_changed_lines(
            new_public_lines, old_private_lines, marker, p=hidden_root)
        # Init the input stream used by read-open file.
        at.read_lines = new_private_lines
        at.read_ptr = 0
        # Read the file using the @file read logic.
        at.readOpenFile(hidden_root, fn, deleteNodes=True)
        # Complete the read.
        for p in hidden_root.self_and_subtree():
            p.b = ''.join(getattr(p.v, 'tempBodyList', []))
        if at.errors: g.trace(at.errors, 'errors!')
        if trace: g.trace(len(s), rev, fn, hidden_c)
        return None if at.errors else hidden_c
    #@+node:ekr.20170806094320.12: *3* gdc.run & helpers
    def run(self):
        '''The main line of the git diff command.'''
        if self.repo_dir:
            # 1. Diff the given revs.
            ok = self.diff_revs()
            # Go back several revs...
            n1, n2 = 1, 0
            while not ok and n1 <= 5:
                # 2. Diff HEAD@{0} HEAD@{1}
                self.rev1 = 'HEAD@{%s}' % (n1)
                self.rev2 = 'HEAD@{%s}' % (n2)
                ok = self.diff_revs()
                n1, n2 = n1+1, n2+1
            if not ok:
                g.es_print('no changed readable files from HEAD@{1}..HEAD@(5)')
        else:
            g.es_print('no git repo found in', g.os_path_abspath('.'))
    #@+node:ekr.20170806094320.18: *4* gdc.create_root
    def create_root(self):
        '''Create the top-level organizer node describing the git diff.'''
        c = self.c
        r1, r2 = self.rev1 or '', self.rev2 or ''
        p = c.lastTopLevel().insertAfter()
        p.h = 'git diff %s %s' % (r1, r2)
        if r1 and r2:
            p.b = '%s=%s\n%s=%s' % (
                r1, self.get_revno(r1),
                r2, self.get_revno(r2),
            )
        else:
            p.b = '%s=%s' % (r1, self.get_revno(r1))
        return p
    #@+node:ekr.20170806094321.5: *4* gdc.finish
    def finish(self):
        '''Finish execution of this command.'''
        c = self.c
        os.chdir(self.old_dir)
        c.contractAllHeadlines(redrawFlag=False)
        self.root.expand()
        c.selectPosition(self.root)
        c.redraw()
    #@+node:ekr.20170806094320.9: *4* gdc.get_files
    def get_files(self):
        '''Return a list of changed files.'''
        
        trace = False and not g.unitTesting
            
        def readable(fn):
            for suffix in ('commit_timestamp.json', '.db', '.leo', '.zip', ):
                if fn.strip().endswith(suffix):
                    return False
            return True

        command = 'git diff --name-only %s %s' % (self.rev1 or '', self.rev2 or '')
        files = [
            z.strip() for z in g.execGitCommand(command, self.repo_dir)
                if readable(z)
        ]
        if trace:
            g.trace(command)
            g.printList(files)
        return files
    #@+node:ekr.20170820082125.1: *4* gdc.diff_revs
    def diff_revs(self):
        '''Diff all files given by self.rev1 and self.rev2.'''
        files = self.get_files()
        if files:
            self.root = self.create_root()
            for fn in files:
                self.diff_file(fn)
            self.finish()
        return bool(files)
        
    #@-others
#@-others
#@-leo

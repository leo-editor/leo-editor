# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514041209.1: * @file ../commands/editFileCommands.py
#@@first
'''Leo's file-editing commands.'''
#@+<< imports >>
#@+node:ekr.20150514050328.1: ** << imports >> (editFileCommands.py)
import difflib
import os
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    '''Command decorator for the EditFileCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'editFileCommands',])

#@+others
#@+node:ekr.20160514121150.1: ** class EditFileCommandsClass
class EditFileCommandsClass(BaseEditCommandsClass):
    '''A class to load files into buffers and save buffers to files.'''
    #@+others
    #@+node:ekr.20160417180751.1: *3* efc.clean-at-clean commands
    #@+node:ekr.20160417131017.1: *4* efc.cleanAtCleanFiles
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
    #@+node:ekr.20160417131341.1: *4* efc.cleanAtCleanNode
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
    #@+node:ekr.20160417133509.1: *4* efc.cleanAtCleanTree
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
    #@+node:ekr.20150514063305.356: *3* efc.compareAnyTwoFiles & helpers
    @cmd('file-compare-leo-files')
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
    #@+node:ekr.20150514063305.357: *4* efc.computeChangeDicts
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
    #@+node:ekr.20150514063305.358: *4* efc.createAllCompareClones & helper
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
    #@+node:ekr.20150514063305.359: *5* efc.createCompareClones
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
    #@+node:ekr.20150514063305.360: *4* efc.createHiddenCommander
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
    #@+node:ekr.20150514063305.361: *4* efc.createFileDict
    def createFileDict(self, c):
        '''Create a dictionary of all relevant positions in commander c.'''
        d = {}
        for p in c.all_positions():
            d[p.v.fileIndex] = p.copy()
        return d
    #@+node:ekr.20150514063305.362: *4* efc.dumpCompareNodes
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
    #@+node:ekr.20150722080425.1: *3* efc.compareTrees
    def compareTrees(self, p1, p2, tag):

        class Controller:
            #@+others
            #@+node:ekr.20150722080308.2: *4* ct.compare
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
            #@+node:ekr.20150722080308.3: *4* ct.run
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
            #@+node:ekr.20150722080308.4: *4* ct.scan
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

        Controller().run(self.c, p1, p2, tag)
    #@+node:ekr.20150514063305.363: *3* efc.deleteFile
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
    #@+node:ekr.20150514063305.364: *3* efc.diff
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
    #@+node:ekr.20150514063305.365: *3* efc.getReadableTextFile
    def getReadableTextFile(self):
        '''Prompt for a text file.'''
        c = self.c
        fn = g.app.gui.runOpenFileDialog(c,
            title='Open Text File',
            filetypes=[("Text", "*.txt"), ("All files", "*")],
            defaultextension=".txt")
        return fn
    #@+node:ekr.20150514063305.366: *3* efc.insertFile
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
    #@+node:ekr.20150514063305.367: *3* efc.makeDirectory
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
    #@+node:ekr.20150514063305.368: *3* efc.openOutlineByName
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
    #@+node:ekr.20150514063305.369: *3* efc.removeDirectory
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
    #@+node:ekr.20150514063305.370: *3* efc.saveFile
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
    #@+node:ekr.20170617152615.1: *3* efc.toggleAtAutoAtEdit & helpers
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
    #@+node:ekr.20170617153619.1: *4* efc.toAtAuto
    def toAtAuto(self, p):
        '''Convert p from @edit to @auto.'''
        c = self.c
        p.h = '@auto' + p.h[5:]
        c.selectPosition(p, enableRedrawFlag=False)
        c.refreshFromDisk()
    #@+node:ekr.20170617153628.1: *4* efc.toAtEdit
    def toAtEdit(self, p):
        '''Convert p from @auto to @edit.'''
        c = self.c
        p.h = '@edit' + p.h[5:]
        c.selectPosition(p, enableRedrawFlag=False)
        c.refreshFromDisk()
    #@-others
#@-others
#@-leo

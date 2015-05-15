# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514041209.1: * @file ../commands/editFileCommands.py
#@@first
'''Leo's file-editing commands.'''
#@+<< imports >>
#@+node:ekr.20150514050328.1: ** << imports >> (editFileCommands.py)
import leo.core.leoGlobals as g

from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass

import difflib
import os
#@-<< imports >>

def cmd(name):
    '''Command decorator for the EditFileCommandsClass class.'''
    return g.new_cmd_decorator(name,['c','editFileCommands',])

class EditFileCommandsClass (BaseEditCommandsClass):
    '''A class to load files into buffers and save buffers to files.'''
    #@+others
    #@+node:ekr.20150514063305.356: ** compareAnyTwoFiles & helpers
    @cmd('file-compare-leo-files')
    def compareAnyTwoFiles (self,event):
        '''Compare two files.'''
        trace = False and not g.unitTesting
        c = c1 = self.c
        w = c.frame.body.wrapper
        commanders = g.app.commanders()
        if g.app.diff:
            if len(commanders) == 2:
                c1,c2 = commanders
                fn1 = g.shortFileName(c1.wrappedFileName) or c1.shortFileName()
                fn2 = g.shortFileName(c2.wrappedFileName) or c2.shortFileName()
                g.es('--diff auto compare',color='red')
                g.es(fn1)
                g.es(fn2)
            else:
                g.es('expecting two .leo files')
                return
        else:
            # Prompt for the file to be compared with the present outline.
            filetypes = [("Leo files", "*.leo"),("All files", "*"),]
            fileName = g.app.gui.runOpenFileDialog(c,
                title="Compare .leo Files",filetypes=filetypes,defaultextension='.leo')
            if not fileName: return
            # Read the file into the hidden commander.
            c2 = self.createHiddenCommander(fileName)
            if not c2: return
        # Compute the inserted, deleted and changed dicts.
        d1 = self.createFileDict(c1)
        d2 = self.createFileDict(c2)  
        inserted, deleted, changed = self.computeChangeDicts(d1,d2)
        if trace: self.dumpCompareNodes(fileName,c1.mFileName,inserted,deleted,changed)
        # Create clones of all inserted, deleted and changed dicts.
        self.createAllCompareClones(c1,c2,inserted,deleted,changed)
        # Fix bug 1231656: File-Compare-Leo-Files leaves other file open-count incremented.
        if not g.app.diff:
            g.app.forgetOpenFile(fn=c2.fileName(),force=True)
            c2.frame.destroySelf()
            g.app.gui.set_focus(c,w)
    #@+node:ekr.20150514063305.357: *3* computeChangeDicts
    def computeChangeDicts (self,d1,d2):

        '''Compute inserted, deleted, changed dictionaries.
        
        New in Leo 4.11: show the nodes in the *invisible* file, d2, if possible.'''

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
    #@+node:ekr.20150514063305.358: *3* createAllCompareClones & helper
    def createAllCompareClones(self,c1,c2,inserted,deleted,changed):
        '''Create the comparison trees.'''
        c = self.c # Always use the visible commander
        assert c == c1
        # Create parent node at the start of the outline.
        u,undoType = c.undoer,'Compare Two Files'
        u.beforeChangeGroup(c.p,undoType)
        undoData = u.beforeInsertNode(c.p)
        parent = c.p.insertAfter()
        parent.setHeadString(undoType)
        u.afterInsertNode(parent,undoType,undoData,dirtyVnodeList=[])
        # Use the wrapped file name if possible.
        fn1 = g.shortFileName(c1.wrappedFileName) or c1.shortFileName()
        fn2 = g.shortFileName(c2.wrappedFileName) or c2.shortFileName()
        for d,kind in (
            (deleted,'not in %s' % fn2),
            (inserted,'not in %s' % fn1),
            (changed,'changed: as in %s' % fn2),
        ):
            self.createCompareClones(d,kind,parent)
        c.selectPosition(parent)
        u.afterChangeGroup(parent,undoType,reportFlag=True) 
        c.redraw()
    #@+node:ekr.20150514063305.359: *4* createCompareClones
    def createCompareClones (self,d,kind,parent):

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
    #@+node:ekr.20150514063305.360: *3* createHiddenCommander (EditFileCommandsClass)
    def createHiddenCommander(self,fn):
        '''Read the file into a hidden commander (Similar to g.openWithFileName).'''
        import leo.core.leoCommands as leoCommands
        lm = g.app.loadManager
        c2 = leoCommands.Commands(fn,gui=g.app.nullGui)
        theFile = lm.openLeoOrZipFile(fn)
        if theFile:
            c2.fileCommands.openLeoFile(theFile,fn,readAtFileNodesFlag=True,silent=True)
            return c2
        else:
            return None
    #@+node:ekr.20150514063305.361: *3* createFileDict
    def createFileDict (self,c):
        '''Create a dictionary of all relevant positions in commander c.'''
        d = {}
        for p in c.all_positions():
            d[p.v.fileIndex] = p.copy()
        return d
    #@+node:ekr.20150514063305.362: *3* dumpCompareNodes
    def dumpCompareNodes (self,fileName1,fileName2,inserted,deleted,changed):

        for d,kind in (
            (inserted,'inserted (only in %s)' % (fileName1)),
            (deleted, 'deleted  (only in %s)' % (fileName2)),
            (changed, 'changed'),
        ):
            g.pr('\n',kind)
            for key in d:
                p = d.get(key)
                if g.isPython3:
                    g.pr('%-32s %s' % (key,p.h))
                else:
                    g.pr('%-32s %s' % (key,g.toEncodedString(p.h,'ascii')))
    #@+node:ekr.20150514063305.363: ** deleteFile
    @cmd('file-delete')
    def deleteFile (self,event):

        '''Prompt for the name of a file and delete it.'''

        k = self.c.k ; state = k.getState('delete_file')

        if state == 0:
            k.setLabelBlue('Delete File: ')
            k.extendLabel(os.getcwd() + os.sep)
            k.getArg(event,'delete_file',1,self.deleteFile)
        else:
            k.keyboardQuit()
            k.clearState()
            try:
                os.remove(k.arg)
                k.setStatusLabel('Deleted: %s' % k.arg)
            except Exception:
                k.setStatusLabel('Not Deleted: %s' % k.arg)
    #@+node:ekr.20150514063305.364: ** diff
    @cmd('file-diff-files')
    def diff (self,event):

        '''Creates a node and puts the diff between 2 files into it.'''

        w = self.editWidget(event)
        if not w: return
        fn = self.getReadableTextFile()
        if not fn: return
        fn2 = self.getReadableTextFile()
        if not fn2: return
        s1,e = g.readFileIntoString(fn)
        if s1 is None: return
        s2,e = g.readFileIntoString(fn2)
        if s2 is None: return

        # self.switchToBuffer(event,"*diff* of ( %s , %s )" % (name,name2))
        data = difflib.ndiff(s1,s2)
        idata = []
        for z in data:
            idata.append(z)
        w.delete(0,'end')
        w.insert(0,''.join(idata))
    #@+node:ekr.20150514063305.365: ** getReadableTextFile (EditFileCommandsClass)
    def getReadableTextFile (self):
        '''Prompt for a text file.'''
        c = self.c
        fn = g.app.gui.runOpenFileDialog(c,
            title = 'Open Text File',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")
        return fn
    #@+node:ekr.20150514063305.366: ** insertFile
    @cmd('file-insert')
    def insertFile (self,event):

        '''Prompt for the name of a file and put the selected text into it.'''

        w = self.editWidget(event)
        if not w: return

        fn = self.getReadableTextFile()
        if not fn: return

        s,e = g.readFileIntoString(fn)
        if s is None: return

        self.beginCommand(undoType='insert-file')
        i = w.getInsertPoint()
        w.insert(i,s)
        w.seeInsertPoint()
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20150514063305.367: ** makeDirectory
    @cmd('directory-make')
    def makeDirectory (self,event):
        '''Prompt for the name of a directory and create it.'''
        k = self.c.k
        state = k.getState('make_directory')
        if state == 0:
            k.setLabelBlue('Make Directory: ')
            k.extendLabel(os.getcwd() + os.sep)
            k.getArg(event,'make_directory',1,self.makeDirectory)
        else:
            k.keyboardQuit()
            k.clearState()
            try:
                os.mkdir(k.arg)
                k.setStatusLabel("Created: %s" % k.arg)
            except Exception:
                k.setStatusLabel("Not Create: %s" % k.arg)
    #@+node:ekr.20150514063305.368: ** openOutlineByName (EditFileCommandsClass)
    @cmd('file-open-by-name')
    def openOutlineByName (self,event):
        '''file-open-by-name: Prompt for the name of a Leo outline and open it.'''
        c,k = self.c,self.c.k
        fileName = ''.join(k.givenArgs)
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if fileName and g.os_path_exists(fileName):
            g.openWithFileName(fileName,old_c=c)
        else:
            k.setLabelBlue('Open Leo Outline: ')
            k.getFileName(event,callback=self.openOutlineByNameFinisher)

    def openOutlineByNameFinisher (self,fn):
        c = self.c
        if fn and g.os_path_exists(fn) and not g.os_path_isdir(fn):
            c2 = g.openWithFileName(fn,old_c=c)
            try:
                g.app.gui.runAtIdle(c2.treeWantsFocusNow)
            except Exception:
                pass
        else:
            g.es('ignoring: %s' % fn)
    #@+node:ekr.20150514063305.369: ** removeDirectory
    @cmd('directory-remove')
    def removeDirectory (self,event):

        '''Prompt for the name of a directory and delete it.'''

        k = self.c.k ; state = k.getState('remove_directory')

        if state == 0:
            k.setLabelBlue('Remove Directory: ')
            k.extendLabel(os.getcwd() + os.sep)
            k.getArg(event,'remove_directory',1,self.removeDirectory)
        else:
            k.keyboardQuit()
            k.clearState()
            try:
                os.rmdir(k.arg)
                k.setStatusLabel('Removed: %s' % k.arg)
            except Exception:
                k.setStatusLabel('Not Removed: %s' % k.arg)
    #@+node:ekr.20150514063305.370: ** saveFile
    @cmd('file-save')
    def saveFile (self,event):
        '''Prompt for the name of a file and put the body text of the selected node into it..'''
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile = None,
            title='save-file',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")
        if fileName:
            try:
                f = open(fileName,'w')
                s = w.getAllText()
                if not g.isPython3: # 2010/08/27
                    s = g.toEncodedString(s,encoding='utf-8',reportErrors=True)
                f.write(s)
                f.close()
            except IOError:
                g.es('can not create',fileName)
    #@-others

#@-leo

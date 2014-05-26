# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140524144107.15803: * @file leoRope.py
#@@first
#@+<< leoRope imports >>
#@+node:ekr.20140525065558.15807: ** << leoRope imports >>
import leo.core.leoGlobals as g
import rope.base.project as project
# import rope.refactor.rename
import rope.refactor as refactor
import glob
#@-<< leoRope imports >>
class RopeController:
    #@+others
    #@+node:ekr.20140525065558.15809: ** ctor
    def __init__(self,c):
        self.c = c
        self.proj = project.Project(g.app.loadDir)
    #@+node:ekr.20140525065558.15806: ** modules
    def modules(self):
        '''Return full path names of all Leo modules.'''
        aList = glob.glob(g.os_path_join(g.app.loadDir,'*.py'))
        return sorted(aList)
    #@+node:ekr.20140525065558.15808: ** path
    def path(self,fn):
        return g.os_path_join(g.app.loadDir,fn)
    #@+node:ekr.20140525065558.15805: ** refactor
    def refactor(self):
        '''Perform refactorings.'''
        # atFile -> AtFile
        proj = self.proj
        m = proj.get_resource(self.path('leoAtFile.py'))
        s = m.read()
        tag1 = 'atFile'
        tag2 = self.pep8_class_name(tag1)
        g.trace(tag1,'to',tag2)
        # Find an offset that is not in a comment line.
        i = 0
        while i < len(s):
            progress = i
            # g.trace(m,len(s),s.find('\r'))
            offset = s.find(tag1,i)
            if offset == -1:
                break
            j1,j2 = g.getLine(s,offset)
            if s[j1:j2].strip().startswith('#'):
                i = j2
            else:
                break
            assert progress < i
        if offset > -1:
            changes = refactor.rename.Rename(proj,m,offset+1).get_changes(tag2)
            g.trace(changes.get_description())
        else:
            g.trace('not found',tag)
        # prog.do(changes)
    #@+node:ekr.20140525065558.15812: ** pep8_class_name
    def pep8_class_name(self,s):
        '''Return the proper class name for s.'''
        assert s
        if s[0].islower():
            s = s[0].upper()+s[1:]
        return s
    #@+node:ekr.20140525065558.15810: ** run
    def run(self):
        '''run the refactorings.'''
        proj = self.proj
        proj.validate(proj.root)
        self.refactor()
        proj.close()
    #@-others
#@-leo

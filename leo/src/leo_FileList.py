#@+leo-ver=4-thin
#@+node:ekr.20060516173523:@thin leo_FileList.py
#@@language python
#@@tabwidth -4

import leoGlobals as g

import os
# from Tkinter import *
# import tkMessageBox

#@+others
#@+node:ekr.20060516173523.2:class FileList
class FileList:
    
    '''Maintain a list of open files being handled by the IDE.
    
    For Leo, this probably should be all @file nodes.'''
    
    
    if 0:
	    from EditorWindow import EditorWindow
            # class variable, may be overridden
            # e.g. by PyShellFileList

    #@	@+others
    #@+node:ekr.20060516173523.4:__init__
    def __init__(self, c): # was root
        
        g.trace('FileList',g.callers())
        
        self.c = c
        self.p = p = c.currentPosition()
        
        if 1:
            if p.isAnyAtFileNode():
                g.trace(p.headString())
                self.open(p)
        else:
            for p in c.allNodes_iter():
                if p.isAnyAtFileNode():
                    g.trace(p.headString())
        
        if 0: # No longer needed.  All the work will be done in g.gotolline.
            self.dict = {}
            self.inversedict = {}
            self.vars = {} # For EditorWindow.getrawvar (shared Tcl variables)
    #@nonl
    #@-node:ekr.20060516173523.4:__init__
    #@+node:ekr.20060516173523.5:open
    def open(self, filename, action=None):
        
        assert filename
        filename = self.canonize(filename)
        if os.path.isdir(filename):
            # This can happen when bad filename is passed on command line.
            return g.es_print('%s is a directory' % (filename),color='red')
            
        key = os.path.normcase(filename)
        g.trace(key)
        return key # EKR
    
        if 0:
            if self.dict.has_key(key):
                edit = self.dict[key]
                edit.top.wakeup()
                return edit
            if action:
                # Don't create window, perform 'action', e.g. open in same window
                return action(filename)
            else:
                return self.EditorWindow(self, filename, key)
    #@nonl
    #@-node:ekr.20060516173523.5:open
    #@+node:ekr.20060516173523.6:gotofileline
    def gotofileline(self, filename, lineno=None):
        
        g.trace(filename,lineno)
        
        if 1: # Leo-centric code.
            filename = self.open(filename)
            if filename:
                g.trace(filename,lineno)
                # g.gotoline(lineno)
            
        else: # IDLE-centric code.
            edit = self.open(filename)
            if edit is not None and lineno is not None:
                edit.gotoline(lineno)
    #@nonl
    #@-node:ekr.20060516173523.6:gotofileline
    #@+node:ekr.20060516173523.7:new
    def new(self, filename=None):
        
        g.trace(filename)
        
        return None
    
        # return self.EditorWindow(self, filename)
    #@-node:ekr.20060516173523.7:new
    #@+node:ekr.20060516173523.8:close_all_callback
    def close_all_callback(self, event):
        
        g.trace()
        
        if 0: # The Leo editor never closes
            for edit in self.inversedict.keys():
                reply = edit.close()
                if reply == "cancel":
                    break
    
        return "break"
    #@nonl
    #@-node:ekr.20060516173523.8:close_all_callback
    #@+node:ekr.20060516173523.9:close_edit
    def close_edit(self, edit):
        
        g.trace(edit)
        
        if 0: # The Leo editor never quits.
            try:
                key = self.inversedict[edit]
            except KeyError:
                print "Don't know this EditorWindow object.  (close)"
                return
            if key:
                del self.dict[key]
            del self.inversedict[edit]
            if not self.inversedict:
                self.root.quit()
    #@nonl
    #@-node:ekr.20060516173523.9:close_edit
    #@+node:ekr.20060516173523.10:filename_changed_edit
    def filename_changed_edit(self, edit):
        
        g.trace(edit)
        
        if 0: # Probably not needed for Leo.
            edit.saved_change_hook()
            try:
                key = self.inversedict[edit]
            except KeyError:
                print "Don't know this EditorWindow object.  (rename)"
                return
            filename = edit.io.filename
            if not filename:
                if key:
                    del self.dict[key]
                self.inversedict[edit] = None
                return
            filename = self.canonize(filename)
            newkey = os.path.normcase(filename)
            if newkey == key:
                return
            if self.dict.has_key(newkey):
                conflict = self.dict[newkey]
                self.inversedict[conflict] = None
                tkMessageBox.showerror(
                    "Name Conflict",
                    "You now have multiple edit windows open for %r" % (filename,),
                    master=self.root)
            self.dict[newkey] = edit
            self.inversedict[edit] = newkey
            if key:
                try:
                    del self.dict[key]
                except KeyError:
                    pass
        
    #@nonl
    #@-node:ekr.20060516173523.10:filename_changed_edit
    #@+node:ekr.20060516173523.11:canonize
    def canonize(self, filename):
    
        if not os.path.isabs(filename):
            try:
                pwd = os.getcwd()
            except os.error:
                pass
            else:
                filename = os.path.join(pwd, filename)
    
        return os.path.normpath(filename)
    #@-node:ekr.20060516173523.11:canonize
    #@-others
#@nonl
#@-node:ekr.20060516173523.2:class FileList
#@+node:ekr.20060516173523.12:_test
def _test():
    
    if 0:
        from EditorWindow import fixwordbreaks
        import sys
        root = Tk()
        
        fixwordbreaks(root)
        root.withdraw()
        flist = FileList(root)
        if sys.argv[1:]:
            for filename in sys.argv[1:]:
                flist.open(filename)
        else:
            flist.new()
        if flist.inversedict:
            root.mainloop()
    
#@nonl
#@-node:ekr.20060516173523.12:_test
#@-others
#@nonl
#@-node:ekr.20060516173523:@thin leo_FileList.py
#@-leo

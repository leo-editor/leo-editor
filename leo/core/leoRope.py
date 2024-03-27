#@+leo-ver=5-thin
#@+node:ekr.20140526082700.18440: * @file leoRope.py
#@+<< leoRope imports >>
#@+node:ekr.20140525065558.15807: ** << leoRope imports >>
import time
import importlib
from leo.core import leoGlobals as g
# Third-party imports.
try:
    import rope.base.project as project
    import rope.base.simplify as simplify
    import rope.refactor as refactor
    has_rope = True
except Exception:
    has_rope = False
if has_rope:
    importlib.reload(project)
    importlib.reload(simplify)
    importlib.reload(refactor)
#@-<< leoRope imports >>
#@+others
#@+node:ekr.20140526123310.17592: ** class RopeController
class RopeController:
    #@+others
    #@+node:ekr.20140525065558.15809: *3* ctor
    def __init__(self, c):
        self.c = c
        if has_rope:
            self.proj = project.Project(g.app.loadDir)
        else:
            self.proj = None
    #@+node:ekr.20140525065558.15806: *3* modules (RopeController)
    def modules(self):
        """Return full path names of all Leo modules."""
        aList = g.glob_glob(g.os_path_join(g.app.loadDir, '*.py'))
        return sorted(aList)
    #@+node:ekr.20140525065558.15808: *3* path
    def path(self, fn):
        return g.os_path_join(g.app.loadDir, fn)
    #@+node:ekr.20140525065558.15805: *3* refactor
    def refactor(self):
        """Perform refactorings."""
        proj = self.proj
        if not proj:
            g.es_print('rope not found')
            return
        m = proj.get_resource(self.path('leoAtFile.py'))
        s = m.read()
        # Important: get an offset in actual code.
        s = simplify.real_code(s)
        tag1 = 'atFile'
        tag2 = g.pep8_class_name(tag1)
        offset = s.find(tag1)
        if offset > -1:
            changes = refactor.rename.Rename(proj, m, offset).get_changes(tag2)
            g.trace(changes.get_description())
        else:
            g.trace('not found', tag1)
        # prog.do(changes)
    #@+node:ekr.20140525065558.15810: *3* run
    def run(self):
        """run the refactorings."""
        proj = self.proj
        if proj:
            proj.validate(proj.root)
            self.refactor()
            proj.close()
        else:
            g.es_print('rope not found')
    #@-others
#@+node:ekr.20140526123310.17593: ** test
def test(c):
    g.cls()
    t1 = time.time()
    RopeController(c).run()
    print(f"done: {g.timeSince(t1)} sec.")
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

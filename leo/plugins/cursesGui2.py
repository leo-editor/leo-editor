#@+leo-ver=5-thin
#@+node:ekr.20170419092835.1: * @file cursesGui2.py
import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui

#@+others
#@+node:ekr.20170419094705.1: ** init (cursesGui2.py)
def init():
    ok = not g.app.gui and not g.app.unitTesting # Not Ok for unit testing!
    if ok:
        g.app.gui = CursesGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
    elif g.app.gui and not g.app.unitTesting:
        s = "Can't install text gui: previous gui installed"
        g.es_print(s, color="red")
    return ok
#@+node:ekr.20170419105852.1: ** class CursesFrame
class CursesFrame:
    
    def __init__ (self, c, title):
        self.c = c
        self.d = {}
        self.title = title
        self.menu = CursesMenu(c)
        
    #@+others
    #@+node:ekr.20170419111214.1: *3* CF.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('CursesFrame.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@+node:ekr.20170419111305.1: *3* CF.getShortCut
    def getShortCut(self, *args, **kwargs):
        return None
    #@-others
    
#@+node:ekr.20170419094731.1: ** class CursesGui
class CursesGui(leoGui.LeoGui):
    '''A do-nothing curses gui template.'''

    def __init__(self):
        self.d = {}
            # Keys are names, values of lists of g.callers values.
            
    #@+others
    #@+node:ekr.20170419110330.1: *3* CG.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('CursesGui.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@+node:ekr.20170419110052.1: *3* CG.createLeoFrame
    def createLeoFrame(self, c, title):
        
        return CursesFrame(c, title)
    #@+node:ekr.20170419111744.1: *3* CG.Focus...
    def get_focus(self, *args, **keys):
        return None
    #@-others
#@+node:ekr.20170419111515.1: ** class CursesMenu
class CursesMenu:
    
    def __init__ (self, c):
        self.c = c
        self.d = {}
        
    #@+others
    #@+node:ekr.20170419111555.1: *3* CM.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('CursesMenu.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@-others
#@-others
#@-leo

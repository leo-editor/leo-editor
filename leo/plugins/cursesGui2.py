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
#@+node:ekr.20170419094731.1: ** class CursesGui
class CursesGui(leoGui.LeoGui):
    '''A do-nothing curses gui template.'''

    def __init__(self):
        self.d = {}
            # Keys are names, values of lists of g.callers values.

    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(6)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace(name, callers)
        return g.NullObject()
            # Or just raise AttributeError.
#@-others
#@-leo

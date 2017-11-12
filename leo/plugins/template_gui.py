#@+leo-ver=5-thin
#@+node:ekr.20170419150249.1: * @file template_gui.py
'''An example of a gui plugin that completes startup without doing anything.'''
import sys
import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui
# pylint: disable=arguments-differ
#@+others
#@+node:ekr.20170419150249.2: ** init (template_gui.py)
def init():
    '''The top-level init method for the template_gui plugin.'''
    ok = not g.app.gui and not g.app.unitTesting
        # Not Ok for unit testing!
    if ok:
        g.app.gui = TemplateGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
    elif g.app.gui and not g.app.unitTesting:
        s = "Can't install text gui: previous gui installed"
        g.es_print(s, color="red")
    return ok
#@+node:ekr.20170419150249.3: ** class TemplateFrame
class TemplateFrame:

    def __init__ (self, c, title):
        self.c = c
        self.d = {}
        self.title = title
        self.menu = TemplateMenu(c)

    #@+others
    #@+node:ekr.20170419150249.4: *3* TF.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('TemplateFrame.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@+node:ekr.20170419150249.5: *3* TF.getShortCut
    def getShortCut(self, *args, **kwargs):
        return None
    #@-others

#@+node:ekr.20170419150249.6: ** class TemplateGui
class TemplateGui(leoGui.LeoGui):
    '''A do-nothing gui template.'''

    def __init__(self):

        leoGui.LeoGui.__init__(self, 'curses')
            # Init the base class.
        self.consoleOnly = True # Affects g.es, etc.
        self.d = {}
            # Keys are names, values of lists of g.callers values.

    #@+others
    #@+node:ekr.20170419150249.7: *3* TG.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('TemplateGui.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@+node:ekr.20170419150249.8: *3* TG.createLeoFrame
    def createLeoFrame(self, c, title):

        return TemplateFrame(c, title)
    #@+node:ekr.20170419150249.9: *3* TG.Focus...
    def get_focus(self, *args, **keys):
        return None
    #@+node:ekr.20170419150249.10: *3* TG.runMainLoop
    def runMainLoop(self):
        g.trace(g.callers())
        sys.exit(0)
    #@-others
#@+node:ekr.20170419150249.39: ** class TemplateMenu
class TemplateMenu:

    def __init__ (self, c):
        self.c = c
        self.d = {}

    #@+others
    #@+node:ekr.20170419150249.40: *3* TM.__getattr__
    # https://docs.python.org/2/reference/datamodel.html#object.__getattr__
    def __getattr__(self, name):
        aList = self.d.get(name, [])
        callers = g.callers(4)
        if callers not in aList:
            aList.append(callers)
            self.d[name] = aList
            g.trace('%30s' % ('TemplateMenu.' + name), callers)
        return g.NullObject()
            # Or just raise AttributeError.
    #@-others
#@-others
#@-leo

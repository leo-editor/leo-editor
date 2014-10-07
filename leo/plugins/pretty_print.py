#@+leo-ver=5-thin
#@+node:ekr.20041021120118: * @file pretty_print.py
'''Customizes pretty printing.

The plugin creates a do-nothing subclass of the default pretty printer. To
customize, simply override in this file the methods of the base prettyPrinter
class in leoCommands.py. You would typically want to override putNormalToken or
its allies. Templates for these methods have been provided. You may, however,
override any methods you like. You could even define your own class entirely,
provided you implement the prettyPrintNode method.

'''
import leo.core.leoGlobals as g
import leo.core.leoCommands as leoCommands
#@+others
#@+node:ekr.20100128073941.5378: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not for unit testing:  modifies core.
    if ok:
        leoCommands.Commands.prettyPrinter = MyPrettyPrinter
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20041021120454: ** class MyPrettyPrinter
class MyPrettyPrinter(leoCommands.Commands.PythonPrettyPrinter):

    '''An example subclass of Leo's PrettyPrinter class.

    Not all the base class methods are shown here:
    just the ones you are likely to want to override.'''

    #@+others
    #@+node:ekr.20041021123018: *3* myPrettyPrinter.__init__
    def __init__ (self,c):
        '''Ctor for MyPrettyPrinter class.'''
        leoCommands.Commands.PythonPrettyPrinter.__init__(self,c)
            # Init the base class.
        self.tracing = False
        # g.pr("Overriding class leoCommands.PythonPrettyPrinter")
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

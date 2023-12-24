#@+leo-ver=5-thin
#@+node:ekr.20170428084207.3: * @file ../external/npyscreen/apNPSApplication.py
#!/usr/bin/env python
from leo.core import leoGlobals as g
assert g
#@+others
#@+node:ekr.20170428084207.4: ** Declarations
import curses
# import locale
# import _curses

from . import npyssafewrapper


#@+node:ekr.20170428084207.5: ** class AlreadyOver
class AlreadyOver(Exception):
    pass

#@+node:ekr.20170428084207.6: ** class NPSApp
class NPSApp:
    _run_called = 0
    #@+others
    #@+node:ekr.20170428084207.7: *3* main
    def main(self):
        """Overload this method to create your application"""

    #@+node:ekr.20170428084207.8: *3* resize
    def resize(self):
        pass

    #@+node:ekr.20170428084207.9: *3* __remove_argument_call_main
    def __remove_argument_call_main(self, screen, enable_mouse=True):
        # screen discarded.
        if enable_mouse:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
        del screen
        return self.main()

    #@+node:ekr.20170428084207.10: *3* NPS.run
    def run(self, fork=None):
        """Run application.  Calls Mainloop wrapped properly."""
        # g.trace('===== (NPS) fork:', repr(fork))
        if fork is None:
            return npyssafewrapper.wrapper(self.__remove_argument_call_main)
        else:
            return npyssafewrapper.wrapper(self.__remove_argument_call_main, fork=fork)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

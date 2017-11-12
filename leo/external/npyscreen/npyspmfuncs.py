#@+leo-ver=5-thin
#@+node:ekr.20170428084207.364: * @file ../external/npyscreen/npyspmfuncs.py
#!/usr/bin/python

#@+others
#@+node:ekr.20170428084207.365: ** Declarations
import curses
import os

#@+node:ekr.20170428084207.366: ** class ResizeError
class ResizeError(Exception):
    "The screen has been resized"

#@+node:ekr.20170428084207.367: ** hidecursor
def hidecursor():
    try:
        curses.curs_set(0)
    except Exception:
        pass

#@+node:ekr.20170428084207.368: ** showcursor
def showcursor():
    try:
        curses.curs_set(1)
    except Exception:
        pass

#@+node:ekr.20170428084207.369: ** CallSubShell
def CallSubShell(subshell):
    """Call this function if you need to execute an external command in a subshell (os.system).  All the usual warnings apply -- the command line will be
    expanded by the shell, so make sure it is safe before passing it to this function."""
    curses.def_prog_mode()
    #curses.endwin() # Probably causes a memory leak.

    rtn = os.system("%s" % (subshell))
    curses.reset_prog_mode()
    if rtn is not 0: return False
    else: return True

    curses.reset_prog_mode()

hide_cursor = hidecursor
show_cursor = showcursor
#@-others
#@@language python
#@@tabwidth -4
#@-leo

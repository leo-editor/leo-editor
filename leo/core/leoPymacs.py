# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20061024060248.1: * @file leoPymacs.py
#@@first
#@+<< docstring>>
#@+node:ekr.20061024060248.2: ** << docstring >> (leoPymacs.py)
"""A module to allow the Pymacs bridge to access Leo data.

All code in this module must be called *from* Emacs:
calling Pymacs.lisp in other situations will hang Leo.

Notes:

- The init method adds the parent directory of leoPymacs.py to
  Python's sys.path. This is essential to make imports work from
  inside Emacs.

- As of Leo 4.5, the following code, when executed from an Emacs buffer,
  will open trunk/leo/test.leo::

      (pymacs-load "c:\\leo.repo\\trunk\\leo\\core\\leoPymacs" "leo-")
      (setq c (leo-open "c:\\leo.repo\\trunk\\leo\\test\\test.leo"))

  Note that full path names are required in each case.

"""
#@-<< docstring>>
# As in leo.py we must be very careful about imports.
# pylint: disable = global-variable-not-assigned
g = None # set by init: do *not* import it here!
inited = False
pymacsFile = __file__
# print('leoPymacs:pymacsFile',pymacsFile)
#@+others
#@+node:ekr.20061024131236: ** dump (pymacs)
def dump(anObject):
    global g
    init()
    return str(g.toEncodedString(repr(anObject), encoding='ascii'))
#@+node:ekr.20061024130957: ** getters (pymacs)
def get_app():
    """Scripts can use g.app.scriptDict for communication with pymacs."""
    global g
    init()
    return g.app

def get_g():
    global g
    init()
    return g

def script_result():
    global g
    init()
    return g.app.scriptResult
#@+node:ekr.20061024060248.3: ** hello (pymacs)
def hello():
    init()
    return f"Hello from Leo.  g.app: {g.app}"
#@+node:ekr.20061024075542: ** init  (pymacs)
def init():
    global inited
    if inited:
        return
    inited = True # Only try once, no matter what happens.
    # Add the parent path of this file to sys.path
    import os
    import sys
    theDir = os.path.abspath(os.path.join(os.path.dirname(pymacsFile), '..', '..'))
    if theDir not in sys.path:
        print('leoPymacs:adding', theDir, 'to sys.path')
        sys.path.append(theDir)
    # Create the dummy app
    try:
        import leo.core.runLeo as leo
    except ImportError:
        print('leoPymacs.init: can not import runLeo')
        print('leoPymacs.init: sys.path:')
        for z in sys.path: print(z)
    leo.run(pymacs=True)
    try:
        import leo.core.leoGlobals as leoGlobals
    except ImportError:
        print('leoPymacs.init: can not import leoGlobals')
    global g; g = leoGlobals
    # print('leoPymacs:init:g',g)
    if 1: # These traces show up in the pymacs buffer.
        g.trace('app', g.app)
        g.trace('gui', g.app.gui)
#@+node:ekr.20061024075542.1: ** open (pymacs)
def open(fileName=None):
    global g
    init()
    if g.app.unitTesting:
        return None
    if not fileName:
        g.es_print('', 'leoPymacs.open:', 'no file name')
        return None
    # openWithFileName checks to see if the file is already open.
    c = g.openWithFileName(fileName)
    if c:
        g.es_print('', 'leoPymacs.open:', c)
    else:
        g.es_print('', 'leoPymacs.open:', 'can not open', fileName)
    return c
#@+node:ekr.20061024084200: ** run-script (pymacs)
def run_script(c, script, p=None):
    # It is possible to use script=None, in which case p must be defined.
    global g
    init()
    if c is None:
        c = g.app.newCommander(fileName='dummy script file')
    g.app.scriptResult = None
    c.executeScript(
        event=None,
        p=p,
        script=script,
        useSelectedText=False,
        define_g=True,
        define_name='__main__',
        silent=True, # Don't write to the log.
    )
    return g.app.scriptResult
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

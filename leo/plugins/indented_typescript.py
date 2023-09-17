#@+leo-ver=5-thin
#@+node:ekr.20230917013414.1: * @file ../plugins/indented_typescript.py
"""
A plugin to edit typescript files using indentation instead of curly brackets.

- The ``open2`` event handler deletes curly brackets,
  after checking that nothing (except comments?) follows curly brackets.
- The ``read1`` event handler inserts curly brackets based on indentation.

Both event handlers will do a check similar to Python's tabnanny module.
"""
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoCommands import Commands as Cmdr
assert g

#@+others
#@+node:ekr.20230917084259.1: ** top-level (indented_typescript.py)
#@+node:ekr.20230917015308.1: *3* init (indented_typescript.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    g.registerHandler('before-create-leo-frame', onCreate)
    g.registerHandler('after-reading-external-file', onAfterRead)
    g.registerHandler('before-writing-external-file', onBeforeWrite)
    return True
#@+node:ekr.20230917084347.1: *3* event handlers (indented_typescript.py)
def onCreate(tag: str, keys: Any) -> None:
    """Instantiate an IndentedTypeScript instance for c."""
    c=keys.get('c')
    if c:
        # g.trace(c.shortFileName(), g.callers())
        gControllers[c.hash()] = IndentedTypeScript(c)

def onAfterRead(tag: str, kwargs: Any) -> None:
    """after-read-external-file event handler for indented_typescript.py"""
    c, p = kwargs.get('c'), kwargs.get('p')
    if c and p:
        controller = gControllers.get(c.hash())
        controller.after_read(c, p)

def onBeforeWrite(tag: str, kwargs: Any) -> None:
    """before-writing-external-file event handler for indented_typescript.py"""
    c, p = kwargs.get('c'), kwargs.get('p')
    if c and p:
        controller = gControllers.get(c.hash())
        controller.before_write(c, p)
#@+node:ekr.20230917083456.1: ** class IndentedTypeScript
class IndentedTypeScript:
    """A class to support indented typescript files."""

    def __init__(self, c: Cmdr) -> None:
        self.c = c

    #@+others
    #@+node:ekr.20230917091730.1: *3* IndentedTypeScript.after_read
    def after_read(self, c, p):
        assert c == self.c
        assert p.isAnyAtFileNode(), p.h
        if not p.h.strip().endswith('.ts'):
            g.trace(f"Not a .ts file: {p.h}")
            return
        g.trace(p.h)
    #@+node:ekr.20230917091801.1: *3* IndentedTypeScript.before_write
    def before_write(self, c, p):
        assert c == self.c
        assert p.isAnyAtFileNode(), p.h
        if not p.h.strip().endswith('.ts'):
            g.trace(f"Not a .ts file: {p.h}")
            return
        g.trace(p.h)
        
    #@-others
#@-others

gControllers: dict[str, IndentedTypeScript] = {}  # keys are c.hash()
#@-leo

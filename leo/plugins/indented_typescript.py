#@+leo-ver=5-thin
#@+node:ekr.20230917013414.1: * @file ../plugins/indented_typescript.py
"""
A plugin to edit typescript files using indentation instead of curly brackets.

- The ``open2`` event handler deletes curly brackets,
  after checking that nothing (except comments?) follows curly brackets.
- The ``read1`` event handler inserts curly brackets based on indentation.

Both event handlers will do a check similar to Python's tabnanny module.
"""

#@+<< imports: indented_typescript.py>>
#@+node:ekr.20230917013945.1: ** << imports: indented_typescript.py>>
# To do.
#@-<< imports: indented_typescript.py>>

#@+others
#@+node:ekr.20230917015308.1: ** init
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    return True
#@-others
#@-leo

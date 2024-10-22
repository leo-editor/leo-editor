#@+leo-ver=5-thin
#@+node:ekr.20241022090855.1: * @file leoJupytext.py
"""
Support for pairing .ipynb and .py files with jupytext.

https://github.com/mwouts/jupytext
"""

#@+<< leoJupytext: imports and annotations >>
#@+node:ekr.20241022093347.1: ** << leoJupytext: imports and annotations >>
try:
    import jupytext
    has_jupytext = True
except Exception:
    has_jupytext = False
    print('Can not import jupytext')
    print('pip install jupytext')

from leo.core import leoGlobals as g
assert g  ###
assert jupytext  ###
#@-<< leoJupytext: imports and annotations >>

#@+others
#@+node:ekr.20241022093215.1: ** class JupytextManager
class JupytextManager:

    def __init__(self) -> None:
        g.trace('has_jupytext', has_jupytext, g.callers())  ###
        pass

    #@+others
    #@-others
#@-others

#@-leo

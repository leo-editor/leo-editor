#@+leo-ver=5-thin
#@+node:ekr.20241030151621.1: * @file ../modes/jupytext.py
#@@language python
"""
leo/modes/jupytext.py, Leo's colorizer for @language jupytext.
"""
#@+<< jupytext.py: imports >>
#@+node:ekr.20241031140333.1: ** << jupytext.py: imports >>
from __future__ import annotations

from typing import Any

from leo.core import leoGlobals as g
assert g
#@-<< jupytext.py: imports >>

#@+others
#@+node:ekr.20241105203501.1: ** alternate_main_loop (jupytext.py)
def alternate_main_loop(colorer: Any, n: int, s: str) -> None:
    """A main loop to replace jedit.mainLoop"""
    self = colorer

    if self.match_at_language(s, 0) > 0:  # Sets state
        return
    if not s.startswith('# %%'):
        return

    # Colorize with jupytext comments.
    self.colorRangeWithTag(s, 0, len(s), tag='comment1')

    # Simulate @language md or @language python.
    language = 'md' if s.startswith('# %% [markdown]') else 'python'
    self.init_mode(language)
    n = self.setInitialStateNumber()
    self.setState(n)
#@-others
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20241103040135.1: * @file ../modes/new_jupytext.py
#@@language python
"""
leo/modes/jupytext.py, Leo's colorizer for @language jupytext.
"""

#@+<< new_jupytext.py: imports >>
#@+node:ekr.20241103040135.2: ** << new_jupytext.py: imports >>
from __future__ import annotations

from typing import TYPE_CHECKING

from leo.core.leoColorizer import JEditColorizer as Colorer
from leo.core import leoGlobals as g
assert g

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@-<< new_jupytext.py: imports >>
#@+<< new_jupytext.py: data >>
#@+node:ekr.20241103083624.1: ** << new_jupytext.py: data >>
outer_state = None  ### 'outer-state'
#@-<< new_jupytext.py: data >>

#@+others
#@+node:ekr.20241103040332.1: ** colorize_line (new_jupytext.py)
def colorize_line(colorizer: Colorer, n: int, s: str) -> str:
    g.trace(f"{n:2}     {s!r}")
    assert isinstance(colorizer, Colorer), colorizer
    return 'outer-state'  ###
#@+node:ekr.20241103072835.1: ** init_scanner (new_jupytext.py)
def init_scanner(n: int) -> str:
    """Init this file and return the initial state."""
    ### g.trace(outer_state, g.callers(2))
    return outer_state
#@+node:ekr.20241103040135.4: ** jupytext_comment
def predicate(s: str) -> str:
    """Return a valid language name if s is a jupytext marker."""
    line = s.strip()
    if line.startswith('# %% [markdown]'):
        return 'md'
    if line.startswith('# %%'):
        return 'python'
    return ''

def jupytext_comment(colorer: Colorer, s: str, i: int) -> int:
    """
    Color a *single line* in the appropriate state.
    
    Return: n > 1 if n characters match, otherwise -1.
    """
    assert s[i] == '#'

    # Colorize *this* line.
    colorer.match_line(s, i, kind='comment1')

    line = s.strip()
    if line.startswith('# %%'):
        # Colorize the *next* lines until the predicate matches.
        language = 'md' if line.startswith('# %% [markdown]') else 'python'
        colorer.match_span_delegated_lines(s, i, language=language, predicate=predicate)

    return -1  # This line has been completely handled.
#@+node:ekr.20241103040135.5: ** jupytext_keyword
def jupytext_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)

#@-others
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20241030151621.1: * @file ../modes/jupytext.py
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

#@+others  # Define rules.
#@+node:ekr.20241105203501.1: ** jupytext_comment
def jupytext_comment(colorer: Any, s: str, i: int) -> int:
    """
    Switch to md or python coloring if s is a %% comment, provided that
    c.p.b contains @language jupytext.
    
    New in Leo 6.8.3.
    """
    try:
        c = colorer.c
    except Exception:
        return 0  # Fail, allowing other matches.

    # *Always* colorize the comment line as a *jupytext* comment.
    n = colorer.match_eol_span(s, i, kind="comment1", seq="#")

    is_any_jupytext_comment = (
        i == 0
        and s.startswith('# %%')
        and any(z.startswith('@language jupytext')
            for z in g.splitLines(c.p.b))
    )
    if is_any_jupytext_comment:
        # Simulate @language md or @language python.
        language = 'md' if s.startswith('# %% [markdown]') else 'python'
        colorer.init_mode(language)
        state_i = colorer.setInitialStateNumber()
        colorer.setState(state_i)

    return n  # Succeed. Do not allow other matches.
#@+node:ekr.20241105230332.1: ** jupytext_directive
def jupytext_directive(colorer: Any, s: str, i: int) -> int:
    return colorer.match_leo_keywords(s, i)
#@-others

rulesDict1 = {
    "#": [jupytext_comment],
    "@": [jupytext_directive],
}

# x.rulesDictDict for jupytext mode.
rulesDictDict = {
    "jupytext_main": rulesDict1,
}

#@@language python
#@-leo

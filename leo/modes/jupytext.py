#@+leo-ver=5-thin
#@+node:ekr.20241030151621.1: * @file ../modes/jupytext.py
#@@language python
"""
leo/modes/jupytext.py, Leo's colorizer for @language jupytext.
"""
#@+<< jupytext.py: imports >>
#@+node:ekr.20241031140333.1: ** << jupytext.py: imports >>
from __future__ import annotations

from typing import Dict, TYPE_CHECKING

from leo.core import leoGlobals as g
assert g

if TYPE_CHECKING:
    from leo.core.leoColorizer import JEditColorizer as Colorer
#@-<< jupytext.py: imports >>
#@+<< jupytext.py: rules >>
#@+node:ekr.20241031024909.1: ** << jupytext.py: rules >>
#@+others
#@+node:ekr.20241031024939.2: *3* jupytext_comment
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
#@+node:ekr.20241031024936.1: *3* jupytext_keyword
def jupytext_keyword(colorer: Colorer, s: str, i: str) -> int:
    return colorer.match_keywords(s, i)

#@-others

#@-<< jupytext.py: rules >>
#@+<< jupytext.py: interface dicts >>
#@+node:ekr.20241101031846.1: ** << jupytext.py: interface dicts >>
properties: Dict = {}

jupytext_rules_dict: Dict = {
    '@': [jupytext_keyword],
    '#': [jupytext_comment],
}

rulesDictDict: Dict = {
    "jupytext_main": jupytext_rules_dict,
}
#@-<< jupytext.py: interface dicts >>
#@-leo

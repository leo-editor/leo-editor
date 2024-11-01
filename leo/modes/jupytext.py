#@+leo-ver=5-thin
#@+node:ekr.20241030151621.1: * @file ../modes/jupytext.py
#@@language python
"""
Leo colorizer control file for @language notebook.
This file is in the public domain.
"""

#@+<< jupytext.py: imports >>
#@+node:ekr.20241031140333.1: ** << jupytext.py: imports >>
from __future__ import annotations
import string
from typing import Any

from leo.core import leoGlobals as g
assert g
#@-<< jupytext.py: imports >>
global_state = '??'
#@+<< jupytext.py: global data >>
#@+node:ekr.20241031140131.1: ** << jupytext.py: global data >>
delegate_dict = {
    'md': 'md:md_main',
    'py': 'python:python_main',
    '??': '',
}
marker_dict = {
    'md': '# %% [markdown]',
    'py': '# %%',
    '??': '',
}
markup_table = (
    ('md', '# %% [markdown]'),
    ('py', '# %%'),
)
#@-<< jupytext.py: global data >>
#@+<< jupytext.py: rules >>
#@+node:ekr.20241031024909.1: ** << jupytext.py: rules >>

# n > 0: success.
# n == 0: temporary failure.
# n < 0: total failure, skip n chars.

#@+others
#@+node:ekr.20241031043109.1: *3* comment_helper
# This is a helper, not a rule!

def predicate(s: str) -> bool:
    return s.strip().startswith('# %%)')  # Also matches '# %% [markdown]'.

def comment_helper(colorer: Any, s: str, i: int) -> int:
    """Continue coloring."""
    global global_state

    if 1:  ###
        print('')
        g.trace(global_state, i, s)

    # Colorize *this* line.
    colorer.match_line(s, i, kind='comment1')

    # Continue colorizing on the *next* line.
    colorer.match_span_delegated_lines(s, i,
        delegate=delegate_dict.get(global_state),
        predicate=predicate)

    # We have completely colorized *this* line.
    return -1
#@+node:ekr.20241031024939.2: *3* jupytext_comment
def jupytext_comment(colorer, s, i) -> int:
    """
    Color a *single line* in the appropriate state.
    
    Return: n > 1 if n characters match, otherwise -1.
    """
    assert s[i] == '#'
    global global_state
    # Check for the next target.
    line = s.strip()
    if True:  ### global_state == '??':
        for (state, target) in markup_table:
            if line.startswith(target):
                # Switch to a new state.
                global_state = state
                g.trace('   NEW STATE', global_state, line)  ###
                colorer.clearState()
                return comment_helper(colorer, s, i)
    # This is not an error.
    return comment_helper(colorer, s, i)

#@+node:ekr.20241031024936.1: *3* jupytext_keyword
def jupytext_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)

#@-others

#@-<< jupytext.py: rules >>
#@+<< jupytext.py: interface dicts >>
#@+node:ekr.20241101031846.1: ** << jupytext.py: interface dicts >>
properties = {}

jupytext_rules_dict = {
    '@': [jupytext_keyword],
    '#': [jupytext_comment],
}

rulesDictDict = {
    "jupytext_main": jupytext_rules_dict,
}
#@-<< jupytext.py: interface dicts >>
#@-leo

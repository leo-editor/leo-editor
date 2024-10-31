#@+leo-ver=5-thin
#@+node:ekr.20241030151621.1: * @file ../modes/notebook.py
#@@language python
"""
Leo colorizer control file for @language notebook.
This file is in the public domain.
"""

#@+<< notebook: imports >>
#@+node:ekr.20241031140333.1: ** << notebook: imports >>
from __future__ import annotations
from typing import Any
from leo.core import leoGlobals as g  ###
#@-<< notebook: imports >>
#@+<< notebook: global data >>
#@+node:ekr.20241031140131.1: ** << notebook: global data >>
# The state of the previous line: ('??', 'md', 'py').
global_state = '??'

delegate_dict = {
    'md': 'md::md_main',
    'py': 'python::python_main',
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
#@-<< notebook: global data >>
#@+<< notebook: rules >>
#@+node:ekr.20241031024909.1: ** << notebook: rules >>

# n > 0: success.
# n == 0: temporary failure.
# n < 0: total failure, skip n chars.

#@+others
#@+node:ekr.20241031043109.1: *3* comment_helper
# This is a helper, not a rule!

def comment_helper(colorer: Any, s: str, i: int) -> int:
    """Continue coloring until match_span finds the end_markup."""
    global global_state
    state = global_state

    # Bind the target and the delegate.
    delegate = delegate_dict.get(state)
    target = marker_dict.get(state)
    n = colorer.match_span_delegated_lines(s, i, target, delegate)
    if 1:
        g.trace(f"returns: {n} state: {state!r} {s!r}")
        # g.trace(f"target: {target!r} delegate: {delegate!r}")
        print('')
    if n > 0:
        ### colorer.clearState()
        colorer.match_line(s, i, kind='comment1')
    return n
#@+node:ekr.20241031024936.1: *3* notebook_keyword
def notebook_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)

#@+node:ekr.20241031024939.2: *3* notebook_comment
def notebook_comment(colorer, s, i) -> int:
    """
    Color a *single line* in the appropriate state.
    
    Return: n > 1 if n characters match, otherwise -1.
    """
    assert s[i] == '#'
    global global_state
    # Check for the next target.
    line = s.strip()
    for (state, target) in markup_table:
        if line.startswith(target):
            # Switch to a new state.
            global_state = state
            g.trace('   NEW STATE', global_state, line)  ###
            return comment_helper(colorer, s, i)
    # Continue the present state
    ### g.trace('FALL THROUGH', global_state, line)
    return comment_helper(colorer, s, i)
#@-others

#@-<< notebook: rules >>

notebook_rules_dict = {
    '@': [notebook_keyword],
    '#': [notebook_comment],
}

rulesDictDict = {
    "notebook_main": notebook_rules_dict,
}

properties = {}
#@-leo

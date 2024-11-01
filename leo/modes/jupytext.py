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
#@+<< jupytext.py: global data >>
#@+node:ekr.20241031140131.1: ** << jupytext.py: global data >>
# The state of the previous line: ('??', 'md', 'py').
global_state = '??'

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
#@+node:ekr.20241031043109.1: *3* comment_helper (Needs a loop????)
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
        g.trace(f"returns: {n} state: {state!r} i: {i} {s!r}")
        # g.trace(f"target: {target!r} delegate: {delegate!r}")
        print('')
    if n == -1:
        colorer.match_line(s, i, kind='comment1')
    return n
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
            colorer.clearState()
            return comment_helper(colorer, s, i)
    # Continue the present state
    ### g.trace('FALL THROUGH', global_state, line)
    return comment_helper(colorer, s, i)
#@+node:ekr.20241031143235.1: *3* notebook_default (not used)
def notebook_default(colorer, s, i):
    global global_state
    assert False, g.callers()
    return -1  ############
    state = global_state
    if i > 0:
        return -1
    # n = colorer.currentState()
    # color_state = colorer.stateDict.get(n, 'no-state')
    # g.trace('COLOR_STATE', color_state)
    if colorer.language != 'notebook':
        g.trace('LANGUAGE', colorer.language)
        return -1

    # Bind the target and the delegate.
    delegate = delegate_dict.get(state)
    target = marker_dict.get(state)
    # g.trace(f"state: {state!r} target: {target!r} delegate: {delegate!r} {s!r}")
    g.trace(f"state: {state!r} {s!r}")
    n = colorer.match_span_delegated_lines(s, i, target, delegate)
    if 1:
        g.trace(f"returns: {n}")
        print('')
    ###
        # # # colorer.match_line(s, i, kind='comment1')
    return n
#@+node:ekr.20241031024936.1: *3* notebook_keyword
def notebook_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)

#@-others

#@-<< jupytext.py: rules >>

notebook_rules_dict = {
    '@': [notebook_keyword],
    '#': [notebook_comment],
}

# Add all ascii characters.
if 0:  # This may not be necessary!
    for ch in string.printable:
        if ch not in notebook_rules_dict:
            notebook_rules_dict[ch] = [notebook_default]

rulesDictDict = {
    "notebook_main": notebook_rules_dict,
}

properties = {}
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20241119063015.1: * @file ../modes/vue.py
"""
leo/modes/vue.py: Leo's mode file for @language vue.
"""
#@+<< vue.py: imports >>
#@+node:ekr.20241119063015.2: ** << vue.py: imports >>
from __future__ import annotations
from typing import Any
from leo.core import leoGlobals as g
assert g
#@-<< vue.py: imports >>

# This file does *not* call colorizer.end_delegated_mode().
supports_delegated_modes = False

#@+<< vue.py: rules >>
#@+node:ekr.20241120011456.1: ** << vue.py: rules >>
#@+others
#@+node:ekr.20241119063015.4: *3* vue_directive
def vue_directive(colorer: Any, s: str, i: int) -> int:
    return colorer.match_leo_keywords(s, i)
#@+node:ekr.20241119063015.3: *3* vue_element
def vue_element(colorer: Any, s: str, i: int) -> int:
    """
    Handle `<`, the start of an element.
    Switch between modes provided that c.p.b contains @language vue.
    
    New in Leo 6.8.3.
    """
    try:
        c = colorer.c
    except Exception:
        return 0  # Fail, allowing other matches.

    # Prototype.
    # g.trace(i, s)
    n = colorer.match_span(s, i, kind="comment1",
        begin="<", end=">", at_line_start=True)

    # # *Always* colorize the comment line as a *vue* comment.
    # n = colorer.match_eol_span(s, i, kind="comment1", seq="#")
    # is_any_vue_comment = (
        # i == 0
        # and s.startswith('# %%')
        # and any(z.startswith('@language vue')
            # for z in g.splitLines(c.p.b))
    # )
    # if is_any_vue_comment:
        # # Simulate @language md or @language python.
        # language = 'md' if s.startswith('# %% [markdown]') else 'python'
        # colorer.init_mode(language)
        # state_i = colorer.setInitialStateNumber()
        # colorer.setState(state_i)

    return n  # Succeed. Do not allow other matches.
#@-others
#@-<< vue.py: rules >>
#@+<< vue.py: dictionaries >>
#@+node:ekr.20241120011610.1: ** << vue.py: dictionaries >>

rulesDict1 = {
    "<": [vue_element],
    "@": [vue_directive],
}

# x.rulesDictDict for vue mode.
rulesDictDict = {
    "vue_main": rulesDict1,
}
#@-<< vue.py: dictionaries >>

#@@language python
#@@tabwidth -4
#@-leo

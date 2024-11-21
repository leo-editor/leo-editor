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
    """
    if i != 0:
        return -len(s)  # Fail completely.

    # top-level language blocks and their corresponding mode files.
    blocks = (
        ('<script', 'javascript'),
        ('<style', 'css'),
        ('<template', 'html'),
    )
    for block, language in blocks:
        if s.startswith(block):
            # Colorize the element as an html element.
            # g.trace(f"new language: {language}")
            colorer.match_seq(s, i, kind="markup", seq=block, delegate="html")

            # Simulate `@language language`.
            colorer.push_delegate(language)
            return len(s)  # Success.

    # Error: colorizer the element as a comment.
    # g.trace('Oops:', s)
    colorer.match_span(s, i, kind="comment1", begin="<", end=">")
    return -len(s)  # Fail completely.
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

#@+leo-ver=5-thin
#@+node:ekr.20241030151621.1: * @file ../modes/notebook.py
#@@language python
"""
Leo colorizer control file for @language notebook.
This file is in the public domain.
"""

#@+<< notebook: rules >>
#@+node:ekr.20241031024909.1: ** << notebook: rules >>

# n > 0: success.
# n == 0: temporary failure.
# n < 0: total failure, skip n chars.

#@+others
#@+node:ekr.20241031043109.1: *3* comment_helper
# This is a helper, not a rule!

def comment_helper(colorer: Any, s: str, i: int, delegate: str) -> n:
    """Continue coloring until match_span finds the end_markup."""
    n = colorer.match_span(s, i,
        kind=None,
        at_line_start=True,
        begin='',
        end='\n# %%',  # New in Leo 6.8.3.
        delegate=delegate,
    )
    if n > 0:
        global_state = '??'
        colorer.match_line(s, i, kind='comment1')
    return n
#@+node:ekr.20241031024936.1: *3* notebook_keyword
def notebook_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)

#@+node:ekr.20241031024939.2: *3* notebook_comment
markup_table = (
    ('md', '# %% [markdown]'),
    ('py', '# %%'),
)

# The state of the previous line: ('??', 'md', 'py').
global_state = '??'

def notebook_comment(colorer, s, i) -> int:
    """
    Color a *single line* in the appropriate state.
    
    Return: n > 1 if n characters match, otherwise -1.
    """
    assert s[i] == '#'
    global global_state
    line = s.strip()
    if global_state == '??':
        for (state, markup) in markup_table:
            if line.startswith(markup):
                global_state = state
                # The entire line is a comment.
                return colorer.match_line(s, i, kind='comment1')
        if 1:  ### Debugging only.
            print(f"notebook.py::notebook_comment: can not happen: line: {s!r}")
        return -1  # Should never happen.
    if global_state == 'md':
        return comment_helper(colorer, s, i, 'md::md_main')
    if global_state == 'py':
        return comment_helper(colorer, s, i, 'python::python_main')
    return -1  # Should never happen.
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

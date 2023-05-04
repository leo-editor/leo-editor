#@+leo-ver=5-thin
#@+node:ekr.20230419050031.1: * @file ../modes/html.py
# Leo colorizer control file for html mode.
# This file is in the public domain.

from typing import Any

# Properties for html mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

#@+<< Attributes dicts >>
#@+node:ekr.20230419050200.1: ** << Attributes dicts >>
# Attributes dict for html_main ruleset.
html_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_tags ruleset.
html_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_javascript ruleset.
html_javascript_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_back_to_html ruleset.
html_back_to_html_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for html_css ruleset.
html_css_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for html mode.
attributesDictDict = {
    "html_back_to_html": html_back_to_html_attributes_dict,
    "html_css": html_css_attributes_dict,
    "html_javascript": html_javascript_attributes_dict,
    "html_main": html_main_attributes_dict,
    "html_tags": html_tags_attributes_dict,
}

#@-<< Attributes dicts >>
#@+<< Keywords dicts >>
#@+node:ekr.20230419050229.1: ** << Keywords dicts >>
# Keywords dict for html_main ruleset.
html_main_keywords_dict = {}

# Keywords dict for html_tags ruleset.
html_tags_keywords_dict = {}

# Keywords dict for html_javascript ruleset.
html_javascript_keywords_dict = {}

# Keywords dict for html_back_to_html ruleset.
html_back_to_html_keywords_dict = {}

# Keywords dict for html_css ruleset.
html_css_keywords_dict = {}

# Dictionary of keywords dictionaries for html mode.
keywordsDictDict = {
    "html_back_to_html": html_back_to_html_keywords_dict,
    "html_css": html_css_keywords_dict,
    "html_javascript": html_javascript_keywords_dict,
    "html_main": html_main_keywords_dict,
    "html_tags": html_tags_keywords_dict,
}
#@-<< Keywords dicts >>

# Rules for html_main ruleset.

#@+others
#@+node:ekr.20230419051223.1: ** main ruleset
#@+others
#@+node:ekr.20230419050050.1: *3* html_rule0
def html_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

#@+node:ekr.20230419050050.2: *3* html_rule1 <script..</script>
def match(s: str, i: int, pattern: str) -> bool:
    """Same as g.match."""
    return s and s.find(pattern, i, i + len(pattern)) == i

def html_rule1(colorer: Any, s: str, i: int) -> int:

    # Do quick check first.
    if not match(s, i, '<script') and not match(s, i, '<SCRIPT'):
        return 0

    return colorer.match_span(s, i, kind="markup", begin="<script", end="</script>",
        delegate='javascript')  # "html::javascript"

#@+node:ekr.20230419050050.4: *3* html_rule2 <style..</style>
def html_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<style", end="</style>",
        delegate="html::css")

#@+node:ekr.20230419050050.6: *3* html_rule3 <!..>
def html_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">")

#@+node:ekr.20230419050050.7: *3* html_rule4 <..>
def html_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        delegate="html::tags")

#@+node:ekr.20230419050050.8: *3* html_rule5 &..;
def html_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
        no_word_break=True)

#@+node:ekr.20230419050050.9: *3* html_rule_handlebar {{..}}
# New rule for handlebar markup, colored with the literal3 color.
def html_rule_handlebar(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="{{", end="}}")

#@-others

# Rules dict for html_main ruleset.
rulesDict1 = {
    "&": [html_rule5],
    "<": [html_rule0, html_rule1, html_rule2, html_rule3, html_rule4],
    "{": [html_rule_handlebar],
}

#@+node:ekr.20230419050351.1: ** html_tags ruleset
# Rules for html_tags ruleset.

def html_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def html_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def html_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

# Rules dict for html_tags ruleset.
rulesDict2 = {
    "\"": [html_rule6],
    "'": [html_rule7],
    "=": [html_rule8],
}

#@+node:ekr.20230419050529.1: ** html_javascript ruleset
# Rules for html_javascript ruleset.

def html_rule9(colorer, s, i):
    return colorer.match_seq(s, i, "markup", seq=">",
        delegate="javascript::main")

def html_rule10(colorer, s, i):
    return colorer.match_seq(s, i, "markup", seq="SRC=",
        delegate="html::back_to_html")

# Rules dict for html_javascript ruleset.
rulesDict3 = {
    ">": [html_rule9],
    "S": [html_rule10],
}

#@+node:ekr.20230419050552.1: ** back_to_html ruleset
# Rules for html_back_to_html ruleset.

def html_rule11(colorer, s, i):
    return colorer.match_seq(s, i, "markup", seq=">",
        delegate="html::main")

# Rules dict for html_back_to_html ruleset.
rulesDict4 = {
    ">": [html_rule11],
}

#@+node:ekr.20230419051037.1: ** html_css ruleset
# Rules for html_css ruleset.

def html_rule12(colorer, s, i):
    return colorer.match_seq(s, i, "markup", seq=">",
        delegate="css::main")

# Rules dict for html_css ruleset.
rulesDict5 = {
    ">": [html_rule12],
}

#@-others

# x.rulesDictDict for html mode.
rulesDictDict = {
    "html_back_to_html": rulesDict4,
    "html_css": rulesDict5,
    "html_javascript": rulesDict3,
    "html_main": rulesDict1,
    "html_tags": rulesDict2,
}

# Import dict for html mode.
importDict = {}
#@@language python
#@@tabwidth -4
#@-leo

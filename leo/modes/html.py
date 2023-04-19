# Leo colorizer control file for html mode.
# This file is in the public domain.

from typing import Any

# Properties for html mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

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

# Rules for html_main ruleset.

def html_rule0(colorer, s, i):
    return colorer.match_span(s, i, "comment1", begin="<!--", end="-->")
def match(s: str, i: int, pattern: str) -> bool:
    """Same as g.match."""
    return s and s.find(pattern, i, i + len(pattern)) == i

def html_rule1(colorer: Any, s: str, i: int) -> int:
    
    # Do quick check first.
    if not match(s, i, '<script') and not match(s, i, '<SCRIPT'):
        return 0
   
    return colorer.match_span(s, i, "markup", begin="<script", end="</script>",
        delegate='javascript')  # "html::javascript"
def html_rule2(colorer, s, i):
    return colorer.match_span(s, i, "markup", begin="<style", end="</style>",
        delegate="html::css")
def html_rule3(colorer, s, i):
    return colorer.match_span(s, i, "keyword2", begin="<!", end=">")
def html_rule4(colorer, s, i):
    return colorer.match_span(s, i, "markup", begin="<", end=">",
        delegate="html::tags")
def html_rule5(colorer, s, i):
    return colorer.match_span(s, i, "literal2", begin="&", end=";",
        no_word_break=True)
# New rule for handlebar markup, colored with the literal3 color.
def html_rule_handlebar(colorer, s, i):
    return colorer.match_span(s, i, "literal3", begin="{{", end="}}")

# Rules dict for html_main ruleset.
rulesDict1 = {
    "&": [html_rule5],
    "<": [html_rule0, html_rule1, html_rule2, html_rule3, html_rule4],
    "{": [html_rule_handlebar],
}

# Rules for html_tags ruleset.

def html_rule6(colorer, s, i):
    return colorer.match_span(s, i, "literal1", begin="\"", end="\"")

def html_rule7(colorer, s, i):
    return colorer.match_span(s, i, "literal1", begin="'", end="'")

def html_rule8(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="=")

# Rules dict for html_tags ruleset.
rulesDict2 = {
    "\"": [html_rule6],
    "'": [html_rule7],
    "=": [html_rule8],
}

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

# Rules for html_back_to_html ruleset.

def html_rule11(colorer, s, i):
    return colorer.match_seq(s, i, "markup", seq=">",
        delegate="html::main")

# Rules dict for html_back_to_html ruleset.
rulesDict4 = {
    ">": [html_rule11],
}

# Rules for html_css ruleset.

def html_rule12(colorer, s, i):
    return colorer.match_seq(s, i, "markup", seq=">",
        delegate="css::main")

# Rules dict for html_css ruleset.
rulesDict5 = {
    ">": [html_rule12],
}

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

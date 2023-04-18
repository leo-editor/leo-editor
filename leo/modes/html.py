# Leo colorizer control file for html mode.
# This file is in the public domain.
# July 2, 2014: modifications for

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
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def html_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)
        
def html_rule1a(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)
    return j

def html_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::css", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)
        
def html_rule2a(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def html_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::dtd-tags", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def html_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::tags", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def html_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=True)

# New rule for handlebar markup, colored with the literal3 color.
def html_rule_handlebar(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="{{", end="}}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)


# Rules dict for html_main ruleset.
rulesDict1 = {
    "&": [html_rule5],
    "<": [
        html_rule0,
        html_rule1a, html_rule2a,  #3281
        html_rule3, html_rule4,
        ],
    "{": [html_rule_handlebar],
}

# Rules for html_tags ruleset.

def html_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def html_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def html_rule8(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for html_tags ruleset.
rulesDict2 = {
    "\"": [html_rule6,],
    "'": [html_rule7,],
    "=": [html_rule8,],
}

# Rules for html_javascript ruleset.

def html_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="javascript::main")

def html_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="SRC=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="html::back_to_html")

# Rules dict for html_javascript ruleset.
rulesDict3 = {
    ">": [html_rule9,],
    "S": [html_rule10,],
}

# Rules for html_back_to_html ruleset.

def html_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="html::main")

# Rules dict for html_back_to_html ruleset.
rulesDict4 = {
    ">": [html_rule11,],
}

# Rules for html_css ruleset.

def html_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="css::main")

# Rules dict for html_css ruleset.
rulesDict5 = {
    ">": [html_rule12,],
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

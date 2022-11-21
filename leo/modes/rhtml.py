# Leo colorizer control file for rhtml mode.
# This file is in the public domain.

# Properties for rhtml mode.
properties = {
    "commentEnd": "%>",
    "commentStart": "<%#",
}

# Attributes dict for rhtml_main ruleset.
rhtml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for rhtml_tags ruleset.
rhtml_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for rhtml_tags_literal ruleset.
rhtml_tags_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rhtml mode.
attributesDictDict = {
    "rhtml_main": rhtml_main_attributes_dict,
    "rhtml_tags": rhtml_tags_attributes_dict,
    "rhtml_tags_literal": rhtml_tags_literal_attributes_dict,
}

# Keywords dict for rhtml_main ruleset.
rhtml_main_keywords_dict = {}

# Keywords dict for rhtml_tags ruleset.
rhtml_tags_keywords_dict = {}

# Keywords dict for rhtml_tags_literal ruleset.
rhtml_tags_literal_keywords_dict = {}

# Dictionary of keywords dictionaries for rhtml mode.
keywordsDictDict = {
    "rhtml_main": rhtml_main_keywords_dict,
    "rhtml_tags": rhtml_tags_keywords_dict,
    "rhtml_tags_literal": rhtml_tags_literal_keywords_dict,
}

# Rules for rhtml_main ruleset.

def rhtml_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<%#", end="%>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%=", end="%>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="ruby::main", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="ruby::main", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::css", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::dtd-tags", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="rhtml::tags", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=True)

# Rules dict for rhtml_main ruleset.
rulesDict1 = {
    "&": [rhtml_rule8,],
    "<": [rhtml_rule0, rhtml_rule1, rhtml_rule2, rhtml_rule3, rhtml_rule4, rhtml_rule5, rhtml_rule6, rhtml_rule7,],
}

# Rules for rhtml_tags ruleset.

def rhtml_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<%#", end="%>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="rhtml::tags_literal", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="rhtml::tags_literal", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for rhtml_tags ruleset.
rulesDict2 = {
    "\"": [rhtml_rule11,],
    "'": [rhtml_rule12,],
    "<": [rhtml_rule9, rhtml_rule10,],
    "=": [rhtml_rule13,],
}

# Rules for rhtml_tags_literal ruleset.

def rhtml_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def rhtml_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%=", end="%>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

# Rules dict for rhtml_tags_literal ruleset.
rulesDict3 = {
    "<": [rhtml_rule14, rhtml_rule15,],
}

# x.rulesDictDict for rhtml mode.
rulesDictDict = {
    "rhtml_main": rulesDict1,
    "rhtml_tags": rulesDict2,
    "rhtml_tags_literal": rulesDict3,
}

# Import dict for rhtml mode.
importDict = {}

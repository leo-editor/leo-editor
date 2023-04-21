# Leo colorizer control file for patch mode.
# This file is in the public domain.

# Properties for patch mode.
properties = {}

# Attributes dict for patch_main ruleset.
patch_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for patch mode.
attributesDictDict = {
    "patch_main": patch_main_attributes_dict,
}

# Keywords dict for patch_main ruleset.
patch_main_keywords_dict = {}

# Dictionary of keywords dictionaries for patch mode.
keywordsDictDict = {
    "patch_main": patch_main_keywords_dict,
}

# Rules for patch_main ruleset.

def patch_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal1", seq="+++",
          at_line_start=True)

def patch_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="literal2", seq="---",
          at_line_start=True)

def patch_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq="Index:",
          at_line_start=True)

def patch_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword1", seq="+",
          at_line_start=True)

def patch_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword1", seq=">",
          at_line_start=True)

def patch_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="-",
          at_line_start=True)

def patch_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="<",
          at_line_start=True)

def patch_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq="!",
          at_line_start=True)

def patch_rule8(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq="@@",
          at_line_start=True)

def patch_rule9(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq="*",
          at_line_start=True)

# Rules dict for patch_main ruleset.
rulesDict1 = {
    "!": [patch_rule7,],
    "*": [patch_rule9,],
    "+": [patch_rule0, patch_rule3,],
    "-": [patch_rule1, patch_rule5,],
    "<": [patch_rule6,],
    ">": [patch_rule4,],
    "@": [patch_rule8,],
    "I": [patch_rule2,],
}

# x.rulesDictDict for patch mode.
rulesDictDict = {
    "patch_main": rulesDict1,
}

# Import dict for patch mode.
importDict = {}

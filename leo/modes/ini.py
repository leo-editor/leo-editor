# Leo colorizer control file for ini mode.
# This file is in the public domain.

# Properties for ini mode.
properties = {
    "lineComment": ";",
}

# Attributes dict for ini_main ruleset.
ini_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for ini mode.
attributesDictDict = {
    "ini_main": ini_main_attributes_dict,
}

# Keywords dict for ini_main ruleset.
ini_main_keywords_dict = {}

# Dictionary of keywords dictionaries for ini mode.
keywordsDictDict = {
    "ini_main": ini_main_keywords_dict,
}

# Rules for ini_main ruleset.

def ini_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="[", end="]",
          at_line_start=True)

def ini_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";",
          at_line_start=True)

def ini_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#",
          at_line_start=True)

def ini_rule3(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword1", pattern="=",
          at_line_start=True,
          exclude_match=True)

# Rules dict for ini_main ruleset.
rulesDict1 = {
    "#": [ini_rule2,],
    ";": [ini_rule1,],
    "=": [ini_rule3,],
    "[": [ini_rule0,],
}

# x.rulesDictDict for ini mode.
rulesDictDict = {
    "ini_main": rulesDict1,
}

# Import dict for ini mode.
importDict = {}

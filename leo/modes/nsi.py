# Leo colorizer control file for nsi mode.
# This file is in the public domain.

# Properties for nsi mode.
properties = {
    "lineComment": ";",
}

# Attributes dict for nsi_main ruleset.
nsi_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for nsi mode.
attributesDictDict = {
    "nsi_main": nsi_main_attributes_dict,
}

# Keywords dict for nsi_main ruleset.
nsi_main_keywords_dict = {}

# Dictionary of keywords dictionaries for nsi mode.
keywordsDictDict = {
    "nsi_main": nsi_main_keywords_dict,
}

# Rules for nsi_main ruleset.

def nsi_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";")

def nsi_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin='"', end='"',
          no_line_break=True)

def nsi_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

# Rules dict for nsi_main ruleset.
rulesDict1 = {
    ";": [nsi_rule0,],
    '"': [nsi_rule1,],
    "'": [nsi_rule2,],
}

# x.rulesDictDict for nsi mode.
rulesDictDict = {
    "nsi_main": rulesDict1,
}

# Import dict for nsi mode.
importDict = {}

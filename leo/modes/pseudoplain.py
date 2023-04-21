# Leo colorizer control file for pseudoplain mode.
# This file is in the public domain.

# import leo.core.leoGlobals as g

# Properties for plain mode.
properties = {}

# Attributes dict for pseudoplain_main ruleset.
pseudoplain_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

pseudoplain_interior_main_attributes_dict = {
    "default": "comment1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for plain mode.
attributesDictDict = {
    "pseudoplain_main": pseudoplain_main_attributes_dict,
    "pseudoplain_interior": pseudoplain_interior_main_attributes_dict,
}

# Keywords dict for pseudoplain_main ruleset.
pseudoplain_main_keywords_dict = {}

# Dictionary of keywords dictionaries for plain mode.
keywordsDictDict = {
    "pseudoplain_main": pseudoplain_main_keywords_dict,
}

# Rules for pseudoplain_main ruleset.

def pseudoplain_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="[[", end="]]",
          delegate="pseudoplain::interior")

# Rules dict for pseudoplain_main ruleset.
rulesDict1 = {
    "[": [pseudoplain_rule0,],
}

rulesDict2 = {}

# x.rulesDictDict for pseudoplain mode.
rulesDictDict = {
    "pseudoplain_main": rulesDict1,
    "pseudoplain_interior": rulesDict2,
}

# Import dict for pseudoplain mode.
importDict = {}

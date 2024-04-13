#@+leo-ver=5-thin
#@+node:ekr.20240227082119.1: * @file ../modes/ini.py
#@@language python

# Leo's colorizer control file for .ini and .toml files.
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

def ini_list(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="[", end="]",
          at_line_start=True)

def ini_semi_comment(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";")

def ini_pound_comment(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def ini_equal_op(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="=")

def ini_string(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin='"', end='"')

# Rules dict for ini_main ruleset.
rulesDict1 = {
    "#": [ini_pound_comment],
    ";": [ini_semi_comment],
    "=": [ini_equal_op],
    "[": [ini_list],
    '"': [ini_string],
}

# x.rulesDictDict for ini mode.
rulesDictDict = {
    "ini_main": rulesDict1,
}

# Import dict for ini mode.
importDict = {}
#@-leo

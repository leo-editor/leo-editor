# Leo colorizer control file for rtf mode.
# This file is in the public domain.

# Properties for rtf mode.
properties = {}

# Attributes dict for rtf_main ruleset.
rtf_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rtf mode.
attributesDictDict = {
    "rtf_main": rtf_main_attributes_dict,
}

# Keywords dict for rtf_main ruleset.
rtf_main_keywords_dict = {}

# Dictionary of keywords dictionaries for rtf mode.
keywordsDictDict = {
    "rtf_main": rtf_main_keywords_dict,
}

# Rules for rtf_main ruleset.

def rtf_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def rtf_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def rtf_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\\\'\\w\\d")

def rtf_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="\\*\\")

def rtf_rule4(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword1", pattern="\\")

# Rules dict for rtf_main ruleset.
rulesDict1 = {
    "\\": [rtf_rule2, rtf_rule3, rtf_rule4,],
    "{": [rtf_rule0,],
    "}": [rtf_rule1,],
}

# x.rulesDictDict for rtf mode.
rulesDictDict = {
    "rtf_main": rulesDict1,
}

# Import dict for rtf mode.
importDict = {}

# Leo colorizer control file for texinfo mode.
# This file is in the public domain.

# Properties for texinfo mode.
properties = {
    "lineComment": "@c",
}

# Attributes dict for texinfo_main ruleset.
texinfo_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for texinfo mode.
attributesDictDict = {
    "texinfo_main": texinfo_main_attributes_dict,
}

# Keywords dict for texinfo_main ruleset.
texinfo_main_keywords_dict = {}

# Dictionary of keywords dictionaries for texinfo mode.
keywordsDictDict = {
    "texinfo_main": texinfo_main_keywords_dict,
}

# Rules for texinfo_main ruleset.

def texinfo_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="@c")

def texinfo_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="@comment")

def texinfo_rule2(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword1", pattern="@")

def texinfo_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def texinfo_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

# Rules dict for texinfo_main ruleset.
rulesDict1 = {
    "@": [texinfo_rule0, texinfo_rule1, texinfo_rule2,],
    "{": [texinfo_rule3,],
    "}": [texinfo_rule4,],
}

# x.rulesDictDict for texinfo mode.
rulesDictDict = {
    "texinfo_main": rulesDict1,
}

# Import dict for texinfo mode.
importDict = {}

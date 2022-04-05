# Leo colorizer control file for text mode.
# This file is in the public domain.

# Properties for text mode.
properties = {}

# Attributes dict for text_main ruleset.
text_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for text mode.
attributesDictDict = {
    "text_main": text_main_attributes_dict,
}

# Keywords dict for text_main ruleset.
text_main_keywords_dict = {}

# Dictionary of keywords dictionaries for text mode.
keywordsDictDict = {
    "text_main": text_main_keywords_dict,
}

# Rules for text_main ruleset.

def text_rule0(colorer, s, i):
    return colorer.match_terminate(s, i, kind="", at_char=0)

# Rules dict for text_main ruleset.
rulesDict1 = {}

# x.rulesDictDict for text mode.
rulesDictDict = {
    "text_main": rulesDict1,
}

# Import dict for text mode.
importDict = {}

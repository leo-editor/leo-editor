# Leo colorizer control file for json.
# This is the minimal file needed to support @language json.
# This file is in the public domain.

# Properties for json mode.
properties = {}

# Attributes dict for json_main ruleset.
json_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for json mode.
attributesDictDict = {
    "json_main": json_main_attributes_dict,
}

# Keywords dict for json_main ruleset.
json_main_keywords_dict = {}

# Dictionary of keywords dictionaries for json mode.
keywordsDictDict = {
    "json_main": json_main_keywords_dict,
}

# Rules for json_main ruleset.

def json_string(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

if 0:
    def json_single_string(colorer, s, i):
        return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def json_colon(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def json_comma(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def json_open_brace(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def json_close_brace(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def json_open_bracket(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def json_close_bracket(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

# Rules dict for json_main ruleset.
rulesDict1 = {
    # "'": [json_single_string],
    '"': [json_string],
    ":": [json_colon],
    ",": [json_comma],
    "{": [json_open_brace],
    "}": [json_close_brace],
    "[": [json_open_bracket],
    "]": [json_close_bracket],
}

# x.rulesDictDict for json mode.
rulesDictDict = {
    "json_main": rulesDict1,
}

# Import dict for json mode.
importDict = {}

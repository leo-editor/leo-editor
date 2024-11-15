# Leo colorizer control file for rest mode.
# This file is in the public domain.

# Properties for rest mode.
properties = {
    "indentNextLines": ".+::$",
    "lineComment": "..",
}

# Attributes dict for rest_main ruleset.
rest_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rest mode.
attributesDictDict = {
    "rest_main": rest_main_attributes_dict,
}

# Keywords dict for rest_main ruleset.
rest_main_keywords_dict = {}

# Dictionary of keywords dictionaries for rest mode.
keywordsDictDict = {
    "rest_main": rest_main_keywords_dict,
}

# Rules for rest_main ruleset.

def rest_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq="__",
          at_line_start=True)

def rest_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq=".. _",
          at_line_start=True)

def rest_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="={3,}")

def rest_rule3(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="-{3,}")

def rest_rule4(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="~{3,}")

def rest_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="`{3,}")

def rest_rule6(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="#{3,}")

def rest_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\"{3,}")

def rest_rule8(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\^{3,}")

def rest_rule9(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\+{3,}")

def rest_rule10(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\*{3,}")

def rest_rule11(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\.\\.\\s\\|[^|]+\\|",
          at_line_start=True)

def rest_rule12(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal4", regexp="\\|[^|]+\\|")

def rest_rule13(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\.\\.\\s[A-z][A-z0-9-_]+::",
          at_line_start=True)

def rest_rule14(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="\\*\\*[^*]+\\*\\*")

def rest_rule15(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword4", regexp="\\*[^\\s*][^*]*\\*")

def rest_rule16(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="..",
          at_line_start=True)

def rest_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="`[A-z0-9]+[^`]+`_{1,2}")

def rest_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\[[0-9]+\\]_")

def rest_rule19(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\[#[A-z0-9_]*\\]_")

def rest_rule20(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\[*\\]_")

def rest_rule21(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\[[A-z][A-z0-9_-]*\\]_")

def rest_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="``", end="``")

def rest_rule23(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp="`[^`]+`")

def rest_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp=":[A-z][A-z0-9 \t=\\s\\t_]*:")

def rest_rule25(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\+-[+-]+")

def rest_rule26(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\+=[+=]+")

# Rules dict for rest_main ruleset.
rulesDict1 = {
    "\"": [rest_rule7,],
    "#": [rest_rule6,],
    "*": [rest_rule10, rest_rule14, rest_rule15,],
    "+": [rest_rule9, rest_rule25, rest_rule26,],
    "-": [rest_rule3,],
    ".": [rest_rule1, rest_rule11, rest_rule13, rest_rule16,],
    ":": [rest_rule24,],
    "=": [rest_rule2,],
    "[": [rest_rule18, rest_rule19, rest_rule20, rest_rule21,],
    "^": [rest_rule8,],
    "_": [rest_rule0,],
    "`": [rest_rule5, rest_rule17, rest_rule22, rest_rule23,],
    "|": [rest_rule12,],
    "~": [rest_rule4,],
}

# x.rulesDictDict for rest mode.
rulesDictDict = {
    "rest_main": rulesDict1,
}

# Import dict for rest mode.
importDict = {}

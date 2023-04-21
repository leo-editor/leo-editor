# Leo colorizer control file for yaml mode.
# This file is in the public domain.

# Properties for yaml mode.
properties = {
    "indentNextLines": "\\s*([^\\s]+\\s*:|-)\\s*$",
    "indentSize": "2",
    "noTabs": "true",
    "tabSize": "2",
    "lineComment": "#",
}

# Attributes dict for yaml_main ruleset.
yaml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for yaml mode.
attributesDictDict = {
    "yaml_main": yaml_main_attributes_dict,
}

# Keywords dict for yaml_main ruleset.
yaml_main_keywords_dict = {}

# Dictionary of keywords dictionaries for yaml mode.
keywordsDictDict = {
    "yaml_main": yaml_main_keywords_dict,
}

# Rules for yaml_main ruleset.

def yaml_rule0(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="comment1", regexp="\\s*#.*$",
          at_line_start=True)

def yaml_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="---")

def yaml_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="...")

def yaml_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def yaml_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def yaml_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def yaml_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def yaml_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def yaml_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def yaml_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def yaml_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def yaml_rule11(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="&")

def yaml_rule12(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="*")

def yaml_rule13(colorer, s, i):
    # Fix #1082:
        # Old: regexp="\\s*(-|)?\\s*[^\\s]+\\s*:(\\s|$)"
        # Old: at_line_start=True.
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp=r"\s*-?\s*\w+:")

def yaml_rule14(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+~\\s*$")

def yaml_rule15(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+null\\s*$")

def yaml_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+true\\s*$")

def yaml_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+false\\s*$")

def yaml_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+yes\\s*$")

def yaml_rule19(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+no\\s*$")

def yaml_rule20(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+on\\s*$")

def yaml_rule21(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+off\\s*$")

def yaml_rule22(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="!!(map|seq|str|set|omap|binary)")

def yaml_rule23(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword3", regexp="!![^\\s]+")

def yaml_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword4", regexp="![^\\s]+")

# Rules dict for yaml_main ruleset.
rulesDict1 = {
    # EKR: \\s represents  [\t\n\r\f\v], so the whitespace characters themselves, rather than a backspace, must be the leadin characters!
    # This is a bug in jEdit2py.
    "\t": [yaml_rule13, yaml_rule14, yaml_rule15, yaml_rule16, yaml_rule17, yaml_rule18, yaml_rule19, yaml_rule20, yaml_rule21,],
    "\n": [yaml_rule13, yaml_rule14, yaml_rule15, yaml_rule16, yaml_rule17, yaml_rule18, yaml_rule19, yaml_rule20, yaml_rule21,],
    " ": [yaml_rule13, yaml_rule14, yaml_rule15, yaml_rule16, yaml_rule17, yaml_rule18, yaml_rule19, yaml_rule20, yaml_rule21,],
    "#": [yaml_rule0,],
    "!": [yaml_rule22, yaml_rule23, yaml_rule24,],
    "&": [yaml_rule11,],
    "*": [yaml_rule12,],
    "+": [yaml_rule8,],
    "-": [yaml_rule1, yaml_rule7, yaml_rule13],
        # Fix #1082.
    ".": [yaml_rule2,],
    ">": [yaml_rule10,],
    "[": [yaml_rule4,],
    ## "\\": [yaml_rule13,yaml_rule14,yaml_rule15,yaml_rule16,yaml_rule17,yaml_rule18,yaml_rule19,yaml_rule20,yaml_rule21,],
    "]": [yaml_rule3,],
    "{": [yaml_rule5,],
    "|": [yaml_rule9,],
    "}": [yaml_rule6,],
    # Fix #1082.
    "A": [yaml_rule13,],
    "B": [yaml_rule13,],
    "C": [yaml_rule13,],
    "D": [yaml_rule13,],
    "E": [yaml_rule13,],
    "F": [yaml_rule13,],
    "G": [yaml_rule13,],
    "H": [yaml_rule13,],
    "I": [yaml_rule13,],
    "J": [yaml_rule13,],
    "K": [yaml_rule13,],
    "L": [yaml_rule13,],
    "M": [yaml_rule13,],
    "N": [yaml_rule13,],
    "O": [yaml_rule13,],
    "P": [yaml_rule13,],
    "Q": [yaml_rule13,],
    "R": [yaml_rule13,],
    "S": [yaml_rule13,],
    "T": [yaml_rule13,],
    "U": [yaml_rule13,],
    "V": [yaml_rule13,],
    "W": [yaml_rule13,],
    "X": [yaml_rule13,],
    "Y": [yaml_rule13,],
    "Z": [yaml_rule13,],
    "_": [yaml_rule13,],
    "a": [yaml_rule13,],
    "b": [yaml_rule13,],
    "c": [yaml_rule13,],
    "d": [yaml_rule13,],
    "e": [yaml_rule13,],
    "f": [yaml_rule13,],
    "g": [yaml_rule13,],
    "h": [yaml_rule13,],
    "i": [yaml_rule13,],
    "j": [yaml_rule13,],
    "k": [yaml_rule13,],
    "l": [yaml_rule13,],
    "m": [yaml_rule13,],
    "n": [yaml_rule13,],
    "o": [yaml_rule13,],
    "p": [yaml_rule13,],
    "q": [yaml_rule13,],
    "r": [yaml_rule13,],
    "s": [yaml_rule13,],
    "t": [yaml_rule13,],
    "u": [yaml_rule13,],
    "v": [yaml_rule13,],
    "w": [yaml_rule13,],
    "x": [yaml_rule13,],
    "y": [yaml_rule13,],
    "z": [yaml_rule13,],
}

# x.rulesDictDict for yaml mode.
rulesDictDict = {
    "yaml_main": rulesDict1,
}

# Import dict for yaml mode.
importDict = {}

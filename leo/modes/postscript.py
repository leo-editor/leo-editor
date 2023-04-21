# Leo colorizer control file for postscript mode.
# This file is in the public domain.

# Properties for postscript mode.
properties = {
    "lineComment": "%",
}

# Attributes dict for postscript_main ruleset.
postscript_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for postscript_literal ruleset.
postscript_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for postscript mode.
attributesDictDict = {
    "postscript_literal": postscript_literal_attributes_dict,
    "postscript_main": postscript_main_attributes_dict,
}

# Keywords dict for postscript_main ruleset.
postscript_main_keywords_dict = {
    "NULL": "literal2",
    "abs": "operator",
    "add": "operator",
    "atan": "operator",
    "ceiling": "operator",
    "clear": "keyword1",
    "cleartomark": "keyword1",
    "copy": "keyword1",
    "cos": "operator",
    "count": "keyword1",
    "countexecstack": "keyword1",
    "counttomark": "keyword1",
    "div": "operator",
    "dup": "keyword1",
    "exch": "keyword1",
    "exec": "keyword1",
    "execstack": "keyword1",
    "exit": "keyword1",
    "exp": "operator",
    "false": "literal2",
    "floor": "operator",
    "for": "keyword1",
    "idiv": "operator",
    "if": "keyword1",
    "ifelse": "keyword1",
    "ln": "operator",
    "log": "operator",
    "loop": "keyword1",
    "mark": "keyword1",
    "mod": "operator",
    "mul": "operator",
    "ned": "operator",
    "pop": "keyword1",
    "quit": "keyword1",
    "rand": "operator",
    "repeat": "keyword1",
    "roll": "keyword1",
    "round": "operator",
    "rrand": "operator",
    "sin": "operator",
    "sqrt": "operator",
    "srand": "operator",
    "start": "keyword1",
    "stop": "keyword1",
    "stopped": "keyword1",
    "sub": "operator",
    "true": "literal2",
    "truncate": "operator",
}

# Keywords dict for postscript_literal ruleset.
postscript_literal_keywords_dict = {}

# Dictionary of keywords dictionaries for postscript mode.
keywordsDictDict = {
    "postscript_literal": postscript_literal_keywords_dict,
    "postscript_main": postscript_main_keywords_dict,
}

# Rules for postscript_main ruleset.

def postscript_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="%!")

def postscript_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="%?")

def postscript_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="%%")

def postscript_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def postscript_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="(", end=")",
          delegate="postscript::literal")

def postscript_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="<", end=">")

def postscript_rule6(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="/")

def postscript_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def postscript_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def postscript_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def postscript_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def postscript_rule11(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for postscript_main ruleset.
rulesDict1 = {
    "%": [postscript_rule0, postscript_rule1, postscript_rule2, postscript_rule3,],
    "(": [postscript_rule4,],
    "/": [postscript_rule6,],
    "0": [postscript_rule11,],
    "1": [postscript_rule11,],
    "2": [postscript_rule11,],
    "3": [postscript_rule11,],
    "4": [postscript_rule11,],
    "5": [postscript_rule11,],
    "6": [postscript_rule11,],
    "7": [postscript_rule11,],
    "8": [postscript_rule11,],
    "9": [postscript_rule11,],
    "<": [postscript_rule5,],
    "@": [postscript_rule11,],
    "A": [postscript_rule11,],
    "B": [postscript_rule11,],
    "C": [postscript_rule11,],
    "D": [postscript_rule11,],
    "E": [postscript_rule11,],
    "F": [postscript_rule11,],
    "G": [postscript_rule11,],
    "H": [postscript_rule11,],
    "I": [postscript_rule11,],
    "J": [postscript_rule11,],
    "K": [postscript_rule11,],
    "L": [postscript_rule11,],
    "M": [postscript_rule11,],
    "N": [postscript_rule11,],
    "O": [postscript_rule11,],
    "P": [postscript_rule11,],
    "Q": [postscript_rule11,],
    "R": [postscript_rule11,],
    "S": [postscript_rule11,],
    "T": [postscript_rule11,],
    "U": [postscript_rule11,],
    "V": [postscript_rule11,],
    "W": [postscript_rule11,],
    "X": [postscript_rule11,],
    "Y": [postscript_rule11,],
    "Z": [postscript_rule11,],
    "[": [postscript_rule10,],
    "]": [postscript_rule9,],
    "a": [postscript_rule11,],
    "b": [postscript_rule11,],
    "c": [postscript_rule11,],
    "d": [postscript_rule11,],
    "e": [postscript_rule11,],
    "f": [postscript_rule11,],
    "g": [postscript_rule11,],
    "h": [postscript_rule11,],
    "i": [postscript_rule11,],
    "j": [postscript_rule11,],
    "k": [postscript_rule11,],
    "l": [postscript_rule11,],
    "m": [postscript_rule11,],
    "n": [postscript_rule11,],
    "o": [postscript_rule11,],
    "p": [postscript_rule11,],
    "q": [postscript_rule11,],
    "r": [postscript_rule11,],
    "s": [postscript_rule11,],
    "t": [postscript_rule11,],
    "u": [postscript_rule11,],
    "v": [postscript_rule11,],
    "w": [postscript_rule11,],
    "x": [postscript_rule11,],
    "y": [postscript_rule11,],
    "z": [postscript_rule11,],
    "{": [postscript_rule8,],
    "}": [postscript_rule7,],
}

# Rules for postscript_literal ruleset.

def postscript_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="(", end=")",
          delegate="postscript::literal")

# Rules dict for postscript_literal ruleset.
rulesDict2 = {
    "(": [postscript_rule12,],
}

# x.rulesDictDict for postscript mode.
rulesDictDict = {
    "postscript_literal": rulesDict2,
    "postscript_main": rulesDict1,
}

# Import dict for postscript mode.
importDict = {}

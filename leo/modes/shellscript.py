# Leo colorizer control file for shellscript mode.
# This file is in the public domain.

# Properties for shellscript mode.
properties = {
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
}

# Attributes dict for shellscript_main ruleset.
shellscript_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for shellscript_literal ruleset.
shellscript_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for shellscript_exec ruleset.
shellscript_exec_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for shellscript mode.
attributesDictDict = {
    "shellscript_exec": shellscript_exec_attributes_dict,
    "shellscript_literal": shellscript_literal_attributes_dict,
    "shellscript_main": shellscript_main_attributes_dict,
}

# Keywords dict for shellscript_main ruleset.
shellscript_main_keywords_dict = {
    ";;": "operator",
    "case": "keyword1",
    "continue": "keyword1",
    "do": "keyword1",
    "done": "keyword1",
    "elif": "keyword1",
    "else": "keyword1",
    "esac": "keyword1",
    "fi": "keyword1",
    "for": "keyword1",
    "if": "keyword1",
    "in": "keyword1",
    "local": "keyword1",
    "return": "keyword1",
    "then": "keyword1",
    "while": "keyword1",
}

# Keywords dict for shellscript_literal ruleset.
shellscript_literal_keywords_dict = {}

# Keywords dict for shellscript_exec ruleset.
shellscript_exec_keywords_dict = {}

# Dictionary of keywords dictionaries for shellscript mode.
keywordsDictDict = {
    "shellscript_exec": shellscript_exec_keywords_dict,
    "shellscript_literal": shellscript_literal_keywords_dict,
    "shellscript_main": shellscript_main_keywords_dict,
}

# Rules for shellscript_main ruleset.

def shellscript_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#!")

def shellscript_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def shellscript_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def shellscript_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$#")

def shellscript_rule4(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$?")

def shellscript_rule5(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$*")

def shellscript_rule6(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$@")

def shellscript_rule7(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$$")

def shellscript_rule8(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$<")

def shellscript_rule9(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

def shellscript_rule10(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword2", pattern="=",
          exclude_match=True)

def shellscript_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$((", end="))",
          delegate="shellscript::exec")

def shellscript_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$(", end=")",
          delegate="shellscript::exec")

def shellscript_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$[", end="]",
          delegate="shellscript::exec")

def shellscript_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="`", end="`",
          delegate="shellscript::exec")

def shellscript_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="shellscript::literal")

def shellscript_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def shellscript_rule17(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal1", begin="<<[[:space:]'\"]*([[:alnum:]_]+)[[:space:]'\"]*", end="$1",
          delegate="shellscript::literal")

def shellscript_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def shellscript_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def shellscript_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def shellscript_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def shellscript_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def shellscript_rule23(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="%")

def shellscript_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def shellscript_rule25(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for shellscript_main ruleset.
rulesDict1 = {
    "!": [shellscript_rule20,],
    "\"": [shellscript_rule15,],
    "#": [shellscript_rule0, shellscript_rule1,],
    "$": [shellscript_rule2, shellscript_rule3, shellscript_rule4, shellscript_rule5, shellscript_rule6, shellscript_rule7, shellscript_rule8, shellscript_rule9, shellscript_rule11, shellscript_rule12, shellscript_rule13,],
    "%": [shellscript_rule23,],
    "&": [shellscript_rule19,],
    "'": [shellscript_rule16,],
    "(": [shellscript_rule24,],
    "0": [shellscript_rule25,],
    "1": [shellscript_rule25,],
    "2": [shellscript_rule25,],
    "3": [shellscript_rule25,],
    "4": [shellscript_rule25,],
    "5": [shellscript_rule25,],
    "6": [shellscript_rule25,],
    "7": [shellscript_rule25,],
    "8": [shellscript_rule25,],
    "9": [shellscript_rule25,],
    ";": [shellscript_rule25,],
    "<": [shellscript_rule22,],
    "< ": [shellscript_rule17,],
    "=": [shellscript_rule10,],
    ">": [shellscript_rule21,],
    "@": [shellscript_rule25,],
    "A": [shellscript_rule25,],
    "B": [shellscript_rule25,],
    "C": [shellscript_rule25,],
    "D": [shellscript_rule25,],
    "E": [shellscript_rule25,],
    "F": [shellscript_rule25,],
    "G": [shellscript_rule25,],
    "H": [shellscript_rule25,],
    "I": [shellscript_rule25,],
    "J": [shellscript_rule25,],
    "K": [shellscript_rule25,],
    "L": [shellscript_rule25,],
    "M": [shellscript_rule25,],
    "N": [shellscript_rule25,],
    "O": [shellscript_rule25,],
    "P": [shellscript_rule25,],
    "Q": [shellscript_rule25,],
    "R": [shellscript_rule25,],
    "S": [shellscript_rule25,],
    "T": [shellscript_rule25,],
    "U": [shellscript_rule25,],
    "V": [shellscript_rule25,],
    "W": [shellscript_rule25,],
    "X": [shellscript_rule25,],
    "Y": [shellscript_rule25,],
    "Z": [shellscript_rule25,],
    "`": [shellscript_rule14,],
    "a": [shellscript_rule25,],
    "b": [shellscript_rule25,],
    "c": [shellscript_rule25,],
    "d": [shellscript_rule25,],
    "e": [shellscript_rule25,],
    "f": [shellscript_rule25,],
    "g": [shellscript_rule25,],
    "h": [shellscript_rule25,],
    "i": [shellscript_rule25,],
    "j": [shellscript_rule25,],
    "k": [shellscript_rule25,],
    "l": [shellscript_rule25,],
    "m": [shellscript_rule25,],
    "n": [shellscript_rule25,],
    "o": [shellscript_rule25,],
    "p": [shellscript_rule25,],
    "q": [shellscript_rule25,],
    "r": [shellscript_rule25,],
    "s": [shellscript_rule25,],
    "t": [shellscript_rule25,],
    "u": [shellscript_rule25,],
    "v": [shellscript_rule25,],
    "w": [shellscript_rule25,],
    "x": [shellscript_rule25,],
    "y": [shellscript_rule25,],
    "z": [shellscript_rule25,],
    "|": [shellscript_rule18,],
}

# Rules for shellscript_literal ruleset.

def shellscript_rule26(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def shellscript_rule27(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

# Rules dict for shellscript_literal ruleset.
rulesDict2 = {
    "$": [shellscript_rule26, shellscript_rule27,],
}

# Rules for shellscript_exec ruleset.

def shellscript_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def shellscript_rule29(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$((", end="))")

def shellscript_rule30(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$(", end=")")

def shellscript_rule31(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$[", end="]")

def shellscript_rule32(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

def shellscript_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def shellscript_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def shellscript_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def shellscript_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def shellscript_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

# Rules dict for shellscript_exec ruleset.
rulesDict3 = {
    "!": [shellscript_rule35,],
    "$": [shellscript_rule28, shellscript_rule29, shellscript_rule30, shellscript_rule31, shellscript_rule32,],
    "&": [shellscript_rule34,],
    "<": [shellscript_rule37,],
    ">": [shellscript_rule36,],
    "|": [shellscript_rule33,],
}

# x.rulesDictDict for shellscript mode.
rulesDictDict = {
    "shellscript_exec": rulesDict3,
    "shellscript_literal": rulesDict2,
    "shellscript_main": rulesDict1,
}

# Import dict for shellscript mode.
importDict = {}

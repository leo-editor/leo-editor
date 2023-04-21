# Leo colorizer control file for shell mode.
# This file is in the public domain.

# Properties for shell mode.
properties = {
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
}

# Attributes dict for shell_main ruleset.
shell_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for shell_literal ruleset.
shell_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for shell_exec ruleset.
shell_exec_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for shell mode.
attributesDictDict = {
    "shell_exec": shell_exec_attributes_dict,
    "shell_literal": shell_literal_attributes_dict,
    "shell_main": shell_main_attributes_dict,
}

# Keywords dict for shell_main ruleset.
shell_main_keywords_dict = {
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

# Keywords dict for shell_literal ruleset.
shell_literal_keywords_dict = {}

# Keywords dict for shell_exec ruleset.
shell_exec_keywords_dict = {}

# Dictionary of keywords dictionaries for shell mode.
keywordsDictDict = {
    "shell_exec": shell_exec_keywords_dict,
    "shell_literal": shell_literal_keywords_dict,
    "shell_main": shell_main_keywords_dict,
}

# Rules for shell_main ruleset.

def shell_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#!")

def shell_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def shell_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def shell_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$#")

def shell_rule4(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$?")

def shell_rule5(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$*")

def shell_rule6(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$@")

def shell_rule7(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$$")

def shell_rule8(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$<")

def shell_rule9(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

def shell_rule10(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword2", pattern="=",
          exclude_match=True)

def shell_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$((", end="))",
          delegate="shell::exec")

def shell_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$(", end=")",
          delegate="shell::exec")

def shell_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$[", end="]",
          delegate="shell::exec")

def shell_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="`", end="`",
          delegate="shell::exec")

def shell_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="shell::literal")

def shell_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def shell_rule17(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal1", begin="<<[[:space:]'\"]*([[:alnum:]_]+)[[:space:]'\"]*", end="$1",
          delegate="shell::literal")

def shell_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def shell_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def shell_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def shell_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def shell_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def shell_rule23(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="%")

def shell_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def shell_rule25(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for shell_main ruleset.
rulesDict1 = {
    "!": [shell_rule20,],
    "\"": [shell_rule15,],
    "#": [shell_rule0, shell_rule1,],
    "$": [shell_rule2, shell_rule3, shell_rule4, shell_rule5, shell_rule6, shell_rule7, shell_rule8, shell_rule9, shell_rule11, shell_rule12, shell_rule13,],
    "%": [shell_rule23,],
    "&": [shell_rule19,],
    "'": [shell_rule16,],
    "(": [shell_rule24,],
    "0": [shell_rule25,],
    "1": [shell_rule25,],
    "2": [shell_rule25,],
    "3": [shell_rule25,],
    "4": [shell_rule25,],
    "5": [shell_rule25,],
    "6": [shell_rule25,],
    "7": [shell_rule25,],
    "8": [shell_rule25,],
    "9": [shell_rule25,],
    ";": [shell_rule25,],
    "<": [shell_rule22,],
    "< ": [shell_rule17,],
    "=": [shell_rule10,],
    ">": [shell_rule21,],
    "@": [shell_rule25,],
    "A": [shell_rule25,],
    "B": [shell_rule25,],
    "C": [shell_rule25,],
    "D": [shell_rule25,],
    "E": [shell_rule25,],
    "F": [shell_rule25,],
    "G": [shell_rule25,],
    "H": [shell_rule25,],
    "I": [shell_rule25,],
    "J": [shell_rule25,],
    "K": [shell_rule25,],
    "L": [shell_rule25,],
    "M": [shell_rule25,],
    "N": [shell_rule25,],
    "O": [shell_rule25,],
    "P": [shell_rule25,],
    "Q": [shell_rule25,],
    "R": [shell_rule25,],
    "S": [shell_rule25,],
    "T": [shell_rule25,],
    "U": [shell_rule25,],
    "V": [shell_rule25,],
    "W": [shell_rule25,],
    "X": [shell_rule25,],
    "Y": [shell_rule25,],
    "Z": [shell_rule25,],
    "`": [shell_rule14,],
    "a": [shell_rule25,],
    "b": [shell_rule25,],
    "c": [shell_rule25,],
    "d": [shell_rule25,],
    "e": [shell_rule25,],
    "f": [shell_rule25,],
    "g": [shell_rule25,],
    "h": [shell_rule25,],
    "i": [shell_rule25,],
    "j": [shell_rule25,],
    "k": [shell_rule25,],
    "l": [shell_rule25,],
    "m": [shell_rule25,],
    "n": [shell_rule25,],
    "o": [shell_rule25,],
    "p": [shell_rule25,],
    "q": [shell_rule25,],
    "r": [shell_rule25,],
    "s": [shell_rule25,],
    "t": [shell_rule25,],
    "u": [shell_rule25,],
    "v": [shell_rule25,],
    "w": [shell_rule25,],
    "x": [shell_rule25,],
    "y": [shell_rule25,],
    "z": [shell_rule25,],
    "|": [shell_rule18,],
}

# Rules for shell_literal ruleset.

def shell_rule26(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def shell_rule27(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

# Rules dict for shell_literal ruleset.
rulesDict2 = {
    "$": [shell_rule26, shell_rule27,],
}

# Rules for shell_exec ruleset.

def shell_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def shell_rule29(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$((", end="))")

def shell_rule30(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$(", end=")")

def shell_rule31(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="$[", end="]")

def shell_rule32(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

def shell_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def shell_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def shell_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def shell_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def shell_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

# Rules dict for shell_exec ruleset.
rulesDict3 = {
    "!": [shell_rule35,],
    "$": [shell_rule28, shell_rule29, shell_rule30, shell_rule31, shell_rule32,],
    "&": [shell_rule34,],
    "<": [shell_rule37,],
    ">": [shell_rule36,],
    "|": [shell_rule33,],
}

# x.rulesDictDict for shell mode.
rulesDictDict = {
    "shell_exec": rulesDict3,
    "shell_literal": rulesDict2,
    "shell_main": rulesDict1,
}

# Import dict for shell mode.
importDict = {}

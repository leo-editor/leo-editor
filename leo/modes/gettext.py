# Leo colorizer control file for gettext mode.
# This file is in the public domain.

# Properties for gettext mode.
properties = {
    "lineComment": "# ",
}

# Attributes dict for gettext_main ruleset.
gettext_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for gettext_quoted ruleset.
gettext_quoted_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for gettext mode.
attributesDictDict = {
    "gettext_main": gettext_main_attributes_dict,
    "gettext_quoted": gettext_quoted_attributes_dict,
}

# Keywords dict for gettext_main ruleset.
gettext_main_keywords_dict = {
    "c-format": "keyword2",
    "fuzzy": "keyword2",
    "msgid": "keyword1",
    "msgid_plural": "keyword1",
    "msgstr": "keyword1",
    "no-c-format": "keyword2",
}

# Keywords dict for gettext_quoted ruleset.
gettext_quoted_keywords_dict = {}

# Dictionary of keywords dictionaries for gettext mode.
keywordsDictDict = {
    "gettext_main": gettext_main_keywords_dict,
    "gettext_quoted": gettext_quoted_keywords_dict,
}

# Rules for gettext_main ruleset.

def gettext_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#:")

def gettext_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def gettext_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#.")

def gettext_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#~")

def gettext_rule4(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="comment2", pattern="#,")

def gettext_rule5(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="%")

def gettext_rule6(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="$")

def gettext_rule7(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="@")

def gettext_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="gettext::quoted")

def gettext_rule9(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for gettext_main ruleset.
rulesDict1 = {
    "\"": [gettext_rule8,],
    "#": [gettext_rule0, gettext_rule1, gettext_rule2, gettext_rule3, gettext_rule4,],
    "$": [gettext_rule6,],
    "%": [gettext_rule5,],
    "-": [gettext_rule9,],
    "0": [gettext_rule9,],
    "1": [gettext_rule9,],
    "2": [gettext_rule9,],
    "3": [gettext_rule9,],
    "4": [gettext_rule9,],
    "5": [gettext_rule9,],
    "6": [gettext_rule9,],
    "7": [gettext_rule9,],
    "8": [gettext_rule9,],
    "9": [gettext_rule9,],
    "@": [gettext_rule7, gettext_rule9,],
    "A": [gettext_rule9,],
    "B": [gettext_rule9,],
    "C": [gettext_rule9,],
    "D": [gettext_rule9,],
    "E": [gettext_rule9,],
    "F": [gettext_rule9,],
    "G": [gettext_rule9,],
    "H": [gettext_rule9,],
    "I": [gettext_rule9,],
    "J": [gettext_rule9,],
    "K": [gettext_rule9,],
    "L": [gettext_rule9,],
    "M": [gettext_rule9,],
    "N": [gettext_rule9,],
    "O": [gettext_rule9,],
    "P": [gettext_rule9,],
    "Q": [gettext_rule9,],
    "R": [gettext_rule9,],
    "S": [gettext_rule9,],
    "T": [gettext_rule9,],
    "U": [gettext_rule9,],
    "V": [gettext_rule9,],
    "W": [gettext_rule9,],
    "X": [gettext_rule9,],
    "Y": [gettext_rule9,],
    "Z": [gettext_rule9,],
    "_": [gettext_rule9,],
    "a": [gettext_rule9,],
    "b": [gettext_rule9,],
    "c": [gettext_rule9,],
    "d": [gettext_rule9,],
    "e": [gettext_rule9,],
    "f": [gettext_rule9,],
    "g": [gettext_rule9,],
    "h": [gettext_rule9,],
    "i": [gettext_rule9,],
    "j": [gettext_rule9,],
    "k": [gettext_rule9,],
    "l": [gettext_rule9,],
    "m": [gettext_rule9,],
    "n": [gettext_rule9,],
    "o": [gettext_rule9,],
    "p": [gettext_rule9,],
    "q": [gettext_rule9,],
    "r": [gettext_rule9,],
    "s": [gettext_rule9,],
    "t": [gettext_rule9,],
    "u": [gettext_rule9,],
    "v": [gettext_rule9,],
    "w": [gettext_rule9,],
    "x": [gettext_rule9,],
    "y": [gettext_rule9,],
    "z": [gettext_rule9,],
}

# Rules for gettext_quoted ruleset.

def gettext_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\\\"", end="\\\"",
          no_line_break=True)

def gettext_rule11(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="%")

def gettext_rule12(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="$")

def gettext_rule13(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="@")

# Rules dict for gettext_quoted ruleset.
rulesDict2 = {
    "$": [gettext_rule12,],
    "%": [gettext_rule11,],
    "@": [gettext_rule13,],
    "\\": [gettext_rule10,],
}

# x.rulesDictDict for gettext mode.
rulesDictDict = {
    "gettext_main": rulesDict1,
    "gettext_quoted": rulesDict2,
}

# Import dict for gettext mode.
importDict = {}

# Leo colorizer control file for kivy mode.
# This file is in the public domain.

# Properties for kivy mode.
properties = {
    "ignoreWhitespace": "false",
    "lineComment": "#",
}

# Attributes dict for kivy_main ruleset.
kivy_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for kivy mode.
attributesDictDict = {
    "kivy_main": kivy_main_attributes_dict,
}

# Keywords dict for kivy_main ruleset.
kivy_main_keywords_dict = {
    "app": "keyword2",
    "args": "keyword2",
    "canvas": "keyword1",
    "id": "keyword1",
    "root": "keyword2",
    "self": "keyword2",
    "size": "keyword1",
    "text": "keyword1",
    "x": "keyword1",
    "y": "keyword1",
}

# Dictionary of keywords dictionaries for kivy mode.
keywordsDictDict = {
    "kivy_main": kivy_main_keywords_dict,
}

# Rules for kivy_main ruleset.

def kivy_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def kivy_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="kivy::literal_one")

def kivy_rule2(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for kivy_main ruleset.
rulesDict1 = {
    "\"": [kivy_rule1,],
    "#": [kivy_rule0,],
    "0": [kivy_rule2,],
    "1": [kivy_rule2,],
    "2": [kivy_rule2,],
    "3": [kivy_rule2,],
    "4": [kivy_rule2,],
    "5": [kivy_rule2,],
    "6": [kivy_rule2,],
    "7": [kivy_rule2,],
    "8": [kivy_rule2,],
    "9": [kivy_rule2,],
    "@": [kivy_rule2,],
    "A": [kivy_rule2,],
    "B": [kivy_rule2,],
    "C": [kivy_rule2,],
    "D": [kivy_rule2,],
    "E": [kivy_rule2,],
    "F": [kivy_rule2,],
    "G": [kivy_rule2,],
    "H": [kivy_rule2,],
    "I": [kivy_rule2,],
    "J": [kivy_rule2,],
    "K": [kivy_rule2,],
    "L": [kivy_rule2,],
    "M": [kivy_rule2,],
    "N": [kivy_rule2,],
    "O": [kivy_rule2,],
    "P": [kivy_rule2,],
    "Q": [kivy_rule2,],
    "R": [kivy_rule2,],
    "S": [kivy_rule2,],
    "T": [kivy_rule2,],
    "U": [kivy_rule2,],
    "V": [kivy_rule2,],
    "W": [kivy_rule2,],
    "X": [kivy_rule2,],
    "Y": [kivy_rule2,],
    "Z": [kivy_rule2,],
    "a": [kivy_rule2,],
    "b": [kivy_rule2,],
    "c": [kivy_rule2,],
    "d": [kivy_rule2,],
    "e": [kivy_rule2,],
    "f": [kivy_rule2,],
    "g": [kivy_rule2,],
    "h": [kivy_rule2,],
    "i": [kivy_rule2,],
    "j": [kivy_rule2,],
    "k": [kivy_rule2,],
    "l": [kivy_rule2,],
    "m": [kivy_rule2,],
    "n": [kivy_rule2,],
    "o": [kivy_rule2,],
    "p": [kivy_rule2,],
    "q": [kivy_rule2,],
    "r": [kivy_rule2,],
    "s": [kivy_rule2,],
    "t": [kivy_rule2,],
    "u": [kivy_rule2,],
    "v": [kivy_rule2,],
    "w": [kivy_rule2,],
    "x": [kivy_rule2,],
    "y": [kivy_rule2,],
    "z": [kivy_rule2,],
}

# x.rulesDictDict for kivy mode.
rulesDictDict = {
    "kivy_main": rulesDict1,
}

# Import dict for kivy mode.
importDict = {}

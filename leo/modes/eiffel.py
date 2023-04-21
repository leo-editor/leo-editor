# Leo colorizer control file for eiffel mode.
# This file is in the public domain.

# Properties for eiffel mode.
properties = {
    "lineComment": "--",
}

# Attributes dict for eiffel_main ruleset.
eiffel_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for eiffel mode.
attributesDictDict = {
    "eiffel_main": eiffel_main_attributes_dict,
}

# Keywords dict for eiffel_main ruleset.
eiffel_main_keywords_dict = {
    "alias": "keyword1",
    "all": "keyword1",
    "and": "keyword1",
    "as": "keyword1",
    "check": "keyword1",
    "class": "keyword1",
    "creation": "keyword1",
    "current": "literal2",
    "debug": "keyword1",
    "deferred": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "elseif": "keyword1",
    "end": "keyword1",
    "ensure": "keyword1",
    "expanded": "keyword1",
    "export": "keyword1",
    "external": "keyword1",
    "false": "literal2",
    "feature": "keyword1",
    "from": "keyword1",
    "frozen": "keyword1",
    "if": "keyword1",
    "implies": "keyword1",
    "indexing": "keyword1",
    "infix": "keyword1",
    "inherit": "keyword1",
    "inspect": "keyword1",
    "invariant": "keyword1",
    "is": "keyword1",
    "like": "keyword1",
    "local": "keyword1",
    "loop": "keyword1",
    "not": "keyword1",
    "obsolete": "keyword1",
    "old": "keyword1",
    "once": "keyword1",
    "or": "keyword1",
    "precursor": "literal2",
    "prefix": "keyword1",
    "redefine": "keyword1",
    "rename": "keyword1",
    "require": "keyword1",
    "rescue": "keyword1",
    "result": "literal2",
    "retry": "keyword1",
    "select": "keyword1",
    "separate": "keyword1",
    "strip": "literal2",
    "then": "keyword1",
    "true": "literal2",
    "undefine": "keyword1",
    "unique": "literal2",
    "until": "keyword1",
    "variant": "keyword1",
    "void": "literal2",
    "when": "keyword1",
    "xor": "keyword1",
}

# Dictionary of keywords dictionaries for eiffel mode.
keywordsDictDict = {
    "eiffel_main": eiffel_main_keywords_dict,
}

# Rules for eiffel_main ruleset.

def eiffel_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def eiffel_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def eiffel_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def eiffel_rule3(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for eiffel_main ruleset.
rulesDict1 = {
    "\"": [eiffel_rule1,],
    "'": [eiffel_rule2,],
    "-": [eiffel_rule0,],
    "0": [eiffel_rule3,],
    "1": [eiffel_rule3,],
    "2": [eiffel_rule3,],
    "3": [eiffel_rule3,],
    "4": [eiffel_rule3,],
    "5": [eiffel_rule3,],
    "6": [eiffel_rule3,],
    "7": [eiffel_rule3,],
    "8": [eiffel_rule3,],
    "9": [eiffel_rule3,],
    "@": [eiffel_rule3,],
    "A": [eiffel_rule3,],
    "B": [eiffel_rule3,],
    "C": [eiffel_rule3,],
    "D": [eiffel_rule3,],
    "E": [eiffel_rule3,],
    "F": [eiffel_rule3,],
    "G": [eiffel_rule3,],
    "H": [eiffel_rule3,],
    "I": [eiffel_rule3,],
    "J": [eiffel_rule3,],
    "K": [eiffel_rule3,],
    "L": [eiffel_rule3,],
    "M": [eiffel_rule3,],
    "N": [eiffel_rule3,],
    "O": [eiffel_rule3,],
    "P": [eiffel_rule3,],
    "Q": [eiffel_rule3,],
    "R": [eiffel_rule3,],
    "S": [eiffel_rule3,],
    "T": [eiffel_rule3,],
    "U": [eiffel_rule3,],
    "V": [eiffel_rule3,],
    "W": [eiffel_rule3,],
    "X": [eiffel_rule3,],
    "Y": [eiffel_rule3,],
    "Z": [eiffel_rule3,],
    "a": [eiffel_rule3,],
    "b": [eiffel_rule3,],
    "c": [eiffel_rule3,],
    "d": [eiffel_rule3,],
    "e": [eiffel_rule3,],
    "f": [eiffel_rule3,],
    "g": [eiffel_rule3,],
    "h": [eiffel_rule3,],
    "i": [eiffel_rule3,],
    "j": [eiffel_rule3,],
    "k": [eiffel_rule3,],
    "l": [eiffel_rule3,],
    "m": [eiffel_rule3,],
    "n": [eiffel_rule3,],
    "o": [eiffel_rule3,],
    "p": [eiffel_rule3,],
    "q": [eiffel_rule3,],
    "r": [eiffel_rule3,],
    "s": [eiffel_rule3,],
    "t": [eiffel_rule3,],
    "u": [eiffel_rule3,],
    "v": [eiffel_rule3,],
    "w": [eiffel_rule3,],
    "x": [eiffel_rule3,],
    "y": [eiffel_rule3,],
    "z": [eiffel_rule3,],
}

# x.rulesDictDict for eiffel mode.
rulesDictDict = {
    "eiffel_main": rulesDict1,
}

# Import dict for eiffel mode.
importDict = {}

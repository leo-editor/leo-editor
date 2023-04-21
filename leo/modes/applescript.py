# Leo colorizer control file for applescript mode.
# This file is in the public domain.

# Properties for applescript mode.
properties = {
    "commentEnd": "*)",
    "commentStart": "(*",
    "doubleBracketIndent": "false",
    "lineComment": "--",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for applescript_main ruleset.
applescript_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for applescript mode.
attributesDictDict = {
    "applescript_main": applescript_main_attributes_dict,
}

# Keywords dict for applescript_main ruleset.
applescript_main_keywords_dict = {
    "after": "keyword2",
    "and": "operator",
    "anything": "literal2",
    "apr": "literal2",
    "april": "literal2",
    "as": "operator",
    "ask": "literal2",
    "aug": "literal2",
    "august": "literal2",
    "back": "keyword2",
    "before": "keyword2",
    "beginning": "keyword2",
    "bold": "literal2",
    "case": "literal2",
    "close": "keyword3",
    "condensed": "literal2",
    "considering": "keyword1",
    "contains": "operator",
    "continue": "keyword1",
    "copy": "keyword3",
    "count": "keyword3",
    "days": "literal2",
    "dec": "literal2",
    "december": "literal2",
    "delete": "keyword3",
    "diacriticals": "literal2",
    "div": "operator",
    "duplicate": "keyword3",
    "each": "keyword2",
    "eighth": "keyword2",
    "else": "keyword1",
    "end": "keyword1",
    "equal": "operator",
    "equals": "operator",
    "error": "keyword1",
    "every": "keyword2",
    "exists": "keyword3",
    "exit": "keyword1",
    "expanded": "literal2",
    "expansion": "literal2",
    "false": "literal2",
    "feb": "literal2",
    "february": "literal2",
    "fifth": "keyword2",
    "first": "keyword2",
    "fourth": "keyword2",
    "fri": "literal2",
    "friday": "literal2",
    "from": "keyword1",
    "front": "keyword2",
    "get": "keyword1",
    "given": "keyword1",
    "global": "keyword1",
    "hidden": "literal2",
    "hours": "literal2",
    "hyphens": "literal2",
    "id": "keyword2",
    "if": "keyword1",
    "ignoring": "keyword1",
    "in": "keyword1",
    "index": "keyword2",
    "into": "keyword1",
    "is": "keyword1",
    "isn't": "operator",
    "it": "literal2",
    "italic": "literal2",
    "jan": "literal2",
    "january": "literal2",
    "jul": "literal2",
    "july": "literal2",
    "jun": "literal2",
    "june": "literal2",
    "last": "keyword2",
    "launch": "keyword3",
    "local": "keyword1",
    "make": "keyword3",
    "mar": "literal2",
    "march": "literal2",
    "may": "literal2",
    "me": "literal2",
    "middle": "keyword2",
    "minutes": "literal2",
    "mod": "operator",
    "mon": "literal2",
    "monday": "literal2",
    "month": "literal2",
    "move": "keyword3",
    "my": "keyword1",
    "named": "keyword2",
    "nd": "keyword2",
    "ninth": "keyword2",
    "no": "literal2",
    "not": "operator",
    "nov": "literal2",
    "november": "literal2",
    "oct": "literal2",
    "october": "literal2",
    "of": "keyword1",
    "on": "keyword1",
    "open": "keyword3",
    "or": "operator",
    "outline": "literal2",
    "pi": "literal2",
    "plain": "literal2",
    "print": "keyword3",
    "prop": "keyword1",
    "property": "keyword1",
    "punctuation": "literal2",
    "put": "keyword1",
    "quit": "keyword3",
    "rd": "keyword2",
    "reopen": "keyword3",
    "repeat": "keyword1",
    "result": "literal2",
    "return": "keyword1",
    "run": "keyword3",
    "sat": "literal2",
    "saturday": "literal2",
    "save": "keyword3",
    "saving": "keyword3",
    "script": "keyword1",
    "second": "keyword2",
    "sep": "literal2",
    "september": "literal2",
    "set": "keyword1",
    "seventh": "keyword2",
    "shadow": "literal2",
    "sixth": "keyword2",
    "some": "keyword2",
    "space": "literal2",
    "st": "keyword2",
    "strikethrough": "literal2",
    "subscript": "literal2",
    "sun": "literal2",
    "sunday": "literal2",
    "superscript": "literal2",
    "tab": "literal2",
    "tell": "keyword1",
    "tenth": "keyword2",
    "th": "keyword2",
    "the": "keyword2",
    "then": "keyword1",
    "third": "keyword2",
    "through": "keyword2",
    "thru": "keyword2",
    "thu": "literal2",
    "thursday": "literal2",
    "timeout": "keyword1",
    "times": "keyword1",
    "to": "keyword1",
    "transaction": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "tue": "literal2",
    "tuesday": "literal2",
    "underline": "literal2",
    "until": "keyword1",
    "version": "literal2",
    "wed": "literal2",
    "wednesday": "literal2",
    "weekday": "literal2",
    "weeks": "literal2",
    "where": "keyword2",
    "while": "keyword1",
    "whose": "keyword2",
    "with": "keyword1",
    "without": "keyword1",
    "yes": "literal2",
}

# Dictionary of keywords dictionaries for applescript mode.
keywordsDictDict = {
    "applescript_main": applescript_main_keywords_dict,
}

# Rules for applescript_main ruleset.

def applescript_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="(*", end="*)")

def applescript_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def applescript_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def applescript_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def applescript_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def applescript_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def applescript_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def applescript_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def applescript_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def applescript_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def applescript_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def applescript_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def applescript_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def applescript_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def applescript_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def applescript_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def applescript_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def applescript_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="application[\\t\\s]+responses")

def applescript_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="current[\\t\\s]+application")

def applescript_rule19(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="white[\\t\\s]+space")

def applescript_rule20(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="all[\\t\\s]+caps")

def applescript_rule21(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="all[\\t\\s]+lowercase")

def applescript_rule22(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="small[\\t\\s]+caps")

def applescript_rule23(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword3", regexp="missing[\\t\\s]+value")

def applescript_rule24(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for applescript_main ruleset.
rulesDict1 = {
    "\"": [applescript_rule2,],
    "&": [applescript_rule11,],
    "'": [applescript_rule3, applescript_rule24,],
    "(": [applescript_rule0, applescript_rule4,],
    ")": [applescript_rule5,],
    "*": [applescript_rule9,],
    "+": [applescript_rule6,],
    "-": [applescript_rule1, applescript_rule7,],
    "/": [applescript_rule10,],
    "0": [applescript_rule24,],
    "1": [applescript_rule24,],
    "2": [applescript_rule24,],
    "3": [applescript_rule24,],
    "4": [applescript_rule24,],
    "5": [applescript_rule24,],
    "6": [applescript_rule24,],
    "7": [applescript_rule24,],
    "8": [applescript_rule24,],
    "9": [applescript_rule24,],
    "<": [applescript_rule12, applescript_rule13,],
    "=": [applescript_rule16,],
    ">": [applescript_rule14, applescript_rule15,],
    "@": [applescript_rule24,],
    "A": [applescript_rule24,],
    "B": [applescript_rule24,],
    "C": [applescript_rule24,],
    "D": [applescript_rule24,],
    "E": [applescript_rule24,],
    "F": [applescript_rule24,],
    "G": [applescript_rule24,],
    "H": [applescript_rule24,],
    "I": [applescript_rule24,],
    "J": [applescript_rule24,],
    "K": [applescript_rule24,],
    "L": [applescript_rule24,],
    "M": [applescript_rule24,],
    "N": [applescript_rule24,],
    "O": [applescript_rule24,],
    "P": [applescript_rule24,],
    "Q": [applescript_rule24,],
    "R": [applescript_rule24,],
    "S": [applescript_rule24,],
    "T": [applescript_rule24,],
    "U": [applescript_rule24,],
    "V": [applescript_rule24,],
    "W": [applescript_rule24,],
    "X": [applescript_rule24,],
    "Y": [applescript_rule24,],
    "Z": [applescript_rule24,],
    "^": [applescript_rule8,],
    "a": [applescript_rule17, applescript_rule20, applescript_rule21, applescript_rule24,],
    "b": [applescript_rule24,],
    "c": [applescript_rule18, applescript_rule24,],
    "d": [applescript_rule24,],
    "e": [applescript_rule24,],
    "f": [applescript_rule24,],
    "g": [applescript_rule24,],
    "h": [applescript_rule24,],
    "i": [applescript_rule24,],
    "j": [applescript_rule24,],
    "k": [applescript_rule24,],
    "l": [applescript_rule24,],
    "m": [applescript_rule23, applescript_rule24,],
    "n": [applescript_rule24,],
    "o": [applescript_rule24,],
    "p": [applescript_rule24,],
    "q": [applescript_rule24,],
    "r": [applescript_rule24,],
    "s": [applescript_rule22, applescript_rule24,],
    "t": [applescript_rule24,],
    "u": [applescript_rule24,],
    "v": [applescript_rule24,],
    "w": [applescript_rule19, applescript_rule24,],
    "x": [applescript_rule24,],
    "y": [applescript_rule24,],
    "z": [applescript_rule24,],
}

# x.rulesDictDict for applescript mode.
rulesDictDict = {
    "applescript_main": rulesDict1,
}

# Import dict for applescript mode.
importDict = {}

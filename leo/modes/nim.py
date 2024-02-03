#@+leo-ver=5-thin
#@+node:ekr.20240202211600.1: * @file ../modes/nim.py
#@@language python
# Leo colorizer control file for nim mode.
# This file is in the public domain.

import sys

v1, v2, junk1, junk2, junk3 = sys.version_info

# Properties for nim mode.
properties = {
    "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "#",
}

#@+<< Attributes Dicts >>
#@+node:ekr.20240202211600.2: ** << Attributes Dicts >>
# Attributes dict for nim_main ruleset.
nim_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for nim mode.
attributesDictDict = {
    "nim_main": nim_main_attributes_dict,
}
#@-<< Attributes Dicts >>

# Keywords dict for nim_main ruleset.
nim_main_keywords_dict = {
    #@+<< Nim keywords >>
    #@+node:ekr.20240203080736.1: ** << Nim keywords >>
    # Some are reserved for future use.
    "addr": "keyword1",
    "and": "keyword1",
    "as": "keyword1",
    "asm": "keyword1",
    "bind": "keyword1",
    "block": "keyword1",
    "break": "keyword1",
    "case": "keyword1",
    "cast": "keyword1",
    "concept": "keyword1",
    "const": "keyword1",
    "continue": "keyword1",
    "converter": "keyword1",
    "defer": "keyword1",
    "discard": "keyword1",
    "distinct": "keyword1",
    "div": "keyword1",
    "do": "keyword1",
    "elif": "keyword1",
    "else": "keyword1",
    "end": "keyword1",
    "enum": "keyword1",
    "except": "keyword1",
    "export": "keyword1",
    "finally": "keyword1",
    "for": "keyword1",
    "from": "keyword1",
    "func": "keyword1",
    "if": "keyword1",
    "import": "keyword1",
    "in": "keyword1",
    "include": "keyword1",
    "interface": "keyword1",
    "is": "keyword1",
    "isnot": "keyword1",
    "iterator": "keyword1",
    "let": "keyword1",
    "macro": "keyword1",
    "method": "keyword1",
    "mixin": "keyword1",
    "mod": "keyword1",
    "nil": "keyword1",
    "not": "keyword1",
    "notin": "keyword1",
    "object": "keyword1",
    "of": "keyword1",
    "or": "keyword1",
    "out": "keyword1",
    "proc": "keyword1",
    "ptr": "keyword1",
    "raise": "keyword1",
    "ref": "keyword1",
    "return": "keyword1",
    "shl": "keyword1",
    "shr": "keyword1",
    "static": "keyword1",
    "template": "keyword1",
    "try": "keyword1",
    "tuple": "keyword1",
    "type": "keyword1",
    "using": "keyword1",
    "var": "keyword1",
    "when": "keyword1",
    "while": "keyword1",
    "xor": "keyword1",
    "yield": "keyword1",
    #@-<< Nim keywords >>
    #@+<< Names defined in system module >>
    #@+node:ekr.20240203080936.1: ** << Names defined in system module >>
        

        # Names defined in system module.
        # https://nim-lang.org/docs/system.html

        # Functions that are also keywords.
        # "and", "or", "not".
        # "div", "mod", "shl", "shr", "xor".
        # "len".
        # "addr", "isnot".

        # Defined on multiple types.
        "add": "keyword3",

        # Strings and characters.
        "chr": "keyword3",
        "ord": "keyword3",

        # Seqs.
        "del": "keyword3",
        "delete": "keyword3",
        "insert": "keyword3",
        "newSeq": "keyword3",
        "newSeqOfCap": "keyword3",
        "pop": "keyword3",
        "setLen": "keyword3",

        # Sets.
        "card": "keyword3",
        "contains": "keyword3",
        "excl": "keyword3",
        "incl": "keyword3",

        # Numbers.
        "ashr": "keyword3",
        "toFloat": "keyword3",
        "toInt": "keyword3",

        # Ordinals.
        "dec": "keyword3",
        "high": "keyword3",
        "inc": "keyword3",
        "low": "keyword3",
        "pred": "keyword3",
        "succ": "keyword3",

        # Misc.
        "runnableExamples": "keyword3",

        ### Types.

        ### Vars.

        ### Consts.

        ### Procs.  Many!

        "echo": "keyword3",

        ### Iterators.

        ### Macros.

        ### Templates

        ###

        # Constants.
        "false": "keyword3",
        "true": "keyword3",
    #@-<< Names defined in system module >>
}

# Dictionary of keywords dictionaries for nim mode.
keywordsDictDict = {
    "nim_main": nim_main_keywords_dict,
}

#@+<< Nim rules >>
#@+node:ekr.20240202211600.4: ** << Nim rules >>
#@+others
#@+node:ekr.20240202211600.5: *3* nim_rule0
def nim_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")
#@+node:ekr.20240202211600.6: *3* nim_rule1 """
def nim_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"")
#@+node:ekr.20240202211600.7: *3* nim_rule2 '''
def nim_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'''", end="'''")
#@+node:ekr.20240202211600.8: *3* nim_rule3 "
def nim_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")
#@+node:ekr.20240202211600.9: *3* nim_rule4 '
def nim_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")
#@+node:ekr.20240202211600.10: *3* nim_rule5
def nim_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")


#@+node:ekr.20240202211600.11: *3* nim_rule6
def nim_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")


#@+node:ekr.20240202211600.12: *3* nim_rule7
def nim_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")


#@+node:ekr.20240202211600.13: *3* nim_rule8
def nim_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")


#@+node:ekr.20240202211600.14: *3* nim_rule9
def nim_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")


#@+node:ekr.20240202211600.15: *3* nim_rule10
def nim_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")


#@+node:ekr.20240202211600.16: *3* nim_rule11
def nim_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")


#@+node:ekr.20240202211600.17: *3* nim_rule12
def nim_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")


#@+node:ekr.20240202211600.18: *3* nim_rule13
def nim_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")


#@+node:ekr.20240202211600.19: *3* nim_rule14
def nim_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")


#@+node:ekr.20240202211600.20: *3* nim_rule15
def nim_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")


#@+node:ekr.20240202211600.21: *3* nim_rule16
def nim_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")


#@+node:ekr.20240202211600.22: *3* nim_rule17
def nim_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")


#@+node:ekr.20240202211600.23: *3* nim_rule18
def nim_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")


#@+node:ekr.20240202211600.24: *3* nim_rule19
def nim_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")


#@+node:ekr.20240202211600.26: *3* nim_keyword
def nim_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)
#@-others
#@-<< Nim rules >>
#@+<< nim_rules_dict >>
#@+node:ekr.20240202211600.29: ** << nim_rules_dict >>
# Rules dict for nim_main ruleset.
nim_rules_dict = {
    "!": [nim_rule6],
    "\"": [nim_rule1, nim_rule3],
    "#": [nim_rule0],
    "%": [nim_rule15],
    "&": [nim_rule16],
    "'": [nim_rule2, nim_rule4],
    # "(": [nim_rule20],
    "*": [nim_rule12],
    "+": [nim_rule9],
    "-": [nim_rule10],
    "/": [nim_rule11],
    "0": [nim_keyword],
    "1": [nim_keyword],
    "2": [nim_keyword],
    "3": [nim_keyword],
    "4": [nim_keyword],
    "5": [nim_keyword],
    "6": [nim_keyword],
    "7": [nim_keyword],
    "8": [nim_keyword],
    "9": [nim_keyword],
    "<": [nim_rule8, nim_rule14],
    "=": [nim_rule5],
    ">": [nim_rule7, nim_rule13],
    "@": [nim_keyword],
    "A": [nim_keyword],
    "B": [nim_keyword],
    "C": [nim_keyword],
    "D": [nim_keyword],
    "E": [nim_keyword],
    "F": [nim_keyword],  # nim_rule_f_url,
    "G": [nim_keyword],
    "H": [nim_keyword],  # nim_rule_h_url,
    "I": [nim_keyword],
    "J": [nim_keyword],
    "K": [nim_keyword],
    "L": [nim_keyword],
    "M": [nim_keyword],
    "N": [nim_keyword],
    "O": [nim_keyword],
    "P": [nim_keyword],
    "Q": [nim_keyword],
    "R": [nim_keyword],
    "S": [nim_keyword],
    "T": [nim_keyword],
    "U": [nim_keyword],
    "V": [nim_keyword],
    "W": [nim_keyword],
    "X": [nim_keyword],
    "Y": [nim_keyword],
    "Z": [nim_keyword],
    "^": [nim_rule18],
    "_": [nim_keyword],
    "a": [nim_keyword],
    "b": [nim_keyword],
    "c": [nim_keyword],
    "d": [nim_keyword],
    "e": [nim_keyword],
    "f": [nim_keyword],  # nim_rule_f_url
    "g": [nim_keyword],
    "h": [nim_keyword],  # nim_rule_h_url
    "i": [nim_keyword],
    "j": [nim_keyword],
    "k": [nim_keyword],
    "l": [nim_keyword],
    "m": [nim_keyword],
    "n": [nim_keyword],
    "o": [nim_keyword],
    "p": [nim_keyword],
    "q": [nim_keyword],
    "r": [nim_keyword],
    "s": [nim_keyword],
    "t": [nim_keyword],
    "u": [nim_keyword],
    "v": [nim_keyword],
    "w": [nim_keyword],
    "x": [nim_keyword],
    "y": [nim_keyword],
    "z": [nim_keyword],
    "|": [nim_rule17],
    "~": [nim_rule19],
}
#@-<< nim_rules_dict >>
rulesDictDict = {
    "nim_main": nim_rules_dict,
}

# Import dict for nim mode.
importDict = {}
#@-leo

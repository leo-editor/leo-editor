# Leo colorizer control file for inform mode.
# This file is in the public domain.

# Properties for inform mode.
properties = {
    "doubleBracketIndent": "false",
    "filenameGlob": "*.(inf|h)",
    "indentCloseBrackets": "}]",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{[",
    "lineComment": "!",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for inform_main ruleset.
inform_main_attributes_dict = {
    "default": "null",
    "digit_re": "(\\$[[:xdigit:]]|[[:digit:]])",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for inform_informinnertext ruleset.
inform_informinnertext_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "(\\$[[:xdigit:]]|[[:digit:]])",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for inform mode.
attributesDictDict = {
    "inform_informinnertext": inform_informinnertext_attributes_dict,
    "inform_main": inform_main_attributes_dict,
}

# Keywords dict for inform_main ruleset.
inform_main_keywords_dict = {
    "Abbreviate": "keyword3",
    "Array": "keyword3",
    "Attribute": "keyword3",
    "Class": "keyword3",
    "Constant": "keyword3",
    "Default": "keyword3",
    "End": "keyword3",
    "Endif": "keyword3",
    "Extend": "keyword3",
    "Global": "keyword3",
    "Ifdef": "keyword3",
    "Iffalse": "keyword3",
    "Ifndef": "keyword3",
    "Ifnot": "keyword3",
    "Iftrue": "keyword3",
    "Import": "keyword3",
    "Include": "keyword3",
    "Link": "keyword3",
    "Lowstring": "keyword3",
    "Message": "keyword3",
    "Object": "keyword3",
    "Property": "keyword3",
    "Replace": "keyword3",
    "Serial": "keyword3",
    "Statusline": "keyword3",
    "Switches": "keyword3",
    "System_file": "keyword3",
    "The": "literal2",
    "Verb": "keyword3",
    "a": "literal2",
    "address": "literal2",
    "an": "literal2",
    "bold": "keyword2",
    "box": "function",
    "break": "keyword1",
    "char": "literal2",
    "continue": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "false": "literal2",
    "fixed": "keyword2",
    "font": "function",
    "for": "keyword1",
    "give": "keyword1",
    "has": "keyword1",
    "hasnt": "keyword1",
    "if": "keyword1",
    "in": "keyword1",
    "inversion": "keyword1",
    "jump": "keyword1",
    "move": "keyword1",
    "name": "literal2",
    "new_line": "function",
    "notin": "keyword1",
    "null": "literal2",
    "object": "literal2",
    "objectloop": "keyword1",
    "ofclass": "keyword1",
    "off": "keyword2",
    "on": "keyword2",
    "or": "keyword1",
    "print": "function",
    "print_ret": "function",
    "private": "keyword3",
    "property": "literal2",
    "provides": "keyword1",
    "quit": "function",
    "read": "function",
    "remove": "keyword1",
    "restore": "function",
    "return": "keyword1",
    "reverse": "keyword2",
    "rfalse": "keyword1",
    "roman": "keyword2",
    "rtrue": "keyword1",
    "save": "function",
    "score": "function",
    "self": "literal2",
    "spaces": "function",
    "string": "keyword1",
    "style": "function",
    "super": "literal2",
    "switch": "keyword1",
    "the": "literal2",
    "this": "invalid",
    "time": "function",
    "to": "keyword2",
    "true": "literal2",
    "underline": "keyword2",
    "until": "keyword1",
    "while": "keyword1",
    "with": "keyword1",
}

# Keywords dict for inform_informinnertext ruleset.
inform_informinnertext_keywords_dict = {}

# Dictionary of keywords dictionaries for inform mode.
keywordsDictDict = {
    "inform_informinnertext": inform_informinnertext_keywords_dict,
    "inform_main": inform_main_keywords_dict,
}

# Rules for inform_main ruleset.

def inform_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!")

def inform_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="inform::informinnertext")

def inform_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'", end="'")

def inform_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#")

def inform_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!")

def inform_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def inform_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def inform_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def inform_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def inform_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~=")

def inform_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def inform_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def inform_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="$")

def inform_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def inform_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def inform_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def inform_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def inform_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def inform_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def inform_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def inform_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def inform_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def inform_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def inform_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def inform_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def inform_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def inform_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".&")

def inform_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".#")

def inform_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-->")

def inform_rule29(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def inform_rule30(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="::",
          exclude_match=True)

def inform_rule31(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          exclude_match=True)

def inform_rule32(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for inform_main ruleset.
rulesDict1 = {
    "!": [inform_rule0, inform_rule4,],
    "\"": [inform_rule1,],
    "#": [inform_rule3,],
    "$": [inform_rule12,],
    "%": [inform_rule17,],
    "&": [inform_rule18,],
    "'": [inform_rule2,],
    "(": [inform_rule29,],
    "*": [inform_rule14,],
    "+": [inform_rule10,],
    "-": [inform_rule11, inform_rule28,],
    ".": [inform_rule26, inform_rule27,],
    "/": [inform_rule13,],
    "0": [inform_rule32,],
    "1": [inform_rule32,],
    "2": [inform_rule32,],
    "3": [inform_rule32,],
    "4": [inform_rule32,],
    "5": [inform_rule32,],
    "6": [inform_rule32,],
    "7": [inform_rule32,],
    "8": [inform_rule32,],
    "9": [inform_rule32,],
    ":": [inform_rule30, inform_rule31,],
    "<": [inform_rule8, inform_rule16,],
    "=": [inform_rule5, inform_rule6,],
    ">": [inform_rule7, inform_rule15,],
    "@": [inform_rule32,],
    "A": [inform_rule32,],
    "B": [inform_rule32,],
    "C": [inform_rule32,],
    "D": [inform_rule32,],
    "E": [inform_rule32,],
    "F": [inform_rule32,],
    "G": [inform_rule32,],
    "H": [inform_rule32,],
    "I": [inform_rule32,],
    "J": [inform_rule32,],
    "K": [inform_rule32,],
    "L": [inform_rule32,],
    "M": [inform_rule32,],
    "N": [inform_rule32,],
    "O": [inform_rule32,],
    "P": [inform_rule32,],
    "Q": [inform_rule32,],
    "R": [inform_rule32,],
    "S": [inform_rule32,],
    "T": [inform_rule32,],
    "U": [inform_rule32,],
    "V": [inform_rule32,],
    "W": [inform_rule32,],
    "X": [inform_rule32,],
    "Y": [inform_rule32,],
    "Z": [inform_rule32,],
    "[": [inform_rule25,],
    "]": [inform_rule24,],
    "^": [inform_rule20,],
    "_": [inform_rule32,],
    "a": [inform_rule32,],
    "b": [inform_rule32,],
    "c": [inform_rule32,],
    "d": [inform_rule32,],
    "e": [inform_rule32,],
    "f": [inform_rule32,],
    "g": [inform_rule32,],
    "h": [inform_rule32,],
    "i": [inform_rule32,],
    "j": [inform_rule32,],
    "k": [inform_rule32,],
    "l": [inform_rule32,],
    "m": [inform_rule32,],
    "n": [inform_rule32,],
    "o": [inform_rule32,],
    "p": [inform_rule32,],
    "q": [inform_rule32,],
    "r": [inform_rule32,],
    "s": [inform_rule32,],
    "t": [inform_rule32,],
    "u": [inform_rule32,],
    "v": [inform_rule32,],
    "w": [inform_rule32,],
    "x": [inform_rule32,],
    "y": [inform_rule32,],
    "z": [inform_rule32,],
    "{": [inform_rule23,],
    "|": [inform_rule19,],
    "}": [inform_rule22,],
    "~": [inform_rule9, inform_rule21,],
}

# Rules for inform_informinnertext ruleset.

def inform_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def inform_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def inform_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def inform_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def inform_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal2", seq="@@")

# Rules dict for inform_informinnertext ruleset.
rulesDict2 = {
    "@": [inform_rule35, inform_rule37,],
    "\\": [inform_rule36,],
    "^": [inform_rule33,],
    "~": [inform_rule34,],
}

# x.rulesDictDict for inform mode.
rulesDictDict = {
    "inform_informinnertext": rulesDict2,
    "inform_main": rulesDict1,
}

# Import dict for inform mode.
importDict = {}

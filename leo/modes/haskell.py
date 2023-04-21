# Leo colorizer control file for haskell mode.
# This file is in the public domain.

# Properties for haskell mode.
properties = {
    "commentEnd": "-}",
    "commentStart": "{-",
    "indentSize": "8",
    "lineComment": "--",
    "tabSize": "8",
}

# Attributes dict for haskell_main ruleset.
haskell_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for haskell mode.
attributesDictDict = {
    "haskell_main": haskell_main_attributes_dict,
}

# Keywords dict for haskell_main ruleset.
haskell_main_keywords_dict = {
    ":": "literal2",
    "Addr": "keyword3",
    "Bool": "keyword3",
    "Bounded": "keyword3",
    "Char": "keyword3",
    "Double": "keyword3",
    "EQ": "literal2",
    "Either": "keyword3",
    "Enum": "keyword3",
    "Eq": "keyword3",
    "False": "literal2",
    "FilePath": "keyword3",
    "Float": "keyword3",
    "Floating": "keyword3",
    "Fractional": "keyword3",
    "Functor": "keyword3",
    "GT": "literal2",
    "IO": "keyword3",
    "IOError": "keyword3",
    "IOResult": "keyword3",
    "Int": "keyword3",
    "Integer": "keyword3",
    "Integral": "keyword3",
    "Ix": "keyword3",
    "Just": "literal2",
    "LT": "literal2",
    "Left": "literal2",
    "Maybe": "keyword3",
    "Monad": "keyword3",
    "Nothing": "literal2",
    "Num": "keyword3",
    "Ord": "keyword3",
    "Ordering": "keyword3",
    "Ratio": "keyword3",
    "Rational": "keyword3",
    "Read": "keyword3",
    "ReadS": "keyword3",
    "Real": "keyword3",
    "RealFloat": "keyword3",
    "RealFrac": "keyword3",
    "Right": "literal2",
    "Show": "keyword3",
    "ShowS": "keyword3",
    "String": "keyword3",
    "True": "literal2",
    "_": "keyword1",
    "as": "keyword1",
    "case": "keyword1",
    "class": "keyword1",
    "data": "keyword1",
    "default": "keyword1",
    "deriving": "keyword1",
    "div": "operator",
    "do": "keyword1",
    "elem": "operator",
    "else": "keyword1",
    "hiding": "keyword1",
    "if": "keyword1",
    "import": "keyword1",
    "in": "keyword1",
    "infix": "keyword1",
    "infixl": "keyword1",
    "infixr": "keyword1",
    "instance": "keyword1",
    "let": "keyword1",
    "mod": "operator",
    "module": "keyword1",
    "newtype": "keyword1",
    "notElem": "operator",
    "of": "keyword1",
    "qualified": "keyword1",
    "quot": "operator",
    "rem": "operator",
    "seq": "operator",
    "then": "keyword1",
    "type": "keyword1",
    "where": "keyword1",
}

# Dictionary of keywords dictionaries for haskell mode.
keywordsDictDict = {
    "haskell_main": haskell_main_keywords_dict,
}

# Rules for haskell_main ruleset.

def haskell_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="{-#", end="#-}")

def haskell_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="{-", end="-}")

def haskell_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def haskell_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def haskell_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="' '")

def haskell_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'!'")

def haskell_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'\"'")

def haskell_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'$'")

def haskell_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'%'")

def haskell_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'/'")

def haskell_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'('")

def haskell_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="')'")

def haskell_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'['")

def haskell_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="']'")

def haskell_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'+'")

def haskell_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'-'")

def haskell_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'*'")

def haskell_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'='")

def haskell_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'/'")

def haskell_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'^'")

def haskell_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'.'")

def haskell_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="','")

def haskell_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="':'")

def haskell_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="';'")

def haskell_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'<'")

def haskell_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'>'")

def haskell_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'|'")

def haskell_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="'@'")

def haskell_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",



        ### no_word_break=True)
        )

def haskell_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="..")

def haskell_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&&")

def haskell_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="::")

def haskell_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def haskell_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def haskell_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def haskell_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def haskell_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def haskell_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def haskell_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def haskell_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def haskell_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def haskell_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def haskell_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def haskell_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def haskell_rule44(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def haskell_rule45(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="$")

def haskell_rule46(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for haskell_main ruleset.
rulesDict1 = {
    "!": [haskell_rule44,],
    "\"": [haskell_rule3,],
    "$": [haskell_rule45,],
    "%": [haskell_rule38,],
    "&": [haskell_rule30,],
    "'": [haskell_rule4, haskell_rule5, haskell_rule6, haskell_rule7, haskell_rule8, haskell_rule9, haskell_rule10,
        haskell_rule11, haskell_rule12, haskell_rule13, haskell_rule14, haskell_rule15, haskell_rule16, haskell_rule17,
        haskell_rule18, haskell_rule19, haskell_rule20, haskell_rule21, haskell_rule22, haskell_rule23, haskell_rule24,
        haskell_rule25, haskell_rule26, haskell_rule27, haskell_rule28,],
    "*": [haskell_rule36,],
    "+": [haskell_rule34,],
    "-": [haskell_rule2, haskell_rule35,],
    ".": [haskell_rule29,],
    "/": [haskell_rule37,],

# Bizarre.
    "0": [haskell_rule46,],
    "1": [haskell_rule46,],
    "2": [haskell_rule46,],
    "3": [haskell_rule46,],
    "4": [haskell_rule46,],
    "5": [haskell_rule46,],
    "6": [haskell_rule46,],
    "7": [haskell_rule46,],
    "8": [haskell_rule46,],
    "9": [haskell_rule46,],
#    ":": [haskell_rule31,haskell_rule46,],
    ":": [haskell_rule31,],
    "<": [haskell_rule32,],
    "=": [haskell_rule40,],
    ">": [haskell_rule33,],
#    "@": [haskell_rule42,haskell_rule46,],
    "@": [haskell_rule42,],
    "A": [haskell_rule46,],
    "B": [haskell_rule46,],
    "C": [haskell_rule46,],
    "D": [haskell_rule46,],
    "E": [haskell_rule46,],
    "F": [haskell_rule46,],
    "G": [haskell_rule46,],
    "H": [haskell_rule46,],
    "I": [haskell_rule46,],
    "J": [haskell_rule46,],
    "K": [haskell_rule46,],
    "L": [haskell_rule46,],
    "M": [haskell_rule46,],
    "N": [haskell_rule46,],
    "O": [haskell_rule46,],
    "P": [haskell_rule46,],
    "Q": [haskell_rule46,],
    "R": [haskell_rule46,],
    "S": [haskell_rule46,],
    "T": [haskell_rule46,],
    "U": [haskell_rule46,],
    "V": [haskell_rule46,],
    "W": [haskell_rule46,],
    "X": [haskell_rule46,],
    "Y": [haskell_rule46,],
    "Z": [haskell_rule46,],
    "^": [haskell_rule39,],
    "_": [haskell_rule46,],
    "a": [haskell_rule46,],
    "b": [haskell_rule46,],
    "c": [haskell_rule46,],
    "d": [haskell_rule46,],
    "e": [haskell_rule46,],
    "f": [haskell_rule46,],
    "g": [haskell_rule46,],
    "h": [haskell_rule46,],
    "i": [haskell_rule46,],
    "j": [haskell_rule46,],
    "k": [haskell_rule46,],
    "l": [haskell_rule46,],
    "m": [haskell_rule46,],
    "n": [haskell_rule46,],
    "o": [haskell_rule46,],
    "p": [haskell_rule46,],
    "q": [haskell_rule46,],
    "r": [haskell_rule46,],
    "s": [haskell_rule46,],
    "t": [haskell_rule46,],
    "u": [haskell_rule46,],
    "v": [haskell_rule46,],
    "w": [haskell_rule46,],
    "x": [haskell_rule46,],
    "y": [haskell_rule46,],
    "z": [haskell_rule46,],
    "{": [haskell_rule0, haskell_rule1,],
    "|": [haskell_rule41,],
    "~": [haskell_rule43,],
}

# x.rulesDictDict for haskell mode.
rulesDictDict = {
    "haskell_main": rulesDict1,
}

# Import dict for haskell mode.
importDict = {}

# Leo colorizer control file for coffeescript mode.
# This file is in the public domain.

# Properties for coffeescript mode.
properties = {
    "commentEnd": "###",
    "commentStart": "###",
    "indentNextLines": "((\\s*|.*\\s+)([\\-=]>|[\\+\\-\\*/%\\\\<>=\\!&\\|\\^~]|(.*:|<<|>>|>>>|\\+=|\\-=|\\*=|/=|%=|<=|>=|==|===|\\!=|\\!==|is|isnt|not|and|or|&&|\\|\\||of|in|loop))|\\s*(if|else|try|catch|finally|class|while|until|for)(\\s*|\\s+.*))\\s*",
    "lineComment": "#",
    "unindentNextLines": "^\\s*(else|catch|finally)(\\s*|\\s+.*)$",
    "unindentThisLine": "^\\s*(else|catch|finally)(\\s*|\\s+.*)$",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for coffeescript_main ruleset.
coffeescript_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0b[01]+)|(0o[0-7]+)|(0x\\p{XDigit}+)|(\\d*\\.?\\d+(e[+-]?\\d+)?)",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "$_",
}

# Attributes dict for coffeescript_doublequoteliteral ruleset.
coffeescript_doublequoteliteral_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "(0b[01]+)|(0o[0-7]+)|(0x\\p{XDigit}+)|(\\d*\\.?\\d+(e[+-]?\\d+)?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "$_",
}

# Attributes dict for coffeescript_hereregexp ruleset.
coffeescript_hereregexp_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "(0b[01]+)|(0o[0-7]+)|(0x\\p{XDigit}+)|(\\d*\\.?\\d+(e[+-]?\\d+)?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "$_",
}

# Dictionary of attributes dictionaries for coffeescript mode.
attributesDictDict = {
    "coffeescript_doublequoteliteral": coffeescript_doublequoteliteral_attributes_dict,
    "coffeescript_hereregexp": coffeescript_hereregexp_attributes_dict,
    "coffeescript_main": coffeescript_main_attributes_dict,
}

# Keywords dict for coffeescript_main ruleset.
coffeescript_main_keywords_dict = {
    "Array": "keyword3",
    "Boolean": "keyword3",
    "Date": "keyword3",
    "Function": "keyword3",
    "Global": "keyword3",
    "Infinity": "literal2",
    "Math": "keyword3",
    "NaN": "literal2",
    "Number": "keyword3",
    "Object": "keyword3",
    "RegExp": "keyword3",
    "String": "keyword3",
    "and": "keyword1",
    "break": "keyword1",
    "by": "keyword1",
    "catch": "keyword1",
    "class": "keyword1",
    "constructor": "keyword1",
    "continue": "keyword1",
    "delete": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "escape": "literal2",
    "eval": "literal2",
    "extends": "keyword1",
    "false": "literal2",
    "finally": "keyword1",
    "for": "keyword1",
    "if": "keyword1",
    "in": "keyword1",
    "instanceof": "keyword1",
    "is": "keyword1",
    "isFinite": "literal2",
    "isNaN": "literal2",
    "isnt": "keyword1",
    "loop": "keyword1",
    "new": "keyword1",
    "no": "literal2",
    "not": "keyword1",
    "null": "literal2",
    "of": "keyword1",
    "off": "literal2",
    "on": "literal2",
    "or": "keyword1",
    "parseFloat": "literal2",
    "parseInt": "literal2",
    "prototype": "keyword3",
    "return": "keyword1",
    "super": "keyword3",
    "switch": "keyword1",
    "then": "keyword1",
    "this": "keyword3",
    "throw": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "typeof": "keyword1",
    "undefined": "literal2",
    "unescape": "literal2",
    "unless": "keyword1",
    "until": "keyword1",
    "when": "keyword1",
    "while": "keyword1",
    "yes": "literal2",
}

# Keywords dict for coffeescript_doublequoteliteral ruleset.
coffeescript_doublequoteliteral_keywords_dict = {}

# Keywords dict for coffeescript_hereregexp ruleset.
coffeescript_hereregexp_keywords_dict = {}

# Dictionary of keywords dictionaries for coffeescript mode.
keywordsDictDict = {
    "coffeescript_doublequoteliteral": coffeescript_doublequoteliteral_keywords_dict,
    "coffeescript_hereregexp": coffeescript_hereregexp_keywords_dict,
    "coffeescript_main": coffeescript_main_keywords_dict,
}

# Rules for coffeescript_main ruleset.

def coffeescript_rule0(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="comment2", begin="###(?!#)", end="#{3,}")

def coffeescript_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def coffeescript_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"\"\"", end="\"\"\"",
          delegate="coffeescript::doublequoteliteral")

def coffeescript_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'''", end="'''")

def coffeescript_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="coffeescript::doublequoteliteral")

def coffeescript_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'", end="'")

def coffeescript_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="`", end="`",
          delegate="javascript::main")

def coffeescript_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="///", end="///",
          delegate="coffeescript::hereregexp")

def coffeescript_rule8(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="markup", begin="/(?![\\s=*])", end="/[igmy]{0,4}",
          no_line_break=True)

def coffeescript_rule9(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(")

def coffeescript_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def coffeescript_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def coffeescript_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def coffeescript_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def coffeescript_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def coffeescript_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def coffeescript_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def coffeescript_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def coffeescript_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def coffeescript_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def coffeescript_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def coffeescript_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def coffeescript_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def coffeescript_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def coffeescript_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def coffeescript_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def coffeescript_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def coffeescript_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def coffeescript_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def coffeescript_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def coffeescript_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def coffeescript_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def coffeescript_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def coffeescript_rule33(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword3", regexp="@([a-zA-Z\\$_][a-zA-Z0-9\\$_]*)")

def coffeescript_rule34(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword4", regexp="([a-zA-Z\\$_][a-zA-Z0-9\\$_]*)(?=\\s*(?:[:\\.]|\\?\\.))")

def coffeescript_rule35(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp="for\\s+own(?![a-zA-Z0-9\\$_])")

def coffeescript_rule36(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for coffeescript_main ruleset.
rulesDict1 = {
    "!": [coffeescript_rule28,],
    "\"": [coffeescript_rule2, coffeescript_rule4,],
    "#": [coffeescript_rule0, coffeescript_rule1,],
    "%": [coffeescript_rule23,],
    "&": [coffeescript_rule19,],
    "'": [coffeescript_rule3, coffeescript_rule5,],
    "(": [coffeescript_rule9, coffeescript_rule34,],
    ")": [coffeescript_rule10,],
    "*": [coffeescript_rule18,],
    "+": [coffeescript_rule16,],
    "-": [coffeescript_rule22,],
    ".": [coffeescript_rule15,],
    "/": [coffeescript_rule7, coffeescript_rule8, coffeescript_rule17,],
    "0": [coffeescript_rule36,],
    "1": [coffeescript_rule36,],
    "2": [coffeescript_rule36,],
    "3": [coffeescript_rule36,],
    "4": [coffeescript_rule36,],
    "5": [coffeescript_rule36,],
    "6": [coffeescript_rule36,],
    "7": [coffeescript_rule36,],
    "8": [coffeescript_rule36,],
    "9": [coffeescript_rule36,],
    ":": [coffeescript_rule27,],
    ";": [coffeescript_rule29,],
    "<": [coffeescript_rule25,],
    "=": [coffeescript_rule24,],
    ">": [coffeescript_rule26,],
    "?": [coffeescript_rule32,],
    "@": [coffeescript_rule33, coffeescript_rule36,],
    "A": [coffeescript_rule36,],
    "B": [coffeescript_rule36,],
    "C": [coffeescript_rule36,],
    "D": [coffeescript_rule36,],
    "E": [coffeescript_rule36,],
    "F": [coffeescript_rule36,],
    "G": [coffeescript_rule36,],
    "H": [coffeescript_rule36,],
    "I": [coffeescript_rule36,],
    "J": [coffeescript_rule36,],
    "K": [coffeescript_rule36,],
    "L": [coffeescript_rule36,],
    "M": [coffeescript_rule36,],
    "N": [coffeescript_rule36,],
    "O": [coffeescript_rule36,],
    "P": [coffeescript_rule36,],
    "Q": [coffeescript_rule36,],
    "R": [coffeescript_rule36,],
    "S": [coffeescript_rule36,],
    "T": [coffeescript_rule36,],
    "U": [coffeescript_rule36,],
    "V": [coffeescript_rule36,],
    "W": [coffeescript_rule36,],
    "X": [coffeescript_rule36,],
    "Y": [coffeescript_rule36,],
    "Z": [coffeescript_rule36,],
    "[": [coffeescript_rule13,],
    "\\": [coffeescript_rule21,],
    "]": [coffeescript_rule14,],
    "^": [coffeescript_rule30,],
    "`": [coffeescript_rule6,],
    "a": [coffeescript_rule36,],
    "b": [coffeescript_rule36,],
    "c": [coffeescript_rule36,],
    "d": [coffeescript_rule36,],
    "e": [coffeescript_rule36,],
    "f": [coffeescript_rule35, coffeescript_rule36,],
    "g": [coffeescript_rule36,],
    "h": [coffeescript_rule36,],
    "i": [coffeescript_rule36,],
    "j": [coffeescript_rule36,],
    "k": [coffeescript_rule36,],
    "l": [coffeescript_rule36,],
    "m": [coffeescript_rule36,],
    "n": [coffeescript_rule36,],
    "o": [coffeescript_rule36,],
    "p": [coffeescript_rule36,],
    "q": [coffeescript_rule36,],
    "r": [coffeescript_rule36,],
    "s": [coffeescript_rule36,],
    "t": [coffeescript_rule36,],
    "u": [coffeescript_rule36,],
    "v": [coffeescript_rule36,],
    "w": [coffeescript_rule36,],
    "x": [coffeescript_rule36,],
    "y": [coffeescript_rule36,],
    "z": [coffeescript_rule36,],
    "{": [coffeescript_rule11,],
    "|": [coffeescript_rule20,],
    "}": [coffeescript_rule12,],
    "~": [coffeescript_rule31,],
}

# Rules for coffeescript_doublequoteliteral ruleset.

def coffeescript_rule37(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="#{", end="}",
          delegate="coffeescript::main")

# Rules dict for coffeescript_doublequoteliteral ruleset.
rulesDict2 = {
    "#": [coffeescript_rule37,],
}

# Rules for coffeescript_hereregexp ruleset.

def coffeescript_rule38(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="#{", end="}",
          delegate="coffeescript::main")

def coffeescript_rule39(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

# Rules dict for coffeescript_hereregexp ruleset.
rulesDict3 = {
    "#": [coffeescript_rule38, coffeescript_rule39,],
}

# x.rulesDictDict for coffeescript mode.
rulesDictDict = {
    "coffeescript_doublequoteliteral": rulesDict2,
    "coffeescript_hereregexp": rulesDict3,
    "coffeescript_main": rulesDict1,
}

# Import dict for coffeescript mode.
importDict = {}

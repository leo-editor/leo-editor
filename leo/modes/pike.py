# Leo colorizer control file for pike mode.
# This file is in the public domain.

# Properties for pike mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|(for(each)?)|while|catch|gauge)\\s*\\(|(do|else)\\s*|else\\s+if\\s*\\()[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*`",
}

# Attributes dict for pike_main ruleset.
pike_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+|[[:digit]]+|0[bB][01]+)[lLdDfF]?",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pike_comment ruleset.
pike_comment_attributes_dict = {
    "default": "COMMENT1",
    "digit_re": "(0x[[:xdigit:]]+|[[:digit]]+|0[bB][01]+)[lLdDfF]?",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pike_autodoc ruleset.
pike_autodoc_attributes_dict = {
    "default": "COMMENT1",
    "digit_re": "(0x[[:xdigit:]]+|[[:digit]]+|0[bB][01]+)[lLdDfF]?",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for pike_string_literal ruleset.
pike_string_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "(0x[[:xdigit:]]+|[[:digit]]+|0[bB][01]+)[lLdDfF]?",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for pike mode.
attributesDictDict = {
    "pike_autodoc": pike_autodoc_attributes_dict,
    "pike_comment": pike_comment_attributes_dict,
    "pike_main": pike_main_attributes_dict,
    "pike_string_literal": pike_string_literal_attributes_dict,
}

# Keywords dict for pike_main ruleset.
pike_main_keywords_dict = {
    "array": "keyword3",
    "break": "keyword1",
    "case": "keyword1",
    "catch": "keyword1",
    "class": "keyword3",
    "constant": "keyword1",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "extern": "keyword1",
    "final": "keyword1",
    "float": "keyword3",
    "for": "keyword1",
    "foreach": "keyword1",
    "function": "keyword3",
    "gauge": "keyword1",
    "if": "keyword1",
    "import": "keyword2",
    "inherit": "keyword2",
    "inline": "keyword1",
    "int": "keyword3",
    "lambda": "keyword1",
    "local": "keyword1",
    "mapping": "keyword3",
    "mixed": "keyword3",
    "multiset": "keyword3",
    "nomask": "keyword1",
    "object": "keyword3",
    "optional": "keyword1",
    "private": "keyword1",
    "program": "keyword3",
    "protected": "keyword1",
    "public": "keyword1",
    "return": "keyword1",
    "sscanf": "keyword1",
    "static": "keyword1",
    "string": "keyword3",
    "switch": "keyword1",
    "variant": "keyword1",
    "void": "keyword3",
    "while": "keyword1",
}

# Keywords dict for pike_comment ruleset.
# pylint: disable=fixme
pike_comment_keywords_dict = {
    "FIXME": "comment2",
    "XXX": "comment2",
}

# Keywords dict for pike_autodoc ruleset.
pike_autodoc_keywords_dict = {
    "@appears": "label",
    "@array": "label",
    "@belongs": "label",
    "@bugs": "label",
    "@class": "label",
    "@constant": "label",
    "@deprecated": "label",
    "@dl": "label",
    "@elem": "label",
    "@endarray": "label",
    "@endclass": "label",
    "@enddl": "label",
    "@endignore": "label",
    "@endint": "label",
    "@endmapping": "label",
    "@endmixed": "label",
    "@endmodule": "label",
    "@endmultiset": "label",
    "@endnamespace": "label",
    "@endol": "label",
    "@endstring": "label",
    "@example": "label",
    "@fixme": "label",
    "@ignore": "label",
    "@index": "label",
    "@int": "label",
    "@item": "label",
    "@mapping": "label",
    "@member": "label",
    "@mixed": "label",
    "@module": "label",
    "@multiset": "label",
    "@namespace": "label",
    "@note": "label",
    "@ol": "label",
    "@param": "label",
    "@returns": "label",
    "@section": "label",
    "@seealso": "label",
    "@string": "label",
    "@throws": "label",
    "@type": "label",
    "@ul": "label",
    "@value": "label",
}

# Keywords dict for pike_string_literal ruleset.
pike_string_literal_keywords_dict = {}

# Dictionary of keywords dictionaries for pike mode.
keywordsDictDict = {
    "pike_autodoc": pike_autodoc_keywords_dict,
    "pike_comment": pike_comment_keywords_dict,
    "pike_main": pike_main_keywords_dict,
    "pike_string_literal": pike_string_literal_keywords_dict,
}

# Rules for pike_main ruleset.

def pike_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/",
          delegate="pike::comment")

def pike_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="*/")

def pike_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//!",
          delegate="pike::autodoc")

def pike_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//",
          delegate="pike::comment")

def pike_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="pike::string_literal",
          no_line_break=True)

def pike_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="#\"", end="\"",
          delegate="pike::string_literal")

def pike_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def pike_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="#.*?(?=($|/\\*|//))",
          at_line_start=True)

def pike_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="({")

def pike_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="})")

def pike_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="([")

def pike_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="])")

def pike_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(<")

def pike_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">)")

def pike_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def pike_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def pike_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def pike_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def pike_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def pike_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def pike_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def pike_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def pike_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def pike_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def pike_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def pike_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def pike_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def pike_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def pike_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="`")

def pike_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def pike_rule30(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def pike_rule31(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for pike_main ruleset.
rulesDict1 = {
    "!": [pike_rule15,],
    "\"": [pike_rule4,],
    "#": [pike_rule5, pike_rule7,],
    "%": [pike_rule22,],
    "&": [pike_rule23,],
    "'": [pike_rule6,],
    "(": [pike_rule8, pike_rule10, pike_rule12, pike_rule30,],
    "*": [pike_rule1, pike_rule19,],
    "+": [pike_rule16,],
    "-": [pike_rule17,],
    ".": [pike_rule29,],
    "/": [pike_rule0, pike_rule2, pike_rule3, pike_rule18,],
    "0": [pike_rule31,],
    "1": [pike_rule31,],
    "2": [pike_rule31,],
    "3": [pike_rule31,],
    "4": [pike_rule31,],
    "5": [pike_rule31,],
    "6": [pike_rule31,],
    "7": [pike_rule31,],
    "8": [pike_rule31,],
    "9": [pike_rule31,],
    "<": [pike_rule21,],
    "=": [pike_rule14,],
    ">": [pike_rule13, pike_rule20,],
    "@": [pike_rule27, pike_rule31,],
    "A": [pike_rule31,],
    "B": [pike_rule31,],
    "C": [pike_rule31,],
    "D": [pike_rule31,],
    "E": [pike_rule31,],
    "F": [pike_rule31,],
    "G": [pike_rule31,],
    "H": [pike_rule31,],
    "I": [pike_rule31,],
    "J": [pike_rule31,],
    "K": [pike_rule31,],
    "L": [pike_rule31,],
    "M": [pike_rule31,],
    "N": [pike_rule31,],
    "O": [pike_rule31,],
    "P": [pike_rule31,],
    "Q": [pike_rule31,],
    "R": [pike_rule31,],
    "S": [pike_rule31,],
    "T": [pike_rule31,],
    "U": [pike_rule31,],
    "V": [pike_rule31,],
    "W": [pike_rule31,],
    "X": [pike_rule31,],
    "Y": [pike_rule31,],
    "Z": [pike_rule31,],
    "]": [pike_rule11,],
    "^": [pike_rule25,],
    "`": [pike_rule28,],
    "a": [pike_rule31,],
    "b": [pike_rule31,],
    "c": [pike_rule31,],
    "d": [pike_rule31,],
    "e": [pike_rule31,],
    "f": [pike_rule31,],
    "g": [pike_rule31,],
    "h": [pike_rule31,],
    "i": [pike_rule31,],
    "j": [pike_rule31,],
    "k": [pike_rule31,],
    "l": [pike_rule31,],
    "m": [pike_rule31,],
    "n": [pike_rule31,],
    "o": [pike_rule31,],
    "p": [pike_rule31,],
    "q": [pike_rule31,],
    "r": [pike_rule31,],
    "s": [pike_rule31,],
    "t": [pike_rule31,],
    "u": [pike_rule31,],
    "v": [pike_rule31,],
    "w": [pike_rule31,],
    "x": [pike_rule31,],
    "y": [pike_rule31,],
    "z": [pike_rule31,],
    "|": [pike_rule24,],
    "}": [pike_rule9,],
    "~": [pike_rule26,],
}

# Rules for pike_comment ruleset.

def pike_rule32(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for pike_comment ruleset.
rulesDict2 = {
    "0": [pike_rule32,],
    "1": [pike_rule32,],
    "2": [pike_rule32,],
    "3": [pike_rule32,],
    "4": [pike_rule32,],
    "5": [pike_rule32,],
    "6": [pike_rule32,],
    "7": [pike_rule32,],
    "8": [pike_rule32,],
    "9": [pike_rule32,],
    "@": [pike_rule32,],
    "A": [pike_rule32,],
    "B": [pike_rule32,],
    "C": [pike_rule32,],
    "D": [pike_rule32,],
    "E": [pike_rule32,],
    "F": [pike_rule32,],
    "G": [pike_rule32,],
    "H": [pike_rule32,],
    "I": [pike_rule32,],
    "J": [pike_rule32,],
    "K": [pike_rule32,],
    "L": [pike_rule32,],
    "M": [pike_rule32,],
    "N": [pike_rule32,],
    "O": [pike_rule32,],
    "P": [pike_rule32,],
    "Q": [pike_rule32,],
    "R": [pike_rule32,],
    "S": [pike_rule32,],
    "T": [pike_rule32,],
    "U": [pike_rule32,],
    "V": [pike_rule32,],
    "W": [pike_rule32,],
    "X": [pike_rule32,],
    "Y": [pike_rule32,],
    "Z": [pike_rule32,],
    "a": [pike_rule32,],
    "b": [pike_rule32,],
    "c": [pike_rule32,],
    "d": [pike_rule32,],
    "e": [pike_rule32,],
    "f": [pike_rule32,],
    "g": [pike_rule32,],
    "h": [pike_rule32,],
    "i": [pike_rule32,],
    "j": [pike_rule32,],
    "k": [pike_rule32,],
    "l": [pike_rule32,],
    "m": [pike_rule32,],
    "n": [pike_rule32,],
    "o": [pike_rule32,],
    "p": [pike_rule32,],
    "q": [pike_rule32,],
    "r": [pike_rule32,],
    "s": [pike_rule32,],
    "t": [pike_rule32,],
    "u": [pike_rule32,],
    "v": [pike_rule32,],
    "w": [pike_rule32,],
    "x": [pike_rule32,],
    "y": [pike_rule32,],
    "z": [pike_rule32,],
}

# Rules for pike_autodoc ruleset.

def pike_rule33(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq="@decl",
          delegate="pike::main",
          exclude_match=True)

def pike_rule34(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="@xml{", end="@}",
          delegate="xml::tags")

def pike_rule35(colorer, s, i):
    return colorer.match_span(s, i, kind="function", begin="@[", end="]",
          no_line_break=True)

def pike_rule36(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="function", regexp="@(b|i|u|tt|url|pre|ref|code|expr|image)?(\\{.*@\\})")

def pike_rule37(colorer, s, i):
    return colorer.match_keywords(s, i)

def pike_rule38(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq="@decl",
          delegate="pike::main")

# Rules dict for pike_autodoc ruleset.
rulesDict3 = {
    "0": [pike_rule37,],
    "1": [pike_rule37,],
    "2": [pike_rule37,],
    "3": [pike_rule37,],
    "4": [pike_rule37,],
    "5": [pike_rule37,],
    "6": [pike_rule37,],
    "7": [pike_rule37,],
    "8": [pike_rule37,],
    "9": [pike_rule37,],
    "@": [pike_rule33, pike_rule34, pike_rule35, pike_rule36, pike_rule37, pike_rule38,],
    "A": [pike_rule37,],
    "B": [pike_rule37,],
    "C": [pike_rule37,],
    "D": [pike_rule37,],
    "E": [pike_rule37,],
    "F": [pike_rule37,],
    "G": [pike_rule37,],
    "H": [pike_rule37,],
    "I": [pike_rule37,],
    "J": [pike_rule37,],
    "K": [pike_rule37,],
    "L": [pike_rule37,],
    "M": [pike_rule37,],
    "N": [pike_rule37,],
    "O": [pike_rule37,],
    "P": [pike_rule37,],
    "Q": [pike_rule37,],
    "R": [pike_rule37,],
    "S": [pike_rule37,],
    "T": [pike_rule37,],
    "U": [pike_rule37,],
    "V": [pike_rule37,],
    "W": [pike_rule37,],
    "X": [pike_rule37,],
    "Y": [pike_rule37,],
    "Z": [pike_rule37,],
    "a": [pike_rule37,],
    "b": [pike_rule37,],
    "c": [pike_rule37,],
    "d": [pike_rule37,],
    "e": [pike_rule37,],
    "f": [pike_rule37,],
    "g": [pike_rule37,],
    "h": [pike_rule37,],
    "i": [pike_rule37,],
    "j": [pike_rule37,],
    "k": [pike_rule37,],
    "l": [pike_rule37,],
    "m": [pike_rule37,],
    "n": [pike_rule37,],
    "o": [pike_rule37,],
    "p": [pike_rule37,],
    "q": [pike_rule37,],
    "r": [pike_rule37,],
    "s": [pike_rule37,],
    "t": [pike_rule37,],
    "u": [pike_rule37,],
    "v": [pike_rule37,],
    "w": [pike_rule37,],
    "x": [pike_rule37,],
    "y": [pike_rule37,],
    "z": [pike_rule37,],
}

# Rules for pike_string_literal ruleset.

def pike_rule39(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="%([^ a-z]*[a-z]|\\[[^\\]]*\\])")

def pike_rule40(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="comment2", regexp="DEBUG:")

# Rules dict for pike_string_literal ruleset.
rulesDict4 = {
    "%": [pike_rule39,],
    "D": [pike_rule40,],
}

# x.rulesDictDict for pike mode.
rulesDictDict = {
    "pike_autodoc": rulesDict3,
    "pike_comment": rulesDict2,
    "pike_main": rulesDict1,
    "pike_string_literal": rulesDict4,
}

# Import dict for pike mode.
importDict = {}

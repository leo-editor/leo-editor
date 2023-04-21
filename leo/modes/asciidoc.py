# Leo colorizer control file for asciidoc mode.
# This file is in the public domain.

# Changes from asciidoc.xml:
# - Use "markup" rather than "function" tag.

# Properties for asciidoc mode.
properties = {
        "commentEnd": "*/",
        "commentStart": "/*",
        "contextInsensitive": "true",
        "lineComment": "//",
}

# Attributes dict for asciidoc_main ruleset.
asciidoc_main_attributes_dict = {
        "default": "null",
        "digit_re": "",
        "escape": "",
        "highlight_digits": "true",
        "ignore_case": "true",
        "no_word_sep": "",
}

# Dictionary of attributes dictionaries for asciidoc mode.
attributesDictDict = {
        "asciidoc_main": asciidoc_main_attributes_dict,
}

# Keywords dict for asciidoc_main ruleset.
asciidoc_main_keywords_dict = {
        "asciimath": "keyword2",
        "endif": "keyword3",
        "eval": "keyword1",
        "footnote:": "keyword2",
        "footnoteref": "keyword2",
        "ifdef": "keyword3",
        "ifndef": "keyword3",
        "image:": "keyword1",
        "include:": "keyword1",
        "indexterm2|": "keyword2",
        "indexterm:": "keyword2",
        "latexmath": "keyword2",
        "pass:": "keyword2",
        "sys": "keyword1",
        "sys2": "keyword1",
        "template": "keyword3",
        "unfloat": "keyword3",
}

# Dictionary of keywords dictionaries for asciidoc mode.
keywordsDictDict = {
        "asciidoc_main": asciidoc_main_keywords_dict,
}

# Rules for asciidoc_main ruleset.

def asciidoc_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="=====",
          at_line_start=True)

def asciidoc_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="====",
          at_line_start=True)

def asciidoc_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="===",
          at_line_start=True)

def asciidoc_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="==",
          at_line_start=True)

def asciidoc_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="=",
          at_line_start=True)

def asciidoc_rule5(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="markup", regexp="^[=-]{4,}",
          at_line_start=True)

def asciidoc_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="~~~~",
          at_line_start=True)

def asciidoc_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="^^^^",
          at_line_start=True)

def asciidoc_rule8(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="++++",
          at_line_start=True)

def asciidoc_rule9(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="comment2", begin="^\\/\\/\\/\\/+\\s*$", end="\\/\\/\\/\\/\\s*$",
          at_line_start=True)

def asciidoc_rule10(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq="//")

def asciidoc_rule11(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal1", begin="^----+\\s*$", end="----\\s*$",
          at_line_start=True)

def asciidoc_rule12(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal2", begin="^\\+\\+\\+\\++\\s*$", end="\\+\\+\\+\\+\\s*$",
          at_line_start=True)

def asciidoc_rule13(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal3", begin="^\\.\\.\\.\\.+\\s*$", end="\\.\\.\\.\\.\\s*$",
          at_line_start=True)

def asciidoc_rule14(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal4", begin="^\\*\\*\\*\\*+\\s*$", end="\\*\\*\\*\\*\\s*$",
          at_line_start=True)

def asciidoc_rule15(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="comment4", begin="^____+\\s*$", end="____\\s*$",
          at_line_start=True)

def asciidoc_rule16(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="^\\s*\\S+:.+\\[")

def asciidoc_rule17(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="^\\s*\\S+::.+\\[")

def asciidoc_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="[[", end="]]",
          at_line_start=True)

def asciidoc_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<<", end=">>")

def asciidoc_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="[", end="]",
          at_line_start=True)

def asciidoc_rule21(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="literal1", regexp="^:.{1,20}:")

def asciidoc_rule22(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="comment1", begin="(^|[\\s\\.,\\(\\)\\[\\]])_\\S", end="_")

def asciidoc_rule23(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="comment1", begin="(^|[\\s\\.,\\(\\)\\[\\]])'\\S", end="'")

def asciidoc_rule24(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="(^|[\\s\\.,\\(])\\*[^\\*\\s]", end="*")

def asciidoc_rule25(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="(^|[\\s\\.,\\(])`\\S", end="`")

def asciidoc_rule26(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="(^|[\\s\\.,\\(])\\+\\S", end="+")

def asciidoc_rule27(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="-",
          at_line_start=True)

def asciidoc_rule28(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="*",
          at_line_start=True)

def asciidoc_rule29(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="**",
          at_line_start=True)

def asciidoc_rule30(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="***",
          at_line_start=True)

def asciidoc_rule31(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="****",
          at_line_start=True)

def asciidoc_rule32(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="*****",
          at_line_start=True)

def asciidoc_rule33(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=".",
          at_line_start=True)

def asciidoc_rule34(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="..",
          at_line_start=True)

def asciidoc_rule35(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="...",
          at_line_start=True)

def asciidoc_rule36(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="....",
          at_line_start=True)

def asciidoc_rule37(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=".....",
          at_line_start=True)

def asciidoc_rule38(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="comment4", pattern="::",
          at_whitespace_end=True)

def asciidoc_rule39(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="comment4", pattern=":::",
          at_whitespace_end=True)

def asciidoc_rule40(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="comment4", pattern="::::",
          at_whitespace_end=True)

def asciidoc_rule41(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="^\\.\\S",
          at_line_start=True)

def asciidoc_rule42(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="markup", begin="\\s*NOTE:", end=" ",
          at_line_start=True)

def asciidoc_rule43(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="operator", seq="|==",
          at_line_start=True)

def asciidoc_rule44(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="digit", pattern="|")

def asciidoc_rule45(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="NOTE:", end=" ",
          at_line_start=True)

def asciidoc_rule46(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="(((", end=")))")

def asciidoc_rule47(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for asciidoc_main ruleset.
rulesDict1 = {
        "(": [asciidoc_rule22, asciidoc_rule23, asciidoc_rule24, asciidoc_rule25, asciidoc_rule26, asciidoc_rule46,],
        "*": [asciidoc_rule28, asciidoc_rule29, asciidoc_rule30, asciidoc_rule31, asciidoc_rule32,],
        "****": [asciidoc_rule14,],
        "+": [asciidoc_rule8,],
        "++++": [asciidoc_rule12,],
        "-": [asciidoc_rule27,],
        "----": [asciidoc_rule11,],
        ".": [asciidoc_rule33, asciidoc_rule34, asciidoc_rule35, asciidoc_rule36, asciidoc_rule37, asciidoc_rule41,],
        "....": [asciidoc_rule13,],
        "/": [asciidoc_rule10,],
        "////": [asciidoc_rule9,],
        "0": [asciidoc_rule47,],
        "1": [asciidoc_rule47,],
        "2": [asciidoc_rule47,],
        "3": [asciidoc_rule47,],
        "4": [asciidoc_rule47,],
        "5": [asciidoc_rule47,],
        "6": [asciidoc_rule47,],
        "7": [asciidoc_rule47,],
        "8": [asciidoc_rule47,],
        "9": [asciidoc_rule47,],
        ":": [asciidoc_rule21, asciidoc_rule38, asciidoc_rule39, asciidoc_rule40, asciidoc_rule47,],
        "<": [asciidoc_rule19,],
        "=": [asciidoc_rule0, asciidoc_rule1, asciidoc_rule2, asciidoc_rule3, asciidoc_rule4,],
        "@": [asciidoc_rule47,],
        "A": [asciidoc_rule47,],
        "B": [asciidoc_rule47,],
        "C": [asciidoc_rule47,],
        "D": [asciidoc_rule47,],
        "E": [asciidoc_rule47,],
        "F": [asciidoc_rule47,],
        "G": [asciidoc_rule47,],
        "H": [asciidoc_rule47,],
        "I": [asciidoc_rule47,],
        "J": [asciidoc_rule47,],
        "K": [asciidoc_rule47,],
        "L": [asciidoc_rule47,],
        "M": [asciidoc_rule47,],
        "N": [asciidoc_rule45, asciidoc_rule47,],
        "O": [asciidoc_rule47,],
        "P": [asciidoc_rule47,],
        "Q": [asciidoc_rule47,],
        "R": [asciidoc_rule47,],
        "S": [asciidoc_rule47,],
        "T": [asciidoc_rule47,],
        "U": [asciidoc_rule47,],
        "V": [asciidoc_rule47,],
        "W": [asciidoc_rule47,],
        "X": [asciidoc_rule47,],
        "Y": [asciidoc_rule47,],
        "Z": [asciidoc_rule47,],
        "[": [asciidoc_rule18, asciidoc_rule20,],
        "\\": [asciidoc_rule42,],
        "^": [asciidoc_rule5, asciidoc_rule7, asciidoc_rule16, asciidoc_rule17,],
        "____": [asciidoc_rule15,],
        "a": [asciidoc_rule47,],
        "b": [asciidoc_rule47,],
        "c": [asciidoc_rule47,],
        "d": [asciidoc_rule47,],
        "e": [asciidoc_rule47,],
        "f": [asciidoc_rule47,],
        "g": [asciidoc_rule47,],
        "h": [asciidoc_rule47,],
        "i": [asciidoc_rule47,],
        "j": [asciidoc_rule47,],
        "k": [asciidoc_rule47,],
        "l": [asciidoc_rule47,],
        "m": [asciidoc_rule47,],
        "n": [asciidoc_rule47,],
        "o": [asciidoc_rule47,],
        "p": [asciidoc_rule47,],
        "q": [asciidoc_rule47,],
        "r": [asciidoc_rule47,],
        "s": [asciidoc_rule47,],
        "t": [asciidoc_rule47,],
        "u": [asciidoc_rule47,],
        "v": [asciidoc_rule47,],
        "w": [asciidoc_rule47,],
        "x": [asciidoc_rule47,],
        "y": [asciidoc_rule47,],
        "z": [asciidoc_rule47,],
        "|": [asciidoc_rule43, asciidoc_rule44, asciidoc_rule47,],
        "~": [asciidoc_rule6,],
}

# x.rulesDictDict for asciidoc mode.
rulesDictDict = {
        "asciidoc_main": rulesDict1,
}

# Import dict for asciidoc mode.
importDict = {}

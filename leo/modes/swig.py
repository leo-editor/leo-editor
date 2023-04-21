# Leo colorizer control file for swig mode.
# This file is in the public domain.

# Properties for swig mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for swig_main ruleset.
swig_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for swig mode.
attributesDictDict = {
    "swig_main": swig_main_attributes_dict,
}

# Keywords dict for swig_main ruleset.
swig_main_keywords_dict = {}

# Dictionary of keywords dictionaries for swig mode.
keywordsDictDict = {
    "swig_main": swig_main_keywords_dict,
}

# Rules for swig_main ruleset.

def swig_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="%{", end="%}")

def swig_rule1(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="%")


# Rules dict for swig_main ruleset.
rulesDict1 = {
    "%": [swig_rule0, swig_rule1,],
}

# x.rulesDictDict for swig mode.
rulesDictDict = {
    "swig_main": rulesDict1,
}

# Import dict for swig mode.
importDict = {
    "swig_main": ["c::main",],
}

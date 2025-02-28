#@+leo-ver=5-thin
#@+node:peckj.20250227213905.1: * @file /home/peckj/repos/leo-editor/leo/modes/typst.py
#@@language python
# Leo colorizer control file for typst mode.
# This file is in the public domain.

#@+others
#@+node:peckj.20250227214521.1: ** properties
# Properties for typst mode.
properties = {
    "lineComment": "//",
    "commentEnd": "*/",
    "commentStart": "/*",
    "defult": "null",
}
#@+node:peckj.20250227214523.1: ** attributes
# Attributes dict for typst_main ruleset.
typst_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for typst mode.
attributesDictDict = {
    "typst_main": typst_main_attributes_dict,
}
#@+node:peckj.20250227214526.1: ** keywords
# Keywords dict for typst_main ruleset.
typst_main_keywords_dict = {}

# Dictionary of keywords dictionaries for typst mode.
keywordsDictDict = {
    "typst_main": typst_main_keywords_dict,
}
#@+node:peckj.20250227214618.1: ** rules: main
# Rules for typst_main ruleset.
#@+others
#@+node:peckj.20250227220324.1: *3* comments
# single line comment
def typst_rule_comment_line(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="comment1", regexp=r"\/\/")

# block comment
def typst_rule_comment_block(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

#@+node:peckj.20250227220829.1: *3* markup
# *strong emphasis*
def typst_rule_strongemphasis(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="*", end="*")

# _emphasis_
def typst_rule_emphasis(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword4", begin="_", end="_")

# `raw text`
def typst_rule_rawtext(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="`", end="`")

# "string literals"
def typst_rule_string(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")
#@+node:peckj.20250227220927.1: *3* anchors
# <label>
def typst_rule_label(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp=r"\<.+\>")

#@verbatim
# @reference
def typst_rule_reference(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp=r"\@\S+")

# = Heading
def typst_rule_heading(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"^=+.*$")
#@+node:peckj.20250227220951.1: *3* lists
# / Term: description
def typst_rule_term_description(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword3", regexp=r"\/.*\:")
#@+node:peckj.20250227221051.1: *3* math & code
# $math$
def typst_rule_math(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="$", end="$")

# #code()
def typst_rule_code(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword4", regexp=r"\#\w+")
#@-others

# Rules dict for typst_main ruleset.
# note! These are priority lists -- the first match wins.
rulesDict1 = {
    "/": [typst_rule_comment_block, typst_rule_comment_line, typst_rule_term_description],
    "`": [typst_rule_rawtext,],
    "*": [typst_rule_strongemphasis,],
    "_": [typst_rule_emphasis,],
    "<": [typst_rule_label,],
    "@": [typst_rule_reference,],
    "=": [typst_rule_heading,],
    "$": [typst_rule_math,],
    "#": [typst_rule_code,],
    "\"": [typst_rule_string,],
}
#@-others

# x.rulesDictDict for typst mode.
rulesDictDict = {
    "typst_main": rulesDict1,
}

# Import dict for typst mode.
importDict = {}
#@-leo

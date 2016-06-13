# Leo colorizer control file for yaml mode.
# This file is in the public domain.

# Properties for yaml mode.
properties = {
    "indentNextLines": "\\s*([^\\s]+\\s*:|-)\\s*$",
    "indentSize": "2",
    "noTabs": "true",
    "tabSize": "2",
    "lineComment": "#",
}

# Attributes dict for yaml_main ruleset.
yaml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for yaml mode.
attributesDictDict = {
    "yaml_main": yaml_main_attributes_dict,
}

# Keywords dict for yaml_main ruleset.
yaml_main_keywords_dict = {}

# Dictionary of keywords dictionaries for yaml mode.
keywordsDictDict = {
    "yaml_main": yaml_main_keywords_dict,
}

# Rules for yaml_main ruleset.

def yaml_rule0(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="comment1", regexp="\\s*#.*$",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule1(colorer, s, i):
    return colorer.match_seq(s, i, kind="label", seq="---",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule2(colorer, s, i):
    return colorer.match_seq(s, i, kind="label", seq="...",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="[",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="{",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule6(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="-",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule8(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="|",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule11(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def yaml_rule12(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def yaml_rule13(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp="\\s*(-|)?\\s*[^\\s]+\\s*:(\\s|$)",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule14(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+~\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule15(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+null\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+true\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+false\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+yes\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule19(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+no\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule20(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+on\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule21(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="\\s+off\\s*$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule22(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="!!(map|seq|str|set|omap|binary)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule23(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword3", regexp="!![^\\s]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def yaml_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword4", regexp="![^\\s]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for yaml_main ruleset.
rulesDict1 = {
    # EKR: \\s represents  [\t\n\r\f\v], so the whitespace characters themselves, rather than a backspace, must be the leadin characters!
    # This is a bug in jEdit2py.
    "\t":[yaml_rule13,yaml_rule14,yaml_rule15,yaml_rule16,yaml_rule17,yaml_rule18,yaml_rule19,yaml_rule20,yaml_rule21,],    
    "\n":[yaml_rule13,yaml_rule14,yaml_rule15,yaml_rule16,yaml_rule17,yaml_rule18,yaml_rule19,yaml_rule20,yaml_rule21,],
    " ": [yaml_rule13,yaml_rule14,yaml_rule15,yaml_rule16,yaml_rule17,yaml_rule18,yaml_rule19,yaml_rule20,yaml_rule21,],
    "#":[yaml_rule0,],
    "!": [yaml_rule22,yaml_rule23,yaml_rule24,],
    "&": [yaml_rule11,],
    "*": [yaml_rule12,],
    "+": [yaml_rule8,],
    "-": [yaml_rule1,yaml_rule7,],
    ".": [yaml_rule2,],
    ">": [yaml_rule10,],
    "[": [yaml_rule4,],
    ## "\\": [yaml_rule13,yaml_rule14,yaml_rule15,yaml_rule16,yaml_rule17,yaml_rule18,yaml_rule19,yaml_rule20,yaml_rule21,],
    "]": [yaml_rule3,],
    "{": [yaml_rule5,],
    "|": [yaml_rule9,],
    "}": [yaml_rule6,],
}

# x.rulesDictDict for yaml mode.
rulesDictDict = {
    "yaml_main": rulesDict1,
}

# Import dict for yaml mode.
importDict = {}


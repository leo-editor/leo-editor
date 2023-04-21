# Leo colorizer control file for rpmspec mode.
# This file is in the public domain.

# Properties for rpmspec mode.
properties = {
    "lineComment": "#",
}

# Attributes dict for rpmspec_main ruleset.
rpmspec_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for rpmspec_attr ruleset.
rpmspec_attr_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for rpmspec_verify ruleset.
rpmspec_verify_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rpmspec mode.
attributesDictDict = {
    "rpmspec_attr": rpmspec_attr_attributes_dict,
    "rpmspec_main": rpmspec_main_attributes_dict,
    "rpmspec_verify": rpmspec_verify_attributes_dict,
}

# Keywords dict for rpmspec_main ruleset.
rpmspec_main_keywords_dict = {
    "%build": "label",
    "%clean": "label",
    "%config": "markup",
    "%description": "label",
    "%dir": "markup",
    "%doc": "markup",
    "%docdir": "markup",
    "%else": "function",
    "%endif": "function",
    "%files": "label",
    "%ifarch": "function",
    "%ifnarch": "function",
    "%ifnos": "function",
    "%ifos": "function",
    "%install": "label",
    "%package": "markup",
    "%post": "label",
    "%postun": "label",
    "%pre": "label",
    "%prep": "label",
    "%preun": "label",
    "%setup": "function",
    "%verifyscript": "label",
    "AutoReqProv:": "keyword1",
    "BuildArch:": "keyword1",
    "BuildRoot:": "keyword1",
    "Conflicts:": "keyword1",
    "Copyright:": "keyword1",
    "Distribution:": "keyword1",
    "ExcludeArch:": "keyword1",
    "ExclusiveArch:": "keyword1",
    "ExclusiveOS:": "keyword1",
    "Group:": "keyword1",
    "Icon:": "keyword1",
    "Name:": "keyword1",
    "NoPatch:": "keyword1",
    "NoSource:": "keyword1",
    "Packager:": "keyword1",
    "Prefix:": "keyword1",
    "Provides:": "keyword1",
    "Release:": "keyword1",
    "Requires:": "keyword1",
    "Serial:": "keyword1",
    "Summary:": "keyword1",
    "URL:": "keyword1",
    "Vendor:": "keyword1",
    "Version:": "keyword1",
}

# Keywords dict for rpmspec_attr ruleset.
rpmspec_attr_keywords_dict = {}

# Keywords dict for rpmspec_verify ruleset.
rpmspec_verify_keywords_dict = {
    "group": "keyword2",
    "maj": "keyword2",
    "md5": "keyword2",
    "min": "keyword2",
    "mode": "keyword2",
    "mtime": "keyword2",
    "not": "operator",
    "owner": "keyword2",
    "size": "keyword2",
    "symlink": "keyword2",
}

# Dictionary of keywords dictionaries for rpmspec mode.
keywordsDictDict = {
    "rpmspec_attr": rpmspec_attr_keywords_dict,
    "rpmspec_main": rpmspec_main_keywords_dict,
    "rpmspec_verify": rpmspec_verify_keywords_dict,
}

# Rules for rpmspec_main ruleset.

def rpmspec_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#",
          at_line_start=True)

def rpmspec_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def rpmspec_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def rpmspec_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def rpmspec_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="%attr(", end=")",
          delegate="rpmspec::attr",
          no_line_break=True)

def rpmspec_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="%verify(", end=")",
          delegate="rpmspec::verify",
          no_line_break=True)

def rpmspec_rule6(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword1", pattern="Source",
          at_line_start=True)

def rpmspec_rule7(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword1", pattern="Patch",
          at_line_start=True)

def rpmspec_rule8(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern="%patch",
          at_line_start=True)

def rpmspec_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def rpmspec_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="%{", end="}",
          no_line_break=True)

def rpmspec_rule11(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$#")

def rpmspec_rule12(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$?")

def rpmspec_rule13(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$*")

def rpmspec_rule14(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$<")

def rpmspec_rule15(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

def rpmspec_rule16(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for rpmspec_main ruleset.
rulesDict1 = {
    "#": [rpmspec_rule0,],
    "$": [rpmspec_rule9, rpmspec_rule11, rpmspec_rule12, rpmspec_rule13, rpmspec_rule14, rpmspec_rule15,],
    "%": [rpmspec_rule4, rpmspec_rule5, rpmspec_rule8, rpmspec_rule10, rpmspec_rule16,],
    "0": [rpmspec_rule16,],
    "1": [rpmspec_rule16,],
    "2": [rpmspec_rule16,],
    "3": [rpmspec_rule16,],
    "4": [rpmspec_rule16,],
    "5": [rpmspec_rule16,],
    "6": [rpmspec_rule16,],
    "7": [rpmspec_rule16,],
    "8": [rpmspec_rule16,],
    "9": [rpmspec_rule16,],
    ":": [rpmspec_rule16,],
    "<": [rpmspec_rule1,],
    "=": [rpmspec_rule3,],
    ">": [rpmspec_rule2,],
    "@": [rpmspec_rule16,],
    "A": [rpmspec_rule16,],
    "B": [rpmspec_rule16,],
    "C": [rpmspec_rule16,],
    "D": [rpmspec_rule16,],
    "E": [rpmspec_rule16,],
    "F": [rpmspec_rule16,],
    "G": [rpmspec_rule16,],
    "H": [rpmspec_rule16,],
    "I": [rpmspec_rule16,],
    "J": [rpmspec_rule16,],
    "K": [rpmspec_rule16,],
    "L": [rpmspec_rule16,],
    "M": [rpmspec_rule16,],
    "N": [rpmspec_rule16,],
    "O": [rpmspec_rule16,],
    "P": [rpmspec_rule7, rpmspec_rule16,],
    "Q": [rpmspec_rule16,],
    "R": [rpmspec_rule16,],
    "S": [rpmspec_rule6, rpmspec_rule16,],
    "T": [rpmspec_rule16,],
    "U": [rpmspec_rule16,],
    "V": [rpmspec_rule16,],
    "W": [rpmspec_rule16,],
    "X": [rpmspec_rule16,],
    "Y": [rpmspec_rule16,],
    "Z": [rpmspec_rule16,],
    "a": [rpmspec_rule16,],
    "b": [rpmspec_rule16,],
    "c": [rpmspec_rule16,],
    "d": [rpmspec_rule16,],
    "e": [rpmspec_rule16,],
    "f": [rpmspec_rule16,],
    "g": [rpmspec_rule16,],
    "h": [rpmspec_rule16,],
    "i": [rpmspec_rule16,],
    "j": [rpmspec_rule16,],
    "k": [rpmspec_rule16,],
    "l": [rpmspec_rule16,],
    "m": [rpmspec_rule16,],
    "n": [rpmspec_rule16,],
    "o": [rpmspec_rule16,],
    "p": [rpmspec_rule16,],
    "q": [rpmspec_rule16,],
    "r": [rpmspec_rule16,],
    "s": [rpmspec_rule16,],
    "t": [rpmspec_rule16,],
    "u": [rpmspec_rule16,],
    "v": [rpmspec_rule16,],
    "w": [rpmspec_rule16,],
    "x": [rpmspec_rule16,],
    "y": [rpmspec_rule16,],
    "z": [rpmspec_rule16,],
}

# Rules for rpmspec_attr ruleset.

def rpmspec_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def rpmspec_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

# Rules dict for rpmspec_attr ruleset.
rulesDict2 = {
    ",": [rpmspec_rule17,],
    "-": [rpmspec_rule18,],
}

# Rules for rpmspec_verify ruleset.

def rpmspec_rule19(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for rpmspec_verify ruleset.
rulesDict3 = {
    "%": [rpmspec_rule19,],
    "0": [rpmspec_rule19,],
    "1": [rpmspec_rule19,],
    "2": [rpmspec_rule19,],
    "3": [rpmspec_rule19,],
    "4": [rpmspec_rule19,],
    "5": [rpmspec_rule19,],
    "6": [rpmspec_rule19,],
    "7": [rpmspec_rule19,],
    "8": [rpmspec_rule19,],
    "9": [rpmspec_rule19,],
    ":": [rpmspec_rule19,],
    "@": [rpmspec_rule19,],
    "A": [rpmspec_rule19,],
    "B": [rpmspec_rule19,],
    "C": [rpmspec_rule19,],
    "D": [rpmspec_rule19,],
    "E": [rpmspec_rule19,],
    "F": [rpmspec_rule19,],
    "G": [rpmspec_rule19,],
    "H": [rpmspec_rule19,],
    "I": [rpmspec_rule19,],
    "J": [rpmspec_rule19,],
    "K": [rpmspec_rule19,],
    "L": [rpmspec_rule19,],
    "M": [rpmspec_rule19,],
    "N": [rpmspec_rule19,],
    "O": [rpmspec_rule19,],
    "P": [rpmspec_rule19,],
    "Q": [rpmspec_rule19,],
    "R": [rpmspec_rule19,],
    "S": [rpmspec_rule19,],
    "T": [rpmspec_rule19,],
    "U": [rpmspec_rule19,],
    "V": [rpmspec_rule19,],
    "W": [rpmspec_rule19,],
    "X": [rpmspec_rule19,],
    "Y": [rpmspec_rule19,],
    "Z": [rpmspec_rule19,],
    "a": [rpmspec_rule19,],
    "b": [rpmspec_rule19,],
    "c": [rpmspec_rule19,],
    "d": [rpmspec_rule19,],
    "e": [rpmspec_rule19,],
    "f": [rpmspec_rule19,],
    "g": [rpmspec_rule19,],
    "h": [rpmspec_rule19,],
    "i": [rpmspec_rule19,],
    "j": [rpmspec_rule19,],
    "k": [rpmspec_rule19,],
    "l": [rpmspec_rule19,],
    "m": [rpmspec_rule19,],
    "n": [rpmspec_rule19,],
    "o": [rpmspec_rule19,],
    "p": [rpmspec_rule19,],
    "q": [rpmspec_rule19,],
    "r": [rpmspec_rule19,],
    "s": [rpmspec_rule19,],
    "t": [rpmspec_rule19,],
    "u": [rpmspec_rule19,],
    "v": [rpmspec_rule19,],
    "w": [rpmspec_rule19,],
    "x": [rpmspec_rule19,],
    "y": [rpmspec_rule19,],
    "z": [rpmspec_rule19,],
}

# x.rulesDictDict for rpmspec mode.
rulesDictDict = {
    "rpmspec_attr": rulesDict2,
    "rpmspec_main": rulesDict1,
    "rpmspec_verify": rulesDict3,
}

# Import dict for rpmspec mode.
importDict = {}

# Leo colorizer control file for jcl mode.
# This file is in the public domain.

# Properties for jcl mode.
properties = {
	"wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for jcl_main ruleset.
jcl_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "false",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for jcl mode.
attributesDictDict = {
	"jcl_main": jcl_main_attributes_dict,
}

# Keywords dict for jcl_main ruleset.
jcl_main_keywords_dict = {
	"cntl": "keyword2",
	"command": "keyword2",
	"dd": "keyword2",
	"else": "keyword2",
	"encntl": "keyword2",
	"endif": "keyword2",
	"exec": "keyword2",
	"if": "keyword2",
	"include": "keyword2",
	"jclib": "keyword2",
	"job": "keyword2",
	"msg": "keyword2",
	"output": "keyword2",
	"pend": "keyword2",
	"proc": "keyword2",
	"set": "keyword2",
	"then": "keyword2",
	"xmit": "keyword2",
}

# Dictionary of keywords dictionaries for jcl mode.
keywordsDictDict = {
	"jcl_main": jcl_main_keywords_dict,
}

# Rules for jcl_main ruleset.

def jcl_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//*",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def jcl_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jcl_rule2(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jcl_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jcl_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jcl_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jcl_rule6(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="|",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jcl_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=",",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jcl_rule8(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for jcl_main ruleset.
rulesDict1 = {
	"&": [jcl_rule5,],
	"'": [jcl_rule1,],
	",": [jcl_rule7,],
	"/": [jcl_rule0,],
	"0": [jcl_rule8,],
	"1": [jcl_rule8,],
	"2": [jcl_rule8,],
	"3": [jcl_rule8,],
	"4": [jcl_rule8,],
	"5": [jcl_rule8,],
	"6": [jcl_rule8,],
	"7": [jcl_rule8,],
	"8": [jcl_rule8,],
	"9": [jcl_rule8,],
	"<": [jcl_rule3,],
	"=": [jcl_rule2,],
	">": [jcl_rule4,],
	"@": [jcl_rule8,],
	"A": [jcl_rule8,],
	"B": [jcl_rule8,],
	"C": [jcl_rule8,],
	"D": [jcl_rule8,],
	"E": [jcl_rule8,],
	"F": [jcl_rule8,],
	"G": [jcl_rule8,],
	"H": [jcl_rule8,],
	"I": [jcl_rule8,],
	"J": [jcl_rule8,],
	"K": [jcl_rule8,],
	"L": [jcl_rule8,],
	"M": [jcl_rule8,],
	"N": [jcl_rule8,],
	"O": [jcl_rule8,],
	"P": [jcl_rule8,],
	"Q": [jcl_rule8,],
	"R": [jcl_rule8,],
	"S": [jcl_rule8,],
	"T": [jcl_rule8,],
	"U": [jcl_rule8,],
	"V": [jcl_rule8,],
	"W": [jcl_rule8,],
	"X": [jcl_rule8,],
	"Y": [jcl_rule8,],
	"Z": [jcl_rule8,],
	"a": [jcl_rule8,],
	"b": [jcl_rule8,],
	"c": [jcl_rule8,],
	"d": [jcl_rule8,],
	"e": [jcl_rule8,],
	"f": [jcl_rule8,],
	"g": [jcl_rule8,],
	"h": [jcl_rule8,],
	"i": [jcl_rule8,],
	"j": [jcl_rule8,],
	"k": [jcl_rule8,],
	"l": [jcl_rule8,],
	"m": [jcl_rule8,],
	"n": [jcl_rule8,],
	"o": [jcl_rule8,],
	"p": [jcl_rule8,],
	"q": [jcl_rule8,],
	"r": [jcl_rule8,],
	"s": [jcl_rule8,],
	"t": [jcl_rule8,],
	"u": [jcl_rule8,],
	"v": [jcl_rule8,],
	"w": [jcl_rule8,],
	"x": [jcl_rule8,],
	"y": [jcl_rule8,],
	"z": [jcl_rule8,],
	"|": [jcl_rule6,],
}

# x.rulesDictDict for jcl mode.
rulesDictDict = {
	"jcl_main": rulesDict1,
}

# Import dict for jcl mode.
importDict = {}


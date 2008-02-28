# Leo colorizer control file for relax_ng_compact mode.
# This file is in the public domain.

# Properties for relax_ng_compact mode.
properties = {
	"doubleBracketIndent": "false",
	"indentCloseBrackets": "}",
	"indentOpenBrackets": "{",
	"lineComment": "#",
	"wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for relax_ng_compact_main ruleset.
relax_ng_compact_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for relax_ng_compact mode.
attributesDictDict = {
	"relax_ng_compact_main": relax_ng_compact_main_attributes_dict,
}

# Keywords dict for relax_ng_compact_main ruleset.
relax_ng_compact_main_keywords_dict = {
	"attribute": "keyword1",
	"datatypes": "keyword1",
	"default": "keyword1",
	"div": "keyword1",
	"element": "keyword1",
	"empty": "keyword1",
	"external": "keyword1",
	"grammar": "keyword1",
	"include": "keyword1",
	"inherit": "keyword1",
	"list": "keyword1",
	"mixed": "keyword1",
	"namespace": "keyword1",
	"notAllowed": "keyword1",
	"parent": "keyword1",
	"start": "keyword1",
	"string": "keyword2",
	"text": "keyword1",
	"token": "keyword2",
}

# Dictionary of keywords dictionaries for relax_ng_compact mode.
keywordsDictDict = {
	"relax_ng_compact_main": relax_ng_compact_main_keywords_dict,
}

# Rules for relax_ng_compact_main ruleset.

def relax_ng_compact_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def relax_ng_compact_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def relax_ng_compact_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def relax_ng_compact_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def relax_ng_compact_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'''", end="'''",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def relax_ng_compact_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule6(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="?",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule8(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="&=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="|=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="|",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="-",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def relax_ng_compact_rule14(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="null", pattern="\\",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def relax_ng_compact_rule15(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for relax_ng_compact_main ruleset.
rulesDict1 = {
	"\"": [relax_ng_compact_rule1,relax_ng_compact_rule3,],
	"#": [relax_ng_compact_rule0,],
	"&": [relax_ng_compact_rule8,relax_ng_compact_rule9,],
	"'": [relax_ng_compact_rule2,relax_ng_compact_rule4,],
	"*": [relax_ng_compact_rule6,],
	"+": [relax_ng_compact_rule5,],
	"-": [relax_ng_compact_rule13,],
	"0": [relax_ng_compact_rule15,],
	"1": [relax_ng_compact_rule15,],
	"2": [relax_ng_compact_rule15,],
	"3": [relax_ng_compact_rule15,],
	"4": [relax_ng_compact_rule15,],
	"5": [relax_ng_compact_rule15,],
	"6": [relax_ng_compact_rule15,],
	"7": [relax_ng_compact_rule15,],
	"8": [relax_ng_compact_rule15,],
	"9": [relax_ng_compact_rule15,],
	"=": [relax_ng_compact_rule12,],
	"?": [relax_ng_compact_rule7,],
	"@": [relax_ng_compact_rule15,],
	"A": [relax_ng_compact_rule15,],
	"B": [relax_ng_compact_rule15,],
	"C": [relax_ng_compact_rule15,],
	"D": [relax_ng_compact_rule15,],
	"E": [relax_ng_compact_rule15,],
	"F": [relax_ng_compact_rule15,],
	"G": [relax_ng_compact_rule15,],
	"H": [relax_ng_compact_rule15,],
	"I": [relax_ng_compact_rule15,],
	"J": [relax_ng_compact_rule15,],
	"K": [relax_ng_compact_rule15,],
	"L": [relax_ng_compact_rule15,],
	"M": [relax_ng_compact_rule15,],
	"N": [relax_ng_compact_rule15,],
	"O": [relax_ng_compact_rule15,],
	"P": [relax_ng_compact_rule15,],
	"Q": [relax_ng_compact_rule15,],
	"R": [relax_ng_compact_rule15,],
	"S": [relax_ng_compact_rule15,],
	"T": [relax_ng_compact_rule15,],
	"U": [relax_ng_compact_rule15,],
	"V": [relax_ng_compact_rule15,],
	"W": [relax_ng_compact_rule15,],
	"X": [relax_ng_compact_rule15,],
	"Y": [relax_ng_compact_rule15,],
	"Z": [relax_ng_compact_rule15,],
	"\\": [relax_ng_compact_rule14,],
	"a": [relax_ng_compact_rule15,],
	"b": [relax_ng_compact_rule15,],
	"c": [relax_ng_compact_rule15,],
	"d": [relax_ng_compact_rule15,],
	"e": [relax_ng_compact_rule15,],
	"f": [relax_ng_compact_rule15,],
	"g": [relax_ng_compact_rule15,],
	"h": [relax_ng_compact_rule15,],
	"i": [relax_ng_compact_rule15,],
	"j": [relax_ng_compact_rule15,],
	"k": [relax_ng_compact_rule15,],
	"l": [relax_ng_compact_rule15,],
	"m": [relax_ng_compact_rule15,],
	"n": [relax_ng_compact_rule15,],
	"o": [relax_ng_compact_rule15,],
	"p": [relax_ng_compact_rule15,],
	"q": [relax_ng_compact_rule15,],
	"r": [relax_ng_compact_rule15,],
	"s": [relax_ng_compact_rule15,],
	"t": [relax_ng_compact_rule15,],
	"u": [relax_ng_compact_rule15,],
	"v": [relax_ng_compact_rule15,],
	"w": [relax_ng_compact_rule15,],
	"x": [relax_ng_compact_rule15,],
	"y": [relax_ng_compact_rule15,],
	"z": [relax_ng_compact_rule15,],
	"|": [relax_ng_compact_rule10,relax_ng_compact_rule11,],
}

# x.rulesDictDict for relax_ng_compact mode.
rulesDictDict = {
	"relax_ng_compact_main": rulesDict1,
}

# Import dict for relax_ng_compact mode.
importDict = {}


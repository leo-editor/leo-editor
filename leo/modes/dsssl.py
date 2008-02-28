# Leo colorizer control file for dsssl mode.
# This file is in the public domain.

# Properties for dsssl mode.
properties = {
	"commentEnd": "-->",
	"commentStart": "<!--",
	"lineComment": ";",
}

# Attributes dict for dsssl_main ruleset.
dsssl_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for dsssl mode.
attributesDictDict = {
	"dsssl_main": dsssl_main_attributes_dict,
}

# Keywords dict for dsssl_main ruleset.
dsssl_main_keywords_dict = {
	"and": "keyword1",
	"append": "keyword1",
	"attribute-string": "function",
	"attributes:": "label",
	"car": "keyword2",
	"cdr": "keyword2",
	"children": "keyword1",
	"cond": "keyword1",
	"cons": "keyword2",
	"current-node": "function",
	"default": "function",
	"define": "keyword1",
	"element": "function",
	"else": "keyword1",
	"empty-sosofo": "function",
	"eq?": "keyword3",
	"equal?": "keyword3",
	"external-procedure": "function",
	"gi": "function",
	"gi:": "label",
	"if": "keyword1",
	"lambda": "keyword1",
	"let": "keyword1",
	"let*": "keyword1",
	"list": "keyword1",
	"literal": "function",
	"loop": "keyword1",
	"make": "function",
	"mode": "function",
	"node": "function",
	"node-list-empty?": "keyword3",
	"node-list-first": "keyword2",
	"node-list-rest": "keyword2",
	"normalize": "keyword1",
	"not": "keyword1",
	"null?": "keyword3",
	"or": "keyword1",
	"pair?": "keyword3",
	"process-children": "function",
	"process-node-list": "function",
	"quote": "keyword1",
	"root": "function",
	"select-elements": "function",
	"sequence": "function",
	"sosofo-append": "function",
	"with-mode": "function",
	"zero?": "keyword3",
}

# Dictionary of keywords dictionaries for dsssl mode.
keywordsDictDict = {
	"dsssl_main": dsssl_main_keywords_dict,
}

# Rules for dsssl_main ruleset.

def dsssl_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def dsssl_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule2(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="'(",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def dsssl_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def dsssl_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="$", end="$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def dsssl_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="%", end="%",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def dsssl_rule7(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="#",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def dsssl_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!ENTITY", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::entity-tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<![CDATA[", end="]]>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::cdata",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::dtd-tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="<=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def dsssl_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="</style-specification", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="</style-sheet", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<style-specification", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<external-specification", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<style-sheet", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def dsssl_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=True)

def dsssl_rule18(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for dsssl_main ruleset.
rulesDict1 = {
	"\"": [dsssl_rule4,],
	"#": [dsssl_rule7,],
	"$": [dsssl_rule5,],
	"%": [dsssl_rule6,],
	"&": [dsssl_rule17,],
	"'": [dsssl_rule2,dsssl_rule3,],
	"*": [dsssl_rule18,],
	"-": [dsssl_rule18,],
	"0": [dsssl_rule18,],
	"1": [dsssl_rule18,],
	"2": [dsssl_rule18,],
	"3": [dsssl_rule18,],
	"4": [dsssl_rule18,],
	"5": [dsssl_rule18,],
	"6": [dsssl_rule18,],
	"7": [dsssl_rule18,],
	"8": [dsssl_rule18,],
	"9": [dsssl_rule18,],
	":": [dsssl_rule18,],
	";": [dsssl_rule0,],
	"<": [dsssl_rule1,dsssl_rule8,dsssl_rule9,dsssl_rule10,dsssl_rule11,dsssl_rule12,dsssl_rule13,dsssl_rule14,dsssl_rule15,dsssl_rule16,],
	"?": [dsssl_rule18,],
	"@": [dsssl_rule18,],
	"A": [dsssl_rule18,],
	"B": [dsssl_rule18,],
	"C": [dsssl_rule18,],
	"D": [dsssl_rule18,],
	"E": [dsssl_rule18,],
	"F": [dsssl_rule18,],
	"G": [dsssl_rule18,],
	"H": [dsssl_rule18,],
	"I": [dsssl_rule18,],
	"J": [dsssl_rule18,],
	"K": [dsssl_rule18,],
	"L": [dsssl_rule18,],
	"M": [dsssl_rule18,],
	"N": [dsssl_rule18,],
	"O": [dsssl_rule18,],
	"P": [dsssl_rule18,],
	"Q": [dsssl_rule18,],
	"R": [dsssl_rule18,],
	"S": [dsssl_rule18,],
	"T": [dsssl_rule18,],
	"U": [dsssl_rule18,],
	"V": [dsssl_rule18,],
	"W": [dsssl_rule18,],
	"X": [dsssl_rule18,],
	"Y": [dsssl_rule18,],
	"Z": [dsssl_rule18,],
	"a": [dsssl_rule18,],
	"b": [dsssl_rule18,],
	"c": [dsssl_rule18,],
	"d": [dsssl_rule18,],
	"e": [dsssl_rule18,],
	"f": [dsssl_rule18,],
	"g": [dsssl_rule18,],
	"h": [dsssl_rule18,],
	"i": [dsssl_rule18,],
	"j": [dsssl_rule18,],
	"k": [dsssl_rule18,],
	"l": [dsssl_rule18,],
	"m": [dsssl_rule18,],
	"n": [dsssl_rule18,],
	"o": [dsssl_rule18,],
	"p": [dsssl_rule18,],
	"q": [dsssl_rule18,],
	"r": [dsssl_rule18,],
	"s": [dsssl_rule18,],
	"t": [dsssl_rule18,],
	"u": [dsssl_rule18,],
	"v": [dsssl_rule18,],
	"w": [dsssl_rule18,],
	"x": [dsssl_rule18,],
	"y": [dsssl_rule18,],
	"z": [dsssl_rule18,],
}

# x.rulesDictDict for dsssl mode.
rulesDictDict = {
	"dsssl_main": rulesDict1,
}

# Import dict for dsssl mode.
importDict = {}


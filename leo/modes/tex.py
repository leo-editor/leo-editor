# Leo colorizer control file for tex mode.
# This file is in the public domain.

# Properties for tex mode.
properties = {
	"lineComment": "%",
}

# Attributes dict for tex_main ruleset.
tex_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for tex_math ruleset.
tex_math_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for tex_verbatim ruleset.
tex_verbatim_attributes_dict = {
	"default": "NULL",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for tex mode.
attributesDictDict = {
	"tex_main": tex_main_attributes_dict,
	"tex_math": tex_math_attributes_dict,
	"tex_verbatim": tex_verbatim_attributes_dict,
}

# Keywords dict for tex_main ruleset.
tex_main_keywords_dict = {}

# Keywords dict for tex_math ruleset.
tex_math_keywords_dict = {}

# Keywords dict for tex_verbatim ruleset.
tex_verbatim_keywords_dict = {}

# Dictionary of keywords dictionaries for tex mode.
keywordsDictDict = {
	"tex_main": tex_main_keywords_dict,
	"tex_math": tex_math_keywords_dict,
	"tex_verbatim": tex_verbatim_keywords_dict,
}

# Rules for tex_main ruleset.

def tex_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="$$", end="$$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="tex::math",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def tex_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="$", end="$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="tex::math",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def tex_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\[", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="tex::math",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def tex_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="\\$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="\\\\",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="\\%",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="\\iffalse", end="\\fi",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def tex_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="\\begin{verbatim}", end="\\end{verbatim}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="tex::verbatim",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def tex_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="\\verb|", end="|",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="tex::verbatim",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def tex_rule9(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword1", pattern="\\",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def tex_rule10(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def tex_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="{",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="[",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for tex_main ruleset.
rulesDict1 = {
	"$": [tex_rule0,tex_rule1,],
	"%": [tex_rule10,],
	"[": [tex_rule13,],
	"\\": [tex_rule2,tex_rule3,tex_rule4,tex_rule5,tex_rule6,tex_rule7,tex_rule8,tex_rule9,],
	"]": [tex_rule14,],
	"{": [tex_rule11,],
	"}": [tex_rule12,],
}

# Rules for tex_math ruleset.

def tex_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword3", seq="\\$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule16(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword3", seq="\\\\",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule17(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword3", seq="\\%",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule18(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="\\",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def tex_rule19(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule20(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="(",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule21(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="{",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule22(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule23(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="[",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule24(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule25(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule26(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="!",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule27(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule28(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="-",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule29(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="/",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule30(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule31(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule32(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="<",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule33(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule34(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="|",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule35(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="^",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule36(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="~",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule37(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq=".",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule38(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq=",",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule39(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule40(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="?",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule41(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq=":",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule42(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule43(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule44(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword2", seq="`",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def tex_rule45(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

# Rules dict for tex_math ruleset.
rulesDict2 = {
	"!": [tex_rule26,],
	"\"": [tex_rule43,],
	"%": [tex_rule45,],
	"&": [tex_rule33,],
	"'": [tex_rule42,],
	"(": [tex_rule20,],
	")": [tex_rule19,],
	"*": [tex_rule30,],
	"+": [tex_rule27,],
	",": [tex_rule38,],
	"-": [tex_rule28,],
	".": [tex_rule37,],
	"/": [tex_rule29,],
	":": [tex_rule41,],
	";": [tex_rule39,],
	"<": [tex_rule32,],
	"=": [tex_rule25,],
	">": [tex_rule31,],
	"?": [tex_rule40,],
	"[": [tex_rule23,],
	"\\": [tex_rule15,tex_rule16,tex_rule17,tex_rule18,],
	"]": [tex_rule24,],
	"^": [tex_rule35,],
	"`": [tex_rule44,],
	"{": [tex_rule21,],
	"|": [tex_rule34,],
	"}": [tex_rule22,],
	"~": [tex_rule36,],
}

# Rules for tex_verbatim ruleset.

# Rules dict for tex_verbatim ruleset.
rulesDict3 = {}

# x.rulesDictDict for tex mode.
rulesDictDict = {
	"tex_main": rulesDict1,
	"tex_math": rulesDict2,
	"tex_verbatim": rulesDict3,
}

# Import dict for tex mode.
importDict = {}


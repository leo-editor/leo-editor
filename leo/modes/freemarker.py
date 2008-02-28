# Leo colorizer control file for freemarker mode.
# This file is in the public domain.

# Properties for freemarker mode.
properties = {}

# Attributes dict for freemarker_main ruleset.
freemarker_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for freemarker_expression ruleset.
freemarker_expression_attributes_dict = {
	"default": "KEYWORD2",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for freemarker_tags ruleset.
freemarker_tags_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for freemarker_inquote ruleset.
freemarker_inquote_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for freemarker_invalid ruleset.
freemarker_invalid_attributes_dict = {
	"default": "INVALID",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for freemarker mode.
attributesDictDict = {
	"freemarker_expression": freemarker_expression_attributes_dict,
	"freemarker_inquote": freemarker_inquote_attributes_dict,
	"freemarker_invalid": freemarker_invalid_attributes_dict,
	"freemarker_main": freemarker_main_attributes_dict,
	"freemarker_tags": freemarker_tags_attributes_dict,
}

# Keywords dict for freemarker_main ruleset.
freemarker_main_keywords_dict = {}

# Keywords dict for freemarker_expression ruleset.
freemarker_expression_keywords_dict = {
	"as": "keyword1",
	"false": "keyword1",
	"gt": "operator",
	"gte": "operator",
	"in": "keyword1",
	"lt": "operator",
	"lte": "operator",
	"true": "keyword1",
	"using": "keyword1",
}

# Keywords dict for freemarker_tags ruleset.
freemarker_tags_keywords_dict = {}

# Keywords dict for freemarker_inquote ruleset.
freemarker_inquote_keywords_dict = {}

# Keywords dict for freemarker_invalid ruleset.
freemarker_invalid_keywords_dict = {}

# Dictionary of keywords dictionaries for freemarker mode.
keywordsDictDict = {
	"freemarker_expression": freemarker_expression_keywords_dict,
	"freemarker_inquote": freemarker_inquote_keywords_dict,
	"freemarker_invalid": freemarker_invalid_keywords_dict,
	"freemarker_main": freemarker_main_keywords_dict,
	"freemarker_tags": freemarker_tags_keywords_dict,
}

# Rules for freemarker_main ruleset.

def freemarker_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script", end="</script>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<Script", end="</Script>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<style", end="</style>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::css",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<Style", end="</Style>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::css",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::css",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::dtd-tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::dtd-tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="${", end="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="#{", end="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule10(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="<#ftl\\>", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule11(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="<#?(if|elseif|switch|foreach|list|case|assign|local|global|setting|include|import|stop|escape|macro|function|transform|call|visit|recurse)(\\s|/|$)", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule12(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="</#?(assign|local|global|if|switch|foreach|list|escape|macro|function|transform|compress|noescape)\\>", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::invalid",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule13(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="<#?(else|compress|noescape|default|break|flush|nested|t|rt|lt|return|recurse)\\>", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::invalid",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule14(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="</@(([_@[:alpha:]][_@[:alnum:]]*)(\\.[_@[:alpha:]][_@[:alnum:]]*)*)?", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::invalid",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule15(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="<@([_@[:alpha:]][_@[:alnum:]]*)(\\.[_@[:alpha:]][_@[:alnum:]]*)*", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<#--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule17(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="<stop>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<comment>", end="</comment>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="invalid", begin="<#", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="invalid", begin="</#", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule21(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

# Rules dict for freemarker_main ruleset.
rulesDict1 = {
	"#": [freemarker_rule9,],
	"$": [freemarker_rule8,],
	"<": [freemarker_rule0,freemarker_rule1,freemarker_rule2,freemarker_rule3,freemarker_rule4,freemarker_rule5,freemarker_rule6,freemarker_rule7,freemarker_rule10,freemarker_rule11,freemarker_rule12,freemarker_rule13,freemarker_rule14,freemarker_rule15,freemarker_rule16,freemarker_rule17,freemarker_rule18,freemarker_rule19,freemarker_rule20,freemarker_rule21,],
}

# Rules for freemarker_expression ruleset.

def freemarker_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<#--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule23(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule24(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule25(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="(", end=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule26(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule27(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="!",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule28(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="|",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule29(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule30(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule31(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule32(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule33(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="/",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule34(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="-",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule35(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule36(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="%",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule37(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=".",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule38(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=":",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule39(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=".",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule40(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=".",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule41(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="[",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule42(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule43(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="{",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule44(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule45(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def freemarker_rule46(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern="?",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def freemarker_rule47(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for freemarker_expression ruleset.
rulesDict2 = {
	"!": [freemarker_rule27,],
	"\"": [freemarker_rule24,],
	"%": [freemarker_rule36,],
	"&": [freemarker_rule29,],
	"(": [freemarker_rule25,],
	"*": [freemarker_rule32,],
	"+": [freemarker_rule35,],
	"-": [freemarker_rule34,],
	".": [freemarker_rule37,freemarker_rule39,freemarker_rule40,],
	"/": [freemarker_rule33,],
	"0": [freemarker_rule47,],
	"1": [freemarker_rule47,],
	"2": [freemarker_rule47,],
	"3": [freemarker_rule47,],
	"4": [freemarker_rule47,],
	"5": [freemarker_rule47,],
	"6": [freemarker_rule47,],
	"7": [freemarker_rule47,],
	"8": [freemarker_rule47,],
	"9": [freemarker_rule47,],
	":": [freemarker_rule38,],
	";": [freemarker_rule45,],
	"<": [freemarker_rule22,freemarker_rule23,freemarker_rule30,],
	"=": [freemarker_rule26,],
	">": [freemarker_rule31,],
	"?": [freemarker_rule46,],
	"@": [freemarker_rule47,],
	"A": [freemarker_rule47,],
	"B": [freemarker_rule47,],
	"C": [freemarker_rule47,],
	"D": [freemarker_rule47,],
	"E": [freemarker_rule47,],
	"F": [freemarker_rule47,],
	"G": [freemarker_rule47,],
	"H": [freemarker_rule47,],
	"I": [freemarker_rule47,],
	"J": [freemarker_rule47,],
	"K": [freemarker_rule47,],
	"L": [freemarker_rule47,],
	"M": [freemarker_rule47,],
	"N": [freemarker_rule47,],
	"O": [freemarker_rule47,],
	"P": [freemarker_rule47,],
	"Q": [freemarker_rule47,],
	"R": [freemarker_rule47,],
	"S": [freemarker_rule47,],
	"T": [freemarker_rule47,],
	"U": [freemarker_rule47,],
	"V": [freemarker_rule47,],
	"W": [freemarker_rule47,],
	"X": [freemarker_rule47,],
	"Y": [freemarker_rule47,],
	"Z": [freemarker_rule47,],
	"[": [freemarker_rule41,],
	"]": [freemarker_rule42,],
	"a": [freemarker_rule47,],
	"b": [freemarker_rule47,],
	"c": [freemarker_rule47,],
	"d": [freemarker_rule47,],
	"e": [freemarker_rule47,],
	"f": [freemarker_rule47,],
	"g": [freemarker_rule47,],
	"h": [freemarker_rule47,],
	"i": [freemarker_rule47,],
	"j": [freemarker_rule47,],
	"k": [freemarker_rule47,],
	"l": [freemarker_rule47,],
	"m": [freemarker_rule47,],
	"n": [freemarker_rule47,],
	"o": [freemarker_rule47,],
	"p": [freemarker_rule47,],
	"q": [freemarker_rule47,],
	"r": [freemarker_rule47,],
	"s": [freemarker_rule47,],
	"t": [freemarker_rule47,],
	"u": [freemarker_rule47,],
	"v": [freemarker_rule47,],
	"w": [freemarker_rule47,],
	"x": [freemarker_rule47,],
	"y": [freemarker_rule47,],
	"z": [freemarker_rule47,],
	"{": [freemarker_rule43,],
	"|": [freemarker_rule28,],
	"}": [freemarker_rule44,],
}

# Rules for freemarker_tags ruleset.

def freemarker_rule48(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::inquote",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule49(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::inquote",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule50(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for freemarker_tags ruleset.
rulesDict3 = {
	"\"": [freemarker_rule48,],
	"'": [freemarker_rule49,],
	"=": [freemarker_rule50,],
}

# Rules for freemarker_inquote ruleset.

def freemarker_rule51(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="${", end="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def freemarker_rule52(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="#{", end="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="freemarker::expression",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

# Rules dict for freemarker_inquote ruleset.
rulesDict4 = {
	"#": [freemarker_rule52,],
	"$": [freemarker_rule51,],
}

# Rules for freemarker_invalid ruleset.

# Rules dict for freemarker_invalid ruleset.
rulesDict5 = {}

# x.rulesDictDict for freemarker mode.
rulesDictDict = {
	"freemarker_expression": rulesDict2,
	"freemarker_inquote": rulesDict4,
	"freemarker_invalid": rulesDict5,
	"freemarker_main": rulesDict1,
	"freemarker_tags": rulesDict3,
}

# Import dict for freemarker mode.
importDict = {}


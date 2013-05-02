# Leo colorizer control file for md mode.
# This file is in the public domain.

# Properties for md mode.
properties = {
	"commentEnd": "-->",
	"commentStart": "<!--",
	"indentSize": "4",
	"maxLineLen": "120",
	"tabSize": "4",
}

# Attributes dict for md_main ruleset.
md_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for md_inline_markup ruleset.
md_inline_markup_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for md_block_html_tags ruleset.
md_block_html_tags_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for md_markdown ruleset.
md_markdown_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for md_link_label_definition ruleset.
md_link_label_definition_attributes_dict = {
	"default": "KEYWORD3",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for md_link_inline_url_title ruleset.
md_link_inline_url_title_attributes_dict = {
	"default": "KEYWORD3",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for md_link_inline_url_title_close ruleset.
md_link_inline_url_title_close_attributes_dict = {
	"default": "KEYWORD3",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for md_link_inline_label_close ruleset.
md_link_inline_label_close_attributes_dict = {
	"default": "LABEL",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for md_markdown_blockquote ruleset.
md_markdown_blockquote_attributes_dict = {
	"default": "LABEL",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for md mode.
attributesDictDict = {
	"md_block_html_tags": md_block_html_tags_attributes_dict,
	"md_inline_markup": md_inline_markup_attributes_dict,
	"md_link_inline_label_close": md_link_inline_label_close_attributes_dict,
	"md_link_inline_url_title": md_link_inline_url_title_attributes_dict,
	"md_link_inline_url_title_close": md_link_inline_url_title_close_attributes_dict,
	"md_link_label_definition": md_link_label_definition_attributes_dict,
	"md_main": md_main_attributes_dict,
	"md_markdown": md_markdown_attributes_dict,
	"md_markdown_blockquote": md_markdown_blockquote_attributes_dict,
}

# Keywords dict for md_main ruleset.
md_main_keywords_dict = {}

# Keywords dict for md_inline_markup ruleset.
md_inline_markup_keywords_dict = {}

# Keywords dict for md_block_html_tags ruleset.
md_block_html_tags_keywords_dict = {}

# Keywords dict for md_markdown ruleset.
md_markdown_keywords_dict = {}

# Keywords dict for md_link_label_definition ruleset.
md_link_label_definition_keywords_dict = {}

# Keywords dict for md_link_inline_url_title ruleset.
md_link_inline_url_title_keywords_dict = {}

# Keywords dict for md_link_inline_url_title_close ruleset.
md_link_inline_url_title_close_keywords_dict = {}

# Keywords dict for md_link_inline_label_close ruleset.
md_link_inline_label_close_keywords_dict = {}

# Keywords dict for md_markdown_blockquote ruleset.
md_markdown_blockquote_keywords_dict = {}

# Dictionary of keywords dictionaries for md mode.
keywordsDictDict = {
	"md_block_html_tags": md_block_html_tags_keywords_dict,
	"md_inline_markup": md_inline_markup_keywords_dict,
	"md_link_inline_label_close": md_link_inline_label_close_keywords_dict,
	"md_link_inline_url_title": md_link_inline_url_title_keywords_dict,
	"md_link_inline_url_title_close": md_link_inline_url_title_close_keywords_dict,
	"md_link_label_definition": md_link_label_definition_keywords_dict,
	"md_main": md_main_keywords_dict,
	"md_markdown": md_markdown_keywords_dict,
	"md_markdown_blockquote": md_markdown_blockquote_keywords_dict,
}

# Rules for md_main ruleset.

def md_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script", end="</script>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="<hr\\b([^<>])*?/?>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule3(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="markup", begin="<(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|noscript|form|fieldset|iframe|math|ins|del)\\b", end="</$1>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="md::block_html_tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq=" < ",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::inline_markup",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)


# Rules dict for md_main ruleset.
rulesDict1 = {
	" ": [md_rule4,],
	"<": [md_rule0,md_rule1,md_rule2,md_rule3,md_rule5,],
}

# Rules for md_inline_markup ruleset.


# Rules dict for md_inline_markup ruleset.
rulesDict2 = {}

# Rules for md_block_html_tags ruleset.

def md_rule6(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="[\\S]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule7(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="{1,3}[\\S]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule8(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="( {4}|\\t)",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="html::main", exclude_match=False)

def md_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for md_block_html_tags ruleset.
rulesDict3 = {
	"\"": [md_rule9,],
	"'": [md_rule10,],
	"(": [md_rule8,],
	"=": [md_rule11,],
	"[": [md_rule6,],
	"{": [md_rule7,],
}

# Rules for md_markdown ruleset.

def md_rule12(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="[ \\t]*(>[ \\t]{1})+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="md::markdown_blockquote", exclude_match=False)

def md_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="_",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="\\][",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="``` ruby", end="```",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="ruby::main",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="```", end="```",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule19(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule20(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule21(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule22(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule23(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule25(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule26(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
        at_line_start=False, at_whitespace_end=True, at_word_start=False,
        delegate="md::link_label_definition", exclude_match=False)

def md_rule27(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::link_inline_url_title",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def md_rule28(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def md_rule29(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

# Rules dict for md_markdown ruleset.
rulesDict4 = {
	"!": [md_rule27,],
	"#": [md_rule22,],
	"(": [md_rule19,md_rule20,md_rule28,md_rule29,],
	"*": [md_rule13,],
	"[": [md_rule12,md_rule21,md_rule23,md_rule24,md_rule25,],
	"\\": [md_rule15,md_rule16,md_rule26,],
	"_": [md_rule14,],
	"`": [md_rule17,md_rule18,],
}

# Rules for md_link_label_definition ruleset.

def md_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule31(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule32(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="(",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule33(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")


# Rules dict for md_link_label_definition ruleset.
rulesDict5 = {
	"\"": [md_rule31,],
	"(": [md_rule32,],
	")": [md_rule33,],
	"\\": [md_rule30,],
}

# Rules for md_link_inline_url_title ruleset.

def md_rule34(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule35(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\[", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::link_inline_label_close",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def md_rule36(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\(", end="\\)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::link_inline_url_title_close",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

# Rules dict for md_link_inline_url_title ruleset.
rulesDict6 = {
	"(": [md_rule36,],
	"[": [md_rule35,],
	"]": [md_rule34,],
}

# Rules for md_link_inline_url_title_close ruleset.

def md_rule37(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::main", exclude_match=False)

# Rules dict for md_link_inline_url_title_close ruleset.
rulesDict7 = {
	")": [md_rule37,],
}

# Rules for md_link_inline_label_close ruleset.

def md_rule38(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::main", exclude_match=False)

# Rules dict for md_link_inline_label_close ruleset.
rulesDict8 = {
	"]": [md_rule38,],
}

# Rules for md_markdown_blockquote ruleset.

def md_rule39(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq=" < ",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule40(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::inline_markup",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule41(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule42(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="_",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule43(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="\\][",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule44(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule45(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule46(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule47(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule48(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule49(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def md_rule50(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule51(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def md_rule52(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::link_label_definition", exclude_match=False)

def md_rule53(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="md::link_inline_url_title",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def md_rule54(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def md_rule55(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

# Rules dict for md_markdown_blockquote ruleset.
rulesDict9 = {
	" ": [md_rule39,],
	"!": [md_rule53,],
	"#": [md_rule48,],
	"(": [md_rule45,md_rule46,md_rule54,md_rule55,],
	"*": [md_rule41,],
	"<": [md_rule40,],
	"[": [md_rule47,md_rule49,md_rule50,md_rule51,],
	"\\": [md_rule43,md_rule44,md_rule52,],
	"_": [md_rule42,],
}

# x.rulesDictDict for md mode.
rulesDictDict = {
	"md_block_html_tags": rulesDict3,
	"md_inline_markup": rulesDict2,
	"md_link_inline_label_close": rulesDict8,
	"md_link_inline_url_title": rulesDict6,
	"md_link_inline_url_title_close": rulesDict7,
	"md_link_label_definition": rulesDict5,
	"md_main": rulesDict1,
	"md_markdown": rulesDict4,
	"md_markdown_blockquote": rulesDict9,
}

# Import dict for md mode.
importDict = {
	"md_inline_markup": ["html::tags",],
	"md_link_label_definition": ["md_link_label_definition::markdown",],
	"md_main": ["md_main::markdown",],
}


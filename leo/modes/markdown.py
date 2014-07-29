# Leo colorizer control file for markdown mode.
# This file is in the public domain.

# Properties for markdown mode.
properties = {
	"commentEnd": "-->",
	"commentStart": "<!--",
	"indentSize": "4",
	"maxLineLen": "120",
	"tabSize": "4",
}

# Attributes dict for markdown_main ruleset.
markdown_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for markdown_inline_markup ruleset.
markdown_inline_markup_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for markdown_block_html_tags ruleset.
markdown_block_html_tags_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for markdown_markdown ruleset.
markdown_markdown_attributes_dict = {
	"default": "MARKUP",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for markdown_link_label_definition ruleset.
markdown_link_label_definition_attributes_dict = {
	"default": "KEYWORD3",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for markdown_link_inline_url_title ruleset.
markdown_link_inline_url_title_attributes_dict = {
	"default": "KEYWORD3",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for markdown_link_inline_url_title_close ruleset.
markdown_link_inline_url_title_close_attributes_dict = {
	"default": "KEYWORD3",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for markdown_link_inline_label_close ruleset.
markdown_link_inline_label_close_attributes_dict = {
	"default": "LABEL",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for markdown_markdown_blockquote ruleset.
markdown_markdown_blockquote_attributes_dict = {
	"default": "LABEL",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for markdown mode.
attributesDictDict = {
	"markdown_block_html_tags": markdown_block_html_tags_attributes_dict,
	"markdown_inline_markup": markdown_inline_markup_attributes_dict,
	"markdown_link_inline_label_close": markdown_link_inline_label_close_attributes_dict,
	"markdown_link_inline_url_title": markdown_link_inline_url_title_attributes_dict,
	"markdown_link_inline_url_title_close": markdown_link_inline_url_title_close_attributes_dict,
	"markdown_link_label_definition": markdown_link_label_definition_attributes_dict,
	"markdown_main": markdown_main_attributes_dict,
	"markdown_markdown": markdown_markdown_attributes_dict,
	"markdown_markdown_blockquote": markdown_markdown_blockquote_attributes_dict,
}

# Keywords dict for markdown_main ruleset.
markdown_main_keywords_dict = {}

# Keywords dict for markdown_inline_markup ruleset.
markdown_inline_markup_keywords_dict = {}

# Keywords dict for markdown_block_html_tags ruleset.
markdown_block_html_tags_keywords_dict = {}

# Keywords dict for markdown_markdown ruleset.
markdown_markdown_keywords_dict = {}

# Keywords dict for markdown_link_label_definition ruleset.
markdown_link_label_definition_keywords_dict = {}

# Keywords dict for markdown_link_inline_url_title ruleset.
markdown_link_inline_url_title_keywords_dict = {}

# Keywords dict for markdown_link_inline_url_title_close ruleset.
markdown_link_inline_url_title_close_keywords_dict = {}

# Keywords dict for markdown_link_inline_label_close ruleset.
markdown_link_inline_label_close_keywords_dict = {}

# Keywords dict for markdown_markdown_blockquote ruleset.
markdown_markdown_blockquote_keywords_dict = {}

# Dictionary of keywords dictionaries for markdown mode.
keywordsDictDict = {
	"markdown_block_html_tags": markdown_block_html_tags_keywords_dict,
	"markdown_inline_markup": markdown_inline_markup_keywords_dict,
	"markdown_link_inline_label_close": markdown_link_inline_label_close_keywords_dict,
	"markdown_link_inline_url_title": markdown_link_inline_url_title_keywords_dict,
	"markdown_link_inline_url_title_close": markdown_link_inline_url_title_close_keywords_dict,
	"markdown_link_label_definition": markdown_link_label_definition_keywords_dict,
	"markdown_main": markdown_main_keywords_dict,
	"markdown_markdown": markdown_markdown_keywords_dict,
	"markdown_markdown_blockquote": markdown_markdown_blockquote_keywords_dict,
}

# Rules for markdown_main ruleset.

def markdown_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script", end="</script>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="<hr\\b([^<>])*?/?>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule3(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="markup", begin="<(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|noscript|form|fieldset|iframe|math|ins|del)\\b", end="</$1>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::block_html_tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq=" < ",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::inline_markup",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)


# Rules dict for markdown_main ruleset.
rulesDict1 = {
	" ": [markdown_rule4,],
	"<": [markdown_rule0,markdown_rule1,markdown_rule2,markdown_rule3,markdown_rule5,],
}

# Rules for markdown_inline_markup ruleset.


# Rules dict for markdown_inline_markup ruleset.
rulesDict2 = {}

# Rules for markdown_block_html_tags ruleset.

def markdown_rule6(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="[\\S]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule7(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="{1,3}[\\S]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule8(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="( {4}|\\t)",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="html::main", exclude_match=False)

def markdown_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for markdown_block_html_tags ruleset.
rulesDict3 = {
	"\"": [markdown_rule9,],
	"'": [markdown_rule10,],
	"(": [markdown_rule8,],
	"=": [markdown_rule11,],
	"[": [markdown_rule6,],
	"{": [markdown_rule7,],
}

# Rules for markdown_markdown ruleset.

def markdown_rule12(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="[ \\t]*(>[ \\t]{1})+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::markdown_blockquote", exclude_match=False)

def markdown_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="_",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="\\][",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="``` ruby", end="```",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="ruby::main",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="```", end="```",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule19(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule20(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule21(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule22(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule23(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule25(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule26(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
        at_line_start=False, at_whitespace_end=True, at_word_start=False,
        delegate="markdown::link_label_definition", exclude_match=False)

def markdown_rule27(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::link_inline_url_title",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def markdown_rule28(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def markdown_rule29(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

# Rules dict for markdown_markdown ruleset.
rulesDict4 = {
	"!": [markdown_rule27,],
	"#": [markdown_rule22,],
	"(": [markdown_rule19,markdown_rule20,markdown_rule28,markdown_rule29,],
	"*": [markdown_rule13,],
	"[": [markdown_rule12,markdown_rule21,markdown_rule23,markdown_rule24,markdown_rule25,],
	"\\": [markdown_rule15,markdown_rule16,markdown_rule26,],
	"_": [markdown_rule14,],
	"`": [markdown_rule17,markdown_rule18,],
}

# Rules for markdown_link_label_definition ruleset.

def markdown_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule31(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule32(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="(",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule33(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")


# Rules dict for markdown_link_label_definition ruleset.
rulesDict5 = {
	"\"": [markdown_rule31,],
	"(": [markdown_rule32,],
	")": [markdown_rule33,],
	"\\": [markdown_rule30,],
}

# Rules for markdown_link_inline_url_title ruleset.

def markdown_rule34(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule35(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\[", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::link_inline_label_close",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def markdown_rule36(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\(", end="\\)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::link_inline_url_title_close",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

# Rules dict for markdown_link_inline_url_title ruleset.
rulesDict6 = {
	"(": [markdown_rule36,],
	"[": [markdown_rule35,],
	"]": [markdown_rule34,],
}

# Rules for markdown_link_inline_url_title_close ruleset.

def markdown_rule37(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::main", exclude_match=False)

# Rules dict for markdown_link_inline_url_title_close ruleset.
rulesDict7 = {
	")": [markdown_rule37,],
}

# Rules for markdown_link_inline_label_close ruleset.

def markdown_rule38(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::main", exclude_match=False)

# Rules dict for markdown_link_inline_label_close ruleset.
rulesDict8 = {
	"]": [markdown_rule38,],
}

# Rules for markdown_markdown_blockquote ruleset.

def markdown_rule39(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq=" < ",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule40(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::inline_markup",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule41(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule42(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="_",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule43(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="\\][",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule44(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule45(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule46(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule47(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule48(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule49(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def markdown_rule50(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule51(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def markdown_rule52(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::link_label_definition", exclude_match=False)

def markdown_rule53(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="markdown::link_inline_url_title",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def markdown_rule54(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def markdown_rule55(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

# Rules dict for markdown_markdown_blockquote ruleset.
rulesDict9 = {
	" ": [markdown_rule39,],
	"!": [markdown_rule53,],
	"#": [markdown_rule48,],
	"(": [markdown_rule45,markdown_rule46,markdown_rule54,markdown_rule55,],
	"*": [markdown_rule41,],
	"<": [markdown_rule40,],
	"[": [markdown_rule47,markdown_rule49,markdown_rule50,markdown_rule51,],
	"\\": [markdown_rule43,markdown_rule44,markdown_rule52,],
	"_": [markdown_rule42,],
}

# x.rulesDictDict for markdown mode.
rulesDictDict = {
	"markdown_block_html_tags": rulesDict3,
	"markdown_inline_markup": rulesDict2,
	"markdown_link_inline_label_close": rulesDict8,
	"markdown_link_inline_url_title": rulesDict6,
	"markdown_link_inline_url_title_close": rulesDict7,
	"markdown_link_label_definition": rulesDict5,
	"markdown_main": rulesDict1,
	"markdown_markdown": rulesDict4,
	"markdown_markdown_blockquote": rulesDict9,
}

# Import dict for markdown mode.
importDict = {
	"markdown_inline_markup": ["html::tags",],
	"markdown_link_label_definition": ["markdown_link_label_definition::markdown",],
	"markdown_main": ["markdown_main::markdown",],
}


# Leo colorizer control file for asp mode.
# This file is in the public domain.

# Properties for asp mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for asp_main ruleset.
asp_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asp_aspvb ruleset.
asp_aspvb_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asp_aspjs ruleset.
asp_aspjs_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asp_asppl ruleset.
asp_asppl_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asp_aspvb_tags ruleset.
asp_aspvb_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asp_aspjs_tags ruleset.
asp_aspjs_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asp_asppl_tags ruleset.
asp_asppl_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for asp mode.
attributesDictDict = {
    "asp_aspjs": asp_aspjs_attributes_dict,
    "asp_aspjs_tags": asp_aspjs_tags_attributes_dict,
    "asp_asppl": asp_asppl_attributes_dict,
    "asp_asppl_tags": asp_asppl_tags_attributes_dict,
    "asp_aspvb": asp_aspvb_attributes_dict,
    "asp_aspvb_tags": asp_aspvb_tags_attributes_dict,
    "asp_main": asp_main_attributes_dict,
}

# Keywords dict for asp_main ruleset.
asp_main_keywords_dict = {}

# Keywords dict for asp_aspvb ruleset.
asp_aspvb_keywords_dict = {}

# Keywords dict for asp_aspjs ruleset.
asp_aspjs_keywords_dict = {}

# Keywords dict for asp_asppl ruleset.
asp_asppl_keywords_dict = {}

# Keywords dict for asp_aspvb_tags ruleset.
asp_aspvb_tags_keywords_dict = {}

# Keywords dict for asp_aspjs_tags ruleset.
asp_aspjs_tags_keywords_dict = {}

# Keywords dict for asp_asppl_tags ruleset.
asp_asppl_tags_keywords_dict = {}

# Dictionary of keywords dictionaries for asp mode.
keywordsDictDict = {
    "asp_aspjs": asp_aspjs_keywords_dict,
    "asp_aspjs_tags": asp_aspjs_tags_keywords_dict,
    "asp_asppl": asp_asppl_keywords_dict,
    "asp_asppl_tags": asp_asppl_tags_keywords_dict,
    "asp_aspvb": asp_aspvb_keywords_dict,
    "asp_aspvb_tags": asp_aspvb_tags_keywords_dict,
    "asp_main": asp_main_keywords_dict,
}

# Rules for asp_main ruleset.

def asp_rule0(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="<%@LANGUAGE=\"VBSCRIPT\"%>",
          delegate="asp::aspvb")

def asp_rule1(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="<%@LANGUAGE=\"JSCRIPT\"%>",
          delegate="asp::aspjs")

def asp_rule2(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="<%@LANGUAGE=\"JAVASCRIPT\"%>",
          delegate="asp::aspjs")

def asp_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="<%@LANGUAGE=\"PERLSCRIPT\"%>",
          delegate="asp::asppl")

def asp_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
          delegate="vbscript::main")

def asp_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"vbscript\" runat=\"server\">", end="</script>",
          delegate="vbscript::main")

def asp_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"perlscript\" runat=\"server\">", end="</script>",
          delegate="perl::main")

def asp_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\">", end="</script>",
          delegate="javascript::main")

def asp_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\">", end="</script>",
          delegate="javascript::main")

def asp_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script>", end="</script>",
          delegate="javascript::main")

def asp_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<!--#", end="-->")

def asp_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def asp_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE>", end="</STYLE>",
          delegate="css::main")

def asp_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="asp::aspvb_tags")

def asp_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for asp_main ruleset.
rulesDict1 = {
    "&": [asp_rule16,],
    "<": [asp_rule0, asp_rule1, asp_rule2, asp_rule3, asp_rule4, asp_rule5, asp_rule6, asp_rule7, asp_rule8, asp_rule9, asp_rule10, asp_rule11, asp_rule12, asp_rule13, asp_rule14, asp_rule15,],
}

# Rules for asp_aspvb ruleset.

def asp_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
          delegate="vbscript::main")

def asp_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"vbscript\" runat=\"server\">", end="</script>",
          delegate="vbscript::main")

def asp_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule21(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"perlscript\" runat=\"server\">", end="</script>",
          delegate="perl::main")

def asp_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\">", end="</script>",
          delegate="javascript::main")

def asp_rule23(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\">", end="</script>",
          delegate="javascript::main")

def asp_rule24(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script>", end="</script>",
          delegate="javascript::main")

def asp_rule25(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<!--#", end="-->")

def asp_rule26(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def asp_rule27(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE>", end="</STYLE>",
          delegate="css::main")

def asp_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="</", end=">",
          delegate="asp::aspvb_tags")

def asp_rule29(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="asp::aspvb_tags")

def asp_rule30(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for asp_aspvb ruleset.
rulesDict2 = {
    "&": [asp_rule30,],
    "<": [asp_rule17, asp_rule18, asp_rule19, asp_rule20, asp_rule21, asp_rule22, asp_rule23, asp_rule24, asp_rule25, asp_rule26, asp_rule27, asp_rule28, asp_rule29,],
}

# Rules for asp_aspjs ruleset.

def asp_rule31(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
          delegate="javascript::main")

def asp_rule32(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"vbscript\" runat=\"server\">", end="</script>",
          delegate="vbscript::main")

def asp_rule33(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule34(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule35(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"perlscript\" runat=\"server\">", end="</script>",
          delegate="perl::main")

def asp_rule36(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\">", end="</script>",
          delegate="javascript::main")

def asp_rule37(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\">", end="</script>",
          delegate="javascript::main")

def asp_rule38(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script>", end="</script>",
          delegate="javascript::main")

def asp_rule39(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<!--#", end="-->")

def asp_rule40(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def asp_rule41(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE>", end="</STYLE>",
          delegate="css::main")

def asp_rule42(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="</", end=">",
          delegate="asp::aspjs_tags")

def asp_rule43(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="asp::aspjs_tags")

def asp_rule44(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for asp_aspjs ruleset.
rulesDict3 = {
    "&": [asp_rule44,],
    "<": [asp_rule31, asp_rule32, asp_rule33, asp_rule34, asp_rule35, asp_rule36, asp_rule37, asp_rule38, asp_rule39, asp_rule40, asp_rule41, asp_rule42, asp_rule43,],
}

# Rules for asp_asppl ruleset.

def asp_rule45(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
          delegate="perl::main")

def asp_rule46(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"vbscript\" runat=\"server\">", end="</script>",
          delegate="vbscript::main")

def asp_rule47(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule48(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\" runat=\"server\">", end="</script>",
          delegate="javascript::main")

def asp_rule49(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"perlscript\" runat=\"server\">", end="</script>",
          delegate="perl::main")

def asp_rule50(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\">", end="</script>",
          delegate="asp::asppl_csjs")

def asp_rule51(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\">", end="</script>",
          delegate="asp::asppl_csjs")

def asp_rule52(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script>", end="</script>",
          delegate="asp::asppl_csjs")

def asp_rule53(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<!--#", end="-->")

def asp_rule54(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def asp_rule55(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE>", end="</STYLE>",
          delegate="css::main")

def asp_rule56(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="</", end=">",
          delegate="asp::asppl_tags")

def asp_rule57(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="asp::asppl_tags")

def asp_rule58(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for asp_asppl ruleset.
rulesDict4 = {
    "&": [asp_rule58,],
    "<": [asp_rule45, asp_rule46, asp_rule47, asp_rule48, asp_rule49, asp_rule50, asp_rule51, asp_rule52, asp_rule53, asp_rule54, asp_rule55, asp_rule56, asp_rule57,],
}

# Rules for asp_aspvb_tags ruleset.

def asp_rule59(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
          delegate="vbscript::main")

# Rules dict for asp_aspvb_tags ruleset.
rulesDict5 = {
    "<": [asp_rule59,],
}

# Rules for asp_aspjs_tags ruleset.

def asp_rule60(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
          delegate="javascript::main")

# Rules dict for asp_aspjs_tags ruleset.
rulesDict6 = {
    "<": [asp_rule60,],
}

# Rules for asp_asppl_tags ruleset.

def asp_rule61(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<%", end="%>",
          delegate="perl::main")

# Rules dict for asp_asppl_tags ruleset.
rulesDict7 = {
    "<": [asp_rule61,],
}

# x.rulesDictDict for asp mode.
rulesDictDict = {
    "asp_aspjs": rulesDict3,
    "asp_aspjs_tags": rulesDict6,
    "asp_asppl": rulesDict4,
    "asp_asppl_tags": rulesDict7,
    "asp_aspvb": rulesDict2,
    "asp_aspvb_tags": rulesDict5,
    "asp_main": rulesDict1,
}

# Import dict for asp mode.
importDict = {}

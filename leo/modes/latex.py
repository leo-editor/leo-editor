# Leo colorizer control file for latex mode.
# This file is in the public domain.

# Properties for latex mode.
properties = {
    "lineComment": "%",
    "noWordSep": "\\",
}

# Attributes dict for latex_main ruleset.
latex_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for latex_mathmode ruleset.
latex_mathmode_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for latex_arraymode ruleset.
latex_arraymode_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for latex_tabularmode ruleset.
latex_tabularmode_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for latex_tabbingmode ruleset.
latex_tabbingmode_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for latex_picturemode ruleset.
latex_picturemode_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for latex mode.
attributesDictDict = {
    "latex_arraymode": latex_arraymode_attributes_dict,
    "latex_main": latex_main_attributes_dict,
    "latex_mathmode": latex_mathmode_attributes_dict,
    "latex_picturemode": latex_picturemode_attributes_dict,
    "latex_tabbingmode": latex_tabbingmode_attributes_dict,
    "latex_tabularmode": latex_tabularmode_attributes_dict,
}

# Keywords dict for latex_main ruleset.
latex_main_keywords_dict = {}

# Keywords dict for latex_mathmode ruleset.
latex_mathmode_keywords_dict = {}

# Keywords dict for latex_arraymode ruleset.
latex_arraymode_keywords_dict = {}

# Keywords dict for latex_tabularmode ruleset.
latex_tabularmode_keywords_dict = {}

# Keywords dict for latex_tabbingmode ruleset.
latex_tabbingmode_keywords_dict = {}

# Keywords dict for latex_picturemode ruleset.
latex_picturemode_keywords_dict = {}

# Dictionary of keywords dictionaries for latex mode.
keywordsDictDict = {
    "latex_arraymode": latex_arraymode_keywords_dict,
    "latex_main": latex_main_keywords_dict,
    "latex_mathmode": latex_mathmode_keywords_dict,
    "latex_picturemode": latex_picturemode_keywords_dict,
    "latex_tabbingmode": latex_tabbingmode_keywords_dict,
    "latex_tabularmode": latex_tabularmode_keywords_dict,
}

# Rules for latex_main ruleset.

def latex_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="__NormalMode__")

def latex_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def latex_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal4", begin="``", end="''")

def latex_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="`", end="'")

def latex_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def latex_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\"")

def latex_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="`")

def latex_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#1")

def latex_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#2")

def latex_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#3")

def latex_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#4")

def latex_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#5")

def latex_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#6")

def latex_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#7")

def latex_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#8")

def latex_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="function", seq="#9")

def latex_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\tabs")

def latex_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\tabset")

def latex_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\tabsdone")

def latex_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\cleartabs")

def latex_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\settabs")

def latex_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\tabalign")

def latex_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\+")

def latex_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\pageno")

def latex_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\headline")

def latex_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\footline")

def latex_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\normalbottom")

def latex_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\folio")

def latex_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\nopagenumbers")

def latex_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\advancepageno")

def latex_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\pagebody")

def latex_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\plainoutput")

def latex_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\pagecontents")

def latex_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\makeheadline")

def latex_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\makefootline")

def latex_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\dosupereject")

def latex_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\footstrut")

def latex_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\vfootnote")

def latex_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\topins")

def latex_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\topinsert")

def latex_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\midinsert")

def latex_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\pageinsert")

def latex_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\endinsert")

def latex_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\fivei")

def latex_rule44(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\fiverm")

def latex_rule45(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\fivesy")

def latex_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\fivebf")

def latex_rule47(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\seveni")

def latex_rule48(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\sevenbf")

def latex_rule49(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\sevensy")

def latex_rule50(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\teni")

def latex_rule51(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\oldstyle")

def latex_rule52(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\eqalign")

def latex_rule53(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\eqalignno")

def latex_rule54(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\leqalignno")

def latex_rule55(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="$$")

def latex_rule56(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\beginsection")

def latex_rule57(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\bye")

def latex_rule58(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\magnification")

def latex_rule59(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="#")

def latex_rule60(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="&")

def latex_rule61(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="_")

def latex_rule62(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\\~")

def latex_rule63(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="$", end="$",
          delegate="latex::mathmode")

def latex_rule64(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\(", end="\\)",
          delegate="latex::mathmode")

def latex_rule65(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\[", end="\\]",
          delegate="latex::mathmode")

def latex_rule66(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{math}", end="\\end{math}",
          delegate="latex::mathmode")

def latex_rule67(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{displaymath}", end="\\end{displaymath}",
          delegate="latex::mathmode")

def latex_rule68(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{equation}", end="\\end{equation}",
          delegate="latex::mathmode")

def latex_rule69(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\ensuremath{", end="}",
          delegate="latex::mathmode")

def latex_rule70(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{eqnarray}", end="\\end{eqnarray}",
          delegate="latex::arraymode")

def latex_rule71(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{eqnarray*}", end="\\end{eqnarray*}",
          delegate="latex::arraymode")

def latex_rule72(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{tabular}", end="\\end{tabular}",
          delegate="latex::tabularmode")

def latex_rule73(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{tabular*}", end="\\end{tabular*}",
          delegate="latex::tabularmode")

def latex_rule74(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{tabbing}", end="\\end{tabbing}",
          delegate="latex::tabbingmode")

def latex_rule75(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{picture}", end="\\end{picture}",
          delegate="latex::picturemode")

def latex_rule76(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def latex_rule77(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="}")

def latex_rule78(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="{")

def latex_rule79(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="totalnumber")

def latex_rule80(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="topnumber")

def latex_rule81(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="tocdepth")

def latex_rule82(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="secnumdepth")

def latex_rule83(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="dbltopnumber")

def latex_rule84(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="]")

def latex_rule85(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\~{")

def latex_rule86(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\~")

def latex_rule87(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\}")

def latex_rule88(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\|")

def latex_rule89(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\{")

def latex_rule90(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\width")

def latex_rule91(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\whiledo{")

def latex_rule92(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\v{")

def latex_rule93(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vspace{")

def latex_rule94(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vspace*{")

def latex_rule95(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vfill")

def latex_rule96(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\verb*")

def latex_rule97(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\verb")

def latex_rule98(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\value{")

def latex_rule99(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\v")

def latex_rule100(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\u{")

def latex_rule101(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usepackage{")

def latex_rule102(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usepackage[")

def latex_rule103(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usecounter{")

def latex_rule104(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usebox{")

def latex_rule105(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upshape")

def latex_rule106(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\unboldmath{")

def latex_rule107(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\u")

def latex_rule108(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\t{")

def latex_rule109(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typeout{")

def latex_rule110(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typein{")

def latex_rule111(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typein[")

def latex_rule112(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\twocolumn[")

def latex_rule113(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\twocolumn")

def latex_rule114(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ttfamily")

def latex_rule115(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\totalheight")

def latex_rule116(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\topsep")

def latex_rule117(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\topfraction")

def latex_rule118(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\today")

def latex_rule119(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\title{")

def latex_rule120(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tiny")

def latex_rule121(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\thispagestyle{")

def latex_rule122(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thinlines")

def latex_rule123(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thicklines")

def latex_rule124(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\thanks{")

def latex_rule125(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textwidth")

def latex_rule126(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textup{")

def latex_rule127(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\texttt{")

def latex_rule128(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsl{")

def latex_rule129(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsf{")

def latex_rule130(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsc{")

def latex_rule131(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textrm{")

def latex_rule132(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textnormal{")

def latex_rule133(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textmd{")

def latex_rule134(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textit{")

def latex_rule135(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textfraction")

def latex_rule136(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textfloatsep")

def latex_rule137(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textcolor{")

def latex_rule138(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textbf{")

def latex_rule139(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tableofcontents")

def latex_rule140(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\tabcolsep")

def latex_rule141(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\tabbingsep")

def latex_rule142(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\t")

def latex_rule143(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\symbol{")

def latex_rule144(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\suppressfloats[")

def latex_rule145(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\suppressfloats")

def latex_rule146(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection{")

def latex_rule147(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection[")

def latex_rule148(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection*{")

def latex_rule149(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection{")

def latex_rule150(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection[")

def latex_rule151(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection*{")

def latex_rule152(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph{")

def latex_rule153(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph[")

def latex_rule154(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph*{")

def latex_rule155(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stretch{")

def latex_rule156(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stepcounter{")

def latex_rule157(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallskip")

def latex_rule158(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\small")

def latex_rule159(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\slshape")

def latex_rule160(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sloppy")

def latex_rule161(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sffamily")

def latex_rule162(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settowidth{")

def latex_rule163(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settoheight{")

def latex_rule164(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settodepth{")

def latex_rule165(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\setlength{")

def latex_rule166(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\setcounter{")

def latex_rule167(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section{")

def latex_rule168(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section[")

def latex_rule169(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section*{")

def latex_rule170(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scshape")

def latex_rule171(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scriptsize")

def latex_rule172(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\scalebox{")

def latex_rule173(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\sbox{")

def latex_rule174(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\savebox{")

def latex_rule175(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rule{")

def latex_rule176(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rule[")

def latex_rule177(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rp,am{")

def latex_rule178(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rotatebox{")

def latex_rule179(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rmfamily")

def latex_rule180(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\rightmargin")

def latex_rule181(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\reversemarginpar")

def latex_rule182(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\resizebox{")

def latex_rule183(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\resizebox*{")

def latex_rule184(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\renewenvironment{")

def latex_rule185(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\renewcommand{")

def latex_rule186(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ref{")

def latex_rule187(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\refstepcounter")

def latex_rule188(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\raisebox{")

def latex_rule189(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\raggedright")

def latex_rule190(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\raggedleft")

def latex_rule191(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\qbeziermax")

def latex_rule192(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\providecommand{")

def latex_rule193(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\protect")

def latex_rule194(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\printindex")

def latex_rule195(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pounds")

def latex_rule196(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part{")

def latex_rule197(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\partopsep")

def latex_rule198(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part[")

def latex_rule199(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part*{")

def latex_rule200(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parskip")

def latex_rule201(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parsep")

def latex_rule202(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parindent")

def latex_rule203(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\parbox{")

def latex_rule204(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\parbox[")

def latex_rule205(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph{")

def latex_rule206(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph[")

def latex_rule207(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph*{")

def latex_rule208(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\par")

def latex_rule209(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagestyle{")

def latex_rule210(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pageref{")

def latex_rule211(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagenumbering{")

def latex_rule212(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagecolor{")

def latex_rule213(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagebreak[")

def latex_rule214(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pagebreak")

def latex_rule215(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\onecolumn")

def latex_rule216(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalsize")

def latex_rule217(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalmarginpar")

def latex_rule218(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalfont")

def latex_rule219(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nopagebreak[")

def latex_rule220(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nopagebreak")

def latex_rule221(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nonfrenchspacing")

def latex_rule222(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nolinebreak[")

def latex_rule223(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nolinebreak")

def latex_rule224(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\noindent")

def latex_rule225(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nocite{")

def latex_rule226(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newtheorem{")

def latex_rule227(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newsavebox{")

def latex_rule228(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\newpage")

def latex_rule229(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newlength{")

def latex_rule230(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newenvironment{")

def latex_rule231(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newcounter{")

def latex_rule232(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newcommand{")

def latex_rule233(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\medskip")

def latex_rule234(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mdseries")

def latex_rule235(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mbox{")

def latex_rule236(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mbox{")

def latex_rule237(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\mathindent")

def latex_rule238(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\mathindent")

def latex_rule239(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\markright{")

def latex_rule240(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\markboth{")

def latex_rule241(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\marginpar{")

def latex_rule242(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparwidth")

def latex_rule243(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparsep")

def latex_rule244(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparpush")

def latex_rule245(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\marginpar[")

def latex_rule246(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\maketitle")

def latex_rule247(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\makelabel")

def latex_rule248(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\makeindex")

def latex_rule249(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\makeglossary")

def latex_rule250(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\makebox{")

def latex_rule251(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\makebox[")

def latex_rule252(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\listparindent")

def latex_rule253(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listoftables")

def latex_rule254(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listoffigures")

def latex_rule255(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listfiles")

def latex_rule256(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\linewidth")

def latex_rule257(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\linethickness{")

def latex_rule258(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\linebreak[")

def latex_rule259(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\linebreak")

def latex_rule260(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\lengthtest{")

def latex_rule261(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginvi")

def latex_rule262(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginv")

def latex_rule263(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginiv")

def latex_rule264(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginiii")

def latex_rule265(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginii")

def latex_rule266(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmargini")

def latex_rule267(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmargin")

def latex_rule268(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\large")

def latex_rule269(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\label{")

def latex_rule270(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\labelwidth")

def latex_rule271(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\labelsep")

def latex_rule272(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\jot")

def latex_rule273(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\itshape")

def latex_rule274(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\itemsep")

def latex_rule275(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\itemindent")

def latex_rule276(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\item[")

def latex_rule277(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\item")

def latex_rule278(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\isodd{")

def latex_rule279(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\intextsep")

def latex_rule280(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\input{")

def latex_rule281(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\index{")

def latex_rule282(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\indent")

def latex_rule283(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\include{")

def latex_rule284(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includeonly{")

def latex_rule285(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics{")

def latex_rule286(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics[")

def latex_rule287(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics*{")

def latex_rule288(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics*[")

def latex_rule289(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ifthenelse{")

def latex_rule290(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hyphenation{")

def latex_rule291(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\huge")

def latex_rule292(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hspace{")

def latex_rule293(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hspace*{")

def latex_rule294(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hfill")

def latex_rule295(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\height")

def latex_rule296(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\glossary{")

def latex_rule297(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fussy")

def latex_rule298(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\frenchspacing")

def latex_rule299(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\framebox{")

def latex_rule300(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\framebox[")

def latex_rule301(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fragile")

def latex_rule302(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnote{")

def latex_rule303(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotetext{")

def latex_rule304(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotetext[")

def latex_rule305(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\footnotesize")

def latex_rule306(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\footnotesep")

def latex_rule307(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\footnoterule")

def latex_rule308(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotemark[")

def latex_rule309(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\footnotemark")

def latex_rule310(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnote[")

def latex_rule311(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fnsymbol{")

def latex_rule312(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\floatsep")

def latex_rule313(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\floatpagefraction")

def latex_rule314(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fill")

def latex_rule315(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fcolorbox{")

def latex_rule316(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fbox{")

def latex_rule317(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\fboxsep")

def latex_rule318(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\fboxrule")

def latex_rule319(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\equal{")

def latex_rule320(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ensuremath{")

def latex_rule321(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\enlargethispage{")

def latex_rule322(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\enlargethispage*{")

def latex_rule323(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\end{")

def latex_rule324(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\emph{")

def latex_rule325(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\d{")

def latex_rule326(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\doublerulesep")

def latex_rule327(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\documentclass{")

def latex_rule328(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\documentclass[")

def latex_rule329(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\depth")

def latex_rule330(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\definecolor{")

def latex_rule331(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ddag")

def latex_rule332(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dbltopfraction")

def latex_rule333(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dbltextfloatsep")

def latex_rule334(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dblfloatsep")

def latex_rule335(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dblfloatpagefraction")

def latex_rule336(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\date{")

def latex_rule337(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dag")

def latex_rule338(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\d")

def latex_rule339(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\c{")

def latex_rule340(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\copyright")

def latex_rule341(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnwidth")

def latex_rule342(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnseprule")

def latex_rule343(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnsep")

def latex_rule344(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\color{")

def latex_rule345(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\colorbox{")

def latex_rule346(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\clearpage")

def latex_rule347(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cleardoublepage")

def latex_rule348(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cite{")

def latex_rule349(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cite[")

def latex_rule350(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter{")

def latex_rule351(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter[")

def latex_rule352(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter*{")

def latex_rule353(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\centering")

def latex_rule354(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\caption{")

def latex_rule355(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\caption[")

def latex_rule356(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\c")

def latex_rule357(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\b{")

def latex_rule358(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bottomnumber")

def latex_rule359(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bottomfraction")

def latex_rule360(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boolean{")

def latex_rule361(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boldmath{")

def latex_rule362(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigskip")

def latex_rule363(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bibliography{")

def latex_rule364(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bibliographystyle{")

def latex_rule365(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bibindent")

def latex_rule366(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bfseries")

def latex_rule367(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\belowdisplayskip")

def latex_rule368(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\belowdisplayshortskip")

def latex_rule369(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\begin{")

def latex_rule370(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\baselinestretch")

def latex_rule371(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\baselineskip")

def latex_rule372(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\b")

def latex_rule373(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\author{")

def latex_rule374(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arraystgretch")

def latex_rule375(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arrayrulewidth")

def latex_rule376(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arraycolsep")

def latex_rule377(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\arabic{")

def latex_rule378(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\appendix")

def latex_rule379(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\alph{")

def latex_rule380(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addvspace{")

def latex_rule381(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtolength{")

def latex_rule382(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtocounter{")

def latex_rule383(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtocontents{")

def latex_rule384(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addcontentsline{")

def latex_rule385(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\abovedisplayskip")

def latex_rule386(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\abovedisplayshortskip")

def latex_rule387(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\`{")

def latex_rule388(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\`")

def latex_rule389(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\_")

def latex_rule390(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\^{")

def latex_rule391(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\^")

def latex_rule392(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\\[")

def latex_rule393(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\\*[")

def latex_rule394(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\*")

def latex_rule395(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\")

def latex_rule396(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\TeX")

def latex_rule397(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\S")

def latex_rule398(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Roman{")

def latex_rule399(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\P")

def latex_rule400(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Large")

def latex_rule401(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\LaTeX")

def latex_rule402(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\LARGE")

def latex_rule403(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\H{")

def latex_rule404(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Huge")

def latex_rule405(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\H")

def latex_rule406(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Alph{")

def latex_rule407(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\@")

def latex_rule408(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\={")

def latex_rule409(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\=")

def latex_rule410(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\.{")

def latex_rule411(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\.")

def latex_rule412(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\-")

def latex_rule413(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\,")

def latex_rule414(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\'{")

def latex_rule415(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\'")

def latex_rule416(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\&")

def latex_rule417(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\%")

def latex_rule418(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\$")

def latex_rule419(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\#")

def latex_rule420(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\"{")

def latex_rule421(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\"")

def latex_rule422(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def latex_rule423(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="[")

def latex_rule424(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="---")

def latex_rule425(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="--")

def latex_rule426(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def latex_rule427(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="\\")

# Rules dict for latex_main ruleset.
rulesDict1 = {
    "\"": [latex_rule4, latex_rule5,],
    "#": [latex_rule7, latex_rule8, latex_rule9, latex_rule10, latex_rule11, latex_rule12, latex_rule13, latex_rule14, latex_rule15, latex_rule59,],
    "$": [latex_rule55, latex_rule63,],
    "%": [latex_rule1,],
    "&": [latex_rule60,],
    "-": [latex_rule424, latex_rule425, latex_rule426,],
    "[": [latex_rule423,],
    "\\": [latex_rule16, latex_rule17, latex_rule18, latex_rule19, latex_rule20, latex_rule21, latex_rule22, latex_rule23, latex_rule24, latex_rule25, latex_rule26, latex_rule27, latex_rule28, latex_rule29, latex_rule30, latex_rule31, latex_rule32, latex_rule33, latex_rule34, latex_rule35, latex_rule36, latex_rule37, latex_rule38, latex_rule39, latex_rule40, latex_rule41, latex_rule42, latex_rule43, latex_rule44, latex_rule45, latex_rule46, latex_rule47, latex_rule48, latex_rule49, latex_rule50, latex_rule51, latex_rule52, latex_rule53, latex_rule54, latex_rule56, latex_rule57, latex_rule58, latex_rule62, latex_rule64, latex_rule65, latex_rule66, latex_rule67, latex_rule68, latex_rule69, latex_rule70, latex_rule71, latex_rule72, latex_rule73, latex_rule74, latex_rule75, latex_rule85, latex_rule86, latex_rule87, latex_rule88, latex_rule89, latex_rule90, latex_rule91, latex_rule92, latex_rule93, latex_rule94, latex_rule95, latex_rule96, latex_rule97, latex_rule98, latex_rule99, latex_rule100, latex_rule101, latex_rule102, latex_rule103, latex_rule104, latex_rule105, latex_rule106, latex_rule107, latex_rule108, latex_rule109, latex_rule110, latex_rule111, latex_rule112, latex_rule113, latex_rule114, latex_rule115, latex_rule116, latex_rule117, latex_rule118, latex_rule119, latex_rule120, latex_rule121, latex_rule122, latex_rule123, latex_rule124, latex_rule125, latex_rule126, latex_rule127, latex_rule128, latex_rule129, latex_rule130, latex_rule131, latex_rule132, latex_rule133, latex_rule134, latex_rule135, latex_rule136, latex_rule137, latex_rule138, latex_rule139, latex_rule140, latex_rule141, latex_rule142, latex_rule143, latex_rule144, latex_rule145, latex_rule146, latex_rule147, latex_rule148, latex_rule149, latex_rule150, latex_rule151, latex_rule152, latex_rule153, latex_rule154, latex_rule155, latex_rule156, latex_rule157, latex_rule158, latex_rule159, latex_rule160, latex_rule161, latex_rule162, latex_rule163, latex_rule164, latex_rule165, latex_rule166, latex_rule167, latex_rule168, latex_rule169, latex_rule170, latex_rule171, latex_rule172, latex_rule173, latex_rule174, latex_rule175, latex_rule176, latex_rule177, latex_rule178, latex_rule179, latex_rule180, latex_rule181, latex_rule182, latex_rule183, latex_rule184, latex_rule185, latex_rule186, latex_rule187, latex_rule188, latex_rule189, latex_rule190, latex_rule191, latex_rule192, latex_rule193, latex_rule194, latex_rule195, latex_rule196, latex_rule197, latex_rule198, latex_rule199, latex_rule200, latex_rule201, latex_rule202, latex_rule203, latex_rule204, latex_rule205, latex_rule206, latex_rule207, latex_rule208, latex_rule209, latex_rule210, latex_rule211, latex_rule212, latex_rule213, latex_rule214, latex_rule215, latex_rule216, latex_rule217, latex_rule218, latex_rule219, latex_rule220, latex_rule221, latex_rule222, latex_rule223, latex_rule224, latex_rule225, latex_rule226, latex_rule227, latex_rule228, latex_rule229, latex_rule230, latex_rule231, latex_rule232, latex_rule233, latex_rule234, latex_rule235, latex_rule236, latex_rule237, latex_rule238, latex_rule239, latex_rule240, latex_rule241, latex_rule242, latex_rule243, latex_rule244, latex_rule245, latex_rule246, latex_rule247, latex_rule248, latex_rule249, latex_rule250, latex_rule251, latex_rule252, latex_rule253, latex_rule254, latex_rule255, latex_rule256, latex_rule257, latex_rule258, latex_rule259, latex_rule260, latex_rule261, latex_rule262, latex_rule263, latex_rule264, latex_rule265, latex_rule266, latex_rule267, latex_rule268, latex_rule269, latex_rule270, latex_rule271, latex_rule272, latex_rule273, latex_rule274, latex_rule275, latex_rule276, latex_rule277, latex_rule278, latex_rule279, latex_rule280, latex_rule281, latex_rule282, latex_rule283, latex_rule284, latex_rule285, latex_rule286, latex_rule287, latex_rule288, latex_rule289, latex_rule290, latex_rule291, latex_rule292, latex_rule293, latex_rule294, latex_rule295, latex_rule296, latex_rule297, latex_rule298, latex_rule299, latex_rule300, latex_rule301, latex_rule302, latex_rule303, latex_rule304, latex_rule305, latex_rule306, latex_rule307, latex_rule308, latex_rule309, latex_rule310, latex_rule311, latex_rule312, latex_rule313, latex_rule314, latex_rule315, latex_rule316, latex_rule317, latex_rule318, latex_rule319, latex_rule320, latex_rule321, latex_rule322, latex_rule323, latex_rule324, latex_rule325, latex_rule326, latex_rule327, latex_rule328, latex_rule329, latex_rule330, latex_rule331, latex_rule332, latex_rule333, latex_rule334, latex_rule335, latex_rule336, latex_rule337, latex_rule338, latex_rule339, latex_rule340, latex_rule341, latex_rule342, latex_rule343, latex_rule344, latex_rule345, latex_rule346, latex_rule347, latex_rule348, latex_rule349, latex_rule350, latex_rule351, latex_rule352, latex_rule353, latex_rule354, latex_rule355, latex_rule356, latex_rule357, latex_rule358, latex_rule359, latex_rule360, latex_rule361, latex_rule362, latex_rule363, latex_rule364, latex_rule365, latex_rule366, latex_rule367, latex_rule368, latex_rule369, latex_rule370, latex_rule371, latex_rule372, latex_rule373, latex_rule374, latex_rule375, latex_rule376, latex_rule377, latex_rule378, latex_rule379, latex_rule380, latex_rule381, latex_rule382, latex_rule383, latex_rule384, latex_rule385, latex_rule386, latex_rule387, latex_rule388, latex_rule389, latex_rule390, latex_rule391, latex_rule392, latex_rule393, latex_rule394, latex_rule395, latex_rule396, latex_rule397, latex_rule398, latex_rule399, latex_rule400, latex_rule401, latex_rule402, latex_rule403, latex_rule404, latex_rule405, latex_rule406, latex_rule407, latex_rule408, latex_rule409, latex_rule410, latex_rule411, latex_rule412, latex_rule413, latex_rule414, latex_rule415, latex_rule416, latex_rule417, latex_rule418, latex_rule419, latex_rule420, latex_rule421, latex_rule422, latex_rule427,],
    "]": [latex_rule84,],
    "_": [latex_rule0, latex_rule61,],
    "`": [latex_rule2, latex_rule3, latex_rule6,],
    "d": [latex_rule83,],
    "s": [latex_rule82,],
    "t": [latex_rule79, latex_rule80, latex_rule81,],
    "{": [latex_rule78,],
    "}": [latex_rule77,],
    "~": [latex_rule76,],
}

# Rules for latex_mathmode ruleset.

def latex_rule428(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="__MathMode__")

def latex_rule429(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def latex_rule430(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="_")

def latex_rule431(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def latex_rule432(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\zeta")

def latex_rule433(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\xi")

def latex_rule434(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\wr")

def latex_rule435(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\wp")

def latex_rule436(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\widetilde{")

def latex_rule437(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\widehat{")

def latex_rule438(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\wedge")

def latex_rule439(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\veebar")

def latex_rule440(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vee")

def latex_rule441(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vec{")

def latex_rule442(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vdots")

def latex_rule443(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vdash")

def latex_rule444(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartriangleright")

def latex_rule445(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartriangleleft")

def latex_rule446(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartriangle")

def latex_rule447(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartheta")

def latex_rule448(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsupsetneqq")

def latex_rule449(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsupsetneq")

def latex_rule450(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsubsetneqq")

def latex_rule451(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsubsetneq")

def latex_rule452(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsigma")

def latex_rule453(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varrho")

def latex_rule454(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varpropto")

def latex_rule455(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varpi")

def latex_rule456(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varphi")

def latex_rule457(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varnothing")

def latex_rule458(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varkappa")

def latex_rule459(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varepsilon")

def latex_rule460(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vDash")

def latex_rule461(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\urcorner")

def latex_rule462(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upuparrows")

def latex_rule463(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upsilon")

def latex_rule464(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\uplus")

def latex_rule465(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upharpoonright")

def latex_rule466(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upharpoonleft")

def latex_rule467(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\updownarrow")

def latex_rule468(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\uparrow")

def latex_rule469(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ulcorner")

def latex_rule470(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\twoheadrightarrow")

def latex_rule471(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\twoheadleftarrow")

def latex_rule472(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\trianglerighteq")

def latex_rule473(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangleright")

def latex_rule474(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangleq")

def latex_rule475(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\trianglelefteq")

def latex_rule476(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangleleft")

def latex_rule477(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangledown")

def latex_rule478(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangle")

def latex_rule479(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\top")

def latex_rule480(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\times")

def latex_rule481(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\tilde{")

def latex_rule482(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thicksim")

def latex_rule483(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thickapprox")

def latex_rule484(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\theta")

def latex_rule485(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\therefore")

def latex_rule486(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\text{")

def latex_rule487(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\textstyle")

def latex_rule488(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tau")

def latex_rule489(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tanh")

def latex_rule490(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tan")

def latex_rule491(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\swarrow")

def latex_rule492(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\surd")

def latex_rule493(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supsetneqq")

def latex_rule494(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supsetneq")

def latex_rule495(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supseteqq")

def latex_rule496(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supseteq")

def latex_rule497(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supset")

def latex_rule498(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sum")

def latex_rule499(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succsim")

def latex_rule500(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succnsim")

def latex_rule501(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succnapprox")

def latex_rule502(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succeq")

def latex_rule503(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succcurlyeq")

def latex_rule504(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succapprox")

def latex_rule505(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succ")

def latex_rule506(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subsetneqq")

def latex_rule507(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subsetneq")

def latex_rule508(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subseteqq")

def latex_rule509(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subseteq")

def latex_rule510(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subset")

def latex_rule511(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\star")

def latex_rule512(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stackrel{")

def latex_rule513(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\square")

def latex_rule514(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsupseteq")

def latex_rule515(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsupset")

def latex_rule516(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsubseteq")

def latex_rule517(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsubset")

def latex_rule518(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\sqrt{")

def latex_rule519(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqcup")

def latex_rule520(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqcap")

def latex_rule521(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sphericalangle")

def latex_rule522(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\spadesuit")

def latex_rule523(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smile")

def latex_rule524(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallsmile")

def latex_rule525(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallsetminus")

def latex_rule526(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallfrown")

def latex_rule527(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sinh")

def latex_rule528(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sin")

def latex_rule529(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\simeq")

def latex_rule530(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sim")

def latex_rule531(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sigma")

def latex_rule532(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\shortparallel")

def latex_rule533(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\shortmid")

def latex_rule534(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sharp")

def latex_rule535(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\setminus")

def latex_rule536(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sec")

def latex_rule537(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\searrow")

def latex_rule538(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scriptstyle")

def latex_rule539(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scriptscriptstyle")

def latex_rule540(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rtimes")

def latex_rule541(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\risingdotseq")

def latex_rule542(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right|")

def latex_rule543(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightthreetimes")

def latex_rule544(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightsquigarrow")

def latex_rule545(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightrightarrows")

def latex_rule546(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightrightarrows")

def latex_rule547(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightleftharpoons")

def latex_rule548(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightleftharpoons")

def latex_rule549(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightleftarrows")

def latex_rule550(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightharpoonup")

def latex_rule551(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightharpoondown")

def latex_rule552(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightarrowtail")

def latex_rule553(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightarrow")

def latex_rule554(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right]")

def latex_rule555(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\|")

def latex_rule556(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\updownarrow")

def latex_rule557(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\uparrow")

def latex_rule558(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\rfloor")

def latex_rule559(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\rceil")

def latex_rule560(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\rangle")

def latex_rule561(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\lfloor")

def latex_rule562(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\lceil")

def latex_rule563(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\langle")

def latex_rule564(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\downarrow")

def latex_rule565(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\backslash")

def latex_rule566(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\Updownarrow")

def latex_rule567(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\Uparrow")

def latex_rule568(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\Downarrow")

def latex_rule569(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\)")

def latex_rule570(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\(")

def latex_rule571(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\right[")

def latex_rule572(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right/")

def latex_rule573(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right)")

def latex_rule574(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right(")

def latex_rule575(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rho")

def latex_rule576(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\psi")

def latex_rule577(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\propto")

def latex_rule578(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\prod")

def latex_rule579(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\prime")

def latex_rule580(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precsim")

def latex_rule581(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precnsim")

def latex_rule582(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precnapprox")

def latex_rule583(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\preceq")

def latex_rule584(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\preccurlyeq")

def latex_rule585(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precapprox")

def latex_rule586(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\prec")

def latex_rule587(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pmod{")

def latex_rule588(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pmb{")

def latex_rule589(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pm")

def latex_rule590(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pitchfork")

def latex_rule591(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pi")

def latex_rule592(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\phi")

def latex_rule593(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\perp")

def latex_rule594(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\partial")

def latex_rule595(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\parallel")

def latex_rule596(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\overline{")

def latex_rule597(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\otimes")

def latex_rule598(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\oslash")

def latex_rule599(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\oplus")

def latex_rule600(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ominus")

def latex_rule601(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\omega")

def latex_rule602(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\oint")

def latex_rule603(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\odot")

def latex_rule604(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nwarrow")

def latex_rule605(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nvdash")

def latex_rule606(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nvDash")

def latex_rule607(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nvDash")

def latex_rule608(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nu")

def latex_rule609(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntrianglerighteq")

def latex_rule610(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntriangleright")

def latex_rule611(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntrianglelefteq")

def latex_rule612(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntriangleleft")

def latex_rule613(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsupseteqq")

def latex_rule614(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsupseteq")

def latex_rule615(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsucceq")

def latex_rule616(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsucc")

def latex_rule617(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsubseteq")

def latex_rule618(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsim")

def latex_rule619(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nshortparallel")

def latex_rule620(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nshortmid")

def latex_rule621(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nrightarrow")

def latex_rule622(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\npreceq")

def latex_rule623(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nprec")

def latex_rule624(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nparallel")

def latex_rule625(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\notin")

def latex_rule626(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nmid")

def latex_rule627(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nless")

def latex_rule628(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleqslant")

def latex_rule629(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleqq")

def latex_rule630(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleq")

def latex_rule631(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleftrightarrow")

def latex_rule632(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleftarrow")

def latex_rule633(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ni")

def latex_rule634(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngtr")

def latex_rule635(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngeqslant")

def latex_rule636(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngeqq")

def latex_rule637(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngeq")

def latex_rule638(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nexists")

def latex_rule639(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\neq")

def latex_rule640(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\neg")

def latex_rule641(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nearrow")

def latex_rule642(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ncong")

def latex_rule643(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\natural")

def latex_rule644(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nabla")

def latex_rule645(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nVDash")

def latex_rule646(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nRightarrow")

def latex_rule647(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nLeftrightarrow")

def latex_rule648(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nLeftarrow")

def latex_rule649(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\multimap")

def latex_rule650(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mu")

def latex_rule651(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mp")

def latex_rule652(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\models")

def latex_rule653(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\min")

def latex_rule654(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mid")

def latex_rule655(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mho")

def latex_rule656(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\measuredangle")

def latex_rule657(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\max")

def latex_rule658(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathtt{")

def latex_rule659(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathsf{")

def latex_rule660(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mathrm{~~")

def latex_rule661(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathit{")

def latex_rule662(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathcal{")

def latex_rule663(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathbf{")

def latex_rule664(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mapsto")

def latex_rule665(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lvertneqq")

def latex_rule666(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ltimes")

def latex_rule667(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lrcorner")

def latex_rule668(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lozenge")

def latex_rule669(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\looparrowright")

def latex_rule670(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\looparrowleft")

def latex_rule671(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longrightarrow")

def latex_rule672(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longmapsto")

def latex_rule673(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longleftrightarrow")

def latex_rule674(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longleftarrow")

def latex_rule675(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\log")

def latex_rule676(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lnsim")

def latex_rule677(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lneqq")

def latex_rule678(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lneq")

def latex_rule679(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lnapprox")

def latex_rule680(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ln")

def latex_rule681(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lll")

def latex_rule682(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\llcorner")

def latex_rule683(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ll")

def latex_rule684(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\limsup")

def latex_rule685(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\liminf")

def latex_rule686(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lim")

def latex_rule687(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lg")

def latex_rule688(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lesssim")

def latex_rule689(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lessgtr")

def latex_rule690(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lesseqqgtr")

def latex_rule691(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lesseqgtr")

def latex_rule692(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lessdot")

def latex_rule693(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lessapprox")

def latex_rule694(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leqslant")

def latex_rule695(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leqq")

def latex_rule696(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leq")

def latex_rule697(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left|")

def latex_rule698(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftthreetimes")

def latex_rule699(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightsquigarrow")

def latex_rule700(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightharpoons")

def latex_rule701(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightarrows")

def latex_rule702(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightarrow")

def latex_rule703(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftleftarrows")

def latex_rule704(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftharpoonup")

def latex_rule705(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftharpoondown")

def latex_rule706(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\lefteqn{")

def latex_rule707(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftarrowtail")

def latex_rule708(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftarrow")

def latex_rule709(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left]")

def latex_rule710(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\|")

def latex_rule711(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\updownarrow")

def latex_rule712(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\uparrow")

def latex_rule713(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\rfloor")

def latex_rule714(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\rceil")

def latex_rule715(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\rangle")

def latex_rule716(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\lfloor")

def latex_rule717(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\lceil")

def latex_rule718(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\langle")

def latex_rule719(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\downarrow")

def latex_rule720(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\backslash")

def latex_rule721(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\Updownarrow")

def latex_rule722(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\Uparrow")

def latex_rule723(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\Downarrow")

def latex_rule724(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\)")

def latex_rule725(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\(")

def latex_rule726(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\left[")

def latex_rule727(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left/")

def latex_rule728(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left)")

def latex_rule729(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left(")

def latex_rule730(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ldots")

def latex_rule731(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lambda")

def latex_rule732(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ker")

def latex_rule733(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\kappa")

def latex_rule734(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\jmath")

def latex_rule735(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\jmath")

def latex_rule736(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\iota")

def latex_rule737(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\intercal")

def latex_rule738(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\int")

def latex_rule739(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\infty")

def latex_rule740(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\inf")

def latex_rule741(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\in")

def latex_rule742(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\imath")

def latex_rule743(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\imath")

def latex_rule744(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hslash")

def latex_rule745(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hookrightarrow")

def latex_rule746(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hookleftarrow")

def latex_rule747(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hom")

def latex_rule748(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\heartsuit")

def latex_rule749(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hbar")

def latex_rule750(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hat{")

def latex_rule751(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gvertneqq")

def latex_rule752(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrsim")

def latex_rule753(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrless")

def latex_rule754(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtreqqless")

def latex_rule755(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtreqless")

def latex_rule756(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrdot")

def latex_rule757(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrapprox")

def latex_rule758(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\grave{")

def latex_rule759(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gnsim")

def latex_rule760(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gneqq")

def latex_rule761(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gneq")

def latex_rule762(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gnapprox")

def latex_rule763(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gnapprox")

def latex_rule764(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gimel")

def latex_rule765(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ggg")

def latex_rule766(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gg")

def latex_rule767(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\geqslant")

def latex_rule768(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\geqq")

def latex_rule769(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\geq")

def latex_rule770(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gcd")

def latex_rule771(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gamma")

def latex_rule772(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\frown")

def latex_rule773(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\frak{")

def latex_rule774(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\frac{")

def latex_rule775(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\forall")

def latex_rule776(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\flat")

def latex_rule777(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fallingdotseq")

def latex_rule778(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\exp")

def latex_rule779(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\exists")

def latex_rule780(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eth")

def latex_rule781(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eta")

def latex_rule782(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\equiv")

def latex_rule783(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eqslantless")

def latex_rule784(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eqslantgtr")

def latex_rule785(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eqcirc")

def latex_rule786(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\epsilon")

def latex_rule787(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ensuremath{")

def latex_rule788(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\end{")

def latex_rule789(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\emptyset")

def latex_rule790(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ell")

def latex_rule791(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downharpoonright")

def latex_rule792(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downharpoonleft")

def latex_rule793(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downdownarrows")

def latex_rule794(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downarrow")

def latex_rule795(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\doublebarwedge")

def latex_rule796(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\dot{")

def latex_rule797(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dotplus")

def latex_rule798(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\doteqdot")

def latex_rule799(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\doteq")

def latex_rule800(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\divideontimes")

def latex_rule801(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\div")

def latex_rule802(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\displaystyle")

def latex_rule803(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dim")

def latex_rule804(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\digamma")

def latex_rule805(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diamondsuit")

def latex_rule806(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diamond")

def latex_rule807(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diagup")

def latex_rule808(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diagdown")

def latex_rule809(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\det")

def latex_rule810(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\delta")

def latex_rule811(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\deg")

def latex_rule812(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ddot{")

def latex_rule813(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ddots")

def latex_rule814(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ddagger")

def latex_rule815(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dashv")

def latex_rule816(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dashrightarrow")

def latex_rule817(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dashleftarrow")

def latex_rule818(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\daleth")

def latex_rule819(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dagger")

def latex_rule820(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curvearrowright")

def latex_rule821(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curvearrowleft")

def latex_rule822(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlywedge")

def latex_rule823(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlyvee")

def latex_rule824(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlyeqsucc")

def latex_rule825(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlyeqprec")

def latex_rule826(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cup")

def latex_rule827(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\csc")

def latex_rule828(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\coth")

def latex_rule829(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cot")

def latex_rule830(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cosh")

def latex_rule831(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cos")

def latex_rule832(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\coprod")

def latex_rule833(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cong")

def latex_rule834(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\complement")

def latex_rule835(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\clubsuit")

def latex_rule836(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circleddash")

def latex_rule837(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circledcirc")

def latex_rule838(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circledast")

def latex_rule839(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circledS")

def latex_rule840(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circlearrowright")

def latex_rule841(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circlearrowleft")

def latex_rule842(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circeq")

def latex_rule843(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circ")

def latex_rule844(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\chi")

def latex_rule845(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\check{")

def latex_rule846(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\centerdot")

def latex_rule847(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cdots")

def latex_rule848(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cdot")

def latex_rule849(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cap")

def latex_rule850(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bumpeq")

def latex_rule851(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bullet")

def latex_rule852(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\breve{")

def latex_rule853(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxtimes")

def latex_rule854(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxplus")

def latex_rule855(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxminus")

def latex_rule856(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxdot")

def latex_rule857(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bowtie")

def latex_rule858(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bot")

def latex_rule859(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boldsymbol{")

def latex_rule860(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bmod")

def latex_rule861(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangleright")

def latex_rule862(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangleleft")

def latex_rule863(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangledown")

def latex_rule864(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangle")

def latex_rule865(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacksquare")

def latex_rule866(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacklozenge")

def latex_rule867(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigwedge")

def latex_rule868(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigvee")

def latex_rule869(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\biguplus")

def latex_rule870(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigtriangleup")

def latex_rule871(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigtriangledown")

def latex_rule872(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigstar")

def latex_rule873(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigsqcup")

def latex_rule874(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigotimes")

def latex_rule875(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigoplus")

def latex_rule876(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigodot")

def latex_rule877(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigcup")

def latex_rule878(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigcirc")

def latex_rule879(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigcap")

def latex_rule880(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\between")

def latex_rule881(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\beth")

def latex_rule882(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\beta")

def latex_rule883(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\begin{")

def latex_rule884(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\because")

def latex_rule885(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bar{")

def latex_rule886(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\barwedge")

def latex_rule887(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backslash")

def latex_rule888(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backsimeq")

def latex_rule889(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backsim")

def latex_rule890(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backprime")

def latex_rule891(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\asymp")

def latex_rule892(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ast")

def latex_rule893(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arg")

def latex_rule894(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arctan")

def latex_rule895(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arcsin")

def latex_rule896(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arccos")

def latex_rule897(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\approxeq")

def latex_rule898(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\approx")

def latex_rule899(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\angle")

def latex_rule900(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\angle")

def latex_rule901(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\amalg")

def latex_rule902(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\alpha")

def latex_rule903(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\aleph")

def latex_rule904(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\acute{")

def latex_rule905(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Xi")

def latex_rule906(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Vvdash")

def latex_rule907(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Vdash")

def latex_rule908(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Upsilon")

def latex_rule909(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Updownarrow")

def latex_rule910(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Uparrow")

def latex_rule911(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Theta")

def latex_rule912(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Supset")

def latex_rule913(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Subset")

def latex_rule914(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Sigma")

def latex_rule915(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Rsh")

def latex_rule916(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Rightarrow")

def latex_rule917(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Re")

def latex_rule918(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Psi")

def latex_rule919(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Pr")

def latex_rule920(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Pi")

def latex_rule921(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Phi")

def latex_rule922(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Omega")

def latex_rule923(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Lsh")

def latex_rule924(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Longrightarrow")

def latex_rule925(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Longleftrightarrow")

def latex_rule926(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Longleftarrow")

def latex_rule927(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Lleftarrow")

def latex_rule928(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Leftrightarrow")

def latex_rule929(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Leftarrow")

def latex_rule930(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Lambda")

def latex_rule931(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Im")

def latex_rule932(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Gamma")

def latex_rule933(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Game")

def latex_rule934(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Finv")

def latex_rule935(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Downarrow")

def latex_rule936(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Delta")

def latex_rule937(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Cup")

def latex_rule938(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Cap")

def latex_rule939(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Bumpeq")

def latex_rule940(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Bbb{")

def latex_rule941(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Bbbk")

def latex_rule942(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\;")

def latex_rule943(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\:")

def latex_rule944(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\,")

def latex_rule945(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\!")

def latex_rule946(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="'")

def latex_rule947(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\\begin{array}", end="\\end{array}",
          delegate="latex::arraymode")

def latex_rule948(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="\\")

# Rules dict for latex_mathmode ruleset.
rulesDict2 = {
    "%": [latex_rule429,],
    "'": [latex_rule946,],
    "\\": [latex_rule432, latex_rule433, latex_rule434, latex_rule435, latex_rule436, latex_rule437, latex_rule438, latex_rule439, latex_rule440, latex_rule441, latex_rule442, latex_rule443, latex_rule444, latex_rule445, latex_rule446, latex_rule447, latex_rule448, latex_rule449, latex_rule450, latex_rule451, latex_rule452, latex_rule453, latex_rule454, latex_rule455, latex_rule456, latex_rule457, latex_rule458, latex_rule459, latex_rule460, latex_rule461, latex_rule462, latex_rule463, latex_rule464, latex_rule465, latex_rule466, latex_rule467, latex_rule468, latex_rule469, latex_rule470, latex_rule471, latex_rule472, latex_rule473, latex_rule474, latex_rule475, latex_rule476, latex_rule477, latex_rule478, latex_rule479, latex_rule480, latex_rule481, latex_rule482, latex_rule483, latex_rule484, latex_rule485, latex_rule486, latex_rule487, latex_rule488, latex_rule489, latex_rule490, latex_rule491, latex_rule492, latex_rule493, latex_rule494, latex_rule495, latex_rule496, latex_rule497, latex_rule498, latex_rule499, latex_rule500, latex_rule501, latex_rule502, latex_rule503, latex_rule504, latex_rule505, latex_rule506, latex_rule507, latex_rule508, latex_rule509, latex_rule510, latex_rule511, latex_rule512, latex_rule513, latex_rule514, latex_rule515, latex_rule516, latex_rule517, latex_rule518, latex_rule519, latex_rule520, latex_rule521, latex_rule522, latex_rule523, latex_rule524, latex_rule525, latex_rule526, latex_rule527, latex_rule528, latex_rule529, latex_rule530, latex_rule531, latex_rule532, latex_rule533, latex_rule534, latex_rule535, latex_rule536, latex_rule537, latex_rule538, latex_rule539, latex_rule540, latex_rule541, latex_rule542, latex_rule543, latex_rule544, latex_rule545, latex_rule546, latex_rule547, latex_rule548, latex_rule549, latex_rule550, latex_rule551, latex_rule552, latex_rule553, latex_rule554, latex_rule555, latex_rule556, latex_rule557, latex_rule558, latex_rule559, latex_rule560, latex_rule561, latex_rule562, latex_rule563, latex_rule564, latex_rule565, latex_rule566, latex_rule567, latex_rule568, latex_rule569, latex_rule570, latex_rule571, latex_rule572, latex_rule573, latex_rule574, latex_rule575, latex_rule576, latex_rule577, latex_rule578, latex_rule579, latex_rule580, latex_rule581, latex_rule582, latex_rule583, latex_rule584, latex_rule585, latex_rule586, latex_rule587, latex_rule588, latex_rule589, latex_rule590, latex_rule591, latex_rule592, latex_rule593, latex_rule594, latex_rule595, latex_rule596, latex_rule597, latex_rule598, latex_rule599, latex_rule600, latex_rule601, latex_rule602, latex_rule603, latex_rule604, latex_rule605, latex_rule606, latex_rule607, latex_rule608, latex_rule609, latex_rule610, latex_rule611, latex_rule612, latex_rule613, latex_rule614, latex_rule615, latex_rule616, latex_rule617, latex_rule618, latex_rule619, latex_rule620, latex_rule621, latex_rule622, latex_rule623, latex_rule624, latex_rule625, latex_rule626, latex_rule627, latex_rule628, latex_rule629, latex_rule630, latex_rule631, latex_rule632, latex_rule633, latex_rule634, latex_rule635, latex_rule636, latex_rule637, latex_rule638, latex_rule639, latex_rule640, latex_rule641, latex_rule642, latex_rule643, latex_rule644, latex_rule645, latex_rule646, latex_rule647, latex_rule648, latex_rule649, latex_rule650, latex_rule651, latex_rule652, latex_rule653, latex_rule654, latex_rule655, latex_rule656, latex_rule657, latex_rule658, latex_rule659, latex_rule660, latex_rule661, latex_rule662, latex_rule663, latex_rule664, latex_rule665, latex_rule666, latex_rule667, latex_rule668, latex_rule669, latex_rule670, latex_rule671, latex_rule672, latex_rule673, latex_rule674, latex_rule675, latex_rule676, latex_rule677, latex_rule678, latex_rule679, latex_rule680, latex_rule681, latex_rule682, latex_rule683, latex_rule684, latex_rule685, latex_rule686, latex_rule687, latex_rule688, latex_rule689, latex_rule690, latex_rule691, latex_rule692, latex_rule693, latex_rule694, latex_rule695, latex_rule696, latex_rule697, latex_rule698, latex_rule699, latex_rule700, latex_rule701, latex_rule702, latex_rule703, latex_rule704, latex_rule705, latex_rule706, latex_rule707, latex_rule708, latex_rule709, latex_rule710, latex_rule711, latex_rule712, latex_rule713, latex_rule714, latex_rule715, latex_rule716, latex_rule717, latex_rule718, latex_rule719, latex_rule720, latex_rule721, latex_rule722, latex_rule723, latex_rule724, latex_rule725, latex_rule726, latex_rule727, latex_rule728, latex_rule729, latex_rule730, latex_rule731, latex_rule732, latex_rule733, latex_rule734, latex_rule735, latex_rule736, latex_rule737, latex_rule738, latex_rule739, latex_rule740, latex_rule741, latex_rule742, latex_rule743, latex_rule744, latex_rule745, latex_rule746, latex_rule747, latex_rule748, latex_rule749, latex_rule750, latex_rule751, latex_rule752, latex_rule753, latex_rule754, latex_rule755, latex_rule756, latex_rule757, latex_rule758, latex_rule759, latex_rule760, latex_rule761, latex_rule762, latex_rule763, latex_rule764, latex_rule765, latex_rule766, latex_rule767, latex_rule768, latex_rule769, latex_rule770, latex_rule771, latex_rule772, latex_rule773, latex_rule774, latex_rule775, latex_rule776, latex_rule777, latex_rule778, latex_rule779, latex_rule780, latex_rule781, latex_rule782, latex_rule783, latex_rule784, latex_rule785, latex_rule786, latex_rule787, latex_rule788, latex_rule789, latex_rule790, latex_rule791, latex_rule792, latex_rule793, latex_rule794, latex_rule795, latex_rule796, latex_rule797, latex_rule798, latex_rule799, latex_rule800, latex_rule801, latex_rule802, latex_rule803, latex_rule804, latex_rule805, latex_rule806, latex_rule807, latex_rule808, latex_rule809, latex_rule810, latex_rule811, latex_rule812, latex_rule813, latex_rule814, latex_rule815, latex_rule816, latex_rule817, latex_rule818, latex_rule819, latex_rule820, latex_rule821, latex_rule822, latex_rule823, latex_rule824, latex_rule825, latex_rule826, latex_rule827, latex_rule828, latex_rule829, latex_rule830, latex_rule831, latex_rule832, latex_rule833, latex_rule834, latex_rule835, latex_rule836, latex_rule837, latex_rule838, latex_rule839, latex_rule840, latex_rule841, latex_rule842, latex_rule843, latex_rule844, latex_rule845, latex_rule846, latex_rule847, latex_rule848, latex_rule849, latex_rule850, latex_rule851, latex_rule852, latex_rule853, latex_rule854, latex_rule855, latex_rule856, latex_rule857, latex_rule858, latex_rule859, latex_rule860, latex_rule861, latex_rule862, latex_rule863, latex_rule864, latex_rule865, latex_rule866, latex_rule867, latex_rule868, latex_rule869, latex_rule870, latex_rule871, latex_rule872, latex_rule873, latex_rule874, latex_rule875, latex_rule876, latex_rule877, latex_rule878, latex_rule879, latex_rule880, latex_rule881, latex_rule882, latex_rule883, latex_rule884, latex_rule885, latex_rule886, latex_rule887, latex_rule888, latex_rule889, latex_rule890, latex_rule891, latex_rule892, latex_rule893, latex_rule894, latex_rule895, latex_rule896, latex_rule897, latex_rule898, latex_rule899, latex_rule900, latex_rule901, latex_rule902, latex_rule903, latex_rule904, latex_rule905, latex_rule906, latex_rule907, latex_rule908, latex_rule909, latex_rule910, latex_rule911, latex_rule912, latex_rule913, latex_rule914, latex_rule915, latex_rule916, latex_rule917, latex_rule918, latex_rule919, latex_rule920, latex_rule921, latex_rule922, latex_rule923, latex_rule924, latex_rule925, latex_rule926, latex_rule927, latex_rule928, latex_rule929, latex_rule930, latex_rule931, latex_rule932, latex_rule933, latex_rule934, latex_rule935, latex_rule936, latex_rule937, latex_rule938, latex_rule939, latex_rule940, latex_rule941, latex_rule942, latex_rule943, latex_rule944, latex_rule945, latex_rule947, latex_rule948,],
    "^": [latex_rule431,],
    "_": [latex_rule428, latex_rule430,],
}

# Rules for latex_arraymode ruleset.

def latex_rule949(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="__ArrayMode__")

def latex_rule950(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def latex_rule951(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="_")

def latex_rule952(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def latex_rule953(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\zeta")

def latex_rule954(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\xi")

def latex_rule955(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\wr")

def latex_rule956(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\wp")

def latex_rule957(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\widetilde{")

def latex_rule958(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\widehat{")

def latex_rule959(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\wedge")

def latex_rule960(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vline")

def latex_rule961(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\veebar")

def latex_rule962(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vee")

def latex_rule963(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vec{")

def latex_rule964(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vdots")

def latex_rule965(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vdash")

def latex_rule966(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartriangleright")

def latex_rule967(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartriangleleft")

def latex_rule968(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartriangle")

def latex_rule969(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vartheta")

def latex_rule970(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsupsetneqq")

def latex_rule971(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsupsetneq")

def latex_rule972(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsubsetneqq")

def latex_rule973(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsubsetneq")

def latex_rule974(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varsigma")

def latex_rule975(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varrho")

def latex_rule976(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varpropto")

def latex_rule977(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varpi")

def latex_rule978(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varphi")

def latex_rule979(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varnothing")

def latex_rule980(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varkappa")

def latex_rule981(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\varepsilon")

def latex_rule982(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vDash")

def latex_rule983(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\urcorner")

def latex_rule984(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upuparrows")

def latex_rule985(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upsilon")

def latex_rule986(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\uplus")

def latex_rule987(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upharpoonright")

def latex_rule988(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upharpoonleft")

def latex_rule989(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\updownarrow")

def latex_rule990(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\uparrow")

def latex_rule991(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ulcorner")

def latex_rule992(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\twoheadrightarrow")

def latex_rule993(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\twoheadleftarrow")

def latex_rule994(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\trianglerighteq")

def latex_rule995(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangleright")

def latex_rule996(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangleq")

def latex_rule997(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\trianglelefteq")

def latex_rule998(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangleleft")

def latex_rule999(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangledown")

def latex_rule1000(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\triangle")

def latex_rule1001(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\top")

def latex_rule1002(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\times")

def latex_rule1003(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\tilde{")

def latex_rule1004(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thicksim")

def latex_rule1005(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thickapprox")

def latex_rule1006(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\theta")

def latex_rule1007(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\therefore")

def latex_rule1008(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\text{")

def latex_rule1009(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\textstyle")

def latex_rule1010(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tau")

def latex_rule1011(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tanh")

def latex_rule1012(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tan")

def latex_rule1013(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\swarrow")

def latex_rule1014(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\surd")

def latex_rule1015(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supsetneqq")

def latex_rule1016(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supsetneq")

def latex_rule1017(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supseteqq")

def latex_rule1018(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supseteq")

def latex_rule1019(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\supset")

def latex_rule1020(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sum")

def latex_rule1021(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succsim")

def latex_rule1022(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succnsim")

def latex_rule1023(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succnapprox")

def latex_rule1024(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succeq")

def latex_rule1025(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succcurlyeq")

def latex_rule1026(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succapprox")

def latex_rule1027(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\succ")

def latex_rule1028(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subsetneqq")

def latex_rule1029(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subsetneq")

def latex_rule1030(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subseteqq")

def latex_rule1031(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subseteq")

def latex_rule1032(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\subset")

def latex_rule1033(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\star")

def latex_rule1034(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stackrel{")

def latex_rule1035(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\square")

def latex_rule1036(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsupseteq")

def latex_rule1037(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsupset")

def latex_rule1038(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsubseteq")

def latex_rule1039(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqsubset")

def latex_rule1040(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\sqrt{")

def latex_rule1041(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqcup")

def latex_rule1042(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sqcap")

def latex_rule1043(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sphericalangle")

def latex_rule1044(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\spadesuit")

def latex_rule1045(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smile")

def latex_rule1046(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallsmile")

def latex_rule1047(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallsetminus")

def latex_rule1048(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallfrown")

def latex_rule1049(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sinh")

def latex_rule1050(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sin")

def latex_rule1051(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\simeq")

def latex_rule1052(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sim")

def latex_rule1053(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sigma")

def latex_rule1054(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\shortparallel")

def latex_rule1055(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\shortmid")

def latex_rule1056(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sharp")

def latex_rule1057(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\setminus")

def latex_rule1058(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sec")

def latex_rule1059(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\searrow")

def latex_rule1060(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scriptstyle")

def latex_rule1061(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scriptscriptstyle")

def latex_rule1062(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rtimes")

def latex_rule1063(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\risingdotseq")

def latex_rule1064(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right|")

def latex_rule1065(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightthreetimes")

def latex_rule1066(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightsquigarrow")

def latex_rule1067(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightrightarrows")

def latex_rule1068(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightrightarrows")

def latex_rule1069(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightleftharpoons")

def latex_rule1070(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightleftharpoons")

def latex_rule1071(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightleftarrows")

def latex_rule1072(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightharpoonup")

def latex_rule1073(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightharpoondown")

def latex_rule1074(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightarrowtail")

def latex_rule1075(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rightarrow")

def latex_rule1076(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right]")

def latex_rule1077(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\|")

def latex_rule1078(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\updownarrow")

def latex_rule1079(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\uparrow")

def latex_rule1080(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\rfloor")

def latex_rule1081(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\rceil")

def latex_rule1082(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\rangle")

def latex_rule1083(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\lfloor")

def latex_rule1084(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\lceil")

def latex_rule1085(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\langle")

def latex_rule1086(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\downarrow")

def latex_rule1087(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\backslash")

def latex_rule1088(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\Updownarrow")

def latex_rule1089(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\Uparrow")

def latex_rule1090(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\Downarrow")

def latex_rule1091(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\)")

def latex_rule1092(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right\\(")

def latex_rule1093(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\right[")

def latex_rule1094(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right/")

def latex_rule1095(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right)")

def latex_rule1096(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\right(")

def latex_rule1097(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rho")

def latex_rule1098(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\psi")

def latex_rule1099(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\propto")

def latex_rule1100(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\prod")

def latex_rule1101(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\prime")

def latex_rule1102(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precsim")

def latex_rule1103(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precnsim")

def latex_rule1104(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precnapprox")

def latex_rule1105(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\preceq")

def latex_rule1106(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\preccurlyeq")

def latex_rule1107(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\precapprox")

def latex_rule1108(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\prec")

def latex_rule1109(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pmod{")

def latex_rule1110(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pmb{")

def latex_rule1111(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pm")

def latex_rule1112(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pitchfork")

def latex_rule1113(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pi")

def latex_rule1114(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\phi")

def latex_rule1115(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\perp")

def latex_rule1116(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\partial")

def latex_rule1117(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\parallel")

def latex_rule1118(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\overline{")

def latex_rule1119(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\otimes")

def latex_rule1120(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\oslash")

def latex_rule1121(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\oplus")

def latex_rule1122(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ominus")

def latex_rule1123(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\omega")

def latex_rule1124(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\oint")

def latex_rule1125(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\odot")

def latex_rule1126(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nwarrow")

def latex_rule1127(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nvdash")

def latex_rule1128(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nvDash")

def latex_rule1129(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nvDash")

def latex_rule1130(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nu")

def latex_rule1131(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntrianglerighteq")

def latex_rule1132(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntriangleright")

def latex_rule1133(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntrianglelefteq")

def latex_rule1134(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ntriangleleft")

def latex_rule1135(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsupseteqq")

def latex_rule1136(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsupseteq")

def latex_rule1137(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsucceq")

def latex_rule1138(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsucc")

def latex_rule1139(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsubseteq")

def latex_rule1140(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nsim")

def latex_rule1141(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nshortparallel")

def latex_rule1142(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nshortmid")

def latex_rule1143(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nrightarrow")

def latex_rule1144(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\npreceq")

def latex_rule1145(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nprec")

def latex_rule1146(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nparallel")

def latex_rule1147(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\notin")

def latex_rule1148(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nmid")

def latex_rule1149(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nless")

def latex_rule1150(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleqslant")

def latex_rule1151(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleqq")

def latex_rule1152(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleq")

def latex_rule1153(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleftrightarrow")

def latex_rule1154(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nleftarrow")

def latex_rule1155(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ni")

def latex_rule1156(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngtr")

def latex_rule1157(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngeqslant")

def latex_rule1158(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngeqq")

def latex_rule1159(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ngeq")

def latex_rule1160(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nexists")

def latex_rule1161(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\neq")

def latex_rule1162(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\neg")

def latex_rule1163(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nearrow")

def latex_rule1164(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ncong")

def latex_rule1165(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\natural")

def latex_rule1166(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nabla")

def latex_rule1167(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nVDash")

def latex_rule1168(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nRightarrow")

def latex_rule1169(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nLeftrightarrow")

def latex_rule1170(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nLeftarrow")

def latex_rule1171(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\multimap")

def latex_rule1172(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\multicolumn{")

def latex_rule1173(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mu")

def latex_rule1174(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mp")

def latex_rule1175(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\models")

def latex_rule1176(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\min")

def latex_rule1177(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mid")

def latex_rule1178(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mho")

def latex_rule1179(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\measuredangle")

def latex_rule1180(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\max")

def latex_rule1181(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathtt{")

def latex_rule1182(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathsf{")

def latex_rule1183(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mathrm{~~")

def latex_rule1184(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathit{")

def latex_rule1185(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathcal{")

def latex_rule1186(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mathbf{")

def latex_rule1187(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mapsto")

def latex_rule1188(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lvertneqq")

def latex_rule1189(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ltimes")

def latex_rule1190(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lrcorner")

def latex_rule1191(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lozenge")

def latex_rule1192(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\looparrowright")

def latex_rule1193(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\looparrowleft")

def latex_rule1194(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longrightarrow")

def latex_rule1195(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longmapsto")

def latex_rule1196(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longleftrightarrow")

def latex_rule1197(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\longleftarrow")

def latex_rule1198(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\log")

def latex_rule1199(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lnsim")

def latex_rule1200(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lneqq")

def latex_rule1201(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lneq")

def latex_rule1202(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lnapprox")

def latex_rule1203(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ln")

def latex_rule1204(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lll")

def latex_rule1205(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\llcorner")

def latex_rule1206(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ll")

def latex_rule1207(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\limsup")

def latex_rule1208(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\liminf")

def latex_rule1209(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lim")

def latex_rule1210(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lg")

def latex_rule1211(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lesssim")

def latex_rule1212(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lessgtr")

def latex_rule1213(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lesseqqgtr")

def latex_rule1214(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lesseqgtr")

def latex_rule1215(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lessdot")

def latex_rule1216(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lessapprox")

def latex_rule1217(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leqslant")

def latex_rule1218(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leqq")

def latex_rule1219(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leq")

def latex_rule1220(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left|")

def latex_rule1221(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftthreetimes")

def latex_rule1222(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightsquigarrow")

def latex_rule1223(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightharpoons")

def latex_rule1224(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightarrows")

def latex_rule1225(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftrightarrow")

def latex_rule1226(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftleftarrows")

def latex_rule1227(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftharpoonup")

def latex_rule1228(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftharpoondown")

def latex_rule1229(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\lefteqn{")

def latex_rule1230(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftarrowtail")

def latex_rule1231(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\leftarrow")

def latex_rule1232(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left]")

def latex_rule1233(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\|")

def latex_rule1234(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\updownarrow")

def latex_rule1235(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\uparrow")

def latex_rule1236(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\rfloor")

def latex_rule1237(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\rceil")

def latex_rule1238(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\rangle")

def latex_rule1239(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\lfloor")

def latex_rule1240(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\lceil")

def latex_rule1241(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\langle")

def latex_rule1242(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\downarrow")

def latex_rule1243(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\backslash")

def latex_rule1244(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\Updownarrow")

def latex_rule1245(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\Uparrow")

def latex_rule1246(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\Downarrow")

def latex_rule1247(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\)")

def latex_rule1248(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left\\(")

def latex_rule1249(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\left[")

def latex_rule1250(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left/")

def latex_rule1251(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left)")

def latex_rule1252(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\left(")

def latex_rule1253(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ldots")

def latex_rule1254(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\lambda")

def latex_rule1255(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ker")

def latex_rule1256(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\kappa")

def latex_rule1257(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\jmath")

def latex_rule1258(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\jmath")

def latex_rule1259(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\iota")

def latex_rule1260(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\intercal")

def latex_rule1261(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\int")

def latex_rule1262(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\infty")

def latex_rule1263(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\inf")

def latex_rule1264(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\in")

def latex_rule1265(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\imath")

def latex_rule1266(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\imath")

def latex_rule1267(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hslash")

def latex_rule1268(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hookrightarrow")

def latex_rule1269(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hookleftarrow")

def latex_rule1270(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hom")

def latex_rule1271(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hline")

def latex_rule1272(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\heartsuit")

def latex_rule1273(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hbar")

def latex_rule1274(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hat{")

def latex_rule1275(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gvertneqq")

def latex_rule1276(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrsim")

def latex_rule1277(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrless")

def latex_rule1278(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtreqqless")

def latex_rule1279(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtreqless")

def latex_rule1280(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrdot")

def latex_rule1281(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gtrapprox")

def latex_rule1282(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\grave{")

def latex_rule1283(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gnsim")

def latex_rule1284(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gneqq")

def latex_rule1285(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gneq")

def latex_rule1286(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gnapprox")

def latex_rule1287(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gnapprox")

def latex_rule1288(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gimel")

def latex_rule1289(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ggg")

def latex_rule1290(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gg")

def latex_rule1291(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\geqslant")

def latex_rule1292(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\geqq")

def latex_rule1293(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\geq")

def latex_rule1294(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gcd")

def latex_rule1295(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\gamma")

def latex_rule1296(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\frown")

def latex_rule1297(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\frak{")

def latex_rule1298(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\frac{")

def latex_rule1299(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\forall")

def latex_rule1300(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\flat")

def latex_rule1301(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fallingdotseq")

def latex_rule1302(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\exp")

def latex_rule1303(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\exists")

def latex_rule1304(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eth")

def latex_rule1305(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eta")

def latex_rule1306(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\equiv")

def latex_rule1307(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eqslantless")

def latex_rule1308(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eqslantgtr")

def latex_rule1309(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\eqcirc")

def latex_rule1310(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\epsilon")

def latex_rule1311(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ensuremath{")

def latex_rule1312(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\end{")

def latex_rule1313(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\emptyset")

def latex_rule1314(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ell")

def latex_rule1315(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downharpoonright")

def latex_rule1316(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downharpoonleft")

def latex_rule1317(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downdownarrows")

def latex_rule1318(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\downarrow")

def latex_rule1319(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\doublebarwedge")

def latex_rule1320(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\dot{")

def latex_rule1321(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dotplus")

def latex_rule1322(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\doteqdot")

def latex_rule1323(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\doteq")

def latex_rule1324(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\divideontimes")

def latex_rule1325(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\div")

def latex_rule1326(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\displaystyle")

def latex_rule1327(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dim")

def latex_rule1328(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\digamma")

def latex_rule1329(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diamondsuit")

def latex_rule1330(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diamond")

def latex_rule1331(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diagup")

def latex_rule1332(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\diagdown")

def latex_rule1333(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\det")

def latex_rule1334(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\delta")

def latex_rule1335(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\deg")

def latex_rule1336(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ddot{")

def latex_rule1337(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ddots")

def latex_rule1338(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ddagger")

def latex_rule1339(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dashv")

def latex_rule1340(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dashrightarrow")

def latex_rule1341(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dashleftarrow")

def latex_rule1342(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\daleth")

def latex_rule1343(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dagger")

def latex_rule1344(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curvearrowright")

def latex_rule1345(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curvearrowleft")

def latex_rule1346(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlywedge")

def latex_rule1347(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlyvee")

def latex_rule1348(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlyeqsucc")

def latex_rule1349(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\curlyeqprec")

def latex_rule1350(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cup")

def latex_rule1351(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\csc")

def latex_rule1352(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\coth")

def latex_rule1353(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cot")

def latex_rule1354(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cosh")

def latex_rule1355(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cos")

def latex_rule1356(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\coprod")

def latex_rule1357(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cong")

def latex_rule1358(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\complement")

def latex_rule1359(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\clubsuit")

def latex_rule1360(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cline{")

def latex_rule1361(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circleddash")

def latex_rule1362(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circledcirc")

def latex_rule1363(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circledast")

def latex_rule1364(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circledS")

def latex_rule1365(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circlearrowright")

def latex_rule1366(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circlearrowleft")

def latex_rule1367(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circeq")

def latex_rule1368(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\circ")

def latex_rule1369(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\chi")

def latex_rule1370(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\check{")

def latex_rule1371(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\centerdot")

def latex_rule1372(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cdots")

def latex_rule1373(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cdot")

def latex_rule1374(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cap")

def latex_rule1375(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bumpeq")

def latex_rule1376(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bullet")

def latex_rule1377(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\breve{")

def latex_rule1378(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxtimes")

def latex_rule1379(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxplus")

def latex_rule1380(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxminus")

def latex_rule1381(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\boxdot")

def latex_rule1382(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bowtie")

def latex_rule1383(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bot")

def latex_rule1384(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boldsymbol{")

def latex_rule1385(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bmod")

def latex_rule1386(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangleright")

def latex_rule1387(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangleleft")

def latex_rule1388(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangledown")

def latex_rule1389(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacktriangle")

def latex_rule1390(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacksquare")

def latex_rule1391(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\blacklozenge")

def latex_rule1392(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigwedge")

def latex_rule1393(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigvee")

def latex_rule1394(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\biguplus")

def latex_rule1395(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigtriangleup")

def latex_rule1396(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigtriangledown")

def latex_rule1397(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigstar")

def latex_rule1398(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigsqcup")

def latex_rule1399(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigotimes")

def latex_rule1400(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigoplus")

def latex_rule1401(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigodot")

def latex_rule1402(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigcup")

def latex_rule1403(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigcirc")

def latex_rule1404(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigcap")

def latex_rule1405(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\between")

def latex_rule1406(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\beth")

def latex_rule1407(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\beta")

def latex_rule1408(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\begin{")

def latex_rule1409(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\because")

def latex_rule1410(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bar{")

def latex_rule1411(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\barwedge")

def latex_rule1412(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backslash")

def latex_rule1413(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backsimeq")

def latex_rule1414(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backsim")

def latex_rule1415(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\backprime")

def latex_rule1416(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\asymp")

def latex_rule1417(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ast")

def latex_rule1418(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arg")

def latex_rule1419(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arctan")

def latex_rule1420(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arcsin")

def latex_rule1421(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\arccos")

def latex_rule1422(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\approxeq")

def latex_rule1423(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\approx")

def latex_rule1424(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\angle")

def latex_rule1425(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\angle")

def latex_rule1426(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\amalg")

def latex_rule1427(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\alpha")

def latex_rule1428(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\aleph")

def latex_rule1429(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\acute{")

def latex_rule1430(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Xi")

def latex_rule1431(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Vvdash")

def latex_rule1432(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Vdash")

def latex_rule1433(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Upsilon")

def latex_rule1434(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Updownarrow")

def latex_rule1435(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Uparrow")

def latex_rule1436(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Theta")

def latex_rule1437(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Supset")

def latex_rule1438(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Subset")

def latex_rule1439(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Sigma")

def latex_rule1440(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Rsh")

def latex_rule1441(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Rightarrow")

def latex_rule1442(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Re")

def latex_rule1443(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Psi")

def latex_rule1444(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Pr")

def latex_rule1445(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Pi")

def latex_rule1446(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Phi")

def latex_rule1447(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Omega")

def latex_rule1448(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Lsh")

def latex_rule1449(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Longrightarrow")

def latex_rule1450(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Longleftrightarrow")

def latex_rule1451(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Longleftarrow")

def latex_rule1452(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Lleftarrow")

def latex_rule1453(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Leftrightarrow")

def latex_rule1454(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Leftarrow")

def latex_rule1455(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Lambda")

def latex_rule1456(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Im")

def latex_rule1457(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Gamma")

def latex_rule1458(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Game")

def latex_rule1459(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Finv")

def latex_rule1460(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Downarrow")

def latex_rule1461(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Delta")

def latex_rule1462(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Cup")

def latex_rule1463(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Cap")

def latex_rule1464(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Bumpeq")

def latex_rule1465(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Bbb{")

def latex_rule1466(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Bbbk")

def latex_rule1467(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\;")

def latex_rule1468(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\:")

def latex_rule1469(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\,")

def latex_rule1470(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\!")

def latex_rule1471(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="'")

def latex_rule1472(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def latex_rule1473(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="\\")

# Rules dict for latex_arraymode ruleset.
rulesDict3 = {
    "%": [latex_rule950,],
    "&": [latex_rule1472,],
    "'": [latex_rule1471,],
    "\\": [latex_rule953, latex_rule954, latex_rule955, latex_rule956, latex_rule957, latex_rule958, latex_rule959, latex_rule960, latex_rule961, latex_rule962, latex_rule963, latex_rule964, latex_rule965, latex_rule966, latex_rule967, latex_rule968, latex_rule969, latex_rule970, latex_rule971, latex_rule972, latex_rule973, latex_rule974, latex_rule975, latex_rule976, latex_rule977, latex_rule978, latex_rule979, latex_rule980, latex_rule981, latex_rule982, latex_rule983, latex_rule984, latex_rule985, latex_rule986, latex_rule987, latex_rule988, latex_rule989, latex_rule990, latex_rule991, latex_rule992, latex_rule993, latex_rule994, latex_rule995, latex_rule996, latex_rule997, latex_rule998, latex_rule999, latex_rule1000, latex_rule1001, latex_rule1002, latex_rule1003, latex_rule1004, latex_rule1005, latex_rule1006, latex_rule1007, latex_rule1008, latex_rule1009, latex_rule1010, latex_rule1011, latex_rule1012, latex_rule1013, latex_rule1014, latex_rule1015, latex_rule1016, latex_rule1017, latex_rule1018, latex_rule1019, latex_rule1020, latex_rule1021, latex_rule1022, latex_rule1023, latex_rule1024, latex_rule1025, latex_rule1026, latex_rule1027, latex_rule1028, latex_rule1029, latex_rule1030, latex_rule1031, latex_rule1032, latex_rule1033, latex_rule1034, latex_rule1035, latex_rule1036, latex_rule1037, latex_rule1038, latex_rule1039, latex_rule1040, latex_rule1041, latex_rule1042, latex_rule1043, latex_rule1044, latex_rule1045, latex_rule1046, latex_rule1047, latex_rule1048, latex_rule1049, latex_rule1050, latex_rule1051, latex_rule1052, latex_rule1053, latex_rule1054, latex_rule1055, latex_rule1056, latex_rule1057, latex_rule1058, latex_rule1059, latex_rule1060, latex_rule1061, latex_rule1062, latex_rule1063, latex_rule1064, latex_rule1065, latex_rule1066, latex_rule1067, latex_rule1068, latex_rule1069, latex_rule1070, latex_rule1071, latex_rule1072, latex_rule1073, latex_rule1074, latex_rule1075, latex_rule1076, latex_rule1077, latex_rule1078, latex_rule1079, latex_rule1080, latex_rule1081, latex_rule1082, latex_rule1083, latex_rule1084, latex_rule1085, latex_rule1086, latex_rule1087, latex_rule1088, latex_rule1089, latex_rule1090, latex_rule1091, latex_rule1092, latex_rule1093, latex_rule1094, latex_rule1095, latex_rule1096, latex_rule1097, latex_rule1098, latex_rule1099, latex_rule1100, latex_rule1101, latex_rule1102, latex_rule1103, latex_rule1104, latex_rule1105, latex_rule1106, latex_rule1107, latex_rule1108, latex_rule1109, latex_rule1110, latex_rule1111, latex_rule1112, latex_rule1113, latex_rule1114, latex_rule1115, latex_rule1116, latex_rule1117, latex_rule1118, latex_rule1119, latex_rule1120, latex_rule1121, latex_rule1122, latex_rule1123, latex_rule1124, latex_rule1125, latex_rule1126, latex_rule1127, latex_rule1128, latex_rule1129, latex_rule1130, latex_rule1131, latex_rule1132, latex_rule1133, latex_rule1134, latex_rule1135, latex_rule1136, latex_rule1137, latex_rule1138, latex_rule1139, latex_rule1140, latex_rule1141, latex_rule1142, latex_rule1143, latex_rule1144, latex_rule1145, latex_rule1146, latex_rule1147, latex_rule1148, latex_rule1149, latex_rule1150, latex_rule1151, latex_rule1152, latex_rule1153, latex_rule1154, latex_rule1155, latex_rule1156, latex_rule1157, latex_rule1158, latex_rule1159, latex_rule1160, latex_rule1161, latex_rule1162, latex_rule1163, latex_rule1164, latex_rule1165, latex_rule1166, latex_rule1167, latex_rule1168, latex_rule1169, latex_rule1170, latex_rule1171, latex_rule1172, latex_rule1173, latex_rule1174, latex_rule1175, latex_rule1176, latex_rule1177, latex_rule1178, latex_rule1179, latex_rule1180, latex_rule1181, latex_rule1182, latex_rule1183, latex_rule1184, latex_rule1185, latex_rule1186, latex_rule1187, latex_rule1188, latex_rule1189, latex_rule1190, latex_rule1191, latex_rule1192, latex_rule1193, latex_rule1194, latex_rule1195, latex_rule1196, latex_rule1197, latex_rule1198, latex_rule1199, latex_rule1200, latex_rule1201, latex_rule1202, latex_rule1203, latex_rule1204, latex_rule1205, latex_rule1206, latex_rule1207, latex_rule1208, latex_rule1209, latex_rule1210, latex_rule1211, latex_rule1212, latex_rule1213, latex_rule1214, latex_rule1215, latex_rule1216, latex_rule1217, latex_rule1218, latex_rule1219, latex_rule1220, latex_rule1221, latex_rule1222, latex_rule1223, latex_rule1224, latex_rule1225, latex_rule1226, latex_rule1227, latex_rule1228, latex_rule1229, latex_rule1230, latex_rule1231, latex_rule1232, latex_rule1233, latex_rule1234, latex_rule1235, latex_rule1236, latex_rule1237, latex_rule1238, latex_rule1239, latex_rule1240, latex_rule1241, latex_rule1242, latex_rule1243, latex_rule1244, latex_rule1245, latex_rule1246, latex_rule1247, latex_rule1248, latex_rule1249, latex_rule1250, latex_rule1251, latex_rule1252, latex_rule1253, latex_rule1254, latex_rule1255, latex_rule1256, latex_rule1257, latex_rule1258, latex_rule1259, latex_rule1260, latex_rule1261, latex_rule1262, latex_rule1263, latex_rule1264, latex_rule1265, latex_rule1266, latex_rule1267, latex_rule1268, latex_rule1269, latex_rule1270, latex_rule1271, latex_rule1272, latex_rule1273, latex_rule1274, latex_rule1275, latex_rule1276, latex_rule1277, latex_rule1278, latex_rule1279, latex_rule1280, latex_rule1281, latex_rule1282, latex_rule1283, latex_rule1284, latex_rule1285, latex_rule1286, latex_rule1287, latex_rule1288, latex_rule1289, latex_rule1290, latex_rule1291, latex_rule1292, latex_rule1293, latex_rule1294, latex_rule1295, latex_rule1296, latex_rule1297, latex_rule1298, latex_rule1299, latex_rule1300, latex_rule1301, latex_rule1302, latex_rule1303, latex_rule1304, latex_rule1305, latex_rule1306, latex_rule1307, latex_rule1308, latex_rule1309, latex_rule1310, latex_rule1311, latex_rule1312, latex_rule1313, latex_rule1314, latex_rule1315, latex_rule1316, latex_rule1317, latex_rule1318, latex_rule1319, latex_rule1320, latex_rule1321, latex_rule1322, latex_rule1323, latex_rule1324, latex_rule1325, latex_rule1326, latex_rule1327, latex_rule1328, latex_rule1329, latex_rule1330, latex_rule1331, latex_rule1332, latex_rule1333, latex_rule1334, latex_rule1335, latex_rule1336, latex_rule1337, latex_rule1338, latex_rule1339, latex_rule1340, latex_rule1341, latex_rule1342, latex_rule1343, latex_rule1344, latex_rule1345, latex_rule1346, latex_rule1347, latex_rule1348, latex_rule1349, latex_rule1350, latex_rule1351, latex_rule1352, latex_rule1353, latex_rule1354, latex_rule1355, latex_rule1356, latex_rule1357, latex_rule1358, latex_rule1359, latex_rule1360, latex_rule1361, latex_rule1362, latex_rule1363, latex_rule1364, latex_rule1365, latex_rule1366, latex_rule1367, latex_rule1368, latex_rule1369, latex_rule1370, latex_rule1371, latex_rule1372, latex_rule1373, latex_rule1374, latex_rule1375, latex_rule1376, latex_rule1377, latex_rule1378, latex_rule1379, latex_rule1380, latex_rule1381, latex_rule1382, latex_rule1383, latex_rule1384, latex_rule1385, latex_rule1386, latex_rule1387, latex_rule1388, latex_rule1389, latex_rule1390, latex_rule1391, latex_rule1392, latex_rule1393, latex_rule1394, latex_rule1395, latex_rule1396, latex_rule1397, latex_rule1398, latex_rule1399, latex_rule1400, latex_rule1401, latex_rule1402, latex_rule1403, latex_rule1404, latex_rule1405, latex_rule1406, latex_rule1407, latex_rule1408, latex_rule1409, latex_rule1410, latex_rule1411, latex_rule1412, latex_rule1413, latex_rule1414, latex_rule1415, latex_rule1416, latex_rule1417, latex_rule1418, latex_rule1419, latex_rule1420, latex_rule1421, latex_rule1422, latex_rule1423, latex_rule1424, latex_rule1425, latex_rule1426, latex_rule1427, latex_rule1428, latex_rule1429, latex_rule1430, latex_rule1431, latex_rule1432, latex_rule1433, latex_rule1434, latex_rule1435, latex_rule1436, latex_rule1437, latex_rule1438, latex_rule1439, latex_rule1440, latex_rule1441, latex_rule1442, latex_rule1443, latex_rule1444, latex_rule1445, latex_rule1446, latex_rule1447, latex_rule1448, latex_rule1449, latex_rule1450, latex_rule1451, latex_rule1452, latex_rule1453, latex_rule1454, latex_rule1455, latex_rule1456, latex_rule1457, latex_rule1458, latex_rule1459, latex_rule1460, latex_rule1461, latex_rule1462, latex_rule1463, latex_rule1464, latex_rule1465, latex_rule1466, latex_rule1467, latex_rule1468, latex_rule1469, latex_rule1470, latex_rule1473,],
    "^": [latex_rule952,],
    "_": [latex_rule949, latex_rule951,],
}

# Rules for latex_tabularmode ruleset.

def latex_rule1474(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="__TabularMode__")

def latex_rule1475(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def latex_rule1476(colorer, s, i):
    return colorer.match_span(s, i, kind="literal4", begin="``", end="''")

def latex_rule1477(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="`", end="'")

def latex_rule1478(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def latex_rule1479(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\"")

def latex_rule1480(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="`")

def latex_rule1481(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def latex_rule1482(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="}")

def latex_rule1483(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="{")

def latex_rule1484(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="totalnumber")

def latex_rule1485(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="topnumber")

def latex_rule1486(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="tocdepth")

def latex_rule1487(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="secnumdepth")

def latex_rule1488(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="dbltopnumber")

def latex_rule1489(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="]")

def latex_rule1490(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\~{")

def latex_rule1491(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\~")

def latex_rule1492(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\}")

def latex_rule1493(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\|")

def latex_rule1494(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\{")

def latex_rule1495(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\width")

def latex_rule1496(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\whiledo{")

def latex_rule1497(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\v{")

def latex_rule1498(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vspace{")

def latex_rule1499(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vspace*{")

def latex_rule1500(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vline")

def latex_rule1501(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vfill")

def latex_rule1502(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\verb*")

def latex_rule1503(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\verb")

def latex_rule1504(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\value{")

def latex_rule1505(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\v")

def latex_rule1506(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\u{")

def latex_rule1507(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usepackage{")

def latex_rule1508(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usepackage[")

def latex_rule1509(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usecounter{")

def latex_rule1510(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usebox{")

def latex_rule1511(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upshape")

def latex_rule1512(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\unboldmath{")

def latex_rule1513(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\u")

def latex_rule1514(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\t{")

def latex_rule1515(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typeout{")

def latex_rule1516(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typein{")

def latex_rule1517(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typein[")

def latex_rule1518(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\twocolumn[")

def latex_rule1519(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\twocolumn")

def latex_rule1520(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ttfamily")

def latex_rule1521(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\totalheight")

def latex_rule1522(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\topsep")

def latex_rule1523(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\topfraction")

def latex_rule1524(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\today")

def latex_rule1525(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\title{")

def latex_rule1526(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tiny")

def latex_rule1527(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\thispagestyle{")

def latex_rule1528(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thinlines")

def latex_rule1529(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thicklines")

def latex_rule1530(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\thanks{")

def latex_rule1531(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textwidth")

def latex_rule1532(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textup{")

def latex_rule1533(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\texttt{")

def latex_rule1534(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsl{")

def latex_rule1535(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsf{")

def latex_rule1536(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsc{")

def latex_rule1537(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textrm{")

def latex_rule1538(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textnormal{")

def latex_rule1539(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textmd{")

def latex_rule1540(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textit{")

def latex_rule1541(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textfraction")

def latex_rule1542(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textfloatsep")

def latex_rule1543(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textcolor{")

def latex_rule1544(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textbf{")

def latex_rule1545(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tableofcontents")

def latex_rule1546(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\tabcolsep")

def latex_rule1547(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\tabbingsep")

def latex_rule1548(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\t")

def latex_rule1549(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\symbol{")

def latex_rule1550(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\suppressfloats[")

def latex_rule1551(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\suppressfloats")

def latex_rule1552(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection{")

def latex_rule1553(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection[")

def latex_rule1554(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection*{")

def latex_rule1555(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection{")

def latex_rule1556(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection[")

def latex_rule1557(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection*{")

def latex_rule1558(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph{")

def latex_rule1559(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph[")

def latex_rule1560(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph*{")

def latex_rule1561(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stretch{")

def latex_rule1562(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stepcounter{")

def latex_rule1563(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallskip")

def latex_rule1564(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\small")

def latex_rule1565(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\slshape")

def latex_rule1566(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sloppy")

def latex_rule1567(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sffamily")

def latex_rule1568(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settowidth{")

def latex_rule1569(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settoheight{")

def latex_rule1570(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settodepth{")

def latex_rule1571(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\setlength{")

def latex_rule1572(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\setcounter{")

def latex_rule1573(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section{")

def latex_rule1574(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section[")

def latex_rule1575(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section*{")

def latex_rule1576(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scshape")

def latex_rule1577(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scriptsize")

def latex_rule1578(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\scalebox{")

def latex_rule1579(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\sbox{")

def latex_rule1580(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\savebox{")

def latex_rule1581(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rule{")

def latex_rule1582(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rule[")

def latex_rule1583(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rp,am{")

def latex_rule1584(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rotatebox{")

def latex_rule1585(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rmfamily")

def latex_rule1586(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\rightmargin")

def latex_rule1587(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\reversemarginpar")

def latex_rule1588(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\resizebox{")

def latex_rule1589(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\resizebox*{")

def latex_rule1590(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\renewenvironment{")

def latex_rule1591(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\renewcommand{")

def latex_rule1592(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ref{")

def latex_rule1593(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\refstepcounter")

def latex_rule1594(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\raisebox{")

def latex_rule1595(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\raggedright")

def latex_rule1596(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\raggedleft")

def latex_rule1597(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\qbeziermax")

def latex_rule1598(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\providecommand{")

def latex_rule1599(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\protect")

def latex_rule1600(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\printindex")

def latex_rule1601(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pounds")

def latex_rule1602(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part{")

def latex_rule1603(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\partopsep")

def latex_rule1604(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part[")

def latex_rule1605(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part*{")

def latex_rule1606(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parskip")

def latex_rule1607(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parsep")

def latex_rule1608(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parindent")

def latex_rule1609(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\parbox{")

def latex_rule1610(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\parbox[")

def latex_rule1611(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph{")

def latex_rule1612(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph[")

def latex_rule1613(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph*{")

def latex_rule1614(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\par")

def latex_rule1615(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagestyle{")

def latex_rule1616(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pageref{")

def latex_rule1617(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagenumbering{")

def latex_rule1618(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagecolor{")

def latex_rule1619(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagebreak[")

def latex_rule1620(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pagebreak")

def latex_rule1621(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\onecolumn")

def latex_rule1622(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalsize")

def latex_rule1623(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalmarginpar")

def latex_rule1624(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalfont")

def latex_rule1625(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nopagebreak[")

def latex_rule1626(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nopagebreak")

def latex_rule1627(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nonfrenchspacing")

def latex_rule1628(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nolinebreak[")

def latex_rule1629(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nolinebreak")

def latex_rule1630(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\noindent")

def latex_rule1631(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nocite{")

def latex_rule1632(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newtheorem{")

def latex_rule1633(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newsavebox{")

def latex_rule1634(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\newpage")

def latex_rule1635(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newlength{")

def latex_rule1636(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newenvironment{")

def latex_rule1637(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newcounter{")

def latex_rule1638(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newcommand{")

def latex_rule1639(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\multicolumn{")

def latex_rule1640(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\medskip")

def latex_rule1641(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mdseries")

def latex_rule1642(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mbox{")

def latex_rule1643(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mbox{")

def latex_rule1644(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\mathindent")

def latex_rule1645(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\mathindent")

def latex_rule1646(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\markright{")

def latex_rule1647(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\markboth{")

def latex_rule1648(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\marginpar{")

def latex_rule1649(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparwidth")

def latex_rule1650(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparsep")

def latex_rule1651(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparpush")

def latex_rule1652(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\marginpar[")

def latex_rule1653(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\maketitle")

def latex_rule1654(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\makelabel")

def latex_rule1655(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\makeindex")

def latex_rule1656(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\makeglossary")

def latex_rule1657(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\makebox{")

def latex_rule1658(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\makebox[")

def latex_rule1659(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\listparindent")

def latex_rule1660(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listoftables")

def latex_rule1661(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listoffigures")

def latex_rule1662(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listfiles")

def latex_rule1663(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\linewidth")

def latex_rule1664(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\linethickness{")

def latex_rule1665(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\linebreak[")

def latex_rule1666(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\linebreak")

def latex_rule1667(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\lengthtest{")

def latex_rule1668(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginvi")

def latex_rule1669(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginv")

def latex_rule1670(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginiv")

def latex_rule1671(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginiii")

def latex_rule1672(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginii")

def latex_rule1673(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmargini")

def latex_rule1674(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmargin")

def latex_rule1675(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\large")

def latex_rule1676(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\label{")

def latex_rule1677(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\labelwidth")

def latex_rule1678(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\labelsep")

def latex_rule1679(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\jot")

def latex_rule1680(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\itshape")

def latex_rule1681(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\itemsep")

def latex_rule1682(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\itemindent")

def latex_rule1683(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\item[")

def latex_rule1684(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\item")

def latex_rule1685(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\isodd{")

def latex_rule1686(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\intextsep")

def latex_rule1687(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\input{")

def latex_rule1688(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\index{")

def latex_rule1689(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\indent")

def latex_rule1690(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\include{")

def latex_rule1691(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includeonly{")

def latex_rule1692(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics{")

def latex_rule1693(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics[")

def latex_rule1694(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics*{")

def latex_rule1695(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics*[")

def latex_rule1696(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ifthenelse{")

def latex_rule1697(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hyphenation{")

def latex_rule1698(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\huge")

def latex_rule1699(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hspace{")

def latex_rule1700(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hspace*{")

def latex_rule1701(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hline")

def latex_rule1702(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hfill")

def latex_rule1703(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\height")

def latex_rule1704(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\glossary{")

def latex_rule1705(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fussy")

def latex_rule1706(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\frenchspacing")

def latex_rule1707(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\framebox{")

def latex_rule1708(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\framebox[")

def latex_rule1709(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fragile")

def latex_rule1710(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnote{")

def latex_rule1711(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotetext{")

def latex_rule1712(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotetext[")

def latex_rule1713(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\footnotesize")

def latex_rule1714(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\footnotesep")

def latex_rule1715(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\footnoterule")

def latex_rule1716(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotemark[")

def latex_rule1717(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\footnotemark")

def latex_rule1718(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnote[")

def latex_rule1719(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fnsymbol{")

def latex_rule1720(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\floatsep")

def latex_rule1721(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\floatpagefraction")

def latex_rule1722(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fill")

def latex_rule1723(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fcolorbox{")

def latex_rule1724(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fbox{")

def latex_rule1725(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\fboxsep")

def latex_rule1726(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\fboxrule")

def latex_rule1727(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\equal{")

def latex_rule1728(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ensuremath{")

def latex_rule1729(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\enlargethispage{")

def latex_rule1730(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\enlargethispage*{")

def latex_rule1731(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\end{")

def latex_rule1732(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\emph{")

def latex_rule1733(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\d{")

def latex_rule1734(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\doublerulesep")

def latex_rule1735(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\documentclass{")

def latex_rule1736(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\documentclass[")

def latex_rule1737(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\depth")

def latex_rule1738(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\definecolor{")

def latex_rule1739(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ddag")

def latex_rule1740(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dbltopfraction")

def latex_rule1741(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dbltextfloatsep")

def latex_rule1742(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dblfloatsep")

def latex_rule1743(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dblfloatpagefraction")

def latex_rule1744(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\date{")

def latex_rule1745(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dag")

def latex_rule1746(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\d")

def latex_rule1747(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\c{")

def latex_rule1748(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\copyright")

def latex_rule1749(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnwidth")

def latex_rule1750(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnseprule")

def latex_rule1751(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnsep")

def latex_rule1752(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\color{")

def latex_rule1753(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\colorbox{")

def latex_rule1754(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cline{")

def latex_rule1755(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\clearpage")

def latex_rule1756(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cleardoublepage")

def latex_rule1757(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cite{")

def latex_rule1758(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cite[")

def latex_rule1759(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter{")

def latex_rule1760(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter[")

def latex_rule1761(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter*{")

def latex_rule1762(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\centering")

def latex_rule1763(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\caption{")

def latex_rule1764(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\caption[")

def latex_rule1765(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\c")

def latex_rule1766(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\b{")

def latex_rule1767(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bottomnumber")

def latex_rule1768(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bottomfraction")

def latex_rule1769(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boolean{")

def latex_rule1770(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boldmath{")

def latex_rule1771(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigskip")

def latex_rule1772(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bibliography{")

def latex_rule1773(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bibliographystyle{")

def latex_rule1774(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bibindent")

def latex_rule1775(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bfseries")

def latex_rule1776(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\belowdisplayskip")

def latex_rule1777(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\belowdisplayshortskip")

def latex_rule1778(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\begin{")

def latex_rule1779(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\baselinestretch")

def latex_rule1780(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\baselineskip")

def latex_rule1781(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\b")

def latex_rule1782(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\author{")

def latex_rule1783(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arraystgretch")

def latex_rule1784(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arrayrulewidth")

def latex_rule1785(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arraycolsep")

def latex_rule1786(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\arabic{")

def latex_rule1787(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\appendix")

def latex_rule1788(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\alph{")

def latex_rule1789(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addvspace{")

def latex_rule1790(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtolength{")

def latex_rule1791(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtocounter{")

def latex_rule1792(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtocontents{")

def latex_rule1793(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addcontentsline{")

def latex_rule1794(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\abovedisplayskip")

def latex_rule1795(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\abovedisplayshortskip")

def latex_rule1796(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\`{")

def latex_rule1797(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\`")

def latex_rule1798(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\_")

def latex_rule1799(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\^{")

def latex_rule1800(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\^")

def latex_rule1801(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\\[")

def latex_rule1802(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\\*[")

def latex_rule1803(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\*")

def latex_rule1804(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\")

def latex_rule1805(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\TeX")

def latex_rule1806(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\S")

def latex_rule1807(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Roman{")

def latex_rule1808(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\P")

def latex_rule1809(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Large")

def latex_rule1810(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\LaTeX")

def latex_rule1811(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\LARGE")

def latex_rule1812(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\H{")

def latex_rule1813(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Huge")

def latex_rule1814(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\H")

def latex_rule1815(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Alph{")

def latex_rule1816(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\@")

def latex_rule1817(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\={")

def latex_rule1818(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\=")

def latex_rule1819(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\.{")

def latex_rule1820(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\.")

def latex_rule1821(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\-")

def latex_rule1822(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\,")

def latex_rule1823(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\'{")

def latex_rule1824(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\'")

def latex_rule1825(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\&")

def latex_rule1826(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\%")

def latex_rule1827(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\$")

def latex_rule1828(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\#")

def latex_rule1829(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\"{")

def latex_rule1830(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\"")

def latex_rule1831(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def latex_rule1832(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="[")

def latex_rule1833(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="---")

def latex_rule1834(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="--")

def latex_rule1835(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def latex_rule1836(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def latex_rule1837(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="\\")

# Rules dict for latex_tabularmode ruleset.
rulesDict4 = {
    "\"": [latex_rule1478, latex_rule1479,],
    "%": [latex_rule1475,],
    "&": [latex_rule1836,],
    "-": [latex_rule1833, latex_rule1834, latex_rule1835,],
    "[": [latex_rule1832,],
    "\\": [latex_rule1490, latex_rule1491, latex_rule1492, latex_rule1493, latex_rule1494, latex_rule1495, latex_rule1496, latex_rule1497, latex_rule1498, latex_rule1499, latex_rule1500, latex_rule1501, latex_rule1502, latex_rule1503, latex_rule1504, latex_rule1505, latex_rule1506, latex_rule1507, latex_rule1508, latex_rule1509, latex_rule1510, latex_rule1511, latex_rule1512, latex_rule1513, latex_rule1514, latex_rule1515, latex_rule1516, latex_rule1517, latex_rule1518, latex_rule1519, latex_rule1520, latex_rule1521, latex_rule1522, latex_rule1523, latex_rule1524, latex_rule1525, latex_rule1526, latex_rule1527, latex_rule1528, latex_rule1529, latex_rule1530, latex_rule1531, latex_rule1532, latex_rule1533, latex_rule1534, latex_rule1535, latex_rule1536, latex_rule1537, latex_rule1538, latex_rule1539, latex_rule1540, latex_rule1541, latex_rule1542, latex_rule1543, latex_rule1544, latex_rule1545, latex_rule1546, latex_rule1547, latex_rule1548, latex_rule1549, latex_rule1550, latex_rule1551, latex_rule1552, latex_rule1553, latex_rule1554, latex_rule1555, latex_rule1556, latex_rule1557, latex_rule1558, latex_rule1559, latex_rule1560, latex_rule1561, latex_rule1562, latex_rule1563, latex_rule1564, latex_rule1565, latex_rule1566, latex_rule1567, latex_rule1568, latex_rule1569, latex_rule1570, latex_rule1571, latex_rule1572, latex_rule1573, latex_rule1574, latex_rule1575, latex_rule1576, latex_rule1577, latex_rule1578, latex_rule1579, latex_rule1580, latex_rule1581, latex_rule1582, latex_rule1583, latex_rule1584, latex_rule1585, latex_rule1586, latex_rule1587, latex_rule1588, latex_rule1589, latex_rule1590, latex_rule1591, latex_rule1592, latex_rule1593, latex_rule1594, latex_rule1595, latex_rule1596, latex_rule1597, latex_rule1598, latex_rule1599, latex_rule1600, latex_rule1601, latex_rule1602, latex_rule1603, latex_rule1604, latex_rule1605, latex_rule1606, latex_rule1607, latex_rule1608, latex_rule1609, latex_rule1610, latex_rule1611, latex_rule1612, latex_rule1613, latex_rule1614, latex_rule1615, latex_rule1616, latex_rule1617, latex_rule1618, latex_rule1619, latex_rule1620, latex_rule1621, latex_rule1622, latex_rule1623, latex_rule1624, latex_rule1625, latex_rule1626, latex_rule1627, latex_rule1628, latex_rule1629, latex_rule1630, latex_rule1631, latex_rule1632, latex_rule1633, latex_rule1634, latex_rule1635, latex_rule1636, latex_rule1637, latex_rule1638, latex_rule1639, latex_rule1640, latex_rule1641, latex_rule1642, latex_rule1643, latex_rule1644, latex_rule1645, latex_rule1646, latex_rule1647, latex_rule1648, latex_rule1649, latex_rule1650, latex_rule1651, latex_rule1652, latex_rule1653, latex_rule1654, latex_rule1655, latex_rule1656, latex_rule1657, latex_rule1658, latex_rule1659, latex_rule1660, latex_rule1661, latex_rule1662, latex_rule1663, latex_rule1664, latex_rule1665, latex_rule1666, latex_rule1667, latex_rule1668, latex_rule1669, latex_rule1670, latex_rule1671, latex_rule1672, latex_rule1673, latex_rule1674, latex_rule1675, latex_rule1676, latex_rule1677, latex_rule1678, latex_rule1679, latex_rule1680, latex_rule1681, latex_rule1682, latex_rule1683, latex_rule1684, latex_rule1685, latex_rule1686, latex_rule1687, latex_rule1688, latex_rule1689, latex_rule1690, latex_rule1691, latex_rule1692, latex_rule1693, latex_rule1694, latex_rule1695, latex_rule1696, latex_rule1697, latex_rule1698, latex_rule1699, latex_rule1700, latex_rule1701, latex_rule1702, latex_rule1703, latex_rule1704, latex_rule1705, latex_rule1706, latex_rule1707, latex_rule1708, latex_rule1709, latex_rule1710, latex_rule1711, latex_rule1712, latex_rule1713, latex_rule1714, latex_rule1715, latex_rule1716, latex_rule1717, latex_rule1718, latex_rule1719, latex_rule1720, latex_rule1721, latex_rule1722, latex_rule1723, latex_rule1724, latex_rule1725, latex_rule1726, latex_rule1727, latex_rule1728, latex_rule1729, latex_rule1730, latex_rule1731, latex_rule1732, latex_rule1733, latex_rule1734, latex_rule1735, latex_rule1736, latex_rule1737, latex_rule1738, latex_rule1739, latex_rule1740, latex_rule1741, latex_rule1742, latex_rule1743, latex_rule1744, latex_rule1745, latex_rule1746, latex_rule1747, latex_rule1748, latex_rule1749, latex_rule1750, latex_rule1751, latex_rule1752, latex_rule1753, latex_rule1754, latex_rule1755, latex_rule1756, latex_rule1757, latex_rule1758, latex_rule1759, latex_rule1760, latex_rule1761, latex_rule1762, latex_rule1763, latex_rule1764, latex_rule1765, latex_rule1766, latex_rule1767, latex_rule1768, latex_rule1769, latex_rule1770, latex_rule1771, latex_rule1772, latex_rule1773, latex_rule1774, latex_rule1775, latex_rule1776, latex_rule1777, latex_rule1778, latex_rule1779, latex_rule1780, latex_rule1781, latex_rule1782, latex_rule1783, latex_rule1784, latex_rule1785, latex_rule1786, latex_rule1787, latex_rule1788, latex_rule1789, latex_rule1790, latex_rule1791, latex_rule1792, latex_rule1793, latex_rule1794, latex_rule1795, latex_rule1796, latex_rule1797, latex_rule1798, latex_rule1799, latex_rule1800, latex_rule1801, latex_rule1802, latex_rule1803, latex_rule1804, latex_rule1805, latex_rule1806, latex_rule1807, latex_rule1808, latex_rule1809, latex_rule1810, latex_rule1811, latex_rule1812, latex_rule1813, latex_rule1814, latex_rule1815, latex_rule1816, latex_rule1817, latex_rule1818, latex_rule1819, latex_rule1820, latex_rule1821, latex_rule1822, latex_rule1823, latex_rule1824, latex_rule1825, latex_rule1826, latex_rule1827, latex_rule1828, latex_rule1829, latex_rule1830, latex_rule1831, latex_rule1837,],
    "]": [latex_rule1489,],
    "_": [latex_rule1474,],
    "`": [latex_rule1476, latex_rule1477, latex_rule1480,],
    "d": [latex_rule1488,],
    "s": [latex_rule1487,],
    "t": [latex_rule1484, latex_rule1485, latex_rule1486,],
    "{": [latex_rule1483,],
    "}": [latex_rule1482,],
    "~": [latex_rule1481,],
}

# Rules for latex_tabbingmode ruleset.

def latex_rule1838(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="__TabbingMode__")

def latex_rule1839(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def latex_rule1840(colorer, s, i):
    return colorer.match_span(s, i, kind="literal4", begin="``", end="''")

def latex_rule1841(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="`", end="'")

def latex_rule1842(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def latex_rule1843(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="\"")

def latex_rule1844(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="invalid", seq="`")

def latex_rule1845(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def latex_rule1846(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="}")

def latex_rule1847(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="{")

def latex_rule1848(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="totalnumber")

def latex_rule1849(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="topnumber")

def latex_rule1850(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="tocdepth")

def latex_rule1851(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="secnumdepth")

def latex_rule1852(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="dbltopnumber")

def latex_rule1853(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="]")

def latex_rule1854(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\~{")

def latex_rule1855(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\~")

def latex_rule1856(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\}")

def latex_rule1857(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\|")

def latex_rule1858(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\{")

def latex_rule1859(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\width")

def latex_rule1860(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\whiledo{")

def latex_rule1861(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\v{")

def latex_rule1862(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vspace{")

def latex_rule1863(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\vspace*{")

def latex_rule1864(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vfill")

def latex_rule1865(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\verb*")

def latex_rule1866(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\verb")

def latex_rule1867(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\value{")

def latex_rule1868(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\v")

def latex_rule1869(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\u{")

def latex_rule1870(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usepackage{")

def latex_rule1871(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usepackage[")

def latex_rule1872(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usecounter{")

def latex_rule1873(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\usebox{")

def latex_rule1874(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\upshape")

def latex_rule1875(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\unboldmath{")

def latex_rule1876(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\u")

def latex_rule1877(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\t{")

def latex_rule1878(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typeout{")

def latex_rule1879(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typein{")

def latex_rule1880(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\typein[")

def latex_rule1881(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\twocolumn[")

def latex_rule1882(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\twocolumn")

def latex_rule1883(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ttfamily")

def latex_rule1884(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\totalheight")

def latex_rule1885(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\topsep")

def latex_rule1886(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\topfraction")

def latex_rule1887(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\today")

def latex_rule1888(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\title{")

def latex_rule1889(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tiny")

def latex_rule1890(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\thispagestyle{")

def latex_rule1891(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thinlines")

def latex_rule1892(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thicklines")

def latex_rule1893(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\thanks{")

def latex_rule1894(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textwidth")

def latex_rule1895(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textup{")

def latex_rule1896(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\texttt{")

def latex_rule1897(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsl{")

def latex_rule1898(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsf{")

def latex_rule1899(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textsc{")

def latex_rule1900(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textrm{")

def latex_rule1901(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textnormal{")

def latex_rule1902(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textmd{")

def latex_rule1903(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textit{")

def latex_rule1904(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textfraction")

def latex_rule1905(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\textfloatsep")

def latex_rule1906(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textcolor{")

def latex_rule1907(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\textbf{")

def latex_rule1908(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\tableofcontents")

def latex_rule1909(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\tabcolsep")

def latex_rule1910(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\tabbingsep")

def latex_rule1911(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\t")

def latex_rule1912(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\symbol{")

def latex_rule1913(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\suppressfloats[")

def latex_rule1914(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\suppressfloats")

def latex_rule1915(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection{")

def latex_rule1916(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection[")

def latex_rule1917(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsubsection*{")

def latex_rule1918(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection{")

def latex_rule1919(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection[")

def latex_rule1920(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subsection*{")

def latex_rule1921(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph{")

def latex_rule1922(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph[")

def latex_rule1923(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\subparagraph*{")

def latex_rule1924(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stretch{")

def latex_rule1925(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\stepcounter{")

def latex_rule1926(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\smallskip")

def latex_rule1927(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\small")

def latex_rule1928(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\slshape")

def latex_rule1929(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sloppy")

def latex_rule1930(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\sffamily")

def latex_rule1931(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settowidth{")

def latex_rule1932(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settoheight{")

def latex_rule1933(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\settodepth{")

def latex_rule1934(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\setlength{")

def latex_rule1935(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\setcounter{")

def latex_rule1936(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section{")

def latex_rule1937(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section[")

def latex_rule1938(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\section*{")

def latex_rule1939(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scshape")

def latex_rule1940(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\scriptsize")

def latex_rule1941(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\scalebox{")

def latex_rule1942(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\sbox{")

def latex_rule1943(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\savebox{")

def latex_rule1944(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rule{")

def latex_rule1945(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rule[")

def latex_rule1946(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rp,am{")

def latex_rule1947(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\rotatebox{")

def latex_rule1948(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\rmfamily")

def latex_rule1949(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\rightmargin")

def latex_rule1950(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\reversemarginpar")

def latex_rule1951(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\resizebox{")

def latex_rule1952(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\resizebox*{")

def latex_rule1953(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\renewenvironment{")

def latex_rule1954(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\renewcommand{")

def latex_rule1955(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ref{")

def latex_rule1956(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\refstepcounter")

def latex_rule1957(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\raisebox{")

def latex_rule1958(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\raggedright")

def latex_rule1959(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\raggedleft")

def latex_rule1960(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\qbeziermax")

def latex_rule1961(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pushtabs")

def latex_rule1962(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\providecommand{")

def latex_rule1963(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\protect")

def latex_rule1964(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\printindex")

def latex_rule1965(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pounds")

def latex_rule1966(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\poptabs")

def latex_rule1967(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part{")

def latex_rule1968(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\partopsep")

def latex_rule1969(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part[")

def latex_rule1970(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\part*{")

def latex_rule1971(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parskip")

def latex_rule1972(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parsep")

def latex_rule1973(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\parindent")

def latex_rule1974(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\parbox{")

def latex_rule1975(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\parbox[")

def latex_rule1976(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph{")

def latex_rule1977(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph[")

def latex_rule1978(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\paragraph*{")

def latex_rule1979(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\par")

def latex_rule1980(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagestyle{")

def latex_rule1981(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pageref{")

def latex_rule1982(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagenumbering{")

def latex_rule1983(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagecolor{")

def latex_rule1984(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\pagebreak[")

def latex_rule1985(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\pagebreak")

def latex_rule1986(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\onecolumn")

def latex_rule1987(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalsize")

def latex_rule1988(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalmarginpar")

def latex_rule1989(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\normalfont")

def latex_rule1990(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nopagebreak[")

def latex_rule1991(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nopagebreak")

def latex_rule1992(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nonfrenchspacing")

def latex_rule1993(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nolinebreak[")

def latex_rule1994(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\nolinebreak")

def latex_rule1995(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\noindent")

def latex_rule1996(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\nocite{")

def latex_rule1997(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newtheorem{")

def latex_rule1998(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newsavebox{")

def latex_rule1999(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\newpage")

def latex_rule2000(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newlength{")

def latex_rule2001(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newenvironment{")

def latex_rule2002(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newcounter{")

def latex_rule2003(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\newcommand{")

def latex_rule2004(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\medskip")

def latex_rule2005(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\mdseries")

def latex_rule2006(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mbox{")

def latex_rule2007(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\mbox{")

def latex_rule2008(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\mathindent")

def latex_rule2009(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\mathindent")

def latex_rule2010(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\markright{")

def latex_rule2011(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\markboth{")

def latex_rule2012(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\marginpar{")

def latex_rule2013(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparwidth")

def latex_rule2014(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparsep")

def latex_rule2015(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\marginparpush")

def latex_rule2016(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\marginpar[")

def latex_rule2017(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\maketitle")

def latex_rule2018(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\makelabel")

def latex_rule2019(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\makeindex")

def latex_rule2020(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\makeglossary")

def latex_rule2021(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\makebox{")

def latex_rule2022(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\makebox[")

def latex_rule2023(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\listparindent")

def latex_rule2024(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listoftables")

def latex_rule2025(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listoffigures")

def latex_rule2026(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\listfiles")

def latex_rule2027(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\linewidth")

def latex_rule2028(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\linethickness{")

def latex_rule2029(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\linebreak[")

def latex_rule2030(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\linebreak")

def latex_rule2031(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\lengthtest{")

def latex_rule2032(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginvi")

def latex_rule2033(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginv")

def latex_rule2034(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginiv")

def latex_rule2035(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginiii")

def latex_rule2036(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmarginii")

def latex_rule2037(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmargini")

def latex_rule2038(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\leftmargin")

def latex_rule2039(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\large")

def latex_rule2040(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\label{")

def latex_rule2041(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\labelwidth")

def latex_rule2042(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\labelsep")

def latex_rule2043(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\kill")

def latex_rule2044(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\jot")

def latex_rule2045(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\itshape")

def latex_rule2046(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\itemsep")

def latex_rule2047(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\itemindent")

def latex_rule2048(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\item[")

def latex_rule2049(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\item")

def latex_rule2050(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\isodd{")

def latex_rule2051(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\intextsep")

def latex_rule2052(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\input{")

def latex_rule2053(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\index{")

def latex_rule2054(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\indent")

def latex_rule2055(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\include{")

def latex_rule2056(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includeonly{")

def latex_rule2057(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics{")

def latex_rule2058(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics[")

def latex_rule2059(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics*{")

def latex_rule2060(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\includegraphics*[")

def latex_rule2061(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ifthenelse{")

def latex_rule2062(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hyphenation{")

def latex_rule2063(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\huge")

def latex_rule2064(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hspace{")

def latex_rule2065(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\hspace*{")

def latex_rule2066(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\hfill")

def latex_rule2067(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\height")

def latex_rule2068(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\glossary{")

def latex_rule2069(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fussy")

def latex_rule2070(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\frenchspacing")

def latex_rule2071(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\framebox{")

def latex_rule2072(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\framebox[")

def latex_rule2073(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fragile")

def latex_rule2074(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnote{")

def latex_rule2075(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotetext{")

def latex_rule2076(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotetext[")

def latex_rule2077(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\footnotesize")

def latex_rule2078(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\footnotesep")

def latex_rule2079(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\footnoterule")

def latex_rule2080(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnotemark[")

def latex_rule2081(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\footnotemark")

def latex_rule2082(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\footnote[")

def latex_rule2083(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fnsymbol{")

def latex_rule2084(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\floatsep")

def latex_rule2085(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\floatpagefraction")

def latex_rule2086(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\fill")

def latex_rule2087(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fcolorbox{")

def latex_rule2088(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\fbox{")

def latex_rule2089(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\fboxsep")

def latex_rule2090(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\fboxrule")

def latex_rule2091(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\equal{")

def latex_rule2092(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\ensuremath{")

def latex_rule2093(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\enlargethispage{")

def latex_rule2094(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\enlargethispage*{")

def latex_rule2095(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\end{")

def latex_rule2096(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\emph{")

def latex_rule2097(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\d{")

def latex_rule2098(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\doublerulesep")

def latex_rule2099(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\documentclass{")

def latex_rule2100(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\documentclass[")

def latex_rule2101(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\depth")

def latex_rule2102(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\definecolor{")

def latex_rule2103(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\ddag")

def latex_rule2104(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dbltopfraction")

def latex_rule2105(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dbltextfloatsep")

def latex_rule2106(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dblfloatsep")

def latex_rule2107(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\dblfloatpagefraction")

def latex_rule2108(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\date{")

def latex_rule2109(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\dag")

def latex_rule2110(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\d")

def latex_rule2111(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\c{")

def latex_rule2112(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\copyright")

def latex_rule2113(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnwidth")

def latex_rule2114(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnseprule")

def latex_rule2115(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\columnsep")

def latex_rule2116(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\color{")

def latex_rule2117(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\colorbox{")

def latex_rule2118(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\clearpage")

def latex_rule2119(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\cleardoublepage")

def latex_rule2120(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cite{")

def latex_rule2121(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\cite[")

def latex_rule2122(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter{")

def latex_rule2123(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter[")

def latex_rule2124(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\chapter*{")

def latex_rule2125(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\centering")

def latex_rule2126(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\caption{")

def latex_rule2127(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\caption[")

def latex_rule2128(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\c")

def latex_rule2129(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\b{")

def latex_rule2130(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bottomnumber")

def latex_rule2131(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bottomfraction")

def latex_rule2132(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boolean{")

def latex_rule2133(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\boldmath{")

def latex_rule2134(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bigskip")

def latex_rule2135(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bibliography{")

def latex_rule2136(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\bibliographystyle{")

def latex_rule2137(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\bibindent")

def latex_rule2138(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\bfseries")

def latex_rule2139(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\belowdisplayskip")

def latex_rule2140(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\belowdisplayshortskip")

def latex_rule2141(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\begin{")

def latex_rule2142(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\baselinestretch")

def latex_rule2143(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\baselineskip")

def latex_rule2144(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\b")

def latex_rule2145(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\author{")

def latex_rule2146(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arraystgretch")

def latex_rule2147(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arrayrulewidth")

def latex_rule2148(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\arraycolsep")

def latex_rule2149(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\arabic{")

def latex_rule2150(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\appendix")

def latex_rule2151(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\alph{")

def latex_rule2152(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addvspace{")

def latex_rule2153(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtolength{")

def latex_rule2154(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtocounter{")

def latex_rule2155(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addtocontents{")

def latex_rule2156(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\addcontentsline{")

def latex_rule2157(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\abovedisplayskip")

def latex_rule2158(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="\\abovedisplayshortskip")

def latex_rule2159(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\a`")

def latex_rule2160(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\a=")

def latex_rule2161(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\a'")

def latex_rule2162(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\`{")

def latex_rule2163(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\`")

def latex_rule2164(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\`")

def latex_rule2165(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\_")

def latex_rule2166(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\^{")

def latex_rule2167(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\^")

def latex_rule2168(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\\[")

def latex_rule2169(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\\*[")

def latex_rule2170(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\*")

def latex_rule2171(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\")

def latex_rule2172(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\")

def latex_rule2173(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\TeX")

def latex_rule2174(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\S")

def latex_rule2175(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Roman{")

def latex_rule2176(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\P")

def latex_rule2177(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Large")

def latex_rule2178(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\LaTeX")

def latex_rule2179(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\LARGE")

def latex_rule2180(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\H{")

def latex_rule2181(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\Huge")

def latex_rule2182(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\H")

def latex_rule2183(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\Alph{")

def latex_rule2184(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\@")

def latex_rule2185(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\={")

def latex_rule2186(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\=")

def latex_rule2187(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\=")

def latex_rule2188(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\.{")

def latex_rule2189(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\.")

def latex_rule2190(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\-")

def latex_rule2191(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\-")

def latex_rule2192(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\,")

def latex_rule2193(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\+")

def latex_rule2194(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\'{")

def latex_rule2195(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\'")

def latex_rule2196(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\'")

def latex_rule2197(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\<")

def latex_rule2198(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\>")

def latex_rule2199(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\&")

def latex_rule2200(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\%")

def latex_rule2201(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\$")

def latex_rule2202(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\#")

def latex_rule2203(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\\"{")

def latex_rule2204(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\"")

def latex_rule2205(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def latex_rule2206(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="[")

def latex_rule2207(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="---")

def latex_rule2208(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="--")

def latex_rule2209(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def latex_rule2210(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="\\")

# Rules dict for latex_tabbingmode ruleset.
rulesDict5 = {
    "\"": [latex_rule1842, latex_rule1843,],
    "%": [latex_rule1839,],
    "-": [latex_rule2207, latex_rule2208, latex_rule2209,],
    "[": [latex_rule2206,],
    "\\": [latex_rule1854, latex_rule1855, latex_rule1856, latex_rule1857, latex_rule1858, latex_rule1859, latex_rule1860, latex_rule1861, latex_rule1862, latex_rule1863, latex_rule1864, latex_rule1865, latex_rule1866, latex_rule1867, latex_rule1868, latex_rule1869, latex_rule1870, latex_rule1871, latex_rule1872, latex_rule1873, latex_rule1874, latex_rule1875, latex_rule1876, latex_rule1877, latex_rule1878, latex_rule1879, latex_rule1880, latex_rule1881, latex_rule1882, latex_rule1883, latex_rule1884, latex_rule1885, latex_rule1886, latex_rule1887, latex_rule1888, latex_rule1889, latex_rule1890, latex_rule1891, latex_rule1892, latex_rule1893, latex_rule1894, latex_rule1895, latex_rule1896, latex_rule1897, latex_rule1898, latex_rule1899, latex_rule1900, latex_rule1901, latex_rule1902, latex_rule1903, latex_rule1904, latex_rule1905, latex_rule1906, latex_rule1907, latex_rule1908, latex_rule1909, latex_rule1910, latex_rule1911, latex_rule1912, latex_rule1913, latex_rule1914, latex_rule1915, latex_rule1916, latex_rule1917, latex_rule1918, latex_rule1919, latex_rule1920, latex_rule1921, latex_rule1922, latex_rule1923, latex_rule1924, latex_rule1925, latex_rule1926, latex_rule1927, latex_rule1928, latex_rule1929, latex_rule1930, latex_rule1931, latex_rule1932, latex_rule1933, latex_rule1934, latex_rule1935, latex_rule1936, latex_rule1937, latex_rule1938, latex_rule1939, latex_rule1940, latex_rule1941, latex_rule1942, latex_rule1943, latex_rule1944, latex_rule1945, latex_rule1946, latex_rule1947, latex_rule1948, latex_rule1949, latex_rule1950, latex_rule1951, latex_rule1952, latex_rule1953, latex_rule1954, latex_rule1955, latex_rule1956, latex_rule1957, latex_rule1958, latex_rule1959, latex_rule1960, latex_rule1961, latex_rule1962, latex_rule1963, latex_rule1964, latex_rule1965, latex_rule1966, latex_rule1967, latex_rule1968, latex_rule1969, latex_rule1970, latex_rule1971, latex_rule1972, latex_rule1973, latex_rule1974, latex_rule1975, latex_rule1976, latex_rule1977, latex_rule1978, latex_rule1979, latex_rule1980, latex_rule1981, latex_rule1982, latex_rule1983, latex_rule1984, latex_rule1985, latex_rule1986, latex_rule1987, latex_rule1988, latex_rule1989, latex_rule1990, latex_rule1991, latex_rule1992, latex_rule1993, latex_rule1994, latex_rule1995, latex_rule1996, latex_rule1997, latex_rule1998, latex_rule1999, latex_rule2000, latex_rule2001, latex_rule2002, latex_rule2003, latex_rule2004, latex_rule2005, latex_rule2006, latex_rule2007, latex_rule2008, latex_rule2009, latex_rule2010, latex_rule2011, latex_rule2012, latex_rule2013, latex_rule2014, latex_rule2015, latex_rule2016, latex_rule2017, latex_rule2018, latex_rule2019, latex_rule2020, latex_rule2021, latex_rule2022, latex_rule2023, latex_rule2024, latex_rule2025, latex_rule2026, latex_rule2027, latex_rule2028, latex_rule2029, latex_rule2030, latex_rule2031, latex_rule2032, latex_rule2033, latex_rule2034, latex_rule2035, latex_rule2036, latex_rule2037, latex_rule2038, latex_rule2039, latex_rule2040, latex_rule2041, latex_rule2042, latex_rule2043, latex_rule2044, latex_rule2045, latex_rule2046, latex_rule2047, latex_rule2048, latex_rule2049, latex_rule2050, latex_rule2051, latex_rule2052, latex_rule2053, latex_rule2054, latex_rule2055, latex_rule2056, latex_rule2057, latex_rule2058, latex_rule2059, latex_rule2060, latex_rule2061, latex_rule2062, latex_rule2063, latex_rule2064, latex_rule2065, latex_rule2066, latex_rule2067, latex_rule2068, latex_rule2069, latex_rule2070, latex_rule2071, latex_rule2072, latex_rule2073, latex_rule2074, latex_rule2075, latex_rule2076, latex_rule2077, latex_rule2078, latex_rule2079, latex_rule2080, latex_rule2081, latex_rule2082, latex_rule2083, latex_rule2084, latex_rule2085, latex_rule2086, latex_rule2087, latex_rule2088, latex_rule2089, latex_rule2090, latex_rule2091, latex_rule2092, latex_rule2093, latex_rule2094, latex_rule2095, latex_rule2096, latex_rule2097, latex_rule2098, latex_rule2099, latex_rule2100, latex_rule2101, latex_rule2102, latex_rule2103, latex_rule2104, latex_rule2105, latex_rule2106, latex_rule2107, latex_rule2108, latex_rule2109, latex_rule2110, latex_rule2111, latex_rule2112, latex_rule2113, latex_rule2114, latex_rule2115, latex_rule2116, latex_rule2117, latex_rule2118, latex_rule2119, latex_rule2120, latex_rule2121, latex_rule2122, latex_rule2123, latex_rule2124, latex_rule2125, latex_rule2126, latex_rule2127, latex_rule2128, latex_rule2129, latex_rule2130, latex_rule2131, latex_rule2132, latex_rule2133, latex_rule2134, latex_rule2135, latex_rule2136, latex_rule2137, latex_rule2138, latex_rule2139, latex_rule2140, latex_rule2141, latex_rule2142, latex_rule2143, latex_rule2144, latex_rule2145, latex_rule2146, latex_rule2147, latex_rule2148, latex_rule2149, latex_rule2150, latex_rule2151, latex_rule2152, latex_rule2153, latex_rule2154, latex_rule2155, latex_rule2156, latex_rule2157, latex_rule2158, latex_rule2159, latex_rule2160, latex_rule2161, latex_rule2162, latex_rule2163, latex_rule2164, latex_rule2165, latex_rule2166, latex_rule2167, latex_rule2168, latex_rule2169, latex_rule2170, latex_rule2171, latex_rule2172, latex_rule2173, latex_rule2174, latex_rule2175, latex_rule2176, latex_rule2177, latex_rule2178, latex_rule2179, latex_rule2180, latex_rule2181, latex_rule2182, latex_rule2183, latex_rule2184, latex_rule2185, latex_rule2186, latex_rule2187, latex_rule2188, latex_rule2189, latex_rule2190, latex_rule2191, latex_rule2192, latex_rule2193, latex_rule2194, latex_rule2195, latex_rule2196, latex_rule2197, latex_rule2198, latex_rule2199, latex_rule2200, latex_rule2201, latex_rule2202, latex_rule2203, latex_rule2204, latex_rule2205, latex_rule2210,],
    "]": [latex_rule1853,],
    "_": [latex_rule1838,],
    "`": [latex_rule1840, latex_rule1841, latex_rule1844,],
    "d": [latex_rule1852,],
    "s": [latex_rule1851,],
    "t": [latex_rule1848, latex_rule1849, latex_rule1850,],
    "{": [latex_rule1847,],
    "}": [latex_rule1846,],
    "~": [latex_rule1845,],
}

# Rules for latex_picturemode ruleset.

def latex_rule2211(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="__PictureMode__")

def latex_rule2212(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def latex_rule2213(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\vector(")

def latex_rule2214(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thinlines")

def latex_rule2215(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\thicklines")

def latex_rule2216(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\shortstack{")

def latex_rule2217(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\shortstack[")

def latex_rule2218(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\savebox{")

def latex_rule2219(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\qbezier[")

def latex_rule2220(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\qbezier(")

def latex_rule2221(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\put(")

def latex_rule2222(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\oval[")

def latex_rule2223(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\oval(")

def latex_rule2224(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\multiput(")

def latex_rule2225(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\makebox(")

def latex_rule2226(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\linethickness{")

def latex_rule2227(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\line(")

def latex_rule2228(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\graphpaper[")

def latex_rule2229(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\graphpaper(")

def latex_rule2230(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\frame{")

def latex_rule2231(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="\\framebox(")

def latex_rule2232(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\dashbox{")

def latex_rule2233(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\circle{")

def latex_rule2234(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq="\\circle*{")

def latex_rule2235(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="\\")

# Rules dict for latex_picturemode ruleset.
rulesDict6 = {
    "%": [latex_rule2212,],
    "\\": [latex_rule2213, latex_rule2214, latex_rule2215, latex_rule2216, latex_rule2217, latex_rule2218, latex_rule2219, latex_rule2220, latex_rule2221, latex_rule2222, latex_rule2223, latex_rule2224, latex_rule2225, latex_rule2226, latex_rule2227, latex_rule2228, latex_rule2229, latex_rule2230, latex_rule2231, latex_rule2232, latex_rule2233, latex_rule2234, latex_rule2235,],
    "_": [latex_rule2211,],
}

# x.rulesDictDict for latex mode.
rulesDictDict = {
    "latex_arraymode": rulesDict3,
    "latex_main": rulesDict1,
    "latex_mathmode": rulesDict2,
    "latex_picturemode": rulesDict6,
    "latex_tabbingmode": rulesDict5,
    "latex_tabularmode": rulesDict4,
}

# Import dict for latex mode.
importDict = {}

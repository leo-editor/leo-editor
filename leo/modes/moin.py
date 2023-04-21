# Leo colorizer control file for moin mode.
# This file is in the public domain.

# Properties for moin mode.
properties = {
    "lineComment": "##",
    "wrap": "soft",
}

# Attributes dict for moin_main ruleset.
moin_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for moin mode.
attributesDictDict = {
    "moin_main": moin_main_attributes_dict,
}

# Keywords dict for moin_main ruleset.
moin_main_keywords_dict = {}

# Dictionary of keywords dictionaries for moin mode.
keywordsDictDict = {
    "moin_main": moin_main_keywords_dict,
}

# Rules for moin_main ruleset.

def moin_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="##")

def moin_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#pragma")

def moin_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword4", begin="[[", end="]]")

def moin_rule3(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="\\s+\\w[[:alnum:][:blank:]]+::",
          at_line_start=True)

def moin_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="{{{", end="}}}")

def moin_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="`", end="`")

def moin_rule6(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal1", regexp="('{2,5})[^']+\\1[^']")

def moin_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal4", regexp="-{4,}")

def moin_rule8(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword1", begin="(={1,5})", end="$1",
          at_line_start=True)

def moin_rule9(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="A[a-z]+[A-Z][a-zA-Z]+")

def moin_rule10(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="B[a-z]+[A-Z][a-zA-Z]+")

def moin_rule11(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="C[a-z]+[A-Z][a-zA-Z]+")

def moin_rule12(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="D[a-z]+[A-Z][a-zA-Z]+")

def moin_rule13(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="E[a-z]+[A-Z][a-zA-Z]+")

def moin_rule14(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="F[a-z]+[A-Z][a-zA-Z]+")

def moin_rule15(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="G[a-z]+[A-Z][a-zA-Z]+")

def moin_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="H[a-z]+[A-Z][a-zA-Z]+")

def moin_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="I[a-z]+[A-Z][a-zA-Z]+")

def moin_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="J[a-z]+[A-Z][a-zA-Z]+")

def moin_rule19(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="K[a-z]+[A-Z][a-zA-Z]+")

def moin_rule20(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="L[a-z]+[A-Z][a-zA-Z]+")

def moin_rule21(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="M[a-z]+[A-Z][a-zA-Z]+")

def moin_rule22(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="N[a-z]+[A-Z][a-zA-Z]+")

def moin_rule23(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="O[a-z]+[A-Z][a-zA-Z]+")

def moin_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="P[a-z]+[A-Z][a-zA-Z]+")

def moin_rule25(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="Q[a-z]+[A-Z][a-zA-Z]+")

def moin_rule26(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="R[a-z]+[A-Z][a-zA-Z]+")

def moin_rule27(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="S[a-z]+[A-Z][a-zA-Z]+")

def moin_rule28(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="T[a-z]+[A-Z][a-zA-Z]+")

def moin_rule29(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="U[a-z]+[A-Z][a-zA-Z]+")

def moin_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="V[a-z]+[A-Z][a-zA-Z]+")

def moin_rule31(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="W[a-z]+[A-Z][a-zA-Z]+")

def moin_rule32(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="X[a-z]+[A-Z][a-zA-Z]+")

def moin_rule33(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="Y[a-z]+[A-Z][a-zA-Z]+")

def moin_rule34(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="Z[a-z]+[A-Z][a-zA-Z]+")

def moin_rule35(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="[\"", end="\"]")

def moin_rule36(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="[", end="]")

# Rules dict for moin_main ruleset.
rulesDict1 = {
    " ": [moin_rule3,],
    "#": [moin_rule0, moin_rule1,],
    "'": [moin_rule6,],
    "-": [moin_rule7,],
    "=": [moin_rule8,],
    "A": [moin_rule9,],
    "B": [moin_rule10,],
    "C": [moin_rule11,],
    "D": [moin_rule12,],
    "E": [moin_rule13,],
    "F": [moin_rule14,],
    "G": [moin_rule15,],
    "H": [moin_rule16,],
    "I": [moin_rule17,],
    "J": [moin_rule18,],
    "K": [moin_rule19,],
    "L": [moin_rule20,],
    "M": [moin_rule21,],
    "N": [moin_rule22,],
    "O": [moin_rule23,],
    "P": [moin_rule24,],
    "Q": [moin_rule25,],
    "R": [moin_rule26,],
    "S": [moin_rule27,],
    "T": [moin_rule28,],
    "U": [moin_rule29,],
    "V": [moin_rule30,],
    "W": [moin_rule31,],
    "X": [moin_rule32,],
    "Y": [moin_rule33,],
    "Z": [moin_rule34,],
    "[": [moin_rule2, moin_rule35, moin_rule36,],
    "`": [moin_rule5,],
    "{": [moin_rule4,],
}

# x.rulesDictDict for moin mode.
rulesDictDict = {
    "moin_main": rulesDict1,
}

# Import dict for moin mode.
importDict = {}

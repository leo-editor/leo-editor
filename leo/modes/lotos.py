# Leo colorizer control file for lotos mode.
# This file is in the public domain.

# Properties for lotos mode.
properties = {
    "commentEnd": "*)",
    "commentStart": "(*",
    "indentNextLines": "\\s*(let|library|process|specification|type|>>).*|\\s*(\\(|\\[\\]|\\[>|\\|\\||\\|\\|\\||\\|\\[.*\\]\\||\\[.*\\]\\s*->)\\s*",
}

# Attributes dict for lotos_main ruleset.
lotos_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for lotos mode.
attributesDictDict = {
    "lotos_main": lotos_main_attributes_dict,
}

# Keywords dict for lotos_main ruleset.
lotos_main_keywords_dict = {
    "accept": "keyword1",
    "actualizedby": "keyword1",
    "any": "keyword1",
    "basicnaturalnumber": "keyword2",
    "basicnonemptystring": "keyword2",
    "behavior": "keyword1",
    "behaviour": "keyword1",
    "bit": "keyword2",
    "bitnatrepr": "keyword2",
    "bitstring": "keyword2",
    "bool": "keyword2",
    "boolean": "keyword2",
    "choice": "keyword1",
    "decdigit": "keyword2",
    "decnatrepr": "keyword2",
    "decstring": "keyword2",
    "element": "keyword2",
    "endlib": "keyword1",
    "endproc": "keyword1",
    "endspec": "keyword1",
    "endtype": "keyword1",
    "eqns": "keyword1",
    "exit": "keyword1",
    "false": "literal1",
    "fbool": "keyword2",
    "fboolean": "keyword2",
    "for": "keyword1",
    "forall": "keyword1",
    "formaleqns": "keyword1",
    "formalopns": "keyword1",
    "formalsorts": "keyword1",
    "hexdigit": "keyword2",
    "hexnatrepr": "keyword2",
    "hexstring": "keyword2",
    "hide": "keyword1",
    "i": "keyword1",
    "in": "keyword1",
    "is": "keyword1",
    "let": "keyword1",
    "library": "keyword1",
    "nat": "keyword2",
    "natrepresentations": "keyword2",
    "naturalnumber": "keyword2",
    "noexit": "keyword1",
    "nonemptystring": "keyword2",
    "octdigit": "keyword2",
    "octet": "keyword2",
    "octetstring": "keyword2",
    "octnatrepr": "keyword2",
    "octstring": "keyword2",
    "of": "keyword1",
    "ofsort": "keyword1",
    "opnnames": "keyword1",
    "opns": "keyword1",
    "par": "keyword1",
    "process": "keyword1",
    "renamedby": "keyword1",
    "richernonemptystring": "keyword2",
    "set": "keyword2",
    "sortnames": "keyword1",
    "sorts": "keyword1",
    "specification": "keyword1",
    "stop": "keyword1",
    "string": "keyword2",
    "string0": "keyword2",
    "string1": "keyword2",
    "true": "literal1",
    "type": "keyword1",
    "using": "keyword1",
    "where": "keyword1",
}

# Dictionary of keywords dictionaries for lotos mode.
keywordsDictDict = {
    "lotos_main": lotos_main_keywords_dict,
}

# Rules for lotos_main ruleset.

def lotos_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="(*", end="*)")

def lotos_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>")

def lotos_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[>")

def lotos_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|||")

def lotos_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="||")

def lotos_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|[")

def lotos_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]|")

def lotos_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[]")

def lotos_rule8(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for lotos_main ruleset.
rulesDict1 = {
    "(": [lotos_rule0,],
    "0": [lotos_rule8,],
    "1": [lotos_rule8,],
    "2": [lotos_rule8,],
    "3": [lotos_rule8,],
    "4": [lotos_rule8,],
    "5": [lotos_rule8,],
    "6": [lotos_rule8,],
    "7": [lotos_rule8,],
    "8": [lotos_rule8,],
    "9": [lotos_rule8,],
    ">": [lotos_rule1,],
    "@": [lotos_rule8,],
    "A": [lotos_rule8,],
    "B": [lotos_rule8,],
    "C": [lotos_rule8,],
    "D": [lotos_rule8,],
    "E": [lotos_rule8,],
    "F": [lotos_rule8,],
    "G": [lotos_rule8,],
    "H": [lotos_rule8,],
    "I": [lotos_rule8,],
    "J": [lotos_rule8,],
    "K": [lotos_rule8,],
    "L": [lotos_rule8,],
    "M": [lotos_rule8,],
    "N": [lotos_rule8,],
    "O": [lotos_rule8,],
    "P": [lotos_rule8,],
    "Q": [lotos_rule8,],
    "R": [lotos_rule8,],
    "S": [lotos_rule8,],
    "T": [lotos_rule8,],
    "U": [lotos_rule8,],
    "V": [lotos_rule8,],
    "W": [lotos_rule8,],
    "X": [lotos_rule8,],
    "Y": [lotos_rule8,],
    "Z": [lotos_rule8,],
    "[": [lotos_rule2, lotos_rule7,],
    "]": [lotos_rule6,],
    "a": [lotos_rule8,],
    "b": [lotos_rule8,],
    "c": [lotos_rule8,],
    "d": [lotos_rule8,],
    "e": [lotos_rule8,],
    "f": [lotos_rule8,],
    "g": [lotos_rule8,],
    "h": [lotos_rule8,],
    "i": [lotos_rule8,],
    "j": [lotos_rule8,],
    "k": [lotos_rule8,],
    "l": [lotos_rule8,],
    "m": [lotos_rule8,],
    "n": [lotos_rule8,],
    "o": [lotos_rule8,],
    "p": [lotos_rule8,],
    "q": [lotos_rule8,],
    "r": [lotos_rule8,],
    "s": [lotos_rule8,],
    "t": [lotos_rule8,],
    "u": [lotos_rule8,],
    "v": [lotos_rule8,],
    "w": [lotos_rule8,],
    "x": [lotos_rule8,],
    "y": [lotos_rule8,],
    "z": [lotos_rule8,],
    "|": [lotos_rule3, lotos_rule4, lotos_rule5,],
}

# x.rulesDictDict for lotos mode.
rulesDictDict = {
    "lotos_main": rulesDict1,
}

# Import dict for lotos mode.
importDict = {}

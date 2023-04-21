# Leo colorizer control file for sdl_pr mode.
# This file is in the public domain.

# Properties for sdl_pr mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentNextLines": "\\s*(block|channel|connection|decision|generator|input|macro|newtype|operator|package|procedure|process|refinement|service|start|state|substructure|syntype|system).*|\\s*(signal)\\s*",
}

# Attributes dict for sdl_pr_main ruleset.
sdl_pr_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for sdl_pr mode.
attributesDictDict = {
    "sdl_pr_main": sdl_pr_main_attributes_dict,
}

# Keywords dict for sdl_pr_main ruleset.
sdl_pr_main_keywords_dict = {
    "active": "keyword1",
    "adding": "keyword1",
    "all": "keyword1",
    "alternative": "keyword1",
    "any": "keyword1",
    "array": "keyword3",
    "as": "keyword1",
    "atleast": "keyword1",
    "axioms": "keyword1",
    "block": "keyword1",
    "boolean": "keyword2",
    "call": "keyword1",
    "channel": "keyword1",
    "character": "keyword2",
    "charstring": "keyword2",
    "comment": "keyword1",
    "connect": "keyword1",
    "connection": "keyword1",
    "constant": "keyword1",
    "constants": "keyword1",
    "create": "keyword1",
    "dcl": "keyword1",
    "decision": "keyword1",
    "default": "keyword1",
    "duration": "keyword2",
    "else": "keyword1",
    "end": "keyword1",
    "endalternative": "keyword1",
    "endblock": "keyword1",
    "endchannel": "keyword1",
    "endconnection": "keyword1",
    "enddecision": "keyword1",
    "endgenerator": "keyword1",
    "endmacro": "keyword1",
    "endnewtype": "keyword1",
    "endoperator": "keyword1",
    "endpackage": "keyword1",
    "endprocedure": "keyword1",
    "endprocess": "keyword1",
    "endrefinement": "keyword1",
    "endselect": "keyword1",
    "endservice": "keyword1",
    "endstate": "keyword1",
    "endsubstructure": "keyword1",
    "endsyntype": "keyword1",
    "endsystem": "keyword1",
    "env": "keyword1",
    "error": "keyword1",
    "export": "keyword1",
    "exported": "keyword1",
    "external": "keyword1",
    "false": "literal1",
    "fi": "keyword1",
    "finalized": "keyword1",
    "for": "keyword1",
    "fpar": "keyword1",
    "from": "keyword1",
    "gate": "keyword1",
    "generator": "keyword1",
    "if": "keyword1",
    "import": "keyword1",
    "imported": "keyword1",
    "in": "keyword1",
    "inherits": "keyword1",
    "input": "keyword1",
    "integer": "keyword2",
    "interface": "keyword1",
    "join": "keyword1",
    "literal": "keyword1",
    "literals": "keyword1",
    "macro": "keyword1",
    "macrodefinition": "keyword1",
    "macroid": "keyword1",
    "map": "keyword1",
    "nameclass": "keyword1",
    "natural": "keyword2",
    "newtype": "keyword1",
    "nextstate": "keyword1",
    "nodelay": "keyword1",
    "noequality": "keyword1",
    "none": "keyword1",
    "now": "keyword1",
    "null": "literal1",
    "offspring": "keyword1",
    "operator": "keyword1",
    "operators": "keyword1",
    "ordering": "keyword1",
    "out": "keyword1",
    "output": "keyword1",
    "package": "keyword1",
    "parent": "keyword1",
    "pid": "keyword2",
    "powerset": "keyword3",
    "priority": "keyword1",
    "procedure": "keyword1",
    "process": "keyword1",
    "provided": "keyword1",
    "real": "keyword2",
    "redefined": "keyword1",
    "referenced": "keyword1",
    "refinement": "keyword1",
    "remote": "keyword1",
    "reset": "keyword1",
    "return": "keyword1",
    "returns": "keyword1",
    "revealed": "keyword1",
    "reverse": "keyword1",
    "route": "keyword1",
    "save": "keyword1",
    "select": "keyword1",
    "self": "keyword1",
    "sender": "keyword1",
    "service": "keyword1",
    "set": "keyword1",
    "signal": "keyword1",
    "signallist": "keyword1",
    "signalroute": "keyword1",
    "signalset": "keyword1",
    "spelling": "keyword1",
    "start": "keyword1",
    "state": "keyword1",
    "stop": "keyword1",
    "string": "keyword3",
    "struct": "keyword1",
    "substructure": "keyword1",
    "synonym": "keyword1",
    "syntype": "keyword1",
    "system": "keyword1",
    "task": "keyword1",
    "then": "keyword1",
    "this": "keyword1",
    "time": "keyword2",
    "timer": "keyword1",
    "to": "keyword1",
    "true": "literal1",
    "type": "keyword1",
    "use": "keyword1",
    "via": "keyword1",
    "view": "keyword1",
    "viewed": "keyword1",
    "virtual": "keyword1",
    "with": "keyword1",
}

# Dictionary of keywords dictionaries for sdl_pr mode.
keywordsDictDict = {
    "sdl_pr_main": sdl_pr_main_keywords_dict,
}

# Rules for sdl_pr_main ruleset.

def sdl_pr_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="/*#SDTREF", end="*/")

def sdl_pr_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def sdl_pr_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'", end="'",
          no_line_break=True)

def sdl_pr_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"", end="\"",
          no_line_break=True)

def sdl_pr_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def sdl_pr_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def sdl_pr_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def sdl_pr_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def sdl_pr_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def sdl_pr_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/=")

def sdl_pr_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def sdl_pr_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def sdl_pr_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def sdl_pr_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def sdl_pr_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def sdl_pr_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def sdl_pr_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def sdl_pr_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def sdl_pr_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="//")

def sdl_pr_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="and")

def sdl_pr_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="mod")

def sdl_pr_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="not")

def sdl_pr_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="or")

def sdl_pr_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="rem")

def sdl_pr_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="xor")

def sdl_pr_rule25(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for sdl_pr_main ruleset.
rulesDict1 = {
    "!": [sdl_pr_rule17,],
    "\"": [sdl_pr_rule3,],
    "'": [sdl_pr_rule2,],
    "*": [sdl_pr_rule6,],
    "+": [sdl_pr_rule4,],
    "-": [sdl_pr_rule5,],
    ".": [sdl_pr_rule16,],
    "/": [sdl_pr_rule0, sdl_pr_rule1, sdl_pr_rule7, sdl_pr_rule9, sdl_pr_rule18,],
    "0": [sdl_pr_rule25,],
    "1": [sdl_pr_rule25,],
    "2": [sdl_pr_rule25,],
    "3": [sdl_pr_rule25,],
    "4": [sdl_pr_rule25,],
    "5": [sdl_pr_rule25,],
    "6": [sdl_pr_rule25,],
    "7": [sdl_pr_rule25,],
    "8": [sdl_pr_rule25,],
    "9": [sdl_pr_rule25,],
    ":": [sdl_pr_rule10,],
    "<": [sdl_pr_rule12, sdl_pr_rule13,],
    "=": [sdl_pr_rule8, sdl_pr_rule11,],
    ">": [sdl_pr_rule14, sdl_pr_rule15,],
    "@": [sdl_pr_rule25,],
    "A": [sdl_pr_rule25,],
    "B": [sdl_pr_rule25,],
    "C": [sdl_pr_rule25,],
    "D": [sdl_pr_rule25,],
    "E": [sdl_pr_rule25,],
    "F": [sdl_pr_rule25,],
    "G": [sdl_pr_rule25,],
    "H": [sdl_pr_rule25,],
    "I": [sdl_pr_rule25,],
    "J": [sdl_pr_rule25,],
    "K": [sdl_pr_rule25,],
    "L": [sdl_pr_rule25,],
    "M": [sdl_pr_rule25,],
    "N": [sdl_pr_rule25,],
    "O": [sdl_pr_rule25,],
    "P": [sdl_pr_rule25,],
    "Q": [sdl_pr_rule25,],
    "R": [sdl_pr_rule25,],
    "S": [sdl_pr_rule25,],
    "T": [sdl_pr_rule25,],
    "U": [sdl_pr_rule25,],
    "V": [sdl_pr_rule25,],
    "W": [sdl_pr_rule25,],
    "X": [sdl_pr_rule25,],
    "Y": [sdl_pr_rule25,],
    "Z": [sdl_pr_rule25,],
    "a": [sdl_pr_rule19, sdl_pr_rule25,],
    "b": [sdl_pr_rule25,],
    "c": [sdl_pr_rule25,],
    "d": [sdl_pr_rule25,],
    "e": [sdl_pr_rule25,],
    "f": [sdl_pr_rule25,],
    "g": [sdl_pr_rule25,],
    "h": [sdl_pr_rule25,],
    "i": [sdl_pr_rule25,],
    "j": [sdl_pr_rule25,],
    "k": [sdl_pr_rule25,],
    "l": [sdl_pr_rule25,],
    "m": [sdl_pr_rule20, sdl_pr_rule25,],
    "n": [sdl_pr_rule21, sdl_pr_rule25,],
    "o": [sdl_pr_rule22, sdl_pr_rule25,],
    "p": [sdl_pr_rule25,],
    "q": [sdl_pr_rule25,],
    "r": [sdl_pr_rule23, sdl_pr_rule25,],
    "s": [sdl_pr_rule25,],
    "t": [sdl_pr_rule25,],
    "u": [sdl_pr_rule25,],
    "v": [sdl_pr_rule25,],
    "w": [sdl_pr_rule25,],
    "x": [sdl_pr_rule24, sdl_pr_rule25,],
    "y": [sdl_pr_rule25,],
    "z": [sdl_pr_rule25,],
}

# x.rulesDictDict for sdl_pr mode.
rulesDictDict = {
    "sdl_pr_main": rulesDict1,
}

# Import dict for sdl_pr mode.
importDict = {}

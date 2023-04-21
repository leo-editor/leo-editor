# Leo colorizer control file for verilog mode.
# This file is in the public domain.

# Properties for verilog mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentNextLines": "(.*:\\s*)|(\\s*(begin|fork|task|table|specify|primitive|module|generate|function|case[xz]?)\\>.*)|(\\s*(always|if|else|for|forever|initial|repeat|while)\\>[^;]*)",
    "lineComment": "//",
    "noWordSep": "_'",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for verilog_main ruleset.
verilog_main_attributes_dict = {
    "default": "null",
    "digit_re": "([[:digit:]]|_)+",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "'",
}

# Dictionary of attributes dictionaries for verilog mode.
attributesDictDict = {
    "verilog_main": verilog_main_attributes_dict,
}

# Keywords dict for verilog_main ruleset.
verilog_main_keywords_dict = {
    "$cleartrace": "function",
    "$finish": "function",
    "$monitoroff": "function",
    "$monitoron": "function",
    "$printtimescale": "function",
    "$random": "function",
    "$realtime": "function",
    "$settrace": "function",
    "$showscopes": "function",
    "$showvars": "function",
    "$stime": "function",
    "$stop": "function",
    "$time": "function",
    "$timeformat": "function",
    "`autoexpand_vectornets": "keyword2",
    "`celldefine": "keyword2",
    "`default_nettype": "keyword2",
    "`define": "keyword2",
    "`else": "keyword2",
    "`endcelldefine": "keyword2",
    "`endif": "keyword2",
    "`endprotect": "keyword2",
    "`endprotected": "keyword2",
    "`expand_vectornets": "keyword2",
    "`ifdef": "keyword2",
    "`ifndef": "keyword2",
    "`include": "keyword2",
    "`noexpand_vectornets": "keyword2",
    "`noremove_gatename": "keyword2",
    "`noremove_netname": "keyword2",
    "`nounconnected_drive": "keyword2",
    "`protect": "keyword2",
    "`protected": "keyword2",
    "`remove_gatename": "keyword2",
    "`remove_netname": "keyword2",
    "`resetall": "keyword2",
    "`signed": "keyword2",
    "`timescale": "keyword2",
    "`unconnected_drive": "keyword2",
    "`undef": "keyword2",
    "`unsigned": "keyword2",
    "always": "keyword1",
    "and": "function",
    "assign": "keyword1",
    "begin": "keyword1",
    "buf": "function",
    "bufif0": "function",
    "bufif1": "function",
    "case": "keyword1",
    "casex": "keyword1",
    "casez": "keyword1",
    "cmos": "function",
    "deassign": "keyword1",
    "default": "keyword1",
    "defparam": "keyword3",
    "disable": "keyword1",
    "else": "keyword1",
    "end": "keyword1",
    "endcase": "keyword1",
    "endfunction": "keyword1",
    "endgenerate": "keyword1",
    "endmodule": "keyword1",
    "endprimitive": "keyword1",
    "endspecify": "keyword1",
    "endtable": "keyword1",
    "endtask": "keyword1",
    "event": "keyword3",
    "for": "keyword1",
    "force": "keyword1",
    "forever": "keyword1",
    "fork": "keyword1",
    "function": "keyword1",
    "generate": "keyword1",
    "highz0": "keyword3",
    "highz1": "keyword3",
    "if": "keyword1",
    "initial": "keyword1",
    "inout": "keyword3",
    "input": "keyword3",
    "integer": "keyword3",
    "join": "keyword1",
    "large": "keyword3",
    "macromodule": "keyword1",
    "medium": "keyword3",
    "module": "keyword1",
    "nand": "function",
    "negedge": "keyword1",
    "nmos": "function",
    "nor": "function",
    "not": "function",
    "notif0": "function",
    "notif1": "function",
    "or": "function",
    "output": "keyword3",
    "parameter": "keyword3",
    "pmos": "function",
    "posedge": "keyword1",
    "primitive": "keyword1",
    "pull0": "keyword3",
    "pull1": "keyword3",
    "pulldown": "function",
    "pullup": "function",
    "rcmos": "function",
    "realtime": "keyword3",
    "reg": "keyword3",
    "release": "keyword1",
    "repeat": "keyword1",
    "rnmos": "function",
    "rpmos": "function",
    "rtran": "function",
    "rtranif0": "function",
    "rtranif1": "function",
    "scalared": "keyword3",
    "small": "keyword3",
    "specify": "keyword1",
    "strong0": "keyword3",
    "strong1": "keyword3",
    "supply0": "keyword3",
    "supply1": "keyword3",
    "table": "keyword1",
    "task": "keyword1",
    "time": "keyword3",
    "tran": "function",
    "tranif0": "function",
    "tranif1": "function",
    "tri": "keyword3",
    "tri0": "keyword3",
    "tri1": "keyword3",
    "triand": "keyword3",
    "trior": "keyword3",
    "trireg": "keyword3",
    "vectored": "keyword3",
    "wait": "keyword1",
    "wand": "keyword3",
    "weak0": "keyword3",
    "weak1": "keyword3",
    "while": "keyword1",
    "wire": "keyword3",
    "wor": "keyword3",
    "xnor": "function",
    "xor": "function",
}

# Dictionary of keywords dictionaries for verilog mode.
keywordsDictDict = {
    "verilog_main": verilog_main_keywords_dict,
}

# Rules for verilog_main ruleset.

def verilog_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def verilog_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def verilog_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def verilog_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="digit", seq="'d")

def verilog_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="digit", seq="'h")

def verilog_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="digit", seq="'b")

def verilog_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="digit", seq="'o")

def verilog_rule7(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def verilog_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def verilog_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def verilog_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def verilog_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def verilog_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def verilog_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def verilog_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def verilog_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def verilog_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def verilog_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def verilog_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def verilog_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def verilog_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def verilog_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def verilog_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def verilog_rule23(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for verilog_main ruleset.
rulesDict1 = {
    "!": [verilog_rule9,],
    "\"": [verilog_rule2,],
    "$": [verilog_rule23,],
    "%": [verilog_rule16,],
    "&": [verilog_rule17,],
    "'": [verilog_rule3, verilog_rule4, verilog_rule5, verilog_rule6,],
    "(": [verilog_rule7,],
    "*": [verilog_rule13,],
    "+": [verilog_rule10,],
    "-": [verilog_rule11,],
    "/": [verilog_rule0, verilog_rule1, verilog_rule12,],
    "0": [verilog_rule23,],
    "1": [verilog_rule23,],
    "2": [verilog_rule23,],
    "3": [verilog_rule23,],
    "4": [verilog_rule23,],
    "5": [verilog_rule23,],
    "6": [verilog_rule23,],
    "7": [verilog_rule23,],
    "8": [verilog_rule23,],
    "9": [verilog_rule23,],
    "<": [verilog_rule15,],
    "=": [verilog_rule8,],
    ">": [verilog_rule14,],
    "@": [verilog_rule23,],
    "A": [verilog_rule23,],
    "B": [verilog_rule23,],
    "C": [verilog_rule23,],
    "D": [verilog_rule23,],
    "E": [verilog_rule23,],
    "F": [verilog_rule23,],
    "G": [verilog_rule23,],
    "H": [verilog_rule23,],
    "I": [verilog_rule23,],
    "J": [verilog_rule23,],
    "K": [verilog_rule23,],
    "L": [verilog_rule23,],
    "M": [verilog_rule23,],
    "N": [verilog_rule23,],
    "O": [verilog_rule23,],
    "P": [verilog_rule23,],
    "Q": [verilog_rule23,],
    "R": [verilog_rule23,],
    "S": [verilog_rule23,],
    "T": [verilog_rule23,],
    "U": [verilog_rule23,],
    "V": [verilog_rule23,],
    "W": [verilog_rule23,],
    "X": [verilog_rule23,],
    "Y": [verilog_rule23,],
    "Z": [verilog_rule23,],
    "^": [verilog_rule19,],
    "_": [verilog_rule23,],
    "`": [verilog_rule23,],
    "a": [verilog_rule23,],
    "b": [verilog_rule23,],
    "c": [verilog_rule23,],
    "d": [verilog_rule23,],
    "e": [verilog_rule23,],
    "f": [verilog_rule23,],
    "g": [verilog_rule23,],
    "h": [verilog_rule23,],
    "i": [verilog_rule23,],
    "j": [verilog_rule23,],
    "k": [verilog_rule23,],
    "l": [verilog_rule23,],
    "m": [verilog_rule23,],
    "n": [verilog_rule23,],
    "o": [verilog_rule23,],
    "p": [verilog_rule23,],
    "q": [verilog_rule23,],
    "r": [verilog_rule23,],
    "s": [verilog_rule23,],
    "t": [verilog_rule23,],
    "u": [verilog_rule23,],
    "v": [verilog_rule23,],
    "w": [verilog_rule23,],
    "x": [verilog_rule23,],
    "y": [verilog_rule23,],
    "z": [verilog_rule23,],
    "{": [verilog_rule22,],
    "|": [verilog_rule18,],
    "}": [verilog_rule21,],
    "~": [verilog_rule20,],
}

# x.rulesDictDict for verilog mode.
rulesDictDict = {
    "verilog_main": rulesDict1,
}

# Import dict for verilog mode.
importDict = {}

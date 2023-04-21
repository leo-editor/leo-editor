# Leo colorizer control file for erlang mode.
# This file is in the public domain.

# Properties for erlang mode.
properties = {
    "lineComment": "%",
}

# Attributes dict for erlang_main ruleset.
erlang_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for erlang mode.
attributesDictDict = {
    "erlang_main": erlang_main_attributes_dict,
}

# Keywords dict for erlang_main ruleset.
erlang_main_keywords_dict = {
    "-behaviour": "keyword3",
    "-compile": "keyword3",
    "-define": "keyword3",
    "-else": "keyword3",
    "-endif": "keyword3",
    "-export": "keyword3",
    "-file": "keyword3",
    "-ifdef": "keyword3",
    "-ifndef": "keyword3",
    "-import": "keyword3",
    "-include": "keyword3",
    "-include_lib": "keyword3",
    "-module": "keyword3",
    "-record": "keyword3",
    "-undef": "keyword3",
    "abs": "keyword2",
    "acos": "keyword2",
    "after": "keyword1",
    "alive": "keyword2",
    "apply": "keyword2",
    "asin": "keyword2",
    "atan": "keyword2",
    "atan2": "keyword2",
    "atom": "keyword2",
    "atom_to_list": "keyword2",
    "begin": "keyword1",
    "binary": "keyword2",
    "binary_to_list": "keyword2",
    "binary_to_term": "keyword2",
    "case": "keyword1",
    "catch": "keyword1",
    "check_process_code": "keyword2",
    "concat_binary": "keyword2",
    "cond": "keyword1",
    "constant": "keyword2",
    "cos": "keyword2",
    "cosh": "keyword2",
    "date": "keyword2",
    "delete_module": "keyword2",
    "disconnect_node": "keyword2",
    "element": "keyword2",
    "end": "keyword1",
    "erase": "keyword2",
    "exit": "keyword2",
    "exp": "keyword2",
    "float": "keyword2",
    "float_to_list": "keyword2",
    "fun": "keyword1",
    "function": "keyword2",
    "get": "keyword2",
    "get_cookie": "keyword2",
    "get_keys": "keyword2",
    "group_leader": "keyword2",
    "halt": "keyword2",
    "hash": "keyword2",
    "hd": "keyword2",
    "if": "keyword1",
    "integer": "keyword2",
    "integer_to_list": "keyword2",
    "is_alive": "keyword2",
    "length": "keyword2",
    "let": "keyword1",
    "link": "keyword2",
    "list": "keyword2",
    "list_to_atom": "keyword2",
    "list_to_binary": "keyword2",
    "list_to_float": "keyword2",
    "list_to_integer": "keyword2",
    "list_to_pid": "keyword2",
    "list_to_tuple": "keyword2",
    "load_module": "keyword2",
    "log": "keyword2",
    "log10": "keyword2",
    "make_ref": "keyword2",
    "math": "keyword2",
    "module_loaded": "keyword2",
    "monitor_node": "keyword2",
    "node": "keyword2",
    "nodes": "keyword2",
    "now": "keyword2",
    "number": "keyword2",
    "of": "keyword1",
    "open_port": "keyword2",
    "pi": "keyword2",
    "pid": "keyword2",
    "pid_to_list": "keyword2",
    "port_close": "keyword2",
    "port_info": "keyword2",
    "ports": "keyword2",
    "pow": "keyword2",
    "power": "keyword2",
    "preloaded": "keyword2",
    "process": "keyword2",
    "process_flag": "keyword2",
    "process_info": "keyword2",
    "processes": "keyword2",
    "purge_module": "keyword2",
    "put": "keyword2",
    "query": "keyword1",
    "receive": "keyword1",
    "record": "keyword2",
    "reference": "keyword2",
    "register": "keyword2",
    "registered": "keyword2",
    "round": "keyword2",
    "self": "keyword2",
    "set_cookie": "keyword2",
    "set_node": "keyword2",
    "setelement": "keyword2",
    "sin": "keyword2",
    "sinh": "keyword2",
    "size": "keyword2",
    "spawn": "keyword2",
    "spawn_link": "keyword2",
    "split_binary": "keyword2",
    "sqrt": "keyword2",
    "statistics": "keyword2",
    "tan": "keyword2",
    "tanh": "keyword2",
    "term_to_binary": "keyword2",
    "throw": "keyword2",
    "time": "keyword2",
    "tl": "keyword2",
    "trunc": "keyword2",
    "tuple_to_list": "keyword2",
    "unlink": "keyword2",
    "unregister": "keyword2",
    "when": "keyword1",
    "whereis": "keyword2",
}

# Dictionary of keywords dictionaries for erlang mode.
keywordsDictDict = {
    "erlang_main": erlang_main_keywords_dict,
}

# Rules for erlang_main ruleset.

def erlang_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def erlang_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def erlang_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def erlang_rule3(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def erlang_rule4(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="literal2", pattern=":",
          exclude_match=True)

def erlang_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\$.\\w*")

def erlang_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="badarg")

def erlang_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="nocookie")

def erlang_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="false")

def erlang_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="true")

def erlang_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def erlang_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<-")

def erlang_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def erlang_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def erlang_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def erlang_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def erlang_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def erlang_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="#")

def erlang_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def erlang_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def erlang_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def erlang_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def erlang_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def erlang_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def erlang_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def erlang_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def erlang_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def erlang_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def erlang_rule28(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bdiv\\b")

def erlang_rule29(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\brem\\b")

def erlang_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bor\\b")

def erlang_rule31(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bxor\\b")

def erlang_rule32(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbor\\b")

def erlang_rule33(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbxor\\b")

def erlang_rule34(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbsl\\b")

def erlang_rule35(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbsr\\b")

def erlang_rule36(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\band\\b")

def erlang_rule37(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bband\\b")

def erlang_rule38(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bnot\\b")

def erlang_rule39(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbnot\\b")

def erlang_rule40(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for erlang_main ruleset.
rulesDict1 = {
    "!": [erlang_rule27,],
    "\"": [erlang_rule1,],
    "#": [erlang_rule17,],
    "$": [erlang_rule5,],
    "%": [erlang_rule0,],
    "'": [erlang_rule2,],
    "(": [erlang_rule3,],
    "*": [erlang_rule19,],
    "+": [erlang_rule18,],
    ",": [erlang_rule25,],
    "-": [erlang_rule10, erlang_rule40,],
    ".": [erlang_rule12,],
    "/": [erlang_rule15,],
    "0": [erlang_rule40,],
    "1": [erlang_rule40,],
    "2": [erlang_rule40,],
    "3": [erlang_rule40,],
    "4": [erlang_rule40,],
    "5": [erlang_rule40,],
    "6": [erlang_rule40,],
    "7": [erlang_rule40,],
    "8": [erlang_rule40,],
    "9": [erlang_rule40,],
    ":": [erlang_rule4, erlang_rule20,],
    ";": [erlang_rule13,],
    "<": [erlang_rule11,],
    "=": [erlang_rule14,],
    "?": [erlang_rule26,],
    "@": [erlang_rule40,],
    "A": [erlang_rule40,],
    "B": [erlang_rule40,],
    "C": [erlang_rule40,],
    "D": [erlang_rule40,],
    "E": [erlang_rule40,],
    "F": [erlang_rule40,],
    "G": [erlang_rule40,],
    "H": [erlang_rule40,],
    "I": [erlang_rule40,],
    "J": [erlang_rule40,],
    "K": [erlang_rule40,],
    "L": [erlang_rule40,],
    "M": [erlang_rule40,],
    "N": [erlang_rule40,],
    "O": [erlang_rule40,],
    "P": [erlang_rule40,],
    "Q": [erlang_rule40,],
    "R": [erlang_rule40,],
    "S": [erlang_rule40,],
    "T": [erlang_rule40,],
    "U": [erlang_rule40,],
    "V": [erlang_rule40,],
    "W": [erlang_rule40,],
    "X": [erlang_rule40,],
    "Y": [erlang_rule40,],
    "Z": [erlang_rule40,],
    "[": [erlang_rule23,],
    "]": [erlang_rule24,],
    "_": [erlang_rule40,],
    "a": [erlang_rule36, erlang_rule40,],
    "b": [erlang_rule6, erlang_rule32, erlang_rule33, erlang_rule34, erlang_rule35, erlang_rule37, erlang_rule39, erlang_rule40,],
    "c": [erlang_rule40,],
    "d": [erlang_rule28, erlang_rule40,],
    "e": [erlang_rule40,],
    "f": [erlang_rule8, erlang_rule40,],
    "g": [erlang_rule40,],
    "h": [erlang_rule40,],
    "i": [erlang_rule40,],
    "j": [erlang_rule40,],
    "k": [erlang_rule40,],
    "l": [erlang_rule40,],
    "m": [erlang_rule40,],
    "n": [erlang_rule7, erlang_rule38, erlang_rule40,],
    "o": [erlang_rule30, erlang_rule40,],
    "p": [erlang_rule40,],
    "q": [erlang_rule40,],
    "r": [erlang_rule29, erlang_rule40,],
    "s": [erlang_rule40,],
    "t": [erlang_rule9, erlang_rule40,],
    "u": [erlang_rule40,],
    "v": [erlang_rule40,],
    "w": [erlang_rule40,],
    "x": [erlang_rule31, erlang_rule40,],
    "y": [erlang_rule40,],
    "z": [erlang_rule40,],
    "{": [erlang_rule21,],
    "|": [erlang_rule16,],
    "}": [erlang_rule22,],
}

# x.rulesDictDict for erlang mode.
rulesDictDict = {
    "erlang_main": rulesDict1,
}

# Import dict for erlang mode.
importDict = {}

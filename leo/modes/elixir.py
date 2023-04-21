# Leo colorizer controfl file for elixir mode.  Based on erlang.
# This file is in the public domain.

# Properties for elixir mode.
properties = {
    "lineComment": "#",
}

# Attributes dict for elixir_main ruleset.
elixir_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for elixir mode.
attributesDictDict = {
    "elixir_main": elixir_main_attributes_dict,
}

# Keywords dict for elixir_main ruleset.
elixir_main_keywords_dict = {
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
    "defmodule": "keyword1",
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

# Dictionary of keywords dictionaries for elixir mode.
keywordsDictDict = {
    "elixir_main": elixir_main_keywords_dict,
}

# Rules for elixir_main ruleset.

def elixir_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def elixir_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def elixir_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def elixir_rule3(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def elixir_rule4(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="literal2", pattern=":",
          exclude_match=True)

# Not used.
def elixir_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\$.\\w*")

def elixir_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="badarg")

def elixir_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="nocookie")

def elixir_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="false")

def elixir_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal3", seq="true")

def elixir_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def elixir_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<-")

def elixir_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def elixir_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def elixir_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def elixir_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def elixir_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def elixir_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="#")

def elixir_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def elixir_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def elixir_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def elixir_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def elixir_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def elixir_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def elixir_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def elixir_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def elixir_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def elixir_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def elixir_rule28(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bdiv\\b")

def elixir_rule29(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\brem\\b")

def elixir_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bor\\b")

def elixir_rule31(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bxor\\b")

def elixir_rule32(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbor\\b")

def elixir_rule33(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbxor\\b")

def elixir_rule34(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbsl\\b")

def elixir_rule35(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbsr\\b")

def elixir_rule36(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\band\\b")

def elixir_rule37(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bband\\b")

def elixir_rule38(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bnot\\b")

def elixir_rule39(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="operator", regexp="\\bbnot\\b")

def elixir_rule40(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for elixir_main ruleset.
rulesDict1 = {
    "!": [elixir_rule27,],
    "\"": [elixir_rule1,],
    "#": [elixir_rule0, elixir_rule17,],
    # "$": [elixir_rule5,],
    "'": [elixir_rule2,],
    "(": [elixir_rule3,],
    "*": [elixir_rule19,],
    "+": [elixir_rule18,],
    ",": [elixir_rule25,],
    "-": [elixir_rule10, elixir_rule40,],
    ".": [elixir_rule12,],
    "/": [elixir_rule15,],
    "0": [elixir_rule40,],
    "1": [elixir_rule40,],
    "2": [elixir_rule40,],
    "3": [elixir_rule40,],
    "4": [elixir_rule40,],
    "5": [elixir_rule40,],
    "6": [elixir_rule40,],
    "7": [elixir_rule40,],
    "8": [elixir_rule40,],
    "9": [elixir_rule40,],
    ":": [elixir_rule4, elixir_rule20,],
    ";": [elixir_rule13,],
    "<": [elixir_rule11,],
    "=": [elixir_rule14,],
    "?": [elixir_rule26,],
    "@": [elixir_rule40,],
    "A": [elixir_rule40,],
    "B": [elixir_rule40,],
    "C": [elixir_rule40,],
    "D": [elixir_rule40,],
    "E": [elixir_rule40,],
    "F": [elixir_rule40,],
    "G": [elixir_rule40,],
    "H": [elixir_rule40,],
    "I": [elixir_rule40,],
    "J": [elixir_rule40,],
    "K": [elixir_rule40,],
    "L": [elixir_rule40,],
    "M": [elixir_rule40,],
    "N": [elixir_rule40,],
    "O": [elixir_rule40,],
    "P": [elixir_rule40,],
    "Q": [elixir_rule40,],
    "R": [elixir_rule40,],
    "S": [elixir_rule40,],
    "T": [elixir_rule40,],
    "U": [elixir_rule40,],
    "V": [elixir_rule40,],
    "W": [elixir_rule40,],
    "X": [elixir_rule40,],
    "Y": [elixir_rule40,],
    "Z": [elixir_rule40,],
    "[": [elixir_rule23,],
    "]": [elixir_rule24,],
    "_": [elixir_rule40,],
    "a": [elixir_rule36, elixir_rule40,],
    "b": [elixir_rule6, elixir_rule32, elixir_rule33, elixir_rule34, elixir_rule35, elixir_rule37, elixir_rule39, elixir_rule40,],
    "c": [elixir_rule40,],
    "d": [elixir_rule28, elixir_rule40,],
    "e": [elixir_rule40,],
    "f": [elixir_rule8, elixir_rule40,],
    "g": [elixir_rule40,],
    "h": [elixir_rule40,],
    "i": [elixir_rule40,],
    "j": [elixir_rule40,],
    "k": [elixir_rule40,],
    "l": [elixir_rule40,],
    "m": [elixir_rule40,],
    "n": [elixir_rule7, elixir_rule38, elixir_rule40,],
    "o": [elixir_rule30, elixir_rule40,],
    "p": [elixir_rule40,],
    "q": [elixir_rule40,],
    "r": [elixir_rule29, elixir_rule40,],
    "s": [elixir_rule40,],
    "t": [elixir_rule9, elixir_rule40,],
    "u": [elixir_rule40,],
    "v": [elixir_rule40,],
    "w": [elixir_rule40,],
    "x": [elixir_rule31, elixir_rule40,],
    "y": [elixir_rule40,],
    "z": [elixir_rule40,],
    "{": [elixir_rule21,],
    "|": [elixir_rule16,],
    "}": [elixir_rule22,],
}

# x.rulesDictDict for elixir mode.
rulesDictDict = {
    "elixir_main": rulesDict1,
}

# Import dict for elixir mode.
importDict = {}

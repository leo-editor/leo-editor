# Leo colorizer control file for assembly_parrot mode.
# This file is in the public domain.

# Properties for assembly_parrot mode.
properties = {
    "lineComment": "#",
}

# Attributes dict for assembly_parrot_main ruleset.
assembly_parrot_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+|[[:digit:]]+)",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for assembly_parrot mode.
attributesDictDict = {
    "assembly_parrot_main": assembly_parrot_main_attributes_dict,
}

# Keywords dict for assembly_parrot_main ruleset.
assembly_parrot_main_keywords_dict = {
    "abs": "keyword1",
    "acos": "keyword1",
    "add": "keyword1",
    "and": "keyword1",
    "asec": "keyword1",
    "asin": "keyword1",
    "atan": "keyword1",
    "bounds": "keyword1",
    "branch": "keyword1",
    "bsr": "keyword1",
    "chopm": "keyword1",
    "cleari": "keyword1",
    "clearn": "keyword1",
    "clearp": "keyword1",
    "clears": "keyword1",
    "clone": "keyword1",
    "close": "keyword1",
    "cmod": "keyword1",
    "concat": "keyword1",
    "cos": "keyword1",
    "cosh": "keyword1",
    "debug": "keyword1",
    "dec": "keyword1",
    "div": "keyword1",
    "end": "keyword1",
    "entrytype": "keyword1",
    "eq": "keyword1",
    "err": "keyword1",
    "exp": "keyword1",
    "find_global": "keyword1",
    "find_type": "keyword1",
    "ge": "keyword1",
    "getfile": "keyword1",
    "getline": "keyword1",
    "getpackage": "keyword1",
    "gt": "keyword1",
    "if": "keyword1",
    "inc": "keyword1",
    "index": "keyword1",
    "jsr": "keyword1",
    "jump": "keyword1",
    "le": "keyword1",
    "length": "keyword1",
    "ln": "keyword1",
    "log10": "keyword1",
    "log2": "keyword1",
    "lt": "keyword1",
    "mod": "keyword1",
    "mul": "keyword1",
    "ne": "keyword1",
    "new": "keyword1",
    "newinterp": "keyword1",
    "noop": "keyword1",
    "not": "keyword1",
    "open": "keyword1",
    "or": "keyword1",
    "ord": "keyword1",
    "pack": "keyword1",
    "pop": "keyword1",
    "popi": "keyword1",
    "popn": "keyword1",
    "popp": "keyword1",
    "pops": "keyword1",
    "pow": "keyword1",
    "print": "keyword1",
    "profile": "keyword1",
    "push": "keyword1",
    "pushi": "keyword1",
    "pushn": "keyword1",
    "pushp": "keyword1",
    "pushs": "keyword1",
    "read": "keyword1",
    "readline": "keyword1",
    "repeat": "keyword1",
    "restore": "keyword1",
    "ret": "keyword1",
    "rotate_up": "keyword1",
    "runinterp": "keyword1",
    "save": "keyword1",
    "sec": "keyword1",
    "sech": "keyword1",
    "set": "keyword1",
    "set_keyed": "keyword1",
    "setfile": "keyword1",
    "setline": "keyword1",
    "setpackage": "keyword1",
    "shl": "keyword1",
    "shr": "keyword1",
    "sin": "keyword1",
    "sinh": "keyword1",
    "sleep": "keyword1",
    "sub": "keyword1",
    "substr": "keyword1",
    "tan": "keyword1",
    "tanh": "keyword1",
    "time": "keyword1",
    "trace": "keyword1",
    "typeof": "keyword1",
    "unless": "keyword1",
    "warningsoff": "keyword1",
    "warningson": "keyword1",
    "write": "keyword1",
    "xor": "keyword1",
}

# Dictionary of keywords dictionaries for assembly_parrot mode.
keywordsDictDict = {
    "assembly_parrot_main": assembly_parrot_main_keywords_dict,
}

# Rules for assembly_parrot_main ruleset.

def assembly_parrot_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def assembly_parrot_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def assembly_parrot_rule2(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_line_start=True,
          exclude_match=True)

def assembly_parrot_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def assembly_parrot_rule4(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="I\\d{1,2}")

def assembly_parrot_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="S\\d{1,2}")

def assembly_parrot_rule6(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="N\\d{1,2}")

def assembly_parrot_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="P\\d{1,2}")

def assembly_parrot_rule8(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for assembly_parrot_main ruleset.
rulesDict1 = {
    "\"": [assembly_parrot_rule0,],
    "#": [assembly_parrot_rule1,],
    ",": [assembly_parrot_rule3,],
    "0": [assembly_parrot_rule8,],
    "1": [assembly_parrot_rule8,],
    "2": [assembly_parrot_rule8,],
    "3": [assembly_parrot_rule8,],
    "4": [assembly_parrot_rule8,],
    "5": [assembly_parrot_rule8,],
    "6": [assembly_parrot_rule8,],
    "7": [assembly_parrot_rule8,],
    "8": [assembly_parrot_rule8,],
    "9": [assembly_parrot_rule8,],
    ":": [assembly_parrot_rule2,],
    "@": [assembly_parrot_rule8,],
    "A": [assembly_parrot_rule8,],
    "B": [assembly_parrot_rule8,],
    "C": [assembly_parrot_rule8,],
    "D": [assembly_parrot_rule8,],
    "E": [assembly_parrot_rule8,],
    "F": [assembly_parrot_rule8,],
    "G": [assembly_parrot_rule8,],
    "H": [assembly_parrot_rule8,],
    "I": [assembly_parrot_rule4, assembly_parrot_rule8,],
    "J": [assembly_parrot_rule8,],
    "K": [assembly_parrot_rule8,],
    "L": [assembly_parrot_rule8,],
    "M": [assembly_parrot_rule8,],
    "N": [assembly_parrot_rule6, assembly_parrot_rule8,],
    "O": [assembly_parrot_rule8,],
    "P": [assembly_parrot_rule7, assembly_parrot_rule8,],
    "Q": [assembly_parrot_rule8,],
    "R": [assembly_parrot_rule8,],
    "S": [assembly_parrot_rule5, assembly_parrot_rule8,],
    "T": [assembly_parrot_rule8,],
    "U": [assembly_parrot_rule8,],
    "V": [assembly_parrot_rule8,],
    "W": [assembly_parrot_rule8,],
    "X": [assembly_parrot_rule8,],
    "Y": [assembly_parrot_rule8,],
    "Z": [assembly_parrot_rule8,],
    "_": [assembly_parrot_rule8,],
    "a": [assembly_parrot_rule8,],
    "b": [assembly_parrot_rule8,],
    "c": [assembly_parrot_rule8,],
    "d": [assembly_parrot_rule8,],
    "e": [assembly_parrot_rule8,],
    "f": [assembly_parrot_rule8,],
    "g": [assembly_parrot_rule8,],
    "h": [assembly_parrot_rule8,],
    "i": [assembly_parrot_rule8,],
    "j": [assembly_parrot_rule8,],
    "k": [assembly_parrot_rule8,],
    "l": [assembly_parrot_rule8,],
    "m": [assembly_parrot_rule8,],
    "n": [assembly_parrot_rule8,],
    "o": [assembly_parrot_rule8,],
    "p": [assembly_parrot_rule8,],
    "q": [assembly_parrot_rule8,],
    "r": [assembly_parrot_rule8,],
    "s": [assembly_parrot_rule8,],
    "t": [assembly_parrot_rule8,],
    "u": [assembly_parrot_rule8,],
    "v": [assembly_parrot_rule8,],
    "w": [assembly_parrot_rule8,],
    "x": [assembly_parrot_rule8,],
    "y": [assembly_parrot_rule8,],
    "z": [assembly_parrot_rule8,],
}

# x.rulesDictDict for assembly_parrot mode.
rulesDictDict = {
    "assembly_parrot_main": rulesDict1,
}

# Import dict for assembly_parrot mode.
importDict = {}

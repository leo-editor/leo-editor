# Leo colorizer control file for bbj mode.
# This file is in the public domain.

# Properties for bbj mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for bbj_main ruleset.
bbj_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for bbj mode.
attributesDictDict = {
    "bbj_main": bbj_main_attributes_dict,
}

# Keywords dict for bbj_main ruleset.
bbj_main_keywords_dict = {
    "abs": "keyword1",
    "addr": "keyword3",
    "adjn": "keyword1",
    "all": "keyword3",
    "argc": "keyword1",
    "argv": "keyword1",
    "asc": "keyword1",
    "ath": "keyword1",
    "atn": "keyword1",
    "auto": "keyword3",
    "background": "keyword1",
    "begin": "keyword3",
    "bin": "keyword1",
    "break": "keyword3",
    "bsz": "keyword1",
    "call": "keyword3",
    "callback": "keyword1",
    "case": "keyword3",
    "chanopt": "keyword1",
    "chdir": "keyword2",
    "chn": "keyword3",
    "chr": "keyword1",
    "cisam": "keyword2",
    "clear": "keyword3",
    "clipclear": "keyword1",
    "clipfromfile": "keyword1",
    "clipfromstr": "keyword1",
    "clipisformat": "keyword1",
    "cliplock": "keyword1",
    "clipregformat": "keyword1",
    "cliptofile": "keyword1",
    "cliptostr": "keyword1",
    "clipunlock": "keyword1",
    "close": "keyword2",
    "continue": "keyword2",
    "cos": "keyword1",
    "cpl": "keyword1",
    "crc": "keyword1",
    "crc16": "keyword1",
    "ctl": "keyword3",
    "ctrl": "keyword1",
    "cvs": "keyword1",
    "cvt": "keyword1",
    "data": "keyword3",
    "date": "keyword1",
    "day": "keyword3",
    "dec": "keyword1",
    "def": "keyword3",
    "default": "keyword3",
    "defend": "keyword3",
    "delete": "keyword3",
    "dim": "keyword3",
    "dims": "keyword1",
    "dir": "keyword2",
    "direct": "keyword2",
    "disable": "keyword2",
    "dom": "keyword2",
    "dread": "keyword3",
    "drop": "keyword3",
    "dsk": "keyword1",
    "dsz": "keyword1",
    "dump": "keyword2",
    "edit": "keyword3",
    "else": "keyword3",
    "enable": "keyword2",
    "end": "keyword2",
    "endif": "keyword3",
    "endtrace": "keyword2",
    "enter": "keyword3",
    "ept": "keyword1",
    "erase": "keyword2",
    "err": "keyword3",
    "errmes": "keyword1",
    "escape": "keyword3",
    "escoff": "keyword3",
    "escon": "keyword3",
    "execute": "keyword3",
    "exit": "keyword3",
    "exitto": "keyword3",
    "extract": "keyword2",
    "fattr": "keyword1",
    "fbin": "keyword1",
    "fdec": "keyword1",
    "fi": "keyword3",
    "fid": "keyword2",
    "field": "keyword1",
    "file": "keyword2",
    "fileopt": "keyword1",
    "fill": "keyword1",
    "fin": "keyword2",
    "find": "keyword2",
    "floatingpoint": "keyword1",
    "for": "keyword3",
    "fpt": "keyword1",
    "from": "keyword2",
    "gap": "keyword1",
    "gosub": "keyword3",
    "goto": "keyword3",
    "hsa": "keyword1",
    "hsh": "keyword1",
    "hta": "keyword1",
    "if": "keyword3",
    "iff": "keyword3",
    "imp": "keyword1",
    "ind": "keyword2",
    "indexed": "keyword2",
    "info": "keyword1",
    "initfile": "keyword3",
    "input": "keyword2",
    "inpute": "keyword2",
    "inputn": "keyword2",
    "int": "keyword1",
    "iol": "keyword2",
    "iolist": "keyword2",
    "ior": "keyword3",
    "jul": "keyword1",
    "key": "keyword2",
    "keyf": "keyword2",
    "keyl": "keyword2",
    "keyn": "keyword2",
    "keyp": "keyword2",
    "kgen": "keyword2",
    "knum": "keyword2",
    "lcheckin": "keyword1",
    "lcheckout": "keyword1",
    "len": "keyword1",
    "let": "keyword3",
    "linfo": "keyword1",
    "list": "keyword2",
    "load": "keyword2",
    "lock": "keyword2",
    "log": "keyword1",
    "lrc": "keyword1",
    "lst": "keyword1",
    "mask": "keyword1",
    "max": "keyword1",
    "menuinfo": "keyword1",
    "merge": "keyword2",
    "min": "keyword1",
    "mkdir": "keyword2",
    "mkeyed": "keyword2",
    "mod": "keyword1",
    "msgbox": "keyword1",
    "neval": "keyword1",
    "next": "keyword3",
    "nfield": "keyword1",
    "not": "keyword3",
    "notice": "keyword1",
    "noticetpl": "keyword1",
    "num": "keyword1",
    "on": "keyword3",
    "open": "keyword2",
    "opts": "keyword3",
    "or": "keyword3",
    "pad": "keyword1",
    "pck": "keyword1",
    "pfx": "keyword3",
    "pgm": "keyword1",
    "pos": "keyword1",
    "precision": "keyword3",
    "prefix": "keyword2",
    "print": "keyword2",
    "process_events": "keyword1",
    "program": "keyword1",
    "psz": "keyword1",
    "pub": "keyword1",
    "read": "keyword2",
    "read_resource": "keyword2",
    "record": "keyword2",
    "release": "keyword3",
    "remove": "keyword2",
    "remove_callback": "keyword1",
    "rename": "keyword2",
    "renum": "keyword3",
    "repeat": "keyword3",
    "resclose": "keyword2",
    "reserve": "keyword1",
    "reset": "keyword3",
    "resfirst": "keyword2",
    "resget": "keyword2",
    "resinfo": "keyword2",
    "resnext": "keyword2",
    "resopen": "keyword2",
    "restore": "keyword3",
    "retry": "keyword3",
    "return": "keyword3",
    "rev": "keyword2",
    "rmdir": "keyword2",
    "rnd": "keyword1",
    "round": "keyword1",
    "run": "keyword3",
    "save": "keyword2",
    "scall": "keyword1",
    "select": "keyword2",
    "sendmsg": "keyword1",
    "serial": "keyword2",
    "set_case_sensitive_off": "keyword3",
    "set_case_sensitive_on": "keyword3",
    "setday": "keyword2",
    "setdrive": "keyword2",
    "seterr": "keyword3",
    "setesc": "keyword3",
    "setopts": "keyword3",
    "settime": "keyword3",
    "settrace": "keyword2",
    "seval": "keyword1",
    "sgn": "keyword1",
    "sin": "keyword1",
    "siz": "keyword2",
    "sort": "keyword2",
    "sqlchn": "keyword2",
    "sqlclose": "keyword2",
    "sqlerr": "keyword2",
    "sqlexec": "keyword2",
    "sqlfetch": "keyword2",
    "sqllist": "keyword2",
    "sqlopen": "keyword2",
    "sqlprep": "keyword2",
    "sqlset": "keyword2",
    "sqltables": "keyword2",
    "sqltmpl": "keyword2",
    "sqlunt": "keyword2",
    "sqr": "keyword1",
    "ssn": "keyword3",
    "ssort": "keyword1",
    "ssz": "keyword1",
    "start": "keyword3",
    "stbl": "keyword1",
    "step": "keyword3",
    "stop": "keyword3",
    "str": "keyword1",
    "string": "keyword2",
    "swap": "keyword1",
    "swend": "keyword3",
    "switch": "keyword3",
    "sys": "keyword1",
    "table": "keyword2",
    "tbl": "keyword2",
    "tcb": "keyword1",
    "then": "keyword3",
    "tim": "keyword2",
    "tmpl": "keyword1",
    "to": "keyword3",
    "tsk": "keyword1",
    "unlock": "keyword2",
    "unt": "keyword3",
    "until": "keyword3",
    "upk": "keyword1",
    "wait": "keyword3",
    "wend": "keyword3",
    "where": "keyword2",
    "while": "keyword3",
    "winfirst": "keyword1",
    "wininfo": "keyword1",
    "winnext": "keyword1",
    "write": "keyword2",
    "xfid": "keyword2",
    "xfile": "keyword2",
    "xfin": "keyword2",
    "xor": "keyword3",
}

# Dictionary of keywords dictionaries for bbj mode.
keywordsDictDict = {
    "bbj_main": bbj_main_keywords_dict,
}

# Rules for bbj_main ruleset.

def bbj_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def bbj_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def bbj_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def bbj_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="REM")

def bbj_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def bbj_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def bbj_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def bbj_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def bbj_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def bbj_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def bbj_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def bbj_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def bbj_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def bbj_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def bbj_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def bbj_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="and")

def bbj_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="or")

def bbj_rule17(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_line_start=True,
          exclude_match=True)

def bbj_rule18(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def bbj_rule19(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for bbj_main ruleset.
rulesDict1 = {
    "\"": [bbj_rule1,],
    "(": [bbj_rule18,],
    "*": [bbj_rule10,],
    "+": [bbj_rule7,],
    "-": [bbj_rule8,],
    "/": [bbj_rule0, bbj_rule2, bbj_rule9,],
    "0": [bbj_rule19,],
    "1": [bbj_rule19,],
    "2": [bbj_rule19,],
    "3": [bbj_rule19,],
    "4": [bbj_rule19,],
    "5": [bbj_rule19,],
    "6": [bbj_rule19,],
    "7": [bbj_rule19,],
    "8": [bbj_rule19,],
    "9": [bbj_rule19,],
    ":": [bbj_rule17,],
    "<": [bbj_rule6, bbj_rule12, bbj_rule13,],
    "=": [bbj_rule4,],
    ">": [bbj_rule5, bbj_rule11,],
    "@": [bbj_rule19,],
    "A": [bbj_rule19,],
    "B": [bbj_rule19,],
    "C": [bbj_rule19,],
    "D": [bbj_rule19,],
    "E": [bbj_rule19,],
    "F": [bbj_rule19,],
    "G": [bbj_rule19,],
    "H": [bbj_rule19,],
    "I": [bbj_rule19,],
    "J": [bbj_rule19,],
    "K": [bbj_rule19,],
    "L": [bbj_rule19,],
    "M": [bbj_rule19,],
    "N": [bbj_rule19,],
    "O": [bbj_rule19,],
    "P": [bbj_rule19,],
    "Q": [bbj_rule19,],
    "R": [bbj_rule3, bbj_rule19,],
    "S": [bbj_rule19,],
    "T": [bbj_rule19,],
    "U": [bbj_rule19,],
    "V": [bbj_rule19,],
    "W": [bbj_rule19,],
    "X": [bbj_rule19,],
    "Y": [bbj_rule19,],
    "Z": [bbj_rule19,],
    "^": [bbj_rule14,],
    "_": [bbj_rule19,],
    "a": [bbj_rule15, bbj_rule19,],
    "b": [bbj_rule19,],
    "c": [bbj_rule19,],
    "d": [bbj_rule19,],
    "e": [bbj_rule19,],
    "f": [bbj_rule19,],
    "g": [bbj_rule19,],
    "h": [bbj_rule19,],
    "i": [bbj_rule19,],
    "j": [bbj_rule19,],
    "k": [bbj_rule19,],
    "l": [bbj_rule19,],
    "m": [bbj_rule19,],
    "n": [bbj_rule19,],
    "o": [bbj_rule16, bbj_rule19,],
    "p": [bbj_rule19,],
    "q": [bbj_rule19,],
    "r": [bbj_rule19,],
    "s": [bbj_rule19,],
    "t": [bbj_rule19,],
    "u": [bbj_rule19,],
    "v": [bbj_rule19,],
    "w": [bbj_rule19,],
    "x": [bbj_rule19,],
    "y": [bbj_rule19,],
    "z": [bbj_rule19,],
}

# x.rulesDictDict for bbj mode.
rulesDictDict = {
    "bbj_main": rulesDict1,
}

# Import dict for bbj mode.
importDict = {}

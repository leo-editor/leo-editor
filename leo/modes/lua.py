# Leo colorizer control file for lua mode.
# This file is in the public domain.

# Properties for lua mode.
properties = {
    "commentEnd": "]]",
    "commentStart": "--[[",
    "doubleBracketIndent": "true",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "--",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for lua_main ruleset.
lua_main_attributes_dict = {
    "default": "null",
    "digit_re": "[[:digit:]]*(\\.[[:digit:]]*)?([eE][+-]?[[:digit:]]*)?",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "_:.",
}

# Dictionary of attributes dictionaries for lua mode.
attributesDictDict = {
    "lua_main": lua_main_attributes_dict,
}

# Keywords dict for lua_main ruleset.
lua_main_keywords_dict = {
    "...": "keyword2",
    "LUA_PATH": "keyword2",
    "_ALERT": "keyword2",
    "_ERRORMESSAGE": "keyword2",
    "_G": "keyword2",
    "_LOADED": "keyword2",
    "_PROMPT": "keyword2",
    "_REQUIREDNAME": "keyword2",
    "_VERSION": "keyword2",
    "__add": "keyword2",
    "__call": "keyword2",
    "__concat": "keyword2",
    "__div": "keyword2",
    "__eq": "keyword2",
    "__fenv": "keyword2",
    "__index": "keyword2",
    "__le": "keyword2",
    "__lt": "keyword2",
    "__metatable": "keyword2",
    "__mode": "keyword2",
    "__mul": "keyword2",
    "__newindex": "keyword2",
    "__pow": "keyword2",
    "__sub": "keyword2",
    "__tostring": "keyword2",
    "__unm": "keyword2",
    "and": "keyword1",
    "arg": "keyword2",
    "assert": "keyword2",
    "break": "keyword1",
    "collectgarbage": "keyword2",
    "coroutine.create": "keyword2",
    "coroutine.resume": "keyword2",
    "coroutine.status": "keyword2",
    "coroutine.wrap": "keyword2",
    "coroutine.yield": "keyword2",
    "debug.debug": "keyword2",
    "debug.gethook": "keyword2",
    "debug.getinfo": "keyword2",
    "debug.getlocal": "keyword2",
    "debug.getupvalue": "keyword2",
    "debug.sethook": "keyword2",
    "debug.setlocal": "keyword2",
    "debug.setupvalue": "keyword2",
    "debug.traceback": "keyword2",
    "do": "keyword1",
    "dofile": "keyword2",
    "else": "keyword1",
    "elseif": "keyword1",
    "end": "keyword1",
    "error": "keyword2",
    "false": "keyword3",
    "for": "keyword1",
    "function": "keyword1",
    "gcinfo": "keyword2",
    "getfenv": "keyword2",
    "getmetatable": "keyword2",
    "if": "keyword1",
    "in": "keyword1",
    "io.close": "keyword2",
    "io.flush": "keyword2",
    "io.input": "keyword2",
    "io.lines": "keyword2",
    "io.open": "keyword2",
    "io.read": "keyword2",
    "io.stderr": "keyword2",
    "io.stdin": "keyword2",
    "io.stdout": "keyword2",
    "io.tmpfile": "keyword2",
    "io.type": "keyword2",
    "io.write": "keyword2",
    "ipairs": "keyword2",
    "loadfile": "keyword2",
    "loadlib": "keyword2",
    "loadstring": "keyword2",
    "local": "keyword1",
    "math.abs": "keyword2",
    "math.acos": "keyword2",
    "math.asin": "keyword2",
    "math.atan": "keyword2",
    "math.atan2": "keyword2",
    "math.ceil": "keyword2",
    "math.cos": "keyword2",
    "math.deg": "keyword2",
    "math.exp": "keyword2",
    "math.floor": "keyword2",
    "math.frexp": "keyword2",
    "math.ldexp": "keyword2",
    "math.log": "keyword2",
    "math.log10": "keyword2",
    "math.max": "keyword2",
    "math.min": "keyword2",
    "math.mod": "keyword2",
    "math.pi": "keyword2",
    "math.pow": "keyword2",
    "math.rad": "keyword2",
    "math.random": "keyword2",
    "math.randomseed": "keyword2",
    "math.sin": "keyword2",
    "math.sqrt": "keyword2",
    "math.tan": "keyword2",
    "next": "keyword2",
    "nil": "keyword3",
    "not": "keyword1",
    "or": "keyword1",
    "os.clock": "keyword2",
    "os.date": "keyword2",
    "os.difftime": "keyword2",
    "os.execute": "keyword2",
    "os.exit": "keyword2",
    "os.getenv": "keyword2",
    "os.remove": "keyword2",
    "os.rename": "keyword2",
    "os.setlocale": "keyword2",
    "os.time": "keyword2",
    "os.tmpname": "keyword2",
    "pairs": "keyword2",
    "pcall": "keyword2",
    "print": "keyword2",
    "rawequal": "keyword2",
    "rawget": "keyword2",
    "rawset": "keyword2",
    "repeat": "keyword1",
    "require": "keyword2",
    "return": "keyword1",
    "setfenv": "keyword2",
    "setmetatable": "keyword2",
    "string.byte": "keyword2",
    "string.char": "keyword2",
    "string.dump": "keyword2",
    "string.find": "keyword2",
    "string.format": "keyword2",
    "string.gfind": "keyword2",
    "string.gsub": "keyword2",
    "string.len": "keyword2",
    "string.lower": "keyword2",
    "string.rep": "keyword2",
    "string.sub": "keyword2",
    "string.upper": "keyword2",
    "table.concat": "keyword2",
    "table.foreach": "keyword2",
    "table.foreachi": "keyword2",
    "table.getn": "keyword2",
    "table.insert": "keyword2",
    "table.remove": "keyword2",
    "table.setn": "keyword2",
    "table.sort": "keyword2",
    "then": "keyword1",
    "tonumber": "keyword2",
    "tostring": "keyword2",
    "true": "keyword3",
    "type": "keyword2",
    "unpack": "keyword2",
    "until": "keyword1",
    "while": "keyword1",
    "xpcall": "keyword2",
}

# Dictionary of keywords dictionaries for lua mode.
keywordsDictDict = {
    "lua_main": lua_main_keywords_dict,
}

# Rules for lua_main ruleset.

def lua_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="--[[", end="]]")

def lua_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def lua_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#!",
          at_line_start=True)

def lua_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def lua_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

# Leo issue #1175:
def lua_rule5(colorer, s, i):
    return colorer.match_lua_literal(s, i, kind="literal1")

def lua_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def lua_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def lua_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def lua_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def lua_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def lua_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="..")

def lua_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def lua_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def lua_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def lua_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def lua_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def lua_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~=")

def lua_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def lua_rule19(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def lua_rule20(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="{",
          exclude_match=True)

def lua_rule21(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="\"",
          exclude_match=True)

def lua_rule22(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="'",
          exclude_match=True)

def lua_rule23(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for lua_main ruleset.
rulesDict1 = {
    "\"": [lua_rule3, lua_rule21,],
    "#": [lua_rule2,],
    "'": [lua_rule4, lua_rule22,],
    "(": [lua_rule19,],
    "*": [lua_rule8,],
    "+": [lua_rule6,],
    "-": [lua_rule0, lua_rule1, lua_rule7,],
    ".": [lua_rule11, lua_rule23,],
    "/": [lua_rule9,],
    "0": [lua_rule23,],
    "1": [lua_rule23,],
    "2": [lua_rule23,],
    "3": [lua_rule23,],
    "4": [lua_rule23,],
    "5": [lua_rule23,],
    "6": [lua_rule23,],
    "7": [lua_rule23,],
    "8": [lua_rule23,],
    "9": [lua_rule23,],
    "<": [lua_rule12, lua_rule13,],
    "=": [lua_rule16, lua_rule18,],
    ">": [lua_rule14, lua_rule15,],
    "@": [lua_rule23,],
    "A": [lua_rule23,],
    "B": [lua_rule23,],
    "C": [lua_rule23,],
    "D": [lua_rule23,],
    "E": [lua_rule23,],
    "F": [lua_rule23,],
    "G": [lua_rule23,],
    "H": [lua_rule23,],
    "I": [lua_rule23,],
    "J": [lua_rule23,],
    "K": [lua_rule23,],
    "L": [lua_rule23,],
    "M": [lua_rule23,],
    "N": [lua_rule23,],
    "O": [lua_rule23,],
    "P": [lua_rule23,],
    "Q": [lua_rule23,],
    "R": [lua_rule23,],
    "S": [lua_rule23,],
    "T": [lua_rule23,],
    "U": [lua_rule23,],
    "V": [lua_rule23,],
    "W": [lua_rule23,],
    "X": [lua_rule23,],
    "Y": [lua_rule23,],
    "Z": [lua_rule23,],
    "[": [lua_rule5,],
    "^": [lua_rule10,],
    "_": [lua_rule23,],
    "a": [lua_rule23,],
    "b": [lua_rule23,],
    "c": [lua_rule23,],
    "d": [lua_rule23,],
    "e": [lua_rule23,],
    "f": [lua_rule23,],
    "g": [lua_rule23,],
    "h": [lua_rule23,],
    "i": [lua_rule23,],
    "j": [lua_rule23,],
    "k": [lua_rule23,],
    "l": [lua_rule23,],
    "m": [lua_rule23,],
    "n": [lua_rule23,],
    "o": [lua_rule23,],
    "p": [lua_rule23,],
    "q": [lua_rule23,],
    "r": [lua_rule23,],
    "s": [lua_rule23,],
    "t": [lua_rule23,],
    "u": [lua_rule23,],
    "v": [lua_rule23,],
    "w": [lua_rule23,],
    "x": [lua_rule23,],
    "y": [lua_rule23,],
    "z": [lua_rule23,],
    "{": [lua_rule20,],
    "~": [lua_rule17,],
}

# x.rulesDictDict for lua mode.
rulesDictDict = {
    "lua_main": rulesDict1,
}

# Import dict for lua mode.
importDict = {}

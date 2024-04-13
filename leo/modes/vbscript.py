# Leo colorizer control file for vbscript mode.
# This file is in the public domain.

# Properties for vbscript mode.
properties = {
    "lineComment": "'",
}

# Attributes dict for vbscript_main ruleset.
vbscript_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for vbscript mode.
attributesDictDict = {
    "vbscript_main": vbscript_main_attributes_dict,
}

# Keywords dict for vbscript_main ruleset.
vbscript_main_keywords_dict = {
    "abs": "keyword2",
    "adasyncexecute": "literal2",
    "adasyncfetch": "literal2",
    "adasyncfetchnonblocking": "literal2",
    "adbigint": "literal2",
    "adbinary": "literal2",
    "adboolean": "literal2",
    "adbstr": "literal2",
    "adchapter": "literal2",
    "adchar": "literal2",
    "adcmdfile": "literal2",
    "adcmdstoredproc": "literal2",
    "adcmdtable": "literal2",
    "adcmdtabledirect": "literal2",
    "adcmdtext": "literal2",
    "adcmdunknown": "literal2",
    "adcurrency": "literal2",
    "addate": "literal2",
    "addbdate": "literal2",
    "addbfiletime": "literal2",
    "addbtime": "literal2",
    "addbtimestamp": "literal2",
    "addecimal": "literal2",
    "addouble": "literal2",
    "adempty": "literal2",
    "aderror": "literal2",
    "adexecutenorecords": "literal2",
    "adfiletime": "literal2",
    "adguid": "literal2",
    "adidispatch": "literal2",
    "adinteger": "literal2",
    "adiunknown": "literal2",
    "adlockbatchoptimistic": "literal2",
    "adlockoptimistic": "literal2",
    "adlockpessimistic": "literal2",
    "adlockreadonly": "literal2",
    "adlongvarbinary": "literal2",
    "adlongvarchar": "literal2",
    "adlongvarwchar": "literal2",
    "adnumeric": "literal2",
    "adopendynamic": "literal2",
    "adopenforwardonly": "literal2",
    "adopenkeyset": "literal2",
    "adopenstatic": "literal2",
    "adparaminput": "literal2",
    "adparaminputoutput": "literal2",
    "adparamlong": "literal2",
    "adparamnullable": "literal2",
    "adparamoutput": "literal2",
    "adparamreturnvalue": "literal2",
    "adparamsigned": "literal2",
    "adparamunknown": "literal2",
    "adpersistadtg": "literal2",
    "adpersistxml": "literal2",
    "adpropvariant": "literal2",
    "adrunasync": "literal2",
    "adsingle": "literal2",
    "adsmallint": "literal2",
    "adstateclosed": "literal2",
    "adstateconnecting": "literal2",
    "adstateexecuting": "literal2",
    "adstatefetching": "literal2",
    "adstateopen": "literal2",
    "adtinyint": "literal2",
    "adunsignedbigint": "literal2",
    "adunsignedint": "literal2",
    "adunsignedsmallint": "literal2",
    "adunsignedtinyint": "literal2",
    "aduseclient": "literal2",
    "aduserdefined": "literal2",
    "aduseserver": "literal2",
    "advarbinary": "literal2",
    "advarchar": "literal2",
    "advariant": "literal2",
    "advarnumeric": "literal2",
    "advarwchar": "literal2",
    "adwchar": "literal2",
    "and": "operator",
    "array": "keyword2",
    "as": "keyword1",
    "asc": "keyword2",
    "ascb": "keyword2",
    "ascw": "keyword2",
    "atn": "keyword2",
    "byref": "keyword1",
    "byval": "keyword1",
    "call": "keyword1",
    "case": "keyword1",
    "cbool": "keyword2",
    "cbyte": "keyword2",
    "ccur": "keyword2",
    "cdate": "keyword2",
    "cdbl": "keyword2",
    "chr": "keyword2",
    "chrb": "keyword2",
    "chrw": "keyword2",
    "cint": "keyword2",
    "class": "keyword1",
    "clng": "keyword2",
    "const": "keyword1",
    "cos": "keyword2",
    "createobject": "keyword2",
    "csng": "keyword2",
    "cstr": "keyword2",
    "date": "keyword2",
    "dateadd": "keyword2",
    "datediff": "keyword2",
    "datepart": "keyword2",
    "dateserial": "keyword2",
    "datevalue": "keyword2",
    "day": "keyword2",
    "default": "keyword1",
    "dim": "keyword1",
    "do": "keyword1",
    "each": "keyword1",
    "else": "keyword1",
    "elseif": "keyword1",
    "empty": "keyword3",
    "end": "keyword1",
    "erase": "keyword1",
    "err": "keyword2",
    "error": "keyword1",
    "eval": "keyword1",
    "execute": "keyword1",
    "exit": "keyword1",
    "exp": "keyword2",
    "explicit": "keyword1",
    "false": "keyword3",
    "filter": "keyword2",
    "fix": "keyword2",
    "for": "keyword1",
    "formatcurrency": "keyword2",
    "formatdatetime": "keyword2",
    "formatnumber": "keyword2",
    "formatpercent": "keyword2",
    "function": "keyword1",
    "get": "keyword1",
    "getobject": "keyword2",
    "getref": "keyword2",
    "goto": "keyword1",
    "hex": "keyword2",
    "hour": "keyword2",
    "if": "keyword1",
    "imp": "operator",
    "in": "keyword1",
    "inputbox": "keyword2",
    "instr": "keyword2",
    "instrb": "keyword2",
    "instrrev": "keyword2",
    "int": "keyword2",
    "is": "operator",
    "isarray": "keyword2",
    "isdate": "keyword2",
    "isempty": "keyword2",
    "isnull": "keyword2",
    "isnumeric": "keyword2",
    "isobject": "keyword2",
    "join": "keyword2",
    "lbound": "keyword2",
    "lcase": "keyword2",
    "left": "keyword2",
    "leftb": "keyword2",
    "len": "keyword2",
    "lenb": "keyword2",
    "let": "keyword1",
    "loadpicture": "keyword2",
    "log": "keyword2",
    "loop": "keyword1",
    "ltrim": "keyword2",
    "mid": "keyword2",
    "midb": "keyword2",
    "minute": "keyword2",
    "mod": "operator",
    "month": "keyword2",
    "monthname": "keyword2",
    "msgbox": "keyword2",
    "new": "keyword1",
    "next": "keyword1",
    "not": "operator",
    "nothing": "keyword3",
    "now": "keyword2",
    "null": "keyword3",
    "oct": "keyword2",
    "on": "keyword1",
    "option": "keyword1",
    "or": "operator",
    "preserve": "keyword1",
    "private": "keyword1",
    "property": "keyword1",
    "public": "keyword1",
    "randomize": "keyword1",
    "redim": "keyword1",
    "rem": "keyword1",
    "replace": "keyword2",
    "resume": "keyword1",
    "rgb": "keyword2",
    "right": "keyword2",
    "rightb": "keyword2",
    "rnd": "keyword2",
    "round": "keyword2",
    "rtrim": "keyword2",
    "scriptengine": "keyword2",
    "scriptenginebuildversion": "keyword2",
    "scriptenginemajorversion": "keyword2",
    "scriptengineminorversion": "keyword2",
    "second": "keyword2",
    "select": "keyword1",
    "set": "keyword1",
    "sgn": "keyword2",
    "sin": "keyword2",
    "space": "keyword2",
    "split": "keyword2",
    "sqr": "keyword2",
    "step": "keyword1",
    "strcomp": "keyword2",
    "string": "keyword2",
    "strreverse": "keyword2",
    "sub": "keyword1",
    "tan": "keyword2",
    "then": "keyword1",
    "time": "keyword2",
    "timeserial": "keyword2",
    "timevalue": "keyword2",
    "to": "keyword1",
    "trim": "keyword2",
    "true": "keyword3",
    "typename": "keyword2",
    "ubound": "keyword2",
    "ucase": "keyword2",
    "until": "keyword1",
    "vartype": "keyword2",
    "vbabort": "literal2",
    "vbabortretryignore": "literal2",
    "vbapplicationmodal": "literal2",
    "vbarray": "literal2",
    "vbblack": "literal2",
    "vbblue": "literal2",
    "vbboolean": "literal2",
    "vbbyte": "literal2",
    "vbcancel": "literal2",
    "vbcr": "literal2",
    "vbcritical": "literal2",
    "vbcrlf": "literal2",
    "vbcurrency": "literal2",
    "vbcyan": "literal2",
    "vbdataobject": "literal2",
    "vbdate": "literal2",
    "vbdecimal": "literal2",
    "vbdefaultbutton1": "literal2",
    "vbdefaultbutton2": "literal2",
    "vbdefaultbutton3": "literal2",
    "vbdefaultbutton4": "literal2",
    "vbdouble": "literal2",
    "vbempty": "literal2",
    "vberror": "literal2",
    "vbexclamation": "literal2",
    "vbfalse": "literal2",
    "vbformfeed": "literal2",
    "vbgeneraldate": "literal2",
    "vbgreen": "literal2",
    "vbignore": "literal2",
    "vbinformation": "literal2",
    "vbinteger": "literal2",
    "vblf": "literal2",
    "vblong": "literal2",
    "vblongdate": "literal2",
    "vblongtime": "literal2",
    "vbmagenta": "literal2",
    "vbnewline": "literal2",
    "vbno": "literal2",
    "vbnull": "literal2",
    "vbnullchar": "literal2",
    "vbnullstring": "literal2",
    "vbobject": "literal2",
    "vbobjecterror": "literal2",
    "vbok": "literal2",
    "vbokcancel": "literal2",
    "vbokonly": "literal2",
    "vbquestion": "literal2",
    "vbred": "literal2",
    "vbretry": "literal2",
    "vbretrycancel": "literal2",
    "vbshortdate": "literal2",
    "vbshorttime": "literal2",
    "vbsingle": "literal2",
    "vbstring": "literal2",
    "vbsystemmodal": "literal2",
    "vbtab": "literal2",
    "vbtrue": "literal2",
    "vbusedefault": "literal2",
    "vbvariant": "literal2",
    "vbverticaltab": "literal2",
    "vbwhite": "literal2",
    "vbyellow": "literal2",
    "vbyes": "literal2",
    "vbyesno": "literal2",
    "vbyesnocancel": "literal2",
    "weekday": "keyword2",
    "weekdayname": "keyword2",
    "wend": "keyword1",
    "while": "keyword1",
    "with": "keyword1",
    "xor": "operator",
    "year": "keyword2",
}

# Dictionary of keywords dictionaries for vbscript mode.
keywordsDictDict = {
    "vbscript_main": vbscript_main_keywords_dict,
}

# Rules for vbscript_main ruleset.

def vbscript_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def vbscript_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#if")

def vbscript_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#else")

def vbscript_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#end")

def vbscript_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="'")

def vbscript_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="rem")

def vbscript_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def vbscript_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def vbscript_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def vbscript_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def vbscript_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def vbscript_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def vbscript_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def vbscript_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def vbscript_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def vbscript_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def vbscript_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def vbscript_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def vbscript_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def vbscript_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def vbscript_rule20(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_line_start=True,
          exclude_match=True)

def vbscript_rule21(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for vbscript_main ruleset.
rulesDict1 = {
    "\"": [vbscript_rule0,],
    "#": [vbscript_rule1, vbscript_rule2, vbscript_rule3,],
    "&": [vbscript_rule19,],
    "'": [vbscript_rule4,],
    "*": [vbscript_rule15,],
    "+": [vbscript_rule13,],
    "-": [vbscript_rule14,],
    ".": [vbscript_rule12,],
    "/": [vbscript_rule16,],
    "0": [vbscript_rule21,],
    "1": [vbscript_rule21,],
    "2": [vbscript_rule21,],
    "3": [vbscript_rule21,],
    "4": [vbscript_rule21,],
    "5": [vbscript_rule21,],
    "6": [vbscript_rule21,],
    "7": [vbscript_rule21,],
    "8": [vbscript_rule21,],
    "9": [vbscript_rule21,],
    ":": [vbscript_rule20,],
    "<": [vbscript_rule6, vbscript_rule7, vbscript_rule11,],
    "=": [vbscript_rule10,],
    ">": [vbscript_rule8, vbscript_rule9,],
    "@": [vbscript_rule21,],
    "A": [vbscript_rule21,],
    "B": [vbscript_rule21,],
    "C": [vbscript_rule21,],
    "D": [vbscript_rule21,],
    "E": [vbscript_rule21,],
    "F": [vbscript_rule21,],
    "G": [vbscript_rule21,],
    "H": [vbscript_rule21,],
    "I": [vbscript_rule21,],
    "J": [vbscript_rule21,],
    "K": [vbscript_rule21,],
    "L": [vbscript_rule21,],
    "M": [vbscript_rule21,],
    "N": [vbscript_rule21,],
    "O": [vbscript_rule21,],
    "P": [vbscript_rule21,],
    "Q": [vbscript_rule21,],
    "R": [vbscript_rule21,],
    "S": [vbscript_rule21,],
    "T": [vbscript_rule21,],
    "U": [vbscript_rule21,],
    "V": [vbscript_rule21,],
    "W": [vbscript_rule21,],
    "X": [vbscript_rule21,],
    "Y": [vbscript_rule21,],
    "Z": [vbscript_rule21,],
    "\\": [vbscript_rule17,],
    "^": [vbscript_rule18,],
    "a": [vbscript_rule21,],
    "b": [vbscript_rule21,],
    "c": [vbscript_rule21,],
    "d": [vbscript_rule21,],
    "e": [vbscript_rule21,],
    "f": [vbscript_rule21,],
    "g": [vbscript_rule21,],
    "h": [vbscript_rule21,],
    "i": [vbscript_rule21,],
    "j": [vbscript_rule21,],
    "k": [vbscript_rule21,],
    "l": [vbscript_rule21,],
    "m": [vbscript_rule21,],
    "n": [vbscript_rule21,],
    "o": [vbscript_rule21,],
    "p": [vbscript_rule21,],
    "q": [vbscript_rule21,],
    "r": [vbscript_rule5, vbscript_rule21,],
    "s": [vbscript_rule21,],
    "t": [vbscript_rule21,],
    "u": [vbscript_rule21,],
    "v": [vbscript_rule21,],
    "w": [vbscript_rule21,],
    "x": [vbscript_rule21,],
    "y": [vbscript_rule21,],
    "z": [vbscript_rule21,],
}

# x.rulesDictDict for vbscript mode.
rulesDictDict = {
    "vbscript_main": rulesDict1,
}

# Import dict for vbscript mode.
importDict = {}

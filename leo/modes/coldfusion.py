# Leo colorizer control file for coldfusion mode.
# This file is in the public domain.

# Properties for coldfusion mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for coldfusion_main ruleset.
coldfusion_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for coldfusion_tags ruleset.
coldfusion_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for coldfusion_cfscript ruleset.
coldfusion_cfscript_attributes_dict = {
    "default": "KEYWORD1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for coldfusion_cftags ruleset.
coldfusion_cftags_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for coldfusion mode.
attributesDictDict = {
    "coldfusion_cfscript": coldfusion_cfscript_attributes_dict,
    "coldfusion_cftags": coldfusion_cftags_attributes_dict,
    "coldfusion_main": coldfusion_main_attributes_dict,
    "coldfusion_tags": coldfusion_tags_attributes_dict,
}

# Keywords dict for coldfusion_main ruleset.
coldfusion_main_keywords_dict = {}

# Keywords dict for coldfusion_tags ruleset.
coldfusion_tags_keywords_dict = {}

# Keywords dict for coldfusion_cfscript ruleset.
coldfusion_cfscript_keywords_dict = {
    "abs": "function",
    "arrayappend": "function",
    "arrayavg": "function",
    "arrayclear": "function",
    "arraydeleteat": "function",
    "arrayinsertat": "function",
    "arrayisempty": "function",
    "arraylen": "function",
    "arraymax": "function",
    "arraymin": "function",
    "arraynew": "function",
    "arrayprepend": "function",
    "arrayresize": "function",
    "arrayset": "function",
    "arraysort": "function",
    "arraysum": "function",
    "arrayswap": "function",
    "arraytolist": "function",
    "asc": "function",
    "atn": "function",
    "bitand": "function",
    "bitmaskclear": "function",
    "bitmaskread": "function",
    "bitmaskset": "function",
    "bitnot": "function",
    "bitor": "function",
    "bitshln": "function",
    "bitshrn": "function",
    "bitxor": "function",
    "break": "function",
    "ceiling": "function",
    "chr": "function",
    "cjustify": "function",
    "compare": "function",
    "comparenocase": "function",
    "cos": "function",
    "createdate": "function",
    "createdatetime": "function",
    "createodbcdate": "function",
    "createodbcdatetime": "function",
    "createodbctime": "function",
    "createtime": "function",
    "createtimespan": "function",
    "dateadd": "function",
    "datecompare": "function",
    "datediff": "function",
    "dateformat": "function",
    "datepart": "function",
    "day": "function",
    "dayofweek": "function",
    "dayofweekasstring": "function",
    "dayofyear": "function",
    "daysinmonth": "function",
    "daysinyear": "function",
    "de": "function",
    "decimalformat": "function",
    "decrementvalue": "function",
    "decrypt": "function",
    "deleteclientvariable": "function",
    "directoryexists": "function",
    "dollarformat": "function",
    "else": "function",
    "encrypt": "function",
    "evaluate": "function",
    "exp": "function",
    "expandpath": "function",
    "fileexists": "function",
    "find": "function",
    "findnocase": "function",
    "findoneof": "function",
    "firstdayofmonth": "function",
    "fix": "function",
    "for": "function",
    "formatbasen": "function",
    "getbasetagdata": "function",
    "getbasetaglist": "function",
    "getclientvariableslist": "function",
    "getdirectoryfrompath": "function",
    "getfilefrompath": "function",
    "getlocale": "function",
    "gettempdirectory": "function",
    "gettempfile": "function",
    "gettemplatepath": "function",
    "gettickcount": "function",
    "gettoken": "function",
    "hour": "function",
    "htmlcodeformat": "function",
    "htmleditformat": "function",
    "if": "function",
    "if(": "function",
    "iif": "function",
    "incrementvalue": "function",
    "inputbasen": "function",
    "insert": "function",
    "int": "function",
    "isarray": "function",
    "isauthenticated": "function",
    "isauthorized": "function",
    "isboolean": "function",
    "isdate": "function",
    "isdebugmode": "function",
    "isdefined": "function",
    "isleapyear": "function",
    "isnumeric": "function",
    "isnumericdate": "function",
    "isquery": "function",
    "issimplevalue": "function",
    "isstruct": "function",
    "lcase": "function",
    "left": "function",
    "len": "function",
    "listappend": "function",
    "listchangedelims": "function",
    "listcontains": "function",
    "listcontainsnocase": "function",
    "listdeleteat": "function",
    "listfind": "function",
    "listfindnocase": "function",
    "listfirst": "function",
    "listgetat": "function",
    "listinsertat": "function",
    "listlast": "function",
    "listlen": "function",
    "listprepend": "function",
    "listrest": "function",
    "listsetat": "function",
    "listtoarray": "function",
    "ljustify": "function",
    "log": "function",
    "log10": "function",
    "lscurrencyformat": "function",
    "lsdateformat": "function",
    "lsiscurrency": "function",
    "lsisdate": "function",
    "lsisnumeric": "function",
    "lsnumberformat": "function",
    "lsparsecurrency": "function",
    "lsparsedatetime": "function",
    "lsparsenumber": "function",
    "lstimeformat": "function",
    "ltrim": "function",
    "max": "function",
    "mid": "function",
    "min": "function",
    "minute": "function",
    "month": "function",
    "monthasstring": "function",
    "now": "function",
    "numberformat": "function",
    "paragraphformat": "function",
    "parameterexists": "function",
    "parsedatetime": "function",
    "pi": "function",
    "preservesinglequotes": "function",
    "quarter": "function",
    "queryaddrow": "function",
    "querynew": "function",
    "querysetcell": "function",
    "quotedvaluelist": "function",
    "rand": "function",
    "randomize": "function",
    "randrange": "function",
    "refind": "function",
    "refindnocase": "function",
    "removechars": "function",
    "repeatstring": "function",
    "replace": "function",
    "replacelist": "function",
    "replacenocase": "function",
    "rereplace": "function",
    "rereplacenocase": "function",
    "reverse": "function",
    "right": "function",
    "rjustify": "function",
    "round": "function",
    "rtrim": "function",
    "second": "function",
    "setlocale": "function",
    "setvariable": "function",
    "sgn": "function",
    "sin": "function",
    "spanexcluding": "function",
    "spanincluding": "function",
    "sqr": "function",
    "stripcr": "function",
    "structclear": "function",
    "structcopy": "function",
    "structcount": "function",
    "structdelete": "function",
    "structfind": "function",
    "structinsert": "function",
    "structisempty": "function",
    "structkeyexists": "function",
    "structnew": "function",
    "structupdate": "function",
    "tan": "function",
    "timeformat": "function",
    "trim": "function",
    "ucase": "function",
    "urlencodedformat": "function",
    "val": "function",
    "valuelist": "function",
    "week": "function",
    "while": "function",
    "writeoutput": "function",
    "year": "function",
    "yesnoformat": "function",
    "{": "function",
    "}": "function",
    "}else": "function",
    "}else{": "function",
}

# Keywords dict for coldfusion_cftags ruleset.
coldfusion_cftags_keywords_dict = {
    "abs": "keyword2",
    "and": "operator",
    "arrayappend": "keyword2",
    "arrayavg": "keyword2",
    "arrayclear": "keyword2",
    "arraydeleteat": "keyword2",
    "arrayinsertat": "keyword2",
    "arrayisempty": "keyword2",
    "arraylen": "keyword2",
    "arraymax": "keyword2",
    "arraymin": "keyword2",
    "arraynew": "keyword2",
    "arrayprepend": "keyword2",
    "arrayresize": "keyword2",
    "arrayset": "keyword2",
    "arraysort": "keyword2",
    "arraysum": "keyword2",
    "arrayswap": "keyword2",
    "arraytolist": "keyword2",
    "asc": "keyword2",
    "atn": "keyword2",
    "bitand": "keyword2",
    "bitmaskclear": "keyword2",
    "bitmaskread": "keyword2",
    "bitmaskset": "keyword2",
    "bitnot": "keyword2",
    "bitor": "keyword2",
    "bitshln": "keyword2",
    "bitshrn": "keyword2",
    "bitxor": "keyword2",
    "ceiling": "keyword2",
    "chr": "keyword2",
    "cjustify": "keyword2",
    "compare": "keyword2",
    "comparenocase": "keyword2",
    "cos": "keyword2",
    "createdate": "keyword2",
    "createdatetime": "keyword2",
    "createodbcdate": "keyword2",
    "createodbcdatetime": "keyword2",
    "createodbctime": "keyword2",
    "createtime": "keyword2",
    "createtimespan": "keyword2",
    "dateadd": "keyword2",
    "datecompare": "keyword2",
    "datediff": "keyword2",
    "dateformat": "keyword2",
    "datepart": "keyword2",
    "day": "keyword2",
    "dayofweek": "keyword2",
    "dayofweekasstring": "keyword2",
    "dayofyear": "keyword2",
    "daysinmonth": "keyword2",
    "daysinyear": "keyword2",
    "de": "keyword2",
    "decimalformat": "keyword2",
    "decrementvalue": "keyword2",
    "decrypt": "keyword2",
    "deleteclientvariable": "keyword2",
    "directoryexists": "keyword2",
    "dollarformat": "keyword2",
    "encrypt": "keyword2",
    "eq": "operator",
    "evaluate": "keyword2",
    "exp": "keyword2",
    "expandpath": "keyword2",
    "fileexists": "keyword2",
    "find": "keyword2",
    "findnocase": "keyword2",
    "findoneof": "keyword2",
    "firstdayofmonth": "keyword2",
    "fix": "keyword2",
    "formatbasen": "keyword2",
    "getbasetagdata": "keyword2",
    "getbasetaglist": "keyword2",
    "getclientvariableslist": "keyword2",
    "getdirectoryfrompath": "keyword2",
    "getfilefrompath": "keyword2",
    "getlocale": "keyword2",
    "gettempdirectory": "keyword2",
    "gettempfile": "keyword2",
    "gettemplatepath": "keyword2",
    "gettickcount": "keyword2",
    "gettoken": "keyword2",
    "greater": "operator",
    "gt": "operator",
    "gte": "operator",
    "hour": "keyword2",
    "htmlcodeformat": "keyword2",
    "htmleditformat": "keyword2",
    "iif": "keyword2",
    "incrementvalue": "keyword2",
    "inputbasen": "keyword2",
    "insert": "keyword2",
    "int": "keyword2",
    "is": "operator",
    "isarray": "keyword2",
    "isauthenticated": "keyword2",
    "isauthorized": "keyword2",
    "isboolean": "keyword2",
    "isdate": "keyword2",
    "isdebugmode": "keyword2",
    "isdefined": "keyword2",
    "isleapyear": "keyword2",
    "isnumeric": "keyword2",
    "isnumericdate": "keyword2",
    "isquery": "keyword2",
    "issimplevalue": "keyword2",
    "isstruct": "keyword2",
    "lcase": "keyword2",
    "left": "keyword2",
    "len": "keyword2",
    "less": "operator",
    "listappend": "keyword2",
    "listchangedelims": "keyword2",
    "listcontains": "keyword2",
    "listcontainsnocase": "keyword2",
    "listdeleteat": "keyword2",
    "listfind": "keyword2",
    "listfindnocase": "keyword2",
    "listfirst": "keyword2",
    "listgetat": "keyword2",
    "listinsertat": "keyword2",
    "listlast": "keyword2",
    "listlen": "keyword2",
    "listprepend": "keyword2",
    "listrest": "keyword2",
    "listsetat": "keyword2",
    "listtoarray": "keyword2",
    "ljustify": "keyword2",
    "log": "keyword2",
    "log10": "keyword2",
    "lscurrencyformat": "keyword2",
    "lsdateformat": "keyword2",
    "lsiscurrency": "keyword2",
    "lsisdate": "keyword2",
    "lsisnumeric": "keyword2",
    "lsnumberformat": "keyword2",
    "lsparsecurrency": "keyword2",
    "lsparsedatetime": "keyword2",
    "lsparsenumber": "keyword2",
    "lstimeformat": "keyword2",
    "lt": "operator",
    "lte": "operator",
    "ltrim": "keyword2",
    "max": "keyword2",
    "mid": "keyword2",
    "min": "keyword2",
    "minute": "keyword2",
    "month": "keyword2",
    "monthasstring": "keyword2",
    "neq": "operator",
    "not": "operator",
    "now": "keyword2",
    "numberformat": "keyword2",
    "or": "operator",
    "paragraphformat": "keyword2",
    "parameterexists": "keyword2",
    "parsedatetime": "keyword2",
    "pi": "keyword2",
    "preservesinglequotes": "keyword2",
    "quarter": "keyword2",
    "queryaddrow": "keyword2",
    "querynew": "keyword2",
    "querysetcell": "keyword2",
    "quotedvaluelist": "keyword2",
    "rand": "keyword2",
    "randomize": "keyword2",
    "randrange": "keyword2",
    "refind": "keyword2",
    "refindnocase": "keyword2",
    "removechars": "keyword2",
    "repeatstring": "keyword2",
    "replace": "keyword2",
    "replacelist": "keyword2",
    "replacenocase": "keyword2",
    "rereplace": "keyword2",
    "rereplacenocase": "keyword2",
    "reverse": "keyword2",
    "right": "keyword2",
    "rjustify": "keyword2",
    "round": "keyword2",
    "rtrim": "keyword2",
    "second": "keyword2",
    "setlocale": "keyword2",
    "setvariable": "keyword2",
    "sgn": "keyword2",
    "sin": "keyword2",
    "spanexcluding": "keyword2",
    "spanincluding": "keyword2",
    "sqr": "keyword2",
    "stripcr": "keyword2",
    "structclear": "keyword2",
    "structcopy": "keyword2",
    "structcount": "keyword2",
    "structdelete": "keyword2",
    "structfind": "keyword2",
    "structinsert": "keyword2",
    "structisempty": "keyword2",
    "structkeyexists": "keyword2",
    "structnew": "keyword2",
    "structupdate": "keyword2",
    "tan": "keyword2",
    "than": "operator",
    "timeformat": "keyword2",
    "trim": "keyword2",
    "ucase": "keyword2",
    "urlencodedformat": "keyword2",
    "val": "keyword2",
    "valuelist": "keyword2",
    "week": "keyword2",
    "writeoutput": "keyword2",
    "xor": "operator",
    "year": "keyword2",
    "yesnoformat": "keyword2",
}

# Dictionary of keywords dictionaries for coldfusion mode.
keywordsDictDict = {
    "coldfusion_cfscript": coldfusion_cfscript_keywords_dict,
    "coldfusion_cftags": coldfusion_cftags_keywords_dict,
    "coldfusion_main": coldfusion_main_keywords_dict,
    "coldfusion_tags": coldfusion_tags_keywords_dict,
}

# Rules for coldfusion_main ruleset.

def coldfusion_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment4", begin="<!---", end="--->")

def coldfusion_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def coldfusion_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def coldfusion_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="<!--", end="-->")

def coldfusion_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="<CFSCRIPT", end="</CFSCRIPT>",
          delegate="coldfusion::cfscript")

def coldfusion_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="<CF", end=">",
          delegate="coldfusion::cftags")

def coldfusion_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="</CF", end=">",
          delegate="coldfusion::cftags")

def coldfusion_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
          delegate="html::javascript")

def coldfusion_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
          delegate="html::css")

def coldfusion_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="coldfusion::tags")

def coldfusion_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for coldfusion_main ruleset.
rulesDict1 = {
    "&": [coldfusion_rule10,],
    "/": [coldfusion_rule1, coldfusion_rule2,],
    "<": [coldfusion_rule0, coldfusion_rule3, coldfusion_rule4, coldfusion_rule5, coldfusion_rule6, coldfusion_rule7, coldfusion_rule8, coldfusion_rule9,],
}

# Rules for coldfusion_tags ruleset.

def coldfusion_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def coldfusion_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def coldfusion_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def coldfusion_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="<CF", end=">",
          delegate="coldfusion::cftags")

def coldfusion_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="</CF", end=">",
          delegate="coldfusion::cftags")

def coldfusion_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="<CFSCRIPT", end="</CFSCRIPT>",
          delegate="coldfusion::cfscript")

# Rules dict for coldfusion_tags ruleset.
rulesDict2 = {
    "\"": [coldfusion_rule11,],
    "'": [coldfusion_rule12,],
    "<": [coldfusion_rule14, coldfusion_rule15, coldfusion_rule16,],
    "=": [coldfusion_rule13,],
}

# Rules for coldfusion_cfscript ruleset.

def coldfusion_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def coldfusion_rule18(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def coldfusion_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="\"", end="\"")

def coldfusion_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="'", end="'")

def coldfusion_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal2", seq="(")

def coldfusion_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal2", seq=")")

def coldfusion_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def coldfusion_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def coldfusion_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def coldfusion_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def coldfusion_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def coldfusion_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def coldfusion_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="><")

def coldfusion_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def coldfusion_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!!")

def coldfusion_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&&")

def coldfusion_rule33(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for coldfusion_cfscript ruleset.
rulesDict3 = {
    "!": [coldfusion_rule31,],
    "\"": [coldfusion_rule19,],
    "&": [coldfusion_rule32,],
    "'": [coldfusion_rule20,],
    "(": [coldfusion_rule21, coldfusion_rule33,],
    ")": [coldfusion_rule22,],
    "*": [coldfusion_rule30,],
    "+": [coldfusion_rule24,],
    "-": [coldfusion_rule25,],
    "/": [coldfusion_rule17, coldfusion_rule18, coldfusion_rule26,],
    "0": [coldfusion_rule33,],
    "1": [coldfusion_rule33,],
    "2": [coldfusion_rule33,],
    "3": [coldfusion_rule33,],
    "4": [coldfusion_rule33,],
    "5": [coldfusion_rule33,],
    "6": [coldfusion_rule33,],
    "7": [coldfusion_rule33,],
    "8": [coldfusion_rule33,],
    "9": [coldfusion_rule33,],
    "<": [coldfusion_rule28,],
    "=": [coldfusion_rule23,],
    ">": [coldfusion_rule27, coldfusion_rule29,],
    "@": [coldfusion_rule33,],
    "A": [coldfusion_rule33,],
    "B": [coldfusion_rule33,],
    "C": [coldfusion_rule33,],
    "D": [coldfusion_rule33,],
    "E": [coldfusion_rule33,],
    "F": [coldfusion_rule33,],
    "G": [coldfusion_rule33,],
    "H": [coldfusion_rule33,],
    "I": [coldfusion_rule33,],
    "J": [coldfusion_rule33,],
    "K": [coldfusion_rule33,],
    "L": [coldfusion_rule33,],
    "M": [coldfusion_rule33,],
    "N": [coldfusion_rule33,],
    "O": [coldfusion_rule33,],
    "P": [coldfusion_rule33,],
    "Q": [coldfusion_rule33,],
    "R": [coldfusion_rule33,],
    "S": [coldfusion_rule33,],
    "T": [coldfusion_rule33,],
    "U": [coldfusion_rule33,],
    "V": [coldfusion_rule33,],
    "W": [coldfusion_rule33,],
    "X": [coldfusion_rule33,],
    "Y": [coldfusion_rule33,],
    "Z": [coldfusion_rule33,],
    "a": [coldfusion_rule33,],
    "b": [coldfusion_rule33,],
    "c": [coldfusion_rule33,],
    "d": [coldfusion_rule33,],
    "e": [coldfusion_rule33,],
    "f": [coldfusion_rule33,],
    "g": [coldfusion_rule33,],
    "h": [coldfusion_rule33,],
    "i": [coldfusion_rule33,],
    "j": [coldfusion_rule33,],
    "k": [coldfusion_rule33,],
    "l": [coldfusion_rule33,],
    "m": [coldfusion_rule33,],
    "n": [coldfusion_rule33,],
    "o": [coldfusion_rule33,],
    "p": [coldfusion_rule33,],
    "q": [coldfusion_rule33,],
    "r": [coldfusion_rule33,],
    "s": [coldfusion_rule33,],
    "t": [coldfusion_rule33,],
    "u": [coldfusion_rule33,],
    "v": [coldfusion_rule33,],
    "w": [coldfusion_rule33,],
    "x": [coldfusion_rule33,],
    "y": [coldfusion_rule33,],
    "z": [coldfusion_rule33,],
    "{": [coldfusion_rule33,],
    "}": [coldfusion_rule33,],
}

# Rules for coldfusion_cftags ruleset.

def coldfusion_rule34(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def coldfusion_rule35(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def coldfusion_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def coldfusion_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="##")

def coldfusion_rule38(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="#", end="#")

def coldfusion_rule39(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for coldfusion_cftags ruleset.
rulesDict4 = {
    "\"": [coldfusion_rule34,],
    "#": [coldfusion_rule37, coldfusion_rule38,],
    "'": [coldfusion_rule35,],
    "(": [coldfusion_rule39,],
    "0": [coldfusion_rule39,],
    "1": [coldfusion_rule39,],
    "2": [coldfusion_rule39,],
    "3": [coldfusion_rule39,],
    "4": [coldfusion_rule39,],
    "5": [coldfusion_rule39,],
    "6": [coldfusion_rule39,],
    "7": [coldfusion_rule39,],
    "8": [coldfusion_rule39,],
    "9": [coldfusion_rule39,],
    "=": [coldfusion_rule36,],
    "@": [coldfusion_rule39,],
    "A": [coldfusion_rule39,],
    "B": [coldfusion_rule39,],
    "C": [coldfusion_rule39,],
    "D": [coldfusion_rule39,],
    "E": [coldfusion_rule39,],
    "F": [coldfusion_rule39,],
    "G": [coldfusion_rule39,],
    "H": [coldfusion_rule39,],
    "I": [coldfusion_rule39,],
    "J": [coldfusion_rule39,],
    "K": [coldfusion_rule39,],
    "L": [coldfusion_rule39,],
    "M": [coldfusion_rule39,],
    "N": [coldfusion_rule39,],
    "O": [coldfusion_rule39,],
    "P": [coldfusion_rule39,],
    "Q": [coldfusion_rule39,],
    "R": [coldfusion_rule39,],
    "S": [coldfusion_rule39,],
    "T": [coldfusion_rule39,],
    "U": [coldfusion_rule39,],
    "V": [coldfusion_rule39,],
    "W": [coldfusion_rule39,],
    "X": [coldfusion_rule39,],
    "Y": [coldfusion_rule39,],
    "Z": [coldfusion_rule39,],
    "a": [coldfusion_rule39,],
    "b": [coldfusion_rule39,],
    "c": [coldfusion_rule39,],
    "d": [coldfusion_rule39,],
    "e": [coldfusion_rule39,],
    "f": [coldfusion_rule39,],
    "g": [coldfusion_rule39,],
    "h": [coldfusion_rule39,],
    "i": [coldfusion_rule39,],
    "j": [coldfusion_rule39,],
    "k": [coldfusion_rule39,],
    "l": [coldfusion_rule39,],
    "m": [coldfusion_rule39,],
    "n": [coldfusion_rule39,],
    "o": [coldfusion_rule39,],
    "p": [coldfusion_rule39,],
    "q": [coldfusion_rule39,],
    "r": [coldfusion_rule39,],
    "s": [coldfusion_rule39,],
    "t": [coldfusion_rule39,],
    "u": [coldfusion_rule39,],
    "v": [coldfusion_rule39,],
    "w": [coldfusion_rule39,],
    "x": [coldfusion_rule39,],
    "y": [coldfusion_rule39,],
    "z": [coldfusion_rule39,],
    "{": [coldfusion_rule39,],
    "}": [coldfusion_rule39,],
}

# x.rulesDictDict for coldfusion mode.
rulesDictDict = {
    "coldfusion_cfscript": rulesDict3,
    "coldfusion_cftags": rulesDict4,
    "coldfusion_main": rulesDict1,
    "coldfusion_tags": rulesDict2,
}

# Import dict for coldfusion mode.
importDict = {}

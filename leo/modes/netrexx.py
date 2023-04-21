# Leo colorizer control file for netrexx mode.
# This file is in the public domain.

# Properties for netrexx mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentNextLines": "\\s*(if|loop|do|else|select|otherwise|catch|finally|class|method|properties)(.*)",
    "lineComment": "--",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for netrexx_main ruleset.
netrexx_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for netrexx mode.
attributesDictDict = {
    "netrexx_main": netrexx_main_attributes_dict,
}

# Keywords dict for netrexx_main ruleset.
netrexx_main_keywords_dict = {
    "abbrev": "function",
    "abs": "function",
    "abstract": "keyword1",
    "adapter": "keyword1",
    "all": "keyword3",
    "arithmeticexception": "markup",
    "arrayindexoutofboundsexception": "markup",
    "arraylist": "label",
    "arraystoreexception": "markup",
    "ask": "keyword3",
    "b2x": "function",
    "badargumentexception": "markup",
    "badcolumnexception": "markup",
    "badnumericexception": "markup",
    "bigdecimal": "label",
    "biginteger": "label",
    "binary": "literal2",
    "boolean": "label",
    "bufferedinputstream": "label",
    "bufferedoutputstream": "label",
    "bufferedreader": "label",
    "bufferedwriter": "label",
    "by": "keyword2",
    "byte": "label",
    "bytearrayinputstream": "label",
    "bytearrayoutputstream": "label",
    "c2d": "function",
    "c2x": "function",
    "calendar": "label",
    "case": "keyword2",
    "catch": "keyword2",
    "center": "function",
    "centre": "function",
    "changestr": "function",
    "char": "label",
    "character": "label",
    "chararrayreader": "label",
    "chararraywriter": "label",
    "charat": "function",
    "charconversionexception": "markup",
    "class": "keyword1",
    "classcastexception": "markup",
    "classnotfoundexception": "markup",
    "clonenotsupportedexception": "markup",
    "comments": "literal2",
    "compact": "literal2",
    "compare": "function",
    "concurrentmodificationexception": "label",
    "console": "literal2",
    "constant": "keyword1",
    "copies": "function",
    "copyindexed": "function",
    "countstr": "function",
    "crossref": "literal2",
    "d2c": "function",
    "d2x": "function",
    "datainputstream": "label",
    "dataoutputstream": "label",
    "datatype": "function",
    "date": "label",
    "decimal": "literal2",
    "delstr": "function",
    "delword": "function",
    "dependent": "keyword1",
    "deprecated": "keyword1",
    "diag": "literal2",
    "digits": "keyword3",
    "divideexception": "markup",
    "do": "keyword2",
    "double": "label",
    "else": "keyword2",
    "end": "keyword2",
    "engineering": "keyword3",
    "eofexception": "markup",
    "equals": "function",
    "exception": "markup",
    "exists": "function",
    "exit": "keyword2",
    "explicit": "literal2",
    "exponentoverflowexception": "markup",
    "extends": "keyword1",
    "file": "label",
    "filedescriptor": "label",
    "fileinputstream": "label",
    "filenotfoundexception": "markup",
    "fileoutputstream": "label",
    "filepermission": "label",
    "filereader": "label",
    "filewriter": "label",
    "filterinputstream": "label",
    "filteroutputstream": "label",
    "filterreader": "label",
    "filterwriter": "label",
    "final": "keyword1",
    "finally": "keyword2",
    "float": "label",
    "for": "keyword2",
    "forever": "keyword2",
    "form": "keyword3",
    "format": "literal2",
    "hashcode": "function",
    "hashmap": "label",
    "hashset": "label",
    "hashtable": "label",
    "if": "keyword2",
    "illegalaccessexception": "markup",
    "illegalargumentexception": "markup",
    "illegalmonitorstateexception": "markup",
    "illegalstateexception": "markup",
    "illegalthreadstateexception": "markup",
    "implements": "keyword1",
    "import": "keyword3",
    "indexoutofboundsexception": "markup",
    "indirect": "keyword1",
    "inheritable": "keyword1",
    "inputstream": "label",
    "inputstreamreader": "label",
    "insert": "function",
    "instantiationexception": "markup",
    "int": "label",
    "integer": "label",
    "interface": "keyword1",
    "interruptedexception": "markup",
    "interruptedioexception": "markup",
    "invalidclassexception": "markup",
    "invalidobjectexception": "markup",
    "ioexception": "markup",
    "iterate": "keyword2",
    "java": "literal2",
    "keep": "literal2",
    "label": "keyword2",
    "lastpos": "function",
    "leave": "keyword2",
    "left": "function",
    "length": "function",
    "linenumberinputstream": "label",
    "linenumberreader": "label",
    "linkedhashmap": "label",
    "linkedhashset": "label",
    "logo": "literal2",
    "long": "label",
    "loop": "keyword2",
    "lower": "function",
    "max": "function",
    "method": "keyword1",
    "methods": "keyword3",
    "min": "function",
    "native": "keyword1",
    "negativearraysizeexception": "markup",
    "nobinary": "literal2",
    "nocomments": "literal2",
    "nocompact": "literal2",
    "noconsole": "literal2",
    "nocrossref": "literal2",
    "nodecimal": "literal2",
    "nodiag": "literal2",
    "noexplicit": "literal2",
    "noformat": "literal2",
    "nojava": "literal2",
    "nokeep": "literal2",
    "nologo": "literal2",
    "nootherwiseexception": "markup",
    "nop": "function",
    "noreplace": "literal2",
    "nosavelog": "literal2",
    "nosourcedir": "literal2",
    "nostrictargs": "literal2",
    "nostrictassign": "literal2",
    "nostrictcase": "literal2",
    "nostrictimport": "literal2",
    "nostrictprops": "literal2",
    "nostrictsignal": "literal2",
    "nosuchfieldexception": "markup",
    "nosuchmethodexception": "markup",
    "nosymbols": "literal2",
    "notactiveexception": "markup",
    "notcharacterexception": "markup",
    "notlogicexception": "markup",
    "notrace": "literal2",
    "notserializableexception": "markup",
    "noutf8": "literal2",
    "noverbose": "literal2",
    "null": "keyword3",
    "nullpointerexception": "markup",
    "number": "label",
    "numberformatexception": "markup",
    "numeric": "keyword3",
    "object": "label",
    "objectinputstream": "label",
    "objectoutputstream": "label",
    "objectstreamexception": "markup",
    "off": "keyword3",
    "optionaldataexception": "markup",
    "options": "literal2",
    "otherwise": "keyword2",
    "outputstream": "label",
    "outputstreamwriter": "label",
    "over": "keyword2",
    "overlay": "function",
    "package": "keyword3",
    "parent": "keyword3",
    "parse": "function",
    "pipedinputstream": "label",
    "pipedoutputstream": "label",
    "pipedreader": "label",
    "pipedwriter": "label",
    "pos": "function",
    "printstream": "label",
    "printwriter": "label",
    "private": "keyword1",
    "properties": "keyword1",
    "protect": "keyword2",
    "public": "keyword1",
    "pushbackinputstream": "label",
    "pushbackreader": "label",
    "randomaccessfile": "label",
    "reader": "label",
    "remoteexception": "markup",
    "replace": "literal2",
    "results": "keyword3",
    "return": "keyword2",
    "returns": "keyword1",
    "reverse": "function",
    "rexx": "label",
    "right": "function",
    "runtimeexception": "markup",
    "savelog": "literal2",
    "say": "function",
    "scientific": "keyword3",
    "securityexception": "markup",
    "select": "keyword2",
    "sequence": "function",
    "sequenceinputstream": "label",
    "short": "label",
    "sign": "function",
    "signal": "keyword2",
    "signals": "keyword1",
    "source": "keyword3",
    "sourcedir": "literal2",
    "sourceline": "keyword3",
    "space": "function",
    "static": "keyword1",
    "streamcorruptedexception": "markup",
    "streamtokenizer": "label",
    "strictargs": "literal2",
    "strictassign": "literal2",
    "strictcase": "literal2",
    "strictimport": "literal2",
    "strictprops": "literal2",
    "strictsignal": "literal2",
    "string": "label",
    "stringbuffer": "label",
    "stringbufferinputstream": "label",
    "stringindexoutofboundsexception": "markup",
    "stringreader": "label",
    "stringwriter": "label",
    "strip": "function",
    "substr": "function",
    "subword": "function",
    "super": "keyword3",
    "symbols": "literal2",
    "syncfailedexception": "markup",
    "then": "keyword2",
    "this": "keyword3",
    "to": "keyword2",
    "toboolean": "function",
    "tobyte": "function",
    "tochar": "function",
    "tochararray": "function",
    "todouble": "function",
    "tofloat": "function",
    "toint": "function",
    "tolong": "function",
    "toshort": "function",
    "tostring": "function",
    "trace": "keyword3",
    "transient": "keyword1",
    "translate": "function",
    "treemap": "label",
    "treeset": "label",
    "trunc": "function",
    "unsupportedencodingexception": "markup",
    "unsupportedoperationexception": "markup",
    "until": "keyword2",
    "unused": "keyword1",
    "upper": "function",
    "uses": "keyword1",
    "utf8": "literal2",
    "utfdataformatexception": "markup",
    "var": "keyword3",
    "vector": "label",
    "verbose": "literal2",
    "verbose0": "literal2",
    "verbose1": "literal2",
    "verbose2": "literal2",
    "verbose3": "literal2",
    "verbose4": "literal2",
    "verbose5": "literal2",
    "verify": "function",
    "version": "keyword3",
    "volatile": "keyword1",
    "when": "keyword2",
    "while": "keyword2",
    "word": "function",
    "wordindex": "function",
    "wordlength": "function",
    "wordpos": "function",
    "words": "function",
    "writeabortedexception": "markup",
    "writer": "label",
    "x2b": "function",
    "x2c": "function",
    "x2d": "function",
}

# Dictionary of keywords dictionaries for netrexx mode.
keywordsDictDict = {
    "netrexx_main": netrexx_main_keywords_dict,
}

# Rules for netrexx_main ruleset.

def netrexx_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="/**", end="*/",
          delegate="java::javadoc")

def netrexx_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def netrexx_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def netrexx_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def netrexx_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def netrexx_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def netrexx_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def netrexx_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def netrexx_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def netrexx_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def netrexx_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def netrexx_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def netrexx_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=".*")

def netrexx_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def netrexx_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def netrexx_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def netrexx_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def netrexx_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def netrexx_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def netrexx_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def netrexx_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def netrexx_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def netrexx_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def netrexx_rule23(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for netrexx_main ruleset.
rulesDict1 = {
    "!": [netrexx_rule6,],
    "\"": [netrexx_rule2,],
    "%": [netrexx_rule16,],
    "&": [netrexx_rule17,],
    "'": [netrexx_rule3,],
    "*": [netrexx_rule13,],
    "+": [netrexx_rule9,],
    "-": [netrexx_rule4, netrexx_rule10,],
    ".": [netrexx_rule12,],
    "/": [netrexx_rule0, netrexx_rule1, netrexx_rule11,],
    "0": [netrexx_rule23,],
    "1": [netrexx_rule23,],
    "2": [netrexx_rule23,],
    "3": [netrexx_rule23,],
    "4": [netrexx_rule23,],
    "5": [netrexx_rule23,],
    "6": [netrexx_rule23,],
    "7": [netrexx_rule23,],
    "8": [netrexx_rule23,],
    "9": [netrexx_rule23,],
    "<": [netrexx_rule8, netrexx_rule15,],
    "=": [netrexx_rule5,],
    ">": [netrexx_rule7, netrexx_rule14,],
    "@": [netrexx_rule23,],
    "A": [netrexx_rule23,],
    "B": [netrexx_rule23,],
    "C": [netrexx_rule23,],
    "D": [netrexx_rule23,],
    "E": [netrexx_rule23,],
    "F": [netrexx_rule23,],
    "G": [netrexx_rule23,],
    "H": [netrexx_rule23,],
    "I": [netrexx_rule23,],
    "J": [netrexx_rule23,],
    "K": [netrexx_rule23,],
    "L": [netrexx_rule23,],
    "M": [netrexx_rule23,],
    "N": [netrexx_rule23,],
    "O": [netrexx_rule23,],
    "P": [netrexx_rule23,],
    "Q": [netrexx_rule23,],
    "R": [netrexx_rule23,],
    "S": [netrexx_rule23,],
    "T": [netrexx_rule23,],
    "U": [netrexx_rule23,],
    "V": [netrexx_rule23,],
    "W": [netrexx_rule23,],
    "X": [netrexx_rule23,],
    "Y": [netrexx_rule23,],
    "Z": [netrexx_rule23,],
    "^": [netrexx_rule19,],
    "a": [netrexx_rule23,],
    "b": [netrexx_rule23,],
    "c": [netrexx_rule23,],
    "d": [netrexx_rule23,],
    "e": [netrexx_rule23,],
    "f": [netrexx_rule23,],
    "g": [netrexx_rule23,],
    "h": [netrexx_rule23,],
    "i": [netrexx_rule23,],
    "j": [netrexx_rule23,],
    "k": [netrexx_rule23,],
    "l": [netrexx_rule23,],
    "m": [netrexx_rule23,],
    "n": [netrexx_rule23,],
    "o": [netrexx_rule23,],
    "p": [netrexx_rule23,],
    "q": [netrexx_rule23,],
    "r": [netrexx_rule23,],
    "s": [netrexx_rule23,],
    "t": [netrexx_rule23,],
    "u": [netrexx_rule23,],
    "v": [netrexx_rule23,],
    "w": [netrexx_rule23,],
    "x": [netrexx_rule23,],
    "y": [netrexx_rule23,],
    "z": [netrexx_rule23,],
    "{": [netrexx_rule22,],
    "|": [netrexx_rule18,],
    "}": [netrexx_rule21,],
    "~": [netrexx_rule20,],
}

# x.rulesDictDict for netrexx mode.
rulesDictDict = {
    "netrexx_main": rulesDict1,
}

# Import dict for netrexx mode.
importDict = {}

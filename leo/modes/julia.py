#@+leo-ver=5-thin
#@+node:ekr.20210223151922.1: * @file ../modes/julia.py
#@@language python
# Leo colorizer control file for julia mode.
# This file is in the public domain.

# Properties for julia mode.
properties = {
        "lineComment": "#",
}

# Attributes dict for julia_main ruleset.
julia_main_attributes_dict = {
        "default": "null",
        "digit_re": "[0-9]+(im)?|0x[0-9a-fA-F]+(im)?|[0-9]+e[0-9]*(im)?",
        "escape": "",
        "highlight_digits": "true",
        "ignore_case": "false",
        "no_word_sep": "",
}

# Attributes dict for julia_stringliteral2 ruleset.
julia_stringliteral2_attributes_dict = {
        "default": "LITERAL2",
        "digit_re": "[0-9]+(im)?|0x[0-9a-fA-F]+(im)?|[0-9]+e[0-9]*(im)?",
        "escape": "\\",
        "highlight_digits": "true",
        "ignore_case": "false",
        "no_word_sep": "",
}

# Attributes dict for julia_stringliteral3 ruleset.
julia_stringliteral3_attributes_dict = {
        "default": "LITERAL3",
        "digit_re": "[0-9]+(im)?|0x[0-9a-fA-F]+(im)?|[0-9]+e[0-9]*(im)?",
        "escape": "\\",
        "highlight_digits": "true",
        "ignore_case": "false",
        "no_word_sep": "",
}

# Attributes dict for julia_stringliteral4 ruleset.
julia_stringliteral4_attributes_dict = {
        "default": "LITERAL4",
        "digit_re": "[0-9]+(im)?|0x[0-9a-fA-F]+(im)?|[0-9]+e[0-9]*(im)?",
        "escape": "\\",
        "highlight_digits": "true",
        "ignore_case": "false",
        "no_word_sep": "",
}

# Attributes dict for julia_typedescription ruleset.
julia_typedescription_attributes_dict = {
        "default": "KEYWORD3",
        "digit_re": "[0-9]+(im)?|0x[0-9a-fA-F]+(im)?|[0-9]+e[0-9]*(im)?",
        "escape": "\\",
        "highlight_digits": "true",
        "ignore_case": "false",
        "no_word_sep": "",
}

# Dictionary of attributes dictionaries for julia mode.
attributesDictDict = {
        "julia_main": julia_main_attributes_dict,
        "julia_stringliteral2": julia_stringliteral2_attributes_dict,
        "julia_stringliteral3": julia_stringliteral3_attributes_dict,
        "julia_stringliteral4": julia_stringliteral4_attributes_dict,
        "julia_typedescription": julia_typedescription_attributes_dict,
}

# Keywords dict for julia_main ruleset.
julia_main_keywords_dict = {
        "ASCIIString": "keyword3",
        "Any": "keyword3",
        "Array": "keyword3",
        "Bool": "keyword3",
        "Char": "keyword3",
        "Cmd": "keyword3",
        "Float32": "keyword3",
        "Float64": "keyword3",
        "Inf": "digit",
        "Int": "keyword3",
        "Int16": "keyword3",
        "Int32": "keyword3",
        "Int64": "keyword3",
        "Int8": "keyword3",
        "NaN": "digit",
        "None": "keyword3",
        "Regex": "keyword3",
        "Task": "keyword3",
        "UTF8String": "keyword3",
        "Uint16": "keyword3",
        "Uint32": "keyword3",
        "Uint64": "keyword3",
        "Uint8": "keyword3",
        "abs": "keyword4",
        "abs2": "keyword4",
        "abstract": "keyword2",
        "acos": "keyword4",
        "acot": "keyword4",
        "acoth": "keyword4",
        "acsc": "keyword4",
        "acsch": "keyword4",
        "add": "keyword4",
        "addprocs_local": "keyword4",
        "addprocs_sge": "keyword4",
        "addprocs_ssh": "keyword4",
        "all": "keyword4",
        "allp": "keyword4",
        "any": "keyword4",
        "anyp": "keyword4",
        "applicable": "keyword4",
        "asec": "keyword4",
        "asech": "keyword4",
        "asin": "keyword4",
        "ask": "keyword4",
        "assert": "keyword4",
        "assign": "keyword4",
        "atan": "keyword4",
        "atan2": "keyword4",
        "begin": "keyword1",
        "bin": "keyword4",
        "binomial": "keyword4",
        "bitstype": "keyword2",
        "bool": "keyword4",
        "break": "keyword2",
        "bswap": "keyword4",
        "cat": "keyword4",
        "catch": "keyword1",
        "cbrt": "keyword4",
        "ceil": "keyword4",
        "cell": "keyword4",
        "changedist": "keyword4",
        "char": "keyword4",
        "chars": "keyword4",
        "chol": "keyword4",
        "chomp": "keyword4",
        "choose": "keyword4",
        "chop": "keyword4",
        "chr2ind": "keyword4",
        "circshift": "keyword4",
        "cis": "keyword4",
        "clock": "keyword4",
        "close": "keyword4",
        "complex": "keyword4",
        "cond": "keyword4",
        "const": "keyword2",
        "consume": "keyword4",
        "contains": "keyword4",
        "continue": "keyword2",
        "conv": "keyword4",
        "convert": "keyword4",
        "copy": "keyword4",
        "copysign": "keyword4",
        "cos": "keyword4",
        "cosc": "keyword4",
        "cosh": "keyword4",
        "cot": "keyword4",
        "coth": "keyword4",
        "count": "keyword4",
        "countp": "keyword4",
        "csc": "keyword4",
        "csch": "keyword4",
        "cstring": "keyword4",
        "csvread": "keyword4",
        "csvwrite": "keyword4",
        "cumsum": "keyword4",
        "current_output_stream": "keyword4",
        "current_task": "keyword4",
        "darray": "keyword4",
        "dcell": "keyword4",
        "dec": "keyword4",
        "deconv": "keyword4",
        "del": "keyword4",
        "del_all": "keyword4",
        "det": "keyword4",
        "dfill": "keyword4",
        "diag": "keyword4",
        "diagm": "keyword4",
        "distdim": "keyword4",
        "distribute": "keyword4",
        "div": "keyword4",
        "dlmread": "keyword4",
        "dlmwrite": "keyword4",
        "dlopen": "keyword4",
        "dlsym": "keyword4",
        "done": "keyword4",
        "dones": "keyword4",
        "drand": "keyword4",
        "drandn": "keyword4",
        "dump": "keyword4",
        "dzeros": "keyword4",
        "each_line": "keyword4",
        "edit": "keyword4",
        "eig": "keyword4",
        "else": "keyword1",
        "elseif": "keyword1",
        "eltype": "keyword4",
        "emoteRef": "keyword4",
        "empty": "keyword4",
        "end": "keyword1",
        "enq": "keyword4",
        "eps": "keyword4",
        "erf": "keyword4",
        "erfc": "keyword4",
        "errno": "keyword4",
        "error": "keyword4",
        "eval": "keyword4",
        "exit": "keyword4",
        "exp": "keyword4",
        "expm1": "keyword4",
        "exponent": "keyword4",
        "eye": "keyword4",
        "factorial": "keyword4",
        "false": "literal4",
        "falses": "keyword4",
        "fdio": "keyword4",
        "fetch": "keyword4",
        "fft": "keyword4",
        "fftshift": "keyword4",
        "fill": "keyword4",
        "filter": "keyword4",
        "finalizer": "keyword4",
        "find": "keyword4",
        "findn": "keyword4",
        "fld": "keyword4",
        "flip": "keyword4",
        "flipdim": "keyword4",
        "fliplr": "keyword4",
        "flipud": "keyword4",
        "float32": "keyword4",
        "float64": "keyword4",
        "floor": "keyword4",
        "flush": "keyword4",
        "for": "keyword1",
        "function": "keyword1",
        "gamma": "keyword4",
        "gcd": "keyword4",
        "gensym": "keyword4",
        "get": "keyword4",
        "getcwd": "keyword4",
        "gethostname": "keyword4",
        "getipaddr": "keyword4",
        "getpid": "keyword4",
        "global": "keyword2",
        "grow": "keyword4",
        "has": "keyword4",
        "hash": "keyword4",
        "hcat": "keyword4",
        "hex": "keyword4",
        "hex2num": "keyword4",
        "hypot": "keyword4",
        "if": "keyword1",
        "ifft": "keyword4",
        "ifftshift": "keyword4",
        "ind2chr": "keyword4",
        "ineIterator": "keyword4",
        "insert": "keyword4",
        "int16": "keyword4",
        "int2str": "keyword4",
        "int32": "keyword4",
        "int64": "keyword4",
        "int8": "keyword4",
        "integer_valued": "keyword4",
        "intset": "keyword4",
        "inv": "keyword4",
        "invoke": "keyword4",
        "ipermute": "keyword4",
        "iround": "keyword4",
        "is": "keyword4",
        "isa": "keyword4",
        "iscomplex": "keyword4",
        "isdenormal": "keyword4",
        "isempty": "keyword4",
        "isequal": "keyword4",
        "isfinite": "keyword4",
        "isless": "keyword4",
        "isnan": "keyword4",
        "isreal": "keyword4",
        "issorted": "keyword4",
        "istaskdone": "keyword4",
        "itrunc": "keyword4",
        "join": "keyword4",
        "kron": "keyword4",
        "lcm": "keyword4",
        "ldexp": "keyword4",
        "length": "keyword4",
        "let": "keyword1",
        "lgamma": "keyword4",
        "linreg": "keyword4",
        "linspace": "keyword4",
        "load": "keyword4",
        "local": "keyword2",
        "localize": "keyword4",
        "log": "keyword4",
        "log10": "keyword4",
        "log1p": "keyword4",
        "log2": "keyword4",
        "logb": "keyword4",
        "lpad": "keyword4",
        "lu": "keyword4",
        "macro": "keyword1",
        "make_scheduled": "keyword4",
        "mantissa": "keyword4",
        "map": "keyword4",
        "max": "keyword4",
        "memio": "keyword4",
        "method_exists": "keyword4",
        "min": "keyword4",
        "mod": "keyword4",
        "myid": "keyword4",
        "myindexes": "keyword4",
        "ndims": "keyword4",
        "new": "keyword4",
        "next": "keyword4",
        "nextfloat": "keyword4",
        "nextpow2": "keyword4",
        "nnz": "keyword4",
        "nprocs": "keyword4",
        "ntSet": "keyword4",
        "nthperm": "keyword4",
        "ntuple": "keyword4",
        "num2hex": "keyword4",
        "numel": "keyword4",
        "nvHash": "keyword4",
        "oct": "keyword4",
        "one": "keyword4",
        "ones": "keyword4",
        "op": "keyword4",
        "open": "keyword4",
        "owner": "keyword4",
        "parse_int": "keyword4",
        "permute": "keyword4",
        "pop": "keyword4",
        "position": "keyword4",
        "pow": "keyword4",
        "powermod": "keyword4",
        "prevfloat": "keyword4",
        "print": "keyword4",
        "println": "keyword4",
        "procs": "keyword4",
        "prod": "keyword4",
        "produce": "keyword4",
        "promote": "keyword4",
        "promote_type": "keyword4",
        "push": "keyword4",
        "put": "keyword4",
        "qr": "keyword4",
        "quote": "keyword1",
        "rand": "keyword4",
        "randchi2": "keyword4",
        "randcycle": "keyword4",
        "randf": "keyword4",
        "randg": "keyword4",
        "randi": "keyword4",
        "randn": "keyword4",
        "randperm": "keyword4",
        "rank": "keyword4",
        "read": "keyword4",
        "readall": "keyword4",
        "readline": "keyword4",
        "readlines": "keyword4",
        "readuntil": "keyword4",
        "real_valued": "keyword4",
        "realmax": "keyword4",
        "realmin": "keyword4",
        "reduce": "keyword4",
        "ref": "keyword4",
        "reinterpret": "keyword4",
        "rem": "keyword4",
        "remote_call": "keyword4",
        "remote_call_fetch": "keyword4",
        "remote_call_wait": "keyword4",
        "repmat": "keyword4",
        "reshape": "keyword4",
        "return": "keyword2",
        "reverse": "keyword4",
        "round": "keyword4",
        "rpad": "keyword4",
        "rray": "keyword4",
        "safe_char": "keyword4",
        "sec": "keyword4",
        "sech": "keyword4",
        "seek": "keyword4",
        "set_current_output_stream": "keyword4",
        "setcwd": "keyword4",
        "show": "keyword4",
        "showall": "keyword4",
        "shuffle": "keyword4",
        "sign": "keyword4",
        "signbit": "keyword4",
        "similar": "keyword4",
        "sin": "keyword4",
        "sinc": "keyword4",
        "sinh": "keyword4",
        "size": "keyword4",
        "sizeof": "keyword4",
        "skip": "keyword4",
        "slicedim": "keyword4",
        "sort": "keyword4",
        "sortperm": "keyword4",
        "sortr": "keyword4",
        "split": "keyword4",
        "sqrt": "keyword4",
        "squeeze": "keyword4",
        "start": "keyword4",
        "strcat": "keyword4",
        "strchr": "keyword4",
        "strerror": "keyword4",
        "stride": "keyword4",
        "strides": "keyword4",
        "string": "keyword4",
        "strlen": "keyword4",
        "sub": "keyword4",
        "subtype": "keyword4",
        "sum": "keyword4",
        "super": "keyword4",
        "svd": "keyword4",
        "system": "keyword4",
        "take": "keyword4",
        "tan": "keyword4",
        "tanh": "keyword4",
        "task_exit": "keyword4",
        "throw": "keyword4",
        "tic": "keyword4",
        "tls": "keyword4",
        "toc": "keyword4",
        "toq": "keyword4",
        "trace": "keyword4",
        "tril": "keyword4",
        "tring": "keyword4",
        "triu": "keyword4",
        "true": "literal4",
        "trues": "keyword4",
        "trunc": "keyword4",
        "try": "keyword1",
        "tuple": "keyword4",
        "type": "keyword1",
        "typealias": "keyword2",
        "typemax": "keyword4",
        "typemin": "keyword4",
        "typeof": "keyword4",
        "uid": "keyword4",
        "uint16": "keyword4",
        "uint32": "keyword4",
        "uint64": "keyword4",
        "uint8": "keyword4",
        "union": "keyword4",
        "value": "keyword4",
        "vcat": "keyword4",
        "wait": "keyword4",
        "while": "keyword1",
        "whos": "keyword4",
        "with_output_stream": "keyword4",
        "write": "keyword4",
        "xcorr": "keyword4",
        "yield": "keyword4",
        "yieldto": "keyword4",
        "zero": "keyword4",
        "zeros": "keyword4",
}

# Keywords dict for julia_stringliteral2 ruleset.
julia_stringliteral2_keywords_dict = {}

# Keywords dict for julia_stringliteral3 ruleset.
julia_stringliteral3_keywords_dict = {}

# Keywords dict for julia_stringliteral4 ruleset.
julia_stringliteral4_keywords_dict = {}

# Keywords dict for julia_typedescription ruleset.
julia_typedescription_keywords_dict = {}

# Dictionary of keywords dictionaries for julia mode.
keywordsDictDict = {
        "julia_main": julia_main_keywords_dict,
        "julia_stringliteral2": julia_stringliteral2_keywords_dict,
        "julia_stringliteral3": julia_stringliteral3_keywords_dict,
        "julia_stringliteral4": julia_stringliteral4_keywords_dict,
        "julia_typedescription": julia_typedescription_keywords_dict,
}

# Rules for julia_main ruleset.

def julia_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment4", seq="####")

def julia_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq="###")

def julia_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="##")

def julia_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def julia_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def julia_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"", end="\"",
        delegate="julia::stringliteral2")

def julia_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="I\"", end="\"",
        delegate="julia::stringliteral2")

def julia_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="E\"", end="\"")

def julia_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="L\"", end="\"")

def julia_rule9(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal4", begin="r[ims]*\"", end="\"")

def julia_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal4", begin="b\"", end="\"",
        delegate="julia::stringliteral4")

def julia_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="`", end="`",
        delegate="julia::stringliteral3")

def julia_rule12(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="::")

def julia_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="{", end="}",
        delegate="julia::typedescription")

def julia_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<:")

def julia_rule15(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(")

def julia_rule16(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="markup", pattern="@")

def julia_rule17(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="markup", pattern="$")

def julia_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=":[a-zA-Z_][a-zA-Z_0-9]*")

def julia_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def julia_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&&")

def julia_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="||")

def julia_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def julia_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def julia_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&=")

def julia_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|=")

def julia_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="$=")

def julia_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>>=")

def julia_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>=")

def julia_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<=")

def julia_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def julia_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def julia_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="$")

def julia_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>>")

def julia_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>")

def julia_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<")

def julia_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def julia_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!=")

def julia_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def julia_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def julia_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def julia_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def julia_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="//")

def julia_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+=")

def julia_rule44(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-=")

def julia_rule45(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*=")

def julia_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/=")

def julia_rule47(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^=")

def julia_rule48(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%=")

def julia_rule49(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def julia_rule50(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def julia_rule51(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def julia_rule52(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def julia_rule53(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def julia_rule54(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def julia_rule55(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="...")

def julia_rule56(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def julia_rule57(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def julia_rule58(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def julia_rule59(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def julia_rule60(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def julia_rule61(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="::")

def julia_rule62(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def julia_rule63(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def julia_rule64(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def julia_rule65(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for julia_main ruleset.
rulesDict1 = {
    "!": [julia_rule22, julia_rule37,],
    "\"": [julia_rule5,],
    "#": [julia_rule0, julia_rule1, julia_rule2, julia_rule3,],
    "$": [julia_rule17, julia_rule26, julia_rule32,],
    "%": [julia_rule48, julia_rule54,],
    "&": [julia_rule20, julia_rule24, julia_rule30,],
    "'": [julia_rule4,],
    "(": [julia_rule15,],
    "*": [julia_rule45, julia_rule51,],
    "+": [julia_rule43, julia_rule49,],
    "-": [julia_rule19, julia_rule44, julia_rule50,],
    ".": [julia_rule55,],
    "/": [julia_rule42, julia_rule46, julia_rule52,],
    "0": [julia_rule65,],
    "1": [julia_rule65,],
    "2": [julia_rule65,],
    "3": [julia_rule65,],
    "4": [julia_rule65,],
    "5": [julia_rule65,],
    "6": [julia_rule65,],
    "7": [julia_rule65,],
    "8": [julia_rule65,],
    "9": [julia_rule65,],
    ":": [julia_rule12, julia_rule18, julia_rule61, julia_rule63,],
    ";": [julia_rule64,],
    "<": [julia_rule14, julia_rule29, julia_rule35, julia_rule39, julia_rule41,],
    "=": [julia_rule36, julia_rule60,],
    ">": [julia_rule27, julia_rule28, julia_rule33, julia_rule34, julia_rule38, julia_rule40,],
    "?": [julia_rule62,],
    "@": [julia_rule16, julia_rule65,],
    "A": [julia_rule65,],
    "B": [julia_rule65,],
    "C": [julia_rule65,],
    "D": [julia_rule65,],
    "E": [julia_rule7, julia_rule65,],
    "F": [julia_rule65,],
    "G": [julia_rule65,],
    "H": [julia_rule65,],
    "I": [julia_rule6, julia_rule65,],
    "J": [julia_rule65,],
    "K": [julia_rule65,],
    "L": [julia_rule8, julia_rule65,],
    "M": [julia_rule65,],
    "N": [julia_rule65,],
    "O": [julia_rule65,],
    "P": [julia_rule65,],
    "Q": [julia_rule65,],
    "R": [julia_rule65,],
    "S": [julia_rule65,],
    "T": [julia_rule65,],
    "U": [julia_rule65,],
    "V": [julia_rule65,],
    "W": [julia_rule65,],
    "X": [julia_rule65,],
    "Y": [julia_rule65,],
    "Z": [julia_rule65,],
    "[": [julia_rule57,],
    "]": [julia_rule56,],
    "^": [julia_rule47, julia_rule53,],
    "_": [julia_rule65,],
    "`": [julia_rule11,],
    "a": [julia_rule65,],
    "b": [julia_rule10, julia_rule65,],
    "c": [julia_rule65,],
    "d": [julia_rule65,],
    "e": [julia_rule65,],
    "f": [julia_rule65,],
    "g": [julia_rule65,],
    "h": [julia_rule65,],
    "i": [julia_rule65,],
    "j": [julia_rule65,],
    "k": [julia_rule65,],
    "l": [julia_rule65,],
    "m": [julia_rule65,],
    "n": [julia_rule65,],
    "o": [julia_rule65,],
    "p": [julia_rule65,],
    "q": [julia_rule65,],
    "r": [julia_rule9, julia_rule65,],
    "s": [julia_rule65,],
    "t": [julia_rule65,],
    "u": [julia_rule65,],
    "v": [julia_rule65,],
    "w": [julia_rule65,],
    "x": [julia_rule65,],
    "y": [julia_rule65,],
    "z": [julia_rule65,],
    "{": [julia_rule13, julia_rule58,],
    "|": [julia_rule21, julia_rule25, julia_rule31,],
    "}": [julia_rule59,],
    "~": [julia_rule23,],
}

# Rules for julia_stringliteral2 ruleset.

def julia_rule66(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="$(", end=")")

def julia_rule67(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="$[", end="]")

def julia_rule68(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="null", pattern="$")

# Rules dict for julia_stringliteral2 ruleset.
rulesDict2 = {
    "$": [julia_rule66, julia_rule67, julia_rule68,],
}

# Rules for julia_stringliteral3 ruleset.

def julia_rule69(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="$(", end=")")

def julia_rule70(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="$[", end="]")

def julia_rule71(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="null", pattern="$")

# Rules dict for julia_stringliteral3 ruleset.
rulesDict3 = {
    "$": [julia_rule69, julia_rule70, julia_rule71,],
}

# Rules for julia_stringliteral4 ruleset.

def julia_rule72(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="$(", end=")",
        delegate="julia::main")

def julia_rule73(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="$[", end="]",
        delegate="julia::main")

def julia_rule74(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="null", pattern="$")

# Rules dict for julia_stringliteral4 ruleset.
rulesDict4 = {
    "$": [julia_rule72, julia_rule73, julia_rule74,],
}

# Rules for julia_typedescription ruleset.

def julia_rule75(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<:")

def julia_rule76(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def julia_rule77(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def julia_rule78(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=",")

# Rules dict for julia_typedescription ruleset.
rulesDict5 = {
    ",": [julia_rule78,],
    "<": [julia_rule75,],
    "{": [julia_rule76,],
    "}": [julia_rule77,],
}

# x.rulesDictDict for julia mode.
rulesDictDict = {
    "julia_main": rulesDict1,
    "julia_stringliteral2": rulesDict2,
    "julia_stringliteral3": rulesDict3,
    "julia_stringliteral4": rulesDict4,
    "julia_typedescription": rulesDict5,
}

# Import dict for julia mode.
importDict = {}

#@-leo

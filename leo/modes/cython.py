# Leo colorizer control file for cython mode.
# This file is in the public domain.

# Properties for cython mode.
properties = {
    "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "#",
}

# Attributes dict for cython_main ruleset.
cython_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for cython mode.
attributesDictDict = {
    "cython_main": cython_main_attributes_dict,
}

# Keywords dict for cython_main ruleset.
cython_main_keywords_dict = {

    # Additional cython keywords....
    # The colorizer computes word chars, so "except?" is handled correctly.
    "by": "keyword4",
    "cdef": "keyword4",
    "cimport": "keyword4",
    "cpdef": "keyword4",
    "ctypedef": "keyword4",
    "enum": "keyword4",
    "except?": "keyword4",
    "extern": "keyword4",
    "gil": "keyword4",
    "include": "keyword4",
    "nogil": "keyword4",
    "property": "keyword4",
    "public": "keyword4",
    "readonly": "keyword4",
    "struct": "keyword4",
    "union": "keyword4",
    "DEF": "keyword4",
    "IF": "keyword4",
    "ELIF": "keyword4",
    "ELSE": "keyword4",

    # New types, hightlighted as builtins (keyword3).
    "NULL": "keyword3",
    "bint": "keyword3",
    "char": "keyword3",
    "dict": "keyword3",
    "double": "keyword3",
    "float": "keyword3",
    "int": "keyword3",
    "list": "keyword3",
    "long": "keyword3",
    "object": "keyword3",
    "Py_ssize_t": "keyword3",
    "short": "keyword3",
    "size_t": "keyword3",
    "void": "keyword3",

    # Normal Python keywords, the same as in python.py...
    # except that conflicts with cython keywords have been removed.
    "ArithmeticError": "keyword3",
    "AssertionError": "keyword3",
    "AttributeError": "keyword3",
    "BufferType": "keyword3",
    "BuiltinFunctionType": "keyword3",
    "BuiltinMethodType": "keyword3",
    "ClassType": "keyword3",
    "CodeType": "keyword3",
    "ComplexType": "keyword3",
    "DeprecationWarning": "keyword3",
    "DictProxyType": "keyword3",
    "DictType": "keyword3",
    "DictionaryType": "keyword3",
    "EOFError": "keyword3",
    "EllipsisType": "keyword3",
    "EnvironmentError": "keyword3",
    "Exception": "keyword3",
    "False": "keyword3",
    "FileType": "keyword3",
    "FloatType": "keyword3",
    "FloatingPointError": "keyword3",
    "FrameType": "keyword3",
    "FunctionType": "keyword3",
    "GeneratorType": "keyword3",
    "IOError": "keyword3",
    "ImportError": "keyword3",
    "IndentationError": "keyword3",
    "IndexError": "keyword3",
    "InstanceType": "keyword3",
    "IntType": "keyword3",
    "KeyError": "keyword3",
    "KeyboardInterrupt": "keyword3",
    "LambdaType": "keyword3",
    "ListType": "keyword3",
    "LongType": "keyword3",
    "LookupError": "keyword3",
    "MemoryError": "keyword3",
    "MethodType": "keyword3",
    "ModuleType": "keyword3",
    "NameError": "keyword3",
    "None": "keyword3",
    "NoneType": "keyword3",
    "NotImplemented": "keyword3",
    "NotImplementedError": "keyword3",
    "OSError": "keyword3",
    "ObjectType": "keyword3",
    "OverflowError": "keyword3",
    "OverflowWarning": "keyword3",
    "ReferenceError": "keyword3",
    "RuntimeError": "keyword3",
    "RuntimeWarning": "keyword3",
    "SliceType": "keyword3",
    "StandardError": "keyword3",
    "StopIteration": "keyword3",
    "StringType": "keyword3",
    "StringTypes": "keyword3",
    "SyntaxError": "keyword3",
    "SyntaxWarning": "keyword3",
    "SystemError": "keyword3",
    "SystemExit": "keyword3",
    "TabError": "keyword3",
    "TracebackType": "keyword3",
    "True": "keyword3",
    "TupleType": "keyword3",
    "TypeError": "keyword3",
    "TypeType": "keyword3",
    "UnboundLocalError": "keyword3",
    "UnboundMethodType": "keyword3",
    "UnicodeError": "keyword3",
    "UnicodeType": "keyword3",
    "UserWarning": "keyword3",
    "ValueError": "keyword3",
    "Warning": "keyword3",
    "WindowsError": "keyword3",
    "XRangeType": "keyword3",
    "ZeroDivisionError": "keyword3",
    "__abs__": "keyword3",
    "__add__": "keyword3",
    "__all__": "keyword3",
    "__author__": "keyword3",
    "__bases__": "keyword3",
    "__builtins__": "keyword3",
    "__call__": "keyword3",
    "__class__": "keyword3",
    "__cmp__": "keyword3",
    "__coerce__": "keyword3",
    "__contains__": "keyword3",
    "__debug__": "keyword3",
    "__del__": "keyword3",
    "__delattr__": "keyword3",
    "__delitem__": "keyword3",
    "__delslice__": "keyword3",
    "__dict__": "keyword3",
    "__div__": "keyword3",
    "__divmod__": "keyword3",
    "__doc__": "keyword3",
    "__eq__": "keyword3",
    "__file__": "keyword3",
    "__float__": "keyword3",
    "__floordiv__": "keyword3",
    "__future__": "keyword3",
    "__ge__": "keyword3",
    "__getattr__": "keyword3",
    "__getattribute__": "keyword3",
    "__getitem__": "keyword3",
    "__getslice__": "keyword3",
    "__gt__": "keyword3",
    "__hash__": "keyword3",
    "__hex__": "keyword3",
    "__iadd__": "keyword3",
    "__import__": "keyword3",
    "__imul__": "keyword3",
    "__init__": "keyword3",
    "__int__": "keyword3",
    "__invert__": "keyword3",
    "__iter__": "keyword3",
    "__le__": "keyword3",
    "__len__": "keyword3",
    "__long__": "keyword3",
    "__lshift__": "keyword3",
    "__lt__": "keyword3",
    "__members__": "keyword3",
    "__metaclass__": "keyword3",
    "__mod__": "keyword3",
    "__mro__": "keyword3",
    "__mul__": "keyword3",
    "__name__": "keyword3",
    "__ne__": "keyword3",
    "__neg__": "keyword3",
    "__new__": "keyword3",
    "__nonzero__": "keyword3",
    "__oct__": "keyword3",
    "__or__": "keyword3",
    "__path__": "keyword3",
    "__pos__": "keyword3",
    "__pow__": "keyword3",
    "__radd__": "keyword3",
    "__rdiv__": "keyword3",
    "__rdivmod__": "keyword3",
    "__reduce__": "keyword3",
    "__repr__": "keyword3",
    "__rfloordiv__": "keyword3",
    "__rlshift__": "keyword3",
    "__rmod__": "keyword3",
    "__rmul__": "keyword3",
    "__ror__": "keyword3",
    "__rpow__": "keyword3",
    "__rrshift__": "keyword3",
    "__rsub__": "keyword3",
    "__rtruediv__": "keyword3",
    "__rxor__": "keyword3",
    "__self__": "keyword3",
    "__setattr__": "keyword3",
    "__setitem__": "keyword3",
    "__setslice__": "keyword3",
    "__slots__": "keyword3",
    "__str__": "keyword3",
    "__sub__": "keyword3",
    "__truediv__": "keyword3",
    "__version__": "keyword3",
    "__xor__": "keyword3",
    "abs": "keyword2",
    "and": "keyword1",
    "apply": "keyword2",
    "as": "keyword1",
    "assert": "keyword1",
    "bool": "keyword2",
    "break": "keyword1",
    "buffer": "keyword2",
    "callable": "keyword2",
    "chr": "keyword2",
    "class": "keyword1",
    "classmethod": "keyword2",
    "cmp": "keyword2",
    "coerce": "keyword2",
    "compile": "keyword2",
    "complex": "keyword2",
    "continue": "keyword1",
    "def": "keyword1",
    "del": "keyword1",
    "delattr": "keyword2",
    # "dict": "keyword2",
    "dir": "keyword2",
    "divmod": "keyword2",
    "elif": "keyword1",
    "else": "keyword1",
    "enumerate": "keyword2",
    "eval": "keyword2",
    "except": "keyword1",
    "exec": "keyword1",
    "execfile": "keyword2",
    "file": "keyword2",
    "filter": "keyword2",
    "finally": "keyword1",
    # "float": "keyword2",
    "for": "keyword1",
    "from": "keyword1",
    "getattr": "keyword2",
    "global": "keyword1",
    "globals": "keyword2",
    "hasattr": "keyword2",
    "hash": "keyword2",
    "hex": "keyword2",
    "id": "keyword2",
    "if": "keyword1",
    "import": "keyword1",
    "in": "keyword1",
    "input": "keyword2",
    # "int": "keyword2",
    "intern": "keyword2",
    "is": "keyword1",
    "isinstance": "keyword2",
    "issubclass": "keyword2",
    "iter": "keyword2",
    "lambda": "keyword1",
    "len": "keyword2",
    # "list": "keyword2",
    "locals": "keyword2",
    # "long": "keyword2",
    "map": "keyword2",
    "max": "keyword2",
    "min": "keyword2",
    "not": "keyword1",
    # "object": "keyword2",
    "oct": "keyword2",
    "open": "keyword2",
    "or": "keyword1",
    "ord": "keyword2",
    "pass": "keyword1",
    "pow": "keyword2",
    "print": "keyword1",
    # "property": "keyword2",
    "raise": "keyword1",
    "range": "keyword2",
    "raw_input": "keyword2",
    "reduce": "keyword2",
    "reload": "keyword2",
    "repr": "keyword2",
    "return": "keyword1",
    "round": "keyword2",
    "setattr": "keyword2",
    "slice": "keyword2",
    "sorted": "keyword2",
    "staticmethod": "keyword2",
    "str": "keyword2",
    "sum": "keyword2",
    "super": "keyword2",
    "try": "keyword1",
    "tuple": "keyword2",
    "type": "keyword2",
    "unichr": "keyword2",
    "unicode": "keyword2",
    "vars": "keyword2",
    "while": "keyword1",
    "xrange": "keyword2",
    "yield": "keyword1",
    "zip": "keyword2",
}

# Dictionary of keywords dictionaries for cython mode.
keywordsDictDict = {
    "cython_main": cython_main_keywords_dict,
}

# Rules for cython_main ruleset.

def cython_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def cython_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"")

def cython_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'''", end="'''")

def cython_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def cython_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def cython_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def cython_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def cython_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def cython_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def cython_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def cython_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def cython_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def cython_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def cython_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def cython_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def cython_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def cython_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def cython_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def cython_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def cython_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def cython_rule20(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def cython_rule21(colorer, s, i):
    return colorer.match_keywords(s, i)

url = False

if url:
    h_url_regex = r"""(http|https)://[^\s'"]+[\w=/]"""
    f_url_regex = r"""(file|ftp)://[^\s'"]+[\w=/]"""

    def cython_rule_h_url(colorer, s, i):
        return colorer.match_seq_regexp(s, i, kind="keyword", regexp=h_url_regex)

    def cython_rule_f_url(colorer, s, i):
        return colorer.match_seq_regexp(s, i, kind="keyword", regexp=f_url_regex)
else:
    # Always fail.
    def cython_rule_h_url(colorer, s, i):
        return 0

    def cython_rule_f_url(colorer, s, i):
        return 0

# Rules dict for cython_main ruleset.
rulesDict1 = {
    "!": [cython_rule6,],
    "\"": [cython_rule1, cython_rule3,],
    "#": [cython_rule0,],
    "%": [cython_rule15,],
    "&": [cython_rule16,],
    "'": [cython_rule2, cython_rule4,],
    "(": [cython_rule20,],
    "*": [cython_rule12,],
    "+": [cython_rule9,],
    "-": [cython_rule10,],
    "/": [cython_rule11,],
    "0": [cython_rule21,],
    "1": [cython_rule21,],
    "2": [cython_rule21,],
    "3": [cython_rule21,],
    "4": [cython_rule21,],
    "5": [cython_rule21,],
    "6": [cython_rule21,],
    "7": [cython_rule21,],
    "8": [cython_rule21,],
    "9": [cython_rule21,],
    "<": [cython_rule8, cython_rule14,],
    "=": [cython_rule5,],
    ">": [cython_rule7, cython_rule13,],
    "@": [cython_rule21,],
    "A": [cython_rule21,],
    "B": [cython_rule21,],
    "C": [cython_rule21,],
    "D": [cython_rule21,],
    "E": [cython_rule21,],
    "F": [cython_rule_f_url, cython_rule21,],
    "G": [cython_rule21,],
    "H": [cython_rule_h_url, cython_rule21,],
    "I": [cython_rule21,],
    "J": [cython_rule21,],
    "K": [cython_rule21,],
    "L": [cython_rule21,],
    "M": [cython_rule21,],
    "N": [cython_rule21,],
    "O": [cython_rule21,],
    "P": [cython_rule21,],
    "Q": [cython_rule21,],
    "R": [cython_rule21,],
    "S": [cython_rule21,],
    "T": [cython_rule21,],
    "U": [cython_rule21,],
    "V": [cython_rule21,],
    "W": [cython_rule21,],
    "X": [cython_rule21,],
    "Y": [cython_rule21,],
    "Z": [cython_rule21,],
    "^": [cython_rule18,],
    "_": [cython_rule21,],
    "a": [cython_rule21,],
    "b": [cython_rule21,],
    "c": [cython_rule21,],
    "d": [cython_rule21,],
    "e": [cython_rule21,],
    "f": [cython_rule_f_url, cython_rule21,],
    "g": [cython_rule21,],
    "h": [cython_rule_h_url, cython_rule21,],
    "i": [cython_rule21,],
    "j": [cython_rule21,],
    "k": [cython_rule21,],
    "l": [cython_rule21,],
    "m": [cython_rule21,],
    "n": [cython_rule21,],
    "o": [cython_rule21,],
    "p": [cython_rule21,],
    "q": [cython_rule21,],
    "r": [cython_rule21,],
    "s": [cython_rule21,],
    "t": [cython_rule21,],
    "u": [cython_rule21,],
    "v": [cython_rule21,],
    "w": [cython_rule21,],
    "x": [cython_rule21,],
    "y": [cython_rule21,],
    "z": [cython_rule21,],
    "|": [cython_rule17,],
    "~": [cython_rule19,],
}

# x.rulesDictDict for cython mode.
rulesDictDict = {
    "cython_main": rulesDict1,
}

# Import dict for cython mode.
importDict = {}

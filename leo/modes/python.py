#@+leo-ver=5-thin
#@+node:ekr.20210219115553.109: * @file ../modes/python.py
#@@language python
# Leo colorizer control file for python mode.
# This file is in the public domain.

# Properties for python mode.
properties = {
    "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "#",
}

#@+<< Attributes Dicts >>
#@+node:ekr.20230419163615.1: ** << Attributes Dicts >>

# Attributes dict for python_main ruleset.
python_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for python mode.
attributesDictDict = {
    "python_main": python_main_attributes_dict,
}
#@-<< Attributes Dicts >>
#@+<< Keywords Dicts >>
#@+node:ekr.20230419163648.1: ** << Keywords Dicts >>
# Keywords dict for python_main ruleset.
python_main_keywords_dict = {
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
    "async": "keyword1",  # Python 3.7
    "await": "keyword1",  # Python 3.7.
    "basestring": "keyword2",  # Only in Python 2.
    "bool": "keyword2",
    "break": "keyword1",
    "buffer": "keyword2",
    "callable": "keyword2",
    "chr": "keyword2",
    "class": "keyword1",
    "@classmethod": "keyword2",  # Bug fix: 5/14/2016
    "cmp": "keyword2",
    "coerce": "keyword2",
    "compile": "keyword2",
    "complex": "keyword2",
    "continue": "keyword1",
    "def": "keyword1",
    "del": "keyword1",
    "delattr": "keyword2",
    "dict": "keyword2",
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
    "float": "keyword2",
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
    "int": "keyword2",
    "intern": "keyword2",
    "is": "keyword1",
    "isinstance": "keyword2",
    "issubclass": "keyword2",
    "iter": "keyword2",
    "lambda": "keyword1",
    "len": "keyword2",
    "list": "keyword2",
    "locals": "keyword2",
    "long": "keyword2",
    "nonlocal": "keyword1",
    "map": "keyword2",
    "max": "keyword2",
    "min": "keyword2",
    "not": "keyword1",
    "object": "keyword2",
    "oct": "keyword2",
    "open": "keyword2",
    "or": "keyword1",
    "ord": "keyword2",
    "pass": "keyword1",
    "pow": "keyword2",
    "print": "keyword1",
    "property": "keyword2",
    "raise": "keyword1",
    "range": "keyword2",
    "raw_input": "keyword2",
    "reduce": "keyword2",
    "reload": "keyword2",
    "repr": "keyword2",
    "return": "keyword1",
    "reversed": "keyword2",
    "round": "keyword2",
    "set": "keyword2",
    "setattr": "keyword2",
    "slice": "keyword2",
    "sorted": "keyword2",
    "@staticmethod": "keyword2",  # Bug fix: 5/14/2016
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
    "with": "keyword1",  # Fix bug 1174532: Python mode file missing 'with' keyword
    "xrange": "keyword2",
    "yield": "keyword1",
    "zip": "keyword2",
}

# Dictionary of keywords dictionaries for python mode.
keywordsDictDict = {
    "python_main": python_main_keywords_dict,
}
#@-<< Keywords Dicts >>
#@+others
#@+node:ekr.20230419163736.1: ** Python rules
#@+node:ekr.20230419163819.1: *3* python_rule0
def python_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")
#@+node:ekr.20230419163819.2: *3* python_rule1
def python_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"")
#@+node:ekr.20230419163819.3: *3* python_rule2
def python_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'''", end="'''")
#@+node:ekr.20230419163819.4: *3* python_rule3
def python_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")
#@+node:ekr.20230419163819.5: *3* python_rule4
def python_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")
#@+node:ekr.20230419163819.6: *3* python_rule5
def python_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")


#@+node:ekr.20230419163819.7: *3* python_rule6
def python_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")


#@+node:ekr.20230419163819.8: *3* python_rule7
def python_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")


#@+node:ekr.20230419163819.9: *3* python_rule8
def python_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")


#@+node:ekr.20230419163819.10: *3* python_rule9
def python_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")


#@+node:ekr.20230419163819.11: *3* python_rule10
def python_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")


#@+node:ekr.20230419163819.12: *3* python_rule11
def python_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")


#@+node:ekr.20230419163819.13: *3* python_rule12
def python_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")


#@+node:ekr.20230419163819.14: *3* python_rule13
def python_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")


#@+node:ekr.20230419163819.15: *3* python_rule14
def python_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")


#@+node:ekr.20230419163819.16: *3* python_rule15
def python_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")


#@+node:ekr.20230419163819.17: *3* python_rule16
def python_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")


#@+node:ekr.20230419163819.18: *3* python_rule17
def python_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")


#@+node:ekr.20230419163819.19: *3* python_rule18
def python_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")


#@+node:ekr.20230419163819.20: *3* python_rule19
def python_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")


#@+node:ekr.20230419163819.21: *3* python_rule20 (not used)
if 0:  # #1821.
    def python_rule20(colorer, s, i):
        return colorer.match_mark_previous(s, i, kind="function", pattern="(")
#@+node:ekr.20230419163819.22: *3* python_rule21
def python_rule21(colorer, s, i):
    return colorer.match_keywords(s, i)
#@+node:ekr.20230419163931.1: *3* python_rule_h_url/rule_f_url (not used)
if 0:
    url = False

    if url:
        h_url_regex = r"""(http|https)://[^\s'"]+[\w=/]"""
        f_url_regex = r"""(file|ftp)://[^\s'"]+[\w=/]"""

        def python_rule_h_url(colorer, s, i):
            return colorer.match_seq_regexp(s, i, kind="keyword", regexp=h_url_regex)

        def python_rule_f_url(colorer, s, i):
            return colorer.match_seq_regexp(s, i, kind="keyword", regexp=f_url_regex)

    else:
        # Always fail.
        def python_rule_h_url(colorer, s, i):
            return 0

        def python_rule_f_url(colorer, s, i):
            return 0
#@-others
#@+<< Rules Dicts >>
#@+node:ekr.20230419164059.1: ** << Rules Dicts >>
# Rules dict for python_main ruleset.
rulesDict1 = {
    "!": [python_rule6],
    "\"": [python_rule1, python_rule3],
    "#": [python_rule0],
    "%": [python_rule15],
    "&": [python_rule16],
    "'": [python_rule2, python_rule4],
    # "(": [python_rule20],
    "*": [python_rule12],
    "+": [python_rule9],
    "-": [python_rule10],
    "/": [python_rule11],
    "0": [python_rule21],
    "1": [python_rule21],
    "2": [python_rule21],
    "3": [python_rule21],
    "4": [python_rule21],
    "5": [python_rule21],
    "6": [python_rule21],
    "7": [python_rule21],
    "8": [python_rule21],
    "9": [python_rule21],
    "<": [python_rule8, python_rule14],
    "=": [python_rule5],
    ">": [python_rule7, python_rule13],
    "@": [python_rule21],
    "A": [python_rule21],
    "B": [python_rule21],
    "C": [python_rule21],
    "D": [python_rule21],
    "E": [python_rule21],
    "F": [python_rule21],  # python_rule_f_url,
    "G": [python_rule21],
    "H": [python_rule21],  # python_rule_h_url,
    "I": [python_rule21],
    "J": [python_rule21],
    "K": [python_rule21],
    "L": [python_rule21],
    "M": [python_rule21],
    "N": [python_rule21],
    "O": [python_rule21],
    "P": [python_rule21],
    "Q": [python_rule21],
    "R": [python_rule21],
    "S": [python_rule21],
    "T": [python_rule21],
    "U": [python_rule21],
    "V": [python_rule21],
    "W": [python_rule21],
    "X": [python_rule21],
    "Y": [python_rule21],
    "Z": [python_rule21],
    "^": [python_rule18],
    "_": [python_rule21],
    "a": [python_rule21],
    "b": [python_rule21],
    "c": [python_rule21],
    "d": [python_rule21],
    "e": [python_rule21],
    "f": [python_rule21],  # python_rule_f_url
    "g": [python_rule21],
    "h": [python_rule21],  # python_rule_h_url
    "i": [python_rule21],
    "j": [python_rule21],
    "k": [python_rule21],
    "l": [python_rule21],
    "m": [python_rule21],
    "n": [python_rule21],
    "o": [python_rule21],
    "p": [python_rule21],
    "q": [python_rule21],
    "r": [python_rule21],
    "s": [python_rule21],
    "t": [python_rule21],
    "u": [python_rule21],
    "v": [python_rule21],
    "w": [python_rule21],
    "x": [python_rule21],
    "y": [python_rule21],
    "z": [python_rule21],
    "|": [python_rule17],
    "~": [python_rule19],
}

# x.rulesDictDict for python mode.
rulesDictDict = {
    "python_main": rulesDict1,
}
#@-<< Rules Dicts >>

# Import dict for python mode.
importDict = {}
#@-leo

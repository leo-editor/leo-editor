#@+leo-ver=5-thin
#@+node:ekr.20210219115553.109: * @file ../modes/python.py
#@@language python
# Leo colorizer control file for python mode.
# This file is in the public domain.

import re
import string
import sys
from leo.core import leoGlobals as g
assert g

v1, v2, junk1, junk2, junk3 = sys.version_info

# Properties for python mode.
properties = {
    "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "#",
}

#@+<< Python attributes dicts >>
#@+node:ekr.20230419163615.1: ** << Python attributes dicts >>

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
#@-<< Python attributes dicts >>
#@+<< Python keywords dicts >>
#@+node:ekr.20230419163648.1: ** << Python keywords dicts >>
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
    "async": "keyword1",
    "await": "keyword1",
    "bool": "keyword2",
    "break": "keyword1",
    "buffer": "keyword2",
    "bytes": "keyword2",
    "callable": "keyword2",
    "chr": "keyword2",
    "class": "keyword1",
    "@classmethod": "keyword2",
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
    "@staticmethod": "keyword2",
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
    "with": "keyword1",
    "xrange": "keyword2",
    "yield": "keyword1",
    "zip": "keyword2",
}

# Dictionary of keywords dictionaries for python mode.
keywordsDictDict = {
    "python_main": python_main_keywords_dict,
}
#@-<< Python keywords dicts >>
#@+<< Python rules >>
#@+node:ekr.20230419163736.1: ** << Python rules >>
#@+others
#@+node:ekr.20230419163819.1: *3* python_comment
def python_comment(colorer, s, i):
    """
    Switch to md coloring if s is '# %% [markdown]', provided that c.p.b
    contains @language jupytext.
    
    New in Leo 6.8.3.
    """
    trace = 'coloring' in g.app.debug and not g.unitTesting

    try:
        c = colorer.c
    except Exception:
        return 0  # Fail, allowing other matches.

    # Always colorize the comment line as a *python* comment.
    n = colorer.match_eol_span(s, i, kind="comment1", seq="#")

    # Leo 6.8.3. Add special case for @language jupytext.
    in_jupytext_tree = any(
        z.startswith('@language jupytext')
        for z_p in c.p.self_and_parents()
        for z in g.splitLines(z_p.b)
    )
    is_any_jupytext_comment = (
        i == 0
        and s.startswith('# %%')
        and in_jupytext_tree
    )
    if is_any_jupytext_comment:
        # Simulate @language md or @language python.
        language = 'md' if s.startswith('# %% [markdown]') else 'python'
        if trace:
            print('')
            g.trace(f"init_mode({language}) {c.p.h}")
        colorer.init_mode(language)
        state_i = colorer.setInitialStateNumber()
        colorer.setState(state_i)

    return n  # Succeed. Do not allow other matches.
#@+node:ekr.20230419163819.4: *3* python_double_quote
def python_double_quote(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")
#@+node:ekr.20230419163819.2: *3* python_double_quote_docstring
def python_double_quote_docstring(colorer, s, i):
    c = colorer.c
    seq = '"""'
    if not g.match(s, i, seq):
        return 0
    rest_flag = c.config.getBool('color-doc-parts-as-rest', default=False)
    delegate = 'rest' if rest_flag else None
    return colorer.match_span(s, i, kind='literal2', begin=seq, end=seq, delegate=delegate)
#@+node:ekr.20231209010502.1: *3* python_fstring (not used)
def python_fstring(colorer, s, i):
    return colorer.match_fstring(s, i)
#@+node:ekr.20230419163819.22: *3* python_keyword
def python_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)
#@+node:ekr.20240213104932.1: *3* python_len_op1 (all single-character ops)
def python_op1(colorer, s, i):
    """Color a s[i] as an operator."""
    colorer.colorRangeWithTag(s, i, i + 1, tag='operator')
    return 1
#@+node:ekr.20240213105320.1: *3* python_number
# Does not include suffixes or hex digits.
int_s = r'[0-9]+'
float_s = fr'{int_s}\.({int_s})?'
number_pat = re.compile(fr'({float_s}|{int_s})')

def python_number(colorer, s, i):
    if 1:  # Legacy: don't colorize numbers.
        return 0

    # New, experimental.
    n = colorer.match_seq_regexp(s, i, kind='number', regexp=number_pat)
    # print(f"python_number: i: {i:3} n: {n:2} {s[i : i + n]!r}")
    return n
#@+node:ekr.20240213103850.1: *3* python_op_gt/lt & helpers
def python_op_gt(colorer, s, i):
    """Color '>=' and '>'. """
    n = 2 if s[i : i + 2] == '>=' else 1
    colorer.colorRangeWithTag(s, i, i + n, tag='operator')
    return n

def python_op_lt(colorer, s, i):
    """Color '<=' and '<'. """
    n = 2 if s[i : i + 2] == '<=' else 1
    colorer.colorRangeWithTag(s, i, i + n, tag='operator')
    return n
#@+node:ekr.20230419163931.1: *3* python_rule_h/f_url (not used)
if 0:
    url = False

    if url:
        h_url_regex = r"""(http|https)://[^\s'"]+[\w=/]"""
        f_url_regex = r"""(file|ftp)://[^\s'"]+[\w=/]"""

        def python_h_url(colorer, s, i):
            return colorer.match_seq_regexp(s, i, kind="keyword", regexp=h_url_regex)

        def python_f_url(colorer, s, i):
            return colorer.match_seq_regexp(s, i, kind="keyword", regexp=f_url_regex)

    else:
        # Always fail.
        def python_h_url(colorer, s, i):
            return 0

        def python_f_url(colorer, s, i):
            return 0
#@+node:ekr.20230419163819.5: *3* python_single_quote
def python_single_quote(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")
#@+node:ekr.20230419163819.3: *3* python_single_quote_docstring
def python_single_quote_docstring(colorer, s, i):
    c = colorer.c
    seq = "'''"
    if not g.match(s, i, seq):
        return 0
    rest_flag = c.config.getBool('color-doc-parts-as-rest', default=False)
    delegate = 'rest' if rest_flag else None
    return colorer.match_span(s, i, kind='literal2', begin=seq, end=seq, delegate=delegate)
#@-others
#@-<< Python rules >>
#@+<< Python rules dicts >>
#@+node:ekr.20230419164059.1: ** << Python rules dicts >>
# Rules dict for python_main ruleset.
rulesDict1 = {
    # Operators of length 1.
    "!": [python_op1],
    "%": [python_op1],
    "&": [python_op1],
    "|": [python_op1],
    "~": [python_op1],
    "*": [python_op1],
    "+": [python_op1],
    "-": [python_op1],
    "/": [python_op1],
    "=": [python_op1],
    "^": [python_op1],

    # Operators of length 1 or 2.
    "<": [python_op_lt],
    ">": [python_op_gt],

    # Quotes and quotes.
    '"': [python_double_quote_docstring, python_double_quote],
    "'": [python_single_quote_docstring, python_single_quote],
    "#": [python_comment],

    # Numbers...
    ".": [python_number],
    "0": [python_number],
    "1": [python_number],
    "2": [python_number],
    "3": [python_number],
    "4": [python_number],
    "5": [python_number],
    "6": [python_number],
    "7": [python_number],
    "8": [python_number],
    "9": [python_number],
}

# Add *all* characters that could start a Python identifier.
lead_ins = string.ascii_letters + '_'
for lead_in in lead_ins:
    aList = rulesDict1.get(lead_in, [])
    if python_keyword not in aList:
        aList.insert(0, python_keyword)
        rulesDict1[lead_in] = aList

if False:  # #3770: Revert colorizing of PEP 701 f-strings.
    if (v1, v2) >= (3, 12):
        # Update rules to for Python 3.12+ f-strings.
        for key in 'frFR':
            rulesDict1[key] = [python_fstring, python_keyword]

# x.rulesDictDict for python mode.
rulesDictDict = {
    "python_main": rulesDict1,
}
#@-<< Python rules dicts >>

# Import dict for python mode.
importDict = {}
#@-leo

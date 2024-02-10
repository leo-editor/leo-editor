#@+leo-ver=5-thin
#@+node:ekr.20240202211600.1: * @file ../modes/nim.py
#@@language python
# Leo colorizer control file for nim mode.
# This file is in the public domain.

import re
import sys
from leo.core import leoGlobals as g
assert g

v1, v2, junk1, junk2, junk3 = sys.version_info

#@+<< Nim attributes dicts >>
#@+node:ekr.20240202211600.2: ** << Nim attributes dicts >>
# Properties for nim mode.
properties = {
    "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "#",
}

# Attributes dict for nim_main ruleset.
nim_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for nim mode.
attributesDictDict = {
    "nim_main": nim_main_attributes_dict,
}
#@-<< Nim attributes dicts >>

# Keywords dict for nim_main ruleset.
nim_main_keywords_dict = {
    #@+<< Nim keywords >>
    #@+node:ekr.20240203080736.1: ** << Nim keywords >> (keyword1)
    # Some are reserved for future use.
    "addr": "keyword1",
    "and": "keyword1",
    "as": "keyword1",
    "asm": "keyword1",
    "bind": "keyword1",
    "block": "keyword1",
    "break": "keyword1",
    "case": "keyword1",
    "cast": "keyword1",
    "concept": "keyword1",
    "const": "keyword1",
    "continue": "keyword1",
    "converter": "keyword1",
    "defer": "keyword1",
    "discard": "keyword1",
    "distinct": "keyword1",
    "div": "keyword1",
    "do": "keyword1",
    "elif": "keyword1",
    "else": "keyword1",
    "end": "keyword1",
    "enum": "keyword1",
    "except": "keyword1",
    "export": "keyword1",
    "finally": "keyword1",
    "for": "keyword1",
    "from": "keyword1",
    "func": "keyword1",
    "if": "keyword1",
    "import": "keyword1",
    "in": "keyword1",
    "include": "keyword1",
    "interface": "keyword1",
    "is": "keyword1",
    "isnot": "keyword1",
    "iterator": "keyword1",
    "let": "keyword1",
    "macro": "keyword1",
    "method": "keyword1",
    "mixin": "keyword1",
    "mod": "keyword1",
    "nil": "keyword1",
    "not": "keyword1",
    "notin": "keyword1",
    "object": "keyword1",
    "of": "keyword1",
    "or": "keyword1",
    "out": "keyword1",
    "proc": "keyword1",
    "ptr": "keyword1",
    "raise": "keyword1",
    "ref": "keyword1",
    "return": "keyword1",
    "shl": "keyword1",
    "shr": "keyword1",
    "static": "keyword1",
    "template": "keyword1",
    "try": "keyword1",
    "tuple": "keyword1",
    "type": "keyword1",
    "using": "keyword1",
    "var": "keyword1",
    "when": "keyword1",
    "while": "keyword1",
    "xor": "keyword1",
    "yield": "keyword1",
    #@-<< Nim keywords >>
    #@+<< Nim type names >>
    #@+node:ekr.20240203094444.1: ** << Nim type names >> (keyword1)
    # Type names should be colorized like reserved words.

    # Defined in std/unicode.
    "Rune": "keyword1",

    # Defined in system module...
    "any": "keyword1",
    "array": "keyword1",
    "auto": "keyword1",
    "bool": "keyword1",
    "byte": "keyword1",
    "char": "keyword1",
    "csize": "keyword1",
    "cstring": "keyword1",
    "float": "keyword1",
    "float32": "keyword1",
    "float64": "keyword1",
    "int": "keyword1",
    "int8": "keyword1",
    "int16": "keyword1",
    "int32": "keyword1",
    "int64": "keyword1",
    "lent": "keyword1",
    "iterable": "keyword1",
    "openArray": "keyword1",
    "owned": "keyword1",
    "pointer": "keyword1",
    "range": "keyword1",
    "seq": "keyword1",
    "set": "keyword1",
    "sink": "keyword1",
    "string": "keyword1",
    "typed": "keyword1",
    "typedesc": "keyword1",
    "uint": "keyword1",
    "uint8": "keyword1",
    "uint16": "keyword1",
    "uint32": "keyword1",
    "uint64": "keyword1",
    "untyped": "keyword1",
    "varargs": "keyword1",
    "void": "keyword1",
    #@-<< Nim type names >>
    #@+<< Nim constants >>
    #@+node:ekr.20240203093634.1: ** << Nim constants >> (keyword2)
    "false": "keyword2",
    "none": "keyword2",
    "true": "keyword2",
    #@-<< Nim constants >>
    # https://nim-lang.org/docs/system.html
    #@+<< Nim upper-case constants >>
    #@+node:ekr.20240203194744.1: ** << Nim upper-case constants >> (keyword3)
    # Upper-case names are constants.

    "ATOMIC_ACQUIRE": "keyword3",
    "ATOMIC_ACQ_REL": "keyword3",
    "ATOMIC_CONSUME": "keyword3",
    "ATOMIC_RELAXED": "keyword3",
    "ATOMIC_RELEASE": "keyword3",
    "ATOMIC_SEQ_CST": "keyword3",

    "AccessViolationDefect": "keyword3",
    "AccessViolationError": "keyword3",
    "AllocStats": "keyword3",
    "ArithmeticDefect": "keyword3",
    "ArithmeticError": "keyword3",
    "AssertionDefect": "keyword3",
    "AssertionError": "keyword3",
    "AtomMemModel": "keyword3",
    "AtomType": "keyword3",

    "BackwardsIndex": "keyword3",
    "BiggestFloat": "keyword3",
    "BiggestInt": "keyword3",
    "BiggestUInt": "keyword3",
    "ByteAddress": "keyword3",

    "CatchableError": "keyword3",
    "Channel": "keyword3",
    "CompileDate": "keyword3",
    "CompileTime": "keyword3",

    "DeadThreadDefect": "keyword3",
    "DeadThreadError": "keyword3",
    "Defect": "keyword3",
    "DivByZeroDefect": "keyword3",
    "DivByZeroError": "keyword3",

    "EOFError": "keyword3",
    "Endianness": "keyword3",
    "Exception": "keyword3",
    "ExecIOEffect": "keyword3",

    "FieldDefect": "keyword3",
    "FieldError": "keyword3",
    "File": "keyword3",
    "FileHandle": "keyword3",
    "FileMode": "keyword3",
    "FileSeekPos": "keyword3",
    "FloatDivByZeroDefect": "keyword3",
    "FloatDivByZeroError": "keyword3",
    "FloatInexactDefect": "keyword3",
    "FloatInexactError": "keyword3",
    "FloatInvalidOpDefect": "keyword3",
    "FloatInvalidOpError": "keyword3",
    "FloatOverflowDefect": "keyword3",
    "FloatOverflowError": "keyword3",
    "FloatUnderflowDefect": "keyword3",
    "FloatUnderflowError": "keyword3",
    "FloatingPointDefect": "keyword3",
    "FloatingPointError": "keyword3",
    "ForLoopStmt": "keyword3",
    "ForeignCell": "keyword3",

    "GC_Strategy": "keyword3",
    "GC_collectZct": "keyword3",
    "GC_disable": "keyword3",
    "GC_disableMarkAndSweep": "keyword3",
    "GC_enable": "keyword3",
    "GC_enableMarkAndSweep": "keyword3",
    "GC_fullCollect": "keyword3",
    "GC_getStatistics": "keyword3",
    "GC_ref": "keyword3",
    "GC_unref": "keyword3",

    "HSlice": "keyword3",

    "IOEffect": "keyword3",
    "IOError": "keyword3",
    "IndexDefect": "keyword3",
    "IndexError": "keyword3",
    "Inf": "keyword3",

    "JsRoot": "keyword3",

    "KeyError": "keyword3",

    "LibraryError": "keyword3",

    "NaN": "keyword3",
    "Natural": "keyword3",
    "NegInf": "keyword3",
    "NilAccessDefect": "keyword3",
    "NilAccessError": "keyword3",
    "NimMajor": "keyword3",
    "NimMinor": "keyword3",
    "NimNode": "keyword3",
    "NimPatch": "keyword3",
    "NimVersion": "keyword3",

    "OSError": "keyword3",
    "ObjectAssignmentDefect": "keyword3",
    "ObjectAssignmentError": "keyword3",
    "ObjectConversionDefect": "keyword3",
    "ObjectConversionError": "keyword3",
    "Ordinal": "keyword3",
    "OutOfMemDefect": "keyword3",
    "OutOfMemError": "keyword3",
    "OverflowDefect": "keyword3",
    "OverflowError": "keyword3",

    "PFloat32": "keyword3",
    "PFloat64": "keyword3",
    "PFrame": "keyword3",
    "PInt32": "keyword3",
    "PInt64": "keyword3",
    "Positive": "keyword3",

    "QuitFailure": "keyword3",
    "QuitSuccess": "keyword3",

    "RangeDefect": "keyword3",
    "RangeError": "keyword3",
    "ReadIOEffect": "keyword3",
    "ReraiseDefect": "keyword3",
    "ReraiseError": "keyword3",
    "ResourceExhaustedError": "keyword3",
    "RootEffect": "keyword3",
    "RootObj": "keyword3",
    "RootRef": "keyword3",

    "Slice": "keyword3",
    "SomeFloat": "keyword3",
    "SomeInteger": "keyword3",
    "SomeNumber": "keyword3",
    "SomeOrdinal": "keyword3",
    "SomeSignedInt": "keyword3",
    "SomeUnsignedInt": "keyword3",
    "StackOverflowDefect": "keyword3",
    "StackOverflowError": "keyword3",
    "StackTraceEntry": "keyword3",

    "TFrame": "keyword3",
    "TaintedString": "keyword3",
    "Thread": "keyword4",
    "TimeEffect": "keyword3",
    "TypeOfMode": "keyword3",

    "UncheckedArray": "keyword3",
    "Utf16Char": "keyword3",
    "ValueError": "keyword3",

    "WideCString": "keyword3",
    "WideCStringObj": "keyword3",
    "WriteIOEffect": "keyword3",
    #@-<< Nim upper-case constants >>
    #@+<< Nim lower-case functions >>
    #@+node:ekr.20240203080936.1: ** << Nim lower-case functions >> (keyword4)
    # From the unitcode module.
    "runes": "keyword4",

    # From the system module...
    "abs": "keyword4",
    "add": "keyword4",
    "addEscapedChar": "keyword4",
    "addFloat": "keyword4",
    "addInt": "keyword4",
    "addQuitProc": "keyword4",
    "addQuoted": "keyword4",
    "alignof": "keyword4",
    "alloc": "keyword4",
    "alloc0": "keyword4",
    "alloc0Impl": "keyword4",
    "allocCStringArray": "keyword4",
    "allocImpl": "keyword4",
    "allocShared": "keyword4",
    "allocShared0": "keyword4",
    "allocShared0Impl": "keyword4",
    "allocSharedImpl": "keyword4",
    "appType": "keyword4",
    "arrayWith": "keyword4",
    "ashr": "keyword4",
    "assert": "keyword4",
    "astToStr": "keyword4",
    "atomicAddFetch": "keyword4",
    "atomicAlwaysLockFree": "keyword4",
    "atomicAndFetch": "keyword4",
    "atomicClear": "keyword4",
    "atomicCompareExchange": "keyword4",
    "atomicCompareExchangeN": "keyword4",
    "atomicDec": "keyword4",
    "atomicExchange": "keyword4",
    "atomicExchangeN": "keyword4",
    "atomicFetchAdd": "keyword4",
    "atomicFetchAnd": "keyword4",
    "atomicFetchNand": "keyword4",
    "atomicFetchOr": "keyword4",
    "atomicFetchSub": "keyword4",
    "atomicFetchXor": "keyword4",
    "atomicInc": "keyword4",
    "atomicIsLockFree": "keyword4",
    "atomicLoad": "keyword4",
    "atomicLoadN": "keyword4",
    "atomicNandFetch": "keyword4",
    "atomicOrFetch": "keyword4",
    "atomicSignalFence": "keyword4",
    "atomicStore": "keyword4",
    "atomicStoreN": "keyword4",
    "atomicSubFetch": "keyword4",
    "atomicTestAndSet": "keyword4",
    "atomicThreadFence": "keyword4",
    "atomicXorFetch": "keyword4",

    "capacity": "keyword4",
    "card": "keyword4",
    "cas": "keyword4",
    "cchar": "keyword4",
    "cdouble": "keyword4",
    "cfloat": "keyword4",
    "chr": "keyword4",
    "cint": "keyword4",
    "clamp": "keyword4",
    "clong": "keyword4",
    "clongdouble": "keyword4",
    "clonglong": "keyword4",
    "close": "keyword4",
    "closureScope": "keyword4",
    "cmp": "keyword4",
    "cmpMem": "keyword4",
    "compileOption": "keyword4",
    "compiles": "keyword4",
    "contains": "keyword4",
    "copyMem": "keyword4",
    "countdown": "keyword4",
    "countup": "keyword4",
    "cpuEndian": "keyword4",
    "cpuRelax": "keyword4",
    "create": "keyword4",
    "createShared": "keyword4",
    "createSharedU": "keyword4",
    "createThread": "keyword4",
    "createU": "keyword4",
    "cschar": "keyword4",
    "cshort": "keyword4",
    "csize_t": "keyword4",
    "cstringArray": "keyword4",
    "cstringArrayToSeq": "keyword4",
    "cuchar": "keyword4",
    "cuint": "keyword4",
    "culong": "keyword4",
    "culonglong": "keyword4",
    "currentSourcePath": "keyword4",
    "cushort": "keyword4",

    "dealloc": "keyword4",
    "deallocCStringArray": "keyword4",
    "deallocHeap": "keyword4",
    "deallocImpl": "keyword4",
    "deallocShared": "keyword4",
    "deallocSharedImpl": "keyword4",
    "debugEcho": "keyword4",
    "dec": "keyword4",
    "declared": "keyword4",
    "declaredInScope": "keyword4",
    "deepCopy": "keyword4",
    "default": "keyword4",
    "defined": "keyword4",
    "del": "keyword4",
    "delete": "keyword4",
    "disarm": "keyword4",
    "dispose": "keyword4",
    "doAssert": "keyword4",
    "doAssertRaises": "keyword4",
    "dumpAllocstats": "keyword4",

    "echo": "keyword4",
    "endOfFile": "keyword4",
    "ensureMove": "keyword4",
    "equalMem": "keyword4",
    "errorMessageWriter": "keyword4",
    "excl": "keyword4",

    "failedAssertImpl": "keyword4",
    "fence": "keyword4",
    "fieldPairs": "keyword4",
    "fields": "keyword4",
    "find": "keyword4",
    "finished": "keyword4",
    "flushFile": "keyword4",
    "formatErrorIndexBound": "keyword4",
    "formatFieldDefect": "keyword4",
    "freeShared": "keyword4",

    "gcInvariant": "keyword4",
    "getAllocStats": "keyword4",
    "getCurrentException": "keyword4",
    "getCurrentExceptionMsg": "keyword4",
    "getFileHandle": "keyword4",
    "getFilePos": "keyword4",
    "getFileSize": "keyword4",
    "getFrame": "keyword4",
    "getFrameState": "keyword4",
    "getFreeMem": "keyword4",
    "getFreeSharedMem": "keyword4",
    "getGcFrame": "keyword4",
    "getMaxMem": "keyword4",
    "getOccupiedMem": "keyword4",
    "getOccupiedSharedMem": "keyword4",
    "getOsFileHandle": "keyword4",
    "getStackTrace": "keyword4",
    "getStackTraceEntries": "keyword4",
    "getThreadId": "keyword4",
    "getTotalMem": "keyword4",
    "getTotalSharedMem": "keyword4",
    "getTypeInfo": "keyword4",
    "globalRaiseHook": "keyword4",
    "gorge": "keyword4",
    "gorgeEx": "keyword4",

    "handle": "keyword4",
    "high": "keyword4",
    "hostCPU": "keyword4",
    "hostOS": "keyword4",

    "inc": "keyword4",
    "incl": "keyword4",
    "insert": "keyword4",
    "instantiationInfo": "keyword4",
    "internalNew": "keyword4",
    "isMainModule": "keyword4",
    "isNil": "keyword4",
    "isNotForeign": "keyword4",
    "items": "keyword4",
    "iterToProc": "keyword4",

    "joinThread": "keyword4",
    "joinThreads": "keyword4",

    "len": "keyword4",
    "likely": "keyword4",
    "lines": "keyword4",
    "localRaiseHook": "keyword4",
    "locals": "keyword4",
    "low": "keyword4",

    "max": "keyword4",
    "min": "keyword4",
    "mitems": "keyword4",
    "move": "keyword4",
    "moveMem": "keyword4",
    "mpairs": "keyword4",

    "new": "keyword4",
    "newException": "keyword4",
    "newSeq": "keyword4",
    "newSeqOfCap": "keyword4",
    "newSeqUninitialized": "keyword4",
    "newString": "keyword4",
    "newStringOfCap": "keyword4",
    "newWideCString": "keyword4",
    "nimGC_setStackBottom": "keyword4",
    "nimThreadDestructionHandlers": "keyword4",
    "nimThreadProcWrapperBody": "keyword4",
    "nimvm": "keyword4",

    "off": "keyword4",
    "offsetOf": "keyword4",
    "on": "keyword4",
    "onFailedAssert": "keyword4",
    "onThreadDestruction": "keyword4",
    "onUnhandledException": "keyword4",
    "once": "keyword4",
    "open": "keyword4",
    "ord": "keyword4",
    "outOfMemHook": "keyword4",

    "pairs": "keyword4",
    "peek": "keyword4",
    "pinToCpu": "keyword4",
    "pop": "keyword4",
    "popGcFrame": "keyword4",
    "pred": "keyword4",
    "prepareMutation": "keyword4",
    "procCall": "keyword4",
    "programResult": "keyword4",
    "protect": "keyword4",
    "pushGcFrame": "keyword4",

    "quit": "keyword4",

    "raiseAssert": "keyword4",
    "rangeCheck": "keyword4",
    "rawEnv": "keyword4",
    "rawProc": "keyword4",
    "readAll": "keyword4",
    "readBuffer": "keyword4",
    "readBytes": "keyword4",
    "readChar": "keyword4",
    "readChars": "keyword4",
    "readFile": "keyword4",
    "readLine": "keyword4",
    "readLines": "keyword4",
    "ready": "keyword4",
    "realloc": "keyword4",
    "realloc0": "keyword4",
    "realloc0Impl": "keyword4",
    "reallocImpl": "keyword4",
    "reallocShared": "keyword4",
    "reallocShared0": "keyword4",
    "reallocShared0Impl": "keyword4",
    "reallocSharedImpl": "keyword4",
    "recv": "keyword4",
    "reopen": "keyword4",
    "repr": "keyword4",
    "reprDiscriminant": "keyword4",
    "reset": "keyword4",
    "resize": "keyword4",
    "resizeShared": "keyword4",
    "runnableExamples": "keyword4",
    "running": "keyword4",

    "send": "keyword4",
    "setControlCHook": "keyword4",
    "setCurrentException": "keyword4",
    "setFilePos": "keyword4",
    "setFrame": "keyword4",
    "setFrameState": "keyword4",
    "setGcFrame": "keyword4",
    "setInheritable": "keyword4",
    "setLen": "keyword4",
    "setStdIoUnbuffered": "keyword4",
    "setupForeignThreadGc": "keyword4",
    "shallow": "keyword4",
    "shallowCopy": "keyword4",
    "sizeof": "keyword4",
    "slurp": "keyword4",
    "stackTraceAvailable": "keyword4",
    "staticExec": "keyword4",
    "staticRead": "keyword4",
    "stderr": "keyword4",
    "stdin": "keyword4",
    "stdmsg": "keyword4",
    "stdout": "keyword4",
    "substr": "keyword4",
    "succ": "keyword4",
    "swap": "keyword4",

    "tearDownForeignThreadGc": "keyword4",
    "toBiggestFloat": "keyword4",
    "toBiggestInt": "keyword4",
    "toFloat": "keyword4",
    "toInt": "keyword4",
    "toOpenArray": "keyword4",
    "toOpenArrayByte": "keyword4",
    "tryRecv": "keyword4",
    "trySend": "keyword4",
    "typeof": "keyword4",

    "unhandledExceptionHook": "keyword4",
    "unlikely": "keyword4",
    "unown": "keyword4",
    "unsafeAddr": "keyword4",
    "unsafeNew": "keyword4",
    "unsetControlCHook": "keyword4",

    "varargsLen": "keyword4",

    "wasMoved": "keyword4",
    "write": "keyword4",
    "writeBuffer": "keyword4",
    "writeBytes": "keyword4",
    "writeChars": "keyword4",
    "writeFile": "keyword4",
    "writeLine": "keyword4",
    "writeStackTrace": "keyword4",

    "zeroDefault": "keyword4",
    "zeroMem": "keyword4",
    #@-<< Nim lower-case functions >>
}

# Dictionary of keywords dictionaries for nim mode.
keywordsDictDict = {
    "nim_main": nim_main_keywords_dict,
}

#@+<< Nim rules >>
#@+node:ekr.20240202211600.4: ** << Nim rules >>
#@+others
#@+node:ekr.20240207062639.1: *3* nim_character_literal
def nim_character_literal(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")
#@+node:ekr.20240202211600.5: *3* nim_comment (comment1)
def nim_comment(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")
#@+node:ekr.20240208152632.8: *3* nim_unusual_single_quote (keyword1)
# Note: The suffix comes *before* the single quote.
lower_suffixes = [
    z for z in ('b,e,f,o,x,i,i8,i16,i32,i64,u,u8,u16,u32,u64').split(',')
]
suffixes = tuple(lower_suffixes + [z.upper() for z in lower_suffixes])
word_pattern = re.compile(r'\b(\w+)')

def nim_unusual_single_quote(colorer, s, i):
    """
    Handle unusual single quotes, including custom_numeric_literals.
    
    Color all such single quotes as a keyword1.
    """

    def fail() -> int:
        # Color a prefixed "'" as a keyword.
        if i > 0 and s[i - 1] in colorer.word_chars:
            colorer.colorRangeWithTag(s, i, i + 1, tag='keyword1')
            return 1
        return 0

    # Find the suffix.
    assert s[i : i + 1] == "'", repr(s)
    head = s[:i]
    for suffix in suffixes:
        if head.endswith(suffix):
            break
    else:
        return fail()  # pragma: no cover

    # Make sure the suffix is a word.
    j = i - len(suffix)
    is_word = j == 0 or j > 0 and s[j - 1] not in colorer.word_chars
    if not is_word:
        return fail()  # pragma: no cover

    # Find the preceding word.
    m = word_pattern.match(s, i + 1)
    if not m:
        return fail()  # pragma: no cover

    # Color the suffix.
    colorer.colorRangeWithTag(s, i - len(suffix), i, tag='literal1')

    # Color the single quote.
    colorer.colorRangeWithTag(s, i, i + 1, tag='keyword1')

    # Color the following word.
    word = m.group(0)
    colorer.colorRangeWithTag(s, i + 1, i + 1 + len(word), tag='literal1')
    return 1 + len(word)
#@+node:ekr.20240202211600.26: *3* nim_keyword (keyword1)
def nim_keyword(colorer, s, i):
    return colorer.match_keywords(s, i)
#@+node:ekr.20240206040507.1: *3* nim_multi_line_comment (comment2)
def nim_multi_line_comment(colorer, s, i):

    return colorer.match_span(s, i,
        kind="comment2", begin="#[", end="]#", nested=True)
#@+node:ekr.20240206033640.1: *3* nim_number (do-nothing)
# Only an approximation.
# Underscores are allowed in numbers.
number_regex = re.compile(r'([0-9_]+)(b|B|d|D|f|F|i|I|u|U|x|X|32|64)*')

def nim_number(colorer, s, i):
    # return colorer.match_compiled_regexp(s, i, 'literal2', regexp=number_regex)
    return 0
#@+node:ekr.20240206051847.1: *3* nim_op (do-nothing)
def nim_op(colorer, s: str, i: int) -> int:
    # Don't color ordinary ops.
    return 0
#@+node:ekr.20240202211600.8: *3* nim_string (literal1)
def nim_string(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")
#@+node:ekr.20240202211600.6: *3* nim_triple_quote (literal2)
def nim_triple_quote(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"")
#@+node:ekr.20240206062831.1: *3* nim_unary (do-nothing
unary_pattern = re.compile(r'(\+|\-)')

def nim_unary(colorer, s, i):
    # return colorer.match_seq_regexp(s, i, kind="keyword1", regexp=unary_pattern)
    return 0
#@-others
#@-<< Nim rules >>
#@+<< nim_rules_dict >>
#@+node:ekr.20240202211600.29: ** << nim_rules_dict >>
# Rules dict for nim_main ruleset.
nim_rules_dict = {
    '"': [nim_triple_quote, nim_string],
    "#": [nim_multi_line_comment, nim_comment],
    "'": [nim_unusual_single_quote, nim_character_literal],
    ".": [nim_number, nim_op],
    "+": [nim_unary],
    "-": [nim_unary],
    "0": [nim_number],
    "1": [nim_number],
    "2": [nim_number],
    "3": [nim_number],
    "4": [nim_number],
    "5": [nim_number],
    "6": [nim_number],
    "7": [nim_number],
    "8": [nim_number],
    "9": [nim_number],
    "A": [nim_keyword],
    "B": [nim_keyword],
    "C": [nim_keyword],
    "D": [nim_keyword],
    "E": [nim_keyword],
    "F": [nim_keyword],
    "G": [nim_keyword],
    "H": [nim_keyword],
    "I": [nim_keyword],
    "J": [nim_keyword],
    "K": [nim_keyword],
    "L": [nim_keyword],
    "M": [nim_keyword],
    "N": [nim_keyword],
    "O": [nim_keyword],
    "P": [nim_keyword],
    "Q": [nim_keyword],
    "R": [nim_keyword],
    "S": [nim_keyword],
    "T": [nim_keyword],
    "U": [nim_keyword],
    "V": [nim_keyword],
    "W": [nim_keyword],
    "X": [nim_keyword],
    "Y": [nim_keyword],
    "Z": [nim_keyword],
    "_": [nim_keyword],
    "a": [nim_keyword],
    "b": [nim_keyword],
    "c": [nim_keyword],
    "d": [nim_keyword],
    "e": [nim_keyword],
    "f": [nim_keyword],
    "g": [nim_keyword],
    "h": [nim_keyword],
    "i": [nim_keyword],
    "j": [nim_keyword],
    "k": [nim_keyword],
    "l": [nim_keyword],
    "m": [nim_keyword],
    "n": [nim_keyword],
    "o": [nim_keyword],
    "p": [nim_keyword],
    "q": [nim_keyword],
    "r": [nim_keyword],
    "s": [nim_keyword],
    "t": [nim_keyword],
    "u": [nim_keyword],
    "v": [nim_keyword],
    "w": [nim_keyword],
    "x": [nim_keyword],
    "y": [nim_keyword],
    "z": [nim_keyword],
    # The following are all do-notings.
    "!": [nim_op],
    "%": [nim_op],
    "&": [nim_op],
    "(": [nim_op],
    "*": [nim_op],
    "/": [nim_op],
    "<": [nim_op],
    "=": [nim_op],
    ">": [nim_op],
    "@": [nim_op],
    "^": [nim_op],
    "|": [nim_op],
    "~": [nim_op],
}
#@-<< nim_rules_dict >>

rulesDictDict = {
    "nim_main": nim_rules_dict,
}

# Import dict for nim mode.
importDict = {}
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20230203163544.1: * @file tracing_utils.py
"""
Stand-alone tracing and debugging functions.

Leonista's are welcome to use this file in their own projects.

Leo does not use this file.

Unlike the corresponding functions in leoGlobals.py,
all names in this file are pep8 compliant.
"""

import os
import pprint
import sys
import traceback
from typing import Any, Sequence


#@+others
#@+node:ekr.20230203163544.2: ** tracing_utils._caller_name
def _caller_name(n: int) -> str:
    """Return the name of the caller n levels back in the call stack."""
    try:
        # Get the function name from the call stack.
        frame = sys._getframe(n)  # The stack frame, n levels up.
        code = frame.f_code  # The code object
        locals_ = frame.f_locals  # The local namespace.
        name = code.co_name
        obj = locals_.get("self")
        if obj and name == "__init__":
            return f"{obj.__class__.__name__}.{name}"
        return name
    except ValueError:
        # The stack is not deep enough OR
        # sys._getframe does not exist on this platform.
        return ""
    except Exception:
        return ""  # "<no caller name>"
#@+node:ekr.20230203163544.3: ** tracing_utils.caller
def caller(i: int = 1) -> str:
    """Return the caller name i levels up the call stack."""
    return callers(i + 1).split(",")[0]
#@+node:ekr.20230203163544.4: ** tracing_utils.callers
def callers(n: int = 4) -> str:
    """
    Return a string containing a comma-separated list of the calling
    function's callers.
    """
    # Be careful to call _caller_name with smaller values of i first:
    # sys._getframe throws ValueError if there are less than i entries.
    i, result = 3, []
    while 1:
        s = _caller_name(n=i)
        if s:
            result.append(s)
        if not s or len(result) >= n:
            break
        i += 1
    return ",".join(reversed(result))
#@+node:ekr.20230203163544.5: ** tracing_utils.callers_list
def callers_list(n: int = 4) -> list[str]:
    """
    Return a string containing a comma-separated list of the calling
    function's callers.
    """
    # Be careful to call _caller_name with smaller values of i first:
    # sys._getframe throws ValueError if there are less than i entries.
    i, result = 3, []
    while 1:
        s = _caller_name(n=i)
        if s:
            result.append(s)
        if not s or len(result) >= n:
            break
        i += 1
    return list(reversed(result))
#@+node:ekr.20230208054438.1: ** tracing_utils.es_exception
def es_exception(*args: Sequence, **kwargs: Sequence) -> None:
    # val is the second argument to the raise statement.
    typ, val, tb = sys.exc_info()
    for line in traceback.format_exception(typ, val, tb):
        print(line)
#@+node:ekr.20230203163544.6: ** tracing_utils.get_ctor_name
def get_ctor_name(self: Any, file_name: str, width: int = 25) -> str:
    """Return <module-name>.<class-name> padded to the given width."""
    class_name = self.__class__.__name__
    module_name = short_file_name(file_name).replace(".py", "")
    combined_name = f"{module_name}.{class_name}"
    padding = " " * max(0, 25 - len(combined_name))
    return f"{padding}{combined_name}"
#@+node:ekr.20230203163544.7: ** tracing_utils.plural
def plural(obj: Any) -> str:
    """Return "s" or "" depending on n."""
    if isinstance(obj, (list, tuple, str)):
        n = len(obj)
    else:
        n = obj
    return "" if n == 1 else "s"
#@+node:ekr.20230203163544.8: ** tracing_utils.print_obj
def print_obj(obj: Any, tag: str = None, indent: int = 0) -> None:
    """Pretty print any Python object."""
    print(to_string(obj, indent=indent, tag=tag))
#@+node:ekr.20230203163544.9: ** tracing_utils.short_file_name
def short_file_name(file_name: str) -> str:
    """Return the base name of a path."""
    return os.path.basename(file_name) if file_name else ""
#@+node:ekr.20230203163544.10: ** tracing_utils.split_lines
def split_lines(s: str) -> list[str]:
    """
    Split s into lines, preserving the number of lines and
    the endings of all lines, including the last line.

    This function is not the same as s.splitlines(True).
    """
    return s.splitlines(True) if s else []
#@+node:ekr.20230208053831.1: ** tracing_utils.to_encoded_string
def to_encoded_string(s: Any, encoding: str = 'utf-8') -> bytes:
    """Convert unicode string to an encoded string."""
    if not isinstance(s, str):
        return s
    try:
        s = s.encode(encoding, "strict")
    except UnicodeError:
        s = s.encode(encoding, "replace")
        print(f"toEncodedString: Error converting {s!r} to {encoding}")
    return s
#@+node:ekr.20230203163544.11: ** tracing_utils.to_string
def to_string(obj: Any, indent: int = 0, tag: str = None, width: int = 120) -> str:
    """
    Pretty print any Python object to a string.
    """
    if not isinstance(obj, str):
        result = pprint.pformat(obj, indent=indent, width=width)
    elif "\n" not in obj:
        result = repr(obj)
    else:
        # Return the enumerated lines of the string.
        lines = "".join([f"  {i:4}: {z!r}\n" for i, z in enumerate(split_lines(obj))])
        result = f"[\n{lines}]\n"
    return f"{tag.strip()}: {result}" if tag and tag.strip() else result
#@+node:ekr.20230208053732.1: ** tracing_utils_to_unicode
def to_unicode(s: Any, encoding: str = 'utf-8') -> str:
    """Convert bytes to unicode if necessary."""
    tag = 'g.toUnicode'
    if isinstance(s, str):
        return s
    if not isinstance(s, bytes):
        print(f"{tag}: bad s: {s!r}")
        return ''
    b: bytes = s
    try:
        s2 = b.decode(encoding, 'strict')
    except(UnicodeDecodeError, UnicodeError):  # noqa
        s2 = b.decode(encoding, 'replace')
        print(f"{tag}: unicode error. encoding: {encoding!r}, s2:\n{s2!r}")
        trace(callers())
    except Exception:
        es_exception()
        print(f"{tag}: unexpected error! encoding: {encoding!r}, s2:\n{s2!r}")
        trace(callers())
    return s2
#@+node:ekr.20230203163544.12: ** tracing_utils.trace
def trace(*args: Any) -> None:
    """Print the name of the calling function followed by all the args."""
    name = _caller_name(2)
    if name.endswith(".pyc"):
        name = name[:-1]
    args_s = " ".join(str(z) for z in args)
    print(f"{name} {args_s}")
#@+node:ekr.20230208054910.1: ** tracing_utils.truncate
def truncate(s: str, n: int) -> str:
    """Return s truncated to n characters."""
    if len(s) <= n:
        return s
    s2 = s[: n - 3] + f"...({len(s)})"
    return s2 + '\n' if s.endswith('\n') else s2
#@-others
#@-leo

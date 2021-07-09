#@+leo-ver=5-thin
#@+node:ekr.20210709045755.1: * @file ../../wax_off.py
"""
The "wax-off" utility.

Create stub files from existing annotation, then remove all function annotations.
"""
import difflib
import os
import re
# Define regex's to discover classes and defs.
class_pat = re.compile(r'^[ ]*class\s+[\w_]+.*?:', re.MULTILINE)
def_pat = re.compile(r'^([ ]*)def\s+([\w_]+)\s*\((.*?)\)(.*?):', re.MULTILINE + re.DOTALL)
# Define helper functions.
#@+others
#@+node:ekr.20210709052929.2: ** function: stripped_args
def stripped_args(s):
    """
    s is the argument list, without parens, possibly containing annotations.

    Return the argument list without annotations.
    """
    s = s.replace('\n',' ').replace('  ','').rstrip().rstrip(',')
    args, i = [], 0
    while i < len(s):
        progress = i
        arg, i = get_next_arg(s, i)
        if not arg:
            break
        args.append(arg)
        assert progress < i, (i, repr(s[i:]))
    return ', '.join(args)
#@+node:ekr.20210709052929.3: ** function: get_next_arg
name_pat = re.compile(r'\s*([\w_]+)\s*')

def get_next_arg(s, i):
    """
    Scan the next argument, retaining initializers, stripped of annotations.
    
    Return (arg, i):
    - arg: The next argument.
    - i:   The index of the character after arg.
    """
    trace = False
    assert i < len(s), (i, len(s))
    if trace:
        print('')
    m = name_pat.match(s[i:])
    if not m:
        # if trace: g.trace('no match', i, repr(s[i:]))
        return (None, len(s))
    name = m.group(0).strip()
    i += len(m.group(0))
    # if s[i:].strip():
    #    if trace: g.trace(i, 'Name', name, 'Rest:', repr(s[i:]))
    if i >= len(s):
        # if trace: g.trace(i, 'nothing after name')
        return (name, i)
    if s[i] == ':':
        # Skip the annotation.
        i += 1
        j = skip_to_outer_delim(s, i, delims="=,")
        ### annotation = s[i:j].strip()
        i =skip_ws(s, j)
        # if trace: g.trace(i, 'annotation', repr(annotation))
    if i >= len(s):
        # if trace: g.trace(i, 'nothing after annotation')
        return name, i
    if s[i] == ',':
        # if trace: g.trace(i, 'comma', repr(s[i:]))
        return name, i + 1
    # Skip the initializer.
    assert s[i] == '=', (i, s[i:])
    i += 1
    j = skip_to_outer_delim(s, i, delims=",")
    initializer = s[i:j].strip()
    # if trace: g.trace(i, 'initializer', initializer)
    if j < len(s) and s[j] == ',':
        j += 1
    i = skip_ws(s, j)
    return f"{name}={initializer}", i
    
#@+node:ekr.20210709052929.4: ** function: skip_to_outer_delim & helpers
def skip_to_outer_delim(s, i, delims):
    """
    Skip to next *outer*, ignoring inner delimis contained in strings, etc.
    
    It is valid to reach the end of s before seeing the expected delim.
    
    Return i, the character after the delim, or len(s) if the delim has not been seen.
    """
    # trace = False
    # i1 = 0  # For tracing.
    assert i < len(s), i
    # Type annotations only use [], but initializers can use anything.
    c_level, p_level, s_level = 0, 0, 0  # Levels for {}, (), []
    while i < len(s):
        ch = s[i]
        progress = i
        i += 1
        if ch in delims:
            if (c_level, p_level, s_level) == (0, 0, 0):
                # if trace: g.trace(i, 'Val1:', s[i1:i], 'Rest:', repr(s[i:]))
                return i - 1  # Let caller handle ending delim.
        elif ch == '{':
            c_level += 1
        elif ch == '}':
            c_level -= 1
        elif ch == '(':
            p_level += 1
        elif ch == ')':
            p_level -= 1
        elif ch == '[':
            s_level += 1
        elif ch == ']':
            s_level -= 1
        elif ch in "'\"":
            i = skip_string(s, i-1)
        elif ch == "#":
            i = skip_comment(s, i-1)
        else:
            pass
        assert progress < i, (i, repr(s[i:]))
    assert (c_level, p_level, s_level) == (0, 0, 0), (c_level, p_level, s_level)
    # if trace: g.trace(i, 'Val2:', s[i1:i], 'Rest:', repr(s[i:]))
    return len(s)
#@+node:ekr.20210709052929.5: *3* function: skip_comment
def skip_comment(s, i):
    """Scan forward to the end of a comment."""
    assert s[i] == '#'
    while i < len(s) and s[i] != '\n':
        i += 1
    return i
#@+node:ekr.20210709052929.6: *3* function: skip_string
def skip_string(s, i):
    """Scan forward to the end of a string."""
    delim = s[i]
    i += 1
    assert(delim == '"' or delim == '\'')
    n = len(s)
    while i < n and s[i] != delim:
        if s[i] == '\\':
            i += 2
        else:
            i += 1
    assert i < len(s) and s[i] == delim, (i, delim)
    i += 1
    return i
#@+node:ekr.20210709053410.1: *3* function: skip_ws
def skip_ws(s, i):
    while i < len(s) and s[i] in ' \t':
        i += 1
    return i
#@-others
# Define directories
output_directory = r'c:\leo.repo\leo-editor\mypy_stubs'
assert os.path.exists(output_directory), output_directory
source_directory = r'c:\leo.repo\leo-editor\leo\core'
assert os.path.exists(source_directory), source_directory
stub_directory = r'c:\leo.repo\leo-editor\mypy_stubs'
assert os.path.exists(stub_directory), stub_directory
# Define files
input_fn = os.path.join(source_directory, 'leoNodes.py')
assert os.path.exists(input_fn), input_fn
stub_fn = os.path.join(stub_directory, 'leoNodes.pyi')
new_fn = os.path.join(output_directory, 'new_leoNodes.py')
# Read the input file.
with open(input_fn, 'r') as f:
    contents = f.read()
# Find all the class defs.
n = 0
file_stubs, replacements = [], []
for m in class_pat.finditer(contents):
    class_stub = m.group(0).rstrip() + '\n'
    file_stubs.append((m.start(), class_stub))
# Find all the defs.
for m in def_pat.finditer(contents):
    n += 1
    stub = f"{m.group(0)} ...\n"
    lws = m.group(1)
    name = m.group(2)
    args = stripped_args(m.group(3))
    ret = m.group(4)
    stripped = f"{lws}def {name}({args}):"
    assert not stripped.startswith('\n'), stripped
    if 0:
        print(f"{n:>3} original: {m.group(0).rstrip()}")
        print(f"{n:>3}     stub: {stub.rstrip()}")
        print(f"{n:>3} stripped: {stripped}")
        print('')
    # Append the results.
    replacements.append((m.start(), m.group(0), stripped))
    file_stubs.append((m.start(), stub))
# Dump the replacements:
if 0:
    for i, data in enumerate(replacements):
        start, old, new = data
        print(i, start)
        print(f"{old!r}")
        print(f"{new!r}")
# Sort the stubs.
file_stubs.sort()
if 0:
    for data in file_stubs:
        start, s = data
        print(s.rstrip())
# Write the stub file.
if 1:
    with open(stub_fn, 'w') as f:
        f.write(''.join(z[1] for z in file_stubs))
    print('wrote', stub_fn)
# Compute the new contents.
new_contents = contents
for data in reversed(replacements):
    start, old, new = data
    assert new_contents[start:].startswith(old), (start, old, new_contents[start:start+50])
    new_contents = new_contents[:start] + new + new_contents[start+len(old):]
if 0:
    print('\nnew contents...\n')
    print(new_contents)
# Diff the old and new contents.
if 0:
    lines = list(difflib.unified_diff(
        contents.splitlines(True),
        new_contents.splitlines(True),
        fromfile="Old",
        tofile="New",
        n=0))
    for line in lines:
        print(repr(line))
# Write the new file.
if 1:
    with open(new_fn, 'w') as f:
        f.write(new_contents)
print(f"{len(replacements)} replacements")
#@-leo

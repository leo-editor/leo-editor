# For Devs: All About Importers

This documentation contains everything developers and maintainers need to
know about Leo's new importers. In particular, it tells how to write an
importer for a new language.

## Overview

This is the overview.
### Node 2 header

More

### Design

The typescript importer refutes that notion expressed in the middle-of-the-night post that nothing simpler than the state-scanner code can be imagined. There are at least four ways that the present code base can be simplified.

For at least some languages, including python, rescanning may be significantly simpler than v2_gen_lines and its helpers. The scan method in importers.typescript.py is shockingly simple. importers.python.py may use very similar code.

Explorations last night show that the coffeescript scanner depends very little on the base BaseScanner class. Indeed, the coffeescript scanner uses just a few of its utilities! So the coffeescript scanner could easily be adapted to the V2 scanner code in LineScanner.

It should be possible to simplify the "cassette" at the top level of each importer in leo/plugins/importers. Rather than separating the Controller and Scanner classes, a single Controller class will suffice. The coffeescript importer already uses this approach. Unifying these classes should simplify both the code, the cassette interface, and the documentation.

[Completed] A head-slapping moment. Put the LineScanner class and related stuff in a new file, linescanner.py. Doh! This will be a great aid in keeping the new and legacy code bases separate. Much less need for tests on gen_v2.

Update: 4. didn't work the first time. I made too many changes at once. The way forward was to focus on goals, namely:

Exactly one way of importing any file. This may vary from language to language. A single file, linescanner.py, containing all the supporting code. Unifying the various classes into a single Importer class. The eventual elimination of all switches.

After reverting the code, a more incremental approach did work. The plan was to remove all switches from both basescanner.py and linescanner.py. That worked very well:

basescanner.py now contains no V2 code.
linescanner.py now contains only V2 code.
The cassette interface to linescanner.py will be a single class: the Importer class.

Next: I'll start converting the best code, which is probably the coffeescript importer. I'll make that work using only code in linescanner.py. Then I'll use that template to add new importers, one language at a time.

Update: The coffeescript, javascript, perl, python and typescript importers have been fully converted. The Python importer presently uses the legacy code, based on a local switch in python.py. These conversions went much more easily than I expected.

### p.b is a huge performance bug

Fixed at e660cd2, as described below.

The old code runs unit tests quickly. The new code can cause Leo to hang for seconds. At first I thought Leo had hanged, but then it started up again...

Alas, p.b concatenates larger and larger strings. As a result, it is an O(N**2) algorithm. In contrast, concatenating strings to a list is an O(N) algorithm. I suspect, but do not know for sure, that the hangs were the result of garbage collection.

Last night I attempted to concatenate lines to a new lines list in the Target class. But this proved unexpectedly tricky. Instantly, the simplicity of the code was compromised. Worse, it didn't work ;-)

Some simple solution must be found. e660cd2 completely solves the problem:

- `i.v2_gen_lines` injects `v._importer_lines` list into the root vnode using `i.inject_lines_ivar'.

- Similarly, `i.v2_create_child_node` calls `i.inject_lines_ivar' into each created node.

- Replace `p.b = p.b + s` by `self.add_line(p, s)`.

- `i.v2_gen_lines` calls `self.finalize`, which does the following:
```python
for p in parent.self_and_subtree():
    v = p.v
    assert not v._bodyString, repr(v._bodyString)
    v._bodyString = ''.join(v._import_lines)
    delattr(v, '_import_lines')
```

The assert was helpful initially.

### Importer API for setting body text

As of 6dbeb6a, all code in stages 1, 2 and 3 must use the following API to change body text. It is easier, faster than setting p.b to strings. And it stresses the GC much less.
```python
def add_line(self, p, s):
    '''Append the line s to p.v._import_lines.'''
    assert not p.b, repr(p.b)
    assert hasattr(p.v, '_import_lines'), repr(p)
    p.v._import_lines.append(s)

def clear_lines(self, p, lines):
    p.v._import_lines = []

def extend_lines(self, p, lines):
    p.v._import_lines.extend(list(lines))

def get_lines(self, p):
    return  p.v._import_lines

def has_lines(self, p):
    return hasattr(p.v, '_import_lines')

def prepend_lines(self, p, lines):
    p.v._import_lines = list(lines) + p.v._import_lines

def set_lines(self, p, lines):
    p.v._import_lines = list(lines)
```

The actual code uses `p.v._import_lines` explicitly rather than using the get_lines or set_lines methods. It's clearer, imo.
### i.is_ws_line

This is a one-line predicate that is crucial conceptually, and greatly clarifies the code in several places.

It returns True if the line is either blank or contains nothing but leading whitespace followed by a single-line comment. v2_gen_lines must put such lines in the existing block, regardless of their indentation.

`i.undent` does not recognize the underindented line in the following (legal!) python program:
```python
if 1:
    def f():
        '''
        This
is a valid
        docstring.
        '''
        g.trace(f.__doc__)

f()
```
There is no way that `i.is_ws_line` can determine that is a valid is part of a docstring.

**Aha**: Indentation mostly doesn't matter in python!! Python blocks begin if and only if a line begins with class or def outside of any context (string, docstring or comment).
### The Importer class *is* a pipeline

@tfer Tom's importer proposal, was the first to suggest that the importers be organized as a pipeline. At first, I dismissed that suggestion, but in fact Tom's suggestions have been marinating in the back of my mind ever since. Thank you, Tom! Leo's great new importers owe a lot to you.

The new Importer class now clearly is a pipeline:

`i.run` calls `i.generate_nodes`, which explicitly calls three sub-passes:

**Stage 1: i.v2_gen_lines**

Generates all nodes in a single, non-recursive pass

**Stage 2: i.post_pass**

Runs a series of other sub-stages. The default (base-class) code is:
```python
def post_pass(self, parent):
    self.clean_all_headlines(parent)
    self.clean_all_nodes(parent)
    self.unindent_all_nodes(parent)
    #
    # This sub-pass must follow unindent_all_nodes.
    self.promote_trailing_underindented_lines(parent)
    #
    # This probably should be the last sub-pass.
    self.delete_all_empty_nodes(parent)
```
Subclasses may override `i.post_pass` for complete control over post processing.

**Stage 3: i.finish**

Does *essential* late processing. It inserts Leo directives in the root nodes and, last of all, does `p.b = p.v._import_lines` and then deletes all `v._import_lines` attributes. 

Subclasses should never have to override `i.finish`.

Furthermore, subclasses of the Importer class can easily modify code by overriding the following Importer methods:

**i.clean_headline**

This typically removed cruft from lines that define classes or defs. Py_Importer.clean_headline is one of the more complex overrides:
```python
def clean_headline(self, s):
    '''Return a cleaned up headline s.'''
    m = re.match(r'\s*def\s+(\w+)', s)
    if m:
        return m.group(1)
    else:
        m = re.match(r'\s*class\s+(\w+)', s)
        if m: return 'class %s' % m.group(1)
        else: return s.strip()
```
**Summary**

The Importer class is organized as pipeline:
- Stage 1 creates the nodes.
- Stage 2 post-processes the nodes in several sub-stages.
- Stage 3 finishes up in a language independent way.

Subclasses of the Importer class may further customize the importers by overriding severa short methods.
### Almost all importers will work the same way

After the old importer classes are retired, almost all importers will be subclasses of the Importer class, except for the following:

**json.py, and .ipynb.py** In both cases, the incoming text is a json dict, so normal import code is out of the question.

**ctext.py** The importer is very simple. It doesn't need to be a subclass of Importer.
### Most scan_line methods are table-driven

The new coffeescript.scanner is an example of the nifty new pattern. See `i.v2_scan_line` and its helpers, `i.get_new_table` and `i.scan_table`.

Here is the revised `i.v2_scan_line`. It implicitly defines a protocol that all ScanState classes must follow:
```python
def v2_scan_line(self, s, prev_state):
    '''
    A generalized scan-line method.

    SCAN STATE PROTOCOL:

    The Importer class should have a state_class ivar that references a
    **state class**. This class probably should *not* be subclass of the
    ScanState class, but it should observe the following protocol:

    1. The state class's ctor must have the following signature:

        def __init__(self, d)

    2. The state class must have an update method.
    '''
    # This dict allows new data to be added without changing ScanState signatures.
    d = {
        'indent': self.get_int_lws(s),
        'is_ws_line': self.is_ws_line(s),
        'prev':prev_state,
        's':s,
    }
    new_state = self.state_class(d)
    i = 0
    while i < len(s):
        progress = i
        context = new_state.context
        table = self.get_table(context)
        data = self.scan_table(context, i, s, table)
        i = new_state.update(data)
        assert progress < i
    return new_state
```
The tables returned by `i.get_table` describe scanning much more clearly than the blah-blah-blah of code.
### Python *does* need to handle all kinds of brackets

I'm not sure that the present python code can be made to work without understanding the nesting levels of parens, curly-brackets and square-brackets. Consider this code from @test python comment after dict assign:
```python
s = '''\
NS = { 'i': 'http://www.inkscape.org/namespaces/inkscape',
      's': 'http://www.w3.org/2000/svg',
      'xlink' : 'http://www.w3.org/1999/xlink'}

tabLevels = 4
```

This is valid code, no matter what kind of indentation is used in the dict.

To handle this, `i.scan_table` now keeps of brackets for all languages.
### i.scan_table

Note the hack for recognizing backslash. i.scan_table also adds a bs-nl flag to the returned 6-tuple. "bs-nl" can not be context!
```python
def scan_table(self, context, i, s, table):
    '''
    i.scan_table: Scan at position i of s with the give context and table.
    May be overridden in subclasses, but most importers will use this code.

    Return the 6-tuple: (new_context, i, delta_c, delta_p, delta_s, bs_nl)
    '''
    # kind,   pattern, out-ctx,     in-ctx,     delta{}, delta(), delta[]
    for kind, pattern, out_context, in_context, delta_c, delta_p, delta_s in table:
        if self.match(s, i, pattern):
            assert kind in ('all', 'len', 'len+1'), kind
            assert pattern, pattern
            # Backslash patterns must match in all contexts!
            if pattern.startswith('\\'):
                ok = True
                new_context = out_context
            elif context == '':
                ok = True
                new_context = out_context
            else:
                ok = context == pattern
                new_context = in_context
            if ok:
                assert new_context is not None, (pattern, repr(s))
                if kind == 'all':
                    i = len(s)
                elif kind == 'len+1':
                    i += (len(pattern) + 1)
                else:
                    i += len(pattern)
                bs_nl = pattern == '\\\n'
                return new_context, i, delta_c, delta_p, delta_s, bs_nl
    # No match: stay in present state. All deltas are zero.
    return context, i+1, 0, 0, 0, False
```
### state.level()

ScanState classes all define a state.level() method that returns either an int or a tuple of ints. This allows comparisons such as the following for *all* languages:
```python
if new_state.level() > prev_state.level():
    # enter new blockgs
```

There are several special cases, however.

**1: pattern matching**

Languages that use a regex pattern to determine whether a line starts a block must take care. x.starts_block must fail if prev_state.context is non-empty. In that case, the next line is in a comment or string. Here is a python example:
```python
s = r'''
def spam():
    pass
'''
```

And similarly for coffeescript.

At present, the C-language importer only counts curly brackets, but this can lead to a strange assignment of lines to block in cases such as:
```c
static void foo(bar)
{}
```
The block associated with foo will consist only of the line {}, with an unhelpful headline. The perfect import check will succeed, but the post-pass should move the int foo(bar) line into the next block. Theoretically, the post-pass should be aware of comments that intervene between the two lines given above, but in practice we can ignore such bizarre cases, because the file will still import correctly.
### A subtle detail about comparisons.

The python and coffeescript importers no longer override i.v2_gen_lines.

There were some tradeoffs involved, discussed in the lengthy checkin log.

The rest of this post discusses something subtle about the new code. It took me several hours to figure out what was going on. Happily, the resolution is simple, and will not likely cause problems in future.

**About comparisons**

Making the python importer work with the base `i.v2_gen_lines` was much harder than expected. After considerable work, I noticed a subtle difference the base `i.v2_gen_lines` and the python override, `py_i.v2_gen_lines`.

The override correctly tested the new state against the state at the top of the stack. The base `i.v2_gen_lines` dubiously tested the new state against the previous state. Changing `i.v2_gen_lines` so it too tests the new state against the top-of-stack state allowed everything to work.

I suspected that the change was valid because all unit tests passed. However, it would have been wrong to leave it at that. Imo, it is crucial that the change be proven correct.

Here is the code I am talking about, in `i.v2_gen_lines`:
```python
    for line in g.splitLines(s):
        new_state = self.v2_scan_line(line, prev_state)
        top = stack[-1]
        if self.is_ws_line(line):
            p = tail_p or top.p
            self.add_line(p, line)
        elif self.starts_block(line, new_state, prev_state):
            tail_p = None
            self.start_new_block(line, new_state, prev_state, stack)
        elif new_state.level() >= top.state.level():
            # Comparing new_state against prev_state does not work for python.
            p = tail_p or top.p
            self.add_line(p, line)
        else:
            tail_p = self.end_block(line, new_state, stack)
        prev_state = new_state
```
As the comment states, changing:
```python
    elif new_state.level() >= top.state.level():
```
to:
```python
    elif new_state.level() >= prev_state.level():
```
does not work for python, but it does work for importers for language that use braces, not indentation.

**What's going on?**

After a bit of noodling, the answer became clear. For languages that use braces, `prev_state.level()` is always the same as `top_state.level()`, because intervening lines that don't have brackets can't possibly change `prev_state.level()`. But for python, `state.level()` is `state.indent`, and `state.indent` depends on the vagaries of leading whitespace. So `top_state.level()` isn't guaranteed to be `prev_state.level()`.

Yes, it would be possible to define `Python_ScanState.update` so that it preserves `state.level()`, but that would add a serious, unnecessary constraint on update.

Summary

It's unlikely that the code discussed here will ever have to change. Still, it's important for future maintainers to understand something that caused me hours of confusion.

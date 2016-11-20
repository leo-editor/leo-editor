# For Devs: All About Importers

This documentation contains everything developers and maintainers need to
know about Leo's new importers. In particular, it tells how to write an
importer for a new language.

## Overview

This is the overview.
### Node 2 header

More
### Simplifying Leos importers is crucial so that future devs can add importers and fix existing importers.

This issue will continue previous engineering notebook posts. All are welcome to comment.

    Nov. 4: ENB: Leo's line-oriented importers: the last collapse in complexity

    Nov. 6: Important documentation for devs: Leo's new importers
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

    i.v2_gen_lines injects v._importer_lines list into the root vnode using `i.inject_lines_ivar'.

    Similarly, i.v2_create_child_node calls `i.inject_lines_ivar' into each created node.

    Replace p.b = p.b + s by p.v._importer_lines.append(s) self.add_line(p, s).

    i.v2_gen_lines calls self.finalize, which does the following:

    for p in parent.self_and_subtree():
        v = p.v
        assert not v._bodyString, repr(v._bodyString)
        v._bodyString = ''.join(v._import_lines)
        delattr(v, '_import_lines')

The assert was helpful initially.
### Importer API for setting body text

As of 6dbeb6a, all code in stages 1, 2 and 3 must use the following API to change body text. It is easier, faster than setting p.b to strings. And it stresses the GC much less.

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

Update: in practice, I prefer using p.v._import_lines explicitly rather than using the get_lines or set_lines methods. It's clearer, imo.
### i.is_ws_line

This is a one-line predicate that is crucial conceptually, and greatly clarifies the code in several places.

It returns True if the line is either blank or contains nothing but leading whitespace followed by a single-line comment. v2_gen_lines must put such lines in the existing block, regardless of their indentation.

Update: i.undent does not recognize the underindented line in the following (legal!, tested) python program:

if 1:
    def f():
        '''
        This
is a valid
        docstring.
        '''
        g.trace(f.__doc__)

f()

There is no way that i.is_ws_line can determine that is a valid is part of a docstring. There are two three possible approaches:

    Heavy handed: Use i.scan_line to keep track of state in i.undent. This implies overriding i.undent in importers.python.py to handle this special case.

    Simple, general: Inject v._import_indent into every generated node, including the root. i.undent will call i.undent_by(s, p.v._import_indent), which will undent all lines by exactly the given amount, regardless of the contents of the node. This should positively guarantee that all lines are indented properly, regardless of special cases. i.finish will remove all the temporary v._import_indent attributes.

    Best: Aha: Indentation mostly doesn't matter in python!! Python blocks begin if and only if a line begins with class or def outside of any context (string, docstring or comment). The easy way to do this is to override i.v2_gen_lines. It's a simple, beautiful solution. It will remove special case code from both i.v2_gen_lines and the new python_i.v2_gen_lines.

### Prefer s.isspace() to s.strip()

Until today, I have always tested for an empty string using not s.strip(). But Doh, this is an unnecessary stress on the GC. s.isspace() much faster and more pythonic.

Rev 2de4669 replaces (id).strip() with not id.isspace() everywhere in the Import class, removing not not in two or three places.

This regex makes the substitution safely:

  Find:   ([\w_\.]+)\.strip\(\)
  To:      not \1.isspace()

At one point I thought I had found a bug, but "correcting" it caused a unit test to fail. Indeed, i.post_pass moves whitespace from p to back. A new comment should avoid future confusion. All unit tests pass again.

It would be suicidal to attempt to make this changes in Leo's core--Leo's unit tests are not nearly good enough to catch blunders. However, this is an important change to make for the importers, and now is the time to make it while everything is in flux.

Update: As another aspect of this pattern, instead of testing:

   if not ''.join(lines).strip():

the new code now tests:

    if all([z.isspace() for z in lines]):

Update 2: As discussed on leo-editor, using s.isspace() works because s is never empty ('') for any line.
### The Importer class *is* a pipeline

@tfer Tom's importer proposal, was the first to suggest that the importers be organized as a pipeline. At first, I dismissed that suggestion, but in fact Tom's suggestions have been marinating in the back of my mind ever since. Thank you, Tom! Leo's great new importers owe a lot to you.

The new Importer class now clearly is a pipeline:

Update: i.run now calls i.generate_nodes, which explicitly calls three sub-passes:

Stage 1: i.v2_gen_linesgenerates, in a single, non-recursive pass, all the output nodes.

Stage 2: i.post_pass, which runs a series of other sub-stages. The default (base-class) code is:

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

Subclasses can override i.post_pass for complete control over post processing.

Stage 3: i.finish does "late" processing. In inserts Leo directives in the root nodes and, last of all, converts sets p.b to p.v._import_lines and then deletes the v._import_lines attribute. Subclasses should never have to override i.finish.

Furthermore, subclasses of the Importer class can easily modify code by overriding the following Importer methods:

i.clean_headline: This typically removed cruft from lines that define classes or defs. Py_Importer.clean_headline is one of the more complex overrides:

def clean_headline(self, s):
    '''Return a cleaned up headline s.'''
    m = re.match(r'\s*def\s+(\w+)', s)
    if m:
        return m.group(1)
    else:
        m = re.match(r'\s*class\s+(\w+)', s)
        if m: return 'class %s' % m.group(1)
        else: return s.strip()

Rich comparisons, i.starts_block, i.ends_block, i.initial_state and i.v2_scan_line:

These have been described in one of the two posts mentioned at the start of this issue.

Summary

The Importer class is organized as pipeline. Stage 1 creates the nodes. Stage 2 consists of several sub-stages, each of which adjust nodes in various ways. Stage 3 finishes up in a language independent way.

Subclasses of the Importer class may further customize the importers by override short methods.
### Almost all importers will work the same way

After the old importer classes are retired, almost all importers will be subclasses of the Importer class, except for the following:

    json.py, and .ipynb.py. In both cases, the incoming text is a json dict, so normal import code is out of the question.

    ctext.py. The importer is very simple. It doesn't need to be a subclass of Importer.
### Most scan_line methods are table-driven

The new coffeescript.scanner is an example of the nifty new pattern. Search for v2_scan_line and its helpers, in_table, out_table i.get_table, i.get_new_table and i.scan_table.

Update 11/20/2016: A lot has happened in the past week. Here is the revised i.v2_scan_line. It implicitly defines a protocol that all ScanState classes must follow:

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

The tables returned by in_table(context) and out_table() i.get_table describe the scanning much more clearly than the blah-blah-blah of code.

I feel like an absolute idiot for not using this easy pattern earlier. Furthermore, it would have saved me considerable work had I had proper unit tests for all scanners. This will happen next.
### Python *does* need to handle all kinds of brackets

I'm not sure that the present python code can be made to work without understanding the nesting levels of parens, curly-brackets and square-brackets. Consider this code from @test python comment after dict assign:

s = '''\
NS = { 'i': 'http://www.inkscape.org/namespaces/inkscape',
      's': 'http://www.w3.org/2000/svg',
      'xlink' : 'http://www.w3.org/1999/xlink'}

tabLevels = 4  # number of defined tablevels, FIXME, could derive from template?

This is valid code, no matter what kind of indentation is used in the dict.

I would rather not have the python scanner keep track of brackets. We shall see...

It's not a problem. i.scan_table now keeps of brackets for all languages.
### i.scan_table

Here is the latest (as of 11/15/2016). Note the hack for recognizing backslash. i.scan_table also adds a bs-nl flag to the returned 6-tuple. For sure, "bs-nl" can not be context!

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
### When context does, and doesn't matter

As discussed here, the client code that uses i.v2_scan_line can (usually) ignore context! This should simplify x.v2_gen_lines and the various ScanState classes. Indeed, ScanState classes will defined a state.level method that returns either an int or a tuple of ints. With this very easy infrastructure in place, comparisons such as:

if new_state.level() > prev_state.level():
    # enter new blockgs

with "just work", regardless of language. This will be surprisingly important in collapsing code (making it independent of language).

There are several special cases, however. Languages that use a regex pattern to determine whether a line starts a block must take care. x.starts_block must fail if prev_state.context is non-empty. In that case, the next line is in a comment or string. Here is a python example:

s = r'''
def spam():
    pass
'''

And similarly for coffeescript.

At present, the C-language importer only counts curly brackets, but this can lead to a strange assignment of lines to block in cases such as:

static void foo(bar)
{}

The block associated with foo will consist only of the line {}, with an unhelpful headline. The perfect import check will succeed, but the post-pass should move the int foo(bar) line into the next block. Theoretically, the post-pass should be aware of comments that intervene between the two lines given above, but in practice we can ignore such bizarre cases, because the file will still import correctly.
### A subtle detail about comparisons.

the python and coffeescript importers no longer override i.v2_gen_lines.

There were some tradeoffs involved, discussed in the lengthy checkin log.

The rest of this post discusses something subtle about the new code. It took me several hours to figure out what was going on. Happily, the resolution is simple, and will not likely cause problems in future.

About comparisons

Making the python importer work with the base i.v2_gen_lines was much harder than expected. After considerable work, I noticed a subtle difference the base i.v2_gen_lines and the python override, py_i.v2_gen_lines.

The override correctly tested the new state against the state at the top of the stack. The base i.v2_gen_lines dubiously tested the new state against the previous state. Changing i.v2_gen_lines so it too tests the new state against the top-of-stack state allowed everything to work.

I suspected that the change was valid because all unit tests passed. However, it would have been wrong to leave it at that. Imo, it is crucial that the change be proven correct.

Here is the code I am talking about, in i.v2_gen_lines:

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

As the comment states, changing:

elif new_state.level() >= top.state.level():

to:

elif new_state.level() >= prev_state.level():

does not work for python, but it does work for importers for language that use braces, not indentation.

What's going on?

After a bit of noodling, the answer became clear. For languages that use braces, prev_state.level() is always the same as top_state.level(), because intervening lines that don't have brackets can't possibly change prev_state.level(). But for python, state.level() is state.indent, and state.indent depends on the vagaries of leading whitespace. So top_state.level() isn't guaranteed to be prev_state.level().

Yes, it would be possible to define Python_ScanState.update so that it preserves state.level(), but there is no reason to do that. Worse, if it were done, it would be a serious, unnecessary constraint on update.

Summary

I have said several times now that the new importers are worth any amount of work. Understanding the only truly subtle aspect of i.v2_gen_lines is part of the required work.

It's unlikely that the code discussed here will ever have to change. Still, it's important for future maintainers to understand something that caused me hours of confusion yesterday.

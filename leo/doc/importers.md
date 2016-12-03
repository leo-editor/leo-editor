#The grand overview
This file documents Leo's importers.
You can view this file on-line [here](https://github.com/leo-editor/leo-editor/tree/master/leo/doc/importers.md). These docs focus on the big picture. For details, consult the code.

**The task**

Each importer allocates lines of input file to outline nodes, preserving the order of lines. The resulting outline structure should reflect the natural structure of the input file.

**Taxonomy of importers**

There are two sets of complications, almost mutually exclusive. These complications naturally partition the importers into two groups. A third group of importers are either very simple, or completely idiosyncratic.  Aside from a short discussion below, this documentation will say nothing about this third group.  Consult the source code.

**Complication 1: strings, comments & regex expressions**

Languages such a C, Javascript, HTML/XML, PHP and Python contain syntax constructs that must be handled correctly, because such constructs could contain text that *look* like they affect node structure, but don't.  For example, in python:

```python
    '''
    def spam():
        pass
    '''
```
    
In general, a character-by-character scan of the input file is required to recognize such syntax *accurately*. Happily, python dictionaries greatly speed such scanning.
    
**Complication 2: multi-line patterns**

Languages that *don't* have strings, comments, etc. typically *do* have structures whose syntax spans several lines.  Examples are ctext, markdown and reStructuredText. A [beautiful coding pattern](***) greatly simplifies these importers.

**Other importers**

Importers for the org-mode and otl (vim-outline) file formats are easiest of all. They have neither complex syntax nor multi-line patterns to contend with. Languages such as the ipynb (Jupyter Notebook) and json are driven by what are, in essence, nested python dictionaries.  The json importer is straightforward, the ipynb isn't. 
#The new importers vs the old
Leo's new importers are fundamentally simpler than the old.

The old importers attempted to parse their languages *character-by-character*. Only whole lines can be assigned to nodes, so the importers had to adjust the results of the parse to line boundaries. This was an extremely complex process, filled with error-prone index adjustments.

The new importers know *nothing* about parsing.  They only understand strings, comments, etc. In particular, the javascript importer knows nothing about javascript coding patterns or conventions.  It cares only about the net number of brackets and parentheses at the end of each line.

The old importers handled nested language constructs by recursively rescanning them.  The new importers handle each line of the input file exactly once, non-recursively, line by line.

The old importers kept strict track of indentation.  This presereved indentation, but required a complex code-generation infrastructure. The new importers handle indentation implicitly.  As a result, the new importers can *regularize* leading whitespace for most languages. Python requires that leading whitespace be preserved, but this too is done quite simply.
#The Importer class
All but the simplest importers are subclasses of the Importer class, in leo.plugins.importers.linescanner.py. The Importer class defines default methods that subclasses that subclasses are (usually) free to override.

**`i.run`** is the top-level driver code. It calls each stage of a **four-stage pipeline**. Few importers need to override it.

Stage 1, **`i.gen_lines`**, generates nodes. Most importers override `i.gen_lines`; a few use `i.gen_lines` as it is.

Stage 2, **`i.post_pass`**, is an optional post-pass. When present, x.post_pass reassigns lines to new nodes. Several importers defining a do-nothing x.post_pass. Other importers perform only part default i.post_pass processing.

Stage 3, **`i.finish`**, sets `p.b` in all generated nodes using the hidden `v._import_lines` machinery used in the line-oriented API. Manipulating `p.b` directly would be a huge performance bug. Importers should never have to override this final stage. 

Stage 4, **`i.check`**, performs perfect import checks. The rst and markdown importers disable this check by defining do-nothing overrides of i.check.

The following sections discuss i.gen_lines and the line-oriented API. This API simplifies the code and eliminates a huge performance bug.
##i.gen lines & helpers
**i.gen_lines** is the first stage of the pipeline. It allocates lines from the input file to outline nodes, creating those nodes as needed. Several importers override this method, or its helpers. These helpers are important, but they won't be discussed here. If you're interested, consult the source code.

**i.scan_line** is an optional helper for importers having strings, comments, etc. It calls i.scan_dict for every character of a line, returning a ScanState object describing the state at the *end* of the line just scanned. Few (no?) importers override i.scan_line. Instead, subclasses override **i.update**, as described [later](***).

**i.scan_dict** matches patterns against the character at position i of a line. Pattern matching is very fast because the code uses **scanning dictionaries**. Scanning dictionaries define the syntax of strings, comments, docstrings, etc.

**i.get_new_dict** returns the scanning dictionary for a particular combination of context and language. Some importers can use i.get_new_dict as it is because this method understands the format of strings and uses the language's comment delimiters.

Importers for langauges that have more complex syntax override i.get_new_dict. The PHP importer even overrides (hacks) i.scan_dict so that it can handle heredoc strings.

**i.get_dict** caches scanning dicts.  It returns a cached table if available, calling i.new_dict only if the dictionary for a language/context pair is not already in the cache. Subclasses should never need to override i.get_dict.

**Summary**

- i.gen_lines is the first stage of the pipline.  Most importers override it; a few use i.gen_lines as it is.

- Scanning dictionaries (x.get_new_dict) define the syntax of a language. Only importers that have strings, comments, etc. use (or override) i.scan_line or i.get_new_dict. In an emergency, importers can even override i.scan_dict.

- i.get_dict caches scanning dictionaries. Importers should never need to override it.


##The line-oriented API
The line-oriented API fixes a huge performance bug.

Concatenating strings to p.b directly creates larger and larger strings. As a result, it is an O(N**2) algorithm. In contrast, concatenating strings to a list is an O(N) algorithm.

Last night I attempted to concatenate lines to a new lines list in the Target class. But this proved unexpectedly tricky. Instantly, the simplicity of the code was compromised. Worse, it didn't work ;-)

- `i.gen_lines` injects `v._importer_lines` list into the root vnode using `i.inject_lines_ivar'.

- Similarly, `i.create_child_node` calls `i.inject_lines_ivar' into each created node.

- Replace `p.b = p.b + s` by `self.add_line(p, s)`.

- `i.gen_lines` calls `self.finalize`, which does the following:

```python
for p in parent.self_and_subtree():
    v = p.v
    assert not v._bodyString, repr(v._bodyString)
    v._bodyString = ''.join(v._import_lines)
    delattr(v, '_import_lines')
```

The assert was helpful initially.
#The ScanState classes
##state_update & the scan_line protocol

The new coffeescript.scanner is an example of the nifty new pattern. See `i.scan_line` and its helpers, `i.get_new_table` and `i.scan_table`.

Here is the revised `i.scan_line`. It implicitly defines a protocol that all ScanState classes must follow:
```python
def scan_line(self, s, prev_state):
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

##state.level()
ScanState classes all define a state.level() method that returns either an int or a tuple of ints. This allows comparisons such as the following for *all* languages:
```python
if new_state.level() > prev_state.level():
    # enter new block.
```

There are several special cases, however.

**Pattern matching** Languages that use a regex pattern to determine whether a line starts a block must take care. x.starts_block must fail if prev_state.context is non-empty. In that case, the next line is in a comment or string. Here is a python example:
```python
s = r'''
def spam():
    pass
'''
```

And similarly for coffeescript.

**Missing function signature lines** At present, the C-language importer only counts curly brackets, but this can lead to a strange assignment of lines to block in cases such as:
```c
static void foo(bar)
{}
```
The block associated with foo will consist only of the line {}, with an unhelpful headline. The perfect import check will succeed, but the post-pass should move the int foo(bar) line into the next block. Theoretically, the post-pass should be aware of comments that intervene between the two lines given above, but in practice we can ignore such bizarre cases, because the file will still import correctly.

#Notes
##The @button make-importer script
##Recognizing multi-line patterns
##Python must track brackets

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


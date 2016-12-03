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

The following sections discuss `i.gen_lines` and the line-oriented API. This API simplifies the code and eliminates a huge performance bug.
##i.gen lines & helpers
**`i.gen_lines`** is the first stage of the pipeline. It allocates lines from the input file to outline nodes, creating those nodes as needed. Several importers override this method, or its helpers. These helpers are important, but they won't be discussed here. If you're interested, consult the source code.

**`i.scan_line`** is an optional helper for importers having strings, comments, etc. It calls `i.scan_dict` for every character of a line, returning a `ScanState` object describing the state at the *end* of the line just scanned. Few (no?) importers override i.scan_line. Instead, subclasses override **`i.update`**, as described [later](***).

**`i.scan_dict`** matches patterns against the character at position `i` of a line. Pattern matching is very fast because the code uses **scanning dictionaries**. Scanning dictionaries define the syntax of strings, comments, docstrings, etc.

**`i.get_new_dict`** returns the scanning dictionary for a particular combination of context and language. Some importers can use i.get_new_dict as it is because this method understands the format of strings and uses the language's comment delimiters.

Importers for langauges that have more complex syntax override `i.get_new_dict`. The PHP importer even overrides (hacks) `i.scan_dict` so that it can handle heredoc strings.

**`i.get_dict`** caches scanning dicts.  It returns a cached table if available, calling `i.new_dict` only if the dictionary for a language/context pair is not already in the cache. Subclasses should never need to override `i.get_dict`.

**Summary**

- `i.gen_lines` is the first stage of the pipline.  Most importers override it. A few use `i.gen_lines` as it is.

- Scanning dictionaries (`x.get_new_dict`) define the syntax of a language. Only importers that have strings, comments, etc. use (or override) `i.scan_line` or `i.get_new_dict`. In an emergency, importers can even override `i.scan_dict`.

- `i.get_dict` caches scanning dictionaries. Importers should never need to override it.


##The line-oriented API
The line-oriented API fixes a huge performance bug. Concatenating strings to p.b directly creates larger and larger strings. As a result, it is an `O(N**2)` algorithm. In contrast, concatenating strings to a list is an `O(N)` algorithm.

In stage 1, **`i.create_child_node`** calls **`i.inject_lines_ivar(p)`** to init `p.v._import_lines`.

In stages 1 and 2,  **`i.add_line(p, s)`** and **`i.extend_lines(p, aList)`** append one or more lines to `p.v._import_lines`.

In stage 3, **`i.finalize`** sets `p.b = ''.join(p.v._import_lines)` for all created nodes and then deletes all `v._import_lines` attributes.
#The ScanState classes
ScanState classes are needed only for importers for languages containing strings, comments, etc. When present, the ScanState class consists of a manditory **`context`** ivar, and optional ivars counting indentation level and bracket levels.

It's clearer to define a custom ScanState level for each importer. Subclassing the base ScanState class in linescanner.py would be more confusing and more clumsy.

ScanState classes are short and simple. The following sections define the interface between the ScanState classes and the Importer classes.
##ScanState.context
The ScanState.context ivar is `''` (An empty string) when the present scanning index ``i`` is outside any string, comment, etc. Otherwise, the context ivar is a copy of the string that starts the string, comment, etc. We say that the importer is **in a context** when the scanner is inside a string, comment or regex.

Context can generally be ignored for languages that only count brackets.  Examples are C and Javascript.  In that case, the counts at the *end* of the line are accurate, *regardless* of whether the line ends in a context. In contrast, importers that use patterns to discover block structure must take care that the pattern matches fail when the *previous* line ends in a context.  It's just that simple.
##ScanState.level()
Unless an importer completely overrides `i.gen_lines`, each ScanState classes must define a state.level() method. The level method must return either an int or a tuple of ints. This allows *all* importers to make the following comparison:

```python
if new_state.level() > prev_state.level():
    # enter new block.
```

Most states will use one or more bracket counts to define levels.  Others, like python, will use indentation counts. Some states always return 0.
##ScanState protocols
The following protocols are needed only when the importer uses the base i.scan_line method. In that case...

1. The ScanState class must have a ctor with the following signature:

```python
    def __init__(self, d):
```

When d is None, the ctor should init all ivars. Otherwise, d is a dict that tells how to init all ivars.

2. The state class must have an update method:

```python
    def update(self, data):
```

where data is the 6-tuple returned from `i.scan_line`, namely:

```python
    new_context, i, delta_c, delta_p, delta_s, bs_nl
```

new_context is a context (a string), i is the scan index, the delta items are changes to the counts of curly brackets, parens and square brackets, and bs_nl is True if the lines ends in a backslash/newline.

The ScanState.update method simply sets all appropriate ivars in the ScanState, ignoring items of the 6-tuple that don't correspond to ScanState ivars.
#The @button make-importer script
#Notes
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


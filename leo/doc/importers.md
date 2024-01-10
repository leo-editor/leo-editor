# Table of contents
1. [The grand overview](importers.md#the-grand-overview)
2. [The new importers vs. the old](importers.md#the-new-importers-vs-the-old)
3. [The Importer class](importers.md#the-importer-class)
    1. [i.gen lines & helpers](importers.md#igen-lines--helpers)
    2. [The line-oriented API](importers.md#the-line-oriented-api)
    3. [Indentation](importers.md#indentation)
4. [The ScanState classes](importers.md#the-scanstate-classes)
    1. [ScanState.context](importers.md#scanstatecontext)
    2. [ScanState.level()](importers.md#scanstatelevel)
    3. [ScanState protocols](importers.md#scanstate-protocols)
5. [Using @button make-importer](importers.md#using-button-make-importer)
6. [Notes](importers.md#notes)
    1. [Recognizing multi-line patterns](importers.md#recognizing-multi-line-patterns)
    2. [The python importer must count brackets](importers.md#the-python-importer-must-count-brackets)
    3. [Scanning strings and comments](importers.md#scanning-strings-and-comments)
7. [Conclusion](importers.md#conclusion)

# The grand overview
This file documents Leo's importers.
You can view this file on-line [here](https://github.com/leo-editor/leo-editor/tree/master/leo/doc/importers.md). These docs are intended solely to help you read the code. For details, consult the code.

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

Languages that *don't* have strings, comments, etc. typically *do* have structures whose syntax spans several lines.  Examples are ctext, markdown and reStructuredText. A [beautiful coding pattern](importers.md#recognizing-multi-line-patterns) greatly simplifies these importers.

**Other importers**

Importers for the org-mode and otl (vim-outline) file formats are easiest of all. They have neither complex syntax nor multi-line patterns to contend with. Languages such as the ipynb (Jupyter Notebook) and json are driven by what are, in essence, nested python dictionaries.  The json importer is straightforward, the ipynb isn't.

# The new importers vs. the old
Leo's new importers are fundamentally simpler than the old.

The old importers attempted to parse their languages *character-by-character*. Only whole lines can be assigned to nodes, so the importers had to adjust the results of the parse to line boundaries. This was an extremely complex process, filled with error-prone index adjustments.

The new importers usually know *nothing* about parsing.  They only understand strings, comments, etc. In particular, the javascript importer knows nothing about javascript coding patterns or conventions.  It cares only about the net number of brackets and parentheses at the end of each line. The python and java importers *do* attempt to parse class and function lines using regular expressions.

The old importers handled nested language constructs by recursively rescanning them.  The new importers handle each line of the input file exactly once, non-recursively, line by line.

The old importers kept strict track of indentation.  This preserved indentation, but required a complex code-generation infrastructure. The new importers handle indentation implicitly.  As a result, the new importers can *regularize* leading whitespace for most languages. Python requires that leading whitespace be preserved, but this too is done quite simply.

# The Importer class
All but the simplest importers are subclasses of the Importer class, in leo/plugins/importers/linescanner.py. The Importer class defines default methods that subclasses that subclasses are (usually) free to override.

**`i.run`** is the top-level driver code. It calls each stage of a **five-stage pipeline**. Few importers will need to override `i.run`.

Stage 0, **`i.check_blanks_and_tabs`**, checks to see that leading whitespace appears consistently in all input lines, and are consistent with `@tabwidth`. If not, certain kinds of perfect-import checks must be disabled in stage 4...

Stage 1, **`i.gen_lines`**, is the heart of the code. It generates nodes whose outline structure reflects the meaning of the sources. Some importers override `i.gen_lines`. Others use `i.gen_lines` as it is.

Stage 2, **`i.post_pass`**, is an optional post-pass. When present, x.post_pass reassigns lines to new nodes. Several importers defining a do-nothing x.post_pass. Other importers perform only part default `i.post_pass` processing.

Stage 3, **`i.finish`**, sets `p.b` in all generated nodes using the hidden `v._import_lines` machinery used in the line-oriented API. Manipulating `p.b` directly would be a huge performance bug. Importers should never have to override this stage. 

Stage 4, **`i.check`**, performs perfect import checks. The rst and markdown importers disable this check by defining do-nothing overrides of `i.check`.

The following sections discuss `i.gen_lines`, the line-oriented API, and how importers indent lines properly.

## i.gen lines & helpers
**`i.gen_lines`** is the first stage of the pipeline. It allocates lines from the input file to outline nodes, creating those nodes as needed. Several importers override this method, or its helpers. These helpers are important, but they won't be discussed here. If you're interested, consult the source code.

**`i.scan_line`** is an optional helper for importers having strings, comments, etc. It calls `i.scan_dict` for every character of a line, returning a `ScanState` object describing the state at the *end* of the line just scanned. Few importers override `i.scan_line`. Instead, subclasses override **`i.update`**, as described [later](importers.md#scanstate-protocols).

**`i.scan_dict`** matches patterns against the character at position `i` of a line. Pattern matching is very fast because the code uses **scanning dictionaries**. Scanning dictionaries define the syntax of strings, comments, docstrings, etc.

**`i.get_new_dict`** returns the scanning dictionary for a particular combination of context and language. Some importers can use `i.get_new_dict` as it is because this method understands the format of strings and uses the language's comment delimiters.

Importers for languages that have more complex syntax override `i.get_new_dict`. The PHP importer even overrides (hacks) `i.scan_dict` so that it can handle heredoc strings.

**`i.get_dict`** caches scanning dicts.  It returns a cached table if available, calling `i.new_dict` only if the dictionary for a language/context pair is not already in the cache. Subclasses should never need to override `i.get_dict`.

## The line-oriented API
The line-oriented API fixes a huge performance bug. Concatenating strings to p.b directly created larger and larger strings. As a result, it was an `O(N**2)` algorithm. In contrast, concatenating strings to a list is an `O(N)` algorithm.

In stage 1, **`i.create_child_node`** calls **`i.inject_lines_ivar(p)`** to inject the `p.v._import_lines` attribute into the vnode.

In stages 1 and 2, high-level methods such as **`i.add_line(p, s)`** and **`i.extend_lines(p, aList)`** append one or more lines to `p.v._import_lines`.

In stage 3, **`i.finalize`** sets `p.b = ''.join(p.v._import_lines)` for all created nodes and then deletes all `v._import_lines` attributes.

## Indentation
**Strict** languages are languages like python for which leading whitespace (lws) is particularly important.

Stage 1 never changes lws. However, stage 1 *can* create indented `@others` and section references. When Leo eventually writes the file, such lws will affect the indentation of the output file.

Only stage 2 removes lws. **`i.undent`** does this, using the following trick. In a round-about way (too complex and uninteresting to describe here), **`i.common_lws`** *ignores* blank lines and comments. So `i.undent` can remove maximum lws from all lines. By definition, *there won't be enough lws for underindented comments*, so `i.undent` prepends Leo's underindented escape string to such lines.

**Important**: importers maintain no global indentation counts, even for python.  This works because `i.run` verifies that the lws in the python file is consistent with the present `@tabwidth`. As a result, the lws before `@others` and section references *will turn out to be correct*.  It's clever, and not so obvious.

**Important**: The net effect of the code is to *regularize* indentation for non-strict languages. Source files for languages like xml, html and javascript can have *randomly indented* lines. There is no way to preserve random indentation in a Leonine way, and no *reason* to do so. Converting source code to a typical Leo outline improves the code markedly.

# The ScanState classes
ScanState classes are needed only for importers for languages containing strings, comments, etc. When present, the ScanState class consists of a mandatory **`context`** ivar, and optional ivars counting indentation level and bracket levels.

It's clearer to define a custom ScanState level for each importer. Subclassing the base ScanState class in linescanner.py would be more confusing and more clumsy.

ScanState classes are short and simple. The following sections define the interface between the ScanState classes and the Importer classes.

## ScanState.context
The ScanState.context ivar is `''` (an empty string) when the present scanning index ``i`` is outside any string, comment, etc. Otherwise, the context ivar is a copy of the string that starts the string, comment, etc. We say that the importer is **in a context** when the scanner is inside a string, comment or regex.

Context can generally be ignored for languages that only count brackets.  Examples are C and Javascript.  In that case, the counts at the *end* of the line are accurate, *regardless* of whether the line ends in a context! In contrast, importers that use patterns to discover block structure must take care that the pattern matches fail when the *previous* line ends in a context.  It's just that simple.

## ScanState.level()
Unless an importer completely overrides `i.gen_lines`, each `ScanState` class must define a state.level() method. The `level` method must return either an int or a tuple of ints. This allows *all* importers to make the following comparison:

```python
if new_state.level() > prev_state.level():
    # enter new block.
```

Most states will use one or more bracket counts to define levels.  Others, like python, will use indentation counts. Some states always return 0.

## ScanState protocols
The following protocols are needed only when the importer uses the base `i.scan_line` method. In that case...

1. The ScanState class should have a ctor with the following signature:

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

`new_context` is a context (a string), `i` is the scan index, the `delta` items are changes to the counts of curly brackets, parens and square brackets, and `bs_nl` is `True` if the lines ends in a backslash/newline.

The `ScanState.update` method should set all appropriate ivars in the ScanState, ignoring items of the 6-tuple that don't correspond to ScanState ivars.

# Using @button make-importer
This script appears in scripts.leo. To use this script, simply change the constants (strings) in the root `@button` node and run the script.

The script creates an `@@file` node for the new importer. When you are ready, change `@@file` to `@file`. The file contains an `X_Importer` class (a subclass of the base `Importer` class) and a stand-alone `X_ScanState` class. Search for `###` for places that you may want to customize.

Not all importers need a `ScanState` class.  In that case, just delete the `ScanState` class and set `state_class = None` when initing the base Importer class in `X_Importer`.

# Notes

## Recognizing multi-line patterns
`i.gen_lines` now supports skip counts, using the `skip` ivar. Skip counts allow pattern matching to be done naturally.

The new coding pattern encourages *multi-line* pattern matching.  This can drastically simplify code. `i.gen_lines` remains straightforward:

```python
    lines = g.splitLines(s)
    self.skip = 0
    for i, line in enumerate(lines):
        new_state = self.scan_line(line, prev_state)
        top = stack[-1]
        if trace: self.trace_status(line, new_state, prev_state, stack, top)
        if self.skip > 0:
            self.skip -= 1
        elif self.is_ws_line(line):
            p = tail_p or top.p
            self.add_line(p, line)
        elif self.starts_block(i, lines, new_state, prev_state):
            tail_p = None
            self.start_new_block(i, lines, new_state, prev_state, stack)
        elif self.ends_block(line, new_state, prev_state, stack):
            tail_p = self.end_block(line, new_state, stack)
        else:
            p = tail_p or top.p
            self.add_line(p, line)
        prev_state = new_state
```

## The python importer must count brackets
The Python importer must count parens, curly-brackets and square-brackets. Keeping track of indentation is not enough, because of code such as this:

```python
s = '''\
NS = { 'i': 'http://www.inkscape.org/namespaces/inkscape',
        's': 'http://www.w3.org/2000/svg',
    'xlink' : 'http://www.w3.org/1999/xlink'}

tabLevels = 4
```

This is valid code, no matter what kind of indentation is used in the dict. As a result, `i.scan_dict` now keeps track of brackets for all languages.

## Scanning strings and comments
Is there some way to scan comments and strings quickly while using the line-oriented scanning code? Using a dedicated "quick string-scanning mode" might speed up the scan compared to calling i.scan_dict for every character.

In fact, a dedicated scanner would hardly speed up the scan at all, because `i.scan_dict` is very fast. Worse, such a scheme would complicate `x.gen_lines`. Indeed, if `i.scan_dict` scanned the comment or string completely, it might return an index `i` that is *past* the line that `x.gen_lines` is handling.  Somehow, `x.gen_lines` would have to re-sync to the next complete line. That would be complex and slow.

**Aha**: `i.scan_dict` doesn't need to scan strings and comments completely! It could just scan to the end of the present line, or the end of the string or comment, whichever comes first. This is a superb answer to the original question. It speeds up strings and comments almost as much as possible, while keeping `i` on the present line.

But to repeat, there is not much reason actually to have `i.scan_table` go into "quick scan mode". Scanning is already fast enough.

# Conclusion
This documentation is merely a starting point for studying the code. This documentation is concise for a reason: too many details obscure the big picture.

Once you have a *general* notion of what the code does, and how it does it, you should definitely study the code itself to gain deeper understanding. Use the code to guide your memory, not this documentation! When studying code for the first time, focus on seeing the shape of the outline. What files have many classes? What classes are complex?

If you have questions about the code, please feel free to ask questions.  But do explore the code first. It's usually straightforward.

.. rst3: filename: html/appendices.html

##########
Appendices
##########

.. |br| raw:: html

   <br />
   
.. contents:: Contents
    :depth: 3
    :local:

Format of .leo files
++++++++++++++++++++

.. _`Writing plugins`:   writingPlugins.html

Here are the XML elements that may appear in Leo files:

<?xml>
    Leo files start with the following line::

        <?xml version="1.0" encoding="UTF-8"?>

<?xml-stylesheet>
    An xml-stylesheet line is option.  For example::

        <?xml-stylesheet ekr_stylesheet?>

<leo_file>
    The <leo_file> element opens an element that contains the entire file.
    </leo_file> ends the file.

<leo_header> 
    The <leo_header> element specifies version information and other information
    that affects how Leo parses the file.  For example::

        <leo_header file_format="2" tnodes="0" max_tnode_index="5725" clone_windows="0"/>

    The file_format attribute gives the 'major' format number.
    It is '2' for all 4.x versions of Leo.
    The tnodes and clone_windows attributes are no longer used.
    The max_tnode_index	attribute is the largest tnode index.

<globals>
    The globals element specifies information relating to the entire file.
    For example::

        <globals body_outline_ratio="0.50">
            <global_window_position top="27" left="27" height="472" width="571"/>
            <global_log_window_position top="183" left="446" height="397" width="534"/>
        </globals>

    -   The body_outline_ratio attribute specifies the ratio of the height of the body pane to
        the total height of the Leo window.
        It initializes the position of the splitter separating the outline pane from the body pane.

    -   The global_window_position and global_log_window_position elements
        specify the position of the Leo window and Log window in global coordinates:

<preferences>
    This element is vestigial.
    Leo ignores the <preferences> element when reading.
    Leo writes an empty <preferences> element.

<find_panel_settings>
    This element is vestigial.
    Leo ignores the <find_panel_settings> element when reading.
    Leo writes an empty <find_panel_settings> element.

<clone_windows>
    This element is vestigial.
    Leo ignores the <clone_windows> element when reading.
    Leo no longer writes <clone_windows> elements.

<vnodes>
    A single <vnodes> element contains nested <v> elements.
    <v> elements correspond to vnodes.
    The nesting of <v> elements indicates outline structure in the obvious way.

<v>
    The <v> element represents a single vnode and has the following form::

        <v...><vh>sss</vh> (zero or more nested v elements) </v>

    The <vh> element specifies the headline text.
    sss is the headline text encoded with the usual XML escapes.
    As shown above, a <v> element may contain nested <v> elements.
    This nesting indicates outline structure in the obvious way.
    Zero or more of the following attributes may appear in <v> elements::

        t=name.timestamp.n
        a="xxx"

    The t="Tnnn" attribute specifies the <t> element associated with a <v> element.
    The a="xxx" attribute specifies vnode attributes.
    The xxx denotes one or more upper-case letters whose meanings are as follows::

        C	The vnode is a clone. (Not used in 4.x)
        E	The vnode is expanded so its children are visible.
        M	The vnode is marked.
        T	The vnode is the top visible node.
        V	The vnode is the current vnode.

    For example, a="EM"  specifies that the vnode is expanded and is marked.

    **New in 4.0**:

    -   <v> elements corresponding to @file nodes now contain tnodeList attributes.
        The tnodeList attribute allows Leo to recreate the order in which nodes should 
        appear in the outline.
        The tnodeList attribute is a list of gnx's: global node indices.
        See Format of external files (4.x) for the format of gnx's.

    -   Plugins and scripts may add attributes to <v> and <t> elements.
        See `Writing plugins`_ for details.

<tnodes>
    A single <tnodes> element contains a non-nested list of <t> elements.

<t>
    The <t> element represents the body text of the corresponding <v> element.
    It has this form::

        <t tx="<gnx>">sss</t>

    The tx attribute is required.
    The t attribute of <v> elements refer to this tx attribute.
    sss is the body text encoded with the usual XML escapes.

    **New in 4.0**: Plugins and scripts may add attributes to <v> and <t>
    elements. See `Writing plugins`_ for details.

Format of external files
++++++++++++++++++++++++

.. _`sentinel lines`: glossary.html#sentinel-lines

This section describe the format of external files. Leo's `sentinel lines`_ are comments, and this section describes those comments.

.. index:: gnx

External files created by @file use gnx's in @+node sentinels. Such gnx's permanently and uniquely identify nodes. Gnx's have the form::

    id.yyyymmddhhmmss
    id.yyyymmddhhmmss.n

The second form is used if two gnx's would otherwise be identical.

- id is a string unique to a developer, e.g., a git id.

- yyyymmddhhmmss is the node's creation date.

- n is an integer.

Closing sentinels are required for section references and the @all and @others directives, collectively known as **embedding constructs.** Proof: These constructs do not terminate the node in which they appear. Without a closing sentinel there would be no way to know where the construct ended and the following lines of the enclosing node began.

New sentinels do not include @nonl or @nl. As a result, body text always ends with at least one newline.

Here are the sentinels used by Leo, in alphabetical order. Unless otherwise noted, the documentation applies to all versions of Leo. In the following discussion, gnx denotes a gnx as described above.

\@<<
    A sentinel of the form @<<section_name>> represents a section reference.

    If the reference does not end the line, the sentinel line ending
    the expansion is followed by the remainder of the reference line.
    This allows the Read code to recreate the reference line exactly.

\@@
    The @@ sentinel represents any line starting with @ in body text
    except @*whitespace*, @doc and @others.
    Examples::

      @@nocolor
      @@pagewidth 80
      @@tabwidth 4
      @@code

\@afterref
    Marks non-whitespace text appearing after a section references.

\@+all
    Marks the start of text generated by the @all directive.

\@-all
    Marks the end of text generated by the @all directive.

\@at and @doc

    The @+doc @+at sentinels indicate the start of a doc parts.

    We use the following **trailing whitespace convention** to
    determine where putDocPart has inserted line breaks::

        A line in a doc part is followed by an inserted newline
        if and only if the newline if preceded by whitespace.

    To make this convention work, Leo's write code deletes the trailing
    whitespace of all lines that are followed by a "real" newline.

\@+body **(Leo 3.x only)**
    Marks the start of body text.

\@-body **(Leo 3.x only)**
    Marks the end of body text.

\@delims
    The @delims directive inserts @@delims sentinels into the
    external file. The new delimiter strings continue in effect until
    the next @@delims sentinel *in the external file* or until the
    end of the external file. Adding, deleting or changing @@delim
    *sentinels* will destroy Leo's ability to read the external file.
    Mistakes in using the @delims *directives* have no effect on Leo,
    though such mistakes will thoroughly mess up a external file as
    far as compilers, HTML renderers, etc. are concerned.

\@+leo
    Marks the start of any external file. This sentinel has the form::

        <opening_delim>@leo<closing_delim>

    The read code uses single-line comments if <closing_delim> is empty.
    The write code generates single-line comments if possible.

    The @+leo sentinel contains other information. For example::

        <opening_delim>@leo-ver=4-thin<closing_delim>

\@-leo
    Marks the end of the Leo file.
    Nothing but whitespace should follow this directive.

\@+middle **(Created in Leo 4.0, removed in Leo 5.3)**

\@-middle **(Created in Leo 4.0, removed in Leo 5.3)**
    Marks the start/end of intermediate nodes between the node that
    references a section and the node that defines the section.
    
    These sentinels were a **mistake** that created bugs.  See:
    https://github.com/leo-editor/leo-editor/issues/132
    
\@nl **(Leo 3.x only)**
    Insert a newline in the outline.

\@+node
    Mark the start and end of a node::

        @+node:gnx:<headline>
        
\@nonl **(Leo 3.x only)**
    Suppresses a newline in the outline.

\@others
    The @+others sentinel indicates the start of the expansion of an @+others          
    directive, which continues until the matching @-others sentinel.

\@verbatim
    @verbatim indicates that the next line of the external file is not a sentinel.
    This escape convention allows body text to contain lines that would otherwise
    be considered sentinel lines.

\@@verbatimAfterRef
    @verbatimAfterRef is generated when a comment following a section reference would
    otherwise be treated as a sentinel. In Python code, an example would be::

      << ref >> #+others

Unicode reference
+++++++++++++++++

Leo uses unicode internally for all strings.

1. Leo converts headline and body text to unicode when reading .leo files and external files. Both .leo files and external files may specify their encoding.  The default is utf-8. If the encoding used in a external file is not "utf-8" it is represented in the @+leo sentinel line. For example::

        #@+leo-encoding=iso-8859-1.

    The utf-8 encoding is a "lossless" encoding (it can represent all
    unicode code points), so converting to and from utf-8 plain
    strings will never cause a problem. When reading or writing a
    character not in a "lossy" encoding, Leo converts such characters
    to '?' and issues a warning.

2. When writing .leo files and external files Leo uses the same encoding used to read the file, again with utf-8 used as a default.

3. leoSettings.leo contains the following Unicode settings, with the defaults as shown::

        default_derived_file_encoding = UTF-8 
        new_leo_file_encoding = UTF-8 

    These control the default encodings used when writing external
    files and .leo files. Changing the new_leo_file_encoding setting
    is not recommended. See the comments in leoSettings.leo. You may
    set default_derived_file_encoding to anything that makes sense for
    you.

4. The @encoding directive specifies the encoding used in a external file. You can't mix encodings in a single external file.

Valid URL's
+++++++++++

Leo checks that the URL is valid before attempting to open it. A valid URL is:

-   3 or more lowercase alphas
-   followed by one :
-   followed by one or more of:
-   ``$%&'()*+,-./0-9:=?@A-Z_a-z{}~``
-   followed by one of: ``$%&'()*+/0-9:=?@A-Z_a-z}~`` 

That is, a comma, hyphen and open curly brace may not be the last character.

URL's in Leo should contain no spaces: use %20 to indicate spaces.

You may use any type of URL that your browser supports: http, mailto, ftp, file, etc.

The Mulder/Ream update algorithm
++++++++++++++++++++++++++++++++

This appendix documents the Mulder/Ream update algorithm in detail, with an informal proof of its correctness.

Prior to Leo 5.1, Leo used Bernhard Mulder's original algorithm to read @shadow files. Starting with Leo 5.1, Leo uses this algorithm to read both @clean and @shadow files. Conceptually, both algorithms work as described in the next section.

In February 2015 EKR realized that the @shadow algorithm could be used to update @clean (@nosent) files. Simplifying the algorithm instantly became a top priority. The new code emerged several days later, made possible by the x.sentinels array. It is an important milestone in Leo's history.

What the algorithm does
***********************

For simplicity, this discussion will assume that we are updating an
external file, x, created with @clean x. The update algorithm works
exactly the same way with @shadow trees.

The algorithm works with *any* kind of text file. The algorithm uses only
difflib. It knows nothing about the text or its meaning. No parsing is ever
done.

Suppose file x has been changed outside of Leo. When Leo reads x it does
the following:

1. Recreates the *old* version of x *without* sentinels by writing the
   @clean x *outline* into a string, as if it were writing the @clean x
   outline again.
   
2. Recreates all the lines of x *with* sentinels by writing the @clean x
   *outline* into a string, as if it was writing an @file node! Let's call
   these lines the **old sentinels** lines.
   
3. Uses difflib.SequenceMatcher to create a set of diffs between the
   old and new versions of x *without* sentinels.
   
   **Terminology**: the diffs tell how to change file a into file b. The
   actual code uses this terminology: **a** is set of lines in the old
   version of x, **b** is the set of lines in the new version of x.
   
4. Creates a set of lines, the **new sentinels lines** using the old
   sentinels lines, the a and b lines and the diffs.
   
   This is the magic. Bernhard Mulder's genius was conceiving that a
   three-way merge of lines could produce the new outline, *with*
   sentinels. The code is in x.propagate_changed_lines and its helpers.
   
5. Replaces the @clean tree with the new tree created by reading the new
   sentinels lines with the @file read logic.

**Important**: The update algorithm never changes sentinels. It never
inserts or deletes nodes. The user is responsible for creating nodes to
hold new lines, or for deleting nodes that become empty as the result of
deleting lines.

Guesses don't matter
********************

There are several boundary cases that the update algorithm can not resolve.
For example, if a line is inserted between nodes, the algorithm can not
determine whether the line should be inserted at the end of one node or the
start of the next node. Let us call such lines **ambiguous lines**.

The algorithm *guesses* that ambiguous lines belongs at the end of a node
rather than at the start of the next node. This is usually what is
wanted--we usually insert lines at the end of a node.

Happily, **guesses don't matter**, for the following reasons:

1. The external file that results from writing the @clean x tree will be
   the same as the updated external file *no matter where* ambiguous lines
   are placed. In other words, the update algorithm is **sound**.

2. Leo reports nodes that were changed when reading any external file. The
   user can review changes to @clean and @file trees in the same way.

3. The user can permanently correct any mistaken guess. Guesses only happen
   for *newly inserted or changed* lines. Moving an ambiguous line to the
   following node will not change the external file. As a result, the
   next time Leo reads the file the line will be placed in the correct node!

This proves that @shadow and @clean are easy and safe to use. The
remaining sections of this document discuss code-level details.

Background of the code
**********************

The algorithm depends on three simple, guaranteed, properties of
SequenceMatcher.opcodes. See
https://docs.python.org/2/library/difflib.html#sequencematcher-examples

**Fact 1**: The opcodes tell how to turn x.a (a list of lines) into x.b
(another list of lines).

The code uses the a and b terminology. It's concise and easy to remember.

**Fact 2**: The opcode indices ai, aj, bi, bj *never* change because
neither x.a nor x.b changes.

Plain lines of the result can be built up by copying lines from x.b to x.results::

    'replace'   x.results.extend(x.b[b1:b2])
    'delete'    do nothing  (b1 == b2)
    'insert'    x.results.extend(x.b[b1:b2])
    'equal'     x.results.extend(x.b[b1:b2])

**Fact 3**: The opcodes *cover* both x.a and x.b, in order, without any gaps.

This is an explicit requirement of sm.get_opcode:

- The first tuple has ai==aj==bi==bj==0.

- Remaining tuples have ai == (aj from the preceding tuple) and bi == (bj
  from the previous tuple).
  
Keep in mind this crucial picture:

- The slices x.a[ai:aj] cover the x.a array, in order without gaps.
- The slices x.b[bi:bj] cover the x.b array, in order without gaps.

Aha: the x.sentinels array
**************************

Mulder's original algorithm was hard to understand or to change. The
culprit was the x.mapping array, which mapped indices into arrays of lines
*with* sentinels to indices into arrays of lines *without* sentinels.

The new algorithm replaces the x.mapping array with the x.sentinels array.
As a result, diff indices never need to be adjusted and handling diff
opcodes is easy.

For any index i, x.sentinels[i] is the (possibly empty) list of sentinel
lines that precede line a[i]. Computing x.sentinels from old_private_lines
is easy. Crucially, x.a and x.sentinels are *parallel arrays*. That is,
len(x.a) == len(x.sentinels), so indices into x.a are *also* indices into
x.sentinels.

Strategy & proof of correctness
*******************************

Given the x.sentinels array, the strategy for creating the results is
simple. Given indices ai, aj, bi, bj from an opcode, the algorithm:

- Writes sentinels from x.sentinels[i], for i in range(ai,aj).

- Writes plain lines from b[i], for i in range(bi,bj).

This "just works" because the indices cover both a and b.

- The algorithm writes sentinels exactly once (in order) because each
  sentinel appears in x.sentinels[i] for some i in range(len(x.a)).

- The algorithm writes plain lines exactly once (in order) because
  each plain line appears in x.b[i] for some i in range(len(x.b)).

This completes an informal proof of the correctness of the algorithm.

The leading and trailing sentinels lines are easy special cases. This
code, appearing before the main loop, ensures that leading lines are
written first, and only once::

    x.put_sentinels(0)
    x.sentinels[0] = []

Similarly, this line, at the end of the main loop, writes trailing
sentinels::

    x.results.extend(x.trailing_sentinels)

Summary
*******

The algorithm creates an updated set of lines *with* sentinels using the
@clean outline and the updated external file. These new lines then replace
the original @clean with a new @clean tree. The algorithm uses only
difflib. It will work with *any* kind of text file. No knowledge of any
language is needed.

The algorithm depends on simple, guaranteed, properties of indices in
SequenceMatcher opcodes.

The algorithm steps through x.sentinels and x.b, extending x.results
as it goes.

The algorithm gets all needed data directly from opcode indices into
x.sentinels and x.b. Using opcode indices requires neither reader
classes nor auxiliary indices.

The algorithm is simple enough to be understood at first reading. I'll
remember its details for the rest of my life.

Why I like Python
+++++++++++++++++

I wrote this soon after discovering Python in 2001. The conclusions are still valid today.
    
I've known for a while that Python was interesting; I attended a Python conference last year and added Python support to Leo. But last week I got that Python is something truly remarkable. I wanted to convert Leo from wxWindows to wxPython, so I began work on c2py, a Python script that would help convert from C++ syntax to Python. While doing so, I had an Aha experience. Python is more than an incremental improvement over Smalltalk or C++ or objective-C; it is "something completely different". The rest of this post tries to explain this difference.

Clarity
*******

What struck me first as I converted C++ code to Python is how much less blah, blah, blah there is in Python. No braces, no stupid semicolons and most importantly, *no declarations*. No more pointless distinctions between const, char \*, char const \*, char \* and wxString. No more wondering whether a variable should be signed, unsigned, short or long.

Declarations add clutter, declarations are never obviously right and declarations don't prevent memory allocation tragedies. Declarations also hinder prototyping. In C++, if I change the type of something I must change all related declarations; this can be a huge and dangerous task. With Python, I can change the type of an object without changing the code at all! It's no accident that Leo's new log pane was created first in Python.

Functions returning tuples are a "minor" feature with a huge impact on code clarity. No more passing pointers to data, no more defining (and allocating and deallocating) temporary structs to hold multiple values.

.. _`pylint`: http://www.logilab.org/857

Python can't check declarations because there aren't any. However, there is a really nifty tool called `pylint`_ that does many of the checks typically done by compilers.

Power
*****

Python is much more powerful than C++, not because Python has more features, but because Python needs *less* features. Some examples:

- Python does everything that the C++ Standard Template Library (STL) does, without any of the blah, blah, blah needed by STL. No fuss, no muss, no code bloat.

- Python's slicing mechanism is very powerful and applies to any sequence (string, list or tuple). Python's string library does more with far less functions because slices replace many functions typically found in other string libraries.

- Writing dict = {} creates a dictionary (hash table). Hash tables can contain anything, including lists and other hash tables.

- Python's special functions,  __init__, __del__, __repr__, __cmp__, etc. are an elegant way to handle any special need that might arise.

Safety
******

Before using Python I never fully realized how difficult and dangerous memory allocation is in C++. Try doing::

        aList[i:j] = list(aString)

in C.  You will write about 20 lines of C code. Any error in this code will create a memory allocation crash or leak.

Python is fundamentally safe. C++ is fundamentally unsafe. When I am using Python I am free from worry and anxiety. When I am using C++ I must be constantly "on guard." A momentary lapse can create a hard-to-find pointer bug. With Python, almost nothing serious can ever go wrong, so I can work late at night, or after a beer. The Python debugger is always available. If an exception occurs, the debugger/interpreter tells me just what went wrong. I don't have to plan a debugging strategy! Finally, Python recovers from exceptions, so Leo can keep right on going even after a crash!

Speed
*****

Python has almost all the speed of C. Other interpretive environments such as icon and Smalltalk have clarity, power and safety similar to Python. What makes Python unique is its seamless way of making C code look like Python code. Python executes at essentially the speed of C code because most Python modules are written in C. The overhead in calling such modules is negligible. Moreover, if code is too slow, one can always create a C module to do the job.

In fact, Python encourages optimization by moving to higher levels of expression. For example, Leo's Open command reads an XML file. If this command is too slow I can use Python's XML parser module. This will speed up Leo while at the same time raising the level of the code.

Conclusions
***********

Little of Python is completely new. What stands out is the superb engineering judgment evident in Python's design. Python is extremely powerful, yet small, simple and elegant. Python allows me to express my intentions clearly and at the highest possible level.

The only hope of making Leo all it can be is to use the best possible tools. I believe Python will allow me to add, at long last, the new features that Leo should have.

Edward K. Ream, October 25, 2001.  P.S., September, 2005:

Four years of experience have only added to my admiration for Python. Leo could
not possibly be what it is today without Python.


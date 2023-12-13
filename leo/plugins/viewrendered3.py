#@+leo-ver=5-thin
#@+node:TomP.20191215195433.1: * @file ../plugins/viewrendered3.py
#@@tabwidth -4
#@@language python
r"""
#@+<< vr3 docstring >>
#@+node:TomP.20191215195433.2: ** << vr3 docstring >>
#@@language rest
#@@nocolor
Creates a window for live rendering of reSTructuredText,
Markdown and Asciidoc text, images, movies, sounds, rst, html, jupyter notebooks, etc.

#@+others
#@+node:TomP.20200308230224.1: *3* About
About Viewrendered3 V4.02
===========================

The ViewRendered3 plugin (hereafter "VR3") renders Restructured Text (RsT),
Markdown (MD), and Asciidoc (nodes and subtrees) in a separate pane.
it duplicates and extendes the functionality of the ViewRendered plugin.  The plugin can:

    #. Render entire subtrees starting at the selected node;
    #. Render code and literal blocks in a visually distinct way;
    #. Any number of code blocks can be intermixed with RsT, MD, or Asciidoc in
       a single node.
    #. Display just the code blocks;
    #. Colorize code blocks;
    #. Execute Python code in the code blocks;
    #. Execute non-Python code blocks for certain languages.  Command line
       parameters can be passed to these language processors. [RsT only]
    #. Insert the print() output of an execution at the bottom of the rendered display;
    #. Identify code blocks by either an @language directive or by the code block
       syntax normally used by RsT, MD, or Asciidoc (e.g., code fences for MD);
    #. Honor "@" and "@c" directives to ignore all lines between them;
    #. Insert an image using the ``@image`` directive in addition to the image
       syntax for the structured text in use.
    #. Export the rendered node or subtree to the system browser;
    #. Export the generated markup to a chosen text editor.
    #. Optionally render mathematics symbols and equations using MathJax.
    #. While an entire subtree rendering is visible, the display can be locked
       so that the entire tree shows even while a single node is being edited.
    #. When an entire subtree is rendered, and editing is being done in one
       node, the display can be frozen (no changes will be displayed) if
       necessary to avoid excessive delay in re-rendering, or visual anomalies.
    #. The default rendering language for a node can be selected to by one of
       "RsT", "MD", "Asciidoc", or "TEXT".  This setting applies when the node
       or subtree has no @rst or @md headline.
    #. Display a node's headline text as the overall heading for the rendering.
       However, if the first line of a node exactly equals the headline text
       (not counting a directive like "@rst"), only one copy of that heading
       will be displayed.

A number of other special types of nodes can be rendered (see the
section `Special Renderings`_.

@setting nodes in an @settings tree can modify the behavior of the plugin.

New With This Version
======================
Bug fixes:
- Quit early if no qt gui.
- Fix messags with "VR4" to read "VR3".

Previous Recent Changes
========================
#@@language plain is equivalent to @language text.
VR3 can now open either in a pane in the splitter (up until now this is been the
only location) or in a tab in the log frame.  Two new commands give access to
the tab: *vr3-tab* and *vr3-toggle-tab*.

*@*/*@c* now work correctly for ReStructuredText for multiline strings.  This
fix makes them work the same way for all three structured languages: *rest*,
*md*, and *asciidoc*.


For both plain and text, an @language directive at the top of a node is removed.

For both plain and text, the command *vr3-open-markup-in-editor* can display
the entire subtree's text when that option is active.

An external Ruby asciidoctor processor is found more reliably.  The complete
path to the processor can be specified in the *vr3-prefer-external* setting
(sometimes Ruby can be installed into a location not on the PATH).

Asciidoctor enhancements

    - New setting to suppress the default footer (``@bool vr3-asciidoctor-nofooter = True``).
    - Set default directory for asciidoctor icons (``@string vr3-asciidoctor-icons=''``).
    - Set default image directory (``@string vr3-asciidoctor-imagesdir=''``).

The Dart programming language is now supported.

New minibuffer commands *vr3-freeze* and *vr3-unfreeze*.

Improved detection of the notebook URL in *@jupyter* nodes.  The URL no longer
has to be the second item in the headline after the string "@jupyter".  If
a URL is not found in the headline, the first line of the body is tried.

Fix commands "vr3-lock", "vr3-unlock", "vr3-lock-unlock-tree" so that they
correctly lock or unlock the rendering to the current subtree, including
changing the checked/unchecked character of the toolbar menu "locked to tree" item.

Correct Asciidoc rendering bug when rendering entire tree.

Correct handling of case when markdown package is not installed.

Mathjax, html pages with script imports work with PyQt6.

Added new command *vr3-render-html-from-clip*.

Added Lua to the list of supported languages.  Lua programs can be syntax-colored
and executed using the ``@language lua`` directive. For Lua programs to be executable,
the path to a Lua processor must be added to the *.leo/vr3/vr3_config.ini* file.

Added a line similar to the following to the *[executables]* section::

    lua = C:\Program Files (x86)\Lua\5.1\lua.exe
#@+node:TomP.20200309205046.1: *3* Compatibility
Compatibility
=============

Viewrendered3 is intended to be able to co-exist with Viewrendered.  In limited
testing, this seems to work as expected.

It is advisable to bind VR to a different hot key than VR3.  One possibility is
Alt-0 for VR3 and Alt-F10 for VR.

#@+node:TomP.20200308232305.1: *3* Limitations and Quirks
Limitations and Quirks
======================

    #. The plugin requires PyQt5 or PyQt6. All Leo versions since 6.0 can
       use at least PyQt5 so this requirement should always be met. The PyQt6
       version must be at least 6.23 to avoid limited rendering capability.

    #. The RsT processor (``docutils``) is fussy about having blank lines after
       blocks.  A node may render correctly on its own, but will show errors
       when displayed in a subtree.  In most cases, the fix is to add a blank
       line at the end of a node. This may be fixed in a future version.

    #. Without MathJax, mathematical symbols in RsT are rendered using CSS,
       which has a cruder appearance than MathJax rendering but may be servicable.
       With MD, mathematical symbols are not rendered without MathJax.

    #. Code blocks for several programming languages can be colorized, even
       within a single node.  Python, and certain other languages can be
       executed if they have been installed.  Python code blocks are
       executed with a Leo environment the includes the standard Leo
       variables c, g, and c.p.

    #. All code blocks in a node or subtree must contain the same code language
       or they cannot be executed.

    #. Non-Python code can currently only be executed in RsT trees.

    #. Text nodes and subtrees that have no language specified are rendered as
       preformated text.  They cannot be executed.

    #. Behavior for nodes other than @rst or @md nodes is the same as for the
       Viewrendered plugin.  This includes any bugs or unexpected behaviors.

    #. There is currently no provision to pass through extensions to the
       Markdown processor.

    #. The rendered pane can change the magnification (zoom and unzoom) using
       the standard hot keys <CTRL>+ - and <CTRL>+ =.  This only works if the
       cursor has been clicked inside the render pane first.  You may have to
       click back in the body or outline panes after this.

#@+node:TomP.20200115200249.1: *3* Dependencies
Dependencies
============

This plugin uses docutils, http://docutils.sourceforge.net/,
to render reStructuredText, so installing docutils is highly
recommended when using this plugin.

This plugin uses markdown,
http://http://pypi.python.org/pypi/Markdown, to render Markdown,
so installing markdown is highly recommended when using this plugin.

This plugin uses pygments to regenerate the MD stylesheet.


#@+node:TomP.20200115200807.1: *3* Settings and Configuration
Settings and Configuration
==========================

Settings
---------

Settings are put into nodes with the headlines ``@setting ...``.
They must be placed into an ``@settings`` tree, preferably
in the myLeoSettings file.

All settings are of type @string unless shown as ``@bool``.

.. csv-table:: VR3 Settings
   :header: "Setting", "Default", "Values", "Purpose"
   :widths: 18, 5, 5, 30

   "vr3-default-kind", "rst", "rst, md, asciidoc", "Default for rendering type"
   "vr3-ext-editor", "''", "Path to external editor", "Specify desired external editor to receive generated markup"
   "vr3-math-output", "False", "bool (True, False)", "RsT MathJax math rendering"
   "vr3-md-math-output", "False", "bool (True, False)", "MD MathJax math rendering"
   "vr3-mathjax-url", "''", "url string", "MathJax script URL (both RsT and MD)"
   "vr3-rst-stylesheet", "''", "url string", "Optional URL for RsT Stylesheet"
   "vr3-rst-use-dark-theme", "''", "True, False", "Whether to force the use of the default dark stylesheet"
   "vr3-md-stylesheet", "''", "url string", "Optional URL for MD stylesheet"
   "@bool vr3-insert-headline-from-node", "True", "True, False", "Render node headline as top heading if True"


.. csv-table:: Asciidoctor External Processor Settings
   :header: "Setting", "Default", "Values", "Purpose"
   :widths: 18, 5, 5, 30

   "vr3-asciidoc-path", "''", "string", "Path to ``asciidoc`` directory"
   "@bool vr3-prefer-asciidoc3", "False", "True, False", "Use ``asciidoc3`` if available, else use ``asciidoc``"
   "@string vr3-prefer-external", "''", "Name of external asciidoctor processor", "Use Ruby ``asciidoctor`` program"
   "@bool vr3-asciidoctor-nofooter", "False", "True, False", "Whether to suppress footer (``sciidoctor`` only)"
   "@string vr3-asciidoctor-icons", "''", "'', font, image", "Whether to use icons (``asciidoctor`` only)"
   "@string vr3-asciidoctor-imagesdir", "''", "'', absolutePath, relativePath, URL", "Whether to use imagesdir (``asciidoctor`` only)"
   "@bool vr3-asciidoctor-diagram", "False", "False, True", "Whether to use the ``asciidoctor-diagram`` extension to render plantuml diagrams"

.. csv-table:: Int Settings (integer only, do not use any units)
   :header: "Setting", "Default", "Values", "Purpose"
   :widths: 18, 5, 5, 30

   qweb-view-font-size, \-, small integer, Change Initial Font size

**Examples**::

    @string vr3-mathjax-url = file:///D:/utility/mathjax/es5/tex-chtml.js
    @string vr3-mathjax-url = https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.6/latest.js?config=TeX-AMS_CHTML
    @string vr3-md-math-output = True
    @int qweb-view-font-size = 16

**Note** The font size setting, *qweb-view-font-size*, will probably not be needed.  Useful values will generally be from 8 - 20.

Hot Key
=======

Binding the plugin's visibility to a hot key is very desirable.  ``Alt-0`` is
convenient.  The standard Leo way to bind a hot key is by putting the binding
into the body of a setting node with the headline ``@shortcuts``.  Here is an
example for the VR3 plugin::

    vr3-toggle = Alt+0

#@+node:tom.20210612193759.1: *4* Stylesheets
Stylesheets
===========

#@+node:tom.20211118000408.1: *5* ReStructuredText
ReStructuredText
------------------

Default CSS stylesheets are located in Leo's plugin/viewrendered3 directory. For
Restructured Text, stylesheet handling is quite flexible.

There are dark-theme and light-theme default stylesheets for RsT and MD. If no
related settings are present, then VR3 chooses the dark one if the Leo
theme name contains "dark" or the theme name is "DefaultTheme".

If the setting ``@bool vr3-rst-use-dark-theme = True``, then the dark theme will
be used. If it is set to ``False``, then the light one will be used.

The use of these default stylesheets can be overridden by the setting ``@string
vr3-rst-stylesheet``. This setting must be set to the path of a css stylesheet
file. If it is a relative path, it is taken to be relative to the user's
.leo/vr3 directory. If it is an absolute path, then the string ``file:///`` may
be prepended to the path; it will be removed if present.

These stylesheet settings can be changed and will take effect when the settings
are reloaded, and VR3 is refreshed or restarted. There is no need to close Leo
and restart it.

These settings can be placed into the @settings tree of an outline, and then
that outline's settings will be used when that outline is active. It is possible
for one outline to use the dark stylesheet, another to use the light stylesheet,
and a third to use a custom one.
#@+node:tom.20211118000432.1: *5* Markdown
Markdown
---------

Markdown stylesheets can be specified in very flexible ways. Css stylesheets are
looked for first in the user's `~/.leo/vr3 directory`, and then in the
`leo/plugins/viewrendered3` directory.  The choice of stylesheet is as follows:

- If the string setting `vr3-md-stylesheet` contains an absolute path, that file will
  be used if it is found;  if it contains a bare file name, it will be used if it can
  be found in either of the two stylesheet directories.

Otherwise:

- If the boolean setting `vr3-md-style-auto` is ``True``, then the current Leo theme
  will be examined to see if it is a dark theme or not.  If the theme is dark (light),
  a stylesheet named `md_styles_solarized_dark.css` (`md_styles_solarized_light.css`)
  will be looked for in the two stylesheet directories and used if found.

Otherwise:

- A default stylesheet named `md_styles.css` will be looked for in the two stylesheet
  directories. If is not found, the plugin will re-create it on startup
  (however, the RsT stylesheet will not be recreated if removed).

The dark, light, and default stylesheets are included in the `leo/plugins/viewrendered3` directory.

This priority scheme allow a user to modify any of the standard stylesheets in the default location
(`leo/plugins/viewrendered3`) and put them in the `~/.leo/vr3` in order to override the standard ones.

When a specific stylesheet path is specified by the `vr3-md-stylesheet` setting, the path separators
can be any mix of Windows and Linux separators.

#@+node:tom.20210612193820.1: *4* MathJax Script Location
MathJax Script Location
=======================

The script for MathJax rendering of math symbols can be in a local directory on
your computer.  This has the advantages of fast loading and working without an
internet. Using an Internet URL has the advantage that the URL will work if the
exported HTML file is sent to someone else.

If the MathJax scripts are installed on the local computer, it is recommended
that one of the ``.js`` script files in the ``es`` directory be used, as shown
in the above table.  If the script is loaded from the Internet, the URL must
include a ``?config`` specifer.  The one shown in the example above works well.

#@+node:TomP.20210422235304.1: *4* External Processors For Other Languages
External Processors For Other Languages
=======================================

VR3 can make use of external processors for executing code blocks in programming languages other than Python.  Examples are Javascript and Julia.  Parameters can be passed to the processor as well.  The command line must have the format::

    <processor> [optional parameters] filename

External language processors must be specified in the file `vr3_config.ini`.  This file is located in the `vr3` directory under Leo's Home directory.  The must be entered in the `[executables]` section. Here is an example::

    [executables]
    javascript = D:\usr\graalvm-ce-java11-20.0.0\languages\js\bin\js.exe
    julia = C:\Users\tom\AppData\Local\Programs\Julia 1.5.3\bin\julia.exe

Note that

1. The name of the language (e.g., `julia`) **must** agree with the name of the language used in `@language` directives;

2. The full path to the processing executable **must** be included.  VR3 will not use the system path, and the processor need not be on the system path.

This directory and .ini file must be created by the user.  VR3 will not create them.

A language that is specified here will not automatically be executed: only languages known by VR3 will be executed.  Code in known languages will be colorized provided that Leo has a colorizing mode file for that language.  This should normally be the case.  For example, colorizer mode files for both julia and javascript are included in the version of Leo that includes this version of VR3.

VR3 can only successfully execute code if all code blocks in a node or subtree use the same language.

#@+node:TomP.20210423000029.1: *5* @param Optional Parameters
Optional Parameters
====================

\@param - Specify parameter(s) to be passed to a non-Python language processor.
-------------------------------------------------------------------------------
The `@param` directive specifies command-line parameters to be passed
to an external language processor.  These parameters will be inserted
between the name of the processor and the name of a temporary file that
VR3 will write the program code to.

For example if we include the following directives::

    @language julia
    @param -q

then the julia processor will be invoked with the command line::

    <path-to-julia> -q <progfile>

Any number of parameters may be included on one @param line, and
multiple @param directives are allowed.  Parameters can include redirection symbols (e.g., "<", ">").

Only @param directives that occur inside a code block are recognized.  Thus the following @param directive is not recognized because it is
outside a code block::

    @language rest
    @param -q

    @language julia
    # code to execute
    # ...

#@+node:TomP.20210423002026.1: *5* Limitations
Limitations
============

1. The ability to launch an external processor currently works only for ReStructuredText markup language nodes or trees.

2. The supported command line format is fairly simple, so a language that needs separate compile and run stages will be difficult to use.

#@+node:TomP.20200115200324.1: *3* Commands
Commands
========

viewrendered3-specific commands all start with a "vr3-" prefix.  There is
rarely a reason to invoke any of them, except these:

    1. ``vr3-toggle`` and ``vr3-toggle-tab``, which show or hide the VR3 pane.
    They are best bound to a hot key (see `Hot Key`_) or button.  The "*-tab*"
    versions open in a tab in the log frame.  Either command will close
    the VR3 pane, no matter whether it is open in a tab or in a splitter pane.

    2. ``vr3`` and ``vr3-tab`` open VR3 in a splitter pane or a tab in the
    log panel, respectively.  If one of these commands is issued while VR3
    is already open, it will stay open but move from splitter to tab or
    vice-versa depending on which command was issued.
    
    .. Note:: ``vr3-use-default-layout`` opens VR3 in a splitter pane with three full-height panes.

    3.``vr3-open-markup-in-editor`` exports the generated markup
    to temporary file and opens it in a text editor. The editor
    is one specified by the setting ``@string vr3-ext-editor``,
    the setting ``@string external-editor``, by the environmental
    variable ``EDITOR`` or ``LEO-EDITOR``, or is the default
    editor chosen by Leo.

    4. ``vr3-help-plot-2d`` opens a help page in the system browser
    for the *Plot 2D* capability.

    5. ``vr3-lock-unlock-tree`` locks/unlocks the rendering to the current
    subtree if the *Entire Tree* option is set.

    6. ``vr3-freeze``/``vr3-unfreeze`` prevents/allows updating the rendering
    panel.


#@+node:TomP.20200902222012.1: *3* Structured Text
Structured Text
===============

VR3 renders three kinds of structured text: reStructured Text (RsT), Markdown (MD),
and Asciidoc.  Normally the currently selected node is rendered, but a toolbar menu item
can be selected to render an entire subtree, or just the code blocks.

Any number of code blocks can be used in a node, but do not split a
code block across two nodes.

Other languages are supported besides python.  See the list of languages below
at `Colorized Languages`_.  Only Python can be successfully executed.

VR3 can render RsT, MD, and Asciidoc, but do not include more than one in any
one node or subtree.

#@+node:TomP.20200902222226.1: *4* Special Directives
Special Directives
------------------

For all structured text types, VR3 recognizes certain special Leo directives.
Each of these directives must begin with an "@" character at the start of a line.

\@/@c - Omit Text
-------------------
All lines between the pair "@" and "@c" will be omitted.

\@language - Set Language Type For Node Or Block
--------------------------------------------------
If a node or the top of a subtree begins with `@rst`, `@md`, or `asciidoc`,
that language will be the default language of the node or subtree.  If the
node or subtree is not marked with one of these `@xxx` types, then the
default language is given by the setting `@string vr3-default-kind = xxx`.
This can be overridden by the ``Default Kind`` toolbar menu.

Within a node, the ``@language`` directive will set the language to be used
until another ``@language`` directive or the end of the node.

Current languages are `rst`, `rest`, `md`, `asciidoc`, `text`, `python`,
`javascript`, `java`, `css`, and `xml`.

A directive line must be blank except for the elements of the directive.
Examples of ``@language`` directives::

    @language python
    def f(x):
        return 2*x

    @language javascript
    function f(x) {
        return 2*x;
    }

    @language java
    function f(x) {
        return 2*x;
    }


\@image - Alternate Method For Inserting an Image
--------------------------------------------------
In addition to the image syntax of the structured text in use, the `@image`
directive can be used::

    @image url-or-file_url-or-data_url

\@param - Insert optional parameters for an external language processor
------------------------------------------------------------------------
See `Settings and Configuration/External Processors/Optional Parameters`.

#@+node:TomP.20200115200601.1: *4* Rendering reStructuredText
Rendering reStructuredText
==========================

The VR3 plugin will render a node using RsT if its headline, or the headline of
a parent, starts with ``@rst``. The type of rendering is called its "kind". If
no kind is known, then RsT rendering will be used unless the ``vr3-default-kind``
setting is set to another allowed value.  The default kind can also be changed
using the ``Default Kind`` menu.

**Note**: reStructuredText errors and warnings will appear in red in the
rendering pane.

#@+node:TomP.20200115200634.1: *4* Rendering Markdown
Rendering Markdown
==================

Please see the markdown syntax document at

http://daringfireball.net/projects/markdown/syntax

for more information on markdown.

Unless ``@string vr3-default-kind`` is set to ``md``, markdown
rendering must be specified by putting it in a ``@md`` node.

Literal Blocks
--------------
A literal block is declared using backtick "fences"::


    ```text
    this should be a literal block.
    ```

Note that the string ``text`` is required for proper rendering,
even though some MD processors will accept the triple-backtick
fence by itself without it. Fences must begin at the start of a line.

Code Blocks
------------
A code block is indicated with the same fence, but the name of
the language instead::

    ```python
    def f(x):
        return 2*x
    ```

.. note::
    No space is allowed between the fence characters and the language.

Mathematics
------------
Mathematics symbols and equations can be rendered with MathJax.  When enabled by the *vr3-md-math-output* setting, inline formulas and separate equation blocks can be specifed.  Equations are written in a Latex dialect.

Inline Formulas
________________
Inline formulas are enclosed with the symbol pairs *\\(* and *\\)*.

Equation Blocks
________________
There are several ways to enclose equation blocks.  The Markdown (semi-)standard way is to use a math fence, similar to a literal or code block::

    ```math
    \begin{align*}
        α_t(i) &=P(O_1,O_2,…O_t,q_t)=S_iλ\\
        k &=\int_{0}^{10}xdx\\
        E &=mc^2
    \end{align*}
    ```
The fence must start at the beginning of a line.

Blocks may also be enclosed with the standard MathJax delimiters, either double *$* characters::

    $$
    \begin{align*}
        α_t(i) &=P(O_1,O_2,…O_t,q_t)=S_iλ\\
        k &=\int_{0}^{10}xdx\\
        E &=mc^2
    \end{align*}
    $$

or *\\[*, *\\]* pairs::

    \[
    \begin{align*}
        α_t(i) &=P(O_1,O_2,…O_t,q_t)=S_iλ\\
        k &=\int_{0}^{10}xdx\\
        E &=mc^2
    \end{align*}
    \]


Tables
-------
Tables may be created using the `PHP Markdown Extra` syntax: https://python-markdown.github.io/extensions/tables/.  Here is an example from the Markdown package documentation::


    First Header  | Second Header
    ------------- | -------------
    Content Cell  | Content Cell
    Content Cell  | Content Cell

No Language Mixing
-------------------
As with RsT rendering, do not mix multiple structured languages in a single
node or subtree.

#@+node:TomP.20200820170225.1: *4* Rendering Asciidoc
Rendering Asciidoc
===================

The VR3 plugin will render a node using Asciidoc if
an Asciidoc or Asciidoc3 processor has been installed and the node type
is ``@asciidoc`` or if the node starts with ``@language asciidoc``.

The asciidoc processor must be one of:

    1. *asciidoctor*, which requires a Ruby environment to be
       installed on your computer;

    2. *asciidoc* from https://asciidoc.org/index.html.
       This may be available pre-installed or as a package
       in some Linux distributions;

    3. *asciidoc3*, which is available as a python pip-installable
       package but may be hard to get working on Windows.

Processor Priority
-------------------
A user may have both *asciidoc* and asciidoc3* installed.  VR3 will
try processors using the following priority:

1. The Ruby *asciidoctor* processor if it is requested by the setting::

    @string vr3-prefer-external = asciidoctor

2. *asciidoc3* if requested by the setting::

    @bool vr3-prefer-asciidoc3 = True

3. *asciidoc* .  If the setting *vr3-prefer-asciidoc3* is not *True*, then asciidoc will be tried before asciidoc3.

asciidoctor
-------------
To use *asciidoctor* first install Ruby.  First install the Ruby code environment.
It is not necessary to install the entire development system. A minimal
install will be enough. Next, run the following commands in a terminal
or Windows console::

    gem install asciidoctor
    gem install pygments.rb

There is more information at https://docs.asciidoctor.org/asciidoctor/latest/install/ruby-packaging/.
VR3 will attempt to find the program when it starts up.  The program should
be on your PATH.

If the ``asciidoctor-diagram`` gem is installed, the asciidoctor processor will be able to render nodes that contain a plantuml diagram.  To install the gem, run the following command in a terminal or console::

    gem install asciidoctor-diagram

To declare a plantuml diagram, use this header::

    [plantuml, target=diagram-classes, format=png, !pragma layout smetana]

If the ``asciidoctor-diagram`` extension is not present, VR3 will only render the text in the node as ordinary asciidoc, not as a diagram.  No error message will be given.

A diagram must follow this example::

    [plantuml, target=diagram-classes, format=png, !pragma layout smetana]
    ....
    class BlockProcessor
    class DiagramBlock
    class DitaaBlock
    class PlantUmlBlock

    BlockProcessor <|-- DiagramBlock
    DiagramBlock <|-- DitaaBlock
    DiagramBlock <|-- PlantUmlBlock
    ....


asciidoc
--------
*asciidoc* comes as a zip file, and is normally unzipped in some convenient
location.  The setting *@string vr3-asciidoc-path* must point to the
unzipped directory, e.g.::

    @string vr3-asciidoc-path = c:\utility\asciidoc-9.1.0

asciidoc3
----------
asciidoc3 is a Python package that can be installed with pip.  On Windows,
a post-install program must be run.  Sometimes, and with some versions,
asciidoc3 will malfunction on Windows.  If that happens, a message will
be written to Leo's Log pane and VR3 will try to use *asciidoc* if it is
present.


.. note:: The Asciidoc processors are quite slow at rendering
          long documents, as can happen when the "Entire Tree"
          setting is used.The Ruby *asciidoctor* is much faster,
          but there will be a delay as the Ruby runtime is loaded.

          When rendering is slow, typing into a node can be annoying.
          If so, use VR3's *Freeze* and *Reload* toolbar functions.

Rendering Equations and Formulas
---------------------------------
When the setting *@bool vr3-math-output* is set to *True*, then a MathJax script
will be included in the HTML output. Mathjax interprets a subset of Latex to
render mathematics.  The Latex expressions must be enclosed by delimiters. The following seem to work with all three processors, although  you may need to experiment if
math renderings do not look right.

1. Inline math: enclose the latex with ``\( ....\ \)`` characters, where where ``....`` represents the Latex math expression.  Example::

    \(a = \sqrt{b}\ \)

.. Note:: There must be a backslash following the last character of the inline math, with no space bfore that added backslash.

2. Blocks, such as aligned equations: enclose the latex block with ``$$ .... $$``,
where ``....`` represents the Latex expressions.

Asciidoc Dialects
=================
Asciidoc dialects vary somewhat.  The dialect used by the
asciidoc processors described above does not use the
syntactical form ``[.xxx]``, e.g., ``[.big.]``.  Instead,
the leading period must be omitted: ``[big]``. There may be
other differences.

#@+node:TomP.20200309191519.1: *3* Colorized Languages
Colorized Languages
===================

Currently the languages that can be colorized are python, dart, javascript,
java, julia, css, xml, and sql.

#@+node:TomP.20210225000326.1: *3* Code Execution
Code Execution
===============

Code that occurs inside one or more code blocks can be executed.
Execution is initiated when the "Execute" button on the
VR3 toolbar is pressed.  Output from the processor to stdout and
stderr is displayed under the node (or last node of a subtree).

A node may contain multiple code blocks, but they can only successfully
be executed if they are all for the same code language.

Command line parameters can be specified using one or more `@param`
directives (see above at Structured Languages/Special Directives).

Python code will be executed within a Leo environment that includes
the standard Leo variables g, c, and c.p.  Thus, Leo-specific
commands like g.es() can be invoked.

If View Options/Entire Tree is checked on the VR3 toolbar, then
all code blocks in the current node and all its child nodes
(to any nesting depth) will be executed.  Otherwise only the current
node will be executed.

If only the current node is to be executed, note that if imports occur or variables are declared in a parent node, then execution of the node
will fail because the current node being executed will not know
about them.

Processor output for stdout (i.e., print() statements, etc. and
stderr are captured and displayed inline below the code.

Non-Python code can be executed if

    #. A language processor for the target language has been installed
       on the computer;

    #. The processor invokes a program using a command line like thus::

        <path-to-processor> [parameters] <program file>

The full path to non-Python processors is specified in a configuration
file located in Leo's home directory, `.leo`.  This file is at::

    .leo/vr3/vr3_config.ini

The language processor(s) must be defined in an ``[executables]`` section
of the configuration file, like this::

    [executables]
    javascript = D:\usr\graalvm-ce-java11-20.0.0\languages\js\bin\js.exe
    julia = C:\Users\tom\AppData\Local\Programs\Julia 1.5.3\bin\julia.exe

The names of the languages **must** be spelled exactly as they are used
in `@language` directives.

The languages that can currently be used are `javascript` and `julia`.  This list may be expanded in the future.

#@+node:TomP.20200115200704.1: *3* Special Renderings
Special Renderings
==================

As stated above, the rendering pane renders body text as reStructuredText
by default, with all Leo directives removed. However, if the body text
starts with ``<`` (after removing directives), the body text is rendered as
html.

This plugin renders @md, @image, @jupyter, @html, @movie, @networkx and @svg
nodes as follows:

**Note**: For @image, @movie and @svg nodes, either the headline or the first
line of body text may contain a filename.  If relative, the filename is resolved
relative to Leo's load directory.

- ``@md`` renders the body text as markdown, as described above.

- ``@graphics-script`` executes the script in the body text in a context
  containing two predefined variables:

    - gs is the QGraphicsScene for the rendering pane.
    - gv is the QGraphicsView for the rendering pane.

  Using these variables, the script in the body text may create graphics to the
  rendering pane.

- ``@image`` renders the file as an image.

    The headline should start with @image.
    All other characters in the headline are ignored.

    The first line of the body should be the full path to the image file.
    All other lines are ignored.

- ``@html`` renders the body text as html.

- ``@jupyter`` renders the output from Jupyter Notebooks.

  The contents of the @jupyter node can be either a url to the notebook or
  the actual JSON notebook itself.

  Use file:// urls for local files. Some examples:

      Windows: ``file:///c:/Test/a_notebook.ipynb``

      Linux:   ``file:///home/a_notebook.ipynb``

- ``@movie`` plays a file as a movie. @movie also works for music files.
  The path to the file must be on the first line of the body of the node.
  Media can be started or paused using the *vr3-pause-play-movie* command.
  Movies might not render in the current version, depending in video
  type and installed codecs.

- ``@networkx`` is non-functional at present.  It is intended to
  render the body text as a networkx graph.
  See http://networkx.lanl.gov/

- ``@svg`` renders the file as a (possibly animated) svg (Scalable Vector Image).
  See http://en.wikipedia.org/wiki/Scalable_Vector_Graphics

  .. note:: if the first character of the body text is ``<`` after removing
            Leo directives, the contents of body pane is taken to svg code.

#@+node:tom.20211104225431.1: *3* Easy Plotting Of X-Y Data
Easy Plotting Of X-Y Data
--------------------------

If the selected node contains data in one or two columns, VR3 can
plot the data as an X-Y graph. The labeling and appearance of the
plot can optionally and easily adjusted. The graph is produced
when the toolbar menu labeled *Other Actions* is pressed and
*Plot 2D* is clicked.

If the selected node has an optional section *[source]* containing the key *file*, the value of the key will be used as the path to
the data, instead of using the selected node itself as the data source.

Help for the plotting capability is displayed in the system
browser when *Other Actions/Help For Plot 2D* is clicked. This
help is also invoked by the minibuffer command
*vr3-help-plot-2d*.

#@+node:tom.20220225114320.1: *3* Rendering HTML From Clipboard
Rendering HTML From Clipboard
==============================

The VR3 command *vr3-render-html-from-clip* renders the clipboard string contents with the assumption that it is HTML.  The rendering can be exported to the system web browser using the VR3 *Export* button.

Pressing the *Reload* button restores the view to the current node.

Currently VR3 has to be open for the command to work.
#@+node:TomP.20200115200833.1: *3* Acknowledgments
Acknowledgments
================

The original Viewrendered plugin was created by Terry Brown, and enhanced by
Edward K. Ream. Jacob Peck added markdown support.

Viewrendered2 was created by Peter Mills, based on the viewrendered.py plugin.
It added the ability to render an entire RsT tree, the ability to display only
the code blocks, and to execute one block of Python code in a node and insert
any printed output into the node.  Thomas B. Passin enhanced Viewrendered2,
adding the ability to change from RsT to Python and back within a node.

Viewrendered3 was created by Thomas B. Passin to provide VR2 functionality with
Python 3/QT5. VR3 brings more enhancements to ReStructured Text and Markdown
rendering, and adds Asciidoc rendering.  Most functionality of the Viewrendered
is included, and some additional capability has been added..

Enhancements to the RsT stylesheets were adapted from Peter Mills' stylesheet.

#@-others

#@-<< vr3 docstring >>
"""

#@+<< imports >>
#@+node:TomP.20191215195433.4: ** << imports >>
#
# Stdlib...
from configparser import ConfigParser
from contextlib import redirect_stdout
from enum import Enum, auto
import html
from inspect import cleandoc
from io import StringIO, open as ioOpen

import json
import os
import os.path
from pathlib import PurePath
import re
import shutil
import site
import string

import subprocess
import sys
import textwrap
import webbrowser
from urllib.request import urlopen

# Leo imports...
import leo.core.leoGlobals as g
from leo.core.leoApp import LoadManager as LM

# 1946
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

#@+<< Qt Imports >>
#@+node:tom.20210517102737.1: *3* << Qt Imports >>
try:
    from leo.plugins import qt_text
    from leo.plugins import free_layout
    from leo.core.leoQt import QtCore, QtWidgets
    from leo.core.leoQt import phonon, QtMultimedia, QtSvg
    from leo.core.leoQt import KeyboardModifier, Orientation, WrapMode
    from leo.core.leoQt import QAction, QActionGroup
except ImportError:
    g.es('Viewrendered3: cannot import QT modules')
    raise ImportError from None

has_webengineview = False
try:
    from leo.core.leoQt import QtWebEngineWidgets
    has_webengineview = True
except ImportError:
    # Might have Qt without QtWebEngineWidgets
    if not g.unitTesting:
        g.trace("Can't import QtWebEngineWidgets")

qwv = None
if has_webengineview:
    qwv = QtWebEngineWidgets.QWebEngineView
    try:
        from leo.core.leoQt import QtWebEngineCore
        QWebEngineSettings = QtWebEngineCore.QWebEngineSettings
    except Exception:
        QWebEngineSettings = QtWebEngineWidgets.QWebEngineSettings
    from leo.core.leoQt import WebEngineAttribute
else:
    try:
        qwv = QtWidgets.QTextBrowser
        if not g.unitTesting:
            print("vr3: *** limited RsT rendering in effect")
            print('vr3" *** For full rendering capability,')
            print('vr3:     install QWebEngine using python3 -m pip install PyQt6-WebEngine')
            print('vr3:     for PyQt6 or python3 -m pip install PyQtWebEngine for PyQt5')
    except Exception as e:
        g.trace(e)

if QtSvg:
    if hasattr(QtSvg, 'QSvgWidget'):
        QSvgWidget = QtSvg.QSvgWidget
    else:
        QtSvg = None
#@-<< Qt Imports >>

# Optional imports...
try:
    import docutils
    import docutils.core
except ImportError:
    docutils = None
if docutils:
    try:
        from docutils.core import publish_string
        from docutils.utils import SystemMessage
        got_docutils = True
    except ImportError:
        got_docutils = False
        g.es_exception()
    except SyntaxError:
        got_docutils = False
        g.es_exception()
else:
    got_docutils = False
    print('VR3: *** no docutils')
try:
    import markdown
    got_markdown = True
except ImportError:
    got_markdown = False
    print('VR3: *** No Markdown ***')
try:
    import matplotlib  # Make *sure* this is imported.
    import matplotlib.pyplot as plt
    from matplotlib import animation
except ImportError:
    matplotlib = None
    print('VR3: *** No matplotlib')
try:
    import numpy as np
except ImportError:
    print('VR3: *** No numpy')
    np = None
# nbformat (@jupyter) support, non-vital.
jupyter_ok = nbformat_ok = nbconvert_ok = False
try:
    from nbconvert.exporters import HTMLExporter
    nbconvert_ok = True
except ImportError:
    print('VR3: *** nbconvert module is needed by @jupyter nodes.\n'
          '         if you want to use @jupyter nodes, then\n'
          '         install nbconvert: python3 -m pip install nbconvert')
try:
    import nbformat
    nbformat_ok = True
    # from traitlets.config import Config
except ImportError:
    print('VR3: *** nbformat module is needed by @jupyter nodes.\n'
          '         if you want to use @jupyter nodes, then\n'
          '         install nbformat: python3 -m pip install nbformat')
jupyter_ok = nbformat_ok and nbconvert_ok

try:
    from pygments import cmdline
except ImportError:
    pygments = None
    print('VR3: *** no pygments')
#@-<< imports >>
#@+<< declarations >>
#@+node:TomP.20191231111412.1: ** << declarations >>
# pylint: disable=invalid-name
C = 'c'
VR3_NS_ID = '_leo_viewrendered3'
VR3_DEF_LAYOUT = 'viewrendered3_default_layouts'

TABNAME = 'VR3'
OPENED_IN_TAB = 'tab'
OPENED_IN_SPLITTER = 'splitter'

ASCIIDOC = 'asciidoc'
CODE = 'code'
CSS = 'css'
DART = 'dart'
ENCODING = 'utf-8'
JAVA = 'java'
JAVASCRIPT = 'javascript'
JULIA = 'julia'

LUA = 'lua'
MATH = 'math'
MD = 'md'
PLAIN = 'plain'
PYPLOT = 'pyplot'
PYTHON = 'python'
RESPONSE = 'response'
REST = 'rest'
RST = 'rst'

ASCIIDOC_CONF_FILENAME = 'html5.conf'
MATHJAX_POLYFILL_URL = 'https://polyfill.io/v3/polyfill.min.js?features=es5'
MATHJAX_URL = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml-full.js'

#@+<< RsT Error styles>>
#@+node:tom.20210621192144.1: *3* << RsT Error styles>>
RST_ERROR_BODY_STYLE = ('color:#606060;'
                        'background: aliceblue;'
                        'padding-left:1em;'
                        'padding-right:1em;'
                        'border:thin solid gray;'
                        'border-radius:.4em;')

RST_ERROR_MSG_STYLE = ('color:red;'
                       'background:white;'
                       'padding-left:1em;'
                       'padding-right:1em;'
                       'border:thin solid gray;'
                       'border-radius:.4em;')
#@-<< RsT Error styles>>
# RST_HEADING_CHARS = '''=-:.`'"-~^_*+#'''# Symbol hierarchy - maybe some day
RST_HEADING_CHARS = '''=============='''  # For now, same symbol for all levels
RST_NO_WARNINGS = 5

SQL = 'sql'
TEXT = 'text'
VR3_TEMP_FILE = 'leo_rst_html.html'
XML = 'xml'
ZOOM_FACTOR = 1.1

#@+<< MD stylesheets >>
#@+node:tom.20211117122509.1: *3* << MD stylesheets >>
MD_BASE_STYLESHEET_NAME = 'md_styles.css'
MD_STYLESHEET_DARK = 'md_styles_solarized_dark.css'
MD_STYLESHEET_LIGHT = 'md_styles_solarized_light.css'

MD_STYLESHEET_APPEND = '''pre {
   font-size: 110%;
   border: 1px solid gray;
   border-radius: .7em; padding: 1em;
   background-color: #fff8f8
}
body, th, td {
  font-family: Verdana,Arial,"Bitstream Vera Sans", sans-serif;
  background-color: white;
  font-size: 90%;
}
'''

MD_STYLESHEET_DARK_APPEND = '''pre {
   font-size: 110%;
   border: 1px solid gray;
   border-radius: .7em; padding: 1em;
   background-color: #fff8f8
}
body, th, td {
  font-family: Verdana,Arial,"Bitstream Vera Sans", sans-serif;
  color: #839496;
  background: #002b36;
  font-size: 90%;
}
'''
#@-<< MD stylesheets >>

TEXT_HTML_HEADER = f'''<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset={ENCODING}">
</head>
'''

LEO_THEME_NAME = 'DefaultTheme.leo'
RST_DEFAULT_STYLESHEET_NAME = 'vr3_rst.css'
RST_DEFAULT_DARK_STYLESHEET = 'v3_rst_solarized-dark.css'
RST_USE_DARK = False

# For code rendering
LANGUAGES = (PYTHON, DART, JAVASCRIPT, JAVA, JULIA, LUA, CSS, XML, SQL)
TRIPLEQUOTES = '"""'
TRIPLEAPOS = "'''"
RST_CODE_INTRO = '.. code::'
MD_CODE_FENCE = '```'
MD_MATH_FENCE = '```math'
ASCDOC_CODE_LANG_MARKER = '[source,'
ASCDOC_FENCE_MARKER = '----'

RST_INDENT = '    '
SKIPBLOCKS = ('.. toctree::', '.. index::')
ASCDOC_PYGMENTS_ATTRIBUTE = ':source-highlighter: pygments'

_in_code_block = False

VR3_DIR = 'vr3'
VR3_CONFIG_FILE = 'vr3_config.ini'
EXECUTABLES_SECTION = 'executables'
LEO_PLUGINS_DIR = os.path.dirname(__file__)
NO_SVG_WIDGET_MSG = 'QSvgWidget not available'

#@+<< Misc Globals >>
#@+node:tom.20211126230402.1: *3* << Misc Globals >>
ad3_file = ''
asciidoc = None
asciidoctor = None
asciidoc_ok = False
asciidoc3_ok = False
asciidoc_dirs = {'asciidoc': {}, 'asciidoc3': {}}
asciidoc_processors = []
asciidoc_has_diagram = False
#@-<< Misc Globals >>
#@-<< declarations >>

trace = False  # This global trace is convenient.

#@+<< define html templates >>
#@+node:TomP.20191215195433.6: ** << define html templates >> (vr3)
image_template = '''\
<html>
<body bgcolor="#fffbdc">
<img style="width: 100%%" src="%s">
</body>
</html>
'''

# http://docs.mathjax.org/en/latest/start.html
latex_template = f'''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <script src="{MATHJAX_POLYFILL_URL}"></script>
    <script src='{MATHJAX_URL}'></script>
</head>
<body bgcolor="#fffbdc">
%s
</body>
</html>
'''
#@-<< define html templates >>

# keys for all three below: c.hash()
controllers = {}  # values: VR3 widets
positions = {}  # values: OPENED_IN_TAB or OPENED_IN_SPLITTER
layouts = {}  # values: tuples (layout_when_closed, layout_when_open)


#@+others
#@+node:TomP.20200508124457.1: ** find_exe()
def find_exe(exename):
    """Locate an executable and return its path.

    Works for Windows and Linux.  Works whether or not a virtual
    environment is in effect.

    Finds executables that are in:
        - the Python Scripts directory;
        - the system path.

    ARGUMENT
    exename -- the name of the executable file to find.

    RETURNS
    the full path to the executable as a string, or None.
    Returns None if the found executable is not marked as executable.
    """
    # Works for Linux and Windows
    venvdir = os.getenv("VIRTUAL_ENV")
    if venvdir:
        scriptsdir = os.path.join(venvdir, 'Scripts')
        scripts_local_dir = ''
    else:
        scriptsdir = os.path.join(os.path.dirname(sys.executable), 'Scripts')
        local_python_appdata_dir = os.path.dirname(site.getusersitepackages())
        scripts_local_dir = os.path.join(local_python_appdata_dir, 'Scripts')

    exe = shutil.which(exename, os.X_OK, scriptsdir) \
            or shutil.which(exename, os.X_OK, scripts_local_dir) \
            or shutil.which(exename, os.X_OK)

    return exe
#@+node:tom.20211127234312.1: ** find_dir()
def find_dir(name, path):
    """Given a starting directory, return the full path to the named directory.

    RETURNS
    A full directory, or None if the named directory is not found.
    """
    for root, dirs, files in os.walk(path):
        if name in dirs:
            return os.path.join(root, name)
    return None
#@+node:tom.20221231143118.1: ** get_gems()
def check_gems(gem: str, encoding: str = 'utf-8') -> bool:
    """Check if a particular ruby gem is installed."""
    cmd = f'gem list {gem}'
    # pylint: disable = subprocess-run-check
    proc = subprocess.run(cmd, shell=True, capture_output=True)
    installed = gem in proc.stdout.decode(encoding)
    return installed

#@+node:tom.20211125003406.1: ** configure_asciidoc
def configure_asciidoc():
    r"""
    #@+<< asciidoc docstring >>
    #@+node:tom.20211125003406.2: *3* << asciidoc docstring >>
    #@@nocolor
    Determine which Asciidoc processor to use.

    There are three possible processors:  asciidoc, asciidoc3, and asciidoctor.
    asciidoctor is a Ruby program and must be run as an external program.
    asciidoc comes as a zip file that gets unzipped somewhere.
    asciidoc3 can be installed with pip, but on Windows can be a problem
    to get working right.

    Each one has its own way to be called.  The rendering code needs to know
    which one to use.  VR3 will attempt to use one or the other depending
    on these settings:

        ``@string vr3-prefer-external = asciidoctor``
        Specifies the use of the external Ruby program, if available.

        ``@bool vr3-prefer-asciidoc3 = False``
        When an internal processor will be used, whether to try asciidoc3
        or asciidoc first.  Some installations will have both.

    Sets several variables::

        asciidoc3_ok      # imported asciidoc3
        asciidoc_ok       # imported asciidoc
        asciidoctor       # path to asciidoctor program

    This function also tries to detect the presence of the Ruby gem
    "asciidoctor-diagram", which the external asciidoctor processor uses to
    render Plantuml diagrams.  (If asciidoctor is used and a node contains a
    plantuml diagram, the diagram will be rendered).
    #@-<< asciidoc docstring >>
    """
    # pylint: disable = import-outside-toplevel
    global AsciiDocAPI, AsciiDoc3API, ad3, ad3_file
    global asciidoc_ok, asciidoc3_ok, asciidoc_processors
    global asciidoc_dirs
    global asciidoc_has_diagram

    asciidoc_ok = False
    asciidoc3_ok = False
    asciidoc_has_diagram = check_gems('asciidoctor-diagram')

    #@+<< get asciidoc >>
    #@+node:tom.20211125003406.3: *3* << get asciidoc >>
    try:
        from asciidoc import AsciiDocAPI
        from asciidoc.asciidoc import VERSION
        version = VERSION.split('.')
        major = int(version[0])
        goldilocks = int(version[1])
        minor = int(version[-1])
        dopatch = major == 10 and goldilocks == 0 and minor < 3

        def new_init(self, asciidoc_py=None):
            self.options = Options()
            self.attributes = {}
            self.messages = ['AsciiDocError']
            self.asciidoc = self
            self.cmd = 'asciidoc'

        if dopatch:
            print('.... Patching asciidoc')
            from asciidoc.api import Options
            AsciiDocAPI.__init__ = new_init

        asciidoc_ok = True

    except ImportError:
        g.es('VR3 -- no asciidoc processor')

    if asciidoc_ok:
        # These locations are needed by our custom config file html5.conf
        d_ = {}
        file_ = sys.modules['asciidoc.asciidoc'].__file__
        asciidoc_dir = os.path.dirname(file_)
        d_['stylesheets'] = find_dir('stylesheets', asciidoc_dir)
        d_['javascripts'] = find_dir('javascripts', asciidoc_dir)
        asciidoc_dirs['asciidoc'] = d_
    #@-<< get asciidoc >>
    #@+<< get asciidoc3 >>
    #@+node:tom.20211125003406.4: *3* << get asciidoc3 >>
    try:
        from asciidoc3.asciidoc3api import AsciiDoc3API
        from asciidoc3 import asciidoc3 as ad3
        ad3_file = ad3.__file__
        asciidoc3_ok = True
    except ImportError:
        asciidoc3_ok = False
        g.es('VR3 -- no asciidoc3 processor')

    if asciidoc3_ok:
        # These locations are needed by our custom config file html5.conf
        d_ = {}
        asciidoc3_dir = os.path.dirname(ad3_file)
        d_['stylesheets'] = find_dir('stylesheets', asciidoc3_dir)
        d_['javascripts'] = find_dir('javascripts', asciidoc3_dir)
        asciidoc_dirs['asciidoc3'] = d_
    #@-<< get asciidoc3 >>

configure_asciidoc()
#@+node:TomP.20200508125029.1: ** Find External Executables
pandoc_exec = find_exe('pandoc') or None
#@+node:TomP.20210218231600.1: ** Find executables in VR3_CONFIG_FILE
#@@language python
# Get paths for executables from the VR3_CONFIG_FILE file
lm = LM()
leodir = os.path.abspath(g.app.homeLeoDir)

inifile = os.path.join(leodir, VR3_DIR, VR3_CONFIG_FILE)
inifile_exists = os.path.exists(inifile)

exepaths = {}
if inifile_exists:
    config = ConfigParser()
    config.read(inifile)
    if config.has_section(EXECUTABLES_SECTION):
        exepaths = dict(config[EXECUTABLES_SECTION])
else:
    g.es(f"Can't find {inifile} so VR3 cannot execute non-Python code")
#@+node:TomP.20191215195433.7: ** vr3.Top-level
#@+node:TomP.20191215195433.8: *3* vr3.decorate_window
def decorate_window(w):
    # Do not override the style sheet!
    # This interferes with themes
        # w.setStyleSheet(stickynote_stylesheet)
    g.app.gui.attachLeoIcon(w)
    w.resize(600, 300)
#@+node:TomP.20191215195433.9: *3* vr3.init
def init():
    """Return True if the plugin has loaded successfully."""
    # global got_docutils
    if g.app.gui.guiName() != 'qt':
        return False  # #1248.
    # if g.app.gui.guiName()
    if not QtWidgets or not g.app.gui.guiName().startswith('qt'):
        if (not g.unitTesting\
            and not g.app.batchMode\
            and g.app.gui.guiName() in ('browser', 'curses')  # EKR.
           ):
            g.es_print('viewrendered3 requires Qt')
        return False
    if not has_webengineview:
        g.es_print('viewrendered3.py requires PyQtWebEngine')
        g.es_print('pip install PyQtWebEngine')
        return False
    if not got_docutils:
        g.es_print('Warning: viewrendered3.py running without docutils.')
    # Always enable this plugin, even if imports fail.
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    g.registerHandler('close-frame', onClose)
    g.registerHandler('scrolledMessage', show_scrolled_message)
    return True
#@+node:TomP.20191215195433.10: *3* vr3.isVisible
def isVisible():
    """Return True if the VR3 pane is visible."""
    return
#@+node:TomP.20191215195433.11: *3* vr3.onCreate
def onCreate(tag, keys):
    c = keys.get('c')
    if not c:
        return
    provider = ViewRenderedProvider3(c)
    free_layout.register_provider(c, provider)

#@+node:TomP.20191215195433.12: *3* vr3.onClose
def onClose(tag, keys):
    c = keys.get('c')
    h = c.hash()
    vr3 = controllers.get(h)
    if vr3:
        c.bodyWantsFocus()
        del controllers[h]
        vr3.deactivate()
        vr3.deleteLater()
#@+node:TomP.20191215195433.13: *3* vr3.show_scrolled_message
def show_scrolled_message(tag, kw):
    """Show "scrolled message" in VR3.
    
    If not already open, open in last opened position,
    or in splitter if none.
    """
    if g.unitTesting:
        return None  # This just slows the unit tests.

    c = kw.get('c')
    flags = kw.get('flags') or 'rst'
    h = c.hash()
    vr3 = controllers.get(h, None)
    if not vr3:
        if positions.get(h, None) == None or OPENED_IN_SPLITTER:
            vr3 = viewrendered(event=kw)
        else:
            vr3 = viewrendered_tab(event=kw)

    title = kw.get('short_title', '').strip()
    vr3.setWindowTitle(title)
    s = '\n'.join([
        title,
        '=' * len(title),
        '',
        kw.get('msg')
    ])

    vr3.update(
        tag='show-scrolled-message',
        keywords={'c': c, 'force': True, 's': s, 'flags': flags},
    )
    return True
#@+node:TomP.20191215195433.14: *3* vr3.split_last_sizes
def split_last_sizes(sizes):
    result = [2 * x for x in sizes[:-1]]
    result.append(sizes[-1])
    result.append(sizes[-1])
    return result
#@+node:tom.20230403142205.1: *3* vr3.open_in_tab
def open_in_tab(c, vr3):
    """Open a vr3 instance in a tab in the log pane."""
    log = c.frame.log
    log.createTab(TABNAME, widget=vr3, createText=False)
    log.selectTab(TABNAME)
    positions[c.hash()] = OPENED_IN_TAB
#@+node:tom.20230403143106.1: *3* vr3.close_tab
def close_tab(c, vr3):
    """Close the VR3 tab if it is open.
    
    Does not delete or deactivate the vr3 instance.
    """
    log = c.frame.log
    log.hideTab(TABNAME)
    log.deleteTab(TABNAME)
    h = c.hash()
    positions[h] = OPENED_IN_TAB

#@+node:TomP.20191215195433.15: *3* vr3.getVr3
def getVr3(event):
    """Return the VR3 ViewRenderedController3

    If the controller is not found, a new one
    is created.  Used in various commands.

    ARGUMENT
    event -- an event provided by Leo when the command
             is dispatched.

    RETURNS
    The active ViewRenderedController3 or None.
    """
    global controllers
    if g.app.gui.guiName() != 'qt':
        return None
    c = event.get('c')
    if not c:
        return None
    h = c.hash()
    vr3 = controllers.get(h) if h else None
    if not vr3:
        controllers[h] = vr3 = viewrendered(event)
    return vr3
#@+node:TomP.20191215195433.16: ** vr3.Commands
#@+node:TomP.20191215195433.18: *3* g.command('vr3')
@g.command('vr3')
def viewrendered(event):
    """Open render view for commander"""
    global controllers, layouts
    if g.app.gui.guiName() != 'qt':
        return None
    c = event.get('c')
    if not c:
        return None
    h = c.hash()
    vr3 = controllers.get(h)
    if not vr3:
        controllers[h] = vr3 = ViewRenderedController3(c)

    layouts[h] = c.db.get(VR3_DEF_LAYOUT, (None, None))
    vr3._ns_id = VR3_NS_ID  # for free_layout load/save
    vr3.splitter = splitter = c.free_layout.get_top_splitter()

    if splitter:
        vr3.store_layout('closed')
        sizes = split_last_sizes(splitter.sizes())
        ok = splitter.add_adjacent(vr3, '_leo_pane:bodyFrame', 'right-of')
        if not ok:
            splitter.insert(0, vr3)
        elif splitter.orientation() == Orientation.Horizontal:
            splitter.setSizes(sizes)
        vr3.adjust_layout('open')
        positions[c.hash()] = OPENED_IN_SPLITTER

    c.bodyWantsFocusNow()

    return vr3
#@+node:tom.20230403141635.1: *3* g.command('vr3-tab')
@g.command('vr3-tab')
def viewrendered_tab(event):
    """Open render view for commander"""
    # global controllers
    if g.app.gui.guiName() != 'qt':
        return None
    c = event.get('c')
    if not c:
        return None
    h = c.hash()
    vr3 = controllers.get(h)
    if not vr3:
        controllers[h] = vr3 = ViewRenderedController3(c)

    open_in_tab(c, vr3)
    return vr3
#@+node:tom.20220824141850.1: *3* g.command('vr3-freeze')
@g.command('vr3-freeze')
def freeze_rendering_pane(event):
    """Freeze the rendering pane so it does not update."""
    vr3 = getVr3(event)
    if not vr3: return
    vr3.set_freeze()
#@+node:tom.20220824142721.1: *3* g.command('vr3-unfreeze')
@g.command('vr3-unfreeze')
def unfreeze_rendering_pane(event):
    """Allow the rendering pane to update."""
    vr3 = getVr3(event)
    if not vr3: return

    vr3.set_unfreeze()
#@+node:TomP.20191215195433.21: *3* g.command('vr3-hide')
@g.command('vr3-hide')
def hide_rendering_pane(event):
    """Close the rendering pane."""
    global controllers, layouts
    if g.app.gui.guiName() != 'qt':
        return

    c = event.get('c')
    if not c:
        return

    vr3 = getVr3(event)
    if not vr3: return

    if vr3.pyplot_active:
        g.es_print('can not close vr3 pane after using pyplot')
        return

    pos = positions[c.hash()]
    if pos == OPENED_IN_SPLITTER:
        vr3.store_layout('open')
    elif pos == OPENED_IN_TAB:
        close_tab(c, vr3)

    def at_idle(c=c, _vr3=vr3):
        c = event.get('c')
        _vr3.adjust_layout('closed')
        c.bodyWantsFocusNow()

    vr3.deactivate()
    vr3.deleteLater()
    del controllers[c.hash()]

    QtCore.QTimer.singleShot(0, at_idle)
    c.bodyWantsFocus()
# Compatibility

close_rendering_pane = hide_rendering_pane
#@+node:TomP.20191215195433.22: *3* g.command('vr3-lock')
@g.command('vr3-lock')
def lock_rendering_pane(event):
    """Lock the rendering pane to the current node."""
    vr3 = getVr3(event)
    if not vr3: return

    vr3.lock()
#@+node:TomP.20191215195433.23: *3* g.command('vr3-pause-play')
@g.command('vr3-pause-play-movie')
def pause_play_movie(event):
    """Pause or play a movie in the rendering pane."""
    vr3 = getVr3(event)
    if not vr3: return
    vp = vr3.vp
    if not vp:
        return
    _state = vp.state()
    f = vp.pause if _state == 1 else vp.play
    f()

#@+node:TomP.20191215195433.24: *3* g.command('vr3-show')
@g.command('vr3-show')
def show_rendering_pane(event):
    """Show the rendering pane."""
    vr3 = getVr3(event)
    if not vr3: return

    vr3.show_dock_or_pane()
#@+node:TomP.20191215195433.25: *3* g.command('vr3-toggle')
@g.command('vr3-toggle')
def toggle_rendering_pane(event):
    """Toggle the rendering pane.
    
    If a VR3 instance exists for this controller, remove it.
    Otherwise, create it, respecting its position if any from
    the last time it was open.
    """
    # global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return

    h = c.hash()
    vr3 = controllers.get(h, None)

    if not vr3:
        if positions.get(h, None) == None or OPENED_IN_SPLITTER:
            vr3 = viewrendered(event)
        else:
            vr3 = viewrendered_tab(event)
    else:
        # c.doCommandByName('vr3-hide')  # Doesn't work
        # This timer is *required* or vr3 won't open on next toggle
        QtCore.QTimer.singleShot(0, lambda: c.doCommandByName('vr3-hide'))
#@+node:tom.20230403190542.1: *3* g.command('vr3-toggle-tab')
@g.command('vr3-toggle-tab')
def toggle_rendering_pane_tab(event):
    """Toggle the rendering pane.
    
    If a VR3 instance exists for this controller, remove it.
    Otherwise, create it in a tab in the log pane, or in
    the last position it had when previously open.
    """
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return

    h = c.hash()
    vr3 = controllers.get(h, None)

    if not vr3:
        if positions.get(h, None) == None or OPENED_IN_TAB:
            vr3 = viewrendered_tab(event)
        else:
            vr3 = viewrendered(event)
    else:
        # c.doCommandByName('vr3-hide')  # Doesn't work
        # This timer is *required* or vr3 won't open on next toggle
        QtCore.QTimer.singleShot(0, lambda: c.doCommandByName('vr3-hide'))
#@+node:TomP.20191215195433.26: *3* g.command('vr3-unlock')
@g.command('vr3-unlock')
def unlock_rendering_pane(event):
    """Allow rendering pane to witch to current node."""
    vr3 = getVr3(event)
    if not vr3: return

    vr3.unlock()
#@+node:TomP.20191215195433.27: *3* g.command('vr3-update')
@g.command('vr3-update')
def update_rendering_pane(event):
    """Update the rendering pane"""
    vr3 = getVr3(event)
    if not vr3: return

    c = event.get('c')
    _freeze = vr3.freeze
    if vr3.freeze:
        vr3.freeze = False
    vr3.update(tag='view', keywords={'c': c, 'force': True})
    if _freeze:
        vr3.freeze = _freeze
#@+node:TomP.20200112232719.1: *3* g.command('vr3-execute')
@g.command('vr3-execute')
def execute_code(event):
    """Execute code in a RsT or MD node or subtree."""
    vr3 = getVr3(event)
    if not vr3: return

    c = event.get('c')
    vr3.execute_flag = True
    vr3.update(tag='view', keywords={'c': c, 'force': True})
#@+node:TomP.20191215195433.29: *3* g.command('vr3-export-rst-html')
@g.command('vr3-export-rst-html')
def export_rst_html(event):
    """Export rendering to system browser."""
    vr3 = getVr3(event)
    if not vr3:
        return
    try:
        _html = vr3.rst_html
    except NameError as e:
        g.es(f'=== {type(e)}: {e}')
        return
    if not _html:
        return

    _html = g.toUnicode(_html)
    # Write to temp file
    c = vr3.c
    path = c.getNodePath(c.rootPosition())
    pathname = g.finalize_join(path, VR3_TEMP_FILE)
    with ioOpen(pathname, 'w', encoding='utf-8') as f:
        f.write(_html)
    webbrowser.open_new_tab(pathname)
#@+node:TomP.20200113230428.1: *3* g.command('vr3-lock-unlock-tree')
@g.command('vr3-lock-unlock-tree')
def lock_unlock_tree(event):
    """Toggle between lock(), unlock()."""
    vr3 = getVr3(event)
    if not vr3: return

    if vr3.lock_to_tree:
        vr3.unlock()
    else:
        vr3.lock()
#@+node:TomP.20200923123015.1: *3* g.command('vr3-use-default-layout')
@g.command('vr3-use-default-layout')
def open_with_layout(event):
    vr3 = getVr3(event)
    c = vr3.c
    layout = {'orientation': 1,
              'content': [{'orientation': 2,
                              'content': ['_leo_pane:outlineFrame', '_leo_pane:logFrame'],
                              'sizes': [200, 200]
                              },
                           '_leo_pane:bodyFrame', VR3_NS_ID
                         ],
              'sizes': [200, 200, 200]
             }

    vr3.splitter = c.free_layout.get_top_splitter()
    if vr3.splitter:
        # Make it work with old and new layout code
        try:
            vr3.splitter.load_layout(layout)
        except TypeError:
            vr3.splitter.load_layout(c, layout)
    else:
        g.es('=== No splitter')
    c.doCommandByName('vr3-update')
    c.bodyWantsFocusNow()

#@+node:TomP.20201003182436.1: *3* g.command('vr3-zoom-view')
@g.command('vr3-zoom-view')
def zoom_view(event):
    vr3 = getVr3(event)
    vr3.zoomView()
#@+node:TomP.20201003182453.1: *3* g.command('vr3-shrink-view')
@g.command('vr3-shrink-view')
def shrink_view(event):
    vr3 = getVr3(event)
    vr3.shrinkView()
#@+node:tom.20210620170624.1: *3* g.command('vr3-open-markup-in-editor')
@g.command('vr3-open-markup-in-editor')
def markup_to_editor(event):
    """Send VR3's markup to an external editor.

    This is to make it easier to understand the markup, in case it
    isn't what was expected.  There is currently no way to
    write the text back from the editor into VR3.
    """
    vr3 = getVr3(event)
    editor_from_settings = vr3.external_editor
    if editor_from_settings.lower() == 'none':  # weird but has happened
        editor_from_settings = ''
    editor = editor_from_settings or g.guessExternalEditor(event.get('c'))

    if not editor:
        g.es('No external editor defined', color='red')
        return

    with open('vr3_last_markup.txt', 'w', encoding=ENCODING) as f:
        f.write(vr3.last_markup)

    cmd = [editor, 'vr3_last_markup.txt']
    # pylint: disable = consider-using-with
    subprocess.Popen(cmd)

#@+node:tom.20211103011049.1: *3* g.command('vr3-plot-2d')
@g.command('vr3-plot-2d')
def vr3_plot_2d(event):
    #@+<< vr3-plot-2d docstring >>
    #@+node:tom.20211104105903.2: *4* << vr3-plot-2d docstring >>
    #@@language rest
    r"""
    Show a plot of x-y data in the selected node.

    The data can be either a one-column or two-column list
    of rows.  Columns are separated by whitespace.  Optionally,
    the node may contain a config file-like set of sections
    that define the labels, and plot styling.

    Optionally, the data can be read from a file instead of taken
    from the selected node.

    The matplotlib package is required for plotting.

    Data Format
    ------------
    Data must be in one or two columns separated by whitespace  Here
    is an example of two-column data::

        1 1
        2 2
        3 4
        # comment
        ; comment

        4 16
        5 32

    Comment lines start with one of ";", "#". Comment, non-numeric, and
    blank lines are ignored.

    Here is an example of one-column data - the missing first column will
    assigned integers starting with 0::

        1
        .5
        6
        # comment
        ; comment

        16
        32

    Whether the data contains one or two columns is determined
    from the first non-comment, non-blank, all numeric row.
    If one-column, an implicit first column is added starting
    with zero.


    Configuration Sections
    -----------------------
    The labeling, styling, and data source for the plot can be
    specified in configuration sections.  Each section starts with
    a *[name]*, has zero or more lines in the form *key = value*,
    and must end with a blank line or the end of the node.

    Sections may be placed anywhere in the selected node.  The
    *[sectionname]* must be left-justified.  Currently the
    following sections are recognized::

        [style]
        [labels]
        [source]

    Optional Data Source
    ---------------------
    Data to be plotted can be read from a file.  The selected node must
    contain a section *[source]* with a *file* key, like this::

        [source]
        file = c:\example\datafile.txt

    If the file exists, it will be used as the data source instead of the
    selected Leo node.  All configuration sections in the selected nodes
    will still take effect.

    Graph And Data Labels
    ----------------------

    A figure title and axis labels can optionally be added. These are
    specified by the configuration section *[labels]*.

    Here is an example::

        [labels]
        title = Plot Example
        xaxis = Days
        yaxis = Values

    Any or all of the entries may be omitted.

    Plot Styling
    -------------

    The appearance of the plot can optionally be changed in several
    ways. By default, a certain Matplotlib style file will be used if
    present (see below), or default Matplotlib styling will be
    applied. If the data node has a section *[style]*, one of two
    styling methods can be used:

    1. A named style. Matplotlib has a number of named
       styles, such as *ggplot*. One of these built-in
       style names can be specified by the *stylename*
       key. The style *xkcd* can also be used even
       though it is not one of the named styles.

    2. A Matplotlib style file. The name of this file
       is specified by the *stylefile* key. The file
       can be located Leo's home directory, typically
       *~/.leo* or its equivalent in Windows.

    Here is an example *[data]* section, with explanatory comments added::

        [style]
        # For VR3 "Plot 2D", only one of these
        # will be used. "stylename" has priority
        # over "stylefile".
        stylename = ggplot
        # stylefile = styles.mpl

    The section may be placed anywhere in the node.

    The Default Style File
    ----------------------

    When no *[data]* section is present, a style file named
    *local_mplstyle* will be used if found. It will first be looked
    for in Leo's home directory, and then in the *site.userbase()*
    directory. On Windows, this is usually the *%APPDATA%\\Python*
    directory. On Linux, this is usually *~/.local*.

    When no style file can be found, Matplotlib will use its default
    styling, as modified by a *matplotlibrc* file if Matplotlib can
    find one.
    """
    #@-<< vr3-plot-2d docstring >>
    vr3 = getVr3(event)
    vr3.plot_2d()
#@+node:tom.20211103161929.1: *3* g.command('vr3-help-plot-2d')
@g.command('vr3-help-plot-2d')
def vr3_help_for_plot_2d(event):
    vr3 = getVr3(event)
    c = vr3.c

    doc_ = vr3.plot_2d.__doc__
    doclines = doc_.split('\n')
    doclines = [line for line in doclines
                if not line.lstrip().startswith('#@')]
    doc = '\n'.join(doclines)
    docstr = cleandoc(doc)
    docstr = ('Help For VR3 Plot 2D\n'
              '=====================\n'
              + docstr)

    args = {'output_encoding': 'utf-8'}
    if vr3.rst_stylesheet and os.path.exists(vr3.rst_stylesheet):
        args['stylesheet_path'] = f'{vr3.rst_stylesheet}'
        args['embed_stylesheet'] = True
        args['report_level'] = RST_NO_WARNINGS

    try:
        _html = publish_string(docstr, writer_name='html', settings_overrides=args)
        _html = _html.decode(ENCODING)
    except SystemMessage as sm:
        msg = sm.args[0]
        if 'SEVERE' in msg or 'FATAL' in msg:
            output = f'<pre style="{RST_ERROR_MSG_STYLE}">RST error: {msg}\n</pre><b><b>'
            output += f'<pre style="{RST_ERROR_BODY_STYLE}">{docstr}</pre>'

    path = c.getNodePath(c.rootPosition())
    pathname = g.finalize_join(path, VR3_TEMP_FILE)
    with ioOpen(pathname, 'w', encoding='utf-8') as f:
        f.write(_html)
    webbrowser.open_new_tab(pathname)
#@+node:tom.20220225110149.1: *3* g.command('vr3-render-html-from-clip')
@g.command('vr3-render-html-from-clip')
def vr3_render_html_from_clip(event):
    """Render HTML string from clipboard.

    The html is available for export until the current selected
    node is reloaded.
    """
    vr3 = getVr3(event)
    clip_str = g.app.gui.getTextFromClipboard()
    vr3.rst_html = clip_str  # So we can be exported to system browser.

    # For some reason, the update below doesn't take effect if vr3 was
    # not previously open.  The getVr3() call opens it and
    # renders the current node, but then the update does
    # not happen.
    vr3.update_html(clip_str, {})


#@+node:ekr.20200918085543.1: ** class ViewRenderedProvider3
class ViewRenderedProvider3:
    #@+others
    #@+node:ekr.20200918085543.2: *3* vr3.__init__
    def __init__(self, c):
        self.c = c
        # Careful: we may be unit testing.
        self.vr3_instance = None
        if hasattr(c, 'free_layout'):
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.register_provider(self)
    #@+node:ekr.20200918085543.3: *3* vr3.ns_provide
    def ns_provide(self, id_):
        global controllers, layouts
        # #1678: duplicates in Open Window list
        if id_ == self.ns_provider_id():
            c = self.c
            h = c.hash()
            vr3 = controllers.get(h) or ViewRenderedController3(c)
            controllers[h] = vr3
            if not layouts.get(h):
                layouts[h] = c.db.get(VR3_DEF_LAYOUT, (None, None))
            return vr3
        return None
    #@+node:ekr.20200918085543.4: *3* vr3.ns_provider_id
    def ns_provider_id(self):
        return VR3_NS_ID
    #@+node:ekr.20200918085543.5: *3* vr3.ns_provides
    def ns_provides(self):
        # #1671: Better Window names.
        # #1678: duplicates in Open Window list
        return [('Viewrendered 3', self.ns_provider_id())]
    #@+node:ekr.20200918085543.6: *3* vr3.ns_title
    def ns_title(self, id_):
        if id_ != self.ns_provider_id():
            return None
        filename = self.c.shortFileName() or 'Unnamed file'
        return f"Viewrendered 3: {filename}"
    #@-others
#@+node:TomP.20191215195433.36: ** class ViewRenderedController3 (QWidget)
class ViewRenderedController3(QtWidgets.QWidget):
    """A class to control rendering in a rendering pane."""
    #@+others
    #@+node:TomP.20200329223820.1: *3* vr3.ctor & helpers
    def __init__(self, c, parent=None):
        """Ctor for ViewRenderedController class."""
        global _in_code_block
        self.c = c
        # Create the widget.
        QtWidgets.QWidget.__init__(self)  # per http://enki-editor.org/2014/08/23/Pyqt_mem_mgmt.html
        # super().__init__(parent)

        self.create_pane(parent)
        # Set the ivars.
        self.active = False
        self.badColors = []
        self.delete_callback = None
        self.gnx = None
        self.graphics_class = QtWidgets.QGraphicsWidget
        self.pyplot_canvas = None

        self.pyplot_imported = False
        self.gs = None  # For @graphics-script: a QGraphicsScene
        self.gv = None  # For @graphics-script: a QGraphicsView
        self.inited = False
        self.length = 0  # The length of previous p.b.
        self.last_text = ''
        self.locked = False

        self.pyplot_active = False
        self.scrollbar_pos_dict = {}  # Keys are vnodes, values are positions.
        self.sizes = []  # Saved splitter sizes.
        self.splitter = None
        self.splitter_index = None  # The index of the rendering pane in the splitter.
        self.title = None

        self.Markdown = None  # MD processor instance
        self.vp = None  # The present video player.
        self.w = None  # The present widget in the rendering pane.

        # For viewrendered3
        self.code_only = False
        self.code_only = False
        self.current_tree_root = None
        self.execute_flag = False
        self.freeze = False
        self.last_markup = ''
        self.lock_to_tree = False
        self.qwev = self.create_base_text_widget()
        self.rst_html = ''
        self.show_whole_tree = False

        # User settings.
        self.reloadSettings()
        self.node_changed = True

        # Init.
        self.create_dispatch_dict()
        self.activate()
        self.zoomed = False

        self.asciidoc3_internal_ok = True
        self.asciidoc_internal_ok = True
        self.using_ext_proc_msg_shown = False


    #@+node:TomP.20200329223820.3: *4* vr3.create_dispatch_dict
    def create_dispatch_dict(self):
        pc = self
        pc.dispatch_dict = {
            'asciidoc': pc.update_asciidoc,
            'big': pc.update_rst,
            'html': pc.update_html,
            'graphics-script': pc.update_graphics_script,
            'image': pc.update_image,
            'jupyter': pc.update_jupyter,
            'md': pc.update_md,
            'movie': pc.update_movie,
            'networkx': pc.update_networkx,
            'plain': pc.update_text,
            'pyplot': pc.update_pyplot,
            'rst': pc.update_rst,
            'svg': pc.update_svg,
            'text': pc.update_text,
            # 'url': pc.update_url,
        }

        pc.dispatch_dict['rest'] = pc.dispatch_dict['rst']
        pc.dispatch_dict['markdown'] = pc.dispatch_dict['md']
    #@+node:TomP.20200329223820.2: *4* vr3.create_base_text_widget
    def create_base_text_widget(self):
        """
        Create a QWebEngineView.
        """
        c = self.c
        w = qwv()
        n = c.config.getInt('qweb-view-font-size')
        if hasattr(w, 'settings'):
            settings = w.settings()
            if n is not None:
                try:
                    settings.setFontSize(settings.DefaultFontSize, n)
                except Exception:
                    pass
            wa = WebEngineAttribute.LocalContentCanAccessRemoteUrls
            settings.setAttribute(wa, True)
        return w
    #@+node:TomP.20200329223820.4: *4* vr3.create_md_header
    def create_md_header(self):
        """Create a header for the md HTML output.

        Check whether or not MathJax output is wanted (self.md_math_output).
        If it is, make sure that the MathJax url or file location is known.

        Then construct an HTML header to be prepended to the MarkDown
        output.

        VARIABLES USED  See reloadSettings() for the settings' names.
        self.md_math_output -- True if MaxJax math display is wanted.
        self.md_stylesheet -- The URL to the stylesheet.  Must include
                               the "file:///" if it is a local file.
        self.md_mathjax_url -- The URL to the MathJax code package.  Must include
                               the "file:///" if it is a local file. The URL
                               should be to a MathJax V3 site.  A typical URL
                               is https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
                               If the MathJax package has been downloaded to the
                               local computer, a typical (Windows) URL would be
                               file:///D:/utility/mathjax/es5/tex-chtml.js
        self.md_header -- where the header string gets stored.
        """

        script_str = ''
        if self.md_math_output and self.mathjax_url:
            script_str = fr'<script defer type="text/javascript" src="{self.mathjax_url}"></script>'
        self.md_header = fr'''
    <!DOCTYPE html>
    <html><head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <link rel="stylesheet" type="text/css" href="{self.md_stylesheet}">
    {script_str}
    </head>
    '''
    #@+node:TomP.20200329223820.5: *4* vr3.create_pane
    def create_pane(self, parent):
        """Create the vr3 pane."""

        if g.unitTesting:
            return
        # Create the inner contents.
        self.setObjectName('viewrendered3_pane')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.create_toolbar()
    #@+node:TomP.20200329223820.6: *4* vr3.create_toolbar & helper functions
    def create_toolbar(self):
        """Create toolbar and attach to the VR3 widget.

        Child widgets can be found using the findChild() method with the
        name of the child widget.  E.g.,

        label = self.findChild(QtWidgets.QLabel, 'vr3-toolbar-label')

        Note that "self" refers to the enclosing viewrendered3 instance.

        NAMES CREATED
        'vr3-toolbar-label' -- the toolbar label.
        """
        # Ref: https://forum.qt.io/topic/52022/solved-how-can-i-add-a-toolbar-for-a-qwidget-not-qmainwindow
        # Ref: https://stackoverflow.com/questions/51459331/pyqt5-how-to-add-actions-menu-in-a-toolbar

        c = self.c
        _toolbar = QtWidgets.QToolBar('Menus')
        _options_button = QtWidgets.QPushButton("View Options")
        _options_button.setDefault(True)
        _toolbar.addWidget(_options_button)

        _default_type_button = QtWidgets.QPushButton("Default Kind")
        _toolbar.addWidget(_default_type_button)

        _other_actions_button = QtWidgets.QPushButton("Other Actions")

        #@+others  # functions.
        #@+node:TomP.20200329223820.7: *5* function: vr3.set_action
        def set_action(label, menu_var_name):
            """Add a QAction to a QT menu.

            ARGUMENTS
            label -- a string containing the display label for the action.
            menu_var_name -- the name of the instance variable that holds this action's
                             isChecked() value.  For example, if the menu_var_name
                             is 'code_only', then a variable self.code_only will be
                             created, and updated if the action's isChecked status
                             is changed.

                             Note that "self" refers to the enclosing viewrendered3 instance.

            RETURNS
            nothing
            """

            setattr(self, menu_var_name, False)
            _action = QAction(label, self, checkable=True)
            _action.triggered.connect(lambda: set_menu_var(menu_var_name, _action))
            menu.addAction(_action)
        #@+node:TomP.20200329223820.8: *5* function: vr3.set_default_kind
        def set_default_kind(kind):
            self.default_kind = kind
            self.c.doCommandByName('vr3-update')
        #@+node:TomP.20200329223820.9: *5* function: vr3.set_freeze
        def set_freeze(checked):
            action = self.action_freeze
            self.freeze = checked
            action.setChecked(checked)
        #@+node:TomP.20200329223820.10: *5* function: vr3.set_group_action
        def set_group_action(label, kind):
            """Coordinates the menu's checked state.

            The triggered function sets the value of the self.default_kind variable.

            ARGUMENTS
            label -- a string containing the display label for the action.
            kind -- the kind of structure to be used by default (e.g., 'rst',
                    'md', 'text')

            RETURNS
            nothing.
            """

            _action = QAction(label, self, checkable=True)
            _action.triggered.connect(lambda: set_default_kind(kind))
            group.addAction(_action)
            menu.addAction(_action)
        #@+node:TomP.20200329223820.11: *5* function: vr3.set_menu_var
        def set_menu_var(menu_var_name, action):
            """Update an QAction's linked variable's value.

            ARGUMENTS
            menu_var_name -- the name of the instance variable that holds this action's
                             isChecked() value.
            action -- the QAction.

            RETURNS
            nothing
            """

            setattr(self, menu_var_name, action.isChecked())
            self.c.doCommandByName('vr3-update')
        #@+node:TomP.20200329223820.12: *5* function: vr3.set_tree_lock
        def set_tree_lock(checked):
            action = self.action_lock_to_tree
            action.setChecked(checked)
            self.lock_to_tree = checked
            self.current_tree_root = self.c.p if checked else None
        #@-others
        #@+<< vr3: create menus >>
        #@+node:TomP.20200329223820.13: *5* << vr3: create menus >>
        menu = QtWidgets.QMenu()
        set_action("Entire Tree", 'show_whole_tree')
        _action = QAction('Lock to Tree Root', self, checkable=True)
        _action.triggered.connect(lambda checked: set_tree_lock(checked))
        menu.addAction(_action)
        self.action_lock_to_tree = _action

        _action = QAction('Freeze', self, checkable=True)
        _action.triggered.connect(lambda checked: set_freeze(checked))
        menu.addAction(_action)
        self.action_freeze = _action

        set_action("Code Only", 'code_only')
        _options_button.setMenu(menu)

        menu = QtWidgets.QMenu()
        group = QActionGroup(self)
        set_group_action('RsT', RST)
        set_group_action('MD', MD)
        set_group_action('Text', TEXT)
        set_group_action('Asciidoc', ASCIIDOC)
        _default_type_button.setMenu(menu)

        menu = QtWidgets.QMenu()
        _action = QAction('Plot 2D', self, checkable=False)
        _action.triggered.connect(lambda: c.doCommandByName('vr3-plot-2d'))
        menu.addAction(_action)

        _action = QAction('Help For Plot 2D', self, checkable=False)
        _action.triggered.connect(lambda: c.doCommandByName('vr3-help-plot-2d'))
        menu.addAction(_action)

        _action = QAction('Reload', self, checkable=False)
        _action.triggered.connect(lambda: c.doCommandByName('vr3-update'))
        menu.addAction(_action)

        _other_actions_button.setMenu(menu)
        #@-<< vr3: create menus >>
        #@+<< vr3: finish toolbar >>
        #@+node:TomP.20200329223820.14: *5* << vr3: finish toolbar >>
        _export_button = QtWidgets.QPushButton("Export")
        _export_button.setDefault(True)
        _export_button.clicked.connect(lambda: c.doCommandByName('vr3-export-rst-html'))
        _toolbar.addWidget(_export_button)

        # _reload_button = QtWidgets.QPushButton("Reload")
        # _reload_button.setDefault(True)
        # _reload_button.clicked.connect(lambda: c.doCommandByName('vr3-update'))
        # _toolbar.addWidget(_reload_button)

        _execute_button = QtWidgets.QPushButton('Execute')
        _execute_button.setDefault(True)
        _execute_button.clicked.connect(lambda: c.doCommandByName('vr3-execute'))
        _toolbar.addWidget(_execute_button)

        _toolbar.addWidget(_other_actions_button)

        self.layout().setMenuBar(_toolbar)
        self.vr3_toolbar = _toolbar

        #@-<< vr3: finish toolbar >>
    #@+node:TomP.20200329223820.15: *4* vr3.reloadSettings
    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.default_kind = c.config.getString('vr3-default-kind') or 'rst'
        self.rst_stylesheet = c.config.getString('vr3-rst-stylesheet') or ''
        self.use_dark_theme = c.config.getBool('vr3-rst-use-dark-theme', RST_USE_DARK)

        self.math_output = c.config.getBool('vr3-math-output', default=False)
        self.mathjax_url = c.config.getString('vr3-mathjax-url') or ''
        self.rst_math_output = 'mathjax ' + self.mathjax_url

        self.use_node_headline = c.config.getBool('vr3-insert-headline-from-node', default=True)

        self.md_math_output = c.config.getBool('vr3-md-math-output', default=False)
        self.md_stylesheet = c.config.getString('vr3-md-stylesheet') or ''
        self.md_style_switch_auto = c.config.getBool('vr3-md-style-auto', default=True)

        self.set_md_stylesheet()
        self.set_rst_stylesheet()
        self.create_md_header()

        if got_markdown:
            ext = ['fenced_code', 'codehilite', 'def_list', 'tables']
            if self.md_math_output:
                ext.append('leo.extensions.mdx_math_gi')
            self.Markdown = markdown.Markdown(extensions=ext)

        self.asciidoc_path = c.config.getString('vr3-asciidoc-path') or ''
        self.prefer_asciidoc3 = c.config.getBool('vr3-prefer-asciidoc3', default=False)
        self.prefer_external = c.config.getString('vr3-prefer-external') or ''
        if self.prefer_external:
            self.asciidoctor = find_exe(self.prefer_external) or None

        self.asciidoc_show_proc_fail_msgs = True
        self.asciidoctor_suppress_footer = c.config.getBool('vr3-asciidoctor-nofooter', default=False)
        self.asciidoctor_icons = c.config.getString('vr3-asciidoctor-icons') or ''
        self.asciidoctor_imagesdir = c.config.getString('vr3-asciidoctor-imagesdir') or ''
        self.asciidoctor_diagram = asciidoc_has_diagram and \
                                       c.config.getBool('vr3-asciidoctor-diagram', default=False)

        self.external_editor = c.config.getString('vr3-ext-editor') or ''

        self.DEBUG = bool(os.environ.get("VR3_DEBUG", None))
    #@+node:TomP.20200329223820.16: *4* vr3.set_md_stylesheet
    def set_md_stylesheet(self):
        """Set or create css stylesheet for Markdown node.

        Stylesheet files are looked for first in ~/.leo/vr3,
        then in the default location of leo/plugins/viewrendered3,
        if their full path is not given.

        If a stylesheet file is specified by the setting "vr3-md-stylesheet",
        then use this stylesheet if it is found.

        Otherwise, if the setting "vr3-md-style-auto" is True, then attempt to
        use a dark-vs-light theme according to whether the Leo theme
        is marked dark or not.

        Otherwise use the default stylesheet at leo/plugins/viewrendered3.
        If not present, create a default stylesheet and write it to a
        file at that place.


        VARIABLES USED
        self.md_stylesheet -- The URL to the stylesheet.  Need not include
                              the "file:///", and must be an absolute path
                              if it is a local file.

                              Set by @string vr3-md-stylesheet.

        self.md_style_switch_auto -- If True, try to use a dark-vs-light
                                     stylesheet according to the Leo theme
                                     in use.
        """

        #@+others
        #@+node:tom.20211117180937.1: *5* check_paths()
        def check_paths(filename, dir_list):
            """Given a file name, check for its existence in one of
            a sequence of directories.  Return the first full path where
            the file is found, or None.
            """

            for direc in dir_list:
                abs_file = os.path.join(direc, filename)
                if os.path.exists(abs_file):
                    return abs_file
            return None
        #@-others

        # Style file locations
        default_style_dir = os.path.join(g.app.leoDir, 'plugins', 'viewrendered3')
        home_style_dir = os.path.join(g.app.homeDir, '.leo', 'vr3')
        if g.isWindows:
            default_style_dir = default_style_dir.replace('/', '\\')
            home_style_dir = home_style_dir.replace('/', '\\')
        style_dirs = (home_style_dir, default_style_dir)

        style_path = ''

        # If user has specified a stylesheet file, try to use it.
        # Can be absolute path or file name. Can use either path separator.
        if self.md_stylesheet:
            #@+<< fix path separators >>
            #@+node:tom.20211117161459.1: *5* << fix path separators >>
            # Fix up path
            # Defensive programming; only the first form should be needed
            # but check the others just in case:
            expr = ('file:///', 'file://', 'file:/', 'file:')
            stylefile = self.md_stylesheet
            for ex_ in expr:
                if self.md_stylesheet.startswith(ex_):
                    stylefile = self.md_stylesheet.replace(ex_, '')
                    break

            # Make all separators consistent and correct for the OS
            stylefile = str(PurePath(stylefile))
            #@-<< fix path separators >>
            #@+<< check existence >>
            #@+node:tom.20211117161734.1: *5* << check existence >>
            # Check for style file's existence
            style_path = None
            if os.path.isabs(stylefile):
                style_path = stylefile
            else:
                style_path = check_paths(stylefile, style_dirs)
            #@-<< check existence >>
            if style_path:
                self.md_stylesheet = 'file:///' + style_path
                g.es('VR3 Markdown stylesheet:', self.md_stylesheet)
                return

        # See if we should try to use stylesheet for Leo theme's light/dark character
        if self.md_style_switch_auto:
            dict_ = g.app.loadManager.globalSettingsDict
            is_dark = dict_.get_setting('color-theme-is-dark')
            stylefile = MD_STYLESHEET_DARK if is_dark else MD_STYLESHEET_LIGHT
            style_path = check_paths(stylefile, style_dirs)
            if style_path:
                self.md_stylesheet = 'file:///' + style_path
                g.es('VR3 Markdown stylesheet:', self.md_stylesheet)
                return
            g.es("Can't find light/dark style file")

        # If no custom stylesheet specified, use standard one.
        if not self.md_stylesheet:
            # Look for the standard one
            style_path = check_paths(MD_BASE_STYLESHEET_NAME, style_dirs)
            if style_path:
                self.md_stylesheet = 'file:///' + style_path
                g.es('VR3 Markdown stylesheet:', self.md_stylesheet)
                return

            # If there is no stylesheet at the standard location, have Pygments
            # generate a default stylesheet there.
            # Note: "cmdline" is a function imported from pygments
            args = [cmdline.__name__, '-S', 'default', '-f', 'html']
            # pygments cmdline() writes to stdout; we have to redirect it to a file
            g.es('VR3-- creating new MD style sheet')
            style_path = os.path.join(default_style_dir, MD_BASE_STYLESHEET_NAME)
            with ioOpen(style_path, 'w') as out:
                with redirect_stdout(out):
                    cmdline.main(args)
            # Add some fine-tuning css
            with ioOpen(style_path, 'a') as out:
                out.write(MD_STYLESHEET_APPEND)
            self.md_stylesheet = 'file:///' + style_path

        g.es('VR3 Markdown stylesheet:', self.md_stylesheet)


    #@+node:TomP.20200329223820.17: *4* vr3.set_rst_stylesheet
    #@@language python
    def set_rst_stylesheet(self):
        """Set rst stylesheet to default if none specified.

        A file location must start with 'file:///';. If
        a file does not exist for the path, use the default
        stylesheet.

        The default location is in leo/plugins/viewrendered3.

        VARIABLES USED
        self.rst_stylesheet -- The URL to the stylesheet.  Need not include
                               the "file:///" if it is a local file.  If
                               a local file and the path is relative, then
                               the default stylesheet folder will be used.
                               Set by @string vr3-rst-stylesheet.
        leodir -- user's .leo directory
        """

        # Default location
        # NOTE - for the stylesheet url we need to use forward slashes no matter
        # what OS is being used.  Apparently, the g.os_path methods do this.
        vr_style_dir = g.os_path_join(LEO_PLUGINS_DIR, 'viewrendered3')

        # Stylesheet may already be specified by @setting vr3-rst-stylesheet.
        # If so, check if it exists.
        use_default = not self.rst_stylesheet
        if not use_default:
            if self.rst_stylesheet.startswith('file:///'):
                # Note that docutils must *not* have a leading 'file:///'
                pth = self.rst_stylesheet.split('file:///')[1]
            else:
                pth = self.rst_stylesheet
            is_abs = PurePath.is_absolute(PurePath(pth))

            if is_abs:
                # This method changes '\' to '/' in the path if needed.
                self.rst_stylesheet = g.finalize_join(pth)
            else:
                self.rst_stylesheet = g.os_path_join(leodir, VR3_DIR, self.rst_stylesheet)
                self.rst_stylesheet = g.finalize_join(self.rst_stylesheet)

            if not os.path.exists(self.rst_stylesheet):
                use_default = True
                g.es(f'Specified VR3 stylesheet not found at {self.rst_stylesheet}')
                g.es('using default')

        if use_default:
            leo_theme_path = g.app.loadManager.computeThemeFilePath()
            leo_theme_name = g.os_path_basename(leo_theme_path)
            use_dark_theme = self.use_dark_theme or 'dark' in leo_theme_name \
                                or leo_theme_name == LEO_THEME_NAME
            if use_dark_theme:
                stylesheet = RST_DEFAULT_DARK_STYLESHEET
            else:
                stylesheet = RST_DEFAULT_STYLESHEET_NAME
            self.rst_stylesheet = g.os_path_join(vr_style_dir, stylesheet)
        g.es('VR3 RsT stylesheet:', self.rst_stylesheet)
    #@+node:tom.20210621132824.1: *4* vr3.dbg_print
    def dbg_print(self, *args):
        if self.DEBUG:
            g.es(*args)
    #@+node:tom.20211104105903.1: *4* vr3.plot_2d
    def plot_2d(self):
        if not matplotlib:
            g.es('VR3 -- Matplotlib is needed to plot 2D data')
            return

        page = self.c.p.b
        page_lines = page.split('\n')
        data_lines = []

        #@+others
        #@+node:tom.20211104105903.5: *5* declarations
        ENCODING = 'utf-8'
        STYLEFILE = 'local_mplstyle'  # Must be in site.getuserbase()
        SECTION_RE = re.compile(r'^\[([a-zA-Z0-9]+)\]')
        #@+node:tom.20211104105903.6: *5* functions
        #@+node:tom.20211104105903.7: *6* has_config_section()
        def has_config_section(pagelines):
            """Find config-like sections in the data page.

            Sections are defined by:
                1. A left-justified term in [brackets].
                2. A blank line or the end of the list of lines.

            ARGUMENT
            pagelines -- a list of text lines.

            RETURNS
            a dictionary keyed by section label: {label: line_num, ...}
            """
            sections = {}
            for i, line in enumerate(pagelines):
                if m := SECTION_RE.match(line):
                    sections[m[1]] = i
            return sections
        #@+node:tom.20211104105903.8: *6* set custom_style()
        #@@pagewidth 65
        def set_custom_style():
            r"""Apply custom matplotlib styles from a file.

            The style file has the name given by STYLEFILE. The .leo
            directory (usually ~/.leo) will be checked first for the
            style file.

            If not found, the site.getuserbase() directory will be
            checked for the style file. On Windows, this is usually the
            %APPDATA%\Python directory. On Linux, this is usually at
            /home/tom/.local.

            """
            found_styles = False
            lm = g.app.loadManager
            style_dir = lm.computeHomeLeoDir()
            if g.isWindows:
                style_dir = style_dir.replace('/', '\\')
            style_file = os.path.join(style_dir, STYLEFILE)
            if os.path.exists(style_file):
                plt.style.use(style_file)
                found_styles = True
            else:
                style_dir = site.getuserbase()
                style_file = os.path.join(style_dir, STYLEFILE)
                if os.path.exists(style_file):
                    plt.style.use(style_file)
                    found_styles = True

            if not found_styles:
                g.es(f'Pyplot style file "{style_file}" not found, using default styles')
        #@+node:tom.20211104105903.12: *6* plot_plain_data()
        def plot_plain_data(pagelines):
            """Plot 1- or 2- column data.  Ignore all non-numeric lines."""


            # from leo.plugins import viewrendered3 as vr3
            # from leo.plugins import viewrendered as vr

            # Helper functions
            #@+<< is_numeric >>
            #@+node:tom.20211104105903.13: *7* << is_numeric >>
            def is_numeric(line):
                """Test if first or 1st and 2nd cols are numeric"""
                fields = line.split()
                numfields = len(fields)
                fields = line.split()
                numfields = len(fields)

                numeric = False
                try:
                    _ = float(fields[0])
                    if numfields > 1:
                        _ = float(fields[1])
                    numeric = True
                except ValueError:
                    pass

                return numeric
            #@-<< is_numeric >>
            #@+<< get_data >>
            #@+node:tom.20211104105903.14: *7* << get_data >>
            def get_data(pagelines):
                num_cols = 0

                # Skip lines starting with """ or '''
                lines = [line.replace('"""', '') for line in pagelines]
                lines = [line.replace("'''", '') for line in lines]

                # Skip blank lines
                lines = [line for line in lines if line.strip()]

                # skip non-data lines (first or 2nd col is not a number)
                t = []
                for line in lines:
                    line = line.replace(',', '')  # remove formatting commas
                    if is_numeric(line):
                        t.append(line.strip())
                        # Check if first all-numeric row has one or more fields
                        if not num_cols:
                            num_cols = min(len(t[0].split()), 2)
                if not t:
                    return None, None

                # Extract x, y values into separate lists; ignore columns after col. 2
                if num_cols == 1:
                    x = range(len(t))
                    y = [float(b.strip()) for b in t]
                else:
                    xy = [line.split()[:2] for line in t]
                    xs, ys = zip(*xy)
                    x = [float(a) for a in xs]
                    y = [float(b) for b in ys]

                return x, y
            #@-<< get_data >>

            x, y = get_data(pagelines)
            if not x:
                g.es('VR3 -- cannot find data')
                return

            plt.plot(x, y)
            plt.show()


            # try:
                # plot2d(page)
            # except Exception as e:
                # g.es('VR3:', e)
        #@+node:tom.20211104155447.1: *6* set_user_style()
        #@@pagewidth 65
        def set_user_style(style_config_lines):
            """Set special plot styles.

            If the data node has a section [style], then if there is a
            key "stylename", apply that named style; otherwise if there
            is a key "stylefile", look for a file of that name ins the
            user's Leo home directory (usually ~/.leo) and use those
            styles.

            The stylename must be one of the built-in style names, such
            as "ggplot". "xkcd" also works even though it is not actually
            one of the style names.

            ARGUMENT style_config_lines -- a sequence of lines starting
            at the [style] section of the data node.

            RETURNS
            True if a style was set.
            """
            set_style = False
            for line in style_config_lines:
                if not line.strip:
                    break
                fields = line.split('=')
                if len(fields) < 2:
                    continue
                kind, val = fields[0].strip(), fields[1].strip()
                if kind == 'stylename':
                    if val == 'xkcd':
                        plt.xkcd()
                    else:
                        plt.style.use(val)
                    set_style = True
                    break
            if not set_style:
                for line in style_config_lines:
                    if not line.strip:
                        break
                    fields = line.split('=')
                    if len(fields) < 2:
                        continue
                    kind, val = fields[0].strip(), fields[1].strip()

                    if kind == 'stylefile':
                        lm = g.app.loadManager
                        style_dir = lm.computeHomeLeoDir()
                        if g.isWindows:
                            style_dir = style_dir.replace('/', '\\')
                        style_file = os.path.join(style_dir, val)
                        if os.path.exists(style_file):
                            plt.style.use(style_file)
                            set_style = True
                        break

            return set_style
        #@-others

        config_sections = has_config_section(page_lines)
        source_start = config_sections.get('source', -1)
        if source_start > 0:
            #@+<< set_data >>
            #@+node:tom.20211106174814.1: *5* << set_data >>
            for line in page_lines[source_start:]:
                if not line.strip:
                    break
                fields = line.split('=')
                if len(fields) < 2:
                    continue
                kind, val = fields[0].strip(), fields[1].strip()
                if kind == 'file':
                    _, filename = fields[0].strip(), fields[1].strip()
                    g.es(filename)
                    if os.path.exists(filename):
                        with open(filename, encoding=ENCODING) as f:
                            data_lines = f.readlines()
                        if not data_lines:
                            g.es(f'VR3 -- no data in file {filename}')
                    else:
                        g.es(f'VR3 -- cannot open data file {filename}')
            #@-<< set_data >>
        else:
            data_lines = page_lines

        if not data_lines:
            return

        style_start = config_sections.get('style', -1)
        if style_start >= 0:
            if not set_user_style(page_lines[style_start:]):
                set_custom_style()
        else:
            set_custom_style()

        plt.ion()
        fig, ax = plt.subplots()
        fig.clear()

        label_start = config_sections.get('labels', -1)
        if label_start >= 0:
            #@+<< configure labels >>
            #@+node:tom.20211104105903.11: *5* << configure labels >>
            # Get lines for the labels section
            for line in page_lines[label_start:]:
                if not line.strip:
                    break
                fields = line.split('=')
                if len(fields) < 2:
                    continue
                kind, val = fields[0].strip(), fields[1].strip()
                if kind == 'title':
                    plt.title(val)
                elif kind == 'xaxis':
                    plt.xlabel(val)
                elif kind == 'yaxis':
                    plt.ylabel(val)

            #@-<< configure labels >>

        plot_plain_data(data_lines)
        plt.rcdefaults()
    #@+node:TomP.20191215195433.49: *3* vr3.update & helpers
    # Must have this signature: called by leoPlugins.callTagHandler.
    def update(self, tag, keywords):
        """Update the vr3 pane. Called at idle time.

        If the VR3 variable "freeze" is True, do not update.
        """
        pc = self
        p = pc.c.p

        if tag in ('show-scrolled-message',):
            # If we are called as a "scrolled message" - usually for display of
            # docstrings.  keywords will contain the RsT to be displayed.
            _kind = keywords.get('flags', 'rst')
            s = keywords.get('s', '')
            f = pc.dispatch_dict.get(_kind)
            f([s,], keywords)

            # Prevent VR3 from showing the selected node at
            # the next idle-time callback,
            # Which would over-write the scrolled message.
            pc.node_changed = False
            pc.gnx = p.v.gnx
            pc.length = len(p.b)  # not s
            pc.last_text = p.b
            return

        if self.freeze: return
        if pc.lock_to_tree:
            _root = pc.current_tree_root or p
        else:
            _root = p

        self.controlling_code_lang = None
        self.params = []

        _kind = pc.get_kind(p) or self.default_kind
        if _kind in ('edit', 'file', 'clean', 'auto'):
            _kind = RST
        if _kind == RST and p.h.startswith('@jupyter'):
            _kind = 'jupyter'
        f = pc.dispatch_dict.get(_kind)
        # if f in (pc.update_rst, pc.update_md, pc.update_text):
            # self.show_toolbar()
        # else:
            # self.hide_toolbar()
        if self.locked:
            return

        if pc.must_update(keywords):
            # Suppress updates until we change nodes.
            pc.node_changed = pc.gnx != p.v.gnx
            pc.gnx = p.v.gnx
            pc.length = len(p.b)  # not s

            # Remove Leo directives.
            s = keywords.get('s') if 's' in keywords else p.b
            s = pc.remove_directives(s)

            # For rst, md, asciidoc handler
            self.rst_html = ''

            # Dispatch based on the computed kind.
            kind = keywords.get('flags') if 'flags' in keywords else _kind
            if not kind:
                h = f'<pre>{s}</pre>'
                w = pc.w
                self.set_html(h, w)
                self.rst_html = h
                w.show()
                return

            _tree = []
            if tag in ('show-scrolled-message',):
                # This branch is for rendering docstrings, help-for-command messages,
                # etc.  Called from qt_gui.py.
                # In case Leo node elements get mixed into the message, remove them:
                pc.node_changed = False
                txt = keywords.get('s', '')
                lines = txt.split('\n')
                keywords['s'] = '\n'.join([l for l in lines if not l.startswith('#@')])
            else:
                # This branch is for rendering nodes and subtrees.
                try:
                    rootcopy = _root.copy()
                    _tree = [rootcopy]
                except UnboundLocalError as e:
                    g.trace('=======', tag, e)
                    return
            if kind in (ASCIIDOC, MD, PLAIN, RST, REST, TEXT) and _tree and self.show_whole_tree:
                _tree.extend(rootcopy.subtree())
            f = pc.dispatch_dict.get(kind)
            if not f:
                g.trace(f'no handler for kind: {kind}')
                f = pc.update_rst
            if kind in (ASCIIDOC, MD, PLAIN, RST, REST, TEXT):
                f(_tree, keywords)
            else:
                f(s, keywords)
        else:
            pass
            # Save the scroll position.
            # w = pc.w
            # if w.__class__ == QtWidgets.QTextBrowser:
                # # 2011/07/30: The widget may no longer exist.
                # try:
                    # sb = w.verticalScrollBar()
                    # pc.scrollbar_pos_dict[p.v] = sb.sliderPosition()
                # except Exception:
                    # g.es_exception()
                    # pc.deactivate()
    #@+node:TomP.20191215195433.51: *4* vr3.embed_widget & helper
    def embed_widget(self, w, delete_callback=None):
        """Embed widget w in the free_layout splitter."""
        pc = self; c = pc.c  #X ; splitter = pc.splitter
        pc.w = w
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeItem(layout.itemAt(0))
        self.layout().addWidget(w)
        # w.show()

        # Special inits for text widgets...
        if w.__class__ == QtWidgets.QTextBrowser:
            text_name = 'body-text-renderer'
            w.setObjectName(text_name)
            # Do not do this! It interferes with themes.
                # pc.setBackgroundColor(pc.background_color, text_name, w)
            w.setReadOnly(True)
            # Create the standard Leo bindings.
            wrapper_name = 'rendering-pane-wrapper'
            wrapper = qt_text.QTextEditWrapper(w, wrapper_name, c)
            w.leo_wrapper = wrapper
            c.k.completeAllBindingsForWidget(wrapper)
            w.setWordWrapMode(WrapMode.WrapAtWordBoundaryOrAnywhere)
    #@+node:TomP.20191215195433.52: *5* vr3.setBackgroundColor
    def setBackgroundColor(self, colorName, name, w):
        """Set the background color of the vr3 pane."""

        return
        # Do not do this! It interferes with themes.
        # pc = self
        # if not colorName: return
        # styleSheet = 'QTextEdit#%s { background-color: %s; }' % (name, colorName)
        # if QtGui.QColor(colorName).isValid():
            # w.setStyleSheet(styleSheet)
        # elif colorName not in pc.badColors:
            # pc.badColors.append(colorName)
            # g.warning('invalid body background color: %s' % (colorName))
    #@+node:TomP.20191215195433.53: *4* vr3.must_update
    def must_update(self, keywords):
        """Return True if we must update the rendering pane."""
        _must_update = False
        pc = self
        c, p = pc.c, pc.c.p

        if g.unitTesting:
            _must_update = False
        elif keywords.get('force'):
            pc.active = True
            _must_update = True
        elif c != keywords.get('c') or not pc.active:
            _must_update = False
        elif pc.locked:
            _must_update = False
        elif pc.gnx != p.v.gnx:
            _must_update = True
        elif len(p.b) != pc.length or pc.last_text != p.b:
            if pc.get_kind(p) in ('html', 'pyplot'):
                _must_update = False  # Only update explicitly.
            else:
                _must_update = True
            pc.length = len(p.b)
            pc.last_text = p.b
        else:
            _must_update = False
            # This trace would be called at idle time.
            # g.trace('no change')

        if _must_update and self.w:
            # Hide the old widget so it won't keep us from seeing the new one.
            self.w.hide()

        return _must_update

    #@+node:TomP.20191215195433.54: *4* vr3.update_asciidoc & helpers
    def update_asciidoc(self, node_list, keywords):
        """Update asciidoc in the vr3 pane."""

        pc = self
        # Do this regardless of whether we show the widget or not.
        w = pc.ensure_web_widget()
        assert pc.w
        pc.show()
        self.rst_html = ''

        ascdoc = self.process_asciidoc_nodes(node_list)
        self.last_markup = ascdoc
        h = self.convert_to_asciidoc(ascdoc) or "No return from asciidoc processor"
        h = g.toUnicode(h)  # EKR.
        self.set_html(h, w)
    #@+node:TomP.20200825083904.1: *5* vr3.process_asciidoc_nodes
    def process_asciidoc_nodes(self, node_list, s=''):
        """Convert content of Leo nodes, or a string, to Asciidoc.

        If the input contains Python code and self.execute_flag is True,
        execute the code and capture stdout and stderr output.
        Return the Asciidoc output with any execution results
        appended in a literal block.

        This method uses a rudimentary state machine.

        ARGUMENTS
        node_list -- a list of Leo nodes to process.
        s -- a string.  The node_list must be empty.

        RETURNS
        a string containing the Asciidoc and execution results.
        """

        result = ASCDOC_PYGMENTS_ATTRIBUTE + '\n'
        codelist = []

        sm = StateMachine(self, tag=TEXT, structure=ASCIIDOC, lang=ASCIIDOC)

        if not node_list:
            lines = s.split('\n')
            # Process node's entire body text; handle @language directives
            sproc, codelines = sm.runMachine(lines)
            result += sproc
            sm.reset()
        else:
            for node in node_list:
                # Add node's text as a headline
                s = node.b
                s = self.remove_directives(s)
                # Remove "@" directive from headline, if any
                if self.use_node_headline:
                    header = node.h or ''
                    if header.startswith('@'):
                        fields = header.split()
                        headline = ' '.join(fields[1:]) if len(fields) > 1 else header[1:]
                    else:
                        headline = header
                    headline_str = '== ' + headline
                    s = headline_str + '\n' + s
                lines = s.split('\n')

                # Process node's entire body text; handle @language directives
                sproc, codelines = sm.runMachine(lines)
                result += sproc + '\n'
                sm.reset(sm.tag, sm.lang)
            if codelines:
                codelist.extend(codelines)

        # Execute code blocks; capture and insert execution results.
        # This means anything written to stdout or stderr.
        if self.execute_flag and codelist:
            execution_result, err_result = None, None
            code = '\n'.join(codelist)
            c = self.c
            environment = {'c': c, 'g': g, 'p': c.p}  # EKR: predefine c & p.
            execution_result, err_result = self.exec_code(code, environment)
            execution_result, err_result = execution_result.strip(), err_result.strip()
            self.execute_flag = False

            if execution_result or err_result:
                result += '\n----\n'
                if execution_result:
                    result += f'\n{execution_result}\n'
                if err_result:
                    result += f'{err_result}\n'
                result += '----\n'

        return result
    #@+node:TomP.20200824155122.1: *5* vr3.convert_to_asciidoc
    def convert_to_asciidoc(self, s):
        r"""
        #@+<< convert asciidoc docstring >>
        #@+node:tom.20211122114736.1: *6* << convert asciidoc docstring >>
        Convert a string to html using an asciidoc processor.

        If the settings prefer an external asciidoctor (Ruby) processor,
        use that if it can be found.  Else try to use either asciidoc or
        asciidoc3, if either or both are installed; try asciidoc3 first if
        requested by a setting.

        Asciidoc3 can be a problem on Windows and might not work. If
        so, we fall back on asciidoc.

        If the "use math" setting is present, then tell the processors to
        include a MathJax script in the output.

        We use a customized .conf file with both asciidoc and asciidoc3
        to insert Mathjax scripts into the  output when math output is
        requested.

        Settings used::

               Setting            Instance Variable
            vr3-math-output        self.math_output
            vr3-prefer-external    self.prefer_external
            vr3-prefer-asciidoc3   self.prefer_asciidoc3
            vr3-asciidoc-path      self.asciidoc_path

        ARGUMENT
        s -- the asciidoc string to convert.

        RETURNS
        the html returned by the processor, or an error message.
        #@-<< convert asciidoc docstring >>
        """
        global AsciiDocAPI, AsciiDoc3, API, ad3_file, asciidoc_processors
        h = ''
        if self.asciidoctor:
            h = self.convert_to_asciidoc_external(s)
            self.rst_html = h
            return h

        #@+<< function proc_string >>
        #@+node:tom.20211122104550.1: *6* << function proc_string >>
        def proc_string(proc):
            st = f'{type(proc)}'.lower()
            name = 'asciidoc3' if 'doc3' in st else 'asciidoc'
            return name
        #@-<< function proc_string >>

        # Reuse cached processors if possible
        if not asciidoc_processors:
            asciidoc_processors = []
            #@+<< Find available processors >>
            #@+node:tom.20211122104636.1: *6* << Find available processors >>
            # pylint: disable = undefined-variable
            if asciidoc_ok:
                asciidoc_processors.append(AsciiDocAPI())
            if asciidoc3_ok:
                asciidoc_processors.append(AsciiDoc3API(ad3_file))
            if not asciidoc_processors:
                h = '<h1>No asciidoc processors found</h1>'
                self.rst_html = h
                return h

            #@-<< Find available processors >>
            if not asciidoc_processors:
                h = '<h1>VR3 -- Cannot find an asciidoc processor</h1>'
                self.rst_html = h
                return h

        #@+<< set processor priority >>
        #@+node:tom.20211125140326.1: *6* << set processor priority >>
        if self.prefer_asciidoc3:
            if proc_string(asciidoc_processors[0]) != 'asciidoc3':
                asciidoc_processors.reverse()
        elif proc_string(asciidoc_processors[0]) != 'asciidoc':
            asciidoc_processors.reverse()
        #@-<< set processor priority >>

        infile = StringIO(s)
        outfile = StringIO()
        h = ''
        succeeded = None
        failed = []

        # Path of directory for our own asciidoc config file
        asciidoc_conf_file = os.path.join(LEO_PLUGINS_DIR, 'viewrendered3', ASCIIDOC_CONF_FILENAME)
        if not os.path.exists(asciidoc_conf_file):
            asciidoc_conf_file = ''

        #@+<< try all processors >>
        #@+node:tom.20211122104319.1: *6* << try all processors >>
        for processor in asciidoc_processors:
            proc_name = proc_string(processor)

            user_dir = PurePath(LEO_PLUGINS_DIR) / 'viewrendered3' / proc_name
            conf_file = str(user_dir / ASCIIDOC_CONF_FILENAME)
            stylesdir = asciidoc_dirs[proc_name]['stylesheets']
            scriptsdir = asciidoc_dirs[proc_name]['javascripts']

            processor.attributes['stylesdir'] = stylesdir
            processor.attributes['scriptsdir'] = scriptsdir

            if conf_file not in processor.options.values:
                processor.options.append('--conf-file', conf_file)
            if self.math_output:
                processor.attributes['mathjax'] = True  # Can be anything
            else:
                processor.attributes.pop('mathjax', None)

            h = ''
            bkend = os.path.splitext(conf_file)[0]
            try:
                processor.execute(infile, outfile, backend=bkend)
                h = outfile.getvalue()
                succeeded = proc_name
                break
            except Exception as e:
                failed.append(proc_name)
                h += f'{proc_name} Failed: {e}\n'
        #@-<< try all processors >>
        self.rst_html = h
        #@+<< show fail-succeed processors >>
        #@+node:tom.20211122104420.1: *6* << show fail-succeed processors >>
        if self.asciidoc_show_proc_fail_msgs:
            if failed:
                failed_procs = ','.join([f'{fail}' for fail in failed])
                g.es(f'VR3 -- Asciidoc processing failed trying {failed_procs}')
            if succeeded:
                g.es(f'VR3 -- Asciidoc succeeded using {succeeded}')
            # Reset to True on reload of settings:
            self.asciidoc_show_proc_fail_msgs = False
        #@-<< show fail-succeed processors >>

        if succeeded:
            infile.close()
            outfile.close()
        return h
    #@+node:TomP.20191215195433.56: *5* vr3.convert_to_asciidoc_external
    def convert_to_asciidoc_external(self, s):
        """Convert s to html using the Ruby asciidoctor3 processor."""
        s = self.run_asciidoctor_external(s)
        return g.toUnicode(s)
    #@+node:TomP.20191215195433.57: *6* vr3.run_asciidoctor_external
    def run_asciidoctor_external(self, s):
        """
        Process s with an asciidoctor3 external processor.
        Return the contents of the html file. The caller handles most exceptions.
        """
        c = self.c
        # Find path relative to this file.  Needed as the base of relative
        # URLs, e.g., image or included files.
        path = c.getNodePath(c.p)
        i_path = g.finalize_join(path, 'vr3_adoc.adoc')
        o_path = g.finalize_join(path, 'vr3_adoc.html')

        # Write the input file.
        with open(i_path, 'w', encoding='utf-8') as f:
            f.write(s)

        # Set up special command-line asciidoctor attributes
        attrs = []
        if self.math_output:
            attrs.append('stem')
        if self.asciidoctor_suppress_footer:
            attrs.append('nofooter')
        if self.asciidoctor_icons:  # not ""
            attrs.append(f'icons={self.asciidoctor_icons}')
        if self.asciidoctor_imagesdir:
            attrs.append(f'imagesdir={self.asciidoctor_imagesdir}')
        att_str = ''
        for att in attrs:
            # pylint: disable = consider-using-join
            att_str += f'-a {att} '

        # Call the external program to write the output file.
        command = (f'{self.asciidoctor} -b html5 {att_str} {i_path}')

        # If find asciidoctor-diagram converter config, then use it.
        if self.asciidoctor_diagram:
            command += ' -r asciidoctor-diagram'

        g.execute_shell_commands(command)
        # Read the output file and return it.
        try:
            with open(o_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            message = f'asciidoctor output file not found:\n {e}'
            g.es(message)
            return message

    #@+node:TomP.20191215195433.58: *4* vr3.update_graphics_script
    def update_graphics_script(self, s, keywords):
        """Update the graphics script in the vr3 pane."""
        pc = self; c = pc.c
        force = keywords.get('force')
        if pc.gs and not force:
            return
        if not pc.gs:
            splitter = c.free_layout.get_top_splitter()
            # Careful: we may be unit testing.
            if not splitter:
                g.trace('no splitter')
                return
            # Create the widgets.
            pc.gs = QtWidgets.QGraphicsScene(splitter)
            pc.gv = QtWidgets.QGraphicsView(pc.gs)
            w = pc.gv.viewport()  # A QWidget
            # Embed the widgets.

            def delete_callback():
                for w in (pc.gs, pc.gv):
                    w.deleteLater()
                pc.gs = pc.gv = None

            pc.embed_widget(w, delete_callback=delete_callback)
        c.executeScript(
            script=s,
            namespace={'gs': pc.gs, 'gv': pc.gv})
    #@+node:TomP.20191215195433.59: *4* vr3.update_html
    update_html_count = 0

    def update_html(self, s, keywords):
        """Update html in the vr3 pane."""
        pc = self
        c = pc.c
        if pc.must_change_widget(has_webengineview):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert w == pc.w
        else:
            w = pc.w
        w.hide()  # This forces a proper update.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.60: *4* vr3.update_image
    def update_image(self, s, keywords):
        """Update an image in the vr3 pane.

        The path to the file can be an absolute or relative file path,
        or an http: URL.  It must be the first line in the body.
        File URLs must not start with "file:".
        """

        pc = self
        if not s.strip():
            return
        lines = g.splitLines(s) or []
        fn = lines and lines[0].strip()
        if not fn:
            return

        is_url = False
        if fn.startswith('http'):
            ok = True
            path = fn
            is_url = True
        else:  #file URL
            ok, path = pc.get_fn(fn, '@image')

        if not ok:
            w = pc.ensure_text_widget()
            w.setPlainText(f'@image: file not found: {path}')
            return

        if not is_url:
            path, fname = os.path.split(path)
            path = path.replace('\\', '/') + '/'
        else:
            fname = path
            path = ''

        template = image_template % (fname)
        # Only works in Python 3.x.
        # Sensitive to leading blank lines.
        template = textwrap.dedent(template).strip()

        w = pc.ensure_web_widget()
        pc.set_html(template, w)
        w.show()
    #@+node:TomP.20191215195433.61: *4* vr3.update_jupyter & helper
    update_jupyter_count = 0

    def update_jupyter(self, s, keywords):
        """Update @jupyter node in the vr3 pane."""
        pc = self
        c = pc.c
        if pc.must_change_widget(has_webengineview):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert w == pc.w
        else:
            w = pc.w
        s = self.get_jupyter_source(c)
        self.rst_html = s
        w.hide()  # This forces a proper update.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.62: *5* vr3.get_jupyter_source
    def get_jupyter_source(self, c):
        """Return the html for the @jupyter node."""
        body = c.p.b.lstrip()
        if body.startswith('<'):
            # Assume the body is html.
            return body

        if not jupyter_ok:
            return 'can not render @jupyter nodes: need missing nbformat or nbconvert package'

        if body.startswith('{'):
            # Leo 5.7.1: Allow raw JSON.
            s = body
        else:
            url = ''
            fields = c.p.h.split()
            if len(fields) > 1:
                for f in fields:
                    if '://' in f:
                        url = f
                        break
            if not url:
                if c.p.b:
                    # Try first line of body
                    url = c.p.b.split('\n')[0]
                if not url:
                    return 'No url found'
            try:
                with urlopen(url) as u:
                    s = u.read().decode()
            except Exception:
                return f'url not found: {url}'
        try:
            nb = nbformat.reads(s, as_version=4)
            e = HTMLExporter()
            (s, junk_resources) = e.from_notebook_node(nb)
        except nbformat.reader.NotJSONError:
            pass  # Assume the result is html.
        return s
    #@+node:TomP.20191215195433.63: *4* vr3.update_latex & helper
    def update_latex(self, s, keywords):
        """Update latex in the vr3 pane."""
        pc = self
        c = pc.c
        if sys.platform.startswith('win'):
            g.es_print('latex rendering not ready for Python 3')
            w = pc.ensure_text_widget()
            pc.show()
            w.setPlainText(s)
            c.bodyWantsFocusNow()
            return
        if pc.must_change_widget(has_webengineview):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert w == pc.w
        else:
            w = pc.w
        w.hide()  # This forces a proper update.
        s = self.create_latex_html(s)
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.64: *5* vr3.create_latex_html
    def create_latex_html(self, s):
        """Create an html page embedding the latex code s."""
        html_s = html.escape(s)
        template = latex_template % (html_s)
        template = textwrap.dedent(template).strip()
        return template
    #@+node:TomP.20191215195433.65: *4* vr3.update_md & helpers
    def update_md(self, node_list, keywords):
        """Update markdown text in the vr3 pane.

            ARGUMENTS
            node_list -- a list of outline nodes to be processed.
            keywords -- a dictionary of keywords

            RETURNS
            nothing
        """
        # Do this regardless of whether we show the widget or not.
        self.ensure_web_widget()
        assert self.w
        w = self.w

        if node_list:
            self.show()

        if got_markdown:
            if not node_list:
                return
            if node_list:
                s = node_list[0].b
            else:
                s = keywords.get('s', '')
            s = self.remove_directives(s)
            isHtml = s and s[0] == '<'
            if s.startswith('<svg'):
                g.es(NO_SVG_WIDGET_MSG, color='red')
                return
            self.rst_html = ''
            if s and isHtml:
                h = s
            else:
                h = self.convert_markdown_to_html(node_list)
            if h:
                h = g.toUnicode(h)  # EKR.
                self.set_html(h, w)
                self.rst_html = h
        else:
            # s = node_list[0].b
            w.setHtml('')  # EKR.

    #@+node:TomP.20191215195433.66: *5* convert_markdown_to_html
    def convert_markdown_to_html(self, node_list, s=''):
        """Convert node_list to html using the markdown processor.

        If node_list == [], render the string s.

        RETURNS
        the HTML returned by markdown.
        """

        #@+others
        #@+node:TomP.20200208211132.1: *6* setup
        pc = self
        c, p = pc.c, pc.c.p
        if g.app.gui.guiName() != 'qt':
            return ''  # EKR

        vr3 = controllers.get(c.hash())
        if not vr3:
            vr3 = ViewRenderedController3(c)

        # Update the current path.
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)

        #@+node:TomP.20200208211347.1: *6* process nodes
        result = ''
        codelist = []
        sm = StateMachine(self, TEXT, MD, MD)

        if not node_list:
            lines = s.split('\n')
            # Process node's entire body text; handle @language directives
            sproc, codelines = sm.runMachine(lines)
            result += sproc
            sm.reset()
        else:
            for node in node_list:
                s = node.b
                s = self.remove_directives(s)
                if self.use_node_headline:
                    # Add node's text as a headline
                    # Remove "@" directive from headline, if any
                    header = node.h or ''
                    if header.startswith('@'):
                        fields = header.split()
                        headline = ' '.join(fields[1:]) if len(fields) > 1 else header[1:]
                    else:
                        headline = header
                    headline_str = '## ' + headline.lstrip()
                    s = headline_str + '\n' + s
                lines = s.split('\n')

                # Process node's entire body text; handle @language directives
                sproc, codelines = sm.runMachine(lines)
                result += sproc
                if codelines:
                    codelist.extend(codelines)
                sm.reset()

        # Execute code blocks; capture and insert execution results.
        # This means anything written to stdout or stderr.
        if self.execute_flag and codelist:
            execution_result, err_result = None, None
            code = '\n'.join(codelist)
            c = self.c
            environment = {'c': c, 'g': g, 'p': c.p}  # EKR: predefine c & p.
            execution_result, err_result = self.exec_code(code, environment)
            execution_result, err_result = execution_result.strip(), err_result.strip()
            self.execute_flag = False

            if execution_result or err_result:
                result += '\n```text\n'
                if execution_result:
                    result += f'\n{execution_result}\n'
                if err_result:
                    result += f'{err_result}\n'
                result += '```\n'

        #@+node:TomP.20200209115750.1: *6* generate HTML

        try:
            _html = self.Markdown.reset().convert(result)
            self.last_markup = result

        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                _html = f'MD error:\n{msg}\n\n{s}'

        _html = self.md_header + '\n<body>\n' + _html + '\n</body>\n</html>'
        return _html
        #@-others
    #@+node:TomP.20191215195433.67: *4* vr3.update_movie
    movie_warning = False

    def update_movie(self, s, keywords):
        """Update a movie in the vr3 pane."""
        pc = self
        ok, path = pc.get_fn(s, '@movie')
        if not ok:
            w = pc.ensure_text_widget()
            w.setPlainText(f'Not found: {path}')
            return
        if not phonon and not QtMultimedia:
            if not self.movie_warning:
                self.movie_warning = True
                g.es_print('No phonon and no QtMultimedia modules')
            w = pc.ensure_text_widget()
            w.setPlainText('')
            return
        if pc.vp:
            vp = pc.vp
            pc.vp.stop()
            pc.vp.deleteLater()
        # Create a fresh player.
        g.es_print('playing', path)
        vw = vp.videoWidget()
        vw.setObjectName('video-renderer')
        # Embed the widgets

        def delete_callback():
            if pc.vp:
                pc.vp.stop()
                pc.vp.deleteLater()
                pc.vp = None

        pc.embed_widget(vp, delete_callback=delete_callback)
        pc.show()
        vp = pc.vp
        vp.load(phonon.MediaSource(path))
        vp.play()
    #@+node:TomP.20191215195433.68: *4* vr3.update_networkx
    def update_networkx(self, s, keywords):
        """Update a networkx graphic in the vr3 pane."""
        pc = self
        w = pc.ensure_text_widget()
        w.setPlainText('')  # 'Networkx: len: %s' % (len(s)))
        pc.show()
    #@+node:TomP.20191215195433.69: *4* vr3.update_pandoc & helpers
    def update_pandoc(self, s, keywords):
        """
        Update an @pandoc in the vr3 pane.

        There is no such thing as @language pandoc,
        so only @pandoc nodes trigger this code.
        """
        global pandoc_exec
        pc = self
        w = pc.ensure_text_widget()
        assert pc.w
        if s:
            pc.show()
        if pandoc_exec:
            try:
                self.last_markup = s
                s2 = self.convert_to_pandoc(s)
                self.set_html(s2, w)
            except Exception:
                g.es_exception()
            return
        self.update_rst(s, keywords)
    #@+node:TomP.20191215195433.70: *5* vr3.convert_to_pandoc
    def convert_to_pandoc(self, s):
        """Convert s to html using the asciidoctor or asciidoc processor."""
        pc = self
        c, p = pc.c, pc.c.p
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        if pc.title:
            s = pc.make_pandoc_title(pc.title) + s
            pc.title = None
        s = pc.run_pandoc(s)
        return g.toUnicode(s)
    #@+node:TomP.20191215195433.71: *5* vr3.run_pandoc
    def run_pandoc(self, s):
        """
        Process s with pandoc.
        return the contents of the html file.
        The caller handles all exceptions.
        """
        global pandoc_exec
        assert pandoc_exec, g.callers()
        home = g.os.path.expanduser('~')
        i_path = g.finalize_join(home, 'vr3_input.pandoc')
        o_path = g.finalize_join(home, 'vr3_output.html')
        # Write the input file.
        with open(i_path, 'w', encoding=ENCODING) as f:
            f.write(s)
        # Call pandoc to write the output file.
        # --quiet does no harm.
        command = f"pandoc {i_path} -t html5 -o {o_path}"
        g.execute_shell_commands(command)
        # Read the output file and return it.
        with open(o_path, 'r', encoding=ENCODING) as f:
            return f.read()
    #@+node:TomP.20191215195433.72: *4* vr3.update_pyplot
    def update_pyplot(self, s, keywords):
        """Get the pyplot script at c.p.b and show it."""
        g.es('@pyplot nodes not implemented', color='gray')

        if 0:  # Keep old code here for possible resurrection
            c = self.c
            if not self.pyplot_imported:
                self.pyplot_imported = True
                backend = g.finalize_join(
                    g.app.loadDir, '..', 'plugins', 'pyplot_backend.py')
                if g.os_path_exists(backend):
                    if matplotlib:
                        try:
                            matplotlib.use('module://leo.plugins.pyplot_backend')
                        except ImportError:
                            g.trace('===== FAIL: pyplot.backend')
                else:
                    g.trace('===== MISSING: pyplot.backend')
            try:
                plt.ion()  # Automatically set interactive mode.
                namespace = {
                    'animation': animation,
                    'matplotlib': matplotlib,
                    'numpy': np, 'np': np,
                    'pyplot': plt, 'plt': plt,
                }
            except Exception:
                g.es_print('matplotlib imports failed')
                namespace = {}
            # Embedding already works without this!
                # self.embed_pyplot_widget()
            self.pyplot_imported = True
            # pyplot will throw RuntimeError if we close the pane.
            self.pyplot_active = True
            c.executeScript(
                event=None,
                args=None, p=None,
                script=c.p.b,  #None,
                useSelectedText=False,
                define_g=True,
                define_name='__main__',
                silent=False,
                namespace=namespace,
                raiseFlag=False,
                runPyflakes=False,  # Suppress warnings about pre-defined symbols.
            )
            c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.73: *4* vr3.update_rst & helpers
    #@@language python
    def update_rst(self, node_list, keywords=None):
        """Update rst in the vr3 pane.

            ARGUMENTS
            node_list -- a list of outline nodes to be processed.
            keywords -- a dictionary of keywords

            RETURNS
            nothing
        """
        if not keywords:  # EKR
            keywords = {}
        # Do this regardless of whether we show the widget or not.
        self.ensure_web_widget()
        assert self.w
        w = self.w
        self.show()

        if got_docutils:
            if not node_list or isinstance(node_list[0], str):  # EKR.
                # We were called as a "scrolled message"
                s = node_list[0]
                node_list = None
            else:
                s = node_list[0].b
                s = self.remove_directives(s)
            isHtml = s and s[0] == '<'
    #@+at
    #         # In case we bring back QtSvg again)
    #         if s.startswith('<svg'):
    #             if QtSvg is None:
    #                 g.es(NO_SVG_WIDGET_MSG, color = 'red')
    #                 return
    #             else:
    #                 self.update_svg(s, keywords)
    #@@c
            self.rst_html = ''
            if s and isHtml:
                _code = [n.b for n in node_list]
                h = '\n'.join(_code)
            else:
                h = self.convert_to_html(node_list, s)
            if h:
                self.set_html(h, w)
                self.rst_html = h
        else:
            _text_list = [n.b for n in node_list]
            s = '<pre>' + '\n'.join(_text_list) + r'\</pre>'
            self.set_html(s, w)
    #@+node:TomP.20191215195433.74: *5* vr3.convert_to_html
    #@@language python
    def convert_to_html(self, node_list, s=''):
        """Convert node_list to html using docutils.

        PARAMETERS
        node_list -- a list of Leo nodes to be rendered.  May be empty ([]).
        s -- a string to be rendered if node_list is empty.

        RETURNS
        the html returned by docutils.
        """

        #@+others
        #@+node:TomP.20200105214716.1: *6* vr3.setup
        #@@language python
        c, p = self.c, self.c.p
        if g.app.gui.guiName() != 'qt':
            return ''  # EKR

        vr3 = controllers.get(c.hash())
        if not vr3:
            vr3 = ViewRenderedController3(c)

        # Update the current path.
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        #@+node:TomP.20200105214928.1: *6* vr3.process nodes
        #@@language python
        result = ''
        codelist = []
        if not node_list:
            result, codelines = self.process_rst_node(s)
        else:
            for node in node_list:
                # Add node's text as a headline
                s = node.b
                s = self.remove_directives(s)
                if self.use_node_headline:
                    s = self.make_rst_headline(node, s)

                # Process node's entire body text to handle @language directives
                sproc, codelines = self.process_rst_node(s)
                result += sproc
                if codelines:
                    codelist.extend(codelines)
        #@+node:TomP.20200426183119.1: *6* vr3.execute code blocks
        #@@language python
        # Execute code blocks; capture and insert execution results.
        # This means anything written to stdout or stderr.
        # The paths to known executables are in the exepaths dictionary, which
        # was loaded at startup from data in the VR3_CONFIG_FILE.
        if self.execute_flag and codelist:
            code = '\n'.join(codelist)
            c = self.c
            environment = {'c': c, 'g': g, 'p': c.p}  # EKR: predefine c & p.

            execution_result = err_result = ''

            if self.controlling_code_lang == PYTHON:
                execution_result, err_result = self.exec_code(code, environment)
            # Otherwise check VR3_CONFIG_FILE to see if we know how to run this language
            elif self.controlling_code_lang in exepaths:
                execution_result, err_result = self.ext_execute_code(self.controlling_code_lang, code)
            else:
                err_result = f"Can't execute {self.controlling_code_lang} today."

            # Format execution result
            ex = execution_result.split('\n') if execution_result.strip() else []
            err = err_result.split('\n') if err_result.strip() else []
            ex_indented_lines = [RST_INDENT + li for li in ex]
            err_indented_lines = [RST_INDENT + li for li in err]
            indented_execution_result = '\n'.join(ex_indented_lines)
            indented_err_result = '\n'.join(err_indented_lines)
            self.execute_flag = False

            if indented_execution_result.strip():
                result += f'\n::\n\n{indented_execution_result}\n'
            if indented_err_result.strip():
                result += f'\n::\n\n{indented_err_result}\n'
        #@+node:TomP.20200105214743.1: *6* vr3.get html from docutils
        #@@language python
        args = {'output_encoding': 'utf-8'}
        if self.rst_stylesheet and os.path.exists(self.rst_stylesheet):
            args['stylesheet_path'] = f'{self.rst_stylesheet}'
            args['embed_stylesheet'] = True
            args['report_level'] = RST_NO_WARNINGS

        # Suppress RsT warnings
        # args['report_level'] = 5

        if self.math_output:
            if self.mathjax_url:
                args['math_output'] = self.rst_math_output
            else:
                g.es('VR3 - missing URL for MathJax')

        # Call docutils to get the html rendering.
        _html = ''.encode(ENCODING)
        if result.strip():
            try:
                self.last_markup = result
                _html = publish_string(result, writer_name='html',
                                       settings_overrides=args)
            except SystemMessage as sm:
                msg = sm.args[0]
                if 'SEVERE' in msg or 'FATAL' in msg:
                    output = f'<pre style="{RST_ERROR_MSG_STYLE}">RST error: {msg}\n</pre><b><b>'
                    output += f'<pre style="{RST_ERROR_BODY_STYLE}">{result}</pre>'
                    _html = output.encode(ENCODING)

        self.rst_html = _html
        return _html
        #@-others


    #@+node:TomP.20210218003018.1: *5* execution helpers
    # Helper functions to execute non-python languages.
    #@+others
    #@+node:TomP.20210218232648.1: *6* ext_execute_code
    def ext_execute_code(self, lang, code):
        """Execute code using an external processor.

        The path to the processor will have been stored in
        the exepath dictionary.

        ARGUMENTS
        lang -- a string representing the code language; e.g. 'javascript'.
        code -- a string containing the code to be run.

        RETURNS
        a tuple (result.stdout, result.stderr) with any console output from
        the external processor.
        """
        exepath = exepaths[lang]
        progfile = '_##temp_execute.txt'

        with open(progfile, 'w', encoding=ENCODING) as f:
            f.write(code)

        cmd = [exepath]
        cmd.extend(self.params)
        cmd.append(progfile)

        # We are not checking the return code here, so:
        # pylint: disable=subprocess-run-check
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True, encoding='utf-8')
        return result.stdout, result.stderr
    #@-others
    #@+node:TomP.20200112103934.1: *5* process_rst_node
    #@@language python
    def process_rst_node(self, s):
        """Process the string of a rst node, honoring "@language" code blocks

           Any sections delineated by "@language xxx" /"@language yyy" directives
           are marked as code blocks in RST, where "xxx" is a code name
           (e.g., "python"), and "yyy" is a non-code name (e.g., "rst").
           There can be several changes from code to non-code and back
           within the node.

           Lines that contain only "@" cause all succeeding lines
           to be skipped until the next line that contains only "@c".

           ARGUMENT
           s -- the node's contents as a string

           RETURNS
           a string having the code parts formatted as rst code blocks.
        """
        #@+<< rst special line helpers >>
        #@+node:TomP.20200121121247.1: *6* << rst special line helpers >>
        def get_rst_code_language(line):
            """Return the language and tag for a line beginning with ".. code::"."""
            global _in_code_block
            _fields = line.split('.. code::')
            if len(_fields) > 1:
                _lang = _fields[1].strip()
            else:
                _lang = PYTHON  # Standard RsT default.
            _tag = CODE if _lang in LANGUAGES else TEXT
            _in_code_block = _tag == CODE
            if _tag == CODE and not self.controlling_code_lang:
                self.controlling_code_lang = _lang

            return _lang, _tag

        def indented(line):
            return line[0] in string.whitespace

        def empty_line(line):
            return not line.strip()
        #@-<< rst special line helpers >>
        #@+<< Loop Over Lines >>
        #@+node:TomP.20200112103729.1: *6* << Loop Over Lines >>

        lines = s.split('\n')
        # Break up text into chunks
        results = None
        chunks = []
        _structure = RST
        _lang = RST
        _tag = TEXT

        _at_skip_in_effect = False
        _got_language = False
        _in_rst_block = False
        _in_code_block = False
        _in_quotes = False
        _quotes_type = None
        _in_skipblock = False

        # c = self.c
        # environment = {'c': c, 'g': g, 'p': c.p} # EKR: predefine c & p.

        for i, line in enumerate(lines):
            #@+<< omit at-others >>
            #@+node:TomP.20200909123019.1: *7* << omit at-others >>
            # Omit lines starting with [blank]*line = @others
            left = line.lstrip()
            if left.startswith('@others'):
                continue
            #@-<< omit at-others >>
            #@+<< handle toctree >>
            #@+node:TomP.20200411133219.1: *7* << handle toctree >>
            # Skip all lines in an indented block started by a string in SKIPBLOCKS
            # such as ".. toctree::" or ".. index::"
            # We need to skip all lines in the block until there is a non-blank
            # line that is not indented, or we have reached the last line.
            if not _in_code_block and not _in_skipblock:
                _in_skipblock = any(line.startswith(d) for d in SKIPBLOCKS)
                if _in_skipblock:
                    continue

            if _in_skipblock:
                if empty_line(line):
                    try:
                        next_line = lines[i + 1]
                    except IndexError:  # no more lines
                        continue
                    if not empty_line(next_line) and not indented(next_line):
                        _in_skipblock = False
                        continue
                elif indented(line):
                    continue
            #@-<< handle toctree >>
            #@+<< handle quotes >>
            #@+node:TomP.20200117172607.1: *7* << handle quotes >>
            # Detect if we are starting or ending a multi-line
            # string in a code block.  We need to know
            # to prevent directives within a string from
            # being acted upon.
            # Inside an RsT code block (one that started with .. code::),
            # all lines are indented and therefore cannot
            # contain a directive.

            if _in_code_block and not _in_rst_block:
                _quotes_type = TRIPLEQUOTES if line.find(TRIPLEQUOTES) >= 0 else None
                if not _quotes_type:
                    _quotes_type = TRIPLEAPOS if line.find(TRIPLEAPOS) >= 0 else None
                if _quotes_type:
                    if not _in_quotes:
                        # We are in a quoted section unless we found two quote markers
                        # in the line.
                        _in_quotes = line.count(_quotes_type) == 1
                    else:
                        _in_quotes = False
            #@-<< handle quotes >>
            #@+<< handle_ats >>
            #@+node:TomP.20200112103729.2: *7* << handle_ats >>
            # Honor "@", "@c": skip all lines after "@" until next "@c".
            if line.rstrip() == '@':
                _at_skip_in_effect = True
            elif line.rstrip() == '@c':
                _at_skip_in_effect = False
                continue  # Needed to avoid displaying the "@c"

            if _at_skip_in_effect:
                continue
            #@-<< handle_ats >>
            #@+<< handle at-image >>
            #@+node:TomP.20200416153716.1: *7* << handle at-image >>
            # Handle @image and @param directives.
            # param format: space separated words, stored in self.params
            # as a list of the words.

            if not _in_code_block:
                if line.startswith('@image'):
                    # insert RsT code for image
                    fields = line.split(' ', 1)
                    if len(fields) > 1:
                        url = fields[1]
                        line = f'\n.. image:: {url}\n      :width: 100%\n\n'
                    else:
                        # No url for an image: ignore and skip to next line
                        continue
            else:
                if line.startswith('@param'):
                    # Will add nothing if no params on the line.
                    params = line.split()
                    if len(params) > 1:
                        params = params[1:]
                        self.params.extend(params)
                    continue
            #@-<< handle at-image >>
            #@+<< identify_code_blocks >>
            #@+node:TomP.20200112103729.3: *7* << identify_code_blocks >>
            # Identify code blocks
            # Can start with "@language" or ".. code::"
            _got_language_by_rst_block = line.startswith(RST_CODE_INTRO) and not _in_quotes

            # Somewhat gnarly code here - have to find end of the code block.
            if _got_language_by_rst_block:
                _got_language = True
                _in_rst_block = True
                _in_code_block = True
                _tag, _lang = get_rst_code_language(line)

                # If this is an RsT-delineated code block, then we need to
                # find the end of the block.  These blocks will be indented,
                # and we have to use the initial indentation to un-indent,
                # and to detect the end of the block.  We need to un-indent
                # because CODE chunks assume the lines are not indented.
                _numlines = len(lines)
                if _numlines < i + 2: continue  # Reached the end of the node.

                # Skip mandatory first blank line before indent
                _first_code_line_num = i + 2
                _first_code_line = lines[_first_code_line_num]

                # Figure out the indentation
                _indentation = ''
                for ch in _first_code_line:
                    if ch not in (' ', '\t'): break
                    _indentation += ch

                # Last line of code block must be followed by at least one blank line and
                # then a non-blank, non-indented line, unless we reached the end of the node.
                _last_code_line_num = _first_code_line_num
                if not _last_code_line_num == _numlines - 1:
                    for j in range(_first_code_line_num, _numlines):
                        if lines[j].startswith(_indentation): continue
                        if j == _numlines - 1:
                            _last_code_line_num = j
                        elif lines[j + 1] and lines[j + 1][0] not in (' ', '\t'):
                            _last_code_line_num = j
                            break
            elif line.find('@language') == 0 and not _in_quotes:
                _got_language = True
                # Check if there really is a language named after the '@language' directive
                stripped_line = line.strip()  # #1934.
                _language = line.split()[1] if ' ' in stripped_line else TEXT
                _in_rst_block = False
                _in_code_block = _language in LANGUAGES
                if _in_code_block and not self.controlling_code_lang:
                    self.controlling_code_lang = _language if _in_code_block else None
            #@-<< identify_code_blocks >>
            #@+<< fill_chunks >>
            #@+node:TomP.20200112103729.5: *7* << fill_chunks >>

            _cleanline = line.strip()
            _starts_with_at = not _got_language and line and \
                              line[0] == '@' and\
                              not _cleanline == '@' and\
                              not _cleanline == '@c'

            if i == 0 and not _got_language:
                # Set up the first chunk (unless the first line changes the language)
                _chunk = Chunk(_tag, _structure, _lang)
                _chunk.add_line(line)
            elif _starts_with_at:
                # Keep Python decorators in code blocks
                if _chunk.tag == CODE:
                    _chunk.add_line(line)
            elif _got_language:
                if not _got_language_by_rst_block:
                    # We are starting a code block started by @language
                    if i > 0:
                        chunks.append(_chunk)
                    fields = line.split()
                    _lang = fields[1] if len(fields) > 1 else RST
                    _tag = CODE if _lang in LANGUAGES else TEXT
                    _chunk = Chunk(_tag, _structure, _lang)
                else:
                    # We are starting a code block started by ".. code::"
                    if i > 0:
                        chunks.append(_chunk)
                    _lang = TEXT
                    for lan_t in LANGUAGES:
                        if lan_t in line:
                            _lang = lan_t
                            break

                    _tag = CODE if _lang in LANGUAGES else TEXT
                    _chunk = Chunk(_tag, _structure, _lang)
                _got_language = False
            else:
                if _in_rst_block:
                    # We are in an indented code block started by ".. code::"
                    if not line.strip():
                        _chunk.add_line('')
                    elif _indentation:
                        fields = line.split(_indentation, 1)
                        if len(fields) > 1:
                            _chunk.add_line(fields[1])

                    if i == _last_code_line_num:
                        _in_rst_block = False
                        _tag = TEXT
                        _lang = RST
                        chunks.append(_chunk)
                        _chunk = Chunk(_tag, _structure, _lang)
                else:
                    _chunk.add_line(line)
            #@-<< fill_chunks >>
        #@-<< Loop Over Lines >>
        #@+<< Finalize Node >>
        #@+node:TomP.20200112103742.1: *6* << Finalize Node >>
        # Make sure chunk ends with a blank line
        _chunk.add_line('\n')

        chunks.append(_chunk)

        for ch in chunks:
            ch.format_code()
        if self.code_only:
            results = [ch.formatted for ch in chunks if ch.tag == CODE]
        else:
            results = [ch.formatted for ch in chunks]

        final_text = '\n'.join(results)
        codelines = []
        if self.execute_flag:
            codelines = ['\n'.join(ch.text_lines) for ch in chunks if ch.tag == CODE]

        return final_text, codelines
        #@-<< Finalize Node >>
    #@+node:tom.20210621144739.1: *5* vr3.make_title_from_headline
    def make_title_from_headline(self, p, h):
        """From node title, return title with over- and underline- strings.

           Symbol is chosen based on the indent level of the node.
           Note that might differe from p.h because of, e.g.,
           directive removal.

           ARGUMENTS
           p -- the node position whose indent level is to be used.
           h -- the headline string to be processed.

           RETURNS
           a string
        """
        level = min(p.level(), 4) - 1
        heading_str = RST_HEADING_CHARS[level] * (len(h) + 1)
        return f'{heading_str}\n{h}\n{heading_str}'
    #@+node:TomP.20200107232540.1: *5* vr3.make_rst_headline
    #@@language python
    def make_rst_headline(self, p, s):
        """Turn node's title into a headline and add to front of text.

        If the headline text (without directives and leading whitespace)
        equals the first line of the body text, don't insert a title.

        ARGUMENTS
        p -- the node being processed.
        s -- a string

        RETURNS
        a string s1 where s1 = (modified headline) + s.
        """

        _headline_str = ''
        if p.h:
            if p.h.startswith('@'):
                fields = p.h.split()
                if len(fields) > 1:
                    _headline = fields[1:]
                    _headline_str = ' '.join(_headline)
            else:
                _headline_str = p.h

            _headline_str = _headline_str.strip()  # Docutils raises error for leading space
            _headline_str = _headline_str.replace('\\', '\\\\')


        # Don't duplicate node heading if the body already has it
        # Assumes that 1st two lines are a heading if
        # node headline == body's first line.
        body_lines = p.b.split('\n', 1)
        first_line = body_lines[0].strip()

        if not first_line or _headline_str != first_line:
            headline_str = self.make_title_from_headline(p, _headline_str)
            s = f'{headline_str}\n\n{s}'

        return s
    #@+node:TomP.20191215195433.77: *4* vr3.update_svg
    # http://doc.trolltech.com/4.4/qtsvg.html
    # http://doc.trolltech.com/4.4/painting-svgviewer.html

    def update_svg(self, s, keywords):
        if not QtSvg:
            g.es(NO_SVG_WIDGET_MSG, color='red')
            return
        pc = self

        if pc.must_change_widget(QSvgWidget):
            w = QSvgWidget()
            pc.embed_widget(w)
            assert w == pc.w
        else:
            w = pc.w
        if s.strip().startswith('<'):
            # Assume it is the svg (xml) source.
            # Sensitive to leading blank lines.
            s = textwrap.dedent(s).strip()
            bytes = g.toEncodedString(s)
            pc.show()
            w.load(QtCore.QByteArray(bytes))
            w.show()
        else:
            # Get a filename from the headline or body text.
            ok, path = pc.get_fn(s, '@svg')
            if ok:
                pc.show()
                w.load(path)
                w.show()
    #@+node:TomP.20191215195433.78: *4* vr3.update_url
    def update_url(self, s, keywords):
        pc = self
        c, p = self.c, self.c.p
        colorizer = c.frame.body.colorizer
        language = colorizer.scanLanguageDirectives(p)
        if language == 'asciidoc':
            p.update_asciidoc(s, keywords)
        elif language in ('rest', 'rst'):
            pc.update_rst(s, keywords)
        elif language in ('markdown', 'md'):
            pc.update_md(s, keywords)
        elif pc.default_kind in ('rest', 'rst'):
            pc.update_rst(s, keywords)
        elif pc.default_kind in ('markdown', 'md'):
            pc.update_md(s, keywords)
        else:
            # Do nothing.
            g.trace('ignore', s)
            w = pc.ensure_text_widget()
            pc.show()
            w.setPlainText('')
    #@+node:TomP.20191215195433.79: *4* vr3.utils for update helpers...
    #@+node:TomP.20191215195433.80: *5* vr3.ensure_text_widget
    def ensure_text_widget(self):
        """Swap a text widget into the rendering pane if necessary."""
        c, pc = self.c, self
        if pc.must_change_widget(QtWidgets.QTextBrowser):
            # Instantiate a new QTextBrowser.
            w = QtWidgets.QTextBrowser()

            def handleClick(url, w=w):
                wrapper = qt_text.QTextEditWrapper(w, name='vr3-body', c=c)
                event = g.Bunch(c=c, w=wrapper)
                g.openUrlOnClick(event, url=url)

            if self.w and hasattr(self.w, 'anchorClicked'):
                try:
                    self.w.anchorClicked.disconnect()
                except Exception:
                    g.es_exception()

            w.anchorClicked.connect(handleClick)
            w.setOpenLinks(False)

            pc.embed_widget(w)  # Creates w.wrapper
            assert w == pc.w
        return pc.w
    #@+node:TomP.20191227101625.1: *5* vr3.ensure_web_widget
    def ensure_web_widget(self):
        """Swap a webengineview widget into the rendering pane if necessary."""
        pc = self
        w = self.qwev
        if pc.must_change_widget(has_webengineview):
            pc.embed_widget(w)  # Creates w.wrapper
            assert w == pc.w
        return pc.w
    #@+node:TomP.20191215195433.81: *5* vr3.get_kind
    def get_kind(self, p):
        """Return the proper rendering kind for node p."""

        #  #1287: Honor both kind of directives node by node.
        for p1 in p.self_and_parents(p):
            language = self.get_language(p1)
            if got_markdown and language in ('md', 'markdown'):
                return language
            if got_docutils and language in ('rest', 'rst'):
                return language
            if language and language in self.dispatch_dict:
                return language
        return None
    #@+node:TomP.20200109132851.1: *6* vr3.get_language
    def get_language(self, p):
        """Return the language in effect at position p.

        Headline directives over-ride normal Leo directives in body text.
        """

        c = self.c
        h = p.h
        # First, look for headline directives.
        if h.startswith('@'):
            i = g.skip_id(h, 1, chars='-')
            word = h[1:i].lower().strip()
            if word in self.dispatch_dict:
                return word
        # Look for @language directives.
        # Warning: (see #344): don't use c.target_language as a default.
        colorizer = getattr(c.frame.body.colorizer, 'findFirstValidAtLanguageDirective', g)
        return colorizer.findFirstValidAtLanguageDirective(p.b)
    #@+node:TomP.20191215195433.82: *5* vr3.get_fn
    def get_fn(self, s, tag):
        pc = self
        c = pc.c
        fn = s or c.p.h[len(tag) :]
        fn = fn.strip()
        # Similar to code in g.computeFileUrl
        if fn.startswith('~'):
            fn = fn[1:]
            fn = g.finalize(fn)
        else:
            # Handle ancestor @path directives.
            if c and c.fileName():
                base = c.getNodePath(c.p)
                fn = g.finalize_join(g.os_path_dirname(c.fileName()), base, fn)
            else:
                fn = g.finalize(fn)

        ok = g.os_path_exists(fn)
        return ok, fn

    #@+node:TomP.20191215195433.83: *5* vr3.get_url
    def get_url(self, s, tag):
        p = self.c.p
        url = s or p.h[len(tag) :]
        url = url.strip()
        return url
    #@+node:TomP.20191215195433.84: *5* vr3.must_change_widget
    def must_change_widget(self, widget_class):
        pc = self
        return not pc.w or pc.w.__class__ != widget_class  # EKR.
    #@+node:TomP.20191215195433.85: *5* vr3.remove_directives
    def remove_directives(self, s):
        """Remove all Leo directives from a string except "@language"."""

        _directives = g.globalDirectiveList[:]
        _directives.remove('language')
        _directives.remove('c')
        lines = g.splitLines(s)
        result = []
        for li in lines:
            if li.startswith('@'):
                i = g.skip_id(li, 1)
                word = li[1:i]
                if word in _directives:
                    continue
            result.append(li)
        return ''.join(result)
    #@+node:TomP.20200112233701.1: *5* vr3.execute_code
    # Modified from VR2
    def exec_code(self, code, environment):
        """Execute the code, capturing the output in stdout and stderr."""
        saveout = sys.stdout  # save stdout
        saveerr = sys.stderr
        sys.stdout = bufferout = StringIO()
        sys.stderr = buffererr = StringIO()
        except_err = ''

        try:
            exec(code, environment)
        except Exception as e:
            # g.es('Viewrendered3 exception:')
            # g.es('    ', e)
            print('Viewrendered3 exception:')
            print('    ', e)
            g.es_exception()
            except_err = f'{type(e).__name__}: {str(e)}\n'
        # Restore stdout, stderr
        finally:
            sys.stdout = saveout  # was sys.__stdout__
            sys.stderr = saveerr  # restore stderr

        return bufferout.getvalue(), buffererr.getvalue() + except_err
    #@+node:TomP.20200330152649.1: *4* vr3.update_text
    def update_text(self, node_list, keywords=None):
        """Update as text-only in the vr3 pane.

            ARGUMENTS
            node_list -- a list of outline nodes to be processed.
            keywords -- a dictionary of keywords

            RETURNS
            nothing
        """
        # Do this regardless of whether we show the widget or not.
        self.ensure_web_widget()
        assert self.w
        w = self.w
        lines = []
        for node in node_list:
            body = node.b
            if body.startswith('@language'):
                i = body.find('\n')
                if i > -1:
                    body = body[i + 1 :]
            lines.append(body)
        s = '\n'.join(lines)
        self.last_markup = s

        s = html.escape(s, quote=True)
        s = f'{TEXT_HTML_HEADER}<pre>{s}</pre></html>'
        h = s.encode('utf-8')
        self.set_html(h, w)
        self.rst_html = h

        w.show()
    #@+node:TomP.20200329230436.1: *4* vr3: command helpers...
    #@+node:TomP.20200329230436.2: *5* vr3.activate
    def activate(self):
        """Activate the vr3-window."""
        pc = self
        if pc.active:
            return
        pc.inited = True
        pc.active = True
        g.registerHandler('select2', pc.update)
        g.registerHandler('idle', pc.update)
    #@+node:TomP.20200329230436.3: *5* vr3.contract & expand
    # Change zoom factor of rendering pane
    def contract(self):
        self.change_size(-100)

    def expand(self):
        self.change_size(100)

    def change_size(self, delta):
        if hasattr(self.c, 'free_layout'):
            splitter = self.parent()
            i = splitter.indexOf(self)
            assert i > -1
            sizes = splitter.sizes()
            n = len(sizes)
            for j, size in enumerate(sizes):
                if j == i:
                    sizes[j] = max(0, size + delta)
                else:
                    sizes[j] = max(0, size - int(delta / (n - 1)))
            splitter.setSizes(sizes)
    #@+node:TomP.20200329230436.4: *5* vr3.deactivate
    def deactivate(self):
        """Deactivate the vr3 window."""
        pc = self
        # Never disable the idle-time hook: other plugins may need it.
        g.unregisterHandler('select2', pc.update)
        g.unregisterHandler('idle', pc.update)
        pc.active = False
    #@+node:tom.20220824142257.1: *5* vr3.freeze/unfreeze
    def set_freeze(self):
        """Freeze the vr3 pane to prevent updates ."""
        action = self.action_freeze
        action.setChecked(True)
        self.freeze = True

    def set_unfreeze(self):
        """Freeze the vr3 pane to prevent updates ."""
        action = self.action_freeze
        action.setChecked(False)
        self.freeze = False
    #@+node:TomP.20200329230436.5: *5* vr3.lock/unlock
    def lock(self):
        """Lock the vr3 pane to the current node ."""
        action = self.action_lock_to_tree
        action.setChecked(True)
        self.lock_to_tree = True
        self.current_tree_root = self.c.p

    def unlock(self):
        """Unlock the vr3 pane."""
        action = self.action_lock_to_tree
        action.setChecked(False)
        self.lock_to_tree = False
        self.current_tree_root = None
    #@+node:TomP.20200329230436.6: *5* vr3.show_dock_or_pane
    def show_dock_or_pane(self):
        c, vr3 = self.c, self
        vr3.activate()
        # vr3.show()
        if positions[c.hash()] == OPENED_IN_SPLITTER:
            vr3.adjust_layout('open')
        c.bodyWantsFocusNow()
    #@+node:TomP.20200329230436.8: *5* vr3: toolbar helpers...
    #@+node:TomP.20200329230436.9: *6* vr3.get_toolbar_label
    #@+at
    # def get_toolbar_label(self):
    #     """Return the toolbar label object."""
    #
    #     return self.findChild(QtWidgets.QLabel, VR3_TOOLBAR_NAME)
    #@+node:TomP.20200329230436.10: *6* vr3.hide_toolbar
    def hide_toolbar(self):
        try:
            _toolbar = self.vr3_toolbar
            _toolbar.setVisible(False)
        except RuntimeError as e:
            g.es(f'show_toolbar(): no toolbar; {type(e)}: {e}')
            return

    #@+node:TomP.20200329230436.11: *6* vr3.show_toolbar
    def show_toolbar(self):
        try:
            _toolbar = self.vr3_toolbar
            _toolbar.setVisible(True)
        except RuntimeError as e:
            g.es(f'show_toolbar(): no toolbar; {type(e)}: {e}')
            return


    #@+node:TomP.20200329230436.7: *5* vr3.adjust_layout (legacy only)
    def adjust_layout(self, which):

        global layouts
        c = self.c
        splitter = self.splitter
        deflo = c.db.get(VR3_DEF_LAYOUT, (None, None))
        loc, loo = layouts.get(c.hash(), deflo)
        if which == 'closed' and loc and splitter:
            # Make it work with old and new layout code
            try:
                splitter.load_layout(loc)
            except TypeError:
                splitter.load_layout(c, loc)
        elif which == 'open' and loo and splitter:
            try:
                splitter.load_layout(loo)
            except TypeError:
                splitter.load_layout(c, loo)
    #@+node:TomP.20200329230436.12: *5* vr3: zoom helpers...
    #@+node:TomP.20200329230436.13: *6* vr3.shrinkView
    def shrinkView(self):
        w = self.qwev
        _zf = w.zoomFactor()
        w.setZoomFactor(_zf / ZOOM_FACTOR)
    #@+node:TomP.20200329230436.14: *6* vr3.zoomView
    def zoomView(self):
        w = self.qwev
        _zf = w.zoomFactor()
        w.setZoomFactor(_zf * ZOOM_FACTOR)
    #@+node:TomP.20200329230453.1: *4* vr3: events...
    #@+node:TomP.20200329230453.2: *5* vr3.closeEvent
    def closeEvent(self, event):
        """Close the vr3 window."""
        self.deactivate()
    #@+node:TomP.20200329230453.3: *5* vr3.keyPressEvent
    def keyPressEvent(self, event):
        """Take actions on keypresses when the VR3 render pane has focus and a
           key is pressed.

        A method of this name receives keystrokes for most or all
        QObject-descended objects. Currently, check only for <CNTRL-=> and
        <CONTROL-MINUS> events for zooming or unzooming the VR3 browser pane.
        """
        mod = ''
        modifiers = event.modifiers()
        bare_key = event.text()
        if modifiers and modifiers == KeyboardModifier.ControlModifier:
            mod = 'cntrl'
        if bare_key == '=' and mod == 'cntrl':
            self.zoomView()
        elif bare_key == '-' and mod == 'cntrl':
            self.shrinkView()
    #@+node:TomP.20200329230503.1: *4* vr3: utils
    #@+node:TomP.20200329230503.2: *5* vr3.set_html
    def set_html(self, s, w):
        """Set text in w to s."""
        c = self.c
        # Find path relative to this file.  Needed as the base of relative
        # URLs, e.g., image or included files.
        path = c.getNodePath(c.p)
        s = g.toUnicode(s)
        try:
            url_base = QtCore.QUrl('file:///' + path + '/')
            w.setHtml(s, url_base)
        except Exception as e:
            # Oops, don't have a QWebEngineView
            g.es(e)
            w.setHtml(s)

        w.show()
    #@+node:TomP.20200329230503.3: *5* vr3.underline
    def underline(self, s):
        """Generate rST underlining for s."""
        ch = '#'
        n = max(4, len(g.toEncodedString(s, reportErrors=False)))
        return f'{s}\n{ch * n}\n\n'
    #@+node:TomP.20200329230503.4: *5* vr3.store_layout
    def store_layout(self, which):

        global layouts
        c = self.c
        h = c.hash()
        splitter = self.splitter
        deflo = c.db.get(VR3_DEF_LAYOUT, (None, None))
        (loc, loo) = layouts.get(c.hash(), deflo)
        if which == 'closed' and splitter:
            loc = splitter.get_saveable_layout()
            loc = json.loads(json.dumps(loc))
            layouts[h] = loc, loo
        elif which == 'open' and splitter:
            loo = splitter.get_saveable_layout()
            loo = json.loads(json.dumps(loo))
            layouts[h] = loc, loo
        c.db[VR3_DEF_LAYOUT] = layouts[h]
    #@-others
#@+node:TomP.20200827172759.1: ** State Machine Components
#@+node:TomP.20200213170204.1: *3* class State
class State(Enum):
    BASE = auto()
    AT_LANG_CODE = auto()
    AT_MATH_CODE = auto()
    FENCED_CODE = auto()
    FENCED_MATH = auto()
    IN_SKIP = auto()
    IN_MATH = auto()
    TO_BE_COMPUTED = auto()

    STARTING_ASCDOC_CODE_BLOCK = auto()
    ASCDOC_READY_FOR_FENCE = auto()

#@+node:TomP.20200213170314.1: *3* class Action
class Action:
    @staticmethod
    def new_chunk(sm, line, tag, language, addline_at_new_start=False):
        """ Add chunk to chunk list, create new chunk.

        ARGUMENTS
        sm -- a StateMachine instance.
        line -- the line of text to be processed.
        tag -- the current tag for the chunk.
        """

        sm.chunk_list.append(sm.current_chunk)
        sm.current_chunk = Chunk(tag, sm.structure, language)
        if addline_at_new_start:
            sm.current_chunk.add_line(line)

    @staticmethod
    def new_chunk_add_line_to_old_end(sm, line, tag, language):
        sm.current_chunk.add_line(line)
        sm.chunk_list.append(sm.current_chunk)
        sm.current_chunk = Chunk(tag, sm.structure, language)

    @staticmethod
    def new_chunk_add_line_to_new_start(sm, line, tag, language):
        Action.new_chunk(sm, line, tag, language, True)

    @staticmethod
    def add_line(sm, line, tag=None, language=TEXT):
        sm.current_chunk.add_line(line)

    @staticmethod
    def add_image(sm, line, tag=None, language=None):
        # Used for @image lines
        marker, tag, _lang = StateMachine.get_marker(sm, line)
        # Get image url
        fields = line.split(' ', 1)
        if len(fields) > 1:
            url = fields[1] or ''
            if url:
                if sm.structure == MD:
                    # image syntax: ![label](url)
                    line = f'![]({url})'
                elif sm.structure == ASCIIDOC:
                    # image syntax: image:<target>[<attributes>] (must include "{}" even if no attributes
                    line = f'image:{url}[]'
                sm.current_chunk.add_line(line)
            # If no url parameter, do nothing

    @staticmethod
    def no_action(sm, line, tag=None, language=TEXT):
        pass

    @staticmethod
    def add_math_block_start(sm, line, tag=None, language=None):
        line = r'\['
        sm.current_chunk.add_line(line)

    @staticmethod
    def add_math_block_end(sm, line, tag=None, language=None):
        line = r'\]'
        sm.current_chunk.add_line(line)
#@+node:TomP.20200213170250.1: *3* class Marker
class Marker(Enum):
    """
    For indicating markers in a text line that characterize their purpose, like "@language".
    """

    AT_LANGUAGE_MARKER = auto()
    MD_FENCE_LANG_MARKER = auto()  # fence token with language; e.g. ```python
    MD_FENCE_MATH_MARKER = auto()  # math fence: ```math
    MD_FENCE_MARKER = auto()  # fence token with no language
    MARKER_NONE = auto()  # Not a special line.
    START_SKIP = auto()
    END_SKIP = auto()
    IMAGE_MARKER = auto()

    ASCDOC_CODE_MARKER = auto()
    ASCDOC_CODE_LANG_MARKER = auto()  # a line like "[source, python]" before a line "---"

#@+node:TomP.20191231172446.1: *3* class Chunk
#@@language python
class Chunk:
    """Holds a block of text, with various metadata about it."""

    def __init__(self, tag='', structure=RST, language=''):
        self.text_lines = []  # The text as a sequence of lines, free of directives
        self.tag = tag  # A descriptive value for the kind of chunk, such as CODE, TEXT.
        self.structure = structure  # The type of structure (rst, md, etc.).
        self.language = language  # The programming language, if any, for this chunk.
        self.formatted = ''  # The formatted text.

    def add_line(self, line):
        self.text_lines.append(line)

    def format_code(self):
        """Format the text of a chunk. Include special formatting for CODE chunks.

        Currently reformats RsT, MD, and Asciidoc, for code languages
        python, javascript, java, css, and xml.
        """

        if self.tag != CODE or self.structure not in (RST, REST, MD, ASCIIDOC):
            self.formatted = '\n'.join(self.text_lines)
            return

        _formatted = ['']
        if self.tag == CODE:
            if self.structure in (RST, REST):
                _formatted = [f'.. code:: {self.language}\n']
                for line in self.text_lines:
                    if not line.strip():
                        _formatted.append('')
                    else:
                        _formatted.append(RST_INDENT + line)
                _formatted.append('')
                self.formatted = '\n'.join(_formatted)
            elif self.structure == MD:
                _formatted = [f'{MD_CODE_FENCE}{self.language}']
                _formatted.extend(self.text_lines)
                _formatted.append(f'{MD_CODE_FENCE}')
                self.formatted = '\n'.join(_formatted)
            elif self.structure == ASCIIDOC:
                code_marker = ASCDOC_CODE_LANG_MARKER + self.language + ']'
                _formatted = [code_marker]
                _formatted.append(ASCDOC_FENCE_MARKER)
                _formatted.extend(self.text_lines)
                _formatted.append(ASCDOC_FENCE_MARKER)
                self.formatted = '\n'.join(_formatted)
#@+node:TomP.20200211142437.1: *3* class StateMachine
#@@language python

class StateMachine:
    def __init__(self, vr3, tag=TEXT, structure=RST, lang=RST):
        self.vr3 = vr3
        self.base_tag = tag
        self.structure = structure
        self.base_lang = lang
        self.state = State.BASE
        self.last_state = State.BASE
        self.last_marker = None

        self.chunk_list = []
        self.current_chunk = Chunk(self.base_tag, structure, self.base_lang)
        self.lang = lang
        self.tag = tag
        self.codelang = ''

        self.inskip = False

    def reset(self, tag=TEXT, lang=RST):
        self.state = State.BASE
        self.last_state = State.BASE
        self.chunk_list = []
        self.current_chunk = Chunk(tag, self.structure, lang)
        self.lang = lang
        self.tag = tag
        self.inskip = False
        self.codelang = ''

    #@+<< runMachine >>
    #@+node:TomP.20200215180012.1: *4* << runMachine >>
    def runMachine(self, lines):
        """Process a list of text lines and return final text and a list of lines of code.

        ARGUMENT
        lines -- a list of lines of text.

        RETURNS
        a tuple (final_text, code_lines).
        """

        for self.i, line in enumerate(lines):
            self.do_state(self.state, line)
        self.chunk_list.append(self.current_chunk)  # have to pick up the last chunk


        for ch in self.chunk_list:
            ch.format_code()

        if self.vr3.code_only:
            results = [ch.formatted for ch in self.chunk_list if ch.tag == CODE]
        else:
            results = [ch.formatted for ch in self.chunk_list]

        codelines = []
        if self.vr3.execute_flag:
            codelines = ['\n'.join(ch.text_lines) for ch in self.chunk_list if ch.tag == CODE]

        final_text = '\n'.join(results)
        return final_text, codelines
    #@-<< runMachine >>
    #@+<< do_state >>
    #@+node:TomP.20200213170532.1: *4* << do_state >>
    #@@language python
    def do_state(self, state, line):
        marker, tag, language = self.get_marker(line)
        if marker == Marker.START_SKIP:
            self.inskip = True
            self.last_state = self.state
            self.state = State.IN_SKIP
            return
        if marker == Marker.END_SKIP:
            self.inskip = False  # EKR.
            self.state = self.last_state
            return
        if self.state == State.IN_SKIP:
            return
        try:
            action, next = StateMachine.State_table[(state, marker)]
        except KeyError:
            return

        if next == State.TO_BE_COMPUTED:
            # Need to know if this line specified a code or text language.
            # Only known case is if we are in an @language code block
            # and encounter another @language block.
            if tag == CODE:
                next = State.AT_LANG_CODE
                # _lang = language
            else:
                next = State.BASE
                # _lang = self.base_lang

        action(self, line, tag, language)
        self.state = next
    #@-<< do_state >>
    #@+<< get_marker_md >>
    #@+node:TomP.20200901214058.1: *4* << get_marker_md >>
    def get_marker_md(self, line, tag, _lang, marker):
        # If _lang == a code language, we are starting a code block.
        if _lang:
            if _lang in LANGUAGES:
                lang = _lang
                tag = CODE
                marker = Marker.MD_FENCE_LANG_MARKER
            elif _lang == MATH:
                lang = MATH
                tag = MATH
                marker = Marker.MD_FENCE_MATH_MARKER
            else:
                # If _lang is TEXT or unknown, we are starting a new literal block.
                lang = _lang
                tag = TEXT
                marker = Marker.MD_FENCE_MARKER
        else:
            # If there is no language indicator after the fence,
            # We are ending the block
            lang = _lang
            tag = TEXT
            marker = Marker.MD_FENCE_MARKER

        return (marker, tag, lang)
    #@-<< get_marker_md >>
    #@+<< get_marker_asciidoc >>
    #@+node:TomP.20200901211601.1: *4* << get_marker_asciidoc >>
    def get_marker_asciidoc(self, line, tag, lang, marker):

        if line.startswith(ASCDOC_CODE_LANG_MARKER):
            self.codelang = ''
            lang = ASCIIDOC
            frags = line.split(',')
            if len(frags) == 2:
                _lang = frags[1][:-1].strip()  # remove trailing ']' and spaces
                if _lang in LANGUAGES:
                    lang = _lang
                self.codelang = _lang
                marker = Marker.ASCDOC_CODE_LANG_MARKER
                self.last_marker = marker
                self.tag = TEXT
        elif line.startswith(ASCDOC_FENCE_MARKER):
            # Might be either the start or end of a code block
            if self.last_marker == Marker.ASCDOC_CODE_LANG_MARKER:
                if self.codelang in LANGUAGES:
                    tag = CODE
                    lang = self.codelang
                else:
                    tag = TEXT
                marker = Marker.ASCDOC_CODE_MARKER
                self.tag = tag
                self.last_marker = Marker.ASCDOC_CODE_MARKER
            else:
                # Must be at the end of a code chunk
                lang = ASCIIDOC
                tag = TEXT
                self.codelang = ''
                marker = Marker.ASCDOC_CODE_MARKER
                self.last_marker = None

        return (marker, tag, lang)
    #@-<< get_marker_asciidoc >>
    #@+<< get_marker >>
    #@+node:TomP.20200212085651.1: *4* << get_marker >>
    #@@language python
    def get_marker(self, line):
        """Return classification information about a line.

        Used by the state table machinery.

        ARGUMENT
        line -- the line of text to be classified.

        RETURNS
        a tuple (marker, tag, lang), where
            marker is one of the enumeration from class Marker;
            tag is one of CODE, TEXT;
            lang is the language (e.g., MD, RST, ASCIIDOC, PYTHON) specified by the line, else None.
        """

        marker = Marker.MARKER_NONE
        tag = TEXT
        lang = None

        # For debugging
        if line.startswith('#%%%%'):
            g.es(f'==== state: {self.state}, lang: {self.lang}, chunk_lang: {self.current_chunk.language}, tag: {self.current_chunk.tag}')
            return (None, None, None)

        # Omit lines between @ and @c
        if line.rstrip() == '@':
            marker = Marker.START_SKIP
        elif line.strip() == '@c':
            marker = Marker.END_SKIP

        # A marker line may start with "@language", "@image", or a  code fence.
        elif line.startswith("@language"):
            marker = Marker.AT_LANGUAGE_MARKER
            for _lang in LANGUAGES:
                if _lang in line:
                    lang = _lang
                    tag = CODE
                    break

        elif line.startswith("@image"):
            marker = Marker.IMAGE_MARKER
            lang = self.structure

        elif line.startswith(MD_CODE_FENCE) and self.structure == MD:
            lang = MD
            tag = TEXT
            _lang = line.split(MD_CODE_FENCE)[1]
            (marker, tag, lang) = self.get_marker_md(line, tag, _lang, marker)

        elif self.structure == ASCIIDOC:
            lang = ASCIIDOC
            tag = TEXT
            (marker, tag, lang) = self.get_marker_asciidoc(line, tag, lang, marker)

        else:
            marker = Marker.MARKER_NONE

        return (marker, tag, lang)
    #@-<< get_marker >>
    #@+<< State Table >>
    #@+node:TomP.20200213171040.1: *4* << State Table >>
    State_table = {  # (state, marker): (action, next_state)

        (State.BASE, Marker.AT_LANGUAGE_MARKER): (Action.new_chunk, State.AT_LANG_CODE),
        # (State.AT_LANG_CODE, Marker.MARKER_NONE): (Action.add_line, State.AT_LANG_CODE),
        (State.AT_LANG_CODE, Marker.MARKER_NONE): (Action.add_line, State.BASE),
        (State.BASE, Marker.MARKER_NONE): (Action.add_line, State.BASE),

        # When we encounter a new @language line, the next state might be either
        # State.BASE or State.AT_LANG_CODE, so we have to compute which it will be.
        (State.AT_LANG_CODE, Marker.AT_LANGUAGE_MARKER):
                    (Action.new_chunk, State.TO_BE_COMPUTED),

        (State.BASE, Marker.IMAGE_MARKER): (Action.add_image, State.BASE),

        # ========= Markdown-specific states ==================
        (State.BASE, Marker.MD_FENCE_LANG_MARKER): (Action.new_chunk, State.FENCED_CODE),
        (State.BASE, Marker.MD_FENCE_MARKER): (Action.add_line, State.BASE),
        (State.FENCED_CODE, Marker.MARKER_NONE): (Action.add_line, State.FENCED_CODE),
        (State.FENCED_CODE, Marker.MD_FENCE_MARKER): (Action.new_chunk, State.BASE),
        (State.AT_LANG_CODE, Marker.MD_FENCE_MARKER):
                    (Action.add_line, State.AT_LANG_CODE),
        (State.BASE, Marker.MD_FENCE_MATH_MARKER): (Action.add_math_block_start, State.FENCED_MATH),
        (State.FENCED_MATH, Marker.MARKER_NONE): (Action.add_line, State.FENCED_MATH),
        (State.FENCED_MATH, Marker.MD_FENCE_MARKER): (Action.add_math_block_end, State.BASE),

        # ========== ASCIIDOC-specific states =================
        (State.BASE, Marker.ASCDOC_CODE_LANG_MARKER):
                    (Action.no_action, State.ASCDOC_READY_FOR_FENCE),
        (State.ASCDOC_READY_FOR_FENCE, Marker.ASCDOC_CODE_MARKER):
                    # Start a new code chunk
                    (Action.new_chunk, State.FENCED_CODE),
        (State.FENCED_CODE, Marker.MARKER_NONE): (Action.add_line, State.FENCED_CODE),
        (State.FENCED_CODE, Marker.ASCDOC_CODE_MARKER):
                    # End fenced code chunk
                    (Action.new_chunk, State.BASE)
    }
    #@-<< State Table >>

#@-others

#@-leo

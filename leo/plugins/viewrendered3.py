#@+leo-ver=5-thin
#@+node:TomP.20191215195433.1: * @file viewrendered3.py
#@@tabwidth -4
#@@language python
"""
#@+<< vr3 docstring >>
#@+node:TomP.20191215195433.2: ** << vr3 docstring >>
#@@language rest
#@@wrap
Creates a window for *live* rendering of reSTructuredText, markdown text,
images, movies, sounds, rst, html, jupyter notebooks, etc.

#@+others
#@+node:TomP.20200308230224.1: *3* About
About
=====

The ViewRendered3 plugin (hereafter "VR3") duplicates the functionalities of the ViewRendered plugin and enhances the display of Restructured Text (RsT) and Markdown (MD) nodes and subtrees.  For RsT and MD, the plugin can:

    #. Display entire subtrees starting at the selected node;
    #. Display code and literal blocks in a visually distinct way;
    #. Any number of code blocks and be intermixed with RsT ot MD in a single node.
    #. Display just the code blocks;
    #. Colorize code blocks;
    #. Execute Python code in the code blocks;
    #. Insert the print() output of an execution at the bottom of the rendered display;
    #. Identify code blocks by either an @language directive or by the code block syntax normally used by RsT or MD (e.g., code fences for MD);
    #. Honor "@" and "@c" directives to ignore all lines between them;
    #. Export the rendered node or subtree to the system browser;
    #. Optionally render mathematics symbols and equations using MathJax;
    #. Correctly handle RsT or MD in a docstring'
    #. While an entire subtree rendering is visible, the display can be locked so that the entire tree shows even while a single node is being edited.
    #. When an entire subtree is rendered, and editing is being done in one node, the display can be frozen (no changes will be displayed) if necessary to avoid excessive delay in re-rendering, or visual anomalies.
    #. The default rendering language for a node can be selected to by one of "RsT", "MD", or "TEXT".  This setting applies when the node or subtree has no @rst or @md headline.
    #. Displays a node's headline text as the overall heading for the rendering.  However, if the first line of a node exactly equals the headline text (not counting a directive like "@rst"), only one copy of that heading will be displayed.

@setting nodes in an @settings tree can modify the behavior of the plugin.
#@+node:TomP.20200309205046.1: *3* Compatibility
Compatibility
=============

Viewrendered3 is intended to be able to co-exist with Viewrendered.  In limited testing, this seems to work as expected.

It is advisable to bind VR to a different hot key than VR3.  One possibility is Alt-0 for VR3 and Alt-F10 for VR.

#@+node:TomP.20200308232305.1: *3* Limitations and Quirks
Limitations and Quirks
======================

    #. The plugin requires QT5 and Python 3.6+. All Leo versions since 6.0 also use them, so this requirement should always be met.

    #. At the current time, the plugin **only works** when Leo is launched using docks.  For Leo versions > 6.1, this means launching it with the **``--use-docks``** parameter.

    #. The RsT processor (``docutils``) is fussy about having blank lines after blocks.  A node may render correctly on its own, but will show errors when displayed in a subtree.  In most cases, the fix is to add a blank line at the end of a node. This may be fixed in a future version.
    
    #. Without MathJax, mathematical symbols RsT is rendered using CSS, which has a cruder appearance than MathJax rendering but may be servicable.  With MD, mathematical symbols are not rendered.
    
    #. Code blocks for several programming languages can be colorized, even within a single node.  But only Python blocks can be executed.  Blocks intended for another language (such as javascript) will cause syntax errors if an attempt is made to execute the node.
    
    #. The Viewrendered2 plugin, now obsolete, could be set to display execution output as RsT.  This was useful for code that would print RsT.  The current VR3 plugin cannot be set to render the output as RsT.

    #. Behavior for nodes other than @rst or @md nodes is the same as for the Viewrendered plugin.  This includes any bugs or unexpected behaviors.

    #. There is currently no provision to pass through extensions to the Markdown processor.
    
    #. The rendered pane have the magnification change (zoom and unzoom) using the standard hot keys <CTRL>+ - and <CTRL>+ =.  This only works if the cursor has been clicked inside the render pane first.

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
========

Settings are put into nodes with the headlines ``@setting ....``.  They must be placed into an ``@settings`` tree, preferably in the myLeoSettings file.

.. csv-table:: Settings
   :header: "Setting", "Default", "Values", "Purpose"
   :widths: 18, 5, 5, 30

   "vr3-default-kind", "rst", "rst, md", "Default for rendering type"
   "vr3-math-output", "False", "True, False", "RsT MathJax math rendering"
   "vr3-md-math-output", "False", "True, False", "MD MathJax math rendering"
   "vr3-mathjax-url", "''", "url string", "MathJax script URL (both RsT and MD)"
   "vr3-rst-stylesheet", "''", "url string", "URL for RsT Stylesheet"
   "vr3-md-stylesheet", "''", "url string", "URL for MD stylesheet"

**Examples**::

    @string vr3-mathjax-url = file:///D:/utility/mathjax/es5/tex-chtml.js
    @string vr3-mathjax-url = https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.6/latest.js?config=TeX-AMS_CHTML
    @string vr3-md-math-output = True

Stylesheets
===========

CSS stylesheets are located in Leo's plugin/viewrendered3 directory.  They are used if no other location is specified by an ``@setting`` node, or if a specified file:/// URL does not exist.  If the MD stylesheet is removed, the plugin will re-create it on startup, but the RsT stylesheet will not be recreated if removed.

MathJax Script Location
=======================

The script for MathJax rendering of math symbols can be in a local directory on your computer.  This has the advantages of fast loading and working without an internet. Using an Internet URL has the advantage that the URL will work if the exported HTML file is sent to someone else.

If the MathJax scripts are installed on the local computer, it is recommended that one of the ``.js`` script files in the ``es`` directory be used, as shown in the above table.  If the script is loaded from the Internet, the URL must include a ``?config`` specifer.  The one shown in the example above works well.
 
Hot Key
=======

Binding the plugin's visibility to a hot key is very desirable.  ``Alt-0`` is convenient.  The standard Leo way to bind a hot key is by putting the binding into the body of a setting node with the headline ``@shortcuts``.  Here is an example for the VR3 plugin::

    vr3-toggle = Alt+0

#@+node:TomP.20200115200324.1: *3* Commands
Commands
========

viewrendered3.py- specific commands all start with a "vr3-" prefix.  There is rarely a reason to invoke any of them, except for ``vr3-toggle``, which shows or hides the VR3 pane. This is best bound to a hot key (see above).

#@+node:TomP.20200115200601.1: *3* Rendering reStructuredText
Rendering reStructuredText
==========================

The VR3 plugin will render a node using RsT if its headline, or the headline of a parent, starts with ``@rst``. The type of rendering is called its "kind". If no kind is known, then RsT rendering will be used unless the ``vr3-default-kind`` setting is set to ``@md``.  The default kind can also be changed using the ``Default Kind`` menu.

Besides the normal RsT method of declaring a code block::

    .. code:: python

        # This will be some Python code
        def f(x):
            return 2*x

A code block can be started with an ``@language directive``::

    @language python
    def f(x):
        return 2*x

Return to RsT rendering with an ``@language rest`` directive at the start of a line (the code block must end with a blank line before the new directive). ``@language rst`` is also accepted

Any number of code blocks can be used in a node, but do not try to split a code block across two nodes.

Other languages are supported besides python.  See the list of languages below at **Colorized Languages**.  Only Python can be successfully executed.

VR3 can render both RsT and MD, but do not mix the two in any one node or subtree.

**Note**: reStructuredText errors and warnings will appear in red in the rendering pane.

#@+node:TomP.20200115200634.1: *3* Rendering Markdown
Rendering Markdown
==================

Please see the markdown syntax document at http://daringfireball.net/projects/markdown/syntax for more information on markdown.

Unless ``@string vr3-default-kind`` is set to ``md``, markdown 
rendering must be specified by putting it in a ``@md`` node.

A literal block is declared using backtick "fences"::


    ``` text
    this should be a literal block.
    ```

Note that the string ``text`` is required for proper rendering, 
even though some MD processors will accept the triple-backtick 
fence by itself without it. Fences must begin at the start of a line.

A code block is indicated with the same fence, but the name of 
the language instead::

    ``` python
    def f(x):
        return 2*x
    ```

Code blocks can be also be started with an ``@language directive``::

    @language python
    def f(x):
        return 2*x

After a code block, MD rendering can specified with a ``@language md`` 
directive.

Other languages are supported besides python.  See the 
list of languages below at **Colorized Languages**.  Only Python 
can be successfully executed.

As with RsT rendering, do not mix MD and RsT in a single node or subtree.

#@+node:TomP.20200309191519.1: *3* Colorized Languages
Colorized Languages
===================

Currently the languages that can be colorized are Python, Javascript, Java, and CSS.

#@+node:TomP.20200115200704.1: *3* Special Renderings
Special Renderings
==================

As stated above, the rendering pane renders body text as reStructuredText
by default, with all Leo directives removed. However, if the body text
starts with ``<`` (after removing directives), the body text is rendered as
html.

This plugin renders @md, @image, @jupyter, @html, @movie, @networkx and @svg nodes as follows:

**Note**: For @image, @movie and @svg nodes, either the headline or the first line of body text may
contain a filename.  If relative, the filename is resolved relative to Leo's load directory.

- ``@md`` renders the body text as markdown, as described above.

- ``@graphics-script`` executes the script in the body text in a context containing
  two predefined variables:

    - gs is the QGraphicsScene for the rendering pane.
    - gv is the QGraphicsView for the rendering pane.

  Using these variables, the script in the body text may create graphics to the rendering pane.

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
      
      Windows: file:///c:/Test/a_notebook.ipynb
      
      Linux:   file:///home/a_notebook.ipynb

- ``@movie`` plays the file as a movie.  @movie also works for music files.

- ``@networkx`` is non-functional at present.  It is intended to
  render the body text as a networkx graph.
  See http://networkx.lanl.gov/

- ``@svg`` renders the file as a (possibly animated!) svg (Scalable Vector Image).
  See http://en.wikipedia.org/wiki/Scalable_Vector_Graphics
  **Note**: if the first character of the body text is ``<`` after removing Leo directives,
  the contents of body pane is taken to be an svg image.
  
#@+node:TomP.20200115200833.1: *3* Acknowledgments
Acknowledgments
================

The original Viewrendered plugin was created by Terry Brown, and enhanced by Edward K. Ream. Jacob Peck added markdown support.

Viewrendered2 was created by Peter Mills, based on the viewrendered.py plugin.  It added the ability to render an entire RsT tree, the ability to display only the code blocks, and to execute one block of Python code in a node and insert any printed output into the node.  Thomas B. Passin enhanced Viewrendered2, adding the ability to change from RsT to Python and back within a node.

Viewrendered3 was created by Thomas B. Passin to provide VR2 functionality with Python 3/QT5 .  VR3 brings more enhancements to ReStructured Text and Markdown rendering.  Other functionality is the same as for the Viewrendered plugin.

Enhancements to the RsT stylesheets were adapted from Peter Mills' stylesheet.

#@-others

#@-<< vr3 docstring >>
"""
#pylint: disable=no-member,invalid-name

trace = False
    # This global trace is convenient.
#@+<< imports >>
#@+node:TomP.20191215195433.4: ** << imports >> (v3)
import json
import os

try:
    from urllib.request import urlopen
except ImportError:
    try:
        from urllib import urlopen  # for Python 2.7 (although no longer used).
    except ImportError:
        urllib = None

import leo.core.leoGlobals as g
try:
    import leo.plugins.qt_text as qt_text
    import leo.plugins.free_layout as free_layout
    from leo.core.leoQt import isQt5, QtCore, QtGui, QtWidgets#, QString
    from leo.core.leoQt import phonon, QtMultimedia, QtSvg, QtWebKitWidgets
    #from PyQt5.QtCore import pyqtSignal
except Exception:
    QtWidgets = False

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
# markdown support, non-vital
try:
    from markdown import markdown
    got_markdown = True
except ImportError:
    got_markdown = False
# nbformat (@jupyter) support, non-vital.
try:
    import nbformat
    from nbconvert import HTMLExporter
    # from traitlets.config import Config
except ImportError:
    nbformat = None

# for VR3.  t.b. passin
import sys
import os.path
import io
from io import StringIO

import shutil
from enum import Enum, auto

import webbrowser
from contextlib import redirect_stdout
from pygments import cmdline

try:
    QWebView = QtWebKitWidgets.QWebView
except Exception:
    QWebView = QtWidgets.QTextBrowser  # #1542.
#@-<< imports >>
#@+<< declarations >>
#@+node:TomP.20191231111412.1: ** << declarations >>
ZOOM_FACTOR = 1.2
CODE = 'code'
RST = 'rst'
REST = 'rest'
MD = 'md'
PYPLOT = 'pyplot'
PYTHON = 'python'

JAVASCRIPT = 'javascript'
JAVA = 'java'
C = 'c'
CSS = 'css'
RESPONSE = 'response'
TEXT = 'text'

VR3_TEMP_FILE = 'leo_rst_html.html'
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

RST_DEFAULT_STYLESHEET_NAME = 'vr3_rst.css'
MD_BASE_STYLESHEET_NAME = 'md_styles.css'

VR3_TOOLBAR_NAME = 'vr3-toolbar-label'

# For code rendering
LANGUAGES = (PYTHON, JAVASCRIPT, JAVA, CSS)
TRIPLEQUOTES = '"""'
TRIPLEAPOS = "'''"
RST_CODE_INTRO = '.. code::'
MD_CODE_FENCE = '```'

RST_INDENT = '    '

#@-<< declarations >>

asciidoctor_exec = shutil.which('asciidoctor')
asciidoc3_exec = shutil.which('asciidoc3')
pandoc_exec = shutil.which('pandoc')

#@+<< set BaseTextWidget >>
#@+node:TomP.20191215195433.5: ** << set BaseTextWidget >> (vr3)
if QtWidgets:
    try:
        BaseTextWidget = QtWebKitWidgets.QWebView
    except Exception:
        BaseTextWidget = QtWidgets.QTextBrowser
else:
    BaseTextWidget = None
#@-<< set BaseTextWidget >>
#@+<< define html templates >>
#@+node:TomP.20191215195433.6: ** << define html templates >> (vr3)
image_template = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head></head>
<body bgcolor="#fffbdc">
<img src="%s">
</body>
</html>
'''

# http://docs.mathjax.org/en/latest/start.html
latex_template = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-AMS-MML_HTMLorMML'>
    </script>
</head>
<body bgcolor="#fffbdc">
%s
</body>
</html>
'''
#@-<< define html templates >>
controllers = {}
    # Keys are c.hash(): values are PluginControllers (QWidget's).
layouts = {}
    # Keys are c.hash(): values are tuples (layout_when_closed, layout_when_open)

#@+others
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
    '''Return True if the plugin has loaded successfully.'''
    #global got_docutils
    if g.app.gui.guiName() != 'qt':
        return False
            # #1248.
    # if g.app.gui.guiName()
    if not QtWidgets or not g.app.gui.guiName().startswith('qt'):
        if (
            not g.unitTesting and
            not g.app.batchMode and
            g.app.gui.guiName() in ('browser', 'curses')  # EKR.
        ):
            g.es_print('viewrendered3 requires Qt')
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
    '''Return True if the VR pane is visible.'''
    pass
#@+node:TomP.20191215195433.11: *3* vr3.onCreate
def onCreate(tag, keys):
    c = keys.get('c')
    if not c:
        return
    provider = ViewRenderedProvider3(c)
    free_layout.register_provider(c, provider)
    if g.app.dock:
        # Instantiate immediately.
        viewrendered(event={'c': c})

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
    if g.unitTesting:
        return None # This just slows the unit tests.

    c = kw.get('c')
    flags = kw.get('flags') or 'rst'
    vr3 = viewrendered(event=kw)
    title = kw.get('short_title', '').strip()
    vr3.setWindowTitle(title)
    s = '\n'.join([
        title,
        '=' * len(title),
        '',
        kw.get('msg')
    ])
    vr3.show_dock_or_pane() # #1332.
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
    if g.app.dock:
        dock = vr3.leo_dock
        if not c.mFileName:
            # #1318 and #1332: Tricky init code for new windows.
            g.app.restoreWindowState(c)
            dock.hide()
            dock.raise_()
        return vr3
    #
    # Legacy code: add the pane to the splitter.
    layouts[h] = c.db.get('viewrendered_default_layouts', (None, None))
    vr3._ns_id = '_leo_viewrendered3' # for free_layout load/save
    vr3.splitter = splitter = c.free_layout.get_top_splitter()
    if splitter:
        vr3.store_layout('closed')
        sizes = split_last_sizes(splitter.sizes())
        ok = splitter.add_adjacent(vr3, 'bodyFrame', 'right-of')
        if not ok:
            splitter.insert(0, vr3)
        elif splitter.orientation() == QtCore.Qt.Horizontal:
            splitter.setSizes(sizes)
        vr3.adjust_layout('open')
    c.bodyWantsFocusNow()
    return vr3
#@+node:TomP.20191215195433.21: *3* g.command('vr3-hide')
@g.command('vr3-hide')
def hide_rendering_pane(event):
    '''Close the rendering pane.'''
    vr3 = getVr3(event)
    if not vr3: return

    c = event.get('c')
    if g.app.dock:
        if vr3.external_dock:
            return # Can't hide a top-level dock.
        dock = vr3.leo_dock
        if dock:
            dock.hide()
        return
    #
    # Legacy code.
    if vr3.pyplot_active:
        g.es_print('can not close vr3 pane after using pyplot')
        return
    vr3.store_layout('open')
    vr3.deactivate()
    vr3.deleteLater()

    def at_idle(c=c, _vr3=vr3):
        c = event.get('c')
        _vr3.adjust_layout('closed')
        c.bodyWantsFocusNow()

    QtCore.QTimer.singleShot(0, at_idle)
    h = c.hash()
    c.bodyWantsFocus()
    if vr3 == controllers.get(h):
        del controllers[h]
    else:
        g.trace('Can not happen: no controller for %s' % (c))
# Compatibility

close_rendering_pane = hide_rendering_pane
#@+node:TomP.20191215195433.22: *3* g.command('vr3-lock')
@g.command('vr3-lock')
def lock_rendering_pane(event):
    '''Lock the rendering pane.'''
    vr3 = getVr3(event)
    if not vr3: return

    if not vr3.locked:
        vr3.lock()
#@+node:TomP.20191215195433.23: *3* g.command('vr3-pause-play')
@g.command('vr3-pause-play-movie')
def pause_play_movie(event):
    '''Pause or play a movie in the rendering pane.'''
    vr3 = getVr3(event)
    if not vr3: return

    vp = vr3.vp
    if not vp:
        return
    f = vp.pause if vp.isPlaying() else vp.play
    f()
#@+node:TomP.20191215195433.24: *3* g.command('vr3-show')
@g.command('vr3-show')
def show_rendering_pane(event):
    '''Show the rendering pane.'''
    vr3 = getVr3(event)
    if not vr3: return

    vr3.show_dock_or_pane()
#@+node:TomP.20191215195433.25: *3* g.command('vr3-toggle')
@g.command('vr3-toggle')
def toggle_rendering_pane(event):
    '''Toggle the rendering pane.'''
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    if g.app.gui.guiName() != 'qt':
        return

    h = c.hash()
    controllers[h] = vr3 = controllers.get(h) if h else None
    if not vr3:
        vr3 = viewrendered(event)
        vr3.hide() # So the toggle below will work.

    if g.app.dock:
        if vr3.external_dock:
            return # Can't hide a top-level dock.
        dock = vr3.leo_dock
        if dock:
            f = dock.show if dock.isHidden() else dock.hide
            f()
            if not dock.isHidden():
                vr3.update(tag='view', keywords={'c': c, 'force': True})

    elif vr3.isHidden():
        show_rendering_pane(event)
    else:
        hide_rendering_pane(event)
#@+node:TomP.20191215195433.26: *3* g.command('vr3-unlock')
@g.command('vr3-unlock')
def unlock_rendering_pane(event):
    '''Pause or play a movie in the rendering pane.'''
    vr3 = getVr3(event)
    if not vr3: return

    if vr3.locked:
        vr3.unlock()
#@+node:TomP.20191215195433.27: *3* g.command('vr3-update')
@g.command('vr3-update')
def update_rendering_pane(event):
    '''Update the rendering pane'''
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
    """Execute code in a RsT or MS node or subtree."""
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
        g.es('=== %s: %s' % (type(e), e))
        return
    if not _html:
        return
    _html = g.toUnicode(_html)
    # Write to temp file
    c = vr3.c
    path = c.getNodePath(c.rootPosition())
    pathname = g.os_path_finalize_join(path, VR3_TEMP_FILE)
    with io.open(pathname, 'w', encoding='utf-8') as f:
        f.write(_html)
    webbrowser.open_new_tab(pathname)
#@+node:TomP.20200113230428.1: *3* g.command('vr3-lock-unlock-tree')
@g.command('vr3-lock-unlock-tree')
def lock_unlock_tree(event):
    """Toggle between lock(), unlock()."""
    vr3 = getVr3(event)
    if not vr3: return

    if vr3.lock_to_tree:
        vr3.lock()
    else:
        vr3.unlock()
#@+node:TomP.20191215195433.32: ** class ViewRenderedProvider3 (vr3)
class ViewRenderedProvider3:
    #@+others
    #@+node:TomP.20191215195433.33: *3* vr3.__init__
    def __init__(self, c):
        self.c = c
        # Careful: we may be unit testing.
        if hasattr(c, 'free_layout'):
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.register_provider(self)
    #@+node:TomP.20191215195433.34: *3* vr3.ns_provides
    def ns_provides(self):
        return [('Viewrendered3', '_leo_viewrendered3')]
    #@+node:TomP.20191215195433.35: *3* vr3.ns_provide
    def ns_provide(self, id_):
        global controllers, layouts
        if id_ == '_leo_viewrendered3':
            c = self.c
            vr3 = controllers.get(c.hash()) or ViewRenderedController3(c)
            h = c.hash()
            controllers[h] = vr3
            if not layouts.get(h):
                layouts[h] = c.db.get('viewrendered_default_layouts', (None, None))
            # return ViewRenderedController(self.c)
            return vr3
        return None
    #@-others
#@+node:TomP.20191215195433.36: ** class ViewRenderedController3 (QWidget)
class ViewRenderedController3(QtWidgets.QWidget):
    '''A class to control rendering in a rendering pane.'''
    #@+others
    #@+node:TomP.20191215195433.37: *3* vr3.ctor & helpers
    def __init__(self, c, parent=None):
        '''Ctor for ViewRenderedController class.'''
        self.c = c
        # Create the widget.
        super().__init__(parent)

        self.create_pane(parent)
        # Set the ivars.
        self.active = False
        self.badColors = []
        self.delete_callback = None
        self.gnx = None
        self.graphics_class = QtWidgets.QGraphicsWidget
        self.pyplot_canvas = None

        self.pyplot_imported = False
        self.gs = None # For @graphics-script: a QGraphicsScene
        self.gv = None # For @graphics-script: a QGraphicsView
        self.inited = False
        self.length = 0 # The length of previous p.b.
        self.locked = False

        self.pyplot_active = False
        self.scrollbar_pos_dict = {} # Keys are vnodes, values are positions.
        self.sizes = [] # Saved splitter sizes.
        self.splitter = None
        self.splitter_index = None # The index of the rendering pane in the splitter.
        self.title = None

        self.vp = None # The present video player.
        self.w = None # The present widget in the rendering pane.

        # For viewrendered3
        self.rst_html = ''
        self.code_only = False
        self.show_whole_tree = False
        self.execute_flag = False
        self.code_only = False
        self.lock_to_tree = False
        self.current_tree_root = None
        self.freeze = False

        # User settings.
        self.reloadSettings()
        self.node_changed = True

        # Init.
        self.create_dispatch_dict()
        self.activate()
        self.zoomed = False

    #@+node:TomP.20200104180310.1: *4* vr3 listen for keys
    def keyPressEvent(self, event):
        """Take actions on keypresses when the VR3 render pane has focus and a key is pressed. 
        
        A method of this name receives keystrokes for most or all QObject-descended objects.
        Currently, check only for <CNTRL-=> and <CONTROL-MINUS> events for zooming or unzooming
        the VR3 browser pane.
        """

        mod = ''
        modifiers = event.modifiers()
        bare_key = event.text()

        if modifiers and modifiers == QtCore.Qt.ControlModifier:
            mod = 'cntrl'

        if bare_key == '=' and mod == 'cntrl':
            self.zoomView()
        elif bare_key == '-' and mod == 'cntrl':
            self.shrinkView()
    #@+node:TomP.20191215195433.38: *4* vr3.create_dispatch_dict
    def create_dispatch_dict(self):
        pc = self
    #    VrC.create_dispatch_dict(self)

        # From viewrendered (i.e., VrC)
        pc = self
        pc.dispatch_dict = {
            'big': pc.update_rst,
            'html': pc.update_html,
            'graphics-script': pc.update_graphics_script,
            'image': pc.update_image,
            'md': pc.update_md,
            'movie': pc.update_movie,
            'networkx': pc.update_networkx,
            'rst': pc.update_rst,
            'pyplot': pc.update_pyplot,
            'svg': pc.update_svg,
            #'url': pc.update_url,
        }
    #@@c
        pc.dispatch_dict['rest'] = pc.dispatch_dict['rst']
        pc.dispatch_dict['markdown'] = pc.dispatch_dict['md']
    #@+node:TomP.20200303185005.1: *4* vr3.set_rst_stylesheet
    def set_rst_stylesheet(self):
        """Set rst stylesheet to default if none specified.
        
        A file location must start with 'file:///';. If
        a file does not exist for the path, use the default
        stylesheet.
        
        The default location is in leo/plugins/viewrendered3.
        
        VARIABLE USED
        self.rst_stylesheet -- The URL to the stylesheet.  Need not include
                               the "file:///", and must be an absolute path 
                               if it is a local file.  
                               
                               Set by @string vr3-rst-stylesheet.
        """

        # Stylesheet may already be specified by @setting vr3-rst-stylesheet.
        # If so, check if it exists.
        if self.rst_stylesheet:
            if self.rst_stylesheet.startswith('file:///'):
                pth = self.rst_stylesheet.split('file:///')[1]
                if os.path.exists(pth):
                    # Note that docutils must *not* have a leading 'file:///'
                    # This method changes '\' to '/' in the path if needed.
                    self.rst_stylesheet = g.os_path_finalize_join(pth)
                    return
                g.es('Specified VR3 stylesheet not found; using default')
            return

        # Default location
        # NOTE - for the stylesheet url we need to use forward slashes no matter
        # what OS is being used.  Apparently, the g.os_path methods do this.
        vr_style_dir = g.os_path_join(g.app.leoDir, 'plugins', 'viewrendered3')
        self.rst_stylesheet = g.os_path_join(vr_style_dir, RST_DEFAULT_STYLESHEET_NAME)
    #@+node:TomP.20200103171535.1: *4* vr3.set_md_stylesheet
    def set_md_stylesheet(self):
        """Verify or create css stylesheet for Markdown node.
        
        If there is no custom css stylesheet specified by self.md_stylesheet,
        check if there is one at the standard location.  If not, create
        a default stylesheet and write it to a file at that place.
        
        The default location is assumed to be at leo/plugins/viewrendered3.
        
        VARIABLE USED
        self.md_stylesheet -- The URL to the stylesheet.  Need not include
                               the "file:///", and must be an absolute path 
                               if it is a local file.  
                               
                               Set by @string vr3-md-stylesheet.  
        """

        # If no custom stylesheet specified, use standard one.
        if not self.md_stylesheet:
            # Look for the standard one
            vr_style_dir = g.os_path_join(g.app.leoDir, 'plugins', 'viewrendered3')
            style_path = g.os_path_join(vr_style_dir, MD_BASE_STYLESHEET_NAME)

            # If there is no stylesheet at the standard location, have Pygments 
            # generate a default stylesheet there.
            # Note: "cmdline" is a function imported from pygments
            if not os.path.exists(style_path):
                args = [cmdline.__name__, '-S', 'default', '-f', 'html']
                # pygments cmdline() writes to stdout; we have to redirect it to a file
                with io.open(style_path, 'w') as out:
                    with redirect_stdout(out):
                        cmdline.main(args)
                # Add some fine-tuning css
                with io.open(style_path, 'a') as out:
                    out.write(MD_STYLESHEET_APPEND)
            self.md_stylesheet = 'file:///' + style_path

    #@+node:TomP.20200104001436.1: *4* vr3.create_md_header
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
                               the "file:///" if it is a local file. A typical URL
                               is http://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_HTMLorMML
                               If the MathJax package has been downloaded to the local computer,
                               a typical (Windows) URL would be 
                               file:///D:/utility/mathjax/es5/tex-chtml.js
        self.md_header -- where the header string gets stored.
        """

        if self.md_math_output and self.mathjax_url:
            self.md_header = fr'''
    <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <link rel="stylesheet" type="text/css" href="{self.md_stylesheet}">
    <script type="text/javascript" src="{self.mathjax_url}"></script>
    </head>
    '''
        else:
            self.md_header = fr'''
    <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <link rel="stylesheet" type="text/css" href="{self.md_stylesheet}">
    </head>
    '''

    #@+node:TomP.20191215195433.39: *4* vr3.reloadSettings
    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        #self.auto_create = c.config.getBool('view-rendered-auto-create', False)
        #self.background_color = c.config.getColor('rendering-pane-background-color') or 'white'
        self.default_kind = c.config.getString('vr3-default-kind') or 'rst'
        self.external_dock = c.config.getBool('use-vr3-dock', default=False)
        self.rst_stylesheet = c.config.getString('vr3-rst-stylesheet') or ''

        self.math_output = c.config.getBool('vr3-math-output', default=False)
        self.mathjax_url = c.config.getString('vr3-mathjax-url') or ''
        self.rst_math_output = 'mathjax ' + self.mathjax_url

        self.set_rst_stylesheet()

        self.md_math_output = c.config.getBool('vr3-md-math-output', default=False)
        self.md_stylesheet = c.config.getString('vr3-md-stylesheet') or ''

        self.set_md_stylesheet()
        self.create_md_header()
    #@+node:TomP.20191215195433.40: *4* vr3.create_pane
    def create_pane(self, parent):
        '''Create the vr3 pane or dock.'''
        c = self.c
        dw = c.frame.top
        self.leo_dock = None # May be set below.
        if g.app.unitTesting:
            return
        # Create the inner contents.
        self.setObjectName('viewrendered3_pane')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.create_toolbar()
        if not g.app.dock:
            return
        # Allow the VR dock to move only in special circumstances.
        central_body = g.app.get_central_widget(c) == 'body'
        moveable = g.app.init_docks or central_body
        self.leo_dock = dock = g.app.gui.create_dock_widget(
            closeable=True, moveable=moveable, height=50, name='ViewRendered3')
        if central_body:
            # Create a stand-alone dockable area.
            dock.setWidget(self)
            dw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        else:
            # Split the body dock.
            # Removed per @ekr- see https://groups.google.com/forum/#!topic/leo-editor/AeHYnVqrQCU:
            #dw.leo_docks.append(dock)
            dock.setWidget(self)
            dw.splitDockWidget(dw.body_dock, dock, QtCore.Qt.Horizontal)
        if g.app.init_docks:
            dock.show()
    #@+node:TomP.20191215195433.42: *3* vr3.closeEvent
    def closeEvent(self, event):
        '''Close the vr3 window.'''
        self.deactivate()
    #@+node:TomP.20191215224043.1: *3* vr3.create_toolbar
    def create_toolbar(self):
        """Create toolbar and attach to the VR3 widget.
        
        Child widgets can be found using the findChild() method with the
        name of the child widget.  E.g.,
        
        label = self.findChild(QtWidgets.QLabel, 'vr3-toolbar-label')
        
        Note that "self" refers to the enclosing viewrendered3 instance.
        
        NAMES CREATED
        'vr3-toolbar-label' -- the toolbar label.
        """
        # pylint: disable=unnecessary-lambda

        # Ref: https://forum.qt.io/topic/52022/solved-how-can-i-add-a-toolbar-for-a-qwidget-not-qmainwindow
        # Ref: https://stackoverflow.com/questions/51459331/pyqt5-how-to-add-actions-menu-in-a-toolbar

        c = self.c
        _toolbar = QtWidgets.QToolBar('Menus')
        _options_button = QtWidgets.QPushButton("View Options")
        _options_button.setDefault(True)
        _toolbar.addWidget(_options_button)

        _default_type_button =  QtWidgets.QPushButton("Default Kind")
        _toolbar.addWidget(_default_type_button)

        #@+others
        #@+node:TomP.20191231135656.1: *4* Menu Creation Helpers
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
            self.c.k.simulateCommand('vr3-update')

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
            _action = QtWidgets.QAction(label, self, checkable=True)
            _action.triggered.connect(lambda: set_menu_var(menu_var_name, _action))
            menu.addAction(_action)

        def set_group_action(label, kind):
            """Add a QAction to a QT menu along with a GroupAction that coordinates the checked state.
            
            The triggered function sets the value of the self.default_kind variable.
            
            ARGUMENTS
            label -- a string containing the display label for the action.
            kind -- the kind of structure to be used by default (e.g., 'rst', 'md', 'text')
            
            RETURNS
            nothing.
            """

            _action = QtWidgets.QAction(label, self, checkable=True)
            _action.triggered.connect(lambda: set_default_kind(kind))
            group.addAction(_action)
            menu.addAction(_action)

        def set_default_kind(kind):
            self.default_kind = kind
            self.c.k.simulateCommand('vr3-update')
        #@+node:TomP.20191231140246.1: *4* Create Menus
        def set_tree_lock(checked):
            self.lock_to_tree = checked
            self.current_tree_root = self.c.p if checked else None

        def set_freeze(checked):
            self.freeze = checked

        menu = QtWidgets.QMenu()
        set_action("Entire Tree", 'show_whole_tree')
        _action = QtWidgets.QAction('Lock to Tree Root', self, checkable=True)
        _action.triggered.connect(lambda checked: set_tree_lock(checked))
        menu.addAction(_action)

        _action = QtWidgets.QAction('Freeze', self, checkable=True)
        _action.triggered.connect(lambda checked: set_freeze(checked))
        menu.addAction(_action)

        set_action("Code Only", 'code_only')
        _options_button.setMenu(menu)


        menu = QtWidgets.QMenu()
        group = QtWidgets.QActionGroup(self)
        set_group_action('RsT', RST)
        set_group_action('MD', MD)
        set_group_action('Text', TEXT)
        _default_type_button.setMenu(menu)



        #@+node:TomP.20191231135753.1: *4* Finish Toolbar
        _export_button = QtWidgets.QPushButton("Export")
        _export_button.setDefault(True)
        _export_button.clicked.connect(lambda: c.k.simulateCommand('vr3-export-rst-html'))
        _toolbar.addWidget(_export_button)

        _reload_button = QtWidgets.QPushButton("Reload")
        _reload_button.setDefault(True)
        _reload_button.clicked.connect(lambda: c.k.simulateCommand('vr3-update'))
        _toolbar.addWidget(_reload_button)

        _execute_button = QtWidgets.QPushButton('Execute')
        _execute_button.setDefault(True)
        _execute_button.clicked.connect(lambda: c.k.simulateCommand('vr3-execute'))
        _toolbar.addWidget(_execute_button)

        #_hide_button = QtWidgets.QPushButton('Hide')
        #_hide_button.clicked.connect(lambda: self.w.hide())
        #_toolbar.addWidget(_hide_button)

        # _label = QtWidgets.QLabel('<b>ViewRendered3</b>')
        # _label.setObjectName(VR3_TOOLBAR_NAME)
        # _label.setTextFormat(1)
        # _toolbar.addWidget(_label)

        self.layout().setMenuBar(_toolbar)
        self.vr3_toolbar = _toolbar
        #@-others
    #@+node:TomP.20191215195433.43: *3* vr3.contract & expand
    def contract(self):
        #VrC.contract(self)
        self.change_size(-100)

    def expand(self):
        #VrC.expand(self)
        self.change_size(100)

    def change_size(self, delta):
    #    VrC.change_size(self, delta)

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
    #@+node:TomP.20191215195433.44: *3* vr3.activate
    def activate(self):
        '''Activate the vr3-window.'''
        #VrC.activate(self)

        pc = self
        if pc.active: return
        pc.inited = True
        pc.active = True
        g.registerHandler('select2', pc.update)
        g.registerHandler('idle', pc.update)
    #@+node:TomP.20191215195433.45: *3* vr3.deactivate
    def deactivate(self):
        '''Deactivate the vr3 window.'''
        #VrC.deactivate(self)

        pc = self
        # Never disable the idle-time hook: other plugins may need it.
        g.unregisterHandler('select3', pc.update)
        g.unregisterHandler('idle', pc.update)
        pc.active = False
    #@+node:TomP.20191215195433.46: *3* vr3.lock/unlock
    def lock(self):
        '''Lock the vr3 pane to the current node .'''
        #g.note('rendering pane locked')
        self.lock_to_tree = True
        self.current_tree_root = self.c.p

    def unlock(self):
        '''Unlock the vr3 pane.'''
        #g.note('rendering pane unlocked')
        self.lock_to_tree = False
        self.current_tree_root = None

    #@+node:TomP.20191215195433.47: *3* vr3.set_html
    def set_html(self, s, w):
        '''Set text in w to s, preserving scroll position.'''
        c = self.c
        # Find path relative to this file.  Needed as the base of relative
        # URLs, e.g., image or included files.
        path = c.getNodePath(c.p)
        s = g.toUnicode(s)
        url_base = QtCore.QUrl('file:///' + path + '/')
        try:
            # A QWebView.
            w.setHtml(s, url_base)
        except Exception:
            # A QTextBrowser.
            w.setHtml(s)  # #1543.
        w.show()
    #@+node:TomP.20191215195433.48: *3* vr3.underline
    def underline(self, s):
        '''Generate rST underlining for s.'''
        #VrC.underline(self, s)

        ch = '#'
        n = max(4, len(g.toEncodedString(s, reportErrors=False)))
        # return '%s\n%s\n%s\n\n' % (ch*n,s,ch*n)
        return '%s\n%s\n\n' % (s, ch * n)
    #@+node:TomP.20191231110143.1: *3* vr3.zoomView

    def zoomView(self):
        try:
            w = self.qwev
        except Exception:
            return

        _zf = w.zoomFactor()
        w.setZoomFactor(_zf * ZOOM_FACTOR)
    #@+node:TomP.20191231111540.1: *3* vr3.shrinkView
    def shrinkView(self):
        try:
            w = self.qwev
        except NameError:
            return

        _zf = w.zoomFactor()
        w.setZoomFactor(_zf / ZOOM_FACTOR)
    #@+node:TomP.20191215195433.49: *3* vr3.update & helpers
    # Must have this signature: called by leoPlugins.callTagHandler.
    def update(self, tag, keywords):
        '''Update the vr3 pane. Called at idle time.
        
        If the VR3 variable "freeze" is True, do not update.
        '''

        if self.freeze: return
        pc = self
        p = pc.c.p
        if pc.lock_to_tree:
            _root = pc.current_tree_root or p
        else:
            _root = p

        if tag in ('show-scrolled-message'):
            # If we are called as a "scrolled message" - usually for display of
            # docstrings.  keywords will contain the RsT to be displayed.
            _kind = keywords.get('flags', 'rst')
            keywords['tag'] = tag
        else:
            _kind = pc.get_kind(p) or self.default_kind
        f = pc.dispatch_dict.get(_kind)
        if f in (pc.update_rst, pc.update_md):  # EKR.
             self.show_toolbar()
        else:
            self.hide_toolbar()
        if self.locked:
            return

        if pc.must_update(keywords):
            # Suppress updates until we change nodes.
            pc.node_changed = pc.gnx != p.v.gnx
            pc.gnx = p.v.gnx
            pc.length = len(p.b) # not s

            # Remove Leo directives.
            s = keywords.get('s') if 's' in keywords else p.b
            s = pc.remove_directives(s)

            # Use plain text if we are hidden.
            # This avoids annoying messages with rst.
            dock = pc.leo_dock or pc
            if dock.isHidden():
                w = pc.ensure_text_widget()
                w.setPlainText(s)
                return

            # For rst, md handler
            self.rst_html = ''

            # Dispatch based on the computed kind.
            kind = keywords.get('flags') if 'flags' in keywords else _kind
            if not kind or kind == TEXT:
                # Just display plain text.
                w = pc.ensure_text_widget()
                w.setPlainText(s)
                w.show()
                return

            _tree = []
            if tag in ('show-scrolled-message'):
                # This branch is for rendering docstrings, help-for-command messages,
                # etc.  Called from qt_gui.py.
                # In case Leo node elements get mixed into the message, remove them:
                txt = keywords.get('s', '')
                lines = txt.split('\n')
                keywords['s'] = '\n'.join([l for l in lines if not l.startswith('#@')])
            else:
                # This branch is for rendering nodes and subtrees.
                try:
                    rootcopy = _root.copy()
                    _tree = [rootcopy]
                except UnboundLocalError as e:
                    g.es('=======', tag, e)
                    return
            if kind in (MD, RST, REST) and _tree and self.show_whole_tree:
                _tree.extend(rootcopy.subtree())
            f = pc.dispatch_dict.get(kind)
            if not f:
                g.trace('no handler for kind: %s' % kind)
                f = pc.update_rst
            if kind in (MD, RST, REST):
                f(_tree, keywords)
            else:
                f(s, keywords)
        else:
            # Save the scroll position.
            w = pc.w
            if w.__class__ == QtWidgets.QTextBrowser:
                # 2011/07/30: The widget may no longer exist.
                try:
                    sb = w.verticalScrollBar()
                    pc.scrollbar_pos_dict[p.v] = sb.sliderPosition()
                except Exception:
                    g.es_exception()
                    pc.deactivate()
    #@+node:TomP.20191215195433.50: *4* vr3.create_base_text_widget
    def create_base_text_widget(self):
        '''Create a QWebView or a QTextBrowser.'''
        c = self.c
        w = BaseTextWidget()
        n = c.config.getInt('qweb-view-font-size')
        if n:
            try:
                # BaseTextWidget is a QWebView.
                settings = w.settings()
                settings.setFontSize(settings.DefaultFontSize, n)
            except AttributeError:
                # BaseTextWidget is a QTextBrowser.
                pass
        return w
    #@+node:TomP.20191215195433.51: *4* vr3.embed_widget & helper
    def embed_widget(self, w, delete_callback=None):
        '''Embed widget w in the free_layout splitter.'''
        #VrC.embed_widget(self, w, delete_callback=None)

        pc = self; c = pc.c #X ; splitter = pc.splitter
        pc.w = w
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeItem(layout.itemAt(0))
        self.layout().addWidget(w)
        w.show()
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
            w.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
    #@+node:TomP.20191215195433.52: *5* vr3.setBackgroundColor
    def setBackgroundColor(self, colorName, name, w):
        '''Set the background color of the vr3 pane.'''
        if 0: # Do not do this! It interferes with themes.
            pc = self
            if not colorName: return
            styleSheet = 'QTextEdit#%s { background-color: %s; }' % (name, colorName)
            if QtGui.QColor(colorName).isValid():
                w.setStyleSheet(styleSheet)
            elif colorName not in pc.badColors:
                pc.badColors.append(colorName)
                g.warning('invalid body background color: %s' % (colorName))
    #@+node:TomP.20191215195433.53: *4* vr3.must_update
    def must_update(self, keywords):
        '''Return True if we must update the rendering pane.'''
        #_must_update = VrC.must_update(self, keywords)
        # if _must_update and self.w:
            # # Hide the old widget so it won't keep us from seeing the new one.
            # self.w.hide()
        # return _must_update

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
        elif len(p.b) != pc.length:
            if pc.get_kind(p) in ('html', 'pyplot'):
                pc.length = len(p.b)
                _must_update = False # Only update explicitly.
            _must_update = True
        # This trace would be called at idle time.
            # g.trace('no change')
        else:
            _must_update = False

        if _must_update and self.w:
            # Hide the old widget so it won't keep us from seeing the new one.
            self.w.hide()
        #g.es('===', _must_update)
        return _must_update

    #@+node:TomP.20191215195433.54: *4* vr3.update_asciidoc & helpers
    def update_asciidoc(self, s, keywords):
        '''Update asciidoc in the vr3 pane.'''
        #VrC.pdate_asciidoc(self, s, keywords)

        global asciidoctor_exec, asciidoc3_exec
        pc = self
        # Do this regardless of whether we show the widget or not.
        w = pc.ensure_text_widget()
        assert pc.w
        if s:
            pc.show()
        if asciidoctor_exec or asciidoc3_exec:
            try:
                s2 = self.convert_to_asciidoctor(s)
                self.set_html(s2,w)
                return
            except Exception:
                g.es_exception()
        self.update_rst(s,keywords)
    #@+node:TomP.20191215195433.55: *5* vr3.make_asciidoc_title
    def make_asciidoc_title(self, s):
        '''Generate an asciiidoc title for s.'''
        line = '#' * (min(4, len(s)))
        return f"{line}\n{s}\n{line}\n\n"
    #@+node:TomP.20191215195433.56: *5* vr3.convert_to_asciidoctor
    def convert_to_asciidoctor(self, s):
        '''Convert s to html using the asciidoctor or asciidoc processor.'''
        pc = self
        c, p = pc.c, pc.c.p
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        if pc.title:
            s = pc.make_asciidoc_title(pc.title) + s
            pc.title = None
        s = pc.run_asciidoctor(s)
        return g.toUnicode(s)
    #@+node:TomP.20191215195433.57: *5* vr3.run_asciidoctor
    def run_asciidoctor(self, s):
        """
        Process s with asciidoctor or asciidoc3.
        return the contents of the html file.
        The caller handles all exceptions.
        """
        global asciidoctor_exec, asciidoc3_exec
        assert asciidoctor_exec or asciidoc3_exec, g.callers()
        home = g.os.path.expanduser('~')
        i_path = g.os_path_finalize_join(home, 'vr3_input.adoc')
        o_path = g.os_path_finalize_join(home, 'vr3_output.html')
        # Write the input file.
        with open(i_path, 'w') as f:
            f.write(s)
        # Call the external program to write the output file.
        prog = 'asciidoctor' if asciidoctor_exec else 'asciidoc3'
        command = f"{prog} {i_path} -b html5 -o {o_path}"
            # The -e option deletes css.
        g.execute_shell_commands(command)
        # Read the output file and return it.
        with open(o_path, 'r') as f:
            return f.read()
      
    #@+node:TomP.20191215195433.58: *4* vr3.update_graphics_script
    def update_graphics_script(self, s, keywords):
        '''Update the graphics script in the vr3 pane.'''
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
            w = pc.gv.viewport() # A QWidget
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
        '''Update html in the vr3 pane.'''
        pc = self
        c = pc.c
        if pc.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert(w == pc.w)
        else:
            w = pc.w
        if isQt5:
            w.hide() # This forces a proper update.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.60: *4* vr3.update_image
    def update_image(self, s, keywords):
        '''Update an image in the vr3 pane.
        
        The path to the file can be an absolute or relative file path,
        or an http: URL.  It must be the first line in the body.
        File URLs must not start with "file:".
        '''

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
        else: #file URL
            ok, path = pc.get_fn(fn, '@image')

        if not ok:
            w = pc.ensure_text_widget()
            w.setPlainText('@image: file not found: %s' % (path))
            return

        if not is_url:
            path, fname = os.path.split(path)
            path = path.replace('\\', '/') + '/'
        else:
            fname = path
            path = ''

        template = image_template % (fname)
        # Only works in Python 3.x.
        template = g.adjustTripleString(template, pc.c.tab_width).strip()
            # Sensitive to leading blank lines.

        w = pc.ensure_web_widget()
        pc.show()
        # For file URLs, we need to give a base URL to the file system as the 2nd param.
        # Otherwise the QT widget will not allow a file:/// location.
        w.setHtml(template, QtCore.QUrl(path))
        w.show()
    #@+node:TomP.20191215195433.61: *4* vr3.update_jupyter & helper
    update_jupyter_count = 0

    def update_jupyter(self, s, keywords):
        '''Update @jupyter node in the vr3 pane.'''
        pc = self
        c = pc.c
        if pc.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert(w == pc.w)
        else:
            w = pc.w
        s = self.get_jupyter_source(c)
        if isQt5:
            w.hide() # This forces a proper update.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.62: *5* vr3.get_jupyter_source
    def get_jupyter_source(self, c):
        '''Return the html for the @jupyer node.'''
        body = c.p.b.lstrip()
        if body.startswith('<'):
            # Assume the body is html.
            return body
        if body.startswith('{'):
            # Leo 5.7.1: Allow raw JSON.
            s = body
        else:
            url = g.getUrlFromNode(c.p)
            if not url:
                return ''
            if not nbformat:
                return 'can not import nbformt to render url: %r' % url
            try:
                s = urlopen(url).read().decode()
            except Exception:
                return 'url not found: %s' % url
        try:
            nb = nbformat.reads(s, as_version=4)
            e = HTMLExporter()
            (s, junk_resources) = e.from_notebook_node(nb)
        except nbformat.reader.NotJSONError:
            pass # Assume the result is html.
        return s
    #@+node:TomP.20191215195433.63: *4* vr3.update_latex & helper
    def update_latex(self, s, keywords):
        '''Update latex in the vr3 pane.'''
        import sys
        pc = self
        c = pc.c
        if sys.platform.startswith('win'):
            g.es_print('latex rendering not ready for Python 3')
            w = pc.ensure_text_widget()
            pc.show()
            w.setPlainText(s)
            c.bodyWantsFocusNow()
            return
        if pc.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert(w == pc.w)
        else:
            w = pc.w
        w.hide() # This forces a proper update.
        s = self.create_latex_html(s)
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.64: *5* vr3.create_latex_html
    def create_latex_html(self, s):
        '''Create an html page embedding the latex code s.'''
        c = self.c
        # pylint: disable=deprecated-method
        try:
            import html
            escape = html.escape
        except AttributeError:
            import cgi
            escape = cgi.escape
        html_s = escape(s)
        template = latex_template % (html_s)
        template = g.adjustTripleString(template, c.tab_width).strip()
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
            s = node_list[0].b
            w.setPlainText(s)

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
        sm = StateMachine(self)

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
                header = node.h or ''
                if header.startswith('@'):
                    fields = header.split()
                    headline = ' '.join(fields[1:]) if len(fields) > 1 else header[1:]
                else:
                    headline = header
                headline_str = '#' + headline
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
            environment = {'c': c, 'g': g, 'p': c.p} # EKR: predefine c & p.
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

        ext = ['fenced_code', 'codehilite']

        try:
            s = markdown(result, extensions=ext) # s will be an encoded byte attay
        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                _html = 'MD error:\n%s\n\n%s' % (msg, s)
                return _html

        _html = self.md_header + s
        return _html
        #@-others
    #@+node:TomP.20191215195433.67: *4* vr3.update_movie
    movie_warning = False

    def update_movie(self, s, keywords):
        '''Update a movie in the vr3 pane.'''
        # pylint: disable=maybe-no-member
            # 'PyQt4.phonon' has no 'VideoPlayer' member
            # 'PyQt4.phonon' has no 'VideoCategory' member
            # 'PyQt4.phonon' has no 'MediaSource' member
        pc = self
        ok, path = pc.get_fn(s, '@movie')
        if not ok:
            w = pc.ensure_text_widget()
            w.setPlainText('Not found: %s' % (path))
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
        if QtMultimedia:
            url= QtCore.QUrl.fromLocalFile(path)
            content= QtMultimedia.QMediaContent(url)
            pc.vp = vp = QtMultimedia.QMediaPlayer()
            vp.setMedia(content)
            # Won't play .mp4 files: https://bugreports.qt.io/browse/QTBUG-32783
            vp.play()
        else:
            pc.vp = vp = phonon.VideoPlayer(phonon.VideoCategory)
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
        '''Update a networkx graphic in the vr3 pane.'''
        pc = self
        w = pc.ensure_text_widget()
        w.setPlainText('') # 'Networkx: len: %s' % (len(s)))
        pc.show()
    #@+node:TomP.20191215195433.69: *4* vr3.update_pandoc & helpers
    def update_pandoc(self, s, keywords):
        '''
        Update an @pandoc in the vr3 pane.
        
        There is no such thing as @language pandoc,
        so only @pandoc nodes trigger this code.
        '''
        global pandoc_exec
        pc = self
        w = pc.ensure_text_widget()
        assert pc.w
        if s:
            pc.show()
        if pandoc_exec:
            try:
                s2 = self.convert_to_pandoc(s)
                self.set_html(s2,w)
            except Exception:
                g.es_exception()
            return
        self.update_rst(s,keywords)
    #@+node:TomP.20191215195433.70: *5* vr3.convert_to_pandoc
    def convert_to_pandoc(self, s):
        '''Convert s to html using the asciidoctor or asciidoc processor.'''
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
        i_path = g.os_path_finalize_join(home, 'vr3_input.pandoc')
        o_path = g.os_path_finalize_join(home, 'vr3_output.html')
        # Write the input file.
        with open(i_path, 'w') as f:
            f.write(s)
        # Call pandoc to write the output file.
        command = f"pandoc {i_path} -t html5 -o {o_path}"
            # --quiet does no harm.
        g.execute_shell_commands(command)
        # Read the output file and return it.
        with open(o_path, 'r') as f:
            return f.read()
    #@+node:TomP.20191215195433.72: *4* vr3.update_pyplot
    def update_pyplot(self, s, keywords):
        '''Get the pyplot script at c.p.b and show it.'''
        c = self.c
        if not self.pyplot_imported:
            self.pyplot_imported = True
            backend = g.os_path_finalize_join(
                g.app.loadDir, '..', 'plugins', 'pyplot_backend.py')
            if g.os_path_exists(backend):
                try:
                    # The order of these statements is important...
                    import matplotlib
                    matplotlib.use('module://leo.plugins.pyplot_backend')
                except ImportError:
                    g.trace('===== FAIL: pyplot.backend')
            else:
                g.trace('===== MISSING: pyplot.backend')
        try:
            import matplotlib # Make *sure* this is imported.
            import matplotlib.pyplot as plt
            import numpy as np
            import matplotlib.animation as animation
            plt.ion() # Automatically set interactive mode.
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
        self.pyplot_active = True
            # pyplot will throw RuntimeError if we close the pane.
        c.executeScript(
            event=None,
            args=None, p=None,
            script=c.p.b, #None,
            useSelectedText=False,
            define_g=True,
            define_name='__main__',
            silent=False,
            namespace=namespace,
            raiseFlag=False,
            runPyflakes=False, # Suppress warnings about pre-defined symbols.
        )
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.73: *4* vr3.update_rst & helpers
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
                s = keywords.get('s', '')
            else:
                s = node_list[0].b
                s = self.remove_directives(s)
            isHtml = s and s[0] == '<'
            self.rst_html = ''
            if s and isHtml:
                h = s
            else:
                h = self.convert_to_html(node_list, s)
            if h:
                self.set_html(h, w)
        else:
            s = node_list[0].b
            w.setPlainText(s)
    #@+node:TomP.20191215195433.74: *5* vr3.convert_to_html
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
                s, headline_str = self.make_rst_headline(node, s)
                # Process node's entire body text to handle @language directives
                sproc, codelines = self.process_rst_node(s)
                result += sproc
                if codelines:
                    codelist.extend(codelines)

        # Execute code blocks; capture and insert execution results.
        # This means anything written to stdout or stderr.
        if self.execute_flag and codelist:
            code = '\n'.join(codelist)
            c = self.c
            environment = {'c': c, 'g': g, 'p': c.p} # EKR: predefine c & p.
            execution_result, err_result = self.exec_code(code, environment)

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
            args['stylesheet_path'] = '{}'.format(self.rst_stylesheet)
            args['embed_stylesheet'] = True

        if self.math_output:
            if self.mathjax_url:
                args['math_output'] = self.rst_math_output
            else:
                g.es('VR3 - missing URL for MathJax')

        # Call docutils to get the string.
        html = None
        if result.strip():
            try:
                html = publish_string(result, writer_name='html', settings_overrides=args)
            except SystemMessage as sm:
                msg = sm.args[0]
                if 'SEVERE' in msg or 'FATAL' in msg:
                    result = 'RST error:\n%s\n\n%s' % (msg, result)

            self.rst_html = html
            return html

        return ''
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

            _fields = line.split('.. code::')
            if len(_fields) > 1:
                _lang = _fields[1].strip()
            else:
                _lang = PYTHON # Standard RsT default.
            _tag = CODE if _lang in (PYTHON,) else TEXT

            return _lang, _tag
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
        _skipthis = False

        _got_language = False
        _in_rst_block = False
        _in_code_block = False
        _in_quotes = False
        _quotes_type = None

        #c = self.c
        #environment = {'c': c, 'g': g, 'p': c.p} # EKR: predefine c & p.

        for i, line in enumerate(lines):
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
                    _quotes_type = TRIPLEAPOS if line.find(TRIPLEAPOS) >=0 else None
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
            # However, ignore these markers if we are in a code block and
            # and also within a quoted section.
            if not (_in_code_block and _in_quotes):
                if line.rstrip() == '@':
                    _skipthis = True
                    continue
                elif line.rstrip() == '@c':
                    _skipthis = False
                    continue
                if _skipthis:
                    continue
            #@-<< handle_ats >>
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
                if _numlines < i + 2: continue # Reached the end of the node.

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
                        elif lines[j + 1][0] not in (' ', '\t'):
                            _last_code_line_num = j
                            break
            elif line.find('@language') == 0 and not _in_quotes:
                _got_language = True
                _in_rst_block = False
                _in_code_block = True
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
    #@+node:TomP.20200107232540.1: *5* vr3.make_rst_headline
    #@@language python
    def make_rst_headline(self, p, s):
        """Turn node's title into a headline and add to front of text.
        
        ARGUMENTS
        p -- the node being processed.
        s -- a string
        
        RETURNS
        a tuple (s, _headline), where the string _headline + s
        """

        _underline = ''
        _headline_str = ''
        if p.h:
            if p.h.startswith('@'):
                _headline = p.h.split()
                if len(_headline) > 1:
                    _headline = _headline[1:]
                _headline_str = ' '.join(_headline)
            else:
                _headline_str = p.h
            _headline_str.replace('\\', '\\\\')
            _underline = '='*len(_headline_str)

        # Don't duplicate node heading if the body already has it
        # Assumes that 1st two lines are a heading if
        # node headline == body's first line.
        body_lines = p.b.split('\n', 1)
        if _headline_str == body_lines[0].strip():
            return s, _headline_str

        s = f'{_headline_str}\n{_underline}\n\n{s}'
        return s, _headline_str
    #@+node:TomP.20191215195433.77: *4* vr3.update_svg
    # http://doc.trolltech.com/4.4/qtsvg.html
    # http://doc.trolltech.com/4.4/painting-svgviewer.html

    def update_svg(self, s, keywords):
        #VrC.update_svg(self, s, keywords)

        pc = self
        if pc.must_change_widget(QtSvg.QSvgWidget):
            w = QtSvg.QSvgWidget()
            pc.embed_widget(w)
            assert(w == pc.w)
        else:
            w = pc.w
        if s.strip().startswith('<'):
            # Assume it is the svg (xml) source.
            s = g.adjustTripleString(s, pc.c.tab_width).strip()
                # Sensitive to leading blank lines.
            s = g.toEncodedString(s)
            pc.show()
            w.load(QtCore.QByteArray(s))
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
        #VrC.update_url(self, s, keywords)

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
            g.trace('ignore',s)
            w = pc.ensure_text_widget()
            pc.show()
            w.setPlainText('')
    #@+node:TomP.20191215195433.79: *4* vr3.utils for update helpers...
    #@+node:TomP.20191215195433.80: *5* vr3.ensure_text_widget
    def ensure_text_widget(self):
        '''Swap a text widget into the rendering pane if necessary.
        
        Cannot delegate to viewrendered version.'''

        c, pc = self.c, self
        if pc.must_change_widget(QtWidgets.QTextBrowser):
            # Instantiate a new QTextBrowser.
            w = QtWidgets.QTextBrowser()

            def handleClick(url, w=w):
                import leo.plugins.qt_text as qt_text
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

            pc.embed_widget(w) # Creates w.wrapper
            assert(w == pc.w)
        return pc.w
    #@+node:TomP.20191227101625.1: *5* vr3.ensure_web_widget
    def ensure_web_widget(self):
        '''Swap a webengineview widget into the rendering pane if necessary.'''
        pc = self
        if pc.must_change_widget(QWebView):
            try:
                w = self.qwev
            except Exception:
                # Instantiate and cache a new QWebView.
                w = QWebView() # For QT5, this is actually a QWebEngineView
                #w.page().setZoomFactor(1.0)
                self.qwev = w
            pc.embed_widget(w) # Creates w.wrapper
            assert(w == pc.w)

        return pc.w
    #@+node:TomP.20191215195433.81: *5* vr3.get_kind
    def get_kind(self, p):
        """Return the proper rendering kind for node p."""

        #  #1287: Honor both kind of directives node by node.
        for p in p.self_and_parents(p):
            language = self.get_language(p)
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
            word = h[1: i].lower().strip()
            if word in self.dispatch_dict:
                return word
        # Look for @language directives.
        # Warning: (see #344): don't use c.target_language as a default.
        colorizer = c.frame.body.colorizer
        return colorizer.findFirstValidAtLanguageDirective(p.copy())
    #@+node:TomP.20191215195433.82: *5* vr3.get_fn
    def get_fn(self, s, tag):
        pc = self
        c = pc.c
        fn = s or c.p.h[len(tag):]
        fn = fn.strip()
        # Similar to code in g.computeFileUrl
        if fn.startswith('~'):
            # Expand '~' and handle Leo expressions.
            fn = fn[1:]
            fn = g.os_path_expanduser(fn)
            fn = g.os_path_expandExpression(fn, c=c)
            fn = g.os_path_finalize(fn)
        else:
            # Handle Leo expressions.
            fn = g.os_path_expandExpression(fn, c=c)
            # Handle ancestor @path directives.
            if c and c.openDirectory:
                base = c.getNodePath(c.p)
                fn = g.os_path_finalize_join(c.openDirectory, base, fn)
            else:
                fn = g.os_path_finalize(fn)

        ok = g.os_path_exists(fn)
        return ok, fn

    #@+node:TomP.20191215195433.83: *5* vr3.get_url
    def get_url(self, s, tag):
        #VrC.get_url(self, s, tag)

        p = self.c.p
        url = s or p.h[len(tag):]
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
                word = li[1: i]
                if word in _directives:
                    continue
            result.append(li)
        return ''.join(result)
    #@+node:TomP.20200112233701.1: *5* vr3.execute_code
    # Modified from VR2
    def exec_code(self, code, environment):
        """Execute the code, capturing the output in stdout and stderr."""
        saveout = sys.stdout # save stdout
        saveerr = sys.stderr
        sys.stdout = bufferout = StringIO()
        sys.stderr = buffererr = StringIO()
        except_err = ''

        try:
            exec(code, environment)
        except Exception as e:
            # print &gt;&gt; buffererr, traceback.format_exc()
            # buffererr.flush() # otherwise exception info appears too late
            # g.es('Viewrendered traceback:\n', sys.exc_info()[1])
            g.es('Viewrendered2 exception')
            g.es_exception()
            except_err = f'{type(e).__name__}: {str(e)}\n'
        # Restore stdout, stderr
        finally:
            sys.stdout = saveout # was sys.__stdout__
            sys.stderr = saveerr # restore stderr

        return bufferout.getvalue(), buffererr.getvalue() + except_err
    #@+node:TomP.20191215195433.86: *3* vr3.adjust_layout (legacy only)
    def adjust_layout(self, which):
        #VrC.adjust_layout(self, which)

        global layouts
        c = self.c
        splitter = self.splitter
        deflo = c.db.get('viewrendered_default_layouts', (None, None))
        loc, loo = layouts.get(c.hash(), deflo)
        if which == 'closed' and loc and splitter:
            splitter.load_layout(loc)
        elif which == 'open' and loo and splitter:
            splitter.load_layout(loo)
    #@+node:TomP.20191215195433.87: *3* vr3.show_dock_or_pane
    def show_dock_or_pane(self):

        c, vr = self.c, self
        if g.app.dock:
            dock = vr.leo_dock
            if dock:
                dock.show()
                dock.raise_()
                    # #1230.
        else:
            vr.activate()
            vr.show()
            vr.adjust_layout('open')
        c.bodyWantsFocusNow()
    #@+node:TomP.20191215195433.88: *3* vr3.store_layout
    def store_layout(self, which):
        #VrC.store_layout(self, which)

        global layouts
        c = self.c; h = c.hash()
        splitter = self.splitter
        deflo = c.db.get('viewrendered_default_layouts', (None, None))
        (loc, loo) = layouts.get(c.hash(), deflo)
        if which == 'closed' and splitter:
            loc = splitter.get_saveable_layout()
            loc = json.loads(json.dumps(loc))
            layouts[h] = loc, loo
        elif which == 'open' and splitter:
            loo = splitter.get_saveable_layout()
            loo = json.loads(json.dumps(loo))
            layouts[h] = loc, loo
        c.db['viewrendered_default_layouts'] = layouts[h]
    #@+node:TomP.20191226054120.1: *3* vr3.show_toolbar
    def show_toolbar(self):
        try:
            _toolbar = self.vr3_toolbar
        except RuntimeError as e:
            g.es(f'show_toolbar(): {type(e)}: {e}')
            return

        if _toolbar and _toolbar.isHidden():
            try:
                _toolbar.setVisible(True)
            except RuntimeError as e:
                g.es('show_toolbar(): cannot setVisible(): %s: %s' % (type(e), e))
    #@+node:TomP.20191226055702.1: *3* vr3.hide_toolbar
    def hide_toolbar(self):
        _toolbar = self.vr3_toolbar
        if not _toolbar: return

        try:
            _toolbar.setVisible(False)
        except Exception as e:
            g.es('=== hide_toolbar(): %s: %s' % (type(e), e))
    #@+node:TomP.20200106204157.1: *3* vr3.get_toolbar_label
    def get_toolbar_label(self):
        """Return the toolbar label object."""
        
        return self.findChild(QtWidgets.QLabel, VR3_TOOLBAR_NAME)
    #@-others
#@+node:TomP.20200213170204.1: ** class State
class State(Enum):
    BASE = auto()
    AT_LANG_CODE = auto()
    FENCED_CODE = auto()
    IN_SKIP = auto()
    TO_BE_COMPUTED = auto()

#@+node:TomP.20200213170314.1: ** class Action
class Action:
    @staticmethod
    def new_chunk(sm, line, tag):
        """ Add chunk to chunk list, create new chunk.
        
        ARGUMENTS
        sm -- a StateMachine instance.
        line -- the line of text to be processed.
        tag -- the current tag for the chunk.
        """

        sm.chunk_list.append(sm.current_chunk)
        marker, tag, _lang = StateMachine.get_marker(None, line)
        sm.current_chunk = Chunk(tag, sm.structure, _lang)

    @staticmethod
    def add_line(sm, line, tag=None):
        sm.current_chunk.add_line(line)

    @staticmethod
    def no_action(sm, line, tag=None):
        pass
#@+node:TomP.20200213170250.1: ** class Marker
class Marker(Enum):
    """
    For indicating markers in a text line that characterize their purpose, like "@language".
    """
    AT_LANGUAGE_MARKER = auto()
    MD_FENCE_LANG_MARKER = auto() # fence token with language; e.g. ```python
    MD_FENCE_MARKER = auto() # fence token with no language
    MARKER_NONE = auto() # Not a special line.
    START_SKIP = auto()
    END_SKIP = auto()
#@+node:TomP.20191231172446.1: ** class Chunk
class Chunk:
    """Holds a block of text, with various metadata about it."""

    def __init__(self, tag='', structure=RST, language=''):
        self.text_lines = [''] # The text as a sequence of lines, free of directives
        self.tag = tag  # A descriptive value for the kind of chunk, such as CODE, TEXT.
        self.structure = structure # The type of structure (rst, md, etc.).
        self.language = language # The programming language, if any, for this chunk.
        self.formatted = '' # The formatted text.

    def add_line(self, line):
        self.text_lines.append(line)

    def format_code(self):
        """Format the text of a chunk. Include special formatting for CODE chunks. 
        
        Currently only reformats RsT/Python and MD/Python.
        """

        if self.tag != CODE or self.structure not in (RST, REST, MD):
            self.formatted = '\n'.join(self.text_lines)
            return

        if self.tag == CODE:
            if self.structure in (RST, REST):
                _formatted = ['.. code:: %s\n' % (self.language)]
                for line in self.text_lines:
                    if not line.strip():
                        _formatted.append('')
                    else:
                        _formatted.append(RST_INDENT + line)
                _formatted.append('')
                self.formatted = '\n'.join(_formatted)
            elif self.structure == MD:
                _formatted = [f'{MD_CODE_FENCE}{self.language}\n']
                _formatted.append('\n'.join(self.text_lines))
                _formatted.append(f'{MD_CODE_FENCE}\n')
                self.formatted = '\n'.join(_formatted)
#@+node:TomP.20200211142437.1: ** class StateMachine
#@@language python

class StateMachine:
    def __init__(self, vr3, tag=TEXT, structure=MD, lang=MD):
        self.vr3 = vr3
        self.base_tag =  tag
        self.structure = structure
        self.base_lang = lang
        self.state = State.BASE
        self.last_state = State.BASE

        self.chunk_list = []
        self.current_chunk = Chunk(self.base_tag, structure, self.base_lang)
        self.lang = lang

        self.inskip = False

    def reset(self, tag=TEXT, lang=MD):
        self.state = State.BASE
        self.last_state = State.BASE
        self.chunk_list = []
        self.current_chunk = Chunk(tag, self.structure, lang)
        self.lang = lang
        self.inskip = False

    #@+<< runMachine >>
    #@+node:TomP.20200215180012.1: *3* << runMachine >>
    def runMachine(self, lines):
        """Process a list of text lines and return final text and a list of lines of code.
        
        ARGUMENT
        lines -- a list of lines of text.
        
        RETURNS
        a tuple (final_text, code_lines).
        """

        for i, line in enumerate(lines):
            self.i = i
            self.do_state(self.state, line)
        self.chunk_list.append(self.current_chunk) # have to pick up the last chunk

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
    #@+node:TomP.20200213170532.1: *3* << do_state >>

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
            # And encounter another @language block.
            if tag == CODE:
                next = State.AT_LANG_CODE
                #_lang = language
            else:
                next = State.BASE
                #_lang = self.base_lang

        action(self, line, tag)
        self.state = next
    #@-<< do_state >>
    #@+<< get_marker >>
    #@+node:TomP.20200212085651.1: *3* << get_marker >>

    def get_marker(self, line):
        """Return classification information about a line.
        
        Used by the state table machinery.
        
        ARGUMENT
        line -- the line of text to be classified.
        
        RETURNS
        a tuple (marker, tag, lang), where 
            marker is one of AT_LANGUAGE_MARKER, MD_FENCE_LANG_MARKER, MD_FENCE_MARKER, MARKER_NONE;
            tag is one of CODE, TEXT;
            lang is the language (e.g., MD, RST, PYTHON) specified by the line, else None.
        """

        marker = Marker.MARKER_NONE
        tag = TEXT
        lang = None

        # For debugging
        if line.startswith('#%%%%'):
            print(self.state, self.current_chunk.language, self.current_chunk.tag)
            return(None, None, None)

        # Omit lines between @ and @c
        if line.rstrip() == '@':
            marker = Marker.START_SKIP
        elif line.strip() == '@c':
            marker = Marker.END_SKIP

        # A marker line may start with "@language" or a Markdown code fence.
        elif line.startswith("@language"):
            marker = Marker.AT_LANGUAGE_MARKER
            lang = MD
            for _lang in LANGUAGES:
                if _lang in line:
                    lang = _lang
                    break
        elif line.startswith(MD_CODE_FENCE):
            lang = MD
            for _lang in LANGUAGES:
                if _lang in line:
                    lang = _lang
                    marker = Marker.MD_FENCE_LANG_MARKER
                    break
                else:
                    marker = Marker.MD_FENCE_MARKER # either a literal block or the end of a fenced code block.

        if lang in LANGUAGES:
            tag = CODE

        return (marker, tag, lang)
    #@-<< get_marker >>
    #@+<< State Table >>
    #@+node:TomP.20200213171040.1: *3* << State Table >>
    State_table = { # (state, marker): (action, next_state)

        (State.BASE, Marker.AT_LANGUAGE_MARKER):  (Action.new_chunk, State.AT_LANG_CODE),
        (State.AT_LANG_CODE, Marker.MARKER_NONE): (Action.add_line, State.AT_LANG_CODE),
        (State.BASE, Marker.MARKER_NONE):         (Action.add_line, State.BASE),

        # When we encounter a new @language line, the next state might be either 
        # State.BASE or State.AT_LANG_CODE, so we have to compute which it will be.
        (State.AT_LANG_CODE, Marker.AT_LANGUAGE_MARKER): (Action.new_chunk, State.TO_BE_COMPUTED),

        # ========= Markdown-specific states ==================
        (State.BASE, Marker.MD_FENCE_LANG_MARKER):         (Action.new_chunk, State.FENCED_CODE),
        (State.BASE, Marker.MD_FENCE_MARKER):              (Action.add_line, State.BASE),
        (State.FENCED_CODE, Marker.MARKER_NONE):           (Action.add_line, State.FENCED_CODE),
        (State.FENCED_CODE, Marker.MD_FENCE_MARKER):       (Action.new_chunk, State.BASE),
        (State.AT_LANG_CODE, Marker.MD_FENCE_LANG_MARKER): (Action.new_chunk, State.FENCED_CODE),
        (State.AT_LANG_CODE, Marker.MD_FENCE_MARKER):      (Action.add_line, State.BASE),
    }
    #@-<< State Table >>


#@-others

#@-leo

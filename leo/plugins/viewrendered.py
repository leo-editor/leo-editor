#@+leo-ver=5-thin
#@+node:tbrown.20100318101414.5990: * @file ../plugins/viewrendered.py
#@+<< vr: docstring >>
#@+node:tbrown.20100318101414.5991: ** << vr: docstring >>
"""

Creates a window for *live* rendering of reSTructuredText, markdown text,
images, movies, sounds, rst, html, jupyter notebooks, etc.

Dependencies
============

This plugin uses docutils, http://docutils.sourceforge.net/, to render reStructuredText,
so installing docutils is highly recommended when using this plugin.

This plugin uses markdown, http://http://pypi.python.org/pypi/Markdown, to render Markdown,
so installing markdown is highly recommended when using this plugin.

Commands
========

viewrendered.py creates the following (``Alt-X``) commands:

``viewrendered (abbreviated vr)``
    Opens a new rendering window.

    By default, the rendering pane renders body text as reStructuredText,
    with all Leo directives removed.
    However, if the body text starts with ``<`` (after removing directives),
    the body text is rendered as html.

    **Important**: The default rendering just described does not apply to nodes
    whose headlines begin with @image, @html, @movie, @networkx, @svg and @url.
    See the section called **Special Renderings** below.

    Rendering sets the process current directory (os.chdir()) to the path
    to the node being rendered, to allow relative paths to work in ``.. image::`` directives.

.. ``viewrendered-big``
..    as above, but zoomed in, useful for presentations
.. ``viewrendered-html``
..    displays the html source generated from reStructuredText, useful for
..    debugging

``vr-hide``
    Makes the rendering pane invisible, but does not destroy it.

``vr-lock`` and ``vr-unlock``
    Locks and unlocks the rendering pane.
    When unlocked (the initial state), the rendering pane renders the contents
    of the presently selected node.
    When locked, the rendering pane does not change when other nodes are selected.
    This is useful for playing movies in the rendering pane.

``vr-pause-play-movie``
    This command has effect only if the rendering pane is presently showing a movie.
    It pauses the movie if playing, or resumes the movie if paused.

``vr-show``
    Makes the rendering pane visible.

``vr-toggle``
    Shows the rendering pane if invisible, otherwise hides it.

``vr-update``
    Forces an update of the rendering pane.
    This is especially useful for @graphics-script nodes:
    such nodes are update automatically only when selected,
    not when the body text changes.

Rendering reStructuredText
==========================

For example, both::

    Heading
    -------

    `This` is **really** a line of text.

and::

    <h1>Heading<h1>

    <tt>This</tt> is <b>really</b> a line of text.

will look something like:

    **Heading**

    `This` is **really** a line of text.

**Important**: reStructuredText errors and warnings will appear in red in the rendering pane.

Rendering markdown
==================
Please see the markdown syntax document at http://daringfireball.net/projects/markdown/syntax
for more information on markdown.

Unless ``@string view-rendered-default-kind`` is set to ``md``, markdown rendering must be
specified by putting it in a ``@md`` node.

Special Renderings
===================

As stated above, the rendering pane renders body text as reStructuredText
by default, with all Leo directives removed. However, if the body text
starts with ``<`` (after removing directives), the body text is rendered as
html.

This plugin renders @md, @image, @jupyter, @html, @movie, @networkx and @svg nodes as follows:

**Note**: For @image, @movie and @svg nodes, either the headline or the first line of body text may
contain a filename.  If relative, the filename is resolved relative to Leo's load directory.

- ``@md`` renderes the body text as markdown, as described above.

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

Relative file names
===================

vr.convert_to_html resolves relative paths using whatever @path directive
is in effect for a particular node. It also does `os.chdir(path)` for that
path.

Settings
========

- ``@color rendering-pane-background-color = white``
  The background color the rendering pane when rendering text.

- ``@bool view-rendered-auto-create = False``
  When True, show the rendering pane when Leo opens an outline.

- ``@bool view-rendered-auto-hide = False``
  When True, hide the rendering pane for text-only renderings.

- ``@string view-rendered-default-kind = rst``
  The default kind of rendering.  One of (big,rst,md,html)

- ``@string view-rendered-md-extensions = extra``
  A comma-delineated list of markdown extensions to use.
  Suitable extensions can be seen here:
  http://pythonhosted.org/Markdown/extensions/index.html

Acknowledgments
================

Terry Brown created this initial version of this plugin.

Edward K. Ream generalized this plugin.

Jacob Peck added markdown support to this plugin.

"""
#@-<< vr: docstring >>
#@+<< vr: imports >>
#@+node:tbrown.20100318101414.5993: ** << vr: imports >>
from __future__ import annotations
from collections.abc import Callable
import os
from pathlib import Path
import shutil
import sys
import textwrap
from typing import Any, Optional, TYPE_CHECKING
from urllib.request import urlopen
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
from leo.core.leoQt import QtMultimedia, QtSvg, QUrl
from leo.core.leoQt import ContextMenuPolicy, WrapMode
from leo.plugins import qt_text

try:
    from leo.core.leoQt import WebEngineAttribute, QtWebEngineWidgets
    qwv = QtWebEngineWidgets.QWebEngineView
    has_webengineview = True
except Exception:
    has_webengineview = False
    try:
        qwv = QtWidgets.QTextBrowser
    except Exception as e:
        g.trace(e)
        qwv = None

# Optional third-party imports...

# Docutils.
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

# Jinja.
try:
    from jinja2 import Template
except ImportError:
    Template = None  # type:ignore

# Markdown.
try:
    from markdown import markdown
    got_markdown = True
except ImportError:
    got_markdown = False  # type:ignore

# nbformat (@jupyter) support.
try:
    import nbformat
    from nbconvert import HTMLExporter
except ImportError:
    nbformat = None

try:
    import pyperclip
except Exception:
    pyperclip = None

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< vr: imports >>
#@+<< vr: annotations >>
#@+node:ekr.20220828161918.1: ** << vr: annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position, VNode
    from leo.core.leoQt import QtGui
    from QtMultimedia import QMediaPlayer

    QCloseEvent = QtGui.QCloseEvent
    QGraphicsScene = QtWidgets.QGraphicsScene
    QGraphicsView = QtWidgets.QGraphicsView
    QWidget = QtWidgets.QWidget
#@-<< vr: annotations >>
trace = False  # This global trace is convenient.
asciidoctor_exec = shutil.which('asciidoctor')
asciidoc3_exec = shutil.which('asciidoc3')
pandoc_exec = shutil.which('pandoc')
#@+others
#@+node:ekr.20110320120020.14491: ** vr.Top-level functions
#@+node:tbrown.20100318101414.5995: *3* vr function: init
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    global got_docutils
    if not g.app.gui.guiName().startswith('qt'):
        return False
    if not got_docutils:
        g.es_print('Warning: viewrendered.py running without docutils.')
    # Always enable this plugin, even if imports fail.
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    g.registerHandler('close-frame', onClose)
    g.registerHandler('scrolledMessage', show_scrolled_message)
    return True
#@+node:ekr.20240727091022.1: *3* vr function: getVR
def getVr(*, c: Any = None, event: Any = None, parent: QtWidgets.QWidget = None) -> Optional[QtWidgets.QWidget]:
    """Return the ViewRenderedController instance or None."""
    if g.app.gui.guiName() != 'qt':
        return None

    # First, get c.
    if c:
        pass
    elif event:
        c = event.get('c')
        if not c:
            return None
    else:
        g.trace('"c" or "event" kwarg required', g.callers())
        return None
    vr = getattr(c, 'vr', None)
    if not vr:
        vr = ViewRenderedController(c)
        c.vr = vr
        if parent:
            vr.setParent(parent)
        else:
            dw = c.frame.top
            if dw:
                dw.insert_vr_frame(vr)
    return vr
#@+node:ekr.20110317024548.14376: *3* vr function: onCreate
def onCreate(tag: str, keys: dict) -> None:
    c = keys.get('c')
    if not c:
        return
    vr = getVr(c=c)
    g.registerHandler('select2', vr.update)
    g.registerHandler('idle', vr.update)
    vr.active = True
    vr.is_visible = False
    vr.hide()
#@+node:vitalije.20170712174157.1: *3* vr function: onClose
def onClose(tag: str, keys: dict) -> None:
    """
    Handle a close event in the Leo outline.
    """
    c = keys.get('c')
    if not c:
        return
    vr = getattr(c, 'vr', None)
    if vr:
        vr.closeEvent(event=None)

#@+node:tbrown.20110629132207.8984: *3* vr function: show_scrolled_message
def show_scrolled_message(tag: str, kw: Any) -> None:
    if g.unitTesting:
        return  # This just slows the unit tests.
    c = kw.get('c')
    if not c:
        return
    p = c and c.p
    s = kw.get('msg')
    if not s.strip():
        g.trace('No message', g.callers())
        return
    # Create the VR pane if necessary.
    vr = getVr(c=c)
    if not vr:
        return
    # Make sure we will show the message.
    vr.is_active = True
    vr.is_visible = True
    vr.show()
    # A hack: suppress updates until the node changes.
    vr.gnx = p.v.gnx
    vr.length = len(p.v.b)
    # Render!
    f = vr.dispatch_dict.get('rest')
    f(s, kw)
    c.bodyWantsFocusNow()
#@+node:ekr.20110320120020.14490: ** vr.Commands
#@+node:ekr.20131213163822.16471: *3* g.command('preview')
@g.command('preview')
def preview(event: LeoKeyEvent) -> None:
    """A synonym for the vr-toggle command."""
    toggle_rendering_pane(event)
#@+node:tbrown.20100318101414.5998: *3* g.command('vr')
@g.command('vr')
def viewrendered(event: LeoKeyEvent) -> Optional[Any]:
    """Open render view for commander"""
    vr = getVr(event=event)
    if vr:
        c = vr.c
        vr.show()
        vr.is_visible = True
        c.bodyWantsFocusNow()
        return vr
    return None
#@+node:ekr.20130413061407.10362: *3* g.command('vr-contract')
@g.command('vr-contract')
def contract_rendering_pane(event: LeoKeyEvent) -> None:
    """Contract the rendering pane."""
    vr = getVr(event=event)
    if vr:
        vr.show()
        vr.contract()
#@+node:ekr.20130413061407.10361: *3* g.command('vr-expand')
@g.command('vr-expand')
def expand_rendering_pane(event: LeoKeyEvent) -> None:
    """Expand the rendering pane."""
    vr = getVr(event=event)
    if vr:
        vr.show()
        vr.expand()
#@+node:ekr.20240507095853.1: *3* g.command('vr-fully-expand')
@g.command('vr-fully-expand')
def fully_expand_rendering_pane(event: LeoKeyEvent) -> None:
    """Expand the rendering pane."""
    vr = getVr(event=event)
    if vr:
        vr.show()
        vr.fully_expand()
#@+node:ekr.20110917103917.3639: *3* g.command('vr-hide')
@g.command('vr-hide')
def hide_rendering_pane(event: LeoKeyEvent) -> None:
    """Close the rendering pane."""
    vr = getVr(event=event)
    if vr:
        vr.hide()
        vr.is_visible = False

# Compatibility

close_rendering_pane = hide_rendering_pane
#@+node:ekr.20110321072702.14507: *3* g.command('vr-lock')
@g.command('vr-lock')
def lock_rendering_pane(event: LeoKeyEvent) -> None:
    """Lock the rendering pane."""
    vr = getVr(event=event)
    if vr and not vr.locked:
        vr.lock()
#@+node:ekr.20110320233639.5777: *3* g.command('vr-pause-play')
@g.command('vr-pause-play-movie')
def pause_play_movie(event: LeoKeyEvent) -> None:
    """Pause or play a movie in the rendering pane."""
    vr = getVr(event=event)
    if vr:
        vp = vr.vp
        if not vp:
            return
        f = vp.pause if vp.isPlaying() else vp.play
        f()
#@+node:ekr.20110317080650.14386: *3* g.command('vr-show')
@g.command('vr-show')
def show_rendering_pane(event: LeoKeyEvent) -> None:
    """Show the rendering pane."""
    vr = getVr(event=event)
    if vr:
        c = vr.c
        vr.show()  # QWidget.show.
        vr.is_visible = True
        c.bodyWantsFocusNow()
#@+node:ekr.20131001100335.16606: *3* g.command('vr-toggle-visibility')
@g.command('vr-toggle-visibility')
@g.command('vr-toggle')  # Legacy
def toggle_rendering_pane(event: LeoKeyEvent) -> None:
    """Toggle the visibility of the VR pane."""
    vr = getVr(event=event)
    if not vr:
        return
    c = vr.c
    vr.is_visible = not vr.is_visible
    if vr.is_visible:
        g.es('VR pane on', color='red')
        vr.show()
    else:
        g.es('VR pane off', color='red')
        vr.hide()
    c.bodyWantsFocusNow()
#@+node:ekr.20240508082844.1: *3* g.command('vr-toggle-keep-open')
@g.command('vr-toggle-keep-open')
def toggle_keep_open(event: LeoKeyEvent) -> None:
    """Toggle the visibility of the VR pane."""
    vr = getVr(event=event)
    if vr:
        c = vr.c
        vr.hide()  # So the toggle below will work.
        vr.keep_open = not vr.keep_open
        vr.update('keep-open', {'c': c, 'force': True})  # type:ignore
#@+node:ekr.20130412180825.10345: *3* g.command('vr-unlock')
@g.command('vr-unlock')
def unlock_rendering_pane(event: LeoKeyEvent) -> None:
    """Pause or play a movie in the rendering pane."""
    vr = getVr(event=event)
    if vr and vr.locked:
        vr.unlock()
#@+node:ekr.20110321151523.14464: *3* g.command('vr-update')
@g.command('vr-update')
def update_rendering_pane(event: LeoKeyEvent) -> None:
    """Update the rendering pane"""
    vr = getVr(event=event)
    if vr:
        c = vr.c
        vr.update(tag='view', keywords={'c': c, 'force': True})  # type:ignore
#@+node:ekr.20110317024548.14375: ** class ViewRenderedController (QWidget)
class ViewRenderedController(QtWidgets.QWidget):  # type:ignore
    """A class to control rendering in a rendering pane."""
    #@+<< vr: default templates >>
    #@+node:ekr.20241231164944.1: *3* << vr: default templates >>
    #@+others
    #@+node:ekr.20170324090828.1: *4* vr.default_image template
    default_image_template = '''\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head></head>
    <body bgcolor=white>
    <img src="%s">
    </body>
    </html>
    '''
    #@+node:ekr.20241231121842.1: *4* vr.default_katex_template
    default_katex_template = textwrap.dedent(r'''
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.19/dist/katex.min.css"
            integrity="sha384-7lU0muIg/i1plk7MgygDUp3/bNRA65orrBub4/OSWHECgwEsY83HaS1x3bljA/XV"
            crossorigin="anonymous">

        <!-- The loading of KaTeX is deferred to speed up page rendering -->
        <script defer
            src="https://cdn.jsdelivr.net/npm/katex@0.16.19/dist/katex.min.js"
            integrity="sha384-RdymN7NRJ+XoyeRY4185zXaxq9QWOOx3O7beyyrRK4KQZrPlCDQQpCu95FoCGPAE"
            crossorigin="anonymous"></script>

        <!-- To automatically render math in text elements, include the auto-render extension: -->
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.19/dist/contrib/auto-render.min.js" integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous"
            onload="renderMathInElement(document.body);">
        </script>
    </head>
    <body>
    [[body]]
    </body>
    </html>
    ''')
    #@+node:ekr.20241231122327.1: *4* vr.default_latex template
    default_latex_template = r'''
    \documentclass[12pt, letter-paper]{article}
    \usepackage{graphicx} % Images.
    \usepackage{tikz} % Evaluate expressions.
    \usepackage{hyperref} % For \href.
    \hypersetup{colorlinks=true, urlcolor=cyan}
    \urlstyle{same}
    \usepackage{pgfplots} % For inline plots.
    \usepackage{amsmath} % For alignment.
    \usepackage[
        bindingoffset=0.2in, footskip=.25in,
        left=0.5in, right=2.5in, top=0.5in, bottom=0.5in,
    ]{geometry}

    \title{My Title}
    \author{Edward K. Ream}
    \date{December 2024}

    \pagenumbering{gobble}
    \setlength{\parskip}{6pt}
    \setlength{\parindent}{0pt}
    \pgfplotsset{compat=1.18}

    \begin{document}
    % \maketitle

    \section*{Section name}


    \end{document}
    '''
    #@+node:ekr.20241224072714.1: *4* vr.default_mathjax_template
    default_mathjax_template = '''
    <head>
      <script type="text/x-mathjax-config">
        MathJax.Hub.Config({tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}});
      </script>
      <script type="text/javascript" async
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS_CHTML">
      </script>
    </head>
    '''
    #@+node:ekr.20241231180612.1: *4* vr.default_typst_template
    default_typst_template = None
    #@-others
    #@-<< vr: default templates >>
    #@+others
    #@+node:ekr.20110317080650.14380: *3*  vr.ctor & helpers
    def __init__(self, c: Cmdr, parent: QWidget = None) -> None:
        """Ctor for ViewRenderedController class."""
        self.c = c
        # Create the widget.
        super().__init__(parent)
        self.create_pane(parent)
        # Ivars set by reloadSettings.
        self.auto_create: bool = None
        self.background_color: str = None
        self.keep_open: bool = None
        self.katex_template: str = None
        self.latex_template: str = None
        self.mathjax_template: str = None
        self.typst_template: str = None
        self.pdf_zoom: int = None
        # Widgets managed by destroy_widgets.
        self.browser: QWidget = None
        self.gs: QGraphicsScene = None
        self.gv: QGraphicsView = None
        self.vp: QMediaPlayer = None
        self.w: QWidget = None  # The present widget in the rendering pane.
        # Set the ivars.
        self.active = True
        self.gnx: str = None
        self.keep_open = False  # True: keep the VR pane open even when showing text.
        self.is_visible = False
        self.length = 0  # The length of previous p.b.
        self.locked = False
        self.pdf_qwv = None  # The singleton qwv instance, with support for pdf.
        self.qwv = None  # The singleton qwv instance.
        self.scrollbar_pos_dict: dict[VNode, Position] = {}  # Keys are vnodes, values are positions.
        # User settings.
        self.reloadSettings()
        self.node_changed = True
        # Init.
        self.create_dispatch_dict()
        self.is_visible = self.auto_create
        if self.auto_create:
            self.show()
        else:
            self.hide()
    #@+node:ekr.20110320120020.14478: *4* vr.create_dispatch_dict
    def create_dispatch_dict(self) -> dict[str, Callable]:
        d = {
            'asciidoc': self.update_asciidoc,
            'big': self.update_rst,
            'html': self.update_html,
            'graphics-script': self.update_graphics_script,
            'image': self.update_image,
            'jinja': self.update_jinja,
            'jupyter': self.update_jupyter,
            'katex': self.update_katex,
            'latex': self.update_latex,
            'markdown': self.update_md,
            'mathjax': self.update_mathjax,
            'md': self.update_md,
            'movie': self.update_movie,
            'networkx': self.update_networkx,
            # 'pandoc': self.update_pandoc,
            'pdf': self.update_pdf,
            'pyplot': self.update_pyplot,
            'rest': self.update_rst,
            'rst': self.update_rst,
            'svg': self.update_svg,
            'plantuml': self.update_plantuml,
            'typst': self.update_typst,
            # 'url': self.update_url,
            # 'xml': self.update_xml,
        }
        self.dispatch_dict = d
        return d
    #@+node:ekr.20171114150510.1: *4* vr.reloadSettings
    def reloadSettings(self) -> None:
        c = self.c
        c.registerReloadSettings(self)
        self.auto_create = c.config.getBool('view-rendered-auto-create', False)
        self.keep_open = c.config.getBool('view-rendered-keep-open', True)
        self.background_color = c.config.getColor('rendering-pane-background-color') or 'white'
        self.default_kind = c.config.getString('view-rendered-default-kind') or 'rst'
        self.pdf_zoom = c.config.getInt('view-rendered-pdf-zoom') or 100

        # Templates...

        def get_template(kind: str) -> str:
            setting_name = f"view-rendered-{kind}-template"
            aList = c.config.getData(setting_name, strip_comments=True, strip_data=True)
            if aList is None:
                return getattr(self, f"default_{kind}_template")
            return '\n'.join(aList)

        self.image_template = get_template('image')
        self.katex_template = get_template('katex')
        self.latex_template = get_template('latex')
        self.mathjax_template = get_template('mathjax')
        self.typst_template = get_template('typst')
    #@+node:ekr.20190614065659.1: *4* vr.create_pane
    def create_pane(self, parent: QWidget) -> None:
        """Create the VR pane."""
        if g.unitTesting:
            return
        # Create the inner contents.
        self.setObjectName('viewrendered_pane')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
    #@+node:tbrown.20110621120042.22676: *3* vr.closeEvent
    def closeEvent(self, event: QCloseEvent) -> None:
        """Deactivate callbacks when an Outline closes."""
        self.active = False
        g.unregisterHandler('select2', self.update)
        g.unregisterHandler('idle', self.update)
        g.unregisterHandler('scrolledMessage', show_scrolled_message)
        self.destroy_widgets()
    #@+node:ekr.20130413061407.10363: *3* vr.contract & expand
    def contract(self) -> None:
        self.change_size(-100)

    def expand(self) -> None:
        self.change_size(100)

    def change_size(self, delta: int) -> None:
        splitter = self.parent()
        if not splitter:
            return
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
    #@+node:ekr.20240507100254.1: *3* vr.fully_expand
    def fully_expand(self) -> None:
        """Cover the body pane with the VR pane."""
        splitter = self.parent()
        if splitter and isinstance(splitter, QtWidgets.QSplitter):
            i = splitter.indexOf(self)
            splitter.moveSplitter(0, i)
        self.show()
    #@+node:ekr.20110321072702.14508: *3* vr.lock/unlock
    def lock(self) -> None:
        """Lock the VR pane."""
        g.note('rendering pane locked')
        self.locked = True

    def unlock(self) -> None:
        """Unlock the VR pane."""
        g.note('rendering pane unlocked')
        self.locked = False
    #@+node:ekr.20240507100402.1: *3* vr.restore_body
    def restore_body(self) -> None:
        """Restore the visibility of the body pane."""
        splitter = self.parent()  # A NestedSplitter
        if splitter and isinstance(splitter, QtWidgets.QSplitter):
            i = splitter.indexOf(self)
            splitter.moveSplitter(int(sum(splitter.sizes()) / 2), i)
        self.show()
    #@+node:ekr.20160921071239.1: *3* vr.set_html
    def set_html(self, s: str, w: QWidget) -> None:
        """Set text in w to s, preserving scroll position."""
        p = self.c.p
        sb = w.verticalScrollBar()
        if sb:
            d = self.scrollbar_pos_dict
            if self.node_changed:
                # Set the scrollbar.
                pos = d.get(p.v, sb.sliderPosition())
                sb.setSliderPosition(pos)
            else:
                # Save the scrollbars
                d[p.v] = pos = sb.sliderPosition()
        # if trace: g.trace('\n'+s)
        w.setHtml(s)
        if sb:
            # Restore the scrollbars
            assert pos is not None
            sb.setSliderPosition(pos)
    #@+node:ekr.20101112195628.5426: *3* vr.update & helpers
    # Must have this signature: called by leoPlugins.callTagHandler.

    def update(self, tag: str, keywords: Any) -> None:  # type:ignore
        """
        vr.update: Update the VR pane.
        Called at idle time and by the vr-update command.
        """
        p = self.c.p
        if not self.active:
            try:
                # Save the scroll position.
                w = self.w
                if w and w.__class__ == QtWidgets.QTextBrowser:
                    sb = w.verticalScrollBar()
                    self.scrollbar_pos_dict[p.v] = sb.sliderPosition()
            except Exception:
                g.es_exception()
            return
        if self.locked:
            return
        if not self.is_visible:
            return
        if not self.must_update(keywords):
            return
        # Suppress updates until we change nodes.
        f: Callable = None
        self.node_changed = self.gnx != p.v.gnx
        self.gnx = p.v.gnx
        self.length = len(p.b)  # not s
        # Remove Leo directives.
        s = keywords.get('s') if 's' in keywords else p.b
        s = self.remove_directives(s)
        # Dispatch based on the computed kind.
        kind = keywords.get('flags') if 'flags' in keywords else self.get_kind(p)
        # g.trace('kind', repr(kind))
        if kind or keywords.get('force'):
            f = self.dispatch_dict.get(kind)
        else:
            # Do *not* try to render plain text.
            w = self.get_base_text_widget()
            w.setPlainText(s)
        if f:
            f(s, keywords)
            self.show()
        elif self.keep_open:
            self.show()
        else:
            self.hide()
    #@+node:ekr.20241227053437.1: *4* vr.update: helpers
    #@+node:ekr.20241224074331.1: *5* vr.create_web_engineview
    def create_web_engineview(self) -> QWidget:
        """
        Return a *new* QWebEngineView instance, deleting any previous instance.
        """
        c = self.c
        # Kill the old QWebEngineView!
        self.destroy_widgets()

        # Always create a new QWebEngineView.
        self.qwv = self.w = w = qwv()
        self.embed_widget(w)
        if isinstance(w, QtWidgets.QTextBrowser):
            return w

        # Allow remote access.
        settings = w.settings()
        wa = WebEngineAttribute.LocalContentCanAccessRemoteUrls
        settings.setAttribute(wa, True)

        # Set the font size, but this does very little.
        n = c.config.getInt('qweb-view-font-size') or 16
        n = abs(n)
        settings.setFontSize(settings.FontSize.DefaultFontSize, n)
        return w
    #@+node:ekr.20241226173150.1: *5* vr.create_web_engineview_with_pdf
    def create_web_engineview_with_pdf(self) -> QWidget:
        """
        Return a *new* QWebEngineView instance with support for pdf,
        deleting any previous instance.
        """
        # Create the QWebEngineView if possible and embed the widget.
        w = self.create_web_engineview()
        assert w == self.w, g.callers()
        if isinstance(w, QtWidgets.QTextBrowser):
            # create_web_engineview has issued the warning.
            return w

        # Allow rendering of .pdf files.
        settings = w.settings()
        settings.setAttribute(settings.WebAttribute.PluginsEnabled, True)
        return w
    #@+node:ekr.20241227044803.1: *5* vr.destroy_widgets
    def destroy_widgets(self) -> None:
        """Destroy all widgets."""
        # g.trace(g.shortFileName(self.c.fileName()))
        for ivar in ('gs', 'gv', 'pdf_qwv', 'qwv', 'vp'):
            var = getattr(self, ivar, None)
            if var is not None:
                del var
            setattr(self, ivar, None)
        self.w = None
    #@+node:ekr.20110320120020.14486: *5* vr.embed_widget
    def embed_widget(self, w: QWidget) -> None:
        """Embed widget w in the layout."""

        assert w == self.w, g.callers()  # Invariant.

        # Delete all previous widgets.
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeItem(layout.itemAt(0))

        # Add the new widget.
        self.layout().addWidget(w)
        w.show()
    #@+node:ekr.20110320120020.14476: *5* vr.must_update
    def must_update(self, keywords: Any) -> bool:
        """Return True if we must update the rendering pane."""
        c, p = self.c, self.c.p
        if g.unitTesting:
            return False
        if c != keywords.get('c') or not self.active:
            return False
        if keywords.get('force'):
            return True
        if self.locked:
            return False
        if self.gnx != p.v.gnx:
            return True
        if self.length != len(p.b):
            self.length = len(p.b)  # Suppress updates until next change.
            return self.get_kind(p) != 'pyplot'
        return False
    #@+node:ekr.20191004143229.1: *4* vr.update_asciidoc & helpers
    def update_asciidoc(self, s: str, keywords: Any) -> None:
        """Update asciidoc in the VR pane."""
        global asciidoctor_exec, asciidoc3_exec
        # Do this regardless of whether we show the widget or not.
        w = self.get_base_text_widget()
        assert self.w
        if s:
            self.show()
        if asciidoctor_exec or asciidoc3_exec:
            try:
                s2 = self.convert_to_asciidoctor(s)
                self.set_html(s2, w)
                return
            except Exception:
                g.es_exception()
        self.update_rst(s, keywords)
    #@+node:ekr.20191004143805.1: *5* vr.convert_to_asciidoctor
    def convert_to_asciidoctor(self, s: str) -> str:
        """Convert s to html using the asciidoctor or asciidoc processor."""
        c, p = self.c, self.c.p
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        s = self.run_asciidoctor(s)
        return g.toUnicode(s)
    #@+node:ekr.20191004144128.1: *5* vr.run_asciidoctor
    def run_asciidoctor(self, s: str) -> str:
        """
        Process s with asciidoctor or asciidoc3.
        return the contents of the html file.
        The caller handles all exceptions.
        """
        global asciidoctor_exec, asciidoc3_exec
        assert asciidoctor_exec or asciidoc3_exec, g.callers()
        home = g.os.path.expanduser('~')
        i_path = g.finalize_join(home, 'vr_input.adoc')
        o_path = g.finalize_join(home, 'vr_output.html')
        # Write the input file.
        with open(i_path, 'w') as f:
            f.write(s)
        # Call the external program to write the output file.
        prog = 'asciidoctor' if asciidoctor_exec else 'asciidoc3'
        # The -e option deletes css.
        command = f"{prog} {i_path} -b html5 -o {o_path}"
        g.execute_shell_commands(command)
        # Read the output file and return it.
        with open(o_path, 'r') as f:
            return f.read()
    #@+node:ekr.20110321151523.14463: *4* vr.update_graphics_script
    def update_graphics_script(self, s: str, keywords: Any) -> None:
        """Display the graphics script in `s` in the VR pane."""
        c = self.c
        if g.unitTesting:
            return
        force = keywords.get('force')
        if self.gs and not force:
            return

        # Create the widgets.
        if not self.gs:
            splitter = g.app.gui.get_top_splitter()
            self.gs = QtWidgets.QGraphicsScene(splitter)
            self.gv = QtWidgets.QGraphicsView(self.gs)
            w = self.w = self.gv.viewport()  # A QWidget
            self.embed_widget(w)

        c.executeScript(
            script=s,
            namespace={'gs': self.gs, 'gv': self.gv},
        )
    #@+node:ekr.20110321005148.14534: *4* vr.update_html
    update_html_count = 0

    def update_html(self, s: str, keywords: Any) -> None:
        """Display the html text in `s` in the VR pane."""
        c = self.c

        # Create a new QWebEngineView.
        w = self.create_web_engineview()

        # Set the html.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:ekr.20110320120020.14482: *4* vr.update_image
    def update_image(self, s: str, keywords: Any) -> None:
        """
        Display an image in the VR pane.
        The first line of `s` should be a `@image <path>`.
        """
        if not s.strip():
            return
        lines = g.splitLines(s) or []
        fn = lines and lines[0].strip()
        if not fn:
            return
        w = self.get_base_text_widget()
        ok, path = self.get_fn(fn, '@image')
        if not ok:
            w.setPlainText(f"@image: file not found: {path!r}")
            return
        path = path.replace('\\', '/')
        template = self.image_template % (path)
        template = textwrap.dedent(template).strip()
        self.show()
        w.setHtml(template)
    #@+node:ekr.20170105124347.1: *4* vr.update_jupyter & helper
    update_jupyter_count = 0

    def update_jupyter(self, s: str, keywords: Any) -> None:
        """Update an @jupyter node in the VR pane."""
        c = self.c
        w = self.get_base_text_widget()
        s = self.get_jupyter_source(c)
        w.hide()  # This forces a proper update.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()

        if pyperclip:
            pyperclip.copy(s)
    #@+node:ekr.20180311090852.1: *5* vr.get_jupyter_source
    def get_jupyter_source(self, c: Cmdr) -> str:
        """Return the html for the @jupyter node."""
        body = c.p.b.lstrip()
        if body.startswith('<'):
            # Assume the body is html.
            return body
        if body.startswith('{'):
            # Leo 5.7.1: Allow raw JSON.
            s = body
        else:
            url = c.p.h.split()[1]
            if not url:
                return ''
            if not nbformat:
                return 'can not import nbformat to render url: %r' % url
            try:
                s = urlopen(url).read().decode()
            except Exception:
                return 'url not found: %s' % url

        try:
            nb = nbformat.reads(s, as_version=4)
            e = HTMLExporter()
            (s, junk_resources) = e.from_notebook_node(nb)
        except nbformat.reader.NotJSONError:
            pass  # Assume the result is html.
        return s
    #@+node:ekr.20241231121212.1: *4* vr.update_katex
    def update_katex(self, s: str, keywords: Any) -> None:
        """Display the katex text `s` in the VR pane."""

        # Create a new QWebEngineView.
        w = self.create_web_engineview()
        if not has_webengineview:
            g.print_unique_message('katex rendering requires PyQt6-WebEngine')
            w.setHtml(s)
            self.show()
            return

        # Replace whole-line katex comments with html comments.
        s = ''.join([
            z for z in g.splitLines(s) if not z.strip().startswith('%')
        ])
        contents = self.katex_template.replace('[[body]]', s)
        w.setHtml(contents)
        self.show()
    #@+node:ekr.20170324064811.1: *4* vr.update_latex
    def update_latex(self, s: str, keywords: Any) -> None:
        """Display the LaTeX text `s` in the VR pane."""

        # Create a new QWebEngineView.
        w = self.create_web_engineview()
        if not has_webengineview:
            g.print_unique_message('LaTeX rendering requires PyQt6-WebEngine')
            w.setHtml(s)
            self.show()
            return

        # Replace whole-line latex comments with html comments.
        s = ''.join([
            z for z in g.splitLines(s) if not z.strip().startswith('%')
        ])
        contents = self.latex_template + '\n\n' + s
        w.setHtml(contents)
        self.show()
    #@+node:ekr.20241224072334.1: *4* vr.update_mathjax
    def update_mathjax(self, s: str, keywords: Any) -> None:
        """Display the mathjax text `s` in the VR pane."""

        # Create a new QWebEngineView.
        w = self.create_web_engineview()
        if not has_webengineview:
            g.print_unique_message('mathjax rendering requires PyQt6-WebEngine')
            w.setHtml(s)
            self.show()
            return

        # Replace whole-line latex comments with html comments.
        s = ''.join([
            z for z in g.splitLines(s) if not z.strip().startswith('%')
        ])
        contents = self.mathjax_template + '\n\n' + s
        w.setHtml(contents)
        self.show()
    #@+node:peckj.20130207132858.3671: *4* vr.update_md & helper
    def update_md(self, s: str, keywords: Any) -> None:
        """Display the markdown text in `s` in the VR pane."""
        c = self.c
        p = c.p
        s = s.strip().strip('"""').strip("'''").strip()
        isHtml = s.startswith('<') and not s.startswith('<<')
        # Do this regardless of whether we show the widget or not.
        w = self.get_base_text_widget()
        assert self.w
        if s:
            self.show()
        if got_markdown:
            force = keywords.get('force')
            colorizer = c.frame.body.colorizer
            language = colorizer.scanLanguageDirectives(p)
            if force or language in ('rst', 'rest', 'markdown', 'md'):
                if not isHtml:
                    s = self.convert_to_markdown(s)
            self.set_html(s, w)
        else:
            # g.trace('markdown not available: using rst')
            self.update_rst(s, keywords)
    #@+node:ekr.20160921134552.1: *5* vr.convert_to_markdown
    def convert_to_markdown(self, s: str) -> str:
        """Convert s to html using the markdown processor."""
        c, p = self.c, self.c.p
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        try:
            mdext = c.config.getString('view-rendered-md-extensions') or 'extra'
            mdext_list = [x.strip() for x in mdext.split(',')]
            s = markdown(s, extensions=mdext_list)
            s = g.toUnicode(s)
        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                s = 'MD error:\n%s\n\n%s' % (msg, s)
        return s
    #@+node:ekr.20110320120020.14481: *4* vr.update_movie
    movie_warning = False

    def update_movie(self, s: str, keywords: Any) -> None:
        """
        Show an @movie in the VR pane.
        
        The first line of `s` should be the path to the movie.
        """
        ok, path = self.get_fn(s, '@movie')
        if not ok:
            w = self.get_base_text_widget()
            w.setPlainText('Not found: %s' % (path))
            return
        if not QtMultimedia:
            if not self.movie_warning:
                self.movie_warning = True
                g.es_print('No QtMultimedia module')
            w = self.get_base_text_widget()
            w.setPlainText('')
            return
        if self.vp:
            vp = self.vp
            self.vp.stop()
            self.vp.deleteLater()

        # Create a fresh player.
        g.es_print('playing', path)
        url = QtCore.QUrl.fromLocalFile(path)
        content = QtMultimedia.QMediaContent(url)
        self.vp = vp = QtMultimedia.QMediaPlayer()
        vp.setMedia(content)
        # Won't play .mp4 files: https://bugreports.qt.io/browse/QTBUG-32783
        vp.play()


    #@+node:ekr.20110320120020.14484: *4* vr.update_networkx
    def update_networkx(self, s: str, keywords: Any) -> None:
        """Dispaly a networkx graphic in `s` in the VR pane."""
        w = self.get_base_text_widget()
        w.setPlainText('')  # 'Networkx: len: %s' % (len(s)))
        self.show()
    #@+node:ekr.20191006155748.1: *4* vr.update_pandoc & helpers (disabled)
    def update_pandoc(self, s: str, keywords: Any) -> None:
        """
        Display an @pandoc node in the VR pane.
        
        This code has been disabled.
        """
        global pandoc_exec
        w = self.get_base_text_widget()
        assert self.w
        if s:
            self.show()
        if pandoc_exec:
            try:
                s2 = self.convert_to_pandoc(s)
                self.set_html(s2, w)
            except Exception:
                g.es_exception()
            return
        self.update_rst(s, keywords)
    #@+node:ekr.20191006155748.3: *5* vr.convert_to_pandoc
    def convert_to_pandoc(self, s: str) -> str:
        """Convert s to html using the asciidoctor or asciidoc processor."""
        c, p = self.c, self.c.p
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        s = self.run_pandoc(s)
        return g.toUnicode(s)
    #@+node:ekr.20191006155748.4: *5* vr.run_pandoc
    def run_pandoc(self, s: str) -> str:
        """
        Process s with pandoc.
        return the contents of the html file.
        The caller handles all exceptions.
        """
        global pandoc_exec
        assert pandoc_exec, g.callers()
        home = g.os.path.expanduser('~')
        i_path = g.finalize_join(home, 'vr_input.pandoc')
        o_path = g.finalize_join(home, 'vr_output.html')
        # Write the input file.
        with open(i_path, 'w') as f:
            f.write(s)
        # Call pandoc to write the output file.
        # --quiet does no harm.
        command = f"pandoc {i_path} -t html5 -o {o_path}"
        g.execute_shell_commands(command)
        # Read the output file and return it.
        with open(o_path, 'r') as f:
            return f.read()
    #@+node:ekr.20241226011006.1: *4* vr.update_pdf
    def update_pdf(self, s: str, keywords: Any) -> None:
        """
        Display a pdf file in the VR pane.
        The first line of `s` should be a `@pdf <path>`.
        Resolve relative paths using the outline's directory.
        """
        if not s.strip():
            return

        # Create a new QWebEngineView.
        w = self.create_web_engineview_with_pdf()
        if not has_webengineview:
            g.print_unique_message('@pdf rendering requires PyQt6-WebEngine')
            w.setHtml(s)
            self.show()
            return

        ok, path = self.get_fn(s, '@pdf')
        if not ok:
            s = f"File not found: {path}"
            g.print_unique_message(s)
            w.setHtml(s)
            self.show()
            return

        # Load the file.
        url = QUrl.fromLocalFile(path)
        # https://www.rfc-editor.org/rfc/rfc8118
        url.setFragment(f"zoom={self.pdf_zoom}")
        w.load(url)
        self.show()
    #@+node:ekr.20160928023915.1: *4* vr.update_pyplot
    def update_pyplot(self, s: str, keywords: Any) -> None:
        """
        Execute the pyplot script in `s` and show the results in the VR pane.
        """
        c = self.c
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            from matplotlib import animation
            import numpy as np
        except Exception:
            g.print_unique_message('VR: missing imports: cannot process @pyplot node')
            return
        backend = plt.get_backend()  # Returns 'qtagg' initially.
        if backend != 'module://leo.plugins.pyplot_backend':
            backend = g.finalize_join(g.app.loadDir, '..', 'plugins', 'pyplot_backend.py')
            if g.os_path_exists(backend):
                try:
                    matplotlib.use('module://leo.plugins.pyplot_backend')
                except ImportError:
                    g.trace('===== FAIL: pyplot.backend')
            else:
                g.trace('===== MISSING: pyplot.backend')

        plt.ion()  # Set interactive mode.

        if 0:  # Embedding works without this!
            self.embed_pyplot_widget()

        # pyplot will throw RuntimeError if we close the pane.
        namespace = {
            'animation': animation,
            'matplotlib': matplotlib,
            'numpy': np, 'np': np,
            'pyplot': plt, 'plt': plt,
        }
        c.executeScript(
            event=None,
            args=None, p=None,
            script=None,
            useSelectedText=False,
            define_g=True,
            define_name='__main__',
            silent=False,
            namespace=namespace,
            raiseFlag=False,
            runPyflakes=False,  # Suppress warnings about pre-defined symbols.
        )
        c.bodyWantsFocusNow()

        # Be courteous to other users - restore default pyplot drawing target
        matplotlib.use('QtAgg')
    #@+node:ekr.20110320120020.14477: *4* vr.update_rst & helpers
    def update_rst(self, s: str, keywords: Any) -> None:
        """Show the rst text in `s` in the VR pane."""
        s = s.strip().strip('"""').strip("'''").strip()
        isHtml = s.startswith('<') and not s.startswith('<<')

        # Do this regardless of whether we show the widget or not.
        w = self.get_base_text_widget()
        if s:
            self.show()
        if got_docutils:
            if not isHtml:
                s = self.convert_to_html(s)
            self.set_html(s, w)
        else:
            w.setPlainText(s)
    #@+node:ekr.20160920221324.1: *5* vr.convert_to_html
    def convert_to_html(self, s: str) -> str:
        """Convert s to html using docutils."""
        c, p = self.c, self.c.p
        # Update the current path.
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        try:
            # Suppress all error messages.
            sys.stderr = open(os.devnull, "w")
            # Call docutils to get the string.
            s = publish_string(s, writer_name='html')
            s = g.toUnicode(s)
        except SystemMessage:
            # msg = sm.args[0]
            # if 'SEVERE' in msg or 'FATAL' in msg:
                # s = 'RST error:\n%s\n\n%s' % (msg, s)
            pass
        finally:
            sys.stderr = sys.__stderr__
        return s

    def update_plantuml(self, s: str, keywords: Any) -> None:
        w = self.get_base_text_widget()
        path = self.c.p.h[9:].strip()
        print("Plantuml output file name: ", path)
        with open("temp.plantuml", "w") as f:
            f.write(s)
        pth_plantuml_jar = "~/.leo"
        os.system("cat temp.plantuml | java -jar %s/plantuml.jar -pipe > %s" % (pth_plantuml_jar, path))
        template = self.image_template % (path)
        template = textwrap.dedent(template).strip()
        self.show()
        w.setReadOnly(False)
        w.setHtml(template)
        w.setReadOnly(True)

    def update_jinja(self, s: str, keywords: Any) -> None:
        h = self.c.p.h
        p = self.c.p
        c = self.c
        oldp = None

        if not h.startswith('@jinja'):
            return

        def find_root(p: Position) -> Optional[tuple[Position, Position]]:
            for newp in p.parents():
                if newp.h.strip() == '@jinja':
                    oldp, p = p, newp
                    return oldp, p
            return None, None

        def find_inputs(p: Position) -> Optional[tuple[Position, Position]]:
            for newp in p.parents():
                if newp.h.strip() == '@jinja inputs':
                    oldp, p = p, newp
                    _, p = find_root(p)
                    return oldp, p
            return None, None

        # if on jinja node's children, find the parent
        if h.strip() == '@jinja template' or h.strip() == '@jinja inputs':
            # not at @jinja, find from parents
            oldp, p = find_root(p)

        elif h.startswith('@jinja variable'):
            # not at @jinja, first find @jinja inputs, then @jinja
            oldp, p = find_inputs(p)

        def untangle(c: Cmdr, p: Position) -> str:
            return g.getScript(c, p,
                useSelectedText=False,
                useSentinels=False)

        template_data = {}
        for child in p.children():
            if child.h == '@jinja template':
                template_path = g.finalize_join(c.getNodePath(p), untangle(c, child).strip())
            elif child.h == '@jinja inputs':
                for template_var_node in child.children():
                    # pylint: disable=line-too-long
                    template_data[template_var_node.h.replace('@jinja variable', '').strip()] = untangle(c, template_var_node).strip()

        if not template_path:
            g.es(
                "No template_path given. "
                "Your @jinja node should contain a child node 'template' "
                "with the path to the template (relative or absolute)")
            return

        tmpl = Template(Path(template_path).read_text())
        out = tmpl.render(template_data)
        w = self.get_base_text_widget()
        self.show()
        w.setPlainText(out)
        p.b = out
        c.redraw(p)

        # focus back on entry node
        if oldp:
            c.redraw(oldp)
    #@+node:ekr.20110320120020.14479: *4* vr.update_svg
    # http://doc.trolltech.com/4.4/qtsvg.html
    # http://doc.trolltech.com/4.4/painting-svgviewer.html
    def update_svg(self, s: str, keywords: Any) -> None:
        """
        Show an svg image in the VR pane.
        
        `s` may be a path to the image or the image itself.
        """
        if 0:  # Use webengine. Works, but scaling is too big.
            w = self.create_web_engineview()
            w.setHtml(s)
            w.show()
        else:  # Legacy:  Better scaling.
            if hasattr(QtSvg, "QSvgWidget"):  # #2134
                QSvgWidget = QtSvg.QSvgWidget
            else:
                try:
                    from PyQt6 import QtSvgWidgets
                    QSvgWidget = QtSvgWidgets.QSvgWidget
                except Exception:
                    QSvgWidget = None
            if not QSvgWidget:
                g.print_unique_message('svg rendering requires PyQt6-WebEngine')
                w = self.get_base_text_widget()
                w.setPlainText(s)
                return
            if isinstance(self.w, QSvgWidget):
                w = self.w
            else:
                w = self.w = QSvgWidget()
                self.embed_widget(w)

            # Compute the contents.
            if s.strip().startswith('<'):
                # Assume it is the svg (xml) source.
                # Sensitive to leading blank lines.
                s = textwrap.dedent(s).strip()
                s_bytes = g.toEncodedString(s)
                self.show()
                w.load(QtCore.QByteArray(s_bytes))
                w.show()
            else:
                # Get a filename from the headline or body text.
                ok, path = self.get_fn(s, '@svg')
                if ok:
                    self.show()
                    w.load(path)
                    w.show()
    #@+node:ekr.20241231121247.1: *4* vr.update_typst
    def update_typst(self, s: str, keywords: Any) -> None:
        """Display the typest text in `s` in the VR pane."""
        # Create a new QWebEngineView.
        w = self.create_web_engineview_with_pdf()
        if not has_webengineview:
            g.print_unique_message('typst rendering requires PyQt6-WebEngine')
            w.setHtml(s)
            self.show()
            return

        sfn = 'temp.tex'
        tex_path = self.resolve_path(sfn)
        if not tex_path:
            g.print_unique_message(f"File not found: {sfn}")
            return

        # Create the .pdf file.
        pdf_path = tex_path.replace('.tex', '.pdf')
        contents = self.typst_template + '\n\n' + s.strip() + '\n'
        with open(tex_path, 'w') as f:
            f.write(contents)
            g.print_unique_message(f"Wrote {tex_path}")
        g.execute_shell_commands([
            f"typst compile {tex_path}",  # Invoke the typst app.
        ])

        # Render the .pdf file.
        url = QUrl.fromLocalFile(pdf_path)
        # https://www.rfc-editor.org/rfc/rfc8118
        url.setFragment(f"zoom={self.pdf_zoom}")
        w.load(url)
        self.show()
    #@+node:ekr.20110321005148.14537: *4* vr.update_url
    def update_url(self, s: str, keywords: Any) -> None:
        """Display the url in `s` in the VR pane."""
        c, p = self.c, self.c.p
        colorizer = c.frame.body.colorizer
        language = colorizer.scanLanguageDirectives(p)
        if language == 'asciidoc':
            p.update_asciidoc(s, keywords)
        elif language in ('rest', 'rst'):
            self.update_rst(s, keywords)
        elif language in ('markdown', 'md'):
            self.update_md(s, keywords)
        elif self.default_kind in ('rest', 'rst'):
            self.update_rst(s, keywords)
        elif self.default_kind in ('markdown', 'md'):
            self.update_md(s, keywords)
        else:
            # Do nothing.
            g.trace('ignore', s)
            w = self.get_base_text_widget()
            self.show()
            w.setPlainText('')
    #@+node:ekr.20110322031455.5765: *3* vr: utils...
    #@+node:ekr.20190424083049.1: *4* vr.get_base_text_widget
    def get_base_text_widget(self) -> QWidget:
        """Create a QTextBrowser."""
        c = self.c
        if isinstance(self.w, QtWidgets.QTextBrowser):
            return self.w

        self.destroy_widgets()
        self.browser = self.w = w = QtWidgets.QTextBrowser()
        self.embed_widget(w)  # Creates w.wrapper

        text_name = 'body-text-renderer'
        w.setObjectName(text_name)
        w.setReadOnly(True)
        # Create the standard Leo bindings.
        wrapper_name = 'rendering-pane-wrapper'
        wrapper = qt_text.QTextEditWrapper(w, wrapper_name, c)
        w.leo_wrapper = wrapper
        c.k.completeAllBindingsForWidget(wrapper)
        w.setWordWrapMode(WrapMode.WrapAtWordBoundaryOrAnywhere)

        def contextMenuCallback(point: Any) -> None:
            """LeoQtTree: Callback for customContextMenuRequested events."""
            # #1286.
            w = self  # Required.
            g.app.gui.onContextMenu(c, w, point)

        # #1286.
        w.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        w.customContextMenuRequested.connect(contextMenuCallback)

        def handleClick(url: str, w: QWidget = w) -> None:
            wrapper = qt_text.QTextEditWrapper(w, name='vr-body', c=c)
            event = g.Bunch(c=c, w=wrapper)
            g.openUrlOnClick(event, url=url)

        w.anchorClicked.connect(handleClick)
        w.setOpenLinks(False)
        return w
    #@+node:ekr.20110320120020.14483: *4* vr.get_kind
    def get_kind(self, p: Position) -> Optional[str]:
        """Return the proper rendering kind for node p."""

        p0 = p  # Special case selected position.

        def get_language(p: Position) -> str:
            """
            Return the language in effect at position p.
            Headline directives over-ride normal Leo directives in body text.
            """
            h = p.h
            # Case 1: Look for headline directives.
            if h.startswith('@'):
                i = g.skip_id(h, 1, chars='-')
                word = h[1:i].lower().strip()
                if word in self.dispatch_dict:
                    return word

            # Case 2: Look at body text in c.p.
            #         We *must* assume the first @language directive is in effect.
            if p == p0:
                # Careful: never use c.target_language as a default.
                return g.findFirstValidAtLanguageDirective(p.b)

            # Case 3: Look at body text in ancestor nodes.
            #         Ignore nodes with ambiguous @language directives!
            m_list = list(g.g_language_pat.finditer(p.b))
            if len(m_list) == 1:
                m = m_list[0]
                language = m.group(1)
                if g.isValidLanguage(language):
                    return language
            return None

        # #1287: Honor both kind of directives node by node.
        for p1 in p.self_and_parents():
            language = get_language(p1)
            if language:
                if language in ('md', 'markdown'):
                    return language if got_markdown else None
                if language in ('rest', 'rst'):
                    return language if got_docutils else None
                if language in self.dispatch_dict:
                    return language
        return None
    #@+node:ekr.20110320233639.5776: *4* vr.get_fn
    def get_fn(self, s: str, tag: str) -> tuple[bool, str]:
        """
        Return an absolute path using s or c.p.h.
        
        Resolve relative paths using the outline's directory.
        """
        c = self.c
        fn = s or c.p.h[len(tag) :]
        fn = fn.strip()

        # Similar to code in g.computeFileUrl.
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
        g.trace(fn)
        return ok, fn
    #@+node:ekr.20110321005148.14536: *4* vr.get_url
    def get_url(self, s: str, tag: str) -> str:
        p = self.c.p
        url = s or p.h[len(tag) :]
        url = url.strip()
        return url
    #@+node:ekr.20110320120020.14485: *4* vr.remove_directives
    def remove_directives(self, s: str) -> str:
        lines = g.splitLines(s)
        result = []
        for s1 in lines:
            if s1.startswith('@'):
                i = g.skip_id(s1, 1)
                word = s1[1:i]
                if word in g.globalDirectiveList:
                    continue
            result.append(s1)
        return ''.join(result)
    #@+node:ekr.20250102053905.1: *4* vr.resolve_path
    def resolve_path(self, path: str) -> str:
        """Resolve the given path to an absolute path."""
        c = self.c
        if not os.path.isfile(path):
            return ''
        if os.path.isabs(path):
            return path

        # Similar to code in g.computeFileUrl.
        if path.startswith('~'):
            path = path[1:]
            path = g.finalize(path)
        else:
            # Handle ancestor @path directives.
            if c and c.fileName():
                base = c.getNodePath(c.p)
                path = g.finalize_join(g.os_path_dirname(c.fileName()), base, path)
            else:
                path = g.finalize(path)
        return path
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

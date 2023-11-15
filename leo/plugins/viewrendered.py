#@+leo-ver=5-thin
#@+node:tbrown.20100318101414.5990: * @file ../plugins/viewrendered.py
#@+<< vr docstring >>
#@+node:tbrown.20100318101414.5991: ** << vr docstring >>
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

Terry Brown created this initial version of this plugin, and the
free_layout and NestedSplitter plugins used by viewrendered.

Edward K. Ream generalized this plugin and added communication and
coordination between the free_layout, NestedSplitter and viewrendered
plugins.

Jacob Peck added markdown support to this plugin.

"""
#@-<< vr docstring >>
#@+<< vr imports >>
#@+node:tbrown.20100318101414.5993: ** << vr imports >>
# pylint: disable = c-extension-no-member
from __future__ import annotations
from collections.abc import Callable
import json
import os
from pathlib import Path
import shutil
import textwrap
from typing import Any, Optional, TYPE_CHECKING
from urllib.request import urlopen
from leo.core import leoGlobals as g
from leo.core.leoQt import isQt5, QtCore, QtGui, QtWidgets
from leo.core.leoQt import phonon, QtMultimedia, QtSvg, QtWebKitWidgets
from leo.core.leoQt import ContextMenuPolicy, Orientation, WrapMode
from leo.plugins import qt_text
from leo.plugins import free_layout
try:
    BaseTextWidget = QtWebKitWidgets.QWebView  # type:ignore
except Exception:
    BaseTextWidget = QtWidgets.QTextBrowser  # type:ignore
#
# Optional third-party imports...
#
# Docutils.
try:
    # pylint: disable=import-error
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
#
# Jinja.
try:
    from jinja2 import Template
except ImportError:
    Template = None  # type:ignore
#
# Markdown.
try:
    # pylint: disable=import-error
    from markdown import markdown
    got_markdown = True
except ImportError:
    got_markdown = False  # type:ignore
#
# nbformat (@jupyter) support.
try:
    # pylint: disable=import-error
    import nbformat
    from nbconvert import HTMLExporter
    # from traitlets.config import Config
except ImportError:
    nbformat = None

try:
    # pylint: disable=import-error
    import pyperclip
except Exception:
    pyperclip = None

got_pyplot = False
try:
    # pylint: disable=import-error
    from matplotlib import pyplot
    got_pyplot = True
except ImportError:
    pass

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< vr imports >>
#@+<< vr annotations >>
#@+node:ekr.20220828161918.1: ** << vr annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Widget = Any
#@-<< vr annotations >>
# pylint: disable=no-member
trace = False  # This global trace is convenient.
asciidoctor_exec = shutil.which('asciidoctor')
asciidoc3_exec = shutil.which('asciidoc3')
pandoc_exec = shutil.which('pandoc')
#@+<< vr set BaseTextWidget >>
#@+node:ekr.20190424081947.1: ** << vr set BaseTextWidget >>
#@-<< vr set BaseTextWidget >>
#@+<< vr define html templates >>
#@+node:ekr.20170324090828.1: ** << vr define html templates >>
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
    <script src='https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'>
    </script>
</head>
<body bgcolor="#fffbdc">
%s
</body>
</html>
'''
#@-<< vr define html templates >>
controllers: dict[str, Any] = {}  # Dict[c.hash(), PluginControllers (QWidget's)].
layouts: dict[str, tuple] = {}  # Dict[c.hash(), tuple[layout_when_closed, layout_when_open]].
#@+others
#@+node:ekr.20110320120020.14491: ** vr.Top-level
#@+node:tbrown.20100318101414.5994: *3* vr.decorate_window
def decorate_window(w: Wrapper) -> None:
    # Do not override the style sheet!
    # This interferes with themes
        # w.setStyleSheet(stickynote_stylesheet)
    g.app.gui.attachLeoIcon(w)
    w.resize(600, 300)
#@+node:tbrown.20100318101414.5995: *3* vr.init
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
#@+node:ekr.20180825025924.1: *3* vr.isVisible
def isVisible() -> bool:
    """Return True if the VR pane is visible."""
#@+node:ekr.20110317024548.14376: *3* vr.onCreate
def onCreate(tag: str, keys: dict) -> None:
    c = keys.get('c')
    if not c:
        return
    provider = ViewRenderedProvider(c)
    free_layout.register_provider(c, provider)
#@+node:vitalije.20170712174157.1: *3* vr.onClose
def onClose(tag: str, keys: dict) -> None:
    c = keys.get('c')
    h = c.hash()
    vr = controllers.get(h)
    if vr:
        c.bodyWantsFocus()
        del controllers[h]
        vr.deactivate()
        vr.deleteLater()
#@+node:tbrown.20110629132207.8984: *3* vr.show_scrolled_message
def show_scrolled_message(tag: str, kw: Any) -> bool:
    if g.unitTesting:
        return None  # This just slows the unit tests.
    c = kw.get('c')
    flags = kw.get('flags') or 'rst'
    vr = viewrendered(event=kw)
    title = kw.get('short_title', '').strip()
    vr.setWindowTitle(title)
    s = '\n'.join([
        title,
        '=' * len(title),
        '',
        kw.get('msg')
    ])
    vr.show_dock_or_pane()  # #1332.
    vr.update(
        tag='show-scrolled-message',
        keywords={'c': c, 'force': True, 's': s, 'flags': flags},
    )
    return True
#@+node:vitalije.20170713082256.1: *3* vr.split_last_sizes
def split_last_sizes(sizes: list[int]) -> list[int]:
    result = [2 * x for x in sizes[:-1]]
    result.append(sizes[-1])
    result.append(sizes[-1])
    return result
#@+node:ekr.20110320120020.14490: ** vr.Commands
#@+node:ekr.20131213163822.16471: *3* g.command('preview')
@g.command('preview')
def preview(event: Event) -> None:
    """A synonym for the vr-toggle command."""
    toggle_rendering_pane(event)
#@+node:tbrown.20100318101414.5998: *3* g.command('vr')
@g.command('vr')
def viewrendered(event: Event) -> Optional[Any]:
    """Open render view for commander"""
    global controllers, layouts
    if g.app.gui.guiName() != 'qt':
        return None
    c = event.get('c')
    if not c:
        return None
    h = c.hash()
    vr = controllers.get(h)
    if not vr:
        controllers[h] = vr = ViewRenderedController(c)
    # Add the pane to the splitter.
    layouts[h] = c.db.get('viewrendered_default_layouts', (None, None))
    vr._ns_id = '_leo_viewrendered'  # for free_layout load/save
    vr.splitter = splitter = c.free_layout.get_top_splitter()
    if splitter:
        vr.store_layout('closed')
        sizes = split_last_sizes(splitter.sizes())
        ok = splitter.add_adjacent(vr, 'bodyFrame', 'right-of')
        if not ok:
            splitter.insert(0, vr)
        elif splitter.orientation() == Orientation.Horizontal:
            splitter.setSizes(sizes)
        vr.adjust_layout('open')
    c.bodyWantsFocusNow()
    return vr
#@+node:ekr.20130413061407.10362: *3* g.command('vr-contract')
@g.command('vr-contract')
def contract_rendering_pane(event: Event) -> None:
    """Contract the rendering pane."""
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    vr.contract()
#@+node:ekr.20130413061407.10361: *3* g.command('vr-expand')
@g.command('vr-expand')
def expand_rendering_pane(event: Event) -> None:
    """Expand the rendering pane."""
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    vr.expand()
#@+node:ekr.20110917103917.3639: *3* g.command('vr-hide')
@g.command('vr-hide')
def hide_rendering_pane(event: Event) -> None:
    """Close the rendering pane."""
    global controllers, layouts
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    if vr.pyplot_active:
        g.es_print('can not close VR pane after using pyplot')
        return
    vr.store_layout('open')
    vr.deactivate()
    vr.deleteLater()

    def at_idle(c: Cmdr = c, _vr: ViewRenderedController = vr) -> None:
        _vr.adjust_layout('closed')
        c.bodyWantsFocusNow()

    QtCore.QTimer.singleShot(0, at_idle)
    h = c.hash()
    c.bodyWantsFocus()
    if vr == controllers.get(h):
        del controllers[h]
    else:
        g.trace('Can not happen: no controller for %s' % (c))
# Compatibility

close_rendering_pane = hide_rendering_pane
#@+node:ekr.20110321072702.14507: *3* g.command('vr-lock')
@g.command('vr-lock')
def lock_rendering_pane(event: Event) -> None:
    """Lock the rendering pane."""
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    if not vr.locked:
        vr.lock()
#@+node:ekr.20110320233639.5777: *3* g.command('vr-pause-play')
@g.command('vr-pause-play-movie')
def pause_play_movie(event: Event) -> None:
    """Pause or play a movie in the rendering pane."""
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    vp = vr.vp
    if not vp:
        return
    f = vp.pause if vp.isPlaying() else vp.play
    f()
#@+node:ekr.20110317080650.14386: *3* g.command('vr-show')
@g.command('vr-show')
def show_rendering_pane(event: Event) -> None:
    """Show the rendering pane."""
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    vr.show_dock_or_pane()
#@+node:ekr.20131001100335.16606: *3* g.command('vr-toggle')
@g.command('vr-toggle')
def toggle_rendering_pane(event: Event) -> None:
    """Toggle the rendering pane."""
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    if g.app.gui.guiName() != 'qt':
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
        vr.hide()  # So the toggle below will work.
    if vr.isHidden():
        show_rendering_pane(event)
    else:
        hide_rendering_pane(event)
#@+node:ekr.20130412180825.10345: *3* g.command('vr-unlock')
@g.command('vr-unlock')
def unlock_rendering_pane(event: Event) -> None:
    """Pause or play a movie in the rendering pane."""
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    if vr.locked:
        vr.unlock()
#@+node:ekr.20110321151523.14464: *3* g.command('vr-update')
@g.command('vr-update')
def update_rendering_pane(event: Event) -> None:
    """Update the rendering pane"""
    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    vr.update(tag='view', keywords={'c': c, 'force': True})
#@+node:vitalije.20170712195827.1: *3* @g.command('vr-zoom')
@g.command('vr-zoom')
def zoom_rendering_pane(event: Event) -> None:

    global controllers
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    flc = c.free_layout
    if vr.zoomed:
        for ns in flc.get_top_splitter().top().self_and_descendants():
            if hasattr(ns, '_unzoom'):
                # this splitter could have been added since
                ns.setSizes(ns._unzoom)
    else:
        parents = []
        parent = vr
        while parent:
            parents.append(parent)
            parent = parent.parent()
        for ns in flc.get_top_splitter().top().self_and_descendants():
            # FIXME - shouldn't be doing this across windows
            ns._unzoom = ns.sizes()
            for i in range(ns.count()):
                w = ns.widget(i)
                if w in parents:
                    sizes = [0] * len(ns._unzoom)
                    sizes[i] = sum(ns._unzoom)
                    ns.setSizes(sizes)
                    break
    vr.zoomed = not vr.zoomed
#@+node:tbrown.20110629084915.35149: ** class ViewRenderedProvider
class ViewRenderedProvider:
    #@+others
    #@+node:tbrown.20110629084915.35154: *3* vr.__init__
    def __init__(self, c: Cmdr) -> None:
        self.c = c
        # Careful: we may be unit testing.
        if hasattr(c, 'free_layout'):
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.register_provider(self)
    #@+node:tbrown.20110629084915.35151: *3* vr.ns_provide
    def ns_provide(self, id_: str) -> Optional[Widget]:
        global controllers, layouts
        # #1678: duplicates in Open Window list
        if id_ == self.ns_provider_id():
            c = self.c
            vr = controllers.get(c.hash()) or ViewRenderedController(c)
            h = c.hash()
            controllers[h] = vr
            if not layouts.get(h):
                layouts[h] = c.db.get('viewrendered_default_layouts', (None, None))
            # return ViewRenderedController(self.c)
            return vr
        return None
    #@+node:ekr.20200917062806.1: *3* vr.ns_provider_id
    def ns_provider_id(self) -> str:
        # return f"vr_id:{self.c.shortFileName()}"
        return '_leo_viewrendered'
    #@+node:tbrown.20110629084915.35150: *3* vr.ns_provides
    def ns_provides(self) -> list[tuple[str, str]]:
        # #1671: Better Window names.
        # #1678: duplicates in Open Window list
        return [('Viewrendered', self.ns_provider_id())]
    #@+node:ekr.20200917063221.1: *3* vr.ns_title
    def ns_title(self, id_: str) -> Optional[str]:
        if id_ != self.ns_provider_id():
            return None
        filename = self.c.shortFileName() or 'Unnamed file'
        return f"Viewrendered: {filename}"
    #@-others
#@+node:ekr.20110317024548.14375: ** class ViewRenderedController (QWidget)
class ViewRenderedController(QtWidgets.QWidget):  # type:ignore
    """A class to control rendering in a rendering pane."""
    #@+others
    #@+node:ekr.20110317080650.14380: *3*  vr.ctor & helpers
    def __init__(self, c: Cmdr, parent: Position = None) -> None:
        """Ctor for ViewRenderedController class."""
        self.c = c
        # Create the widget.
        super().__init__(parent)
        self.create_pane(parent)
        # Set the ivars.
        self.active = False
        self.badColors: list[str] = []
        self.delete_callback: Callable = None
        self.gnx: str = None
        self.graphics_class = QtWidgets.QGraphicsWidget
        self.pyplot_canvas: Widget = None
        self.gs: Widget = None  # For @graphics-script: a QGraphicsScene
        self.gv: Widget = None  # For @graphics-script: a QGraphicsView
        self.inited = False
        self.length = 0  # The length of previous p.b.
        self.locked = False
        self.pyplot_active = False
        self.scrollbar_pos_dict: dict[VNode, Position] = {}  # Keys are vnodes, values are positions.
        self.sizes: list[int] = []  # Saved splitter sizes.
        self.splitter = None
        self.splitter_index: int = None  # The index of the rendering pane in the splitter.
        self.title: str = None
        self.vp: Widget = None  # The present video player.
        self.w: Wrapper = None  # The present widget in the rendering pane.
        # User settings.
        self.reloadSettings()
        self.node_changed = True
        # Init.
        self.create_dispatch_dict()
        self.activate()
        self.zoomed = False
    #@+node:ekr.20110320120020.14478: *4* vr.create_dispatch_dict
    def create_dispatch_dict(self) -> dict[str, Callable]:
        pc = self
        d = {
            'asciidoc': pc.update_asciidoc,
            'big': pc.update_rst,
            'html': pc.update_html,
            'graphics-script': pc.update_graphics_script,
            'image': pc.update_image,
            'jupyter': pc.update_jupyter,
            'latex': pc.update_latex,
            'markdown': pc.update_md,
            'md': pc.update_md,
            'movie': pc.update_movie,
            'networkx': pc.update_networkx,
            'pandoc': pc.update_pandoc,
            'pyplot': pc.update_pyplot,
            'rest': pc.update_rst,
            'rst': pc.update_rst,
            'svg': pc.update_svg,
            'plantuml': pc.update_plantuml,
            'jinja': pc.update_jinja,
            # 'url': pc.update_url,
            # 'xml': pc.update_xml,
        }
        pc.dispatch_dict = d
        return d
    #@+node:ekr.20171114150510.1: *4* vr.reloadSettings
    def reloadSettings(self) -> None:
        c = self.c
        c.registerReloadSettings(self)
        self.auto_create = c.config.getBool('view-rendered-auto-create', False)
        self.background_color = c.config.getColor('rendering-pane-background-color') or 'white'
        self.default_kind = c.config.getString('view-rendered-default-kind') or 'rst'

    #@+node:ekr.20190614065659.1: *4* vr.create_pane
    def create_pane(self, parent: Position) -> None:
        """Create the VR pane or dock."""
        if g.unitTesting:
            return
        # Create the inner contents.
        self.setObjectName('viewrendered_pane')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
    #@+node:ekr.20110317080650.14381: *3* vr.activate
    def activate(self) -> None:
        """Activate the vr-window."""
        pc = self
        if pc.active:
            return
        pc.inited = True
        pc.active = True
        g.registerHandler('select2', pc.update)
        g.registerHandler('idle', pc.update)
    #@+node:vitalije.20170712183051.1: *3* vr.adjust_layout (legacy only)
    def adjust_layout(self, which: str) -> None:
        global layouts
        c = self.c
        splitter = self.splitter
        deflo = c.db.get('viewrendered_default_layouts', (None, None))
        loc, loo = layouts.get(c.hash(), deflo)
        if which == 'closed' and loc and splitter:
            splitter.load_layout(c, loc)
        elif which == 'open' and loo and splitter:
            splitter.load_layout(c, loo)
    #@+node:tbrown.20110621120042.22676: *3* vr.closeEvent
    def closeEvent(self, event: Event) -> None:
        """Close the vr window."""
        self.deactivate()
    #@+node:ekr.20130413061407.10363: *3* vr.contract & expand
    def contract(self) -> None:
        self.change_size(-100)

    def expand(self) -> None:
        self.change_size(100)

    def change_size(self, delta: int) -> None:
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
    #@+node:ekr.20110317080650.14382: *3* vr.deactivate
    def deactivate(self) -> None:
        """Deactivate the vr window."""
        pc = self
        # Never disable the idle-time hook: other plugins may need it.
        g.unregisterHandler('select2', pc.update)
        g.unregisterHandler('idle', pc.update)
        pc.active = False
    #@+node:ekr.20110321072702.14508: *3* vr.lock/unlock
    def lock(self) -> None:
        """Lock the vr pane."""
        g.note('rendering pane locked')
        self.locked = True

    def unlock(self) -> None:
        """Unlock the vr pane."""
        g.note('rendering pane unlocked')
        self.locked = False
    #@+node:ekr.20160921071239.1: *3* vr.set_html
    def set_html(self, s: str, w: Wrapper) -> None:
        """Set text in w to s, preserving scroll position."""
        pc = self
        p = pc.c.p
        sb = w.verticalScrollBar()
        if sb:
            d = pc.scrollbar_pos_dict
            if pc.node_changed:
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
    #@+node:ekr.20190614133401.1: *3* vr.show_dock_or_pane
    def show_dock_or_pane(self) -> None:

        c, vr = self.c, self
        vr.activate()
        vr.show()
        vr.adjust_layout('open')
        c.bodyWantsFocusNow()
    #@+node:vitalije.20170712183618.1: *3* vr.store_layout
    def store_layout(self, which: str) -> None:
        global layouts
        c = self.c
        h = c.hash()
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
    #@+node:ekr.20110319143920.14466: *3* vr.underline
    def underline(self, s: str) -> str:
        """Generate rST underlining for s."""
        ch = '#'
        n = max(4, len(g.toEncodedString(s, reportErrors=False)))
        # return '%s\n%s\n%s\n\n' % (ch*n,s,ch*n)
        return '%s\n%s\n\n' % (s, ch * n)
    #@+node:ekr.20101112195628.5426: *3* vr.update & helpers
    # Must have this signature: called by leoPlugins.callTagHandler.

    def update(self, tag: str, keywords: Any) -> None:
        """Update the vr pane. Called at idle time."""
        pc = self
        p = pc.c.p
        # #1256.
        if self.locked:
            return
        if pc.must_update(keywords):
            #
            # Suppress updates until we change nodes.
            pc.node_changed = pc.gnx != p.v.gnx
            pc.gnx = p.v.gnx
            pc.length = len(p.b)  # not s
            #
            # Remove Leo directives.
            s = keywords.get('s') if 's' in keywords else p.b
            s = pc.remove_directives(s)
            #
            # Use plain text if we are hidden.
            # This avoids annoying messages with rst.
            if pc.isHidden():
                w = pc.ensure_text_widget()
                w.setPlainText(s)
                return
            #
            # Dispatch based on the computed kind.
            kind = keywords.get('flags') if 'flags' in keywords else pc.get_kind(p)
            if not kind:
                # Do *not* try to render plain text.
                w = pc.ensure_text_widget()
                w.setPlainText(s)
                pc.show()  # Must be last.
                return
            f = pc.dispatch_dict.get(kind)
            if not f:
                g.trace('no handler for kind: %s' % kind)
                f = pc.update_rst
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
    #@+node:ekr.20190424083049.1: *4* vr.create_base_text_widget
    def create_base_text_widget(self) -> Wrapper:
        """Create a QWebView or a QTextBrowser."""
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
    #@+node:ekr.20110320120020.14486: *4* vr.embed_widget & helper
    def embed_widget(self, w: Wrapper, delete_callback: Callable = None) -> None:
        """Embed widget w in the free_layout splitter."""
        pc = self
        c = pc.c
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
            w.setWordWrapMode(WrapMode.WrapAtWordBoundaryOrAnywhere)
    #@+node:ekr.20110321072702.14510: *5* vr.setBackgroundColor
    def setBackgroundColor(self, colorName: str, name: str, w: Wrapper) -> None:
        """Set the background color of the vr pane."""
        # pylint: disable = using-constant-test
        if 0:  # Do not do this! It interferes with themes.
            pc = self
            if not colorName:
                return
            styleSheet = 'QTextEdit#%s { background-color: %s; }' % (name, colorName)
            if QtGui.QColor(colorName).isValid():
                w.setStyleSheet(styleSheet)
            elif colorName not in pc.badColors:
                pc.badColors.append(colorName)
                g.warning('invalid body background color: %s' % (colorName))
    #@+node:ekr.20110320120020.14476: *4* vr.must_update
    def must_update(self, keywords: Any) -> bool:
        """Return True if we must update the rendering pane."""
        pc = self
        c, p = pc.c, pc.c.p
        if g.unitTesting:
            return False
        if keywords.get('force'):
            pc.active = True
            return True
        if c != keywords.get('c') or not pc.active:
            return False
        if pc.locked:
            return False
        if pc.gnx != p.v.gnx:
            return True
        if len(p.b) != pc.length:
            if pc.get_kind(p) in ('html', 'pyplot'):
                pc.length = len(p.b)
                return False  # Only update explicitly.
            return True
        # This trace would be called at idle time.
            # g.trace('no change')
        return False
    #@+node:ekr.20191004143229.1: *4* vr.update_asciidoc & helpers
    def update_asciidoc(self, s: str, keywords: Any) -> None:
        """Update asciidoc in the vr pane."""
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
                self.set_html(s2, w)
                return
            except Exception:
                g.es_exception()
        self.update_rst(s, keywords)
    #@+node:ekr.20191004144242.1: *5* vr.make_asciidoc_title
    def make_asciidoc_title(self, s: str) -> str:
        """Generate an asciiidoc title for s."""
        line = '#' * (min(4, len(s)))
        return f"{line}\n{s}\n{line}\n\n"
    #@+node:ekr.20191004143805.1: *5* vr.convert_to_asciidoctor
    def convert_to_asciidoctor(self, s: str) -> str:
        """Convert s to html using the asciidoctor or asciidoc processor."""
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
        """Update the graphics script in the vr pane."""
        pc = self
        c = pc.c
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

            def delete_callback() -> None:
                for w in (pc.gs, pc.gv):
                    w.deleteLater()
                pc.gs = pc.gv = None

            pc.embed_widget(w, delete_callback=delete_callback)
        c.executeScript(
            script=s,
            namespace={'gs': pc.gs, 'gv': pc.gv})
    #@+node:ekr.20110321005148.14534: *4* vr.update_html
    update_html_count = 0

    def update_html(self, s: str, keywords: Any) -> None:
        """Update html in the vr pane."""
        pc = self
        c = pc.c
        if pc.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert w == pc.w
        else:
            w = pc.w
        if isQt5:
            w.hide()  # This forces a proper update.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:ekr.20110320120020.14482: *4* vr.update_image
    def update_image(self, s: str, keywords: Any) -> None:
        """Update an image in the vr pane."""
        pc = self
        if not s.strip():
            return
        lines = g.splitLines(s) or []
        fn = lines and lines[0].strip()
        if not fn:
            return
        w = pc.ensure_text_widget()
        ok, path = pc.get_fn(fn, '@image')
        if not ok:
            w.setPlainText('@image: file not found: %s' % (path))
            return
        path = path.replace('\\', '/')
        template = image_template % (path)
        # Only works in Python 3.x.
        # Sensitive to leading blank lines.
        template = textwrap.dedent(template).strip()
        # template = g.toUnicode(template)
        pc.show()
        w.setReadOnly(False)
        w.setHtml(template)
        w.setReadOnly(True)
    #@+node:ekr.20170105124347.1: *4* vr.update_jupyter & helper
    update_jupyter_count = 0

    def update_jupyter(self, s: str, keywords: Any) -> None:
        """Update @jupyter node in the vr pane."""
        pc = self
        c = pc.c
        if pc.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            pc.embed_widget(w)
            assert w == pc.w
        else:
            w = pc.w

        s = self.get_jupyter_source(c)
        w.hide()  # This forces a proper update.
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()

        if pyperclip:
            pyperclip.copy(s)
    #@+node:ekr.20180311090852.1: *5* vr.get_jupyter_source
    def get_jupyter_source(self, c: Cmdr) -> str:
        """Return the html for the @jupyer node."""
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
            pass  # Assume the result is html.
        return s
    #@+node:ekr.20170324064811.1: *4* vr.update_latex & helper
    def update_latex(self, s: str, keywords: Any) -> None:
        """Update latex in the vr pane."""
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
            assert w == pc.w
        else:
            w = pc.w
        w.hide()  # This forces a proper update.
        s = self.create_latex_html(s)
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:ekr.20170324085132.1: *5* vr.create_latex_html
    def create_latex_html(self, s: str) -> str:
        """Create an html page embedding the latex code s."""
        # pylint: disable=deprecated-method
        try:
            import html
            escape = html.escape
        except AttributeError:
            import cgi
            escape = cgi.escape
        html_s = escape(s)
        template = latex_template % (html_s)
        template = textwrap.dedent(template).strip()
        return template
    #@+node:peckj.20130207132858.3671: *4* vr.update_md & helper
    def update_md(self, s: str, keywords: Any) -> None:
        """Update markdown text in the vr pane."""
        pc = self
        c = pc.c
        p = c.p
        s = s.strip().strip('"""').strip("'''").strip()
        isHtml = s.startswith('<') and not s.startswith('<<')
        # Do this regardless of whether we show the widget or not.
        w = pc.ensure_text_widget()
        assert pc.w
        if s:
            pc.show()
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
    #@+node:ekr.20160921134552.1: *5* convert_to_markdown
    def convert_to_markdown(self, s: str) -> str:
        """Convert s to html using the markdown processor."""
        pc = self
        c, p = pc.c, pc.c.p
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        try:
            if pc.title:
                s = pc.underline(pc.title) + s
                pc.title = None
            mdext = c.config.getString('view-rendered-md-extensions') or 'extra'
            mdext = [x.strip() for x in mdext.split(',')]
            s = markdown(s, extensions=mdext)
            s = g.toUnicode(s)
        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                s = 'MD error:\n%s\n\n%s' % (msg, s)
        return s
    #@+node:ekr.20110320120020.14481: *4* vr.update_movie
    movie_warning = False

    def update_movie(self, s: str, keywords: Any) -> None:
        """Update a movie in the vr pane."""
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
            url = QtCore.QUrl.fromLocalFile(path)
            content = QtMultimedia.QMediaContent(url)
            pc.vp = vp = QtMultimedia.QMediaPlayer()
            vp.setMedia(content)
            # Won't play .mp4 files: https://bugreports.qt.io/browse/QTBUG-32783
            vp.play()
        else:
            pc.vp = vp = phonon.VideoPlayer(phonon.VideoCategory)
            vw = vp.videoWidget()
            vw.setObjectName('video-renderer')
            # Embed the widgets

            def delete_callback() -> None:
                if pc.vp:
                    pc.vp.stop()
                    pc.vp.deleteLater()
                    pc.vp = None

            pc.embed_widget(vp, delete_callback=delete_callback)
            pc.show()
            vp = pc.vp
            vp.load(phonon.MediaSource(path))
            vp.play()
    #@+node:ekr.20110320120020.14484: *4* vr.update_networkx
    def update_networkx(self, s: str, keywords: Any) -> None:
        """Update a networkx graphic in the vr pane."""
        pc = self
        w = pc.ensure_text_widget()
        w.setPlainText('')  # 'Networkx: len: %s' % (len(s)))
        pc.show()
    #@+node:ekr.20191006155748.1: *4* vr.update_pandoc & helpers
    def update_pandoc(self, s: str, keywords: Any) -> None:
        """
        Update an @pandoc in the vr pane.

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
                s2 = self.convert_to_pandoc(s)
                self.set_html(s2, w)
            except Exception:
                g.es_exception()
            return
        self.update_rst(s, keywords)
    #@+node:ekr.20191006155748.3: *5* vr.convert_to_pandoc
    def convert_to_pandoc(self, s: str) -> str:
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
    #@+node:ekr.20160928023915.1: *4* vr.update_pyplot
    def update_pyplot(self, s: str, keywords: Any) -> None:
        """Get the pyplot script at c.p.b and show it."""
        if not got_pyplot:
            g.es(('==== Viewrendered: MISSING matplotlib.  Cannot process @pyplot node'))
            return

        c = self.c

        if pyplot.get_backend() != 'module://leo.plugins.pyplot_backend':
            backend = g.finalize_join(
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
            import matplotlib  # Make *sure* this is imported.
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib import animation
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
        # pyplot will throw RuntimeError if we close the pane.
        self.pyplot_active = True
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
        """Update rst in the vr pane."""
        pc = self
        s = s.strip().strip('"""').strip("'''").strip()
        isHtml = s.startswith('<') and not s.startswith('<<')
        # Do this regardless of whether we show the widget or not.
        w = pc.ensure_text_widget()
        assert pc.w
        if s:
            pc.show()
        if got_docutils:
            # Fix #420: viewrendered does not render some nodes
            # Users (rightly) complained, so don't be clever here:
                # c, p = pc.c, pc.c.p
                # force = keywords.get('force')
                # colorizer = c.frame.body.colorizer
                # language = colorizer.scanLanguageDirectives(p)
                # force or language in ('rst', 'rest', 'markdown', 'md'):
            if not isHtml:
                s = pc.convert_to_html(s)
            pc.set_html(s, w)
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
            if self.title:
                s = self.underline(self.title) + s
                self.title = None
            # Call docutils to get the string.
            s = publish_string(s, writer_name='html')
            s = g.toUnicode(s)
        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                s = 'RST error:\n%s\n\n%s' % (msg, s)
        return s

    def update_plantuml(self, s: str, keywords: Any) -> None:
        pc = self
        w = pc.ensure_text_widget()
        path = self.c.p.h[9:].strip()
        print("Plantuml output file name: ", path)
        with open("temp.plantuml", "w") as f:
            f.write(s)
        pth_plantuml_jar = "~/.leo"
        os.system("cat temp.plantuml | java -jar %s/plantuml.jar -pipe > %s" % (pth_plantuml_jar, path))
        template = image_template % (path)
        template = textwrap.dedent(template).strip()
        pc.show()
        w.setReadOnly(False)
        w.setHtml(template)
        w.setReadOnly(True)

    def update_jinja(self, s: str, keywords: Any) -> None:
        pc = self
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
        w = pc.ensure_text_widget()
        pc.show()
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
        # pylint: disable=no-name-in-module
        pc = self
        if hasattr(QtSvg, "QSvgWidget"):  # #2134
            QSvgWidget = QtSvg.QSvgWidget
        else:
            try:
                from PyQt6 import QtSvgWidgets
                QSvgWidget = QtSvgWidgets.QSvgWidget
            except Exception:
                QSvgWidget = None
        if not QSvgWidget:
            w = pc.ensure_text_widget()
            w.setPlainText(s)
            return
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
            s_bytes = g.toEncodedString(s)
            pc.show()
            w.load(QtCore.QByteArray(s_bytes))
            w.show()
        else:
            # Get a filename from the headline or body text.
            ok, path = pc.get_fn(s, '@svg')
            if ok:
                pc.show()
                w.load(path)
                w.show()
    #@+node:ekr.20110321005148.14537: *4* vr.update_url
    def update_url(self, s: str, keywords: Any) -> None:
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
    #@+node:ekr.20110322031455.5765: *4* vr.utils for update helpers...
    #@+node:ekr.20110322031455.5764: *5* vr.ensure_text_widget
    def ensure_text_widget(self) -> Widget:
        """Swap a text widget into the rendering pane if necessary."""
        c, pc = self.c, self
        if pc.must_change_widget(QtWidgets.QTextBrowser):
            # Instantiate a new QTextBrowser.
            # Allow non-ctrl clicks to open url's.
            w = QtWidgets.QTextBrowser()

            def contextMenuCallback(point: Any) -> None:
                """LeoQtTree: Callback for customContextMenuRequested events."""
                # #1286.
                w = self  # Required.
                g.app.gui.onContextMenu(c, w, point)

            # #1286.
            w.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
            w.customContextMenuRequested.connect(contextMenuCallback)

            def handleClick(url: str, w: Widget = w) -> None:
                wrapper = qt_text.QTextEditWrapper(w, name='vr-body', c=c)
                event = g.Bunch(c=c, w=wrapper)
                g.openUrlOnClick(event, url=url)

            w.anchorClicked.connect(handleClick)
            w.setOpenLinks(False)
            pc.embed_widget(w)  # Creates w.wrapper
            assert w == pc.w
        return pc.w
    #@+node:ekr.20110320120020.14483: *5* vr.get_kind
    def get_kind(self, p: Position) -> Optional[str]:
        """Return the proper rendering kind for node p."""

        def get_language(p: Position) -> str:
            """
            Return the language in effect at position p.
            Headline directives over-ride normal Leo directives in body text.
            """
            h = p.h
            # First, look for headline directives.
            if h.startswith('@'):
                i = g.skip_id(h, 1, chars='-')
                word = h[1:i].lower().strip()
                if word in self.dispatch_dict:
                    return word
            # Look for @language directives.
            # Warning: (see #344): don't use c.target_language as a default.
            return g.findFirstValidAtLanguageDirective(p.b)
        #
        #  #1287: Honor both kind of directives node by node.
        for p1 in p.self_and_parents():
            language = get_language(p1)
            if got_markdown and language in ('md', 'markdown'):
                return language
            if got_docutils and language in ('rest', 'rst'):
                return language
            if language and language in self.dispatch_dict:
                return language
        return None
    #@+node:ekr.20110320233639.5776: *5* vr.get_fn
    def get_fn(self, s: str, tag: str) -> tuple[bool, str]:
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
    #@+node:ekr.20110321005148.14536: *5* vr.get_url
    def get_url(self, s: str, tag: str) -> str:
        p = self.c.p
        url = s or p.h[len(tag) :]
        url = url.strip()
        return url
    #@+node:ekr.20110322031455.5763: *5* vr.must_change_widget
    def must_change_widget(self, widget_class: Any) -> bool:
        pc = self
        return not pc.w or pc.w.__class__ != widget_class
    #@+node:ekr.20110320120020.14485: *5* vr.remove_directives
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
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

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
from leo.core.leoQt import QtMultimedia, QtSvg
from leo.core.leoQt import ContextMenuPolicy, Orientation, WrapMode
from leo.plugins import qt_text

BaseTextWidget = QtWidgets.QTextBrowser

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

got_pyplot = False
try:
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
    from leo.core.leoNodes import Position, VNode

    # These need more work!
    Event = Any
    QWidget = QtWidgets.QWidget
    Widget = Any
    Wrapper = Any
#@-<< vr annotations >>
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
#@+node:ekr.20110317024548.14376: *3* vr function: onCreate
def onCreate(tag: str, keys: dict) -> None:
    c = keys.get('c')
    if not c:
        return
    vr = viewrendered(keys)
    g.registerHandler('select2', vr.update)
    g.registerHandler('idle', vr.update)
    vr.active = True
    vr.is_visible = False
    vr.hide()
#@+node:vitalije.20170712174157.1: *3* vr function: onClose
def onClose(tag: str, keys: dict) -> None:
    """
    Handle a close event in the Leo *outline*, not the VR pane.
    
    Delete the per-commander data after idle time.
    """
    c = keys.get('c')
    h = c.hash()
    vr = controllers.get(h)
    if vr and vr.active:
        c.bodyWantsFocus()
        del controllers[h]
        vr.active = False
        vr.deleteLater()
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
    vr = viewrendered(event=kw)
    # Make sure we will show the message.
    vr.is_active = True
    vr.is_visible = True
    # A hack: suppress updates until the node changes.
    vr.gnx = p.v.gnx
    vr.length = p.v.b
    # Render!
    f = vr.dispatch_dict.get('rest')
    f(s, kw)
    vr.show()
    c.bodyWantsFocusNow()
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
    gui = g.app.gui
    if gui.guiName() != 'qt':
        return None
    c = event.get('c')
    if not c:
        return None
    h = c.hash()
    vr = controllers.get(h)
    if vr:
        c.bodyWantsFocusNow()
        return vr
    # Create the VR frame
    controllers[h] = vr = ViewRenderedController(c)
    # Use different layouts depending on the main splitter's *initial* orientation.
    main_splitter = gui.find_widget_by_name(c, 'main_splitter')
    if main_splitter.orientation() == Orientation.Vertical:
        # Share the VR pane with the body pane.
        # Create a new splitter.
        vr_splitter = QtWidgets.QSplitter(orientation=Orientation.Horizontal)
        vr_splitter.setObjectName('vr-splitter')
        main_splitter.addWidget(vr_splitter)
        # First, add the body frame.
        body_frame = gui.find_widget_by_name(c, 'bodyFrame')
        vr_splitter.addWidget(body_frame)
        # Second, add the vr pane.
        vr_splitter.addWidget(vr)
        # Give equal width to all splitter panes.
        vr_splitter.setSizes([1, 1])
        main_splitter.setSizes([1, 1])
    else:
        # Put the VR pane in the secondary splitter.
        secondary_splitter = gui.find_widget_by_name(c, 'secondary_splitter')
        # Add the VR pane to the secondary splitter.
        secondary_splitter.addWidget(vr)
        # Give equal width to the panes in the secondary splitter.
        secondary_splitter.setSizes([1, 1, 1])
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
        vr.show()
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
#@+node:ekr.20240507095853.1: *3* g.command('vr-fully-expand')
@g.command('vr-fully-expand')
def fully_expand_rendering_pane(event: Event) -> None:
    """Expand the rendering pane."""
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
        vr.show()
    vr.fully_expand()
    g.es('VR pane covers body pane', color='red')
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
    vr.hide()
    vr.is_visible = False
    c.bodyWantsFocus()

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
#@+node:ekr.20240507100013.1: *3* g.command('vr-restore-body')
@g.command('vr-restore-body')
def restore_body(event: Event) -> None:
    """Expand the rendering pane."""
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    vr = controllers.get(c.hash())
    if not vr:
        vr = viewrendered(event)
    vr.restore_body()
    g.es('VR pane uncovers body pane', color='red')

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
    vr.show()
    vr.is_visible = True
    c.bodyWantsFocusNow()

#@+node:ekr.20131001100335.16606: *3* g.command('vr-toggle-visibility')
@g.command('vr-toggle-visibility')
@g.command('vr-toggle')  # Legacy
def toggle_rendering_pane(event: Event) -> None:
    """Toggle the visibility of the VR pane."""
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
def toggle_keep_open(event: Event) -> None:
    """Toggle the visibility of the VR pane."""
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
    vr.keep_open = not vr.keep_open
    vr.update('keep-open', {'c': c, 'force': True})
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
#@+node:vitalije.20170712195827.1: *3* g.command('vr-zoom') (rewrite)
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
    if not flc:
        return
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
#@+node:ekr.20110317024548.14375: ** class ViewRenderedController (QWidget)
class ViewRenderedController(QtWidgets.QWidget):  # type:ignore
    """A class to control rendering in a rendering pane."""
    #@+others
    #@+node:ekr.20110317080650.14380: *3*  vr.ctor & helpers
    def __init__(self, c: Cmdr, parent: Widget = None) -> None:
        """Ctor for ViewRenderedController class."""
        self.c = c
        # Create the widget.
        super().__init__(parent)
        self.create_pane(parent)
        # Ivars set by reloadSettings.
        self.auto_create: bool = None
        self.keep_open: bool = None
        # Set the ivars.
        self.active = True
        self.gnx: str = None
        self.gs: Widget = None  # For @graphics-script: a QGraphicsScene
        self.gv: Widget = None  # For @graphics-script: a QGraphicsView
        self.keep_open = False  # True: keep the VR pane open even when showing text.
        self.is_visible = False
        self.length = 0  # The length of previous p.b.
        self.locked = False
        self.scrollbar_pos_dict: dict[VNode, Position] = {}  # Keys are vnodes, values are positions.
        self.vp: Widget = None  # A QtMultimedia.QMediaPlayer or None.
        self.w: Wrapper = None  # The present widget in the rendering pane.
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
            'jupyter': self.update_jupyter,
            'latex': self.update_latex,
            'markdown': self.update_md,
            'md': self.update_md,
            'movie': self.update_movie,
            'networkx': self.update_networkx,
            'pandoc': self.update_pandoc,
            'pyplot': self.update_pyplot,
            'rest': self.update_rst,
            'rst': self.update_rst,
            'svg': self.update_svg,
            'plantuml': self.update_plantuml,
            'jinja': self.update_jinja,
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

    #@+node:ekr.20190614065659.1: *4* vr.create_pane
    def create_pane(self, parent: Position) -> None:
        """Create the VR pane."""
        if g.unitTesting:
            return
        # Create the inner contents.
        self.setObjectName('viewrendered_pane')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
    #@+node:tbrown.20110621120042.22676: *3* vr.closeEvent
    def closeEvent(self, event: Event) -> None:
        """Deactivate callbacks when an Outline closes."""
        self.active = False
        g.unregisterHandler('select2', self.update)
        g.unregisterHandler('idle', self.update)
    #@+node:ekr.20130413061407.10363: *3* vr.contract & expand
    def contract(self) -> None:
        self.change_size(-100)

    def expand(self) -> None:
        self.change_size(100)

    def change_size(self, delta: int) -> None:
        ### Test.
        # if not hasattr(self.c, 'free_layout'):
            # return
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
    def set_html(self, s: str, w: Wrapper) -> None:
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
        """Update the VR pane. Called at idle time."""
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
        if kind or keywords.get('force'):
            f = self.dispatch_dict.get(kind)
        else:
            # Do *not* try to render plain text.
            w = self.ensure_text_widget()
            w.setPlainText(s)
        if f:
            f(s, keywords)
            self.show()
        elif self.keep_open:
            self.show()
        else:
            self.hide()
    #@+node:ekr.20190424083049.1: *4* vr.create_base_text_widget
    def create_base_text_widget(self) -> Wrapper:
        """Create a QTextBrowser."""
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
    #@+node:ekr.20110320120020.14486: *4* vr.embed_widget (test)
    def embed_widget(self, w: Wrapper, delete_callback: Callable = None) -> None:
        """Embed widget w in the free_layout splitter."""
        c = self.c
        self.w = w

        # #3892: Replace the body pane
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeItem(layout.itemAt(0))
        self.layout().addWidget(w)
        w.show()

        # Special inits for text widgets...
        if w.__class__ == QtWidgets.QTextBrowser:
            text_name = 'body-text-renderer'
            w.setObjectName(text_name)
            w.setReadOnly(True)
            # Create the standard Leo bindings.
            wrapper_name = 'rendering-pane-wrapper'
            wrapper = qt_text.QTextEditWrapper(w, wrapper_name, c)
            w.leo_wrapper = wrapper
            c.k.completeAllBindingsForWidget(wrapper)
            w.setWordWrapMode(WrapMode.WrapAtWordBoundaryOrAnywhere)
    #@+node:ekr.20110320120020.14476: *4* vr.must_update
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
            if self.get_kind(p) in ('html', 'pyplot'):
                return False  # Only update explicitly.
            return True
        return False
    #@+node:ekr.20191004143229.1: *4* vr.update_asciidoc & helpers
    def update_asciidoc(self, s: str, keywords: Any) -> None:
        """Update asciidoc in the VR pane."""
        global asciidoctor_exec, asciidoc3_exec
        # Do this regardless of whether we show the widget or not.
        w = self.ensure_text_widget()
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
    #@+node:ekr.20191004144242.1: *5* vr.make_asciidoc_title (not used)
    def make_asciidoc_title(self, s: str) -> str:
        """Generate an asciidoc title for s."""
        line = '#' * (min(4, len(s)))
        return f"{line}\n{s}\n{line}\n\n"
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
        """Update the graphics script in the VR pane."""
        c = self.c
        if g.unitTesting:
            return
        force = keywords.get('force')
        if self.gs and not force:
            return
        if not self.gs:
            splitter = g.app.gui.get_top_splitter()
            # Create the widgets.
            self.gs = QtWidgets.QGraphicsScene(splitter)
            self.gv = QtWidgets.QGraphicsView(self.gs)
            w = self.gv.viewport()  # A QWidget
            # Embed the widgets.

            def delete_callback() -> None:
                for w in (self.gs, self.gv):
                    w.deleteLater()
                self.gs = self.gv = None

            self.embed_widget(w, delete_callback=delete_callback)

        c.executeScript(
            script=s,
            namespace={'gs': self.gs, 'gv': self.gv})
    #@+node:ekr.20110321005148.14534: *4* vr.update_html
    update_html_count = 0

    def update_html(self, s: str, keywords: Any) -> None:
        """Update html in the VR pane."""
        c = self.c
        if self.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            self.embed_widget(w)
            assert w == self.w
        else:
            w = self.w
        w.setHtml(s)
        w.show()
        c.bodyWantsFocusNow()
    #@+node:ekr.20110320120020.14482: *4* vr.update_image
    def update_image(self, s: str, keywords: Any) -> None:
        """Update an image in the VR pane."""
        if not s.strip():
            return
        lines = g.splitLines(s) or []
        fn = lines and lines[0].strip()
        if not fn:
            return
        w = self.ensure_text_widget()
        ok, path = self.get_fn(fn, '@image')
        if not ok:
            w.setPlainText('@image: file not found: %s' % (path))
            return
        path = path.replace('\\', '/')
        template = image_template % (path)
        # Only works in Python 3.x.
        # Sensitive to leading blank lines.
        template = textwrap.dedent(template).strip()
        # template = g.toUnicode(template)
        self.show()
        w.setReadOnly(False)
        w.setHtml(template)
        w.setReadOnly(True)
    #@+node:ekr.20170105124347.1: *4* vr.update_jupyter & helper
    update_jupyter_count = 0

    def update_jupyter(self, s: str, keywords: Any) -> None:
        """Update @jupyter node in the VR pane."""
        c = self.c
        if self.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            self.embed_widget(w)
            assert w == self.w
        else:
            w = self.w

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
    #@+node:ekr.20170324064811.1: *4* vr.update_latex & helper
    def update_latex(self, s: str, keywords: Any) -> None:
        """Update latex in the VR pane."""
        c = self.c
        if sys.platform.startswith('win'):
            g.es_print('latex rendering not ready for Python 3')
            w = self.ensure_text_widget()
            self.show()
            w.setPlainText(s)
            c.bodyWantsFocusNow()
            return
        if self.must_change_widget(BaseTextWidget):
            w = self.create_base_text_widget()
            self.embed_widget(w)
            assert w == self.w
        else:
            w = self.w
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
        """Update markdown text in the VR pane."""
        c = self.c
        p = c.p
        s = s.strip().strip('"""').strip("'''").strip()
        isHtml = s.startswith('<') and not s.startswith('<<')
        # Do this regardless of whether we show the widget or not.
        w = self.ensure_text_widget()
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
        """Update a movie in the VR pane."""
        ok, path = self.get_fn(s, '@movie')
        if not ok:
            w = self.ensure_text_widget()
            w.setPlainText('Not found: %s' % (path))
            return
        if not QtMultimedia:
            if not self.movie_warning:
                self.movie_warning = True
                g.es_print('No QtMultimedia module')
            w = self.ensure_text_widget()
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
        """Update a networkx graphic in the VR pane."""
        w = self.ensure_text_widget()
        w.setPlainText('')  # 'Networkx: len: %s' % (len(s)))
        self.show()
    #@+node:ekr.20191006155748.1: *4* vr.update_pandoc & helpers
    def update_pandoc(self, s: str, keywords: Any) -> None:
        """
        Update an @pandoc in the VR pane.

        There is no such thing as @language pandoc,
        so only @pandoc nodes trigger this code.
        """
        global pandoc_exec
        w = self.ensure_text_widget()
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
        """Update rst in the VR pane."""
        s = s.strip().strip('"""').strip("'''").strip()
        isHtml = s.startswith('<') and not s.startswith('<<')
        # Do this regardless of whether we show the widget or not.
        w = self.ensure_text_widget()
        assert self.w
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
        w = self.ensure_text_widget()
        path = self.c.p.h[9:].strip()
        print("Plantuml output file name: ", path)
        with open("temp.plantuml", "w") as f:
            f.write(s)
        pth_plantuml_jar = "~/.leo"
        os.system("cat temp.plantuml | java -jar %s/plantuml.jar -pipe > %s" % (pth_plantuml_jar, path))
        template = image_template % (path)
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
        w = self.ensure_text_widget()
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

        if hasattr(QtSvg, "QSvgWidget"):  # #2134
            QSvgWidget = QtSvg.QSvgWidget
        else:
            try:
                from PyQt6 import QtSvgWidgets
                QSvgWidget = QtSvgWidgets.QSvgWidget
            except Exception:
                QSvgWidget = None
        if not QSvgWidget:
            w = self.ensure_text_widget()
            w.setPlainText(s)
            return
        if self.must_change_widget(QSvgWidget):
            w = QSvgWidget()
            self.embed_widget(w)
            assert w == self.w
        else:
            w = self.w
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
    #@+node:ekr.20110321005148.14537: *4* vr.update_url
    def update_url(self, s: str, keywords: Any) -> None:
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
            w = self.ensure_text_widget()
            self.show()
            w.setPlainText('')
    #@+node:ekr.20110322031455.5765: *4* vr.utils for update helpers...
    #@+node:ekr.20110322031455.5764: *5* vr.ensure_text_widget
    def ensure_text_widget(self) -> Widget:
        """Swap a text widget into the rendering pane if necessary."""
        c = self.c
        if self.must_change_widget(QtWidgets.QTextBrowser):
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
            self.embed_widget(w)  # Creates w.wrapper
            assert w == self.w
        return self.w
    #@+node:ekr.20110320120020.14483: *5* vr.get_kind
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
    #@+node:ekr.20110320233639.5776: *5* vr.get_fn
    def get_fn(self, s: str, tag: str) -> tuple[bool, str]:
        c = self.c
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
    def must_change_widget(self, widget_class: Widget) -> bool:
        return not self.w or self.w.__class__ != widget_class
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

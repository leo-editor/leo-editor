#@+leo-ver=5-thin
#@+node:ekr.20160331123847.1: * @file viewrendered3.py
'''
#@+<< vr3 docstring >>
#@+node:ekr.20160331134105.1: ** << vr3 docstring >>
#@@language rest
#@@wrap
#@+others
#@+node:ekr.20160331124028.2: *3* vr3 docstring: intro
#@@language rest
#@@wrap

viewrendered3.py.

Creates a window for *live* rendering of reSTructuredText, markdown text,
images, movies, sounds, rst, html, etc.

Dependencies
============

This plugin uses [docutils](http://docutils.sourceforge.net/) to render
reStructuredText, so installing docutils is highly recommended when using
this plugin.

This plugin uses [Markdown](http://http://pypi.python.org/pypi/Markdown) to
render Markdown, so installing markdown is highly recommended when using
this plugin.
#@+node:ekr.20160331133626.1: *3* vr3 docstring: commands

Commands
========

viewrendered.py creates the following (``Alt-X``) commands:

``viewrendered (abbreviated vr)``
    Opens a new rendering window.

    By default, the rendering pane renders body text as reStructuredText,
    with all Leo directives removed. However, if the body text starts with
    ``<`` (after removing directives), the body text is rendered as html.

    **Important**: The default rendering just described does not apply to
    nodes whose headlines begin with @image, @html, @movie, @networkx, @svg
    and @url. See the section called **Special Renderings** below.

    Rendering sets the process current directory (os.chdir()) to the path
    to the node being rendered, to allow relative paths to work in ``..
    image::`` directives.

.. ``viewrendered-big``
..    as above, but zoomed in, useful for presentations
.. ``viewrendered-html``
..    displays the html source generated from reStructuredText, useful for
..    debugging

``hide-rendering-pane``
    Makes the rendering pane invisible, but does not destroy it.

``lock-unlock-rendering-pane``
    Toggles the locked state of the rendering pane. When unlocked (the
    initial state), the rendering pane renders the contents of the
    presently selected node. When locked, the rendering pane does not
    change when other nodes are selected. This is useful for playing movies
    in the rendering pane.

``pause-play-movie``
    This command has effect only if the rendering pane is presently showing
    a movie. It pauses the movie if playing, or resumes the movie if
    paused.

``show-rendering-pane``
    Makes the rendering pane visible.

``toggle-rendering-pane``
    Shows the rendering pane if invisible, otherwise hides it.

``update-rendering-pane``
    Forces an update of the rendering pane. This is especially useful for
    @graphics-script nodes: such nodes are update automatically only when
    selected, not when the body text changes.
#@+node:ekr.20160331133628.1: *3* vr3 docstring: rendering rST

Rendering reStructuredText
==========================

For example, both::

    Heading
    -------

    `This` is **really** a line of text.

and::

    <h1>Heading<h1>

    <tt>This</tt> is <b>really</b> a line of text.

will look something like::

    **Heading**

    `This` is **really** a line of text.

**Important**: reStructuredText errors and warnings will appear in red in
the rendering pane.

#@+node:ekr.20160331133819.1: *3* vr3 docstring: rendering markdown

Rendering markdown
==================

Please see the [markdown syntax
document](http://daringfireball.net/projects/markdown/syntax) for more
information on markdown.

Unless ``@string view-rendered-default-kind`` is set to ``md``, markdown
rendering must be specified by putting it in a ``@md`` node.
#@+node:ekr.20160331133834.1: *3* vr3 docstring: special renderings

Special Renderings
===================

As stated above, the rendering pane renders body text as reStructuredText
by default, with all Leo directives removed. However, if the body text
starts with ``<`` (after removing directives), the body text is rendered as
html.

This plugin renders @md, @image, @html, @movie, @networkx and @svg nodes as
follows:

**Note**: For @image, @movie and @svg nodes, either the headline or the
first line of body text may contain a filename. If relative, the filename
is resolved relative to Leo's load directory.

- ``@md`` renderes the body text as markdown, as described above.

- ``@graphics-script`` executes the script in the body text in a context
  containing two predefined variables:

    - gs is the QGraphicsScene for the rendering pane.
    - gv is the QGraphicsView for the rendering pane.

  Using these variables, the script in the body text may create graphics to
  the rendering pane.

- ``@image`` renders the file as an image.

- ``@html`` renders the body text as html.

- ``@movie`` plays the file as a movie.  @movie also works for music files.

- ``@networkx`` is non-functional at present.  It is intended to
  render the body text as a [networkx](http://networkx.lanl.gov/) graph.

- ``@svg`` renders the file as a (possibly animated!) svg [Scalable Vector Image](http://en.wikipedia.org/wiki/Scalable_Vector_Graphics).
  
  **Note**: if the first character of the body text is ``<`` after removing
  Leo directives, the contents of body pane is taken to be an svg image.

.. - ``@url`` is non-functional at present.
#@+node:ekr.20160331133628.2: *3* vr3 docstring: settings

Settings
========

The following settings are the same as in the viewrendered.py plugin:

- ``@bool view-rendered-auto-create = False``
  When True, show the rendering pane when Leo opens an outline.

- ``@color rendering-pane-background-color = white``
  The background color the rendering pane when rendering text.

- ``@string view-rendered-default-kind = rst``
  The default kind of rendering.  One of (big,rst,md,html)

- ``@string view-rendered-md-extensions = extra``
  A comma-delineated list of markdown extensions to use.
  Suitable extensions can be seen [here](http://pythonhosted.org/Markdown/extensions/index.html).

The following settings are new in the viewrendered2.py plugin:

These settings directly override the corresponding docutils settings (note the
underscores in the docutil keywords):

- ``@string vr-stylesheet_path = html4css1.css``
- ``@int vr-halt_level = 6``
- ``@string vr-math_output = mathjax``
- ``@bool vr-smart_quotes = True``
- ``@bool vr-embed_stylesheet = True``
- ``@bool vr-xml_declaration = False``
- ``@bool vr-syntax_highlight = long``
- ``@bool vr-no_compact_lists = False``
- ``@bool vr-no_compact_field_lists = False``

The following settings override viewrendered2.py internal settings:

- ``@bool vr-verbose = False``
- ``@bool vr-tree-mode = False``
- ``@bool vr-auto-update = True``
- ``@bool vr-lock-node = False``
- ``@bool vr-slideshow = False``
- ``@bool vr-visible-code = True``
- ``@bool vr-execute-code = False``
- ``@bool vr-rest-code-output = False``

#@+node:ekr.20160331123847.3: *3* vr3 docstring: to do

VR3 To Do
=========

- Use the free_layout rotate-all command in Leo's toggle-split-direction
  command.
- Add dict to allow customize must_update.
- Lock movies automatically until they are finished?
- Render @url nodes as html?
- Support uA's that indicate the kind of rendering desired.
- (Failed) Make viewrendered-big work.
#@+node:ekr.20160331133914.1: *3* vr3 docstring: acknowledgements

Acknowledgments
================

Terry Brown created viewrendered.py, the free_layout and NestedSplitter
plugins used by viewrendered.

Jacob Peck added markdown support.

Peter Mills created viewrendered2, based on the viewrendered.py plugin.

Edward K. Ream created viewrendered3.py and added communication and
coordination between the free_layout, NestedSplitter and viewrendered
plugins.
#@-others
#@-<< vr3 docstring >>
'''
#pylint: disable=no-member
trace = False
verbose = False
    # These global switches are convenient.
#@+<< vr3 imports >>
#@+node:ekr.20160331123847.4: ** << vr3 imports >>
trace_imports = False
    # Good for debugging only.

# Standard library...
import os
import sys
# import traceback

# Leo imports...
import leo.core.leoGlobals as g
import leo.plugins.qt_text as qt_text
import leo.plugins.free_layout as free_layout
from leo.core.leoQt import isQt5
from leo.core.leoQt import QtCore, QtGui, QtWidgets
from leo.core.leoQt import phonon, QtSvg, QtWebKitWidgets, QUrl

# Other imports...
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
if trace_imports:
    print('viewrendered3.py: got_docutils: %s' % got_docutils)
try:
    from markdown import markdown
    got_markdown = True
except ImportError:
    got_markdown = False
if trace_imports:
    print('viewrendered3.py: got_markdown: %s' % got_markdown)
try:
    import pygments
except ImportError:
    pygments = None
if g.isPython3:
    from io import StringIO
else:
    from StringIO import StringIO
#@-<< vr3 imports >>
#@+<< vr3 stylesheet >>
#@+node:ekr.20160331123847.5: ** << vr3 stylesheet >>
stickynote_stylesheet = """
/* The body pane */
QPlainTextEdit {
    background-color: #fdf5f5; /* A kind of pink. */
    selection-color: white;
    selection-background-color: lightgrey;
    font-family: DejaVu Sans Mono;
    /* font-family: Courier New; */
    font-size: 12px;
    font-weight: normal; /* normal,bold,100,..,900 */
    font-style: normal; /* normal,italic,oblique */
}
"""
#@-<< vr3 stylesheet >>
controllers = {}
    # Keys are c.hash(): values are PluginControllers
# Global constants.
VR3 = True
    # True: use the VR2 code. False: use the VR code.
vr3_ns_id = '_leo_viewrendered3'
    # Must match for all controllers.
vr3_pane_name = 'viewrendered_pane'
    # Must match for all controllers
#@+others
#@+node:ekr.20160331123847.6: ** Top-level
#@+node:ekr.20160331123847.7: *3* decorate_window (not used)
def decorate_window(w):
    '''Decorate the VR window with the Leo icon.'''
    w.setStyleSheet(stickynote_stylesheet)
    w.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    w.resize(600, 300)
#@+node:ekr.20160331123847.8: *3* init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = bool(QtSvg and QtWebKitWidgets)
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    g.registerHandler('scrolledMessage', show_scrolled_message)
    return ok
#@+node:ekr.20160331123847.9: *3* onCreate (viewrendered3.py)
def onCreate(tag, keys):
    c = keys.get('c')
    if c:
        provider = ViewRenderedProvider3(c)
        free_layout.register_provider(c, provider)
#@+node:ekr.20160331123847.10: *3* show_scrolled_message
def show_scrolled_message(tag, kw):
    if g.unitTesting:
        return # This just slows the unit tests.
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
    if trace: g.trace(tag, len(s), 'flags', flags)
    vr.update(
        tag='show-scrolled-message',
        keywords={
            'c': c,
            'flags': flags, ### Not in VR2
            'force': True, 's': s,
            'kind': 'rst', ### New in VR2.
            'show-scrolled-message': True,
        }
    )
    return True
#@+node:ekr.20160331123847.11: ** vr3 Commands
#@+node:ekr.20160331123847.12: *3* g.command('preview')
@g.command('preview')
def preview(event):
    '''A synonym for the vr-toggle command.'''
    toggle_rendering_pane(event)
#@+node:ekr.20160331123847.13: *3* g.command('vr')
@g.command('vr')
def viewrendered(event):
    """Open render view for commander"""
    global controllers
    c = event.get('c')
    if not c: return None
    vr = controllers.get(c.hash())
    if vr:
        if trace: g.trace('** controller exists: %s' % (vr))
        vr.show()
    else:
        controllers[c.hash()] = vr = ViewRenderedController3(c)
        if trace and verbose: g.trace('new controller: %s' % (vr))
        if hasattr(c, 'free_layout'):
            vr._ns_id = vr3_ns_id # for free_layout load/save
            splitter = c.free_layout.get_top_splitter()
            # Careful: we may be unit testing.
            if splitter:
                ok = splitter.add_adjacent(vr, 'bodyFrame', 'right-of')
                if not ok:
                    splitter.insert(0, vr)
        else:
            vr.setWindowTitle("Rendered View")
            vr.resize(600, 600)
            vr.show()
    c.bodyWantsFocusNow()
    # The following conflicts with F11: help-for-command.
    # I'm not sure why it was needed, but for sure it can not be used.
        # def at_idle(c=c):
        #    c.bodyWantsFocusNow()
        # QtCore.QTimer.singleShot(0,at_idle)
    return vr

#@+node:ekr.20160331123847.14: *3* g.command('vr-contract')
@g.command('vr-contract')
def contract_rendering_pane(event):
    '''Contract the rendering pane.'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if vr:
            vr.contract()
        else:
            # Just open the pane.
            viewrendered(event)
#@+node:ekr.20160331123847.15: *3* g.command('vr-expand')
@g.command('vr-expand')
def expand_rendering_pane(event):
    '''Expand the rendering pane.'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if not vr:
            vr = viewrendered(event)
        if vr:
            vr.expand()
#@+node:ekr.20160331123847.16: *3* g.command('vr-hide')
@g.command('vr-hide')
def hide_rendering_pane(event):
    '''Close the rendering pane.'''
    global controllers
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if vr:
            vr.deactivate()
            vr.deleteLater()

            def at_idle(c=c):
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

#@+node:ekr.20160331123847.17: *3* g.command('vr-lock')
@g.command('vr-lock')
def lock_rendering_pane(event):
    '''Lock rendereing pane.'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if vr and not vr.locked:
            vr.lock()
#@+node:ekr.20160331123847.18: *3* g.command('vr-pause-play')
@g.command('vr-pause-play-movie')
def pause_play_movie(event):
    '''Pause or play a movie in the rendering pane.'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if not vr:
            vr = viewrendered(event)
        if vr and vr.vp:
            vp = vr.vp
            if vp.isPlaying():
                vp.pause()
            else:
                vp.play()
#@+node:ekr.20160331123847.19: *3* g.command('vr-show')
@g.command('vr-show')
def show_rendering_pane(event):
    '''Show the rendering pane.'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if vr:
            pass # hide_rendering_pane(event)
        else:
            viewrendered(event)
#@+node:ekr.20160331123847.20: *3* g.command('vr-toggle')
@g.command('vr-toggle')
def toggle_rendering_pane(event):
    '''Toggle the rendering pane.'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if vr:
            hide_rendering_pane(event)
        else:
            viewrendered(event)
#@+node:ekr.20160331123847.21: *3* g.command('vr-unlock')
@g.command('vr-unlock')
def unlock_rendering_pane(event):
    '''Pause or play a movie in the rendering pane.'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if vr and vr.locked:
            vr.unlock()
#@+node:ekr.20160331123847.22: *3* g.command('vr-update')
@g.command('vr-update')
def update_rendering_pane(event):
    '''Update the rendering pane'''
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtWidgets.QWidget, vr3_pane_name)
        if not vr:
            vr = viewrendered(event)
        if vr:
            vr.update(tag='view', keywords={'c': c, 'force': True})

#@+node:ekr.20160331123847.27: ** class ViewRenderedController3 (QWidget)
if QtWidgets:

    class ViewRenderedController3(QtWidgets.QWidget):
        '''A class to control rendering in a rendering pane.'''
        #@+others
        #@+node:ekr.20160331123847.28: *3* vr3.ctor & helper ** VR3
        def __init__(self, c, parent=None):
            '''Ctor for ViewRenderedController class.'''
            # Create the widget.
            QtWidgets.QWidget.__init__(self, parent)
            self.setObjectName(vr3_pane_name)
            self.setLayout(QtWidgets.QVBoxLayout())
            self.layout().setContentsMargins(0, 0, 0, 0)
            # Define the classes.
            self.graphics_class = QtWidgets.QGraphicsWidget
            if VR3:
                self.html_class = WebViewPlus
            else:
                self.html_class = QtWebKitWidgets.QWebView
            self.svg_class = QtSvg.QSvgWidget
            self.text_class = QtWidgets.QTextBrowser
            # Define ivars.
            self.active = False
            self.badColors = []
            self.c = c
            self.delete_callback = None
            self.gnx = None
            self.gs = None # For @graphics-script: a QGraphicsScene
            self.gv = None # For @graphics-script: a QGraphicsView
            self.inited = False
            self.length = 0 # The length of previous p.b.
            self.locked = False
            self.node_changed = True
            self.scrollbar_pos_dict = {} # Keys are vnodes, values are positions.
            self.sizes = [] # Saved splitter sizes.
            self.splitter_index = None # The index of the rendering pane in the splitter.
            self.title = None
            self.vp = None # The present video player.
            self.w = None # The present widget in the rendering pane.
            # User-options:
            self.default_kind = c.config.getString('view-rendered-default-kind') or 'rst'
            self.auto_create = c.config.getBool('view-rendered-auto-create', False)
            self.background_color = c.config.getColor('rendering-pane-background-color') or 'white'
            # Init.
            self.create_dispatch_dict()
            self.activate()
            # Additional elements for WebView additions for reST.
            self.execcode = False
            self.output = 'html'
            self.reflevel = 0
            self.restoutput = False
            self.showcode = True
            self.tree = True
            self.verbose = False
        #@+node:ekr.20160331123847.29: *4* vr3.create_dispatch_dict
        def create_dispatch_dict(self):
            pc = self
            d = {
                'big': pc.update_rst,
                'html': pc.update_html,
                'graphics-script': pc.update_graphics_script,
                'image': pc.update_image,
                'movie': pc.update_movie,
                'networkx': pc.update_networkx,
                'svg': pc.update_svg,
                'url': pc.update_url, # Handle url's like rest or md.
                # 'xml': pc.update_xml,
            }
            if got_markdown:
                for key in ('markdown', 'md'):
                    d [key] = pc.update_md
            if got_docutils:
                for key in ('rest', 'rst'):
                    d [key] = pc.update_rst
            pc.dispatch_dict = d
            return d
        #@+node:ekr.20160401044123.1: *3* vr3.command helpers
        #@+node:ekr.20160331123847.30: *4* vr3.closeEvent
        def closeEvent(self, event):
            '''Close the vr window.'''
            self.deactivate()
        #@+node:ekr.20160331123847.31: *4* vr3.contract & expand
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
                for j in range(len(sizes)):
                    if j == i:
                        sizes[j] = max(0, sizes[i] + delta)
                    else:
                        sizes[j] = max(0, sizes[j] - int(delta / (n - 1)))
                splitter.setSizes(sizes)
        #@+node:ekr.20160331123847.32: *4* vr3.activate
        def activate(self):
            '''Activate the vr-window.'''
            pc = self
            if not pc.active:
                if trace: g.trace('=====')
                pc.inited = True
                pc.active = True
                g.registerHandler('select2', pc.update)
                g.registerHandler('idle', pc.update)
        #@+node:ekr.20160331123847.33: *4* vr3.deactivate
        def deactivate(self):
            '''Deactivate the vr window.'''
            pc = self
            # Never disable the idle-time hook: other plugins may need it.
            if trace: g.trace('=====')
            g.unregisterHandler('select2', pc.update)
            g.unregisterHandler('idle', pc.update)
            pc.active = False
        #@+node:ekr.20160331123847.34: *4* vr3.lock/unlock
        def lock(self):
            '''Lock the vr pane.'''
            g.note('rendering pane locked')
            self.locked = True

        def unlock(self):
            '''Unlock the vr pane.'''
            g.note('rendering pane unlocked')
            self.locked = False
        #@+node:ekr.20160331150055.1: *3* vr3.update and helpers
        #@+node:ekr.20160331123847.36: *4* vr3.update
        # Must have this signature: called by leoPlugins.callTagHandler.

        def update(self, tag, keywords):
            '''Update the vr pane.'''
            pc = self
            c, p = pc.c, pc.c.p
            if pc.must_update(keywords):
                if trace:
                    if verbose: g.trace('===== updating', keywords)
                # Suppress updates until we change nodes.
                pc.node_changed = pc.gnx != p.v.gnx
                pc.gnx = p.v.gnx
                pc.length = len(p.b)
                    # Not len(s): this length of the previous p.b.
                s = keywords.get('s') if 's' in keywords else p.b
                if keywords.get('show-scrolled-message'):
                    s = pc.remove_directives(s)
                    pc.update_rst(s, keywords, force_rst=True)
                    return
                # Dispatch based on the computed kind.
                if VR3:
                    kind = keywords.get('kind', None) # vr2
                else:
                    kind = keywords.get('flags', None) # vr
                if trace: g.trace('kind1', kind)
                if not kind:
                    kind = pc.get_kind(p)
                if trace: g.trace('kind:', kind)
                f = pc.dispatch_dict.get(kind)
                if f:
                    if trace and verbose: g.trace(p.h, f.__name__)
                else:
                    if trace: g.trace('no handler for kind: %s' % kind)
                    f = pc.update_url
                        # Has cool inference logic.
                f(s, keywords)
            else:
                # Save the scroll position.
                w = pc.w
                if w.__class__ == pc.text_class:
                    # 2011/07/30: The widge may no longer exist.
                    try:
                        sb = w.verticalScrollBar()
                    except Exception:
                        g.es_exception()
                        pc.deactivate()
                    if sb:
                        pc.scrollbar_pos_dict[p.v] = sb.sliderPosition()
                # Saving scroll position for QWebView used in new html_class
                #            elif w.__class__ == pc.html_class:
                #                # The widge may no longer exist.
                #                mf = None
                #                try:
                #                    mf = w.view.page().mainFrame()
                #                except Exception:
                #                    g.es_exception()
                #                    pc.deactivate()
                #                if mf:
                #                    pos = mf.scrollBarValue(QtCore.Qt.Vertical)
                #                    pc.scrollbar_pos_dict[p.v] = pos
                #                    print 'saved1 scroll pos', pos
                # Will be called at idle time.
                # if trace: g.trace('no update')
        #@+node:ekr.20160331123847.37: *4* vr3.embed_widget & helper
        def embed_widget(self, w, delete_callback=None):
            '''Embed widget w in the free_layout splitter.'''
            pc = self; c = pc.c
            pc.w = w
            layout = self.layout()
            for i in range(layout.count()):
                layout.removeItem(layout.itemAt(0))
            self.layout().addWidget(w)
            w.show()
            # Special inits for text widgets...
            if w.__class__ == pc.text_class:
                text_name = 'body-text-renderer'
                w.setObjectName(text_name)
                pc.setBackgroundColor(pc.background_color, text_name, w)
                w.setReadOnly(True)
                # Create the standard Leo bindings.
                wrapper_name = 'rendering-pane-wrapper'
                wrapper = qt_text.QTextEditWrapper(w, wrapper_name, c)
                w.leo_wrapper = wrapper
                c.k.completeAllBindingsForWidget(wrapper)
                w.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        #@+node:ekr.20160331123847.38: *5* vr3.setBackgroundColor
        def setBackgroundColor(self, colorName, name, w):
            '''Set the background color of the vr pane.'''
            pc = self
            if not colorName: return
            styleSheet = 'QTextEdit#%s { background-color: %s; }' % (name, colorName)
            # g.trace(name,colorName)
            if QtGui.QColor(colorName).isValid():
                w.setStyleSheet(styleSheet)
            elif colorName not in pc.badColors:
                pc.badColors.append(colorName)
                g.warning('invalid body background color: %s' % (colorName))
        #@+node:ekr.20160331123847.39: *4* vr3.must_update
        def must_update(self, keywords):
            '''Return True if we must update the rendering pane.'''
            c, p, pc = self.c, self.c.p, self
            trace = False and not g.unitTesting
                # Don't trace this by default.
            verbose = True
            if g.unitTesting:
                return False
            if keywords.get('force'):
                pc.active = True
                if trace: g.trace('force: activating', p.h)
                return True
            if c != keywords.get('c') or not pc.active:
                if trace: g.trace('not active', p.h)
                return False
            if pc.locked:
                if trace and verbose: g.trace('locked', p.h)
                return False
            if pc.gnx != p.v.gnx:
                if trace and verbose: g.trace('changed node', p.h)
                return True
            if len(p.b) != pc.length:
                if trace: g.trace('text changed', p.h)
                return True
            # This will be called at idle time.
            # if trace: g.trace('no change')
            return False
        #@+node:ekr.20160331123847.40: *4* vr3.update_graphics_script
        def update_graphics_script(self, s, keywords):
            '''Update the graphics script in the vr pane.'''
            pc = self; c = pc.c
            force = keywords.get('force')
            if pc.gs and not force:
                return
            s = pc.remove_directives(s)
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
        #@+node:ekr.20160331123847.41: *4* vr3.update_html ** VR3
        def update_html(self, s, keywords):
            '''Update html in the vr pane.'''
            pc = self
            if trace: g.trace(len(s))
            s = pc.remove_directives(s)
            if pc.must_change_widget(pc.html_class):
                if VR3:
                    w = pc.html_class(pc=pc)
                else:
                    w = pc.html_class()
                pc.embed_widget(w)
                assert(w == pc.w)
            else:
                w = pc.w
            pc.show()
            w.setHtml(s)
        #@+node:ekr.20160331123847.42: *4* vr3.update_image
        def update_image(self, s, keywords):
            '''Update an image in the vr pane.'''
            pc = self
            if not s.strip():
                return
            s = pc.remove_directives(s)
            lines = g.splitLines(s) or []
            fn = lines and lines[0].strip()
            if not fn:
                return
            w = pc.ensure_text_widget()
            ok, path = pc.get_fn(fn, '@image')
            if not ok:
                w.setPlainText('@image: file not found:\n%s' % (path))
                return
            path = path.replace('\\', '/')
            template = '''\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head></head>
        <body bgcolor="#fffbdc">
        <img src="%s">
        </body>
        </html>
        ''' % (path)
            # Only works in Python 3.x.
            template = g.adjustTripleString(template, pc.c.tab_width).strip() # Sensitive to leading blank lines.
            # template = g.toUnicode(template)
            pc.show()
            w.setReadOnly(False)
            w.setHtml(template)
            w.setReadOnly(True)
        #@+node:ekr.20160331123847.43: *4* vr3.update_md ** VR3
        def update_md(self, s, keywords):
            '''Update markdown text in the vr pane.'''
            pc = self
            if trace: g.trace(len(s))
            if VR3:
                # Do this regardless of whether we show the widget or not.
                if pc.must_change_widget(pc.html_class):
                    if trace: g.trace('new widget')
                    w = pc.html_class(pc)
                    pc.embed_widget(w)
                    assert(w == pc.w)
                else:
                    if trace: g.trace('use existing widget')
                    w = pc.w
                s = pc.remove_directives(s)
                w.render_md(s, keywords)
            else:
                c, p = pc.c, pc.c.p
                s = pc.remove_directives(s)
                s = s.strip().strip('"""').strip("'''").strip()
                isHtml = s.startswith('<') and not s.startswith('<<')
                if trace and verbose: g.trace('isHtml:', isHtml, p.h)
                # Do this regardless of whether we show the widget or not.
                w = pc.ensure_text_widget()
                assert pc.w
                if s:
                    pc.show()
                if not got_markdown:
                    isHtml = True
                    s = '<pre>\n%s</pre>' % s
                if not isHtml:
                    # Not html: convert to html.
                    path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
                    if not os.path.isdir(path):
                        path = os.path.dirname(path)
                    if os.path.isdir(path):
                        os.chdir(path)
                    try:
                        msg = '' # The error message from docutils.
                        if pc.title:
                            s = pc.underline(pc.title) + s
                            pc.title = None
                        mdext = c.config.getString('view-rendered-md-extensions') or 'extra'
                        mdext = [x.strip() for x in mdext.split(',')]
                        s = markdown(s, mdext)
                        s = g.toUnicode(s)
                        show = True
                    except SystemMessage as sm:
                        msg = sm.args[0]
                        if 'SEVERE' in msg or 'FATAL' in msg:
                            s = 'MD error:\n%s\n\n%s' % (msg, s)
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
                # 2016/03/25: honor @language md.
                colorizer = c.frame.body.colorizer
                language = colorizer.scanColorDirectives(p)
                if (
                    language in ('markdown', 'md') or
                    pc.default_kind in ('big', 'rst', 'html', 'md')
                ):
                    w.setHtml(s)
                    if pc.default_kind == 'big':
                        w.zoomIn(4) # Doesn't work.
                else:
                    w.setPlainText(s)
                if sb and pos:
                    # Restore the scrollbars
                    sb.setSliderPosition(pos)
        #@+node:ekr.20160331123847.44: *4* vr3.update_movie
        def update_movie(self, s, keywords):
            '''Update a movie in the vr pane.'''
            # pylint: disable=maybe-no-member
                # 'PyQt4.phonon' has no 'VideoPlayer' member
                # 'PyQt4.phonon' has no 'VideoCategory' member
                # 'PyQt4.phonon' has no 'MediaSource' member
            pc = self
            ok, path = False, None
            s = pc.remove_directives(s)
            lines = g.splitLines(s)
            if lines:
                s = lines[0].strip()
                if g.isValidUrl(s):
                    if trace: g.trace('move url', s)
                    path = s
                    ok = True
            if not ok:
                ok, path = pc.get_fn(s, '@movie')
            if not ok:
                w = pc.ensure_text_widget()
                w.setPlainText('Movie\n\nfile not found: %s' % (path))
                return
            if not phonon:
                w = pc.ensure_text_widget()
                w.setPlainText('Movie\n\nno movie player: %s' % (path))
                return
            if pc.vp:
                vp = pc.vp
                pc.vp.stop()
                pc.vp.deleteLater()
            # Create a fresh player.
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
        #@+node:ekr.20160331123847.45: *4* vr3.update_networkx
        def update_networkx(self, s, keywords):
            '''Update a networkx graphic in the vr pane.'''
            pc = self
            w = pc.ensure_text_widget()
            s = pc.remove_directives(s)
            w.setPlainText('') # 'Networkx: len: %s' % (len(s)))
            pc.show()
        #@+node:ekr.20160331123847.46: *4* vr3.update_rst *** VR3
        def update_rst(self, s, keywords, force_rst=False):
            '''Update rst in the vr pane.'''
            pc = self
            verbose = True
            if trace: g.trace(len(s))
            if VR3:
                # Do this regardless of whether we show the widget or not.
                if pc.must_change_widget(pc.html_class):
                    w = pc.html_class(pc)
                    pc.embed_widget(w)
                    assert(w == pc.w)
                else:
                    w = pc.w
                s = pc.remove_directives(s)
                w.render_rst(s, keywords)
            else:
                c, p = pc.c, pc.c.p
                s1 = s
                s = s.strip().strip('"""').strip("'''").strip()
                isHtml = s.startswith('<') and not s.startswith('<<')
                # Do this regardless of whether we show the widget or not.
                w = pc.ensure_text_widget()
                assert pc.w
                # Always do this to clear the VR pane.
                pc.show()
                if not s:
                    w.setPlainText('')
                    return
                # 2016/03/25: honor @language rest.
                colorizer = c.frame.body.colorizer
                language = colorizer.scanColorDirectives(p)
                if not isHtml and not force_rst and language not in ('rest', 'rst'):
                    if trace: g.trace('setPlain: isHtml=%s, language=%s' % (
                        isHtml, language))
                    w.setPlainText(s1)
                    return
                # After this point, HTML *will* be generated.
                s = pc.remove_directives(s1)
                if not got_docutils:
                    isHtml = True
                    s = '<pre>\n%s</pre>' % s
                if not isHtml:
                    # Not html: convert to html.
                    path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
                    if not os.path.isdir(path):
                        path = os.path.dirname(path)
                    if os.path.isdir(path):
                        os.chdir(path)
                    try:
                        msg = '' # The error message from docutils.
                        if pc.title:
                            s = pc.underline(pc.title) + s
                            pc.title = None
                        # Call docutils to get the string.
                        s = publish_string(s, writer_name='html')
                        if trace: g.trace('after docutils:', len(s))
                        s = g.toUnicode(s) # 2011/03/15
                        show = True
                    except SystemMessage as sm:
                        # g.trace(sm,sm.args)
                        msg = sm.args[0]
                        if 'SEVERE' in msg or 'FATAL' in msg:
                            s = 'RST error:\n%s\n\n%s' % (msg, s)
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
                if trace: g.trace('setHtml: language=%s, default=%s, force_rst=%s' % (
                    language, pc.default_kind, force_rst))
                w.setHtml(s)
                if pc.default_kind == 'big':
                    w.zoomIn(4) # Doesn't work.
                if sb and pos:
                    # Restore the scrollbars
                    sb.setSliderPosition(pos)
        #@+node:ekr.20160331123847.47: *4* vr3.update_svg
        # http://doc.trolltech.com/4.4/qtsvg.html
        # http://doc.trolltech.com/4.4/painting-svgviewer.html

        def update_svg(self, s, keywords):
            pc = self
            if pc.must_change_widget(pc.svg_class):
                w = pc.svg_class()
                pc.embed_widget(w)
                assert(w == pc.w)
            else:
                w = pc.w
            s = pc.remove_directives(s)
            if s.strip().startswith('<'):
                # Assume it is the svg (xml) source.
                s = g.adjustTripleString(s, pc.c.tab_width).strip() # Sensitive to leading blank lines.
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
        #@+node:ekr.20160401040150.1: *4* vr3.update_url
        def update_url(self, s, keywords):
            '''
            Handle @url nodes like rest or md, depending first on color directives,
            and second, on the first non-blank character of s.
            '''
            pc = self
            p = self.c.p
            # At this point, Leo directives have *not* been removed.
            kind = self.get_kind(p, handle_headline=False, use_default=False)
                # Return None if no @language directive is in effect.
            if trace: g.trace('kind', kind)
            if kind in ('rst', 'rest'):
                self.update_rst(s, keywords)
            elif kind in ('md', 'markdown'):
                self.update_md(s, keywords)
            elif not kind and s.strip().startswith('`'):
                self.update_rst(s, keywords, force_rst=True)
            elif not kind and s.strip().startswith('['):
                self.update_md(s, keywords)
            elif kind:
                f = pc.dispatch_dict.get(kind)
                if f:
                    f(s, keywords)
                elif s.strip().startswith('`'):
                    self.update_rst(s, keywords, force_rst=True)
                elif s.strip().startswith('['):
                    self.update_md(s, keywords)
                elif VR3:
                    if trace: g.trace('unknown kind:', kind, 'using md')
                    self.update_md(s, keywords)
                else:
                    if trace: g.trace('unknown kind:', kind, 'using rst')
                    self.update_rst(s, keywords)
            elif VR3:
                if trace: g.trace('no kind:', kind, 'using md')
                self.update_md(s, keywords)
            else:
                if trace: g.trace('no kind:', kind, 'using rst')
                self.update_rst(s, keywords)
        #@+node:ekr.20160331123847.49: *3* vr3.utils
        #@+node:ekr.20160331123847.50: *4* vr3.ensure_text_widget ** VR3
        def ensure_text_widget(self):
            '''Swap a text widget into the rendering pane if necessary.'''
            c, pc = self.c, self
            if not pc.must_change_widget(pc.text_class):
                return pc.w
            w = pc.text_class()
            if VR3:
                def mouseReleaseEvent(event, w=w):
                    if QtCore.Qt.ControlModifier & event.modifiers():
                        event2 = {'c': self.c, 'w': w.leo_wrapper}
                        g.openUrlOnClick(event2)
                    else:
                        QtWidgets.QTextBrowser.mouseReleaseEvent(w, event)

                w.mouseReleaseEvent = mouseReleaseEvent
            else:
                def handleClick(url, w=w):
                    event = g.Bunch(c=c, w=w)
                    g.openUrlOnClick(event, url=url)

                w.anchorClicked.connect(handleClick)
                w.setOpenLinks(False)
            pc.embed_widget(w) # Creates w.wrapper
            assert(w == pc.w)
            return pc.w
        #@+node:ekr.20160331123847.51: *4* vr3.get_kind
        def get_kind(self, p, handle_headline=True, use_default=True):
            '''Return the proper rendering kind for node p.'''
            c, h, pc = self.c, self.c.p.h, self
            if handle_headline and h.startswith('@'):
                i = g.skip_id(h, 1, chars='-')
                word = h[1: i].lower().strip()
                if word in pc.dispatch_dict:
                    return word
            # 2016/03/25: Honor @language
            colorizer = c.frame.body.colorizer
            language = colorizer.scanColorDirectives(p)
            if language in ('md', 'markdown'):
                if VR3:
                    return 'md'
                        # Always handle markdown
                else:
                    return 'md' if got_markdown else 'rst'
                        # legacy code: fall back to rst.
            elif language:
                return language
            ###
            # elif got_docutils and language in ('rest', 'rst'):
                # return language
            # elif language == 'html':
                # return 'html'
            elif use_default:
                # To do: look at ancestors, or uA's.
                return pc.default_kind # The default.
            else:
                return None # For update_url
        #@+node:ekr.20160331123847.52: *4* vr3.get_fn
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
        #@+node:ekr.20160331123847.54: *4* vr3.must_change_widget
        def must_change_widget(self, widget_class):
            pc = self
            return not pc.w or pc.w.__class__ != widget_class
        #@+node:ekr.20160331123847.55: *4* vr3.remove_directives
        def remove_directives(self, s):
            lines = g.splitLines(s)
            result = []
            for s in lines:
                if s.startswith('@'):
                    i = g.skip_id(s, 1)
                    word = s[1: i]
                    if word in g.globalDirectiveList:
                        continue
                result.append(s)
            return ''.join(result)
        #@+node:ekr.20160331123847.35: *4* vr3.underline
        def underline(self, s):
            '''Generate rST underlining for s.'''
            ch = '#'
            n = max(4, len(g.toEncodedString(s, reportErrors=False)))
            return '%s\n%s\n\n' % (s, ch * n)
        #@-others
#@+node:ekr.20160331123847.23: ** class ViewRenderedProvider3
class ViewRenderedProvider3:
    
    def __init__(self, c):
        '''Ctor for ViewRenderedProvider3 class.'''
        self.c = c
    
    def ns_provides(self):
        return [('Viewrendered3', vr3_ns_id)]
        
    def ns_provide(self, id_):
        global controllers
        if id_ == vr3_ns_id:
            c = self.c
            # SINGLE: return *the* singleton controller.
            vr = controllers.get(c.hash())
            if not vr:
                vr = ViewRenderedController3(c)
                controllers [c.hash()] = vr
            return vr
        else:
            return None
#@+node:ekr.20160331124028.22: ** class WebViewPlus (QWidget)
class WebViewPlus(QtWidgets.QWidget):
    #@+others
    #@+node:ekr.20160331124028.23: *3* wvp.ctor & helpers
    def __init__(self, pc):
        super(WebViewPlus, self).__init__()
        self.app = QtCore.QCoreApplication.instance()
        self.c = c = pc.c
        self.docutils_settings = None # Set below.
        self.html = '' # For communication with export().
        self.last_node = c.p
        self.pc = pc
        self.plock = None # A copy of a position
        self.plockmode = None
        self.pr = None
        self.rendering = False
        self.s = ''
        self.timer = self.init_timer()
        self.view = self.init_view()
        # Must be done after calling init_view.
        self.docutils_settings = self.init_config()
    #@+node:ekr.20160331124028.24: *4* wvp.init_view
    def init_view(self):
        '''Init the vr pane.'''
            # QWebView parts, including progress bar
        view = QtWebKitWidgets.QWebView()
        mf = view.page().mainFrame()
        mf.contentsSizeChanged.connect(self.restore_scroll_position)
        # ToolBar parts
        self.export_button = QtWidgets.QPushButton('Export')
        self.export_button.clicked.connect(self.export)
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(16, 16))
        for a in (QtWebKitWidgets.QWebPage.Back, QtWebKitWidgets.QWebPage.Forward):
            self.toolbar.addAction(view.pageAction(a))
        self.toolbar.setToolTip(self.tooltip_text(
            """
            Toolbar:
            -  Navigation buttons (like a normal browser),
            -  Reload button which is used to "update" this rendering pane
            -  Options tool-button to control the way rendering is done
            -  Export button to export to the standard browser

            Keyboard shortcuts:
            Ctl - C\tCopy html/text from the pane
            Ctl - +\tZoom in
            Ctl - -\tZoom out
            Ctl - 0\tZoom to original size"""         ))
        # Handle reload separately since this is used to re-render everything
        self.reload_action = view.pageAction(QtWebKitWidgets.QWebPage.Reload)
        self.reload_action.triggered.connect(self.render_delegate)
        self.toolbar.addAction(self.reload_action)
        #self.reload_action.clicked.connect(self.render)
        # Create the "Mode" toolbutton
        self.toolbutton = QtWidgets.QToolButton()
        self.toolbutton.setText('Options')
        self.toolbutton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.toolbutton.setToolTip(self.tooltip_text(
            """
            Options:
            Whole tree - Check this to render the whole tree rather than the node.
            Verbose logging - Provide more verbose logging of the rendering process.
            Auto-update - Check to automatically rerender when changes are made.
            Lock to node - Lock the rendered node/tree while another node is editted.
            Show as slideshow - Show a tree as an s5 slideshow (requires s5 support files).
            Visible code - Show the code designated by '@language' directives
            Execute code - Execute '@language' code blocks and show the output.
            Code output reST/md - Assume code outputs reStructuredText or Markdown."""         ))
        self.toolbar.addWidget(self.toolbutton)
        # Add a progress bar
        self.pbar = QtWidgets.QProgressBar()
        self.pbar.setMaximumWidth(120)
        menu = QtWidgets.QMenu()

        def action(label,callback=self.state_change):
            action = QtWidgets.QAction(label,self,checkable=True,triggered=callback)
            menu.addAction(action)
            return action

        self.tree_mode_action = action('Whole tree')
        self.verbose_mode_action = action('Verbose logging')
        self.auto_mode_action = action('Auto-update')
        self.lock_mode_action = action('Lock to node', self.lock)
        # Add an s5 option
        self.slideshow_mode_action = action('Show as slideshow')
        menu.addSeparator() # Separate render mode and code options
        self.visible_code_action = action('Visible code')
        self.execute_code_action = action('Execute code')
        self.reST_code_action = action('Code outputs reST/md')
        # radio button checkables example at
        # http://stackoverflow.com/questions/10368947/how-to-make-qmenu-item-checkable-pyqt4-python
        self.toolbutton.setMenu(menu)
        # Remaining toolbar items
            #self.toolbar.addSeparator()
            #self.toolbar.addWidget(self.export_button)
        # Create the 'Export' toolbutton
        self.export_button = QtWidgets.QToolButton()
        self.export_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.export_button.setToolTip(self.tooltip_text(
            """
            Show this in the default web-browser.
            If the default browser is not already open it will be started.  Exporting
            is useful for full-screen slideshows and also for using the printing and
            saving functions of the browser."""         ))
        self.toolbar.addWidget(self.export_button)
        self.export_button.clicked.connect(self.export)
        self.export_button.setText('Export')
        #self.toolbar.addSeparator()
        # Setting visibility in toolbar is tricky, must be done throug QAction
        # http://www.qtcentre.org/threads/32437-remove-Widget-from-QToolBar
        self.pbar_action = self.toolbar.addWidget(self.pbar)
        self.pbar_action.setVisible(False)
        # Document title in toolbar
        #self.toolbar.addSeparator()
        #   spacer = QtWidgets.QWidget()
        #   spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #   self.toolbar.addWidget(spacer)
        self.title = QtWidgets.QLabel()
        self.title.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.title.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.title.setTextFormat(1) # Set to rich text interpretation
        # None of this font stuff works! - instead I've gone for rich text above
        # font = QtGui.QFont("Sans Serif", 12, QtGui.QFont.Bold)
        #font = QtGui.QFont("Arial", 8)
        #font = QtGui.QFont()
        #font.setBold(True)
        #font.setWeight(75)
        self.toolbar.addWidget(self.title) # if needed, use 'title_action ='
        #title_action.setFont(font)  # Set font of 'QAction' rather than widget
        spacer = QtWidgets.QWidget()
        spacer.setMinimumWidth(5)
        self.toolbar.addWidget(spacer)
        # Layouts
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0) # Remove the default 11px margins
        vlayout.setSpacing( 0 );  # remove spacing between content widgets
        vlayout.addWidget(self.toolbar)
        vlayout.addWidget(view)
        self.setLayout(vlayout)
        # Key shortcuts - zoom
        view.setZoomFactor(1.0) # smallish panes demand small zoom
        self.zoomIn = QtWidgets.QShortcut("Ctrl++", self, activated=lambda: view.setZoomFactor(view.zoomFactor() + .2))
        self.zoomOut = QtWidgets.QShortcut("Ctrl+-", self, activated=lambda: view.setZoomFactor(view.zoomFactor() - .2))
        self.zoomOne = QtWidgets.QShortcut("Ctrl+0", self, activated=lambda: view.setZoomFactor(1.0))
        # Some QWebView settings
        # setMaximumPagesInCache setting prevents caching of images etc.
        if isQt5: ###
            pass # not ready yet.
        else:
            view.settings().setAttribute(QtWebKitWidgets.QWebSettings.PluginsEnabled, True)
        # Prevent caching, especially of images
        view.settings().setMaximumPagesInCache(0)
        view.settings().setObjectCacheCapacities(0, 0, 0)
        #self.toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        # Set up other widget states
        return view
    #@+node:ekr.20160331124028.25: *4* wvp.init_config
    def init_config(self):
        '''Init docutils settings.'''
        ds = {}
        gc = self.c.config

        def getConfig(getfun, name, default, setfun=None, setvar=None):
            """Make a shorthand way to get and store a setting with defaults"""
            r = getfun('vr-' + name) # keep docutils name but prefix
            if setfun: # settings are held in Qactions
                if r: setfun(r)
                else: setfun(default)
            elif setvar: # Just setting a variable
                if r: setvar = r
                else: setvar = default
            else: # settings held in dict (for docutils use)
                if r: ds[name] = r
                else: ds[name] = default

        # Do docutils config (note that the vr- prefix is omitted)
        # These update the options dictionary passed to docutils.
        getConfig(gc.getString, 'stylesheet_path', 'html4css1.css')
        getConfig(gc.getInt, 'halt_level', 6)
        getConfig(gc.getInt, 'report_level', 2)  # set to 5 to eliminate all error messages
        getConfig(gc.getString, 'math_output', 'HTML math.css')
        getConfig(gc.getBool, 'smart_quotes', True)
        getConfig(gc.getBool, 'embed_stylesheet', True)
        getConfig(gc.getBool, 'xml_declaration', False)
        # Additional docutils values suggested by T P <wingusr@gmail.com>
        getConfig(gc.getString, 'syntax_highlight', 'long')
        getConfig(gc.getBool, 'no_compact_lists', False)
        getConfig(gc.getBool, 'no_compact_field_lists', False)
        # Do VR2 init values
        # These directly update the state of the VR "Options" menu.
        getConfig(gc.getBool, 'verbose', False, self.verbose_mode_action.setChecked)
        getConfig(gc.getBool, 'tree-mode', False, self.tree_mode_action.setChecked)
        getConfig(gc.getBool, 'auto-update', True, self.auto_mode_action.setChecked)
        getConfig(gc.getBool, 'lock-node', False, self.lock_mode_action.setChecked)
        getConfig(gc.getBool, 'slideshow', False, self.slideshow_mode_action.setChecked)
        getConfig(gc.getBool, 'visible-code', True, self.visible_code_action.setChecked)
        getConfig(gc.getBool, 'execute-code', False, self.execute_code_action.setChecked)
        getConfig(gc.getBool, 'rest-code-output', False, self.reST_code_action.setChecked)
        # Misc other internal settings
        # Mark of the Web (for IE) to allow sensible security options - not required with modern browsers?
        #getConfig(gc.getBool, 'include_MOTW', True, setvar=self.MOTW)
        return ds
    #@+node:ekr.20160331124028.26: *4* wvp.init_timer
    def init_timer(self):
        '''Init the timer for delayed rendering (to allow smooth tree navigation).'''
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(1100)
            # just longer than the 1000ms interval of calls from update_rst
        timer.timeout.connect(self.render_delegate)
        return timer
    #@+node:ekr.20160331124028.27: *4* wvp.get_mode
    def get_mode(self):
        if self.lock_mode_action.isChecked():
            return self.plockmode
        else:
            kind = self.pc.get_kind(self.c.p)
            if kind in ('rest', 'rst'):
                return 'rst'
            elif kind in ('markdown', 'md'):
                return 'md'
            else:
                return kind
            # EKR
            # default = self.pc.default_kind
            # h = self.c.p.h
            # if h.startswith('@rst'): return 'rst'
            # elif h.startswith('@md'): return 'md'
            # elif h.startswith('@html'): return 'html'
            # return default
    #@+node:ekr.20160331124028.28: *4* wvp.tooltip_text
    def tooltip_text(self, s):
        '''Return the reformatted tooltip text corresponding to the triple string s.'''
        lines = g.splitLines(s)
        if lines:
            i = 0 if lines[0].strip() else 1
            s = ''.join(lines[i:])
            s = g.adjustTripleString(s, self.c.tab_width)
        return s
    #@+node:ekr.20160331124028.29: *3* wvp.gui helpers
    #@+node:ekr.20160331124028.30: *4* wvp.getUIconfig
    def getUIconfig(self):
        """Get the rendering configuration from the GUI controls."""
        # Pull internal configuration options from GUI
        self.verbose = self.verbose_mode_action.isChecked()
        #self.output = 'html'
        self.tree = self.tree_mode_action.isChecked()
        self.execcode = self.execute_code_action.isChecked()
        # If executing code, don't allow auto-mode otherwise navigation
        # can lead to getting stuck doing many recalculations
        if self.execcode:
            self.auto_mode_action.setChecked(False)
        self.auto = self.auto_mode_action.isChecked()
        self.lock_mode = self.lock_mode_action.isChecked()
        self.slideshow = self.slideshow_mode_action.isChecked()
        self.showcode = self.visible_code_action.isChecked()
        self.restoutput = self.reST_code_action.isChecked()
    #@+node:ekr.20160331124028.31: *4* wvp.lock
    def lock(self):
        """Implement node lock (triggered by "Lock node" action)."""
        # Lock "action" has been triggered, so state will have changed.
        if self.lock_mode_action.isChecked(): # Just become active
            self.plock = self.pc.c.p.copy() # make a copy of node position
            self.plockmode = self.get_mode() # copy current node's md/rst state
            if self.pr:
                self.pc.scrollbar_pos_dict[self.pr.v] = self.view.page().\
                mainFrame().scrollBarValue(QtCore.Qt.Vertical)
        else:
            self.render_delegate()
                # Render again since root node may have changed now
        # Add an icon or marker to node currently locked?
    #@+node:ekr.20160331124028.32: *4* wvp.render_rst
    def render_rst(self, s, keywords):
        """Generate the reST and render it in this pane."""
        self.getUIconfig()
        self.s = keywords.get('s') if 's' in keywords else ''
        show_scrolled_message = keywords.get('show-scrolled-message', False)
        if show_scrolled_message and got_docutils:
            c = self.c
            html = publish_string(s, writer_name='html', settings_overrides=self.docutils_settings)
            html = g.toUnicode(html)
            self.html = html
            self.path = c.getNodePath(c.rootPosition())
            ext = 'html'
            pathname = g.os_path_finalize_join(self.path, 'leo.' + ext)
            f = open(pathname, 'wb')
            f.write(html.encode('utf8'))
            f.close()
            self.view.setUrl(QUrl.fromLocalFile(pathname))
        elif self.auto and got_docutils:
            self.timer.start()
    #@+node:ekr.20160331124028.33: *4* wvp.render_md
    def render_md(self, s, keywords):
        """Generate the markdown and render it in this pane."""
        self.getUIconfig()
        self.s = keywords.get('s') if 's' in keywords else ''
        show_scrolled_message = keywords.get('show-scrolled-message', False)
        if show_scrolled_message:
            c = self.c
            mdext = c.config.getString('view-rendered-md-extensions') or 'extra'
            mdext = [x.strip() for x in mdext.split(',')]
            if pygments:
                mdext.append('codehilite')
            html = markdown(s, mdext)
            html = g.toUnicode(html)
            self.html = html
            self.path = c.getNodePath(c.rootPosition())
            ext = 'html'
            pathname = g.os_path_finalize_join(self.path, 'leo.' + ext)
            f = open(pathname, 'wb')
            f.write(html.encode('utf8'))
            f.close()
            self.view.setUrl(QUrl.fromLocalFile(pathname))
            return
        if self.auto:
            self.timer.start()
    #@+node:ekr.20160331124028.34: *4* wvp.render_html
    def render_html(self, html, keywords = None):
        """Render the string html in this pane."""
            # A new method by EKR.
            # Fixes bug 136: viewrendered2 chokes on displaying @html nodes
        c = self.c
        self.getUIconfig()
        # show_scrolled_message = keywords.get('show-scrolled-message', False)
        self.html = g.toUnicode(html)
        self.view.setHtml(self.html)
        if self.auto:
            self.timer.start()
    #@+node:ekr.20160331124028.35: *4* wvp.restore_scroll_position
    def restore_scroll_position(self):
        # Restore scroll bar position for (possibly) new node
        d = self.pc.scrollbar_pos_dict
        mf = self.view.page().mainFrame()
        # Set the scrollbar.
        if self.pr is None:
            spos = 0
        else:
            spos = d.get(self.pr.v, mf.scrollBarValue(QtCore.Qt.Vertical))
        mf.setScrollBarValue(QtCore.Qt.Vertical, spos)
        #print 'remembered scroll pos restored, re-read pos:', spos, mf.scrollBarValue(QtCore.Qt.Vertical)
    #@+node:ekr.20160331124028.36: *4* wvp.setHtml (EKR)
    def setHtml(self, s):
        
        self.view.setHtml(s)
    #@+node:ekr.20160331124028.37: *4* wvp.state_change
    def state_change(self, checked):
        """A wrapper for 'render' to re-render on all QAction state changes."""
        self.render_delegate()
    #@+node:ekr.20160331124028.38: *3* wvp.render_delegate
    def render_delegate(self):
        mode = self.get_mode()
        if mode == 'md':
            self.md_render()
        elif mode == 'html':
            self.render_html(self.html)
        else:
            self.render()
    #@+node:ekr.20160331124028.39: *3* wvp.render & helpers
    def render(self):
        """Re-render the existing string, but probably with new configuration."""
        if self.rendering:
            # if already rendering, don't execute
            self.timer.start() # Don't forget to do this last render request
        else:
            try:
                self.rendering = True
                self.render_helper()
            finally:
                # No longer rendering, OK to receive another rendering call
                self.rendering = False
    #@+node:ekr.20160331124028.40: *4* wvp.render_helper & helper
    def render_helper(self):
        '''Rendering helper: self.rendering is True.'''
        c, p, pc = self.c, self.c.p, self.pc
        self.getUIconfig()
            # Get the UI config again, in case directly called by control.
        if got_docutils:
            self.html = html = self.to_html(p)
        else:
            self.html = html = '<pre>\n%s</pre>' % self.s
        self.app.processEvents()
        # TODO: I think this path should be set when scanning directives!
        d = self.c.scanAllDirectives(p)
        # Put temporary or output files in location given by path directives
        self.path = d['path']
        if pc.default_kind in ('big', 'rst', 'html', 'md'):
            # Render to file to allow QWebView to load this without blocking
            # and be able to load any associated css from the local file system.
            ext = 'html'
            # Write the output file
            pathname = g.os_path_finalize_join(self.path,'leo.' + ext)
            f = open(pathname,'wb')
            f.write(self.html.encode('utf8'))
            f.close()
            # render to file, not directly to "QWebView.setHtml"
            self.view.setUrl(QUrl.fromLocalFile(pathname))
        else:
            self.view.setPlainText(html)
        if not self.auto:
            self.pbar.setValue(100)
            self.app.processEvents()
            self.pbar_action.setVisible(False)
    #@+node:ekr.20160331124028.41: *5* wvp.to_html & helper
    def to_html(self, p):
        '''Convert p.b to html using docutils.'''
        c, pc = self.c, self.pc
        mf = self.view.page().mainFrame()
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        # Need to save position of last node before rendering
        ps = mf.scrollBarValue(QtCore.Qt.Vertical)
        pc.scrollbar_pos_dict[self.last_node.v] = ps
        # Which node should be rendered?
        self.getUIconfig()  # Update the state of self.lock_mode
        if self.lock_mode:
            # use locked node for position to be rendered.
            self.pr = self.plock or c.p # EKR: added or c.p.
        else:
            # use new current node, whether changed or not.
            self.pr = c.p # use current node
        self.last_node = self.pr.copy()
            # Store this node as last node rendered
        # Set the node header in the toolbar.
        self.title.setText('' if self.s else '<b>' + self.pr.h + '</b>')
        if not self.auto:
            self.pbar.setValue(0)
            self.pbar_action.setVisible(True)
        # Handle all the nodes in the tree.
        html = self.process_nodes(self.pr, tree=self.tree)
        if not self.auto:
            self.pbar.setValue(50)
        self.app.processEvents()
            # Apparently this can't be done in docutils.
        try:
            # Call docutils to get the string.
            html = publish_string(html,
                writer_name='s5_html' if self.slideshow else 'html',
                settings_overrides=self.docutils_settings)
            return g.toUnicode(html)
        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                return 'RST error:\n%s\n\n%s' % (msg, html)
            else:
                return html
    #@+node:ekr.20160331124028.42: *6* wvp.process_nodes & helpers
    def process_nodes(self, p, tree=True):
        """
        Process the reST for a node, defaulting to node's entire tree.

        Any code blocks found (designated by @language python) will be executed
        in order found as the tree is walked. No section references are heeded.
        Output directed to stdout and stderr are included in the reST source.
        If self.showcode is True, then the execution output is included in a
        '::' block. Otherwise the output is assumed to be valid reST and
        included in the reST source.
        """
        c = self.c
        root = p.copy()
        self.reflevel = p.level() # for self.underline2().
        result = []
        environment = {'c': c, 'g': g, 'p': c.p} # EKR: predefine c & p.
        self.process_one_node(root, result, environment)
        if tree:
            # Create a progress counter showing 50% at end of tree processing.
            i, numnodes = 0, sum(1 for j in p.subtree())
            for p in root.subtree():
                self.process_one_node(p, result, environment)
                if not self.auto:
                    i += 1
                    self.pbar.setValue(i * 50 / numnodes)
                self.app.processEvents()
        s = '\n'.join(result)
        if self.verbose:
            self.write_rst(root, s)
        return s
    #@+node:ekr.20160331124028.43: *7* wvp.code_directive
    def code_directive(self, lang):
        '''Return an reST block or code directive.'''
        if pygments:
            # g.trace('using pygments')
            # See code in initCodeBlock for complications.
            return '\n\n.. code:: ' + lang + '\n\n'
        else:
            g.trace('NOT using pygments')
            return '\n\n::\n\n'
    #@+node:peter.20160410194526.1: *7* wvp.plain_directive
    def plain_directive(self):
        '''Return an reST plain text block header/directive.'''
        return '\n\n::\n\n'
    #@+node:ekr.20160331124028.44: *7* wvp.initCodeBlockString (from leoRst, for reference)
    def initCodeBlockString(self, p, language):
        '''Reference code illustrating the complications of code blocks.'''
        # Note: lines that end with '\n\n' are a signal to handleCodeMode.
        if pygments and language in ('python', 'ruby', 'perl', 'c'):
            self.code_block_string = '**code**:\n\n.. code-block:: %s\n\n' % language
        else:
            self.code_block_string = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
    #@+node:ekr.20160331124028.45: *7* wvp.process_one_node
    def process_one_node(self, p, result, environment):
        '''Handle one node.'''
        c = self.c
        result.append(self.underline2(p))
        d = c.scanAllDirectives(p)
        if self.verbose:
            g.trace(d.get('language') or 'None', ':', p.h)
        s, code = self.process_directives(p.b, d)
        result.append(s)
        result.append('\n\n')
            # Add an empty line so bullet lists display properly.
        if code and self.execcode:
            s, err = self.exec_code(code, environment)
                # execute code found in a node, append output to reST
            if not self.restoutput and s.strip():
                s = self.format_output(s) # if some non-reST to print
            result.append(s) # append, whether plain or reST output
            if err:
                err = self.format_output(err, prefix='**Error**::')
                result.append(err)
    #@+node:ekr.20160331124028.46: *7* wvp.exec_code
    def exec_code(self, code, environment):
        """Execute the code, capturing the output in stdout and stderr."""
        c = self.c
        saveout = sys.stdout # save stdout
        saveerr = sys.stderr
        sys.stdout = bufferout = StringIO()
        sys.stderr = buffererr = StringIO()
        # Protect against exceptions within exec
        try:
            exec(code, environment)
        except Exception:
            # print >> buffererr, traceback.format_exc()
            # buffererr.flush() # otherwise exception info appears too late
            # g.es('Viewrendered traceback:\n', sys.exc_info()[1])
            g.es('Viewrendered2 code execution exception')
            g.es_exception()
        # Restore stdout, stderr
        sys.stdout = saveout # was sys.__stdout__
        sys.stderr = saveerr # restore stderr
        return bufferout.getvalue(), buffererr.getvalue()
    #@+node:ekr.20160331124028.47: *7* wvp.format_output
    def format_output(self, s, prefix='::'):
        """Formats the multi-line string 's' into a reST literal block."""
        out = '\n\n' + prefix + '\n\n'
        lines = g.splitLines(s)
        for line in lines:
            out += '    ' + line
        return out + '\n'
    #@+node:ekr.20160331124028.48: *7* wvp.process_directives
    def process_directives(self, s, d):
        """s is string to process, d is dictionary of directives at the node."""
        trace = False and not g.unitTesting
        #lang = d.get('language') or 'python' # EKR.
        lang = d.get('language')
        #codeflag = lang != 'rest' # EKR
        # function to define flag in one place only
        def getcodeflag():
            return lang not in ['rest','md','plain','text',None]
        codeflag = getcodeflag()
        # function to define flag in one place only
        def getplainflag():
            """Needs to be rendered as a literal block, but not if body empty"""
            return len(s.strip())>0 and lang in ['plain','text','']
        plainflag = getplainflag()
        lines = g.splitLines(s)
        result = []
        code = ''
        if codeflag and self.showcode:
            result.append(self.code_directive(lang)) # EKR
        if plainflag:
            result.append(self.plain_directive())
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s, 1)
                word = s[1: i]
                # Add capability to detect mid-node language directives.
                # If removing, ensure "if word in g.globalDirectiveList:  continue" is retained
                # to stop directive being put into the reST output.
                # if word == 'language' and not codeflag and not plainflag: # only if not already code
                    # lang = s[i:].strip()
                # Check to see if there is a new language directive and that it has changed
                if word == 'language' and s[i:].strip() != lang:
                    lang = s[i:].strip()  # store the new language
                    # For *rendering* code, any type of code is eligible
                    codeflag = getcodeflag()
                    plainflag = getplainflag()
                    if codeflag:
                        if self.verbose:
                            g.es('New code section within node:', lang)
                        if self.showcode:
                            result.append(self.code_directive(lang)) # EKR
                    elif plainflag:
                        result.append(self.plain_directive())
                    else:
                        result.append('\n\n')
                    continue
                elif word in g.globalDirectiveList:
                    continue
            if (codeflag and self.showcode) or plainflag:
                    result.append('    ' + s) # 4 space indent on each line
            # For *execution* of code, only Python code is valid.
            if lang in ['python']:
                code += s # accumulate code lines for execution
            elif not plainflag:
                result.append(s)
        result = ''.join(result)
        if trace: g.trace('result:\n', result) # ,'\ncode:',code)
        return result, code
    #@+node:ekr.20160331124028.49: *7* wvp.underline2
    def underline2(self, p):
        r"""
        Use the given string and convert it to an reST headline for display
        The most unused underline characters are used here, so as not to clash
        with headings used in the reST.  These characters must not be used for
        underlining in nodes.

        Note that the full range of valid characters defined for reST is ::

            ! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~

        and the recommended ones are::

            = - ` : . ' " ~ ^ _ * + #
        """
        # Use relatively unused underline characters, cater for many levels
        ch = """><:_`*+"';/{|}()$%&@#"""[p.level() - self.reflevel]
        n = max(4, len(g.toEncodedString(p.h, reportErrors=False)))
        return '%s\n%s\n\n' % (p.h, ch * n)
    #@+node:ekr.20160331124028.50: *7* wvp.write_rst
    def write_rst(self, root, s):
        '''Write s, the final assembled reST text, to leo.rst.'''
        c = self.c
        filename = 'leo.rst'
        d = c.scanAllDirectives(root)
        path = d.get('path')
        pathname = g.os_path_finalize_join(path, filename)
        # Render constructed reST string
        # s = self.html_render(s)
        f = open(pathname, 'wb')
        f.write(s.encode('utf8'))
        f.close()
    #@+node:ekr.20160331124028.51: *3* wvp.md_render & helpers (md)
    def md_render(self):
        """Re-render the existing string, but probably with new configuration."""
        if self.rendering:
            # if already rendering, don't execute
            self.timer.start() # Don't forget to do this last render request
        else:
            try:
                self.rendering = True
                self.md_render_helper()
            finally:
                # No longer rendering, OK to receive another rendering call
                self.rendering = False
    #@+node:ekr.20160331124028.52: *4* wvp.md_render_helper & helper
    def md_render_helper(self):
        '''Rendinging helper: self.rendering is True.'''
        c, p, pc = self.c, self.c.p, self.pc
        self.getUIconfig()
            # Get the UI config again, in case directly called by control.
        if got_markdown:
            self.html = html = self.md_to_html(p)
        else:
            self.html = html = '<pre>\n%s</pre>' % self.s
        self.app.processEvents()
        # TODO: I think this path should be set when scanning directives!
        d = self.c.scanAllDirectives(p)
        # Put temporary or output files in location given by path directives
        self.path = d['path']
        if pc.default_kind in ('big', 'rst', 'html', 'md'):
            # Rendering to file and have QWebView load this without blocking
            # Write the output file
            pathname = g.os_path_finalize_join(self.path, 'leo.html')
            f = open(pathname, 'wb')
            f.write(html.encode('utf8'))
            f.close()
            # render
            self.view.setUrl(QUrl.fromLocalFile(pathname))
        else:
            self.view.setPlainText(html)
        if not self.auto:
            self.pbar.setValue(100)
            self.app.processEvents()
            self.pbar_action.setVisible(False)
    #@+node:ekr.20160331124028.53: *4* wvp.md_to_html & helper
    def md_to_html(self, p):
        '''Convert p.b to html using markdown.'''
        c, pc = self.c, self.pc
        mf = self.view.page().mainFrame()
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        # Need to save position of last node before rendering
        ps = mf.scrollBarValue(QtCore.Qt.Vertical)
        pc.scrollbar_pos_dict[self.last_node.v] = ps
        # Which node should be rendered?
        self.getUIconfig()  # Update the state of self.lock_mode
        if self.lock_mode:
            # use locked node for position to be rendered.
            self.pr = self.plock or c.p # EKR: added or c.p.
        else:
            # use new current node, whether changed or not.
            self.pr = c.p # use current node
        self.last_node = self.pr.copy()
            # Store this node as last node rendered
        # Set the node header in the toolbar.
        self.title.setText('' if self.s else '<b>' + self.pr.h + '</b>')
        if not self.auto:
            self.pbar.setValue(0)
            self.pbar_action.setVisible(True)
        # Handle all the nodes in the tree.
        html = self.md_process_nodes(self.pr, tree=self.tree)
        if not self.auto:
            self.pbar.setValue(50)
        self.app.processEvents()
            # Apparently this can't be done in docutils.
        try:
            # Call markdown to get the string.
            mdext = c.config.getString('view-rendered-md-extensions') or 'extra'
            mdext = [x.strip() for x in mdext.split(',')]
            if pygments:
                mdext.append('codehilite')
            html = markdown(html, mdext)
            return g.toUnicode(html)
        except Exception as e:
            print(e)
            return 'Markdown error... %s' % e
    #@+node:ekr.20160331124028.54: *4* wvp.md_process_nodes & helpers
    def md_process_nodes(self, p, tree=True):
        """
        Process the markdown for a node, defaulting to node's entire tree.

        Any code blocks found (designated by @language python) will be executed
        in order found as the tree is walked. No section references are heeded.
        Output directed to stdout and stderr are included in the md source.
        If self.showcode is True, then the execution output is included in a
        '```' block. Otherwise the output is assumed to be valid markdown and
        included in the md source.
        """
        c = self.c
        root = p.copy()
        self.reflevel = p.level() # for self.underline2().
        result = []
        environment = {'c': c, 'g': g, 'p': c.p}
        self.md_process_one_node(root, result, environment)
        if tree:
            # Create a progress counter showing 50% at end of tree processing.
            i, numnodes = 0, sum(1 for j in p.subtree())
            for p in root.subtree():
                self.md_process_one_node(p, result, environment)
                if not self.auto:
                    i += 1
                    self.pbar.setValue(i * 50 / numnodes)
                self.app.processEvents()
        s = '\n'.join(result)
        if self.verbose:
            self.md_write_md(root, s)
        return s
    #@+node:ekr.20160331124028.55: *5* wvp.md_code_directive
    def md_code_directive(self, lang):
        '''Return a markdown block or code directive.'''
        if pygments:
            d = '\n    :::' + lang
            return d
        else:
            return '\n'
    #@+node:ekr.20160331124028.56: *5* wvp.md_process_one_node
    def md_process_one_node(self, p, result, environment):
        '''Handle one node.'''
        c = self.c
        result.append(self.md_underline2(p))
        d = c.scanAllDirectives(p)
        if self.verbose:
            g.trace(d.get('language') or 'None', ':', p.h)
        s, code = self.md_process_directives(p.b, d)
        result.append(s)
        result.append('\n\n')
            # Add an empty line so bullet lists display properly.
        if code and self.execcode:
            s, err = self.md_exec_code(code, environment)
                # execute code found in a node, append to md
            if not self.restoutput and s.strip():
                s = self.md_format_output(s) # if some non-md to print
            result.append(s) # append, whether plain or md output
            if err:
                err = self.md_format_output(err, prefix='**Error**:')
                result.append(err)
    #@+node:ekr.20160331124028.57: *5* wvp.md_exec_code
    def md_exec_code(self, code, environment):
        """Execute the code, capturing the output in stdout and stderr."""
        trace = True and not g.unitTesting
        if trace: g.trace('\n', code)
        c = self.c
        saveout = sys.stdout # save stdout
        saveerr = sys.stderr
        sys.stdout = bufferout = StringIO()
        sys.stderr = buffererr = StringIO()
        # Protect against exceptions within exec
        try:
            exec(code, environment)
        except Exception:
            # print >> buffererr, traceback.format_exc()
            # buffererr.flush() # otherwise exception info appears too late
            g.es('Viewrendered2 code execution exception')
            g.es_exception()
        # Restore stdout, stderr
        sys.stdout = saveout # was sys.__stdout__
        sys.stderr = saveerr # restore stderr
        return bufferout.getvalue(), buffererr.getvalue()
    #@+node:ekr.20160331124028.58: *5* wvp.md_format_output
    def md_format_output(self, s, prefix='```'):
        """Formats the multi-line string 's' into a md literal block."""
        out = '\n\n' + prefix + '\n\n'
        lines = g.splitLines(s)
        for line in lines:
            out += '    ' + line
        return out + '\n```\n'
    #@+node:ekr.20160331124028.59: *5* wvp.md_process_directives
    def md_process_directives(self, s, d):
        """s is string to process, d is dictionary of directives at the node."""
        trace = False and not g.unitTesting
        lang = d.get('language') or 'python' # EKR.
        codeflag = lang != 'md' # EKR
        lines = g.splitLines(s)
        result = []
        code = ''
        if codeflag and self.showcode:
            result.append(self.md_code_directive(lang)) # EKR
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s, 1)
                word = s[1: i]
                # Add capability to detect mid-node language directives (not really that useful).
                # Probably better to just use a code directive.  "execute-script" is not possible.
                # If removing, ensure "if word in g.globalDirectiveList:  continue" is retained
                # to stop directive being put into the reST output.
                if word == 'language' and not codeflag: # only if not already code
                    lang = s[i:].strip()
                    codeflag = lang in ['python',]
                    if codeflag:
                        if self.verbose:
                            g.es('New code section within node:', lang)
                        if self.showcode:
                            result.append(self.md_code_directive(lang)) # EKR
                    else:
                        result.append('\n\n')
                    continue
                elif word in g.globalDirectiveList:
                    continue
            if codeflag:
                if self.showcode:
                    result.append('    ' + s) # 4 space indent on each line
                code += s # accumulate code lines for execution
            else:
                result.append(s)
        result = ''.join(result)
        if trace: g.trace('result:\n', result) # ,'\ncode:',code)
        return result, code
    #@+node:ekr.20160331124028.60: *5* wvp.md_underline2
    def md_underline2(self, p):
        """
        Use the given string and convert it to a markdown headline for display
        """
        # Use relatively unused underline characters, cater for many levels
        l = p.level() - self.reflevel + 1
        ch = '#' * l
        ch += ' ' + p.h
        return ch
    #@+node:ekr.20160331124028.61: *5* wvp.md_write_md
    def md_write_md(self, root, s):
        '''Write s, the final assembled md text, to leo.md.'''
        c = self.c
        filename = 'leo.md'
        d = c.scanAllDirectives(root)
        path = d.get('path')
        pathname = g.os_path_finalize_join(path, filename)
        # Render constructed md string
        # s = self.html_render(s)
        f = open(pathname, 'wb')
        f.write(s.encode('utf8'))
        f.close()
    #@+node:ekr.20160331124028.62: *3* wvp.export
    def export(self):
        """Sends self.html to an external browser through leo.html.

        Note: If rendering outputs a file, e.g. leo.html, then this routine
        need not write the file again as is presently the case."""
        import webbrowser
        c = self.c
        path = c.getNodePath(c.rootPosition())
        pathname = g.os_path_finalize_join(path, 'leo.html')
        f = open(pathname, 'wb')
        f.write(self.html.encode('utf8'))
        f.close()
        webbrowser.open(pathname, new=0, autoraise=True)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

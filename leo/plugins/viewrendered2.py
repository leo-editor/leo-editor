#@+leo-ver=5-thin
#@+node:ekr.20140225222704.16748: * @file viewrendered2.py
#@+<< docstring >>
#@+node:ekr.20140226074510.4187: ** << docstring >>
'''

Creates a window for *live* rendering of reSTructuredText, markdown text,
images, movies, sounds, rst, html, etc.

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

``hide-rendering-pane``
    Makes the rendering pane invisible, but does not destroy it.

``lock-unlock-rendering-pane``
    Toggles the locked state of the rendering pane.
    When unlocked (the initial state), the rendering pane renders the contents
    of the presently selected node.
    When locked, the rendering pane does not change when other nodes are selected.
    This is useful for playing movies in the rendering pane.
    
``pause-play-movie``
    This command has effect only if the rendering pane is presently showing a movie.
    It pauses the movie if playing, or resumes the movie if paused.

``show-rendering-pane``
    Makes the rendering pane visible.

``toggle-rendering-pane``
    Shows the rendering pane if invisible, otherwise hides it.
    
``update-rendering-pane``
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

This plugin renders @md, @image, @html, @movie, @networkx and @svg nodes as follows:

**Note**: For @image, @movie and @svg nodes, either the headline or the first line of body text may
contain a filename.  If relative, the filename is resolved relative to Leo's load directory.

- ``@md`` renderes the body text as markdown, as described above.

- ``@graphics-script`` executes the script in the body text in a context containing
  two predefined variables:
      
    - gs is the QGraphicsScene for the rendering pane.
    - gv is the QGraphicsView for the rendering pane.
    
  Using these variables, the script in the body text may create graphics to the rendering pane.

- ``@image`` renders the file as an image.


- ``@html`` renders the body text as html.


- ``@movie`` plays the file as a movie.  @movie also works for music files.

- ``@networkx`` is non-functional at present.  It is intended to
  render the body text as a networkx graph.
  See http://networkx.lanl.gov/


- ``@svg`` renders the file as a (possibly animated!) svg (Scalable Vector Image).
  See http://en.wikipedia.org/wiki/Scalable_Vector_Graphics
  **Note**: if the first character of the body text is ``<`` after removing Leo directives,
  the contents of body pane is taken to be an svg image.

.. - ``@url`` is non-functional at present.

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
  Suitable extensions can be seen here: 
  http://pythonhosted.org/Markdown/extensions/index.html
  
The following settings are new in the viewrendered2.py plugin:

These settings directly override the corresponiding docutils settings:
  
- ``@string vr-stylesheet-path``
- ``@int vr-halt-level = 6``
- ``@string vr-math-output = mathjax``
- ``@bool vr-smart-quotes = True``
- ``@bool vr-embed_stylesheet = True``
- ``@bool vr-xml-declaration', False``

The following settings override viewrendered2.py internal settings:

- ``@bool vr-verbose = False``
- ``@bool vr-tree_mode = False``
- ``@bool vr-auto_update = True``
- ``@bool vr-lock_node = False``
- ``@bool vr-slideshow = False``
- ``@bool vr-visible_code = True``
- ``@bool vr-execute_code = False``
- ``@bool vr-rest_code_output = False``

Acknowledgments
================

Peter Mills created this plugin, based on the viewrendered.py plugin.

See the viewrendered.py plugin for additional acknowledgments.

'''
#@-<< docstring >>

__version__ = '1.1' # EKR: Move class WebViewPlus into it's own subtree.

#@+<< imports >>
#@+node:ekr.20140226074510.4188: ** << imports >>
import leo.core.leoGlobals as g
from PyQt4 import QtCore, QtGui, QtSvg, QtWebKit
from PyQt4.QtCore import QUrl
import leo.plugins.qtGui as qtGui
g.assertUi('qt')
import os
import sys
from StringIO import StringIO
import traceback

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
    g.es_print('viewrendered2.py: docutils not found',color='red')
    got_docutils = False

## markdown support, non-vital
try:
    from markdown import markdown
    got_markdown = True
except ImportError:
    got_markdown = False
    
try:
    import PyQt4.phonon as phonon
    phonon = phonon.Phonon
except ImportError:
    phonon = None

#import PyQt4.QtCore as QtCore
#import PyQt4.QtGui as QtGui
#import PyQt4.QtSvg as QtSvg
#import PyQt4.QtWebKit as QtWebKit
#@-<< imports >>
#@+<< define stylesheet >>
#@+node:ekr.20140226074510.4189: ** << define stylesheet >>
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
#@-<< define stylesheet >>

#@+at
# To do:
# 
# - Use the free_layout rotate-all command in Leo's toggle-split-direction command.
# - Add dict to allow customize must_update.
# - Lock movies automatically until they are finished?
# - Render @url nodes as html?
# - Support uA's that indicate the kind of rendering desired.
# - (Failed) Make viewrendered-big work.
#@@c

controllers = {}
    # Keys are c.hash(): values are PluginControllers

#@+others
#@+node:ekr.20140226074510.4190: ** Top-level
#@+node:ekr.20140226074510.4191: *3* decorate_window
def decorate_window(w):
    
    w.setStyleSheet(stickynote_stylesheet)
    w.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
    w.resize(600, 300)
#@+node:ekr.20140226074510.4192: *3* init
def init():
    
    g.plugin_signon(__name__)

    g.registerHandler('after-create-leo-frame', onCreate)
    
    g.registerHandler('scrolledMessage', show_scrolled_message)

    return True
#@+node:ekr.20140226074510.4193: *3* onCreate
def onCreate(tag, keys):
    
    c = keys.get('c')
    if c:
        ViewRenderedProvider(c)
    
    return
#@+node:ekr.20140226074510.4194: *3* show_scrolled_message
def show_scrolled_message(tag, kw):

    if g.unitTesting:
        return # This just slows the unit tests.
    c = kw.get('c')
    vr = viewrendered(event=kw)
    title = kw.get('short_title','').strip()
    vr.setWindowTitle(title)
    s = '\n'.join([
        title,
        '=' * len(title),
        '',
        kw.get('msg')
    ])
    vr.update(tag='show-scrolled-message',keywords={'c':c,'force':True,'s':s})
    return True
#@+node:ekr.20140226074510.4195: ** Commands
#@+node:ekr.20140226074510.4196: *3* g.command('preview')
@g.command('preview')
def preview(event):
    '''A synonym for the vr-toggle command.'''
    toggle_rendering_pane(event)
#@+node:ekr.20140226074510.4197: *3* g.command('vr')
@g.command('vr')
def viewrendered(event):
    """Open render view for commander"""
    
    trace = False and not g.unitTesting
    c = event.get('c')
    if not c: return None
   
    global controllers
    vr = controllers.get(c.hash())
    if vr:
        if trace: g.trace('** controller exists: %s' % (vr))
        vr.show()
    else:
        controllers[c.hash()] = vr = ViewRenderedController(c)
        if trace: g.trace('** new controller: %s' % (vr))
        if hasattr(c,'free_layout'):
            vr._ns_id = '_leo_viewrendered'  # for free_layout load/save
            splitter = c.free_layout.get_top_splitter()
            # Careful: we may be unit testing.
            if splitter:
                ok = splitter.add_adjacent(vr,'bodyFrame','right-of')
                if not ok:
                    splitter.insert(0, vr)
        else:
            vr.setWindowTitle("Rendered View")
            vr.resize(600, 600)
            vr.show()
    return vr
#@+node:ekr.20140226074510.4198: *3* g.command('vr-contract')
@g.command('vr-contract')
def contract_rendering_pane(event):
    
    '''Expand the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget,'viewrendered_pane')
        if vr:
            vr.contract()
        else:
            # Just open the pane.
            viewrendered(event)
#@+node:ekr.20140226074510.4199: *3* g.command('vr-expand')
@g.command('vr-expand')
def expand_rendering_pane(event):
    
    '''Expand the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget,'viewrendered_pane')
        if not vr:
            vr = viewrendered(event)
        if vr:
            vr.expand()
#@+node:ekr.20140226074510.4200: *3* g.command('vr-hide')
@g.command('vr-hide')
def hide_rendering_pane(event):
    
    '''Close the rendering pane.'''

    global controllers
    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if vr:
            vr.deactivate()
            vr.deleteLater()
            def at_idle(c=c):
                c.bodyWantsFocusNow()
            QtCore.QTimer.singleShot(0,at_idle)
            h = c.hash()
            c.bodyWantsFocus()
            if vr == controllers.get(h):
                del controllers[h]
            else:
                g.trace('Can not happen: no controller for %s' % (c))
            
# Compatibility
close_rendering_pane = hide_rendering_pane
#@+node:ekr.20140226074510.4201: *3* g.command('vr-lock')
@g.command('vr-lock')
def lock_rendering_pane(event):
    
    '''Pause or play a movie in the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if vr and not vr.locked:
            vr.lock()
#@+node:ekr.20140226074510.4202: *3* g.command('vr-pause-play')
@g.command('vr-pause-play')
def pause_play_movie(event):
    
    '''Pause or play a movie in the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget,'viewrendered_pane')
        if not vr:
            vr = viewrendered(event)
        if vr and vr.vp:
            vp = vr.vp
            if vp.isPlaying():
                vp.pause()
            else:
                vp.play()
#@+node:ekr.20140226074510.4203: *3* g.command('vr-show')
@g.command('vr-show')
def show_rendering_pane(event):
    
    '''Show the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if vr:
            pass # hide_rendering_pane(event)
        else:
            viewrendered(event)
#@+node:ekr.20140226074510.4204: *3* g.command('vr-toggle')
@g.command('vr-toggle')
def toggle_rendering_pane(event):
    
    '''Toggle the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget,'viewrendered_pane')
        if vr:
            hide_rendering_pane(event)
        else:
            viewrendered(event)
#@+node:ekr.20140226074510.4205: *3* g.command('vr-unlock')
@g.command('vr-unlock')
def unlock_rendering_pane(event):
    
    '''Pause or play a movie in the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if vr and vr.locked:
            vr.unlock()
#@+node:ekr.20140226074510.4206: *3* g.command('vr-update')
@g.command('vr-update')
def update_rendering_pane (event):
    
    '''Update the rendering pane'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if not vr:
            vr = viewrendered(event)
        if vr:
            vr.update(tag='view',keywords={'c':c,'force':True})
#@+node:ekr.20140226075611.16792: ** class WebViewPlus (QWidget)
class WebViewPlus(QtGui.QWidget):
    #@+others
    #@+node:ekr.20140226075611.16793: *3* ctor (WebViewPlus) & helpers
    def __init__(self, pc):
        super(WebViewPlus, self).__init__()
        self.app = QtCore.QCoreApplication.instance()
        self.c = c = pc.c
        self.docutils_settings = None # Set below.
        self.html = '' # For communication with export().
        self.last_node = c.p
        self.pc = pc
        self.pr = None
        self.rendering = False
        self.s = ''
        self.timer = self.init_timer()
        self.view = self.init_view()
        # Must be done after calling init_view.
        self.docutils_settings = self.init_config()
    #@+node:ekr.20140227055626.16842: *4* init_view
    def init_view(self):
        '''Init the vr pane.'''
            # QWebView parts, including progress bar
        view = QtWebKit.QWebView()
        mf = view.page().mainFrame()
        mf.contentsSizeChanged.connect(self.restore_scroll_position)
        # ToolBar parts
        self.export_button = QtGui.QPushButton('Export')
        self.export_button.clicked.connect(self.export)
        self.toolbar = QtGui.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(16,16))
        for a in (QtWebKit.QWebPage.Back, QtWebKit.QWebPage.Forward):
            self.toolbar.addAction(view.pageAction(a))
        self.toolbar.setToolTip(self.tooltip_text(
            """
            Toolbar:
            -  Navigation buttons (like a normal browser), 
            -  Reload button which is used to "update" this rendering pane
            -  Options tool-button to control the way rendering is done
            -  Export button to export to the standard browser
                    
            Keyboard shortcuts:
            <b>Ctl-C</b>  Copy html/text from the pane
            Ctl-+  Zoom in
            Ctl--  Zoom out
            Ctl-=  Zoom to original size"""))
        # Handle reload separately since this is used to re-render everything
        self.reload_action = view.pageAction(QtWebKit.QWebPage.Reload)
        self.reload_action.triggered.connect(self.render)
        self.toolbar.addAction(self.reload_action)
        #self.reload_action.clicked.connect(self.render)
        # Create the "Mode" toolbutton
        self.toolbutton = QtGui.QToolButton()
        self.toolbutton.setText('Options')
        self.toolbutton.setPopupMode(QtGui.QToolButton.InstantPopup)
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
            Code output reST - Assume code execution text output is reStructuredText."""))
        self.toolbar.addWidget(self.toolbutton)
        # Add a progress bar
        self.pbar = QtGui.QProgressBar()
        self.pbar.setMaximumWidth(120)
        menu = QtGui.QMenu()
        self.tree_mode_action = QtGui.QAction('Whole tree', self,
                                         checkable=True, triggered=self.state_change)
        #self.tree_mode_action.setChecked(False)
        menu.addAction(self.tree_mode_action)
        self.verbose_mode_action = QtGui.QAction('Verbose logging', self,
                                         checkable=True, triggered=self.state_change)
        menu.addAction(self.verbose_mode_action)
        self.auto_mode_action = QtGui.QAction('Auto-update', self,
                                         checkable=True, triggered=self.state_change)
        menu.addAction(self.auto_mode_action)
        #self.auto_mode_action.setChecked(True)
        self.lock_mode_action = QtGui.QAction('Lock to node', self,
                                         checkable=True, triggered=self.lock)
        menu.addAction(self.lock_mode_action)
        # Add an s5 option
        self.slideshow_mode_action = QtGui.QAction('Show as slideshow', self,
                                         checkable=True, triggered=self.state_change)
        menu.addAction(self.slideshow_mode_action)
        #self.s5_mode_action = QtGui.QAction('s5 slideshow', self,
        #                                 checkable=True, triggered=self.lock)
        #menu.addAction(self.lock_mode_action)
        menu.addSeparator()  # Separate render mode and code options
        self.visible_code_action = QtGui.QAction('Visible code', self,
                                         checkable=True, triggered=self.state_change)
        #self.visible_code_action.setChecked(True)
        menu.addAction(self.visible_code_action)
        self.execute_code_action = QtGui.QAction('Execute code', self,
                                         checkable=True, triggered=self.state_change)
        menu.addAction(self.execute_code_action)
        self.reST_code_action = QtGui.QAction('Code outputs reST', self,
                                         checkable=True, triggered=self.state_change)
        menu.addAction(self.reST_code_action)

        # radio button checkables example at http://stackoverflow.com/questions/10368947/how-to-make-qmenu-item-checkable-pyqt4-python
        self.toolbutton.setMenu(menu)
        # Remaining toolbar items
        #self.toolbar.addSeparator()
        #self.toolbar.addWidget(self.export_button)
        
        # Create the 'Export' toolbutton
        self.export_button = QtGui.QToolButton()
        self.export_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.export_button.setToolTip(self.tooltip_text(
            """
            Show this in the default web-browser.
            If the default browser is not already open it will be started.  Exporting
            is useful for full-screen slideshows and also for using the printing and
            saving functions of the browser."""))
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
        #        spacer = QtGui.QWidget() 
        #        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 
        #        self.toolbar.addWidget(spacer)
        self.title = QtGui.QLabel()
        self.title.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) 
        self.title.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.title.setTextFormat(1)  # Set to rich text interpretation
        # None of this font stuff works! - instead I've gone for rich text above
        # font = QtGui.QFont("Sans Serif", 12, QtGui.QFont.Bold)
        #font = QtGui.QFont("Arial", 8)
        #font = QtGui.QFont()
        #font.setBold(True)
        #font.setWeight(75)
        self.toolbar.addWidget(self.title)  # if needed, use 'title_action =' 
        #title_action.setFont(font)  # Set font of 'QAction' rather than widget
        spacer = QtGui.QWidget() 
        spacer.setMinimumWidth(5) 
        self.toolbar.addWidget(spacer)
        # Layouts
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0,0,0,0)  # Remove the default 11px margins
        vlayout.addWidget(self.toolbar)
        vlayout.addWidget(view)
        self.setLayout(vlayout)
        # Key shortcuts - zoom
        view.setZoomFactor(1.0)  # smallish panes demand small zoom
        self.zoomIn = QtGui.QShortcut("Ctrl++", self, activated = lambda: view.setZoomFactor(view.zoomFactor()+.2))
        self.zoomOut = QtGui.QShortcut("Ctrl+-", self, activated = lambda: view.setZoomFactor(view.zoomFactor()-.2))
        self.zoomOne = QtGui.QShortcut("Ctrl+0", self, activated = lambda: view.setZoomFactor(0.8))
        # Some QWebView settings
        # setMaximumPagesInCache setting prevents caching of images etc.
        view.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled,True)
        # Prevent caching, especially of images
        view.settings().setMaximumPagesInCache(0)
        view.settings().setObjectCacheCapacities(0, 0, 0)
        #self.toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        # Set up other widget states
        
        # Get Leo settings related to docutils.  Using 'or' trick for defaults
        #---------------------------------------------------------------------
        # defaults ...
        #'stylesheet_path' : './css/leo_vr.css',  # path for css files
        #'halt_level' : 6,  # raise halt level to still attempt to render
        #'report_level' : 5, #5,  # heading level errors, remove rather than error in output
        #'math_output' : 'mathjax',  # use MathJax for rendering equations
        #'smart_quotes' : True,  # ??allows --,---,... to dashes etc., nice quotes
        #'embed_stylesheet' : True,  # include stylesheet into a self-contained html
        #'xml_declaration' : False,  # remove declaration to allow import/paste into Word
        return view
    #@+node:ekr.20140227055626.16843: *4* init_config
    def init_config(self):
        '''Init docutils settings.'''
        ds = {}
        gc = self.c.config
        def getConfig(getfun, name, default, setfun=None, setvar=None):
            """Make a shorthand way to get and store a setting with defaults"""
            r = getfun('vr_'+name)  # keep docutils name but prefix
            if setfun:  # settings are held in Qactions
                if r:  setfun(r)
                else:  setfun(default)
            elif setvar:  # Just setting a variable
                if r:  setvar = r
                else:  setvar = default                
            else:  # settings held in dict (for docutils use)
                if r:  ds[name] = r
                else:  ds[name] = default
        # Do docutils config (note that the vr_ prefix is omitted)
        getConfig(gc.getString, 'stylesheet_path', '')
        getConfig(gc.getInt,    'halt_level', 6)
        getConfig(gc.getInt,    'report_level', 5)
        getConfig(gc.getString, 'math_output', 'mathjax')
        getConfig(gc.getBool,   'smart_quotes', True)
        getConfig(gc.getBool,   'embed_stylesheet', True)
        getConfig(gc.getBool,   'xml_declaration', False)
        # Do VR2 init values
        getConfig(gc.getBool, 'verbose', False, self.verbose_mode_action.setChecked)
        getConfig(gc.getBool, 'tree_mode', False, self.tree_mode_action.setChecked)
        getConfig(gc.getBool, 'auto_update', True, self.auto_mode_action.setChecked)
        getConfig(gc.getBool, 'lock_node', False, self.lock_mode_action.setChecked)
        getConfig(gc.getBool, 'slideshow', False, self.slideshow_mode_action.setChecked)
        getConfig(gc.getBool, 'visible_code', True, self.visible_code_action.setChecked)
        getConfig(gc.getBool, 'execute_code', False, self.execute_code_action.setChecked)
        getConfig(gc.getBool, 'rest_code_output', False, self.reST_code_action.setChecked)
        # Misc other internal settings
        # Mark of the Web (for IE) to allow sensible security options
        #getConfig(gc.getBool, 'include_MOTW', True, setvar=self.MOTW)
        return ds
    #@+node:ekr.20140227055626.16844: *4* init_timer
    def init_timer(self):
        '''Init the timer for delayed rendering (to allow smooth tree navigation).'''
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(1100)
            # just longer than the 1000ms interval of calls from update_rst
        timer.timeout.connect(self.render)
        return timer
    #@+node:ekr.20140226081920.16816: *4* tooltip_text
    def tooltip_text(self,s):
        '''Return the reformatted tooltip text corresponding to the triple string s.'''
        lines = g.splitLines(s)
        if lines:
            i = 0 if lines[0].strip() else 1
            s = ''.join(lines[i:])
            s = g.adjustTripleString(s,self.c.tab_width)
        return s
    #@+node:ekr.20140227055626.16845: *3* gui helpers
    #@+node:ekr.20140226075611.16798: *4* getUIconfig
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
    #@+node:ekr.20140226075611.16800: *4* lock
    def lock(self):
        """Implement node lock (triggered by "Lock node" action)."""
        # Lock "action" has been triggered, so state will have changed.
        if self.lock_mode_action.isChecked():  # Just become active
            self.plock = self.pc.c.p.copy()  # make a copy of node position
            if self.pr:
                self.pc.scrollbar_pos_dict[self.pr.v] = self.view.page().\
                    mainFrame().scrollBarValue(QtCore.Qt.Vertical)
        else:
            self.render()
                # Render again since root node may have changed now
        # Add an icon or marker to node currently locked?
    #@+node:ekr.20140226075611.16799: *4* render_rst
    def render_rst(self, s, keywords):
        """Generate the reST and render it in this pane."""
        self.getUIconfig()
        self.s = keywords.get('s') if 's' in keywords else ''
        if self.auto:
            self.timer.start()
    #@+node:ekr.20140226075611.16802: *4* restore_scroll_position
    def restore_scroll_position(self):
        # Restore scroll bar position for (possibly) new node
        d = self.pc.scrollbar_pos_dict
        mf = self.view.page().mainFrame()
        # Set the scrollbar.
        if self.pr is not None:
            spos = d.get(self.pr.v,mf.scrollBarValue(QtCore.Qt.Vertical))
        else:
            spos = 0
        mf.setScrollBarValue(QtCore.Qt.Vertical, spos)
        #print 'remembered scroll pos restored, re-read pos:', spos, mf.scrollBarValue(QtCore.Qt.Vertical)
    #@+node:ekr.20140226075611.16794: *4* state_change
    def state_change(self, checked):
        """A wrapper for 'render' to re-render on all QAction state changes."""
        self.render()
    #@+node:ekr.20140226075611.16801: *3* render & helpers
    def render(self):
        """Re-render the existing string, but probably with new configuration."""
        if self.rendering:
            # if already rendering, don't execute
            self.timer.start()  # Don't forget to do this last render request
        else:
            try:
                self.rendering = True
                self.render_helper()
            finally:
                # No longer rendering, OK to receive another rendering call
                self.rendering = False
    #@+node:ekr.20140226125539.16825: *4* render_helper & helper
    def render_helper(self):
        '''Rendinging helper: self.rendering is True.'''
        c,p,pc = self.c,self.c.p,self.pc
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
        if pc.default_kind in ('big','rst','html', 'md'):
            # Trial of rendering to file and have QWebView load this without blocking
            ext = 'html'
            # Write the output file
            pathname = g.os_path_finalize_join(self.path,'leo.' + ext)
            f = file(pathname,'wb')
            f.write(html.encode('utf8'))
            f.close()
            # render
            self.view.setUrl(QUrl.fromLocalFile(pathname))
            #self.view.setHtml(html, baseUrl = QUrl(self.path))
            # PMM
            # Write the output file 
            #pathname = "M:/leo/info/leo.html"
            #f = file(pathname,'wb')
            #f.write(self.s.encode('utf8'))
            #f.close()
            #w.load(QUrl("M:/leo/info/leo.html"))
        else:
            self.view.setPlainText(html) 
        if not self.auto:  
            self.pbar.setValue(100)
            self.app.processEvents()
            self.pbar_action.setVisible(False)
    #@+node:ekr.20140226125539.16826: *5* to_html & helper
    def to_html(self,p):
        '''Convert p.b to html using docutils.'''
        c,pc = self.c,self.pc
        mf = self.view.page().mainFrame()
        path = g.scanAllAtPathDirectives(c,p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        # Need to save position of last node before rendering
        ps = mf.scrollBarValue(QtCore.Qt.Vertical)
        pc.scrollbar_pos_dict[self.last_node.v] = ps
        # Which node should be rendered?
        if self.lock_mode:
            # use locked node for position to be rendered.
            self.pr = self.plock  
        else:
            # use new current node, whether changed or not.
            self.pr = c.p  # use current node
        self.last_node = self.pr.copy() 
            # Store this node as last node rendered
        # Set the node header in the toolbar.
        self.title.setText('' if self.s else '<b>'+self.pr.h+'</b>')
        if not self.auto:  
            self.pbar.setValue(0)
            self.pbar_action.setVisible(True)
        # Handle all the nodes in the tree.
        html = self.process_nodes(self.pr,tree=self.tree)
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
                return 'RST error:\n%s\n\n%s' % (msg,html)
            else:
                return html
    #@+node:ekr.20140226075611.16797: *6* process_nodes & helpers
    def process_nodes(self,p,tree=True):
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
        self.process_one_node(root,result)
        if tree:
            # Create a progress counter showing 50% at end of tree processing.
            i,numnodes = 0,sum(1 for j in p.subtree())
            for p in root.subtree():
                self.process_one_node(p,result)
                if not self.auto:
                    i += 1
                    self.pbar.setValue(i * 50 / numnodes)
                self.app.processEvents()
        s = '\n'.join(result)
        if self.verbose:
            self.write_rst(root,s)
        return s
    #@+node:ekr.20140227055626.16838: *7* code_directive
    def code_directive(self,lang):
        '''Return an reST code directive or an reST block.'''
        
        if True: ### has_pygments:
            # Peter Mills's original code.
            # See code in initCodeBlock for complications.
            return '\n\n.. code:: '+lang+'\n\n'
        else:
            return '\n\n::\n\n'
    #@+node:ekr.20140227055626.16841: *7* initCodeBlockString (from leoRst, for reference)
    def initCodeBlockString(self,p):

        trace = False and not g.unitTesting
        c = self.c
        # if trace: os.system('cls')
        d = c.scanAllDirectives(p)
        language = d.get('language')
        if language is None: language = 'python'
        else: language = language.lower()
        syntax = SilverCity is not None

        if trace: g.trace('language',language,'language.title()',language.title(),p.h)

        # Note: lines that end with '\n\n' are a signal to handleCodeMode.
        s = self.getOption('code_block_string')
        if s:
            self.code_block_string = s.replace('\\n','\n')
        elif syntax and language in ('python','ruby','perl','c'):
            self.code_block_string = '**code**:\n\n.. code-block:: %s\n\n' % (
                language.title())
        else:
            self.code_block_string = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
    #@+node:ekr.20140226125539.16824: *7* process_one_node
    def process_one_node(self,p,result):
        '''Handle one node.'''
        c = self.c
        result.append(self.underline2(p))
        d = c.scanAllDirectives(p)
        if self.verbose:
            g.trace(d.get('language') or 'None',':',p.h)
        s,code = self.process_directives(p.b,d)
        result.append(s)
        result.append('\n\n')
            # Add an empty line so bullet lists display properly.
        if code and self.execcode:
            s,err = self.exec_code(code)
                # execute code found in a node, append to reST
            if not self.restoutput and s.strip():
                s = self.format_output(s)  # if some non-reST to print
            result.append(s) # append, whether plain or reST output
            if err:
                err = self.format_output(err, prefix='**Error**::')      
                result.append(err)
    #@+node:ekr.20140226125539.16822: *7* exec_code
    def exec_code(self,code):
        """Execute the code, capturing the output in stdout and stderr."""
        trace = True and not g.unitTesting
        if trace: g.trace('\n',code)
        c = self.c
        saveout = sys.stdout  # save stdout
        saveerr = sys.stderr
        sys.stdout = bufferout = StringIO()
        sys.stderr = buffererr = StringIO()
        # Protect against exceptions within exec
        try:
            scope = {'c':c,'g': g,'p':c.p} # EKR: predefine c & p.
            exec code in scope
        except Exception:
            #print Exception, err
            #print sys.exc_info()[1]
            print >> buffererr, traceback.format_exc()
            buffererr.flush()  # otherwise exception info appears too late
            g.es('Viewrendered traceback:\n', sys.exc_info()[1])
        # Restore stdout, stderr
        sys.stdout = saveout  # was sys.__stdout__
        sys.stderr = saveerr  # restore stderr
        return bufferout.getvalue(), buffererr.getvalue()
    #@+node:ekr.20140226125539.16823: *7* format_output
    def format_output(self,s, prefix='::'):
        """Formats the multi-line string 's' into a reST literal block."""
        out = '\n\n'+prefix+'\n\n'
        lines = g.splitLines(s)
        for line in lines:
            out += '    ' + line
        return out + '\n'
    #@+node:ekr.20140226075611.16796: *7* process_directives
    def process_directives(self, s, d):
        """s is string to process, d is dictionary of directives at the node."""
        trace = False and not g.unitTesting
        lang = d.get('language') or 'python' # EKR.
        codeflag = lang != 'rest' # EKR
        lines = g.splitLines(s)
        result = []
        code = ''
        if codeflag and self.showcode:
            result.append(self.code_directive(lang)) # EKR
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s,1)
                word = s[1:i]
                # Add capability to detect mid-node language directives (not really that useful).
                # Probably better to just use a code directive.  "execute-script" is not possible.
                # If removing, ensure "if word in g.globalDirectiveList:  continue" is retained
                # to stop directive being put into the reST output.
                if word=='language' and not codeflag:  # only if not already code
                    lang = s[i:].strip()
                    codeflag = lang in ['python',]
                    if codeflag:
                        if self.verbose:
                            g.es('New code section within node:',lang)
                        if self.showcode:
                            result.append(self.code_directive(lang)) # EKR
                    else:
                        result.append('\n\n')
                    continue
                elif word in g.globalDirectiveList:
                    continue
            if codeflag:
                if self.showcode:
                    result.append('    ' + s)  # 4 space indent on each line
                code += s  # accumulate code lines for execution
            else:
                result.append(s)
        result = ''.join(result)
        if trace: g.trace('result:\n',result) # ,'\ncode:',code)
        return result, code
    #@+node:ekr.20140226075611.16795: *7* underline2
    def underline2(self, p):
        """
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
        ch = """><:_`*+"';/{|}()$%&@#"""[p.level()-self.reflevel]
        n = max(4,len(g.toEncodedString(p.h,reportErrors=False)))
        return '%s\n%s\n\n' % (p.h,ch*n)
    #@+node:ekr.20140227055626.16839: *7* write_rst
    def write_rst(self,root,s):
        '''Write s, the final assembled reST text, to leo.rst.'''
        filename = 'leo.rst'
        d = c.scanAllDirectives(root)
        path = d.get('path')
        pathname = g.os_path_finalize_join(path,filename)
        # Render constructed reST string
        # s = self.html_render(s)
        f = file(pathname,'wb')
        f.write(s.encode('utf8'))
        f.close()
    #@+node:ekr.20140226075611.16803: *3* export
    def export(self):
        """Sends self.html to an external browser through leo.html.
        
        Note: If rendering outputs a file, e.g. leo.html, then this routine
        need not write the file again as is presently the case."""
        import webbrowser
        pathname = g.os_path_finalize_join(self.path,'leo.html')
        f = file(pathname,'wb')
        f.write(self.html.encode('utf8'))
        f.close()
        webbrowser.open(pathname,new=0, utoraise=True)
    #@+node:ekr.20140226075611.16801: *3* render & helpers
    def render(self):
        """Re-render the existing string, but probably with new configuration."""
        if self.rendering:
            # if already rendering, don't execute
            self.timer.start()  # Don't forget to do this last render request
        else:
            try:
                self.rendering = True
                self.render_helper()
            finally:
                # No longer rendering, OK to receive another rendering call
                self.rendering = False
    #@+node:ekr.20140226125539.16825: *4* render_helper & helper
    def render_helper(self):
        '''Rendinging helper: self.rendering is True.'''
        c,p,pc = self.c,self.c.p,self.pc
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
        if pc.default_kind in ('big','rst','html', 'md'):
            # Trial of rendering to file and have QWebView load this without blocking
            ext = 'html'
            # Write the output file
            pathname = g.os_path_finalize_join(self.path,'leo.' + ext)
            f = file(pathname,'wb')
            f.write(html.encode('utf8'))
            f.close()
            # render
            self.view.setUrl(QUrl.fromLocalFile(pathname))
            #self.view.setHtml(html, baseUrl = QUrl(self.path))
            # PMM
            # Write the output file 
            #pathname = "M:/leo/info/leo.html"
            #f = file(pathname,'wb')
            #f.write(self.s.encode('utf8'))
            #f.close()
            #w.load(QUrl("M:/leo/info/leo.html"))
        else:
            self.view.setPlainText(html) 
        if not self.auto:  
            self.pbar.setValue(100)
            self.app.processEvents()
            self.pbar_action.setVisible(False)
    #@+node:ekr.20140226125539.16826: *5* to_html & helper
    def to_html(self,p):
        '''Convert p.b to html using docutils.'''
        c,pc = self.c,self.pc
        mf = self.view.page().mainFrame()
        path = g.scanAllAtPathDirectives(c,p) or c.getNodePath(p)
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            os.chdir(path)
        # Need to save position of last node before rendering
        ps = mf.scrollBarValue(QtCore.Qt.Vertical)
        pc.scrollbar_pos_dict[self.last_node.v] = ps
        # Which node should be rendered?
        if self.lock_mode:
            # use locked node for position to be rendered.
            self.pr = self.plock  
        else:
            # use new current node, whether changed or not.
            self.pr = c.p  # use current node
        self.last_node = self.pr.copy() 
            # Store this node as last node rendered
        # Set the node header in the toolbar.
        self.title.setText('' if self.s else '<b>'+self.pr.h+'</b>')
        if not self.auto:  
            self.pbar.setValue(0)
            self.pbar_action.setVisible(True)
        # Handle all the nodes in the tree.
        html = self.process_nodes(self.pr,tree=self.tree)
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
                return 'RST error:\n%s\n\n%s' % (msg,html)
            else:
                return html
    #@+node:ekr.20140226075611.16797: *6* process_nodes & helpers
    def process_nodes(self,p,tree=True):
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
        self.process_one_node(root,result)
        if tree:
            # Create a progress counter showing 50% at end of tree processing.
            i,numnodes = 0,sum(1 for j in p.subtree())
            for p in root.subtree():
                self.process_one_node(p,result)
                if not self.auto:
                    i += 1
                    self.pbar.setValue(i * 50 / numnodes)
                self.app.processEvents()
        s = '\n'.join(result)
        if self.verbose:
            self.write_rst(root,s)
        return s
    #@+node:ekr.20140227055626.16838: *7* code_directive
    def code_directive(self,lang):
        '''Return an reST code directive or an reST block.'''
        
        if True: ### has_pygments:
            # Peter Mills's original code.
            # See code in initCodeBlock for complications.
            return '\n\n.. code:: '+lang+'\n\n'
        else:
            return '\n\n::\n\n'
    #@+node:ekr.20140227055626.16841: *7* initCodeBlockString (from leoRst, for reference)
    def initCodeBlockString(self,p):

        trace = False and not g.unitTesting
        c = self.c
        # if trace: os.system('cls')
        d = c.scanAllDirectives(p)
        language = d.get('language')
        if language is None: language = 'python'
        else: language = language.lower()
        syntax = SilverCity is not None

        if trace: g.trace('language',language,'language.title()',language.title(),p.h)

        # Note: lines that end with '\n\n' are a signal to handleCodeMode.
        s = self.getOption('code_block_string')
        if s:
            self.code_block_string = s.replace('\\n','\n')
        elif syntax and language in ('python','ruby','perl','c'):
            self.code_block_string = '**code**:\n\n.. code-block:: %s\n\n' % (
                language.title())
        else:
            self.code_block_string = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
    #@+node:ekr.20140226125539.16824: *7* process_one_node
    def process_one_node(self,p,result):
        '''Handle one node.'''
        c = self.c
        result.append(self.underline2(p))
        d = c.scanAllDirectives(p)
        if self.verbose:
            g.trace(d.get('language') or 'None',':',p.h)
        s,code = self.process_directives(p.b,d)
        result.append(s)
        result.append('\n\n')
            # Add an empty line so bullet lists display properly.
        if code and self.execcode:
            s,err = self.exec_code(code)
                # execute code found in a node, append to reST
            if not self.restoutput and s.strip():
                s = self.format_output(s)  # if some non-reST to print
            result.append(s) # append, whether plain or reST output
            if err:
                err = self.format_output(err, prefix='**Error**::')      
                result.append(err)
    #@+node:ekr.20140226125539.16822: *7* exec_code
    def exec_code(self,code):
        """Execute the code, capturing the output in stdout and stderr."""
        trace = True and not g.unitTesting
        if trace: g.trace('\n',code)
        c = self.c
        saveout = sys.stdout  # save stdout
        saveerr = sys.stderr
        sys.stdout = bufferout = StringIO()
        sys.stderr = buffererr = StringIO()
        # Protect against exceptions within exec
        try:
            scope = {'c':c,'g': g,'p':c.p} # EKR: predefine c & p.
            exec code in scope
        except Exception:
            #print Exception, err
            #print sys.exc_info()[1]
            print >> buffererr, traceback.format_exc()
            buffererr.flush()  # otherwise exception info appears too late
            g.es('Viewrendered traceback:\n', sys.exc_info()[1])
        # Restore stdout, stderr
        sys.stdout = saveout  # was sys.__stdout__
        sys.stderr = saveerr  # restore stderr
        return bufferout.getvalue(), buffererr.getvalue()
    #@+node:ekr.20140226125539.16823: *7* format_output
    def format_output(self,s, prefix='::'):
        """Formats the multi-line string 's' into a reST literal block."""
        out = '\n\n'+prefix+'\n\n'
        lines = g.splitLines(s)
        for line in lines:
            out += '    ' + line
        return out + '\n'
    #@+node:ekr.20140226075611.16796: *7* process_directives
    def process_directives(self, s, d):
        """s is string to process, d is dictionary of directives at the node."""
        trace = False and not g.unitTesting
        lang = d.get('language') or 'python' # EKR.
        codeflag = lang != 'rest' # EKR
        lines = g.splitLines(s)
        result = []
        code = ''
        if codeflag and self.showcode:
            result.append(self.code_directive(lang)) # EKR
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s,1)
                word = s[1:i]
                # Add capability to detect mid-node language directives (not really that useful).
                # Probably better to just use a code directive.  "execute-script" is not possible.
                # If removing, ensure "if word in g.globalDirectiveList:  continue" is retained
                # to stop directive being put into the reST output.
                if word=='language' and not codeflag:  # only if not already code
                    lang = s[i:].strip()
                    codeflag = lang in ['python',]
                    if codeflag:
                        if self.verbose:
                            g.es('New code section within node:',lang)
                        if self.showcode:
                            result.append(self.code_directive(lang)) # EKR
                    else:
                        result.append('\n\n')
                    continue
                elif word in g.globalDirectiveList:
                    continue
            if codeflag:
                if self.showcode:
                    result.append('    ' + s)  # 4 space indent on each line
                code += s  # accumulate code lines for execution
            else:
                result.append(s)
        result = ''.join(result)
        if trace: g.trace('result:\n',result) # ,'\ncode:',code)
        return result, code
    #@+node:ekr.20140226075611.16795: *7* underline2
    def underline2(self, p):
        """
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
        ch = """><:_`*+"';/{|}()$%&@#"""[p.level()-self.reflevel]
        n = max(4,len(g.toEncodedString(p.h,reportErrors=False)))
        return '%s\n%s\n\n' % (p.h,ch*n)
    #@+node:ekr.20140227055626.16839: *7* write_rst
    def write_rst(self,root,s):
        '''Write s, the final assembled reST text, to leo.rst.'''
        filename = 'leo.rst'
        d = c.scanAllDirectives(root)
        path = d.get('path')
        pathname = g.os_path_finalize_join(path,filename)
        # Render constructed reST string
        # s = self.html_render(s)
        f = file(pathname,'wb')
        f.write(s.encode('utf8'))
        f.close()
    #@-others
#@+node:ekr.20140226074510.4207: ** class ViewRenderedProvider
class ViewRenderedProvider:
    #@+others
    #@+node:ekr.20140226074510.4208: *3* __init__
    def __init__(self, c):
        self.c = c
        # Careful: we may be unit testing.
        if hasattr(c, 'free_layout'):
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.register_provider(self)
    #@+node:ekr.20140226074510.4209: *3* ns_provides
    def ns_provides(self):
        return[('Viewrendered', '_leo_viewrendered')]
    #@+node:ekr.20140226074510.4210: *3* ns_provide
    def ns_provide(self, id_):
        
        global controllers
        
        if id_ == '_leo_viewrendered':
            c = self.c
            vr = controllers.get(c.hash()) or ViewRenderedController(c)
            # return ViewRenderedController(self.c)
            return vr
    #@-others
#@+node:ekr.20140226074510.4211: ** class ViewRenderedController (QWidget)
class ViewRenderedController(QtGui.QWidget):
    
    '''A class to control rendering in a rendering pane.'''

    #@+others
    #@+node:ekr.20140226074510.4212: *3* ctor & helpers
    def __init__ (self, c, parent=None):
        
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName('viewrendered_pane')
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        
        self.active = False
        self.c = c
        self.badColors = []
        self.delete_callback = None
        self.gnx = None
        self.inited = False
        self.gs = None # For @graphics-script: a QGraphicsScene 
        self.gv = None # For @graphics-script: a QGraphicsView
        #self.kind = 'rst' # in self.dispatch_dict.keys()
        self.length = 0 # The length of previous p.b.
        self.locked = False
        self.scrollbar_pos_dict = {} # Keys are vnodes, values are positions.
        self.sizes = [] # Saved splitter sizes.
        self.splitter_index = None # The index of the rendering pane in the splitter.
        self.svg_class = QtSvg.QSvgWidget
        self.text_class = QtGui.QTextBrowser # QtGui.QTextEdit # qtGui.LeoQTextBrowser 
        self.html_class = WebViewPlus #QtWebKit.QWebView
        self.graphics_class = QtGui.QGraphicsWidget
        self.vp = None # The present video player.
        self.w = None # The present widget in the rendering pane.
        self.title = None
        # User-options:
        self.default_kind = c.config.getString('view-rendered-default-kind') or 'rst'
        self.auto_create  = c.config.getBool('view-rendered-auto-create',False)
        # self.auto_hide    = c.config.getBool('view-rendered-auto-hide',False)
        self.background_color = c.config.getColor('rendering-pane-background-color') or 'white'
        self.node_changed = True
        
        # Init.
        self.create_dispatch_dict()
        self.activate()
        
        #---------------PMM additional elements for WebView additions for reST
        self.reflevel = 0
        # Special-mode rendering settings
        self.verbose = False
        self.output = 'html'
        self.tree = True
        self.showcode = True
        self.execcode = False
        self.restoutput = False
    #@+node:ekr.20140226074510.4213: *4* create_dispatch_dict
    def create_dispatch_dict (self):
        
        pc = self
        
        pc.dispatch_dict = {
            'big':          pc.update_rst,
            'html':         pc.update_html,
            'graphics-script':  pc.update_graphics_script,
            'image':        pc.update_image,
            'md':           pc.update_md,
            'movie':        pc.update_movie,
            'networkx':     pc.update_networkx,
            'rst':          pc.update_rst,
            'svg':          pc.update_svg,
            'url':          pc.update_url,
        }
    #@+node:ekr.20140226074510.4214: *3* closeEvent
    def closeEvent(self, event):
        
        self.deactivate()

    #@+node:ekr.20140226074510.4215: *3* contract & expand
    def contract(self):
        self.change_size(-100)

    def expand(self):
        self.change_size(100)
        
    def change_size(self,delta):
        if hasattr(self.c,'free_layout'):
            splitter = self.parent()
            i = splitter.indexOf(self)
            assert i > -1
            sizes = splitter.sizes()
            n = len(sizes)
            for j in range(len(sizes)):
                if j == i:
                    sizes[j] = max(0,sizes[i]+delta)
                else:
                    sizes[j] = max(0,sizes[j]-int(delta/(n-1)))
            splitter.setSizes(sizes)
    #@+node:ekr.20140226074510.4216: *3* activate (creates idle-time hook)
    def activate (self):
        
        pc = self
        
        if pc.active: return
        
        pc.inited = True
        pc.active = True
        
        g.registerHandler('select2',pc.update)
        g.registerHandler('idle',pc.update)
        
        # Enable the idle-time hook if it has not already been enabled.
        if not g.app.idleTimeHook:
            g.enableIdleTimeHook(idleTimeDelay=1000)
    #@+node:ekr.20140226074510.4217: *3* deactivate
    def deactivate (self):
        
        pc = self
        
        # Never disable the idle-time hook: other plugins may need it.
        g.unregisterHandler('select2',pc.update)
        g.unregisterHandler('idle',pc.update)
        pc.active = False
    #@+node:ekr.20140226074510.4218: *3* lock/unlock
    def lock (self):
        g.note('rendering pane locked')
        self.locked = True
        
    def unlock (self):
        g.note('rendering pane unlocked')
        self.locked = False
    #@+node:ekr.20140226074510.4219: *3* underline
    def underline (self,s):
        
        ch = '#'
        n = max(4,len(g.toEncodedString(s,reportErrors=False)))
        # return '%s\n%s\n%s\n\n' % (ch*n,s,ch*n)
        return '%s\n%s\n\n' % (s,ch*n)
    #@+node:ekr.20140226074510.4220: *3* update & helpers
    # Must have this signature: called by leoPlugins.callTagHandler.

    def update(self,tag,keywords):
        trace = False and not g.unitTesting
        pc = self
        c,p = pc.c,pc.c.p
        
        if pc.must_update(keywords):

            # Suppress updates until we change nodes.
            pc.node_changed = pc.gnx != p.v.gnx
            pc.gnx = p.v.gnx
            pc.length = len(p.b) # not s
        
            # Remove Leo directives.
            s = keywords.get('s') if 's' in keywords else p.b
            s = pc.remove_directives(s)
            # Dispatch based on the computed kind.
            kind = pc.get_kind(p)
            f = pc.dispatch_dict.get(kind)
            if f:
                if trace: g.trace(f.__name__)
            else:
                g.trace('no handler for kind: %s' % kind)
                f = pc.update_rst
            f(s,keywords)
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
    #@+node:ekr.20140226074510.4221: *4* embed_widget & helper
    def embed_widget (self,w,delete_callback=None):
        
        '''Embed widget w in the free_layout splitter.'''
        
        pc = self ; c = pc.c #X ; splitter = pc.splitter
        
        pc.w = w
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeItem(layout.itemAt(0))
        self.layout().addWidget(w)
        w.show()

        # Special inits for text widgets...
        if w.__class__ == pc.text_class:
            text_name = 'body-text-renderer'
            # pc.w = w = widget_class()
            w.setObjectName(text_name)
            pc.setBackgroundColor(pc.background_color,text_name,w)
            w.setReadOnly(True)
            
            # Create the standard Leo bindings.
            wrapper_name = 'rendering-pane-wrapper'
            wrapper = qtGui.leoQTextEditWidget(w,wrapper_name,c)
            w.leo_wrapper = wrapper
            c.k.completeAllBindingsForWidget(wrapper)
            w.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
              
        return
    #@+node:ekr.20140226074510.4222: *5* setBackgroundColor
    def setBackgroundColor (self,colorName,name,w):
        
        pc = self
        
        if not colorName: return

        styleSheet = 'QTextEdit#%s { background-color: %s; }' % (name,colorName)
            
        # g.trace(name,colorName)

        if QtGui.QColor(colorName).isValid():
            w.setStyleSheet(styleSheet)

        elif colorName not in pc.badColors:
            pc.badColors.append(colorName)
            g.warning('invalid body background color: %s' % (colorName))
    #@+node:ekr.20140226074510.4223: *4* must_update
    def must_update (self,keywords):
        
        '''Return True if we must update the rendering pane.'''
        
        trace = False and not g.unitTesting
        pc = self
        c,p = pc.c,pc.c.p
        if g.unitTesting:
            return False
        if keywords.get('force'):
            pc.active = True
            if trace: g.trace('force: activating')
            return True
        if c != keywords.get('c') or not pc.active:
            if trace: g.trace('not active')
            return False
        if pc.locked:
            if trace: g.trace('locked')
            return False
        if pc.gnx != p.v.gnx:
            if trace: g.trace('changed node')
            return True
        if len(p.b) != pc.length:
            if trace: g.trace('text changed')
            return True
        # This will be called at idle time.
        # if trace: g.trace('no change')
        return False
    #@+node:ekr.20140226074510.4224: *4* update_graphics_script
    def update_graphics_script (self,s,keywords):
        
        pc = self ; c = pc.c
        
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
            pc.gs = QtGui.QGraphicsScene(splitter)
            pc.gv = QtGui.QGraphicsView(pc.gs)
            w = pc.gv.viewport() # A QWidget
            
            # Embed the widgets.
            def delete_callback():
                for w in (pc.gs,pc.gv):
                    w.deleteLater()
                pc.gs = pc.gv = None

            pc.embed_widget(w,delete_callback=delete_callback)

        c.executeScript(
            script=s,
            namespace={'gs':pc.gs,'gv':pc.gv})
    #@+node:ekr.20140226074510.4225: *4* update_html
    def update_html (self,s,keywords):
        
        pc = self
        
        if pc.must_change_widget(pc.html_class):
            w = pc.html_class()
            pc.embed_widget(w)
            assert (w == pc.w)
        else:
            w = pc.w
        pc.show()
        w.setHtml(s)
        #print 'Debug printing: before w.load(...leo.html)'
        #w.load('file:///M:/leo/info/leo.html')
    #@+node:ekr.20140226074510.4226: *4* update_image
    def update_image (self,s,keywords):
        
        pc = self
        
        w = pc.ensure_text_widget()
        ok,path = pc.get_fn(s,'@image')
        if not ok:
            w.setPlainText('@image: file not found:\n%s' % (path))
            return
            
        path = path.replace('\\','/')
            
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
        template = g.adjustTripleString(template,pc.c.tab_width).strip() # Sensitive to leading blank lines.
        # template = g.toUnicode(template)
        pc.show()
        w.setReadOnly(False)
        w.setHtml(template)
        w.setReadOnly(True)
        
    #@+node:ekr.20140226074510.4227: *4* update_md
    def update_md (self,s,keywords):
        
        trace = False and not g.unitTesting
        pc = self ; c = pc.c ;  p = c.p
        s = s.strip().strip('"""').strip("'''").strip()
        isHtml = s.startswith('<') and not s.startswith('<<')
        if trace: g.trace('isHtml',isHtml)
        
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
            path = g.scanAllAtPathDirectives(c,p) or c.getNodePath(p)
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
                s = g.toUnicode(s) # 2011/03/15
                #show = True
            except SystemMessage as sm:
                # g.trace(sm,sm.args)
                msg = sm.args[0]
                if 'SEVERE' in msg or 'FATAL' in msg:
                    s = 'MD error:\n%s\n\n%s' % (msg,s)

        sb = w.verticalScrollBar()
        if sb:
            d = pc.scrollbar_pos_dict
            if pc.node_changed:
                # Set the scrollbar.
                pos = d.get(p.v,sb.sliderPosition())
                sb.setSliderPosition(pos)
            else:
                # Save the scrollbars
                d[p.v] = pos = sb.sliderPosition()
        if pc.default_kind in ('big','rst','html', 'md'):
            w.setHtml(s)
            if pc.default_kind == 'big':
                w.zoomIn(4) # Doesn't work.
        else:
            w.setPlainText(s) 
        if sb and pos:
            # Restore the scrollbars
            sb.setSliderPosition(pos)
    #@+node:ekr.20140226074510.4228: *4* update_movie
    def update_movie (self,s,keywords):
        
        # pylint: disable=E1103
        # E1103:update_movie: Module 'PyQt4.phonon' has no 'VideoPlayer' member
        # E1103:update_movie: Module 'PyQt4.phonon' has no 'VideoCategory' member
        # E1103:update_movie: Module 'PyQt4.phonon' has no 'MediaSource' member

        pc = self
        
        ok,path = pc.get_fn(s,'@movie')
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

        pc.embed_widget(vp,delete_callback=delete_callback)

        pc.show()
        vp = pc.vp
        vp.load(phonon.MediaSource(path))
        vp.play()
    #@+node:ekr.20140226074510.4229: *4* update_networkx
    def update_networkx (self,s,keywords):
        
        pc = self
        w = pc.ensure_text_widget()
        w.setPlainText('') # 'Networkx: len: %s' % (len(s)))
        pc.show()
    #@+node:ekr.20140226074510.4230: *4* update_rst
    def update_rst (self,s,keywords):
        # Do this regardless of whether we show the widget or not.
        #w = pc.ensure_text_widget()
        # PMM - test forcing qwebview in
        pc = self ; #c = pc.c
        if pc.must_change_widget(pc.html_class):
            w = pc.html_class(pc)
            pc.embed_widget(w)
            assert (w == pc.w)
        else:
            w = pc.w
        #assert pc.w
        #if s:
        #    pc.show()
        w.render_rst(s, keywords)
        #        if sb and pos:
        #            # Restore the scrollbars
        #            sb.setSliderPosition(pos)
    #@+node:ekr.20140226074510.4231: *4* update_svg
    # http://doc.trolltech.com/4.4/qtsvg.html 
    # http://doc.trolltech.com/4.4/painting-svgviewer.html

    def update_svg (self,s,keywords):

        pc = self
        
        if pc.must_change_widget(pc.svg_class):
            w = pc.svg_class()
            pc.embed_widget(w)
            assert (w == pc.w)
        else:
            w = pc.w
        if s.strip().startswith('<'):
            # Assume it is the svg (xml) source.
            s = g.adjustTripleString(s,pc.c.tab_width).strip() # Sensitive to leading blank lines.
            s = g.toEncodedString(s)
            pc.show()
            w.load(QtCore.QByteArray(s))
            w.show()
        else:
            # Get a filename from the headline or body text.
            ok,path = pc.get_fn(s,'@svg')
            if ok:
                pc.show()
                w.load(path)
                w.show()
    #@+node:ekr.20140226074510.4232: *4* update_url
    def update_url (self,s,keywords):
        
        pc = self
        
        w = pc.ensure_text_widget()
        pc.show()
        
        if 1:
            w.setPlainText('')
        else:
            url = pc.get_url(s,'@url')
            
            if url:
                w.setPlainText('@url %s' % url)
            else:
                w.setPlainText('@url: no url given')
            
        # w.setReadOnly(False)
        # w.setHtml(s)
        # w.setReadOnly(True)
    #@+node:ekr.20140226074510.4233: *4* utils for update helpers...
    #@+node:ekr.20140226074510.4234: *5* ensure_text_widget
    def ensure_text_widget (self):
        
        '''Swap a text widget into the rendering pane if necessary.'''
        
        pc = self
        if pc.must_change_widget(pc.text_class):
            w = pc.text_class()
            
            def mouseReleaseHelper(w,event):
                if QtCore.Qt.ControlModifier & event.modifiers():
                    event2 = {'c':self.c,'w':w.leo_wrapper}
                    g.openUrlOnClick(event2)
                else:
                    QtGui.QTextBrowser.mouseReleaseEvent(w,event)
            
            # Monkey patch a click handler.
            # 2012/04/10: Use the same pattern for mouseReleaseEvents
            # that is used in Leo's core:
            def mouseReleaseEvent(*args,**keys):
                if len(args) == 1:
                    event = args[0]
                elif len(args) == 2:
                    event = args[1]
                else:
                    g.trace('can not happen',args)
                    return
                mouseReleaseHelper(w,event)
            
            w.mouseReleaseEvent = mouseReleaseEvent
            pc.embed_widget(w) # Creates w.wrapper
            assert (w == pc.w)
            return pc.w
        else:
            return pc.w
    #@+node:ekr.20140226074510.4235: *5* get_kind
    def get_kind(self,p):
        
        '''Return the proper rendering kind for node p.'''
        
        pc = self ; h = p.h

        if h.startswith('@'):
            i = g.skip_id(h,1,chars='-')
            word = h[1:i].lower().strip()
            if word in pc.dispatch_dict:
                return word
                
        # To do: look at ancestors, or uA's.

        return pc.default_kind # The default.
    #@+node:ekr.20140226074510.4236: *5* get_fn
    def get_fn (self,s,tag):
        
        pc = self
        c = pc.c
        fn = s or c.p.h[len(tag):]
        fn = fn.strip()
        
        # Similar to code in g.computeFileUrl
        if fn.startswith('~'):
            # Expand '~' and handle Leo expressions.
            fn = fn[1:]
            fn = g.os_path_expanduser(fn)
            fn = g.os_path_expandExpression(fn,c=c)
            fn = g.os_path_finalize(fn)
        else:
            # Handle Leo expressions.
            fn = g.os_path_expandExpression(fn,c=c)
            # Handle ancestor @path directives.
            if c and c.openDirectory:
                base = c.getNodePath(c.p)
                fn = g.os_path_finalize_join(c.openDirectory,base,fn)
            else:
                fn = g.os_path_finalize(fn)

        ok = g.os_path_exists(fn)
        return ok,fn
    #@+node:ekr.20140226074510.4237: *5* get_url
    def get_url (self,s,tag):
        
        p = self.c.p
        url = s or p.h[len(tag):]
        url = url.strip()
        return url
    #@+node:ekr.20140226074510.4238: *5* must_change_widget
    def must_change_widget (self,widget_class):
        
        pc = self
        return not pc.w or pc.w.__class__ != widget_class
    #@+node:ekr.20140226074510.4239: *5* remove_directives
    def remove_directives (self,s):
        
        lines = g.splitLines(s)
        result = []
        for s in lines:
            if s.startswith('@'):
                i = g.skip_id(s,1)
                word = s[1:i]
                if word in g.globalDirectiveList:
                    continue
            result.append(s)
        
        return ''.join(result)
    #@-others
#@-others
#@-leo

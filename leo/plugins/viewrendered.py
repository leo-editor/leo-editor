#@+leo-ver=5-thin
#@+node:tbrown.20100318101414.5990: * @file viewrendered.py
#@+<< docstring >>
#@+node:tbrown.20100318101414.5991: ** << docstring >>
'''

Creates a window for *live* rendering of images, movies, sounds, rst, html, etc.

Dependencies
============

This plugin uses docutils,http://docutils.sourceforge.net/, to render reStructuredText,
so installing docutils is highly recommended when using this plugin.

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

Special Renderings
===================

This plugin renders @image, @html, @movie, @networkx, @svg and @url nodes in special ways.

For @image, @movie and @svg nodes, either the headline or the first line of body text may
contain a filename.  If relative, the filename is resolved relative to Leo's load directory.

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

- ``@url`` is non-functional at present.

Settings
========

- ``@color rendering-pane-background-color = white``
  The background color the rendering pane when rendering text.

- ``@bool view-rendered-auto-create = False``
  When True, show the rendering pane when Leo opens an outline.
  
- ``@bool view-rendered-auto-hide = False``
  When True, hide the rendering pane for text-only renderings.

- ``@string view-rendered-default-kind = rst``
  The default kind of rendering.  One of (big,rst,html)

- ``@bool scrolledmessage_use_viewrendered = True``
  When True the scrolledmessage dialog will use the rendering pane,
  creating it as needed.  In particular, the plugins_menu plugin
  will show plugin docstrings in the rendering pane.
  
Acknowledgments
================

Terry Brown created this initial version of this plugin,
and the free_layout and NestedSplitter plugins used by viewrendered.

Edward K. Ream generalized this plugin and added communication
and coordination between the free_layout, NestedSplitter and viewrendered plugins.

'''
#@-<< docstring >>

__version__ = '1.0'

#@+<< imports >>
#@+node:tbrown.20100318101414.5993: ** << imports >>
import leo.core.leoGlobals as g
import leo.plugins.qtGui as qtGui

g.assertUi('qt')

import sys
import os
import webbrowser

try:
    from docutils.core import publish_string
    from docutils.utils import SystemMessage
    got_docutils = True
except ImportError:
    got_docutils = False
    
try:
    import PyQt4.phonon as phonon
    phonon = phonon.Phonon
except ImportError:
    phonon = None

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import PyQt4.QtSvg as QtSvg
#@-<< imports >>

#@+<< define stylesheet >>
#@+node:ekr.20110317024548.14377: ** << define stylesheet >>
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
# 
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
#@+node:ekr.20110320120020.14491: ** Top-level
#@+node:tbrown.20100318101414.5994: *3* decorate_window
def decorate_window(w):
    
    w.setStyleSheet(stickynote_stylesheet)
    w.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
    w.resize(600, 300)
#@+node:tbrown.20100318101414.5995: *3* init
def init():
    
    g.plugin_signon(__name__)

    g.registerHandler('after-create-leo-frame', onCreate)
    
    g.registerHandler('scrolledMessage', show_scrolled_message)

    return True
#@+node:ekr.20110317024548.14376: *3* onCreate
def onCreate(tag, keys):
    
    c = keys.get('c')
    if c:
        ViewRenderedProvider(c)
    
    return
#@+node:tbrown.20110629132207.8984: *3* show_scrolled_message
def show_scrolled_message(tag, kw):

    c = kw.get('c')
    
    vr = c.frame.top.findChild(QtGui.QWidget, 'vr_scrolled_message')
    if vr is None:
        vr = ViewRenderedController(c)
        vr.setObjectName('vr_scrolled_message')
        if hasattr(c, 'free_layout'):
            splitter = c.free_layout.get_top_splitter()
            if not splitter.add_adjacent(vr, 'bodyFrame', 'right-of'):
                splitter.insert(0, vr)
        else:
            vr.resize(600, 600)
            vr.show()
    
    title = kw.get('short_title','').strip()
    vr.setWindowTitle(title)
    s = [
        title,
        '=' * len(title),
        '',
        kw.get('msg')
    ]
    s = '\n'.join(s)

    vr.update_rst(s, kw)
    vr.locked = True
    vr.active = False
    
    return True
#@+node:ekr.20110320120020.14490: ** Commands
#@+node:ekr.20110917103917.3639: *3* g.command('close-rendering-pane')
@g.command('close-rendering-pane')
def close_rendering_pane(event):
    
    '''Close the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if vr:
            vr.deactivate()
            vr.deleteLater()
#@+node:ekr.20110321085459.14462: *3* g.command('hide-rendering-pane')
@g.command('hide-rendering-pane')
def hide_rendering_pane(event):
    
    '''A synonym for 'close-rendering-pane.'''
    
    close_rendering_pane(event)
#@+node:ekr.20110321072702.14507: *3* g.command('lock-unlock-rendering-pane')
@g.command('lock-unlock-rendering-pane')
def lock_unlock_rendering_pane(event):
    
    '''Pause or play a movie in the rendering pane.'''

    c = event.get('c')
    if c:
        
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if not vr:
            g.es('Open a viewrendered pane first')
        else:
            if vr.locked:
                vr.unlock()
            else:
                vr.lock()
#@+node:ekr.20110320233639.5777: *3* g.command('pause-play-movie')
@g.command('pause-play-movie')
def pause_play_movie(event):
    
    '''Pause or play a movie in the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if not vr:
            g.es('Open a viewrendered pane first')
        else:
            if vr and vr.vp:
                vp = vr.vp
                if vp.isPlaying():
                    vp.pause()
                else:
                    vp.play()
#@+node:ekr.20110917103917.3637: *3* g.command('show-rendering-pane')
@g.command('show-rendering-pane')
def show_rendering_pane (event):
    
    '''A synonym for viewrendered.'''
    
    viewrendered(event)
#@+node:ekr.20110317080650.14386: *3* g.command('toggle-rendering-pane')
@g.command('toggle-rendering-pane')
def toggle_rendering_pane(event):
    
    '''Show or hide the rendering pane.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if vr:
            hide_rendering_pane(event)
        else:
            viewrendered(event)
#@+node:ekr.20110321151523.14464: *3* g.command('update-rendering-pane')
@g.command('update-rendering-pane')
def update_rendering_pane (event):
    
    '''Hide the rendering pane, but do not delete it.'''

    c = event.get('c')
    if c:
        vr = c.frame.top.findChild(QtGui.QWidget, 'viewrendered_pane')
        if not vr:
            g.es('Open a viewrendered pane first')
        else:
            vr.update(tag='view',keywords={'c':c,'force':True})
#@+node:tbrown.20100318101414.5998: *3* g.command('viewrendered')
@g.command('viewrendered')
def viewrendered(event):
    """Open render view for commander"""

    c = event.get('c')
    if c:
        
        vr = ViewRenderedController(c)
        
        if hasattr(c, 'free_layout'):
            
            vr._ns_id = '_leo_viewrendered'  # for free_layout load/save
            
            splitter = c.free_layout.get_top_splitter()
            if not splitter.add_adjacent(vr, 'bodyFrame', 'right-of'):
                splitter.insert(0, vr)
        else:
            vr.setWindowTitle("Rendered View")
            vr.resize(600, 600)
            vr.show()
#@+node:ekr.20110320120020.14475: *3* g.command('vr')
@g.command('vr')
def viewrendered_alias(event):
    """A synonynm for the viewrendered command"""

    viewrendered(event)
#@+node:tbrown.20110629084915.35149: ** class ViewRenderedProvider
class ViewRenderedProvider:
    #@+others
    #@+node:tbrown.20110629084915.35154: *3* __init__
    def __init__(self, c):
        self.c = c
        if hasattr(c, 'free_layout'):
            c.free_layout.get_top_splitter().register_provider(self)
    #@+node:tbrown.20110629084915.35150: *3* ns_provides
    def ns_provides(self):
        return[('Viewrendered', '_leo_viewrendered')]
    #@+node:tbrown.20110629084915.35151: *3* ns_provide
    def ns_provide(self, id_):
        if id_ == '_leo_viewrendered':
            return ViewRenderedController(self.c)
    #@-others
#@+node:ekr.20110317024548.14375: ** class ViewRenderedController
class ViewRenderedController(QtGui.QWidget):
    
    '''A class to control rendering in a rendering pane.'''
    
    #@+others
    #@+node:ekr.20110317080650.14380: *3* ctor & helpers
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
        self.kind = 'rst' # in self.dispatch_dict.keys()
        self.length = 0 # The length of previous p.b.
        self.locked = False
        self.s = '' # The plugin's docstring to be rendered temporarily.
        self.scrollbar_pos_dict = {} # Keys are vnodes, values are positions.
        self.sizes = [] # Saved splitter sizes.
        self.splitter_index = None # The index of the rendering pane in the splitter.
        self.svg_class = QtSvg.QSvgWidget
        self.text_class = QtGui.QTextEdit
        self.graphics_class = QtGui.QGraphicsWidget
        self.vp = None # The present video player.
        self.w = None # The present widget in the rendering pane.
        self.title = None
        # User-options:
        self.default_kind = c.config.getString('view-rendered-default-kind') or 'rst'
        self.auto_create  = c.config.getBool('view-rendered-auto-create',False)
        self.auto_hide    = c.config.getBool('view-rendered-auto-hide',False)
        self.background_color = c.config.getColor('rendering-pane-background-color') or 'white'
        self.scrolled_message_use_viewrendered = c.config.getBool('scrolledmessage_use_viewrendered',True)
        self.node_changed = True
        
        # Init.
        self.create_dispatch_dict()
        self.activate()
    #@+node:ekr.20110320120020.14478: *4* create_dispatch_dict
    def create_dispatch_dict (self):
        
        pc = self
        
        pc.dispatch_dict = {
            'big':          pc.update_rst,
            'html':         pc.update_html,
            'graphics-script':  pc.update_graphics_script,
            'image':        pc.update_image,
            'movie':        pc.update_movie,
            'networkx':     pc.update_networkx,
            'rst':          pc.update_rst,
            'svg':          pc.update_svg,
            'url':          pc.update_url,
        }
    #@+node:tbrown.20110621120042.22676: *3* closeEvent
    def closeEvent(self, event):
        
        self.deactivate()

    #@+node:ekr.20110317080650.14381: *3* activate
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
    #@+node:ekr.20110317080650.14382: *3* deactivate
    def deactivate (self):
        
        pc = self
        
        # Never disable the idle-time hook: other plugins may need it.
        g.unregisterHandler('select2',pc.update)
        g.unregisterHandler('idle',pc.update)
        
        pc.active = False
    #@+node:ekr.20110321072702.14508: *3* lock/unlock
    def lock (self):
        g.note('rendering pane locked')
        self.locked = True
        
    def unlock (self):
        g.note('rendering pane unlocked')
        self.locked = False
    #@+node:ekr.20110319143920.14466: *3* underline
    def underline (self,s):
        
        ch = '#'
        n = max(4,len(g.toEncodedString(s,reportErrors=False)))
        # return '%s\n%s\n%s\n\n' % (ch*n,s,ch*n)
        return '%s\n%s\n\n' % (s,ch*n)
    #@+node:ekr.20101112195628.5426: *3* update & helpers
    def update(self,tag,keywords):
        
        trace = False and not g.unitTesting
        pc = self ; c = pc.c ; p = c.p ; w = pc.w
        force = keywords.get('force')
        s, val = pc.must_update(keywords)
        
        if not force and not val:
            # Save the scroll position.
            if w.__class__ == pc.text_class:
                # 2011/07/30: The widge may no longer exist.
                try:
                    sb = w.verticalScrollBar()
                except Exception:
                    g.es_exception()
                    self.deactivate()
                if sb:
                    pc.scrollbar_pos_dict[p.v] = sb.sliderPosition()
            # g.trace('no update')
            return
            
        # Suppress updates until we change nodes.
        pc.node_changed = pc.gnx != p.v.gnx
        pc.gnx = p.v.gnx
        pc.length = len(p.b) # Use p.b, not s.

        if pc.s:
            if trace: g.trace('docstring',len(pc.s))
            # A plugin docstring.
            s = pc.s
            pc.s = None
            keywords['force']=True
            pc.update_rst(s,keywords)
        else:
            # Remove Leo directives.
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
    #@+node:ekr.20110320120020.14486: *4* embed_widget & helper
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
            c.k.completeAllBindingsForWidget(wrapper)
            w.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
              
        return
    #@+node:ekr.20110321072702.14510: *5* setBackgroundColor
    def setBackgroundColor (self,colorName,name,w):
        
        pc = self
        
        if not colorName: return

        styleSheet = 'QTextEdit#%s { background-color: %s; }' % (name,colorName)
            
        # g.trace(name,colorName)

        if QtGui.QColor(colorName).isValid():
            w.setStyleSheet(styleSheet)

        elif colorName not in pc.badColors:
            pc.badColors.append(colorName)
            g.es_print('invalid body background color: %s' % (colorName),color='blue')
    #@+node:ekr.20110320120020.14476: *4* must_update
    def must_update (self,keywords):
        
        '''Return True if we must update the rendering pane.'''
        
        trace = False and not g.unitTesting
        verbose = False
        pc = self ; c = pc.c ; p = c.p
        
        if (c != keywords.get('c') or 
            not pc.active or
            (pc.locked and not keywords.get('force')) or
            g.unitTesting):
            if trace: g.trace('not active')
            return None,False
        
        if pc.s:
            s = pc.s
            if trace: g.trace('self.s exists',len(s))
            return s,True
        else:
            s = p.b
            val = pc.gnx != p.v.gnx
            if val:
                if trace: g.trace('changed node')
                return s,val
            val = len(s) != pc.length
            if val:
                if trace: g.trace('text changed')
            return s,val

            # try:
                # # Can fail if the window has been deleted.
                # w.setWindowTitle(p.h)
            # except exception:
                # pc.splitter = None
                # return
    #@+node:ekr.20110321151523.14463: *4* update_graphics_script
    def update_graphics_script (self,s,keywords):
        
        pc = self ; c = pc.c
        
        force = keywords.get('force')
        
        if pc.gs and not force: return

        if not pc.gs:
            # Create the widgets.
            pc.gs = QtGui.QGraphicsScene(pc.splitter)
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
    #@+node:ekr.20110321005148.14534: *4* update_html
    def update_html (self,s,keywords):
        
        pc = self
        
        pc.show()
        w = pc.ensure_text_widget()
        w.setReadOnly(False)
        w.setHtml(s)
        w.setReadOnly(True)
    #@+node:ekr.20110320120020.14482: *4* update_image
    def update_image (self,s,keywords):
        
        pc = self
        
        w = pc.ensure_text_widget()
        ok,path = pc.get_fn(s,'@image')
        if not ok:
            w.setPlainText('@image: file not found:\n%s' % (path))
            return
            
        template = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head></head>
    <body bgcolor="#fffbdc">
    <img src="%s">
    </body>
    </html>
    ''' % (path)

        pc.show()
        w.setReadOnly(False)
        w.setHtml(template)
        w.setReadOnly(True)
        
    #@+node:ekr.20110320120020.14481: *4* update_movie
    def update_movie (self,s,keywords):
        
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
            
        if not pc.vp:
            # Create the widgets.
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
    #@+node:ekr.20110320120020.14484: *4* update_networkx
    def update_networkx (self,s,keywords):
        
        pc = self
        w = pc.ensure_text_widget()
        w.setPlainText('') # 'Networkx: len: %s' % (len(s)))
        pc.show()
    #@+node:ekr.20110320120020.14477: *4* update_rst
    def update_rst (self,s,keywords):
        
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
        else:
            if pc.auto_hide:
                pass  # needs review
                # pc.hide()
            return
        
        if got_docutils and not isHtml:
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
                s = publish_string(s,writer_name='html')
                s = g.toUnicode(s) # 2011/03/15
                show = True
            except SystemMessage as sm:
                # g.trace(sm,sm.args)
                msg = sm.args[0]
                if 'SEVERE' in msg or 'FATAL' in msg:
                    s = 'RST error:\n%s\n\n%s' % (msg,s)

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

        if pc.kind in ('big','rst','html'):
            w.setHtml(s)
            if pc.kind == 'big':
                w.zoomIn(4) # Doesn't work.
        else:
            w.setPlainText(s)
            
        if sb and pos:
            # Restore the scrollbars
            sb.setSliderPosition(pos)
    #@+node:ekr.20110320120020.14479: *4* update_svg
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
            w.load(s)
            w.show()
        else:
            # Get a filename from the headline or body text.
            ok,path = pc.get_fn(s,'@svg')
            if ok:
                pc.show()
                w.load(path)
                w.show()
    #@+node:ekr.20110321005148.14537: *4* update_url
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
    #@+node:ekr.20110322031455.5765: *4* utils for update helpers...
    #@+node:ekr.20110322031455.5764: *5* ensure_text_widget
    def ensure_text_widget (self):
        
        '''Swap a text widget into the rendering pane if necessary.'''
        
        pc = self
        
        if pc.must_change_widget(pc.text_class):
            w = pc.text_class()
            pc.embed_widget(w)
            assert (w == pc.w)
            return pc.w
        else:
            return pc.w
    #@+node:ekr.20110320120020.14483: *5* get_kind
    def get_kind(self,p):
        
        '''Return the proper rendering kind for node p.'''
        
        pc = self ; h = p.h

        if h.startswith('@'):
            i = g.skip_id(h,1,chars='-')
            word = h[1:i].lower().strip()
            if word in pc.dispatch_dict:
                return word
                
        # To do: look at ancestors, or uA's.

        return pc.kind # The default.
    #@+node:ekr.20110320233639.5776: *5* get_fn
    def get_fn (self,s,tag):
        
        pc = self ; c = pc.c
        fn = s or c.p.h[len(tag):]
        fn = fn.strip()
        # path = g.os_path_finalize_join(g.app.loadDir,fn)
        fn = fn.replace('\\','/')
        parts = fn.split('/')
        args = [g.app.loadDir]
        args.extend(parts)
        path = g.os_path_finalize_join(*args,c=c)
        ok = g.os_path_exists(path)
        return ok,path
    #@+node:ekr.20110321005148.14536: *5* get_url
    def get_url (self,s,tag):
        
        p = self.c.p
        url = s or p.h[len(tag):]
        url = url.strip()
        return url
    #@+node:ekr.20110322031455.5763: *5* must_change_widget
    def must_change_widget (self,widget_class):
        
        pc = self
        return not pc.w or pc.w.__class__ != widget_class
    #@+node:ekr.20110320120020.14485: *5* remove_directives
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

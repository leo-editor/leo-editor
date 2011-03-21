#@+leo-ver=5-thin
#@+node:tbrown.20100318101414.5990: * @file viewrendered.py
#@+<< docstring >>
#@+node:tbrown.20100318101414.5991: ** << docstring >>
''' Creates a window for *live* rendering of rst, html, etc.  (Qt only).

**Commands**

viewrendered.py creates the following (``Alt-X``) commands:

``viewrendered``
    opens a new window where the current body text is rendered as HTML
    (if it starts with '<'), or otherwise reStructuredText.
``viewrendered-big``
    as above, but zoomed in, useful for presentations
``viewrendered-html``
    displays the html source generated from reStructuredText, useful for
    debugging

``viewrendered`` sets the process current directory (os.chdir()) to the path
to the node being rendered, to allow relative paths to work in
``.. image::`` directives.

reStructuredText errors and warnings may be shown.  For example, both::

    Heading
    -------

    `This` is **really** a line of text.

and::

    <h1>Heading<h1>

    <tt>This</tt> is <b>really</b> a line of text.

will look something like:

    **Heading**

    `This` is **really** a line of text.

**Settings**

- \@string view-rendered-default-kind = rst
  
  The default kind of rendering.  One of (big,rst,html)
    
- \@bool view-rendered-auto-create = False
  
  When True, the plugin will create a rendering pane automatically.

'''
#@-<< docstring >>

__version__ = '0.1'

#@+<< imports >>
#@+node:tbrown.20100318101414.5993: ** << imports >>
import leo.core.leoGlobals as g

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
# - Allow URL's and file names in body text of @svg, etc.
# - @color viewrendered-pane-color.
# - Generalize: allow registration of other kinds of renderers.
#   In particular, allow different kinds of widgets in the viewrendered pane.
# - Support uA's that indicate the kind of rendering desired.
# 
# Fix bugs:
# 
# - Save/restore viewrendered pane size.
# - Eliminate the call to c.frame.equalSizedPanes in create_renderer (in free_layout).
#   That is, be able to specify the pane ratios from user options.
# - (Failed) Make viewrendered-big work.
# 
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
def init ():
    
    # g.trace('viewrendered.py')
    
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame',onCreate)

    return True
#@+node:ekr.20110317024548.14376: *3* onCreate
def onCreate (tag, keys):
    
    global controllers
    
    c = keys.get('c')
    if c:
        h = c.hash()
        if not controllers.get(h):
            controllers[h] = ViewRenderedController(c)
#@+node:ekr.20110320120020.14490: ** Commands
#@+node:tbrown.20100318101414.5998: *3* g.command('viewrendered')
@g.command('viewrendered')
def viewrendered(event):
    """Open render view for commander"""

    c = event.get('c')
    if c:
        pc = controllers.get(c.hash())
        if pc: pc.view('rst')
#@+node:ekr.20110320120020.14475: *3* g.command('vr')
@g.command('vr')
def viewrendered(event):
    """A synonynm for the viewrendered command"""

    c = event.get('c')
    if c:
        pc = controllers.get(c.hash())
        if pc: pc.view('rst')
#@+node:tbrown.20101127112443.14856: *3* g.command('viewrendered-html') (not used)
# @g.command('viewrendered-html')
# def viewrendered(event):
    # """Open view of html which would be rendered"""

    # c = event.get('c')
    # if c:
        # pc = controllers.get(c.hash())
        # if pc: pc.view('html')
#@+node:tbrown.20101127112443.14854: *3* g.command('viewrendered-big') (not used)
# @g.command('viewrendered-big')
# def viewrendered(event):
    # """Open render view for commander, with big text

    # (useful for presentations)

    # """

    # c = event.get('c')
    # if c:
        # pc = controllers.get(c.hash())
        # if pc:
            # w = pc.w
            # pc.view('big')
            # w.zoomIn(4)
#@+node:ekr.20110317080650.14383: *3* g.command('hide-rendering-pane')
@g.command('hide-rendering-pane')
def hide_rendering_pane(event):
    
    '''Hide the rendering pane, but do not delete it.'''

    c = event.get('c')
    if c:
        pc = controllers.get(c.hash())
        if pc: pc.hide()
#@+node:ekr.20110317080650.14386: *3* g.command('show-rendering-pane')
@g.command('show-rendering-pane')
def show_rendering_pane(event):
    
    '''Hide the rendering pane, but do not delete it.'''

    c = event.get('c')
    if c:
        pc = controllers.get(c.hash())
        if pc:
            pc.length = -1
            pc.s = None
            pc.gnx = 0
            pc.view('rst')
#@+node:ekr.20110317024548.14375: ** class ViewRenderedController
class ViewRenderedController:
    
    '''A class to control rendering in a rendering pane.'''
    
    #@+others
    #@+node:ekr.20110317080650.14380: *3* ctor & helpers
    def __init__ (self,c):
            
        self.active = False
        self.c = c
        self.delete_callback = None
        self.gnx = None
        self.inited = False
        self.free_layout_pc = None # Set later by embed.
        self.kind = 'rst' # in self.dispatch_dict.keys()
        self.length = 0 # The length of previous p.b.
        self.s = ''
        self.splitter = None # The free_layout splitter containing the rendering pane.
        self.splitter_index = None # The index of the rendering pane in the splitter.
        self.svg_class = QtSvg.QSvgWidget
        self.text_class = QtGui.QTextEdit
        self.vp = None # The present video player.
        self.w = None # w = QtGui.QTextEdit() # QtGui.QTextBrowser()
        
        # User-options:
        self.default_kind = c.config.getString('view-rendered-default-kind') or 'rst'
        self.auto_create  = c.config.getBool('view-rendered-auto-create',False)
        self.scrolled_message_use_viewrendered = c.config.getBool('scrolledmessage_use_viewrendered',True)
        
        # Init.
        c.viewrendered = self # For free_layout
        # w.setReadOnly(True)
        self.create_dispatch_dict()
        self.load_free_layout()

        if self.auto_create:
            self.view(self.default_kind)
    #@+node:ekr.20110320120020.14478: *4* create_dispatch_dict
    def create_dispatch_dict (self):
        
        pc = self
        
        pc.dispatch_dict = {
            'big':      pc.update_rst,
            'html':     pc.update_rst,
            'graphic':  pc.update_graphic,
            'movie':    pc.update_movie,
            'networkx': pc.update_networkx,
            'rst':      pc.update_rst,
            'svg':      pc.update_svg,
        }
    #@+node:ekr.20110319013946.14467: *4* load_free_layout
    def load_free_layout (self):
        
        c = self.c
        
        fl = hasattr(c,'free_layout') and c.free_layout

        if not fl:
            # g.trace('auto-loading free_layout.py')
            m = g.loadOnePlugin('free_layout.py',verbose=False)
            m.onCreate(tag='viewrendered',keys={'c':c})
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
    #@+node:ekr.20110318080425.14388: *3* has/set_renderer
    def has_renderer (self):
        
        '''Return True if the renderer pane is visible.'''
        
        return self.splitter

    def set_renderer (self,splitter,index):
        
        self.splitter = splitter
        self.splitter_index = index
        # g.trace(index,splitter)
    #@+node:ekr.20110317080650.14384: *3* show & hide
    def hide (self):
        
        pc = self
        pc.deactivate()
        pc.w.hide()
        
    def show (self):
        
        pc = self
        pc.activate()
        pc.update(tag='view',keywords={'c':self.c})
        pc.w.show()
    #@+node:ekr.20110319143920.14466: *3* underline
    def underline (self,s):
        
        ch = '#'
        n = max(4,len(g.toEncodedString(s,reportErrors=False)))
        # return '%s\n%s\n%s\n\n' % (ch*n,s,ch*n)
        return '%s\n%s\n\n' % (s,ch*n)
    #@+node:ekr.20101112195628.5426: *3* update & helpers
    def update(self,tag,keywords):
        
        pc = self ; c = pc.c ; p = c.p
        s, val = pc.must_update(keywords)
        if not val:
            # g.trace('no update')
            return
        
        # Suppress updates until we change nodes.  
        self.gnx = p.v.gnx
        self.length = len(p.b) # Use p.b, not s.
        
        # Remove Leo directives.
        s = pc.remove_directives(s)

        # Dispatch based on the computed kind.
        kind = self.get_kind(p)
        f = pc.dispatch_dict.get(kind)
        if not f:
            g.trace('no handler for kind: %s' % kind)
            f = self.update_rst
        f(s,keywords)
    #@+node:ekr.20110320120020.14486: *4* embed_widget
    def embed_widget (self,widget_class,callback=None,delete_callback=None):
        
        '''Embed widget w in the free_layout splitter.'''
        
        pc = self
        
        if pc.splitter:
            same_class = self.w and self.w.__class__ == widget_class
            w2 = pc.splitter.widget(pc.splitter_index)
            if not same_class:
                if self.delete_callback:
                    self.delete_callback()
                self.delete_callback = delete_callback
                if callback:
                    self.w = w = callback()
                else:
                    self.w = w = widget_class()
                # g.trace(same_class,widget_class)
                pc.splitter.replace_widget_at_index(pc.splitter_index,w)
                if widget_class == self.text_class:
                    w.setReadOnly(True)
        else:
            g.trace('no splitter')
    #@+node:ekr.20110320120020.14483: *4* get_kind
    def get_kind(self,p):
        
        '''Return the proper rendering kind for node p.'''
        
        pc = self ; h = p.h

        if h.startswith('@'):
            i = g.skip_id(h,1)
            word = h[1:i].lower().strip()
            if word in pc.dispatch_dict:
                return word
                
        # To do: look at ancestors, or uA's.

        return self.kind # The default.
    #@+node:ekr.20110320120020.14476: *4* must_update
    def must_update (self,keywords):
        
        '''Return True if we must update the rendering pane.'''
        
        pc = self ; c = pc.c ; p = c.p
        
        if c != keywords.get('c') or not pc.active:
            return None,False
        
        if self.s:
            s = self.s
            self.s = None
            return s,True
        else:
            s = p.b
            val = self.gnx != p.v.gnx or len(s) != self.length
            return s,val

            # try:
                # # Can fail if the window has been deleted.
                # w.setWindowTitle(p.h)
            # except exception:
                # self.splitter = None
                # return
    #@+node:ekr.20110320120020.14485: *4* remove_directives
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
    #@+node:ekr.20110320120020.14482: *4* update_graphic
    def update_graphic (self,s,keywords):
        
        self.embed_widget(self.text_class)

        self.w.setPlainText('Graphic\n\n%s' % (s))
        
    #@+node:ekr.20110320120020.14477: *4* update_rst
    def update_rst (self,s,keywords):
        
        pc = self ; c = pc.c ;  p = c.p
        s = s.strip().strip('"""').strip("'''").strip()

        if got_docutils and (not s.startswith('<') or s.startswith('<<')):
            path = g.scanAllAtPathDirectives(c,p) or c.getNodePath(p)
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            if os.path.isdir(path):
                os.chdir(path)

            try:
                msg = '' # The error message from docutils.
                if self.title:
                    s = self.underline(self.title) + s
                    self.title = None
                s = publish_string(s,writer_name='html')
                s = g.toUnicode(s) # 2011/03/15
            except SystemMessage as sm:
                # g.trace(sm,sm.args)
                msg = sm.args[0]
                if 'SEVERE' in msg or 'FATAL' in msg:
                    s = 'RST error:\n%s\n\n%s' % (msg,s)
                    
        self.embed_widget(self.text_class)
        w = self.w

        if self.kind in ('big','rst','html'):
            w.setHtml(s)
            if self.kind == 'big':
                w.zoomIn(4) # Doesn't work.
        else:
            w.setPlainText(s)
    #@+node:ekr.20110320120020.14479: *4* update_svg
    # http://doc.trolltech.com/4.4/qtsvg.html 
    # http://doc.trolltech.com/4.4/painting-svgviewer.html

    def update_svg (self,s,keywords):

        self.embed_widget(self.svg_class)
        w = self.w

        if 0:
            path = g.os_path_finalize_join(g.app.loadDir,'..','Icons','bubbles.svg')
            w.load(path)
        else:
            s = g.adjustTripleString(s,self.c.tab_width).strip() # Sensitive to leading blank lines.
            s = g.toEncodedString(s)
            w.load(s)

        w.show()
    #@+node:ekr.20110320120020.14481: *4* update_movie
    def update_movie (self,s,keywords):
        
        if not phonon:
            self.embed_widget(self.text_class)
            self.w.setPlainText('Movie\n\n%s' % (s))
            return
        
        pc = self ;  p = pc.c.p ; tag = '@movie'
        fn = s or p.h[len(tag):]
        fn = fn.strip()
        path = g.os_path_finalize_join(g.app.loadDir,fn)

        if not g.os_path_exists(path):
            return g.es_print('Not found: %s' % (path))
        
        def delete_callback():
            if self.vp:
                self.vp.stop()
                self.vp = None
            
        def video_callback():
            self.vp = vp = phonon.VideoPlayer(phonon.VideoCategory)
            vw = vp.videoWidget()
            return vw
            
        self.embed_widget(phonon.VideoPlayer,
            callback=video_callback,
            delete_callback=delete_callback)

        vp = self.vp
        vp.load(phonon.MediaSource(path))
        vp.play()
    #@+node:ekr.20110320120020.14484: *4* update_networkx
    def update_networkx (self,s,keywords):
        
        self.embed_widget(self.text_class)
        
        self.w.setPlainText('Networkx: len: %s' % (len(s)))
    #@+node:ekr.20110317024548.14379: *3* view & helper
    def view(self,kind,s=None,title=None):
        
        pc = self
        pc.kind = kind
        
        # g.trace(kind,len(s))
        
        self.embed_renderer()
        self.s = s
        self.title = title
        pc.show()

        # if big:
            # pc.w.zoomIn(4)
    #@+node:ekr.20110318080425.14394: *4* embed_renderer
    def embed_renderer (self):
        
        '''Use the free_layout plugin to embed self.w in a splitter.'''
        
        c = self.c
        
        if self.splitter:
            return

        pc = hasattr(c,'free_layout') and c.free_layout
        if pc:
            self.free_layout_pc = pc
            pc.create_renderer(self.w)
                # Calls set_renderer, which sets self.splitter.
    #@-others
#@-others
#@-leo

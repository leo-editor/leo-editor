#@+leo-ver=5-thin
#@+node:ekr.20100908110845.5505: * @thin screenshots.py
#@+<< docstring >>
#@+node:ekr.20100908115707.5554: ** << docstring >>
"""The screenshots.py plugin
============================

The screenshots plugin defines three commands. The
make-slide and make-slide-show commands
(collectively known as **slide commands**) create
slides and slide shows (collections of slides)
from Leo outlines. The apropos-slides command
prints this message to Leo's log pane.

Nodes
-----

A **slide node** is a node whose headline of the form::

    @slide <name of slide>

A **slideshow** is a tree of nodes whose root
node has the form::

    @slidesnow <name of slide show>

**Option nodes** allow slide-by-slide control of
slide commands. Options nodes must be direct
children of a slide node.

Files
-----


Making slides
-------------

For each slide, the make-slide and make-slide-show
commands do the following:

1. Create the **target outline**, screenshot-setup.leo.

By default, the target outline is a copy of the
Leo outline containing the slide node. If the
slide node contains an @screenshot-tree node, the
target outline consists of all the descendants of
the @scrrenshot-tree node.

2. Take a **screenshot**, a bitmap (PNG) file. The
   slide commands take a screen shot of the target
   outline.  Several option nodes apply to this step:

- If the slide node contains an option node of the
  form @select <headline> the slide commands select
  the node in the target outline whose headline
  matches <headline>.

- If the slide node contains an @pause node as one
  of its directive children, the slide commands
  open the target node, but do *not* take a screen
  shot.

  The user may adjust the screen as desired,
  for example by selecting menus or showing dialogs.
  The *user* must then take the screen shot manually.
  As soon as the user closes the target outline,
  the slide commands look for the screen shot on the
  clipboard.  If found, the slide commands save the
  screenshot to the screenshot file.

3. Add an .. image:: directive and @image node.

4. Convert the screenshot file to a **work file**,
   an SVG (Scalable Vector Graphics) file. See
   http://www.w3.org/Graphics/SVG/.

   @callout

5. (Optional) Edit the work file interactively
   with Inkscape. Inkscape, http://inkscape.org/,
   is an Open Source vector graphics editor.

   This step happens only if the slide node contains
   an @edit node as a direct child of the slide node.

6. Use Inkscape non-interactively to
   render a **final output file** (a PNG image) from the work file.
   If the Python Imaging Libary (PIL) is available,
   this step will use PIL to improve the quality
   of the final output file.

Examples
--------

The following examples show how to create screen shots.

Example 1: Fully automatic operation.

Example 2: Creating a custom screen shot.

Example 3: Editing the work file with callouts.

Prerequisites
-------------

Inkscape (Required)
  An SVG editor
  http://www.inkscape.org/

PIL (Optional but highly recommended)
  The Python Imaging Library,
  http://www.pythonware.com/products/pil/

Settings
--------

@string inkscape-bin

This setting tells Leo the location of the Inkscape executable.

Scripting reference
-------------------

The run method has the following signature::

    def run (self,fn,
        callouts=[],
        markers=[],
        png_fn=None,svg_fn=None,template_fn=None)

        fn  The name of the bitmap screenshot file.
  callouts  A possibly empty list of strings.
   markers  A possibly empty list of numbers.
    png_fn  The name of final png image file.
            No image is generated if this argument is None.
    svg_fn  The name of working svg file.
            If no name is given, ``working_file.svg`` is used.
 template_fn The name of the **template svg file**.
            This file contains images to be used for
            callouts and markers.  If no name is given,
            inkscape-template.svg is used.

For example, the following places three text
balloon callouts and three black circle
numeric markers on a screenshot::

    fn = "some_screen_shot.png"
    png_fn = "final_screen_shot.png"
    callouts = (
        "This goes here",
        "These are those, but slightly longer",
        "Then you pull this")
    markers = (2,4,17)

    c.inkscapeCommands.run(fn,
        callouts=callouts,markers=markers,
        png_fn=png_fn)

"""

#@@pagewidth 50
#@-<< docstring >>
#@+<< notes >>
#@+node:ekr.20101004082701.5741: ** << notes >>
#@@nocolor-node
#@+at
# 
# 
# * Specify global options in @slideshow node.
# - Revise docstring and apropos-screen-shots.
# 
# Done:
# - @slide is now requred
# - Rename @select to @pause
# - Rewrote path init logic.
# - Added info_command.
# - Put screenshots in same folder as the slideshow.
# - Changed the .. image: directive.
# - Called docutils to process each @slide node into an html file.
# - Create make_all_directories.
# - Copy sphinx build files from doc/html to doc/slides/slideshow-name directory.
# - Generated leo_toc.html as the first slide.
# - Generate titles for all slides.
# - Ignore @slide ande @slideshow nodes in @screenshot-tree trees.
# - Use @slideshow title as title of all slides.
# - Copy only leo_toc.html.txt to the slideshow folder.
#@-<< notes >>
__version__ = '0.1'
#@+<< imports >>
#@+node:ekr.20100908110845.5604: ** << imports >>
import leo.core.leoGlobals as g

import copy
import os

# Warnings are given later.
try:
    from PIL import Image, ImageChops
    got_pil = True
except ImportError:
    got_pil = False

try:
    import PyQt4.QtGui
    got_qt = True
except ImportError:
    got_qt = False

import shutil
import subprocess
import sys
import tempfile

import xml.etree.ElementTree as etree
#@-<< imports >>

#@+others
#@+node:ekr.20100914090933.5771: ** Top level
#@+node:ekr.20100908110845.5581: *3* g.command(apropos-slides)
@g.command('apropos-slides')
def apropos_screen_shots(event):

    # Just print the module's docstring.
    g.es(__doc__)
#@+node:ekr.20100908110845.5583: *3* g.command(make-slide)
@g.command('make-slide')
def make_slide_command (event):

    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.make_slide_command(c.p)
        g.note('take-screen-shot command finished')
#@+node:ekr.20100911044508.5634: *3* g.command(make-slide-show)
@g.command('make-slide-show')
def make_slide_show_command(event=None):

    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.make_slide_show_command(c.p)
        g.note('make-slide-show command finished')
#@+node:ekr.20101004082701.5733: *3* g.command(slide-show-info)
@g.command('slide-show-info')
def slide_show_info_command(event):

    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.slide_show_info_command(c.p)
#@+node:ekr.20100908110845.5606: *3* init
def init ():

    ok = got_qt

    if ok:
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20100914090933.5770: *3* make_screen_shot
def make_screen_shot (path):

    '''Create a screenshot of the present Leo outline and save it to path.
    This is a callback called from make_screen_shot in runLeo.py'''

    # g.trace('screenshots.py:',path)

    app = g.app.gui.qtApp
    pix = PyQt4.QtGui.QPixmap
    w = pix.grabWindow(app.activeWindow().winId())
    w.save(path,'png')
#@+node:ekr.20100908110845.5531: ** class ScreenShotController
class ScreenShotController(object):

    '''A class to take screen shots and control Inkscape.

    apropos-screenshots contains a more complete description.'''

    #@+others
    #@+node:ekr.20100908110845.5532: *3*  ctor & helpers
    def __init__(self,c):

        self.c = c

        # import flags
        try:
            from PIL import Image, ImageChops
            self.got_pil = True
        except ImportError:
            self.got_pil = False

        try:
            import PyQt4.QtGui
            self.got_qt = True
        except ImportError:
            self.got_qt = False

        # The path to the Inkscape executable.
        self.inkscape_bin = self.get_inkscape_bin()

        # Standard screenshot size
        self.default_screenshot_height = 900
        self.default_screenshot_width = 700
        self.screenshot_height = None
        self.screenshot_width = None

        # The @slideshow node.
        self.slideshow_node = None

        # Dimension cache.
        self.dimCache = {}
        self.is_reads,self.is_cache = 0,0

        # Internal constants.
        # element IDs which should exist in the SVG template
        self.ids = [
            "co_bc_1",        # 1 digit black circle
            "co_bc_2",        # 2 digit black circle
            "co_bc_text_1",   # text holder for 1 digit black circle
            "co_bc_text_2",   # text holder for 2 digit black circle
            "co_frame",       # frame for speech balloon callout
            "co_g_bc_1",      # group for 1 digit black circle
            "co_g_bc_2",      # group for 2 digit black circle
            "co_g_co",        # group for speech balloon callout
            "co_shot",        # image for screen shot
            "co_text_holder", # text holder for speech balloon callout
        ]

        self.xlink = "{http://www.w3.org/1999/xlink}"
        # self.namespace = {'svg': "http://www.w3.org/2000/svg"}

        self.verbose = False
    #@+node:ekr.20100913085058.5657: *4* get_inkscape_bin
    def get_inkscape_bin(self):

        c = self.c
        bin = c.config.getString('screenshot-bin').strip('"').strip("'")

        if bin:
            if g.os_path_exists(bin):
                self.inkscape_bin = bin
            else:
                g.warning('Invalid @string screenshot-bin:',bin)

        if not bin:
            g.warning('Inkscape not found. No editing is possible.')

        return bin
    #@+node:ekr.20101004082701.5731: *3* commands
    #@+node:ekr.20101004082701.5732: *4* sc.slide-show-info_command
    def slide_show_info_command (self,p):

        sc = self
        sc.init(p)
        table = (
            ('\npaths...',''),
            ('at_image_fn      ',sc.at_image_fn),
            ('directive_fn     ',sc.directive_fn),
            ('output_fn        ',sc.output_fn),
            ('screenshot_fn    ',sc.screenshot_fn),
            ('sphinx_path      ',sc.sphinx_path),
            ('slide_fn         ',sc.slide_fn),
            ('slideshow_path   ',sc.slideshow_path),
            ('template_fn      ',sc.template_fn),
            ('working_fn       ',sc.working_fn),
            ('\nnodes...',''),
            ('screenshot_tree  ',sc.screenshot_tree.h),
            ('select_node      ',sc.select_node),
            ('slide_node       ',sc.slide_node.h),
            ('\nother args...',''),
            ('edit_flag        ',sc.edit_flag),
            ('pause_flag       ',sc.pause_flag),
            ('screenshot_height',sc.screenshot_height),
            ('screenshot_width ',sc.screenshot_width),
            ('slide_base_name  ',sc.slide_base_name),
        )
        for tag,s in table:
            g.es_print(tag,s)
    #@+node:ekr.20100911044508.5635: *4* sc.make_slide_show_command & helper
    def make_slide_show_command (self,p):

        '''Create slides for all slide nodes (direct children)
        of the @slideshow node p.'''

        sc = self

        if not sc.inkscape_bin:
            return # The ctor has given the warning.

        if not g.match_word(p.h,0,'@slideshow'):
            return g.error('Not an @slideshow node:',p.h)

        if self.verbose:
            g.note('sphinx-path:',sc.get_sphinx_path(None))

        def match(p,pattern):
            return g.match_word(p.h,0,pattern)

        root = p.copy()
        p = p.firstChild()
        while p:
            if g.app.commandInterruptFlag: return
            if match(p,'@slide'):
                sc.run(p,slideshow_node=root)
                # Skip the entire tree, including
                # any inner @screenshot-tree trees.
                p.moveToNodeAfterTree()
            elif match(p,'@protect') or match(p,'@ignore'):
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20100913085058.5629: *4* sc.make_slide_command
    def make_slide_command (self,p):

        sc = self

        if not sc.inkscape_bin:
            return # The ctor has given the warning.

        if not sc.in_slide_show(p):
            return g.error('Not in slide show:',p.h)

        if sc.get_protect_flag(p):
            return g.error('Protected:',p.h)

        sc.run(p,
            callouts=sc.get_callouts(p),
            markers=sc.get_markers(p))

        # sc.select_at_image_node(p)
    #@+node:ekr.20100908110845.5533: *3* lxml replacements
    #@+node:ekr.20100908110845.5534: *4* getElementsWithAttrib
    def getElementsWithAttrib (self,e,attr_name,aList=None):

        sc = self
        if aList is None: aList = []

        val = e.attrib.get(attr_name)
        if val: aList.append(e)

        for child in e.getchildren():
            sc.getElementsWithAttrib(child,attr_name,aList)

        return aList
    #@+node:ekr.20100908110845.5535: *4* getElementsWithAttribList (not used)
    def getElementsWithAttribList (self,e,attr_names,aList=None):

        sc = self
        if aList is None: aList = []

        for z in attr_names:
            if not e.attrib.get(z):
                break
        else:
            aList.append(e)

        for child in e.getchildren():
            sc.getElementsWithAttribList(child,attr_names,aList)

        return aList
    #@+node:ekr.20100908110845.5536: *4* getIds
    def getIds (self,e,d=None):

        '''Return a dict d. Keys are ids, values are elements.'''

        sc = self
        aList = sc.getElementsWithAttrib(e,'id')
        return dict([(e.attrib.get('id'),e) for e in aList])
    #@+node:ekr.20100908110845.5537: *4* getParents
    def getParents (self,e,d=None):

        sc = self
        if d is None:
            d = {}
            d[e] = None

        for child in e.getchildren():
            d[child] = e
            sc.getParents(child,d)

        return d
    #@+node:ekr.20100911044508.5630: *3* options
    #@+node:ekr.20101004082701.5734: *4* Finding nodes
    #@+node:ekr.20100909121239.5742: *5* find_at_screenshot_tree_node
    def find_at_screenshot_tree_node (self,p):

        '''
        Return the @screenshot-tree node in a direct child of p.
        '''

        for p2 in p.children():
            if g.match_word(p2.h,0,'@screenshot-tree'):
                return p2
        else:
            return None
    #@+node:ekr.20100913085058.5660: *5* find_select_node
    def find_select_node (self,p):

        '''
        Find the @select node in a direct child of p.
        Return whatever follows @select in the headline.
        '''

        tag = '@select'

        for p2 in p.children():
            if g.match_word(p2.h,0,tag):
                return p2.h[len(tag):].strip()
        else:
            return ''
    #@+node:ekr.20100915074635.5652: *5* find_slide_node
    def find_slide_node (self,p):

        '''Return the @slide node at or near p.'''

        sc = self ; p1 = p.copy()

        def match(p):
            return g.match_word(p.h,0,'@slide')
        def match_slide_show(p):
            return g.match_word(p.h,0,'@slideshow')

        if match(p):
            return p

        # Look up the tree.
        for parent in p.self_and_parents():
            if match(parent):
                return parent
            elif match_slide_show(parent):
                break

        # Look down the tree.
        p = p.firstChild()
        while p:
            if match(p):
                return p
            elif match_slide_show(p):
                break
            else:
                p.moveToThreadNext()

        g.trace('No @slide node found:',p1.h)
        return None
    #@+node:ekr.20100913085058.5654: *5* find_slideshow_node
    def find_slideshow_node (self,p):

        '''Return the nearest ancestor @slideshow node.'''

        for parent in p.self_and_parents():
            if g.match_word(parent.h,0,'@slideshow'):
                return parent
        else:
            return None
    #@+node:ekr.20101004082701.5735: *4* Path utils
    #@+node:ekr.20100908110845.5540: *5* finalize
    def finalize (self,fn):

        '''Return the absolute path to fn in the slideshow folder.'''

        sc = self

        return sc.fix(g.os_path_finalize_join(sc.slideshow_path,fn))
    #@+node:ekr.20100911044508.5632: *5* fix
    def fix (self,fn):

        '''Fix the case of a file name,
        especially on Windows the case of drive letters.

        This method is safe to call at any time:
        it changes only case and slashes.
        '''

        return os.path.normcase(fn).replace('\\','/')
    #@+node:ekr.20100913085058.5658: *5* sanitize
    def sanitize (self,fn):

        return g.sanitize_filename(fn.lower()).replace('.','-').replace('_','-')
    #@+node:ekr.20101004082701.5736: *4* Computed paths
    # These methods compute final paths.
    #@+node:ekr.20100911044508.5631: *5* get_at_image_fn
    def get_at_image_fn (self,screenshot_fn):

        '''Return the screenshot name **relative to g.app.loadDir**.

        @image directives (sc.screenshot_fn) are relative to g.app.loadDir.
        '''

        sc = self
        base = sc.fix(g.os_path_finalize(g.app.loadDir))
        fn = sc.fix(screenshot_fn)
        fn = os.path.relpath(fn,base)
        fn = sc.fix(fn)
        return fn
    #@+node:ekr.20100909121239.5669: *5* get_directive_fn
    def get_directive_fn (self,screenshot_fn):

        '''Compute the path for use in an .. image:: directive.
        '''

        return g.shortFileName(screenshot_fn)
    #@+node:ekr.20100911044508.5627: *5* get_output_fn
    def get_output_fn (self,p):

        '''Return the full, absolute, output file name.

        An empty filename disables output.

        The default is <sc.slide_base_name>.png, where h is the @slideshow nodes's sanitized headline.
        '''

        # Look for any @output nodes in p's children.
        sc = self ; tag = '@output'
        for child in p.children():
            h = child.h
            if g.match_word(h,0,tag):
                fn = h[len(tag):].strip()
                if fn:
                    fn = sc.finalize(fn)
                else:
                    fn = None
        else:
            fn = '%s-%03d.png' % (sc.slide_base_name,sc.slide_number)
            fn = sc.finalize(fn)

        return fn
    #@+node:ekr.20100911044508.5628: *5* get_screenshot_fn
    def get_screenshot_fn (self,p):

        '''Return the full, absolute, screenshot file name.'''

        sc = self
        fn = '%s-%03d.png' % (sc.slide_base_name,sc.slide_number)
        fn = sc.finalize(fn)
        return fn
    #@+node:ekr.20101004082701.5738: *5* get_slide_base_name
    def get_slide_base_name (self,slideshow_path):

        junk,name = g.os_path_split(slideshow_path)

        return name
    #@+node:ekr.20101004082701.5740: *5* get_slide_fn
    def get_slide_fn (self):

        sc = self
        if sc.slide_number == 0:
            # The first slide is the toc for the slideshow.
            fn = 'leo_toc.html.txt'
        else:
            fn = '%s-%03d.html.txt' % (sc.slide_base_name,sc.slide_number)
        fn = sc.finalize(fn)
        return fn
    #@+node:ekr.20100919075719.5641: *5* get_slideshow_path
    def get_slideshow_path (self,p,sphinx_path):

        '''p is an @slideshow node.

        Return the path to the folder to be used for slides and screenshots.
        This is sphinx_path/slides/<sanitized-p.h>
        '''

        sc = self
        h = p.h
        tag = '@slideshow'
        assert g.match_word(h,0,tag)
        h = h[len(tag):].strip()
        if h:
            theDir = sc.sanitize(h)
            path = sc.fix(g.os_path_finalize_join(sphinx_path,'slides',theDir))
            return path
        else:
            g.error('@slideshow node has no name')
            return None
    #@+node:ekr.20100911044508.5633: *5* get_sphinx_path
    def get_sphinx_path (self,sphinx_path):

        '''Return the full, absolute, path to the sphinx directory.

        By default this will be the leo/doc/html directory.

        If a relative path is given, it will resolved
        relative to the directory containing the .leo file.
        '''

        sc = self ; c = sc.c

        if sphinx_path:
            if g.os_path_isabs(sphinx_path):
                path = sphinx_path
            else:
                # The path is relative to the .leo file
                leo_fn = c.fileName()
                if not leo_fn:
                    g.error('relative sphinx path given but outline not named')
                    return None
                leo_fn = g.os_path_finalize_join(g.app.loadDir,leo_fn)
                base,junk = g.os_path_split(leo_fn)
                path = g.os_path_finalize_join(base,sphinx_path)
        else:
            # The default is the leo/doc/html directory.
            path = g.os_path_finalize_join(g.app.loadDir,'..','doc','html')

        path = sc.fix(path)
        return path
    #@+node:ekr.20100908110845.5542: *5* get_template_fn
    def get_template_fn (self,template_fn):

        '''Return the full, absolute, template file name.'''

        sc = self ; c = sc.c

        if template_fn:
            fn = sc.fix(g.os_path_finalize(template_fn))
        else:
            fn = sc.fix(g.os_path_finalize_join(g.app.loadDir,
                '..','doc','inkscape-template.svg'))

        if g.os_path_exists(fn):
            return fn
        else:
            g.error('template file not found:',fn)
            return None
    #@+node:ekr.20100911044508.5626: *5* get_working_fn
    def get_working_fn (self,p,working_fn):

        '''Return the full, absolute, name of the working file.'''

        sc = self
        fn = working_fn or '%s-%03d.svg' % (sc.slide_base_name,sc.slide_number)
        fn = sc.finalize(fn)
        return fn
    #@+node:ekr.20101004082701.5737: *4* Options
    # These methods examine the children/descendants of a node for options nodes.
    #@+node:ekr.20100908110845.5596: *5* get_callouts & helper
    def get_callouts (self,p):

        '''Return the list of callouts from the
        direct children that are @callout nodes.'''

        sc = self
        aList = []
        for child in p.children():
            if g.match_word(child.h,0,'@callout'):
                callout = sc.get_callout(child)
                if callout: aList.append(callout)
        # g.trace(aList)
        return aList
    #@+node:ekr.20100909121239.6096: *6* get_callout
    def get_callout (self,p):

        '''Return the text of the callout at p.'''

        if p.b.strip():
            return p.b
        else:
            s = p.h
            assert g.match_word(s,0,'@callout')
            i = g.skip_id(s,0,chars='@')
                # Match @callout or @callouts, etc.
            s = s[i:].strip()
            return s
    #@+node:ekr.20100911044508.5620: *5* get_edit_flag
    def get_edit_flag (self,p):

        '''Return True if any of p's children is an @edit node.'''

        sc = self ; c = sc.c

        # Look for any @edit nodes in p's children.
        for child in p.children():
            if g.match_word(child.h,0,'@edit'):
                return True
        else:
            return False
    #@+node:ekr.20100908110845.5597: *5* get_markers & helper
    def get_markers (self,p):

        '''Return the list of markers from all @marker nodes.'''

        sc = self
        aList = []
        for child in p.children():
            if (
                g.match_word(child.h,0,'@marker') or
                g.match_word(child.h,0,'@markers')
            ):
                callout = sc.get_marker(child)
                if callout: aList.extend(callout)
        # g.trace(aList)
        return aList
    #@+node:ekr.20100909121239.6097: *6* get_marker
    def get_marker (self,p):

        '''Return a list of markers at p.'''

        s = p.h
        assert g.match_word(s,0,'@markers') or g.match_word(s,0,'marker')
        i = g.skip_id(s,0,chars='@')  
        s = s[i:].strip()
        return [z.strip() for z in s.split(',')]
    #@+node:ekr.20100913085058.5630: *5* get_pause_flag
    def get_pause_flag (self,p):

        # Look for an @pause nodes in p's children.
        for child in p.children():
            if g.match_word(child.h,0,'@pause'):
                return True
        else:
            return False
    #@+node:ekr.20100913085058.5628: *5* get_protect_flag
    def get_protect_flag (self,p):

         # Look for any @protect or @ignore nodes in p's children.
        for child in p.children():
            if g.match_word(p.h,0,'@ignore') or g.match_word(p.h,0,'@protect'):
                return True
        else:
            return False
    #@+node:ekr.20100911044508.5618: *3* utilities
    #@+node:ekr.20100911044508.5637: *4* clear_cache
    def clear_cache (self):

        '''Clear the dimension cache.'''

        sc = self
        sc.dimCache = {}
        sc.is_reads,sc.is_cache = 0,0
    #@+node:ekr.20101005193146.5687: *4* copy_files & helper
    def copy_files (self):

        sc = self
        slide_path,junk = g.os_path_split(sc.slide_fn)

        # It's best to allow sphinx "make" operations only in
        # the top-level sphinx folder (leo/doc/html) because
        # so that only a single _build directory tree exists.
        table = (
            # 'conf.py',
            # 'leo_toc.html.txt',
            # 'Leo4-80-border.jpg',
            # 'Makefile',
            # 'make.bat',
        )
        for fn in table:
            path = g.os_path_finalize_join(slide_path,fn)
            if not g.os_path_exists(path):
                self.copy_file(sc.sphinx_path,slide_path,fn)
    #@+node:ekr.20101005193146.5688: *5* copy_file
    def copy_file (self,src_path,dst_path,fn):

        src_fn = g.os_path_finalize_join(src_path,fn)
        dst_fn = g.os_path_finalize_join(dst_path,fn)
        junk,dst_dir = g.os_path_split(dst_path)
        g.note('creating',g.os_path_join('slides',dst_dir,fn))
        shutil.copyfile(src_fn,dst_fn)
    #@+node:ekr.20100913085058.5653: *4* get_slide_number
    def get_slide_number (self,p):

        sc = self
        assert sc.slideshow_node
        assert p == sc.slide_node

        n = 0 ; p1 = p.copy()
        p = sc.slideshow_node.firstChild()
        while p:
            if p == p1:
                return n
            elif g.match_word(p.h,0,'@slide'):
                n += 1
                # Skip the entire tree, including
                # any inner @screenshot-tree trees.
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        g.trace('Can not happen. Not found:',p.h)
        return -666
    #@+node:ekr.20100908110845.5543: *4* give_pil_warning
    pil_message_given = False

    def give_pil_warning(self):

        '''Give a singleton warning that PIL could not be loaded.'''

        sc = self
        if sc.pil_message_given:
            return # Warning already given.

        if self.got_pil:
            return # The best situation

        sc.pil_message_given = True

        if self.got_qt:
            g.warning('PIL not found: images may have transparent borders')
        else:
            g.warning('PIL and Qt both not found: images may be less clear')
    #@+node:ekr.20100908110845.5592: *4* in_slide_show
    def in_slide_show (self,p):

        '''Return True if p is a descendant of an @slideshow node.'''

        sc = self
        return bool(sc.find_slideshow_node(p))
    #@+node:ekr.20101004201006.5685: *4* make_all_directories
    def make_all_directories (self):

        sc = self

        # Don't create a path for directive_fn: it is a relative fn!
        table = (
            ('at_image_fn   ',sc.at_image_fn),
            ('output_fn     ',sc.output_fn),
            ('screenshot_fn ',sc.screenshot_fn),
            ('sphinx_path   ',sc.sphinx_path),
            ('slide_fn      ',sc.slide_fn),
            ('slideshow_path',sc.slideshow_path),
            ('template_fn   ',sc.template_fn),
            ('working_fn    ',sc.working_fn),
        )
        for tag,path in table:
            if tag.strip().endswith('fn'):
                path,junk = g.os_path_split(path)
            if not g.os_path_exists(path):
                g.makeAllNonExistentDirectories(path,
                    c=sc.c,force=True,verbose=True)
    #@+node:ekr.20100911044508.5636: *4* open_inkscape_with_list (not used)
    def open_inkscape_with_list (self,aList):

        '''Open inkscape with a list of file.'''

        sc = self
        cmd = [sc.inkscape_bin,"--with-gui"]
        cmd.extend(aList)

        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate() # Wait for Inkscape to terminate.
    #@+node:ekr.20100909193826.5600: *4* select_at_image_node
    def select_at_image_node (self,p):

        '''Select the @image node in one of p's direct children.'''

        sc = self ; c = sc.c
        for child in p.children():
            if g.match_word(child.h,0,'@image'):
                c.selectPosition(child)
                c.redraw_now(child)
                break
        else:
            c.selectPosition(p)
            c.redraw_now(p)
    #@+node:ekr.20101005193146.5690: *4* underline
    def underline (self,s):

        '''Return s overlined and underlined with '=' characters.'''

        # Write longer underlines for non-ascii characters.
        n = max(4,len(g.toEncodedString(s,encoding='utf-8',reportErrors=False)))
        ch = '='
        # return '%s\n%s\n%s\n\n' % (ch*n,s,ch*n)
        return '%s\n%s\n' % (s,ch*n)
    #@+node:ekr.20100911044508.5616: *3* sc.run & helpers
    def run (self,p,callouts=[],markers=[],output_fn=None,
        screenshot_fn=None,screenshot_height=None,screenshot_width=None,
        slideshow_node=None,sphinx_path=None,template_fn=None,working_fn=None
    ):
        '''Create a slide from p with given callouts and markers.
        Call Inkscape to edit the slide if requested.
        '''

        # Init ivars.
        sc = self ; c = sc.c
        ok = sc.init(p,callouts,markers,output_fn,
            screenshot_fn,screenshot_height,screenshot_width,
            slideshow_node,sphinx_path,template_fn,working_fn)
        if not ok: return

        sc.make_all_directories()
        sc.copy_files()

        # sc.slide_show_info_command(sc.slide_node)

        # Take the screenshot and update the tree.
        ok = sc.take_screen_shot()
        if not ok: return

        # Create the working file from the template.
        sc.give_pil_warning()
        template = sc.make_dom()
        if not template:
            return g.error('Can not make template from:',template_fn)

        sc.make_working_file(template)

        if sc.edit_flag:
            if self.verbose: g.note('editing:',sc.working_fn)
            sc.edit_working_file()

        # Create the output file.
        if sc.output_fn:
            sc.make_output_file()
        elif self.verbose:
            g.note('Empty @output node inhibits output')

        sc.make_slide()

        return sc.screenshot_fn
    #@+node:ekr.20100915074635.5651: *4* 0: init
    def init (self,p,
        callouts=[],markers=[],output_fn=None,
        screenshot_fn=None,screenshot_height=None,screenshot_width=None,
        slideshow_node=None,sphinx_path=None,template_fn=None,working_fn=None
    ):

        # Set ivars from the arguments.
        sc = self
        sc.callouts = callouts
        sc.markers = markers

        # Compute p, the slide_node.
        sc.slideshow_node = slideshow_node or sc.find_slideshow_node(p)
        if not sc.slideshow_node: return False
        sc.slide_node = p = sc.find_slide_node(p)
        if not p: return False
        sc.slide_number = n = sc.get_slide_number(p)
        if n < 0: return False

        # Do nothing if the slide node is protected.
        if sc.get_protect_flag(p):
            if self.verbose: g.note('Skipping protected slide:',p.h)
            return False

        # Compute essential paths.
        sc.sphinx_path = sc.get_sphinx_path(sphinx_path)
        if not sc.sphinx_path: return False
        sc.slideshow_path = sc.get_slideshow_path(
            sc.slideshow_node,sc.sphinx_path)
        sc.slide_base_name = sc.get_slide_base_name(sc.slideshow_path)
        sc.working_fn = sc.get_working_fn(p,working_fn)
        if not sc.working_fn: return False
        sc.screenshot_fn = sc.get_screenshot_fn(p)
        if not sc.screenshot_fn: return False

        # Find optional nodes, all relative to the slide node.
        sc.screenshot_tree = sc.find_at_screenshot_tree_node(p)
        sc.select_node = sc.find_select_node(p)

        # Compute paths and file names.
        if output_fn:
            sc.output_fn = output_fn
        else:
            sc.output_fn = sc.get_output_fn(p)
        sc.template_fn = sc.get_template_fn(template_fn)

        # Compute these after computing sc.sphinx_path and sc.screenshot_fn...
        sc.at_image_fn = sc.get_at_image_fn(sc.screenshot_fn)
        sc.directive_fn = sc.get_directive_fn(sc.screenshot_fn)
        sc.slide_fn = sc.get_slide_fn()

        # Compute simple ivars.
        sc.screenshot_height=screenshot_height or sc.default_screenshot_height
        sc.screenshot_width=screenshot_width or sc.default_screenshot_width
        sc.edit_flag = sc.get_edit_flag(p) or bool(sc.callouts or sc.markers)
        sc.pause_flag = sc.get_pause_flag(p)
        return True
    #@+node:ekr.20100909121239.6117: *4* 1: take_screen_shot & helpers
    def take_screen_shot(self):

        '''Take the screen shot, create an @image node,
        and add an .. image:: directive to p.'''

        sc = self ; p = sc.slide_node

        # Always create 'screenshot-setup.leo' 
        fn = sc.create_setup_leo_file()

        # Always open fn in a separate process.
        ok = sc.setup_screen_shot(fn)

        if ok:
            if self.verbose:
                g.note('slide node:  %s' % p.h)
                g.note('output file: %s' % g.shortFileName(sc.screenshot_fn))
            sc.make_image_node()
            sc.add_image_directive()
        else:
            g.warning('problems making screen shot:',p.h)
        return ok
    #@+node:ekr.20100908110845.5594: *5* add_image_directive
    def add_image_directive (self):

        '''Add ".. image:: <sc.directive_fn>" to p.b if it is not already there.'''

        sc = self ; p = sc.slide_node

        s = '.. image:: %s' % sc.directive_fn.replace('\\','/')

        if p.b.find(s) == -1:
            p.b = p.b.rstrip() + '\n\n%s\n\n' % (s)
    #@+node:ekr.20100914090933.5643: *5* create_setup_leo_file
    def create_setup_leo_file(self):

        '''Create an ouline containing all children of sc.screenshot_tree.
        Do not copy @slide nodes or @slideshow nodes.'''

        sc = self ; fn = sc.finalize('screenshot-setup.leo')

        c,frame = g.app.newLeoCommanderAndFrame(
            fileName=fn,relativeFileName=None) # ,gui=gui)

        def isSlide(p):
            return g.match_word(p.h,0,'@slide') or g.match_word(p.h,0,'@slideshow')

        c.frame.createFirstTreeNode()
        root = c.rootPosition()
        if sc.screenshot_tree:
             # Copy all descendants of the @screenshot-tree node.
            children = [z.copy() for z in sc.screenshot_tree.children() if not isSlide(z)]
        else:
            # Copy the entire Leo outline.
            p = root.copy()
            children = []
            while p:
                if not isSlide(p):
                    children.append(p.copy())
                p.moveToNext()

        children.reverse()
        child1 = children and children[0]
        for child in children:
            child2 = root.insertAfter()
            child.copyTreeFromSelfTo(child2)
        # g.trace(root)
        if child1:
            root.doDelete(newNode=None)
            c.setRootPosition(child1) # Essential!

        # Save the file silently.
        c.fileCommands.save(fn)
        c.close()

        return fn
    #@+node:ekr.20100908110845.5599: *5* make_image_node
    def make_image_node (self):

        '''Create an @image node as the first child of sc.slide_node.'''

        sc = self ; c = sc.c ; p = sc.slide_node

        h = '@image %s' % sc.at_image_fn

        # Create the node if it doesn't exist.
        for child in p.children():
            if child.h == h:
                # print('already exists: %s' % h)
                break
        else:
            c.selectPosition(p)
            p2 = p.insertAsNthChild(0)
            p2.h = h
    #@+node:ekr.20100913085058.5659: *5* setup_screen_shot & helpers
    def setup_screen_shot (self,fn):

        '''Take the screen shot after adjusting the window and outline.'''

        sc = self

        # Important: we must *not* have the clipboard open here!
        # Doing so can hang if the user does a clipboard operation
        # in a subprocess.
        if 0:
            cb = g.app.gui.qtApp.clipboard()
            if cb: cb.clear(cb.Clipboard) # Does not work anyway.

        ok = sc.open_screenshot_app(fn)

        if ok and sc.pause_flag:
            ok = sc.save_clipboard_to_screenshot_file()

        return ok
    #@+node:ekr.20100913085058.5656: *6* open_screenshot_app
    def open_screenshot_app (self,leo_fn):

        '''Open the screenshot app.
        Return True if the app exists and can be opened.'''

        verbose = False
        sc = self ; c = sc.c
        launch = g.os_path_finalize_join(g.app.loadDir,
            '..','..','launchLeo.py')
        python = sys.executable

        h,w = sc.screenshot_height,sc.screenshot_width
        cmd = [python,launch,'--window-size=%sx%s' % (h,w)]

        if sc.select_node:
            cmd.append('--select="%s"' % (sc.select_node))

        if sc.pause_flag:
            g.es_print('**** pausing:',sc.screenshot_fn)
        else:
            cmd.append('--screen-shot="%s"' % sc.screenshot_fn)

        cmd.append('--file="%s"' % (leo_fn))

        if verbose:
            proc = subprocess.Popen(cmd)
        else:
            # Eat the output.
            proc = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        proc.communicate() # Wait for Leo to terminate.
        return True
    #@+node:ekr.20100913085058.5655: *6* save_clipboard_to_screenshot_file
    def save_clipboard_to_screenshot_file (self):

        '''Save the clipboard to screenshot_fn.
        Return True if all went well.'''

        sc = self

        cb = g.app.gui.qtApp.clipboard()
        if not cb:
            return g.error('no clipboard')

        image = cb.image()

        if image:
            image.save(sc.screenshot_fn)
            return True
        else:
            return g.error('no image on clipboard')
    #@+node:ekr.20100908110845.5546: *4* 2: make_dom & helpers
    def make_dom (self):

        '''Create the template dom object.'''

        trace = True and not g.unitTesting
        sc = self
        template = sc.get_template()
        if not template: return None
        root = template.getroot()
        ids_d = sc.getIds(root)
        parents_d = sc.getParents(root)

        # make a dict of the groups we're going to manipulate
        part = dict([(z,ids_d.get(z))
            for z in ('co_g_co', 'co_g_bc_1', 'co_g_bc_2')])

        # note where we should place modified copies
        part_parent = parents_d.get(part.get('co_g_co'))

        # remove them from the document
        for i in part.values():
            parents_d = sc.getParents(root)
            parent = parents_d.get(i)
            parent.remove(i)

        for n,callout in enumerate(sc.callouts):
            if trace: g.trace('callout %s: %s' % (n,callout))
            z = copy.deepcopy(part['co_g_co'])
            ids_d = sc.getIds(z)
            text = ids_d.get('co_text_holder')
            text.text = callout
            # need distinct IDs on frames/text for sizing
            frame = ids_d.get('co_frame')
            sc.clear_id(z) # let inkscape pick new IDs for other elements

            # A) it's the flowRoot, not the flowPara, which carries the size info
            # B) Inkscape trashes the IDs on flowParas on load!
            parents_d = sc.getParents(z)
            parent = parents_d.get(text)
            parent.set('id', 'co_text_%d'%n)
            frame.set('id', 'co_frame_%d'%n)

            # offset so user can see them all
            sc.move_element(z, 20*n, 20*n)
            part_parent.append(z)

        for n,number in enumerate(sc.markers):
            if trace: g.trace('number %s: %s' % (n,number))
            if len(str(number)) == 2:
                use_g,use_t = 'co_g_bc_2', 'co_bc_text_2'
            else:
                use_g,use_t = 'co_g_bc_1', 'co_bc_text_1'

            z = copy.deepcopy(part[use_g])
            ids_d = sc.getIds(z)
            bc_text = ids_d.get(use_t) 
            bc_text.text = str(number)
            sc.move_element(z, 20*n, 20*n)
            part_parent.append(z)

        # point to the right screen shot
        ids_d = sc.getIds(template.getroot())
        img_element = ids_d.get('co_shot')
        img_element.set(sc.xlink+'href',sc.screenshot_fn)

        # adjust screen shot dimensions
        if self.got_pil:
            img = Image.open(sc.screenshot_fn)
            img_element.set('width', str(img.size[0]))
            img_element.set('height', str(img.size[1]))

        # write temp file to get size info
        fh, fp = tempfile.mkstemp()
        os.close(fh)
        template.write(fp)

        # could reload file at this point to reflect offsets etc.
        # but don't need to because of relative position mode in paths

        # resize things to fit text
        for n,callout in enumerate(sc.callouts):
            sc.resize_curve_box(fp,template,n)

        os.unlink(fp)
        return template
    #@+node:ekr.20100908110845.5547: *5* clear_id
    def clear_id(self,x):

        """Recursively clear @id on element x and descendants."""

        sc = self
        if 'id' in x.keys():
            del x.attrib['id']

        ids_d = sc.getIds(x)
        objects = set(list(ids_d.values()))
        for z in objects:
            del z.attrib['id']

        return x
    #@+node:ekr.20100908110845.5548: *5* get_template
    def get_template(self):

        """Load and check the template SVG and return DOM"""

        sc = self
        infile = open(sc.template_fn)
        template = etree.parse(infile)
        ids_d = sc.getIds(template.getroot())

        # check all IDs we expect are present
        ids = list(ids_d.keys())
        if set(sc.ids) <= set(ids):
            return template
        else:
            g.error('template did not include all required IDs:',sc.template_fn)
            return None
    #@+node:ekr.20100908110845.5549: *5* move_element
    def move_element(self,element,x,y):

        if not element.get('transform'):
            element.set('transform', "translate(%f,%f)" % (x,y))
        else:
            ox,oy = element.get('transform').split(',')
            ox = ox.split('(')[1]
            oy = oy.split(')')[0]

            element.set('transform', "translate(%f,%f)" %
                (float(ox)+x, float(oy)+y))
    #@+node:ekr.20100908110845.5550: *5* resize_curve_box & helper
    def resize_curve_box(self,fn,template,n):

        sc = self
        d = sc.getIds(template.getroot())
        text = d.get('co_text_%d' % (n))
        frame = d.get('co_frame_%d' % (n))
        text_id = text.get('id')
        frame_id = frame.get('id')

        pnts = frame.get('d').split()
        i = 0
        while i < len(pnts):
            if ',' not in pnts[i]:
                type_ = pnts[i]
                del pnts[i]
            else:
                pnts[i] = [float(j) for j in pnts[i].split(',')]
                pnts[i].insert(0, type_)
                if type_ == 'm':
                    type_ = 'l'
                i += 1

        # kludge for now
        h0 = 12  # index of vertical component going down right side
        h1 = -4  # index of vertical component coming up left side
        min_ = 0  # must leave this many
        present = 5  # components present initially
        h = pnts[h0][2]  # height of one component
        th = sc.get_dim(fn,text_id,'height')  # text height
        if not th:
            g.trace('no th')
        # g.trace('  ', present, h, present*h, th)
        while present > min_ and present * h + 15 > th:
            # g.trace('  ', present, h, present*h, th)
            del pnts[h0]
            del pnts[h1]
            present -= 1

        last = ''
        d = []
        for p in pnts:
            if last != p[0]:
                last = p[0]
                if last == 'm':
                    last = 'l'
                d.append(p[0])
            d.append("%s,%s" % (p[1], p[2]))
        d.append('z')

        frame.set('d', ' '.join(d))
    #@+node:ekr.20100908110845.5551: *6* get_dim
    def get_dim(self, fn, Id, what):
        """return dimension of element in fn with @id Id, what is
        x, y, width, or height
        """

        trace = False
        sc = self
        hsh = fn+Id+what
        if trace: g.trace('hsh',repr(fn),repr(Id),repr(what))
        if hsh in sc.dimCache:
            sc.is_cache += 1
            return sc.dimCache[hsh]

        cmd = [sc.inkscape_bin, '--without-gui', '--query-all', fn]

        proc = subprocess.Popen(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)

        # make new pipe for stderr to supress chatter from inkscape.
        stdout, stderr = proc.communicate() # Wait for Inkscape to terminate.
        s = str(stdout).strip()

        # Necessary for Python 3k.
        if s.startswith("b'"): s = s[2:]
        if s.endswith("'"): s = s[:-1]
        aList = s.replace('\\r','').replace('\\n','\n').split('\n')
        for line in aList:
            if not line.strip(): continue
            id_,x,y,w,h = line.split(',')
            for part in ('x',x), ('y',y), ('width',w), ('height',h):
                hsh2 = fn+id_+part[0]
                if trace: g.trace('hsh2',repr(id_),repr(part[0]))
                sc.dimCache[hsh2] = float(part[1])
        sc.is_reads += 1

        assert sc.dimCache.get(hsh)
        return sc.dimCache.get(hsh)
    #@+node:ekr.20100908110845.5545: *4* 3: make_working_file
    def make_working_file(self,template):

        '''Create the working file from the template.'''

        sc = self
        outfile = open(sc.working_fn,'w')
        template.write(outfile)
        outfile.close()
    #@+node:ekr.20100908110845.5552: *4* 4: edit_working_file & helper
    def edit_working_file(self):

        '''Invoke Inkscape on the working file.'''

        sc = self
        sc.enable_filters(sc.working_fn, False)

        cmd = [sc.inkscape_bin,"--with-gui",sc.working_fn]
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate()  # Wait for Inkscape to terminate.

        sc.enable_filters(sc.working_fn, True)
    #@+node:ekr.20100908110845.5553: *5* enable_filters
    def enable_filters(self,svgfile,enable):
        """Disable/enable filters in SVG at the XML level

        The drop-shadow filter on several objects kills editing performance
        in inkscape, so this turns them on/off in the XML.  There's a GUI
        operation to turn them off in inkscape, but it's a pain to have to
        keep using it.

        Disabling copys the real @style to @__style and changes
        "filter:url" to "_filter:url" in the active @style, while
        enabling just copys @__style to @style and deletes @__style.
        """

        sc = self
        doc = etree.parse(svgfile)
        root = doc.getroot()

        if enable:
            # copy @__style to @style and deletes @__style.
            aList = sc.getElementsWithAttrib(root,'__style')
            for i in aList:
                i.set("style", i.get("__style"))
                del i.attrib['__style']
        else:
            aList3 = sc.getElementsWithAttrib(root,'style')
            aList = [z for z in aList3
                if z.attrib.get('style').find('filter:url(') > -1]
            # copy the real @style to @__style and
            # changes "filter:url" to "_filter:url" in the active @style
            for i in aList:
                i.set("__style", i.get("style"))
                i.set("style", i.get("style").replace(
                    'filter:url(', '_filter:url('))

        doc.write(open(svgfile, 'w'))
    #@+node:ekr.20100908110845.5554: *4* 5: make_output_file & helper
    def make_output_file(self):

        '''Create the output file from the working file.'''

        sc = self
        cmd = (
            sc.inkscape_bin,
            "--without-gui",
            "--export-png="+sc.output_fn,
            "--export-area-drawing",
            "--export-area-snap",
            sc.working_fn)

        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate() # Wait for Inkscape to terminate.

        if self.got_pil: # trim transparent border
            try:
                img = Image.open(sc.output_fn)
                img = sc.trim(img, (255,255,255,0))
                img.save(sc.output_fn)
            except IOError:
                g.trace('Can not open %s' % sc.output_fn)

        # os.system(png_fn)
    #@+node:ekr.20100908110845.5555: *5* trim
    def trim(self, im, border):

        bg = Image.new(im.mode, im.size, border)
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)
        else:
            # found no content
            raise ValueError("cannot trim; image was empty")
    #@+node:ekr.20101004082701.5739: *4* 6: make_slide & helpers
    def make_slide (self):

        '''Write sc.slide_node.b to <sc.slide_fn>, a .html.txt file.'''

        sc = self ; fn = sc.slide_fn
        #  Don't call rstCommands.writeToDocutils--we are using sphinx!
        # result = self.c.rstCommands.writeToDocutils(sc.slide_node.b,'.html')
        s = sc.make_slide_contents()
        try:
            f = open(fn,'w')
            f.write(s)
            f.close()
            if self.verbose: g.note('wrote slide:',g.shortFileName(fn))
        except Exception:
            g.error('writing',fn)
            g.es_exception()
    #@+node:ekr.20101005193146.5689: *5* make_slide_contents
    def make_slide_contents (self):

        sc = self
        n = sc.slide_number
        h = sc.slideshow_node.h[len('@slideshow'):].strip()

        #@+<< define toc_body >>
        #@+node:ekr.20101005193146.5691: *6* << define toc_body >>
        s = '''\
        Contents:

        .. toctree::
           :maxdepth: 1
           :glob:

           %s-*
        ''' % (sc.slide_base_name)

        # Indices and tables
        # ==================

        # * :ref:`genindex`
        # * :ref:`search`


        toc_body = g.adjustTripleString(s,sc.c.tab_width)
        #@-<< define toc_body >>

        if n == 0:
            # h = 'Slideshow: %s' % (h)
            body = toc_body
        else:
            h = '%s: %s' % (h,n)
            body = sc.slide_node.b

        title = sc.underline(h)

        return '%s\n\n%s' % (title,body)
    #@-others

#@-others
#@-leo
